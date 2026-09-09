"""
tables.py - generates every statistical table and control-chart constant used
by the course from scipy, and checks a sample of entries against published
tables. Also writes the reference points used by test_calculators.js to test
the JavaScript numerical functions in assets/js/stats.js against scipy.

Outputs
  verification/constants.json        control-chart constants n = 2..25, rounded
                                     to the precision of published tables. This
                                     is the single table that the course pages,
                                     compute.py, recompute.py and stats.js use,
                                     so a learner with a textbook table
                                     reproduces every limit on a page.
  verification/results/_tables.json  Z, t, chi-square, F tables for tables.html
  verification/results/_refpoints.json  scipy values at test points for
                                     test_calculators.js

Published entries checked here (see SOURCES.md)
  S-B2  NIST/SEMATECH e-Handbook 6.3.2.1: A2, D3, D4 for n = 2..10
  S-A2  AIAG & VDA SPC Manual (2026) pp. 97-98: d2, d3 for n = 2..10
  NIST/SEMATECH e-Handbook 1.3.6.7.2 (t), 1.3.6.7.3 (F), 1.3.6.7.4 (chi-square):
        sample critical values read on 2026-09-09.

Definitions (Montgomery, Introduction to Statistical Quality Control, App. VI):
  d2 = E(R/sigma), d3 = SD(R/sigma) for the range of n normal observations
  c4 = sqrt(2/(n-1)) * Gamma(n/2) / Gamma((n-1)/2)
  A2 = 3/(d2 sqrt n),  D3 = max(0, 1 - 3 d3/d2),  D4 = 1 + 3 d3/d2
  A3 = 3/(c4 sqrt n),  B3 = max(0, 1 - 3 sqrt(1-c4^2)/c4),
  B4 = 1 + 3 sqrt(1-c4^2)/c4,  E2 = 3/d2 (individuals chart)
"""
import json
import math
import os
import sys

import numpy as np
from scipy import integrate, special, stats

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
os.makedirs(RESULTS, exist_ok=True)

Phi = stats.norm.cdf


def d2_exact(n):
    """E(range) of n standard normal observations (Tippett 1925):
    integral over x of 1 - Phi(x)^n - (1 - Phi(x))^n."""
    f = lambda x: 1.0 - Phi(x) ** n - (1.0 - Phi(x)) ** n
    v, _ = integrate.quad(f, -12, 12, limit=400, epsabs=1e-12, epsrel=1e-12)
    return v


def d3_exact(n):
    """SD(range). E(W^2) = 2 * int_{y} int_{x<y}
    [1 - Phi(y)^n - (1 - Phi(x))^n + (Phi(y) - Phi(x))^n] dx dy."""
    def inner(x, y):
        return 1.0 - Phi(y) ** n - (1.0 - Phi(x)) ** n + (Phi(y) - Phi(x)) ** n
    ew2, _ = integrate.dblquad(inner, -10, 10, lambda y: -10, lambda y: y,
                               epsabs=1e-10, epsrel=1e-10)
    return math.sqrt(2.0 * ew2 - d2_exact(n) ** 2)


def c4_exact(n):
    return math.sqrt(2.0 / (n - 1)) * math.exp(
        special.gammaln(n / 2.0) - special.gammaln((n - 1) / 2.0))


def build_constants(nmax=25):
    out = {}
    for n in range(2, nmax + 1):
        d2, d3, c4 = d2_exact(n), d3_exact(n), c4_exact(n)
        out[str(n)] = {
            "d2": round(d2, 3), "d3": round(d3, 4), "c4": round(c4, 4),
            "A2": round(3.0 / (d2 * math.sqrt(n)), 3),
            "D3": round(max(0.0, 1.0 - 3.0 * d3 / d2), 3),
            "D4": round(1.0 + 3.0 * d3 / d2, 3),
            "A3": round(3.0 / (c4 * math.sqrt(n)), 3),
            "B3": round(max(0.0, 1.0 - 3.0 * math.sqrt(1.0 - c4 ** 2) / c4), 3),
            "B4": round(1.0 + 3.0 * math.sqrt(1.0 - c4 ** 2) / c4, 3),
            "E2": round(3.0 / round(d2, 3), 3),  # from the tabulated d2, as published (E2(2) = 2.660)
            "d2_exact": d2, "d3_exact": d3, "c4_exact": c4,
        }
    return out


# Published entries used as checks -------------------------------------------
NIST_A2_D3_D4 = {  # S-B2
    2: (1.880, 0, 3.267), 3: (1.023, 0, 2.575), 4: (0.729, 0, 2.282),
    5: (0.577, 0, 2.115), 6: (0.483, 0, 2.004), 7: (0.419, 0.076, 1.924),
    8: (0.373, 0.136, 1.864), 9: (0.337, 0.184, 1.816), 10: (0.308, 0.223, 1.777)}
