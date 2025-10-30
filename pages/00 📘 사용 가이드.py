import streamlit as st

st.set_page_config(page_title="📘 사용 가이드", page_icon="📘", layout="centered")

st.title("📘 ASAP (AI Search Agent Platform)")
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
