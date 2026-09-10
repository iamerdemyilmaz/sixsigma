"""
compute.py - Check 1: every statistic shown on a page is computed here from
the CSV in verification/data/ using numpy, scipy and statsmodels, and written
to verification/results/<id>.json. Nothing on a page is typed by hand.

Conventions (see PROGRESS.md decision 7 and SOURCES.md S-A2):
  overall.*   indices from the overall sample standard deviation s (n-1).
              Under the 2026 AIAG & VDA / ISO 22514 convention these are
              Cp/Cpk when stability was shown, Pp/Ppk otherwise; the formula
              is the same. Stored as Pp/Ppk here; the page applies the letter.
  within.*    indices from the within-subgroup sigma (Rbar/d2, Sbar/c4 or
              MRbar/d2). AIAG & VDA 2026 calls these Cw/Cwk (p. 51-52);
              the legacy 2005 AIAG convention and most software call them
              Cp/Cpk. Stored as Cw/Cwk.
  legacy.*    the same numbers under the 2005 labels, for supplier reports.
  vsm, funnel  Module 2 (process thinking): value-stream lead time/PCE, and
              the four funnel-experiment rules. See generate.py for the kind.
Control-chart constants come from verification/constants.json (tables.py),
rounded to the precision of published tables. The individuals chart uses
3 * MRbar / 1.128 (NIST 6.3.2.2), not the 3-decimal E2.
"""
import csv
import json
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.diagnostic import normal_ad

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
RESULTS = os.path.join(HERE, "results")
os.makedirs(RESULTS, exist_ok=True)
CONST = json.load(open(os.path.join(HERE, "constants.json")))
D2_MR = CONST["2"]["d2"]  # 1.128


def load(ex_id):
    meta = json.load(open(os.path.join(DATA, ex_id + ".json")))
    cols = {}
    p = os.path.join(DATA, ex_id + ".csv")
    if os.path.exists(p):
        with open(p, newline="") as f:
            r = csv.reader(f)
            header = next(r)
            cols = {h: [] for h in header}
            for row in r:
                for h, v in zip(header, row):
                    try:
                        cols[h].append(float(v))
                    except ValueError:
                        cols[h].append(v)
    return meta, cols


# --------------------------------------------------------------------------
# Building blocks
# --------------------------------------------------------------------------
def descriptive(x):
    x = np.asarray(x, float)
    n = len(x)
    out = {"n": n, "mean": float(x.mean()), "median": float(np.median(x)),
           "s": float(x.std(ddof=1)) if n > 1 else float("nan"),
           "variance": float(x.var(ddof=1)) if n > 1 else float("nan"),
           "sd_pop": float(x.std(ddof=0)), "ss": float(((x - x.mean()) ** 2).sum()), "sum": float(x.sum()),
           "min": float(x.min()), "max": float(x.max()), "range": float(x.max() - x.min()),
           "q1": float(np.percentile(x, 25, method="weibull")),
           "q3": float(np.percentile(x, 75, method="weibull")),
           "skewness": float(stats.skew(x, bias=False)) if n > 2 else float("nan"),
           "kurtosis_excess": float(stats.kurtosis(x, bias=False)) if n > 3 else float("nan")}
    out["sem"] = out["s"] / math.sqrt(n)
    if n >= 8:
        a2, p = normal_ad(x)  # raw A2 statistic; p from the adjusted A2* (Stephens 1986)
        a2 = float(a2)
        out["ad_A2"] = a2
        out["ad_A2_adjusted"] = a2 * (1.0 + 0.75 / n + 2.25 / n ** 2)
        out["ad_p"] = float(p)
    return out


def descriptive_block(x, params):
    """Plain descriptive statistics with a histogram; optional count outside
    specification limits and optional statistics of ln(x) (for a lognormal
    check). No capability index: Module 1 only summarises."""
    x = np.asarray(x, float)
    out = {"descriptive": descriptive(x), "histogram": histogram(x)}
    usl, lsl = params.get("usl"), params.get("lsl")
    if usl is not None or lsl is not None:
        n_out = int(sum(1 for v in x if (usl is not None and v > usl) or (lsl is not None and v < lsl)))
        out["observed"] = {"n_out": n_out, "fraction_out": n_out / len(x)}
    if params.get("log"):
        lx = np.log(x)
        out["log"] = descriptive(lx)
        out["log"]["geometric_mean"] = float(math.exp(lx.mean()))
    return out


def subgroup_means(x, params):
    """Means of consecutive subgroups of the given sizes, to show the central
    limit theorem on printed data: the spread of the means against s/sqrt(n)
    and the skewness of the means against that of the individuals."""
    x = np.asarray(x, float)
    d = descriptive(x)
    out = {"individuals": {"n": int(len(x)), "mean": d["mean"], "s": d["s"], "skewness": d["skewness"], "ad_p": d["ad_p"]}}
    for n in params["sizes"]:
        k = len(x) // n
        m = x[:k * n].reshape(k, n).mean(axis=1)
        dm = descriptive(m)
        blk = {"n": int(n), "k": int(k), "means": [float(v) for v in m], "mean_of_means": dm["mean"],
               "sd_of_means": dm["s"], "s_over_sqrt_n": d["s"] / math.sqrt(n), "ratio": dm["s"] / (d["s"] / math.sqrt(n)),
               "skewness_of_means": dm["skewness"]}
        if k >= 8:
            blk["ad_p"] = dm["ad_p"]
        out[f"n{n}"] = blk
    return out


def binomial_poisson(params):
    """Binomial and Poisson probabilities for a list of counts k."""
    n, p, lam, ks = params["n"], params["p"], params["lambda"], [int(k) for k in params["k"]]
    b = {"n": n, "p": p, "k": ks, "mean": n * p, "sd": math.sqrt(n * p * (1 - p)),
         "pmf": [float(stats.binom.pmf(k, n, p)) for k in ks], "cdf": [float(stats.binom.cdf(k, n, p)) for k in ks]}
    po = {"lambda": lam, "k": ks, "mean": lam, "sd": math.sqrt(lam),
          "pmf": [float(stats.poisson.pmf(k, lam)) for k in ks], "cdf": [float(stats.poisson.cdf(k, lam)) for k in ks]}
    return {"binomial": b, "poisson": po}


def vsm_metrics(params):
    """Value-stream lead time and process cycle efficiency (Module 2).
    Inventory converted to days by the standard VSM shorthand: quantity
    divided by the daily customer requirement. Total lead time is that
    inventory time plus the value-add (cycle) time; PCE is the cycle time's
    share of the lead time."""
    demand = float(params["daily_demand_pieces"])
    opsec = float(params["operating_seconds_per_day"])
    steps = params["steps"]
    total_ct_s = float(sum(s["ct_s"] for s in steps))
    total_ct_days = total_ct_s / opsec
    inv_out = []
    total_inv_days = 0.0
    for item in params["inventory"]:
        d = float(item["wip_pieces"]) / demand
        inv_out.append({"name": item["name"], "wip_pieces": item["wip_pieces"], "days": d})
        total_inv_days += d
    total_lead_days = total_inv_days + total_ct_days
    return {"takt_s": opsec / demand, "steps": steps, "total_ct_s": total_ct_s, "total_ct_days": total_ct_days,
            "inventory": inv_out, "total_inventory_days": total_inv_days,
            "total_lead_time_days": total_lead_days, "pce_pct": 100.0 * total_ct_days / total_lead_days,
            "lead_time_to_ct_ratio": total_lead_days / total_ct_days}


