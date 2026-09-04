# Electroweak v0.9.2 → Living Execution Runway Transition Blueprint
**Authority**: Planning & Staging Resource (`.draft/`)  
**Target Runway**: [`docs/execution/`](../docs/execution/) (`milestones.md`, `backlog.md`, `spec.md`, `technical.md`, `tasks.md`)  
**Source Corpus**: `docs/reports/reviews/electroweak_v092/` (`grok/`, `opus/`, `octopus/`, `gpt/`)  
**Date**: 2026-09-04  

---

## Executive Architectural Strategy: The 2-Step Funnel

### Why the 2-Step Approach is Mandatory
Attempting to jump straight from unstructured review dossiers into low-level code or granular tasks creates **severe hallucination, merge thrashing, and scope creep**.

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: HIGH-LEVEL ARCHITECTURAL LOCK (COMPLETED VIA GEMINI & OPUS)        │
│ - Resolve core conflicts (fuzzy matching vs exact, L2 PPR vs L5, swarms)    │
│ - Formalize candidate capability packages (HAR-01, SET-01, EDT-01, etc.)    │
│ - Establish target milestone gates (MS-TRUTH, MS-SEE, MS-CHANGE, etc.)      │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP 2: SURGICAL TECHNICAL DETAILING & EXECUTION RUNWAY STAGING             │
│ - Prompt-by-prompt insertion of exact code recipes into technical.md        │
│ - Typed wire contracts and schema deltas into spec.md                       │
│ - Atomic task dependency trees into tasks.md                                │
│ - Strict TCB ceiling (<= 1438 LOC) & invariant enforcement audits           │
└─────────────────────────────────────────────────────────────────────────────┘
```

By completing **Step 1**, we have a locked consensus on what to adopt and what to reject.  
**Step 2** takes each adopted package and meticulously details its implementation inside `docs/execution/`.

Below are **11 modular, surgical prompts** ready to be fed one by one into Opus, Gemini, or any frontier coding agent to turn every review finding into concrete runway engineering truth.

---

## Modular Prompt Suite for `docs/execution/`

```text
Prompt Index:
  01. Backlog Inventory Registration & Reconciliation (backlog.md)
  02. Milestone Overlay Gates & Release Invariants (milestones.md)
  03. Technical Handbook & Spec for HAR-01: Harness & Tool Protocol Normalization (technical.md, spec.md)
  04. Technical Handbook & Spec for SET-01: Settlement Integrity & Tamper Shield (technical.md, spec.md)
  05. Technical Handbook & Spec for EDT-01: Atomic 2PC & AST Preflight Edit Primitive (technical.md, spec.md)
  06. Technical Handbook & Spec for IDX-01: Port-Backed LDA Repository Intelligence (technical.md, spec.md)
  07. Technical Handbook & Spec for Greenfield Oracle & Cache Telemetry (technical.md, spec.md)
  08. Technical Handbook & Spec for PRF-01: Product Presets & MS-CONTROL Baseline (technical.md, spec.md)
  09. Technical Handbook & Spec for DIR-01: Outer Director & Campaign Orchestration (technical.md, spec.md)
  10. Atomic Task Work-Tree Deconstruction (tasks.md)
  11. Constitutional Invariant, TCB Budget & Boundary Gate Audit (Runway Verification)
```

---

### Prompt 01: Backlog Inventory Registration & Reconciliation
* **Target File**: `docs/execution/backlog.md`
* **Goal**: Register packages `HAR-01`, `SET-01`, `EDT-01`, `IDX-01`, `PRF-01`, `DIR-01` into Section 2 of `backlog.md`, explicitly reconciling them with existing legacy task IDs (`T-04`, `T-18`, `T-20`, `T-26`, `OCT-*`, `CMX-*`).

```markdown
# ASSIGNMENT: Backlog Registration & Legacy Reconciliation
Target Document: `docs/execution/backlog.md`
Authority Tier: Execution Runway (Living Document)

