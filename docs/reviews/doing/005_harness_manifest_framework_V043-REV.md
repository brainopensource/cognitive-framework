# 005 — Active Harness Manifest Requirements (v0.5.0 Rewrite Baseline)

> **Status**: SIMPLIFIED ACTIVE ARCHITECTURAL DIRECTIVES
> **Last Audit**: 2026-08-17

---

## Active Architectural Requirements for v0.5.0

### [MAN-01] Eliminate Decorative Manifest Fields & Enforce Composition Consumption
- **Severity**: High
- **Subsystem**: `vanguard/packages/agency/manifests/` & `runtime/root.py`
- **Spec Anchor**: `VG-02 C-01` / `FT-10`
- **Current Defect**: `context_policy.json` and `routing_policy.json` are read into composition digests but never consumed by execution components (`ContextCompiler` or model router).
- **v0.5.0 Requirement**: Ensure every field declared in a harness manifest pack (`context_policy`, `routing_policy`, `budget_policy`) is explicitly consumed by a runtime component or reject the manifest at composition time.

### [MAN-02] Expand Manifest Schema to Express Harness Variance Dimensions
- **Severity**: High
- **Subsystem**: `vanguard/packages/domain/artifacts/manifest.py` & `schemas/v4/`
- **Spec Anchor**: `VG-02 C-01` / `C-02`
- **Current Defect**: Manifest packs currently differ only by system prompt and tool alias names. Core variance dimensions (permission threshold, compaction strategy, sub-agent topology, retry policy) cannot be expressed in configuration.
- **v0.5.0 Requirement**: Extend manifest schemas to support declarative configuration of compaction strategies, permission threshold allowlists, and sub-agent spawn capabilities.
