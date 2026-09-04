"""Study 3, pilot B: direct pairwise similarity judgment, blind.

Two panels are composited side by side (labelled A and B, random order, no
captions) and a vision model rates how alike they are on a fixed rubric.
Judgments are cached per (image a, image b, model, order).

Sets (all from the triaged, capped corpus of 450):
  target       Pillar 43 vs moai back, 4 times (both orders x both models)
  search_p43   Pillar 43 vs every other panel            (opus)
  search_hoa   moai back vs every other panel            (opus)
  null         1,500 random pairs from different groups  (opus)
  same         200 random pairs from the same group      (opus)
  poscontrol   150 random Assyria x Persepolis pairs     (opus)
  reliability  200 of the null pairs re-judged           (sonnet)

usage: python s3_judge.py plan | run <set> | run all
"""
import os, sys, json, io, base64, time, random, hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Literal
from pydantic import BaseModel
import anthropic
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S3 = os.path.join(ROOT, "data", "s3"); JD = os.path.join(S3, "judgments")  # v2 prompt (depicted content); v1 archived in judgments_v1; os.makedirs(JD, exist_ok=True)
MODELS = {"opus": "claude-opus-5", "sonnet": "claude-sonnet-5", "gpt": "gpt-5.5"}
client = anthropic.Anthropic()
_openai = None
def openai_client():
    global _openai
    if _openai is None:
        import certifi; os.environ.setdefault("SSL_CERT_FILE", certifi.where())
        from openai import OpenAI; _openai = OpenAI()
    return _openai

def judge_openai(block, prompt):
    schema = Judgment.model_json_schema(); schema["additionalProperties"] = False
    for k, v in schema.get("properties", {}).items(): v.pop("title", None)
    r = openai_client().responses.create(model=MODELS["gpt"], input=[{"role": "user", "content": [{"type": "input_image", "image_url": "data:image/jpeg;base64," + block["source"]["data"]}, {"type": "input_text", "text": prompt}]}],
                                          text={"format": {"type": "json_schema", "name": "judgment", "schema": schema, "strict": True}})
    return json.loads(r.output_text), [r.usage.input_tokens, r.usage.output_tokens]

