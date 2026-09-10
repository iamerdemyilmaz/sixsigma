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


# ---------------------------------------------------------------------------
# Module 3: Defining a project (prefix m03-)
# ---------------------------------------------------------------------------
# The capstone's own baseline: 42 of 1,000 brazed assemblies fail the leak
# test (4.2 %), the figure Module 19 states as the capstone's starting point.
# The charter's goal state, 1 % or fewer, registered the same way.
register(id="m03-charter-leak", module="03", kind="dpmo",
         title="Charter baseline: leak-test reject rate, 1,000 brazed assemblies",
         source="constructed (matches the capstone baseline stated in SOURCES.md Module 19)",
         setting="brazed aluminium heat-exchanger cores, leak-tested at final inspection, 1 opportunity per assembly",
         params={"defects": 42, "units": 1000, "opportunities": 1}, columns=None, rows=None)
register(id="m03-charter-goal", module="03", kind="dpmo",
         title="Charter goal: leak-test reject rate at or below 1 %",
         source="constructed", setting="same line, the charter's stated goal state",
         params={"defects": 10, "units": 1000, "opportunities": 1}, columns=None, rows=None)


# ---------------------------------------------------------------------------
# Module 8: Process capability II (prefix m08-)
# ---------------------------------------------------------------------------
# A turned shaft journal whose mean creeps upward through the study (tool
# wear): every subgroup is tight, the X-bar chart is not stable, and the
# within-sigma index looks fine while the overall index does not.
_rng = np.random.default_rng(2)
_dr = []
for g in range(1, 26):
    mu = 19.996 + 0.014 * (g - 1) / 24
    for _ in range(5):
        _dr.append([g, round(float(_rng.normal(mu, 0.004)), 3)])
register(id="m08-drift", module="08", kind="capability",
         title="Shaft journal with tool-wear drift, 25 x 5: Cwk 1.37 but Ppk 0.97, not stable",
         source="constructed", setting="turned shaft journal Ø20.000 ± 0.020 mm, micrometer to 0.001 mm, 5 consecutive parts every 20 min, mean drifting upward with tool wear",
         params={"usl": 20.020, "lsl": 19.980, "target": 20.000, "subgroup_size": 5, "chart": "xbar_r", "units": "mm"},
         columns=["subgroup", "x"], rows=_dr)

# The Module 1 flatness data (lognormal, bounded at zero) against a maximum
# of 25 µm: normal-based, lognormal, Box-Cox and empirical capability compared.
register(id="m08-flatness", module="08", kind="capability_nonnormal",
         title="Flatness, 200 individuals, lognormal, maximum 25 µm: four capability methods compared",
         source="constructed", setting="the Module 1 flatness data (milled face, µm, CMM to 0.1 µm, 200 consecutive parts) with a drawing maximum of 25 µm and a natural lower bound of zero",
         params={"usl": 25.0, "lsl": None, "natural_lower": 0.0, "units": "µm"},
         columns=["i", "x"], rows=_flat)

# Leak-test rejects on a pressed seal fitting, 24 lots of 150 to 250: attribute capability.
_rng = np.random.default_rng(1)
_ln = [int(v) for v in _rng.integers(150, 251, 24)]
_ld = [int(_rng.binomial(v, 0.021)) for v in _ln]
register(id="m08-leak", module="08", kind="attribute_capability",
         title="Leak-test rejects, 24 lots of 150 to 250 fittings, p about 2.3 %",
         source="constructed", setting="pressed seal fittings, 100 % leak test at the end of the line, one lot per shift for 24 shifts, lot sizes 150 to 250",
         params={"precision_e": 0.005, "units": "fittings"},
         columns=["lot", "n", "defectives"], rows=[[i + 1, n, d] for i, (n, d) in enumerate(zip(_ln, _ld))])

# A supplier's 30-part report: pin diameter, parts picked from a tote and
# measured in the order they came out. Ppk 1.38 with a 95 % interval of 1.00 to 1.75.
_rng = np.random.default_rng(30)
register(id="m08-supplier", module="08", kind="capability",
         title="Supplier report: pin diameter, 30 parts from a tote, Ppk 1.38 with 95 % CI 1.00 to 1.75",
         source="constructed", setting="ground pin Ø5.000 ± 0.012 mm, 30 parts taken from a tote and measured with a micrometer to 0.001 mm in the order they were picked",
         params={"usl": 5.012, "lsl": 4.988, "target": 5.000, "subgroup_size": 1, "chart": "imr", "units": "mm"},
         columns=["i", "x"], rows=[[i + 1, round(float(v), 3)] for i, v in enumerate(_rng.normal(5.0005, 0.0028, 30))])

# Exercise 1: radial runout of a turned shaft (a Rayleigh-type characteristic:
# the length of a two-dimensional eccentricity vector), maximum 0.030 mm.
_rng = np.random.default_rng(1)
_e1 = _rng.normal(0, 0.008, 80); _e2 = _rng.normal(0, 0.008, 80)
_ro = [round(float(v), 3) for v in np.sqrt(_e1 ** 2 + _e2 ** 2)]
register(id="m08-ex1-runout", module="08", kind="capability_nonnormal",
         title="Exercise 1: radial runout, 80 individuals, bounded at zero, maximum 0.030 mm",
         source="constructed", setting="radial runout of a turned shaft on a dial indicator to 0.001 mm, 80 consecutive parts, drawing maximum 0.030 mm; constructed as the length of a two-dimensional eccentricity vector with 0.008 mm noise on each axis",
         params={"usl": 0.030, "lsl": None, "natural_lower": 0.0, "units": "mm"},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_ro)])

# Exercise 2: cosmetic rejects on painted covers, 20 lots of about 400.
_rng = np.random.default_rng(1)
_cn = [int(v) for v in _rng.integers(360, 441, 20)]
_cd = [int(_rng.binomial(v, 0.012)) for v in _cn]
register(id="m08-ex2-paint", module="08", kind="attribute_capability",
         title="Exercise 2: cosmetic rejects on painted covers, 20 lots of 360 to 440, p about 1.3 %",
         source="constructed", setting="painted covers inspected 100 % at the end of the paint line, one lot per day for 20 days",
         params={"precision_e": 0.004, "units": "covers"},
         columns=["lot", "n", "defectives"], rows=[[i + 1, n, d] for i, (n, d) in enumerate(zip(_cn, _cd))])


# ---------------------------------------------------------------------------
# Module 11: Hypothesis testing (prefix m11-; m11-ttest2-pull and
# m11-anova-machines were registered in Phase C and are taught here)
# ---------------------------------------------------------------------------
# The two supplier groups of m11-ttest2-pull as separate descriptive sets, for
# the normality check on each group.
register(id="m11-pull-a", module="11", kind="descriptive",
         title="Supplier A pull strengths (the A group of m11-ttest2-pull)", source="constructed",
         setting="12 solder-joint pull strengths in N from supplier A", params={"units": "N"},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_ta)])
register(id="m11-pull-b", module="11", kind="descriptive",
         title="Supplier B pull strengths (the B group of m11-ttest2-pull)", source="constructed",
         setting="12 solder-joint pull strengths in N from supplier B", params={"units": "N"},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_tb)])

# Power of the pull-strength study at n = 12 per group for a 2.0 N difference,
# and the sample size that would give 80 % power.
register(id="m11-power-pull", module="11", kind="power",
         title="Power of a two-sample t at n = 12 per group, delta 2.0 N, sigma 2.65 N",
         source="arithmetic on the normal approximation (NIST 7.2.2.2 formula solved for power)",
         setting="parameters only; sigma 2.65 N is the pooled sd of the pull-strength study rounded",
         params={"alpha": 0.05, "sides": 2, "delta": 2.0, "sigma": 2.65, "n": 12, "design": "two-sample",
                 "curve_n": [4, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60]},
         columns=None, rows=None)
register(id="m11-samplesize-pull", module="11", kind="samplesize",
         title="Sample size per group for delta 2.0 N, sigma 2.65 N, alpha 0.05 two-sided, power 0.80",
         source="NIST 7.2.2.2 (S-B8) formula", setting="parameters only",
         params={"alpha": 0.05, "beta": 0.20, "delta": 2.0, "sigma": 2.65, "sides": 2, "design": "two-sample"},
         columns=None, rows=None)

