"""
Refined official Seva Kendra Appointment Slip generator.
Draws vector government emblem, authentic rotated violet rubber stamp,
gate entry QR code, barcode, and authorized signature.
"""
import os
import math
import hashlib
from PIL import Image, ImageDraw, ImageFont

def draw_emblem(draw, cx, cy, r):
    # Classical government pillar emblem in vector
    # Base
    draw.rectangle([(cx - 28, cy + 24), (cx + 28, cy + 30)], fill="#38bdf8")
    draw.rectangle([(cx - 24, cy + 18), (cx + 24, cy + 24)], fill="#ffffff")
    # 4 Pillars
    for px in [-18, -6, 6, 18]:
        draw.rectangle([(cx + px - 2, cy - 14), (cx + px + 2, cy + 18)], fill="#38bdf8")
    # Capital / Roof
    draw.rectangle([(cx - 24, cy - 20), (cx + 24, cy - 14)], fill="#ffffff")
    draw.polygon([(cx - 28, cy - 20), (cx + 28, cy - 20), (cx, cy - 32)], fill="#38bdf8")

def draw_star(draw, cx, cy, r, color):
    points = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        curr_r = r if i % 2 == 0 else r * 0.4
        points.append((cx + curr_r * math.cos(angle), cy + curr_r * math.sin(angle)))
    draw.polygon(points, fill=color)

