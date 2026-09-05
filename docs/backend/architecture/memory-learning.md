---
id: arch.memory.learning
canonical_id: arch.memory.learning
class: architecture
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: memory-learning
canonical_for:
  - memory authority/data flow
  - category persistence
  - retrieval provenance
  - promotion/rollback lifecycle
purpose: Detail memory data flow, scoped authorization before retrieval, skill persistence, and governed composition promotion.
audience:
  - developer
  - architect
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-037
  - E-B-038
  - E-B-039
relationships:
  - arch.system.overview
  - arch.trust.kernel
  - ref.artifacts
  - ref.ports
reviewer: documentation-specialist
confidence: high
---

# Memory & Governed Learning Architecture

## Purpose
This document is the canonical architecture owner for the memory subsystem data flow, scoped authorization before memory retrieval (`INV-B-010`), episodic and semantic persistence tiers, and the governed promotion and rollback lifecycle for learned skills and compositions.

## Scope
- Memory authority boundaries and the `IMemoryEngine` SPI.
- Pre-retrieval capability authorization checks (`INV-B-010`).
- Durability tiers: working memory, episodic turn memory, semantic workspace knowledge, and procedural rules.
- Skill capture, verification, and governed promotion lifecycle (`learning.py`).
- Reversion, blacklisting, and rollback mechanics.

## Non-responsibilities
- Exact memory port protocol signatures and dataclass structures (owned by [`ref.artifacts`](../reference/artifacts-memory.md) and [`ref.ports`](../reference/ports.md)).
- Operational memory management guides (owned by [`guide.operate-service`](../guides/operate-runtime-service.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Scoped memory retrieval, SQLite storage engines, and governed learning promotions are operational in `vanguard.packages.runtime.memory` and `vanguard.packages.runtime.governance.learning`.

---

## 1. Memory Authority & Data Flow

Memory retrieval is a mediated side-effect that accesses historical or cross-session state.

```text
Turn Context Compiler / Agent
            │
            │ Submits MemoryQuery + CapabilityGrant
            ▼
Runtime Memory Service (vanguard.packages.runtime.memory)
            │
            │ [INV-B-010] Verify Grant Scopes & Principal
            ▼
SqliteMemoryEngine / Store Adapter
            │
            ▼
Returns Scored MemoryHits with Provenance Digests
```

---

## 2. Scoped Authorization Before Retrieval (`INV-B-010`)

To prevent data exfiltration, privilege escalation, or cross-tenant contamination across agent runs:

- **Strict Pre-Retrieval Check**: The memory engine verifies that the caller presents a valid, unexpired `CapabilityGrant` with `memory:read` permissions for the requested categories *before* performing indexing, similarity matching, or record dereference.
- **Provenance Tagging**: Every returned `MemoryHit` includes its source `event_id`, `run_id`, and `record_digest`, ensuring full causal auditability in the active turn context.

---

## 3. Durability & Memory Categories

The memory architecture organizes information across four lifecycle categories:

| Tier | Scope | Durability | Access Mechanism |
|---|---|---|---|
| **Working Memory** | Active Turn / Episode | In-memory only (ephemeral) | Direct context scratchpad. |
| **Episodic Memory** | Active Run & Lineage | SQLite WAL (durable) | Semantic query over turn receipts and tool outcomes. |
| **Semantic Memory** | Workspace Root | SQLite WAL (durable) | Fact extraction, indexed symbols, code documentation. |
| **Procedural Memory** | Governed Global | Versioned Pack (promoted) | Explicitly approved operational skills and policies. |

---

## 4. Skill Extraction & Governed Promotion Lifecycle

Vanguard implements a formal promotion pipeline before learned behaviors can modify agent defaults:

```text
[ Raw Turn Trajectory ]
         │
         ▼
[ Skill Candidate Extraction ] (Synthesizes task pattern into reusable skill pack)
         │
         ▼
[ Exterior Evaluator Attestation ] (Requires signed hermetic evaluation score >= 1.0)
         │
         ▼
[ Operator Ed25519 Approval ] (Governance gate validates promotion)
         │
         ▼
[ Promoted Procedural Rule / Pack ] (Assigned new immutable composition digest)
```

### Rollback & Quarantine Semantics
- If a promoted skill causes regressions in subsequent evaluations, the governance engine emits `CanaryRollback` and adds the skill digest to the workspace blacklist.
- Rollbacks are instantaneous because composition digests are immutable.

---

## Implementation Evidence

- **Memory Service**: `vanguard/packages/runtime/memory.py`.
- **Governed Learning**: `vanguard/packages/runtime/governance/learning.py`.
- **Memory Adapter**: `vanguard/packages/adapters/stores/memory_engine.py`.
- **Security & Authorization Tests**: `test/security/test_m8_memory_falsifiers.py`, `test/security/test_m8_memory_fake_parity.py`, `test/runtime/test_governed_learning.py`.

---

## Architectural Decisions & Philosophical Rationale

### DEC-10 — Authorization-Before-Ranking in Memory Retrieval

- **Decision:** Memory retrieval must verify principal access scope, category isolation, and legal hold/revocation *before* relevance ranking and artifact dereference.
- **Rationale:** Post-ranking filtering leaks existence and metadata of unauthorized memory entries through relevance score distortions and token side-channels.
- **Rejected alternative:** Retrieve-and-rank first, followed by downstream output filtering of unauthorized documents.
- **Reversal condition:** Zero-knowledge cryptographic vector search that provably prevents cross-principal information leakage during un-authenticated indexing.

