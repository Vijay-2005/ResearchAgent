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
    "APIFY_API_KEY",
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
    allow_origins=["https://www.siliconsynapse.in", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["Content-Type"],
    max_age=600
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
            
            # Return results with content formatting information
            return {
                "conversation_id": conversation_id,
                "messages": updated_messages,
                "format_info": {
                    "content_type": "markdown",
                    "rendering_instructions": {
                        "headings": "Use proper heading elements (h1-h6) for lines starting with # symbols",
                        "emphasis": "Render * and _ wrapped text as italic, ** and __ as bold",
                        "lists": "Render proper ordered and unordered lists for lines starting with numbers or - symbols",
                        "code_blocks": "Properly format code blocks surrounded by ``` marks"
                    }
                }
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
                    "error": str(e),
                    "format_info": {
                        "content_type": "markdown",
                        "rendering_instructions": {
                            "headings": "Use proper heading elements (h1-h6) for lines starting with # symbols",
                            "emphasis": "Render * and _ wrapped text as italic, ** and __ as bold",
                            "lists": "Render proper ordered and unordered lists for lines starting with numbers or - symbols",
                            "code_blocks": "Properly format code blocks surrounded by ``` marks"
                        }
                    }
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

@app.get("/frontend-endpoints")
async def frontend_endpoints():
    """Returns a structured list of available endpoints for frontend integration"""
    # Information about available endpoints for the frontend
    return {
        "api_version": "1.0.0",
        "base_url": os.environ.get("API_URL", f"http://localhost:{os.environ.get('PORT', 8000)}"),
        "endpoints": [
            {
                "path": "/chat",
                "method": "POST",
                "description": "Chat with the AI Research Assistant",
                "request_format": {
                    "conversation_id": "Optional string to continue a conversation",
                    "message": "User's message (required)",
                    "model": "Optional model name ('openai' or 'anthropic')"
                },
                "response_format": {
                    "conversation_id": "String ID for the conversation",
                    "messages": "Array of message objects with role and content"
                }
            },
            {
                "path": "/conversations",
                "method": "GET",
                "description": "List all active conversation IDs",
                "response_format": {
                    "conversations": "Array of conversation IDs"
                }
            },
            {
                "path": "/conversations/{conversation_id}",
                "method": "DELETE",
                "description": "Delete a specific conversation",
                "response_format": {
                    "message": "Success message"
                }
            },
            {
                "path": "/health",
                "method": "GET",
                "description": "Check API health status",
                "response_format": {
                    "api": "Status string",
                    "key_statuses": "Boolean values for each API key"
                }
            },
            {
                "path": "/api-status",
                "method": "GET",
                "description": "Get detailed API configuration status",
                "response_format": {
                    "api_keys": "Status of each API key",
                    "available_tools": "List of available research tools"
                }
            }
        ],
        "research_capabilities": [
            "Web search (via Tavily, Google/Serper, and Metaphor)",
            "Website content extraction",
            "E-commerce website scraping (via Apify)"
        ]
    }

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