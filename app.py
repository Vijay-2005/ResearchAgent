import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import uvicorn
from typing import Dict, List, Any, Optional

# Import our agent
from my_agent.agent import graph  # Use the compiled graph instead of workflow
from my_agent.utils.state import AgentState

# Load environment variables first thing
load_dotenv()

# All API keys to verify
API_KEYS = [
    "TAVILY_API_KEY", 
    "OPENAI_API_KEY",
    "SERPER_API_KEY",
    "METAPHOR_API_KEY", 
    "BROWSERLESS_API_KEY",
    "LANGCHAIN_API_KEY",
    "LANGSMITH_API_KEY"
]

# Verify all keys are available
print("\n===== API KEYS STATUS =====")
for key in API_KEYS:
    value = os.environ.get(key)
    if value:
        masked_value = value[:5] + "..." + value[-4:] if len(value) > 10 else "***"
        print(f"✅ {key}: {masked_value}")
    else:
        print(f"⚠️ Warning: {key} not found in environment variables!")
print("===========================\n")

# Create the FastAPI app with explicit configuration
app = FastAPI(
    title="AI Research Assistant",
    description="API for AI Research Assistant",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

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
    return {"message": "AI Research Assistant API is running. See /docs for API documentation."}
    
@app.get("/debug")
async def debug_info():
    """Return debug information about the API and route configuration"""
    routes = [
        {
            "path": route.path,
            "name": route.name,
            "methods": route.methods
        }
        for route in app.routes
    ]
    
    return {
        "routes": routes,
        "api_version": "1.0.0",
        "environment": {
            "port": os.environ.get("PORT", "Not set"),
            "api_url": os.environ.get("API_URL", "Not set"),
            "python_version": sys.version,
        }
    }

@app.post("/chat")
async def chat(request: Dict[str, Any] = Body(...)):
    """
    Chat with the agent.
    
    Expects a JSON body with:
    - conversation_id: Optional ID to continue a conversation
    - message: The user's message
    - model: Optional model to use ("openai" or "anthropic")
    """
    print("POST /chat endpoint called with body:", request)
    
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
        
        # Debug environment variables - show status for all keys
        print("\n----- Using API Keys -----")
        for key_name in API_KEYS:
            key_value = os.environ.get(key_name, 'Not set')
            mask = key_value[:5] + '...' + key_value[-4:] if len(key_value) > 10 else 'Not set or too short'
            print(f"Using {key_name}: {mask}")
        print("--------------------------\n")
        
        # Check if essential keys are valid before proceeding
        openai_key = os.environ.get('OPENAI_API_KEY', 'Not set')
        if openai_key == 'Not set' or len(openai_key) < 10:
            raise ValueError("OPENAI_API_KEY is not properly set in the environment")
            
        # Configure with the model
        config = {"configurable": {"model_name": model_name}}
        
        # Invoke the agent
        try:
            print(f"Invoking graph with model: {model_name}")
            # Use the compiled graph instead of workflow
            result = graph.invoke(state, config=config)
            print("Graph invocation successful")
            
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
    # Return detailed status about API keys
    status = {key: bool(os.environ.get(key)) for key in API_KEYS}
    status["api"] = "healthy"
    return status

@app.get("/api-status")
async def api_status():
    """Get detailed status of configured APIs"""
    api_status = {}
    
    # Check all API keys
    for key in API_KEYS:
        value = os.environ.get(key)
        api_status[key] = {
            "configured": bool(value),
            "length": len(value) if value else 0,
            "valid_format": len(value) > 10 if value else False
        }
    
    # Check tools from research_tools
    try:
        from my_agent.utils.research_tools import research_tools
        api_status["available_tools"] = [tool.name for tool in research_tools]
        api_status["tool_count"] = len(research_tools)
    except ImportError:
        api_status["available_tools"] = "Error: Could not import research_tools"
    
    return api_status

# Make sure all routes are explicitly registered
def register_routes():
    print("Registered API routes:")
    for route in app.routes:
        print(f" - {route.path} [{', '.join(route.methods if route.methods else [''])}]")

# Register routes explicitly for clarity
register_routes()

if __name__ == "__main__":
    # Get port from environment variable (for cloud deployment) with fallback to 8000
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting FastAPI server on port {port}")
    print(f"Environment variables: API_URL={os.environ.get('API_URL')}, PORT={port}")
    
    # Make sure to bind to 0.0.0.0 to listen on all interfaces
    uvicorn.run(app, host="0.0.0.0", port=port)