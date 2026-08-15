# Lane C — Developer — ports and OpenRouter

You own port activation bundles, then the real model adapter. You do not own the episode loop, Git, or governance.

Tickets: `S3-DC-001`, `S3-DC-002`, `S3-DC-003`, `S4-DC-001`  
Contract: `REQ-PORT-002`, `REQ-PORT-004`, `REQ-PORT-005`, then `REQ-PORT-006`  
Packages: `vanguard/packages/ports/`, fakes under `vanguard/packages/adapters/`, suites under `test/contracts/`.

## Read (in order), then implement from the tree

1. This file and `docs/sprint3-4/README.md`
2. `docs/sprint3/backlog.md`, `docs/sprint3/dc-packet.md`
3. `docs/sprint4/backlog.md`, `docs/sprint4/dc-packet.md`
4. ICD §4 port table; `vanguard/packages/ports/README.md` (activation bundle rule)
5. `schemas/v4/port-interfaces.md`
6. `spike/provider_notes.md` and `slice/slice-findings.md` — notes only; **do not import those trees**
7. Your contract rows in `docs/sprint0/active-mvp-contract.json`
8. Existing `EventStorePort` fake+real as the pattern to copy
9. `.github/pull_request_template.md`

A port with no fake and no shared suite must not land.

## S3 (no network)

- `ModelPort`: interface + cassette/fake + suite. Provider failures are instrument errors, not task failures.
- `EvaluatorPort`: interface + fake. `agency` must not import it.
- `SandboxRunner`: interface + visibly non-contained fake; unverified containment blocks publication.

## S4

- OpenRouter (OpenAI-compatible) adapter behind `ModelPort`. Secret references only.
- Cassette record/replay for CI. Skip live calls when the key is unset.
- Trust-spine tests (`TEST-TRUST-001`) must not instantiate this adapter.

## Out

Episode engine, process engine, Git worktree adapter, deleting disposables, CLI dogfood.

## Git

Branch `sprints3-4/integration` only. After each ticket: `git status`, `git diff`, commit with ticket + `req_id` + done-state, then `git push -u origin HEAD`. Example:

```
S3-DC-001: ModelPort fake and cassette suite with typed instrument errors (REQ-PORT-002).
```
