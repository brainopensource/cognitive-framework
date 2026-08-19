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
# 004 — Active Cognition & Evidence Requirements (v0.5.0 Rewrite Baseline)

> **Status**: SIMPLIFIED ACTIVE ARCHITECTURAL DIRECTIVES
> **Last Audit**: 2026-08-17

---

## Active Architectural Requirements for v0.5.0

### [GE-01] Implement Minimum Viable Evidence Graph ($G_E$) Dataclasses
- **Severity**: High
- **Subsystem**: `vanguard/packages/domain/evidence/`
- **Spec Anchor**: `VG-02 §1` / `T4.11`
- **Current Defect**: `Claim` exists only as a JSON schema (`schemas/v4/evidence-claim.schema.json`). Pure domain Python types, evaluation protocol references, and invalidation condition data structures do not exist in `domain/`.
- **v0.5.0 Requirement**: Create `domain/evidence/claim.py` declaring immutable `Claim` dataclasses with `subject`, `predicate`, `protocol`, `evaluator`, `uncertainty`, and `invalidation_conditions`.

### [AA-01] Establish A/A Benchmark Floor Runner
- **Severity**: High
- **Subsystem**: `vanguard/packages/runtime/` & `lab/`
- **Spec Anchor**: `VG-02 §8` / `O-01`
- **Current Defect**: The A/A benchmark floor does not exist, blocking the trigger for `O-01` (derived competence lifecycle).
- **v0.5.0 Requirement**: Build a refusing A/A benchmark floor runner that verifies null-lift baseline variance before registering competence claims.
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
# 010 — Active ACI Harvest Requirements (v0.5.0 Rewrite Baseline)

> **Status**: SIMPLIFIED ACTIVE ARCHITECTURAL DIRECTIVES
> **Last Audit**: 2026-08-17

---

## Active ACI Harvest Directives for v0.5.0

### [ACI-1] Paginated `fs.read` Tool & Adapter
- **Severity**: High
- **Subsystem**: `vanguard/packages/adapters/` & `schemas/v4/`
- **Spec Anchor**: `VG-03 §7.4`
- **v0.5.0 Requirement**: Implement 100-line default pagination with offset parameter on `fs.read` tool adapter and schema to prevent context dump-and-drown.

### [ACI-2] Succinct `fs.search` File-First Output
- **Severity**: Medium
- **Subsystem**: `vanguard/packages/adapters/`
- **Spec Anchor**: `VG-03 §7.4`
- **v0.5.0 Requirement**: Cap `fs.search` observation receipts to file matches first with snippet truncations.

### [ACI-3] Empty-Output Acknowledgment on `proc.exec`
- **Severity**: Low
- **Subsystem**: `vanguard/packages/adapters/`
- **Spec Anchor**: `VG-03 §7.4`
- **v0.5.0 Requirement**: Emit explicit `[Command executed with exit code 0 and empty stdout]` receipt text on `proc.exec` to prevent model looping on silent execution.

### [ACI-4] Lint-on-Patch Receipt Observation
- **Severity**: Medium
- **Subsystem**: `vanguard/packages/adapters/`
- **Spec Anchor**: `VG-03 §7.4` / `A-05`
- **v0.5.0 Requirement**: Run fast syntax linter on file patches and return syntax errors as observation receipts to the agent without triggering the evaluator.
