# ✅ 프로젝트 완성!

## 🎉 CrewAI 기반 음식 추천 챗봇 구축 완료

---

## 📁 생성된 파일 목록

### 핵심 파일
- ✅ `app.py` - Streamlit 챗봇 UI
- ✅ `crew.py` - CrewAI 오케스트레이션
- ✅ `config.py` - 설정 파일

### 에이전트 (agents/)
- ✅ `chef_agent.py` - 요리사
- ✅ `taste_agent.py` - 맛슐랭
- ✅ `nutrition_agent.py` - 영양사
- ✅ `budget_agent.py` - 총무
- ✅ `scheduler_agent.py` - 스케줄러
- ✅ `coordinator_agent.py` - 종합판단

### 도구 (tools/)
- ✅ `notion_tools.py` - 노션 데이터 조회 (4개 도구)
- ✅ `baemin_tools.py` - 배민 메뉴 검색 (3개 도구)

### MCP 서버 (mcp_servers/)
- ✅ `notion_server.py` - 식단 기록 MCP 서버
- ✅ `baemin_server.py` - 메뉴 정보 MCP 서버

### Mock 데이터 (data/)
- ✅ `mock_notion.json` - 사용자 식단/선호도 데이터
- ✅ `mock_baemin.json` - 레스토랑/메뉴 데이터

### 문서
- ✅ `README.md` - 프로젝트 소개
- ✅ `SETUP.md` - 상세 설치 가이드
- ✅ `QUICKSTART.md` - 빠른 시작 가이드
- ✅ `ENV_SETUP.txt` - .env 파일 설정 가이드

### 기타
- ✅ `requirements.txt` - 의존성
- ✅ `test_tools.py` - 도구 테스트 스크립트
- ✅ `.gitignore` - Git 제외 파일

---

## 🚀 바로 실행하기

### 1단계: 패키지 설치
```bash
cd crewai-food-app
pip install -r requirements.txt
```

### 2단계: .env 파일 생성
프로젝트 루트에 `.env` 파일 생성 후 다음 내용 입력:
```
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### 3단계: 도구 테스트 (선택)
```bash
python test_tools.py
```

### 4단계: 챗봇 실행
```bash
streamlit run app.py
```

---

## 🤖 에이전트 구성

| 에이전트 | 역할 | 가중치 | 도구 |
|---------|------|--------|------|
| 👨‍🍳 요리사 | 집밥 레시피 추천 | 10% | 선호도, 레시피 검색 |
| ⭐ 맛슐랭 | 맛 평가 | 20% | 선호도, 메뉴 검색 |
| 🥗 영양사 | 건강/영양 관리 | 30% | 선호도, 식단기록, 메뉴검색 |
| 💰 총무 | 예산 최적화 | 25% | 예산현황, 가격필터 |
| ⏰ 스케줄러 | 시간 관리 | 15% | 일정, 메뉴검색, 레시피 |
| 🎯 코디네이터 | 최종 추천 | - | 없음 (통합만) |

---

## 💡 주요 기능

### 1. 멀티 에이전트 협업
- 6개 전문 에이전트가 순차적으로 작업
- 각 에이전트의 전문 분야 분석
- 가중치 기반 종합 판단

### 2. MCP 프로토콜 구현
- 노션 MCP 서버: 사용자 데이터
- 배민 MCP 서버: 메뉴 데이터
- Mock 데이터로 실제 API 시뮬레이션

### 3. CrewAI Tools
- 7개의 커스텀 도구
- JSON 기반 Mock 데이터 활용
- 간단한 함수 호출 인터페이스

### 4. Streamlit 챗봇 UI
- 대화형 인터페이스
- 실시간 진행 상황 표시
- 사이드바에 정보 및 설정

---

## 📊 시스템 아키텍처

```
사용자
  ↓
Streamlit UI (app.py)
  ↓
CrewAI Crew (crew.py)
  ↓
┌─────────────────────────────────┐
│ 6개 에이전트 (순차 실행)          │
│ 1. 영양사                        │
│ 2. 총무                          │
│ 3. 스케줄러                      │
│ 4. 요리사                        │
│ 5. 맛슐랭                        │
│ 6. 코디네이터                    │
└─────────────────────────────────┘
  ↓
