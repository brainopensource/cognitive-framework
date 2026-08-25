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
last_verified: 2026-08-23
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Vanguard / AETHER Contracts & Schemas Index

> **Authority.** These contracts are subordinate to [`VISION.md`](../../VISION.md) (Law Zero, `ADR-0095`), then [`SPEC.md`](../SPEC.md) and [`01_law/`](../01_law/). They realize the law on the wire and introduce no architecture of their own. Where they still describe the pre-0095 architecture, the Vision wins and the text is reconciled.


> **Classification:** Contract reference with maturity stated per row.
> **Authority:** Derived projection. Governing schemas live in [`schemas/`](../../schemas/) and normative law lives in [`docs/SPEC.md`](../SPEC.md).

---

## Wire & Data Contracts

For implementation, follow each row from contract page → generated schema → producer/reader → bound
test. Contract pages are concise discovery aids and must not maintain a second JSON example or field
matrix when a schema already owns the exact shape.

| Contract | Schema `$id` | Producer / Writer | Key Invariants & Guarantees |
|---|---|---|---|
| [`events.md`](events.md) | `mhf.event/1` | `runtime/ledger_emitter.py` | `AS_BUILT`: schema catalog plus role-owned emission |
| [`trajectories.md`](trajectories.md) | `mhf.trajectory/1` | `runtime/trajectory.py` | `ACTIVE_REPAIR`: schema exists; RF-23 content/accounting proof is red |
| [`manifests.md`](manifests.md) | `mhf.manifest/2` | M-3 compose target | `IMPLEMENTED_PENDING_M3_GATE`: Named Component Graph |
| [`verdicts.md`](verdicts.md) | `mhf.spi_payloads/1` | `adapters/evaluators/daemon.py` | Ed25519 cryptographic signature over canonical JCS bytes; request/nonce bound |
| [`selectors_and_budgets.md`](selectors_and_budgets.md) | Stdlib Python | `domain/selectors/` | Monotonic capability containment algebra; typed 6D budget dimensions |
