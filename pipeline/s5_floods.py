"""Study 5: the raven and the dove. Code every flood story in Mark Isaak's compendium
(talkorigins.org/faqs/flood-myths.html, 263 summaries with sources) for a fixed list of
details, blind to region, then ask which details cluster by region and language family and
which track the Biblical account and its transmission.

usage: python s5_floods.py code | analyse
"""
import os, sys, json, re, html
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Literal, List
from pydantic import BaseModel
import anthropic

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S5 = os.path.join(ROOT, "data", "s5"); RAW = os.path.join(S5, "raw"); CD = os.path.join(S5, "codes"); os.makedirs(CD, exist_ok=True)
client = anthropic.Anthropic()
T3 = Literal["yes", "no", "unclear"]

class FloodCode(BaseModel):
    # cause and warning
    flood_is_punishment: T3            # sent because of human wickedness, impiety or noise
    warned_by_deity: T3                # a god or spirit warns the hero in advance
    warned_by_animal: T3               # an animal warns
    # the hero and the vessel
    single_hero_family: T3             # one man/family survives (rather than many or a whole people)
    vessel_built: T3                   # a boat, ark, raft, chest, drum, gourd, box is deliberately built or prepared
    vessel_type: Literal["boat_or_ark", "raft", "chest_box_drum", "gourd_or_fruit", "tree_or_log", "none", "other"]
    refuge_mountain: T3                # survivors escape to or land on a mountain or high place
    refuge_tree: T3                    # survivors climb a tree
    animals_taken: T3                  # animals are deliberately brought aboard or saved
    seeds_taken: T3                    # seeds or plants are brought
    # during and after
    birds_sent_out: T3                 # a bird (raven, dove, other) is sent out to find land
    raven_or_dove_named: T3            # the bird is a raven or a dove
    animal_scout_other: T3             # another animal sent to look for land (rat, muskrat, etc.)
    earth_diver: T3                    # an animal dives to bring up earth to make new land
    duration_stated: T3                # duration of the flood stated in days/months/years
    forty_days: T3                     # the number forty appears
    sacrifice_after: T3                # sacrifice or offering after the flood
    rainbow_or_promise: T3             # rainbow or a promise not to flood again
    repopulation_from_objects: T3      # people re-made from stones, bones, seeds, clay etc.
    repopulation_by_incest: T3         # siblings or parent-child marry to repopulate
    survivors_marry_animal_or_spirit: T3
    god_or_hero_bearded_or_pale: T3    # any mention of a bearded, white or pale figure
    fire_or_other_catastrophe_too: T3  # a fire, darkness, cold or other catastrophe alongside the flood
    giants_or_previous_race: T3        # a previous race (giants etc.) destroyed
    mentions_bible_or_noah: T3         # the text itself mentions Noah, the Bible, missionaries, Christians, or Biblical influence
    told_as_local_river_or_sea: T3     # the flood is a specific local river, lake or sea rather than the whole world
    whole_world_flooded: T3
    survivors_count: Literal["one_or_couple", "family", "several_or_many", "whole_people", "unstated"]
    note: str

PROMPT = """You are coding a summary of a flood story for a comparative study. Read the text and answer each field from the TEXT ONLY, not from anything you know about the culture. Answer "yes" only if the text states or clearly implies the detail; "no" if the text tells enough of the story for the detail to have appeared and it does not; "unclear" if the summary is too short or vague to tell. Do not name or guess the culture. One sentence in note on anything unusual."""

def load_entries():
    E = json.load(open(os.path.join(RAW, "flood_entries_raw.json")))
    # language family/group from the companion page (nested lists: region > family > group<br/>names)
    lg = open(os.path.join(RAW, "flood-myths-lang.html"), encoding="utf-8", errors="replace").read()
    from html.parser import HTMLParser
    fam = {}
    class P(HTMLParser):
        def __init__(self): super().__init__(); self.stack = []; self.buf = ""; self.after_br = False; self.cur_names = ""
        def handle_starttag(self, tag, attrs):
            if tag == "li": self.stack.append(""); self.buf = ""; self.after_br = False
            if tag == "br" and self.stack: self.after_br = True; self.stack[-1] = self.buf.strip()
            if tag == "ul" and self.stack and not self.stack[-1]: self.stack[-1] = self.buf.strip()
        def handle_data(self, data):
            if not self.stack: return
            if self.after_br: self.cur_names += data
            else: self.buf += data
        def handle_endtag(self, tag):
            if tag == "li" and self.stack:
                group = self.stack[-1] or self.buf.strip(); names = self.cur_names
                if names.strip():
                    family = next((x for x in reversed(self.stack[:-1]) if x), None)
                    for n in re.split(r",", names):
                        n = re.sub(r"\s+", " ", html.unescape(n)).strip().rstrip("?")
                        if n: fam[n.lower()] = dict(family=family or group, group=group)
                self.stack.pop(); self.buf = ""; self.cur_names = ""; self.after_br = False
    P().feed(lg[lg.find("<ul>"):lg.find("Reader Paths")])
    for e in E:
        key = e["name"].lower(); hit = fam.get(key) or fam.get(key.split(" (")[0]) or fam.get(key.split(" (")[0].rstrip("?"))
        e["family"] = hit["family"] if hit else None; e["lang_group"] = hit["group"] if hit else None
        e["christian_terms"] = sorted(set(m.lower() for m in re.findall(r"\b(Noah|No[eé]h|Christ|Jesus|angel|archangel|Saint|Bible|Biblical|Jehovah|missionar\w*|priest|church|Adam|Eve|Genesis|Allah|Koran|Quran|Mohammed|Muhammad|Christian\w*)\b", e["text"], flags=re.I)))
        # first cited author + year from the references (compiler year, not collection year)
        e["cite_authors"] = [c.split(",")[0].strip() for c in e["cites"]]
    return E

def code(e):
    out = os.path.join(CD, e["id"] + ".json")
    if os.path.exists(out): return "cached"
    for attempt in range(3):
        try:
            r = client.messages.parse(model="claude-sonnet-5", max_tokens=2500, output_format=FloodCode, messages=[{"role": "user", "content": PROMPT + "\n\nTEXT:\n" + re.sub(r"\[[^\]]*\]", "", e["text"])}])
            d = r.parsed_output.model_dump() if r.parsed_output else None
            if d: d.update(id=e["id"], name=e["name"], region=e["region"], family=e.get("family")); json.dump(d, open(out, "w"), indent=1); return "ok"
        except Exception as ex:
            if attempt == 2: return "error:" + str(ex)[:80]
    return "error"

def main():
    E = load_entries()
    if sys.argv[1] == "code":
        counts = {}
        with ThreadPoolExecutor(max_workers=4) as ex:
            for f in as_completed([ex.submit(code, e) for e in E]): st = f.result(); counts[st[:5]] = counts.get(st[:5], 0) + 1
        print(counts)
    json.dump(E, open(os.path.join(S5, "entries.json"), "w"), indent=1)
    import collections; print("families:", collections.Counter(e["family"] for e in E).most_common(12))

if __name__ == "__main__":
    main()
