"""
Agent execution runtime for multi-turn MCP tool calling.
"""
from typing import Callable, Optional, Dict, Any, List
import json
from mcp_servers.registry import MCPHub
from agent.schema import AgentTrajectory, Turn, ToolCall, ToolResult
from agent.prompts import format_system_prompt
from agent.parser import parse_agent_response

class MCPAgentRuntime:
    def __init__(self, mcp_hub: MCPHub, model_fn: Callable[[List[Dict[str, str]]], str], max_iterations: int = 6):
        self.hub = mcp_hub
        self.model_fn = model_fn
        self.max_iterations = max_iterations
        self.system_prompt = format_system_prompt(self.hub.get_all_tools())

    def run_task(self, task_id: str, user_prompt: str) -> AgentTrajectory:
        trajectory = AgentTrajectory(task_id=task_id, user_prompt=user_prompt)
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        trajectory.turns.append(Turn(role="user", content=user_prompt))

        for iteration in range(self.max_iterations):
            # Generate assistant response
            raw_response = self.model_fn(messages)
            thought, tool_call, final_answer, parse_error = parse_agent_response(raw_response)
            
            turn = Turn(
                role="assistant",
                content=raw_response,
                thought=thought,
                tool_call=tool_call
            )

            # If there was a parse error in tool call
            if parse_error:
                error_response = f"<tool_response>\n{{\"isError\": true, \"error\": \"{parse_error}\"}}\n</tool_response>"
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": error_response})
                trajectory.turns.append(turn)
                trajectory.turns.append(Turn(role="tool", content=error_response, tool_result=ToolResult(tool_name="unknown", output={"error": parse_error}, is_error=True)))
                continue

            # If tool call exists, execute via MCP Hub
            if tool_call:
                tool_exec_result = self.hub.execute_call(tool_call.name, tool_call.arguments)
                tool_result_obj = ToolResult(
                    tool_name=tool_call.name,
                    output=tool_exec_result,
                    is_error=tool_exec_result.get("isError", False)
                )
                turn.tool_result = tool_result_obj
                trajectory.turns.append(turn)

                # Format tool output back to agent context
                tool_resp_str = f"<tool_response>\n{json.dumps(tool_exec_result, indent=2, ensure_ascii=False)}\n</tool_response>"
                messages.append({"role": "assistant", "content": raw_response})
                messages.append({"role": "user", "content": tool_resp_str})
                trajectory.turns.append(Turn(role="tool", content=tool_resp_str, tool_result=tool_result_obj))

                # Check if final answer was also provided in the same turn (unusual but possible)
                if final_answer:
                    trajectory.final_answer = final_answer
                    trajectory.success = True
                    break
                continue

            # If final answer provided without tool call
            if final_answer:
                trajectory.final_answer = final_answer
                trajectory.success = True
                trajectory.turns.append(turn)
                break

            # If neither tool call nor final answer was found (freeform text)
            trajectory.turns.append(turn)
            messages.append({"role": "assistant", "content": raw_response})
            # Remind agent of output contract
            prompt_reminder = "Please use <tool_call>...</tool_call> to invoke a tool, or <final_answer>...</final_answer> to conclude."
            messages.append({"role": "user", "content": prompt_reminder})

        trajectory.total_steps = len(trajectory.turns)
        return trajectory
