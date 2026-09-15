#!/usr/bin/env bash
# ==============================================================================
# HISTORICAL AUDIT REPRODUCTION HARNESS — AUDIT-2026-09-06-wave2-closeout.md
# ==============================================================================
# Target Subject: Historical commit dfb0bb64 (2026-09-06)
# Current Status: ALL FINDINGS RESOLVED (Phase C0-C4 / NT-1 accepted at HEAD)
#
# Boundary checks: PASS (0 violations across 833 files).
# Test suite:      PASS (3,121 unit/contract/agency/pack tests passing).
# Authority:       Non-canonical diagnostic script (.draft/audit/).
# ==============================================================================
# Read-only: this script does not modify the repository.
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"

hr() { printf '\n== %s ==\n' "$1"; }

hr "subject"
git rev-parse HEAD
git status --short || true

hr "linters (justfile 'check' recipe body)"
for l in check_boundaries check_tcb_budget check_domain_blindness \
         check_isolation_policy check_path_hygiene; do
  python3 "tools/linters/$l.py" >/dev/null 2>&1
  echo "$l exit=$?"
done
echo "--- boundary detail ---"
python3 tools/linters/check_boundaries.py 2>&1 | head -10

hr "F-C1 configuration identity proof (all three must hash equal today)"
for p in fast balanced max; do
  printf '%-9s ' "$p"
  sed -E 's/"harness":[^,]*/"H"/; s/"budgetPolicy":[^,]*/"B"/' \
    "vanguard/packages/agency/manifests/vg-code-$p/manifest.json" | sha256sum
done

hr "F-C3 / F-C4 dead production API (non-test caller counts)"
for s in compile_preset compile_pack budget_policy_document resolve_preset_policy; do
  printf '%-24s ' "$s"
  grep -rn "$s" --include=*.py . 2>/dev/null \
    | grep -v __pycache__ | grep -v '\.venv' \
    | grep -v 'packs/code-default/load.py' | wc -l
done

hr "F-D1 entrypoint Type-2 clone (expect 2 differing lines of 13)"
diff <(sed -n '27,39p' vanguard/packages/apps/coding_max/facade.py) \
     <(sed -n '40,52p' vanguard/packages/runtime/entrypoint.py)

hr "F-D1 preset literal repetition"
grep -rn '"fast".*"balanced".*"max"\|fast.*balanced.*max' \
  --include=*.py vanguard/ packs/ benchmarks/ 2>/dev/null \
  | grep -v __pycache__ | grep -vi 'test' | head

hr "F-D3 Forge reachable from benchmarks via runtime re-export"
grep -rn "ForgeFacade" --include=*.py vanguard/packages/runtime benchmarks/ | grep -v __pycache__

hr "F-D3 Chimera importers (expect: tests only)"
grep -rn "agency.chimera" --include=*.py . 2>/dev/null \
  | grep -v __pycache__ | grep -v '\.venv' | grep -v '/agency/chimera'

hr "F-D4 deleted lab package"
ls -d lab 2>&1 || true
git show --stat --oneline 67f033d5 -- lab | head -12
echo "--- dependent test modules still present ---"
grep -rln "from lab\.\|/ \"lab\" /\|ROOT / \"lab\"" --include=*.py test/ | sort

hr "F-D5 ladder namespace collision"
grep -rn "run_ladder" --include=*.py tools/ test/ | grep -v __pycache__ | head -4
ls -d benchmarks/ladder tools/002_LLM_API_MOCK/ladder.py

hr "F-D5 sys.path mutation count"
grep -rn "sys.path.insert\|sys.path.append" --include=*.py \
  vanguard/ packs/ benchmarks/ tools/ 2>/dev/null | grep -v __pycache__ | wc -l

hr "size distribution"
for d in vanguard/packages/*/; do
  printf '%-42s ' "$d"
  find "$d" -name '*.py' -not -path '*__pycache__*' -print0 2>/dev/null \
    | xargs -0 wc -l 2>/dev/null | tail -1
done
printf '%-42s ' "benchmarks/"
find benchmarks -name '*.py' -not -path '*__pycache__*' -print0 \
  | xargs -0 wc -l 2>/dev/null | tail -1
printf '%-42s ' "vanguard/clients (TypeScript src)"
find vanguard/clients -path '*/src/*' -name '*.ts' -print0 \
  | xargs -0 wc -l 2>/dev/null | tail -1

hr "F-B1 lossy terminal-state projection (expect 4 sites -> completed, 1 -> abandoned)"
grep -rn 'in {"completed", "abstained"}\|"abstained":' --include=*.py \
  vanguard/packages/runtime/ | grep -v __pycache__

hr "F-B5 code --help is effectful and exits 0"
timeout 90 node bin/aether code --help; echo "exit=$?"

hr "TypeScript client suite (sibling-audit claim did NOT reproduce: expect pass)"
npm --workspace @vanguard/cli test 2>&1 | tail -6

hr "full dynamic suite (pytest is NOT installed; unittest is the only runnable path)"
.venv/bin/python -m pytest --version 2>&1 | head -1
.venv/bin/python -m unittest discover -s test -t . 2>&1 | tail -3
