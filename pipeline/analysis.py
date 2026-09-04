"""The experiments, all run on the 926-tradition x 2,138-motif presence matrix.

Definitions fixed before any result was looked at:

  A tradition HAS a class if it has at least one motif of that class.
  BUNDLE = the three classes together (bird-people, cosmic serpent, world centre).

  1. Base rates. Fraction of traditions with each class, and with the bundle.
  2. Co-occurrence vs. two nulls.
     (a) independence: product of class rates x number of traditions.
     (b) curveball: 2,000 randomised matrices that keep every tradition's motif
         count and every motif's tradition count (Strona et al. 2014). This
         controls for the fact that well-documented traditions have everything.
     Report observed bundle count, null mean, and the fraction of null matrices
     with as many or more.
  3. Surprise rank. Draw 5,000 random three-class bundles, each class being a
     random set of motifs with the same size as the real class, and compute the
     same co-occurrence excess. Where does the real bundle rank?
  4. The named cultures. The traditions that stand for the cultures in the
     posts: Sumer; Akkad/Assyria/Babylon; Ancient Egypt; Hittite; Aztec; Yucatec
     Maya; Kechua (Cuzco); Easter Island. How many hold each class, and the
     bundle? Against random sets of the same size, and random sets matched on
     documentation (motif count), how unusual is that?
  5. Geography. For each class, Moran's I of presence over inverse great-circle
     distance (nearest 10 neighbours). Compare with random motif sets of the
     same prevalence. A transmitted trait clusters in space; a convergent one
     need not. Also the mean distance to the nearest other tradition with the
     class, versus random.
  6. Bundle map. The traditions holding all three classes, for the map.
"""
import os, json
import numpy as np
from load import load

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "results"); os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(2026)

NAMED = {
    "Sumer": "Sumer", "Akkad / Assyria / Babylon": "Akkad,Assiria,Babylon", "Ancient Egypt": "Ancient Egypt",
    "Hittite / Hurrian": "Hittite, Hurrit", "Aztec": "Aztec", "Yucatec Maya": "Yucatec, Itza",
    "Kechua (Cuzco region)": "Kechua: South Peru, Bolivia", "Easter Island": "Easter Island",
}

def curveball(M, n_iter=None):
    """One randomisation preserving row and column sums (Strona et al. 2014)."""
    M = M.copy(); R, C = M.shape
    rows = [set(np.flatnonzero(M[i])) for i in range(R)]
    n_iter = n_iter or 5 * R
    for _ in range(n_iter):
        a, b = rng.choice(R, 2, replace=False)
        A, B = rows[a], rows[b]
        onlyA = list(A - B); onlyB = list(B - A)
        if not onlyA or not onlyB: continue
        pool = onlyA + onlyB; rng.shuffle(pool)
        newA = set(pool[:len(onlyA)]); newB = set(pool[len(onlyA):])
        rows[a] = (A & B) | newA; rows[b] = (A & B) | newB
    out = np.zeros_like(M)
    for i in range(R): out[i, list(rows[i])] = 1
    return out

def haversine(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    dlat = la[:, None] - la[None, :]; dlon = lo[:, None] - lo[None, :]
    a = np.sin(dlat / 2) ** 2 + np.cos(la[:, None]) * np.cos(la[None, :]) * np.sin(dlon / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))

def morans_I(x, W):
    x = x.astype(float); z = x - x.mean()
    if z.std() == 0: return 0.0
    n = len(x); S0 = W.sum()
    return (n / S0) * (z @ W @ z) / (z @ z)

