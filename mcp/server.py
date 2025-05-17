from mcp.server.fastmcp import FastMCP
import sys

mcp = FastMCP("Demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mode = (sys.argv[1] if len(sys.argv) > 1 else "stdio").lower()
    if mode == "http":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        mcp.run(transport="http", port=port)
    else:
        # Default to stdio mode
        mcp.run(transport="stdio")