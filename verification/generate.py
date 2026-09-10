"""
generate.py - the registry of every dataset in the course.

Each entry writes verification/data/<id>.csv (the data, verbatim as it will be
embedded in the HTML page) and verification/data/<id>.json (the metadata:
kind of analysis, parameters such as specification limits, the source or
the "constructed" label, and any published expected values used as a
known-answer check).

Constructed datasets are generated from a seeded numpy Generator so that the
same values are produced on every run. Textbook check datasets are typed in
from the cited source and flagged source != "constructed".

Kinds handled by compute.py / recompute.py / stats.js:
  capability   x (optional subgroup column); params usl, lsl, target,
               natural_lower/upper, subgroup_size
  imr, xbar_r, xbar_s   variables control charts
  p, np, c, u  attribute charts
  ewma, cusum  time-weighted charts
  grr          crossed gauge R&R, columns part, operator, trial, y
  grr_summary  variance components from a published ANOVA table (no CSV)
  factorial    2^k design, columns run, rep, A, B[, C], y
  ttest2, anova1, paired, ttest1, regression
  samplesize   no CSV; params only
  dpmo, sigma_table, binomial_poisson   no CSV; params only
  descriptive  x; optional usl/lsl (count outside) and log (statistics of ln x)
  subgroup_means  x; params sizes (means of consecutive subgroups, CLT on data)
  vsm          no CSV; params daily_demand_pieces, operating_seconds_per_day,
               steps [{name, ct_s}], inventory [{name, wip_pieces}]
  funnel       column e (noise); params sigma (the true sd used to generate e).
               Rule 1 x=e; Rule 2 x[k]=e[k]-e[k-1]; Rule 3 x[k]=e[k]-x[k-1];
               Rule 4 x[k]=x[k-1]+e[k] (cumulative sum). See Module 2.
  funnel_growth  columns e0..e{R-1}, R independent noise replications of the
               same length; params sigma, checkpoints (drop numbers). Rules
               3 and 4 are random walks, so a single path's window variance
               is too noisy to check against theory; replication gives a
               proper Monte Carlo estimate of Var(x_k) at each checkpoint.
"""
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)

EXAMPLES = []


def register(**kw):
    EXAMPLES.append(kw)


def standardized_normal(seed, n, mean, sd, decimals=None):
    """Seeded normal sample, then shifted and scaled so the sample mean and
    sample standard deviation (n-1) equal `mean` and `sd` exactly (to floating
    point). Used for check examples whose source gives only summary values."""
    rng = np.random.default_rng(seed)
    z = rng.standard_normal(n)
    z = (z - z.mean()) / z.std(ddof=1)
    x = mean + sd * z
    if decimals is not None:
        x = np.round(x, decimals)
    return x


# ---------------------------------------------------------------------------
# Phase B check examples with published answers
# ---------------------------------------------------------------------------
register(
    id="chk-nist-capability", module="B", kind="capability",
    title="NIST 6.1.6 capability example",
    source="S-B1 NIST/SEMATECH e-Handbook 6.1.6 (USL 20, LSL 8, xbar 16, s 2)",
    setting="n = 100 constructed values standardized to xbar = 16, s = 2 exactly",
    params={"usl": 20.0, "lsl": 8.0, "target": 14.0, "subgroup_size": 1},
    columns=["i", "x"],
    rows=[[i + 1, float(v)] for i, v in enumerate(standardized_normal(101, 100, 16.0, 2.0))],
    expected={"overall.mean": [16.0, 1e-9], "overall.s": [2.0, 1e-9],
              "overall.Pp": [1.0, 1e-9], "overall.Ppk": [0.6667, 5e-5],
              "overall.Ppu": [0.6667, 5e-5], "overall.Ppl": [1.3333, 5e-5],
              "overall.k": [0.3333, 5e-5]},
)

register(
    id="chk-nist-imr", module="B", kind="imr",
    title="NIST 6.3.2.2 individuals chart example",
    source="S-B3 NIST/SEMATECH e-Handbook 6.3.2.2 (10 batches of flow rate)",
    setting="textbook data", params={},
    columns=["batch", "x"],
    rows=[[i + 1, v] for i, v in enumerate([49.6, 47.6, 49.9, 51.3, 47.8, 51.2, 52.6, 52.4, 53.6, 52.1])],
    expected={"xbar": [50.81, 1e-9], "mrbar": [1.8778, 5e-5],
              "ucl_x": [55.8041, 5e-5], "lcl_x": [45.8159, 5e-5]},
)

register(
    id="chk-nist-ewma", module="B", kind="ewma",
    title="NIST 6.3.2.4 EWMA chart example",
    source="S-B4 NIST/SEMATECH e-Handbook 6.3.2.4 (20 values, lambda 0.3, EWMA0 50, s 2.0539)",
    setting="textbook data",
    params={"lambda": 0.3, "target": 50.0, "sigma": 2.0539, "L": 3.0, "limits": "asymptotic"},
    columns=["i", "x"],
    rows=[[i + 1, v] for i, v in enumerate([52.0, 47.0, 53.0, 49.3, 50.1, 47.0, 51.0, 50.1, 51.2, 50.5,
                                            49.6, 47.6, 49.9, 51.3, 47.8, 51.2, 52.6, 52.4, 53.6, 52.1])],
    expected={"ucl": [52.5884, 5e-5], "lcl": [47.4115, 1e-4],  # NIST truncates the LCL to 47.4115
              "ewma[0]": [50.60, 5e-3], "ewma[1]": [49.52, 5e-3], "ewma[19]": [51.99, 5e-3],
              "ewma[18]": [51.94, 5e-3]},
)

