(async function () {
  { const o = new URLSearchParams(location.search).get("off"); if (o) document.body.style.marginTop = (-parseInt(o, 10)) + "px"; }
  const D = await (await fetch("data/site.json")).json();
  const R = D.results, T = R.traditions;
  const el = (tag, attrs = {}, ...kids) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)) { if (k === "class") e.className = v; else if (k === "html") e.innerHTML = v; else e.setAttribute(k, v); } for (const k of kids) if (k != null) e.append(k); return e; };
  const NS = "http://www.w3.org/2000/svg";
  const sv = (tag, attrs = {}, text) => { const e = document.createElementNS(NS, tag); for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v); if (text != null) e.textContent = text; return e; };
  const svg = (w, h) => { const s = sv("svg", { viewBox: `0 0 ${w} ${h}`, width: "100%" }); s.style.maxWidth = w + "px"; s.style.display = "block"; return s; };
  const COL = { ink: "#201b12", soft: "#4c453a", faint: "#877e6c", rule: "#d9d0be", copper: "#9a5b33", moss: "#47705f", rust: "#8e4a38", slate: "#5d6672", gold: "#96731f" };
  const pct = x => (100 * x).toFixed(0) + "%";
  const ord = n => { n = Math.round(n); const s = ["th", "st", "nd", "rd"], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); };
  const CL = { bird_people: "Bird-people", cosmic_serpent: "Cosmic serpent", world_centre: "World centre" };
  const KEY = { bird_people: "b", cosmic_serpent: "s", world_centre: "c" };

  // numbers in prose
  const vals = {
    rate_b: pct(R.rates.bird_people), rate_s: pct(R.rates.cosmic_serpent), rate_c: pct(R.rates.world_centre),
    bundle_count: R.bundle_count, indep: R.independence_expected.toFixed(0), curve_mean: R.curveball.mean.toFixed(0), curve_sd: R.curveball.sd.toFixed(0),
    surprise_rank: R.surprise.rank.toLocaleString(), named_bundle: R.named_test.observed_bundle, named_p: pct(R.named_test.matched_p_ge),
    matched_mean: R.named_test.matched_mean.toFixed(2), random_mean: R.named_test.random_mean.toFixed(2),
    serpent_pct: (100 * R.geography.cosmic_serpent.moran_pct).toFixed(0), bird_pct: (100 * R.geography.bird_people.moran_pct).toFixed(0),
    doc_bundle: R.doc_median_bundle.toFixed(0), doc_all: R.doc_median_all.toFixed(0),
  };
  document.querySelectorAll("[data-v]").forEach(e => { if (vals[e.dataset.v] !== undefined) e.textContent = vals[e.dataset.v]; });

  // ---------- maps ----------
  const W = 1040, H = 520;
  const px = lon => (lon + 180) / 360 * W, py = lat => (90 - lat) / 180 * H;
  const AREA_COL = ["#9a5b33", "#47705f", "#5d6672", "#96731f", "#8e4a38", "#6b7a3a", "#7a5a8a", "#3f6f8a", "#b06a3e", "#4c453a", "#877e6c", "#2f6b5e", "#a3473c", "#5b6a9c", "#7f6a2c", "#3a5f52"];
  function baseMap() {
    const s = svg(W, H); s.classList.add("map");
    s.append(sv("rect", { x: 0, y: 0, width: W, height: H, fill: "#f6f1e8" }));
    for (const line of D.coast) {
      let dpath = "";
      line.forEach(([lon, lat], i) => { dpath += (i ? "L" : "M") + px(lon).toFixed(1) + " " + py(lat).toFixed(1); });
      s.append(sv("path", { d: dpath, class: "coast" }));
    }
    return s;
  }
  (function () {
    const s = baseMap();
    for (const t of T) {
      const c = sv("circle", { cx: px(t.lon), cy: py(t.lat), r: 1.6 + Math.sqrt(t.n) / 3, fill: AREA_COL[(parseInt(t.area, 10) - 1) % 16], "fill-opacity": .75, class: "dot" });
      c.append(sv("title", {}, `${t.name}: ${t.n} motifs (${D.areas[t.area]})`)); s.append(c);
    }
    document.getElementById("map-all").append(s);
  })();
  const mapBox = document.getElementById("map-class"), ctrl = document.getElementById("map-controls"), cap = document.getElementById("map-cap");
  let current = "bird_people";
  function drawClass(k) {
    mapBox.innerHTML = ""; const s = baseMap();
    const has = t => k === "bundle" ? (t.b && t.s && t.c) : t[KEY[k]];
    for (const t of T) if (!has(t)) s.append(sv("circle", { cx: px(t.lon), cy: py(t.lat), r: 1.8, fill: COL.faint, "fill-opacity": .35, class: "dot" }));
    for (const t of T) if (has(t)) { const c = sv("circle", { cx: px(t.lon), cy: py(t.lat), r: 3.6, fill: COL.copper, "fill-opacity": .9, class: "dot" }); c.append(sv("title", {}, `${t.name} (${D.areas[t.area]})`)); s.append(c); }
    mapBox.append(s);
    const n = T.filter(has).length;
    cap.innerHTML = `<b>${k === "bundle" ? "All three classes together" : CL[k]}: ${n} of 926 traditions (${pct(n / 926)}).</b> Copper dots have the ${k === "bundle" ? "bundle" : "class"}; grey dots are documented traditions without it.`;
    ctrl.querySelectorAll(".btn").forEach(b => b.classList.toggle("on", b.dataset.k === k));
  }
  for (const k of ["bird_people", "cosmic_serpent", "world_centre", "bundle"]) {
    const b = el("button", { class: "btn", "data-k": k }, k === "bundle" ? "All three" : CL[k]); b.addEventListener("click", () => drawClass(k)); ctrl.append(b);
  }
  drawClass(current);

  // ---------- class tables ----------
  (function () {
    const box = document.getElementById("class-tables");
    for (const [k, list] of Object.entries(D.classes)) {
      const kept = list.filter(x => !x.excluded), exc = list.filter(x => x.excluded);
      box.append(el("h3", {}, `${CL[k]}: ${kept.length} motifs, ${exc.length} excluded, present in ${pct(R.rates[k])} of traditions`));
      const t = el("table", { class: "inv" });
      t.append(el("tr", {}, el("th", {}, "Code"), el("th", {}, "Motif"), el("th", {}, "Definition"), el("th", {}, "Traditions")));
      for (const x of kept.sort((a, b) => b.n - a.n)) t.append(el("tr", {}, el("td", { class: "mono" }, x.code), el("td", {}, x.name), el("td", { class: "desc" }, x.description), el("td", { class: "n" }, String(x.n))));
      for (const x of exc) t.append(el("tr", { style: "opacity:.55" }, el("td", { class: "mono" }, el("s", {}, x.code)), el("td", {}, el("s", {}, x.name)), el("td", { class: "desc" }, "Excluded: " + x.excluded), el("td", { class: "n" }, String(x.n))));
      box.append(el("div", { class: "frame plain", style: "margin-bottom:26px" }, t));
    }
  })();

  // ---------- curveball histogram ----------
  (function () {
    const box = document.getElementById("fig-curveball"); const h = R.curveball.hist; const lo = 60, hi = 220; const Wc = 1040, Hc = 240, L = 40, B = 50;
    const s = svg(Wc, Hc); const x = v => L + (v - lo) / (hi - lo) * (Wc - L - 20); const maxc = Math.max(...h); const y = c => Hc - B - c / maxc * (Hc - B - 30);
    h.forEach((c, i) => { if (c > 0 && i >= lo && i <= hi) s.append(sv("rect", { x: x(i), y: y(c), width: Math.max(1, x(i + 1) - x(i) - .5), height: Hc - B - y(c), fill: COL.faint, "fill-opacity": .6 })); });
    for (let v = lo; v <= hi; v += 20) s.append(sv("text", { x: x(v), y: Hc - B + 16, "text-anchor": "middle", "font-size": 11, fill: COL.faint }, String(v)));
    s.append(sv("line", { x1: x(R.bundle_count), x2: x(R.bundle_count), y1: 20, y2: Hc - B, stroke: COL.copper, "stroke-width": 2 }));
    s.append(sv("text", { x: x(R.bundle_count) - 6, y: 32, "text-anchor": "end", "font-size": 12, fill: COL.copper }, `observed ${R.bundle_count}`));
    s.append(sv("line", { x1: x(R.independence_expected), x2: x(R.independence_expected), y1: 20, y2: Hc - B, stroke: COL.slate, "stroke-dasharray": "4 4" }));
    s.append(sv("text", { x: x(R.independence_expected) - 6, y: 50, "text-anchor": "end", "font-size": 11, fill: COL.slate }, `independence ${R.independence_expected.toFixed(0)}`));
    s.append(sv("text", { x: x(R.curveball.mean), y: 32, "text-anchor": "start", "font-size": 11, fill: COL.faint }, `  documentation-preserving null ${R.curveball.mean.toFixed(0)} ± ${R.curveball.sd.toFixed(0)}`));
    s.append(sv("text", { x: L, y: Hc - B + 34, "font-size": 11, fill: COL.faint }, "number of traditions with all three classes"));
    box.append(s);
  })();

  // ---------- surprise strip ----------
  (function () {
    const box = document.getElementById("fig-surprise"); const q = R.surprise.random_excess_quantiles; const Wc = 1040, Hc = 120, L = 40;
    const lo = 0, hi = 16; const x = v => L + (v - lo) / (hi - lo) * (Wc - L - 20); const s = svg(Wc, Hc);
    s.append(sv("line", { x1: x(q[0]), x2: x(q[4]), y1: 50, y2: 50, stroke: COL.faint, "stroke-width": 2 }));
    s.append(sv("rect", { x: x(q[1]), y: 38, width: x(q[3]) - x(q[1]), height: 24, fill: COL.faint, "fill-opacity": .35 }));
    s.append(sv("line", { x1: x(q[2]), x2: x(q[2]), y1: 34, y2: 66, stroke: COL.ink, "stroke-width": 2 }));
    s.append(sv("circle", { cx: x(R.surprise.real_excess), cy: 50, r: 7, fill: COL.copper }));
    s.append(sv("text", { x: x(R.surprise.real_excess), y: 26, "text-anchor": "middle", "font-size": 12, fill: COL.copper }, `real bundle ${R.surprise.real_excess.toFixed(1)} · rank ${R.surprise.rank.toLocaleString()} of 5,000`));
    s.append(sv("text", { x: x(q[2]), y: 84, "text-anchor": "middle", "font-size": 11, fill: COL.soft }, `random bundles: median ${q[2].toFixed(1)}, box 25–75%, whisker 5–95%`));
    for (let v = lo; v <= hi; v += 4) s.append(sv("text", { x: x(v), y: 108, "text-anchor": "middle", "font-size": 11, fill: COL.faint }, String(v)));
    box.append(s);
  })();

  // ---------- named table ----------
  (function () {
    const t = document.getElementById("named-table");
    t.append(el("tr", {}, el("th", {}, "Culture"), el("th", {}, "Catalogue tradition"), el("th", {}, "Bird-people"), el("th", {}, "Cosmic serpent"), el("th", {}, "World centre"), el("th", {}, "All three"), el("th", {}, "Motifs coded")));
    const names = { "Sumer": "Sumer", "Akkad / Assyria / Babylon": "Akkad, Assiria, Babylon", "Ancient Egypt": "Ancient Egypt", "Hittite / Hurrian": "Hittite, Hurrit", "Aztec": "Aztec", "Yucatec Maya": "Yucatec, Itza", "Kechua (Cuzco region)": "Kechua: South Peru, Bolivia", "Easter Island": "Easter Island" };
    const yes = v => el("td", { class: "mono", style: `color:${v ? "var(--copper)" : "var(--faint)"}` }, v ? "yes" : "–");
    for (const [lab, v] of Object.entries(R.named)) t.append(el("tr", { class: v.bundle ? "hl" : "" }, el("td", {}, lab), el("td", { class: "mono" }, names[lab] || lab), yes(v.bird_people), yes(v.cosmic_serpent), yes(v.world_centre), yes(v.bundle), el("td", { class: "n" }, String(v.n_motifs))));
  })();

  // ---------- geography ----------
  (function () {
    const box = document.getElementById("fig-geo"); const G = R.geography; const rows = ["bird_people", "cosmic_serpent", "world_centre", "bundle"];
    const Wc = 1040, Hc = 230, L = 160; const lo = -0.05, hi = 0.4; const x = v => L + (v - lo) / (hi - lo) * (Wc - L - 30); const s = svg(Wc, Hc);
    rows.forEach((k, i) => {
      const g = G[k]; const y = 16 + i * 46;
      s.append(sv("text", { x: L - 10, y: y + 14, "text-anchor": "end", "font-size": 12, fill: COL.soft }, k === "bundle" ? "All three" : CL[k]));
      s.append(sv("line", { x1: x(g.moran_null_mean - 2 * g.moran_null_sd), x2: x(g.moran_null_mean + 2 * g.moran_null_sd), y1: y + 10, y2: y + 10, stroke: COL.faint, "stroke-width": 2 }));
      s.append(sv("line", { x1: x(g.moran_null_mean), x2: x(g.moran_null_mean), y1: y + 2, y2: y + 18, stroke: COL.faint }));
      s.append(sv("rect", { x: x(lo), y: y + 4, width: Math.max(0, x(g.moran) - x(lo)), height: 12, fill: COL.copper, "fill-opacity": .85 }));
      s.append(sv("text", { x: x(lo) + 4, y: y + 30, "font-size": 10.5, fill: COL.soft }, `I = ${g.moran.toFixed(2)} · ${ord(100 * g.moran_pct)} percentile of random motif sets`));
    });
    for (let v = 0; v <= hi; v += 0.1) s.append(sv("text", { x: x(v), y: Hc - 6, "text-anchor": "middle", "font-size": 11, fill: COL.faint }, v.toFixed(1)));
    s.append(sv("text", { x: L, y: Hc - 22, "font-size": 11, fill: COL.faint }, "Moran's I over ten nearest neighbours · grey whisker: random motif sets of equal frequency, mean ± 2 sd"));
    box.append(s);
  })();

  // ---------- bundle list ----------
  (function () {
    const box = document.getElementById("bundle-list"); const by = {};
    for (const t of T) if (t.b && t.s && t.c) (by[t.area] = by[t.area] || []).push(t.name);
    for (const a of Object.keys(by).sort((p, q) => parseInt(p) - parseInt(q))) box.append(el("p", {}, el("b", {}, D.areas[a] + " (" + by[a].length + "): "), by[a].join(", ")));
  })();
})();
