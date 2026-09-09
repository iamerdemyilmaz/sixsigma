# CLAUDE.md

## Project

You are building a complete, publishable online course titled **"Six Sigma for Engineers: Process Capability, SPC, and DMAIC in Practice"** (working title). The deliverable is a multi-page static HTML site with interactive calculators, deployable as-is to GitHub Pages, Netlify, or any static host with no build step.

The author is Erdem Yilmaz, a senior manufacturing engineer with about eight years of NPI experience. The course is written in his voice as a practitioner who has run capability studies, sat through supplier PPAP reviews, and had to explain to a program manager why a Cpk of 1.1 is not "close enough". It is not a certification prep course and must not claim to be one, but it should cover what a Green Belt is expected to know, and say so.

This is a statistics course. Every number in it can be checked, and readers will check them. A wrong Cpk in a worked example destroys the credibility of the whole course. The verification protocol below is therefore the most important section of this file.

## Audience

Junior to mid-level mechanical and manufacturing engineers (roughly 0 to 5 years). They have taken one statistics class and remember little of it. They can use Excel, some can use Python or Minitab. They need to run and read capability studies, set up control charts, understand a gauge R\&R report, and lead or support a DMAIC project. They do not need to derive anything. Every formula is given, explained in words, and immediately applied to numbers.

## Scope

Full Green Belt style DMAIC curriculum, with process capability and SPC treated as the core and taught in the most depth:

- Foundations: variation, distributions, descriptive statistics, sampling, the normal distribution and its limits  
- Six Sigma as a framework: history, sigma level and DPMO, the 1.5 sigma shift and its controversy, belts and roles, Lean and Six Sigma together, honest critique of the methodology  
- Define: charters, problem statements, VOC, CTQ, SIPOC, scoping  
- Measure: measurement systems analysis (gauge R\&R, bias, linearity, stability, attribute agreement), data collection, rational subgrouping, process capability (Cp, Cpk, Pp, Ppk, Cpm), non-normal capability, attribute capability, DPMO, DPU, RTY  
- Analyze: graphical analysis, root cause tools, FMEA, hypothesis testing, confidence intervals, sample size and power, correlation and regression  
- Improve: design of experiments (factorial, fractional factorial, introduction to response surface), Lean improvement tools, solution selection, piloting, linking variation reduction back to design tolerances  
- Control: control chart theory, variables charts (Xbar-R, Xbar-S, I-MR), attribute charts (p, np, c, u), run rules, EWMA and CUSUM introduction, chart selection, control plans, reaction plans, handoff and ongoing monitoring  
- Capstone: a complete DMAIC project on a fully specified synthetic dataset

## Non-negotiable rules

### 1\. Real-world examples, studies, statistics, and standards must be verified

Same rules as any credible technical publication:

- Search for and read a source before writing any historical claim, case study, statistic, or citation. Never write the claim first and look for a source after.  
- Every module ends with a **References** section: author or organization, title, publisher or site, year, URL, date accessed.  
- Every claim a skeptical quality engineer might challenge gets an inline citation `[n]` linked to the References entry.  
- Maintain `SOURCES.md` at the repo root: one entry per source, what it supports, and a status of **verified** (you read it and it says what you claim), **secondary** (cited by a credible source; original not read), or **unverified**. Unverified sources may not appear in the course. Secondary sources are labeled as such in the References.  
- Standards and handbooks must be cited by correct designation and current edition, checked by search: for example the AIAG SPC reference manual, the AIAG MSA reference manual (4th edition), the AIAG PPAP manual, AIAG-VDA FMEA handbook, ISO 22514 series, ISO 7870 series, ISO 3534, IATF 16949, ASTM E2281, the NIST/SEMATECH e-Handbook of Statistical Methods. Paraphrase; never quote standard text at length.  
- Teach controversies honestly. The 1.5 sigma shift, the origin of the 3.4 DPMO figure, the debate over Cpk on non-normal data, the requirement of statistical control before capability means anything (Wheeler and others), and the published critiques of Six Sigma programs' business results are all real and documented. Present each with its strongest sources on both sides. Never present a contested claim as settled.  
- Never invent a company case study, a named engineer, a paper, a savings figure, or a percentage. If you want a story and cannot verify one, use a clearly labeled illustrative example (see rule 2).

