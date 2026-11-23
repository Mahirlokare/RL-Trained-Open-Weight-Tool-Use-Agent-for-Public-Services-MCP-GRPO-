"""
Registry and base classes for Model Context Protocol (MCP) tool servers.
Implements the standard MCP JSON-RPC tool specification with backend security enforcement.
"""
from typing import Dict, Any, List, Callable
import json
from mcp_servers.security import SecurityPolicyEngine

class MCPToolServer:
    def __init__(self, name: str, description: str, security_engine: SecurityPolicyEngine = None):
        self.name = name
        self.description = description
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable] = {}
        self.scopes: Dict[str, str] = {}
        self.security = security_engine or SecurityPolicyEngine()

    def register_tool(
        self, 
        name: str, 
        description: str, 
        input_schema: Dict[str, Any], 
        handler: Callable,
        scope: str = "read:public"
    ):
        self.tools[name] = {
            "name": name,
            "description": description,
            "inputSchema": input_schema,
            "scope": scope
        }
        self.handlers[name] = handler
        self.scopes[name] = scope

    def list_tools(self) -> List[Dict[str, Any]]:
        return list(self.tools.values())

    def call_tool(self, name: str, arguments: Dict[str, Any], client_role: str = "citizen") -> Dict[str, Any]:
        if name not in self.handlers:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Tool '{name}' not found on server '{self.name}'"}]
            }

        # 1. Taint tracking & Prompt Injection check
        args_str = json.dumps(arguments)
        is_injection, alert_msg = self.security.scan_for_prompt_injection(args_str)
        if is_injection:
            return {
                "isError": True,
                "securityViolation": True,
                "content": [{"type": "text", "text": alert_msg}]
            }

        # 2. Permission check
        required_scope = self.scopes.get(name, "read:public")
        authorized, perm_msg = self.security.verify_permission(required_scope, client_role)
        if not authorized:
            return {
                "isError": True,
                "permissionDenied": True,
                "content": [{"type": "text", "text": perm_msg}]
            }

        # 3. Idempotency check for write actions
        if required_scope.startswith("write:"):
            idempotency_key = f"{name}:{hash(args_str)}"
            is_dup, cached_res = self.security.check_idempotency(idempotency_key)
            if is_dup:
                return {
                    "isError": False,
                    "idempotentReplay": True,
                    "content": [{"type": "text", "text": json.dumps(cached_res, indent=2, ensure_ascii=False)}]
                }

        try:
            result = self.handlers[name](**arguments)
            # Cache if write action
            if required_scope.startswith("write:"):
                self.security.register_idempotency(f"{name}:{hash(args_str)}", result)
                
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

    def execute_call(self, tool_name: str, arguments: Dict[str, Any], client_role: str = "citizen") -> Dict[str, Any]:
        for server in self.servers.values():
            if tool_name in server.tools:
                return server.call_tool(tool_name, arguments, client_role)
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"No server registered tool '{tool_name}'"}]
        }
