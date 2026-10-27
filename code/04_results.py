"""Step 4: gather every number into ../data/results.json and the compact page data ../work/site.json."""
import os, csv, json, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
W = lambda f: json.load(open(os.path.join(ROOT, "work", f)))
SM = W("sites_meta.json"); RA = W("r_align.json"); RL = W("r_lines.json"); SIMS = W("region_sims.json"); GEO = W("lines_geo.json")
curve = list(csv.DictReader(open(os.path.join(ROOT, "data", "density_curve.csv"))))

R = dict(meta=dict(pulled="27 October 2026", doi="10.5281/zenodo.23691885", slug="ley-lines",
                   url="https://tristan-hotham.github.io/ley-lines/", blog="https://blog.tristanhotham.com/2026/10/27/ley-lines/"))
R["sites"] = SM
R["places"] = RA["places"]
R["params"] = RA["params"]
R["regions"] = {}
for rk, rg in RA["regions"].items():
    out = dict(label=rg["label"], long=rg["long"], land_km2=rg["land_km2"], maximal_4plus=rg["maximal_4plus"],
               maximal_4plus_prehistoric_only=rg["maximal_4plus_prehistoric_only"], sim_maximal_4plus=rg["sim_maximal_4plus"], sets={})
    for sk, s in rg["sets"].items():
        w = s["widths"]["100"]
        o = dict(n=s["n"], per_100km2=s["per_100km2"], obs={k: int(v) for k, v in w["observed"].items()}, longest=w["longest"], nulls={})
        for nl, nv in w["nulls"].items():
            o["nulls"][nl] = {k: dict(mean=round(v["mean"], 1), lo=round(v["lo"], 1), hi=round(v["hi"], 1), p=v["p_ge"],
                                      ratio=(round(v["ratio"], 2) if v["ratio"] is not None else None))
                              for k, v in nv.items() if k in "3456"}
            o["nulls"][nl]["longest_mean"] = round(nv["longest_mean"], 2); o["nulls"][nl]["longest_share_ge"] = nv["longest_share_ge"]
        o["by_width"] = {wd: dict(obs4=int(s["widths"][wd]["observed"]["4"]), uniform4=round(s["widths"][wd]["nulls"]["uniform"]["4"]["mean"], 1),
                                  obs3=int(s["widths"][wd]["observed"]["3"]), uniform3=round(s["widths"][wd]["nulls"]["uniform"]["3"]["mean"], 1))
                         for wd in s["widths"]}
        out["sets"][sk] = o
    R["regions"][rk] = out
R["curve"] = dict(rows=[{k: float(v) for k, v in r.items()} for r in curve], check=RA["curve_check"])
R["michael"] = RL["michael"]; R["piper"] = RL["piper"]; R["random_lines"] = RL["random_lines"]

