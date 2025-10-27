"""
노션 MCP 서버 - 사용자 식단 기록 및 선호도 제공
Mock 데이터 기반으로 MCP 프로토콜 구현 (사용자별 데이터 지원)
"""
import json
import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# MCP 서버 인스턴스
app = Server("notion-meal-server")

# 데이터 경로
DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_DATA_PATH = DATA_DIR / "mock_notion.json"


def load_notion_data():
    """현재 사용자의 Notion Mock 데이터 로드"""
    # 환경 변수에서 현재 사용자 가져오기
    current_user = os.getenv("CURRENT_NOTION_USER", "소윤")
    
    # 디버깅: stderr로 현재 사용자 출력
    print(f"[Mock Server] 🔍 Current User from ENV: {current_user}", file=sys.stderr)
    
    # 사용자별 파일 경로
    user_file = DATA_DIR / f"parsed_notion_{current_user}.json"
    
    # 사용자별 파일이 존재하면 로드
    if user_file.exists():
        print(f"[Mock Server] ✅ Loading user data: {user_file.name}", file=sys.stderr)
        with open(user_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # fallback to default
        print(f"[Mock Server] ⚠️ User file not found, using default: {DEFAULT_DATA_PATH.name}", file=sys.stderr)
        with open(DEFAULT_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)


@app.list_resources()
async def list_resources() -> list[Resource]:
    """사용 가능한 리소스 목록"""
    return [
        Resource(
            uri="notion://meal/history",
            name="식단 기록",
            description="사용자의 최근 식단 기록",
            mimeType="application/json"
        ),
        Resource(
            uri="notion://user/preferences",
            name="사용자 선호도",
            description="알레르기, 선호 음식, 다이어트 목표 등",
            mimeType="application/json"
        ),
        Resource(
            uri="notion://user/schedule",
            name="사용자 일정",
            description="오늘 일정 및 가용 시간",
            mimeType="application/json"
        ),
        Resource(
            uri="notion://user/budget",
            name="예산 정보",
            description="일일 예산 및 지출 현황",
            mimeType="application/json"
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    """특정 리소스 데이터 반환"""
    data = load_notion_data()
    
    if uri == "notion://meal/history":
        return json.dumps(data["meal_history"], ensure_ascii=False, indent=2)
    
    elif uri == "notion://user/preferences":
        return json.dumps(data["preferences"], ensure_ascii=False, indent=2)
    
    elif uri == "notion://user/schedule":
        return json.dumps(data["schedule"], ensure_ascii=False, indent=2)
    
    elif uri == "notion://user/budget":
        return json.dumps(data["budget"], ensure_ascii=False, indent=2)
    
    else:
        raise ValueError(f"Unknown resource: {uri}")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """사용 가능한 도구 목록"""
    return [
        Tool(
            name="get_meal_history",
            description="사용자의 최근 식단 기록 조회",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "조회할 일수 (기본: 7일)",
                        "default": 7
                    }
                }
            }
        ),
        Tool(
            name="get_user_preferences",
            description="사용자의 알레르기, 선호도, 다이어트 목표 조회",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="check_allergen",
            description="특정 음식이 사용자의 알레르기 항목에 해당하는지 확인",
            inputSchema={
                "type": "object",
                "properties": {
                    "food_allergens": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "확인할 알레르기 항목 목록"
                    }
                },
                "required": ["food_allergens"]
            }
        ),
        Tool(
            name="get_available_time",
            description="오늘 사용자가 식사 준비에 사용할 수 있는 시간 조회",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_budget_status",
            description="오늘 예산 사용 현황 및 남은 예산 조회",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
    """도구 실행"""
    data = load_notion_data()
    
    if name == "get_meal_history":
        days = arguments.get("days", 7)
        history = data["meal_history"][:days]
        result = {
            "recent_meals": history,
            "average_calories": sum(m["calories"] for m in history) / len(history) if history else 0,
            "total_cost": sum(m["cost"] for m in history)
        }
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]
    
    elif name == "get_user_preferences":
        return [TextContent(
            type="text",
            text=json.dumps(data["preferences"], ensure_ascii=False, indent=2)
        )]
    
    elif name == "check_allergen":
        food_allergens = arguments.get("food_allergens", [])
        user_allergens = data["preferences"]["allergies"]
        
        conflicts = [allergen for allergen in food_allergens if allergen in user_allergens]
        
        result = {
            "safe": len(conflicts) == 0,
            "conflicts": conflicts,
            "message": "안전합니다" if not conflicts else f"알레르기 주의: {', '.join(conflicts)}"
        }
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]
    
    elif name == "get_available_time":
        schedule = data["schedule"]
        return [TextContent(
            type="text",
            text=json.dumps(schedule, ensure_ascii=False, indent=2)
        )]
    
    elif name == "get_budget_status":
        budget = data["budget"]
        remaining = budget["daily_limit"] - budget["today_spent"]
        result = {
            **budget,
            "remaining": remaining,
            "status": "초과" if remaining < 0 else "여유있음" if remaining > 5000 else "빠듯함"
        }
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def main():
    """MCP 서버 시작"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

