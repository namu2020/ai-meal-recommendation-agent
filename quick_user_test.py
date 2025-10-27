"""
빠른 사용자 전환 테스트
Mock 모드에서 각 사용자가 올바른 데이터를 받는지 간단히 검증
"""
import os
os.environ["USE_NOTION_MCP"] = "false"  # Mock 모드

from tools.notion_tools_mcp import get_user_preferences
import json

print("="*70)
print("🔍 사용자 전환 테스트 (Mock 모드)")
print("="*70)

users = ["소윤", "태식", "지민", "현우", "라미"]

for user in users:
    print(f"\n{'─'*70}")
    print(f"👤 {user}")
    print(f"{'─'*70}")
    
    # 환경 변수로 사용자 설정
    os.environ["CURRENT_NOTION_USER"] = user
    
    # 선호도 조회
    result = get_user_preferences()
    data = json.loads(result)
    
    allergies = data.get('allergies', [])
    dislikes = data.get('dislikes', [])
    diet_goal = data.get('diet_goal', '')
    
    print(f"   알레르기: {allergies if allergies else '없음'}")
    print(f"   기피음식: {dislikes if dislikes else '없음'}")
    print(f"   목표: {diet_goal if diet_goal else '없음'}")
    
    # 건강 상태 (태식)
    if 'health_conditions' in data and data['health_conditions']:
        print(f"   건강상태: {data['health_conditions']}")
    
    # 식이 제한 (지민, 태식)
    if 'dietary_restrictions' in data and data['dietary_restrictions']:
        restrictions = data['dietary_restrictions']
        if isinstance(restrictions, dict) and restrictions:
            print(f"   식이제한: {restrictions}")

print("\n" + "="*70)
print("✅ 모든 사용자 전환 테스트 완료!")
print("="*70)

