"""Step 3: test two named lines, and ask what any straight line picks up.

1. Saint Michael's line. I draw it as the straight line (British National Grid) from St Michael's Mount through
   St Michael's Church on Glastonbury Tor, extended until it leaves Great Britain on the east coast. I count
   sites within 1 km (a corridor 2 km wide) and within 100 m, leaving out anything within 1 km of the two anchor
   points that define the line. Null: NLINES copies of the same line, rotated about its midpoint by up to
   +/-20 degrees and shifted sideways by up to +/-80 km, compared per 100 km of line over land.
2. G. H. Piper's 1882 line (quoted by Watkins): from Ysgyryd Fawr to Arthur's Stone. How far each place he named
   lies from the straight line, and how many sites in my data lie within 50 m of it, against the same line
   moved at random over the surrounding land.
3. Random lines: straight 20 km lines dropped at random over the land of each sample region and of Great Britain:
   how many sites does each pass within 50 m of?
Outputs: ../data/michael_line_null.csv, ../data/line_points.csv, ../work/r_lines.json, ../work/lines_geo.json
"""
import os, csv, json, math
import numpy as np
import shapely
from shapely.geometry import shape, LineString, Point, box
from scipy.spatial import cKDTree
from pyproj import Transformer

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
rng = np.random.default_rng(1969)
TI = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
land = shape(json.load(open(os.path.join(ROOT, "work", "land_bng.json"))))
S = list(csv.DictReader(open(os.path.join(ROOT, "data", "sites.csv"))))
X = np.array([float(s["x"]) for s in S]); Y = np.array([float(s["y"]) for s in S])
CAT = np.array([s["cat"] for s in S]); PRE = np.array([s["prehistoric"] == "1" for s in S]); CH = np.array([s["church"] == "1" for s in S])
MICH = np.array([s["michael"] == "1" for s in S])
tree = cKDTree(np.column_stack([X, Y]))
NP = {(r["line"], int(r["order"])): r for r in csv.DictReader(open(os.path.join(ROOT, "data", "named_points.csv")))}
NLINES = 2000


