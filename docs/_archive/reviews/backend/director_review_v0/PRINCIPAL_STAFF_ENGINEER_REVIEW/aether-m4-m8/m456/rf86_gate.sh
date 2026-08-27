#!/usr/bin/env bash
# RF-86 — the M-5 generality gate. Run in CI on every commit.
# Fails if Pack #2 work mutated the frozen substrate.
set -uo pipefail
BASE="${1:-M-5-BASE}"
FROZEN=(domain kernel ports runtime agency/episode)
rc=0
for p in "${FROZEN[@]}"; do
  d=$(git diff --stat "$BASE" -- "vanguard/packages/$p" 2>/dev/null)
  if [[ -n "$d" ]]; then
    echo "RF-86 FAIL: M-5 mutated frozen substrate vanguard/packages/$p"
    echo "$d"; rc=1
  else
    echo "RF-86 ok: vanguard/packages/$p clean"
  fi
done
tcb=$(find vanguard/packages/kernel -name '*.py' -print0 | xargs -0 cat | wc -l)
echo "kernel TCB: $tcb (ceiling 1438 logical)"
exit $rc