register(
    id="chk-nist-samplesize", module="B", kind="samplesize",
    title="NIST 7.2.2.2 sample size example",
    source="S-B8 NIST/SEMATECH e-Handbook 7.2.2.2 (one-sided, alpha 0.05, beta 0.10, delta = sigma)",
    setting="parameters only",
    params={"alpha": 0.05, "beta": 0.10, "delta": 1.0, "sigma": 1.0, "sides": 1, "design": "one-sample"},
    columns=None, rows=None,
    expected={"n_z_exact": [8.567, 4e-3], "n_z": [9, 0], "n_t": [11, 0]},  # NIST uses z rounded to 1.645 and 1.282 (8.567); exact z gives 8.564
)

register(
    id="chk-aiagvda-onesided-a", module="B", kind="capability",
    title="AIAG & VDA SPC Manual Fig. 7-6, location near natural limit",
    source="S-A2 AIAG & VDA SPC Manual (2026) p. 48: xbar 0.166, s 0.0457, Cp* 1.46, Cpk 1.71 "
           "(upper limit inferred as 0.40 mm, natural lower limit 0)",
    setting="n = 100 constructed values standardized to xbar = 0.166 mm, s = 0.0457 mm",
    params={"usl": 0.40, "lsl": None, "natural_lower": 0.0, "subgroup_size": 1, "units": "mm"},
    columns=["i", "x"],
    rows=[[i + 1, float(v)] for i, v in enumerate(standardized_normal(102, 100, 0.166, 0.0457))],
    expected={"overall.Ppk": [1.71, 5e-3], "overall.Pp_natural": [1.46, 5e-3]},
)

register(
    id="chk-aiagvda-onesided-b", module="B", kind="capability",
    title="AIAG & VDA SPC Manual Fig. 7-6, location near the tolerance limit",
    source="S-A2 AIAG & VDA SPC Manual (2026) p. 48: xbar 0.250, s 0.0292, Cp* 2.28, Cpk 1.71",
    setting="n = 100 constructed values standardized to xbar = 0.250 mm, s = 0.0292 mm",
    params={"usl": 0.40, "lsl": None, "natural_lower": 0.0, "subgroup_size": 1, "units": "mm"},
    columns=["i", "x"],
    rows=[[i + 1, float(v)] for i, v in enumerate(standardized_normal(103, 100, 0.250, 0.0292))],
    expected={"overall.Ppk": [1.71, 5e-3], "overall.Pp_natural": [2.28, 5e-3]},
)

# Montgomery, Design and Analysis of Experiments, plasma etch 2^3 example
# (secondary: reproduced with data, effects and ANOVA in the University of
# Washington STAT 502 lecture notes, "The 2^k Factorial Design").
_etch = {"(1)": (550, 604), "a": (669, 650), "b": (633, 601), "ab": (642, 635),
         "c": (1037, 1052), "ac": (749, 868), "bc": (1075, 1063), "abc": (729, 860)}
_rows = []
_run = 0
for label, ys in _etch.items():
    A = 1 if "a" in label else -1
    B = 1 if "b" in label else -1
    C = 1 if "c" in label else -1
    for rep, y in enumerate(ys, start=1):
        _run += 1
        _rows.append([_run, rep, A, B, C, y])
register(
    id="chk-montgomery-etch", module="B", kind="factorial",
    title="Montgomery plasma etch 2^3 factorial, 2 replicates",
    source="Montgomery, Design and Analysis of Experiments, plasma etch example; data and "
           "effects as reproduced in UW STAT 502 lecture notes (secondary)",
    setting="A gap, B gas flow, C power; response etch rate (angstrom/min)",
    params={"k": 3, "replicates": 2, "factors": ["A", "B", "C"]},
    columns=["run", "rep", "A", "B", "C", "y"], rows=_rows,
    expected={"effects.A": [-101.625, 1e-9], "effects.B": [7.375, 1e-9], "effects.C": [306.125, 1e-9],
              "effects.AB": [-24.875, 1e-9], "effects.AC": [-153.625, 1e-9], "effects.BC": [-2.125, 1e-9],
              "effects.ABC": [5.625, 1e-9], "anova.A.ss": [41311, 0.5], "anova.C.ss": [374850, 0.5],
              "anova.AC.ss": [94403, 0.5], "anova.residual.ss": [18020, 0.5], "anova.residual.df": [8, 0],
              "anova.A.F": [18.34, 5e-3], "anova.C.F": [166.41, 5e-3], "anova.AC.F": [41.91, 5e-3],
              "anova.A.p": [0.0026786, 5e-7], "anova.C.p": [1.233e-06, 5e-10], "anova.AC.p": [0.0001934, 5e-8],
              "residual_sd": [47.46, 5e-3], "r2": [0.9661, 5e-5]},
)

