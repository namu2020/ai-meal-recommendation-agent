"""
레스토랑 추천 시스템 테스트
식당_DB.json 활용 검증
"""
from tools.restaurant_tools import (
    search_restaurants,
    get_restaurant_details,
    recommend_best_value_restaurants,
    search_by_menu
)


def test_basic_search():
    """기본 레스토랑 검색 테스트"""
    print("\n" + "="*80)
    print("테스트 1: 기본 레스토랑 검색")
    print("="*80)
    
    result = search_restaurants(
        max_budget=10000,
        max_time_minutes=30,
        meal_type="배달",
        keyword=""
    )
    print(result)


def test_budget_optimization():
    """예산 최적화 레스토랑 추천 테스트"""
    print("\n" + "="*80)
    print("테스트 2: 예산 최적화 레스토랑 추천")
    print("="*80)
    
    result = recommend_best_value_restaurants(
        max_budget=15000,
        max_time_minutes=40,
        meal_type="배달"
    )
    print(result)


def test_menu_search():
    """메뉴 기반 레스토랑 검색 테스트"""
    print("\n" + "="*80)
    print("테스트 3: 메뉴 기반 레스토랑 검색 (칼국수)")
    print("="*80)
    
    result = search_by_menu(
        menu_keywords="칼국수",
        max_budget=10000,
        max_time_minutes=30
    )
    print(result)


def test_restaurant_details():
    """레스토랑 상세 정보 조회 테스트"""
    print("\n" + "="*80)
    print("테스트 4: 레스토랑 상세 정보 조회")
    print("="*80)
    
    result = get_restaurant_details(restaurant_name="시골식당")
    print(result)


def test_tight_budget():
    """빡빡한 예산 테스트"""
    print("\n" + "="*80)
    print("테스트 5: 빡빡한 예산 (5,000원 이하)")
    print("="*80)
    
    result = search_restaurants(
        max_budget=5000,
        max_time_minutes=60,
        meal_type="배달",
        keyword=""
    )
    print(result)


def test_tight_time():
    """촉박한 시간 테스트"""
    print("\n" + "="*80)
    print("테스트 6: 촉박한 시간 (20분 이내)")
    print("="*80)
    
    result = search_restaurants(
        max_budget=20000,
        max_time_minutes=20,
        meal_type="배달",
        keyword=""
    )
    print(result)


def test_keyword_search():
    """키워드 검색 테스트"""
    print("\n" + "="*80)
    print("테스트 7: 키워드 검색 (라멘)")
    print("="*80)
    
    result = search_restaurants(
        max_budget=10000,
        max_time_minutes=40,
        meal_type="배달",
        keyword="라멘"
    )
    print(result)


def test_dine_in_search():
    """매장 식사 검색 테스트"""
    print("\n" + "="*80)
    print("테스트 8: 매장 식사 레스토랑 검색")
    print("="*80)
    
    result = search_restaurants(
        max_budget=30000,
        max_time_minutes=90,
        meal_type="매장",
        keyword=""
    )
    print(result)


if __name__ == "__main__":
    print("\n🍽️ 레스토랑 추천 시스템 테스트 시작\n")
    
    try:
        # 기본 테스트
        test_basic_search()
        
        # 예산 최적화 테스트
        test_budget_optimization()
        
        # 메뉴 기반 검색 테스트
        test_menu_search()
        
        # 상세 정보 조회 테스트
        test_restaurant_details()
        
        # 엣지 케이스 테스트
        test_tight_budget()
        test_tight_time()
        
        # 키워드 검색 테스트
        test_keyword_search()
        
        # 매장 식사 테스트
        test_dine_in_search()
        
        print("\n" + "="*80)
        print("✅ 모든 테스트 완료!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

