# 000 — Index & Active Task Summary (v0.4.3 Reconciliation)

> **Status**: SIMPLIFIED ACTIVE WORKLIST
> **Last Audit**: 2026-08-17

---

## Active Findings & Pending Tasks

### [SEC-01] Git History Secret Cleanup
- **Severity**: High
- **Description**: Secret scanner passes on `HEAD`, but fails when scanning reachable git history.
- **Evidence**: `python3 tools/scan_secrets.py --all-refs` returns `SECRET SCAN FAIL: reachable-object: env-named blob .env`.
- **Action Required**: Purge historical `.env` blob from reachable git refs/history.

### [M-18] Wire Telemetry Instrument Tuple
- **Severity**: High
- **Description**: The instrument tuple in `tools/telemetry/tuple.py` exists but is unwired in runtime execution paths.
- **Evidence**: `tools/telemetry/tuple.py` is present, but no runner in `vanguard/packages/runtime/` emits it.
- **Action Required**: Wire `tuple.py` emission into runtime session execution.
