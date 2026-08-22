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
implementation_status: RATIFIED_NOT_IMPLEMENTED
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Bidirectional Traceability Matrix

> **Status:** Mixed maturity. This is a navigation projection, not proof by itself; each row states
> whether its subject is built, active work, or queued.

This matrix maps foundational concepts directly to normative law, accepted decisions, wire schemas, code symbols, executable falsifiers, and milestone gates.

| Concept | Law / Decision Owner | Schema / Port | Current Symbol | Evidence | Maturity / Gate |
|---|---|---|---|---|---|
| **S0–S12 Dispatch** | SPEC §1; KERNEL §2; ADR-0069/0074 | `ports/kernel.py` | `kernel/dispatch.py:Kernel.dispatch` | `test/kernel/test_dispatch.py` | `AS_BUILT` · M-1 green |
| **Capability Attenuation** | SPEC §1.0; KERNEL §4; ADR-0070/0074 | `domain/selectors/` | `kernel/attenuation.py:attenuate` | `test/kernel/test_attenuation.py` | `AS_BUILT` · M-1 green |
| **Typed Budget Algebra** | SPEC A-1/§1.0; ADR-0074 | `ports/kernel.py` | `kernel/budget.py:Governor` | `test/kernel/test_grant_budget_events.py` | `AS_BUILT` · M-1 green |
| **Ledger Single Writer** | SPEC §1.2; ADR-0071/0076 | `ports/event_store.py` | `runtime/ledger_emitter.py:LedgerEmitter` | `test/runtime/test_ledger_truth.py` | `AS_BUILT` · M-1 green |
| **Exterior Signed Judge** | SPEC §0/§1.2; ADR-0072/0076 | `schemas/mhf/spi_payloads.schema.json` | `adapters/evaluators/signing.py:VerdictSigner` | `test/adapters/test_evaluator_signing.py` | `AS_BUILT` · M-1 green |
| **JCS Canonicalization** | SPEC A-4; ADR-0076 | RFC 8785 | `domain/canonicalisation/jcs.py:canonical_bytes` | `test/contracts/t1_dev1_canonicalisation.py` | `AS_BUILT` · M-1 green |
| **Truthful Trajectory** | SPEC §7/I-9; ADR-0078 | `schemas/mhf/trajectory.schema.json` | `runtime/trajectory.py:assemble_trajectory` | `test/falsifiers/test_rf23_trajectory_content.py` | `ACTIVE_REPAIR` · RF-23 red, M-2 |
| **SQLite-WAL Continuation** | SPEC §1.3/I-4; ADR-0082 | `ports/event_store.py` | `runtime/ledger/recovery.py:replay_ledger_state` | `test/falsifiers/test_rf25_cold_continuation.py` | `ACTIVE_REPAIR` · RF-25 red, M-2 |
| **Named Component Graph** | ADR-0077 | planned `mhf.manifest/2` | current `runtime/compose.py:Runtime.compose` is not the graph | RF-28…RF-33 | `RATIFIED_NOT_IMPLEMENTED` · M-3 |
| **Plugin Lifecycle Parity** | SPEC §2.1; ADR-0081 | current catalog has five of seven target events | current reducer folds `PluginResolved`…`PluginFaulted` | RF-38…RF-45 | `RATIFIED_NOT_IMPLEMENTED` · M-3 |
| **Mediated `agent.spawn`** | SPEC A-6; ADR-0080 | future S0–S12 verb | current `EpisodeEngine.spawn` is not the M-6 mediated effect | RF-55…RF-59 | `RATIFIED_NOT_IMPLEMENTED` · M-6 |
