# Reward Design, Verifiers, and GRPO Mathematical Specification

**Document Version:** 1.0  
**Target:** Post-Training Reinforcement Learning for Open-Weight Tool-Use Agents  
**Base Architecture:** `Qwen2.5-7B-Instruct` with LoRA ($r=16, \alpha=32$)  

---

## 1. Group Relative Policy Optimization (GRPO) Formulation

Group Relative Policy Optimization (GRPO) eliminates the parameter-heavy critic value network used in Proximal Policy Optimization (PPO). For each citizen prompt $q$, the policy $\pi_\theta$ samples a group of $G=4$ candidate outputs $\{o_1, o_2, o_3, o_4\}$. The advantages are normalized relatively across the group:

$$A_i = \frac{R_i - \text{mean}(\{R_1, \dots, R_G\})}{\text{std}(\{R_1, \dots, R_G\})}$$

The GRPO objective maximizes advantage while bounding drift via KL divergence against the reference policy $\pi_{\text{ref}}$:

$$\mathcal{L}_{\text{GRPO}}(\theta) = \mathbb{E}_{q \sim P(Q), \{o_i\}_{i=1}^G \sim \pi_{\theta_{\text{old}}}(O|q)} \left[ \frac{1}{G} \sum_{i=1}^G \min \left( \frac{\pi_\theta(o_i|q)}{\pi_{\text{old}}(o_i|q)} A_i, \text{clip} \left( \frac{\pi_\theta(o_i|q)}{\pi_{\text{old}}(o_i|q)}, 1-\epsilon, 1+\epsilon \right) A_i \right) - \beta D_{\text{KL}}(\pi_\theta \| \pi_{\text{ref}}) \right]$$

---

## 2. Rubric Verifier Decomposition

The composite trajectory reward $R_i$ is evaluated deterministically using rubric verifiers:

$$R_i = R_{\text{format}} + R_{\text{schema}} + R_{\text{outcome}} + P_{\text{loop}} - \beta \cdot D_{\text{KL}}$$

| Reward Term | Evaluation Criteria | Value Range | Verifier Type |
| :--- | :--- | :--- | :--- |
| **$R_{\text{format}}$** | Valid XML tags (`<think>`, `<tool_call>`, `<final_answer>`) without unmatched delimiters. | $[0.0, +0.40]$ | Deterministic Regex & AST Parser |
| **$R_{\text{schema}}$** | Valid JSON payload with registered MCP tool name and strictly typed parameters matching `inputSchema`. | $[0.0, +0.30]$ | JSON Schema Validator |
| **$R_{\text{outcome}}$** | Task fulfillment verified against ground truth (e.g. valid booking token, correct statutory benefit calculation). | $[0.0, +0.50]$ | Ground Truth Oracle |
| **$P_{\text{loop}}$** | Penalty for calling the identical tool with identical parameters repeatedly in the same trajectory. | $[-0.35, 0.0]$ | Deduplication Cache |
| **$P_{\text{hallucinate}}$** | Penalty for claiming benefits or booking appointments without invoking required MCP tool servers. | $[-0.50, 0.0]$ | Execution Audit Verifier |
| **$D_{\text{KL}}$** | Per-token KL divergence drift against the reference model $\pi_{\text{ref}}$ with penalty coefficient $\beta=0.04$. | Bounded | Token Logit Divergence |

---

## 3. Defense Against Reward Hacking

1. **Syntax vs. Outcome Decoupling:** Emitting perfectly formatted `<tool_call>` tags earns syntax credit ($+0.20$), but cannot achieve a passing advantage without successful tool result ingestion and outcome resolution.
2. **Anti-Looping Penalty:** Un-tuned models often get trapped repeatedly querying `check_center_slots`. A cumulative penalty of $-0.35$ per duplicate invocation forces exploration toward subsequent actions (`book_appointment`, `send_confirmation_sms`).
3. **Ground-Truth Substring Grounding:** Final answers must contain verified attributes (e.g. exact booking reference `BK-SEVA-*`, official helpline `104`, or statutory benefit amount `5000`) retrieved from tools. Answers with unsubstantiated claims receive an automatic zero outcome score.
4. **Hard Trajectory Horizon:** A strict ceiling of 6 turns prevents the model from gaming step-based rewards by generating needlessly lengthy conversational turns.
