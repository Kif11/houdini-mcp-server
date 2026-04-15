#!/usr/bin/env python
"""
Debug wrapper for Houdini MCP Server
Logs all activity to help diagnose connection issues
"""

import sys
import os
from datetime import datetime

# Setup logging
log_file = "/tmp/houdini_mcp_debug.log"

def log(message):
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now()}] {message}\n")
        f.flush()

log("=" * 60)
log("Houdini MCP Server Debug Starting")
log(f"Python: {sys.version}")
log(f"Executable: {sys.executable}")

# Add the MCP server to the path
sys.path.insert(0, "/Users/kif/Library/Preferences/houdini/20.5/houdini-mcp-server/python")

try:
    log("Importing hou module...")
    import hou
    log(f"✓ hou module imported: {hou.applicationVersionString()}")
except ImportError as e:
    log(f"✗ Failed to import hou: {e}")
    sys.exit(1)

try:
    log("Importing MCP SDK...")
    import mcp
    log("✓ MCP SDK imported")
except ImportError as e:
    log(f"✗ Failed to import MCP SDK: {e}")
    sys.exit(1)

try:
    log("Importing houdini_mcp_server...")
    from houdini_mcp_server import main
    log("✓ houdini_mcp_server imported")
    
    log("Starting MCP server...")
    main()
except Exception as e:
    log(f"✗ Error: {e}")
    import traceback
    log(traceback.format_exc())
    sys.exit(1)