# Paired: cycle time at 12 assembly stations before and after a fixture change.
_rng = np.random.default_rng(6)
_pb = np.round(_rng.normal(48.0, 3.0, 12), 1); _pa = np.round(_pb - 1.6 + _rng.normal(0, 1.1, 12), 1)
register(id="m11-paired-cycle", module="11", kind="paired",
         title="Cycle time at 12 stations before and after a fixture change, paired t",
         source="constructed", setting="manual assembly cycle time in s at 12 stations, each timed before and after a fixture change, stopwatch to 0.1 s",
         params={"alpha": 0.05, "units": "s"},
         columns=["pair", "before", "after"], rows=[[i + 1, float(b), float(a)] for i, (b, a) in enumerate(zip(_pb, _pa))])

# One-sample: the Module 1 torque data against the 12.0 N·m target.
_rng = np.random.default_rng(2)
register(id="m11-ttest1-torque", module="11", kind="ttest1",
         title="Tightening torque, 30 joints, one-sample t against the 12.0 N·m target",
         source="constructed", setting="the Module 1 exercise data: tightening torque of a bolted joint, 12.0 ± 1.0 N·m, torque analyser to 0.01 N·m, 30 consecutive joints",
         params={"mu0": 12.0, "alpha": 0.05, "units": "N·m"},
         columns=["i", "x"], rows=[[i + 1, round(float(v), 2)] for i, v in enumerate(_rng.normal(12.15, 0.28, 30))])

# Chi-square: defect type by shift on a brazed assembly line.
_rng = np.random.default_rng(1)
_P3 = [[0.40, 0.30, 0.20, 0.10], [0.42, 0.28, 0.20, 0.10], [0.25, 0.30, 0.35, 0.10]]
_obs3 = [list(map(int, _rng.multinomial(t, p))) for t, p in zip([120, 110, 95], _P3)]
register(id="m11-chisq-shift", module="11", kind="chisq",
         title="Defect type by shift, 3 x 4 contingency table",
         source="constructed", setting="rejects on a brazed assembly line over a month, classified by defect type (porosity, crack, gap, other) and by shift",
         params={"columns": ["Porosity", "Crack", "Gap", "Other"], "alpha": 0.05},
         columns=["row", "Porosity", "Crack", "Gap", "Other"],
         rows=[[nm] + o for nm, o in zip(["Day", "Evening", "Night"], _obs3)])

# Mann-Whitney: flatness (lognormal) from two fixtures, 15 parts each.
_rng = np.random.default_rng(39)
_fa = np.round(np.exp(_rng.normal(np.log(8.0), 0.5, 15)), 1); _fb = np.round(np.exp(_rng.normal(np.log(12.0), 0.5, 15)), 1)
register(id="m11-mw-flatness", module="11", kind="mannwhitney",
         title="Flatness from two fixtures, 15 parts each, Mann-Whitney U",
         source="constructed", setting="flatness of a milled face in µm (CMM to 0.1 µm) on 15 parts from each of two fixtures; right-skewed by construction",
         params={"alpha": 0.05, "units": "µm"},
         columns=["group", "x"], rows=[["F1", float(v)] for v in _fa] + [["F2", float(v)] for v in _fb])

# Exercise 1: adhesive cure time from two ovens, 10 each, no real difference.
_rng = np.random.default_rng(2)
_o1 = np.round(_rng.normal(31.5, 1.8, 10), 1); _o2 = np.round(_rng.normal(32.3, 1.8, 10), 1)
register(id="m11-ex1-cure", module="11", kind="ttest2",
         title="Exercise 1: adhesive cure time from two ovens, two-sample t",
         source="constructed", setting="time in min for an adhesive to reach handling strength, 10 samples cured in each of two ovens, timed to 0.1 min",
         params={"alpha": 0.05, "mu0_diff": 0.0, "units": "min"},
         columns=["group", "x"], rows=[["Oven 1", float(v)] for v in _o1] + [["Oven 2", float(v)] for v in _o2])

# Exercise 2: leak location by braze fixture, 2 x 3, no evidence of association.
_rng = np.random.default_rng(1)
_obs2 = [list(map(int, _rng.multinomial(t, p))) for t, p in zip([60, 52], [[0.5, 0.3, 0.2], [0.45, 0.33, 0.22]])]
register(id="m11-ex2-chisq-leak", module="11", kind="chisq",
         title="Exercise 2: leak location by fixture, 2 x 3 contingency table",
         source="constructed", setting="leak location (header joint, tube joint, baffle joint) of 112 leaking heat-exchanger cores, by the braze fixture they were built on",
         params={"columns": ["Header", "Tube", "Baffle"], "alpha": 0.05},
         columns=["row", "Header", "Tube", "Baffle"], rows=[[nm] + o for nm, o in zip(["Fixture A", "Fixture B"], _obs2)])


# ---------------------------------------------------------------------------
# Module 13: Design of experiments (prefix m13-)
# ---------------------------------------------------------------------------
_STD3 = [(-1, -1, -1), (1, -1, -1), (-1, 1, -1), (1, 1, -1), (-1, -1, 1), (1, -1, 1), (-1, 1, 1), (1, 1, 1)]
_STD2 = [(-1, -1), (1, -1), (-1, 1), (1, 1)]

# 2^3 with 2 replicates: length of a moulded housing (mm) vs melt temperature (A),
# hold pressure (B) and cooling time (C); A and B large, AB present, C small.
_rng = np.random.default_rng(12)
_m13a = []; _run = 0
for (_a, _b, _c) in _STD3:
    for _rep in (1, 2):
        _run += 1
        _m13a.append([_run, _rep, _a, _b, _c, round(float(45.20 - 0.040 * _a + 0.050 * _b + 0.010 * _c - 0.025 * _a * _b + _rng.normal(0, 0.02)), 2)])
register(id="m13-mould", module="13", kind="factorial",
         title="2^3 factorial with 2 replicates: moulded housing length vs melt temperature, hold pressure, cooling time",
         source="constructed", setting="injection-moulded housing, overall length nominal 45.20 mm measured on a CMM to 0.01 mm; A melt temperature 230/250 °C, B hold pressure 40/60 MPa, C cooling time 15/25 s; 16 runs in random order",
         params={"k": 3, "replicates": 2, "factors": ["A", "B", "C"], "units": "mm"},
         columns=["run", "rep", "A", "B", "C", "y"], rows=_m13a)

# 2^2 with 2 replicates where one-factor-at-a-time misses the optimum: bond strength (MPa)
# vs cure temperature (A) and cure time (B) with a strong interaction.
_rng = np.random.default_rng(1)
_base = {(-1, -1): 15.0, (1, -1): 12.0, (-1, 1): 13.0, (1, 1): 22.0}
_m13b = []; _run = 0
for (_a, _b) in _STD2:
    for _rep in (1, 2):
        _run += 1
        _m13b.append([_run, _rep, _a, _b, round(float(_base[(_a, _b)] + _rng.normal(0, 0.8)), 1)])
register(id="m13-ofat", module="13", kind="factorial",
         title="2^2 factorial with 2 replicates: adhesive bond strength with a strong interaction (the OFAT trap)",
         source="constructed", setting="lap-shear strength in MPa of a structural adhesive; A cure temperature 80/120 °C, B cure time 30/60 min; tester to 0.1 MPa",
         params={"k": 2, "replicates": 2, "factors": ["A", "B"], "units": "MPa"},
         columns=["run", "rep", "A", "B", "y"], rows=_m13b)

# 2^(4-1) half fraction, D = ABC, unreplicated: plating thickness (µm) vs current density (A),
# bath temperature (B), agitation (C) and plating time (D); A and D active, analysed by Lenth's method.
_rng = np.random.default_rng(1)
_m13c = []; _run = 0
for (_a, _b, _c) in _STD3:
    _d = _a * _b * _c; _run += 1
    _m13c.append([_run, 1, _a, _b, _c, _d, round(float(25.0 + 3.0 * _a + 0.75 * _b - 0.25 * _c + 4.0 * _d + _rng.normal(0, 0.9)), 1)])
register(id="m13-plating", module="13", kind="factorial",
         title="2^(4-1) half fraction (D = ABC), unreplicated: plating thickness vs current density, bath temperature, agitation, time",
         source="constructed", setting="nickel plating thickness in µm measured by XRF to 0.1 µm; A current density 2/4 A/dm², B bath temperature 50/60 °C, C agitation off/on, D plating time 20/30 min; 8 runs, generator D = ABC, analysed as a 2^3 in A, B, C with the ABC contrast estimating D",
         params={"k": 3, "replicates": 1, "factors": ["A", "B", "C"], "generator": "D = ABC", "units": "µm"},
         columns=["run", "rep", "A", "B", "C", "D", "y"], rows=_m13c)

