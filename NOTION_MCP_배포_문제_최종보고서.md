# 🔍 Notion MCP 배포 문제 최종 보고서

## 📊 **요약**

`USE_NOTION_MCP='true'`로 배포하셨다고 하셨는데, **Streamlit Cloud 환경에서는 MCP 모드가 작동하지 않을 가능성이 매우 높습니다**.

---

## 🚨 **핵심 문제 3가지**

### 1️⃣ **서브프로세스 실행 차단**

**문제**: MCP 서버는 별도의 Python 프로세스를 시작합니다.

```python
# mcp_client/notion_mcp_client.py (Line 44-46)
server_params = StdioServerParameters(
    command="python",  # ← 새 프로세스 시작!
    args=["-u", server_script],
    env=os.environ.copy()
)
```

**영향**:
- Streamlit Cloud의 샌드박스 환경에서 서브프로세스 실행이 제한됨
- "MCP 연결 오류" 또는 "Permission denied" 에러 발생 가능

---

### 2️⃣ **Notion API 키 필수**

**문제**: MCP 모드는 실제 Notion API를 호출합니다.

```python
# mcp_servers/notion_server_real.py (Line 22-24)
NOTION_API_KEY = os.getenv("NOTION_API_KEY")  # ← 필수!
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")  # ← 필수!
```

**필요 조치**:
```toml
# Streamlit Cloud Secrets 설정
USE_NOTION_MCP = "true"
NOTION_API_KEY = "ntn_..."
NOTION_DATABASE_ID = "2976b5ca-..."
```

---

### 3️⃣ **비동기 이벤트 루프 충돌**

**문제**: Streamlit과 MCP가 모두 비동기 루프를 사용합니다.

**해결**: `nest_asyncio` 패키지 사용 (이미 적용됨 ✅)

---

## ✅ **체크리스트: 현재 배포 상태 확인**

### 배포된 앱에서 확인할 것들:

#### 1. **앱이 정상 작동하는가?**
- [ ] 사용자 선택 화면이 뜨는가?
- [ ] 사용자를 선택하면 챗봇이 나타나는가?
- [ ] "오늘 저녁 메뉴 추천해줘" 입력 시 응답이 오는가?

#### 2. **Streamlit Cloud Logs 확인**
```
Dashboard → Your App → ⋮ Menu → Manage app → Logs
```

**찾아야 할 로그**:
- ✅ "🔗 Notion MCP 모드 활성화" (MCP 모드 시작)
- ✅ "[MCP Server] 🔍 Target User from ENV: ..." (MCP 서버 실행)
- ❌ "MCP 연결 오류" (연결 실패)
- ❌ "subprocess" 관련 에러 (프로세스 실행 차단)
- ❌ "Permission denied" (권한 거부)

#### 3. **에러 증상별 진단**

| 증상 | 원인 | 해결 방법 |
|------|------|----------|
| 앱이 시작되지 않음 | MCP 서버 실행 실패 | `USE_NOTION_MCP=false` |
| "MCP 연결 오류" | 서브프로세스 차단 | Mock 모드로 전환 |
| 응답이 매우 느림 | Notion API 호출 지연 | Mock 모드로 전환 |
| "NOTION_API_KEY not found" | Secrets 미설정 | Secrets에 키 추가 |

---

## 🎯 **즉시 해야 할 조치**

### **Option 1: Mock 모드로 전환 (권장! 99%)**

```toml
# Streamlit Cloud → Settings → Secrets
USE_NOTION_MCP = "false"  # ← 이렇게 수정
```

**장점**:
- ✅ 안정적 작동 보장
- ✅ 빠른 응답 속도
- ✅ 서브프로세스 문제 없음
- ✅ Notion API 불필요

**단점**:
- ⚠️ 고정된 Mock 데이터 사용 (실시간 업데이트 불가)

---

### **Option 2: MCP 모드 유지 (권장하지 않음!)**

**조건**:
- Streamlit Cloud Logs에 "MCP 서버" 로그가 정상적으로 보여야 함
- Notion API 호출이 성공해야 함
- 응답 속도가 너무 느리지 않아야 함

