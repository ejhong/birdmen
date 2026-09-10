"""Fidelity audit of the circulating 24-pair chart.

Step 1 (this script): cut the chart in the tweet screenshot into its 48 cells
(3 Indus rows + 3 Easter Island rows, 8 columns), normalise each drawing with
the same pipeline as everything else, and list the nearest catalogue signs in
Mahadevan (Indus) and Barthel (rongorongo) by the combined similarity.

Step 2 (manual, recorded in data/fidelity/mapping.json): a human picks the
catalogue sign each chart drawing was meant to depict, from the candidates,
or records that no catalogue sign matches.

Step 3: for each pair, report the similarity of the chart drawings to each
other, the similarity of the two catalogue signs to each other, and where
that catalogue-to-catalogue similarity ranks among all 417 x 604 Indus-
rongorongo pairs and among random cross-script pairs.
"""
import os, json, sys
import numpy as np, cv2
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import normalize as NZ, similarity as S, features as F
from scipy import ndimage as ndi
from skimage.morphology import skeletonize
from skimage.feature import hog

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the Deep Memory repository; this study lives in pipeline/rongo, data/rongo, docs/rongo, inputs/rongo
FID = os.path.join(ROOT, "data", "rongo", "fidelity"); os.makedirs(FID, exist_ok=True)
CELLS = os.path.join(FID, "cells"); os.makedirs(CELLS, exist_ok=True)

def cut_chart():
    """Locate the chart in inputs/claim_1.png and split into 6 rows x 8 columns of drawings."""
    im = np.array(Image.open(os.path.join(ROOT, "inputs", "rongo", "claim_1.png")).convert("L"))
    # the chart is the large light rectangle on the dark tweet background
    light = im > 150
    rows = np.where(light.mean(1) > 0.6)[0]; cols = np.where(light[rows.min():rows.max()].mean(0) > 0.6)[0]
    chart = im[rows.min():rows.max(), cols.min():cols.max()]
    Image.fromarray(chart).save(os.path.join(FID, "chart.png"))
    ink = chart < 110
    # drop the row labels ("Indus Valley" / "Easter Island") on the left: they occupy the first ~15% of width
    W = chart.shape[1]; ink[:, :int(0.15 * W)] = False
    # rows of glyphs from the horizontal projection
    prof = ndi.uniform_filter1d(ink.mean(1), 9) > 0.003
    bands = []
    y = 0
    while y < len(prof):
        if prof[y]:
            y0 = y
            while y < len(prof) and prof[y]: y += 1
            if y - y0 >= 30: bands.append((y0, y))
        y += 1
    merged = bands
    assert len(merged) == 6, merged
    # columns align across the six rows: take the vertical projection over all glyph rows and find 8 bands
    allrows = np.zeros_like(ink)
    for y0, y1 in merged: allrows[y0:y1] = ink[y0:y1]
    cprof = ndi.uniform_filter1d(allrows.mean(0), 5) > 0.002
    cbands = []; x = 0
    while x < len(cprof):
        if cprof[x]:
            x0 = x
            while x < len(cprof) and cprof[x]: x += 1
            if x - x0 >= 12: cbands.append([x0, x])
        x += 1
    # merge column fragments closer than a quarter of the typical column pitch
    mergedc = []
    for b in cbands:
        if mergedc and b[0] - mergedc[-1][1] < 22: mergedc[-1][1] = b[1]
        else: mergedc.append(b)
    # a band much wider than the others holds two columns: split it at the projection valley in its middle half
    widths = [b[1] - b[0] for b in mergedc]
    while len(mergedc) < 8:
        k = int(np.argmax([b[1] - b[0] for b in mergedc])); x0, x1 = mergedc[k]
        prof = ndi.uniform_filter1d(allrows.mean(0), 5)
        lo, hi = x0 + (x1 - x0) // 4, x1 - (x1 - x0) // 4
        cut = lo + int(np.argmin(prof[lo:hi]))
        mergedc[k:k + 1] = [[x0, cut], [cut, x1]]
    assert len(mergedc) == 8, mergedc
    cells = []
    for ri, (y0, y1) in enumerate(merged):
        for ci, (x0, x1) in enumerate(mergedc):
            sub = ink[y0:y1, x0:x1]
            ys, xs = np.where(sub)
            if len(ys) == 0: continue
            pad = 3
            crop = chart[y0 + ys.min() - pad:y0 + ys.max() + pad, x0 + xs.min() - pad:x0 + xs.max() + pad]
            script = "indus" if ri % 2 == 0 else "rongorongo"
            pair = (ri // 2) * 8 + ci + 1
            fn = os.path.join(CELLS, f"P{pair:02d}_{script}.png"); Image.fromarray(crop).save(fn)
            cells.append(dict(pair=pair, script=script, file=os.path.relpath(fn, ROOT),
                              box=[int(x0 + xs.min()), int(y0 + ys.min()), int(x0 + xs.max()), int(y0 + ys.max())]))
    json.dump(cells, open(os.path.join(FID, "cells.json"), "w"), indent=1)
    return cells

def featurize(path, style="line"):
    out, feats = NZ.normalise(path, style)
    sk1 = skeletonize(out > 127)
    skel, dt = [], []
    for flip in (False, True):
        s = sk1[:, ::-1] if flip else sk1
        skel.append(s.astype(np.float32).ravel()); dt.append(np.minimum(ndi.distance_transform_edt(~s), 12).astype(np.float32).ravel())
    h = hog(out.astype(np.float32) / 255, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), feature_vector=True).astype(np.float32)
    h /= np.linalg.norm(h) + 1e-9
    d = F.embed_dino([out])[0]
    return dict(skel=np.stack(skel)[None], dt=np.stack(dt)[None], hog=h[None], dino=d[None], length=np.array([feats["length"]])), out

def candidates(cells, k=8):
    """Nearest catalogue signs for every chart drawing."""
    c = S.calibration(None)
    res = []
    for cell in cells:
        feat, out = featurize(os.path.join(ROOT, cell["file"]))
        Image.fromarray(out).save(os.path.join(CELLS, os.path.basename(cell["file"]).replace(".png", "_norm.png")))
        B = S.load(cell["script"])
        m = {"chamfer": S.chamfer_matrix(feat, B), "hog": S.hog_matrix(feat, B), "dino": S.dino_matrix(feat, B)}
        z = sum((m[kk] - c[kk]["mean"]) / c[kk]["sd"] for kk in m)[0] / 3.0
        top = np.argsort(-z)[:k]
        cell["candidates"] = [dict(id=str(B["ids"][i]), z=round(float(z[i]), 2)) for i in top]
        res.append(cell)
    json.dump(res, open(os.path.join(FID, "candidates.json"), "w"), indent=1)
    return res

if __name__ == "__main__":
    cells = cut_chart()
    print("cells:", len(cells))
    cands = candidates(cells)
    for c in cands:
        print(f"P{c['pair']:02d} {c['script']:10s}", " ".join(f"{x['id']}({x['z']})" for x in c["candidates"]))
