"""
Benchmark runner and ablation evaluator for MCP agents.
Compares:
1. Naive Zero-Shot / Prompting Baseline
2. SFT Warm-Start Baseline
3. RL-Trained Policy (GRPO)
"""
import os
import sys
import json
import time

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from typing import Dict, Any, List, Callable
from agent.runtime import MCPAgentRuntime
from agent.schema import AgentTrajectory
from mcp_servers.services import create_default_mcp_hub
from rewards.verifiers import TrajectoryVerifier

class BenchmarkSuite:
    def __init__(self, test_cases_path: str):
        with open(test_cases_path, "r", encoding="utf-8") as f:
            self.test_cases = json.load(f)

    def evaluate_policy(
        self, 
        policy_name: str, 
        model_fn: Callable[[List[Dict[str, str]]], str]
    ) -> Dict[str, Any]:
        hub = create_default_mcp_hub()
        runtime = MCPAgentRuntime(mcp_hub=hub, model_fn=model_fn)
        
        trajectories: List[AgentTrajectory] = []
        latencies: List[float] = []
        total_tool_calls = 0
        valid_tool_calls = 0
        passed_tasks = 0

        for test_case in self.test_cases:
            t0 = time.time()
            traj = runtime.run_task(
                task_id=test_case["task_id"], 
                user_prompt=test_case["prompt"]
            )
            elapsed = time.time() - t0
            latencies.append(elapsed)
            trajectories.append(traj)

            # Check tool call validity
            for turn in traj.turns:
                if turn.tool_call:
                    total_tool_calls += 1
                    if turn.tool_result and not turn.tool_result.is_error:
                        valid_tool_calls += 1

            # Check outcome against ground truth
            outcome_score, report = TrajectoryVerifier.verify_ground_truth_outcome(
                traj, test_case["ground_truth"]
            )
            if outcome_score >= 0.7:
                passed_tasks += 1

        pass_rate = (passed_tasks / len(self.test_cases)) * 100.0
        tool_validity = (valid_tool_calls / max(1, total_tool_calls)) * 100.0
        avg_steps = sum(t.total_steps for t in trajectories) / max(1, len(trajectories))
        
        # Calculate cost estimate: ~800 tokens/turn on average
        avg_tokens_per_task = avg_steps * 400
        # Frontier API baseline price: ~$2.50 per 1M tokens vs local 8B: ~$0.12 equivalent compute
        cost_per_1k_tasks = (avg_tokens_per_task * 1000 / 1_000_000) * (0.15 if "RL" in policy_name else 2.50)

        latencies.sort()
        p95_latency = latencies[int(0.95 * len(latencies))] if latencies else 0.0

        return {
            "policy": policy_name,
            "tasks_evaluated": len(self.test_cases),
            "pass_rate_pct": round(pass_rate, 1),
            "tool_call_validity_pct": round(tool_validity, 1),
            "avg_steps": round(avg_steps, 2),
            "p95_latency_sec": round(p95_latency, 3),
            "estimated_cost_per_1k_tasks_usd": round(cost_per_1k_tasks, 3),
            "trajectories": trajectories
        }
