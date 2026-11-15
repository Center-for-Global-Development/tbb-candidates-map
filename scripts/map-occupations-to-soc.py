# -*- coding: utf-8 -*-
"""TBB occupation -> SOC 2020 -> RQF / TSL mapping, v2 (post-review)."""
import openpyxl, os
from openpyxl.styles import Font, Alignment
from openpyxl.utils import get_column_letter

BASE = r"C:\Users\SamuelHuckstep(shuck\OneDrive - Center for Global Development\Green skills\Blogs\DTV blog post-announcement"
TBB = os.path.join(BASE, "TBB Candidates Across 26 Countries.xlsx")
ANNEX = os.path.join(BASE, "TSL_Stage_2_-_Annex_4_-_SOC_2020_Occupation_Information.xlsx")

# TBB occupation -> (primary SOC, alternative SOC or None, confidence, note)
M = {
"Accountant": (2421, 3533, "Medium", "Two-way: qualified accountant (RQF 6+) vs accounts technician (RQF 3-5)."),
"Administrative assistant": (4159, 4152, "Medium", "Two-way: general admin (RQF 3-5) vs data entry (RQF 1-2). 4215 PA/secretary also possible."),
"Agricultural, fishery or related laborer": (9111, None, "High", ""),
"Agronomist or related": (2112, None, "Medium", "Agronomy sits with biological scientists; 2152 environment professionals also possible. Both RQF 6+."),
"Aircraft pilot or related professional": (3511, None, "High", ""),
"Anthropologist": (2115, None, "High", ""),
"Appraiser": (3541, None, "Medium", "Read as valuer/assessor."),
"Archaeologist": (2115, None, "High", ""),
"Architect or planner": (2451, None, "Medium", "Planner would be 2452; both RQF 6+."),
"Archivist, curator, or librarian": (2472, None, "Medium", "Librarian would be 2471; both RQF 6+."),
"Armed forces/military": (3311, None, "Medium", "Other ranks assumed; officers are 1161. Both Ineligible for sponsorship."),
"Assembler (mechanical/ electrical)": (8141, None, "Medium", "8142 vehicles/metal goods equally plausible; both RQF 1-2."),
"Astrologer or related worker": (None, None, "n/a", "EXCLUDED: no SOC 2020 equivalent."),
"Athlete or sportsperson": (3431, None, "High", "Sports players are Ineligible for sponsorship."),
"Auctioneer": (3555, None, "High", ""),
"Audiologist and Speech Therapists": (2223, None, "Medium", "Audiologists would be 2259; both RQF 6+."),
"Baker or pastry-cook": (5432, None, "High", ""),
"Biologist": (2112, None, "High", ""),
"Blacksmith, tool maker, or forge worker": (5212, None, "Medium", "Tool makers specifically are 5222; both RQF 3-5."),
"Bookkeeper": (4122, None, "High", ""),
"Botanist": (2112, None, "High", ""),
"Bricklayer": (5313, None, "High", ""),
"Building construction labourer": (9129, None, "High", ""),
"Business professional not elsewhere classified": (2439, 3549, "Low", "Two-way catch-all: professional (RQF 6+) vs associate professional (RQF 3-5)."),
"Butcher": (5431, None, "High", ""),
"Carpenter or joiner": (5316, None, "High", ""),
"Cartographer": (2119, 3120, "Low", "No explicit SOC 2020 cartography code. Two-way: science professional (RQF 6+) vs CAD/drawing technician (RQF 3-5, on TSL)."),
"Cartoonist": (3411, None, "Medium", ""),
"Chef": (5434, None, "High", ""),
"Chemist": (2111, None, "Medium", "Assumes chemical scientist, not a pharmacy 'chemist' (2251)."),
"Child-care worker": (6111, 3232, "Medium", "Two-way: childcare assistant (RQF 1-2) vs qualified early years practitioner (RQF 3-5)."),
"Companion or valet": (None, None, "n/a", "EXCLUDED: no clean SOC 2020 equivalent."),
"Computer programmer": (2134, None, "High", ""),
"Construction labourer (roads, dams)": (8152, None, "Medium", "9121/9129 also fit; all RQF 1-2."),
"Cook": (5435, None, "High", ""),
"Corporate director or chief executive": (1111, None, "High", ""),
"Craft and related trades worker (pottery, hand metal work, glass maker, painter, jewelry etc.)": (5449, None, "Medium", "Spans several codes (e.g. 5441 glass/ceramics); all RQF 3-5."),
"Craftsman (wood, textile, leather)": (5442, None, "Low", "Spans 5442 wood, 5419 textiles, 5412 leather; all RQF 1-2."),
"Data entry operator": (4152, None, "High", ""),
"Decorator and commercial designer": (3421, 5323, "Low", "Two-way: interior/commercial designer (RQF 3-5, not on TSL) vs painter and decorator (RQF 3-5, on TSL)."),
"Dental Assistants and Therapists": (6133, 3213, "Medium", "Two-way: dental nurse/assistant (RQF 1-2) vs dental therapist/technician (RQF 3-5)."),
"Dentist": (2253, None, "High", ""),
"Dietician & nutritionist": (2259, None, "Medium", "No dedicated SOC 2020 code; grouped with other health professionals."),
"Draughtsperson": (3120, None, "High", ""),
"Driver and mobile-plant operator": (8229, None, "Medium", "Could be 8221/8222; all RQF 1-2."),
"Economist": (2433, None, "High", ""),
"Education methods specialist": (2329, None, "Medium", "2323 education advisers also fits; both RQF 6+."),
"Electrician": (5241, None, "High", ""),
"Employment agent or labour contractor": (3571, None, "Low", "No clean match; mapped to HR and industrial relations officers."),
"Engineer (biomedical)": (2129, None, "Medium", "No dedicated biomedical engineering code."),
"Engineer (chemical)": (2129, None, "Medium", "Chemical engineers fall in engineering professionals n.e.c."),
"Engineer (civil)": (2121, None, "High", ""),
"Engineer (electrical)": (2123, None, "High", ""),
"Engineer (electronic)": (2124, None, "High", ""),
"Engineer (industrial)": (2125, None, "Medium", "Read as production and process engineer."),
"Engineer (mechanical)": (2122, None, "High", ""),
"Engineer (other)": (2129, None, "High", ""),
"Engineer (petroleum)": (2129, None, "Medium", ""),
"Engineer, diesel": (2122, 3113, "Low", "Two-way: professional engineer (RQF 6+) vs engineering technician (RQF 3-5, on TSL)."),
"Farmer (crop and vegetable)": (5111, None, "High", ""),
"Fashion or other model": (None, None, "n/a", "EXCLUDED: no SOC 2020 equivalent."),
"Filmmaker": (3416, None, "Medium", ""),
"Finance professional": (2422, 3534, "Medium", "Two-way: finance professional (RQF 6+) vs financial accounts manager (RQF 3-5)."),
"Fire-fighter": (3313, None, "High", ""),
"Fishery, hunting or trapping labourer": (9119, None, "High", ""),
"Fishmonger": (5433, None, "High", ""),
"Floor layer or tile setter": (5322, None, "High", ""),
"Food & beverage taster or grader": (8144, 3115, "Medium", "Two-way: grader/sorter (RQF 1-2) vs quality assurance technician (RQF 3-5)."),
"Forestry worker and logger": (9112, None, "High", ""),
"Garbage collector": (9225, None, "High", ""),
"General manager (own or small business)": (1259, None, "Medium", "Sector-dependent; mapped to managers and proprietors in other services n.e.c."),
"General manager in wholesale or retail": (1150, None, "High", ""),
"Geologist": (2114, None, "High", ""),
"Geophysicist": (2114, None, "High", ""),
"Graphic designer": (2142, None, "High", ""),
"Hairdresser, barber, beautician or related": (6221, None, "Medium", "Beauticians are 6222; both RQF 1-2."),
"Healthcare professional (hospice)": (6135, None, "Low", "Per review: assumed care worker (RQF 1-2) rather than a registered health professional."),
"Healthcare professional (other)": (6135, None, "Low", "Per review: assumed care worker (RQF 1-2) rather than a registered health professional."),
"Housekeeper": (6231, None, "High", ""),
"Human resource manager": (1136, 3571, "Medium", "Two-way: HR director (RQF 6+) vs HR officer (RQF 3-5)."),
"Humanitarian worker": (4113, 2469, "Low", "Two-way: NGO officer (RQF 3-5) vs welfare professional (RQF 6+)."),
"Information technology professional": (2139, 3131, "Medium", "Two-way: IT professional (RQF 6+) vs IT technician (RQF 3-5)."),
"Inspector, building": (3581, 3114, "Low", "Two-way: inspector of standards/regulations (RQF 3-5, not on TSL) vs building and civil engineering technician (RQF 3-5, on TSL)."),
"Inspector, fire": (3581, 3313, "Low", "Two-way: inspector of standards/regulations vs fire service officer; both RQF 3-5."),
"Insurance": (3532, None, "Low", "Label gives no role; insurance underwriter assumed."),
"Judge": (2411, None, "High", ""),
"Lawyer": (2412, None, "High", ""),
"Livestock Worker": (9111, 5111, "Medium", "Two-way: farm worker (RQF 1-2) vs farmer/proprietor (RQF 3-5)."),
"Machine operator": (8139, None, "Medium", "Sector-dependent; almost all 81xx operative codes are RQF 1-2."),
"Manufacturing labourer": (8149, None, "High", ""),
"Marketing professional": (2432, 3554, "Low", "Two-way: marketing manager (RQF 6+) vs marketing associate professional (RQF 3-5)."),
"Mathematician or related professional": (2433, None, "Medium", ""),
"Mechanic": (5231, None, "Medium", "Vehicle mechanic assumed."),
"Mechanic, engine: diesel (except motor vehicle)": (5223, None, "Medium", "Metal working production and maintenance fitter assumed."),
"Medical and Dental Prosthetic Technicians": (3213, None, "High", ""),
"Medical doctor": (2211, None, "Medium", "Specialists would be 2212; both RQF 6+."),
"Metal worker": (5211, None, "Low", "Generic; 5212/5221/5223 also fit, all RQF 3-5."),
"Meteorologist": (2114, None, "High", ""),
"Mining and quarrying worker": (8132, None, "High", "Merged with 'Mining or quarry worker' for the map."),
"Mining or quarry worker": (8132, None, "High", "Merged with 'Mining and quarrying worker' for the map."),
"Motor vehicle driver (cab, truck, or other)": (8213, None, "Medium", "Spans 8211 LGV, 8212, 8214; all RQF 1-2."),
"Nursing": (2237, None, "Medium", "Confirmed at review: registered nurse (RQF 6+). An auxiliary/care-work reading would be 6131 (RQF 1-2)."),
"Optician, ophthalmic": (3211, 2252, "Low", "Two-way: dispensing optician (RQF 3-5) vs optometrist (RQF 6+). Optometrist is also a separate TBB category."),
"Optometrist": (2252, None, "High", ""),
"Other Craft and Related Workers": (5449, None, "Medium", ""),
"Other legal professional": (2419, None, "High", ""),
"Other Personal Services Workers": (None, None, "n/a", "EXCLUDED: residual ISCO-style label with no SOC 2020 equivalent."),
"Other Teaching Professionals": (2319, None, "High", ""),
"Pathologist": (2212, None, "High", ""),
"Performing artist (musician, actor/actreess, etc.)": (3413, 3415, "Medium", "Two-way: actor/entertainer (RQF 3-5) vs musician (RQF 3-5, special TSL treatment)."),
"Personal and Protective Service Worker": (None, None, "n/a", "EXCLUDED: residual ISCO major-group label with no SOC 2020 equivalent."),
"Pharmaceutical assistant": (7114, 3212, "Medium", "Two-way: dispensing assistant (RQF 1-2) vs pharmaceutical technician (RQF 3-5)."),
"Pharmacist": (2251, None, "High", ""),
"Pharmacologist": (2113, None, "Medium", ""),
"Photographer": (3417, None, "High", "Merged with 'Photographer, image or sound equipment operator' for the map."),
"Photographer, image or sound equipment operator": (3417, None, "High", "Merged with 'Photographer' for the map."),
"Physical therapist": (2221, None, "High", ""),
"Plasterer/painter/varnisher": (5321, None, "Medium", "Painters and decorators are 5323; both RQF 3-5 and both on the TSL."),
"Plumber or pipe fitter": (5315, None, "Medium", "Pipe fitters specifically are 5214; both RQF 3-5 and both on the TSL."),
"Police officer": (3312, None, "High", ""),
"Poultry producer": (5111, 9111, "Medium", "Two-way: proprietor/farmer (RQF 3-5) vs farm worker (RQF 1-2)."),
"Professor or Lecturer": (2311, None, "High", ""),
"Psychologist": (2226, None, "Medium", "Clinical psychologists are 2225; both RQF 6+."),
"Religious professional": (2463, None, "High", "Clergy are Ineligible for sponsorship."),
"Robotic Specialist": (2129, 3113, "Low", "Two-way: engineering professional (RQF 6+) vs engineering technician (RQF 3-5, on TSL)."),
"Safety, health & quality inspector": (3582, None, "Medium", "The quality side could be 3115 or 8143; all RQF 3-5."),
"Sales professional": (3552, 2432, "Medium", "Two-way: business sales executive (RQF 3-5) vs marketing/commercial manager (RQF 6+)."),
"School inspector": (2323, None, "High", ""),
"Scientist, data mining": (2133, None, "Medium", "Confirmed at review: data scientist (RQF 6+). A data-analyst reading would be 3544 (RQF 3-5, on TSL)."),
"Scribe or related worker": (None, None, "n/a", "EXCLUDED: no modern SOC 2020 equivalent."),
"Secretary": (4215, None, "Medium", "Specialist secretaries (4211-4213) are RQF 1-2."),
"Sewer, embroiderer or related": (8146, None, "Medium", "5419 textiles/garments trades n.e.c. also fits; both RQF 1-2."),
"Ship and aircraft controller or technician": (3512, None, "Low", "Confirmed at review: ship/hovercraft officer (RQF 3-5, on TSL). Air traffic controllers would be 3511 (RQF 6+)."),
"Social scientist": (2115, None, "High", ""),
"Social work professional": (2461, None, "High", ""),
"Sociologist": (2115, None, "High", ""),
"Software engineer": (2134, None, "High", ""),
"Statistician": (2433, None, "High", ""),
"Stonemason": (5312, None, "High", ""),
"Street food vendor": (7124, None, "Medium", ""),
"Surveyor, land": (2454, 3114, "Medium", "Two-way: chartered surveyor (RQF 6+) vs building/civil engineering technician (RQF 3-5, on TSL)."),
"Tailor, dressmaker or hatter": (5413, None, "High", ""),
"Teacher": (2313, None, "Low", "Phase unspecified; 2313-2317 are all RQF 6+, so the RQF level is robust even though the code is not."),
"Teller or other counter clerk": (4123, None, "High", ""),
"Tuner, musical instrument": (5449, None, "Medium", ""),
"Upholsterer or related worker": (5411, None, "High", ""),
"Veterinarian": (2240, None, "High", ""),
"Waiter, waitress, bartender, restaurant worker": (9264, None, "Medium", "Bar staff are 9265; both RQF 1-2."),
"Welder or flamecutter": (5213, None, "High", ""),
"Woodworker": (5442, 5316, "Medium", "Two-way: craft woodworker (RQF 1-2) vs carpenter/joiner (RQF 3-5, on TSL)."),
"Writer": (3412, None, "High", ""),
"Zoologist": (2112, None, "High", ""),
}

