# PROGRESS.md

**Resume here:** Phase B is complete: `verification/` (tables.py, generate.py, compute.py, recompute.py, sanity.py, test_calculators.js, verify_all.sh), `assets/js/stats.js` and `EXAMPLES.md` exist and `bash verification/verify_all.sh` passes every check (2026-09-09). Next: **Phase C.** (1) Copy `reference/course.css` and `reference/course.js` to `assets/` and adapt (add the calculators, tables and formulas pages to the nav list; MODULES array for the 20 modules). (2) Build `assets/js/calculators.js`: UI and inline-SVG charts only, calling the engines in `assets/js/stats.js` (`Stats.capability`, `Stats.imrChart`, `Stats.xbarRChart`, `Stats.xbarSChart`, `Stats.pChart` etc., `Stats.grr`, `Stats.factorial`, `Stats.ttest2`, `Stats.anova1`, `Stats.sampleSize`, `Stats.dpmo`, `Stats.runRules`; see the file header). (3) Build `index.html` and `modules/07-capability-1.html` as the reference implementation. Register the Module 7 illustrative datasets in `verification/generate.py` with ids `m07-*` (the running bore Ø12.000 ± 0.025 mm example, 25 subgroups of 5, plus at least two more), run `verify_all.sh`, and mark every number on the page with `<span data-ex="id" data-key="path" data-dp="n">` and declare the ids in `<meta name="examples">` so sanity.py cross-checks the page (see the sanity.py docstring). The `hb-*` datasets are harness-only and must not appear on pages. Stop and ask the author to review in a browser.

**Recommended model:** the strongest available model for Phase C (scaffold, calculators.js and the Module 7 reference implementation), because every later module copies its structure.

**Open decisions waiting on the author:** none. All Phase A decisions were made on 2026-09-09.

**Decisions made (2026-09-09):**

1. Module outlines and example plans in `SOURCES.md` Part 2: **approved**.
2. Capstone: **brazed aluminium heat-exchanger line**, leak-test reject rate driven by braze-joint gap. The bore Ø12.000 ± 0.025 mm stays the running example for Modules 7, 8, and 16.
3. AIAG MSA-4 and PPAP-4 thresholds: cite as guidelines, marked "confirmed via secondary sources". The AIAG & VDA SPC Manual's own target tables (S-A2, Tables 8-1 and 9-3) are cited directly with page numbers.
4. Sony television story: told "as reported by Taguchi and Clausing and by Phadke", labelled not independently verified.
5. License: **CC BY-NC-SA 4.0 for content, MIT for code**.
6. Deployment: the course is published on the author's portfolio site **erdemyilmaz.me** as a new course alongside the DFx course at `https://erdemyilmaz.me/dfx/`. Phase C must match the DFx course's look, navigation, footer, and URL layout (see "Deployment target" below). No finished DFx module page is in `reference/`; the live site is the reference.
7. **Cpk convention:** teach the 2026 AIAG & VDA / ISO 22514 convention as current (Cp/Cpk and Pp/Ppk share the overall-sigma formula; the letter records whether stability was proven; the within-sigma index is Cw/Cwk). Teach the legacy 2005 AIAG convention explicitly as what supplier reports and Minitab-style software still print (Cpk from R̄/d₂, Ppk from overall s). Every page and calculator prints the sigma estimate beside every index; the capability calculator has a convention toggle. CLAUDE.md rule 3 is read in this light.

## Deployment target (recorded 2026-09-09)

- Portfolio: `https://erdemyilmaz.me/` (static site; `assets/css/site.css`, pages `index.html`, `about.html`). The home page lists the DFx course and says two more courses are "in preparation".
- DFx course: `https://erdemyilmaz.me/dfx/`. Layout: `index.html`, `modules/<NN-slug>.html` (e.g. `modules/00-introduction.html`), `glossary.html`, `references.html`, `about.html`, `assets/css/course.css`, `assets/js/course.js`. Navigation, module list, prev/next, quiz engine and progress are built by `course.js` from a `MODULES` array (`{num, slug, title, built}`); pages set `data-root` on `<body>` ("" at top level, "../" inside `modules/`). Header has "Back to erdemyilmaz.me"; footer has copyright, licence line, last-updated date. Progress stored in the browser only; a module counts as complete at a 70 % quiz score.
- `reference/course.css` and `reference/course.js` are byte-identical to the live DFx files apart from CRLF line endings. Phase C starts from them; the DFx course has no `calculators.html`, `tables.html`, or `formulas.html`, so those pages are new and must be added to the nav list in the copied `course.js`.
- Proposed path for this course: `https://erdemyilmaz.me/six-sigma/` (author to confirm the slug when deploying; nothing in the build depends on it because all links are relative).

## Environment (set up 2026-09-09)

- Python 3.11.9 (Windows Store build); installed numpy 2.4.6, scipy 1.17.1, pandas 3.0.5, statsmodels 0.15.0, pypdf.
- Node v24.19.0 and npm 11.17.0 installed via winget (OpenJS.NodeJS.LTS). New shells pick it up from PATH; an already-open shell may need its PATH refreshed.
- `CLAUDE.md` extracted from `sixsigmacourseclaudecodeprompt.md` (the source prompt file is kept in the folder).

