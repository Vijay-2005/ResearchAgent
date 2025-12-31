# 🤖 AI Research Agent with MCP Integration

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Latest-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*An intelligent research assistant powered by LangGraph and Model Context Protocol (MCP) integration*

[Features](#-features) • [Quick Start](#-quick-start) • [API Documentation](#-api-documentation) • [Architecture](#-architecture) • [Deployment](#-deployment)

</div>

---

## 📖 Overview

**AI Research Agent** is a production-ready, AI-powered research assistant that combines the power of LangGraph's state machine architecture with Model Context Protocol (MCP) integration. It provides intelligent web search capabilities, external tool integration via MCP servers, and built-in safety guardrails for secure operation.

### Why This Project?

- **🔌 Extensible Architecture**: Built on LangGraph for flexible agent workflows
- **🛡️ Production-Ready**: Includes guardrails, error handling, and comprehensive logging
- **🌐 MCP Integration**: Connect to external tools and services via standardized MCP protocol
- **🔍 Intelligent Search**: Powered by Tavily for accurate, up-to-date information retrieval
- **🚀 Easy Deployment**: Docker support with FastAPI backend for seamless deployment

---

## ✨ Features

### Core Capabilities

| Feature | Description | Status |
|---------|-------------|--------|
| **Web Search** | Real-time web search using Tavily API | ✅ Active |
| **MCP Integration** | Connect to external MCP servers (Google Workspace, Rube, etc.) | ✅ Active |
| **Conversation Memory** | Persistent conversation history across sessions | ✅ Active |
| **Safety Guardrails** | Input validation, content filtering, and operation confirmation | ✅ Active |
| **Multi-Model Support** | OpenAI GPT models (extensible to Anthropic) | ✅ Active |
| **RESTful API** | FastAPI-powered endpoints with automatic documentation | ✅ Active |

### 🛡️ Safety Features

- **Input Validation**: Empty message detection, length limits (1000 chars)
- **Content Filtering**: Blocks harmful keywords (hack, illegal, steal, etc.)
- **Operation Confirmation**: Requires explicit confirmation for sensitive actions
- **Error Handling**: Graceful degradation with detailed error messages
- **Audit Logging**: Comprehensive logging for debugging and monitoring

### 🔧 Available Tools

#### Research Tools
- `web_search` - Tavily-powered web search for current information

#### MCP Tools (Rube Integration)
The agent connects to MCP servers to access external tools dynamically. Current integration supports:
- Google Workspace tools (Gmail, Calendar, Drive)
- Custom MCP server integrations
- Extensible to any MCP-compatible service

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- API keys for:
  - OpenAI API
  - Tavily API (for web search)
  - MCP server authentication (if using Rube or other services)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Vijay-2005/ResearchAgent.git
   cd ResearchAgent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # Required API Keys
   OPENAI_API_KEY=sk-your-openai-api-key
   TAVILY_API_KEY=tvly-your-tavily-api-key
   
   # Optional: Configure port (default: 8000)
   PORT=8000
   API_URL=http://localhost:8000
   
   # Optional: LangSmith tracing
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your-langsmith-key
   LANGCHAIN_PROJECT=ai-research-agent
   ```

5. **Run the application**
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

6. **Access the API**
   - API Root: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## 📡 API Documentation

### Core Endpoints

#### 1. Chat with Agent
**POST** `/chat`

Send a message to the AI agent and receive a response.

```json
{
  "message": "Search for latest AI research papers",
  "conversation_id": "conv_1",
  "model": "openai"
}
```

**Response:**
```json
{
  "conversation_id": "conv_1",
  "messages": [
    {"role": "user", "content": "Search for latest AI research papers"},
    {"role": "assistant", "content": "Here are the latest AI research papers..."}
  ]
}
```

#### 2. Health Check
**GET** `/health`

Check API and MCP connection status.

```json
{
  "api": "healthy",
  "mcp": "connected",
  "TAVILY_API_KEY": true,
  "OPENAI_API_KEY": true
}
```

#### 3. API Status
**GET** `/api-status`

Detailed status of all configured APIs and tools.

```json
{
  "OPENAI_API_KEY": {
    "configured": true,
    "valid_format": true
  },
  "mcp": {
    "configured": true,
    "connected": true,
    "url": "https://rube.app/mcp",
    "mcp_tools": ["tool1", "tool2"]
  },
  "guardrails": {
    "enabled": true,
    "features": ["Input validation", "Content filtering"]
  }
}
```

#### 4. Conversation Management
**GET** `/conversations` - List all conversation IDs

**DELETE** `/conversations/{conversation_id}` - Delete a specific conversation

### Example Usage

```python
import requests

# Start a conversation
response = requests.post("http://localhost:8000/chat", json={
    "message": "What are the latest trends in machine learning?",
    "model": "openai"
})

data = response.json()
conversation_id = data["conversation_id"]

# Continue the conversation
response = requests.post("http://localhost:8000/chat", json={
    "message": "Can you search for more details on transformer models?",
    "conversation_id": conversation_id,
    "model": "openai"
})
```

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
│                         (app.py)                         │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                  LangGraph Workflow                      │
│                     (agent.py)                           │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐     │
│  │  Agent   │─────▶│  Tools   │─────▶│  Agent   │     │
│  │  Node    │      │  Node    │      │  Node    │     │
│  └──────────┘      └──────────┘      └──────────┘     │
└───────────────┬───────────────────────────┬─────────────┘
                │                           │
                ▼                           ▼
┌───────────────────────────┐   ┌──────────────────────┐
│   Research Tools          │   │   MCP Client         │
│   - Tavily Search         │   │   - Rube Server      │
│   - Web Search            │   │   - Google Tools     │
└───────────────────────────┘   └──────────────────────┘
```

### Project Structure

```
ai-research-agent/
├── app.py                      # FastAPI application entry point
├── my_agent/
│   ├── __init__.py
│   ├── agent.py               # LangGraph workflow definition
│   └── utils/
│       ├── __init__.py
│       ├── auth_setup.py      # API key configuration
│       ├── guardrails.py      # Safety and validation layer
│       ├── langsmith_setup.py # Optional tracing setup
│       ├── mcp_client.py      # MCP server connection
│       ├── nodes.py           # Agent and tool execution nodes
│       ├── research_tools.py  # Tavily search integration
│       ├── state.py           # Agent state definition
│       └── tools.py           # Tool management utilities
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── .dockerignore             # Docker ignore patterns
├── langgraph.json            # LangGraph configuration
├── render.yaml               # Render.com deployment config
└── README.md                 # This file
```

### Key Components

#### 1. **Agent Workflow** (`agent.py`)
- Defines the state machine using LangGraph
- Manages conversation flow between agent and tools
- Handles decision-making and tool selection

#### 2. **Node Functions** (`nodes.py`)
- `call_model`: Invokes the LLM with current state
- `tool_node`: Executes selected tools (web search, MCP tools)
- `should_continue`: Determines workflow continuation

#### 3. **State Management** (`state.py`)
- Maintains conversation history
- Tracks tool execution results
- Preserves context across turns

#### 4. **MCP Integration** (`mcp_client.py`)
- Connects to external MCP servers
- Dynamically loads available tools
- Manages authentication and headers

#### 5. **Guardrails** (`guardrails.py`)
- Validates user inputs
- Blocks unsafe content
- Requires confirmation for sensitive operations

---

## 🔒 Security & Guardrails

### Input Validation
```python
# Automatic validation of all user inputs
✅ Length limit: 1000 characters
✅ Empty message detection
✅ Format validation for lists and strings
```

### Content Safety

**Blocked Keywords:**
- `hack`, `illegal`, `steal`, `password`, `exploit`

**Example:**
```
User: "Help me hack a system"
Agent: ⚠️ This request is out of scope. I cannot help with: 'hack'
```

### Sensitive Operation Confirmation

**Protected Actions:**
- `delete`, `remove`, `send email`, `send message`

**Example Flow:**
```
User: "Delete all my old emails"
Agent: ⚠️ This action involves 'delete'. Please confirm by adding 'confirmed'.

User: "Delete all my old emails confirmed"
Agent: ✅ Proceeding with deletion...
```

---

## 🐳 Deployment

### Docker Deployment

1. **Build the image**
   ```bash
   docker build -t ai-research-agent .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 \
     -e OPENAI_API_KEY=your-key \
     -e TAVILY_API_KEY=your-key \
     ai-research-agent
   ```

3. **Using Docker Compose**
   ```yaml
   version: '3.8'
   services:
     ai-agent:
       build: .
       ports:
         - "8000:8000"
       environment:
         - OPENAI_API_KEY=${OPENAI_API_KEY}
         - TAVILY_API_KEY=${TAVILY_API_KEY}
       restart: unless-stopped
   ```

### Cloud Deployment

#### Render.com
```yaml
# render.yaml included in project
services:
  - type: web
    name: ai-research-agent
    runtime: docker
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: TAVILY_API_KEY
        sync: false
```

#### Railway.app
```bash
railway up
```

#### Heroku
```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your-key
heroku config:set TAVILY_API_KEY=your-key
git push heroku main
```

---

## 🔧 Configuration

### MCP Server Configuration

Edit `my_agent/utils/mcp_client.py` to configure MCP servers:

```python
MCP_CONFIG = {
    "rube": {
        "url": "https://rube.app/mcp",
        "transport": "streamable_http",
        "headers": {
            "Authorization": "Bearer YOUR_TOKEN"
        }
    }
}
```

### Model Configuration

The agent supports multiple models. Configure in your request:

```python
# Use OpenAI (default)
{"message": "Hello", "model": "openai"}

# Extensible to other providers
{"message": "Hello", "model": "anthropic"}
```

---

## 📊 Monitoring & Debugging

### LangSmith Integration

Enable tracing for debugging and monitoring:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=ai-research-agent
```

### Logging

The application provides comprehensive logging:

```
===== API KEYS STATUS =====
✅ TAVILY_API_KEY: tvly-...xyz
✅ OPENAI_API_KEY: sk-...abc
===========================

===== MCP SERVER CONFIG =====
✅ Connected to MCP server: https://rube.app/mcp
============================

===== MCP AVAILABLE TOOLS =====
1. search_gmail_messages
2. list_gmail_messages
...
✅ Total tools available: 15
================================
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Commit your changes** (`git commit -m 'Add amazing feature'`)
4. **Push to the branch** (`git push origin feature/amazing-feature`)
5. **Open a Pull Request**

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run linting
black . && flake8 .
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **LangChain & LangGraph** - For the excellent agent framework
- **FastAPI** - For the high-performance web framework
- **Tavily** - For powerful web search capabilities
- **Model Context Protocol** - For standardized tool integration

---

## 📧 Contact

**Vijay** - [@Vijay-2005](https://github.com/Vijay-2005)

**Project Link**: [https://github.com/Vijay-2005/ResearchAgent](https://github.com/Vijay-2005/ResearchAgent)

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by Vijay

</div>