"""
Generate Complete Chat Transcript PDF for Civic AI.
Extracts the full unabridged conversation between the User and the AI Assistant
from transcript_full.jsonl and typesets it into an executive-grade, readable multi-page PDF.
Direct flowable streaming without rigid table cell height constraints.
"""
import os
import sys
import json
import re
import html
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
            self.drawString(54, letter[1] - 36, "Civic AI — Complete Engineering & Project Consultation Chat Transcript")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)
        
        # Footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 30, page_str)
        self.drawString(54, 30, "Civic AI Consultation Archive • Author: Mahir Lokare • Complete Transcript")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 40, letter[0] - 54, 40)
        
        self.restoreState()


def format_markdown_to_xml(text: str) -> str:
    """Safely converts markdown to ReportLab inline tags."""
    text = html.escape(text)
    # Code spans `code`
    text = re.sub(r'`([^`\n]+?)`', r'<font face="Courier" color="#1e3a8a"><b>\1</b></font>', text)
    # Bold **text**
    text = re.sub(r'\*\*([^*]+?)\*\*', r'<b>\1</b>', text)
    return text


def create_safe_paragraph(raw_text: str, style: ParagraphStyle) -> Paragraph:
    """Attempts to render with formatted XML; falls back to pure escaped text on any syntax mismatch."""
    if not raw_text.strip():
        return Paragraph("&nbsp;", style)
    try:
        formatted = format_markdown_to_xml(raw_text)
        return Paragraph(formatted, style)
    except Exception:
        pass
    
    # Fallback to plain escaped text
    try:
        plain_escaped = html.escape(raw_text).replace('\n', '<br/>')
        return Paragraph(plain_escaped, style)
    except Exception:
        safe_str = "".join([c for c in raw_text if ord(c) < 128])
        return Paragraph(html.escape(safe_str), style)


