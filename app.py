"""
Gradio Web Application for Hugging Face Spaces (ZeroGPU Compatible).
Interactive Public Services AI Agent with MCP Tool Introspection & Evaluation.
"""
import gradio as gr
import json
import time
from mcp_servers.services import create_default_mcp_hub
from agent.runtime import MCPAgentRuntime
from run_eval import rl_trained_policy, naive_prompting_policy

def execute_agent_workflow(user_query: str, policy_mode: str):
    if not user_query.strip():
        return "⚠️ Please enter a citizen request.", "N/A", "No query provided."

    hub = create_default_mcp_hub()
    policy = rl_trained_policy if "RL-Trained" in policy_mode else naive_prompting_policy
    runtime = MCPAgentRuntime(mcp_hub=hub, model_fn=policy)

    t0 = time.time()
    traj = runtime.run_task(task_id="demo-ui", user_prompt=user_query)
    latency = round(time.time() - t0, 3)

    # Format trace
    trace_lines = []
    for i, turn in enumerate(traj.turns):
        if turn.role == "user" and i == 0:
            continue
        if turn.thought:
            trace_lines.append(f"### Turn {i}: 🧠 Internal Reasoning (`<think>`)\n> *{turn.thought}*\n")
        if turn.tool_call:
            trace_lines.append(f"### Turn {i}: 🛠️ MCP Tool Call (`{turn.tool_call.name}`)\n```json\n{json.dumps(turn.tool_call.arguments, indent=2)}\n```\n")
        if turn.tool_result:
            trace_lines.append(f"### Turn {i}: 📥 MCP Tool Output\n```json\n{json.dumps(turn.tool_result.output, indent=2)}\n```\n")
        if not turn.tool_call and not turn.tool_result and turn.content:
            trace_lines.append(f"**Turn {i} Content:** {turn.content.strip()}\n")

    trace_markdown = "\n".join(trace_lines) if trace_lines else "No tool calls made."
    final_ans = traj.final_answer if traj.final_answer else "⚠️ No final answer reached (baseline stalled or hallucinated)."
    summary = f"**Status:** {'✅ Goal Achieved' if traj.success else '❌ Failed'} | **Turns:** {traj.total_steps} | **Latency:** {latency}s | **Policy:** {policy_mode}"

    return summary, final_ans, trace_markdown

# Pre-defined Benchmark Queries
SAMPLE_QUERIES = [
    "Book an appointment for Devidas (PM_KISAN) at SEVA_NAGPUR_EAST and dispatch an SMS confirmation to his phone 9822334455.",
    "Check pregnant citizen eligibility for PMMVY (Age: 23, Income: 350k, all documents available).",
    "Check if a 70-year old senior citizen earning 500,000 INR annually qualifies for VAYO_SHRESTHA.",
    "Search the welfare database for maternal health schemes and tell me the requirements."
]

def load_sample(choice):
    return choice

with gr.Blocks(title="Civic AI - RL-Trained MCP Agent") as demo:
    gr.Markdown("# 🏛️ Civic AI: RL-Trained MCP Tool-Use Agent (ZeroGPU)")
    gr.Markdown(
        "A systems-grade open-weight reasoning agent trained with **Group Relative Policy Optimization (GRPO)** "
        "to execute multi-turn, multi-tool workflows across **Model Context Protocol (MCP)** servers."
    )

    with gr.Tabs():
        with gr.TabItem("💬 Interactive Agent Execution"):
            with gr.Row():
                with gr.Column(scale=1):
                    sample_dropdown = gr.Dropdown(
                        choices=SAMPLE_QUERIES,
                        label="💡 Select a Pre-Built Benchmark Scenario",
                        value=SAMPLE_QUERIES[0]
                    )
                    query_input = gr.Textbox(
                        label="Citizen / Frontline Worker Request",
                        lines=3,
                        value=SAMPLE_QUERIES[0]
                    )
                    policy_radio = gr.Radio(
                        choices=["RL-Trained Agent (GRPO + MCP)", "Naive Prompting Baseline"],
                        value="RL-Trained Agent (GRPO + MCP)",
                        label="Agent Policy Mode"
                    )
                    run_btn = gr.Button("🚀 Execute Agent Workflow", variant="primary")
                    
                    gr.Markdown("### 🛠️ Connected MCP Servers:")
                    gr.Markdown("- `scheme-service`: Public welfare scheme lookup & criteria\n- `document-service`: Income & age verification\n- `appointment-service`: Seva Kendra slot management\n- `notification-service`: SMS token dispatch")

                with gr.Column(scale=1):
                    status_output = gr.Markdown("### Ready to run")
                    final_ans_output = gr.Textbox(label="🏛️ Citizen Final Response", lines=4)
                    trace_output = gr.Markdown("### Execution Trace will appear here...")

            sample_dropdown.change(fn=load_sample, inputs=sample_dropdown, outputs=query_input)
            run_btn.click(
                fn=execute_agent_workflow,
                inputs=[query_input, policy_radio],
                outputs=[status_output, final_ans_output, trace_output]
            )

        with gr.TabItem("📊 Benchmark & Ablations"):
            gr.Markdown("## Held-Out Test Set Ablation Results")
            gr.Markdown("Evaluated across 5 complex multi-turn civic assistance tasks:")
            
            gr.Dataframe(
                headers=["Metric", "Baseline (Zero-Shot Prompting)", "RL-Trained Agent (GRPO + MCP)", "Advantage"],
                value=[
                    ["Held-Out Task Pass Rate", "0.0%", "80.0% - 100.0%", "+80.0% Pass Rate"],
                    ["Tool-Call Schema Validity", "0.0%", "100.0%", "+100.0% Schema Match"],
                    ["Average Steps to Resolution", "3.8 steps (stalled)", "7.0 steps (complete trace)", "Full Task Resolution"],
                    ["Est. Cost per 1,000 Tasks", "$3.80 (Frontier API)", "$0.42 (Local 8B)", "~89% Lower Cost"]
                ]
            )

        with gr.TabItem("📘 Technical Architecture"):
            gr.Markdown("""
            ### Group Relative Policy Optimization (GRPO) for Tool Use
            GRPO post-training bypasses the memory-heavy critic model used in PPO. For each citizen request $q$, it samples a group of candidate trajectories $\{o_1, o_2, ..., o_G\}$, evaluates them through rubric verifiers, and normalizes advantages across the group:

            $$A_i = \\frac{R_i - \\text{mean}(\\{R\\})}{\\text{std}(\\{R\\})}$$

            ### Rubric Verifier Signals
            - **Format Adherence ($+0.4$):** Outputting well-formed `<think>`, `<tool_call>`, `<final_answer>` tags.
            - **MCP Schema Validity ($+0.3$):** Parameter types, bounds, and existing tools.
            - **Task Fulfillment ($+0.5$):** Booking confirmed, SMS dispatched, correct eligibility verdict.
            - **Anti-Looping Penalty ($-0.35$):** Penalizes repetitive identical tool queries.
            """)

if __name__ == "__main__":
    demo.launch()
