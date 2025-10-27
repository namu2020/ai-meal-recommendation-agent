"""
영양사 에이전트 수정 사항 검증 스크립트
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def verify_agent_configuration():
    """에이전트 설정 검증"""
    print("="*80)
    print("🔍 영양사 에이전트 설정 검증")
    print("="*80)
    print()
    
    from config import get_llm
    from agents.nutrition_agent import create_nutrition_agent
    from crew import FoodRecommendationCrew
    
    llm = get_llm()
    
    # 1. 영양사 에이전트 생성
    print("1️⃣ 영양사 에이전트 생성...")
    nutrition_agent = create_nutrition_agent(llm)
    print(f"   ✅ 역할: {nutrition_agent.role}")
    print(f"   ✅ 도구 개수: {len(nutrition_agent.tools)}")
    print(f"   ✅ 도구 목록:")
    for tool in nutrition_agent.tools:
        print(f"      - {tool.name}")
    print()
    
    # 2. Goal 확인
    print("2️⃣ Goal (목표) 확인...")
    goal_lines = nutrition_agent.goal.split('\n')
    print(f"   ✅ Goal 라인 수: {len(goal_lines)}")
    print(f"   ✅ '3단계' 포함 여부: {'3단계' in nutrition_agent.goal}")
    print(f"   ✅ '도구 2개만' 포함 여부: {'도구 2개만' in nutrition_agent.goal}")
    print()
    
    # 3. Backstory 확인
    print("3️⃣ Backstory (배경) 확인...")
    backstory_lines = nutrition_agent.backstory.split('\n')
    print(f"   ✅ Backstory 라인 수: {len(backstory_lines)}")
    print(f"   ✅ '작업 효율성' 포함 여부: {'작업 효율성' in nutrition_agent.backstory}")
    print(f"   ✅ '재시도 금지' 포함 여부: {'재시도' in nutrition_agent.backstory}")
    print()
    
    # 4. Crew 설정 확인
    print("4️⃣ Crew 설정 확인...")
    crew = FoodRecommendationCrew()
    print(f"   ✅ 영양사 max_iter: {crew.nutrition_agent.max_iter}")
    print(f"   ✅ 예산 관리자 max_iter: {crew.budget_agent.max_iter}")
    print(f"   ✅ 일정 관리자 max_iter: {crew.scheduler_agent.max_iter}")
    print()
    
    # 5. 사용자 데이터 확인
    print("5️⃣ 지민 페르소나 데이터 확인...")
    import json
    with open('data/current_user.json', 'r', encoding='utf-8') as f:
        current_user = json.load(f)
    print(f"   ✅ 현재 사용자: {current_user['current_user']}")
    
    with open('data/parsed_notion.json', 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    
    dietary = user_data.get('preferences', {}).get('dietary_restrictions', {})
    if dietary:
        print(f"   ✅ 식이 제한:")
        for day, restriction in dietary.items():
            print(f"      - {day}: {restriction}")
    
    print(f"   ✅ 예산: {user_data.get('budget', {}).get('daily_limit', 0):,}원")
    print(f"   ✅ 가용 시간: {user_data.get('schedule', {}).get('available_time', 0)}분")
    print()
    
    print("="*80)
    print("✅ 모든 검증 완료!")
    print("="*80)
    print()
    
    # 요약
    print("📊 검증 요약:")
    print(f"   - 영양사 도구 개수: {len(nutrition_agent.tools)} (목표: 3개)")
    print(f"   - max_iter: {crew.nutrition_agent.max_iter} (목표: 8회)")
    print(f"   - Goal 간결성: {'✅ 간결함' if len(goal_lines) < 20 else '⚠️ 여전히 김'}")
    print(f"   - 현재 사용자: {current_user['current_user']}")
    print()
    
    # LLM Judge 도구 제거 확인
    judge_tool_exists = any('judge' in tool.name.lower() for tool in nutrition_agent.tools)
    print(f"   - LLM Judge 도구 제거: {'❌ 아직 있음' if judge_tool_exists else '✅ 제거됨'}")
    print()

if __name__ == "__main__":
    try:
        verify_agent_configuration()
    except Exception as e:
        print(f"❌ 검증 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

