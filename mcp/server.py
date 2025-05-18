from agents.trainer import generate_and_run_script
from mcp.server.fastmcp import FastMCP
import sys

# 1️⃣  Instantiate the server
mcp = FastMCP("Demo", version="0.0.1")


# 2️⃣  Register a tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def train_on_dataset(dataset_path: str,
                     task: str,
                     metric: str,
                     target: str,
                     output_dir: str = "results"):
    """
    This script defines a framework for generating and running machine learning training scripts based on a dataset and task parameters, using the Anthropic API for AI-assisted script generation. It includes functionality for:

    - Generating a training script tailored to a specific dataset and task (e.g., classification).
    - Running the generated training script to train a model.
    - Handling errors and retries in case the training script fails, with automatic regeneration of training scripts based on error contexts.

    Example usage:
        If you want to generate and run a script for classification on a CSV dataset, call `train_on_dataset` like this:
        generate_and_run_script("path_to_dataset.csv", "classification", "accuracy", "label")
    """

    return generate_and_run_script(dataset_path=dataset_path,
                                   task=task,
                                   metric=metric,
                                   target=target,
                                   output_dir=output_dir)


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