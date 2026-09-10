# EXAMPLES.md

Every dataset in the course, with the status of the verification protocol
(CLAUDE.md rule 2). An example may appear on a page only when every check
passes. Run `bash verification/verify_all.sh` to regenerate this status.

Checks:

- **Check 1** `compute.py`: computed from the CSV with numpy, scipy and statsmodels; where the source publishes an answer, the computed value must match it to the source's rounding (the "published" column gives the number of such values).
- **Check 2** `recompute.py`: closed-form textbook formulas in plain Python with its own normal, t, F and chi-square functions; must agree with Check 1 to 1e-9 relative (1e-6 for p-values).
- **Check 3** `sanity.py`: known relationships, plausible ranges, constants for the subgroup size, narrative-versus-number checks on the pages.
- **Check 4** `test_calculators.js`: the JavaScript engines in `assets/js/stats.js` reproduce every value in `results/` (1e-8 relative), and the numerical functions match scipy at 200 or more points each.

## Phase B harness proof (2026-09-09)

Textbook examples with published answers. All checks passed on 2026-09-09.

| id | Kind | Source (SOURCES.md) | Published values checked | Check 1 | Check 2 | Check 3 | Check 4 |
|---|---|---|---|---|---|---|---|
| chk-nist-capability | capability, individuals | S-B1 NIST 6.1.6: USL 20, LSL 8, x̄ 16, s 2 → Cp 1.0, Cpk 0.6667, Cpu 0.6667, Cpl 1.3333, k 0.3333. Data: 100 constructed values standardized to x̄ = 16, s = 2 exactly. | 7 | pass | pass (56 quantities) | pass | pass (199 values) |
| chk-nist-imr | I-MR chart | S-B3 NIST 6.3.2.2: 10 batches → x̄ 50.81, MR̄ 1.8778, UCL 55.8041, LCL 45.8159 | 4 | pass | pass (18) | pass | pass (21) |
| chk-nist-ewma | EWMA chart | S-B4 NIST 6.3.2.4: 20 values, λ 0.3, EWMA₀ 50, s 2.0539 → UCL 52.5884, LCL 47.4115 (NIST truncates; computed 47.41157), EWMA sequence 50.60, 49.52 … 51.94, 51.99 | 6 | pass | pass (8) | pass | pass (29) |
| chk-nist-samplesize | sample size, one-sided | S-B8 NIST 7.2.2.2: α 0.05, β 0.10, δ = σ → z-based 8.567 ≈ 9 (NIST uses z rounded to 1.645 and 1.282; exact z gives 8.564), t-iteration → 11 | 3 | pass | pass (5) | pass | pass (12) |
| chk-aiagvda-onesided-a | capability, natural lower limit 0, USL 0.40 mm | S-A2 AIAG & VDA SPC Manual p. 48 Fig. 7-6: x̄ 0.166, s 0.0457 → Cp* 1.46, Cpk 1.71 (USL inferred as 0.40 mm from both cases) | 2 | pass | pass (53) | pass | pass (194) |
| chk-aiagvda-onesided-b | same, second case | S-A2 p. 48: x̄ 0.250, s 0.0292 → Cp* 2.28, Cpk 1.71 | 2 | pass | pass (53) | pass | pass (193) |
| chk-montgomery-etch | 2³ factorial, 2 replicates | S-D33 Montgomery DAE plasma etch example, as reproduced with data, effects, ANOVA and R output in UW STAT 502 notes (secondary): effects A −101.625, B 7.375, C 306.125, AB −24.875, AC −153.625, BC −2.125, ABC 5.625; SS A 41311, C 374850, AC 94403, residual 18020 on 8 df; F 18.34, 166.41, 41.91; p 0.0026786, 1.233e-6, 0.0001934; residual SE 47.46; R² 0.9661 | 20 | pass | pass (44) | pass | pass (71) |
| chk-minitab-grr-anova | gauge R&R from a published ANOVA table | S-E30 Minitab "Example of Crossed Gage R&R Study": interaction F 0.434, p 0.974 (removed); variance components 0.09143 / 0.03997 / 0.05146 / 1.08645 / 1.17788; %Contribution 7.76, 92.24; SD 0.30237, 1.04233, 1.08530; %Study Var 27.86, 18.42, 20.90, 96.04; %Tolerance 22.68, 78.17 (tolerance 8); ndc 4 | 19 | pass | pass (51) | pass | pass (55) |

The raw measurements behind the Minitab example are not published on that page, so the raw-data-to-ANOVA step of the gauge R&R engine is proved by the three independent implementations on `hb-grr` (statsmodels OLS two-way ANOVA, hand sums of squares in Python, hand sums of squares in JavaScript) rather than by a published answer.

Control-chart constants (`tables.py`): d₂ and d₃ by numerical integration of the range distribution, c₄ from the gamma function; A₂, D₃, D₄ for n = 2 to 10 match NIST 6.3.2.1 (S-B2) to 0.001 (NIST prints D₄(5) as 2.115; the exact value 2.11447 rounds to 2.114 as in Montgomery and ASTM E2587); d₂, d₃ for n = 2 to 10 match AIAG & VDA SPC Manual pp. 97–98 (S-A2); c₄ for n = 2, 5, 10, 25 and E₂(2) = 2.660 match Montgomery App. VI. Statistical tables: t, chi-square and F critical values match the NIST 1.3.6.7 tables at 19 sampled entries (S-B14 to S-B16).

Numerical functions in `assets/js/stats.js` against scipy (test run 2026-09-09):

