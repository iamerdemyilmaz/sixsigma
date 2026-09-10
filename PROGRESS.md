# PROGRESS.md

**Resume here:** **Phases E and F are complete. The course is finished.** All 20 modules, all 7
supporting pages (`index`, `calculators`, `tables`, `formulas`, `glossary`, `references`, `about`), the
9 calculators, the verification suite and `README.md` are built, verified and committed.
`bash verification/verify_all.sh` passes: 172 examples, 4,829 quantities agreeing between the two
independent Python routes, 9,655 values agreeing between Python and the JavaScript engines, 1,573 page
checks. There is no next unit of work queued. If the author asks for more, the open items are the
two standing invitations under "Still open, for the author only" below (both are review requests, not
blockers) and any correction the author finds when reading the live site.

**Recommended model:** whatever suits the specific request. There is no phase in progress. Content
corrections and new modules would want the strongest available model for the statistics and the
sources; a mid-tier model is fine for copy edits, deployment and README work.

**Deployed.** The Phase E and F commits were pushed to `main` on 2026-09-10 and are live at
`https://erdemyilmaz.me/sixsigma/`. GitHub Pages serves the repository root, so any future correction
goes live by committing and pushing `main`; there is no build step and nothing else to run.

**This file was trimmed on 2026-09-10** once the course was finished: it was 119 KB, most of it a
session-by-session build log that a fresh session pays for in context and cannot act on. See "Build
history" at the end for how to get the full log back out of git.

---

## Phase E: the verification pass (2026-09-10)

Run as CLAUDE.md defines it: every module reread against every number tracing to `results/`, every
example labelled real-with-source or illustrative, every citation resolving, the sigma estimate stated
for every index, stability shown before every capability, p-values explained correctly, metric units
only, no employer content, no placeholders, every quiz scoring correctly, every calculator reproducing
its page's example. The mechanical parts were done by scripts written for the pass (kept in the session
scratchpad, not the repo, because they are one-off audits rather than part of the build): a page audit
for structure, citations, links, units, placeholders and SVG accessibility; a dataset-printing check; a
numeric-quiz-answer traceability check; and an external link checker.

**What passed unchanged.** No broken internal links, no dangling anchors, no `<svg>` missing a
`<title>` or `<desc>`, no hotlinked image, no CDN or external stylesheet, no placeholder text, no
non-metric unit anywhere in the course, no employer-derived content, and the `<!-- AUTHOR: -->` hooks in
place (12 anecdote hooks across the modules, plus the footer copyright hook on all 27 pages). Of 152 unique external URLs, none is dead: the 39 that do not return 2xx
are publisher and standards-body paywalls (Taylor & Francis, Oxford, ISO, ASQ, Wiley, Sage, INFORMS,
PubMed, Emerald) returning 403 to an automated request, which is bot protection rather than link rot.
Every capability example on every page already showed a control chart or an explicit stability
statement of the same data first. The "control limits are not specification limits" point is made
explicitly in Modules 7, 16 and 18, as the brief requires. Every p-value explanation in the course is
correct; the audit's remaining flags on Modules 11, `formulas.html` and `glossary.html` are the
*negations* ("it is **not** the probability that the hypothesis is true"), which is the wording the
brief asks for.

**What was wrong, and was fixed.**

1. **A wrong quiz answer.** Module 13, quiz question 2: a 2² design with cell means 12, 14, 13, 20 was
   keyed as a main effect of A of 4.75, tolerance ±0.02. The correct value is
   ((14 + 20) − (12 + 13))/2 = 4.5, so a learner who did it right was marked wrong. Answer, explanation
   and answer key corrected. This was the only wrong answer in the course: all 218 questions across the
   26 quizzes were then graded in the browser against their declared answers and all scored 100 %, with
   every explanation revealing.
