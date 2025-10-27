# 🍽️ CrewAI 기반 개인화 음식 추천 챗봇

**5명의 페르소나**를 위한 개인화된 AI 음식 추천 서비스!  
6개의 AI 에이전트가 협업하여 각 사용자에게 최적의 메뉴를 추천합니다.

## ✨ 주요 특징

- 🎯 **5명의 페르소나**: 각자의 알레르기, 선호도, 예산, 일정 관리
- 🔗 **Notion MCP 연동**: 실시간 사용자 데이터 동기화
- 🤖 **동적 워크플로우**: 요청에 따라 필요한 에이전트만 자동 선택
- 💬 **대화형 UI**: Streamlit 기반 직관적인 채팅 인터페이스

## 👥 5명의 페르소나 (실제 Notion 데이터 기반)

### 🌙 소윤 - 야간근무자
- 갑각류 알레르기
- 15분 빠른 식사
- 분식 감성 유지
- 야간근무 (23:00-23:15 / 03:00-03:15)

### 👴 태식 - 시니어
- 당뇨·고혈압 관리
- 따뜻한 한식 선호
- 전자레인지만 사용
- 국밥·찌개류 (국물 적게)

### 🥗 지민 - 채식 중심 직장인
- 평일 락토오보, 주말 페스코
- 식이섬유 중시 (≥30g)
- 버섯 식감 기피, 생양파 싫어함
- 체중 유지 + 장건강

### 🏃 현우 - 헬스 다이어터
- 퇴근 후 헬스
- 유당불내증 (우유·치즈·크림 주의)
- 1,800kcal, 단백질 ≥120g
- 빠르고 가벼운 저녁

### 💪 라미 - 벌크업
- 고단백 고칼로리 (2,800kcal)
- 단백질 ≥140g
- 운동 전후 타이밍 중시
- 주 1회 밀프렙

## 🤖 AI 에이전트 구성

1. **🎛️ 오케스트레이터**: 사용자 의도 분석 및 워크플로우 설계
2. **👨‍🍳 요리사**: 집밥 레시피 생성 및 조리법 제공
3. **⭐ 맛슐랭**: 맛 평가 및 메뉴 추천
4. **🥗 영양사**: 건강 및 영양 관리 (알레르기 체크)
5. **💰 총무**: 예산 및 가성비 최적화
6. **⏰ 스케줄러**: 시간 관리 전문가
7. **🎯 코디네이터**: 종합 판단 및 최종 추천

## 🛠️ 기술 스택

- **CrewAI**: 멀티 에이전트 오케스트레이션
- **MCP (Model Context Protocol)**: 데이터 소스 연동
- **OpenAI GPT-4o-mini**: LLM 엔진
- **Streamlit**: 챗봇 UI

## 📦 설치 및 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 OPENAI_API_KEY 입력

# 앱 실행
streamlit run app.py
```

## 📁 프로젝트 구조

```
crewai-food-app/
├── mcp_servers/      # MCP 서버 (노션, 배민)
├── agents/           # 6개 에이전트
├── tools/            # CrewAI 도구
├── data/             # Mock 데이터
├── crew.py           # 오케스트레이션
├── app.py            # Streamlit UI
└── config.py         # 설정
```

## 🚀 시작하기

### 1. 앱 실행
```bash
streamlit run app.py
```

### 2. 사용자 선택
5명의 페르소나 중 한 명을 선택합니다.

### 3. 개인화된 추천 받기
선택한 사용자의 데이터(알레르기, 선호도, 예산 등)를 기반으로  
맞춤형 메뉴를 추천받습니다.

## 💡 사용 예시

### 🌙 소윤님의 경우
```
👤 "오늘 야근인데 빨리 먹을 수 있는 거 추천해줘"

🤖 "소윤님의 야간근무 시간(23:00-23:15)에 맞춰 
    갑각류가 없는 매콤한 떡볶이(7,000원)를 추천드립니다.
    5분 내 조리 가능하며 분식 감성에 딱 맞습니다!"
```

### 👴 태식님의 경우
```
👤 "저녁 메뉴 추천해줘"

🤖 "태식님의 당뇨·고혈압 관리를 위해 
    따뜻한 된장찌개(국물 적게)를 추천드립니다.
    전자레인지로 간편하게 데우실 수 있습니다!"
```

### 🏃 현우님의 경우
```
👤 "헬스 끝났어. 저칼로리 고단백 메뉴"

🤖 "현우님의 다이어트(1,800kcal, 단백질 120g)를 위해 
    닭가슴살 샐러드를 추천드립니다.
    유당불내증이 있으시니 크림 드레싱은 제외했습니다!"
```

## 📝 질문 예시

챗봇에 다음과 같이 질문하세요:

- "오늘 저녁 메뉴 추천해줘"
- "1만원 이하로 다이어트 식단 추천해줘"
- "30분 안에 만들 수 있는 집밥 레시피 알려줘"

## 📝 Mock 데이터

- **노션 MCP**: 사용자 식단 기록 및 선호도

## 🌐 Streamlit Cloud 배포

### 1. GitHub에 Push
```bash
# 모든 변경사항 추가
git add .

# 커밋
git commit -m "feat: 개인화 음식 추천 챗봇 완성"

# GitHub에 푸시
git push origin main
```

### 2. Streamlit Cloud 배포
1. [Streamlit Community Cloud](https://streamlit.io/cloud)에 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 선택: `crewai-food-app`
5. Main file path: `app.py`
6. 배포 클릭

### 3. 환경 변수 설정 (Secrets)
Streamlit Cloud 대시보드에서 **Settings > Secrets**에 다음 내용 추가:

```toml
OPENAI_API_KEY = "your-openai-api-key-here"
OPENAI_MODEL = "gpt-4o-mini"
CREWAI_TRACING_ENABLED = true

# Notion MCP 설정 (선택사항)
USE_NOTION_MCP = true
NOTION_API_KEY = "your-notion-api-key-here"
NOTION_DATABASE_ID = "your-notion-database-id-here"
```

⚠️ **중요**: API 키는 절대 GitHub에 직접 커밋하지 마세요! `.env` 파일은 `.gitignore`에 포함되어 있습니다.

### 4. 배포 완료
몇 분 후 앱이 배포되면 공유 가능한 URL이 생성됩니다!