NOT_OCC = {
    "Bachelor's Degree": "EXCLUDED: not an occupation (qualification field).",
    "Freelance": "EXCLUDED: not an occupation (employment status).",
    "Housewife": "EXCLUDED: not an occupation in SOC terms (economically inactive).",
    "Student": "EXCLUDED: not an occupation (economic status).",
    "Unknown": "EXCLUDED: occupation not recorded.",
}

# merged map categories: TBB label -> label used by the map
MERGE = {
    "Mining and quarrying worker": "Mining or quarry worker",
    "Mining or quarry worker": "Mining or quarry worker",
    "Photographer": "Photographer or AV equipment operator",
    "Photographer, image or sound equipment operator": "Photographer or AV equipment operator",
}

# ---------- read the MAC annex ----------
awb = openpyxl.load_workbook(ANNEX, read_only=True, data_only=True)
soc = {}
for r in awb["Annex 4"].iter_rows(min_row=14, values_only=True):
    if r[0] is None or not str(r[0]).strip().isdigit():
        continue
    soc[int(r[0])] = {"title": (r[1] or "").strip(),
                      "rqf": (r[2] or "").strip(),
                      "tsl": (r[8] or "").strip()}
print("SOC codes loaded:", len(soc))
codes = {c for v in M.values() for c in v[:2] if c}
assert not (codes - set(soc)), sorted(codes - set(soc))


