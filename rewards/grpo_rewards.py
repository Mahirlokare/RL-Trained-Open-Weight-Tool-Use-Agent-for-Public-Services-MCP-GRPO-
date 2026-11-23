"""
TRL / GRPO compatible reward functions.
GRPO evaluates a group of generations sampled from the current policy,
normalizing rewards across the group to compute policy advantages.
"""
from typing import List, Dict, Any, Optional
import math
from rewards.verifiers import TrajectoryVerifier
from agent.schema import AgentTrajectory
from agent.parser import parse_agent_response

REGISTERED_TOOL_NAMES = [
    "search_schemes",
    "get_scheme_details",
    "verify_eligibility",
    "scan_document_ocr",
    "check_center_slots",
    "book_appointment",
    "send_confirmation_sms"
]

def format_reward_func(completions: List[str], **kwargs) -> List[float]:
    """Rewards adherence to XML tags (<tool_call>, <final_answer>) and valid JSON."""
    rewards = []
    for comp in completions:
        score, _ = TrajectoryVerifier.verify_syntax_and_schema(comp, REGISTERED_TOOL_NAMES)
        rewards.append(score)
    return rewards

def schema_reward_func(completions: List[str], **kwargs) -> List[float]:
    """Checks whether the completion contains valid JSON tool schemas and recognized tool names."""
    rewards = []
    for comp in completions:
        thought, tool_call, final_answer, parse_error = parse_agent_response(comp)
        if tool_call is not None and not parse_error:
            if tool_call.name in REGISTERED_TOOL_NAMES and isinstance(tool_call.arguments, dict):
                rewards.append(0.3)
            else:
                rewards.append(-0.3)
        elif final_answer is not None:
            rewards.append(0.1)
        else:
            rewards.append(-0.2)
    return rewards

def outcome_reward_func(completions: List[str], ground_truth_list: Optional[List[Dict[str, Any]]] = None, **kwargs) -> List[float]:
    """Evaluates task outcome relevance against expected domain/tool."""
    rewards = []
    gt_list = ground_truth_list or [{}] * len(completions)
    for comp, gt in zip(completions, gt_list):
        thought, tool_call, final_answer, parse_error = parse_agent_response(comp)
        score = 0.0
        if tool_call is not None and not parse_error:
            expected_tool = gt.get("expected_first_tool") or "search_schemes"
            if tool_call.name == expected_tool:
                score += 0.5
            else:
                score += 0.1
        elif final_answer is not None:
            if gt.get("expected_outcome") and gt.get("expected_outcome") in comp:
                score += 0.4
            else:
                score += 0.1
        rewards.append(score)
    return rewards

def loop_penalty_func(completions: List[str], **kwargs) -> List[float]:
    """Penalizes repetition and redundant tool calling."""
    penalties = []
    for comp in completions:
        penalty = 0.0
        if comp.count("<tool_call>") > 1:
            penalty -= 0.25
        if "Analyzing citizen requirement" in comp and comp.count("Analyzing") > 1:
            penalty -= 0.2
        penalties.append(penalty)
    return penalties

def compute_grpo_group_advantages(group_rewards: List[float], eps: float = 1e-8) -> List[float]:
    """
    Computes GRPO relative advantages:
    A_i = (R_i - mean(R)) / (std(R) + eps)
    """
    if not group_rewards:
        return []
    n = len(group_rewards)
    mean_r = sum(group_rewards) / n
    variance = sum((r - mean_r) ** 2 for r in group_rewards) / n
    std_r = math.sqrt(variance)
    if std_r < 1e-6:
        # If all candidates receive identical rewards, advantage is zero
        return [0.0 for _ in group_rewards]
    return [(r - mean_r) / (std_r + eps) for r in group_rewards]

def tool_execution_reward_func(trajectories: List[AgentTrajectory], **kwargs) -> List[float]:
    """Rewards non-error tool executions and penalizes error status."""
    rewards = []
    for traj in trajectories:
        score = 0.0
        tool_turns = [turn for turn in traj.turns if turn.tool_result]
        if not tool_turns:
            rewards.append(0.0)
            continue
        
        for turn in tool_turns:
            if not turn.tool_result.is_error:
                score += 0.25
            else:
                score -= 0.3
        rewards.append(score)
    return rewards

def trajectory_outcome_reward_func(
    trajectories: List[AgentTrajectory], 
    ground_truth_list: List[Dict[str, Any]], 
    **kwargs
) -> List[float]:
    """
    Computes overall end-to-end task fulfillment reward, incorporating:
    - Format adherence
    - Tool outcome completion
    - Loop & repetition penalties
    """
    total_rewards = []
    for traj, gt in zip(trajectories, ground_truth_list):
        outcome_score, report = TrajectoryVerifier.verify_ground_truth_outcome(traj, gt)
        loop_penalty, _ = TrajectoryVerifier.check_looping_and_redundancy(traj)
        step_efficiency = 0.1 if (traj.success and traj.total_steps <= 6) else -0.1

        combined = outcome_score + loop_penalty + step_efficiency
        
        traj.reward_score = combined
        traj.reward_breakdown = {
            "outcome": outcome_score,
            "loop_penalty": loop_penalty,
            "efficiency": step_efficiency
        }
        total_rewards.append(combined)

    return total_rewards

