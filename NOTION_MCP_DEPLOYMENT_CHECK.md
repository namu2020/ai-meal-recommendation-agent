# 🔍 Notion MCP 배포 체크리스트

## ⚠️ **중요 발견 사항**

`USE_NOTION_MCP='true'`로 배포하셨다고 하셨는데, **배포 환경에 따라 문제가 발생할 수 있습니다**.

---

## 🚨 **주요 문제점 및 해결 방안**

### ❌ **문제 1: Streamlit Cloud에서 MCP 서버 실행 불가**

#### 원인:
- MCP는 **별도의 Python 서브프로세스**를 시작합니다 (`notion_server_real.py`)
- Streamlit Cloud는 **샌드박스 환경**으로 서브프로세스 실행이 제한됩니다
- `NotionMCPClient`가 `subprocess`로 MCP 서버를 실행하려고 하면 **차단될 수 있습니다**

#### 코드 확인:
```python
# mcp_client/notion_mcp_client.py (Line 43-46)
server_params = StdioServerParameters(
    command="python",  # ← 새로운 프로세스 시작 시도!
    args=["-u", server_script],
    env=os.environ.copy()
)
```

#### 증상:
- 앱이 시작되지 않거나
- "MCP 연결 오류" 메시지 발생
- Timeout 에러

#### 해결 방법:
**→ 배포 시에는 `USE_NOTION_MCP=false` (Mock 모드) 권장!**

---

### ❌ **문제 2: Notion API 키 필수**

#### 원인:
- `USE_NOTION_MCP=true`로 설정하면:
  - `NOTION_API_KEY` 필수
  - `NOTION_DATABASE_ID` 필수
  - Notion API에 접근 권한 필요

#### 코드 확인:
```python
# mcp_servers/notion_server_real.py (Line 22-29)
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if NOTION_API_KEY:
    notion = AsyncClient(auth=NOTION_API_KEY)
else:
    print("⚠️ NOTION_API_KEY가 설정되지 않았습니다.")
    notion = None
```

#### Secrets 설정 필요:
```toml
# Streamlit Cloud Secrets
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4o-mini"

# Notion MCP 사용 시 (필수!)
USE_NOTION_MCP = "true"
NOTION_API_KEY = "ntn_..."
NOTION_DATABASE_ID = "2976b5ca-..."
```

---

### ❌ **문제 3: 비동기 이벤트 루프 충돌**

#### 원인:
- Streamlit은 자체 이벤트 루프를 실행합니다
- MCP 클라이언트도 비동기 이벤트 루프를 사용합니다
- **두 개의 루프가 충돌**할 수 있습니다

#### 코드 확인:
```python
# tools/notion_tools.py (Line 27-35)
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)
```

#### 해결책:
- `nest_asyncio` 패키지 사용 (이미 적용됨 ✅)
- `requirements.txt`에 포함 확인 필요

---

### ❌ **문제 4: 환경 변수 전달**

#### 원인:
- `CURRENT_NOTION_USER`가 MCP 서버로 전달되지 않을 수 있음
- Streamlit Cloud에서 동적 환경 변수 설정이 제한될 수 있음

#### 코드 확인:
```python
# app.py (Line 123)
os.environ["CURRENT_NOTION_USER"] = st.session_state.selected_user

# mcp_client/notion_mcp_client.py (Line 46)
env=os.environ.copy()  # ← 이게 전달될까?
```

#### 잠재적 문제:
- 멀티 세션 환경에서 사용자 간 데이터 혼선
- 서브프로세스에 환경 변수가 전달되지 않을 수 있음

---

## ✅ **체크리스트: 배포 전 확인사항**

### 1️⃣ **Streamlit Cloud 배포 시**

- [ ] **`USE_NOTION_MCP=false` 사용 권장** (Mock 모드)
  - MCP 서버 서브프로세스 문제 회피
  - `data/mock_notion.json` 파일 사용
  
- [ ] **또는** MCP 사용 시:
  - [ ] `NOTION_API_KEY` Secrets에 추가
  - [ ] `NOTION_DATABASE_ID` Secrets에 추가
  - [ ] `USE_NOTION_MCP=true` Secrets에 추가
  - [ ] Notion API 권한 확인
  - [ ] 배포 후 Logs 확인 (서브프로세스 실행 여부)

### 2️⃣ **로컬 테스트 (MCP 모드)**

```bash
# .env 설정
USE_NOTION_MCP=true
NOTION_API_KEY=ntn_...
NOTION_DATABASE_ID=2976b5ca-...

# 테스트
python test_mcp_mode.py

# 정상 작동 확인
streamlit run app.py
```

### 3️⃣ **requirements.txt 확인**

현재 `requirements.txt`:
```txt
crewai>=0.28.0
crewai-tools>=0.2.0
openai>=1.12.0
streamlit>=1.31.0
python-dotenv>=1.0.0
mcp>=0.9.0              # ← MCP 필요
pydantic>=2.6.0
langchain-openai>=0.1.0
notion-client>=2.0.0    # ← Notion API 필요
nest-asyncio>=1.5.0     # ← 비동기 충돌 방지
```

✅ 모두 포함되어 있음!

---

