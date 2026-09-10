"""Pairwise similarity between sign inventories, from the three frozen representations.

All three similarities are in [0, 1] where 1 is identical. They are combined by
a rank-free z-score average whose mean and sd are fixed once, from a large random
sample of cross-script pairs drawn over ALL scripts (so the combination is the
same for every script pair and was not tuned on the Indus-rongorongo pair).

  chamfer(a, b) = exp(-d / TAU), d = symmetric mean skeleton-to-skeleton distance
                   (mean over a's pixels of distance to b, and vice versa), best of
                   {identity, horizontal mirror} - the same allowance for every pair
  hog(a, b)     = cosine similarity of HOG descriptors, rescaled from [-1,1] to [0,1]
  dino(a, b)    = cosine similarity of DINOv2 embeddings, rescaled to [0,1]
"""
import os, json
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEAT = os.path.join(ROOT, "data", "features")
TAU = 4.0

_cache = {}
def load(script):
    if script not in _cache:
        z = np.load(os.path.join(FEAT, f"{script}.npz"))
        _cache[script] = {k: z[k] for k in z.files}
    return _cache[script]

def chamfer_matrix(A, B):
    """A, B: feature dicts. Returns (nA, nB) similarity."""
    skA, dtA = A["skel"][:, 0], A["dt"][:, 0]           # identity orientation for A
    nA = skA.sum(1, keepdims=True) + 1e-6
    best = None
    for o in (0, 1):                                    # B upright or mirrored
        skB, dtB = B["skel"][:, o], B["dt"][:, o]
        nB = skB.sum(1, keepdims=True) + 1e-6
        d_ab = (skA @ dtB.T) / nA                       # mean distance from A's pixels to B
        d_ba = (dtA @ skB.T) / nB.T                     # mean distance from B's pixels to A
        d = 0.5 * (d_ab + d_ba)
        best = d if best is None else np.minimum(best, d)
    return np.exp(-best / TAU)

def hog_matrix(A, B):
    return 0.5 * (1 + A["hog"] @ B["hog"].T)

def dino_matrix(A, B):
    return 0.5 * (1 + A["dino"] @ B["dino"].T)

_norm = None
def calibration(scripts, n_pairs=200000, seed=0):
    """Fixed mean/sd of each metric over random cross-script pairs (cached to disk)."""
    global _norm
    path = os.path.join(FEAT, "calibration.json")
    if _norm is None and os.path.exists(path):
        _norm = json.load(open(path))
    if _norm is not None:
        return _norm
    rng = np.random.default_rng(seed)
    vals = {"chamfer": [], "hog": [], "dino": []}
    pairs = [(a, b) for i, a in enumerate(scripts) for b in scripts[i + 1:]]
    per = max(1, n_pairs // len(pairs))
    for a, b in pairs:
        A, B = load(a), load(b)
        ia = rng.integers(0, len(A["ids"]), per); ib = rng.integers(0, len(B["ids"]), per)
        sa = {k: A[k][ia] for k in ("skel", "dt", "hog", "dino")}; sb = {k: B[k][ib] for k in ("skel", "dt", "hog", "dino")}
        vals["chamfer"].append(np.diag(chamfer_matrix(sa, sb)))
        vals["hog"].append(np.diag(hog_matrix(sa, sb)))
        vals["dino"].append(np.diag(dino_matrix(sa, sb)))
    _norm = {k: dict(mean=float(np.concatenate(v).mean()), sd=float(np.concatenate(v).std())) for k, v in vals.items()}
    json.dump(_norm, open(path, "w"), indent=1)
    return _norm

def combined_matrix(a, b, ia=None, ib=None):
    """Combined z-score similarity plus the three components, for scripts a and b (optionally subsets)."""
    A, B = load(a), load(b)
    if ia is not None: A = {k: v[ia] for k, v in A.items()}
    if ib is not None: B = {k: v[ib] for k, v in B.items()}
    c = calibration(None) if _norm or os.path.exists(os.path.join(FEAT, "calibration.json")) else None
    if c is None:
        raise RuntimeError("run calibration(scripts) first")
    m = {"chamfer": chamfer_matrix(A, B), "hog": hog_matrix(A, B), "dino": dino_matrix(A, B)}
    z = sum((m[k] - c[k]["mean"]) / c[k]["sd"] for k in m) / 3.0
    return z, m
