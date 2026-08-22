---
status: living
id: architecture-traceability-matrix
class: architecture
authority: descriptive
canonical_for:
  - bidirectional-traceability-matrix
source_of_truth:
  - docs/SPEC.md
  - docs/05_adr/INDEX.md
derived_from:
  - vanguard/packages/
  - test/
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Bidirectional Traceability Matrix

> **Status:** `AS_BUILT` · Descriptive View.

This matrix maps foundational concepts directly to normative law, accepted decisions, wire schemas, code symbols, executable falsifiers, and milestone gates.

| Concept | Law Clause | Accepted ADR | Schema / Port | Code Symbol | Falsifier / Test | Milestone |
|---|---|---|---|---|---|---|
| **S0–S12 Dispatch** | SPEC §4.2, KERNEL §2 | ADR-0054 | `ports/kernel.py` | `kernel/dispatch.py:dispatch` | `test_dispatch.py` | M-1 (Green) |
| **Capability Attenuation** | SPEC §3.1, KERNEL §3 | ADR-0012, ADR-0070 | `domain/selectors/` | `kernel/attenuation.py:attenuate` | `test_attenuation.py` | M-1 (Green) |
| **6D Budget Algebra** | SPEC §4.3, KERNEL §4 | ADR-0074 | `ports/kernel.py` | `kernel/budget.py:BudgetEngine` | `test_budget.py` | M-1 (Green) |
| **Ledger Single Writer** | SPEC §2.1 | ADR-0071, ADR-0076 | `ports/event_store.py` | `runtime/ledger_emitter.py:LedgerEmitter` | `test_ledger_truth.py` | M-1 (Green) |
| **Exterior Signed Judge** | SPEC §1.3 | ADR-0072, ADR-0076 | `schemas/mhf/spi_payloads.schema.json` | `adapters/evaluators/daemon.py` | `test_signed_verdict.py` | M-1 (Green) |
| **JCS Canonicalization** | SPEC §6.1 | ADR-0009, ADR-0076 | RFC 8785 | `domain/canonicalisation/jcs.py:canonicalize` | `test_jcs.py` | M-1 (Green) |
| **Truthful Trajectory** | SPEC §6.2 | ADR-0078 | `schemas/mhf/trajectory.schema.json` | `runtime/trajectory.py:assemble_trajectory` | `test_rf23_trajectory_content.py` (RF-23) | M-2 (In Progress) |
| **SQLite WAL Continuation** | SPEC §2.2 | ADR-0082 | `ports/event_store.py` | `runtime/ledger/recovery.py:recover_session` | `test_rf25_cold_continuation.py` (RF-25) | M-2 (In Progress) |
| **Named Component Graph** | SPEC §5.1 | ADR-0077 | `schemas/mhf/manifest.schema.json` | `runtime/compose.py` | RF-28…RF-33 | M-3 (Queued) |
| **Plugin Lifecycle FSM** | SPEC §5.2 | ADR-0081 | `domain/wire/` | `runtime/service/` | RF-38…RF-45 | M-3 (Queued) |
| **Mediated `agent.spawn`** | SPEC §3.2 | ADR-0080 | `ports/kernel.py` | `agency/episode/engine.py:spawn` | RF-55…RF-59 | M-6 (Deferred) |
