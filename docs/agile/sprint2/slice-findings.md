# T0b disposable-slice findings

Moved here from `slice/slice-findings.md` ahead of the `S4-GATE-001` deletion
of `spike/` and `slice/`. The findings are the part of a disposable worth
keeping: the directory is deleted, what it taught is not (`REQ-SLICE-001`).

Status: deterministic path proven (5/5 workspace tests, 2026-08-15). Live-provider run **blocked**: no `VG_SLICE_*` / `OPENROUTER_*` / `OPENAI_*` credential in the environment. `REQ-SLICE-001` stays `open`. Do not invent latency numbers.

## Proven without a live model

- Provider text cannot be treated as a patch: extraction, repository containment, and `git apply --check` are distinct failure stages.
- Human approval must see the exact patch and file stat after validation, not only the model's explanation. Runner requires typing `approve`.
- A test command must cross the boundary as argv. Accepting a shell string would add quoting ambiguity and injection.
- Repository root and working directory are operational contract fields.
- Provider failure, invalid patch, human rejection, apply failure, and test failure are different outcomes.
- HTTP provider failure is an instrument error, not a task failure (`provider.test.ts`).
- Parent-traversal paths in a purported patch are rejected.

## Still required for `REQ-SLICE-001`

One live OpenAI-compatible call against an expendable repository, with a disposable key, recording provider shape and patch latency here. Until that receipt exists, Sprint 3 may proceed locally (`DECISION-0003`) but must not treat slice code as a production adapter.

Nothing in this directory is suitable for promotion. T6.1 rebuilds provider and Git adapters behind activated ports; S4 deletes this directory.
