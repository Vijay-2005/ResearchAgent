from functools import lru_cache
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from my_agent.utils.tools import tools
from langgraph.prebuilt import ToolNode


@lru_cache(maxsize=4)
def _get_model(model_name: str):
    print(f"Creating model instance for: {model_name}")
    import os
    # Print the first few characters of the key for debugging
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        print(f"OPENAI_API_KEY found in environment: {openai_key[:5]}...")
    else:
        print("WARNING: OPENAI_API_KEY not found in environment")

    try:
        if model_name == "openai":
            print("Initializing OpenAI model...")
            # Be explicit about the API key to avoid any environment issues
            model = ChatOpenAI(
                temperature=0, 
                model_name="gpt-4o",
                api_key=openai_key
            )
            # Test that the model works by making a simple call
            print("Testing OpenAI model connection...")
            test_response = model.invoke([{"role": "user", "content": "Hello"}])
            print(f"OpenAI test successful: {test_response.content[:20]}...")
        elif model_name == "anthropic":
            anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
            if not anthropic_key or anthropic_key == "...":
                print("Anthropic API key not found or is placeholder. Falling back to OpenAI.")
                return _get_model("openai")
                
            model = ChatAnthropic(
                temperature=0, 
                model_name="claude-3-sonnet-20240229",
                api_key=anthropic_key
            )
            # Test that the model works by making a simple call
            print("Testing Anthropic model connection...")
            test_response = model.invoke([{"role": "user", "content": "Hello"}])
            print(f"Anthropic test successful: {test_response.content[:20]}...")
        else:
            raise ValueError(f"Unsupported model type: {model_name}")

        model = model.bind_tools(tools)
        return model
    except Exception as e:
        import traceback
        print(f"Error initializing model {model_name}: {str(e)}")
        print(traceback.format_exc())
        
        # Fall back to a more basic approach if we're having trouble
        if model_name == "openai" and openai_key:
            print("Trying fallback initialization for OpenAI...")
            try:
                from openai import OpenAI
                # Create a basic client object
                client = OpenAI(api_key=openai_key)
                test_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": "Hello"}]
                )
                print(f"Direct OpenAI test succeeded: {test_response.choices[0].message.content[:20]}...")
                # If we can't use the LangChain wrapper, raise the original error
                raise e
            except Exception as direct_error:
                print(f"Direct OpenAI call also failed: {direct_error}")
                
        # Fall back to OpenAI if there's an error with the requested model
        if model_name != "openai":
            print("Falling back to OpenAI model...")
            return _get_model("openai")
        else:
            # If we're already trying OpenAI and it's failing, raise the error
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


system_prompt = """Be a helpful assistant"""

# Define the function that calls the model
def call_model(state, config):
    messages = state["messages"]
    messages = [{"role": "system", "content": system_prompt}] + messages
    # Use OpenAI as default instead of anthropic
    model_name = config.get('configurable', {}).get("model_name", "openai")
    model = _get_model(model_name)
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}

# Define the function to execute tools
tool_node = ToolNode(tools)