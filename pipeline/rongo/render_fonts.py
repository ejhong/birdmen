"""Render control-script sign inventories from Noto fonts (Google Fonts, OFL).

Each script's inventory is the set of encoded characters in its Unicode block(s)
that the font actually has an outline for (so unassigned code points and
combining marks are skipped). Output: data/glyphs/<script>/<U+XXXX>.png and
data/glyphs/<script>_manifest.json, in the same shape as the two scanned
inventories.
"""
import json, os, unicodedata
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # the Deep Memory repository; this study lives in pipeline/rongo, data/rongo, docs/rongo, inputs/rongo
FONTS = os.path.join(ROOT, "data", "rongo", "raw", "fonts")
OUT = os.path.join(ROOT, "data", "rongo", "glyphs")

# script id -> (font file, Unicode ranges, label, family/notes)
SCRIPTS = {
    "egyptian":      ("NotoSansEgyptianHieroglyphs-Regular.ttf", [(0x13000, 0x1342F)], "Egyptian hieroglyphs", "Egypt, c. 3200 BCE - 400 CE"),
    "anatolian":     ("NotoSansAnatolianHieroglyphs-Regular.ttf", [(0x14400, 0x1467F)], "Anatolian (Luwian) hieroglyphs", "Anatolia, c. 1400 - 700 BCE"),
    "linear_a":      ("NotoSansLinearA-Regular.ttf", [(0x10600, 0x1077F)], "Linear A", "Crete, c. 1800 - 1450 BCE"),
    "linear_b":      ("NotoSansLinearB-Regular.ttf", [(0x10000, 0x100FF)], "Linear B", "Crete and Greece, c. 1450 - 1200 BCE"),
    "cypro_minoan":  ("NotoSansCyproMinoan-Regular.ttf", [(0x12F90, 0x12FFF)], "Cypro-Minoan", "Cyprus, c. 1550 - 1050 BCE"),
    "cuneiform":     ("NotoSansCuneiform-Regular.ttf", [(0x12000, 0x123FF)], "Sumero-Akkadian cuneiform", "Mesopotamia, c. 3200 BCE - 100 CE"),
    "ugaritic":      ("NotoSansUgaritic-Regular.ttf", [(0x10380, 0x1039F)], "Ugaritic", "Syria, c. 1400 - 1200 BCE"),
    "old_persian":   ("NotoSansOldPersian-Regular.ttf", [(0x103A0, 0x103DF)], "Old Persian cuneiform", "Persia, c. 525 - 330 BCE"),
    "phoenician":    ("NotoSansPhoenician-Regular.ttf", [(0x10900, 0x1091F)], "Phoenician", "Levant, c. 1050 - 150 BCE"),
    "old_italic":    ("NotoSansOldItalic-Regular.ttf", [(0x10300, 0x1032F)], "Old Italic", "Italy, c. 700 - 100 BCE"),
    "carian":        ("NotoSansCarian-Regular.ttf", [(0x102A0, 0x102DF)], "Carian", "Anatolia, c. 700 - 300 BCE"),
    "lycian":        ("NotoSansLycian-Regular.ttf", [(0x10280, 0x1029F)], "Lycian", "Anatolia, c. 500 - 300 BCE"),
    "old_south_arabian": ("NotoSansOldSouthArabian-Regular.ttf", [(0x10A60, 0x10A7F)], "Old South Arabian", "Arabia, c. 900 BCE - 600 CE"),
    "meroitic":      ("NotoSansMeroitic-Regular.ttf", [(0x10980, 0x109FF)], "Meroitic", "Sudan, c. 300 BCE - 400 CE"),
    "runic":         ("NotoSansRunic-Regular.ttf", [(0x16A0, 0x16FF)], "Runic", "Northern Europe, c. 150 - 1100 CE"),
    "old_turkic":    ("NotoSansOldTurkic-Regular.ttf", [(0x10C00, 0x10C4F)], "Old Turkic", "Central Asia, c. 700 - 1000 CE"),
    "tifinagh":      ("NotoSansTifinagh-Regular.ttf", [(0x2D30, 0x2D7F)], "Tifinagh", "North Africa, c. 300 BCE - present"),
    "vai":           ("NotoSansVai-Regular.ttf", [(0xA500, 0xA63F)], "Vai", "Liberia, 1830s - present"),
    "mende_kikakui": ("NotoSansMendeKikakui-Regular.ttf", [(0x1E800, 0x1E8DF)], "Mende Kikakui", "Sierra Leone, 1920s - present"),
    "pahawh_hmong":  ("NotoSansPahawhHmong-Regular.ttf", [(0x16B00, 0x16B8F)], "Pahawh Hmong", "Laos, 1959 - present"),
    "nushu":         ("NotoSansNushu-Regular.ttf", [(0x1B170, 0x1B2FF)], "Nüshu", "Hunan, China, c. 1600s - present"),
    "yi":            ("NotoSansYi-Regular.ttf", [(0xA000, 0xA48F)], "Yi syllabary", "Sichuan, China, 1970s standardisation"),
}

def render_script(sid, font_file, ranges, size=160):
    path = os.path.join(FONTS, font_file)
    tt = TTFont(path)
    cmap = tt.getBestCmap()
    glyphset = tt.getGlyphSet()
    pil = ImageFont.truetype(path, size)
    outdir = os.path.join(OUT, sid); os.makedirs(outdir, exist_ok=True)
    manifest = []
    for lo, hi in ranges:
        for cp in range(lo, hi + 1):
            if cp not in cmap: continue
            cat = unicodedata.category(chr(cp))
            if cat.startswith("M") or cat in ("Cn", "Cf", "Zs", "Nd", "No", "Nl", "Po", "Pd", "Ps", "Pe", "Sm"):
                continue                       # marks, numerals, punctuation, unassigned
            gname = cmap[cp]
            if gname not in glyphset: continue
            try:
                bbox = pil.getbbox(chr(cp))
            except Exception:
                continue
            if bbox is None or bbox[2] - bbox[0] < 4 or bbox[3] - bbox[1] < 4: continue
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            im = Image.new("L", (w + 16, h + 16), 255)
            ImageDraw.Draw(im).text((8 - bbox[0], 8 - bbox[1]), chr(cp), font=pil, fill=0)
            # skip glyphs that rendered as (nearly) empty or as a .notdef box
            px = im.getextrema()
            if px[0] > 100: continue
            fn = os.path.join(outdir, f"U{cp:05X}.png"); im.save(fn)
            manifest.append(dict(number=f"U+{cp:04X}", name=unicodedata.name(chr(cp), ""), file=os.path.relpath(fn, ROOT),
                                 status="ok", source=font_file))
    json.dump(manifest, open(os.path.join(OUT, f"{sid}_manifest.json"), "w"), indent=1)
    return len(manifest)

if __name__ == "__main__":
    summary = {}
    for sid, (font, ranges, label, note) in SCRIPTS.items():
        n = render_script(sid, font, ranges)
        summary[sid] = n; print(f"{sid:20s} {n:5d}  {label}")
    json.dump({sid: dict(font=v[0], label=v[2], note=v[3], count=summary[sid]) for sid, v in SCRIPTS.items()},
              open(os.path.join(OUT, "control_scripts.json"), "w"), indent=1)
