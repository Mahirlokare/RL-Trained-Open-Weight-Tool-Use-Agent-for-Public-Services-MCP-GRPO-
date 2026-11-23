"""
Interactive Demo for RL-Trained Public Services MCP Agent.
"""
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_servers.services import create_default_mcp_hub
from agent.runtime import MCPAgentRuntime
from run_eval import rl_trained_policy

def run_interactive_demo():
    print("=" * 70)
    print("   CIVIC AI: PUBLIC WELFARE MCP AGENT (RL-TRAINED GRPO SLICE)")
    print("=" * 70)
    print("Connected MCP Servers:")
    print(" - scheme-service       (search_schemes, get_scheme_details)")
    print(" - document-service     (verify_eligibility)")
    print(" - appointment-service  (check_center_slots, book_appointment)")
    print(" - notification-service (send_confirmation_sms)")
    print("=" * 70)

    sample_queries = [
        "1. Check pregnant citizen eligibility for PMMVY (Age: 23, Income: 350k, all docs ready)",
        "2. Check senior citizen eligibility for VAYO_SHRESTHA (Age: 70, Income: 500k)",
        "3. Book PM_KISAN verification slot for Devidas at SEVA_NAGPUR_EAST and dispatch SMS",
    ]

    print("\nSample queries:")
    for q in sample_queries:
        print(f"  {q}")

    hub = create_default_mcp_hub()
    runtime = MCPAgentRuntime(mcp_hub=hub, model_fn=rl_trained_policy)

    print("\n--- Running Live Trace for Query 3 (Multi-tool appointment & SMS dispatch) ---")
    query = "Book an appointment for Devidas (PM_KISAN) at SEVA_NAGPUR_EAST and dispatch an SMS confirmation to his phone 9822334455."
    print(f"User Query: \"{query}\"\n")

    traj = runtime.run_task(task_id="demo-interactive", user_prompt=query)

    for i, turn in enumerate(traj.turns):
        if turn.role == "user" and i == 0:
            continue
        print(f"[{turn.role.upper()} TURN]")
        if turn.thought:
            print(f"Thinking: {turn.thought}")
        if turn.tool_call:
            print(f"Tool Invocation: {turn.tool_call.name}")
            print(f"Arguments: {json.dumps(turn.tool_call.arguments)}")
        if turn.tool_result:
            print(f"MCP Tool Output: {json.dumps(turn.tool_result.output)}")
        if not turn.tool_call and not turn.tool_result and turn.content:
            print(f"Content:\n{turn.content.strip()}")
        print("-" * 50)

    print("\nTask Outcome:")
    print(f"Total Steps: {traj.total_steps}")
    print(f"Success Status: {traj.success}")
    print(f"Final Answer: {traj.final_answer}")
    print("=" * 70)

if __name__ == "__main__":
    run_interactive_demo()
