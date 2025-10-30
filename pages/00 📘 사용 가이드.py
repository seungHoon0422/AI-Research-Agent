import streamlit as st

st.set_page_config(page_title="📘 사용 가이드", page_icon="📘", layout="centered")

st.title("📘 AI Research Agent 사용 가이드")
st.caption("아래 각 섹션의 제목을 클릭하면 해당 페이지로 이동합니다.")
st.markdown("---")

from information.markdown import GUIDE_01_SUMMARY_MD, GUIDE_02_SUMMARY_MD, GUIDE_03_SUMMARY_MD

st.page_link(
    "pages/01 💫 기술 자료 수집 및 검색 기능.py",
    label="### 01. 💫 기술 자료 수집 및 검색 기능",
)
st.markdown(GUIDE_01_SUMMARY_MD)

st.markdown("---")

st.page_link(
    "pages/02 💫 Chat Model with RAG.py",
    label="### 02. 💫 Chat Model with RAG",
)
st.markdown(GUIDE_02_SUMMARY_MD)

st.markdown("---")

st.page_link(
    "pages/03 🍀 Document Hub.py",
    label="### 03. 🍀 Document Hub",
)
st.markdown(GUIDE_03_SUMMARY_MD)

st.markdown("---")

with st.expander("ℹ️ 팁: 자주 묻는 질문"):
    st.markdown("""
    - 도메인 입력칸은 최대 3개까지 추가됩니다. CLEAR로 초기화할 수 있습니다.
    - PDF 미리보기는 최대 5페이지 텍스트만 표시됩니다(이미지 기반 PDF는 제외).
    - 인덱서 실행/상태 확인은 `ai_search.IndexerManager`를 통해 관리됩니다.
    - 그래프는 컬럼 너비에 맞춰 100%로 렌더링되며, 레이아웃 비율은 상단 3:1 구성입니다.
    """)


