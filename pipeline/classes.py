"""Define the three motif classes by explicit keyword rules over the English
motif names and descriptions, BEFORE looking at where they occur.

  BIRD_PEOPLE   humans that are, become, marry or dress as birds
  COSMIC_SERPENT serpents/snakes of cosmic scale: sky, rainbow, lightning, earth-holder, world
  WORLD_CENTRE  the world's axis, tree, pillar, supports, navel, hole/door in the sky

Every motif matched by a rule is listed in data/classes.json with the rule that
matched it. Manual exclusions (obvious false hits of the keyword rule) are
recorded there too, with a one-line reason, so the choice is auditable.
"""
import os, re, json
from load import load

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RULES = {
    "bird_people": [
        r"(turn|transform|become|change)\w*\s+(into\s+)?(a\s+)?(bird|swan|eagle|vulture|crow|raven|owl|hawk|duck|goose|geese|heron|crane|condor)",
        r"(bird|swan|eagle|vulture|buzzard|condor|crow|raven|owl|hawk|goose|duck)[\s-]*(wife|husband|woman|man|maiden|lover|paramour|spouse|people|person|mother|father)",
        r"(wife|husband|woman|man|maiden|lover|paramour|spouse|people|person)\s+(is|are|was|were)?\s*(a\s+)?(bird|swan|eagle|vulture|buzzard|condor|crow|raven|owl|hawk)",
        r"feather(s|ed)?\s+(dress|garment|cloak|coat|costume|skin|clothes)|bird[\s-]*(skin|costume|dress|garment)|put(s|ting)? on (the )?feathers",
        r"thunderbird|sun-bird|bird[\s-]*man\b|bird[\s-]*headed|winged (man|woman|people|person)",
        r"fly (away|off|up) as (a )?bird|flies (away|off|up) as (a )?bird|wings (grow|are given)",
    ],
    "cosmic_serpent": [
        r"(rainbow|horned|cloud|lightning|celestial|sky|cosmic|chthonic|world|feathered|plumed|winged|giant)[\s-]*(serpent|snake|dragon)",
        r"(serpent|snake|dragon)\s+(pushes|holds|supports|carries|surrounds|encircles|girds)\s+(the\s+)?(sky|earth|world)",
        r"(earth|world|milky way) is a (serpent|snake|reptile)",
        r"(serpent|snake)[\s-]*(of the )?(rainbow|sky|earth|underworld|water|lake|sea)\b",
        r"snake turns into dragon|snake.?s crown|snake bridge",
    ],
    "world_centre": [
        r"world[\s-]*(axis|tree|pillar|column|mountain|navel|centre|center)|axis mundi|primeval tree|cosmic tree",
        r"support(s)? of the (world|earth|sky)|earth[\s-]*holder|holds? (up )?the (earth|sky|world)|atlas",
        r"(hole|door|opening|window) (in|of) the sky|sky door|sky hole|polaris",
        r"navel|umbilic|centre of the (world|earth)|center of the (world|earth)|middle of the (world|earth)",
    ],
}

EXCLUDE = {
    # code: reason (keyword rule fired on incidental wording)
    "b60": "offended children abandon parents: transformation is incidental and not necessarily into birds",
    "e15": "ducks and canoes: people learn from birds; no bird-person",
    "i86": "hairs into animals: creator makes birds, no bird-person",
    "k10f": "nestlings turn into eagles: birds into birds",
    "k11a": "feathers turn into birds: birds into birds",
    "i13c": "snake's crown: treasure-guarding snake, not cosmic scale",
    "i24": "snake bridge: a snake as a rope over a river, not cosmic scale",
    "i76a": "snake turns into dragon: no cosmic role stated",
    "b42s": "hit with a projectile: Polaris as a struck animal, not an axis",
    "i72": "stars are people: rule fired on 'Polaris' in a parenthesis",
    "i85a": "horses around Polaris: circumpolar animals, not an axis",
    "i85b": "Polaris is a man: personification, not an axis",
    "i68": "opening of the sky: calendrical wish-granting, not a centre",
}

def classify(motifs):
    out = {k: [] for k in RULES}
    for m in motifs:
        text = f"{m['name']}. {m['description']}"
        for cls, rules in RULES.items():
            for r in rules:
                if re.search(r, text, re.I):
                    if m["code"] in EXCLUDE:
                        out[cls].append(dict(code=m["code"], name=m["name"], rule=r, excluded=EXCLUDE[m["code"]]))
                    else:
                        out[cls].append(dict(code=m["code"], name=m["name"], rule=r))
                    break
    return out

if __name__ == "__main__":
    d = load()
    cl = classify(d["motifs"])
    json.dump(cl, open(os.path.join(ROOT, "data", "classes.json"), "w"), indent=1)
    for k, v in cl.items():
        keep = [x for x in v if "excluded" not in x]
        print(f"\n== {k}: {len(keep)} motifs ({len(v) - len(keep)} excluded)")
        for x in v:
            print(f"  {x['code']:8s} {x['name'][:60]:60s} {'EXCLUDED: ' + x['excluded'] if 'excluded' in x else ''}")
