# Goal Structuring Notation (GSN) Safety Case: Civic AI Agent

```mermaid
graph TD
    G1["Goal: Agent executes public welfare workflows safely without misinformation or data harm"]
    
    G1 --> S1["Strategy 1: Multi-layer input and tool isolation"]
    G1 --> S2["Strategy 2: Verifiable deterministic truth grounding"]
    G1 --> S3["Strategy 3: Safe human escalation and fail-closed policies"]

    S1 --> C1["Claim 1.1: Indirect prompt injections are rejected by SecurityPolicyEngine"]
    S1 --> C12["Claim 1.2: Tool actions enforce RBAC scopes (read:schemes vs write:appointments)"]

    S2 --> C2["Claim 2.1: Final answers cite official portals and helplines"]
    S2 --> C22["Claim 2.2: Booking tokens (BK-) verified against DB log before issuance"]

    S3 --> C3["Claim 3.1: Ineligible applicants receive empathetic reason and alternative links"]
    S3 --> C32["Claim 3.2: Malformed tool inputs fail closed without state corruption"]
```

## Hazard Analysis & Risk Mitigation Matrix

| Hazard | Consequence | Mitigation Layer | Residual Risk |
| :--- | :--- | :--- | :---: |
| **H1: Hallucinated Eligibility** | Citizen is misled into believing they qualify for benefits they cannot receive. | Eligibility server computes deterministic mathematical rules on age and income caps. | Low |
| **H2: Double-Booking Overload** | Citizen double-clicks or retries, booking multiple center slots. | Idempotency engine (`SecurityPolicyEngine`) caches request hashes and replays prior bookings. | Zero |
| **H3: Indirect Prompt Injection** | Untrusted document text triggers unauthorized actions. | Taint tracking engine quarantines queries containing injection regexes (`ignore previous`, `<script>`). | Low |
| **H4: Ephemeral Data Loss** | Model restart wipes user records. | Decoupled MCP servers with mock DB persistence and structured JSON-RPC responses. | Low |
| **H5: Unverified Actions** | Agent claims appointment is confirmed without executing DB write. | Grounding verifier penalizes ungrounded tokens by -0.50 in RL reward landscape. | Zero |
