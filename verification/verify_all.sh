#!/usr/bin/env bash
# verify_all.sh - runs the whole verification protocol and exits non-zero on
# any failure. Run before every commit.
#
#   tables.py            constants and tables from scipy, checked against
#                        published values; reference points for stats.js
#   generate.py          datasets and metadata from the seeded registry
#   compute.py           Check 1: library route, published known answers
#   recompute.py         Check 2: closed-form route, must agree with Check 1
#   sanity.py            Check 3: relationships, ranges, page cross-check
#   test_calculators.js  Check 4: stats.js vs scipy and vs results/
set -u
cd "$(dirname "$0")/.."
PY=${PYTHON:-python}
if command -v node >/dev/null 2>&1; then NODE=node
elif [ -x "/c/Program Files/nodejs/node.exe" ]; then NODE="/c/Program Files/nodejs/node.exe"
else NODE=${NODE:-node}; fi
status=0
step() {
  echo "== $1"
  shift
  if ! "$@"; then status=1; echo "   ^^^ FAILED"; fi
}
step "tables.py" "$PY" verification/tables.py
step "generate.py" "$PY" verification/generate.py
step "compute.py" "$PY" verification/compute.py
step "recompute.py" "$PY" verification/recompute.py
step "sanity.py" "$PY" verification/sanity.py
step "test_calculators.js" "$NODE" verification/test_calculators.js
if [ $status -eq 0 ]; then echo "verify_all.sh: ALL CHECKS PASSED"; else echo "verify_all.sh: FAILURES"; fi
exit $status
