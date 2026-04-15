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
        finally:
            sys.stdout = old_stdout
    
    def get_scene_info(self):
        """Get current scene information"""
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
