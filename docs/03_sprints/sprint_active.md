---
id: SPRINT-V060-FOUNDATION-BOARD
file: docs/03_sprints/sprint_active.md
title: "Active board — v0.6 Foundation (Wave 0 in flight → Wave 1 queued)"
status: ACTIVE
milestone: M-0 (Wave 0, separate team) → M-1 (Wave 1, queued)
spec: docs/SPEC.md
law: ADRs 0069–0076 + docs/04_annex/
register: docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md
plans: docs/03_sprints/plans/
last_reviewed: 2026-08-20
---

# Active board — v0.6 Foundation

**Start here if you are new:** read
[`plans/000_CANONICAL_EXECUTION_PATH.md`](plans/000_CANONICAL_EXECUTION_PATH.md) first — it names
production truth, the one flow, and the decisions you must not re-make. Then your wave plan.

## Now

| Lane | State | Who |
|---|---|---|
| **Wave 0 — CI truth + falsifiers** | IN FLIGHT | Wave-0 team (separate); exit gate in `002` §3 |
| **Wave 1 — Trust spine** | **QUEUED — entry: Wave 0 exit gate green** | Next assignment; plan: [`plans/wave1_trust_spine.md`](plans/wave1_trust_spine.md) |

### Wave 1 assignment slices (parallelizable)

- **Slice A (evidence):** Sprint 1.1 tasks 1.1-A…G — signed-verdict loop + translator. One developer.
- **Slice B (state):** Sprint 1.2 tasks 1.2-A…F — LedgerEmitter, lineage, cold replay. One developer. Runs parallel to A.
- **Slice C (identity):** Sprint 1.3 — starts when B lands the emitter; 1.3-C (kernel budget diff) needs Tech Lead review before merge.

### Blocked / decision queue

| Item | Needs | Owner |
|---|---|---|
| 1.2-C `project_id` source | Pick config-declared vs workspace-derived id | Tech Lead |
| 1.3-C kernel diff | Pre-merge review (TCB surface) | Tech Lead |
| 2.2-A parity triage | Keep/kill list for layer0 assertions | Tech Lead (at Wave 2 entry) |
| Release/version cut after M-4 | Decision | Director |

## Already settled — do not reopen on this board

Canonical envelope, one selector algebra, JCS-only bytes, `D_H` definition, verdict binding fields,
single writer (ADR-0076). Scope refusals: SPEC §9. Verdicts on "should we…" questions those cover:
no.

## Scaffolds waiting for completion

| Scaffold | Landed | Completes in |
|---|---|---|
| `schemas/mhf/trajectory.schema.json` (mhf.trajectory/1) | Director prep | 1.3-D |
| `SignedVerdict` binding fields (`schemas/mhf/spi_payloads.schema.json`) | Director prep | 1.1-B/C/F |
| Envelope lineage fields (`schemas/mhf/event_envelope.schema.json`) | Director prep | 1.2-A |

## Definition of done (every task)

Falsifier/acceptance evidence named in the wave plan passes on the canonical path · suites of
record stay green · boundary/TCB/duplication linters green · no new `layer0` imports · trajectory,
envelope, verdict shapes validate against `schemas/mhf/`.
