# Initial Project Audit Report — Civic AI (RL-Trained MCP Agent)

**Date of Audit:** 2026-11-23  
**Auditor Roles:** Senior AI Engineer, Staff Software Architect, ML Researcher, MCP Specialist, Security Engineer, QA Automation Engineer  
**Repository:** `Mahirlokare/RL-Trained-Open-Weight-Tool-Use-Agent-for-Public-Services-MCP-GRPO-`  
**Live Application Target:** `https://mahirlokare-civic-mcp-agent.hf.space/`  

---

## 1. Executive Summary
This audit evaluated the complete codebase of the Civic AI project across backend services, Model Context Protocol (MCP) tool servers, multi-turn reasoning runtime, security defenses, reinforcement learning (GRPO) training pipeline, evaluation framework, frontend UI, and deployment configuration.

---

## 2. Issues Identified & Severity Classifications

### [CRITICAL] None Detected
The core application starts and functions without unhandled server crashes.

---

### [HIGH] Issue H-1: Missing Import in CLI Interactive Demo (`demo.py`)
- **File & Location:** `demo.py:12`
- **Problem:** `from run_eval import rl_trained_policy` fails with `ImportError`.
- **Why It Occurs:** `run_eval.py` defines `grpo_policy` and `dynamic_rl_agent_policy` but did not alias or export `rl_trained_policy`.
- **Impact:** Anyone running the terminal CLI demo `python demo.py` experiences an immediate startup crash.
- **Fix Applied/Planned:** Alias `rl_trained_policy = grpo_policy` in `run_eval.py` and import `dynamic_rl_agent_policy` directly in `demo.py`.
- **Verification Method:** Execute `python demo.py` and assert zero errors.

---

### [HIGH] Issue H-2: Non-Deterministic Idempotency Hash & Missing Argument Schema Validation in MCP Server
- **File & Location:** `mcp_servers/registry.py:67, 80`
- **Problem:**
  1. `idempotency_key = f"{name}:{hash(args_str)}"` uses Python's built-in `hash()`, which is salted with random seeds across process restarts (`PYTHONHASHSEED`), violating persistent idempotency.
  2. `call_tool` directly unpacks `**arguments` without validating against `inputSchema`, leading to unhandled `TypeError` exceptions if parameters are missing or typed incorrectly.
  3. No execution timeout wrapper exists for tool invocations.
- **Why It Occurs:** Prototype implementation relied on Python native hashing and duck-typing.
- **Impact:** Cache collisions or misses across restarts; parameter errors reported as opaque Python internal errors rather than standard JSON-RPC schema violations.
- **Fix Applied/Planned:**
  1. Replace `hash()` with `hashlib.sha256(args_str.encode()).hexdigest()`.
  2. Implement strict argument validation against `inputSchema` (required fields, expected types) returning structured validation error payloads.
  3. Introduce configurable tool execution timeouts with graceful timeout error responses.
- **Verification Method:** Unit test in `tests/test_mcp_servers.py` testing schema validation failures, timeout triggers, and SHA-256 idempotency reproducibility.

---

### [HIGH] Issue H-3: Stub Implementation in SFT Warm-Start Pipeline (`training/train_sft.py`)
- **File & Location:** `training/train_sft.py:18-24`
- **Problem:** Function `run_sft_warmstart` was a stub returning `{"status": "ready"}` without actual trajectory formatting, tokenizer mapping, or loss computation.
- **Why It Occurs:** Focus was initially placed on inference reasoners and GRPO reward logic.
- **Impact:** Cannot warm-start open-weight models from synthetic multi-turn data prior to GRPO RL exploration.
- **Fix Applied/Planned:** Implement complete SFT pipeline loading datasets from `training/data_generator.py`, formatting into conversation templates, configuring PEFT LoRA, and running training steps with checkpoint saving.
- **Verification Method:** Run `python -m pytest tests/test_training.py` and execute `python training/train_sft.py --epochs 1`.

---

### [HIGH] Issue H-4: Absence of Formal Automated Test Suite (`tests/` directory)
- **File & Location:** Root directory
- **Problem:** Tests were limited to manual root scripts (`test_mcp_servers.py`, `run_eval.py`) without a modular `tests/` directory running under standard `pytest`.
- **Why It Occurs:** Rapid iterative prototyping.
- **Impact:** No CI/CD regression testing, lacking automated unit, integration, end-to-end, and security tests.
- **Fix Applied/Planned:** Build comprehensive pytest suite:
  - `tests/test_schemas.py`
  - `tests/test_mcp_servers.py`
  - `tests/test_reasoner.py`
  - `tests/test_security.py`
  - `tests/test_rewards.py`
  - `tests/test_evaluation.py`
- **Verification Method:** Execute `python -m pytest tests/ -v`.

---

### [MEDIUM] Issue M-1: Structured Logging & Standardized Error Categories
- **File & Location:** `app.py`, `agent/runtime.py`
- **Problem:** Logs use direct `print()` statements and string formatting rather than Python's standard `logging` library with structured log levels (`INFO`, `WARNING`, `ERROR`, `AUDIT`).
- **Why It Occurs:** Convenience in initial script development.
- **Impact:** Hard to trace production issues in cloud containers; error responses do not classify errors into formal taxonomy (Validation, Authentication, RateLimit, Provider, Timeout, Internal).
- **Fix Applied/Planned:** Implement centralized `logging` configuration and structured error classification classes.
- **Verification Method:** Inspect server logs for structured formatting and test intentional error conditions.

---

### [MEDIUM] Issue M-2: File Upload Path Traversal & File Size Guardrails
- **File & Location:** `app.py`, `mcp_servers/services.py`
- **Problem:** File references in document scanning did not sanitize paths against directory traversal (`../`) or enforce a maximum upload file size (e.g., 10MB ceiling).
- **Why It Occurs:** File inputs were trusted from local Gradio temporary directories.
- **Impact:** Potential path traversal vulnerability if arbitrary paths are supplied by an attacker.
- **Fix Applied/Planned:** Implement `SecurityPolicyEngine.sanitize_file_path()` enforcing path boundaries and maximum file size verification.
- **Verification Method:** Security test with path traversal payload `../../etc/passwd` asserting immediate rejection.

---

### [LOW] Issue L-1: Data Provenance & Source Attribution Metadata
- **File & Location:** `mcp_servers/services.py`
- **Problem:** Records in `SCHEMES_DB` contain helpline and portal URLs, but lacked explicit provenance tags distinguishing `REAL DATA`, `CACHED DATA`, and `DEMO SIMULATED DATA`.
- **Why It Occurs:** Omission in database metadata schema.
- **Impact:** Evaluators cannot programmatically distinguish official verified portal data from demo simulation fixtures.
- **Fix Applied/Planned:** Add `provenance_type: "OFFICIAL_GOVERNMENT_PORTAL"` and `last_audited_timestamp` to all 9 welfare sector records.
- **Verification Method:** Verify schema contains provenance attributes in unit tests.

---

## 3. Summary of Planned Remediation

1. Repair `demo.py` and `run_eval.py` exports.
2. Upgrade `mcp_servers/registry.py` with SHA-256 idempotency, argument validation, and timeouts.
3. Finish `training/train_sft.py` with reproducible PEFT LoRA training workflow.
4. Add security guardrails: path traversal protection, file size bounds, structured error categories.
5. Build complete `tests/` directory and pass all tests via `pytest`.
6. Generate complete documentation package in `docs/`.
7. Push changes to GitHub and Hugging Face Spaces and verify live deployment.
