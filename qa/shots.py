#!/usr/bin/env python
"""Screenshot the figure at the review widths, and print the in-page audits.

  python qa/shots.py                 # default state
  python qa/shots.py tsl             # shortage-list only
  python qa/shots.py occ="Welder or flamecutter"

Writes qa/shots/<state>-<width>.png.
"""
from __future__ import annotations
import functools, http.server, socketserver, sys, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # legend text is not cp1252

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "qa" / "shots"
WIDTHS = [320, 390, 700, 768, 1200]

setup, label = "", "default"
for arg in sys.argv[1:]:
    if arg == "tsl":
        setup, label = "document.getElementById('tslOnly').click();", "tsl"
    elif arg.startswith("occ="):
        name = arg[4:]
        setup = (f"const s=document.getElementById('occSelect');s.value={name!r};"
                 "s.dispatchEvent(new Event('change'));")
        label = "occ"
    elif arg.startswith("rqf="):
        setup = (f"document.querySelector('[data-rqf=\"{arg[4:]}\"]').click();")
        label = "rqf"

OUT.mkdir(parents=True, exist_ok=True)
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(REPO))
handler.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]

AUDIT = r"""() => {
  const out = {};
  const panel = document.querySelector('.controls');
  const pb = panel.getBoundingClientRect();
  out.outside = [...panel.children].filter(n => {
    const b = n.getBoundingClientRect();
    return b.left < pb.left - 1 || b.right > pb.right + 1 || b.top < pb.top - 1 || b.bottom > pb.bottom + 1;
  }).length;
  out.clippedText = [...panel.querySelectorAll('button,label,select')]
    .filter(n => n.scrollWidth > n.clientWidth + 1 || n.scrollHeight > n.clientHeight + 1)
    .map(n => n.textContent.trim().slice(0, 40));
  const t = [...document.querySelectorAll('svg text')];
  out.svgText = t.length;
  out.pageOverflow = document.documentElement.scrollWidth - document.documentElement.clientWidth;
  out.inputsUnder16 = [...document.querySelectorAll('input:not([type=checkbox]),textarea')]
    .filter(n => parseFloat(getComputedStyle(n).fontSize) < 16).map(n => n.id);
  const heights = new Set([...panel.querySelectorAll('.segmented,.plain-select')]
    .map(n => Math.round(n.getBoundingClientRect().height)));
  out.controlHeights = [...heights];
  const sel = document.getElementById('occSelect');
  out.selectHasMatch = [...sel.options].some(o => o.value === sel.value);
  out.notesSourceCount = (document.getElementById('notes').textContent.match(/Source:/g) || []).length;
  out.subtitle = document.getElementById('vizSub').textContent;
  out.legend = document.getElementById('scaleLegend').textContent;
  out.bodyHeight = Math.round(document.body.getBoundingClientRect().height);
  return out;
}"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    for w in WIDTHS:
        page = browser.new_page(viewport={"width": w, "height": 900})
        errs = []
        page.on("pageerror", lambda e: errs.append("pageerror: " + str(e)))
        page.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" else None)
        page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="load")
        page.wait_for_function("() => window.CGD_READY === true", timeout=15000)
        if setup:
            page.evaluate(setup)
        page.evaluate("document.fonts && document.fonts.ready")
        page.wait_for_timeout(250)
        page.screenshot(path=str(OUT / f"{label}-{w}.png"), full_page=True)
        print(f"--- {label} @ {w}px", page.evaluate(AUDIT))
        if errs:
            print("    ERRORS:", errs)
        page.close()
    browser.close()
srv.shutdown()
print("shots in", OUT)