Candidate sources to verify, not to assume: Montgomery, *Introduction to Statistical Quality Control*; Wheeler and Chambers, *Understanding Statistical Process Control*; Wheeler, *Advanced Topics in Statistical Process Control*; Breyfogle, *Implementing Six Sigma*; Pyzdek and Keller, *The Six Sigma Handbook*; the ASQ Six Sigma Green Belt Body of Knowledge; Shewhart's original work at Bell Labs; Deming's red bead and funnel experiments; Taguchi's loss function and the widely repeated Sony television case (verify whether it is documented or apocryphal before using it); Motorola's Six Sigma origin with Bill Smith and the MAIC to DMAIC evolution; General Electric's program under Jack Welch and the reported financial claims; published critiques (search for the Fortune and Wall Street Journal coverage of Six Sigma company performance and the academic responses); Bothe, *Measuring Process Capability*; Kotz and Johnson's review of capability indices; the NIST/SEMATECH handbook throughout; peer-reviewed case studies in *Quality Engineering*, *Journal of Quality Technology*, and *International Journal of Six Sigma and Competitive Advantage*; ASQ published case studies.

### 2\. Every invented example passes the triple check

The author explicitly allows invented examples, because real datasets with full context are rare and often proprietary. Invented examples are the backbone of this course. Each one must be realistic, clearly labeled, and independently verified three ways before it appears on a page.

**Labeling.** Every invented example is introduced as illustrative: "The data below is a constructed example, not a real production run." Give it a realistic engineering setting with metric units (a bore diameter of 12.000 mm with a tolerance of ±0.025 mm, a fill weight in grams, a solder joint pull strength in N, a cycle time in seconds). Never name a real company in an invented example.

**Generation.** Every dataset is generated by a seeded script in `verification/generate.py`, saved as CSV in `verification/data/`, and embedded verbatim in the HTML page (in a table or a `<script type="application/json">` block). The learner must be able to copy the exact data into Excel or Minitab and reproduce every number on the page. Datasets must be small enough to print (typically 25 to 125 values) unless the point is large-sample behavior.

**Check 1: computed, not typed.** Every statistic shown on a page (mean, standard deviation, Cp, Cpk, Pp, Ppk, control limits, %R\&R, p-value, F ratio, effect estimate, DPMO, sigma level) is computed by `verification/compute.py` using `numpy`, `scipy`, and `statsmodels` from the CSV, and written to `verification/results/<example-id>.json`. Numbers are never typed into HTML by hand from your own arithmetic.

**Check 2: recomputed independently.** `verification/recompute.py` recomputes every number in `results/` by a different route: closed-form textbook formulas written out explicitly (Rbar/d2 for within-subgroup sigma, sample standard deviation with n-1 for overall sigma, the AIAG MSA ANOVA method for gauge R\&R, the Yates or contrast method for factorial effects) without calling the library functions used in Check 1\. Both routes must agree to the rounding shown on the page. Any disagreement is a bug in one of them; find it before proceeding.

**Check 3: consistency and reasonableness.** `verification/sanity.py` asserts known relationships and realistic ranges: Cpk ≤ Cp; Ppk ≤ Pp; Cpk \= min(Cpu, Cpl); Cpk equals Cp only when the mean is centered; the PPM predicted from Cpk matches the normal tail area from the same Z; within-subgroup sigma is not wildly larger than overall sigma; control limits use the correct constants (d2, A2, D3, D4, c4, B3, B4) for the subgroup size; %R\&R and ndc are consistent; effects in a DOE sum to the observed response means; p-values fall in \[0, 1\]; every number on the page appears in `results/` (grep the HTML for numbers and cross-check). It also confirms the narrative matches the numbers: if the text says "the process is capable", Cpk must be at or above the threshold the text names.

