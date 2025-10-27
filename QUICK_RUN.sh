#!/bin/bash

# Notion MCP 통합 빠른 실행 스크립트

echo "=================================="
echo "🚀 Notion MCP 통합 테스트"
echo "=================================="
echo ""

# 1. 패키지 설치
echo "📦 1단계: 패키지 설치..."
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org notion-client nest-asyncio 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ 패키지 설치 완료"
else
    echo "⚠️ 패키지 설치 실패 - 수동으로 설치해주세요"
    echo "   pip install notion-client nest-asyncio"
fi
echo ""

# 2. .env 파일 확인
echo "🔍 2단계: .env 파일 확인..."
if [ -f .env ]; then
    if grep -q "NOTION_API_KEY" .env && grep -q "NOTION_DATABASE_ID" .env; then
        echo "✅ .env 파일에 Notion 설정 있음"
    else
        echo "⚠️ .env 파일에 Notion 설정이 없습니다"
        echo "   다음 내용을 .env 파일에 추가하세요:"
        echo "   NOTION_API_KEY=secret_xxx"
        echo "   NOTION_DATABASE_ID=page_id"
        exit 1
    fi
else
    echo "❌ .env 파일이 없습니다. 먼저 .env 파일을 생성하세요."
    exit 1
fi
echo ""

# 3. Notion API 테스트
echo "🧪 3단계: Notion API 연결 테스트..."
python test_notion_api.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Notion API 테스트 완료!"
    echo ""
    
    # 4. 생성된 파일 확인
    if [ -f notion_structure.json ]; then
        echo "📄 생성된 파일:"
        echo "   - notion_structure.json (Notion 데이터 구조)"
        echo ""
        echo "📊 다음 명령어로 데이터 구조 확인:"
        echo "   cat notion_structure.json | python -m json.tool | less"
        echo ""
    fi
    
    # 5. 다음 단계 안내
    echo "🎯 다음 단계:"
    echo "   1. notion_structure.json 파일을 확인하여 데이터 구조 파악"
    echo "   2. mcp_servers/notion_server_real.py에 파싱 로직 구현"
    echo "   3. python test_mcp_client.py로 MCP 테스트"
    echo "   4. streamlit run app.py로 전체 시스템 테스트"
    echo ""
    echo "📖 상세 가이드: TEST_NOTION_INTEGRATION.md 참고"
    
else
    echo ""
    echo "❌ Notion API 테스트 실패"
    echo ""
    echo "💡 확인사항:"
    echo "   1. NOTION_API_KEY가 올바른가요?"
    echo "   2. NOTION_DATABASE_ID가 올바른 페이지 ID인가요?"
    echo "   3. Notion Integration이 해당 페이지에 연결되어 있나요?"
    echo ""
    echo "📖 자세한 내용: TEST_NOTION_INTEGRATION.md 참고"
fi

echo ""
echo "=================================="

