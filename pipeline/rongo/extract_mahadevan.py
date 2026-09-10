"""Extract the 417 Indus signs from Mahadevan (1977), The Indus Script: Texts,
Concordance and Tables, "Sign List of the Indus Script" (book pp. 32-35).

Source: archive.org scan, PDF pages 43-46, 827x1067 px (~100 ppi).

Layout: a 10-column grid, ~11 rows per page; each sign has its number set
beneath it (a dagger after the number marks signs with recorded variants).
Numbers run 1..417 consecutively in reading order, so the grid position
determines the number; tesseract OCR of every label is an independent check.

Output: data/glyphs/indus/<NNN>.png, data/glyphs/indus_manifest.json,
        data/qa/mahadevan_overlay_<page>.png
"""
import json, os, subprocess, tempfile
from collections import Counter
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the Deep Memory repository; this study lives in pipeline/rongo, data/rongo, docs/rongo, inputs/rongo
RAW = os.path.join(ROOT, "data", "rongo", "raw", "mahadevan")
OUT = os.path.join(ROOT, "data", "rongo", "glyphs", "indus")
QA = os.path.join(ROOT, "data", "rongo", "qa")
os.makedirs(OUT, exist_ok=True); os.makedirs(QA, exist_ok=True)

def ocr_digits(img):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        Image.fromarray(img).save(f.name); path = f.name
    best = ("", 0.0)
    try:
        for psm in ("7", "8"):
            r = subprocess.run(["tesseract", path, "stdout", "--psm", psm,
                                "-c", "tessedit_char_whitelist=0123456789", "tsv"], capture_output=True, text=True)
            words = [(p[11].strip(), float(p[10])) for p in (l.split("\t") for l in r.stdout.splitlines()[1:])
                     if len(p) == 12 and p[11].strip()]
            if words:
                txt = "".join(w for w, _ in words); conf = min(c for _, c in words)
                if conf > best[1]: best = (txt, conf)
    finally:
        os.unlink(path)
    return best

def cluster_1d(vals, gap):
    vals = sorted(vals); out = []
    for v in vals:
        if out and v - out[-1][-1] <= gap: out[-1].append(v)
        else: out.append([v])
    return out

