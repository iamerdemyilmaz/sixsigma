# SOURCES.md

Master source register for "Six Sigma for Engineers: Process Capability, SPC, and DMAIC in Practice".
Phase A, research and outline. All entries accessed 2026-09-09 unless noted.

## How to read this file

**Status** (per CLAUDE.md rule 1):

- **verified**: I read it (full text, abstract, or official catalog/scope page) and it says what the course will claim from it. The **Depth** column says how much was read: `full`, `abstract`, `scope` (a standard's public scope and table of contents), or `catalog` (publisher or library record confirming bibliographic facts and subject only).
- **secondary**: cited by a credible source I read; the original was not read. Must be labelled "secondary" in module References.
- **unverified**: may not appear in the course.

**Rule applied to `catalog` depth:** a source read only at catalog depth may support bibliographic facts and the general statement that the work covers a topic. Any specific number, method detail, or quotation attributed to it is treated as **secondary** unless another verified source carries the claim. The "Supports" column is the whitelist of what each entry may be cited for.

Publisher pages at tandfonline.com, iso.org, asq.org, and link.springer.com returned HTTP 403 to automated fetches during this session. Where that happened, abstracts were read via the publisher's listing text, Semantic Scholar, ProQuest, or open mirrors, and the depth column reflects what was actually read.

---

## Part 1. Master source list

### A. Standards, reference manuals, and bodies of knowledge

| ID | Citation | URL | Status | Depth | Supports |
|---|---|---|---|---|---|
| S-A1 | AIAG. *Manuals catalog* (lists SPCAV-1 "AIAG & VDA SPC Manual", published July 2026; MSA-4 "Measurement Systems Analysis", 4th ed., June 2010; PPAP-4 "Production Part Approval Process", 4th ed., Nov 2009 printing; APQP-3, 3rd ed., March 2024; CP-1 "Control Plan", 1st ed., March 2024; FMEAAV-1 "AIAG & VDA FMEA Handbook", Aug 2022 printing). Automotive Industry Action Group. | https://www.aiag.org/training-and-resources/manuals | verified | catalog | Correct designations and editions of every AIAG core-tool manual cited in the course. |
| S-A2 | AIAG & VDA. *Statistical Process Control (SPC) Manual: Process Management, Performance and Capability, Control Charts*, 1st ed., February 2026 (VDA QMC "Yellow Volume" online download edition; AIAG catalog lists the July 2026 printing as SPCAV-1). 144 pp. Author's licensed copy in `reference/AIAG-VDA-SPC-Yellow-Volume.pdf` (permission-protected; not redistributed). | https://vda-qmc.de/en/publikationen-und-apps/gelbbaende/ ; https://www.aiag.org/training-and-resources/manuals/details/SPCAV-1 | verified | full (targeted sections read 2026-09-09: 6.2.3, 6.3, 7.2–7.5, 7.6–7.8, 8.3–8.4, 9.3–9.5, 10.2, 10.3.2, 10.4; TOC) | **Definitions (7.2, p.33; 7.4, p.38; 7.8.2.1, pp.46–47):** P (performance) and C (capability) indices use the *same formula on total variation*; the letter indicates only whether stability was proven. Cp/Cpk "must only be used if the process is stable"; otherwise Pp/Ppk. **Within-subgroup index (7.8.2.5, pp.51–52):** the R̄/d₂ or S̄/c₄ index is named Cw/Cwk; footnote 11: "In AIAG SPC 2nd edition the Cwk was referred to as Cpk"; Cwk is an analysis tool and "should not be used for reporting purposes"; a large Cwk vs Ppk gap signals between-subgroup variation. **Two calculation methods (7.8.2, pp.45–51):** General Geometric (ISO 22514/3534 quantile method, subscript G, X0.135 %, X50 %, X99.865 %) and z-Score/Bothe exceedance method (subscript Z); identical for normal data. **Sample sizes (7.4, p.38; Table 7-4, p.44):** n ≥ 125 in k ≥ 25 subgroups of 5 for process studies; n = 50–100 consecutive parts for machine performance Pm/Pmk (8.2.1). **Targets (Table 9-3, p.75; Table 8-1, p.58):** examples by characteristic class, e.g. process Cp/Cpk or Pp/Ppk ≥ 1.67 critical, 1.33 major, 1.00 minor; preliminary Pp/Ppk 2.00/1.67 critical, 1.67/1.33 major at n ≥ 125, adjusted upward for smaller n; stated as examples, targets are customer agreements (p.76). **Stability (10.2.2, pp.80–81):** five rules listed (beyond ±3s; 2 of 3 beyond 2s; 4 of 5 beyond 1s; run of nine; 15 within 1s) with a caution that each added rule raises Type I error. **"Controlled stable" vs "statistically stable" (9.4, p.75):** Cp/Cpk may be used for controlled-stable processes that are not in statistical control, under stated conditions. **ISO 22514-2 time-dependent models A1, A2, B, C1–C4, D (9.4, pp.67–74; Table 10-2, p.130).** **Non-normal (7.8.1, p.45; 10.3.2.6, p.90):** choose the distribution from process knowledge, folded distributions for form tolerances, Box-Cox/Johnson allowed with back-transformation; **one-sided natural limits (7.8.2.2, pp.48–49):** Cpk may exceed Cp; compute Cp for information without a target. **Control vs tolerance limits (7.5, p.39):** "the tolerance limits are thus not included in quality control charts". **MSA prerequisite (6.3, p.26; p.34; 9.3, p.67).** **Outliers (7.6, p.43):** never deleted, marked invalid with documented cause. **ARL and OC (10.2.4, pp.82–84).** **Chart selection (10.3.2, pp.86–91)** including memory charts (CUSUM, EWMA), Pearson and extended Shewhart charts for non-normal data, short-run Z-MR. |
| S-A3 | AIAG. *Statistical Process Control (SPC) Reference Manual*, 2nd ed., 2005. | (superseded by S-A2) | secondary | – | Historical prior edition; the source of the convention still used by most software and supplier reports, in which Cpk is computed from within-subgroup sigma (R̄/d₂) and Ppk from overall sigma. That this was the 2005 convention is **verified** via S-A2 footnote 11 (p.51). Cite as "superseded by S-A2". |
| S-A4 | AIAG. *Measurement Systems Analysis (MSA) Reference Manual*, 4th ed., June 2010. | https://www.aiag.org/training-and-resources/manuals/details/MSA-4 | verified | catalog | Existence, edition, scope (gauge R&R, bias, linearity, stability, attribute studies). The %GRR thresholds (<10 / 10–30 / >30 %) and ndc ≥ 5 are **secondary** (confirmed by S-E14, S-E16) and must be cited as guidelines. |
| S-A5 | AIAG. *Production Part Approval Process (PPAP)*, 4th ed., 2006 (Nov 2009 printing). | https://www.aiag.org/training-and-resources/manuals/details/PPAP-4 | verified | catalog | Existence and edition. The initial-study acceptance bands (>1.67 acceptable; 1.33–1.67 may be acceptable; <1.33 not) are **secondary** (S-E15) until the author confirms against the manual. |
| S-A6 | AIAG. *Control Plan*, 1st ed., March 2024. | https://www.aiag.org/training-and-resources/manuals/details/CP-1 | verified | catalog | Standalone control plan manual; clarifies linkages to APQP; adds a "Safe Launch" phase; guidance for automated manufacturing and software-managed control plans; revised forms and checklists. |
| S-A7 | AIAG. *Advanced Product Quality Planning (APQP)*, 3rd ed., March 2024. | https://www.aiag.org/training-and-resources/manuals | verified | catalog | Existence and edition; control plan now separate (S-A6). |
| S-A8 | AIAG & VDA. *FMEA Handbook*, 1st ed., June 2019; 2nd printing with errata Aug 2022. | https://www.aiag.org/training-and-resources/manuals/details/FMEAAV-1 | verified | catalog | Existence, edition, printing history; seven-step approach; Action Priority (AP) replaces RPN for prioritization. AP-table specifics are **secondary** (S-E17). |
| S-A9 | ISO 22514-1:2014. *Statistical methods in process management — Capability and performance — Part 1: General principles and concepts*. ISO. | https://cdn.standards.iteh.ai/samples/64135/dbf61853327948a6a0c292b5f57cc6f5/ISO-22514-1-2014.pdf | verified | scope | Definitions and structure of the ISO 22514 series; the series parts (2, 3, 4, 6, 7, 8); "six different types of performance and capability"; a capability study starts as a performance study. |
| S-A10 | ISO 22514-2:2026. *…Part 2: Process capability and performance of time-dependent process models*, 3rd ed., Feb 2026 (replaces ISO 22514-2:2017). | https://www.dinmedia.de/en/standard/iso-22514-2/400044429 | verified | catalog | Current edition and date; eight time-dependent distribution models; explicitly extends methods to processes not always in statistical control (the nuance for the stability controversy). |
| S-A11 | ISO 22514-7:2021. *…Part 7: Capability of measurement processes*. | https://www.iso.org/standard/80624.html (403; listed in S-A9) | secondary | – | Existence as the ISO measurement-capability counterpart to AIAG MSA. |
| S-A12 | ISO/TR 22514-9:2023. *…Part 9: Process capability statistics for characteristics defined by geometrical specifications*. | https://www.iso.org/standard/69643.html (403; search listing) | secondary | – | Existence; relevant to bounded characteristics (flatness, runout) in Module 8. |
| S-A13 | ISO 7870-2:2023. *Control charts — Part 2: Shewhart control charts*, 2nd ed., 14 March 2023 (replaces 2013). | https://www.evs.ee/en/iso-7870-2-2023 | verified | catalog | Current edition; scope: Shewhart charts, warning limits, trend patterns, brief capability. |
| S-A14 | ISO 7870-4:2021. *Control charts — Part 4: Cumulative sum charts*. | https://www.iso.org/standard/74101.html (403; search listing) | secondary | – | Existence and scope (CUSUM for variables and attributes). |
| S-A15 | ISO 7870-6:2016. *Control charts — Part 6: EWMA control charts*. | https://www.iso.org/standard/40173.html (403; search listing) | secondary | – | Existence and scope. |
| S-A16 | ISO 7870-8:2017. *Control charts — Part 8: Charting techniques for short runs and small mixed batches*. | https://cdn.standards.iteh.ai/samples/67410/0471b1bd8dc9472aaa07c7ce99c3249a/ISO-7870-8-2017.pdf | verified | scope | Existence, structure; pre-established limits and deviation-from-nominal techniques are standardized. |
| S-A17 | ISO 3534-2:2006. *Statistics — Vocabulary and symbols — Part 2: Applied statistics*. | https://www.iso.org/standard/40147.html (403; search listing) | secondary | – | Vocabulary source referenced by ISO 22514-1 (S-A9). |
| S-A18 | ASTM E2281-15(2020). *Standard Practice for Process Capability and Performance Measurement*. ASTM International. | https://www.astm.org/Standards/E2281.htm (403; ANSI webstore listing read) | secondary | – | Existence, current designation, scope (Cp, Cpk, Pp, Ppk, attribute capability). |
| S-A19 | IATF 16949:2016. *Quality management system requirements for automotive production and relevant service parts organizations*. IATF. Clause 9.1.1.1 summarized via S-E18. | (standard not online) | secondary | – | Requirement for process studies on new processes, capability verification, reaction plans when unstable or not capable, recording significant process events. |
| S-A20 | ASME Y14.5-2018. *Dimensioning and Tolerancing*. ASME. | https://www.asme.org/codes-standards/find-codes-standards/y14-5-dimensioning-tolerancing/2018 | verified | catalog | Existence and edition. Statistical tolerancing symbol details are **secondary**. |
| S-A21 | ASQ. *Certified Six Sigma Green Belt (CSSGB) Body of Knowledge Map 2014–2022*. ASQ, 2022. | https://www.asq.org/cert/resource/pdf/certification/2022-CSSGB-BoK-Map.pdf | verified | full | What a Green Belt is expected to know: six sections; Measure includes MSA (GR&R, bias, linearity, P/T), capability studies "verifying stability and normality", Cp/Cpk vs Pp/Ppk, Cpm, sigma level, short- vs long-term and sigma shift; Analyze includes multi-vari, correlation/regression, hypothesis tests, root cause (5 Whys, fault tree); Improve includes DOE; Control includes SPC. Justifies the "not a certification course, but covers the BoK" statement. |
| S-A22 | NASA. *Fault Tree Handbook with Aerospace Applications*, Version 1.1 (Vesely, Stamatelatos et al.), Aug 2002. | https://s3vi.ndc.nasa.gov/ssri-kb/static/resources/Fault%20Tree%20Handbook_NASA.pdf | verified | catalog | Public-domain handbook defining FTA as a deductive, top-down method; update of the 1981 handbook. |
| S-A23 | Western Electric Co. *Statistical Quality Control Handbook*, 1st ed. Indianapolis, 1956. | (out of print; rules confirmed via S-E19) | secondary | – | Origin of the four zone rules (1 beyond 3σ; 2 of 3 beyond 2σ; 4 of 5 beyond 1σ; 8 in a row one side). |

### B. NIST/SEMATECH e-Handbook of Statistical Methods (NIST, public domain)

| ID | Section | URL | Status | Depth | Supports |
|---|---|---|---|---|---|
| S-B0 | NIST/SEMATECH. *e-Handbook of Statistical Methods*. NIST, 2012 (updated). | https://www.itl.nist.gov/div898/handbook/ | verified | catalog | Master citation for all NIST sections. |
| S-B1 | 6.1.6 What is Process Capability? | https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm | verified | full | Cp, Cpk, Cpm definitions and estimators; capability is for an *in-control* process; normality assumption; about 50 values "large enough", n ≥ 100 preferred for capability studies; approximate CI on Cpk: Ĉpk ± z·√[1/(9n) + Ĉpk²/(2(n−1))]; worked example USL 20, LSL 8, x̄ 16, s 2 → Cp 1.0, Cpk 0.667, Cpu 0.667, Cpl 1.333; Box-Cox and nonparametric Cnp/Cnpk for non-normal data. Textbook check example for Phase B. |
| S-B2 | 6.3.2.1 Shewhart X-bar and R and S Control Charts | https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc321.htm | verified | full | X̄-R and X̄-S formulas; A2, D3, D4 table (n=2: 1.880, 0, 3.267 … n=10: 0.308, 0.223, 1.777); range method satisfactory up to n≈10, use S beyond. Phase B constant check. |
| S-B3 | 6.3.2.2 Individuals Control Charts | https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc322.htm | verified | full | I-MR chart; MR = |xᵢ − xᵢ₋₁|; limits x̄ ± 3·MR̄/1.128; worked example (10 batches, x̄ 50.81, MR̄ 1.8778, UCL 55.80, LCL 45.82). Phase B check example. |
| S-B4 | 6.3.2.4 EWMA Control Charts | https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm | verified | full | EWMAₜ = λYₜ + (1−λ)EWMAₜ₋₁; λ typically 0.2–0.3; s²ewma = λ/(2−λ)·s²; example EWMA₀ 50, s 2.0539, λ 0.3 → UCL 52.59, LCL 47.41. Phase B check example. |
| S-B5 | 6.3.3 Attributes Control Charts (overview and subsections) | https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc33.htm | verified | full (overview) | p, np, c, u chart purposes; formulas in subsections pmc331–pmc333 to be read in Phase B. |
| S-B6 | 2.4 Gauge R&R Studies; 2.4.4 Analysis of Variability | https://www.itl.nist.gov/div898/handbook/mpc/section4/mpc4.htm ; https://www.itl.nist.gov/div898/handbook/mpc/section4/mpc44.htm | verified | full | Study design (artifacts, operators, gauges); repeatability, reproducibility, stability as nested levels; formulas for level-1/2/3 standard deviations and combined uncertainty. Complements AIAG MSA. |
| S-B7 | 5.3.3 How do you select an experimental design? | https://www.itl.nist.gov/div898/handbook/pri/section3/pri33.htm | verified | full | Design selection by objective and number of factors; full or fractional factorial for 2–4 factors; fractional or Plackett-Burman for 5+; keep runs below budget for centre points. Sub-pages pri333/pri334 to be read in Phase B. |
| S-B8 | 7.2.2.2 Sample sizes required | https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm | verified | full | N = (z₁₋α/₂ + z₁₋β)²(σ/δ)² (two-sided), t-based iterative version; example α 0.05, β 0.10, δ = σ → N ≈ 9 (z) → 11 (t). Phase B check example. |
| S-B9 | 7.2.2 Are the data consistent with the assumed process mean? | https://www.itl.nist.gov/div898/handbook/prc/section2/prc22.htm | verified | full | One-sample t and z test logic and worked example (t = 1.782). |
| S-B10 | 1.3.6.6.1 Normal Distribution | https://www.itl.nist.gov/div898/handbook/eda/section3/eda3661.htm | verified | full | pdf, standard normal, no closed-form CDF, CLT statement (sampling distribution of the mean tends to normal with sd σ/√N). |
| S-B11 | 8.1.6 Basic lifetime distribution models for non-repairable populations | https://www.itl.nist.gov/div898/handbook/apr/section1/apr16.htm | verified | full | Exponential, Weibull, extreme value, lognormal, gamma, Birnbaum-Saunders, proportional hazards as engineering distributions. |
| S-B12 | 4.4.4 How can I tell if a model fits my data? | https://www.itl.nist.gov/div898/handbook/pmd/section4/pmd44.htm | verified | full | Graphical residual analysis is primary; checks functional form, constant variance, drift, independence, normality; "a high R² value does not guarantee that the model fits the data well". |
| S-B13 | 6.3.2.3 CUSUM Control Charts; 6.3.2.3.1 CUSUM Average Run Length | https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm | verified | full (2026-09-09, Phase B) | Tabular CUSUM: S_hi(i) = max(0, S_hi(i−1) + x_i − μ̂₀ − k), S_lo(i) = max(0, S_lo(i−1) + μ̂₀ − k − x_i); signal when either exceeds h; rule of thumb k = δ/2 (in σ units), h ≈ 4 or 5; worked example μ̂₀ 325, h 4.1959, k 0.3175 signals at point 14. Implemented in compute.py, recompute.py and stats.js in standardized units. |
| S-B14 | 1.3.6.7.2 Critical Values of the Student's t Distribution | https://www.itl.nist.gov/div898/handbook/eda/section3/eda3672.htm | verified | full | Upper one-sided critical values; sampled entries (df 10: 1.812, 2.228; df 20: 2.086; df 5 at 0.005: 4.032; df 30: 1.697; df 1: 12.706) used as the published check in tables.py. |
| S-B15 | 1.3.6.7.3 Upper Critical Values of the F Distribution | https://www.itl.nist.gov/div898/handbook/eda/section3/eda3673.htm | verified | full | 5 % entries (2,20) 3.493, (3,30) 2.922, (10,10) 2.978, (4,15) 3.056 confirmed on the page; (1,10) 4.965 and (5,10) 3.326 taken from Montgomery App. IV because the page reader transposed those cells. Checked in tables.py. |
| S-B16 | 1.3.6.7.4 Critical Values of the Chi-Square Distribution | https://www.itl.nist.gov/div898/handbook/eda/section3/eda3674.htm | verified | full | Upper-tail and lower-tail tables; sampled entries (df 10: 18.307, 23.209, lower 3.940; df 1: 3.841; df 5: 11.070; df 30: 43.773; df 20 at 0.01: 37.566) checked in tables.py. |
| S-B17 | 6.3.3.1 Counts Control Charts (c chart) | https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc331.htm | verified | full | c chart limits c̄ ± 3√c̄; worked example 25 wafers, c̄ = 400/25 = 16, UCL 28, LCL 4. Note: the NIST page numbering puts the c chart in 6.3.3.1 and the p chart in 6.3.3.2. |
| S-B18 | 6.3.3.2 Proportions Control Charts (p chart) | https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc332.htm | verified | full | p chart limits p̄ ± 3√(p̄(1−p̄)/n), p̄ = ΣD_i/(mn); worked example 30 samples of 50 chips, p̄ ≈ 0.24, UCL ≈ 0.43, LCL ≈ 0.05. The np and u chart formulas follow the same binomial and Poisson logic (S-A2 10.3.6 prefers exact binomial and Poisson limits; the course teaches the 3-sigma form and says so). |

### C. Journal articles

| ID | Citation | URL | Status | Depth | Supports |
|---|---|---|---|---|---|
| S-C1 | Kane, V. E. (1986). Process capability indices. *Journal of Quality Technology*, 18(1), 41–52. | https://www.tandfonline.com/doi/abs/10.1080/00224065.1986.11978984 | verified | abstract | Origin paper for Cp, CPU, CPL, k, Cpk as a system; author at Ford; Japanese industry use and US automotive adoption. |
| S-C2 | Chan, L. K., Cheng, S. W., & Spiring, F. A. (1988). A new measure of process capability: Cpm. *Journal of Quality Technology*, 20(3), 162–175. | https://www.tandfonline.com/doi/abs/10.1080/00224065.1988.11979102 | verified | abstract | Origin of Cpm (target-based index). |
| S-C3 | Kotz, S., & Johnson, N. L. (2002). Process capability indices—a review, 1992–2000 (with discussion). *Journal of Quality Technology*, 34(1), 2–19. | http://asq.org/qic/display-item/index.html?item=20422 | verified | abstract | 170 publications reviewed; normal, non-normal, multivariate indices; discussants include Bothe, Boyles, Spiring, Vännman. |
| S-C4 | Kushler, R. H., & Hurley, P. (1992). Confidence bounds for capability indices. *Journal of Quality Technology*, 24(4), 188–195. | https://www.tandfonline.com/doi/abs/10.1080/00224065.1992.11979400 | verified | abstract | Lower confidence bounds for Cpk from a sample. |
| S-C5 | Bissell, A. F. (1990). How reliable is your capability index? *Applied Statistics (JRSS C)*, 39(3), 331–340. | https://academic.oup.com/jrsssc/article-pdf/39/3/331/48622534/jrsssc_39_3_331.pdf | verified | abstract | Standard-error and CI approximations for Cp/Cpk; the source behind "a Cpk from 30 samples has a wide interval". |
| S-C6 | Clements, J. A. (1989). Process capability calculations for non-normal distributions. *Quality Progress*, 22(9), 95–100. | https://asq.org/quality-progress/articles/column-qualityware-process-capability-calculations-for-non-normal-distributions?id=236610e130d446d783460aa0debc745f | verified | abstract | Pearson-curve percentile method using mean, sd, skewness, kurtosis. |
| S-C7 | Somerville, S. E., & Montgomery, D. C. (1996). Process capability indices and non-normal distributions. *Quality Engineering*, 9(2), 305–316. | https://www.tandfonline.com/doi/abs/10.1080/08982119608919047 | secondary | citation only | Errors in PPM predictions when normal-based indices are used on non-normal data. Cite via S-C3. |
| S-C8 | Bothe, D. R. (2002). Statistical reason for the 1.5σ shift. *Quality Engineering*, 14(3), 479–487. | https://www.tandfonline.com/doi/abs/10.1081/qen-120001884 | verified | abstract | With subgroups of n = 4, shifts up to about 1.5σ tend to go undetected by an X̄ chart, hence a statistical rationale; introduces "dynamic Cpk". |
| S-C9 | Tadikamalla, P. R. (1994). The confusion over six-sigma quality. *Quality Progress*, 27(11), 83–85. | https://www.proquest.com/openview/df184b19ba7003517881a00d6f967c6d/1 | verified | abstract | Sigma quality levels translate to defect rates only given a centring assumption; Motorola's 3.4 PPM comes from placing the mean 1.5σ off centre; the terminology confuses statisticians. |
| S-C10 | Nelson, L. S. (1984). The Shewhart control chart—tests for special causes. *Journal of Quality Technology*, 16(4), 237–239. | https://www.leansixsigmadefinition.com/wp-content/uploads/2023/07/The-Shewhart-Control-Chart-Tests-for-Special-Causes-Lloyd-Nelson-Journal-of-Quality-Technology.pdf | verified | full | The eight tests (1: one point beyond zone A; 2: nine in a row one side; 3: six steadily increasing or decreasing; 4: fourteen alternating; 5: two of three in zone A or beyond; 6: four of five in zone B or beyond; 7: fifteen in zone C; 8: eight beyond zone C both sides) and Nelson's guidance on use. |
| S-C11 | Champ, C. W., & Woodall, W. H. (1987). Exact results for Shewhart control charts with supplementary runs rules. *Technometrics*, 29(4), 393–399. | https://www.tandfonline.com/doi/abs/10.1080/00401706.1987.10488266 | verified | abstract | Markov-chain ARL of charts with runs rules; runs rules shorten in-control ARL (more false alarms); comparison with CUSUM. Reference for the false-alarm table (values computed by our scripts, not copied). |
| S-C12 | Woodall, W. H. (2000). Controversies and contradictions in statistical process control (with discussion). *Journal of Quality Technology*, 32(4), 341–378. | https://www.tandfonline.com/doi/abs/10.1080/00224065.2000.11980013 | verified | abstract | Controversies: hypothesis-testing view vs Shewhart's view, role of theory, competing methods, Phase I vs Phase II; researcher–practitioner gap. |
| S-C13 | Roberts, S. W. (1959). Control chart tests based on geometric moving averages. *Technometrics*, 1(3), 239–250. | https://www.tandfonline.com/doi/abs/10.1080/00401706.1959.10489860 | verified | abstract (listing) | Origin of the EWMA chart. |
| S-C14 | Page, E. S. (1954). Continuous inspection schemes. *Biometrika*, 41(1/2), 100–115. | https://doi.org/10.1093/biomet/41.1-2.100 | verified | abstract (listing) | Origin of CUSUM. |
| S-C15 | Lucas, J. M., & Saccucci, M. S. (1990). Exponentially weighted moving average control schemes: properties and enhancements. *Technometrics*, 32(1), 1–12. | https://www.tandfonline.com/doi/abs/10.1080/00401706.1990.10484583 | verified | abstract (listing) | EWMA ARL properties; λ and L design; FIR and combined Shewhart-EWMA. |
| S-C16 | Laney, D. B. (2002). Improved control charts for attributes. *Quality Engineering*, 14(4), 531–537. | https://www.tandfonline.com/doi/abs/10.1081/QEN-120003555 | verified | abstract | p′ and u′ charts for over-dispersed attribute data with large subgroups. |
| S-C17 | Burdick, R. K., Borror, C. M., & Montgomery, D. C. (2003). A review of methods for measurement systems capability analysis. *Journal of Quality Technology*, 35(4), 342–354. | https://www.tandfonline.com/doi/abs/10.1080/00224065.2003.11980232 | verified | abstract | ANOVA method for crossed two-factor gauge studies; variance components; point and interval estimates. |
| S-C18 | Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement*, 20(1), 37–46. | https://journals.sagepub.com/doi/10.1177/001316446002000104 | verified | abstract | Kappa for two raters, chance-corrected agreement (attribute agreement analysis). |
| S-C19 | Fleiss, J. L. (1971). Measuring nominal scale agreement among many raters. *Psychological Bulletin*, 76(5), 378–382. | https://doi.org/10.1037/h0031619 | verified | abstract (listing) | Kappa for more than two raters. |
| S-C20 | Wasserstein, R. L., & Lazar, N. A. (2016). The ASA's statement on p-values: context, process, and purpose. *The American Statistician*, 70(2), 129–133. | https://www.stat.berkeley.edu/~aldous/Real_World/ASA_statement.pdf | verified | full | Six principles: p-values indicate incompatibility of data with a model; do not measure the probability the hypothesis is true; conclusions should not rest on p < 0.05 alone; require full reporting; do not measure effect size; are not by themselves good evidence. |
| S-C21 | Welch, B. L. (1947). The generalization of 'Student's' problem when several different population variances are involved. *Biometrika*, 34(1/2), 28–35. | https://academic.oup.com/biomet/article-abstract/34/1-2/28/210174 | verified | abstract (listing) | Unequal-variance t-test (the default in the course calculators). |
| S-C22 | Levene, H. (1960). Robust tests for equality of variances. In I. Olkin (Ed.), *Contributions to Probability and Statistics: Essays in Honor of Harold Hotelling* (pp. 278–292). Stanford University Press. | https://www.scirp.org/reference/ReferencesPapers?ReferenceID=2363177 | verified | abstract (listing) | Levene's test for variances. |
| S-C23 | Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality (complete samples). *Biometrika*, 52(3/4), 591–611. | https://academic.oup.com/biomet/article-abstract/52/3-4/591/336553 | verified | abstract | Shapiro-Wilk normality test. |
| S-C24 | Anderson, T. W., & Darling, D. A. (1952). Asymptotic theory of certain "goodness of fit" criteria based on stochastic processes. *Annals of Mathematical Statistics*, 23(2), 193–212. | https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-23/issue-2/Asymptotic-Theory-of-Certain-Goodness-of-Fit-Criteria-Based-on/10.1214/aoms/1177729437.full | verified | abstract (listing) | Anderson-Darling statistic (the default normality test in most SPC software). |
| S-C25 | Box, G. E. P., & Cox, D. R. (1964). An analysis of transformations. *JRSS B*, 26(2), 211–252. | https://academic.oup.com/jrsssb/article/26/2/211/7028064 | verified | abstract | Box-Cox power transformation. |
| S-C26 | Johnson, N. L. (1949). Systems of frequency curves generated by methods of translation. *Biometrika*, 36(1/2), 149–176. | https://academic.oup.com/biomet/article-abstract/36/1-2/149/200775 | verified | abstract (listing) | Johnson SL, SU, SB transformation families. |
| S-C27 | Wilcoxon, F. (1945). Individual comparisons by ranking methods. *Biometrics Bulletin*, 1(6), 80–83; Mann, H. B., & Whitney, D. R. (1947). *Ann. Math. Statist.*, 18(1), 50–60; Kruskal, W. H., & Wallis, W. A. (1952). *JASA*, 47(260), 583–621. | https://garfield.library.upenn.edu/classics1987/A1987K083100001.pdf | verified | abstract (listing) | Nonparametric alternatives to the t-test and ANOVA. |
| S-C28 | Anscombe, F. J. (1973). Graphs in statistical analysis. *The American Statistician*, 27(1), 17–21. | https://www.sjsu.edu/faculty/gerstman/StatPrimer/anscombe1973.pdf | verified | abstract | Four datasets with identical summary statistics and different plots; the published data may be embedded as a **real** dataset in Modules 9 and 12. |
| S-C29 | Box, G. E. P. (1988). Signal-to-noise ratios, performance criteria, and transformations (with discussion). *Technometrics*, 30(1), 1–40. | https://www.tandfonline.com/doi/abs/10.1080/00401706.1988.10488313 | verified | abstract | Critique of Taguchi SN ratios; a log transformation achieves the same more simply. |
| S-C30 | Nair, V. N. (Ed.) (1992). Taguchi's parameter design: a panel discussion. *Technometrics*, 34(2), 127–161. | https://www.stat.cmu.edu/technometrics/90-00/vol-34-02/v3402127.pdf | verified | abstract | The formal debate on Taguchi methods (Box, Phadke, Shoemaker, Tsui, Taguchi, Wu, and others). |
| S-C31 | Plackett, R. L., & Burman, J. P. (1946). The design of optimum multifactorial experiments. *Biometrika*, 33(4), 305–325. | https://academic.oup.com/biomet/article-abstract/33/4/305/225377 | verified | abstract | Screening designs. |
| S-C32 | Box, G. E. P., & Wilson, K. B. (1951). On the experimental attainment of optimum conditions. *JRSS B*, 13(1), 1–45. | https://academic.oup.com/jrsssb/article/13/1/1/7026650 | verified | abstract | Origin of response surface methodology. |
| S-C33 | Evans, D. H. (1974–1975). Statistical tolerancing: the state of the art. Parts I–III. *Journal of Quality Technology*, 6(4), 188–195; 7(1), 1–12; 7(2), 72–76. | https://www.tandfonline.com/doi/abs/10.1080/00224065.1975.11980657 | verified | abstract | Linear propagation (RSS), non-linear, quadrature, Monte Carlo; Part III on shifts and drifts. |
| S-C34 | Chase, K. W., & Parkinson, A. R. (1991). A survey of research in the application of tolerance analysis to the design of mechanical assemblies. *Research in Engineering Design*, 3, 23–37. | https://link.springer.com/article/10.1007/BF01580066 | verified | abstract | Tolerance analysis as a design function; worst-case vs statistical. |
| S-C35 | Schroeder, R. G., Linderman, K., Liedtke, C., & Choo, A. S. (2008). Six Sigma: definition and underlying theory. *Journal of Operations Management*, 26(4), 536–554. | https://strategicimprovementsystems.com/wp-content/uploads/2011/07/PAPER_SIX_SIGMA.pdf | verified | abstract (PDF) | Tools are "strikingly similar to prior approaches"; what is new is the organizational structure (belts, projects, metrics). |
| S-C36 | Zu, X., Fredendall, L. D., & Douglas, T. J. (2008). The evolving theory of quality management: the role of Six Sigma. *Journal of Operations Management*, 26(5), 630–650. | https://onlinelibrary.wiley.com/doi/10.1016/j.jom.2008.02.001 | verified | abstract | Three new practices: role structure, structured improvement procedure, focus on metrics. |
| S-C37 | Linderman, K., Schroeder, R. G., Zaheer, S., & Choo, A. S. (2003). Six Sigma: a goal-theoretic perspective. *Journal of Operations Management*, 21(2), 193–203. | https://pure.psu.edu/en/publications/six-sigma-a-goal-theoretic-perspective/ | verified | abstract | Six Sigma explained through goal theory; a widely used academic definition of Six Sigma. |
| S-C38 | Swink, M., & Jacobs, B. W. (2012). Six Sigma adoption: operating performance impacts and contextual drivers of success. *Journal of Operations Management*, 30(6), 437–453. | https://onlinelibrary.wiley.com/doi/10.1016/j.jom.2012.05.001 | verified | abstract | Event study of 200 adopters vs matched firms: positive ROA effect, mostly from indirect cost reductions. The academic counterweight to S-E1. |
| S-C39 | Hahn, G. J., Doganaksoy, N., & Hoerl, R. (2000). The evolution of Six Sigma. *Quality Engineering*, 12(3), 317–326. | https://www.tandfonline.com/doi/abs/10.1080/08982110008962595 | secondary | citation only | GE insiders' account of the programme's evolution. |
| S-C40 | Antony, J., Snee, R., & Hoerl, R. (2017). Lean Six Sigma: yesterday, today and tomorrow. *International Journal of Quality & Reliability Management*, 34(7), 1073–1093. | https://www.emerald.com/insight/content/doi/10.1108/ijqrm-03-2016-0035/full/html | verified | abstract | History of the Lean and Six Sigma integration; current and future trends. |
| S-C41 | Kano, N., Seraku, N., Takahashi, F., & Tsuji, S. (1984). Attractive quality and must-be quality. *Journal of the Japanese Society for Quality Control*, 14(2), 147–156. | https://www.jstage.jst.go.jp/article/quality/14/2/14_KJ00002952366/_article/-char/en | verified | abstract | Two-dimensional quality model; attractive, must-be, one-dimensional; validated by consumer surveys on televisions and table clocks. |
| S-C42 | Griffin, A., & Hauser, J. R. (1993). The voice of the customer. *Marketing Science*, 12(1), 1–27. | https://pubsonline.informs.org/doi/10.1287/mksc.12.1.1 | verified | abstract | Identifying, structuring, and prioritizing customer needs (VOC to CTQ). |
| S-C43 | Deming, W. E. (1975). On probability as a basis for action. *The American Statistician*, 29(4), 146–152. | https://deming.org/wp-content/uploads/2020/06/On-Probability-As-a-Basis-For-Action-1975.pdf | verified | full | Enumerative vs analytic studies; an analytic study aims at "action on the cause-system or the process, in order to improve product of the future". |
| S-C44 | Best, M., & Neuhauser, D. (2006). Walter A Shewhart, 1924, and the Hawthorne factory. *Quality and Safety in Health Care*, 15(2), 142–143. | https://pmc.ncbi.nlm.nih.gov/articles/PMC2464836/ | verified | full | 16 May 1924 memo; assignable vs chance causes; slow adoption at Hawthorne; Bell Labs founded 1925. |
| S-C45 | Juran, J. M. (1975). The non-Pareto principle; mea culpa. *Quality Progress*, 8(5), 8–9. (Juran Institute reprint dated 1974.) | https://www.juran.com/wp-content/uploads/2021/03/The-Non-Pareto-Principle-1974.pdf | verified | full | Juran admits he misnamed the "vital few and trivial many" after Pareto. |
| S-C46 | Sharma, G. V. S. S., & Rao, P. S. (2014). A DMAIC approach for process capability improvement an engine crankshaft manufacturing process. *Journal of Industrial Engineering International*, 10, 65. Open access (CC BY). | https://link.springer.com/article/10.1007/s40092-014-0065-7 | verified | abstract | Real published DMAIC case: sd 0.003 → 0.002, Cp 1.29 → 2.02, Cpk 0.32 → 1.45; Ishikawa and PFMEA used. Numbers cited exactly as published, not recomputed. |
| S-C47 | Seder, L. A. (1950). Diagnosis with diagrams, Parts I and II. *Industrial Quality Control*, 6(4) and 6(5). | (via ASQ Quality Progress, "The multi-vari chart: an underutilized quality tool", and Wikipedia) | secondary | – | Origin of the multi-vari chart. |
| S-C48 | Yates, F. (1937). *The Design and Analysis of Factorial Experiments*. Imperial Bureau of Soil Science, Technical Communication 35. | https://link.springer.com/rwe/10.1007/978-0-387-32833-1_429 | secondary | – | Yates algorithm for 2ᵏ effects (the hand method used in recompute.py). |

### D. Books

| ID | Citation | URL | Status | Depth | Supports |
|---|---|---|---|---|---|
| S-D1 | Montgomery, D. C. (2019). *Introduction to Statistical Quality Control*, 8th ed. Wiley. ISBN 978-1-119-65711-8. | https://www.wiley.com/en-us/Introduction+to+Statistical+Quality+Control,+8th+Edition-p-9781119399308 | verified | catalog | Standard textbook; existence and edition. Specific numbers (ARL, constants, examples) are computed by our scripts; the textbook is cited for method, and as secondary for any quoted figure. |
| S-D2 | Montgomery, D. C. (2019). *Design and Analysis of Experiments*, 10th ed. Wiley. | https://www.wiley.com/en-us/Design+and+Analysis+of+Experiments,+10th+Edition-p-9781119492443 | verified | catalog | DOE textbook reference. |
| S-D3 | Wheeler, D. J., & Chambers, D. S. (2010). *Understanding Statistical Process Control*, 3rd ed. SPC Press. ISBN 978-0-945320-69-2. | https://www.spcpress.com/book_understanding_statistical_process_control.php | verified | catalog | Existence and edition; Wheeler's approach (process behaviour charts, three-sigma limits, rational subgrouping). |
| S-D4 | Wheeler, D. J. (2004). *Advanced Topics in Statistical Process Control: The Power of Shewhart's Charts*, 2nd ed. SPC Press. | https://www.spcpress.com/book_advanced_topics_in_spc.php | verified | catalog | Theory of process behaviour charts. |
| S-D5 | Wheeler, D. J. (1991). *Short Run SPC*. SPC Press. | https://www.amazon.com/Short-Run-SPC-Donald-Wheeler/dp/0945320124 | verified | catalog | Difference (deviation-from-nominal) and Zed charts. |
| S-D6 | Bothe, D. R. (1997). *Measuring Process Capability: Techniques and Calculations for Quality and Manufacturing Engineers*. McGraw-Hill. | https://search.worldcat.org/title/36135779 | verified | catalog | Comprehensive capability reference (897 pp.). |
| S-D7 | Pyzdek, T., & Keller, P. A. (2018). *The Six Sigma Handbook*, 5th ed. McGraw-Hill. ISBN 978-1-260-12182-7. | https://www.accessengineeringlibrary.com/browse/six-sigma-handbook-fifth-edition | verified | catalog | General Six Sigma handbook. |
| S-D8 | Breyfogle, F. W. III (2003). *Implementing Six Sigma: Smarter Solutions Using Statistical Methods*, 2nd ed. Wiley. | https://www.wiley.com/en-us/Implementing+Six+Sigma:+Smarter+Solutions+Using+Statistical+Methods,+2nd+Edition-p-9780471476320 | verified | catalog | General reference. |
| S-D9 | Shewhart, W. A. (1931). *Economic Control of Quality of Manufactured Product*. Van Nostrand. (Reissued ASQ, 1980.) | https://archive.org/details/in.ernet.dli.2015.150272 | verified | catalog | Origin of the control chart and three-sigma limits (an economic, not a probabilistic, justification). |
| S-D10 | Deming, W. E. (1986). *Out of the Crisis*. MIT Center for Advanced Engineering Study. | https://archive.org/details/outofcrisisquali00demi | verified | catalog | 14 points; funnel experiment and tampering (p. 327 per S-E21, secondary); red beads. |
| S-D11 | Deming, W. E. (1993). *The New Economics for Industry, Government, Education*. MIT CAES. | https://deming.org/explore/sopk/ | verified | catalog | System of Profound Knowledge (four parts, per S-E4). |
| S-D12 | Ohno, T. (1988). *Toyota Production System: Beyond Large-Scale Production*. Productivity Press. | https://books.google.com/books/about/Toyota_Production_System.html?id=QebEDwAAQBAJ | verified | catalog | Seven wastes; 5 Whys. The waste list itself is verified via S-E22. |
| S-D13 | Liker, J. K. (2004). *The Toyota Way*. McGraw-Hill. | https://books.google.com/books/about/The_Toyota_Way.html?id=eZutzPww02EC | verified | catalog | Eighth waste (unused employee creativity) attributed to Liker (secondary for the attribution). |
| S-D14 | Womack, J. P., & Jones, D. T. (1996). *Lean Thinking*. Simon & Schuster. | https://www.lean.org/the-lean-post/articles/lean-thinking-a-look-back-and-a-look-forward/ | verified | catalog | Five lean principles; the term "value stream". |
| S-D15 | Rother, M., & Shook, J. (1999). *Learning to See*. Lean Enterprise Institute. | https://www.lean.org/lexicon-terms/value-stream-mapping/ | verified | catalog | Value-stream mapping method (S-E23 confirms). |
| S-D16 | Shingo, S. (1985). *A Revolution in Manufacturing: The SMED System*. Productivity Press. | https://www.routledge.com/A-Revolution-in-Manufacturing-The-SMED-System/Dillon-Shingo/p/book/9780915299034 | verified | catalog | SMED method (internal vs external setup). |
| S-D17 | Shingo, S. (1986). *Zero Quality Control: Source Inspection and the Poka-yoke System*. Productivity Press. | https://www.routledge.com/Zero-Quality-Control-Source-Inspection-and-the-Poka-Yoke-System/Shingo/p/book/9780915299072 | verified | catalog | Poka-yoke and source inspection. |
| S-D18 | Hirano, H. (1995). *5 Pillars of the Visual Workplace*. Productivity Press. | https://www.routledge.com/5-Pillars-of-the-Visual-Workplace/Hirano/p/book/9781563270475 | verified | catalog | 5S. |
| S-D19 | Imai, M. (1986). *Kaizen: The Key to Japan's Competitive Success*. McGraw-Hill. | https://archive.org/details/kaizen00masa | verified | catalog | Kaizen. |
| S-D20 | Pugh, S. (1991). *Total Design: Integrated Methods for Successful Product Engineering*. Addison-Wesley. | https://en.wikipedia.org/wiki/Stuart_Pugh | secondary | – | Pugh concept-selection matrix. |
| S-D21 | Taguchi, G. (1986). *Introduction to Quality Engineering: Designing Quality into Products and Processes*. Asian Productivity Organization. | https://archive.org/details/introductiontoqu0000tagu | verified | catalog | Quadratic loss function; parameter and tolerance design. |
| S-D22 | Phadke, M. S. (1989). *Quality Engineering Using Robust Design*. Prentice Hall. | https://books.google.com/books/about/Quality_Engineering_Using_Robust_Design.html?id=TZoQAQAAMAAJ | verified | catalog | Robust design; source of the Sony colour-density figure (per S-E24). |
| S-D23 | Creveling, C. M. (1997). *Tolerance Design: A Handbook for Developing Optimal Specifications*. Addison-Wesley. | https://searchworks.stanford.edu/view/3399329 | verified | catalog | Tolerance design linking the loss function and capability. |
| S-D24 | Box, G. E. P., Hunter, J. S., & Hunter, W. G. (2005). *Statistics for Experimenters*, 2nd ed. Wiley. | https://www.wiley.com/en-us/Statistics+for+Experimenters:+Design,+Innovation,+and+Discovery,+2nd+Edition-p-9780471718130 | verified | catalog | Factorial design, effects, blocking. |
| S-D25 | Fisher, R. A. (1935). *The Design of Experiments*. Oliver and Boyd. | https://archive.org/details/in.ernet.dli.2015.502684 | verified | catalog | Randomization, replication, blocking. |
| S-D26 | Ishikawa, K. (1976). *Guide to Quality Control*. Asian Productivity Organization. | https://openlibrary.org/books/OL4595409M/Guide_to_quality_control | verified | catalog | Cause-and-effect diagram; the seven basic tools. |
| S-D27 | Kepner, C. H., & Tregoe, B. B. (1965). *The Rational Manager*. McGraw-Hill. | https://books.google.com/books/about/The_Rational_Manager.html?id=OboWAAAAIAAJ | verified | catalog | Is/Is-not problem analysis. |
| S-D28 | Harry, M. J. (1988). *The Nature of Six Sigma Quality*. Motorola University Press. | https://openlibrary.org/books/OL9828527M/The_Nature_of_Six_Sigma_Quality | verified | catalog | Motorola's articulation of Six Sigma; source of the 1.5σ convention (secondary for that claim). |
| S-D29 | Harry, M., & Schroeder, R. (2000). *Six Sigma: The Breakthrough Management Strategy Revolutionizing the World's Top Corporations*. Currency/Doubleday. | https://books.google.com/books/about/Six_Sigma.html?id=RY0rAAAAYAAJ | verified | catalog | Popular account; RTY, belts, breakthrough strategy. Savings claims in it are **secondary** and are not to be repeated as fact. |
| S-D30 | Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. Lawrence Erlbaum. | https://www.routledge.com/Statistical-Power-Analysis-for-the-Behavioral-Sciences/Cohen/p/book/9780805802832 | verified | catalog | Cohen's d; small 0.2, medium 0.5, large 0.8 (conventions from behavioural science, flagged as such). |
| S-D31 | Tukey, J. W. (1977). *Exploratory Data Analysis*. Addison-Wesley. | https://www.scirp.org/reference/referencespapers?referenceid=1482121 | verified | catalog | Box plot origin. |
| S-D32 | Wheeler, D. J. *SPC Press reading room* (open PDFs of Quality Digest columns). | https://www.spcpress.com/reading_room.php | verified | catalog | Index page for S-E5 to S-E7. |
| S-D33 | Montgomery, D. C. *Design and Analysis of Experiments* (8th ed., Wiley, 2013), plasma etch 2³ example (Section 6.3). | (not read; reproduced in S-E34) | secondary | – | Data (16 runs, two replicates) and effects A −101.625, B 7.375, C 306.125, AB −24.875, AC −153.625, BC −2.125, ABC 5.625, with the ANOVA table, as reproduced with R output in S-E34. Phase B check example chk-montgomery-etch. |
| S-D34 | Press, W. H., Teukolsky, S. A., Vetterling, W. T., & Flannery, B. P. (2007). *Numerical Recipes: The Art of Scientific Computing*, 3rd ed. Cambridge University Press. | https://numerical.recipes/ | secondary | – | Algorithms for the regularized incomplete beta (modified Lentz continued fraction, section 6.4) and incomplete gamma (series and continued fraction, section 6.2) used in stats.js and recompute.py; correctness established independently by the scipy comparison in test_calculators.js. |
| S-D35 | D'Agostino, R. B., & Stephens, M. A. (eds.) (1986). *Goodness-of-Fit Techniques*. Marcel Dekker. Table 4.9. | (not read; formula as reproduced in the statsmodels normal_ad source and Minitab documentation) | secondary | – | Anderson-Darling adjustment A*² = A²(1 + 0.75/n + 2.25/n²) and the piecewise p-value formula for the case with estimated mean and variance. |

### E. Articles, reports, and web pages

| ID | Citation | URL | Status | Depth | Supports |
|---|---|---|---|---|---|
| S-E1 | Fortune (Morris, B.). "Jack Welch's rules for winning don't work anymore (but we've got 7 new ones that do)" (rule "Look out, not in"). *Fortune*, 24 July 2006 issue. | https://fortune.com/article/fortune-archives-jack-welch/ | verified | full (passage) | "Of 58 large companies that have announced Six Sigma programs, 91% have trailed the S&P 500 since, according to an analysis by Charles Holland of consulting firm Qualpro." Fortune notes Qualpro sells a competing method. Correlation, not causation; sample and method not peer reviewed. |
| S-E2 | Hindo, B. "At 3M, a struggle between efficiency and creativity." *BusinessWeek*, 11 June 2007. (Note: BusinessWeek, not the Wall Street Journal as the brief guessed.) | https://effectuation.org/hubfs/Journal%20Articles/2016/06/3m-struggle-between-efficiency-and-creativity.pdf | verified | full | McNerney's Six Sigma push at 3M (thousands trained as Black Belts; 8,000 layoffs); the share of sales from products under five years old fell from about one-third to one-quarter; Buckley: "Invention is by its very nature a disorderly process"; von Hippel and Govindarajan quotes. |
| S-E3 | General Electric Company. *1998 Annual Report*, letter to share owners. | https://www.annualreports.com/HostedData/AnnualReportArchive/g/NYSE_GE_1998.pdf | verified | full (letter) | GE's own claims: three growth initiatives (Globalization, Services, Six Sigma); invested "more than a billion dollars"; "more than three quarters of a billion dollars in savings beyond our investment in 1998, with a billion and a half in sight for 1999". Self-reported; to be presented as the company's claim. |
| S-E4 | The W. Edwards Deming Institute. "Red Bead Experiment"; "The Deming System of Profound Knowledge". | https://deming.org/explore/red-bead-experiment/ ; https://deming.org/explore/sopk/ | verified | full | Deming used the red beads from the early 1980s; willing workers limited by the system; fallacy of ranking people; SoPK four parts. |
| S-E5 | Wheeler, D. J. "The keys to quality assurance: it takes more than a good capability ratio." *Quality Digest*, 4 March 2019 (SPC Press manuscript 345). | https://spcpress.com/pdf/DJW345.pdf | verified | full | Cp, Cpk, Pp, Ppk defined with within-subgroup Sigma(X) vs global s; the four indexes agree only when the process is operated predictably and on target; for an unpredictable process the indexes describe the past and cannot predict; "Until this process is operated predictably we simply cannot use" the indexes for prediction. |
| S-E6 | Wheeler, D. J. "Rational subgrouping: the conceptual foundation of process behavior charts." *Quality Digest*, 1 June 2015 (manuscript 282); and "Rational sampling", 1 July 2015 (manuscript 283). | https://spcpress.com/pdf/DJW282.pdf ; https://www.qualitydigest.com/inside/standards-column/rational-subgrouping-060115.html | verified | full | Subgroups from "some small region of space, or time, or product"; within-subgroup variation must be routine variation; the chart answers the question the subgrouping asks. |
| S-E7 | Wheeler, D. J. "Problems with skewness and kurtosis, Part One." *Quality Digest*, 1–2 Aug 2011 (manuscript 231). | http://spcpress.com/pdf/DJW231.pdf | verified | full | When data are not homogeneous, transforming them is the wrong response; question the lack of homogeneity first. The counter-position to routine Box-Cox/Johnson transformation. |
| S-E8 | NIST. "Malcolm Baldrige National Quality Award 1988 Recipient: Motorola Inc." | https://www.nist.gov/system/files/documents/2017/10/11/1988_Motorola_Inc.pdf | verified | full | 1981 tenfold-improvement drive; goal "Zero defects in everything we do"; "Six Sigma Quality … a target of no more than 3.4 defects per million products, customer services included"; 99,000 employees; $6.7 billion 1987 sales. |
| S-E9 | Motorola Inc. *1988 Annual Report*. | https://www.motorolasolutions.com/content/dam/msi/docs/en-xw/static_files/1988_Motorola_Annual_Report.pdf | unverified | – | File exceeded the fetch size limit (>10 MB). Not used unless the author downloads it. |
| S-E10 | Wikipedia. "Bill Smith (Motorola engineer)"; "Six Sigma". | https://en.wikipedia.org/wiki/Bill_Smith_(Motorola_engineer) | secondary | – | Smith proposed the approach to Galvin (1985–86); MAIC to DMAIC; service mark 1991, trademark 1993. Used only for dates cross-checked with S-E8; labelled secondary. |
| S-E11 | Hindle, S. A. "Shewhart's great discovery." *Quality Digest*, 16 May 2024. | https://www.qualitydigest.com/inside/six-sigma-article/shewharts-great-discovery-051624.html | verified | partial (intro) | The 16 May 1924 memo as the first record of the control chart (corroborates S-C44). |
| S-E12 | DQS. "New AIAG & VDA SPC Manual 1st Edition released." 2026. | https://www.dqsglobal.com/en/explore/blog/release-of-aiag-vda-spc-manual-1st-edition | verified | full | Released 1 July 2026; harmonizes AIAG SPC and VDA Volume 4; aligns with ISO 7870, ISO 22514, ISO 3534; states Cp/Cpk only for statistically stable processes, Pp/Ppk otherwise; MSA before capability; scenario-based chart selection including EWMA/CUSUM. (The page mis-states the prior AIAG edition number; AIAG's own catalog is authoritative.) |
| S-E13 | Quality Magazine. "A first look at the AIAG/VDA SPC manual." 2026. | https://www.qualitymag.com/articles/99695-a-first-look-at-the-aiagvda-spc-manual | secondary | – (403 on fetch; search excerpt) | Prior AIAG SPC 2nd edition dated 2005; unified eight special-cause rules. |
| S-E14 | SPC for Excel. "Acceptance criteria for measurement systems analysis." | https://www.spcforexcel.com/knowledge/measurement-systems-analysis-gage-rr/acceptance-criteria-for-msa/ | secondary | – | AIAG MSA %GRR bands and ndc ≥ 5 (restates the manual). |
| S-E15 | Quality Engineer Stuff. "Initial process studies in PPAP." | https://qualityengineerstuff.com/doc/initial-process-studies/ | secondary | – | PPAP initial-study bands (>1.67; 1.33–1.67; <1.33) and ongoing Cpk ≥ 1.33. |
| S-E16 | QualityEngineer.ai. "Gauge R&R acceptance criteria: %GRR, NDC, and what AIAG MSA requires." | https://app.qualityengineer.ai/blog/gauge-rr-acceptance-criteria | secondary | – | Corroborates S-E14. |
| S-E17 | Quality-One. "AIAG & VDA FMEA." | https://quality-one.com/aiag-vda-fmea/ | secondary | – | Seven-step process; AP table replaces RPN; severity weighted first. |
| S-E18 | Biswas, P. "IATF 16949:2016 Clause 9.1.1.1 Monitoring and measurement of manufacturing processes." 6 Aug 2023. | https://preteshbiswas.com/2023/08/06/iatf-169492016-clause-9-1-1-1-monitoring-and-measurement-of-manufacturing-processes/ | verified | full (commentary) | Paraphrase of clause 9.1.1.1 requirements (see S-A19). Cited as a commentary, with the standard as the primary. |
| S-E19 | Wikipedia. "Western Electric rules." | https://en.wikipedia.org/wiki/Western_Electric_rules | verified | full | The four rules and zones; cites the 1956 handbook. Secondary for the handbook itself. |
| S-E20 | Wikipedia. "Nelson rules." | https://en.wikipedia.org/wiki/Nelson_rules | secondary | – | Cross-check of S-C10 only. |
| S-E21 | SPC for Excel. "Over-controlling a process: the funnel experiment." | https://www.spcforexcel.com/knowledge/variation/overcontrolling-process-funnel-experiment/ | secondary | – | Four funnel rules; tampering definition with a page reference to *Out of the Crisis* p. 327. |
| S-E22 | Lean Enterprise Institute. Lexicon: "Seven wastes." | https://www.lean.org/lexicon-terms/seven-wastes/ | verified | full | Ohno's seven wastes: overproduction, waiting, conveyance, processing, inventory, motion, correction; overproduction "the worst form of waste". |
| S-E23 | Lean Enterprise Institute. Lexicon: "Value-stream mapping." | https://www.lean.org/lexicon-terms/value-stream-mapping/ | verified | full | VSM definition; *Learning to See* introduced it (Shingo Research Prize 1999). |
| S-E24 | Simpson, T. W. "IE 466: Concurrent Engineering, 32.3 Taguchi's robust design method" (Penn State course handout). | https://www.me.psu.edu/simpson/courses/ie466/ie466.robust.handout.pdf | verified | full | Recounts the Sony USA vs Sony Japan colour-density story, citing Phadke (1989). The only readable source for the story found in this session. |
| S-E25 | Taguchi, G., & Clausing, D. (1990). Robust quality. *Harvard Business Review*, 68(1), 65–75. | https://hbr.org/1990/01/robust-quality | secondary | paywalled (title and lead only) | The Sony television comparison and the loss-function argument. **Decision:** the Sony story will be presented as "as reported by Taguchi and Clausing and by Phadke" with a note that the underlying 1979 newspaper data were not independently verified. |
| S-E26 | Juran Institute. "A guide to the Pareto principle (80/20 rule)." | https://www.juran.com/blog/a-guide-to-the-pareto-principle-80-20-rule-pareto-analysis/ | secondary | – | Background; S-C45 is primary. |
| S-E27 | ASQ. "The multi-vari chart: an underutilized quality tool." *Quality Progress* case study. | https://asq.org/quality-progress/articles/case-studies/the-multi-vari-chart-an-underutilized-quality-tool?id=d23574b44b3d49b88e9dcdddc4785cbb | secondary | – (403) | Seder attribution. |
| S-E28 | Burns, T. "Predictable." *Quality Digest*, 13 June 2018. | https://www.qualitydigest.com/inside/six-sigma-article/predictable-061318.html | verified | full | A practitioner critique: a process with a permanent 1.5σ shift "is wildly out of control and is hence unpredictable"; analytic vs enumerative framing. Opinion piece; cited as one side of the controversy. |
| S-E29 | Commercial training sites (GoLeanSixSigma, iSixSigma, SixSigmaDSI, 6sigma.us, and similar). | – | unverified | – | **Not used.** Not credible enough for historical or numerical claims. |
| S-E30 | Minitab, LLC. "Example of Crossed Gage R&R Study." Minitab Statistical Software help. | https://support.minitab.com/en-us/minitab/help-and-how-to/quality-and-process-improvement/measurement-system-analysis/how-to/gage-study/crossed-gage-r-r-study/before-you-start/example/ | verified | full | Published ANOVA table (with and without interaction), variance components, %Contribution, %Study Var, %Tolerance (tolerance 8) and ndc 4 for a 10 × 3 × 3 study; the interaction (p 0.974) is removed. Phase B check chk-minitab-grr-anova. The raw data file is not shown on the page. |
| S-E31 | Minitab, LLC. "Crossed Gage R&R: How are the variance components calculated?" Minitab Blog. | https://blog.minitab.com/en/blog/crossed-gage-rr-how-are-the-variance-components-calculated | verified | full | Variance component formulas from the mean squares: repeatability = MS_e; operator = (MS_op − MS_e)/(parts × replicates); part = (MS_part − MS_e)/(operators × replicates) for the reduced model. Confirms the AIAG MSA ANOVA method as implemented. |
| S-E32 | West, G. (2005). Better approximations to cumulative normal functions. *Wilmott Magazine*, 70–76. | (not read; algorithm widely reproduced) | secondary | – | Hart (1968) double-precision rational approximation of the normal CDF used in stats.js; accuracy established by the scipy comparison (max error 1e-16 at 268 points). |
| S-E33 | Acklam, P. J. (2003). An algorithm for computing the inverse normal cumulative distribution function. | https://web.archive.org/web/20151030215612/http://home.online.no/~pjacklam/notes/invnorm/ | secondary | – | Rational approximation (relative error 1.15e-9) with one refinement step, used in stats.js; accuracy established by the scipy comparison. |
| S-E34 | University of Washington, STAT 502 lecture notes. "The 2ᵏ Factorial Design (Montgomery chap. 6; BHH chap. 5)." | https://sites.stat.washington.edu/pds/stat502/LectureNotes/2k.factorial.intro.pdf | verified | full | Reproduces the Montgomery plasma etch 2³ data, the contrast effects, and the R lm/anova output (SS, F, p, residual SE 47.46, R² 0.9661). Supports S-D33. |

---

## Part 2. Per-module source lists, outlines, and planned examples

Verified sources are counted at any depth (full, abstract, scope, catalog). Catalog items may only be cited for what their Supports column allows. Invented example ids are the ids that will appear in `EXAMPLES.md` and `verification/`.

### Module 0. Introduction: what Six Sigma is and is not

**Verified sources (9):** S-E8, S-E3, S-E1, S-E2, S-C35, S-C36, S-C38, S-C9, S-A21. **Secondary:** S-E10, S-D28, S-D29, S-C39, S-C40.

**Outline.** Motorola's 1981 tenfold-improvement drive, the Six Sigma programme, and the 1988 Baldrige award, told from the NIST profile rather than from training-site folklore; the "3.4 defects per million" target as Motorola stated it. GE's adoption from 1995 and its own 1998 claims, presented as the company's claims. What a sigma level is (a preview of Module 6), DMAIC in one page, belts and roles as an organizational structure (the point of Schroeder et al. 2008 and Zu et al. 2008). Lean and Six Sigma. The critiques: Fortune/Qualpro 2006 (91 % of 58 adopters trailed the S&P 500, a correlation from a competitor's study), BusinessWeek's 3M story, and the peer-reviewed counterweight (Swink and Jacobs 2012 found positive ROA effects, mainly from indirect cost). What to take from it: the tools are old and sound, the packaging is what varies, and the statistics are where the value is. Covers the Green Belt BoK without claiming to certify. How to use the course.

