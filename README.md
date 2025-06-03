# AI Research Agent

![](static/agent_ui.png)

## Overview
AI Research Agent is a powerful, specialized assistant designed to help with research tasks. Leveraging LangGraph and LangChain technologies, this agent can search the web, process information, and provide comprehensive research assistance through a conversational interface.

## Features

- **Multi-Source Research**: Utilizes various search engines and tools including Google/SerpAPI, Tavily, and more
- **Advanced Web Scraping**: Extracts detailed information from webpages
- **Interactive UI**: Clean Streamlit interface for easy interaction
- **Conversational Memory**: Maintains context throughout research sessions
- **Customizable Search Tools**: Multiple search providers with fallback mechanisms

## Tech Stack

- **Framework**: [LangGraph](https://github.com/langchain-ai/langgraph) - For building stateful, multi-actor LLM applications
- **UI**: Streamlit
- **API**: FastAPI backend service
- **Deployment**: Docker containerization with options for LangGraph Cloud deployment

## Getting Started

### Prerequisites
- Python 3.10+
- API keys for the following services:
  
  **Required:**
  - At least one LLM provider:
    - [OpenAI API key](https://platform.openai.com/account/api-keys)
    - [Anthropic API key](https://www.anthropic.com/api)
  - At least one search provider:
    - [Tavily API key](https://tavily.com/) (Recommended)
    - [Google Serper API key](https://serper.dev/)
    - [SerpAPI key](https://serpapi.com/)
    
  **Optional but recommended:**
  - [Metaphor API key](https://metaphor.systems/) (for research-focused searches)
  - [Browserless API key](https://www.browserless.io/) (for web scraping)
  - [Apify API key](https://apify.com/) (for advanced web scraping)
  - [LangSmith API key](https://smith.langchain.com/) (for debugging and tracing)

### Environment Setup

1. Copy the `.env.example` file to create your own `.env` file:
   ```bash
   cp .env.example .env
   ```
   
2. Add your API keys to the `.env` file

### Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure API keys in your environment variables

### Running the Application

**Start the backend:**
```bash
python serve.py
```

**Launch the UI:**
```bash
streamlit run streamlit_app.py
```

## Deployment

You can deploy this agent to LangGraph Cloud by following the instructions [here](https://langchain-ai.github.io/langgraph/cloud/).

## Docker Support

Build and run using Docker:
```bash
docker build -t ai-research-agent .
docker run -p 8000:8000 -p 8501:8501 ai-research-agent
```

## API Configuration

This agent is designed with flexibility in mind, allowing you to choose which search and AI services to use based on your needs and available API keys:

### Search APIs (at least one required)
- **Tavily**: Primary search provider, specialized for research queries
- **SerpAPI/Google Serper**: Alternative search engines with more general web results
- **Metaphor**: Research-oriented search engine that's particularly good for finding academic content

### Web Processing APIs (optional)
- **Browserless**: Enables headless browser capabilities for advanced web scraping
- **Apify**: Provides structured data extraction from websites

### LLM APIs (at least one required)
- **OpenAI**: Used for GPT models


If an API key is missing, the agent will automatically fall back to other available services. Configure your preferred services in the `.env` file.

## License

This project uses the same license as the LangGraph project.
