"""Analysis of the direct pairwise judgments (pilot B), three judges.

Judges: opus (Claude Opus 5), sonnet (Claude Sonnet 5), gpt (GPT-5.5). Opus is the
primary judge for the null and the searches; GPT-5.5 repeats the Pillar 43 and moai
searches and 500 null pairs independently; Sonnet and GPT-5.5 re-judge 200 null pairs
for reliability.

Output: data/s3/results_judge.json
"""
import os, json, math
import numpy as np
from scipy.stats import spearmanr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S3 = os.path.join(ROOT, "data", "s3"); JD = os.path.join(S3, "judgments")

def dist(rows):
    s = np.array([r["score"] for r in rows])
    return dict(n=int(len(s)), mean=float(s.mean()), sd=float(s.std()), quantiles={str(q): float(np.quantile(s, q)) for q in (0.5, 0.75, 0.9, 0.95, 0.99)}, hist=np.bincount(s, minlength=11).tolist()) if len(s) else {}

def main():
    corpus = {im["id"]: im for im in json.load(open(os.path.join(S3, "corpus.json")))["images"]}
    T = json.load(open(os.path.join(S3, "targets.json")))
    J = [json.load(open(os.path.join(JD, f))) for f in os.listdir(JD) if f.endswith(".json")]
    J = [j for j in J if "error" not in j and "overall" in j]
    for j in J:
        j["score"] = int(j["overall"]); j["sub"] = int(j["element_similarity"]) + int(j["relationship_similarity"]) + int(j["arrangement_similarity"]) + int(j["style_similarity"]) + int(j["gestalt_similarity"])
    by = {}
    for j in J: by.setdefault(j["set"], []).append(j)
    res = dict(n_judgments=len(J), sets={k: len(v) for k, v in by.items()})
    null_opus = by.get("null", []); null_gpt = by.get("null_gpt", [])
    res["null"] = dist(null_opus); res["null_gpt"] = dist(null_gpt); res["same"] = dist(by.get("same", [])); res["poscontrol"] = dist(by.get("poscontrol", []))
    # target: every judgment, grouped by judge and by image pair
    tg = by.get("target", []) + by.get("target_iso", []); P43 = {T["pillar43"]: "full", T.get("pillar43_alt"): "full_above", T.get("pillar43_top"): "top_only", T.get("pillar43_iso"): "iso"}; HOA = {T["hoa_back"]: "back_full", T.get("hoa_back2"): "back_close", T.get("hoa_back_iso"): "iso"}
    OT = json.load(open(os.path.join(S3, "objtype.json"))) if os.path.exists(os.path.join(S3, "objtype.json")) else {}
    MONO = {i for i, d in OT.items() if d.get("object_type") in ("freestanding_monolith", "statue")}
    rows = []
    for r in tg:
        p = r["a"] if r["a"] in P43 else r["b"]; h = r["b"] if r["a"] in P43 else r["a"]
        rows.append(dict(judge=r["model"], p43=P43.get(p), hoa=HOA.get(h), order="p43_left" if r["a"] == p else "p43_right", score=r["score"], sub=r["sub"], elements=r["shared_elements"], why=r["justification"]))
    res["target_rows"] = rows
    def agg(sel):
        s = [r["score"] for r in rows if sel(r)]; return dict(n=len(s), mean=float(np.mean(s)) if s else None, min=min(s) if s else None, max=max(s) if s else None)
    res["target"] = dict(all=agg(lambda r: True), full_pillar=agg(lambda r: r["p43"] in ("full", "full_above")), top_only=agg(lambda r: r["p43"] == "top_only"),
                         by_judge={m: agg(lambda r, m=m: r["judge"] == m and r["p43"] in ("full", "full_above")) for m in ("opus", "sonnet", "gpt")},
                         by_pair={f"{p}|{h}": agg(lambda r, p=p, h=h: r["p43"] == p and r["hoa"] == h) for p in ("full", "full_above", "top_only", "iso") for h in ("back_full", "back_close", "iso")},
                         iso_by_judge={m: agg(lambda r, m=m: r["judge"] == m and r["p43"] == "iso") for m in ("opus", "sonnet", "gpt")})
    # percentiles of the full-pillar target mean within each judge's null
    m_opus = res["target"]["by_judge"]["opus"]["mean"]; m_gpt = res["target"]["by_judge"]["gpt"]["mean"]
    if null_opus and m_opus is not None:
        s = np.array([r["score"] for r in null_opus]); res["target"]["opus_pct_null"] = float((s < m_opus).mean() * 100); res["target"]["opus_share_null_ge"] = float((s >= m_opus).mean())
        s2 = np.array([r["score"] for r in by.get("same", [])]); res["target"]["opus_pct_same"] = float((s2 < m_opus).mean() * 100) if len(s2) else None
        s3 = np.array([r["score"] for r in by.get("poscontrol", [])]); res["target"]["opus_pct_pos"] = float((s3 < m_opus).mean() * 100) if len(s3) else None
    if null_gpt and m_gpt is not None:
        s = np.array([r["score"] for r in null_gpt]); res["target"]["gpt_pct_null"] = float((s < m_gpt).mean() * 100); res["target"]["gpt_share_null_ge"] = float((s >= m_gpt).mean())
    # related neighbours: pairs of traditions that may share by contact are not a fair null
    RELATED = {frozenset(x) for x in (("anatolia_ppn", "catalhoyuk"), ("assyria", "persepolis"), ("gotland", "tanum"))}
    def related(r): return frozenset((corpus[r["a"]]["group"], corpus[r["b"]]["group"])) in RELATED
    nd = [r for r in null_opus if not related(r)]; res["null_distant"] = dist(nd); res["null_related_pairs"] = dist([r for r in null_opus if related(r)])
    if nd and m_opus is not None:
        s = np.array([r["score"] for r in nd]); res["target"]["opus_pct_null_distant"] = float((s < m_opus).mean() * 100)
    # same-object pairs inside the same-tradition control (flagged by s3_sameobj.py)
    SO = json.load(open(os.path.join(S3, "sameobj.json"))) if os.path.exists(os.path.join(S3, "sameobj.json")) else {}
    def sameobj(a, b): v = SO.get(f"{a}|{b}", {}).get("verdict"); return v in ("same_object", "same_object_different_part")
    def unsure(a, b): return SO.get(f"{a}|{b}", {}).get("verdict") == "unsure"
    same_rows = by.get("same", []); res["same_diffobj"] = dist([r for r in same_rows if not sameobj(r["a"], r["b"]) and not unsure(r["a"], r["b"])]); res["same_sameobj"] = dist([r for r in same_rows if sameobj(r["a"], r["b"])])
    res["same_n_sameobj"] = int(sum(sameobj(r["a"], r["b"]) for r in same_rows)); res["same_n_unsure"] = int(sum(unsure(r["a"], r["b"]) for r in same_rows))
    if res["same_diffobj"] and m_opus is not None:
        s = np.array([r["score"] for r in same_rows if not sameobj(r["a"], r["b"]) and not unsure(r["a"], r["b"])]); res["target"]["opus_pct_same_diffobj"] = float((s < m_opus).mean() * 100)
    # resemblance-only: the sub-score sum (element+relationship+arrangement+style+gestalt, 0-15), target vs null
    if null_opus:
        ts = [r["sub"] for r in tg if r["model"] == "opus" and (r["a"] in (T["pillar43"], T.get("pillar43_alt")) or r["b"] in (T["pillar43"], T.get("pillar43_alt")))]
        if ts:
            tsub = float(np.mean(ts)); ns = np.array([r["sub"] for r in null_opus]); res["target"]["opus_sub_mean"] = tsub; res["target"]["opus_sub_pct_null"] = float((ns < tsub).mean() * 100); res["null_sub_mean"] = float(ns.mean())
    # object type: the null restricted to monolith x monolith pairs, and the target's place in it
    if MONO:
        nm = [r for r in null_opus if r["a"] in MONO and r["b"] in MONO]; res["null_mono"] = dist(nm)
        if nm and m_opus is not None:
            s = np.array([r["score"] for r in nm]); res["target"]["opus_pct_null_mono"] = float((s < m_opus).mean() * 100); res["target"]["opus_share_null_mono_ge"] = float((s >= m_opus).mean())
        res["objtype_counts"] = {}
        for i, d in OT.items():
            if i in corpus: g = corpus[i]["group"]; t = d.get("object_type", "other"); res["objtype_counts"].setdefault(g, {}); res["objtype_counts"][g][t] = res["objtype_counts"][g].get(t, 0) + 1
    # searches
    def top(setname, tid, k=12):
        rr = by.get(setname, []); out = []
        for r in rr:
            other = r["b"] if r["a"] == tid else r["a"]
            out.append(dict(id=other, group=corpus[other]["group"], score=r["score"], sub=r["sub"], elements=r["shared_elements"], why=r["justification"]))
        out.sort(key=lambda x: (-x["score"], -x["sub"])); s = np.array([x["score"] for x in out])
        for x in out: x["objtype"] = OT.get(x["id"], {}).get("object_type")
        bt = {}
        for x in out: bt.setdefault(x["objtype"], []).append(x["score"])
        return dict(n=len(out), top=out[:k], top_foreign=[x for x in out if x["group"] not in ("anatolia_ppn", "rapa_nui")][:12], by_objtype={t: dict(n=len(v), mean=float(np.mean(v)), n_ge6=int(sum(1 for q in v if q >= 6))) for t, v in bt.items() if t}, top_foreign_mono=[x for x in out if x["group"] not in ("anatolia_ppn", "rapa_nui") and x["id"] in MONO][:12], mean=float(s.mean()) if len(s) else None, hist=np.bincount(s, minlength=11).tolist() if len(s) else [],
                    by_group={g: float(np.mean([x["score"] for x in out if x["group"] == g])) for g in sorted(set(x["group"] for x in out))},
                    n_ge={str(v): int((s >= v).sum()) for v in (5, 6, 7, 8)})
    for name, tid in (("search_p43", T["pillar43"]), ("search_p43_gpt", T["pillar43"]), ("search_hoa", T["hoa_back"]), ("search_hoa_gpt", T["hoa_back"])):
        if name in by: res[name] = top(name, tid)
    # where would the moai rank among P43's search matches (and vice versa), per judge
    for judge, sname in (("opus", "search_p43"), ("gpt", "search_p43_gpt")):
        if sname in res and res["target"]["by_pair"].get("full|back_full", {}).get("mean") is not None:
            tscore = np.mean([r["score"] for r in rows if r["judge"] == judge and r["p43"] == "full" and r["hoa"] == "back_full"]) if any(r["judge"] == judge and r["p43"] == "full" and r["hoa"] == "back_full" for r in rows) else None
            if tscore is not None:
                def other(r): return r["b"] if r["a"] == T["pillar43"] else r["a"]
                allsc = [r["score"] for r in by[sname]]; fsc = [r["score"] for r in by[sname] if corpus[other(r)]["group"] not in ("anatolia_ppn", "rapa_nui")]
                above = {}
                for r in by[sname]:
                    g = corpus[other(r)]["group"]
                    if g not in ("anatolia_ppn", "rapa_nui") and r["score"] > tscore: above[g] = above.get(g, 0) + 1
                res[f"rank_moai_in_p43_search_{judge}"] = dict(target=float(tscore), n_better_all=int(sum(1 for v in allsc if v > tscore)), n_all=len(allsc), n_better=int(sum(1 for v in fsc if v > tscore)), n_equal=int(sum(1 for v in fsc if v == tscore)), n=len(fsc), above_by_group=dict(sorted(above.items(), key=lambda kv: -kv[1])))
    # reliability vs opus on the same 200 null pairs
    nullmap = {(r["a"], r["b"]): r["score"] for r in null_opus}
    rel = {}
    for judge in ("sonnet", "gpt"):
        pairs = [(nullmap[(r["a"], r["b"])], r["score"]) for r in by.get("reliability", []) if r["model"] == judge and (r["a"], r["b"]) in nullmap]
        if len(pairs) > 5:
            x, y = zip(*pairs); rho = spearmanr(x, y)
            rel[judge] = dict(n=len(pairs), spearman=float(rho.correlation), p=float(rho.pvalue), exact=float(np.mean([a == b for a, b in pairs])), within_one=float(np.mean([abs(a - b) <= 1 for a, b in pairs])), mean_opus=float(np.mean(x)), mean_other=float(np.mean(y)))
    # opus vs gpt on the P43 search (same pairs)
    if "search_p43" in by and "search_p43_gpt" in by:
        mo = {(r["a"], r["b"]): r["score"] for r in by["search_p43"]}; pairs = [(mo[(r["a"], r["b"])], r["score"]) for r in by["search_p43_gpt"] if (r["a"], r["b"]) in mo]
        if len(pairs) > 5:
            x, y = zip(*pairs); rho = spearmanr(x, y); rel["gpt_on_p43_search"] = dict(n=len(pairs), spearman=float(rho.correlation), within_one=float(np.mean([abs(a - b) <= 1 for a, b in pairs])))
    res["reliability"] = rel
    json.dump(res, open(os.path.join(S3, "results_judge.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("search") and k != "target_rows"}, indent=1)[:5000])
    for k in ("search_p43", "search_p43_gpt", "search_hoa", "search_hoa_gpt"):
        if k in res: print(k, "mean", round(res[k]["mean"], 2), "n>=6:", res[k]["n_ge"]["6"], "by group", {g: round(v, 2) for g, v in res[k]["by_group"].items()}); print("   top:", [(x["id"], x["score"]) for x in res[k]["top"][:8]])

if __name__ == "__main__":
    main()