2. **Five supporting pages did not exist.** `tables.html`, `formulas.html`, `glossary.html`,
   `references.html` and `about.html` were in `course.js`'s `PAGES` array as `built: false` and had
   never been written. All five are now built and marked built. `tables.html` (Z, t, chi-square, F and
   the control chart constants for n = 2 to 25) is generated from `verification/results/_tables.json`,
   so it is computed rather than copied, as rule 3 requires. `references.html` (152 unique sources, 209
   citations) is generated from the modules' own References lists, so it cannot drift out of step with
   them. `glossary.html` has 50 entries, `formulas.html` 10 formula blocks covering every formula the
   course uses, and `about.html` states what the course is and is not, how the numbers are verified and
   the licence.
3. **Module 12 was below the brief on structure.** It had two worked examples where the brief requires
   three, and one exercise where it requires two. Added Worked example 3 (a pooled regression whose
   slope reverses sign when stratified by spray nozzle: Simpson's paradox on continuous data, with a
   new two-panel figure drawn from the actual data) and Exercise 2 (an r of −0.146 over a strong
   relationship with an interior optimum, resolved with a quadratic fit). Five new verified datasets.
4. **Module 10 had two worked examples, not three.** Added Worked example 3: verifying a candidate root
   cause by turning it off and on, with a two-sample t-test on the braze gap before and after replacing
   a worn fixture pin. This also supplies the discipline the module's own 5 Whys section calls its whole
   value but had not previously demonstrated with data.
5. **Fourteen datasets were used but never printed.** The brief requires every dataset to be embedded
   on its page so a learner can reproduce the numbers. `m04-grr-scale`, `m05-rounding-fine`,
   `m05-ex1-naive`/`-rational`, `m09-boxplot-shift1/2/3`, `m09-ex2-multivari`, `m12-mreg-fillet`,
   `m12-ex1-mreg`, `m18-month1` to `-month5` and `m18-ex2-montha/b/c` are now printed as collapsible
   data tables. The print stylesheet already expands closed `<details>` blocks, so they survive
   printing. Datasets printed in the module that introduces them and reused later by reference, the
   published NIST and Montgomery check datasets (cited to the source that holds them), and the Monte
   Carlo simulations (whose seed and parameters are embedded instead) were left as they were.
6. **Twenty-six References entries were never cited inline.** Each was either given its inline citation
   at the claim it actually supports (the AIAG MSA bands' two corroborating secondaries in Module 4;
   NIST's normal-distribution and c/p chart pages in Modules 6 and 17; Harry 1988 and Harry & Schroeder
   at the 1.5σ shift's origin; Deming's *Out of the Crisis* at operational definitions; Wheeler &
   Chambers at rational subgrouping; NIST 4.4.4 at model fit; Chase & Parkinson at statistical
   tolerancing; the two AIAG SPC manual editions at Module 18's Cp-versus-Pp naming, which also gained a
   paragraph explaining why that module reports Ppk) or explicitly marked as further reading that no
   single claim rests on. The audit script now recognises that marking, so the convention is
   enforceable.
7. **Three modules were below the 2,500-word body-text target** (6, 9 and 10, at 2,283, 2,167 and
   2,315). Each gained a substantive section rather than padding: "Which metric to report, and to whom"
   in Module 6, "When to stop looking and start testing" plus "Reading a plot honestly" in Module 9, and
   Module 10's new worked example. All three are now between 2,640 and 2,780.
8. **Smaller corrections.** Module 12 printed R² as "0.5 × 100, i.e. about 48 %" (an artefact of quoting
   a rounded value through the traceability spans) and mislabelled a plain R² of 0.876 as an adjusted
   R², with a footnote apologising for it; both fixed, the second by using the simple fit's own
   `r2_adj`. Module 18 twice described constructed data as "real numbers", now "the computed intervals".
   Modules 8 and 17 had eight key takeaways where the brief allows five to seven; two pairs merged.
   `index.html` no longer says modules are published as they are finished, and now links the five new
   reference pages.

**Deviations from the brief, recorded as required.**

