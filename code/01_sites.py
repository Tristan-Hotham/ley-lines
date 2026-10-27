"""Step 1: build one point layer of old sites in Great Britain, plus the named points of two claimed lines.

Inputs (read in place, never copied):
  churches     /home/claude/hist/_data2/wikidata/ch_GB.json            Wikidata (CC0), every church with coordinates, ALL dates
  stone circles /home/claude/hist/stone-circles/data/stone_circles.csv  OSM (ODbL) + Wikidata (CC0)
  megaliths    /home/claude/hist/megalith-highway/data/megaliths.csv    OSM (ODbL), standing stones, rows, tombs
  barrows      /home/claude/hist/barrows-of-europe/data/barrows.csv     OSM (ODbL) + Wikidata (CC0), barrows and cairns
  hillforts    /home/claude/hist/within-sight/data/forts_visibility.csv Atlas of Hillforts (CC BY-SA 4.0)
  holy wells   /home/claude/hist/holy-wells/data/wells.csv              OSM (ODbL) + Wikidata (CC0), holy=True only
  OS Open Names /home/claude/hist/osnames_gb.tsv (OGL v3) for named hills and hamlets on the claimed lines
  Natural Earth 10m land (public domain) for the land mask.
Outputs: ../data/sites.csv (merged sites), ../data/named_points.csv, ../work/land_bng.json
"""
import os, csv, json, math, collections
import numpy as np
from pyproj import Transformer
from shapely.geometry import shape, Point, mapping
from shapely.prepared import prep
from shapely.ops import transform as stransform
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
H = "/home/claude/hist"
os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
T = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)
TI = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

# ---- land: Great Britain island polygons (exclude Ireland and the Isle of Man) ----
land = json.load(open(f"{H}/_data3/ne/geojson/ne_10m_land.geojson"))
polys = []
for f in land["features"]:
    g = shape(f["geometry"])
    for p in getattr(g, "geoms", [g]):
        b = p.bounds
        if not (b[0] > -11 and b[2] < 2.0 and b[1] > 49.8 and b[3] < 61.0):
            continue  # keep only islands wholly inside the British Isles box (drops Eurasia)
        polys.append(p)
ireland = [p for p in polys if p.contains(Point(-6.26, 53.35))][0]
man = [p for p in polys if p.contains(Point(-4.5, 54.2))]
gbp = [p for p in polys if p is not ireland and not any(p is m for m in man)]
from shapely.ops import unary_union
gb = unary_union(gbp)
gb_bng = stransform(lambda x, y, z=None: T.transform(x, y), gb)
json.dump(mapping(gb_bng.simplify(50)), open(os.path.join(ROOT, "work", "land_bng.json"), "w"))


def in_gb_many(lats, lons):
    """Vectorised: on Great Britain land, or within about 1 km of it (0.012 degrees), not Ireland or Man."""
    import shapely
    lats = np.asarray(lats); lons = np.asarray(lons)
    ok = (lats > 49.85) & (lats < 61) & (lons > -8.7) & (lons < 2)
    ok &= ~((lats > 54.03) & (lats < 54.43) & (lons > -4.85) & (lons < -4.3))
    ok &= ~shapely.contains_xy(ireland, lons, lats)
    inside = shapely.contains_xy(gb, lons, lats)
    near = np.zeros_like(inside)
    cand = np.where(ok & ~inside)[0]
    if len(cand):
        near[cand] = shapely.dwithin(shapely.points(lons[cand], lats[cand]), gb, 0.012)
    return ok & (inside | near)


rows = []


def add(cat, sub, name, lat, lon, src, sid, qid=""):
    rows.append(dict(cat=cat, sub=sub, name=(name or "").strip().replace(chr(8211), "-").replace(chr(8212), "-"), lat=float(lat), lon=float(lon), src=src, sid=sid, qid=qid))


# churches (Wikidata, all dates)
bad_church_coords = 0
for c in json.load(open(f"{H}/_data2/wikidata/ch_GB.json")):
    try:
        lon, lat = map(float, c["c"].replace("Point(", "").rstrip(")").split())
    except ValueError:
        bad_church_coords += 1; continue
    nm = c.get("en") or c.get("lab") or ""
    mich = c.get("ded") == "Q45581" or "michael" in nm.lower()
    add("church", "St Michael" if mich else "", nm, lat, lon, "wikidata", c["ch"], c["ch"])