# Exercise 1: 2^2 with 3 replicates, spot-weld nugget diameter (mm) vs current (A) and weld time (B).
_rng = np.random.default_rng(2)
_m13d = []; _run = 0
for (_a, _b) in _STD2:
    for _rep in (1, 2, 3):
        _run += 1
        _m13d.append([_run, _rep, _a, _b, round(float(5.4 + 0.30 * _a + 0.15 * _b + 0.03 * _a * _b + _rng.normal(0, 0.12)), 2)])
register(id="m13-ex1-weld", module="13", kind="factorial",
         title="Exercise 1: 2^2 factorial with 3 replicates, spot-weld nugget diameter",
         source="constructed", setting="nugget diameter in mm from peel tests, to 0.01 mm; A weld current 8/10 kA, B weld time 10/14 cycles; 12 welds in random order",
         params={"k": 2, "replicates": 3, "factors": ["A", "B"], "units": "mm"},
         columns=["run", "rep", "A", "B", "y"], rows=_m13d)

# Exercise 2: 2^3 unreplicated, surface roughness Ra (µm) vs feed (A), speed (B), depth of cut (C).
_rng = np.random.default_rng(1)
_m13e = []; _run = 0
for (_a, _b, _c) in _STD3:
    _run += 1
    _m13e.append([_run, 1, _a, _b, _c, round(float(1.60 + 0.40 * _a - 0.20 * _b + 0.15 * _a * _b + _rng.normal(0, 0.06)), 2)])
register(id="m13-ex2-roughness", module="13", kind="factorial",
         title="Exercise 2: 2^3 unreplicated, turned surface roughness, Lenth's method",
         source="constructed", setting="surface roughness Ra in µm of a turned shaft, profilometer to 0.01 µm; A feed 0.1/0.2 mm/rev, B cutting speed 150/250 m/min, C depth of cut 0.5/1.0 mm; 8 runs",
         params={"k": 3, "replicates": 1, "factors": ["A", "B", "C"], "units": "µm"},
         columns=["run", "rep", "A", "B", "C", "y"], rows=_m13e)


# ---------------------------------------------------------------------------
# Module 16: Statistical process control I (prefix m16-; m07-bore is reused
# for the X-bar-R chart and chk-nist-imr is the published individuals check)
# ---------------------------------------------------------------------------
# Braze furnace zone temperature, hourly, 50 readings, one special cause (a spike at reading 33).
_rng = np.random.default_rng(25)
_ft = np.round(_rng.normal(610.0, 1.2, 50), 1); _ft[32] = round(float(_ft[32] + 5.5), 1)
register(id="m16-furnace", module="16", kind="imr",
         title="Furnace zone temperature, 50 hourly readings, one special cause at reading 33",
         source="constructed", setting="braze furnace zone-3 temperature in °C, logged hourly by the controller's thermocouple to 0.1 °C, 50 consecutive hours",
         params={"units": "°C"}, columns=["i", "x"], rows=[[i + 1, float(v)] for i, v in enumerate(_ft)])
# The same readings with the special cause (reading 33) removed after its cause was found: the recomputed limits.
register(id="m16-furnace-clean", module="16", kind="imr",
         title="Furnace zone temperature, the 49 readings after removing the assigned special cause at reading 33",
         source="constructed", setting="m16-furnace without reading 33 (cause found and documented), for the recomputed limits",
         params={"units": "°C"}, columns=["i", "x"], rows=[[i + 1, float(v)] for i, v in enumerate(_ft) if i != 32])

# Heat-seal width, 20 subgroups of 10, stable: the X-bar-S case.
_rng = np.random.default_rng(1)
_sw = []
for _g in range(1, 21):
    for _ in range(10):
        _sw.append([_g, round(float(_rng.normal(5.00, 0.06)), 2)])
register(id="m16-seal", module="16", kind="xbar_s",
         title="Heat-seal width, 20 subgroups of 10, X-bar-S chart, stable",
         source="constructed", setting="heat-seal width of a pouch in mm measured with a calibrated loupe to 0.01 mm, 10 consecutive pouches every hour for 20 hours",
         params={"units": "mm"}, columns=["subgroup", "x"], rows=_sw)

# Dispensed adhesive mass, 50 shots, a one-sigma upward shift from shot 26: the runs rules catch what rule 1 misses.
_rng = np.random.default_rng(585)
_am = np.round(np.concatenate([_rng.normal(20.0, 0.5, 25), _rng.normal(20.5, 0.5, 25)]), 2)
register(id="m16-shift", module="16", kind="imr",
         title="Dispensed adhesive mass, 50 shots, a 1-sigma shift at shot 26 caught by the runs rules",
         source="constructed", setting="mass of adhesive dispensed per shot in mg, one shot weighed on a balance to 0.01 mg every 10 minutes; a new adhesive lot from shot 26",
         params={"units": "mg", "shift_at": 26}, columns=["i", "x"], rows=[[i + 1, float(v)] for i, v in enumerate(_am)])

# Average run lengths of the Shewhart chart with the Western Electric rules (exact Markov chain,
# Champ and Woodall 1987), for shifts in units of the plotted statistic's sigma.
register(id="m16-arl", module="16", kind="arl",
         title="ARL of the 3-sigma chart with the Western Electric rules, exact Markov chain",
         source="method: Champ and Woodall 1987 (S-C11); values computed by the course's own chain and checked by Monte Carlo in recompute.py",
         setting="parameters only; normal plotted statistic with a shift of delta sigma",
         params={"rule_sets": [["we1"], ["we1", "we2"], ["we1", "we3"], ["we1", "we4"], ["we1", "we2", "we3", "we4"]],
                 "shifts": [0.0, 0.5, 1.0, 1.5, 2.0, 3.0], "mc_runs": 20000},
         columns=None, rows=None,
         expected={"arl.we1.0": [370.398, 0.001]})  # 1 / (2 Phi(-3)), the textbook in-control ARL of the 3-sigma chart

# Exercise 1: pin length, 20 subgroups of 4, stable.
_rng = np.random.default_rng(1)
_pl = []
for _g in range(1, 21):
    for _ in range(4):
        _pl.append([_g, round(float(_rng.normal(30.000, 0.020)), 3)])
register(id="m16-ex1-pin", module="16", kind="xbar_r",
         title="Exercise 1: pin length, 20 subgroups of 4, X-bar-R chart",
         source="constructed", setting="length of a turned pin in mm on a height gauge to 0.001 mm, 4 consecutive pins every 15 minutes for 20 samples",
         params={"units": "mm"}, columns=["subgroup", "x"], rows=_pl)

# Exercise 2: coolant concentration drifting down over 30 shifts (evaporation without top-up): what a trend looks like on an I-MR chart.
_rng = np.random.default_rng(1270)
_cc = np.round(8.0 - 0.035 * np.arange(30) + _rng.normal(0, 0.15, 30), 2)
register(id="m16-ex2-trend", module="16", kind="imr",
         title="Exercise 2: coolant concentration, 30 shifts, a steady downward trend on an I-MR chart",
         source="constructed", setting="coolant concentration in % by refractometer to 0.01 %, one reading per shift for 30 shifts, drifting down as water evaporates without top-up",
         params={"units": "%"}, columns=["i", "x"], rows=[[i + 1, float(v)] for i, v in enumerate(_cc)])


# ---------------------------------------------------------------------------
# Module 17: Statistical process control II (prefix m17-; chk-nist-ewma is the
# published EWMA check and the Module 1 flatness rows return for the
# non-normal individuals chart)
# ---------------------------------------------------------------------------
# p chart: leak-test rejects per lot, 30 lots of 180 to 260, rate doubling from lot 21.
_rng = np.random.default_rng(72)
_pn = [int(v) for v in _rng.integers(180, 261, 30)]
_pd = [int(_rng.binomial(_pn[i], 0.03 if i < 20 else 0.07)) for i in range(30)]
register(id="m17-p-leak", module="17", kind="p",
         title="Leak-test rejects per lot, 30 lots of 180 to 260, rate change at lot 21",
         source="constructed", setting="pressed fittings leak-tested 100 %, one lot per shift; a seal supplier change took effect at lot 21",
         params={"units": "fittings"}, columns=["lot", "n", "defectives"], rows=[[i + 1, n, d] for i, (n, d) in enumerate(zip(_pn, _pd))])

