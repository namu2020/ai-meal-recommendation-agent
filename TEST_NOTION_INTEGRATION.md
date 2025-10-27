# Notion MCP 통합 테스트 가이드 🧪

실제 Notion 데이터와 MCP를 연결하여 테스트하는 전체 프로세스입니다.

---

## ✅ 사전 준비 체크리스트

- [ ] Notion Integration 생성 완료
- [ ] Notion에 합성 데이터 페이지 준비 (5개 하위 페이지)
- [ ] `.env` 파일에 API 키 설정
  - `NOTION_API_KEY=secret_xxx`
  - `NOTION_DATABASE_ID=페이지ID`
- [ ] Integration을 Notion 페이지에 연결

---

## 🚀 1단계: 패키지 설치

### SSL 오류가 있는 경우
```bash
cd "/Users/namu123/Documents/테크 관련/공훈의_AI특강/팀플/crewai-food-app"

# SSL 무시하고 설치
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org notion-client nest-asyncio
```

### 일반 설치
```bash
pip install notion-client nest-asyncio
```

### 설치 확인
```bash
python -c "import notion_client; print('✅ 설치 완료')"
```

---

## 🧪 2단계: Notion API 직접 테스트

### 실행
```bash
python test_notion_api.py
```

### 예상 출력
```
======================================================================
🔍 Notion API 연결 테스트
======================================================================

✅ NOTION_API_KEY: secret_xxx...
✅ NOTION_DATABASE_ID: abc123...

📄 1단계: 메인 페이지 조회
----------------------------------------------------------------------
✅ 페이지 ID: abc123...
   생성일: 2025-01-...
   수정일: 2025-01-...
   제목: 음식 추천 데이터

📦 2단계: 하위 블록/페이지 조회
----------------------------------------------------------------------
✅ 하위 블록 수: 5

1. 블록 타입: child_page
   ID: xyz...
   📄 페이지 제목: 식단 기록
   프로퍼티:
     - title (title)
   내용 블록 수: 10
     1. paragraph
        내용: 2025년 1월 15일...
     ...

2. 블록 타입: child_page
   ID: xyz...
   📄 페이지 제목: 사용자 선호도
   ...

💾 3단계: 데이터 구조 저장
----------------------------------------------------------------------
✅ 데이터 구조를 'notion_structure.json'에 저장했습니다.
```

### 생성된 파일
- `notion_structure.json` - Notion 데이터의 전체 구조

---

## 📊 3단계: 데이터 구조 분석

```bash
# JSON 파일을 보기 좋게 출력
python -m json.tool notion_structure.json | less

# 또는 에디터로 열기
code notion_structure.json
```

### 확인 사항
1. **하위 페이지 제목**: 각 페이지가 어떤 데이터를 담고 있는지
2. **프로퍼티**: 각 페이지의 속성 (날짜, 숫자, 텍스트 등)
3. **콘텐츠 블록**: 실제 데이터가 어떤 형태로 저장되어 있는지

---

## 🔧 4단계: 파싱 로직 구현

`notion_structure.json`을 확인한 후, 실제 데이터 구조에 맞게 파싱 로직을 구현합니다.

### 구현 파일
`mcp_servers/notion_server_real.py`의 `query_notion_pages()` 함수

### 예시 파싱 로직

```python
async def query_notion_pages():
    """Notion 페이지들에서 데이터 조회"""
    # 하위 페이지 조회
    children = await notion.blocks.children.list(block_id=NOTION_DATABASE_ID)
    
    meal_history = []
    preferences = {}
    schedule = {}
    budget = {}
    
    for block in children.get('results', []):
        if block.get('type') == 'child_page':
            child_id = block.get('id')
            child_page = await notion.pages.retrieve(page_id=child_id)
            
            # 페이지 제목 추출
            page_title = ""
            if 'properties' in child_page:
                for prop_name, prop_data in child_page['properties'].items():
                    if prop_data.get('type') == 'title' and prop_data.get('title'):
                        page_title = prop_data['title'][0]['plain_text']
                        break
            
            # 페이지 내용 블록 조회
            content = await notion.blocks.children.list(block_id=child_id)
            
            # 제목에 따라 데이터 분류 및 파싱
            if '식단' in page_title or 'meal' in page_title.lower():
                meal_history = parse_meal_history(content.get('results', []))
            
            elif '선호' in page_title or 'preference' in page_title.lower():
                preferences = parse_preferences(content.get('results', []))
            
            elif '일정' in page_title or 'schedule' in page_title.lower():
                schedule = parse_schedule(content.get('results', []))
            
            elif '예산' in page_title or 'budget' in page_title.lower():
                budget = parse_budget(content.get('results', []))
    
    return {
        "meal_history": meal_history,
        "preferences": preferences,
        "schedule": schedule,
        "budget": budget
    }


def parse_meal_history(blocks):
    """식단 기록 파싱"""
    meals = []
    
    for block in blocks:
        block_type = block.get('type')
        
        if block_type == 'paragraph':
            text = extract_text(block.get('paragraph', {}))
            # 텍스트에서 날짜, 메뉴, 칼로리 등 파싱
            # 예: "2025-01-15 점심: 닭가슴살 샐러드 (350kcal, 12000원)"
            # → {"date": "2025-01-15", "type": "점심", "meal": "닭가슴살 샐러드", ...}
            
        elif block_type == 'bulleted_list_item':
            text = extract_text(block.get('bulleted_list_item', {}))
            # 리스트 아이템 파싱
    
    return meals


def extract_text(block_content):
    """블록에서 텍스트 추출"""
    rich_text = block_content.get('rich_text', [])
    if rich_text:
        return rich_text[0].get('plain_text', '')
    return ""
```