Review the current package inventory in `docs/execution/backlog.md` alongside the approved Electroweak v0.9.2 synthesis.
Your task is to integrate the 6 new SOTA execution packages into Section 2 of `backlog.md`:
1. `HAR-01` (Tool Protocol & Profile Normalization) — Subsumes harness precondition fixes from Opus Defect A, C, E, K, L.
2. `SET-01` (Inner Settlement & Verification Integrity) — Subsumes T-04 (ADMISSION_GATE_EXEMPT removal), T-05 (tamper shield wiring), T-07, T-18 (implicated test verification), and greenfield stub-fail/impl-pass oracle.
3. `EDT-01` (Atomic 2PC & Syntax Preflight Edit Primitive) — Subsumes T-14, T-17, exact str_replace, 2PC transaction coordinator, and adapter AST preflight.
4. `IDX-01` (Port-Backed LDA Repository Intelligence) — Backs IndexPort with .lda/index.db, exposes L5 query tools, and enforces L1-L3 KV-cache prefix stability.
5. `PRF-01` (Product Preset Differentiation & Budget Passthrough) — Subsumes T-26, T-27, and replaces cosmetic aliases with real typed budgets (fast/balanced/max).
6. `DIR-01` (Outer-Loop Sequential & Campaign Director) — Stages OCT-01..11 into Wave 5 as a runtime client of EpisodeEngine.

REQUIREMENTS:
- For each package, provide: ID, Title, Subsystem, Lane (A or B), Status (APPROVED or PROPOSED), Target Milestone, Depends On, and Concrete Acceptance Falsifier.
- Explicitly add a "Legacy Reconciliation Matrix" explaining which existing T-* and OCT-* tickets are closed, subsumed, or superseded by these packages.
- Maintain strict markdown table formatting consistent with existing sections of `backlog.md`.
```

---

### Prompt 02: Milestone Overlay Gates & Release Invariants
* **Target File**: `docs/execution/milestones.md`
* **Goal**: Update the overlay gates (`MS-TRUTH`, `MS-SEE`, `MS-CHANGE`, `MS-CONTROL`, `MS-CAMPAIGN`) with exact exit predicates derived from the reviews.

```markdown
# ASSIGNMENT: Milestone Overlay Gates & Release Predicates
Target Document: `docs/execution/milestones.md`
Authority Tier: Execution Runway (Living Document)

Update Section 3 of `docs/execution/milestones.md` to incorporate the verified acceptance boundaries and release invariants from the Electroweak review synthesis:

1. `MS-TRUTH`:
   - Prerequisite packages: `HAR-01`, `SET-01`.
   - Gate Condition: Zero completed sessions without bound verification receipt; ADMISSION_GATE_EXEMPT eliminated for coding packs; TestTamperShield rejects assertion edits; greenfield oracle verified red-then-green; terminal state reporting fixed (oracle pass records completed, never abandoned).
   - Invariants: G-1 (Evidence Verifiability), I-7 (Domain Blindness).

2. `MS-SEE`:
   - Prerequisite packages: `IDX-01`.
   - Gate Condition: LdaRepoIndex adapter backs IndexPort (77k relations); observation tools return structured facts into L5 dialogue; L1–L3 cache prefix remains byte-identical across turns; provider cache breakpoints emitted.
   - Invariants: Cache-Prefix Immutability, Neutral Index Port (no implicit policy).

3. `MS-CHANGE`:
   - Prerequisite packages: `EDT-01`.
   - Gate Condition: Exact str_replace replaces fragile diff preimages; 2PC multi-file atomic transaction coordinator in adapters/environment/transaction.py; AST syntax preflight executes before staging; read-before-edit enforced.
   - Invariants: I-6 (Isolation), I-7 (Zero AST in Kernel).

4. `MS-CONTROL`:
   - Prerequisite packages: `PRF-01`.
   - Gate Condition: Single-worker vg-code-balanced qualified on frozen 30-task canary (Wilson score lower bound >= 0.40); typed budgets (usd_micros, turns, tokens) strictly enforced by kernel TypedBudgetGovernor; zero multi-agent lift claims authorized prior to closure.
   - Invariants: G-2 (Linear Authorization), G-3 (Non-Contamination).

