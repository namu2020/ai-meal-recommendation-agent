"""
Notion API 직접 테스트
MCP 없이 Notion API를 직접 호출하여 데이터 구조 확인
"""
import asyncio
import json
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

# 환경 변수 로드
load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")  # 실제로는 페이지 ID일 수 있음


async def test_notion_connection():
    """Notion API 연결 테스트"""
    print("="*70)
    print("🔍 Notion API 연결 테스트")
    print("="*70)
    print()
    
    if not NOTION_API_KEY:
        print("❌ NOTION_API_KEY가 .env 파일에 설정되지 않았습니다!")
        return
    
    if not NOTION_DATABASE_ID:
        print("❌ NOTION_DATABASE_ID가 .env 파일에 설정되지 않았습니다!")
        return
    
    print(f"✅ NOTION_API_KEY: {NOTION_API_KEY[:20]}...")
    print(f"✅ NOTION_DATABASE_ID: {NOTION_DATABASE_ID}")
    print()
    
    notion = AsyncClient(auth=NOTION_API_KEY)
    
    try:
        # 1. 페이지 자체 조회
        print("📄 1단계: 메인 페이지 조회")
        print("-" * 70)
        page = await notion.pages.retrieve(page_id=NOTION_DATABASE_ID)
        
        print(f"✅ 페이지 ID: {page.get('id')}")
        print(f"   생성일: {page.get('created_time')}")
        print(f"   수정일: {page.get('last_edited_time')}")
        
        # 페이지 제목 추출
        if 'properties' in page:
            for prop_name, prop_data in page['properties'].items():
                if prop_data.get('type') == 'title':
                    if prop_data.get('title'):
                        title = prop_data['title'][0]['plain_text']
                        print(f"   제목: {title}")
        print()
        
        # 2. 하위 블록들 조회
        print("📦 2단계: 하위 블록/페이지 조회")
        print("-" * 70)
        children = await notion.blocks.children.list(block_id=NOTION_DATABASE_ID)
        
        blocks = children.get('results', [])
        print(f"✅ 하위 블록 수: {len(blocks)}")
        print()
        
        # 각 블록 상세 정보
        for i, block in enumerate(blocks, 1):
            block_type = block.get('type')
            block_id = block.get('id')
            
            print(f"{i}. 블록 타입: {block_type}")
            print(f"   ID: {block_id}")
            
            if block_type == 'child_page':
                # 하위 페이지인 경우 페이지 정보 가져오기
                try:
                    child_page = await notion.pages.retrieve(page_id=block_id)
                    
                    # 제목 추출
                    page_title = "제목 없음"
                    if 'properties' in child_page:
                        for prop_name, prop_data in child_page['properties'].items():
                            if prop_data.get('type') == 'title':
                                if prop_data.get('title'):
                                    page_title = prop_data['title'][0]['plain_text']
                                    break
                    
                    print(f"   📄 페이지 제목: {page_title}")
                    
                    # 하위 페이지의 프로퍼티 출력
                    if 'properties' in child_page:
                        print(f"   프로퍼티:")
                        for prop_name, prop_data in child_page['properties'].items():
                            prop_type = prop_data.get('type')
                            print(f"     - {prop_name} ({prop_type})")
                    
                    # 하위 페이지의 내용(블록) 조회
                    page_content = await notion.blocks.children.list(block_id=block_id)
                    content_blocks = page_content.get('results', [])
                    print(f"   내용 블록 수: {len(content_blocks)}")
                    
                    # 처음 몇 개 블록 출력
                    for j, content_block in enumerate(content_blocks[:3], 1):
                        content_type = content_block.get('type')
                        print(f"     {j}. {content_type}")
                        
                        # 텍스트 내용 추출
                        if content_type == 'paragraph':
                            paragraph = content_block.get('paragraph', {})
                            rich_text = paragraph.get('rich_text', [])
                            if rich_text:
                                text = rich_text[0].get('plain_text', '')
                                print(f"        내용: {text[:50]}...")
                        
                        elif content_type == 'heading_1':
                            heading = content_block.get('heading_1', {})
                            rich_text = heading.get('rich_text', [])
                            if rich_text:
                                text = rich_text[0].get('plain_text', '')
                                print(f"        제목: {text}")
                        
                        elif content_type == 'heading_2':
                            heading = content_block.get('heading_2', {})
                            rich_text = heading.get('rich_text', [])
                            if rich_text:
                                text = rich_text[0].get('plain_text', '')
                                print(f"        소제목: {text}")
                        
                        elif content_type == 'bulleted_list_item':
                            item = content_block.get('bulleted_list_item', {})
                            rich_text = item.get('rich_text', [])
                            if rich_text:
                                text = rich_text[0].get('plain_text', '')
                                print(f"        • {text}")
                    
                    if len(content_blocks) > 3:
                        print(f"     ... 외 {len(content_blocks) - 3}개 블록")
                    
                except Exception as e:
                    print(f"   ⚠️ 페이지 조회 실패: {str(e)}")
            
            print()
        
        # 3. 전체 구조를 JSON으로 저장
        print("💾 3단계: 데이터 구조 저장")
        print("-" * 70)
        
        output_file = "notion_structure.json"
        structure_data = {
            "main_page": {
                "id": page.get('id'),
                "properties": page.get('properties', {}),
                "created_time": page.get('created_time'),
                "last_edited_time": page.get('last_edited_time')
            },
            "children": []
        }
        
        for block in blocks:
            block_info = {
                "id": block.get('id'),
                "type": block.get('type'),
            }
            
            if block.get('type') == 'child_page':
                try:
                    child_page = await notion.pages.retrieve(page_id=block.get('id'))
                    block_info['page_data'] = {
                        "properties": child_page.get('properties', {}),
                        "created_time": child_page.get('created_time'),
                        "last_edited_time": child_page.get('last_edited_time')
                    }
                    
                    # 페이지 내용
                    page_content = await notion.blocks.children.list(block_id=block.get('id'))
                    block_info['content_blocks'] = page_content.get('results', [])
                except:
                    pass
            
            structure_data['children'].append(block_info)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(structure_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 데이터 구조를 '{output_file}'에 저장했습니다.")
        print(f"   이 파일을 확인하여 Notion 데이터 구조를 파악할 수 있습니다.")
        print()
        
        print("="*70)
        print("✅ 테스트 완료!")
        print("="*70)
        print()
        print("📝 다음 단계:")
        print("   1. notion_structure.json 파일을 열어서 데이터 구조 확인")
        print("   2. 데이터 구조에 맞게 파싱 로직 구현")
        print("   3. mcp_servers/notion_server_real.py 수정")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        print()
        print("상세 오류:")
        traceback.print_exc()
        print()
        print("💡 확인사항:")
        print("   1. NOTION_API_KEY가 올바른가?")
        print("   2. NOTION_DATABASE_ID가 올바른 페이지/DB ID인가?")
        print("   3. Notion Integration이 해당 페이지에 연결되어 있는가?")


if __name__ == "__main__":
    asyncio.run(test_notion_connection())

