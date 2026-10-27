# Ley Lines, Tested

Are ancient sites in Britain lined up more than chance allows? Alfred Watkins saw straight alignments of churches, mounds, stones and hillforts across Herefordshire in 1921 and called them leys. This project maps {{headline.sites|int}} old sites in Great Britain, counts every straight line of three, four, five and six of them in four sample landscapes, and compares each count with random points. It also tests the Saint Michael's line and G. H. Piper's 1882 line from the Skirrid to Arthur's Stone.

**Interactive version:** https://tristan-hotham.github.io/ley-lines/

**Blog post:** https://blog.tristanhotham.com/2026/10/27/ley-lines/

By Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349). Blog: https://blog.tristanhotham.com/

## Headline results

- {{sites.gb_total|int}} records of churches (Wikidata, all dates), barrows and cairns, megaliths and standing stones, stone circles, hillforts and holy wells in Great Britain merge into {{headline.sites|int}} sites, and {{places.n|int}} places once sites within {{params.place_m|int}} m are grouped.
- Random points give lines in abundance, and the count rises steeply with density: doubling the points gives about {{headline.curve_double_n|int}} times as many lines of four, doubling the corridor width {{headline.curve_double_w|int}} times as many. 200 random points in a 40 km square with a 100 m corridor give about {{headline.curve_n200_w100_e4|int}} lines of four.
- In all four landscapes (Herefordshire, West Penwith, Avebury to Stonehenge, around Cambridge) real sites form more lines than evenly scattered points: {{headline.unif_ratio_min|f1}} to {{headline.unif_ratio_max|f1}} times as many lines of four. Herefordshire: {{headline.hf_obs4|int}} real against {{headline.hf_unif4|int}} on average.
- Against random points that keep the real clustering (each place moved up to 1 km), the real counts are {{headline.jit_ratio_min|f2}} to {{headline.jit_ratio_max|f2}} times the average and inside the 95% range in all {{headline.regions_inside_jitter|int}} landscapes (Herefordshire: {{headline.hf_jit4|int}} expected, 95% range {{headline.hf_jit4_lo|int}} to {{headline.hf_jit4_hi|int}}).
- Prehistoric sites only: West Penwith has {{headline.pen_pre_obs4|int}} lines of four against {{headline.pen_pre_uniform4|f1}} from even scatter and {{headline.pen_pre_shuffle4|f1}} from shuffled real places, but {{headline.pen_pre_jitter4|f1}} from the nudged prehistoric sites themselves, which match or beat the real count in {{headline.pen_pre_jitter4_p|pct0}} of runs.
- A random 20 km line in Britain passes within 50 m of {{headline.rl_gb_mean|f2}} sites on average; {{headline.rl_gb_ge3|pct1}} pass three or more, rising to {{headline.rl_wilts_ge3|pct0}} on the Wiltshire chalk.
- Saint Michael's line (St Michael's Mount through Glastonbury Tor to the Norfolk coast, {{michael.length_km|f1}} km): {{headline.mich_all_1km|int}} sites within 1 km against {{headline.mich_all_1km_exp|int}} for moved copies ({{headline.mich_all_1km_pct|int}}th percentile); prehistoric {{headline.mich_pre_1km|int}} against {{headline.mich_pre_1km_exp|int}} ({{headline.mich_pre_1km_pct|int}}th); St Michael churches {{headline.mich_mich_1km|int}} against {{headline.mich_mich_1km_exp|f1}} ({{headline.mich_mich_1km_pct|int}}th). Within 100 m: {{headline.mich_all_100m|int}} against {{headline.mich_all_100m_exp|int}}.
- Piper's line: the places he named lie {{piper.min_off_m|int}} m to {{piper.max_off_m|int}} m from the straight line from Ysgyryd Fawr to Arthur's Stone.

## Files

