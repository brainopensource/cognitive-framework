---
id: upcoming-sprint-board
class: execution
authority: execution
canonical_for:
  - next-qualified-work-window
status: living
owner: tech-lead
version: "1.0.0"
last_verified: 2026-08-26
subordinate_to: ../../VISION.md
supersedes:
  - leadership-sprint-upcoming-2026-08-25
superseded_by: null
---

# Upcoming Sprints — Measured Control, Topology, and Memory

This file is preparation, not authorization. Items move to
[`sprint_active.md`](sprint_active.md) only when their named entry gates are true.

| Sprint | Order | Package | Owner | Planned state | Entry gate | Exit |
|:--|---:|---|---|---|---|---|
| C2 | 1 | WP-A2 stable meta-control observation seam | Dev A | **BLOCKED** | WP-A1 merged (`ca683fd`) ✓; progress/checkpoint contract frozen (ADR-0103) ✓; **C1 independent acceptance outstanding** | runtime seam `PACKAGE_READY` |
| C2 | 2 | WP-B2 stochastic instrument and paired M-6.5 study | Dev B | **NOT_STARTED** | WP-A1 merged ✓; WP-A2 contract frozen (ADR-0103) ✓; provider/task fixtures reviewed | signed positive/negative evidence |
| C3 | 3 | WP-A3 sequential topology integration and timing telemetry | Dev A | **NOT_STARTED** | WP-A1 canonical recursion merged ✓ | three runtime topologies |
| C3 | 4 | WP-B3 M7-01 and ADR-0099 evidence package | Dev B | **NOT_STARTED** | WP-A3 topology bundle and telemetry completeness | accepted report; ADR-0099 decision |
| C4 | 5 | WP-A4 durable authorized memory | Dev A | **NOT_STARTED** | ADR-0099 M-7 disposition; ADR-0100 contract kit frozen | security/recovery evidence |
| C4 | 6 | WP-B4 governed promotion and rollback | Dev B | **NOT_STARTED** | WP-A4 memory/registry contract; valid M-6.5 disposition | held-out lift and real rollback |

Merge order is A2 -> B2 final study; A3 -> B3 -> ADR-0099; A4 -> B4 -> M-8 gate. M-6.5 and
M-7 package construction may overlap after C1 because their files and evidence subjects are disjoint;
M-8 remains dependency-blocked. Full contracts are in [`backlog.md`](backlog.md).

M-9/M-10 remain absent from the sprint system. Their only current influence is the compatibility
boundary in [`milestones.md`](milestones.md): exterior candidates, immutable compositions, authorized
memory, and run-plan extension seams.
