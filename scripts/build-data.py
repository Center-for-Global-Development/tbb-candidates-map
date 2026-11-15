# -*- coding: utf-8 -*-
"""Build the map payload from the mapped TBB workbook."""
import openpyxl, os, json
from collections import defaultdict

BASE = r"C:\Users\SamuelHuckstep(shuck\OneDrive - Center for Global Development\Green skills\Blogs\DTV blog post-announcement"
TBB = os.path.join(BASE, "TBB Candidates Across 26 Countries.xlsx")
OUT = r"C:\Users\SamuelHuckstep(shuck\dev\tbb-candidates-map\data\tbb-candidates-data.js"

# M49 numeric ids as used by world-atlas countries-110m
M49 = {
    "Bangladesh": "050", "Burundi": "108", "Colombia": "170", "Costa Rica": "188",
    "Dominican Republic": "214", "Ecuador": "218", "Egypt": "818", "Ethiopia": "231",
    "Guatemala": "320", "India": "356", "Indonesia": "360", "Iraq": "368",
    "Jordan": "400", "Kenya": "404", "Lebanon": "422", "Malawi": "454",
    "Malaysia": "458", "Pakistan": "586", "Rwanda": "646", "Saudi Arabia": "682",
    "South Africa": "710", "Tanzania": "834", "Trinidad and Tobago": "780",
    "Turkiye": "792", "UAE": "784", "Uganda": "800",
}
# display names where the sheet label is not the map label
DISPLAY = {"UAE": "United Arab Emirates", "Turkiye": "Türkiye"}
# Home Office initial selection, per the written statement cited in the blog
HOME_OFFICE = ["Bangladesh", "Egypt", "India", "Kenya", "Malaysia", "Pakistan", "Uganda"]

wb = openpyxl.load_workbook(TBB, read_only=True, data_only=True)

# --- mapping metadata, keyed by TBB occupation label -----------------------
meta = {}
cats = {}   # map category -> metadata
for r in wb["SOC mapping"].iter_rows(min_row=2, values_only=True):
    label, n, cat, soc, soc_title, rqf, tsl = r[0], r[1], r[2], r[3], r[4], r[5], r[6]
    include = r[12]
    if include != "Yes":
        continue
    cats[cat] = {"cat": cat, "soc": soc, "socTitle": soc_title, "rqf": rqf,
                 "tsl": tsl, "conf": r[11], "members": label}

# --- counts, country x map category ---------------------------------------
counts = defaultdict(lambda: defaultdict(float))
occ_to_cat = {}
excluded_total = 0.0
ws = wb["Full list"]
for r in ws.iter_rows(min_row=2, values_only=True):
    country, occ, n = r[0], r[1], r[2]
    if not country or not occ:
        continue
    country, occ, n = str(country).strip(), str(occ).strip(), (n or 0)
    cat, include = r[3], r[13]
    if include != "Yes":
        excluded_total += n
        continue
    occ_to_cat[occ] = cat
    counts[cat][country] += n

countries = sorted(M49)
missing = [c for c in {c for d in counts.values() for c in d} if c not in M49]
assert not missing, missing

cat_names = sorted(cats)
rows = []
for cat in cat_names:
    m = cats[cat]
    vec = [int(round(counts[cat].get(c, 0))) for c in countries]
    rows.append({"n": cat, "soc": m["soc"], "st": m["socTitle"], "r": m["rqf"],
                 "t": m["tsl"], "c": m["conf"], "v": vec})

payload = {
    "countries": [{"id": M49[c], "name": DISPLAY.get(c, c), "sheet": c,
                   "ho": c in HOME_OFFICE} for c in countries],
    "occupations": rows,
    "excluded": int(round(excluded_total)),
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("/* TBB talent catalogue candidates by country and occupation.\n"
            "   Generated from 'TBB Candidates Across 26 Countries.xlsx'.\n"
            "   v[] is aligned to countries[]. Do not hand-edit. */\n")
    f.write("window.TBB_DATA = " + json.dumps(payload, separators=(",", ":"), ensure_ascii=False) + ";\n")

# --- checks ----------------------------------------------------------------
grand = sum(sum(r["v"]) for r in rows)
print("file bytes:", os.path.getsize(OUT))
print("map categories:", len(rows), "countries:", len(countries))
print("mapped candidates:", grand, "excluded:", payload["excluded"])
by_country = {c: sum(r["v"][i] for r in rows) for i, c in enumerate(countries)}
ho = sum(by_country[c] for c in HOME_OFFICE)
print("Home Office 7 total:", ho, f"({ho/grand:.1%})")
print("top 8 countries:", sorted(by_country.items(), key=lambda x: -x[1])[:8])
print("HO country totals:", {c: by_country[c] for c in HOME_OFFICE})
for f_rqf in ["RQF 6+", "RQF 3-5", "RQF 1-2", "Ineligible"]:
    tot = sum(sum(r["v"]) for r in rows if r["r"] == f_rqf)
    h = sum(r["v"][countries.index(c)] for r in rows if r["r"] == f_rqf for c in HOME_OFFICE)
    print(f"  {f_rqf}: {tot}  HO7 {h} ({h/tot:.1%})")
tsl = sum(sum(r["v"]) for r in rows if r["t"] == "Yes")
tsl_ho = sum(r["v"][countries.index(c)] for r in rows if r["t"] == "Yes" for c in HOME_OFFICE)
print(f"  TSL: {tsl}  HO7 {tsl_ho} ({tsl_ho/tsl:.1%})")
print("distinct TSL values:", sorted({r["t"] for r in rows}))
print("Bangladesh total:", by_country["Bangladesh"])
