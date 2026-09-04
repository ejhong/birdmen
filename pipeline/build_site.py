"""Assemble docs/data/site.json for the static page."""
import os, json
from load import load

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs"); os.makedirs(os.path.join(DOCS, "data"), exist_ok=True)

AREAS = {"1": "Sub-Saharan Africa", "2": "Madagascar", "3": "North Africa, Mediterranean, Near East", "4": "Central and Eastern Europe",
         "5": "Caucasus, Central and South Asia", "6": "Tribal India, South-East Asia, Indonesia", "7": "Melanesia, Micronesia, Polynesia",
         "8": "Australia", "9": "Siberia and Inner Asia", "10": "Taiwan, China, Japan", "11": "Arctic", "12": "Western North America",
         "13": "Plains and Eastern North America", "14": "Mesoamerica and Central Andes", "15": "Amazonia and Eastern South America",
         "16": "Chaco and Southern Cone"}

def coast():
    g = json.load(open(os.path.join(ROOT, "data", "raw", "ne_110m_coastline.geojson")))
    lines = []
    for f in g["features"]:
        geom = f["geometry"]; parts = geom["coordinates"] if geom["type"] == "MultiLineString" else [geom["coordinates"]]
        for p in parts:
            pts = [[round(x, 1), round(y, 1)] for x, y in p]
            dedup = [pts[0]] + [q for i, q in enumerate(pts[1:], 1) if q != pts[i - 1]]
            if len(dedup) > 1: lines.append(dedup)
    return lines

def main():
    d = load()
    res = json.load(open(os.path.join(ROOT, "data", "results", "results.json")))
    cl = json.load(open(os.path.join(ROOT, "data", "classes.json")))
    desc = {m["code"]: m for m in d["motifs"]}
    classes = {k: [dict(x, description=desc[x["code"]]["description"], n=int(d["M"][:, d["codes"].index(x["code"])].sum())) for x in v] for k, v in cl.items()}
    site = dict(results={k: v for k, v in res.items()}, classes=classes, areas=AREAS, coast=coast())
    json.dump(site, open(os.path.join(DOCS, "data", "site.json"), "w"))
    print("site.json", os.path.getsize(os.path.join(DOCS, "data", "site.json")) // 1024, "KB")

if __name__ == "__main__":
    main()
