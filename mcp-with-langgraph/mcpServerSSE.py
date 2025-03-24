from mcp.server.lowlevel import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.requests import Request

import mcp.types as types
import uvicorn, asyncio


from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-server")

@mcp.tool()
async def  add(a:int, b:int) -> int:
    """Add two numbers"""
    return a+b

@mcp.tool()
async def multiply(a:int, b:int) -> int:
    """Multiply two numbers
    """
    
    return a * b


def create_starlette_app(mcp_server: Server, *, debug:bool = False) -> Starlette:
    """Create a Starlette application that can server the provided mcp Server with SSE.

    Args:
        mcp_server (Server): _description_
        debug (bool, optional): _description_. Defaults to False.

    Returns:
        Starlette: _description_
    """
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream, 
                write_stream, 
                mcp_server.create_initialization_options()
            )

    return Starlette(
        debug = debug, 
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ]
    )
    

if __name__ == "__main__":
    mcp_server = mcp._mcp_server
    
    starlette_app = create_starlette_app(mcp_server, debug=True)
    uvicorn.run(starlette_app, host="0.0.0.0", port=8000)
