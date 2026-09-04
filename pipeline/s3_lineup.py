"""Study 3, pilot C: blind lineups (the social-rv design).

A judge sees one target panel and ten numbered candidates, and ranks the ten
from most to least similar to the target. One candidate is "planted"; the
other nine are random decoys from other traditions. The planted item's rank
(chance: 5.5 on average, 10% chance of rank 1) measures whether it stands out.

Sets:
  moai_among_random   target Pillar 43 (whole); planted = moai back; 9 decoys from other traditions   40 trials
  p43_among_random    target moai back; planted = Pillar 43 (whole); 9 decoys                          40 trials
  hard                target Pillar 43; planted = moai back; 9 decoys = Opus's top foreign matches for P43  10 trials
  related_control     target random Persepolis panel; planted = random Assyrian panel; 9 decoys        40 trials
  same_control        target random panel; planted = another panel of its tradition; 9 decoys          40 trials
  moai_close_among_random  as moai_among_random but the planted item is the close view of the back      40 trials
  moai_iso_among_random    both targets with backgrounds removed; 9 random decoys                       40 trials
  moai_iso_among_monoliths as above but decoys are free-standing monoliths and statues only              40 trials
  p43_iso_among_monoliths  moai (isolated) as target; Pillar 43 (isolated) planted among monoliths       40 trials
  same_control_monoliths   same-tradition control drawn from monoliths and statues only                 40 trials
Judges: opus, gpt, gemini on all sets; sonnet, grok on the first 12 trials of each set.

usage: python s3_lineup.py plan | run <judge> [set] | run all [set]
"""
import os, sys, json, io, base64, time, random, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Literal
from pydantic import BaseModel
import anthropic
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S3 = os.path.join(ROOT, "data", "s3"); LD = os.path.join(S3, "lineups")  # v2 prompt (depicted content); v1 archived in lineups_v1; os.makedirs(LD, exist_ok=True)
MODELS = {"opus": "claude-opus-5", "sonnet": "claude-sonnet-5", "gpt": "gpt-5.5", "gemini": "gemini-3.1-pro-preview", "grok": "grok-4.6"}
client = anthropic.Anthropic()

class Lineup(BaseModel):
    ranking: List[int]
    most_similar_reason: str
    least_similar_reason: str

from s3_judge import CONTENT
PROMPT = CONTENT + """

On the left is a TARGET decorated surface. On the right are ten CANDIDATE surfaces numbered 1 to 10. You know nothing about where any of them is from; do not guess or name cultures, sites or periods. Judge similarity of DEPICTED CONTENT only: shared kinds of depicted elements, the specific forms they take, the relationships between them, their arrangement, and the style in which they are drawn (not the medium, not the photograph).

Rank ALL ten candidates from most similar to the target to least similar. Return the ranking as a list of the ten candidate numbers, most similar first, each number exactly once. Then give one sentence on why your top choice is the most similar in depicted content and one on why your last choice is the least."""

