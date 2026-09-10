"""
recompute.py - Check 2: recomputes every number in verification/results/ by
a different route from compute.py and compares to the displayed precision.

Rules of this file: no numpy, scipy, pandas or statsmodels. Textbook formulas
written out in plain Python: sums of squares by hand, Rbar/d2 and Sbar/c4,
the AIAG MSA ANOVA method for gauge R&R, the contrast (Yates-style) method
for factorial effects, Welch-Satterthwaite by hand. Distribution functions
are implemented here from first principles:
  normal CDF      from math.erfc
  inverse normal  bisection on the CDF
  regularized incomplete beta (Lentz continued fraction, as in Numerical
                  Recipes 3rd ed. section 6.4) for t and F CDFs
  regularized incomplete gamma (series and continued fraction, NR 6.2) for
                  the chi-square CDF
  inverse t / chi-square by bisection
Any disagreement with compute.py beyond the tolerance is a bug in one of the
two routes and stops the build.
"""
import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
RESULTS = os.path.join(HERE, "results")
CONST = json.load(open(os.path.join(HERE, "constants.json")))
D2_MR = CONST["2"]["d2"]

# --------------------------------------------------------------------------
# Distribution functions from first principles
# --------------------------------------------------------------------------
def norm_cdf(z):
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def norm_sf(z):
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def norm_ppf(p):
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def _betacf(a, b, x):
    MAXIT, EPS, FPMIN = 300, 1e-15, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    if abs(d) < FPMIN: d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN: d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN: d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h


def betainc(a, b, x):
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def gammainc(a, x):
    """Regularized lower incomplete gamma P(a, x)."""
    if x <= 0.0: return 0.0
    if x < a + 1.0:
        ap, s, de = a, 1.0 / a, 1.0 / a
        for _ in range(1000):
            ap += 1.0
            de *= x / ap
            s += de
            if abs(de) < abs(s) * 1e-16:
                break
        return s * math.exp(-x + a * math.log(x) - math.lgamma(a))
    FPMIN = 1e-300
    b = x + 1.0 - a
    c = 1.0 / FPMIN
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < FPMIN: d = FPMIN
        c = b + an / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-16:
            break
    return 1.0 - math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def t_cdf(t, df):
    x = df / (df + t * t)
    tail = 0.5 * betainc(df / 2.0, 0.5, x)
    return 1.0 - tail if t > 0 else tail


def t_ppf(p, df):
    lo, hi = -1e4, 1e4
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < p: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)


def f_cdf(F, d1, d2):
    if F <= 0: return 0.0
    return betainc(d1 / 2.0, d2 / 2.0, d1 * F / (d1 * F + d2))


def f_sf(F, d1, d2):
    if F <= 0: return 1.0
    return betainc(d2 / 2.0, d1 / 2.0, d2 / (d1 * F + d2))


def chi2_cdf(x, k):
    return gammainc(k / 2.0, x / 2.0)


def chi2_ppf(p, k):
    lo, hi = 0.0, max(1000.0, 10.0 * k)
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if chi2_cdf(mid, k) < p: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)


# --------------------------------------------------------------------------
# Plain-Python statistics
# --------------------------------------------------------------------------
def mean(x): return sum(x) / len(x)


def sd(x):
    m = mean(x)
    return math.sqrt(sum((v - m) ** 2 for v in x) / (len(x) - 1))


def median(x):
    s = sorted(x); n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def quantile_weibull(x, p):
    s = sorted(x); n = len(s)
    h = (n + 1) * p
    j = int(math.floor(h))
    g = h - j
    if j < 1: return s[0]
    if j >= n: return s[-1]
    return s[j - 1] + g * (s[j] - s[j - 1])


def ad_normal(x):
    """Anderson-Darling A2 for normality with estimated parameters, and the
    p-value from the adjusted statistic (D'Agostino & Stephens 1986, Table 4.9)."""
    n = len(x); m = mean(x); s = sd(x)
    z = sorted((v - m) / s for v in x)
    tot = 0.0
    for i in range(n):
        tot += (2 * i + 1) * (math.log(norm_cdf(z[i])) + math.log(1.0 - norm_cdf(z[n - 1 - i])))
    a2 = -n - tot / n
    a2s = a2 * (1.0 + 0.75 / n + 2.25 / n ** 2)
    if a2s >= 0.6: p = math.exp(1.2937 - 5.709 * a2s + 0.0186 * a2s ** 2)
    elif a2s >= 0.34: p = math.exp(0.9177 - 4.279 * a2s - 1.38 * a2s ** 2)
    elif a2s >= 0.2: p = 1 - math.exp(-8.318 + 42.796 * a2s - 59.938 * a2s ** 2)
    else: p = 1 - math.exp(-13.436 + 101.14 * a2s - 223.73 * a2s ** 2)
    return a2, a2s, p


