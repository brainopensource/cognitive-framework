# 001 — Active Architectural Directives (v0.5.0 Rewrite Baseline)

> **Status**: SIMPLIFIED ACTIVE ARCHITECTURAL DIRECTIVES
> **Last Audit**: 2026-08-17

---

## Active Architectural Requirements for v0.5.0

### [C-3] Implement Competence ($G_C$) and Evidence ($G_E$) Graphs
- **Severity**: Critical
- **Subsystem**: `vanguard/packages/domain/` & `agency/`
- **Spec Anchor**: `VG-02 §1`
- **Current Defect**: `Claim` exists as a JSON schema, but $G_C$ (competence graph) and $G_E$ (evidence graph) Python data structures and storage drivers do not exist.
- **v0.5.0 Requirement**: Implement immutable $G_C$ and $G_E$ graph nodes, edges, lineage, and supersession in `domain/` and `agency/`.

### [H-1] Enforce Composition-Time Alias Validation in Manifest Loader
- **Severity**: High
- **Subsystem**: `vanguard/packages/agency/manifests/loader.py`
- **Spec Anchor**: `VG-03 §5.3` / `N-17`
- **Current Defect**: `loader.py` falls back to identity (`to_canonical`) on unknown tool names, failing silently at runtime instead of failing at composition time.
- **v0.5.0 Requirement**: Enforce strict tool alias validation during manifest loading so invalid tool aliases fail fast at composition time.

### [H-2] Wire Context Policy in Manifest to ContextCompiler
- **Severity**: High
- **Subsystem**: `vanguard/packages/agency/context/compiler.py`
- **Spec Anchor**: `VG-03 §4`
- **Current Defect**: `context_policy.json` (e.g. `recency-window`) is hashed into the manifest digest but ignored by `ContextCompiler`.
- **v0.5.0 Requirement**: Wire `context_policy` parameters directly into `ContextCompiler` strategy selection.
