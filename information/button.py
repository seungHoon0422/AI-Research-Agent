
### RAG(Retrieval-Augmented Generation) 기반 채팅        
RAG_CHAT_HELP_DIALOG_MESSAGE = """
    이 페이지는 Azure AI Search와 연동된 RAG 에이전트 채팅 페이지입니다.
    
    **📚 주요 기능:**
    1. 사용자가 업로드한 파일 기반 응답 생성
    2. Keyword 기반 사용자 질문 시 관련 문서를 자동으로 검색
    3. 검색된 문서를 참고하여 정확한 답변 제공
    4. 답변 시 참고한 청크(Citation) 표시
    
    **🔍 동작 방식:**
    1. 사용자가 업로드한 파일을 Azure Blob Storage에 저장
    2. 인덱스 업데이트를 통해 업로드된 파일을 document 형태로 Azure AI Search에 저장
    2. 질문 입력 시 관련 문서 자동 검색
    3. 검색 결과를 모델 컨텍스트에 포함하여 답변 생성
    
    **💡 팁:**
    - 문서 업로드는 "기술 자료 수집 및 검색 기능" 페이지에서 가능합니다
    - 인덱서를 재실행하면 업로드된 문서가 검색 가능한 상태가 됩니다
"""

RAG_CHAT_CLEAR_BUTTON_MESSAGE = "🗑️ 채팅 초기화"

RAG_CHAT_HELP_BUTTON_MESSAGE = "ℹ️ 에이전트 사용법"

# Document Hub
DOCUMENT_HUB_HELP_BUTTON_MESSAGE = "ℹ️ Document Hub 사용법"