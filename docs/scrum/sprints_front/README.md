# Frontend sprint kits

Status: `BINDING for FE lanes` under the two-lanes lock  
Numbering: **FE-A-n / FE-B-n** (not Sprint 1–4; ROADMAP §0.3)

| Kit | Contents |
|---|---|
| `lane_a_wave1.md` | FE-A1 … FE-A5 |
| `lane_a_wave2.md` | FE-A6 … FE-A10 |
| `lane_b_wave1.md` | FE-B1 … FE-B4 |
| `lane_b_wave2.md` | FE-B5 … FE-B8 |

Replaces any `sprints_front/sprint1.md` … `sprint4.md`.

## Lane rules

- FE-A writes only `vanguard/clients/cli/**` (plus FE docs if the task says so).
- FE-B writes only `vanguard-ide/**`.
- Shared contract is owned by FE-A; FE-B vendors copies.
- Backend trees stay frozen. Joint notes J1–J5 are requests, not FE PRs.
- Every task is a **delta** against files that exist (or a new `vanguard-ide/` tree for B1).

## Default DoD commands

```bash
cd vanguard/clients/cli && npm run typecheck && npm test
cd vanguard-ide && npm run typecheck && npm run build
```

Boundary:

```bash
# expect no hits in application/UI sources
grep -r "vanguard/packages" vanguard/clients/cli/src vanguard-ide/src || true
```
