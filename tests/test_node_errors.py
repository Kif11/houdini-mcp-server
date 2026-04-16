#!/usr/bin/env hython
"""
Test the get_node_errors function
"""
import hou

# Create test network with some errors
geo = hou.node('/obj').createNode('geo', 'test_errors')

# Node 1: Box (should be fine)
box = geo.createNode('box')

# Node 2: Scatter with no input (will have error)
scatter = geo.createNode('scatter')
# Don't connect input - this will cause an error

# Node 3: Copy with missing second input (may cause warning/error)
copy = geo.createNode('copytopoints')
copy.setInput(0, box)
# Missing second input

# Node 4: File node with invalid path (will have error)
file_node = geo.createNode('file')
file_node.parm('file').set('/nonexistent/path/to/file.bgeo')

geo.layoutChildren()

# Test the function
def get_node_errors(context_path='/obj'):
    """
    Get all node errors for a specified Houdini graph context.
    """
    context = hou.node(context_path)
    if not context:
        return {
            'error': f'Context node not found: {context_path}',
            'context': context_path,
            'total_errors': 0,
            'total_warnings': 0,
            'nodes_with_errors': []
        }
    
    nodes_with_issues = []
    total_errors = 0
    total_warnings = 0
    
    # Recursively check all nodes in the context
    def check_node(node):
        nonlocal total_errors, total_warnings
        
        errors = []
        warnings = []
        
        # Get node errors
        try:
            if node.errors():
                errors = [node.errors()]
                total_errors += 1
        except:
            pass
            
        # Get node warnings
        try:
            if node.warnings():
                warnings = [node.warnings()]
                total_warnings += 1
        except:
            pass
        
        # If node has errors or warnings, add to list
        if errors or warnings:
            nodes_with_issues.append({
                'path': node.path(),
                'name': node.name(),
                'type': node.type().name(),
                'errors': errors,
                'warnings': warnings
            })
        
        # Recursively check children
        try:
            for child in node.children():
                check_node(child)
        except:
            pass
    
    # Start checking from context
    check_node(context)
    
    return {
        'result': {
            'context': context_path,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'nodes_with_errors': nodes_with_issues
        }
    }

result = get_node_errors('/obj/test_errors')

print("=" * 60)
print("Node Errors Report:")
print("=" * 60)
if 'result' in result:
    r = result['result']
    print(f"Context: {r['context']}")
    print(f"Total Errors: {r['total_errors']}")
    print(f"Total Warnings: {r['total_warnings']}")
    print()
    
    if r['nodes_with_errors']:
        print("Nodes with issues:")
        for node_info in r['nodes_with_errors']:
            print(f"\n  {node_info['path']} [{node_info['type']}]")
            if node_info['errors']:
                for err in node_info['errors']:
                    print(f"    ERROR: {err}")
            if node_info['warnings']:
                for warn in node_info['warnings']:
                    print(f"    WARNING: {warn}")
    else:
        print("No errors or warnings found!")
        
elif 'error' in result:
    print(f"ERROR: {result['error']}")
    
print("=" * 60)

# Cleanup
geo.destroy()
