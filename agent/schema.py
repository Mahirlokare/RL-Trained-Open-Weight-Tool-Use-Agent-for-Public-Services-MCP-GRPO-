"""
Data schemas for Agent trajectories, tool calls, and interaction turns.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional

@dataclass
class ToolCall:
    name: str
    arguments: Dict[str, Any]
    raw_text: str = ""

@dataclass
class ToolResult:
    tool_name: str
    output: Dict[str, Any]
    is_error: bool = False

@dataclass
class Turn:
    role: str  # 'user', 'assistant', 'tool'
    content: str
    thought: Optional[str] = None
    tool_call: Optional[ToolCall] = None
    tool_result: Optional[ToolResult] = None

@dataclass
class AgentTrajectory:
    task_id: str
    user_prompt: str
    turns: List[Turn] = field(default_factory=list)
    final_answer: Optional[str] = None
    total_steps: int = 0
    success: bool = False
    reward_score: float = 0.0
    reward_breakdown: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
