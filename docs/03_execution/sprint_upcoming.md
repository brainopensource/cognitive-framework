---
id: upcoming-sprint-board
class: execution
authority: execution
canonical_for:
  - next-qualified-work-window
status: living
owner: tech-lead
version: "1.0.0"
last_verified: 2026-08-27
subordinate_to: ../../VISION.md
supersedes:
  - leadership-sprint-upcoming-2026-08-25
superseded_by: null
---

# Upcoming Development Waves — AETHER v0.9

This file is preparation, not current authorization. Items move to
[`sprint_active.md`](sprint_active.md) only when their named entry gates are true.

The remaining implementation is organized into two lanes. Work starts when the
listed machine predicate is true; evidence integrity remains separate from
package readiness.

| Sprint | Order | Package | Owner | Planned state | Entry gate | Exit |
|:--|---:|---|---|---|---|---|
| C2 | 1 | WP-A2 | Lane A | **BLOCKED** | WP-A1 merged (`ca683fd`) ✓; progress/checkpoint contract frozen (ADR-0103) ✓; WP-C1 package predicate unresolved | runtime seam `PACKAGE_READY` |
| C3 | 2 | WP-A3 | Lane A | **NOT_STARTED** | WP-A1 canonical recursion merged ✓ | three runtime topologies |
| C3 | 3 | WP-B3 | Lane B | **NOT_STARTED** | WP-A3 topology bundle and telemetry completeness | M7-01 receipt; ADR-0099 disposition |
| C4 | 4 | WP-A4 | Lane A | **NOT_STARTED** | ADR-0099 M-7 disposition; ADR-0100 contract kit frozen | security/recovery evidence |
| C4 | 5 | WP-B4 | Lane B | **NOT_STARTED** | WP-A4 memory/registry contract; valid M-6.5 disposition | held-out lift and real rollback |

Wave order is W1 implementation -> W2 M-8 implementation -> consolidated review and repair.
Lane A and Lane B may work in parallel after the current predicates are true; W2 may prepare against
frozen contracts but cannot claim M-8 acceptance until M-6.5 and M-7 have valid dispositions. Full contracts remain in
[`backlog.md`](backlog.md).

M-9/M-10 are stable release stages in [`milestones.md`](milestones.md); implementation begins only
when their predecessor predicates are true.
