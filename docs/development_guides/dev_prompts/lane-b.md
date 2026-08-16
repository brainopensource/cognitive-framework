# Lane B — Senior — process engine and perimeter

You own finite, model-free governance, then the worker perimeter. You do not own the episode loop or providers.

Tickets: `S3-SB-001`, `S4-SB-001`  
Contract: `REQ-EXEC-002`, then `REQ-SEC-001`  
Packages: `vanguard/packages/runtime/governance/`, then sandbox adapter.

## Read (in order), then implement from the tree

1. This file and `docs/sprint3-4/README.md`
2. `docs/sprint3/backlog.md`, `docs/sprint3/sb-packet.md`
3. `docs/sprint4/backlog.md`, `docs/sprint4/sb-packet.md`
4. Decision Record — `ADR-0050`, `ADR-0055`
5. ICD isolation topology and `SandboxRunner`
6. VG-05 perimeter / containment (as cited by the ICD)
7. Your contract rows in `docs/sprint0/active-mvp-contract.json`
8. Process wire types already in `schemas/v4/` and `vanguard/packages/domain/`
9. `.github/pull_request_template.md`

If two docs disagree, stop and ask the Tech Lead.

## S3

- Process engine: declared states, approvals, restart-resume from the ledger with **no** `ModelPort`.
- Readable without opening the implementation.
- Lane A will join your resume test in `S3-INT-001`. Keep the engine importable without `agency/`.

## S4

- Real (or probed) `SandboxRunner` using Lane C’s Sprint 3 port.
- Containment report from probes. Unverified report blocks publication.
- Scoped fixture: worker cannot read the evaluator bundle. Not a full-programme red team.

## Out

Episode loop, OpenRouter, Git adapter, deleting `spike/`/`slice/` (Lane A gate), S5 evaluator OS identity.

## Git

Branch `sprints3-4/integration` only. After each ticket: `git status`, `git diff`, commit with ticket + `req_id` + done-state, then `git push -u origin HEAD`. Example:

```
S3-SB-001: interrupted process resumes from the ledger without an episode (REQ-EXEC-002).
```
