---
id: ref.schemas
canonical_id: ref.schemas
class: reference
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: domain-wire
canonical_for:
  - schema family catalog
  - producer/consumer map
  - generation/vector relationships
  - compatibility status
purpose: Route exact schema families to producers, consumers, generated readers and vectors.
audience:
  - developer
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-005
  - E-B-008
  - E-B-012
  - E-B-021
  - E-B-027
  - E-B-040
  - E-B-041
  - E-B-044
  - E-B-045
  - E-B-046
  - E-B-048
  - E-B-049
  - E-B-050
  - E-B-051
  - E-B-053
  - E-B-054
relationships:
  - arch.system.overview
  - ref.events
  - ref.runtime-service
  - ref.manifests
reviewer: documentation-specialist
confidence: high
---

# JSON Schemas & Wire Contracts Reference

## Purpose
This document is the canonical reference owner for the catalog of JSON Schema families in the repository, their code generation mappings, producer/consumer relationships, and test vector corpora.

## Scope
- Schema families located in `schemas/` (`mhf/`, `v4/`, `contracts/`, `vectors/`).
- Code-generated Python bindings in `vanguard.packages.domain.wire.types_gen`.
- TypeScript client contract bindings in `@vanguard/client-core`.
- Documented vector corpora and compatibility caveats (`UNR-B-006`).

## Non-responsibilities
- Duplicating raw JSON schema texts (readers should consult the `schemas/` directory directly).
- Defining behavioral invariants from schema syntax alone (owned by [`arch.system.overview`](../../architecture/overview.md) and [`arch.trust.kernel`](../architecture/kernel.md)).
- Event envelope detailed semantics (owned by [`ref.events`](events.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Schema families are validated continuously in CI and generate typed domain models used across Python and TypeScript.

---

## 1. Schema Authority Caveat

JSON Schemas define external wire formats, serialized validation boundaries, and test vectors. While schemas establish type contracts, execution authority resides in the code and trusted kernel boundaries. The presence of a schema definition does not alone imply that an associated subsystem is active in the production runtime.

Repository change-surface estimates are domain observations rather than wire schemas. The
`ChangeSurfaceEstimator` records primary, related, and test paths with deterministic reasons;
pack middleware supplies bounded `IndexPort` symbol, dependency, and test observations. These
observations do not authorize edits or completion and remain subordinate to runtime policy and
exterior verification.

Semantic task state (`vanguard/packages/domain/task_state.py`, `SemanticTaskState` /
`CodingTaskState`) is a domain value with RFC 8785 JCS digest via `digest_of`. It is not a
`schemas/` wire family. Runtime `fold_task_state` is the only producer.

---

## 2. Active Schema Families

The repository organizes schemas into three primary functional families:

### A. MHF Schemas (`schemas/mhf/`)

The Modular Harness Framework (MHF) schemas represent core agent and runtime contracts:

| Schema File | Wire API Version | Primary Producer | Primary Consumer | Purpose |
|---|---|---|---|---|
| `event_envelope.schema.json` | `mhf.event/1`, `mhf.event/2` | `LedgerEmitter` | `EventEnvelope`, event stores | Event envelope format and kind enum. |
| `manifest_v2.schema.json` | `mhf.manifest/2` | Pack authors | `ManifestLoader`, `compose.py` | Component declarations, tool packs, bindings. |
| `execution_profile_v2.schema.json`| `mhf.execution-profile/2` | `profiles.py` | `HarnessSession`, `RunPlan` | Containment, approval, and assurance profiles. |
| `trajectory_v2.schema.json` | `mhf.trajectory/2` | `EpisodeEngine` | `EvaluatorGateway`, Evaluator | Causal turn trajectory capture format. |
| `verdict_v2.schema.json` | `mhf.verdict/2` | Exterior Evaluator | `EvaluatorGateway`, ledger | Signed evaluation verdicts and rubrics. |

### B. `vg.4` Runtime Service Schemas (`schemas/v4/`)

Schemas governing client-daemon IPC and JSON-RPC communication:

| Schema File | Wire Version | Producer | Consumer | Purpose |
|---|---|---|---|---|
| `runtime-service.schema.json` | `vg.4` | `RuntimeService`, `client-core` | Daemons, CLI, Studio | Discriminated frames, commands, and receipts. |
| `primitives.schema.json` | `vg.4` | Shared | Shared | Shared primitive types (UUIDs, IntString, digests). |
| `approval-decision.schema.json` | `vg.4` | CLI / Operator | Governance / Kernel | Ed25519-signed operator approval payloads. |

### C. `v4` Legacy & Compatibility Schemas

Compatibility schemas maintained for reading historical records and migration verification:
- `schemas/v4/event-envelope.schema.json`: VG-04 event envelope format.
- `schemas/v4/manifest.schema.json`: V1 manifest declaration shape.
- `schemas/v4/agent-view.schema.json`: In-memory agent projection shape.

---

## 3. Code Generation & Typed Readers

Schemas are compiled into strongly-typed language bindings:

1. **Python (`vanguard/packages/domain/wire/types_gen.py`)**:
   - Auto-generated dataclasses, enums, and typed unions (`EventKind`, `Proposal`, `Receipt`, `SignedVerdict`, `ManifestV2`).
   - Ensures runtime type-safety without manual type duplication.
2. **TypeScript (`vanguard/clients/client-core/src/contract/`)**:
   - Generated interfaces and type guards (`RuntimeServiceFrame`, `Command`, `CommandReceipt`, `ClientFailure`).

---

## 4. Test Vectors & Conformance Corpora (`UNR-B-006`)

The `schemas/vectors/` directory contains hundreds of golden test vectors used in contract testing:

- **Positive Vectors (`test_vectors_positive.json`)**: Valid message payloads tested against both Python and TypeScript validators to guarantee wire-level compatibility.
- **Negative Vectors (`test_vectors_negative.json`)**: Malformed or unauthorized payloads tested to ensure fail-closed schema rejection across all implementations.
- **Compatibility Corpora**: Historical payloads verifying that updated parsers do not reject previously recorded ledgers.

---

## Implementation Evidence

- **Schema Directory**: `schemas/mhf/`, `schemas/v4/`, `schemas/vectors/`.
- **Python Generated Types**: `vanguard/packages/domain/wire/types_gen.py`.
- **TypeScript Contract Types**: `vanguard/clients/client-core/src/contract/`.
- **Contract Parity Tests**: `test/contracts/test_runtime_service_vectors.py`, `test/contracts/test_event_substrate_v2.py`, `test/contracts/test_manifest_v2_graph.py`.