| Function | Points | Max error | Target |
|---|---|---|---|
| normCdf | 268 | 1.1e-16 abs | 1e-7 |
| normPpf | 257 | 2.9e-10 abs | 1e-6 |
| erf | 201 | 3.3e-16 abs | 1e-7 |
| tCdf | 260 | 2.3e-13 abs | 1e-5 |
| fCdf | 260 | 1.5e-13 abs | 1e-5 |
| chi2Cdf | 260 | 1.5e-14 abs | 1e-5 |
| tPpf, fPpf, chi2Ppf | 120 each | 3.2e-8, 1.7e-11, 3.4e-13 rel | 1e-6 |
| lgamma | 200 | 2.3e-15 rel | 1e-10 |

## Harness-only constructed datasets (prefix `hb-`)

Seeded constructed data with no published answer. They exist to prove that the three routes agree on every analysis kind. **They are not course examples and must not appear on any page**; the course examples for each module are registered separately (prefix `m<NN>-`) when the module is built.

| id | Kind | Setting | Check 1 | Check 2 | Check 3 | Check 4 |
|---|---|---|---|---|---|---|
| hb-xbar-r | capability with X̄-R chart, 25 × 5, shift at subgroup 19 | bore Ø12.000 ± 0.025 mm | pass | pass (58) | pass | pass (153) |
| hb-xbar-s | same data, X̄-S chart, S̄/c₄ sigma | as above | pass | pass (58) | pass | pass (153) |
| hb-imr | capability with I-MR chart, one special cause | fill weight 248–254 g | pass | pass (56) | pass | pass (130) |
| hb-p, hb-np, hb-c, hb-u | attribute charts | leak-test rejects, solder defects | pass | pass (14, 14, 13, 14) | pass | pass (78, 6, 4, 79) |
| hb-ewma, hb-cusum | time-weighted charts, 1σ shift at point 21 | cycle time s | pass | pass (8, 6) | pass | pass (128, 94) |
| hb-grr | crossed gauge R&R 10 × 3 × 3 | bore diameter, tolerance 0.050 mm | pass | pass (63) | pass | pass (92) |
| hb-factorial-2 | 2² factorial, 3 replicates | pull strength N | pass | pass (24) | pass | pass (39) |
| hb-ttest2, hb-anova1, hb-paired, hb-ttest1 | hypothesis tests | pull strength, cycle time, flatness, fill weight | pass | pass (17, 14, 8, 8) | pass | pass (28, 30, 25, 11) |
| hb-regression | simple linear regression | pull strength vs solder temperature | pass | pass (18) | pass | pass (60) |
| hb-samplesize-2 | two-sample t sample size | δ 1.5, σ 2.0, α 0.05, power 0.9 | pass | pass (5) | pass | pass (12) |

Totals on 2026-09-09: 25 examples; 63 published values matched; 686 quantities agree between Check 1 and Check 2; 1,896 values agree between Check 1 and the JavaScript engines; 240 constants match.

## Course examples

Constructed course examples (prefix `m<NN>-`). Each is labelled "constructed data, not a real production run" where it appears. The ids replace the planning ids in SOURCES.md Part 2 (`ex07-bore-capability` → `m07-bore`, and so on). All checks passed on 2026-09-09 (`verify_all.sh`: 57 examples, 1,741 quantities agree between Check 1 and Check 2, 4,162 values agree between Check 1 and the JavaScript engines, 425 page checks).

Module 2's `vsm`, `funnel` and `funnel_growth` kinds have no interactive calculator (none of the nine required calculators fits value-stream or funnel-experiment arithmetic, and Module 2 precedes the control-chart calculator by design), so Check 4 does not apply to them; `test_calculators.js` skips these kinds explicitly (see its header comment) and they are fully covered by Checks 1 to 3 instead. Module 8's `capability_nonnormal` (lognormal, Box-Cox and empirical percentile capability) and `attribute_capability` (binomial intervals) are in the same position: the capability calculator covers the normal case and the DPMO converter the p-to-sigma step, but no calculator fits distributions. Module 11's `chisq`, `mannwhitney` and `power` kinds likewise have no calculator (the tests calculator covers t-tests and ANOVA, the sample-size calculator the n-for-power direction). Module 16's `arl` kind is a static table whose Check 2 is a Monte Carlo simulation with an independent generator, compared at 5 % (several standard errors); the CLT/detection simulator is its interactive counterpart. Module 17's `p_prime` and `dnom` kinds are hand computations taught on the page (the control chart builder draws the classic p chart and an I-MR chart of pasted deviations). Module 19's `pareto` kind is arithmetic on printed counts.

