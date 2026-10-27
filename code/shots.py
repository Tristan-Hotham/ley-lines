"""Screenshots of the built page for checking (desktop and phone). Not part of the analysis.
Leaflet is served from a local copy (LEAFLET_DIR) because the test machine cannot reach the CDN."""
import os, sys
from playwright.sync_api import sync_playwright
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."); out = os.path.join(ROOT, "_shots"); os.makedirs(out, exist_ok=True)
LD = os.environ.get("LEAFLET_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/leaflet/dist")
views = sys.argv[1:] or []
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, vw, vh in (("desk", 1280, 900), ("phone", 390, 844)):
        pg = b.new_page(viewport={"width": vw, "height": vh}, device_scale_factor=1)
        pg.route("**/leaflet.min.js", lambda r: r.fulfill(path=os.path.join(LD, "leaflet.js")))
        pg.route("**/leaflet.min.css", lambda r: r.fulfill(path=os.path.join(LD, "leaflet.css")))
        pg.route("**/*arcgisonline*/**", lambda r: r.abort()); pg.route("**/fonts.g*/**", lambda r: r.abort())
        msgs = []; pg.on("console", lambda m: msgs.append(m.text)); pg.on("pageerror", lambda e: msgs.append("ERR " + str(e)))
        pg.goto("file://" + os.path.abspath(os.path.join(ROOT, "index.html"))); pg.wait_for_timeout(3000)
        print(name, "scrollWidth", pg.evaluate("document.documentElement.scrollWidth"), "errors", [m for m in msgs if "ERR" in m][:5])
        pg.screenshot(path=os.path.join(out, f"{name}_full.png"), full_page=True)
        for v in views:
            pg.click(f"#views [data-v={v}]"); pg.wait_for_timeout(1200)
            pg.locator("#map").screenshot(path=os.path.join(out, f"{name}_map_{v}.png"))
            if v in ("penwith", "wiltshire"):
                pg.click("#realsim [data-v=sim]"); pg.wait_for_timeout(800)
                pg.locator("#map").screenshot(path=os.path.join(out, f"{name}_map_{v}_sim.png")); pg.click("#realsim [data-v=real]")
    b.close()
