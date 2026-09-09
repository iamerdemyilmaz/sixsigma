/* Design for Manufacturing and Assembly: From Prototype to Production
   Shared script: navigation, quiz engine, progress tracking.
   Vanilla JS, no dependencies. Works from file:// and any static host. */

(function () {
  "use strict";

  /* ---------- Curriculum ----------
     `built` controls whether the module is linked in navigation.
     Only finished modules are linked (no placeholder pages). */
  var MODULES = [
    { num: "00", slug: "00-introduction", title: "Introduction: Why DFx", built: true },
    { num: "01", slug: "01-npi-process", title: "The product development and NPI process", built: true },
    { num: "02", slug: "02-process-selection", title: "Process selection and cost drivers", built: true },
    { num: "03", slug: "03-tolerancing", title: "Tolerancing for manufacturability", built: true },
    { num: "04", slug: "04-cnc-machining", title: "DFM for CNC machining", built: true },
    { num: "05", slug: "05-sheet-metal", title: "DFM for sheet metal", built: true },
    { num: "06", slug: "06-injection-molding", title: "DFM for injection molding", built: true },
    { num: "07", slug: "07-casting-forging", title: "DFM for casting and forging", built: true },
    { num: "08", slug: "08-additive", title: "DFM for additive manufacturing", built: true },
    { num: "09", slug: "09-pcb-pcba", title: "DFM for PCB and PCBA", built: true },
    { num: "10", slug: "10-design-for-assembly", title: "Design for assembly", built: true },
    { num: "11", slug: "11-design-for-test", title: "Design for test", built: true },
    { num: "12", slug: "12-service-reliability-compliance", title: "Design for service, reliability, and compliance", built: true },
    { num: "13", slug: "13-materials-finishes-joining", title: "Materials, finishes, and joining", built: true },
    { num: "14", slug: "14-suppliers", title: "Working with suppliers and contract manufacturers", built: true },
    { num: "15", slug: "15-cost-modeling", title: "Cost modeling and should-cost", built: true },
    { num: "16", slug: "16-capstone", title: "Capstone: a full DFx review", built: true }
  ];

  var PASS_MARK = 0.7; /* fraction of quiz questions needed to mark a module complete */
  var STORE_KEY = "dfx-course-progress";

  /* ---------- Storage (always wrapped; page works without it) ---------- */
  function loadProgress() {
    try {
      var raw = window.localStorage.getItem(STORE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }
  function saveProgress(p) {
    try {
      window.localStorage.setItem(STORE_KEY, JSON.stringify(p));
      return true;
    } catch (e) {
      return false;
    }
  }

  /* ---------- Helpers ---------- */
  function root() {
    /* Pages set data-root on <body>: "" for top level, "../" for modules/ */
    return document.body.getAttribute("data-root") || "";
  }
  function currentModule() {
    return document.body.getAttribute("data-module") || null;
  }
  function el(tag, attrs, text) {
    var e = document.createElement(tag);
    if (attrs) { Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); }); }
    if (text !== undefined) { e.textContent = text; }
    return e;
  }
  function moduleHref(m) {
    return root() + "modules/" + m.slug + ".html";
  }

  /* ---------- Navigation ---------- */
  function buildSidebar() {
    var nav = document.querySelector("[data-nav]");
    if (!nav) { return; }
    var progress = loadProgress();
    var cur = currentModule();

    var h = el("h2", null, "Modules");
    nav.appendChild(h);
    var ol = el("ol");
    MODULES.forEach(function (m) {
      var li = el("li");
      if (m.num === cur) { li.className += " current"; }
      if (progress[m.num]) { li.className += " done"; }
      var num = el("span", { "class": "num" }, m.num);
      if (m.built) {
        var a = el("a", { href: moduleHref(m) });
        if (m.num === cur) { a.setAttribute("aria-current", "page"); }
        a.appendChild(num);
        a.appendChild(document.createTextNode(" " + m.title));
        li.appendChild(a);
      } else {
        var s = el("span", { "class": "planned", title: "Not yet published" });
        s.appendChild(num);
        s.appendChild(document.createTextNode(" " + m.title));
        li.appendChild(s);
      }
      ol.appendChild(li);
    });
    nav.appendChild(ol);

    var h2 = el("h2", null, "Course");
    nav.appendChild(h2);
    var ol2 = el("ol");
    var pages = [
      { href: root() + "index.html", title: "Course home", key: "index" },
      { href: root() + "glossary.html", title: "Glossary", key: "glossary", built: true },
      { href: root() + "references.html", title: "All references", key: "references", built: true },
      { href: root() + "about.html", title: "About and licence", key: "about", built: true },
      { href: "https://erdemyilmaz.me/", title: "Back to erdemyilmaz.me", key: "home", built: true }
    ];
    var page = document.body.getAttribute("data-page");
    pages.forEach(function (p) {
      var li = el("li");
      if (p.key === page) { li.className = "current"; }
      if (p.built === false) {
        li.appendChild(el("span", { "class": "planned", title: "Not yet published" }, p.title));
      } else {
        var a = el("a", { href: p.href }, p.title);
        li.appendChild(a);
      }
      ol2.appendChild(li);
    });
    nav.appendChild(ol2);
  }

  function setupNavToggle() {
    var btn = document.querySelector(".nav-toggle");
    var side = document.querySelector(".sidebar");
    if (!btn || !side) { return; }
    btn.addEventListener("click", function () {
      var open = side.classList.toggle("open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  function buildPager() {
    var pager = document.querySelector("[data-pager]");
    var cur = currentModule();
    if (!pager || !cur) { return; }
    var idx = -1;
    MODULES.forEach(function (m, i) { if (m.num === cur) { idx = i; } });
    if (idx < 0) { return; }
    var prev = idx > 0 ? MODULES[idx - 1] : null;
    var next = idx < MODULES.length - 1 ? MODULES[idx + 1] : null;

    function item(m, label) {
      if (!m) { return el("span", null, ""); }
      var wrap;
      if (m.built) {
        wrap = el("a", { href: moduleHref(m) });
      } else {
        wrap = el("span", { title: "Not yet published" });
      }
      var lab = el("span", { "class": "label" }, label);
      wrap.appendChild(lab);
      wrap.appendChild(document.createTextNode(m.num + " " + m.title));
      return wrap;
    }
    pager.appendChild(item(prev, "Previous"));
    pager.appendChild(item(next, "Next"));
  }

  /* ---------- Progress bar (index) ---------- */
  function buildProgressBar() {
    var box = document.querySelector("[data-progress]");
    if (!box) { return; }
    var progress = loadProgress();
    var built = MODULES.filter(function (m) { return m.built; });
    var done = built.filter(function (m) { return progress[m.num]; }).length;
    var pct = built.length ? Math.round(100 * done / built.length) : 0;

    var bar = el("div", { "class": "progress-bar", role: "progressbar", "aria-valuemin": "0", "aria-valuemax": "100", "aria-valuenow": String(pct), "aria-label": "Course progress" });
    var fill = el("div");
    fill.style.width = pct + "%";
    bar.appendChild(fill);
    box.appendChild(bar);
    var p = el("p", null, done + " of " + built.length + " published module" + (built.length === 1 ? "" : "s") + " completed (" + pct + "%). A module is marked complete when you score at least " + Math.round(PASS_MARK * 100) + "% on its quiz.");
    box.appendChild(p);

    if (done > 0) {
      var reset = el("button", { "class": "secondary", type: "button" }, "Reset progress");
      reset.className = "secondary";
      reset.style.cssText = "font:inherit;margin-top:0.6rem;padding:0.3rem 0.7rem;border:1px solid var(--line);background:transparent;color:var(--fg);border-radius:4px;cursor:pointer;";
      reset.addEventListener("click", function () {
        if (window.confirm("Clear your saved quiz progress on this device?")) {
          saveProgress({});
          window.location.reload();
        }
      });
      box.appendChild(reset);
    }
  }

  function buildModuleList() {
    var list = document.querySelector("[data-module-list]");
    if (!list) { return; }
    var progress = loadProgress();
    MODULES.forEach(function (m) {
      var li = el("li");
      li.appendChild(el("span", { "class": "num" }, m.num));
      var body = el("div");
      if (m.built) {
        body.appendChild(el("a", { href: moduleHref(m) }, m.title));
      } else {
        body.appendChild(el("span", null, m.title));
      }
      var descNode = document.querySelector('[data-module-desc="' + m.num + '"]');
      if (descNode) {
        var d = el("span", { "class": "desc" }, descNode.textContent.trim());
        body.appendChild(d);
      }
      li.appendChild(body);
      var status;
      if (!m.built) {
        status = el("span", { "class": "status" }, "In preparation");
      } else if (progress[m.num]) {
        status = el("span", { "class": "status done" }, "Completed");
      } else {
        status = el("span", { "class": "status" }, "Published");
      }
      li.appendChild(status);
      list.appendChild(li);
    });
  }

  /* ---------- Quiz engine ----------
     Markup contract:
     <form class="quiz" data-module="06">           (add data-pre for a "before you start" check: graded, never saved)
       <fieldset class="q" data-answer="b">          multiple choice: radio inputs, value = letter
         <legend>1. Question text</legend>
         <label><input type="radio" name="q1" value="a"> ...</label>
         <p class="explain" hidden>Explanation shown after checking.</p>
       </fieldset>
       <fieldset class="q" data-type="numeric" data-answer="2.5" data-tolerance="0.1">
         <legend>2. Question</legend>
         <input type="number" name="q2" step="any">
         <p class="explain" hidden>...</p>
       </fieldset>
       <button type="submit">Check answers</button>
       <output class="quiz-score" aria-live="polite"></output>
     </form>
  */
  function setupQuizzes() {
    var forms = document.querySelectorAll("form.quiz");
    Array.prototype.forEach.call(forms, function (form) {
      form.setAttribute("novalidate", "novalidate");
      form.addEventListener("submit", function (ev) {
        ev.preventDefault();
        gradeQuiz(form);
      });
      var reset = form.querySelector("button[type=reset]");
      if (reset) {
        reset.addEventListener("click", function () {
          window.setTimeout(function () { clearQuiz(form); }, 0);
        });
      }
    });
  }

  function clearQuiz(form) {
    Array.prototype.forEach.call(form.querySelectorAll("fieldset.q"), function (fs) {
      fs.classList.remove("correct", "incorrect");
      var v = fs.querySelector(".verdict");
      if (v) { v.remove(); }
      var ex = fs.querySelector(".explain");
      if (ex) { ex.hidden = true; }
    });
    var out = form.querySelector(".quiz-score");
    if (out) { out.textContent = ""; out.className = "quiz-score"; }
  }

  function gradeQuiz(form) {
    var qs = form.querySelectorAll("fieldset.q");
    var total = qs.length;
    var score = 0;
    var unanswered = 0;

    Array.prototype.forEach.call(qs, function (fs) {
      var type = fs.getAttribute("data-type") || "choice";
      var answer = fs.getAttribute("data-answer");
      var ok = false;
      var answered = true;

      if (type === "numeric") {
        var inp = fs.querySelector("input[type=number], input[type=text]");
        var raw = inp ? String(inp.value).trim().replace(",", ".") : "";
        if (raw === "") { answered = false; }
        var val = parseFloat(raw);
        var target = parseFloat(answer);
        var tol = parseFloat(fs.getAttribute("data-tolerance") || "0");
        ok = answered && !isNaN(val) && Math.abs(val - target) <= tol + 1e-9;
      } else {
        var checked = fs.querySelector("input[type=radio]:checked");
        if (!checked) { answered = false; }
        ok = answered && checked.value === answer;
      }

      if (!answered) { unanswered += 1; }
      if (ok) { score += 1; }

      fs.classList.remove("correct", "incorrect");
      fs.classList.add(ok ? "correct" : "incorrect");
      var legend = fs.querySelector("legend");
      var old = fs.querySelector(".verdict");
      if (old) { old.remove(); }
      if (legend) {
        var v = el("span", { "class": "verdict" }, ok ? "Correct" : (answered ? "Incorrect" : "Not answered"));
        legend.appendChild(v);
      }
      var ex = fs.querySelector(".explain");
      if (ex) { ex.hidden = false; }
    });

    var out = form.querySelector(".quiz-score");
    var pct = total ? score / total : 0;
    if (form.hasAttribute("data-pre")) {
      /* Pre-module check: show the result and explanations, never record progress. */
      var pre = "You got " + score + " of " + total + ". ";
      if (unanswered) { pre += unanswered + " left blank. "; }
      pre += (score === total) ? "You know this ground; the module adds the numbers and the reasons." : "The explanations point to the sections that cover each answer.";
      if (out) { out.textContent = pre; out.className = "quiz-score"; }
      return;
    }
    var passed = pct >= PASS_MARK;
    var msg = "Score: " + score + " of " + total + " (" + Math.round(pct * 100) + "%). ";
    msg += passed ? "Pass. " : "Below the " + Math.round(PASS_MARK * 100) + "% pass mark. Review the explanations and try again. ";
    if (unanswered) { msg += unanswered + " question" + (unanswered === 1 ? "" : "s") + " left blank. "; }

    var modNum = form.getAttribute("data-module") || currentModule();
    if (passed && modNum) {
      var progress = loadProgress();
      progress[modNum] = { passed: true, score: score, total: total, date: new Date().toISOString().slice(0, 10) };
      if (saveProgress(progress)) {
        msg += "This module is now marked complete on this device.";
        var li = document.querySelector(".sidebar li.current");
        if (li) { li.classList.add("done"); }
      } else {
        msg += "Progress could not be saved in this browser (storage unavailable), but your score is shown above.";
      }
    }
    if (out) {
      out.textContent = msg;
      out.className = "quiz-score " + (passed ? "pass" : "fail");
    }
  }

  /* ---------- Footer date ---------- */
  function fillDates() {
    var nodes = document.querySelectorAll("[data-year]");
    Array.prototype.forEach.call(nodes, function (n) { n.textContent = String(new Date().getFullYear()); });
  }

  /* ---------- Init ---------- */
  document.addEventListener("DOMContentLoaded", function () {
    buildSidebar();
    setupNavToggle();
    buildPager();
    buildProgressBar();
    buildModuleList();
    setupQuizzes();
    fillDates();
  });

  /* Expose for tests */
  window.DFX = { MODULES: MODULES, PASS_MARK: PASS_MARK, loadProgress: loadProgress, gradeQuiz: gradeQuiz };
})();
