# 🚀 무료 웹 배포 가이드 (한국 최적화)

## ✅ 추천 방법: Streamlit Community Cloud

**완전 무료**, 설정 간단, 한국에서 원활하게 작동합니다!

---

## 📋 배포 전 체크리스트

### 1️⃣ GitHub 저장소 준비

```bash
# 현재 상태 확인
git status

# 변경사항 커밋 (필요시)
git add .
git commit -m "Add deployment configuration"
git push origin main
```

### 2️⃣ 필요한 API 키 준비
- ✅ **OpenAI API Key** (필수)
- ⚠️ **Notion API Key** (Notion 연동 사용 시)

---

## 🌐 Streamlit Community Cloud 배포 방법

### Step 1: Streamlit Community Cloud 접속
1. [https://streamlit.io/cloud](https://streamlit.io/cloud) 접속
2. GitHub 계정으로 로그인

### Step 2: 새 앱 배포
1. **"New app"** 버튼 클릭
2. 다음 정보 입력:
   - **Repository**: `your-username/crewai-food-app`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL** (선택): 원하는 URL 입력

### Step 3: 환경 변수 설정 (중요!)
**"Advanced settings"** 클릭 후 **Secrets** 섹션에 다음 입력:

```toml
# Secrets 설정 (TOML 형식)
OPENAI_API_KEY = "sk-your-actual-openai-api-key"
OPENAI_MODEL = "gpt-4o-mini"

# ⚠️ Streamlit Cloud 배포 시에는 Mock 모드 권장!
USE_NOTION_MCP = "false"

# Notion MCP 사용 시 (권장하지 않음! 서브프로세스 문제)
# USE_NOTION_MCP = "true"
# NOTION_API_KEY = "your-notion-api-key"
# NOTION_DATABASE_ID = "your-database-id"
```

> **⚠️ 중요**: Streamlit Cloud는 서브프로세스 실행을 제한하므로, Notion MCP 모드(`USE_NOTION_MCP=true`)는 작동하지 않을 수 있습니다. **Mock 모드(`false`)를 권장합니다!**

### Step 4: 배포!
- **"Deploy!"** 버튼 클릭
- 2-5분 정도 기다리면 배포 완료 ✅

### Step 5: 앱 접속
- 배포 완료 후 제공되는 URL로 접속
- 예: `https://your-app-name.streamlit.app`

---

## 🔧 배포 후 문제 해결

### ❌ 에러: "ModuleNotFoundError"
**해결책**: `requirements.txt` 확인
```bash
# 로컬에서 테스트
pip install -r requirements.txt
python -m streamlit run app.py
```

### ❌ 에러: "OpenAI API Error"
**해결책**: Secrets에 API 키가 올바르게 설정되었는지 확인
- Streamlit Cloud Dashboard → Your App → Settings → Secrets

### ❌ 에러: "MCP 연결 오류" 또는 "subprocess error"
**원인**: Streamlit Cloud에서 MCP 서버 서브프로세스 실행 차단됨
**해결책**:
```toml
# Secrets에서 수정
USE_NOTION_MCP = "false"  # Mock 모드로 전환
```
- Save 후 앱 자동 재배포 (2-3분 소요)

### ❌ 앱이 느리게 작동
**원인**: 무료 티어 제한 (메모리 1GB, CPU 공유) 또는 MCP 모드 사용
**해결책**:
1. `USE_NOTION_MCP=false` (Mock 모드가 더 빠름)
2. 불필요한 import 제거
3. 캐싱 활용 (`@st.cache_data` 데코레이터)
4. 필요 시 유료 플랜 고려

### 🔄 앱 업데이트 방법
```bash
# 코드 수정 후
git add .
git commit -m "Update app"
git push origin main
```
- GitHub에 push하면 **자동으로 재배포됩니다!**

---

## 🌏 다른 무료 배포 옵션

### Option 2: Hugging Face Spaces
- **장점**: 무료, ML 모델 친화적
- **단점**: 초기 설정이 조금 복잡
- **링크**: [https://huggingface.co/spaces](https://huggingface.co/spaces)

**배포 방법**:
1. Hugging Face 계정 생성
2. New Space 생성
3. Space SDK: **Streamlit** 선택
4. Git으로 코드 업로드
5. Settings에서 환경 변수 설정

### Option 3: Render
- **장점**: 무료 티어 제공, 안정적
- **단점**: 콜드 스타트 시간 (무료 플랜)
- **링크**: [https://render.com](https://render.com)

**배포 방법**:
1. Render 계정 생성
2. New → Web Service
3. GitHub 저장소 연결
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `streamlit run app.py --server.port $PORT`
6. Environment Variables에 API 키 추가

---

## 💡 한국에서 최적화 팁

### 1. 응답 속도 개선
```python
# config.py에서 온도 낮추기 (더 빠른 응답)
OPENAI_MODEL = "gpt-4o-mini"  # gpt-4보다 빠르고 저렴
temperature = 0.5  # 낮은 온도 = 빠른 응답
```

### 2. 비용 절감
- **gpt-4o-mini** 사용 (현재 설정 ✅)
- 불필요한 API 호출 최소화
- 캐싱 활용

### 3. 사용자 경험 개선
```python
# app.py에 로딩 메시지 추가
with st.spinner("🤖 AI가 생각하고 있어요..."):
    result = crew.run(user_input)
```

---

## 📊 배포 비용 비교

| 서비스 | 무료 플랜 | 제한사항 | 한국 속도 |
|--------|-----------|----------|-----------|
| **Streamlit Cloud** | ✅ 무제한 | 1GB RAM, 공유 CPU | ⚡ 빠름 |
| **Hugging Face** | ✅ 무제한 | 2 CPU, 16GB RAM | ⚡ 빠름 |
| **Render** | ✅ 750시간/월 | 콜드 스타트 | 🐢 보통 |
| **Railway** | ⚠️ $5 크레딧 | 사용량 기반 | ⚡ 빠름 |

---

## ✅ 추천 순서

1. **🥇 Streamlit Community Cloud** ← 가장 추천!
   - 무료, 간단, 빠름
   
2. **🥈 Hugging Face Spaces**
   - 무료, 안정적
   
3. **🥉 Render**
   - 무료 티어 제한적

---

## 🆘 도움이 필요하신가요?

### Streamlit Cloud 공식 문서
- [배포 가이드](https://docs.streamlit.io/streamlit-community-cloud/get-started)
- [Secrets 관리](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

### 자주 묻는 질문

**Q: API 키가 노출되지 않나요?**
A: Secrets에 저장하면 안전합니다. GitHub에는 업로드되지 않습니다.

**Q: 몇 명이 동시에 사용할 수 있나요?**
A: Streamlit Cloud 무료 플랜은 수백 명의 동시 사용자를 지원합니다.

**Q: 도메인을 연결할 수 있나요?**
A: 유료 플랜에서 가능합니다. 무료 플랜은 `.streamlit.app` 도메인만 사용 가능합니다.

**Q: 한국 서버로 배포할 수 있나요?**
A: Streamlit Cloud는 글로벌 CDN을 사용하여 한국에서도 빠릅니다. 별도 한국 서버는 AWS/GCP 등 유료 서비스 필요합니다.

---

## 🎉 배포 완료 후 확인사항

- [ ] 앱이 정상적으로 로드되는가?
- [ ] 사용자 선택이 가능한가?
- [ ] AI 응답이 정상적으로 생성되는가?
- [ ] 환경 변수가 제대로 작동하는가?
- [ ] 에러 로그 확인

---

**행운을 빕니다! 🚀**

