#!/usr/bin/env python
"""Test script to verify the MCP server can be imported and initialized"""

import sys

# Test import
try:
    import hou
    print(f"✓ hou module available: {hou.applicationVersionString()}")
except ImportError as e:
    print(f"✗ hou module NOT available: {e}")
    sys.exit(1)

try:
    import mcp
    print(f"✓ mcp module available: {mcp.__version__ if hasattr(mcp, '__version__') else 'unknown version'}")
except ImportError as e:
    print(f"✗ mcp module NOT available: {e}")
    sys.exit(1)

# Test server initialization
try:
    sys.path.insert(0, "/Users/kif/Library/Preferences/houdini/20.5/houdini-mcp-server/python")
    from houdini_mcp_server import HoudiniMCPServer
    print("✓ HoudiniMCPServer imported successfully")
    
    server = HoudiniMCPServer()
    print("✓ HoudiniMCPServer instance created successfully")
    print(f"✓ Server name: {server.server.name}")
    
except Exception as e:
    print(f"✗ Failed to initialize server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ All tests passed! Server is ready to use.")
