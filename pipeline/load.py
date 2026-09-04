"""Load the Berezkin-Duvakin motif matrix (2016 snapshot parsed by D. Nikolaev's
mythology-queries project) into numpy, with English motif names/descriptions.

Source files (data/raw/berezkin/):
  berezkin_new.csv       926 traditions x 2,138 motifs, 0/1, plus name, lat, lon, area codes
  new_motif_list.json    column -> English motif name
  new_descriptions.json  motif code -> {name, description}
Catalogue: Yu. E. Berezkin & E. N. Duvakin, "Thematic classification and areal
distribution of folklore-mythological motifs", ruthenia.ru/folklore/berezkin,
CC BY-NC-SA 4.0.
"""
import os, csv, json, re
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "berezkin")

def code(col):
    return re.sub(r"_\d+$", "", col)

def load():
    rows = list(csv.reader(open(os.path.join(RAW, "berezkin_new.csv"), encoding="utf-8"), delimiter="\t"))
    hdr, data = rows[0], rows[1:]
    motcols = hdr[12:]
    codes = [code(c) for c in motcols]
    names = [r[1] for r in data]
    lat = np.array([float(r[2]) for r in data]); lon = np.array([float(r[3]) for r in data])
    areas = {k: [r[i] for r in data] for k, i in (("area1", 6), ("area2", 7), ("area3", 8))}
    M = np.array([[int(v) for v in r[12:]] for r in data], dtype=np.int8)
    ml = dict((code(c), n) for c, n in json.load(open(os.path.join(RAW, "new_motif_list.json"))))
    desc = json.load(open(os.path.join(RAW, "new_descriptions.json")))
    motifs = [dict(code=c, name=ml.get(c, ""), description=desc.get(c, {}).get("description", "")) for c in codes]
    return dict(names=names, lat=lat, lon=lon, areas=areas, M=M, motifs=motifs, codes=codes)

if __name__ == "__main__":
    d = load()
    print(d["M"].shape, d["M"].sum(), "traditions", len(d["names"]), "motifs", len(d["motifs"]))
