# Civic AI: System Architecture & Operational Workflow

This document provides a comprehensive technical blueprint of the **Civic AI** system architecture, component boundaries, and end-to-end operational workflows.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph UI_Layer ["1. Presentation & Citizen Interaction Layer"]
        User["Citizen / Administrative Official"]
        BrowserUI["Web Application (13 Dedicated Modules)\n• AI Assistant • Scheme Explorer • Eligibility Checker\n• Document OCR • Appointments • Training Center"]
        Lang["Bilingual Engine\n(English & Hindi)"]
    end

    subgraph Security_Gateway ["2. Security, Safety & Gateway Layer"]
        Sanitizer["Input Sanitizer & Injection Guard"]
        PII["PII Masking & Privacy Anonymizer"]
        RBAC["Role-Based Access Control (RBAC)\n[Citizen vs. Official]"]
        TokenGen["Parameter-Bound Token Engine\n(SHA-256 Digest • 10-min TTL)"]
    end

    subgraph AI_Engine ["3. AI & Reasoning Engine (Dual-Mode)"]
        Tokenizer["Turn Context & Truncation Manager\n(Max 6 turns • Loop prevention)"]
        Reasoner{"Reasoning Engine"}
        HF_Model["Open-Weight LLM\n(Qwen2.5-7B-Instruct / Llama-3.1-8B)"]
        GRPO_Policy["GRPO Policy Optimization\n(Group-Relative Advantage • G=4)"]
        Fallback["Transparent Fallback Policy\n(Deterministic Rules)"]
    end

    subgraph MCP_Layer ["4. Model Context Protocol (MCP) Hub"]
        MCP_Client["MCP Host / Client Runtime\n(JSON-RPC 2.0 Protocol)"]
        Registry["Tool Registry & Scope Validator\n(read:schemes • read:documents • write:appointments)"]
    end

    subgraph MCP_Servers ["5. Independent MCP Service Servers"]
        S_Scheme["scheme-service\n• search_schemes\n• get_scheme_details"]
        S_Elig["eligibility-service\n• verify_eligibility"]
        S_Doc["ocr-service\n• inspect_document"]
        S_Appt["appointment-service\n• check_availability\n• request_hold\n• book_appointment (Protected)"]
        S_Notif["notification-service\n• send_notification (Protected)"]
    end

    subgraph External_State ["6. Live Public Infrastructure & Data"]
        GovRegistry[("Official Gazette & Portals\nPM-KISAN • Ayushman Bharat • PMAY")]
        ApptDB[("Appointment State Store\nCenter Slots • Held Tokens")]
        AuditDB[("Tamper-Evident Audit Logs\nSecurity & Telemetry")]
    end

    User -->|Voice / Text / Document| BrowserUI
    BrowserUI <--> Lang
    BrowserUI --> Sanitizer
    Sanitizer --> PII --> RBAC
    RBAC --> Tokenizer
    Tokenizer --> Reasoner

    Reasoner -->|Remote API| HF_Model
    Reasoner -->|RL Checkpoint| GRPO_Policy
    Reasoner -->|Offline Default| Fallback

    Reasoner -->|Structured XML Tool Call| MCP_Client
    MCP_Client --> Registry
    Registry -->|Scope: read:*| S_Scheme & S_Elig & S_Doc
    Registry -->|Scope: write:* with Token| TokenGen
    TokenGen --> S_Appt & S_Notif

    S_Scheme <--> GovRegistry
    S_Appt <--> ApptDB
    TokenGen & MCP_Client -.-> AuditDB

    MCP_Client -->|Structured Tool Result| Reasoner
    Reasoner -->|Sanitized Final Answer| BrowserUI
    BrowserUI --> User
