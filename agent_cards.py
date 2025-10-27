"""
에이전트 카드 시스템
각 에이전트의 역할과 사용 시나리오를 정의
"""

AGENT_CARDS = {
    "taste_agent": {
        "name": "맛슐랭 (맛 평가 전문가)",
        "role": "맛과 식사 경험 평가",
        "capabilities": [
            "식단 기록 조회 및 분석",
            "사용자 선호도 파악",
            "맛 기반 메뉴 추천",
            "음식 조합 평가"
        ],
        "use_cases": [
            "전체 메뉴 추천이 필요할 때",
            "사용자 선호도 기반 추천이 필요할 때",
            "과거 식단 분석이 필요할 때"
        ],
        "keywords": ["메뉴 추천", "맛", "선호도", "식단 기록", "음식 조합"]
    },
    "nutrition_agent": {
        "name": "영양사",
        "role": "영양 균형 및 칼로리 관리",
        "capabilities": [
            "식단 기록 분석",
            "칼로리 계산",
            "영양 균형 평가",
            "건강 기반 메뉴 필터링"
        ],
        "use_cases": [
            "전체 메뉴 추천이 필요할 때",
            "칼로리나 영양 정보가 필요할 때",
            "다이어트나 건강 식단이 필요할 때"
        ],
        "keywords": ["칼로리", "영양", "건강", "다이어트", "영양 균형"]
    },
    "budget_agent": {
        "name": "예산 관리자 (총무)",
        "role": "예산 관리 및 비용 최적화",
        "capabilities": [
            "예산 현황 조회",
            "가격 기반 메뉴 필터링",
            "비용 효율 분석",
            "예산 초과 경고"
        ],
        "use_cases": [
            "전체 메뉴 추천이 필요할 때",
            "예산이나 가격 정보가 필요할 때",
            "저렴한 메뉴를 찾을 때"
        ],
        "keywords": ["예산", "가격", "비용", "저렴한", "경제적"]
    },
    "scheduler_agent": {
        "name": "일정 관리자",
        "role": "시간 관리 및 일정 조율",
        "capabilities": [
            "사용자 일정 조회",
            "조리 시간 기반 필터링",
            "배달 시간 고려",
            "시간 최적화"
        ],
        "use_cases": [
            "전체 메뉴 추천이 필요할 때",
            "시간이 제한적일 때",
            "빠른 식사가 필요할 때"
        ],
        "keywords": ["일정", "시간", "빠른", "조리 시간", "배달"]
    },
    "chef_agent": {
        "name": "집밥 레시피 전문가",
        "role": "집밥 레시피 추천 및 생성",
        "capabilities": [
            "레시피 데이터베이스 검색",
            "AI 기반 맞춤 레시피 생성",
            "조리법 상세 설명",
            "요리 난이도 평가",
            "재료 및 조리 팁 제공"
        ],
        "use_cases": [
            "집에서 요리하고 싶을 때",
            "레시피나 조리법이 필요할 때",
            "특정 요리 만드는 방법을 물을 때",
            "요리 팁이나 재료 정보가 필요할 때"
        ],
        "keywords": [
            "레시피", "조리법", "요리 방법", "만들기", "집밥",
            "재료", "조리", "요리", "만드는 법", "어떻게 만들",
            "요리 팁", "조리 순서", "레시피 추천"
        ]
    }
}


def get_agent_card(agent_type: str) -> dict:
    """특정 에이전트의 카드 정보를 반환"""
    return AGENT_CARDS.get(agent_type, {})


def get_all_agent_cards() -> dict:
    """모든 에이전트 카드 반환"""
    return AGENT_CARDS


def get_agent_summary() -> str:
    """에이전트 카드를 요약한 문자열 반환 (오케스트레이터용)"""
    summary = "=== 사용 가능한 에이전트들 ===\n\n"
    
    for agent_type, card in AGENT_CARDS.items():
        summary += f"**{card['name']}** ({agent_type})\n"
        summary += f"역할: {card['role']}\n"
        summary += f"주요 기능: {', '.join(card['capabilities'][:3])}\n"
        summary += f"사용 시나리오: {', '.join(card['use_cases'][:2])}\n"
        summary += f"키워드: {', '.join(card['keywords'][:5])}\n"
        summary += "\n"
    
    return summary

