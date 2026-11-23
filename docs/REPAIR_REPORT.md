# Civic AI Engineering Changelog & Hardening Record

**Engineering Review Cycle:** November 2026  
**Technical Lead:** Mahir Lokare  

---

## 1. Summary of Applied Engineering Enhancements

| ID | Component / File | Issue Description | Engineering Fix Applied | Verification Method |
| :---: | :--- | :--- | :--- | :--- |
| **FIX-01** | `demo.py` & `run_eval.py` | `ImportError: cannot import name 'rl_trained_policy' from 'run_eval'` | Aliased `rl_trained_policy = grpo_policy` in `run_eval.py` and exported cleanly. | Executed `python demo.py`; completed 8-turn run with 0 errors. |
| **FIX-02** | `mcp_servers/registry.py` | Non-deterministic idempotency key (`hash(args_str)`) vulnerable to process restart variation. | Upgraded to cryptographic `hashlib.sha256(args_str.encode()).hexdigest()`. | Tested duplicate write call; verified identical replay token. |
| **FIX-03** | `mcp_servers/registry.py` | Missing schema argument validation causing unhandled `TypeError` exceptions on missing/malformed arguments. | Implemented strict `validate_arguments` checking required fields and types against `inputSchema`. | Pytest unit tests in `tests/test_mcp_servers.py` (missing & invalid type). |
| **FIX-04** | `mcp_servers/registry.py` | No timeout enforcement on tool execution handlers. | Implemented `ThreadPoolExecutor` timeout wrapper with configurable limit ($10.0\text{s}$) returning standard JSON-RPC timeout errors. | Verified timeout protection and latency logging. |
| **FIX-05** | `mcp_servers/security.py` | Potential directory traversal (`../`) and unbounded file upload size risks. | Implemented `sanitize_file_path()` checking for traversal patterns and enforcing a $10\text{ MB}$ file size ceiling. | Pytest test `test_path_traversal_sanitization` passed on `../../etc/passwd`. |
| **FIX-06** | `mcp_servers/services.py` | Mock OCR returned hardcoded `XXXX-XXXX-8921` and approved fake IDs without validation. | Integrated real `pytesseract` / binary text extraction, extracted the user's **exact** uploaded numbers, and implemented the official **UIDAI Verhoeff Dihedral ($D_5$) Checksum**. | Tested fake UID `1234 5678 9012` $\to$ returned `REJECTED: Fraud / Fake Identity Proof Detected` with exact `XXXX-XXXX-9012`. |
| **FIX-07** | `agent/reasoner.py` | Agent reasoner lacked multi-turn dialogue memory and stalled on conversational queries. | Rebuilt `dynamic_rl_agent_policy` as a stateful entity extractor tracking name, age, income, district, and scheme across turns; added natural greetings. | Tested interactive chat turns and greeting inputs live. |
| **FIX-08** | `training/train_sft.py` | SFT script was an empty stub returning `{"status": "ready"}`. | Implemented full SFT pipeline generating 50 synthetic multi-turn trajectories, formatting conversation templates, and configuring LoRA checkpoints. | Executed `python training/train_sft.py`; produced dataset and metrics. |
| **FIX-09** | `app.py` | Chatbot component used unsupported `show_copy_button=True` causing container crash. | Removed incompatible argument while retaining full interactive conversational capabilities. | Live container startup succeeded (`Running on Zero`). |
| **FIX-10** | `tests/` Directory | Complete absence of automated pytest suite. | Built modular test suite: `test_schemas_and_parser.py`, `test_mcp_servers.py`, `test_security.py`, `test_rewards.py`, `test_e2e_workflows.py`. | Ran `python -m pytest tests/ -v` $\to$ **25 passed in 0.25s**. |
