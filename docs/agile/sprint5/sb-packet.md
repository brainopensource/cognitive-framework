# Lane SB Developer Packet — OS-Isolated Evaluator with Double Probes

**Assignee:** Senior Developer B  
**Tickets:** `S5-SB-001`, `S5-SB-002`  
**Complexity:** Level 4 / 5 (Gate Component)  
**Contract Row:** [`REQ-EVAL-001`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json)  
**Owned Code:** `vanguard/packages/adapters/evaluators/isolated.py`  
**Target Test:** `test/adapters/test_isolated_evaluator.py`

---

## 1. Scope & Objective
Implement the exterior, OS-isolated evaluator adapter implementing `EvaluatorPort`.

The evaluator runs outside the worker sandbox, in a dedicated OS process under a distinct non-root identity (`UID 10002`) with an immutable container/image digest.

---

## 2. Invariants & Rules
1. **The Double Probe Protocol:**
   - **Probe 1 (Immutability Probe):** Before running the test runner, verify that all test oracle files match their pre-registered sha256 digests. If the agent modified the test file, reject the run immediately (`EvaluationTampered`).
   - **Probe 2 (Non-Pollution Probe):** Scan the workspace for untracked monkey-patches (e.g. `conftest.py`, `.pth` files, altered site-packages). If found, fail closed.
2. **Fail-Closed on Instrument Errors:** If the runner times out, drops socket, or crashes, emit `EvaluationInconclusive` with status `inconclusive`. Never convert an unconfirmed execution into a test pass.
3. **Exteriority:** The episode loop has zero authority to invoke this module. The evaluator is triggered strictly by ledger observation.

---

## 3. First Failing Test & Verification
```bash
python3 -m unittest test.adapters.test_isolated_evaluator
python3 tools/check_boundaries.py
python3 tools/run_broken_tests.py
```
Must prove: Modified test oracle fails closed; dropped socket returns `inconclusive`; genuine fix returns `passed`.
