# Gate R4 Evidence Receipt — Rootless Sandbox & Privilege Attenuation

**Date:** 2026-08-15  
**Gate:** R4 (Rootless Sandbox & Privilege Attenuation)  
**Status:** PASS  
**Authority:** `docs/phases_0-2_review_full_rev2.md` §14, `ADR-0056`  

---

## 1. Sandbox Verification
- **Target Components:** `vanguard.packages.adapters.sandbox.rootless`, `vanguard.packages.kernel.attenuation`
- **Unit Suite:** `python3 -m unittest test.adapters.test_rootless_sandbox`
- **Test Results:**
  - Double-probe immutability check passed.
  - Mount/unmount lifecycle overhead accounted in ms.
  - Privilege attenuation enforced (unprivileged uid/gid mapping, no ambient root, restricted path namespace).
  - Path traversal and outside-workspace symlink attacks rejected fail-closed.

## 2. Verdict
The rootless sandbox provides strict execution boundary isolation with full double-probe state verification.
