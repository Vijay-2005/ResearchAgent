import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uvicorn
from typing import Dict, List, Any, Optional

# Import our agent
from my_agent.agent import workflow
from my_agent.utils.state import AgentState

# Load environment variables first thing
load_dotenv()

# Verify keys are available
for key in ["TAVILY_API_KEY", "OPENAI_API_KEY"]:
    if not os.environ.get(key):
        print(f"Warning: {key} not found in environment variables!")

# Create the FastAPI app
app = FastAPI(title="Knowledge Navigator")

# Add CORS middleware to allow web requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for conversations (in-memory, will reset on server restart)
conversations = {}

@app.get("/")
async def root():
    return {"message": "Knowledge Navigator API is running. See /docs for API documentation."}

@app.post("/chat")
async def chat(request: Dict[str, Any] = Body(...)):
    """
    Chat with the agent.
    
    Expects a JSON body with:
    - conversation_id: Optional ID to continue a conversation
    - message: The user's message
    - model: Optional model to use ("openai" or "anthropic")
    """
    
    # Extract parameters from request
    conversation_id = request.get("conversation_id", None)
    message = request.get("message")
    model_name = request.get("model", "openai")
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    # Get or create conversation history
    if conversation_id and conversation_id in conversations:
        messages = conversations[conversation_id]
    else:
        # Start a new conversation
        messages = []
        conversation_id = f"conv_{len(conversations) + 1}"
    
    # Add user message to history
    messages.append({"role": "user", "content": message})
    
    # Create the initial state
    state = AgentState(messages=messages)
    
    # Configure with the model
    config = {"configurable": {"model_name": model_name}}
    
    # Invoke the agent
    result = workflow.invoke(state, config=config)
    
    # Get the updated messages
    updated_messages = result["messages"]
    
    # Save the updated conversation
    conversations[conversation_id] = updated_messages
    
    # Return results
    return {
        "conversation_id": conversation_id,
        "messages": updated_messages
    }

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation by ID"""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"message": f"Conversation {conversation_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")

@app.get("/conversations")
async def list_conversations():
    """List all conversation IDs"""
    return {"conversations": list(conversations.keys())}

@app.get("/health")
async def health_check():
    """Check if the API is healthy"""
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
