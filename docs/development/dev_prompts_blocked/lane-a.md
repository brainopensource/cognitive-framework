# Developer Prompt — Lane SA: Lead Architect / Tech Lead (Sprint 6)

**Role:** Lead Software Architect, Tech Lead, Senior Developer A  
**Branch:** `sprint5-6/integration`  
**Base:** Sprint 5 merged cleanly on `sprint5-6/integration`  
**Assigned Packet:** [`docs/sprint6/sa-packet.md`](../../sprint6/sa-packet.md)  
**Contract Row:** [`REQ-DOG-001`](../../sprint0/active-mvp-contract.json)  
**Your Target Code:** `vanguard/packages/runtime/root.py`

---

## 1. Goal
Implement the **Runtime Composition Root** (`vanguard/packages/runtime/root.py`) assembling all ports, kernel, and agency loop into the `Runtime.execute_harness()` entrypoint.

Execute the **Beta Dogfood Milestone Gate** solving a real single-file bug end-to-end with zero human code edits.

---

## 2. Mandatory Reading Before Writing Code
Read these exact files in order:
1. [`docs/v4/13_C_gts_mvp_program_and_engineering_plan.md`](../../v4/13_C_gts_mvp_program_and_engineering_plan.md) — Chapter 10 Gate Q1+Q2.
2. [`docs/v4/09_vanguard_decision_register_v040.md`](../../v4/09_vanguard_decision_register_v040.md) — ADR-0057, ADR-0058.
3. [`docs/sprint6/sa-packet.md`](../../sprint6/sa-packet.md) — Composition root contract and dogfood requirements.
4. [`docs/sprint0/active-mvp-contract.json`](../../sprint0/active-mvp-contract.json) — `REQ-DOG-001`.
5. [`vanguard/packages/agency/episode/engine.py`](../../../vanguard/packages/agency/episode/engine.py) & [`vanguard/packages/runtime/governance/engine.py`](../../../vanguard/packages/runtime/governance/engine.py).

---

## 3. Strict Invariants (DO NOT DRIFT)
* **Zero Cognitive Identifiers:** No `plan`, `reflect`, `debug` in symbol names.
* **Pure Declarative Composition:** Wire concrete adapters dynamically from `HarnessManifest`. Zero hardcoded business logic in `root.py`.
* **Dogfood Gate:** Prove that the agent diagnoses, patches, requests approval, and passes tests on a real external test repository.

---

## 4. Verification Gate
```bash
python3 -m unittest test.runtime.test_composition_root
python3 tools/check_boundaries.py
python3 tools/check_active_mvp_contract.py
```
Push with commit message format: `[dev-sa] S6-SA-001: <reason naming REQ-DOG-001>`.
