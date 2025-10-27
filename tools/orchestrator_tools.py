"""
오케스트레이터 전용 도구
"""
import os
from crewai.tools import tool
from typing import Optional, Annotated
from pydantic import Field
from openai import OpenAI
from agent_cards import get_agent_summary


@tool("사용자 의도 분석")
def analyze_user_intent(
    user_message: str,
    conversation_history: Annotated[str, Field(description="이전 대화 내역 (선택)", default="")] = ""
) -> str:
    """
    사용자의 메시지를 분석하여 어떤 에이전트들을 활용해야 하는지 판단합니다.
    대화 맥락을 고려하여 적절한 워크플로우를 제안합니다.
    
    Args:
        user_message: 사용자의 현재 메시지
        conversation_history: 이전 대화 내역 (옵션)
    
    Returns:
        필요한 에이전트 목록과 워크플로우 타입을 JSON 형식으로 반환
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        agent_info = get_agent_summary()
        
        prompt = f"""당신은 멀티 에이전트 시스템의 오케스트레이터입니다.
사용자의 요청을 분석하여 어떤 에이전트들을 활용해야 하는지 판단해야 합니다.

{agent_info}

=== 워크플로우 타입 ===
1. **FULL_RECOMMENDATION** - 전체 메뉴 추천 (집밥 위주)
   - 모든 에이전트 활용 (맛, 영양, 예산, 일정, 요리사)
   - 예: "오늘 저녁 메뉴 추천해줘", "점심 뭐 먹을까?"

2. **RESTAURANT_DELIVERY** - 외식/배달 추천
   - 예산, 일정, 영양사, 맛슐랭 활용 (식당_DB.json 사용)
   - 예: "오늘 외식하고 싶어", "배달 시켜먹을래", "레스토랑 추천해줘"
   - **중요**: 반드시 식당_DB.json에 있는 레스토랑만 추천

3. **RECIPE_ONLY** - 레시피/조리법만 필요
   - 요리사 에이전트만 활용
   - 예: "된장찌개 만드는 법 알려줘", "파스타 레시피 알려줘"

4. **BUDGET_CHECK** - 예산 확인
   - 예산 관리자만 활용
   - 예: "이번 달 식비 얼마 썼어?", "예산 남았어?"

5. **NUTRITION_INFO** - 영양/칼로리 정보
   - 영양사 에이전트만 활용
   - 예: "이 음식 칼로리 얼마야?", "오늘 먹은 음식 영양 분석"

6. **SCHEDULE_CHECK** - 일정 확인
   - 일정 관리자만 활용
   - 예: "오늘 일정 어때?", "언제 식사 가능해?"

7. **QUICK_MEAL** - 빠른 식사 (시간 중심)
   - 일정 관리자 + 메뉴 검색
   - 예: "30분 안에 먹을 수 있는 거", "빨리 먹을 수 있는 음식"

=== 사용자 메시지 ===
{user_message}

=== 대화 맥락 ===
{conversation_history if conversation_history else "없음 (첫 대화)"}

=== 분석 요청 ===
위 정보를 바탕으로 다음을 판단하세요:

1. 워크플로우 타입은? (위 7가지 중 하나)
2. 필요한 에이전트는? (taste_agent, nutrition_agent, budget_agent, scheduler_agent, chef_agent)
3. 우선순위가 높은 에이전트는?

**특별 주의사항:**
- '외식', '배달', '시켜먹', '레스토랑', '식당' 등의 키워드가 있으면 → RESTAURANT_DELIVERY
- '집밥', '요리', '만들어먹' 등의 키워드가 있으면 → FULL_RECOMMENDATION
- 명확하지 않으면 맥락과 사용자 선호도로 판단

**다음 JSON 형식으로만 답변하세요:**

{{
  "workflow_type": "워크플로우 타입",
  "required_agents": ["필요한 에이전트1", "필요한 에이전트2", ...],
  "primary_agent": "가장 중요한 에이전트",
  "reasoning": "판단 근거를 한 줄로",
  "user_intent": "사용자 의도 요약"
}}

