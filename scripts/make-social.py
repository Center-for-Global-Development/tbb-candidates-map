# -*- coding: utf-8 -*-
"""Render social.html to PNGs for social media.

    python scripts/make-social.py

Writes social/*.png at 2x, so the images stay sharp on a retina timeline.
Serves the repo over loopback rather than opening the file directly, because
file:// blocks the data scripts the page loads.
"""
from __future__ import annotations
import functools, http.server, os, socketserver, sys, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "social"
SCALE = 2

# name -> (width, height, subtitle key)
# 1200x675 is the 16:9 that link cards and X both accept without cropping.
# 1200x800 is for a timeline post, where the extra height goes to the map.
SHOTS = [
    ("tbb-map-16x9-brief",     1200, 675, "brief"),
    ("tbb-map-16x9-finding",   1200, 675, "finding"),
    ("tbb-map-natural-brief",  1200, 0,   "brief"),
    ("tbb-map-natural-finding", 1200, 0,  "finding"),
]

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(REPO))
handler.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]

OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch()
    for name, w, h, sub in SHOTS:
        page = browser.new_page(viewport={"width": w, "height": h or 1000},
                                device_scale_factor=SCALE)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        url = f"http://127.0.0.1:{port}/social.html?w={w}&sub={sub}"
        if h:
            url += f"&h={h}"
        page.goto(url, wait_until="load")
        # The page sets this once its webfont has loaded; without it the still
        # can be captured mid-swap and ship in the fallback face.
        page.wait_for_function("() => window.SOCIAL_READY === true", timeout=20000)
        path = OUT / f"{name}.png"
        page.locator("#card").screenshot(path=str(path))
        if errors:
            raise SystemExit("page errors in " + name + ": " + "; ".join(errors))
        got = page.evaluate("() => { const r = document.getElementById('card')"
                            ".getBoundingClientRect(); return [Math.round(r.width),"
                            " Math.round(r.height)]; }")
        print("%-26s %4dx%-4d @%dx  %6.1f KB"
              % (path.name, got[0], got[1], SCALE, os.path.getsize(path) / 1024))
        page.close()
    browser.close()
srv.shutdown()
print("written to", OUT)