def near_segment(ax, ay, bx, by, maxd):
    """Indices of sites whose perpendicular distance to segment AB is <= maxd (foot inside AB), and distances, positions."""
    L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
    n = int(L // 5000) + 2; cand = set()
    for t in np.linspace(0, L, n):
        cand.update(tree.query_ball_point((ax + ux * t, ay + uy * t), 2600 + maxd))
    c = np.array(sorted(cand), dtype=int)
    if len(c) == 0: return c, np.array([]), np.array([])
    vx, vy = X[c] - ax, Y[c] - ay; t = vx * ux + vy * uy; p = np.abs(vx * uy - vy * ux)
    ok = (t >= 0) & (t <= L) & (p <= maxd)
    return c[ok], p[ok], t[ok]


LANDB = land.buffer(1000); shapely.prepare(LANDB); shapely.prepare(land)


def on_land(idx):
    return shapely.contains_xy(LANDB, X[idx], Y[idx]) if len(idx) else np.zeros(0, bool)


R = {}
# ---------------- 1. Saint Michael's line ----------------
A = NP[("michael", 0)]; B = NP[("michael", 4)]
ax, ay, bx, by = float(A["x"]), float(A["y"]), float(B["x"]), float(B["y"])
L0 = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L0, (by - ay) / L0
far = LineString([(ax, ay), (ax + ux * 900000, ay + uy * 900000)])
inter = far.intersection(land)
parts = list(getattr(inter, "geoms", [inter]))
tend = max(far.project(Point(p.coords[-1])) for p in parts if p.length > 0)
ex, ey = ax + ux * tend, ay + uy * tend
seg = LineString([(ax, ay), (ex, ey)]); land_len = seg.intersection(land).length / 1000
bearing = (math.degrees(math.atan2(ux, uy)) + 360) % 360
elon, elat = TI.transform(ex, ey)
# nearest OS Open Names populated place to the east end
best = None
for line in open("/home/claude/hist/osnames_gb.tsv"):
    p = line.rstrip("\n").split("\t")
    if p[4] != "populatedPlace": continue
    try: d = math.hypot(float(p[8]) - ex, float(p[9]) - ey)
    except ValueError: continue
    if best is None or d < best[0]: best = (d, p[0], p[5], p[12] or p[11])
anchor = lambda idx: (np.hypot(X[idx] - ax, Y[idx] - ay) <= 1000) | (np.hypot(X[idx] - bx, Y[idx] - by) <= 1000)


def tally(idx, excl_anchor):
    if excl_anchor: idx = idx[~anchor(idx)]
    return dict(all=int(len(idx)), prehistoric=int(PRE[idx].sum()), churches=int(CH[idx].sum()), michael=int(MICH[idx].sum()),
                **{c: int((CAT[idx] == c).sum()) for c in ["stone_circle", "megalith", "barrow", "hillfort", "holy_well"]})


i1, p1, t1 = near_segment(ax, ay, ex, ey, 1000); i1 = i1[on_land(i1)]
i100, _, _ = near_segment(ax, ay, ex, ey, 100); i100 = i100[on_land(i100)]
real1 = tally(i1, True); real100 = tally(i100, True)
real1_incl = tally(i1, False)
# named Michael sites: distance from the line
named = []
for o in range(5):
    r = NP[("michael", o)]; px, py = float(r["x"]), float(r["y"])
    named.append(dict(name=r["name"], off_m=round(abs((px - ax) * uy - (py - ay) * ux)), along_km=round(((px - ax) * ux + (py - ay) * uy) / 1000, 1)))
mx, my = (ax + ex) / 2, (ay + ey) / 2; half = math.hypot(ex - ax, ey - ay) / 2
nulls = []
while len(nulls) < NLINES:
    th = math.radians(rng.uniform(-20, 20)); sh = rng.uniform(-80000, 80000)
    dx, dy = math.cos(th) * ux - math.sin(th) * uy, math.sin(th) * ux + math.cos(th) * uy
    cx, cy = mx + (-uy) * sh, my + ux * sh
    a2x, a2y, b2x, b2y = cx - dx * half, cy - dy * half, cx + dx * half, cy + dy * half
    ll = LineString([(a2x, a2y), (b2x, b2y)]).intersection(land).length / 1000
    if ll < 0.5 * land_len: continue
    i, _, _ = near_segment(a2x, a2y, b2x, b2y, 1000); i = i[on_land(i)]
    j, _, _ = near_segment(a2x, a2y, b2x, b2y, 100); j = j[on_land(j)]
    t = tally(i, False); t100 = tally(j, False)
    nulls.append(dict(rot_deg=round(math.degrees(th), 2), shift_km=round(sh / 1000, 1), land_km=round(ll, 1),
                      **{f"n1km_{k}": v for k, v in t.items()}, **{f"n100m_{k}": v for k, v in t100.items()}))
with open(os.path.join(ROOT, "data", "michael_line_null.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(nulls[0])); w.writeheader(); w.writerows(nulls)
comp = {}
for band, real in [("1km", real1), ("100m", real100)]:
    for k in ["all", "prehistoric", "churches", "michael", "barrow", "hillfort", "stone_circle", "megalith", "holy_well"]:
        rate = real[k] / land_len * 100
        nr = np.array([n[f"n{band}_{k}"] / n["land_km"] * 100 for n in nulls])
        comp[f"{band}_{k}"] = dict(real=real[k], real_per100=round(rate, 2), null_mean_per100=round(nr.mean(), 2),
                                   null_lo=round(np.percentile(nr, 2.5), 2), null_hi=round(np.percentile(nr, 97.5), 2),
                                   share_null_ge=round(float((nr >= rate).mean()), 4), pct_rank=round(float((nr < rate).mean()) * 100, 1),
                                   expected_on_real_length=round(nr.mean() * land_len / 100, 1))
R["michael"] = dict(anchor_a=A["name"], anchor_b=B["name"], bearing_deg=round(bearing, 1), length_km=round(seg.length / 1000, 1),
                    land_km=round(land_len, 1), east_end=dict(lat=round(elat, 5), lon=round(elon, 5), nearest_place=best[1],
                    nearest_type=best[2], nearest_km=round(best[0] / 1000, 1), area=best[3]),
                    named=named, real_1km=real1, real_1km_incl_anchors=real1_incl, real_100m=real100, comp=comp, nlines=NLINES,
                    michael_churches_gb=int(MICH.sum()), sites_gb=len(S))
# list the sites along the line for the page and data file
rows = []
for i, p, t in zip(*near_segment(ax, ay, ex, ey, 1000)):
    if not on_land(np.array([i]))[0]: continue
    s = S[i]; rows.append(dict(line="michael", site_id=s["id"], cat=s["cat"], name=s["name"], lat=s["lat"], lon=s["lon"],
                               offset_m=round(p), along_km=round(t / 1000, 2), anchor=int(anchor(np.array([i]))[0]), michael=s["michael"]))

# ---------------- 2. Piper's line ----------------
A2 = NP[("piper", 0)]; B2 = NP[("piper", 7)]
pax, pay, pbx, pby = float(A2["x"]), float(A2["y"]), float(B2["x"]), float(B2["y"])
PL = math.hypot(pbx - pax, pby - pay); pux, puy = (pbx - pax) / PL, (pby - pay) / PL
pnamed = []
for o in range(1, 7):
    r = NP[("piper", o)]; px, py = float(r["x"]), float(r["y"])
    pnamed.append(dict(name=r["name"], off_m=round(abs((px - pax) * puy - (py - pay) * pux)), along_km=round(((px - pax) * pux + (py - pay) * puy) / 1000, 1)))
pi, pp, pt = near_segment(pax, pay, pbx, pby, 50)
inner = [i for i, t in zip(pi, pt) if 300 < t < PL - 300]
for i, p, t in zip(*near_segment(pax, pay, pbx, pby, 500)):
    s = S[i]; rows.append(dict(line="piper", site_id=s["id"], cat=s["cat"], name=s["name"], lat=s["lat"], lon=s["lon"],
                               offset_m=round(p), along_km=round(t / 1000, 2), anchor=0, michael=s["michael"]))
pn = []
pc = ((pax + pbx) / 2, (pay + pby) / 2)
while len(pn) < NLINES:
    th = rng.uniform(0, math.pi); cx, cy = pc[0] + rng.uniform(-25000, 25000), pc[1] + rng.uniform(-25000, 25000)
    dx, dy = math.cos(th), math.sin(th)
    a2x, a2y, b2x, b2y = cx - dx * PL / 2, cy - dy * PL / 2, cx + dx * PL / 2, cy + dy * PL / 2
    if not (land.contains(Point(a2x, a2y)) and land.contains(Point(b2x, b2y))): continue
    i, _, t = near_segment(a2x, a2y, b2x, b2y, 50)
    pn.append(int(((t > 300) & (t < PL - 300)).sum()))
pn = np.array(pn)
R["piper"] = dict(length_km=round(PL / 1000, 1), named=pnamed, max_off_m=max(n["off_m"] for n in pnamed),
                  sites_within_50m=len(inner), null_mean=round(float(pn.mean()), 2), null_share_ge=round(float((pn >= len(inner)).mean()), 3),
                  null_max=int(pn.max()), names_within_50m=[S[i]["name"] or S[i]["cat"] for i in inner])
with open(os.path.join(ROOT, "data", "line_points.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# ---------------- 3. Random 20 km lines ----------------
REG = {"herefordshire": (325000, 225000, 365000, 265000), "penwith": (134000, 18000, 160000, 44000),
       "wiltshire": (395000, 135000, 435000, 175000), "cambridge": (525000, 240000, 565000, 280000), "gb": None}
RL = {}
for rk, bx_ in REG.items():
    poly = land if bx_ is None else box(*bx_).intersection(land)
    x0, y0, x1, y1 = poly.bounds; vals = []; vpre = []
    LL = 20000 if rk != "penwith" else 15000
    while len(vals) < 1000:
        cx, cy = rng.uniform(x0, x1), rng.uniform(y0, y1); th = rng.uniform(0, math.pi)
        a2x, a2y, b2x, b2y = cx - math.cos(th) * LL / 2, cy - math.sin(th) * LL / 2, cx + math.cos(th) * LL / 2, cy + math.sin(th) * LL / 2
        if not all(poly.contains(Point(p)) for p in [(a2x, a2y), (cx, cy), (b2x, b2y)]): continue
        i, _, _ = near_segment(a2x, a2y, b2x, b2y, 50); vals.append(len(i)); vpre.append(int(PRE[i].sum()))
    v = np.array(vals); vp = np.array(vpre)
    RL[rk] = dict(length_km=LL / 1000, mean=round(float(v.mean()), 2), share_ge2=round(float((v >= 2).mean()), 3),
                  share_ge3=round(float((v >= 3).mean()), 3), share_ge4=round(float((v >= 4).mean()), 3), max=int(v.max()),
                  pre_mean=round(float(vp.mean()), 2), pre_share_ge3=round(float((vp >= 3).mean()), 3),
                  hist=[int((v == k).sum()) for k in range(0, 8)] + [int((v >= 8).sum())])
    print(rk, RL[rk])
R["random_lines"] = RL
json.dump(R, open(os.path.join(ROOT, "work", "r_lines.json"), "w"), indent=1)
geo = dict(michael=[[round(c, 5) for c in TI.transform(ax, ay)][::-1], [round(elat, 5), round(elon, 5)]],
           piper=[[float(A2["lat"]), float(A2["lon"])], [float(B2["lat"]), float(B2["lon"])]])
json.dump(geo, open(os.path.join(ROOT, "work", "lines_geo.json"), "w"))
print(json.dumps({k: v for k, v in R.items() if k != "random_lines"}, indent=1)[:5000])
