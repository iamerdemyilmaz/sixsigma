/*
 * calculators.js - calculator user interfaces and inline-SVG charts for the
 * course. All statistics come from the engines in stats.js (global `Stats`),
 * which are tested against scipy and against verification/results/ by
 * verification/test_calculators.js. This file only parses input, calls the
 * engines, formats the output and draws SVG. Vanilla JavaScript, no
 * dependencies, works from file://.
 *
 * Markup contract (one per calculator instance):
 *   <div class="calc" data-calc="capability" id="calc-cap">
 *     <script type="application/json" class="calc-data">{ ...preloaded data... }</script>
 *   </div>
 * Calc.mountAll() (run on DOMContentLoaded) builds the UI inside every
 * [data-calc] element and computes once with the preloaded data so that the
 * learner sees the calculator agree with the page. Available types:
 *   descriptive, capability, dpmo, control, grr, tests, samplesize,
 *   factorial, simulator
 */
(function (root) {
  "use strict";
  var S = root.Stats;
  var Calc = {};

  // ------------------------------------------------------------------ utils
  function el(tag, attrs, children) {
    var e = document.createElement(tag);
    if (attrs) { Object.keys(attrs).forEach(function (k) { if (k === "text") { e.textContent = attrs[k]; } else if (k === "html") { e.innerHTML = attrs[k]; } else { e.setAttribute(k, attrs[k]); } }); }
    if (children) { children.forEach(function (c) { if (c === null || c === undefined) { return; } e.appendChild(typeof c === "string" ? document.createTextNode(c) : c); }); }
    return e;
  }
  var SVGNS = "http://www.w3.org/2000/svg";
  function svg(tag, attrs, children) {
    var e = document.createElementNS(SVGNS, tag);
    if (attrs) { Object.keys(attrs).forEach(function (k) { if (k === "text") { e.textContent = attrs[k]; } else { e.setAttribute(k, attrs[k]); } }); }
    if (children) { children.forEach(function (c) { if (c) { e.appendChild(c); } }); }
    return e;
  }
  function has(v) { return v !== null && v !== undefined && !(typeof v === "number" && isNaN(v)); }
  function fmt(v, dp) {
    if (!has(v)) { return "–"; }
    if (!isFinite(v)) { return v > 0 ? "∞" : "−∞"; }
    var s = Number(v).toFixed(dp);
    if (Math.abs(v) >= 10000) { s = Number(v).toFixed(dp).replace(/\B(?=(\d{3})+(?!\d))/g, ","); }
    return s.replace("-", "−");
  }
  function fmtP(p) {
    if (!has(p)) { return "–"; }
    if (p < 0.0005) { return "< 0.001"; }
    return p.toFixed(3);
  }
  function fmtPpm(v) { if (!has(v)) { return "–"; } return v < 1 ? v.toFixed(2) : (v < 100 ? v.toFixed(1) : fmt(v, 0)); }
  function autoDp(values) {
    // decimals needed to show the data at its own resolution, plus one
    var maxd = 0;
    values.forEach(function (v) { var s = String(v); var i = s.indexOf("."); if (i >= 0) { maxd = Math.max(maxd, s.length - i - 1); } });
    return Math.min(6, maxd + 1);
  }
  function parseRows(text) {
    return String(text).split(/\r?\n/).map(function (line) { return line.trim(); }).filter(function (l) { return l.length; })
      .map(function (line) { return line.split(/[\s,;]+/).filter(function (t) { return t.length; }); });
  }
  function toNum(t) { var v = Number(String(t).replace(/−/g, "-")); return isNaN(v) ? null : v; }
  function numsOf(text) { return S.parseNumbers(text); }
  function optNum(input) { var s = String(input.value).trim().replace(",", "."); if (s === "") { return null; } var v = Number(s); return isNaN(v) ? null : v; }
  function joinRows(rows, sep) { return rows.map(function (r) { return r.join(sep || "  "); }).join("\n"); }

  // form controls
  function field(label, control, opts) {
    var l = el("label", null, [el("span", { text: label }), control]);
    if (opts && opts.title) { l.title = opts.title; }
    return l;
  }
  function num(name, value, attrs) {
    var a = { type: "number", name: name, step: "any" };
    if (attrs) { Object.keys(attrs).forEach(function (k) { a[k] = attrs[k]; }); }
    var i = el("input", a);
    if (has(value)) { i.value = value; }
    return i;
  }
  function select(name, options, value) {
    var s = el("select", { name: name });
    options.forEach(function (o) { var op = el("option", { value: o[0], text: o[1] }); if (o[0] === String(value)) { op.selected = true; } s.appendChild(op); });
    return s;
  }
  function textarea(name, value, rows) {
    var t = el("textarea", { name: name, rows: rows || 6, spellcheck: "false" });
    t.value = value || "";
    return t;
  }
  function check(name, label, checked) {
    var i = el("input", { type: "checkbox", name: name });
    i.checked = !!checked;
    return el("label", { "class": "check" }, [i, label]);
  }
  function button(text, cls) { return el("button", { type: "button", "class": cls || "", text: text }); }
  function table(caption, headers, rows, cls) {
    var t = el("table", { "class": cls || "" });
    if (caption) { t.appendChild(el("caption", { text: caption })); }
    var thead = el("thead"), tr = el("tr");
    headers.forEach(function (h) { tr.appendChild(el("th", { text: h, "class": /^[\d.\-–−]+$/.test(h) ? "num" : "" })); });
    thead.appendChild(tr); t.appendChild(thead);
    var tb = el("tbody");
    rows.forEach(function (r) {
      var trr = el("tr");
      r.forEach(function (c, i) {
        var td = el("td");
        if (c && typeof c === "object" && c.nodeType) { td.appendChild(c); }
        else if (c && typeof c === "object") { td.textContent = c.text; if (c.cls) { td.className = c.cls; } }
        else { td.textContent = c; if (i > 0 && /^[\s\d.,\-–−<∞%]+$/.test(String(c))) { td.className = "num"; } }
        trr.appendChild(td);
      });
      tb.appendChild(trr);
    });
    t.appendChild(tb);
    return el("div", { "class": "table-wrap" }, [t]);
  }
  function msg(text, cls) { return el("p", { "class": "msg " + (cls || ""), text: text }); }
  function note(html) { return el("p", { "class": "note", html: html }); }
  function h4(text) { return el("h4", { text: text }); }
  function outBox(node) {
    var o = node.querySelector(".calc-out");
    if (!o) { o = el("div", { "class": "calc-out", "aria-live": "polite" }); node.appendChild(o); }
    while (o.firstChild) { o.removeChild(o.firstChild); }
    return o;
  }
  function readData(node) {
    var s = node.querySelector("script.calc-data");
    if (!s) { return {}; }
    try { return JSON.parse(s.textContent); } catch (e) { return {}; }
  }
  function ruleNames() {
    return { we1: "WE 1: one point beyond 3σ", we2: "WE 2: two of three beyond 2σ (same side)", we3: "WE 3: four of five beyond 1σ (same side)", we4: "WE 4: eight in a row on one side",
      n2: "Nelson 2: nine in a row on one side", n3: "Nelson 3: six in a row steadily rising or falling", n4: "Nelson 4: fourteen in a row alternating", n7: "Nelson 7: fifteen in a row within 1σ", n8: "Nelson 8: eight in a row beyond 1σ (either side)" };
  }
  function listRules(rules, filter) {
    var names = ruleNames(), items = [];
    Object.keys(names).forEach(function (k) {
      if (filter && filter.indexOf(k) < 0) { return; }
      if (rules[k] && rules[k].length) { items.push(names[k] + " at " + rules[k].join(", ")); }
    });
    return items;
  }

  // --------------------------------------------------------------- scales
  function scale(d0, d1, r0, r1) { var f = function (v) { return r0 + (v - d0) * (r1 - r0) / (d1 - d0); }; f.d0 = d0; f.d1 = d1; return f; }
  function niceStep(span, n) {
    var raw = span / Math.max(1, n), p = Math.pow(10, Math.floor(Math.log(raw) / Math.LN10)), m = raw / p;
    var step = m < 1.5 ? 1 : (m < 3 ? 2 : (m < 7 ? 5 : 10));
    return step * p;
  }
  function ticks(lo, hi, n) {
    var st = niceStep(hi - lo, n), out = [], v = Math.ceil(lo / st) * st;
    for (var i = 0; i < 100 && v <= hi + st * 1e-9; i++) { out.push(Math.round(v / st) * st); v += st; }
    return out;
  }
  function tickLabel(v, st) { var dp = Math.max(0, Math.min(6, -Math.floor(Math.log(st) / Math.LN10 + 1e-9))); return Number(v).toFixed(dp); }
  function figure(svgEl, caption) {
    var f = el("figure", null, [svgEl]);
    if (caption) { f.appendChild(el("figcaption", { html: caption })); }
    return f;
  }

  // ------------------------------------------------------- control chart
  // opts: values, center, ucl, lcl (number or array), signals (1-based index list, red),
  // warn (1-based list, accent), title, desc, ylabel, xlabel, zones (sigma or null)
  function controlChart(o) {
    var W = 660, H = o.height || 230, ml = 62, mr = 70, mt = 26, mb = 34;
    var n = o.values.length;
    var uclA = Array.isArray(o.ucl) ? o.ucl : o.values.map(function () { return o.ucl; });
    var lclA = Array.isArray(o.lcl) ? o.lcl : o.values.map(function () { return o.lcl; });
    var all = o.values.concat(uclA, lclA, [o.center]).filter(has);
    var lo = Math.min.apply(null, all), hi = Math.max.apply(null, all), pad = (hi - lo || 1) * 0.08;
    lo -= pad; hi += pad;
    var x = scale(1, Math.max(n, 2), ml, W - mr), y = scale(lo, hi, H - mb, mt);
    var root = svg("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-labelledby": o.id + "-t " + o.id + "-d", "class": "control-chart" });
    root.appendChild(svg("title", { id: o.id + "-t", text: o.title }));
    root.appendChild(svg("desc", { id: o.id + "-d", text: o.desc || o.title }));
    // axes
    root.appendChild(svg("path", { d: "M" + ml + " " + mt + " V" + (H - mb) + " H" + (W - mr), "class": "chart-axis" }));
    var st = niceStep(hi - lo, 5);
    ticks(lo, hi, 5).forEach(function (t) {
      root.appendChild(svg("line", { x1: ml - 4, x2: ml, y1: y(t), y2: y(t), "class": "chart-axis" }));
      root.appendChild(svg("text", { x: ml - 7, y: y(t) + 4, "text-anchor": "end", "class": "chart-text small", text: tickLabel(t, st) }));
    });
    var xt = n <= 12 ? 1 : (n <= 30 ? 5 : 10);
    for (var i = 1; i <= n; i++) {
      if (i === 1 || i % xt === 0) {
        root.appendChild(svg("line", { x1: x(i), x2: x(i), y1: H - mb, y2: H - mb + 4, "class": "chart-axis" }));
        root.appendChild(svg("text", { x: x(i), y: H - mb + 15, "text-anchor": "middle", "class": "chart-text small", text: String(i) }));
      }
    }
    root.appendChild(svg("text", { x: (ml + W - mr) / 2, y: H - 4, "text-anchor": "middle", "class": "chart-text muted", text: o.xlabel || "Subgroup" }));
    root.appendChild(svg("text", { x: 14, y: (mt + H - mb) / 2, "text-anchor": "middle", transform: "rotate(-90 14 " + ((mt + H - mb) / 2) + ")", "class": "chart-text muted", text: o.ylabel || "" }));
    root.appendChild(svg("text", { x: ml, y: 14, "class": "chart-title", text: o.title }));
    // zones
    if (has(o.zones) && !Array.isArray(o.ucl)) {
      [1, 2, -1, -2].forEach(function (k) {
        var v = o.center + k * o.zones;
        if (v > lo && v < hi) { root.appendChild(svg("line", { x1: ml, x2: W - mr, y1: y(v), y2: y(v), "class": "chart-zone" })); }
      });
    }
    // limits and center
    function path(arr, cls) {
      var d = ""; arr.forEach(function (v, i) { d += (i ? " L" : "M") + x(i + 1) + " " + y(v); });
      return svg("path", { d: d, "class": cls });
    }
    root.appendChild(path(uclA, "chart-limit"));
    if (has(o.lcl)) { root.appendChild(path(lclA, "chart-limit")); }
    root.appendChild(svg("line", { x1: ml, x2: W - mr, y1: y(o.center), y2: y(o.center), "class": "chart-center" }));
    var dpl = o.dp === undefined ? 3 : o.dp;
    root.appendChild(svg("text", { x: W - mr + 5, y: y(uclA[n - 1]) + 4, "class": "chart-text accent small", text: "UCL " + fmt(uclA[n - 1], dpl) }));
    root.appendChild(svg("text", { x: W - mr + 5, y: y(o.center) + 4, "class": "chart-text accent small", text: (o.centerLabel || "CL") + " " + fmt(o.center, dpl) }));
    if (has(o.lcl)) { root.appendChild(svg("text", { x: W - mr + 5, y: y(lclA[n - 1]) + 4, "class": "chart-text accent small", text: "LCL " + fmt(lclA[n - 1], dpl) })); }
    // data
    root.appendChild(path(o.values, "chart-line"));
    var sig = o.signals || [], warn = o.warn || [];
    o.values.forEach(function (v, i) {
      var cls = "chart-point" + (sig.indexOf(i + 1) >= 0 ? " signal" : (warn.indexOf(i + 1) >= 0 ? " warn" : ""));
      root.appendChild(svg("circle", { cx: x(i + 1), cy: y(v), r: 3.2, "class": cls }));
    });
    if (o.baseline && o.baseline < n) {
      root.appendChild(svg("line", { x1: x(o.baseline + 0.5), x2: x(o.baseline + 0.5), y1: mt, y2: H - mb, "class": "chart-spec" }));
      root.appendChild(svg("text", { x: x(o.baseline + 0.5) + 3, y: mt + 10, "class": "chart-text small muted", text: "limits frozen here" }));
    }
    return root;
  }

  // ----------------------------------------------------------- histogram
  // opts: edges, counts, usl, lsl, target, mean, sigma (normal curve), n, xlabel, title, desc, id, dp
  function histogram(o) {
    var W = 660, H = 250, ml = 48, mr = 20, mt = 26, mb = 40;
    var lo = o.edges[0], hi = o.edges[o.edges.length - 1];
    [o.usl, o.lsl, o.target].forEach(function (v) { if (has(v)) { lo = Math.min(lo, v); hi = Math.max(hi, v); } });
    if (has(o.mean) && has(o.sigma)) { lo = Math.min(lo, o.mean - 3.5 * o.sigma); hi = Math.max(hi, o.mean + 3.5 * o.sigma); }
    var pad = (hi - lo) * 0.05; lo -= pad; hi += pad;
    var maxc = Math.max.apply(null, o.counts);
    var binw = o.edges[1] - o.edges[0];
    var curveMax = has(o.sigma) ? o.n * binw * S.normPdf(0) / o.sigma : 0;
    var ymax = Math.max(maxc, curveMax) * 1.1;
    var x = scale(lo, hi, ml, W - mr), y = scale(0, ymax, H - mb, mt);
    var root = svg("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-labelledby": o.id + "-t " + o.id + "-d" });
    root.appendChild(svg("title", { id: o.id + "-t", text: o.title }));
    root.appendChild(svg("desc", { id: o.id + "-d", text: o.desc || o.title }));
    root.appendChild(svg("path", { d: "M" + ml + " " + mt + " V" + (H - mb) + " H" + (W - mr), "class": "chart-axis" }));
    var st = niceStep(hi - lo, 7);
    ticks(lo, hi, 7).forEach(function (t) {
      root.appendChild(svg("line", { x1: x(t), x2: x(t), y1: H - mb, y2: H - mb + 4, "class": "chart-axis" }));
      root.appendChild(svg("text", { x: x(t), y: H - mb + 15, "text-anchor": "middle", "class": "chart-text small", text: tickLabel(t, st) }));
    });
    var yst = niceStep(ymax, 4);
    ticks(0, ymax, 4).forEach(function (t) {
      root.appendChild(svg("line", { x1: ml - 4, x2: ml, y1: y(t), y2: y(t), "class": "chart-axis" }));
      root.appendChild(svg("text", { x: ml - 7, y: y(t) + 4, "text-anchor": "end", "class": "chart-text small", text: tickLabel(t, yst) }));
    });
    root.appendChild(svg("text", { x: (ml + W - mr) / 2, y: H - 6, "text-anchor": "middle", "class": "chart-text muted", text: o.xlabel || "" }));
    root.appendChild(svg("text", { x: 12, y: (mt + H - mb) / 2, "text-anchor": "middle", transform: "rotate(-90 12 " + ((mt + H - mb) / 2) + ")", "class": "chart-text muted", text: "Count" }));
    root.appendChild(svg("text", { x: ml, y: 14, "class": "chart-title", text: o.title }));
    o.counts.forEach(function (c, i) {
      root.appendChild(svg("rect", { x: x(o.edges[i]), y: y(c), width: Math.max(0, x(o.edges[i + 1]) - x(o.edges[i])), height: y(0) - y(c), "class": "chart-bar" }));
    });
    if (has(o.sigma) && o.sigma > 0) {
      var d = "";
      for (var i = 0; i <= 120; i++) {
        var xv = lo + (hi - lo) * i / 120, yv = o.n * binw * S.normPdf((xv - o.mean) / o.sigma) / o.sigma;
        d += (i ? " L" : "M") + x(xv).toFixed(1) + " " + y(yv).toFixed(1);
      }
      root.appendChild(svg("path", { d: d, "class": "chart-curve" }));
    }
    var dpl = o.dp === undefined ? 3 : o.dp;
    function vline(v, cls, label, dy) {
      if (!has(v)) { return; }
      root.appendChild(svg("line", { x1: x(v), x2: x(v), y1: mt + 4, y2: H - mb, "class": cls }));
      root.appendChild(svg("text", { x: x(v), y: mt + dy, "text-anchor": "middle", "class": "chart-text small " + (cls === "chart-spec" ? "bad" : ""), text: label + " " + fmt(v, dpl) }));
    }
    vline(o.lsl, "chart-spec", "LSL", 0); vline(o.usl, "chart-spec", "USL", 0); vline(o.target, "chart-target", "T", 12);
    if (has(o.mean)) { vline(o.mean, "chart-center", "x̄", 38); }
    return root;
  }

  // --------------------------------------------------------------- bars
  function barChart(o) {
    // horizontal bars, o.items = [{label, value}], sorted by |value| desc if o.sort
    var items = o.items.slice();
    if (o.sort) { items.sort(function (a, b) { return Math.abs(b.value) - Math.abs(a.value); }); }
    var W = 660, rowH = 26, ml = 90, mr = 80, mt = 26, mb = 30, H = mt + mb + rowH * items.length;
    var maxv = Math.max.apply(null, items.map(function (i) { return Math.abs(i.value); })) || 1;
    var x = scale(0, maxv, ml, W - mr);
    var root = svg("svg", { viewBox: "0 0 " + W + " " + H, role: "img", "aria-labelledby": o.id + "-t " + o.id + "-d" });
    root.appendChild(svg("title", { id: o.id + "-t", text: o.title }));
    root.appendChild(svg("desc", { id: o.id + "-d", text: o.desc || o.title }));
    root.appendChild(svg("text", { x: ml, y: 14, "class": "chart-title", text: o.title }));
    items.forEach(function (it, i) {
      var yy = mt + i * rowH;
      root.appendChild(svg("text", { x: ml - 8, y: yy + 17, "text-anchor": "end", "class": "chart-text", text: it.label }));
      root.appendChild(svg("rect", { x: ml, y: yy + 5, width: x(Math.abs(it.value)) - ml, height: rowH - 10, "class": "chart-bar" + (it.dim ? " dim" : "") }));
      root.appendChild(svg("text", { x: x(Math.abs(it.value)) + 5, y: yy + 17, "class": "chart-text small", text: fmt(it.value, o.dp === undefined ? 3 : o.dp) }));
    });
    if (has(o.refLine) && o.refLine <= maxv) {
      root.appendChild(svg("line", { x1: x(o.refLine), x2: x(o.refLine), y1: mt, y2: H - mb, "class": "chart-spec" }));
      root.appendChild(svg("text", { x: x(o.refLine), y: H - mb + 14, "text-anchor": "middle", "class": "chart-text small bad", text: o.refLabel || "" }));
    }
    root.appendChild(svg("path", { d: "M" + ml + " " + mt + " V" + (H - mb), "class": "chart-axis" }));
    return root;
  }

  // ------------------------------------------------------ shared: charts
  // Draw the stability charts for a capability result (I-MR or Xbar-R/S)
  function stabilityCharts(cap, units, dp, idp) {
    var ch = cap.chart, out = [];
    var we = ["we1", "we2", "we3", "we4"];
    function warnList(rules) { var w = []; we.slice(1).forEach(function (k) { (rules[k] || []).forEach(function (i) { if (w.indexOf(i) < 0) { w.push(i); } }); }); return w; }
    if (cap.chart_type === "imr") {
      out.push(figure(controlChart({ id: idp + "-i", values: cap.x, center: ch.xbar, ucl: ch.ucl_x, lcl: ch.lcl_x, signals: ch.rules_x.we1, warn: warnList(ch.rules_x), zones: ch.sigma_within, dp: dp,
        title: "Individuals chart", desc: "Individual values with centre line and 3-sigma limits computed from the average moving range.", ylabel: "Value" + (units ? " (" + units + ")" : ""), xlabel: "Observation", centerLabel: "x̄" })));
      out.push(figure(controlChart({ id: idp + "-mr", values: ch.mr, center: ch.mrbar, ucl: ch.ucl_mr, lcl: null, signals: ch.beyond_mr, dp: dp,
        title: "Moving range chart", desc: "Moving ranges of successive values with centre line and upper limit D4 times the average moving range.", ylabel: "Moving range" + (units ? " (" + units + ")" : ""), xlabel: "Observation", centerLabel: "MR̄" })));
    } else if (cap.chart_type === "xbar_s") {
      out.push(figure(controlChart({ id: idp + "-x", values: ch.means, center: ch.xbarbar, ucl: ch.ucl_x, lcl: ch.lcl_x, signals: ch.rules_x.we1, warn: warnList(ch.rules_x), zones: ch.A3 * ch.sbar / 3, dp: dp,
        title: "X̄ chart (limits from S̄)", desc: "Subgroup means with centre line and limits x̄̄ ± A3·S̄.", ylabel: "Subgroup mean" + (units ? " (" + units + ")" : ""), centerLabel: "x̄̄" })));
      out.push(figure(controlChart({ id: idp + "-s", values: ch.sds, center: ch.sbar, ucl: ch.ucl_s, lcl: ch.B3 > 0 ? ch.lcl_s : null, signals: ch.beyond_s, dp: dp,
        title: "S chart", desc: "Subgroup standard deviations with limits B3·S̄ and B4·S̄.", ylabel: "Subgroup s" + (units ? " (" + units + ")" : ""), centerLabel: "S̄" })));
    } else {
      out.push(figure(controlChart({ id: idp + "-x", values: ch.means, center: ch.xbarbar, ucl: ch.ucl_x, lcl: ch.lcl_x, signals: ch.rules_x.we1, warn: warnList(ch.rules_x), zones: ch.A2 * ch.rbar / 3, dp: dp,
        title: "X̄ chart (limits from R̄)", desc: "Subgroup means with centre line and limits x̄̄ ± A2·R̄.", ylabel: "Subgroup mean" + (units ? " (" + units + ")" : ""), centerLabel: "x̄̄" })));
      out.push(figure(controlChart({ id: idp + "-r", values: ch.ranges, center: ch.rbar, ucl: ch.ucl_r, lcl: ch.D3 > 0 ? ch.lcl_r : null, signals: ch.beyond_r, dp: dp,
        title: "R chart", desc: "Subgroup ranges with limits D3·R̄ and D4·R̄.", ylabel: "Subgroup range" + (units ? " (" + units + ")" : ""), centerLabel: "R̄" })));
    }
    return out;
  }
  function stabilityVerdict(cap) {
    var ch = cap.chart, items = [];
    var primary = listRules(ch.rules_x, ["we1"]);
    var rangeHits = ch.beyond_mr || ch.beyond_r || ch.beyond_s || [];
    var p = el("div");
    if (cap.stable) {
      p.appendChild(msg("Stability: no point beyond the 3-sigma limits on either chart. The process is treated as stable for this study.", "ok"));
    } else {
      var t = "Stability: NOT stable. ";
      if (primary.length) { t += primary.join("; ") + ". "; }
      if (rangeHits.length) { t += "Range or spread chart beyond its limit at " + rangeHits.join(", ") + ". "; }
      p.appendChild(msg(t + "Any capability index below is descriptive of this sample only and does not predict future output.", "bad"));
    }
    var other = listRules(ch.rules_x, ["we2", "we3", "we4", "n2", "n3", "n4", "n7", "n8"]);
    if (other.length) {
      p.appendChild(note("Other run rules that fired on the X̄ or individuals chart (points marked in blue): " + other.join("; ") + ". These are worth a look at the process before you rely on the index; each added rule also raises the false-alarm rate."));
    }
    return p;
  }

  // ================================================================ 1. descriptive
  Calc.descriptive = {
    mount: function (node, data) {
      var f = el("div");
      var ta = textarea("x", (data.x || []).join(" "), 5);
      var usl = num("usl", data.usl), lsl = num("lsl", data.lsl), units = el("input", { type: "text", name: "units", value: data.units || "" });
      f.appendChild(el("div", { "class": "calc-grid wide" }, [field("Data (any separator: space, comma, tab, new line)", ta)]));
      f.appendChild(el("div", { "class": "calc-grid" }, [field("Upper specification (optional)", usl), field("Lower specification (optional)", lsl), field("Units", units)]));
      var run = button("Compute");
      f.appendChild(el("div", { "class": "row" }, [run]));
      node.appendChild(f);
      function compute() {
        var o = outBox(node), x = numsOf(ta.value);
        if (x.length < 2) { o.appendChild(el("p", { "class": "error", text: "Enter at least two numbers." })); return; }
        var d = S.descriptive(x), hgram = S.histogram(x), dp = autoDp(x), u = units.value ? " " + units.value : "";
        var rows = [["n", String(d.n)], ["Mean x̄", fmt(d.mean, dp + 1) + u], ["Median", fmt(d.median, dp) + u], ["Sample standard deviation s (n − 1)", fmt(d.s, dp + 2) + u], ["Variance s²", d.variance.toPrecision(4)],
          ["Minimum", fmt(d.min, dp) + u], ["Maximum", fmt(d.max, dp) + u], ["Range", fmt(d.range, dp) + u], ["First quartile Q1", fmt(d.q1, dp) + u], ["Third quartile Q3", fmt(d.q3, dp) + u],
          ["Skewness (sample, bias-corrected)", fmt(d.skewness, 3)], ["Excess kurtosis (sample, bias-corrected)", fmt(d.kurtosis_excess, 3)], ["Standard error of the mean s/√n", fmt(d.sem, dp + 2) + u]];
        if (has(d.ad_p)) { rows.push(["Anderson-Darling A²", fmt(d.ad_A2, 3)], ["Anderson-Darling p-value (normality)", fmtP(d.ad_p)]); }
        o.appendChild(table("Descriptive statistics", ["Statistic", "Value"], rows));
        var U = optNum(usl), L = optNum(lsl);
        if (has(U) || has(L)) {
          var nout = x.filter(function (v) { return (has(U) && v > U) || (has(L) && v < L); }).length;
          o.appendChild(msg(nout + " of " + x.length + " values outside the specification (" + fmt(100 * nout / x.length, 1) + " %).", nout ? "bad" : "ok"));
        }
        if (has(d.ad_p)) { o.appendChild(note(d.ad_p >= 0.05 ? "Anderson-Darling p ≥ 0.05: no evidence against normality at the 5 % level. That is not proof of normality; look at the histogram and think about the physics." : "Anderson-Darling p < 0.05: the data depart from a normal distribution more than chance would explain. Find out why before using a normal-based index.")); }
        o.appendChild(figure(histogram({ id: node.id + "-h", edges: hgram.edges, counts: hgram.counts, usl: U, lsl: L, mean: d.mean, sigma: d.s, n: d.n, dp: dp, xlabel: "Value" + (units.value ? " (" + units.value + ")" : ""), title: "Histogram with fitted normal curve", desc: "Histogram of the data with a normal curve using the sample mean and standard deviation, and specification limits if given." })));
      }
      run.addEventListener("click", compute);
      compute();
    }
  };

  // ================================================================ 2. capability
  function subgroupText(x, n) {
    if (!n || n < 2) { return x.join("\n"); }
    var lines = [];
    for (var i = 0; i < x.length; i += n) { lines.push(x.slice(i, i + n).join("  ")); }
    return lines.join("\n");
  }
  Calc.capability = {
    mount: function (node, data) {
      var f = el("div");
      var nsub = data.subgroup_size || 1;
      var ta = textarea("x", subgroupText(data.x || [], nsub), 8);
      var size = num("n", nsub, { min: 1, max: 25, step: 1 });
      var chart = select("chart", [["auto", "Automatic (I-MR for n = 1, X̄-R for n ≤ 10, X̄-S above)"], ["imr", "I-MR (individuals)"], ["xbar_r", "X̄-R"], ["xbar_s", "X̄-S"]], data.chart || "auto");
      var usl = num("usl", data.usl), lsl = num("lsl", data.lsl), target = num("target", data.target), units = el("input", { type: "text", name: "units", value: data.units || "" });
      var conv = select("convention", [["2026", "AIAG & VDA 2026 / ISO 22514: Cp/Cpk if stable, else Pp/Ppk, both from overall s; Cw/Cwk from within sigma"], ["2005", "Legacy AIAG 2005 (most software): Cp/Cpk from within sigma, Pp/Ppk from overall s"]], data.convention || "2026");
      f.appendChild(el("div", { "class": "calc-grid wide" }, [field("Data, in time order. One subgroup per line, or a plain list with the subgroup size given below", ta)]));
      f.appendChild(el("div", { "class": "calc-grid" }, [field("Subgroup size n", size), field("Chart for the stability check", chart)]));
      f.appendChild(el("div", { "class": "calc-grid" }, [field("USL", usl), field("LSL", lsl), field("Target (for Cpm)", target), field("Units", units)]));
      f.appendChild(el("div", { "class": "calc-grid wide" }, [field("Index naming convention", conv)]));
      var run = button("Compute capability");
      f.appendChild(el("div", { "class": "row" }, [run]));
      node.appendChild(f);
      function compute() {
        var o = outBox(node);
        var rows = parseRows(ta.value), x = [], n = Math.max(1, Math.round(optNum(size) || 1));
        rows.forEach(function (r) { r.forEach(function (t) { var v = toNum(t); if (has(v)) { x.push(v); } }); });
        if (x.length < 4) { o.appendChild(el("p", { "class": "error", text: "Enter at least four numbers." })); return; }
        if (n > 1 && x.length % n !== 0) { o.appendChild(el("p", { "class": "error", text: x.length + " values do not divide into subgroups of " + n + "." })); return; }
        var U = optNum(usl), L = optNum(lsl), T = optNum(target);
        if (!has(U) && !has(L)) { o.appendChild(el("p", { "class": "error", text: "Enter at least one specification limit." })); return; }
        var ct = chart.value === "auto" ? (n === 1 ? "imr" : (n <= 10 ? "xbar_r" : "xbar_s")) : chart.value;
        if (ct !== "imr" && n === 1) { o.appendChild(el("p", { "class": "error", text: "An X̄ chart needs a subgroup size of at least 2." })); return; }
        if (ct === "imr") { n = 1; }
        var groups = null;
        if (n > 1) { groups = x.map(function (_, i) { return Math.floor(i / n) + 1; }); }
        var p = { usl: U, lsl: L, target: T, subgroup_size: n, chart: ct };
        var cap = S.capability(x, p, groups);
        cap.x = x;
        var dp = autoDp(x), u = units.value ? " " + units.value : "", legacy = conv.value === "2005";
        // Step 1: stability
        o.appendChild(h4("Step 1. Is the process stable? (control chart of the same data)"));
        var ch = cap.chart;
        var consts = ct === "imr" ? "MR̄ = " + fmt(ch.mrbar, dp + 1) + ", d₂(2) = 1.128, limits x̄ ± 3·MR̄/d₂" :
          (ct === "xbar_s" ? "k = " + ch.k + " subgroups of n = " + ch.n + ": S̄ = " + fmt(ch.sbar, dp + 2) + ", A₃ = " + ch.A3 + ", B₃ = " + ch.B3 + ", B₄ = " + ch.B4 + ", c₄ = " + ch.c4 :
            "k = " + ch.k + " subgroups of n = " + ch.n + ": R̄ = " + fmt(ch.rbar, dp + 1) + ", A₂ = " + ch.A2 + ", D₃ = " + ch.D3 + ", D₄ = " + ch.D4 + ", d₂ = " + ch.d2);
        o.appendChild(note("Limits computed from the data: " + consts + ". Specification limits are not drawn on a control chart."));
        stabilityCharts(cap, units.value, dp, node.id).forEach(function (fg) { o.appendChild(fg); });
        o.appendChild(stabilityVerdict(cap));
        // Step 2: normality
        o.appendChild(h4("Step 2. Does a normal distribution describe the data?"));
        var d = cap.descriptive;
        if (has(d.ad_p)) {
          o.appendChild(msg("Anderson-Darling A² = " + fmt(d.ad_A2, 3) + ", p = " + fmtP(d.ad_p) + ". " + (d.ad_p >= 0.05 ? "No evidence against normality at the 5 % level; the normal-based indices and PPM below are reasonable." : "The data depart from normality. The indices below assume a normal distribution and the PPM figures will be wrong; see Module 8 for what to do."), d.ad_p >= 0.05 ? "ok" : "bad"));
        } else { o.appendChild(note("Fewer than 8 values: no normality test.")); }
        o.appendChild(figure(histogram({ id: node.id + "-h", edges: cap.histogram.edges, counts: cap.histogram.counts, usl: U, lsl: L, target: T, mean: d.mean, sigma: d.s, n: d.n, dp: dp, xlabel: "Value" + (units.value ? " (" + units.value + ")" : ""),
          title: "Histogram with specification limits and normal curve (overall s)", desc: "Histogram of all values with the specification limits, the target if given, the sample mean, and a normal curve fitted with the overall sample standard deviation." })));
        // Step 3: indices
        o.appendChild(h4("Step 3. Capability and performance indices"));
        var ov = cap.overall, wi = cap.within;
        var sigW = wi.sigma_estimate === "Rbar/d2" ? "within, R̄/d₂" : (wi.sigma_estimate === "Sbar/c4" ? "within, S̄/c₄" : "within, MR̄/d₂");
        var sigO = "overall, sample s (n − 1)";
        o.appendChild(table("Sigma estimates", ["Estimate", "Value", "How"], [
          ["Overall σ̂ (sample standard deviation, n − 1)", fmt(ov.s, dp + 2) + u, "all " + d.n + " values pooled"],
          ["Within-subgroup σ̂ (" + sigW.split(", ")[1] + ")", fmt(wi.sigma, dp + 2) + u, ct === "imr" ? "average moving range ÷ 1.128" : (ct === "xbar_s" ? "S̄ ÷ c₄ = " + fmt(wi.sbar, dp + 3) + " ÷ " + wi.c4 : "R̄ ÷ d₂ = " + fmt(wi.rbar, dp + 2) + " ÷ " + wi.d2)],
          ["Ratio within ÷ overall", fmt(wi.sigma / ov.s, 3), wi.sigma / ov.s < 0.9 ? "overall is larger: there is variation between subgroups (drift, shifts, batches)" : "close to 1: little variation beyond what is inside a subgroup"]]));
        var label = legacy ? "Pp/Ppk" : cap.aiag_vda_2026_label;
        var nameO = label.split("/"), nameW = legacy ? ["Cp", "Cpk"] : ["Cw", "Cwk"];
        var idx = [];
        function row(name, val, sig, formula, ppm) { idx.push([name, has(val) ? fmt(val, 2) : "–", sig, formula, has(ppm) ? fmtPpm(ppm) : "–"]); }
        if (has(ov.Pp)) { row(nameO[0], ov.Pp, sigO, "(USL − LSL) / 6σ̂", null); }
        if (has(ov.Ppu)) { row(nameO[1].replace("k", "u"), ov.Ppu, sigO, "(USL − x̄) / 3σ̂", ov.ppm_upper); }
        if (has(ov.Ppl)) { row(nameO[1].replace("k", "l"), ov.Ppl, sigO, "(x̄ − LSL) / 3σ̂", ov.ppm_lower); }
        row(nameO[1], ov.Ppk, sigO, "min of the two one-sided indices", ov.ppm_total);
        if (has(ov.Cpm)) { row("Cpm", ov.Cpm, sigO + ", plus (x̄ − T)²", "(USL − LSL) / 6·√(σ̂² + (x̄ − T)²)", null); }
        if (has(wi.Cw)) { row(nameW[0], wi.Cw, sigW, "(USL − LSL) / 6σ̂", null); }
        if (has(wi.Cwu)) { row(nameW[1].replace("k", "u"), wi.Cwu, sigW, "(USL − x̄) / 3σ̂", wi.ppm_upper); }
        if (has(wi.Cwl)) { row(nameW[1].replace("k", "l"), wi.Cwl, sigW, "(x̄ − LSL) / 3σ̂", wi.ppm_lower); }
        row(nameW[1], wi.Cwk, sigW, "min of the two one-sided indices", wi.ppm_total);
        o.appendChild(table("Indices, each with the sigma estimate that produced it (x̄ = " + fmt(ov.mean, dp + 1) + u + ")", ["Index", "Value", "Sigma estimate", "Formula", "Predicted PPM out of spec"], idx));
        var conventionNote = legacy ?
          "Legacy AIAG 2005 labels, as printed by most software: Cp/Cpk use the within-subgroup sigma, Pp/Ppk the overall sample s. Under this convention Cpk describes the process if it stayed as it is inside a subgroup; Ppk describes what was actually delivered." :
          "AIAG & VDA 2026 / ISO 22514 labels: the index that describes delivered output is computed from the overall s and is named Cp/Cpk only because the control chart showed stability" + (cap.stable ? "" : " (it did not here, so the index is named Pp/Ppk)") + ". The within-subgroup index is named Cw/Cwk; it is an analysis tool that shows what the process could do without between-subgroup variation, not a reporting figure.";
        o.appendChild(note(conventionNote));
        var ci = ov.Ppk_ci95;
        var kv = el("dl", { "class": "kv" });
        function kvrow(k, v) { kv.appendChild(el("dt", { text: k })); kv.appendChild(el("dd", { text: v })); }
        kvrow("Observed out of specification", cap.observed.n_out + " of " + d.n + " values (" + fmtPpm(cap.observed.ppm_observed) + " PPM)");
        kvrow("Predicted PPM from " + nameO[1] + " (overall σ̂, normal)", fmtPpm(ov.ppm_total));
        kvrow("Predicted PPM from " + nameW[1] + " (within σ̂, normal)", fmtPpm(wi.ppm_total));
        if (has(ov.k)) { kvrow("Centring k = |mid-tolerance − x̄| / half-tolerance", fmt(ov.k, 3)); }
        if (ci) { kvrow("Approximate 95 % confidence interval on " + nameO[1] + " (n = " + d.n + ")", fmt(ci[0], 2) + " to " + fmt(ci[1], 2)); }
        if (ov.Pp_ci95) { kvrow("95 % confidence interval on " + nameO[0] + " (chi-square)", fmt(ov.Pp_ci95[0], 2) + " to " + fmt(ov.Pp_ci95[1], 2)); }
        o.appendChild(kv);
        if (!cap.stable) { o.appendChild(note("Because the chart is not stable, none of these numbers predicts anything. Find the special cause, fix it, collect new data, and repeat.")); }
      }
      run.addEventListener("click", compute);
      compute();
    }
  };

  // ================================================================ 3. DPMO and sigma level
  Calc.dpmo = {
    mount: function (node, data) {
      var f = el("div");
      var defects = num("defects", has(data.defects) ? data.defects : 37, { min: 0, step: 1 }), units = num("units", has(data.units) ? data.units : 2400, { min: 1, step: 1 }), opps = num("opps", has(data.opportunities) ? data.opportunities : 5, { min: 1, step: 1 });
      f.appendChild(h4("A. From a defect count"));
      f.appendChild(el("div", { "class": "calc-grid" }, [field("Defects counted", defects), field("Units inspected", units), field("Opportunities per unit", opps)]));
      f.appendChild(h4("B. Convert DPMO to sigma level or back"));
      var dpmoIn = num("dpmo", has(data.dpmo) ? data.dpmo : 3.4, { min: 0 }), sigIn = num("sigma", "", { step: 0.01 });
      f.appendChild(el("div", { "class": "calc-grid" }, [field("DPMO (fill this …)", dpmoIn), field("… or sigma level with the 1.5 shift (this)", sigIn)]));
      f.appendChild(h4("C. Rolled throughput yield of a chain of steps"));
      var yields = textarea("yields", (data.yields || [0.98, 0.95, 0.99, 0.97, 0.985]).join(" "), 2);
      f.appendChild(el("div", { "class": "calc-grid wide" }, [field("Step yields as fractions or percentages, in order", yields)]));
      var run = button("Compute");
      f.appendChild(el("div", { "class": "row" }, [run]));
      node.appendChild(f);
      function compute() {
        var o = outBox(node);
        var D = optNum(defects), Un = optNum(units), Op = optNum(opps);
        if (has(D) && has(Un) && has(Op) && Un > 0 && Op > 0) {
          var r = S.dpmo(D, Un, Op);
          var rows = [["Defects per unit, DPU = D / U", fmt(r.dpu, 4)], ["Defects per opportunity, DPO = D / (U·O)", (D / (Un * Op)).toPrecision(4)], ["Defects per million opportunities, DPMO = DPO × 10⁶", fmt(r.dpmo, 1)],
            ["First-time yield (Poisson) = e^(−DPU)", fmt(100 * r.yield_fty, 2) + " %"], ["Z from DPMO, no shift (long-term Z)", has(r.sigma_long_term) && isFinite(r.sigma_long_term) ? fmt(r.sigma_long_term, 2) : "–"], ["Sigma level with the 1.5σ shift added (Motorola convention)", has(r.sigma_level_shifted) && isFinite(r.sigma_level_shifted) ? fmt(r.sigma_level_shifted, 2) : "–"]];
          o.appendChild(table("A. From the defect count", ["Quantity", "Value"], rows));
        }
        var dv = optNum(dpmoIn), sv = optNum(sigIn);
        if (has(sv)) { dv = S.dpmoFromSigma(sv, 1.5); dpmoIn.value = dv < 1 ? dv.toPrecision(3) : fmt(dv, 1).replace(/,/g, ""); }
        if (has(dv) && dv > 0 && dv < 1e6) {
          var zs = S.sigmaFromDpmo(dv, 0), zl = S.sigmaFromDpmo(dv, 1.5);
          o.appendChild(table("B. Conversion (both conventions shown)", ["Quantity", "Value"], [["DPMO", fmtPpm(dv)], ["Yield = 1 − DPMO/10⁶", fmt(100 * (1 - dv / 1e6), 4) + " %"], ["Z without shift (the actual normal tail)", fmt(zs, 2)], ["Sigma level with 1.5σ shift (as in most Six Sigma tables)", fmt(zl, 2)]]));
          sigIn.value = "";
        }
        var ys = numsOf(yields.value).map(function (v) { return v > 1 ? v / 100 : v; });
        if (ys.length) {
          var rc = S.rtyChain({ yields: ys });
          o.appendChild(table("C. Rolled throughput yield", ["Quantity", "Value"], [["Number of steps", String(ys.length)], ["Step yields", ys.map(function (v) { return fmt(100 * v, 2) + " %"; }).join(", ")], ["Rolled throughput yield = product of step yields", fmt(100 * rc.rty, 2) + " %"], ["Normalised yield per step = RTY^(1/k)", fmt(100 * rc.normalized_yield, 2) + " %"], ["Total DPU implied = −ln(RTY)", fmt(rc.total_dpu, 4)]]));
          o.appendChild(table("Cumulative yield after each step", ["Step", "Cumulative RTY"], rc.cumulative_rty.map(function (v, i) { return [String(i + 1), fmt(100 * v, 2) + " %"]; })));
        }
        o.appendChild(note("Sigma level = Z + 1.5 is a convention, not a measurement. Both values are shown so the reader always knows which one a report is quoting."));
      }
      run.addEventListener("click", compute);
      compute();
    }
  };

  // ================================================================ 4. control chart builder
  var CHART_TYPES = [["imr", "I-MR (individuals and moving range)"], ["xbar_r", "X̄-R (subgroups, ranges)"], ["xbar_s", "X̄-S (subgroups, standard deviations)"], ["p", "p (proportion defective, n may vary)"], ["np", "np (number defective, constant n)"], ["c", "c (count of defects, constant area)"], ["u", "u (defects per unit, n may vary)"]];
  function chartFromData(type, cols, baselineK) {
    // returns {values, center, ucl, lcl, signals, rules, secondary:{...}, label}
    var K = baselineK || null;
    function sliceRows(arr, k) { return k ? arr.slice(0, k) : arr; }
    if (type === "imr") {
      var xs = cols.x, base = K ? xs.slice(0, K) : xs, b = S.imrChart(base);
      var mr = []; for (var i = 1; i < xs.length; i++) { mr.push(Math.abs(xs[i] - xs[i - 1])); }
      var rules = S.runRules(xs, b.xbar, b.sigma_within);
      var beyondMr = []; mr.forEach(function (v, i) { if (v > b.ucl_mr) { beyondMr.push(i + 1); } });
      return { values: xs, center: b.xbar, ucl: b.ucl_x, lcl: b.lcl_x, sigma: b.sigma_within, rules: rules, xlabel: "Observation", ylabel: "Individual value", centerLabel: "x̄",
        secondary: { values: mr, center: b.mrbar, ucl: b.ucl_mr, lcl: null, signals: beyondMr, title: "Moving range chart", ylabel: "Moving range", centerLabel: "MR̄" },
        info: "x̄ = " + fmt(b.xbar, 4) + ", MR̄ = " + fmt(b.mrbar, 4) + ", σ̂ = MR̄/1.128 = " + fmt(b.sigma_within, 4) + "; UCL/LCL = x̄ ± 3σ̂; UCL(MR) = 3.267·MR̄" + (K ? " (from the first " + K + " observations)" : "") };
    }
    if (type === "xbar_r" || type === "xbar_s") {
      var subs = cols.subs, n = subs[0].length, c = S.CONSTANTS[String(n)];
      if (!c) { throw new Error("subgroup size must be 2 to 25"); }
      var flat = [], g = [];
      subs.forEach(function (s, gi) { s.forEach(function (v) { flat.push(v); g.push(gi + 1); }); });
      var bsubs = K ? subs.slice(0, K) : subs, bflat = [], bg = [];
      bsubs.forEach(function (s, gi) { s.forEach(function (v) { bflat.push(v); bg.push(gi + 1); }); });
      var means = subs.map(function (s) { var t = 0; s.forEach(function (v) { t += v; }); return t / s.length; });
      if (type === "xbar_r") {
        var br = S.xbarRChart(bflat, bg);
        var ranges = subs.map(function (s) { return Math.max.apply(null, s) - Math.min.apply(null, s); });
        var rr = S.runRules(means, br.xbarbar, br.A2 * br.rbar / 3);
        var beyondR = []; ranges.forEach(function (v, i) { if (v > br.ucl_r || v < br.lcl_r) { beyondR.push(i + 1); } });
        return { values: means, center: br.xbarbar, ucl: br.ucl_x, lcl: br.lcl_x, sigma: br.A2 * br.rbar / 3, rules: rr, ylabel: "Subgroup mean", centerLabel: "x̄̄",
          secondary: { values: ranges, center: br.rbar, ucl: br.ucl_r, lcl: br.D3 > 0 ? br.lcl_r : null, signals: beyondR, title: "R chart", ylabel: "Subgroup range", centerLabel: "R̄" },
          info: "n = " + n + ": A₂ = " + br.A2 + ", D₃ = " + br.D3 + ", D₄ = " + br.D4 + ", d₂ = " + br.d2 + "; x̄̄ = " + fmt(br.xbarbar, 4) + ", R̄ = " + fmt(br.rbar, 4) + "; UCL/LCL = x̄̄ ± A₂R̄; UCL(R) = D₄R̄, LCL(R) = D₃R̄; σ̂ within = R̄/d₂ = " + fmt(br.sigma_within, 4) + (K ? " (from the first " + K + " subgroups)" : "") };
      }
      var bs = S.xbarSChart(bflat, bg);
      var sds = subs.map(function (s) { var m = 0; s.forEach(function (v) { m += v; }); m /= s.length; var ss = 0; s.forEach(function (v) { ss += (v - m) * (v - m); }); return Math.sqrt(ss / (s.length - 1)); });
      var rs = S.runRules(means, bs.xbarbar, bs.A3 * bs.sbar / 3);
      var beyondS = []; sds.forEach(function (v, i) { if (v > bs.ucl_s || v < bs.lcl_s) { beyondS.push(i + 1); } });
      return { values: means, center: bs.xbarbar, ucl: bs.ucl_x, lcl: bs.lcl_x, sigma: bs.A3 * bs.sbar / 3, rules: rs, ylabel: "Subgroup mean", centerLabel: "x̄̄",
        secondary: { values: sds, center: bs.sbar, ucl: bs.ucl_s, lcl: bs.B3 > 0 ? bs.lcl_s : null, signals: beyondS, title: "S chart", ylabel: "Subgroup s", centerLabel: "S̄" },
        info: "n = " + n + ": A₃ = " + bs.A3 + ", B₃ = " + bs.B3 + ", B₄ = " + bs.B4 + ", c₄ = " + bs.c4 + "; x̄̄ = " + fmt(bs.xbarbar, 4) + ", S̄ = " + fmt(bs.sbar, 4) + "; UCL/LCL = x̄̄ ± A₃S̄; UCL(S) = B₄S̄, LCL(S) = B₃S̄; σ̂ within = S̄/c₄ = " + fmt(bs.sigma_within, 4) + (K ? " (from the first " + K + " subgroups)" : "") };
    }
    if (type === "p" || type === "u") {
      var nn = cols.n, dd = cols.d, bp = type === "p" ? S.pChart(sliceRows(nn, K), sliceRows(dd, K)) : S.uChart(sliceRows(nn, K), sliceRows(dd, K));
      var cbar = type === "p" ? bp.pbar : bp.ubar;
      var vals = dd.map(function (v, i) { return v / nn[i]; });
      var sig = nn.map(function (ni) { return type === "p" ? Math.sqrt(cbar * (1 - cbar) / ni) : Math.sqrt(cbar / ni); });
      var ucl = sig.map(function (s) { return cbar + 3 * s; }), lcl = sig.map(function (s) { return Math.max(0, cbar - 3 * s); });
      var rl = S.runRules(vals, cbar, sig);
      return { values: vals, center: cbar, ucl: ucl, lcl: lcl, rules: rl, ylabel: type === "p" ? "Proportion defective" : "Defects per unit", centerLabel: type === "p" ? "p̄" : "ū", variable: true,
        info: (type === "p" ? "p̄ = Σd / Σn = " : "ū = Σc / Σn = ") + fmt(cbar, 4) + "; limits per point " + (type === "p" ? "p̄ ± 3√(p̄(1 − p̄)/nᵢ)" : "ū ± 3√(ū/nᵢ)") + ", lower limit floored at 0" + (K ? " (from the first " + K + " samples)" : "") };
    }
    if (type === "np") {
      var nconst = cols.nconst, bnp = S.npChart(nconst, sliceRows(cols.d, K));
      return { values: cols.d, center: bnp.npbar, ucl: bnp.ucl, lcl: bnp.lcl, rules: S.runRules(cols.d, bnp.npbar, Math.sqrt(nconst * bnp.pbar * (1 - bnp.pbar))), ylabel: "Number defective", centerLabel: "np̄",
        info: "n = " + nconst + ", np̄ = " + fmt(bnp.npbar, 3) + ", p̄ = " + fmt(bnp.pbar, 4) + "; limits np̄ ± 3√(np̄(1 − p̄)), lower floored at 0" + (K ? " (from the first " + K + " samples)" : "") };
    }
    var bc = S.cChart(sliceRows(cols.d, K));
    return { values: cols.d, center: bc.cbar, ucl: bc.ucl, lcl: bc.lcl, rules: S.runRules(cols.d, bc.cbar, Math.sqrt(bc.cbar)), ylabel: "Count of defects", centerLabel: "c̄",
      info: "c̄ = " + fmt(bc.cbar, 3) + "; limits c̄ ± 3√c̄, lower floored at 0" + (K ? " (from the first " + K + " samples)" : "") };
  }
  Calc.control = {
    mount: function (node, data) {
      var f = el("div");
      var type = select("type", CHART_TYPES, data.type || "xbar_r");
      var helpText = { imr: "One value per line (or any separator), in time order.", xbar_r: "One subgroup per line, values separated by spaces or commas; or a plain list with the subgroup size below.", xbar_s: "One subgroup per line, values separated by spaces or commas; or a plain list with the subgroup size below.",
        p: "One sample per line: sample size n, then the number of defectives.", np: "One count of defectives per line; constant sample size below.", c: "One count of defects per line (constant inspection unit).", u: "One sample per line: number of units n, then the count of defects." };
      var help = el("p", { "class": "calc-intro", text: helpText[type.value] });
      var initial = "";
      if (data.rows) { initial = joinRows(data.rows); } else if (data.x) { initial = subgroupText(data.x, data.subgroup_size || 1); }
      var ta = textarea("data", initial, 8);
      var size = num("n", data.subgroup_size || (data.nconst || ""), { min: 1, step: 1 });
      var freeze = num("freeze", data.baseline || "", { min: 2, step: 1 });
      var units = el("input", { type: "text", name: "units", value: data.units || "" });
      var ruleBox = el("div", { "class": "row" });
      var ruleChecks = {};
      [["we1", "WE 1 (beyond 3σ)", true], ["we2", "WE 2 (2 of 3 beyond 2σ)", true], ["we3", "WE 3 (4 of 5 beyond 1σ)", true], ["we4", "WE 4 (8 on one side)", true], ["n2", "Nelson 2 (9 on one side)", false], ["n3", "Nelson 3 (6 trending)", false], ["n4", "Nelson 4 (14 alternating)", false], ["n7", "Nelson 7 (15 within 1σ)", false], ["n8", "Nelson 8 (8 beyond 1σ)", false]].forEach(function (r) {
        var c = check(r[0], r[1], data.rules ? data.rules.indexOf(r[0]) >= 0 : r[2]); ruleChecks[r[0]] = c.querySelector("input"); ruleBox.appendChild(c);
      });
      f.appendChild(el("div", { "class": "calc-grid" }, [field("Chart type", type)]));
      f.appendChild(help);
      f.appendChild(el("div", { "class": "calc-grid wide" }, [field("Data, in time order", ta)]));
      f.appendChild(el("div", { "class": "calc-grid" }, [field("Subgroup size (X̄ charts from a plain list) or constant n (np chart)", size), field("Freeze limits from the first k subgroups (blank = all data)", freeze), field("Units", units)]));
      f.appendChild(el("p", { "class": "calc-intro", text: "Run rules to flag (the 3σ rule always decides stability; the others add sensitivity and false alarms):" }));
      f.appendChild(ruleBox);
      var run = button("Build chart");
      f.appendChild(el("div", { "class": "row" }, [run]));
      node.appendChild(f);
      type.addEventListener("change", function () { help.textContent = helpText[type.value]; });
      function compute() {
        var o = outBox(node), t = type.value, rows = parseRows(ta.value), cols = {}, K = optNum(freeze);
        try {
          if (t === "imr") { cols.x = numsOf(ta.value); if (cols.x.length < 3) { throw new Error("Enter at least three values."); } }
          else if (t === "xbar_r" || t === "xbar_s") {
            var n = optNum(size), subs;
            if (rows.length > 1 && rows.every(function (r) { return r.length === rows[0].length; }) && rows[0].length > 1 && !(has(n) && n > 1 && rows[0].length !== n)) { subs = rows.map(function (r) { return r.map(toNum); }); }
            else { var flat = numsOf(ta.value); if (!has(n) || n < 2) { throw new Error("Give the subgroup size, or put one subgroup per line."); } if (flat.length % n) { throw new Error(flat.length + " values do not divide into subgroups of " + n + "."); } subs = []; for (var i = 0; i < flat.length; i += n) { subs.push(flat.slice(i, i + n)); } }
            if (subs.length < 2) { throw new Error("Need at least two subgroups."); }
            cols.subs = subs;
          }
          else if (t === "p" || t === "u") { cols.n = []; cols.d = []; rows.forEach(function (r) { if (r.length >= 2) { cols.n.push(toNum(r[0])); cols.d.push(toNum(r[1])); } }); if (cols.n.length < 2) { throw new Error("Each line needs n and a count."); } }
          else if (t === "np") { cols.d = numsOf(ta.value); cols.nconst = optNum(size); if (!has(cols.nconst)) { throw new Error("Give the constant sample size n."); } }
          else { cols.d = numsOf(ta.value); }
          if (has(K) && K < 2) { K = null; }
          var r = chartFromData(t, cols, K);
        } catch (e) { o.appendChild(el("p", { "class": "error", text: e.message })); return; }
        var chosen = Object.keys(ruleChecks).filter(function (k) { return ruleChecks[k].checked; });
        var signals = r.rules.we1.slice(), warn = [];
        chosen.forEach(function (k) { if (k !== "we1") { (r.rules[k] || []).forEach(function (i) { if (signals.indexOf(i) < 0 && warn.indexOf(i) < 0) { warn.push(i); } }); } });
        var u = units.value ? " (" + units.value + ")" : "";
        var raw = cols.x || (cols.subs ? [].concat.apply([], cols.subs) : cols.d);
        var dp = t === "p" || t === "u" ? 4 : (t === "np" || t === "c" ? 2 : autoDp(raw));
        o.appendChild(note("Limits computed from the data: " + r.info + ". Specification limits are never drawn on a control chart."));
        o.appendChild(figure(controlChart({ id: node.id + "-c1", values: r.values, center: r.center, ucl: r.ucl, lcl: r.lcl, signals: signals, warn: warn, zones: r.variable ? null : r.sigma, dp: dp, baseline: K,
          title: CHART_TYPES.filter(function (c) { return c[0] === t; })[0][1].split(" (")[0] + " chart", desc: "Control chart with centre line and 3-sigma limits computed from the data; points flagged by the selected rules are marked.", ylabel: r.ylabel + u, xlabel: r.xlabel || "Sample", centerLabel: r.centerLabel })));
        if (r.secondary) {
          var s2 = r.secondary;
          o.appendChild(figure(controlChart({ id: node.id + "-c2", values: s2.values, center: s2.center, ucl: s2.ucl, lcl: s2.lcl, signals: s2.signals, dp: dp, baseline: K, title: s2.title, desc: s2.title + " with centre line and limits from the constants for the subgroup size.", ylabel: s2.ylabel + u, xlabel: r.xlabel || "Sample", centerLabel: s2.centerLabel })));
        }
        var fired = listRules(r.rules, chosen);
        var secHits = r.secondary ? r.secondary.signals : [];
        if (!r.rules.we1.length && !secHits.length) { o.appendChild(msg("No point beyond the 3σ limits" + (r.secondary ? " on either chart" : "") + ".", "ok")); }
        else { o.appendChild(msg("Beyond 3σ limits: " + (r.rules.we1.length ? "primary chart at " + r.rules.we1.join(", ") : "") + (secHits.length ? (r.rules.we1.length ? "; " : "") + "range/spread chart at " + secHits.join(", ") : "") + ".", "bad")); }
        if (fired.length) { o.appendChild(table("Rule violations (selected rules)", ["Rule", "Points"], fired.map(function (s) { var i = s.lastIndexOf(" at "); return [s.slice(0, i), s.slice(i + 4)]; }))); }
        else { o.appendChild(note("None of the selected rules fired.")); }
      }
      run.addEventListener("click", compute);
      compute();
    }
  };

  // ================================================================ 5. gauge R&R
  Calc.grr = {
    mount: function (node, data) {
      var f = el("div");
      var ta = textarea("grr", data.rows ? joinRows(data.rows, "\t") : "", 10);
      var tol = num("tol", data.tolerance), ksv = select("k", [["6", "6 (99.73 %, AIAG MSA 4th ed.)"], ["5.15", "5.15 (99 %, older convention)"]], String(data.study_var_k || 6));
      var alpha = select("alpha", [["0.05", "Drop the interaction if p > 0.05 (Minitab default)"], ["0.25", "Drop the interaction if p > 0.25 (AIAG MSA 4th ed.)"], ["0", "Always keep the interaction term"]], String(has(data.alpha_remove) ? data.alpha_remove : 0.05));
      f.appendChild(el("p", { "class": "calc-intro", text: "One measurement per line: part, operator, trial, value (tab, comma or space separated). Every operator measures every part the same number of times (crossed design)." }));
      f.appendChild(el("div", { "class": "calc-grid wide" }, [field("Measurements", ta)]));
      f.appendChild(el("div", { "class": "calc-grid" }, [field("Tolerance (USL − LSL), optional", tol), field("Study variation multiplier", ksv), field("Interaction term", alpha)]));
      var run = button("Compute gauge R&R");
      f.appendChild(el("div", { "class": "row" }, [run]));
      node.appendChild(f);
      function compute() {
        var o = outBox(node), rows = parseRows(ta.value), cols = { part: [], operator: [], trial: [], y: [] };
        rows.forEach(function (r) { if (r.length >= 4) { cols.part.push(r[0]); cols.operator.push(r[1]); cols.trial.push(r[2]); cols.y.push(toNum(r[3])); } });
        if (cols.y.length < 8 || cols.y.some(function (v) { return !has(v); })) { o.appendChild(el("p", { "class": "error", text: "Need at least 2 parts × 2 operators × 2 trials of numeric values." })); return; }
        var r;
        try { r = S.grr(cols, { tolerance: optNum(tol), study_var_k: Number(ksv.value), alpha_remove: Number(alpha.value) }); } catch (e) { o.appendChild(el("p", { "class": "error", text: e.message })); return; }
        if (!(r.parts * r.operators * r.replicates === r.N)) { o.appendChild(el("p", { "class": "error", text: "The design is not balanced: " + r.parts + " parts × " + r.operators + " operators × " + r.replicates + " trials ≠ " + r.N + " rows." })); return; }
        var dp = autoDp(cols.y);
        o.appendChild(note(r.parts + " parts × " + r.operators + " operators × " + r.replicates + " trials = " + r.N + " measurements. Grand mean " + fmt(r.grand_mean, dp + 1) + "."));
        var full = r.ss_full, dff = r.df_full, msf = r.ms_full;
        var an = [["Part", String(dff.part), fmt(full.part, 6), fmt(msf.part, 6), fmt(msf.part / msf.interaction, 3), fmtP(S.fSf(msf.part / msf.interaction, dff.part, dff.interaction))],
          ["Operator", String(dff.operator), fmt(full.operator, 6), fmt(msf.operator, 6), fmt(msf.operator / msf.interaction, 3), fmtP(S.fSf(msf.operator / msf.interaction, dff.operator, dff.interaction))],
          ["Part × operator", String(dff.interaction), fmt(full.interaction, 6), fmt(msf.interaction, 6), fmt(r.interaction_F, 3), fmtP(r.interaction_p)],
          ["Repeatability (error)", String(dff.repeatability), fmt(full.repeatability, 6), fmt(msf.repeatability, 6), "", ""],
          ["Total", String(dff.part + dff.operator + dff.interaction + dff.repeatability), fmt(full.total, 6), "", "", ""]];
        o.appendChild(table("Two-way ANOVA with interaction", ["Source", "df", "SS", "MS", "F", "p"], an));
        if (r.interaction_removed) {
          var msr = r.ms_reduced, dfr = r.df_reduced;
          o.appendChild(table("Reduced ANOVA (interaction p = " + fmtP(r.interaction_p) + " > " + alpha.value + ", pooled into repeatability)", ["Source", "df", "MS", "F", "p"], [["Part", String(dfr.part), fmt(msr.part, 6), fmt(r.F_part, 3), fmtP(r.p_part)], ["Operator", String(dfr.operator), fmt(msr.operator, 6), fmt(r.F_operator, 3), fmtP(r.p_operator)], ["Repeatability", String(dfr.repeatability), fmt(msr.repeatability, 6), "", ""]]));
        } else { o.appendChild(note("Interaction kept (p = " + fmtP(r.interaction_p) + "). Part and operator are tested against the interaction mean square.")); }
        var keys = [["grr", "Total gauge R&R"], ["repeatability", "  Repeatability (equipment)"], ["reproducibility", "  Reproducibility (operators)"], ["operator", "    Operator"], ["interaction", "    Operator × part"], ["part", "Part-to-part"], ["total", "Total variation"]];
        var vrows = keys.map(function (k) { var row = [k[1], r.varcomp[k[0]].toPrecision(4), fmt(r.pct_contribution[k[0]], 2), fmt(r.sd[k[0]], dp + 2), fmt(r.study_var[k[0]], dp + 2), fmt(r.pct_study_var[k[0]], 2)]; if (r.pct_tolerance) { row.push(fmt(r.pct_tolerance[k[0]], 2)); } return row; });
        var vh = ["Source", "Variance component", "% Contribution", "Std dev", ksv.value + " × std dev", "% Study variation"]; if (r.pct_tolerance) { vh.push("% Tolerance"); }
        o.appendChild(table("Variance components", vh, vrows));
        var kv = el("dl", { "class": "kv" });
        function kvrow(k, v) { kv.appendChild(el("dt", { text: k })); kv.appendChild(el("dd", { text: v })); }
        kvrow("%GRR (study variation)", fmt(r.pct_study_var.grr, 1) + " %");
        if (r.pct_tolerance) { kvrow("%GRR (tolerance)", fmt(r.pct_tolerance.grr, 1) + " %"); }
        kvrow("Number of distinct categories, ndc = ⌊1.41 × σ_part / σ_GRR⌋", String(r.ndc) + " (unrounded " + fmt(r.ndc_exact, 2) + ")");
        o.appendChild(kv);
        var g = r.pct_tolerance ? Math.max(r.pct_study_var.grr, r.pct_tolerance.grr) : r.pct_study_var.grr;
        var verdict = g < 10 ? "under 10 %: generally acceptable" : (g <= 30 ? "10 to 30 %: may be acceptable depending on the application, cost and customer agreement" : "over 30 %: unacceptable; improve the measurement system before using it");
        o.appendChild(msg("AIAG MSA guideline on the larger of %study variation and %tolerance: " + verdict + ". ndc " + (r.ndc >= 5 ? "≥ 5: the gauge can distinguish parts well enough for process analysis." : "< 5: the gauge cannot resolve enough part categories for process analysis."), g < 10 && r.ndc >= 5 ? "ok" : (g > 30 ? "bad" : "")));
        o.appendChild(note("These thresholds are the AIAG MSA reference manual's guidelines, not laws; your customer may set different ones."));
      }
      run.addEventListener("click", compute);
      compute();
    }
  };

  // ================================================================ 6. tests: t-test and ANOVA
  Calc.tests = {
    mount: function (node, data) {
      var f = el("div");
      var mode = select("mode", [["ttest2", "Two-sample t-test (two groups)"], ["anova1", "One-way ANOVA (two or more groups)"], ["paired", "Paired t-test (before / after, same units)"], ["ttest1", "One-sample t-test against a target"]], data.mode || "ttest2");
      var ta = textarea("groups", data.lines ? data.lines.join("\n") : "", 6);
      var alpha = num("alpha", has(data.alpha) ? data.alpha : 0.05, { min: 0.001, max: 0.5, step: 0.01 }), mu0 = num("mu0", data.mu0);
      f.appendChild(el("p", { "class": "calc-intro", text: "One group per line: a label, then the values (space, comma or tab separated). For a paired test give two lines in the same order (before, after). For a one-sample test give one line and the target." }));
      f.appendChild(el("div", { "class": "calc-grid" }, [field("Test", mode)]));
      f.appendChild(el("div", { "class": "calc-grid wide" }, [field("Groups", ta)]));
      f.appendChild(el("div", { "class": "calc-grid" }, [field("Significance level α", alpha), field("Target μ₀ (one-sample test only)", mu0)]));
      var run = button("Run test");
      f.appendChild(el("div", { "class": "row" }, [run]));
      node.appendChild(f);
      function compute() {
        var o = outBox(node), rows = parseRows(ta.value), groups = [], a = optNum(alpha) || 0.05;
        rows.forEach(function (r) { if (r.length >= 2) { var lbl = r[0], vals = r.slice(1).map(toNum).filter(has); if (has(toNum(lbl))) { vals.unshift(toNum(lbl)); lbl = "Group " + (groups.length + 1); } if (vals.length >= 2) { groups.push({ label: lbl, x: vals }); } } });
        if (!groups.length) { o.appendChild(el("p", { "class": "error", text: "Enter at least one group with two or more values." })); return; }
        var dp = autoDp(groups[0].x), m = mode.value;
        var summ = groups.map(function (g) { var d = S.descriptive(g.x); return [g.label, String(d.n), fmt(d.mean, dp + 1), fmt(d.s, dp + 2), fmt(d.sem, dp + 2)]; });
        o.appendChild(table("Group summary", ["Group", "n", "Mean", "s", "SE of mean"], summ));
        var cols;
        if (m === "ttest2") {
          if (groups.length < 2) { o.appendChild(el("p", { "class": "error", text: "Two groups are needed." })); return; }
          cols = { group: [], x: [] }; groups.slice(0, 2).forEach(function (g) { g.x.forEach(function (v) { cols.group.push(g.label); cols.x.push(v); }); });
          var r = S.ttest2(cols, { alpha: a });
          o.appendChild(table("Two-sample t-test, H₀: μ₁ − μ₂ = 0", ["Method", "Difference", "SE", "t", "df", "p (two-sided)", (100 * (1 - a)).toFixed(0) + " % CI for the difference"], [
            ["Pooled variances (Student)", fmt(r.diff, dp + 1), fmt(r.pooled.se, dp + 2), fmt(r.pooled.t, 3), String(r.pooled.df), fmtP(r.pooled.p), fmt(r.pooled.ci[0], dp + 1) + " to " + fmt(r.pooled.ci[1], dp + 1)],
            ["Unequal variances (Welch)", fmt(r.diff, dp + 1), fmt(r.welch.se, dp + 2), fmt(r.welch.t, 3), fmt(r.welch.df, 1), fmtP(r.welch.p), fmt(r.welch.ci[0], dp + 1) + " to " + fmt(r.welch.ci[1], dp + 1)]]));
          o.appendChild(table("Variances and effect size", ["Quantity", "Value"], [["Ratio of variances F = s₁²/s₂²", fmt(r.variance_tests.F, 3) + " (p = " + fmtP(r.variance_tests.F_p) + ", assumes normality)"], ["Levene's test (median-centred) p", fmtP(r.variance_tests.levene_p)], ["Cohen's d = difference / pooled s", fmt(r.cohen_d, 2)]]));
          o.appendChild(interpret(r.welch.p, a, "the two means are equal", "difference " + fmt(r.diff, dp + 1) + " (Welch CI " + fmt(r.welch.ci[0], dp + 1) + " to " + fmt(r.welch.ci[1], dp + 1) + ")"));
        } else if (m === "anova1") {
          cols = { group: [], x: [] }; groups.forEach(function (g) { g.x.forEach(function (v) { cols.group.push(g.label); cols.x.push(v); }); });
          var ra = S.anova1(cols, { alpha: a });
          o.appendChild(table("One-way ANOVA, H₀: all group means equal", ["Source", "df", "SS", "MS", "F", "p"], [["Between groups", String(ra.df_between), ra.ss_between.toPrecision(5), ra.ms_between.toPrecision(5), fmt(ra.F, 3), fmtP(ra.p)], ["Within groups (error)", String(ra.df_within), ra.ss_within.toPrecision(5), ra.ms_within.toPrecision(5), "", ""], ["Total", String(ra.df_between + ra.df_within), ra.ss_total.toPrecision(5), "", "", ""]]));
          o.appendChild(table("Effect size and assumptions", ["Quantity", "Value"], [["η² = SS between / SS total", fmt(ra.eta2, 3)], ["Pooled standard deviation √MS within", fmt(ra.pooled_sd, dp + 2)], ["Levene's test for equal variances p", fmtP(ra.levene_p)]]));
          o.appendChild(interpret(ra.p, a, "all group means are equal", "η² = " + fmt(ra.eta2, 2) + " of the variation is between groups"));
        } else if (m === "paired") {
          if (groups.length < 2 || groups[0].x.length !== groups[1].x.length) { o.appendChild(el("p", { "class": "error", text: "A paired test needs two lines of equal length." })); return; }
          var rp = S.paired({ before: groups[0].x, after: groups[1].x }, { alpha: a });
          o.appendChild(table("Paired t-test on the differences (second line − first line), H₀: mean difference = 0", ["n", "Mean difference", "s of differences", "SE", "t", "df", "p (two-sided)", (100 * (1 - a)).toFixed(0) + " % CI", "Cohen's d"], [[String(rp.n), fmt(rp.mean, dp + 1), fmt(rp.s, dp + 2), fmt(rp.se, dp + 2), fmt(rp.t, 3), String(rp.df), fmtP(rp.p), fmt(rp.ci[0], dp + 1) + " to " + fmt(rp.ci[1], dp + 1), fmt(rp.cohen_d, 2)]]));
          o.appendChild(interpret(rp.p, a, "the mean difference is zero", "mean difference " + fmt(rp.mean, dp + 1)));
        } else {
          var mu = optNum(mu0); if (!has(mu)) { o.appendChild(el("p", { "class": "error", text: "Give the target μ₀." })); return; }
          var r1 = S.oneSample(groups[0].x, mu, a);
          o.appendChild(table("One-sample t-test, H₀: μ = " + mu, ["n", "Mean", "s", "SE", "t", "df", "p (two-sided)", (100 * (1 - a)).toFixed(0) + " % CI for μ", "Cohen's d"], [[String(r1.n), fmt(r1.mean, dp + 1), fmt(r1.s, dp + 2), fmt(r1.se, dp + 2), fmt(r1.t, 3), String(r1.df), fmtP(r1.p), fmt(r1.ci[0], dp + 1) + " to " + fmt(r1.ci[1], dp + 1), fmt(r1.cohen_d, 2)]]));
          o.appendChild(interpret(r1.p, a, "the mean equals " + mu, "mean " + fmt(r1.mean, dp + 1)));
        }
      }
      function interpret(p, a, h0, effect) {
        var t = "p = " + fmtP(p) + ": if " + h0 + " and the assumptions hold, data at least this far from H₀ would occur in about " + (p < 0.001 ? "fewer than 0.1 %" : fmt(100 * p, 1) + " %") + " of repeated samples. ";
        t += p < a ? "At α = " + a + " this is called statistically significant. " : "At α = " + a + " this is not statistically significant; the data are consistent with H₀ (which is not proof of H₀). ";
        t += "Practical significance is a separate question: " + effect + ". Decide whether that size matters in engineering terms.";
        return note(t);
      }
      run.addEventListener("click", compute);
      compute();
    }
  };

  // ================================================================ 7. sample size
  Calc.samplesize = {
    mount: function (node, data) {
      var f = el("div");
      var delta = num("delta", has(data.delta) ? data.delta : 1.5), sigma = num("sigma", has(data.sigma) ? data.sigma : 2.0), alpha = num("alpha", has(data.alpha) ? data.alpha : 0.05, { step: 0.01 }), power = num("power", has(data.power) ? data.power : 0.9, { step: 0.05, min: 0.5, max: 0.999 });
      var sides = select("sides", [["2", "Two-sided"], ["1", "One-sided"]], String(data.sides || 2)), design = select("design", [["two-sample", "Two-sample t (n per group)"], ["one-sample", "One-sample or paired t"]], data.design || "two-sample");
      f.appendChild(el("div", { "class": "calc-grid" }, [field("Difference to detect δ", delta), field("Standard deviation σ (same units)", sigma), field("α", alpha), field("Power 1 − β", power), field("Alternative", sides), field("Design", design)]));
      var run = button("Compute sample size");
      f.appendChild(el("div", { "class": "row" }, [run]));
      node.appendChild(f);
      function compute() {
        var o = outBox(node), d = optNum(delta), s = optNum(sigma), a = optNum(alpha), pw = optNum(power);
        if (!(d > 0 && s > 0 && a > 0 && a < 1 && pw > 0 && pw < 1)) { o.appendChild(el("p", { "class": "error", text: "δ and σ must be positive; α and power between 0 and 1." })); return; }
        var p = { alpha: a, beta: 1 - pw, delta: d, sigma: s, sides: Number(sides.value), design: design.value };
        var r = S.sampleSize(p);
        var per = design.value === "two-sample" ? " per group" : "";
        o.appendChild(table("Result", ["Quantity", "Value"], [["Standardised difference δ/σ", fmt(d / s, 3)], ["z(1 − α" + (r.sides === 2 ? "/2" : "") + ")", fmt(r.z_alpha, 3)], ["z(1 − β)", fmt(r.z_beta, 3)], ["n from the normal approximation" + per, fmt(r.n_z_exact, 2) + " → " + r.n_z], ["n with the t distribution (iterated)" + per, String(r.n_t)]]));
        var trows = [0.5, 0.75, 1, 1.5, 2].map(function (k) { var rr = S.sampleSize({ alpha: a, beta: 1 - pw, delta: k, sigma: 1, sides: Number(sides.value), design: design.value }); return [fmt(k, 2), String(rr.n_t)]; });
        o.appendChild(table("n" + per + " for other standardised differences at the same α and power", ["δ/σ", "n (t-based)"], trows));
        o.appendChild(note("Formula: n = " + (design.value === "two-sample" ? "2" : "1") + "·(z<sub>1−α" + (r.sides === 2 ? "/2" : "") + "</sub> + z<sub>1−β</sub>)²·(σ/δ)², then iterated with t quantiles on the resulting degrees of freedom. Use the t-based value. The answer is only as good as your estimate of σ; if σ is uncertain, run a pilot."));
      }
      run.addEventListener("click", compute);
      compute();
    }
  };

  // ================================================================ 8. 2^k factorial
  Calc.factorial = {
    mount: function (node, data) {
      var f = el("div");
      var k = select("k", [["2", "2 factors (4 runs)"], ["3", "3 factors (8 runs)"]], String(data.k || 3));
      var reps = select("reps", [["1", "1"], ["2", "2"], ["3", "3"], ["4", "4"]], String(data.replicates || 2));
      var names = el("input", { type: "text", name: "names", value: (data.factors || ["A", "B", "C"]).join(", ") });
      var grid = el("div", { "class": "grid-input" });
      f.appendChild(el("div", { "class": "calc-grid" }, [field("Factors", k), field("Replicates", reps), field("Factor names (comma separated)", names)]));
      f.appendChild(el("p", { "class": "calc-intro", text: "Runs in standard (Yates) order: the first factor alternates fastest. Enter one response per replicate." }));
      f.appendChild(grid);
      var run = button("Compute effects");
      f.appendChild(el("div", { "class": "row" }, [run]));
      node.appendChild(f);
      var current = data.y || null;
      function buildGrid() {
        while (grid.firstChild) { grid.removeChild(grid.firstChild); }
        var kk = Number(k.value), R = Number(reps.value), nm = names.value.split(",").map(function (s) { return s.trim(); }).filter(Boolean).slice(0, kk);
        while (nm.length < kk) { nm.push("ABC"[nm.length]); }
        var hdr = ["Run"].concat(nm); for (var r = 1; r <= R; r++) { hdr.push("y (rep " + r + ")"); }
        var rows = [];
        for (var i = 0; i < (1 << kk); i++) {
          var row = [String(i + 1)];
          for (var j = 0; j < kk; j++) { row.push((i >> j) & 1 ? "+" : "−"); }
          for (var rr = 0; rr < R; rr++) { var inp = el("input", { type: "number", step: "any", "aria-label": "run " + (i + 1) + " replicate " + (rr + 1) }); if (current && current[i] && has(current[i][rr])) { inp.value = current[i][rr]; } row.push(inp); }
          rows.push(row);
        }
        grid.appendChild(table(null, hdr, rows));
      }
      function compute() {
        var o = outBox(node), kk = Number(k.value), R = Number(reps.value), nm = names.value.split(",").map(function (s) { return s.trim(); }).filter(Boolean).slice(0, kk);
        while (nm.length < kk) { nm.push("ABC"[nm.length]); }
        // compute with single-letter codes so that interaction keys are "AB", "ABC"; display with the user's names
        var letters = "ABC".slice(0, kk).split("");
        var inputs = grid.querySelectorAll("input"), cols = { run: [], rep: [], y: [] }; letters.forEach(function (n) { cols[n] = []; });
        function disp(l) { return l.split("").map(function (ch) { return nm[letters.indexOf(ch)]; }).join(" × "); }
        var ok = true; current = [];
        for (var i = 0; i < (1 << kk); i++) {
          current.push([]);
          for (var rr = 0; rr < R; rr++) {
            var v = optNum(inputs[i * R + rr]); if (!has(v)) { ok = false; }
            current[i].push(v); cols.run.push(i + 1); cols.rep.push(rr + 1); cols.y.push(v);
            for (var j = 0; j < kk; j++) { cols[letters[j]].push((i >> j) & 1 ? 1 : -1); }
          }
        }
        if (!ok) { o.appendChild(el("p", { "class": "error", text: "Fill every response cell." })); return; }
        var r = S.factorial(cols, { k: kk, replicates: R, factors: letters });
        var dp = autoDp(cols.y);
        var labels = Object.keys(r.effects);
        var rows = labels.map(function (l) { var row = [disp(l), fmt(r.effects[l], dp + 1), fmt(r.coefficients[l], dp + 2)]; if (r.anova) { row.push(r.anova[l].ss.toPrecision(5), fmt(r.anova[l].F, 2), fmtP(r.anova[l].p)); } return row; });
        var hdr = ["Term", "Effect (ȳ₊ − ȳ₋)", "Coefficient (effect / 2)"]; if (r.anova) { hdr.push("SS", "F", "p"); }
        o.appendChild(table("Effects (grand mean " + fmt(r.grand_mean, dp + 1) + ")", hdr, rows));
        if (r.anova) {
          o.appendChild(table("Residual", ["Quantity", "Value"], [["Residual SS", r.anova.residual.ss.toPrecision(5)], ["Residual df", String(r.anova.residual.df)], ["Residual standard deviation", fmt(r.residual_sd, dp + 2)], ["Standard error of an effect = 2·√(MSE/N)", fmt(r.se_effect, dp + 2)], ["R²", fmt(r.r2, 4)], ["Adjusted R²", fmt(r.r2_adj, 4)]]));
        } else if (r.lenth) {
          o.appendChild(note("Unreplicated design: no residual, so no F-tests. Lenth's method (1989) estimates the noise from the small effects: s₀ = 1.5 × median|effect|, PSE = 1.5 × median of the |effects| below 2.5 s₀, margin of error ME = t(0.975, m/3) × PSE. Effects beyond ME are judged active; the simultaneous margin SME is the stricter limit for the whole set."));
          o.appendChild(table("Lenth's method", ["Quantity", "Value"], [["s₀", fmt(r.lenth.s0, dp + 2)], ["Pseudo standard error PSE", fmt(r.lenth.pse, dp + 2)], ["Degrees of freedom m/3", fmt(r.lenth.df, 2)], ["Margin of error ME", fmt(r.lenth.me, dp + 2)], ["Simultaneous margin SME", fmt(r.lenth.sme, dp + 2)], ["Effects beyond ME", r.lenth.active.length ? r.lenth.active.map(disp).join(", ") : "none"]]));
        }
        var ref = r.anova ? S.tPpf(0.975, r.anova.residual.df) * r.se_effect : (r.lenth ? r.lenth.me : null);
        o.appendChild(figure(barChart({ id: node.id + "-p", items: labels.map(function (l) { return { label: disp(l), value: r.effects[l] }; }), sort: true, dp: dp + 1, title: "Pareto of effects (absolute value)", desc: "Horizontal bars of the absolute effect of each term, largest first." + (ref ? " A reference line marks the effect size that would be significant at the 5 % level." : ""), refLine: ref, refLabel: ref ? "t₀.₉₇₅ × SE" : "" })));
        var cm = Object.keys(r.cell_means).map(function (c) { return [c, fmt(r.cell_means[c], dp + 1)]; });
        o.appendChild(table("Cell means (label = factors at the high level)", ["Treatment", "Mean response"], cm));
      }
      k.addEventListener("change", function () { current = null; buildGrid(); });
      reps.addEventListener("change", function () { current = null; buildGrid(); });
      names.addEventListener("change", buildGrid);
      run.addEventListener("click", compute);
      buildGrid();
      if (current) { compute(); }
    }
  };

  // ================================================================ 9. CLT and control chart simulator
  function mulberry32(seed) { var a = seed >>> 0; return function () { a = (a + 0x6D2B79F5) >>> 0; var t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }
  function parentSampler(kind, rnd) {
    function normal() { var u = 1 - rnd(), v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); }
    if (kind === "uniform") { return function () { return (rnd() - 0.5) * Math.sqrt(12); }; }
    if (kind === "exponential") { return function () { return -Math.log(1 - rnd()) - 1; }; }
    if (kind === "bimodal") { return function () { return (rnd() < 0.5 ? -1 : 1) * 0.95 + 0.35 * normal(); }; }
    return normal;
  }
  Calc.simulator = {
    mount: function (node, data) {
      var f = el("div");
      var parent = select("parent", [["normal", "Normal (mean 0, σ 1)"], ["uniform", "Uniform (flat, σ 1)"], ["exponential", "Exponential, shifted (right-skewed, σ 1)"], ["bimodal", "Bimodal (two modes at ±0.95)"]], data.parent || "exponential");
      var n = num("n", data.n || 5, { min: 1, max: 25, step: 1 }), kk = num("k", data.k || 40, { min: 10, max: 200, step: 1 }), shift = num("shift", has(data.shift) ? data.shift : 1.0, { step: 0.25 }), at = num("at", data.shiftAt || 25, { min: 5, step: 1 }), seed = num("seed", data.seed || 7, { min: 1, step: 1 }), reps = num("reps", data.repeats || 200, { min: 10, max: 2000, step: 10 });
      f.appendChild(el("div", { "class": "calc-grid" }, [field("Parent distribution of individual values", parent), field("Subgroup size n", n), field("Number of subgroups k", kk)]));
      f.appendChild(el("div", { "class": "calc-grid" }, [field("Shift in the mean after the change point (in σ of individuals)", shift), field("Change point: after subgroup", at), field("Random seed", seed), field("Repeats for the detection statistics", reps)]));
      var run = button("Simulate"), again = button("New seed", "secondary");
      f.appendChild(el("div", { "class": "row" }, [run, again]));
      node.appendChild(f);
      function simulate() {
        var o = outBox(node), N = Math.max(1, Math.round(optNum(n) || 5)), K = Math.max(10, Math.round(optNum(kk) || 40)), dlt = optNum(shift) || 0, A = Math.min(K - 1, Math.max(5, Math.round(optNum(at) || 25))), sd = Math.round(optNum(seed) || 7);
        var rnd = mulberry32(sd), draw = parentSampler(parent.value, rnd);
        var indiv = [], means = [], ranges = [], sds = [];
        for (var g = 0; g < K; g++) {
          var s = []; for (var i = 0; i < N; i++) { var v = draw() + (g >= A ? dlt : 0); s.push(v); indiv.push(v); }
          var m = 0; s.forEach(function (x) { m += x; }); m /= N; means.push(m);
          ranges.push(Math.max.apply(null, s) - Math.min.apply(null, s));
        }
        // histograms: individuals (first A subgroups only, in control) and means
        var baseInd = indiv.slice(0, A * N), hi = S.histogram(baseInd, 20), hm = S.histogram(means.slice(0, A), Math.max(6, Math.min(15, Math.ceil(Math.sqrt(A)))));
        var dI = S.descriptive(baseInd), dM = S.descriptive(means.slice(0, A));
        o.appendChild(h4("1. The distribution of subgroup means is tighter and closer to normal than the parent"));
        o.appendChild(el("div", { "class": "cols2" }, [
          figure(histogram({ id: node.id + "-hi", edges: hi.edges, counts: hi.counts, mean: dI.mean, sigma: dI.s, n: baseInd.length, dp: 2, xlabel: "Individual value", title: "Individual values (before the shift)", desc: "Histogram of the simulated individual values with a normal curve of the same mean and standard deviation." }), "s of individuals = " + fmt(dI.s, 3) + "; skewness " + fmt(dI.skewness, 2)),
          figure(histogram({ id: node.id + "-hm", edges: hm.edges, counts: hm.counts, mean: dM.mean, sigma: dM.s, n: A, dp: 2, xlabel: "Subgroup mean (n = " + N + ")", title: "Subgroup means (before the shift)", desc: "Histogram of the subgroup means with a normal curve." }), "s of means = " + fmt(dM.s, 3) + " (theory: σ/√n = " + fmt(1 / Math.sqrt(N), 3) + "); skewness " + fmt(dM.skewness, 2))]));
        // control chart with limits from the baseline
        o.appendChild(h4("2. An X̄ chart with limits from the first " + A + " subgroups, then a shift of " + fmt(dlt, 2) + "σ"));
        var ch;
        if (N === 1) {
          var b = S.imrChart(indiv.slice(0, A));
          ch = { center: b.xbar, ucl: b.ucl_x, lcl: b.lcl_x, sig: b.sigma_within };
        } else {
          var flat = [], grp = []; for (var q = 0; q < A; q++) { for (var w = 0; w < N; w++) { flat.push(indiv[q * N + w]); grp.push(q + 1); } }
          var br = S.xbarRChart(flat, grp);
          ch = { center: br.xbarbar, ucl: br.ucl_x, lcl: br.lcl_x, sig: br.A2 * br.rbar / 3 };
        }
        var rules = S.runRules(means, ch.center, ch.sig);
        var warn = []; ["we2", "we3", "we4"].forEach(function (r) { rules[r].forEach(function (i) { if (warn.indexOf(i) < 0) { warn.push(i); } }); });
        o.appendChild(figure(controlChart({ id: node.id + "-cc", values: means, center: ch.center, ucl: ch.ucl, lcl: ch.lcl, signals: rules.we1, warn: warn, zones: ch.sig, dp: 2, baseline: A, title: N === 1 ? "Individuals chart" : "X̄ chart (n = " + N + ")", desc: "Subgroup means against limits computed from the baseline subgroups; the change point is marked.", ylabel: "Subgroup mean", centerLabel: "x̄̄" })));
        function firstAfter(list, after) { for (var i = 0; i < list.length; i++) { if (list[i] > after) { return list[i]; } } return null; }
        function falseBefore(list, after) { return list.filter(function (i) { return i <= after; }).length; }
        var sets = [["WE 1 only", ["we1"]], ["WE 1 to 4", ["we1", "we2", "we3", "we4"]], ["Nelson 1 to 8", ["we1", "we2", "we3", "n2", "n3", "n4", "n7", "n8"]]];
        var one = sets.map(function (st) { var hits = []; st[1].forEach(function (r) { hits = hits.concat(rules[r]); }); hits.sort(function (a, b) { return a - b; }); var fa = firstAfter(hits, A); return [st[0], fa ? "subgroup " + fa + " (" + (fa - A) + " after the change)" : "not detected in " + (K - A) + " subgroups", String(falseBefore(hits, A))]; });
        o.appendChild(table("This run: first signal after the change point", ["Rule set", "First signal", "Signals before the change (false alarms in " + A + " subgroups)"], one));
        // repeated runs
        var R = Math.max(10, Math.round(optNum(reps) || 200)), totals = sets.map(function () { return { sum: 0, det: 0, fa: 0 }; });
        for (var rr = 0; rr < R; rr++) {
          var rnd2 = mulberry32(sd * 7919 + rr + 1), draw2 = parentSampler(parent.value, rnd2), ms = [], fl = [], gp = [];
          for (var g2 = 0; g2 < K; g2++) { var mm = 0; for (var i2 = 0; i2 < N; i2++) { var v2 = draw2() + (g2 >= A ? dlt : 0); mm += v2; if (g2 < A) { fl.push(v2); gp.push(g2 + 1); } } ms.push(mm / N); }
          var c2 = N === 1 ? (function () { var b2 = S.imrChart(fl); return { center: b2.xbar, sig: b2.sigma_within }; })() : (function () { var b3 = S.xbarRChart(fl, gp); return { center: b3.xbarbar, sig: b3.A2 * b3.rbar / 3 }; })();
          var ru = S.runRules(ms, c2.center, c2.sig);
          sets.forEach(function (st, si) { var hits = []; st[1].forEach(function (r) { hits = hits.concat(ru[r]); }); hits.sort(function (a, b) { return a - b; }); var fa = firstAfter(hits, A); if (fa) { totals[si].det++; totals[si].sum += fa - A; } totals[si].fa += falseBefore(hits, A) > 0 ? 1 : 0; });
        }
        o.appendChild(table(R + " repeated simulations with different seeds", ["Rule set", "Detected within " + (K - A) + " subgroups", "Mean subgroups to detection (when detected)", "Runs with at least one false alarm in the " + A + " baseline subgroups"], totals.map(function (t, i) { return [sets[i][0], fmt(100 * t.det / R, 0) + " %", t.det ? fmt(t.sum / t.det, 1) : "–", fmt(100 * t.fa / R, 0) + " %"]; })));
        o.appendChild(note("Adding rules shortens the time to detect a shift and raises the false-alarm rate at the same time. Neither number is free. With a non-normal parent, note how the means still look close to normal for n of 4 or 5, which is why X̄ charts are robust and individuals charts on skewed data are not."));
      }
      run.addEventListener("click", simulate);
      again.addEventListener("click", function () { seed.value = String(Math.floor(Math.random() * 100000) + 1); simulate(); });
      simulate();
    }
  };

  // ------------------------------------------------------------ mounting
  Calc.mount = function (node) {
    var type = node.getAttribute("data-calc"), data = readData(node);
    if (!node.id) { node.id = "calc-" + type + "-" + Math.floor(Math.random() * 1e6); }
    if (!Calc[type] || !Calc[type].mount) { return; }
    try { Calc[type].mount(node, data); } catch (e) { node.appendChild(el("p", { "class": "error", text: "Calculator error: " + e.message })); }
    if (data.collapsed) {
      // Worked examples repeat the calculator with its inputs folded away; the output stays visible.
      var form = null;
      Array.prototype.forEach.call(node.children, function (c) { if (!form && c.tagName === "DIV" && !c.classList.contains("calc-out")) { form = c; } });
      if (form) {
        var det = el("details", null, [el("summary", { text: "Show the inputs (edit and recompute)" })]);
        node.insertBefore(det, form);
        det.appendChild(form);
      }
    }
  };
  Calc.mountAll = function () {
    if (!S) { return; }
    Array.prototype.forEach.call(document.querySelectorAll("[data-calc]"), Calc.mount);
  };
  Calc.charts = { controlChart: controlChart, histogram: histogram, barChart: barChart };
  if (typeof document !== "undefined") { document.addEventListener("DOMContentLoaded", Calc.mountAll); }
  root.Calc = Calc;
})(typeof self !== "undefined" ? self : this);
