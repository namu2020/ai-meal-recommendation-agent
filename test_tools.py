"""
도구 테스트 스크립트 - 각 도구가 정상 작동하는지 확인
"""
from tools import (
    get_meal_history,
    get_user_preferences,
    get_user_schedule,
    get_budget_status,
    search_menu,
    filter_by_price,
    search_home_recipes,
)

def test_notion_tools():
    """노션 도구 테스트"""
    print("\n" + "="*80)
    print("노션 도구 테스트")
    print("="*80)
    
    # 식단 기록 조회
    print("\n1. 식단 기록 조회:")
    result = get_meal_history.run(days=3)
    print(result)
    
    # 선호도 조회
    print("\n2. 사용자 선호도 조회:")
    result = get_user_preferences.run()
    print(result)
    
    # 일정 조회
    print("\n3. 사용자 일정 조회:")
    result = get_user_schedule.run()
    print(result)
    
    # 예산 조회
    print("\n4. 예산 현황 조회:")
    result = get_budget_status.run()
    print(result)


def test_baemin_tools():
    """배민 도구 테스트"""
    print("\n" + "="*80)
    print("배민 도구 테스트")
    print("="*80)
    
    # 메뉴 검색
    print("\n1. 메뉴 검색 (한식, 1만원 이하):")
    result = search_menu.run(category="한식", max_price=10000)
    print(result)
    
    # 가격대별 필터
    print("\n2. 가격대별 메뉴 (5000~8000원):")
    result = filter_by_price.run(min_price=5000, max_price=8000)
    print(result)
    
    # 집밥 레시피
    print("\n3. 집밥 레시피 (쉬움, 30분 이하):")
    result = search_home_recipes.run(difficulty="쉬움", max_time=30)
    print(result)


if __name__ == "__main__":
    print("\n🔧 CrewAI 도구 테스트 시작\n")
    
    try:
        test_notion_tools()
        test_baemin_tools()
        
        print("\n" + "="*80)
        print("✅ 모든 도구 테스트 완료!")
        print("="*80)
        print("\n이제 'streamlit run app.py' 명령으로 챗봇을 실행하세요! 🚀\n")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print("\n문제 해결 방법:")
        print("1. requirements.txt의 모든 패키지가 설치되었는지 확인하세요")
        print("2. data/ 폴더에 mock_notion.json과 mock_baemin.json이 있는지 확인하세요")
