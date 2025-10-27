"""
Notion MCP 클라이언트
MCP 서버와 stdio 통신하여 Notion 데이터 가져오기
"""
import asyncio
import json
import os
from typing import Optional, Any
from contextlib import asynccontextmanager
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()


class NotionMCPClient:
    """Notion MCP 서버와 통신하는 클라이언트"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self._read = None
        self._write = None
        
        # 프로젝트 루트 경로 찾기
        self.project_root = Path(__file__).parent.parent
        
        # USE_NOTION_MCP 설정에 따라 서버 선택
        use_mcp = os.getenv("USE_NOTION_MCP", "false").lower() == "true"
        if use_mcp:
            self.server_script = "notion_server_real.py"
        else:
            self.server_script = "notion_server.py"
    
    @asynccontextmanager
    async def connect(self):
        """MCP 서버에 연결"""
        server_script = str(self.project_root / "mcp_servers" / self.server_script)
        
        # 🔥 중요: 부모 프로세스의 환경 변수를 MCP 서버로 전달
        # 이를 통해 app.py에서 설정한 CURRENT_NOTION_USER가 MCP 서버로 전달됨
        server_params = StdioServerParameters(
            command="python",
            args=["-u", server_script],
            env=os.environ.copy()  # ← 환경 변수 복사하여 전달!
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
    
    async def list_tools(self) -> list:
        """사용 가능한 도구 목록 조회"""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")
        
        result = await self.session.list_tools()
        return result.tools


# 싱글톤 인스턴스 (모듈 레벨)
_client_instance = None


def get_mcp_client() -> NotionMCPClient:
    """MCP 클라이언트 싱글톤 인스턴스 반환"""
    global _client_instance
    if _client_instance is None:
        _client_instance = NotionMCPClient()
    return _client_instance

