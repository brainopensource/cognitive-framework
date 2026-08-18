# 003 — Active Architecture & Recursion Requirements (v0.5.0 Rewrite Baseline)

> **Status**: SIMPLIFIED ACTIVE ARCHITECTURAL DIRECTIVES
> **Last Audit**: 2026-08-17

---

## Active Architectural Requirements for v0.5.0

### [REC-01] Implement Recursive Sub-Agent Spawning in `EpisodeEngine`
- **Severity**: Critical
- **Subsystem**: `vanguard/packages/agency/episode/engine.py`
- **Spec Anchor**: `VG-03 §5.2` / `GTS-13C §4.3`
- **Current Defect**: `EpisodeEngine` is restricted to depth-1 non-recursive execution. Child episode context isolation and parent/child spawn delegation are not wired into the episode engine loop.
- **v0.5.0 Requirement**: Support recursive episode spawning (`spawn` primitive) with context window isolation (child exploration remains isolated, returning only result receipt to parent).

### [RT-01] Wire Model Router Adapter to Model Selection
- **Severity**: High
- **Subsystem**: `vanguard/packages/adapters/models/routing.py`
- **Spec Anchor**: `VG-03 §10.4`
- **Current Defect**: `adapters/models/routing.py` (107 LOC) exists but is unwired in the model selection and runtime engine.
- **v0.5.0 Requirement**: Wire `routing.py` to handle tier escalation and dynamic model selection driven by harness manifests.
