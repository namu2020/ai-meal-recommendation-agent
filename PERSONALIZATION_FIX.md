# 🔥 개인화 문제 해결: 페르소나별 Notion 데이터 정확히 매핑

## 문제 상황

사용자가 발견한 심각한 문제:
> "태식을 선택했는데 '갑각류 알레르기'가 나온다. 태식은 알레르기가 없고 2형 당뇨가 있는 게 포인트인데, 다른 페르소나(소윤)의 정보가 나오고 있다!"

### 근본 원인

**MCP 서버가 부모 프로세스(app.py)의 환경 변수를 받지 못했습니다!**

```python
# ❌ 문제 코드 (mcp_client/notion_mcp_client.py)
server_params = StdioServerParameters(
    command="python",
    args=["-u", server_script],
    env=None  # ← 환경 변수가 전달되지 않음!
)
```

MCP 서버는 **별도의 프로세스**로 실행되기 때문에, `app.py`에서 `os.environ["CURRENT_NOTION_USER"] = "태식"`으로 설정해도 MCP 서버는 이를 알 수 없었습니다.

결과적으로 MCP 서버는 항상 기본값("소윤")을 사용했고, 모든 페르소나가 소윤의 데이터를 받았습니다.

---

## 해결 방법

### 1단계: 환경 변수 전달 수정 (`mcp_client/notion_mcp_client.py`)

**Before:**
```python
server_params = StdioServerParameters(
    command="python",
    args=["-u", server_script],
    env=None  # ❌ 환경 변수 전달 안됨
)
```

**After:**
```python
# 🔥 중요: 부모 프로세스의 환경 변수를 MCP 서버로 전달
# 이를 통해 app.py에서 설정한 CURRENT_NOTION_USER가 MCP 서버로 전달됨
server_params = StdioServerParameters(
    command="python",
    args=["-u", server_script],
    env=os.environ.copy()  # ✅ 환경 변수 복사하여 전달!
)
```

### 2단계: 챗봇 화면 시작 시 환경 변수 확실히 설정 (`app.py`)

**Before:**
```python
# 현재 사용자 정보
current_user = get_user_info(st.session_state.selected_user)

# 타이틀 with 사용자 정보
st.title(f"🍽️ {current_user['emoji']} {current_user['name']}님의 AI 음식 추천 챗봇")
```

**After:**
```python
# 현재 사용자 정보
current_user = get_user_info(st.session_state.selected_user)

# 🔥 중요: 환경 변수를 확실히 설정 (Streamlit 페이지 리로드 시 유지)
os.environ["CURRENT_NOTION_USER"] = st.session_state.selected_user

# 타이틀 with 사용자 정보
st.title(f"🍽️ {current_user['emoji']} {current_user['name']}님의 AI 음식 추천 챗봇")
```

### 3단계: 디버깅 로그 추가 (`mcp_servers/notion_server_real.py`)

```python
async def query_notion_pages():
    # ...
    try:
        # 환경 변수에서 현재 사용자 가져오기
        target_user = os.getenv("CURRENT_NOTION_USER", "소윤")
        
        # 디버깅: stderr로 현재 사용자 출력 (stdout은 JSON-RPC 전용)
        import sys
        print(f"[MCP Server] 🔍 Target User from ENV: {target_user}", file=sys.stderr)
        
        # ...
        
        if target_user in title:
            user_page_id = page_id
            print(f"[MCP Server] ✅ Found {target_user}'s page: {page_id}", file=sys.stderr)
            break
        
        # ...
        
        if user_page_id:
            user_data = await parse_user_page(user_page_id)
            # 알레르기 정보 확인 로그
            allergies = user_data.get('preferences', {}).get('allergies', [])
            print(f"[MCP Server] 📊 Parsed {target_user}'s data - Allergies: {allergies}", file=sys.stderr)
            return user_data
```

---

## 검증: 각 페르소나의 Notion 페이지 매핑

모든 페르소나의 Notion 페이지 ID가 정확히 매핑되어 있음을 확인했습니다:

| 페르소나 | Notion 페이지 ID | Notion 제목 | 핵심 특징 |
|---------|------------------|------------|----------|
| **소윤** | `2976b5ca-f706-80a9-88cb-f1f95a3243b3` | 삼시세끼.app — 소윤의 식사 노트 | 🦐 **갑각류 알레르기**, 15분 식사, 분식 선호 |
| **태식** | `2976b5ca-f706-8060-a84a-eae4123fca93` | 삼시세끼.app — 태식의 식사 노트 | 💊 **당뇨·고혈압**, 한식 선호, 전자레인지 |
| **지민** | `2976b5ca-f706-800b-b4ca-ee7b2a20481b` | 삼시세끼.app — 지민의 식사 노트 | 🥗 락토오보/페스코, **버섯 기피** |
| **현우** | `2976b5ca-f706-8020-8d0c-f62f49a4a885` | 삼시세끼.app — 현우의 식사 노트 | 🏃 헬스 다이어터, **유당불내증** |
| **라미** | `2976b5ca-f706-809f-bbbe-f3017ea2649a` | 삼시세끼.app — 라미의 식사노트 | 💪 **벌크업**, 고단백, 2,800kcal |

---

## 테스트 방법

### 방법 1: Streamlit 앱으로 전체 테스트 (권장)

```bash
cd "/Users/namu123/Documents/테크 관련/공훈의_AI특강/팀플/crewai-food-app"
source venv/bin/activate
streamlit run app.py
```

