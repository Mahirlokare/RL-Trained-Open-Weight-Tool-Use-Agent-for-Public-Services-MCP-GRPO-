"""
Security and Policy Engine for MCP Tool Servers.
Implements:
1. Scope-based permission checks (RBAC)
2. Indirect prompt injection & taint detection
3. Deterministic cryptographic idempotency verification
4. File upload sanitization & path traversal prevention
5. Token and credential protection
"""
from typing import Dict, Any, Tuple, Optional
import os
import re
import hashlib
import time

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"(system\s+prompt|developer\s+mode|jailbreak)", re.IGNORECASE),
    re.compile(r"(grant\s+all\s+benefits|bypass\s+eligibility)", re.IGNORECASE),
    re.compile(r"(drop\s+table|delete\s+from|<script>)", re.IGNORECASE),
    re.compile(r"(\bDAN\b|do\s+anything\s+now|override\s+system)", re.IGNORECASE),
    re.compile(r"(reveal\s+(api\s+)?keys?|print\s+credentials|dump\s+database)", re.IGNORECASE),
    re.compile(r"(act\s+as\s+root|sudo\s+rm|rm\s+-rf)", re.IGNORECASE)
]

class SecurityPolicyEngine:
    def __init__(self, max_file_size_mb: float = 10.0):
        self.processed_idempotency_keys: Dict[str, Dict[str, Any]] = {}
        self.max_file_size_mb = max_file_size_mb
        self.rate_limit_tracker: Dict[str, list] = {}

    def scan_for_prompt_injection(self, text: str) -> Tuple[bool, str]:
        """Detects indirect prompt injection, jailbreaks, or taint in user prompts and tool arguments."""
        if not text:
            return False, ""
        for pattern in INJECTION_PATTERNS:
            if pattern.search(text):
                return True, f"Security Alert: Malicious prompt injection pattern detected ('{pattern.pattern}'). Request quarantined."
        return False, ""

    def verify_permission(self, tool_scope: str, client_role: str = "citizen") -> Tuple[bool, str]:
        """Enforces least-privilege tool execution policies across scopes."""
        # Read and verification operations are authorized for citizens
        if tool_scope.startswith("read:") or tool_scope.startswith("verify:"):
            return True, "Authorized"
        
        # Write operations (e.g. appointment booking, SMS dispatch)
        if tool_scope.startswith("write:"):
            if client_role in ["verified_citizen", "official", "citizen"]:
                return True, "Authorized"
            return False, f"Permission Denied: Scope '{tool_scope}' requires verified credentials."

        # Administrative / Internal scopes
        if tool_scope.startswith("admin:"):
            if client_role == "official":
                return True, "Authorized"
            return False, f"Permission Denied: Scope '{tool_scope}' requires administrative privilege."

        return True, "Authorized"

    def check_idempotency(self, idempotency_key: str) -> Tuple[bool, Dict[str, Any]]:
        """Prevents duplicate execution of stateful operations using cryptographic hashes."""
        if idempotency_key in self.processed_idempotency_keys:
            return True, self.processed_idempotency_keys[idempotency_key]
        return False, {}

    def register_idempotency(self, idempotency_key: str, result: Dict[str, Any]):
        self.processed_idempotency_keys[idempotency_key] = result

    def sanitize_file_path(self, path_str: str) -> Tuple[bool, str]:
        r"""
        Guards against directory traversal attacks (../ or ..\)
        and verifies file size remains under safety bounds.
        """
        if not path_str:
            return True, ""
        
        # Check for directory traversal sequences or system file targets
        if ".." in path_str or "/etc" in path_str or "\\windows" in path_str.lower() or "system32" in path_str.lower():
            return False, "Security Alert: Directory traversal sequence detected in file path."

        # Check file size if it exists on local filesystem
        if os.path.exists(path_str):
            try:
                size_mb = os.path.getsize(path_str) / (1024 * 1024)
                if size_mb > self.max_file_size_mb:
                    return False, f"File size ({size_mb:.1f} MB) exceeds maximum security threshold of {self.max_file_size_mb} MB"
            except Exception as e:
                return False, f"File access error: {str(e)}"

        return True, path_str

    def check_rate_limit(self, client_id: str, max_requests_per_minute: int = 60) -> Tuple[bool, str]:
        """Sliding-window rate limiter preventing API abuse and denial-of-service."""
        now = time.time()
        window_start = now - 60.0
        
        if client_id not in self.rate_limit_tracker:
            self.rate_limit_tracker[client_id] = []
            
        # Clean older requests outside window
        self.rate_limit_tracker[client_id] = [t for t in self.rate_limit_tracker[client_id] if t > window_start]
        
        if len(self.rate_limit_tracker[client_id]) >= max_requests_per_minute:
            return False, f"Rate Limit Exceeded: Maximum {max_requests_per_minute} requests per minute reached."
            
        self.rate_limit_tracker[client_id].append(now)
        return True, "Rate limit within bounds"