def _openai_client(kind):
    from openai import OpenAI
    import certifi; os.environ.setdefault("SSL_CERT_FILE", certifi.where())
    if kind == "gpt": return OpenAI()
    if kind == "gemini": return OpenAI(api_key=os.environ["GEMINI_API_KEY"], base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
    if kind == "grok": return OpenAI(api_key=os.environ["XAI_API_KEY"], base_url="https://api.x.ai/v1")

def load_corpus():
    corpus = json.load(open(os.path.join(S3, "corpus.json")))["images"]
    sel = set(json.load(open(os.path.join(S3, "selected.json"))))
    ims = {im["id"]: im for im in corpus if im["id"] in sel}
    return ims, json.load(open(os.path.join(S3, "targets.json")))

def composite(ims, target, cands, h=420):
    f = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
    t = Image.open(os.path.join(ROOT, ims[target]["path"])).convert("RGB"); t.thumbnail((h * 2, h * 2))
    cw, ch = 300, 300
    tiles = []
    for c in cands:
        im = Image.open(os.path.join(ROOT, ims[c]["path"])).convert("RGB"); im.thumbnail((cw - 10, ch - 40))
        tile = Image.new("RGB", (cw, ch), (255, 255, 255)); tile.paste(im, ((cw - im.width) // 2, 36 + (ch - 40 - im.height) // 2)); tiles.append(tile)
    grid = Image.new("RGB", (5 * cw + 40, 2 * ch + 30), (246, 241, 232)); d = ImageDraw.Draw(grid)
    for k, tile in enumerate(tiles):
        x, y = 10 + (k % 5) * (cw + 5), 10 + (k // 5) * (ch + 10); grid.paste(tile, (x, y)); d.text((x + 8, y + 4), str(k + 1), fill=(154, 91, 51), font=f)
    W = t.width + grid.width + 60; H = max(t.height, grid.height) + 60
    out = Image.new("RGB", (W, H), (246, 241, 232)); d = ImageDraw.Draw(out)
    out.paste(t, (20, 50)); d.text((20, 10), "TARGET", fill=(32, 27, 18), font=f)
    out.paste(grid, (t.width + 40, 50)); d.text((t.width + 40, 10), "CANDIDATES 1-10", fill=(32, 27, 18), font=f)
    if out.width > 2000: out = out.resize((2000, int(out.height * 2000 / out.width)), Image.LANCZOS)
    buf = io.BytesIO(); out.save(buf, "JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()

def judge(ims, trial, model):
    key = hashlib.md5(f"{trial['set']}|{trial['i']}|{model}".encode()).hexdigest()[:16]
    out = os.path.join(LD, key + ".json")
    if os.path.exists(out): return "cached"
    b64 = composite(ims, trial["target"], trial["cands"])
    for attempt in range(3):
        try:
            if model in ("opus", "sonnet"):
                r = client.messages.parse(model=MODELS[model], max_tokens=3000, output_format=Lineup,
                                          messages=[{"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}}, {"type": "text", "text": PROMPT}]}])
                d = r.parsed_output.model_dump() if r.parsed_output else None
            elif model == "gpt":
                schema = Lineup.model_json_schema(); schema["additionalProperties"] = False
                for k, v in schema.get("properties", {}).items(): v.pop("title", None)
                r = _openai_client("gpt").responses.create(model=MODELS["gpt"], input=[{"role": "user", "content": [{"type": "input_image", "image_url": "data:image/jpeg;base64," + b64}, {"type": "input_text", "text": PROMPT}]}],
                                                            text={"format": {"type": "json_schema", "name": "lineup", "schema": schema, "strict": True}})
                d = json.loads(r.output_text)
            else:
                c = _openai_client(model)
                r = c.chat.completions.create(model=MODELS[model], messages=[{"role": "user", "content": [{"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}, {"type": "text", "text": PROMPT + "\n\nRespond with a single JSON object: {\"ranking\": [ten integers], \"most_similar_reason\": string, \"least_similar_reason\": string}."}]}], response_format={"type": "json_object"})
                d = json.loads(r.choices[0].message.content)
            if not d or sorted(int(x) for x in d.get("ranking", [])) != list(range(1, 11)):
                if attempt < 2: continue
                json.dump(dict(trial, model=model, error="bad_ranking", raw=d), open(out, "w")); return "bad"
            d["ranking"] = [int(x) for x in d["ranking"]]
            d.update(trial); d["model"] = model; d["planted_rank"] = d["ranking"].index(trial["planted_pos"]) + 1
            json.dump(d, open(out, "w"), indent=1); return "ok"
        except Exception as e:
            if attempt == 2:
                json.dump(dict(trial, model=model, error=str(e)[:200]), open(out, "w")); return "error"
            time.sleep(5)
    return "error"

def plan(ims, T):
    rng = random.Random(7); ids = sorted(ims); grp = {i: ims[i]["group"] for i in ids}
    p43, hoa = T["pillar43"], T["hoa_back"]; special = {T[k] for k in T}
    def decoys(exclude_groups, n=9, exclude_ids=()):
        pool = [i for i in ids if grp[i] not in exclude_groups and i not in special and i not in exclude_ids]
        return rng.sample(pool, n)
    def trial(setname, i, target, planted, ds):
        cands = ds + [planted]; rng.shuffle(cands)
        return dict(set=setname, i=i, target=target, planted=planted, cands=cands, planted_pos=cands.index(planted) + 1, decoy_groups=[grp[c] for c in ds])
    trials = []
    for i in range(40): trials.append(trial("moai_among_random", i, p43, hoa, decoys({"anatolia_ppn", "rapa_nui"})))
    for i in range(40): trials.append(trial("p43_among_random", i, hoa, p43, decoys({"anatolia_ppn", "rapa_nui"})))
    # hard lineup: Opus's best matches for Pillar 43 as decoys
    res = json.load(open(os.path.join(S3, "results_judge.json"))) if os.path.exists(os.path.join(S3, "results_judge.json")) else None
    if res and "search_p43" in res:
        rng_h = random.Random(11); top9 = [x["id"] for x in res["search_p43"]["top_foreign"]][:9]
        for i in range(10):
            cands = top9 + [hoa]; rng_h.shuffle(cands)
            trials.append(dict(set="hard", i=i, target=p43, planted=hoa, cands=cands, planted_pos=cands.index(hoa) + 1, decoy_groups=[grp[c] for c in top9]))
    A = [i for i in ids if grp[i] == "assyria" and i not in special]; P = [i for i in ids if grp[i] == "persepolis" and i not in special]
    for i in range(40):
        t = rng.choice(P); pl = rng.choice(A); trials.append(trial("related_control", i, t, pl, decoys({"assyria", "persepolis"})))
    for i in range(40):
        t = rng.choice([x for x in ids if x not in special]); same = [x for x in ids if grp[x] == grp[t] and x != t and x not in special]
        if not same: continue
        pl = rng.choice(same); trials.append(trial("same_control", i, t, pl, decoys({grp[t]})))
    # close view of the moai's back (hoa_back2), own seed so the sets above are unchanged
    rng2 = random.Random(99); hoa2 = T["hoa_back2"]
    for i in range(40):
        pool = [x for x in ids if grp[x] not in {"anatolia_ppn", "rapa_nui"} and x not in special]; ds = rng2.sample(pool, 9)
        cands = ds + [hoa2]; rng2.shuffle(cands)
        trials.append(dict(set="moai_close_among_random", i=i, target=p43, planted=hoa2, cands=cands, planted_pos=cands.index(hoa2) + 1, decoy_groups=[grp[c] for c in ds]))
    # isolated targets (background removed) and object-type-matched decoys (needs objtype.json)
    OT = os.path.join(S3, "objtype.json")
    if os.path.exists(OT) and "pillar43_iso" in T:
        ot = json.load(open(OT)); p43i, hoai = T["pillar43_iso"], T["hoa_back_iso"]
        mono = [x for x in ids if x not in special and ot.get(x, {}).get("object_type") in ("freestanding_monolith", "statue")]
        rng3 = random.Random(2027)
        def mk(setname, i, target, planted, pool, exclude_groups):
            ds = rng3.sample([x for x in pool if grp[x] not in exclude_groups], 9); cands = ds + [planted]; rng3.shuffle(cands)
            return dict(set=setname, i=i, target=target, planted=planted, cands=cands, planted_pos=cands.index(planted) + 1, decoy_groups=[grp[c] for c in ds])
        allpool = [x for x in ids if x not in special]
        for i in range(40): trials.append(mk("moai_iso_among_random", i, p43i, hoai, allpool, {"anatolia_ppn", "rapa_nui"}))
        for i in range(40): trials.append(mk("moai_iso_among_monoliths", i, p43i, hoai, mono, {"anatolia_ppn", "rapa_nui"}))
        for i in range(40): trials.append(mk("p43_iso_among_monoliths", i, hoai, p43i, mono, {"anatolia_ppn", "rapa_nui"}))
        i = 0
        while i < 40:
            t = rng3.choice(mono); same = [x for x in mono if grp[x] == grp[t] and x != t]
            if len(same) < 1 or len([x for x in mono if grp[x] != grp[t]]) < 9: continue
            pl = rng3.choice(same); trials.append(mk("same_control_monoliths", i, t, pl, mono, {grp[t]})); i += 1
    json.dump(trials, open(os.path.join(S3, "lineup_plan.json"), "w"), indent=0)
    return trials

def main():
    ims, T = load_corpus()
    if sys.argv[1] == "plan":
        tr = plan(ims, T); import collections; print(collections.Counter(t["set"] for t in tr)); return
    trials = json.load(open(os.path.join(S3, "lineup_plan.json")))
    if len(sys.argv) > 3: trials = [t for t in trials if t["set"] == sys.argv[3]]
    judges = ["opus", "gpt", "gemini", "sonnet", "grok"] if sys.argv[2] == "all" else [sys.argv[2]]
    for m in judges:
        jobs = [t for t in trials if m in ("opus", "gpt", "gemini") or t["i"] < 12]
        counts = {}; workers = 2 if m == "grok" else 5
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(judge, ims, t, m) for t in jobs]
            for f in as_completed(futs):
                st = f.result(); counts[st] = counts.get(st, 0) + 1
        print(m, "done", counts, flush=True)

if __name__ == "__main__":
    main()
