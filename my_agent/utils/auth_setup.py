"""
This module sets up authentication for essential services: Tavily and OpenAI.
Import this module first to ensure environment variables are set.
"""
import os
from pathlib import Path

def setup_environment():
    """Set up environment variables from .env file."""
    from dotenv import load_dotenv
    
    # Find .env file in current project directory
    current_dir = Path(__file__).parent.parent.parent  # Go up to project root
    ENV_FILE = current_dir / ".env"
    
    if not ENV_FILE.exists():
        print(f"Warning: .env file not found at {ENV_FILE}")
        print("Looking for .env.example instead...")
        ENV_FILE = current_dir / ".env.example"
    
    # Load .env file
    print(f"Loading environment variables from: {ENV_FILE}")
    load_dotenv(dotenv_path=str(ENV_FILE))
    
    # Essential API keys only
    keys = {
        "TAVILY_API_KEY": os.environ.get("TAVILY_API_KEY"),
        "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
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
