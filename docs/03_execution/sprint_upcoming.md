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

# Upcoming Development Waves — M-4 through M-8

This file is preparation, not current authorization. Items move to
[`sprint_active.md`](sprint_active.md) only when their named entry gates are true.

The remaining implementation is organized into two parallel development waves.
Developers may build in parallel and defer the consolidated review until both
waves are complete; milestone acceptance, evidence integrity, and independent
review still remain separate closure requirements.

| Sprint | Order | Package | Owner | Planned state | Entry gate | Exit |
|:--|---:|---|---|---|---|---|
| C2 | 1 | WP-A2 | Dev A | **BLOCKED** | WP-A1 merged (`ca683fd`) ✓; progress/checkpoint contract frozen (ADR-0103) ✓; **C1 independent acceptance outstanding** | runtime seam `PACKAGE_READY` |
| C3 | 2 | WP-A3 | Dev A | **NOT_STARTED** | WP-A1 canonical recursion merged ✓ | three runtime topologies |
| C3 | 3 | WP-B3 | Dev B | **NOT_STARTED** | WP-A3 topology bundle and telemetry completeness | accepted report; ADR-0099 decision |
| C4 | 4 | WP-A4 | Dev A | **NOT_STARTED** | ADR-0099 M-7 disposition; ADR-0100 contract kit frozen | security/recovery evidence |
| C4 | 5 | WP-B4 | Dev B | **NOT_STARTED** | WP-A4 memory/registry contract; valid M-6.5 disposition | held-out lift and real rollback |

Wave order is W1 implementation -> W2 M-8 implementation -> consolidated review and repair.
Dev A and Dev B may work in parallel after C1; W2 may prepare against frozen contracts but cannot claim
M-8 acceptance until M-6.5 and M-7 have valid dispositions. Full contracts remain in
[`backlog.md`](backlog.md).

M-9/M-10 remain absent from the sprint system. Their only current influence is the compatibility
boundary in [`milestones.md`](milestones.md): exterior candidates, immutable compositions, authorized
memory, and run-plan extension seams.