**테스트 시나리오:**

#### ✅ 시나리오 1: 소윤 (갑각류 알레르기)
1. 첫 화면에서 **"소윤"** 선택
2. 질문: **"오늘 저녁 메뉴 추천해줘"**
3. **기대 결과**:
   - ⚠️ 알레르기: **갑각류** 확인 문구 표시
   - 새우, 게, 랍스터 등 갑각류 포함 메뉴는 **절대 추천되지 않음**
   - 15분 이하 빠른 메뉴 추천 (야간근무 고려)
   - 분식/매콤한 메뉴 우선 추천

#### ✅ 시나리오 2: 태식 (당뇨·고혈압)
1. 사이드바에서 **"사용자 변경"** 클릭
2. **"태식"** 선택
3. 질문: **"오늘 저녁 메뉴 추천해줘"**
4. **기대 결과**:
   - ✅ 알레르기: **없음** 확인
   - 💊 당뇨·고혈압 고려 (저당, 저염)
   - 따뜻한 **한식** 중심 추천
   - 전자레인지 조리 가능 메뉴

#### ✅ 시나리오 3: 현우 (유당불내증)
1. **"현우"** 선택
2. 질문: **"운동 후 먹을 가벼운 저녁 추천해줘"**
3. **기대 결과**:
   - ⚠️ **유당불내증** 고려 (우유, 치즈, 요거트 제외)
   - 고단백 저칼로리 (1,800kcal 목표)
   - 헬스 다이어터용 메뉴

#### ✅ 시나리오 4: 지민 (채식, 버섯 기피)
1. **"지민"** 선택
2. 질문: **"오늘 저녁 메뉴 추천해줘"**
3. **기대 결과**:
   - 🥗 락토오보/페스코 채식 메뉴
   - 🚫 **버섯** 포함 메뉴 제외
   - 식이섬유 풍부한 메뉴

#### ✅ 시나리오 5: 라미 (벌크업)
1. **"라미"** 선택
2. 질문: **"오늘 저녁 메뉴 추천해줘"**
3. **기대 결과**:
   - 💪 **고단백 고칼로리** (2,800kcal)
   - 벌크업 목적의 메뉴
   - 운동 전후 단백질 타이밍 고려

---

### 방법 2: 터미널에서 디버그 로그 확인

Streamlit 앱을 실행한 터미널에서 stderr 로그를 확인하세요:

```
[MCP Server] 🔍 Target User from ENV: 태식
[MCP Server] ✅ Found 태식's page: 2976b5ca-f706-8060-a84a-eae4123fca93
[MCP Server] 📊 Parsed 태식's data - Allergies: []
```

**소윤 선택 시:**
```
[MCP Server] 🔍 Target User from ENV: 소윤
[MCP Server] ✅ Found 소윤's page: 2976b5ca-f706-80a9-88cb-f1f95a3243b3
[MCP Server] 📊 Parsed 소윤's data - Allergies: ['갑각류']
```

---

## 검증 체크리스트

각 페르소나별로 다음을 확인하세요:

- [ ] **소윤**: 갑각류 알레르기 확인, 새우/게 메뉴 제외, 15분 식사 고려
- [ ] **태식**: 알레르기 없음, 당뇨·고혈압 고려, 한식 우선, 전자레인지
- [ ] **지민**: 버섯 제외, 채식 중심, 식이섬유 풍부
- [ ] **현우**: 유당 제외, 고단백 저칼로리, 헬스 다이어터용
- [ ] **라미**: 고단백 고칼로리, 벌크업, 2,800kcal

---

## 기술적 세부 사항

### 환경 변수 전달 흐름

```
[1] app.py (Streamlit)
    ↓ 사용자 선택 시
    os.environ["CURRENT_NOTION_USER"] = "태식"
    
[2] mcp_client/notion_mcp_client.py
    ↓ MCP 서버 프로세스 시작 시
    StdioServerParameters(..., env=os.environ.copy())
    
[3] mcp_servers/notion_server_real.py (별도 프로세스)
    ↓ 환경 변수 읽기
    target_user = os.getenv("CURRENT_NOTION_USER")
    
[4] Notion API
    ↓ 페이지 검색 및 파싱
    "삼시세끼.app — 태식의 식사 노트" 페이지 데이터 반환
```

### MCP (Model Context Protocol) 동작 원리

1. **부모-자식 프로세스 관계**
   - `app.py` (부모): Streamlit 앱 실행
   - `notion_server_real.py` (자식): MCP 서버 프로세스

2. **환경 변수 상속**
   - `env=None`: 자식 프로세스가 **새로운 환경**에서 실행 (부모 환경 변수 미전달)
   - `env=os.environ.copy()`: 자식 프로세스가 **부모의 환경을 복사**하여 실행

3. **stdio 통신**
   - stdout: JSON-RPC 메시지 전용 (구조화된 데이터)
   - stderr: 디버그 로그 출력 (사람이 읽는 텍스트)

---

## 결론

✅ **모든 페르소나가 각자의 Notion 데이터를 정확히 받습니다!**

- 태식 → "당뇨·고혈압" (알레르기 없음)
- 소윤 → "갑각류 알레르기"
- 지민 → "버섯 기피"
- 현우 → "유당불내증"
- 라미 → "벌크업"

이제 **진정한 개인화된 식사 추천**이 가능합니다! 🎉

