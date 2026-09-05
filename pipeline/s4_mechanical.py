"""Study 4, knowledge-free instruments: cosine similarity of the de-identified texts under a small
local sentence-embedding model (all-MiniLM-L6-v2) and TF-IDF. Output: data/s4/mechanical.json"""
import os, json, re, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S4 = os.path.join(ROOT, "data", "s4"); BL = os.path.join(S4, "blind")
def main():
    B = {}
    for f in os.listdir(BL):
        if f.endswith(".json"): d = json.load(open(os.path.join(BL, f))); B[d["key"]] = d
    keys = sorted(B); texts = [B[k]["blind"] for k in keys]; idx = {k: i for i, k in enumerate(keys)}
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer("all-MiniLM-L6-v2"); E = m.encode(texts, normalize_embeddings=True); SE = E @ E.T
    from sklearn.feature_extraction.text import TfidfVectorizer
    X = TfidfVectorizer(stop_words="english", min_df=2).fit_transform(texts); ST = (X @ X.T).toarray()
    def rank(S, a, b):
        i, j = idx[a], idx[b]; s = S[i].copy(); s[i] = -9; return int((s > s[j]).sum()) + 1
    plan = json.load(open(os.path.join(S4, "lineup_plan.json")))
    pairs = {}
    for t in plan:
        if t["set"] == "random": continue
        a, b = t["pair"].split(" | ")
        if (a, b) in pairs or (b, a) in pairs or a not in idx or b not in idx: continue
        pairs[(a, b)] = dict(set=t["set"], pair=t["pair"], emb_rank=rank(SE, a, b), emb_rank_rev=rank(SE, b, a), tfidf_rank=rank(ST, a, b), tfidf_rank_rev=rank(ST, b, a), emb_cos=float(SE[idx[a], idx[b]]), tfidf_cos=float(ST[idx[a], idx[b]]))
    rnd = []
    for t in [t for t in plan if t["set"] == "random"]:
        a, b = t["target"], t["planted"]
        if a in idx and b in idx: rnd.append(dict(set="random", pair=t["pair"], emb_rank=rank(SE, a, b), emb_rank_rev=rank(SE, b, a), tfidf_rank=rank(ST, a, b), tfidf_rank_rev=rank(ST, b, a), emb_cos=float(SE[idx[a], idx[b]]), tfidf_cos=float(ST[idx[a], idx[b]])))
    allp = list(pairs.values()) + rnd
    summary = {}
    for st in ("hancock", "positive", "related", "random"):
        rows = [p for p in allp if p["set"] == st]
        if rows: summary[st] = dict(n=len(rows), emb_median=float(np.median([x for p in rows for x in (p["emb_rank"], p["emb_rank_rev"])])), tfidf_median=float(np.median([x for p in rows for x in (p["tfidf_rank"], p["tfidf_rank_rev"])])), emb_cos_mean=float(np.mean([p["emb_cos"] for p in rows])))
    # nearest neighbours of the civiliser targets under the embedding
    nn = {}
    for k in ("Viracocha", "Quetzalcoatl", "Oannes", "Osiris", "Bochica", "Gilgamesh flood myth", "Gautama Buddha", "Ramayana"):
        if k in idx:
            s = SE[idx[k]].copy(); s[idx[k]] = -9
            for j, kk in enumerate(keys):
                if B[kk]["url"] == B[k]["url"] and kk != k: s[j] = -9   # same article under two keys (Oannes / Apkallu)
            nn[k] = [dict(key=keys[j], title=B[keys[j]]["title"], region=B[keys[j]]["region"], cos=float(s[j])) for j in np.argsort(-s)[:5]]
    out = dict(n_corpus=len(keys), pairs=list(pairs.values()) + rnd, summary=summary, nn=nn)
    json.dump(out, open(os.path.join(S4, "mechanical.json"), "w"), indent=1)
    print(json.dumps(summary, indent=1)); print({k: [(x["title"], round(x["cos"], 2)) for x in v[:3]] for k, v in nn.items()})
if __name__ == "__main__": main()
