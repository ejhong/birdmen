(async function () {
  { const o = new URLSearchParams(location.search).get("off"); if (o) document.body.style.marginTop = (-parseInt(o, 10)) + "px"; }
  const D = await (await fetch("data/s3.json")).json();
  const P = D.results, E = D.exploratory, J = D.jaccard, G = D.groups, IM = D.images, T = D.targets;
  const el = (tag, attrs = {}, ...kids) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "class") e.className = v; else if (k === "html") e.innerHTML = v; else e.setAttribute(k, v); } for (const k of kids) if (k != null) e.append(k); return e; };
  const NS = "http://www.w3.org/2000/svg";
  const sv = (tag, attrs = {}, text) => { const e = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); if (text != null) e.textContent = text; return e; };
  const svg = (w, h) => { const s = sv("svg", { viewBox: `0 0 ${w} ${h}`, width: "100%" }); s.style.maxWidth = w + "px"; s.style.display = "block"; return s; };
  const COL = { ink: "#201b12", soft: "#4c453a", faint: "#877e6c", rule: "#d9d0be", copper: "#9a5b33", moss: "#47705f", rust: "#8e4a38" };
  const label = g => (G[g] ? G[g].label : g);
  const short = g => label(g).split(" (")[0];
  const f2 = x => (x == null || Number.isNaN(x)) ? "–" : Number(x).toFixed(2);
  const f0 = x => (x == null || Number.isNaN(x)) ? "–" : Number(x).toFixed(0);
  const PHRASE = { tanum: "Tanum rock carving", gotland: "Gotland picture stone", assyria: "Nimrud relief", persepolis: "Persepolis relief", egypt: "Egyptian stela", maya: "Maya stela", mississippian: "Mississippian piece", catalhoyuk: "Çatalhöyük painting", anatolia_ppn: "Anatolian pillar", rapa_nui: "Rapa Nui carving" };
  const nKept = P.kept_features.length, nAll = Object.keys(P.alpha).length;
  const vals = {
    n_images: P.n_images.toLocaleString(), n_coded: P.n_coded.toLocaleString(), n_usable: P.n_triaged_usable.toLocaleString(),
    kept: nKept, all: nAll, kept_e: E.kept_features.length,
    e_d: f2(E.target.distance), e_pct: f0(E.target.percentile), e_med: f2(E.nfn_quantiles["0.5"]),
    j_d: f2(J.target.distance), j_pct: f0(J.target.percentile), j_med: f2(J.nfn_quantiles["0.5"]), j_q5: f2(J.nfn_quantiles["0.05"]), j_q95: f2(J.nfn_quantiles["0.95"]),
    p43_nn_group: J.target.p43_nfn && J.target.p43_nfn[1] && IM[J.target.p43_nfn[1]] ? PHRASE[IM[J.target.p43_nfn[1]].group] || short(IM[J.target.p43_nfn[1]].group) : "–",
    hoa_nn_group: J.target.hoa_nfn && J.target.hoa_nfn[1] && IM[J.target.hoa_nfn[1]] ? PHRASE[IM[J.target.hoa_nfn[1]].group] || short(IM[J.target.hoa_nfn[1]].group) : "–",
    pc_both: (J.positive_controls.assyria_persepolis && J.positive_controls.anatolia_catalhoyuk) ? "both positive controls pass" : (!J.positive_controls.assyria_persepolis && !J.positive_controls.anatolia_catalhoyuk) ? "both positive controls fail" : "one positive control passes and the other fails",
    e_p43_nn_group: E.target.p43_nfn && E.target.p43_nfn[1] && IM[E.target.p43_nfn[1]] ? short(IM[E.target.p43_nfn[1]].group) : "–",
    mantel_r: f2(J.mantel.r), mantel_p: f2(J.mantel.p),
    alpha_bird: f2(P.alpha["bird.present"]), alpha_snake: f2(P.alpha["reptile_or_snake.present"]), alpha_posture: f2(P.alpha["bird_posture"]), alpha_headless: f2(P.alpha["headless_human"]), alpha_bag: f2(P.alpha["container_or_bag.present"]), alpha_text: f2(P.alpha["text_or_glyphs.present"]), alpha_quad: f2(P.alpha["quadruped.present"]), alpha_human: f2(P.alpha["human.present"]),
    pc_ap: J.positive_controls.assyria_persepolis ? "passes" : "fails", pc_ac: J.positive_controls.anatolia_catalhoyuk ? "passes" : "fails",
  };
  document.querySelectorAll("[data-v]").forEach(e => { if (vals[e.dataset.v] !== undefined) e.textContent = vals[e.dataset.v]; });

  // stats tiles
  const stats = document.getElementById("stats");
  const stat = (num, lbl) => stats.append(el("div", { class: "stat" }, el("div", { class: "num", html: num }), el("div", { class: "lbl" }, lbl)));
  stat(`${nKept}<small> / ${nAll}</small>`, "Features on which the two blind coders agreed well enough (alpha ≥ 0.67) to be used, as pre-registered. Too few to compute the pre-registered distance.");
  stat(`${vals.alpha_bird}`, "Agreement on whether a bird is present at all. The claim is about birds; the coders could not agree on them.");
  stat(`${vals.j_pct}<small>th pct</small>`, "Exploratory: where the Pillar 43 – moai distance falls among every panel's nearest-foreign-neighbour distance. 5 or below was the bar; 100 is farthest.");
  stat(`${vals.pc_ap} · ${vals.pc_ac}`, "Exploratory positive controls (Assyria–Persepolis, Anatolia–Çatalhöyük). The instrument is not yet trusted.");

  // pair cards
  const card = (id, title, extra = "") => {
    const im = IM[id]; const c = el("div", { class: "pcard" });
    c.append(el("div", { class: "ph" }, el("img", { src: `img/s3/${id}.jpg`, alt: title })));
    c.append(el("div", { class: "cap", html: `<b>${title}</b>${extra}<br>${label(im.group)} · <a href="${im.page}">${im.title}</a> (${im.license})<br><br><b>Opus:</b> ${im.notes}<br><b>Sonnet:</b> ${im.notes_sonnet}` }));
    return c;
  };
  const pair = document.getElementById("pair");
  if (T.pillar43 && IM[T.pillar43]) pair.append(card(T.pillar43, "Göbekli Tepe, Pillar 43"));
  if (T.hoa_back && IM[T.hoa_back]) pair.append(card(T.hoa_back, "Hoa Hakananai'a, the back"));
  const pnn = document.getElementById("pair-nn");
  for (const [tid, name] of [[T.pillar43, "Pillar 43"], [T.hoa_back, "the moai's back"]]) {
    const nn = IM[tid] && IM[tid].nn; if (!nn || !IM[nn]) continue;
    pnn.append(card(nn, `Nearest foreign neighbour of ${name}`, ` · distance ${f2(IM[tid].nn_d)} (exploratory, Jaccard)`));
  }

  // corpus table
  const ct = document.getElementById("corpus-table");
  ct.append(el("tr", {}, el("th", {}, "Group"), el("th", {}, "Role"), el("th", {}, "Fetched"), el("th", {}, "Usable"), el("th", {}, "Coded")));
  const roles = { anatolia_ppn: "target A", rapa_nui: "target B", catalhoyuk: "control, positive pair with A", assyria: "control, positive pair", persepolis: "control, positive pair", egypt: "control", maya: "control", mississippian: "control (independent birdman)", gotland: "control", tanum: "control" };
  const usableBy = {}; // not in results; approximate from per_group and fetched
  for (const g of Object.keys(G)) ct.append(el("tr", {}, el("td", {}, label(g)), el("td", {}, roles[g] || "control"), el("td", { class: "n" }, String(P.fetched_per_group[g] || 0)), el("td", { class: "n" }, String((P.usable_per_group || {})[g] ?? "")), el("td", { class: "n" }, String(P.per_group[g] || 0))));

  // alpha table
  const at = document.getElementById("alpha-table");
  at.append(el("tr", {}, el("th", {}, "Feature"), el("th", {}, "Alpha"), el("th", {}, "Pre-registered (≥ 0.67)"), el("th", {}, "Exploratory (≥ 0.5)")));
  const kept = new Set(P.kept_features), keptE = new Set(E.kept_features);
  for (const [ft, a] of Object.entries(P.alpha).sort((x, y) => y[1] - x[1])) at.append(el("tr", { class: kept.has(ft) ? "hl" : "" }, el("td", { class: "mono" }, ft), el("td", { class: "n" }, f2(a)), el("td", { class: "mono", style: `color:${kept.has(ft) ? "var(--moss)" : "var(--faint)"}` }, kept.has(ft) ? "kept" : "dropped"), el("td", { class: "mono", style: `color:${keptE.has(ft) ? "var(--moss)" : "var(--faint)"}` }, keptE.has(ft) ? "kept" : "dropped")));

  // null histogram (Jaccard variant)
  (function () {
    const box = document.getElementById("fig-null"); const ds = D.nfn.map(r => r.d).filter(x => x != null && !Number.isNaN(x)); const tg = J.target;
    const W = 1040, H = 260, L = 40, B = 50; const s = svg(W, H); const lo = 0, hi = Math.max(0.7, tg.distance + 0.05, ...ds); const nb = 30;
    const bins = new Array(nb).fill(0); for (const d of ds) bins[Math.min(nb - 1, Math.floor((d - lo) / (hi - lo) * nb))]++;
    const x = v => L + (v - lo) / (hi - lo) * (W - L - 20); const maxc = Math.max(...bins); const y = c => H - B - c / maxc * (H - B - 30);
    bins.forEach((c, i) => { const v0 = lo + (hi - lo) * i / nb, v1 = lo + (hi - lo) * (i + 1) / nb; s.append(sv("rect", { x: x(v0), y: y(c), width: x(v1) - x(v0) - 1, height: H - B - y(c), fill: COL.faint, "fill-opacity": .6 })); });
    for (let v = 0; v <= hi + 1e-9; v += 0.1) s.append(sv("text", { x: x(v), y: H - B + 16, "text-anchor": "middle", "font-size": 11, fill: COL.faint }, v.toFixed(1)));
    s.append(sv("text", { x: L, y: H - B + 34, "font-size": 11, fill: COL.faint }, "distance to nearest foreign neighbour (0 = identical code, 1 = nothing in common); exploratory Jaccard variant"));
    s.append(sv("line", { x1: x(tg.distance), x2: x(tg.distance), y1: 20, y2: H - B, stroke: COL.copper, "stroke-width": 2 })); s.append(sv("text", { x: x(tg.distance) - 6, y: 32, "text-anchor": "end", "font-size": 12, fill: COL.copper }, `Pillar 43 – moai back: ${f2(tg.distance)} (${f0(tg.percentile)}th pct)`));
    const q5 = J.nfn_quantiles["0.05"]; s.append(sv("line", { x1: x(q5), x2: x(q5), y1: 40, y2: H - B, stroke: COL.rust, "stroke-dasharray": "4 4" })); s.append(sv("text", { x: x(q5) + 6, y: 52, "font-size": 11, fill: COL.rust }, `closest 5% (the pre-registered bar)`));
    box.append(s);
    document.getElementById("cap-null").innerHTML = `<b>Nearest-foreign-neighbour distances for all ${ds.length} coded panels, exploratory Jaccard variant.</b> Median ${f2(J.nfn_quantiles["0.5"])}; 5th to 95th percentile ${f2(J.nfn_quantiles["0.05"])} to ${f2(J.nfn_quantiles["0.95"])}. The target pair is farther apart than ${f0(J.target.percentile)}% of panels are from their own best foreign match.`;
  })();

  // heatmap (Jaccard)
  (function () {
    const box = document.getElementById("fig-heat"); const gs = Object.keys(G); const gd = J.group_distances;
    const get = (a, b) => gd[`${[a, b].sort()[0]}|${[a, b].sort()[1]}`];
    const vals = Object.values(gd).filter(v => v != null); const lo = Math.min(...vals), hi = Math.max(...vals);
    const grid = el("div", { class: "heat", style: `grid-template-columns: 170px repeat(${gs.length}, 1fr)` });
    grid.append(el("div", { class: "lbl" }, "")); for (const g of gs) grid.append(el("div", { class: "top" }, short(g)));
    for (const a of gs) { grid.append(el("div", { class: "lbl" }, short(a))); for (const b of gs) { const v = get(a, b); const t = v == null ? 0 : (v - lo) / (hi - lo + 1e-9); const bg = v == null ? "#fff" : `rgba(154,91,51,${(1 - t) * 0.85 + 0.05})`; grid.append(el("div", { style: `background:${bg}`, title: `${label(a)} × ${label(b)}: ${f2(v)}` }, v == null ? "" : f2(v))); } }
    box.append(grid);
    const near = J.nearest_groups; const lines = Object.keys(near).map(g => `${short(g)} → ${near[g].slice(0, 2).map(short).join(", ")}`);
    document.getElementById("cap-heat").innerHTML = `<b>Mean composition distance between groups, exploratory Jaccard variant</b> (darker = closer; the diagonal is within-group). Each group's two closest groups: ${lines.join(" · ")}.`;
    const within = gs.map(g => get(g, g)).filter(v => v != null); const between = gs.flatMap(a => gs.filter(b => b > a).map(b => get(a, b))).filter(v => v != null);
    document.getElementById("mantel-text").innerHTML = `Within-group distances average <b>${f2(within.reduce((s, v) => s + v, 0) / within.length)}</b> and between-group distances <b>${f2(between.reduce((s, v) => s + v, 0) / between.length)}</b>: the retained features barely tell a tradition's own panels from foreign ones, which is the clearest statement of how coarse this pilot's instrument is. Composition distance against geographic distance gives a Mantel correlation of <b>${f2(J.mantel.r)}</b> (permutation p = ${f2(J.mantel.p)}, ${gs.length} groups): ${J.mantel.r > 0.3 ? "nearby traditions compose alike" : "no usable distance decay at this resolution"}.`;
  })();

  // drivers (Jaccard results carry consensus codes for the two targets)
  (function () {
    const t = document.getElementById("drivers-table"); const tg = J.target; if (!tg.drivers) return;
    t.append(el("tr", {}, el("th", {}, "Feature"), el("th", {}, "Pillar 43"), el("th", {}, "Moai back"), el("th", {}, "Match"), el("th", {}, "Corpus share of this value")));
    let m = 0, mm = 0, rare = 0, dis = 0;
    for (const [ft, v] of Object.entries(tg.drivers)) {
      const a = v.p43, b = v.hoa; if (a == null || b == null) { dis++; t.append(el("tr", { style: "opacity:.55" }, el("td", { class: "mono" }, ft), el("td", { class: "v" }, a ?? "coders disagree"), el("td", { class: "v" }, b ?? "coders disagree"), el("td", {}, "–"), el("td", {}, ""))); continue; }
      const match = a === b; if (match) m++; else mm++;
      const share = match ? (tg.base_rates[ft] || {})[a] : null; if (match && share != null && share < 0.25) rare++;
      t.append(el("tr", { class: match ? "match" : "mismatch" }, el("td", { class: "mono" }, ft), el("td", { class: "v" }, String(a)), el("td", { class: "v" }, String(b)), el("td", { class: "mono" }, match ? "yes" : "no"), el("td", { class: "v" }, match && share != null ? `${(100 * share).toFixed(0)}%${share < 0.25 ? " · rare" : share > 0.5 ? " · common" : ""}` : "")));
    }
    document.getElementById("cap-drivers").innerHTML = `<b>${m} features match, ${mm} do not, ${dis} could not be compared because the coders disagreed on one of the two panels.</b> ${rare} of the matches are on values held by fewer than a quarter of the corpus. Most matches are shared absences: neither panel has a plant, a weapon, a text block or a bird-human hybrid as coded, and a shared absence is what the Jaccard variant discounts.`;
  })();

  // neighbour gallery
  (function () {
    const box = document.getElementById("nn-grid"); const rows = D.nfn.filter(r => r.nn && IM[r.id] && IM[r.nn]);
    function draw() {
      box.innerHTML = ""; const pick = rows.slice().sort(() => Math.random() - .5).slice(0, 12);
      for (const r of pick) {
        const c = el("div", { class: "nn" }); const two = el("div", { class: "two" });
        two.append(el("div", { class: "ph" }, el("img", { src: `img/s3/${r.id}.jpg`, loading: "lazy" })), el("div", { class: "ph" }, el("img", { src: `img/s3/${r.nn}.jpg`, loading: "lazy" })));
        c.append(two, el("div", { class: "cap", html: `${short(r.group)} → ${short(r.nn_group)} · d = ${f2(r.d)}` })); box.append(c);
      }
    }
    document.getElementById("btn-shuffle").addEventListener("click", draw); draw();
  })();
})();

