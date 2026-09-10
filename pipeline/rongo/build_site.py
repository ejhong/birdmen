"""Assemble everything the static site needs into docs/rongo/ (data JSON + small images), served by GitHub Pages with the rest of the site."""
import os, json, shutil, random
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the Deep Memory repository; this study lives in pipeline/rongo, data/rongo, docs/rongo, inputs/rongo
SITE = os.path.join(ROOT, "docs", "rongo")
IMG = os.path.join(SITE, "img"); DATA = os.path.join(SITE, "data")
for d in (IMG, DATA): os.makedirs(d, exist_ok=True)
random.seed(11)

def thumb(src, dst, h=72, invert=False):
    if os.path.exists(dst): return
    im = Image.open(src).convert("L")
    if invert: im = Image.eval(im, lambda v: 255 - v)
    im.thumbnail((h * 3, h), Image.LANCZOS)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    # transparent ink on nothing: keep as grayscale PNG with white->transparent for nicer compositing on paper
    rgba = Image.new("RGBA", im.size, (32, 27, 18, 0))
    a = Image.eval(im, lambda v: 255 - v)
    rgba.putalpha(a)
    rgba.save(dst, optimize=True)

norm = {}
def load_norm(s):
    if s not in norm:
        norm[s] = {r["id"]: r for r in json.load(open(os.path.join(ROOT, "data", "rongo", "norm", f"{s}.json")))}
    return norm[s]

def export_glyph(script, gid):
    r = load_norm(script)[gid]
    thumb(os.path.join(ROOT, r["src"]), os.path.join(IMG, "g", script, f"{gid}.png"))
    thumb(os.path.join(ROOT, r["norm"]), os.path.join(IMG, "n", script, f"{gid}.png"), h=48, invert=True)
    return dict(id=gid, length=r["length"], endpoints=r["endpoints"], junctions=r["junctions"], loops=r["loops"])

