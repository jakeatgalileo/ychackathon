# MCP Server with Mock Evaluation Model

This is a Machine-Callable Program (MCP) server implementation that includes a mock evaluation model for Yelp reviews.

## Setup

1. Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

To start the MCP server with HTTP transport:
```bash
python server.py
```

The server will be available at http://localhost:8000/mcp

## Evaluation Model Tool

The server includes a mock evaluation model that randomly generates scores (1-5) for Yelp reviews in the `datasets/yelp_reviews_test.csv` file.

### Testing the Evaluation Model

You can test the mock evaluation model directly without starting the server:
```bash
python test_evaluation_model.py
```

### Using the MCP Client

To see how to call the evaluation model via the MCP API:
```bash
# First make sure the server is running in a separate terminal
python server.py

# Then in another terminal
python mcp_client_example.py
```

### API Usage

#### Evaluating a Specific Row

```json
POST http://localhost:8000/mcp
Content-Type: application/json

{
  "method": "tool/evaluation_model",
  "params": {
    "row_index": 0
  }
}
```

#### Evaluating All Rows

```json
POST http://localhost:8000/mcp
Content-Type: application/json

{
  "method": "tool/evaluation_model",
  "params": {}
}
```

## Available MCP Endpoints

1. `tool/add` - Adds two numbers
2. `tool/get_profile_info` - Returns a profile info string
3. `tool/evaluation_model` - Evaluates Yelp reviews with scores from 1-5
4. `resource/greeting/{name}` - Returns a personalized greeting