| id | Module | Kind | Setting and the point it makes | Dataset | Check 1 | Check 2 | Check 3 | Check 4 | Pages |
|---|---|---|---|---|---|---|---|---|---|
| m00-sigma-table | 0 | sigma level to PPM (parameters only) | levels 1 to 6 with the 1.5σ shift: centred two-sided PPM and shifted one-sided PPM (3.4 at 6σ, checked as the published Motorola target); Z of 3.4, 100, 1,000, 10,000 and 100,000 PPM | none | pass (1 published value) | pass | pass | pass | 00 |
| m00-bore-preview | 0 | capability, I-MR, 100 individuals | drilled hole Ø8.000 ± 0.050 mm, bore gauge to 0.001 mm; stable, normal, running large: 5 of 100 oversize, Z 1.75 to the USL, 41,074 PPM predicted; the "sigma level is a tail area" preview | `m00-bore-preview.csv` | pass | pass | pass | pass | 00 |
| m00-dpmo-leak-1, m00-dpmo-leak-6 | 0 | DPMO (parameters only) | 23 leak-test failures in 1,250 brazed assemblies counted with 1 and with 6 opportunities per unit: DPMO 18,400 vs 3,067, "sigma level" 3.59 vs 4.24, same DPU 0.0184 | none | pass | pass | pass | pass | 00 |
| m00-ex1-dpmo | 0 | DPMO (parameters only) | 331 solder-joint defects on 4,800 boards of 120 joints: DPU 0.069, DPMO 575, FTY 93.3 %, Z 3.25 / 4.75; exercise 1 | none | pass | pass | pass | pass | 00 |
| m00-ex2-pull | 0 | capability, I-MR, one-sided, 60 individuals | wire-bond pull strength, minimum 8.0 N, tester to 0.01 N; stable, 1 of 60 below, Z 2.07, 19,078 PPM predicted; exercise 2 | `m00-ex2-pull.csv` | pass | pass | pass | pass | 00 |
| m01-shaft | 1 | descriptive, 60 individuals | ground shaft Ø8.000 ± 0.015 mm, micrometer to 0.001 mm; near-normal (AD p 0.38), x̄ 8.0022, s 0.00444 (n − 1) vs 0.00440 (n); the by-hand mean, median, SS and s example | `m01-shaft.csv` | pass | pass | pass | pass | 01 |
| m01-shaft-means | 1 | subgroup means, n = 5 | the same 60 values in 12 consecutive subgroups: sd of means 0.00208 vs s/√5 0.00198 (ratio 1.05); exercise 2 | `m01-shaft-means.csv` | pass | pass | pass | pass | 01 |
| m01-flatness | 1 | descriptive with log statistics, 200 individuals | milled-face flatness, µm, CMM to 0.1 µm, lognormal by construction: mean 7.875 vs median 7.2, skewness 1.40, AD p < 0.001; ln x: skewness −0.05, AD p 0.98, geometric mean 7.17 | `m01-flatness.csv` | pass | pass | pass | pass | 01 |
| m01-flatness-means | 1 | subgroup means, n = 2, 5, 10 | the same 200 values: sd of means vs s/√n ratios 0.99, 1.10, 1.05; skewness 1.40 → 0.52, −0.15, 0.08; AD p of the means 0.21, 0.28, 0.88 (the central limit theorem on printed data) | `m01-flatness-means.csv` | pass | pass | pass | pass | 01 |
| m01-binomial | 1 | binomial and Poisson (parameters only) | n 50, p 0.02: P(0) 0.364, P(≥3) 0.078; λ 1.5: P(0) 0.223, P(≥3) 0.191 | none | pass | pass | pass | pass | 01 |
| m01-ex1-torque | 1 | descriptive, 30 individuals | tightening torque 12.0 ± 1.0 N·m, analyser to 0.01 N·m; x̄ 12.1287, s 0.2854 vs 0.2806 (n); exercise 1 | `m01-ex1-torque.csv` | pass | pass | pass | pass | 01 |
| m01-anscombe-1 … -4 | 1 | simple linear regression (**real data**, S-C28 via S-E35, S-E36) | Anscombe's quartet; published shared properties checked: mean x 9, mean y 7.50, slope 0.500, intercept 3.00, r 0.816 (set 4 gives 0.8165), R² 0.67 | `m01-anscombe-N.csv` | pass (6 published values each) | pass | pass | pass | 01 |
| m07-bore | 7 | capability, X̄-R, 25 × 5 | reamed bore Ø12.000 ± 0.025 mm, bore micrometer to 0.001 mm; stable, normal, Cwk 1.06 / Ppk 1.04 with 95 % CI 0.90–1.18: the "not close enough" case | `m07-bore.csv` | pass | pass | pass | pass | 07, calculators |
| m07-bore-30 | 7 | capability, first 6 subgroups | the same process from 30 values: Ppk 1.07 with 95 % CI 0.77–1.37 | `m07-bore-30.csv` | pass | pass | pass | pass | 07 |
| m07-fill | 7 | capability, I-MR, one-sided | powder fill, declared minimum 250.0 g, 100 individuals; Ppl 0.75, 12,500 PPM predicted, 1 of 100 observed | `m07-fill.csv` | pass | pass | pass | pass | 07 |
| m07-cpm | 7 | capability, I-MR, off target | shoulder length 25.000 ± 0.030 mm, 50 individuals; Ppk 1.40 but Cpm 0.76 | `m07-cpm.csv` | pass | pass | pass | pass | 07 |
| m07-ex1-keyway | 7 | capability, X̄-R, 20 × 4 | keyway 6.000 +0.030/0 mm, stable, Cwk 0.97 / Ppk 0.94; exercise 1 | `m07-ex1-keyway.csv` | pass | pass | pass | pass | 07 |
| m07-ex2-wall | 7 | capability, X̄-R, 30 × 3, shift at 21 | die-cast wall 2.50 ± 0.15 mm; not stable (rule 1 at 22, 23, 26), Cwk 1.36 vs Ppk 0.95; exercise 2 | `m07-ex2-wall.csv` | pass | pass | pass | pass | 07 |
| m04-grr-bore | 4 (registered in Phase C) | crossed gauge R&R 10 × 3 × 3 | bore gauge, tolerance 0.050 mm; %GRR 23.9 % of study variation, 29.8 % of tolerance, ndc 5, interaction pooled (p 0.23) | `m04-grr-bore.csv` | pass | pass | pass | pass | calculators |
| m11-ttest2-pull | 11 (registered in Phase C) | two-sample t | solder pull strength N, suppliers A and B, 12 each; Welch p 0.010, d −1.16 | `m11-ttest2-pull.csv` | pass | pass | pass | pass | calculators |
| m11-anova-machines | 11 (registered in Phase C) | one-way ANOVA | cycle time s on three machines, 10 each; F 5.60, p 0.009, η² 0.29 | `m11-anova-machines.csv` | pass | pass | pass | pass | calculators |
| m02-redbead-theory | 2 | binomial and Poisson (parameters only) | red-bead paddle, n 50, p 0.20: mean 10.0, sd 2.83; P(=10) 0.1398, P(≤5) 0.0480, P(≤15) 0.9692 | none | pass | pass | pass | pass | 02 |
| m02-redbead-days | 2 | descriptive, 20 individuals | simulated red-bead counts, 5 workers × 4 rounds, Binomial(50, 0.20); mean 10.6, s 2.66, range 6 to 16, all within ±3 SD of the theoretical mean | `m02-redbead-days.csv` | pass | pass | pass | pass | 02 |
| m02-vsm-machining | 2 | value stream metrics (parameters only) | 4-step machining cell, demand 400/day, 27,000 s/day; takt 67.5 s, total lead time 3.8807 days, PCE 0.148 % | none | pass | pass | pass | n/a (no calculator) | 02 |
| m02-ex1-vsm | 2 | value stream metrics (parameters only) | 3-step assembly/test cell, demand 600/day; takt 42.0 s, lead time 1.5864 days, PCE 0.195 %; exercise 1 | none | pass | pass | pass | n/a (no calculator) | 02 |
| m02-funnel | 2 | funnel experiment, 4 rules, single 100-drop path | σ = 5.0 mm; Rule 1 var 19.35 mm², Rule 2 var 36.94 mm² (ratio 1.91 ≈ 2); Rules 3 and 4 shown for the trajectory figure only (a single path is too noisy to check their growth rate, see m02-funnel-growth) | `m02-funnel.csv` | pass | pass | pass | n/a (no calculator) | 02 |
| m02-funnel-growth | 2 | funnel experiment, 4 rules, 150 × 40-drop replications | Monte Carlo check of the Var(x_k) = k·σ² claim: mean square at drop 8 and drop 40 for each rule, all four within a factor of 2 of theory, Rules 3 and 4 growing roughly fivefold as theory predicts | `m02-funnel-growth.csv` | pass | pass | pass | n/a (no calculator) | 02 |
| m02-ex2-funnel | 2 | funnel experiment, rules 1 and 2, 30 drops | σ = 4.0 mm; Rule 1 var 12.70 mm², Rule 2 var 26.36 mm² (ratio 2.08 ≈ 2); exercise 2 | `m02-ex2-funnel.csv` | pass | pass | pass | n/a (no calculator) | 02 |

