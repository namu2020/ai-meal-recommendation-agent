# Notion MCP 통합 가이드

실제 Notion 데이터를 MCP를 통해 CrewAI에 연결하는 방법입니다.

---

## 📝 전체 흐름

```
Notion Database
    ↓
MCP Server (notion_server.py) - stdio 통신
    ↓
MCP Client (새로 생성) - subprocess로 서버 호출
    ↓
CrewAI Tools (notion_tools.py 수정)
    ↓
CrewAI Agents
```

---

## 🔧 1단계: Notion API 설정

### 1.1 Notion Integration 생성

1. https://www.notion.so/my-integrations 접속
2. "New integration" 클릭
3. Integration 이름: "CrewAI Food App"
4. Capabilities: "Read content" 체크
5. Integration Secret 복사 (나중에 사용)

### 1.2 Database 연결

1. Notion에서 음식 추천 데이터베이스 페이지 열기
2. 우측 상단 "..." → "Connections" → 위에서 만든 Integration 추가
3. Database ID 복사:
   - URL이 `https://notion.so/workspace/abc123def456?v=...` 형태라면
   - `abc123def456`이 Database ID

### 1.3 환경 변수 설정

`.env` 파일에 추가:
```bash
# Notion API
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxx
NOTION_DATABASE_ID=abc123def456
```

---

## 🚀 2단계: 파일 생성 및 수정

### 2.1 MCP 클라이언트 생성

**새 파일: `mcp_client/notion_mcp_client.py`**

```python
"""
Notion MCP 클라이언트
MCP 서버와 stdio 통신하여 Notion 데이터 가져오기
"""
import asyncio
import json
from typing import Optional, Any
from contextlib import asynccontextmanager
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class NotionMCPClient:
    """Notion MCP 서버와 통신하는 클라이언트"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self._read = None
        self._write = None
    
    @asynccontextmanager
    async def connect(self):
        """MCP 서버에 연결"""
        server_params = StdioServerParameters(
            command="python",
            args=["-u", "mcp_servers/notion_server.py"],
            env=None
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                self.session = session
                yield self
    
    async def call_tool(self, tool_name: str, arguments: dict = None) -> str:
        """MCP 도구 호출"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        if arguments is None:
            arguments = {}
        
        result = await self.session.call_tool(tool_name, arguments)
        
        # TextContent에서 텍스트 추출
        if result.content:
            return result.content[0].text
        return ""
    
    async def read_resource(self, uri: str) -> str:
        """리소스 읽기"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        result = await self.session.read_resource(uri)
        
        if result.contents:
            return result.contents[0].text
        return ""


# 싱글톤 인스턴스 (모듈 레벨)
_client_instance = None


def get_mcp_client() -> NotionMCPClient:
    """MCP 클라이언트 싱글톤 인스턴스 반환"""
    global _client_instance
    if _client_instance is None:
        _client_instance = NotionMCPClient()
    return _client_instance
```

### 2.2 실제 Notion API와 연결하도록 MCP 서버 수정

**수정: `mcp_servers/notion_server.py`**

기존 `load_notion_data()` 함수를 실제 Notion API 호출로 변경:

```python
"""
노션 MCP 서버 - 실제 Notion API 연동
"""
import json
import asyncio
import os
from pathlib import Path
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from notion_client import AsyncClient
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# MCP 서버 인스턴스
app = Server("notion-meal-server")

# Notion 클라이언트
notion = AsyncClient(auth=os.getenv("NOTION_API_KEY"))
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")


async def query_notion_database():
    """Notion 데이터베이스에서 데이터 조회"""
    response = await notion.databases.query(database_id=DATABASE_ID)
    
    # Notion 데이터를 앱에서 사용하는 형태로 변환
    meal_history = []
    preferences = {}
    schedule = {}
    budget = {}
    
    for page in response["results"]:
        props = page["properties"]
        
        # 여기서 Notion 속성을 파싱
        # 예: props["날짜"]["date"], props["메뉴"]["title"] 등
        # 사용자의 Notion 구조에 맞게 파싱 로직 구현
        
    return {
        "meal_history": meal_history,
        "preferences": preferences,
        "schedule": schedule,
        "budget": budget
    }


# 나머지 @app.list_resources(), @app.call_tool() 등은 동일
# load_notion_data() 대신 query_notion_database() 사용
```

