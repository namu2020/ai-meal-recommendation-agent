"""
노션 MCP 서버 - 실제 Notion API 연동
"""
import json
import asyncio
import os
from pathlib import Path
from typing import Any, Sequence
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent
from notion_client import AsyncClient
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# MCP 서버 인스턴스
app = Server("notion-meal-server")

# Notion 클라이언트
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

if NOTION_API_KEY:
    notion = AsyncClient(auth=NOTION_API_KEY)
else:
    print("⚠️ NOTION_API_KEY가 설정되지 않았습니다.")
    notion = None


def extract_text_from_rich_text(rich_text_array):
    """rich_text 배열에서 텍스트 추출"""
    if not rich_text_array:
        return ""
    return "".join([item.get('plain_text', '') for item in rich_text_array])


async def fetch_table_rows(table_block_id):
    """테이블의 행 데이터 가져오기"""
    try:
        response = await notion.blocks.children.list(block_id=table_block_id)
        rows = []
        
        for block in response.get('results', []):
            if block.get('type') == 'table_row':
                row_data = block.get('table_row', {})
                cells = row_data.get('cells', [])
                row = [extract_text_from_rich_text(cell) for cell in cells]
                rows.append(row)
        
        return rows
    except Exception as e:
        print(f"⚠️ 테이블 행 가져오기 실패: {str(e)}")
        return []


