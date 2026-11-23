"""
Registry and base classes for Model Context Protocol (MCP) tool servers.
Implements the standard MCP JSON-RPC tool specification:
- tools/list: Returns tool definitions with JSON Schema parameters.
- tools/call: Dispatches execution with argument validation and structured returns.
"""
from typing import Dict, Any, List, Callable
import json

class MCPToolServer:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable] = {}

    def register_tool(self, name: str, description: str, input_schema: Dict[str, Any], handler: Callable):
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema
        }
        self.handlers[name] = handler

    def list_tools(self) -> List[Dict[str, Any]]:
        return list(self.tools.values())

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name not in self.handlers:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Tool '{name}' not found on server '{self.name}'"}]
            }
        try:
            result = self.handlers[name](**arguments)
            return {
                "isError": False,
                "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
            }
        except Exception as e:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Execution error in {name}: {str(e)}"}]
            }

class MCPHub:
    """Aggregates multiple MCP servers and routes tool calls according to MCP standard."""
    def __init__(self):
        self.servers: Dict[str, MCPToolServer] = {}

    def add_server(self, server: MCPToolServer):
        self.servers[server.name] = server

    def get_all_tools(self) -> List[Dict[str, Any]]:
        all_tools = []
        for server in self.servers.values():
            all_tools.extend(server.list_tools())
        return all_tools

    def execute_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        for server in self.servers.values():
            if tool_name in server.tools:
                return server.call_tool(tool_name, arguments)
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"No server registered tool '{tool_name}'"}]
        }
