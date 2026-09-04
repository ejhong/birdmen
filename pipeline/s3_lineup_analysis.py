"""Analysis of the blind lineups (pilot C). Output: data/s3/results_lineup.json"""
import os, json, math
import numpy as np
from scipy.stats import binomtest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S3 = os.path.join(ROOT, "data", "s3"); LD = os.path.join(S3, "lineups")

def main():
    corpus = {im["id"]: im for im in json.load(open(os.path.join(S3, "corpus.json")))["images"]}
    L = [json.load(open(os.path.join(LD, f))) for f in os.listdir(LD) if f.endswith(".json")]
    L = [x for x in L if "planted_rank" in x]
    sets = sorted(set(x["set"] for x in L)); judges = ["opus", "gpt", "gemini", "sonnet", "grok"]
    res = dict(n=len(L), by_set={}, trials=[])
    for s in sets:
        res["by_set"][s] = {}
        for j in judges + ["all"]:
            rows = [x for x in L if x["set"] == s and (j == "all" or x["model"] == j)]
            if not rows: continue
            ranks = np.array([x["planted_rank"] for x in rows])
            n1 = int((ranks == 1).sum()); n3 = int((ranks <= 3).sum())
            res["by_set"][s][j] = dict(n=len(rows), mean_rank=float(ranks.mean()), sd=float(ranks.std()), rank1=n1, top3=n3, share_rank1=n1 / len(rows), share_top3=n3 / len(rows),
                                       p_rank1=float(binomtest(n1, len(rows), 0.1, alternative="greater").pvalue), p_top3=float(binomtest(n3, len(rows), 0.3, alternative="greater").pvalue),
                                       hist=np.bincount(ranks, minlength=11)[1:].tolist())
    for x in L:
        res["trials"].append(dict(set=x["set"], i=x["i"], model=x["model"], target=x["target"], planted=x["planted"], planted_rank=x["planted_rank"], ranking=x["ranking"], cands=x["cands"],
                                  top_id=x["cands"][x["ranking"][0] - 1], top_group=corpus[x["cands"][x["ranking"][0] - 1]]["group"], why_top=x.get("most_similar_reason", ""), why_last=x.get("least_similar_reason", "")))
    # which decoy groups beat the moai most often in the target sets
    for s in ("moai_among_random", "moai_close_among_random", "moai_iso_among_random", "moai_iso_among_monoliths", "p43_among_random", "p43_iso_among_monoliths", "hard"):
        rows = [x for x in L if x["set"] == s]
        beat = {}
        for x in rows:
            for pos in x["ranking"][:x["planted_rank"] - 1]:
                g = corpus[x["cands"][pos - 1]]["group"]; beat[g] = beat.get(g, 0) + 1
        if s in res["by_set"]: res["by_set"][s]["decoy_groups_ranked_above_planted"] = dict(sorted(beat.items(), key=lambda kv: -kv[1]))
    json.dump(res, open(os.path.join(S3, "results_lineup.json"), "w"), indent=1)
    for s in sets:
        print(s)
        for j, v in res["by_set"][s].items():
            if isinstance(v, dict) and "n" in v: print(f"   {j:7s} n={v['n']:3d} mean rank {v['mean_rank']:.2f}  rank1 {v['rank1']}/{v['n']} ({v['share_rank1']:.0%}, p={v['p_rank1']:.3f})  top3 {v['share_top3']:.0%}")

if __name__ == "__main__":
    main()
