
import os
import json
import asyncio
from typing import Dict, Any, List, Optional, Union, Annotated
from functools import lru_cache

from langchain.tools.base import BaseTool
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from langchain_community.tools.google_serper import GoogleSerperRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
# MCP Chart Server Tool
try:
    from my_agent.utils.mcp_tools import (
        MultiServerMCPClient, 
        MCPChartTool, 
        get_mcp_chart_server_path,
        get_default_mcp_connections,
        create_mcp_client,
        Connection
    )
    mcp_chart_available = True
except ImportError:
    mcp_chart_available = False

class MultiMCPToolWrapper(BaseTool):
    """Tool wrapper for multiple MCP servers."""
    name: str = "multi_mcp_tools"
    description: str = "Access tools from multiple MCP servers including chart generation, file operations, and more."
    client: Optional[Any] = None
    _tools_cache: Optional[List] = None
    
    def __init__(self):
        super().__init__()
        self.client = None
        self._tools_cache = None
        
    async def _get_client(self):
        """Get or create MCP client."""
        if self.client is None:
            connections = get_default_mcp_connections()
            self.client = MultiServerMCPClient(connections)
            await self.client.initialize()
        return self.client
        
    async def _get_available_tools(self):
        """Get all available tools from all servers."""
        if self._tools_cache is None:
            client = await self._get_client()
            self._tools_cache = await client.get_tools()
        return self._tools_cache
        
    def _run(self, query: str) -> Dict[str, Any]:
        """Synchronous run method."""
        try:
            return asyncio.run(self._async_run(query))
        except Exception as e:
            return {"error": str(e)}
            
    async def _async_run(self, query: str) -> Dict[str, Any]:
        """Handle MCP tool requests."""
        try:
            # Parse the query to extract server, tool, and arguments
            # Expected format: "server_name:tool_name:arguments_json"
            parts = query.split(":", 2)
            if len(parts) < 2:
                # List available tools
                client = await self._get_client()
                tools_info = {}
                for server_name in client.sessions.keys():
                    tools_info[server_name] = await client.list_server_tools(server_name)
                return {"available_tools": tools_info}
                
            server_name = parts[0]
            tool_name = parts[1]
            arguments = json.loads(parts[2]) if len(parts) > 2 else {}
            
            client = await self._get_client()
            result = await client.call_tool(server_name, tool_name, arguments)
            return {"result": result, "server": server_name, "tool": tool_name}
            
        except json.JSONDecodeError:
            return {"error": "Invalid JSON arguments"}
        except Exception as e:
            return {"error": str(e)}

class MCPChartToolWrapper(BaseTool):
    name: str = "mcp_chart"
    description: str = "Generate charts using your MCP Chart server. Input should be a JSON object with chart_type, data, and optional config."
    chart_tool: Optional[Any] = None

    def __init__(self):
        super().__init__()
        if mcp_chart_available:
            server_path = get_mcp_chart_server_path()
            self.chart_tool = MCPChartTool(server_path)

    def _run(self, chart_data: dict) -> Dict[str, Any]:
        if not self.chart_tool:
            return {"error": "MCP Chart server tool not available."}
        try:
            # Synchronous call
            return self.chart_tool._run(**chart_data)
        except Exception as e:
            return {"error": str(e)}

# Fix SerpAPI imports - using correct modules
try:
    from langchain_community.utilities.serpapi import SerpAPIWrapper
    serpapi_available = True
except ImportError:
    serpapi_available = False

# Optional imports for more advanced tools
try:
    from langchain_community.document_loaders import WebBaseLoader
    web_loader_available = True
except ImportError:
    web_loader_available = False

try:
    from metaphor_python import Metaphor
    metaphor_available = True
except ImportError:
    metaphor_available = False


# Fallback tool
class SimpleSearchTool(BaseTool):
    name: str = "simple_search"
    description: str = "Search the web for information. Use this when you need to find facts or current information."
    
    def _run(self, query: str) -> Dict[str, Any]:
        return {
            "results": f"I would normally search for '{query}', but search is currently unavailable. Please try again later or ask me something I can answer without searching."
        }

# Create SerpAPI tool class
class SerpAPITool(BaseTool):
    name: str = "serpapi_search"
    description: str = "Search Google through SerpAPI. Use this for comprehensive search results."
    api_wrapper: Any = None
    def _run(self, query: str) -> Dict[str, Any]:
        results = self.api_wrapper.run(query)
        return {"results": results}

# Wikipedia research tool
class WikipediaResearchTool(BaseTool):
    name: str = "wikipedia_research"
    description: str = "Search Wikipedia for factual information and historical data. Use this for getting verified information about concepts, people, places, and events."
    
    def _run(self, query: str) -> Dict[str, Any]:
        try:
            wikipedia = WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=5000)
            results = wikipedia.run(query)
            return {"results": results}
        except Exception as e:
            print(f"Error in Wikipedia search: {str(e)}")
            return {"error": str(e)}


