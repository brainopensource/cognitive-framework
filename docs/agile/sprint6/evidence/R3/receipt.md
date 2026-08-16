# Gate R3 Evidence Receipt — Harness & Adversarial Failure Discipline

**Date:** 2026-08-15  
**Gate:** R3 (Harness & Adversarial Failure Discipline)  
**Status:** PASS  
**Authority:** `docs/phases_0-2_review_full_rev2.md` §9.1, §14  

---

## 1. Adversarial Test Matrix Execution
- **Runner:** `python3 tools/run_broken_tests.py`
- **Total Registered Broken Counterparts:** 26
- **Results Summary:** 26 / 26 broken counterparts observed failing with exact expected failure signatures; 26 / 26 reference controls exit 0.

## 2. Test Cases Breakdown
- `MF-S0-001` through `MF-S0-009`: Step invariants and state transitions.
- `MF-KRN-001` through `MF-KRN-011`: Kernel grant attenuations, policy boundaries, and budget checks.
- `MF-S4-001`: Disposable presence check on S4 exit.
- `MF-GOV-001`: Tampered approval descriptor detection.
- `MF-CTX-001`: Compiled context bypass rejection.
- `MF-CTX-002`: Tool observation absence on turn 2 rejection.
- `MF-SEC-002`: Secret in envelope rejection.
- `MF-TEL-001`: Synthetic timing in live report rejection.

## 3. Verdict
BROKEN HARNESS PASS: 26 broken counterparts observed failing.