**Real-world examples:** Motorola 1988 (S-E8); GE 1998 letter (S-E3); Fortune 2006 (S-E1); 3M 2007 (S-E2); Swink & Jacobs 2012 (S-C38).
**Invented examples:** `ex00-sigma-preview` – a bore diameter dataset (n = 100) used only to show a histogram against specifications and a defect rate, foreshadowing Modules 6 and 7. Point: a "sigma level" is a defect rate expressed as a Z-value.

### Module 1. Variation and basic statistics

**Verified sources (6):** S-B10, S-B11, S-B0, S-C28, S-C43, S-D1. **Secondary:** S-D31.

**Outline.** Types of data (continuous, discrete, attribute). Mean, median, range, sample vs population standard deviation, why n−1. Histograms and what bin width does. The normal distribution and the empirical rule, with the CDF computed, not looked up. Distributions engineers actually meet: lognormal (surface roughness, flatness), Weibull (fatigue life), binomial (defectives), Poisson (defects). Sampling versus population; enumerative vs analytic studies (Deming 1975) as the reason SPC is not just sampling theory. Central limit theorem shown by simulation in the browser (Calculator 9). Anscombe's quartet as the argument for plotting.

**Real-world examples:** Anscombe's quartet data, embedded verbatim (S-C28). Deming's enumerative/analytic distinction (S-C43).
**Invented examples:** `ex01-shaft-descriptives` – 60 shaft diameters (Ø8.000 ± 0.015 mm, micrometer to 0.001 mm), mean, median, sd by hand and by script. `ex01-fill-weight-lognormal` – 80 fill weights (g, to 0.1 g) with mild right skew, to show a distribution that is not normal and why. `ex01-clt-sim` – seeded simulation from a skewed parent, subgroup sizes 2, 5, 10.

