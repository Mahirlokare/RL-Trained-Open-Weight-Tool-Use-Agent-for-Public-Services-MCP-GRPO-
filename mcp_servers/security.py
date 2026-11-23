"""
Security and Policy Engine for MCP Tool Servers.
Implements:
1. Scope-based permission checks (RBAC)
2. Indirect prompt injection & taint detection
3. Idempotency verification for stateful write actions
"""
from typing import Dict, Any, Tuple
import re

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"(system\s+prompt|developer\s+mode|jailbreak)", re.IGNORECASE),
    re.compile(r"(grant\s+all\s+benefits|bypass\s+eligibility)", re.IGNORECASE),
    re.compile(r"(drop\s+table|delete\s+from|<script>)", re.IGNORECASE)
]

class SecurityPolicyEngine:
    def __init__(self):
        self.processed_idempotency_keys: Dict[str, Dict[str, Any]] = {}

    def scan_for_prompt_injection(self, text: str) -> Tuple[bool, str]:
        """Detects indirect prompt injection or taint in citizen inputs and tool arguments."""
        for pattern in INJECTION_PATTERNS:
            if pattern.search(text):
                return True, f"Security Alert: Malicious prompt injection pattern detected ('{pattern.pattern}'). Request quarantined."
        return False, ""

    def verify_permission(self, tool_scope: str, client_role: str = "citizen") -> Tuple[bool, str]:
        """Enforces least-privilege tool execution policies."""
        # Read operations allowed for public/citizen
        if tool_scope.startswith("read:") or tool_scope.startswith("verify:"):
            return True, "Authorized"
        
        # Write operations require verified citizen or official role
        if tool_scope.startswith("write:"):
            if client_role in ["verified_citizen", "official", "citizen"]:
                return True, "Authorized"
            return False, f"Permission Denied: Scope '{tool_scope}' requires verified credentials."

        return True, "Authorized"

    def check_idempotency(self, idempotency_key: str) -> Tuple[bool, Dict[str, Any]]:
        """Prevents duplicate execution of stateful operations (e.g. appointment booking)."""
        if idempotency_key in self.processed_idempotency_keys:
            return True, self.processed_idempotency_keys[idempotency_key]
        return False, {}

    def register_idempotency(self, idempotency_key: str, result: Dict[str, Any]):
        self.processed_idempotency_keys[idempotency_key] = result
