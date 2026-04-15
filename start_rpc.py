#!/usr/bin/env hython
"""
Start the Houdini RPC service
This connects to the running Houdini session and starts the HTTP server
"""

import sys
import os

# Add the MCP server to the path
sys.path.insert(0, '/Users/kif/Library/Preferences/houdini/20.5/houdini-mcp-server/python')

try:
    import hou
    print(f"Connected to Houdini {hou.applicationVersionString()}")
    
    import houdini_rpc_service
    
    print("\nStarting Houdini RPC Service...")
    houdini_rpc_service.start_rpc_server(port=9876)
    
except KeyboardInterrupt:
    print("\nRPC service stopped")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