**Check 4 (free): the calculators agree.** The in-page JavaScript calculators are run on every example dataset by `verification/test_calculators.js` (Node) and must match `results/` to the displayed precision. This also serves as the unit test suite for the calculators.

**Record.** `EXAMPLES.md` lists every example: id, module, setting, dataset file, the three check scripts' pass status, and the date. An example with any failing check cannot appear on a page. `verification/verify_all.sh` runs everything and exits non-zero on any failure. Run it before every commit.

**Realism.** Constructed data should look like real data: use plausible process means, a standard deviation that gives an interesting Cpk (not always 1.33 or 2.00), occasional realistic features (a shift after a tool change, a subgroup with a special cause, a gauge with 25% R\&R), and rounding that matches the gauge resolution (a micrometer reading to 0.001 mm, a scale to 0.1 g). Never generate data that happens to produce a suspiciously clean answer.

### 3\. Statistical correctness rules

- Always state which sigma estimate is in use (within, from Rbar/d2 or Sbar/c4, versus overall, from the sample standard deviation) and therefore whether the index is Cp/Cpk or Pp/Ppk. Never use the terms interchangeably.  
- Capability is only reported after stability is shown. Every capability example first shows a control chart of the same data. If the process is not in control, the example says so and explains why the index is then only descriptive.  
- Normality is checked before a normal-based capability index is used, and the course shows what to do when it fails (identify the reason, transformation, alternative distribution, or a nonparametric percentile method), with the limitations of each.  
- p-values are explained correctly (the probability of data at least this extreme if the null hypothesis were true), never as the probability the hypothesis is true. Confidence intervals are explained correctly. Effect size and practical significance appear alongside every hypothesis test.  
- Sample sizes used in examples must be large enough for the conclusion drawn, and the course says what the confidence interval on a Cpk from 30 samples actually looks like.  
- Control limits are computed from the data with the standard constants; specification limits never appear on a control chart as limits. The course explains this distinction at least three times, in three different modules, because it is the most common error in industry.  
- Use the AIAG MSA acceptance guidelines (%R\&R under 10% acceptable, 10 to 30% conditional, over 30% unacceptable; ndc of 5 or more) and cite them as guidelines with their source, not as laws.  
- Statistical tables (Z, t, chi-square, F, control chart constants) included in the appendix are generated by `scipy` in `verification/tables.py`, not copied from a book, and are compared against a published table for a sample of entries.

### 4\. Do not use the author's employer information

No case study, data, part, supplier, or process detail that could only come from his employers. Leave `<!-- AUTHOR: optional personal note here -->` HTML comments where a personal anecdote would fit.

### 5\. Do not copy text or images from other courses, software documentation, or books

Minitab, JMP, and ASQ materials and the NIST handbook are good sources for method descriptions and must be cited, but paraphrase the text and draw every figure yourself as inline SVG. Never hotlink or embed images from other sites.

### 6\. Metric units only

All engineering quantities in SI or metric (mm, µm, g, N, °C, MPa, s). No inches, mils, or pounds in examples.

### 7\. No placeholder content in the final deliverable

No lorem ipsum, no TODO, no empty quiz, no calculator that returns NaN on the page's own example data.

## Curriculum

One HTML page per module. Target 2,500 to 4,500 words of body text per module plus tables, figures, examples, exercises, and quiz. The capability and SPC modules (7, 8, 9, 17, 18\) may run longer. Note any deviation in `PROGRESS.md`.

**Part 1: Foundations**