def run_rules(v, center, sig):
    n = len(v)
    sigs = sig if isinstance(sig, list) else [sig] * n
    z = [(v[i] - center) / sigs[i] for i in range(n)]
    out = {"we1": [], "we2": [], "we3": [], "we4": [], "n2": [], "n3": [], "n4": [], "n7": [], "n8": []}
    for i in range(n):
        if abs(z[i]) > 3: out["we1"].append(i + 1)
        if i >= 2:
            w = z[i - 2:i + 1]
            if (sum(1 for q in w if q > 2) >= 2 and w[-1] > 2) or (sum(1 for q in w if q < -2) >= 2 and w[-1] < -2):
                out["we2"].append(i + 1)
        if i >= 4:
            w = z[i - 4:i + 1]
            if (sum(1 for q in w if q > 1) >= 4 and w[-1] > 1) or (sum(1 for q in w if q < -1) >= 4 and w[-1] < -1):
                out["we3"].append(i + 1)
        if i >= 7:
            w = z[i - 7:i + 1]
            if all(q > 0 for q in w) or all(q < 0 for q in w): out["we4"].append(i + 1)
        if i >= 8:
            w = z[i - 8:i + 1]
            if all(q > 0 for q in w) or all(q < 0 for q in w): out["n2"].append(i + 1)
        if i >= 5:
            w = v[i - 5:i + 1]
            if all(w[j + 1] > w[j] for j in range(5)) or all(w[j + 1] < w[j] for j in range(5)): out["n3"].append(i + 1)
        if i >= 13:
            w = v[i - 13:i + 1]
            d = [w[j + 1] - w[j] for j in range(13)]
            if all(q != 0 for q in d) and all(d[j] * d[j + 1] < 0 for j in range(12)): out["n4"].append(i + 1)
        if i >= 14:
            if all(abs(q) < 1 for q in z[i - 14:i + 1]): out["n7"].append(i + 1)
        if i >= 7:
            w = z[i - 7:i + 1]
            if all(abs(q) > 1 for q in w) and any(q > 0 for q in w) and any(q < 0 for q in w): out["n8"].append(i + 1)
    return out


def load(ex_id):
    meta = json.load(open(os.path.join(DATA, ex_id + ".json")))
    cols = {}
    p = os.path.join(DATA, ex_id + ".csv")
    if os.path.exists(p):
        with open(p, newline="") as f:
            r = csv.reader(f); header = next(r); cols = {h: [] for h in header}
            for row in r:
                for h, v in zip(header, row):
                    try: cols[h].append(float(v))
                    except ValueError: cols[h].append(v)
    return meta, cols


# --------------------------------------------------------------------------
# Recomputation per kind. Each returns a flat dict path -> value that is
# compared with the same path in results/<id>.json.
# --------------------------------------------------------------------------
def r_imr(x, prefix=""):
    n = len(x)
    mr = [abs(x[i] - x[i - 1]) for i in range(1, n)]
    xbar, mrbar = mean(x), mean(mr)
    sig = mrbar / D2_MR
    out = {"xbar": xbar, "mrbar": mrbar, "sigma_within": sig, "ucl_x": xbar + 3 * sig, "lcl_x": xbar - 3 * sig,
           "ucl_mr": CONST["2"]["D4"] * mrbar, "lcl_mr": 0.0}
    rr = run_rules(x, xbar, sig)
    for k, v in rr.items(): out[f"rules_x.{k}"] = v
    out["beyond_mr"] = [i + 1 for i, v in enumerate(mr) if v > out["ucl_mr"]]
    out["stable"] = len(rr["we1"]) == 0 and len(out["beyond_mr"]) == 0
    return {prefix + k: v for k, v in out.items()}, sig


def _groups(x, g):
    order = []
    d = {}
    for gi, xi in zip(g, x):
        if gi not in d: d[gi] = []; order.append(gi)
        d[gi].append(xi)
    return [d[k] for k in order]


def r_xbar_r(x, g, prefix=""):
    subs = _groups(x, g)
    n = len(subs[0]); c = CONST[str(n)]
    means = [mean(s) for s in subs]; ranges = [max(s) - min(s) for s in subs]
    xbb, rbar = mean(means), mean(ranges)
    out = {"xbarbar": xbb, "rbar": rbar, "ucl_x": xbb + c["A2"] * rbar, "lcl_x": xbb - c["A2"] * rbar,
           "ucl_r": c["D4"] * rbar, "lcl_r": c["D3"] * rbar, "sigma_within": rbar / c["d2"], "means": means, "ranges": ranges}
    rr = run_rules(means, xbb, c["A2"] * rbar / 3.0)
    for k, v in rr.items(): out[f"rules_x.{k}"] = v
    out["beyond_r"] = [i + 1 for i, v in enumerate(ranges) if v > out["ucl_r"] or v < out["lcl_r"]]
    out["stable"] = len(rr["we1"]) == 0 and len(out["beyond_r"]) == 0
    return {prefix + k: v for k, v in out.items()}, rbar / c["d2"]


