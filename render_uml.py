"""Renders uml/*.mmd to uml/out/*.svg and *.png with headless Edge + Mermaid (pinned, loaded from jsDelivr).

Usage: python render_uml.py
"""
import html
import json
import re
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
SRC, OUT = HERE / "uml", HERE / "uml" / "out"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"

PAGE = """<!doctype html><meta charset="utf-8"><body style="margin:0;background:#fff">
<div id="out"></div><pre id="svgsrc"></pre>
<script src="%(lib)s"></script>
<script>
mermaid.initialize({startOnLoad: false, theme: "default", securityLevel: "loose",
  flowchart: {htmlLabels: false, curve: "basis", useMaxWidth: false}, sequence: {useMaxWidth: false, mirrorActors: false},
  class: {useMaxWidth: false}, state: {useMaxWidth: false}, themeVariables: {fontFamily: "Segoe UI, Arial, sans-serif"}});
mermaid.render("m", %(code)s).then((r) => {
  document.getElementById("out").innerHTML = r.svg;
  document.getElementById("svgsrc").textContent = new XMLSerializer().serializeToString(document.querySelector("#out svg"));
}).catch((e) => { document.getElementById("svgsrc").textContent = "ERROR: " + e.message; });
</script>"""


def edge(*args: str) -> str:
    return subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--hide-scrollbars", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180).stdout


def render(mmd: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "r.html"
        page.write_text(PAGE % {"lib": MERMAID, "code": json.dumps(mmd.read_text(encoding="utf-8"))}, encoding="utf-8")
        dom = edge("--virtual-time-budget=20000", "--dump-dom", page.as_uri())
        m = re.search(r'<pre id="svgsrc">(.*?)</pre>', dom, re.S)
        svg = html.unescape(m.group(1)) if m else ""
        if not svg.startswith("<svg"):
            raise SystemExit(f"{mmd.name}: render failed: {svg[:300] or 'no output'}")
        if 'xmlns="http://www.w3.org/2000/svg"' not in svg[:300]:
            svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
        (OUT / f"{mmd.stem}.svg").write_text(svg, encoding="utf-8")

        svg_to_png(svg, OUT / f"{mmd.stem}.png")


def svg_to_png(svg: str, png: Path) -> None:
    """Screenshot an SVG at 2x; the headless viewport is smaller than --window-size, hence the extra margin."""
    vb = re.search(r'viewBox="([-\d.\s]+)"', svg)
    _, _, w, h = (float(v) for v in vb.group(1).split()) if vb else (0, 0, 1600, 1000)
    with tempfile.TemporaryDirectory() as tmp:
        shot = Path(tmp) / "s.html"
        shot.write_text(f'<!doctype html><body style="margin:0;background:#fff"><div style="padding:16px;width:{w:.0f}px">{svg}</div>', encoding="utf-8")
        edge(f"--window-size={int(w) + 120},{int(h) + 160}", "--force-device-scale-factor=2", f"--screenshot={png}", shot.as_uri())
    print(f"{png.stem}: {int(w)}x{int(h)}  png {png.stat().st_size // 1024} KB")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for f in sorted(SRC.glob("*.mmd")):
        render(f)
