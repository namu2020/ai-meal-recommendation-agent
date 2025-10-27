"""
모든 사용자 데이터 분석 및 검증
"""
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mcp_servers.notion_server_real import query_notion_pages

async def analyze_user(username):
    """특정 사용자 데이터 분석"""
    os.environ["CURRENT_NOTION_USER"] = username
    
    data = await query_notion_pages()
    
    print(f"\n{'='*80}")
    print(f"👤 {username}")
    print(f"{'='*80}")
    print(f"알레르기: {', '.join(data['preferences']['allergies']) if data['preferences']['allergies'] else '없음'}")
    print(f"싫어하는 음식: {', '.join(data['preferences']['dislikes']) if data['preferences']['dislikes'] else '없음'}")
    print(f"다이어트 목표: {data['preferences']['diet_goal']}")
    print(f"선호 요리: {', '.join(data['preferences']['favorite_cuisines'])}")
    print(f"매운맛 선호도: {data['preferences']['spicy_level']}")
    print(f"요리 실력: {data['preferences']['cooking_skill']}")
    print()
    print(f"📅 오늘: {data['schedule']['today']}")
    print(f"⏰ 가용 시간: {data['schedule']['available_time']}분")
    print(f"🍽️ 식사 시간: {data['schedule']['meal_time']}")
    print()
    print(f"💰 일일 예산: {data['budget']['daily_limit']:,}원")
    print(f"💸 오늘 지출: {data['budget']['today_spent']:,}원")
    print(f"📊 선호 가격대: {data['budget']['preferred_range'][0]:,}원 ~ {data['budget']['preferred_range'][1]:,}원")
    
    return data

async def main():
    print("="*80)
    print("🔍 모든 사용자 데이터 분석")
    print("="*80)
    
    users = ["소윤", "태식", "지민", "현우", "라미"]
    
    all_data = {}
    for username in users:
        try:
            data = await analyze_user(username)
            all_data[username] = data
        except Exception as e:
            print(f"\n❌ {username} 분석 실패: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ 분석 완료!")
    print("="*80)
    
    # 요약 비교
    print("\n📊 페르소나 요약 비교:")
    print("="*80)
    for username, data in all_data.items():
        allergies = ', '.join(data['preferences']['allergies']) if data['preferences']['allergies'] else '없음'
        time = data['schedule']['available_time']
        budget = data['budget']['daily_limit']
        
        print(f"{username:6s} | 알레르기: {allergies:15s} | 시간: {time:2d}분 | 예산: {budget:7,d}원")

if __name__ == "__main__":
    asyncio.run(main())

