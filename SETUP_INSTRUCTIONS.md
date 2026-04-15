# Houdini MCP Server - Setup Complete!

## ✅ What's Been Done

1. ✅ Created Houdini MCP Server package in `houdini-mcp-server/`
2. ✅ Installed MCP SDK in virtual environment
3. ✅ Configured OpenCode to connect to the server
4. ✅ Created HTTP bridge to work around Houdini's asyncio incompatibility

## 🚀 Next Steps - Complete the Setup

### Step 1: Start the Houdini RPC Service

Houdini should now be open. In Houdini's **Python Shell** (Windows > Python Shell), run:

```python
import sys
sys.path.insert(0, '/Users/kif/Library/Preferences/houdini/20.5/houdini-mcp-server/python')
import houdini_rpc_service
houdini_rpc_service.start_rpc_server_thread()
```

You should see:
```
✓ Houdini RPC Service started on http://localhost:9876
  MCP Server can now connect to this Houdini session
RPC server running in background. Keep this Houdini session open.
```

### Step 2: Test the Connection

In your terminal, run:

```bash
opencode mcp list
```

You should see `houdini` listed and marked as ✓ (connected) instead of ✗ (failed).

### Step 3: Test with OpenCode

Start OpenCode and try commands like:

- "What's the current frame in Houdini?"
- "Create a geometry node in Houdini"
- "Get scene information from Houdini"

## 📁 File Structure

```
houdini-mcp-server/
├── python/
│   ├── houdini_mcp_server_http.py    # MCP server (runs with standard Python)
│   ├── houdini_rpc_service.py        # RPC service (runs inside Houdini)
│   ├── houdini_mcp_server.py         # Original (doesn't work due to asyncio issue)
│   └── start_mcp_server.py          # Helper scripts
├── venv/                              # Python virtual environment
├── houdini_mcp_server.json           # Houdini package definition
├── KNOWN_ISSUES.md                   # Documentation of asyncio issue
└── README.md                          # Full documentation
```

## 🔧 How It Works

```
OpenCode ←→ MCP Server (HTTP Bridge) ←→ Houdini RPC Service ←→ Houdini
         stdio                  HTTP                    Python API
```

1. **OpenCode** communicates with **MCP Server** via stdio (standard MCP protocol)
2. **MCP Server** (running in standard Python) forwards requests to **Houdini RPC Service** via HTTP
3. **Houdini RPC Service** (running inside Houdini) executes commands using the `hou` module
4. Results flow back through the chain

## 📝 Making it Permanent

To auto-start the RPC service when Houdini launches, create:

`$HOME/houdini20.5/scripts/456.py`:

```python
import sys
sys.path.insert(0, '/Users/kif/Library/Preferences/houdini/20.5/houdini-mcp-server/python')
import houdini_rpc_service
houdini_rpc_service.start_rpc_server_thread()
print("Houdini MCP RPC Service started automatically")
```

This will run automatically when Houdini starts.

## ⚠️ Known Limitations

- Houdini must be running for the MCP server to work
- The RPC service must be started manually (or via startup script)  
- If Houdini closes, OpenCode will lose connection

## 🐛 Troubleshooting

### "Cannot connect to Houdini RPC service"

1. Make sure Houdini is running
2. Check that the RPC service is started (run the Python code in Step 1 again)
3. Verify the service is listening: `curl http://localhost:9876`

### "Connection closed" error

1. Check OpenCode config: `cat ~/.config/opencode/opencode.json`
2. Verify the venv Python exists: `ls -la houdini-mcp-server/venv/bin/python`
3. Check MCP server list: `opencode mcp list`

## 🎉 Success!

Once connected, you can:
- Execute arbitrary Python code in Houdini
- Query scene information  
- Create and manipulate nodes
- Evaluate expressions
- And more!

Enjoy using OpenCode with Houdini!
