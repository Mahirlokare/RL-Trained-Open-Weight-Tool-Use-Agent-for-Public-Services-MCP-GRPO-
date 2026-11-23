"""
Unit and integration tests for Model Context Protocol (MCP) servers and tools.
"""
import pytest
import json
from mcp_servers.services import create_default_mcp_hub, SCHEMES_DB
from mcp_servers.security import SecurityPolicyEngine
from mcp_servers.registry import MCPToolServer

def test_hub_registers_all_five_servers():
    hub = create_default_mcp_hub()
    tools = hub.get_all_tools()
    assert len(tools) >= 7
    tool_names = [t["name"] for t in tools]
    assert "search_schemes" in tool_names
    assert "get_scheme_details" in tool_names
    assert "scan_document_ocr" in tool_names
    assert "verify_eligibility" in tool_names
    assert "check_center_slots" in tool_names
    assert "book_appointment" in tool_names
    assert "send_confirmation_sms" in tool_names

def test_search_schemes_execution():
    hub = create_default_mcp_hub()
    res = hub.execute_call("search_schemes", {"query": "farmer"})
    assert res["isError"] is False
    payload = json.loads(res["content"][0]["text"])
    assert payload["total_matches"] >= 1
    assert payload["scope"] == "read:schemes"

def test_get_scheme_details():
    hub = create_default_mcp_hub()
    res = hub.execute_call("get_scheme_details", {"scheme_id": "PM_KISAN"})
    assert res["isError"] is False
    payload = json.loads(res["content"][0]["text"])
    assert payload["found"] is True
    assert payload["scheme"]["benefit_amount"] == 6000

def test_argument_validation_missing_required():
    sec = SecurityPolicyEngine()
    server = MCPToolServer("test-srv", "test", sec)
    server.register_tool(
        name="test_tool",
        description="desc",
        input_schema={"type": "object", "required": ["param1"], "properties": {"param1": {"type": "string"}}},
        handler=lambda param1: {"ok": True}
    )
    res = server.call_tool("test_tool", {})
    assert res["isError"] is True
    assert res["validationError"] is True
    assert "Missing required argument 'param1'" in res["content"][0]["text"]

def test_argument_validation_invalid_type():
    sec = SecurityPolicyEngine()
    server = MCPToolServer("test-srv", "test", sec)
    server.register_tool(
        name="test_tool",
        description="desc",
        input_schema={"type": "object", "properties": {"age": {"type": "number"}}},
        handler=lambda age: {"ok": True}
    )
    res = server.call_tool("test_tool", {"age": "not-a-number"})
    assert res["isError"] is True
    assert res["validationError"] is True
    assert "expected number" in res["content"][0]["text"]

def test_idempotent_replay_on_stateful_write():
    hub = create_default_mcp_hub()
    args = {
        "center_id": "SEVA_PUNE_NORTH",
        "slot_time": "2026-12-05 10:00 AM",
        "citizen_name": "Ramesh Patil",
        "scheme_id": "PM_KISAN"
    }
    # First call with authorized administrative role
    res1 = hub.execute_call("book_appointment", args, client_role="official")
    assert res1["isError"] is False
    token1 = json.loads(res1["content"][0]["text"])["booking_reference"]

    # Second call with identical arguments
    res2 = hub.execute_call("book_appointment", args, client_role="official")
    assert res2["isError"] is False
    assert res2.get("idempotentReplay") is True
    token2 = json.loads(res2["content"][0]["text"])["booking_reference"]
    assert token1 == token2, "Idempotent replay must return identical booking token"