### Module 2. Process thinking

**Verified sources (6):** S-E22, S-E23, S-E4, S-C44, S-C43, S-D12. **Secondary:** S-D13, S-D14, S-D15, S-E21.

**Outline.** SIPOC and process maps as the first tool of every project. Value-stream basics (definition per LEI; Rother and Shook as the method). Ohno's seven wastes with the LEI definitions, and Liker's eighth (labelled as his addition). Common versus special cause in words, using Deming's red beads (a verified, repeatable demonstration) and the funnel experiment (four rules, tampering), before any chart. Shewhart's 1924 memo as the origin, and the Hawthorne story that adoption took decades.

**Real-world examples:** Red bead experiment (S-E4); Shewhart 1924 and Hawthorne (S-C44).
**Invented examples:** `ex02-sipoc-brazing` – SIPOC for a brazed heat-exchanger line (the capstone process, introduced early). `ex02-funnel-sim` – seeded simulation of the four funnel rules with variance results (Calculator 9 variant). `ex02-vsm-machining` – a simple current-state map with cycle times and WIP in seconds and pieces.

### Module 3. Defining a project

**Verified sources (6):** S-C41, S-C42, S-C37, S-C35, S-A21, S-C46. **Secondary:** S-D7, S-D29.

**Outline.** Problem statements that name a measurable gap. Charters, business case, scope. VOC to CTQ using Griffin and Hauser's structure. Kano's model with his own validation on televisions and clocks. Stakeholder analysis. What a good Green Belt project looks like in manufacturing: the crankshaft case (Sharma and Rao 2014) as a published example of scope and metrics.

