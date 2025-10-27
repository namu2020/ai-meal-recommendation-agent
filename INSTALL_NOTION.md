# Notion 패키지 설치 가이드

## 문제
SSL 인증서 오류로 인해 pip 설치가 실패합니다.

## 해결 방법

### 방법 1: SSL 인증서 무시하고 설치 (빠름)
```bash
cd "/Users/namu123/Documents/테크 관련/공훈의_AI특강/팀플/crewai-food-app"

# 가상환경이 있다면 활성화
source venv/bin/activate

# SSL 인증서 체크 건너뛰고 설치
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org notion-client nest-asyncio
```

### 방법 2: Python 인증서 업데이트 (권장)
```bash
# macOS의 경우
/Applications/Python\ 3.11/Install\ Certificates.command

# 또는
pip install --upgrade certifi
```

그 다음:
```bash
pip install notion-client nest-asyncio
```

### 방법 3: 직접 다운로드 후 설치
```bash
# GitHub에서 직접 다운로드
git clone https://github.com/ramnes/notion-sdk-py.git
cd notion-sdk-py
pip install .
cd ..

pip install nest-asyncio
```

## 설치 확인

```bash
python -c "import notion_client; print('✅ notion-client 설치 완료')"
```

## 다음 단계

설치 완료 후:
```bash
# 1. Notion API 테스트
python test_notion_api.py

# 2. 결과 확인
cat notion_structure.json
```

