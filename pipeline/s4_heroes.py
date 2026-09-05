"""Study 4: blind lineups of de-identified culture-hero myths.

Each myth (a Wikipedia article's narrative, source and revision recorded) is retold by
Claude Sonnet 5 as a short neutral narrative with every identifying name removed. A judge
(Claude Opus 5, Claude Sonnet 5) then sees one TARGET story and ten CANDIDATE stories and
ranks the candidates by similarity of story content. One candidate is planted; the rest are
random hero myths from other regions. Sets: the lost-civilisation pairs (Viracocha,
Quetzalcoatl, Oannes, Osiris, Bochica, Votan, Thoth, Nommo); documented transmissions as
positive controls (Gilgamesh flood / Genesis flood, Ramayana / Reamker, Buddha / Barlaam,
Panchatantra / Kalila wa-Dimna); same-region pairs (related by contact); random pairs (the
base rate). Also a leak test: can a judge name the culture from the blind text?

usage: python s4_heroes.py prep | leak | plan | run <judge|all> | analyse
"""
import os, sys, json, random, hashlib, re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Literal
from pydantic import BaseModel
import anthropic
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S4 = os.path.join(ROOT, "data", "s4"); RAW = os.path.join(S4, "raw")
BL = os.path.join(S4, "blind"); LD = os.path.join(S4, "lineups"); os.makedirs(BL, exist_ok=True); os.makedirs(LD, exist_ok=True)
client = anthropic.Anthropic(); MODELS = {"opus": "claude-opus-5", "sonnet": "claude-sonnet-5"}

class Blind(BaseModel):
    story: str          # faithful retelling with names, 200-300 words
    blind: str          # the same story, de-identified
    identifying_terms_removed: List[str]

PREP = """Below is an encyclopedia article about a mythological figure or story. Retell THE MYTH (what the figure does, what happens, who does what to whom, what is brought, taught, made or destroyed) as a single narrative of 200-300 words, using ONLY what the article says. Ignore scholarship, etymology, dates, archaeology, modern reception and comparisons to other cultures.

Then write the SAME narrative de-identified so that a reader could not tell which culture, region, language or period it comes from: replace every personal name, deity name, place name, people's name and language-specific word with a plain role or description (the hero; the sky god; a great lake; a city on a hill; a foreign people). Keep everything else: actions, relationships, objects, animals (by kind), plants (by kind: 'maize' becomes 'a grain crop'; 'llama' becomes 'a pack animal'), numbers, sequence, outcomes. Do not add anything. List the identifying terms you removed."""

class Guess(BaseModel):
    region: Literal["andes", "mesoamerica", "amazonia", "north_america", "northwest_coast", "mesopotamia", "egypt", "near_east", "greece", "rome", "europe", "finland", "celtic", "germanic", "caucasus", "india", "china", "korea", "japan", "tibet", "southeast_asia", "polynesia", "melanesia", "australia", "siberia", "west_africa", "central_africa", "east_africa", "southern_africa", "cannot_tell"]
    named_figure_guess: str
    confidence: Literal["low", "medium", "high"]

LEAK = "This is a de-identified myth. From the text alone, which region and which named figure or story do you think it is? If you cannot tell, say cannot_tell. Be honest about confidence."

class Lineup(BaseModel):
    ranking: List[int]
    most_similar_reason: str
    least_similar_reason: str

JUDGE = """You are comparing STORIES for a study of narrative similarity. Below is a TARGET story and ten CANDIDATE stories numbered 1 to 10. All have been de-identified; do not guess or name cultures. Judge similarity of story content only: the roles of the figures, what they do, the sequence of events, what is brought or taught or made, the specific motifs and relationships. Weigh specific and unusual correspondences (the same distinctive episode, the same odd detail) far more than generic ones (a god, a journey, a punishment).

Rank ALL ten candidates from most similar to the target to least similar: a list of the ten candidate numbers, most similar first, each exactly once. Then one sentence on why your top choice is most similar and one on why your last is least."""

def load():
    W = json.load(open(os.path.join(RAW, "wiki_pages.json")))
    B = {k: json.load(open(os.path.join(BL, safe(k) + ".json"))) for k in W if os.path.exists(os.path.join(BL, safe(k) + ".json"))}
    return W, B
def safe(k): return re.sub(r"[^A-Za-z0-9]+", "_", k).strip("_")

def prep_one(k, v):
    out = os.path.join(BL, safe(k) + ".json")
    if os.path.exists(out): return "cached"
    text = v["text"][:14000]
    for attempt in range(3):
        try:
            r = client.messages.parse(model="claude-sonnet-5", max_tokens=3000, output_format=Blind, messages=[{"role": "user", "content": PREP + "\n\nARTICLE (" + v["title"] + "):\n" + text}])
            d = r.parsed_output.model_dump() if r.parsed_output else None
            if d: d.update(key=k, title=v["title"], region=v["region"], url=v["url"], revid=v["revid"]); json.dump(d, open(out, "w"), indent=1); return "ok"
        except Exception as e:
            if attempt == 2: return "error:" + str(e)[:80]
    return "error"

