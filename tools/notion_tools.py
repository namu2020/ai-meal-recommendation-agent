"""
노션 MCP 서버와 연동하는 CrewAI 도구
"""
import json
import os
import asyncio
from pathlib import Path
from crewai.tools import tool
from typing import Optional, Annotated
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()

# USE_NOTION_MCP 설정 확인
USE_NOTION_MCP = os.getenv("USE_NOTION_MCP", "false").lower() == "true"

# Mock 데이터 경로
DATA_PATH = Path(__file__).parent.parent / "data" / "mock_notion.json"


def load_notion_data():
    """노션 데이터 로드 (Mock 모드)"""
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


# MCP 클라이언트 함수들 (지연 import)
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
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from mcp_client.notion_mcp_client import get_mcp_client
    
    client = get_mcp_client()
    
    async with client.connect():
        result = await client.call_tool("get_meal_history", {"days": days})
        return result


async def _get_user_preferences_async() -> str:
    """비동기 사용자 선호도 조회"""
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from mcp_client.notion_mcp_client import get_mcp_client
    
    client = get_mcp_client()
    
    async with client.connect():
        result = await client.call_tool("get_user_preferences", {})
        return result


async def _get_user_schedule_async() -> str:
    """비동기 사용자 일정 조회"""
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from mcp_client.notion_mcp_client import get_mcp_client
    
    client = get_mcp_client()
    
    async with client.connect():
        result = await client.call_tool("get_available_time", {})
        return result


async def _get_budget_status_async() -> str:
    """비동기 예산 현황 조회"""
    import sys
    sys.path.append(str(Path(__file__).parent.parent))
    from mcp_client.notion_mcp_client import get_mcp_client
    
    client = get_mcp_client()
    
    async with client.connect():
        result = await client.call_tool("get_budget_status", {})
        return result


@tool("식단 기록 조회")
def get_meal_history(days: Annotated[int, Field(description="조회할 일수", default=7)] = 7) -> str:
    """
    사용자의 최근 식단 기록을 조회합니다.
    최근 며칠간 먹은 음식, 칼로리, 비용 정보를 확인할 수 있습니다.
    
    Args:
        days: 조회할 일수 (기본값: 7일)
    
    Returns:
        식단 기록 정보
    """
    if USE_NOTION_MCP:
        # MCP 모드: JSON 데이터를 사람이 읽기 쉬운 형태로 변환
        json_result = run_async(_get_meal_history_async(days))
        import json
        try:
            meals = json.loads(json_result)
            
            if not meals or len(meals) == 0:
                return "⚠️ 식단 기록이 없습니다."
            
            result = f"=== 최근 {days}일 식단 기록 (Notion 실시간 데이터) ===\n\n"
            result += f"📊 총 {len(meals)}개 식사 기록\n\n"
            
            # 날짜별로 그룹화
            from collections import defaultdict
            by_date = defaultdict(list)
            for meal in meals:
                if isinstance(meal, dict) and 'date' in meal:
                    by_date[meal['date']].append(meal)
            
            # 최신 날짜부터 표시
            sorted_dates = sorted(by_date.keys(), reverse=True)
            
            total_calories = 0
            total_cost = 0
            
            for date in sorted_dates[:days]:
                result += f"\n📅 {date}\n"
                day_calories = 0
                day_cost = 0
                
                for meal in by_date[date]:
                    meal_type = meal.get('type', '')
                    meal_name = meal.get('meal', '')
                    calories = meal.get('calories', 0)
                    cost = meal.get('cost', 0)
                    
                    day_calories += calories
                    day_cost += cost
                    
                    result += f"   • {meal_type}: {meal_name}\n"
                    result += f"     칼로리: {calories}kcal | 비용: {cost:,}원\n"
                
                result += f"   💡 하루 합계: {day_calories}kcal | {day_cost:,}원\n"
                
                total_calories += day_calories
                total_cost += day_cost
            
            # 평균 계산
            num_days = len(sorted_dates[:days])
            if num_days > 0:
                avg_calories = total_calories / num_days
                avg_cost = total_cost / num_days
                
                result += f"\n📈 **평균 (최근 {num_days}일)**:\n"
                result += f"   • 칼로리: {avg_calories:.0f}kcal/일\n"
                result += f"   • 비용: {avg_cost:,.0f}원/일\n"
            
            return result
        except Exception as e:
            return f"⚠️ 데이터 파싱 실패: {str(e)}\n원본: {json_result}"
    else:
        # Mock 모드
        data = load_notion_data()
        history = data["meal_history"][:days]
        
        if not history:
            return "식단 기록이 없습니다."
        
        avg_calories = sum(m["calories"] for m in history) / len(history)
        total_cost = sum(m["cost"] for m in history)
        
        result = f"최근 {days}일 식단 기록:\n\n"
        for meal in history:
            result += f"- {meal['date']} {meal['type']}: {meal['meal']} ({meal['calories']}kcal, {meal['cost']:,}원)\n"
        
        result += f"\n평균 칼로리: {avg_calories:.0f}kcal\n"
        result += f"총 지출: {total_cost:,}원\n"
        
        return result


