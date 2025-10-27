# 🚀 설치 및 실행 가이드

## 1. 환경 설정

### 1-1. Python 가상환경 생성 (권장)

```bash
cd crewai-food-app

# 가상환경 생성
python -m venv venv

# 가상환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 1-2. 의존성 설치

```bash
pip install -r requirements.txt
```

## 2. OpenAI API 키 설정

### 2-1. `.env` 파일 생성

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 입력하세요:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 2-2. OpenAI API 키 발급 방법

1. https://platform.openai.com/ 접속
2. 로그인 후 우측 상단 프로필 클릭
3. "View API keys" 선택
4. "Create new secret key" 버튼 클릭
5. 생성된 키를 복사하여 `.env` 파일에 붙여넣기

**⚠️ 주의: API 키는 절대 공개 저장소에 커밋하지 마세요!**

## 3. 실행 방법

### 3-1. Streamlit 앱 실행 (추천)

```bash
streamlit run app.py
```

브라우저가 자동으로 열리며 챗봇 UI가 표시됩니다.  
주소: http://localhost:8501

### 3-2. 터미널에서 테스트 (선택)

```bash
python crew.py
```

## 4. 사용 예시

챗봇에 다음과 같이 질문해보세요:

```
오늘 저녁 메뉴 추천해줘
```

```
1만원 이하로 다이어트 식단 추천해줘
```

```
30분 안에 만들 수 있는 집밥 레시피 알려줘
```

## 5. 문제 해결

### Q1. `ModuleNotFoundError` 발생

**해결방법:**
```bash
pip install -r requirements.txt
```

### Q2. OpenAI API 키 오류

**해결방법:**
1. `.env` 파일이 프로젝트 루트에 있는지 확인
2. API 키가 정확한지 확인
3. OpenAI 계정에 크레딧이 있는지 확인

### Q3. MCP 서버 관련 오류

**해결방법:**
- 현재 버전은 MCP 서버를 직접 실행하지 않고 Mock 데이터를 사용합니다.
- `data/mock_notion.json`과 `data/mock_baemin.json` 파일이 있는지 확인하세요.

### Q4. Streamlit 실행 포트 변경

```bash
streamlit run app.py --server.port 8502
```

## 6. 프로젝트 구조

```
crewai-food-app/
├── agents/           # 6개 에이전트
├── tools/            # CrewAI 도구
├── mcp_servers/      # MCP 서버 (현재 미사용)
├── data/             # Mock 데이터
├── crew.py           # 오케스트레이션
├── app.py            # Streamlit UI
├── config.py         # 설정
└── requirements.txt  # 의존성
```

## 7. 추가 정보

### 비용 예상 (OpenAI GPT-4o-mini)

- 입력: $0.15 / 1M tokens
- 출력: $0.60 / 1M tokens
- 1회 추천당 약 10,000~20,000 tokens 사용
- **예상 비용: 1회당 약 $0.01~0.02 (약 10~20원)**

### 성능 최적화

- `config.py`에서 `temperature` 조정 가능 (현재 0.7)
- 낮을수록 일관된 답변, 높을수록 창의적 답변

### 데이터 커스터마이징

`data/mock_notion.json`과 `data/mock_baemin.json`을 수정하여 원하는 데이터로 변경 가능합니다.

## 8. 개발 모드

### 디버깅 로그 확인

`config.py`의 `CREW_CONFIG`에서 `verbose=True`로 설정되어 있으면 에이전트의 모든 작업 과정이 출력됩니다.

### 에이전트 가중치 조정

`config.py`의 `AGENT_WEIGHTS` 딕셔너리를 수정하여 에이전트 중요도를 변경할 수 있습니다.

## 9. 지원

문제가 있으시면 GitHub Issues에 올려주세요!

---

**즐거운 음식 추천되세요! 🍽️**

