# TBB candidates map

One interactive figure for the CGD blog post on the UK's Displaced Talent Visa:
where the skilled refugees in Talent Beyond Boundaries' talent catalogue are,
and how the pool changes when you filter to the occupations the UK says it needs.

**Live figure:** <https://center-for-global-development.github.io/tbb-candidates-map/>
· **Live review page:** <https://center-for-global-development.github.io/tbb-candidates-map/preview.html>
· local: [`index.html`](index.html), [`preview.html`](preview.html)

## The question, and the default state

> Where are the skilled refugees the UK could recruit, and how many of them are
> in the seven countries chosen for the first phase?

Default: all 144 mapped occupations, every skill level, no country selected —
186,944 candidates across 26 countries, 32% of them in the seven first-phase
countries. The point the figure has to let a reader reach is that **the pools
are mostly somewhere else**, and more so for shortage-list occupations (20%).
Those numbers are not printed above the map: a reader who wants them reads the
key and the tooltip, and the blog text carries the headline.

| What the reader does | What it decides |
|---|---|
| Occupations: All / RQF 6+ / RQF 3–5 / RQF 1–2 / Shortage list | restricts the pool to one band. One control, not a skill filter plus a shortage-list checkbox: every shortage-list occupation is RQF 3–5, so the two could never say anything together that either did not say alone, and the checkbox spent half its life disabled |
| Occupation | restricts to one occupation. Rebuilt from the band above, and reset to "all" when the band removes the chosen one |
| Click a country / press Enter on one / Find a country | outlines it and opens its occupation breakdown. Below 600px the select returns to its placeholder afterwards: it is too narrow there to show a country's name without cutting it, and it is a way in rather than a readout |
| Zoom in / out / reset, drag, pinch, ctrl-wheel | moves the window over the map. Nothing else depends on it |
| The band control inside that breakdown | re-splits that one country's pool. It is the card's own: it starts from the map's band and changes nothing underneath |

Colour is candidate count; a gold ring marks the seven countries named in the
Home Office's *Lead sponsors: refugee eligibility criteria*, published 29 October
2026: Bangladesh, India, Pakistan, Malaysia, Egypt, Uganda, Kenya. That guidance
is where the figure's "first phase" comes from — it says the routes "will
initially operate in" those seven.

The ring means **the route operates from that country**, not that everyone
counted there is eligible. The same guidance requires an applicant to be outside
their country of nationality, recognised as a refugee by the relevant authority,
and present and registered before 1 October 2026. The map counts people in TBB's
catalogue by country of residence, which is the right denominator for "where
could the UK recruit from", but it is not a count of eligible applicants, and the
figure's note says so.

## Data

| File | What it is |
|---|---|
| `data/tbb-candidates-data.js` | 144 occupations × 26 countries, with SOC 2020 code, RQF level and TSL status per occupation |
| `data/world-paths.js` | world geometry, pre-projected to SVG paths. Natural Earth 50m for the 26 catalogue countries, 110m for the context |

