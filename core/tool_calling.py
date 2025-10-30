# Tool Calling 모듈
# Azure OpenAI Function Calling을 처리하는 전용 모듈

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from mcp import ListToolsResult
from openai import AzureOpenAI
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError, ResourceNotFoundError
import streamlit as st
from tools.mcp.mcp_service import build_mcp_client
from tools.mcp.mcp_client import McpClient
from tools.current_time import GET_CURRENT_TIME
import asyncio

class ToolCallingManager:
    """Azure OpenAI Function Calling을 관리하는 클래스"""
    
    def __init__(self, azure_client: AzureOpenAI, model_name: str):
        self.client = azure_client
        self.model_name = model_name

        self.tool_client_mapper:dict[str,Any] = {}
        self.server_client_mapper:dict[str,Any] = {}
        self.tool_list:list = []
        self.available_tools = self._register_tools()
        self.init_mcp_servers()    


    def init_mcp_servers(self):

        builtin_tools = [GET_CURRENT_TIME]
        tavily_mcp_server_url = os.getenv("TAVILY_MCP_URL")
        paper_search_mcp_server_url = os.getenv("PAPER_SEARCH_MCP_SERVER_URL")

        tavily_mcp_client = build_mcp_client("tavily", tavily_mcp_server_url)
        paper_search_mcp_client = build_mcp_client("paper_search", paper_search_mcp_server_url)
        
        self.server_client_mapper = {
            "tavily": tavily_mcp_client,
            "paper_search": paper_search_mcp_client,
        }

        converted_mcp_tools = []
        tavily_tools, paper_search_tools = [], []

        # Tool List 호출
        if not self.tool_list or len(self.tool_list) <= 0:
            # tavily tool list 목록 조회
            tavily_tools:ListToolsResult = asyncio.run(tavily_mcp_client.tool_list())
            for tavily_tool in tavily_tools.tools:
                converted_tool = self.convert_mcp_tool_to_openai(tavily_tool)
                converted_mcp_tools.append(converted_tool)
                self.tool_client_mapper[tavily_tool.name] = tavily_mcp_client

            # paper search tool list 목록 조회
            paper_search_tools:ListToolsResult = asyncio.run(paper_search_mcp_client.tool_list())
            for paper_search_tool in paper_search_tools.tools:
                converted_tool = self.convert_mcp_tool_to_openai(paper_search_tool)
                converted_mcp_tools.append(converted_tool)
                self.tool_client_mapper[paper_search_tool.name] = paper_search_mcp_client

            self.tool_list = builtin_tools + converted_mcp_tools
        

    def get_mcp_client(self, tool_name: str) -> McpClient:
        return self.tool_client_mapper[tool_name]

    def _register_tools(self) -> Dict[str, Any]:
        """사용 가능한 도구들을 등록"""
        return {
            "get_current_time": {
                "function": self.get_current_time,
                "definition": {
                    "type": "function",
                    "function": {
                        "name": "get_current_time",
                        "description": "Get the current time in a given location",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The city name, e.g. Seoul, Tokyo, Paris",
                                },
                            },
                            "required": ["location"],
                        },
                    }
                }
            },
            "tavily_search": {
                "function": self.tavily_search,
                "definition": {
                    "type": "function",
                    "function": {
                        "name": "tavily_search",
                        "description": "Search the web for current information",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The search query",
                                },
                                "max_results": {
                                    "type": "integer",
                                    "description": "Maximum number of results (default: 5)",
                                    "default": 5
                                }
                            },
                            "required": ["query"],
                        },
                    }
                }
            }
        }
    
    def get_current_time(self, location: str) -> str:
        """특정 위치의 현재 시간을 반환"""
        print(f"get_current_time called with location: {location}")
        
        # 간단한 타임존 매핑
        timezone_map = {
            "seoul": "Asia/Seoul",
            "서울": "Asia/Seoul",
            "tokyo": "Asia/Tokyo",
            "도쿄": "Asia/Tokyo",
            "paris": "Europe/Paris",
            "파리": "Europe/Paris",
            "london": "Europe/London",
            "런던": "Europe/London",
            "san francisco": "America/Los_Angeles",
            "샌프란시스코": "America/Los_Angeles",
            "los angeles": "America/Los_Angeles",
            "로스앤젤레스": "America/Los_Angeles",
            "new york": "America/New_York",
            "뉴욕": "America/New_York",
            "chicago": "America/Chicago",
            "시카고": "America/Chicago",
            "utc": "UTC"
        }
        
        location_lower = location.lower()
        tz_name = timezone_map.get(location_lower, "UTC")
        
        try:
            current_time = datetime.now(ZoneInfo(tz_name))
            result = {
                "location": location,
                "timezone": tz_name,
                "current_time": current_time.strftime("%Y-%m-%d %H:%M:%S %Z"),
                "formatted_time": current_time.strftime("%I:%M %p")
            }
            print(f"Timezone found for {location}: {tz_name}")
            return json.dumps(result)
        except Exception as e:
            print(f"Error getting time for {location}: {e}")
            return json.dumps({"location": location, "error": str(e)})
    
    def tavily_search(self, query: str, max_results: int = 5) -> str:
        """Tavily를 사용하여 웹 검색"""
        print(f"tavily_search called with query: {query}")
        
        tavily_url = os.getenv("TAVILY_MCP_URL", "http://localhost:8000")
        api_key = os.getenv("TAVILY_API_KEY", "")
        
        try:
            import requests
            response = requests.post(
                f"{tavily_url}/search",
                json={
                    "query": query,
                    "max_results": max_results
                },
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": api_key
                } if api_key else {"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                return json.dumps(response.json())
            else:
                return json.dumps({"error": f"Search failed with status {response.status_code}"})
        except Exception as e:
            print(f"Error in tavily_search: {e}")
            return json.dumps({"error": str(e)})
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """사용 가능한 도구 정의들을 반환"""
        return [tool_info["definition"] for tool_info in self.available_tools.values()]
    
    def execute_tool_call(self, tool_call, tool_name, tool_args) -> str:
        """단일 도구 호출을 실행"""
        if tool_name == "get_current_time":
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            if function_name not in self.available_tools:
                return json.dumps({"error": f"Unknown function: {function_name}"})
            
            tool_function = self.available_tools[function_name]["function"]
            
            try:
                # 함수 실행
                result = tool_function(**function_args)
                return result
            except Exception as e:
                return json.dumps({"error": f"Function execution failed: {str(e)}"})
        else:
            mcp_client = self.get_mcp_client(tool_name)
            tool_response = asyncio.run(mcp_client.async_streamablehttp_call_tool(tool_name, tool_args))
            return tool_response.content
    
    def process_chat_with_tools(self, messages: List[Dict[str, str]], show_process: bool = True) -> str:
        """도구를 사용한 채팅 처리"""
        try:
            # 첫 번째 API 호출: 모델에게 함수 사용 요청
            if show_process:
                st.info("🤖 AI가 응답을 생성하고 있습니다...")
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.get_tool_definitions(),
                tool_choice="auto",
            )
            
            response_message = response.choices[0].message
            messages.append(response_message)
            
            # Tool 호출이 있는 경우 처리
            if response_message.tool_calls:
                if show_process:
                    st.info(f"🔧 {len(response_message.tool_calls)}개의 도구를 호출합니다...")
                
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    # Tool 호출 정보 표시
                    if show_process:
                        with st.expander(f"🔧 {function_name} 호출 중...", expanded=True):
                            st.write("**매개변수:**")
                            st.json(function_args)
                    
                    # 도구 실행
                    function_response = self.execute_tool_call(tool_call)
                    
                    # Tool 실행 결과 표시
                    if show_process:
                        with st.expander(f"✅ {function_name} 실행 결과", expanded=True):
                            try:
                                result_data = json.loads(function_response)
                                st.json(result_data)
                            except:
                                st.text(function_response)
                    
                    # Tool 응답을 메시지에 추가
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": function_response,
                    })
                
                # 두 번째 API 호출: 최종 응답 생성
                if show_process:
                    st.info("🤖 도구 결과를 바탕으로 최종 답변을 생성합니다...")
                
                final_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                )
                return final_response.choices[0].message.content
            
            # Tool 호출이 없는 경우 바로 반환
            return response_message.content
            
        except (HttpResponseError, ClientAuthenticationError, ResourceNotFoundError) as e:
            st.error(f"Azure OpenAI API 호출 중 오류가 발생했습니다: {e}")
            return f"오류: {e}"
        except Exception as e:
            st.error(f"예상치 못한 오류가 발생했습니다: {e}")
            return f"오류: {e}"
    
    def process_chat_without_tools(self, messages: List[Dict[str, str]]) -> str:
        """도구 없이 채팅 처리"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"API 호출 중 오류가 발생했습니다: {e}")
            return f"오류: {e}"



    def convert_mcp_tool_to_openai(self, mcp_tool):
        """MCP Tool을 Azure OpenAI 형식으로 변환"""
        try:
            # 기본 구조
            tool_def = {
                "type": "function",
                "function": {
                    "name": mcp_tool.name,
                    "description": getattr(mcp_tool, 'description', f"Tool: {mcp_tool.name}"),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            
            # inputSchema가 있는 경우 처리
            if hasattr(mcp_tool, 'inputSchema') and mcp_tool.inputSchema:
                schema = mcp_tool.inputSchema
                
                # properties 처리
                if isinstance(schema, dict) and 'properties' in schema and schema['properties']:
                    for prop_name, prop_info in schema['properties'].items():
                        param_def = {
                            "type": prop_info.get('type', 'string'),
                            "description": prop_info.get('description', f"Parameter: {prop_name}")
                        }
                        
                        # 배열 타입인 경우 items 속성 추가
                        if prop_info.get('type') == 'array' and 'items' in prop_info:
                            param_def['items'] = prop_info['items']
                        
                        tool_def["function"]["parameters"]["properties"][prop_name] = param_def
                
                # required 처리
                if isinstance(schema, dict) and 'required' in schema and schema['required']:
                    tool_def["function"]["parameters"]["required"] = schema['required']
            
            return tool_def
        except Exception as e:
            print(f"Tool 변환 오류: {e}")
            # 기본 구조라도 반환
            return {
                "type": "function",
                "function": {
                    "name": mcp_tool.name,
                    "description": f"Tool: {mcp_tool.name}",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }

    async def get_arxiv_search_tools(self):
        try:
            tools_result = await self.arxiv_search_client.tool_list()
            return tools_result.tools
        except Exception as e:
            st.error(f"Arxiv 도구 로드 실패: {e}")
            return []

    async def get_tavily_tools(self):
        try:
            tools_result = await self.tavily_mcp_client.tool_list()
            # MCP Tool을 Azure OpenAI 형식으로 변환
            converted_tools = []
            for tool in tools_result.tools:
                converted_tool = self.convert_mcp_tool_to_openai(tool)
                converted_tools.append(converted_tool)
            return converted_tools
        except Exception as e:
            st.error(f"Tavily 도구 로드 실패: {e}")
            return []

    # if self.tavily_tools == []:
    #     tavily_tools = asyncio.run(get_tavily_tools())