# np chart: rejects in fixed samples of 200 connectors from an automatic gauge, 25 samples, stable.
_rng = np.random.default_rng(1)
register(id="m17-np-connector", module="17", kind="np",
         title="Rejects in fixed samples of 200 connectors, 25 samples, np chart, stable",
         source="constructed", setting="200 connectors per hour through an automatic go/no-go gauge, 25 hourly samples",
         params={"n": 200, "units": "connectors"}, columns=["sample", "defectives"],
         rows=[[i + 1, int(_rng.binomial(200, 0.04))] for i in range(25)])

# c chart: pores per casting radiograph, 30 castings, one special cause at casting 17.
_rng = np.random.default_rng(3)
_cp = [int(v) for v in _rng.poisson(4.5, 30)]; _cp[16] += 9
register(id="m17-c-porosity", module="17", kind="c",
         title="Pores per casting on the radiograph, 30 castings, one special cause",
         source="constructed", setting="gas pores counted on the radiograph of a die-cast housing, one casting per hour for 30 hours",
         params={"units": "pores per casting"}, columns=["sample", "defects"], rows=[[i + 1, v] for i, v in enumerate(_cp)])

# u chart: solder defects per board on lots of 8 to 15 boards, 25 lots, stable.
_rng = np.random.default_rng(1)
_un = [int(v) for v in _rng.integers(8, 16, 25)]
_uc = [int(_rng.poisson(1.4 * ni)) for ni in _un]
register(id="m17-u-solder", module="17", kind="u",
         title="Solder defects per board, 25 lots of 8 to 15 boards, u chart, stable",
         source="constructed", setting="defects found by automated optical inspection on a lot of assembled boards, one lot per shift",
         params={"units": "defects per board"}, columns=["sample", "n", "defects"], rows=[[i + 1, n, c] for i, (n, c) in enumerate(zip(_un, _uc))])

# Laney p' chart: daily reject proportion on 4,000 to 6,000 units with genuine day-to-day variation (over-dispersion).
_rng = np.random.default_rng(1)
_ln2 = [int(v) for v in _rng.integers(4000, 6001, 25)]
_pt = np.clip(_rng.normal(0.020, 0.004, 25), 0.005, 0.05)
_ld2 = [int(_rng.binomial(_ln2[i], _pt[i])) for i in range(25)]
register(id="m17-pprime", module="17", kind="p_prime",
         title="Daily reject proportion on thousands of units, 25 days: classic p chart vs Laney p'",
         source="constructed (Laney 2002 method, formulas as in Minitab's methods page and Arafah 2022)",
         setting="automated end-of-line test on a high-volume connector line, 4,000 to 6,000 units per day for 25 days; the true daily rate varies with material lot",
         params={"units": "units"}, columns=["day", "n", "defectives"], rows=[[i + 1, n, d] for i, (n, d) in enumerate(zip(_ln2, _ld2))])

# EWMA and CUSUM on one series: 60 readings, a 0.7-sigma shift from reading 31, baseline 30.
_rng = np.random.default_rng(7)
_ts2 = [round(float(v), 1) for v in np.concatenate([_rng.normal(50.0, 2.0, 30), _rng.normal(51.4, 2.0, 30)])]
register(id="m17-drift-imr", module="17", kind="imr",
         title="Etch depth, 60 readings, a 0.7-sigma shift from reading 31: the individuals chart",
         source="constructed", setting="etch depth in µm from a profilometer to 0.1 µm, one wafer per hour for 60 hours; a gas-flow controller drifted from hour 31",
         params={"units": "µm", "shift_at": 31}, columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_ts2)])
register(id="m17-drift-ewma", module="17", kind="ewma",
         title="The same series on an EWMA chart, lambda 0.2, L 3, limits from the first 30 readings",
         source="constructed", setting="as m17-drift-imr",
         params={"lambda": 0.2, "L": 3.0, "limits": "exact", "baseline": 30, "units": "µm"},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_ts2)])
register(id="m17-drift-cusum", module="17", kind="cusum",
         title="The same series on a tabular CUSUM, k 0.5, h 4, parameters from the first 30 readings",
         source="constructed", setting="as m17-drift-imr",
         params={"k": 0.5, "h": 4.0, "baseline": 30, "units": "µm"},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_ts2)])

# Short-run DNOM chart: three part numbers on one lathe, 30 parts in the order machined.
_rng = np.random.default_rng(7)
_pnoms = [["P20", 20.00], ["P25", 25.00], ["P32", 32.00]]
_dn = []
for _i in range(30):
    _pn2, _nom = _pnoms[_rng.integers(0, 3)]
    _dn.append([_i + 1, _pn2, _nom, round(float(_nom + 0.004 + _rng.normal(0, 0.012)), 3)])
register(id="m17-dnom", module="17", kind="dnom",
         title="Short-run deviation-from-nominal chart: three shaft diameters on one lathe, 30 parts",
         source="constructed", setting="three part numbers (nominal diameters 20.00, 25.00 and 32.00 mm) turned on one lathe in mixed order, micrometer to 0.001 mm; the chart plots the deviation from each part's nominal",
         params={"units": "mm"}, columns=["i", "part", "nominal", "x"], rows=_dn)

# Non-normal individuals: the Module 1 flatness data charted raw and after a log transformation.
register(id="m17-flatness-imr", module="17", kind="imr",
         title="The Module 1 flatness data (lognormal) on an individuals chart: three tail points beyond the limit",
         source="constructed", setting="the 200 flatness values of Module 1 (µm) in production order",
         params={"units": "µm"}, columns=["i", "x"], rows=_flat)
register(id="m17-flatness-log-imr", module="17", kind="imr",
         title="The same flatness data charted as ln(x)",
         source="constructed", setting="natural logarithm of the Module 1 flatness values, to 4 decimals",
         params={"units": "ln µm"}, columns=["i", "x"], rows=[[i + 1, round(float(np.log(v)), 4)] for i, v in _flat])

# Exercise 1: u chart of braze-joint defects per core, 20 cores of 40 to 80 joints, one special cause at core 12.
_rng = np.random.default_rng(13)
_en = [int(v) for v in _rng.integers(40, 81, 20)]
_ec = [int(_rng.poisson(0.03 * ni * (2.5 if i == 11 else 1))) for i, ni in enumerate(_en)]
register(id="m17-ex1-u-braze", module="17", kind="u",
         title="Exercise 1: braze-joint defects per core, 20 cores of 40 to 80 joints, u chart with one special cause",
         source="constructed", setting="joint defects found by pressure decay and dye check on brazed heat-exchanger cores of different sizes, one core per shift",
         params={"units": "defects per joint"}, columns=["sample", "n", "defects"], rows=[[i + 1, n, c] for i, (n, c) in enumerate(zip(_en, _ec))])

# Exercise 2: a 0.5-sigma shift at reading 21 of 40 that the I chart misses and an EWMA catches.
_rng = np.random.default_rng(1)
_e2 = [round(float(v), 2) for v in np.concatenate([_rng.normal(12.00, 0.10, 20), _rng.normal(12.05, 0.10, 20)])]
register(id="m17-ex2-imr", module="17", kind="imr",
         title="Exercise 2: plating thickness, 40 readings with a 0.5-sigma shift at reading 21, individuals chart",
         source="constructed", setting="plating thickness in µm by XRF to 0.01 µm, one panel per hour; a bath concentration change from hour 21",
         params={"units": "µm", "shift_at": 21}, columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_e2)])
register(id="m17-ex2-ewma", module="17", kind="ewma",
         title="Exercise 2: the same readings on an EWMA chart, lambda 0.2, L 3, baseline 20",
         source="constructed", setting="as m17-ex2-imr",
         params={"lambda": 0.2, "L": 3.0, "limits": "exact", "baseline": 20, "units": "µm"},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_e2)])


# ---------------------------------------------------------------------------
# Module 19: Capstone (prefix m19-). One consistent story: a brazed aluminium
# heat-exchanger line with a 4.2 % leak-test reject rate (the Module 3
# charter baseline), driven by the braze-joint gap at the tube-to-header
# joint (specification 0.10 ± 0.05 mm). The baseline process runs at high
# clamp force with standard tube expansion (the DOE's "a" cell); the DOE finds
# that increased expansion (B) closes the gap, and the post-improvement data
# sit near the DOE's "ab" cell.
# ---------------------------------------------------------------------------
_GAP = {"usl": 0.15, "lsl": 0.05, "target": 0.10, "subgroup_size": 5, "chart": "xbar_r", "units": "mm"}
# Baseline leak-test results, 30 lots.
_rng = np.random.default_rng(1)
_bn = [int(v) for v in _rng.integers(150, 251, 30)]; _bd = [int(_rng.binomial(v, 0.042)) for v in _bn]
register(id="m19-leak-baseline", module="19", kind="attribute_capability",
         title="Capstone baseline: leak-test rejects, 30 lots, p about 4.3 %",
         source="constructed (the charter baseline of Module 3 is 42 per 1,000)", setting="brazed aluminium heat-exchanger cores, 100 % helium leak test at final inspection, one lot per shift for 30 shifts",
         params={"precision_e": 0.005, "units": "cores"}, columns=["lot", "n", "defectives"], rows=[[i + 1, n, d] for i, (n, d) in enumerate(zip(_bn, _bd))])
