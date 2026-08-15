# Sprint 3–4 wave — four developer lanes

Branch: `sprints3-4/integration`  
Status: **Sprints 0–2 engineering DONE.** This wave implements Sprints 3 and 4 only. Sprints 5–6 are the following wave.

| Lane | Prompt | S3 | S4 |
|---|---|---|---|
| **A** Senior | [`lane-a.md`](lane-a.md) | Episode loop | No-model trust spine + delete gate |
| **B** Senior | [`lane-b.md`](lane-b.md) | Process engine | Worker perimeter |
| **C** Mid | [`lane-c.md`](lane-c.md) | Port fakes (model/evaluator/sandbox) | OpenRouter adapter |
| **D** Mid | [`lane-d.md`](lane-d.md) | Env fake + `vg-code-default` | Permanent Git adapter |

All four start in parallel. Do not wait for another lane’s merge to write the first failing test. Integrate only at `S3-INT` (A) and `S4-GATE` (A+B).

## Sprint 0–2

| Status | Item |
|---|---|
| **DONE** | S0 governance, ICD, contract, CI boundaries, tag `v0.0.0-sprint0` |
| **DONE** | S1 T1 schemas (DRAFT, dual readers), T0a `spike/`, mock CLI |
| **DONE** | S2 kernel, ledger, T7 `vg-shell-only`, deterministic `slice/` |
| **TODO** | Live T0b (`REQ-SLICE-001`) — needs a disposable API key |
| **TODO** | Schema `LOCKED` — GAP-010..014 evidence bundle + human timing |
| **TODO** | GitHub branch protection on `main` |
| **TODO** | Issue-tracker import (B-07); margin reporting (B-06) |

Those TODOs do not block local S3 work. They are not S3 tickets.

## Git (every lane)

Work only on `sprints3-4/integration`. Do not commit to `main`. After each ticket:

```bash
git status
git diff
git log -5 --oneline
git add <paths you changed>
git commit -m "$(cat <<'EOF'
<ticket>: <why this change, naming the req_id and the observable done-state>

EOF
)"
git push -u origin HEAD
```

Cite `req_id` in the PR body. Do not import `spike/` or `slice/`. Do not copy disposable code into `adapters/`.
