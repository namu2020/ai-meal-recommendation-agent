# ⚡ 5분 빠른 배포 가이드

## 🎯 Streamlit Cloud로 5분 안에 배포하기!

### 1단계: GitHub 준비 (1분)
```bash
# 현재 상태 저장
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2단계: Streamlit Cloud 접속 (1분)
1. 🌐 [https://streamlit.io/cloud](https://streamlit.io/cloud) 접속
2. 🔐 GitHub으로 로그인

### 3단계: 앱 배포 (2분)
1. **"New app"** 클릭
2. 저장소 정보 입력:
   ```
   Repository: your-github-username/crewai-food-app
   Branch: main
   Main file: app.py
   ```
3. **"Advanced settings"** 클릭

### 4단계: API 키 설정 (1분)
**Secrets** 섹션에 복붙:
```toml
OPENAI_API_KEY = "여기에_실제_OpenAI_API_키_입력"
OPENAI_MODEL = "gpt-4o-mini"
USE_NOTION_MCP = "false"  # ← 반드시 false! (Mock 모드)
```

> ⚠️ **주의**: `USE_NOTION_MCP`는 반드시 `"false"`로 설정하세요! Streamlit Cloud에서는 MCP 모드가 작동하지 않습니다.

### 5단계: 배포!
- **"Deploy!"** 버튼 클릭
- ☕ 2-3분 대기
- ✅ 완료!

---

## 🔑 API 키는 어디서?

### OpenAI API 키 발급
1. [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys) 접속
2. "Create new secret key" 클릭
3. 키 복사 (다시 볼 수 없으니 저장!)

💰 **비용**: gpt-4o-mini는 매우 저렴합니다 (1000번 질문해도 $1 미만)

---

## ✅ 배포 완료 확인

앱 URL은 이런 형식입니다:
```
https://your-app-name.streamlit.app
```

### 작동 테스트
1. 사용자 선택 화면이 뜨나요? ✅
2. 사용자를 선택하면 챗봇이 뜨나요? ✅
3. "오늘 저녁 메뉴 추천해줘" 라고 물어보세요 ✅
4. AI가 답변하나요? ✅

---

## 🔧 문제 해결

### 에러: "OPENAI_API_KEY not found"
➡️ Secrets 설정을 다시 확인하세요
   - Streamlit Cloud → Your App → Settings → Secrets

### 에러: "MCP 연결 오류" 또는 앱이 멈춤
➡️ Secrets에서 `USE_NOTION_MCP = "false"`로 설정했는지 확인
   - Settings → Secrets → 수정 → Save
   - 2-3분 후 자동 재배포

### 에러: "Module not found"
➡️ GitHub에 `requirements.txt` 파일이 있는지 확인

### 앱이 시작되지 않음
➡️ Logs 확인
   - Streamlit Cloud → Your App → Manage app → Logs

---

## 📱 배포 후 링크 공유

배포 완료 후:
1. 앱 URL 복사
2. 친구들에게 공유!
3. 모바일에서도 작동합니다 📱

---

## 🎁 보너스 팁

### 앱 이름 변경
- Settings → General → App name

### 자동 재배포
```bash
# 코드 수정 후
git push origin main
# 자동으로 재배포됩니다!
```

### 앱 중지/재시작
- Streamlit Cloud Dashboard → ⋮ 메뉴 → Reboot

---

**이게 전부입니다! 5분이면 충분합니다! 🚀**

더 자세한 내용은 `DEPLOYMENT.md`를 참고하세요.