0. **Introduction: What Six Sigma is and is not** — origin at Motorola, spread through GE and others, what a sigma level means, DMAIC at a glance, belts and roles, Lean and Six Sigma, what the published critiques say and what to take from them, how to use this course.  
1. **Variation and basic statistics** — types of data, mean, median, range, standard deviation (population versus sample), histograms, the normal distribution, other distributions engineers meet (lognormal, Weibull, binomial, Poisson), sampling versus population, the central limit theorem shown with a simulation.  
2. **Process thinking** — SIPOC, process maps, value stream basics, the eight wastes, common versus special cause variation introduced in words before any chart.

**Part 2: Define**

3. **Defining a project** — problem statements that survive scrutiny, project charters, business case, scope and boundaries, VOC to CTQ translation, Kano model, stakeholder analysis, what a good Green Belt project looks like in a manufacturing setting.

**Part 3: Measure**

4. **Measurement systems analysis** — why the gauge comes before the process, bias, linearity, stability, repeatability and reproducibility, crossed gauge R\&R by the ANOVA method with a full worked example, %R\&R, %Tolerance, ndc, attribute agreement analysis, what to do with a bad gauge.  
5. **Data collection and sampling** — operational definitions, sampling plans, rational subgrouping and why it decides everything downstream, data collection sheets, common data quality failures.  
6. **Sigma level, DPMO, DPU, RTY** — defects versus defectives, opportunities and how they get gamed, first time yield versus rolled throughput yield, sigma level conversion, the 1.5 sigma shift explained and its history and controversy presented fairly.  
7. **Process capability I** — Cp, Cpk, Cpu, Cpl, Pp, Ppk, Cpm, within versus overall sigma, short-term versus long-term, capability to PPM conversion, the 1.33 and 1.67 conventions and where they come from (AIAG PPAP), confidence intervals on Cpk, a full worked capability study from raw data to report.  
8. **Process capability II** — stability first, non-normal data, one-sided specifications, transformations and alternative distributions, attribute capability, capability of bounded processes (flatness, runout), how capability indices are misused, how to read a supplier's capability report and the questions to ask.

**Part 4: Analyze**

9. **Graphical analysis** — Pareto, box plots, scatter plots, stratification, multi-vari charts, time series plots, why you look before you test.  
10. **Root cause analysis** — cause and effect diagrams, 5 whys done properly, is/is not, fault tree introduction, process FMEA per the AIAG-VDA handbook with a worked example, prioritization.  
11. **Hypothesis testing** — the logic of a test, null and alternative, Type I and II error, p-values and confidence intervals explained correctly, one and two sample t-tests, paired t, one-way ANOVA, chi-square, tests for variances, normality tests, nonparametric alternatives, power and sample size with a worked example.  
12. **Correlation and regression** — correlation and its traps, simple linear regression, residual analysis, multiple regression introduction, what R² does and does not tell you.

**Part 5: Improve**

13. **Design of experiments** — one factor at a time and why it fails, 2^k full factorials, main effects and interactions, a fully worked 2^3 example with effect calculation by hand and by script, fractional factorials and confounding, blocking, replication, introduction to response surface methods, Taguchi methods and the debate about them.  
14. **Lean improvement tools** — 5S, standard work, poka-yoke, SMED, kaizen events, solution selection with a Pugh matrix, piloting and how to prove an improvement with data (before and after with a hypothesis test, not a bar chart).  
15. **Variation reduction and design** — tolerance stack-up revisited from a capability angle, allocating tolerances using capability data, robust design introduction, the Taguchi loss function, feeding capability data back into DFM.

**Part 6: Control**

16. **Statistical process control I** — Shewhart's insight, common versus special cause, control limits versus specification limits, Xbar-R, Xbar-S, I-MR charts built by hand from data with the constants, Western Electric and Nelson rules, false alarm rates, how often to sample.  
17. **Statistical process control II** — attribute charts (p, np, c, u), chart selection tree, EWMA and CUSUM introduction, short-run SPC, charts for non-normal data, reacting to a signal, what to do when a chart is out of control and the process is still within specification.  
18. **Control plans and sustaining gains** — control plans, reaction plans, standardization, documentation, handoff to production, linking to PPAP and IATF 16949 expectations, ongoing capability monitoring, project closure and reporting.

