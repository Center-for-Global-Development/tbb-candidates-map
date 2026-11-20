# -*- coding: utf-8 -*-
"""Pre-project world-atlas countries-110m into SVG paths (Natural Earth 1).

Writes data/world-paths.js so the figure needs no CDN, no runtime fetch and
works from file:// (which the QA gate uses).
"""
import json, math, os, sys, urllib.request

# The catalogue countries are drawn from Natural Earth 50m, the rest of the
# world from 110m. 110m is a world-scale generalisation: it gives Trinidad and
# Tobago eight vertices and Lebanon eleven, so no amount of enlargement makes
# them resemble their own coastlines, and the map's credibility rests on their
# doing so. 50m costs about 300KB over the 26 countries that carry data; the
# grey context stays on 110m, where nobody is looking that closely.
BASE = "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/"
# Downloads live in their own directory, away from the scripts, so nothing
# here can shadow a module this build imports.
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".geocache")
OUT = r"C:\Users\SamuelHuckstep(shuck\dev\tbb-candidates-map\data\world-paths.js"

CATALOGUE = {  # M49 -> sheet name, the 26 TBB countries
    "050": "Bangladesh", "108": "Burundi", "170": "Colombia", "188": "Costa Rica",
    "214": "Dominican Republic", "218": "Ecuador", "818": "Egypt", "231": "Ethiopia",
    "320": "Guatemala", "356": "India", "360": "Indonesia", "368": "Iraq",
    "400": "Jordan", "404": "Kenya", "422": "Lebanon", "454": "Malawi",
    "458": "Malaysia", "586": "Pakistan", "646": "Rwanda", "682": "Saudi Arabia",
    "710": "South Africa", "834": "Tanzania", "780": "Trinidad and Tobago",
    "792": "Turkiye", "784": "United Arab Emirates", "800": "Uganda",
}
DROP = {"010"}          # Antarctica: irrelevant here and it dominates the frame
MIN_LAT = -60.0         # clip the far south with it

def load(name):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, name)
    if not os.path.exists(path):
        print("downloading", BASE + name)
        urllib.request.urlretrieve(BASE + name, path)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def geometries(topo):
    """-> {id: [ring, ...]} in lon/lat, with the antimeridian un-wrapped."""
    tr = topo.get("transform")
    sx, sy = (tr["scale"] if tr else (1, 1))
    tx, ty = (tr["translate"] if tr else (0, 0))

    def decode(arc):
        out, x, y = [], 0, 0
        for dx, dy in arc:
            x += dx
            y += dy
            out.append((x * sx + tx, y * sy + ty) if tr else (x, y))
        return out

    arcs = [decode(a) for a in topo["arcs"]]

    def ring(idxs):
        pts = []
        for i in idxs:
            a = arcs[~i][::-1] if i < 0 else arcs[i]
            pts.extend(a[1:] if pts else a)
        return pts

    out = {}
    for g in topo["objects"]["countries"]["geometries"]:
        gid = str(g.get("id", "")).zfill(3)
        t = g["type"]
        if t == "Polygon":
            rings = [ring(r) for r in g["arcs"]]
        elif t == "MultiPolygon":
            rings = [ring(r) for poly in g["arcs"] for r in poly]
        else:
            continue
        rings = [unwrap(r) for r in rings if len(r) >= 4]
        if rings:
            out[gid] = {"rings": rings,
                        "name": (g.get("properties") or {}).get("name", "")}
    return out


# ---- Natural Earth 1 (same polynomial as d3-geo) ---------------------------
def project(lon, lat):
    lam = math.radians(lon)
    phi = math.radians(max(MIN_LAT, lat))
    p2 = phi * phi
    p4 = p2 * p2
    x = lam * (0.8707 - 0.131979 * p2 + p4 * (-0.013791 + p4 * (0.003971 * p2 - 0.001529 * p4)))
    y = phi * (1.007226 + p2 * (0.015085 + p4 * (-0.044475 + 0.028874 * p2 - 0.005916 * p4)))
    return x, y


def unwrap(ring):
    """Undo the antimeridian wrap.

    A country that straddles 180 degrees is stored with its eastern vertices at
    about +180 and its western ones at about -180. Projected literally, the edge
    between the two is drawn as a straight sweep right across the map: Fiji
    produced the horizontal line through the South Pacific, and Russia's
    Chukotka ring another one above the frame. Walking the ring and keeping each
    consecutive step under 180 degrees puts the pieces back together; the part
    that then sits beyond the frame is simply clipped by the viewBox.
    """
    out = [ring[0]]
    for lon, lat in ring[1:]:
        prev = out[-1][0]
        while lon - prev > 180:
            lon -= 360
        while lon - prev < -180:
            lon += 360
        out.append((lon, lat))
    # Unwrapping can walk a whole ring off the map if it happened to start on
    # the far side of the join; slide it back to where the land actually is.
    mid = (min(p[0] for p in out) + max(p[0] for p in out)) / 2
    shift = -360 if mid > 180 else (360 if mid < -180 else 0)
    return [(lon + shift, lat) for lon, lat in out] if shift else out