register(
    id="chk-minitab-grr-anova", module="B", kind="grr_summary",
    title="Minitab crossed gauge R&R example, from the published ANOVA table",
    source="Minitab Statistical Software help, 'Example of Crossed Gage R&R Study' (10 parts, 3 operators, "
           "3 replicates, tolerance 8); ANOVA table as published",
    setting="published mean squares; the raw data file is not reproduced on the page",
    params={"parts": 10, "operators": 3, "replicates": 3, "tolerance": 8.0, "study_var_k": 6.0,
            "alpha_remove": 0.05,
            "ms_full": {"part": 9.81799, "operator": 1.58363, "interaction": 0.01994, "repeatability": 0.04598},
            "df_full": {"part": 9, "operator": 2, "interaction": 18, "repeatability": 60},
            "ms_reduced": {"part": 9.81799, "operator": 1.58363, "repeatability": 0.03997},
            "df_reduced": {"part": 9, "operator": 2, "repeatability": 78}},
    columns=None, rows=None,
    expected={"interaction_p": [0.974, 5e-4], "interaction_F": [0.434, 5e-4],
              "varcomp.grr": [0.09143, 5e-6], "varcomp.repeatability": [0.03997, 5e-6],
              "varcomp.reproducibility": [0.05146, 5e-6], "varcomp.part": [1.08645, 5e-6],
              "varcomp.total": [1.17788, 1e-5],  # Minitab prints the sum of rounded components
              "pct_contribution.grr": [7.76, 5e-3], "pct_contribution.part": [92.24, 5e-3],
              "sd.grr": [0.30237, 5e-6], "sd.part": [1.04233, 5e-6], "sd.total": [1.08530, 5e-6],
              "pct_study_var.grr": [27.86, 5e-3], "pct_study_var.repeatability": [18.42, 5e-3],
              "pct_study_var.reproducibility": [20.90, 5e-3], "pct_study_var.part": [96.04, 5e-3],
              "pct_tolerance.grr": [22.68, 5e-3], "pct_tolerance.part": [78.17, 5e-3],
              "ndc": [4, 0]},
)

# ---------------------------------------------------------------------------
# Harness-only constructed datasets (prefix hb-): no published answer; they
# prove that compute.py, recompute.py and stats.js agree on every route.
# They are NOT course examples and do not appear on any page.
# ---------------------------------------------------------------------------
rng = np.random.default_rng(20260909)

# Bore diameter, 25 subgroups of 5, shift after subgroup 18 (tool change)
_sub = []
for g in range(1, 26):
    mu = 12.004 if g <= 18 else 12.012
    for _ in range(5):
        _sub.append([g, round(float(rng.normal(mu, 0.0065)), 3)])
register(id="hb-xbar-r", module="B", kind="capability",
         title="harness: bore diameter, 25 x 5, shift at subgroup 19",
         source="constructed", setting="bore 12.000 +/- 0.025 mm, micrometer to 0.001 mm",
         params={"usl": 12.025, "lsl": 11.975, "target": 12.000, "subgroup_size": 5, "chart": "xbar_r", "units": "mm"},
         columns=["subgroup", "x"], rows=_sub)
register(id="hb-xbar-s", module="B", kind="capability",
         title="harness: same data with an Xbar-S chart and Sbar/c4 sigma",
         source="constructed", setting="as hb-xbar-r",
         params={"usl": 12.025, "lsl": 11.975, "target": 12.000, "subgroup_size": 5, "chart": "xbar_s", "units": "mm"},
         columns=["subgroup", "x"], rows=_sub)

# Fill weight, individuals, 40 values, one outlier
_fw = [round(float(v), 1) for v in rng.normal(250.6, 1.1, 40)]
_fw[27] = 255.4
register(id="hb-imr", module="B", kind="capability",
         title="harness: fill weight I-MR with one special cause",
         source="constructed", setting="fill weight 250 g nominal, spec 248 to 254 g, scale to 0.1 g",
         params={"usl": 254.0, "lsl": 248.0, "target": 250.0, "subgroup_size": 1, "chart": "imr", "units": "g"},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_fw)])

# Attribute charts
_pn = [[i + 1, int(n), int(rng.binomial(n, 0.045))] for i, n in enumerate(rng.integers(180, 240, 25))]
register(id="hb-p", module="B", kind="p", title="harness: p chart, variable n", source="constructed",
         setting="leak-test rejects per shift", params={}, columns=["sample", "n", "defectives"], rows=_pn)
register(id="hb-np", module="B", kind="np", title="harness: np chart, n = 200", source="constructed",
         setting="rejects in fixed samples of 200", params={"n": 200},
         columns=["sample", "defectives"], rows=[[i + 1, int(rng.binomial(200, 0.04))] for i in range(25)])
register(id="hb-c", module="B", kind="c", title="harness: c chart", source="constructed",
         setting="solder defects per board", params={},
         columns=["sample", "defects"], rows=[[i + 1, int(rng.poisson(6.3))] for i in range(30)])
_un = rng.integers(8, 15, 25)
register(id="hb-u", module="B", kind="u", title="harness: u chart, variable n", source="constructed",
         setting="defects per unit, batches of 8 to 14 units", params={},
         columns=["sample", "n", "defects"], rows=[[i + 1, int(n), int(rng.poisson(1.4 * n))] for i, n in enumerate(_un)])

# EWMA and CUSUM on the same individuals series with a 1-sigma shift at 21
_ts = [round(float(v), 2) for v in np.concatenate([rng.normal(20.0, 0.5, 20), rng.normal(20.5, 0.5, 20)])]
register(id="hb-ewma", module="B", kind="ewma", title="harness: EWMA, lambda 0.2, exact limits", source="constructed",
         setting="cycle time s", params={"lambda": 0.2, "L": 2.7, "limits": "exact", "baseline": 20},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_ts)])
