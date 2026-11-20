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
| Click a country / press Enter on one / Find a country | outlines it and opens its occupation breakdown |
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
* **A dilated country at zero is hatched, not a grey disc.** Zero is a hatch
  everywhere else on the map, so the small countries were the one place it read
  as a category of its own, sitting next to hatched neighbours. A stroke takes a
  pattern paint just as a fill does.
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
exercise clean (71 checks, including the country breakdown, its tooltips, the
two-layer Escape, the invisible hit target, and the spill test below), control
audit clean at
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
