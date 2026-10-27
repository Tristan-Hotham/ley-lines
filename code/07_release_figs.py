"""Step 7: static figures for the blog (release/blog/b_*.png, 1520 px wide) and the paper
(release/paper/fig*.png, same images). Light parchment background, house palette, no titles inside images.
All values from ../data/results.json and the data files.
"""
import os, json, csv, math
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly, Rectangle
from matplotlib.collections import PatchCollection, LineCollection
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
FD = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts/")
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf"]:
    if os.path.exists(FD + f): fm.fontManager.addfont(FD + f)
MONO = "IBM Plex Mono"
BG, FG, MUT, RULE, LAND, CARD = "#F4EEE1", "#25221C", "#6B6457", "#D9CFBA", "#E6DDC9", "#FBF7EE"
HOT, TEAL, PURP = "#B7741C", "#1F6F78", "#6E4C8F"
COL = ["#1F6F78", "#6E4C8F", "#9A6A2A", "#B0452F", "#2F6DA3", "#8E877A"]
TYPES = ["Stone circle", "Megalith", "Barrow or cairn", "Hillfort", "Holy well", "Church or chapel"]
CODE = {"stone_circle": 0, "megalith": 1, "barrow": 2, "hillfort": 3, "holy_well": 4, "church": 5}
plt.rcParams.update({"font.family": MONO, "font.size": 15, "text.color": FG, "axes.labelcolor": FG, "xtick.color": MUT, "ytick.color": MUT,
                     "axes.edgecolor": RULE, "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG})
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
B = os.path.join(ROOT, "release", "blog"); P = os.path.join(ROOT, "release", "paper")
os.makedirs(B, exist_ok=True); os.makedirs(P, exist_ok=True)
land = shape(json.load(open(os.path.join(ROOT, "work", "land_bng.json"))))
BOX = {"herefordshire": (325000, 225000, 365000, 265000), "penwith": (134000, 18000, 160000, 44000),
       "wiltshire": (395000, 135000, 435000, 175000), "cambridge": (525000, 240000, 565000, 280000)}


def save(fig, name, n):
    fig.savefig(os.path.join(B, f"b_{name}.png"), dpi=200)
    fig.savefig(os.path.join(P, f"fig{n}_{name}.png"), dpi=200)
    plt.close(fig)


def land_patches(ax, fc=LAND, ec="#CFC4AC", lw=.4):
    polys = [MPoly(np.array(p.exterior.coords), closed=True) for p in getattr(land, "geoms", [land])]
    ax.add_collection(PatchCollection(polys, facecolor=fc, edgecolor=ec, lw=lw, zorder=0))


S = list(csv.DictReader(open(os.path.join(ROOT, "data", "sites.csv"))))
SX = np.array([float(s["x"]) for s in S]); SY = np.array([float(s["y"]) for s in S]); SC = np.array([CODE[s["cat"]] for s in S])
NP = {(r["line"], int(r["order"])): r for r in csv.DictReader(open(os.path.join(ROOT, "data", "named_points.csv")))}

# ---------- 1 map of Britain ----------
fig = plt.figure(figsize=(7.6, 10.6)); ax = fig.add_axes([0, .1, 1, .9])
land_patches(ax)
for t in [5, 2, 3, 1, 0, 4]:
    m = SC == t; ax.scatter(SX[m], SY[m], s=.35 if t == 5 else 1.1, c=COL[t], lw=0, alpha=.55 if t == 5 else .85, zorder=2)
a, b = NP[("michael", 0)], NP[("michael", 4)]
ax0, ay0, bx0, by0 = float(a["x"]), float(a["y"]), float(b["x"]), float(b["y"])
L = R["michael"]["length_km"] * 1000; ux, uy = (bx0 - ax0), (by0 - ay0); n = math.hypot(ux, uy); ux, uy = ux / n, uy / n
ax.plot([ax0, ax0 + ux * L], [ay0, ay0 + uy * L], color=HOT, lw=2.2, zorder=4, solid_capstyle="round")
pass
LBL = {"herefordshire": ("Herefordshire", "left"), "penwith": ("West Penwith", "right"), "wiltshire": ("Avebury and\nStonehenge", "right"), "cambridge": ("Around\nCambridge", "left")}
for k, (x0, y0, x1, y1) in BOX.items():
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, ec=FG, lw=1.3, zorder=5))
    t, side = LBL[k]
    if k == "penwith": ax.text(x0 + 2000, y1 + 6000, t, fontsize=12, ha="left", va="bottom", zorder=6)
    elif k == "cambridge": ax.text(x1 + 6000, (y0 + y1) / 2, t, fontsize=12, ha="left", va="center", zorder=6)
    elif k == "wiltshire": ax.text((x0 + x1) / 2, y0 - 7000, t.replace("\n", " "), fontsize=12, ha="center", va="top", zorder=6, bbox=dict(fc=BG, ec="none", alpha=.7, pad=1))
    else: ax.text(x0 - 6000, (y0 + y1) / 2, t, fontsize=12, ha="right", va="center", zorder=6)