register(id="hb-cusum", module="B", kind="cusum", title="harness: tabular CUSUM, k 0.5, h 4", source="constructed",
         setting="cycle time s", params={"k": 0.5, "h": 4.0, "baseline": 20},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_ts)])

# Crossed gauge R&R, 10 parts x 3 operators x 3 trials
_parts = np.linspace(11.980, 12.020, 10) + rng.normal(0, 0.002, 10)
_opbias = [0.0, 0.0025, -0.0015]
_grr = []
for p in range(10):
    for o in range(3):
        for t in range(3):
            y = _parts[p] + _opbias[o] + rng.normal(0, 0.0022)
            _grr.append([p + 1, "ABC"[o], t + 1, round(float(y), 3)])
register(id="hb-grr", module="B", kind="grr", title="harness: crossed gauge R&R, 10 x 3 x 3", source="constructed",
         setting="bore diameter, tolerance 0.050 mm", params={"tolerance": 0.050, "study_var_k": 6.0, "alpha_remove": 0.05},
         columns=["part", "operator", "trial", "y"], rows=_grr)

# 2^2 factorial with 3 replicates
_f2 = []
_r = 0
for (A, B) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
    for rep in range(1, 4):
        _r += 1
        y = 42 + 3.0 * A - 1.5 * B + 2.2 * A * B + rng.normal(0, 1.2)
        _f2.append([_r, rep, A, B, round(float(y), 2)])
register(id="hb-factorial-2", module="B", kind="factorial", title="harness: 2^2, 3 replicates", source="constructed",
         setting="pull strength N", params={"k": 2, "replicates": 3, "factors": ["A", "B"]},
         columns=["run", "rep", "A", "B", "y"], rows=_f2)

# Two-sample t, one-way ANOVA, paired t, one-sample t, regression
_g1 = [round(float(v), 1) for v in rng.normal(48.2, 2.1, 15)]
_g2 = [round(float(v), 1) for v in rng.normal(49.9, 2.6, 18)]
register(id="hb-ttest2", module="B", kind="ttest2", title="harness: two-sample t", source="constructed",
         setting="pull strength N, two fixtures", params={"alpha": 0.05, "mu0_diff": 0.0},
         columns=["group", "x"], rows=[["A", v] for v in _g1] + [["B", v] for v in _g2])
_an = []
for g, mu in zip(["M1", "M2", "M3", "M4"], [3.10, 3.18, 3.05, 3.26]):
    for v in rng.normal(mu, 0.09, 8):
        _an.append([g, round(float(v), 2)])
register(id="hb-anova1", module="B", kind="anova1", title="harness: one-way ANOVA, 4 machines", source="constructed",
         setting="cycle time s", params={"alpha": 0.05}, columns=["group", "x"], rows=_an)
_b = rng.normal(0.62, 0.05, 12)
_a = _b - 0.03 + rng.normal(0, 0.02, 12)
register(id="hb-paired", module="B", kind="paired", title="harness: paired t, before/after", source="constructed",
         setting="flatness mm before and after fixture change", params={"alpha": 0.05},
         columns=["pair", "before", "after"], rows=[[i + 1, round(float(x), 3), round(float(y), 3)] for i, (x, y) in enumerate(zip(_b, _a))])
register(id="hb-ttest1", module="B", kind="ttest1", title="harness: one-sample t vs target", source="constructed",
         setting="fill weight g vs 250.0", params={"mu0": 250.0, "alpha": 0.05},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_fw)])
_x = np.round(rng.uniform(180, 240, 20), 0)
_y = np.round(1.8 + 0.0125 * _x + rng.normal(0, 0.12, 20), 2)
register(id="hb-regression", module="B", kind="regression", title="harness: simple linear regression", source="constructed",
         setting="pull strength N vs solder temperature degC", params={"alpha": 0.05},
         columns=["x", "y"], rows=[[float(a), float(b)] for a, b in zip(_x, _y)])
register(id="hb-samplesize-2", module="B", kind="samplesize", title="harness: two-sample t sample size", source="constructed",
         setting="delta 1.5, sigma 2.0, alpha 0.05 two-sided, power 0.9",
         params={"alpha": 0.05, "beta": 0.10, "delta": 1.5, "sigma": 2.0, "sides": 2, "design": "two-sample"},
         columns=None, rows=None)


# ---------------------------------------------------------------------------
# Module 7: Process capability I (constructed course examples, prefix m07-)
# Seeds were chosen so that each dataset has the property the text teaches;
# the data are otherwise ordinary seeded normal samples rounded to the gauge.
# ---------------------------------------------------------------------------
def _m07_bore():
    # Bore Ø12.000 ± 0.025 mm, 25 subgroups of 5, micrometer to 0.001 mm.
    # Slightly above nominal, small subgroup-to-subgroup drift (fixture
    # warm-up) so that overall s is a little larger than Rbar/d2.
    rng = np.random.default_rng(26)
    rows = []
    for g in range(1, 26):
        mu = 12.0035 + rng.normal(0, 0.0018)
        for _ in range(5):
            rows.append([g, round(float(rng.normal(mu, 0.0060)), 3)])
    return rows

