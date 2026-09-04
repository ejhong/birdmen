"""Study 3 pilot analysis, exactly as pre-registered (docs/study3/preregistration.md).

Inputs: data/s3/corpus.json, data/s3/triage/<id>.json, data/s3/codes/<coder>/<id>.json
Output: data/s3/results.json
"""
import os, sys, json, itertools, math
import numpy as np
ALPHA_MIN = float(os.environ.get("ALPHA_MIN", "0.67"))
MODE = os.environ.get("MODE", "consensus")        # consensus (pre-registered) | average (exploratory)
OUTNAME = os.environ.get("OUTNAME", "results.json")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S3 = os.path.join(ROOT, "data", "s3")
CODERS = ["opus", "sonnet"]
CLASSES = ["bird", "human", "bird_human_hybrid", "other_hybrid", "quadruped", "reptile_or_snake", "fish", "insect_or_arachnid",
           "disc_or_circle", "container_or_bag", "weapon_or_staff", "plant_or_tree", "geometric_band", "text_or_glyphs"]
POS = {"top": 0, "middle": 1, "bottom": 2}
rng = np.random.default_rng(3)

def load():
    corpus = json.load(open(os.path.join(S3, "corpus.json")))
    imgs = {im["id"]: im for im in corpus["images"]}
    tri = {}
    for f in os.listdir(os.path.join(S3, "triage")):
        if f.endswith(".json"): tri[f[:-5]] = json.load(open(os.path.join(S3, "triage", f)))
    codes = {c: {} for c in CODERS}
    for c in CODERS:
        d = os.path.join(S3, "codes", c)
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith(".json"):
                    j = json.load(open(os.path.join(d, f)))
                    if "error" not in j: codes[c][f[:-5]] = j
    return corpus, imgs, tri, codes

def features_of(code):
    """Flatten one coder's JSON into {feature: nominal value}."""
    f = {"registers": str(code.get("registers", "")), "facing_pair": str(code.get("facing_pair", "")),
         "bilateral_symmetry": str(code.get("bilateral_symmetry", "")), "dominant_figure": code.get("dominant_figure", ""),
         "headless_human": str(code.get("headless_human", "")), "bird_posture": code.get("bird_posture", ""),
         "hybrid_type": code.get("hybrid_type", ""), "medium": code.get("medium", "")}
    el = code.get("elements", {}) or {}
    for c in CLASSES:
        e = el.get(c, {}) or {}
        pres = bool(e.get("present", False)); f[f"{c}.present"] = str(pres)
        f[f"{c}.position"] = e.get("position", "none") if pres else "none"
    return f

def alpha_nominal(pairs):
    """Krippendorff's alpha for two coders, nominal data. pairs: list of (a, b)."""
    vals = [v for p in pairs for v in p]; n = len(vals)
    if n < 4: return float("nan")
    cats = sorted(set(vals)); idx = {c: i for i, c in enumerate(cats)}
    o = np.zeros((len(cats), len(cats)))
    for a, b in pairs: o[idx[a], idx[b]] += 1; o[idx[b], idx[a]] += 1
    nc = o.sum(1)
    Do = sum(o[i, j] for i in range(len(cats)) for j in range(len(cats)) if i != j) / (n - 1) if n > 1 else 0
    De = sum(nc[i] * nc[j] for i in range(len(cats)) for j in range(len(cats)) if i != j) / (n * (n - 1)) if n > 1 else 0
    if De == 0: return 1.0
    return float(1 - Do / De)

