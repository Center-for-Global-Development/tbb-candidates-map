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

    print("row tooltips carry the skill level, and only where it varies")
    check("a tip on every row under All",
          page.evaluate("() => [...document.querySelectorAll('.occ-row')]"
                        ".every(r => /^(RQF [0-9+–-]+|Ineligible)$/.test(r.getAttribute('data-tip') || ''))"), True)
    page.hover(".occ-row")
    page.wait_for_timeout(250)
    check("it shows", page.evaluate("() => { const t = document.querySelector('.cgd-quicktip');"
                                    " return !!t && !t.hidden; }"), True)

    print("the card's band control is its own")
    page.click('#occBand [data-band="TSL"]')
    check("rows", page.evaluate(DROWS), expected_country("818", "TSL")[1])
    check("no tips once the band is fixed",
          page.evaluate("() => [...document.querySelectorAll('.occ-row')]"
                        ".every(r => !r.hasAttribute('data-tip'))"), True)
    check("map underneath unchanged", page.evaluate(TOTAL), expected()[0])
    check("map band unchanged", page.evaluate(BAND), "ALL")

    print("resize with the card open")
    wide_open = page.evaluate(HEIGHT)
    page.set_viewport_size({"width": 360, "height": 900})
    page.wait_for_timeout(300)
    check("card survives resize", page.evaluate(DRILL), True)
    check("selection survives resize", page.evaluate(SEL), "818")
    check("still exactly one outline", page.evaluate(OUTLINES), 1)
    check("the card is inside the figure, not hanging off it",
          page.evaluate("() => { const c = document.querySelector('.cmap-card').getBoundingClientRect();"
                        " const r = document.getElementById('vizRoot').getBoundingClientRect();"
                        " return c.height > 100 && c.top >= r.top - 1 && c.bottom <= r.bottom + 1; }"), True)
    page.set_viewport_size({"width": 1100, "height": 900})
    page.wait_for_timeout(300)
    check("frame returns to the height it had", page.evaluate(HEIGHT), wide_open)
    page.keyboard.press("Escape")
    page.wait_for_timeout(200)

    # The figure is published in a fixed-height iframe, because the cgdev.org
    # parent has no listener for the height it reports. A state that makes the
    # body taller is a state that gets clipped, so opening a country must not
    # change the height at any width. This is what the card stops being a
    # section under the map and becomes an overlay over the whole figure for.
    print("opening a country never changes the frame height")
    for w in (328, 489, 611, 700, 930):
        page.set_viewport_size({"width": w, "height": 1100})
        page.wait_for_timeout(250)
        shut = page.evaluate(HEIGHT)
        page.evaluate("() => window.TBB_MAP.open('422')")
        page.wait_for_timeout(250)
        check("  %dpx wide" % w, page.evaluate(HEIGHT), shut)
        page.keyboard.press("Escape")
        page.wait_for_timeout(150)
    page.keyboard.press("Escape")
    page.set_viewport_size({"width": 1100, "height": 900})
    page.wait_for_timeout(250)
    page.evaluate("() => window.TBB_MAP.open('818')")
    page.wait_for_timeout(250)

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

    print("every country is drawn where it is, at the size it is")
    # The invariant two earlier attempts broke. A stroke in the country's own
    # colour filled every inlet; enlarging the shape about its centre pushed it
    # into its neighbours, so Trinidad and Tobago reached the coast of Venezuela
    # and Lebanon reached into the Mediterranean. Countries tile the plane, so
    # any enlargement takes someone else's territory.
    check("nothing on the map is transformed",
          page.evaluate("() => document.querySelectorAll('#map [transform]').length"), 0)
    check("every path drawn is the payload's own, unmodified",
          page.evaluate("() => [...document.querySelectorAll('#map .country')].every(c =>"
                        " c.getAttribute('d') === window.TBB_GEO.countries[c.getAttribute('data-id')].d)"), True)
    check("every country keeps the ordinary hairline border",
          page.evaluate("() => [...document.querySelectorAll('#map .country')]"
                        ".every(c => getComputedStyle(c).strokeWidth === '0.7px')"), True)
    check("Trinidad and Tobago still has both islands",
          page.evaluate("() => (document.querySelector('#map [data-id=\"780\"]')"
                        ".getAttribute('d').match(/M/g) || []).length"), 2)

    # The direct test of the defect: no country may paint on another's land.
    # Sampled in the browser's own geometry, so it covers all 26 at once rather
    # than the two that happened to be reported.
    #
    # Two things this has to get right. Everything goes through screen space,
    # because isPointInFill works in the element's own user space, before its
    # transform — a test written in user space silently checks the payload
    # rather than the picture, and passed with a 2.2x enlargement put back.
    # And only strictly interior points count: neighbours share a border and
    # both polygons contain it, so a point within a pixel of the coast is
    # inside two countries legitimately.
    SPILL = """() => {
        const svg = document.querySelector('#map svg');
        const cs = [...document.querySelectorAll('#map .country')];
        const ctx = document.querySelector('#map .context');
        const ctm = cs.map(c => c.getScreenCTM());
        const inv = ctm.map(m => m.inverse());
        const back = ctx.getScreenCTM().inverse();
        const at = (el, m, x, y) => {
          const u = svg.createSVGPoint(); u.x = x; u.y = y;
          const q = m ? u.matrixTransform(m) : u;
          const r = svg.createSVGPoint(); r.x = q.x; r.y = q.y;
          return el.isPointInFill(r);
        };
        const RING = [[2,0],[-2,0],[0,2],[0,-2],[1.4,1.4],[-1.4,-1.4]];
        const over = [], onto = [];
        cs.forEach((c, ci) => {
          const bb = c.getBBox();
          const px = 2 / (ctm[ci].a || 1);          // 2 screen px, in user units
          const inner = [];
          for (let t = 0; t < 6000 && inner.length < 25; t++) {
            const x = bb.x + Math.random() * bb.width;
            const y = bb.y + Math.random() * bb.height;
            if (!at(c, null, x, y)) continue;
            if (!RING.every(([dx, dy]) => at(c, null, x + dx * px / 2, y + dy * px / 2))) continue;
            const s = svg.createSVGPoint(); s.x = x; s.y = y;
            inner.push(s.matrixTransform(ctm[ci]));
          }
          if (!inner.length) return;
          cs.forEach((o, oi) => {
            if (o === c) return;
            if (inner.some(s => { const q = s.matrixTransform(inv[oi]);
                                  return at(o, null, q.x, q.y); }))
              over.push(c.getAttribute('data-id') + ' over ' + o.getAttribute('data-id'));
          });
          if (inner.some(s => { const q = s.matrixTransform(back);
                                return at(ctx, null, q.x, q.y); }))
            onto.push(c.getAttribute('data-id'));
        });
        return { over, onto };
    }"""
    spill = page.evaluate(SPILL)
    check("no country is drawn on another country's land", spill["over"], [])
    # The other half: the countries not in the catalogue are one merged path.
    # A catalogue country painting inside it is Trinidad and Tobago on the coast
    # of Venezuela, or Lebanon in Syria.
    check("and none is drawn over the surrounding land", spill["onto"], [])

    print("small countries get an invisible target, not a bigger body")
    PAD = ("id => { const c = document.querySelector('#map [data-id=\"' + id + '\"]');"
           " const p = c.previousElementSibling;"
           " if (!p || !p.classList.contains('hit')) return 0;"
           " return Math.round(parseFloat(getComputedStyle(p).strokeWidth) * 10) / 10; }")
    check("Lebanon has one", page.evaluate(PAD, "422") > 3, True)
    check("Trinidad and Tobago has one", page.evaluate(PAD, "780") > 3, True)
    check("India, which needs none, has none", page.evaluate(PAD, "356"), 0)
    check("the pad paints nothing",
          page.evaluate("() => [...document.querySelectorAll('#map .hit')].every(p => {"
                        " const cs = getComputedStyle(p);"
                        " return cs.fill === 'none' && /rgba\(0, 0, 0, 0\)/.test(cs.stroke); })"), True)
    check("and it traces the country, so it cannot drag the shape out of place",
          page.evaluate("() => [...document.querySelectorAll('#map .hit')].every(p =>"
                        " p.getAttribute('d') === p.nextElementSibling.getAttribute('d'))"), True)
    # The point of the pad: a country a pixel and a half across is still usable.
    page.evaluate("""() => { const c = document.querySelector('#map [data-id="422"]');
        const b = c.getBoundingClientRect();
        const e = new MouseEvent('click', { clientX: b.x + b.width / 2,
                                            clientY: b.y - 3, bubbles: true });
        document.elementFromPoint(b.x + b.width / 2, b.y - 3).dispatchEvent(e); }""")
    page.wait_for_timeout(200)
    check("a click just off the coast still selects Lebanon",
          page.evaluate(SEL), "422")
    page.keyboard.press("Escape")
    page.keyboard.press("Escape")

    print("zoom")
    PITCH = ("() => { const p = document.querySelector('#zeroHatch');"
             " const svg = document.querySelector('#map svg');"
             " const k = svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;"
             " return Math.round(parseFloat(p.getAttribute('width')) * k * 10) / 10; }")
    VB = "() => document.querySelector('#map svg').getAttribute('viewBox')"
    K = "() => window.TBB_MAP.zoom.k"
    rest = page.evaluate(VB)
    pads_at_rest = page.evaluate("() => document.querySelectorAll('#map .hit').length")
    check("starts at rest", page.evaluate(K), 1)
    check("and some countries need a hit pad there", pads_at_rest > 0, True)
    check("zoom out is not offered at rest",
          page.evaluate("() => document.getElementById('zoomOut').disabled"), True)
    check("nor is reset",
          page.evaluate("() => document.getElementById('zoomReset').hidden"), True)
    # At rest the page must still scroll over the map on a touch screen; an
    # embedded figure that eats the scroll is worse than one that cannot zoom.
    check("the page can still be scrolled over the map",
          page.evaluate("() => document.getElementById('map').style.touchAction"), "manipulation")
    page.click("#zoomIn")
    page.click("#zoomIn")
    page.wait_for_timeout(200)
    check("zooming in changes the window", page.evaluate(VB) != rest, True)
    check("and the gesture becomes ours",
          page.evaluate("() => document.getElementById('map').style.touchAction"), "none")
    check("reset is offered",
          page.evaluate("() => document.getElementById('zoomReset').hidden"), False)
    # The scale everything else is sized from has to follow the zoom, or the
    # hit pads stay fat and the rings stay thin while the map gets bigger.
    check("the hit pads stand down as the countries grow",
          page.evaluate("() => document.querySelectorAll('#map .hit').length") < pads_at_rest, True)
    check("the hatch still holds its pitch",
          page.evaluate(PITCH), 5)
    before = page.evaluate(VB)
    page.mouse.move(500, 380)
    page.mouse.down()
    page.mouse.move(380, 320, steps=10)
    page.mouse.up()
    page.wait_for_timeout(200)
    check("dragging pans", page.evaluate(VB) != before, True)
    check("and does not select the country under the pointer",
          page.evaluate(SEL), None)
    page.click("#zoomReset")
    page.wait_for_timeout(200)
    check("reset returns exactly to the fitted frame", page.evaluate(VB), rest)
    check("and to rest", page.evaluate(K), 1)

    print("the hatch, the gold ring and the zero mark hold their size")
    # All three are defined in frame units, so left alone they scale with the
    # viewBox. The hatch became a sub-pixel line at 320px, and the gold ring
    # took a third of Bangladesh's narrow side and most of its colour with it.
    page.select_option("#occSelect", "Meteorologist")
    check("the hatch is 5px on a laptop", page.evaluate(PITCH), 5)
    check("every country at zero is hatched, enlarged or not",
          page.evaluate("() => { const t = window.TBB_MAP.view().totals;"
                        " const cs = [...document.querySelectorAll('#map .country')];"
                        " const z = cs.filter((c, i) => t[i] === 0);"
                        " return z.length > 0 && z.every(c => c.style.fill.includes('zeroHatch')); }"), True)
    check("the gold ring is at full width on a laptop",
          page.evaluate("() => Math.max(...[...document.querySelectorAll('#map .ho-ring')]"
                        ".map(e => parseFloat(getComputedStyle(e).strokeWidth)))"), 1.9)
    page.set_viewport_size({"width": 360, "height": 900})
    page.wait_for_timeout(300)
    check("the hatch is still 5px on a phone", page.evaluate(PITCH), 5)
    check("the ring thins on a narrow country in a small frame",
          page.evaluate("() => Math.min(...[...document.querySelectorAll('#map .ho-ring')]"
                        ".map(e => parseFloat(getComputedStyle(e).strokeWidth))) < 1.9"), True)
    check("but never thins away to nothing",
          page.evaluate("() => Math.min(...[...document.querySelectorAll('#map .ho-ring')]"
                        ".map(e => parseFloat(getComputedStyle(e).strokeWidth))) >= 0.6"), True)
    page.set_viewport_size({"width": 1100, "height": 900})
    page.wait_for_timeout(300)
    page.select_option("#occSelect", "ALL")

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
