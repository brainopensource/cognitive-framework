# Problem: Distributed Two-Phase Commit (2PC) Engine & Crash Recovery (Tier 9)

Implement a robust Two-Phase Commit (2PC) transaction engine with coordinator WAL recovery, participant timeouts, and atomic abort cascades.

### Requirements:
1. `TwoPhaseCoordinator.execute_tx(tx_id, operations, participants)`:
   - Phase 1 (Prepare): Solicit vote from all participants. If ANY participant votes NO or times out, coordinator logs `ABORT` and instructs all to abort.
   - Phase 2 (Commit): If ALL participants vote YES, coordinator logs `COMMIT` and instructs all to commit.
2. Participant must lock resources during `prepare()` and hold locks until `commit()` or `abort()`.
3. Crash Recovery: `Coordinator.recover_from_wal(wal_records)` must replay incomplete transactions and resolve pending states to achieve consensus consistency across participants.
