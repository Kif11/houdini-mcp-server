#!/usr/bin/env python3
"""
Houdini MCP Server
Model Context Protocol server for Houdini integration.

Uses HTTP bridge architecture to work around Houdini's asyncio incompatibility:
- Runs with standard Python (handles MCP protocol)
- Communicates with Houdini via HTTP RPC service
"""

import asyncio
import json
import sys
import httpx
from typing import Any, Dict

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.server.stdio
except ImportError:
    print("Error: MCP SDK not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)


class HoudiniMCPServerHTTP:
    """MCP Server that connects to Houdini via HTTP"""
    
    def __init__(self, houdini_url="http://localhost:9876"):
        self.server = Server("houdini-mcp-server")
        self.houdini_url = houdini_url
        self.http_client = None
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
                    name="get_context_as_mermaid",
                    description=(
                        "Get a Houdini network context as a Mermaid diagram. "
                        "Shows node graph structure with connections in Mermaid graph format."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "context_path": {
                                "type": "string",
                                "description": "Path to the context node (e.g. '/obj', '/obj/geo1'). Defaults to '/obj'",
                                "default": "/obj"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_node_errors",
                    description=(
                        "Get all node errors and warnings for a specified Houdini graph context. "
                        "Recursively checks all nodes in the context and returns detailed error information."
                    ),
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "context_path": {
                                "type": "string",
                                "description": "Path to the context node (e.g. '/obj', '/obj/geo1'). Defaults to '/obj'",
                                "default": "/obj"
                            }
                        }
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls"""
            
            try:
                # Call the Houdini RPC service
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        self.houdini_url,
                        json={"method": name, "params": arguments}
                    )
                    response.raise_for_status()
                    result = response.json()
                
                # Format the response
                if 'error' in result:
                    return [TextContent(type="text", text=f"Error: {result['error']}")]
                elif 'output' in result and 'result' in result:
                    # execute_python response
                    text = result['output']
                    if result['result']:
                        text += f"\nResult: {result['result']}"
                    return [TextContent(type="text", text=text or "Code executed successfully")]
                elif 'result' in result:
                    return [TextContent(type="text", text=str(result['result']))]
                else:
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
            except httpx.ConnectError:
                return [TextContent(
                    type="text",
                    text=f"Error: Cannot connect to Houdini RPC service at {self.houdini_url}\n"
                         f"Make sure Houdini is running and the RPC service is started.\n"
                         f"Run this in Houdini's Python shell: execfile('{sys.path[0]}/houdini_rpc_service.py')"
                )]
            except Exception as e:
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
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
    houdini_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:9876"
    
    print(f"Starting Houdini MCP Server (HTTP Bridge)", file=sys.stderr)
    print(f"Connecting to Houdini RPC at: {houdini_url}", file=sys.stderr)
    
    server = HoudiniMCPServerHTTP(houdini_url)
    asyncio.run(server.run())


if __name__ == "__main__":
    main()
