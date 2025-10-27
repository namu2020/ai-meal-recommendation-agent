"""
설정 파일 - LLM 및 에이전트 설정
"""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# 환경 변수 로드
load_dotenv()

# OpenAI 설정
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# LLM 인스턴스 생성
def get_llm(temperature=0.7):
    """LLM 인스턴스 반환"""
    return ChatOpenAI(
        model=OPENAI_MODEL,
        temperature=temperature,
        api_key=OPENAI_API_KEY
    )

# 에이전트 가중치
AGENT_WEIGHTS = {
    "nutrition": 0.30,  # 영양사 - 건강 최우선
    "budget": 0.25,     # 총무 - 예산 효율
    "taste": 0.20,      # 맛슐랭 - 맛의 품질
    "scheduler": 0.15,  # 스케줄러 - 시간 효율
    "chef": 0.10,       # 요리사 - 집밥 가능성
}

# 데이터 경로
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
NOTION_DATA_PATH = os.path.join(DATA_DIR, "mock_notion.json")
BAEMIN_DATA_PATH = os.path.join(DATA_DIR, "mock_baemin.json")

# MCP 사용 여부 설정
USE_NOTION_MCP = os.getenv("USE_NOTION_MCP", "false").lower() == "true"

# Notion API 설정 (MCP 사용 시)
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# CrewAI 설정
CREW_CONFIG = {
    "verbose": True,
    "memory": False,  # 메모리 기능 비활성화 (간단한 구현)
}