5. `MS-CAMPAIGN` / `M-OCT`:
   - Prerequisite packages: `DIR-01`.
   - Gate Condition: SequentialDirector operates strictly as a runtime client with zero mutating tools; child episodes execute in isolated git worktrees; subagents coordinate via content-addressed SHA-256 mailbox (OCT-01); merge policy determined solely by external test verifier, never LLM voting.
   - Invariants: D-02 (Single Runtime Path), Monotonic Attenuation.

Ensure the table schema in `milestones.md` matches existing tables and preserves all existing M-0 to M-10 gates.
```

---

### Prompt 03: Technical Handbook & Spec for HAR-01 (Harness & Tool Protocols)
* **Target Files**: `docs/execution/technical.md` (§ Harness & Agent Protocols) and `docs/execution/spec.md` (§ Model Profiles & Tool Wire Formats)
* **Corpus Sources**: `opus/part1-evidence.md`, `opus/part2-diagnosis.md`, `opus/opus_solution.md`
* **Goal**: Provide the exact engineering recipe and schema deltas to fix the "deaf-mute agent" harness bugs.

```markdown
# ASSIGNMENT: Technical Handbook & Spec for HAR-01 (Harness Normalization)
Target Documents: `docs/execution/technical.md` (§ Harness & Agent Protocols) and `docs/execution/spec.md` (§ Model Profiles & Tool Wire Formats)
Source Evidence: Opus Review Dossier (Defects A, C, E, K, L, N)

Document the exact engineering specifications, classes, and schema changes for HAR-01:
1. Native Tool Calling Profiles (`domain/models/profile.py`):
   - Replace prose-dumping `FENCED_JSON` default with `tool_call_style = ToolCallStyle.NATIVE` for all production models.
   - Define the wire schema for native tool definitions and call parsing.
2. Approval Threshold Decoupling (`runtime/session.py`):
   - Replace hardcoded `approval_required_above="low"` with a manifest-configured parameter (`approval_threshold`).
   - Allow autonomous execution of `patch.apply` (medium) and `proc.exec` (high) in non-interactive `Mode.BENCHMARK`.
3. Explicit `finish` Tool Declaration:
   - Provide the exact JSON schema for `finish-tool.json` to be declared across all pack manifests.
   - Specify the payload: `status: {"completed", "failed"}`, `summary: str`.
4. SSE Stream Error Resilience (`adapters/models/openrouter.py`):
   - Add `retryable=True` to malformed or incomplete SSE stream chunk exceptions to prevent premature session aborts.
5. Duplicate `EffectStarted` Emission Fix (`runtime/ledger/emitter.py`):
   - Eliminate duplicate adjacent `EffectStarted` events with identical leases to preserve `State = fold(events)` integrity.
6. Terminal State Reporting Fix (`benchmarks/benchmark_20_suite/runner.py`):
   - Fix the completion inversion bug where 8/8 oracle-passing runs were recorded as `abandoned`.

Provide exact code snippets, method signatures, error types, and executable test falsifiers for `technical.md` and `spec.md`.
```

---

### Prompt 04: Technical Handbook & Spec for SET-01 (Settlement Integrity & Tamper Shield)
* **Target Files**: `docs/execution/technical.md` (§ Settlement & Verification) and `docs/execution/spec.md` (§ Evidence Models & Invariants)
* **Corpus Sources**: `grok/01-live-agent-and-holes.md`, `grok/02-theories-and-control-laws.md`, `grok/05-whitepaper...`
* **Goal**: Specify the settlement truth spine, removing exemptions, wiring tamper shields, and codifying the honest 4-state disposition.

```markdown
# ASSIGNMENT: Technical Handbook & Spec for SET-01 (Settlement Integrity)
Target Documents: `docs/execution/technical.md` (§ Settlement & Verification) and `docs/execution/spec.md` (§ Evidence Models & Invariants)
Source Evidence: Grok Dossier (§A.1–A.5), Opus Dossier (Part 7 §5)

