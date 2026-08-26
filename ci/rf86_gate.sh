#!/usr/bin/env bash
# RF-86 — the M-5 generality gate. Run in CI on every commit.
# Fails if Pack #2 work mutated the frozen substrate.
#
# Source: docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/aether-m4-m8/m456/rf86_gate.sh
# Deltas from the bundle copy (both strengthen the gate; neither weakens an assertion):
#   1. fail-closed on a missing baseline ref. The bundle version sent `git diff`
#      stderr to /dev/null, so an absent M-5A-BASE-v2 tag left `$d` empty and every
#      frozen path reported "ok" -- the gate passed precisely when it could not run.
#   2. the TCB line is labelled `raw`, and the authoritative logical-LOC linter is
#      invoked. Printing a raw count against the *logical* 1438 ceiling reads as a
#      breach (1737 vs 1438) when the ceiling is not in fact exceeded.
set -uo pipefail
BASE="${1:-M-5A-BASE-v2}"
FROZEN=(domain kernel ports runtime agency/episode)

if ! git rev-parse --verify --quiet "${BASE}^{commit}" >/dev/null; then
  echo "RF-86 FAIL: baseline ref '${BASE}' does not resolve; the gate cannot run."
  echo "RF-86 fails closed rather than reporting paths clean it never compared."
  echo "Fetch tags (actions/checkout needs fetch-depth: 0) or push the tag."
  exit 2
fi

rc=0
for p in "${FROZEN[@]}"; do
  d=$(git diff --stat "$BASE" -- "vanguard/packages/$p")
  if [[ -n "$d" ]]; then
    echo "RF-86 FAIL: M-5 mutated frozen substrate vanguard/packages/$p"
    echo "$d"; rc=1
  else
    echo "RF-86 ok: vanguard/packages/$p clean"
  fi
done

tcb=$(find vanguard/packages/kernel -name '*.py' -print0 | xargs -0 cat | wc -l)
echo "kernel TCB: ${tcb} raw lines (informational; the 1438 ceiling is LOGICAL lines)"
python3 tools/linters/check_tcb_budget.py || rc=1
exit $rc
