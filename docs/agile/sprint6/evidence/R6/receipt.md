# Gate R6 Evidence Receipt — Recovery Engine & Ledger-Only Replay

**Date:** 2026-08-15  
**Gate:** R6 (Recovery Engine & Ledger-Only Replay)  
**Status:** PASS  
**Authority:** `docs/phases_0-2_review_full_rev2.md` §14, `ADR-0059`  

---

## 1. Ledger Replay & Recovery Verification
- **Target Components:** `vanguard.packages.runtime.ledger.recovery`, `vanguard.packages.domain.ledger.events`
- **Unit Suite:** `python3 -m unittest test.runtime.test_recovery`
- **Invariants Verified:**
  - Full state recovery reconstructed strictly from persisted `SqliteEventStore` event stream.
  - Zero LLM invocation required to resume a suspended run once approval is signed.
  - UUIDv7 monotonic ordering preserved across all envelopes and recovery events.
  - Idempotent replay: re-running recovery over completed runs does not duplicate effects.

## 2. Verdict
Recovery engine successfully resumes from crash/suspension without model calls, driven purely by durable ledger state.
