# Houdini CLI

Control a running Houdini instance from the terminal. No MCP, no Python venv, no JSON parsing. Just curl. Feed SKILL.md to your agent or mess with active Houdini session yourself from command line.

## How It Works

```
hctl.sh ←→ HTTP ←→ RPC Service ←→ Houdini
 (curl)   :9876   (inside Houdini)
```

## Install

### 1. Copy shelf tool to Houdini

```sh
cp houdini_rpc.shelf ~/Library/Preferences/houdini/21.0/toolbar/
```

### 2. Add `hctl.sh` to your PATH

```sh
ln -s /path/to/houdini-mcp-server/hctl.sh ~/.local/bin/hctl
```

## Usage

**Start Houdini** and click the **Start RPC** shelf button.

```sh
# Execute Python in Houdini
hctl exec "hou.hipFile.path()"
hctl exec "hou.node('/obj').createNode('box')"
hctl exec "[n.path() for n in hou.selectedNodes()]"

# Scene info
hctl scene

# Network as Mermaid diagram
hctl mermaid /obj/geo1

# Node errors
hctl errors /obj
```

### Raw curl

```sh
curl http://localhost:9876/scene
curl -X POST http://localhost:9876/exec -d "hou.hipFile.path()"
curl http://localhost:9876/mermaid?path=/obj/geo1
curl http://localhost:9876/errors?path=/obj
```

### Environment

- `HOUDINI_URL` — RPC endpoint (default: `http://localhost:9876`)

## Requirements

- Houdini 20.5+
- `curl`

## Files

- **`hctl.sh`** — CLI wrapper, plain curl
- **`houdini_rpc_service.py`** — runs inside Houdini, executes code with `hou` module access
- **`houdini_rpc.shelf`** — shelf tool, copy to `~/Library/Preferences/houdini/<version>/toolbar/`

## Resources

Inspired by https://github.com/OleksandrChekhovskyi/hax/blob/master/docs/philosophy.md

## License

MIT
