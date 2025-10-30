import streamlit as st
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError, ResourceNotFoundError
from dotenv import load_dotenv
import json
from core.tool_calling import ToolCallingManager
from models.model_selector import model, init_model
from prompt.system_prompt import DEFAULT_SYSTEM_PROMPT
from information.button import RAG_CHAT_HELP_BUTTON_MESSAGE, RAG_CHAT_CLEAR_BUTTON_MESSAGE, RAG_CHAT_HELP_DIALOG_MESSAGE
from information.title import RAG_CHAT_TITLE
import os

st.set_page_config(page_title="AI 기술 리서치 플랫폼", page_icon="🤖", layout="wide")


#### NOTE: title 설정
col2_1, col2_2 = st.columns([0.8, 0.2])
with col2_1:
    st.markdown(RAG_CHAT_TITLE)
    # 에이전트 사용법 모달 함수 정의

with col2_2:
    # 에이전트 사용법 모달 버튼
    help_button_clicked = st.button(RAG_CHAT_HELP_BUTTON_MESSAGE, use_container_width=True, help="에이전트 사용법 확인")
    
    # 버튼 클릭 시 모달 호출
    if help_button_clicked:
        from information.dialog import show_rag_chat_help_dialog
        show_rag_chat_help_dialog()
    
    # 채팅 초기화 버튼 (아래로 이동)
    chat_clear_button_clicked = st.button(RAG_CHAT_CLEAR_BUTTON_MESSAGE, use_container_width=True, help="채팅 기록 초기화")
    if chat_clear_button_clicked:
        st.session_state.messages = []
        st.toast("채팅 초기화되었습니다.")
        st.rerun()

st.markdown("---")


#### NOTE: Sidebar model Config 설정
st.sidebar.title("💡 모델 설정")


### NOTE: 모델 채팅

load_dotenv()

### 모델 초기화
init_model()
#### 채팅 기록의 초기화
if 'messages' not in st.session_state:
    st.session_state.messages = []

#### SYTEM Prompt 초기화
if st.session_state.messages == []:
    st.session_state.messages.append({"role": "system", "content": DEFAULT_SYSTEM_PROMPT})

# RAG 에이전트 채팅에서는 도구 사용 x
# use_tool = st.sidebar.checkbox("🔧 도구 사용", value=False, help="도구 사용 여부")
use_tool = False

####  NOTE: openai client 설정

model_client = model.client()
temperature = st.sidebar.slider("temperature", 0.0, 1.0, 0.4)

tool_calling_manager = None
if use_tool:
    tool_calling_manager = ToolCallingManager(azure_client=model_client, model_name=model.base_model_name())


    

#### Azure OpenAI Client 생성
def get_azure_openai_client(messages):
    tools =[]
    if use_tool:
        tools = tool_calling_manager.tool_list

    try:
        rag_params={
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": os.getenv("AZURE_AI_SEARCH_ENDPOINT"),
                            "index_name": os.getenv("INDEX_NAME", "aisearch"),
                            "authentication": {
                                "type": "api_key",
                                "key": os.getenv("AZURE_AI_SEARCH_API_KEY")
                            }
                        }
                    }
                ]
            }
            
        response = model.chat(
            tools=tools,
            messages=messages,
            temperature=temperature,
            extra_body=rag_params,
        )

        final_response = None

        # Tool 호출이 있는 경우
        if response.choices[0].message.tool_calls:
            # Tool 호출이 있는 경우 처리
            # ChatCompletionMessage 객체를 딕셔너리로 변환
            assistant_message = {
                "role": "assistant",
                "content": response.choices[0].message.content or "",
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
                tool_response_str = ""
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
                        tool_response_str = json.dumps({"error": str(e)})
                                
                # Tool 응답을 메시지에 추가
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_response_str,
                }
                messages.append(tool_message)
            # 최종 응답 생성
            final_response = model.chat(
                messages=messages,
                temperature=temperature,
                extra_body=rag_params,
            )

        # Tool 호출이 없는 경우
        else:
            final_response = response
        
        # 참고한 청크(citations) 표시 (메시지 내 마커 [docN] 기반 필터링)
        try:
            import re
            msg = final_response.choices[0].message
            ctx = getattr(msg, "context", None)
            content_text = msg.content or ""
            doc_markers = set(int(m) for m in re.findall(r"\[doc(\d+)\]", content_text))
            if isinstance(ctx, dict):
                all_citations = ctx.get("citations", []) or []
                # [docN] 마커가 있으면 해당 인덱스만(1-based) 필터링, 없으면 전체 노출(혹은 상위 3개 등)
                if doc_markers:
                    citations = [c for i, c in enumerate(all_citations, start=1) if i in doc_markers]
                else:
                    citations = all_citations
                if citations:
                    with st.chat_message("assistant"):
                        with st.expander("🔗 참고한 문서/청크", expanded=False):
                            for idx, cite in enumerate(citations, start=1):
                                title = cite.get("title") or cite.get("filepath") or f"Citation {idx}"
                                url = cite.get("url")
                                filepath = cite.get("filepath")
                                chunk_id = cite.get("chunk_id")
                                # 표시용 파일명 (filepath가 있으면 basename 사용)
                                try:
                                    filename = os.path.basename(filepath) if filepath else title
                                except Exception:
                                    filename = title
                                content = cite.get("content", "")
                                if content:
                                    exp_title = f"미리보기 - {filename} (chunkid: {chunk_id})" if chunk_id is not None else f"미리보기 - {filename}"
                                    with st.expander(exp_title, expanded=False):
                                        st.text(content)
        except Exception:
            pass

        return final_response.choices[0].message.content

    except (HttpResponseError, ClientAuthenticationError, ResourceNotFoundError) as e:
        st.error(f"Azure OpenAI API 호출 중 오류가 발생했습니다: {e}")
        return f"오류: {e}" 
    except Exception as e:
        st.error(f"OpenAI API 호출 중 오류가 발생했습니다: {e}")
        return f"오류: {e}"



#### NOTE: 채팅 메시지 표시 
for message in st.session_state.messages:
    if not message:
        continue
    elif message["role"] == "system":
        continue
    elif message["role"] == "tool":
        # 툴 호출 결과 표시
        with st.chat_message("assistant"):
            with st.expander(f'Tool Calling: {message.get("name", "unknown")}', expanded=False):
                st.write(message["content"])
    elif message.get("tool_calls"):
        # 툴 호출 요청 메시지는 표시하지 않거나 간단히 표시
        continue
    else:  # 일반 메시지인 경우
        st.chat_message(message["role"]).write(message["content"])


#### NOTE 사용자 채팅 입력 및 chat message 추가
if user_input := st.chat_input("메시지를 입력하세요"):

    st.session_state.messages.append({"role": "user","content": user_input})
    st.chat_message("user").markdown(user_input)

    with st.spinner("GPT가 응답하는 중..."):
        assistant_response = get_azure_openai_client(st.session_state.messages)
    
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    st.chat_message("assistant").markdown(assistant_response)