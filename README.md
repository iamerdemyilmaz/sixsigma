# Six Sigma for Engineers: Process Capability, SPC, and DMAIC in Practice

A complete, self-contained online course for junior and mid-level mechanical and manufacturing
engineers. Twenty modules plus seven supporting pages, nine interactive calculators, and a
verification suite that recomputes every number on every page by two independent routes before it is
allowed to appear.

Static HTML, CSS and vanilla JavaScript. No framework, no build step, no CDN, no cookies, no
third-party fonts. It works opened straight from the filesystem (`file://`) and from any static host.

**Live:** <https://erdemyilmaz.me/sixsigma/>

- Content licence: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
- Code licence (calculators, `stats.js`, verification scripts): MIT

---

## What is here

```
index.html                    landing page, outline, progress bar
modules/00-introduction.html  ... modules/19-capstone.html
calculators.html              all nine calculators on one page
tables.html                   Z, t, chi-square, F, control chart constants (generated)
formulas.html                 formula sheet
glossary.html                 glossary
references.html               consolidated references (generated from the modules)
about.html                    what the course is, how it is verified, licence

assets/css/course.css         the whole stylesheet, including the print stylesheet
assets/js/course.js           navigation, quiz engine, progress tracking
assets/js/stats.js            numerical functions and every calculator engine (UMD, testable in Node)
assets/js/calculators.js      calculator UI and the inline SVG charts

verification/generate.py      seeded dataset registry -> data/*.csv + metadata
verification/compute.py       Check 1: numpy / scipy / statsmodels -> results/*.json
verification/recompute.py     Check 2: independent closed-form route, must agree with Check 1
verification/sanity.py        Check 3: relationships, ranges, and a page-by-page number scan
verification/tables.py        control chart constants and statistical tables, checked against published ones
verification/test_calculators.js  Check 4: stats.js vs scipy and vs results/
verification/verify_all.sh    runs all of the above; non-zero exit on any failure

SOURCES.md                    every source, with reading depth and verification status
EXAMPLES.md                   every example: id, module, dataset, check status
PROGRESS.md                   build log, decisions, and the resume point for a new session
```

---

## Deploying

Everything is static. There is nothing to build and no server-side code.

### GitHub Pages

The course is already published this way.

1. Push the repository to GitHub.
2. **Settings → Pages → Build and deployment**: source **Deploy from a branch**, branch `main`,
   folder `/ (root)`. Save.
3. The site appears at `https://<user>.github.io/<repo>/` within a minute or two.
4. For a custom domain, add a `CNAME` file at the repository root containing the domain, and point a
   DNS `CNAME` record at `<user>.github.io`. A project site under an existing user-site domain (the
   arrangement used here, `erdemyilmaz.me/sixsigma/`) needs no `CNAME` file in this repository: the
   user site's domain covers it and the repository name becomes the path.

Every link in the course is relative, so the repository name, the path depth and the domain can all
change without editing a single page.

### Netlify

1. **Add new site → Import an existing project**, and pick the repository.
2. Build command: leave **empty**. Publish directory: `.` (the repository root).
3. Deploy. Drag-and-drop of the folder onto the Netlify dashboard works just as well for a one-off.

### Anything else

Copy the repository to any web root. Apache, nginx, S3, a USB stick. The only requirement is that
`assets/` keeps its position relative to the pages.

---

## Running the verification suite

Run this before every commit. It is the reason the numbers in the course can be trusted.

```bash
bash verification/verify_all.sh
```

Requirements: Python 3.11 or later with `numpy`, `scipy`, `pandas` and `statsmodels`, and Node 18 or
later for the JavaScript checks.

```bash
python -m pip install numpy scipy pandas statsmodels
```

The run takes a few minutes, most of it in `recompute.py` and the Monte Carlo examples. It prints one
line per stage and exits non-zero if any stage fails:

```
== tables.py            constants and tables computed, checked against published values
== generate.py          172 datasets written to verification/data
== compute.py           every example computed by the library route
== recompute.py         4,829 quantities compared with an independent closed-form route
== sanity.py            172 results files, 1,573 page checks
== test_calculators.js  stats.js vs scipy, and every calculator vs results/
verify_all.sh: ALL CHECKS PASSED
```

On Windows, run it from Git Bash. If Node is not on the Git Bash `PATH`, the script looks for
`/c/Program Files/nodejs/node.exe` on its own. `PYTHON=python3 bash verification/verify_all.sh`
overrides the interpreter.

### Previewing locally

```bash
python -m http.server 8781
```