@tool("사용자 선호도 조회")
def get_user_preferences() -> str:
    """
    사용자의 음식 선호도, 알레르기 정보, 건강 상태, 다이어트 목표를 조회합니다.
    알레르기, 당뇨, 고혈압 등 건강 제약사항과 선호하는 음식 종류 등을 확인할 수 있습니다.
    
    Returns:
        사용자 선호도 정보
    """
    if USE_NOTION_MCP:
        # MCP 모드: JSON 데이터를 사람이 읽기 쉬운 형태로 변환
        json_result = run_async(_get_user_preferences_async())
        import json
        try:
            prefs = json.loads(json_result)
            
            result = "=== 사용자 선호도 정보 (Notion 실시간 데이터) ===\n\n"
            
            # 🔥 건강 상태 - 최우선 확인!
            health_conditions = prefs.get('health_conditions', [])
            if health_conditions:
                result += f"🏥 **건강 상태 (최우선 고려!)**: {', '.join(health_conditions)}\n"
                result += f"   → 건강 제약에 맞는 메뉴만 추천해야 합니다!\n"
                
                # 당뇨 체크
                if any('당뇨' in c for c in health_conditions):
                    result += f"   🩸 당뇨: 저당, 저탄수화물, 저GI 식품 필수!\n"
                # 고혈압 체크
                if any('고혈압' in c for c in health_conditions):
                    result += f"   💊 고혈압: 저염식 필수! 나트륨 제한!\n"
                result += "\n"
            
            # 식이 제한사항
            restrictions = prefs.get('dietary_restrictions', {})
            if restrictions:
                result += f"📊 **식이 제한사항**:\n"
                if 'carb_limit' in restrictions:
                    result += f"   • 탄수화물 한도: {restrictions['carb_limit']}g/일\n"
                if 'sodium_limit' in restrictions:
                    result += f"   • 나트륨 한도: {restrictions['sodium_limit']}mg/일\n"
                if 'raw' in restrictions:
                    result += f"   • 기타 제한: {restrictions['raw']}\n"
                result += "\n"
            
            # 알레르기
            if prefs.get('allergies'):
                result += f"⚠️ **알레르기**: {', '.join(prefs['allergies'])}\n"
                result += f"   → 이 식재료가 포함된 메뉴는 절대 추천 금지!\n\n"
            else:
                result += f"✅ 알레르기: 없음\n\n"
            
            # 싫어하는 음식
            if prefs.get('dislikes'):
                result += f"👎 싫어하는 음식: {', '.join(prefs['dislikes'])}\n"
                result += f"   → 가능한 피해서 추천해주세요\n\n"
            
            # 선호 음식
            if prefs.get('favorite_cuisines'):
                result += f"❤️ 선호하는 음식: {', '.join(prefs['favorite_cuisines'])}\n"
                result += f"   → 이 종류의 메뉴를 우선 추천!\n\n"
            
            # 요리 실력
            result += f"👨‍🍳 요리 실력: {prefs.get('cooking_skill', '중급')}\n"
            if 'cooking_notes' in prefs:
                result += f"   상세: {prefs['cooking_notes']}\n"
            
            # 매운맛 선호도
            result += f"🌶️ 매운맛 선호도: {prefs.get('spicy_level', '보통')}\n"
            
            # 다이어트 목표 (있으면)
            if prefs.get('diet_goal'):
                result += f"🎯 다이어트 목표: {prefs.get('diet_goal')}\n"
            
            return result
        except Exception as e:
            return f"⚠️ 데이터 파싱 실패: {str(e)}\n원본: {json_result}"
    else:
        # Mock 모드
        data = load_notion_data()
        prefs = data["preferences"]
        
        result = "=== 사용자 선호도 정보 ===\n\n"
        
        # 알레르기 - 가장 중요!
        if prefs.get('allergies'):
            result += f"⚠️ **알레르기 (필수 확인!)**: {', '.join(prefs['allergies'])}\n"
            result += f"   → 이 식재료가 포함된 메뉴는 절대 추천 금지!\n\n"
        else:
            result += f"✅ 알레르기: 없음\n\n"
        
        # 싫어하는 음식
        if prefs.get('dislikes'):
            result += f"👎 싫어하는 음식: {', '.join(prefs['dislikes'])}\n\n"
        
        # 선호 음식
        if prefs.get('favorite_cuisines'):
            result += f"❤️ 선호하는 음식: {', '.join(prefs['favorite_cuisines'])}\n"
            result += f"   → 이 종류의 메뉴를 우선 추천!\n\n"
        
        result += f"🎯 다이어트 목표: {prefs['diet_goal']}\n"
        result += f"🌶️ 매운맛 선호도: {prefs['spicy_level']}\n"
        result += f"👨‍🍳 요리 실력: {prefs['cooking_skill']}\n"
        
        return result


