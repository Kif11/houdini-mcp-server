#!/usr/bin/env python
"""Test the MCP server tools in Houdini context"""

import sys
import asyncio
sys.path.insert(0, "/Users/kif/Library/Preferences/houdini/20.5/houdini-mcp-server/python")

import hou
from houdini_mcp_server import HoudiniMCPServer

async def test_tools():
    """Test each tool"""
    server = HoudiniMCPServer()
    
    print("=" * 60)
    print("Testing Houdini MCP Server Tools")
    print("=" * 60)
    
    # Test 1: execute_python
    print("\n[Test 1] Testing execute_python tool...")
    try:
        result = await server._execute_python({
            "code": """
import hou
version = hou.applicationVersionString()
print(f"Running Houdini {version}")
nodes = len(hou.node('/obj').children())
print(f"Number of nodes in /obj: {nodes}")
"""
        })
        print("✓ execute_python succeeded:")
        print(result)
    except Exception as e:
        print(f"✗ execute_python failed: {e}")
    
    # Test 2: get_scene_info
    print("\n[Test 2] Testing get_scene_info tool...")
    try:
        result = await server._get_scene_info({})
        print("✓ get_scene_info succeeded:")
        print(result)
    except Exception as e:
        print(f"✗ get_scene_info failed: {e}")
    
    # Test 3: evaluate_expression
    print("\n[Test 3] Testing evaluate_expression tool...")
    try:
        result = await server._evaluate_expression({
            "expression": "hou.frame()",
            "expression_language": "python"
        })
        print("✓ evaluate_expression succeeded:")
        print(f"Current frame: {result}")
    except Exception as e:
        print(f"✗ evaluate_expression failed: {e}")
    
    # Test 4: Create a node using execute_python
    print("\n[Test 4] Testing node creation via execute_python...")
    try:
        result = await server._execute_python({
            "code": """
import hou
# Create a geometry node
geo = hou.node('/obj').createNode('geo', 'test_geo')
# Create a sphere inside
sphere = geo.createNode('sphere', 'test_sphere')
print(f"Created: {geo.path()}")
print(f"Created: {sphere.path()}")
# Return the paths
_ = [geo.path(), sphere.path()]
"""
        })
        print("✓ Node creation succeeded:")
        print(result)
    except Exception as e:
        print(f"✗ Node creation failed: {e}")
    
    print("\n" + "=" * 60)
    print("✅ All tool tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_tools())