**Part 7: Capstone**

19. **Capstone: a DMAIC project end to end** — a fully specified synthetic manufacturing problem (for example, a leak test failure rate on a brazed assembly, or a bore diameter with a Cpk of 0.9) with all datasets provided, taken through every phase with every tool used at least once. The learner works it; a full solution is provided in collapsible blocks.

**Supporting pages:** `index.html` (landing page, outline, how to use), `calculators.html` (all calculators on one page for reuse after the course), `tables.html` (statistical tables and control chart constants, generated), `formulas.html` (formula sheet), `glossary.html`, `references.html` (consolidated), `about.html`.

## Interactive calculators

All in vanilla JavaScript with no external libraries, no CDN, no server. Charts are rendered as inline SVG generated by the JS. Each calculator appears inside the module where it is taught and again on `calculators.html`. Each one is pre-loaded with the module's example data so the learner sees it agree with the text, and accepts pasted data (comma, space, tab, or newline separated).

Required calculators:

1. **Descriptive statistics and histogram** with optional specification limits overlaid and a normal curve fit.  
2. **Process capability**: input data (optionally with subgroup size), USL, LSL; output Cp, Cpk, Cpu, Cpl, Pp, Ppk, Cpm (with target), within and overall sigma, expected PPM within and overall, and a histogram with spec limits. Shows which sigma estimate feeds which index.  
3. **Sigma level and DPMO converter**: DPMO ⇄ sigma level (with and without the 1.5 shift, both labeled), yield, DPU, RTY from a chain of steps.  
4. **Control chart builder**: paste data, choose I-MR, Xbar-R, Xbar-S, p, np, c, or u; compute limits from the data with the correct constants; draw the chart; flag Western Electric and Nelson rule violations; option to freeze limits from a baseline period.  
5. **Gauge R\&R (crossed, ANOVA method)**: parts × operators × replicates grid input; output ANOVA table, variance components, %Contribution, %Study Variation, %Tolerance, ndc.  
6. **Two-sample t-test and one-way ANOVA** with confidence intervals and a simple effect size.  
7. **Sample size for a two-sample t-test** given delta, sigma, alpha, and power.  
8. **2^k factorial effects calculator** (k \= 2 or 3): enter responses, get main effects, interactions, and a Pareto of effects.  
9. **Central limit theorem and control chart simulator** (teaching tool): pick a parent distribution and subgroup size, draw samples, watch the distribution of means; add a process shift and watch how many subgroups it takes each chart type and rule set to detect it.

Numerical functions needed (normal CDF and inverse, t and F and chi-square CDFs, erf) are implemented in `assets/js/stats.js` with the algorithm and its accuracy cited in a code comment, and tested against `scipy` in `verification/test_calculators.js` on at least 200 points each. Accuracy targets: normal CDF to 1e-7, inverse normal to 1e-6, t and F CDF to 1e-5.

## Structure of every module page

1. Module number and title  
2. **Learning objectives** (3 to 6 bullets starting with a verb)  
3. **Why this matters** (2 to 3 paragraphs and one verified real-world example or one clearly labeled illustrative failure)  
4. **Core content** with H2 and H3 headings; every formula shown, explained in words, then applied to numbers  
5. **Worked examples**: at least three per module, each with its labeled dataset, every number traceable to `verification/results/`  
6. **Calculator** (where applicable), pre-loaded with the module's example  
7. **Common mistakes**: 5 to 8, each with the consequence and the fix  
8. **Exercises**: at least two problems with data, full solutions in collapsible `<details>` blocks, solutions verified by the same protocol  
9. **Quiz**: 8 to 12 questions, multiple choice and numeric, scored in the browser, answers with one-sentence explanations  
10. **Key takeaways**: 5 to 7 bullets  
11. **References**  
12. Previous / next navigation

