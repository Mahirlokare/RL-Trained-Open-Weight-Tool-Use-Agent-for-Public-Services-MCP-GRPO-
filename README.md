# RL-Trained Open-Weight Tool-Use Agent for Public Services (MCP + GRPO)

Production-grade research repository and vertical slice demonstrating post-training of open-weight LLMs (Qwen 4B/8B class) with Group Relative Policy Optimization (GRPO) to execute multi-turn, multi-tool workflows across Model Context Protocol (MCP) servers.

## Architecture Overview

```mermaid
flowchart TD
    User["Citizen / Frontline Worker Request"] --> Agent["Open-Weight LLM Agent (Qwen-8B)"]
    Agent --> MCPBridge["MCP Client / Tool Router"]
    
    subgraph "MCP Tool Layer (Standard Protocols)"
        MCPBridge --> S1["Scheme DB Server (Search & Criteria)"]
        MCPBridge --> S2["Document Verifier (OCR & Eligibility)"]
        MCPBridge --> S3["Appointment Booking Server"]
        MCPBridge --> S4["SMS / Notification Dispatch"]
    end
    
    subgraph "Post-Training Loop (GRPO)"
        Train["Trajectory Generator"] --> RL["GRPO Policy Optimization"]
        RL --> V1["Format & Schema Verifier (+0.2)"]
        RL --> V2["Tool Call Execution Verifier (+0.3)"]
        RL --> V3["Task Goal Outcome Evaluator (+0.5)"]
        RL --> V4["Loop & Redundancy Penalty (-0.4)"]
    end
```

## Structure
- `mcp_servers/`: FastMCP-compatible server definitions for public service operations.
- `agent/`: Agent execution engine, prompt templates, and schema parsing for tool calls.
- `rewards/`: Deterministic and rubric-based reward functions designed for GRPO.
- `training/`: Synthetic trajectory generator, SFT warm-start, and TRL/Unsloth GRPO scripts.
- `evaluation/`: Held-out benchmark suite testing pass rates, tool validity, and cost.
- `demo.py`: Interactive runner to demonstrate agent interactions.