CrewAI Tools (tools/)
  ↓
Mock Data (data/)
```

---

## 🎯 사용 예시

### 예시 1: 기본 추천
```
사용자: 오늘 저녁 메뉴 추천해줘
```

### 예시 2: 조건부 추천
```
사용자: 1만원 이하로 다이어트 식단 추천해줘
```

### 예시 3: 시간 제약
```
사용자: 30분 안에 만들 수 있는 집밥 알려줘
```

### 예시 4: 카테고리 지정
```
사용자: 한식으로 저칼로리 메뉴 추천해줘
```

---

## 🔧 커스터마이징

### 에이전트 가중치 변경
`config.py`의 `AGENT_WEIGHTS` 수정:
```python
AGENT_WEIGHTS = {
    "nutrition": 0.30,  # 영양사
    "budget": 0.25,     # 총무
    "taste": 0.20,      # 맛슐랭
    "scheduler": 0.15,  # 스케줄러
    "chef": 0.10,       # 요리사
}
```

### Mock 데이터 수정
- `data/mock_notion.json` - 사용자 정보
- `data/mock_baemin.json` - 메뉴 정보

### LLM 모델 변경
`config.py`에서 모델 변경:
```python
OPENAI_MODEL = "gpt-4o"  # 더 강력한 모델
```

---

## 💰 비용 예상

### OpenAI GPT-4o-mini
- 입력: $0.15 / 1M tokens
- 출력: $0.60 / 1M tokens
- **1회 추천: 약 $0.01~0.02 (10~20원)**

### 100회 추천 시
- 약 $1~2 (1,000~2,000원)

---

## 🐛 문제 해결

### Q: ModuleNotFoundError
```bash
pip install -r requirements.txt
```

### Q: OpenAI API 키 오류
1. `.env` 파일 확인
2. API 키 정확성 확인
3. 크레딧 잔액 확인

### Q: Streamlit 오류
```bash
pip install --upgrade streamlit
```

### Q: 도구 작동 안 함
```bash
python test_tools.py
```

---

## 📈 확장 가능성

### Phase 2 (실제 API 연동)
- [ ] 실제 노션 API 연동
- [ ] 배달의민족 API 연동 (공식 API 없음, 크롤링)
- [ ] Google Calendar 연동

### Phase 3 (기능 추가)
- [ ] 사용자별 히스토리 저장
- [ ] 추천 피드백 학습
- [ ] 음성 입력/출력
- [ ] 이미지 생성 (음식 사진)

### Phase 4 (배포)
- [ ] Docker 컨테이너화
- [ ] AWS/GCP 배포
- [ ] 다중 사용자 지원
- [ ] 데이터베이스 연동

---

## 🎓 학습 포인트

이 프로젝트에서 배운 것:

1. **CrewAI 프레임워크**
   - Agent, Task, Crew 개념
   - 멀티 에이전트 오케스트레이션
   - Process.sequential 워크플로우

2. **MCP (Model Context Protocol)**
   - Resources, Tools, Prompts 구조
   - Stdio 서버 구현
   - Mock 데이터 활용

3. **LLM 에이전트 설계**
   - Role, Goal, Backstory 정의
   - 도구 선택 및 활용
   - Context 전달 및 통합

4. **Streamlit UI**
   - 챗봇 인터페이스 구현
   - 세션 상태 관리
   - 실시간 피드백

---

## 🙏 다음 단계

1. **테스트**: `python test_tools.py` 실행
2. **실행**: `streamlit run app.py` 실행
3. **질문**: 챗봇에 다양한 질문 시도
4. **커스터마이징**: 데이터나 가중치 수정
5. **확장**: 새로운 에이전트나 도구 추가

---

## 📞 지원

문제가 있으시면:
1. `SETUP.md` 참고
2. `test_tools.py`로 디버깅
3. GitHub Issues에 문의

---

**🎉 축하합니다! 프로젝트가 완성되었습니다!**

**이제 `streamlit run app.py`를 실행하여 챗봇을 즐겨보세요! 🍽️**

---

*Created with ❤️ by AI Assistant*
*Powered by CrewAI, OpenAI, and Streamlit*

