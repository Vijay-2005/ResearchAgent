"""
Test script for LangGraph agent
"""
import requests
import json
import time

# Configuration
BASE_URL = "http://127.0.0.1:2024"
MODEL = "openai"  # Use "openai" since we know it works

def test_agent():
    print("Testing LangGraph agent...")
    
    # 1. Create a new thread
    print("\n1. Creating a new thread...")
    response = requests.post(f"{BASE_URL}/api/threads")
    thread_data = response.json()
    thread_id = thread_data['id']
    print(f"Thread created with ID: {thread_id}")
    
    # 2. Start a run on the thread with a test question
    print("\n2. Starting a run with a test question...")
    payload = {
        "config": {
            "configurable": {
                "model_name": MODEL
            }
        },
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": "What's the capital of France? And can you search for information about the Eiffel Tower?"
                }
            ]
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/threads/{thread_id}/runs/agent",
        json=payload
    )
    run_data = response.json()
    run_id = run_data['id']
    print(f"Run started with ID: {run_id}")
    
    # 3. Poll for completion
    print("\n3. Waiting for the agent to process...")
    max_attempts = 30
    attempt = 0
    while attempt < max_attempts:
        response = requests.get(f"{BASE_URL}/api/threads/{thread_id}/runs/{run_id}")
        status_data = response.json()
        status = status_data.get('status')
        print(f"Current status: {status}")
        
        if status in ['completed', 'failed', 'cancelled']:
            break
            
        time.sleep(1)
        attempt += 1
    
    # 4. Get the messages
    print("\n4. Getting the conversation messages:")
    response = requests.get(f"{BASE_URL}/api/threads/{thread_id}/messages")
    messages = response.json()
    
    print("\n===== CONVERSATION =====")
    for msg in messages:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        if isinstance(content, list):
            content = " ".join([c.get('text', '') for c in content if c.get('type') == 'text'])
        print(f"\n{role.upper()}: {content}")
    
    print("\n===== END OF CONVERSATION =====")
    
    # 5. Test search tool capability
    print("\n5. Testing a question that should trigger the Tavily search tool...")
    payload = {
        "input": {
            "messages": [
                {
                    "role": "user",
                    "content": "Search for the latest news about artificial intelligence."
                }
            ]
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/threads/{thread_id}/runs/agent",
        json=payload
    )
    run_data = response.json()
    run_id = run_data['id']
    print(f"Run started with ID: {run_id}")
    
    # 6. Poll for completion
    print("\n6. Waiting for the search to complete...")
    attempt = 0
    while attempt < max_attempts:
        response = requests.get(f"{BASE_URL}/api/threads/{thread_id}/runs/{run_id}")
        status_data = response.json()
        status = status_data.get('status')
        print(f"Current status: {status}")
        
        if status in ['completed', 'failed', 'cancelled']:
            break
            
        time.sleep(1)
        attempt += 1
    
    # 7. Get the updated messages
    print("\n7. Getting the updated conversation with search results:")
    response = requests.get(f"{BASE_URL}/api/threads/{thread_id}/messages")
    messages = response.json()
    
    print("\n===== SEARCH RESULTS CONVERSATION =====")
    for msg in messages:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')
        if isinstance(content, list):
            content = " ".join([c.get('text', '') for c in content if c.get('type') == 'text'])
        print(f"\n{role.upper()}: {content}")
    
    print("\n===== END OF SEARCH RESULTS CONVERSATION =====")
    
    return thread_id, run_id

if __name__ == "__main__":
    if not requests.get(f"{BASE_URL}/health").ok:
        print("ERROR: LangGraph server is not running. Please start it with 'langgraph dev --allow-blocking'")
    else:
        thread_id, run_id = test_agent()
        print(f"\nTest completed successfully!")
        print(f"Thread ID: {thread_id}")
        print(f"Final Run ID: {run_id}")
        print(f"\nYou can view the full conversation in the LangGraph Studio UI:")
        print(f"https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024")
