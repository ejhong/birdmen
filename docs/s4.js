(async function () {
  { const o = new URLSearchParams(location.search).get("off"); if (o) document.body.style.marginTop = (-parseInt(o, 10)) + "px"; }
  const R = await (await fetch("data/s4.json")).json();
  const el = (tag, attrs = {}, ...kids) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "class") e.className = v; else if (k === "html") e.innerHTML = v; else e.setAttribute(k, v); } for (const k of kids) if (k != null) e.append(k); return e; };
  const NS = "http://www.w3.org/2000/svg"; const sv = (tag, attrs = {}, text) => { const e = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); if (text != null) e.textContent = text; return e; };
  const svg = (w, h) => { const s = sv("svg", { viewBox: `0 0 ${w} ${h}`, width: "100%" }); s.style.maxWidth = w + "px"; s.style.display = "block"; return s; };
  const COL = { ink: "#201b12", soft: "#4c453a", faint: "#6e6556", rule: "#d9d0be", copper: "#92552e", moss: "#47705f", rust: "#8e4a38", slate: "#5d6672" };
  const pc = x => (x == null) ? "–" : (100 * x).toFixed(0) + "%", f2 = x => (x == null) ? "–" : Number(x).toFixed(2);
  const SN = { hancock: "The civilisers (lost-civilisation pairs)", positive: "Designated positive controls", related: "Designated related pairs", random: "Random pairs (base rate)" };
  const C = R.corpus, BS = R.by_set, BP = R.by_pair, LK = R.leak;
  const title = k => C[k] ? C[k].title : k;
  document.querySelectorAll("[data-v='n_corpus']").forEach(e => e.textContent = Object.keys(C).length); document.querySelectorAll("[data-v='n_lineups']").forEach(e => e.textContent = R.n);
  const g = s => BS[s] && BS[s].all;
  const h = g("hancock"), p = g("positive"), r = g("related"), z = g("random");
  const hp = Object.entries(BP).filter(([k, v]) => v.set === "hancock").sort((a, b) => b[1].share_rank1 - a[1].share_rank1);
  const best = hp[0], worst = hp[hp.length - 1];
  const M = R.mechanical && R.mechanical.summary; const pos = Object.entries(BP).filter(([k, v]) => v.set === "positive").sort((a, b) => b[1].share_rank1 - a[1].share_rank1);
  document.getElementById("verdict-p").innerHTML = `The claimed civiliser partner ranked first in <b>${h.rank1} of ${h.n}</b> completed lineups (<b>${(100*h.share_rank1).toFixed(1)}%</b>), compared with ${z.rank1} of ${z.n} random lineups (${(100*z.share_rank1).toFixed(1)}%) and ${p.rank1} of ${p.n} designated positive-control lineups (${(100*p.share_rank1).toFixed(1)}%). This is a substantial similarity signal under the pilot's conditions. It varies across pairs and does not identify a historical cause. The names were removed, but Opus identified the region of <b>${LK.region_correct} of ${LK.n}</b> stories. The source compressions, recognisable narratives, unmatched decoys and repeated judgments limit the inference. The <a href="civilisers.html">source-level follow-up</a> investigates the details behind the resemblance; the original results remain below.`;
  const stats = document.getElementById("stats"); const stat = (num, lbl) => stats.append(el("div", { class: "stat" }, el("div", { class: "num", html: num }), el("div", { class: "lbl" }, lbl)));
  stat(`${h ? pc(h.share_rank1) : "–"}`, `Civiliser pairs: share of ${h ? h.n : "–"} lineups in which the partner was ranked closest of ten. Chance 10%.`);
  stat(`${p ? pc(p.share_rank1) : "–"}`, `Designated positive controls (Gilgamesh and Genesis, Buddha and Josaphat, Ramayana and Reamker …): the same measure.`);
  stat(`${r ? pc(r.share_rank1) : "–"} · ${z ? pc(z.share_rank1) : "–"}`, "Designated related pairs · random pairs from different regions.");
  stat(`${LK.region_correct}<small> / ${LK.n}</small>`, "De-identified stories whose region Opus could still name. The blinding leak.");
  // chart by set and judge
  (function () { const box = document.getElementById("fig-sets"); const sets = ["hancock", "positive", "related", "random"].filter(s => BS[s]); const W = 1100, H = 30 + sets.length * 64; const s = svg(W, H); const L = 330; const x = v => L + v * (W - L - 300);
    for (const v of [0, .1, .25, .5, .75, 1]) { s.append(sv("line", { x1: x(v), x2: x(v), y1: 16, y2: H - 18, stroke: v === .1 ? COL.rust : COL.rule, "stroke-dasharray": v === .1 ? "4 4" : "0" })); s.append(sv("text", { x: x(v), y: H - 4, "text-anchor": "middle", "font-size": 10.5, fill: v === .1 ? COL.rust : COL.faint }, v === .1 ? "chance 10%" : (100 * v) + "%")); }
    sets.forEach((st, i) => { const y = 22 + i * 64; s.append(sv("text", { x: L - 10, y: y + 14, "text-anchor": "end", "font-size": 11.5, fill: COL.soft }, SN[st]));
      [["opus", "Opus 5", 0], ["sonnet", "Sonnet 5", 16], ["all", "both", 32]].forEach(([j, lab, dy]) => { const a = BS[st][j]; if (!a) return; const c = st === "hancock" ? COL.copper : st === "random" ? COL.faint : COL.moss; s.append(sv("rect", { x: x(0), y: y + dy, width: x(a.share_rank1) - x(0), height: 12, fill: c, "fill-opacity": j === "all" ? .95 : .55 })); s.append(sv("text", { x: x(a.share_rank1) + 6, y: y + dy + 10, "font-size": 10, fill: COL.ink }, `${lab}: first ${pc(a.share_rank1)} · mean rank ${f2(a.mean_rank)} · n=${a.n}`)); }); });
    box.append(s); document.getElementById("cap-sets").innerHTML = `<b>How often the planted partner was ranked first, by set and judge.</b> Dashed line: chance. Copper: the civiliser pairs. Green: the designated positive and related controls. Grey: random pairs.`; })();
  // example
  const ex = C["Viracocha"] || C[Object.keys(C)[0]]; const exb = document.getElementById("example");
  exb.append(el("div", { class: "txt" }, el("div", { class: "h" }, `${ex.title} · retold from the article`), ex.story), el("div", { class: "txt" }, el("div", { class: "h" }, "the same story, de-identified · what the judges saw"), ex.blind));
  for (const [k, v] of Object.entries({ leak_correct: LK.region_correct, leak_n: LK.n, leak_cannot: LK.cannot_tell, leak_high_correct: LK.high_conf_correct, leak_high: LK.high_conf })) document.querySelectorAll(`[data-v='${k}']`).forEach(e => e.textContent = v);
  const KEY = ["Viracocha", "Quetzalcoatl", "Kukulkan", "Oannes", "Osiris", "Bochica", "Votan", "Thoth", "Nommo", "Gilgamesh flood myth", "Genesis flood narrative", "Gautama Buddha", "Barlaam and Josaphat", "Ramayana", "Reamker", "Panchatantra", "Kalila wa-Dimna"];
  const lt = document.getElementById("leak-table"); lt.append(el("tr", {}, el("th", {}, "Story"), el("th", {}, "True region"), el("th", {}, "Opus guessed"), el("th", {}, "Figure guessed"), el("th", {}, "Confidence")));
  for (const k of KEY) { const d = LK.per_item[k]; if (!d) continue; lt.append(el("tr", { class: d.guess === d.true ? "hl" : "" }, el("td", {}, title(k)), el("td", {}, d.true), el("td", {}, d.guess), el("td", {}, d.figure), el("td", {}, d.conf))); }
  document.getElementById("leak-text").textContent = `Of the civiliser stories, ${["Viracocha", "Quetzalcoatl", "Oannes", "Osiris", "Bochica", "Votan", "Thoth", "Nommo"].filter(k => LK.per_item[k] && LK.per_item[k].guess === LK.per_item[k].true).length} of 8 had their region named correctly.`;
  // pair table
  const pt = document.getElementById("pair-table"); pt.append(el("tr", {}, el("th", {}, "Set"), el("th", {}, "Pair"), el("th", {}, "n"), el("th", {}, "Mean rank"), el("th", {}, "Ranked first"), el("th", {}, "p"), el("th", {}, "Top three"), el("th", {}, "Opus · Sonnet first"), el("th", {}, "Leak")));
  const leakOf = k => LK.per_item[k] && LK.per_item[k].guess === LK.per_item[k].true ? (LK.per_item[k].conf === "high" ? "high" : "yes") : "";
  for (const st of ["hancock", "positive", "related"]) for (const [k, v] of Object.entries(BP).filter(([k, v]) => v.set === st).sort((a, b) => b[1].share_rank1 - a[1].share_rank1)) { const [a, b] = k.split(" | "); pt.append(el("tr", {}, el("td", {}, SN[st].split(" (")[0]), el("td", {}, `${title(a)} · ${title(b)}`), el("td", { class: "n" }, String(v.n)), el("td", { class: "n" }, f2(v.mean_rank)), el("td", { class: "n" }, `${v.rank1} (${pc(v.share_rank1)})`), el("td", { class: "n" }, v.p_rank1 < 0.001 ? "<0.001" : v.p_rank1.toFixed(3)), el("td", { class: "n" }, pc(v.share_top3)), el("td", { class: "n" }, `${v.by_judge.opus ? pc(v.by_judge.opus.share_rank1) : "–"} · ${v.by_judge.sonnet ? pc(v.by_judge.sonnet.share_rank1) : "–"}`), el("td", { class: "mono" }, [leakOf(a), leakOf(b)].filter(Boolean).join(" / ")))); }
  const rs = document.getElementById("reasons");
  for (const [k, v] of hp) { if (!v.reasons_top.length) continue; rs.append(el("p", { class: "small", html: `<b>${k.replace(" | ", " → ")}</b>, when the partner was ranked first: <em>${v.reasons_top[0]}</em>` })); }
  const bt = document.getElementById("beat-table"); bt.append(el("tr", {}, el("th", {}, "Pair"), el("th", {}, "Ranked above the partner most often")));
  for (const [k, v] of hp) bt.append(el("tr", {}, el("td", {}, k.replace(" | ", " → ")), el("td", {}, Object.entries(v.beaten_by).map(([t, n]) => `${t} (${n})`).join(", ") || "nothing")));
  const cl = document.getElementById("corpus-list");
  for (const k of Object.keys(C).sort((a, b) => C[a].region.localeCompare(C[b].region) || a.localeCompare(b))) { const d = el("details"); d.append(el("summary", { html: `<b>${C[k].title}</b> · ${C[k].region} · <a href="${C[k].url}?oldid=${C[k].revid}">source</a>` }), el("p", { class: "small" }, C[k].blind)); cl.append(d); }
})();

