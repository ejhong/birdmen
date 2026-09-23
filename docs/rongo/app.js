(async function () {
  { const o = new URLSearchParams(location.search).get("off"); if (o) document.body.style.marginTop = (-parseInt(o, 10)) + "px"; } // dbg-offset
  const D = await (await fetch("data/site.json")).json();
  const S = D.summary, M = D.meta;
  const label = s => (M[s] ? M[s].label : s);
  const SHORT = { egyptian: "Egyptian", anatolian: "Anatolian", cuneiform: "Cuneiform", yi: "Yi", linear_a: "Linear A", linear_b: "Linear B", vai: "Vai", mende_kikakui: "Mende Kikakui", nushu: "Nüshu", indus: "Indus", rongorongo: "Rongorongo" };
  const short = s => s.endsWith("_w") ? (SHORT[s.slice(0, -2)] || label(s)) + " (wobbled)" : (SHORT[s] || label(s));
  const fmt = (x, d = 2) => (x === null || x === undefined || Number.isNaN(x)) ? "–" : Number(x).toFixed(d);
  const pct = x => (100 * x).toFixed(0) + "%";
  const el = (tag, attrs = {}, ...kids) => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) { if (k === "class") e.className = v; else if (k === "html") e.innerHTML = v; else e.setAttribute(k, v); }
    for (const k of kids) if (k != null) e.append(k);
    return e;
  };
  const glyph = (script, id, cls = "", skel = false) => {
    const g = el("span", { class: "glyph " + cls + (skel ? " skel" : "") });
    g.append(el("img", { src: `img/${skel ? "n" : "g"}/${script}/${id}.png`, alt: `${label(script)} ${id}`, loading: "lazy" }));
    return g;
  };
  const SVGNS = "http://www.w3.org/2000/svg";
  const svg = (w, h) => { const s = document.createElementNS(SVGNS, "svg"); s.setAttribute("viewBox", `0 0 ${w} ${h}`); s.setAttribute("width", "100%"); s.style.maxWidth = w + "px"; s.style.display = "block"; return s; };
  const sv = (tag, attrs = {}, text) => { const e = document.createElementNS(SVGNS, tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); if (text != null) e.textContent = text; return e; };
  const COL = { ink: "#201b12", soft: "#4c453a", faint: "#6e6556", rule: "#d9d0be", copper: "#92552e", moss: "#47705f", rust: "#8e4a38", slate: "#5d6672", paper2: "#efe8da" };

  // ---------- numbers in the prose ----------
  const R = D.results;
  const smallSorted = Object.entries(R.small_panel).sort((a, b) => b[1].mean - a[1].mean);
  const vals = {
    rank_best24: S.target_rank_best24,
    lineup_indus_pct: pct(S.lineup.indus), lineup_w_indus_pct: pct(S.lineup_w.indus),
    fid_inflated: S.fidelity_inflated, fid_match: S.fidelity.n_match,
    T: fmt(R.T, 2), Lmed: R.complexity_median, n_pairs: R.target_full.n_pairs.toLocaleString(),
    fid_mean_chart: fmt(S.fidelity_mean_chart), fid_mean_catalog: fmt(S.fidelity_mean_catalog),
    fid_median_pct: S.fidelity.median_pct.toFixed(0), target_matches: R.target_full.matches,
    small_rank: smallSorted.findIndex(([k]) => k === "indus|rongorongo") + 1,
  };
  document.querySelectorAll("[data-v]").forEach(e => { const v = vals[e.dataset.v]; if (v !== undefined) e.textContent = v; });

  // ---------- inventory table ----------
  const invTable = document.getElementById("inv-table");
  invTable.append(el("tr", {}, el("th", {}, "Script"), el("th", {}, "Where and when"), el("th", {}, "Signs"), el("th", {}, "Source"), el("th", {}, "Sample")));
  const order = ["indus", "rongorongo", ...R.all.filter(s => s !== "indus" && s !== "rongorongo").sort((a, b) => R.sizes[b] - R.sizes[a])];
  for (const s of order) {
    const tr = el("tr", { class: (s === "indus" || s === "rongorongo") ? "hl" : "" });
    const name = el("td", {}, label(s), " ", R.big.includes(s) ? el("span", { class: "tag" }, "large") : null);
    tr.append(name, el("td", {}, M[s].note), el("td", { class: "n" }, String(R.sizes[s])), el("td", {}, M[s].source));
    const strip = el("div", { class: "strip" }); for (const g of D.samples[s].slice(0, 11)) strip.append(glyph(s, g.id, "sm"));
    tr.append(el("td", { class: "sample" }, strip)); invTable.append(tr);
  }

  // ---------- statistic selector ----------
  const STATS = {
    best24: ["Best-24 score", "mean combined similarity of the 24 best one-to-one matches (both scripts subsampled to 200 signs, 20 repeats)"],
    match_rate: ["Match rate", "matches (pairs at or above the threshold) per 10,000 candidate pairs"],
    nn_mean: ["Nearest-neighbour mean", "mean over signs of their best match in the other script, both directions"],
    best24_cx: ["Best-24, complex signs only", "best-24 score restricted to signs with above-median skeleton length"],
    rate_cx: ["Match rate, complex signs only", "matches per 10,000 among complex signs"],
    best24_chamfer: ["Best-24, chamfer only", "the same statistic using only the skeleton chamfer similarity"],
    best24_hog: ["Best-24, HOG only", "using only the gradient-histogram similarity"],
    best24_dino: ["Best-24, DINOv2 only", "using only the frozen vision-model embedding"],
  };
  const sel = document.getElementById("stat-select");
  for (const [k, v] of Object.entries(STATS)) sel.append(el("option", { value: k }, v[0]));
  const related = new Set(R.related.map(p => p.join("|")));
  const isRelated = key => { const [a, b] = key.split("|"); return related.has(`${a}|${b}`) || related.has(`${b}|${a}`); };

  function drawAllPairs(stat) {
    const rows = S.all_pairs[stat]; const box = document.getElementById("fig-allpairs"); box.innerHTML = "";
    const W = 1040, H = 300, L = 40, Rr = 40;
    const xs = rows.map(r => r.mean); const lo = Math.min(...xs), hi = Math.max(...xs); const pad = (hi - lo) * 0.08;
    const x = v => L + (v - lo + pad) / (hi - lo + 2 * pad) * (W - L - Rr);
    const s = svg(W, H);
    s.append(sv("line", { x1: L, x2: W - Rr, y1: 150, y2: 150, stroke: COL.rule }));
    // ticks
    const nt = 6; for (let i = 0; i <= nt; i++) { const v = lo - pad + (hi - lo + 2 * pad) * i / nt; s.append(sv("line", { x1: x(v), x2: x(v), y1: 146, y2: 154, stroke: COL.faint })); s.append(sv("text", { x: x(v), y: 172, "text-anchor": "middle", "font-size": 11, fill: COL.faint }, fmt(v, 2))); }
    s.append(sv("text", { x: L, y: 195, "font-size": 11, fill: COL.faint }, STATS[stat][0] + ", 55 pairs of the eleven large scripts"));
    // beeswarm-ish: stack dots that collide
    const placed = [];
    const items = rows.map(r => ({ ...r, x: x(r.mean) })).sort((a, b) => a.x - b.x);
    for (const it of items) {
      let dy = 0, tries = 0;
      const collide = y => placed.some(p => Math.abs(p.x - it.x) < 11 && Math.abs(p.y - y) < 11);
      while (collide(150 + dy) && tries < 20) { tries++; dy = (tries % 2 ? 1 : -1) * Math.ceil(tries / 2) * 11; }
      it.y = 150 + dy; placed.push(it);
    }
    for (const it of placed) {
      const target = it.pair === "indus|rongorongo", rel = isRelated(it.pair);
      const c = target ? COL.copper : rel ? COL.moss : COL.faint;
      const dot = sv("circle", { cx: it.x, cy: it.y, r: target || rel ? 7 : 5, fill: c, "fill-opacity": target || rel ? 1 : .55, stroke: "#fff", "stroke-width": 1 });
      dot.append(sv("title", {}, `${label(it.pair.split("|")[0])} × ${label(it.pair.split("|")[1])}: ${fmt(it.mean, 3)} ± ${fmt(it.sd, 3)}`));
      s.append(dot);
      if (target || rel) {
        const above = target;
        s.append(sv("line", { x1: it.x, x2: it.x, y1: it.y + (above ? -9 : 9), y2: above ? 70 : 240, stroke: c, "stroke-width": 1 }));
        const t = sv("text", { x: it.x, y: above ? 62 : 256, "text-anchor": "middle", "font-size": 12, fill: c }, `${label(it.pair.split("|")[0])} × ${label(it.pair.split("|")[1])}`);
        s.append(t);
        s.append(sv("text", { x: it.x, y: above ? 46 : 272, "text-anchor": "middle", "font-size": 11, fill: c }, `${fmt(it.mean, 2)} · rank ${rows.findIndex(r => r.pair === it.pair) + 1} of 55`));
      }
    }
    box.append(s);
    box.append(el("div", { class: "legend" }, el("span", {}, el("i", { style: `background:${COL.copper}` }), "Indus × rongorongo"), el("span", {}, el("i", { style: `background:${COL.moss}` }), "known related pair (Linear A × Linear B)"), el("span", {}, el("i", { style: `background:${COL.faint}` }), "other pairs")));
    document.getElementById("cap-allpairs").innerHTML = `<b>${STATS[stat][0]} for every pair of the eleven large scripts.</b> ${STATS[stat][1]}. Hover a dot for the pair and its spread over subsamples.`;
    document.getElementById("stat-help").textContent = "";
  }

  function barList(rows, target, statName, highlight = new Set()) {
    const W = 500, rowH = 22, L = 170, H = rows.length * rowH + 40;
    const hi = Math.max(...rows.map(r => r.mean + r.sd)) * 1.05, lo = Math.min(0, ...rows.map(r => r.mean - r.sd));
    const x = v => L + (v - lo) / (hi - lo) * (W - L - 20);
    const s = svg(W, H);
    s.append(sv("text", { x: L, y: 14, "font-size": 11, fill: COL.faint }, `${statName}, against ${label(target)}`));
    rows.forEach((r, i) => {
      const y = 28 + i * rowH; const hl = highlight.has(r.other);
      const c = hl ? COL.copper : r.other.endsWith("_w") ? COL.slate : COL.faint;
      s.append(sv("text", { x: L - 8, y: y + 12, "text-anchor": "end", "font-size": 11.5, fill: hl ? COL.copper : COL.soft }, short(r.other)));
      s.append(sv("rect", { x: x(lo), y: y + 3, width: Math.max(0, x(r.mean) - x(lo)), height: rowH - 8, fill: c, "fill-opacity": hl ? .95 : .55 }));
      s.append(sv("line", { x1: x(r.mean - r.sd), x2: x(r.mean + r.sd), y1: y + rowH / 2 - 1, y2: y + rowH / 2 - 1, stroke: COL.ink, "stroke-width": 1 }));
      s.append(sv("text", { x: x(r.mean + r.sd) + 5, y: y + 12, "font-size": 10.5, fill: COL.faint }, fmt(r.mean, 2)));
    });
    return s;
  }
  function drawVs(stat) {
    const box = document.getElementById("fig-vs"); box.innerHTML = "";
    const wrap = el("div", { style: "display:grid;grid-template-columns:1fr 1fr;gap:24px" });
    wrap.append(barList(S.rank_vs_rongorongo[stat], "rongorongo", STATS[stat][0], new Set(["indus"])), barList(S.rank_vs_indus[stat], "indus", STATS[stat][0], new Set(["rongorongo"])));
    box.append(wrap);
    const boxw = document.getElementById("fig-vs-w"); boxw.innerHTML = "";
    const wrapw = el("div", { style: "display:grid;grid-template-columns:1fr 1fr;gap:24px" });
    wrapw.append(barList(S.wob_vs_rongorongo[stat], "rongorongo", STATS[stat][0] + " (wobbled controls)", new Set(["indus"])), barList(S.wob_vs_indus[stat], "indus", STATS[stat][0] + " (wobbled controls)", new Set(["rongorongo"])));
    boxw.append(wrapw);
  }
  sel.addEventListener("change", () => { drawAllPairs(sel.value); drawVs(sel.value); });
  drawAllPairs("best24"); drawVs("best24");

  // ---------- lineup ----------
  (function () {
    const box = document.getElementById("fig-lineup");
    const W = 1040, H = 250, L = 30;
    const s = svg(W, H);
    const rows = [["Clean font controls", S.lineup, "indus"], ["Wobbled controls", S.lineup_w, "indus"]];
    const keys = Object.keys(S.lineup);
    const bw = (W - L - 20) / keys.length;
    rows.forEach(([title, data, hl], ri) => {
      const y0 = 30 + ri * 110;
      s.append(sv("text", { x: L, y: y0 - 8, "font-size": 11.5, fill: COL.soft }, title + ": which script holds each rongorongo glyph's nearest neighbour"));
      const ymax = 0.45; const yy = v => y0 + 70 - v / ymax * 70;
      s.append(sv("line", { x1: L, x2: W - 20, y1: yy(0.1), y2: yy(0.1), stroke: COL.rust, "stroke-dasharray": "4 4" }));
      s.append(sv("text", { x: W - 22, y: yy(0.1) - 3, "text-anchor": "end", "font-size": 10, fill: COL.rust }, "chance 10%"));
      keys.forEach((k, i) => {
        const kk = ri === 0 ? k : (k === "indus" ? "indus" : k + "_w"); const v = data[kk] ?? 0;
        const x = L + i * bw + 6;
        s.append(sv("rect", { x, y: yy(v), width: bw - 12, height: yy(0) - yy(v), fill: k === hl ? COL.copper : COL.faint, "fill-opacity": k === hl ? 1 : .55 }));
        s.append(sv("text", { x: x + (bw - 12) / 2, y: yy(v) - 4, "text-anchor": "middle", "font-size": 10.5, fill: COL.ink }, pct(v)));
        s.append(sv("text", { x: x + (bw - 12) / 2, y: y0 + 84, "text-anchor": "middle", "font-size": 10.5, fill: COL.soft }, short(k)));
      });
    });
    box.append(s);
  })();

  // ---------- tournament ----------
  (function () {
    const all = { ...D.galleries, ...D.wobble_galleries };
    const keys = Object.keys(all);
    const box = document.getElementById("tournament");
    let hidden = !(new URLSearchParams(location.search).get("reveal") === "1");   // ?reveal=1 starts with labels shown
    function panel(key) {
      const [a, b] = key.split("|"); const g = all[key];
      const p = el("div", { class: "panel" + (hidden ? " hidden-label" : "") });
      const who = el("span", { class: "who" }, hidden ? "? × ?" : `${label(a)} × ${label(b)}`);
      const btn = el("button", { class: "reveal" }, hidden ? "reveal" : "hide");
      btn.addEventListener("click", () => { const h = p.classList.toggle("hidden-label"); who.textContent = h ? "? × ?" : `${label(a)} × ${label(b)}`; btn.textContent = h ? "reveal" : "hide"; });
      const mean = g.reduce((t, r) => t + r.z, 0) / g.length;
      p.append(el("h4", {}, who, el("span", {}, `mean ${fmt(mean, 2)} `, btn)));
      const grid = el("div", { class: "pairs-grid" });
      for (const r of g) { const pr = el("div", { class: "pair" }); pr.append(glyph(a, r.a), glyph(b, r.b), el("span", { class: "z" }, fmt(r.z, 2))); grid.append(pr); }
      p.append(grid); return p;
    }
    function draw() {
      box.innerHTML = "";
      const must = ["indus|rongorongo", "linear_a|linear_b"];
      const rest = keys.filter(k => !must.includes(k)).sort(() => Math.random() - .5).slice(0, 10);
      const show = [...must, ...rest].sort(() => Math.random() - .5);
      for (const k of show) box.append(panel(k));
    }
    document.getElementById("btn-shuffle").addEventListener("click", () => { hidden = true; draw(); });
    document.getElementById("btn-reveal").addEventListener("click", () => { box.querySelectorAll(".panel.hidden-label .reveal").forEach(b => b.click()); });
    document.getElementById("btn-hide").addEventListener("click", () => { box.querySelectorAll(".panel:not(.hidden-label) .reveal").forEach(b => b.click()); });
    draw();
  })();

  // ---------- fidelity cards ----------
  (function () {
    const box = document.getElementById("fidelity");
    for (const p of D.fidelity.pairs) {
      const card = el("div", { class: "fid" });
      const head = el("div", { class: "kicker", style: "display:flex;justify-content:space-between;align-items:center;margin-bottom:8px" }, el("b", { style: "color:var(--ink)" }, p.pair));
      const tags = el("span", {});
      if (p.how === "reviewed") tags.append(el("span", { class: "tag" }, "reviewed"));
      if ((p.note || "").includes("weak")) tags.append(" ", el("span", { class: "tag weak" }, "weak id"));
      if (p.match) tags.append(" ", el("span", { class: "tag target" }, "match"));
      if (p.reciprocal) tags.append(" ", el("span", { class: "tag target" }, "reciprocal"));
      head.append(tags); card.append(head);
      const row = el("div", { class: "row" });
      const cell = (node, lbl, cls = "") => { const c = el("div", { class: "cell " + cls }); c.append(node, el("div", { class: "lbl" }, lbl)); return c; };
      const chartG = f => { const g = el("span", { class: "glyph" }); g.append(el("img", { src: "img/chart/" + f.split("/").pop(), loading: "lazy" })); return g; };
      row.append(cell(chartG(p.chart_indus), "chart, Indus", "chart"), cell(glyph("indus", p.indus), "Mahadevan " + Number(p.indus)), cell(glyph("rongorongo", p.rongorongo), "Barthel " + Number(p.rongorongo)), cell(chartG(p.chart_rongorongo), "chart, Easter Is.", "chart"));
      card.append(row);
      const meta = el("div", { class: "meta" });
      meta.append(el("div", { html: `chart drawings: <b>${fmt(p.z_chart)}</b> &nbsp; catalogue signs: <b>${fmt(p.z_catalog)}</b> <span class="pct">${fmt(p.pct_catalog, 1)}th pct</span>, rank ${p.rank_catalog.toLocaleString()} of ${R.target_full.n_pairs.toLocaleString()}` }));
      meta.append(el("div", { html: `skeleton length ${p.len_indus} / ${p.len_rongorongo} &nbsp;·&nbsp; chamfer ${fmt(p.chamfer)} · hog ${fmt(p.hog)} · dino ${fmt(p.dino)}` }));
      const ru = el("div", { style: "margin-top:6px;display:flex;gap:4px;align-items:center;flex-wrap:wrap" }, el("span", { class: "lbl", style: "margin-right:4px" }, "runners-up"));
      for (const c of p.cand_indus.slice(0, 3)) ru.append(glyph("indus", c.id, "sm"));
      ru.append(el("span", { class: "lbl" }, "·"));
      for (const c of p.cand_rongorongo.slice(0, 3)) ru.append(glyph("rongorongo", c.id, "sm"));
      meta.append(ru);
      card.append(meta);
      if (p.note) card.append(el("div", { class: "note" }, p.note));
      box.append(card);
    }
  })();

  // ---------- histogram ----------
  (function () {
    const box = document.getElementById("fig-hist");
    const h = R.target_full.hist, bins = R.target_full.bins; const W = 1040, H = 300, L = 50, B = 60;
    const s = svg(W, H);
    const x = v => L + (v - bins[0]) / (bins[bins.length - 1] - bins[0]) * (W - L - 20);
    const maxc = Math.max(...h); const y = c => H - B - (c > 0 ? Math.log10(c + 1) / Math.log10(maxc + 1) : 0) * (H - B - 30);
    h.forEach((c, i) => { if (c > 0) s.append(sv("rect", { x: x(bins[i]), y: y(c), width: x(bins[i + 1]) - x(bins[i]) - .5, height: H - B - y(c), fill: COL.faint, "fill-opacity": .6 })); });
    for (let v = -4; v <= 6; v++) { s.append(sv("text", { x: x(v), y: H - B + 16, "text-anchor": "middle", "font-size": 11, fill: COL.faint }, String(v))); }
    [1, 10, 100, 1000, 10000].forEach(c => { if (c <= maxc) { s.append(sv("line", { x1: L - 4, x2: L, y1: y(c), y2: y(c), stroke: COL.faint })); s.append(sv("text", { x: L - 8, y: y(c) + 4, "text-anchor": "end", "font-size": 10, fill: COL.faint }, c.toLocaleString())); } });
    s.append(sv("text", { x: L, y: H - B + 34, "font-size": 11, fill: COL.faint }, "combined similarity (z)  ·  vertical axis is the number of pairs, log scale"));
    s.append(sv("line", { x1: x(R.T), x2: x(R.T), y1: 20, y2: H - B, stroke: COL.rust, "stroke-dasharray": "5 4" }));
    s.append(sv("text", { x: x(R.T) + 6, y: 30, "font-size": 11, fill: COL.rust }, `match threshold ${fmt(R.T)}`));
    for (const p of D.fidelity.pairs) if (p.z_catalog !== undefined) {
      s.append(sv("line", { x1: x(p.z_catalog), x2: x(p.z_catalog), y1: H - B - 26, y2: H - B - 4, stroke: COL.copper, "stroke-width": 1.5 }));
    }
    s.append(sv("text", { x: x(1.3), y: H - B - 32, "font-size": 11, fill: COL.copper }, "the 24 chart pairs' catalogue signs"));
    box.append(s);
  })();

  // ---------- small panel ----------
  (function () {
    const box = document.getElementById("fig-small");
    const rows = smallSorted; const W = 1040, H = 330, L = 30;
    const s = svg(W, H);
    const xs = rows.map(r => r[1].mean); const lo = Math.min(...xs), hi = Math.max(...xs);
    const x = v => L + (v - lo) / (hi - lo) * (W - L - 30);
    s.append(sv("line", { x1: L, x2: W - 30, y1: 180, y2: 180, stroke: COL.rule }));
    for (let v = Math.ceil(lo * 2) / 2; v <= hi; v += .5) { s.append(sv("line", { x1: x(v), x2: x(v), y1: 176, y2: 184, stroke: COL.faint })); s.append(sv("text", { x: x(v), y: 200, "text-anchor": "middle", "font-size": 11, fill: COL.faint }, fmt(v, 1))); }
    const placed = [];
    const items = rows.map(([k, v]) => ({ pair: k, mean: v.mean, x: x(v.mean), rel: isRelated(k), target: k === "indus|rongorongo" })).sort((a, b) => a.x - b.x);
    for (const it of items) {
      let dy = 0, tries = 0; const collide = yy => placed.some(p => Math.abs(p.x - it.x) < 8 && Math.abs(p.y - yy) < 8);
      while (collide(180 + dy) && tries < 40) { tries++; dy = (tries % 2 ? 1 : -1) * Math.ceil(tries / 2) * 8; }
      it.y = 180 + dy; placed.push(it);
    }
    for (const it of placed) {
      const c = it.target ? COL.copper : it.rel ? COL.moss : COL.faint;
      const d = sv("circle", { cx: it.x, cy: it.y, r: it.target || it.rel ? 5.5 : 3.5, fill: c, "fill-opacity": it.target || it.rel ? 1 : .45, stroke: "#fff", "stroke-width": .8 });
      d.append(sv("title", {}, `${label(it.pair.split("|")[0])} × ${label(it.pair.split("|")[1])}: ${fmt(it.mean, 2)}`)); s.append(d);
    }
    const tgt = placed.find(p => p.target);
    s.append(sv("line", { x1: tgt.x, x2: tgt.x, y1: tgt.y - 8, y2: 40, stroke: COL.copper }));
    s.append(sv("text", { x: tgt.x, y: 32, "text-anchor": "middle", "font-size": 12, fill: COL.copper }, `Indus × rongorongo ${fmt(tgt.mean, 2)}, rank ${vals.small_rank} of 276`));
    // label the top related pairs
    let n = 0; for (const it of placed.slice().reverse()) { if (it.rel && n < 5) { n++; s.append(sv("text", { x: it.x, y: 236 + (n - 1) * 15, "text-anchor": "end", "font-size": 10.5, fill: COL.moss }, `${label(it.pair.split("|")[0])} × ${label(it.pair.split("|")[1])} ${fmt(it.mean, 2)}`)); s.append(sv("line", { x1: it.x, x2: it.x, y1: it.y + 6, y2: 224 + (n - 1) * 15, stroke: COL.moss, "stroke-width": .7 })); } }
    s.append(sv("text", { x: L, y: 320, "font-size": 11, fill: COL.faint }, "best-8 score at 22 signs per script, 40 repeats; 276 pairs of all 24 scripts"));
    box.append(s);
    box.append(el("div", { class: "legend" }, el("span", {}, el("i", { style: `background:${COL.copper}` }), "Indus × rongorongo"), el("span", {}, el("i", { style: `background:${COL.moss}` }), "documented relatives"), el("span", {}, el("i", { style: `background:${COL.faint}` }), "other pairs")));
  })();

  // ---------- inventories ----------
  for (const s of ["indus", "rongorongo"]) {
    const box = document.getElementById("inv-" + s); document.getElementById("n-" + s).textContent = `${D.inventories[s].length} signs`;
    for (const g of D.inventories[s]) {
      const c = el("div", { class: "cell" }); const gl = glyph(s, g.id);
      gl.title = `${label(s)} ${g.id}: skeleton length ${g.length}, ${g.endpoints} endpoints, ${g.junctions} junctions, ${g.loops} loops`;
      gl.addEventListener("mouseenter", () => { gl.querySelector("img").src = `img/n/${s}/${g.id}.png`; gl.classList.add("skel"); });
      gl.addEventListener("mouseleave", () => { gl.querySelector("img").src = `img/g/${s}/${g.id}.png`; gl.classList.remove("skel"); });
      c.append(gl, el("div", { class: "lbl" }, g.id)); box.append(c);
    }
  }
})();
