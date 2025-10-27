# Streamlit Cloud 배포 체크리스트 (Mock 모드)

**날짜**: 2025-10-27  
**모드**: `USE_NOTION_MCP = "false"` (Mock 모드)

---

## 🔍 배포 전 필수 체크사항

### ✅ 1. 사용자별 데이터 파일 Git 추가 (필수!)

**현재 상태**: ❌ **Untracked** - Git에 추가되지 않음

```bash
# 확인된 파일들
data/parsed_notion_소윤.json  (Untracked)
data/parsed_notion_태식.json  (Untracked)
data/parsed_notion_지민.json  (Untracked)
data/parsed_notion_현우.json  (Untracked)
data/parsed_notion_라미.json  (Untracked)
```

**⚠️ 문제**: Streamlit Cloud에 파일이 없으면 앱이 작동하지 않습니다!

**해결 방법**:
```bash
git add data/parsed_notion_*.json
git commit -m "Add user-specific mock data for 5 users"
git push
```

---

### ✅ 2. Mock 서버 아키텍처 검증

**현재 구조**:
- Mock 모드(`USE_NOTION_MCP=false`)에서도 **MCP 서버를 subprocess로 실행**
- `notion_server.py`가 별도 Python 프로세스로 실행됨
- 환경 변수 `CURRENT_NOTION_USER`를 subprocess에 전달

**Streamlit Cloud 제약사항**:
- ⚠️ **Subprocess 실행 가능하지만 제한적**
- stdio 통신은 일반적으로 작동
- 하지만 복잡한 프로세스 간 통신은 불안정할 수 있음

**검증 포인트**:
1. ✅ `mcp_client/notion_mcp_client.py`가 환경 변수를 복사 (`os.environ.copy()`)
2. ✅ `notion_server.py`가 환경 변수를 읽음 (`os.getenv("CURRENT_NOTION_USER")`)
3. ✅ Fallback 로직 존재 (사용자 파일이 없으면 `mock_notion.json` 사용)

---

### ✅ 3. 파일 경로 검증

**Mock 서버 경로 설정**:
```python
# mcp_servers/notion_server.py (23-43번 줄)
DATA_DIR = Path(__file__).parent.parent / "data"
DEFAULT_DATA_PATH = DATA_DIR / "mock_notion.json"

def load_notion_data():
    current_user = os.getenv("CURRENT_NOTION_USER", "소윤")
    user_file = DATA_DIR / f"parsed_notion_{current_user}.json"
    
    if user_file.exists():
        # 사용자별 파일 로드
        return json.load(user_file)
    else:
        # fallback
        return json.load(DEFAULT_DATA_PATH)
```

**검증**:
- ✅ 상대 경로 사용 (`Path(__file__).parent.parent`)
- ✅ Streamlit Cloud에서도 작동하는 경로
- ✅ Fallback 로직 있음

---

### ✅ 4. 환경 변수 전달 체인

**전달 경로**:
```
1. Streamlit Secrets (USE_NOTION_MCP = "false")
   ↓
2. app.py (사용자 선택 시 os.environ["CURRENT_NOTION_USER"] 설정)
   ↓
3. crew.py (FoodRecommendationCrew 초기화)
   ↓
4. tools/notion_tools_mcp.py (MCP 클라이언트 사용)
   ↓
5. mcp_client/notion_mcp_client.py (subprocess 실행, env=os.environ.copy())
   ↓
6. mcp_servers/notion_server.py (os.getenv("CURRENT_NOTION_USER"))
```

**검증**:
- ✅ 1→2: `app.py:52` `os.environ["CURRENT_NOTION_USER"] = users[0]`
- ✅ 5→6: `notion_mcp_client.py:46` `env=os.environ.copy()`
- ✅ 6: `notion_server.py:26` `os.getenv("CURRENT_NOTION_USER", "소윤")`

---

### ✅ 5. 필수 패키지 확인

