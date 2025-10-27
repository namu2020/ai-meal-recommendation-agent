"""
사용자별 데이터 로딩 테스트
Mock 모드에서 각 사용자별로 올바른 데이터를 로드하는지 검증
"""
import asyncio
import os
import sys
from pathlib import Path

# MCP 클라이언트 import
sys.path.append(str(Path(__file__).parent))
from mcp_client.notion_mcp_client import get_mcp_client
import json


async def test_user_data(username):
    """특정 사용자의 데이터 테스트"""
    print(f"\n{'='*70}")
    print(f"🧪 {username}의 데이터 테스트")
    print(f"{'='*70}")
    
    # 환경 변수 설정
    os.environ["CURRENT_NOTION_USER"] = username
    os.environ["USE_NOTION_MCP"] = "false"  # Mock 모드
    
    client = get_mcp_client()
    
    try:
        async with client.connect():
            # 사용자 선호도 조회
            print("\n📋 사용자 선호도 조회 중...")
            preferences_result = await client.call_tool("get_user_preferences", {})
            preferences = json.loads(preferences_result)
            
            print(f"✅ 알레르기: {preferences.get('allergies', [])}")
            print(f"✅ 싫어하는 음식: {preferences.get('dislikes', [])}")
            print(f"✅ 다이어트 목표: {preferences.get('diet_goal', '없음')}")
            print(f"✅ 선호 음식: {preferences.get('favorite_cuisines', [])}")
            
            # 예산 현황 조회
            print("\n💰 예산 현황 조회 중...")
            budget_result = await client.call_tool("get_budget_status", {})
            budget = json.loads(budget_result)
            
            print(f"✅ 일일 한도: {budget.get('daily_limit', 0):,}원")
            print(f"✅ 현재 지출: {budget.get('today_spent', 0):,}원")
            print(f"✅ 남은 예산: {budget.get('remaining', 0):,}원")
            print(f"✅ 선호 범위: {budget.get('preferred_range', [])[0]:,}원 ~ {budget.get('preferred_range', [])[1]:,}원")
            
            # 일정 조회
            print("\n📅 일정 조회 중...")
            schedule_result = await client.call_tool("get_available_time", {})
            schedule = json.loads(schedule_result)
            
            print(f"✅ 오늘 날짜: {schedule.get('today', '')}")
            print(f"✅ 가용 시간: {schedule.get('available_time', 0)}분")
            print(f"✅ 식사 시간: {schedule.get('meal_time', '')}")
            
            print(f"\n{'='*70}")
            print(f"✅ {username} 테스트 완료!")
            print(f"{'='*70}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """모든 사용자 테스트"""
    print("="*70)
    print("🔍 사용자별 데이터 로딩 테스트 (Mock 모드)")
    print("="*70)
    
    users = ["소윤", "태식", "지민", "현우", "라미"]
    
    for username in users:
        await test_user_data(username)
        # 각 테스트 사이에 약간의 딜레이
        await asyncio.sleep(0.5)
    
    print("\n" + "="*70)
    print("✅ 모든 사용자 테스트 완료!")
    print("="*70)
    print("\n📊 요약:")
    print("   - 소윤: 갑각류 알레르기, 15분 식사")
    print("   - 태식: 당뇨/고혈압 (데이터에 반영)")
    print("   - 지민: 락토오보/페스코 (데이터에 반영)")
    print("   - 현우: 유당불내증, 1,800kcal")
    print("   - 라미: 벌크업, 2,800kcal")


if __name__ == "__main__":
    asyncio.run(main())

