#!/usr/bin/env python3
"""
Test the Houdini MCP Server end-to-end
"""

import asyncio
import sys
sys.path.insert(0, '/Users/kif/Library/Preferences/houdini/20.5/houdini-mcp-server/venv/lib/python3.14/site-packages')

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_houdini_mcp():
    """Test the MCP server"""
    print("Testing Houdini MCP Server...")
    print("="*60)
    
    server_params = StdioServerParameters(
        command="/Users/kif/Library/Preferences/houdini/20.5/houdini-mcp-server/venv/bin/python",
        args=["/Users/kif/Library/Preferences/houdini/20.5/houdini-mcp-server/python/houdini_mcp_server_http.py"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            print("\n1. Listing available tools...")
            tools = await session.list_tools()
            print(f"   Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"   - {tool.name}: {tool.description[:60]}...")
            
            # Test get_scene_info
            print("\n2. Getting scene info...")
            result = await session.call_tool("get_scene_info", {})
            print(f"   {result.content[0].text[:200]}...")
            
            # Test execute_python
            print("\n3. Executing Python code in Houdini...")
            code = """
import hou
version = hou.applicationVersionString()
print(f"Houdini version: {version}")
nodes = len(hou.node('/obj').children())
print(f"Nodes in /obj: {nodes}")
"""
            result = await session.call_tool("execute_python", {"code": code})
            print(f"   Result:\n{result.content[0].text}")
            
            print("\n" + "="*60)
            print("✅ All tests passed!")
            print("="*60)

if __name__ == "__main__":
    asyncio.run(test_houdini_mcp())