| m03-charter-leak | 3 | DPMO (parameters only) | capstone baseline: 42 of 1,000 brazed assemblies fail the leak test; DPU 0.042 (4.2 %), DPMO 42,000, sigma level (shifted) 3.23 | none | pass | pass | pass | pass | 03 |
| m03-charter-goal | 3 | DPMO (parameters only) | charter goal: 10 of 1,000 (1.0 %); DPU 0.01, DPMO 10,000, sigma level (shifted) 3.83 | none | pass | pass | pass | pass | 03 |
| m08-drift | 8 | capability, X̄-R, 25 × 5, tool-wear drift | shaft journal Ø20.000 ± 0.020 mm, micrometer to 0.001 mm; X̄ chart out of control (rule 1 at 1, 3, 4, 6, 22, 24, 25; rule 4 both sides), R chart clean; Cwk 1.37 vs Ppk 0.97, 19 vs 1,865 PPM: stability first | `m08-drift.csv` | pass | pass | pass | pass | 08 |
| m08-flatness | 8 | capability, non-normal (new kind `capability_nonnormal`), 200 individuals | the Module 1 flatness data against a 25 µm maximum: normal PpU 1.60 (0.8 PPM, x̄ − 3s = −2.8 µm); lognormal fit (AD p 0.98) PpU.G 0.93, Ppk.Z 0.96, 2,032 PPM; Box-Cox λ̂ 0.036 → 0.04, PpU 0.98, 1,652 PPM; empirical Cnpk 0.99; 1 of 200 observed out (5,000 PPM); raw I-MR chart flags 3 tail points, log-scale chart 1 | `m08-flatness.csv` | pass | pass | pass | n/a (no calculator fits distributions; see test_calculators.js header) | 08 |
| m08-leak | 8 | attribute capability (new kind `attribute_capability`), 24 lots | leak-test rejects, lots of 150 to 250: 110 of 4,856, p̂ 2.27 %, p chart stable, Wilson 95 % CI 1.88 to 2.72 %, exact 1.87 to 2.72 %, 22,652 DPMO, Z 2.00 (3.50 with the shift), n = 3,402 for ±0.5 points | `m08-leak.csv` | pass | pass | pass | n/a (DPMO converter covers the p-to-sigma step only) | 08 |
| m08-supplier | 8 | capability, I-MR, 30 individuals | ground pin Ø5.000 ± 0.012 mm from a tote: Ppk 1.38 with 95 % CI 1.00 to 1.75, chart order meaningless; the read-a-supplier-report example | `m08-supplier.csv` | pass | pass | pass | pass | 08 |
| m08-ex1-runout | 8 | capability, non-normal, 80 individuals | radial runout (Rayleigh-type), maximum 0.030 mm: normal PpU 1.47 (5 PPM); lognormal rejected (AD p 0.036, PpU.G 0.59); Box-Cox λ 0.4 (AD p 0.39) PpU 1.02, 1,127 PPM; empirical Cnpk 1.38; 0 of 80 out; exercise 1 | `m08-ex1-runout.csv` | pass | pass | pass | n/a | 08 |
| m08-ex2-paint | 8 | attribute capability, 20 lots | cosmetic rejects, 101 of 7,966, p̂ 1.27 %, stable, Wilson CI 1.04 to 1.54 %, 12,679 DPMO, Z 2.24; n = 3,006 for ±0.4 points; exercise 2 | `m08-ex2-paint.csv` | pass | pass | pass | n/a | 08 |
| m11-pull-a, m11-pull-b | 11 | descriptive, 12 each | the two supplier groups of m11-ttest2-pull separately: AD p 0.11 and 0.81 (normality check per group) | `m11-pull-a.csv`, `m11-pull-b.csv` | pass | pass | pass | pass | 11 |
| m11-paired-cycle | 11 | paired t, 12 pairs | cycle time before/after a fixture change: d̄ −1.29 s, t −4.24, p 0.0014, CI −1.96 to −0.62 s, d −1.22; the same data unpaired give p ≈ 0.4 | `m11-paired-cycle.csv` | pass | pass | pass | pass | 11 |
| m11-ttest1-torque | 11 | one-sample t, 30 | the Module 1 torque data vs 12.0 N·m: t 2.47, p 0.020, offset 0.13 N·m = 13 % of the half-tolerance; significant but small | `m11-ttest1-torque.csv` | pass | pass | pass | pass | 11 |
| m11-chisq-shift | 11 | chi-square independence (new kind `chisq`), 3 × 4 | defect type by shift, N 325: χ² 15.15, df 6, p 0.019, Cramér's V 0.15, min expected 12.3; gap defects 18/22/34 % by shift | `m11-chisq-shift.csv` | pass | pass | pass | n/a (no calculator) | 11 |
| m11-mw-flatness | 11 | Mann-Whitney U (new kind `mannwhitney`), 15 + 15 | flatness from two fixtures, lognormal: U 57, z 2.28, p 0.022, Hodges-Lehmann −3.1 µm, while Welch t gives p 0.13 | `m11-mw-flatness.csv` | pass | pass | pass | n/a (no calculator) | 11 |
| m11-power-pull | 11 | power (new kind `power`, parameters only) | δ 2.0 N, σ 2.65 N, n 12 per group: power 0.46 (normal approximation; noncentral t 0.42 as information); power curve for n = 4 to 60 | none | pass | pass | pass | n/a | 11 |
| m11-samplesize-pull | 11 | sample size (parameters only) | the same δ and σ at 80 % power: 27.6 → 28 (z), 29 (t-iteration) | none | pass | pass | pass | pass | 11 |
| m11-ex1-cure | 11 | two-sample t, 10 + 10 | adhesive cure time in two ovens: diff −0.64 min, Welch p 0.41, CI −2.24 to +0.96; n ≈ 22 per oven for 80 % power at 1.0 min; exercise 1 | `m11-ex1-cure.csv` | pass | pass | pass | pass | 11 |
| m11-ex2-chisq-leak | 11 | chi-square independence, 2 × 3 | leak location by fixture, N 112: χ² 1.50, p 0.47, V 0.12; no evidence; exercise 2 | `m11-ex2-chisq-leak.csv` | pass | pass | pass | n/a | 11 |
| m13-ofat | 13 | 2² factorial, 2 replicates | adhesive lap-shear strength, MPa: cell means (1) 15.5, a 11.65, b 13.55, ab 22.05; effects A 2.33, B 4.23, AB 6.18 (p 0.0001); the OFAT path from (1) rejects both factors and misses ab | `m13-ofat.csv` | pass | pass | pass | pass | 13 |
| m13-mould | 13 | 2³ factorial, 2 replicates | moulded housing length, mm, vs melt temperature, hold pressure, cooling time: A −0.080 (p 0.0002), B +0.0875 (p 0.0001), AB −0.050 (p 0.003), C and other interactions noise; residual sd 0.024 mm, R² 0.937; prediction equation and corner predictions | `m13-mould.csv` | pass | pass | pass | pass | 13, calculators (module page) |
| m13-plating | 13 | 2⁴⁻¹ half fraction (D = ABC), unreplicated | plating thickness, µm: A + BCD 5.875, D + ABC 8.825, others below Lenth's ME 1.27 (PSE 0.3375, SME 3.04); alias structure and resolution IV | `m13-plating.csv` | pass | pass | pass | pass | 13 |
| m13-ex1-weld | 13 | 2² factorial, 3 replicates | spot-weld nugget diameter, mm: A 0.615 (p 0.0001), B 0.318 (p 0.007), AB 0.022 (p 0.81); prediction 5.88 mm at both high vs a 5.6 mm minimum; exercise 1 | `m13-ex1-weld.csv` | pass | pass | pass | pass | 13 |
| m13-ex2-roughness | 13 | 2³ unreplicated | turned surface Ra, µm: A 0.79, B −0.45, AB 0.29 active by Lenth (ME 0.127), C and others noise; exercise 2 | `m13-ex2-roughness.csv` | pass | pass | pass | pass | 13 |
| m16-seal | 16 | X̄-S chart, 20 × 10 | heat-seal width, mm: x̄̄ 4.9954, S̄ 0.05506, limits 4.9417 to 5.0491, S chart 0.0156 to 0.0945; stable (Nelson 7 fires at 15–16 as a false alarm) | `m16-seal.csv` | pass | pass | pass | pass | 16 |
| m16-furnace, m16-furnace-clean | 16 | I-MR chart, 50 and 49 individuals | furnace zone temperature, °C: spike at reading 33 (615.7, 4.6σ above the mean) flagged by rule 1 and the MR chart; limits 606.84 to 613.84 on all 50, 607.08 to 613.39 after excluding the assigned cause | `m16-furnace.csv`, `m16-furnace-clean.csv` | pass | pass | pass | pass | 16 |
| m16-shift | 16 | I-MR chart, 50 individuals, 1σ shift at 26 | dispensed adhesive mass, mg: rule 1 never fires; rule 4 at 40 (and 49, 50), rules 2 and 3 at 50, Nelson 3 at 40–41, Nelson 4 false alarm at 14–16 before the shift; MR chart quiet | `m16-shift.csv` | pass | pass | pass | pass | 16 |
| m16-arl | 16 | ARL by Markov chain (new kind `arl`, parameters only) | rule sets {1}, {1,2}, {1,3}, {1,4}, {1–4} at shifts 0, 0.5, 1, 1.5, 2, 3σ: in control 370.40, 225.44, 166.05, 152.73, 91.75; at 1σ 43.9 vs 9.2; rule-1 column equals 1/p (published check 370.398); Monte Carlo in recompute.py agrees within 5 % | none | pass (1 published value) | pass (Monte Carlo, 20,000 in-control runs per set) | pass | n/a (static table; the detection simulator is the interactive counterpart) | 16 |
| m16-ex1-pin | 16 | X̄-R chart, 20 × 4 | pin length, mm: x̄̄ 29.9986, R̄ 0.03395, limits 29.9738 to 30.0233, UCL_R 0.0775; stable; exercise 1 | `m16-ex1-pin.csv` | pass | pass | pass | pass | 16 |
| m16-ex2-trend | 16 | I-MR chart, 30 individuals, linear drift | coolant concentration, %: MR-based σ̂ 0.148 vs overall s 0.328 (ratio 2.2); rules 2 and 3 at 3 and 5, rule 4 at 14, rule 1 at 26; MR chart quiet; exercise 2 | `m16-ex2-trend.csv` | pass | pass | pass | pass | 16 |
| m17-p-leak | 17 | p chart, 30 lots of 180–260 | leak-test rejects: p̄ 0.0417, rate 3.0 % for 20 lots then 6.6 %; rule 1 at lot 23, rules 2–4 later; lower limits all zero | `m17-p-leak.csv` | pass | pass | pass | pass | 17 |
| m17-np-connector, m17-u-solder | 17 | np chart (n 200, 25 samples); u chart (25 lots of 8–15 boards) | np̄ 8.24, UCL 16.67; ū 1.456 with limits moving with n (positive lower limits); both stable | `m17-np-connector.csv`, `m17-u-solder.csv` | pass | pass | pass | pass | 17 |
| m17-c-porosity | 17 | c chart, 30 castings | pores per radiograph: c̄ 5.00, UCL 11.71, casting 17 (14 pores) beyond | `m17-c-porosity.csv` | pass | pass | pass | pass | 17 |
| m17-pprime | 17 | Laney p′ (new kind `p_prime`), 25 days of 4,000–6,000 | p̄ 0.0194; classic p chart flags days 10, 11, 12, 13, 18, 21, 25; σ_z 2.42 (sd of daily p 2.7× binomial); p′ limits flag none, no runs rule on z | `m17-pprime.csv` | pass | pass | pass | n/a (hand computation; control chart builder draws the classic p chart) | 17 |
| m17-drift-imr, m17-drift-ewma, m17-drift-cusum | 17 | I-MR; EWMA λ 0.2 L 3 exact limits; tabular CUSUM k 0.5 h 4; baseline 30 of 60 | etch depth with a 0.7σ shift at 31: I chart rule 1 never fires (rules 2/3 false alarms at 21, 23); EWMA and CUSUM both signal at 38; CUSUM last zero at 34 | `m17-drift-imr.csv` (+ same rows) | pass | pass | pass | pass | 17 |
| m17-dnom | 17 | short-run DNOM (new kind `dnom`), 3 part numbers, 30 parts | deviations from 20.00/25.00/32.00 mm nominals: σ̂ 0.0111, limits ±0.033 mm, rule 3 at part 15; per-part sd ratio 1.10 | `m17-dnom.csv` | pass | pass | pass | n/a (I-MR of pasted deviations in the builder) | 17 |
| m17-flatness-imr, m17-flatness-log-imr | 17 | I-MR, 200 individuals, raw and ln x | the Module 1 flatness data: raw chart 3 of 200 beyond (1.5 %, 6× the normal rate), runs at 121–137; log chart 1 beyond, same runs | `m17-flatness-imr.csv`, `m17-flatness-log-imr.csv` | pass | pass | pass | pass | 17 |
| m17-ex1-u-braze | 17 | u chart, 20 cores of 40–80 joints | ū 0.0385 defects per joint; core 12 (9 on 78) beyond its limit 0.105; exercise 1 | `m17-ex1-u-braze.csv` | pass | pass | pass | pass | 17 |
| m17-ex2-imr, m17-ex2-ewma | 17 | I-MR; EWMA λ 0.2 L 3, baseline 20 of 40 | plating thickness with a 0.5σ shift at 21: I chart silent (two MR points), EWMA signals at 31; exercise 2 | `m17-ex2-imr.csv` | pass | pass | pass | pass | 17 |
| m19-leak-baseline | 19 | attribute capability, 30 lots of 150–250 | capstone baseline leak rate: 259 of 6,037, p̂ 4.29 % (Wilson 3.81–4.83 %), 42,902 DPMO, Z 1.72; p chart stable (Nelson 3 once, a false alarm); n 6,310 for ±0.5 points | `m19-leak-baseline.csv` | pass | pass | pass | n/a | 19 |
| m19-pareto | 19 | Pareto table (new kind `pareto`) | leak locations of the 259 leakers: header joint 168 (64.9 %), first two categories 80.7 % | `m19-pareto.csv` | pass | pass | pass | n/a (arithmetic on printed counts) | 19 |
| m19-grr | 19 | crossed gauge R&R 10 × 3 × 2 | gap pin-gauge, tolerance 0.10 mm: interaction pooled (p 0.99), operators differ (p 0.0005); %R&R 12.1 % of study variation, 18.1 % of tolerance, ndc 11 | `m19-grr.csv` | pass | pass | pass | pass | 19 |
| m19-gap-baseline | 19 | capability, X̄-R, 25 × 5 | joint gap 0.10 ± 0.05 mm: stable, AD p 0.91, mean 0.1124, s 0.0141, Cpk 0.89 (CI 0.76–1.01), Cwk 0.85, 3,938 PPM predicted, 0 of 125 out; 2.7 % of core means above the 0.14 mm bridging limit | `m19-gap-baseline.csv` | pass | pass | pass | pass | 19 |
| m19-furnace | 19 | I-MR, 40 individuals | furnace peak temperature: x̄ 599.83 °C, σ̂ 1.87, limits 594.22–605.44, stable, no rule | `m19-furnace.csv` | pass | pass | pass | pass | 19 |
| m19-gap-leakers | 19 | two-sample t, 20 + 20 | header-joint gap on sectioned leakers vs passers: 0.1364 vs 0.1109 mm, diff 0.0255 (CI 0.0174–0.0336), Welch t 6.37, p 2e-7, d 2.01 | `m19-gap-leakers.csv` | pass | pass | pass | pass | 19 |
| m19-doe | 19 | 2³ factorial, 2 replicates | clamp (A), expansion (B), furnace (C) → mean gap: B −0.0239 (p 2e-5), A −0.0126 (p 0.002), AB +0.0071 (p 0.03), C nil; residual sd 0.0054; prediction at ab 0.0982 mm | `m19-doe.csv` | pass | pass | pass | pass | 19 |
| m19-gap-after | 19 | capability, X̄-R, 25 × 5 | after the mandrel change: stable, mean 0.1003, s 0.0093, Cpk 1.79 (CI 1.56–2.02), Cwk 1.71, 0.07 PPM | `m19-gap-after.csv` | pass | pass | pass | pass | 19 |
| m19-leak-after | 19 | attribute capability, 30 lots | 49 of 6,037, p̂ 0.81 % (Wilson 0.61–1.07 %), 8,117 DPMO; stable by rule 1 (one rule-2 flag) | `m19-leak-after.csv` | pass | pass | pass | n/a | 19 |
| m19-before-after | 19 | chi-square 2 × 2 | 259/5,778 vs 49/5,988: χ² 146.9, p ≈ 0, reduction 3.48 points (CI 2.92–4.04), factor 5.3 | `m19-before-after.csv` | pass | pass | pass | n/a | 19 |