def r_xbar_s(x, g, prefix=""):
    subs = _groups(x, g)
    n = len(subs[0]); c = CONST[str(n)]
    means = [mean(s) for s in subs]; sds = [sd(s) for s in subs]
    xbb, sbar = mean(means), mean(sds)
    out = {"xbarbar": xbb, "sbar": sbar, "ucl_x": xbb + c["A3"] * sbar, "lcl_x": xbb - c["A3"] * sbar,
           "ucl_s": c["B4"] * sbar, "lcl_s": c["B3"] * sbar, "sigma_within": sbar / c["c4"], "means": means, "sds": sds}
    rr = run_rules(means, xbb, c["A3"] * sbar / 3.0)
    for k, v in rr.items(): out[f"rules_x.{k}"] = v
    out["beyond_s"] = [i + 1 for i, v in enumerate(sds) if v > out["ucl_s"] or v < out["lcl_s"]]
    out["stable"] = len(rr["we1"]) == 0 and len(out["beyond_s"]) == 0
    return {prefix + k: v for k, v in out.items()}, sbar / c["c4"]


def ppm(mean_, sig, usl, lsl):
    pu = norm_sf((usl - mean_) / sig) if usl is not None else 0.0
    pl = norm_cdf((lsl - mean_) / sig) if lsl is not None else 0.0
    return pu * 1e6, pl * 1e6, (pu + pl) * 1e6


def r_descriptive(x, prefix="descriptive."):
    n = len(x); m = mean(x); s = sd(x)
    ss = sum((v - m) ** 2 for v in x)
    out = {"n": n, "mean": m, "s": s, "median": median(x), "sd_pop": math.sqrt(ss / n), "ss": ss, "sum": sum(x),
           "min": min(x), "max": max(x), "range": max(x) - min(x),
           "q1": quantile_weibull(x, 0.25), "q3": quantile_weibull(x, 0.75), "sem": s / math.sqrt(n)}
    m2 = ss / n; m3 = sum((v - m) ** 3 for v in x) / n; m4 = sum((v - m) ** 4 for v in x) / n
    g1 = m3 / m2 ** 1.5; g2 = m4 / m2 ** 2 - 3
    if n > 2: out["skewness"] = math.sqrt(n * (n - 1)) / (n - 2) * g1
    if n > 3: out["kurtosis_excess"] = (n - 1) / ((n - 2) * (n - 3)) * ((n + 1) * g2 + 6)
    if n >= 8:
        a2, a2s, adp = ad_normal(x)
        out["ad_A2"] = a2; out["ad_A2_adjusted"] = a2s; out["ad_p"] = adp
    return {prefix + k: v for k, v in out.items()}


def r_descriptive_block(meta, cols):
    p = meta["params"]; x = cols["x"]
    out = r_descriptive(x)
    usl, lsl = p.get("usl"), p.get("lsl")
    if usl is not None or lsl is not None:
        n_out = sum(1 for v in x if (usl is not None and v > usl) or (lsl is not None and v < lsl))
        out["observed.n_out"] = n_out; out["observed.fraction_out"] = n_out / len(x)
    if p.get("log"):
        lx = [math.log(v) for v in x]
        out.update(r_descriptive(lx, "log."))
        out["log.geometric_mean"] = math.exp(mean(lx))
    return out


def r_subgroup_means(meta, cols):
    x = cols["x"]; s = sd(x); N = len(x)
    out = {"individuals.n": N, "individuals.mean": mean(x), "individuals.s": s}
    out["individuals.skewness"] = r_descriptive(x)["descriptive.skewness"]
    for n in meta["params"]["sizes"]:
        k = N // n
        m = [mean(x[i * n:(i + 1) * n]) for i in range(k)]
        dm = r_descriptive(m, "")
        pre = f"n{n}."
        out[pre + "n"] = n; out[pre + "k"] = k; out[pre + "means"] = m
        out[pre + "mean_of_means"] = dm["mean"]; out[pre + "sd_of_means"] = dm["s"]
        out[pre + "s_over_sqrt_n"] = s / math.sqrt(n); out[pre + "ratio"] = dm["s"] / (s / math.sqrt(n))
        out[pre + "skewness_of_means"] = dm["skewness"]
        if k >= 8: out[pre + "ad_p"] = dm["ad_p"]
    return out


def r_binomial_poisson(meta):
    p = meta["params"]; n, pr, lam, ks = p["n"], p["p"], p["lambda"], [int(k) for k in p["k"]]
    def bpmf(k): return math.comb(n, k) * pr ** k * (1 - pr) ** (n - k)
    def ppmf(k): return math.exp(-lam) * lam ** k / math.factorial(k)
    out = {"binomial.mean": n * pr, "binomial.sd": math.sqrt(n * pr * (1 - pr)), "poisson.mean": lam, "poisson.sd": math.sqrt(lam)}
    for i, k in enumerate(ks):
        out[f"binomial.pmf.{i}"] = bpmf(k); out[f"binomial.cdf.{i}"] = sum(bpmf(j) for j in range(k + 1))
        out[f"poisson.pmf.{i}"] = ppmf(k); out[f"poisson.cdf.{i}"] = sum(ppmf(j) for j in range(k + 1))
    return out