# ---- headline numbers used in text ----
g = R["regions"]; h = {}
h["sites"] = SM["merged_sites"]; h["places"] = RA["places"]["n"]; h["churches"] = SM["church_sites"]; h["prehistoric"] = SM["prehistoric_sites"]
H4 = g["herefordshire"]["sets"]["all"]
h["hf_obs4"] = H4["obs"]["4"]; h["hf_unif4"] = H4["nulls"]["uniform"]["4"]["mean"]; h["hf_jit4"] = H4["nulls"]["jitter"]["4"]["mean"]
h["hf_jit4_lo"] = H4["nulls"]["jitter"]["4"]["lo"]; h["hf_jit4_hi"] = H4["nulls"]["jitter"]["4"]["hi"]
h["hf_unif4_lo"] = H4["nulls"]["uniform"]["4"]["lo"]; h["hf_unif4_hi"] = H4["nulls"]["uniform"]["4"]["hi"]
h["regions_inside_jitter"] = sum(1 for rk in g if g[rk]["sets"]["all"]["nulls"]["jitter"]["4"]["lo"] <= g[rk]["sets"]["all"]["obs"]["4"] <= g[rk]["sets"]["all"]["nulls"]["jitter"]["4"]["hi"])
h["regions_above_uniform"] = sum(1 for rk in g if g[rk]["sets"]["all"]["obs"]["4"] > g[rk]["sets"]["all"]["nulls"]["uniform"]["4"]["hi"])
ratios = [g[rk]["sets"]["all"]["nulls"]["uniform"]["4"]["ratio"] for rk in g]
h["unif_ratio_min"] = min(ratios); h["unif_ratio_max"] = max(ratios)
jr = [g[rk]["sets"]["all"]["nulls"]["jitter"]["4"]["ratio"] for rk in g]
h["jit_ratio_min"] = min(jr); h["jit_ratio_max"] = max(jr)
# density scaling, from the formula at width 100 m
cv = {(int(float(r["width_m"])), int(float(r["n_points"]))): r for r in R["curve"]["rows"]}
h["curve_n100_w100_e4"] = cv[(100, 100)]["expected_4"]; h["curve_n200_w100_e4"] = cv[(100, 200)]["expected_4"]
h["curve_n400_w100_e4"] = cv[(100, 400)]["expected_4"]; h["curve_n200_w200_e4"] = cv[(200, 200)]["expected_4"]
h["curve_double_n"] = cv[(100, 400)]["expected_4"] / cv[(100, 200)]["expected_4"]
h["curve_double_w"] = cv[(200, 200)]["expected_4"] / cv[(100, 200)]["expected_4"]
h["curve_n200_w100_e3"] = cv[(100, 200)]["expected_3"]; h["curve_n200_w100_e5"] = cv[(100, 200)]["expected_5"]
m = R["michael"]; c = m["comp"]
h["mich_all_1km"] = c["1km_all"]["real"]; h["mich_all_1km_pct"] = c["1km_all"]["pct_rank"]; h["mich_all_1km_exp"] = c["1km_all"]["expected_on_real_length"]
h["mich_pre_1km"] = c["1km_prehistoric"]["real"]; h["mich_pre_1km_pct"] = c["1km_prehistoric"]["pct_rank"]; h["mich_pre_1km_exp"] = c["1km_prehistoric"]["expected_on_real_length"]
h["mich_mich_1km"] = c["1km_michael"]["real"]; h["mich_mich_1km_pct"] = c["1km_michael"]["pct_rank"]; h["mich_mich_1km_exp"] = c["1km_michael"]["expected_on_real_length"]
h["mich_all_100m"] = c["100m_all"]["real"]; h["mich_all_100m_pct"] = c["100m_all"]["pct_rank"]; h["mich_all_100m_exp"] = c["100m_all"]["expected_on_real_length"]
h["mich_ch_1km"] = c["1km_churches"]["real"]; h["mich_ch_1km_pct"] = c["1km_churches"]["pct_rank"]; h["mich_ch_1km_exp"] = c["1km_churches"]["expected_on_real_length"]
h["rl_gb_mean"] = R["random_lines"]["gb"]["mean"]; h["rl_gb_ge3"] = R["random_lines"]["gb"]["share_ge3"]
h["rl_wilts_ge3"] = R["random_lines"]["wiltshire"]["share_ge3"]; h["rl_hf_ge3"] = R["random_lines"]["herefordshire"]["share_ge3"]
h["pen_pre_obs4"] = g["penwith"]["sets"]["prehistoric"]["obs"]["4"]
for nl in ("uniform", "jitter", "shuffle"):
    h[f"pen_pre_{nl}4"] = g["penwith"]["sets"]["prehistoric"]["nulls"][nl]["4"]["mean"]
    h[f"pen_pre_{nl}4_p"] = g["penwith"]["sets"]["prehistoric"]["nulls"][nl]["4"]["p"]
h["church_dec_le2"] = sum(v for k, v in SM["church_decimals"].items() if int(k) <= 2)
h["church_dec_3"] = SM["church_decimals"].get("3", 0)
h["above_uniform_all_widths"] = int(all(s["by_width"][wd]["obs4"] > s["by_width"][wd]["uniform4"] for g_ in g.values() for s in [g_["sets"]["all"]] for wd in s["by_width"]))
R["piper"]["min_off_m"] = min(n["off_m"] for n in R["piper"]["named"])
# longest real line in each landscape (from alignments_found.csv)
F = list(csv.DictReader(open(os.path.join(ROOT, "data", "alignments_found.csv"))))
R["examples"] = {}
for rk in g:
    f = sorted([x for x in F if x["region"] == rk], key=lambda x: (-int(x["n_places"]), -float(x["length_km"])))[0]
    R["examples"][rk] = dict(n_places=int(f["n_places"]), length_km=float(f["length_km"]), names=f["member_names"].split("|"),
                             types=f["member_types"].split("|"), n_churches=f["member_types"].split("|").count("church"))
h["unif_p_max_all4"] = max(g[rk]["sets"]["all"]["nulls"]["uniform"]["4"]["p"] for rk in g)
h["unif_matches_max_all4"] = int(round(h["unif_p_max_all4"] * 300))
jp = [(g[rk]["sets"][sk]["nulls"]["jitter"][k]["p"], rk, sk, k) for rk in g for sk in g[rk]["sets"] for k in "3456"
      if g[rk]["sets"][sk]["obs"][k] > 0 or g[rk]["sets"][sk]["nulls"]["jitter"][k]["mean"] >= 0.5]