ax.set_xlim(120000, 660000); ax.set_ylim(0, 1000000); ax.set_aspect("equal"); ax.axis("off")
h = [plt.Line2D([], [], ls="", marker="o", ms=7, color=COL[t], label=TYPES[t]) for t in range(6)] + [plt.Line2D([], [], color=HOT, lw=2.5, label="Saint Michael's line"), plt.Line2D([], [], ls="", marker="s", ms=10, mfc="none", mec=FG, label="Sample landscape")]
fig.legend(handles=h, loc="lower center", ncol=3, frameon=False, prop={"family": MONO, "size": 12.5}, bbox_to_anchor=(.5, .005), columnspacing=1.2)
save(fig, "map", 1)

# ---------- 2 real against random, two landscapes ----------
P_ = list(csv.DictReader(open(os.path.join(ROOT, "data", "places.csv"))))
PX = np.array([float(p["x"]) for p in P_]); PY = np.array([float(p["y"]) for p in P_]); PC = np.array([CODE[p["cat"]] for p in P_])
PID = {p["pid"]: i for i, p in enumerate(P_)}
F = list(csv.DictReader(open(os.path.join(ROOT, "data", "alignments_found.csv"))))
SIM = json.load(open(os.path.join(ROOT, "work", "region_sims.json")))
fig, axs = plt.subplots(2, 2, figsize=(7.6, 7.9)); fig.subplots_adjust(left=.01, right=.99, top=.94, bottom=.01, wspace=.04, hspace=.1)
for r, k in enumerate(["penwith", "herefordshire"]):
    x0, y0, x1, y1 = BOX[k]
    for c, mode in enumerate(["real", "sim"]):
        ax = axs[r, c]; ax.set_facecolor("#E9ECE8")
        land_patches(ax, fc=CARD, ec="#CFC4AC", lw=.6)
        if mode == "real":
            fr = sorted([f for f in F if f["region"] == k], key=lambda f: -int(f["n_places"]))
            segs = [[(PX[PID[f["end_a"]]], PY[PID[f["end_a"]]]), (PX[PID[f["end_b"]]], PY[PID[f["end_b"]]])] for f in fr]
            ww = [2.2 if int(f["n_places"]) >= 6 else 1.2 if int(f["n_places"]) == 5 else .5 for f in fr]
            ax.add_collection(LineCollection(segs, colors=HOT, linewidths=ww, alpha=.7, zorder=2))
            m = (PX >= x0) & (PX < x1) & (PY >= y0) & (PY < y1)
            ax.scatter(PX[m], PY[m], s=9, c=[COL[t] for t in PC[m]], lw=.3, edgecolor=BG, zorder=3)
            nlines = len(fr)
        else:
            sx, sy = np.array(SIM[k]["x"]), np.array(SIM[k]["y"])
            segs = [[(sx[i], sy[i]), (sx[j], sy[j])] for i, j, n in SIM[k]["segs"]]
            ww = [2.2 if n >= 6 else 1.2 if n == 5 else .5 for i, j, n in SIM[k]["segs"]]
            ax.add_collection(LineCollection(segs, colors=TEAL, linewidths=ww, alpha=.7, zorder=2))
            ax.scatter(sx, sy, s=9, c=TEAL, lw=.3, edgecolor=BG, zorder=3)
            nlines = len(segs)
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_color(RULE)
        lab = ("Real places" if mode == "real" else "Random points")
        ax.text(.03, .97, f"{lab}\n{nlines:,} lines of 4+", transform=ax.transAxes, va="top", fontsize=11.5, color=HOT if mode == "real" else TEAL,
                bbox=dict(fc=BG, ec="none", alpha=.85, pad=2.5))
    axs[r, 0].text(0, 1.02, R["regions"][k]["label"] + f"  ({R['regions'][k]['sets']['all']['n']} places)", transform=axs[r, 0].transAxes, fontsize=13, va="bottom", weight="medium")