Detail the exact implementation recipe and wire contracts for SET-01:
1. Removal of `ADMISSION_GATE_EXEMPT` (T-04):
   - Document how `session.py` removes the exemption for `vg-code-default` after recording the RF-25 successor baseline.
   - Specify the failure response when an agent calls `finish` without a non-empty patch on mutating tasks.
2. Wire `TestTamperShield` into Admission:
   - Specify the wiring of `TestTamperShield.evaluate(workspace_diff)` into `session._admit_completion`.
   - Define tamper detection logic: any modification or deletion of existing test files or weakening of assertions raises `TAMPER_DETECTED_FAIL_CLOSED`.
3. Implicated Tests as Verification Subject (T-18):
   - Define how reverse dependency callers from `IndexPort` are bound into session verification.
   - Refuse completion if modified symbols have untested callers in the repo.
4. Greenfield Stub-Fail / Impl-Pass Oracle:
   - Define the two-phase verification protocol for greenfield tasks: phase 1 must observe test failure against initial stubs; phase 2 must observe test pass against implementation.
5. Honest 4-State Disposition Wire Contract (`domain/evidence/disposition.py`):
   - Define the exact Python enum:
     ```python
     class ExecutionDisposition(str, Enum):
         PASSED = "passed"
         FAILED = "failed"
         UNDETERMINABLE = "undeterminable"
         NOT_RUN = "not_run"
     ```
   - Detail the event schema for `VerificationReceipt` and its reducer in `runtime/task_state.py`.

Provide complete recipes, class diagrams, error codes, and falsifiers for `technical.md` and `spec.md`.
```

---

### Prompt 05: Technical Handbook & Spec for EDT-01 (Atomic 2PC & AST Preflight)
* **Target Files**: `docs/execution/technical.md` (§ Edit Engine & Workspace Integrity) and `docs/execution/spec.md` (§ Patch Primitives & Errors)
* **Corpus Sources**: `opus/part3-sota-agent-engineering.md`, `grok/03-evolution-architecture.md`
* **Goal**: Specify the exact `str_replace` primitive, 2PC transaction coordinator, and adapter-level AST syntax preflight.

```markdown
# ASSIGNMENT: Technical Handbook & Spec for EDT-01 (2PC & AST Edit Primitive)
Target Documents: `docs/execution/technical.md` (§ Edit Engine & Workspace Integrity) and `docs/execution/spec.md` (§ Patch Primitives & Errors)
Source Evidence: Opus Dossier (Part 3 §5), Grok Dossier (Atomic 2PC)

Detail the exact architecture and implementation for EDT-01:
1. Exact-Match `str_replace` Primitive:
   - Reject 9-strategy fuzzy matching cascade (explain why indentation-flexible matching breaks Python syntax).
   - Implement strategies 1 & 2: unique exact substring match and trimmed-EOL match.
   - On preimage failure, emit `PATCH_PREIMAGE_MISMATCH` with line offsets, forcing a targeted `fs.read` re-anchor.
2. Read-Before-Edit Effect Boundary:
   - Implement an epoch check at `patch.apply` dispatch: refuse modification if the target file has not been read in the current episode epoch (`MODIFIED_FILE_NOT_INSPECTED`).
3. Multi-File 2PC Transaction Coordinator (`adapters/environment/transaction.py`):
   - Detail the shadow staging tree workflow: stage edits in memory/shadow tree, validate all files, commit to working tree atomically or roll back on any error.
4. Adapter AST Syntax Preflight:
   - Execute AST parsing (<0.2ms) inside `adapters/environment/git.py` prior to git staging.
   - Enforce Invariant I-7: confirm zero AST code is added to `kernel/dispatch.py`.

