"""Flag pairs that are two photographs of the SAME object (or of overlapping parts of it),
so that same-tradition controls can be reported with those pairs excluded.
Covers: pilot B 'same' pairs; lineup same_control / same_control_monoliths (target, planted).
Output: data/s3/sameobj.json {"a|b": {...}}"""
import os, json, io, base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Literal
from pydantic import BaseModel
import anthropic
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S3 = os.path.join(ROOT, "data", "s3"); OUT = os.path.join(S3, "sameobj.json")
client = anthropic.Anthropic()
class R(BaseModel):
    verdict: Literal["same_object", "same_object_different_part", "different_objects", "unsure"]
    note: str
PROMPT = "Two photographs, A (left) and B (right). Are they photographs of the SAME physical object (the same statue, pillar, stela, slab, wall or rock panel), possibly from different angles, distances or lighting, or showing different parts of it? Or are they different objects? Do not name a culture or site. Answer same_object, same_object_different_part, different_objects or unsure, with one sentence."
def comp(pa, pb, h=560):
    a = Image.open(pa).convert("RGB"); b = Image.open(pb).convert("RGB"); a.thumbnail((h, h)); b.thumbnail((h, h))
    im = Image.new("RGB", (a.width + b.width + 60, h + 20), (246, 241, 232)); im.paste(a, (20, 10)); im.paste(b, (a.width + 40, 10))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=85); return base64.b64encode(buf.getvalue()).decode()
def judge(ims, a, b):
    r = client.messages.parse(model="claude-sonnet-5", max_tokens=800, output_format=R, messages=[{"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": comp(os.path.join(ROOT, ims[a]["path"]), os.path.join(ROOT, ims[b]["path"]))}}, {"type": "text", "text": PROMPT}]}])
    d = r.parsed_output.model_dump() if r.parsed_output else {"verdict": "unsure", "note": "no parse"}; d.update(title_a=ims[a]["title"], title_b=ims[b]["title"]); return d
def main():
    ims = {im["id"]: im for im in json.load(open(os.path.join(S3, "corpus.json")))["images"]}
    pairs = set()
    for a, b, m in json.load(open(os.path.join(S3, "judge_plan.json")))["same"]: pairs.add((a, b))
    for t in json.load(open(os.path.join(S3, "lineup_plan.json"))):
        if t["set"].startswith("same_control"): pairs.add((t["target"], t["planted"]))
    done = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [p for p in pairs if f"{p[0]}|{p[1]}" not in done]; print("pairs", len(pairs), "todo", len(todo))
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(judge, ims, a, b): (a, b) for a, b in todo}
        for f in as_completed(futs):
            a, b = futs[f]
            try: done[f"{a}|{b}"] = f.result()
            except Exception as e: print("err", a, b, str(e)[:100])
    json.dump(done, open(OUT, "w"), indent=1)
    import collections; print(collections.Counter(v["verdict"] for v in done.values()))
if __name__ == "__main__": main()
