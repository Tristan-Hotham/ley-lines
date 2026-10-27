"""r/dataisbeautiful collage for Ley Lines, Tested (2400 x 3000 px, light parchment background).
Hero: Herefordshire's real places with every straight line of four or more (ochre) beside the same places nudged
up to 1 km at random (teal), which crowd the same way and draw as many lines. Numbers from ../data/results.json.
The nudged panel is one illustrative random draw (fixed seed); the counts printed come from the 300-run results.
Run from this folder: python3 collage.py
"""
import os, sys, json, csv, math
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Polygon as MPoly, Rectangle
from shapely.geometry import shape

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "code"))
from align import list_alignments, members

F = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts/")
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf"]:
    fm.fontManager.addfont(F + f)
DISP = fm.FontProperties(fname=F + "FrauncesVar.ttf", weight=900)
SER = "Source Serif 4"; MONO = "IBM Plex Mono"
BG = "#F3ECDC"; CARD = "#FBF7EE"; FG = "#25221C"; MUT = "#6B6457"; RULE = "#D9CFBA"; LAND = "#E6DCC6"
HOT = "#B7741C"; TEAL = "#1F6F78"
COL = ["#1F6F78", "#6E4C8F", "#9A6A2A", "#B0452F", "#2F6DA3", "#8E877A"]
CODE = {"stone_circle": 0, "megalith": 1, "barrow": 2, "hillfort": 3, "holy_well": 4, "church": 5}
R = json.load(open(os.path.join(ROOT, "data", "results.json"))); h = R["headline"]; g = R["regions"]
land = shape(json.load(open(os.path.join(ROOT, "work", "land_bng.json"))))
P = list(csv.DictReader(open(os.path.join(ROOT, "data", "places.csv"))))
PX = np.array([float(p["x"]) for p in P]); PY = np.array([float(p["y"]) for p in P]); PC = np.array([CODE[p["cat"]] for p in P])
BOX = (325000, 225000, 365000, 265000)
m = (PX >= BOX[0]) & (PX < BOX[2]) & (PY >= BOX[1]) & (PY < BOX[3])
x, y, c = PX[m], PY[m], PC[m]


def maximal(x, y):
    L = sorted(list_alignments(x, y, 50.0, 1000.0, 20000.0, 2), key=lambda r: (-r[2], -math.hypot(x[r[1]] - x[r[0]], y[r[1]] - y[r[0]])))
    kept = []; segs = []
    for i, j, mm in L:
        s = set(members(x, y, i, j, 50.0))
        if any(s <= k for k in kept): continue
        kept.append(s); segs.append((i, j, mm + 2))
    return segs


rng = np.random.default_rng(7)
a = rng.uniform(0, 2 * np.pi, len(x)); d = 1000 * np.sqrt(rng.uniform(0, 1, len(x)))
jx, jy = x + d * np.cos(a), y + d * np.sin(a)
real_segs = maximal(x, y); jit_segs = maximal(jx, jy)

fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BG)
# ---------- title ----------
fig.text(.045, .972, "Do Britain's ancient sites line up?", fontproperties=DISP, fontsize=44, color=FG, va="top")
fig.text(.047, .926, "In 1921 Alfred Watkins saw \"ley lines\" of churches, mounds, stones and hillforts across Herefordshire.\n"
         f"I counted every straight line of four or more old sites there, then drew the same lines through random points.",
         family=SER, fontsize=15.5, color=FG, va="top", linespacing=1.4)


# ---------- hero: two panels ----------
def panel(rect, px, py, cols, segs, col, title, sub, numtxt):
    ax = fig.add_axes(rect); ax.set_facecolor(CARD)
    lw = [3.0 if n >= 6 else 1.7 if n == 5 else .75 for i, j, n in segs]
    al = [.95 if n >= 5 else .55 for i, j, n in segs]
    lc = LineCollection([[(px[i], py[i]), (px[j], py[j])] for i, j, n in segs], colors=[matplotlib.colors.to_rgba(col, a_) for a_ in al], linewidths=lw, zorder=2)
    ax.add_collection(lc)
    ax.scatter(px, py, s=16, c=cols, lw=.5, edgecolor=CARD, zorder=3)
    ax.set_xlim(BOX[0], BOX[2]); ax.set_ylim(BOX[1], BOX[3]); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color(RULE); s.set_linewidth(1.2)
    fig.text(rect[0], rect[1] + rect[3] + .028, title, family=MONO, fontsize=13.5, color=col, weight="medium", va="bottom")
    fig.text(rect[0], rect[1] + rect[3] + .008, sub, family=MONO, fontsize=11, color=MUT, va="bottom")
    fig.text(rect[0] + rect[2], rect[1] - .008, numtxt, family=SER, fontsize=13, color=FG, va="top", ha="right")
    return ax


