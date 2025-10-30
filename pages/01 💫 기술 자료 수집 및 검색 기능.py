import streamlit as st
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError, ResourceNotFoundError
from dotenv import load_dotenv
import json
from core.tool_calling import ToolCallingManager
from models.model_selector import model, init_model
from prompt.system_prompt import DEFAULT_SYSTEM_PROMPT, DOMAI_ADD_SYSTEM_PROMPT
from information.button import RAG_CHAT_CLEAR_BUTTON_MESSAGE
import os


MAX_DOMAIN_INPUT_COUNT = 3

st.set_page_config(page_title="AI 기술 리서치 플랫폼", page_icon="🤖", layout="wide")

col1, col2 = st.columns([1, 1])

with col1:
    # 검색할 도메인 사용자에게 입력받는 레이아웃 (동적 입력칸 + 버튼으로 추가)
    if 'domain_input_list' not in st.session_state:
        st.session_state.domain_input_list = []  # 확정 저장된 도메인 목록
    if 'domain_fields' not in st.session_state:
        st.session_state.domain_fields = [""]  # 화면에 보이는 입력칸들
    if 'files_uploaded' not in st.session_state:
        st.session_state.files_uploaded = False  # 파일 업로드 완료 상태

    
    st.markdown("### 📮 관심 도메인 등록")


    from information.expander import DOMAIN_REGISTER_GUIDE_TITLE
    from information.markdown import DOMAIN_REGISTER_GUIDE_MD
    with st.expander(DOMAIN_REGISTER_GUIDE_TITLE, expanded=False):
        st.markdown(DOMAIN_REGISTER_GUIDE_MD)


    # 동적 입력칸 렌더링
        for idx in range(len(st.session_state.domain_fields)):
            st.session_state.domain_fields[idx] = st.text_input(
                label=f"도메인 {idx + 1}",
                key=f"domain_field_{idx}",
                placeholder="https://example.com",
                label_visibility="collapsed",
                value=st.session_state.domain_fields[idx],
                help="http 또는 https로 시작하는 URL을 입력하세요.",
            )

        # '+' 버튼: 입력칸 추가
        add_clicked = st.button("입력칸 추가 +", use_container_width=True, help="입력칸 추가")
        if add_clicked:
            if len(st.session_state.domain_fields) >= MAX_DOMAIN_INPUT_COUNT:
                st.toast(f"📋 입력칸은 최대 {MAX_DOMAIN_INPUT_COUNT}개까지 가능합니다.")
            else:
                st.session_state.domain_fields.append("")
                st.rerun()

        # '도메인 등록' 버튼: 입력값을 검증 후 확정 목록에 추가
        button_col1, button_col2 = st.columns([0.8, 0.2])

        with button_col1:
            submit_clicked = st.button("도메인 등록", use_container_width=True)
            if submit_clicked:
                added = 0
                for url in st.session_state.domain_fields:
                    if not url:
                        continue
                    if not url.startswith("http"):
                        st.toast(f"❌ 잘못된 URL: {url} (http/https로 시작해야 합니다)")
                        continue
                    if url in st.session_state.domain_input_list:
                        continue
                    if len(st.session_state.domain_input_list) >= MAX_DOMAIN_INPUT_COUNT:
                        st.toast(f"ℹ️ 최대 {MAX_DOMAIN_INPUT_COUNT}개까지만 저장됩니다.")
                        break
                    st.session_state.domain_input_list.append(url)
                    added += 1
                if added > 0:
                    st.toast(f"✅ 도메인 {added}개가 추가되었습니다.")

        with button_col2:
            clear_button_clicked = st.button("CLEAR", type='primary', use_container_width=True)
            if clear_button_clicked:
                st.session_state.domain_input_list = []
                st.toast("저장된 도메인을 모두 지웠습니다.")
                st.rerun()
            
    st.markdown("---")

    import io
    import PyPDF2
    from storage.azure_blob_storage import AzureBlobStorage


    storage = AzureBlobStorage()


    doc_file = None
    doc_file_list = []

    @st.dialog('문서 미리보기')
    def vote_preview_document(item):
        doc_file = None
        if item and len(item) > 0:
            doc_file = item[0]

            if doc_file.type == "text/plain" or doc_file.name.endswith('.txt'):
                # 텍스트 파일 내용 표시
                content = doc_file.getvalue().decode('utf-8')
                st.text_area("파일 내용", content, height=300)
                    
            elif doc_file.type == "text/markdown" or doc_file.name.endswith('.md'):
                # 마크다운 파일 내용 표시
                content = doc_file.getvalue().decode('utf-8')
                st.markdown("**마크다운 미리보기:**")
                st.markdown(content)
                
            elif doc_file.type == "application/pdf":
                # PDF 파일 내용 추출 및 표시
                try:
                    # PDF 파일을 BytesIO로 변환
                    pdf_file = io.BytesIO(doc_file.getvalue())
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    
                    st.write(f"📄 **PDF 정보:** {len(pdf_reader.pages)}페이지")
                    
                    # 첫 번째 페이지부터 최대 5페이지까지 텍스트 추출
                    max_pages = min(5, len(pdf_reader.pages))
                    extracted_text = ""
                    
                    for page_num in range(max_pages):
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        extracted_text += f"\n--- 페이지 {page_num + 1} ---\n"
                        extracted_text += text + "\n"
                    
                    if extracted_text.strip():
                        st.text_area("PDF 내용", extracted_text, height=400)
                    else:
                        st.warning("PDF에서 텍스트를 추출할 수 없습니다. (이미지만 포함된 PDF일 수 있습니다)")
                        
                    if len(pdf_reader.pages) > 5:
                        st.info(f"📄 총 {len(pdf_reader.pages)}페이지 중 처음 5페이지만 표시됩니다.")
                        
                except Exception as e:
                    st.error(f"PDF 파일을 읽는 중 오류가 발생했습니다: {str(e)}")
                
            elif doc_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
                                "application/msword"]:
                st.info("📄 Word 문서는 미리보기를 지원하지 않습니다.")
            else:
                st.info("📄 이 파일 형식은 미리보기를 지원하지 않습니다.")
        
    st.markdown("### 📄 기술 문서 등록")
    from information.expander import DOC_UPLOAD_GUIDE_TITLE
    from information.markdown import DOC_UPLOAD_GUIDE_MD, DOC_UPLOAD_INFO_MD
    with st.expander(DOC_UPLOAD_GUIDE_TITLE):
        st.markdown(DOC_UPLOAD_GUIDE_MD)
        st.info(DOC_UPLOAD_INFO_MD)

        # pdf, 등 문서 파일 업로드
        doc_file = st.file_uploader('문서 파일을 업로드하세요.', accept_multiple_files=True, type=['pdf', 'docx', 'doc', 'txt', 'md'])
        if doc_file is not None:
            doc_file_list.extend(doc_file)
            st.session_state.files_uploaded = False  # 새 파일 선택 시 업로드 상태 초기화
            if len(doc_file_list) > 0:
                doc_file = doc_file_list[0]
            else:
                doc_file = None

        st.markdown('---')


        col1_1, col1_2 = st.columns(2)

        with col1_1:
            preview_button_clicked = st.button("문서 미리보기", use_container_width=True)
            if preview_button_clicked:
                if doc_file_list and len(doc_file_list) > 0:
                    vote_preview_document(doc_file_list)
                else:
                    st.toast("문서를 업로드해주세요.", duration="short", icon="🚨")
        with col1_2:
            upload_button_clicked = st.button("파일 업로드", use_container_width=True)
            if upload_button_clicked:
                if len(doc_file_list) > 0:
                    with st.spinner("파일 업로드 중..."):
                        for uploaded_file in doc_file_list:
                            storage.upload_blob_file_from_streamlit(uploaded_file)
                    st.success(f"{len(doc_file_list)}개의 파일 업로드가 완료되었습니다.")
                    st.session_state.files_uploaded = True  # 업로드 완료 상태로 변경
                else:
                    st.toast("문서를 업로드해주세요.", duration="short", icon="🚨")

    # 인덱서 관리 섹션  
    st.markdown("---")      

    st.markdown("### 🍀 Document Hub 등록")
    from information.expander import DOC_HUB_GUIDE_TITLE
    from information.markdown import DOC_HUB_GUIDE_MD
    with st.expander(DOC_HUB_GUIDE_TITLE, expanded=False):
        st.markdown(DOC_HUB_GUIDE_MD)

        rerun_indexer_button_clicked = st.button(
            "Document Hub 업데이트", 
            use_container_width=True, 
            help="AI Search 인덱서를 재실행합니다."
        )
        
        # 인덱서 재실행 처리
        if rerun_indexer_button_clicked:
            try:
                from ai_search.indexer_manager import IndexerManager
                indexer_manager = IndexerManager()
                
                with st.spinner("Updating Document Hub..."):
                    result = indexer_manager.run_indexer()
                    
                    if result["success"]:
                        st.success(result["message"])
                        st.toast(result["message"], icon="✅")
                    else:
                        st.error(result["message"])
                        st.toast(result["message"], icon="🚨")
            except Exception as e:
                st.error(f"Document Hub 업데이트 중 오류: {e}")
                st.toast("Document Hub 업데이트 오류가 발생했습니다.", icon="🚨")
        
        # 인덱서 상태 확인 버튼
        status_button_clicked = st.button("Document Hub 연결 확인", use_container_width=True, help="Document Hub 연결 상태를 확인합니다.")
        
        # 인덱서 상태 확인 처리
        if status_button_clicked:
            try:
                from ai_search.indexer_manager import IndexerManager
                indexer_manager = IndexerManager()
                
                with st.spinner("Document Hub 연결 확인 중..."):
                    result = indexer_manager.get_indexer_status()
                    
                    if result["success"]:
                        st.toast(result["message"], icon="✅")
                        if result["data"]:
                            with st.expander("Indexer Connection Detail", expanded=False):
                                st.json(result["data"])
                    else:
                        st.error(result["message"])
                        st.toast(result["message"], icon="🚨")
            except Exception as e:
                st.error(f"Document Hub 확인 중 오류: {e}")
                st.toast("Document Hub  확인 중 오류가 발생했습니다.", icon="🚨")