# Where the leaks were: the same 259 leakers by location (Pareto).
_pareto_counts = {"Tube-to-header joint": 168, "Tube-to-tube joint": 41, "Baffle joint": 22, "Manifold weld": 17, "Other / not located": 11}
assert sum(_pareto_counts.values()) == sum(_bd)
register(id="m19-pareto", module="19", kind="pareto",
         title="Capstone: leak location of the 259 baseline leakers",
         source="constructed (totals match m19-leak-baseline)", setting="leak location recorded by the test operator for every leaking core of the baseline period",
         params={}, columns=["category", "count"], rows=[[k, v] for k, v in _pareto_counts.items()])
# Gauge R&R on the gap gauge: 10 cores spanning the range, 3 operators, 2 trials.
_rng = np.random.default_rng(4)
_gp = np.linspace(0.075, 0.150, 10) + _rng.normal(0, 0.003, 10); _gob = [0.0, 0.0015, -0.001]
_g19 = []
for _p in range(10):
    for _o in range(3):
        for _t in range(2):
            _g19.append([_p + 1, "ABC"[_o], _t + 1, round(float(_gp[_p] + _gob[_o] + _rng.normal(0, 0.0025)), 3)])
register(id="m19-grr", module="19", kind="grr",
         title="Capstone: crossed gauge R&R on the joint-gap gauge, 10 x 3 x 2, tolerance 0.10 mm",
         source="constructed", setting="tube-to-header gap measured with a calibrated pin-gauge set to 0.001 mm on 10 cores spanning the range, 3 operators, 2 trials, randomised",
         params={"tolerance": 0.10, "study_var_k": 6.0, "alpha_remove": 0.05, "units": "mm"},
         columns=["part", "operator", "trial", "y"], rows=_g19)
# Baseline gap capability study, 25 subgroups of 5 cores.
_rng = np.random.default_rng(2)
_gb = []
for _g in range(1, 26):
    for _ in range(5):
        _gb.append([_g, round(float(_rng.normal(0.112, 0.0145)), 3)])
register(id="m19-gap-baseline", module="19", kind="capability",
         title="Capstone baseline: tube-to-header gap, 25 subgroups of 5 cores, Cpk about 0.9",
         source="constructed", setting="mean tube-to-header gap per core (six joints) in mm, pin gauge to 0.001 mm, five consecutive cores every hour for 25 hours, specification 0.10 ± 0.05 mm",
         params=dict(_GAP), columns=["subgroup", "x"], rows=_gb)
# Furnace peak temperature log, 40 cores.
_rng = np.random.default_rng(4)
register(id="m19-furnace", module="19", kind="imr",
         title="Capstone: furnace peak temperature, 40 consecutive cores, stable",
         source="constructed", setting="peak core temperature in °C from the braze furnace's travelling thermocouple, one core per hour for 40 hours",
         params={"units": "°C"}, columns=["i", "x"], rows=[[i + 1, round(float(v), 1)] for i, v in enumerate(_rng.normal(600.0, 1.5, 40))])
# Gap at the header joint on 20 leaking and 20 passing cores.
_rng = np.random.default_rng(2)
_la = np.round(_rng.normal(0.137, 0.012, 20), 3); _lb = np.round(_rng.normal(0.110, 0.014, 20), 3)
register(id="m19-gap-leakers", module="19", kind="ttest2",
         title="Capstone: header-joint gap on 20 leaking and 20 passing cores, two-sample t",
         source="constructed", setting="gap at the leaking joint (or the corresponding joint on a passing core) measured after sectioning, mm to 0.001",
         params={"alpha": 0.05, "mu0_diff": 0.0, "units": "mm"},
         columns=["group", "x"], rows=[["Leak", float(v)] for v in _la] + [["Pass", float(v)] for v in _lb])
# The 2^3 DOE with 2 replicates: A clamp force, B tube expansion, C furnace peak temperature; response mean gap per core.
_rng = np.random.default_rng(9)
_d19 = []; _run = 0
for (_a, _b, _c) in _STD3:
    for _rep in (1, 2):
        _run += 1
        _d19.append([_run, _rep, _a, _b, _c, round(float(0.112 - 0.006 * _a - 0.014 * _b + 0.001 * _c + 0.004 * _a * _b + _rng.normal(0, 0.004)), 3)])
register(id="m19-doe", module="19", kind="factorial",
         title="Capstone: 2^3 factorial with 2 replicates on the braze process, response mean joint gap",
         source="constructed", setting="A fixture clamp force 2/4 kN, B tube expansion standard/increased (mandrel +0.05 mm), C furnace peak temperature 595/605 °C; 16 cores in random order, response the mean tube-to-header gap per core in mm",
         params={"k": 3, "replicates": 2, "factors": ["A", "B", "C"], "units": "mm"},
         columns=["run", "rep", "A", "B", "C", "y"], rows=_d19)
# After the change (increased expansion, clamp kept high): gap capability and leak rate.
_rng = np.random.default_rng(2)
_ga = []
for _g in range(1, 26):
    for _ in range(5):
        _ga.append([_g, round(float(_rng.normal(0.100, 0.0095)), 3)])
register(id="m19-gap-after", module="19", kind="capability",
         title="Capstone after improvement: tube-to-header gap, 25 subgroups of 5, Cpk about 1.7",
         source="constructed", setting="as m19-gap-baseline, after the tube-expansion change, 25 hours of production",
         params=dict(_GAP), columns=["subgroup", "x"], rows=_ga)
_rng = np.random.default_rng(1)
_an2 = [int(v) for v in _rng.integers(150, 251, 30)]; _ad2 = [int(_rng.binomial(v, 0.008)) for v in _an2]
register(id="m19-leak-after", module="19", kind="attribute_capability",
         title="Capstone after improvement: leak-test rejects, 30 lots, p about 0.8 %",
         source="constructed", setting="as m19-leak-baseline, the 30 shifts after the change",
         params={"precision_e": 0.004, "units": "cores"}, columns=["lot", "n", "defectives"], rows=[[i + 1, n, d] for i, (n, d) in enumerate(zip(_an2, _ad2))])
# Before/after as a 2 x 2 table.
register(id="m19-before-after", module="19", kind="chisq",
         title="Capstone: leak results before and after, 2 x 2 chi-square (equivalent to a two-proportion test)",
         source="constructed (totals of m19-leak-baseline and m19-leak-after)", setting="leak and pass counts over the 30 baseline shifts and the 30 shifts after the change",
         params={"columns": ["Leak", "Pass"], "alpha": 0.05},
         columns=["row", "Leak", "Pass"], rows=[["Before", sum(_bd), sum(_bn) - sum(_bd)], ["After", sum(_ad2), sum(_an2) - sum(_ad2)]])


# ---------------------------------------------------------------------------
# Module 4: Measurement systems analysis (prefix m04-)
# New kind this module: attribute_agreement (columns part, appraiser, trial,
# rating; params standard = {part_id: true_rating}). See compute.py.
# ---------------------------------------------------------------------------
# A second, tighter crossed gauge R&R: a checkweigher on fill weight, spec
# 248.0 to 254.0 g (tolerance 6.0 g), %GRR about 7 % of study variation -
# the "good gauge" contrast to m04-grr-bore's conditional 24 %.
_rng = np.random.default_rng(1)
_parts4 = np.linspace(248.6, 253.4, 10) + _rng.normal(0, 0.15, 10)
_opbias4 = [0.0, float(_rng.normal(0, 0.05)), float(_rng.normal(0, 0.05))]
_g4s = []
for p in range(10):
    for o in range(3):
        for t in range(3):
            _g4s.append([p + 1, "ABC"[o], t + 1, round(float(_parts4[p] + _opbias4[o] + _rng.normal(0, 0.12)), 1)])