def main():
    d = load(); M = d["M"]; names = d["names"]; codes = d["codes"]; idx = {c: i for i, c in enumerate(codes)}
    cl = json.load(open(os.path.join(ROOT, "data", "classes.json")))
    classes = {k: [x["code"] for x in v if "excluded" not in x] for k, v in cl.items()}
    cols = {k: np.array([idx[c] for c in v]) for k, v in classes.items()}
    has = {k: (M[:, cols[k]].sum(1) > 0).astype(int) for k in classes}
    bundle = has["bird_people"] & has["cosmic_serpent"] & has["world_centre"]
    n = len(names); rates = {k: float(has[k].mean()) for k in classes}
    res = dict(n_traditions=n, n_motifs=M.shape[1], classes={k: len(v) for k, v in classes.items()}, rates=rates,
               bundle_count=int(bundle.sum()), bundle_rate=float(bundle.mean()),
               independence_expected=float(n * np.prod(list(rates.values()))))
    # documented-ness: how many motifs each tradition has
    doc = M.sum(1); res["doc_median_all"] = float(np.median(doc)); res["doc_median_bundle"] = float(np.median(doc[bundle == 1]))
    # 2b curveball null
    print("curveball...", flush=True)
    null_counts = []; null_rates = {k: [] for k in classes}
    for r in range(300):
        Mr = curveball(M)
        hr = {k: (Mr[:, cols[k]].sum(1) > 0) for k in classes}
        null_counts.append(int((hr["bird_people"] & hr["cosmic_serpent"] & hr["world_centre"]).sum()))
        for k in classes: null_rates[k].append(float(hr[k].mean()))
    res["curveball"] = dict(n=len(null_counts), mean=float(np.mean(null_counts)), sd=float(np.std(null_counts)),
                            p_ge=float(np.mean(np.array(null_counts) >= bundle.sum())), rates={k: float(np.mean(v)) for k, v in null_rates.items()},
                            hist=np.bincount(null_counts).tolist())
    # 3 surprise rank: random bundles of same class sizes; excess = observed / independence-expected
    print("random bundles...", flush=True)
    def excess(h):
        b = h[0] & h[1] & h[2]; exp = n * np.prod([x.mean() for x in h]); return (b.sum() - exp) / max(1.0, np.sqrt(exp)), int(b.sum()), float(exp)
    real_excess = excess([has[k] for k in ("bird_people", "cosmic_serpent", "world_centre")])
    rand = []
    sizes = [len(classes[k]) for k in ("bird_people", "cosmic_serpent", "world_centre")]
    for r in range(5000):
        hs = []
        for s in sizes:
            c = rng.choice(M.shape[1], s, replace=False); hs.append((M[:, c].sum(1) > 0).astype(int))
        rand.append(excess(hs))
    rand_ex = np.array([x[0] for x in rand])
    res["surprise"] = dict(real_excess=float(real_excess[0]), real_count=real_excess[1], real_expected=real_excess[2],
                           rank=int((rand_ex > real_excess[0]).sum()) + 1, n_random=len(rand),
                           random_excess_quantiles=[float(np.quantile(rand_ex, q)) for q in (0.05, 0.25, 0.5, 0.75, 0.95)],
                           random_count_median=float(np.median([x[1] for x in rand])))
    # 4 named cultures
    nidx = {lab: names.index(nm) for lab, nm in NAMED.items()}
    named = {lab: {k: int(has[k][i]) for k in classes} | {"bundle": int(bundle[i]), "n_motifs": int(doc[i])} for lab, i in nidx.items()}
    res["named"] = named
    k_named = len(nidx); ids = np.array(list(nidx.values()))
    obs_bundle = int(bundle[ids].sum()); obs_any = {k: int(has[k][ids].sum()) for k in classes}
    rand_b = [int(bundle[rng.choice(n, k_named, replace=False)].sum()) for _ in range(20000)]
    # documentation-matched: for each named tradition pick a random one with motif count within +-25%
    matched = []
    for _ in range(20000):
        pick = []
        for i in ids:
            lo, hi = 0.75 * doc[i], 1.25 * doc[i]
            cand = np.flatnonzero((doc >= lo) & (doc <= hi)); cand = cand[cand != i]
            pick.append(rng.choice(cand))
        matched.append(int(bundle[np.array(pick)].sum()))
    res["named_test"] = dict(k=k_named, observed_bundle=obs_bundle, observed_any=obs_any,
                             random_mean=float(np.mean(rand_b)), random_p_ge=float(np.mean(np.array(rand_b) >= obs_bundle)),
                             matched_mean=float(np.mean(matched)), matched_p_ge=float(np.mean(np.array(matched) >= obs_bundle)))
    # 5 geography
    print("geography...", flush=True)
    D = haversine(d["lat"], d["lon"]); np.fill_diagonal(D, np.inf)
    knn = np.argsort(D, axis=1)[:, :10]
    W = np.zeros((n, n))
    for i in range(n): W[i, knn[i]] = 1.0 / np.maximum(D[i, knn[i]], 1.0)
    geo = {}
    for k in list(classes) + ["bundle"]:
        x = bundle if k == "bundle" else has[k]
        I = morans_I(x, W)
        nn = np.array([D[i, x == 1].min() if (x == 1).sum() > 1 else np.nan for i in np.flatnonzero(x)])
        # null: random motif sets with the same prevalence (same number of motifs, resampled), 300 draws
        Is, nns = [], []
        for _ in range(300):
            if k == "bundle":
                hs = []
                for s in sizes:
                    c = rng.choice(M.shape[1], s, replace=False); hs.append((M[:, c].sum(1) > 0))
                xr = (hs[0] & hs[1] & hs[2]).astype(int)
            else:
                c = rng.choice(M.shape[1], len(classes[k]), replace=False); xr = (M[:, c].sum(1) > 0).astype(int)
            if xr.sum() < 3: continue
            Is.append(morans_I(xr, W))
            nns.append(float(np.nanmedian([D[i, xr == 1].min() for i in np.flatnonzero(xr)])))
        geo[k] = dict(moran=float(I), moran_null_mean=float(np.mean(Is)), moran_null_sd=float(np.std(Is)),
                      moran_pct=float(np.mean(np.array(Is) < I)), nn_median_km=float(np.nanmedian(nn)),
                      nn_null_median_km=float(np.median(nns)), prevalence=float(x.mean()))
    res["geography"] = geo
    # 6 per-tradition table for maps
    res["traditions"] = [dict(name=names[i], lat=float(d["lat"][i]), lon=float(d["lon"][i]), n=int(doc[i]),
                              b=int(has["bird_people"][i]), s=int(has["cosmic_serpent"][i]), c=int(has["world_centre"][i]),
                              area=d["areas"]["area1"][i]) for i in range(n)]
    # per-motif prevalence within classes
    res["motif_prevalence"] = {k: [dict(code=c, name=cl[k][[x["code"] for x in cl[k]].index(c)]["name"], n=int(M[:, idx[c]].sum())) for c in v] for k, v in classes.items()}
    json.dump(res, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("traditions", "motif_prevalence")}, indent=1)[:6000])

if __name__ == "__main__":
    main()