def r_capability(meta, cols):
    p = meta["params"]; x = cols["x"]
    usl, lsl, tgt = p.get("usl"), p.get("lsl"), p.get("target")
    nl, nu = p.get("natural_lower"), p.get("natural_upper")
    chart = p.get("chart", "imr" if p.get("subgroup_size", 1) == 1 else "xbar_r")
    n = len(x); m = mean(x); s = sd(x)
    out = r_descriptive(x)
    if chart == "imr": ch, sw = r_imr(x, "chart.")
    elif chart == "xbar_s": ch, sw = r_xbar_s(x, cols["subgroup"], "chart.")
    else: ch, sw = r_xbar_r(x, cols["subgroup"], "chart.")
    out.update(ch)
    out["within.sigma"] = sw
    for name, sig, pre in (("overall", s, "P"), ("within", sw, "Cw")):
        cu = (usl - m) / (3 * sig) if usl is not None else None
        cl = (m - lsl) / (3 * sig) if lsl is not None else None
        both = [v for v in (cu, cl) if v is not None]
        kk = "Pp" if name == "overall" else "Cw"
        out[f"{name}.{kk}u"] = cu; out[f"{name}.{kk}l"] = cl; out[f"{name}.{kk}k"] = min(both)
        if usl is not None and lsl is not None:
            out[f"{name}.{kk}"] = (usl - lsl) / (6 * sig)
            if name == "overall":
                out["overall.k"] = abs((usl + lsl) / 2 - m) / ((usl - lsl) / 2)
                if tgt is not None: out["overall.Cpm"] = (usl - lsl) / (6 * math.sqrt(sig ** 2 + (m - tgt) ** 2))
        else:
            lo = lsl if lsl is not None else nl; hi = usl if usl is not None else nu
            if lo is not None and hi is not None: out[f"{name}.{kk}_natural"] = (hi - lo) / (6 * sig)
        pu, pl, pt = ppm(m, sig, usl, lsl)
        out[f"{name}.ppm_upper"] = pu; out[f"{name}.ppm_lower"] = pl; out[f"{name}.ppm_total"] = pt
    z = norm_ppf(0.975)
    ppk = out["overall.Ppk"]
    se = math.sqrt(1 / (9 * n) + ppk ** 2 / (2 * (n - 1)))
    out["overall.Ppk_ci95"] = [ppk - z * se, ppk + z * se]
    if "overall.Pp" in out:
        out["overall.Pp_ci95"] = [out["overall.Pp"] * math.sqrt(chi2_ppf(0.025, n - 1) / (n - 1)),
                                  out["overall.Pp"] * math.sqrt(chi2_ppf(0.975, n - 1) / (n - 1))]
    nout = sum(1 for v in x if (usl is not None and v > usl) or (lsl is not None and v < lsl))
    out["observed.n_out"] = nout; out["observed.ppm_observed"] = nout * 1e6 / n
    out["legacy.Cpk"] = out["within.Cwk"]; out["legacy.Ppk"] = out["overall.Ppk"]
    return out


def r_p(cols):
    n = cols["n"]; d = cols["defectives"]
    pbar = sum(d) / sum(n)
    p = [d[i] / n[i] for i in range(len(n))]
    sig = [math.sqrt(pbar * (1 - pbar) / ni) for ni in n]
    ucl = [pbar + 3 * s for s in sig]; lcl = [max(0.0, pbar - 3 * s) for s in sig]
    out = {"pbar": pbar, "p": p, "ucl": ucl, "lcl": lcl}
    for k, v in run_rules(p, pbar, sig).items(): out[f"rules.{k}"] = v
    out["beyond"] = [i + 1 for i in range(len(n)) if p[i] > ucl[i] or p[i] < lcl[i]]
    return out


def r_np(meta, cols):
    n = meta["params"]["n"]; d = cols["defectives"]
    npbar = mean(d); pbar = npbar / n; sig = math.sqrt(n * pbar * (1 - pbar))
    out = {"npbar": npbar, "pbar": pbar, "ucl": npbar + 3 * sig, "lcl": max(0.0, npbar - 3 * sig)}
    for k, v in run_rules(d, npbar, sig).items(): out[f"rules.{k}"] = v
    out["beyond"] = [i + 1 for i, v in enumerate(d) if v > out["ucl"] or v < out["lcl"]]
    return out


def r_c(cols):
    c = cols["defects"]; cbar = mean(c); sig = math.sqrt(cbar)
    out = {"cbar": cbar, "ucl": cbar + 3 * sig, "lcl": max(0.0, cbar - 3 * sig)}
    for k, v in run_rules(c, cbar, sig).items(): out[f"rules.{k}"] = v
    out["beyond"] = [i + 1 for i, v in enumerate(c) if v > out["ucl"] or v < out["lcl"]]
    return out


def r_u(cols):
    n = cols["n"]; c = cols["defects"]
    ubar = sum(c) / sum(n); u = [c[i] / n[i] for i in range(len(n))]
    sig = [math.sqrt(ubar / ni) for ni in n]
    ucl = [ubar + 3 * s for s in sig]; lcl = [max(0.0, ubar - 3 * s) for s in sig]
    out = {"ubar": ubar, "u": u, "ucl": ucl, "lcl": lcl}
    for k, v in run_rules(u, ubar, sig).items(): out[f"rules.{k}"] = v
    out["beyond"] = [i + 1 for i in range(len(n)) if u[i] > ucl[i] or u[i] < lcl[i]]
    return out


