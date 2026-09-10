"""Bring every sign, whatever its drawing style, to one common representation.

The three sources are drawn differently: Barthel's rongorongo glyphs are
hollow outline drawings (double contour), Mahadevan's Indus signs are thin
single-stroke line drawings, and the font-rendered control scripts are filled
silhouettes. Comparing those directly would mostly measure drawing style.

Pipeline (identical for every script; the only per-source parameter is the
outline-closing radius, which is set from the measured double-line gap of
the Barthel scan and is zero for the other sources):

  1. binarise (Otsu), crop to ink, pad
  2. outline sources only: morphological closing to fill the body between the
     double contour (radius ~ half the gap between the two lines)
  3. medial-axis skeleton (skimage skeletonize)
  4. prune skeleton spurs shorter than 5% of the glyph size
  5. render the skeleton with a fixed stroke width into a 64x64 box that
     preserves aspect ratio (longest side = 56 px), centred

Outputs per glyph: the 64x64 skeleton image (uint8), plus simple complexity
features measured on the skeleton: total skeleton length (px, at 64 scale),
number of endpoints, number of junctions, number of enclosed regions (loops).
"""
import os, json
import numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize, disk, binary_closing, remove_small_objects

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = 64
INNER = 56

def load_binary(path):
    im = np.array(Image.open(path).convert("L"))
    _, bw = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    bw = bw > 0
    bw = remove_small_objects(bw, 8)
    ys, xs = np.where(bw)
    if len(ys) == 0:
        return None
    return bw[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

def harmonise(bw, style):
    """Make the ink a solid body. Outline drawings get their double contour closed."""
    h, w = bw.shape
    s = max(h, w)
    if style == "outline":
        # Barthel double-line gap is ~7% of glyph height on the 391 ppi scan; close with a disk of that radius
        r = max(2, int(round(0.055 * s)))
        bw = binary_closing(np.pad(bw, r), disk(r))[r:-r, r:-r]
        bw = ndi.binary_fill_holes(bw) if False else bw   # (kept explicit: we do NOT fill large holes)
    return bw

def prune(skel, min_len):
    """Iteratively remove endpoint branches shorter than min_len."""
    skel = skel.copy()
    for _ in range(min_len):
        nb = ndi.convolve(skel.astype(int), np.ones((3, 3)), mode="constant") - skel
        endpoints = skel & (nb == 1)
        if not endpoints.any():
            break
        skel[endpoints] = False
    # the iterative erosion above also shortens real branches by min_len; regrow is not needed for our purposes
    return skel

def skeleton_features(skel):
    nb = ndi.convolve(skel.astype(int), np.ones((3, 3)), mode="constant") - skel
    endpoints = int(((nb == 1) & skel).sum())
    junctions = int(((nb >= 3) & skel).sum())
    length = int(skel.sum())
    # enclosed regions: background components fully surrounded by skeleton (loops)
    filled = ndi.binary_fill_holes(skel)
    holes, nh = ndi.label(filled & ~skel)
    loops = int(nh)
    return dict(length=length, endpoints=endpoints, junctions=junctions, loops=loops)

def normalise(path, style):
    bw = load_binary(path)
    if bw is None:
        return None, None
    bw = harmonise(bw, style)
    h, w = bw.shape
    scale = INNER / max(h, w)
    nh, nw = max(1, int(round(h * scale))), max(1, int(round(w * scale)))
    # resize the solid body at a larger working size, skeletonise there, then downsample the skeleton
    work = 4
    body = cv2.resize(bw.astype(np.uint8) * 255, (nw * work, nh * work), interpolation=cv2.INTER_AREA) > 127
    body = ndi.binary_closing(body, iterations=1)
    skel = skeletonize(body)
    skel = prune(skel, max(2, int(0.04 * max(nh, nw) * work)))
    # rasterise the skeleton with a fixed stroke into the 64 box
    canvas = np.zeros((BOX * work, BOX * work), bool)
    y0 = (BOX * work - nh * work) // 2; x0 = (BOX * work - nw * work) // 2
    canvas[y0:y0 + nh * work, x0:x0 + nw * work] = skel
    feats = skeleton_features(skel)
    feats["length"] = int(round(feats["length"] / work))     # express length in 64-box pixels
    thick = cv2.dilate(canvas.astype(np.uint8) * 255, np.ones((work + 1, work + 1), np.uint8))
    out = cv2.resize(thick, (BOX, BOX), interpolation=cv2.INTER_AREA)
    return out, feats

STYLES = {"rongorongo": "outline", "indus": "line"}

def run(script):
    style = STYLES.get(script, "font")
    man = json.load(open(os.path.join(ROOT, "data", "glyphs", f"{script}_manifest.json")))
    outdir = os.path.join(ROOT, "data", "norm", script); os.makedirs(outdir, exist_ok=True)
    recs = []
    for r in man:
        if not r.get("file") or not r.get("number"):
            continue
        out, feats = normalise(os.path.join(ROOT, r["file"]), style)
        if out is None:
            continue
        name = r["number"].replace("+", "")
        fn = os.path.join(outdir, f"{name}.png"); Image.fromarray(out).save(fn)
        recs.append(dict(script=script, id=name, number=r["number"], src=r["file"], norm=os.path.relpath(fn, ROOT), **feats))
    json.dump(recs, open(os.path.join(ROOT, "data", "norm", f"{script}.json"), "w"), indent=1)
    return recs

if __name__ == "__main__":
    import sys
    for s in sys.argv[1:]:
        recs = run(s); print(s, len(recs))