# stone circles
for r in csv.DictReader(open(f"{H}/stone-circles/data/stone_circles.csv")):
    if r["country"] == "United Kingdom" and r["form"] == "stone circle":
        add("stone_circle", "stone circle", r["name"], r["lat"], r["lon"], r["src"], r["osm"] or r["qid"], r["qid"])
# megaliths and standing stones
MEG = {"menhir": "standing stone", "rows": "stone row", "circle": "stone circle", "longb": "long barrow",
       "dolmen": "dolmen", "chamber": "chambered tomb", "passage": "passage tomb", "cpw": "chambered tomb",
       "unk": "megalith", "other": "megalith"}
for r in csv.DictReader(open(f"{H}/megalith-highway/data/megaliths.csv")):
    if r["country"] != "United Kingdom": continue
    sub = MEG.get(r["cls"], "megalith")
    cat = "stone_circle" if sub == "stone circle" else "megalith"
    add(cat, sub, r["name"], r["lat"], r["lon"], "osm", r["osm"], (r["wikidata"] or "").split("/")[-1])
# barrows and cairns
for r in csv.DictReader(open(f"{H}/barrows-of-europe/data/barrows.csv")):
    if r["iso"] != "GBR": continue
    add("barrow", r["cls"], r["name"], r["lat"], r["lon"], r["src"], r["id"], (r["wd"] or "").split("/")[-1])
# hillforts (Atlas)
for r in csv.DictReader(open(f"{H}/within-sight/data/forts_visibility.csv")):
    if r["country"] in ("England", "Wales", "Scotland"):
        add("hillfort", "hillfort", r["name"], r["lat"], r["lon"], "atlas", "atlas:" + r["atlas_id"])
# holy wells
for r in csv.DictReader(open(f"{H}/holy-wells/data/wells.csv")):
    if r["nation"] in ("England", "Wales", "Scotland") and r["holy"] == "True":
        add("holy_well", "holy well", r["name"], r["lat"], r["lon"], r["src"], r["id"])

raw_n = collections.Counter(r["cat"] for r in rows)
keep = in_gb_many([r["lat"] for r in rows], [r["lon"] for r in rows])
rows = [r for r, k in zip(rows, keep) if k]
gb_n = collections.Counter(r["cat"] for r in rows)
xy = np.column_stack(T.transform(np.array([r["lon"] for r in rows]), np.array([r["lat"] for r in rows])))

# ---- merge duplicates: same Wikidata QID, or any two records within 50 m (union-find) ----
MERGE_M = 50.0
par = list(range(len(rows)))


def find(a):
    while par[a] != a:
        par[a] = par[par[a]]; a = par[a]
    return a


def union(a, b):
    a, b = find(a), find(b)
    if a != b: par[max(a, b)] = min(a, b)


byq = {}
for i, r in enumerate(rows):
    if r["qid"]:
        if r["qid"] in byq: union(i, byq[r["qid"]])
        else: byq[r["qid"]] = i
for i, j in cKDTree(xy).query_pairs(MERGE_M):
    union(i, j)
groups = collections.defaultdict(list)
for i in range(len(rows)): groups[find(i)].append(i)
PRI = ["stone_circle", "megalith", "barrow", "hillfort", "holy_well", "church"]
PRE = {"stone_circle", "megalith", "barrow", "hillfort"}
out = []
for k, (g, idx) in enumerate(sorted(groups.items())):
    cats = sorted({rows[i]["cat"] for i in idx}, key=PRI.index)
    lead = sorted(idx, key=lambda i: (PRI.index(rows[i]["cat"]), rows[i]["name"] == ""))[0]
    x, y = xy[idx].mean(axis=0)
    lon, lat = TI.transform(x, y)
    names = [rows[i]["name"] for i in idx if rows[i]["name"]]
    out.append(dict(id=f"S{k + 1:05d}", cat=cats[0], cats="|".join(cats), prehistoric=int(any(c in PRE for c in cats)),
                    church=int("church" in cats), michael=int(any(rows[i]["sub"] == "St Michael" for i in idx)),
                    sub=rows[lead]["sub"], name=names[0] if names else "", lat=round(lat, 6), lon=round(lon, 6),
                    x=round(x, 1), y=round(y, 1), n_records=len(idx),
                    sources="|".join(sorted({rows[i]["src"] for i in idx})),
                    ids="|".join(rows[i]["sid"] for i in idx)[:200]))