⚠️ **중요**: Notion 데이터베이스 구조에 맞춰 파싱 로직을 작성해야 합니다.

### 2.3 CrewAI Tools를 MCP 클라이언트 사용하도록 수정

**수정: `tools/notion_tools.py`**

```python
"""
노션 MCP 클라이언트를 통한 CrewAI 도구
"""
import asyncio
from crewai.tools import tool
import sys
from pathlib import Path

# MCP 클라이언트 import
sys.path.append(str(Path(__file__).parent.parent))
from mcp_client.notion_mcp_client import get_mcp_client


def run_async(coro):
    """비동기 함수를 동기적으로 실행"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


async def _get_meal_history_async(days: int = 7) -> str:
    """비동기 식단 기록 조회"""
    client = get_mcp_client()
    
    async with client.connect():
        result = await client.call_tool("get_meal_history", {"days": days})
        return result


@tool("식단 기록 조회")
def get_meal_history(days: int = 7) -> str:
    """
    사용자의 최근 식단 기록을 조회합니다.
    최근 며칠간 먹은 음식, 칼로리, 비용 정보를 확인할 수 있습니다.
    
    Args:
        days: 조회할 일수 (기본값: 7일)
    
    Returns:
        식단 기록 정보
    """
    return run_async(_get_meal_history_async(days))


async def _get_user_preferences_async() -> str:
    """비동기 사용자 선호도 조회"""
    client = get_mcp_client()
    
    async with client.connect():
        result = await client.call_tool("get_user_preferences", {})
        return result


@tool("사용자 선호도 조회")
def get_user_preferences() -> str:
    """
    사용자의 음식 선호도, 알레르기 정보, 다이어트 목표를 조회합니다.
    알레르기가 있는 음식, 싫어하는 음식, 선호하는 음식 종류 등을 확인할 수 있습니다.
    
    Returns:
        사용자 선호도 정보
    """
    return run_async(_get_user_preferences_async())


async def _get_user_schedule_async() -> str:
    """비동기 사용자 일정 조회"""
    client = get_mcp_client()
    
    async with client.connect():
        result = await client.call_tool("get_available_time", {})
        return result


@tool("사용자 일정 조회")
def get_user_schedule() -> str:
    """
    사용자의 오늘 일정과 식사 준비 가능 시간을 조회합니다.
    조리에 사용할 수 있는 시간을 파악하여 적절한 메뉴를 추천할 수 있습니다.
    
    Returns:
        사용자 일정 정보
    """
    return run_async(_get_user_schedule_async())


async def _get_budget_status_async() -> str:
    """비동기 예산 현황 조회"""
    client = get_mcp_client()
    
    async with client.connect():
        result = await client.call_tool("get_budget_status", {})
        return result


@tool("예산 현황 조회")
def get_budget_status() -> str:
    """
    사용자의 일일 예산과 현재까지 지출 현황을 조회합니다.
    남은 예산 내에서 적절한 가격대의 메뉴를 추천할 수 있습니다.
    
    Returns:
        예산 현황 정보
    """
    return run_async(_get_budget_status_async())
```

---

## 📦 3단계: 추가 의존성 설치

```bash
pip install notion-client
```

`requirements.txt`에 추가:
```
notion-client>=2.0.0
```

---

## 🧪 4단계: 테스트

### 4.1 MCP 서버 단독 테스트

```bash
# MCP 서버 실행
python mcp_servers/notion_server.py
```

