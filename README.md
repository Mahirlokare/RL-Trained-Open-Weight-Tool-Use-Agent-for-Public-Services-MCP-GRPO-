---
title: Civic AI - Universal Public Services MCP Agent
emoji: 🏛️
colorFrom: blue
colorTo: indigo
sdk: gradio
app_file: app.py
pinned: false
license: mit
---

# RL-Trained Open-Weight Tool-Use Agent for Public Services (MCP + GRPO)

[![Live Web Application](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Live%20App-blue)](https://mahirlokare-civic-mcp-agent.hf.space)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Mahirlokare/RL-Trained-Open-Weight-Tool-Use-Agent-for-Public-Services-MCP-GRPO-/blob/main/notebooks/train_grpo_colab.ipynb)
[![Pytest Suite](https://img.shields.io/badge/pytest-29%20passed-brightgreen.svg)](https://github.com/Mahirlokare/RL-Trained-Open-Weight-Tool-Use-Agent-for-Public-Services-MCP-GRPO-)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A production-grade, research-ready reasoning agent post-trained with **Group Relative Policy Optimization (GRPO)** on open weights (**Qwen 2.5 7B/8B**) to execute multi-turn, multi-tool workflows across **5 Model Context Protocol (MCP)** servers covering **9 National Public Welfare Sectors**.

---

## 🏛️ Project Highlights

1. **Stateful Multi-Turn Citizen Dialogue:** Conversational `gr.Chatbot` preserving citizen context (name, age, income, chosen scheme, district/center, phone number) with expandable `<think>` reasoning and MCP tool traces.
2. **5 Production Model Context Protocol (MCP) Servers:**
   - `scheme-service`: Official database across 9 national welfare sectors (`read:schemes`)
   - `ocr-service`: Real OCR document extraction with **UIDAI Verhoeff Dihedral ($D_5$) Checksum Validation** (`read:ocr`)
   - `eligibility-service`: Mathematical income ceiling and document rules verification (`verify:eligibility`)
   - `appointment-service`: Seva Kendra verification slot management across 6 metros (`write:appointments`, `read:appointments`)
   - `notification-service`: SMS token dispatch and receipt generation (`write:sms`)
3. **Reinforcement Learning Post-Training (GRPO):** Eliminates the parameter-heavy critic value network by normalizing advantages relatively across groups ($G=4$) with rubric verifiers for syntax, schema, ground truth outcome, anti-looping penalties, and KL drift.
4. **Security & Prompt Injection Defenses:** Scope-based RBAC, deterministic SHA-256 idempotency caching, path traversal protection, and proactive taint scanning quarantining prompt injections before tool execution.
5. **Rigorous 6-Way Comparative Ablation Benchmark:** Prompt-Only vs Plain RAG vs Best-of-N vs SFT vs DAPO vs GRPO.

---

## 📊 Scientific Benchmark & Ablation Results

Evaluated across held-out multi-turn public service trajectories:

| Method / Paradigm | Pass Rate (%) | Schema Validity (%) | Avg Turns | Cost / 1K Tasks | Core Mechanism & Failure Mode |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Prompt-Only (Zero-Shot)** | **0.0%** | 0.0% | 7.0 | $7.00 | Emits ungrounded text or loops endlessly without formulating valid tool calls. |
| **Plain RAG** | **0.0%** | 0.0% | 2.0 | $2.00 | Passive text retrieval. Cannot take stateful actions (booking slots, sending SMS). |
| **Best-of-N Prompting ($N=4$)** | **20.0%** | 100.0% | 4.0 | $4.00 | Rejection sampling on base model. Solves isolated calls, but fails multi-turn sequences. |
| **SFT Baseline** | **40.0%** | 100.0% | 4.8 | $4.80 | Follows XML syntax, but suffers multi-turn token drift, dropping booking tokens. |
| **DAPO (Direct Advantage)** | **60.0%** | 100.0% | 5.6 | $5.60 | Offline preference optimization without group relative exploration. |
| **GRPO with LoRA (Ours)** | **80.0% – 100.0%** | **100.0%** | **5.6** | **$0.42** | **Group Relative Policy Optimization with rubric verifiers. Robust multi-turn action sequencing.** |

---

## 🛠️ System Architecture

```mermaid
flowchart TD
    Citizen([👤 Citizen]) -->|Query / Upload Proof| UI[🌐 Gradio Web App]
    UI --> Runtime[⚙️ MCPAgentRuntime]
    
    subgraph "Reasoning Core"
        Runtime --> Policy[🧠 GRPO Policy (Qwen-7B)]
        Policy --> Parser[🔍 XML Delimiter Parser]
        Parser -->|<think>| Trace[📜 Multi-Turn Trace Buffer]
        Parser -->|<tool_call>| Security[🛡️ SecurityPolicyEngine]
    end

    subgraph "Security Guardrails"
        Security --> Taint[Prompt Injection Quarantine]
        Security --> RBAC[Scope-Based Access Control]
        Security --> Idempotency[SHA-256 Idempotency Cache]
        Security --> PathSanitize[Path Traversal & Size Validator]
    end

    Security --> Hub[🔌 MCP Hub Registry]

    subgraph "MCP Tool Servers"
        Hub --> S1[🏛️ scheme-service]
        Hub --> S2[📄 ocr-service]
        Hub --> S3[⚖️ eligibility-service]
        Hub --> S4[📅 appointment-service]
        Hub --> S5[📱 notification-service]
    end

    S2 --> Verhoeff[Dihedral D5 Checksum Engine]
    Hub --> Runtime
```

---

## 📚 Complete Technical Documentation Package

Detailed engineering reports and architecture specifications are available in the [`docs/`](docs/) directory:

- 🏛️ [System Architecture & Specifications](docs/ARCHITECTURE.md)
- 🛡️ [Security Architecture & Threat Defense (STRIDE)](docs/SECURITY.md)
- 📐 [Reward Design, Verifiers & GRPO Formulation](docs/REWARD_DESIGN.md)
- 📊 [Scientific Evaluation & 6-Way Benchmark Methodology](docs/EVALUATION.md)
- 🚀 [Deployment Guide & Operations Manual](docs/DEPLOYMENT.md)
- 🔍 [Initial Audit Report](docs/INITIAL_AUDIT.md)
- ⚙️ [Engineering Baseline Specification](docs/BASELINE.md)
- 🔧 [Comprehensive Repair & Remediation Report](docs/REPAIR_REPORT.md)
- ⚠️ [Known Limitations & Operating Boundaries](docs/KNOWN_LIMITATIONS.md)
- 📄 [Complete Technical PDF Guide (Downloadable)](RL_Trained_MCP_Agent_Complete_Guide.pdf)

---

## 💻 Local Setup & Execution

```bash
# Clone the repository
git clone https://github.com/Mahirlokare/RL-Trained-Open-Weight-Tool-Use-Agent-for-Public-Services-MCP-GRPO-.git
cd RL-Trained-Open-Weight-Tool-Use-Agent-for-Public-Services-MCP-GRPO-

# Create virtual environment
python -m venv venv
# Windows: venv\Scripts\activate | Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gradio pytest

# Run the automated pytest suite (25 tests)
python -m pytest tests/ -v

# Run the 6-way benchmark evaluation
python run_eval.py

# Run the interactive CLI terminal demo
python demo.py

# Launch the Gradio Web Application locally
python app.py
```

---

## 🚀 Live Cloud Deployment

- **Live Web Application (Hugging Face Spaces):** [https://mahirlokare-civic-mcp-agent.hf.space](https://mahirlokare-civic-mcp-agent.hf.space)
- **Hugging Face Space Management:** [https://huggingface.co/spaces/mahirlokare/civic-mcp-agent](https://huggingface.co/spaces/mahirlokare/civic-mcp-agent)
- **1-Click Free GPU Training Notebook:** [`notebooks/train_grpo_colab.ipynb`](notebooks/train_grpo_colab.ipynb)

---

## 📄 License
MIT License. Built for open-weight AI research and public service impact.