Provide full classes, method signatures, transaction rollback state machines, and falsifiers for `technical.md` and `spec.md`.
```

---

### Prompt 06: Technical Handbook & Spec for IDX-01 (Port-Backed LDA Intelligence)
* **Target Files**: `docs/execution/technical.md` (§ Repository Intelligence & IndexPort) and `docs/execution/spec.md` (§ Index Port Contracts & Tools)
* **Corpus Sources**: `opus/part3-sota-agent-engineering.md`, `ports/index.py`
* **Goal**: Back `IndexPort` with `.lda/index.db`, expose active L5 query tools, and preserve KV-cache prefix stability.

```markdown
# ASSIGNMENT: Technical Handbook & Spec for IDX-01 (LDA IndexPort & Cache Stability)
Target Documents: `docs/execution/technical.md` (§ Repository Intelligence & IndexPort) and `docs/execution/spec.md` (§ Index Port Contracts & Tools)
Source Evidence: Opus Dossier (Part 3 §6), ports/index.py

Specify the architectural integration of `.lda/index.db` (77k relations) behind `IndexPort`:
1. Adapter Implementation (`adapters/stores/lda_index.py`):
   - Implement `LdaRepoIndex` fulfilling `IndexPort` protocols (`ports/index.py`).
   - Query SQLite tables in `.lda/index.db` for symbols, callers, dependencies, and file tests.
2. Dialogue Observation Tools (L5 Dialogue):
   - Expose tools: `repo.search_symbols`, `repo.get_callers`, `repo.get_dependencies`, `repo.get_tests`.
   - Tool observations return bounded JSON/Markdown facts into conversation turn dialogue (Layer L5).
3. KV-Cache Prefix Protection (L1–L3 Immutability):
   - Reject treatise proposal of auto-injecting Personalized PageRank (PPR) into L2 system context.
   - Explain why L1–L3 must remain byte-identical across the entire episode to preserve ~90% prompt cache discounts.
4. Provider Cache Breakpoints:
   - Emit provider-specific breakpoint tokens (e.g. Anthropic `cache_control: {"type": "ephemeral"}`) at the L3 boundary.

Provide exact SQL queries, adapter classes, manifest tool definitions, and cache falsifiers for `technical.md` and `spec.md`.
```

---

### Prompt 07: Technical Handbook & Spec for Greenfield Oracle & Cache Telemetry
* **Target Files**: `docs/execution/technical.md` and `docs/execution/spec.md`
* **Corpus Sources**: `grok/01-live-agent-and-holes.md`, `opus/part1-evidence.md`
* **Goal**: Eliminate workspace noise (`.pyc`), add ledger cache telemetry, and enforce greenfield test honesty (T-15, T-19, T-36, T-37).

```markdown
# ASSIGNMENT: Technical Handbook & Spec for Greenfield Oracle & Telemetry
Target Documents: `docs/execution/technical.md` and `docs/execution/spec.md`
Tasks Covered: T-15, T-19, T-36, T-37

Provide detailed recipes and spec deltas for:
1. Workspace Noise Elimination (Opus Defect G):
   - Configure sandbox execution environment to route `PYTHONPYCACHEPREFIX` to tmpfs outside the repository tree.
   - Prevent generation of `.pyc` files that amplify workspace digests by 178x and confuse diff-based oracles.
2. Prompt Cache Telemetry (`runtime/ledger/emitter.py`):
   - Extend `TurnCompleted` ledger events with `cache_read_tokens` and `cache_write_tokens`.
   - Document how reducers track actual dollar savings per episode.
3. Greenfield Red-Then-Green Oracle Policy (T-15 / T-19):
   - Detail the verification policy in `packs/code-default/policies/greenfield.py`:
     - Disallow completing greenfield tasks if the test suite passed before any implementation code was written.
     - Reject empty stub completions that pass vacuously on `NotImplementedError` or `pass`.