```

---

## 2. End-to-End Operational Workflow: Citizen Inquiry & Booking

```mermaid
sequenceDiagram
    autonumber
    actor Citizen
    participant UI as Gradio Frontend (Citizen UI)
    participant Sec as Security & RBAC Gateway
    participant AI as GRPO Reasoner (Agent)
    participant MCP as MCP Registry & Host
    participant SchemeSvc as Scheme & Eligibility Server
    participant ApptSvc as Appointment Server (Protected)
    participant Ext as Official State / DB

    Citizen->>UI: "I am a small farmer from Maharashtra. Am I eligible for PM-KISAN, and can I book a verification slot?"
    UI->>Sec: Sanitize input & verify role ('citizen')
    Sec->>AI: Forward prompt + session history (Turn 1)
    
    Note over AI: Reasoner generates structured tool call<br/>Grounded via GRPO policy
    AI->>MCP: Call tool: search_schemes(keyword="farmer", state="Maharashtra")
    MCP->>SchemeSvc: Execute search_schemes
    SchemeSvc->>Ext: Query verified scheme database
    Ext-->>SchemeSvc: Return [PM_KISAN, PMMVY, etc.]
    SchemeSvc-->>MCP: Formatted scheme criteria
    MCP-->>AI: Tool Response (Age >= 18, Land record needed, Rs 6000/yr)

    Note over AI: Evaluate eligibility criteria<br/>Formulates follow-up & availability check
    AI->>MCP: Call tool: check_availability(center_id="CSC-MAH-01", date="2026-11-26")
    MCP->>ApptSvc: Execute read-only slot check
    ApptSvc-->>MCP: Available slots: ["10:30 AM", "02:00 PM"]
    MCP-->>AI: Tool Response

    AI-->>UI: "You qualify for PM-KISAN (Rs 6,000/yr). Available slots on Nov 26 are 10:30 AM and 02:00 PM. Would you like to confirm the 10:30 AM slot?"
    UI-->>Citizen: Displays plain-language advice + slot options (Tool traces collapsed)

    Citizen->>UI: "Yes, please confirm the 10:30 AM slot for Ramesh Patil."
    UI->>Sec: Request appointment hold
    Sec->>ApptSvc: request_appointment_hold("CSC-MAH-01", "2026-11-26 10:30", "Ramesh Patil")
    ApptSvc->>Sec: Generate Token: CONFIRM-A8F391 (SHA-256 digest bound, 10m TTL)
    
    Note over Sec: Strict Fail-Closed Check:<br/>Token is cryptographically bound to parameters
    Sec->>ApptSvc: book_appointment(token="CONFIRM-A8F391", params)
    ApptSvc->>Ext: Atomically commit booking & burn token
    Ext-->>ApptSvc: Booking ID #APPT-849102 confirmed
    ApptSvc-->>MCP: Success payload
    MCP-->>AI: Synthesize final confirmation
    AI-->>UI: "Appointment confirmed at CSC Pune Center for Nov 26, 10:30 AM. Booking ID: #APPT-849102."
    UI-->>Citizen: Green confirmation banner + SMS notification dispatched
```

---

## 3. Layer-by-Layer Architectural Breakdown

### Layer 1: Presentation & Citizen Interface
* **13 Functional Tabs:** Provides complete coverage from citizen interactions to deep ML telemetry and evaluation.
* **Bilingual Translation Support:** Native Hindi and English support with graceful conversational clarification when citizen inputs are ambiguous.
* **Clean Trace Separation:** Sanitizes raw internal `<think>` tokens from citizen view while exposing operational tool traces in inspectable dropdown accordions.

### Layer 2: Security & Governance Gateway
* **Fail-Closed Authorization:** Write actions (`write:appointments`, `write:notifications`) are physically blocked unless authenticated with valid permissions and cryptographic tokens.
* **Parameter-Bound Confirmation Tokens:** Generates `CONFIRM-XXXXXX` tokens tied via SHA-256 digest to specific parameters (citizen name, center, slot time). Tampering with any parameter immediately invalidates the token.
* **Atomic Token Consumption:** Tokens expire in 10 minutes and cannot be reused, preventing replay attacks.
* **Prompt Injection & PII Masking:** Regex and heuristic filters strip script injection vectors, while Aadhaar and phone numbers are anonymized before logging.

### Layer 3: AI & Dual-Mode Inference Engine
* **GRPO Policy Optimization:** Trained via Group Relative Policy Optimization ($G=4$) with advantage baseline:
  $$A_i = \frac{R_i - \text{mean}(R)}{\text{std}(R) + \epsilon}$$
* **Multi-Component Reward:** Heavy reward weights for format compliance ($0.35$), tool selection precision ($0.35$), safety bounds ($0.20$), and conciseness ($0.10$).
* **Pluggable Architecture:** Seamless switching between Hugging Face Remote Inference (`Qwen2.5-7B-Instruct`), Local Quantized PyTorch PEFT, and a transparent deterministic fallback policy.

### Layer 4: Model Context Protocol (MCP) Hub
* **JSON-RPC 2.0 Compliance:** Standardized schemas with typed input parameters and execution timeout guards.
* **Scope-Based Tool Registry:** Decouples the reasoning model from direct code execution, isolating tools into read-only and stateful scopes.

### Layer 5: Independent MCP Service Servers
1. `scheme-service`: Search and detail retrieval across 1,500+ Central and State welfare programs.
2. `eligibility-service`: Evaluates demographic criteria (age, income, land holding, category, state).
3. `ocr-service`: Multimodal text and format verification for Aadhaar, Ration Cards, and Land Records.
4. `appointment-service`: Two-stage hold and booking engine for physical service centers.
5. `notification-service`: Dispatches auditable citizen alerts for status updates and deadlines.
