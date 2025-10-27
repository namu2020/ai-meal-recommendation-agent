"""
사용자 관리 모듈
Notion의 5명 페르소나 정보 관리
"""
import json
from pathlib import Path

# 사용자 정보 (Notion 페이지 ID와 매핑)
# ⚠️ 실제 Notion 페이지 내용과 정확히 일치하도록 수정됨
USERS = {
    "소윤": {
        "id": "2976b5ca-f706-80a9-88cb-f1f95a3243b3",
        "name": "소윤",
        "emoji": "🌙",
        "description": "격주 야간근무. 15분 식사, 갑각류 알레르기. 분식 감성 유지.",
        "special": "야간근무 | 빠른 식사 | 갑각류 알레르기"
    },
    "태식": {
        "id": "2976b5ca-f706-8060-a84a-eae4123fca93",
        "name": "태식",
        "emoji": "👴",
        "description": "당뇨·고혈압. 따뜻한 한식 선호, 전자레인지만 사용.",
        "special": "당뇨/고혈압 | 한식 선호 | 전자레인지"
    },
    "지민": {
        "id": "2976b5ca-f706-800b-b4ca-ee7b2a20481b",
        "name": "지민",
        "emoji": "🥗",
        "description": "평일 락토오보, 주말 페스코. 식이섬유↑, 버섯 식감 기피.",
        "special": "채식 중심 | 장건강 | 버섯 기피"
    },
    "현우": {
        "id": "2976b5ca-f706-8020-8d0c-f62f49a4a885",
        "name": "현우",
        "emoji": "🏃",
        "description": "퇴근 헬스 후 빠르고 가벼운 저녁을 찾는 다이어터. 유당불내증.",
        "special": "헬스 다이어터 | 유당불내증 | 1,800kcal"
    },
    "라미": {
        "id": "2976b5ca-f706-809f-bbbe-f3017ea2649a",
        "name": "라미",
        "emoji": "💪",
        "description": "벌크업. 운동 전후 단백질 타이밍, 주 1회 밀프렙.",
        "special": "벌크업 | 고단백 | 2,800kcal"
    }
}


def get_all_users():
    """모든 사용자 목록 반환"""
    return list(USERS.keys())


def get_user_info(username):
    """특정 사용자 정보 반환"""
    return USERS.get(username)


def get_user_id(username):
    """특정 사용자의 Notion 페이지 ID 반환"""
    user = USERS.get(username)
    return user["id"] if user else None


def save_current_user(username):
    """현재 선택된 사용자를 파일에 저장"""
    user_file = Path(__file__).parent / "data" / "current_user.json"
    user_file.parent.mkdir(exist_ok=True)
    
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump({"current_user": username}, f, ensure_ascii=False)


def load_current_user():
    """저장된 현재 사용자 불러오기"""
    user_file = Path(__file__).parent / "data" / "current_user.json"
    
    if not user_file.exists():
        return None
    
    try:
        with open(user_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("current_user")
    except:
        return None

