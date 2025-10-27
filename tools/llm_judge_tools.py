"""
LLM as Judge - 개인화 적합성 판단 도구
각 에이전트가 추천한 메뉴가 사용자 페르소나에 적합한지 LLM이 판단
"""
from crewai.tools import tool
from typing import List, Dict, Any, Optional, Annotated, Union
from pydantic import Field
import json


@tool("메뉴 개인화 적합성 판단")
def judge_menu_personalization(
    menu_recommendations: Annotated[Union[str, dict], Field(default="")] = "",
    user_persona_info: Annotated[Union[str, dict], Field(default="")] = ""
) -> str:
    """
    추천된 메뉴가 사용자 페르소나에 적합한지 LLM이 판단합니다.
    
    Args:
        menu_recommendations: 추천 메뉴 목록 (str 또는 dict)
        user_persona_info: 사용자 페르소나 정보 (str 또는 dict)
    
    Returns:
        판단 결과 (적합/부적합 + 이유)
    
    Example:
        메뉴 개인화 적합성 판단(
            menu_recommendations="원조장충왕족발 - 족발",
            user_persona_info="채식주의자 (락토오보)"
        )
        → 결과: "❌ 부적합 - 채식주의자에게 족발(돼지고기) 추천 불가"
    """
    
    # dict를 JSON string으로 변환
    if isinstance(menu_recommendations, dict):
        menu_recommendations = json.dumps(menu_recommendations, ensure_ascii=False, indent=2)
    if isinstance(user_persona_info, dict):
        user_persona_info = json.dumps(user_persona_info, ensure_ascii=False, indent=2)
    
    # None 체크
    if menu_recommendations is None:
        menu_recommendations = ""
    if user_persona_info is None:
        user_persona_info = ""
    
    if not menu_recommendations or not user_persona_info:
        return "❌ 메뉴 추천 정보와 사용자 페르소나 정보가 모두 필요합니다."
    
    # Few-shot 예시
    few_shot_examples = """
=== Few-Shot 예시 ===

**예시 1: 채식주의자에게 고기 추천 (부적합)**
입력:
- 추천 메뉴: "원조장충왕족발 - 족발 세트"
- 페르소나: "채식주의자 (락토오보), 평일에는 고기를 먹지 않음"

판단:
❌ **부적합**
이유: 족발은 돼지고기로 만든 음식으로, 채식주의자(락토오보)에게 절대 추천 불가합니다.
대안: 두부, 샐러드, 채소 요리, 해물 요리 등을 추천해야 합니다.

---

**예시 2: 당뇨 환자에게 고당분 음식 (부적합)**
입력:
- 추천 메뉴: "매드독스시카고피자 - 슈퍼콤보 피자"
- 페르소나: "당뇨·고혈압, 저염·저당식 필요"

판단:
❌ **부적합**
이유: 피자는 고염·고당·고칼로리 음식으로 당뇨·고혈압 환자에게 위험합니다.
대안: 찜 요리, 구이, 샐러드, 생선 요리 등 건강식을 추천해야 합니다.

---

**예시 3: 채식주의자에게 해물 (적합)**
입력:
- 추천 메뉴: "시골식당 - 해물칼국수"
- 페르소나: "페스코 채식주의자 (생선·해물은 섭취)"

판단:
✅ **적합**
이유: 페스코 채식주의자는 생선과 해물을 섭취할 수 있으므로 해물칼국수는 적합합니다.

---

**예시 4: 알레르기 체크 (부적합)**
입력:
- 추천 메뉴: "해물탕 (새우, 게 포함)"
- 페르소나: "알레르기: 갑각류(새우, 게)"

판단:
❌ **부적합**
이유: 새우와 게가 포함된 해물탕은 갑각류 알레르기가 있는 사용자에게 위험합니다.
대안: 갑각류가 없는 생선 요리, 두부 요리 등을 추천해야 합니다.

---

**예시 5: 다이어터에게 저칼로리 음식 (적합)**
입력:
- 추천 메뉴: "썬한식 - 손두부"
- 페르소나: "다이어트 목표, 저칼로리 식단 선호"

판단:
✅ **적합**
이유: 두부는 저칼로리 고단백 식품으로 다이어터에게 이상적입니다.

---
"""
    
    # 판단 프롬프트
    judgment_prompt = f"""
{few_shot_examples}

=== 판단 요청 ===

**추천 메뉴:**
{menu_recommendations}

**사용자 페르소나:**
{user_persona_info}

**판단 기준:**
1. **식이 제한 체크**
   - 채식주의자: 고기(돼지, 소, 닭, 양 등) 절대 금지
   - 페스코: 생선·해물은 가능, 고기는 금지
   - 락토오보: 유제품·계란은 가능, 고기·생선은 금지

2. **알레르기 체크**
   - 알레르기 식재료가 포함된 메뉴는 절대 금지
   - 예: 갑각류 알레르기 → 새우, 게 금지

3. **건강 상태 체크**
   - 당뇨: 고당분 음식 금지 (피자, 짜장면, 탕수육 등)
   - 고혈압: 고염분 음식 금지 (짬뽕, 라면 등)
   - 다이어트: 고칼로리 음식 주의 (튀김, 족발 등)

4. **선호도 체크**
   - 싫어하는 음식은 추천하지 않음
   - 선호 음식은 우대

**판단 결과를 다음 형식으로 작성:**

✅ **적합** 또는 ❌ **부적합**

**이유:** [구체적인 이유 설명]

**대안 (부적합인 경우):** [추천할 만한 대안 메뉴]

---

판단을 시작하세요:
"""
    
    # 판단 프롬프트를 반환 (LLM이 크루 내에서 처리)
    return judgment_prompt