// ---------------- Pilot B: direct judgment ----------------
(async function () {
  const D = await (await fetch("data/s3.json")).json();
  const R = D.judge; if (!R || !R.target) return;
  const G = D.groups, IM = D.images, T = D.targets;
  const el = (tag, attrs = {}, ...kids) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "class") e.className = v; else if (k === "html") e.innerHTML = v; else e.setAttribute(k, v); } for (const k of kids) if (k != null) e.append(k); return e; };
  const NS = "http://www.w3.org/2000/svg";
  const sv = (tag, attrs = {}, text) => { const e = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); if (text != null) e.textContent = text; return e; };
  const svg = (w, h) => { const s = sv("svg", { viewBox: `0 0 ${w} ${h}`, width: "100%" }); s.style.maxWidth = w + "px"; s.style.display = "block"; return s; };
  const COL = { ink: "#201b12", soft: "#4c453a", faint: "#877e6c", rule: "#d9d0be", copper: "#9a5b33", moss: "#47705f", rust: "#8e4a38", slate: "#5d6672" };
  const short = g => (G[g] ? G[g].label : g).split(" (")[0];
  const f1 = x => (x == null || Number.isNaN(x)) ? "–" : Number(x).toFixed(1);
  const f0 = x => (x == null || Number.isNaN(x)) ? "–" : Number(x).toFixed(0);
  const JN = { opus: "Claude Opus 5", sonnet: "Claude Sonnet 5", gpt: "GPT-5.5" };
  const tg = R.target;

  // verdict + tiles
  const full = tg.full_pillar, top = tg.top_only, bj = tg.by_judge;
  const nullO = R.null, nullG = R.null_gpt, same = R.same, pos = R.poscontrol;
  const pctO = tg.opus_pct_null, pctG = tg.gpt_pct_null;
  const p43s = R.search_p43, hoas = R.search_hoa, p43g = R.search_p43_gpt, hoag = R.search_hoa_gpt;
  const nBetterO = R.rank_moai_in_p43_search_opus, nBetterG = R.rank_moai_in_p43_search_gpt;
  const LU = (D.lineup && D.lineup.by_set) || {}; const g = (st) => LU[st] && LU[st].all; const mm = g("moai_iso_among_monoliths"), pm = g("p43_iso_among_monoliths"), mr = g("moai_among_random"), pr = g("p43_among_random"), sm = g("same_control_monoliths"), sc = g("same_control"), rc = g("related_control");
  const pc = x => (x == null) ? "–" : (100 * x).toFixed(0) + "%";
  const verdict = `Five vision models, judging blind, do not find the back of Hoa Hakananai'a unusually similar to Pillar 43. <b>Lineups.</b> Shown the pillar and ten candidates, all free-standing monoliths or statues with their backgrounds removed, the judges ranked the moai first in <b>${mm ? `${mm.rank1} of ${mm.n}` : "–"}</b> lineups (chance: one in ten; mean rank ${mm ? mm.mean_rank.toFixed(1) : "–"} of 10, chance 5.5); shown the moai, they ranked Pillar 43 first in <b>${pm ? pc(pm.share_rank1) : "–"}</b>. A monolith from the same tradition as the target was picked out of the same kind of lineup <b>${sm ? pc(sm.share_rank1) : "–"}</b> of the time. With random decoys and the original photographs the moai had been picked out ${mr ? pc(mr.share_rank1) : "–"} of the time and the pillar ${pr ? pc(pr.share_rank1) : "–"}, and the judges' reasons showed why: both are carved standing stones in a lineup of wall reliefs and rock panels. <b>Direct scores.</b> Side by side, the whole of Pillar 43 and the moai's back score <b>${f1(full.mean)}</b> out of 10 on average across ${full.n} judgments by three models (Opus ${f1(bj.opus.mean)}, Sonnet ${f1(bj.sonnet.mean)}, GPT-5.5 ${f1(bj.gpt.mean)}); random foreign pairs average <b>${f1(nullO.mean)}</b> under the primary judge, same-tradition pairs <b>${f1(same.mean)}</b>, and Assyrian–Persepolis pairs, the documented-descent control, <b>${f1(pos.mean)}</b>. The pair's Opus score sits at the <b>${f0(pctO)}th percentile</b> of the foreign-pair null${tg.opus_pct_null_mono != null ? ` (${f0(tg.opus_pct_null_mono)}th among monolith-to-monolith pairs)` : ""}${pctG != null ? `, its GPT-5.5 score at the <b>${f0(pctG)}th</b> of GPT-5.5's own null` : ""}. Searching the whole corpus for Pillar 43's best match, Opus rates <b>${nBetterO ? nBetterO.n_better : "–"}</b> panel${nBetterO && nBetterO.n_better === 1 ? "" : "s"} from other traditions above the moai and ${nBetterO ? nBetterO.n_equal : "–"} level with it, GPT-5.5 <b>${nBetterG ? nBetterG.n_better : "–"}</b> above; so for Opus the moai is near the top of the foreign list, at a score its own reasons call "generic monolith-decoration conventions rather than a common specific scheme", and the direct scores show the same object-type pull as the lineups: Opus scores Pillar 43 against free-standing monoliths ${p43s && p43s.by_objtype.freestanding_monolith ? f1(p43s.by_objtype.freestanding_monolith.mean) : "–"} on average and against wall reliefs ${p43s && p43s.by_objtype.wall_or_architectural_relief ? f1(p43s.by_objtype.wall_or_architectural_relief.mean) : "–"}.`;
  document.getElementById("verdict-b").innerHTML = verdict;
  const stats = document.getElementById("stats-b");
  const stat = (num, lbl) => stats.append(el("div", { class: "stat" }, el("div", { class: "num", html: num }), el("div", { class: "lbl" }, lbl)));
  stat(`${mm ? mm.rank1 : "–"}<small> / ${mm ? mm.n : "–"}</small>`, "Object-type-matched lineups in which the moai was ranked the closest of ten candidates to Pillar 43. Chance would give about one in ten.");
  stat(`${sm ? pc(sm.share_rank1) : "–"}`, "How often a monolith from the target's own tradition was picked out of the same kind of lineup.");
  stat(`${f1(full.mean)}<small> / 10</small>`, `Mean similarity of Pillar 43 (whole) and the moai's back across ${full.n} blind judgments by three models.`);
  stat(`${f1(nullO.mean)} · ${f1(same.mean)} · ${f1(pos.mean)}`, "Mean score for random foreign pairs · same-tradition pairs · Assyria–Persepolis pairs (Opus).");
  stat(`${f0(pctO)}<small>th pct</small>`, "Where the pair's Opus score falls among random foreign pairs. Above 95 would be exceptional.");
  stat(`${nBetterO ? nBetterO.n_better : "–"}<small> / ${nBetterO ? nBetterO.n : "–"}</small>`, "Panels from other traditions that Opus rates above the moai as a match for Pillar 43, out of all such panels.");
  stats.style.gridTemplateColumns = "repeat(3, 1fr)";

  // target table
  const tt = document.getElementById("target-table");
  tt.append(el("tr", {}, el("th", {}, "Pillar 43 image"), el("th", {}, "Moai image"), el("th", {}, "Opus"), el("th", {}, "Sonnet"), el("th", {}, "GPT-5.5"), el("th", {}, "Mean")));
  const PN = { full: "whole pillar (DAI photo)", full_above: "whole pillar, from above (DAI photo)", top_only: "top only (Commons photo, pilot A)", iso: "whole pillar, background removed" }, HN = { back_full: "full back, British Museum", back_close: "closer view of the back", iso: "full back, background removed" };
  for (const p of ["full", "full_above", "top_only", "iso"]) for (const h of ["back_full", "back_close", "iso"]) {
    if ((p === "iso") !== (h === "iso")) continue;
    const rows = tg.by_pair[`${p}|${h}`]; if (!rows || !rows.n) continue;
    const per = m => { const s = R.target_rows.filter(r => r.p43 === p && r.hoa === h && r.judge === m).map(r => r.score); return s.length ? s.join(" / ") : "–"; };
    tt.append(el("tr", { class: p === "full" && h === "back_full" ? "hl" : "" }, el("td", {}, PN[p]), el("td", {}, HN[h]), el("td", { class: "mono" }, per("opus")), el("td", { class: "mono" }, per("sonnet")), el("td", { class: "mono" }, per("gpt")), el("td", { class: "n" }, f1(rows.mean))));
  }
  document.getElementById("cap-target").innerHTML = `<b>Every judgment of the target pair.</b> Two scores per cell are the two left–right orders. The highlighted row is the primary pairing: the whole pillar against the full back.`;

  // null histogram
  (function () {
    const box = document.getElementById("fig-judge-null"); const W = 1040, H = 300, L = 50, B = 60; const s = svg(W, H);
    const series = [[nullO.hist, COL.faint, "random foreign pairs (Opus, n=" + nullO.n + ")"], [same.hist, COL.slate, "same-tradition pairs (n=" + same.n + ")"], [pos.hist, COL.moss, "Assyria–Persepolis pairs (n=" + pos.n + ")"]].filter(([h]) => h && h.length);
    const x = v => L + v / 11 * (W - L - 20); const bw = (W - L - 20) / 11 / 3.4;
    const maxp = Math.max(...series.map(([h]) => Math.max(...h.map(c => c / h.reduce((a, b) => a + b, 0)))));
    const y = p => H - B - p / maxp * (H - B - 40);
    series.forEach(([h, c, lab], k) => { const tot = h.reduce((a, b) => a + b, 0); h.forEach((cnt, v) => { const p = cnt / tot; s.append(sv("rect", { x: x(v) + k * bw + 4, y: y(p), width: bw - 1, height: H - B - y(p), fill: c, "fill-opacity": .8 })); }); s.append(sv("rect", { x: L + k * 300, y: H - 22, width: 10, height: 10, fill: c })); s.append(sv("text", { x: L + k * 300 + 14, y: H - 13, "font-size": 11, fill: COL.soft }, lab)); });
    for (let v = 0; v <= 10; v++) s.append(sv("text", { x: x(v) + 1.7 * bw, y: H - B + 16, "text-anchor": "middle", "font-size": 11, fill: COL.faint }, String(v)));
    s.append(sv("text", { x: L, y: H - B + 32, "font-size": 11, fill: COL.faint }, "similarity score, 0 to 10 · bars are the share of pairs at each score"));
    const tx = x(full.mean) + 1.7 * bw; s.append(sv("line", { x1: tx, x2: tx, y1: 16, y2: H - B, stroke: COL.copper, "stroke-width": 2 })); s.append(sv("text", { x: tx + 6, y: 28, "font-size": 12, fill: COL.copper }, `Pillar 43 × moai: ${f1(full.mean)} (${f0(pctO)}th pct of foreign pairs)`));
    box.append(s);
    document.getElementById("cap-judge-null").innerHTML = `<b>What similarity scores look like across the corpus.</b> Foreign pairs: median ${f1(nullO.quantiles["0.5"])}, 95th percentile ${f1(nullO.quantiles["0.95"])}. Same-tradition pairs and the documented-descent control show what "related" looks like to the same judge.`;
    const bo = p43s && p43s.by_objtype; const ho = hoas && hoas.by_objtype;
  document.getElementById("judge-context").innerHTML = `Among random foreign pairs, ${(100 * (tg.opus_share_null_ge || 0)).toFixed(1)}% score at or above the pair's Opus mean of ${f1(bj.opus.mean)}${R.null_mono && R.null_mono.n ? `; among foreign pairs where both panels are free-standing monoliths or statues (n=${R.null_mono.n}, mean ${f1(R.null_mono.mean)}), the pair is at the ${f0(tg.opus_pct_null_mono)}th percentile` : ""}. Object type pulls the direct scores as it pulled the lineups: with Pillar 43 as one side, Opus's mean score against monoliths is ${bo && bo.freestanding_monolith ? f1(bo.freestanding_monolith.mean) : "–"}, against statues ${bo && bo.statue ? f1(bo.statue.mean) : "–"}, against wall reliefs ${bo && bo.wall_or_architectural_relief ? f1(bo.wall_or_architectural_relief.mean) : "–"}, against rock surfaces ${bo && bo.rock_surface ? f1(bo.rock_surface.mean) : "–"}; with the moai's back as one side, against statues ${ho && ho.statue ? f1(ho.statue.mean) : "–"}, monoliths ${ho && ho.freestanding_monolith ? f1(ho.freestanding_monolith.mean) : "–"}, wall reliefs ${ho && ho.wall_or_architectural_relief ? f1(ho.wall_or_architectural_relief.mean) : "–"}. The pair scores at the ${f0(tg.opus_pct_same)}th percentile of same-tradition pairs and the ${f0(tg.opus_pct_pos)}th percentile of Assyria–Persepolis pairs.`;
  })();

  // quotes
  const q = document.getElementById("target-quotes");
  for (const r of R.target_rows.filter(r => r.p43 === "full" && r.hoa === "back_full").sort((a, b) => a.judge.localeCompare(b.judge))) {
    q.append(el("p", { class: "small", html: `<b>${JN[r.judge]}</b> (${r.order === "p43_left" ? "pillar left" : "pillar right"}), score ${r.score}: <em>${r.why}</em> Shared elements listed: ${r.elements.join("; ") || "none"}.` }));
  }

  // search panels
  const sp = document.getElementById("search-panels");
  const panel = (title, res, tid) => {
    if (!res) return;
    const wrap = el("div", { style: "margin:14px 0 26px" });
    const nSame = res.top.filter(x => x.group === "anatolia_ppn" || x.group === "rapa_nui").length;
    wrap.append(el("h4", { class: "kicker", style: "margin:0 0 8px;font-size:.85rem" }, `${title} · ${res.n} panels judged · ${res.n_ge["6"]} scored 6 or more, ${res.n_ge["7"]} scored 7 or more · the top ${nSame} of ${res.top.length} are other photographs from the target's own tradition, often of the same object; these are the best from other traditions`));
    const grid = el("div", { class: "nn-grid" });
    for (const m of (res.top_foreign || res.top).slice(0, 6)) {
      const c = el("div", { class: "nn" }); const two = el("div", { class: "two" });
      two.append(el("div", { class: "ph" }, el("img", { src: `img/s3/${tid}.jpg`, loading: "lazy" })), el("div", { class: "ph" }, el("img", { src: `img/s3/${m.id}.jpg`, loading: "lazy" })));
      c.append(two, el("div", { class: "cap", html: `<b>${m.score}/10</b> · ${short(m.group)} · <a href="${IM[m.id] ? IM[m.id].page : "#"}">source</a><br>${m.why}` })); grid.append(c);
    }
    wrap.append(grid); sp.append(wrap);
  };
  panel("Best matches for Pillar 43, judged by Opus", p43s, T.pillar43);
  panel("Best matches for Pillar 43, judged by GPT-5.5", p43g, T.pillar43);
  panel("Best matches for the moai's back, judged by Opus", hoas, T.hoa_back);
  panel("Best matches for the moai's back, judged by GPT-5.5", hoag, T.hoa_back);

  // reliability
  const rel = R.reliability || {};
  const rt = [];
  if (rel.sonnet) rt.push(`Sonnet against Opus on ${rel.sonnet.n} shared foreign pairs: Spearman ${rel.sonnet.spearman.toFixed(2)}, within one point ${(100 * rel.sonnet.within_one).toFixed(0)}% of the time (Sonnet's mean ${f1(rel.sonnet.mean_other)} vs Opus ${f1(rel.sonnet.mean_opus)}).`);
  if (rel.gpt) rt.push(`GPT-5.5 against Opus on ${rel.gpt.n} shared pairs: Spearman ${rel.gpt.spearman.toFixed(2)}, within one point ${(100 * rel.gpt.within_one).toFixed(0)}% (GPT-5.5's mean ${f1(rel.gpt.mean_other)}).`);
  if (rel.gpt_on_p43_search) rt.push(`On the ${rel.gpt_on_p43_search.n} Pillar 43 comparisons both judged, Opus and GPT-5.5 correlate at ${rel.gpt_on_p43_search.spearman.toFixed(2)}.`);
  document.getElementById("rel-text").innerHTML = rt.join(" ") || "Reliability sets not yet judged.";
})();

