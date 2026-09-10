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
