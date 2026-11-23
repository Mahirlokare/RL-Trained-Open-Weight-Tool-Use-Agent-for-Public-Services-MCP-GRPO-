# Security Architecture & Threat Defense Specification — Civic AI

**Document Version:** 1.0  
**Classification:** Public Services AI Agent Security Standard  
**Compliance Target:** NIST AI RMF, OWASP Top 10 for LLMs, Goal Structuring Notation (GSN) Safety Case  

---

## 1. Threat Modeling (STRIDE Framework)

| STRIDE Category | Threat Description in AI Agent Context | Mitigation in Civic AI Architecture | Verification Status |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Citizen impersonation or submitting synthetic/fake Aadhaar identity cards. | Real document OCR + **UIDAI Verhoeff Dihedral ($D_5$) Checksum Validation**. Fake UIDs rejected at the tool layer. | **VERIFIED** ✅ |
| **Tampering** | Indirect prompt injection within uploaded document files or tool payloads attempting to override system constraints. | Proactive **Taint Tracking & Regex Interception** before tool execution (`SecurityPolicyEngine`). | **VERIFIED** ✅ |
| **Repudiation** | Denying an appointment booking or claiming unauthorized SMS notifications were dispatched. | Deterministic **SHA-256 Idempotency Keys** and timestamped dispatch records with persistent tokens. | **VERIFIED** ✅ |
| **Information Disclosure** | Leakage of full 12-digit Aadhaar numbers, private citizen phone numbers, or model system prompts. | Strict **Identity Masking** (`XXXX-XXXX-1234`), sensitive token redaction, and internal thought segregation. | **VERIFIED** ✅ |
| **Denial of Service** | Agent trapped in recursive infinite tool-calling loops or processing unbounded file uploads. | Hard runtime ceiling of **6 iterations**, $1,200$-character payload truncation, and $10\text{ MB}$ file size ceiling. | **VERIFIED** ✅ |
| **Elevation of Privilege** | Citizen prompting the agent to grant statutory welfare benefits without required supporting proofs. | **Scope-Based Role-Based Access Control (RBAC)** enforced by backend code, bypassing prompt-only vulnerabilities. | **VERIFIED** ✅ |

---

## 2. Least-Privilege Scope Matrix

The Model Context Protocol (MCP) server enforces scope requirements at the handler level:

| Tool Name | Server | Required Scope | Authorized Roles | Action Type |
| :--- | :--- | :--- | :--- | :--- |
| `search_schemes` | `scheme-service` | `read:schemes` | `public`, `citizen`, `official` | Read-only |
| `get_scheme_details` | `scheme-service` | `read:schemes` | `public`, `citizen`, `official` | Read-only |
| `scan_document_ocr` | `ocr-service` | `read:ocr` | `citizen`, `official` | Read-only (Verified) |
| `verify_eligibility` | `eligibility-service` | `verify:eligibility` | `citizen`, `official` | Mathematical Verification |
| `check_center_slots` | `appointment-service` | `read:appointments` | `citizen`, `official` | Read-only |
| `book_appointment` | `appointment-service` | `write:appointments` | `citizen`, `official` | Stateful Mutation (Idempotent) |
| `send_confirmation_sms` | `notification-service` | `write:sms` | `citizen`, `official` | Notification Dispatch |

---

## 3. Cryptographic Idempotency Architecture

Stateful write actions (e.g. appointment reservation and SMS dispatch) compute a deterministic SHA-256 digest:

$$\text{Key} = \text{tool\_name} : \text{SHA-256}(\text{JSON}(\text{arguments}))$$

- If an identical booking request arrives within the cache window, the backend serves the cached transaction token without double-booking or sending duplicate SMS messages.
- Unlike Python's non-deterministic built-in `hash()`, SHA-256 remains 100% reproducible across process restarts and distributed worker nodes.

---

## 4. Document File Upload & Path Traversal Protections
- Paths containing directory traversal sequences (`../`, `..\`, `/etc`, `C:\Windows`) are intercepted and quarantined by `SecurityPolicyEngine.sanitize_file_path()`.
- File uploads are validated against an upper bound of $10\text{ MB}$ to prevent buffer exhaustion and memory exhaustion attacks.
- Supported file types are restricted strictly to `.png`, `.jpg`, `.jpeg`, and `.pdf`.

---

## 5. Defense Against Prompt Injection & Jailbreaks
Any input matching known injection signatures (such as `"ignore previous instructions"`, `"bypass eligibility"`, `"system prompt"`, `"grant all benefits"`) is quarantined immediately. The system outputs a clear security refusal notice without executing any tool calls:

```text
Status: 🛡️ Security Alert: Malicious Input Quarantined
The system refused to bypass verification rules or grant unauthorized privileges.
```