def r_ewma(meta, cols):
    p = meta["params"]; x = cols["x"]; lam = p["lambda"]; L = p.get("L", 3.0)
    base = p.get("baseline", len(x))
    sigma = p["sigma"] if "sigma" in p else mean([abs(x[i] - x[i - 1]) for i in range(1, base)]) / D2_MR
    target = p["target"] if "target" in p else mean(x[:base])
    z = []; prev = target
    for v in x:
        prev = lam * v + (1 - lam) * prev; z.append(prev)
    n = len(x)
    asym = L * sigma * math.sqrt(lam / (2 - lam))
    out = {"sigma": sigma, "target": target, "ewma": z, "ucl_asymptotic": target + asym, "lcl_asymptotic": target - asym}
    if p.get("limits") == "asymptotic":
        out["ucl"] = target + asym; out["lcl"] = target - asym
        out["signals"] = [i + 1 for i in range(n) if z[i] > out["ucl"] or z[i] < out["lcl"]]
    else:
        half = [L * sigma * math.sqrt(lam / (2 - lam) * (1 - (1 - lam) ** (2 * (i + 1)))) for i in range(n)]
        out["ucl"] = [target + h for h in half]; out["lcl"] = [target - h for h in half]
        out["signals"] = [i + 1 for i in range(n) if z[i] > out["ucl"][i] or z[i] < out["lcl"][i]]
    return out


def r_cusum(meta, cols):
    p = meta["params"]; x = cols["x"]; k, h = p["k"], p["h"]
    base = p.get("baseline", len(x))
    sigma = p.get("sigma", mean([abs(x[i] - x[i - 1]) for i in range(1, base)]) / D2_MR)
    target = p.get("target", mean(x[:base]))
    cp, cm, up, lo = [], [], 0.0, 0.0
    for v in x:
        zi = (v - target) / sigma
        up = max(0.0, up + zi - k); lo = max(0.0, lo - zi - k)
        cp.append(up); cm.append(lo)
    return {"sigma": sigma, "target": target, "c_plus": cp, "c_minus": cm,
            "signals_plus": [i + 1 for i, v in enumerate(cp) if v > h],
            "signals_minus": [i + 1 for i, v in enumerate(cm) if v > h]}


def grr_from_ms(msf, dff, msr, dfr, P, O, R, tol, ksv, alpha):
    Fi = msf["interaction"] / msf["repeatability"]
    pi = f_sf(Fi, dff["interaction"], dff["repeatability"])
    out = {"interaction_F": Fi, "interaction_p": pi, "interaction_removed": pi > alpha}
    if pi > alpha:
        rep = msr["repeatability"]; inter = 0.0
        op = max(0.0, (msr["operator"] - rep) / (P * R)); part = max(0.0, (msr["part"] - rep) / (O * R))
        out["F_operator"] = msr["operator"] / rep; out["F_part"] = msr["part"] / rep
        out["p_operator"] = f_sf(out["F_operator"], dfr["operator"], dfr["repeatability"])
        out["p_part"] = f_sf(out["F_part"], dfr["part"], dfr["repeatability"])
    else:
        rep = msf["repeatability"]; inter = max(0.0, (msf["interaction"] - rep) / R)
        op = max(0.0, (msf["operator"] - msf["interaction"]) / (P * R)); part = max(0.0, (msf["part"] - msf["interaction"]) / (O * R))
        out["F_operator"] = msf["operator"] / msf["interaction"]; out["F_part"] = msf["part"] / msf["interaction"]
        out["p_operator"] = f_sf(out["F_operator"], dff["operator"], dff["interaction"])
        out["p_part"] = f_sf(out["F_part"], dff["part"], dff["interaction"])
    vc = {"repeatability": rep, "reproducibility": op + inter, "operator": op, "interaction": inter,
          "grr": rep + op + inter, "part": part, "total": rep + op + inter + part}
    for k, v in vc.items():
        out[f"varcomp.{k}"] = v; out[f"pct_contribution.{k}"] = 100 * v / vc["total"]
        out[f"sd.{k}"] = math.sqrt(v); out[f"study_var.{k}"] = ksv * math.sqrt(v)
        out[f"pct_study_var.{k}"] = 100 * math.sqrt(v) / math.sqrt(vc["total"])
        if tol: out[f"pct_tolerance.{k}"] = 100 * ksv * math.sqrt(v) / tol
    out["ndc_exact"] = 1.41 * math.sqrt(part) / math.sqrt(vc["grr"])
    out["ndc"] = max(1, math.floor(out["ndc_exact"]))
    return out


