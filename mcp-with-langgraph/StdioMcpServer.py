from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-server")

@mcp.tool()
def  add(a:int, b:int) -> int:
    """Add two numbers"""
    return a+b

def multiply(a:int, b:int) -> int:
    return a * b


if __name__ =="__main__":
    mcp.run(transport="sse")

