import streamlit as st
from information.button import RAG_CHAT_HELP_BUTTON_MESSAGE, RAG_CHAT_CLEAR_BUTTON_MESSAGE, RAG_CHAT_HELP_DIALOG_MESSAGE


def show_data_collect_agent_help_dialog():
    @st.dialog("ℹ️ 에이전트 사용법")
    def _dialog():
        st.markdown(
            """
            ### 💫 자료 수집 에이전트 사용법
            
            **도메인 기반 검색 기능**
            - 좌측에서 관심 도메인(URL)을 등록하면 시스템 프롬프트에 반영됩니다.
            - 이후 채팅에서 해당 도메인을 컨텍스트로 활용하여 검색/요약이 이뤄집니다.
            - 등록/초기화, 동적 입력칸 추가, 형식 검증(http/https) 지원.
            
            **MCP 도구 설명**
            - Tavily Search Tool: 웹 전반(SERP) 기반의 신뢰도 높은 검색 결과를 반환합니다. 최신 이슈/뉴스/블로그 검색에 적합합니다.
            - Paper Search Tool: 논문/학술 자료 중심의 키워드 검색을 수행합니다. 제목/요약/링크 중심 결과를 반환합니다.
            
            사용 팁: 채팅 입력에 "도메인 기반으로 최신 자료 찾아줘", "논문 위주로 정리해줘" 등 의도를 명시하면 도구 선택이 더 정확해집니다.
            
            추천 도메인
            - https://www.aitimes.com/news
            - https://huggingface.co/models?pipeline_tag=text-generation&sort=created
            """
        )
    _dialog()


def show_knowledge_hub_info_dialog():
    @st.dialog("ℹ️ 지식 허브 사용법")
    def _dialog():
        st.markdown(
            """
            ### 지식 허브란?
            
            **🔍 키워드 기반 AI 기술 관계도 시각화**
            
            - 검색된 자료의 키워드를 추출하여 기술 관계도를 생성합니다
            - 각 키워드별로 연결된 기술과 논문을 시각적으로 확인할 수 있습니다
            
            **📊 대시보드 구성:**
            - **차트**: 키워드별 하위 기술 개수를 한눈에 확인
            - **표**: 전체 키워드 또는 특정 키워드의 논문 목록 조회
            
            **💡 사용 방법:**
            1. 키워드 드롭다운에서 확인하고 싶은 키워드 선택
            2. 차트에서 키워드별 기술 분포 확인
            3. 표에서 해당 키워드의 논문 목록 확인
            """
        )
    _dialog()


def show_rag_chat_help_dialog():
    @st.dialog(RAG_CHAT_HELP_BUTTON_MESSAGE)
    def _dialog():
        st.markdown(RAG_CHAT_HELP_DIALOG_MESSAGE)
    _dialog()


