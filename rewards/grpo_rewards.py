"""
TRL / GRPO compatible reward functions.
GRPO evaluates a group of generations sampled from the current policy,
normalizing rewards across the group to compute policy advantages.
"""
from typing import List, Dict, Any, Optional
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

def tool_execution_reward_func(trajectories: List[AgentTrajectory], **kwargs) -> List[float]:
    """Rewards non-error tool executions and penalizes error status."""
    rewards = []
    for traj in trajectories:
        score = 0.0
        tool_turns = [turn for turn in traj.turns if turn.tool_result]
        if not tool_turns:
            # Neutral if no tool needed or penalty if stuck
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
        # Base outcome score
        outcome_score, report = TrajectoryVerifier.verify_ground_truth_outcome(traj, gt)
        
        # Repetition penalty
        loop_penalty, _ = TrajectoryVerifier.check_looping_and_redundancy(traj)
        
        # Step efficiency bonus (penalize wandering)
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
