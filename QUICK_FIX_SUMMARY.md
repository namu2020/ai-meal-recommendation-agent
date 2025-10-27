# 🔧 긴급 수정 완료

## 문제
```
TypeError: tool() got an unexpected keyword argument 'args_schema'
```

## 원인
CrewAI는 LangChain과 달리 `@tool` 데코레이터에서 `args_schema` 매개변수를 **지원하지 않습니다**.

## 해결
선택적 매개변수를 `None` 대신 **구체적인 기본값**으로 변경:

| 이전 (❌ 실패)                  | 이후 (✅ 성공)              |
|--------------------------------|---------------------------|
| `category: Optional[str] = None` | `category: str = ""`      |
| `max_price: Optional[int] = None` | `max_price: int = 999999` |
| `max_calories: Optional[int] = None` | `max_calories: int = 999999` |

## 수정된 파일
- ✅ `tools/baemin_tools.py` - 3개 도구 수정
- ✅ `tools/notion_tools.py` - 1개 도구 수정

## 테스트
```bash
streamlit run app.py
```

이제 프론트엔드가 정상적으로 로드되고 에이전트가 도구를 호출할 수 있습니다! 🎉