def r_grr(meta, cols):
    p = meta["params"]
    parts = [str(int(v)) if isinstance(v, float) else str(v) for v in cols["part"]]
    ops = [str(v) for v in cols["operator"]]; y = cols["y"]
    P = len(set(parts)); O = len(set(ops)); N = len(y); R = N // (P * O)
    gm = mean(y)
    pm = {pp: mean([y[i] for i in range(N) if parts[i] == pp]) for pp in set(parts)}
    om = {oo: mean([y[i] for i in range(N) if ops[i] == oo]) for oo in set(ops)}
    cm = {(pp, oo): mean([y[i] for i in range(N) if parts[i] == pp and ops[i] == oo]) for pp in set(parts) for oo in set(ops)}
    ss_part = O * R * sum((v - gm) ** 2 for v in pm.values())
    ss_op = P * R * sum((v - gm) ** 2 for v in om.values())
    ss_cells = R * sum((v - gm) ** 2 for v in cm.values())
    ss_int = ss_cells - ss_part - ss_op
    ss_tot = sum((v - gm) ** 2 for v in y)
    ss_rep = ss_tot - ss_cells
    dff = {"part": P - 1, "operator": O - 1, "interaction": (P - 1) * (O - 1), "repeatability": P * O * (R - 1)}
    msf = {"part": ss_part / dff["part"], "operator": ss_op / dff["operator"], "interaction": ss_int / dff["interaction"],
           "repeatability": ss_rep / dff["repeatability"]}
    dfr = {"part": P - 1, "operator": O - 1, "repeatability": dff["interaction"] + dff["repeatability"]}
    msr = {"part": msf["part"], "operator": msf["operator"], "repeatability": (ss_int + ss_rep) / dfr["repeatability"]}
    out = {"ss_full.part": ss_part, "ss_full.operator": ss_op, "ss_full.interaction": ss_int, "ss_full.repeatability": ss_rep,
           "ss_full.total": ss_tot, "ms_full.part": msf["part"], "ms_full.operator": msf["operator"],
           "ms_full.interaction": msf["interaction"], "ms_full.repeatability": msf["repeatability"],
           "ms_reduced.repeatability": msr["repeatability"], "df_reduced.repeatability": dfr["repeatability"], "grand_mean": gm}
    out.update(grr_from_ms(msf, dff, msr, dfr, P, O, R, p.get("tolerance"), p.get("study_var_k", 6.0), p.get("alpha_remove", 0.05)))
    return out


def r_factorial(meta, cols):
    p = meta["params"]; names = p["factors"]; k = p["k"]; y = cols["y"]; N = len(y)
    signs = {nm: cols[nm] for nm in names}
    # all interaction terms
    from itertools import combinations
    terms = []
    for r in range(1, k + 1):
        for combo in combinations(names, r): terms.append(combo)
    out = {"grand_mean": mean(y)}
    contrasts = {}
    for combo in terms:
        label = "".join(combo)
        c = 0.0
        for i in range(N):
            s = 1.0
            for nm in combo: s *= signs[nm][i]
            c += s * y[i]
        contrasts[label] = c
        out[f"effects.{label}"] = c / (N / 2.0)          # effect = contrast / (r 2^(k-1))
        out[f"coefficients.{label}"] = c / N            # coefficient = effect / 2
    if N > 2 ** k:
        sst = sum((v - out["grand_mean"]) ** 2 for v in y)
        ss_model = 0.0
        for label, c in contrasts.items():
            ss = c * c / N                               # SS = contrast^2 / (r 2^k)
            out[f"anova.{label}.ss"] = ss; ss_model += ss
        ss_res = sst - ss_model; df_res = N - 2 ** k; mse = ss_res / df_res
        out["anova.residual.ss"] = ss_res; out["anova.residual.df"] = df_res; out["anova.residual.ms"] = mse
        out["anova.total.ss"] = sst
        for label in contrasts:
            F = out[f"anova.{label}.ss"] / mse
            out[f"anova.{label}.F"] = F; out[f"anova.{label}.p"] = f_sf(F, 1, df_res)
        out["residual_sd"] = math.sqrt(mse); out["se_effect"] = 2 * math.sqrt(mse / N)
        out["r2"] = 1 - ss_res / sst; out["r2_adj"] = 1 - (ss_res / df_res) / (sst / (N - 1))
    return out


def r_ttest2(meta, cols):
    alpha = meta["params"].get("alpha", 0.05)
    groups = []
    for g in cols["group"]:
        if g not in groups: groups.append(g)
    a = [cols["x"][i] for i in range(len(cols["x"])) if cols["group"][i] == groups[0]]
    b = [cols["x"][i] for i in range(len(cols["x"])) if cols["group"][i] == groups[1]]
    na, nb = len(a), len(b); ma, mb = mean(a), mean(b); va, vb = sd(a) ** 2, sd(b) ** 2
    diff = ma - mb
    sp = math.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
    se_p = sp * math.sqrt(1 / na + 1 / nb); dfp = na + nb - 2; tp = diff / se_p
    tc = t_ppf(1 - alpha / 2, dfp)
    out = {"diff": diff, "pooled.sp": sp, "pooled.se": se_p, "pooled.t": tp, "pooled.df": dfp,
           "pooled.p": 2 * (1 - t_cdf(abs(tp), dfp)), "pooled.ci": [diff - tc * se_p, diff + tc * se_p], "cohen_d": diff / sp}
    se_w = math.sqrt(va / na + vb / nb)
    dfw = (va / na + vb / nb) ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    tw = diff / se_w; tcw = t_ppf(1 - alpha / 2, dfw)
    out.update({"welch.se": se_w, "welch.t": tw, "welch.df": dfw, "welch.p": 2 * (1 - t_cdf(abs(tw), dfw)),
                "welch.ci": [diff - tcw * se_w, diff + tcw * se_w]})
    Fv = va / vb
    out["variance_tests.F"] = Fv
    out["variance_tests.F_p"] = 2 * min(f_cdf(Fv, na - 1, nb - 1), f_sf(Fv, na - 1, nb - 1))
    W, pW = levene([a, b])
    out["variance_tests.levene_W"] = W; out["variance_tests.levene_p"] = pW
    return out


