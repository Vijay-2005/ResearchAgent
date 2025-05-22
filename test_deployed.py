import requests
import json

# URL of your deployed app
BASE_URL = "https://langgraph-example.onrender.com"

def test_health():
    """Test the health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check status code: {response.status_code}")
    if response.ok:
        print(f"Health check response: {response.json()}")
    else:
        print(f"Health check failed: {response.text}")

def test_chat():
    """Test the chat endpoint"""
    payload = {
        "message": "What is the capital of France?",
        "model": "openai"
    }
    
    print("\nSending test message to chat endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            timeout=30  # Longer timeout for the first request which might be cold start
        )
        
        if response.ok:
            data = response.json()
            print("Chat response received:")
            conversation_id = data.get("conversation_id")
            messages = data.get("messages", [])
            
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                print(f"\n{role.upper()}: {content}")
            
            print(f"\nConversation ID: {conversation_id}")
            return conversation_id
        else:
            print(f"Chat request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error testing chat endpoint: {e}")
        return None

def test_search():
    """Test the search capability"""
    payload = {
        "message": "What are the latest developments in quantum computing?",
        "model": "openai"
    }
    
    print("\nTesting search capability...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            timeout=60  # Longer timeout since search takes more time
        )
        
        if response.ok:
            data = response.json()
            print("Search response received:")
            conversation_id = data.get("conversation_id")
            messages = data.get("messages", [])
            
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                print(f"\n{role.upper()}: {content[:100]}..." if len(content) > 100 else f"\n{role.upper()}: {content}")
            
            return conversation_id
        else:
            print(f"Search request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error testing search capability: {e}")
        return None

if __name__ == "__main__":
    print("Testing deployed Knowledge Navigator application")
    print(f"Base URL: {BASE_URL}")
    
    # Test health endpoint
    test_health()
    
    # Test chat endpoint
    conv_id = test_chat()
    
    # Test search capability
    if conv_id:
        print("\nBasic chat is working!")
        print("\nNow testing search capability. This may take a minute...")
        test_search()
    
    print("\nTest completed. Check the output above to see if your deployment is working correctly.")
