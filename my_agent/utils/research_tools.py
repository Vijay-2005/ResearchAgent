
import os
from typing import Dict, Any, List
from functools import lru_cache

from langchain.tools.base import BaseTool
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults

# Web search tool using Tavily
class TavilySearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for information. Use this when you need to find facts or current information."
    api_wrapper: Any = None
    
    def _run(self, query: str) -> Dict[str, Any]:
        try:
            results = self.api_wrapper.run(query)
            return {"results": results}
        except Exception as e:
            return {"error": f"Search error: {str(e)}"}

@lru_cache(maxsize=1)
def get_search_tools() -> List[BaseTool]:
    """Create and return Tavily search tool."""
    tools = []
    
    # Set up Tavily
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    if tavily_api_key:
        try:
            tavily_wrapper = TavilySearchAPIWrapper(tavily_api_key=tavily_api_key)
            print("Initializing Tavily web search...")
            tools.append(TavilySearchResults(
                api_wrapper=tavily_wrapper, 
                max_results=5,
                description="Search the web for information. Use this when you need to find facts or current information."
            ))
            print("✅ Tavily web search initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Tavily API: {e}")
            # Add a simple fallback tool
            tools.append(TavilySearchTool())
    else:
        print("⚠️ TAVILY_API_KEY not found. Web search will be unavailable.")
    
    return tools

# Create research_tools variable to export
research_tools = get_search_tools()

# System prompt for available tools
SYSTEM_PROMPT = """You are an AI research assistant with access to web search.
You can use the following tool:
- web_search: For searching the web to find facts and current information
"""