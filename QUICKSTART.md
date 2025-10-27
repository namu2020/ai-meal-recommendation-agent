# ⚡ 빠른 시작 가이드

## 5분 안에 실행하기! 🚀

### 1️⃣ 의존성 설치

```bash
cd crewai-food-app
pip install -r requirements.txt
```

### 2️⃣ OpenAI API 키 설정

프로젝트 폴더에 `.env` 파일 생성:

```bash
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini
```

> 💡 API 키는 https://platform.openai.com/ 에서 발급

### 3️⃣ 도구 테스트 (선택사항)

```bash
python test_tools.py
```

모든 도구가 정상 작동하는지 확인합니다.

### 4️⃣ 챗봇 실행

```bash
streamlit run app.py
```

브라우저가 자동으로 열립니다! (http://localhost:8501)

### 5️⃣ 질문하기

챗봇에 질문해보세요:

```
오늘 저녁 메뉴 추천해줘
```

---

## 🎯 주요 기능

### 6개 전문 에이전트

1. 👨‍🍳 **요리사** - 집밥 레시피
2. ⭐ **맛슐랭** - 맛 평가
3. 🥗 **영양사** - 건강 관리
4. 💰 **총무** - 예산 관리
5. ⏰ **스케줄러** - 시간 관리
6. 🎯 **코디네이터** - 최종 추천

### 추천 예시

- "1만원 이하 다이어트 식단"
- "30분 안에 만들 수 있는 집밥"
- "한식으로 저칼로리 메뉴"
- "가성비 좋은 점심 메뉴"

---

## ❓ 문제 해결

### ImportError 발생?
```bash
pip install -r requirements.txt
```

### OpenAI API 오류?
- `.env` 파일에 올바른 API 키 입력
- API 키 앞에 따옴표 없이 입력

### 포트 충돌?
```bash
streamlit run app.py --server.port 8502
```

---

## 📚 더 자세한 정보

- 설치 가이드: `SETUP.md`
- README: `README.md`

---

**즐거운 음식 추천 되세요! 🍽️**