Then open <http://localhost:8781/>. Opening `index.html` directly from the filesystem also works;
`localStorage` (used only for quiz progress) may be restricted under `file://` in some browsers, and
the pages handle that.

---

## Editing a module

Each module page is plain HTML with no templating. The header, sidebar, prev/next pager, quiz
grading and progress bar are all built at runtime by `assets/js/course.js` from the `MODULES` array
near the top of that file; a page only has to set `data-root` and `data-module` on `<body>`.

**Prose, headings and figures** can be edited directly. Figures are inline SVG with a `<title>` and a
`<desc>`; keep both, they are what a screen reader reads.

**Numbers may not be edited directly.** Every statistic on a page is quoted inside a span that names
where it came from:

```html
<span data-ex="m07-bore" data-key="overall.Ppk" data-dp="3">1.040</span>
```

`sanity.py` reads `verification/results/m07-bore.json`, resolves `overall.Ppk`, rounds it to
`data-dp` decimals, and fails the build if the text between the tags differs. It also scans the whole
page for any number with two or more decimals and fails if it cannot trace it to a results file, to a
declared dataset, or to the page's `<meta name="allowed-numbers">` list. To change a number, change
the data or the computation and re-run the suite.

### Adding a new example

1. Register the dataset in `verification/generate.py` with a seeded generator and an `id` prefixed by
   the module (`m09-...`). Use a realistic metric quantity and a resolution that matches a plausible
   gauge.
2. If it needs a new kind of analysis, add it to `compute.py` (library route), `recompute.py`
   (independent closed-form route) and `sanity.py` (relationship checks) together. Never add it to
   only one.
3. Add the id to the page's `<meta name="examples" content="...">`.
4. Print the data on the page, in a table or a `<script type="application/json">` block, so a reader
   can reproduce the result in a spreadsheet.
5. Quote every number with a `data-ex` / `data-key` / `data-dp` span, and label the example as
   constructed.
6. Run `bash verification/verify_all.sh`, then add a row to `EXAMPLES.md`.

### Adding a quiz question

The markup contract is documented in `assets/js/course.js` above `setupQuizzes()`. In short: a
`<fieldset class="q" data-answer="b">` with radio inputs sharing one `name`, or
`data-type="numeric"` with `data-answer` and a `data-tolerance`, plus a `<p class="explain" hidden>`
that is revealed on grading. Eight to twelve questions per module; a score of 70 % marks the module
complete in that browser.

### Adding a page

Copy the shell from any supporting page, set `data-page`, and add an entry to the `PAGES` array in
`assets/js/course.js` so it appears in the sidebar.

---

## Conventions this course follows

These are decisions, not accidents, and changing one means changing it everywhere:

- **Capability letters.** The current AIAG & VDA and ISO 22514 convention is taught as current: Cp/Cpk
  and Pp/Ppk share the overall-sigma formula, and the letter records whether stability was
  demonstrated; the within-sigma index is Cw/Cwk. The legacy 2005 convention (Cpk from R̄/d₂, Ppk from
  the overall s), which most supplier reports and software still print, is taught explicitly as what
  you will actually receive. Every index on every page and in every calculator prints its sigma
  estimate beside it.
- **Stability before capability.** No capability index appears without a control chart of the same
  data and a statement of what it showed.
- **Specification limits never appear on a control chart.** The distinction is made in Modules 7, 16
  and 18.
- **Metric units only.**
- **Real versus constructed.** Historical claims, published cases and standards are cited with their
  reading depth. Everything else is a constructed example, generated by script and labelled as
  constructed on the page. No constructed example names a real company, and nothing in the course
  comes from the author's employers.
- **Contested claims stay contested.** The 1.5 sigma shift, the 3.4 DPMO figure, capability on
  non-normal data and the published critiques of Six Sigma programmes are all presented with sources
  on both sides.

---

## Accessibility and printing

Semantic HTML, keyboard-operable quizzes and calculators, `<title>` and `<desc>` on every SVG, light
and dark themes from `prefers-color-scheme`, and no horizontal page scrolling at any width (wide
tables and charts scroll inside their own containers). Every module prints as a clean handout: the
print stylesheet drops the navigation and expands every collapsed `<details>` block, so the exercise
solutions and the data tables are all on the page.

---

## Contributing a correction

A wrong number is a bug. The verification suite makes silent arithmetic errors unlikely, but it
cannot catch a badly chosen example, a source that does not quite say what the course says it does,
or an explanation that misleads while being technically true. Those are the corrections most worth
having. Open an issue, or a pull request with `verify_all.sh` passing.
