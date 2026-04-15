# Houdini MCP Server

Minimal Model Context Protocol (MCP) server for integrating Houdini with OpenCode and other MCP clients.

## Features

- **execute_python**: Execute arbitrary Python code within Houdini's context with full access to the `hou` module
- **get_scene_info**: Get information about the current Houdini scene (hip file, frame range, selected nodes, etc.)

## Architecture

Due to Houdini 20.5's custom asyncio implementation being incompatible with the MCP SDK, this server uses an HTTP bridge:

```
OpenCode ←→ MCP Server ←→ HTTP ←→ RPC Service ←→ Houdini
         stdio      (venv)     :9876    (inside Houdini)
```

- **MCP Server** (`houdini_mcp_server.py`) - Runs in standard Python venv, handles MCP protocol via stdio
- **RPC Service** (`houdini_rpc_service.py`) - Runs inside Houdini on port 9876, executes code with `hou` module

## Setup (3 steps)

### 1. Create Python Virtual Environment

```bash
cd /Users/YOUR_USERNAME/Library/Preferences/houdini/20.5/houdini-mcp-server
python3 -m venv venv
source venv/bin/activate
pip install mcp httpx
deactivate
```

### 2. Symlink Houdini Package

```bash
ln -s "$(pwd)/houdini_mcp_server.json" "$HOME/Library/Preferences/houdini/20.5/packages/houdini_mcp_server.json"
```

### 3. Configure OpenCode

Edit `~/.config/opencode/opencode.json`:

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

Replace `YOUR_USERNAME` with your actual username.

## Usage

### Start RPC Service in Houdini

Before using the MCP server, you must start the RPC service inside Houdini. Copy and paste this code into the Houdini Python Shell:

```python
import sys
sys.path.insert(0, '/Users/YOUR_USERNAME/Library/Preferences/houdini/20.5/houdini-mcp-server/python')
from houdini_rpc_service import start_server
start_server()
```

Or use the provided shelf tool: `MCP_Server.shelf` (add to your shelf and click to start).

The RPC service runs on `http://localhost:9876` and must be running for the MCP server to work.

### Example Interactions

Once configured and the RPC service is running, interact with Houdini from OpenCode:

```
Create a geometry node with a sphere inside it
```

```
What's the current frame and how many nodes are selected?
```

```
Execute this code: 
for i in range(5):
    hou.node('/obj').createNode('geo', f'geo_{i}')
```

## Available Tools

### execute_python

Execute arbitrary Python code within Houdini's context with full `hou` module access.

**Parameters:**
- `code` (string): Python code to execute

**Returns:** Execution result or printed output

**Example:**
```python
geo = hou.node('/obj').createNode('geo')
sphere = geo.createNode('sphere')
sphere.parm('rad').set(2.5)
print(f"Created {sphere.path()}")
```

### get_scene_info

Get comprehensive information about the current Houdini scene.

**Parameters:** None

**Returns:**
- Hip file path and name
- Frame range (start, end, current)
- FPS
- Selected nodes
- Current working directory  
- Houdini version

## Project Structure

```
houdini-mcp-server/
├── .git/                          # Git repository
├── .gitignore                     # Git ignore patterns
├── houdini_mcp_server.json        # Houdini package definition
├── MCP_Server.shelf               # Shelf tool to start RPC service
├── START_IN_HOUDINI.py            # Copy-paste startup script
├── README.md                      # This file
├── venv/                          # Python virtual environment (mcp + httpx)
└── python/
    ├── houdini_mcp_server.py      # MCP server (runs in venv)
    └── houdini_rpc_service.py     # RPC service (runs in Houdini)
```

## Troubleshooting

**RPC service not running:**
- Start it in Houdini Python Shell using `START_IN_HOUDINI.py` or the shelf tool
- Check that port 9876 is not already in use

**OpenCode shows server disconnected:**
- Verify venv paths in `opencode.json` are correct
- Check that venv has `mcp` and `httpx` installed: `venv/bin/pip list`
- Restart OpenCode after config changes

**"Connection refused" errors:**
- RPC service must be running inside Houdini before using MCP server
- Verify RPC service is listening: `curl http://localhost:9876/execute -d '{"code":"print(123)"}'`

## Known Limitations

- RPC service must be manually started in Houdini each session (no auto-start)
- Uses polling HTTP instead of WebSocket (adequate performance for typical usage)
- Houdini's asyncio incompatibility prevents running MCP server directly in hython

## Tested Environment

- macOS
- Houdini 20.5.613
- Python 3.11 (venv)
- OpenCode with MCP support

## License

MIT
