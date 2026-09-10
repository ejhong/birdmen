"""Does the similarity metric recognise a glyph when it sees it drawn again?

The kohaumotu glyph library holds an independent, very low-resolution
rendition (24 x 40 px GIFs) of the same Barthel glyphs that were extracted
from the 391 ppi plates. Each thumbnail is upscaled, pushed through the
identical pipeline, and used as a query against the 604-glyph inventory.
If the metric is any good, the true glyph should come back first.

Output: data/results/validation.json
"""
import os, sys, json
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import normalize as NZ, similarity as S, features as F
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
from skimage.feature import hog

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the Deep Memory repository; this study lives in pipeline/rongo, data/rongo, docs/rongo, inputs/rongo
QDIR = os.path.join(ROOT, "data", "rongo", "raw", "barthel", "kohaumotu_thumbs")

def main():
    B = S.load("rongorongo"); ids = [str(x) for x in B["ids"]]; idx = {g: i for i, g in enumerate(ids)}
    c = S.calibration(None)
    feats, truth = [], []
    for fn in sorted(os.listdir(QDIR)):
        g = fn[:-4]
        if g not in idx: continue
        im = Image.open(os.path.join(QDIR, fn)).convert("L"); im = im.resize((im.width * 6, im.height * 6), Image.LANCZOS)
        tmp = os.path.join(ROOT, "data", "rongo", "qa", "_q.png"); im.save(tmp)
        out, _ = NZ.normalise(tmp, "line")
        if out is None: continue
        sk1 = skeletonize(out > 127); skel, dt = [], []
        for flip in (False, True):
            s = sk1[:, ::-1] if flip else sk1
            skel.append(s.astype(np.float32).ravel()); dt.append(np.minimum(ndi.distance_transform_edt(~s), 12).astype(np.float32).ravel())
        h = hog(out.astype(np.float32) / 255, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), feature_vector=True).astype(np.float32)
        h /= np.linalg.norm(h) + 1e-9
        feats.append((np.stack(skel), np.stack(dt), h, out)); truth.append(idx[g])
    os.remove(tmp)
    Q = dict(skel=np.stack([f[0] for f in feats]), dt=np.stack([f[1] for f in feats]), hog=np.stack([f[2] for f in feats]),
             dino=F.embed_dino([f[3] for f in feats]))
    m = {"chamfer": S.chamfer_matrix(Q, B), "hog": S.hog_matrix(Q, B), "dino": S.dino_matrix(Q, B)}
    zs = {k: (m[k] - c[k]["mean"]) / c[k]["sd"] for k in m}
    zs["combined"] = sum(zs[k] for k in m) / 3
    truth = np.array(truth)
    def acc(mat, k):
        order = np.argsort(-mat, axis=1)[:, :k]; return float(np.mean([truth[i] in order[i] for i in range(len(truth))]))
    res = {k: dict(top1=acc(v, 1), top5=acc(v, 5), top10=acc(v, 10)) for k, v in zs.items()}
    ranks = [int((zs["combined"][i] > zs["combined"][i, truth[i]]).sum()) + 1 for i in range(len(truth))]
    res["combined"]["median_rank"] = int(np.median(ranks))
    res["n_queries"] = int(len(truth)); res["n_inventory"] = int(len(ids)); res["chance_top1"] = 1 / len(ids)
    json.dump(res, open(os.path.join(ROOT, "data", "rongo", "results", "validation.json"), "w"), indent=1)
    for k, v in res.items():
        if isinstance(v, dict): print(f"{k:9s} top1 {v['top1']:.2f}  top5 {v['top5']:.2f}  top10 {v['top10']:.2f}")

if __name__ == "__main__":
    main()
