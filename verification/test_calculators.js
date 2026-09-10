/*
 * test_calculators.js - Check 4 and the unit-test suite for assets/js/stats.js.
 *
 * 1. Tests every numerical function in stats.js against scipy at the points
 *    written by tables.py to results/_refpoints.json (200 or more per
 *    function). Accuracy targets from CLAUDE.md: normal CDF 1e-7, inverse
 *    normal 1e-6, t and F CDF 1e-5 (chi-square held to the same).
 * 2. Checks the constants table embedded in stats.js against
 *    verification/constants.json.
 * 3. Runs every engine on every example in verification/data/ and compares
 *    every numeric and string leaf of results/<id>.json to the JS output at
 *    the same path.
 *
 * Run: node verification/test_calculators.js   (exit code 1 on any failure)
 */
"use strict";
const fs = require("fs");
const path = require("path");
const Stats = require(path.join(__dirname, "..", "assets", "js", "stats.js"));

const HERE = __dirname;
const DATA = path.join(HERE, "data");
const RESULTS = path.join(HERE, "results");
let failures = 0;
const report = [];

function fail(msg) { failures++; console.log("  FAIL " + msg); }

// --- 1. numerical functions -----------------------------------------------
const pts = JSON.parse(fs.readFileSync(path.join(RESULTS, "_refpoints.json"), "utf8"));
// reference rows are stored as [parameters..., argument, value]; the
// functions take (argument, parameters...), so the arguments are rotated
function testFn(name, arr, fn, target, relative, rotate) {
  let worst = 0, n = 0;
  for (const row of arr) {
    const want = row[row.length - 1];
    let args = row.slice(0, row.length - 1);
    if (rotate) args = [args[args.length - 1]].concat(args.slice(0, args.length - 1));
    const got = fn.apply(null, args);
    let err = Math.abs(got - want);
    if (relative) err /= Math.max(1e-300, Math.abs(want));
    if (!(err <= target)) { fail(`${name}(${row.slice(0, -1).join(", ")}) = ${got}, scipy ${want}`); }
    if (err > worst) worst = err;
    n++;
  }
  report.push(`${name}: ${n} points, max ${relative ? "relative" : "absolute"} error ${worst.toExponential(2)} (target ${target})`);
}
testFn("normCdf", pts.normcdf, Stats.normCdf, 1e-7, false);
testFn("normPpf", pts.norminv, Stats.normPpf, 1e-6, false);
testFn("erf", pts.erf, Stats.erf, 1e-7, false);
testFn("tCdf", pts.tcdf, Stats.tCdf, 1e-5, false, true);
testFn("fCdf", pts.fcdf, Stats.fCdf, 1e-5, false, true);
testFn("chi2Cdf", pts.chi2cdf, Stats.chi2Cdf, 1e-5, false, true);
testFn("tPpf", pts.tinv, Stats.tPpf, 1e-6, true, true);
testFn("fPpf", pts.finv, Stats.fPpf, 1e-6, true, true);
testFn("chi2Ppf", pts.chi2inv, Stats.chi2Ppf, 1e-6, true, true);
testFn("lgamma", pts.lgamma, Stats.lgamma, 1e-10, true);

// --- 2. constants -----------------------------------------------------------
const consts = JSON.parse(fs.readFileSync(path.join(HERE, "constants.json"), "utf8"));
let nconst = 0;
for (const n in consts) {
  for (const k in consts[n]) {
    nconst++;
    if (!Stats.CONSTANTS[n] || Math.abs(Stats.CONSTANTS[n][k] - consts[n][k]) > 1e-12) fail(`constant ${k} n=${n}: stats.js ${Stats.CONSTANTS[n] && Stats.CONSTANTS[n][k]} vs constants.json ${consts[n][k]}`);
  }
}
report.push(`constants: ${nconst} entries match constants.json`);

// --- 3. engines on every example ---------------------------------------------
function readCsv(p) {
  const lines = fs.readFileSync(p, "utf8").split(/\r?\n/).filter(function (l) { return l.length; });
  const header = lines[0].split(",");
  const cols = {}; header.forEach(function (h) { cols[h] = []; });
  for (let i = 1; i < lines.length; i++) {
    const parts = lines[i].split(",");
    header.forEach(function (h, j) { const v = parts[j]; cols[h].push(v !== "" && !isNaN(Number(v)) ? Number(v) : v); });
  }
  return cols;
}

