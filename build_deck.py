"""Builds InsureNdClaim_Demo.pptx (7 slides) from the screenshots in img/. Run: python build_deck.py"""
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

HERE = Path(__file__).parent
OUT = HERE.parent / "insurendclaim" / "docs" / "InsureNdClaim_Demo.pptx"

NAVY, INDIGO, PURPLE = RGBColor(0x12, 0x15, 0x1D), RGBColor(0x2F, 0x5B, 0xEA), RGBColor(0x6A, 0x3D, 0xE8)
INK, MUTED, BG, CARD = RGBColor(0x1C, 0x23, 0x33), RGBColor(0x66, 0x70, 0x85), RGBColor(0xF6, 0xF7, 0xFB), RGBColor(0xFF, 0xFF, 0xFF)
GREEN, AMBER, LINE, SOFT = RGBColor(0x12, 0x80, 0x5C), RGBColor(0xB7, 0x79, 0x1F), RGBColor(0xE1, 0xE4, 0xEC), RGBColor(0xEE, 0xF2, 0xFF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)


# ---------- screenshots: trim the browser chrome / empty space ----------
def crop(name: str, x0=150, x1=1262, pad=24) -> Path:
    im = Image.open(HERE / "img" / f"{name}.png").convert("RGB")
    w, h = im.size
    # the capture window is taller than the page: below the page everything is pure white
    white_from = next((y for y in range(120, h) if all(im.getpixel((x, y)) == (255, 255, 255) for x in range(x0, x1, 40))), h)
    bg = im.getpixel((20, 20))
    bottom = max(y for y in range(0, white_from) if any(im.getpixel((x, y)) != bg for x in range(x0, x1, 6)))
    out = HERE / "img" / f"{name}_crop.png"
    im.crop((x0, 0, x1, min(bottom + pad, white_from))).save(out)
    return out


IMG = {n: crop(n) for n in ("dashboard", "claim", "devices", "adjuster", "adminclaims", "admin", "policies", "directory")}


# ---------- helpers ----------
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def rect(slide, x, y, w, h, fill=None, line=None, shape=MSO_SHAPE.RECTANGLE, radius=None):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1)
    s.shadow.inherit = False
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    return s


