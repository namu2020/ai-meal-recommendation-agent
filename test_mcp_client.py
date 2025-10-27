"""
MCP 클라이언트 테스트 스크립트
Notion MCP 서버와의 연결을 테스트합니다.
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 Python path에 추가
sys.path.append(str(Path(__file__).parent))

from mcp_client.notion_mcp_client import get_mcp_client


async def test_mcp_connection():
    """MCP 연결 테스트"""
    print("🔗 Notion MCP 서버 연결 테스트 시작...\n")
    
    client = get_mcp_client()
    
    try:
        async with client.connect():
            print("✅ MCP 서버 연결 성공!\n")
            
            # 도구 목록 조회
            print("📋 사용 가능한 도구 목록:")
            tools = await client.list_tools()
            for tool in tools:
                print(f"  - {tool.name}: {tool.description}")
            print()
            
            # 사용자 선호도 조회 테스트
            print("🧪 테스트 1: 사용자 선호도 조회")
            result = await client.call_tool("get_user_preferences", {})
            print(f"결과:\n{result}\n")
            
            # 식단 기록 조회 테스트
            print("🧪 테스트 2: 최근 3일 식단 기록 조회")
            result = await client.call_tool("get_meal_history", {"days": 3})
            print(f"결과:\n{result}\n")
            
            # 일정 조회 테스트
            print("🧪 테스트 3: 사용자 일정 조회")
            result = await client.call_tool("get_available_time", {})
            print(f"결과:\n{result}\n")
            
            # 예산 조회 테스트
            print("🧪 테스트 4: 예산 현황 조회")
            result = await client.call_tool("get_budget_status", {})
            print(f"결과:\n{result}\n")
            
            print("✅ 모든 테스트 완료!")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_resource_read():
    """리소스 읽기 테스트"""
    print("\n" + "="*60)
    print("📚 리소스 읽기 테스트\n")
    
    client = get_mcp_client()
    
    try:
        async with client.connect():
            # 식단 기록 리소스 읽기
            print("🧪 리소스 읽기: notion://meal/history")
            result = await client.read_resource("notion://meal/history")
            print(f"결과:\n{result}\n")
            
            print("✅ 리소스 읽기 성공!")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")


if __name__ == "__main__":
    print("="*60)
    print("Notion MCP 클라이언트 테스트")
    print("="*60 + "\n")
    
    # 도구 호출 테스트
    asyncio.run(test_mcp_connection())
    
    # 리소스 읽기 테스트
    asyncio.run(test_resource_read())
    
    print("\n" + "="*60)
    print("테스트 완료!")
    print("="*60)