Built by the scripts in `scripts/`, from two workbooks held outside this repo
(the TBB catalogue extract, and the MAC's TSL stage 2 Annex 4). Re-run them if
either workbook changes; do not hand-edit the generated files.

**Sources.** Candidate counts: Talent Beyond Boundaries talent catalogue, supplied
to CGD. First-phase countries: Home Office, *Lead sponsors: refugee eligibility
criteria*, 29 October 2026. Skill level and shortage-list status: Migration Advisory Committee,
*Temporary Shortage List stage 2 report*, Annex 4 (SOC 2020 occupation
information). Geometry: Natural Earth (public domain) via world-atlas 2.0.2.

**Counts are people registered with TBB, not applicants to any UK route.**

### The occupation-to-SOC match is indicative

TBB records a coarse occupation description; the MAC's skill levels and shortage
list are keyed to SOC 2020. CGD matched the two by hand. The match is sound for
most occupations and genuinely uncertain for some: TBB's categories are broader
than SOC, and a few could sit at either professional or associate-professional
level, which changes both the RQF band and whether the occupation is on the
shortage list. The blog text says the map is indicative; the figure says the
same in its note. The full match, with a confidence rating and a caveat per
occupation, is on the `SOC mapping` sheet of the TBB workbook.

**Excluded throughout:** 6,772 candidates (3.5%) whose recorded occupation has no
SOC equivalent (astrologer, fashion model, scribe, companion/valet, and two
residual ISCO-style labels) or is not an occupation (student, housewife,
freelance, "Bachelor's Degree", unknown).

**Merged for the map:** "Mining and quarrying worker" with "Mining or quarry
worker"; "Photographer" with "Photographer, image or sound equipment operator".

### Hand-checked benchmarks

Both reconciled against the source workbook by a route the export script does
not use (the country × occupation grid rather than the long list):

* Jordan, all mapped occupations: **35,483**
* All countries, shortage-list occupations: **17,401**

## Controls on a narrow screen

At a third of a laptop screen the control bank was as tall as the map. Two
things cost a row each, neither of them necessary:

* **The five bands wrapped to two rows.** They were not too wide - the full
  labels need 280px and there is more than that down to about 335px of panel.
  A rule here was forcing it. They now stay on one row at every width, and below
  384px the labels shorten (`RQF 6+` to `6+`, `Shortage list` to `Shortage`)
  rather than the row breaking. The full wording stays in `aria-label`.
* **The country select took a row of its own.** It now keeps the title's row and
  the title wraps into what is left, which costs nothing.

Measured, controls plus panel header: **286px to 225px at 480px wide**, and
306px to 263px at 320px.

Two sizing bugs turned up on the way, both older than this change.
`United Arab Emirates` needs 155px of text box and the select gave it 146px at
*every* width, so the longest names had always been cut; the select is 215px
where there is room, and a finder below 600px. No audit catches that, because a
`<select>` draws its own text and there is no child element for the clipped-text
check to find.

## Design decisions worth not "fixing"

* **Shading bands are recalculated for the occupations shown.** Counts run from
  about 140 to 35,000 at the default and from a handful to a few hundred inside
  one occupation. A single fixed set of bands either flattens the map to its
  darkest two classes or, under a filter, to its palest one. The bands are
  log-spaced across the range on screen, rounded to readable numbers, and the
  key states them in full, so no reader has to infer a value from a hue.
* **The palest class is a clear colour, not an off-grey.** At `#E4F0F1` the
  smallest pools were indistinguishable from countries not in the catalogue at
  all. Catalogue countries also carry a darker boundary than the context.
* **Every country is drawn at its true size, in its true place.** Two earlier
  attempts to make the small ones easier to see are gone, because both lied
  about the map. A stroke in the country's own fill colour added a constant
  margin all round, filling every inlet and rounding every headland, so the mark
  was a lozenge at any size. Enlarging the shape about its centre kept the
  outline honest but pushed it into its neighbours: Trinidad and Tobago reached
  the coast of Venezuela, and Lebanon reached into the Mediterranean and down
  towards Jordan. Countries tile the plane — there is no empty space to grow
  into, so any enlargement takes territory that belongs to someone else. The
  cost is that Lebanon, which holds the second largest pool, is about 4px across
  on a laptop and a pixel and a half on a phone.
* **What a small country gets instead is an invisible target.** A transparent
  stroke, wide enough to reach an 11px hit area, carrying the same handlers as
  the country. It paints nothing, so the geography is untouched, and it is
  applied by on-screen size rather than by a fixed list, so it follows the frame
  — Jordan gets one at 320px and none on a laptop. Hover still lights the
  country itself, through an adjacent-sibling rule.
* **One resolution for the whole map: Natural Earth 50m.** Mixing them was a
  mistake that shipped: catalogue countries at 50m over a 110m world do not
  register against their own neighbours, so Colombia sat on a Venezuela whose
  border ran somewhere else and grey showed through the join, and Türkiye had a
  grey fringe along its whole coast. Borders only line up if both sides come
  from the same generalisation. 110m is also too coarse for the small ones on
  its own terms — it gave Trinidad and Tobago eight vertices and one island,
  where 50m gives 38 and two.
* **The context is culled to the frame and simplified; the catalogue is not.**
  A 50m world is 1MB. Nothing outside the view box is ever drawn, so Patagonia,
  the Arctic and the Pacific are dropped at build time; backdrop islands under
  a square pixel go too, and the rest is Douglas-Peucker simplified at 0.4
  units, under half a pixel at the widths this is drawn at. That brings it to
  238KB, 85KB gzipped — slightly less than the mixed-resolution build it
  replaces. Catalogue countries keep every vertex and are written at two
  decimals rather than one, because on a country 2.4 units across a 0.1 grid is
  itself a generalisation.
* **The zero hatch keeps a constant 5px pitch.** It is defined in frame units,
  so left alone it scales with the viewBox: a 6.5px pitch on a laptop became
  1.9px with a sub-pixel line at 320px, which aliases into flat grey and stops
  reading as a hatch. Dividing by the on-screen scale holds it, at every width
  and at every zoom, and keeps it in step with the legend's own swatch.
* **The gold first-phase ring thins on a narrow country in a small frame.** It
  is centred on the boundary, so it eats into the fill from both sides - and the
  fill is the data. A flat 1.9px is 5-11% of a country's narrow side on a laptop
  but a third of Bangladesh's at 320px. It is a tenth of the narrow side, capped
  at 1.9px and floored at 0.6px. Bangladesh stays mostly gold at 320px and
  thinning cannot fix it: hiding its own ring moves it from 85% to 81%, hiding
  *India's* moves it to 40%. What surrounds Bangladesh is India's ring.
* **No country labels.** Six of the nine largest pools sit in one cluster
  (Turkiye, Lebanon, Jordan, Egypt, Iraq, Saudi Arabia) and the top-ranked set
  changes with every filter, so no label layout survives every state. Every
  country is reachable by hover, tap, keyboard and the "Find a country" select,
  and clicking one gives its numbers in full. A deliberate departure from 13.7.
* **The frame is fitted, not the whole globe.** The catalogue runs from
  Guatemala to Indonesia and from Turkiye to South Africa; the empty Pacific and
  the Arctic cost about a third of the frame. The view box is computed by the
  build from the catalogue's own extent, so a rebuild cannot leave a hand-tuned
  frame pointing at the wrong part of a re-scaled map.
* **Antimeridian rings are un-wrapped at build time.** Fiji is stored with its
  eastern vertices near +180 and its western ones near -180; projected as given,
  the edge between them was drawn as a straight line across the South Pacific.
  The build walks each ring and keeps every step under 180 degrees.
* **The horizontal extent is the projection's, not the data's.** Taking it from
  the data made the scale depend on whichever land touched the edge - which was
  Fiji's wrapped polygon, so fixing the line above silently resized the whole
  map.
* **The country breakdown is an overlay on a laptop and a section on a phone.**
  At 320px the map is about 150px tall, so a card floated over it has nowhere to
  go. Below 620px the same card is laid out under the map instead and the frame
  grows to fit. Same content, same controls - not a shrunken desktop overlay.
* **The breakdown ignores the map's occupation filter.** A list of occupations
  filtered to one occupation is a list of one row.
* **Hover is a halo, not a colour change.** The fill is the data and the gold
  ring means "first phase", so neither can be borrowed to say "your pointer is
  here". A soft shadow belongs to no scale and reads the same over the palest
  class and the darkest.
* **The occupation rows carry one tooltip line, and only under "All".** The row
  already shows the occupation and the count; under any single band every row
  shares that band. What is left worth saying is the skill level of a mixed
  list, so that is all the tooltip says.
* **Selection traces the country.** An earlier version put a circle on the small
  ones, which threw the shape away and read as a bullseye dropped on the map.
* **Zoom, as of the build that stopped enlarging countries.** The figure shipped
  without it on the grounds that nothing was out of reach once the frame was
  fitted and the small countries enlarged. The enlargement is gone - countries
  are drawn true, so Lebanon really is a few pixels - and that makes zoom the
  honest way to look closely rather than a control that earns nothing. Buttons,
  drag to pan, pinch, and ctrl/cmd with the wheel. **Not a bare wheel**: this is
  an iframe in an article, and a figure that eats the reader's scroll is worse
  than one that cannot zoom. For the same reason a touch drag only pans once
  zoomed in; at rest the page scrolls over the map as usual. The controls sit on
  the map, not in the control bank, because the bank is already the tallest
  thing on a narrow screen. Everything sized from the on-screen scale - hit
  pads, gold rings, the hatch - is computed from the window actually shown, so
  it all follows the zoom. Replaces the earlier 13.5 departure.
* **Escape holds.** Re-rendering puts a new node under a stationary cursor and
  the browser fires `pointerenter` without the pointer moving, so Escape used to
  hide the tooltip and the next frame brought it back. Dismissal now holds until
  the reader moves the pointer.

## Dependencies

None. No CDN, no map library, no build step — geometry is pre-projected at build
time, so the figure also renders from `file://`. The only shared code is the
published CGD layer in `shared/`, which must not be forked or edited here:

| File | Role |
|---|---|
| `shared/cgd-embed.js` | iframe resize + analytics. Loads **last** in `<body>` |
| `shared/cgd-figure.css` | house look and type scale |
| `shared/cgd-responsive.css` | mobile and control behaviour |
| `shared/chart-core.js`, `shared/dom.js` | formatters, width observer, DOM helpers |

## Embedding

```html
<iframe src="https://center-for-global-development.github.io/tbb-candidates-map/"
        title="Map: Talent Beyond Boundaries candidates by country and occupation"
        style="width:100%;border:0" loading="lazy"></iframe>
```

The child posts `{type:'cgd-iframe-resize', height}` to `https://www.cgdev.org`
and observes `document.body`, so the frame grows **and** shrinks. Analytics are
documented in [`TRACKING.md`](TRACKING.md).

## Social stills

```bash
python scripts/make-social.py      # writes social/*.png at 2x
```

`social.html` renders the map with no controls, a title and a one-line
subtitle, for posting as an image. It is not the figure: no interaction, no
resize or analytics contract, and it is marked `data-cgd-harness` so the gate
skips it. It reads the same `data/` files and repeats the figure's colour ramp
and threshold rules verbatim, so the still cannot drift from the live map's
shading.

Three things it does differently, all for a thumbnail rather than a reader:

* **It crops to the countries, not to the figure's frame.** The live frame is
  padded to hold a readable aspect on a phone, which leaves a band of empty
  ocean; the still measures what was drawn, gold rings included, and crops to
  that.
* **The gold ring is 2.4px, not 1.9px.** It has to survive being looked at 400px
  wide in a timeline.
* **It loads Inter.** The figure doesn't: on cgdev.org the parent supplies Sofia
  Pro. A headless browser has neither, and a still rendered in whatever sans the
  machine happens to have is not something to publish.

Four files, two shapes and two subtitles. `16x9` is 1200×675, the safe size for
a link card. `natural` lets the canvas take the height the map wants, which
gives the map more room in a timeline post. `brief` carries the supplied
subtitle; `finding` carries the map's own headline (seven countries, 68%
elsewhere), and the numbers in it are computed from the data rather than typed.