class Judgment(BaseModel):
    shared_elements: List[str]
    element_similarity: Literal["0", "1", "2", "3"]
    relationship_similarity: Literal["0", "1", "2", "3"]
    arrangement_similarity: Literal["0", "1", "2", "3"]
    style_similarity: Literal["0", "1", "2", "3"]
    gestalt_similarity: Literal["0", "1", "2", "3"]
    overall: Literal["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    justification: str

CONTENT = """WHAT TO COMPARE. You are comparing WHAT IS DEPICTED: the subject matter and iconography of the artwork. That means the kinds of things shown (creatures, human figures, body parts, objects, symbols, geometric motifs), the specific forms they take (a standing figure holding a staff; an animal shown in profile; a rosette; a boat; a row of repeated signs), how they are combined, the relationships between them (what holds, touches, faces, sits on or encloses what), how they are arranged on the surface, and the STYLE in which they are drawn: schematic or naturalistic, proportions, outline and infill conventions, how a wing or a hand or an eye is rendered.
Do NOT compare, and do not let your score be moved by: the medium or material (stone, clay, plaster, paint, metal, wood); the colour or texture of the material; erosion, damage or state of preservation; the scale of the object; and above all the photographs themselves (lighting, angle, cropping, resolution, sharpness, colour cast, background, whether the picture is a drawing, a museum shot or a field snapshot). Two surfaces that show the same kinds of things in the same arrangement are highly similar even if one is a crisp photograph of carved stone and the other a blurred snapshot of painted clay. Two surfaces of the same material photographed the same way are NOT similar if they show different things.
THE STANDARD. Ask whether the correspondence is of the kind that would suggest the two surfaces share an iconographic tradition, as opposed to what two unrelated traditions could easily produce independently. Any tradition might depict a bird, a circle, a standing figure or a band of pattern; few would independently arrive at the same distinctive motif in the same relationship to the same other elements. Score arbitrary, specific, conventional correspondences high; score universal or obvious ones low. That both show "some animals" or "some pattern" counts for little; that both show the same distinctive motif in the same relationship counts for a lot. Photographs may show an object from different angles or only in part; judge the depicted scene, not the framing."""

PROMPT = CONTENT + """

You are comparing two decorated surfaces, A (left) and B (right), for a study of similarity of depicted content. You know nothing about where either is from; do not guess or name a culture, site or period. Judge only what is depicted, as a careful, sceptical iconographer would.

Rate:
- shared_elements: list the kinds of things depicted in BOTH (e.g. "bird in profile", "circle or disc", "horizontal band of pattern", "standing human figure", "snake", "handled object"). Empty list if nothing is shared.
- element_similarity (0-3): how specific the shared depicted elements are. 0 = nothing depicted in common; 1 = only generic things (some animal, some pattern); 2 = the same specific kinds of things (e.g. a bird in profile, a disc, a snake); 3 = the same specific kinds of things in the same specific forms (same posture, same attributes, same combinations).
- relationship_similarity (0-3): how alike the relationships between depicted elements are (what holds, touches, faces, sits on, flanks or encloses what). 0 = none in common; 3 = the same specific relationships.
- arrangement_similarity (0-3): 0 = no correspondence in how depicted elements are placed; 3 = the same kinds of elements occupy the same relative positions in the same order.
- style_similarity (0-3): similarity in the manner of depiction, NOT the medium or photograph: schematic vs naturalistic, proportions, outline and infill conventions, how details are rendered. 0 = utterly different conventions; 3 = could follow the same conventions.
- gestalt_similarity (0-3): your immediate impression of the two scenes as wholes, before analysis, ignoring medium and photography.
- overall (0-10): 0 = nothing depicted in common; 3 = a couple of generic elements in common; 5 = several shared elements, loosely comparable arrangement; 7 = a specific iconographic scheme shared; 10 = the same scene.
- justification: two sentences on what drives your score, naming the most specific correspondence in depicted content and the biggest difference in depicted content."""

def load_corpus():
    corpus = json.load(open(os.path.join(S3, "corpus.json")))["images"]
    sel = set(json.load(open(os.path.join(S3, "selected.json"))))
    ims = {im["id"]: im for im in corpus if im["id"] in sel}
    targets = json.load(open(os.path.join(S3, "targets.json")))
    return ims, targets

def composite(pa, pb, h=640):
    a = Image.open(pa).convert("RGB"); b = Image.open(pb).convert("RGB")
    a.thumbnail((h, h)); b.thumbnail((h, h))
    W = a.width + b.width + 60; im = Image.new("RGB", (W, h + 60), (246, 241, 232))
    im.paste(a, (20, 40)); im.paste(b, (a.width + 40, 40))
    from PIL import ImageDraw, ImageFont
    d = ImageDraw.Draw(im); f = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
    d.text((20, 8), "A", fill=(32, 27, 18), font=f); d.text((a.width + 40, 8), "B", fill=(32, 27, 18), font=f)
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=85)
    return {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}

def judge(ims, a, b, model, setname):
    key = hashlib.md5(f"{a}|{b}|{model}".encode()).hexdigest()[:16]
    out = os.path.join(JD, key + ".json")
    if os.path.exists(out): return "cached"
    for attempt in range(4):
        try:
            block = composite(os.path.join(ROOT, ims[a]["path"]), os.path.join(ROOT, ims[b]["path"]))
            if model == "gpt":
                d, usage = judge_openai(block, PROMPT)
                d.update(a=a, b=b, model=model, set=setname, usage=usage); json.dump(d, open(out, "w"), indent=1); return "ok"
            r = client.messages.parse(model=MODELS[model], max_tokens=3000, output_format=Judgment,
                                      messages=[{"role": "user", "content": [block, {"type": "text", "text": PROMPT}]}])
            if r.parsed_output is None:
                json.dump(dict(a=a, b=b, model=model, set=setname, error=r.stop_reason), open(out, "w")); return "empty"
            d = r.parsed_output.model_dump(); d.update(a=a, b=b, model=model, set=setname, usage=[r.usage.input_tokens, r.usage.output_tokens])
            json.dump(d, open(out, "w"), indent=1); return "ok"
        except anthropic.RateLimitError:
            time.sleep(10 * (attempt + 1))
        except Exception as e:
            if attempt == 3:
                json.dump(dict(a=a, b=b, model=model, set=setname, error=str(e)[:200]), open(out, "w")); return "error"
            time.sleep(3)
    return "error"