_m07b = _m07_bore()
_P_BORE = {"usl": 12.025, "lsl": 11.975, "target": 12.000, "subgroup_size": 5, "chart": "xbar_r", "units": "mm"}
register(id="m07-bore", module="07", kind="capability",
         title="Bore diameter, 25 subgroups of 5, stable, Cpk about 1.1",
         source="constructed", setting="reamed bore Ø12.000 ± 0.025 mm in an aluminium housing, bore micrometer to 0.001 mm, 5 consecutive parts every 30 min",
         params=dict(_P_BORE), columns=["subgroup", "x"], rows=_m07b)
register(id="m07-bore-30", module="07", kind="capability",
         title="The first 6 subgroups (30 values) of m07-bore, for the confidence-interval point",
         source="constructed", setting="first 30 values of m07-bore",
         params=dict(_P_BORE), columns=["subgroup", "x"], rows=_m07b[:30])

# Fill weight with a one-sided lower specification (declared minimum 250.0 g),
# 100 consecutive containers, scale to 0.1 g. Ppl about 0.75.
_rng = np.random.default_rng(121)
register(id="m07-fill", module="07", kind="capability",
         title="Fill weight, lower specification only, 100 individuals",
         source="constructed", setting="powder fill, declared minimum 250.0 g, checkweigher to 0.1 g, 100 consecutive containers",
         params={"usl": None, "lsl": 250.0, "target": None, "subgroup_size": 1, "chart": "imr", "units": "g"},
         columns=["i", "x"], rows=[[i + 1, round(float(v), 1)] for i, v in enumerate(_rng.normal(251.9, 0.85, 100))])

# Shoulder length, off target but well inside the tolerance: Cpk looks fine,
# Cpm does not. 50 individuals from a CMM, to 0.001 mm.
_rng = np.random.default_rng(217)
register(id="m07-cpm", module="07", kind="capability",
         title="Shoulder length off target, Cpk 1.4 but Cpm 0.76",
         source="constructed", setting="turned shoulder length 25.000 ± 0.030 mm, CMM to 0.001 mm, 50 consecutive parts",
         params={"usl": 25.030, "lsl": 24.970, "target": 25.000, "subgroup_size": 1, "chart": "imr", "units": "mm"},
         columns=["i", "x"], rows=[[i + 1, round(float(v), 3)] for i, v in enumerate(_rng.normal(25.013, 0.0042, 50))])

# Exercise 1: keyway width with a unilateral tolerance 6.000 +0.030/0 mm,
# 20 subgroups of 4, stable, Cpk just under 1.
_rng = np.random.default_rng(314)
_kw = []
for g in range(1, 21):
    for _ in range(4):
        _kw.append([g, round(float(_rng.normal(6.017, 0.0045)), 3)])
register(id="m07-ex1-keyway", module="07", kind="capability",
         title="Exercise 1: keyway width, unilateral tolerance, 20 subgroups of 4",
         source="constructed", setting="milled keyway width 6.000 +0.030/0 mm (target at mid-tolerance 6.015), gauge to 0.001 mm",
         params={"usl": 6.030, "lsl": 6.000, "target": 6.015, "subgroup_size": 4, "chart": "xbar_r", "units": "mm"},
         columns=["subgroup", "x"], rows=_kw)

# Exercise 2: die-cast wall thickness, 30 subgroups of 3, a shift after
# subgroup 20 (die temperature drifted). Not stable: Cwk looks good, Ppk does not.
_rng = np.random.default_rng(417)
_wt = []
for g in range(1, 31):
    mu = 2.505 if g <= 20 else 2.565
    for _ in range(3):
        _wt.append([g, round(float(_rng.normal(mu, 0.028)), 2)])
register(id="m07-ex2-wall", module="07", kind="capability",
         title="Exercise 2: die-cast wall thickness with a shift at subgroup 21",
         source="constructed", setting="die-cast housing wall 2.50 ± 0.15 mm, ultrasonic gauge to 0.01 mm, 3 parts per shot",
         params={"usl": 2.65, "lsl": 2.35, "target": 2.50, "subgroup_size": 3, "chart": "xbar_r", "units": "mm"},
         columns=["subgroup", "x"], rows=_wt)


# ---------------------------------------------------------------------------
# Datasets registered in Phase C so that calculators.html has verified
# preloaded data for the gauge R&R and hypothesis-test calculators. They are
# the planned examples of Modules 4 and 11 (SOURCES.md Part 2) and will be
# taught there; until then they appear only on calculators.html.
# ---------------------------------------------------------------------------
_rng = np.random.default_rng(500)
_parts = np.linspace(11.984, 12.016, 10) + _rng.normal(0, 0.0015, 10)
_opbias = [0.0, 0.0018, -0.0012]
_g4 = []
for p in range(10):
    for o in range(3):
        for t in range(3):
            _g4.append([p + 1, "ABC"[o], t + 1, round(float(_parts[p] + _opbias[o] + _rng.normal(0, 0.0021)), 3)])
register(id="m04-grr-bore", module="04", kind="grr",
         title="Crossed gauge R&R on the bore gauge, 10 parts x 3 operators x 3 trials, %GRR about 24 %",
         source="constructed", setting="bore gauge for Ø12.000 ± 0.025 mm (tolerance 0.050 mm), 10 parts spanning the tolerance, 3 operators, 3 trials each, randomised order",
         params={"tolerance": 0.050, "study_var_k": 6.0, "alpha_remove": 0.05, "units": "mm"},
         columns=["part", "operator", "trial", "y"], rows=_g4)