| m04-grr-bore | 4 | crossed gauge R&R 10 × 3 × 3 (registered Phase C) | bore gauge, tolerance 0.050 mm; %GRR 23.9 % of study variation, 29.8 % of tolerance, ndc 5, interaction pooled (p 0.229) | `m04-grr-bore.csv` | pass | pass | pass | pass | 04, calculators |
| m04-grr-scale | 4 | crossed gauge R&R 10 × 3 × 3 | checkweigher, tolerance 6.0 g; %GRR 7.0 % of study variation, 11.4 % of tolerance, ndc 20, interaction pooled (p 0.162): the "good gauge" contrast to the bore gauge | `m04-grr-scale.csv` | pass | pass | pass | pass | 04 |
| m04-bias | 4 | one-sample t (new use of `ttest1`) | bore gauge on a 12.010 mm reference, 15 readings: bias +0.0028 mm, t 7.61, p < 0.001 | `m04-bias.csv` | pass | pass | pass | pass | 04 |
| m04-linearity | 4 | simple regression (new use of `regression`) | bore gauge, 5 reference levels × 4 replicates: bias vs reference slope 0.1225 (p < 0.001), R² 0.823 | `m04-linearity.csv` | pass | pass | pass | pass | 04 |
| m04-stability | 4 | I-MR (new use of `imr`) | bore gauge, 12.010 mm reference, 24 shifts: stable, no rule fired | `m04-stability.csv` | pass | pass | pass | pass | 04 |
| m04-attribute-braze | 4 | attribute agreement (new kind `attribute_agreement`) | 3 inspectors × 30 parts × 2 trials on braze fillet appearance: Fleiss' κ 0.626 (substantial), per-inspector Cohen's κ vs standard 0.645–0.772, overall effectiveness 85 % | `m04-attribute-braze.csv` | pass | pass | pass | n/a (no calculator fits; SKIP_KIND) | 04 |
| m04-ex1-bias | 4 | one-sample t | keyway caliper on a 6.015 mm reference, 12 readings: bias −0.0053 mm (17.7 % of the 0.030 mm tolerance), t −9.61, p < 0.001; exercise 1 | `m04-ex1-bias.csv` | pass | pass | pass | pass | 04 |
| m04-ex2-attribute | 4 | attribute agreement | 2 inspectors × 20 parts × 2 trials: Fleiss' κ 0.560 (moderate), within-inspector repeatability 0.90 / 0.80; exercise 2 | `m04-ex2-attribute.csv` | pass | pass | pass | n/a (no calculator fits) | 04 |

