import os
from typing import Dict, Any, List, Optional, Union, Annotated
from functools import lru_cache

from langchain.tools.base import BaseTool
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from langchain_community.tools.google_serper import GoogleSerperRun
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

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

try:
    from apify_client import ApifyClient
    apify_available = True
except ImportError:
    apify_available = False
    print("Warning: Apify client not available")

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

# Add this class with your other tool classes
class ApifyScraper(BaseTool):
    name: str = "apify_scraper"
    description: str = "Scrape data from websites using Apify. Useful for extracting product information, prices, and other details from websites including e-commerce sites."
    
    def _run(self, url: str) -> Dict[str, Any]:
        """Run a web scraper on the specified URL using Apify."""
        print(f"🕸️ Running Apify scraper on: {url}")
        
        apify_api_key = os.environ.get("APIFY_API_KEY")
        if not apify_api_key:
            return {"error": "APIFY_API_KEY not found in environment variables"}
            
        try:
            # Initialize the ApifyClient with your API token
            client = ApifyClient(apify_api_key)
            
            # Choose the appropriate actor based on the URL
            actor_to_use = "apify/web-scraper"  # Default general-purpose scraper
            
            # For specific sites, use specialized actors
            if "amazon" in url.lower():
                actor_to_use = "fhytlu/amazon-product"
            elif "ebay" in url.lower():
                actor_to_use = "dtrungtin/ebay-scraper"
                
            print(f"Using Apify actor: {actor_to_use}")
            
            # Configure actor input based on URL
            run_input = {
                "startUrls": [{"url": url}],
                "maxCrawlPages": 1,  # Limit to just the requested page
                "pageWaitSelectorTimeout": 20000
            }
            
            # Run the Actor and wait for it to finish
            run = client.actor(actor_to_use).call(run_input=run_input)
            
            # Fetch results from the Actor's default dataset
            items = client.dataset(run["defaultDatasetId"]).list_items().items
            
            if items:
                # Process and return the results
                return {
                    "success": True,
                    "url": url,
                    "results": items[:5],  # Return up to 5 items
                    "count": len(items),
                    "actor_used": actor_to_use
                }
            else:
                return {
                    "success": False,
                    "error": "No data extracted",
                    "url": url,
                    "actor_used": actor_to_use
                }
                
        except Exception as e:
            print(f"❌ Apify scraper error: {str(e)}")
            return {"error": f"Failed to scrape {url}: {str(e)}"}

@lru_cache(maxsize=4)
def get_search_tools() -> List[BaseTool]:
    """Create and return available search tools based on API keys."""
    tools = []
    
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
    
    # Add Apify scraper if API key is available
    apify_api_key = os.environ.get("APIFY_API_KEY")
    if apify_api_key and apify_available:
        try:
            tools.append(ApifyScraper())
            print("✅ Apify web scraper initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Apify scraper: {e}")
    
    # Add a fallback tool if none of the other tools are available
    if not tools:
        tools.append(SimpleSearchTool())
        print("No API keys available. Using fallback search tool.")
    
    return tools

# Create research_tools variable to export
research_tools = get_search_tools()

# Update the system prompt to include Apify capability
SYSTEM_PROMPT = """You are an AI research assistant with access to various tools including web search and web scraping.
You can use the following tools:
- tavily_search: For general web search
- serper_search: For Google search results
- browse_web: For browsing specific webpages
- apify_scraper: For scraping e-commerce websites and extracting structured data
...
"""