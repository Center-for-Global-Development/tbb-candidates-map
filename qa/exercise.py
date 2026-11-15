#!/usr/bin/env python
"""State exercise for the TBB candidates map (SKILL.md §F step 4).

Drives every filter, the selection, the country drill-down, the keyboard route
and a resize while the drill-down is open, and checks the figure against the
payload each time — so a stale selection, a stale occupation list or a frame
that grows but never shrinks fails here rather than in review.

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


def in_band(o, band):
    if band == "ALL":
        return True
    return o["t"] == "Yes" if band == "TSL" else o["r"] == band


def expected(band="ALL", occ=None):
    rows = [o for o in OCCS if in_band(o, band) and (occ is None or o["n"] == occ)]
    totals = [sum(o["v"][i] for o in rows) for i in range(len(COUNTRIES))]
    return sum(totals), len(rows)


def expected_country(cid, band="ALL"):
    """Occupation rows for one country, as the drill-down should list them."""
    i = [c["id"] for c in COUNTRIES].index(cid)
    rows = [o for o in OCCS if in_band(o, band) and o["v"][i] > 0]
    return sum(o["v"][i] for o in rows), len(rows)


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
UNIV = "() => window.TBB_MAP.universe()"
BAND = "() => window.TBB_MAP.state.band"
OPTS = "() => document.getElementById('occSelect').options.length - 1"
SEL = "() => window.TBB_MAP.state.selected"
OUTLINES = "() => document.querySelectorAll('#map .outline').length"
HEIGHT = "() => Math.round(document.body.getBoundingClientRect().height)"
DRILL = "() => !document.getElementById('drill').hidden"
DROWS = "() => document.querySelectorAll('.occ-row').length"
TITLE = "() => document.getElementById('drillTitle').textContent"
PRESSED = ("() => [...document.querySelectorAll('#bandToggle button')]"
           ".filter(b => b.getAttribute('aria-pressed') === 'true').length")
SORTED = ("() => { const v = [...document.querySelectorAll('.occ-row .vl')]"
          ".map(e => +e.textContent.replace(/,/g, '')); "
          "return v.every((x, i) => !i || v[i - 1] >= x); }")
TIP_HIDDEN = "() => document.getElementById('tooltip').hidden"
ACTIVE_ID = "() => document.activeElement.getAttribute('data-id')"

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
    check("share denominator is the whole catalogue", page.evaluate(UNIV), expected()[0])

    print("occupation band: RQF 6+")
    page.click('[data-band="RQF 6+"]')
    check("total", page.evaluate(TOTAL), expected("RQF 6+")[0])
    check("occupations offered", page.evaluate(OPTS), expected("RQF 6+")[1])
    check("denominator unchanged by the band", page.evaluate(UNIV), expected()[0])

    print("pick an occupation, then move the band")
    page.select_option("#occSelect", "Nursing")
    check("total", page.evaluate(TOTAL), expected("RQF 6+", occ="Nursing")[0])
    check("denominator is that occupation", page.evaluate(UNIV), expected(occ="Nursing")[0])
    page.click('[data-band="RQF 1-2"]')
    check("occupation reset (Nursing is not RQF 1-2)",
          page.evaluate("() => window.TBB_MAP.state.occ"), "ALL")
    check("total", page.evaluate(TOTAL), expected("RQF 1-2")[0])

    print("shortage list is one of the bands, not a second control")
    page.click('[data-band="TSL"]')
    check("total", page.evaluate(TOTAL), expected("TSL")[0])
    check("exactly one band pressed", page.evaluate(PRESSED), 1)
    check("occupations offered", page.evaluate(OPTS), expected("TSL")[1])
    check("every one of them is RQF 3-5",
          page.evaluate("() => window.TBB_MAP.view().rows.every(o => o.r === 'RQF 3-5')"), True)
    page.click('[data-band="ALL"]')
    check("back to all", page.evaluate(TOTAL), expected()[0])

    print("clicking a country opens its detail")
    # A real pointer click, on a country whose bounding-box centre is inside its
    # own border: Playwright aims at the box centre, which for an L-shaped or
    # tiny country lands on a neighbour. Small countries are covered below,
    # through the select and through the keyboard.
    page.click('#map [data-id="818"]')                      # Egypt
    check("selected", page.evaluate(SEL), "818")
    check("one outline drawn", page.evaluate(OUTLINES), 1)
    check("detail open", page.evaluate(DRILL), True)
    check("named", page.evaluate(TITLE), "Egypt")
    check("rows listed", page.evaluate(DROWS), expected_country("818")[1])
    check("largest first", page.evaluate(SORTED), True)
    check("focus moved into the card", page.evaluate("() => document.activeElement.id"), "drillClose")

    print("the card's band control is its own")
    page.click('#occBand [data-band="TSL"]')
    check("rows", page.evaluate(DROWS), expected_country("818", "TSL")[1])
    check("map underneath unchanged", page.evaluate(TOTAL), expected()[0])
    check("map band unchanged", page.evaluate(BAND), "ALL")

    print("resize with the card open")
    tall = page.evaluate(HEIGHT)
    page.set_viewport_size({"width": 360, "height": 900})
    page.wait_for_timeout(300)
    check("card survives resize", page.evaluate(DRILL), True)
    check("selection survives resize", page.evaluate(SEL), "818")
    check("still exactly one outline", page.evaluate(OUTLINES), 1)
    narrow = page.evaluate(HEIGHT)
    check("frame grows when narrow", narrow > tall, True)
    page.set_viewport_size({"width": 1100, "height": 900})
    page.wait_for_timeout(300)
    check("frame shrinks again", page.evaluate(HEIGHT) <= tall + 2, True)

    print("escape closes one layer at a time")
    page.keyboard.press("Escape")
    check("card closed", page.evaluate(DRILL), False)
    check("selection still there", page.evaluate(SEL), "818")
    check("focus returned to the map", page.evaluate(ACTIVE_ID), "818")
    page.keyboard.press("Escape")
    check("selection cleared", page.evaluate(SEL), None)
    check("no outline left", page.evaluate(OUTLINES), 0)
    check("tooltip hidden", page.evaluate(TIP_HIDDEN), True)

    print("find a country reaches the same detail")
    page.select_option("#countrySelect", "422")             # Lebanon
    check("selected", page.evaluate(SEL), "422")
    check("outline drawn for a dilated small country", page.evaluate(OUTLINES), 1)
    check("detail open", page.evaluate(DRILL), True)
    check("rows", page.evaluate(DROWS), expected_country("422")[1])
    page.click("#drillClose")
    check("closed by the button", page.evaluate(DRILL), False)
    page.select_option("#countrySelect", "")
    check("cleared", page.evaluate(SEL), None)

    print("clicking outside the card closes it")
    page.click('#map [data-id="818"]')
    page.click("#drill", position={"x": 8, "y": 8})
    check("closed", page.evaluate(DRILL), False)
    page.keyboard.press("Escape")

    print("a filter change does not leave a stale tooltip")
    page.click('[data-band="RQF 3-5"]')
    check("tooltip hidden", page.evaluate(TIP_HIDDEN), True)
    check("total", page.evaluate(TOTAL), expected("RQF 3-5")[0])
    page.click('[data-band="ALL"]')

    print("keyboard route")
    page.evaluate('() => document.querySelector(\'#map [data-id="050"]\').focus()')
    check("focus reaches a country", page.evaluate(ACTIVE_ID), "050")
    check("it has an accessible name",
          page.evaluate("() => /Bangladesh: [\\d,]+ candidates, one of the seven/"
                        ".test(document.activeElement.getAttribute('aria-label'))"), True)
    page.keyboard.press("Enter")
    check("enter opens the detail", page.evaluate(DRILL), True)
    check("for the focused country", page.evaluate(TITLE), "Bangladesh")
    page.keyboard.press("Escape")

    if errors:
        failures.append("console errors")
        print("\nCONSOLE/PAGE ERRORS:")
        for e in errors:
            print("   -", e)
    browser.close()
srv.shutdown()

print("\n" + ("FAILED: " + ", ".join(failures) if failures else "PASS: state exercise clean."))
sys.exit(1 if failures else 0)