def extract_page(path, page_idx, start_number):
    im = np.array(Image.open(path).convert("L"))
    H, W = im.shape
    _, bw = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(bw, connectivity=8)
    comps = []
    for i in range(1, n):
        x, y, w, h, a = stats[i]
        if a < 3: continue
        if y < 60 or y > H - 30: continue        # running head / page number
        comps.append(dict(id=i, x=int(x), y=int(y), w=int(w), h=int(h), a=int(a), cx=float(cent[i][0]), cy=float(cent[i][1])))
    # numerals: ~9-13 px tall. Group into labels by adjacency.
    digit_like = [c for c in comps if 8 <= c["h"] <= 14 and 3 <= c["w"] <= 12 and c["a"] > 0.25 * c["w"] * c["h"]]
    digit_like.sort(key=lambda c: c["x"])
    used, labels = set(), []
    for c in digit_like:
        if c["id"] in used: continue
        grp = [c]; used.add(c["id"])
        while len(grp) < 3:
            gx1 = max(g["x"] + g["w"] for g in grp); gy = np.mean([g["cy"] for g in grp])
            cand = [d for d in digit_like if d["id"] not in used and abs(d["cy"] - gy) < 4 and -1 <= d["x"] - gx1 <= 5]
            if not cand: break
            d = min(cand, key=lambda d: d["x"]); grp.append(d); used.add(d["id"])
        labels.append(grp)
    recs = []
    for grp in labels:
        x0 = min(g["x"] for g in grp); x1 = max(g["x"] + g["w"] for g in grp)
        y0 = min(g["y"] for g in grp); y1 = max(g["y"] + g["h"] for g in grp)
        recs.append(dict(x0=x0, x1=x1, y0=y0, y1=y1, cx=(x0 + x1) / 2, cy=(y0 + y1) / 2, n=len(grp), ids=[g["id"] for g in grp]))
    # rows: labels form horizontal bands
    cand = [float(np.mean(x)) for x in cluster_1d([r["cy"] for r in recs], 10) if len(x) >= 4]
    # real label rows lie on a regular grid (pitch ~87 px); fit y0/pitch and keep rows on it
    best = (-1, None)
    for pitch in np.arange(80, 96, 0.5):
        for y0 in np.arange(60, 200, 1.0):
            grid = [y0 + k * pitch for k in range(12) if y0 + k * pitch < H - 60]
            cnt = sum(1 for c in cand if min(abs(c - g) for g in grid) < 6)
            if cnt > best[0]: best = (cnt, (y0, pitch))
    y0, pitch = best[1]
    grid = [y0 + k * pitch for k in range(12) if y0 + k * pitch < H - 30]
    rows = []
    for g in grid:
        near = [c for c in cand if abs(c - g) < 14]
        if near: rows.append(min(near, key=lambda c: abs(c - g)))
    for r in recs:
        d = [abs(c - r["cy"]) for c in rows]; j = int(np.argmin(d))
        r["row"] = j if d[j] < 8 else None
    recs = [r for r in recs if r["row"] is not None]
    # columns: ten clusters of label centre-x
    template = [66, 140, 210, 280, 350, 420, 490, 560, 630, 700]
    best = (-1, 0)
    for sh in range(-40, 41):
        cnt = sum(1 for r in recs if min(abs(r["cx"] - (t + sh)) for t in template) < 14)
        if cnt > best[0]: best = (cnt, sh)
    cols = [t + best[1] for t in template]
    for r in recs:
        d = [abs(c - r["cx"]) for c in cols]; j = int(np.argmin(d))
        r["col"] = j if d[j] < 20 else None
    recs = [r for r in recs if r["col"] is not None]
    # Every grid cell is a sign (numbers run consecutively), so iterate cells rather than labels.
    label_ids = set(i for r in recs for i in r["ids"])
    by_cell = {(r["row"], r["col"]): r for r in sorted(recs, key=lambda r: r["x1"] - r["x0"])}
    results, taken = [], set()
    col_half = (cols[1] - cols[0]) / 2
    # Sign 218 (page 33, last row) is set double width, so that row has nine signs across ten columns.
    SPANS = {(1, 10): [[0], [1], [2], [3], [4], [5], [6], [7, 8], [9]]}
    num = start_number
    for ri, ry in enumerate(rows):
        spans = SPANS.get((page_idx, ri), [[c] for c in range(10)])
        for span in spans:
            ci = span[0]; cx = float(np.mean([cols[c] for c in span]))
            half = col_half * len(span)
            if num > 417: break
            this = num; num += 1
            top = (rows[ri - 1] + 12) if ri > 0 else 60
            bottom = ry - 8                       # label band is ry +- 8
            # numeral-sized pieces hugging either label band are stray label fragments, not sign strokes
            in_band = lambda c: (abs(c["cx"] - cx) < half - 1 and c["y"] >= top - 2 and c["cy"] < bottom
                                 and not (c["h"] <= 14 and (c["cy"] < top + 10 or c["cy"] > bottom - 4)))
            parts = [c for c in comps if c["id"] not in taken and c["id"] not in label_ids and in_band(c) and c["y"] + c["h"] <= ry - 4]
            rec = dict(page=page_idx, row=ri, col=ci, number=f"{this:03d}")
            r = by_cell.get((ri, ci))
            if r is not None:
                pad = 3
                crop = im[max(0, r["y0"]-pad):r["y1"]+pad, max(0, r["x0"]-pad):r["x1"]+pad]
                crop = cv2.resize(crop, None, fx=6, fy=6, interpolation=cv2.INTER_CUBIC)
                crop = cv2.copyMakeBorder(crop, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
                txt, conf = ocr_digits(crop)
                rec.update(ocr=txt, ocr_conf=round(conf, 1), label_box=[int(r["x0"]), int(r["y0"]), int(r["x1"]), int(r["y1"])])
            else:
                rec.update(ocr="", ocr_conf=0, label_box=[int(cx - 15), int(ry - 6), int(cx + 15), int(ry + 6)])
            if not parts:   # retry with a looser lower bound (some tall signs nearly touch their number)
                parts = [c for c in comps if c["id"] not in taken and c["id"] not in label_ids and in_band(c) and c["y"] + c["h"] <= ry + 2]
            if not parts:   # last resort: numeral-sized strokes that were grouped as a label but sit in the glyph band
                parts = [c for c in comps if c["id"] not in taken and in_band(c) and c["y"] + c["h"] <= ry - 4]
            if not parts:
                if os.environ.get("DEBUG_CELL") == f"{page_idx},{ri},{ci}":
                    print("DEBUG cell", (page_idx, ri, ci), "cx", cx, "half", half, "top", top, "ry", ry, "bottom", bottom)
                    for c in comps:
                        if abs(c["cx"] - cx) < 60 and top - 40 < c["cy"] < ry + 10:
                            print("   ", c, "taken" if c["id"] in taken else "", "label" if c["id"] in label_ids else "")
                rec["status"] = "no_glyph"; results.append(rec); continue
            for c in parts: taken.add(c["id"])
            rec["glyph_box"] = [int(min(c["x"] for c in parts)), int(min(c["y"] for c in parts)),
                                int(max(c["x"] + c["w"] for c in parts)), int(max(c["y"] + c["h"] for c in parts))]
            rec["ocr_agrees"] = (rec["ocr"] == str(this))
            rec["status"] = "ok" if rec["ocr_agrees"] else "check_ocr"
            results.append(rec)
    return im, results, cols, rows

def overlay(im, results, path):
    rgb = Image.fromarray(im).convert("RGB").resize((im.shape[1] * 2, im.shape[0] * 2), Image.LANCZOS)
    d = ImageDraw.Draw(rgb); font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    for r in results:
        x0, y0, x1, y1 = [v * 2 for v in r["label_box"]]
        col = {"ok": (0, 140, 0), "check_ocr": (200, 120, 0)}.get(r["status"], (200, 0, 0))
        d.rectangle([x0, y0, x1, y1], outline=col, width=2)
        if "glyph_box" in r: d.rectangle([v * 2 for v in r["glyph_box"]], outline=(0, 80, 220), width=2)
        d.text((x0, y1 + 2), f"{int(r['number'])}|{r['ocr']}", fill=col, font=font)
    rgb.save(path)

def main():
    manifest = []
    STARTS = {0: 1, 1: 111, 2: 220, 3: 330}   # page 33 holds 111-219 (109 signs), page 34 holds 220-329
    for p in range(4):
        start = STARTS[p]
        im, res, cols, rows = extract_page(os.path.join(RAW, f"signlist-00{p}.jpg"), p, start)
        for r in res:
            if "glyph_box" in r:
                x0, y0, x1, y1 = r["glyph_box"]; pad = 3
                crop = im[max(0, y0-pad):y1+pad, max(0, x0-pad):x1+pad]
                fn = os.path.join(OUT, f"{r['number']}.png"); Image.fromarray(crop).save(fn); r["file"] = os.path.relpath(fn, ROOT)
            manifest.append(r)
        overlay(im, res, os.path.join(QA, f"mahadevan_overlay_{p}.png"))
        st = Counter(r["status"] for r in res)
        print(f"page {p}: start={start} rows={len(rows)} cols={[int(c) for c in cols]} labels={len(res)} {dict(st)} "
              f"ocr_mismatch={[(r['number'], r['ocr']) for r in res if r['status']!='ok']}")
    json.dump(manifest, open(os.path.join(ROOT, "data", "rongo", "glyphs", "indus_manifest.json"), "w"), indent=1)
    print("total signs:", len(manifest), "last number:", manifest[-1]["number"])

if __name__ == "__main__":
    main()