def main():
    results = json.load(open(os.path.join(ROOT, "data", "rongo", "results", "results.json")))
    wob = json.load(open(os.path.join(ROOT, "data", "rongo", "results", "wobble.json")))
    fid = json.load(open(os.path.join(ROOT, "data", "rongo", "fidelity", "pairs.json")))
    ctrl = json.load(open(os.path.join(ROOT, "data", "rongo", "glyphs", "control_scripts.json")))
    meta = {"indus": dict(label="Indus", note="Indus valley, c. 2600 - 1900 BCE", source="Mahadevan 1977 sign list (scan)"),
            "rongorongo": dict(label="Rongorongo", note="Rapa Nui, before 1864 CE", source="Barthel 1958 Formentafeln (scan)")}
    for k, v in ctrl.items(): meta[k] = dict(label=v["label"], note=v["note"], source=f"Noto font ({v['font']})")
    for k in list(meta):
        if k in results["big"] and k not in ("indus", "rongorongo"):
            meta[k + "_w"] = dict(label=meta[k]["label"] + " (wobbled)", note=meta[k]["note"], source=meta[k]["source"] + ", elastic distortion + blur")
    # full inventories of the two target scripts + samples of the others
    inventories = {}
    for s in ("indus", "rongorongo"):
        inventories[s] = [export_glyph(s, gid) for gid in sorted(load_norm(s))]
    samples = {}
    for s in results["all"] + [k for k in meta if k.endswith("_w")]:
        ids = sorted(load_norm(s)); pick = random.sample(ids, min(14, len(ids)))
        samples[s] = [export_glyph(s, gid) for gid in pick]
    # galleries
    for key, g in list(results["galleries"].items()) + list(wob["galleries"].items()):
        a, b = key.split("|")
        for p in g: export_glyph(a, p["a"]); export_glyph(b, p["b"])
    # fidelity cells
    for p in fid["pairs"]:
        for k in ("chart_indus", "chart_rongorongo"):
            if p[k]:
                src = os.path.join(ROOT, p[k]); dst = os.path.join(IMG, "chart", os.path.basename(p[k]))
                thumb(src, dst, h=72)
                thumb(src.replace(".png", "_norm.png"), dst.replace(".png", "_norm.png"), h=48, invert=True)
        if p.get("indus"): export_glyph("indus", p["indus"])
        if p.get("rongorongo"): export_glyph("rongorongo", p["rongorongo"])
        for c in p["cand_indus"]: export_glyph("indus", c["id"])
        for c in p["cand_rongorongo"]: export_glyph("rongorongo", c["id"])
    # method figures
    fig = os.path.join(IMG, "fig"); os.makedirs(fig, exist_ok=True)
    def copy_scaled(src, dst, w):
        im = Image.open(src).convert("RGB"); im.thumbnail((w, w * 3), Image.LANCZOS); im.save(dst, optimize=True, quality=82)
    copy_scaled(os.path.join(ROOT, "data", "rongo", "fidelity", "chart.png"), os.path.join(fig, "chart.jpg"), 1100)
    copy_scaled(os.path.join(ROOT, "data", "rongo", "raw", "barthel", "tafel-005.png"), os.path.join(fig, "barthel_plate6.jpg"), 1400)
    copy_scaled(os.path.join(ROOT, "data", "rongo", "raw", "mahadevan", "signlist-000.jpg"), os.path.join(fig, "mahadevan_p32.jpg"), 900)
    copy_scaled(os.path.join(ROOT, "data", "rongo", "qa", "barthel_overlay_5.png"), os.path.join(fig, "barthel_overlay6.jpg"), 1400)
    copy_scaled(os.path.join(ROOT, "data", "rongo", "qa", "mahadevan_overlay_0.png"), os.path.join(fig, "mahadevan_overlay32.jpg"), 900)
    copy_scaled(os.path.join(ROOT, "data", "rongo", "qa", "norm_check.png"), os.path.join(fig, "norm_check.png"), 1120)
    copy_scaled(os.path.join(ROOT, "data", "rongo", "qa", "wobble_check.png"), os.path.join(fig, "wobble_check.png"), 1120)
    copy_scaled(os.path.join(ROOT, "data", "rongo", "qa", "top_lineara_linearb.png"), os.path.join(fig, "top_lineara_linearb.png"), 1400)
    for i in (0, 1): copy_scaled(os.path.join(ROOT, "data", "rongo", "qa", f"sheet_indus_{i}.png"), os.path.join(fig, f"sheet_indus_{i}.jpg"), 1536)
    for i in range(4): copy_scaled(os.path.join(ROOT, "data", "rongo", "qa", f"sheet_rongorongo_{i}.png"), os.path.join(fig, f"sheet_rongorongo_{i}.jpg"), 1536)
    # derived summaries used in the prose
    P = results["pairs"]
    def ranking(stat, script):
        rows = []
        for k, v in P.items():
            a, b = k.split("|")
            if script in (a, b): rows.append(dict(other=b if a == script else a, mean=v[stat]["mean"], sd=v[stat]["sd"]))
        return sorted(rows, key=lambda r: -r["mean"])
    def wrank(stat, key):
        rows = [dict(other=k, mean=v[stat]["mean"], sd=v[stat]["sd"]) for k, v in wob[key].items()]
        return sorted(rows, key=lambda r: -r["mean"])
    stats = ["best24", "match_rate", "nn_mean", "best24_cx", "rate_cx", "best24_chamfer", "best24_hog", "best24_dino"]
    summary = dict(
        rank_vs_rongorongo={s: ranking(s, "rongorongo") for s in stats},
        rank_vs_indus={s: ranking(s, "indus") for s in stats},
        wob_vs_rongorongo={s: wrank(s, "vs_rongorongo") for s in stats},
        wob_vs_indus={s: wrank(s, "vs_indus") for s in stats},
        all_pairs={s: sorted([dict(pair=k, mean=v[s]["mean"], sd=v[s]["sd"]) for k, v in P.items()], key=lambda r: -r["mean"]) for s in stats},
        lineup=results["lineup_rongorongo"], lineup_indus=results["lineup_indus"],
        lineup_w=wob["lineup_rongorongo"], lineup_indus_w=wob["lineup_indus"],
        fidelity=fid["summary"],
        fidelity_mean_chart=float(np.mean([p["z_chart"] for p in fid["pairs"] if "z_chart" in p])),
        fidelity_mean_catalog=float(np.mean([p["z_catalog"] for p in fid["pairs"] if "z_catalog" in p])),
        fidelity_inflated=sum(1 for p in fid["pairs"] if "z_catalog" in p and "z_chart" in p and p["z_chart"] > p["z_catalog"]),
    )
    for s in stats:
        allp = summary["all_pairs"][s]; keys = [r["pair"] for r in allp]
        summary[f"target_rank_{s}"] = keys.index("indus|rongorongo") + 1
    site = dict(meta=meta, results={k: v for k, v in results.items() if k != "galleries"}, galleries=results["galleries"],
                wobble={k: v for k, v in wob.items() if k != "galleries"}, wobble_galleries=wob["galleries"],
                fidelity=fid, inventories=inventories, samples=samples, summary=summary,
                calibration=json.load(open(os.path.join(ROOT, "data", "rongo", "features", "calibration.json"))),
                threshold=json.load(open(os.path.join(ROOT, "data", "rongo", "results", "threshold.json"))))
    json.dump(site, open(os.path.join(DATA, "site.json"), "w"))
    n = sum(len(f) for _, _, f in os.walk(IMG))
    print("images:", n, " site.json:", os.path.getsize(os.path.join(DATA, "site.json")) // 1024, "KB")

if __name__ == "__main__":
    main()