**설정**:
```toml
# Streamlit Cloud → Settings → Secrets
USE_NOTION_MCP = "true"
NOTION_API_KEY = "ntn_your_actual_key"
NOTION_DATABASE_ID = "your_actual_database_id"
```

**주의사항**:
- ⚠️ Logs를 꼼꼼히 모니터링
- ⚠️ 에러 발생 시 즉시 Mock 모드로 전환
- ⚠️ 사용자 경험 저하 가능 (느린 응답)

---

## 📋 **생성된 파일들**

### 1. `NOTION_MCP_DEPLOYMENT_CHECK.md`
- Notion MCP 배포 시 발생 가능한 모든 문제 상세 설명
- 문제별 해결 방법
- 체크리스트

### 2. `check_deployment_readiness.py`
- 배포 전 환경 확인 스크립트
- Mock/MCP 모드별 요구사항 체크

**실행 방법**:
```bash
python check_deployment_readiness.py
```

### 3. `DEPLOYMENT.md` (업데이트)
- Notion MCP 주의사항 추가
- "MCP 연결 오류" 해결 방법 추가

### 4. `QUICK_DEPLOY.md` (업데이트)
- Mock 모드 강조
- MCP 모드 주의사항 추가

---

## 🔧 **로컬 테스트 방법**

### Mock 모드 테스트:
```bash
# .env 설정
USE_NOTION_MCP=false

# 앱 실행
streamlit run app.py
```

### MCP 모드 테스트:
```bash
# .env 설정
USE_NOTION_MCP=true
NOTION_API_KEY=ntn_...
NOTION_DATABASE_ID=...

# MCP 테스트
python test_mcp_mode.py

# 정상 작동하면 앱 실행
streamlit run app.py
```

---

## 💡 **최종 권장사항**

### ✅ **배포 시 권장 설정**

```toml
# Streamlit Cloud Secrets (최종 권장)
OPENAI_API_KEY = "sk-your-actual-key"
OPENAI_MODEL = "gpt-4o-mini"
USE_NOTION_MCP = "false"  # ← Mock 모드 (안전!)
```

### 이유:
1. **안정성**: 100% 작동 보장
2. **속도**: 빠른 응답 시간
3. **간편함**: 추가 설정 불필요
4. **비용**: Notion API 호출 없음

---

## 📞 **문제 발생 시 조치 순서**

1. **Streamlit Cloud Logs 확인**
   - Dashboard → Your App → ⋮ → Manage app → Logs
   - "MCP", "Error", "subprocess" 키워드 검색

2. **Mock 모드로 즉시 전환**
   ```toml
   USE_NOTION_MCP = "false"
   ```
   - Settings → Secrets → 수정 → Save
   - 2-3분 후 자동 재배포

3. **정상 작동 확인**
   - 앱 URL 접속
   - 사용자 선택 및 챗봇 테스트

4. **여전히 문제 발생 시**
   - OPENAI_API_KEY 확인
   - requirements.txt 확인
   - GitHub 코드 동기화 확인

---

## 🎯 **결론**

### 현재 상황 분석:
- ✅ 코드에는 문제가 없습니다
- ⚠️ **배포 환경(Streamlit Cloud)이 MCP 모드를 지원하지 않을 가능성이 높습니다**
- ✅ Mock 모드로 전환하면 모든 문제가 해결됩니다

### 즉시 실행할 것:
1. 배포된 앱 접속하여 작동 여부 확인
2. Logs에서 "MCP 연결 오류" 확인
3. 에러 발생 시 `USE_NOTION_MCP=false`로 변경

### 장기적 권장사항:
- **배포 환경**: Mock 모드 사용 (`USE_NOTION_MCP=false`)
- **로컬 개발**: MCP 모드로 실제 Notion 데이터 테스트
- **데이터 업데이트**: `data/mock_notion.json` 수동 업데이트

---

**다음 질문이 있으시면 알려주세요!** 😊
- 배포된 앱의 Logs를 보여주시면 더 정확한 진단이 가능합니다
- 특정 에러 메시지가 있다면 공유해주세요