| m05-subgroup-naive | 5 | capability, X̄-R, 20 × 5 (new use, no new kind) | two-cavity mould, consecutive-order subgrouping mixes both cavities: R̄ 0.0163 mm, σ̂ 0.0070, stable (falsely reassuring) | `m05-subgroup-naive.csv` | pass | pass | pass | pass | 05 |
| m05-subgroup-rational | 5 | capability, X̄-R, 20 × 5 | the identical 100 values, regrouped one cavity per subgroup: R̄ 0.0106 mm (35 % smaller), not stable — WE1 at 2/3/7, WE4 (8 in a row) at both cavity blocks — correctly reveals the 0.010 mm cavity difference | `m05-subgroup-rational.csv` | pass | pass | pass | pass | 05 |
| m05-rounding-fine, m05-rounding-coarse | 5 | descriptive (new use) | the same 80 readings at 0.001 mm vs 0.01 mm resolution: s 0.00677 → 0.00763 mm (13 % inflation), 80 → 5 distinct values | `m05-rounding-fine.csv`, `m05-rounding-coarse.csv` | pass | pass | pass | pass | 05 |
| m05-ex1-naive, m05-ex1-rational | 5 | capability, X̄-R, 8 × 5 | two-lathe exercise, smaller scale: R̄ 0.0328 → 0.0196 mm, stable → not stable; exercise 1 | `m05-ex1-naive.csv`, `m05-ex1-rational.csv` | pass | pass | pass | pass | 05 |

