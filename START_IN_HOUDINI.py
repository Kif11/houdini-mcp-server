"""
COPY AND PASTE THIS INTO HOUDINI'S PYTHON SHELL
(Windows > Python Shell in Houdini)
"""

import sys
sys.path.insert(0, '/Users/kif/Library/Preferences/houdini/20.5/houdini-mcp-server/python')

import houdini_rpc_service

# Start the RPC service in background
if not hasattr(hou.session, 'mcp_rpc_thread'):
    hou.session.mcp_rpc_thread = houdini_rpc_service.start_rpc_server_thread(port=9876)
    print("\n" + "="*60)
    print("✓ Houdini MCP RPC Service started on http://localhost:9876")
    print("  OpenCode can now connect to this Houdini session")
    print("="*60 + "\n")
else:
    print("MCP RPC Service is already running")