def leak(B):
    out = os.path.join(S4, "leak.json"); done = json.load(open(out)) if os.path.exists(out) else {}
    def one(k):
        r = client.messages.parse(model="claude-opus-5", max_tokens=600, output_format=Guess, messages=[{"role": "user", "content": LEAK + "\n\nTEXT:\n" + B[k]["blind"]}])
        d = r.parsed_output.model_dump(); d.update(true_region=B[k]["region"], title=B[k]["title"]); return k, d
    with ThreadPoolExecutor(max_workers=4) as ex:
        for f in as_completed([ex.submit(one, k) for k in B if k not in done]):
            try: k, d = f.result(); done[k] = d
            except Exception as e: print("err", e)
    json.dump(done, open(out, "w"), indent=1)
    hit = sum(1 for d in done.values() if d["region"] == d["true_region"]); print("region guessed correctly:", hit, "of", len(done))

HANCOCK = [("Viracocha", "Quetzalcoatl"), ("Viracocha", "Oannes"), ("Viracocha", "Osiris"), ("Quetzalcoatl", "Oannes"), ("Quetzalcoatl", "Osiris"), ("Oannes", "Osiris"), ("Bochica", "Quetzalcoatl"), ("Votan", "Quetzalcoatl"), ("Thoth", "Quetzalcoatl"), ("Nommo", "Oannes"), ("Viracocha", "Bochica")]
POSITIVE = [("Gilgamesh flood myth", "Genesis flood narrative"), ("Atra-Hasis", "Gilgamesh flood myth"), ("Utnapishtim", "Noah"), ("Ramayana", "Reamker"), ("Ramayana", "Ramakien"), ("Gautama Buddha", "Barlaam and Josaphat"), ("Panchatantra", "Kalila wa-Dimna"), ("Manu (Hinduism)", "Matsya"), ("Deucalion", "Noah")]
RELATED = [("Quetzalcoatl", "Kukulkan"), ("Viracocha", "Manco Cápac"), ("Viracocha", "Tunupa"), ("Osiris", "Isis"), ("Enki", "Oannes"), ("Fuxi", "Nüwa"), ("Māui (Māori mythology)", "Māui (Hawaiian mythology)"), ("Idris (prophet)", "Enoch (ancestor of Noah)")]

def plan(B):
    rng = random.Random(41); keys = sorted(B); reg = {k: B[k]["region"] for k in keys}
    special = {k for pr in HANCOCK + POSITIVE + RELATED for k in pr}
    def decoys(exclude, n=9):
        pool = [k for k in keys if reg[k] not in exclude and k not in special]; return rng.sample(pool, n)
    trials = []
    def add(setname, pair, n=10):
        for a, b in (pair, pair[::-1]):
            if a not in B or b not in B: print("missing", a, b); return
            for i in range(n):
                ds = decoys({reg[a], reg[b]}); cands = ds + [b]; rng.shuffle(cands)
                trials.append(dict(set=setname, pair=f"{a} | {b}", i=len(trials), target=a, planted=b, cands=cands, planted_pos=cands.index(b) + 1))
    for pr in HANCOCK: add("hancock", pr)
    for pr in POSITIVE: add("positive", pr)
    for pr in RELATED: add("related", pr)
    pool = [k for k in keys if k not in special]
    for i in range(60):
        a = rng.choice(pool); b = rng.choice([k for k in pool if reg[k] != reg[a]]); ds = decoys({reg[a], reg[b]}); ds = [d for d in ds if d not in (a, b)][:9]
        while len(ds) < 9:
            c = rng.choice(pool)
            if c not in ds and c not in (a, b) and reg[c] not in (reg[a], reg[b]): ds.append(c)
        cands = ds + [b]; rng.shuffle(cands); trials.append(dict(set="random", pair=f"{a} | {b}", i=len(trials), target=a, planted=b, cands=cands, planted_pos=cands.index(b) + 1))
    json.dump(trials, open(os.path.join(S4, "lineup_plan.json"), "w"), indent=0)
    import collections; print(collections.Counter(t["set"] for t in trials))

def judge(B, t, model):
    key = hashlib.md5(f"{t['i']}|{model}".encode()).hexdigest()[:16]; out = os.path.join(LD, key + ".json")
    if os.path.exists(out): return "cached"
    body = "TARGET:\n" + B[t["target"]]["blind"] + "\n\n" + "\n\n".join(f"CANDIDATE {k+1}:\n{B[c]['blind']}" for k, c in enumerate(t["cands"]))
    for attempt in range(3):
        try:
            r = client.messages.parse(model=MODELS[model], max_tokens=2000, output_format=Lineup, messages=[{"role": "user", "content": JUDGE + "\n\n" + body}])
            d = r.parsed_output.model_dump() if r.parsed_output else None
            if not d or sorted(int(x) for x in d["ranking"]) != list(range(1, 11)):
                if attempt < 2: continue
                json.dump(dict(t, model=model, error="bad_ranking"), open(out, "w")); return "bad"
            d["ranking"] = [int(x) for x in d["ranking"]]; d.update(t); d["model"] = model; d["planted_rank"] = d["ranking"].index(t["planted_pos"]) + 1
            json.dump(d, open(out, "w"), indent=1); return "ok"
        except Exception as e:
            if attempt == 2: json.dump(dict(t, model=model, error=str(e)[:200]), open(out, "w")); return "error"
    return "error"