**Real-world examples:** Kano 1984 (S-C41); Sharma & Rao 2014 (S-C46).
**Invented examples:** `ex03-charter-leak` – full charter for the capstone leak-test problem (baseline 4.2 % leak reject, goal ≤ 1 %). `ex03-ctq-tree` – VOC to CTQ tree for a machined housing. `ex03-problem-statements` – three bad statements rewritten. (Numeric verification limited to the baseline figures generated in verification/.)

### Module 4. Measurement systems analysis

**Verified sources (7):** S-A4, S-B6, S-C17, S-C18, S-C19, S-A21, S-C46. **Secondary:** S-A11, S-E14, S-E16.

**Outline.** Why the gauge comes before the process. Bias, linearity, stability. Repeatability and reproducibility. Crossed gauge R&R by the ANOVA method (Burdick et al. 2003; NIST 2.4) with a full worked example: 10 parts × 3 operators × 3 replicates, variance components, %Contribution, %Study Variation, %Tolerance, ndc. AIAG acceptance guidelines (<10 %, 10–30 %, >30 %; ndc ≥ 5) cited as guidelines from MSA-4 (secondary until the author confirms page references). Attribute agreement analysis with Cohen's and Fleiss's kappa. What to do with a bad gauge.

**Real-world examples:** none with public data; "Why this matters" uses S-C46 (a published case that used MSA) plus a labelled illustrative failure.
**Invented examples:** `ex04-grr-bore-gauge` – bore gauge, Ø12.000 ± 0.025 mm, %GRR about 24 % (conditional). `ex04-grr-scale` – 0.1 g scale on fill weight, %GRR about 7 %. `ex04-attribute-visual` – 3 inspectors × 30 parts × 2 trials on braze fillet appearance, kappa about 0.6. `ex04-bias-linearity` – reference standards at 5 levels.