- `index.html`: the interactive page (Leaflet map of all sites with real and random lines in four landscapes, the Saint Michael's and Piper's lines, a make-your-own-leys simulator, charts).
- `header.png`: social card.
- `data/sites.csv`: {{headline.sites|int}} merged sites: id, main type, all types, prehistoric and church flags, St Michael dedication flag, subtype, name, lat, lon, British National Grid x and y, number of source records, sources, source ids.
- `data/places.csv`: sites grouped into {{places.n|int}} places (within {{params.place_m|int}} m), as used for alignments.
- `data/named_points.csv`: the named points of the Saint Michael's and Piper's lines and Blackwardine, with where each location came from.
- `data/alignments_summary.csv`: every alignment count (landscape, set of places, corridor width, k) with the mean, 95% range and share of random runs at or above the real count, for each kind of random points.
- `data/alignments_found.csv`: every maximal real line of four or more places in each landscape, with members.
- `data/density_curve.csv`: expected lines of 3, 4 and 5 for uniform points by number and corridor width.
- `data/michael_line_null.csv`: the 2,000 moved copies of the Saint Michael's line and their counts. `data/line_points.csv`: sites within 1 km of the Saint Michael's line and 500 m of Piper's line.
- `data/results.json`: every number quoted on the page, in the README, paper, blog and collage.
- `code/`: Python scripts, run in order: `01_sites.py`, `02_alignments.py` (uses `align.py`, needs numba), `03_lines.py`, `04_results.py`, `05_build_site.py`, `06_header.py`. Release outputs: `07_release_figs.py`, `08_paper.py` (fills `paper_template.tex`, needs xelatex), `09_release.py` (fills `blog_template.html`, builds Zenodo files). Collage: `reddit/collage.py`.

The raw inputs are not included; `01_sites.py` reads the cleaned outputs of my earlier projects and the shared downloads listed below.

## Method in brief

A line of k places is a set of k places whose two outer places are 1 to 20 km apart and whose other places all lie within 50 m (a 100 m corridor) of the segment between them, on the British National Grid. For each landscape and set of places I compare the real count with 300 random versions: points scattered evenly over the same land; the real places each moved up to 1 km at random; and, for prehistoric-only or church-only sets, the same number drawn from all real places in the landscape. For uniform points the expected count is C(N,2) x C(N-2,k-2) x E[(w d / A)^(k-2)], which my simulations match.

Caveats: churches are of all dates (Wikidata gives no reliable founding date for most); only six kinds of site are included, and coverage in Wikidata and OpenStreetMap is uneven (Arthur's Stone in Herefordshire is missing and I placed it from Wikipedia); {{headline.church_dec_le2|int}} churches have coordinates to two decimal places or fewer; the Saint Michael's line is my definition (Mount to Tor, extended); the "camp" on Hatterall Hill is my reading (Pen Twyn hillfort); the nudged-points test keeps clustering above 1 km, so it cannot separate lines along a ridge from the ridge itself.

## Sources and licences

- Churches: Wikidata (CC0), items in the UK that are church buildings, with coordinates, pulled {{meta.pulled|raw}}.
- Barrows, megaliths, stone circles and holy wells: OpenStreetMap (© OpenStreetMap contributors, ODbL 1.0, https://www.openstreetmap.org/copyright) and Wikidata (CC0), as cleaned in my projects Barrows of Europe, Megalith Highway, Same Shape, Different Millennia and Holy Wells.
- Hillforts: Lock, G. and Ralston, I. 2017, Atlas of Hillforts of Britain and Ireland, https://hillforts.arch.ox.ac.uk (CC BY-SA 4.0), via Middleton, M. 2024, The Hillforts Primer (https://github.com/MikeDairsie/hillforts-primer).
- OS Open Names (OGL v3): contains OS data © Crown copyright and database right 2026.
- English Wikipedia (CC BY-SA 4.0): Ley line, The Old Straight Track, Saint Michael's line, Blackwardine, Arthur's Stone, Herefordshire.
- Natural Earth (public domain): coastline for the land mask.
- Broadbent, S. 1980, Simulating the Ley Hunter, Journal of the Royal Statistical Society, Series A 143(2), 109 to 140, https://doi.org/10.2307/2981985. Williamson, T. and Bellamy, L. 1983, Ley Lines in Question. Watkins, A. 1925, The Old Straight Track.
- Base map tiles on the page: © Esri. Map library: Leaflet.

**Licence.** The derived data in `data/` include OpenStreetMap data and are released under the Open Database License (ODbL 1.0); rows from the Atlas of Hillforts also carry its CC BY-SA 4.0 terms. Text and figures are CC BY-SA 4.0. Code is MIT (see `LICENSE`).

## How to rerun

Python 3 with numpy, scipy, shapely 2, pyproj, numba, matplotlib and playwright (for the header). Run the scripts in `code/` in order from that folder. `02_alignments.py` takes a few minutes.

## Citation

Hotham, T. (2026) *Ley Lines, Tested: are ancient sites in Britain lined up more than chance allows?* Zenodo. https://doi.org/{{meta.doi|raw}}

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