def levene(samples):
    """Brown-Forsythe form (deviations from the group median), as scipy center='median'."""
    devs = [[abs(v - median(s)) for v in s] for s in samples]
    return anova_F(devs)


def anova_F(samples):
    N = sum(len(s) for s in samples); k = len(samples)
    allv = [v for s in samples for v in s]; gm = mean(allv)
    ssb = sum(len(s) * (mean(s) - gm) ** 2 for s in samples)
    ssw = sum(sum((v - mean(s)) ** 2 for v in s) for s in samples)
    F = (ssb / (k - 1)) / (ssw / (N - k))
    return F, f_sf(F, k - 1, N - k)


def r_anova1(meta, cols):
    groups = []
    for g in cols["group"]:
        if g not in groups: groups.append(g)
    samples = [[cols["x"][i] for i in range(len(cols["x"])) if cols["group"][i] == g] for g in groups]
    N = sum(len(s) for s in samples); k = len(samples)
    gm = mean(cols["x"])
    ssb = sum(len(s) * (mean(s) - gm) ** 2 for s in samples)
    ssw = sum(sum((v - mean(s)) ** 2 for v in s) for s in samples)
    F = (ssb / (k - 1)) / (ssw / (N - k))
    W, pW = levene(samples)
    return {"means": [mean(s) for s in samples], "sds": [sd(s) for s in samples], "grand_mean": gm,
            "ss_between": ssb, "ss_within": ssw, "ss_total": ssb + ssw, "ms_between": ssb / (k - 1), "ms_within": ssw / (N - k),
            "F": F, "p": f_sf(F, k - 1, N - k), "eta2": ssb / (ssb + ssw), "pooled_sd": math.sqrt(ssw / (N - k)),
            "levene_W": W, "levene_p": pW}


def r_one_sample(x, mu0, alpha):
    n = len(x); m = mean(x); s = sd(x); se = s / math.sqrt(n); t = (m - mu0) / se
    tc = t_ppf(1 - alpha / 2, n - 1)
    return {"mean": m, "s": s, "se": se, "t": t, "df": n - 1, "p": 2 * (1 - t_cdf(abs(t), n - 1)),
            "ci": [m - tc * se, m + tc * se], "cohen_d": (m - mu0) / s}


def r_regression(meta, cols):
    x, y = cols["x"], cols["y"]; n = len(x); alpha = meta["params"].get("alpha", 0.05)
    mx, my = mean(x), mean(y)
    sxx = sum((v - mx) ** 2 for v in x); sxy = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    syy = sum((v - my) ** 2 for v in y)
    b1 = sxy / sxx; b0 = my - b1 * mx
    fitted = [b0 + b1 * v for v in x]; resid = [y[i] - fitted[i] for i in range(n)]
    ssr = sum(r * r for r in resid); sse = syy - ssr
    s = math.sqrt(ssr / (n - 2)); se_b1 = s / math.sqrt(sxx); se_b0 = s * math.sqrt(1 / n + mx ** 2 / sxx)
    t1 = b1 / se_b1; tc = t_ppf(1 - alpha / 2, n - 2)
    F = (sse / 1) / (ssr / (n - 2))
    return {"slope": b1, "intercept": b0, "se_slope": se_b1, "se_intercept": se_b0, "t_slope": t1,
            "p_slope": 2 * (1 - t_cdf(abs(t1), n - 2)), "slope_ci": [b1 - tc * se_b1, b1 + tc * se_b1],
            "r": sxy / math.sqrt(sxx * syy), "r2": 1 - ssr / syy, "r2_adj": 1 - (ssr / (n - 2)) / (syy / (n - 1)),
            "s": s, "F": F, "p_F": f_sf(F, 1, n - 2), "ss_regression": sse, "ss_residual": ssr, "ss_total": syy,
            "fitted": fitted, "residuals": resid}


def r_samplesize(meta):
    p = meta["params"]; alpha, beta = p["alpha"], p["beta"]; sides = p.get("sides", 2)
    two = p.get("design", "one-sample") == "two-sample"; mult = 2.0 if two else 1.0
    ratio = (p["sigma"] / p["delta"]) ** 2
    za, zb = norm_ppf(1 - alpha / sides), norm_ppf(1 - beta)
    nz = mult * (za + zb) ** 2 * ratio; n = math.ceil(nz)
    seen = set(); nt = n
    for _ in range(50):
        dfree = 2 * nt - 2 if two else nt - 1
        nn = math.ceil(mult * (t_ppf(1 - alpha / sides, dfree) + t_ppf(1 - beta, dfree)) ** 2 * ratio)
        if nn == nt or nn in seen: nt = max(nn, nt); break
        seen.add(nt); nt = nn
    return {"z_alpha": za, "z_beta": zb, "n_z_exact": nz, "n_z": n, "n_t": nt}


