"""
Unit tests for rubric verifiers, reward functions, and anti-looping penalties.
"""
import pytest
from rewards.verifiers import TrajectoryVerifier
from rewards.grpo_rewards import (
    format_reward_func, 
    tool_execution_reward_func, 
    trajectory_outcome_reward_func,
    REGISTERED_TOOL_NAMES
)
from agent.schema import AgentTrajectory, Turn, ToolCall, ToolResult

def test_syntax_and_schema_verifier_valid():
    completion = """<think>Looking up scheme.</think>
<tool_call>
{"name": "search_schemes", "arguments": {"query": "farmer"}}
</tool_call>"""
    score, info = TrajectoryVerifier.verify_syntax_and_schema(completion, REGISTERED_TOOL_NAMES)
    assert score >= 0.7
    assert info["valid_tags"] is True
    assert info["valid_json"] is True
    assert info["valid_tool"] is True

def test_syntax_verifier_unknown_tool_penalized():
    completion = """<tool_call>
{"name": "non_existent_hack_tool", "arguments": {}}
</tool_call>"""
    score, info = TrajectoryVerifier.verify_syntax_and_schema(completion, REGISTERED_TOOL_NAMES)
    assert info["valid_tool"] is False
    assert "Unknown tool" in info.get("error", "")

def test_anti_looping_penalty():
    traj = AgentTrajectory(task_id="loop-test", user_prompt="test")
    # First invocation
    traj.turns.append(Turn(role="assistant", content="calling slots", tool_call=ToolCall(name="check_center_slots", arguments={"center_id": "SEVA_PUNE_NORTH"})))
    penalty1, _ = TrajectoryVerifier.check_looping_and_redundancy(traj)
    assert penalty1 == 0.0

    # Redundant duplicate invocation with identical arguments
    traj.turns.append(Turn(role="assistant", content="calling slots again", tool_call=ToolCall(name="check_center_slots", arguments={"center_id": "SEVA_PUNE_NORTH"})))
    penalty2, warnings = TrajectoryVerifier.check_looping_and_redundancy(traj)
    assert penalty2 < 0.0, "Duplicate tool call must receive negative looping penalty"
    assert len(warnings) >= 1

def test_ground_truth_outcome_verifier():
    traj = AgentTrajectory(task_id="gt-test", user_prompt="Check PMMVY eligibility")
    traj.turns.append(Turn(role="assistant", content="calling verify", tool_call=ToolCall(name="verify_eligibility", arguments={"scheme_id": "PMMVY"})))
    traj.final_answer = "Eligible for benefit of Rs. 5000 under PMMVY."

    gt = {
        "expected_tools": ["verify_eligibility"],
        "required_output_substrings": ["5000", "PMMVY"],
        "must_not_contain": ["rejected"]
    }
    score, report = TrajectoryVerifier.verify_ground_truth_outcome(traj, gt)
    assert score >= 0.9
    assert report["tools_matched"] is True
    assert report["final_answer_present"] is True
