"""
MCP 모드 테스트 스크립트
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("🧪 MCP 모드 테스트")
print("="*70)
print()

# 환경 변수 확인
use_mcp = os.getenv("USE_NOTION_MCP", "false").lower() == "true"
notion_key = os.getenv("NOTION_API_KEY")
notion_db = os.getenv("NOTION_DATABASE_ID")

print(f"USE_NOTION_MCP: {use_mcp}")
print(f"NOTION_API_KEY: {'설정됨' if notion_key else '없음'}")
print(f"NOTION_DATABASE_ID: {notion_db if notion_db else '없음'}")
print()

if not use_mcp:
    print("⚠️ MCP 모드가 비활성화되어 있습니다. Mock 모드로 실행됩니다.")
    print("   .env 파일에서 USE_NOTION_MCP=true로 설정하세요.")
    print()

# Tools 테스트
print("="*70)
print("📦 Tools 불러오기")
print("="*70)
print()

try:
    from tools.notion_tools import (
        get_meal_history,
        get_user_preferences,
        get_user_schedule,
        get_budget_status
    )
    print("✅ Tools 임포트 성공")
    print()
except Exception as e:
    print(f"❌ Tools 임포트 실패: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# 각 tool 테스트
print("="*70)
print("🔍 Tool 테스트")
print("="*70)
print()

try:
    print("1️⃣ 사용자 선호도 조회")
    print("-"*70)
    result = get_user_preferences()
    print(result)
    print()
    
    print("2️⃣ 사용자 일정 조회")
    print("-"*70)
    result = get_user_schedule()
    print(result)
    print()
    
    print("3️⃣ 예산 현황 조회")
    print("-"*70)
    result = get_budget_status()
    print(result)
    print()
    
    print("4️⃣ 식단 기록 조회")
    print("-"*70)
    result = get_meal_history(7)
    print(result)
    print()
    
    print("="*70)
    print("✅ 모든 테스트 완료!")
    print("="*70)
    
except Exception as e:
    print(f"❌ 테스트 실패: {e}")
    import traceback
    traceback.print_exc()

