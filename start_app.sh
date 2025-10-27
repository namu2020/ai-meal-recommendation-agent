#!/bin/bash

# Streamlit 앱 시작 스크립트 (FSEvents 에러 우회)

cd "/Users/namu123/Documents/테크 관련/공훈의_AI특강/팀플/crewai-food-app"

# 가상환경 활성화
source venv/bin/activate

# FSEvents 에러 우회를 위한 환경 변수 설정
export WATCHDOG_USE_KQUEUE=1

echo "🚀 Streamlit 앱 시작..."
echo ""

# Streamlit 실행 (파일 감시 비활성화)
streamlit run app.py --server.fileWatcherType none

# 또는 일반 실행
# streamlit run app.py

