"""Study 3: blind triage and blind composition coding of every corpus image.

Triage (Sonnet 5): is this a single decorated surface that can be coded?
Coding (Opus 5 and Sonnet 5 independently): the pre-registered feature schema.
The models receive ONLY the image and the instructions below: no file name,
no category, no caption, no site. Results are cached per image and coder.

usage: python s3_code.py triage | code opus | code sonnet
"""
import os, sys, json, io, base64, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Literal, Optional
from pydantic import BaseModel
import anthropic
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S3 = os.path.join(ROOT, "data", "s3")
MODELS = {"opus": "claude-opus-5", "sonnet": "claude-sonnet-5", "triage": "claude-sonnet-5"}
client = anthropic.Anthropic()

def image_block(path, max_px=1024):
    im = Image.open(path).convert("RGB"); im.thumbnail((max_px, max_px))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=85)
    return {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(buf.getvalue()).decode()}}

class Triage(BaseModel):
    usable: bool
    reason: str
    medium: Literal["relief", "painting", "petroglyph", "incised", "statue_surface", "object_surface", "drawing_or_photo_of_carving", "unclear", "not_applicable"]
    is_replica_or_drawing: bool
    single_object: bool

TRIAGE_PROMPT = """You are triaging photographs for a study of the composition of carved and painted panels.
Answer only from what is visible. Mark usable=true only if the image shows ONE decorated surface (a relief, petroglyph, incised or pecked carving, painting, or the carved surface of a statue or object) whose figures or designs are discernible well enough to say what classes of things are depicted and where they sit on the surface.
Mark usable=false for: site or landscape views, architecture without discernible figures, maps, plans, text pages, book scans without images, museum rooms, plain undecorated statues or blocks, multiple separate objects in one frame, extreme close-ups of a fragment with no readable composition, or images too blurred or dark to read.
A freestanding statue, statuette or figurine that simply IS a figure is NOT usable, unless its surface carries separate carved or painted imagery (for example figures carved on the back or body of a statue); in that case code the surface imagery only.
A faithful drawing, tracing or historical photograph of a decorated surface counts as usable (set is_replica_or_drawing=true)."""

class Element(BaseModel):
    present: bool
    position: Literal["top", "middle", "bottom", "none"]
    count: Literal["0", "1", "2", "3+"]

class Elements(BaseModel):
    bird: Element
    human: Element
    bird_human_hybrid: Element
    other_hybrid: Element
    quadruped: Element
    reptile_or_snake: Element
    fish: Element
    insect_or_arachnid: Element
    disc_or_circle: Element
    container_or_bag: Element
    weapon_or_staff: Element
    plant_or_tree: Element
    geometric_band: Element
    text_or_glyphs: Element

class Code(BaseModel):
    registers: Literal["1", "2", "3+"]
    elements: Elements
    facing_pair: bool
    bilateral_symmetry: bool
    dominant_figure: Literal["bird", "human", "bird_human_hybrid", "other_hybrid", "quadruped", "reptile_or_snake", "fish", "insect_or_arachnid", "disc_or_circle", "container_or_bag", "weapon_or_staff", "plant_or_tree", "geometric_band", "text_or_glyphs", "none"]
    headless_human: bool
    bird_posture: Literal["profile", "spread_wings", "frontal", "mixed", "none"]
    hybrid_type: Literal["bird_headed_human", "bird_with_human_limbs", "human_in_bird_costume", "other", "none"]
    medium: Literal["relief", "painting", "petroglyph", "incised", "statue_surface", "unclear"]
    confidence: Literal["1", "2", "3", "4", "5"]
    notes: str