async def parse_user_page(page_id):
    """사용자 페이지에서 데이터 파싱 - 완전 재작성"""
    # 페이지 블록들 가져오기
    response = await notion.blocks.children.list(block_id=page_id)
    blocks = response.get('results', [])
    
    # 데이터 구조 (기본값 제거 - 모두 Notion에서 가져옴)
    user_data = {
        "meal_history": [],
        "preferences": {
            "allergies": [],
            "dislikes": [],
            "diet_goal": "",
            "favorite_cuisines": [],
            "spicy_level": "보통",
            "cooking_skill": "",
            "health_conditions": [],  # 🔥 새로 추가: 당뇨, 고혈압 등
            "dietary_restrictions": {}  # 🔥 새로 추가: 탄수, 나트륨 제한
        },
        "schedule": {
            "today": "2025-10-25",
            "available_time": 30,
            "meal_time": "점심"
        },
        "budget": {
            "daily_limit": 20000,
            "today_spent": 0,
            "preferred_range": [8000, 15000]
        },
        "nutrition_goals": {}  # 🔥 새로 추가: 영양 목표
    }
    
    current_section = None
    
    for i, block in enumerate(blocks):
        block_type = block.get('type')
        
        # 섹션 헤더 파악 (heading_2와 heading_3 모두)
        if block_type == 'heading_2':
            heading = block.get('heading_2', {})
            section_title = extract_text_from_rich_text(heading.get('rich_text', []))
            current_section = section_title
        elif block_type == 'heading_3':
            heading = block.get('heading_3', {})
            section_title = extract_text_from_rich_text(heading.get('rich_text', []))
            current_section = section_title
        
        # 설명 텍스트에서 건강 정보 추출 (페이지 상단)
        elif block_type == 'bulleted_list_item' and i < 5:
            item = block.get('bulleted_list_item', {})
            text = extract_text_from_rich_text(item.get('rich_text', []))
            
            # "당뇨·고혈압" 같은 패턴 추출
            if '당뇨' in text:
                if '당뇨' not in user_data['preferences']['health_conditions']:
                    user_data['preferences']['health_conditions'].append('당뇨')
            if '고혈압' in text:
                if '고혈압' not in user_data['preferences']['health_conditions']:
                    user_data['preferences']['health_conditions'].append('고혈압')
            
            # "갑각류 알레르기" 같은 패턴 추출
            if '알레르기' in text or '알러지' in text:
                import re
                allergens = re.findall(r'(\w+)\s*알[레러]지', text)
                if allergens:
                    user_data['preferences']['allergies'].extend(allergens)
        
        # 테이블 처리 - 완전 재작성
        elif block_type == 'table':
            table_id = block.get('id')
            rows = await fetch_table_rows(table_id)
            
            if rows and current_section:
                import re
                
                # ============ Quick Profile ============
                if 'Quick Profile' in current_section or '프로필' in current_section:
                    for row in rows[1:]:  # 헤더 제외
                        if len(row) >= 2:
                            key = row[0].strip()
                            value = row[1].strip()
                            
                            # 건강상태: "제2형 당뇨, 고혈압"
                            if '건강상태' in key or '건강' in key:
                                conditions = [v.strip() for v in value.split(',')]
                                user_data['preferences']['health_conditions'].extend(conditions)
                            
                            # 일일 제한: "탄수 150g, 나트륨 < 2000mg"
                            elif '제한' in key or '한도' in key:
                                user_data['preferences']['dietary_restrictions']['raw'] = value
                                # 탄수 추출
                                carb_match = re.search(r'탄수[^0-9]*(\d+)', value)
                                if carb_match:
                                    user_data['preferences']['dietary_restrictions']['carb_limit'] = int(carb_match.group(1))
                                # 나트륨 추출
                                sodium_match = re.search(r'나트륨[^0-9]*(\d+)', value)
                                if sodium_match:
                                    user_data['preferences']['dietary_restrictions']['sodium_limit'] = int(sodium_match.group(1))
                            
                            # 선호: "국밥·찌개류(국물은 적게)"
                            elif '선호' in key:
                                if value:
                                    user_data['preferences']['favorite_cuisines'].append(value)
                
                # ============ 식단 기록(1주) ============
                elif '식단 기록' in current_section:
                    for row in rows[1:]:  # 헤더 제외
                        if len(row) >= 3:
                            try:
                                meal_entry = {
                                    "date": row[0].strip() if len(row) > 0 else "",
                                    "type": row[1].strip() if len(row) > 1 else "",
                                    "meal": row[2].strip() if len(row) > 2 else "",
                                    "calories": int(row[3].strip()) if len(row) > 3 and row[3].strip().isdigit() else 0,
                                    "cost": int(row[4].strip()) if len(row) > 4 and row[4].strip().isdigit() else 0
                                }
                                if meal_entry['meal']:
                                    user_data['meal_history'].append(meal_entry)
                            except:
                                pass
                
                # ============ 음식 선호 ============
                elif '음식 선호' in current_section:
                    for row in rows[1:]:  # 헤더 제외
                        if len(row) >= 2:
                            key = row[0].strip()
                            value = row[1].strip()
                            
                            if '좋아하는' in key:
                                cuisines = [v.strip() for v in value.split(',')]
                                user_data['preferences']['favorite_cuisines'].extend(cuisines)
                            elif '싫어하는' in key:
                                dislikes = [v.strip() for v in value.split(',')]
                                user_data['preferences']['dislikes'].extend(dislikes)
                            elif '알레르기' in key or '민감' in key:
                                # "알레르기 없음 / 나트륨·당 민감" 형태 파싱
                                if '없음' in value:
                                    user_data['preferences']['allergies'] = []
                                else:
                                    allergens = [v.strip() for v in value.split(',') if '없음' not in v]
                                    user_data['preferences']['allergies'].extend(allergens)
                                
                                # 민감 정보
                                if '나트륨' in value or '당' in value:
                                    user_data['preferences']['dietary_restrictions']['sensitive_to'] = value
                            elif '요리' in key and '실력' in key:
                                # "초급(전자레인지 중심, 전처리 도시락 선호)" 형태
                                if '초급' in value:
                                    user_data['preferences']['cooking_skill'] = '초급'
                                elif '중급' in value:
                                    user_data['preferences']['cooking_skill'] = '중급'
                                elif '고급' in value or '상급' in value:  # 🔥 '상급' 추가!
                                    user_data['preferences']['cooking_skill'] = '상급'
                                user_data['preferences']['cooking_notes'] = value  # 전체 정보 저장
                            elif '매운' in key:
                                user_data['preferences']['spicy_level'] = value
                
                # ============ 영양 목표 ============
                elif '영양 목표' in current_section:
                    for row in rows[1:]:  # 헤더 제외
                        if len(row) >= 2:
                            key = row[0].strip()
                            value = row[1].strip()
                            
                            try:
                                if value.isdigit():
                                    user_data['nutrition_goals'][key] = int(value)
                                else:
                                    user_data['nutrition_goals'][key] = value
                            except:
                                pass
                
                # ============ 예산 ============
                elif '예산' in current_section:
                    for row in rows[1:]:  # 헤더 제외
                        if len(row) >= 2:
                            key = row[0].strip()
                            value = row[1].strip()
                            
                            try:
                                numbers = re.findall(r'\d+', value.replace(',', ''))
                                if numbers:
                                    num_value = int(numbers[0])
                                    
                                    if '1식' in key or '끼' in key:
                                        user_data['budget']['daily_limit'] = num_value * 2  # 하루 2끼 가정
                                        user_data['budget']['preferred_range'] = [
                                            int(num_value * 0.7), 
                                            int(num_value * 1.3)
                                        ]
                                    elif '일일' in key or '하루' in key:
                                        user_data['budget']['daily_limit'] = num_value
                            except:
                                pass
                
                # ============ 스케줄 ============
                elif '스케줄' in current_section or 'schedule' in current_section.lower() or '밀프렙' in current_section:
                    for row in rows[1:]:  # 헤더 제외
                        if len(row) >= 2:
                            key = row[0].strip()
                            value = row[1].strip()
                            
                            try:
                                # "식사 슬롯" 행만 처리
                                if '식사' in key:
                                    user_data['schedule']['meal_time'] = key  # "식사 슬롯" 등
                                    
                                    # "11:30–13:30" 형태에서 시간 범위 추출
                                    if '–' in value or '-' in value:
                                        user_data['schedule']['meal_window'] = value
                                    
                                    # 🔥 메모에서 실제 식사 시간 추출 (우선순위 1)
                                    if len(row) >= 3:
                                        memo = row[2].strip()
                                        time_match = re.search(r'(\d+)\s*분', memo)
                                        if time_match:
                                            user_data['schedule']['available_time'] = int(time_match.group(1))
                                    
                                    # 🔥 메모가 없으면 시간 범위에서 계산 (우선순위 2)
                                    # "23:00–23:15" → 15분
                                    if user_data['schedule']['available_time'] == 30:  # 아직 기본값이면
                                        time_range_match = re.search(r'(\d{2}):(\d{2})[–-](\d{2}):(\d{2})', value)
                                        if time_range_match:
                                            start_h, start_m, end_h, end_m = map(int, time_range_match.groups())
                                            start_minutes = start_h * 60 + start_m
                                            end_minutes = end_h * 60 + end_m
                                            
                                            # 자정 넘어가는 경우 처리
                                            if end_minutes < start_minutes:
                                                end_minutes += 24 * 60
                                            
                                            duration = end_minutes - start_minutes
                                            if 0 < duration <= 120:  # 2시간 이내만
                                                user_data['schedule']['available_time'] = duration
                            except:
                                pass
    
    return user_data


