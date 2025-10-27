# Notion MCP 빠른 시작 가이드 🚀

실제 Notion 데이터를 MCP를 통해 CrewAI에 연결하는 최소 단계 가이드입니다.

---

## ✅ 사전 준비 완료 항목

이미 구현된 파일들:
- ✅ `mcp_client/notion_mcp_client.py` - MCP 클라이언트
- ✅ `mcp_servers/notion_server.py` - MCP 서버 (Mock 데이터)
- ✅ `tools/notion_tools_mcp.py` - MCP 연동 도구
- ✅ `tools/__init__.py` - Mock/MCP 자동 전환
- ✅ `test_mcp_client.py` - MCP 연결 테스트 스크립트

---

## 🎯 단계별 실행 방법

### 1️⃣ Mock 데이터로 MCP 테스트 (Notion API 없이)

현재 상태에서도 MCP 아키텍처를 바로 테스트할 수 있습니다!

```bash
# 1. 추가 패키지 설치
pip install notion-client nest-asyncio

# 2. .env 파일에 MCP 모드 활성화
echo "USE_NOTION_MCP=true" >> .env

# 3. MCP 연결 테스트
python test_mcp_client.py

# 4. Streamlit 앱 실행 (MCP 모드)
streamlit run app.py
```

**이 단계에서는**:
- MCP 서버가 `mock_notion.json` 데이터를 사용
- MCP 클라이언트 ↔ 서버 통신 구조 확인
- CrewAI 도구들이 MCP를 통해 데이터 가져오기

---

### 2️⃣ 실제 Notion과 연결하기 (나중에)

실제 Notion API와 연결하려면:

#### A. Notion Integration 생성
1. https://www.notion.so/my-integrations 접속
2. "New integration" 생성
3. Integration Token 복사

#### B. Notion Database 설정
1. Notion에서 데이터베이스 생성 (음식 기록, 선호도, 일정, 예산)
2. Database를 Integration에 연결
3. Database ID 복사

#### C. .env 파일 설정
```bash
USE_NOTION_MCP=true
NOTION_API_KEY=secret_xxxxxxxxxxxxxxx
NOTION_DATABASE_ID=abc123def456
```

#### D. MCP 서버 수정
`mcp_servers/notion_server.py`에서 Mock 데이터 대신 실제 Notion API 호출:

```python
from notion_client import AsyncClient

notion = AsyncClient(auth=os.getenv("NOTION_API_KEY"))

async def query_notion_database():
    response = await notion.databases.query(
        database_id=os.getenv("NOTION_DATABASE_ID")
    )
    # 데이터 파싱...
    return parsed_data
```

---

## 🔄 Mock ↔ MCP 모드 전환

`.env` 파일에서 간단히 전환:

```bash
# Mock 모드 (기본, 빠른 개발/테스트)
USE_NOTION_MCP=false

# MCP 모드 (실제 MCP 아키텍처 사용)
USE_NOTION_MCP=true
```

---

## 🧪 테스트 순서

### 테스트 1: MCP 서버 단독 실행
```bash
# 터미널 1: MCP 서버 실행
python mcp_servers/notion_server.py
```

서버가 시작되면 stdin/stdout으로 JSON-RPC 메시지를 기다립니다.

### 테스트 2: MCP 클라이언트 테스트
```bash
# 터미널 2: 클라이언트 테스트
python test_mcp_client.py
```

예상 출력:
```
🔗 Notion MCP 서버 연결 테스트 시작...
✅ MCP 서버 연결 성공!

📋 사용 가능한 도구 목록:
  - get_meal_history: 사용자의 최근 식단 기록 조회
  - get_user_preferences: 사용자의 알레르기, 선호도, 다이어트 목표 조회
  ...
```

### 테스트 3: CrewAI 통합 테스트
```bash
# USE_NOTION_MCP=true로 설정 후
streamlit run app.py
```

앱 시작 시 콘솔에:
```
🔗 Notion MCP 모드 활성화
```

---

## 📊 아키텍처 흐름

### Mock 모드 (USE_NOTION_MCP=false)
```
CrewAI Agent
    ↓
tools/notion_tools.py
    ↓
data/mock_notion.json (직접 읽기)
```

### MCP 모드 (USE_NOTION_MCP=true)
```
CrewAI Agent
    ↓
tools/notion_tools_mcp.py
    ↓
mcp_client/notion_mcp_client.py (클라이언트)
    ↓ stdio (subprocess)
mcp_servers/notion_server.py (서버)
    ↓
data/mock_notion.json (또는 실제 Notion API)
```

---

## 🐛 문제 해결

### 문제: "Not connected to MCP server"
**해결**: 
- MCP 서버 경로 확인
- `test_mcp_client.py`로 연결 테스트

### 문제: "Module 'mcp' not found"
**해결**:
```bash
pip install mcp>=0.9.0
```

### 문제: asyncio 관련 오류
**해결**:
```bash
pip install nest-asyncio
```

---

## 📝 현재 구현 상태

| 기능 | Mock 모드 | MCP 모드 (Mock 데이터) | MCP 모드 (실제 Notion) |
|------|-----------|------------------------|----------------------|
| 식단 기록 조회 | ✅ | ✅ | ⚠️ (서버 수정 필요) |
| 사용자 선호도 | ✅ | ✅ | ⚠️ (서버 수정 필요) |
| 일정 조회 | ✅ | ✅ | ⚠️ (서버 수정 필요) |
| 예산 조회 | ✅ | ✅ | ⚠️ (서버 수정 필요) |

**현재 권장**: MCP 모드 (Mock 데이터)로 아키텍처 테스트!

---

## 🎯 다음 단계

1. **현재 단계**: Mock 데이터로 MCP 아키텍처 완벽 동작 확인 ✅
2. **다음 단계**: Notion API 파싱 로직 구현
3. **최종 단계**: 실제 Notion 데이터베이스 연결

---

## 💡 팁

- 개발 중에는 `USE_NOTION_MCP=false` (빠름)
- MCP 아키텍처 테스트는 `USE_NOTION_MCP=true` + Mock 데이터
- 프로덕션에서는 `USE_NOTION_MCP=true` + 실제 Notion API

**질문이 있다면**: `NOTION_MCP_INTEGRATION.md` 참고!

