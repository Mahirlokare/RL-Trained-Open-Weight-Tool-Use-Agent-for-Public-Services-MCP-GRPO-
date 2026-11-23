"""
Generate Complete System Working Guide PDF for Civic AI.
Comprehensive, publication-grade document detailing the entire end-to-end working of the project:
Architecture, Citizen Workflow, GRPO Model Reasoning, MCP Protocol, Security Engine,
All 13 Modules, Test Verification, Code Mapping, and Viva Cheatsheet.
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
            self.drawString(54, letter[1] - 36, "Civic AI — Complete System Working Guide & Technical Architecture")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
        
        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 30, page_str)
        self.drawString(54, 30, "Civic AI Engineering Documentation • Author: Mahir Lokare • Production v2.4")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
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

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=10
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=12,
        textColor=colors.HexColor('#475569'),
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13.5,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#334155'),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletDark',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3.5
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7,
        leading=9.5,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f8fafc'),
        borderColor=colors.HexColor('#e2e8f0'),
        borderWidth=0.5,
        borderPadding=5,
        spaceAfter=5
    )

    callout_box = ParagraphStyle(
        'CalloutBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
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

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell,
        fontName='Helvetica-Bold'
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
    # HEADER / TITLE
    # =========================================================================
    story.append(Paragraph("CIVIC AI: COMPLETE SYSTEM WORKING GUIDE", title_style))
    story.append(Paragraph("End-to-End Architectural Blueprint, AI Reasoning Loop, MCP Protocols & Security Engine", subtitle_style))
    story.append(Paragraph(
        "<b>Author:</b> Mahir Lokare &nbsp;|&nbsp; "
        "<b>Framework:</b> Python, Gradio, Model Context Protocol (MCP), PyTorch & GRPO<br/>"
        "<b>Live Application:</b> <font color='#2563eb'>https://mahirlokare-civic-mcp-agent.hf.space/</font> &nbsp;|&nbsp; "
        "<b>Source Repository:</b> <font color='#2563eb'>https://github.com/Mahirlokare/RL-Trained-Open-Weight-Tool-Use-Agent-for-Public-Services-MCP-GRPO-</font>",
        meta_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceBefore=2, spaceAfter=8))

    # =========================================================================
    # EXECUTIVE SUMMARY CALLOUT
    # =========================================================================
    summary_text = (
        "<b>How Civic AI Works at a Glance:</b> Civic AI is an agentic public services system that empowers Indian citizens "
        "to discover welfare schemes, verify demographic eligibility, pre-validate identity documents, and schedule verification "
        "appointments. Unlike traditional chatbots that hallucinate or static portals that confuse users, Civic AI coordinates "
        "a <b>GRPO-trained open-weight reasoner model</b> with <b>5 decoupled Model Context Protocol (MCP) servers</b>. All stateful write "
        "operations are physically locked behind <b>SHA-256 parameter-bound confirmation tokens</b>, ensuring 100% fail-closed security."
    )
    t_sum = Table([[Paragraph(summary_text, callout_box)]], colWidths=[letter[0] - 108])
    t_sum.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3b82f6')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 1: THE END-TO-END CITIZEN JOURNEY
    # =========================================================================
    story.append(Paragraph("1. The End-to-End Citizen Journey (How a Request is Processed)", h1_style))
    story.append(Paragraph(
        "When a citizen interacts with Civic AI, their request passes through five synchronized stages:",
        body_style
    ))
    story.append(Paragraph("<b>Step 1: Input & Ingestion</b> — The citizen enters a question in natural English or Hindi (or speaks via voice input, or uploads an ID document). The UI passes this to the Security Gateway.", bullet_style))
    story.append(Paragraph("<b>Step 2: Safety & PII Sanitization</b> — The gateway sanitizes prompt injection vectors and masks citizen PII (Aadhaar numbers masked as <code>XXXX-XXXX-1234</code>, phone numbers masked as <code>XXXXXX8910</code>). It checks the caller's role (<code>citizen</code> vs. <code>official</code>).", bullet_style))
    story.append(Paragraph("<b>Step 3: Agentic Reasoning Loop (Turn Context)</b> — The <code>MCPAgentRuntime</code> loads conversational memory (up to 6 turns). It formats the prompt with XML schemas and passes it to the GRPO-trained reasoner model.", bullet_style))
    story.append(Paragraph("<b>Step 4: Tool Execution via MCP Hub</b> — When the model emits a <code>&lt;tool_call&gt;</code> (e.g. <code>verify_eligibility</code>), the MCP Hub routes the JSON-RPC call to the specific server. If the tool is a read operation, it executes immediately. If it is a write operation, the security engine enforces token validation.", bullet_style))
    story.append(Paragraph("<b>Step 5: Citizen-Safe Synthesis</b> — The model synthesizes the returned JSON payload into friendly, plain-language text. Internal reasoning tags (<code>&lt;think&gt;</code>) are filtered out, while raw tool executions are presented inside collapsible accordions for transparency.", bullet_style))

    # =========================================================================
    # SECTION 2: THE AI REASONING ENGINE & GRPO WORKING
    # =========================================================================
    story.append(Paragraph("2. The AI Reasoning Engine: How the Model Thinks & GRPO Training", h1_style))
    story.append(Paragraph(
        "Civic AI solves the core failure of generic commercial LLMs: unconstrained hallucination. It uses open-weight models "
        "(<code>Qwen2.5-7B-Instruct</code> / local LoRA checkpoints) reinforced via <b>Group Relative Policy Optimization (GRPO)</b>.",
        body_style
    ))
    story.append(Paragraph("The Structured XML Prompt Protocol:", h2_style))
    story.append(Paragraph(
        "The reasoner model separates internal deliberation from external tool interaction using strict XML delimiters:<br/>"
        "&lt;think&gt;<br/>"
        "Citizen is 45, income 2.5L, farmer from Maharashtra. Match against PM-KISAN rules.<br/>"
        "&lt;/think&gt;<br/>"
        "&lt;tool_call&gt;<br/>"
        "{\"name\": \"verify_eligibility\", \"arguments\": {\"scheme_id\": \"PM_KISAN\", \"citizen_age\": 45, \"annual_income\": 250000}}<br/>"
        "&lt;/tool_call&gt;<br/>"
        "&lt;tool_response&gt;{\"status\": \"ELIGIBLE\", \"benefit\": \"Rs. 6000/year in 3 installments\"}&lt;/tool_response&gt;<br/>"
        "&lt;final_answer&gt;You are fully eligible for PM-KISAN! You will receive Rs. 6,000 annually.&lt;/final_answer&gt;",
        code_style
    ))
    story.append(Paragraph("How GRPO Eliminates the Critic Network:", h2_style))
    story.append(Paragraph(
        "Traditional PPO (Proximal Policy Optimization) requires training a separate critic/value model alongside the policy, "
        "doubling GPU VRAM requirements. GRPO eliminates the critic entirely by sampling a group of $G=4$ outputs for each prompt "
        "and calculating advantage relative to the cohort mean and standard deviation:<br/>"
        "<b>Advantage Formula:</b> <code>A_i = (R_i - mean(R)) / (std(R) + eps)</code>",
        body_style
    ))
    story.append(Paragraph(
        "<b>Multi-Component Reward Function:</b> Outputs are evaluated by a 4-part deterministic verifier: "
        "<code>Reward = 0.35 * R_format + 0.35 * R_tool + 0.20 * R_safety + 0.10 * R_concise</code>. "
        "Hallucinated tool names or fabricated parameters yield a negative reward penalty.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 3: THE MODEL CONTEXT PROTOCOL (MCP) SERVERS
    # =========================================================================
    story.append(Paragraph("3. Model Context Protocol (MCP) Hub & The 5 Microservices", h1_style))
    story.append(Paragraph(
        "Rather than giving the AI model direct database access or executing Python code arbitrary in the backend, Civic AI implements "
        "the open standard <b>Model Context Protocol (MCP)</b>. The model acts as an MCP Client communicating via JSON-RPC 2.0 with 5 isolated servers:",
        body_style
    ))

    mcp_data = [
        [Paragraph("MCP Server", table_header), Paragraph("Tools Provided", table_header), Paragraph("Scope & Safety Level", table_header), Paragraph("How It Operates", table_header)],
        [
            Paragraph("<b>scheme-service</b>", table_cell_bold),
            Paragraph("• search_schemes<br/>• get_scheme_details", table_cell),
            Paragraph("Scope: <code>read:schemes</code><br/>Role: Citizen / Official", table_cell),
            Paragraph("Queries official gazette database (1,500+ schemes) across categories, ministries, age, and state filters.", table_cell)
        ],
        [
            Paragraph("<b>eligibility-service</b>", table_cell_bold),
            Paragraph("• verify_eligibility", table_cell),
            Paragraph("Scope: <code>read:eligibility</code><br/>Role: Citizen / Official", table_cell),
            Paragraph("Evaluates demographic rules (age, income limits, land records, domicile) without fabricated defaults.", table_cell)
        ],
        [
            Paragraph("<b>ocr-service</b>", table_cell_bold),
            Paragraph("• inspect_document", table_cell),
            Paragraph("Scope: <code>read:documents</code><br/>Role: Citizen / Official", table_cell),
            Paragraph("Parses Aadhaar, Ration Cards, and Land Records; checks layout compliance (preliminary pre-check, not sovereign validation).", table_cell)
        ],
        [
            Paragraph("<b>appointment-service</b>", table_cell_bold),
            Paragraph("• check_availability<br/>• request_appointment_hold<br/>• book_appointment", table_cell),
            Paragraph("Read: Open<br/><b>Write: Protected</b><br/>(Scope: <code>write:appointments</code>)", table_cell),
            Paragraph("Two-stage booking: Hold stage issues a 10-minute token; booking stage commits slot only with valid token.", table_cell)
        ],
        [
            Paragraph("<b>notification-service</b>", table_cell_bold),
            Paragraph("• send_notification", table_cell),
            Paragraph("<b>Write: Protected</b><br/>(Scope: <code>write:notifications</code>)", table_cell),
            Paragraph("Dispatches auditable SMS and Email alerts with unique message IDs and parameter validation.", table_cell)
        ]
    ]

    t_mcp = Table(mcp_data, colWidths=[90, 115, 110, 189])
    t_mcp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_mcp)
    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 4: SECURITY ENGINE & FAIL-CLOSED AUTHORIZATION
    # =========================================================================
    story.append(Paragraph("4. Security Engine: Cryptographic Tokens & Fail-Closed Defense", h1_style))
    story.append(Paragraph(
        "Civic AI eliminates the primary vulnerability of naive AI agents: unauthorized or hijacked state modifications. "
        "In <code>mcp_servers/security.py</code>, the security engine enforces mathematical authorization boundaries:",
        body_style
    ))
    story.append(Paragraph("• <b>Strict Fail-Closed Architecture:</b> Write tools reject execution by default. If a citizen attempts to book an appointment or dispatch an SMS without an official confirmation token, the backend returns: <code>{\"error\": \"PERMISSION_DENIED\", \"status\": 403}</code>.", bullet_style))
    story.append(Paragraph("• <b>Parameter-Bound Tokens (SHA-256 Digest):</b> Tokens are not generic random strings. A token (e.g. <code>CONFIRM-A8F391</code>) is cryptographically bound to the SHA-256 hash of the exact parameters: <code>Digest = SHA256(action + citizen_name + center_id + slot_time + salt)</code>. If an attacker modifies the slot time or citizen name, the token signature fails.", bullet_style))
    story.append(Paragraph("• <b>Atomic Token Destruction (No Replay Attacks):</b> Confirmation tokens have a strict 10-minute TTL (Time-To-Live). Once an appointment is booked, the token is permanently consumed and invalidated. Replaying the same request returns an expired token error.", bullet_style))

    # =========================================================================
    # SECTION 5: THE 13 PRODUCTION MODULES IN APP.PY
    # =========================================================================
    story.append(Paragraph("5. The 13 Production Modules Walkthrough (Web UI)", h1_style))
    story.append(Paragraph("The Gradio application in <code>app.py</code> organizes the system into 13 dedicated operational panels:", body_style))

    modules_summary = [
        ("1. Dashboard", "Live system telemetry, active LLM model provider, MCP servers status, and direct hosting links."),
        ("2. AI Citizen Assistant", "Bilingual conversational chat with multi-turn memory and expandable operational tool execution traces."),
        ("3. Scheme Explorer", "Interactive search & multi-filter catalog across 1,500+ Central and State welfare programs."),
        ("4. Eligibility Checker", "Evaluates age, annual income, domicile, category, and land holdings against scheme criteria."),
        ("5. Document Assistant", "Multimodal OCR pre-check for Aadhaar, Ration Cards, and 7/12 Land Records with format verification."),
        ("6. Appointments", "Two-stage appointment hold and booking engine for physical Seva Kendras requiring confirmation tokens."),
        ("7. Notifications", "Auditable SMS and email alert dispatcher with verified delivery records."),
        ("8. MCP Tool Monitor", "Real-time schema inspector displaying tool definitions, parameters, and live call latencies."),
        ("9. Model Lab", "Dynamic selector to switch between HuggingFace API, Local LoRA weights, or Fallback mode."),
        ("10. Training Center", "Interactive SFT loss tracking and real-time GRPO training curves with advantage telemetry."),
        ("11. Evaluation & Benchmarking", "Head-to-head empirical comparisons across tool precision, latency, and safety benchmarks."),
        ("12. Activity History", "Tamper-evident session history, execution audit logs, and security verification trails."),
        ("13. Settings & API Config", "Role management (Citizen vs. Official), language selection, and API credentials.")
    ]

    for title, desc in modules_summary:
        story.append(Paragraph(f"• <b>{title}:</b> {desc}", bullet_style))

    story.append(PageBreak())

    # =========================================================================
    # SECTION 6: CODEBASE ARCHITECTURE & FILE MAPPING
    # =========================================================================
    story.append(Paragraph("6. Codebase Architecture: What Every File Does", h1_style))
    story.append(Paragraph("A quick reference guide mapping every major file in the repository to its engineering responsibility:", body_style))

    code_data = [
        [Paragraph("Directory / File", table_header), Paragraph("Component", table_header), Paragraph("Key Classes / Functions", table_header), Paragraph("Engineering Responsibility", table_header)],
        [
            Paragraph("<code>app.py</code>", table_cell_bold),
            Paragraph("Frontend UI Layer", table_cell),
            Paragraph("<code>build_ui()</code>, <code>create_demo()</code>", table_cell),
            Paragraph("Assembles the 13 Gradio tabs, manages state, renders bilingual text, and handles user interactions.", table_cell)
        ],
        [
            Paragraph("<code>agent/runtime.py</code>", table_cell_bold),
            Paragraph("Agentic Runtime", table_cell),
            Paragraph("<code>MCPAgentRuntime</code>, <code>run_agent_turn()</code>", table_cell),
            Paragraph("Executes multi-turn reasoning loop, parses XML tool calls, truncates payloads, and prevents infinite loops.", table_cell)
        ],
        [
            Paragraph("<code>agent/models.py</code>", table_cell_bold),
            Paragraph("Model Abstraction", table_cell),
            Paragraph("<code>HuggingFaceInferenceProvider</code>, <code>RuleBasedFallbackPolicy</code>", table_cell),
            Paragraph("Dual-mode inference connecting to Qwen 2.5 7B remote endpoint or local quantized LoRA checkpoint.", table_cell)
        ],
        [
            Paragraph("<code>mcp_servers/registry.py</code>", table_cell_bold),
            Paragraph("Protocol Hub", table_cell),
            Paragraph("<code>MCPRegistry</code>, <code>execute_tool()</code>", table_cell),
            Paragraph("Manages JSON-RPC tool schemas, validates input arguments, checks RBAC permissions, and routes calls.", table_cell)
        ],
        [
            Paragraph("<code>mcp_servers/services.py</code>", table_cell_bold),
            Paragraph("Microservices", table_cell),
            Paragraph("<code>SchemeService</code>, <code>AppointmentService</code>, <code>OCRService</code>", table_cell),
            Paragraph("Implements the 5 independent MCP tool handlers, slot calculations, and document parsing.", table_cell)
        ],
        [
            Paragraph("<code>mcp_servers/security.py</code>", table_cell_bold),
            Paragraph("Security Gateway", table_cell),
            Paragraph("<code>SecurityEngine</code>, <code>validate_confirmation_token()</code>", table_cell),
            Paragraph("Enforces fail-closed writes, generates SHA-256 parameter-bound tokens, and masks citizen PII.", table_cell)
        ],
        [
            Paragraph("<code>training/train_grpo.py</code>", table_cell_bold),
            Paragraph("RL Engine", table_cell),
            Paragraph("<code>train_grpo_step()</code>, <code>compute_group_advantage()</code>", table_cell),
            Paragraph("Implements Group Relative Policy Optimization over group size G=4 with multi-reward decomposition.", table_cell)
        ],
        [
            Paragraph("<code>tests/test_mcp_servers.py</code>", table_cell_bold),
            Paragraph("Automated Tests", table_cell),
            Paragraph("<code>pytest -v</code> (29 test cases)", table_cell),
            Paragraph("Verifies schema integrity, fail-closed writes, token parameter tampering, and replay prevention.", table_cell)
        ]
    ]

    t_code = Table(code_data, colWidths=[110, 85, 130, 179])
    t_code.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_code)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 7: INTERVIEW & VIVA CHEAT SHEET
    # =========================================================================
    story.append(Paragraph("7. Viva & Recruiter Interview Cheat Sheet", h1_style))
    story.append(Paragraph("Top 4 technical questions interviewers will ask and the exact answers to deliver:", body_style))

    story.append(Paragraph("<b>Q1: Why did you use GRPO instead of standard PPO or DPO?</b><br/>"
                           "<i>Answer:</i> Standard PPO requires a separate critic model to estimate value baselines, doubling memory and training latency. GRPO computes advantages relative to a cohort of sampled responses (G=4), removing the critic entirely while maintaining mathematical stability on open-weight models.", body_style))

    story.append(Paragraph("<b>Q2: How do you prevent the AI from booking appointments without user permission?</b><br/>"
                           "<i>Answer:</i> The architecture enforces strict fail-closed authorization. Stateful write tools physically reject calls unless accompanied by a confirmation token bound via SHA-256 digest to the exact citizen parameters. The token expires in 10 minutes and is destroyed atomically upon first use.", body_style))

    story.append(Paragraph("<b>Q3: What is the purpose of the Model Context Protocol (MCP)?</b><br/>"
                           "<i>Answer:</i> MCP provides an open, standardized client-server boundary. The LLM only generates typed JSON-RPC requests; it never executes arbitrary code or accesses databases directly. This prevents prompt injections from escaping into the operating system.", body_style))

    story.append(Paragraph("<b>Q4: How do you verify the system actually works?</b><br/>"
                           "<i>Answer:</i> The project includes a complete test suite (<code>pytest</code>) with 29 automated tests covering schemas, RBAC, parameter tampering, and replay prevention. The system is deployed live on Hugging Face Spaces with verified HTTP 200 uptime.", body_style))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=2, spaceAfter=6))
    story.append(Paragraph(
        "<b>Live Links:</b> Web App: <font color='#2563eb'>https://mahirlokare-civic-mcp-agent.hf.space/</font> &nbsp;|&nbsp; "
        "GitHub: <font color='#2563eb'>https://github.com/Mahirlokare/RL-Trained-Open-Weight-Tool-Use-Agent-for-Public-Services-MCP-GRPO-</font>",
        meta_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {filename}")


if __name__ == "__main__":
    output_pdf = os.path.join(
        "C:\\Users\\Admin\\.gemini\\antigravity\\scratch\\rl-mcp-agent\\docs",
        "Civic_AI_Complete_System_Working_Guide.pdf"
    )
    build_pdf(output_pdf)
