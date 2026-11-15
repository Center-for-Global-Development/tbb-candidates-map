#!/usr/bin/env python
"""State exercise for the TBB candidates map (SKILL.md §F step 4).

Drives every filter, the selection, the keyboard route and a resize while a
selection is open, and checks the figure against the payload each time — so a
stale selection, a stale occupation list or a frame that grows but never
shrinks fails here rather than in review.

  python qa/exercise.py
"""
from __future__ import annotations
import functools, http.server, json, socketserver, sys, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REPO = Path(__file__).resolve().parent.parent

raw = (REPO / "data" / "tbb-candidates-data.js").read_text(encoding="utf-8")
DATA = json.loads(raw[raw.index("=") + 1:].rstrip().rstrip(";"))
OCCS, COUNTRIES = DATA["occupations"], DATA["countries"]


def expected(rqf=None, tsl=False, occ=None):
    rows = [o for o in OCCS
            if (not tsl or o["t"] == "Yes")
            and (rqf is None or o["r"] == rqf)
            and (occ is None or o["n"] == occ)]
    totals = [sum(o["v"][i] for o in rows) for i in range(len(COUNTRIES))]
    return sum(totals), len(rows)


failures = []


def check(name, got, want):
    ok = got == want
    print(("  ok   " if ok else "  FAIL ") + name + f"  got={got!r} want={want!r}")
    if not ok:
        failures.append(name)


handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(REPO))
handler.log_message = lambda *a, **k: None
srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
port = srv.server_address[1]

TOTAL = "() => window.TBB_MAP.view().total"
POOL = "() => window.TBB_MAP.view().rows.length"
OPTS = "() => document.getElementById('occSelect').options.length - 1"
SEL = "() => window.TBB_MAP.state.selected"
OUTLINES = "() => document.querySelectorAll('#map .outline').length"
HEIGHT = "() => Math.round(document.body.getBoundingClientRect().height)"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1100, "height": 900})
    errors = []
    page.on("pageerror", lambda e: errors.append("pageerror: " + str(e)))
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="load")
    page.wait_for_function("() => window.CGD_READY === true", timeout=15000)

    print("default")
    check("total", page.evaluate(TOTAL), expected()[0])
    check("occupations offered", page.evaluate(OPTS), expected()[1])
    check("no selection", page.evaluate(SEL), None)

    print("skill level RQF 6+")
    page.click('[data-rqf="RQF 6+"]')
    check("total", page.evaluate(TOTAL), expected(rqf="RQF 6+")[0])
    check("occupations offered", page.evaluate(OPTS), expected(rqf="RQF 6+")[1])

    print("pick an occupation, then widen the skill filter")
    page.select_option("#occSelect", "Nursing")
    check("total", page.evaluate(TOTAL), expected(rqf="RQF 6+", occ="Nursing")[0])
    page.click('[data-rqf="RQF 1-2"]')
    check("occupation reset (Nursing is not RQF 1-2)", page.evaluate("() => window.TBB_MAP.state.occ"), "ALL")
    check("total", page.evaluate(TOTAL), expected(rqf="RQF 1-2")[0])

    print("shortage list only")
    page.click("#tslOnly")
    check("total", page.evaluate(TOTAL), expected(tsl=True)[0])
    check("skill filter reset", page.evaluate("() => window.TBB_MAP.state.rqf"), "ALL")
    check("skill buttons disabled",
          page.evaluate("() => [...document.querySelectorAll('#skillToggle button')].every(b => b.disabled)"), True)
    check("occupations offered", page.evaluate(OPTS), expected(tsl=True)[1])
    check("every band is RQF 3-5",
          page.evaluate("() => window.TBB_MAP.view().rows.every(o => o.r === 'RQF 3-5')"), True)

    print("shortage list off again")
    page.click("#tslOnly")
    check("total back to all", page.evaluate(TOTAL), expected()[0])
    check("skill buttons live",
          page.evaluate("() => [...document.querySelectorAll('#skillToggle button')].some(b => b.disabled)"), False)

    print("selection")
    # A real pointer click, on a country whose bounding-box centre is inside its
    # own border: Playwright aims at the box centre, which for an L-shaped or
    # tiny country lands on a neighbour. Small countries are covered below,
    # through the select and through the keyboard.
    page.click('#map [data-id="818"]')                      # Egypt
    check("selected", page.evaluate(SEL), "818")
    check("one outline drawn", page.evaluate(OUTLINES), 1)
    check("tooltip shown", page.evaluate("() => !document.getElementById('tooltip').hidden"), True)
    tall = page.evaluate(HEIGHT)
    page.set_viewport_size({"width": 360, "height": 900})    # resize with detail open
    page.wait_for_timeout(300)
    check("selection survives resize", page.evaluate(SEL), "818")
    check("still exactly one outline", page.evaluate(OUTLINES), 1)
    narrow = page.evaluate(HEIGHT)
    check("frame grows when narrow", narrow > tall, True)
    page.set_viewport_size({"width": 1100, "height": 900})
    page.wait_for_timeout(300)
    check("frame shrinks again", page.evaluate(HEIGHT) <= tall + 2, True)

    print("clearing")
    page.keyboard.press("Escape")
    check("escape clears selection", page.evaluate(SEL), None)
    check("no outline left", page.evaluate(OUTLINES), 0)
    check("tooltip hidden", page.evaluate("() => document.getElementById('tooltip').hidden"), True)

    print("find a country")
    page.select_option("#countrySelect", "422")             # Lebanon
    check("selected", page.evaluate(SEL), "422")
    check("outline drawn for a dilated small country", page.evaluate(OUTLINES), 1)
    page.select_option("#countrySelect", "")
    check("cleared", page.evaluate(SEL), None)

    print("filter change clears a stale selection's tooltip")
    page.click('#map [data-id="818"]')                      # Egypt
    page.click('[data-rqf="RQF 3-5"]')
    check("tooltip not left pinned", page.evaluate("() => document.getElementById('tooltip').hidden"), True)
    check("total", page.evaluate(TOTAL), expected(rqf="RQF 3-5")[0])

    print("keyboard route")
    page.evaluate("() => document.querySelector('#map [data-id=\"050\"]').focus()")
    check("focus reaches a country", page.evaluate("() => document.activeElement.getAttribute('data-id')"), "050")
    check("it has an accessible name",
          page.evaluate("() => /Bangladesh: [\\d,]+ candidates, one of the seven/.test(document.activeElement.getAttribute('aria-label'))"), True)

    if errors:
        failures.append("console errors")
        print("\nCONSOLE/PAGE ERRORS:")
        for e in errors:
            print("   -", e)
    browser.close()
srv.shutdown()

print("\n" + ("FAILED: " + ", ".join(failures) if failures else "PASS: state exercise clean."))
sys.exit(1 if failures else 0)
