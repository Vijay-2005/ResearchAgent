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

# Define API URL - will use local endpoint or environment variable
API_URL = os.getenv("API_URL", "http://localhost:8000")

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
        
        try:
            # Make API call
            response = requests.post(f"{API_URL}/chat", json=payload)
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
                
        except Exception as e:
            message_placeholder.markdown(f"⚠️ Error: {str(e)}")
            st.error(f"Failed to get response: {str(e)}")

# Footer
st.markdown("---")
st.caption("Knowledge Navigator - Powered by LangGraph")
