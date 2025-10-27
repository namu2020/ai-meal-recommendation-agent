# Mock 모드 → Notion MCP 모드 전환 완료

## 📋 작업 요약

Mock 모드에서 Notion MCP 모드로 성공적으로 전환했습니다. 이제 실제 Notion 데이터를 읽어서 사용할 수 있습니다.

---

## ✅ 완료된 작업

### 1. 환경 설정
- ✅ `.env` 파일에 `USE_NOTION_MCP=true` 추가
- ✅ Notion API 키와 Database ID 설정

### 2. Notion 데이터 파싱
- ✅ `parse_notion_data.py` 작성: Notion 페이지에서 사용자 데이터 추출
- ✅ `notion_structure.json` 업데이트: 최신 Notion 데이터 구조 저장
- ✅ 실제 Notion API 호출 성공

### 3. MCP 서버 업데이트
- ✅ `mcp_servers/notion_server_real.py`: 실제 Notion API와 연동
  - 사용자 페이지 파싱 로직 구현
  - 알레르기, 선호도, 예산, 일정 데이터 추출
  - Mock 데이터로 fallback 지원

### 4. MCP 클라이언트 설정
- ✅ `mcp_client/notion_mcp_client.py` 수정
  - `USE_NOTION_MCP` 설정에 따라 `notion_server_real.py` 또는 `notion_server.py` 선택
  - 자동으로 올바른 서버 사용

### 5. Tools 업데이트
- ✅ `tools/notion_tools.py` 전면 수정
  - Mock 모드와 MCP 모드 동시 지원
  - `USE_NOTION_MCP=true`일 때 MCP 클라이언트 사용
  - `USE_NOTION_MCP=false`일 때 Mock 데이터 사용
  - 지연 import로 안정성 향상

---

## 🔧 사용 방법

### Mock 모드로 실행 (기본)
```bash
# .env 파일에서
USE_NOTION_MCP=false

# 앱 실행
streamlit run app.py
```

### Notion MCP 모드로 실행
```bash
# .env 파일에서
USE_NOTION_MCP=true
NOTION_API_KEY=ntn_xxxxxxxxxxxx
NOTION_DATABASE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# 앱 실행
streamlit run app.py
```

---

## 📂 주요 파일 변경 사항

### 1. `.env`
```env
# Notion MCP 설정
USE_NOTION_MCP=true  # Mock 모드는 false
NOTION_API_KEY=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
NOTION_DATABASE_ID=2976b5ca-f706-8075-a8cb-fa55ba05de81
```

### 2. `mcp_servers/notion_server_real.py`
- 실제 Notion API 호출 및 데이터 파싱
- 소윤의 페이지 데이터를 기본으로 사용
- 섹션별 데이터 추출 (Quick Profile, 예산, 스케줄 등)

### 3. `mcp_client/notion_mcp_client.py`
```python
# USE_NOTION_MCP 설정에 따라 서버 선택
use_mcp = os.getenv("USE_NOTION_MCP", "false").lower() == "true"
if use_mcp:
    self.server_script = "notion_server_real.py"
else:
    self.server_script = "notion_server.py"
```

### 4. `tools/notion_tools.py`
```python
# 각 tool이 MCP 모드를 지원
if USE_NOTION_MCP:
    # MCP 서버를 통해 실제 Notion 데이터 조회
    return run_async(_get_user_preferences_async())
else:
    # Mock 데이터 사용
    data = load_notion_data()
    # ...
```

---

## 🧪 테스트

### Notion API 연결 테스트
```bash
python test_notion_api.py
```

### Notion 데이터 파싱 테스트
```bash
python parse_notion_data.py
```

### MCP 모드 테스트
```bash
# .env에서 USE_NOTION_MCP=true 설정 후
python test_mcp_mode.py
```

---

## 📊 Notion 데이터 구조

### 메인 페이지
- ID: `2976b5ca-f706-8075-a8cb-fa55ba05de81`
- 제목: HOME

### 하위 사용자 페이지들
1. **소윤의 식사 노트** (기본 사용자)
   - 갑각류 알레르기
   - 15분 식사 시간
   - 1식 13,000원 예산

2. 태식의 식사 노트
3. 지민의 식사 노트
4. 현우의 식사 노트
5. 라미의 식사노트

### 각 사용자 페이지 구조
- Quick Profile: 알레르기, 선호도 등
- 예산: 1식 예산, 월간 예산
- 스케줄 & 슬롯: 식사 시간, 가용 시간
- 주방 & 재료
- 오늘의 상태(샘플): 식단 기록

---

## 🎯 다음 단계 (선택사항)

### 1. 다른 사용자 지원
`notion_server_real.py`의 `target_user` 변수 수정:
```python
target_user = "태식"  # 또는 "지민", "현우", "라미"
```

### 2. 더 정교한 데이터 파싱
- 식단 기록 히스토리 추가
- 선호 요리 종류 추출
- 다이어트 목표 파싱 개선

### 3. 실시간 데이터 업데이트
- Notion 페이지 수정 시 자동 반영
- 캐싱 메커니즘 추가

### 4. 다중 사용자 지원
- 여러 사용자 동시 관리
- 사용자별 설정 전환

---

## ⚠️ 주의사항

1. **Notion Integration 권한**
   - Notion Integration이 페이지에 연결되어 있어야 함
   - https://www.notion.so/my-integrations 에서 확인

2. **API 키 보안**
   - `.env` 파일을 Git에 커밋하지 마세요
   - `.gitignore`에 `.env` 포함 확인

3. **데이터 구조**
   - Notion 페이지 구조가 변경되면 파싱 로직도 수정 필요
   - 섹션 이름과 테이블 구조를 일관되게 유지

---

## 🔄 전환 방법

### Mock → MCP
```bash
# .env 파일에서
USE_NOTION_MCP=true
```

### MCP → Mock
```bash
# .env 파일에서
USE_NOTION_MCP=false
```

---

## ✨ 성과

✅ Mock 데이터에서 실제 Notion 데이터로 완전 전환
✅ 실시간 Notion 정보를 CrewAI 에이전트가 활용
✅ 사용자 알레르기, 선호도, 예산, 일정을 Notion에서 관리
✅ 유연한 모드 전환 (Mock ↔ MCP)
✅ 안정적인 Fallback 메커니즘

---

**작성일**: 2025-10-25
**작성자**: AI Assistant
**버전**: 1.0

