"""
레시피 생성 도구 - AI 기반
"""
import os
from crewai.tools import tool
from openai import OpenAI
from typing import Optional, Annotated
from pydantic import Field


@tool("AI 레시피 생성")
def generate_recipe_with_ai(
    dish_name: str,
    user_health_info: Annotated[str, Field(default="")] = ""
) -> str:
    """
    AI를 사용하여 요리 레시피를 생성합니다.
    사용자의 건강 정보를 고려하여 개인화된 레시피를 제공합니다.
    
    Args:
        dish_name: 만들고 싶은 요리 이름 (예: "된장찌개", "파스타", "김치볶음밥")
        user_health_info: 사용자 건강 정보 (선택, 예: "당뇨", "고혈압", "다이어트")
    
    Returns:
        상세한 레시피 (재료, 조리법, 팁 포함)
    
    Example:
        AI 레시피 생성(dish_name="된장찌개", user_health_info="당뇨·고혈압")
    """
    # None 체크
    if user_health_info is None:
        user_health_info = ""
    
    try:
        print(f"🔄 '{dish_name}' 레시피 생성 중 (건강 정보: {user_health_info or '없음'})...")
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # 건강 정보 반영
        health_consideration = ""
        if user_health_info:
            health_consideration = f"""

🏥 **중요: 사용자 건강 정보 반영**
사용자 건강 상태: {user_health_info}

건강 상태에 맞춰 레시피를 조정해주세요:
- 당뇨: 저당, 저GI 식품 사용, 설탕 대신 스테비아나 당류 제한
- 고혈압: 저염, 나트륨 제한, 간장/소금 최소화
- 다이어트: 저칼로리, 고단백, 저지방
- 채식: 고기 제외, 식물성 재료만 사용
- 알레르기: 해당 식재료 절대 사용 금지

레시피에 건강 고려사항을 명시해주세요."""

        prompt = f"""당신은 전문 요리 연구가입니다. '{dish_name}' 레시피를 작성해주세요.
{health_consideration}

다음 형식으로 작성해주세요:

## {dish_name}
[요리 설명을 2-3줄로]

## 난이도 및 시간
- 난이도: [쉬움/중간/어려움]
- 조리 시간: [분]
- 예상 칼로리: [kcal] (1인분 기준)

## 재료 (2인분 기준)
- [재료 1]: [양]
- [재료 2]: [양]
- [재료 3]: [양]
...

## 조리 순서
1. [1단계를 구체적으로]
2. [2단계를 구체적으로]
3. [3단계를 구체적으로]
...

## 요리 팁
- [팁 1]
- [팁 2]

## 영양 정보
- 칼로리: [kcal]
- 단백질: [g]
- 탄수화물: [g]
- 지방: [g]
"""

        # 건강 고려사항 추가 (f-string 밖에서 처리)
        if user_health_info:
            prompt += f"""
## 건강 고려사항
- {user_health_info}에 적합한 레시피입니다
- [구체적인 건강 이점]
"""
        
        prompt += "\n실용적이고 초보자도 따라할 수 있도록 구체적으로 작성해주세요."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "당신은 20년 경력의 요리 연구가입니다. 실용적이고 따라하기 쉬운 레시피를 제공합니다."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        recipe = response.choices[0].message.content
        
        print(f"✅ '{dish_name}' 레시피 생성 완료!")
        
        return f"🍳 AI 생성 레시피{f' ({user_health_info} 고려)' if user_health_info else ''}\n\n{recipe}"
        
    except Exception as e:
        return f"레시피 생성 중 오류가 발생했습니다: {str(e)}\n\n요청하신 '{dish_name}' 레시피를 생성할 수 없습니다."