def build_chat_pdf(transcript_path: str, output_pdf: str):
    doc = SimpleDocTemplate(
        output_pdf,
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

    user_header_style = ParagraphStyle(
        'UserHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    asst_header_style = ParagraphStyle(
        'AsstHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True
    )

    user_body_style = ParagraphStyle(
        'UserBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=8,
        spaceAfter=4
    )

    asst_body_style = ParagraphStyle(
        'AsstBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=colors.HexColor('#334155'),
        leftIndent=8,
        spaceAfter=4
    )

    asst_bullet_style = ParagraphStyle(
        'AsstBullet',
        parent=asst_body_style,
        leftIndent=18,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=6.5,
        leading=8.5,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f8fafc'),
        borderColor=colors.HexColor('#e2e8f0'),
        borderWidth=0.5,
        borderPadding=4,
        leftIndent=8,
        spaceAfter=4
    )

    story = []

    # Title / Header
    story.append(Paragraph("CIVIC AI: COMPLETE CONSULTATION & CHAT TRANSCRIPT", title_style))
    story.append(Paragraph("Full Chronological Record of Technical Directives, Implementation, & Architecture Sessions", subtitle_style))
    story.append(Paragraph(
        "<b>Project:</b> Civic AI — Universal Public Services Agent (RL & MCP) &nbsp;|&nbsp; "
        "<b>Author:</b> Mahir Lokare<br/>"
        "<b>Live Deployment:</b> <font color='#2563eb'>https://mahirlokare-civic-mcp-agent.hf.space/</font> &nbsp;|&nbsp; "
        "<b>GitHub:</b> <font color='#2563eb'>https://github.com/Mahirlokare/RL-Trained-Open-Weight-Tool-Use-Agent-for-Public-Services-MCP-GRPO-</font>",
        meta_style
    ))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2563eb'), spaceBefore=2, spaceAfter=8))

    # Read and parse transcript
    dialogs = []
    if os.path.exists(transcript_path):
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    d = json.loads(line)
                    t = d.get('type')
                    c = d.get('content')
                    if not c or not isinstance(c, str):
                        continue
                    c = c.strip()
                    if not c:
                        continue
                    if t == 'USER_INPUT':
                        m = re.search(r'<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>', c, re.DOTALL)
                        req_text = m.group(1).strip() if m else c
                        req_text = re.sub(r'<CONTEXT_SUMMARY>.*?</CONTEXT_SUMMARY>', '[Previous Context Summary Truncated]', req_text, flags=re.DOTALL).strip()
                        dialogs.append(('User', req_text, d.get('created_at', '')))
                    elif t == 'PLANNER_RESPONSE':
                        dialogs.append(('Assistant', c, d.get('created_at', '')))
                except Exception:
                    pass

    # Overview Banner
    overview_text = (
        f"<b>Transcript Summary:</b> This document captures the chronological engineering transcript of the Civic AI project "
        f"across <b>{len(dialogs)} recorded dialog turns</b>. It documents the initial project formulation, the Master Engineering Directive, "
        f"the full remediation of P0 security vulnerabilities, the implementation of GRPO training and MCP tool servers, "
        f"the design of 13 production modules, automated test suites, LinkedIn launch strategy, and cloud deployment on Hugging Face Spaces."
    )
    t_ov = Table([[create_safe_paragraph(overview_text, asst_body_style)]], colWidths=[letter[0] - 108])
    t_ov.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#eff6ff')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#3b82f6')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_ov)
    story.append(Spacer(1, 10))

    user_turn_count = 0
    asst_turn_count = 0

    for role, content, timestamp in dialogs:
        ts_clean = timestamp[:19].replace('T', ' ') if timestamp else ''
        
        if role == 'User':
            user_turn_count += 1
            header_text = f"👤 <b>USER</b> &nbsp;|&nbsp; <i>Turn #{user_turn_count} &nbsp;•&nbsp; {ts_clean}</i>"
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#94a3b8'), spaceBefore=8, spaceAfter=4))
            story.append(create_safe_paragraph(header_text, user_header_style))
            
            paragraphs = content.split('\n\n')
            for p in paragraphs:
                p = p.strip()
                if not p:
                    continue
                story.append(create_safe_paragraph(p, user_body_style))

        else:
            asst_turn_count += 1
            header_text = f"🤖 <b>CIVIC AI ASSISTANT</b> &nbsp;|&nbsp; <i>Response #{asst_turn_count} &nbsp;•&nbsp; {ts_clean}</i>"
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#3b82f6'), spaceBefore=10, spaceAfter=4))
            story.append(create_safe_paragraph(header_text, asst_header_style))
            
            lines = content.split('\n')
            in_code = False
            code_buffer = []
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('```'):
                    if in_code:
                        in_code = False
                        code_text = '\n'.join(code_buffer)
                        story.append(create_safe_paragraph(code_text, code_style))
                        code_buffer = []
                    else:
                        in_code = True
                        code_buffer = []
                    continue
                
                if in_code:
                    code_buffer.append(line)
                    continue
                
                if not stripped:
                    continue
                
                if stripped.startswith('* ') or stripped.startswith('- ') or stripped.startswith('• '):
                    bullet_text = stripped[2:].strip()
                    story.append(create_safe_paragraph(f"• {bullet_text}", asst_bullet_style))
                elif stripped.startswith('#'):
                    heading_text = stripped.lstrip('#').strip()
                    h_style = ParagraphStyle(
                        'DynamicH',
                        parent=asst_header_style,
                        fontSize=9.5,
                        leading=13,
                        textColor=colors.HexColor('#1e3a8a'),
                        spaceBefore=4,
                        spaceAfter=2
                    )
                    story.append(create_safe_paragraph(f"<b>{heading_text}</b>", h_style))
                else:
                    story.append(create_safe_paragraph(stripped, asst_body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated Chat Transcript PDF: {output_pdf}")


if __name__ == "__main__":
    transcript_file = r"C:\Users\Admin\.gemini\antigravity\brain\c6c8128e-e388-4cda-9227-fff033773f71\.system_generated\logs\transcript_full.jsonl"
    out_file = r"C:\Users\Admin\.gemini\antigravity\scratch\rl-mcp-agent\docs\Civic_AI_Complete_Chat_Transcript.pdf"
    build_chat_pdf(transcript_file, out_file)
