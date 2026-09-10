"""Extract individual rongorongo glyph drawings from Barthel's (1958) Formentafeln.

Source: kohaumotu.org scan of Barthel, Grundlagen zur Entzifferung der
Osterinselschrift, 8 plates ("Formentafel 1-8"), 3800x3100 px at ~391 ppi.

Layout: each glyph is preceded (to its left) by its Barthel code number, set
in typeset numerals. Numbers sit in fixed columns (units digit; on plate 1 an
extra first column holds the one-digit numbers 1-9), the tens digit is the
row, the hundreds digit is the plate. Left and right halves of a plate have
independent row baselines.

Method: connected components -> numeral-sized components in the label zone of each column
-> grouped into labels -> columns matched to a template grid -> rows fitted
per half -> number derived from grid position, with tesseract OCR of every
label as an independent check, and a second check against the code numbers
used by the kohaumotu glyph library.

Output: data/glyphs/rongorongo/<NNN>.png, data/glyphs/rongorongo_manifest.json,
        data/qa/barthel_overlay_<plate>.png (annotated plates for visual review)
"""
import json, os, subprocess, tempfile
from collections import Counter
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the Deep Memory repository; this study lives in pipeline/rongo, data/rongo, docs/rongo, inputs/rongo
RAW = os.path.join(ROOT, "data", "rongo", "raw", "barthel")
OUT = os.path.join(ROOT, "data", "rongo", "glyphs", "rongorongo")
QA = os.path.join(ROOT, "data", "rongo", "qa")
os.makedirs(OUT, exist_ok=True); os.makedirs(QA, exist_ok=True)
KNOWN = set(l.strip() for l in open(os.path.join(RAW, "kohaumotu_glyph_numbers.txt")) if l.strip().isdigit())

# label right-edge template (px). Plate 0 has 11 columns (1-digit column first).
T_MAIN = [220, 552, 903, 1250, 1597, 2060, 2412, 2760, 3107, 3454]
T_P0 = [75, 400, 713, 1047, 1369, 1729, 2084, 2438, 2790, 3140, 3490]
NOMINAL_PITCH = {0: 236}

def ocr_digits(img):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        Image.fromarray(img).save(f.name); path = f.name
    best = ("", 0.0)
    try:
        for psm in ("7", "8"):
            r = subprocess.run(["tesseract", path, "stdout", "--psm", psm,
                                "-c", "tessedit_char_whitelist=0123456789", "tsv"],
                               capture_output=True, text=True)
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