_rng = np.random.default_rng(603)
_ta = [round(float(v), 1) for v in _rng.normal(46.5, 2.4, 12)]
_tb = [round(float(v), 1) for v in _rng.normal(48.9, 2.9, 12)]
register(id="m11-ttest2-pull", module="11", kind="ttest2",
         title="Solder joint pull strength from two suppliers, two-sample t",
         source="constructed", setting="pull strength in N of a soldered terminal, 12 joints from supplier A and 12 from supplier B, tester to 0.1 N",
         params={"alpha": 0.05, "mu0_diff": 0.0, "units": "N"},
         columns=["group", "x"], rows=[["A", v] for v in _ta] + [["B", v] for v in _tb])

_rng = np.random.default_rng(700)
_am = []
for g, mu in zip(["M1", "M2", "M3"], [42.0, 42.3, 43.1]):
    for v in _rng.normal(mu, 0.9, 10):
        _am.append([g, round(float(v), 1)])
register(id="m11-anova-machines", module="11", kind="anova1",
         title="Cycle time on three machines, one-way ANOVA",
         source="constructed", setting="cycle time in s of the same operation on three nominally identical machines, 10 cycles each",
         params={"alpha": 0.05, "units": "s"}, columns=["group", "x"], rows=_am)


# ---------------------------------------------------------------------------
# Module 0: Introduction (constructed course examples, prefix m00-)
# ---------------------------------------------------------------------------
register(id="m00-sigma-table", module="00", kind="sigma_table",
         title="Sigma level to PPM, centred and with the 1.5 sigma shift",
         source="arithmetic on the normal distribution; the shift is the Motorola convention (S-E8, S-D28), critiqued in S-C9 and S-E28",
         setting="parameters only",
         params={"levels": [1, 2, 3, 4, 4.5, 5, 6], "shift": 1.5, "ppm_targets": [3.4, 100, 1000, 10000, 100000]},
         columns=None, rows=None,
         expected={"ppm_shifted_one_sided.6": [3.4, 0.01]})  # Motorola's stated target (S-E8)

# A drilled hole in a bracket, Ø8.000 ± 0.050 mm, 100 consecutive parts,
# bore gauge to 0.001 mm; running large with about 5 % out of tolerance, so
# that the histogram against the specification shows a visible tail.
_rng = np.random.default_rng(37)
register(id="m00-bore-preview", module="00", kind="capability",
         title="Drilled hole, 100 individuals, about 5 % out of tolerance",
         source="constructed", setting="drilled hole Ø8.000 ± 0.050 mm in a steel bracket, bore gauge to 0.001 mm, 100 consecutive parts",
         params={"usl": 8.050, "lsl": 7.950, "target": 8.000, "subgroup_size": 1, "chart": "imr", "units": "mm"},
         columns=["i", "x"], rows=[[i + 1, round(float(v), 3)] for i, v in enumerate(_rng.normal(8.016, 0.021, 100))])

# Leak-test rejects on brazed assemblies: the same 23 failures counted with
# one opportunity per assembly, then with the six braze joints as opportunities.
for _opp in (1, 6):
    register(id=f"m00-dpmo-leak-{_opp}", module="00", kind="dpmo",
             title=f"Leak-test failures, {_opp} opportunit{'y' if _opp == 1 else 'ies'} per assembly",
             source="constructed", setting="brazed heat-exchanger assemblies, 1,250 tested in a week, 23 failed the leak test",
             params={"defects": 23, "units": 1250, "opportunities": _opp}, columns=None, rows=None)

# Exercise 1: solder-joint defects on assembled boards.
register(id="m00-ex1-dpmo", module="00", kind="dpmo",
         title="Solder-joint defects, 4,800 boards of 120 joints",
         source="constructed", setting="4,800 boards inspected by AOI, 120 solder joints each, 331 joint defects logged",
         params={"defects": 331, "units": 4800, "opportunities": 120}, columns=None, rows=None)

# Exercise 2: solder-joint pull strength with a minimum of 8.0 N, 60 joints,
# pull tester to 0.01 N.
_rng = np.random.default_rng(23)
register(id="m00-ex2-pull", module="00", kind="capability",
         title="Pull strength, minimum 8.0 N, 60 individuals",
         source="constructed", setting="wire-bond pull strength, minimum 8.0 N, pull tester to 0.01 N, 60 consecutive joints",
         params={"usl": None, "lsl": 8.0, "target": None, "subgroup_size": 1, "chart": "imr", "units": "N"},
         columns=["i", "x"], rows=[[i + 1, round(float(v), 2)] for i, v in enumerate(_rng.normal(9.25, 0.55, 60))])


# ---------------------------------------------------------------------------
# Module 1: Variation and basic statistics (prefix m01-)
# ---------------------------------------------------------------------------
# Ground shaft Ø8.000 ± 0.015 mm, 60 consecutive parts, micrometer to 0.001 mm:
# an ordinary, close-to-normal sample for mean, median, s and the histogram.
_rng = np.random.default_rng(21)
_shaft = [[i + 1, round(float(v), 3)] for i, v in enumerate(_rng.normal(8.002, 0.0045, 60))]
register(id="m01-shaft", module="01", kind="descriptive",
         title="Shaft diameter, 60 individuals, descriptive statistics",
         source="constructed", setting="ground shaft Ø8.000 ± 0.015 mm, micrometer to 0.001 mm, 60 consecutive parts",
         params={"usl": 8.015, "lsl": 7.985, "units": "mm"}, columns=["i", "x"], rows=_shaft)