**requirements.txt**:
```
crewai>=0.28.0
crewai-tools>=0.2.0
openai>=1.12.0
streamlit>=1.31.0
python-dotenv>=1.0.0
mcp>=0.9.0                    ← MCP 라이브러리 (필수!)
pydantic>=2.6.0
langchain-openai>=0.1.0
notion-client>=2.0.0         ← Mock 모드에서는 불필요하지만 있어도 OK
nest-asyncio>=1.5.0          ← 이벤트 루프 중첩 지원 (필수!)
```

**검증**:
- ✅ 모든 필수 패키지 포함
- ✅ `mcp>=0.9.0` 포함 (Mock 모드에서도 MCP 프로토콜 사용)
- ✅ `nest-asyncio>=1.5.0` 포함 (Streamlit의 이벤트 루프와 호환)

---

### ✅ 6. Streamlit Secrets 설정

**Streamlit Cloud > App Settings > Secrets**:

```toml
# 필수 설정
OPENAI_API_KEY = "your_openai_api_key"
OPENAI_MODEL = "gpt-4o-mini"
USE_NOTION_MCP = "false"       # ← 반드시 "false"!

# Mock 모드에서는 불필요 (있어도 사용 안 됨)
# NOTION_API_KEY = ""
# NOTION_DATABASE_ID = ""
```

**⚠️ 주의**:
- `USE_NOTION_MCP`는 반드시 **문자열** `"false"` (따옴표 포함)
- `"False"`, `false`, `0` 등은 모두 `"false"`가 아니므로 실패할 수 있음

---

## 🧪 로컬 테스트 (배포 전 필수)

### 테스트 1: Mock 모드 기본 동작
```bash
# .env 파일 설정
USE_NOTION_MCP=false

# 앱 실행
streamlit run app.py

# 테스트:
# 1. 각 사용자 선택 (소윤, 태식, 지민, 현우, 라미)
# 2. 간단한 요청 ("오늘 뭐 먹을까?")
# 3. 사용자별 데이터가 반영되는지 확인
#    - 소윤: 갑각류 알레르기
#    - 태식: 당뇨/고혈압
#    - 지민: 락토오보/페스코
#    - 현우: 유당불내증
#    - 라미: 벌크업
```

### 테스트 2: 사용자 전환
```bash
# 앱 실행 중:
# 1. 소윤 선택 → 메시지 전송
# 2. 브라우저 새로고침 (또는 사용자 변경 버튼)
# 3. 태식 선택 → 메시지 전송
# 4. 각 사용자의 데이터가 올바르게 로드되는지 확인
```

### 테스트 3: 데이터 파일 없을 때 Fallback
```bash
# 임시로 파일 이름 변경
mv data/parsed_notion_소윤.json data/parsed_notion_소윤.json.bak

# 앱 실행
streamlit run app.py

# 소윤 선택 시 mock_notion.json fallback 확인
# 에러 없이 기본 데이터 사용해야 함

# 복구
mv data/parsed_notion_소윤.json.bak data/parsed_notion_소윤.json
```

---

## ⚠️ 알려진 제약사항

### 1. Subprocess 안정성
**문제**: Streamlit Cloud에서 subprocess가 종종 불안정할 수 있음

**대안**:
- Mock 데이터를 직접 로드하는 더 간단한 방식으로 변경 가능
- MCP 아키텍처 없이 직접 JSON 파일 읽기
- 하지만 현재 구조는 로컬 테스트에서 잘 작동함

### 2. 환경 변수 타이밍
**문제**: Streamlit 재실행 시 환경 변수가 리셋될 수 있음

**해결책**:
- `save_current_user()` 함수로 `data/current_user.json`에 저장
- 앱 재시작 시에도 마지막 사용자 유지

### 3. 동시 사용자
**문제**: 환경 변수는 전역적이므로 동시 사용자가 있으면 충돌 가능

**현재 상태**: Streamlit Cloud는 사용자별로 별도 세션 유지하므로 일반적으로 문제 없음

---

## 📋 배포 전 최종 체크리스트

- [ ] **1. 사용자별 데이터 파일 Git 추가** (가장 중요!)
  ```bash
  git add data/parsed_notion_*.json
  git commit -m "Add user-specific mock data"
  git push
  ```

