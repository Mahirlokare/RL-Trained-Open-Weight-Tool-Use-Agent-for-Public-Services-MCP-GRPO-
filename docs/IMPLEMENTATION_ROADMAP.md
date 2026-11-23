# Civic AI: Implementation & Transformation Roadmap

**Project:** Civic AI — Universal Public Services Agent (MCP + GRPO)  
**Repository:** `https://github.com/Mahirlokare/RL-Trained-Open-Weight-Tool-Use-Agent-for-Public-Services-MCP-GRPO-`  
**Live Application:** `https://mahirlokare-civic-mcp-agent.hf.space/`  
**Audit Date:** 2026-11-23  
**Status:** In Progress (Full Transformation Lifecycle)

---

## 1. Issue Classification & Tracking Matrix

| ID | Category | Severity | Problem Description | Root Cause | Status | Verification Plan |
| :--- | :--- | :---: | :--- | :--- | :---: | :--- |
| **ISS-01** | ML/RL | **CRITICAL** | GRPO training metrics and logs are simulated. | Pre-baked synthetic curves in `verify_rl_policy.py`. | **DETECTED** | Replace with real PyTorch/TRL GRPO training pipeline; compute true forward/backward losses; output genuine convergence metrics. |
| **ISS-02** | ML/RL | **CRITICAL** | SFT training generates artificial loss values. | `train_sft.py` does not execute actual gradient updates on model weights. | **DETECTED** | Implement genuine Hugging Face `SFTTrainer` with LoRA config and actual optimizer steps. |
| **ISS-03** | Agent | **CRITICAL** | Reasoner is primarily a deterministic heuristic script, not a real model. | `agent/reasoner.py` uses keyword rules disguised as policy inference. | **DETECTED** | Implement `ModelProvider` abstraction for open-weight models (Qwen2.5/Llama-3); label rule-based mode explicitly as fallback. |
| **ISS-04** | Benchmark | **HIGH** | Benchmark baselines are scripted behaviors rather than empirical model runs. | `run_eval.py` used pre-determined success/failure counters. | **DETECTED** | Rebuild benchmark engine with real test prompts, schema verification, and mark unrun baselines as "NOT RUN". |
| **ISS-05** | Tools | **HIGH** | Appointment booking returns simulated success without real confirmation workflow. | Local in-memory dict without confirmation tokens or status tracking. | **DETECTED** | Implement stateful confirmation tokens (`CONFIRM-XXXX`), Kendra availability checks, and clear demo labeling. |
| **ISS-06** | Tools | **HIGH** | SMS sending simulates delivery without clear provider status. | Dummy response returning `delivered` unconditionally. | **DETECTED** | Implement real gateway adapter abstraction (Twilio/Webhook/Console), explicit citizen consent, and honest status. |
| **ISS-07** | MCP | **HIGH** | MCP tools implemented purely as local function calls rather than protocol architecture. | Monolithic functions bypassing MCP JSON-RPC schemas and standalone transports. | **DETECTED** | Refactor into independent MCP server modules with standard JSON-RPC 2.0 schemas, transports (stdio/HTTP), and validation. |
| **ISS-08** | Tools | **HIGH** | Eligibility checker assumes fake citizen defaults when info is missing. | Hardcoded fallback age (30), income (100k) in `verify_eligibility`. | **DETECTED** | Require progressive field collection; return `UNKNOWN_FIELDS_REQUIRED` when fields are omitted. |
| **ISS-09** | Privacy | **HIGH** | Application contains hardcoded personal information (fallback phone/names). | Sample scripts and UI defaults contain real-looking phone numbers. | **DETECTED** | Remove all personal defaults; sanitize forms and enforce user-supplied data only. |
| **ISS-10** | Security | **HIGH** | Overly permissive write permissions in RBAC engine. | Default sessions granted `write:appointments` and `write:sms` without verification. | **DETECTED** | Enforce strict least privilege; require citizen confirmation tokens before any state-altering tool execution. |
| **ISS-11** | Security | **MEDIUM** | Prompt injection detection relies solely on brittle regex matching. | `SecurityPolicyEngine` only checked basic string keywords. | **DETECTED** | Multi-layer defense: structural system boundaries, input taint scoring, schema enforcement, and output sanitization. |
| **ISS-12** | Security | **MEDIUM** | OCR checksum represented as document authenticity / fraud detection. | Verhoeff checksum labeled as "Fraud / Fake ID Detection". | **DETECTED** | Relabel accurately: "Mathematical Checksum Validation"; explicitly state OCR checksum does not replace official UIDAI authentication. |
| **ISS-13** | UI/UX | **MEDIUM** | Internal `<think>` reasoning tags exposed in chat interface. | Raw reasoning text prepended to chat responses. | **DETECTED** | Remove raw `<think>` content; expose only safe, structured, collapsible operational tool traces. |
| **ISS-14** | Data | **MEDIUM** | Scheme data hardcoded and lacks live provenance verification. | Static records in `SCHEMES_DB` without freshness timestamps or dynamic retrieval. | **DETECTED** | Implement provenance tracking, source ministry attributions, official portal links, and data freshness timestamps. |
| **ISS-15** | Docs | **HIGH** | Previously generated certificates claimed empirical verification that was simulated. | `rl_training_certificate.json` claimed 250 real GPU steps. | **DETECTED** | Revoke synthetic certificates; replace with honest research documentation and reproducible setup guides. |
| **ISS-16** | Frontend | **HIGH** | UI layout is a basic demo rather than a 12-page systems-grade application. | Single monolithic Gradio tab set without unified navigation or design system. | **DETECTED** | Build premium 12-page navigation shell with civic design system, status indicators, and responsive components. |
| **ISS-17** | DevOps | **CRITICAL** | Hugging Face Space & GitHub deployment sync and CI pipeline. | Discrepancies between local tests, GitHub Actions, and HF runtime. | **DETECTED** | Create automated GitHub Actions CI, complete test suite (unit/integration/security), and verify live deployment. |

---

## 2. Transformation Phases & Milestones

1. **Phase 1: Complete Repository Audit & Roadmap** *(Done)*
2. **Phase 2: High-End UI/UX Transformation** (12-section Civic AI shell, modern design tokens, safe operational traces)
3. **Phase 3: Real AI Agent Architecture** (Open-weight model abstraction, structured JSON tool parser, rule fallback mode)
4. **Phase 4: Real MCP Protocol Implementation** (JSON-RPC 2.0 schemas, stdio/HTTP server processes, tool validation)
5. **Phase 5: Real Public Service Integrations** (No fake defaults, stateful appointment confirmation, honest SMS gateway)
6. **Phase 6: Citizen Safety & Security** (Least-privilege RBAC, multi-stage injection defense, PII masking, honest OCR checks)
7. **Phase 7: Actual SFT Training Pipeline** (PyTorch / Transformers / TRL / PEFT pipeline with real loss computation)
8. **Phase 8: Actual GRPO Training Pipeline** (Group Relative Policy Optimization with rubric verifiers and actual loss calculation)
9. **Phase 9: Scientifically Honest Benchmark** (Empirical held-out evaluation, unrun baselines labeled "NOT RUN")
10. **Phase 10: Model Lab & Evaluation Dashboard** (Real experiment telemetry, configuration manager, diagnostic charts)
11. **Phase 11: Testing & Automated QA** (Comprehensive pytest suite across unit, integration, and security vectors)
12. **Phase 12: GitHub Cleanup & Live Hugging Face Deployment** (Clean commits, verified live deployment, documentation)