with col2:
    


    ### NOTE: 모델 채팅
    load_dotenv()

    ### 모델 초기화
    init_model()
    model_client = model.client()
    # use_tool = st.sidebar.checkbox("🔧 도구 사용", value=True, help="도구 사용 여부")
    use_tool = True
    temperature = st.sidebar.slider("temperature", 0.0, 1.0, 0.4)
    tool_calling_manager = None

    #### 채팅 기록의 초기화
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    #### SYTEM Prompt 초기화
    if st.session_state.messages == []:
        # download_path = "/Users/baegseunghun/Desktop/ktds/edu/AI-Research-Agent/download_files"
        # 프로젝트 루트 경로를 받아올 수 있는 방법
        download_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "download_files")
        
        st.session_state.messages.append({"role": "system", "content": DEFAULT_SYSTEM_PROMPT.format(download_path=download_path)})

    col2_1, col2_2 = st.columns([0.7, 0.3])
    with col2_1:
        st.markdown("### 💫 자료 수집 에이전트")
        st.caption("관심 도메인 기반 자료 수집, 논문 검색 기능을 제공합니다.")
    with col2_2:
        from information.dialog import show_data_collect_agent_help_dialog
        if st.button("ℹ️ 에이전트 사용법", use_container_width=True):
            show_data_collect_agent_help_dialog()
        chat_clear_button_clicked = st.button(RAG_CHAT_CLEAR_BUTTON_MESSAGE, use_container_width=True)    
        if chat_clear_button_clicked:
            st.session_state.messages = []
            st.toast("채팅 초기화되었습니다.")
            st.rerun()



    #### Azure OpenAI Client 생성
    def get_azure_openai_client(messages):


        if use_tool:
            tool_calling_manager = ToolCallingManager(azure_client=model_client, model_name=model.base_model_name())
        tools =[]
        if use_tool:
            tools = tool_calling_manager.tool_list
        
        # System Prompt에 관심 도메인 추가
        if len(st.session_state.domain_input_list) > 0:
            system_prompt = DOMAI_ADD_SYSTEM_PROMPT.format(domain_list=st.session_state.domain_input_list)
            breakpoint()
            messages.append({"role": "system", "content": system_prompt})

        try:
            response = model.chat(
                tools=tools,
                messages=messages,
                temperature=temperature,
            )

            if response.choices[0].message.tool_calls:
                # Tool 호출이 있는 경우 처리
                # ChatCompletionMessage 객체를 딕셔너리로 변환
                assistant_message = {
                    "role": "assistant",
                    "content": response.choices[0].message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        } for tool_call in response.choices[0].message.tool_calls
                    ]
                }
                # pprint(f"Assistant Message: {assistant_message}")
                messages.append(assistant_message)
                
                tool_response,tool_response_str = None, None

                for tool_call in response.choices[0].message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    print(f"Tool {tool_name} called with arguments: {tool_args}")
                    
                    # Tool 실행
                    with st.spinner(f'Tool {tool_name} is calling...'):
                        try:
                            tool_response = tool_calling_manager.execute_tool_call(tool_call, tool_name, tool_args)
                            tool_response_str = json.dumps(tool_response, default=str, ensure_ascii=False)
                            # UI에 표시 (expander 사용)
                            with st.chat_message("assistant"):
                                with st.expander(f'Tool Calling: {tool_name}', expanded=False):
                                    st.write(tool_response_str)
                        except Exception as e:
                            st.error(f"Tool {tool_name} 실행 중 오류가 발생했습니다: {e}")
                            
                    # Tool 응답을 메시지에 추가
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_name,
                        "content": tool_response_str,
                    }
                    messages.append(tool_message)
                # 최종 응답 생성
                final_response = model.chat(
                    messages=messages,
                    temperature=temperature,
                )
                return final_response.choices[0].message.content
            else:
                # Tool 호출이 없는 경우
                return response.choices[0].message.content
        except (HttpResponseError, ClientAuthenticationError, ResourceNotFoundError) as e:
            st.error(f"Azure OpenAI API 호출 중 오류가 발생했습니다: {e}")
            return f"오류: {e}" 
        except Exception as e:
            st.error(f"OpenAI API 호출 중 오류가 발생했습니다: {e}")
            return f"오류: {e}"

    
    # 앵커: 바로 다음에 나오는 컨테이너 블록만 선택하기 위한 표식
    st.markdown('<div id="chat-anchor"></div>', unsafe_allow_html=True)

    with st.container(border=True, height= 600):
        # 이 컨테이너 블록을 반응형 높이 + 스크롤로 지정
        st.markdown(
            """
            <style>
            /* 앵커 바로 다음 형제 div(=이 컨테이너의 루트)를 스크롤 영역으로 */
            #chat-anchor + div[data-testid="stVerticalBlock"] {
                height: calc(100vh - 260px); /* 필요에 맞게 260 조정 */
                overflow: auto;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # 여기 안에 채팅 메시지 렌더링
        for message in st.session_state.messages:
            if not message or message.get("role") == "system":
                continue
            elif message["role"] == "tool":
                with st.chat_message("assistant"):
                    with st.expander(f'Tool Calling: {message.get("name", "unknown")}', expanded=False):
                        st.write(message["content"])
            elif message.get("tool_calls"):
                continue
            else:
                st.chat_message(message["role"]).write(message["content"])    
    # 입력창을 마지막에 (하단 고정)
    if user_input := st.chat_input("메시지를 입력하세요"):
        st.session_state.messages.append({"role": "user","content": user_input})
        
        with st.spinner("GPT가 응답하는 중..."):
            assistant_response = get_azure_openai_client(st.session_state.messages)
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        st.rerun()