CODE_PROMPT = """You are coding the COMPOSITION of one decorated surface for a comparative study. You know nothing about where it is from; do not guess or mention a culture, site, date or name. Code only what is visible.

Definitions:
- registers: how many horizontal bands the imagery is organised into (1 = no clear banding).
- For each element class, say whether it is present, how many instances ("1", "2", "3+"), and the vertical position of the TOPMOST instance: top / middle / bottom third of the decorated area. Use position "none" and count "0" when absent.
  bird = any bird; human = a human figure without animal features; bird_human_hybrid = a figure combining human and bird features (bird head on a human body, human with wings or beak, a person in a bird costume); other_hybrid = other human-animal combinations; quadruped = four-legged mammal; reptile_or_snake; fish; insect_or_arachnid (scorpion, spider, insect); disc_or_circle = a plain circle, disc, ring or sphere as an object (not an eye); container_or_bag = a bucket, bag, basket, vessel or any handled container-like object; weapon_or_staff = weapon, staff, tool, sceptre; plant_or_tree; geometric_band = a band or field of repeated abstract pattern (zigzags, chevrons, lattice, spirals); text_or_glyphs = script or glyph blocks.
- facing_pair: two figures of the same class turned toward each other. bilateral_symmetry: the whole composition is roughly mirror-symmetric.
- dominant_figure: the class of the single largest figure. headless_human: a human figure clearly shown without a head.
- bird_posture: the posture of the most prominent bird (profile, spread wings, frontal, mixed); "none" if no bird.
- hybrid_type: the kind of bird-human hybrid if any.
- medium: relief / painting / petroglyph (pecked) / incised (fine lines) / statue_surface / unclear.
- confidence: 1 (guessing) to 5 (certain). notes: one sentence on what you see, no identification."""

def one(kind, coder, im):
    outdir = os.path.join(S3, "triage" if kind == "triage" else os.path.join("codes", coder)); os.makedirs(outdir, exist_ok=True)
    out = os.path.join(outdir, im["id"] + ".json")
    if os.path.exists(out): return im["id"], "cached"
    model = MODELS["triage" if kind == "triage" else coder]
    schema = Triage if kind == "triage" else Code
    prompt = TRIAGE_PROMPT if kind == "triage" else CODE_PROMPT
    for attempt in range(4):
        try:
            r = client.messages.parse(model=model, max_tokens=4000, output_format=schema,
                                      messages=[{"role": "user", "content": [image_block(os.path.join(ROOT, im["path"])), {"type": "text", "text": prompt}]}])
            if r.stop_reason == "refusal" or r.parsed_output is None:
                json.dump({"error": "refusal_or_empty", "stop_reason": r.stop_reason}, open(out, "w")); return im["id"], "refused"
            d = r.parsed_output.model_dump(); d["_model"] = model; d["_usage"] = [r.usage.input_tokens, r.usage.output_tokens]
            json.dump(d, open(out, "w"), indent=1); return im["id"], "ok"
        except anthropic.RateLimitError:
            time.sleep(10 * (attempt + 1))
        except Exception as e:
            if attempt == 3:
                json.dump({"error": str(e)[:300]}, open(out, "w")); return im["id"], "error"
            time.sleep(3)
    return im["id"], "error"

def main():
    kind = sys.argv[1]; coder = sys.argv[2] if len(sys.argv) > 2 else "triage"
    corpus = json.load(open(os.path.join(S3, "corpus.json")))["images"]
    if kind == "code":
        tri = {f[:-5]: json.load(open(os.path.join(S3, "triage", f))) for f in os.listdir(os.path.join(S3, "triage")) if f.endswith(".json")}
        corpus = [im for im in corpus if tri.get(im["id"], {}).get("usable")]
        selp = os.path.join(S3, "selected.json")   # pre-registered cap: up to 60 usable images per group, seeded, targets forced in
        if os.path.exists(selp):
            sel = set(json.load(open(selp))); corpus = [im for im in corpus if im["id"] in sel]
    print(kind, coder, len(corpus), "images", flush=True)
    counts = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(one, kind, coder, im) for im in corpus]
        for k, f in enumerate(as_completed(futs)):
            _, st = f.result(); counts[st] = counts.get(st, 0) + 1
            if k % 25 == 0: print(k, counts, flush=True)
    print("done", counts)

if __name__ == "__main__":
    main()
