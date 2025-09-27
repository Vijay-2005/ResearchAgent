# AI Research Agent

![](static/agent_ui.png)

## Overview
AI Research Agent is a powerful, specialized assistant designed to help with research tasks. Leveraging LangGraph and LangChain technologies, this agent can search the web, process information, and provide comprehensive research assistance through a conversational interface.

## Features

- **Multi-Source Research**: Utilizes various search engines and tools including Tavily, Google Serper, and Wikipedia
- **Web Content Extraction**: Browse and extract content from specific webpages
- **Interactive UI**: Clean HTML/CSS/JS interface for easy interaction
- **Conversational Memory**: Maintains context throughout research sessions
- **Smart Tool Selection**: Automatically chooses the best research tool based on query content

## Tech Stack

- **Framework**: [LangGraph](https://github.com/langchain-ai/langgraph) - For building stateful, multi-actor LLM applications
- **UI**: HTML/CSS/JavaScript frontend
- **API**: FastAPI backend service
- **Deployment**: Render.com ready with environment configuration

## Getting Started

### Prerequisites
- Python 3.10+
- API keys for the following services:
  
  **Required:**
  - At least one LLM provider:
    - [OpenAI API key](https://platform.openai.com/account/api-keys) (Recommended)
    - [Anthropic API key](https://www.anthropic.com/api)
  - At least one search provider:
    - [Tavily API key](https://tavily.com/) (Recommended)
    - [Google Serper API key](https://serper.dev/)
    - [SerpAPI key](https://serpapi.com/)
    
  **Optional but recommended:**
  - [Metaphor API key](https://metaphor.systems/) (for recent content and trends)
  - [Browserless API key](https://www.browserless.io/) (for web content extraction)
  - [LangSmith API key](https://smith.langchain.com/) (for debugging and tracing)

### Environment Setup

1. Create a `.env` file in the project root:
   ```bash
   # Required LLM API Keys (at least one)
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here

   # Required Search API Keys (at least one)
   TAVILY_API_KEY=tvly-your-tavily-api-key-here
   SERPER_API_KEY=your-serper-api-key-here
   SERPAPI_API_KEY=your-serpapi-api-key-here

   # Optional API Keys for enhanced features
   METAPHOR_API_KEY=your-metaphor-api-key-here
   BROWSERLESS_API_KEY=your-browserless-api-key-here
   LANGSMITH_API_KEY=your-langsmith-api-key-here

   # Optional LangSmith tracing
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=ai-research-agent
   ```

### Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure API keys in your `.env` file

### Running the Application

**Start the backend:**
```bash
python app.py
```

The application will be available at `http://localhost:8000`

**Access the web interface:**
Navigate to `http://localhost:8000` in your browser to use the chat interface.

## Available Research Tools

| Tool Name | Purpose | API Key Required | Best For |
|-----------|---------|------------------|----------|
| `wikipedia_research` | Factual information | ❌ Free | Definitions, history, general knowledge |
| `tavily_search` | Web search | ✅ TAVILY_API_KEY | Current information, news |
| `serper_search` | Google search | ✅ SERPER_API_KEY | Academic research, scientific data |
| `serpapi_search` | Google search | ✅ SERPAPI_API_KEY | Comprehensive search results |
| `metaphor_search` | Recent content | ✅ METAPHOR_API_KEY | Trending topics, latest articles |
| `browse_web` | Webpage content | ✅ BROWSERLESS_API_KEY | Extract content from specific URLs |

## API Usage

### Chat Endpoint
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What is artificial intelligence?",
       "model": "openai"
     }'
```

### Health Check
```bash
curl http://localhost:8000/health
```

### API Status
```bash
curl http://localhost:8000/api-status
```

## Testing Your Setup

Use this comprehensive test prompt to verify all API keys are working:

```
"Please test all your available research tools and API keys by doing the following comprehensive test:

1. Test Wikipedia research with query 'artificial intelligence'
2. Test Tavily search with query 'latest technology news'
3. Test Google Serper search with query 'Python programming'
4. Test SerpAPI search with query 'machine learning'
5. Test Metaphor search with query 'AI trends 2024'
6. Test web browsing on 'https://www.wikipedia.org'

For each tool, tell me:
- ✅ WORKING: [tool name] - [brief result]
- ❌ ERROR: [tool name] - [error message]
- ⚠️ NOT AVAILABLE: [tool name] - [reason]

Finally, give me a summary of which API keys are working and which need to be configured."
```

## Deployment

### Render.com Deployment

1. Connect your GitHub repository to Render.com
2. Set environment variables in Render dashboard
3. Deploy using the included `render.yaml` configuration

### Manual Deployment

The application is ready for deployment on any platform that supports Python applications. Make sure to:
- Set all required environment variables
- Install dependencies from `requirements.txt`
- Run `python app.py`

## Smart Tool Selection

The agent automatically selects the best tool based on your query:

- **General knowledge questions** → Wikipedia research
- **Academic/research topics** → Google Serper search
- **Recent news/trends** → Metaphor search
- **Specific webpages** → Web browsing
- **Default fallback** → Tavily search

## Project Structure

```
├── app.py                 # FastAPI main application
├── my_agent/
│   ├── agent.py          # LangGraph workflow
│   └── utils/
│       ├── nodes.py      # Agent/tool nodes
│       ├── state.py      # Agent state definition
│       ├── research_tools.py  # Tool implementations
│       └── auth_setup.py # API key setup
├── static/index.html     # Web UI
├── requirements.txt     # Dependencies
└── render.yaml         # Render.com deployment config
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Make sure your `.env` file is in the project root and contains valid API keys
2. **Tool Not Available**: Check if the corresponding API key is set in your environment
3. **Wikipedia Works But Others Don't**: Wikipedia doesn't require an API key, so test with other tools


### LLM APIs (at least one required)
- **OpenAI**: Used for GPT models



Check API status at `http://localhost:8000/api-status` to see which tools are properly configured.

## License

This project uses the same license as the LangGraph project.
