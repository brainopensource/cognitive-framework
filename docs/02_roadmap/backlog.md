# Global Project Backlog (Single Source of Truth)

> **Purpose**: Centralized pool of all pending, active, and completed tasks across all milestones.
> **Audience**: Tech Lead, Human Developers, and AI Agents.
> **Protocol for AI Agents**:
> - This file is the **ONLY** source of truth for task existence and status tracking.
> - Valid Statuses: `[TODO]`, `[IN_PROGRESS]`, `[DONE]`, `[DEPRECATED]`, `[BLOCKED]`.
> - Assignee Tags: `[AI-READY]` (can be autonomously executed by AI) or `[HUMAN-ONLY]` (requires human key/credentials or manual decision).

---

## Backlog Task Schema Guidelines

Every task entry MUST adhere to the following machine-readable structure:

```markdown
### [TASK-MS_ID-NUM] Task Title Concise
- **Milestone**: [MS-X.Y.Z]
- **Subsystem**: vanguard/packages/<package_name>
- **Spec Anchor**: [Spec Document Name](file:///path/to/spec.md#LXX)
- **Assignee Tag**: [AI-READY] | [HUMAN-ONLY]
- **Status**: [TODO] | [IN_PROGRESS] | [DONE] | [DEPRECATED] | [BLOCKED]
- **Dependencies**: None | [TASK-MS_ID-NUM]
- **Definition of Done (DoD)**:
  - [ ] Actionable requirement 1
  - [ ] Actionable requirement 2
  - [ ] Verification command passes (e.g., `python3 -m unittest test.path.test_mod -v`)
```

---

## Tasks — Milestone v0.5.0 (`[MS-0.5.0]`)

### [TASK-M050-001] Extract Invocation Domain Model to Pure Domain Package
- **Milestone**: `[MS-0.5.0]`
- **Subsystem**: `vanguard/packages/domain`
- **Spec Anchor**: [04_vanguard_core_contracts_and_wire_schema_v040.md](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md)
- **Assignee Tag**: `[AI-READY]`
- **Status**: `[TODO]`
- **Dependencies**: None
- **Definition of Done (DoD)**:
  - [ ] Move `Invocation` schemas into pure domain without runtime imports.
  - [ ] `python3 -m unittest test.domain.test_invocation` passes.
  - [ ] `python3 tools/check_boundaries.py` passes.

---

### [TASK-M050-002] Deprecate Static DAG Coding Coordinator
- **Milestone**: `[MS-0.5.0]`
- **Subsystem**: `vanguard/packages/runtime`
- **Spec Anchor**: [03_vanguard_architecture_planes_and_execution_model_v040.md](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/03_vanguard_architecture_planes_and_execution_model_v040.md)
- **Assignee Tag**: `[AI-READY]`
- **Status**: `[TODO]`
- **Dependencies**: `[TASK-M050-001]`
- **Definition of Done (DoD)**:
  - [ ] Replace hardcoded DAG phase loop with direct invocation of `agency/episode/engine.py`.
  - [ ] Core integration tests pass without coordinator phase state errors.

---

### [TASK-M050-003] Rotate Provider API Credentials
- **Milestone**: `[MS-0.5.0]`
- **Subsystem**: Environment / Security
- **Spec Anchor**: [AGENTS.md](file:///home/rocha/Coding/Aether-D-System/AGENTS.md)
- **Assignee Tag**: `[HUMAN-ONLY]`
- **Status**: `[TODO]`
- **Dependencies**: None
- **Definition of Done (DoD)**:
  - [ ] Human Tech Lead updates provider keys in local `.env`.
