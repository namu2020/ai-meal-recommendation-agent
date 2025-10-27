"""
레스토랑 추천 도구 - 식당_DB.json 활용
"""
import json
import os
from pathlib import Path
from crewai.tools import tool
from typing import List, Dict, Any, Optional, Annotated
from pydantic import Field

# DB 경로
DB_PATH = Path(__file__).parent.parent / "식당_DB.json"

# 레스토랑 DB 캐시
_restaurant_db = None


def _load_restaurant_db() -> List[Dict[str, Any]]:
    """레스토랑 DB 로드 (캐싱)"""
    global _restaurant_db
    
    if _restaurant_db is None:
        try:
            with open(DB_PATH, 'r', encoding='utf-8') as f:
                _restaurant_db = json.load(f)
            print(f"✅ 레스토랑 DB 로드 완료: {len(_restaurant_db)}개 식당")
        except Exception as e:
            print(f"❌ 레스토랑 DB 로드 실패: {e}")
            _restaurant_db = []
    
    return _restaurant_db


def _parse_price(price) -> int:
    """가격을 정수로 파싱"""
    if price is None:
        return 999999  # null 가격은 매우 높게 설정
    if isinstance(price, int):
        return price
    return 999999


def _parse_time(time_str: str) -> int:
    """시간 문자열을 분으로 파싱 (예: "25분" -> 25, "1시간 5분" -> 65)"""
    if not time_str:
        return 999
    
    try:
        # "1시간 5분" 형태 처리
        if "시간" in time_str:
            parts = time_str.replace("분", "").split("시간")
            hours = int(parts[0].strip())
            minutes = int(parts[1].strip()) if len(parts) > 1 and parts[1].strip() else 0
            return hours * 60 + minutes
        # "25분" 형태 처리
        elif "분" in time_str:
            return int(time_str.replace("분", "").strip())
        else:
            return 999
    except:
        return 999