| m06-dpmo-connector | 6 | DPMO (parameters only) | connector, 54 defects / 2,400 units / 5 opportunities: DPU 0.0225, DPMO 4,500, sigma level (shifted) 4.11 | none | pass | pass | pass | pass | 06 |
| m06-gaming-op1, m06-gaming-op10 | 6 | DPMO (parameters only) | the identical 54/2,400 recounted at 1 and 10 opportunities per unit: DPMO 22,500 → 2,250 (exactly 10×), sigma level 3.50 → 4.34, no real process change | none | pass | pass | pass | pass | 06 |
| m06-rty-chain | 6 | RTY of a chain (new kind `rty_chain`) | 5-step wire-harness line, yields 98/95/99/97/98.5 %: RTY 88.06 %, normalised yield 97.49 %, total DPU 0.1271 | none | pass | pass | pass | pass | 06, calculators |
| m06-sigma-table | 6 | sigma table (new use of `sigma_table`) | half-sigma steps 1 to 6, both conventions; k=6 centred 0.0020 PPM vs shifted one-sided 3.4 PPM (the Motorola target, checked) | none | pass (1 published value) | pass | pass | pass | 06 |
| m06-ex1-rty | 6 | RTY of a chain | 4-step board line, yields 99.5/96/98/99 %: RTY 92.67 %, normalised 98.12 %; exercise 1 | none | pass | pass | pass | pass | 06 |
| m06-ex2-dpmo | 6 | DPMO (parameters only) | leak test, 33 defects / 3,000 units / 2 opportunities: DPU 0.011, DPMO 5,500, sigma level 4.04; exercise 2 | none | pass | pass | pass | pass | 06 |

