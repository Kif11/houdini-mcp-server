#!/usr/bin/env python
"""
Houdini MCP Server - Model Context Protocol server for Houdini integration
Runs within Houdini's Python environment and provides access to Houdini APIs
"""

import asyncio
import json
import sys
import traceback
from typing import Any, Dict, Optional

try:
    import hou
    HOU_AVAILABLE = True
except ImportError:
    HOU_AVAILABLE = False
    print("Warning: hou module not available. Server must run within Houdini.", file=sys.stderr)

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    import mcp.server.stdio
except ImportError:
    print("Error: MCP SDK not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)


class HoudiniMCPServer:
    """MCP Server for Houdini integration"""
    
    def __init__(self):
        self.server = Server("houdini-mcp-server")
        self.setup_handlers()
        
    def setup_handlers(self):
        """Setup MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools"""
            return [
                Tool(
                    name="execute_python",
                    description=(
                        "Execute arbitrary Python code within Houdini's context. "
                        "Has full access to the 'hou' module and all Houdini APIs. "
                        "Returns the result of the last expression or any print output."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Python code to execute in Houdini context"
                            },
                            "return_type": {
                                "type": "string",
                                "enum": ["auto", "string", "json"],
                                "description": "How to format the return value (default: auto)",
                                "default": "auto"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_scene_info",
                    description=(
                        "Get information about the current Houdini scene including "
                        "selected nodes, current context, frame range, and hip file path."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="evaluate_expression",
                    description=(
                        "Evaluate a Houdini expression (Hscript or Python) and return the result. "
                        "Useful for querying parameter values, variables, etc."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "expression": {
                                "type": "string",
                                "description": "The expression to evaluate"
                            },
                            "expression_language": {
                                "type": "string",
                                "enum": ["hscript", "python"],
                                "description": "Expression language (default: python)",
                                "default": "python"
                            }
                        },
                        "required": ["expression"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls"""
            
            if not HOU_AVAILABLE:
                return [TextContent(
                    type="text",
                    text="Error: hou module not available. Server must run within Houdini."
                )]
            
            try:
                if name == "execute_python":
                    result = await self._execute_python(arguments)
                elif name == "get_scene_info":
                    result = await self._get_scene_info(arguments)
                elif name == "evaluate_expression":
                    result = await self._evaluate_expression(arguments)
                else:
                    result = f"Error: Unknown tool '{name}'"
                
                return [TextContent(type="text", text=str(result))]
                
            except Exception as e:
                error_msg = f"Error executing {name}:\n{traceback.format_exc()}"
                return [TextContent(type="text", text=error_msg)]
    
    async def _execute_python(self, args: Dict[str, Any]) -> str:
        """Execute Python code in Houdini context"""
        code = args.get("code", "")
        return_type = args.get("return_type", "auto")
        
        if not code:
            return "Error: No code provided"
        
        # Create execution context with hou module
        exec_globals = {
            "hou": hou,
            "__name__": "__main__",
        }
        exec_locals = {}
        
        # Capture stdout
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        
        try:
            # Execute the code
            exec(code, exec_globals, exec_locals)
            
            # Get captured output
            output = captured_output.getvalue()
            
            # Try to get the result of the last expression
            result = exec_locals.get("_", None)
            
            # Format output
            if output and result is not None:
                final_output = f"{output}\nResult: {result}"
            elif output:
                final_output = output
            elif result is not None:
                final_output = str(result)
            else:
                final_output = "Code executed successfully (no output)"
            
            # Format based on return_type
            if return_type == "json":
                try:
                    return json.dumps({"output": output, "result": result})
                except:
                    return json.dumps({"output": output, "result": str(result)})
            else:
                return final_output
                
        finally:
            sys.stdout = old_stdout
    
    async def _get_scene_info(self, args: Dict[str, Any]) -> str:
        """Get current Houdini scene information"""
        info = {
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
        
        # Try to get current desktop
        try:
            desktop = hou.ui.curDesktop()
            if desktop:
                info["current_desktop"] = desktop.name()
        except:
            pass
        
        return json.dumps(info, indent=2)
    
    async def _evaluate_expression(self, args: Dict[str, Any]) -> str:
        """Evaluate a Houdini expression"""
        expression = args.get("expression", "")
        expr_lang = args.get("expression_language", "python")
        
        if not expression:
            return "Error: No expression provided"
        
        try:
            if expr_lang == "python":
                # Evaluate as Python expression
                result = eval(expression, {"hou": hou})
            else:
                # Evaluate as Hscript expression
                result = hou.hscriptExpression(expression)
            
            return str(result)
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"
    
    async def run(self):
        """Run the MCP server using stdio transport"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """Main entry point"""
    if not HOU_AVAILABLE:
        print("Error: This server must be run from within Houdini.", file=sys.stderr)
        print("The 'hou' module is not available in this Python environment.", file=sys.stderr)
        sys.exit(1)
    
    # Initialize Houdini in batch mode (no UI required)
    # This allows the server to work even when launched via hython
    try:
        if not hou.isUIAvailable():
            print("Running in headless mode (no UI)", file=sys.stderr)
    except:
        pass
    
    server = HoudiniMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
