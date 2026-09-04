"""Assemble docs/data/s3.json and thumbnails for the study-3 page."""
import os, json
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S3 = os.path.join(ROOT, "data", "s3"); DOCS = os.path.join(ROOT, "docs")
TH = os.path.join(DOCS, "img", "s3"); os.makedirs(TH, exist_ok=True)

def thumb(path, out, h=260):
    if os.path.exists(out): return
    im = Image.open(path).convert("RGB"); im.thumbnail((h * 2, h)); im.save(out, quality=80, optimize=True)

def main():
    corpus = json.load(open(os.path.join(S3, "corpus.json"))); imgs = {im["id"]: im for im in corpus["images"]}
    res = json.load(open(os.path.join(S3, "results.json")))
    expl = json.load(open(os.path.join(S3, "results_exploratory.json")))
    jac = json.load(open(os.path.join(S3, "results_jaccard.json")))
    judge = json.load(open(os.path.join(S3, "results_judge.json"))) if os.path.exists(os.path.join(S3, "results_judge.json")) else {}
    lineup = json.load(open(os.path.join(S3, "results_lineup.json"))) if os.path.exists(os.path.join(S3, "results_lineup.json")) else {}
    if lineup:
        for key, setname in (("example", "moai_among_random"), ("example_mono", "moai_iso_among_monoliths")):
            ex = [t for t in lineup.get("trials", []) if t["set"] == setname and t["i"] == 0]
            if ex:
                lineup[key] = dict(cands=ex[0]["cands"], planted_pos=ex[0]["cands"].index(ex[0]["planted"]) + 1, ranks={t["model"]: t["planted_rank"] for t in ex}, groups=[imgs[c]["group"] for c in ex[0]["cands"]], top={t["model"]: imgs[t["cands"][t["ranking"][0] - 1]]["group"] for t in ex})
    tri = {f[:-5]: json.load(open(os.path.join(S3, "triage", f))) for f in os.listdir(os.path.join(S3, "triage")) if f.endswith(".json")}
    codes = {c: {f[:-5]: json.load(open(os.path.join(S3, "codes", c, f))) for f in os.listdir(os.path.join(S3, "codes", c)) if f.endswith(".json")} for c in ("opus", "sonnet")}
    usable = [i for i in imgs if tri.get(i, {}).get("usable") and i in codes["opus"] and i in codes["sonnet"]]
    extra = [i for i in imgs if imgs[i].get("extra_target")]
    for i in extra: thumb(os.path.join(ROOT, imgs[i]["path"]), os.path.join(TH, i + ".jpg"), h=520)
    for i in usable: thumb(os.path.join(ROOT, imgs[i]["path"]), os.path.join(TH, i + "_l.jpg"), h=520) if i in (json.load(open(os.path.join(S3, "targets.json"))).values()) else None
    # thumbnails for every usable image (they are shown in the gallery and neighbour panels)
    for i in usable: thumb(os.path.join(ROOT, imgs[i]["path"]), os.path.join(TH, i + ".jpg"))
    nfn = {r["id"]: r for r in jac["nfn"]}
    def rec(i):
        im = imgs[i]; return dict(extra=bool(im.get("extra_target")),id=i, group=im["group"], title=im["title"], page=im["page"], license=im["license"], artist=im["artist"],
                                  nn=nfn.get(i, {}).get("nn"), nn_group=nfn.get(i, {}).get("nn_group"), nn_d=nfn.get(i, {}).get("d"),
                                  notes=codes["opus"][i].get("notes", ""), notes_sonnet=codes["sonnet"][i].get("notes", ""))
    strip = lambda r: {k: v for k, v in r.items() if k != "nfn"}
    for i in extra:
        if i not in codes["opus"]: codes["opus"][i] = {}; codes["sonnet"][i] = {}
    site = dict(groups=corpus["groups"], results=strip(res), exploratory=strip(expl), jaccard=strip(jac), judge=judge, lineup={k: v for k, v in lineup.items() if k != "trials"}, images={i: rec(i) for i in usable + extra},
                nfn=jac["nfn"], nfn_exploratory=expl["nfn"], targets=json.load(open(os.path.join(S3, "targets.json"))) if os.path.exists(os.path.join(S3, "targets.json")) else {})
    os.makedirs(os.path.join(DOCS, "data"), exist_ok=True)
    import math
    def clean(o):
        if isinstance(o, float): return None if (math.isnan(o) or math.isinf(o)) else o
        if isinstance(o, dict): return {k: clean(v) for k, v in o.items()}
        if isinstance(o, list): return [clean(v) for v in o]
        return o
    json.dump(clean(site), open(os.path.join(DOCS, "data", "s3.json"), "w"), allow_nan=False)
    print("usable", len(usable), "json KB", os.path.getsize(os.path.join(DOCS, "data", "s3.json")) // 1024)

if __name__ == "__main__":
    main()