- **Word counts.** The brief targets 2,500 to 4,500 words of body text per module and allows Modules 7,
  8, 9, 17 and 18 to run longer. Over target: 7 (5,312), 8 (5,790), 17 (4,819) and 16 (4,570), all
  explicitly permitted as the capability and SPC core; and 0 (4,842), 1 (4,846) and 11 (4,890), which
  are not on that list. Those three are left long deliberately: Module 0 carries the historical and
  critique material that the rest of the course cites rather than repeating, Module 1 is the statistics
  refresher every later module leans on, and Module 11 covers eight tests. Under target: Module 19
  (1,807 words of prose), which is the capstone; the brief specifies it as a project the learner works
  with the solution in collapsible blocks, and its twelve `<details>` solution blocks, which the count
  excludes, are the bulk of the module.
- **Module 19 has no `id="exercises"` section.** The whole module is the exercise, as the brief
  specifies for the capstone.
- Word counts above are prose only: text inside `<p>`, `<li>`, `<h1>` to `<h3>`, `<dt>` and `<dd>`
  within `<main>`, excluding tables, figures, forms and `<details>` blocks, which the brief counts
  separately ("plus tables, figures, examples, exercises, and quiz").

## Phase F: ship (2026-09-10)

`README.md` written: what is in the repository, deploying to GitHub Pages (including the custom-domain
arrangement actually in use) and to Netlify, running `verify_all.sh` and what its output means,
previewing locally, editing a module, why numbers may not be edited by hand and what the
`data-ex`/`data-key`/`data-dp` contract does, how to add an example, a quiz question or a page, the
conventions the course commits to, and how to send a correction.

**Final figures.** 20 modules and 7 supporting pages. About 74,000 words of body prose across the
modules, plus tables, figures, exercises and quizzes. 152 unique sources with 209 citations, every one
resolving and every one carrying its reading depth in `SOURCES.md`; 3 sources marked unverified there
and none of them used. 172 verified examples and datasets, all constructed ones labelled as constructed
and all real ones cited. 26 quizzes, 218 questions, all grading correctly. 9 calculators, each tested
against `scipy` and against every dataset in the course. `verify_all.sh`: 4,829 quantities agreeing
between the two independent Python routes, 9,655 between Python and JavaScript, 1,573 page checks, all
passing.

**Claims removed or relabelled because they could not be verified:** none in this pass. That work was
done as the modules were built and is recorded in `SOURCES.md` (the Motorola 1988 annual report, too
large to fetch, is marked unverified and unused; commercial training sites are excluded outright; the
red bead experiment's box and paddle numbers are presented as the course's own constructed parameters
because no credible source states them; the Sony television story is told as reported by Taguchi and
Clausing and by Phadke and labelled not independently verified).

---

## Binding decisions (2026-09-09, unchanged)

These are the course's conventions. Changing one means changing it everywhere, so re-read this list
before altering anything that touches capability naming, sourcing standards, or the licence.

1. Module outlines and example plans in `SOURCES.md` Part 2: approved by the author.
2. Capstone: a brazed aluminium heat-exchanger line, leak-test reject rate driven by braze-joint gap.
   The bore Ø12.000 ± 0.025 mm is the running example for Modules 7, 8 and 16.
3. AIAG MSA-4 and PPAP-4 thresholds are cited as guidelines, marked "confirmed via secondary
   sources". The AIAG & VDA SPC Manual's own target tables (S-A2, Tables 8-1 and 9-3) are cited
   directly with page numbers.
4. The Sony television story is told "as reported by Taguchi and Clausing and by Phadke", labelled
   not independently verified.
5. Licence: CC BY-NC-SA 4.0 for content, MIT for code.
6. Deployed as a project site on the author's portfolio domain, alongside the DFx course at
   `https://erdemyilmaz.me/dfx/`. Every link in the course is relative, so the slug and depth can
   change freely.
