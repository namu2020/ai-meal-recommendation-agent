"""
MCP 실시간 모드 테스트
USE_NOTION_MCP=true 모드에서 실제 Notion API 데이터를 가져오는지 검증
"""
import asyncio
import os
import sys
from pathlib import Path

# MCP 클라이언트 import
sys.path.append(str(Path(__file__).parent))
from mcp_client.notion_mcp_client import get_mcp_client
import json


async def test_real_mode_user(username):
    """실시간 Notion API 모드에서 특정 사용자 테스트"""
    print(f"\n{'='*70}")
    print(f"🔥 {username}의 데이터 테스트 (실시간 Notion API)")
    print(f"{'='*70}")
    
    # 환경 변수 설정
    os.environ["CURRENT_NOTION_USER"] = username
    os.environ["USE_NOTION_MCP"] = "true"  # 실시간 Notion API 모드
    
    client = get_mcp_client()
    
    try:
        async with client.connect():
            # 사용자 선호도 조회
            print("\n📋 사용자 선호도 조회 중...")
            preferences_result = await client.call_tool("get_user_preferences", {})
            preferences = json.loads(preferences_result)
            
            print(f"✅ 알레르기: {preferences.get('allergies', [])}")
            
            # health_conditions 확인 (태식)
            if 'health_conditions' in preferences:
                print(f"✅ 건강 상태: {preferences.get('health_conditions', [])}")
            
            # dietary_restrictions 확인 (지민, 태식)
            if 'dietary_restrictions' in preferences:
                restrictions = preferences.get('dietary_restrictions', {})
                print(f"✅ 식이 제한: {restrictions}")
            
            print(f"✅ 싫어하는 음식: {preferences.get('dislikes', [])}")
            print(f"✅ 다이어트 목표: {preferences.get('diet_goal', '없음')}")
            
            print(f"\n{'='*70}")
            print(f"✅ {username} 실시간 모드 테스트 완료!")
            print(f"{'='*70}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """주요 사용자 실시간 모드 테스트"""
    print("="*70)
    print("🔥 실시간 Notion API 모드 테스트")
    print("="*70)
    print("⚠️ 이 테스트는 실제 Notion API를 호출합니다.")
    print()
    
    # 대표 사용자만 테스트 (API 호출 최소화)
    users = ["소윤", "태식", "지민"]
    
    for username in users:
        await test_real_mode_user(username)
        await asyncio.sleep(0.5)
    
    print("\n" + "="*70)
    print("✅ 실시간 모드 테스트 완료!")
    print("="*70)
    print("\n📊 검증 포인트:")
    print("   - 소윤: 갑각류 알레르기가 실제 Notion에서 로드되는가?")
    print("   - 태식: health_conditions에 당뇨/고혈압이 있는가?")
    print("   - 지민: dietary_restrictions에 락토오보/페스코 정보가 있는가?")


if __name__ == "__main__":
    asyncio.run(main())