register(id="m01-shaft-means", module="01", kind="subgroup_means",
         title="Means of consecutive subgroups of 5 from m01-shaft (exercise 2)",
         source="constructed", setting="the m01-shaft values in subgroups of 5 consecutive parts",
         params={"sizes": [5]}, columns=["i", "x"], rows=_shaft)

# Flatness of a milled face in µm, 200 consecutive parts, CMM to 0.1 µm. A
# lognormal characteristic: bounded at zero, right-skewed; ln(x) is normal.
_rng = np.random.default_rng(10)
_flat = [[i + 1, round(float(v), 1)] for i, v in enumerate(np.exp(_rng.normal(np.log(8.0), 0.45, 200)))]
register(id="m01-flatness", module="01", kind="descriptive",
         title="Flatness, 200 individuals, right-skewed (lognormal) with log statistics",
         source="constructed", setting="flatness of a milled face, µm, CMM to 0.1 µm, 200 consecutive parts; no upper limit given here",
         params={"log": True, "units": "µm"}, columns=["i", "x"], rows=_flat)
register(id="m01-flatness-means", module="01", kind="subgroup_means",
         title="Means of consecutive subgroups of 2, 5 and 10 from m01-flatness (central limit theorem on data)",
         source="constructed", setting="the m01-flatness values in consecutive subgroups",
         params={"sizes": [2, 5, 10]}, columns=["i", "x"], rows=_flat)

# Binomial and Poisson: a lot 2 % defective sampled 50 at a time; solder defects
# per board averaging 1.5.
register(id="m01-binomial", module="01", kind="binomial_poisson",
         title="Binomial (n 50, p 0.02) and Poisson (lambda 1.5) probabilities for k = 0 to 5",
         source="arithmetic on the binomial and Poisson distributions (NIST 1.3.6.6.18 and 1.3.6.6.19)",
         setting="parameters only", params={"n": 50, "p": 0.02, "lambda": 1.5, "k": [0, 1, 2, 3, 4, 5]},
         columns=None, rows=None)

# Exercise 1: tightening torque, 30 readings, torque analyser to 0.01 N·m.
_rng = np.random.default_rng(2)
register(id="m01-ex1-torque", module="01", kind="descriptive",
         title="Tightening torque, 30 individuals (exercise 1)",
         source="constructed", setting="tightening torque of a bolted joint, 12.0 ± 1.0 N·m, torque analyser to 0.01 N·m, 30 consecutive joints",
         params={"usl": 13.0, "lsl": 11.0, "units": "N·m"},
         columns=["i", "x"], rows=[[i + 1, round(float(v), 2)] for i, v in enumerate(_rng.normal(12.15, 0.28, 30))])

# Anscombe's quartet (real data, S-C28), typed from the tables reproduced in
# S-E35 and S-E36; the published shared properties are the known-answer check.
_ANS_X = [10.0, 8.0, 13.0, 9.0, 11.0, 14.0, 6.0, 4.0, 12.0, 7.0, 5.0]
_ANS = {
    1: (_ANS_X, [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]),
    2: (_ANS_X, [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]),
    3: (_ANS_X, [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]),
    4: ([8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 19.0, 8.0, 8.0, 8.0], [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]),
}
for _i, (_ax, _ay) in _ANS.items():
    register(id=f"m01-anscombe-{_i}", module="01", kind="regression",
             title=f"Anscombe's quartet, data set {_i} (real data)",
             source="S-C28 Anscombe 1973, The American Statistician 27(1):17-21; values as reproduced in S-E35 (Wikipedia) and the properties as stated in S-E36 (R datasets)",
             setting="published data, no units", params={"alpha": 0.05},
             columns=["x", "y"], rows=[[a, b] for a, b in zip(_ax, _ay)],
             expected={"mean_x": [9.0, 1e-9], "mean_y": [7.50, 5e-3], "slope": [0.500, 5e-4], "intercept": [3.00, 5e-3], "r": [0.816, 1e-3], "r2": [0.67, 5e-3]})


# ---------------------------------------------------------------------------
# Module 2: Process thinking (prefix m02-)
# ---------------------------------------------------------------------------
# Red bead experiment (S-E4): the theoretical distribution for a paddle of
# 50 holes drawn from a mix that is 20 % red. The Poisson side of the kind is
# not used on the page; a placeholder lambda is supplied so the shared
# binomial_poisson function runs.
register(id="m02-redbead-theory", module="02", kind="binomial_poisson",
         title="Red bead paddle: Binomial(n=50, p=0.20), k = 0 to 20",
         source="arithmetic on the binomial distribution for the course's version of the red bead exercise (S-E4)",
         setting="parameters only", params={"n": 50, "p": 0.20, "lambda": 10.0, "k": list(range(0, 21))},
         columns=None, rows=None)

# A simulated run: 5 willing workers, 4 rounds, one paddle draw (50 beads,
# 20 % red) each. The exact box size and headcount in Deming's own sessions
# are not documented on the verified source page (S-E4); these are the
# course's constructed parameters for a common version of the exercise.
_rng = np.random.default_rng(42)
_redbead_days = [[i + 1, int(v)] for i, v in enumerate(_rng.binomial(50, 0.20, 20))]
register(id="m02-redbead-days", module="02", kind="descriptive",
         title="Red bead exercise, 20 simulated paddle draws (5 workers x 4 rounds)",
         source="constructed simulation of the exercise described in S-E4, Binomial(n=50, p=0.20)",
         setting="a paddle of 50 holes dipped into a mix of 20 % red beads, one draw per worker per round",
         params={"units": "red beads per draw"}, columns=["i", "x"], rows=_redbead_days)