// ---------------- Pilot C: lineups ----------------
(async function () {
  const D = await (await fetch("data/s3.json")).json();
  const R = D.lineup; if (!R || !R.by_set) return;
  const G = D.groups; const short = g => (G[g] ? G[g].label : g).split(" (")[0];
  const el = (tag, attrs = {}, ...kids) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "class") e.className = v; else if (k === "html") e.innerHTML = v; else e.setAttribute(k, v); } for (const k of kids) if (k != null) e.append(k); return e; };
  const NS = "http://www.w3.org/2000/svg";
  const sv = (tag, attrs = {}, text) => { const e = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); if (text != null) e.textContent = text; return e; };
  const svg = (w, h) => { const s = sv("svg", { viewBox: `0 0 ${w} ${h}`, width: "100%" }); s.style.maxWidth = w + "px"; s.style.display = "block"; return s; };
  const COL = { ink: "#201b12", soft: "#4c453a", faint: "#877e6c", rule: "#d9d0be", copper: "#9a5b33", moss: "#47705f", rust: "#8e4a38", slate: "#5d6672" };
  const SN = { moai_among_random: "Moai's back among 9 random decoys (target: Pillar 43)", moai_close_among_random: "Moai's back, close view, among 9 random decoys", moai_iso_among_random: "Isolated moai among 9 random decoys (target: isolated Pillar 43)", moai_iso_among_monoliths: "Isolated moai among 9 monoliths and statues", p43_among_random: "Pillar 43 among 9 random decoys (target: moai's back)", p43_iso_among_monoliths: "Isolated Pillar 43 among 9 monoliths (target: isolated moai)", hard: "Moai vs Opus's 9 best foreign matches for Pillar 43", related_control: "Control: Assyrian panel among random decoys (target: Persepolis)", same_control: "Control: same-tradition panel among random decoys", same_control_monoliths: "Control: same-tradition monolith among monoliths" };
  const JN = { opus: "Opus 5", gpt: "GPT-5.5", gemini: "Gemini 3.1 Pro", sonnet: "Sonnet 5", grok: "Grok 4.6", all: "All judges" };
  const f2 = x => (x == null || Number.isNaN(x)) ? "–" : Number(x).toFixed(2);
  const pc = x => (x == null) ? "–" : (100 * x).toFixed(0) + "%";
  const order = ["moai_among_random", "moai_close_among_random", "moai_iso_among_random", "moai_iso_among_monoliths", "p43_among_random", "p43_iso_among_monoliths", "hard", "related_control", "same_control", "same_control_monoliths"].filter(s => R.by_set[s]);
  // chart: share rank-1 per set (all judges), with chance line
  (function () {
    const box = document.getElementById("fig-lineup"); const W = 1180, H = 40 + order.length * 46; const s = svg(W, H); const L = 330;
    const x = v => L + v * (W - L - 300);
    const SS = { moai_among_random: "Moai for Pillar 43, random decoys", moai_close_among_random: "Moai (close view), random decoys", moai_iso_among_random: "Moai, isolated, random decoys", moai_iso_among_monoliths: "Moai, isolated, monolith decoys", p43_among_random: "Pillar 43 for moai, random decoys", p43_iso_among_monoliths: "Pillar 43, isolated, monolith decoys", hard: "Moai vs Opus's 9 best foreign matches", related_control: "Control: Assyrian for Persepolis", same_control: "Control: same tradition, random decoys", same_control_monoliths: "Control: same tradition, monoliths" };
    for (const v of [0, .1, .25, .5, .75, 1]) { s.append(sv("line", { x1: x(v), x2: x(v), y1: 20, y2: H - 20, stroke: v === .1 ? COL.rust : COL.rule, "stroke-dasharray": v === .1 ? "4 4" : "0" })); s.append(sv("text", { x: x(v), y: H - 6, "text-anchor": "middle", "font-size": 10.5, fill: v === .1 ? COL.rust : COL.faint }, v === .1 ? "chance 10%" : (100 * v) + "%")); }
    order.forEach((st, i) => {
      const y = 28 + i * 46; const a = R.by_set[st].all; if (!a) return;
      s.append(sv("text", { x: L - 10, y: y + 12, "text-anchor": "end", "font-size": 11.5, fill: COL.soft }, SS[st] || SN[st]));
      const c = st.startsWith("moai") || st.startsWith("p43") || st === "hard" ? COL.copper : COL.moss;
      s.append(sv("rect", { x: x(0), y: y + 2, width: x(a.share_rank1) - x(0), height: 12, fill: c, "fill-opacity": .9 }));
      s.append(sv("rect", { x: x(0), y: y + 17, width: x(a.share_top3) - x(0), height: 6, fill: c, "fill-opacity": .4 }));
      s.append(sv("text", { x: x(Math.max(a.share_rank1, a.share_top3)) + 6, y: y + 13, "font-size": 10.5, fill: COL.ink }, `first ${pc(a.share_rank1)} · top 3 ${pc(a.share_top3)} · mean rank ${Number(a.mean_rank).toFixed(1)} · n=${a.n}`));
    });
    box.append(s);
    document.getElementById("cap-lineup").innerHTML = `<b>How often the planted panel was picked out, all judges pooled.</b> Dark bar: ranked first of ten (chance 10%). Light bar: ranked in the top three (chance 30%). Copper: the target sets; green: the controls.`;
  })();
  // object types by tradition
  const OC = (D.judge || {}).objtype_counts; const ot = document.getElementById("objtype-table");
  if (OC && ot) {
    const types = ["freestanding_monolith", "statue", "wall_or_architectural_relief", "rock_surface", "portable_object", "drawing_or_plan", "other"]; const TN = { freestanding_monolith: "Monolith", statue: "Statue", wall_or_architectural_relief: "Wall relief", rock_surface: "Rock surface", portable_object: "Portable", drawing_or_plan: "Drawing", other: "Other" };
    ot.append(el("tr", {}, el("th", {}, "Tradition"), ...types.map(x => el("th", {}, TN[x]))));
    for (const g of Object.keys(OC).sort()) ot.append(el("tr", {}, el("td", {}, short(g)), ...types.map(x => el("td", { class: "n" }, String(OC[g][x] || "")))));
  }
  // table
  const t = document.getElementById("lineup-table");
  t.append(el("tr", {}, el("th", {}, "Set"), el("th", {}, "Judge"), el("th", {}, "n"), el("th", {}, "Mean rank"), el("th", {}, "Ranked first"), el("th", {}, "p"), el("th", {}, "Top three")));
  for (const st of order) for (const j of ["opus", "gpt", "gemini", "sonnet", "grok", "all"]) {
    const v = R.by_set[st][j]; if (!v) continue;
    t.append(el("tr", { class: j === "all" ? "hl" : "" }, el("td", {}, j === "opus" ? SN[st] : ""), el("td", {}, JN[j]), el("td", { class: "n" }, String(v.n)), el("td", { class: "n" }, f2(v.mean_rank)), el("td", { class: "n" }, `${v.rank1} (${pc(v.share_rank1)})`), el("td", { class: "n" }, v.p_rank1 < 0.001 ? "<0.001" : v.p_rank1.toFixed(3)), el("td", { class: "n" }, pc(v.share_top3))));
  }
  const m = R.by_set.moai_among_random && R.by_set.moai_among_random.all, m2 = R.by_set.moai_close_among_random && R.by_set.moai_close_among_random.all, p = R.by_set.p43_among_random && R.by_set.p43_among_random.all, h = R.by_set.hard && R.by_set.hard.all, rc = R.by_set.related_control && R.by_set.related_control.all, sc = R.by_set.same_control && R.by_set.same_control.all;
  const mi = R.by_set.moai_iso_among_random && R.by_set.moai_iso_among_random.all, mm = R.by_set.moai_iso_among_monoliths && R.by_set.moai_iso_among_monoliths.all, pm = R.by_set.p43_iso_among_monoliths && R.by_set.p43_iso_among_monoliths.all, sm = R.by_set.same_control_monoliths && R.by_set.same_control_monoliths.all;
  document.getElementById("lineup-text").innerHTML = `<b>Among random decoys.</b> With Pillar 43 as the target, the moai's back was picked out first in <b>${m ? pc(m.share_rank1) : "–"}</b> of lineups${m2 ? ` (close view: ${pc(m2.share_rank1)})` : ""}, against 10% by chance; with the moai as target, Pillar 43 was picked first in <b>${p ? pc(p.share_rank1) : "–"}</b>. The controls calibrate that: a random Assyrian panel was picked out for a Persepolis target <b>${rc ? pc(rc.share_rank1) : "–"}</b> of the time, and a same-tradition panel <b>${sc ? pc(sc.share_rank1) : "–"}</b>. But the judges' reasons in these lineups were mostly of one kind: both are "a free-standing monolith whose body is itself a figure", where nearly every decoy is a wall relief, a rock panel or a drawing. That is the type of object, not what is carved on it. <b>Matched on object type.</b> With the backgrounds removed from both photographs and all nine decoys drawn from free-standing monoliths and statues (Maya stelae, Egyptian stelae, Gotland picture stones), the moai was picked first for Pillar 43 <b>${mm ? pc(mm.share_rank1) : "–"}</b> of the time (isolated targets among random decoys: ${mi ? pc(mi.share_rank1) : "–"}), and Pillar 43 for the moai <b>${pm ? pc(pm.share_rank1) : "–"}</b>; a same-tradition monolith was picked out among monoliths <b>${sm ? pc(sm.share_rank1) : "–"}</b> of the time. In the hard lineup, where the decoys are the nine foreign panels Opus itself rated closest to Pillar 43, the moai ranked first ${h ? pc(h.share_rank1) : "–"} of the time and averaged rank ${h ? f2(h.mean_rank) : "–"}.`;
  const ex = R.example;
  if (ex) {
    const decoys = [...new Set(ex.groups.filter((g, i) => i + 1 !== ex.planted_pos).map(short))].join(", ");
    const ranks = ["opus", "gpt", "gemini", "sonnet", "grok"].filter(j => ex.ranks[j]).map(j => `${JN[j]} ${ex.ranks[j] === 1 ? "first" : "#" + ex.ranks[j]}`).join(", ");
    document.getElementById("cap-lineup-example").innerHTML = `<b>The first lineup, exactly as sent to the judges.</b> Target: Pillar 43 (whole). Candidate ${ex.planted_pos} is the moai's back; the decoys are ${decoys} panels. Where each judge ranked the moai: ${ranks}.`;
  }
  const ex2 = R.example_mono;
  if (ex2) {
    const decoys = [...new Set(ex2.groups.filter((g, i) => i + 1 !== ex2.planted_pos).map(short))].join(", ");
    const ranks = ["opus", "gpt", "gemini", "sonnet", "grok"].filter(j => ex2.ranks[j]).map(j => `${JN[j]} ${ex2.ranks[j] === 1 ? "first" : "#" + ex2.ranks[j]}`).join(", ");
    const tops = ["opus", "gpt", "gemini", "sonnet", "grok"].filter(j => ex2.top[j]).map(j => `${JN[j]}: ${short(ex2.top[j])}`).join(", ");
    document.getElementById("cap-lineup-example-mono").innerHTML = `<b>The first object-type-matched lineup.</b> Target: Pillar 43, isolated. Candidate ${ex2.planted_pos} is the moai's back, isolated; the decoys are ${decoys} monoliths. Where each judge ranked the moai: ${ranks}. What each judge ranked first: ${tops}.`;
  }
  const beat = (R.by_set.moai_among_random || {}).decoy_groups_ranked_above_planted || {}, beatM = (R.by_set.moai_iso_among_monoliths || {}).decoy_groups_ranked_above_planted || {};
  document.getElementById("lineup-beat").innerHTML = (Object.keys(beat).length ? `Among random decoys, when a decoy outranked the moai as Pillar 43's match it came from: ${Object.entries(beat).map(([g, n]) => `${short(g)} (${n})`).join(", ")}. ` : "") + (Object.keys(beatM).length ? `Among monoliths: ${Object.entries(beatM).map(([g, n]) => `${short(g)} (${n})`).join(", ")}.` : "");
})();
