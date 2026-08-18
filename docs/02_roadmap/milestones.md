# Product Roadmap & Milestones

> **Purpose**: High-level strategic roadmap breaking down the product vision into sequential milestones.
> **Audience**: Tech Lead, Product Lead, Developers, and AI Agents.
> **Rule for AI Agents**: Read this file to understand strategic objectives and milestone boundaries. Do NOT update task statuses here (use `backlog.md`).

---

## Strategic Overview

| Milestone ID | Target Version | Objective Summary | Target Date | Status |
|---|---|---|---|---|
| `[MS-0.5.0]` | v0.5.0 | Ground-Up Core Harness & Pure Episode Loop Rewrite | YYYY-MM-DD | `[IN_PROGRESS]` |
| `[MS-0.6.0]` | v0.6.0 | Multi-Agent Delegation & Advanced Tool Streaming | YYYY-MM-DD | `[PLANNED]` |

---

## Milestone Specifications (Templates)

### [MS-0.5.0] Ground-Up Core Harness & Pure Episode Loop Rewrite

- **Status**: `[IN_PROGRESS]`
- **Target Release**: `v0.5.0`
- **Lead / Owner**: Tech Lead
- **Primary Objectives**:
  1. Restore pure episode loop in `vanguard/packages/agency/episode/engine.py`.
  2. Eliminate static DAG coordinator debt in `vanguard/packages/runtime/`.
  3. Ensure 100% harness behavior is configurable via JSON manifests.
- **Affected Subsystems**: `domain`, `ports`, `kernel`, `agency`, `runtime`, `adapters`.
- **Milestone Definition of Done (DoD)**:
  - [ ] All architectural drift items in `SYSTEM_SPEC_DRIFTS.md` addressed.
  - [ ] 100% boundary check pass (`python3 tools/check_boundaries.py`).
  - [ ] 100% TCB budget pass (`python3 tools/check_tcb_budget.py`).
  - [ ] Full test suite green (`python3 -m unittest discover -s test -t .`).

---

### [MS-0.6.0] Multi-Agent Delegation & Tool Streaming

- **Status**: `[PLANNED]`
- **Target Release**: `v0.6.0`
- **Lead / Owner**: Tech Lead
- **Primary Objectives**:
  1. Real-time tool-use streaming protocol.
  2. Expose multi-agent sub-process spawning via harness manifests.
- **Affected Subsystems**: `agency`, `runtime`, `clients/cli`.
- **Milestone Definition of Done (DoD)**:
  - [ ] Sub-agent spawn verification tests pass.
  - [ ] Real-time event stream integration verified.