| m09-pareto-leak | 9 | Pareto (existing kind, first use in this module) | 169 leak-test rejects, 6 causes: header joint 87 (51.5 %), top 3 reach 84.0 %, n_for_80pct = 3 | none | pass | pass | pass | n/a (no calculator) | 09 |
| m09-multivari-braze | 9 | multi-vari (new kind `multivari`) | braze fillet width, 5×4×3 design: positional 14.0 %, cyclical 21.0 %, temporal 65.0 % of σ̂ — temporal (a furnace trend) dominant | `m09-multivari-braze.csv` | pass | pass | pass | n/a (no calculator) | 09 |
| m09-boxplot-shift1/2/3 | 9 | descriptive (new use, box plot) | bore diameter by shift, 30 each: shift 3 median 12.0085 vs shift 1's 11.9995 mm, s 0.0091 vs 0.0064; shift 3 max 12.028 mm exceeds the 12.020 mm USL | `m09-boxplot-shift1.csv` etc. | pass | pass | pass | pass | 09 |
| m09-ex1-pareto | 9 | Pareto | 112 assembly defects, 5 causes; top 3 reach 87.5 %; exercise 1 | none | pass | pass | pass | n/a | 09 |
| m09-ex2-multivari | 9 | multi-vari | 3×3×3 design, positional dominant this time (62.2 % vs 31.9 % cyclical, 5.8 % temporal) — the contrasting case to the main example; exercise 2 | `m09-ex2-multivari.csv` | pass | pass | pass | n/a | 09 |

The published check example `chk-nist-capability` (NIST 6.1.6) is also declared on the Module 7 page as the reproduced textbook check, and `chk-montgomery-etch` (Montgomery plasma etch 2³) is the preload of the factorial calculator on `calculators.html`.

| m10-pfmea-braze | 10 | RPN (new kind `rpn`) | PFMEA excerpt, furnace-braze, 7 failure modes: RPN 210 down to 18, total 754; "wrong braze alloy used" has S=9 (tied highest) but ranks last on RPN (18) — the Action Priority argument on real numbers | `m10-pfmea-braze.csv` | pass | pass | pass | n/a (no calculator) | 10 |
| m10-fault-tree-leak | 10 | fault tree (new kind `fault_tree`) | 4-level AND/OR tree, leak escapes undetected: top probability 0.412 %, vs the 4.2 % reject rate the test catches (Module 3); joint-leaks branch 4.24 %, test-miss basic event 5 % | none | pass | pass | pass | n/a | 10 |
| m10-ex1-pfmea | 10 | RPN | connector assembly, 5 failure modes; same S-high/RPN-low pattern as the main example; exercise 1 | `m10-ex1-pfmea.csv` | pass | pass | pass | n/a | 10 |
| m10-ex2-fault-tree | 10 | fault tree | wire-harness continuity escape, 2-level tree: top probability 0.130 %; exercise 2 | none | pass | pass | pass | n/a | 10 |

Totals on 2026-09-10 (after Module 10, both sessions combined): 142 examples; 3,860 quantities agree between Check 1 and Check 2; 8,211 values agree between Check 1 and the JavaScript engines (112 examples with a calculator engine); 1,314 page checks.
