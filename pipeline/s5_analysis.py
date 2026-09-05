"""Study 5 analysis. Output: data/s5/results.json"""
import os, json, re, collections
import numpy as np
from scipy.cluster.hierarchy import linkage, leaves_list
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S5 = os.path.join(ROOT, "data", "s5"); CD = os.path.join(S5, "codes"); RAW = os.path.join(S5, "raw")
FEATS = ["flood_is_punishment", "warned_by_deity", "warned_by_animal", "single_hero_family", "vessel_built", "refuge_mountain", "refuge_tree", "animals_taken", "seeds_taken", "birds_sent_out", "raven_or_dove_named", "animal_scout_other", "earth_diver", "duration_stated", "forty_days", "sacrifice_after", "rainbow_or_promise", "repopulation_from_objects", "repopulation_by_incest", "survivors_marry_animal_or_spirit", "god_or_hero_bearded_or_pale", "fire_or_other_catastrophe_too", "giants_or_previous_race", "mentions_bible_or_noah", "told_as_local_river_or_sea", "whole_world_flooded"]
# details that are specific to the Genesis account (and its Mesopotamian ancestors), as opposed to what any flood story has
DIAGNOSTIC = ["birds_sent_out", "raven_or_dove_named", "rainbow_or_promise", "forty_days", "sacrifice_after", "animals_taken", "warned_by_deity"]
GENERIC = ["flood_is_punishment", "single_hero_family", "refuge_mountain", "whole_world_flooded", "vessel_built"]
ANCIENT = {"Sumerian", "Babylonian", "Assyrian", "Chaldean", "Hebrew", "Islamic", "Egypt", "Persian", "Zoroastrian", "Greek", "Arcadian", "Samothrace", "Roman", "India", "Hindu", "Bhil", "China", "Chinese"}

