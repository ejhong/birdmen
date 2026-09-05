"""Copy study 4 and 5 results into docs/data (NaN-safe) and write the overview card summaries."""
import os, json, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def clean(x):
    if isinstance(x, float): return None if (math.isnan(x) or math.isinf(x)) else x
    if isinstance(x, dict): return {k: clean(v) for k, v in x.items()}
    if isinstance(x, list): return [clean(v) for v in x]
    return x
for s in ("s4", "s5"):
    p = os.path.join(ROOT, "data", s, "results.json")
    if os.path.exists(p): json.dump(clean(json.load(open(p))), open(os.path.join(ROOT, "docs", "data", s + ".json"), "w"), allow_nan=False); print(s, "ok", os.path.getsize(os.path.join(ROOT, "docs", "data", s + ".json")) // 1024, "KB")
