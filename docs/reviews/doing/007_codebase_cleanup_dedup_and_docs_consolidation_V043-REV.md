# 007 — Active Cleanup & Deduplication Directives (v0.5.0 Rewrite Baseline)

> **Status**: SIMPLIFIED ACTIVE ARCHITECTURAL DIRECTIVES
> **Last Audit**: 2026-08-17

---

## Active Cleanup & Deduplication Tasks for v0.5.0

### [CLN-01] Delete Orphan File `workflow_visualizer.html`
- **Severity**: Medium
- **Target File**: `workflow_visualizer.html` (48 KB in workspace root)
- **Spec Anchor**: `VG-03 §2.3` / `ADR-0003`
- **Current Defect**: Orphan file from rejected static DAG runtime visualizer. Trajectory rendering belongs post-hoc in the inspector over ledger events.
- **Action Required**: Remove `workflow_visualizer.html` from repository root.

### [CLN-02] Deduplicate Unified-Diff Parsers into Pure Domain Module
- **Severity**: High
- **Subsystem**: `vanguard/packages/domain/patch/` & `adapters/environment/`
- **Spec Anchor**: `VG-03 §7.4` / `FT-08`
- **Current Defect**: Three parallel diff parsers exist in `adapters/environment/fake.py`, `git.py`, and `sandboxed.py` (~1,400 LOC total), risking parser behavior divergence between fake and real environments.
- **v0.5.0 Requirement**: Create pure domain module `domain/patch/unified_diff.py` with property tests, and refactor all environment adapters to use it.

### [SEC-01] Purge Reachable `.env` Secret Blob from Git History
- **Severity**: High
- **Subsystem**: Repository History / Security
- **Spec Anchor**: `VG-01` / `scan_secrets.py`
- **Current Defect**: `python3 tools/scan_secrets.py --all-refs` fails due to historical reachable `.env` commit blob.
- **Action Required**: Clean git history to purge historical `.env` blob from all refs.
