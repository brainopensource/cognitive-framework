# Technical Debt Record ARCH-02 — Runtime Bindings & Governance Consolidation

**ID:** DEBT-ARCH-02  
**Recorded By:** Tech Lead Senior  
**Target Milestone:** GA / Q4  
**Authority:** `docs/phases_0-2_review_full_rev2.md` §14  

---

## 1. Description of Technical Debt

### A. Static `DEFAULT_BINDINGS` in Composition Root (`runtime/root.py`)
- **Current State:** `Runtime.compose()` uses a fallback dictionary `DEFAULT_BINDINGS` mapping adapter names (`"fs.read"`, `"patch.apply"`, `"proc.exec"`) to concrete adapter factory functions when not explicitly injected.
- **Risk / Limitation:** While convenient for default CLI usage and test ergonomics, static fallback maps risk coupling the composition root to specific adapter implementations instead of pure dynamic dependency injection.
- **Remediation Plan for GA/Q4:** Move adapter registry to a pluggable manifest-driven discovery mechanism where adapters declare their exported capability verbs in `adapter.json` manifests, removing any hardcoded binding dictionaries from `root.py`.

### B. Dual `ProcessEngine` / `ApprovalFlow` Coordination
- **Current State:** Approval suspensions are coordinated across both `ProcessEngine` (which tracks state machine suspension transitions) and `ApprovalFlow` (which manages cryptographic HMAC challenge-decision verification).
- **Risk / Limitation:** The two-stage suspension handshake requires careful state synchronization between process lifecycle and approval authority.
- **Remediation Plan for GA/Q4:** Consolidate approval suspension states directly into a unified capability suspension state machine inside the kernel/runtime bridge, providing a single durable transaction boundary for all privileged human-in-the-loop interactions.