---

## 🧪 5단계: MCP 서버 테스트

파싱 로직 구현 후:

### 5.1 기존 MCP 서버를 실제 버전으로 교체

```bash
# 백업
cp mcp_servers/notion_server.py mcp_servers/notion_server_mock.py

# 실제 버전으로 교체
cp mcp_servers/notion_server_real.py mcp_servers/notion_server.py
```

### 5.2 MCP 클라이언트 테스트

```bash
# MCP 모드 활성화
echo "USE_NOTION_MCP=true" >> .env

# 테스트 실행
python test_mcp_client.py
```

### 예상 출력
```
============================================================
Notion MCP 클라이언트 테스트
============================================================

🔗 Notion MCP 서버 연결 테스트 시작...

✅ MCP 서버 연결 성공!

📋 사용 가능한 도구 목록:
  - get_meal_history: 사용자의 최근 식단 기록 조회
  - get_user_preferences: 사용자의 알레르기, 선호도, 다이어트 목표 조회
  - get_available_time: 오늘 사용자가 식사 준비에 사용할 수 있는 시간 조회
  - get_budget_status: 오늘 예산 사용 현황 및 남은 예산 조회

🧪 테스트 1: 사용자 선호도 조회
결과:
{
  "allergies": ["새우", "땅콩"],
  "dislikes": ["고수", "청양고추"],
  ...
}
```

---

## 🎯 6단계: CrewAI 통합 테스트

```bash
# Streamlit 앱 실행
streamlit run app.py
```

### 확인 사항
1. 앱 시작 시 콘솔에 `🔗 Notion MCP 모드 활성화` 메시지 표시
2. 챗봇에서 "오늘 저녁 메뉴 추천해줘" 입력
3. 에이전트들이 Notion 데이터를 성공적으로 조회하는지 확인

---

## 🔄 Mock ↔ 실제 Notion 전환

### Mock 모드로 전환 (개발/테스트)
```bash
# .env 파일 수정
USE_NOTION_MCP=false
```

### Notion 모드로 전환 (실제 데이터)
```bash
# .env 파일 수정
USE_NOTION_MCP=true
```

---

## 🐛 문제 해결

### 문제 1: "NOTION_API_KEY가 설정되지 않았습니다"
**해결**: `.env` 파일 확인
```bash
cat .env | grep NOTION
```

### 문제 2: "페이지를 찾을 수 없습니다" (404)
**해결**: 
1. NOTION_DATABASE_ID가 올바른 페이지 ID인지 확인
2. Integration이 해당 페이지에 연결되어 있는지 확인

### 문제 3: "권한이 없습니다" (403)
**해결**:
1. Notion 페이지에서 "..." → "Connections" → Integration 추가
2. Integration의 Capabilities에 "Read content" 체크 확인

### 문제 4: 데이터 파싱 오류
**해결**:
1. `notion_structure.json` 확인하여 실제 데이터 구조 파악
2. 파싱 로직을 데이터 구조에 맞게 수정
3. 디버그 출력 추가:
```python
print(f"DEBUG: block_type = {block_type}")
print(f"DEBUG: content = {json.dumps(block, indent=2)}")
```

---

## 📝 체크리스트

### 완료해야 할 작업
- [ ] 1단계: 패키지 설치 완료
- [ ] 2단계: `test_notion_api.py` 실행 성공
- [ ] 3단계: `notion_structure.json` 확인
- [ ] 4단계: 파싱 로직 구현
- [ ] 5단계: MCP 서버 교체 및 테스트
- [ ] 6단계: CrewAI 앱에서 정상 동작 확인

---

## 💡 팁

1. **단계별 진행**: 한 번에 모두 하지 말고 각 단계를 확인하면서 진행
2. **디버깅**: 문제가 생기면 `notion_structure.json`을 먼저 확인
3. **Mock 활용**: 개발 중에는 Mock 모드로, 테스트 시에만 Notion 모드 사용
4. **로그 활용**: MCP 서버에 `print()` 문 추가하여 데이터 흐름 확인

---

## 🎉 성공 시 확인

✅ Notion API 연결 성공  
✅ 데이터 구조 파악 완료  
✅ 파싱 로직 구현 완료  
✅ MCP 서버 정상 동작  
✅ CrewAI 에이전트가 실제 Notion 데이터 사용  

**축하합니다! 실시간 Notion 연동 완료!** 🚀

