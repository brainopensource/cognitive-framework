# Senior A — first deterministic episode slice

Tickets: `S3-SA-001`, `S3-INT-001` · Contract: `REQ-EXEC-001`

Own `vanguard/packages/agency/` loop code only. Consume `Kernel.dispatch` and `EventStorePort` as they exist. Consume `ModelPort` fake from Dev C; until that merges, a local cassette double is allowed in tests but must not become a second port.

Loop: observe → propose → authorise → effect → receipt. Episode terminates; it does not call `EvaluatorPort`. Use VG-03 §6.2 run-termination names. Lint: no `plan`, `debug`, `reflect`, `architect` identifiers in `agency/`.

Depth-1 only. Recursion, structured concurrency polish, and the no-model trust-spine demo are Sprint 4a.

Must not touch: `runtime/governance/`, `adapters/` except test fakes, `slice/`, kernel algebra.
