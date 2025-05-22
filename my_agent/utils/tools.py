import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

# Find the root directory where .env should be located 
# (going up from the current file to find the project root)
root_dir = Path(__file__).parent.parent.parent
env_file = root_dir / '.env'

# Load environment variables from the .env file
print(f"Loading environment from: {env_file}")
load_dotenv(dotenv_path=env_file)

# Create the API wrapper with the API key from environment
tavily_api_key = os.environ.get("TAVILY_API_KEY")
if not tavily_api_key:
    print(f"ERROR: TAVILY_API_KEY not found in environment. Path checked: {env_file}")
    print(f"Current environment variables: {list(os.environ.keys())}")
    print("Please make sure .env file contains the API key without comments or special characters.")
    # For debugging, print the entire content of .env
    try:
        with open(env_file, "r") as f:
            env_content = f.read()
            first_line = env_content.split('\n')[0]
            print(f"Content of .env file (first line only):\n{first_line}...")
    except Exception as e:
        print(f"Error reading .env file: {e}")
else:
    print(f"Using Tavily API key: {tavily_api_key[:5]}...")

# Create a default tool that doesn't require API keys
from langchain.tools.base import BaseTool
from typing import Any, Dict, Optional, Type

class SimpleTool(BaseTool):
    name: str = "search"
    description: str = "Search the web for the answer."
    
    def _run(self, query: str) -> Dict[str, Any]:
        return {
            "results": f"I would normally search for '{query}', but search is currently unavailable. Please try again later or ask me something I can answer without searching."
        }

# Try to create the API wrapper, falling back to a simple tool if it fails
try:
    # Create the API wrapper
    tavily_wrapper = TavilySearchAPIWrapper(
        tavily_api_key=tavily_api_key
    )
    # Test that it works
    print("Testing Tavily API connection...")
    test_result = tavily_wrapper.results("test query")
    print(f"Tavily test successful: found {len(test_result)} results")
    
    # Pass the wrapper to the tool
    tools = [TavilySearchResults(api_wrapper=tavily_wrapper, max_results=1)]
except Exception as e:
    print(f"Error initializing Tavily API: {e}")
    # Fall back to a basic tool that doesn't require API access
    tools = [SimpleTool()]
    print("Using fallback search tool due to Tavily API initialization error.")