@tool("사용자 일정 조회")
def get_user_schedule() -> str:
    """
    사용자의 오늘 일정과 식사 준비 가능 시간을 조회합니다.
    조리에 사용할 수 있는 시간을 파악하여 적절한 메뉴를 추천할 수 있습니다.
    
    Returns:
        사용자 일정 정보
    """
    if USE_NOTION_MCP:
        # MCP 모드: JSON 데이터를 사람이 읽기 쉬운 형태로 변환
        json_result = run_async(_get_user_schedule_async())
        import json
        try:
            schedule = json.loads(json_result)
            
            result = "=== 사용자 일정 정보 (Notion 실시간 데이터) ===\n\n"
            result += f"📅 날짜: {schedule.get('today', '오늘')}\n"
            result += f"🍽️ 식사 시간: {schedule.get('meal_time', '점심')}\n"
            result += f"⏰ 가용 시간: {schedule.get('available_time', 30)}분\n\n"
            
            avail_time = schedule.get('available_time', 30)
            if avail_time <= 15:
                result += "⚠️ **매우 긴급!** 15분 이하로 먹을 수 있는 초고속 메뉴만 추천!\n"
                result += "   → 배달 음식, 즉석 조리 음식, 간편식 추천\n"
            elif avail_time <= 30:
                result += "⚠️ 시간이 부족합니다. 빠르게 조리/배달 가능한 메뉴 추천!\n"
                result += "   → 30분 이내 조리 또는 배달 가능한 메뉴\n"
            else:
                result += "✅ 시간 여유 있음. 다양한 메뉴 추천 가능\n"
            
            return result
        except:
            return json_result
    else:
        # Mock 모드
        data = load_notion_data()
        schedule = data["schedule"]
        
        result = "=== 사용자 일정 정보 ===\n\n"
        result += f"📅 날짜: {schedule['today']}\n"
        result += f"🍽️ 식사 시간: {schedule['meal_time']}\n"
        result += f"⏰ 가용 시간: {schedule['available_time']}분\n\n"
        
        if schedule['available_time'] <= 15:
            result += "⚠️ **매우 긴급!** 15분 이하로 먹을 수 있는 초고속 메뉴만 추천!\n"
        elif schedule['available_time'] <= 30:
            result += "⚠️ 시간이 부족합니다. 빠르게 조리/배달 가능한 메뉴 추천!\n"
        else:
            result += "✅ 시간 여유 있음. 다양한 메뉴 추천 가능\n"
        
        return result