def components(im, header_y=200):
    _, bw = cv2.threshold(im, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    n, lab, stats, cent = cv2.connectedComponentsWithStats(bw, connectivity=8)
    dt = cv2.distanceTransform(bw, cv2.DIST_L2, 3)
    comps = []
    for i in range(1, n):
        x, y, w, h, a = stats[i]
        if a < 12 or (y < header_y and x > 2800): continue   # plate header, top right only
        sub = dt[y:y+h, x:x+w][lab[y:y+h, x:x+w] == i]
        comps.append(dict(id=i, x=int(x), y=int(y), w=int(w), h=int(h), a=int(a),
                          cx=float(cent[i][0]), cy=float(cent[i][1]), stroke=float(sub.max() * 2)))
    return comps

def find_labels(comps):
    # single numerals are ~30-46 px tall and 4-40 px wide; two or three numerals sometimes touch (w up to 90)
    # (the numeral 4 is printed open and often splits into two shorter components, hence h >= 14)
    digit_like = [c for c in comps if 14 <= c["h"] <= 48 and 3 <= c["w"] <= 90
                  and c["a"] > 0.10 * c["w"] * c["h"]]
    digit_like.sort(key=lambda c: c["x"])
    used, labels = set(), []
    for c in digit_like:
        if c["id"] in used: continue
        grp = [c]; used.add(c["id"])
        while len(grp) < 3:
            gx1 = max(g["x"] + g["w"] for g in grp); gy = np.mean([g["cy"] for g in grp])
            cand = [d for d in digit_like if d["id"] not in used and abs(d["cy"] - gy) < 16 and -6 <= d["x"] - gx1 <= 14]
            if not cand: break
            d = min(cand, key=lambda d: d["x"]); grp.append(d); used.add(d["id"])
        labels.append(grp)
    recs = []
    for grp in labels:
        x0 = min(g["x"] for g in grp); x1 = max(g["x"] + g["w"] for g in grp)
        y0 = min(g["y"] for g in grp); y1 = max(g["y"] + g["h"] for g in grp)
        if y1 - y0 < 28: continue           # a label is at least one full-height numeral
        recs.append(dict(x0=x0, x1=x1, y0=y0, y1=y1, cy=(y0 + y1) / 2, n=len(grp), ids=[g["id"] for g in grp]))
    return recs

def fit_columns(recs, template):
    """Global shift of the template grid, then per-column refinement (columns drift by up to ~100 px between plates)."""
    best = (-1, 0)
    for s in range(-200, 201, 2):
        cnt = sum(1 for r in recs if min(abs(r["x1"] - (t + s)) for t in template) < 30)
        if cnt > best[0]: best = (cnt, s)
    cols = []
    for t in template:
        t0 = t + best[1]
        near = [r["x1"] for r in recs if abs(r["x1"] - t0) < 120]
        if len(near) >= 2:
            cl = max(cluster_1d(near, 30), key=len)
            cols.append(float(np.median(cl)))
        else:
            cols.append(float(t0))
    return cols

def extract_plate(path, plate_idx):
    im = np.array(Image.open(path).convert("L"))
    comps = components(im, header_y=260 if plate_idx == 0 else 200)
    recs = find_labels(comps)
    template = T_P0 if plate_idx == 0 else T_MAIN
    cols = fit_columns(recs, template)
    for r in recs:
        d = [abs(r["x1"] - c) for c in cols]; j = int(np.argmin(d))
        # a label is right-aligned on a column and lies entirely in the label zone left of it
        r["col"] = j if (d[j] < 35 and r["x0"] > cols[j] - 115) else None
    recs = [r for r in recs if r["col"] is not None]
    # trim any component that sits right of the column edge (glyph strokes mistaken for numerals)
    for r in recs:
        r["x1"] = min(r["x1"], int(cols[r["col"]] + 8))
    # OCR every label
    for r in recs:
        pad = 8
        crop = im[max(0, r["y0"]-pad):r["y1"]+pad, max(0, r["x0"]-pad):r["x1"]+pad]
        crop = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        crop = cv2.copyMakeBorder(crop, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=255)
        r["ocr"], r["ocr_conf"] = ocr_digits(crop)
    # rows per half
    row_map = {0: {}, 1: {}}
    split = 6 if plate_idx == 0 else 5
    pitch_nom = NOMINAL_PITCH.get(plate_idx, 285)
    for half in (0, 1):
        sub = [r for r in recs if (r["col"] >= split) == bool(half)]
        if not sub: continue
        rows = cluster_1d([r["cy"] for r in sub], 70)
        centers = [float(np.mean(x)) for x in rows]
        diffs = np.diff(centers)
        if len(diffs):
            units = np.maximum(1, np.round(diffs / pitch_nom))
            pitch = float(np.median(diffs / units))
        else:
            pitch = pitch_nom
        k = [int(round((c - centers[0]) / pitch)) for c in centers]
        # anchor tens of the first row by OCR vote
        votes = []
        for r in sub:
            ci = int(np.argmin([abs(c - r["cy"]) for c in centers])); r["k"] = k[ci]
            t = r["ocr"]
            if not t: continue
            if plate_idx == 0:
                if r["col"] == 0 and len(t) == 1: ot = int(t)
                elif r["col"] > 0 and len(t) == 2: ot = int(t[0])
                else: continue
            else:
                if len(t) == 3 and t[0] == str(plate_idx): ot = int(t[1])
                else: continue
            votes.append(ot - r["k"])
        tens0 = Counter(votes).most_common(1)[0][0] if votes else (1 if plate_idx == 0 else 0)
        for r in sub: r["tens"] = tens0 + r["k"]
        row_map[half] = {tens0 + kk: c for kk, c in zip(k, centers)}
    # one label per cell: keep the widest
    cells = {}
    for r in recs:
        key = (r["col"], r["tens"])
        if key not in cells or (r["x1"] - r["x0"]) > (cells[key]["x1"] - cells[key]["x0"]): cells[key] = r
    recs = list(cells.values())
    # cells with ink in the label zone but no parsed label: synthesise a label record from the grid
    all_ids = set(i for r in recs for i in r["ids"])
    for half in (0, 1):
        for tens, cy in row_map[half].items():
            for col in range(len(cols)):
                if (col >= split) != bool(half) or (col, tens) in cells: continue
                zone = [c for c in comps if c["id"] not in all_ids and cols[col] - 115 < c["x"] and c["x"] + c["w"] < cols[col] + 8
                        and abs(c["cy"] - cy) < 30 and c["h"] >= 14]
                if not zone: continue
                x0 = min(c["x"] for c in zone); x1 = max(c["x"] + c["w"] for c in zone)
                y0 = min(c["y"] for c in zone); y1 = max(c["y"] + c["h"] for c in zone)
                recs.append(dict(x0=x0, x1=x1, y0=y0, y1=y1, cy=cy, n=len(zone), ids=[c["id"] for c in zone],
                                 col=col, tens=tens, k=None, ocr="", ocr_conf=0.0, synthesised=True))
    # numbers and glyph regions
    label_ids = set(i for r in recs for i in r["ids"])
    glyph_comps = [c for c in comps if c["id"] not in label_ids]
    taken, results = set(), []
    recs.sort(key=lambda r: (r["cy"], r["col"]))
    for r in recs:
        tens = r["tens"]
        if plate_idx == 0:
            num = tens if r["col"] == 0 else tens * 10 + (r["col"] - 1)
        else:
            num = plate_idx * 100 + tens * 10 + r["col"]
        valid = (0 <= tens <= 9) and (num is not None) and num >= 1 and not (plate_idx == 0 and tens == 0)
        xmin = cols[r["col"]] + 12
        xmax = cols[r["col"] + 1] - 85 if r["col"] + 1 < len(cols) else cols[r["col"]] + 330
        parts = [c for c in glyph_comps if c["id"] not in taken and c["x"] >= xmin - 4 and xmin <= c["cx"] <= xmax
                 and abs(c["cy"] - r["cy"]) < 160]
        rec = dict(plate=plate_idx, col=r["col"], tens=int(tens), number=f"{num:03d}" if valid else None,
                   label_box=[int(r["x0"]), int(r["y0"]), int(r["x1"]), int(r["y1"])], ocr=r["ocr"], ocr_conf=round(r["ocr_conf"], 1),
                   label_parsed=not r.get("synthesised", False))
        if not parts or not valid:
            rec["status"] = "no_glyph" if valid else "bad_number"; results.append(rec); continue
        big = max(parts, key=lambda c: c["a"])
        parts = [c for c in parts if abs(c["cy"] - big["cy"]) < 130]
        for c in parts: taken.add(c["id"])
        rec["glyph_box"] = [int(min(c["x"] for c in parts)), int(min(c["y"] for c in parts)),
                            int(max(c["x"] + c["w"] for c in parts)), int(max(c["y"] + c["h"] for c in parts))]
        rec["ocr_agrees"] = (r["ocr"].zfill(3) == rec["number"]) if r["ocr"] else False
        rec["known"] = rec["number"] in KNOWN
        rec["status"] = "ok" if (rec["ocr_agrees"] and rec["known"]) else ("check_ocr" if rec["known"] else "review")
        results.append(rec)
    return im, results, cols

def overlay(im, results, path, scale=0.4):
    rgb = Image.fromarray(im).convert("RGB"); d = ImageDraw.Draw(rgb)
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 44)
    for r in results:
        x0, y0, x1, y1 = r["label_box"]
        col = {"ok": (0, 140, 0), "check_ocr": (200, 120, 0)}.get(r["status"], (200, 0, 0))
        d.rectangle([x0, y0, x1, y1], outline=col, width=4)
        if "glyph_box" in r:
            d.rectangle(r["glyph_box"], outline=(0, 80, 220), width=4)
        d.text((x0, y1 + 4), f"{r['number']}|{r['ocr']}", fill=col, font=font)
    rgb = rgb.resize((int(rgb.width * scale), int(rgb.height * scale)), Image.LANCZOS); rgb.save(path)

