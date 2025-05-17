from mcp.server.fastmcp import FastMCP
import sys
from typing import Dict, List, Any, Optional
from dataset_tools import DatasetTools
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import contextlib

# 1️⃣  Instantiate the server
mcp = FastMCP("Demo", version="0.0.1")

# 2️⃣  Register tools
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.tool()
def analyze_dataset_columns(columns: List[str], sample_data: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Analyze the columns in a dataset and infer their data types.
    
    Args:
        columns: List of column names in the dataset
        sample_data: Sample rows of data from the dataset
        
    Returns:
        Dictionary mapping column names to their inferred data types
    """
    return DatasetTools.analyze_data_types(columns, sample_data)

@mcp.tool()
def identify_ml_task(columns: List[str], sample_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Identify potential machine learning tasks for a dataset based on its structure.
    
    Args:
        columns: List of column names in the dataset
        sample_data: Sample rows of data from the dataset
        
    Returns:
        Dictionary with suggested ML tasks and potential target column
    """
    data_types = DatasetTools.analyze_data_types(columns, sample_data)
    target_column = DatasetTools.identify_target_column(columns)
    suggested_tasks = DatasetTools.suggest_ml_tasks(columns, data_types)
    
    return {
        "data_types": data_types,
        "target_column": target_column,
        "suggested_tasks": suggested_tasks
    }

# 3️⃣  Register resources
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.resource("dataset://{owner}/{name}")
def get_dataset_info(owner: str, name: str) -> Dict[str, Any]:
    """
    Get information about a dataset based on owner and name.
    
    Args:
        owner: The dataset owner/creator
        name: The name of the dataset
        
    Returns:
        Dictionary with dataset information
    """
    # This would typically fetch data from a database or API
    # For this demo, we'll return mock information
    return {
        "owner": owner,
        "name": name,
        "full_path": f"{owner}/{name}",
        "description": f"Mock description for the {name} dataset by {owner}",
        "last_updated": "2023-01-01",
        "size": "1.2 GB",
        "file_count": 3,
        "tags": ["demo", "mock", "sample"]
    }

# Create a lifespan context manager for the FastAPI app
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(mcp.session_manager.run())
        yield

# 4️⃣  Entrypoint: choose transport from CLI flag
if __name__ == "__main__":
    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "stdio"

    if mode == "http":
        # Create FastAPI app with the lifespan manager
        app = FastAPI(lifespan=lifespan)
        
        # Add CORS middleware to allow requests from the frontend
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000"],  # Frontend URL
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Mount the MCP app using the streamable_http_app method
        app.mount("/mcp", mcp.streamable_http_app())
        
        # Add a ping endpoint for health checks
        @app.get("/mcp/ping")
        def ping():
            return {"status": "ok"}
        
        # Run the server
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        uvicorn.run(app, host="0.0.0.0", port=port)
    else:
        # desktop-friendly stdio transport
        mcp.run(transport="stdio")