# AI Research Agent with MCP Integration

![MCP Integration](https://www.cursor.sh/brand/cursor-bg-dark.jpg)

## Overview
AI Research Agent is a streamlined assistant designed for research tasks with MCP server integration. Using LangGraph's multiserver client technology, this agent connects to external MCP tools while providing web search capabilities through Tavily.

## Features

- **Web Search**: Utilizes Tavily Search for finding facts and current information
- **MCP Integration**: Connects to the MCP server to access Google tools
- **Guardrails**: Built-in safety layer for input validation, sensitive operation confirmation, and unsafe content blocking
- **FastAPI Backend**: Clean, efficient API endpoints
- **Docker Support**: Ready for container deployment

## Available Tools

| Tool Name | Purpose | API Key Required | Best For |
|-----------|---------|------------------|----------|
| `web_search` | Web search | ✅ TAVILY_API_KEY | Current information, news |
| `mcp_google-tools_search_gmail_messages` | Gmail search | ✅ OAuth token | Searching emails |
| `mcp_google-tools_list_gmail_messages` | Gmail listing | ✅ OAuth token | Listing emails |
| `mcp_google-tools_list_gmail_labels` | Gmail labels | ✅ OAuth token | Email organization |

## Project Structure

```
├── app.py                 # FastAPI main application
├── my_agent/
│   ├── agent.py          # LangGraph workflow with MCP client
│   └── utils/
│       ├── nodes.py      # Agent/tool nodes
│       ├── state.py      # Agent state definition
│       ├── research_tools.py  # Tavily search tool
│       └── auth_setup.py # API key setup
├── requirements.txt     # Dependencies
└── Dockerfile          # Docker configuration
```

## Setup

1. Create a `.env` file with your API keys:
   ```
   TAVILY_API_KEY=your_tavily_key
   OPENAI_API_KEY=your_openai_key
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

## Using Docker

1. Build the container:
   ```bash
   docker build -t ai-research-agent .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 -e TAVILY_API_KEY=your_tavily_key -e OPENAI_API_KEY=your_openai_key ai-research-agent
   ```

## MCP Integration

The agent connects to the MCP server at `http://52.165.80.198:8837/mcp` to access Google tools. The connection status is visible in the server logs and can be verified at the `/health` and `/api-status` endpoints.

## Guardrails

The agent includes built-in safety mechanisms:

### Input Validation
- Blocks empty messages
- Enforces 1000 character limit
- Validates message format

### Unsafe Content Blocking
Automatically blocks requests containing:
- `hack`, `illegal`, `steal`, `password`, `exploit`

Example:
```
User: "Help me hack into a system"
Agent: ⚠️ This request is out of scope. I cannot help with: 'hack'
```

### Sensitive Operation Confirmation
Requires explicit confirmation for:
- `delete`, `remove`, `send email`, `send message`

Example:
```
User: "Delete all my old emails"
Agent: ⚠️ This action involves 'delete'. Please confirm you want to proceed by adding 'confirmed' to your message.

User: "Delete all my old emails confirmed"
Agent: [Proceeds with action]
```

### Testing Guardrails
Run the test suite:
```bash
python test_guardrails.py
```