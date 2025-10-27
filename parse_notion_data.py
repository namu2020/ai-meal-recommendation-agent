"""
Notion 데이터 파싱 스크립트
notion_structure.json에서 사용자별 데이터를 추출하여 mock_notion.json 형식으로 변환
"""
import json
import asyncio
import os
from dotenv import load_dotenv
from notion_client import AsyncClient

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# 사용자 선택 - 전체 파싱 모드
PARSE_ALL_USERS = True  # True: 모든 사용자 파싱, False: 기본 사용자만
DEFAULT_USER = "지민"  # PARSE_ALL_USERS=False일 때 사용


def extract_text_from_rich_text(rich_text_array):
    """rich_text 배열에서 텍스트 추출"""
    if not rich_text_array:
        return ""
    return "".join([item.get('plain_text', '') for item in rich_text_array])


async def fetch_table_rows(notion, table_block_id):
    """테이블의 행 데이터 가져오기"""
    try:
        # 테이블 블록의 자식 블록들(행들) 가져오기
        response = await notion.blocks.children.list(block_id=table_block_id)
        rows = []
        
        for block in response.get('results', []):
            if block.get('type') == 'table_row':
                row_data = block.get('table_row', {})
                cells = row_data.get('cells', [])
                
                # 각 셀의 텍스트 추출
                row = [extract_text_from_rich_text(cell) for cell in cells]
                rows.append(row)
        
        return rows
    except Exception as e:
        print(f"⚠️ 테이블 행 가져오기 실패: {str(e)}")
        return []


async def parse_user_page(notion, page_id, username):
    """사용자 페이지에서 데이터 파싱"""
    print(f"\n{'='*70}")
    print(f"📄 {username}의 데이터 파싱 중...")
    print(f"{'='*70}\n")
    
    # 페이지 블록들 가져오기
    response = await notion.blocks.children.list(block_id=page_id)
    blocks = response.get('results', [])
    
    # 데이터 구조
    user_data = {
        "meal_history": [],
        "preferences": {
            "allergies": [],
            "dislikes": [],
            "diet_goal": "",
            "favorite_cuisines": [],
            "spicy_level": "보통",
            "cooking_skill": "중급"
        },
        "schedule": {
            "today": "2025-10-25",
            "available_time": 30,
            "meal_time": "점심"
        },
        "budget": {
            "daily_limit": 20000,
            "today_spent": 8000,
            "preferred_range": [8000, 15000]
        }
    }
    
    current_section = None
    
    for i, block in enumerate(blocks):
        block_type = block.get('type')
        
        # 섹션 헤더 파악
        if block_type == 'heading_3':
            heading = block.get('heading_3', {})
            section_title = extract_text_from_rich_text(heading.get('rich_text', []))
            current_section = section_title
            print(f"\n📌 섹션: {section_title}")
        
        # 설명 텍스트에서 정보 추출
        elif block_type == 'bulleted_list_item':
            item = block.get('bulleted_list_item', {})
            text = extract_text_from_rich_text(item.get('rich_text', []))
            
            if '알레르기' in text or 'allergies' in text.lower():
                print(f"   • {text}")
        
        # 테이블 처리
        elif block_type == 'table':
            table_id = block.get('id')
            print(f"   테이블 ID: {table_id}")
            
            # 테이블 행 가져오기
            rows = await fetch_table_rows(notion, table_id)
            
            if rows and current_section:
                print(f"   행 수: {len(rows)}")
                
                # 섹션별 데이터 파싱
                if 'Quick Profile' in current_section or '프로필' in current_section:
                    # 프로필 정보
                    for row in rows[1:]:  # 헤더 제외
                        if len(row) >= 2:
                            key = row[0].strip()
                            value = row[1].strip()
                            print(f"     {key}: {value}")
                            
                            if '알레르기' in key:
                                user_data['preferences']['allergies'] = [
                                    v.strip() for v in value.split(',') if v.strip()
                                ]
                            elif '싫어하는' in key or '기피' in key:
                                user_data['preferences']['dislikes'] = [
                                    v.strip() for v in value.split(',') if v.strip()
                                ]
                            elif '다이어트' in key or '목표' in key:
                                user_data['preferences']['diet_goal'] = value
                            elif '매운맛' in key or '스파이시' in key:
                                user_data['preferences']['spicy_level'] = value
                            elif '요리실력' in key or 'cooking' in key.lower():
                                user_data['preferences']['cooking_skill'] = value
                
                elif '예산' in current_section or 'budget' in current_section.lower():
                    # 예산 정보
                    for row in rows[1:]:  # 헤더 제외
                        if len(row) >= 2:
                            key = row[0].strip()
                            value = row[1].strip()
                            print(f"     {key}: {value}")
                            
                            try:
                                # 숫자 추출
                                import re
                                numbers = re.findall(r'\d+', value.replace(',', ''))
                                if numbers:
                                    num_value = int(numbers[0])
                                    
                                    if '일일' in key or '하루' in key:
                                        user_data['budget']['daily_limit'] = num_value
                                    elif '오늘' in key or '현재' in key or '지출' in key:
                                        user_data['budget']['today_spent'] = num_value
                                    elif '최소' in key or 'min' in key.lower():
                                        user_data['budget']['preferred_range'][0] = num_value
                                    elif '최대' in key or 'max' in key.lower():
                                        user_data['budget']['preferred_range'][1] = num_value
                            except:
                                pass
                
                elif '스케줄' in current_section or 'schedule' in current_section.lower():
                    # 일정 정보
                    for row in rows[1:]:  # 헤더 제외
                        if len(row) >= 2:
                            key = row[0].strip()
                            value = row[1].strip()
                            print(f"     {key}: {value}")
                            
                            try:
                                import re
                                if '시간' in key and '분' not in value:
                                    numbers = re.findall(r'\d+', value)
                                    if numbers:
                                        user_data['schedule']['available_time'] = int(numbers[0])
                                elif '식사' in key or '슬롯' in key:
                                    user_data['schedule']['meal_time'] = value
                                    # 15분 식사라는 정보가 있으면 available_time 설정
                                    if '15' in value:
                                        user_data['schedule']['available_time'] = 15
                            except:
                                pass
                
                elif '오늘의 상태' in current_section:
                    # 식단 기록 (샘플)
                    print(f"     식단 기록: {len(rows)-1}개")
                    # 실제 식단 기록 파싱
                    for row in rows[1:]:  # 헤더 제외
                        if len(row) >= 4:  # 날짜, 식사, 메뉴, 칼로리 등
                            try:
                                meal_entry = {
                                    "date": row[0].strip() if row[0] else "",
                                    "type": row[1].strip() if len(row) > 1 and row[1] else "",
                                    "meal": row[2].strip() if len(row) > 2 and row[2] else "",
                                    "calories": 0,
                                    "cost": 0
                                }
                                
                                # 칼로리와 비용 파싱
                                if len(row) > 3 and row[3]:
                                    import re
                                    cal_match = re.search(r'(\d+)', row[3])
                                    if cal_match:
                                        meal_entry["calories"] = int(cal_match.group(1))
                                
                                if len(row) > 4 and row[4]:
                                    import re
                                    cost_match = re.search(r'(\d+)', row[4].replace(',', ''))
                                    if cost_match:
                                        meal_entry["cost"] = int(cost_match.group(1))
                                
                                if meal_entry["meal"]:  # 메뉴가 있는 경우만 추가
                                    user_data["meal_history"].append(meal_entry)
                            except Exception as e:
                                print(f"     ⚠️ 식단 기록 파싱 실패: {e}")
                                pass
    
    print(f"\n✅ {username} 데이터 파싱 완료!")
    return user_data