@tool("예산 현황 조회")
def get_budget_status() -> str:
    """
    사용자의 일일 예산과 현재까지 지출 현황을 조회합니다.
    남은 예산 내에서 적절한 가격대의 메뉴를 추천할 수 있습니다.
    
    Returns:
        예산 현황 정보
    """
    if USE_NOTION_MCP:
        # MCP 모드: JSON 데이터를 사람이 읽기 쉬운 형태로 변환
        json_result = run_async(_get_budget_status_async())
        import json
        try:
            result_data = json.loads(json_result)
            
            budget = result_data
            remaining = budget.get('remaining', budget.get('daily_limit', 20000) - budget.get('today_spent', 0))
            
            result = "=== 예산 현황 (Notion 실시간 데이터) ===\n\n"
            result += f"💰 일일 예산: {budget.get('daily_limit', 20000):,}원\n"
            result += f"💸 오늘 지출: {budget.get('today_spent', 0):,}원\n"
            result += f"💵 남은 예산: {remaining:,}원\n"
            
            pref_range = budget.get('preferred_range', [8000, 15000])
            result += f"📊 선호 가격대: {pref_range[0]:,}원 ~ {pref_range[1]:,}원\n\n"
            
            if remaining <= 0:
                result += "🚨 **예산 초과!** 집밥이나 매우 저렴한 메뉴만 추천!\n"
            elif remaining < 5000:
                result += "⚠️ 남은 예산 적음. 5,000원 이하 가성비 메뉴 추천!\n"
            elif remaining < 10000:
                result += "✅ 예산 적당. 10,000원 이하 메뉴 추천\n"
            else:
                result += "✅ 예산 여유 있음. 다양한 가격대 메뉴 가능\n"
            
            result += f"\n💡 추천: {pref_range[0]:,}원 ~ {pref_range[1]:,}원 범위 메뉴 우선 추천!\n"
            
            return result
        except:
            return json_result
    else:
        # Mock 모드
        data = load_notion_data()
        budget = data["budget"]
        
        remaining = budget["daily_limit"] - budget["today_spent"]
        
        result = "=== 예산 현황 ===\n\n"
        result += f"💰 일일 예산: {budget['daily_limit']:,}원\n"
        result += f"💸 오늘 지출: {budget['today_spent']:,}원\n"
        result += f"💵 남은 예산: {remaining:,}원\n"
        result += f"📊 선호 가격대: {budget['preferred_range'][0]:,}원 ~ {budget['preferred_range'][1]:,}원\n\n"
        
        if remaining <= 0:
            result += "🚨 **예산 초과!** 집밥이나 매우 저렴한 메뉴만 추천!\n"
        elif remaining < 5000:
            result += "⚠️ 남은 예산 적음. 5,000원 이하 가성비 메뉴 추천!\n"
        elif remaining < 10000:
            result += "✅ 예산 적당. 10,000원 이하 메뉴 추천\n"
        else:
            result += "✅ 예산 여유 있음. 다양한 가격대 메뉴 가능\n"
        
        result += f"\n💡 추천: {budget['preferred_range'][0]:,}원 ~ {budget['preferred_range'][1]:,}원 범위 메뉴 우선 추천!\n"
        
        return result

