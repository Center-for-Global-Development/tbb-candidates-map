# TBB candidates map

One interactive figure for the CGD blog post on the UK's Displaced Talent Visa:
where the skilled refugees in Talent Beyond Boundaries' talent catalogue are,
and how the pool changes when you filter to the occupations the UK says it needs.

**Figure:** [`index.html`](index.html) · **Review page:** [`preview.html`](preview.html)

## The question, and the default state

> Where are the skilled refugees the UK could recruit, and how many of them are
> in the seven countries chosen for the first phase?

Default: all 144 mapped occupations, all skill levels, no country selected —
186,944 candidates across 26 countries, 32% of them in the seven first-phase
countries. The point the figure has to let a reader reach is that **the pools
are mostly somewhere else**, and more so for shortage-list occupations (20%).

| What the reader does | What it decides |
|---|---|
| Skill level | restricts to occupations at one RQF band |
| Shortage-list occupations only | restricts to occupations the MAC recommended for the Temporary Shortage List. Every one of them is RQF 3–5, so this disables the skill control rather than leaving it live and inert |
| Occupation | restricts to one occupation. Rebuilt from the two filters above, and reset to "all" when a filter removes the chosen one |
| Click a country / Find a country | outlines it and pins its numbers |

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
  changes with every filter, so no label layout survives every state. The
  ranking is carried as one derived line under the map instead, and every
  country is reachable by hover, tap, keyboard and the "Find a country" select.
  This is a deliberate departure from §13.7 of the CGD interactives standard.
* **No zoom.** With the frame fitted to the countries that carry data and the
  small ones dilated, nothing on the map is unreachable, so zoom would be a
  control that earns nothing. Departure from §13.5, same reason.
* **The frame is fitted, not the whole globe.** The catalogue runs from
  Guatemala to Indonesia and from Türkiye to South Africa; the empty Pacific and
  the Arctic cost about a third of the frame.
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
exercise clean (27 checks), no console errors, frame grows and shrinks. Also
checked on the published site
(<https://center-for-global-development.github.io/tbb-candidates-map/>): every
asset serves, 26 catalogue countries and 7 gold rings render, default total
186,944, no failed requests and no console errors at 320/768/1200px.

**Not yet done:** the resize and analytics contracts have not been exercised
against the real cgdev.org parent, only against `preview.html`, which cannot
verify the origin allowlist. The catalogue extract carries no date; add one to
the figure's note before publication.