def r_dpmo(meta):
    p = meta["params"]; D, U, O = p["defects"], p["units"], p["opportunities"]
    dpo = D / (U * O); dpmo = dpo * 1e6; dpu = D / U
    z = norm_ppf(1 - dpo)
    return {"dpmo": dpmo, "dpu": dpu, "dpo": dpo, "yield_fty": math.exp(-dpu), "yield_from_dpmo": 1 - dpo,
            "sigma_long_term": z, "sigma_level_shifted": z + 1.5}


def r_sigma_table(meta):
    p = meta["params"]; shift = p.get("shift", 1.5)
    out = {}
    for i, k in enumerate(p["levels"]):
        near, far = norm_sf(k - shift), norm_sf(k + shift)
        out[f"ppm_centered_two_sided.{i}"] = 2e6 * norm_sf(k)
        out[f"ppm_shifted_one_sided.{i}"] = 1e6 * near
        out[f"ppm_shifted_two_sided.{i}"] = 1e6 * (near + far)
        out[f"yield_shifted_one_sided.{i}"] = 1 - near
    for i, t in enumerate(p.get("ppm_targets", [])):
        z = norm_ppf(1 - t / 1e6)
        out[f"z_of_targets.{i}"] = z
        out[f"sigma_level_of_targets.{i}"] = z + shift
    return out


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------
def resolve(obj, path):
    cur = obj
    for part in path.split("."):
        if isinstance(cur, list): cur = cur[int(part)]
        else:
            if part not in cur: return None
            cur = cur[part]
    return cur


def close(a, b, path):
    if isinstance(a, bool) or isinstance(b, bool): return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(close(x, y, path) for x, y in zip(a, b))
    if a is None or b is None: return a is None and b is None
    tol = 1e-6 if (".p" in path or "_p" in path or path.endswith("p")) else 1e-9
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def recompute_one(ex_id):
    meta, cols = load(ex_id)
    res = json.load(open(os.path.join(RESULTS, ex_id + ".json")))["results"]
    kind = meta["kind"]
    if kind == "capability": mine = r_capability(meta, cols)
    elif kind == "imr": mine, _ = r_imr(cols["x"])
    elif kind == "xbar_r": mine, _ = r_xbar_r(cols["x"], cols["subgroup"])
    elif kind == "xbar_s": mine, _ = r_xbar_s(cols["x"], cols["subgroup"])
    elif kind == "p": mine = r_p(cols)
    elif kind == "np": mine = r_np(meta, cols)
    elif kind == "c": mine = r_c(cols)
    elif kind == "u": mine = r_u(cols)
    elif kind == "ewma": mine = r_ewma(meta, cols)
    elif kind == "cusum": mine = r_cusum(meta, cols)
    elif kind == "grr": mine = r_grr(meta, cols)
    elif kind == "grr_summary":
        p = meta["params"]
        mine = grr_from_ms(p["ms_full"], p["df_full"], p["ms_reduced"], p["df_reduced"], p["parts"], p["operators"],
                           p["replicates"], p.get("tolerance"), p.get("study_var_k", 6.0), p.get("alpha_remove", 0.05))
    elif kind == "factorial": mine = r_factorial(meta, cols)
    elif kind == "ttest2": mine = r_ttest2(meta, cols)
    elif kind == "anova1": mine = r_anova1(meta, cols)
    elif kind == "paired":
        d = [cols["after"][i] - cols["before"][i] for i in range(len(cols["after"]))]
        mine = r_one_sample(d, 0.0, meta["params"].get("alpha", 0.05))
    elif kind == "ttest1": mine = r_one_sample(cols["x"], meta["params"]["mu0"], meta["params"].get("alpha", 0.05))
    elif kind == "regression": mine = r_regression(meta, cols)
    elif kind == "samplesize": mine = r_samplesize(meta)
    elif kind == "dpmo": mine = r_dpmo(meta)
    elif kind == "sigma_table": mine = r_sigma_table(meta)
    elif kind == "descriptive": mine = r_descriptive_block(meta, cols)
    elif kind == "subgroup_means": mine = r_subgroup_means(meta, cols)
    elif kind == "binomial_poisson": mine = r_binomial_poisson(meta)
    else: raise ValueError(kind)
    bad = []
    for path, v in mine.items():
        got = resolve(res, path)
        if not close(v, got, path):
            bad.append((path, v, got))
    return len(mine), bad


def main(argv):
    ids = argv[1:] or sorted(f[:-5] for f in os.listdir(RESULTS) if f.endswith(".json") and not f.startswith("_"))
    all_ok = True
    total = 0
    for ex_id in ids:
        n, bad = recompute_one(ex_id)
        total += n
        if bad:
            all_ok = False
            print(f"  FAIL {ex_id}: {len(bad)} of {n} quantities disagree")
            for path, v, got in bad[:10]:
                print(f"       {path}: recompute {v}  compute {got}")
        else:
            print(f"  OK   {ex_id}: {n} quantities agree")
    print(f"recompute.py: {total} quantities compared;", "ALL AGREE" if all_ok else "DISAGREEMENTS")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