Provide concrete environment variables, ledger schema diffs, test doubles, and falsifiers for `technical.md` and `spec.md`.
```

---

### Prompt 08: Technical Handbook & Spec for PRF-01 & MS-CONTROL Baseline
* **Target Files**: `docs/execution/technical.md` (§ Presets & Control Baseline) and `docs/execution/spec.md` (§ Product Presets & Budgets)
* **Corpus Sources**: `opus/part5-roadmap.md`, `grok/04-sota-program.md`
* **Goal**: Differentiate product presets (`fast`, `balanced`, `max`) with real typed budgets and specify the single-worker qualification canary.

```markdown
# ASSIGNMENT: Technical Handbook & Spec for PRF-01 & MS-CONTROL
Target Documents: `docs/execution/technical.md` (§ Presets & Control Baseline) and `docs/execution/spec.md` (§ Product Presets & Budgets)
Source Evidence: Opus (Defect O & Roadmap), Grok (SOTA Program)

Detail the concrete specifications for PRF-01 and MS-CONTROL:
1. Differentiated Product Presets:
   - Eliminate identical manifest aliases. Define real configurations in `harness.yaml`:
     - `fast`: $0.05 budget, 12 turns, 32k context, free/local model (Qwen 27B), basic search tools.
     - `balanced`: $0.20 budget, 25 turns, 64k context, DeepSeek/Qwen 27B, full IndexPort query tools, 2PC edit transactions.
     - `max`: $1.00 budget, 60 turns, 128k context, frontier escalation (Claude Opus/GLM-5), full closure, AST preflight.
2. Harness Composition Passthrough:
   - Fix Defect O: ensure declared budget ceilings in `harness.yaml` pass through to `EpisodeStarted.budgetCeiling` and are enforced by `TypedBudgetGovernor` in the kernel.
3. Single-Worker Qualification Canary Protocol (MS-CONTROL):
   - Define the frozen 30-task multi-class canary suite.
   - Specify the qualification threshold: Wilson score lower bound >= 0.40 on single-worker `vg-code-balanced`.
   - Reiterate Release Law: Zero multi-agent swarm lift claims authorized until this single-worker control baseline passes.

Provide YAML manifests, wiring code updates, statistical formulas for Wilson bounds, and falsifiers for `technical.md` and `spec.md`.
```

---

### Prompt 09: Technical Handbook & Spec for DIR-01 (Outer Director & Campaigns)
* **Target Files**: `docs/execution/technical.md` (§ Campaign Orchestrator) and `docs/execution/spec.md` (§ Campaign DAG & Mailbox Schemas)
* **Corpus Sources**: `octopus/consolidation/outer-loop-orchestrator.md`, `octopus/agents/meta-conductor.md`
* **Goal**: Specify the outer-loop director layer (`DIR-01` / `ORCH-01..11`) staged in Wave 5 as an attenuated runtime client of `EpisodeEngine`.

```markdown
# ASSIGNMENT: Technical Handbook & Spec for DIR-01 (Outer Director & Campaign Orchestration)
Target Documents: `docs/execution/technical.md` (§ Campaign Orchestrator) and `docs/execution/spec.md` (§ Campaign DAG & Mailbox Schemas)
Source Evidence: Octopus Dossier (ORCH-01..11, OCT-01/02)

Detail the architecture for the outer director staged in Wave 5 (post-MS-CONTROL):
1. Runtime Client Architecture:
   - Implement `SequentialDirector` as an external orchestrator in `vanguard/packages/runtime/campaign/director.py`.
   - Strictly domain-blind client of `EpisodeEngine`: director has ZERO mutating tools (`patch.apply` and `proc.exec` withheld).
2. Ephemeral Git Worktree Isolation:
   - Each child episode dispatches within an isolated git worktree (`runtime/campaign/worktree.py`).
   - Sibling subagents cannot access or corrupt each other's filesystem or memory.
3. Content-Addressed Mailbox (CAS) & CoordinationPlan:
   - Implement mailbox message passing where coordination packets are content-addressed SHA-256 blobs (zero shared mutable RAM).
4. Exterior Test-Verdict Merge Policy:
   - Reject LLM-quorum or evolutionary code merging.
   - Child branch merging is governed strictly by external test pass (`ExternalVerifier`).
5. Crash/Resume Durability:
   - Campaign state folded from event ledger; crash at node K resumes cleanly at node K+1 without duplicate effect execution.