AIAGVDA_D2_D3 = {  # S-A2 pp. 97-98
    2: (1.128, 0.8525), 3: (1.693, 0.8884), 4: (2.059, 0.8798), 5: (2.326, 0.8641),
    6: (2.534, 0.8480), 7: (2.704, 0.8332), 8: (2.847, 0.8198), 9: (2.970, 0.8078),
    10: (3.078, 0.7971)}
# NIST 1.3.6.7.2: upper one-sided t critical values (df, alpha)
NIST_T = {(10, 0.05): 1.812, (10, 0.025): 2.228, (20, 0.025): 2.086,
          (5, 0.005): 4.032, (30, 0.05): 1.697, (1, 0.025): 12.706}
# NIST 1.3.6.7.4: chi-square upper-tail critical values (df, alpha)
NIST_CHI2 = {(10, 0.05): 18.307, (10, 0.01): 23.209, (1, 0.05): 3.841,
             (5, 0.05): 11.070, (30, 0.05): 43.773, (20, 0.01): 37.566,
             (10, 0.95): 3.940}
# NIST 1.3.6.7.3: F upper 5 % critical values (d1, d2). The (2,20), (3,30),
# (10,10), (4,15) entries were read from the NIST page; (1,10) and (5,10) are
# the standard values (Montgomery App. IV) because the page reader transposed
# those two cells.
NIST_F05 = {(1, 10): 4.965, (5, 10): 3.326, (2, 20): 3.493, (3, 30): 2.922,
            (10, 10): 2.978, (4, 15): 3.056}


def check(label, got, want, tol):
    ok = abs(got - want) <= tol
    print(f"  {'OK  ' if ok else 'FAIL'} {label}: computed {got:.4f}, published {want}")
    return ok


def public(consts):
    return {k: {kk: vv for kk, vv in v.items() if not kk.endswith("_exact")}
            for k, v in consts.items()}


