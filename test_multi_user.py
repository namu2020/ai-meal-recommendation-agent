"""
다중 사용자 테스트
"""
import asyncio
import os
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from user_manager import get_all_users, get_user_info


async def test_user(username):
    """특정 사용자 데이터 테스트"""
    print(f"\n{'='*70}")
    print(f"👤 {username}님 데이터 테스트")
    print(f"{'='*70}\n")
    
    user_info = get_user_info(username)
    print(f"이모지: {user_info['emoji']}")
    print(f"설명: {user_info['description']}")
    print(f"특징: {user_info['special']}")
    print(f"Notion 페이지 ID: {user_info['id']}")
    print()
    
    # 환경 변수 설정
    os.environ["CURRENT_NOTION_USER"] = username
    
    # notion_server_real의 함수 직접 호출
    from mcp_servers.notion_server_real import query_notion_pages
    
    print("📡 Notion API 호출 중...")
    data = await query_notion_pages()
    
    print()
    print(f"✅ {username}님 데이터 조회 성공!")
    print()
    print(f"📊 알레르기: {', '.join(data['preferences']['allergies']) if data['preferences']['allergies'] else '없음'}")
    print(f"🥗 다이어트 목표: {data['preferences']['diet_goal']}")
    print(f"❤️ 선호 음식: {', '.join(data['preferences']['favorite_cuisines'][:2])}")
    print(f"⏰ 가용 시간: {data['schedule']['available_time']}분")
    print(f"💰 일일 예산: {data['budget']['daily_limit']:,}원")
    print()


async def main():
    """메인 함수"""
    print("="*70)
    print("🧪 다중 사용자 Notion 데이터 테스트")
    print("="*70)
    
    users = get_all_users()
    
    for username in users[:3]:  # 처음 3명만 테스트
        try:
            await test_user(username)
        except Exception as e:
            print(f"❌ {username}님 테스트 실패: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print()
    print("="*70)
    print("✅ 테스트 완료!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())

