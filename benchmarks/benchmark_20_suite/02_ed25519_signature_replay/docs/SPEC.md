# Specification: Ed25519 Approval Anti-Replay Verification (SEC-02)

The `ApprovalVerifier` MUST satisfy two anti-replay security invariants:
1. **Timestamp Freshness**: `abs(current_time - timestamp) <= max_drift_seconds`. Any request outside this window MUST be rejected.
2. **Nonce Uniqueness**: Every accepted `nonce` MUST be recorded in `self.seen_nonces`. Any repeated `nonce` MUST be rejected immediately.