register(id="m04-grr-scale", module="04", kind="grr",
         title="Crossed gauge R&R on the checkweigher, 10 parts x 3 operators x 3 trials, %GRR about 7 %",
         source="constructed", setting="checkweigher for fill weight 248.0 to 254.0 g (tolerance 6.0 g), 10 filled containers spanning the range, 3 operators, 3 trials each, to 0.1 g",
         params={"tolerance": 6.0, "study_var_k": 6.0, "alpha_remove": 0.05, "units": "g"},
         columns=["part", "operator", "trial", "y"], rows=_g4s)

# Bias: 15 repeat readings of one certified reference standard (12.010 mm)
# on the bore gauge. A small, statistically detectable positive bias.
_rng = np.random.default_rng(5)
_bias_x = [round(float(v), 3) for v in _rng.normal(12.010 + 0.0028, 0.0015, 15)]
register(id="m04-bias", module="04", kind="ttest1",
         title="Bias study: 15 readings of a 12.010 mm reference standard on the bore gauge",
         source="constructed", setting="certified reference standard, nominal 12.010 mm, bore gauge to 0.001 mm, 15 repeat readings in one sitting",
         params={"mu0": 12.010, "alpha": 0.05, "units": "mm"},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_bias_x)])

# Linearity: 5 reference standards spanning the tolerance, 4 replicate
# readings each; bias regressed against the reference value. A small but
# statistically detectable linearity trend (slope about 0.12).
_rng = np.random.default_rng(1)
_lin_levels = (11.985, 11.995, 12.005, 12.015, 12.025)
_lin_center = sum(_lin_levels) / len(_lin_levels)
_lin_rows = []
for _lv in _lin_levels:
    _true_bias = 0.0015 + 0.14 * (_lv - _lin_center)
    for _ in range(4):
        _measured = round(float(_lv + _true_bias + _rng.normal(0, 0.0015)), 3)
        _lin_rows.append([_lv, _measured, round(_measured - _lv, 4)])
register(id="m04-linearity", module="04", kind="regression",
         title="Linearity study: 5 reference standards x 4 replicates, bias vs reference value",
         source="constructed", setting="5 certified reference standards spanning 11.985 to 12.025 mm, bore gauge to 0.001 mm, 4 repeat readings per standard",
         params={"alpha": 0.05, "units": "mm"},
         columns=["x", "measured", "y"], rows=_lin_rows)

# Stability: the same 12.010 mm reference measured once per shift for 24
# shifts. Stable: no special cause, even though the gauge carries a small
# bias and a small linearity effect (stability is a separate question).
_rng = np.random.default_rng(1)
_stab_x = [round(float(v), 3) for v in _rng.normal(12.010 + 0.0028, 0.0015, 24)]
register(id="m04-stability", module="04", kind="imr",
         title="Stability study: the 12.010 mm reference standard, one reading per shift for 24 shifts",
         source="constructed", setting="certified reference standard, nominal 12.010 mm, bore gauge to 0.001 mm, one reading logged at the start of each of 24 shifts",
         params={"units": "mm"},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_stab_x)])

# Attribute agreement: 3 inspectors x 30 braze-fillet appearance parts x 2
# trials (accept 0 / reject 1). 6 of the 30 parts are borderline (a known,
# constructed "true" state exists for every part, established separately
# from the inspectors' own calls, so effectiveness against that standard can
# be reported alongside inter-appraiser agreement). Target Fleiss' kappa
# (3 appraisers) about 0.6 - moderate agreement, not suspiciously clean.
_rng = np.random.default_rng(9)
_n_parts4 = 30
_truth4 = np.array([0] * (_n_parts4 - 8) + [1] * 8)
_rng.shuffle(_truth4)
_border4 = set(_rng.choice(_n_parts4, 6, replace=False).tolist())
_pcorrect4 = np.full(_n_parts4, 0.93)
for _i in _border4:
    _pcorrect4[_i] = 0.55
_attr_rows = []
for _i in range(_n_parts4):
    for _a in range(3):
        for _t in range(2):
            _r = int(_truth4[_i]) if _rng.random() < _pcorrect4[_i] else 1 - int(_truth4[_i])
            _attr_rows.append([_i + 1, "ABC"[_a], _t + 1, _r])
register(id="m04-attribute-braze", module="04", kind="attribute_agreement",
         title="Attribute agreement: braze fillet appearance, 3 inspectors x 30 parts x 2 trials",
         source="constructed", setting="visual accept/reject call on a braze fillet, 3 inspectors, 30 parts (6 deliberately borderline), 2 trials per inspector in randomised, blind order",
         params={"standard": {str(_i + 1): int(_truth4[_i]) for _i in range(_n_parts4)}},
         columns=["part", "appraiser", "trial", "rating"], rows=_attr_rows)

# Exercise 1: bias study, a caliper checking a keyway reference standard
# (6.015 mm), 12 readings, a small but statistically detectable negative bias.
_rng = np.random.default_rng(1)
_ex1_x = [round(float(v), 3) for v in _rng.normal(6.015 - 0.006, 0.003, 12)]
register(id="m04-ex1-bias", module="04", kind="ttest1",
         title="Exercise 1: bias study, keyway caliper on a 6.015 mm reference, 12 readings",
         source="constructed", setting="certified reference standard, nominal 6.015 mm, dial caliper to 0.001 mm, 12 repeat readings",
         params={"mu0": 6.015, "alpha": 0.05, "units": "mm"},
         columns=["i", "x"], rows=[[i + 1, v] for i, v in enumerate(_ex1_x)])

# Exercise 2: attribute agreement, 2 inspectors x 20 parts x 2 trials, a
# simpler design than the main braze example; target kappa about 0.73 (substantial).
_rng = np.random.default_rng(5)
_n_ex2, _n_border_ex2 = 20, 3
_truth_ex2 = np.array([0] * (_n_ex2 - 5) + [1] * 5)
_rng.shuffle(_truth_ex2)
_border_ex2 = set(_rng.choice(_n_ex2, _n_border_ex2, replace=False).tolist())
_pcorrect_ex2 = np.full(_n_ex2, 0.95)
for _i in _border_ex2:
    _pcorrect_ex2[_i] = 0.6
_ex2_rows = []
for _i in range(_n_ex2):
    for _a in range(2):
        for _t in range(2):
            _r = int(_truth_ex2[_i]) if _rng.random() < _pcorrect_ex2[_i] else 1 - int(_truth_ex2[_i])
            _ex2_rows.append([_i + 1, "AB"[_a], _t + 1, _r])
register(id="m04-ex2-attribute", module="04", kind="attribute_agreement",
         title="Exercise 2: attribute agreement, 2 inspectors x 20 parts x 2 trials",
         source="constructed", setting="visual accept/reject call on a connector housing, 2 inspectors, 20 parts (3 deliberately borderline), 2 trials each",
         params={"standard": {str(_i + 1): int(_truth_ex2[_i]) for _i in range(_n_ex2)}},
         columns=["part", "appraiser", "trial", "rating"], rows=_ex2_rows)


# ---------------------------------------------------------------------------
# Module 5: Data collection and sampling (prefix m05-)
# No new kind: rational subgrouping reuses `capability` (chart="xbar_r")
# twice on the same 100 values with different subgroup assignment; rounding
# loss reuses `descriptive` twice on the same values rounded two ways.
# ---------------------------------------------------------------------------
# A two-cavity mold: cavity A centred on 8.000 mm, cavity B running 0.010 mm
# high, parts produced in strict alternation (A, B, A, B, ...). The same 100
# individual readings are subgrouped two ways below.
def _m05_two_cavity(seed=1, mu=8.000, sigma=0.005, delta=0.010, n=100):
    rng = np.random.default_rng(seed)
    vals = np.empty(n)
    cavity = np.empty(n, dtype=int)
    for i in range(n):
        if i % 2 == 0:
            vals[i] = rng.normal(mu, sigma)
            cavity[i] = 0
        else:
            vals[i] = rng.normal(mu + delta, sigma)
            cavity[i] = 1
    return np.round(vals, 3), cavity


_m05v, _m05c = _m05_two_cavity()
_P_M05 = {"usl": 8.020, "lsl": 7.980, "target": 8.000, "subgroup_size": 5, "chart": "xbar_r", "units": "mm"}

