# Emergent DAGs Concept & Runtime Decoupling Directives

> **Status**: Reference Document for Workflow Evolution & Decoupling
> **Scope**: Moving from hardcoded static DAGs to emergent playbooks and clean harness isolation.

---

## 1. The Emergent DAGs Philosophy (Proteins & Polymers)

- **Anti-Pattern**: Hardcoding a rigid `PLAN -> EXECUTE -> VERIFY` state machine into runtime code.
- **Target Model**: Workflows (DAGs) should be **emergent from practice** — battle-tested sequences of atomic episode actions compiled into reusable playbooks.
- **Rigidity Dial**:
  - `advisory`: Agent receives playbook steps as suggestions, looping freely.
  - `guided`: Agent follows phases in order, but chooses internal turn actions freely.
  - `strict`: Deterministic dependency graph execution for fixed compliance tasks.

---

## 2. Runtime Decoupling Directives for v0.5.0+

1. **Framework vs. Application Boundary**:
   - `runtime/` should only contain composition root and session lifecycle (`root.py`, `HarnessSession`).
   - Coding-specific logic (`coding_plan.py`, `coding_progress.py`, `coding_budget.py`) belongs in harness packs or pure domain/ports.

2. **Consolidate Duplicate Engines**:
   - Merge the 3 model selection paths (`model_selection.py`, `tier_escalation.py`, `coding_coordinator.py`) into one clean policy.
   - Move test doubles (`_fake_backend()`) from `coding_entrypoint.py` to `test/`.