import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print out environment variables (just the first few characters for security)
print("Environment Variables Check:")
print(f"TAVILY_API_KEY: {'✓ Found - ' + os.getenv('TAVILY_API_KEY')[:5] + '...' if os.getenv('TAVILY_API_KEY') else '✗ Not found'}")
print(f"LANGSMITH_API_KEY: {'✓ Found - ' + os.getenv('LANGSMITH_API_KEY')[:5] + '...' if os.getenv('LANGSMITH_API_KEY') else '✗ Not found'}")
print(f"ANTHROPIC_API_KEY: {'✓ Found' if os.getenv('ANTHROPIC_API_KEY') else '✗ Not found'}")
print(f"OPENAI_API_KEY: {'✓ Found - ' + os.getenv('OPENAI_API_KEY')[:5] + '...' if os.getenv('OPENAI_API_KEY') else '✗ Not found'}")

# Set explicit environment variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "langgraph-example"

print("\nEnvironment Variables Set:")
print(f"LANGCHAIN_TRACING_V2: {os.environ.get('LANGCHAIN_TRACING_V2')}")
print(f"LANGCHAIN_PROJECT: {os.environ.get('LANGCHAIN_PROJECT')}")

# Try importing langsmith
try:
    from langsmith import Client
    client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))
    print("\nLangSmith Client Test:")
    print("Client initialized successfully")
except Exception as e:
    print(f"\nLangSmith Client Error:")
    print(f"Error: {str(e)}")

# Try to import and init Tavily
try:
    from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
    wrapper = TavilySearchAPIWrapper(tavily_api_key=os.getenv("TAVILY_API_KEY"))
    print("\nTavily Test:")
    print("Wrapper initialized successfully")
except Exception as e:
    print(f"\nTavily Error:")
    print(f"Error: {str(e)}")