@tool("메뉴 검색")
def search_restaurants(
    max_budget: Annotated[int, Field(default=100000)] = 100000,
    max_time_minutes: Annotated[int, Field(default=120)] = 120,
    meal_type: Annotated[str, Field(default="배달")] = "배달",
    keyword: Annotated[str, Field(default="")] = ""
) -> str:
    """
    예산과 시간 제약을 고려하여 메뉴/레스토랑을 검색합니다.
    
    Args:
        max_budget: 최대 예산 (원). 기본값 100000
        max_time_minutes: 최대 가용 시간 (분). 기본값 120
        meal_type: "배달" 또는 "매장". 기본값 "배달"
        keyword: 검색 키워드 (선택). 빈 문자열 또는 생략 가능. 예: "파스타", "한식", "채식"
    
    Returns:
        조건에 맞는 레스토랑 목록 (최대 10개)
    
    사용 예시:
        메뉴 검색(max_budget=15000, max_time_minutes=30)
        메뉴 검색(max_budget=15000, max_time_minutes=30, keyword="한식")
        메뉴 검색(max_budget=10000) # 시간은 기본값 사용
    
    주의: keyword는 선택 사항입니다. 없으면 빈 문자열("")로 전달하세요.
    """
    restaurants = _load_restaurant_db()
    
    # 기본값 처리 및 타입 변환 (None 안전 처리)
    try:
        max_budget = int(max_budget) if max_budget is not None and max_budget > 0 else 100000
    except (ValueError, TypeError):
        max_budget = 100000
    
    try:
        max_time_minutes = int(max_time_minutes) if max_time_minutes is not None and max_time_minutes > 0 else 120
    except (ValueError, TypeError):
        max_time_minutes = 120
    
    if not meal_type or not isinstance(meal_type, str):
        meal_type = "배달"
    
    if keyword is None or not isinstance(keyword, str):
        keyword = ""
    
    keyword = keyword.strip()  # 공백 제거
    
    if not restaurants:
        return "❌ 레스토랑 DB를 불러올 수 없습니다."
    
    # 시간 키 결정
    time_key = "배달 예상 소요시간" if meal_type == "배달" else "매장 식사 예상 소요시간"
    
    filtered = []
    
    for restaurant in restaurants:
        # 메뉴가 없으면 스킵
        if not restaurant.get("menu"):
            continue
        
        # 시간 필터링
        estimated_time = _parse_time(restaurant.get(time_key, ""))
        if estimated_time > max_time_minutes:
            continue
        
        # 키워드 필터링 (선택 사항)
        if keyword:
            keyword_lower = keyword.lower()
            # 식당 이름, 설명, 메뉴명에서 검색 (None 방어 강화)
            name = restaurant.get("name") or ""
            desc = restaurant.get("desc") or ""
            name_match = keyword_lower in name.lower()
            desc_match = keyword_lower in desc.lower()
            menu_match = any(
                keyword_lower in (menu.get("name") or "").lower() 
                for menu in restaurant.get("menu", [])
            )
            
            if not (name_match or desc_match or menu_match):
                continue
        
        # 예산 내 메뉴 찾기
        affordable_menus = [
            menu for menu in restaurant.get("menu", [])
            if _parse_price(menu.get("price")) <= max_budget
        ]
        
        if affordable_menus:
            filtered.append({
                "restaurant": restaurant,
                "affordable_menus": affordable_menus,
                "estimated_time": estimated_time
            })
    
    # 시간 순으로 정렬 (빠른 순)
    filtered.sort(key=lambda x: x["estimated_time"])
    
    # 결과 포맷팅 (최대 10개)
    if not filtered:
        return (
            f"❌ 조건에 맞는 레스토랑이 없습니다.\n"
            f"- 최대 예산: {max_budget:,}원\n"
            f"- 최대 시간: {max_time_minutes}분\n"
            f"- 유형: {meal_type}\n"
            f"- 키워드: {keyword if keyword else '없음'}\n\n"
            f"💡 예산을 늘리거나 시간 제약을 완화해보세요."
        )
    
    result = f"🍽️ **레스토랑 검색 결과** (총 {len(filtered)}개)\n\n"
    result += f"**검색 조건:**\n"
    result += f"- 최대 예산: {max_budget:,}원\n"
    result += f"- 최대 시간: {max_time_minutes}분\n"
    result += f"- 유형: {meal_type}\n"
    result += f"- 키워드: {keyword if keyword else '없음'}\n\n"
    result += "---\n\n"
    
    for idx, item in enumerate(filtered[:10], 1):
        restaurant = item["restaurant"]
        menus = item["affordable_menus"]
        time = item["estimated_time"]
        
        # None 방어 강화
        name = restaurant.get('name') or "이름 없음"
        desc = restaurant.get('desc') or "설명 없음"
        hours = restaurant.get('hours') or "정보 없음"
        
        result += f"### {idx}. {name}\n"
        result += f"**설명:** {desc[:100]}...\n"
        result += f"**예상 소요시간:** {time}분 ({meal_type})\n"
        result += f"**영업시간:** {hours}\n"
        result += f"**추천 메뉴 (예산 내):**\n"
        
        # 가격 순으로 정렬
        menus.sort(key=lambda m: _parse_price(m.get("price")))
        
        for menu in menus[:5]:  # 최대 5개 메뉴
            menu_name = menu.get('name') or "메뉴명 없음"
            price = menu.get("price_krw") or "가격 미정"
            result += f"  - {menu_name}: {price}\n"
        
        if len(menus) > 5:
            result += f"  - ... 외 {len(menus) - 5}개 메뉴\n"
        
        result += "\n"
    
    if len(filtered) > 10:
        result += f"\n💡 {len(filtered) - 10}개 식당이 더 있습니다. 조건을 조정해보세요.\n"
    
    return result


@tool("레스토랑 상세 정보 조회")
def get_restaurant_details(restaurant_name: str) -> str:
    """
    특정 레스토랑의 상세 정보를 조회합니다.
    
    Args:
        restaurant_name: 레스토랑 이름 (필수)
    
    Returns:
        레스토랑의 전체 메뉴, 영업시간, 설명 등 상세 정보
    
    Example:
        레스토랑 상세 정보 조회(restaurant_name="시골식당")
    """
    restaurants = _load_restaurant_db()
    
    # None 및 빈 문자열 체크
    if not restaurant_name or restaurant_name.strip() == "":
        return "❌ 레스토랑 이름을 입력해주세요."
    
    # 이름으로 검색 (부분 일치) - None 방어 강화
    restaurant_name_lower = restaurant_name.lower()
    matches = [
        r for r in restaurants 
        if restaurant_name_lower in (r.get("name") or "").lower()
    ]
    
    if not matches:
        return f"❌ '{restaurant_name}' 레스토랑을 찾을 수 없습니다."
    
    restaurant = matches[0]
    
    # None 방어 강화
    name = restaurant.get('name') or "이름 없음"
    desc = restaurant.get('desc') or "설명 없음"
    hours = restaurant.get('hours') or "정보 없음"
    holidays = restaurant.get('holidays') or "정보 없음"
    delivery_time = restaurant.get('배달 예상 소요시간') or "정보 없음"
    dine_time = restaurant.get('매장 식사 예상 소요시간') or "정보 없음"
    
    result = f"🍽️ **{name}** 상세 정보\n\n"
    result += f"**설명:**\n{desc}\n\n"
    result += f"**영업시간:**\n{hours}\n\n"
    result += f"**휴무일:**\n{holidays}\n\n"
    
    result += f"**배달 예상 시간:** {delivery_time}\n"
    result += f"**매장 식사 예상 시간:** {dine_time}\n\n"
    
    result += "**전체 메뉴:**\n"
    
    menus = restaurant.get("menu", [])
    if not menus:
        result += "  메뉴 정보 없음\n"
    else:
        # 가격 순으로 정렬
        menus.sort(key=lambda m: _parse_price(m.get("price")))
        for menu in menus:
            menu_name = menu.get('name') or "메뉴명 없음"
            price = menu.get("price_krw") or "가격 미정"
            result += f"  - {menu_name}: {price}\n"
    
    return result


