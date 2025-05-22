import requests
import json

# Test the API endpoint directly
try:
    print("Testing API endpoint...")
    response = requests.post(
        "http://localhost:8000/chat",
        json={"message": "hello", "model": "openai"},
        timeout=60
    )
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

# Also check if the API is running
try:
    health_response = requests.get("http://localhost:8000/health")
    print(f"Health endpoint status: {health_response.status_code}")
    print(f"Health response: {health_response.text}")
except Exception as e:
    print(f"Health check error: {e}")
