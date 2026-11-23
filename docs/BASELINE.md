# Project Baseline Specification — Civic AI

**Date:** 2026-11-23  
**Target Environment:** Hugging Face Spaces (ZeroGPU / CPU fallback), Python 3.10+  
**Local Development OS:** Windows 11 (Python 3.13.2)  

---

## 1. Programming Languages & Frameworks
- **Primary Language:** Python 3.10+
- **Frontend / UI Framework:** Gradio (v6.0+ compatible, unpinned for Hugging Face official managed container)
- **Tool Protocol:** Model Context Protocol (MCP) JSON-RPC standard
- **Machine Learning / RL Stack:** PyTorch, Transformers, PEFT (LoRA), TRL (GRPO)
- **Serving Layer:** vLLM (OpenAI-compatible `/v1/chat/completions`)
- **Testing Framework:** pytest (v9.2+)

---

## 2. Project Entrypoints
- **Web Application Entrypoint:** `app.py` (`demo.launch(server_name="0.0.0.0", server_port=7860)`)
- **CLI Interactive Demo:** `demo.py` (`python demo.py`)
- **Benchmark & Ablation Runner:** `run_eval.py` (`python run_eval.py`)
- **MCP Server Audit Runner:** `test_mcp_servers.py` (`python test_mcp_servers.py`)
- **RL Training Verifier:** `training/verify_rl_policy.py` (`python training/verify_rl_policy.py`)
- **Technical PDF Generator:** `build_manual_pdf.py` (`python build_manual_pdf.py`)

---

## 3. Dependency Management
- **Python Packages:** `requirements.txt`
  - `fastapi>=0.110.0`
  - `pydantic>=2.6.0`
  - `pytesseract>=0.3.10`
  - `Pillow>=10.0.0`
- **Debian APT Packages:** `packages.txt`
  - `tesseract-ocr`
  - `tesseract-ocr-eng`
  - `libtesseract-dev`

---

## 4. Git Repositories & Remotes
- **Branch:** `main`
- **GitHub Remote (`origin`):** `https://github.com/Mahirlokare/RL-Trained-Open-Weight-Tool-Use-Agent-for-Public-Services-MCP-GRPO-.git`
- **Hugging Face Remote (`hf`):** `https://huggingface.co/spaces/mahirlokare/civic-mcp-agent`
- **Live URL:** `https://mahirlokare-civic-mcp-agent.hf.space`

---

## 5. Architectural Baseline
1. **Frontend:** 8 Gradio Tabs (Conversational Chatbot, Scenario Runner, Document OCR Scanner, Live MCP Console, Welfare Catalog, RL Verification, 6-Way Ablations, Security Red-Team).
2. **Reasoning Runtime:** `MCPAgentRuntime` managing multi-turn dialogue context, 6-turn iteration caps, and $1,200$-character tool result truncation.
3. **MCP Tool Servers:** 5 servers registering 7 tools across schemes, OCR, eligibility rules, appointment calendar, and SMS dispatch.
4. **Security Engine:** Regex-based taint tracking, least-privilege scope-based RBAC, and Verhoeff dihedral D5 checksum verification for Aadhaar documents.
5. **Reinforcement Learning:** GRPO training pipeline with rubric verifiers across syntax, schema, ground-truth outcome, anti-looping penalties, and KL divergence bounded exploration.
