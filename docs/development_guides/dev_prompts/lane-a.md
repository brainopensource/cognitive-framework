# Lane A — Senior — episode engine and trust spine

You own open-ended coordination. You do not own ports, Git, OpenRouter, or the process engine.

Tickets: `S3-SA-001`, `S3-INT-001`, `S4-SA-001`, `S4-GATE-001`  
Contract: `REQ-EXEC-001`, then `REQ-TRUST-001`  
Package: `vanguard/packages/agency/` plus the S4 composition-root test for the trust spine.

## Read (in order), then implement from the tree

1. This file and `docs/sprint3-4/README.md`
2. `docs/sprint3/backlog.md`, `docs/sprint3/sa-packet.md`
3. `docs/sprint4/backlog.md`, `docs/sprint4/sa-packet.md`
4. Decision Record §10 — `ADR-0055`, `ADR-0056`, `ADR-0048`
5. ICD call path — `docs/sprint0/system-architecture-icd.md`
6. VG-03 §6 (loop and run-termination names)
7. Contract rows you cite in `docs/sprint0/active-mvp-contract.json`
8. Existing kernel/ledger: `vanguard/packages/kernel/`, `vanguard/packages/runtime/ledger/`
9. `.github/pull_request_template.md`

If two docs disagree, stop and ask the Tech Lead. Do not invent a second dispatch path.

## S3

- Depth-1 episode: observe → propose → authorise → effect → receipt through **existing** `Kernel.dispatch`.
- Cassette or fake `ModelPort` (Lane C). Local test double until C merges; delete the double after.
- Episode terminates. It does not evaluate itself.
- No cognitive identifiers (`plan`, `debug`, `reflect`, `architect`) in `agency/`.
- `S3-INT-001`: one cassette episode turn and Lane B’s process resume share the ledger. Architecture tests still forbid `agency` → adapters and `governance` → model.

## S4

- Finish the loop far enough for a **scripted, no-model** trajectory (`TEST-TRUST-001`): denial, attenuation, budget exhaustion, atomicity, recovery, secret non-disclosure.
- Must pass with any provider key **unset**. Do not import Lane C’s OpenRouter adapter.
- `S4-GATE-001` after B’s perimeter is mergeable: delete `spike/` and `slice/`; keep findings as notes under `docs/` if they are not already there.

## Out

OpenRouter, Git adapter, process engine, OS evaluator isolation (S5), `vg run` live dogfood (S6).

## Git

Branch `sprints3-4/integration` only. After each ticket: `git status`, `git diff`, then commit with ticket + `req_id` + done-state, then `git push -u origin HEAD`. Example:

```
S3-SA-001: cassette episode turn goes through Kernel.dispatch (REQ-EXEC-001).
```