def main():
    corpus, imgs, tri, codes = load()
    usable = [i for i in imgs if tri.get(i, {}).get("usable") and all(i in codes[c] for c in CODERS)]
    groups = corpus["groups"]
    F = {c: {i: features_of(codes[c][i]) for i in usable} for c in CODERS}
    feats = sorted(next(iter(F["opus"].values())).keys()) if usable else []
    # reliability
    alpha = {}
    for ft in feats:
        pairs = [(F["opus"][i][ft], F["sonnet"][i][ft]) for i in usable]
        alpha[ft] = alpha_nominal(pairs)
    keep = [ft for ft in feats if not math.isnan(alpha[ft]) and alpha[ft] >= ALPHA_MIN and ft != "medium"]
    # consensus (agreement only; disagreements missing)
    cons = {i: {ft: (F["opus"][i][ft] if F["opus"][i][ft] == F["sonnet"][i][ft] else None) for ft in keep} for i in usable}
    def mism(ft, x, y):
        if ft.endswith(".position") and x in POS and y in POS: return abs(POS[x] - POS[y]) / 2
        return 0.0 if x == y else 1.0
    def dist(a, b):
        num, den = 0.0, 0
        for ft in keep:
            if MODE in ("average", "jaccard"):   # exploratory: mean of the two coders' mismatches, disagreement kept as noise
                for c in CODERS:
                    x, y = F[c][a][ft], F[c][b][ft]
                    if MODE == "jaccard" and ((ft.endswith(".present") and x == "False" and y == "False") or (ft.endswith(".position") and x == "none" and y == "none")):
                        continue                 # jaccard variant: a shared absence says nothing about similarity
                    num += 0.5 * mism(ft, x, y); den += 0.5
            else:
                x, y = cons[a][ft], cons[b][ft]
                if x is None or y is None: continue
                num += mism(ft, x, y); den += 1
        return num / den if den >= max(6, len(keep) // 3) else float("nan")
    ids = usable; n = len(ids); D = np.full((n, n), np.nan)
    for a in range(n):
        for b in range(a + 1, n): D[a, b] = D[b, a] = dist(ids[a], ids[b])
    grp = np.array([imgs[i]["group"] for i in ids])
    # 1. nearest foreign neighbour
    nfn = {}
    for a in range(n):
        m = (grp != grp[a]) & ~np.isnan(D[a]); nfn[ids[a]] = (float(np.nanmin(D[a][m])), ids[int(np.flatnonzero(m)[np.argmin(D[a][m])])]) if m.any() else (float("nan"), None)
    nfn_vals = np.array([v[0] for v in nfn.values() if not math.isnan(v[0])])
    # target pair: identify by triage tags (the coder marks 'pillar43'/'hoa_back' via a separate manual tag file)
    tags = json.load(open(os.path.join(S3, "targets.json"))) if os.path.exists(os.path.join(S3, "targets.json")) else {}
    target = {}
    if tags.get("pillar43") in ids and tags.get("hoa_back") in ids:
        a, b = ids.index(tags["pillar43"]), ids.index(tags["hoa_back"]); d = D[a, b]
        target = dict(distance=float(d), percentile=float((nfn_vals < d).mean() * 100) if not math.isnan(d) else None,
                      p43_nfn=nfn[tags["pillar43"]], hoa_nfn=nfn[tags["hoa_back"]],
                      drivers={ft: dict(p43=cons[tags["pillar43"]][ft], hoa=cons[tags["hoa_back"]][ft]) for ft in keep})
        # base rates for the drivers
        base = {ft: {} for ft in keep}
        for ft in keep:
            vals = [cons[i][ft] for i in ids if cons[i][ft] is not None]
            for v in set(vals): base[ft][v] = round(vals.count(v) / max(1, len(vals)), 3)
        target["base_rates"] = base
    # 2. group distances
    G = sorted(groups); gd = {}
    for g1, g2 in itertools.combinations_with_replacement(G, 2):
        m = D[np.ix_(grp == g1, grp == g2)]
        if g1 == g2:
            iu = np.triu_indices(m.shape[0], 1); vals = m[iu]
        else: vals = m.ravel()
        vals = vals[~np.isnan(vals)]
        gd[f"{g1}|{g2}"] = float(vals.mean()) if len(vals) else None
    # 3. positive controls: for each group, rank of the other groups by mean distance
    nearest = {}
    for g in G:
        row = sorted(((gd.get(f"{min(g,h)}|{max(g,h)}"), h) for h in G if h != g and gd.get(f"{min(g,h)}|{max(g,h)}") is not None))
        nearest[g] = [h for _, h in row]
    pc = dict(assyria_persepolis=("persepolis" in nearest.get("assyria", [])[:2]) and ("assyria" in nearest.get("persepolis", [])[:2]),
              anatolia_catalhoyuk=("catalhoyuk" in nearest.get("anatolia_ppn", [])[:2]) and ("anatolia_ppn" in nearest.get("catalhoyuk", [])[:2]))
    # 4. Mantel: group composition distance vs geographic distance
    def hav(a, b):
        la1, lo1, la2, lo2 = map(math.radians, (groups[a]["lat"], groups[a]["lon"], groups[b]["lat"], groups[b]["lon"]))
        h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
        return 6371 * 2 * math.asin(math.sqrt(h))
    pairs = [(g1, g2) for g1, g2 in itertools.combinations(G, 2) if gd.get(f"{g1}|{g2}") is not None]
    x = np.array([hav(a, b) for a, b in pairs]); y = np.array([gd[f"{a}|{b}"] for a, b in pairs])
    r_obs = float(np.corrcoef(x, y)[0, 1]) if len(pairs) > 3 else float("nan")
    # permutation over group labels
    perm = []
    for _ in range(5000):
        p = rng.permutation(G); mp = dict(zip(G, p))
        yp = np.array([gd[f"{min(mp[a],mp[b])}|{max(mp[a],mp[b])}"] for a, b in pairs]); perm.append(np.corrcoef(x, yp)[0, 1])
    mantel = dict(r=r_obs, p=float(np.mean(np.array(perm) >= r_obs)))
    res = dict(n_images=len(imgs), n_triaged_usable=len([i for i in imgs if tri.get(i, {}).get("usable")]), n_coded=n,
               per_group={g: int((grp == g).sum()) for g in G}, fetched_per_group={g: sum(1 for i in imgs if imgs[i]["group"] == g) for g in G}, usable_per_group={g: sum(1 for i in imgs if imgs[i]["group"] == g and tri.get(i, {}).get("usable")) for g in G}, alpha=alpha, kept_features=keep,
               nfn_quantiles={q: float(np.quantile(nfn_vals, q)) for q in (0.05, 0.25, 0.5, 0.75, 0.95)} if len(nfn_vals) else {},
               target=target, group_distances=gd, nearest_groups=nearest, positive_controls=pc, mantel=mantel,
               nfn=[dict(id=i, group=imgs[i]["group"], d=v[0], nn=v[1], nn_group=imgs[v[1]]["group"] if v[1] else None) for i, v in nfn.items()])
    res["settings"] = dict(alpha_min=ALPHA_MIN, mode=MODE)
    json.dump(res, open(os.path.join(S3, OUTNAME), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("nfn", "group_distances")}, indent=1, default=str)[:5000])

if __name__ == "__main__":
    main()
