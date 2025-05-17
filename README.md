# MCP Dataset Analyzer

This project provides a web-based interface for analyzing web content and Kaggle datasets using an LLM connected to an MCP server.

## Architecture

The system consists of three main components:

1. **Frontend**: A Next.js application with a dark-mode UI built using React, TypeScript, and Tailwind CSS with shadcn components.
2. **API Layer**: Next.js API routes that handle requests between the frontend and backend services.
3. **MCP Server**: A Python server using FastMCP for providing tools and resources to analyze datasets.

```
┌───────────┐       ┌──────────────┐       ┌─────────────┐
│           │       │              │       │             │
│  Frontend │──────▶│  API Layer   │──────▶│  MCP Server │
│           │       │              │       │             │
└───────────┘       └──────────────┘       └─────────────┘
                           │                       │
                           ▼                       ▼
                    ┌──────────────┐       ┌─────────────┐
                    │              │       │             │
                    │   Kaggle     │       │   Dataset   │
                    │   Datasets   │       │   Tools     │
                    │              │       │             │
                    └──────────────┘       └─────────────┘
```

## Functionality

- **URL Analysis**: Analyze any web URL to extract content insights
- **Dataset Downloading**: Download and preview Kaggle datasets 
- **LLM Analysis**: Process datasets using LLM with MCP server tools
- **Tool Integration**: Showcase MCP server capabilities in the UI

## Components

### Frontend (`/frontend`)

The frontend provides a clean user interface for entering URLs and viewing analysis results.

### MCP Server (`/mcp`)

The MCP (Machine-Callable Program) server provides tools and resources for:
- Adding numbers
- Analyzing dataset columns and inferring data types
- Identifying ML tasks based on dataset structure
- Providing personalized greetings and dataset information

## How To Run

1. **Start the MCP Server**
   ```bash
   cd mcp
   pip install -r requirements.txt
   python server.py http 8000
   ```

2. **Start the Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. **Visit the Application**
   Open your browser to `http://localhost:3000`

## Integration Flow

1. User enters a URL in the frontend
2. For regular URLs, the system analyzes the web content
3. For Kaggle dataset URLs:
   - The system downloads and displays a dataset preview
   - The downloaded dataset is sent to the LLM with MCP tools
   - The LLM analyzes the dataset using MCP tools and resources
   - Analysis results are displayed, showing which MCP tools were used