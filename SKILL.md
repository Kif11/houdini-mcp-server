---
name: houdini
description: |
  Control Houdini 3D software from the terminal. Use when:
  - Creating, modifying, or querying Houdini nodes and networks
  - Executing Houdini Python (hou module) code
  - Querying scene information (selected nodes, frame range, hip file)
  Triggers: "houdini", "hou module", "create node", "scene info", "hip file", "geometry", "sop", "vex"
---

# Houdini CLI

Control a running Houdini instance via HTTP.

## Prerequisites

1. Houdini must be running with the RPC service started (shelf button "Start RPC")
2. `hctl` must be on PATH, or use raw curl

## Commands

### `hctl exec "<python-code>"`

Execute Python in Houdini. Expressions return their value, statements print to stdout.

```sh
hctl exec "hou.hipFile.path()"
hctl exec "hou.node('/obj').createNode('box')"
hctl exec "[n.path() for n in hou.selectedNodes()]"
```

Multi-line:

```sh
hctl exec "
geo = hou.node('/obj').createNode('geo', 'procedural')
box = geo.createNode('box', 'source')
scatter = geo.createNode('scatter', 'points')
scatter.setInput(0, box)
scatter.parm('npts').set(1000)
geo.layoutChildren()
"
```

### `hctl scene`

Scene info as plain text.

### `hctl dot [path]`

Network as Graphviz DOT graph. Default: `/obj`.

```sh
hctl dot /obj/geo1
hctl dot /obj/geo1 | dot -Tpng -o graph.png
```

### `hctl errors [path]`

Node errors. Default: `/obj`.

## Raw curl

```sh
curl http://localhost:9876/scene
curl -X POST http://localhost:9876/exec -d "hou.hipFile.path()"
curl http://localhost:9876/dot?path=/obj/geo1
curl http://localhost:9876/errors?path=/obj
```

## Tips

- Quote multi-line code; use semicolons or newlines inside
- Check node existence: `if hou.node('/path'): ...`
- Set display flags: `node.setDisplayFlag(True)`
- Layout networks: `parent.layoutChildren()`
