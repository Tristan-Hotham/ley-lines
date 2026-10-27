"""Step 8: fill paper_template.tex from ../data/results.json and compile with xelatex into
../release/paper/ (tex, figures, PDF) and copy the PDF to ../release/.
Placeholders {{path|fmt}} (int, pct0, pct1, f1, f2, raw) and {{X:TABLE1}} to {{X:TABLE3}}.
"""
import os, re, json, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
P = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Ley_Lines_Tested"
R = json.load(open(os.path.join(ROOT, "data", "results.json")))


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


esc = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")


def fmt(v, f):
    if f == "int": return f"{int(round(v)):,}"
    if f == "pct0": return f"{v * 100:.0f}\\%"
    if f == "pct1": return f"{v * 100:.1f}\\%"
    if f == "f1": return f"{v:.1f}"
    if f == "f2": return f"{v:.2f}"
    return esc(v)


S = R["sites"]
LAB = [("church", "Churches and chapels", "Wikidata (CC0)"), ("barrow", "Barrows and cairns", "OSM (ODbL), Wikidata"),
       ("hillfort", "Hillforts", "Atlas of Hillforts (CC BY-SA 4.0)"), ("stone_circle", "Stone circles", "OSM, Wikidata"),
       ("megalith", "Megaliths and standing stones", "OSM"), ("holy_well", "Holy wells", "OSM, Wikidata")]
rows = "".join(f"{l} & {s} & {S['gb_records'][k]:,} & {S['any_cat'][k]:,} \\\\\n" for k, l, s in LAB)
rows += f"\\midrule All & & {S['gb_total']:,} & {S['merged_sites']:,} sites \\\\\n"
T1 = ("\\begin{table}[H]\\centering\\small\\caption{Site records in Great Britain by type and source, and merged sites holding each type "
      "(a merged site can hold more than one type).}\\label{tab:sites}\n\\begin{tabular}{llrr}\\toprule Type & Source & Records & Merged sites\\\\\\midrule\n"
      + rows + "\\bottomrule\\end{tabular}\\end{table}")
SL = {"all": "All", "prehistoric": "Prehistoric", "churches": "Churches"}
rows = ""
for rk, g in R["regions"].items():
    for i, sk in enumerate(["all", "prehistoric", "churches"]):
        s = g["sets"][sk]; n = s["nulls"]
        cell = lambda nl: (f"{n[nl]['4']['mean']:,.1f} ({n[nl]['4']['lo']:,.0f} to {n[nl]['4']['hi']:,.0f})" if nl in n else "")
        rows += f"{esc(g['label']) if i == 0 else ''} & {SL[sk]} & {s['n']:,} & {s['obs']['4']:,} & {cell('uniform')} & {cell('jitter')} & {cell('shuffle')} \\\\\n"
    rows += "\\addlinespace\n"
T2 = ("\\begin{table}[H]\\centering\\footnotesize\\caption{Lines of four places (100 m corridor, 1 to 20 km): real count and the mean of 300 random versions, "
      "with the range holding 95\\% of them.}\\label{tab:regions}\n\\setlength{\\tabcolsep}{4pt}\\resizebox{\\textwidth}{!}{\\begin{tabular}{llrrlll}\\toprule Landscape & Places & N & Real & Even scatter & Nudged & Shuffled\\\\\\midrule\n"
      + rows + "\\bottomrule\\end{tabular}}\\end{table}")
C = R["michael"]["comp"]
ML = [("all", "All sites"), ("prehistoric", "Prehistoric"), ("barrow", "Barrows and cairns"), ("churches", "Churches"), ("michael", "St Michael churches"),
      ("megalith", "Megaliths"), ("stone_circle", "Stone circles"), ("hillfort", "Hillforts"), ("holy_well", "Holy wells")]
rows = "".join(f"{l} & {C['1km_' + k]['real']:,} & {C['1km_' + k]['expected_on_real_length']:,.1f} & {C['1km_' + k]['pct_rank']:.0f} & {C['100m_' + k]['real']:,} & {C['100m_' + k]['expected_on_real_length']:,.1f} \\\\\n" for k, l in ML)
T3 = ("\\begin{table}[H]\\centering\\small\\caption{Sites near the Saint Michael's line (anchor sites excluded) against the average of 2,000 rotated and shifted copies, "
      "scaled to the real line's length over land. Percentile: share of copies with a lower rate.}\\label{tab:michael}\n"
      "\\begin{tabular}{lrrrrr}\\toprule & \\multicolumn{3}{c}{Within 1 km} & \\multicolumn{2}{c}{Within 100 m}\\\\ Sites & Real & Expected & Percentile & Real & Expected\\\\\\midrule\n"
      + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(HERE, "paper_template.tex")).read().replace("{{X:TABLE1}}", T1).replace("{{X:TABLE2}}", T2).replace("{{X:TABLE3}}", T3)
t = re.sub(r"\{\{(.+?)\}\}", lambda m: fmt(get(m.group(1).partition("|")[0]), m.group(1).partition("|")[2] or "raw"), t)
os.makedirs(P, exist_ok=True)
shutil.copy(os.path.join(HERE, "paper_template.tex"), os.path.join(P, "paper_template.tex"))
open(os.path.join(P, NAME + ".tex"), "w").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=P, capture_output=True, text=True)
if r.returncode: print(r.stdout[-3000:])
for ext in (".aux", ".log", ".out"):
    if os.path.exists(os.path.join(P, NAME + ext)): os.remove(os.path.join(P, NAME + ext))
shutil.copy(os.path.join(P, NAME + ".pdf"), os.path.join(ROOT, "release", NAME + ".pdf"))
print("paper built", r.returncode)