별도 터미널에서:
```bash
# MCP 클라이언트로 테스트
python -c "
import asyncio
from mcp_client.notion_mcp_client import get_mcp_client

async def test():
    client = get_mcp_client()
    async with client.connect():
        result = await client.call_tool('get_user_preferences', {})
        print(result)

asyncio.run(test())
"
```

### 4.2 CrewAI Tools 테스트

```bash
python test_tools.py
```

### 4.3 전체 시스템 테스트

```bash
streamlit run app.py
```

---

## 🗂️ Notion 데이터베이스 구조 예시

합성 데이터를 Notion에 구성할 때 다음 구조를 권장합니다:

### Database 1: 식단 기록 (Meal History)
| 속성명 | 타입 | 설명 |
|--------|------|------|
| 날짜 | Date | 식사 날짜 |
| 시간 | Select | 아침/점심/저녁 |
| 메뉴 | Title | 먹은 음식 |
| 칼로리 | Number | kcal |
| 비용 | Number | 원 |

### Database 2: 사용자 선호도 (Preferences)
| 속성명 | 타입 | 설명 |
|--------|------|------|
| 알레르기 | Multi-select | 새우, 땅콩 등 |
| 싫어하는 음식 | Multi-select | 고수, 청양고추 등 |
| 다이어트 목표 | Select | 저칼로리/고단백 등 |
| 선호 요리 | Multi-select | 한식/일식 등 |
| 매운맛 선호도 | Select | 약함/보통/강함 |

### Database 3: 일정 (Schedule)
| 속성명 | 타입 | 설명 |
|--------|------|------|
| 날짜 | Date | 오늘 날짜 |
| 가용 시간 | Number | 분 |
| 식사 시간 | Select | 점심/저녁 |

### Database 4: 예산 (Budget)
| 속성명 | 타입 | 설명 |
|--------|------|------|
| 날짜 | Date | 오늘 날짜 |
| 일일 예산 | Number | 원 |
| 오늘 지출 | Number | 원 |
| 선호 가격대 최소 | Number | 원 |
| 선호 가격대 최대 | Number | 원 |

---

## 🔄 Mock → MCP 전환 옵션

개발 과정에서 Mock과 MCP를 쉽게 전환할 수 있도록:

**`config.py`에 추가:**
```python
# MCP 사용 여부 (False면 Mock 데이터 사용)
USE_NOTION_MCP = os.getenv("USE_NOTION_MCP", "false").lower() == "true"
```

**`tools/notion_tools.py` 수정:**
```python
if USE_NOTION_MCP:
    # MCP 클라이언트 사용
    from mcp_client.notion_mcp_client import get_mcp_client
    # ...
else:
    # Mock 데이터 사용 (기존 방식)
    def load_notion_data():
        # ...
```

`.env`에서 제어:
```bash
USE_NOTION_MCP=true   # MCP 사용
USE_NOTION_MCP=false  # Mock 사용
```

---

## ⚠️ 주의사항

1. **비동기 처리**: MCP는 비동기이므로 `asyncio`를 사용해야 합니다
2. **서버 실행**: MCP 서버는 subprocess로 자동 시작되지만, 디버깅 시 수동 실행도 가능
3. **데이터 파싱**: Notion API 응답 구조에 맞춰 파싱 로직을 반드시 수정해야 합니다
4. **에러 처리**: Notion API 호출 실패 시 fallback 로직 추가 권장

---

## 🎯 다음 단계

1. ✅ Notion Integration 생성 및 API Key 발급
2. ✅ Notion 데이터베이스 구조 설계 및 합성 데이터 입력
3. ✅ `.env`에 credentials 추가
4. ✅ `mcp_client/notion_mcp_client.py` 생성
5. ✅ `mcp_servers/notion_server.py` 수정 (Notion API 연동)
6. ✅ `tools/notion_tools.py` 수정 (MCP 클라이언트 사용)
7. ✅ 테스트 및 디버깅

완료되면 실시간으로 Notion 데이터가 CrewAI 에이전트에 전달됩니다! 🚀