def tsl_flag(code):
    s = soc[code]["tsl"].lower()
    if s.startswith("yes"):
        return "Yes"
    if s.startswith("special"):
        return "Special treatment"
    if s.startswith("no"):
        return "No"
    return "Not assessed"  # RQF 6+ (Skilled Worker eligible anyway) or not shortlisted at Stage 1


BLANK = ("", "", "", "")


def soc_block(code):
    if not code:
        return BLANK
    return (code, soc[code]["title"], soc[code]["rqf"], tsl_flag(code))


def lookup(occ):
    """-> (map category, SOC, title, RQF, TSL, altSOC, altTitle, altRQF, altTSL,
           confidence, include, note)"""
    o = (occ or "").strip()
    if o in NOT_OCC:
        return ("", ) + BLANK + BLANK + ("n/a", "No", NOT_OCC[o])
    if o not in M:
        return ("",) * 12
    primary, alt, conf, note = M[o]
    if primary is None:
        return ("",) + BLANK + BLANK + (conf, "No", note)
    cat = MERGE.get(o, o)
    return (cat,) + soc_block(primary) + soc_block(alt) + (conf, "Yes", note)


HDRS = ["Map category", "SOC 2020 code", "SOC 2020 title", "RQF level", "On TSL (Stage 2 rec.)",
        "Alt. SOC 2020 code", "Alt. SOC 2020 title", "Alt. RQF level", "Alt. on TSL",
        "Mapping confidence", "Include in map", "Mapping note"]
