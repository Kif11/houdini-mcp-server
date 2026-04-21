---
name: houdini-mcp
description: |
  Control Houdini 3D software through MCP. Use when:
  - Creating, modifying, or querying Houdini nodes and networks
  - Executing Houdini Python (hou module) code
  - Querying scene information (selected nodes, frame range, hip file)
  - Manipulating geometry, parameters, or scene hierarchy
  - Creating procedural setups, VEX/Python SOPs, or node networks
  - Serializing/deserializing node networks as JSON (recipes)
  Triggers: "houdini", "hou module", "create node", "scene info", "hip file", "geometry node", "sop", "vex", "houdini python", "recipe", "serialize network"
---

# Houdini MCP Server

Control SideFX Houdini through the Model Context Protocol. Execute Python code with full `hou` module access.

## Prerequisites

1. **Houdini must be running** with the MCP RPC service started
2. **Start the service** using the shelf button "Start MCP" in Houdini
3. **Verify MCP is enabled** in your client (OpenCode: check with `/mcps`)

## Available Tools

### `houdini_execute_python`

Execute arbitrary Python code in Houdini's context with full `hou` module access.

**Parameters:**
- `code` (string, required): Python code to execute

**Returns:** Result of the last expression or print output

**Example usage:**

```python
# Create a geometry node
geo = hou.node('/obj').createNode('geo', 'my_geo')
geo.moveToGoodPosition()
```

```python
# Get selected nodes
selected = hou.selectedNodes()
[node.path() for node in selected]
```

```python
# Set parameter values
node = hou.node('/obj/geo1/box1')
node.parm('sizex').set(5.0)
```

### `houdini_get_scene_info`

Get current Houdini scene state and metadata.

**Parameters:** None

**Returns:** JSON object with:
- `hip_file`: Path to current .hip file (or "untitled.hip")
- `frame_range`: `[start, end]` tuple
- `current_frame`: Current timeline frame
- `fps`: Frames per second
- `selected_nodes`: List of selected node paths
- `selected_count`: Number of selected nodes

**Example usage:**

```
Get the current scene information
```

### `houdini_serialize_network`

Serialize nodes and networks to JSON format using Houdini's `hou.data` recipe system. The JSON output can be saved and later loaded back.

**Parameters:**
- `node_paths` (array of strings, required): List of node paths to serialize
- `include_children` (boolean, optional): Recursively include child networks (default: true)
- `include_inputs` (boolean, optional): Save input connections (default: true)  
- `include_parms` (boolean, optional): Save parameter values (default: true)

**Returns:** JSON string containing serialized network data

**Example usage:**

```python
# Serialize a single node
serialize_network(node_paths=["/obj/geo1/box1"])
```

```python
# Serialize multiple nodes with full hierarchy
serialize_network(
    node_paths=["/obj/geo1/box1", "/obj/geo1/scatter1"],
    include_children=True,
    include_inputs=True
)
```

```
Save the current selected nodes as a JSON recipe
```

### `houdini_deserialize_network`

Load and recreate nodes from JSON data created by `serialize_network`. Creates nodes with their parameters, connections, and hierarchy restored.

**Parameters:**
- `json_data` (string, required): JSON string containing serialized network data
- `parent_path` (string, required): Path to parent node where network should be created
- `position` (array of 2 numbers, optional): [x, y] position for created nodes

**Returns:** Object with `created_nodes` (list of paths) and `count`

**Example usage:**

```python
# Load nodes from JSON into /obj
deserialize_network(
    json_data='{"nodes": [...]}',
    parent_path="/obj/geo1"
)
```

```python
# Load and position nodes
deserialize_network(
    json_data=saved_json,
    parent_path="/obj/geo1",
    position=[0, 0]
)
```

```
Load the saved recipe JSON and create it in /obj/geo1
```

## Common Patterns

### Creating Node Networks

When creating complex node setups, build them step by step:

```python
# Create container
geo = hou.node('/obj').createNode('geo', 'procedural_geo')

# Create source geometry
box = geo.createNode('box', 'source')

# Create scatter
scatter = geo.createNode('scatter', 'points')
scatter.setInput(0, box)
scatter.parm('npts').set(1000)

# Create copy to points
copy = geo.createNode('copytopoints', 'instances')
sphere = geo.createNode('sphere', 'instance_geo')
copy.setInput(0, sphere)
copy.setInput(1, scatter)

# Set display flag
copy.setDisplayFlag(True)
copy.setRenderFlag(True)

# Layout nodes
geo.layoutChildren()
```

### Querying Node Parameters

```python
node = hou.node('/obj/geo1/box1')

# Get all parameters
parms = node.parms()
for p in parms:
    print(f"{p.name()}: {p.eval()}")

# Get specific parameter
size = node.parm('size').eval()
```

### Creating VEX/Python Expressions

```python
# Create attribute wrangle (VEX)
wrangle = geo.createNode('attribwrangle', 'custom_vex')
wrangle.parm('snippet').set('''
@P.y += sin(@P.x * 2.0 + @Frame * 0.1);
@Cd = chramp("color", @P.y);
''')

# Create Python SOP
python_sop = geo.createNode('python', 'custom_python')
python_sop.parm('python').set('''
node = hou.pwd()
geo = node.geometry()

for point in geo.points():
    pos = point.position()
    point.setPosition((pos[0], pos[1] * 1.5, pos[2]))
''')
```

### Working with Selection

```python
# Get selected nodes
selected = hou.selectedNodes()

# Clear selection
hou.clearAllSelected()

# Select specific nodes
node = hou.node('/obj/geo1')
node.setSelected(True)

# Select multiple
nodes = [hou.node('/obj/geo1'), hou.node('/obj/geo2')]
for n in nodes:
    n.setSelected(True, clear_all_selected=False)
```

### Error Handling

Always wrap risky operations in try/except:

```python
try:
    node = hou.node('/obj/geo1/box1')
    if node:
        node.parm('size').set(10)
    else:
        print("Node not found")
except hou.Error as e:
    print(f"Houdini error: {e}")
```

## Best Practices

1. **Check node existence** before operating on it
2. **Use relative paths** when possible (e.g., `node.parent()`)
3. **Layout nodes** after creating networks: `parent.layoutChildren()`
4. **Set display/render flags** explicitly on final nodes
5. **Use meaningful names** for nodes to make networks readable
6. **Test small changes** before building complex setups

## Common Tasks

### Create Basic Geometry

```
Create a box and a sphere in Houdini, position them 5 units apart
```

### Procedural Setup

```
Create a scatter SOP with 1000 points on a grid, then copy spheres to each point
```

### Randomization

```
For each scattered point, randomize its size, rotation on Y axis, and color
```

### Scene Queries

```
What nodes are currently selected in Houdini?
```

```
What is the current frame range and FPS?
```

### Parameter Animation

```
Animate the box size from 1 to 5 over frames 1-100 using keyframes
```

## Troubleshooting

**"Connection refused" errors:**
- Ensure Houdini is running
- Click "Start MCP" shelf button in Houdini
- Check if port 9876 is available

**"Module 'hou' not found":**
- This error shouldn't occur - the code runs inside Houdini
- If it does, restart the MCP service in Houdini

**Changes not visible:**
- Check if display flag is set on the correct node
- Verify you're editing the right network path
- Use `node.setDisplayFlag(True)` to make nodes visible

## Reference

- Houdini Python: https://www.sidefx.com/docs/houdini/hom/index.html
- VEX: https://www.sidefx.com/docs/houdini/vex/index.html
- GitHub: https://github.com/Kif11/houdini-mcp-server