JSON만 출력하고 다른 텍스트는 포함하지 마세요."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 사용자 의도를 정확히 파악하는 AI 오케스트레이터입니다. JSON 형식으로만 답변합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result = response.choices[0].message.content.strip()
        
        # JSON 형식이 아닌 경우를 대비한 파싱
        if result.startswith("```json"):
            result = result.replace("```json", "").replace("```", "").strip()
        elif result.startswith("```"):
            result = result.replace("```", "").strip()
        
        return result
        
    except Exception as e:
        # 에러 발생 시 기본값 반환
        return f'{{"workflow_type": "FULL_RECOMMENDATION", "required_agents": ["taste_agent", "nutrition_agent", "budget_agent", "scheduler_agent", "chef_agent"], "primary_agent": "taste_agent", "reasoning": "에러 발생으로 기본 워크플로우 사용: {str(e)}", "user_intent": "메뉴 추천"}}'


@tool("워크플로우 계획 수립")
def plan_workflow(
    intent_analysis: str
) -> str:
    """
    의도 분석 결과를 바탕으로 구체적인 태스크 순서를 계획합니다.
    
    Args:
        intent_analysis: 사용자 의도 분석 결과 (JSON)
    
    Returns:
        실행할 태스크 목록과 순서
    """
    try:
        import json
        analysis = json.loads(intent_analysis)
        
        workflow_type = analysis.get("workflow_type", "FULL_RECOMMENDATION")
        required_agents = analysis.get("required_agents", [])
        
        plan = f"=== 워크플로우 계획 ===\n"
        plan += f"타입: {workflow_type}\n"
        plan += f"필요 에이전트: {', '.join(required_agents)}\n\n"
        
        plan += "=== 실행 순서 ===\n"
        
        if workflow_type == "RECIPE_ONLY":
            plan += "1. 요리사 에이전트: 레시피 생성 및 조리법 제공\n"
        elif workflow_type == "BUDGET_CHECK":
            plan += "1. 예산 관리자: 예산 현황 조회\n"
        elif workflow_type == "NUTRITION_INFO":
            plan += "1. 영양사: 영양 정보 분석\n"
        elif workflow_type == "SCHEDULE_CHECK":
            plan += "1. 일정 관리자: 일정 조회\n"
        elif workflow_type == "QUICK_MEAL":
            plan += "1. 일정 관리자: 사용 가능한 시간 확인\n"
            plan += "2. 맛슐랭: 빠른 메뉴 검색 및 추천\n"
        elif workflow_type == "RESTAURANT_DELIVERY":
            plan += "🍽️ **외식/배달 전용 워크플로우**\n"
            plan += "1. 예산 관리자: 예산 현황 확인 후 가성비 좋은 레스토랑 검색\n"
            plan += "2. 일정 관리자: 가용 시간 확인 후 시간 내 가능한 식당 필터링\n"
            plan += "3. 영양사: 영양 요구사항 및 알레르기 고려하여 메뉴 검증\n"
            plan += "4. 맛슐랭: 식당 상세 정보 분석 후 최적의 레스토랑 추천\n"
            plan += "※ 식당_DB.json에 있는 실제 레스토랑만 추천합니다.\n"
        else:  # FULL_RECOMMENDATION
            plan += "1. 맛슐랭: 식단 기록 및 선호도 분석, 메뉴 후보 검색\n"
            plan += "2. 영양사: 영양 균형 평가 및 칼로리 검증\n"
            plan += "3. 예산 관리자: 예산 범위 내 메뉴 필터링\n"
            plan += "4. 일정 관리자: 시간 제약 고려하여 최종 메뉴 선정\n"
            plan += "5. 요리사 (옵션): 집밥 레시피 추가 제안\n"
        
        return plan
        
    except Exception as e:
        return f"워크플로우 계획 수립 실패: {str(e)}"

