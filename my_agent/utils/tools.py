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
            print(f"Content of .env file (first line only):\n{env_content.split('\\n')[0]}...")
    except Exception as e:
        print(f"Error reading .env file: {e}")
else:
    print(f"Using Tavily API key: {tavily_api_key[:5]}...")

# Create the API wrapper
tavily_wrapper = TavilySearchAPIWrapper(
    tavily_api_key=tavily_api_key
)

# Pass the wrapper to the tool
tools = [TavilySearchResults(api_wrapper=tavily_wrapper, max_results=1)]