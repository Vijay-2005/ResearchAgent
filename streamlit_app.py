import streamlit as st
import requests
import json
import os

# Set page configuration
st.set_page_config(
    page_title="Knowledge Navigator",
    page_icon="🧭",
    layout="wide"
)

# Define API URL handling to work in various hosting environments
def get_api_url():
    # Check environment variable first
    api_url = os.environ.get("API_URL")
    if api_url:
        return api_url
    
    # Default to localhost:8000
    return "http://localhost:8000"

API_URL = get_api_url()
print(f"Using API URL: {API_URL}")

# Add health check to verify API is running
def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            return True
        return False
    except Exception as e:
        print(f"API health check failed: {e}")
        return False

# Print debugging info about environment
import sys
print(f"Python version: {sys.version}")
print(f"Environment variables: {list(os.environ.keys())}")

# Initialize session state for conversation history
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model" not in st.session_state:
    st.session_state.model = "openai"  # Default model

# Title and description
st.title("Knowledge Navigator 🧭")
st.markdown("""
This app uses LangGraph to answer questions by combining AI knowledge with web search capabilities.
Ask anything, and the agent will either answer directly or search the web for relevant information.
""")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    model_option = st.selectbox(
        "Select Model",
        options=["openai", "anthropic"],
        index=0,
        key="model_select"
    )
    st.session_state.model = model_option
    
    # Button to start a new conversation
    if st.button("New Conversation"):
        st.session_state.conversation_id = None
        st.session_state.messages = []
        st.rerun()
    
    # Show current conversation ID if exists
    if st.session_state.conversation_id:
        st.info(f"Current conversation: {st.session_state.conversation_id}")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("Knowledge Navigator uses LangGraph and LangChain to provide intelligent responses with search capabilities.")
    st.markdown("Built with ❤️ using FastAPI and Streamlit")

# Main chat interface
st.header("Chat")

# Display chat messages
for message in st.session_state.messages:
    role = message.get("role", "")
    content = message.get("content", "")
    
    if role == "user":
        st.chat_message("user").write(content)
    else:
        st.chat_message("assistant").write(content)

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Prepare request payload
    payload = {
        "message": prompt,
        "model": st.session_state.model
    }
    
    # Add conversation ID if exists
    if st.session_state.conversation_id:
        payload["conversation_id"] = st.session_state.conversation_id
      # Create a placeholder for the assistant's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        # Check if API is healthy first
        if not check_api_health():
            message_placeholder.markdown("⚠️ API server is not available. Please check if the backend is running.")
            st.error("API server is not responding. Please wait a moment and try again.")
            st.info("Debug info: API URL is " + API_URL)
        else:
            try:
                # Make API call with timeout
                response = requests.post(f"{API_URL}/chat", json=payload, timeout=60)
                response.raise_for_status()  # Raise exception for HTTP errors
                
                # Process response
                data = response.json()
                st.session_state.conversation_id = data.get("conversation_id")
                
                # Update messages
                messages = data.get("messages", [])
                st.session_state.messages = messages
                
                # Display the latest assistant message
                latest_assistant_message = next((msg for msg in reversed(messages) if msg.get("role") != "user"), None)
                if latest_assistant_message:
                    message_placeholder.markdown(latest_assistant_message.get("content", ""))
                else:
                    message_placeholder.markdown("No response received.")
                    
            except requests.exceptions.ConnectionError:
                message_placeholder.markdown("⚠️ Could not connect to the API server. The server might still be starting up.")
                st.error("Connection to API failed. Please try again in a moment.")
            except requests.exceptions.Timeout:
                message_placeholder.markdown("⚠️ Request timed out. The API server took too long to respond.")
                st.error("API request timed out. Please try again.")
            except Exception as e:
                message_placeholder.markdown(f"⚠️ Error: {str(e)}")
                st.error(f"Failed to get response: {str(e)}")
                st.info(f"Debug info: API URL={API_URL}, Payload={json.dumps(payload)}")

# Footer
st.markdown("---")
st.caption("Knowledge Navigator - Powered by LangGraph")