WIDTHS = [34, 13, 36, 11, 16, 13, 36, 11, 14, 13, 12, 62]

wb = openpyxl.load_workbook(TBB)
bold = Font(bold=True)

for sheet, occ_col in (("Country x occupation", 1), ("Full list", 2)):
    ws = wb[sheet]
    start = ws.max_column + 1
    for i, h in enumerate(HDRS):
        c = ws.cell(row=1, column=start + i, value=h)
        c.font = bold
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.column_dimensions[get_column_letter(start + i)].width = WIDTHS[i]
    for row in range(2, ws.max_row + 1):
        occ = ws.cell(row=row, column=occ_col).value
        if occ is None or str(occ).strip() in ("", "Total"):
            continue
        for i, v in enumerate(lookup(str(occ))):
            ws.cell(row=row, column=start + i, value=v)
    print(sheet, "-> cols", get_column_letter(start), "to", get_column_letter(start + len(HDRS) - 1))

# ---------- audit sheet, one row per map category ----------
ws0 = wb["Country x occupation"]
occs = [str(ws0.cell(row=r, column=1).value).strip()
        for r in range(2, ws0.max_row + 1) if ws0.cell(row=r, column=1).value]
occs = [o for o in occs if o != "Total"]
totals = {}
for r in wb["Full list"].iter_rows(min_row=2, values_only=True):
    if r[1]:
        k = str(r[1]).strip()
        totals[k] = totals.get(k, 0) + (r[2] or 0)

