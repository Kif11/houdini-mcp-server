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


def start_rpc_server(port=9876):
    """Start the HTTP RPC server"""
    server = HTTPServer(('localhost', port), HoudiniRPCHandler)
    print(f"✓ Houdini RPC Service started on http://localhost:{port}")
    print("  MCP Server can now connect to this Houdini session")
    server.serve_forever()


def start_rpc_server_thread(port=9876):
    """Start the RPC server in a background thread"""
    thread = threading.Thread(target=start_rpc_server, args=(port,), daemon=True)
    thread.start()
    return thread


# When run as a script or shelf tool
if __name__ == "__main__":
    start_rpc_server_thread()
    print("RPC server running in background. Keep this Houdini session open.")