@tool("레스토랑 추천 종합 판단")
def judge_restaurant_recommendations(
    all_agent_recommendations: Annotated[Union[str, dict], Field(default="")] = "",
    user_persona_info: Annotated[Union[str, dict], Field(default="")] = ""
) -> str:
    """
    모든 에이전트의 추천을 종합하여 최종 적합성을 판단합니다.
    
    Args:
        all_agent_recommendations: 모든 에이전트의 추천 결과 (str 또는 dict)
        user_persona_info: 사용자 페르소나 정보 (str 또는 dict)
    
    Returns:
        종합 판단 결과 및 최종 추천
    
    Example:
        레스토랑 추천 종합 판단(
            all_agent_recommendations="예산: 족발집, 일정: 피자집, 영양: 샐러드집",
            user_persona_info="채식주의자"
        )
    """
    
    # dict를 JSON string으로 변환
    if isinstance(all_agent_recommendations, dict):
        all_agent_recommendations = json.dumps(all_agent_recommendations, ensure_ascii=False, indent=2)
    if isinstance(user_persona_info, dict):
        user_persona_info = json.dumps(user_persona_info, ensure_ascii=False, indent=2)
    
    # None 체크
    if all_agent_recommendations is None:
        all_agent_recommendations = ""
    if user_persona_info is None:
        user_persona_info = ""
    
    if not all_agent_recommendations or not user_persona_info:
        return "❌ 에이전트 추천 정보와 사용자 페르소나 정보가 모두 필요합니다."
    
    judgment_prompt = f"""
=== 종합 판단 요청 ===

당신은 최종 의사결정자로서, 여러 에이전트의 추천을 종합하여 사용자에게 가장 적합한 레스토랑을 선정해야 합니다.

**모든 에이전트의 추천:**
{all_agent_recommendations}

**사용자 페르소나:**
{user_persona_info}

**판단 기준:**
1. **개인화 필터링 (최우선)**
   - 채식주의자에게 고기집 추천 → 즉시 제외
   - 알레르기 식재료 포함 → 즉시 제외
   - 당뇨·고혈압에 위험한 음식 → 즉시 제외

2. **우선순위**
   - 영양사 의견 > 예산 > 일정 > 맛
   - 건강이 최우선

3. **교집합 우선**
   - 여러 에이전트가 공통으로 추천한 레스토랑 우대

4. **최종 출력**
   - 2-3개 레스토랑만 선정
   - 각 레스토랑에 대해:
     * 레스토랑명
     * 추천 메뉴
     * 가격
     * 소요시간
     * 선정 이유
     * 개인화 적합성 설명

---

최종 판단을 시작하세요:
"""
    
    return judgment_prompt

