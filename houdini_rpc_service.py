"""
Houdini HTTP RPC Service
Runs INSIDE Houdini and provides an HTTP API for executing Python code.
This runs in the Houdini GUI's Python environment.

Endpoints:
  POST /exec         - body is raw Python code, returns stdout
  GET  /scene        - scene info as plain text
  GET  /mermaid?path - network as Mermaid diagram
  GET  /errors?path  - node errors as JSON
  GET  /             - this help text
"""

import hou
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sys
from io import StringIO
import threading
import socket


class HoudiniHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')
        qs = parse_qs(parsed.query)

        if path in ('', '/'):
            self._text(200, __doc__.strip())
        elif path == '/scene':
            self._scene()
        elif path == '/mermaid':
            ctx = qs.get('path', ['/obj'])[0]
            self._mermaid(ctx)
        elif path == '/errors':
            ctx = qs.get('path', ['/obj'])[0]
            self._errors(ctx)
        else:
            self._text(404, f'Not found: {path}')

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip('/')

        if path == '/exec':
            length = int(self.headers.get('Content-Length', 0))
            code = self.rfile.read(length).decode('utf-8')
            self._exec(code)
        else:
            self._text(404, f'Not found: {path}')

    # --- handlers ---

    def _exec(self, code):
        old_stdout = sys.stdout
        sys.stdout = captured = StringIO()
        try:
            env = {"hou": hou}
            # try eval first (single expressions get a result)
            try:
                result = eval(code, env)
                out = captured.getvalue()
                if result is not None:
                    out += str(result)
                self._text(200, out)
            except SyntaxError:
                # multi-line or statements — exec only
                exec(code, env)
                self._text(200, captured.getvalue())
        except Exception as e:
            import traceback
            msg = f'{type(e).__name__}: {e}\n{traceback.format_exc()}'
            self._text(500, msg)
        finally:
            sys.stdout = old_stdout

    def _scene(self):
        try:
            info = hou.hipFile.path()
            saved = 'saved' if not hou.hipFile.hasUnsavedChanges() else 'unsaved'
            rng = hou.playbar.playbackRange()
            selected = ', '.join(n.path() for n in hou.selectedNodes()) or '(none)'
            pwd = hou.pwd().path() if hou.pwd() else '/'

            lines = [
                f'hip:       {info} ({saved})',
                f'version:   {hou.applicationVersionString()}',
                f'frame:     {hou.frame()} / {rng[0]}-{rng[1]}',
                f'fps:       {hou.fps()}',
                f'context:   {pwd}',
                f'selected:  {selected}',
            ]
            self._text(200, '\n'.join(lines))
        except Exception as e:
            self._text(500, str(e))

    def _mermaid(self, context_path):
        try:
            context = hou.node(context_path)
            if not context:
                self._text(404, f'Node not found: {context_path}')
                return

            children = context.children()
            if not children:
                self._text(200, f'graph TD\n  empty[No nodes in {context_path}]')
                return

            lines = ['graph TD']
            declared = set()

            for node in children:
                nid = node.name()
                ntype = node.type().name()
                for inp in node.inputs():
                    if inp:
                        lines.append(f'  {inp.name()}[{inp.type().name()}] --> {nid}[{ntype}]')
                        declared.add(inp.name())
                        declared.add(nid)

            for node in children:
                if node.name() not in declared:
                    lines.append(f'  {node.name()}[{node.type().name()}]')

            self._text(200, '\n'.join(lines))
        except Exception as e:
            self._text(500, str(e))

    def _errors(self, context_path):
        try:
            context = hou.node(context_path)
            if not context:
                self._json(404, {'error': f'Node not found: {context_path}'})
                return

            issues = []
            total_err = 0
            total_warn = 0

            def walk(node):
                nonlocal total_err, total_warn
                try:
                    errs = node.errors()
                    if errs:
                        total_err += 1
                        issues.append({'path': node.path(), 'type': node.type().name(),
                                       'errors': list(errs), 'warnings': []})
                except Exception:
                    pass
                try:
                    warns = node.warnings()
                    if warns:
                        total_warn += 1
                        # merge if already added
                        existing = next((i for i in issues if i['path'] == node.path()), None)
                        if existing:
                            existing['warnings'] = list(warns)
                        else:
                            issues.append({'path': node.path(), 'type': node.type().name(),
                                           'errors': [], 'warnings': list(warns)})
                except Exception:
                    pass
                try:
                    for child in node.children():
                        walk(child)
                except Exception:
                    pass

            walk(context)
            self._json(200, {
                'context': context_path,
                'total_errors': total_err,
                'total_warnings': total_warn,
                'nodes': issues,
            })
        except Exception as e:
            self._json(500, {'error': str(e)})

    # --- helpers ---

    def _text(self, code, body):
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(body.encode('utf-8'))

    def _json(self, code, obj):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode('utf-8'))


class StoppableHTTPServer(HTTPServer):
    def __init__(self, *args, **kwargs):
        HTTPServer.__init__(self, *args, **kwargs)
        self._stop_event = threading.Event()

    def serve_forever_stoppable(self):
        while not self._stop_event.is_set():
            self.handle_request()

    def stop(self):
        self._stop_event.set()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(self.server_address)
            sock.close()
        except Exception:
            pass


def start_rpc_server(port=9876, server_holder=None):
    server = StoppableHTTPServer(('localhost', port), HoudiniHandler)
    if server_holder is not None:
        server_holder['instance'] = server
    print(f'Houdini RPC started on http://localhost:{port}')
    server.serve_forever_stoppable()
    server.server_close()


def start_rpc_server_thread(port=9876):
    server_holder = {}
    thread = threading.Thread(target=start_rpc_server, args=(port, server_holder), daemon=True)
    thread.start()
    import time
    time.sleep(0.1)
    return {'thread': thread, 'server_holder': server_holder, 'port': port}


def stop_rpc_server(server_info):
    if not isinstance(server_info, dict):
        return False
    server = server_info.get('server_holder', {}).get('instance')
    if server:
        server.stop()
        thread = server_info.get('thread')
        if thread:
            thread.join(timeout=2.0)
        print('Houdini RPC stopped')
        return True
    return False


if __name__ == '__main__':
    start_rpc_server_thread()
    print('RPC server running. Keep this Houdini session open.')