def main():
    E = {e["id"]: e for e in json.load(open(os.path.join(S5, "entries.json")))}
    C = [json.load(open(os.path.join(CD, f))) for f in os.listdir(CD) if f.endswith(".json")]
    refs = open(os.path.join(RAW, "references.txt")).read()
    years = {}
    for m in re.finditer(r"([A-Z][A-Za-z'\-]+)(?:, [^.]*?)?\. .*?\b(1[5-9]\d\d|20\d\d)\b", refs): years.setdefault(m.group(1), int(m.group(2)))
    rows = []
    for c in C:
        e = E[c["id"]]; ys = [years[a.split(" ")[0]] for a in e.get("cite_authors", []) if a.split(" ")[0] in years]
        v = {f: (1 if c[f] == "yes" else 0) for f in FEATS}; v["vessel_type"] = c["vessel_type"]; v["survivors_count"] = c["survivors_count"]
        rows.append(dict(id=c["id"], name=c["name"], region=c["region"], family=e.get("family"), xtn=bool(e.get("christian_terms")), xtn_terms=e.get("christian_terms", []), year=min(ys) if ys else None, ancient=c["name"].split(" ")[0] in ANCIENT or e["region"] == "Near East", diag=sum(v[f] for f in DIAGNOSTIC), generic=sum(v[f] for f in GENERIC), unclear=sum(1 for f in FEATS if c[f] == "unclear"), bible=v["mentions_bible_or_noah"], note=c["note"], text=e["text"][:900], cites=e["cites"], **{f: v[f] for f in FEATS}, vessel_type=v["vessel_type"], survivors_count=v["survivors_count"]))
    regions = sorted(set(r["region"] for r in rows)); res = dict(n=len(rows), regions=regions, feats=FEATS, diagnostic=DIAGNOSTIC, generic=GENERIC)
    res["prevalence"] = {reg: {f: float(np.mean([r[f] for r in rows if r["region"] == reg])) for f in FEATS} for reg in regions}
    res["prevalence"]["All"] = {f: float(np.mean([r[f] for r in rows])) for f in FEATS}; res["n_region"] = {reg: sum(1 for r in rows if r["region"] == reg) for reg in regions}
    # diagnostic score by region, and by whether the story itself mentions the Bible/Noah/missionaries
    res["diag_by_region"] = {reg: dict(n=len([r for r in rows if r["region"] == reg]), mean=float(np.mean([r["diag"] for r in rows if r["region"] == reg])), hist=np.bincount([r["diag"] for r in rows if r["region"] == reg], minlength=len(DIAGNOSTIC) + 1).tolist()) for reg in regions}
    res["diag_by_bible"] = {k: dict(n=len(g), mean=float(np.mean([r["diag"] for r in g])) if g else None, share_3plus=float(np.mean([r["diag"] >= 3 for r in g])) if g else None) for k, g in (("mentions", [r for r in rows if r["bible"]]), ("no_mention", [r for r in rows if not r["bible"]]))}
    # outside the ancient Near East / classical world: the stories with the most Genesis-specific details
    far = sorted([r for r in rows if not r["ancient"]], key=lambda r: (-r["diag"], r["name"]))
    res["far_top"] = [dict(name=r["name"], region=r["region"], family=r["family"], diag=r["diag"], details=[f for f in DIAGNOSTIC if r[f]], bible=r["bible"], xtn=r["xtn_terms"], year=r["year"], cites=r["cites"][:2], text=r["text"][:500]) for r in far[:25]]
    far3 = [r for r in far if r["diag"] >= 3]; res["far3"] = dict(n=len(far3), n_xtn=sum(1 for r in far3 if r["xtn"]), n_bible=sum(1 for r in far3 if r["bible"]))
    res["far_xtn"] = dict(n=sum(1 for r in far if r["xtn"]), mean_diag_xtn=float(np.mean([r["diag"] for r in far if r["xtn"]])) if any(r["xtn"] for r in far) else None, mean_diag_no=float(np.mean([r["diag"] for r in far if not r["xtn"]])))
    res["far_share_3plus"] = float(np.mean([r["diag"] >= 3 for r in far])); res["far_share_birds"] = float(np.mean([r["birds_sent_out"] for r in far])); res["far_n"] = len(far)
    res["ancient_share_birds"] = float(np.mean([r["birds_sent_out"] for r in rows if r["ancient"]])); res["ancient_n"] = sum(1 for r in rows if r["ancient"])
    # among far stories: birds-sent-out and bible-mention co-occurrence
    fb = [r for r in far if r["birds_sent_out"]]; res["far_birds"] = dict(n=len(fb), n_bible=sum(1 for r in fb if r["bible"]), n_xtn=sum(1 for r in fb if r["xtn"]), items=[dict(name=r["name"], region=r["region"], bible=r["bible"], raven_or_dove=r["raven_or_dove_named"], year=r["year"]) for r in fb])
    # Jaccard similarity on yes/no features (excluding the bible-mention flag), nearest neighbours of the Hebrew story, within vs between region
    F = [f for f in FEATS if f != "mentions_bible_or_noah"]; M = np.array([[r[f] for f in F] for r in rows], dtype=float)
    inter = M @ M.T; union = (M[:, None, :] + M[None, :, :] > 0).sum(2); J = np.where(union > 0, inter / np.maximum(union, 1), 0)
    idx = {r["id"]: i for i, r in enumerate(rows)}
    def nn(name, k=8):
        i = next(i for i, r in enumerate(rows) if r["name"] == name); order = np.argsort(-J[i]); return [dict(name=rows[j]["name"], region=rows[j]["region"], j=float(J[i, j]), diag=rows[j]["diag"], bible=rows[j]["bible"]) for j in order if j != i][:k]
    res["nn_hebrew"] = nn("Hebrew"); res["nn_babylonian"] = nn("Babylonian") if any(r["name"] == "Babylonian" for r in rows) else []
    reg_of = [r["region"] for r in rows]; within = [J[i, j] for i in range(len(rows)) for j in range(i + 1, len(rows)) if reg_of[i] == reg_of[j]]; between = [J[i, j] for i in range(len(rows)) for j in range(i + 1, len(rows)) if reg_of[i] != reg_of[j]]
    res["jaccard"] = dict(within_region=float(np.mean(within)), between_region=float(np.mean(between)))
    fam_of = [r["family"] or "?" for r in rows]; wf = [J[i, j] for i in range(len(rows)) for j in range(i + 1, len(rows)) if fam_of[i] == fam_of[j] and fam_of[i] != "?"]; bf = [J[i, j] for i in range(len(rows)) for j in range(i + 1, len(rows)) if fam_of[i] != fam_of[j] and "?" not in (fam_of[i], fam_of[j])]
    res["jaccard"].update(within_family=float(np.mean(wf)) if wf else None, between_family=float(np.mean(bf)) if bf else None)
    # permutation test: is within-region similarity higher than chance?
    rng = np.random.default_rng(0); obs = np.mean(within) - np.mean(between); null = []
    iu = np.triu_indices(len(rows), 1)
    for _ in range(500):
        perm = rng.permutation(reg_of); same = np.array([perm[i] == perm[j] for i, j in zip(*iu)]); vals = J[iu]; null.append(vals[same].mean() - vals[~same].mean())
    res["jaccard"]["perm_p"] = float(np.mean(np.array(null) >= obs)); res["jaccard"]["obs_diff"] = float(obs)
    # region-distinctive details: for each region, features whose prevalence is highest there and well above the rest
    res["distinctive"] = {}
    for reg in regions:
        inr = [r for r in rows if r["region"] == reg]; outr = [r for r in rows if r["region"] != reg]
        d = sorted([(f, float(np.mean([r[f] for r in inr])), float(np.mean([r[f] for r in outr]))) for f in F], key=lambda x: -(x[1] - x[2]))[:3]
        res["distinctive"][reg] = [dict(feat=f, inside=a, outside=b) for f, a, b in d if a - b > 0.15]
    res["rows"] = [{k: v for k, v in r.items() if k not in ("text", "note")} for r in rows]; res["vessel_by_region"] = {reg: dict(collections.Counter(r["vessel_type"] for r in rows if r["region"] == reg)) for reg in regions}
    res["earth_diver_by_region"] = {reg: float(np.mean([r["earth_diver"] for r in rows if r["region"] == reg])) for reg in regions}
    json.dump(res, open(os.path.join(S5, "results.json"), "w"), indent=1)
    print("n", len(rows), "unclear mean", np.mean([r["unclear"] for r in rows]))
    print("diag by region", {k: round(v["mean"], 2) for k, v in res["diag_by_region"].items()}); print("diag by bible mention", res["diag_by_bible"])
    print("far: share 3+ diagnostic", round(res["far_share_3plus"], 3), "birds far", round(res["far_share_birds"], 3), "birds ancient", round(res["ancient_share_birds"], 3), "far birds n/bible", res["far_birds"]["n"], res["far_birds"]["n_bible"])
    print("jaccard", res["jaccard"]); print("nn hebrew", [(x["name"], round(x["j"], 2)) for x in res["nn_hebrew"]])
    print("prevalence all", {f: round(v, 2) for f, v in res["prevalence"]["All"].items()})
if __name__ == "__main__": main()
