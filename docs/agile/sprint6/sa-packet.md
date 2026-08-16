# Lane SA Developer Packet — Runtime Composition Root & Dogfood Milestone Gate

**Assignee:** Lead Software Architect / Principal Tech Lead  
**Tickets:** `S6-SA-001`, `S6-SA-002`  
**Complexity:** Level 5 / 5 (Final Gate Component)  
**Contract Row:** [`REQ-DOG-001`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json)  
**Owned Code:** `vanguard/packages/runtime/root.py`  
**Target Test:** `test/runtime/test_composition_root.py`

---

## 1. Scope & Objective
Implement the top-level **Runtime Composition Root** (`vanguard/packages/runtime/root.py`) providing the universal programmatic entry point:
```python
class Runtime:
    @classmethod
    def execute_harness(
        cls,
        manifest_path: str | Path,
        task_context: TaskContext,
        interactive: bool = True
    ) -> RunResult:
        ...
```
Wire concrete adapters (`OpenRouterModelAdapter`, `GitEnvironmentAdapter`, `RootlessSandboxRunner`, `ExteriorEvaluator`, `EventStoreSQLite`).

Execute the **Beta Dogfood Milestone Gate**: End-to-end diagnosis, patch generation, human approval, patch application, and isolated verification of a real single-file bug in an external test repository.

---

## 2. Invariants & Rules
1. **Zero Cognitive Identifiers:** No `plan`, `reflect`, `debug` in symbol names.
2. **Immutable Dependency Lattice:** `runtime/` depends on `domain`, `ports`, `kernel`, `agency`, and dynamically wires `adapters/`.
3. **Pure Composition:** Manifest configuration alone controls tool sets and system prompts. Zero hardcoded business logic.

---

## 3. Verification Gate
```bash
python3 -m unittest test.runtime.test_composition_root
python3 tools/check_boundaries.py
python3 tools/check_active_mvp_contract.py
```
Must prove: Complete end-to-end task execution succeeds without manual intervention; all events persisted to ledger.
