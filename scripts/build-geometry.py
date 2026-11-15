# -*- coding: utf-8 -*-
"""Pre-project world-atlas countries-110m into SVG paths (Natural Earth 1).

Writes data/world-paths.js so the figure needs no CDN, no runtime fetch and
works from file:// (which the QA gate uses).
"""
import json, math, os, sys, urllib.request

SRC = "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "countries-110m.json")
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

if not os.path.exists(CACHE):
    print("downloading", SRC)
    urllib.request.urlretrieve(SRC, CACHE)
topo = json.load(open(CACHE, encoding="utf-8"))

# ---- topojson -> geojson ---------------------------------------------------
tr = topo.get("transform")
sx, sy = (tr["scale"] if tr else (1, 1))
tx, ty = (tr["translate"] if tr else (0, 0))


def decode_arc(arc):
    out, x, y = [], 0, 0
    for dx, dy in arc:
        x += dx
        y += dy
        out.append((x * sx + tx, y * sy + ty) if tr else (x, y))
    return out


ARCS = [decode_arc(a) for a in topo["arcs"]]


def ring_coords(idxs):
    pts = []
    for i in idxs:
        a = ARCS[~i][::-1] if i < 0 else ARCS[i]
        pts.extend(a[1:] if pts else a)
    return pts


def polygons(geom):
    """-> list of rings (each a list of lon/lat tuples)."""
    t = geom["type"]
    if t == "Polygon":
        return [ring_coords(r) for r in geom["arcs"]]
    if t == "MultiPolygon":
        return [ring_coords(r) for poly in geom["arcs"] for r in poly]
    return []


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


geoms = topo["objects"]["countries"]["geometries"]
feats = []
for g in geoms:
    gid = str(g.get("id", "")).zfill(3)
    if gid in DROP:
        continue
    rings = [unwrap(r) for r in polygons(g) if len(r) >= 4]
    if not rings:
        continue
    feats.append({"id": gid, "name": (g.get("properties") or {}).get("name", ""), "rings": rings})

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


def path_d(rings, nd=1):
    out = []
    for r in rings:
        seg, prev = [], None
        for lon, lat in r:
            px, py = to_px(lon, lat)
            px, py = round(px, nd), round(py, nd)
            if prev == (px, py):
                continue            # drop points that collapse at this precision
            prev = (px, py)
            seg.append(f"{px:g},{py:g}")
        if len(seg) < 3:
            continue
        out.append("M" + "L".join(seg) + "Z")
    return "".join(out)


def ring_area_px(r):
    p = [to_px(lon, lat) for lon, lat in r]
    return abs(sum(p[i][0] * p[i - 1][1] - p[i - 1][0] * p[i][1] for i in range(len(p)))) / 2


countries, context = {}, []
for f in feats:
    d = path_d(f["rings"])
    if not d:
        continue
    if f["id"] in CATALOGUE:
        big = max(f["rings"], key=ring_area_px)
        bpx = [to_px(lon, lat) for lon, lat in big]
        cx = sum(p[0] for p in bpx) / len(bpx)
        cy = sum(p[1] for p in bpx) / len(bpx)
        area = ring_area_px(big)
        countries[f["id"]] = {"d": d, "cx": round(cx, 1), "cy": round(cy, 1),
                              "a": round(area, 1)}
    else:
        context.append(d)

missing = sorted(set(CATALOGUE) - set(countries))
assert not missing, ["no geometry for: " + ", ".join(CATALOGUE[m] for m in missing)]

# ---- the frame the figure actually shows -----------------------------------
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
small = sorted(((v["a"], CATALOGUE[k]) for k, v in countries.items()))[:8]
print("smallest projected areas (px^2 at 960 wide):", [(n, a) for a, n in small])