H4 = g["herefordshire"]["sets"]["all"]
a1 = panel([.045, .49, .44, .336], x, y, [COL[t] for t in c], real_segs, HOT, "REAL SITES",
           f"{H4['n']} places in a 40 km square around Hereford", f"{H4['obs']['4']:,} lines of four")
a2 = panel([.515, .49, .44, .336], jx, jy, TEAL, jit_segs, TEAL, "RANDOM POINTS THAT CROWD THE SAME WAY",
           "each real place moved up to 1 km at random", f"{H4['nulls']['jitter']['4']['mean']:,.0f} lines of four on average (300 runs)")
# Hereford label on the real panel
hx, hy = 351000, 239800
a1.annotate("Hereford's churches", xy=(hx, hy), xytext=(hx + 2500, hy - 11500), fontsize=11, family=MONO, color=FG,
            arrowprops=dict(arrowstyle="-", color=FG, lw=.8), zorder=5, bbox=dict(fc=CARD, ec="none", alpha=.85, pad=1.5))
fig.text(.5, .455, f"Points spread evenly instead give {H4['nulls']['uniform']['4']['mean']:,.0f} on average. "
         "Lines come from crowding: old sites cluster in towns, valleys and on chalk ridges.",
         family=SER, fontsize=13.5, color=FG, ha="center", va="top", style="italic")

# ---------- big numbers ----------
NUM = [(f"{h['curve_double_n']:.0f}x", "more chance lines of four when\nthe number of sites doubles"),
       (f"{h['regions_inside_jitter']} of 4", "landscapes where real lines match\nrandom points that crowd alike"),
       (f"{h['mich_all_1km_pct']:.0f}th", "percentile: Saint Michael's line\nagainst 2,000 moved copies"),
       (f"{h['rl_gb_ge3'] * 100:.1f}%", "of random 20 km lines in Britain\npass within 50 m of 3+ sites")]
for i, (big, small) in enumerate(NUM):
    x0 = .045 + i * .235
    fig.text(x0, .425, big, fontproperties=DISP, fontsize=40, color=HOT if i % 2 == 0 else TEAL, va="top")
    fig.text(x0, .372, small, family=SER, fontsize=12.5, color=FG, va="top", linespacing=1.35)

# ---------- supporting row ----------
fig.add_artist(plt.Line2D([.045, .955], [.318, .318], color=RULE, lw=1.2))
# (a) ratio chart
ax = fig.add_axes([.205, .095, .30, .155])
ks = ["herefordshire", "penwith", "wiltshire", "cambridge"]
for r, k in enumerate(ks):
    s = g[k]["sets"]["all"]; o = s["obs"]["4"]; yy = -r
    for n, col, off in [("uniform", MUT, .14), ("jitter", TEAL, -.14)]:
        v = s["nulls"][n]["4"]
        ax.plot([o / v["hi"], o / v["lo"]], [yy + off] * 2, color=col, lw=4, alpha=.45, solid_capstyle="round")
        ax.scatter([o / v["mean"]], [yy + off], s=48, color=col, edgecolor=BG, zorder=3)
ax.axvline(1, color=FG, lw=1.3); ax.set_xscale("log"); ax.set_xlim(.5, 8)
ax.set_xticks([.5, 1, 2, 4, 8]); ax.set_xticklabels(["0.5x", "1x", "2x", "4x", "8x"], family=MONO, fontsize=10.5, color=MUT)
ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax.tick_params(axis="x", which="minor", length=0)
ax.set_yticks([-r for r in range(4)]); ax.set_yticklabels([g[k]["label"].replace("Avebury and Stonehenge", "Avebury to\nStonehenge") for k in ks], family=MONO, fontsize=11)
ax.tick_params(axis="y", length=0); ax.set_ylim(-3.5, .5); ax.set_facecolor(BG)
for s_ in ["top", "right", "left"]: ax.spines[s_].set_visible(False)
ax.spines["bottom"].set_color(RULE)
fig.text(.045, .302, "FOUR LANDSCAPES", family=MONO, fontsize=12, color=MUT, va="top")
fig.text(.045, .284, "real lines of four ÷ random average", family=MONO, fontsize=10.5, color=MUT, va="top")
for xx, lab, col in [(.06, "even scatter", MUT), (.2, "same crowding", TEAL)]:
    fig.add_artist(plt.Line2D([xx], [.262], marker="o", ms=7, color=col, transform=fig.transFigure))
    fig.text(xx + .012, .262, lab, family=MONO, fontsize=10.5, color=col, va="center")
