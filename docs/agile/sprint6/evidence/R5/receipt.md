# Gate R5 Evidence Receipt — External Approvals & Descriptor Binding

**Date:** 2026-08-15  
**Gate:** R5 (External Approvals & Descriptor Binding)  
**Status:** PASS  
**Authority:** `docs/phases_0-2_review_full_rev2.md` §14, `ADR-0057`, `ADR-0058`  

---

## 1. Approval Subsystem Verification
- **Target Components:** `vanguard.packages.runtime.governance.approvals`
- **Unit Suite:** `python3 -m unittest test.governance.test_approval_flow`
- **Invariants Verified:**
  - HMAC/SHA256 signature binds the exact descriptor digest of the requested diff.
  - An approval for diff A cannot authorize diff B (fail-closed).
  - Suspended approval states survive process restart via durable ledger replay.
  - Absent or timed-out approvers fail closed to escalation, not automatic grant.

## 2. Verdict
External signature approval mechanism strictly binds the authorized descriptor and prevents any unauthorized privilege escalation.
