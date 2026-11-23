# Model Card: Qwen-8B-GRPO-PublicServices

## Model Overview
- **Model Name:** Qwen-8B-GRPO-PublicServices (LoRA Adapter)
- **Base Architecture:** `Qwen/Qwen2.5-7B-Instruct` / `Qwen3-8B-Class`
- **Tuning Method:** Group Relative Policy Optimization (GRPO) with LoRA ($r=16, \alpha=32$)
- **Domain:** Citizen Welfare & Public Administration Assistance
- **Tool Protocol:** Model Context Protocol (MCP) JSON-RPC Specification
- **License:** MIT License

---

## Intended Use
- **Primary Use:** Decision support for citizens and frontline workers navigating government schemes (maternal support, farmer subsidies, elder care).
- **Tool Actions:** Verification of identity proofs (OCR), eligibility scoring, appointment booking at Seva Kendra centers, and SMS dispatch.
- **Out-of-Scope / Misuse:**
  - Generating legally binding statutory determinations without official human verification.
  - Applying outside authorized jurisdiction databases.
  - Processing financial transactions beyond informational verification.

---

## Training Factors & Hyperparameters
- **Group Size ($G$):** 4 candidate trajectories sampled per prompt for advantage estimation.
- **Advantage Normalization:** $A_i = \frac{R_i - \text{mean}(R)}{\text{std}(R)}$
- **Learning Rate:** $2 \times 10^{-5}$ with linear warmup
- **Hardware Requirement:** Single NVIDIA GPU (16GB VRAM, e.g. T4 or A100 via QLoRA 4-bit)
- **Reward Verifiers:**
  - XML & JSON Format Compliance: $+0.40$
  - MCP JSON Schema Parameter Match: $+0.30$
  - Task Goal Outcome: $+0.50$
  - Anti-Looping Penalty: $-0.35$
  - Hallucinated Reference Penalty: $-0.50$

---

## Ethical Considerations & Bias Analysis
- **Data Privacy:** All training trajectories are synthetically generated; zero real citizen identity or health records were ingested.
- **Language & Accessibility:** Designed to integrate with regional language frontends (Devanagari / Indic scripts) through standardized MCP translation boundaries.
- **Fairness Guarantee:** Hard mathematical eligibility criteria (age, income) prevent subjective discrimination across citizen demographics.
