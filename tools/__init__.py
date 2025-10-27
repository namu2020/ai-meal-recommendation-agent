"""
CrewAI 도구 모듈
환경 변수에 따라 Mock 또는 MCP 버전 선택
"""
import os
import sys
from pathlib import Path

# config import
sys.path.append(str(Path(__file__).parent.parent))
from config import USE_NOTION_MCP

# Notion tools - Mock 또는 MCP 선택
if USE_NOTION_MCP:
    print("🔗 Notion MCP 모드 활성화")
    from .notion_tools_mcp import (
        get_meal_history,
        get_user_preferences,
        get_user_schedule,
        get_budget_status
    )
else:
    print("📦 Mock 데이터 모드 활성화")
    from .notion_tools import (
        get_meal_history,
        get_user_preferences,
        get_user_schedule,
        get_budget_status
    )

# Recipe generation tools
from .recipe_tools import (
    generate_recipe_with_ai
)

# Orchestrator tools
from .orchestrator_tools import (
    analyze_user_intent,
    plan_workflow
)

# Restaurant tools
from .restaurant_tools import (
    search_restaurants,
    get_restaurant_details,
    recommend_best_value_restaurants
)

# LLM Judge tools
from .llm_judge_tools import (
    judge_menu_personalization,
    judge_restaurant_recommendations
)

__all__ = [
    'get_meal_history',
    'get_user_preferences',
    'get_user_schedule',
    'get_budget_status',
    'generate_recipe_with_ai',
    'analyze_user_intent',
    'plan_workflow',
    'search_restaurants',
    'get_restaurant_details',
    'recommend_best_value_restaurants',
    'judge_menu_personalization',
    'judge_restaurant_recommendations',
]