@lru_cache(maxsize=4)
def get_search_tools() -> List[BaseTool]:
    """Create and return available search tools based on API keys."""
    tools = []
    
    # Add Multi-Server MCP tool if available
    if mcp_chart_available:
        try:
            tools.append(MultiMCPToolWrapper())
            print("Multi-Server MCP tool initialized successfully")
        except Exception as e:
            print(f"Error initializing Multi-Server MCP tool: {e}")
    
    # Add individual MCP Chart tool for backward compatibility
    if mcp_chart_available:
        try:
            tools.append(MCPChartToolWrapper())
            print("MCP Chart tool initialized successfully")
        except Exception as e:
            print(f"Error initializing MCP Chart tool: {e}")

    # Add Wikipedia tool (free, no API key required)
    try:
        tools.append(WikipediaResearchTool())
        print("Wikipedia research tool initialized successfully")
    except Exception as e:
        print(f"Error initializing Wikipedia tool: {e}")
    
    # Try to set up Tavily
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    if tavily_api_key:
        try:
            tavily_wrapper = TavilySearchAPIWrapper(tavily_api_key=tavily_api_key)
            # Test that it works
            print("Testing Tavily API connection...")
            # Comment this out to avoid making an actual API call during import
            # tavily_wrapper.results("test query")
            print("Tavily initialized!")
            tools.append(TavilySearchResults(
                api_wrapper=tavily_wrapper, 
                max_results=3,
                description="Search the web for recent information using Tavily. Use this for finding current facts and news."
            ))
        except Exception as e:
            print(f"Error initializing Tavily API: {e}")
    
    # Try to set up Serper
    serper_api_key = os.environ.get("SERPER_API_KEY")
    if serper_api_key:
        try:
            serper_wrapper = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)
            tools.append(GoogleSerperRun(
                api_wrapper=serper_wrapper,
                description="Search the web using Google Serper. Good for finding precise information and facts."
            ))
            print("Serper tool initialized successfully")
        except Exception as e:
            print(f"Error initializing Serper API: {e}")
    
    # Try to set up SerpAPI
    serpapi_api_key = os.environ.get("SERPAPI_API_KEY")
    if serpapi_api_key and serpapi_available:
        try:
            serpapi_wrapper = SerpAPIWrapper(serpapi_api_key=serpapi_api_key)
            serpapi_tool = SerpAPITool()
            serpapi_tool.api_wrapper = serpapi_wrapper
            tools.append(serpapi_tool)
            print("SerpAPI tool initialized successfully")
        except Exception as e:
            print(f"Error initializing SerpAPI: {e}")
    
    # Try to set up Metaphor if available
    metaphor_api_key = os.environ.get("METAPHOR_API_KEY")
    if metaphor_api_key and metaphor_available:
        try:
            # Create a custom Metaphor tool
            class MetaphorSearchTool(BaseTool):
                name: str = "metaphor_search"
                description: str = "Search for recent content and articles using Metaphor. Good for finding trending topics and recent articles."
                
                def _run(self, query: str) -> Dict[str, Any]:
                    client = Metaphor(api_key=metaphor_api_key)
                    response = client.search(query, num_results=5, use_autoprompt=True)
                    
                    results = []
                    for result in response.results:
                        results.append({
                            "title": result.title,
                            "url": result.url,
                            "extract": result.extract
                        })
                    
                    return {"results": results}
            
            tools.append(MetaphorSearchTool())
            print("Metaphor search tool initialized successfully")
        except Exception as e:
            print(f"Error initializing Metaphor API: {e}")
    
    # Add web loading capability if available
    browserless_api_key = os.environ.get("BROWSERLESS_API_KEY")
    if browserless_api_key and web_loader_available:
        try:
            class WebBrowsingTool(BaseTool):
                name: str = "browse_web"
                description: str = "Browse a specific webpage and extract its content. Input should be a URL."
                
                def _run(self, url: str) -> Dict[str, Any]:
                    try:
                        loader = WebBaseLoader(
                            web_paths=[url],
                            api_key=browserless_api_key
                        )
                        docs = loader.load()
                        return {"content": docs[0].page_content}
                    except Exception as e:
                        return {"error": f"Could not load the webpage: {str(e)}"}
            
            tools.append(WebBrowsingTool())
            print("Web browsing tool initialized successfully")
        except Exception as e:
            print(f"Error initializing Web browsing tool: {e}")
    
    
    # Add a fallback tool if none of the other tools are available
    if not tools:
        tools.append(SimpleSearchTool())
        print("No API keys available. Using fallback search tool.")
    
    return tools

# Create research_tools variable to export
research_tools = get_search_tools()

# System prompt for available tools
SYSTEM_PROMPT = """You are an AI research assistant with access to various tools including web search.
You can use the following tools:
- tavily_search: For general web search
- serper_search: For Google search results
- browse_web: For browsing specific webpages
- wikipedia_research: For factual information and historical data
- metaphor_search: For recent content and trending topics
"""