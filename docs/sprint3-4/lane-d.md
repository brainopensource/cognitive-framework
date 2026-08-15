# Lane D — Developer — harness manifest and Git environment

You own the coding environment adapter and the beta harness as **data**. You do not own the episode loop, OpenRouter, or governance.

Tickets: `S3-DD-001`, `S3-DD-002`, `S4-DD-001`  
Contract: `REQ-PORT-003`, `REQ-HARN-001`  
Packages: environment fake then real under `vanguard/packages/adapters/`; manifests under `vanguard/packages/agency/manifests/`.

## Read (in order), then implement from the tree

1. This file and `docs/sprint3-4/README.md`
2. `docs/sprint3/backlog.md`, `docs/sprint3/dd-packet.md`
3. `docs/sprint4/backlog.md`, `docs/sprint4/dd-packet.md`
4. ICD `EnvironmentAdapter`; Decision Record `ADR-0049`
5. `docs/sprint2/slice-findings.md` — absorb the rules; **do not copy deleted `slice/` source**
6. Existing `vg-shell-only` under `vanguard/packages/agency/manifests/`
7. Your contract rows in `docs/sprint0/active-mvp-contract.json`
8. `.github/pull_request_template.md`

## S3

- `EnvironmentAdapter` fake: snapshot, observe, preview **including new files**, apply, reconcile, dispose.
- Tests are argv arrays, never a shell string.
- Register `vg-code-default` (typed `read` / `search` / `patch` / `test`). `vg-shell-only` stays undeletable.
- Leave the CLI on `MockRuntime`.

## S4

- Permanent Git adapter (worktree, preview, apply). Shell is a selector-scoped privileged fallback, not the default.
- The S4 trust-spine command uses the **fake**, not this adapter. Live `vg run` wiring is Sprint 6.

## Out

ModelPort, OpenRouter, episode engine, process engine, deleting `spike/`/`slice/`.

## Git

Branch `sprints3-4/integration` only. After each ticket: `git status`, `git diff`, commit with ticket + `req_id` + done-state, then `git push -u origin HEAD`. Example:

```
S3-DD-002: vg-code-default registered; vg-shell-only remains undeletable (REQ-HARN-001).
```
