import os
from dotenv import load_dotenv
from langsmith import Client

def setup_langsmith():
    """Set up LangSmith client with proper environment variables."""
    load_dotenv()
    
    # Check if LangSmith API key is available
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
    if not langsmith_api_key:
        print("WARNING: LANGSMITH_API_KEY not found in environment variables!")
        return None
    
    # Print confirmation (first 5 chars only for security)
    print(f"Using LangSmith API key: {langsmith_api_key[:5]}...")
    
    # Set LangSmith environment variables needed for proper logging
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "langgraph-example"
    
    # Return LangSmith client
    return Client(api_key=langsmith_api_key)

# Initialize LangSmith when imported
langsmith_client = setup_langsmith()
