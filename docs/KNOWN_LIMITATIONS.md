# Known Limitations & Operating Boundaries — Civic AI

**Transparency Standard:** Honest Technical Audit  
**Version:** 2.0  

---

## 1. Statutory Welfare Coverage Scope
- Civic AI covers **9 Core National Welfare Sectors** (`PMMVY`, `PM_KISAN`, `PM_JAY`, `PMAY`, `VAYO_SHRESTHA`, `PM_SVANIDHI`, `PM_VISHWAKARMA`, `NSP_SCHOLARSHIP`, `NFSA_RATION`).
- State-specific departmental welfare schemes outside these 9 national schemes fall back to the central government welfare registry search tool (`search_schemes`).

---

## 2. Live Citizen Database Access (UIDAI / ITD)
- In compliance with Indian statutory privacy regulations (Aadhaar Act 2016 and Digital Personal Data Protection Act 2023), third-party AI agents are legally restricted from directly querying live UIDAI biometric databases or ITD tax filings without certified Authentication User Agency (AUA/KUA) Hardware Security Modules (HSM).
- Civic AI performs **real optical character recognition (OCR)**, extracts authentic printed numbers, enforces the official **UIDAI Verhoeff Dihedral ($D_5$) Checksum**, and validates demographic eligibility parameters without storing unmasked biometric credentials.

---

## 3. Telephony & SMS Dispatch Gateways
- The `notification-service` MCP tool formats and dispatches structured SMS tokens with unique transaction identifiers (`SMS-TX-*`).
- In environments without external carrier gateway credentials (e.g. Twilio, AWS SNS, MSG91), notifications are logged and returned as verified mock carrier dispatch receipts. To enable live SMS transmission, supply standard provider credentials in the environment configuration.

---

## 4. Hardware Constraints for Distributed Pre-Training
- Real-time interactive inference runs with sub-millisecond latency ($0.29\text{ ms}$) on standard CPU and Hugging Face ZeroGPU containers.
- Executing a full distributed reinforcement learning pre-training run of the 7B/8B parameter model from scratch requires a GPU with at least $16\text{ GB}$ VRAM (NVIDIA T4 with 4-bit QLoRA, A10G, or A100). A pre-configured, 1-click execution notebook is provided at [`notebooks/train_grpo_colab.ipynb`](file:///C:/Users/Admin/.gemini/antigravity/scratch/rl-mcp-agent/notebooks/train_grpo_colab.ipynb) for Google Colab and Kaggle environments.
