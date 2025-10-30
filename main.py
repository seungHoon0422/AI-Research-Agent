import streamlit as st

st.set_page_config(page_title="AI 기술 리서치 플랫폼", page_icon="🤖", layout="wide")

# Streamlit Navigation API (1.39+)
home = st.Page("pages/00 📘 사용 가이드.py", title="사용 가이드", icon="📘")
p1 = st.Page("pages/01 💫 기술 자료 수집 및 검색 기능.py", title="01 기술 자료 수집/검색", icon="💫")
p2 = st.Page("pages/02 💫 Chat Model with RAG.py", title="02 Chat Model with RAG", icon="💫")
p3 = st.Page("pages/03 🍀 Document Hub.py", title="03 Document Hub", icon="🍀")

nav = st.navigation([home, p1, p2, p3])
nav.run()