# Value stream map, a small machining cell (constructed, no employer detail).
register(id="m02-vsm-machining", module="02", kind="vsm",
         title="Current-state value stream map, machined bracket cell",
         source="constructed", setting="a 4-step machining cell (turn, mill, deburr, inspect and pack) making one bracket part number, one shift",
         params={"daily_demand_pieces": 400, "operating_seconds_per_day": 27000,
                 "steps": [{"name": "Turn", "ct_s": 45.0}, {"name": "Mill", "ct_s": 60.0},
                           {"name": "Deburr", "ct_s": 30.0}, {"name": "Inspect & pack", "ct_s": 20.0}],
                 "inventory": [{"name": "Raw material", "wip_pieces": 800.0},
                               {"name": "WIP: turn to mill", "wip_pieces": 150.0},
                               {"name": "WIP: mill to deburr", "wip_pieces": 200.0},
                               {"name": "WIP: deburr to inspect", "wip_pieces": 100.0},
                               {"name": "Finished goods", "wip_pieces": 300.0}]},
         columns=None, rows=None)

# Exercise 1: a second, smaller cell (assembly and test), different numbers.
register(id="m02-ex1-vsm", module="02", kind="vsm",
         title="Current-state value stream map, sub-assembly and test cell (exercise 1)",
         source="constructed", setting="a 3-step assembly cell (sub-assembly, final assembly, function test), one shift",
         params={"daily_demand_pieces": 600, "operating_seconds_per_day": 25200,
                 "steps": [{"name": "Sub-assembly", "ct_s": 25.0}, {"name": "Final assembly", "ct_s": 35.0},
                           {"name": "Function test", "ct_s": 18.0}],
                 "inventory": [{"name": "Component kits", "wip_pieces": 500.0},
                               {"name": "WIP: sub-assembly to final", "wip_pieces": 120.0},
                               {"name": "WIP: final to test", "wip_pieces": 80.0},
                               {"name": "Finished goods", "wip_pieces": 250.0}]},
         columns=None, rows=None)

# The funnel experiment (S-D10 p. 327 via S-E21): four rules simulated from
# the same noise sequence, marble position in mm from the target.
_rng = np.random.default_rng(7)
_e100 = [round(float(v), 3) for v in _rng.normal(0.0, 5.0, 100)]
register(id="m02-funnel", module="02", kind="funnel",
         title="Funnel experiment simulation, 100 drops, sigma = 5.0 mm",
         source="constructed simulation of the four rules described in S-D10 (p. 327) and S-E21",
         setting="a marble dropped through a funnel onto a paper target, position recorded in mm from the target on one axis",
         params={"sigma": 5.0}, columns=["i", "e"], rows=[[i + 1, v] for i, v in enumerate(_e100)])

# The same experiment, backed by 150 independent replications of 40 drops,
# to estimate Var(x_k) at drop 8 and drop 40 for each rule without the noise
# of reading a growth rate off a single random-walk path (see funnel_growth
# above). The first replication is reused as the illustrative single path.
_R, _NFG = 150, 40
_rng = np.random.default_rng(7)
_grid = _rng.normal(0.0, 5.0, (_NFG, _R))
register(id="m02-funnel-growth", module="02", kind="funnel_growth",
         title=f"Funnel experiment, {_R} independent replications of {_NFG} drops, sigma = 5.0 mm",
         source="constructed simulation of the four rules described in S-D10 (p. 327) and S-E21",
         setting="150 independent repeats of the same funnel simulation, 40 drops each, to estimate the variance of each rule at a given drop number",
         params={"sigma": 5.0, "checkpoints": [8, 40]},
         columns=["drop"] + [f"e{r}" for r in range(_R)],
         rows=[[i + 1] + [round(float(_grid[i, r]), 4) for r in range(_R)] for i in range(_NFG)])

# Exercise 2: a shorter run, rules 1 and 2 only asked for.
_rng = np.random.default_rng(19)
_e30 = [round(float(v), 3) for v in _rng.normal(0.0, 4.0, 30)]
register(id="m02-ex2-funnel", module="02", kind="funnel",
         title="Funnel experiment simulation, 30 drops, sigma = 4.0 mm (exercise 2)",
         source="constructed simulation of the four rules described in S-D10 (p. 327) and S-E21",
         setting="a marble dropped through a funnel onto a paper target, position recorded in mm from the target on one axis",
         params={"sigma": 4.0}, columns=["i", "e"], rows=[[i + 1, v] for i, v in enumerate(_e30)])


def main():
    for ex in EXAMPLES:
        meta = {k: v for k, v in ex.items() if k not in ("rows",)}
        if ex["rows"] is not None:
            with open(os.path.join(DATA, ex["id"] + ".csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(ex["columns"])
                for r in ex["rows"]:
                    w.writerow([repr(v) if isinstance(v, float) else v for v in r])
            meta["n_rows"] = len(ex["rows"])
        with open(os.path.join(DATA, ex["id"] + ".json"), "w") as f:
            json.dump(meta, f, indent=1)
    ids = [e["id"] for e in EXAMPLES]
    assert len(ids) == len(set(ids)), "duplicate example id"
    print(f"generate.py: wrote {len(EXAMPLES)} examples to {DATA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
