"""
sanity.py - Check 3: consistency and reasonableness of everything in
verification/results/, and cross-check of the numbers printed on the HTML
pages against those results.

Part 1 (results): asserts the known relationships listed in CLAUDE.md, for
example Cpk <= Cp, Ppk = min(Ppu, Ppl), PPM equals the normal tail area from
the same Z, control-chart constants match constants.json for the subgroup
size, gauge R&R percentages are consistent, factorial effects reproduce the
cell means, p-values lie in [0, 1], and every published expected value in
the example registry was met.

Part 2 (pages): for each modules/*.html and the top-level pages, every
number token with two or more decimals must be a rounding (1 to 6 decimals)
of a value in the results of the examples the page declares
(<meta name="examples" content="id1, id2">), a data value in those
examples' CSVs, a control-chart constant, a statistical-table entry, or a
number listed in <meta name="allowed-numbers" content="...">. Narrative
claims are checked through data attributes:
  <span data-ex="id" data-key="overall.Ppk" data-dp="2">1.07</span>
    the displayed text must equal the results value rounded to data-dp
  <span data-claim data-ex="id" data-key="overall.Ppk" data-min="1.33">
    (or data-max) the value must satisfy the bound the text claims
"""
import csv
import glob
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
RESULTS = os.path.join(HERE, "results")
CONST = json.load(open(os.path.join(HERE, "constants.json")))

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)


def norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def near(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def in01(p, msg):
    check(p is None or (0.0 <= p <= 1.0), msg + f": p = {p}")


def check_rules(rules, n, tag):
    for k, lst in rules.items():
        check(lst == sorted(lst) and all(1 <= i <= n for i in lst), f"{tag}: rule {k} indices malformed")


def check_capability(ex_id, r, data):
    ov, wi, ch = r["overall"], r["within"], r["chart"]
    tag = ex_id
    x = data["x"]
    n = len(x)
    check(ov["mean"] is not None and near(ov["mean"], sum(x) / n), f"{tag}: mean")
    if ov.get("Pp") is not None:
        check(ov["Ppk"] <= ov["Pp"] + 1e-12, f"{tag}: Ppk > Pp")
        check(wi["Cwk"] <= wi["Cw"] + 1e-12, f"{tag}: Cwk > Cw")
        check(near(ov["Ppk"], min(ov["Ppu"], ov["Ppl"])), f"{tag}: Ppk != min(Ppu, Ppl)")
        if ov.get("Cpm") is not None:
            check(ov["Cpm"] <= ov["Pp"] + 1e-12, f"{tag}: Cpm > Pp")
        mid = (r["params"]["usl"] + r["params"]["lsl"]) / 2
        if abs(ov["mean"] - mid) < 1e-12:
            check(near(ov["Ppk"], ov["Pp"]), f"{tag}: centered but Ppk != Pp")
        else:
            check(ov["Ppk"] < ov["Pp"], f"{tag}: off-centre but Ppk == Pp")
        check(near(ov["Pp"] * (1 - ov["k"]), ov["Ppk"], 1e-9), f"{tag}: Cp(1-k) != Cpk")
    # PPM from the same Z as the index
    if ov.get("Ppu") is not None:
        check(near(ov["ppm_upper"], norm_sf(3 * ov["Ppu"]) * 1e6, 1e-9), f"{tag}: ppm_upper vs Z")
    if ov.get("Ppl") is not None:
        check(near(ov["ppm_lower"], norm_sf(3 * ov["Ppl"]) * 1e6, 1e-9), f"{tag}: ppm_lower vs Z")
    check(near(ov["ppm_total"], ov["ppm_upper"] + ov["ppm_lower"]), f"{tag}: ppm_total")
    # within vs overall sigma: within should not exceed overall by much
    ratio = wi["sigma"] / ov["s"]
    check(0.4 < ratio < 1.25, f"{tag}: within/overall sigma ratio {ratio:.3f} implausible")
    # constants used by the chart must match constants.json for its subgroup size
    if r["chart_type"] == "imr":
        check(near(ch["d2"], CONST["2"]["d2"]) and near(ch["D4"], CONST["2"]["D4"]), f"{tag}: I-MR constants")
        check(near(ch["ucl_x"] - ch["xbar"], 3 * ch["mrbar"] / 1.128), f"{tag}: I-MR limit formula")
    elif r["chart_type"] == "xbar_r":
        c = CONST[str(ch["n"])]
        check(all(near(ch[k], c[k]) for k in ("A2", "D3", "D4", "d2")), f"{tag}: Xbar-R constants for n={ch['n']}")
    else:
        c = CONST[str(ch["n"])]
        check(all(near(ch[k], c[k]) for k in ("A3", "B3", "B4", "c4")), f"{tag}: Xbar-S constants for n={ch['n']}")
    check(ch["lcl_x"] < ch.get("xbar", ch.get("xbarbar")) < ch["ucl_x"], f"{tag}: chart limits order")
    check_rules(ch["rules_x"], n if r["chart_type"] == "imr" else ch["k"], tag)
    stable_calc = len(ch["rules_x"]["we1"]) == 0 and len(ch.get("beyond_mr", ch.get("beyond_r", ch.get("beyond_s", [])))) == 0
    check(r["stable"] == stable_calc, f"{tag}: stable flag inconsistent")
    check(r["aiag_vda_2026_label"] == ("Cp/Cpk" if r["stable"] else "Pp/Ppk"), f"{tag}: convention label")
    in01(r.get("normal_p"), f"{tag}: AD p")
    lo, hi = ov["Ppk_ci95"]
    check(lo < ov["Ppk"] < hi, f"{tag}: Ppk CI does not contain Ppk")
    usl, lsl = r["params"].get("usl"), r["params"].get("lsl")
    nout = sum(1 for v in x if (usl is not None and v > usl) or (lsl is not None and v < lsl))
    check(nout == r["observed"]["n_out"], f"{tag}: observed out-of-spec count")
    check(near(r["legacy"]["Cpk"], wi["Cwk"]) and near(r["legacy"]["Ppk"], ov["Ppk"]), f"{tag}: legacy mapping")
    check(sum(r["histogram"]["counts"]) == n, f"{tag}: histogram counts")


def check_chart(ex_id, r, kind):
    tag = ex_id
    if kind == "imr":
        check(r["lcl_x"] < r["xbar"] < r["ucl_x"] and r["lcl_mr"] == 0.0, f"{tag}: limits")
        check_rules(r["rules_x"], r["n"], tag)
    elif kind in ("p", "u"):
        key = "pbar" if kind == "p" else "ubar"
        for i in range(r["k"]):
            check(r["lcl"][i] >= 0.0 and r["lcl"][i] <= r[key] <= r["ucl"][i], f"{tag}: limits at {i + 1}")
        check_rules(r["rules"], r["k"], tag)
    elif kind in ("np", "c"):
        key = "npbar" if kind == "np" else "cbar"
        check(r["lcl"] >= 0.0 and r["lcl"] <= r[key] <= r["ucl"], f"{tag}: limits")
        check_rules(r["rules"], r["k"], tag)
    elif kind == "ewma":
        n = r["n"]
        ucl = r["ucl"] if isinstance(r["ucl"], list) else [r["ucl"]] * n
        check(all(u <= r["ucl_asymptotic"] + 1e-12 for u in ucl), f"{tag}: exact limits exceed asymptotic")
        check(all(1 <= i <= n for i in r["signals"]), f"{tag}: signals")
        z = r["ewma"]
        check(all(min(min(z), r["target"]) - 1e-12 <= v <= max(max(z), r["target"]) + 1e-12 for v in z), f"{tag}: ewma range")
    elif kind == "cusum":
        check(all(v >= 0 for v in r["c_plus"]) and all(v >= 0 for v in r["c_minus"]), f"{tag}: cusum negative")


def check_grr(ex_id, r):
    tag = ex_id
    vc = r["varcomp"]
    check(all(v >= 0 for v in vc.values()), f"{tag}: negative variance component")
    check(near(vc["grr"], vc["repeatability"] + vc["reproducibility"]), f"{tag}: grr = rep + reprod")
    check(near(vc["reproducibility"], vc["operator"] + vc["interaction"]), f"{tag}: reprod = op + int")
    check(near(vc["total"], vc["grr"] + vc["part"]), f"{tag}: total")
    pc = r["pct_contribution"]
    check(near(pc["grr"] + pc["part"], 100.0), f"{tag}: %contribution sums to 100")
    sv = r["pct_study_var"]
    check(near((sv["grr"] ** 2 + sv["part"] ** 2), 100.0 ** 2, 1e-9), f"{tag}: %SV grr^2 + part^2 = 100^2")
    for k, v in vc.items():
        check(near(r["sd"][k] ** 2, v), f"{tag}: sd^2 != varcomp for {k}")
    check(r["ndc"] == max(1, math.floor(1.41 * r["sd"]["part"] / r["sd"]["grr"])), f"{tag}: ndc")
    check(r["interaction_removed"] == (r["interaction_p"] > r["alpha_remove"]), f"{tag}: interaction decision")
    for k in ("interaction_p", "p_operator", "p_part"):
        in01(r[k], f"{tag}: {k}")
    if "pct_tolerance" in r:
        check(near(r["pct_tolerance"]["grr"], 100 * r["study_var_k"] * r["sd"]["grr"] / r["tolerance"]), f"{tag}: %tolerance")


def check_factorial(ex_id, r, data):
    tag = ex_id
    names = r["params"]["factors"] if "params" in r else None
    y = data["y"]
    N = len(y)
    # each main effect equals mean at + minus mean at -
    for nm in names:
        plus = [y[i] for i in range(N) if data[nm][i] > 0]
        minus = [y[i] for i in range(N) if data[nm][i] < 0]
        check(near(r["effects"][nm], sum(plus) / len(plus) - sum(minus) / len(minus)), f"{tag}: effect {nm} vs means")
    # the saturated model reproduces every cell mean
    cells = {}
    for i in range(N):
        key = tuple(int(data[nm][i]) for nm in names)
        cells.setdefault(key, []).append(y[i])
    for key, ys in cells.items():
        pred = r["intercept"]
        for term, coef in r["coefficients"].items():
            s = 1
            for ch in term:
                s *= key[names.index(ch)]
            pred += coef * s
        check(near(pred, sum(ys) / len(ys), 1e-9), f"{tag}: model does not reproduce cell mean {key}")
    if "anova" in r:
        an = r["anova"]
        ss = sum(v["ss"] for k, v in an.items() if k not in ("residual", "total"))
        check(near(ss + an["residual"]["ss"], an["total"]["ss"], 1e-9), f"{tag}: SS do not add")
        for k, v in an.items():
            if "p" in v:
                in01(v["p"], f"{tag}: p for {k}")
        check(0 <= r["r2"] <= 1, f"{tag}: r2")


def check_tests(ex_id, r, kind):
    tag = ex_id
    if kind == "ttest2":
        for m in ("pooled", "welch"):
            in01(r[m]["p"], f"{tag}: {m} p")
            check(r[m]["ci"][0] < r["diff"] < r[m]["ci"][1], f"{tag}: {m} CI")
        check(r["pooled"]["df"] == r["n"][0] + r["n"][1] - 2, f"{tag}: pooled df")
        check(min(r["n"]) - 1 <= r["welch"]["df"] <= r["pooled"]["df"] + 1e-9, f"{tag}: Welch df range")
        in01(r["variance_tests"]["F_p"], f"{tag}: F p"); in01(r["variance_tests"]["levene_p"], f"{tag}: Levene p")
    elif kind == "anova1":
        in01(r["p"], f"{tag}: p"); check(0 <= r["eta2"] <= 1, f"{tag}: eta2")
        check(near(r["ss_between"] + r["ss_within"], r["ss_total"]), f"{tag}: SS")
        check(r["df_between"] + r["df_within"] == sum(r["n"]) - 1, f"{tag}: df")
    elif kind in ("paired", "ttest1"):
        in01(r["p"], f"{tag}: p"); check(r["ci"][0] < r["mean"] < r["ci"][1], f"{tag}: CI")
    elif kind == "regression":
        check(abs(sum(r["residuals"])) < 1e-8 * max(1.0, abs(r["mean_y"]) * r["n"]), f"{tag}: residuals sum")
        check(near(r["ss_regression"] + r["ss_residual"], r["ss_total"]), f"{tag}: SS")
        check(near(r["r"] ** 2, r["r2"]), f"{tag}: r^2 != R2")
        in01(r["p_slope"], f"{tag}: p"); check(r["slope_ci"][0] < r["slope"] < r["slope_ci"][1], f"{tag}: slope CI")
        check(near(r["t_slope"] ** 2, r["F"], 1e-9), f"{tag}: t^2 != F")
    elif kind == "samplesize":
        check(r["n_t"] >= r["n_z"] == math.ceil(r["n_z_exact"]), f"{tag}: sample sizes")


def load_data(ex_id):
    p = os.path.join(DATA, ex_id + ".csv")
    cols = {}
    if os.path.exists(p):
        with open(p, newline="") as f:
            rd = csv.reader(f); header = next(rd); cols = {h: [] for h in header}
            for row in rd:
                for h, v in zip(header, row):
                    try: cols[h].append(float(v))
                    except ValueError: cols[h].append(v)
    return cols


def check_results():
    n = 0
    for path in sorted(glob.glob(os.path.join(RESULTS, "*.json"))):
        if os.path.basename(path).startswith("_"):
            continue
        doc = json.load(open(path))
        ex_id, kind, r = doc["id"], doc["kind"], doc["results"]
        r["params"] = doc["params"]
        data = load_data(ex_id)
        check(doc["expected_ok"], f"{ex_id}: a published expected value was not met")
        if kind == "capability": check_capability(ex_id, r, data)
        elif kind in ("imr", "p", "np", "c", "u", "ewma", "cusum"): check_chart(ex_id, r, kind)
        elif kind in ("grr", "grr_summary"): check_grr(ex_id, r)
        elif kind == "factorial": check_factorial(ex_id, r, data)
        else: check_tests(ex_id, r, kind)
        n += 1
    return n


# --------------------------------------------------------------------------
# Part 2: pages
# --------------------------------------------------------------------------
def leaves(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from leaves(v, f"{prefix}.{k}" if prefix else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from leaves(v, f"{prefix}.{i}")
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        yield prefix, obj


def roundings(v):
    out = set()
    for d in range(0, 7):
        out.add(f"{v:.{d}f}")
        out.add(f"{round(v, d):g}")
    if abs(v) >= 1000:
        out.add(f"{v:,.0f}"); out.add(f"{v:,.1f}")
    return out


def resolve(obj, path):
    cur = obj
    for part in path.split("."):
        cur = cur[int(part)] if isinstance(cur, list) else cur[part]
    return cur


NUMBER_RE = re.compile(r"(?<![\w.])-?\d{1,3}(?:,\d{3})*\.\d{2,}|(?<![\w.])-?\d+\.\d{2,}")
TAG_RE = re.compile(r"<[^>]+>")


def allowed_from_tables():
    p = os.path.join(RESULTS, "_tables.json")
    s = set()
    if os.path.exists(p):
        t = json.load(open(p))
        for _, v in leaves(t):
            s |= roundings(v)
    for n, row in CONST.items():
        for k, v in row.items():
            s |= roundings(v)
    return s


def check_pages():
    pages = sorted(glob.glob(os.path.join(ROOT, "modules", "*.html")) + glob.glob(os.path.join(ROOT, "*.html")))
    if not pages:
        print("  (no HTML pages yet)")
        return 0
    table_numbers = allowed_from_tables()
    checked = 0
    for page in pages:
        html = open(page, encoding="utf-8").read()
        rel = os.path.relpath(page, ROOT)
        m = re.search(r'<meta name="examples" content="([^"]*)"', html)
        ex_ids = [s.strip() for s in m.group(1).split(",") if s.strip()] if m else []
        allowed = set(table_numbers)
        m2 = re.search(r'<meta name="allowed-numbers" content="([^"]*)"', html)
        if m2:
            allowed |= set(m2.group(1).split())
        results = {}
        for ex_id in ex_ids:
            rp = os.path.join(RESULTS, ex_id + ".json")
            check(os.path.exists(rp), f"{rel}: declared example {ex_id} has no results file")
            if not os.path.exists(rp):
                continue
            doc = json.load(open(rp))
            results[ex_id] = doc["results"]
            for _, v in leaves(doc["results"]):
                allowed |= roundings(v)
            for _, v in leaves(doc["params"]):
                allowed |= roundings(v)
            for col, vals in load_data(ex_id).items():
                for v in vals:
                    if isinstance(v, float):
                        allowed |= roundings(v)
        # data-ex spans: displayed text must equal the rounded value
        for sm in re.finditer(r'<(?:span|td|strong|b)[^>]*data-ex="([^"]+)"[^>]*data-key="([^"]+)"[^>]*>(.*?)</', html):
            ex_id, key, text = sm.group(1), sm.group(2), TAG_RE.sub("", sm.group(3)).strip()
            dp = re.search(r'data-dp="(\d+)"', sm.group(0))
            claim = "data-claim" in sm.group(0)
            if ex_id not in results:
                check(False, f"{rel}: data-ex refers to undeclared example {ex_id}")
                continue
            try:
                val = resolve(results[ex_id], key)
            except (KeyError, IndexError, TypeError):
                check(False, f"{rel}: key {key} not in results of {ex_id}")
                continue
            if dp and not claim:
                shown = text.replace(",", "").replace("−", "-")
                want = f"{val:.{int(dp.group(1))}f}"
                check(shown == want, f"{rel}: {ex_id} {key} shows '{text}', results give {want}")
                checked += 1
            mn = re.search(r'data-min="([-\d.]+)"', sm.group(0))
            mx = re.search(r'data-max="([-\d.]+)"', sm.group(0))
            if mn: check(val >= float(mn.group(1)), f"{rel}: claim {ex_id} {key} = {val} is below {mn.group(1)}"); checked += 1
            if mx: check(val <= float(mx.group(1)), f"{rel}: claim {ex_id} {key} = {val} is above {mx.group(1)}"); checked += 1
        # every number with >= 2 decimals in the visible text must be traceable
        body = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
        body = re.sub(r"<style.*?</style>", " ", body, flags=re.S)
        body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
        text = TAG_RE.sub(" ", body)
        unknown = set()
        for nm in NUMBER_RE.finditer(text):
            tok = nm.group(0)
            norm = tok.replace(",", "")
            if tok in allowed or norm in allowed or norm.lstrip("-") in allowed:
                continue
            try:
                v = float(norm)
            except ValueError:
                continue
            if any(f"{v:.{d}f}" in allowed for d in range(2, 7)):
                continue
            unknown.add(tok)
        check(not unknown, f"{rel}: numbers not traceable to results: {sorted(unknown)[:15]}")
        checked += 1
    return checked


def main():
    n = check_results()
    print(f"  {n} results files checked")
    p = check_pages()
    print(f"  {p} page checks")
    if failures:
        for f in failures:
            print("  FAIL", f)
        print(f"sanity.py: {len(failures)} FAILURES")
        return 1
    print("sanity.py: ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
