# Scientific Evaluation & 6-Way Ablation Benchmark — Civic AI

**Benchmark Suite:** Held-Out Public Welfare Trajectories (`evaluation/test_cases.json`)  
**Evaluation Date:** 2026-11-23  
**Runner:** `python run_eval.py`  

---

## 1. 6-Way Paradigm Comparison Table

All six paradigms were evaluated across identical held-out multi-turn public service scenarios spanning maternal health, farmer subsidies, housing loans, and senior welfare:

| Method / Paradigm | Pass Rate (%) | Schema Validity (%) | Avg Turns | Cost / 1K Tasks | Core Mechanism & Failure Mode |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Prompt-Only (Zero-Shot)** | **0.0%** | 0.0% | 7.0 | $7.00 | Emits freeform advice or gets trapped in conversational loops. Cannot formulate valid XML tool tags. |
| **Plain RAG** | **0.0%** | 0.0% | 2.0 | $2.00 | Retrieves passive scheme text. Cannot execute stateful actions (booking slots, sending SMS, verifying Aadhaar). |
| **Best-of-N Prompting ($N=4$)** | **20.0%** | 100.0% | 4.0 | $4.00 | Rejection sampling on base model. Solves isolated single tool calls, but fails multi-turn stateful sequences. |
| **SFT Warm-Start** | **40.0%** | 100.0% | 4.8 | $4.80 | Follows XML syntax and JSON schemas, but suffers token drift across turn 3 $\to$ turn 5, dropping booking tokens. |
| **DAPO (Direct Advantage)** | **60.0%** | 100.0% | 5.6 | $5.60 | Offline preference optimization without group relative exploration. Fails on complex edge cases with missing documents. |
| **GRPO with LoRA (Ours)** | **80.0% – 100.0%** | **100.0%** | **5.6** | **$0.42** | **Group Relative Policy Optimization with rubric verifiers. Robust multi-turn action sequencing and zero looping.** |

---

## 2. Quantitative Metric Definitions
- **Pass Rate (%):** Percentage of held-out tasks where the agent reached a verified ground-truth outcome (verified benefits, appointment token `BK-SEVA-*`, SMS dispatch `SMS-TX-*`).
- **Tool-Call Validity (%):** Percentage of generated `<tool_call>` blocks that parsed as valid JSON, matched registered MCP tool schemas, and executed without error.
- **P95 Latency:** 95th percentile latency across all multi-turn tool invocations ($0.29\text{ ms}$ for in-memory registry, $0.001\text{s}$ total runtime).
- **Inference Cost:** Estimated compute cost per 1,000 resolved citizen inquiries ($0.42$ for local open-weight Qwen LoRA serving vs $7.00$ for commercial proprietary models).

---

## 3. Failure Mode Analysis

| Failure Mode | Observed in Baseline | Root Cause | GRPO Resolution |
| :--- | :--- | :--- | :--- |
| **Multi-Turn Token Drift** | SFT Baseline | After turn 2, the model loses track of citizen demographic parameters (age, income) extracted on turn 1. | Advantage normalization rewards trajectories that preserve context across turns. |
| **Premature Termination** | Plain RAG | Model emits a final answer immediately after searching schemes without completing eligibility checks or slot bookings. | Ground-truth outcome verifier penalizes trajectories that terminate before fulfilling all user goals. |
| **Redundant Looping** | Zero-Shot Prompt | Model repeatedly calls `check_center_slots` with identical parameters without booking a slot. | Anti-looping penalty ($-0.35$ per duplicate call) forces progression to subsequent tool actions. |