def analyse(B):
    from scipy.stats import binomtest
    L = [json.load(open(os.path.join(LD, f))) for f in os.listdir(LD) if f.endswith(".json")]; L = [x for x in L if "planted_rank" in x]
    res = dict(n=len(L), by_set={}, by_pair={}, trials=[])
    def agg(rows):
        r = np.array([x["planted_rank"] for x in rows]); n1 = int((r == 1).sum()); n3 = int((r <= 3).sum())
        return dict(n=len(rows), mean_rank=float(r.mean()), rank1=n1, share_rank1=n1 / len(rows), share_top3=n3 / len(rows), p_rank1=float(binomtest(n1, len(rows), 0.1, alternative="greater").pvalue), hist=np.bincount(r, minlength=11)[1:].tolist())
    for s in sorted(set(x["set"] for x in L)):
        res["by_set"][s] = {j: agg([x for x in L if x["set"] == s and (j == "all" or x["model"] == j)]) for j in ("opus", "sonnet", "all") if [x for x in L if x["set"] == s and (j == "all" or x["model"] == j)]}
    for p in sorted(set(x["pair"] for x in L if x["set"] != "random")):
        rows = [x for x in L if x["pair"] == p]; res["by_pair"][p] = dict(set=rows[0]["set"], **agg(rows), by_judge={j: agg([x for x in rows if x["model"] == j]) for j in ("opus", "sonnet") if [x for x in rows if x["model"] == j]}, reasons_top=[x["most_similar_reason"] for x in rows if x["planted_rank"] == 1][:2], beaten_by={})
        for x in rows:
            for pos in x["ranking"][:x["planted_rank"] - 1]:
                c = x["cands"][pos - 1]; res["by_pair"][p]["beaten_by"][B[c]["title"]] = res["by_pair"][p]["beaten_by"].get(B[c]["title"], 0) + 1
        res["by_pair"][p]["beaten_by"] = dict(sorted(res["by_pair"][p]["beaten_by"].items(), key=lambda kv: -kv[1])[:6])
    leak = json.load(open(os.path.join(S4, "leak.json"))) if os.path.exists(os.path.join(S4, "leak.json")) else {}
    res["leak"] = dict(n=len(leak), region_correct=sum(1 for d in leak.values() if d["region"] == d["true_region"]), cannot_tell=sum(1 for d in leak.values() if d["region"] == "cannot_tell"), high_conf_correct=sum(1 for d in leak.values() if d["confidence"] == "high" and d["region"] == d["true_region"]), high_conf=sum(1 for d in leak.values() if d["confidence"] == "high"), per_item={k: dict(guess=d["region"], true=d["true_region"], figure=d["named_figure_guess"], conf=d["confidence"]) for k, d in leak.items()})
    mp = os.path.join(S4, "mechanical.json"); res["mechanical"] = json.load(open(mp)) if os.path.exists(mp) else None
    res["corpus"] = {k: dict(title=v["title"], region=v["region"], url=v["url"], revid=v["revid"], blind=v["blind"], story=v["story"]) for k, v in B.items()}
    json.dump(res, open(os.path.join(S4, "results.json"), "w"), indent=1)
    for s, v in res["by_set"].items(): print(s, {j: (round(a["mean_rank"], 2), a["rank1"], a["n"]) for j, a in v.items()})
    for p, v in res["by_pair"].items(): print(f"  {v['set']:9s} {p:55s} n={v['n']:2d} mean {v['mean_rank']:.2f} first {v['share_rank1']:.0%}")
    print("leak", {k: v for k, v in res["leak"].items() if k != "per_item"})

def main():
    W, B = load(); cmd = sys.argv[1]
    if cmd == "prep":
        counts = {}
        with ThreadPoolExecutor(max_workers=4) as ex:
            for f in as_completed([ex.submit(prep_one, k, v) for k, v in W.items()]): st = f.result(); counts[st[:5]] = counts.get(st[:5], 0) + 1
        print(counts)
    elif cmd == "leak": leak(B)
    elif cmd == "plan": plan(B)
    elif cmd == "run":
        trials = json.load(open(os.path.join(S4, "lineup_plan.json"))); judges = ["opus", "sonnet"] if sys.argv[2] == "all" else [sys.argv[2]]
        for m in judges:
            counts = {}
            with ThreadPoolExecutor(max_workers=4) as ex:
                for f in as_completed([ex.submit(judge, B, t, m) for t in trials]): st = f.result(); counts[st] = counts.get(st, 0) + 1
            print(m, counts, flush=True)
    elif cmd == "analyse": analyse(B)

if __name__ == "__main__":
    main()
