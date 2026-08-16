# Lane SB Developer Packet — Descriptor-Bound Human Approvals

**Assignee:** Senior Developer B  
**Tickets:** `S6-SB-001`  
**Complexity:** Level 4 / 5 (Gate Component)  
**Contract Row:** [`REQ-APP-001`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json)  
**Owned Code:** `vanguard/packages/runtime/governance/`  
**Target Test:** `test/runtime/test_approval_flow.py`

---

## 1. Scope & Objective
Implement the descriptor-bound human approval lifecycle in `vanguard/packages/runtime/governance/`.

When a proposal verb is `fs.patch` (Sink Class: `privileged`), `Kernel.dispatch` triggers state `ApprovalRequested` (Failure path `F-08`). The process engine extracts the normalized unified diff, computes `argsDigest`, renders the diff payload to the client, and waits for a signed `ApprovalDecision`.

---

## 2. Invariants & Rules
1. **Descriptor Binding:** The approval signature binds the exact `argsDigest` of the unified diff. If an attacker or corrupted process tampers with the diff between approval and application, dispatch fails closed (`MF-GOV-001`).
2. **Deterministic Resumption:** The approval engine resumes purely from ledger state without invoking an LLM.
3. **No Unsigned Privileged Effects:** Privileged sinks can never execute without a valid, unexpired, descriptor-bound grant.

---

## 3. Verification Gate
```bash
python3 -m unittest test.runtime.test_approval_flow
python3 tools/check_boundaries.py
python3 tools/run_broken_tests.py
```
Must prove: Tampered unified diff fails closed (`MF-GOV-001`); signed grant resumes S9 dispatch cleanly.
