# Houdini MCP Server

Control Houdini from AI assistants via the Model Context Protocol (MCP).

## What It Does

Allows MCP-compatible AI tools (like OpenCode, Claude Desktop, etc.) to:
- Execute Python code in Houdini with full `hou` module access
- Query scene information (nodes, frames, selection, etc.)
- Create and manipulate nodes programmatically

## Install

### 1. Clone this repo
```bash
cd ~/Library/Preferences/houdini/20.5/  # macOS
git clone https://github.com/YOUR_USERNAME/houdini-mcp-server
```

### 2. Create Python venv and install dependencies
```bash
cd houdini-mcp-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

### 3. Install shelf tools (one-liner in Houdini Python Shell)
```python
exec(open('/Users/YOUR_USERNAME/Library/Preferences/houdini/20.5/houdini-mcp-server/install_mcp_shelf.py').read())
```

### 4. Configure your AI client

**OpenCode** - Edit `~/.config/opencode/opencode.json` and add to the `mcp` section:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "houdini": {
      "type": "local",
      "command": [
        "/Users/YOUR_USERNAME/Library/Preferences/houdini/20.5/houdini-mcp-server/venv/bin/python",
        "/Users/YOUR_USERNAME/Library/Preferences/houdini/20.5/houdini-mcp-server/python/houdini_mcp_server.py"
      ],
      "enabled": true
    }
  }
}
```

More info at [official opencode docs](https://opencode.ai/docs/mcp-servers/).

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

## Usage

1. **Start Houdini** and click the "Start MCP" shelf button
2. **Start your AI client** (OpenCode, Claude Desktop, etc.) and make sure that Houdini MCP is enabled (in opencode `/mcps`)
3. **Make a prompt with Houdini in mind** to control Houdini

### Examples

**Randomize poins**
```
For each scattered point randomize its size, rotation on Y and color.
```

This will most likely create a wrangler node with necessary expressions. 

**Making special effects**
```
On currently selected point wrangler write vex that will display geometry by a wave that pass trough it as I scrub the timeline. Allow for editing wave amplitude, frequency, timing etc.
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

- **`houdini_mcp_server.py`** - Runs outside Houdini in venv, handles MCP protocol
- **`houdini_rpc_service.py`** - Runs inside Houdini, executes code with `hou` module access

Uses HTTP bridge because Houdini's asyncio implementation is incompatible with MCP SDK.

## License

MIT