# One resolution for the whole map. Mixing them was a mistake: a catalogue
# country drawn at 50m over a 110m world does not register against its own
# neighbours, so Colombia sat on a Venezuela whose border ran somewhere else
# and grey showed through the join. Borders only line up if both sides come
# from the same generalisation.
coarse = geometries(load("countries-110m.json"))
fine = geometries(load("countries-50m.json"))
missing_fine = sorted(set(CATALOGUE) - set(fine))
assert not missing_fine, ["no 50m geometry for: " + ", ".join(CATALOGUE[m] for m in missing_fine)]

feats = []
for gid in sorted(set(fine)):
    if gid in DROP:
        continue
    src = fine
    if gid not in src:
        continue
    feats.append({"id": gid, "name": src[gid]["name"], "rings": src[gid]["rings"]})

# ---- fit to a 960-wide frame ----------------------------------------------
# The horizontal extent is the projection's own, a full 360 degrees measured at
# the equator where Natural Earth 1 is widest — not the extent of whatever land
# happens to touch the edge. Taking it from the data made the scale depend on a
# single ring: Fiji's wrapped polygon reached 180 degrees at 16 degrees south,
# so un-wrapping it silently resized the entire map.
x0, x1 = project(-180.0, 0.0)[0], project(180.0, 0.0)[0]
pts = [project(lon, lat) for f in feats for r in f["rings"] for lon, lat in r]
y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
W, PAD = 960.0, 4.0
k = (W - 2 * PAD) / (x1 - x0)
H = (y1 - y0) * k + 2 * PAD


def to_px(lon, lat):
    x, y = project(lon, lat)
    return (x - x0) * k + PAD, (y1 - y) * k + PAD   # flip y


def to_px_ring(r):
    return [to_px(lon, lat) for lon, lat in r]


def ring_area(p):
    """Shoelace area of a projected ring, in square frame units."""
    return abs(sum(p[i][0] * p[i - 1][1] - p[i - 1][0] * p[i][1]
                   for i in range(len(p)))) / 2


