---
id: decision.index
canonical_id: decision.index
class: decision
authority: binding-decision-navigation
truth_plane: TARGET
status: living
implementation_status: UNRESOLVED
owner: repository-governance
canonical_for:
  - active rationale navigation
  - supersession links
purpose: Navigate current accepted architectural decisions while preserving immutable ADR provenance and unresolved index defects.
audience:
  - architect
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
normative_authority:
  - docs/02_decisions/INDEX.md
relationships:
  - spec.core
  - execution.milestones
reviewer: delegated-tech-lead-block-e
confidence: high
---

# Current Decision Navigation

## Authority and provenance

This TARGET page is a navigation and rationale view. The immutable records under `docs/02_decisions/` remain the decision provenance; this candidate neither rewrites nor replaces them. Law Zero and the normative specification outrank every ADR. An accepted ADR is binding only within that hierarchy and, where it changes law, only when the law is amended consistently.

## Current accepted decision families

| Family | Indexed ADRs | Current rationale owned |
|---|---|---|
| Runtime convergence and trust foundation | `0069`–`0076` | Python-first canonical lattice, recursive substrate, ledger authority, identity trinity, exterior evaluator, typed budgets, canonical artifacts |
| Evolution contracts | `0077`–`0085` | Named composition graph, complete trajectories, evidence missingness, mediated spawn, plugin lifecycle, universal turn loop, profile/strategy reservations |
| Repository governance | `0086`–`0087` | Historical ADR recovery and documentation authority topology |
| M-3C through M-8 concept lock | `0088` | One composition/activation/run path and bounded future seams; milestone sequencing is superseded where indexed |
| Product runtime profiles | `0089` | Explicit assurance profiles, bootstrap authority, real activation, generic entrypoint, durable streaming |
| Delegation and measurement | `0090`–`0094` | Child event ownership, child-state identity, measurement boundary, release baseline, product-first M-4 |
| Constitutional authority | `0095`–`0098` | Vision as Law Zero, proof-honest evidence, two-lane activation, strict event `/2` evolution |
| Scheduler, memory, evidence, and convergence | `0099`–`0105` | Sequential scheduler disposition, M-8 memory/promotion, receipt-backed acceptance, successor baseline, progress projection, verifier separation, Governor thread safety |
| Transform and recovery seam | indexed `0106` | Deterministic transforms, bounded protocol recovery, state-dependent tool policy, failure attribution, preflight, and `mhf.topology/2` seam |

## Supersession and amendment edges

- `ADR-0095` makes `VISION.md` Law Zero and supersedes conflicting roadmap identity or sequencing.
- `ADR-0094` replaces `ADR-0088`'s former M-4 blocking dependence on RF-85; RF-85 remains optional assurance.
- `ADR-0097` refines M-5b/M-6 sequencing without changing milestone meaning.
- `ADR-0102` supersedes the invalid `M-5A-BASE-v2` baseline claims in `ADR-0097` and `ADR-0098`.
- `ADR-0104` supersedes active human/process approval dependencies while preserving product-time operator approval and independent verifier identity.
- `ADR-0099` records `SEQUENTIAL_CONFIRMED`; `ADR-0105` adds defensive Governor thread safety without authorizing concurrency.

## Unresolved authority defect

`CONFLICT-E-001` is unresolved: two files declare accepted ADR number `0106`.

- `docs/02_decisions/INDEX.md` indexes `0106-deterministic-transform-algebra-and-protocol-recovery.md`.
- `0106-evo14-readonly-concurrency-authorized-by-measurement.md` is accepted-labelled but is absent from the index and duplicates the identifier while narrowly claiming to amend `ADR-0099`.

The indexed record is used for TARGET claims. The unindexed duplicate is preserved as conflicting provenance and does **not** authorize concurrency in this reconstruction. Resolving the duplicate requires ADR governance; this page does not renumber, rewrite, or choose a new decision identity.

## Retrieval rule

Use the [TARGET specification](../SPEC.md) for obligations, the AS_BUILT architecture pages for implementation, and the immutable ADR body for rationale. An ADR title or accepted status never proves that its mechanism exists or has passed an execution gate.
