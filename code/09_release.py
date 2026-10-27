"""Step 9: fill blog_template.html into ../release/blog/post.html (+ meta.json) and build ../release/zenodo/.
Image placeholders {{IMG|file|alt|caption}} are left for the uploader; other {{path|fmt}} come from results.json.
"""
import os, re, json, shutil, zipfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, "..")
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
NAME = "Hotham_Ley_Lines_Tested"; DOI = R["meta"]["doi"]


def get(path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f):
    if f == "int": return f"{int(round(v)):,}"
    if f == "pct0": return f"{v * 100:.0f}%"
    if f == "pct1": return f"{v * 100:.1f}%"
    if f == "f1": return f"{v:.1f}"
    if f == "f2": return f"{v:.2f}"
    return str(v)


def fill(t):
    return re.sub(r"\{\{(?!IMG\|)(.+?)\}\}", lambda m: fmt(get(m.group(1).partition("|")[0]), m.group(1).partition("|")[2] or "raw"), t)


B = os.path.join(ROOT, "release", "blog"); os.makedirs(B, exist_ok=True)
post = fill(open(os.path.join(HERE, "blog_template.html")).read())
open(os.path.join(B, "post.html"), "w").write(post)
h = R["headline"]
meta = dict(title="Ley lines, tested: are Britain's ancient sites lined up more than chance allows?", slug="ley-lines",
            excerpt=f"Alfred Watkins saw straight lines of old sites across Herefordshire in 1921. I mapped {h['sites']:,} churches, barrows, stones, hillforts and holy wells and compared every alignment with random points: crowding, not planning, explains the leys.",
            seo_description="Ley lines tested with open data: 50,000 old sites in Britain, every alignment counted in four landscapes and compared with random points.",
            tags=["ley lines", "archaeology", "Alfred Watkins", "Saint Michael's line", "statistics", "maps", "open data", "Britain"],
            header_alt="Title card reading Ley lines, tested, beside a map of West Penwith where ochre straight lines join prehistoric sites and churches")
assert len(meta["seo_description"]) < 160
json.dump(meta, open(os.path.join(B, "meta.json"), "w"), indent=1, ensure_ascii=False)

Z = os.path.join(ROOT, "release", "zenodo")
if os.path.isdir(Z): shutil.rmtree(Z)
os.makedirs(Z)
shutil.copy(os.path.join(ROOT, "release", NAME + ".pdf"), Z)
for f in ["sites.csv", "places.csv", "named_points.csv", "alignments_summary.csv", "alignments_found.csv", "density_curve.csv",
          "michael_line_null.csv", "line_points.csv", "results.json"]:
    shutil.copy(os.path.join(ROOT, "data", f), Z)
with zipfile.ZipFile(os.path.join(Z, "ley-lines_code_and_data.zip"), "w", zipfile.ZIP_DEFLATED) as z:
    for folder in ["code", "data"]:
        for fn in sorted(os.listdir(os.path.join(ROOT, folder))):
            fp = os.path.join(ROOT, folder, fn)
            if os.path.isfile(fp) and not fn.endswith(".pyc"): z.write(fp, f"ley-lines/{folder}/{fn}")
    for fn in ["README.md", "LICENSE"]: z.write(os.path.join(ROOT, fn), f"ley-lines/{fn}")
abstract = open(os.path.join(ROOT, "release", "paper", NAME + ".tex")).read()
abstract = abstract.split("\\begin{quote}\\small", 1)[1].split("\\medskip", 1)[0].strip()
abstract = (abstract.replace("\\%", "%").replace("$k$th", "kth").replace("$(k-2)$th", "(k minus 2)th").replace("\\emph{", "").replace("}", ""))
zmeta = dict(title="Ley Lines, Tested: Are Ancient Sites in Britain Lined Up More Than Chance Allows?",
             description_html=f"<p>{abstract}</p><p>Interactive version: https://tristan-hotham.github.io/ley-lines/. Data and code: https://github.com/Tristan-Hotham/ley-lines. Blog post: to follow.</p>",
             keywords=["ley lines", "alignments", "Alfred Watkins", "Saint Michael's line", "spatial statistics", "Monte Carlo simulation",
                       "archaeology", "Great Britain", "OpenStreetMap", "Wikidata"],
             licence="cc-by-sa-4.0",
             related=[{"identifier": "https://github.com/Tristan-Hotham/ley-lines", "relation": "issupplementedby", "resource_type": "software"},
                      {"identifier": "https://tristan-hotham.github.io/ley-lines/", "relation": "issupplementedby", "resource_type": "other"},
                      {"identifier": "https://www.wikidata.org", "relation": "isderivedfrom", "resource_type": "dataset"},
                      {"identifier": "https://www.openstreetmap.org", "relation": "isderivedfrom", "resource_type": "dataset"},
                      {"identifier": "https://hillforts.arch.ox.ac.uk", "relation": "isderivedfrom", "resource_type": "dataset"},
                      {"identifier": "https://github.com/MikeDairsie/hillforts-primer", "relation": "isderivedfrom", "resource_type": "dataset"},
                      {"identifier": "https://www.ordnancesurvey.co.uk/products/os-open-names", "relation": "isderivedfrom", "resource_type": "dataset"},
                      {"identifier": "https://www.naturalearthdata.com", "relation": "isderivedfrom", "resource_type": "dataset"},
                      {"identifier": "https://en.wikipedia.org/wiki/Ley_line", "relation": "isderivedfrom", "resource_type": "other"},
                      {"identifier": "https://doi.org/10.5281/zenodo.23685256", "relation": "isderivedfrom", "resource_type": "dataset"}])
json.dump(zmeta, open(os.path.join(Z, "meta.json"), "w"), indent=1, ensure_ascii=False)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", post).split())
print("post.html words", words, "; abstract words", len(abstract.split()))
