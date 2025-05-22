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
    try:
        # Extract parameters from request
        conversation_id = request.get("conversation_id", None)
        message = request.get("message")
        model_name = request.get("model", "openai")
        
        # Debug logging
        print(f"Received chat request: model={model_name}, message={message}, conv_id={conversation_id}")
        
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
        
        # Debug environment variables
        openai_key = os.environ.get('OPENAI_API_KEY', 'Not set')
        tavily_key = os.environ.get('TAVILY_API_KEY', 'Not set')
        
        print(f"Using OPENAI_API_KEY: {openai_key[:5] + '...' if len(openai_key) > 5 else 'Not set or too short'}")
        print(f"Using TAVILY_API_KEY: {tavily_key[:5] + '...' if len(tavily_key) > 5 else 'Not set or too short'}")
        
        # Check if keys are valid before proceeding
        if openai_key == 'Not set' or len(openai_key) < 10:
            raise ValueError("OPENAI_API_KEY is not properly set in the environment")
          
        # Configure with the model
        config = {"configurable": {"model_name": model_name}}
        
        # Invoke the agent
        try:
            print(f"Invoking workflow with model: {model_name}")
            result = workflow.invoke(state, config=config)
            print("Workflow invocation successful")
            
            # Get the updated messages
            updated_messages = result["messages"]
            
            # Save the updated conversation
            conversations[conversation_id] = updated_messages
            
            # Return results
            return {
                "conversation_id": conversation_id,
                "messages": updated_messages
            }
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error during workflow invocation: {str(e)}")
            print(error_trace)
            
            # Create a graceful error response
            error_message = {"role": "assistant", "content": f"I'm sorry, I encountered an error: {str(e)}. Please try again."}
            messages.append(error_message)
            conversations[conversation_id] = messages
            
            return JSONResponse(
                status_code=200,  # Return 200 but with error message to client
                content={
                    "conversation_id": conversation_id,
                    "messages": messages,
                    "error": str(e)
                }
            )
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"API error: {str(e)}")
        print(error_trace)
        
        return JSONResponse(
            status_code=500,
            content={"detail": f"Server error: {str(e)}"}
        )

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
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the Knowledge Navigator API")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the API on")
    args = parser.parse_args()
    
    # Get port from command line args or environment or default
    port = args.port or int(os.environ.get("API_PORT", 8000))
    
    print(f"Starting FastAPI server on port {port}")
    # Log more details about the environment
    print(f"Environment variables: API_URL={os.environ.get('API_URL')}, PORT={os.environ.get('PORT')}")
        
    uvicorn.run(app, host="0.0.0.0", port=port)
