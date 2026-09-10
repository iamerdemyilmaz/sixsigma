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

Constructed course examples (prefix `m<NN>-`). Each is labelled "constructed data, not a real production run" where it appears. The ids replace the planning ids in SOURCES.md Part 2 (`ex07-bore-capability` → `m07-bore`, and so on). All checks passed on 2026-09-09 (`verify_all.sh`: 34 examples, 1,119 quantities agree between Check 1 and Check 2, 2,960 values agree between Check 1 and the JavaScript engines, 100 page checks).

| id | Module | Kind | Setting and the point it makes | Dataset | Check 1 | Check 2 | Check 3 | Check 4 | Pages |
|---|---|---|---|---|---|---|---|---|---|
| m07-bore | 7 | capability, X̄-R, 25 × 5 | reamed bore Ø12.000 ± 0.025 mm, bore micrometer to 0.001 mm; stable, normal, Cwk 1.06 / Ppk 1.04 with 95 % CI 0.90–1.18: the "not close enough" case | `m07-bore.csv` | pass | pass | pass | pass | 07, calculators |
| m07-bore-30 | 7 | capability, first 6 subgroups | the same process from 30 values: Ppk 1.07 with 95 % CI 0.77–1.37 | `m07-bore-30.csv` | pass | pass | pass | pass | 07 |
| m07-fill | 7 | capability, I-MR, one-sided | powder fill, declared minimum 250.0 g, 100 individuals; Ppl 0.75, 12,500 PPM predicted, 1 of 100 observed | `m07-fill.csv` | pass | pass | pass | pass | 07 |
| m07-cpm | 7 | capability, I-MR, off target | shoulder length 25.000 ± 0.030 mm, 50 individuals; Ppk 1.40 but Cpm 0.76 | `m07-cpm.csv` | pass | pass | pass | pass | 07 |
| m07-ex1-keyway | 7 | capability, X̄-R, 20 × 4 | keyway 6.000 +0.030/0 mm, stable, Cwk 0.97 / Ppk 0.94; exercise 1 | `m07-ex1-keyway.csv` | pass | pass | pass | pass | 07 |
| m07-ex2-wall | 7 | capability, X̄-R, 30 × 3, shift at 21 | die-cast wall 2.50 ± 0.15 mm; not stable (rule 1 at 22, 23, 26), Cwk 1.36 vs Ppk 0.95; exercise 2 | `m07-ex2-wall.csv` | pass | pass | pass | pass | 07 |
| m04-grr-bore | 4 (registered in Phase C) | crossed gauge R&R 10 × 3 × 3 | bore gauge, tolerance 0.050 mm; %GRR 23.9 % of study variation, 29.8 % of tolerance, ndc 5, interaction pooled (p 0.23) | `m04-grr-bore.csv` | pass | pass | pass | pass | calculators |
| m11-ttest2-pull | 11 (registered in Phase C) | two-sample t | solder pull strength N, suppliers A and B, 12 each; Welch p 0.010, d −1.16 | `m11-ttest2-pull.csv` | pass | pass | pass | pass | calculators |
| m11-anova-machines | 11 (registered in Phase C) | one-way ANOVA | cycle time s on three machines, 10 each; F 5.60, p 0.009, η² 0.29 | `m11-anova-machines.csv` | pass | pass | pass | pass | calculators |

The published check example `chk-nist-capability` (NIST 6.1.6) is also declared on the Module 7 page as the reproduced textbook check, and `chk-montgomery-etch` (Montgomery plasma etch 2³) is the preload of the factorial calculator on `calculators.html`.
