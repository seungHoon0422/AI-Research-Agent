import os 
from tools.mcp.mcp_client import McpClient, McpStreamableHTTPServerInfo
from dotenv import load_dotenv

load_dotenv()

def build_mcp_client(server_name: str, server_url: str) -> McpClient:
    mcp_client = McpClient(
        mcp_server_info=McpStreamableHTTPServerInfo(
            name=server_name,   
            url=server_url,
        )
    )
    return mcp_client
    