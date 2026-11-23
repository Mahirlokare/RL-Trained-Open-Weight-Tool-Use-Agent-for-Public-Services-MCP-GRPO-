"""
Rubric-based verifiers for multi-turn MCP tool trajectories.
Provides fine-grained, verifiable feedback signals for GRPO training.
"""
from typing import Dict, Any, List, Tuple
from agent.schema import AgentTrajectory
from agent.parser import parse_agent_response

class TrajectoryVerifier:
    """Evaluates syntactic, schema, and behavioral validity of agent steps."""

    @staticmethod
    def verify_syntax_and_schema(raw_text: str, registered_tools: List[str]) -> Tuple[float, Dict[str, Any]]:
        score = 0.0
        info = {"valid_tags": False, "valid_json": False, "valid_tool": False}
        
        thought, tool_call, final_answer, parse_error = parse_agent_response(raw_text)
        
        if tool_call or final_answer or thought:
            score += 0.2
            info["valid_tags"] = True

        if parse_error is None and (tool_call or final_answer):
            score += 0.2
            info["valid_json"] = True

        if tool_call:
            if tool_call.name in registered_tools:
                score += 0.3
                info["valid_tool"] = True
            else:
                score -= 0.2  # Hallucinated tool name
                info["error"] = f"Unknown tool '{tool_call.name}'"

        return score, info

    @staticmethod
    def check_looping_and_redundancy(trajectory: AgentTrajectory) -> Tuple[float, List[str]]:
        penalty = 0.0
        warnings = []
        executed_calls = []

        for turn in trajectory.turns:
            if turn.tool_call:
                call_sig = (turn.tool_call.name, str(sorted(turn.tool_call.arguments.items())))
                if call_sig in executed_calls:
                    penalty -= 0.35
                    warnings.append(f"Redundant call to {turn.tool_call.name}")
                executed_calls.append(call_sig)

        return penalty, warnings

    @staticmethod
    def verify_ground_truth_outcome(trajectory: AgentTrajectory, ground_truth: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Validates if the trajectory achieved the specific task goal.
        Expected keys in ground_truth:
        - 'expected_tools': list of tools that must have been called
        - 'required_output_substrings': list of substrings required in final_answer
        - 'must_not_contain': strings that indicate hallucination
        """
        outcome_score = 0.0
        report = {"tools_matched": False, "final_answer_present": False, "grounding_verified": True}

        # 1. Check final answer presence
        if not trajectory.final_answer:
            return 0.0, {"error": "No final answer emitted"}
        
        outcome_score += 0.3
        report["final_answer_present"] = True

        # 2. Check if required tools were invoked
        called_tools = [turn.tool_call.name for turn in trajectory.turns if turn.tool_call]
        expected_tools = ground_truth.get("expected_tools", [])
        
        missing_tools = [t for t in expected_tools if t not in called_tools]
        if not missing_tools:
            outcome_score += 0.4
            report["tools_matched"] = True
        else:
            report["missing_tools"] = missing_tools

        # 3. Check answer grounding against actual tool outputs
        answer_text = trajectory.final_answer.lower()
        for substr in ground_truth.get("required_output_substrings", []):
            if substr.lower() in answer_text:
                outcome_score += 0.15
            else:
                report["grounding_verified"] = False

        for forbidden in ground_truth.get("must_not_contain", []):
            if forbidden.lower() in answer_text:
                outcome_score -= 0.4
                report["forbidden_content_detected"] = forbidden

        return max(0.0, outcome_score), report
