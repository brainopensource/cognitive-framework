# Gate R9 Evidence Receipt — Dogfood Validation

**Date:** 2026-08-15  
**Gate:** R9 (Dogfood Validation)  
**Status:** PASS  
**Authority:** `docs/phases_0-2_review_full_rev2.md` §14, `REQ-DOG-001`  

---

## 1. Preregistered Task Configuration
- **Defect Description:** `slugify.py` boundary length truncation bug causing trailing hyphens and dropped valid characters.
- **Repository Structure:** Real git repository with `slugify.py` and unit test `test_slugify.py`.
- **Pre-Run State:** `python3 -m unittest discover -s <repo>` fails 100% before run.
- **Sole Product Path Executed:**
  `vg / Runtime -> RuntimeService -> ContextCompiler -> streaming ModelPort -> Kernel S0-S12 -> rootless sandbox -> externally signed approval -> ledger-only resume -> terminal event -> exterior evaluator -> CLI`

## 2. Three-Run Validation Summary
| Run Index | Terminal Status | Event Count | External Signature Verified | Evaluator Verdict | Post-Run Test Suite |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Run #1** | `completed` | 11 | `a2f25a7a3fe76a9d9710c51a44a2e214225d7c5a466432d50176a4a21d246a48` | `claims` (passed) | 4/4 passed (0.000s) |
| **Run #2** | `completed` | 11 | `6256f1f44e13ea7db4b1dc71333cb92b3a98ea4d1fe090151dbf3dfa91b427b3` | `claims` (passed) | 4/4 passed (0.000s) |
| **Run #3** | `completed` | 11 | `eb7fe44a954497e2da6eb009e4a362bf7ba9f8e5812239d564fbe3971e4eb4d0` | `claims` (passed) | 4/4 passed (0.000s) |

## 3. Invariants & Zero Human Source Edits
- **Zero Human Source Code Edits:** All source changes applied strictly through the runtime `Kernel.dispatch` via `patch.apply` after external HMAC approval.
- **External Approval Signature:** Descriptor digest bound to external cryptographic key.
- **Ledger Replay:** 11 events persisted per run to SQLite store, including `CompetencePriorRecorded`, `ProposalProduced`, `ApprovalRequested`, `ApprovalResolved`, `EffectStarted`, and `RunTerminated`.
- **Sealed Bundle:** Complete raw execution records sealed under `docs/sprint6/evidence/R9/dogfood_bundle.json`.

## 4. Verdict
Gate R9 PASSED. The sole product path is proven functional, reproducible, and trustworthy.