### Module 5. Data collection and sampling

**Verified sources (5):** S-E6, S-C43, S-B2, S-A21, S-D3. **Secondary:** S-D1, S-D10.

**Outline.** Operational definitions (Deming's phrase, from S-C43 and S-D10). Sampling plans. Rational subgrouping and why it decides everything downstream (Wheeler 2015: within-subgroup variation must be routine variation). Data collection sheets. Common data quality failures: rounding to the tolerance, mixed streams, sorting before measuring.

**Real-world examples:** none with public data (see Part 4).
**Invented examples:** `ex05-subgrouping-two-cavities` – the same 100 measurements subgrouped two ways (consecutive vs mixed cavities), showing how limits change. `ex05-rounding-loss` – data recorded to 0.01 vs 0.001 mm and the sd inflation. `ex05-sampling-plan` – a plan for a 3-shift line.

### Module 6. Sigma level, DPMO, DPU, RTY

**Verified sources (6):** S-E8, S-C9, S-C8, S-E28, S-B10, S-A21. **Secondary:** S-D28, S-D29.

**Outline.** Defects versus defectives, opportunities and how they get gamed (definition discipline). FTY vs RTY. Sigma level as a Z-value, with and without the 1.5σ shift, both labelled. The history: Motorola's 3.4 PPM statement (S-E8), the centred 6σ value of about 0.002 PPM, Tadikamalla's clarification, Bothe's statistical rationale (small subgroups miss 1.5σ shifts), and the practitioner objection (S-E28) that a permanently shifting process is not in control. Presented as contested convention, not law.

**Real-world examples:** Motorola 3.4 PPM statement (S-E8).
**Invented examples:** `ex06-dpmo-connector` – 5 opportunities per unit, 2,400 units, defects table. `ex06-rty-chain` – 5-step line with yields, FTY vs RTY. `ex06-sigma-table` – table generated by scipy for DPMO ⇄ Z with and without the shift.

### Module 7. Process capability I

**Verified sources (9):** S-B1, S-C1, S-C2, S-C4, S-C5, S-E5, S-A5, S-A9, S-A2. **Secondary:** S-E15, S-D6, S-A3.

**Outline.** Cp, Cpk, Cpu, Cpl; Pp, Ppk; Cpm. Within sigma (R̄/d₂, S̄/c₄) versus overall sigma (sample s), stated every time. Short- vs long-term. Capability to PPM. The 1.33 and 1.67 conventions and where they come from (PPAP initial-study bands; ongoing 1.33) as customer conventions. Confidence intervals on Cpk (NIST formula; Bissell; Kushler and Hurley) and what a Cpk from 30 samples looks like. A full worked study from raw data to report, preceded by its control chart.

**Real-world examples:** NIST worked example (S-B1) reproduced as a Phase B check. Wheeler's four-index argument (S-E5).
**Invented examples:** `ex07-bore-capability` – Ø12.000 ± 0.025 mm, 25 subgroups of 5, in control, Cpk about 1.1 (the "not close enough" case), Ppk slightly lower. `ex07-fill-weight` – one-sided lower spec, 100 values. `ex07-cpk-ci` – bootstrap and formula CI for n = 30 vs n = 125. `ex07-cpm-target` – off-target but capable, Cpm vs Cpk.

### Module 8. Process capability II

**Verified sources (8):** S-E5, S-A10, S-C6, S-C25, S-C26, S-E7, S-C3, S-B1. **Secondary:** S-C7, S-A12, S-E12.

**Outline.** Stability first (Wheeler; ISO 22514-1 definitions; the AIAG-VDA 2026 rule that Cp/Cpk apply only to stable processes; and the nuance that ISO 22514-2:2026 provides models for time-dependent processes). Non-normal data: identify the reason (mixture, bounded, skewed physics) before transforming; Box-Cox; Johnson; Clements' percentile method; nonparametric percentiles; each with limitations, and Wheeler's objection to reflexive transformation. One-sided specs. Attribute capability. Bounded characteristics (flatness, runout). How indices are misused. Reading a supplier's report and the questions to ask.

**Real-world examples:** the controversy itself, with S-C6, S-C25, S-E7, S-A10 on their respective sides.
**Invented examples:** `ex08-unstable-then-capable` – a shift after a tool change makes Ppk look fine and Cpk misleading. `ex08-flatness-lognormal` – 100 flatness values bounded at 0, transformed and untransformed capability compared. `ex08-attribute-capability` – leak-test proportion, binomial capability and DPMO. `ex08-supplier-report` – a report to critique (which sigma? stable? n?).

### Module 9. Graphical analysis

**Verified sources (6):** S-C28, S-C45, S-B12, S-A21, S-D31, S-D26. **Secondary:** S-C47, S-E27.

**Outline.** Pareto (with Juran's admission that the name is wrong). Box plots (Tukey). Scatter plots. Stratification. Multi-vari charts (Seder). Time series plots. Why you look before you test: Anscombe.

**Real-world examples:** Anscombe's quartet (S-C28); Juran 1975 (S-C45).
**Invented examples:** `ex09-pareto-leak-causes` – leak reject causes, 6 categories. `ex09-multivari-braze` – positional, cyclical, temporal variation in fillet width. `ex09-boxplot-by-shift` – bore diameter by shift.

### Module 10. Root cause analysis

**Verified sources (6):** S-A8, S-A22, S-D26, S-D12, S-D27, S-C46. **Secondary:** S-E17.

**Outline.** Cause-and-effect diagrams. 5 Whys done properly (with evidence at each step). Is/Is-not (Kepner-Tregoe). Fault tree introduction (NASA handbook). Process FMEA per the AIAG-VDA handbook: seven steps, structure, function, and failure analysis, S-O-D, Action Priority instead of RPN, with a worked PFMEA on the brazing process. Prioritization.

**Real-world examples:** Sharma & Rao 2014 used Ishikawa and PFMEA (S-C46).
**Invented examples:** `ex10-fishbone-leak`; `ex10-pfmea-braze` (full PFMEA table, AP classification computed by script from a coded AP table); `ex10-fault-tree-leak`.

### Module 11. Hypothesis testing

**Verified sources (10):** S-C20, S-B8, S-B9, S-C21, S-C22, S-C23, S-C24, S-C27, S-D30, S-A21.

**Outline.** The logic of a test; null and alternative; Type I and II errors; p-values and confidence intervals explained per the ASA statement; one- and two-sample t (Welch by default), paired t, one-way ANOVA, chi-square, tests for variances (Levene), normality tests (Shapiro-Wilk, Anderson-Darling), nonparametric alternatives, effect size (Cohen's d, with its origin in behavioural science flagged), power and sample size with the NIST worked example.

**Real-world examples:** ASA 2016 statement (S-C20); NIST sample-size example (S-B8).
**Invented examples:** `ex11-two-supplier-t` – pull strength (N) from two suppliers. `ex11-paired-before-after` – cycle time before and after a fixture change. `ex11-anova-three-machines`. `ex11-power-sample-size`. `ex11-chi-square-defect-types`.

### Module 12. Correlation and regression

**Verified sources (5):** S-B12, S-C28, S-B0, S-D1, S-A21.

**Outline.** Correlation and its traps (Anscombe; causation). Simple linear regression by hand and by script. Residual analysis per NIST 4.4.4. Multiple regression introduction. What R² does and does not tell you.

**Real-world examples:** Anscombe (S-C28).
**Invented examples:** `ex12-temp-vs-fillet` – furnace temperature vs braze fillet width. `ex12-anscombe-recompute` – recompute Anscombe's statistics. `ex12-multiple-regression` – fillet width vs temperature, flux mass, gap.

### Module 13. Design of experiments

**Verified sources (9):** S-B7, S-C31, S-C32, S-C29, S-C30, S-D24, S-D25, S-D2, S-D21. **Secondary:** S-C48.

**Outline.** OFAT and why it fails. 2ᵏ full factorials; main effects and interactions; a fully worked 2³ on the braze process (temperature, flux, gap) with effects by Yates' method by hand and by statsmodels. Fractional factorials and confounding; blocking; replication; RSM introduction (Box-Wilson). Taguchi methods and the debate (Box 1988; Nair 1992 panel), presented with both sides.

**Real-world examples:** the Taguchi debate literature (S-C29, S-C30).
**Invented examples:** `ex13-2k3-braze` (8 runs × 2 replicates). `ex13-fractional-2k5-1`. `ex13-ofat-trap` – simulated interaction that OFAT misses.

### Module 14. Lean improvement tools

**Verified sources (7):** S-E22, S-E23, S-E2, S-D16, S-D17, S-D18, S-D19. **Secondary:** S-D20, S-C40.

**Outline.** 5S, standard work, poka-yoke, SMED, kaizen events, solution selection with a Pugh matrix, piloting, and proving an improvement with data (before and after with a hypothesis test and a control chart, not a bar chart). 3M as the cautionary story about applying efficiency tools to invention.

**Real-world examples:** 3M 2007 (S-E2). Shingo's SMED claims are catalog-only, so they are described as "Shingo reports" and labelled secondary.
**Invented examples:** `ex14-smed-changeover` – changeover times before and after (s), with a two-sample test. `ex14-pugh-fixture` – five fixture concepts. `ex14-pilot-before-after` – leak rate before and after with a p-chart.

### Module 15. Variation reduction and design

**Verified sources (6):** S-C33, S-C34, S-A20, S-D21, S-D23, S-E24. **Secondary:** S-E25, S-D22.

**Outline.** Tolerance stack-up revisited from a capability angle: worst-case vs RSS (Evans), the assumptions behind RSS (independence, centring), and what a real Cpk does to the stack. Allocating tolerances using capability data. Robust design introduction. The Taguchi loss function with the Sony story labelled "as reported by Taguchi and Clausing; underlying data not independently verified". Feeding capability data back into DFM.

**Real-world examples:** Sony televisions (secondary; S-E24, S-E25).
**Invented examples:** `ex15-stack-three-parts` – three-part stack, worst-case vs RSS vs simulated with actual Cpk and a 0.5σ mean shift. `ex15-loss-function` – loss for the bore example. `ex15-tolerance-allocation`.

### Module 16. Statistical process control I

**Verified sources (10):** S-C44, S-D9, S-B2, S-B3, S-C10, S-C11, S-E19, S-A13, S-E6, S-C12. **Secondary:** S-A23, S-D3.

**Outline.** Shewhart's insight and the 1924 memo. Common vs special cause. Control limits vs specification limits (first of three treatments). X̄-R, X̄-S, I-MR built by hand from data with the constants. Western Electric and Nelson rules with the exact texts. False alarm rates and ARL (computed by script; Champ and Woodall as the reference). How often to sample; rational subgrouping revisited.

**Real-world examples:** Shewhart 1924 (S-C44); NIST worked I-MR example (S-B3) as a Phase B check.
**Invented examples:** `ex16-xbar-r-bore` (same data as ex07). `ex16-imr-furnace-temp` (individuals, °C). `ex16-xbar-s-n10`. `ex16-false-alarm-sim` – ARL simulation for rule sets.

### Module 17. Statistical process control II

**Verified sources (8):** S-B5, S-C16, S-C13, S-C14, S-C15, S-B4, S-A16, S-A13. **Secondary:** S-A14, S-A15, S-D5, S-B13.

**Outline.** p, np, c, u charts with the correct limits; over-dispersion and Laney's p′. Chart selection tree. EWMA and CUSUM introduction with NIST's example as a check. Short-run SPC (ISO 7870-8; Wheeler's Zed charts). Charts for non-normal data (individuals charts are robust; when to worry). Reacting to a signal. Out of control but within spec (second treatment of the limits distinction).

**Real-world examples:** NIST EWMA example (S-B4).
**Invented examples:** `ex17-p-chart-leak` (30 lots, varying n). `ex17-c-chart-porosity`. `ex17-ewma-shift-0.7sigma` – a small shift the Shewhart chart misses. `ex17-short-run-dnom`.

### Module 18. Control plans and sustaining gains

**Verified sources (5):** S-A6, S-A7, S-A5, S-E18, S-E12. **Secondary:** S-A19, S-A3.

**Outline.** Control plans (CP-1 structure, reaction plans, safe launch), standardization, documentation, handoff to production, linking to PPAP and IATF 16949 clause 9.1.1.1 expectations (process studies, reaction when unstable or not capable, recording significant events), ongoing capability monitoring (third treatment of limits vs specs), project closure and reporting.

**Real-world examples:** standards only (S-A6, S-E18). No public case with data was found.
**Invented examples:** `ex18-control-plan-braze` – full control plan table. `ex18-reaction-plan`. `ex18-ongoing-cpk-trend` – monthly Cpk with its CI, to show when a change is real.

### Module 19. Capstone

**Verified sources:** all of the above as used; "Why this matters" uses S-C46.

**Outline.** A brazed aluminium heat-exchanger line with a 4.2 % leak-test reject rate. Datasets provided: leak results by lot (attribute), braze joint gap (0.10 ± 0.05 mm, variable), furnace temperature log, gap gauge R&R, a 2³ DOE, and post-improvement data. Every tool used at least once, in DMAIC order, with the learner working it and a full solution in collapsible blocks.

**Invented examples:** the `ex19-*` family generated from one seeded script so that the datasets are mutually consistent (the DOE effects explain the gap shift that explains the leak rate).

---

## Part 3. Controversies and the sources on each side

| Controversy | Side A (sources) | Side B (sources) | How the course presents it |
|---|---|---|---|
| The 1.5σ shift | Motorola convention (S-E8 for the 3.4 PPM statement; S-D28 secondary); Bothe 2002's statistical rationale (S-C8) | Tadikamalla 1994 (S-C9): a definitional convention that confuses; Burns 2018 (S-E28): a permanently shifting process is not in control; Woodall 2000 on the hypothesis-testing view (S-C12) | Both Z-values reported and labelled in every sigma-level output; the shift is a convention with one published rationale and standing objections. |
| Origin of 3.4 DPMO | S-E8 (Motorola's stated target), S-C9 | – | Stated as Motorola's target; the arithmetic (6σ centred about 0.002 PPM; 4.5σ one-sided about 3.4 PPM) computed by script. |
| Cpk on non-normal data | Transform or fit: Clements (S-C6), Box-Cox (S-C25), Johnson (S-C26), ISO 22514-2 distribution models (S-A10), Kotz & Johnson review (S-C3) | Wheeler (S-E7): non-homogeneity, not shape, is usually the problem; do not transform reflexively | Show the physical reason first; then each method with its limitation; report the untransformed percentile-based PPM alongside. |
| Stability before capability | Wheeler (S-E5), NIST (S-B1, "in-control process"), AIAG-VDA 2026 (S-A2, p.38: Cp/Cpk "must only be used if the process is stable"), ISO 22514-1 (S-A9) | ISO 22514-2:2026 (S-A10) and AIAG-VDA 2026 (S-A2, pp.67–75) provide time-dependent models for processes not in statistical control, and allow Cp/Cpk for "controlled stable" processes under stated conditions (p.75) | Every capability example shows its chart first; when not stable, the index is labelled Pp/Ppk and the time-dependent models are explained as the ISO/AIAG-VDA route. |
| Which sigma defines Cpk | Legacy AIAG SPC 2005 (S-A3) and most software: Cpk from within-subgroup sigma (R̄/d₂), Ppk from overall s. Wheeler (S-E5) uses the same split (Cp with Sigma(X) within, Pp with global s). | AIAG-VDA 2026 (S-A2, pp.33, 38, 46–47, 51–52) and ISO 22514: Cp/Cpk and Pp/Ppk use the same overall-variation formula; the letter records only whether stability was proven; the within-sigma index is Cw/Cwk and is not for reporting. | **Open decision (PROGRESS.md item 7).** Proposed: teach the 2026 AIAG-VDA/ISO convention as current, teach the legacy within-sigma convention explicitly because supplier reports and Minitab-style software still use it, and have every page and calculator print the sigma estimate next to every index so the reader never has to guess. |
| Business results of Six Sigma programmes | Positive: GE's own claims (S-E3); Swink & Jacobs 2012 (S-C38, peer-reviewed ROA effect) | Negative: Fortune/Qualpro 2006 (S-E1, a competitor's correlation study); 3M (S-E2); academic view that the tools are not new (S-C35, S-C36) | Present both, note the quality of evidence for each, conclude that programme results depend on management and that the statistics are sound regardless. |
| Taguchi methods | Taguchi 1986 (S-D21), Phadke 1989 (S-D22) | Box 1988 (S-C29), Nair 1992 panel (S-C30) | Teach the loss function and the robustness idea; teach the analysis with standard factorial methods; note the SN-ratio critique. |
| Run rules and false alarms | Western Electric 1956 (S-A23, S-E19), Nelson 1984 (S-C10) | Champ & Woodall 1987 (S-C11): rules raise false alarms; Woodall 2000 (S-C12) | Give the rules verbatim, compute the in-control ARL for each set by script, and recommend using few rules deliberately. |
| Sony television story | Taguchi & Clausing 1990 (S-E25, paywalled); Phadke 1989 via S-E24 | – (no independent verification of the 1979 newspaper data) | Told as "as reported by", labelled not independently verified. |
| Pareto principle naming | Juran 1975 (S-C45) admits the misattribution | – | One paragraph; the tool is unaffected. |

---

## Part 4. Gaps and decisions for the author

1. **AIAG SPC manual.** The author supplied a licensed copy of the *AIAG & VDA SPC Manual*, 1st edition (February 2026). Targeted sections were read and page references recorded in S-A2. It supersedes the 2005 AIAG SPC 2nd edition. **It redefines the Cp/Cpk vs Pp/Ppk distinction** (same overall-sigma formula; the letter records whether stability was proven; the within-sigma index becomes Cw/Cwk). This conflicts with the convention assumed in CLAUDE.md rule 3 and with most software. See Part 3 ("Which sigma defines Cpk") and PROGRESS.md decision 7. The 2005 edition was not read; claims about it rest on S-A2 footnote 11.
1a. **AIAG-VDA FMEA Handbook.** A PDF is present in `reference/` but its filename indicates a libgen download, so it is not used as a read source; the FMEA entries (S-A8, S-E17) stay at catalog and secondary depth. If the author has a licensed copy, it can be read in Phase D for Module 10.
2. **AIAG MSA-4 and PPAP-4 thresholds** (%GRR bands, ndc ≥ 5, the 1.67 and 1.33 bands) are confirmed only by secondary sources. They will be cited as "AIAG guidelines (MSA-4; PPAP-4), confirmed via secondary sources" unless the author supplies page numbers.
3. **Modules with no fully verified real-world case with public data:** 5 (data collection), 14 (Lean, only 3M as a caution), 15 (Sony is secondary), 18 (standards only). Each will use a clearly labelled illustrative failure in "Why this matters".
4. **Motorola 1988 annual report** exceeded the fetch limit; the NIST Baldrige profile is used instead and is sufficient.
5. **The brief said "Wall Street Journal" for the 3M story; the article is BusinessWeek (Hindo, 11 June 2007).** A WSJ 2007 Home Depot / Nardelli Six Sigma piece exists (per search listing) but was not read and is not used.
6. **Commercial training sites** (GoLeanSixSigma, iSixSigma, SixSigmaDSI, 6sigma.us, and similar) are excluded as sources for any historical or numerical claim.
7. **Publisher 403s.** Abstract-depth entries can be upgraded to full text if the author has library access; nothing in the outline depends on content beyond the abstracts.

- **Phase B check sources (2026-09-09).** The harness was proved on S-B1, S-B2, S-B3, S-B4, S-B8, S-A2 p. 48, S-D33/S-E34 and S-E30. NIST prints D₄(5) = 2.115 where the exact value (2.11447) rounds to 2.114; the course tables use the exact-rounded value and note the difference. The NIST F-table page reader returned transposed cells for two entries, so those two were checked against Montgomery App. IV. The AIAG MSA 4th edition raw gauge R&R data set could not be found in an open source, so the gauge R&R engine is checked against the Minitab-published ANOVA table and by three independent implementations on constructed data.