## Log

### 2026-09-09, session 1: Phase A

- Confirmed the environment (above).
- Researched sources for all 20 modules. `SOURCES.md` lists 23 standards and manuals, 14 NIST handbook sections, 48 journal articles, 32 books, and 29 articles or web pages, each with status and reading depth. Every module has at least five verified sources.
- Read in full: NIST 6.1.6, 6.3.2.1, 6.3.2.2, 6.3.2.4, 2.4, 5.3.3, 7.2.2.2, 1.3.6.6.1, 8.1.6, 4.4.4; Wheeler 2019, 2015, 2011 columns; Nelson 1984; ASA 2016 p-value statement; Deming 1975; Juran 1975; GE 1998 annual report letter; NIST Baldrige Motorola 1988 profile; BusinessWeek 3M 2007; Fortune 2006 passage; Best and Neuhauser 2006; ISO 22514-1:2014 and ISO 7870-8:2017 scope previews; ASQ CSSGB BoK 2022; Deming Institute and Lean Enterprise Institute pages.
- Deviations from the brief: the 3M article is BusinessWeek, not the Wall Street Journal. The AIAG SPC manual has been replaced by the joint AIAG & VDA SPC Manual, 1st edition (July 2026); the course will cite that as current. ISO 22514-2 is now the 2026 (third) edition. Commercial training sites were excluded as sources.
- No HTML or verification code written (per the kickoff instructions).

### 2026-09-09, session 1 (continued): AIAG & VDA SPC Manual read

- Author placed a licensed, permission-protected PDF of the AIAG & VDA SPC Manual (1st ed., Feb 2026, 144 pp.) in `reference/`. Text extracted locally with pypdf to the session scratchpad (not into the repo); targeted sections read. SOURCES.md entry S-A2 upgraded to verified (full, targeted) with page references; S-A3 note updated; new controversy row and Part 4 items 1 and 1a added.
- Key finding: the manual changes the Cp/Cpk vs Pp/Ppk definition (see open decision 7). Other items now verifiable with page numbers: n ≥ 125 in 25 subgroups of 5; target tables by characteristic class; five stability rules; MSA as prerequisite; ISO 22514-2 time-dependent models; one-sided natural limits where Cpk may exceed Cp; outlier handling; tolerance limits never drawn on control charts.
- The FMEA PDF in `reference/` (libgen filename) is not used as a source.

### 2026-09-09, session 2: Phase B, verification harness

- `git init`; `.gitignore` excludes `reference/*.pdf` (licensed) and caches. First commit covers Phase A and Phase B.
- Built `verification/tables.py` (d₂, d₃ by numerical integration, c₄ from the gamma function, derived A₂ … E₂ for n = 2 to 25, rounded to published precision and checked against NIST 6.3.2.1, AIAG & VDA pp. 97–98 and Montgomery App. VI; Z, t, χ², F tables checked against NIST 1.3.6.7.x; scipy reference points for the JS tests; embeds the constants table into `stats.js`), `generate.py` (seeded registry, CSV plus JSON metadata with published expected values), `compute.py` (numpy, scipy, statsmodels route), `recompute.py` (plain-Python closed-form route with its own incomplete beta and gamma functions), `sanity.py` (relationship checks and the HTML cross-check convention: `<meta name="examples">`, `data-ex`/`data-key`/`data-dp`, `data-claim` with `data-min`/`data-max`, and a scan that every number with two or more decimals on a page is traceable), `assets/js/stats.js` (numerical functions and all calculator engines, UMD so Node can test it), `test_calculators.js`, `verify_all.sh`.
- Results: 8 textbook check examples, 63 published values matched (NIST 6.1.6, 6.3.2.2, 6.3.2.4, 7.2.2.2; AIAG & VDA p. 48 one-sided example with USL inferred as 0.40 mm; Montgomery plasma etch 2³ via UW STAT 502 notes; Minitab crossed gauge R&R ANOVA table). 686 quantities agree between the two Python routes; 1,896 values agree between Python and JavaScript; stats.js matches scipy to 1e-13 or better on 2,000+ points. Details in `EXAMPLES.md`.
- Deviations and notes: NIST D₄(5) is printed 2.115, exact rounds to 2.114 (course uses 2.114 and notes it). The individuals chart uses 3·MR̄/1.128, not the tabulated E₂ = 2.660, so that NIST's UCL 55.8041 is reproduced to four decimals. The AIAG MSA raw gauge R&R data set was not found in an open source; the ANOVA-table-to-variance-components step is checked against Minitab's published output, the raw-data step by three independent implementations. Capability results store `overall.*` (Pp/Ppk formula), `within.*` (Cw/Cwk, AIAG & VDA 2026) and `legacy.*` (2005 labels), plus a stability flag and the 2026 label the page should use; the quantile and z-score methods coincide with these for normal data and will be extended for non-normal data in Module 8.
- Environment note: Node is not on the Git Bash PATH; `verify_all.sh` finds `/c/Program Files/nodejs/node.exe`. Long heredocs fail in the Bash tool; write scripts to files instead.