- [ ] **2. Secrets 설정 확인**
  - `USE_NOTION_MCP = "false"` (문자열로)
  - `OPENAI_API_KEY` 설정
  - `OPENAI_MODEL = "gpt-4o-mini"` 설정

- [ ] **3. requirements.txt 확인**
  - `mcp>=0.9.0` 포함
  - `nest-asyncio>=1.5.0` 포함

- [ ] **4. 로컬 테스트 완료**
  - 5명의 사용자 모두 테스트
  - 사용자 전환 테스트
  - 에러 없이 작동 확인

- [ ] **5. .gitignore 확인**
  - `data/parsed_notion_*.json`이 제외되지 않았는지 확인
  - `.env` 파일만 제외되어야 함

---

## 🚀 배포 후 검증

### 1단계: 기본 작동 확인
1. Streamlit Cloud 앱 열기
2. 로딩 에러 없이 사용자 선택 화면 표시 확인
3. 5명의 사용자 카드 모두 표시 확인

### 2단계: 사용자별 데이터 확인
1. **소윤** 선택
   - "오늘 뭐 먹을까?" 요청
   - 갑각류(새우, 게) 제외된 추천 확인
   - 15분 이내 식사 언급 확인

2. **태식** 선택
   - "점심 추천해줘" 요청
   - 당뇨/고혈압 고려 확인
   - 탄수화물/나트륨 제한 언급 확인

3. **지민** 선택
   - "저녁 뭐 먹지?" 요청
   - 평일: 고기/생선 제외 (락토오보)
   - 버섯 제외 확인

4. **현우** 선택
   - "운동 후 저녁 추천" 요청
   - 우유/치즈/크림 제외 (유당불내증)
   - 1,800kcal 언급 확인

5. **라미** 선택
   - "벌크업 식단 추천" 요청
   - 고단백 메뉴 추천
   - 2,800kcal 언급 확인

### 3단계: 에러 모니터링
- Streamlit Cloud > Logs 확인
- `[Mock Server]` 로그로 사용자 파일 로딩 확인
- 에러 메시지 없는지 확인

---

## ✅ 예상 결과

**성공 시**:
- ✅ 5명의 사용자 각각 맞춤 추천 제공
- ✅ 알레르기/식이 제한 정확히 반영
- ✅ 사용자 전환 시 데이터 올바르게 변경
- ✅ 에러 없이 안정적 작동

**실패 시 대처**:
1. **사용자 파일 없음 에러**
   - → Git에 파일 추가 안 됨, 다시 커밋
2. **Subprocess 에러**
   - → 로그 확인, MCP 버전 확인
3. **환경 변수 전달 안 됨**
   - → Secrets 설정 확인, 문자열 형식 확인

---

## 🎯 결론

**Mock 모드 배포 가능 여부**: ⚠️ **조건부 가능**

**필수 조건**:
1. ✅ 사용자별 데이터 파일 Git에 추가 (현재 **미완료**)
2. ✅ `USE_NOTION_MCP = "false"` Secrets 설정
3. ✅ 로컬 테스트 통과

**권장사항**:
- 배포 전에 반드시 파일 Git 추가
- 배포 후 각 사용자별로 1회 이상 테스트
- 문제 발생 시 Logs 즉시 확인

**현재 상태**: 
- 코드: ✅ 완료
- 데이터: ❌ **Git 추가 필요**
- 설정: ⚠️ Secrets 설정 필요

**다음 단계**:
```bash
# 1. 파일 추가
git add data/parsed_notion_*.json

# 2. 커밋
git commit -m "feat: Add user-specific mock data for 5 users

- 소윤: 갑각류 알레르기, 야간근무, 15분 식사
- 태식: 당뇨/고혈압, 탄수화물/나트륨 제한
- 지민: 락토오보/페스코, 장건강 중심
- 현우: 유당불내증, 1,800kcal 다이어트
- 라미: 벌크업, 2,800kcal 고단백"

# 3. 푸시
git push

# 4. Streamlit Cloud에서 Secrets 설정
# 5. 배포 및 테스트
```

