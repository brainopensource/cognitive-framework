# Active Sprint Execution Board

> **Purpose**: Single operational surface for the CURRENT active sprint.
> **Audience**: Tech Lead, Active Developers, and AI Agents executing the current sprint.
> **Protocol**:
> - Tasks listed here are checked out directly from `docs/02_roadmap/backlog.md`.
> - Status changes MUST be mirrored back to `docs/02_roadmap/backlog.md` upon completion.
> - Only ONE sprint file is active at any given time.

---

## Active Sprint Metadata

- **Sprint Name**: Sprint 01 — v0.5.0 Core Engine Reset
- **Milestone Target**: `[MS-0.5.0]`
- **Start Date**: YYYY-MM-DD
- **End Date**: YYYY-MM-DD
- **Sprint Lead**: Tech Lead
- **Sprint Goal**: Restore pure episode loop in core runtime and eliminate static DAG coordinator debt.

---

## Active Task Execution Queue

| Task ID | Title / Summary | Subsystem | Owner / Assignee | Status | DoD Check |
|---|---|---|---|---|---|
| `[TASK-M050-001]` | Extract Invocation Domain Model | `domain` | `[AI-Agent-1]` | `[IN_PROGRESS]` | ⏳ Pending |
| `[TASK-M050-002]` | Deprecate Static DAG Coordinator | `runtime` | `[AI-Agent-2]` | `[TODO]` | ⏳ Pending |

---

## Active Task Detail Cards

### [TASK-M050-001] Extract Invocation Domain Model to Pure Domain Package
- **Source Backlog Item**: [TASK-M050-001](file:///home/rocha/Coding/Aether-D-System/docs/02_roadmap/backlog.md)
- **Assignee**: AI Agent / Developer Name
- **Current Branch**: `feat/task-m050-001-invocation`
- **Execution Log**:
  - `YYYY-MM-DD HH:MM` - Checked out task. Created branch.
- **Verification Commands**:
  ```bash
  python3 -m unittest test.domain.test_invocation -v
  python3 tools/check_boundaries.py
  ```

---

## Daily Blockers & Notes

- **Blockers**: None currently logged.
- **Sprint Retrospective / Closure Notes**: (To be completed at sprint end before archiving).
