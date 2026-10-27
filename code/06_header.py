"""Step 6: render ../header.png (1200x630 social card) with Playwright Chromium.
Right: the real places of West Penwith with every line of five or more that the count finds (ochre).
Fonts: FONT_DIR with Fraunces, Source Serif 4 and IBM Plex Mono TTFs (github.com/google/fonts); else system serif.
"""
import os, json, math
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
S = json.load(open(os.path.join(ROOT, "work", "site.json"))); R = S["R"]; g = S["reg"]["penwith"]
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts")
COL = ["#1F6F78", "#6E4C8F", "#9A6A2A", "#B0452F", "#2F6DA3", "#8E877A"]
(la0, lo0), (la1, lo1) = g["box"]; k = math.cos(math.radians((la0 + la1) / 2))
X = lambda lo: (lo - lo0) * k; Y = lambda la: (la1 - la)
sc = 560 / max(X(lo1), Y(la0))
pts = [(X(p[1]) * sc, Y(p[0]) * sc, p[2]) for p in g["p"]]
lines = "".join(f'<line x1="{pts[a][0]:.1f}" y1="{pts[a][1]:.1f}" x2="{pts[b][0]:.1f}" y2="{pts[b][1]:.1f}" stroke="#B7741C" stroke-width="{2.4 if n >= 6 else 1.3}" opacity="{.95 if n >= 6 else .6}" stroke-linecap="round"/>'
                for a, b, n in g["lines"] if n >= 5)
dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{COL[t]}" stroke="#F4EEE1" stroke-width="1"/>' for x, y, t in pts)
ff = "".join(f"@font-face{{font-family:'{n}';src:url('file://{FD}/{f}');font-weight:{w};}}" for n, f, w in [
    ("Fraunces", "FrauncesVar.ttf", "100 900"), ("Source Serif 4", "SourceSerif4-Regular.ttf", "400"),
    ("IBM Plex Mono", "IBMPlexMono-Regular.ttf", "400"), ("IBM Plex Mono", "IBMPlexMono-Medium.ttf", "500")]) if os.path.isdir(FD) else ""
h = R["headline"]
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{ff}
body{{margin:0;width:1200px;height:630px;background:#F4EEE1;color:#25221C;overflow:hidden;position:relative;font-family:'Source Serif 4',Georgia,serif}}
.k{{position:absolute;left:64px;top:70px;font:500 15px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#6B6457;display:flex;gap:12px;align-items:center}}
.k b{{background:#7A4A12;color:#F4EEE1;padding:7px 9px;font-weight:500}}
h1{{position:absolute;left:60px;top:112px;margin:0;font:900 104px/.9 Fraunces,Georgia,serif;letter-spacing:-.02em;font-variation-settings:"SOFT" 50;width:600px}}
h1 em{{font-style:normal;color:#B7741C}}
p{{position:absolute;left:64px;top:345px;width:540px;margin:0;font-size:25px;line-height:1.36;color:#33302A}}
.f{{position:absolute;left:64px;bottom:40px;font:400 14px/1 'IBM Plex Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#7C7466}}
svg.m{{position:absolute;right:30px;top:22px}} .cap{{position:absolute;right:34px;bottom:14px;font:400 13px/1.3 'IBM Plex Mono',monospace;color:#6B6457;text-align:right}}
</style></head><body>
<div class="k"><b>Data study</b><span>Britain's ancient sites</span></div>
<h1>Ley lines, <em>tested</em></h1>
<p>{h['sites']:,} old sites, four landscapes and the Saint Michael's line, against random points. Straight lines appear wherever sites crowd together.</p>
<div class="f">Dr Tristan Hotham · Independent researcher</div>
<svg class="m" width="560" height="560" viewBox="0 0 560 560"><rect width="560" height="560" fill="#FBF7EE" stroke="#C9BEA6"/>{lines}{dots}</svg>
<div class="cap">West Penwith: every line of five or more places</div>
</body></html>"""
tmp = os.path.join(ROOT, "work", "header.html"); open(tmp, "w").write(html)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto("file://" + os.path.abspath(tmp)); pg.wait_for_timeout(600)
    pg.screenshot(path=os.path.join(ROOT, "header.png")); b.close()
print("header.png written")
