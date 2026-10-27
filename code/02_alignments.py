"""Step 2: count alignments in four sample regions and compare them with chance.

Places: barrow cemeteries and town-centre churches would otherwise count many times over, so sites are first
grouped into places: in a fixed order (prehistoric first, then wells, then churches), each site joins the first
earlier place whose seed site is within PLACE_M metres, or starts a new place. A place sits at its seed site.
Alignment: see align.py. Main corridor 100 m wide (50 m either side), ends 1 to 20 km apart.
Nulls, each with the same number of places:
  uniform  points scattered at random over the same land (Natural Earth 10m coastline) in the same box
  jitter   every real place moved up to 1 km in a random direction (keeps the real clustering above 1 km)
  shuffle  for subsets (prehistoric only, churches only): the same number of places drawn at random from all
           real places in the region (keeps the real geography, drops the type)
Outputs: ../data/places.csv, ../data/alignments_summary.csv, ../data/alignments_found.csv,
         ../data/density_curve.csv, ../work/r_align.json, ../work/region_sims.json
"""
import os, csv, json, math, time
import numpy as np
import shapely
from shapely.geometry import shape, box
from align import count_alignments, list_alignments, members, KMAX

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
rng = np.random.default_rng(1925)
PLACE_M = 250.0
HALF_W = 50.0; LMIN = 1000.0; LMAX = 20000.0
WIDTHS = [50, 100, 200, 400]          # full corridor widths in metres
NSIM_MAIN = 300; NSIM_W = 100
REGIONS = {
    "herefordshire": dict(label="Herefordshire", long="Herefordshire, around Hereford and Blackwardine (Watkins's country)", box=(325000, 225000, 365000, 265000)),
    "penwith": dict(label="West Penwith", long="West Penwith, Cornwall (John Michell's case study)", box=(134000, 18000, 160000, 44000)),
    "wiltshire": dict(label="Avebury and Stonehenge", long="Wiltshire, from Avebury to Stonehenge", box=(395000, 135000, 435000, 175000)),
    "cambridge": dict(label="Around Cambridge", long="Cambridgeshire, around Cambridge (Watkins's last book)", box=(525000, 240000, 565000, 280000)),
}
land = shape(json.load(open(os.path.join(ROOT, "work", "land_bng.json"))))
S = list(csv.DictReader(open(os.path.join(ROOT, "data", "sites.csv"))))
X = np.array([float(s["x"]) for s in S]); Y = np.array([float(s["y"]) for s in S])

