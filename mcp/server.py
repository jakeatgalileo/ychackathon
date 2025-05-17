from mcp.server.fastmcp import FastMCP
import sys

# 1️⃣  Instantiate the server
mcp = FastMCP("Demo", version="0.0.1")

# 2️⃣  Register a tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# 3️⃣  Register a resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

# 4️⃣  Entrypoint: choose transport from CLI flag
if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "stdio"

    if mode == "http":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        # tiny built-in ASGI server; no FastAPI/uvicorn needed
        mcp.run(transport="http", host="0.0.0.0", port=port)
        # now listening on  http://localhost:8000/mcp
    else:
        # desktop-friendly stdio transport
        mcp.run(transport="stdio")