def main():
    ok = True
    print("Control-chart constants by numerical integration")
    consts = build_constants(25)
    for n, (a2, d3c, d4) in NIST_A2_D3_D4.items():
        r = consts[str(n)]
        ok &= check(f"A2 n={n}", r["A2"], a2, 0.0005)
        ok &= check(f"D3 n={n}", r["D3"], d3c, 0.0005)
        # NIST prints D4(5) = 2.115; the exact value 2.11447 rounds to 2.114,
        # which is what Montgomery and ASTM E2587 print. Tolerance 0.0011.
        ok &= check(f"D4 n={n}", r["D4"], d4, 0.0011)
    for n, (d2, d3) in AIAGVDA_D2_D3.items():
        r = consts[str(n)]
        ok &= check(f"d2 n={n}", r["d2"], d2, 0.0005)
        ok &= check(f"d3 n={n}", r["d3"], d3, 0.00005)
    for n, c4 in {2: 0.7979, 5: 0.9400, 10: 0.9727, 25: 0.9896}.items():
        ok &= check(f"c4 n={n}", consts[str(n)]["c4"], c4, 0.00005)
    ok &= check("E2 n=2", consts["2"]["E2"], 2.660, 0.0005)
    with open(os.path.join(HERE, "constants.json"), "w") as f:
        json.dump(public(consts), f, indent=1)
    # embed the same table in assets/js/stats.js so the calculators use it
    js_path = os.path.join(os.path.dirname(HERE), "assets", "js", "stats.js")
    if os.path.exists(js_path):
        import re
        src = open(js_path, encoding="utf-8").read()
        lit = json.dumps(public(consts), separators=(",", ":"))
        new_src = re.sub(r"/\*CONSTANTS\*/.*?/\*END\*/", "/*CONSTANTS*/" + lit + "/*END*/", src, flags=re.S)
        if new_src != src:
            open(js_path, "w", encoding="utf-8").write(new_src)
            print("  constants table embedded in assets/js/stats.js")

    print("Statistical tables")
    z_rows = [[round(float(Phi(z10 / 10.0 + c / 100.0)), 5) for c in range(10)]
              for z10 in range(0, 40)]
    t_alphas = [0.10, 0.05, 0.025, 0.01, 0.005, 0.001]
    t_dfs = list(range(1, 31)) + [40, 60, 120, 1000000]
    t_rows = {str(df): [round(float(stats.t.ppf(1 - a, df)), 3) for a in t_alphas]
              for df in t_dfs}
    chi_alphas = [0.995, 0.99, 0.975, 0.95, 0.90, 0.10, 0.05, 0.025, 0.01, 0.005]
    chi_dfs = list(range(1, 31)) + [40, 50, 60, 80, 100]
    chi_rows = {str(df): [round(float(stats.chi2.ppf(1 - a, df)), 3) for a in chi_alphas]
                for df in chi_dfs}
    f_d1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 24, 30, 40, 60, 120]
    f_d2 = list(range(1, 31)) + [40, 60, 120, 1000000]
    f_rows = {str(a): {str(d2): [round(float(stats.f.ppf(1 - a, d1, d2)), 3 if a >= 0.05 else 2)
                                 for d1 in f_d1] for d2 in f_d2} for a in (0.05, 0.01)}
    for (df, a), v in NIST_T.items():
        ok &= check(f"t df={df} alpha={a}", float(stats.t.ppf(1 - a, df)), v, 0.0006)
    for (df, a), v in NIST_CHI2.items():
        ok &= check(f"chi2 df={df} alpha={a}", float(stats.chi2.ppf(1 - a, df)), v, 0.0006)
    for (d1, d2), v in NIST_F05.items():
        ok &= check(f"F(0.05; {d1},{d2})", float(stats.f.ppf(0.95, d1, d2)), v, 0.0006)
    ok &= check("Phi(1.96)", float(Phi(1.96)), 0.97500, 0.000005)
    tables = {
        "z": {"rows": z_rows, "note": "Phi(z) for z = row value + column value, 0.00 to 3.99"},
        "t": {"alphas": t_alphas, "dfs": t_dfs, "rows": t_rows,
              "note": "upper one-sided critical values t(alpha, df); df 1000000 stands for infinity"},
        "chi2": {"alphas": chi_alphas, "dfs": chi_dfs, "rows": chi_rows,
                 "note": "upper-tail critical values; alpha 0.95 is the lower 5 % point"},
        "f": {"d1": f_d1, "d2": f_d2, "rows": f_rows,
              "note": "upper critical values at alpha 0.05 (3 decimals) and 0.01 (2 decimals)"},
        "constants": public(consts),
    }
    with open(os.path.join(RESULTS, "_tables.json"), "w") as f:
        json.dump(tables, f)

    print("Reference points for stats.js")
    rng = np.random.default_rng(20260909)
    pts = {}
    xs = np.concatenate([np.linspace(-8, 8, 161), rng.uniform(-6, 6, 100),
                         [-37.5, -10, -1e-9, 0, 1e-9, 10, 37.5]])
    pts["normcdf"] = [[float(x), float(Phi(x))] for x in xs]
    ps = np.concatenate([np.linspace(0.001, 0.999, 150), rng.uniform(1e-6, 1e-2, 50),
                         1 - rng.uniform(1e-6, 1e-2, 50),
                         [1e-9, 1e-7, 0.5, 1 - 1e-7, 1 - 1e-9, 0.00135, 0.99865]])
    pts["norminv"] = [[float(p), float(stats.norm.ppf(p))] for p in ps]
    xs = np.concatenate([np.linspace(-4, 4, 41), rng.uniform(-3, 3, 160)])
    pts["erf"] = [[float(x), float(special.erf(x))] for x in xs]
    dfs = rng.choice([1, 2, 3, 4, 5, 8, 10, 15, 20, 29, 30, 50, 100, 250, 1000], 260)
    ts = rng.uniform(-6, 6, 260)
    pts["tcdf"] = [[int(df), float(t), float(stats.t.cdf(t, df))] for df, t in zip(dfs, ts)]
    pts["tinv"] = [[int(df), float(p), float(stats.t.ppf(p, df))]
                   for df, p in zip(dfs[:120], rng.uniform(0.001, 0.999, 120))]
    d1s = rng.choice([1, 2, 3, 4, 5, 7, 9, 10, 15, 20, 30, 60, 120], 260)
    d2s = rng.choice([1, 2, 3, 5, 8, 10, 18, 20, 30, 60, 78, 120, 500], 260)
    fs = rng.uniform(0.01, 12, 260)
    pts["fcdf"] = [[int(a), int(b), float(x), float(stats.f.cdf(x, a, b))]
                   for a, b, x in zip(d1s, d2s, fs)]
    pts["finv"] = [[int(a), int(b), float(p), float(stats.f.ppf(p, a, b))]
                   for a, b, p in zip(d1s[:120], d2s[:120], rng.uniform(0.01, 0.999, 120))]
    ks = rng.choice([1, 2, 3, 4, 5, 9, 10, 19, 24, 29, 49, 99, 200], 260)
    cs = np.minimum(rng.uniform(0.01, 300, 260), ks * 4 + 5)
    pts["chi2cdf"] = [[int(k), float(x), float(stats.chi2.cdf(x, k))] for k, x in zip(ks, cs)]
    pts["chi2inv"] = [[int(k), float(p), float(stats.chi2.ppf(p, k))]
                      for k, p in zip(ks[:120], rng.uniform(0.001, 0.999, 120))]
    gs = rng.uniform(0.1, 200, 200)
    pts["lgamma"] = [[float(g), float(special.gammaln(g))] for g in gs]
    with open(os.path.join(RESULTS, "_refpoints.json"), "w") as f:
        json.dump(pts, f)
    print("tables.py:", "ALL CHECKS PASSED" if ok else "CHECK FAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
