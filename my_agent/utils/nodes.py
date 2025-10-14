from functools import lru_cache
from langchain_openai import ChatOpenAI
from my_agent.utils.research_tools import research_tools
from langgraph.prebuilt import ToolNode
import os

# Import the MCP client and tools from mcp_client module
from my_agent.utils.mcp_client import mcp_client, mcp_tools_list, list_mcp_tools
import asyncio

# Combine local tools with MCP tools
all_tools = research_tools.copy()

# Function to load MCP tools into all_tools
def integrate_mcp_tools():
    global mcp_tools_list
    if mcp_tools_list:
        # Add MCP tools to all_tools
        all_tools.extend(mcp_tools_list)
        tool_names = [tool.name for tool in mcp_tools_list]
        print(f"✅ Integrated {len(mcp_tools_list)} MCP tools into agent: {', '.join(tool_names)}\n")
        return mcp_tools_list
    elif mcp_client:
        # If tools weren't loaded during initialization, try now
        try:
            print("⏳ Loading MCP tools now...")
            loop = asyncio.get_event_loop()
            if loop.is_running():
                print("⚠️ Event loop is running, tools will be loaded later")
                return []
            else:
                tools = loop.run_until_complete(list_mcp_tools())
                all_tools.extend(tools)
                return tools
        except Exception as e:
            print(f"❌ Error loading MCP tools: {str(e)}")
            return []
    return []

# Try to integrate MCP tools
mcp_tools = integrate_mcp_tools()

@lru_cache(maxsize=1)
def _get_model(model_name: str):
    print(f"Creating model instance for: {model_name}")
    # Print the first few characters of the key for debugging
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        print(f"OPENAI_API_KEY found in environment: {openai_key[:5]}...")
    else:
        print("WARNING: OPENAI_API_KEY not found in environment")

    try:
        print("Initializing OpenAI model...")
        # Using gpt-4o-mini for cost-effective performance
        model = ChatOpenAI(
            temperature=1, 
            model_name="gpt-5-nano",
            api_key=openai_key
        )
        
        # Bind tools to the model
        model = model.bind_tools(all_tools)
        return model
    except Exception as e:
        import traceback
        print(f"Error initializing model: {str(e)}")
        print(traceback.format_exc())
        raise

# Define the function that determines whether to continue or not
def should_continue(state):
    messages = state["messages"]
    last_message = messages[-1]
    # If there are no tool calls, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"

# System prompt for research tools
def generate_system_prompt():
    """Dynamically generate system prompt based on available tools."""
    base_prompt = "You are an AI research assistant with access to web search and MCP tools.\n\n"
    
    tool_descriptions = []
    
    # Add web search tool description
    tool_descriptions.append("- web_search: For searching the web for information")
    
    # Add MCP tool descriptions if available
    if mcp_tools:
        for tool in mcp_tools:
            tool_descriptions.append(f"- {tool.name}: {tool.description}")
    
    # Add usage instructions
    instructions = "\nWhen a user asks about searching for information on the web, use the web_search tool."
    if mcp_tools:
        instructions += "\nFor Google-related tasks, use the appropriate MCP Google tools."
    
    # Combine all parts
    full_prompt = base_prompt + "You can use the following tools:\n" + "\n".join(tool_descriptions) + instructions
    
    return full_prompt

# Generate the system prompt
SYSTEM_PROMPT = generate_system_prompt()

# Define the function that calls the model
def call_model(state, config):
    from my_agent.utils.guardrails import validate_request
    
    messages = state["messages"]
    
    # Get the last user message for guardrails check
    last_user_message = None
    for msg in reversed(messages):
        if hasattr(msg, 'type') and msg.type == 'human':
            last_user_message = msg.content
            break
        elif isinstance(msg, dict) and msg.get('role') == 'user':
            last_user_message = msg.get('content')
            break
    
    # Apply guardrails if we have a user message
    if last_user_message:
        # Convert to string if it's a list (multimodal messages)
        if isinstance(last_user_message, list):
            last_user_message_str = " ".join([str(item.get("text", item)) if isinstance(item, dict) else str(item) for item in last_user_message])
        else:
            last_user_message_str = str(last_user_message)
        
        validation = validate_request(last_user_message)
        print(f"🛡️ Guardrails check: {validation}")
        
        # Block unsafe requests
        if not validation["allowed"]:
            from langchain_core.messages import AIMessage
            blocked_response = AIMessage(content=validation["reason"])
            return {"messages": [blocked_response]}
        
        # Request confirmation for sensitive operations
        if validation["requires_confirmation"] and "confirmed" not in last_user_message_str.lower():
            from langchain_core.messages import AIMessage
            confirm_response = AIMessage(content=validation["confirmation_message"])
            return {"messages": [confirm_response]}
    
    # Proceed with normal model call
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    model_name = config.get('configurable', {}).get("model_name", "openai")
    model = _get_model(model_name)
    response = model.invoke(messages)
    return {"messages": [response]}

# Define the function to execute tools
tool_node = ToolNode(all_tools)