def simplify(p, tol):
    """Douglas-Peucker on a projected ring, tolerance in frame units.

    Only the context is simplified. At 50m the backdrop carries far more
    detail than it can show: a 0.4-unit tolerance is under half a pixel at the
    widths this figure is drawn at, so nothing visible is lost, and it takes
    the payload down by roughly two thirds.
    """
    if len(p) < 4 or tol <= 0:
        return p
    keep = [False] * len(p)
    keep[0] = keep[-1] = True
    stack = [(0, len(p) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        (ax, ay), (bx, by) = p[a], p[b]
        dx, dy = bx - ax, by - ay
        den = dx * dx + dy * dy
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            x, y = p[i]
            if den == 0:
                d = (x - ax) ** 2 + (y - ay) ** 2
            else:
                t = ((x - ax) * dx + (y - ay) * dy) / den
                t = 0.0 if t < 0 else (1.0 if t > 1 else t)
                ex, ey = ax + t * dx - x, ay + t * dy - y
                d = ex * ex + ey * ey
            if d > best:
                best, bi = d, i
        if best > tol * tol:
            keep[bi] = True
            stack.append((a, bi))
            stack.append((bi, b))
    return [q for q, f in zip(p, keep) if f]


def px_path(rings, nd=1):
    out = []
    for p in rings:
        seg, prev = [], None
        for px, py in p:
            px, py = round(px, nd), round(py, nd)
            if prev == (px, py):
                continue            # drop points that collapse at this precision
            prev = (px, py)
            seg.append(f"{px:g},{py:g}")
        if len(seg) < 3:
            continue
        out.append("M" + "L".join(seg) + "Z")
    return "".join(out)


# ---- the frame the figure actually shows -----------------------------------
# Computed before the paths are written, because the context is culled against
# it: nothing outside the frame is ever drawn, so carrying Patagonia, the
# Arctic and the Pacific was paying for geometry no reader can see.
#
# Derived from the catalogue's own extent rather than kept as hand-tuned
# constants in the figure, so a rebuild can never leave the view box pointing at
# the wrong part of a re-scaled map. MARGIN is the breathing space around the
# outermost country, as a share of the box. A tight box round the catalogue is
# a 2.6:1 letterbox — far too flat to read on a phone and nothing like the
# proportions the figure was reviewed at — so the aspect is held in a band and
# the shorter side grown to meet it.
MARGIN, MIN_ASPECT, MAX_ASPECT = 0.04, 1.55, 1.95
cpts = [to_px(lon, lat) for f in feats if f["id"] in CATALOGUE
        for r in f["rings"] for lon, lat in r]
cx0, cx1 = min(p[0] for p in cpts), max(p[0] for p in cpts)
cy0, cy1 = min(p[1] for p in cpts), max(p[1] for p in cpts)
vw = (cx1 - cx0) * (1 + 2 * MARGIN)
vh = (cy1 - cy0) * (1 + 2 * MARGIN)
if vw / vh < MIN_ASPECT:
    vw = vh * MIN_ASPECT
elif vw / vh > MAX_ASPECT:
    vh = vw / MAX_ASPECT
vx = (cx0 + cx1) / 2 - vw / 2
vy = (cy0 + cy1) / 2 - vh / 2
VIEW = {"x": round(vx, 1), "y": round(vy, 1), "w": round(vw, 1), "h": round(vh, 1)}

CULL = 8.0          # keep a little beyond the frame, for strokes and rounding
VX0, VY0 = VIEW["x"] - CULL, VIEW["y"] - CULL
VX1 = VIEW["x"] + VIEW["w"] + CULL
VY1 = VIEW["y"] + VIEW["h"] + CULL


def offscreen(p):
    return (max(q[0] for q in p) < VX0 or min(q[0] for q in p) > VX1
            or max(q[1] for q in p) < VY0 or min(q[1] for q in p) > VY1)


# The context is a backdrop: an island it would draw smaller than a pixel is
# noise. The catalogue keeps everything down to a speck, because Tobago is one.
CTX_TOL, CTX_MIN_AREA, CAT_MIN_AREA = 0.4, 1.2, 0.05

countries, context = {}, []
for f in feats:
    cat = f["id"] in CATALOGUE
    rings = [to_px_ring(r) for r in f["rings"]]
    if cat:
        rings = [p for p in rings if ring_area(p) >= CAT_MIN_AREA]
    else:
        rings = [simplify(p, CTX_TOL) for p in rings
                 if ring_area(p) >= CTX_MIN_AREA and not offscreen(p)]
    if not rings:
        continue
    # Catalogue countries are written at two decimals. At one, the rounding is
    # itself a generalisation: Trinidad and Tobago is 2.4 units across, so a
    # 0.1 grid left it 24 possible x positions and threw away most of the 50m
    # detail the moment it was written out. The context stays at one decimal.
    d = px_path(rings, nd=2 if cat else 1)
    if not d:
        continue
    if cat:
        big = max(rings, key=ring_area)
        cx = sum(q[0] for q in big) / len(big)
        cy = sum(q[1] for q in big) / len(big)
        bw = max(q[0] for q in big) - min(q[0] for q in big)
        bh = max(q[1] for q in big) - min(q[1] for q in big)
        countries[f["id"]] = {"d": d, "cx": round(cx, 1), "cy": round(cy, 1),
                              "a": round(ring_area(big), 1),
                              "m": round(min(bw, bh), 1),
                              "x": round(max(bw, bh), 1)}
    else:
        context.append(d)

missing = sorted(set(CATALOGUE) - set(countries))
assert not missing, ["no geometry for: " + ", ".join(CATALOGUE[m] for m in missing)]

payload = {"w": round(W, 1), "h": round(H, 1), "view": VIEW,
           "context": "".join(context), "countries": countries}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("/* World geometry, pre-projected (Natural Earth 1) from world-atlas 2.0.2\n"
             "   (Natural Earth, public domain). Antarctica dropped, south clipped at 60S.\n"
             "   Built by scripts/build-geometry.py. Do not hand-edit. */\n")
    fh.write("window.TBB_GEO = " + json.dumps(payload, separators=(",", ":")) + ";\n")

print("viewBox 0 0", round(W, 1), round(H, 1))
print("figure view:", VIEW)
print("catalogue countries with geometry:", len(countries), "of", len(CATALOGUE))
print("bytes:", os.path.getsize(OUT))
small = sorted(((v["m"], CATALOGUE[k]) for k, v in countries.items()))[:8]
print("narrowest countries (shorter side, units at 960 wide):", [(n, m) for m, n in small])
