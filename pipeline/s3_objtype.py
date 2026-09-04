"""Study 3: classify every selected panel by OBJECT TYPE (blind, Sonnet 5), so that
lineups and nulls can be matched on it. Output: data/s3/objtype.json"""
import os, sys, json, io, base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Literal
from pydantic import BaseModel
import anthropic
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S3 = os.path.join(ROOT, "data", "s3"); OUT = os.path.join(S3, "objtype.json")
client = anthropic.Anthropic()

class ObjType(BaseModel):
    object_type: Literal["freestanding_monolith", "statue", "wall_or_architectural_relief", "rock_surface", "portable_object", "drawing_or_plan", "other"]
    object_is_figure: bool
    whole_object_visible: bool
    note: str

PROMPT = """Classify the OBJECT shown in this photograph (not the scene carved or painted on it). Do not guess or name a culture, site or period.
- object_type: freestanding_monolith = a free-standing pillar, stela or slab set upright (or once upright), carved or painted on its faces; statue = a sculpture in the round of a figure or creature; wall_or_architectural_relief = relief or painting on a wall, door jamb, staircase, lintel or other built surface; rock_surface = natural rock outcrop, cliff or boulder; portable_object = a vessel, plaque, tablet, seal, ornament or other object that can be carried; drawing_or_plan = a drawing, tracing, rubbing or plan rather than a photograph of an object; other.
- object_is_figure: true if the object as a whole is shaped as a body or figure (a statue, or a pillar with arms/face/belt that makes the stone itself a body), false if it is a panel that carries pictures.
- whole_object_visible: true if the photograph shows the entire object, false if it shows a detail or part.
- note: one short sentence."""

def classify(im):
    p = os.path.join(ROOT, im["path"]); img = Image.open(p).convert("RGB"); img.thumbnail((900, 900))
    buf = io.BytesIO(); img.save(buf, "JPEG", quality=85); b64 = base64.b64encode(buf.getvalue()).decode()
    r = client.messages.parse(model="claude-sonnet-5", max_tokens=1500, output_format=ObjType,
                              messages=[{"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": b64}}, {"type": "text", "text": PROMPT}]}])
    return im["id"], (r.parsed_output.model_dump() if r.parsed_output else {"error": r.stop_reason})

def main():
    corpus = json.load(open(os.path.join(S3, "corpus.json")))["images"]; sel = set(json.load(open(os.path.join(S3, "selected.json"))))
    ims = [im for im in corpus if im["id"] in sel]
    done = json.load(open(OUT)) if os.path.exists(OUT) else {}
    todo = [im for im in ims if im["id"] not in done]
    with ThreadPoolExecutor(max_workers=4) as ex:
        for k, f in enumerate(as_completed([ex.submit(classify, im) for im in todo])):
            try: i, d = f.result(); done[i] = d
            except Exception as e: print("err", e)
            if k % 50 == 0: json.dump(done, open(OUT, "w"), indent=1); print(k, flush=True)
    json.dump(done, open(OUT, "w"), indent=1)
    import collections; print(collections.Counter(d.get("object_type") for d in done.values()))
    print("figure objects:", sum(1 for d in done.values() if d.get("object_is_figure")))

if __name__ == "__main__":
    main()
