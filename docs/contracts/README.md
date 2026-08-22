---
status: living
id: contracts-index
class: contract-reference
authority: descriptive
canonical_for:
  - contracts-and-schemas-index
source_of_truth:
  - docs/SPEC.md
derived_from:
  - schemas/mhf/
applies_to:
  - v0.6.1
implementation_status: AS_BUILT
owner: principal-systems-architect
version: "0.6.1"
last_verified: 2026-08-21
supersedes: []
superseded_by: null
---

# Vanguard / AETHER Contracts & Schemas Index

> **Classification:** Contract Reference (`AS_BUILT`).  
> **Authority:** Derived projection. Governing schemas live in [`schemas/`](../../schemas/) and normative law lives in [`docs/SPEC.md`](../SPEC.md).

---

## Wire & Data Contracts

| Contract | Schema `$id` | Producer / Writer | Key Invariants & Guarantees |
|---|---|---|---|
| [`events.md`](events.md) | `mhf.event/1` | `runtime/ledger_emitter.py` | 56 catalogued event kinds; single-writer authority; full causal lineage |
| [`trajectories.md`](trajectories.md) | `mhf.trajectory/1` | `runtime/trajectory.py` | NOVA-1: attributable model route, conserved cost vector, identity $D_H/D_R/D_X$ |
| [`manifests.md`](manifests.md) | `mhf.manifest/2` | `runtime/compose.py` | Named Component Graph; typed plugin declarations and capability bindings |
| [`verdicts.md`](verdicts.md) | `mhf.spi_payloads/1` | `adapters/evaluators/daemon.py` | Ed25519 cryptographic signature over canonical JCS bytes; request/nonce bound |
| [`selectors_and_budgets.md`](selectors_and_budgets.md) | Stdlib Python | `domain/selectors/` | Monotonic capability containment algebra; typed 6D budget dimensions |
