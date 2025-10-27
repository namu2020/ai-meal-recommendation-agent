"""
간단한 MCP 서버 테스트
"""
import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
sys.path.insert(0, str(Path(__file__).parent))

async def test_server():
    """MCP 서버 직접 테스트"""
    print("="*70)
    print("🧪 MCP 서버 직접 테스트")
    print("="*70)
    print()
    
    # notion_server_real의 함수 직접 호출
    from mcp_servers.notion_server_real import query_notion_pages
    
    print("📡 Notion API 호출 중...")
    data = await query_notion_pages()
    
    print()
    print("✅ 데이터 조회 성공!")
    print()
    print("="*70)
    print("📊 조회된 데이터:")
    print("="*70)
    
    import json
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    print()
    print("="*70)
    print("✅ 테스트 완료!")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_server())