save(fig, "real_vs_random", 2)

# ---------- 3 density curve ----------
rows = R["curve"]["rows"]
fig, ax = plt.subplots(figsize=(7.6, 5.0)); fig.subplots_adjust(left=.2, right=.97, top=.97, bottom=.14); ax.tick_params(labelsize=12.5)
for wd, st in [(50, (MUT, 1.2, .6)), (100, (TEAL, 2.6, 1)), (200, (MUT, 1.2, .8)), (400, (MUT, 1.2, .6))]:
    rr = [r for r in rows if r["width_m"] == wd]
    ax.plot([r["density_per_100km2"] for r in rr], [r["expected_4"] for r in rr], color=st[0], lw=st[1], alpha=st[2])
    x = 2.0; y = rr[0]["expected_4"] * (x / rr[0]["density_per_100km2"]) ** 4
    ax.text(x / 1.06, y * 1.6, f"{wd} m", fontsize=12, ha="right", color=st[0], weight="medium" if wd == 100 else "normal")
pos = {"herefordshire": (.9, .3, "right"), "cambridge": (.9, 2.2, "right"), "penwith": (1.1, 1.0, "left"), "wiltshire": (.9, 1.6, "right")}
for k, g in R["regions"].items():
    s = g["sets"]["all"]; ax.scatter([s["per_100km2"]], [s["obs"]["4"]], s=70, color=HOT, edgecolor=BG, zorder=5)
    fx, fy, ha = pos[k]; ax.text(s["per_100km2"] * fx, s["obs"]["4"] * fy, g["label"], fontsize=11.5, ha=ha, va="center")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(1.2, 80); ax.set_ylim(.01, 1e6)
ax.set_xticks([2, 5, 10, 20, 50]); ax.set_xticklabels(["2", "5", "10", "20", "50"]); ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax.set_yticks([.01, 1, 100, 1e4, 1e6]); ax.set_yticklabels(["0.01", "1", "100", "10,000", "1,000,000"])
ax.set_xlabel("points (places) per 100 km²", fontsize=13); ax.set_ylabel("lines of four points", fontsize=13)
ax.grid(color=RULE, lw=.7); ax.set_axisbelow(True)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
save(fig, "density", 3)

# ---------- 4 ratio chart ----------
SL = {"all": "All places", "prehistoric": "Prehistoric only", "churches": "Churches only"}
NC = {"uniform": MUT, "jitter": TEAL, "shuffle": PURP}; NL = {"uniform": "even scatter", "jitter": "nudged", "shuffle": "shuffled"}
items = []
for k, g in R["regions"].items():
    items.append(("head", g["label"]))
    for sk in ["all", "prehistoric", "churches"]:
        s = g["sets"][sk]
        if s["obs"]["4"] == 0 and s["nulls"]["uniform"]["4"]["mean"] < 1: continue
        items.append((sk, s))
fig, ax = plt.subplots(figsize=(7.6, 7.6)); fig.subplots_adjust(left=.30, right=.97, top=.93, bottom=.08)
yy = 0; ticks = []
for it in items:
    if it[0] == "head":
        ax.annotate(it[1], xy=(.02, yy), xycoords=("figure fraction", "data"), ha="left", va="center", fontsize=12.5, weight="medium"); yy -= 1; continue
    sk, s = it; ticks.append((yy, SL[sk])); nl = list(s["nulls"])
    for q, n in enumerate(nl):
        v = s["nulls"][n]["4"]; o = s["obs"]["4"]; off = (q - (len(nl) - 1) / 2) * .22
        lo = o / v["hi"] if v["hi"] > 0 else 40; hi = o / v["lo"] if v["lo"] > 0 else 40; mid = o / v["mean"] if v["mean"] > 0 else 40
        ax.plot([max(lo, .1), min(hi, 40)], [yy + off] * 2, color=NC[n], lw=3.2, alpha=.45, solid_capstyle="round")
        ax.scatter([mid], [yy + off], s=40, color=NC[n], edgecolor=BG, zorder=3)
    yy -= 1