# Naive (production-sequence) subgrouping: 20 consecutive subgroups of 5, in
# the order parts actually came off the line, mixing both cavities in every
# subgroup because the line alternates cavities part by part.
register(id="m05-subgroup-naive", module="05", kind="capability",
         title="Naive subgrouping: 100 individuals, 20 subgroups of 5 in strict production order (mixed cavities)",
         source="constructed", setting="two-cavity injection-moulded bracket hole, Ø8.000 ± 0.020 mm, bore gauge to 0.001 mm, 100 consecutive parts, cavities alternate A, B, A, B ...",
         params=dict(_P_M05),
         columns=["subgroup", "x"], rows=[[(i // 5) + 1, float(v)] for i, v in enumerate(_m05v)])

# Rational (by-cavity) subgrouping: the identical 100 values, reordered only
# so that each subgroup of 5 comes from a single cavity (cavity A's 50
# values as 10 subgroups, then cavity B's 50 values as 10 subgroups).
_m05_order = [i for i in range(100) if _m05c[i] == 0] + [i for i in range(100) if _m05c[i] == 1]
_m05v_rational = _m05v[_m05_order]
register(id="m05-subgroup-rational", module="05", kind="capability",
         title="Rational subgrouping: the same 100 individuals, regrouped so every subgroup of 5 is a single cavity",
         source="constructed", setting="the same 100 readings as m05-subgroup-naive, reordered so subgroups 1-10 are cavity A and subgroups 11-20 are cavity B",
         params=dict(_P_M05),
         columns=["subgroup", "x"], rows=[[(i // 5) + 1, float(v)] for i, v in enumerate(_m05v_rational)])

# Rounding loss: the same 80 true continuous readings, rounded to a
# 0.001 mm gauge resolution (fine) and to a 0.01 mm resolution (coarse, an
# under-resolved instrument for this tolerance), showing the sd inflation
# from quantisation.
_rng = np.random.default_rng(1)
_m05_true = _rng.normal(6.500, 0.008, 80)
register(id="m05-rounding-fine", module="05", kind="descriptive",
         title="Locating pin diameter, 80 individuals, recorded to 0.001 mm (fine resolution)",
         source="constructed", setting="locating pin Ø6.500 ± 0.030 mm, digital micrometer to 0.001 mm, 80 consecutive parts",
         params={"usl": 6.530, "lsl": 6.470, "units": "mm"},
         columns=["i", "x"], rows=[[i + 1, round(float(v), 3)] for i, v in enumerate(_m05_true)])
register(id="m05-rounding-coarse", module="05", kind="descriptive",
         title="The same 80 parts, recorded to 0.01 mm (coarse resolution, a dial caliper)",
         source="constructed", setting="the same 80 parts as m05-rounding-fine, this time read from a dial caliper to 0.01 mm",
         params={"usl": 6.530, "lsl": 6.470, "units": "mm"},
         columns=["i", "x"], rows=[[i + 1, round(float(v), 2)] for i, v in enumerate(_m05_true)])

# Exercise 1: two machines running the same part in alternation, 40
# individuals, 8 subgroups of 5, the same naive-vs-rational comparison at
# smaller scale.
def _m05_two_machine(seed=5, mu=25.000, sigma=0.010, delta=0.018, n=40):
    rng = np.random.default_rng(seed)
    vals = np.empty(n)
    machine = np.empty(n, dtype=int)
    for i in range(n):
        if i % 2 == 0:
            vals[i] = rng.normal(mu, sigma)
            machine[i] = 0
        else:
            vals[i] = rng.normal(mu + delta, sigma)
            machine[i] = 1
    return np.round(vals, 3), machine


_m05ev, _m05em = _m05_two_machine()
_P_M05EX = {"usl": 25.040, "lsl": 24.960, "target": 25.000, "subgroup_size": 5, "chart": "xbar_r", "units": "mm"}
register(id="m05-ex1-naive", module="05", kind="capability",
         title="Exercise 1: naive subgrouping, two machines, 40 individuals, 8 subgroups of 5",
         source="constructed", setting="a shaft shoulder diameter, Ø25.000 ± 0.040 mm, machined on two nominally identical lathes running in alternation, micrometer to 0.001 mm",
         params=dict(_P_M05EX),
         columns=["subgroup", "x"], rows=[[(i // 5) + 1, float(v)] for i, v in enumerate(_m05ev)])
_m05e_order = [i for i in range(40) if _m05em[i] == 0] + [i for i in range(40) if _m05em[i] == 1]
_m05ev_rational = _m05ev[_m05e_order]
register(id="m05-ex1-rational", module="05", kind="capability",
         title="Exercise 1: rational subgrouping, the same 40 individuals regrouped by machine",
         source="constructed", setting="the same 40 readings as m05-ex1-naive, reordered so subgroups 1-4 are machine 1 and subgroups 5-8 are machine 2",
         params=dict(_P_M05EX),
         columns=["subgroup", "x"], rows=[[(i // 5) + 1, float(v)] for i, v in enumerate(_m05ev_rational)])


# ---------------------------------------------------------------------------
# Module 6: Sigma level, DPMO, DPU, RTY (prefix m06-)
# New kind this module: rty_chain (params yields -> RTY, normalized yield,
# total DPU, cumulative RTY). dpmo and sigma_table already exist.
# ---------------------------------------------------------------------------
# A 5-step wire-harness assembly line; yields match Calc.dpmo's own client-side
# default so the calculator's out-of-the-box view matches this worked example.
register(id="m06-rty-chain", module="06", kind="rty_chain",
         title="Rolled throughput yield, 5-step wire-harness assembly line",
         source="constructed", setting="crimp, insulate, sub-assemble, function test, final inspection; first-time yield at each of the 5 steps",
         params={"yields": [0.98, 0.95, 0.99, 0.97, 0.985],
                 "step_names": ["Crimp", "Insulate", "Sub-assemble", "Function test", "Final inspection"]},
         columns=None, rows=None)

# Connector defects: 2,400 units, 5 solder joints (opportunities) per unit.
register(id="m06-dpmo-connector", module="06", kind="dpmo",
         title="Connector solder-joint defects, 2,400 units, 5 opportunities per unit",
         source="constructed", setting="wire-to-board connector, 5 solder joints inspected per unit (the defined opportunities), 2,400 units, 54 joint defects logged",
         params={"defects": 54, "units": 2400, "opportunities": 5}, columns=None, rows=None)

# The identical 54-defects-in-2,400-units count, recounted with 1 and with 10
# opportunities per unit, to show the sigma level move without the process changing.
register(id="m06-gaming-op1", module="06", kind="dpmo",
         title="The same 54 defects in 2,400 units, counted as 1 opportunity per unit",
         source="constructed", setting="the same connector defects as m06-dpmo-connector, this time counted with only 1 opportunity per unit (a unit either has a defect or it does not)",
         params={"defects": 54, "units": 2400, "opportunities": 1}, columns=None, rows=None)
register(id="m06-gaming-op10", module="06", kind="dpmo",
         title="The same 54 defects in 2,400 units, counted as 10 opportunities per unit",
         source="constructed", setting="the same connector defects as m06-dpmo-connector, this time counted with 10 defined opportunities per unit (splitting each solder joint into 2 sub-checks)",
         params={"defects": 54, "units": 2400, "opportunities": 10}, columns=None, rows=None)

# A fuller sigma-level table than Module 0's preview: half-sigma steps 1 to 6.
register(id="m06-sigma-table", module="06", kind="sigma_table",
         title="Sigma level to PPM, half-sigma steps from 1 to 6, centred and with the 1.5 sigma shift",
         source="arithmetic on the normal distribution; the shift is the Motorola convention (S-E8, S-D28), critiqued in S-C9 and S-E28",
         setting="parameters only",
         params={"levels": [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0], "shift": 1.5, "ppm_targets": [3.4, 100, 1000, 10000, 100000]},
         columns=None, rows=None,
         expected={"ppm_shifted_one_sided.10": [3.4, 0.01]})

# Exercise 1: a 4-step board assembly line, different yields.
register(id="m06-ex1-rty", module="06", kind="rty_chain",
         title="Exercise 1: rolled throughput yield, 4-step board assembly line",
         source="constructed", setting="place, reflow, test, conformal coat; first-time yield at each of 4 steps",
         params={"yields": [0.995, 0.96, 0.98, 0.99],
                 "step_names": ["Place", "Reflow", "Test", "Conformal coat"]},
         columns=None, rows=None)

# Exercise 2: a leak-test DPMO exercise, 3,000 units, 2 opportunities per unit.
register(id="m06-ex2-dpmo", module="06", kind="dpmo",
         title="Exercise 2: leak-test defects, 3,000 units, 2 opportunities per unit",
         source="constructed", setting="brazed assembly, 2 leak-test points per unit (inlet and outlet joints), 3,000 units, 33 point failures logged",
         params={"defects": 33, "units": 3000, "opportunities": 2}, columns=None, rows=None)


# ---------------------------------------------------------------------------
# Module 9: Graphical analysis (prefix m09-)
# New kind this module: multivari (see compute.py). `pareto` already exists
# (added in Phase D for Module 19); box plots reuse `descriptive` once per
# shift; Anscombe reuses the existing m01-anscombe-1..4.
# ---------------------------------------------------------------------------
register(id="m09-pareto-leak", module="09", kind="pareto",
         title="Pareto of leak-test reject causes, 6 categories",
         source="constructed", setting="brazed heat-exchanger cores, 169 leak-test rejects over one quarter, root cause assigned at teardown",
         params={}, columns=["category", "count"],
         rows=[["Header joint", 87], ["Fin-to-tube joint", 34], ["End cap seal", 21],
               ["Braze void", 12], ["Flux residue", 9], ["Handling damage", 6]])

# Multi-vari: braze fillet width, mm. T=5 time points across a shift, P=4
# parts per time point, K=3 positions per part. Seed chosen so that
# time-to-time (temporal) variation dominates (about 65 %), consistent with
# a furnace temperature trend across the shift.
def _m09_multivari(seed, T, P, K, base, trend, pos_sd, cyc_sd, temp_extra_sd):
    rng = np.random.default_rng(seed)
    rows = []
    for ti in range(T):
        time_effect = trend * ti + rng.normal(0, temp_extra_sd)
        for pi in range(P):
            part_effect = rng.normal(0, cyc_sd)
            for _ in range(K):
                x = base + time_effect + part_effect + rng.normal(0, pos_sd)
                rows.append([ti + 1, f"P{pi + 1}", round(float(x), 3)])
    return rows


_m09_rows = _m09_multivari(8, T=5, P=4, K=3, base=1.20, trend=0.008, pos_sd=0.004, cyc_sd=0.006, temp_extra_sd=0.010)
register(id="m09-multivari-braze", module="09", kind="multivari",
         title="Multi-vari chart: braze fillet width, 5 time points x 4 parts x 3 positions",
         source="constructed", setting="braze fillet width (mm) at the header joint, 3 positions measured around each fillet, 4 consecutive parts sampled at each of 5 points across one shift",
         params={}, columns=["time", "part", "x"], rows=_m09_rows)

# Box plot by shift: bore diameter, 3 shifts of 30, the night shift running
# high and more variable.
_rng = np.random.default_rng(8)
_bp1 = [round(float(v), 3) for v in _rng.normal(12.000, 0.006, 30)]
_bp2 = [round(float(v), 3) for v in _rng.normal(12.001, 0.006, 30)]
_bp3 = [round(float(v), 3) for v in _rng.normal(12.006, 0.009, 30)]
for _i, _bp in enumerate((_bp1, _bp2, _bp3), start=1):
    register(id=f"m09-boxplot-shift{_i}", module="09", kind="descriptive",
             title=f"Bore diameter, shift {_i}, 30 individuals",
             source="constructed", setting=f"bore Ø12.000 ± 0.020 mm, bore gauge to 0.001 mm, shift {_i} of 3, 30 consecutive parts",
             params={"usl": 12.020, "lsl": 11.980, "units": "mm"},
             columns=["i", "x"], rows=[[j + 1, v] for j, v in enumerate(_bp)])

# Exercise 1: a second Pareto, assembly defects.
register(id="m09-ex1-pareto", module="09", kind="pareto",
         title="Exercise 1: Pareto of final-assembly defects, 5 categories",
         source="constructed", setting="wire-harness sub-assembly, 112 defects logged over one month at final inspection",
         params={}, columns=["category", "count"],
         rows=[["Missing clip", 58], ["Mislabelled harness", 24], ["Crimp pull-out", 16],
               ["Wrong connector", 9], ["Damaged insulation", 5]])

# Exercise 2: a smaller multi-vari, positional variation dominant this time
# (an unevenly clamping fixture), for contrast with the main worked example.
_m09_ex2_rows = _m09_multivari(2, T=3, P=3, K=3, base=0.800, trend=0.0, pos_sd=0.018, cyc_sd=0.004, temp_extra_sd=0.003)
register(id="m09-ex2-multivari", module="09", kind="multivari",
         title="Exercise 2: multi-vari chart, 3 time points x 3 parts x 3 positions, positional variation dominant",
         source="constructed", setting="clamp fixture flatness deviation (mm), 3 positions per part, 3 parts per time point, 3 time points across a shift",
         params={}, columns=["time", "part", "x"], rows=_m09_ex2_rows)


# ---------------------------------------------------------------------------
# Module 10: Root cause analysis (prefix m10-)
# New kinds this module: rpn, fault_tree (both pure arithmetic; see compute.py).
# ---------------------------------------------------------------------------
register(id="m10-pfmea-braze", module="10", kind="rpn",
         title="PFMEA excerpt, brazed header joint, 7 failure modes",
         source="constructed", setting="process FMEA on the furnace-braze step, brazed aluminium heat-exchanger core, ratings 1-10 per the AIAG-VDA S-O-D scales",
         params={}, columns=["failure_mode", "s", "o", "d"],
         rows=[["Braze void in fillet", 7, 5, 6],
               ["Insufficient braze flow at header joint", 8, 4, 5],
               ["Flux residue trapped in joint", 6, 3, 7],
               ["Tube wall thinning from over-etch", 9, 2, 6],
               ["Fixture misalignment causing gap", 7, 3, 4],
               ["Furnace temperature out of profile", 8, 2, 3],
               ["Wrong braze alloy used", 9, 1, 2]])

# Fault tree: leak escapes to the customer undetected. Three-level tree:
# top = OR(undetected leak, shipping damage); undetected leak = AND(joint
# leaks, test misses it); joint leaks = OR(3 basic causes), chosen so the
# joint-leaks probability lands close to the capstone/Module 3 baseline
# (4.2 %, m03-charter-leak) for continuity across modules.
_m10_tree = {
    "type": "OR", "name": "Leak escapes to the customer undetected",
    "children": [
        {"type": "AND", "name": "Joint leaks and the test fails to catch it", "children": [
            {"type": "OR", "name": "Braze joint leaks", "children": [
                {"type": "basic", "name": "Insufficient flux coverage", "p": 0.015},
                {"type": "basic", "name": "Joint gap out of tolerance", "p": 0.020},
                {"type": "basic", "name": "Furnace temperature low at this joint", "p": 0.008}]},
            {"type": "basic", "name": "Leak test fails to detect a real leak", "p": 0.05}]},
        {"type": "basic", "name": "Shipping or handling damage causes a new leak", "p": 0.002}]}
register(id="m10-fault-tree-leak", module="10", kind="fault_tree",
         title="Fault tree: a leak escapes to the customer undetected",
         source="constructed", setting="brazed heat-exchanger core, from joint formation through 100% leak test to shipment",
         params={"tree": _m10_tree}, columns=None, rows=None)

# Exercise 1: a second, smaller PFMEA, connector assembly.
register(id="m10-ex1-pfmea", module="10", kind="rpn",
         title="Exercise 1: PFMEA excerpt, connector assembly, 5 failure modes",
         source="constructed", setting="process FMEA on final connector assembly, ratings 1-10 per the AIAG-VDA S-O-D scales",
         params={}, columns=["failure_mode", "s", "o", "d"],
         rows=[["Crimp pull-out below spec", 8, 3, 4],
               ["Wrong connector installed", 9, 1, 2],
               ["Missing retention clip", 7, 4, 3],
               ["Wire insulation damaged during strip", 5, 5, 6],
               ["Label transposed", 3, 4, 2]])

# Exercise 2: a smaller two-level fault tree, wire-harness continuity failure.
_m10_ex2_tree = {
    "type": "OR", "name": "Harness ships with an undetected open circuit",
    "children": [
        {"type": "AND", "name": "Open circuit occurs and test misses it", "children": [
            {"type": "basic", "name": "Crimp pull-out creates an open circuit", "p": 0.010},
            {"type": "basic", "name": "Continuity test fails to detect an open", "p": 0.03}]},
        {"type": "basic", "name": "Connector damaged after test, before shipment", "p": 0.001}]}
register(id="m10-ex2-fault-tree", module="10", kind="fault_tree",
         title="Exercise 2: fault tree, wire-harness continuity escape",
         source="constructed", setting="wire-harness assembly, from crimping through continuity test to shipment",
         params={"tree": _m10_ex2_tree}, columns=None, rows=None)


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
