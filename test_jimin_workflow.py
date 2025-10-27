"""
지민 페르소나로 '오늘 저녁 메뉴 추천해줘' 테스트
영양사 에이전트의 tool calling 문제 및 무한 루프 문제 진단
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

# 사용자를 "지민"으로 설정
from user_manager import save_current_user
save_current_user("지민")
print("✅ 사용자를 '지민'으로 설정했습니다.\n")

# 크루 실행
from crew import FoodRecommendationCrew

def main():
    print("="*80)
    print("🔍 지민 페르소나 테스트 시작")
    print("   - 프롬프트: '오늘 저녁 메뉴 추천해줘'")
    print("   - 주요 체크 사항:")
    print("     1. 영양사 에이전트의 tool calling 패턴")
    print("     2. 무한 루프 발생 여부")
    print("     3. 6개 에이전트 상호작용")
    print("="*80)
    print()
    
    # 크루 생성
    crew = FoodRecommendationCrew()
    
    # 실행
    try:
        result = crew.run("오늘 저녁 메뉴로 집밥 1개 외식 메뉴 1개 추천해줘")
        
        print("\n" + "="*80)
        print("✅ 테스트 완료!")
        print("="*80)
        print("\n최종 결과:")
        print(result)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 중단됨 (Ctrl+C)")
        print("무한 루프 문제가 발생한 것으로 보입니다.")
    except Exception as e:
        print(f"\n\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

