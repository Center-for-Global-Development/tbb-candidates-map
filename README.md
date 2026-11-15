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

Colour is candidate count; a gold ring marks the seven countries named for the
first phase in the Home Office written statement of 29 October 2026
(Bangladesh, Egypt, India, Kenya, Malaysia, Pakistan, Uganda).

## Data

| File | What it is |
|---|---|
| `data/tbb-candidates-data.js` | 144 occupations × 26 countries, with SOC 2020 code, RQF level and TSL status per occupation |
| `data/world-paths.js` | world geometry, pre-projected to SVG paths |

Built by the scripts in `scripts/`, from two workbooks held outside this repo
(the TBB catalogue extract, and the MAC's TSL stage 2 Annex 4). Re-run them if
either workbook changes; do not hand-edit the generated files.

**Sources.** Candidate counts: Talent Beyond Boundaries talent catalogue, supplied
to CGD. Skill level and shortage-list status: Migration Advisory Committee,
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
* **Small countries are dilated, not replaced by symbols.** Lebanon holds the
  second largest pool and is one of the smallest countries on the map. A stroke
  in the country's own fill colour keeps the real shape and reaches a usable
  size; markers at that density collided (Rwanda with Burundi, Lebanon with
  Jordan).
* **No country labels.** Six of the nine largest pools sit in one cluster
  (Türkiye, Lebanon, Jordan, Egypt, Iraq, Saudi Arabia) and the top-ranked set
  changes with every filter, so no label layout survives every state. Every
  country is reachable by hover, tap, keyboard and the "Find a country" select,
  and clicking one gives its numbers in full. This is a deliberate departure
  from §13.7 of the CGD interactives standard.
* **No zoom.** With the frame fitted to the countries that carry data and the
  small ones dilated, nothing on the map is unreachable, so zoom would be a
  control that earns nothing. Departure from §13.5, same reason.
* **The frame is fitted, not the whole globe.** The catalogue runs from
  Guatemala to Indonesia and from Türkiye to South Africa; the empty Pacific and
  the Arctic cost about a third of the frame.
* **The country breakdown is an overlay on a laptop and a section on a phone.**
  At 320px the map is about 150px tall, so a card floated over it has nowhere to
  go: the shared bottom-sheet rules produced a sheet taller than the area that
  contained it, with the title and the close button clipped away. Below 620px
  the same card is laid out under the map instead and the frame grows to fit.
  Same content, same controls — not a shrunken desktop overlay.
* **The breakdown ignores the map's occupation filter.** A list of occupations
  filtered to one occupation is a list of one row.
* **Antimeridian rings are un-wrapped at build time.** Fiji is stored with its
  eastern vertices near +180 and its western ones near -180; projected as given,
  the edge between them was drawn as a straight line across the South Pacific.
  Russia produced a second one above the frame. The build walks each ring and
  keeps every step under 180 degrees.
* **The horizontal extent is the projection's, not the data's.** Taking it from
  the data made the scale depend on whichever land touched the edge — which was
  Fiji's wrapped polygon, so fixing the line above silently resized the whole
  map. The frame the figure shows is now computed by the build from the
  catalogue's own extent and carried in the payload, so a rebuild cannot leave
  a hand-tuned view box pointing at the wrong part of a re-scaled world.
* **Hover is a halo, not a colour change.** The fill is the data and the gold
  ring means "first phase", so neither can be borrowed to say "your pointer is
  here". A soft shadow belongs to no scale and reads the same over the palest
  class and the darkest. Countries outside the catalogue take no pointer events
  and so stay still, which makes the halo double as "this one opens".
* **The occupation rows carry one tooltip line, and only under "All".** The row
  already shows the occupation and the count; under any single band every row
  shares that band. What is left worth saying is the skill level of a mixed
  list, so that is all the tooltip says.
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

**Last verified:** 15 November 2026 — gate clean at 320/768/1200px, state
exercise clean (52 checks, including the country breakdown, its tooltips and
the two-layer Escape), control audit clean at 320/390/700/768px, no console errors, frame
grows and shrinks. Published site checked at
<https://center-for-global-development.github.io/tbb-candidates-map/>: every
asset serves, 26 catalogue countries and 7 gold rings render, default total
186,944, no failed requests.

**Not yet done:** the resize and analytics contracts have not been exercised
against the real cgdev.org parent, only against `preview.html`, which cannot
verify the origin allowlist. The catalogue extract carries no date; add one to
the figure's note before publication.
