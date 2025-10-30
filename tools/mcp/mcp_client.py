from enum import Enum

from pydantic import BaseModel, Field
from typing import Optional, Literal
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from pprint import pprint


class TransportType(str, Enum):
    STDIO = 'stdio'
    SSE = 'sse'
    WEBSOCKET = 'websocket'
    STREAMABLEHTTP = 'streamable-http'


class McpServerInfo(BaseModel):
    name: str
    transport_type: TransportType

    model_config = {
        "arbitrary_types_allowed": True
    }


class McpStreamableHTTPServerInfo(McpServerInfo):
    transport_type: TransportType = Field(default=TransportType.STREAMABLEHTTP, Literal=True)
    url: str
    headers: Optional[dict] = None
    timeout: Optional[float] = None
    sse_read_timeout: Optional[float] = None
    auth: Optional[dict] = None


class McpClient:

    def __init__(self, mcp_server_info: McpServerInfo):
        # MCP 서버 정보 initializing
        self.name = mcp_server_info.name
        self.transport_type = mcp_server_info.transport_type
        if isinstance(mcp_server_info, McpStreamableHTTPServerInfo):  # StreamableHTTP 방식인 경우
            self.url = mcp_server_info.url
            self.headers = mcp_server_info.headers
            self.timeout = mcp_server_info.timeout
            self.sse_read_timeout = mcp_server_info.sse_read_timeout
            self.auth = mcp_server_info.auth
        else:
            raise ValueError("mcp_server_info not a McpServerInfo")
        # session initializing
        self.session: Optional[ClientSession] = None



    async def async_streamablehttp_call_tool(self, tool_name, tool_args):
        async with streamablehttp_client(url=self.url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                await session.initialize()
                # Call a tool (when LLM requests it)
                result = await session.call_tool(tool_name, arguments=tool_args)
                return result

    async def tool_list(self) -> list:
        async with streamablehttp_client(url=self.url) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the connection
                await session.initialize()
                # List available tools
                tools_result = await session.list_tools()
                print('------------------------------------')
                pprint(f"Available tools: {', '.join([t.name for t in tools_result.tools])}")
                print('------------------------------------')
                return tools_result