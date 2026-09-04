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