if "SOC mapping" in wb.sheetnames:
    del wb["SOC mapping"]
ms = wb.create_sheet("SOC mapping")
ms.append(["TBB occupation(s)", "Candidates"] + HDRS)
for c in ms[1]:
    c.font = bold
    c.alignment = Alignment(wrap_text=True, vertical="top")

seen = set()
rows = []
for o in occs:
    cat = MERGE.get(o)
    if cat:
        if cat in seen:
            continue
        seen.add(cat)
        members = [x for x in occs if MERGE.get(x) == cat]
        rows.append((" + ".join(members), sum(totals.get(x, 0) for x in members), lookup(o)))
    else:
        rows.append((o, totals.get(o, 0), lookup(o)))
for label, n, vals in rows:
    ms.append([label, n] + list(vals))
for i, w in enumerate([46, 13] + WIDTHS):
    ms.column_dimensions[get_column_letter(i + 1)].width = w
ms.freeze_panes = "C2"

wb.save(TBB)
print("saved")

# ---------- report ----------
from collections import defaultdict
inc = defaultdict(int); exc = defaultdict(int); alt_rqf = defaultdict(int)
inc_tsl = defaultdict(int); amb = 0; amb_n = 0
for label, n, v in rows:
    if v[10] != "Yes":
        exc[label] = n
        continue
    inc[v[3]] += n
    inc_tsl[v[4]] += n
    if v[5]:
        amb += 1; amb_n += n
        alt_rqf[v[7]] += n
    else:
        alt_rqf[v[3]] += n
print("map categories:", len(rows), "included:", sum(1 for _, _, v in rows if v[10] == "Yes"))
print("included candidates:", sum(inc.values()))
print("RQF central :", dict(inc))
print("RQF alt     :", dict(alt_rqf))
print("TSL central :", dict(inc_tsl))
print("two-way categories:", amb, "candidates in them:", amb_n)
print("EXCLUDED:", sum(exc.values()))
for k, v in sorted(exc.items(), key=lambda x: -x[1]):
    print("   ", k, v)
