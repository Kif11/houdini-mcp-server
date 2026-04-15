"""
Houdini MCP Server Launcher
Starts the MCP server in a background thread within a running Houdini session
"""

import sys
import threading
import asyncio

# Add the MCP server to the path
sys.path.insert(0, "/Users/kif/Library/Preferences/houdini/20.5/houdini-mcp-server/python")

from houdini_mcp_server import HoudiniMCPServer

# Global server instance
_mcp_server = None
_mcp_thread = None


def start_mcp_server():
    """Start the MCP server in a background thread"""
    global _mcp_server, _mcp_thread
    
    if _mcp_thread and _mcp_thread.is_alive():
        print("MCP server is already running")
        return
    
    def run_server():
        """Run the server in a thread"""
        try:
            _mcp_server = HoudiniMCPServer()
            # Use new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_mcp_server.run())
        except Exception as e:
            print(f"MCP Server error: {e}")
            import traceback
            traceback.print_exc()
    
    _mcp_thread = threading.Thread(target=run_server, daemon=True)
    _mcp_thread.start()
    print("✓ Houdini MCP Server started successfully")
    print("  OpenCode can now connect to this Houdini session")


def stop_mcp_server():
    """Stop the MCP server"""
    global _mcp_server, _mcp_thread
    
    if _mcp_thread and _mcp_thread.is_alive():
        print("Stopping MCP server...")
        # The thread is daemon so it will stop when Houdini closes
        _mcp_server = None
        _mcp_thread = None
        print("✓ MCP server stopped")
    else:
        print("MCP server is not running")


if __name__ == "__main__":
    # When executed as a shelf tool
    start_mcp_server()