function run(meta, cols) {
  const p = meta.params || {};
  switch (meta.kind) {
    case "capability": return Stats.capability(cols.x, p, cols.subgroup);
    case "imr": return Stats.imrChart(cols.x);
    case "xbar_r": return Stats.xbarRChart(cols.x, cols.subgroup);
    case "xbar_s": return Stats.xbarSChart(cols.x, cols.subgroup);
    case "p": return Stats.pChart(cols.n, cols.defectives);
    case "np": return Stats.npChart(p.n, cols.defectives);
    case "c": return Stats.cChart(cols.defects);
    case "u": return Stats.uChart(cols.n, cols.defects);
    case "ewma": return Stats.ewmaChart(cols.x, p);
    case "cusum": return Stats.cusumChart(cols.x, p);
    case "grr": return Stats.grr(cols, p);
    case "grr_summary": return Stats.grrFromMs(p.ms_full, p.df_full, p.ms_reduced, p.df_reduced, p.parts, p.operators, p.replicates, p.tolerance, p.study_var_k || 6, p.alpha_remove === undefined ? 0.05 : p.alpha_remove);
    case "factorial": return Stats.factorial(cols, p);
    case "ttest2": return Stats.ttest2(cols, p);
    case "anova1": return Stats.anova1(cols, p);
    case "paired": return Stats.paired(cols, p);
    case "ttest1": return Stats.oneSample(cols.x, p.mu0, p.alpha);
    case "regression": return Stats.regression(cols, p);
    case "samplesize": return Stats.sampleSize(p);
    case "dpmo": return Stats.dpmo(p.defects, p.units, p.opportunities);
    case "sigma_table": return Stats.sigmaTable(p);
    default: throw new Error("unknown kind " + meta.kind);
  }
}

const SKIP = { info_power_nct: true };
function compare(ref, got, pth, id) {
  let n = 0;
  if (ref === null || ref === undefined) {
    if (got !== null && got !== undefined) fail(`${id} ${pth}: results null, stats.js ${got}`);
    return 1;
  }
  if (Array.isArray(ref)) {
    if (!Array.isArray(got) || got.length !== ref.length) { fail(`${id} ${pth}: array length ${ref.length} vs ${got && got.length}`); return 1; }
    for (let i = 0; i < ref.length; i++) n += compare(ref[i], got[i], pth + "." + i, id);
    return n;
  }
  if (typeof ref === "object") {
    for (const k in ref) {
      if (SKIP[k]) continue;
      if (got === undefined || got === null || !(k in got)) { fail(`${id} ${pth}.${k}: missing in stats.js output`); n++; continue; }
      n += compare(ref[k], got[k], pth ? pth + "." + k : k, id);
    }
    return n;
  }
  if (typeof ref === "boolean") { if (got !== ref) fail(`${id} ${pth}: ${ref} vs ${got}`); return 1; }
  if (typeof ref === "string") { if (got !== ref) fail(`${id} ${pth}: '${ref}' vs '${got}'`); return 1; }
  if (typeof ref === "number") {
    if (Number.isNaN(ref)) { if (!Number.isNaN(got)) fail(`${id} ${pth}: NaN vs ${got}`); return 1; }
    const isP = /(^|[._])p($|_|\.)|_p$|\.p$/.test(pth) || /p_/.test(pth.split(".").pop());
    const tol = isP ? 1e-6 : 1e-8;
    const err = Math.abs(ref - got) / Math.max(1, Math.abs(ref), Math.abs(got));
    if (!(err <= tol)) fail(`${id} ${pth}: results ${ref}, stats.js ${got}`);
    return 1;
  }
  return 0;
}

let nex = 0, nleaf = 0;
for (const f of fs.readdirSync(RESULTS).sort()) {
  if (!f.endsWith(".json") || f.startsWith("_")) continue;
  const doc = JSON.parse(fs.readFileSync(path.join(RESULTS, f), "utf8"));
  const meta = JSON.parse(fs.readFileSync(path.join(DATA, doc.id + ".json"), "utf8"));
  const csvPath = path.join(DATA, doc.id + ".csv");
  const cols = fs.existsSync(csvPath) ? readCsv(csvPath) : {};
  let got;
  try { got = run(meta, cols); } catch (e) { fail(`${doc.id}: stats.js threw ${e.message}`); continue; }
  const before = failures;
  const n = compare(doc.results, got, "", doc.id);
  nleaf += n; nex++;
  console.log(`  ${failures === before ? "OK  " : "FAIL"} ${doc.id}: ${n} values compared`);
}
report.push(`engines: ${nex} examples, ${nleaf} values compared with results/`);

console.log("");
for (const r of report) console.log("  " + r);
console.log(failures ? `test_calculators.js: ${failures} FAILURES` : "test_calculators.js: ALL PASSED");
process.exit(failures ? 1 : 0);