## Site and code requirements

- Plain HTML5, CSS, vanilla JavaScript. No frameworks, no build step, no CDN. Works from a `file://` open and from any static host.  
- File layout:  
    
  index.html  
    
  modules/00-introduction.html ... modules/19-capstone.html  
    
  calculators.html, tables.html, formulas.html, glossary.html, references.html, about.html  
    
  assets/css/course.css  
    
  assets/js/course.js        (navigation, quiz engine, progress)  
    
  assets/js/stats.js         (numerical functions)  
    
  assets/js/calculators.js   (calculator UI and SVG charts)  
    
  verification/generate.py, compute.py, recompute.py, sanity.py, tables.py  
    
  verification/test\_calculators.js, verify\_all.sh  
    
  verification/data/\*.csv, verification/results/\*.json  
    
  SOURCES.md, EXAMPLES.md, PROGRESS.md, README.md  
    
- Shared header and navigation, current module highlighted, collapsible sidebar on narrow screens, mobile responsive, no horizontal page scroll; tables and wide charts scroll inside their own containers.  
- Progress tracking in `localStorage` wrapped in try/catch; progress bar on the index page.  
- Light and dark themes via `prefers-color-scheme`. Plain, readable, system font stack, 16 to 18 px body text, around 70 characters per line. No decorative colored boxes.  
- Math in plain HTML with `<sub>`, `<sup>`, and Unicode where possible; a formula that needs more than that is rendered as inline SVG or a clearly formatted block. No MathJax or KaTeX from a CDN.  
- All figures are inline SVG with `<title>` and `<desc>`, consistent stroke widths, a two-color scheme that works in both themes, and axis labels with units.  
- Print stylesheet so a module prints as a clean handout.  
- Semantic HTML, alt text, keyboard-accessible quiz and calculator controls, sufficient contrast.  
- Footer with copyright placeholder, license line (suggest CC BY-NC-SA 4.0 for content and MIT for code; author to confirm), last-updated date.

## Working method

**Phase A: Research and outline.** For each module, search for and read sources. Produce `SOURCES.md` with at least 5 verified sources per module and a one-paragraph outline per module. For each module, list the real-world examples you intend to use with their sources and the invented examples you intend to construct with their settings and the point each one makes. Present the outline and stop for the author's approval.

**Phase B: Verification infrastructure first.** Build the `verification/` scripts, `stats.js`, and the test harness before any course page. Prove them on a small set of textbook examples with known answers (for example, worked examples from the NIST handbook or Montgomery, cited) and record the agreement in `EXAMPLES.md`. Stop and show the author the results.

**Phase C: Scaffold and reference module.** Build `index.html`, the CSS, the shared JS, and Module 7 (Process capability I) complete with its calculator as the reference implementation. Stop and ask the author to review in a browser.

**Phase D: Build modules** in curriculum order, one at a time. After each module: run `verify_all.sh`, run an HTML validator if available, check external links, update `PROGRESS.md` and `EXAMPLES.md`, commit with a clear message.

**Phase E: Verification pass.** Reread every module against: every number traceable to `results/`; every example labeled real (with source) or illustrative; every citation resolves; every References entry is verified or secondary in `SOURCES.md`; sigma estimate stated for every index; stability shown before every capability; p-values explained correctly everywhere; metric units only; no employer content; no placeholders; every quiz scores correctly; every calculator reproduces its page's example. Record results in `PROGRESS.md`.

**Phase F: Ship.** `README.md` with deployment steps for GitHub Pages and Netlify, how to edit a module, and how to run `verify_all.sh`. Final summary: word count, number of sources, number of examples (real versus illustrative), number of figures, calculator test results, and any claims removed or relabeled because they could not be verified.

## Token discipline and model selection

This project runs across many sessions. The handoff files, not the conversation history, are the memory of the project. Behave accordingly.

