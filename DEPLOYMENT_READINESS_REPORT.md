# 🚀 Streamlit Cloud 배포 준비 상태 보고서

**날짜**: 2025-10-27  
**모드**: Mock 모드 (`USE_NOTION_MCP = "false"`)  
**상태**: ⚠️ **거의 준비됨 - 1개 작업 필요**

---

## 📊 전체 요약

| 항목 | 상태 | 비고 |
|------|------|------|
| Notion API 연결 | ✅ 검증 완료 | 실시간 데이터 접근 가능 |
| 5명 사용자 데이터 파싱 | ✅ 완료 | 각 파일 생성됨 |
| Mock 서버 사용자별 지원 | ✅ 구현 완료 | 환경 변수로 제어 |
| 로컬 테스트 | ✅ 통과 | Mock/실시간 모두 OK |
| **Git 추가** | ❌ **미완료** | 파일 커밋 필요! |
| Secrets 설정 | ⚠️ 설정 필요 | 배포 시 |

---

## ❌ 해결 필요: 사용자 데이터 파일 Git 추가

### 현재 문제

**5개의 사용자별 데이터 파일이 Git에 추가되지 않았습니다:**

```bash
Untracked files:
  data/parsed_notion_소윤.json  ← 필요!
  data/parsed_notion_태식.json  ← 필요!
  data/parsed_notion_지민.json  ← 필요!
  data/parsed_notion_현우.json  ← 필요!
  data/parsed_notion_라미.json  ← 필요!
```

### 왜 문제인가?

Streamlit Cloud는 **Git 리포지토리의 파일만** 배포합니다.
- Git에 없는 파일 = Streamlit Cloud에 없음
- 사용자 선택 시 파일을 찾지 못함
- 앱이 에러를 발생시키거나 fallback(`mock_notion.json`)만 사용

### 해결 방법

```bash
# 프로젝트 디렉토리에서 실행
cd "/Users/namu123/Documents/테크 관련/공훈의_AI특강/팀플/crewai-food-app"

# 1. 파일 추가
git add data/parsed_notion_소윤.json
git add data/parsed_notion_태식.json
git add data/parsed_notion_지민.json
git add data/parsed_notion_현우.json
git add data/parsed_notion_라미.json

# 또는 한번에:
git add data/parsed_notion_*.json

# 2. 커밋
git commit -m "feat: Add user-specific mock data for all 5 users

- 소윤: 갑각류 알레르기, 야간근무 15분 식사
- 태식: 당뇨/고혈압, 탄수화물/나트륨 제한
- 지민: 락토오보/페스코, 장건강, 버섯 기피
- 현우: 유당불내증, 1,800kcal 다이어트
- 라미: 벌크업, 2,800kcal 고단백

Each user has realistic data parsed from actual Notion pages."

# 3. 푸시
git push origin main
```

---

## ✅ 이미 완료된 사항

### 1. 코드 구현 완료 ✅

**수정된 파일**:
- ✅ `parse_notion_data.py` - 전체 사용자 파싱 모드
- ✅ `mcp_servers/notion_server.py` - 사용자별 파일 로드
- ✅ `app.py` - 사용자 선택 시 환경 변수 설정

### 2. 데이터 생성 완료 ✅

**생성된 파일** (각 사용자의 실제 Notion 데이터):
```
data/parsed_notion_소윤.json  (594B)  - 갑각류 알레르기, 15분 식사
data/parsed_notion_태식.json  (548B)  - 당뇨/고혈압, 탄수/나트륨 제한
data/parsed_notion_지민.json  (632B)  - 락토오보/페스코, 장건강
data/parsed_notion_현우.json  (645B)  - 유당불내증, 1,800kcal
data/parsed_notion_라미.json  (604B)  - 벌크업, 2,800kcal
```

### 3. 검증 테스트 완료 ✅

**Mock 모드 테스트**:
- ✅ 소윤: 갑각류 알레르기 로드 확인
- ✅ 태식: 당뇨/고혈압 데이터 로드 확인
- ✅ 지민: 버섯 기피, 장건강 목표 확인
- ✅ 현우: 유당불내증, 1,800kcal 확인
- ✅ 라미: 2,800kcal 벌크업 확인

**실시간 Notion API 모드 테스트**:
- ✅ 3명 테스트 통과 (소윤, 태식, 지민)
- ✅ 실제 Notion에서 데이터 가져오기 성공
- ✅ health_conditions, dietary_restrictions 등 상세 데이터 파싱 확인

### 4. 환경 변수 전달 체인 검증 ✅

```
Streamlit Secrets
  ↓ (USE_NOTION_MCP = "false")
app.py (os.environ["CURRENT_NOTION_USER"] 설정)
  ↓
MCP Client (env=os.environ.copy())
  ↓
Mock Server (os.getenv("CURRENT_NOTION_USER"))
  ↓
사용자별 파일 로드 (parsed_notion_{user}.json)
```

### 5. Fallback 로직 구현 ✅

사용자별 파일이 없을 경우 `mock_notion.json`으로 자동 fallback:
```python
if user_file.exists():
    return json.load(user_file)
else:
    return json.load(DEFAULT_DATA_PATH)  # fallback
```

---

## 📋 Streamlit Cloud 설정 가이드

### Secrets 설정 (App Settings > Secrets)

```toml
# 필수 설정
OPENAI_API_KEY = "sk-proj-..."
OPENAI_MODEL = "gpt-4o-mini"
USE_NOTION_MCP = "false"

# Mock 모드에서는 불필요 (설정 안 해도 됨)
# NOTION_API_KEY = ""
# NOTION_DATABASE_ID = ""
```

**⚠️ 중요**:
- `USE_NOTION_MCP`는 **문자열** `"false"` (따옴표 포함)
- Boolean `false`나 숫자 `0`이 아님!

