---
adr: 0069
title: "Runtime convergence: Python-first; vanguard/packages/ is the production lattice; layer0/ is absorbed, not a destination rewrite; no third tree; no Rust rewrite"
status: accepted
source_section: "v0.6 Concept Lock"
---

# ADR-0069: Runtime convergence — Python-first, packages canonical, layer0 absorbed

**Context.** Forensic discovery (`docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/VANGUARD_V060_FORENSIC_DISCOVERY.md`) found two
Python runtimes claiming Layer-0 work. Living CI gates `test/layer0` (25 tests, OK) and does not
run `test/kernel` (95 tests, OK). Durable WAL ledger, exterior evaluator daemon, and rootless
sandbox live in `vanguard/packages/`. `layer0/` provides SPI contracts and JSON-RPC/UDS but uses
`MemoryLedger` and fabricates `VerdictRecorded {verdict: "pass"}`
(`layer0/scheduler/driver.py:138-139`). `docs/SPEC.md` v0.5.0 named `layer0/` as the M1 destination.
Supporting reviews disagree: Full Refactor v3.1 wants a Rust core; the execution plan treats
`layer0/` as the v0.6 production target; parecer v4 wants a new top-level `core/`.

**Decision.**

1. The control plane remains Python 3.10+ (`pyproject.toml` `requires-python = ">=3.10"`). This
   reaffirms ADR-0006 and ADR-0063.
2. The canonical production lattice is `vanguard/packages/`
   (`domain → ports → kernel → agency → runtime → adapters`, plus `apps/` as a client package).
   Composition root remains `vanguard/packages/runtime/root.py`.
3. `layer0/` is a copy-fork under convergence. Promote from it: SPI protocols, `jsonrpc.py`,
   broker/sandbox cell, lifecycle FSM, compose digest shape. Keep from packages: S0–S12 kernel
   semantics, JCS, SQLite WAL, exterior evaluator, sandbox, stores, models, episode engine.
4. Duplicate `layer0/` modules MUST NOT be deleted until a later behavioral parity gate. No
   wholesale directory migration.
5. A third identity (`core/`, `aether-rust/`, or a new top-level microkernel tree) is forbidden
   in v0.6.
6. Rust may enter later only if a named TCB hot path fails a measured gate. A Rust rewrite of the
   core is rejected as v0.6 architecture.

This ADR **reverses** the SPEC v0.5.0 sentence that `layer0/` is the M1 destination. Newer ADR
wins by citation.

**Alternative considered (and rejected).**

- Rebuild Layer 0 in `layer0/` and treat packages as legacy with an exit date (execution plan).
  Rejected: would rebuild WAL/evaluator/sandbox that already exist.
- Extract a new `core/` package (parecer v4). Rejected: third identity beside two living trees.
- Strangler-fig Rust core with Python as oracle (Full Refactor v3.1). Rejected: no Rust team
  evidence, no measured TCB gate, would create a third system. ADR-0006 and DEF-05 stand.
- Delete `layer0/` immediately. Rejected: SPI/jsonrpc/lifecycle have no complete packages twin yet.

**Evidence / bound test / links.** Forensic §§3–6, 19 P0-1/P0-2; `.github/workflows/ci.yml`;
`vanguard/packages/adapters/stores/event_store.py` (`PRAGMA journal_mode = WAL`);
`vanguard/packages/adapters/evaluators/daemon.py`;
`vanguard/packages/adapters/sandbox/toolkit.py` (already imports `layer0.spi.jsonrpc`);
`test/kernel` 95 OK not in living CI. `REQ-TRUST-001`, `REQ-DOG-001`. Bound tests land in the
code phase (CI subject-of-record); this ADR locks the target, not the wiring.

**Reversal condition.** A measured gate showing the packages lattice cannot preserve S0–S12
semantics, WAL durability, and exterior evaluation together — recorded in a newer ADR — plus an
explicit decision to replace the lattice. Preference, review seniority, or a green `test/layer0`
suite is not reversal.

**Owner · status.** Principal Staff Engineer / Tech Lead · accepted · 2026-08-20 · accepted
