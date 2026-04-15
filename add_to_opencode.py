#!/usr/bin/env python3
"""
Script to manually add Houdini MCP server to OpenCode configuration
"""

import json
import os
from pathlib import Path

CONFIG_PATH = Path.home() / ".config" / "opencode" / "opencode.json"

# Read existing config
if CONFIG_PATH.exists():
    with open(CONFIG_PATH) as f:
        config = json.load(f)
else:
    config = {}

# Add Houdini MCP server
# Try different possible key names based on common MCP configurations
possible_keys = ["mcp", "mcpServers", "servers", "mcp_servers"]

# Let's add to all possible keys to see which one works
houdini_server = {
    "command": "/Applications/Houdini/Houdini20.5.613/Frameworks/Houdini.framework/Versions/20.5/Resources/bin/hython",
    "args": [
        "/Users/kif/Library/Preferences/houdini/20.5/houdini-mcp-server/python/houdini_mcp_server.py"
    ]
}

# Try the most standard MCP format
if "mcp" not in config:
    config["mcp"] = {}

config["mcp"]["houdini"] = houdini_server

# Write config
with open(CONFIG_PATH, 'w') as f:
    json.dump(config, f, indent=2)

print(f"✓ Added Houdini MCP server to {CONFIG_PATH}")
print(json.dumps(config, indent=2))
