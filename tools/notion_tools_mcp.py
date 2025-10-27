"""
노션 MCP 클라이언트를 통한 CrewAI 도구
실제 MCP 서버와 통신하여 데이터 가져오기
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
        if loop.is_running():
            # 이미 실행 중인 이벤트 루프가 있으면 새 루프 생성
            import nest_asyncio
            nest_asyncio.apply()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


async def _get_meal_history_async(days: int = 7) -> str:
    """비동기 식단 기록 조회"""
    client = get_mcp_client()
    
    try:
        async with client.connect():
            result = await client.call_tool("get_meal_history", {"days": days})
            return result
    except Exception as e:
        return f"MCP 연결 오류: {str(e)}"


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
    
    try:
        async with client.connect():
            result = await client.call_tool("get_user_preferences", {})
            return result
    except Exception as e:
        return f"MCP 연결 오류: {str(e)}"


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
    
    try:
        async with client.connect():
            result = await client.call_tool("get_available_time", {})
            return result
    except Exception as e:
        return f"MCP 연결 오류: {str(e)}"


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
    
    try:
        async with client.connect():
            result = await client.call_tool("get_budget_status", {})
            return result
    except Exception as e:
        return f"MCP 연결 오류: {str(e)}"


@tool("예산 현황 조회")
def get_budget_status() -> str:
    """
    사용자의 일일 예산과 현재까지 지출 현황을 조회합니다.
    남은 예산 내에서 적절한 가격대의 메뉴를 추천할 수 있습니다.
    
    Returns:
        예산 현황 정보
    """
    return run_async(_get_budget_status_async())