with open(os.path.join(ROOT, "data", "sites.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)

# ---- coordinate precision of churches (decimal places as published by Wikidata) ----
dec = collections.Counter()
for c in json.load(open(f"{H}/_data2/wikidata/ch_GB.json")):
    if "genid" in c["c"]: continue
    s = c["c"].replace("Point(", "").rstrip(")").split()[1]
    dec[min(len(s.split(".")[1]) if "." in s else 0, 6)] += 1
# ---- named points of the two claimed lines (sources recorded) ----
osn = {}
want = {"Ysgyryd Fawr", "Hatterrall Hill", "Oldcastle", "St Michael's Mount", "Glastonbury Tor", "Brent Tor",
        "Creech St Michael", "Hopton on Sea", "Blackwardine"}
for line in open(f"{H}/osnames_gb.tsv"):
    p = line.rstrip("\n").split("\t")
    if p[0] in want and p[0] not in osn:
        osn[p[0]] = (float(p[6]), float(p[7]), p[5])
NP = [
    # line, order, name, lat, lon, source
    ("piper", 0, "Ysgyryd Fawr (Skirrid Fawr)", *osn["Ysgyryd Fawr"][:2], "OS Open Names point for the hill (landform), OGL v3"),
    ("piper", 1, "Pen Twyn camp, southern end of Hatterrall Hill", 51.901619, -2.988184, "Atlas of Hillforts no. 2433, Pen Twyn, Llanfihangel Crucorney (my identification of Piper's 'camp')"),
    ("piper", 2, "Hatterrall Hill", *osn["Hatterrall Hill"][:2], "OS Open Names point for the hill (landform), OGL v3"),
    ("piper", 3, "Oldcastle", *osn["Oldcastle"][:2], "OS Open Names point for the hamlet, OGL v3"),
    ("piper", 4, "Longtown Castle", 51.956952, -2.989916, "Wikidata Q6674369 (CC0)"),
    ("piper", 5, "Urishay Castle", 52.032300, -2.988200, "Wikidata Q7900646 (CC0)"),
    ("piper", 6, "Snodhill Castle", 52.057400, -2.989690, "Wikidata Q17537708 (CC0)"),
    ("piper", 7, "Arthur's Stone, Dorstone", 52.082306, -2.995361, "English Wikipedia, Arthur's Stone, Herefordshire (infobox 52.082306 N 2.995361 W, SO318430)"),
    ("michael", 0, "St Michael's Mount", 50.11652, -5.47791, "Wikidata Q24659597 St Michael's Mount Castle (CC0)"),
    ("michael", 1, "St Michael de Rupe, Brentor", 50.6033, -4.16236, "Wikidata Q17527559 (CC0)"),
    ("michael", 2, "Creech St Michael", *osn["Creech St Michael"][:2], "OS Open Names point for the village, OGL v3"),
    ("michael", 3, "Burrow Mump church", 51.070481, -2.916189, "Wikidata Q26628318 (CC0)"),
    ("michael", 4, "St Michael's Church, Glastonbury Tor", 51.1445, -2.69903, "Wikidata Q17675070 (CC0)"),
    ("watkins", 0, "Blackwardine", 52.20545, -2.6852775, "English Wikipedia, Blackwardine (coord from Pastscape via the article)"),
]
with open(os.path.join(ROOT, "data", "named_points.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["line", "order", "name", "lat", "lon", "x", "y", "location_source"])
    for l, o, n, la, lo, s in NP:
        x, y = T.transform(lo, la); w.writerow([l, o, n, round(la, 6), round(lo, 6), round(x, 1), round(y, 1), s])

meta = dict(raw_records=dict(raw_n), gb_records=dict(gb_n), gb_total=sum(gb_n.values()), merged_sites=len(out),
            merged_by_cat=dict(collections.Counter(o["cat"] for o in out)),
            any_cat=dict(collections.Counter(c for o in out for c in o["cats"].split("|"))),
            multi_type_sites=sum(1 for o in out if "|" in o["cats"]), prehistoric_sites=sum(o["prehistoric"] for o in out),
            church_sites=sum(o["church"] for o in out), michael_churches=sum(o["michael"] for o in out),
            merge_m=MERGE_M, church_decimals=dict(sorted(dec.items())),
            gb_land_km2=round(gb_bng.area / 1e6), bad_church_coords=bad_church_coords)
json.dump(meta, open(os.path.join(ROOT, "work", "sites_meta.json"), "w"), indent=1)
print(json.dumps(meta, indent=1))
