"""
Houdini HTTP RPC Service
Runs INSIDE Houdini and provides an HTTP API for executing Python code
This runs in the Houdini GUI's Python environment
"""

import hou
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
from io import StringIO
import threading
import socket

class HoudiniRPCHandler(BaseHTTPRequestHandler):
    """Handle RPC requests from the MCP server"""
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            request = json.loads(post_data)
            method = request.get('method')
            params = request.get('params', {})
            
            if method == 'execute_python':
                result = self.execute_python(params.get('code', ''))
            elif method == 'get_scene_info':
                result = self.get_scene_info()
            elif method == 'get_context_as_mermaid':
                result = self.get_context_as_mermaid(params.get('context_path', '/obj'))
            elif method == 'get_node_errors':
                result = self.get_node_errors(params.get('context_path', '/obj'))
            else:
                result = {'error': f'Unknown method: {method}'}
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            error_response = {'error': str(e)}
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())
    
    def execute_python(self, code):
        """Execute Python code in Houdini context"""
        exec_globals = {"hou": hou}
        exec_locals = {}
        
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            exec(code, exec_globals, exec_locals)
            output = captured_output.getvalue()
            result = exec_locals.get("_", None)
            
            return {
                'output': output,
                'result': str(result) if result is not None else None
            }
        except Exception as e:
            import traceback
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            return {
                'error': error_msg,
                'output': captured_output.getvalue()
            }
        finally:
            sys.stdout = old_stdout
    
    def get_scene_info(self):
        """Get current scene information"""
        try:
            return {
                "hip_file": hou.hipFile.path(),
                "hip_name": hou.hipFile.basename(),
                "is_saved": not hou.hipFile.hasUnsavedChanges(),
                "frame_range": {
                    "start": hou.playbar.playbackRange()[0],
                    "end": hou.playbar.playbackRange()[1],
                    "current": hou.frame()
                },
                "fps": hou.fps(),
                "selected_nodes": [node.path() for node in hou.selectedNodes()],
                "pwd": hou.pwd().path() if hou.pwd() else "/",
                "houdini_version": hou.applicationVersionString(),
            }
        except Exception as e:
            import traceback
            return {
                'error': f"Failed to get scene info: {type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            }
    
    def get_context_as_mermaid(self, context_path):
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
    
    def get_node_errors(self, context_path='/obj'):
        """
        Get all node errors for a specified Houdini graph context.
        
        Args:
            context_path (str): Path to the context node (e.g. '/obj', '/obj/geo1')
            
        Returns:
            dict: Dictionary with structure:
                {
                    'context': str,
                    'total_errors': int,
                    'total_warnings': int,
                    'nodes_with_errors': list of dict with:
                        {
                            'path': str,
                            'name': str,
                            'type': str,
                            'errors': list of str,
                            'warnings': list of str
                        }
                }
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


class StoppableHTTPServer(HTTPServer):
    """HTTPServer with proper shutdown support"""
    
    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        self._stop_event = threading.Event()
    
    def serve_forever_stoppable(self):
        """Serve requests until stop() is called"""
        while not self._stop_event.is_set():
            self.handle_request()
    
    def stop(self):
        """Stop the server"""
        self._stop_event.set()
        # Make a dummy request to unblock handle_request()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.server_address)
            sock.close()
        except:
            pass


def start_rpc_server(port=9876, server_holder=None):
    """Start the HTTP RPC server"""
    server = StoppableHTTPServer(('localhost', port), HoudiniRPCHandler)
    
    # Store server reference if holder provided
    if server_holder is not None:
        server_holder['instance'] = server
    
    print(f"Houdini MCP RPC Service started on http://localhost:{port}")
    
    # Use stoppable serve_forever
    server.serve_forever_stoppable()
    
    # Clean up when stopped
    server.server_close()


def start_rpc_server_thread(port=9876):
    """Start the RPC server in a background thread"""
    # Create a holder dict to store the server instance
    server_holder = {}
    
    thread = threading.Thread(
        target=start_rpc_server, 
        args=(port, server_holder), 
        daemon=True
    )
    thread.start()
    
    # Wait a bit for server to start
    import time
    time.sleep(0.1)
    
    # Store both thread and server holder
    return {
        'thread': thread,
        'server_holder': server_holder,
        'port': port
    }


def stop_rpc_server(server_info):
    """Stop the RPC server"""
    if not isinstance(server_info, dict):
        print("Invalid server info")
        return False
    
    server_holder = server_info.get('server_holder', {})
    server = server_holder.get('instance')
    
    if server:
        server.stop()
        
        # Wait for thread to finish
        thread = server_info.get('thread')
        if thread:
            thread.join(timeout=2.0)
        
        print("MCP RPC Service stopped")
        return True
    
    print("No active server found")
    return False


# When run as a script or shelf tool
if __name__ == "__main__":
    start_rpc_server_thread()
    print("RPC server running in background. Keep this Houdini session open.")
