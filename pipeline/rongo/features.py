"""Compute three independent shape representations for every normalised sign.

  1. chamfer  - the 64x64 skeleton and its distance transform (for symmetric
                chamfer matching; a horizontal mirror is also stored so the
                same reflection allowance applies to every script)
  2. hog      - histogram of oriented gradients of the thickened skeleton
  3. dino     - frozen DINOv2 ViT-S/14 image embedding of the thickened
                skeleton (a generic pretrained vision model; it has never
                seen these labels and is not fine-tuned on anything here)

Output: data/features/<script>.npz
"""
import os, json, sys
import numpy as np, cv2, torch
from PIL import Image
from scipy import ndimage as ndi
from skimage.feature import hog

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the Deep Memory repository; this study lives in pipeline/rongo, data/rongo, docs/rongo, inputs/rongo
OUT = os.path.join(ROOT, "data", "rongo", "features"); os.makedirs(OUT, exist_ok=True)

_dino = None
def dino():
    global _dino
    if _dino is None:
        _dino = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14", trust_repo=True, verbose=False).eval()
        _dino = _dino.to("mps" if torch.backends.mps.is_available() else "cpu")
    return _dino

def embed_dino(imgs):
    """imgs: list of 64x64 uint8 (white ink on black). Returns L2-normalised (n, 384)."""
    m = dino(); dev = next(m.parameters()).device
    mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1); std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
    out = []
    with torch.no_grad():
        for i in range(0, len(imgs), 64):
            batch = []
            for im in imgs[i:i + 64]:
                x = cv2.resize(255 - im, (224, 224), interpolation=cv2.INTER_CUBIC)   # black ink on white, like natural line art
                batch.append(np.repeat(x[None], 3, 0))
            x = torch.tensor(np.stack(batch), dtype=torch.float32) / 255.0
            x = ((x - mean) / std).to(dev)
            out.append(m(x).cpu().numpy())
    e = np.concatenate(out); e /= np.linalg.norm(e, axis=1, keepdims=True) + 1e-9
    return e.astype(np.float32)

def run(script):
    recs = json.load(open(os.path.join(ROOT, "data", "rongo", "norm", f"{script}.json")))
    skels, dts, hogs, ids = [], [], [], []
    for r in recs:
        im = np.array(Image.open(os.path.join(ROOT, r["norm"])).convert("L"))
        sk = im > 127
        # thin the rendered stroke back to a 1-px skeleton for chamfer matching
        from skimage.morphology import skeletonize
        sk1 = skeletonize(sk)
        for flip in (False, True):
            s = sk1[:, ::-1] if flip else sk1
            dt = ndi.distance_transform_edt(~s)
            skels.append(s.astype(np.float32).ravel()); dts.append(np.minimum(dt, 12).astype(np.float32).ravel())
        hogs.append(hog(im.astype(np.float32) / 255, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(2, 2), feature_vector=True).astype(np.float32))
        ids.append(r["id"])
    imgs = [np.array(Image.open(os.path.join(ROOT, r["norm"])).convert("L")) for r in recs]
    d = embed_dino(imgs)
    h = np.stack(hogs); h /= np.linalg.norm(h, axis=1, keepdims=True) + 1e-9
    np.savez_compressed(os.path.join(OUT, f"{script}.npz"), ids=np.array(ids), skel=np.stack(skels).reshape(len(ids), 2, -1),
                        dt=np.stack(dts).reshape(len(ids), 2, -1), hog=h, dino=d,
                        length=np.array([r["length"] for r in recs]), endpoints=np.array([r["endpoints"] for r in recs]),
                        junctions=np.array([r["junctions"] for r in recs]), loops=np.array([r["loops"] for r in recs]))
    return len(ids)

if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(s, run(s), flush=True)