# (b) Saint Michael's line map
ax = fig.add_axes([.545, .085, .2, .2]); ax.set_facecolor(BG)
polys = [MPoly(np.array(p_.exterior.coords), closed=True) for p_ in getattr(land, "geoms", [land]) if p_.area > 2e7]
ax.add_collection(PatchCollection(polys, facecolor=LAND, edgecolor="none"))
NPs = {(r_["line"], int(r_["order"])): r_ for r_ in csv.DictReader(open(os.path.join(ROOT, "data", "named_points.csv")))}
A, B = NPs[("michael", 0)], NPs[("michael", 4)]
ax0, ay0, bx0, by0 = float(A["x"]), float(A["y"]), float(B["x"]), float(B["y"]); L = R["michael"]["length_km"] * 1000
ux, uy = bx0 - ax0, by0 - ay0; n_ = math.hypot(ux, uy); ux, uy = ux / n_, uy / n_
ax.plot([ax0, ax0 + ux * L], [ay0, ay0 + uy * L], color=HOT, lw=2.4, solid_capstyle="round")
for o in range(5):
    r_ = NPs[("michael", o)]; ax.scatter([float(r_["x"])], [float(r_["y"])], s=22, color=FG, zorder=3, marker="D")
ax.set_xlim(130000, 660000); ax.set_ylim(0, 560000); ax.set_aspect("equal"); ax.axis("off")
fig.text(.555, .302, "SAINT MICHAEL'S LINE", family=MONO, fontsize=12, color=MUT, va="top")
fig.text(.555, .284, f"{R['michael']['length_km']:.0f} km, Mount to Tor to Norfolk", family=MONO, fontsize=10.5, color=MUT, va="top")
# (c) Saint Michael numbers
C = R["michael"]["comp"]
rows = [("All sites", C["1km_all"]), ("Prehistoric", C["1km_prehistoric"]), ("St Michael\nchurches", C["1km_michael"])]
fig.text(.765, .262, "within 1 km    real   moved", family=MONO, fontsize=10.5, color=MUT, va="top")
for i, (lab, v) in enumerate(rows):
    yy = .238 - i * .040
    fig.text(.765, yy, lab, family=MONO, fontsize=11.5, color=FG, va="top", linespacing=1.2)
    fig.text(.892, yy, f"{v['real']:,}", family=MONO, fontsize=12.5, color=HOT, va="top", ha="right", weight="medium")
    fig.text(.955, yy, f"{v['expected_on_real_length']:,.0f}" if v["expected_on_real_length"] >= 10 else f"{v['expected_on_real_length']:.1f}",
             family=MONO, fontsize=12.5, color=MUT, va="top", ha="right")
fig.text(.765, .126, "A good line, not an\nexceptional one: none\npasses the 95th percentile.", family=SER, fontsize=11.5, color=FG, va="top", style="italic", linespacing=1.25)

# ---------- footer ----------
fig.add_artist(plt.Line2D([.045, .955], [.064, .064], color=RULE, lw=1.2))
fig.text(.045, .057, "Data: Wikidata (CC0), churches of all dates; OpenStreetMap contributors (ODbL 1.0) and Wikidata: barrows, megaliths,\n"
         "stone circles, holy wells; Atlas of Hillforts of Britain and Ireland (Lock and Ralston 2017, CC BY-SA 4.0); OS Open Names (OGL v3).\n"
         "Sites within 250 m count as one place. A line: places within 50 m of a straight segment 1 to 20 km long. Right panel:\n"
         "one random draw. Analysis and chart: Tristan Hotham, with Python and matplotlib. tristan-hotham.github.io/ley-lines",
         family=MONO, fontsize=9.4, color=MUT, va="top", linespacing=1.3)
out = os.path.join(HERE, "ley_lines_tested.png")
fig.savefig(out, dpi=200, facecolor=BG); print("written", out)