ax.set_yticks([t for t, _ in ticks]); ax.set_yticklabels([l for _, l in ticks], fontsize=11.5)
ax.set_xscale("log"); ax.set_xlim(.1, 40); ax.axvline(1, color=FG, lw=1.3)
ax.set_xticks([.1, .3, 1, 3, 10, 30]); ax.set_xticklabels(["0.1x", "0.3x", "1x", "3x", "10x", "30x"])
ax.set_xlabel("real lines of four ÷ average of 300 random versions", fontsize=12)
ax.grid(axis="x", color=RULE, lw=.7); ax.set_axisbelow(True); ax.tick_params(axis="y", length=0)
for s in ["top", "right", "left"]: ax.spines[s].set_visible(False)
h = [plt.Line2D([], [], ls="-", lw=3, marker="o", ms=7, color=NC[n], label=NL[n]) for n in NC]
fig.legend(handles=h, loc="upper center", ncol=3, frameon=False, prop={"family": MONO, "size": 11.5}, bbox_to_anchor=(.55, 1.0), columnspacing=1.0)
save(fig, "regions", 4)

# ---------- 5 Saint Michael histograms ----------
rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "michael_line_null.csv"))))
K = [("all", "All sites"), ("prehistoric", "Prehistoric sites"), ("churches", "Churches"), ("michael", "St Michael churches")]
fig, axs = plt.subplots(2, 2, figsize=(7.6, 5.8)); fig.subplots_adjust(left=.05, right=.97, top=.89, bottom=.1, hspace=.75, wspace=.15)
for ax, (k, name) in zip(axs.flat, K):
    v = np.array([int(r[f"n1km_{k}"]) / float(r["land_km"]) * 100 for r in rows]); c = R["michael"]["comp"][f"1km_{k}"]
    ax.hist(v, bins=28, color=MUT, alpha=.5)
    ax.axvline(c["real_per100"], color=HOT, lw=3)
    ax.set_title(f"{name}\n{c['pct_rank']:.0f}th percentile", fontsize=12, loc="left", pad=6, linespacing=1.3)
    ax.set_yticks([]); ax.tick_params(labelsize=11)
    for s in ["top", "right", "left"]: ax.spines[s].set_visible(False)
fig.text(.5, .015, "sites within 1 km, per 100 km of line (grey: 2,000 moved copies; ochre: real)", ha="center", fontsize=10.5, color=MUT)
save(fig, "michael", 5)

# ---------- 6 random lines ----------
order = ["gb", "herefordshire", "penwith", "cambridge", "wiltshire"]
L6 = {"gb": "Great Britain", "herefordshire": "Herefordshire", "penwith": "West Penwith", "cambridge": "Around Cambridge", "wiltshire": "Avebury and\nStonehenge"}
cc = ["#DDD3BF", "#7FB3B5", TEAL, HOT]; cats = ["0 sites", "1", "2", "3 or more"]
fig, ax = plt.subplots(figsize=(7.6, 4.0)); fig.subplots_adjust(left=.25, right=.97, top=.86, bottom=.06)
for i, k in enumerate(order):
    hh = R["random_lines"][k]["hist"]; tot = sum(hh); v = [hh[0], hh[1], hh[2], tot - hh[0] - hh[1] - hh[2]]; x0 = 0
    for q, n in enumerate(v):
        ax.barh(-i, n / tot, left=x0, color=cc[q], height=.7)
        if n / tot > .07 and q > 0: ax.text(x0 + n / tot / 2, -i, f"{n / tot * 100:.0f}%", ha="center", va="center", fontsize=11, color=BG if q >= 2 else FG)
        x0 += n / tot
ax.set_yticks([-i for i in range(len(order))]); ax.set_yticklabels([L6[k] for k in order], fontsize=12)
ax.set_xlim(0, 1); ax.set_xticks([]); ax.tick_params(axis="y", length=0)
for s in ax.spines.values(): s.set_visible(False)
h = [Rectangle((0, 0), 1, 1, color=cc[q], label=cats[q]) for q in range(4)]
fig.legend(handles=h, loc="upper center", ncol=4, frameon=False, prop={"family": MONO, "size": 11.5}, bbox_to_anchor=(.6, 1.0))
save(fig, "random_lines", 6)
print("figures written")
