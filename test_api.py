import requests
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Print API keys for debugging (first 5 chars only)
openai_key = os.environ.get("OPENAI_API_KEY", "")
tavily_key = os.environ.get("TAVILY_API_KEY", "")
print(f"OpenAI API Key available: {'Yes' if openai_key else 'No'} ({openai_key[:5]}... if present)")
print(f"Tavily API Key available: {'Yes' if tavily_key else 'No'} ({tavily_key[:5]}... if present)")

# Test API directly
print("\nTesting API endpoint...")
try:
    # First, test the /health endpoint
    health_response = requests.get("http://localhost:8000/health")
    print(f"Health check response: {health_response.status_code}")
    print(f"Health check content: {health_response.text}")
    
    # Now test the /chat endpoint
    chat_payload = {
        "message": "Simple test message",
        "model": "openai"
    }
    
    print(f"\nSending chat request with payload: {json.dumps(chat_payload)}")
    chat_response = requests.post("http://localhost:8000/chat", json=chat_payload)
    
    print(f"Chat response status: {chat_response.status_code}")
    if chat_response.status_code == 200:
        print("SUCCESS: Chat API is working!")
        response_json = chat_response.json()
        print(f"Conversation ID: {response_json.get('conversation_id')}")
        messages = response_json.get('messages', [])
        if messages:
            print(f"Last message: {messages[-1].get('content', '')[:100]}...")
    else:
        print(f"ERROR: Chat API returned: {chat_response.text}")
except Exception as e:
    print(f"ERROR: Failed to connect to API: {str(e)}")

print("\nTest complete!")