async def query_notion_pages():
    """Notion 페이지들에서 데이터 조회"""
    if not notion or not NOTION_DATABASE_ID:
        # Fallback to mock data
        from pathlib import Path
        data_path = Path(__file__).parent.parent / "data" / "mock_notion.json"
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    try:
        # 환경 변수에서 현재 사용자 가져오기
        target_user = os.getenv("CURRENT_NOTION_USER", "소윤")
        
        # 디버깅: stderr로 현재 사용자 출력 (stdout은 JSON-RPC 전용)
        import sys
        print(f"[MCP Server] 🔍 Target User from ENV: {target_user}", file=sys.stderr)
        
        # 메인 페이지의 하위 페이지들 가져오기
        children = await notion.blocks.children.list(block_id=NOTION_DATABASE_ID)
        
        user_page_id = None
        
        for block in children.get('results', []):
            if block.get('type') == 'child_page':
                page_id = block.get('id')
                page = await notion.pages.retrieve(page_id=page_id)
                
                # 페이지 제목 추출
                title = ""
                if 'properties' in page:
                    for prop_name, prop_data in page['properties'].items():
                        if prop_data.get('type') == 'title':
                            if prop_data.get('title'):
                                title = prop_data['title'][0]['plain_text']
                                break
                
                # 사용자 이름 확인
                if target_user in title:
                    user_page_id = page_id
                    import sys
                    print(f"[MCP Server] ✅ Found {target_user}'s page: {page_id}", file=sys.stderr)
                    break
        
        # 사용자 페이지 파싱
        if user_page_id:
            user_data = await parse_user_page(user_page_id)
            import sys
            # 알레르기 정보 확인 로그
            allergies = user_data.get('preferences', {}).get('allergies', [])
            print(f"[MCP Server] 📊 Parsed {target_user}'s data - Allergies: {allergies}", file=sys.stderr)
            return user_data
        else:
            # Fallback to mock data
            from pathlib import Path
            data_path = Path(__file__).parent.parent / "data" / "mock_notion.json"
            with open(data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
    except Exception as e:
        # Fallback to mock data
        from pathlib import Path
        data_path = Path(__file__).parent.parent / "data" / "mock_notion.json"
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)


def load_notion_data():
    """동기 wrapper"""
    return asyncio.run(query_notion_pages())


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
    data = await query_notion_pages()
    
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
    data = await query_notion_pages()
    
    if name == "get_meal_history":
        days = arguments.get("days", 7)
        
        # 날짜 기반으로 필터링 (7일 = 모든 끼니)
        from datetime import datetime, timedelta
        
        if days > 0 and data["meal_history"]:
            # 가장 최근 날짜 찾기
            try:
                latest_date_str = data["meal_history"][0]["date"]
                latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d")
                cutoff_date = latest_date - timedelta(days=days-1)
                
                # 날짜 범위 내의 모든 식사 필터링
                history = [
                    meal for meal in data["meal_history"]
                    if datetime.strptime(meal["date"], "%Y-%m-%d") >= cutoff_date
                ]
            except:
                # 날짜 파싱 실패 시 기존 방식 사용
                history = data["meal_history"][:days]
        else:
            history = data["meal_history"][:days]
        
        result = {
            "recent_meals": history,
            "average_calories": sum(m["calories"] for m in history) / len(history) if history else 0,
            "total_cost": sum(m["cost"] for m in history),
            "days_covered": days
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
    # MCP는 JSON-RPC만 stdout에 출력해야 하므로 print 사용 금지
    # 디버깅이 필요하면 stderr 사용: import sys; print("...", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