**Session boundaries.** Each session does one bounded unit of work: one phase of Phase A or B, or one module in Phase D. When the unit is finished and verified, update `PROGRESS.md`, commit, and tell the author the session should end. Do not start the next module in the same session unless the author explicitly asks.

**`PROGRESS.md` must make a fresh session self-sufficient.** Keep at its top, always current: (1) a "Resume here" line that a fresh session can act on without any other context, for example "Phase D. Modules 0 to 8 complete and verified. Next: build Module 9 (Graphical analysis) following the reference implementation in modules/07-capability-1.html"; (2) a "Recommended model" line (see below); (3) any open decisions waiting on the author. Then the log of completed work and deviations.

**Do not re-read what you do not need.** Never read a finished module unless the current task requires it. When building a new module, read the reference module (Module 7\) once for structure, and `assets/css/course.css` and `assets/js/course.js` only if you need an API from them; do not re-read them every session. Read `SOURCES.md` only for the module being built (search it by module heading rather than reading the whole file). Use `grep` and targeted line-range reads instead of whole-file reads for files over a few hundred lines. Never `cat` the CSV datasets or results JSON into the context; run the scripts and read their summary output.

**Do not narrate.** Keep progress messages to the author short. Do not restate the plan or CLAUDE.md rules in chat.

**Tell the author when to switch models.** At the start of every session and at every phase boundary, print one line in this exact form: `Model recommendation: <model> for <the work about to happen>, because <one clause>.` Use this guidance:

- Phase A (research, source verification, outline): the strongest available model. Judgment about whether a source says what it appears to say is the whole job here.  
- Phase B (verification harness, `stats.js`, numerical accuracy) and Phase C (scaffold and reference module): the strongest available model. Everything downstream depends on these being right.  
- Phase D (building modules 0 to 19 against the reference): a mid-tier model such as Sonnet is sufficient for most modules, because the structure is fixed and `verify_all.sh` catches numerical errors regardless of which model wrote the page. Recommend the strongest model again for modules 7, 8, 11, 13, 16, 17, and 19, where the statistical reasoning and the controversies need the most care.  
- Phase E (verification pass): the strongest available model.  
- Phase F (README and summary): a mid-tier model.

**How the author switches with the least token cost.** A model switch inside a live session discards the prompt cache, and the next turn re-reads the whole conversation at full price. So never recommend switching mid-session. The routine is: finish the unit of work, update `PROGRESS.md`, commit, then the author ends the session and starts a new one with the new model, for example `claude --model sonnet`, and pastes the standing resume prompt: "Read CLAUDE.md and the top of PROGRESS.md, then continue from the Resume here line." A fresh session starts with a context of only those two files plus what the current module needs, which is the cheapest possible state. Only recommend `/compact` if the author chooses to continue in the same session and the context has grown large; recommend `/clear` plus the resume prompt over `/compact` whenever the unit of work is finished.

**Reuse from the DFx course.** If the author places the DFx course's `assets/css/course.css`, `assets/js/course.js`, and one finished module in a `reference/` folder at the repo root, start from those for the shared look, navigation, quiz engine, and progress tracking rather than designing them again. Read them once in Phase C and adapt; do not re-read them afterward. Keep the visual style consistent between the two courses so they read as a series.

## Style

- Practitioner voice, direct, specific. "We" and "you" are fine. No marketing language.  
- Short paragraphs. Tables for numbers. Prose for reasoning. A formula is never left unexplained.  
- Every rule of thumb comes with its reason and its source.  
- Commas or en dashes rather than long dashes.  
- Say when something is contested or when practice varies. "Your customer may require 1.67 for safety characteristics; ask" is better than a universal rule.

## When to stop and ask

Stop when: a real-world example cannot be verified and you want to substitute; two credible sources disagree on a method; a verification check fails and you cannot find the cause within a reasonable effort; the curriculum needs reordering; a licensing or branding decision comes up. Do not ask permission to continue routine building.