# ---- places (leader clustering) ----
ORDER = {"stone_circle": 0, "megalith": 1, "barrow": 2, "hillfort": 3, "holy_well": 4, "church": 5}
order = sorted(range(len(S)), key=lambda i: (ORDER[S[i]["cat"]], S[i]["id"]))
from scipy.spatial import cKDTree
seed_of = -np.ones(len(S), dtype=int)
seeds = []
grid = {}
for i in order:
    gx, gy = int(X[i] // PLACE_M), int(Y[i] // PLACE_M)
    found = -1; bestd = PLACE_M + 1
    for ax in (gx - 1, gx, gx + 1):
        for ay in (gy - 1, gy, gy + 1):
            for p in grid.get((ax, ay), ()):
                d = math.hypot(X[i] - X[seeds[p]], Y[i] - Y[seeds[p]])
                if d <= PLACE_M and d < bestd: found, bestd = p, d
    if found < 0:
        found = len(seeds); seeds.append(i); grid.setdefault((gx, gy), []).append(found)
    seed_of[i] = found
P = []
for p, i in enumerate(seeds):
    mem = np.where(seed_of == p)[0]
    cats = sorted({c for m in mem for c in S[m]["cats"].split("|")}, key=ORDER.get)
    P.append(dict(pid=f"P{p + 1:05d}", seed=S[i]["id"], cat=S[i]["cat"], cats="|".join(cats), n_sites=len(mem),
                  prehistoric=int(any(S[m]["prehistoric"] == "1" for m in mem)), church=int(any(S[m]["church"] == "1" for m in mem)),
                  name=S[i]["name"] or next((S[m]["name"] for m in mem if S[m]["name"]), ""), x=X[i], y=Y[i],
                  lat=S[i]["lat"], lon=S[i]["lon"], site_ids="|".join(S[m]["id"] for m in mem)[:300]))
with open(os.path.join(ROOT, "data", "places.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(P[0])); w.writeheader(); w.writerows(P)
PX = np.array([p["x"] for p in P]); PY = np.array([p["y"] for p in P])
PPRE = np.array([p["prehistoric"] for p in P], bool); PCH = np.array([p["church"] for p in P], bool)
# 'prehistoric' set: places holding at least one prehistoric site; 'churches': places holding a church and no prehistoric site
SETS = {"all": np.ones(len(P), bool), "prehistoric": PPRE, "churches": PCH & ~PPRE}
print("places", len(P), "prehistoric", PPRE.sum(), "church-only", (PCH & ~PPRE).sum())


def uniform(poly, n):
    x0, y0, x1, y1 = poly.bounds; out = []
    while sum(len(o) for o in out) < n:
        xs = rng.uniform(x0, x1, n * 3); ys = rng.uniform(y0, y1, n * 3)
        ok = shapely.contains_xy(poly, xs, ys); out.append(np.column_stack([xs[ok], ys[ok]]))
    a = np.vstack(out)[:n]; return a[:, 0].copy(), a[:, 1].copy()


def jitter(poly, x, y, r=1000.0):
    x = x.copy(); y = y.copy(); todo = np.arange(len(x)); ox, oy = x.copy(), y.copy()
    for _ in range(30):
        if len(todo) == 0: break
        a = rng.uniform(0, 2 * np.pi, len(todo)); d = r * np.sqrt(rng.uniform(0, 1, len(todo)))
        nx = ox[todo] + d * np.cos(a); ny = oy[todo] + d * np.sin(a)
        ok = shapely.contains_xy(poly, nx, ny)
        x[todo[ok]] = nx[ok]; y[todo[ok]] = ny[ok]; todo = todo[~ok]
    return x, y


def counts(x, y, hw):
    c, best = count_alignments(x, y, hw, LMIN, LMAX)
    return [float(c[k]) for k in range(3, KMAX + 1)], int(best)


summary = []; found = []; R = dict(regions={}, params=dict(place_m=PLACE_M, corridor_m=2 * HALF_W, lmin_km=LMIN / 1000, lmax_km=LMAX / 1000,
                                                           widths=WIDTHS, nsim_main=NSIM_MAIN, nsim_widths=NSIM_W, jitter_m=1000))
sims_for_page = {}
t0 = time.time()
for rk, rg in REGIONS.items():
    poly = box(*rg["box"]).intersection(land)
    inbox = shapely.contains_xy(poly, PX, PY)
    area = poly.area / 1e6
    RR = dict(label=rg["label"], long=rg["long"], box=rg["box"], land_km2=round(area, 1), sets={})
    for sk, sm in SETS.items():
        idx = np.where(inbox & sm)[0]; x, y = PX[idx], PY[idx]; n = len(idx)
        all_idx = np.where(inbox)[0]
        SR = dict(n=int(n), per_100km2=round(n / area * 100, 2), widths={})
        for wfull in WIDTHS:
            hw = wfull / 2; main = (wfull == 2 * HALF_W)
            obs, best = counts(x, y, hw)
            nulls = ["uniform", "jitter"] + (["shuffle"] if sk != "all" else [])
            if not main: nulls = ["uniform"]
            WR = dict(observed={str(k): obs[k - 3] for k in range(3, KMAX + 1)}, longest=best, nulls={})
            for nl in nulls:
                ns = NSIM_MAIN if main else NSIM_W
                arr = np.zeros((ns, KMAX - 2)); bests = np.zeros(ns)
                for s in range(ns):
                    if nl == "uniform": sx, sy = uniform(poly, n)
                    elif nl == "jitter": sx, sy = jitter(poly, x, y)
                    else:
                        pick = rng.choice(all_idx, n, replace=False); sx, sy = PX[pick], PY[pick]
                    c, b = counts(sx, sy, hw); arr[s] = c; bests[s] = b
                    if main and nl == "uniform" and s == 0 and sk == "all":
                        sims_for_page[rk] = (sx.copy(), sy.copy())
                NR = {}
                for k in range(3, KMAX + 1):
                    v = arr[:, k - 3]; o = obs[k - 3]
                    NR[str(k)] = dict(mean=float(v.mean()), lo=float(np.percentile(v, 2.5)), hi=float(np.percentile(v, 97.5)),
                                      p_ge=float((v >= o).mean()), ratio=(o / v.mean() if v.mean() > 0 else None))
                    summary.append(dict(region=rk, set=sk, width_m=wfull, n_places=n, k=k, observed=o, null=nl, sims=ns,
                                        null_mean=round(v.mean(), 2), null_lo95=round(np.percentile(v, 2.5), 2),
                                        null_hi95=round(np.percentile(v, 97.5), 2), share_sims_ge_observed=round((v >= o).mean(), 4),
                                        ratio_observed_to_mean=round(o / v.mean(), 3) if v.mean() > 0 else ""))
                NR["longest_mean"] = float(bests.mean()); NR["longest_max"] = int(bests.max())
                NR["longest_share_ge"] = float((bests >= best).mean())
                WR["nulls"][nl] = NR
            SR["widths"][str(wfull)] = WR
            print(rk, sk, wfull, n, obs[:3], {k: round(v["4"]["mean"], 1) for k, v in WR["nulls"].items()}, round(time.time() - t0))
        RR["sets"][sk] = SR
        # alignments of 4 or more places in the real data, main corridor (keep maximal ones only)
        if sk == "all":
            L = sorted(list_alignments(x, y, HALF_W, LMIN, LMAX, 2), key=lambda r: (-r[2], -math.hypot(x[r[1]] - x[r[0]], y[r[1]] - y[r[0]])))
            kept = []
            for i, j, m in L:
                mem = set(members(x, y, i, j, HALF_W))
                if any(mem <= k2 for k2 in kept): continue
                kept.append(mem)
                ml = list(members(x, y, i, j, HALF_W))
                found.append(dict(region=rk, n_places=len(ml), length_km=round(math.hypot(x[j] - x[i], y[j] - y[i]) / 1000, 2),
                                  end_a=P[idx[i]]["pid"], end_b=P[idx[j]]["pid"],
                                  members="|".join(P[idx[q]]["pid"] for q in ml),
                                  member_types="|".join(P[idx[q]]["cat"] for q in ml),
                                  prehistoric_only=int(all(P[idx[q]]["prehistoric"] for q in ml)),
                                  member_names="|".join((P[idx[q]]["name"] or P[idx[q]]["cat"])[:40] for q in ml)))
            RR["maximal_4plus"] = len(kept)
            RR["maximal_4plus_prehistoric_only"] = sum(1 for f in found if f["region"] == rk and f["prehistoric_only"])
            # the same for one uniform simulation, for the page
            sx, sy = sims_for_page[rk]
            Ls = sorted(list_alignments(sx, sy, HALF_W, LMIN, LMAX, 2), key=lambda r: -r[2]); ks = []; segs = []
            for i, j, m in Ls:
                mem = set(members(sx, sy, i, j, HALF_W))
                if any(mem <= k2 for k2 in ks): continue
                ks.append(mem); segs.append((i, j, m + 2))
            RR["sim_maximal_4plus"] = len(ks)
            sims_for_page[rk] = dict(x=sx.round(0).tolist(), y=sy.round(0).tolist(), segs=segs)
    R["regions"][rk] = RR

for fn, rows in [("alignments_summary.csv", summary), ("alignments_found.csv", found)]:
    with open(os.path.join(ROOT, "data", fn), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

# ---- how expected alignments grow with density and width (uniform points in a 40 km square) ----
A = 1600e6; side = 40000.0
u = rng.uniform(0, side, (2, 2, 400000)); dd = np.hypot(u[0, 0] - u[1, 0], u[0, 1] - u[1, 1])
dd = dd[(dd >= LMIN) & (dd <= LMAX)]; frac = len(dd) / 400000


def expected(n, wfull, k):
    # E = C(n,2) * C(n-2,k-2) * E[(w d / A)^(k-2) ; LMIN <= d <= LMAX]
    return math.comb(n, 2) * math.comb(n - 2, k - 2) * frac * np.mean((wfull * dd / A) ** (k - 2))


curve = []
for wfull in WIDTHS:
    for n in [25, 50, 75, 100, 150, 200, 300, 400, 500, 600, 800, 1000, 1200, 1500, 2000]:
        curve.append(dict(width_m=wfull, n_points=n, density_per_100km2=round(n / 16, 3),
                          **{f"expected_{k}": round(expected(n, wfull, k), 3) for k in (3, 4, 5)}))
check = []
for n in (100, 200, 400):
    sq = box(0, 0, side, side); vals = []
    for s in range(40):
        sx, sy = uniform(sq, n); vals.append(counts(sx, sy, HALF_W)[0])
    v = np.array(vals)
    check.append(dict(n=n, sim_mean_4=float(v[:, 1].mean()), formula_4=float(expected(n, 100, 4)),
                      sim_mean_3=float(v[:, 0].mean()), formula_3=float(expected(n, 100, 3))))
with open(os.path.join(ROOT, "data", "density_curve.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(curve[0])); w.writeheader(); w.writerows(curve)
R["curve_check"] = check
R["places"] = dict(n=len(P), prehistoric=int(PPRE.sum()), church_only=int((PCH & ~PPRE).sum()),
                   multi_site=int(sum(1 for p in P if p["n_sites"] > 1)), sites=len(S))
json.dump(R, open(os.path.join(ROOT, "work", "r_align.json"), "w"), indent=1)
json.dump(sims_for_page, open(os.path.join(ROOT, "work", "region_sims.json"), "w"))
print("done", round(time.time() - t0), check)
