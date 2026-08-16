# Developer D — environment fake and vg-code-default

Tickets: `S3-DD-001..002` · Contract: `REQ-PORT-003`, `REQ-HARN-001`

`EnvironmentAdapter` fake: snapshot, observe, preview (including **new files**), apply, reconcile, dispose. Tests are argv arrays, never a shell string. Absorb `slice/slice-findings.md`. Do not copy `slice/` sources.

Author `vg-code-default` as data (typed `read/search/patch/test`). `vg-shell-only` remains undeletable. CLI stays on `MockRuntime`.

Must not build the real Git worktree adapter (`S4-DD`) or OpenRouter.
