"""Draws the UML use case diagram as SVG (Mermaid has no real use case notation) and renders it to PNG.

Usage (from demo_deck): python uml/gen_use_case.py
"""
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from render_uml import svg_to_png  # noqa: E402

W, H = 1700, 880
BLUE, GREEN, INK, MUTED = "#2F5BEA", "#12805C", "#1C2333", "#667085"
parts: list[str] = []


def add(s: str) -> None:
    parts.append(s)


def text(x, y, lines, size=13, anchor="middle", weight="400", fill=INK):
    lines = lines.split("\n")
    y0 = y - (len(lines) - 1) * size * 0.6
    for i, ln in enumerate(lines):
        add(f'<text x="{x}" y="{y0 + i * size * 1.2:.1f}" text-anchor="{anchor}" dominant-baseline="middle" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}">{escape(ln)}</text>')


def usecase(x, y, label, color=BLUE, fill="#EEF2FF", rx=105):
    add(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="29" fill="{fill}" stroke="{color}" stroke-width="1.5"/>')
    text(x, y, label)
    return x, y


def actor(x, y, name):
    add(f'<g stroke="{INK}" stroke-width="2" fill="none"><circle cx="{x}" cy="{y - 38}" r="10"/><line x1="{x}" y1="{y - 28}" x2="{x}" y2="{y + 6}"/>'
        f'<line x1="{x - 18}" y1="{y - 18}" x2="{x + 18}" y2="{y - 18}"/><line x1="{x}" y1="{y + 6}" x2="{x - 14}" y2="{y + 30}"/>'
        f'<line x1="{x}" y1="{y + 6}" x2="{x + 14}" y2="{y + 30}"/></g>')
    text(x, y + 46, name, size=13, weight="600")


def band(y0, y1, title, color):
    add(f'<rect x="215" y="{y0}" width="1230" height="{y1 - y0}" rx="8" fill="{color}" fill-opacity="0.07" stroke="{color}" stroke-width="1.2"/>')
    text(230, y0 + 16, f"«package» {title}", size=13, anchor="start", weight="700", fill=color)


def line(x1, y1, x2, y2, dashed=False, arrow=False, label=None, color=INK, t=0.5):
    dash = ' stroke-dasharray="6 4"' if dashed else ""
    marker = ' marker-end="url(#arr)"' if arrow else ""
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.4"{dash}{marker}/>')
    if label:
        mx, my = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        add(f'<rect x="{mx - 30}" y="{my - 9}" width="60" height="18" fill="#fff"/>')
        text(mx, my, label, size=11, fill=MUTED)


add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Segoe UI, Arial, sans-serif">')
add('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
    f'<path d="M0 0 L10 5 L0 10 z" fill="{INK}"/></marker></defs>')
add(f'<rect width="{W}" height="{H}" fill="#fff"/>')
add(f'<rect x="200" y="20" width="1260" height="820" rx="10" fill="none" stroke="{INK}" stroke-width="2"/>')
text(212, 36, "InsureNdClaim", size=15, anchor="start", weight="700")

# ---- packages ----
band(55, 315, "Policyholder", BLUE)
band(335, 485, "System", GREEN)
band(505, 655, "Adjuster", "#6A3DE8")
band(675, 825, "Admin", "#12805C")

R1, R2 = 135, 250
login = usecase(335, R1, "Log in /\nchange password")
file_ = usecase(583, R1, "File claim with\nAI assistant")
dash = usecase(831, R1, "View dashboard\nKPIs, reminders, score")
upload = usecase(1079, R1, "Upload claim\ndocuments")
track = usecase(1327, R1, "Track claim\nstepper, timeline, next steps")
usecase(459, R2, "Browse adjuster directory\nand book consultation")
usecase(707, R2, "View policies\nand coverage")
evid = usecase(955, R2, "View device evidence\nattach to claim")
usecase(1203, R2, "Manage settings\nnotification preferences")

S = 410
cov = usecase(583, S, "Check coverage\nclause-cited verdict", GREEN, "#E6F6EF")
ingest = usecase(1327, S, "Ingest device event", GREEN, "#E6F6EF")
notif = usecase(955, S, "Send notification", GREEN, "#E6F6EF")

A = 580
usecase(335, A, "Manage\navailability slots", "#6A3DE8", "#F1ECFE")
usecase(583, A, "View calendar\nand bookings", "#6A3DE8", "#F1ECFE")
review = usecase(831, A, "Review documents\nverify / reject", "#6A3DE8", "#F1ECFE")
usecase(1079, A, "Record inspection", "#6A3DE8", "#F1ECFE")
usecase(1327, A, "Propose settlement", "#6A3DE8", "#F1ECFE")

M = 750
usecase(345, M, "Oversee all claims", GREEN, "#E6F6EF", 92)
usecase(550, M, "Assign adjuster", GREEN, "#E6F6EF", 92)
usecase(755, M, "Manage accounts", GREEN, "#E6F6EF", 92)
decide = usecase(955, M, "Approve / reject /\npay settlement", GREEN, "#E6F6EF", 92)
usecase(1150, M, "Send reminders", GREEN, "#E6F6EF", 92)
usecase(1335, M, "View AI and\nHTTP logs", GREEN, "#E6F6EF", 92)

# ---- actors and associations (actor → package) ----
actor(100, 190, "Policyholder")
line(130, 185, 215, 185)
actor(100, 580, "Adjuster")
line(130, 575, 215, 575)
actor(100, 750, "Admin")
line(130, 745, 215, 745)
actor(100, 410, "LLM gateway")
line(130, 405, cov[0] - 105, cov[1])
actor(1590, 410, "Connected device\n(car · home · wearable)".split("\n")[0])
text(1590, 478, "car · home sensor · wearable", size=11, fill=MUTED)
line(1560, 405, ingest[0] + 105, ingest[1])

# ---- «include» / «extend» ----
line(file_[0], file_[1] + 29, cov[0], cov[1] - 29, dashed=True, arrow=True, label="«include»", t=0.75)
line(ingest[0] - 40, ingest[1] - 27, evid[0] + 20, evid[1] + 28, dashed=True, arrow=True, label="«extend»")
line(review[0] + 40, review[1] - 27, notif[0] - 40, notif[1] + 27, dashed=True, arrow=True, label="«include»")
line(decide[0], decide[1] - 29, notif[0], notif[1] + 29, dashed=True, arrow=True, label="«include»", t=0.2)
add("</svg>")

svg = "\n".join(parts)
out = HERE / "out"
out.mkdir(exist_ok=True)
(out / "01_use_case.svg").write_text(svg, encoding="utf-8")
svg_to_png(svg, out / "01_use_case.png")
