# Developer Prompt — Lane SB: Senior Developer B (Sprint 6)

**Role:** Senior Systems Developer B (Governance & Approvals)  
**Branch:** `sprint5-6/integration`  
**Base:** Sprint 5 merged cleanly on `sprint5-6/integration`  
**Assigned Packet:** [`docs/sprint6/sb-packet.md`](../../sprint6/sb-packet.md)  
**Contract Row:** [`REQ-APP-001`](../../sprint0/active-mvp-contract.json)  
**Your Target Code:** `vanguard/packages/runtime/governance/`

---

## 1. Goal
Implement the **Descriptor-Bound Human Approval Flow** in `vanguard/packages/runtime/governance/`.

Extract unified diffs on privileged `fs.patch` requests, verify human signatures against exact `argsDigest`, and enforce fail-closed tampering checks (`MF-GOV-001`).

---

## 2. Mandatory Reading Before Writing Code
Read these exact files in order:
1. [`docs/v4/05_vanguard_kernel_capabilities_and_security_v040.md`](../../v4/05_vanguard_kernel_capabilities_and_security_v040.md) — §2.3 Failure path `F-08`, §2.5 Suspension.
2. [`docs/sprint6/sb-packet.md`](../../sprint6/sb-packet.md) — Unified diff extraction and `argsDigest` signature rules.
3. [`docs/sprint0/active-mvp-contract.json`](../../sprint0/active-mvp-contract.json) — `REQ-APP-001`.
4. [`vanguard/packages/kernel/dispatch.py`](../../../vanguard/packages/kernel/dispatch.py) — Stage S5/S6 grant issuance.

---

## 3. Strict Invariants (DO NOT DRIFT)
* **Descriptor Binding:** Approval MUST bind the exact `argsDigest` of the unified diff. Tampered diffs fail closed (`MF-GOV-001`).
* **Model-Free Resumption:** Process engine resumes purely from ledger state without calling an LLM.
* **Write test first:** Prove tampered diff fails before implementing verification logic.

---

## 4. Verification Gate
```bash
python3 -m unittest test.runtime.test_approval_flow
python3 tools/check_boundaries.py
python3 tools/run_broken_tests.py
```
Push with commit message format: `[dev-sb] S6-SB-001: <reason naming REQ-APP-001>`.