Provide complete data structures, DAG schemas, worktree management routines, and crash/resume falsifiers for `technical.md` and `spec.md`.
```

---

### Prompt 10: Atomic Task Work-Tree Deconstruction
* **Target File**: `docs/execution/tasks.md`
* **Goal**: Deconstruct packages `HAR-01` through `DIR-01` into flat, dependency-ordered tasks with unambiguous acceptance falsifiers.

```markdown
# ASSIGNMENT: Atomic Task Staging in tasks.md
Target Document: `docs/execution/tasks.md`
Authority Tier: Execution Runway (Living Document)

Review the 5-Wave blueprint and the packages defined in `backlog.md` (`HAR-01`, `SET-01`, `EDT-01`, `IDX-01`, `PRF-01`, `DIR-01`).
Your task is to populate `docs/execution/tasks.md` with flat, actionable subtasks:

RULES FOR TASKS.MD:
- Format each task strictly using the canonical schema:
  ```markdown
  ### T-XX: <Task Title>
  - **package**: <HAR-01 | SET-01 | EDT-01 | IDX-01 | PRF-01 | DIR-01>
  - **subsystem**: <domain | ports | kernel | agency | runtime | adapters | packs>
  - **lane**: <Lane A (Build/Core) | Lane B (Audit/Test)>
  - **requires**: [T-YY, T-ZZ]
  - **file_touches**: [<exact relative file paths>]
  - **specification**: <Concise 2-3 sentence implementation directive>
  - **acceptance_falsifier**: <Exact executable command or test case that proves completion>
  ```
- Partition tasks across the 5 waves:
  - Wave 1 (Settlement & Signal Truth): Tasks for HAR-01 and SET-01.
  - Wave 2 (Capability Surface & Retrieval): Tasks for EDT-01 and IDX-01.
  - Wave 3 (Cache Integrity & Greenfield): Tasks for T-15, T-19, T-36, T-37.
  - Wave 4 (Control Baseline & Presets): Tasks for PRF-01 and MS-CONTROL canary.
  - Wave 5 (Outer Director & Campaign): Tasks for DIR-01.
- No sprint calendars, dates, or WIP tags. Use strict `requires:` dependency edges only.
```

---

### Prompt 11: Constitutional Invariant & TCB Budget Audit
* **Target Files**: Entire `docs/execution/` runway and repo linters
* **Goal**: Verify that all additions maintain the <= 1,438 LOC kernel limit, domain-blindness, and hexagonal boundaries.

```markdown
# ASSIGNMENT: Constitutional Invariant & TCB Budget Audit
Target Scope: All modifications in `docs/execution/` (`milestones.md`, `backlog.md`, `spec.md`, `technical.md`, `tasks.md`)

Execute a comprehensive constitutional audit across all proposed execution specifications:
1. TCB Budget Ceiling Verification:
   - Check that no task or specification adds lines of code to `vanguard/packages/kernel/`.
   - Confirm kernel remains strictly <= 1,438 LOC (run `python3 tools/linters/check_tcb_budget.py`).
2. Domain Blindness (Invariant I-7):
   - Confirm zero AST parsing, code analysis, or repository-specific logic is placed inside kernel dispatch stages (S0–S12).
   - Confirm AST preflight is confined to `adapters/environment/git.py`.
3. Hexagonal Dependency Flow:
   - Confirm dependency direction: `domain <- ports <- kernel <- agency <- runtime -> adapters`.
   - Confirm `adapters/` never imports `kernel` or `agency`.
   - Confirm `ports/index.py` remains a neutral protocol without embedded ranking policies.
4. Single Runtime Path (Invariant D-02):
   - Confirm `EpisodeEngine` remains the sole turn-loop engine. No parallel product engines (quarantine Chimera/Forge).
5. Documentation Anti-Sprawl Invariant:
   - Confirm zero new markdown files were introduced under `docs/reports/` or `docs/architecture/`.
   - Confirm all updates reside strictly in the canonical 5 execution files.

Output a formal pass/fail audit verdict for each invariant. If any check fails, provide the exact remediation diff.
```
