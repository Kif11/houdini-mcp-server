#!/usr/bin/env hython
"""
Test the get_context_as_mermaid function
"""
import hou

# Create test network
geo = hou.node('/obj').createNode('geo', 'test_mermaid')
box = geo.createNode('box')
scatter = geo.createNode('scatter')
scatter.setInput(0, box)
copy = geo.createNode('copytopoints')
copy.setInput(0, scatter)
copy.setInput(1, scatter)

# Create another branch
sphere = geo.createNode('sphere')
merge = geo.createNode('merge')
merge.setInput(0, copy)
merge.setInput(1, sphere)

# Standalone node with no connections
null = geo.createNode('null', 'standalone')

geo.layoutChildren()

# Test the function directly
def get_context_as_mermaid(context_path):
    """Get network context as Mermaid diagram"""
    try:
        context = hou.node(context_path)
        if not context:
            return {'error': f'Context node not found: {context_path}'}
        
        # Start mermaid diagram
        lines = ["graph TD"]
        
        # Get all children nodes
        children = context.children()
        
        if not children:
            return {'result': f"graph TD\n  empty[No nodes in {context_path}]"}
        
        # Track which nodes have been mentioned
        declared_nodes = set()
        
        # Build diagram
        for node in children:
            node_id = node.name()
            node_type = node.type().name()
            
            # Add connections
            inputs = node.inputs()
            if inputs:
                for input_node in inputs:
                    if input_node:  # Check if input is connected
                        input_id = input_node.name()
                        input_type = input_node.type().name()
                        lines.append(f"  {input_id}[{input_type}] --> {node_id}[{node_type}]")
                        declared_nodes.add(input_id)
                        declared_nodes.add(node_id)
        
        # Add standalone nodes (no connections)
        for node in children:
            if node.name() not in declared_nodes:
                lines.append(f"  {node.name()}[{node.type().name()}]")
        
        mermaid_diagram = "\n".join(lines)
        return {'result': mermaid_diagram}
        
    except Exception as e:
        import traceback
        return {
            'error': f"Failed to generate mermaid diagram: {type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        }

result = get_context_as_mermaid('/obj/test_mermaid')

print("=" * 60)
print("Mermaid Diagram:")
print("=" * 60)
if 'result' in result:
    print(result['result'])
elif 'error' in result:
    print(f"ERROR: {result['error']}")
print("=" * 60)

# Cleanup
geo.destroy()
