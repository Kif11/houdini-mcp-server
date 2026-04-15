"""
Houdini MCP Server Shelf Installer
Install with one line in Houdini Python Shell:
import urllib.request,ssl;exec(urllib.request.urlopen('https://raw.githubusercontent.com/YOUR_GITHUB/houdini-mcp-server/main/install_mcp_shelf.py',context=ssl._create_unverified_context()).read().decode('utf-8'))
"""

import hou
import os

def install_mcp_shelf():
    """Install the MCP Server shelf into Houdini"""
    
    toolbar_dir = os.path.join(hou.homeHoudiniDirectory(), "toolbar")
    
    # Create the toolbar directory if it doesn't exist
    if not os.path.exists(toolbar_dir):
        os.makedirs(toolbar_dir)
    
    shelf_file = os.path.join(toolbar_dir, "mcp_server.shelf")
    
    # Determine the MCP server path (use hou.homeHoudiniDirectory() for portability)
    mcp_server_path = os.path.join(hou.homeHoudiniDirectory(), 'houdini-mcp-server', 'python')
    
    try:
        print("Installing MCP Server shelf...")
        
        # Create the shelf XML content
        shelf_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<shelfDocument>
  <toolshelf name="mcp_server" label="MCP Server">
    <memberTool name="start_mcp_server"/>
    <memberTool name="stop_mcp_server"/>
  </toolshelf>
  
  <tool name="start_mcp_server" label="Start MCP" icon="PLASMA_App">
    <script scriptType="python"><![CDATA[import sys
sys.path.insert(0, '{mcp_server_path}')

import houdini_rpc_service

# Check if already running
if hasattr(hou.session, 'mcp_rpc_server'):
    server_info = hou.session.mcp_rpc_server
    if isinstance(server_info, dict):
        thread = server_info.get('thread')
        if thread and thread.is_alive():
            print("MCP RPC Service already running on port 9876")
        else:
            hou.session.mcp_rpc_server = houdini_rpc_service.start_rpc_server_thread(port=9876)
    else:
        hou.session.mcp_rpc_server = houdini_rpc_service.start_rpc_server_thread(port=9876)
else:
    hou.session.mcp_rpc_server = houdini_rpc_service.start_rpc_server_thread(port=9876)
]]></script>
  </tool>
  
  <tool name="stop_mcp_server" label="Stop MCP" icon="PLASMA_Stop">
    <script scriptType="python"><![CDATA[import sys
sys.path.insert(0, '{mcp_server_path}')

import houdini_rpc_service

if hasattr(hou.session, 'mcp_rpc_server'):
    server_info = hou.session.mcp_rpc_server
    if houdini_rpc_service.stop_rpc_server(server_info):
        delattr(hou.session, 'mcp_rpc_server')
else:
    print("MCP RPC Service not running")
]]></script>
  </tool>
</shelfDocument>'''
        
        # Write the shelf file
        with open(shelf_file, 'w') as f:
            f.write(shelf_content)
        
        print(f"Successfully saved to {shelf_file}")
        
        # Reload shelves
        hou.shelves.reloadShelfFiles()
        print("Shelf files reloaded")
        
        # Add MCP Server shelf to active shelves
        shelf_set = hou.shelves.shelfSets().get("shelf_set_1")
        if shelf_set:
            # Get the MCP Server shelf
            mcp_shelf = hou.shelves.shelves().get("mcp_server")
            if mcp_shelf:
                # Get current shelves
                current_shelves = list(shelf_set.shelves())
                # Add MCP shelf if not already present
                if mcp_shelf not in current_shelves:
                    current_shelves.append(mcp_shelf)
                    shelf_set.setShelves(current_shelves)
                    print("MCP Server shelf added to active shelves")
                else:
                    print("MCP Server shelf already in active shelves")
            else:
                print("Warning: MCP Server shelf not found after reload")
        else:
            print("Warning: Could not find shelf_set_1")
        
        print("\n" + "=" * 70)
        print("✓ MCP Server shelf installed successfully!")
        print("  Shelf is now visible in your shelf area")
        print("=" * 70 + "\n")
        
        return shelf_file
        
    except Exception as e:
        print(f"Error installing shelf: {e}")
        import traceback
        traceback.print_exc()
        return None

# Run the installer
install_mcp_shelf()
