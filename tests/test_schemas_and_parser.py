"""
Unit tests for response parsing, XML tags extraction, and trajectory schemas.
"""
import pytest
from agent.parser import parse_agent_response
from agent.schema import ToolCall, ToolResult, Turn, AgentTrajectory

def test_parse_valid_tool_call():
    text = """<think>Citizen wants to search schemes.</think>
<tool_call>
{"name": "search_schemes", "arguments": {"query": "farmer"}}
</tool_call>"""
    thought, tool_call, final_answer, parse_error = parse_agent_response(text)
    assert thought == "Citizen wants to search schemes."
    assert tool_call is not None
    assert tool_call.name == "search_schemes"
    assert tool_call.arguments == {"query": "farmer"}
    assert final_answer is None
    assert parse_error is None

def test_parse_final_answer():
    text = """<final_answer>
Eligibility confirmed. Benefit: Rs. 5000 under PMMVY.
</final_answer>"""
    thought, tool_call, final_answer, parse_error = parse_agent_response(text)
    assert thought is None
    assert tool_call is None
    assert final_answer is not None
    assert "PMMVY" in final_answer
    assert parse_error is None

def test_parse_malformed_json_tool_call():
    text = """<tool_call>
{"name": "search_schemes", "arguments": {broken_json
</tool_call>"""
    thought, tool_call, final_answer, parse_error = parse_agent_response(text)
    assert tool_call is None
    assert parse_error is not None
    assert "JSON syntax error" in parse_error

def test_trajectory_schema_properties():
    traj = AgentTrajectory(task_id="test-task", user_prompt="Help me with welfare")
    assert traj.task_id == "test-task"
    assert traj.total_steps == 0
    assert traj.success is False

    traj.turns.append(Turn(role="user", content="Help me with welfare"))
    traj.turns.append(Turn(role="assistant", content="<think>Evaluating</think>"))
    assert len(traj.turns) == 2
