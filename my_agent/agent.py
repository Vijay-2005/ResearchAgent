
# Import auth setup FIRST before any other imports
from my_agent.utils.auth_setup import api_keys

from typing import TypedDict, Literal
import os

from langgraph.graph import StateGraph, END
from my_agent.utils.mcp_client import mcp_client, MCP_CONFIG
from my_agent.utils.nodes import call_model, should_continue, tool_node
from my_agent.utils.state import AgentState

# Define the config
class GraphConfig(TypedDict):
    model_name: Literal["openai"]

# Define a new graph
workflow = StateGraph(AgentState, config_schema=GraphConfig)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
workflow.set_entry_point("agent")

# Add conditional edges from agent node
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END,
    },
)

# Add edge from action back to agent
workflow.add_edge("action", "agent")

# Compile the graph
graph = workflow.compile()
