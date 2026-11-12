from contextlib import asynccontextmanager
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from heartsense.config import settings

@asynccontextmanager
async def get_mcp_session():
    url = settings.mcp_server_url
    token = settings.mcp_auth_token
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    
    async with streamablehttp_client(url, headers=headers) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            # Keep the session open while the tools are yielded
            yield await load_mcp_tools(session)