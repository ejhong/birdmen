"""Step 3 of the fidelity audit: score the 24 chart pairs against the catalogues.

Reads data/fidelity/mapping.json ({"P01": {"indus": "030", "rongorongo": "059", "note": "...", "how": "auto|reviewed"}, ...})
and data/fidelity/candidates.json, and writes data/fidelity/pairs.json with, per pair:
  - the two chart drawings, their catalogue identifications, and how the identification was made
  - z_chart:   similarity of the two chart drawings to each other
  - z_catalog: similarity of the two identified catalogue signs to each other
  - pct_catalog: percentile of z_catalog among ALL 417 x 604 Indus-rongorongo catalogue pairs
  - rank_catalog: its rank among those 251,868 pairs (1 = most similar pair of the whole cross-product)
  - reciprocal: whether each catalogue sign is the other's nearest neighbour in the other script
  - complexity of both catalogue signs (skeleton length)
"""
import os, json, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import similarity as S, fidelity as FD

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FID = os.path.join(ROOT, "data", "fidelity")

def main():
    mapping = json.load(open(os.path.join(FID, "mapping.json")))
    cells = {(c["pair"], c["script"]): c for c in json.load(open(os.path.join(FID, "candidates.json")))}
    A, B = S.load("indus"), S.load("rongorongo")
    z, m = S.combined_matrix("indus", "rongorongo")
    T = json.load(open(os.path.join(ROOT, "data", "results", "threshold.json")))["T"]
    ida = {str(x): i for i, x in enumerate(A["ids"])}; idb = {str(x): i for i, x in enumerate(B["ids"])}
    flat = np.sort(z.ravel())[::-1]
    nnA = z.argmax(1); nnB = z.argmax(0)
    c = S.calibration(None)
    out = []
    for p in range(1, 25):
        key = f"P{p:02d}"; mp = mapping.get(key, {})
        ci, cr = cells.get((p, "indus")), cells.get((p, "rongorongo"))
        rec = dict(pair=key, chart_indus=ci["file"] if ci else None, chart_rongorongo=cr["file"] if cr else None,
                   indus=mp.get("indus"), rongorongo=mp.get("rongorongo"), how=mp.get("how", "auto"), note=mp.get("note", ""),
                   cand_indus=ci["candidates"][:5] if ci else [], cand_rongorongo=cr["candidates"][:5] if cr else [])
        # chart drawing vs chart drawing
        if ci and cr:
            fa, _ = FD.featurize(os.path.join(ROOT, ci["file"])); fb, _ = FD.featurize(os.path.join(ROOT, cr["file"]))
            mm = {"chamfer": S.chamfer_matrix(fa, fb), "hog": S.hog_matrix(fa, fb), "dino": S.dino_matrix(fa, fb)}
            rec["z_chart"] = round(float(sum((mm[k] - c[k]["mean"]) / c[k]["sd"] for k in mm)[0, 0] / 3.0), 3)
            rec["pct_chart"] = round(100.0 * float((flat < rec["z_chart"]).mean()), 2)
        if rec["indus"] in ida and rec["rongorongo"] in idb:
            i, j = ida[rec["indus"]], idb[rec["rongorongo"]]
            v = float(z[i, j])
            rec.update(z_catalog=round(v, 3), rank_catalog=int((flat > v).sum()) + 1, pct_catalog=round(100.0 * float((flat < v).mean()), 2),
                       match=bool(v >= T), reciprocal=bool(nnA[i] == j and nnB[j] == i),
                       nn_of_indus_sign=str(B["ids"][nnA[i]]), nn_of_rongorongo_sign=str(A["ids"][nnB[j]]),
                       len_indus=int(A["length"][i]), len_rongorongo=int(B["length"][j]),
                       chamfer=round(float(m["chamfer"][i, j]), 3), hog=round(float(m["hog"][i, j]), 3), dino=round(float(m["dino"][i, j]), 3))
        out.append(rec)
    summary = dict(T=T, n_pairs=int(z.size), n_identified=sum(1 for r in out if "z_catalog" in r),
                   n_match=sum(1 for r in out if r.get("match")), n_reciprocal=sum(1 for r in out if r.get("reciprocal")),
                   median_pct=float(np.median([r["pct_catalog"] for r in out if "pct_catalog" in r])),
                   top_ranks=sorted(r["rank_catalog"] for r in out if "rank_catalog" in r))
    json.dump(dict(summary=summary, pairs=out), open(os.path.join(FID, "pairs.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1))
    for r in out:
        print(r["pair"], r["indus"], r["rongorongo"], r["how"], "z_cat", r.get("z_catalog"), "rank", r.get("rank_catalog"), "pct", r.get("pct_catalog"), "recip", r.get("reciprocal"), "z_chart", r.get("z_chart"))

if __name__ == "__main__":
    main()