async def main():
    """메인 함수"""
    print("="*70)
    print("🔍 Notion 데이터 파싱")
    print("="*70)
    
    if not NOTION_API_KEY:
        print("❌ NOTION_API_KEY가 설정되지 않았습니다!")
        return
    
    notion = AsyncClient(auth=NOTION_API_KEY)
    
    try:
        # 메인 페이지의 하위 페이지들 가져오기
        response = await notion.blocks.children.list(block_id=NOTION_DATABASE_ID)
        blocks = response.get('results', [])
        
        # 사용자 페이지 찾기
        user_pages = {}
        for block in blocks:
            if block.get('type') == 'child_page':
                page_id = block.get('id')
                page = await notion.pages.retrieve(page_id=page_id)
                
                # 페이지 제목 추출
                title = ""
                if 'properties' in page:
                    for prop_name, prop_data in page['properties'].items():
                        if prop_data.get('type') == 'title':
                            if prop_data.get('title'):
                                title = prop_data['title'][0]['plain_text']
                                break
                
                # 사용자 이름 추출 (예: "소윤의 식사 노트" -> "소윤")
                for name in ['소윤', '태식', '지민', '현우', '라미']:
                    if name in title:
                        user_pages[name] = page_id
                        print(f"✅ {name}의 페이지 발견: {page_id}")
                        break
        
        print()
        
        # 사용자 데이터 파싱
        if PARSE_ALL_USERS:
            # 모든 사용자 파싱
            print("🔄 모든 사용자 데이터 파싱 중...")
            print("="*70)
            
            for username, page_id in user_pages.items():
                user_data = await parse_user_page(notion, page_id, username)
                
                # 사용자별 파일로 저장
                output_file = f"data/parsed_notion_{username}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 {username}의 데이터를 '{output_file}'에 저장했습니다.")
                
                # 간단한 요약 출력
                allergies = user_data.get('preferences', {}).get('allergies', [])
                diet_goal = user_data.get('preferences', {}).get('diet_goal', '')
                meal_count = len(user_data.get('meal_history', []))
                
                print(f"   - 알레르기: {allergies if allergies else '없음'}")
                print(f"   - 다이어트 목표: {diet_goal if diet_goal else '없음'}")
                print(f"   - 식단 기록: {meal_count}개")
                print()
            
            print("="*70)
            print(f"✅ 총 {len(user_pages)}명의 사용자 데이터 파싱 완료!")
            print("="*70)
        else:
            # 기본 사용자만 파싱
            if DEFAULT_USER in user_pages:
                user_data = await parse_user_page(notion, user_pages[DEFAULT_USER], DEFAULT_USER)
                
                # mock_notion.json 형식으로 저장
                output_file = "data/parsed_notion.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(user_data, f, ensure_ascii=False, indent=2)
                
                print(f"\n💾 파싱된 데이터를 '{output_file}'에 저장했습니다.")
                print("\n📊 파싱된 데이터:")
                print(json.dumps(user_data, ensure_ascii=False, indent=2))
            else:
                print(f"❌ {DEFAULT_USER}의 페이지를 찾을 수 없습니다.")
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