## 🎯 **권장 배포 설정**

### **Option A: Mock 모드 (권장! 안정적)**

```toml
# Streamlit Cloud Secrets
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4o-mini"
USE_NOTION_MCP = "false"  # ← Mock 모드
```

**장점**:
- ✅ 서브프로세스 문제 없음
- ✅ 안정적 작동
- ✅ 빠른 응답 속도
- ✅ Notion API 불필요

**단점**:
- ⚠️ 실시간 Notion 데이터 미사용
- ⚠️ `data/mock_notion.json` 고정 데이터

---

### **Option B: MCP 모드 (고급, 주의 필요)**

```toml
# Streamlit Cloud Secrets
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "gpt-4o-mini"
USE_NOTION_MCP = "true"  # ← MCP 모드
NOTION_API_KEY = "ntn_..."
NOTION_DATABASE_ID = "2976b5ca-..."
```

**장점**:
- ✅ 실시간 Notion 데이터 사용
- ✅ 데이터 자동 업데이트

**단점**:
- ⚠️ Streamlit Cloud에서 서브프로세스 실행 안 될 수 있음
- ⚠️ Notion API 키 필요
- ⚠️ 응답 속도 느릴 수 있음
- ⚠️ 디버깅 어려움

**배포 후 확인사항**:
1. Streamlit Cloud → Manage app → Logs 확인
2. "MCP 서버 시작" 로그 확인
3. "MCP 연결 오류" 없는지 확인

---

## 🔧 **현재 배포 상태 진단**

### 배포했는데 문제가 생긴다면?

#### 증상 1: "MCP 연결 오류"
```
MCP 연결 오류: [Errno 2] No such file or directory: 'python'
```
**원인**: Streamlit Cloud에서 서브프로세스 실행 차단됨  
**해결**: `USE_NOTION_MCP=false`로 변경

#### 증상 2: "NOTION_API_KEY not found"
```
⚠️ NOTION_API_KEY가 설정되지 않았습니다.
```
**원인**: Secrets에 Notion API 키 미설정  
**해결**: Secrets에 `NOTION_API_KEY` 추가

#### 증상 3: 앱이 느리거나 멈춤
**원인**: MCP 서버 시작 시간 또는 Notion API 호출 지연  
**해결**: Mock 모드로 전환 또는 타임아웃 늘리기

#### 증상 4: 사용자 데이터 혼선
**원인**: `CURRENT_NOTION_USER` 환경 변수 전달 문제  
**해결**: Mock 모드 사용 또는 세션 관리 강화

---

## 📝 **배포 가이드 업데이트 권장사항**

### `DEPLOYMENT.md`에 추가할 내용:

```markdown
## ⚠️ Notion MCP 사용 시 주의사항

**Streamlit Cloud에서는 Mock 모드 (`USE_NOTION_MCP=false`) 권장!**

### 이유:
1. Streamlit Cloud는 서브프로세스 실행을 제한합니다
2. MCP 서버가 별도 프로세스로 실행되므로 차단될 수 있습니다
3. Mock 모드가 더 안정적이고 빠릅니다

### MCP 모드를 사용해야 한다면:
1. 로컬에서 먼저 충분히 테스트
2. Notion API 키를 Secrets에 올바르게 설정
3. 배포 후 Logs를 꼼꼼히 확인
4. "MCP 연결 오류" 발생 시 Mock 모드로 전환
```

---

## 🎯 **최종 권장사항**

### ✅ **지금 바로 확인할 것**

1. **배포된 앱 접속해서 테스트**
   - 사용자 선택 화면이 뜨는가?
   - 챗봇이 정상 작동하는가?
   - "오늘 저녁 메뉴 추천해줘" 입력 시 응답이 오는가?

2. **Streamlit Cloud Logs 확인**
   ```
   Dashboard → Your App → ⋮ Menu → Manage app → Logs
   ```
   - "MCP 서버" 관련 로그 확인
   - 에러 메시지 확인

3. **문제 발생 시 즉시 조치**
   ```toml
   # Secrets 수정
   USE_NOTION_MCP = "false"  # ← Mock 모드로 전환
   ```
   - Save → 앱 자동 재배포
   - 2-3분 후 재확인

### ✅ **안전한 배포 설정**

```toml
# Streamlit Cloud Secrets (권장)
OPENAI_API_KEY = "sk-your-actual-key"
OPENAI_MODEL = "gpt-4o-mini"
USE_NOTION_MCP = "false"  # ← 이게 안전!
```

---

## 📞 **문제 해결 순서**

1. **로그 확인** → Streamlit Cloud Logs
2. **에러 메시지 확인** → "MCP", "Notion", "API" 키워드 검색
3. **Mock 모드로 전환** → `USE_NOTION_MCP=false`
4. **재배포 확인** → 2-3분 대기
5. **정상 작동 확인** → 사용자 선택 및 챗봇 테스트

---

**결론**: 
- ✅ **Mock 모드가 배포에 가장 안전하고 안정적입니다**
- ⚠️ **MCP 모드는 로컬 개발/테스트용으로 권장합니다**
- 🚨 **Streamlit Cloud에서 MCP 모드는 작동하지 않을 가능성이 높습니다**

