"""
MCP Client initialization module.
This module initializes the MultiServerMCPClient.
"""
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

# Define MCP server configuration
MCP_CONFIG = {
     
    # "google-tools": {
    #     "url": "http://52.165.80.198:8837/mcp",
    #     "transport": "streamable_http",
    #     "headers": {}
    # },
     "google-tools": {
        "url": "https://google-workspace-mcp-0p7u.onrender.com/mcp",
        "transport": "streamable_http",
        "headers": {}
    }
}

# Initialize MultiServerMCPClient for MCP integration
mcp_client = None
mcp_tools_list = []

async def list_mcp_tools():
    """List all available tools from the MCP server."""
    global mcp_tools_list
    if mcp_client:
        try:
            print("🔍 Fetching tools from MCP server...")
            tools = await mcp_client.get_tools()
            mcp_tools_list = tools
            
            print("\n===== MCP AVAILABLE TOOLS =====")
            if tools:
                for i, tool in enumerate(tools, 1):
                    print(f"{i}. {tool.name}")
                    if hasattr(tool, 'description') and tool.description:
                        print(f"   Description: {tool.description}")
                print(f"\n✅ Total tools available: {len(tools)}")
            else:
                print("⚠️ No tools found on MCP server")
            print("================================\n")
            
            return tools
        except Exception as e:
            import traceback
            print(f"❌ Error fetching MCP tools: {str(e)}")
            print(traceback.format_exc())
            return []
    return []

try:
    mcp_client = MultiServerMCPClient(MCP_CONFIG)
    print("\n===== MCP CLIENT INITIALIZED =====")
    print(f"✅ Connected to MCP server: {MCP_CONFIG['google-tools']['url']}")
    print(f"✅ Using transport: {MCP_CONFIG['google-tools']['transport']}")
    print("=================================\n")
    
    # List all available tools
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, we'll fetch tools later in nodes.py
            print("⏳ Event loop is running, tools will be fetched asynchronously...")
        else:
            # Fetch tools immediately
            mcp_tools_list = loop.run_until_complete(list_mcp_tools())
    except RuntimeError:
        # If no event loop, create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        mcp_tools_list = loop.run_until_complete(list_mcp_tools())
        
except Exception as e:
    import traceback
    print(f"❌ Error connecting to MCP server: {str(e)}")
    print(traceback.format_exc())
    mcp_client = None

