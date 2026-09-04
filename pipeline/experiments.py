"""The experiments. Every statistic is computed identically for every script pair.

Definitions (fixed before the target pair was examined):

  combined similarity z(a, b): mean of the three per-metric z-scores (see similarity.py)

  MATCH THRESHOLD T: the combined similarity exceeded by 0.1% of random cross-script
     sign pairs (drawn over all scripts). "A match" means z >= T.

  For a script pair (A, B), with both inventories subsampled to N = 200 signs
  (scripts smaller than N use all their signs), repeated R = 20 times:
     best24      mean combined similarity of the 24 best one-to-one matches
                 (greedy: take the best pair, remove both signs, repeat)
     match_rate  matches per 10,000 candidate pairs (size-independent)
     nn_mean     mean over signs of their best match in the other script (both directions averaged)
     best24_cx   best24 restricted to complex signs (skeleton length above the global median)
     rate_cx     match_rate restricted to complex signs

  Lineup: for each rongorongo sign, which script (among the large ones, each
     subsampled to N) holds its single nearest neighbour? Under no special
     affinity every script wins about 1/k of the time. Same with Indus as the probe.

  Small-inventory panel: every pair of all 24 scripts, both subsampled to n = 22
     (the smallest inventory), R = 40 repeats, best-8 mean similarity. This lets
     the small known-related alphabets act as positive controls.
"""
import os, json, itertools
import numpy as np
import similarity as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "results"); os.makedirs(OUT, exist_ok=True)
ALL = ["indus", "rongorongo", "egyptian", "anatolian", "linear_a", "linear_b", "cypro_minoan", "cuneiform", "ugaritic",
       "old_persian", "phoenician", "old_italic", "carian", "lycian", "old_south_arabian", "meroitic", "runic", "old_turkic",
       "tifinagh", "vai", "mende_kikakui", "pahawh_hmong", "nushu", "yi"]
BIG = ["indus", "rongorongo", "egyptian", "anatolian", "linear_a", "linear_b", "cuneiform", "vai", "mende_kikakui", "nushu", "yi"]
RELATED = {frozenset(p) for p in [("linear_a", "linear_b"), ("linear_a", "cypro_minoan"), ("linear_b", "cypro_minoan"),
                                    ("phoenician", "old_italic"), ("phoenician", "carian"), ("phoenician", "lycian"),
                                    ("old_italic", "carian"), ("old_italic", "lycian"), ("carian", "lycian"),
                                    ("old_italic", "runic"), ("phoenician", "old_south_arabian"), ("egyptian", "meroitic")]}
N, R, K = 200, 20, 24
rng = np.random.default_rng(2026)

def greedy(z, k):
    z = z.copy(); out = []
    for _ in range(min(k, min(z.shape))):
        i, j = np.unravel_index(np.argmax(z), z.shape); out.append((int(i), int(j), float(z[i, j])))
        z[i, :] = -99; z[:, j] = -99
    return out

def threshold():
    path = os.path.join(OUT, "threshold.json")
    if os.path.exists(path):
        return json.load(open(path))["T"]
    vals = []
    pairs = [(a, b) for i, a in enumerate(ALL) for b in ALL[i + 1:]]
    for a, b in pairs:
        A, B = S.load(a), S.load(b)
        ia = rng.integers(0, len(A["ids"]), 800); ib = rng.integers(0, len(B["ids"]), 800)
        z, _ = S.combined_matrix(a, b, ia, ib)
        vals.append(np.diag(z))
    vals = np.concatenate(vals)
    T = float(np.quantile(vals, 0.999))
    json.dump(dict(T=T, n=int(len(vals)), q=0.999, mean=float(vals.mean()), sd=float(vals.std())), open(path, "w"), indent=1)
    return T

def complexity_median():
    L = np.concatenate([S.load(s)["length"] for s in BIG])
    return float(np.median(L))

def pair_stats(a, b, T, Lmed, n=N, k=K, reps=R):
    A, B = S.load(a), S.load(b)
    na, nb = len(A["ids"]), len(B["ids"])
    recs = []
    for r in range(reps):
        ia = np.sort(rng.choice(na, min(n, na), replace=False)); ib = np.sort(rng.choice(nb, min(n, nb), replace=False))
        z, m = S.combined_matrix(a, b, ia, ib)
        top = greedy(z, k)
        cxa = A["length"][ia] > Lmed; cxb = B["length"][ib] > Lmed
        zc = z[np.ix_(cxa, cxb)]
        c = S.calibration(None)
        rec = dict(best24=np.mean([t[2] for t in top]), match_rate=1e4 * float((z >= T).mean()),
                   nn_mean=0.5 * (z.max(1).mean() + z.max(0).mean()),
                   best24_cx=np.mean([t[2] for t in greedy(zc, k)]) if zc.size else np.nan,
                   rate_cx=1e4 * float((zc >= T).mean()) if zc.size else np.nan)
        for kk in ("chamfer", "hog", "dino"):            # the same statistic under each metric alone
            zk = (m[kk] - c[kk]["mean"]) / c[kk]["sd"]
            rec[f"best24_{kk}"] = np.mean([t[2] for t in greedy(zk, k)])
        recs.append(rec)
    keys = recs[0].keys()
    return {kk: dict(mean=float(np.nanmean([r[kk] for r in recs])), sd=float(np.nanstd([r[kk] for r in recs]))) for kk in keys}

