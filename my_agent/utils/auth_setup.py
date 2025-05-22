"""
This module sets up authentication for various services used in the agent.
Import this module first, before any other imports, to ensure environment variables are set.
"""
import os
import sys
from pathlib import Path

# Find the root directory of the project
ROOT_DIR = Path(__file__).parent.parent.parent
ENV_FILE = ROOT_DIR / '.env'

def setup_environment():
    """Set up environment variables from .env file."""
    from dotenv import load_dotenv
    
    # Load .env file
    print(f"Loading environment variables from: {ENV_FILE}")
    load_dotenv(dotenv_path=ENV_FILE)
    
    # Set essential environment variables for LangSmith
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "langgraph-example"
    
    # Validate keys are loaded
    keys = {
        "TAVILY_API_KEY": os.environ.get("TAVILY_API_KEY"),
        "LANGSMITH_API_KEY": os.environ.get("LANGSMITH_API_KEY"),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY")
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