h["jit_tests"] = len(jp); h["jit_p_min"] = min(jp)[0]; h["jit_p_min_where"] = list(min(jp)[1:])
h["jit_tests_below05"] = sum(1 for x in jp if x[0] < 0.05)
h["jit_all_p_min"] = min(x[0] for x in jp if x[2] == "all")
R["headline"] = h
json.dump(R, open(os.path.join(ROOT, "data", "results.json"), "w"), indent=1)

# ---- compact page data ----
CODE = {"stone_circle": 0, "megalith": 1, "barrow": 2, "hillfort": 3, "holy_well": 4, "church": 5}
S = list(csv.DictReader(open(os.path.join(ROOT, "data", "sites.csv"))))
lat = [int(round(float(s["lat"]) * 1e4)) for s in S]; lon = [int(round(float(s["lon"]) * 1e4)) for s in S]
cats = "".join(str(CODE[s["cat"]]) for s in S)
P = list(csv.DictReader(open(os.path.join(ROOT, "data", "places.csv"))))
from pyproj import Transformer
TI = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)
boxes = {"herefordshire": (325000, 225000, 365000, 265000), "penwith": (134000, 18000, 160000, 44000),
         "wiltshire": (395000, 135000, 435000, 175000), "cambridge": (525000, 240000, 565000, 280000)}
REG = {}
found = list(csv.DictReader(open(os.path.join(ROOT, "data", "alignments_found.csv"))))
for rk, b in boxes.items():
    pl = [p for p in P if b[0] <= float(p["x"]) < b[2] and b[1] <= float(p["y"]) < b[3]]
    # keep only places inside the land part (the analysis used the land mask; points in sea are rare)
    idmap = {p["pid"]: k for k, p in enumerate(pl)}
    fr = [f for f in found if f["region"] == rk]
    fr.sort(key=lambda f: (-int(f["n_places"]), -float(f["length_km"])))
    fr = fr[:400]
    lines = [[idmap[f["members"].split("|")[0]], idmap[f["members"].split("|")[-1]], int(f["n_places"])] for f in fr]
    sim = SIMS[rk]
    slon, slat = TI.transform(np.array(sim["x"]), np.array(sim["y"]))
    segs = sorted(sim["segs"], key=lambda s: -s[2])[:400]
    corners = [TI.transform(b[0], b[1])[::-1], TI.transform(b[2], b[3])[::-1]]
    REG[rk] = dict(label=g[rk]["label"], box=[[round(corners[0][0], 4), round(corners[0][1], 4)], [round(corners[1][0], 4), round(corners[1][1], 4)]],
                   p=[[round(float(p["lat"]), 5), round(float(p["lon"]), 5), CODE[p["cat"]], (p["name"] or "")[:60], int(p["n_sites"])] for p in pl],
                   lines=lines, n_lines_total=g[rk]["maximal_4plus"],
                   sim=[[round(a, 5), round(o, 5)] for a, o in zip(slat.tolist(), slon.tolist())], simlines=[[int(s[0]), int(s[1]), int(s[2])] for s in segs],
                   n_sim_total=g[rk]["sim_maximal_4plus"])
LP = list(csv.DictReader(open(os.path.join(ROOT, "data", "line_points.csv"))))
NPs = list(csv.DictReader(open(os.path.join(ROOT, "data", "named_points.csv"))))
mnull = list(csv.DictReader(open(os.path.join(ROOT, "data", "michael_line_null.csv"))))
mrates = {k: [round(int(r[f"n1km_{k}"]) / float(r["land_km"]) * 100, 2) for r in mnull] for k in ("all", "prehistoric", "churches", "michael")}
site = dict(R=R, lat=lat, lon=lon, cat=cats, reg=REG, geo=GEO,
            lp=[[float(r["lat"]), float(r["lon"]), CODE[r["cat"]], r["name"][:60], int(r["offset_m"]), float(r["along_km"]), r["line"], int(r["michael"])] for r in LP],
            named=[[r["line"], r["name"], float(r["lat"]), float(r["lon"]), r["location_source"]] for r in NPs], mrates=mrates)
json.dump(site, open(os.path.join(ROOT, "work", "site.json"), "w"), separators=(",", ":"))
print("results.json and site.json", os.path.getsize(os.path.join(ROOT, "work", "site.json")) // 1024, "KB")
print(json.dumps(h, indent=1))
