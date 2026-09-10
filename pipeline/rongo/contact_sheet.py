"""Contact sheets of extracted glyphs for visual QA."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the Deep Memory repository; this study lives in pipeline/rongo, data/rongo, docs/rongo, inputs/rongo
def sheet(manifest, out_prefix, tile=(96, 96), per_row=16, per_sheet=192):
    recs = [r for r in manifest if r.get("file")]
    recs.sort(key=lambda r: r["number"])
    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 13)
    for si in range(0, len(recs), per_sheet):
        chunk = recs[si:si + per_sheet]
        rows = (len(chunk) + per_row - 1) // per_row
        W, H = per_row * tile[0], rows * (tile[1] + 18)
        im = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(im)
        for i, r in enumerate(chunk):
            g = Image.open(os.path.join(ROOT, r["file"])).convert("L")
            g.thumbnail((tile[0] - 8, tile[1] - 8))
            x = (i % per_row) * tile[0]; y = (i // per_row) * (tile[1] + 18)
            im.paste(g, (x + (tile[0] - g.width) // 2, y + (tile[1] - g.height) // 2))
            col = (0, 120, 0) if r.get("status") == "ok" else (180, 90, 0)
            d.text((x + 4, y + tile[1]), r["number"], fill=col, font=font)
        fn = f"{out_prefix}_{si // per_sheet}.png"; im.save(fn); print(fn, im.size, len(chunk))
if __name__ == "__main__":
    which = sys.argv[1]
    m = json.load(open(os.path.join(ROOT, "data", "rongo", "glyphs", f"{which}_manifest.json")))
    sheet(m, os.path.join(ROOT, "data", "rongo", "qa", f"sheet_{which}"))
