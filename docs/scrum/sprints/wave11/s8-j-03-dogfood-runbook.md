# S8-J-03 — live dogfood runbook (prepared, not executed)

**Status:** protocol ready · **Q2 remains `[TODO]`**  
**Date:** 2026-08-17 · **Owner:** GAMMA  
**REQ:** REQ-TRUST-001

This is not Q2. MOCK evidence is not live interactive dogfood.

## Pre-registered tasks (S9-J-01)

See `docs/scrum/sprints/sprint09/evidence/s9-j-01-dogfood-protocol.md`.

BETA lands directories at `lab/tasks/DOGFOOD-01` … `DOGFOOD-03` plus `lab/tasks/GREENFIELD-API-HTML`. Until then the coding LAM reports `inconclusive:workspace_missing` **in the denominator**.

## Operator commands (no mid-run hand-patch)

```bash
# Measurement only — missing dirs stay in the denominator
python3 - <<'PY'
from pathlib import Path
from tools.telemetry.coding_lam import default_workspace_map, run_coding_lam
from tools.telemetry.coding_lar import hypotheses_from_sessions, write_review_artifact
root = Path('.')
report = run_coding_lam(default_workspace_map(root), arm='mock', model_port='mock')
assert report['passRateDenominator'] == 4
print(report['workspaceMissingCount'], 'missing of', report['denominator'])
write_review_artifact(hypotheses_from_sessions(report['tasks']),
                      Path('docs/scrum/sprints/wave11/evidence/lar_hypotheses.md'))
PY

python3 tools/export_coding_session.py --jsonl path/to/episode.jsonl   # when a ledger exists
```

Live Q2 (human): `interactive=True`, real bugs, **no** editor patches during the episode. Then archive the JSONL. Do not mark the board `[DONE]` from MOCK.

## Anti-cheat

Host test runner is not the episode oracle. `REFERENCE.md` / gold patches are not worker-visible. MOCK must not wear an Ollama/OpenRouter label. LAR writes review markdown only.
