"""
Parsing utilities for extracting thought, tool calls, and final answers.
"""
import re
import json
from typing import Optional, Tuple, Dict, Any
from agent.schema import ToolCall

THINK_REGEX = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)
TOOL_CALL_REGEX = re.compile(r"<tool_call>(.*?)</tool_call>", re.DOTALL | re.IGNORECASE)
FINAL_ANSWER_REGEX = re.compile(r"<final_answer>(.*?)</final_answer>", re.DOTALL | re.IGNORECASE)

def parse_agent_response(text: str) -> Tuple[Optional[str], Optional[ToolCall], Optional[str], Optional[str]]:
    """
    Parses LLM generation.
    Returns (thought, tool_call, final_answer, parse_error)
    """
    thought = None
    tool_call = None
    final_answer = None
    parse_error = None

    # Extract thought if present
    think_match = THINK_REGEX.search(text)
    if think_match:
        thought = think_match.group(1).strip()

    # Extract tool call
    tc_match = TOOL_CALL_REGEX.search(text)
    if tc_match:
        raw_json = tc_match.group(1).strip()
        try:
            parsed = json.loads(raw_json)
            if not isinstance(parsed, dict) or "name" not in parsed or "arguments" not in parsed:
                parse_error = f"Malformed tool_call payload: missing 'name' or 'arguments'. Content: {raw_json}"
            else:
                tool_call = ToolCall(
                    name=parsed["name"],
                    arguments=parsed.get("arguments", {}),
                    raw_text=raw_json
                )
        except json.JSONDecodeError as err:
            parse_error = f"JSON syntax error in tool_call: {err}. Content: {raw_json}"

    # Extract final answer
    fa_match = FINAL_ANSWER_REGEX.search(text)
    if fa_match:
        final_answer = fa_match.group(1).strip()

    return thought, tool_call, final_answer, parse_error