7. **Cpk convention.** The 2026 AIAG & VDA / ISO 22514 convention is taught as current: Cp/Cpk and
   Pp/Ppk share the overall-sigma formula and the letter records whether stability was proven; the
   within-sigma index is Cw/Cwk. The legacy 2005 AIAG convention (Cpk from R̄/d₂, Ppk from overall s)
   is taught explicitly as what supplier reports and Minitab-style software still print. Every page
   and calculator prints the sigma estimate beside every index; the capability calculator has a
   convention toggle. CLAUDE.md rule 3 is read in this light.
8. **Red bead experiment numbers (Module 2).** deming.org (S-E4) confirms the exercise, its creation
   by Bill Boller of Hewlett-Packard as a 1982 gift to Deming, and its use on day one of Deming's
   four-day seminars, but states no box size, colour split, paddle-hole count or headcount. Sources
   that do quote such numbers are commercial training sites, which are on the S-E29 exclusion list.
   Module 2 therefore presents a 50-hole paddle and a 20 % red mix as the course's own constructed
   parameters, labelled as such. Apply the same standard anywhere this experiment comes up again.

## Still open, for the author only

Nothing blocks anything. Two standing invitations:

1. **A read-through in a browser.** No module has been reviewed by the author. The places most worth
   a second opinion: Module 0 section 6 (the critiques), Module 2's red-bead and funnel numbers
   (decision 8 above), Module 7's two-convention capability table and the calculator's convention
   toggle, and whether Modules 0, 1 and 11 are too long (see the deviations recorded under Phase E).
2. **The `<!-- AUTHOR: -->` hooks.** Twelve of them, spread across the modules, mark spots where a
   personal anecdote would fit (each names the kind of story that would land there, and each says
   "without employer detail"). Separately, all 27 pages carry a footer hook asking you to confirm the
   copyright line, and `about.html` has two more, for a personal paragraph and a contact address.
   All are optional.

## Environment

- Python 3.11.9 (Windows Store build) with numpy 2.4.6, scipy 1.17.1, pandas 3.0.5, statsmodels
  0.15.0, and pypdf. Node v24.19.0 and npm 11.17.0 (winget, OpenJS.NodeJS.LTS); Node is not on the
  Git Bash PATH, so `verify_all.sh` finds `/c/Program Files/nodejs/node.exe` itself.
- `.claude/launch.json` (gitignored) defines local static servers on ports 8781, 8791 and 8797. Other
  sessions may hold the first ones; add a config rather than fighting for a port.
- `reference/` holds the author's licensed PDFs of the AIAG & VDA SPC Manual and the AIAG-VDA FMEA
  Handbook (gitignored; the SPC manual was read for S-A2, the FMEA one was not used as a source), and
  `course.css` / `course.js` copied from the live DFx course, which Phase C started from.
- Long heredocs fail in the Bash tool; write scripts to files instead. Never `cat` a dataset or a
  results JSON into the context; run the scripts and read their summary output.

## Build history

The full session-by-session build log for Phases A to D — every module, the harness kind added for
each, the parallel-session file-splitting discipline, and the plan for which analysis kinds each
module needed — was removed from this file on 2026-09-10, once the course was finished, because it
described how the work was done rather than anything a future session must act on. It is preserved in
full in git:

```bash
git show 259e8dc:PROGRESS.md      # the last version carrying the complete log
git log --follow -p PROGRESS.md   # or the whole evolution
```

If a module is ever added or the curriculum changes, the method that built the existing twenty is:
read the module's `### Module N` section in `SOURCES.md` (grep for it, do not read the whole file);
register datasets in `verification/generate.py` with an `mNN-` prefix, checking the page slug against
`course.js`'s `MODULES` array first; add any new analysis kind to `compute.py`, `recompute.py` and
`sanity.py` together; write the page following `modules/07-capability-1.html`, with every number
quoted through a `data-ex`/`data-key`/`data-dp` span and every hand intermediate computed by script
before it goes in `allowed-numbers`; read table values from the generated CSV, never from memory of a
script's printed summary; set `built: true` in `course.js`; run `bash verification/verify_all.sh` in
the background and do other work while it runs; check the page in a browser; update `EXAMPLES.md` and
this file; commit.
