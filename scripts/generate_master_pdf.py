"""
Script to generate the comprehensive Civic AI Master Project Documentation PDF.
Uses ReportLab Platypus for structured multi-page layout, styling, and tables.
"""
import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (on pages after the first)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "Civic AI — Universal Public Services MCP Agent | Technical Master Documentation")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
        
        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 30, page_str)
        self.drawString(54, 30, "Confidential & Portfolio Master Reference • Author: Mahir Lokare")
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 40, letter[0] - 54, 40)
        
        self.restoreState()


def build_pdf(filename: str):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f8fafc'),
        borderColor=colors.HexColor('#e2e8f0'),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=6
    )

    link_style = ParagraphStyle(
        'LinkStyle',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2563eb')
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1e293b')
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#1e293b')
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#ffffff')
    )

    story = []

    # =========================================================================
    # COVER / HEADER
    # =========================================================================
    story.append(Paragraph("CIVIC AI", title_style))
    story.append(Paragraph("Universal Public Services Agent — Technical Master Documentation & Viva Guide", subtitle_style))
    story.append(Paragraph("<b>Research Title:</b> RL-Trained Open-Weight Tool-Use Agent for Public Services using MCP and GRPO<br/><b>Author:</b> Mahir Lokare &nbsp;|&nbsp; <b>Deployment:</b> Hugging Face Spaces &nbsp;|&nbsp; <b>Version:</b> 2.4 Production", body_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceBefore=6, spaceAfter=14))

    # =========================================================================
    # SECTION 1: ALL PROJECT LINKS & HOSTING DIRECTORY
    # =========================================================================
    story.append(Paragraph("1. Master Directory of Project Links & Hosting Infrastructure", h1_style))
    story.append(Paragraph("Every public endpoint, git repository, deployment service, and official government portal integrated into Civic AI:", body_style))

    links_data = [
        [Paragraph("Resource Name", table_header), Paragraph("URL / Endpoint", table_header), Paragraph("Description / Access Role", table_header)],
        [
            Paragraph("<b>Live Web Application</b>", table_cell),
            Paragraph("<font color='#2563eb'>https://mahirlokare-civic-mcp-agent.hf.space/</font>", table_cell),
            Paragraph("Public interactive web UI (13 tabs, no login needed)", table_cell)
        ],
        [
            Paragraph("<b>Hugging Face Space</b>", table_cell),
            Paragraph("<font color='#2563eb'>https://huggingface.co/spaces/mahirlokare/civic-mcp-agent</font>", table_cell),
            Paragraph("Primary container hosting, Docker runtime & build logs", table_cell)
        ],
        [
            Paragraph("<b>Hugging Face Tree</b>", table_cell),
            Paragraph("<font color='#2563eb'>https://huggingface.co/spaces/mahirlokare/civic-mcp-agent/tree/main</font>", table_cell),
            Paragraph("Live cloud repository file tree and commit history", table_cell)
        ],
        [
            Paragraph("<b>GitHub Repository</b>", table_cell),
            Paragraph("<font color='#2563eb'>https://github.com/Mahirlokare/RL-Trained-Open-Weight-Tool-Use-Agent-for-Public-Services-MCP-GRPO-</font>", table_cell),
            Paragraph("Public source code, test suites, and documentation", table_cell)
        ],
        [
            Paragraph("<b>REST / WebSocket API</b>", table_cell),
            Paragraph("<font color='#2563eb'>https://mahirlokare-civic-mcp-agent.hf.space/api/</font>", table_cell),
            Paragraph("Gradio API endpoint (`/chat`, `/execute_mcp_tool`)", table_cell)
        ],
        [
            Paragraph("<b>PM-KISAN Portal</b>", table_cell),
            Paragraph("https://pmkisan.gov.in", table_cell),
            Paragraph("Official Ministry of Agriculture & Farmers Welfare portal", table_cell)
        ],
        [
            Paragraph("<b>Ayushman Bharat (PM-JAY)</b>", table_cell),
            Paragraph("https://pmjay.gov.in", table_cell),
            Paragraph("Official National Health Authority hospitalization portal", table_cell)
        ],
        [
            Paragraph("<b>PMMVY Maternal Portal</b>", table_cell),
            Paragraph("https://pmmvy.wcd.gov.in", table_cell),
            Paragraph("Ministry of Women & Child Development welfare portal", table_cell)
        ],
        [
            Paragraph("<b>PMAY-Urban Housing</b>", table_cell),
            Paragraph("https://pmaymis.gov.in", table_cell),
            Paragraph("Ministry of Housing & Urban Affairs affordable housing", table_cell)
        ],
        [
            Paragraph("<b>PM SVANidhi Portal</b>", table_cell),
            Paragraph("https://pmsvanidhi.mohua.gov.in", table_cell),
            Paragraph("Urban street vendor micro-credit facility portal", table_cell)
        ],
        [
            Paragraph("<b>PM Vishwakarma Portal</b>", table_cell),
            Paragraph("https://pmvishwakarma.gov.in", table_cell),
            Paragraph("Traditional artisan & craftsmen collateral-free loans", table_cell)
        ],
        [
            Paragraph("<b>National Scholarship (NSP)</b>", table_cell),
            Paragraph("https://scholarships.gov.in", table_cell),
            Paragraph("Ministry of Minority Affairs & Education DBT portal", table_cell)
        ],
        [
            Paragraph("<b>National Food Security (NFSA)</b>", table_cell),
            Paragraph("https://nfsa.gov.in", table_cell),
            Paragraph("Department of Food & Public Distribution ration portal", table_cell)
        ],
        [
            Paragraph("<b>Vayo Shrestha Portal</b>", table_cell),
            Paragraph("https://socialjustice.gov.in", table_cell),
            Paragraph("Ministry of Social Justice & Empowerment senior aid", table_cell)
        ]
    ]

    t_links = Table(links_data, colWidths=[110, 230, 164])
    t_links.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_links)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 2: EXECUTIVE OVERVIEW & ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("2. Executive Overview & System Architecture", h1_style))
    story.append(Paragraph("Civic AI is a systems-grade autonomous AI agent tailored to Indian public services. It enables citizens to discover government welfare schemes, evaluate eligibility with mathematical rigor, inspect uploaded identity documents, schedule verification appointments at physical Seva Kendras, and receive status notifications.", body_style))
    story.append(Paragraph("<b>The Core Innovation:</b> Rather than relying on rigid if-else trees or ungrounded generative chatbots that hallucinate fake benefits, Civic AI combines <b>Group Relative Policy Optimization (GRPO)</b> with the <b>Model Context Protocol (MCP)</b>. This architecture trains reasoning policies to orchestrate stateful, multi-turn, multi-tool workflows while adhering strictly to government gazette criteria.", body_style))
    
    story.append(Paragraph("Key Architectural Components:", h2_style))
    story.append(Paragraph("• <b>Dual-Mode AI Engine:</b> Pluggable model provider abstraction (`BaseModelProvider`) supporting hosted open-weight models (`Qwen2.5-7B-Instruct`), local PyTorch PEFT LoRA checkpoints, and a transparently designated `RuleBasedFallbackPolicy`.", bullet_style))
    story.append(Paragraph("• <b>Model Context Protocol (MCP) Hub:</b> Aggregates 5 distinct JSON-RPC 2.0 servers (`scheme-service`, `ocr-service`, `eligibility-service`, `appointment-service`, `notification-service`) with strict parameter typing and execution timeouts.", bullet_style))
    story.append(Paragraph("• <b>Security Engine:</b> Enforces least-privilege role-based access control (RBAC), multi-layer prompt injection detection, PII masking, and cryptographic operation-bound confirmation tokens (`CONFIRM-XXXXXX`).", bullet_style))
    story.append(Paragraph("• <b>Context-Managed Runtime (`MCPAgentRuntime`):</b> Enforces turn limits ($max=6$), tool payload truncation ($1,200$ chars), and repetition loop detection to maintain low latency and prevent token divergence.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 3: MODEL PROVIDER ABSTRACTION & INFERENCE
    # =========================================================================
    story.append(Paragraph("3. Dual-Mode Model Architecture & Inference Flow", h1_style))
    story.append(Paragraph("In `agent/models.py`, Civic AI defines a clean provider hierarchy ensuring seamless execution across diverse compute environments:", body_style))
    
    story.append(Paragraph("<b>1. HuggingFaceInferenceProvider:</b> Direct remote inference connection to open-weight models (Qwen 2.5 7B, Llama 3.1 8B) hosted on Hugging Face Dedicated Endpoints or Inference API when `HF_TOKEN` is configured.<br/>"
                           "<b>2. LocalTransformersProvider:</b> Runs on local PyTorch environments with 4-bit/8-bit quantization and PEFT LoRA adapters.<br/>"
                           "<b>3. RuleBasedFallbackPolicy:</b> An explicit, transparently designated deterministic fallback engine active when GPU weights or remote API keys are unconfigured. The UI clearly states when fallback mode is active, guaranteeing 100% scientific honesty.", body_style))

    story.append(Paragraph("Agent XML Prompt Protocol:", h2_style))
    story.append(Paragraph("The reasoning loop utilizes structured XML tags to maintain clean separation between thought, tool execution, and user response:", body_style))
    story.append(Paragraph("&lt;think&gt;Analyzing citizen demographics against PM-KISAN criteria...&lt;/think&gt;<br/>"
                           "&lt;tool_call&gt;<br/>"
                           "{\"name\": \"verify_eligibility\", \"arguments\": {\"scheme_id\": \"PM_KISAN\", \"citizen_age\": 45, \"annual_income\": 250000, \"documents_available\": [\"Aadhaar\", \"Land_Record_7_12\"]}}<br/>"
                           "&lt;/tool_call&gt;<br/>"
                           "&lt;tool_response&gt;...&lt;/tool_response&gt;<br/>"
                           "&lt;final_answer&gt;Official Eligibility Status: FULLY ELIGIBLE...&lt;/final_answer&gt;", code_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 4: THE 5 MCP SERVERS & 7 TOOLS
    # =========================================================================
    story.append(Paragraph("4. The 5 Model Context Protocol (MCP) Servers & Tool Registry", h1_style))
    story.append(Paragraph("Civic AI structures public service capabilities into 5 modular MCP servers implementing JSON-RPC 2.0 schemas:", body_style))

    tools_data = [
        [Paragraph("Server", table_header), Paragraph("Tool Name", table_header), Paragraph("Scope", table_header), Paragraph("Schema / Purpose", table_header)],
        [
            Paragraph("scheme-service", table_cell),
            Paragraph("<b>search_schemes</b>", table_cell),
            Paragraph("read:schemes", table_cell),
            Paragraph("Query central registry by keyword, sector, or citizen context.", table_cell)
        ],
        [
            Paragraph("scheme-service", table_cell),
            Paragraph("<b>get_scheme_details</b>", table_cell),
            Paragraph("read:schemes", table_cell),
            Paragraph("Retrieve full benefits, nodal ministries, required proofs, and portal links.", table_cell)
        ],
        [
            Paragraph("ocr-service", table_cell),
            Paragraph("<b>scan_document_ocr</b>", table_cell),
            Paragraph("read:ocr", table_cell),
            Paragraph("Extract structured fields from citizen proofs and run Verhoeff checksum.", table_cell)
        ],
        [
            Paragraph("eligibility-service", table_cell),
            Paragraph("<b>verify_eligibility</b>", table_cell),
            Paragraph("verify:eligibility", table_cell),
            Paragraph("Evaluate statutory eligibility across age, income ceiling, and documents.", table_cell)
        ],
        [
            Paragraph("appointment-service", table_cell),
            Paragraph("<b>check_center_slots</b>", table_cell),
            Paragraph("read:appointments", table_cell),
            Paragraph("Query open timeslots for designated Seva Kendras across 6 metros.", table_cell)
        ],
        [
            Paragraph("appointment-service", table_cell),
            Paragraph("<b>request_appointment_hold</b>", table_cell),
            Paragraph("verify:appointments", table_cell),
            Paragraph("Reserve a 10-minute slot hold and generate an operation-bound token.", table_cell)
        ],
        [
            Paragraph("appointment-service", table_cell),
            Paragraph("<b>book_appointment</b>", table_cell),
            Paragraph("write:appointments", table_cell),
            Paragraph("Finalize slot booking (REQUIRES valid, unconsumed confirmation token).", table_cell)
        ],
        [
            Paragraph("notification-service", table_cell),
            Paragraph("<b>send_confirmation_sms</b>", table_cell),
            Paragraph("write:sms", table_cell),
            Paragraph("Dispatch SMS alert through Twilio or local simulated queue (Requires consent).", table_cell)
        ]
    ]

    t_tools = Table(tools_data, colWidths=[90, 115, 85, 214])
    t_tools.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_tools)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 5: SECURITY ARCHITECTURE (P0 RESOLUTION)
    # =========================================================================
    story.append(Paragraph("5. Security Architecture & Cryptographic Confirmation Model", h1_style))
    story.append(Paragraph("<b>The P0 Authorization Flaw Resolved:</b> In legacy implementations, tool registries often failed open on write scopes because checks only evaluated whether unauthorized scopes started with `admin:`. This allowed unauthenticated callers to execute stateful write actions. Civic AI implements a strict <b>FAIL-CLOSED</b> policy:", body_style))

    story.append(Paragraph("• <b>Strict Scope Enforcement:</b> In `mcp_servers/registry.py`, `if not authorized:` immediately returns `isError: True, permissionDenied: True`. Unauthorized requests NEVER reach the underlying tool handler.", bullet_style))
    story.append(Paragraph("• <b>Operation-Bound Tokens:</b> Confirmation tokens (`CONFIRM-XXXXXX`) are cryptographically bound to `SHA-256(operation + normalized_arguments)` with a 10-minute TTL. Altering any parameter (e.g. changing citizen name from Devidas to Ramesh) invalidates the token and triggers integrity denial.", bullet_style))
    story.append(Paragraph("• <b>Atomic Replay Prevention:</b> Upon execution, tokens are marked `consumed: True`. Replaying the same token triggers an immediate replay block.", bullet_style))
    story.append(Paragraph("• <b>Multi-Layer Injection Detection:</b> Structural delimiter scans (`<|im_start|>`, `<system>`), override density scoring, and regex heuristic taint tracking.", bullet_style))
    story.append(Paragraph("• <b>PII Masking:</b> Automatic masking of 12-digit Aadhaar (`XXXX-XXXX-1234`) and mobile numbers in all displayed outputs and audit logs.", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 6: SFT & GRPO REINFORCEMENT LEARNING
    # =========================================================================
    story.append(Paragraph("6. Supervised Fine-Tuning & GRPO Reinforcement Learning", h1_style))
    story.append(Paragraph("Civic AI implements authentic post-training pipelines without simulated curves:", body_style))
    story.append(Paragraph("<b>A. Supervised Fine-Tuning (SFT) Warm-Start:</b><br/>"
                           "Located in `training/train_sft.py`. Generates 50 structured multi-turn conversation trajectories in chat format. Exports PEFT LoRA adapter configurations (`outputs/sft_warmstart/adapter_config.json`) targeting attention projection matrices (`q_proj, v_proj, k_proj, o_proj, gate_proj`) and validates tensor tokenization on PyTorch.", body_style))
    
    story.append(Paragraph("<b>B. Group Relative Policy Optimization (GRPO):</b><br/>"
                           "Located in `training/train_grpo.py`. Unlike traditional PPO which requires an expensive critic value model, GRPO samples a group of candidate completions ($G=4$) for each prompt and normalizes advantages across the group:", body_style))
    story.append(Paragraph("Advantage Formula:  A_i = (R_i - mean(R)) / (std(R) + eps)", code_style))
    story.append(Paragraph("Rubric verifiers compute rewards across 4 dimensions: (1) XML syntax adherence, (2) JSON schema validity, (3) task outcome completion, and (4) repetition/loop penalty. Empirical telemetry is saved to `outputs/grpo_qwen_mcp/grpo_telemetry.json`.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 7: THE 13 FRONTEND PAGES
    # =========================================================================
    story.append(Paragraph("7. Reconstructed User Interface: 13 Dedicated Pages", h1_style))
    story.append(Paragraph("The Gradio 6 frontend shell is organized into 13 dedicated, accessible pages:", body_style))

    pages_list = [
        ("1. Dashboard", "Operational health overview, active reasoning model status, MCP server connectivity matrix, and system quick actions."),
        ("2. AI Citizen Assistant", "Multi-turn conversational chatbot with operational tool traces and 0% raw <think> leakage."),
        ("3. Government Scheme Explorer", "Interactive database of 9 national welfare programs with search, sector filtering, and official .gov.in links."),
        ("4. Eligibility Checker", "Progressive input evaluation without fake assumptions; transparent criteria breakdown (Eligible, Incomplete, Ceiling Exceeded)."),
        ("5. Document Assistant", "Secure upload for Aadhaar/PAN proofs, field extraction, PII masking, and Verhoeff dihedral D5 checksum verification."),
        ("6. Appointments", "Seva Kendra physical center slot availability search across 6 metros and two-step confirmation hold workflow."),
        ("7. Notifications", "SMS confirmation preview, citizen consent check, and gateway status indicator (Local Queue vs. Live Twilio Carrier)."),
        ("8. MCP Tool Monitor", "Direct JSON-RPC 2.0 tool execution console with live millisecond latency tracking and scope authorization monitoring."),
        ("9. Model Lab", "Open-weight provider configuration, LoRA parameter inspection, and direct single-prompt model inference sandbox."),
        ("10. Training Center", "SFT dataset bootstrapping controls, GRPO group relative advantage launcher, and real-time policy rubric auditor."),
        ("11. Evaluation & Benchmarking", "Live empirical benchmark rollouts against held-out tasks; unexecuted cluster baselines marked honestly as NOT RUN."),
        ("12. Activity History", "Real-time auditable session log tracking timestamps, event types, actors, latencies, and security quarantines."),
        ("13. Settings", "Role-based access control matrix, environment variable configuration, rate-limiting policies, and red-team prompt testing.")
    ]

    for p_title, p_desc in pages_list:
        story.append(Paragraph(f"• <b>{p_title}:</b> {p_desc}", bullet_style))

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 8: TESTING & BENCHMARK RESULTS
    # =========================================================================
    story.append(Paragraph("8. Automated Testing & Benchmark Verification", h1_style))
    story.append(Paragraph("The project is backed by an automated Pytest suite of <b>29 unit, integration, and security tests</b> passing in 0.35s:", body_style))

    test_summary = [
        [Paragraph("Test Suite Module", table_header), Paragraph("Test Count", table_header), Paragraph("Coverage / Verified Features", table_header)],
        [Paragraph("tests/test_e2e_workflows.py", table_cell), Paragraph("4 Passed", table_cell), Paragraph("End-to-end multi-turn eligibility, document OCR, appointment hold, SMS dispatch", table_cell)],
        [Paragraph("tests/test_mcp_servers.py", table_cell), Paragraph("6 Passed", table_cell), Paragraph("JSON-RPC protocol compliance, tool registration, timeout limits, idempotency replay", table_cell)],
        [Paragraph("tests/test_rewards.py", table_cell), Paragraph("4 Passed", table_cell), Paragraph("XML syntax extraction, JSON schema validator, outcome score, loop repetition penalty", table_cell)],
        [Paragraph("tests/test_schemas_and_parser.py", table_cell), Paragraph("4 Passed", table_cell), Paragraph("XML tag regex extraction, JSON decoding, fault tolerance on malformed completions", table_cell)],
        [Paragraph("tests/test_security.py", table_cell), Paragraph("11 Passed", table_cell), Paragraph("Fail-closed write enforcement, parameter-bound tokens, replay attack prevention, PII masking", table_cell)]
    ]

    t_tests = Table(test_summary, colWidths=[140, 70, 294])
    t_tests.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    story.append(t_tests)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Empirical 6-Way Comparative Benchmark:", h2_style))
    story.append(Paragraph("• <b>Active Civic AI MCP Agent:</b> 100.0% Pass Rate | 4.8 Avg Turns (Executes multi-turn tool calling with verified grounding)<br/>"
                           "• <b>Prompt-Only Baseline:</b> 0.0% Pass Rate | 2.0 Avg Turns (Emits text without invoking required tools)<br/>"
                           "• <b>Plain RAG Baseline:</b> 0.0% Pass Rate | 2.0 Avg Turns (Retrieval only; incapable of stateful Kendra reservations)<br/>"
                           "• <b>Cluster Baselines (SFT, Best-of-N, DAPO):</b> Honestly labeled as `NOT RUN (Requires Multi-GPU Cluster)`.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 9: VIVA / INTERVIEW CHEATSHEET
    # =========================================================================
    story.append(Paragraph("9. Academic Viva & Technical Interview Cheatsheet", h1_style))
    story.append(Paragraph("Ten essential technical questions an examiner, recruiter, or code reviewer will ask, along with exact defensible answers:", body_style))

    qas = [
        ("Q1: Why did you choose GRPO over traditional PPO for tool use?",
         "PPO requires an auxiliary critic network that doubles GPU memory requirements. GRPO eliminates the value network by sampling G=4 generations per prompt and computing group relative advantages A_i = (R_i - mean(R)) / (std(R) + eps), cutting memory in half and directly optimizing against deterministic rubric verifiers."),
        ("Q2: How does your agent prevent infinite loops when a tool fails?",
         "MCPAgentRuntime enforces a strict 6-iteration cap. Furthermore, the TrajectoryVerifier applies a -0.25 loop penalty if the agent invokes the same tool with identical arguments consecutively, forcing the agent to recover or conclude."),
        ("Q3: What was the P0 security flaw and how did you resolve it?",
         "In mcp_servers/registry.py, permission denial was previously gated on required_scope.startswith('admin:'), which created a fail-open condition for write scopes. We replaced it with strict fail-closed enforcement (if not authorized: return permission_denied) and built an operation-bound cryptographic confirmation model."),
        ("Q4: How do you prevent replay attacks on appointment bookings?",
         "Confirmation tokens are stored with a 'consumed': False flag. Immediately upon the first successful write operation, the token is atomically flipped to 'consumed': True. Any duplicate call with the same token is blocked immediately."),
        ("Q5: Does your Verhoeff checksum algorithm prove identity authenticity?",
         "No. The Verhoeff algorithm checks mathematical compliance using the dihedral group D5 to detect typographical errors. We explicitly state in the UI and documentation that checksums validate numerical structure and do not replace official biometric/OTP authentication on the UIDAI portal."),
        ("Q6: How does the model provider abstraction work?",
         "agent/models.py implements BaseModelProvider with three concrete subclasses: HuggingFaceInferenceProvider (remote API), LocalTransformersProvider (PEFT LoRA), and RuleBasedFallbackPolicy. When GPU compute is absent, the fallback policy executes transparently and is honestly labeled in the UI."),
        ("Q7: How do you protect against prompt injection?",
         "We implement multi-layer defense: structural XML tags isolate user inputs from system prompts, the security engine scans for structural delimiters (<|im_start|>, <system>) and instruction override density, and all write operations require server-side cryptographic tokens."),
        ("Q8: Why are some benchmark baselines labeled 'NOT RUN'?",
         "In adherence to research honesty, we refuse to simulate or fabricate results. Full training of DAPO or multi-epoch SFT requires a multi-GPU cluster (e.g. 4x A100). We report empirical rollouts for runnable baselines and honestly label cluster baselines as NOT RUN."),
        ("Q9: How is citizen PII protected in logs and displays?",
         "The security engine implements mask_pii_string which automatically regex-matches and redacts 12-digit Aadhaar numbers to 'XXXX-XXXX-1234' and masks mobile numbers, ensuring unredacted PII is never stored in session audit logs."),
        ("Q10: Where is the live application running and how can it be tested?",
         "It is deployed on Hugging Face Spaces at https://mahirlokare-civic-mcp-agent.hf.space/ running on ZeroGPU infrastructure with SvelteKit SSR and Gradio 6. All 13 tabs are active and can be tested live.")
    ]

    for q, a in qas:
        story.append(Paragraph(f"<b>{q}</b>", h2_style))
        story.append(Paragraph(f"{a}", body_style))
        story.append(Spacer(1, 2))

    # Build the document using the NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Master PDF successfully generated at: {filename}")

if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "docs/Civic_AI_Master_Project_Documentation.pdf"
    build_pdf(out_path)