def funnel_sim(e, params):
    """The funnel experiment's four rules (Module 2), applied to the same
    noise sequence e. Rule 1: fixed funnel, x = e. Rule 2: move the funnel
    from its last position by -(last deviation), giving x[k] = e[k] - e[k-1].
    Rule 3: move the funnel to -(last deviation) measured from the target,
    giving x[k] = e[k] - x[k-1]. Rule 4: move the funnel to the last resting
    spot, giving the cumulative sum x[k] = x[k-1] + e[k]. Every x[k] is a
    fixed, mean-zero combination of the e's, so E[x_k] = 0 exactly and
    Var(x_k) = E[x_k^2]: Rule 1 is sigma^2 for every k; Rule 2 is 2*sigma^2
    for every k >= 2; Rules 3 and 4 grow as k*sigma^2 (a genuine random walk
    for Rule 4, an alternating one for Rule 3). Because the true mean is
    known to be zero, the mean of x_k^2 over a window (not the window's own
    sample variance, which is the wrong statistic for a non-stationary
    series) is the unbiased way to estimate the average Var(x_k) over that
    window: sigma^2 * mean(k) for k in the window."""
    e = np.asarray(e, float)
    n = len(e)
    sigma = float(params["sigma"])
    x1 = e.copy()
    x2 = np.empty(n); x2[0] = e[0]
    x2[1:] = e[1:] - e[:-1]
    x3 = np.empty(n); x3[0] = e[0]
    for k in range(1, n):
        x3[k] = e[k] - x3[k - 1]
    x4 = np.cumsum(e)

    def meansq(arr, a, b):  # 1-indexed inclusive window, mean of x_k^2 (deviation from the known-zero target)
        return float(np.mean(arr[a - 1:b] ** 2))

    w = min(25, n // 2)
    rules = {}
    for name, arr in (("rule1", x1), ("rule2", x2), ("rule3", x3), ("rule4", x4)):
        rules[name] = {"x": [float(v) for v in arr], "var_all": float(np.var(arr, ddof=1)),
                        "meansq_first_w": meansq(arr, 1, w), "meansq_last_w": meansq(arr, n - w + 1, n)}
    rules["rule1"]["theory_var"] = sigma ** 2
    rules["rule2"]["theory_var"] = 2 * sigma ** 2
    for name in ("rule3", "rule4"):
        rules[name]["theory_meansq_first_w"] = sigma ** 2 * (1 + w) / 2.0
        rules[name]["theory_meansq_last_w"] = sigma ** 2 * ((n - w + 1) + n) / 2.0
    return {"n": n, "sigma": sigma, "w": w, "rules": rules}


def funnel_growth(cols, params):
    """Monte Carlo backing for the funnel experiment's variance-growth claim
    (Module 2). cols holds R independent noise replications (columns e0, e1,
    ...), each of length n. For each replication the four rules are applied
    (as in funnel_sim) and the value at each checkpoint drop is squared;
    averaging that square over the R independent replications is a proper,
    low-noise Monte Carlo estimate of Var(x_k) at that drop (since E[x_k]=0
    exactly for all four rules). The first replication is also returned in
    full, as the illustrative single path drawn in the trajectory figure."""
    sigma = float(params["sigma"])
    checkpoints = [int(c) for c in params["checkpoints"]]
    rep_cols = sorted((k for k in cols if k.startswith("e")), key=lambda k: int(k[1:]))
    n = len(cols[rep_cols[0]])
    R = len(rep_cols)

    def rules_of(e):
        e = np.asarray(e, float)
        x1 = e.copy()
        x2 = np.empty(n); x2[0] = e[0]; x2[1:] = e[1:] - e[:-1]
        x3 = np.empty(n); x3[0] = e[0]
        for k in range(1, n):
            x3[k] = e[k] - x3[k - 1]
        x4 = np.cumsum(e)
        return {"rule1": x1, "rule2": x2, "rule3": x3, "rule4": x4}

    illustrative = {name: [float(v) for v in arr] for name, arr in rules_of(cols[rep_cols[0]]).items()}
    sums = {name: {cp: 0.0 for cp in checkpoints} for name in ("rule1", "rule2", "rule3", "rule4")}
    for rc in rep_cols:
        for name, arr in rules_of(cols[rc]).items():
            for cp in checkpoints:
                sums[name][cp] += float(arr[cp - 1]) ** 2
    theory = {"rule1": lambda cp: sigma ** 2, "rule2": lambda cp: 2 * sigma ** 2,
              "rule3": lambda cp: cp * sigma ** 2, "rule4": lambda cp: cp * sigma ** 2}
    growth = {}
    for name in sums:
        growth[name] = {}
        for cp in checkpoints:
            growth[name][f"meansq_at_{cp}"] = sums[name][cp] / R
            growth[name][f"theory_at_{cp}"] = theory[name](cp)
    return {"n": n, "R": R, "sigma": sigma, "checkpoints": checkpoints, "illustrative": illustrative, "growth": growth}


def histogram(x, k=None):
    x = np.asarray(x, float)
    n = len(x)
    if k is None:
        k = int(min(20, max(5, math.ceil(math.sqrt(n)))))
    counts, edges = np.histogram(x, bins=k)
    return {"k": k, "edges": [float(e) for e in edges], "counts": [int(c) for c in counts]}


def run_rules(values, center, sigma):
    """Western Electric and Nelson rules. sigma may be a scalar or a list of
    per-point sigmas (attribute charts with variable n). Returns a dict rule ->
    list of 1-based indices of the point that completes the pattern."""
    v = np.asarray(values, float)
    n = len(v)
    sig = np.asarray(sigma, float) if np.ndim(sigma) else np.full(n, float(sigma))
    z = (v - center) / sig
    side = np.sign(z)
    viol = {"we1": [], "we2": [], "we3": [], "we4": [], "n2": [], "n3": [], "n4": [], "n7": [], "n8": []}
    for i in range(n):
        if abs(z[i]) > 3:
            viol["we1"].append(i + 1)
        if i >= 2:
            w = z[i - 2:i + 1]
            for s in (1, -1):
                if np.sum(s * w > 2) >= 2 and (s * w[-1] > 2):
                    viol["we2"].append(i + 1); break
        if i >= 4:
            w = z[i - 4:i + 1]
            for s in (1, -1):
                if np.sum(s * w > 1) >= 4 and (s * w[-1] > 1):
                    viol["we3"].append(i + 1); break
        if i >= 7:
            w = side[i - 7:i + 1]
            if np.all(w > 0) or np.all(w < 0):
                viol["we4"].append(i + 1)
        if i >= 8:
            w = side[i - 8:i + 1]
            if np.all(w > 0) or np.all(w < 0):
                viol["n2"].append(i + 1)
        if i >= 5:
            w = v[i - 5:i + 1]
            d = np.diff(w)
            if np.all(d > 0) or np.all(d < 0):
                viol["n3"].append(i + 1)
        if i >= 13:
            d = np.diff(v[i - 13:i + 1])
            if np.all(d != 0) and np.all(d[1:] * d[:-1] < 0):
                viol["n4"].append(i + 1)
        if i >= 14:
            w = z[i - 14:i + 1]
            if np.all(np.abs(w) < 1):
                viol["n7"].append(i + 1)
        if i >= 7:
            w = z[i - 7:i + 1]
            if np.all(np.abs(w) > 1) and np.any(w > 0) and np.any(w < 0):
                viol["n8"].append(i + 1)
    return viol


def normal_ppm(mean, sigma, usl, lsl):
    pu = float(stats.norm.sf((usl - mean) / sigma)) if usl is not None else 0.0
    pl = float(stats.norm.cdf((lsl - mean) / sigma)) if lsl is not None else 0.0
    return {"ppm_upper": pu * 1e6, "ppm_lower": pl * 1e6, "ppm_total": (pu + pl) * 1e6}


def indices(mean, sigma, usl, lsl, target=None, natural_lower=None, natural_upper=None):
    """Capability indices for one sigma estimate. Returns keys without prefix;
    the caller names them Pp/Ppk (overall) or Cw/Cwk (within)."""
    out = {}
    cu = (usl - mean) / (3 * sigma) if usl is not None else None
    cl = (mean - lsl) / (3 * sigma) if lsl is not None else None
    out["u"] = cu
    out["l"] = cl
    both = [c for c in (cu, cl) if c is not None]
    out["k_index"] = min(both) if both else None
    if usl is not None and lsl is not None:
        out["p"] = (usl - lsl) / (6 * sigma)
        m = (usl + lsl) / 2.0
        out["k"] = abs(m - mean) / ((usl - lsl) / 2.0)
        if target is not None:
            out["pm"] = (usl - lsl) / (6 * math.sqrt(sigma ** 2 + (mean - target) ** 2))
    else:
        out["p"] = None
        lo = lsl if lsl is not None else natural_lower
        hi = usl if usl is not None else natural_upper
        if lo is not None and hi is not None:
            out["p_natural"] = (hi - lo) / (6 * sigma)  # AIAG & VDA 2026 p. 48, "Cp for information"
    out.update(normal_ppm(mean, sigma, usl, lsl))
    return out


def within_sigma(x, groups, method):
    """Within-subgroup sigma. method: 'mr' (individuals), 'r' (Rbar/d2), 's' (Sbar/c4)."""
    x = np.asarray(x, float)
    if method == "mr":
        mr = np.abs(np.diff(x))
        return {"method": "MRbar/d2", "n_sub": 2, "mrbar": float(mr.mean()), "d2": D2_MR,
                "sigma": float(mr.mean() / D2_MR)}
    gdf = pd.DataFrame({"g": groups, "x": x})
    sizes = gdf.groupby("g", sort=False)["x"].count().values
    assert np.all(sizes == sizes[0]), "unequal subgroup sizes are not supported"
    n = int(sizes[0])
    c = CONST[str(n)]
    if method == "r":
        rbar = float(gdf.groupby("g", sort=False)["x"].agg(lambda s: s.max() - s.min()).mean())
        return {"method": "Rbar/d2", "n_sub": n, "rbar": rbar, "d2": c["d2"], "sigma": rbar / c["d2"]}
    sbar = float(gdf.groupby("g", sort=False)["x"].std(ddof=1).mean())
    return {"method": "Sbar/c4", "n_sub": n, "sbar": sbar, "c4": c["c4"], "sigma": sbar / c["c4"]}


# --------------------------------------------------------------------------
# Control charts
# --------------------------------------------------------------------------
def imr_chart(x):
    x = np.asarray(x, float)
    mr = np.abs(np.diff(x))
    xbar, mrbar = float(x.mean()), float(mr.mean())
    sig = mrbar / D2_MR
    out = {"n": len(x), "xbar": xbar, "mrbar": mrbar, "d2": D2_MR, "sigma_within": sig,
           "ucl_x": xbar + 3 * sig, "lcl_x": xbar - 3 * sig,
           "ucl_mr": CONST["2"]["D4"] * mrbar, "lcl_mr": 0.0, "D4": CONST["2"]["D4"],
           "mr": [float(v) for v in mr]}
    out["rules_x"] = run_rules(x, xbar, sig)
    out["beyond_mr"] = [i + 1 for i, v in enumerate(mr) if v > out["ucl_mr"]]
    out["stable"] = (len(out["rules_x"]["we1"]) == 0 and len(out["beyond_mr"]) == 0)
    out["stable_we"] = out["stable"] and all(len(out["rules_x"][k]) == 0 for k in ("we2", "we3", "we4"))
    return out


def _subgroups(x, groups):
    gdf = pd.DataFrame({"g": groups, "x": np.asarray(x, float)})
    order = list(dict.fromkeys(groups))
    means = [float(gdf.x[gdf.g == g].mean()) for g in order]
    ranges = [float(gdf.x[gdf.g == g].max() - gdf.x[gdf.g == g].min()) for g in order]
    sds = [float(gdf.x[gdf.g == g].std(ddof=1)) for g in order]
    n = int((gdf.g == order[0]).sum())
    return order, means, ranges, sds, n


def xbar_r_chart(x, groups):
    order, means, ranges, sds, n = _subgroups(x, groups)
    c = CONST[str(n)]
    xbb, rbar = float(np.mean(means)), float(np.mean(ranges))
    out = {"k": len(order), "n": n, "xbarbar": xbb, "rbar": rbar, "A2": c["A2"], "D3": c["D3"], "D4": c["D4"],
           "d2": c["d2"], "ucl_x": xbb + c["A2"] * rbar, "lcl_x": xbb - c["A2"] * rbar,
           "ucl_r": c["D4"] * rbar, "lcl_r": c["D3"] * rbar, "sigma_within": rbar / c["d2"],
           "means": means, "ranges": ranges}
    sig_xbar = c["A2"] * rbar / 3.0
    out["rules_x"] = run_rules(means, xbb, sig_xbar)
    out["beyond_r"] = [i + 1 for i, v in enumerate(ranges) if v > out["ucl_r"] or v < out["lcl_r"]]
    out["stable"] = len(out["rules_x"]["we1"]) == 0 and len(out["beyond_r"]) == 0
    out["stable_we"] = out["stable"] and all(len(out["rules_x"][k]) == 0 for k in ("we2", "we3", "we4"))
    return out


def xbar_s_chart(x, groups):
    order, means, ranges, sds, n = _subgroups(x, groups)
    c = CONST[str(n)]
    xbb, sbar = float(np.mean(means)), float(np.mean(sds))
    out = {"k": len(order), "n": n, "xbarbar": xbb, "sbar": sbar, "A3": c["A3"], "B3": c["B3"], "B4": c["B4"],
           "c4": c["c4"], "ucl_x": xbb + c["A3"] * sbar, "lcl_x": xbb - c["A3"] * sbar,
           "ucl_s": c["B4"] * sbar, "lcl_s": c["B3"] * sbar, "sigma_within": sbar / c["c4"],
           "means": means, "sds": sds}
    sig_xbar = c["A3"] * sbar / 3.0
    out["rules_x"] = run_rules(means, xbb, sig_xbar)
    out["beyond_s"] = [i + 1 for i, v in enumerate(sds) if v > out["ucl_s"] or v < out["lcl_s"]]
    out["stable"] = len(out["rules_x"]["we1"]) == 0 and len(out["beyond_s"]) == 0
    out["stable_we"] = out["stable"] and all(len(out["rules_x"][k]) == 0 for k in ("we2", "we3", "we4"))
    return out


def p_chart(n, d):
    n = np.asarray(n, float); d = np.asarray(d, float)
    pbar = float(d.sum() / n.sum())
    p = d / n
    sig = np.sqrt(pbar * (1 - pbar) / n)
    ucl = pbar + 3 * sig
    lcl = np.maximum(0.0, pbar - 3 * sig)
    out = {"k": len(n), "pbar": pbar, "p": [float(v) for v in p], "ucl": [float(v) for v in ucl],
           "lcl": [float(v) for v in lcl], "n_mean": float(n.mean())}
    out["rules"] = run_rules(p, pbar, sig)
    out["beyond"] = [i + 1 for i in range(len(n)) if p[i] > ucl[i] or p[i] < lcl[i]]
    return out


def np_chart(n, d):
    d = np.asarray(d, float)
    npbar = float(d.mean())
    pbar = npbar / n
    sig = math.sqrt(n * pbar * (1 - pbar))
    out = {"k": len(d), "n": n, "npbar": npbar, "pbar": pbar, "ucl": npbar + 3 * sig, "lcl": max(0.0, npbar - 3 * sig)}
    out["rules"] = run_rules(d, npbar, sig)
    out["beyond"] = [i + 1 for i, v in enumerate(d) if v > out["ucl"] or v < out["lcl"]]
    return out


def c_chart(c):
    c = np.asarray(c, float)
    cbar = float(c.mean())
    sig = math.sqrt(cbar)
    out = {"k": len(c), "cbar": cbar, "ucl": cbar + 3 * sig, "lcl": max(0.0, cbar - 3 * sig)}
    out["rules"] = run_rules(c, cbar, sig)
    out["beyond"] = [i + 1 for i, v in enumerate(c) if v > out["ucl"] or v < out["lcl"]]
    return out


def u_chart(n, c):
    n = np.asarray(n, float); c = np.asarray(c, float)
    ubar = float(c.sum() / n.sum())
    u = c / n
    sig = np.sqrt(ubar / n)
    ucl = ubar + 3 * sig
    lcl = np.maximum(0.0, ubar - 3 * sig)
    out = {"k": len(n), "ubar": ubar, "u": [float(v) for v in u], "ucl": [float(v) for v in ucl],
           "lcl": [float(v) for v in lcl]}
    out["rules"] = run_rules(u, ubar, sig)
    out["beyond"] = [i + 1 for i in range(len(n)) if u[i] > ucl[i] or u[i] < lcl[i]]
    return out


def ewma_chart(x, params):
    x = np.asarray(x, float)
    lam = params["lambda"]; L = params.get("L", 3.0)
    base = params.get("baseline", len(x))
    if "sigma" in params:
        sigma = params["sigma"]
    else:
        mr = np.abs(np.diff(x[:base]))
        sigma = float(mr.mean() / D2_MR)
    target = params["target"] if "target" in params else float(x[:base].mean())
    z = []
    prev = target
    for v in x:
        prev = lam * v + (1 - lam) * prev
        z.append(float(prev))
    n = len(x)
    if params.get("limits", "exact") == "asymptotic":
        half = [L * sigma * math.sqrt(lam / (2 - lam))] * n
    else:
        half = [L * sigma * math.sqrt(lam / (2 - lam) * (1 - (1 - lam) ** (2 * (i + 1)))) for i in range(n)]
    ucl = [target + h for h in half]; lcl = [target - h for h in half]
    out = {"n": n, "lambda": lam, "L": L, "target": target, "sigma": sigma, "ewma": z,
           "ucl": ucl, "lcl": lcl, "ucl_asymptotic": target + L * sigma * math.sqrt(lam / (2 - lam)),
           "lcl_asymptotic": target - L * sigma * math.sqrt(lam / (2 - lam)),
           "signals": [i + 1 for i in range(n) if z[i] > ucl[i] or z[i] < lcl[i]]}
    out["ucl"], out["lcl"] = (out["ucl_asymptotic"], out["lcl_asymptotic"]) if params.get("limits") == "asymptotic" else (ucl, lcl)
    return out


def cusum_chart(x, params):
    x = np.asarray(x, float)
    k, h = params["k"], params["h"]
    base = params.get("baseline", len(x))
    mr = np.abs(np.diff(x[:base]))
    sigma = params.get("sigma", float(mr.mean() / D2_MR))
    target = params.get("target", float(x[:base].mean()))
    cp, cm = [], []
    up = lo = 0.0
    for v in x:
        zi = (v - target) / sigma
        up = max(0.0, up + zi - k)
        lo = max(0.0, lo - zi - k)
        cp.append(up); cm.append(lo)
    out = {"n": len(x), "k": k, "h": h, "target": target, "sigma": sigma, "c_plus": cp, "c_minus": cm,
           "signals_plus": [i + 1 for i, v in enumerate(cp) if v > h],
           "signals_minus": [i + 1 for i, v in enumerate(cm) if v > h]}
    return out


# --------------------------------------------------------------------------
# Capability (with its stability chart and normality check)
# --------------------------------------------------------------------------
def capability(x, params, groups=None):
    x = np.asarray(x, float)
    usl, lsl, target = params.get("usl"), params.get("lsl"), params.get("target")
    nl, nu = params.get("natural_lower"), params.get("natural_upper")
    nsub = params.get("subgroup_size", 1)
    chart = params.get("chart", "imr" if nsub == 1 else "xbar_r")
    d = descriptive(x)
    out = {"descriptive": d, "histogram": histogram(x)}
    if chart == "imr":
        out["chart"] = imr_chart(x); ws = within_sigma(x, None, "mr")
    elif chart == "xbar_s":
        out["chart"] = xbar_s_chart(x, groups); ws = within_sigma(x, groups, "s")
    else:
        out["chart"] = xbar_r_chart(x, groups); ws = within_sigma(x, groups, "r")
    out["chart_type"] = chart
    mean, s = d["mean"], d["s"]
    n = d["n"]
    ov = indices(mean, s, usl, lsl, target, nl, nu)
    overall = {"mean": mean, "s": s, "sigma_estimate": "overall sample standard deviation s (n-1)",
               "Pp": ov["p"], "Ppu": ov["u"], "Ppl": ov["l"], "Ppk": ov["k_index"], "k": ov.get("k"),
               "Cpm": ov.get("pm"), "Pp_natural": ov.get("p_natural"),
               "ppm_upper": ov["ppm_upper"], "ppm_lower": ov["ppm_lower"], "ppm_total": ov["ppm_total"]}
    wv = indices(mean, ws["sigma"], usl, lsl, target, nl, nu)
    within = dict(ws)
    within.update({"sigma_estimate": ws["method"], "Cw": wv["p"], "Cwu": wv["u"], "Cwl": wv["l"], "Cwk": wv["k_index"],
                   "Cw_natural": wv.get("p_natural"), "ppm_upper": wv["ppm_upper"], "ppm_lower": wv["ppm_lower"],
                   "ppm_total": wv["ppm_total"]})
    # confidence intervals on the overall indices (NIST 6.1.6; chi-square for Pp)
    z = stats.norm.ppf(0.975)
    if overall["Ppk"] is not None:
        se = math.sqrt(1.0 / (9 * n) + overall["Ppk"] ** 2 / (2 * (n - 1)))
        overall["Ppk_ci95"] = [overall["Ppk"] - z * se, overall["Ppk"] + z * se]
    if overall["Pp"] is not None:
        overall["Pp_ci95"] = [overall["Pp"] * math.sqrt(stats.chi2.ppf(0.025, n - 1) / (n - 1)),
                              overall["Pp"] * math.sqrt(stats.chi2.ppf(0.975, n - 1) / (n - 1))]
    obs_out = int(np.sum((x > usl) if usl is not None else 0) + np.sum((x < lsl) if lsl is not None else 0))
    out["observed"] = {"n_out": obs_out, "ppm_observed": obs_out * 1e6 / n}
    out["overall"] = overall
    out["within"] = within
    out["legacy"] = {"Cp": within["Cw"], "Cpk": within["Cwk"], "Cpu": within["Cwu"], "Cpl": within["Cwl"],
                     "Pp": overall["Pp"], "Ppk": overall["Ppk"], "note": "2005 AIAG labels: Cp/Cpk from within sigma, Pp/Ppk from overall s"}
    out["stable"] = out["chart"]["stable"]
    out["stable_we"] = out["chart"]["stable_we"]
    out["normal_p"] = d.get("ad_p")
    out["aiag_vda_2026_label"] = "Cp/Cpk" if out["stable"] else "Pp/Ppk"
    if nl is not None and usl is not None and lsl is None:
        out["one_sided_note"] = "natural lower limit; Cpk may exceed Cp (AIAG & VDA 2026 p. 48)"
    return out


# --------------------------------------------------------------------------
# Gauge R&R (crossed, ANOVA method)
# --------------------------------------------------------------------------
def grr_from_ms(ms_full, df_full, ms_reduced, df_reduced, p_parts, o_ops, r_reps, tolerance, k_sv, alpha_remove):
    Fi = ms_full["interaction"] / ms_full["repeatability"]
    pi = float(stats.f.sf(Fi, df_full["interaction"], df_full["repeatability"]))
    use_reduced = pi > alpha_remove
    out = {"interaction_F": Fi, "interaction_p": pi, "interaction_removed": use_reduced, "alpha_remove": alpha_remove}
    if use_reduced:
        rep = ms_reduced["repeatability"]
        op = max(0.0, (ms_reduced["operator"] - rep) / (p_parts * r_reps))
        inter = 0.0
        part = max(0.0, (ms_reduced["part"] - rep) / (o_ops * r_reps))
        out["anova_used"] = "reduced (interaction pooled into repeatability)"
        out["F_operator"] = ms_reduced["operator"] / rep
        out["F_part"] = ms_reduced["part"] / rep
        out["p_operator"] = float(stats.f.sf(out["F_operator"], df_reduced["operator"], df_reduced["repeatability"]))
        out["p_part"] = float(stats.f.sf(out["F_part"], df_reduced["part"], df_reduced["repeatability"]))
    else:
        rep = ms_full["repeatability"]
        inter = max(0.0, (ms_full["interaction"] - rep) / r_reps)
        op = max(0.0, (ms_full["operator"] - ms_full["interaction"]) / (p_parts * r_reps))
        part = max(0.0, (ms_full["part"] - ms_full["interaction"]) / (o_ops * r_reps))
        out["anova_used"] = "full (with part x operator interaction)"
        out["F_operator"] = ms_full["operator"] / ms_full["interaction"]
        out["F_part"] = ms_full["part"] / ms_full["interaction"]
        out["p_operator"] = float(stats.f.sf(out["F_operator"], df_full["operator"], df_full["interaction"]))
        out["p_part"] = float(stats.f.sf(out["F_part"], df_full["part"], df_full["interaction"]))
    reprod = op + inter
    grr = rep + reprod
    total = grr + part
    vc = {"repeatability": rep, "reproducibility": reprod, "operator": op, "interaction": inter,
          "grr": grr, "part": part, "total": total}
    out["varcomp"] = vc
    out["pct_contribution"] = {k: 100.0 * v / total for k, v in vc.items()}
    sd = {k: math.sqrt(v) for k, v in vc.items()}
    out["sd"] = sd
    out["study_var_k"] = k_sv
    out["study_var"] = {k: k_sv * v for k, v in sd.items()}
    out["pct_study_var"] = {k: 100.0 * v / sd["total"] for k, v in sd.items()}
    if tolerance:
        out["tolerance"] = tolerance
        out["pct_tolerance"] = {k: 100.0 * k_sv * v / tolerance for k, v in sd.items()}
    ndc = math.floor(1.41 * sd["part"] / sd["grr"]) if sd["grr"] > 0 else None
    out["ndc"] = max(1, ndc) if ndc is not None else None
    out["ndc_exact"] = 1.41 * sd["part"] / sd["grr"] if sd["grr"] > 0 else None
    return out


def grr(cols, params):
    df = pd.DataFrame({"part": [str(int(v)) if isinstance(v, float) else str(v) for v in cols["part"]],
                       "operator": [str(v) for v in cols["operator"]], "y": cols["y"]})
    p_parts = df.part.nunique(); o_ops = df.operator.nunique()
    r_reps = len(df) // (p_parts * o_ops)
    full = smf.ols("y ~ C(part) * C(operator)", data=df).fit()
    a = anova_lm(full, typ=2)
    red = smf.ols("y ~ C(part) + C(operator)", data=df).fit()
    ar = anova_lm(red, typ=2)
    ms_full = {"part": float(a.loc["C(part)", "sum_sq"] / a.loc["C(part)", "df"]),
               "operator": float(a.loc["C(operator)", "sum_sq"] / a.loc["C(operator)", "df"]),
               "interaction": float(a.loc["C(part):C(operator)", "sum_sq"] / a.loc["C(part):C(operator)", "df"]),
               "repeatability": float(a.loc["Residual", "sum_sq"] / a.loc["Residual", "df"])}
    df_full = {"part": int(a.loc["C(part)", "df"]), "operator": int(a.loc["C(operator)", "df"]),
               "interaction": int(a.loc["C(part):C(operator)", "df"]), "repeatability": int(a.loc["Residual", "df"])}
    ss_full = {"part": float(a.loc["C(part)", "sum_sq"]), "operator": float(a.loc["C(operator)", "sum_sq"]),
               "interaction": float(a.loc["C(part):C(operator)", "sum_sq"]), "repeatability": float(a.loc["Residual", "sum_sq"]),
               "total": float(a["sum_sq"].sum())}
    ms_red = {"part": ms_full["part"], "operator": ms_full["operator"],
              "repeatability": float(ar.loc["Residual", "sum_sq"] / ar.loc["Residual", "df"])}
    df_red = {"part": df_full["part"], "operator": df_full["operator"], "repeatability": int(ar.loc["Residual", "df"])}
    out = {"parts": p_parts, "operators": o_ops, "replicates": r_reps, "N": len(df),
           "ss_full": ss_full, "ms_full": ms_full, "df_full": df_full, "ms_reduced": ms_red, "df_reduced": df_red,
           "grand_mean": float(df.y.mean())}
    out.update(grr_from_ms(ms_full, df_full, ms_red, df_red, p_parts, o_ops, r_reps, params.get("tolerance"),
                           params.get("study_var_k", 6.0), params.get("alpha_remove", 0.05)))
    out["operator_means"] = {k: float(v) for k, v in df.groupby("operator").y.mean().items()}
    out["part_means"] = {k: float(v) for k, v in df.groupby("part").y.mean().items()}
    return out


# --------------------------------------------------------------------------
# Designed experiments: 2^k with replicates
# --------------------------------------------------------------------------
def factorial(cols, params):
    k = params["k"]; names = params["factors"]
    df = pd.DataFrame({nm: cols[nm] for nm in names}); df["y"] = cols["y"]
    formula = "y ~ " + "*".join(names)
    fit = smf.ols(formula, data=df).fit()
    N = len(df)
    terms = [t for t in fit.params.index if t != "Intercept"]
    eff = {t.replace(":", ""): 2.0 * float(fit.params[t]) for t in terms}
    coef = {t.replace(":", ""): float(fit.params[t]) for t in terms}
    out = {"k": k, "N": N, "replicates": params["replicates"], "grand_mean": float(df.y.mean()),
           "effects": eff, "coefficients": coef, "intercept": float(fit.params["Intercept"])}
    if N > 2 ** k:
        a = anova_lm(fit, typ=1)
        an = {}
        for t in terms:
            an[t.replace(":", "")] = {"ss": float(a.loc[t, "sum_sq"]), "df": int(a.loc[t, "df"]),
                                      "ms": float(a.loc[t, "sum_sq"] / a.loc[t, "df"]),
                                      "F": float(a.loc[t, "F"]), "p": float(a.loc[t, "PR(>F)"])}
        an["residual"] = {"ss": float(a.loc["Residual", "sum_sq"]), "df": int(a.loc["Residual", "df"]),
                          "ms": float(a.loc["Residual", "sum_sq"] / a.loc["Residual", "df"])}
        an["total"] = {"ss": float(a["sum_sq"].sum()), "df": int(a["df"].sum())}
        out["anova"] = an
        out["residual_sd"] = math.sqrt(an["residual"]["ms"])
        out["se_effect"] = 2.0 * math.sqrt(an["residual"]["ms"] / N)
        out["r2"] = float(fit.rsquared)
        out["r2_adj"] = float(fit.rsquared_adj)
    if N == 2 ** k:
        # Lenth's method for unreplicated designs (Lenth 1989, Technometrics 31(4):469-473)
        labels = list(eff.keys())
        abs_e = sorted(abs(v) for v in eff.values())
        s0 = 1.5 * float(np.median(abs_e))
        trimmed = [v for v in abs_e if v < 2.5 * s0]
        pse = 1.5 * float(np.median(trimmed))
        m = len(labels); d = m / 3.0
        gamma = (1 + 0.95 ** (1.0 / m)) / 2.0
        me = float(stats.t.ppf(0.975, d)) * pse
        sme = float(stats.t.ppf(gamma, d)) * pse
        out["lenth"] = {"s0": s0, "pse": pse, "df": d, "t_me": float(stats.t.ppf(0.975, d)), "me": me,
                        "t_sme": float(stats.t.ppf(gamma, d)), "sme": sme,
                        "active": [lb for lb in labels if abs(eff[lb]) > me],
                        "n_trimmed": len(abs_e) - len(trimmed)}
    # cell means in standard order for the page tables
    out["cell_means"] = {}
    for _, g in df.groupby(names, sort=True):
        key = "".join(nm.lower() for nm in names if g[nm].iloc[0] > 0) or "(1)"
        out["cell_means"][key] = float(g.y.mean())
    return out


# --------------------------------------------------------------------------
# Hypothesis tests and regression
# --------------------------------------------------------------------------
def ttest2(cols, params):
    df = pd.DataFrame({"g": cols["group"], "x": cols["x"]})
    groups = list(dict.fromkeys(df.g))
    a = df.x[df.g == groups[0]].values; b = df.x[df.g == groups[1]].values
    alpha = params.get("alpha", 0.05)
    out = {"groups": groups, "n": [len(a), len(b)], "means": [float(a.mean()), float(b.mean())],
           "sds": [float(a.std(ddof=1)), float(b.std(ddof=1))], "diff": float(a.mean() - b.mean())}
    tp = stats.ttest_ind(a, b, equal_var=True)
    tw = stats.ttest_ind(a, b, equal_var=False)
    sp = math.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    se_p = sp * math.sqrt(1 / len(a) + 1 / len(b))
    dfp = len(a) + len(b) - 2
    tc = stats.t.ppf(1 - alpha / 2, dfp)
    out["pooled"] = {"sp": sp, "se": se_p, "t": float(tp.statistic), "df": dfp, "p": float(tp.pvalue),
                     "ci": [out["diff"] - tc * se_p, out["diff"] + tc * se_p]}
    se_w = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    dfw = float(tw.df)
    tcw = stats.t.ppf(1 - alpha / 2, dfw)
    out["welch"] = {"se": se_w, "t": float(tw.statistic), "df": dfw, "p": float(tw.pvalue),
                    "ci": [out["diff"] - tcw * se_w, out["diff"] + tcw * se_w]}
    out["cohen_d"] = out["diff"] / sp
    Fv = a.var(ddof=1) / b.var(ddof=1)
    pF = 2 * min(stats.f.cdf(Fv, len(a) - 1, len(b) - 1), stats.f.sf(Fv, len(a) - 1, len(b) - 1))
    lev = stats.levene(a, b, center="median")
    out["variance_tests"] = {"F": Fv, "F_p": float(pF), "levene_W": float(lev.statistic), "levene_p": float(lev.pvalue)}
    out["alpha"] = alpha
    return out


def anova1(cols, params):
    df = pd.DataFrame({"g": cols["group"], "x": cols["x"]})
    groups = list(dict.fromkeys(df.g))
    samples = [df.x[df.g == g].values for g in groups]
    f = stats.f_oneway(*samples)
    N = len(df); k = len(groups)
    gm = df.x.mean()
    ssb = sum(len(s) * (s.mean() - gm) ** 2 for s in samples)
    ssw = sum(((s - s.mean()) ** 2).sum() for s in samples)
    out = {"groups": groups, "n": [len(s) for s in samples], "means": [float(s.mean()) for s in samples],
           "sds": [float(s.std(ddof=1)) for s in samples], "grand_mean": float(gm),
           "ss_between": float(ssb), "ss_within": float(ssw), "ss_total": float(ssb + ssw),
           "df_between": k - 1, "df_within": N - k, "ms_between": float(ssb / (k - 1)), "ms_within": float(ssw / (N - k)),
           "F": float(f.statistic), "p": float(f.pvalue), "eta2": float(ssb / (ssb + ssw)),
           "pooled_sd": math.sqrt(ssw / (N - k))}
    lev = stats.levene(*samples, center="median")
    out["levene_W"], out["levene_p"] = float(lev.statistic), float(lev.pvalue)
    return out


def one_sample(x, mu0, alpha):
    x = np.asarray(x, float)
    n = len(x)
    t = stats.ttest_1samp(x, mu0)
    se = x.std(ddof=1) / math.sqrt(n)
    tc = stats.t.ppf(1 - alpha / 2, n - 1)
    return {"n": n, "mean": float(x.mean()), "s": float(x.std(ddof=1)), "se": float(se), "mu0": mu0,
            "t": float(t.statistic), "df": n - 1, "p": float(t.pvalue),
            "ci": [float(x.mean() - tc * se), float(x.mean() + tc * se)], "cohen_d": float((x.mean() - mu0) / x.std(ddof=1))}


def paired(cols, params):
    b = np.asarray(cols["before"], float); a = np.asarray(cols["after"], float)
    d = a - b
    out = one_sample(d, 0.0, params.get("alpha", 0.05))
    out["mean_before"], out["mean_after"] = float(b.mean()), float(a.mean())
    out["differences"] = [float(v) for v in d]
    return out


def regression(cols, params):
    x = np.asarray(cols["x"], float); y = np.asarray(cols["y"], float)
    alpha = params.get("alpha", 0.05)
    df = pd.DataFrame({"x": x, "y": y})
    fit = smf.ols("y ~ x", data=df).fit()
    n = len(x)
    ci = fit.conf_int(alpha)
    out = {"n": n, "slope": float(fit.params["x"]), "intercept": float(fit.params["Intercept"]),
           "se_slope": float(fit.bse["x"]), "se_intercept": float(fit.bse["Intercept"]),
           "t_slope": float(fit.tvalues["x"]), "p_slope": float(fit.pvalues["x"]),
           "slope_ci": [float(ci.loc["x", 0]), float(ci.loc["x", 1])],
           "r": float(np.corrcoef(x, y)[0, 1]), "r2": float(fit.rsquared), "r2_adj": float(fit.rsquared_adj),
           "s": float(math.sqrt(fit.mse_resid)), "F": float(fit.fvalue), "p_F": float(fit.f_pvalue),
           "ss_regression": float(fit.ess), "ss_residual": float(fit.ssr), "ss_total": float(fit.ess + fit.ssr),
           "fitted": [float(v) for v in fit.fittedvalues], "residuals": [float(v) for v in fit.resid],
           "mean_x": float(x.mean()), "mean_y": float(y.mean())}
    return out


def samplesize(params):
    alpha, beta = params["alpha"], params["beta"]
    ratio = (params["sigma"] / params["delta"]) ** 2
    sides = params.get("sides", 2)
    two = params.get("design", "one-sample") == "two-sample"
    mult = 2.0 if two else 1.0
    za = stats.norm.ppf(1 - alpha / sides); zb = stats.norm.ppf(1 - beta)
    n_z_exact = mult * (za + zb) ** 2 * ratio
    n = math.ceil(n_z_exact)
    # NIST 7.2.2.2 iteration: replace z by t with the current n's degrees of freedom
    seen = set()
    n_t = n
    for _ in range(50):
        dfree = 2 * n_t - 2 if two else n_t - 1
        ta = stats.t.ppf(1 - alpha / sides, dfree); tb = stats.t.ppf(1 - beta, dfree)
        nn = math.ceil(mult * (ta + tb) ** 2 * ratio)
        if nn == n_t or nn in seen:
            n_t = max(nn, n_t); break
        seen.add(n_t); n_t = nn
    out = {"alpha": alpha, "beta": beta, "power": 1 - beta, "delta": params["delta"], "sigma": params["sigma"],
           "sides": sides, "design": params.get("design", "one-sample"), "z_alpha": float(za), "z_beta": float(zb),
           "n_z_exact": float(n_z_exact), "n_z": n, "n_t": int(n_t)}
    # information only: exact power at n_t from the noncentral t (scipy); not recomputed by the closed-form route
    dfree = 2 * n_t - 2 if two else n_t - 1
    ncp = params["delta"] / params["sigma"] * math.sqrt(n_t / mult)
    tcrit = stats.t.ppf(1 - alpha / sides, dfree)
    out["info_power_nct"] = float(stats.nct.sf(tcrit, dfree, ncp))
    return out


def dpmo_block(defects, units, opportunities):
    """Defect count to DPU, DPO, DPMO, Poisson first-time yield, and the two
    Z conventions: the plain normal tail Z (no shift) and the Motorola sigma
    level, which adds 1.5 to it."""
    dpmo = defects / (units * opportunities) * 1e6
    dpu = defects / units
    z_lt = stats.norm.ppf(1 - dpmo / 1e6)
    return {"defects": defects, "units": units, "opportunities": opportunities,
            "dpmo": dpmo, "dpu": dpu, "dpo": defects / (units * opportunities),
            "yield_fty": math.exp(-dpu), "yield_from_dpmo": 1 - dpmo / 1e6,
            "sigma_long_term": float(z_lt), "sigma_level_shifted": float(z_lt + 1.5)}


def sigma_table(params):
    """Sigma level to PPM under both conventions, per level k:
    centred two-sided PPM = 2 * P(Z > k) * 1e6; with the 1.5 sigma shift the
    one-sided PPM = P(Z > k - shift) * 1e6 (the convention behind "3.4 PPM at
    six sigma"); two-sided shifted adds the far tail P(Z > k + shift)."""
    shift = params.get("shift", 1.5)
    levels = [float(k) for k in params["levels"]]
    out = {"shift": shift, "levels": levels, "ppm_centered_two_sided": [], "ppm_shifted_one_sided": [],
           "ppm_shifted_two_sided": [], "yield_shifted_one_sided": []}
    for k in levels:
        near = float(stats.norm.sf(k - shift))
        far = float(stats.norm.sf(k + shift))
        out["ppm_centered_two_sided"].append(2e6 * float(stats.norm.sf(k)))
        out["ppm_shifted_one_sided"].append(1e6 * near)
        out["ppm_shifted_two_sided"].append(1e6 * (near + far))
        out["yield_shifted_one_sided"].append(1 - near)
    if "ppm_targets" in params:
        out["ppm_targets"] = [float(p) for p in params["ppm_targets"]]
        out["z_of_targets"] = [float(stats.norm.isf(p / 1e6)) for p in params["ppm_targets"]]
        out["sigma_level_of_targets"] = [z + shift for z in out["z_of_targets"]]
    return out


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# Module 8: capability of non-normal data and attribute capability
#   capability_nonnormal  x with usl/lsl (natural_lower/upper optional):
#     normal.*     the naive normal-based Pp/Ppk and PPM (what software prints
#                  if nobody looks at the histogram)
#     lognormal.*  fitted lognormal (mean and n-1 sd of ln x), AD test on ln x,
#                  the 0.135 %, 50 % and 99.865 % quantiles, the ISO 22514-2 /
#                  AIAG & VDA 2026 pp. 46-47 general geometric indices (Pp.G,
#                  Ppk.G), the tail areas and the p. 49 z-score index (Ppk.Z)
#     boxcox.*     Box-Cox lambda by maximum likelihood (scipy), rounded to
#                  two decimals for use; normal indices on the transformed
#                  scale; quantiles transformed back; geometric indices
#     empirical.*  NIST 6.1.6 nonparametric percentiles (Weibull plotting
#                  position, as the descriptive quartiles) and Cnp/Cnpk
#     chart_raw, chart_log   I-MR charts of x and of ln x
#   attribute_capability  columns n, defectives: p chart, overall p, Wilson and
#     exact binomial 95 % intervals (NIST 7.2.4.1), DPMO, Z and sigma level.
# --------------------------------------------------------------------------
def _pct_weibull(x, p):
    return float(np.percentile(np.asarray(x, float), 100.0 * p, method="weibull"))


def _geometric(x0135, x50, x99865, usl, lsl):
    """General geometric (quantile) method, AIAG & VDA 2026 pp. 46-47 / ISO 22514-2."""
    out = {"x0135": x0135, "x50": x50, "x99865": x99865, "spread_9973": x99865 - x0135}
    out["Ppu_G"] = (usl - x50) / (x99865 - x50) if usl is not None else None
    out["Ppl_G"] = (x50 - lsl) / (x50 - x0135) if lsl is not None else None
    both = [v for v in (out["Ppu_G"], out["Ppl_G"]) if v is not None]
    out["Ppk_G"] = min(both) if both else None
    out["Pp_G"] = (usl - lsl) / (x99865 - x0135) if (usl is not None and lsl is not None) else None
    return out


def _zscore(pu, pl, usl, lsl):
    """z-score method, AIAG & VDA 2026 p. 49: tail areas of the fitted
    distribution converted to the Z of a normal with the same tail."""
    out = {"ppm_upper": pu * 1e6, "ppm_lower": pl * 1e6, "ppm_total": (pu + pl) * 1e6}
    out["zU"] = float(stats.norm.isf(pu)) if usl is not None else None
    out["zL"] = float(stats.norm.isf(pl)) if lsl is not None else None
    both = [v for v in (out["zU"], out["zL"]) if v is not None]
    out["Ppk_Z"] = min(both) / 3.0 if both else None
    return out


def capability_nonnormal(x, params):
    from scipy import optimize, special
    x = np.asarray(x, float)
    n = len(x)
    usl, lsl = params.get("usl"), params.get("lsl")
    nl = params.get("natural_lower")
    d = descriptive(x)
    out = {"descriptive": d, "histogram": histogram(x), "chart_raw": imr_chart(x)}
    # naive normal-based indices (the software default)
    nv = indices(d["mean"], d["s"], usl, lsl)
    out["normal"] = {"mean": d["mean"], "s": d["s"], "Pp": nv["p"], "Ppu": nv["u"], "Ppl": nv["l"], "Ppk": nv["k_index"],
                     "ppm_upper": nv["ppm_upper"], "ppm_lower": nv["ppm_lower"], "ppm_total": nv["ppm_total"],
                     "lower_3s": d["mean"] - 3 * d["s"], "upper_3s": d["mean"] + 3 * d["s"]}
    if nl is not None:
        out["normal"]["lower_3s_below_natural_limit"] = bool(d["mean"] - 3 * d["s"] < nl)
    # lognormal fit (requires x > 0)
    if np.all(x > 0):
        lx = np.log(x)
        ld = descriptive(lx)
        mu, sg = ld["mean"], ld["s"]
        ln_block = {"mu": mu, "sigma": sg, "ad_A2": ld.get("ad_A2"), "ad_p": ld.get("ad_p"), "skewness_log": ld["skewness"]}
        ln_block.update(_geometric(math.exp(mu - 3 * sg), math.exp(mu), math.exp(mu + 3 * sg), usl, lsl))
        pu = float(stats.norm.sf((math.log(usl) - mu) / sg)) if usl is not None else 0.0
        pl = float(stats.norm.cdf((math.log(lsl) - mu) / sg)) if (lsl is not None and lsl > 0) else 0.0
        ln_block.update(_zscore(pu, pl, usl, lsl if (lsl is not None and lsl > 0) else None))
        ln_block["mean_fitted"] = math.exp(mu + sg ** 2 / 2)
        out["lognormal"] = ln_block
        out["chart_log"] = imr_chart(lx)
        # Box-Cox: lambda by maximum likelihood, refined, then rounded to 2 dp for use
        lam0 = float(stats.boxcox_normmax(x, method="mle"))
        r = optimize.minimize_scalar(lambda l: -float(stats.boxcox_llf(l, x)), bounds=(lam0 - 0.25, lam0 + 0.25),
                                     method="bounded", options={"xatol": 1e-10})
        lam_mle = float(r.x)
        lam = round(lam_mle, 2)
        y = special.boxcox(x, lam) if lam != 0 else lx
        yd = descriptive(y)
        bc = {"lambda_mle": lam_mle, "lambda_used": lam, "llf_at_lambda": float(stats.boxcox_llf(lam, x)),
              "mean_y": yd["mean"], "s_y": yd["s"], "ad_A2": yd.get("ad_A2"), "ad_p": yd.get("ad_p"),
              "skewness_y": yd["skewness"]}
        yU = float(special.boxcox(usl, lam)) if usl is not None else None
        yL = None
        if lsl is not None and (lsl > 0 or lam > 0):
            yL = float(special.boxcox(lsl, lam)) if lam != 0 else math.log(lsl)
        bc["usl_transformed"], bc["lsl_transformed"] = yU, yL
        bv = indices(yd["mean"], yd["s"], yU, yL)
        bc.update({"Pp_y": bv["p"], "Ppu_y": bv["u"], "Ppl_y": bv["l"], "Ppk_y": bv["k_index"],
                   "ppm_upper": bv["ppm_upper"], "ppm_lower": bv["ppm_lower"], "ppm_total": bv["ppm_total"]})

        def back(v):
            if lam == 0:
                return math.exp(v)
            t = lam * v + 1.0
            return float(t ** (1.0 / lam)) if t > 0 else 0.0
        bc.update(_geometric(back(yd["mean"] - 3 * yd["s"]), back(yd["mean"]), back(yd["mean"] + 3 * yd["s"]), usl, lsl))
        out["boxcox"] = bc
    # nonparametric percentiles (NIST 6.1.6), Weibull plotting position
    emp = _geometric(_pct_weibull(x, 0.00135), _pct_weibull(x, 0.5), _pct_weibull(x, 0.99865), usl, lsl)
    emp["Cnp"], emp["Cnpk"] = emp["Pp_G"], emp["Ppk_G"]
    emp["note"] = "AIAG & VDA 2026 p. 47: empirical quantiles need about 2000 observations"
    out["empirical"] = emp
    obs_out = int(np.sum((x > usl) if usl is not None else 0) + np.sum((x < lsl) if lsl is not None else 0))
    out["observed"] = {"n_out": obs_out, "ppm_observed": obs_out * 1e6 / n}
    out["stable_raw"] = out["chart_raw"]["stable"]
    if "chart_log" in out:
        out["stable_log"] = out["chart_log"]["stable"]
    return out


def attribute_capability(n, d, params):
    n = [int(v) for v in n]; d = [int(v) for v in d]
    out = {"chart": p_chart(n, d)}
    N, D = sum(n), sum(d)
    pbar = D / N
    z = float(stats.norm.ppf(0.975))
    centre = (pbar + z * z / (2 * N)) / (1 + z * z / N)
    half = z * math.sqrt(pbar * (1 - pbar) / N + z * z / (4 * N * N)) / (1 + z * z / N)
    lo = float(stats.beta.ppf(0.025, D, N - D + 1)) if D > 0 else 0.0
    hi = float(stats.beta.ppf(0.975, D + 1, N - D)) if D < N else 1.0
    zl = float(stats.norm.isf(pbar))
    out.update({"k": len(n), "n_total": N, "d_total": D, "pbar": pbar, "pct": 100 * pbar, "dpmo": pbar * 1e6,
                "yield": 1 - pbar, "wilson_ci95": [centre - half, centre + half], "exact_ci95": [lo, hi],
                "dpmo_ci95": [1e6 * (centre - half), 1e6 * (centre + half)],
                "z_long_term": zl, "sigma_level_shifted": zl + 1.5,
                "stable": len(out["chart"]["beyond"]) == 0, "n_mean": N / len(n)})
    e = params.get("precision_e")
    if e:
        out["precision_e"] = e
        out["n_for_precision"] = int(math.ceil(z * z * pbar * (1 - pbar) / (e * e)))
    return out


# --------------------------------------------------------------------------
# Module 11: chi-square test of independence, Mann-Whitney U, power at a
# given sample size
#   chisq        columns: row (labels) + one count column per category;
#                params: columns (order), alpha, correction (Yates, default off)
#   mannwhitney  columns group, x (two groups); asymptotic normal p with tie
#                and continuity corrections (scipy method="asymptotic")
#   power        params alpha, sides, delta, sigma, n (per group), design;
#                z-approximation power in closed form, exact noncentral-t
#                power as information only (info_power_nct)
# --------------------------------------------------------------------------
def chisq(cols, params):
    labels = [str(v) for v in cols["row"]]
    names = params.get("columns") or [c for c in cols if c != "row"]
    obs = np.array([[cols[c][i] for c in names] for i in range(len(labels))], float)
    alpha = params.get("alpha", 0.05)
    chi2, p, dof, exp = stats.chi2_contingency(obs, correction=params.get("correction", False))
    n = float(obs.sum()); r, c = obs.shape
    contrib = (obs - exp) ** 2 / exp
    out = {"rows": labels, "columns": names, "observed": obs.tolist(), "expected": exp.tolist(),
           "row_totals": obs.sum(axis=1).tolist(), "col_totals": obs.sum(axis=0).tolist(), "n": int(n),
           "row_proportions": (obs / obs.sum(axis=1, keepdims=True)).tolist(),
           "col_overall_proportions": (obs.sum(axis=0) / n).tolist(),
           "contributions": contrib.tolist(), "chi2": float(chi2), "df": int(dof), "p": float(p),
           "chi2_crit": float(stats.chi2.ppf(1 - alpha, dof)), "alpha": alpha,
           "cramer_v": math.sqrt(float(chi2) / (n * (min(r, c) - 1))), "min_expected": float(exp.min()),
           "cells_expected_below_5": int((exp < 5).sum())}
    return out


def mannwhitney(cols, params):
    df = pd.DataFrame({"g": cols["group"], "x": cols["x"]})
    groups = list(dict.fromkeys(df.g))
    a = df.x[df.g == groups[0]].values.astype(float); b = df.x[df.g == groups[1]].values.astype(float)
    n1, n2 = len(a), len(b)
    res = stats.mannwhitneyu(a, b, alternative="two-sided", method="asymptotic", use_continuity=True)
    U1 = float(res.statistic); U2 = n1 * n2 - U1
    allv = np.concatenate([a, b])
    ranks = stats.rankdata(allv)
    _, t = np.unique(allv, return_counts=True)
    N = n1 + n2
    mu = n1 * n2 / 2.0
    sd = math.sqrt(n1 * n2 / 12.0 * ((N + 1) - float((t ** 3 - t).sum()) / (N * (N - 1))))
    z = (max(U1, U2) - mu - 0.5) / sd
    diffs = np.subtract.outer(a, b).ravel()
    tw = stats.ttest_ind(a, b, equal_var=False)
    out = {"groups": groups, "n": [n1, n2], "medians": [float(np.median(a)), float(np.median(b))],
           "means": [float(a.mean()), float(b.mean())], "rank_sums": [float(ranks[:n1].sum()), float(ranks[n1:].sum())],
           "U1": U1, "U2": U2, "U": min(U1, U2), "mean_U": mu, "sd_U": sd, "z": z, "p": float(res.pvalue),
           "ties": int((t > 1).sum()), "hodges_lehmann": float(np.median(diffs)),
           "prob_superiority": U1 / (n1 * n2), "welch_t": float(tw.statistic), "welch_p": float(tw.pvalue),
           "alpha": params.get("alpha", 0.05)}
    return out


def power(params):
    alpha, sides = params["alpha"], params.get("sides", 2)
    delta, sigma, n = params["delta"], params["sigma"], params["n"]
    two = params.get("design", "two-sample") == "two-sample"
    mult = 2.0 if two else 1.0
    za = float(stats.norm.ppf(1 - alpha / sides))

    def pw(nn):
        ncp = delta / sigma * math.sqrt(nn / mult)
        return float(stats.norm.sf(za - ncp) + (stats.norm.sf(za + ncp) if sides == 2 else 0.0))
    out = {"alpha": alpha, "sides": sides, "delta": delta, "sigma": sigma, "n": n, "design": params.get("design", "two-sample"),
           "z_alpha": za, "ncp": delta / sigma * math.sqrt(n / mult), "power_z": pw(n), "beta_z": 1 - pw(n),
           "effect_d": delta / sigma}
    if "curve_n" in params:
        out["curve_n"] = list(params["curve_n"]); out["curve_power"] = [pw(v) for v in params["curve_n"]]
    dfree = 2 * n - 2 if two else n - 1
    tcrit = stats.t.ppf(1 - alpha / sides, dfree)
    out["info_power_nct"] = float(stats.nct.sf(tcrit, dfree, out["ncp"]))
    return out


# --------------------------------------------------------------------------
# Module 16: average run length of a Shewhart chart with Western Electric
# runs rules, by the exact Markov-chain method of Champ and Woodall (1987),
# for a normal plotted statistic shifted by delta standard deviations.
#   arl   params rule_sets [["we1"], ["we1","we2"], ...], shifts [0, 0.5, ...]
# State = the zone categories of the last four observations (side and zone:
# within 1 sigma, 1 to 2, 2 to 3; "none" before the chart starts) plus a
# count of same-side observations before those four (capped at 3), which is
# what rule 4 (eight in a row) needs. Rules fire on the observation that
# completes the pattern, as in run_rules(); the first-alarm time, and hence
# the ARL, is the same as for the "any window" formulation.
# --------------------------------------------------------------------------
def arl_markov(rules, delta):
    from scipy.sparse import lil_matrix
    from scipy.sparse.linalg import spsolve
    cuts = [-3, -2, -1, 0, 1, 2, 3]
    cdf = [float(stats.norm.cdf(c - delta)) for c in cuts]
    # categories: (side, zone) with side -1/+1, zone 0 (0-1), 1 (1-2), 2 (2-3); None = no observation yet
    cats = [(-1, 2), (-1, 1), (-1, 0), (1, 0), (1, 1), (1, 2)]
    probs = [cdf[1] - cdf[0], cdf[2] - cdf[1], cdf[3] - cdf[2], cdf[4] - cdf[3], cdf[5] - cdf[4], cdf[6] - cdf[5]]
    p_beyond = cdf[0] + (1 - cdf[6])
    use2, use3, use4 = "we2" in rules, "we3" in rules, "we4" in rules

    def fires(stored, extra, new):
        s, z = new
        if use2 and z == 2:
            if sum(1 for c in stored[2:] if c is not None and c[0] == s and c[1] == 2) >= 1:
                return True
        if use3 and z >= 1:
            if sum(1 for c in stored if c is not None and c[0] == s and c[1] >= 1) >= 3:
                return True
        if use4:
            if all(c is not None and c[0] == s for c in stored) and extra >= 3:
                return True
        return False

    def step(stored, extra, new):
        s = new[0]
        c1 = stored[0]
        if c1 is not None and c1[0] == s and all(c is not None and c[0] == s for c in stored[1:]):
            extra2 = min(3, extra + 1)
        else:
            extra2 = 0
        return (stored[1:] + (new,), extra2)

    start = ((None, None, None, None), 0)
    index = {start: 0}; order = [start]; trans = []
    i = 0
    while i < len(order):
        st = order[i]
        row = []
        for cat, pr in zip(cats, probs):
            if fires(st[0], st[1], cat):
                continue
            nxt = step(st[0], st[1], cat)
            if nxt not in index:
                index[nxt] = len(order); order.append(nxt)
            row.append((index[nxt], pr))
        trans.append(row)
        i += 1
    n = len(order)
    M = lil_matrix((n, n))
    for i in range(n):
        M[i, i] = 1.0
        for j, pr in trans[i]:
            M[i, j] -= pr
    x = spsolve(M.tocsr(), np.ones(n))
    return float(x[0]), n, p_beyond


def arl_table(params):
    rule_sets = params["rule_sets"]; shifts = params["shifts"]
    out = {"shifts": list(shifts), "rule_sets": ["+".join(r) for r in rule_sets], "arl": {}, "states": {},
           "p_beyond_3sigma": [float(stats.norm.cdf(-3 - d) + stats.norm.sf(3 - d)) for d in shifts]}
    for rs in rule_sets:
        key = "+".join(rs)
        vals = []
        for d in shifts:
            a, n, _ = arl_markov(rs, d)
            vals.append(a)
        out["arl"][key] = vals
        out["states"][key] = n
    out["arl_rule1_closed_form"] = [1.0 / p for p in out["p_beyond_3sigma"]]
    return out


# --------------------------------------------------------------------------
# Module 17: Laney p' chart for over-dispersed proportions (Laney 2002;
# formulas as in Minitab's methods page and Arafah 2022) and the short-run
# deviation-from-nominal (DNOM) chart (ISO 7870-8; Wheeler, Short Run SPC).
#   p_prime  columns n, defectives: classic p chart plus z-scores, sigma_z
#            from the moving range of z, and limits pbar +/- 3 sigma_pi sigma_z
#   dnom     columns part, nominal, x: I-MR chart of (x - nominal) with a
#            per-part summary and the ratio of part standard deviations
# --------------------------------------------------------------------------
def p_prime_chart(n, d):
    base = p_chart(n, d)
    n = [int(v) for v in n]
    pbar, p = base["pbar"], base["p"]
    sig = [math.sqrt(pbar * (1 - pbar) / ni) for ni in n]
    z = [(p[i] - pbar) / sig[i] for i in range(len(n))]
    mr = [abs(z[i] - z[i - 1]) for i in range(1, len(z))]
    mrbar = float(np.mean(mr))
    sigma_z = mrbar / D2_MR
    ucl = [pbar + 3 * s * sigma_z for s in sig]
    lcl = [max(0.0, pbar - 3 * s * sigma_z) for s in sig]
    out = {"k": len(n), "pbar": pbar, "p": p, "z": z, "mrbar_z": mrbar, "sigma_z": sigma_z, "ucl": ucl, "lcl": lcl,
           "beyond": [i + 1 for i in range(len(n)) if p[i] > ucl[i] or p[i] < lcl[i]],
           "classic_ucl": base["ucl"], "classic_lcl": base["lcl"], "classic_beyond": base["beyond"],
           "n_mean": float(np.mean(n)), "n_total": int(sum(n)), "d_total": int(sum(d)),
           "sd_of_p": float(np.std(p, ddof=1)), "mean_sigma_p": float(np.mean(sig))}
    out["rules_z"] = run_rules(z, 0.0, sigma_z)
    return out


def dnom_chart(cols):
    parts = [str(v) for v in cols["part"]]
    nominal = [float(v) for v in cols["nominal"]]; x = [float(v) for v in cols["x"]]
    dev = [x[i] - nominal[i] for i in range(len(x))]
    out = {"deviations": dev, "chart": imr_chart(dev), "parts": {}}
    for pn in dict.fromkeys(parts):
        vals = [dev[i] for i in range(len(dev)) if parts[i] == pn]
        out["parts"][pn] = {"n": len(vals), "nominal": nominal[parts.index(pn)], "mean_dev": float(np.mean(vals)),
                            "sd_dev": float(np.std(vals, ddof=1)) if len(vals) > 1 else None}
    sds = [v["sd_dev"] for v in out["parts"].values() if v["sd_dev"]]
    out["sd_ratio_max_min"] = max(sds) / min(sds) if sds else None
    out["n_parts"] = len(out["parts"])
    return out


# --------------------------------------------------------------------------
# Module 19 (and Module 9): Pareto table from category counts
#   pareto  columns category, count: sorted counts, percentages, cumulative
# --------------------------------------------------------------------------
def pareto(cols):
    cats = [str(v) for v in cols["category"]]; counts = [int(v) for v in cols["count"]]
    order = sorted(range(len(cats)), key=lambda i: -counts[i])
    total = sum(counts)
    out = {"total": total, "categories": [cats[i] for i in order], "counts": [counts[i] for i in order]}
    out["pct"] = [100.0 * c / total for c in out["counts"]]
    cum = []; run = 0.0
    for v in out["pct"]:
        run += v; cum.append(run)
    out["cum_pct"] = cum
    out["top1_pct"] = out["pct"][0]
    out["top2_pct"] = cum[1] if len(cum) > 1 else cum[0]
    out["n_for_80pct"] = next(i + 1 for i, v in enumerate(cum) if v >= 80.0 - 1e-9)
    return out


# --------------------------------------------------------------------------
# Module 4: attribute agreement analysis (Cohen's and Fleiss' kappa)
#   attribute_agreement  columns part, appraiser, trial, rating (0/1);
#                        params standard = {part_id: true_rating}, optional
# --------------------------------------------------------------------------
def cohen_kappa_binary(a, b):
    """Cohen's kappa between two equal-length lists of 0/1 ratings."""
    a = np.asarray(a); b = np.asarray(b)
    po = float(np.mean(a == b))
    pa1 = float(np.mean(a == 1)); pb1 = float(np.mean(b == 1))
    pe = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    return {"kappa": (po - pe) / (1 - pe) if pe < 1 else float("nan"), "po": po, "pe": pe}


def fleiss_kappa_binary(matrix):
    """matrix: N subjects x n raters (numpy array of 0/1). Returns kappa and the intermediates."""
    N, n = matrix.shape
    n0 = (matrix == 0).sum(axis=1); n1 = (matrix == 1).sum(axis=1)
    Pi = (n0.astype(float) ** 2 + n1.astype(float) ** 2 - n) / (n * (n - 1))
    Pbar = float(Pi.mean())
    p0 = float(n0.sum()) / (N * n); p1 = float(n1.sum()) / (N * n)
    Pe = p0 ** 2 + p1 ** 2
    return {"kappa": (Pbar - Pe) / (1 - Pe), "p_bar": Pbar, "pe_bar": Pe, "p0": p0, "p1": p1}


def attribute_agreement(cols, params):
    df = pd.DataFrame({"part": [str(int(v)) if isinstance(v, float) else str(v) for v in cols["part"]],
                       "appraiser": [str(v) for v in cols["appraiser"]],
                       "trial": [int(v) for v in cols["trial"]], "rating": [int(v) for v in cols["rating"]]})
    parts = sorted(df.part.unique().tolist(), key=lambda p: int(p))
    appraisers = sorted(df.appraiser.unique().tolist())
    n_trials = int(df.trial.max())
    out = {"n_parts": len(parts), "n_appraisers": len(appraisers), "n_trials": n_trials, "n_ratings": len(df)}

    within = {}
    for a in appraisers:
        piv = df[df.appraiser == a].pivot(index="part", columns="trial", values="rating")
        within[a] = float((piv.nunique(axis=1) == 1).mean())
    out["within_appraiser"] = within
    out["within_appraiser_mean"] = float(np.mean(list(within.values())))

    standard = params.get("standard")
    if standard:
        df["truth"] = df["part"].map(lambda p: standard[p]).astype(int)
        out["overall_effectiveness"] = float((df["rating"] == df["truth"]).mean())
        eff, cohen = {}, {}
        for a in appraisers:
            sub = df[df.appraiser == a]
            eff[a] = float((sub["rating"] == sub["truth"]).mean())
            t1 = sub[sub.trial == 1].set_index("part").loc[parts]
            cohen[a] = cohen_kappa_binary(t1["rating"].values, t1["truth"].values)
        out["appraiser_effectiveness"] = eff
        out["cohen_kappa_vs_standard"] = cohen

    t1 = df[df.trial == 1].pivot(index="part", columns="appraiser", values="rating").loc[parts, appraisers]
    out["fleiss"] = fleiss_kappa_binary(t1.values)
    out["fleiss_kappa_appraisers"] = out["fleiss"]["kappa"]
    return out


def resolve(obj, path):
    cur = obj
    for part in path.replace("]", "").replace("[", ".").split("."):
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            cur = cur[part]
    return cur


def compute_one(ex_id):
    meta, cols = load(ex_id)
    kind, params = meta["kind"], meta.get("params", {})
    if kind == "capability":
        groups = cols.get("subgroup")
        res = capability(cols["x"], params, groups)
    elif kind == "imr":
        res = imr_chart(cols["x"])
    elif kind == "xbar_r":
        res = xbar_r_chart(cols["x"], cols["subgroup"])
    elif kind == "xbar_s":
        res = xbar_s_chart(cols["x"], cols["subgroup"])
    elif kind == "p":
        res = p_chart(cols["n"], cols["defectives"])
    elif kind == "np":
        res = np_chart(params["n"], cols["defectives"])
    elif kind == "c":
        res = c_chart(cols["defects"])
    elif kind == "u":
        res = u_chart(cols["n"], cols["defects"])
    elif kind == "ewma":
        res = ewma_chart(cols["x"], params)
    elif kind == "cusum":
        res = cusum_chart(cols["x"], params)
    elif kind == "grr":
        res = grr(cols, params)
    elif kind == "grr_summary":
        res = grr_from_ms(params["ms_full"], params["df_full"], params["ms_reduced"], params["df_reduced"],
                          params["parts"], params["operators"], params["replicates"], params.get("tolerance"),
                          params.get("study_var_k", 6.0), params.get("alpha_remove", 0.05))
    elif kind == "factorial":
        res = factorial(cols, params)
    elif kind == "ttest2":
        res = ttest2(cols, params)
    elif kind == "anova1":
        res = anova1(cols, params)
    elif kind == "paired":
        res = paired(cols, params)
    elif kind == "ttest1":
        res = one_sample(cols["x"], params["mu0"], params.get("alpha", 0.05))
    elif kind == "regression":
        res = regression(cols, params)
    elif kind == "samplesize":
        res = samplesize(params)
    elif kind == "dpmo":
        res = dpmo_block(params["defects"], params["units"], params["opportunities"])
    elif kind == "sigma_table":
        res = sigma_table(params)
    elif kind == "descriptive":
        res = descriptive_block(cols["x"], params)
    elif kind == "subgroup_means":
        res = subgroup_means(cols["x"], params)
    elif kind == "binomial_poisson":
        res = binomial_poisson(params)
    elif kind == "vsm":
        res = vsm_metrics(params)
    elif kind == "funnel":
        res = funnel_sim(cols["e"], params)
    elif kind == "funnel_growth":
        res = funnel_growth(cols, params)
    elif kind == "capability_nonnormal":
        res = capability_nonnormal(cols["x"], params)
    elif kind == "attribute_capability":
        res = attribute_capability(cols["n"], cols["defectives"], params)
    elif kind == "chisq":
        res = chisq(cols, params)
    elif kind == "mannwhitney":
        res = mannwhitney(cols, params)
    elif kind == "power":
        res = power(params)
    elif kind == "arl":
        res = arl_table(params)
    elif kind == "p_prime":
        res = p_prime_chart(cols["n"], cols["defectives"])
    elif kind == "dnom":
        res = dnom_chart(cols)
    elif kind == "attribute_agreement":
        res = attribute_agreement(cols, params)
    elif kind == "pareto":
        res = pareto(cols)
    else:
        raise ValueError(f"unknown kind {kind}")
    checks = []
    ok = True
    for path, (want, tol) in (meta.get("expected") or {}).items():
        got = resolve(res, path)
        good = got is not None and abs(got - want) <= tol
        ok &= good
        checks.append({"key": path, "expected": want, "got": got, "tol": tol, "ok": good})
    doc = {"id": ex_id, "kind": kind, "params": params, "source": meta.get("source"), "results": res,
           "expected_checks": checks, "expected_ok": ok}
    with open(os.path.join(RESULTS, ex_id + ".json"), "w") as f:
        json.dump(doc, f, indent=1, default=float)
    return ok, checks


def main(argv):
    ids = argv[1:] or sorted(f[:-5] for f in os.listdir(DATA) if f.endswith(".json"))
    all_ok = True
    for ex_id in ids:
        ok, checks = compute_one(ex_id)
        all_ok &= ok
        tag = "OK  " if ok else "FAIL"
        print(f"  {tag} {ex_id}" + (f" ({len(checks)} published checks)" if checks else ""))
        for c in checks:
            if not c["ok"]:
                print(f"       {c['key']}: expected {c['expected']}, got {c['got']}")
    print("compute.py:", "ALL PASSED" if all_ok else "FAILURES")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