### Python 버전

권장: **Python 3.11**
- Streamlit Cloud 설정에서 선택 가능
- CrewAI와 최고 호환성

---

## 🧪 배포 후 테스트 시나리오

### 시나리오 1: 소윤 (갑각류 알레르기)
1. 소윤 선택
2. "오늘 저녁 뭐 먹을까?" 요청
3. **기대 결과**:
   - ✅ 새우, 게, 랍스터 등 갑각류 제외
   - ✅ 15분 이내 빠른 식사 언급
   - ✅ 야간근무 시간(23:00경) 고려

### 시나리오 2: 태식 (당뇨/고혈압)
1. 태식 선택
2. "점심 추천해줘" 요청
3. **기대 결과**:
   - ✅ 탄수화물 150g 이하 언급
   - ✅ 나트륨 2000mg 미만 언급
   - ✅ 따뜻한 한식 추천
   - ✅ 가당음료 제외

### 시나리오 3: 지민 (락토오보/페스코)
1. 지민 선택
2. "오늘은 월요일인데 뭐 먹지?" 요청
3. **기대 결과**:
   - ✅ 평일이므로 고기/생선 제외 (락토오보)
   - ✅ 유제품/계란은 포함 가능
   - ✅ 버섯 제외
   - ✅ 식이섬유 30g 이상 언급

### 시나리오 4: 현우 (다이어터)
1. 현우 선택
2. "운동 후 저녁 추천" 요청
3. **기대 결과**:
   - ✅ 우유/치즈/크림 제외 (유당불내증)
   - ✅ 1,800kcal 목표 언급
   - ✅ 단백질 120g 이상 언급
   - ✅ 20:00-20:30 식사 시간 고려

### 시나리오 5: 라미 (벌크업)
1. 라미 선택
2. "벌크업 식단 추천해줘" 요청
3. **기대 결과**:
   - ✅ 2,800kcal 목표 언급
   - ✅ 단백질 140g 이상 언급
   - ✅ 고칼로리/고단백 메뉴
   - ✅ 운동 전후 식사 타이밍 언급

---

## 🔍 문제 발생 시 체크리스트

### 문제 1: "파일을 찾을 수 없습니다" 에러
**원인**: 사용자별 파일이 Git에 없음  
**해결**: 위의 Git 추가 명령 실행

### 문제 2: 모든 사용자가 동일한 데이터
**원인**: 환경 변수 전달 실패 또는 fallback 사용 중  
**확인**: Streamlit Cloud Logs에서 `[Mock Server]` 로그 확인

### 문제 3: Subprocess 에러
**원인**: MCP 서버 실행 실패  
**해결**: 
- `mcp>=0.9.0` 설치 확인
- `nest-asyncio>=1.5.0` 설치 확인
- Logs에서 상세 에러 확인

### 문제 4: OpenAI API 에러
**원인**: API 키 오류 또는 크레딧 소진  
**해결**: Secrets에서 `OPENAI_API_KEY` 확인

---

## 📈 성능 예상

### Mock 모드 (권장)
- **속도**: 매우 빠름 (로컬 JSON 파일)
- **비용**: OpenAI API 비용만
- **안정성**: 높음
- **데이터 신선도**: Notion 파싱 시점 기준

### 실시간 Notion API 모드 (선택사항)
- **속도**: 느림 (Notion API 호출)
- **비용**: OpenAI + Notion API 요청
- **안정성**: Notion API 의존
- **데이터 신선도**: 실시간 최신

**권장**: Mock 모드로 배포 (이미 최신 데이터 반영됨)

---

## ✅ 최종 체크리스트

배포 전에 다음을 확인하세요:

- [ ] **Git에 사용자 파일 추가** (가장 중요!)
  ```bash
  git add data/parsed_notion_*.json
  git commit -m "feat: Add user-specific mock data"
  git push
  ```

- [ ] **로컬 Mock 모드 테스트**
  ```bash
  USE_NOTION_MCP=false streamlit run app.py
  # 5명 모두 테스트
  ```

- [ ] **Streamlit Secrets 설정**
  - `USE_NOTION_MCP = "false"`
  - `OPENAI_API_KEY = "..."`
  - `OPENAI_MODEL = "gpt-4o-mini"`

- [ ] **requirements.txt 확인**
  - `mcp>=0.9.0` 포함
  - `nest-asyncio>=1.5.0` 포함

- [ ] **배포 후 5명 전원 테스트**
  - 각 사용자 선택
  - 간단한 요청
  - 사용자별 데이터 반영 확인

---

## 🎯 결론

### 현재 상태: ⚠️ 거의 준비됨

**완료 사항**:
- ✅ 코드 구현 완료
- ✅ 데이터 생성 완료
- ✅ 로컬 테스트 통과
- ✅ 문서화 완료

**필요 작업**:
- ❌ **Git에 파일 추가** (5분)
- ⚠️ Secrets 설정 (배포 시)

**예상 결과**: ✅ **정상 작동 가능**

Mock 모드(`USE_NOTION_MCP = "false"`)로 배포하면:
- 5명의 사용자 각각 맞춤 추천
- 실제 Notion 데이터 반영
- 빠르고 안정적인 성능
- 낮은 비용 (OpenAI API만)

**다음 단계**:
1. 위의 Git 명령 실행 (파일 추가/커밋/푸시)
2. Streamlit Cloud에서 Secrets 설정
3. 배포
4. 5명 전원 테스트
5. 완료! 🎉

---

**참고 문서**:
- `STREAMLIT_DEPLOYMENT_CHECKLIST.md` - 상세 체크리스트
- `NOTION_API_VERIFICATION_COMPLETE.md` - 작업 완료 보고서

