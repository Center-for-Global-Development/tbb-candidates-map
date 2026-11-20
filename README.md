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
* **Small countries are enlarged, not thickened, and not replaced by symbols.**
  Lebanon holds the second largest pool and is one of the smallest countries on
  the map. It is drawn larger than life about its own centre, with its own
  outline. A stroke in the country's fill colour was the earlier answer and the
  wrong instrument: a stroke adds a constant margin all the way round, so it
  fills every inlet and rounds off every headland, and the result was a lozenge
  that did not resemble the country at any size. Enlarging the path leaves the
  coastline exactly as Natural Earth drew it — same inlets, same proportions,
  same islands — and the border stays a hairline because it does not scale.
  Markers were rejected earlier for a different reason: at this density they
  collided (Rwanda with Burundi, Lebanon with Jordan).
* **The enlargement is only what the frame requires.** The shorter side is
  brought up to a readable, tappable minimum and no further, recomputed on
  every resize, so a country is drawn at its true size as soon as there is room
  for it. At 960px that is Trinidad and Tobago ×3.0, Lebanon ×2.2, Burundi ×1.6,
  Rwanda ×1.4 and nothing else; the Dominican Republic, Malawi and Costa Rica
  are already big enough. Eligibility is the shorter side rather than the area,
  because area mis-sorts a country that is long and thin: Malawi's area is twice
  Costa Rica's, but it is narrower than the Dominican Republic.
* **Catalogue countries are drawn from Natural Earth 50m, the rest of the world
  from 110m.** 110m is a world-scale generalisation — it gave Trinidad and
  Tobago eight vertices (one island, not two) and Lebanon eleven, so no
  enlargement could make them resemble their own coastlines, and the
  credibility of the map rests on their doing so. At 50m they have 38 and 62.
  Catalogue paths are also written at two decimals rather than one: on a country
  2.4 units across, a 0.1 grid is itself a generalisation. The cost is 255KB of
  geometry, 91KB gzipped, for the 26 countries that carry data; the grey context
  stays on 110m, where nobody is looking that closely.
* **Selection traces the country, at whatever size the country is drawn.** An
  earlier version put a circle on the small ones, which threw the shape away and
  read as a bullseye dropped on the map.
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
exercise clean (72 checks, including the country breakdown, its tooltips, the
two-layer Escape, the frame-aware enlargement, the shaped selection outline and
the hatch and ring scaling), control audit clean at
320/390/700/768px, no console errors, frame
grows and shrinks. Published site checked at
<https://center-for-global-development.github.io/tbb-candidates-map/>: every
asset serves, 26 catalogue countries and 7 gold rings render, default total
186,944, no failed requests.

**Carried by this README, not by the figure's note.** The note was cut to four
sentences on request (source, first-phase countries, MAC Annex 4, the SOC match),
so two things it used to say now live only here: the 6,772 excluded candidates,
and the Natural Earth attribution. All three of the note's links were checked
against the live pages.

**Not yet done:** the resize and analytics contracts have not been exercised
against the real cgdev.org parent, only against `preview.html`, which cannot
verify the origin allowlist. The catalogue extract carries no date; add one to
the figure's note before publication.