def full_gallery(a, b, k=K):
    z, m = S.combined_matrix(a, b)
    A, B = S.load(a), S.load(b)
    top = greedy(z, k)
    return [dict(a=str(A["ids"][i]), b=str(B["ids"][j]), z=round(v, 3), chamfer=round(float(m["chamfer"][i, j]), 3),
                 hog=round(float(m["hog"][i, j]), 3), dino=round(float(m["dino"][i, j]), 3),
                 len_a=int(A["length"][i]), len_b=int(B["length"][j])) for i, j, v in top]

def lineup(probe, others, n=N, reps=R):
    P = S.load(probe); nP = len(P["ids"])
    wins = {o: 0 for o in others}; total = 0
    for r in range(reps):
        best = np.full(nP, -99.0); who = np.array([""] * nP, dtype=object)
        for o in others:
            O = S.load(o); io = np.sort(rng.choice(len(O["ids"]), min(n, len(O["ids"])), replace=False))
            z, _ = S.combined_matrix(probe, o, None, io)
            m = z.max(1); better = m > best; best[better] = m[better]; who[better] = o
        for o in others: wins[o] += int((who == o).sum())
        total += nP
    return {o: wins[o] / total for o in others}

def main():
    T = threshold(); Lmed = complexity_median()
    print("threshold T =", round(T, 3), " complexity median =", Lmed, flush=True)
    results = dict(T=T, complexity_median=Lmed, N=N, R=R, K=K, big=BIG, all=ALL,
                   related=[sorted(p) for p in RELATED], sizes={s: int(len(S.load(s)["ids"])) for s in ALL})
    # 1. all pairs of large scripts
    pairs = {}
    for a, b in itertools.combinations(BIG, 2):
        pairs[f"{a}|{b}"] = pair_stats(a, b, T, Lmed); print("pair", a, b, round(pairs[f"{a}|{b}"]["best24"]["mean"], 3), flush=True)
    results["pairs"] = pairs
    # 2. galleries (full inventories) for every large pair, plus the target pair's full-inventory stats
    results["galleries"] = {f"{a}|{b}": full_gallery(a, b) for a, b in itertools.combinations(BIG, 2)}
    # 3. lineups
    results["lineup_rongorongo"] = lineup("rongorongo", [s for s in BIG if s != "rongorongo"])
    results["lineup_indus"] = lineup("indus", [s for s in BIG if s != "indus"])
    # 4. small-inventory panel over all scripts
    small = {}
    for a, b in itertools.combinations(ALL, 2):
        small[f"{a}|{b}"] = pair_stats(a, b, T, Lmed, n=22, k=8, reps=40)["best24"]
    results["small_panel"] = small
    # 5. full-matrix distribution for the target pair: all 417 x 604 combined similarities (histogram) and per-metric
    z, m = S.combined_matrix("indus", "rongorongo")
    results["target_full"] = dict(n_pairs=int(z.size), matches=int((z >= T).sum()), match_rate=1e4 * float((z >= T).mean()),
                                  hist=np.histogram(z, bins=np.linspace(-4, 6, 101))[0].tolist(), bins=np.linspace(-4, 6, 101).tolist())
    json.dump(results, open(os.path.join(OUT, "results.json"), "w"), indent=1)
    print("done")

if __name__ == "__main__":
    main()

def wobble_block():
    """Repeat the target-vs-control comparisons with scan-like (wobbled) control renderings."""
    T = threshold(); Lmed = complexity_median()
    ctrl = [s for s in BIG if s not in ("indus", "rongorongo")]
    out = dict(vs_rongorongo={}, vs_indus={})
    for s in ctrl:
        out["vs_rongorongo"][s + "_w"] = pair_stats("rongorongo", s + "_w", T, Lmed)
        out["vs_indus"][s + "_w"] = pair_stats("indus", s + "_w", T, Lmed)
        print("wobble", s, round(out["vs_rongorongo"][s + "_w"]["best24"]["mean"], 3), round(out["vs_indus"][s + "_w"]["best24"]["mean"], 3), flush=True)
    out["vs_rongorongo"]["indus"] = pair_stats("indus", "rongorongo", T, Lmed)
    out["vs_indus"]["rongorongo"] = out["vs_rongorongo"]["indus"]
    out["lineup_rongorongo"] = lineup("rongorongo", ["indus"] + [s + "_w" for s in ctrl])
    out["lineup_indus"] = lineup("indus", ["rongorongo"] + [s + "_w" for s in ctrl])
    out["galleries"] = {f"rongorongo|{s}_w": full_gallery("rongorongo", s + "_w") for s in ctrl}
    json.dump(out, open(os.path.join(OUT, "wobble.json"), "w"), indent=1)
    return out
