"""Study 3 pilot corpus: fetch every file in the pre-registered Commons categories.

Writes data/s3/raw/<group>/<id>.jpg (max 1024 px) and data/s3/corpus.json with
file name, Commons page, licence, artist, group and site coordinates.
"""
import os, json, subprocess, urllib.parse, time, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "s3"); RAW = os.path.join(OUT, "raw"); os.makedirs(RAW, exist_ok=True)
UA = "deep-memory-testbench/0.1 (ejhong@gmail.com)"

GROUPS = {
    "anatolia_ppn": dict(label="Göbekli Tepe, Karahan Tepe, Nevalı Çori", lat=37.22, lon=38.92, cats=[
        "Göbekli Tepe", "Göbeklitepe Building A", "Göbeklitepe Building B", "Göbeklitepe Building C", "Göbeklitepe Building D",
        "Göbekli Tepe finds and replicas in museums", "Karahan Tepe", "Karahantepe finds from the Neolithic age", "Nevalı Çori",
        "Nevalı Çori finds from neolithic period in the Urfa museum"]),
    "catalhoyuk": dict(label="Çatalhöyük", lat=37.67, lon=32.83, cats=["Çatalhöyük", "Çatalhöyük, findings"]),
    "rapa_nui": dict(label="Rapa Nui (Orongo, moai carvings)", lat=-27.11, lon=-109.35, cats=[
        "Petroglyphs in Orongo area", "Hoa Hakananai'a", "Historical drawings of Orongo", "Historical photographs of Orongo", "Moai tangata manu"]),
    "assyria": dict(label="Assyria (Nimrud)", lat=36.10, lon=43.33, cats=["Ashurnasirpal II reliefs", "Ashurnasirpal II reliefs in the British Museum", "Apkallu"]),
    "persepolis": dict(label="Achaemenid (Persepolis)", lat=29.93, lon=52.89, cats=[
        "Apadana stairs of Persepolis", "Relief of dignitaries at court ceremony, Apadana of Persepolis", "Assyrian delegation, Apadana", "Arachosian delegation, Apadana"]),
    "egypt": dict(label="Egypt (stelae)", lat=27.18, lon=31.18, cats=["Boundary Steles of Akhenaten", "Ancient Egyptian stelae in the Gregorian Egyptian Museum (Vatican Museums)"]),
    "maya": dict(label="Maya (stelae)", lat=16.5, lon=-90.0, cats=["Maya stelae", "Details of Maya stelae", "Maya stelae from Aguateca", "Maya stelae from Izapa", "Stela 5 of Izapa"]),
    "mississippian": dict(label="Mississippian", lat=38.66, lon=-90.06, cats=["Mississippian avian themed artwork", "Mississippian iconography", "Etowah copper artwork"]),
    "gotland": dict(label="Gotland picture stones", lat=57.5, lon=18.5, cats=["Picture stones of Gotland", "Picture stones in Gotlands fornsal"]),
    "tanum": dict(label="Tanum rock carvings", lat=58.70, lon=11.34, cats=["Rock carvings in Tanum", "Petroglyphs in Tanum Municipality"]),
}

def api(params):
    params.update(format="json"); url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)
    return json.loads(subprocess.run(["curl", "-s", "-m", "90", "-A", UA, url], capture_output=True, text=True).stdout)

def files_in(cat):
    out, cont = [], {}
    while True:
        r = api(dict(action="query", list="categorymembers", cmtitle="Category:" + cat, cmlimit=500, cmtype="file", **cont))
        out += [m["title"] for m in r.get("query", {}).get("categorymembers", [])]
        if "continue" in r: cont = r["continue"]
        else: break
    return out

def info(titles):
    res = {}
    for i in range(0, len(titles), 40):
        chunk = titles[i:i + 40]
        r = api(dict(action="query", titles="|".join(chunk), prop="imageinfo", iiprop="url|extmetadata|size|mime", iiurlwidth=1024))
        for p in r.get("query", {}).get("pages", {}).values():
            if "imageinfo" not in p: continue
            ii = p["imageinfo"][0]; em = ii.get("extmetadata", {})
            g = lambda k: re.sub(r"<[^>]+>", "", em.get(k, {}).get("value", "")).strip()
            res[p["title"]] = dict(url=ii.get("thumburl") or ii["url"], page=ii["descriptionurl"], license=g("LicenseShortName"),
                                   artist=g("Artist")[:100], mime=ii.get("mime", ""), w=ii["width"], h=ii["height"], desc=g("ImageDescription")[:300])
        time.sleep(0.2)
    return res

def main():
    corpus = []
    for gid, g in GROUPS.items():
        titles = []
        for c in g["cats"]:
            t = files_in(c); titles += t; print(f"  {gid}: {c} -> {len(t)}", flush=True); time.sleep(0.2)
        titles = sorted(set(titles))
        meta = info(titles)
        gdir = os.path.join(RAW, gid); os.makedirs(gdir, exist_ok=True)
        n = 0
        for k, t in enumerate(titles):
            m = meta.get(t)
            if not m or not m["mime"].startswith("image/") or m["mime"] in ("image/svg+xml", "image/gif"): continue
            if m["w"] < 300 or m["h"] < 300: continue
            fid = f"{gid}_{k:04d}"; path = os.path.join(gdir, fid + ".jpg")
            if not os.path.exists(path):
                subprocess.run(["curl", "-s", "-L", "-m", "120", "-A", UA, "-o", path, m["url"]])
                time.sleep(0.15)
            if os.path.exists(path) and os.path.getsize(path) > 5000:
                corpus.append(dict(id=fid, group=gid, title=t.replace("File:", ""), **{kk: m[kk] for kk in ("page", "license", "artist", "desc", "w", "h")}, path=os.path.relpath(path, ROOT))); n += 1
        print(f"{gid}: {n} images", flush=True)
    json.dump(dict(groups=GROUPS, images=corpus), open(os.path.join(OUT, "corpus.json"), "w"), indent=1, ensure_ascii=False)
    print("total", len(corpus))

if __name__ == "__main__":
    main()
