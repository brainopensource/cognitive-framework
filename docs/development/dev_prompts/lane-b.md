# Developer Prompt — Lane SB: Senior Developer B

**Role:** Senior Systems Developer B (Security & Evaluator Isolation)  
**Branch:** `sprint5-6/integration`  
**Base:** `main` (Sprint 0–4 merged at `v0.4.0-sprint4`)  
**Assigned Packet:** [`docs/sprint5/sb-packet.md`](../../sprint5/sb-packet.md)  
**Contract Row:** [`REQ-EVAL-001`](../../sprint0/active-mvp-contract.json)  
**Your Target Code:** `vanguard/packages/adapters/evaluators/`

---

## 1. Goal
Implement the **OS-Isolated Exterior Evaluator Daemon** (`vanguard/packages/adapters/evaluators/isolated.py`) with the **Double Probe Protocol** (immutability + non-pollution).

---

## 2. Mandatory Reading Before Writing Code
Read these exact files in order:
1. [`docs/v4/05_vanguard_kernel_capabilities_and_security_v040.md`](../../v4/05_vanguard_kernel_capabilities_and_security_v040.md) — §2.1 Dual Ingress (`Principal::EvidencePlane`), §6 Sandbox & Perimeter.
2. [`docs/v4/01_vanguard_engineering_handbook_v040.md`](../../v4/01_vanguard_engineering_handbook_v040.md) — Mental Model M5 (The verifier is outside everything).
3. [`docs/sprint5/sb-packet.md`](../../sprint5/sb-packet.md) — Double probe protocol and `inconclusive` failure states.
4. [`docs/sprint0/system-architecture-icd.md`](../../sprint0/system-architecture-icd.md) — `EvaluatorPort` interface definition.
5. [`vanguard/packages/ports/evaluator.py`](../../../vanguard/packages/ports/evaluator.py) — Port contract.

---

## 3. Strict Invariants (DO NOT DRIFT)
* **Exteriority:** The episode engine holds ZERO evaluation authority. The evaluator daemon is triggered strictly by observing terminal ledger events across an OS boundary.
* **Double Probes:**
  - Probe 1: Pre-registered sha256 digest check over test oracle files. Any modification $\to$ `EvaluationTampered` fail closed.
  - Probe 2: Scan for untracked monkey-patches in the workspace. Any pollution $\to$ fail closed.
* **Fail-Closed Uncertainty:** Instrument crashes or socket timeouts MUST return `inconclusive`, NEVER a fabricated pass.
* **First Failing Test:** Write `test/adapters/test_isolated_evaluator.py` and prove failure before implementing the adapter.

---

## 4. Verification Gate
```bash
python3 -m unittest test.adapters.test_isolated_evaluator
python3 tools/check_boundaries.py
python3 tools/run_broken_tests.py
```
Push only to `sprint5-6/integration` with commit message format: `[dev-sb] S5-SB-001: <reason naming REQ-EVAL-001>`.