def text(slide, x, y, w, h, content, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.1):
    """content: str or list of paragraphs; a paragraph is str or list of (text, {bold, color, size}) runs."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    paras = content if isinstance(content, list) else [content]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        runs = para if isinstance(para, list) else [(para, {})]
        for t, st in runs:
            r = p.add_run()
            r.text = t
            r.font.size = Pt(st.get("size", size))
            r.font.bold = st.get("bold", bold)
            r.font.color.rgb = st.get("color", color)
            r.font.name = "Segoe UI"
    return tb


def bullets(slide, x, y, w, items, size=14, gap=6, color=INK, dot=INDIGO):
    line_h = size / 72 * 1.32
    chars = (w - 0.18) * 72 / (size * 0.47)  # rough characters per line for Segoe UI
    yy = y
    for it in items:
        lines = max(1, -(-len(it) // int(chars)))
        rect(slide, x, yy + 0.09, 0.09, 0.09, fill=dot, shape=MSO_SHAPE.OVAL)
        text(slide, x + 0.18, yy, w - 0.18, lines * line_h + 0.1, it, size=size, color=color)
        yy += lines * line_h + gap / 72 + 0.06


def picture(slide, name, x, y, w=None, h=None):
    pic = slide.shapes.add_picture(str(IMG[name]), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    pic.line.color.rgb = LINE
    pic.line.width = Pt(1)
    return pic


def title(slide, head, sub=None, dark=False):
    text(slide, 0.6, 0.35, 12.1, 0.7, head, size=30, bold=True, color=WHITE if dark else INK)
    if sub:
        text(slide, 0.6, 1.05, 12.1, 0.4, sub, size=16, color=RGBColor(0xB8, 0xC0, 0xD4) if dark else MUTED)


def new_slide(dark=False, notes=""):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = NAVY if dark else BG
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def footer(slide, n, dark=False):
    text(slide, 0.6, 7.05, 6, 0.3, "InsureNdClaim", size=11, color=MUTED if not dark else RGBColor(0x8A, 0x93, 0xA8))
    text(slide, 11.9, 7.05, 0.9, 0.3, f"{n} / 7", size=11, color=MUTED if not dark else RGBColor(0x8A, 0x93, 0xA8), align=PP_ALIGN.RIGHT)


def card(slide, x, y, w, h, accent=None):
    c = rect(slide, x, y, w, h, fill=CARD, line=LINE, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.04)
    if accent:
        rect(slide, x, y + 0.12, 0.07, h - 0.24, fill=accent)
    return c


# =====================================================================
# 1. Title
# =====================================================================
s = new_slide(dark=True, notes=(
    "Open: InsureNdClaim is one platform that takes a policyholder from 'something happened' to 'money in the account', "
    "with AI doing the heavy lifting up front and humans (adjuster, admin) deciding. We'll show three portals live."))
rect(s, 0, 0, 13.333, 0.12, fill=INDIGO)
rect(s, 0.6, 1.5, 0.9, 0.9, fill=INDIGO, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.2)
text(s, 0.6, 1.5, 0.9, 0.9, "IC", size=28, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.6, 2.65, 12, 1.0, "InsureNdClaim", size=54, bold=True, color=WHITE)
text(s, 0.6, 3.65, 11, 1.0, "One AI-powered platform for the whole claim journey: from the first photo to the payout.", size=24, color=RGBColor(0xC9, 0xD1, 0xE6))
for i, (name, sub) in enumerate([("Policyholder", "files, tracks, gets paid"), ("Adjuster", "inspects, schedules, proposes"), ("Admin", "approves, pays, oversees")]):
    x = 0.6 + i * 3.1
    rect(s, x, 5.1, 2.9, 1.0, fill=RGBColor(0x1E, 0x24, 0x35), line=RGBColor(0x33, 0x3B, 0x52), shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)
    text(s, x + 0.15, 5.15, 2.6, 0.4, name, size=18, bold=True, color=WHITE)
    text(s, x + 0.15, 5.6, 2.6, 0.4, sub, size=13, color=RGBColor(0xA8, 0xB1, 0xC8))
text(s, 0.6, 6.55, 12, 0.4, "Live demo  ·  GenAI Kata", size=14, color=RGBColor(0x8A, 0x93, 0xA8))

# =====================================================================
# 2. What it does
# =====================================================================
s = new_slide(notes=(
    "Claims are slow because information is scattered: coverage is unclear, people don't know which documents to send, and nobody can see "
    "where the claim is. We answer that with five capabilities. Each one is live in the app, not a mock-up; I'll point at them as we go."))
title(s, "Five capabilities, one connected claim journey", "Everything a policyholder, adjuster and insurer needs, in one place")
pillars = [
    ("1", "Seamless claims ecosystem", "Coverage lookup, AI filing, document upload, inspection and settlement in one flow.", INDIGO),
    ("2", "Real-time visibility", "Status stepper, timeline, “what happens next” and payout date; a bell for every update.", PURPLE),
    ("3", "Proactive reminders", "Renewals, premium due dates, missing documents and coverage gaps, before the customer asks.", AMBER),
    ("4", "IoT & telematics evidence", "Collision, water-leak and fall data from car, home and wearables attach to the claim.", GREEN),
    ("5", "Adjuster scheduling", "Adjusters publish slots; customers book on-site, video or audio; calendar stays in sync.", INDIGO),
]
for i, (n, head, body, col) in enumerate(pillars):
    x = 0.6 + i * 2.46
    card(s, x, 1.85, 2.3, 3.55)
    rect(s, x, 1.85, 2.3, 0.1, fill=col)
    text(s, x + 0.15, 2.1, 0.6, 0.6, n, size=30, bold=True, color=col)
    text(s, x + 0.15, 2.75, 2.0, 0.9, head, size=17, bold=True)
    text(s, x + 0.15, 3.65, 2.0, 1.7, body, size=13, color=MUTED)
card(s, 0.6, 5.7, 12.13, 1.05)
text(s, 0.85, 5.8, 3.2, 0.85, [[("Before", {"bold": True, "color": MUTED, "size": 13})], "Phone calls, unclear cover, repeat follow-ups"], size=15, color=INK, anchor=MSO_ANCHOR.MIDDLE)
text(s, 4.15, 5.8, 0.6, 0.85, "→", size=30, bold=True, color=INDIGO, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
text(s, 4.9, 5.8, 7.7, 0.85, [[("With InsureNdClaim", {"bold": True, "color": GREEN, "size": 13})], "Describe it, get a clause-cited cover check, see every next step, and get paid, all tracked"], size=15, anchor=MSO_ANCHOR.MIDDLE)
footer(s, 2)

# =====================================================================
# 3. Three portals
# =====================================================================
s = new_slide(notes=(
    "Same login page for everyone; the account decides which portal opens, and the server enforces the same boundaries: "
    "a customer can't see another customer's claim, an adjuster only sees claims assigned to them, and only admin can approve money."))
title(s, "Three portals, one login", "The account decides what you see; the server enforces it on every request")
cols = [
    ("Policyholder", "dashboard", INDIGO, ["Dashboard, policies, claims, devices", "AI assistant files the claim", "Upload documents, track status", "Settings & notifications"]),
    ("Adjuster", "adjuster", PURPLE, ["Own calendar: open / remove slots", "Assigned claims & device evidence", "Verify or reject documents", "Record inspection, propose payout"]),
    ("Admin", "admin", GREEN, ["All claims, assign adjusters", "Approve / reject / pay settlements", "Accounts, reminders, AI & HTTP logs", "Portfolio view: open, awaiting, paid"]),
]
for i, (name, img, col, pts) in enumerate(cols):
    x = 0.6 + i * 4.1
    card(s, x, 1.7, 3.95, 4.95)
    rect(s, x, 1.7, 3.95, 0.5, fill=col, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + 0.15, 1.72, 3.6, 0.46, name, size=18, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    pic = picture(s, img, x + 0.15, 2.35, w=3.65)
    if pic.height > Inches(2.0):  # keep only the top of tall screenshots
        ratio = Inches(2.0) / pic.height
        pic.crop_bottom = 1 - ratio
        pic.height = Inches(2.0)
    bullets(s, x + 0.2, 4.55, 3.65, pts, size=13, gap=7, dot=col)
footer(s, 3)

# =====================================================================
# 4. Claim journey
# =====================================================================
s = new_slide(notes=(
    "Walk the six stages left to right. Point out who acts at each stage. The AI only handles the first stage: it checks the clause and "
    "confirms the incident is covered; humans own inspection and money. On the right is the real claim page: the stepper, the documents "
    "still needed, and the collision data the car sent automatically."))
title(s, "One claim, six stages, always visible", "Who acts at each step, and what the policyholder sees")
stages = [("AI Verified", "Customer + AI", "Clause-cited cover check", INDIGO), ("Pending Adjuster", "Customer", "Books inspection slot", INDIGO),
          ("Inspected", "Adjuster", "Reviews documents, inspects", PURPLE), ("In Review", "Adjuster", "Proposes settlement", PURPLE),
          ("Approved", "Admin", "Approves, sets payout date", GREEN), ("Paid Out", "Admin", "Money sent, claim closed", GREEN)]
for i, (name, who, what, col) in enumerate(stages):
    x = 0.6 + i * 2.03
    ch = rect(s, x, 1.7, 2.05, 0.7, fill=col, shape=MSO_SHAPE.CHEVRON if i else MSO_SHAPE.PENTAGON)
    text(s, x + 0.3, 1.72, 1.55, 0.66, name, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, x + 0.05, 2.5, 1.95, 0.3, who, size=13, bold=True, color=col, align=PP_ALIGN.CENTER)
    text(s, x + 0.05, 2.8, 1.95, 0.55, what, size=12, color=MUTED, align=PP_ALIGN.CENTER)
pic = picture(s, "claim", 0.6, 3.55, w=6.3)
pic.crop_bottom = 1 - (Inches(3.2) / pic.height)  # top part only: stepper, documents
pic.height = Inches(3.2)
card(s, 7.2, 3.55, 5.53, 3.25)
text(s, 7.4, 3.65, 5.1, 0.4, "Visibility at every step", size=18, bold=True)
bullets(s, 7.4, 4.15, 5.2, [
    "“What happens next”: documents, inspection date, payout date",
    "Timeline of every action by customer, adjuster, admin, system",
    "Device evidence flagged “supports claim” for the adjuster",
    "Bell notification on every status change or document review",
    "Admin can reject any open claim with a reason the customer sees",
], size=12, gap=5)
footer(s, 4)

# =====================================================================
# 5. Policyholder experience
# =====================================================================
s = new_slide(notes=(
    "This is Daniel's dashboard, straight from the running app. The four cards are computed from real data: payouts year-to-date only sums "
    "claims actually paid, and the safety score comes from his car's telematics. The purple banner launches the AI assistant. "
    "Reminders are generated by the system: premium due in 5 days, renewal in 21 days, three documents missing."))
title(s, "The policyholder's view", "Daniel Carter's dashboard: live data, not a mock-up")
picture(s, "dashboard", 0.6, 1.6, h=5.3)
notes_ = [
    ("1", "Live KPIs", "Active policies, open claims, payouts paid this year, device-based safety score"),
    ("2", "AI assistant", "Describe the incident, add photos; cover is checked against the policy clauses"),
    ("3", "Proactive reminders", "Premium due, renewal, missing documents, coverage gaps"),
    ("4", "Recent claims", "Status badge, payout and a View Details page for each claim"),
]
for i, (n, head, body) in enumerate(notes_):
    y = 1.6 + i * 1.33
    card(s, 8.3, y, 4.43, 1.2)
    rect(s, 8.45, y + 0.3, 0.55, 0.55, fill=INDIGO, shape=MSO_SHAPE.OVAL)
    text(s, 8.45, y + 0.3, 0.55, 0.55, n, size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 9.15, y + 0.08, 3.5, 0.35, head, size=15, bold=True)
    text(s, 9.15, y + 0.43, 3.5, 0.75, body, size=12, color=MUTED)
footer(s, 5)

# =====================================================================
# 6. Under the hood
# =====================================================================
s = new_slide(notes=(
    "Three things make this credible. First, the AI is boxed in: it can only cite clauses we gave it, the document checklist is fixed code, "
    "and if the model is down the customer still reaches an adjuster. Second, IoT: a device posts to an authenticated endpoint, we match it to the "
    "policy and open claim; each incident lowers the safety score. Third, trust: roles, ownership checks, hashed passwords and 68 automated tests."))
title(s, "Under the hood: trustworthy AI and evidence", "AI that is boxed in, evidence that arrives by itself")
picture(s, "devices", 0.6, 1.6, w=6.0)
img_h = 6.0 * (Image.open(IMG["devices"]).height / Image.open(IMG["devices"]).width)
text(s, 0.6, 1.6 + img_h + 0.05, 6.0, 0.4, "Telematics & IoT: score and readings per connected asset", size=12, color=MUTED)
stack_y = 1.6 + img_h + 0.6
text(s, 0.6, stack_y, 6.0, 0.35, "Tech stack", size=14, bold=True)
for i, (name, col) in enumerate([("React + TypeScript", INDIGO), ("FastAPI", GREEN), ("SQLAlchemy", PURPLE), ("LLM client (mock / real)", AMBER)]):
    cx, cy = 0.6 + (i % 2) * 3.05, stack_y + 0.45 + (i // 2) * 0.62
    rect(s, cx, cy, 2.9, 0.5, fill=CARD, line=col, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
    text(s, cx, cy, 2.9, 0.5, name, size=13, bold=True, color=col, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
blocks = [
    ("AI guardrails", INDIGO, ["Cover verdict must cite a real policy clause, otherwise rejected", "Document checklist is deterministic, not LLM-generated", "LLM failure falls back safely; the adjuster path still works"]),
    ("Connected evidence", GREEN, ["Car, home sensor and wearable post to a key-protected API", "Matched to the policy and open claim; adjuster is alerted", "Each incident lowers the safety score (last 90 days)"]),
    ("Trust & quality", PURPLE, ["Role + ownership checks, scrypt hashes, login lockout", "68 automated tests incl. full claim-to-payout lifecycle", "Mock LLM mode gives a deterministic, offline demo"]),
]
for i, (head, col, pts) in enumerate(blocks):
    y = 1.6 + i * 1.78
    card(s, 6.95, y, 5.78, 1.65, accent=col)
    text(s, 7.2, y + 0.07, 5.4, 0.35, head, size=16, bold=True, color=col)
    bullets(s, 7.2, y + 0.5, 5.4, pts, size=12, gap=3, dot=col)
footer(s, 6)

# =====================================================================
# 7. Demo script
# =====================================================================
s = new_slide(dark=True, notes=(
    "Suggested 8-10 minute flow. Start the backend and frontend beforehand (see README). The demo database resets on every backend restart, "
    "so you can always get back to this exact starting state. If the live LLM is slow, set LLM_PROVIDER=mock for a deterministic run."))
title(s, "Live demo: follow one claim across all three roles", "Credentials are also in CREDENTIALS.md  ·  http://localhost:5173", dark=True)
steps = [
    ("1", "Policyholder", "daniel.carter", "Daniel@123", "Dashboard, reminders; open CLM-000002 and upload a missing document", INDIGO),
    ("2", "Policyholder", "daniel.carter", "Daniel@123", "File New Claim: describe a collision, see the clause-cited cover check, start the claim", INDIGO),
    ("3", "Policyholder", "daniel.carter", "Daniel@123", "Telematics & IoT: simulate a Collision; it attaches to the claim, safety score drops", INDIGO),
    ("4", "Adjuster", "asha.verma", "Asha@123", "Calendar with Daniel's booking; verify documents, record inspection, propose settlement", PURPLE),
    ("5", "Admin", "admin", "Admin@123", "Claims: approve a proposed settlement (e.g. CLM-000003), then mark one paid out", GREEN),
    ("6", "Policyholder", "arjun.mehta", "Arjun@123", "Log in: status moved to Approved with a payout date, plus a bell notification", INDIGO),
]
for i, (n, role, user, pw, what, col) in enumerate(steps):
    y = 1.6 + i * 0.82
    rect(s, 0.6, y, 12.13, 0.72, fill=RGBColor(0x1E, 0x24, 0x35), line=RGBColor(0x33, 0x3B, 0x52), shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12)
    rect(s, 0.75, y + 0.14, 0.48, 0.48, fill=col, shape=MSO_SHAPE.OVAL)
    text(s, 0.75, y + 0.14, 0.48, 0.48, n, size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 1.4, y + 0.06, 1.7, 0.64, role, size=14, bold=True, color=WHITE, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 3.1, y + 0.06, 2.3, 0.64, [[(user, {"bold": True, "color": RGBColor(0x9D, 0xB4, 0xFF)})], [(pw, {"color": RGBColor(0xA8, 0xB1, 0xC8), "size": 12})]], size=13, anchor=MSO_ANCHOR.MIDDLE, spacing=1.0)
    text(s, 5.5, y + 0.06, 7.1, 0.64, what, size=13, color=RGBColor(0xDD, 0xE3, 0xF3), anchor=MSO_ANCHOR.MIDDLE)
text(s, 0.6, 6.6, 12.1, 0.4, "Result: one claim, three roles, every step visible to the customer, from AI check to payout.", size=15, bold=True, color=WHITE)
footer(s, 7, dark=True)

OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides))
