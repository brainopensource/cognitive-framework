> **CLOSED 2026-08-16 — archived from `docs/reviews/todo/`.**
> **SUPERSEDED by `ADR-0058`**, which this document produced.
> Finding-level verdicts and evidence: `docs/reviews/doing/009_prior_review_reconciliation_V043-REV.md`.
> Surviving findings are tracked in `docs/reviews/doing/011_master_backlog_phase3_V043-REV.md`.
> This document is historical. Do not action it directly.

---

# Vanguard General Task Solver (GTS) — Technical Phase Review & Architecture Roadmap

**Document:** `docs/review/todo/phases_review.md`  
**Classification:** Technical Architecture, Systems Engineering & Program Review (PhD-Level Specification)  
**Authors:** Senior Software Architect, Principal Tech Lead & Project Lead  
**Baseline Release Tag:** `v0.4.0-sprint4` (Branch: `sprint5-6/integration`)  
**Target Delivery:** Phase 2 Lightweight Beta MVP (Sprints 5 & 6)  
**Referenced Authorities:** [GTS-13C](file:///home/rocha/Coding/Aether-D-System/docs/v4/13_C_gts_mvp_program_and_engineering_plan.md), [Decision Register v0.4.0](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md), [System Architecture ICD](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/system-architecture-icd.md), [Active MVP Contract](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json), [Verification Plan](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/verification-threat-evaluation-plan.md).

---

## Executive Summary & Program Framing

The Vanguard General Task Solver (GTS) project is engineered to resolve the fundamental question of autonomous agent systems: *Can machine problem-solving competence accumulate monotonically and verifiably over time without representational collapse, safety degradation, or unprincipled ad-hoc scaffolding?*

To answer this question, the program was architected across three discrete operational waves (Phases):
1. **Phase 0 (Plan & Foundation — Sprint 0):** Formal governance baseline, mathematical wire contracts (T1), cryptographic canonicalization, verification plan, and strict package lattice boundary enforcement.
2. **Phase 1 (The Core Trust Spine — Sprints 1 to 4):** Capability-mediated kernel dispatch, attenuation algebra, hierarchical budget conservation, transactional event ledger, failure-path recovery, recursive episode loop, durable governance process engine, port activation bundles, rootless worker containment, worktree-isolated Git environment adapter, and model-free trust spine verification.
3. **Phase 2 (The Beta Product Slice — Sprints 5 & 6):** Exterior evaluator isolation, L1–L5 prefix-stable context compilation, runtime composition root, descriptor-bound human-in-the-loop approvals, interactive CLI/TUI integration, and end-to-end execution of the first typed coding agent harness (`vg-code-default`) against a live LLM ([OpenRouter](https://openrouter.ai)).
4. **Phase 3 & Future Waves (Generalization, Falsification & Evolution — Sprints 7 to 9+):** Harness reconstruction suite (Claude-Code, OpenCode, SWE-agent), A/A statistical floor estimation, paired comparative trials, meta-evaluation, non-coding environment generality falsification, and offline evolutionary Pareto archive distillation.

This review provides a comprehensive audit of all landed code, identifies subtle technical drifts and contract lags, and establishes the exact engineering blueprint for Phase 2.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  VANGUARD PROGRAM ROADMAP                                        │
├───────────────────────────────┬──────────────────────────────────┬───────────────────────────────┤
│    PHASE 0 & PHASE 1 (DONE)   │     PHASE 2 (SPRINTS 5 & 6)      │     PHASE 3+ (SPRINTS 7-9+)   │
│   Sprints 0, 1, 2, 3, 4       │       Beta MVP Delivery          │   Generalization & Evolution  │
├───────────────────────────────┼──────────────────────────────────┼───────────────────────────────┤
│ • Formal Wire Schemas (T1)    │ • Exterior Evaluator OS          │ • Harness Benchmark CLI       │
│ • Deterministic Canonicalizer │   Isolation & Double Probes (T5) │ • Reconstructions (SWE/Claude)│
│ • Kernel Dispatch S0-S12 (T2) │ • Prefix-Stable Context          │ • A/A Noise Floor & Paired    │
│ • Attenuation & Budget Tree   │   Compiler (L1-L5) (T4.9)        │   Statistical Engine (T8)     │
│ • Append-Only Ledger (T3)     │ • Pre-action Competence Log      │ • Generality Falsifier: Non-  │
│ • Episode & Process Engines   │ • Runtime Composition Root       │   Coding Reconciliation (T9)  │
│ • Port Activation Bundles     │ • Descriptor-Bound Approvals     │ • Meta-Evaluator & Sabotage   │
│ • Git Worktree & Rootless OS  │ • Hexagonal CLI / Ink TUI        │ • Offline Evolutionary Pareto │
│ • S4 Model-Free Trust Spine   │ • First Real Bug Fixed Live      │   Archive & CLS Consolidation │
│ • Disposables (spike/) Purged │ • Single-Key Correction Capture  │ • Emergent Coordination Depth │
└───────────────────────────────┴──────────────────────────────────┴───────────────────────────────┘
```

---

## CHAPTER 1: Current State & Baseline Inventory (Phase 0 & Phase 1)

### 1.1 What We Have: The Landed Architecture

Through Sprints 0, 1, 2, 3, and 4 (merged to `main` at `v0.4.0-sprint4`), the foundational keel and trust spine of Vanguard have been constructed. The codebase strictly adheres to an acyclic dependency lattice enforced at build-time:

$$\text{domain} \longleftarrow \text{ports} \longleftarrow \text{kernel} \longleftarrow \text{agency} \longleftarrow \text{runtime} \longrightarrow \text{adapters}$$

```
                                  ┌────────────────────────┐
                                  │      clients/cli       │ (UI presentation & client port)
                                  └───────────┬────────────┘
                                              │ RuntimeClient
                                              ▼
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   vanguard/packages/                                             │
│                                                                                                  │
│  ┌──────────────────────┐              ┌──────────────────────┐                                  │
│  │   agency/episode     │─────────────▶│   kernel/dispatch    │                                  │
│  │  (EpisodeEngine)     │              │  (Mediation/Grants)  │                                  │
│  └──────────┬───────────┘              └──────────┬───────────┘                                  │
│             │                                     │                                              │
│             │                                     ▼                                              │
│             │                          ┌──────────────────────┐        ┌──────────────────────┐  │
│             ├─────────────────────────▶│    ports/ interfaces │◀───────│  adapters/           │  │
│             │                          │ (Model, Env, Eval..) │        │ (Git, OpenRouter...) │  │
│             ▼                          └──────────┬───────────┘        └──────────────────────┘  │
│  ┌──────────────────────┐                         │                                              │
│  │  runtime/governance  │                         ▼                                              │
│  │  (ProcessEngine)     │──────────────▶┌──────────────────┐                                     │
│  └──────────┬───────────┘               │ domain/          │                                     │
│             │                           │ (Wire/Contracts) │                                     │
│             ▼                           └──────────────────┘                                     │
│  ┌──────────────────────┐                                                                        │
│  │    runtime/ledger    │ (Recovery Scanner, Projections, Store Adapters)                        │
│  └──────────────────────┘                                                                        │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### A. Domain Contracts & Mathematical Keel ([`vanguard/packages/domain/`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/domain/))
- **Deterministic Canonicalization ([`t1_dev1_canonicalisation.py`](file:///home/rocha/Coding/Aether-D-System/test/contracts/t1_dev1_canonicalisation.py)):** IEEE 754 float rejection, recursive key-sorting, UTF-8 normalization, and SHA-256 digest hashing validated across $>40$ golden triples.
- **Strongly Typed Primitives ([`primitives`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/domain/primitives/)):** Opaque scalar wrappers for `Digest`, `Timestamp`, `EpisodeId`, `RunId`, `ProcessId`, `GrantId`, `PrincipalId`, and `ArtifactId`.
- **Resource Selector Algebra ([`selectors`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/domain/selectors/)):** Decidable inclusion relation $\text{includes}(A, B)$ across resource kinds (`path`, `glob`, `command`, `host`, `record`). Proved reflexive, transitive, and antisymmetric, denying all undefined pairs.
- **Wire Contract Schemas ([`contracts.ts`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/domain/contracts.ts), [`schemas/v4/`](file:///home/rocha/Coding/Aether-D-System/schemas/v4/)):** Universal schemas for `EffectDescriptor`, `CapabilityGrant`, `Receipt`, `EventEnvelope`, `Artifact`, `Claim`, `CorrectionRecord`, and `Recording`.
- **Dual Reader Conformance:** Dual Python and TypeScript deserializers with forward-compatible reader profiles (`additionalProperties: true`) and strict writer profiles (`additionalProperties: false`).

#### B. The Capability Kernel ([`vanguard/packages/kernel/`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/kernel/))
- **Single Dispatch Pipeline S0–S12 ([`dispatch.py`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/kernel/dispatch.py)):** Every effect request executes through a deterministic 13-stage state pipeline: Scope Verification $\to$ Rate Limiting $\to$ Principal Check $\to$ Selector Matching $\to$ Attenuation Validation $\to$ Pre-Execution Intent Append $\to$ Budget Reservation $\to$ Sandboxed Execution $\to$ Receipt Acquisition $\to$ Budget Reconciliation $\to$ Event Emission.
- **Sink-Class Mediation Theorem ([ADR-0054](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L157)):** Resolves the historical mediation conflict:
  - $\text{pure}$: Recorded in ledger; bypasses capability broker (no grant required).
  - $\text{observation}$: Recorded in ledger; selector-checked and provenance-labeled; no grant required.
  - $\text{privileged}$: Recorded in ledger; requires explicit, descriptor-bound `CapabilityGrant`.
- **Attenuation Algebra ([`attenuation.py`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/kernel/attenuation.py)):** Enforces monotonic narrowing:
  $$\text{ChildGrant} \subseteq \text{ParentGrant} \iff (\text{Verb}_c \subseteq \text{Verb}_p) \land (\text{Selector}_c \subseteq \text{Selector}_p) \land (\text{Expiry}_c \le \text{Expiry}_p) \land (\text{Budget}_c \le \text{Budget}_p)$$
- **Budget Conservation as Lease Trees ([`budget.py`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/kernel/budget.py)):** Multi-dimensional vector ($\text{USD}$, $\text{tokens}$, $\text{milliseconds}$, $\text{bytes}$, $\text{depth}$, $\text{effects}$). Child leases hold reservations against parent capacity; overruns debit negatively and lower the ceiling.
- **TCB Budget Control ([`tools/check_tcb_budget.py`](file:///home/rocha/Coding/Aether-D-System/tools/check_tcb_budget.py)):** Kernel size strictly bounded at 1,307 logical LOC (alarm threshold at 1,438 LOC).

#### C. Event Ledger & Recovery ([`vanguard/packages/runtime/ledger/`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/runtime/ledger/))
- **Transactional Append Log ([`adapters/stores/`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/stores/)):** Single-writer, SQLite and In-Memory event stores supporting atomic batch appends and cryptographic chain hashing.
- **Pure State Reducer:** Associative state reconstruction $(S, E) \to S'$ across arbitrary event batches with zero I/O.
- **Crash Recovery Scanner ([`recovery.py`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/runtime/ledger/recovery.py)):** Independent scanner operating outside the dying process, reconciling uncommitted intents to `undeterminable` and recording terminal run events.
- **Cassette Serialization ([`adapters/models/cassette.py`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/models/cassette.py)):** Byte-reproducible model interaction recording for deterministic replay.

#### D. Execution Coordinators ([`agency/episode/`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/episode/) & [`runtime/governance/`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/runtime/governance/))
- **Episode Loop ([`agency/episode/engine.py`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/episode/engine.py)):** Implements the recursive $\text{observe} \to \text{propose} \to \text{authorise} \to \text{effect} \to \text{receipt}$ reduction for open-ended problem solving. Cognitive vocabulary (`plan`, `reflect`, `debug`) is strictly forbidden in identifier names by CI linter ([`test_agency_lint.py`](file:///home/rocha/Coding/Aether-D-System/test/agency/test_agency_lint.py)).
- **Durable Process Engine ([`runtime/governance/engine.py`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/runtime/governance/engine.py)):** Finite state machine for human-auditable workflows (e.g., approval checkpoints). Resumes from ledger alone without model re-execution.

#### E. Activated Ports & Adapters ([`ports/`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/ports/) & [`adapters/`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/))
- **Port Activation Bundles ([`vanguard/packages/ports/`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/ports/)):** Every port ships an interface, a shared conformance suite, and a deterministic fake:
  - `ModelPort` $\to$ Fake, Cassette, OpenRouter ([`openrouter.py`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/models/openrouter.py)).
  - `EnvironmentPort` $\to$ Fake, Git Worktree Adapter ([`git.py`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/environment/git.py)).
  - `EvaluatorPort` $\to$ Fake Scripted Evaluator ([`evaluators/fake.py`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/evaluators/fake.py)).
  - `SandboxRunner` $\to$ Fake, Rootless Linux Namespace Sandbox ([`rootless.py`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/adapters/sandbox/rootless.py)).
- **Permanent Manifests ([`agency/manifests/`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/manifests/)):** `vg-shell-only` registered as the undeletable baseline control; `vg-code-default` registered as the typed beta manifest (`read`, `search`, `patch`, `test`).

#### F. Trust Spine Verification Gate
- **Model-Free Trust Spine Gate ([`test/trust/test_spine.py`](file:///home/rocha/Coding/Aether-D-System/test/trust/test_spine.py)):** Verifies capability denial, attenuation narrowing, budget exhaustion, event atomicity, crash recovery, and secret non-disclosure with zero model dependencies (`OPENROUTER_API_KEY` unset).
- **Disposables Purged:** `spike/` and `slice/` deleted under `S4-GATE-001`; absence verified by `MF-S4-001`. Findings preserved in [`slice-findings.md`](file:///home/rocha/Coding/Aether-D-System/docs/sprint2/slice-findings.md).

---

## CHAPTER 2: Next Phase — Phase 2 Lightweight Beta MVP (Sprints 5 & 6)

### 2.1 The Phase 2 Mission Statement

Phase 2 takes the verified trust spine and transforms it into an operational, dogfoodable developer tool. The product deliverable of Phase 2 is:

> **The Lightweight Beta MVP:** A modular framework executing one frozen manifest (`vg-code-default`). It uses a real OpenRouter LLM, typed tools (`read`, `search`, `patch`, `test`), isolated Git worktrees, rootless OS sandboxing, an isolated exterior evaluator, and human approval over the exact displayed diff to diagnose, repair, and verify a real bug in an existing repository without mid-run manual patching.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               PHASE 2 (SPRINTS 5 & 6) ARCHITECTURE                               │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                  │
│   ┌────────────────────────────────────────────────────────────────────────┐                     │
│   │               CLI Client Layer (vanguard/clients/cli/)                 │                     │
│   │   • Ink / React TUI with live streaming of VG-04 EventEnvelopes       │                     │
│   │   • Headless execution mode for automated evaluation pipelines        │                     │
│   │   • Interactive Human-in-the-Loop Approval UI (displays exact diff)   │                     │
│   │   • Single-keystroke CorrectionRecord capture (reason codes)          │                     │
│   └───────────────────────────────────┬────────────────────────────────────┘                     │
│                                       │ RuntimeClient IPC / Direct                               │
│                                       ▼                                                          │
│   ┌────────────────────────────────────────────────────────────────────────┐                     │
│   │            Runtime Composition Root (vanguard/packages/runtime/)       │                     │
│   │   • Binds Kernel + Ledger + Agency + Governance + Adapters             │                     │
│   │   • Dispatches typed effects to Git Environment Adapter               │                     │
│   │   • Coordinates process suspension during pending human approvals     │                     │
│   └───────────────┬───────────────────────────────────────┬────────────────┘                     │
│                   │                                       │                                      │
│        Context L1-L5                              Isolated Execution                             │
│                   ▼                                       ▼                                      │
│   ┌───────────────────────────────┐       ┌────────────────────────────────┐                     │
│   │ Context Compiler (agency/)    │       │ Worker Perimeter (adapters/)   │                     │
│   │ • L1 System, L2 Tools         │       │ • Rootless namespace sandbox   │                     │
│   │ • L3 Env, L4 Task, L5 Dialogue│       │ • Mount, egress, syscall probe │                     │
│   │ • Prefix-stable cache economy │       │ • Git worktree per branch      │                     │
│   │ • Provenance labels per block │       │ • Typed read/search/patch/test │                     │
│   └───────────────┬───────────────┘       └────────────────┬───────────────┘                     │
│                   │                                        │                                     │
│                   ▼                                        ▼                                     │
│   ┌───────────────────────────────┐       ┌────────────────────────────────┐                     │
│   │ ModelPort (OpenRouter)        │       │ Exterior Evaluator OS Process  │                     │
│   │ • OpenAI-compatible HTTP      │       │ • Separate OS identity & image │                     │
│   │ • Secret references only      │       │ • Double probe input audit     │                     │
│   │ • Cassette recording fallback │       │ • Triggers only on ledger term │                     │
│   └───────────────────────────────┘       └────────────────────────────────┘                     │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 2.2 Sprint 5: The Judge & Context Substrate

**Goal:** Separate the evaluation plane from the execution plane at the OS level, implement the prefix-stable L1–L5 context compiler, and record pre-action competence predictions.

#### Workstream 1: Exterior Evaluator Isolation (T5.3–T5.6)
1. **Separate OS Identity & Container Image Digest (T5.3):**
   - The candidate agent executes under worker UID `10001` (rootless namespace); the evaluator executes under a dedicated UID `10002` with an immutable container image digest.
   - The worker has zero filesystem read/write access to `/evaluator/` bundles, oracle tests, or scoring fixtures.
2. **Double Probe Verification Protocol (T5.4):**
   - Probe 1 (Immutability): Cryptographic hash verification that tracked evaluator inputs (ground-truth test assertions) are bit-for-bit unchanged after worker execution.
   - Probe 2 (Non-Pollution): Complete directory walk proving zero untracked files or monkey-patched fixtures exist within the test execution path.
   - A verdict cannot be constructed if either probe fails.
3. **Evidence-Plane Evaluation Trigger (T5.5):**
   - The evaluator is triggered strictly by observing a terminal event (`RunCompleted`, `RunAborted`) in the ledger.
   - CI boundary tests ([`TEST-ARCH-004`](file:///home/rocha/Coding/Aether-D-System/tools/check_boundaries.py)) enforce that `vanguard/packages/agency/` has zero import paths to `vanguard/packages/ports/evaluator.py` or evaluator adapters.
4. **Inconclusive Fail-Closed Handling (T5.6):**
   - Provider timeouts, socket resets, runner segfaults, and perimeter violations resolve to `undeterminable` / `inconclusive`. They are never treated as task failure or task success.

#### Workstream 2: Prefix-Stable Context Compiler (T4.9–T4.11)
1. **L1–L5 Layered Architecture ([`vanguard/packages/agency/context/`](file:///home/rocha/Coding/Aether-D-System/vanguard/packages/agency/)):**
   - **L1 (System Core):** Fixed operational identity, capability rules, behavioral constraints (100% prefix-cached).
   - **L2 (Tools & Schemas):** Frozen JSON Schemas for `read`, `search`, `patch`, `test` (100% prefix-cached).
   - **L3 (Environment State):** Repository map, branch context, language runtime version (cache-stable per session).
   - **L4 (Task Description):** User prompt, bug report, issue description, target constraints.
   - **L5 (Dialogue History):** Rolling turn window, observation summaries, redacted error receipts.
2. **Token Accounting & Provenance Tagging:**
   - Every block in the compiled context carries its byte length, token estimate, and cryptographic `provenance` metadata.
3. **Pre-Action Competence Logging (T4.11):**
   - Before emitting a proposal, the model outputs a structured competence prior $P(\text{success} \mid \text{task})$.
   - The prior is recorded to the ledger as an unmediated event for offline Brier calibration scoring.

---

### 2.3 Sprint 6: Beta Integration, Approvals & Live Coding Agent

**Goal:** Wire all components into the runtime composition root, integrate the interactive TUI with descriptor-bound approvals, and fix a real repository bug end-to-end.

#### Workstream 1: Runtime Composition Root (`vanguard/packages/runtime/root.py`)
1. **Component Assembly:**
   - Assembles `Kernel(store, policy, budget_tree)` + `EpisodeEngine(kernel, model_adapter, clock)` + `ProcessEngine(store, definitions)` + `GitEnvironmentAdapter(worktree_root)` + `RootlessSandbox(worker_config)`.
   - Exposes clean programmatic invocation methods (`run_manifest`, `resume_process`, `stream_ledger`).

#### Workstream 2: Descriptor-Bound Approvals & Human-in-the-Loop (T6.6)
1. **Normalised Diff Presentation:**
   - When a proposal requests `fs.patch` (Sink Class: `privileged`), `Kernel.dispatch` intercepts the request and triggers a `SuspensionRequired` event.
   - The `ProcessEngine` transitions to `AWAITING_HUMAN_APPROVAL`.
   - The exact normalized unified diff (including hunk headers and target file path) is presented in the TUI.
2. **Cryptographic Binding:**
   - The human approval command cryptographically signs the `argsDigest` of the displayed `EffectDescriptor`.
   - If the patch content is altered between display and execution, digest mismatch fails closed (`MF-GOV-001`).

#### Workstream 3: Interactive CLI / TUI & Client Adapter ([`vanguard/clients/cli/`](file:///home/rocha/Coding/Aether-D-System/vanguard/clients/cli/))
1. **Hexagonal Client Port Implementation:**
   - Implement `LiveRuntimeClient` conforming to [`cli_tui_architecture.md`](file:///home/rocha/Coding/Aether-D-System/docs/development/cli_tui_architecture.md).
   - Real-time streaming of `EventEnvelope` items via async iterators.
   - Dedicated TUI screens: Run Execution View, Diff Approval Modal, Artifact Inspector (`vg why`), and Run Replay (`vg trace`).

#### Workstream 4: End-to-End Bug Fix & Correction Capture (T6.1, T6.7, T6.8)
1. **The Beta Dogfood Milestone:**
   - Execute `vg run --manifest vg-code-default --task "Fix bug #123"` against a real Git repository.
   - The agent reads files, searches codebase, generates a patch, suspends for human review, applies the diff upon approval, runs `pytest`, and records a verified fix.
2. **Single-Keystroke Correction Capture (T6.7):**
   - If the operator modifies or rejects the patch, the TUI immediately prompts for a single-key reason code (`[d]efect`, `[s]tyle`, `[t]est`, `[s]ecurity`, `[a]rchitecture`).
   - A `CorrectionRecord` is appended to the ledger.
3. **Latency & Performance Instrumentation (T6.8):**
   - Automated measurement of p95 time-to-first-token, p95 time-to-first-effect, approval round-trip overhead, and event serialization overhead.

---

## CHAPTER 3: Future Phases — Phase 3 & Beyond (Sprints 7 to 9+)

Following the Beta MVP delivery in Phase 2, the system expands into its full research and autonomous evolution capacity.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 PHASE 3 & BEYOND EVOLUTIONARY PATH                               │
├────────────────────────────────┬────────────────────────────────┬────────────────────────────────┤
│   SPRINT 7: RECONSTRUCTIONS    │    SPRINT 8: INSTRUMENTATION   │    SPRINT 9+: EMERGENCE        │
├────────────────────────────────┼────────────────────────────────┼────────────────────────────────┤
│ • Claude-Code Manifest         │ • A/A Noise Floor Runner       │ • Offline Evolutionary Pareto  │
│ • OpenCode Manifest            │ • Paired Statistical Engine    │   Archive Optimizers           │
│ • SWE-Agent Manifest           │   (McNemar, Bootstrap)         │ • CLS Dual-Memory Consolidation│
│ • Zero Core Change Detector    │ • Pre-Registration Hashes      │ • Generality Falsifier (Non-   │
│ • `vg harness bench` CLI       │ • Meta-Evaluator Gap Monitor   │   Coding Reconciliation Task)  │
│ • Dynamic Manifest Discovery   │ • Automatic Promotion Freeze   │ • Emergent Coordination Depth  │
└────────────────────────────────┴────────────────────────────────┴────────────────────────────────┘
```

### 3.1 Sprint 7: Framework Generalization & Competitor Reconstructions
- **Harness as Data (T7.5–T7.7):** Express external state-of-the-art architectures (Claude-Code, OpenCode, SWE-agent) entirely as declarative `HarnessManifest` YAML/JSON files.
- **The Configurability Falsification Rule:** If expressing a competitor harness requires modifying a single line of code in `vanguard/packages/kernel/` or `agency/episode/`, the framework abstraction is considered falsified and rejected.
- **Benchmarking CLI:** `vg harness bench --manifest-a vg-code-default --manifest-b claude-code-reconstruction --dataset swe-bench-lite`.

### 3.2 Sprint 8: Statistical Instrumentation & Generality Falsification
- **A/A Floor Estimation (T8.1):** Run identical harness configurations against themselves over $N \ge 100$ runs to establish the baseline stochastic noise floor per task class. No performance delta is considered significant unless it exceeds the A/A floor.
- **Paired Experimental Design (T8.2–T8.4):** Discordant pair evaluation, McNemar exact tests, paired bootstrap confidence intervals, and pre-registered cryptographic evaluation protocols.
- **Meta-Evaluator Dashboard & Sabotage Suite (T8.7–T8.8):** Plant intentionally defective / proxy-exploiting candidates. If the verifier passes them, promotions across the entire system are automatically frozen.
- **Generality Falsifier (T9.1–T9.3):** Introduce a completely non-coding domain (structured data reconciliation and log triage). Added purely through adapters and manifests. Zero changes allowed to the core loop.

### 3.3 Phase 4 (Long-Term): Evolution, Memory & Self-Improvement
- **Complementary Learning Systems (CLS) Memory Architecture:** Fast episodic storage (transactional event ledger) coupled with slow, offline semantic consolidation and procedural skill extraction.
- **Pareto/QD Competence Archives:** Multi-objective evolutionary optimization over artifact representations (prompts, retrieval policies, context strategies) maintaining diverse problem-solving niches.
- **Lakatos Scientific Research Program Partition:**
  - *Hard Core (Immutable):* Capability kernel, event ledger integrity, mathematical contracts.
  - *Protective Belt (Mutable):* Tool descriptions, context layers, operator playbooks, model routing heuristics.
- **Emergent Organizational Hierarchy:** Multi-agent recursion depth (Agents $\to$ Teams $\to$ Departments) discovered empirically through selection pressure rather than hardcoded class hierarchies.

---

## CHAPTER 4: Technical Audits, Flaws, Architectural Drifts & Debt Matrix

A rigorous audit of the current repository revealed several key findings, technical debts, and contract drifts that must be actively addressed during Phase 2 planning:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   AUDIT & TECHNICAL DEBT MATRIX                                  │
├────────────────────┬──────────┬───────────┬──────────────────────────────────┬───────────────────┤
│ Finding / Drift ID │ Severity │ Subsystem │ Summary                          │ Current Status    │
├────────────────────┼──────────┼───────────┼──────────────────────────────────┼───────────────────┤
│ GAP-01: ModulePoll │ CRITICAL │ Test/CI   │ In-process test discovery module │ RESOLVED & GREEN  │
│                    │          │           │ pollution in test_spine.py       │ (Subprocess isol) │
├────────────────────┼──────────┼───────────┼──────────────────────────────────┼───────────────────┤
│ GAP-02: ContractLag│ HIGH     │ Governan. │ active-mvp-contract.json sync    │ RESOLVED & GREEN  │
│                    │          │           │ with landed S3-S4 evidence       │ (100% 42/42 cov)  │
├────────────────────┼──────────┼───────────┼──────────────────────────────────┼───────────────────┤
│ GAP-03: RootStub   │ HIGH     │ Runtime   │ vanguard/packages/runtime/ lacks │ Sprint 6 Planned  │
│                    │          │           │ composition root module (root.py)│ Feature Task      │
├────────────────────┼──────────┼───────────┼──────────────────────────────────┼───────────────────┤
│ GAP-04: ClientSync │ MEDIUM   │ CLI / TUI │ CLI mock-runtime.ts implements   │ Sprint 6 Planned  │
│                    │          │           │ lightweight RuntimePort contract │ Feature Task      │
├────────────────────┼──────────┼───────────┼──────────────────────────────────┼───────────────────┤
│ GAP-05: ContextDir │ MEDIUM   │ Agency    │ agency/context/ compiler (L1-L5) │ Sprint 5 Planned  │
│                    │          │           │ absent from agency codebase      │ Feature Task      │
├────────────────────┼──────────┼───────────┼──────────────────────────────────┼───────────────────┤
│ GAP-06: LiveKeyReq │ LOW      │ Adapters  │ REQ-SLICE-001 live latency log   │ Open (Live key    │
│                    │          │           │ pending disposable credential    │ run in S5/S6)     │
└────────────────────┴──────────┴───────────┴──────────────────────────────────┴───────────────────┘
```

### Detailed Audit Breakdown

#### 1. GAP-01 (Resolved): Test Discovery In-Process `sys.modules` Pollution
- **Symptom:** Running `python3 -m unittest discover -s test` previously failed on [`trust.test_spine.NoModelOnTheGatePath.test_no_provider_adapter_is_loaded_by_the_spine`](file:///home/rocha/Coding/Aether-D-System/test/trust/test_spine.py#L290).
- **Remediation Implemented:** Isolated `test_no_provider_adapter_is_loaded_by_the_spine` and `test_the_episode_holds_no_evaluator_authority` to execute in clean subprocesses. Full suite (`python3 -m unittest discover -s test`) passes 252/252 tests 100%.

#### 2. GAP-02 (Resolved): Contract Status Lag in `active-mvp-contract.json`
- **Symptom:** Requirements [`REQ-EXEC-001..002`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json#L667), [`REQ-PORT-002..006`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json#L701), [`REQ-TRUST-001`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json#L785), and [`REQ-SEC-001`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json#L803) were previously marked `"open"`.
- **Remediation Implemented:** Updated [`active-mvp-contract.json`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json) to mark all 8 landed S3–S4 requirements as `covered` with verified execution evidence. Contract tool reports 100% merged scope evidence coverage (42/42 rows).

#### 3. GAP-03 (High): Missing Runtime Composition Root
- **Symptom:** `vanguard/packages/runtime/` contains subpackages `governance/` and `ledger/`, but no top-level composition module (`root.py` or `runner.py`).
- **Root Cause Analysis:** Sprints 3 and 4 implemented individual engines in isolation. The integration layer that wires ports, kernel, episode engine, and process engine into an executable runtime was scheduled for Sprint 6.
- **Remediation:** Implement `vanguard/packages/runtime/runner.py` with strict dependency injection, ensuring the runtime remains the only legal locus of concrete adapter instantiation.

#### 4. GAP-04 (Medium): CLI Client Contract Synchronization
- **Symptom:** [`vanguard/clients/cli/src/runtime.ts`](file:///home/rocha/Coding/Aether-D-System/vanguard/clients/cli/src/runtime.ts) exposes a minimal `RuntimePort` (`run`, `trace`, `why`), whereas [`docs/development/cli_tui_architecture.md`](file:///home/rocha/Coding/Aether-D-System/docs/development/cli_tui_architecture.md) defines a comprehensive `RuntimeClient` interface (`startRun`, `streamEvents`, `getRun`, `requestCancel`, `resolveApproval`, `explainArtifact`).
- **Remediation:** Refactor `vanguard/clients/cli/src/` in Sprint 6 to implement the full `RuntimeClient` contract, enabling streaming event iteration and interactive human approval resolution.

#### 5. GAP-05 (Medium): Missing `agency/context/` Compiler Module
- **Symptom:** Prompt construction in the episode engine currently utilizes basic dictionary formatting.
- **Remediation:** Implement `vanguard/packages/agency/context/compiler.py` in Sprint 5 to enforce L1–L5 prefix-stable ordering, token budgets, and provenance tracking.

---

## CHAPTER 5: Sprint 5 & 6 Developer Lane Allocation & Merge Gates

Following the non-negotiable **Four-Lane Law** ([Decision Register §10, ADR-0056](file:///home/rocha/Coding/Aether-D-System/docs/v4/09_vanguard_decision_register_v040.md#L164)), the work for Sprints 5 and 6 is structured across four parallel tracks of mixed complexity:

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               PHASE 2 FOUR-LANE WORK ALLOCATION                                  │
├─────────┬──────────────┬──────┬─────────┬────────────────────────────────────────────────────────┤
│ Lane    │ Owner Track  │ Cx   │ Type    │ Primary Deliverable & Owned Subsystem                  │
├─────────┼──────────────┼──────┼─────────┼────────────────────────────────────────────────────────┤
│ Lane SA │ Senior Dev A │ 5/5  │ GATE    │ L1-L5 Context Compiler, Competence Estimator pre-action│
│         │              │      │         │ & Runtime Composition Root (agency/context, runtime/) │
├─────────┼──────────────┼──────┼─────────┼────────────────────────────────────────────────────────┤
│ Lane SB │ Senior Dev B │ 4/5  │ GATE    │ Exterior Evaluator OS Process Isolation, Double Probes │
│         │              │      │         │ & Containment Report Enforcement (adapters/evaluators) │
├─────────┼──────────────┼──────┼─────────┼────────────────────────────────────────────────────────┤
│ Lane DC │ Dev C (Mid)  │ 3/5  │ FAST    │ ModelPort Token Accounting, OpenRouter Live Integration│
│         │              │      │         │ & Performance/Latency Instrumentation (adapters/models)│
├─────────┼──────────────┼──────┼─────────┼────────────────────────────────────────────────────────┤
│ Lane DD │ Dev D (Mid)  │ 2/5  │ FAST    │ CLI RuntimeClient IPC Adapter, Ink TUI Approval Screens│
│         │              │      │         │ & Single-Key Correction Capture (clients/cli)          │
└─────────┴──────────────┴──────┴─────────┴────────────────────────────────────────────────────────┘
```

### Detailed Lane Breakdown

### 5.1 Sprint 5 Packets (Foundation & Isolation)
- **Lane SA (Senior A - GATE, Cx 4):** Context Compiler (`vanguard/packages/agency/context/`). Implement L1–L5 layered assembly, token budgeting, prefix caching stability tests, and pre-action competence logging.
- **Lane SB (Senior B - GATE, Cx 4):** Evaluator Isolation (`vanguard/packages/adapters/evaluators/`). Implement separate OS process execution under dedicated UID, container image verification, immutability probe, and non-pollution directory probe.
- **Lane DC (Developer C - FAST, Cx 2):** OpenRouter Adapter Enhancements (`vanguard/packages/adapters/models/openrouter.py`). Implement token accounting estimation, rate-limit retry backoff with jitter, and cassette recording improvements.
- **Lane DD (Developer D - FAST, Cx 2):** Client Contract Refactoring (`vanguard/clients/cli/src/`). Align TypeScript client interfaces with `RuntimeClient` specification; build replay adapter for JSONL ledger streams.

### 5.2 Sprint 6 Packets (Beta Product Assembly & Dogfood)
- **Lane SA (Senior A - GATE, Cx 5):** Runtime Composition Root & Dogfood Execution (`vanguard/packages/runtime/root.py`). Wire all components, execute end-to-end bug fix on `vg-code-default`, and verify terminal state emission.
- **Lane SB (Senior B - GATE, Cx 4):** Descriptor-Bound Approval Mediation (`vanguard/packages/runtime/governance/`). Connect `ProcessEngine` approval points to the kernel dispatch pipeline; verify `MF-GOV-001` (tampered diff rejection).
- **Lane DC (Developer C - FAST, Cx 3):** Latency & Telemetry Instrumentation (`vanguard/packages/runtime/telemetry.py`). Instrument p95 time-to-first-token, time-to-first-effect, and ledger commit latency against `slice-findings.md` baselines.
- **Lane DD (Developer D - FAST, Cx 3):** Interactive Ink TUI Approval & Correction UX (`vanguard/clients/cli/src/tui.tsx`). Implement interactive diff approval screen and single-keystroke reason code capture prompt.

---

## CHAPTER 6: Summary of Governance, Quality & SOTA Architectural Rules

To guarantee zero architectural debt, high performance, and long-term maintainability, the following non-negotiable rules govern Phase 2:

1. **Strict Dependency Lattice:**
   - No module in `agency/` or `runtime/governance/` may import concrete `adapters/`.
   - `clients/cli/` must remain strictly outside `vanguard/packages/` and communicate exclusively via the `RuntimeClient` interface.
2. **Universal Recording, Scoped Mediation:**
   - All effects (`pure`, `observation`, `privileged`) are recorded in the immutable ledger.
   - Only `privileged` sinks require capability grants and traverse the kernel.
3. **No Cognitive Vocabulary in Code:**
   - Linter forbids `plan`, `debug`, `reflect`, `architect` as class or function identifiers in `vanguard/packages/agency/`. Cognitive strategies exist solely as data artifacts in the manifest graph.
4. **No Model Dependencies in Governance:**
   - The compliance and approval state machine (`ProcessEngine`) must execute and resume purely from ledger state without invoking LLMs.
5. **Exterior Evaluation Invariant:**
   - An episode must never evaluate its own outcome. Evaluation is performed strictly by an exterior evaluator observing terminal ledger events across an OS security boundary.
6. **100% Contract Test Gate:**
   - No PR merges into `main` without citing an active `req_id` and passing all bound contract, property, and must-fail tests.

---

## Concluding Assessment & Readiness

The Vanguard GTS foundation is in an exceptional state. The core trust spine, capability algebra, mathematical wire contracts, and package lattices are solid, fully verified, and backed by comprehensive must-fail suites.

With the roadmap, technical debt remediation, and four-lane parallel allocation defined in this review, the program is fully prepared to execute **Phase 2 (Sprints 5 & 6)** and deliver the **Lightweight Beta MVP**.
