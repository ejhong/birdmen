"""Robustness check for the drawing-style confound.

Indus and rongorongo are both scanned hand drawings; the controls are clean
font renderings. To test whether "looks hand-drawn" is what the metrics are
picking up, every font-rendered control glyph is passed through a random
elastic distortion plus scanner-like blur before normalisation ("wobbled"),
and the target comparisons are repeated against the wobbled controls.
Same seed for everyone; parameters fixed here and not tuned.
"""
import os, json, sys
import numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import normalize as NZ

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rng = np.random.default_rng(7)

def wobble(im):
    """im: uint8 grayscale, black ink on white. Elastic warp + blur + threshold."""
    h, w = im.shape
    s = max(h, w)
    alpha, sigma = 0.045 * s, 0.10 * s        # displacement amplitude and smoothness
    dx = ndi.gaussian_filter(rng.uniform(-1, 1, (h, w)), sigma) ; dy = ndi.gaussian_filter(rng.uniform(-1, 1, (h, w)), sigma)
    dx *= alpha / (np.abs(dx).max() + 1e-9); dy *= alpha / (np.abs(dy).max() + 1e-9)
    yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    warped = ndi.map_coordinates(im.astype(np.float32), [yy + dy, xx + dx], order=1, mode="nearest")
    warped = ndi.gaussian_filter(warped, 0.012 * s + 0.6)
    warped += rng.normal(0, 6, warped.shape)
    return np.clip(warped, 0, 255).astype(np.uint8)

def run(script):
    man = json.load(open(os.path.join(ROOT, "data", "glyphs", f"{script}_manifest.json")))
    gdir = os.path.join(ROOT, "data", "glyphs", f"{script}_w"); os.makedirs(gdir, exist_ok=True)
    out = []
    for r in man:
        im = np.array(Image.open(os.path.join(ROOT, r["file"])).convert("L"))
        pad = int(0.1 * max(im.shape)) + 4
        im = np.pad(im, pad, constant_values=255)
        w = wobble(im)
        fn = os.path.join(gdir, os.path.basename(r["file"])); Image.fromarray(w).save(fn)
        out.append(dict(r, file=os.path.relpath(fn, ROOT)))
    json.dump(out, open(os.path.join(ROOT, "data", "glyphs", f"{script}_w_manifest.json"), "w"), indent=1)
    NZ.STYLES[f"{script}_w"] = "line"
    recs = NZ.run(f"{script}_w")
    return len(recs)

if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(s, run(s), flush=True)