def plan(ims, targets):
    rng = random.Random(2026); ids = sorted(ims); grp = {i: ims[i]["group"] for i in ids}
    p43, hoa = targets["pillar43"], targets["hoa_back"]
    sets = {}
    hoa2 = targets.get("hoa_back2"); p43alt = targets.get("pillar43_alt"); p43top = targets.get("pillar43_top")
    sets["target"] = []
    for m in ("opus", "sonnet", "gpt"):
        for pp in [p43] + ([p43alt] if p43alt else []) + ([p43top] if p43top else []):
            for hh in [hoa] + ([hoa2] if hoa2 else []):
                sets["target"] += [(pp, hh, m), (hh, pp, m)]
    excl = {p43, hoa, hoa2, p43alt, p43top} - {None}
    sets["search_p43"] = [((p43, i) if rng.random() < .5 else (i, p43)) + ("opus",) for i in ids if i not in excl]
    sets["search_p43_gpt"] = [(a, b, "gpt") for a, b, _ in sets["search_p43"]]
    sets["search_hoa"] = [((hoa, i) if rng.random() < .5 else (i, hoa)) + ("opus",) for i in ids if i not in excl]
    sets["search_hoa_gpt"] = [(a, b, "gpt") for a, b, _ in sets["search_hoa"]]
    pool = [i for i in ids if i not in excl]
    null = []
    while len(null) < 1500:
        a, b = rng.sample(pool, 2)
        if grp[a] != grp[b]: null.append((a, b, "opus"))
    sets["null"] = null
    same = []
    while len(same) < 200:
        a, b = rng.sample(ids, 2)
        if grp[a] == grp[b]: same.append((a, b, "opus"))
    sets["same"] = same
    A = [i for i in ids if grp[i] == "assyria"]; P = [i for i in ids if grp[i] == "persepolis"]
    sets["poscontrol"] = [((rng.choice(A), rng.choice(P)) if rng.random() < .5 else (rng.choice(P), rng.choice(A))) + ("opus",) for _ in range(150)]
    sets["reliability"] = [(a, b, "sonnet") for a, b, _ in null[:200]] + [(a, b, "gpt") for a, b, _ in null[:200]]
    sets["null_gpt"] = [(a, b, "gpt") for a, b, _ in null[200:700]]
    json.dump(sets, open(os.path.join(S3, "judge_plan.json"), "w"), indent=0)
    return sets

def main():
    ims, targets = load_corpus()
    if sys.argv[1] == "plan":
        sets = plan(ims, targets); print({k: len(v) for k, v in sets.items()}); return
    sets = json.load(open(os.path.join(S3, "judge_plan.json")))
    which = sys.argv[2]; names = list(sets) if which == "all" else [which]
    for name in names:
        jobs = sets[name]; counts = {}
        with ThreadPoolExecutor(max_workers=6) as ex:
            futs = [ex.submit(judge, ims, a, b, m, name) for a, b, m in jobs]
            for k, f in enumerate(as_completed(futs)):
                st = f.result(); counts[st] = counts.get(st, 0) + 1
                if k % 100 == 0: print(name, k, counts, flush=True)
        print(name, "done", counts, flush=True)

if __name__ == "__main__":
    main()