## QA

```bash
python qa/verify.py      # the gate: 320/768/1200px, exits non-zero on failure
python qa/exercise.py    # every filter, selection, keyboard, resize-with-detail-open
python qa/shots.py       # screenshots at 320/390/700/768/1200px + in-page audits
```

`qa/verify.mjs` is the Node version of the gate, for CI
(`.github/workflows/verify.yml`); `qa/verify.py` is the same gate for a machine
without Node, which is why both are here.

**Last verified:** 15 November 2026 — gate clean at 320/768/1200px, legend
checked in all 149 states (every band and every occupation: never fewer than
three classes, no duplicate class labels), state
exercise clean (85 checks, including the country breakdown, its tooltips, the
two-layer Escape, the invisible hit target, zoom and pan, and the spill test
below), control audit clean at
320/390/700/768px, no console errors, frame
grows and shrinks. Published site checked at
<https://center-for-global-development.github.io/tbb-candidates-map/>: every
asset serves, 26 catalogue countries and 7 gold rings render, default total
186,944, no failed requests.

**The spill test.** `qa/exercise.py` samples strictly interior points of all 26
countries and checks that none falls inside another country or inside the
context path. It is written in screen space on purpose: `isPointInFill` works in
the element's own user space, *before* its transform, so a version written in
user space silently checks the payload rather than the picture — it passed with
the 2.2x enlargement put back, which is the exact defect it exists to catch.
Only strictly interior points count, because neighbours share a border and both
polygons contain it. Verified against a negative control: clean as shipped,
and it reports the overlaps as soon as an enlargement is restored.

**Carried by this README, not by the figure's note.** The note was cut to four
sentences on request (source, first-phase countries, MAC Annex 4, the SOC match),
so two things it used to say now live only here: the 6,772 excluded candidates,
and the Natural Earth attribution. All three of the note's links were checked
against the live pages.

**Not yet done:** the resize and analytics contracts have not been exercised
against the real cgdev.org parent, only against `preview.html`, which cannot
verify the origin allowlist. The catalogue extract carries no date; add one to
the figure's note before publication.
