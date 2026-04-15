# Houdini MCP Server

Model Context Protocol (MCP) server for integrating Houdini with OpenCode and other MCP clients.

This server runs within Houdini's Python environment and provides access to Houdini's APIs through the MCP protocol.

## Features

- **execute_python**: Execute arbitrary Python code within Houdini's context with full access to the `hou` module
- **get_scene_info**: Get information about the current Houdini scene
- **evaluate_expression**: Evaluate Houdini expressions (Hscript or Python)

## Installation

### 1. Install MCP SDK in Houdini's Python

Houdini uses its own Python installation. You need to install the MCP SDK into Houdini's Python:

```bash
# Tested on macOS with Houdini 20.5.613
# Find Houdini's Python executable (hython)

# Install MCP using hython
hython -m pip install mcp

# Or use the full path:
/Applications/Houdini/Houdini20.5.613/Frameworks/Houdini.framework/Versions/20.5/Resources/bin/hython -m pip install mcp
```

### 2. Install the Package

Create a symlink from Houdini's packages directory to this package:

```bash
# From the houdini-mcp-server directory
ln -s "$(pwd)/houdini_mcp_server.json" "$HOME/Library/Preferences/houdini/20.5/packages/houdini_mcp_server.json"
```

Or manually copy `houdini_mcp_server.json` to `$HOME/Library/Preferences/houdini/20.5/packages/`

### 3. Configure OpenCode

Add the server to your OpenCode MCP settings. Open your OpenCode settings and add:

```json
{
  "mcpServers": {
    "houdini": {
      "command": "/Applications/Houdini/Houdini20.5.*/Frameworks/Python.framework/Versions/Current/bin/python3",
      "args": [
        "/Users/YOUR_USERNAME/Library/Preferences/houdini/20.5/houdini-mcp-server/python/houdini_mcp_server.py"
      ],
      "env": {
        "HOUDINI_PATH": "/Users/YOUR_USERNAME/Library/Preferences/houdini/20.5/houdini-mcp-server;&"
      }
    }
  }
}
```

**Important**: Replace `YOUR_USERNAME` and adjust the Houdini version path as needed.

Alternative using `hython`:

```json
{
  "mcpServers": {
    "houdini": {
      "command": "hython",
      "args": [
        "/Users/YOUR_USERNAME/Library/Preferences/houdini/20.5/houdini-mcp-server/python/houdini_mcp_server.py"
      ]
    }
  }
}
```

## Usage

Once configured, you can interact with Houdini from OpenCode:

### Execute Python Code

```
Execute this Python code in Houdini:
node = hou.node('/obj').createNode('geo', 'my_geometry')
print(f"Created node: {node.path()}")
```

### Get Scene Information

```
What's the current state of my Houdini scene?
```

### Evaluate Expressions

```
Evaluate the expression: hou.frame()
```

## Tools Available

### execute_python

Execute arbitrary Python code within Houdini's context.

**Parameters:**
- `code` (required): Python code to execute
- `return_type` (optional): How to format the return value (`auto`, `string`, `json`)

**Example:**
```python
# Create a sphere
geo = hou.node('/obj').createNode('geo')
sphere = geo.createNode('sphere')
print(f"Created sphere at {sphere.path()}")
```

### get_scene_info

Get comprehensive information about the current Houdini scene.

**Returns:**
- Hip file path and name
- Frame range and current frame
- FPS
- Selected nodes
- Current working directory
- Houdini version

### evaluate_expression

Evaluate a Houdini expression.

**Parameters:**
- `expression` (required): The expression to evaluate
- `expression_language` (optional): `python` or `hscript` (default: `python`)

## Development

### Project Structure

```
houdini-mcp-server/
├── houdini_mcp_server.json    # Houdini package definition
├── python/
│   └── houdini_mcp_server.py  # MCP server implementation
├── requirements.txt
├── setup.py
└── README.md
```

### Running Tests

The server has been tested and verified working with Houdini 20.5.613 on macOS.

To run the included test suite:

```bash
# Test server initialization
hython houdini-mcp-server/test_server.py

# Test all tools
hython houdini-mcp-server/test_tools.py
```

**Test Results (Verified):**
- ✅ execute_python: Successfully executes Python code in Houdini context
- ✅ get_scene_info: Returns complete scene information including frame range, selected nodes, etc.
- ✅ evaluate_expression: Evaluates both Python and Hscript expressions
- ✅ Node creation: Can create and manipulate Houdini nodes programmatically

You can also test it through OpenCode once configured:

1. Configure OpenCode with the MCP server (see above)
2. Restart OpenCode to load the server
3. Send commands like "Create a geometry node in Houdini" or "What's the current frame?"

### Adding New Tools

To add new tools, edit `python/houdini_mcp_server.py`:

1. Add a new `Tool` definition in the `list_tools()` handler
2. Add the corresponding handler method (e.g., `_my_new_tool`)
3. Add a case in the `call_tool()` handler

## Troubleshooting

### "hou module not available"

The server must run using Houdini's Python (hython or Houdini's bundled Python), not your system Python.

### MCP module not found

Install the MCP SDK in Houdini's Python:
```bash
hython -m pip install mcp
```

### Server not responding

Check that:
1. Houdini is running
2. The paths in your OpenCode MCP configuration are correct
3. The server script has execute permissions

## License

MIT

## Contributing

Contributions welcome! Please submit pull requests or open issues.
