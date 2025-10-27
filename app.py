"""
Streamlit 챗봇 UI - 개인화된 음식 추천 챗봇
"""
import streamlit as st
from crew import FoodRecommendationCrew
from user_manager import get_all_users, get_user_info, save_current_user
import os
import time

# 페이지 설정
st.set_page_config(
    page_title="AI 음식 추천 챗봇",
    page_icon="🍽️",
    layout="wide"
)

# 세션 상태 초기화
if "selected_user" not in st.session_state:
    st.session_state.selected_user = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "crew" not in st.session_state:
    st.session_state.crew = None

# ============================================
# 사용자 선택 화면
# ============================================
if st.session_state.selected_user is None:
    st.title("🍽️ AI 개인화 음식 추천 챗봇")
    st.markdown("### 👤 사용자를 선택해주세요")
    st.markdown("각 사용자에게 맞춤화된 식사 추천을 제공합니다.")
    
    st.divider()
    
    # 5명의 사용자 카드 표시 (2-2-1 레이아웃)
    users = get_all_users()
    
    # 첫 번째 행: 2명
    col1, col2 = st.columns(2)
    
    with col1:
        user_info = get_user_info(users[0])
        with st.container():
            st.markdown(f"### {user_info['emoji']} {user_info['name']}")
            st.markdown(f"**{user_info['special']}**")
            st.caption(user_info['description'])
            if st.button(f"선택", key=f"btn_{users[0]}", use_container_width=True):
                st.session_state.selected_user = users[0]
                save_current_user(users[0])
                os.environ["CURRENT_NOTION_USER"] = users[0]
                st.rerun()
    
    with col2:
        user_info = get_user_info(users[1])
        with st.container():
            st.markdown(f"### {user_info['emoji']} {user_info['name']}")
            st.markdown(f"**{user_info['special']}**")
            st.caption(user_info['description'])
            if st.button(f"선택", key=f"btn_{users[1]}", use_container_width=True):
                st.session_state.selected_user = users[1]
                save_current_user(users[1])
                os.environ["CURRENT_NOTION_USER"] = users[1]
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 두 번째 행: 2명
    col3, col4 = st.columns(2)
    
    with col3:
        user_info = get_user_info(users[2])
        with st.container():
            st.markdown(f"### {user_info['emoji']} {user_info['name']}")
            st.markdown(f"**{user_info['special']}**")
            st.caption(user_info['description'])
            if st.button(f"선택", key=f"btn_{users[2]}", use_container_width=True):
                st.session_state.selected_user = users[2]
                save_current_user(users[2])
                os.environ["CURRENT_NOTION_USER"] = users[2]
                st.rerun()
    
    with col4:
        user_info = get_user_info(users[3])
        with st.container():
            st.markdown(f"### {user_info['emoji']} {user_info['name']}")
            st.markdown(f"**{user_info['special']}**")
            st.caption(user_info['description'])
            if st.button(f"선택", key=f"btn_{users[3]}", use_container_width=True):
                st.session_state.selected_user = users[3]
                save_current_user(users[3])
                os.environ["CURRENT_NOTION_USER"] = users[3]
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 세 번째 행: 1명 (중앙 정렬)
    col5, col6, col7 = st.columns([1, 2, 1])
    
    with col6:
        user_info = get_user_info(users[4])
        with st.container():
            st.markdown(f"### {user_info['emoji']} {user_info['name']}")
            st.markdown(f"**{user_info['special']}**")
            st.caption(user_info['description'])
            if st.button(f"선택", key=f"btn_{users[4]}", use_container_width=True):
                st.session_state.selected_user = users[4]
                save_current_user(users[4])
                os.environ["CURRENT_NOTION_USER"] = users[4]
                st.rerun()
    
    st.stop()

# ============================================
# 챗봇 화면 (사용자 선택 후)
# ============================================

# 현재 사용자 정보
current_user = get_user_info(st.session_state.selected_user)

# 🔥 중요: 환경 변수를 확실히 설정 (Streamlit 페이지 리로드 시 유지)
os.environ["CURRENT_NOTION_USER"] = st.session_state.selected_user

# 타이틀 with 사용자 정보
st.title(f"🍽️ {current_user['emoji']} {current_user['name']}님의 AI 음식 추천 챗봇")
st.markdown(f"**{current_user['special']}** | {current_user['description']}")

st.divider()

