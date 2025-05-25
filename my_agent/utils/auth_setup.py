"""
This module sets up authentication for various services used in the agent.
Import this module first, before any other imports, to ensure environment variables are set.
"""
import os
from pathlib import Path

def setup_environment():
    """Set up environment variables from .env file."""
    from dotenv import load_dotenv
    
    ENV_FILE = "C:\\Users\\Admin\\vijay\\Ai researchher\\langgraph-example\\.env"
    
    # Load .env file
    print(f"Loading environment variables from: {ENV_FILE}")
    load_dotenv(dotenv_path=ENV_FILE)
    
    # Set essential environment variables for LangSmith
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "langgraph-example"
    
    # Validate keys are loaded - match API_KEYS from app.py
    keys = {
        "TAVILY_API_KEY": os.environ.get("TAVILY_API_KEY"),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        "SERPER_API_KEY": os.environ.get("SERPER_API_KEY"),
        "METAPHOR_API_KEY": os.environ.get("METAPHOR_API_KEY"),
        "BROWSERLESS_API_KEY": os.environ.get("BROWSERLESS_API_KEY"),
        "APIFY_API_KEY": os.environ.get("APIFY_API_KEY"),
        "LANGCHAIN_API_KEY": os.environ.get("LANGCHAIN_API_KEY"),
        "LANGSMITH_API_KEY": os.environ.get("LANGSMITH_API_KEY")
    }
    
    # Print loaded keys (first 5 characters only for security)
    for key_name, key_value in keys.items():
        if key_value:
            print(f"✓ {key_name} loaded: {key_value[:5]}...")
        else:
            print(f"✗ {key_name} not found!")
    
    return keys

# Run setup immediately when this module is imported
api_keys = setup_environment()
