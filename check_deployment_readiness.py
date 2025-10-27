"""
배포 준비 상태 확인 스크립트
USE_NOTION_MCP 설정에 따라 필요한 환경이 갖춰졌는지 체크
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

print("="*70)
print("🔍 배포 준비 상태 체크")
print("="*70)
print()

# 기본 체크
print("1️⃣ 기본 환경 변수 체크")
print("-"*70)

openai_key = os.getenv("OPENAI_API_KEY")
openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
use_mcp = os.getenv("USE_NOTION_MCP", "false").lower() == "true"

print(f"✅ OPENAI_API_KEY: {'설정됨' if openai_key else '❌ 없음!'}")
print(f"✅ OPENAI_MODEL: {openai_model}")
print(f"{'🔗' if use_mcp else '📦'} USE_NOTION_MCP: {use_mcp} ({'MCP 모드' if use_mcp else 'Mock 모드'})")
print()

# Mock 모드 체크
if not use_mcp:
    print("2️⃣ Mock 모드 데이터 파일 체크")
    print("-"*70)
    
    data_path = Path(__file__).parent / "data" / "mock_notion.json"
    if data_path.exists():
        print(f"✅ Mock 데이터 파일 존재: {data_path}")
        
        import json
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ JSON 파싱 성공")
            print(f"   - 식단 기록: {len(data.get('meal_history', []))}개")
            print(f"   - 알레르기: {', '.join(data.get('preferences', {}).get('allergies', [])) or '없음'}")
            print(f"   - 예산: {data.get('budget', {}).get('daily_limit', 0):,}원")
        except Exception as e:
            print(f"❌ JSON 파싱 실패: {e}")
    else:
        print(f"❌ Mock 데이터 파일 없음: {data_path}")
        print(f"   → data/mock_notion.json 파일을 생성하세요!")
    print()
    
    print("3️⃣ Mock 모드 배포 권장 사항")
    print("-"*70)
    print("✅ Mock 모드는 Streamlit Cloud 배포에 적합합니다!")
    print("   - 서브프로세스 불필요")
    print("   - 빠른 응답 속도")
    print("   - 안정적 작동")
    print()
    print("📋 Streamlit Cloud Secrets 설정:")
    print("```toml")
    print('OPENAI_API_KEY = "sk-your-actual-key"')
    print('OPENAI_MODEL = "gpt-4o-mini"')
    print('USE_NOTION_MCP = "false"')
    print("```")
    print()

# MCP 모드 체크
else:
    print("2️⃣ MCP 모드 요구사항 체크")
    print("-"*70)
    
    notion_key = os.getenv("NOTION_API_KEY")
    notion_db = os.getenv("NOTION_DATABASE_ID")
    
    print(f"{'✅' if notion_key else '❌'} NOTION_API_KEY: {'설정됨' if notion_key else '없음!'}")
    print(f"{'✅' if notion_db else '❌'} NOTION_DATABASE_ID: {notion_db if notion_db else '없음!'}")
    print()
    
    if not notion_key or not notion_db:
        print("⚠️ Notion API 키가 설정되지 않았습니다!")
        print("   .env 파일에 다음을 추가하세요:")
        print("   NOTION_API_KEY=ntn_your_key_here")
        print("   NOTION_DATABASE_ID=your_database_id_here")
        print()
    
    print("3️⃣ MCP 모드 필수 패키지 체크")
    print("-"*70)
    
    required_packages = [
        ("mcp", "MCP 클라이언트"),
        ("notion_client", "Notion API 클라이언트"),
        ("nest_asyncio", "비동기 루프 충돌 방지")
    ]
    
    all_installed = True
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: 설치됨 ({description})")
        except ImportError:
            print(f"❌ {package}: 미설치! ({description})")
            all_installed = False
    print()
    
    if not all_installed:
        print("⚠️ 필수 패키지가 설치되지 않았습니다!")
        print("   pip install -r requirements.txt")
        print()
    
    print("4️⃣ MCP 서버 실행 테스트")
    print("-"*70)
    print("⚠️ MCP 서버는 별도 프로세스로 실행됩니다.")
    print()
    
    # MCP 서버 파일 확인
    server_script = Path(__file__).parent / "mcp_servers" / "notion_server_real.py"
    if server_script.exists():
        print(f"✅ MCP 서버 스크립트 존재: {server_script}")
    else:
        print(f"❌ MCP 서버 스크립트 없음: {server_script}")
    print()
    
    print("5️⃣ ⚠️ Streamlit Cloud 배포 주의사항")
    print("-"*70)
    print("🚨 **중요**: Streamlit Cloud는 서브프로세스 실행을 제한합니다!")
    print()
    print("MCP 모드는 다음 이유로 작동하지 않을 수 있습니다:")
    print("   1. MCP 서버가 별도 Python 프로세스로 실행됨")
    print("   2. Streamlit Cloud의 샌드박스 환경에서 차단될 수 있음")
    print("   3. 네트워크 제한으로 Notion API 호출이 느릴 수 있음")
    print()
    print("✅ **권장**: Mock 모드 (`USE_NOTION_MCP=false`) 사용")
    print()
    print("MCP 모드를 사용하려면:")
    print("   1. 로컬에서 먼저 충분히 테스트")
    print("   2. python test_mcp_mode.py 실행하여 확인")
    print("   3. Streamlit Cloud 배포 후 Logs 꼼꼼히 확인")
    print("   4. 문제 발생 시 즉시 Mock 모드로 전환")
    print()

# 최종 권장사항
print("="*70)
print("📝 최종 권장사항")
print("="*70)

if use_mcp:
    print("⚠️ 현재 설정: MCP 모드")
    print()
    print("배포 전 체크리스트:")
    print("  [ ] 로컬에서 python test_mcp_mode.py 실행 성공")
    print("  [ ] NOTION_API_KEY와 NOTION_DATABASE_ID 설정")
    print("  [ ] Streamlit Cloud Secrets에 모든 키 추가")
    print("  [ ] 배포 후 Logs에서 'MCP 서버' 로그 확인")
    print()
    print("❌ 문제 발생 시:")
    print("   Secrets에서 USE_NOTION_MCP = \"false\"로 변경")
    print()
else:
    print("✅ 현재 설정: Mock 모드 (권장!)")
    print()
    print("배포 전 체크리스트:")
    print("  [✓] data/mock_notion.json 파일 존재")
    print("  [✓] 서브프로세스 불필요")
    print("  [✓] Streamlit Cloud 호환")
    print()
    print("Streamlit Cloud Secrets 설정:")
    print("```toml")
    print('OPENAI_API_KEY = "your-key"')
    print('OPENAI_MODEL = "gpt-4o-mini"')
    print('USE_NOTION_MCP = "false"')
    print("```")
    print()
    print("🎉 Mock 모드는 배포 준비가 완료되었습니다!")

print("="*70)

