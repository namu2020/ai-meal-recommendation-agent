# 버그 수정 내역

## 문제점

### 발생한 에러들

#### 1차 에러
```
Tool Usage Failed
Name: 메뉴 검색
Error: Arguments validation failed: 2 validation errors for 메뉴검색
max_price
  Field required [type=missing, ...]
max_calories
  Field required [type=missing, ...]
```

#### 2차 에러 (수정 시도 후)
```
TypeError: tool() got an unexpected keyword argument 'args_schema'
```

### 에러 발생 원인
1. **Pydantic 검증 실패**: `search_menu` 도구의 선택적 매개변수(`Optional[int] = None`)가 CrewAI의 `@tool` 데코레이터에서 제대로 처리되지 않음
2. **무한 재귀**: 에이전트가 도구 호출을 계속 재시도하면서 재귀 깊이 초과
3. **세그먼트 폴트**: Python 스택 오버플로우로 프로그램 충돌
4. **잘못된 수정**: CrewAI는 LangChain과 달리 `args_schema` 매개변수를 지원하지 않음

## 해결 방법

### ✅ 최종 해결책: 기본값을 None 대신 구체적인 값으로 설정

CrewAI의 `@tool` 데코레이터는 `Optional[type] = None` 패턴을 제대로 처리하지 못합니다.
대신 **필터링을 우회하는 기본값**을 사용하여 모든 매개변수를 선택적으로 만듭니다.

### 수정된 파일

#### 1. `tools/baemin_tools.py`

**수정 전 (문제):**
```python
@tool("메뉴 검색")
def search_menu(
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    max_calories: Optional[int] = None,
    max_cooking_time: Optional[int] = None
) -> str:
    # ...
    if max_price and menu["price"] > max_price:  # None 체크로 인해 문제 발생
        continue
```

**수정 후 (정상):**
```python
@tool("메뉴 검색")
def search_menu(
    category: str = "",
    max_price: int = 999999,
    max_calories: int = 999999,
    max_cooking_time: int = 999999
) -> str:
    # ...
    if category and category.strip() and restaurant["category"] != category:
        continue
    if menu["price"] > max_price:  # 매우 큰 기본값으로 필터 우회
        continue
```

#### 2. `tools/notion_tools.py`

선택적 매개변수가 있는 도구들을 동일한 방식으로 수정

## 테스트 방법

```bash
# 가상환경 활성화
source venv/bin/activate

# Streamlit 앱 실행
streamlit run app.py
```

프론트엔드에서 "30분 안에 먹을 수 있는 다이어트 식단 추천해줘" 같은 요청이 정상적으로 작동합니다.

## 핵심 포인트

⚠️ **CrewAI 도구 작성 시 주의사항**:

1. **❌ 사용하지 말 것**:
   - `Optional[type] = None` - Pydantic 검증 실패
   - `args_schema` 매개변수 - CrewAI에서 지원하지 않음 (LangChain과 다름!)

2. **✅ 올바른 방법**:
   - 구체적인 기본값 사용: `str = ""`, `int = 999999` 등
   - 함수 내부에서 빈 문자열/큰 숫자를 체크하여 필터링 우회
   - 문서화에서 기본값의 의미를 명확히 설명

3. **비교: LangChain vs CrewAI**:
   ```python
   # LangChain (지원됨)
   @tool("메뉴 검색", args_schema=SearchMenuInput)
   def search_menu(category: Optional[str] = None): ...
   
   # CrewAI (위 방법 안 됨!)
   @tool("메뉴 검색")  # args_schema 없음
   def search_menu(category: str = ""): ...  # 구체적 기본값
   ```

이 패턴을 따르면 Pydantic 검증 오류를 방지하고 도구가 안정적으로 작동합니다.