def create_appointment_slip(
    output_path: str,
    citizen_name: str = "Ramesh Devidas Patil",
    booking_id: str = "BK-SEVA-68079",
    scheme_name: str = "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
    kendra_name: str = "SEVA KENDRA PUNE NORTH (CENTRAL REGISTRY)",
    kendra_address: str = "Ground Floor, District Collectorate Complex, Station Road, Pune - 411001",
    slot_time: str = "Tuesday, 01 December 2026 at 10:00 AM (Reporting: 09:45 AM)",
    token_ref: str = "CONFIRM-DF037992399C"
):
    width, height = 1200, 1680
    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)

    # Fonts
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 32)
        subtitle_font = ImageFont.truetype("arialbd.ttf", 20)
        h2_font = ImageFont.truetype("arialbd.ttf", 19)
        bold_font = ImageFont.truetype("arialbd.ttf", 16)
        regular_font = ImageFont.truetype("arial.ttf", 15)
        small_font = ImageFont.truetype("arial.ttf", 13)
        stamp_font = ImageFont.truetype("arialbd.ttf", 13)
        stamp_center_font = ImageFont.truetype("arialbd.ttf", 15)
    except Exception:
        title_font = subtitle_font = h2_font = bold_font = regular_font = small_font = stamp_font = stamp_center_font = ImageFont.load_default()

    # Outer decorative borders
    draw.rectangle([(24, 24), (width - 24, height - 24)], outline="#1e3a8a", width=3)
    draw.rectangle([(32, 32), (width - 32, height - 32)], outline="#94a3b8", width=1)

    # Tricolor Banner at top
    draw.rectangle([(33, 33), (width - 33, 41)], fill="#ff9933")
    draw.rectangle([(33, 41), (width - 33, 49)], fill="#ffffff")
    draw.rectangle([(33, 49), (width - 33, 57)], fill="#138808")

    # Header Box (Dark Slate/Navy)
    draw.rectangle([(33, 58), (width - 33, 195)], fill="#0f172a")
    
    # Emblem graphic
    draw.ellipse([(65, 80), (165, 180)], fill="#1e293b", outline="#38bdf8", width=2)
    draw_emblem(draw, 115, 130, 40)

    # Header Titles
    draw.text((195, 85), "PUBLIC SERVICES SEVA KENDRA • STATE CITIZEN WELFARE PORTAL", font=subtitle_font, fill="#38bdf8")
    draw.text((195, 120), "OFFICIAL BENEFICIARY APPOINTMENT CONFIRMATION SLIP", font=title_font, fill="#ffffff")
    draw.text((195, 160), "STATUTORY DIRECT BENEFIT TRANSFER (DBT) & DOCUMENT VERIFICATION PASS", font=small_font, fill="#94a3b8")

    # Status Bar
    draw.rectangle([(40, 210), (width - 40, 260)], fill="#eff6ff", outline="#93c5fd", width=1)
    draw.text((60, 235), "● APPOINTMENT STATUS: CONFIRMED & ALLOTTED", font=h2_font, fill="#1d4ed8", anchor="lm")
    draw.text((width - 60, 235), f"BOOKING REF: {booking_id}", font=h2_font, fill="#0f172a", anchor="rm")

    # Details Grid
    start_y = 280
    fields = [
        ("BENEFICIARY CITIZEN NAME", citizen_name, "Registered Public Benefit Recipient"),
        ("WELFARE SCHEME APPLIED", scheme_name, "Statutory Central Entitlement"),
        ("APPOINTMENT DATE & TIME", slot_time, "Reporting Window: 15 Mins Prior to Slot"),
        ("DESIGNATED KENDRA CENTER", kendra_name, "Center Code: SEVA-PUNE-04"),
        ("CENTER PHYSICAL ADDRESS", kendra_address, "Verification Section • Counter #4"),
        ("SECURITY CONFIRMATION TOKEN", token_ref, "SHA-256 Parameter-Bound Cryptographic Token"),
        ("AUTHENTICATION TIER", "Citizen Direct Self-Booking (Verified)", "Biometric Aadhaar Authentication Required"),
    ]

    for i, (label, val, note) in enumerate(fields):
        curr_y = start_y + (i * 70)
        bg_color = "#f8fafc" if i % 2 == 0 else "#ffffff"
        draw.rectangle([(40, curr_y), (width - 40, curr_y + 66)], fill=bg_color, outline="#e2e8f0", width=1)
        
        draw.text((60, curr_y + 18), label, font=small_font, fill="#64748b")
        draw.text((60, curr_y + 42), val, font=bold_font, fill="#0f172a")
        draw.text((width - 60, curr_y + 42), note, font=small_font, fill="#475569", anchor="rm")

    # Instructions Box
    box_y = start_y + (len(fields) * 70) + 20
    draw.rectangle([(40, box_y), (width - 40, box_y + 260)], fill="#f8fafc", outline="#cbd5e1", width=1)
    draw.rectangle([(40, box_y), (width - 40, box_y + 38)], fill="#e2e8f0")
    draw.text((60, box_y + 19), "MANDATORY CHECKLIST & VERIFICATION PROTOCOL TO BRING AT KENDRA", font=h2_font, fill="#0f172a", anchor="lm")

    checklist = [
        "1. Original Aadhaar Card along with two self-attested photocopies for biometric matching.",
        "2. Original 7/12 Land Revenue Record (Satbara Utara) or relevant land ownership title extract.",
        "3. Active Bank Account Passbook / Canceled Cheque showing IFSC code for DBT direct transfer.",
        "4. Two recent passport-size colored photographs of the primary applicant.",
        "5. Present this digital appointment pass or printout at the Kendra Security Desk for priority queue token.",
        "6. In case of scheduling conflicts, please initiate cancellation at least 4 hours before the slot time."
    ]

    for idx, item in enumerate(checklist):
        draw.text((60, box_y + 55 + (idx * 31)), item, font=regular_font, fill="#334155")

    # Bottom Area: QR Code, Barcode, Official Stamp & Signature
    bottom_y = box_y + 285

    # 1. Gate Scan QR Code Box
    qr_x, qr_y, qr_size = 55, bottom_y + 10, 160
    draw.rectangle([(qr_x, qr_y), (qr_x + qr_size, qr_y + qr_size)], fill="#ffffff", outline="#0f172a", width=2)
    
    # Stylized QR pattern
    h_hash = hashlib.sha256(f"{booking_id}:{token_ref}".encode()).hexdigest()
    for corner_x, corner_y in [(qr_x + 8, qr_y + 8), (qr_x + qr_size - 36, qr_y + 8), (qr_x + 8, qr_y + qr_size - 36)]:
        draw.rectangle([(corner_x, corner_y), (corner_x + 28, corner_y + 28)], fill="#0f172a")
        draw.rectangle([(corner_x + 5, corner_y + 5), (corner_x + 23, corner_y + 23)], fill="#ffffff")
        draw.rectangle([(corner_x + 9, corner_y + 9), (corner_x + 19, corner_y + 19)], fill="#0f172a")
    
    for r in range(4, 12):
        for c in range(4, 12):
            bit = h_hash[(r * 12 + c) % len(h_hash)]
            if bit in "01234567":
                draw.rectangle([(qr_x + c * 12, qr_y + r * 12), (qr_x + c * 12 + 9, qr_y + r * 12 + 9)], fill="#0f172a")

    draw.text((qr_x + qr_size // 2, qr_y + qr_size + 14), "GATE SCAN QR", font=small_font, fill="#64748b", anchor="mm")
    draw.text((qr_x + qr_size // 2, qr_y + qr_size + 28), f"REF: {booking_id}", font=small_font, fill="#0f172a", anchor="mm")

    # 2. Barcode
    bc_x = 245
    bc_y = bottom_y + 30
    draw.text((bc_x, bc_y - 18), "MACHINE READABLE ENTRY BARCODE", font=small_font, fill="#64748b")
    for i in range(115):
        lw = 2 if i % 3 == 0 or i % 7 == 0 else (3 if i % 5 == 0 else 1)
        draw.line([(bc_x + (i * 3), bc_y), (bc_x + (i * 3), bc_y + 60)], fill="#0f172a", width=lw)
    draw.text((bc_x + 172, bc_y + 72), f"* {booking_id} *", font=bold_font, fill="#0f172a", anchor="mm")
    draw.text((bc_x + 172, bc_y + 92), "VALID ONLY ON 01-DEC-2026", font=small_font, fill="#475569", anchor="mm")

    # 3. HIGH-REALISM OFFICIAL PURPLE INK RUBBER STAMP (WITH ROTATION)
    # Create stamp on transparent RGBA canvas and paste with tilt
    stamp_size = 280
    stamp_img = Image.new("RGBA", (stamp_size, stamp_size), (255, 255, 255, 0))
    s_draw = ImageDraw.Draw(stamp_img)
    scx, scy = stamp_size // 2, stamp_size // 2
    sr = 120
    s_color = (88, 28, 135, 230)  # Official dark violet ink with slight opacity

    # Concentric circles with rubber seal aesthetic
    s_draw.ellipse([(scx - sr, scy - sr), (scx + sr, scy + sr)], outline=s_color, width=4)
    s_draw.ellipse([(scx - (sr - 8), scy - (sr - 8)), (scx + (sr - 8), scy + (sr - 8))], outline=s_color, width=1)
    s_draw.ellipse([(scx - (sr - 28), scy - (sr - 28)), (scx + (sr - 28), scy + (sr - 28))], outline=s_color, width=2)

    # Top & Bottom Curved Text Simulation
    s_draw.text((scx, scy - 88), "PUBLIC SERVICES SEVA KENDRA", font=stamp_font, fill=s_color, anchor="mm")
    s_draw.text((scx, scy - 68), "PUNE NORTH DISTRICT", font=small_font, fill=s_color, anchor="mm")

    # Center Box with Status
    s_draw.rectangle([(scx - 85, scy - 24), (scx + 85, scy + 24)], fill=(255, 255, 255, 240), outline=s_color, width=2)
    s_draw.text((scx, scy - 8), "SLOT ALLOTTED & VERIFIED", font=stamp_center_font, fill=s_color, anchor="mm")
    s_draw.text((scx, scy + 10), "DATE: 24-NOV-2026", font=stamp_font, fill=s_color, anchor="mm")

    # Bottom texts in stamp
    s_draw.text((scx, scy + 58), "GOVT. OF MAHARASHTRA", font=small_font, fill=s_color, anchor="mm")
    s_draw.text((scx, scy + 80), "COUNTER #04 • OFFICIALLY ISSUED", font=stamp_font, fill=s_color, anchor="mm")

    # Rotate stamp slightly (-10 degrees) for authentic hand-stamped look
    rotated_stamp = stamp_img.rotate(-10, resample=Image.BICUBIC, expand=False)
    img.paste(rotated_stamp, (650, bottom_y - 25), rotated_stamp)

    # 4. Authorized Officer Signature Box
    sig_x = 1040
    sig_y = bottom_y + 90
    draw.line([(sig_x - 85, sig_y), (sig_x + 85, sig_y)], fill="#64748b", width=1)
    
    # Clean signature stroke
    draw.arc([(sig_x - 60, sig_y - 38), (sig_x, sig_y - 8)], start=180, end=360, fill="#1e3a8a", width=2)
    draw.arc([(sig_x - 20, sig_y - 48), (sig_x + 50, sig_y - 12)], start=120, end=300, fill="#1e3a8a", width=2)
    draw.line([(sig_x + 25, sig_y - 32), (sig_x + 80, sig_y - 10)], fill="#1e3a8a", width=2)

    draw.text((sig_x, sig_y + 10), "Authorized Kendra Officer", font=bold_font, fill="#0f172a", anchor="mm")
    draw.text((sig_x, sig_y + 28), "Public Services Authority", font=small_font, fill="#64748b", anchor="mm")
    draw.text((sig_x, sig_y + 44), "E-Sign: SEC-OFFICER-PUNE", font=small_font, fill="#0284c7", anchor="mm")

    # Bottom Footer line
    draw.line([(40, height - 55), (width - 40, height - 55)], fill="#cbd5e1", width=1)
    draw.text((50, height - 38), "Civic AI Public Infrastructure Engine • Generated via Model Context Protocol (MCP) Secure Token Gateway", font=small_font, fill="#94a3b8")
    draw.text((width - 50, height - 38), "Official Electronic Pass — No Physical Signature Needed", font=small_font, fill="#94a3b8", anchor="rm")

    img.save(output_path, "PNG", dpi=(300, 300))
    print(f"Refined Appointment Slip saved: {output_path}")

if __name__ == "__main__":
    out_dir = r"C:\Users\Admin\.gemini\antigravity\scratch\rl-mcp-agent\docs"
    out_file = os.path.join(out_dir, "Seva_Kendra_Appointment_Slip.png")
    create_appointment_slip(out_file)