// mechanical similarity (embedding + tf-idf), filled if present
(async function () {
  const R = await (await fetch("data/s4.json")).json(); const M = R.mechanical; if (!M) return;
  const el = (tag, attrs = {}, ...kids) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "class") e.className = v; else if (k === "html") e.innerHTML = v; else e.setAttribute(k, v); } for (const k of kids) if (k != null) e.append(k); return e; };
  const SN = { hancock: "The civilisers", positive: "Designated positive controls", related: "Designated related pairs", random: "Random pairs" };
  const t = document.getElementById("mech-table"); t.append(el("tr", {}, el("th", {}, "Set"), el("th", {}, "Pair"), el("th", {}, "Embedding rank (of " + M.n_corpus + ")"), el("th", {}, "TF-IDF rank"), el("th", {}, "Embedding cosine")));
  for (const st of ["hancock", "positive", "related"]) for (const p of M.pairs.filter(x => x.set === st).sort((a, b) => a.emb_rank - b.emb_rank)) t.append(el("tr", {}, el("td", {}, SN[st]), el("td", {}, p.pair.replace(" | ", " · ")), el("td", { class: "n" }, `${p.emb_rank} / ${p.emb_rank_rev}`), el("td", { class: "n" }, `${p.tfidf_rank} / ${p.tfidf_rank_rev}`), el("td", { class: "n" }, p.emb_cos.toFixed(2))));
  const s = M.summary; document.getElementById("cap-mech").innerHTML = `<b>Where each pair's partner ranks among all stories, by embedding and word-overlap comparisons.</b> Two ranks per cell: target→partner and partner→target. Median embedding rank: civiliser pairs ${s.hancock.emb_median}, designated positive controls ${s.positive.emb_median}, designated related pairs ${s.related.emb_median}, random pairs ${s.random.emb_median} (chance is about ${Math.round(M.n_corpus / 2)}).`;
})();