def main():
    manifest = []
    for p in range(8):
        im, res, cols = extract_plate(os.path.join(RAW, f"tafel-00{p}.png"), p)
        for r in res:
            if "glyph_box" in r and r["number"]:
                x0, y0, x1, y1 = r["glyph_box"]; pad = 10
                crop = im[max(0, y0-pad):y1+pad, max(0, x0-pad):x1+pad]
                fn = os.path.join(OUT, f"{r['number']}.png")
                if os.path.exists(fn):
                    r["status"] = "duplicate"; fn = os.path.join(OUT, f"{r['number']}_dup_{x0}.png")
                Image.fromarray(crop).save(fn); r["file"] = os.path.relpath(fn, ROOT)
            manifest.append(r)
        overlay(im, res, os.path.join(QA, f"barthel_overlay_{p}.png"))
        st = Counter(r["status"] for r in res)
        print(f"plate {p}: shift={cols[0]-(T_P0 if p==0 else T_MAIN)[0]} labels={len(res)} {dict(st)} "
              f"review={[r['number'] or r['ocr'] for r in res if r['status'] in ('review','bad_number','no_glyph','duplicate')]}")
    json.dump(manifest, open(os.path.join(ROOT, "data", "rongo", "glyphs", "rongorongo_manifest.json"), "w"), indent=1)
    nums = set(r["number"] for r in manifest if r.get("number") and "glyph_box" in r)
    print("extracted:", len(nums), "known:", len(KNOWN))
    print("missing:", sorted(KNOWN - nums))
    print("unexpected:", sorted(nums - KNOWN))

if __name__ == "__main__":
    main()