# 초기 메시지 설정
if len(st.session_state.messages) == 0:
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"안녕하세요, {current_user['name']}님! 🍽️\n\n저는 **{current_user['name']}님만을 위한** 개인화된 AI 음식 추천 챗봇입니다!\n\n**동적 워크플로우 시스템**으로 여러분의 요청에 최적화된 답변을 제공합니다!\n\n### 질문 예시\n\n**📋 전체 메뉴 추천**\n- 오늘 저녁 메뉴 추천해줘\n- 1만원 이하로 다이어트 식단 추천해줘\n\n**👨‍🍳 레시피/조리법**\n- 된장찌개 만드는 법 알려줘\n- 파스타 레시피 알려줘\n- 김치볶음밥 어떻게 만들어?\n\n**⚡ 빠른 식사**\n- 30분 안에 먹을 수 있는 거\n- 빨리 만들 수 있는 음식\n\n**💰 예산/일정**\n- 이번 달 식비 얼마 썼어?\n- 오늘 일정 어때?\n\n무엇을 도와드릴까요?"
    })

# 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
user_input = st.chat_input("메시지를 입력하세요...")

if user_input:
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # AI 응답 생성
    with st.chat_message("assistant"):
        with st.spinner("🤖 AI가 작업 중입니다..."):
            try:
                # Crew 초기화 (최초 1회) - 대화 맥락 유지
                if st.session_state.crew is None:
                    st.session_state.crew = FoodRecommendationCrew()
                
                # 진행 상황 표시
                progress_placeholder = st.empty()
                
                # 단계별 진행 표시
                progress_placeholder.info("🎛️ 1단계: 사용자 의도 분석 중...")
                time.sleep(0.8)
                
                progress_placeholder.info("🔧 2단계: 필요한 에이전트 선택 중...")
                time.sleep(0.8)
                
                progress_placeholder.info("⚙️ 3단계: 에이전트 실행 중...")
                time.sleep(0.5)
                
                progress_placeholder.empty()
                
                # Crew 실행
                result = st.session_state.crew.run(user_input)
                
                # 결과를 문자열로 변환
                if hasattr(result, 'raw'):
                    response = result.raw
                elif hasattr(result, 'output'):
                    response = result.output
                else:
                    response = str(result)
                
                # 응답 표시
                st.markdown(response)
                
                # 성공 메시지 with workflow info
                workflow_info = ""
                if hasattr(st.session_state.crew, 'conversation_history'):
                    workflow_info = f" (대화 기록: {len(st.session_state.crew.conversation_history)}개)"
                st.success(f"✅ 완료!{workflow_info}")
                
                # 메시지 저장
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })
                
            except Exception as e:
                error_msg = f"❌ 오류가 발생했습니다: {str(e)}\n\n다시 시도해주세요."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# 사이드바 - 정보 및 설정
with st.sidebar:
    # 현재 사용자 정보 카드
    st.markdown(f"### {current_user['emoji']} {current_user['name']}님")
    st.markdown(f"**{current_user['special']}**")
    st.caption(current_user['description'])
    
    # 사용자 변경 버튼
    if st.button("👤 사용자 변경", use_container_width=True):
        st.session_state.selected_user = None
        st.session_state.messages = []
        st.session_state.crew = None
        if "CURRENT_NOTION_USER" in os.environ:
            del os.environ["CURRENT_NOTION_USER"]
        st.rerun()
    
    st.divider()
    
    st.header("ℹ️ 정보")
    
    st.subheader("🎛️ 워크플로우 타입")
    st.markdown("""
    - **FULL_RECOMMENDATION**: 전체 메뉴 추천
    - **RECIPE_ONLY**: 레시피/조리법만
    - **BUDGET_CHECK**: 예산 확인
    - **NUTRITION_INFO**: 영양 정보
    - **SCHEDULE_CHECK**: 일정 확인
    - **QUICK_MEAL**: 빠른 식사
    
    ⚡ 필요한 에이전트만 자동 선택됩니다!
    """)
    
    st.divider()
    
    st.subheader("💡 사용 팁")
    st.markdown("""
    1. **대화 맥락 유지**
       - 이전 대화를 기억합니다
       - "그거 레시피 알려줘" 가능!
    
    2. **구체적 요청**
       - "다이어트 메뉴", "저렴한 메뉴"
       - "30분 이내", "1만원 이하"
    
    3. **선호도 표현**
       - 한식/일식, 매운 정도
       - 알레르기, 다이어트 목표
    """)
    
    st.divider()
    
    st.subheader("🔧 기술 스택")
    st.markdown("""
    - **CrewAI**: 멀티 에이전트
    - **MCP**: Notion 데이터 연동
    - **OpenAI GPT-4o-mini**: LLM
    - **Streamlit**: UI
    """)
    
    st.divider()
    
    # 대화 초기화 버튼
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.crew = None
        st.rerun()
    
    st.divider()
    
    st.caption("© 2025 AI 음식 추천 챗봇")
    st.caption("Powered by CrewAI & OpenAI")

