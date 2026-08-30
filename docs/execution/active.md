---
id: execution.active
canonical_id: execution.active
class: execution
authority: execution
truth_plane: TARGET
status: living
implementation_status: UNRESOLVED
owner: repository-governance
canonical_for:
  - current work/state/ownership
purpose: Represent current execution intent exactly as the active board states it, including unresolved internal status conflicts.
audience:
  - contributor
  - release-owner
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
normative_authority:
  - docs/03_execution/sprint_active.md
  - docs/03_execution/backlog.md
relationships:
  - execution.milestones
  - decision.index
reviewer: delegated-tech-lead-block-e
confidence: high
---

# Current Execution Intent

## Authoritative source

`docs/03_execution/sprint_active.md` declares itself the sole current execution board. This candidate view does not turn its package state into architecture or normative law.

## Uncontested current controls

- Lane A owns runtime, execution, persistence, clients, packaging, deployment, operations, and release surfaces.
- Lane B owns domain/ports contracts, schemas, projections, evaluation semantics, falsifiers, experiments, and promotion criteria.
- Each lane has WIP=1 and one current package.
- Package progression is predicate-driven; product-time approval for privileged effects remains separate from development workflow.
- Exact-subject verifier receipts, not prose or green test counts, close evidence gates.

## Board-declared current packages

| Lane | Package | Board state | Declared next action |
|---|---|---|---|
| A | `WP-A3` | `IN_PROGRESS` | Repair abandoned multi-role lineages and publish M-7 evidence only after real artifact flow |
| B | `WP-B4` | `PACKAGE_READY` | Close baseline, M-5b, M-6.5, and independently accepted M-8 evidence dependencies in order |

## Unresolved status conflicts

The same active board later reports verified `passed` bundles for M-7 and M-8, while its current-package table and critical path still describe both as unfinished. It also describes `CONVERGENCE-BASE-v1` as published while the stable milestones document says the tag is absent and M-8 has no published bundle.

These are `UNRESOLVED` authority conflicts, not permission to choose the most favorable state. Until the active execution authority is corrected atomically:

- treat the package table as the declared work assignment;
- treat individual verifier rows only as claims about the named bundle;
- do not infer milestone acceptance where the board's own predicates disagree;
- do not advance M-9 from staging based on this candidate page.

The exact conflicts and required governance follow-up are recorded as `CONFLICT-E-002` through `CONFLICT-E-004` in `.generated/knowledge/target-conflicts.jsonl`.

## Stable package contracts

The active board supplies current authorization; the [canonical backlog](../../docs/03_execution/backlog.md)
supplies the stable M-4–M-8 package contracts, lane ownership, dependencies, acceptance predicates,
and evidence obligations. This candidate view links that detail rather than copying its mutable
tables, so package status cannot be mistaken for a second active board.
