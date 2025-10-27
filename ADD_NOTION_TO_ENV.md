# .env 파일에 Notion 설정 추가하기

## 현재 상태
`.env` 파일에 OpenAI 설정만 있고 Notion 설정이 없습니다.

## 추가할 내용

`.env` 파일을 열어서 다음 3줄을 **맨 아래에 추가**하세요:

```bash
# MCP 사용 설정 (true로 설정하면 실제 Notion 사용)
USE_NOTION_MCP=false

# Notion API 설정
NOTION_API_KEY=여기에_Notion_Integration_Secret_붙여넣기
NOTION_DATABASE_ID=여기에_Notion_페이지ID_붙여넣기
```

## 설정 방법

### 1. Notion Integration Secret 가져오기
1. https://www.notion.so/my-integrations 접속
2. 생성한 Integration 클릭
3. "Internal Integration Secret" 복사
4. `NOTION_API_KEY=` 뒤에 붙여넣기
   - 예: `NOTION_API_KEY=secret_abc123...`

### 2. Notion 페이지 ID 가져오기
1. Notion에서 데이터가 있는 페이지 열기
2. URL 확인: `https://www.notion.so/workspace명/페이지ID?v=...`
3. URL에서 32자리 ID 복사 (하이픈 포함)
   - 예: `abc123def456ghi789jkl012mno345pq`
4. `NOTION_DATABASE_ID=` 뒤에 붙여넣기
   - 예: `NOTION_DATABASE_ID=abc123def456ghi789jkl012mno345pq`

### 3. Integration 연결 확인
Notion 페이지에서:
1. 우측 상단 "..." 클릭
2. "Connections" 클릭
3. 생성한 Integration이 연결되어 있는지 확인
4. 없으면 추가!

## 빠른 설정 (터미널)

```bash
# .env 파일 열기
nano .env

# 또는
code .env
```

그 다음 위의 3줄을 추가하고 저장하세요.

## 설정 확인

```bash
# 제대로 추가되었는지 확인
cat .env | grep NOTION
```

예상 출력:
```
USE_NOTION_MCP=false
NOTION_API_KEY=secret_xxx...
NOTION_DATABASE_ID=abc123...
```

## 다음 단계

설정 완료 후:
```bash
./QUICK_RUN.sh
```

다시 실행하면 Notion API 연결이 테스트됩니다!

