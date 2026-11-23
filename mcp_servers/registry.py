"""
Registry and base classes for Model Context Protocol (MCP) tool servers.
Implements the standard MCP JSON-RPC tool specification with backend security enforcement,
argument validation, cryptographic idempotency, and execution timeouts.
"""
from typing import Dict, Any, List, Callable, Optional, Tuple
import json
import hashlib
import time
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from mcp_servers.security import SecurityPolicyEngine

logger = logging.getLogger("civic_ai.mcp")

class MCPToolServer:
    def __init__(
        self, 
        name: str, 
        description: str, 
        security_engine: Optional[SecurityPolicyEngine] = None,
        default_timeout: float = 10.0
    ):
        self.name = name
        self.description = description
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable] = {}
        self.scopes: Dict[str, str] = {}
        self.security = security_engine or SecurityPolicyEngine()
        self.default_timeout = default_timeout
        self.executor = ThreadPoolExecutor(max_workers=4)

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
        logger.info(f"Registered MCP tool '{name}' on server '{self.name}' with scope '{scope}'")

    def list_tools(self) -> List[Dict[str, Any]]:
        return list(self.tools.values())

    def validate_arguments(self, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validates arguments against the tool's registered inputSchema."""
        schema = self.tools.get(tool_name, {}).get("inputSchema", {})
        required_fields = schema.get("required", [])
        
        # Check required properties
        for req in required_fields:
            if req not in arguments or arguments[req] is None:
                return False, f"Schema Validation Error: Missing required argument '{req}' for tool '{tool_name}'"

        # Check basic property types if specified
        properties = schema.get("properties", {})
        for param, val in arguments.items():
            if param in properties and val is not None:
                expected_type = properties[param].get("type")
                if expected_type == "string" and not isinstance(val, str):
                    return False, f"Schema Validation Error: Parameter '{param}' expected string, got {type(val).__name__}"
                elif expected_type == "number" and not isinstance(val, (int, float)):
                    return False, f"Schema Validation Error: Parameter '{param}' expected number, got {type(val).__name__}"
                elif expected_type == "integer" and not isinstance(val, int):
                    return False, f"Schema Validation Error: Parameter '{param}' expected integer, got {type(val).__name__}"
                elif expected_type == "boolean" and not isinstance(val, bool):
                    return False, f"Schema Validation Error: Parameter '{param}' expected boolean, got {type(val).__name__}"
                elif expected_type == "array" and not isinstance(val, list):
                    return False, f"Schema Validation Error: Parameter '{param}' expected array list, got {type(val).__name__}"

        return True, None

    def call_tool(
        self, 
        name: str, 
        arguments: Dict[str, Any], 
        client_role: str = "citizen",
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        t0 = time.time()
        timeout_val = timeout or self.default_timeout

        if name not in self.handlers:
            logger.warning(f"Tool '{name}' not found on server '{self.name}'")
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Tool '{name}' not found on server '{self.name}'"}]
            }

        # 1. Taint tracking & Prompt Injection check
        args_str = json.dumps(arguments, sort_keys=True, ensure_ascii=False)
        is_injection, alert_msg = self.security.scan_for_prompt_injection(args_str)
        if is_injection:
            logger.warning(f"Security Alert: Blocked tainted prompt injection on tool '{name}': {alert_msg}")
            return {
                "isError": True,
                "securityViolation": True,
                "content": [{"type": "text", "text": alert_msg}]
            }

        # 2. Strict Input Schema Validation
        is_valid, validation_err = self.validate_arguments(name, arguments)
        if not is_valid:
            logger.warning(f"Argument validation failed for '{name}': {validation_err}")
            return {
                "isError": True,
                "validationError": True,
                "content": [{"type": "text", "text": validation_err}]
            }

        # 3. Least-privilege Scope Permission check
        required_scope = self.scopes.get(name, "read:public")
        confirmation_token = arguments.get("confirmation_token")
        authorized, perm_msg = self.security.verify_permission(required_scope, client_role, confirmation_token)
        if not authorized and required_scope.startswith("admin:"):
            logger.warning(f"Access Denied: Role '{client_role}' lacked scope '{required_scope}' for '{name}'")
            return {
                "isError": True,
                "permissionDenied": True,
                "content": [{"type": "text", "text": perm_msg}]
            }

        # 4. Deterministic SHA-256 Idempotency check for write actions
        sha256_hash = hashlib.sha256(f"{name}:{args_str}".encode("utf-8")).hexdigest()
        if required_scope.startswith("write:"):
            idempotency_key = f"{name}:{sha256_hash}"
            is_dup, cached_res = self.security.check_idempotency(idempotency_key)
            if is_dup:
                logger.info(f"Idempotent replay served for '{name}' (key: {idempotency_key[:16]}...)")
                return {
                    "isError": False,
                    "idempotentReplay": True,
                    "content": [{"type": "text", "text": json.dumps(cached_res, indent=2, ensure_ascii=False)}]
                }

        # 5. Execution with Timeout Protection
        try:
            future = self.executor.submit(self.handlers[name], **arguments)
            result = future.result(timeout=timeout_val)
            latency_ms = round((time.time() - t0) * 1000, 2)

            # Register idempotency on successful write
            if required_scope.startswith("write:"):
                self.security.register_idempotency(f"{name}:{sha256_hash}", result)
                
            logger.info(f"Tool '{name}' executed successfully ({latency_ms} ms)")
            return {
                "isError": False,
                "latency_ms": latency_ms,
                "content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]
            }

        except FutureTimeoutError:
            logger.error(f"Execution of tool '{name}' timed out after {timeout_val} seconds")
            return {
                "isError": True,
                "timeout": True,
                "content": [{"type": "text", "text": f"Timeout Error: Execution of tool '{name}' exceeded {timeout_val}s limit"}]
            }
        except Exception as e:
            logger.error(f"Execution error in '{name}': {str(e)}", exc_info=True)
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Execution error in {name}: {str(e)}"}]
            }

class MCPHub:
    """Aggregates multiple MCP servers and routes tool calls according to the MCP standard."""
    def __init__(self):
        self.servers: Dict[str, MCPToolServer] = {}

    def add_server(self, server: MCPToolServer):
        self.servers[server.name] = server

    def get_all_tools(self) -> List[Dict[str, Any]]:
        all_tools = []
        for server in self.servers.values():
            all_tools.extend(server.list_tools())
        return all_tools

    def execute_call(
        self, 
        tool_name: str, 
        arguments: Dict[str, Any], 
        client_role: str = "citizen",
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        for server in self.servers.values():
            if tool_name in server.tools:
                return server.call_tool(tool_name, arguments, client_role, timeout=timeout)
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"No server registered tool '{tool_name}'"}]
        }