@tool("예산 최적화 레스토랑 추천")
def recommend_best_value_restaurants(
    max_budget: int = 100000,
    max_time_minutes: int = 120,
    meal_type: str = "배달"
) -> str:
    """
    가성비가 좋은 레스토랑을 추천합니다.
    예산 대비 메뉴 가격이 낮고 시간 효율이 좋은 곳을 우선 추천합니다.
    
    Args:
        max_budget: 최대 예산 (원) - 기본값 100,000원
        max_time_minutes: 최대 가용 시간 (분) - 기본값 120분
        meal_type: "배달" 또는 "매장" - 기본값 "배달"
    
    Returns:
        가성비 좋은 레스토랑 TOP 5
    
    Example:
        예산 최적화 레스토랑 추천(max_budget=10000, max_time_minutes=30, meal_type="배달")
        예산 최적화 레스토랑 추천() # 모든 파라미터 생략 가능
    """
    restaurants = _load_restaurant_db()
    
    # 기본값 처리 - 모든 파라미터 None 체크
    if max_budget is None or max_budget <= 0:
        max_budget = 100000
    if max_time_minutes is None or max_time_minutes <= 0:
        max_time_minutes = 120
    if meal_type is None or meal_type == "":
        meal_type = "배달"
    
    time_key = "배달 예상 소요시간" if meal_type == "배달" else "매장 식사 예상 소요시간"
    
    candidates = []
    
    for restaurant in restaurants:
        if not restaurant.get("menu"):
            continue
        
        estimated_time = _parse_time(restaurant.get(time_key, ""))
        if estimated_time > max_time_minutes:
            continue
        
        # 예산 내 메뉴 찾기
        affordable_menus = [
            menu for menu in restaurant.get("menu", [])
            if _parse_price(menu.get("price")) <= max_budget
        ]
        
        if not affordable_menus:
            continue
        
        # 가성비 점수 계산: (예산 - 평균 메뉴 가격) / 시간
        avg_price = sum(_parse_price(m.get("price")) for m in affordable_menus) / len(affordable_menus)
        value_score = (max_budget - avg_price) / max(estimated_time, 1)
        
        candidates.append({
            "restaurant": restaurant,
            "menus": affordable_menus,
            "avg_price": avg_price,
            "time": estimated_time,
            "value_score": value_score
        })
    
    # 가성비 점수 순으로 정렬
    candidates.sort(key=lambda x: x["value_score"], reverse=True)
    
    if not candidates:
        return (
            f"❌ 조건에 맞는 레스토랑이 없습니다.\n"
            f"예산: {max_budget:,}원, 시간: {max_time_minutes}분"
        )
    
    result = f"💰 **가성비 최고 레스토랑 TOP 5**\n\n"
    result += f"예산: {max_budget:,}원 이하 | 시간: {max_time_minutes}분 이내 | 유형: {meal_type}\n\n"
    
    for idx, item in enumerate(candidates[:5], 1):
        restaurant = item["restaurant"]
        avg_price = item["avg_price"]
        time = item["time"]
        
        # None 방어 강화
        name = restaurant.get('name') or "이름 없음"
        
        result += f"### {idx}. {name} ⭐\n"
        result += f"**평균 메뉴 가격:** {avg_price:,.0f}원\n"
        result += f"**소요 시간:** {time}분\n"
        result += f"**가성비 점수:** {item['value_score']:.2f}\n"
        result += f"**추천 메뉴:**\n"
        
        # 저렴한 메뉴 3개
        sorted_menus = sorted(item["menus"], key=lambda m: _parse_price(m.get("price")))
        for menu in sorted_menus[:3]:
            menu_name = menu.get('name') or "메뉴명 없음"
            price = menu.get("price_krw") or "가격 미정"
            result += f"  - {menu_name}: {price}\n"
        
        result += "\n"
    
    return result
