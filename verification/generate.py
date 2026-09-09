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
