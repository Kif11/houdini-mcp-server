# Houdini MCP Server

Control Houdini from AI assistants via the Model Context Protocol (MCP).

## What It Does

Allows MCP-compatible AI tools (like Claude Desktop, Cursor, etc.) to:
- Execute Python code in Houdini with full `hou` module access
- Query scene information (nodes, frames, selection, etc.)
- Create and manipulate nodes programmatically

## Install

### 1. Clone this repo
```bash
cd ~/Library/Preferences/houdini/20.5/  # macOS
git clone https://github.com/YOUR_USERNAME/houdini-mcp-server
```

### 2. Create Python venv
```bash
cd houdini-mcp-server
python3 -m venv venv
source venv/bin/activate
pip install mcp httpx
deactivate
```

### 3. Install shelf tools (one-liner in Houdini Python Shell)
```python
exec(open('/Users/YOUR_USERNAME/Library/Preferences/houdini/20.5/houdini-mcp-server/install_mcp_shelf.py').read())
```

### 4. Configure your AI client

**Claude Desktop** (`~/.config/claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "houdini": {
      "command": "/Users/YOUR_USERNAME/Library/Preferences/houdini/20.5/houdini-mcp-server/venv/bin/python",
      "args": [
        "/Users/YOUR_USERNAME/Library/Preferences/houdini/20.5/houdini-mcp-server/python/houdini_mcp_server.py"
      ]
    }
  }
}
```

**Cursor** - Same config in Settings → MCP

## Usage

1. **Start Houdini** and click the "Start MCP" shelf button
2. **Start your AI client** (Claude Desktop, Cursor, etc.)
3. **Ask the AI** to control Houdini

### Examples

**Create geometry:**
```
Create a sphere and a box in Houdini, position them 5 units apart
```

**Query scene:**
```
What nodes are currently selected in Houdini?
```

**Execute Python:**
```
In Houdini, create 10 random spheres with varying radii between 0.5 and 2.0
```

**Complex operations:**
```
Create a scatter SOP with 1000 points on a grid, then copy spheres to each point
```

## Available Tools

- **`execute_python`** - Run arbitrary Python code with `hou` module access
- **`get_scene_info`** - Get hip file path, frame range, selected nodes, FPS, etc.

## Requirements

- Houdini 20.5+ (tested on macOS)
- Python 3.11+
- MCP-compatible AI client

## Architecture

```
AI Client ←→ MCP Server ←→ HTTP ←→ RPC Service ←→ Houdini
         stdio      (venv)    :9876   (inside Houdini)
```

Uses HTTP bridge because Houdini's asyncio implementation is incompatible with MCP SDK.

## License

MIT
