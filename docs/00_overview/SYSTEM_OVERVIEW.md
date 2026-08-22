# DIRECTOR TODO — LOCK CONCEPTS V2

**Independent Companion Audit & Master Briefing**

| Field | Value |
|---|---|
| **Prepared for** | Engineering Director / Chief Architect |
| **Prepared by** | Senior Principal Systems Engineer (independent audit lane) |
| **Objective** | Authoritative navigational map, architectural index, and executive decision mandate for locking **v0.6.1**, **v0.6.2**, and **v0.7.0** |
| **Date** | 2026-08-21 |
| **Baseline** | `main` @ `afa8e2a` — verified on disk during this audit |
| **Status** | Ready for Director review and determination |
| **Relationship to V1** | Independent companion to `DIRECTOR_TODO_LOCK_CONCEPTS.md` (V1 — consolidated out of the working tree at the ADR-0075 review-corpus cleanup; recoverable at commit `b36481c`). V1 was the executive summary; **V2 is the verified audit that superseded it and is retained here**. See [§7.4](#74-corrections-to-v1) for the specific corrections V2 made to V1. |

> **Authority note.** This document is **advisory**. It amends nothing. Law remains
> [`docs/SPEC.md`](../SPEC.md) → [`docs/05_adr/`](../05_adr/) → [`docs/04_annex/`](../04_annex/).
> Every claim below marked **[VERIFIED]** was re-executed against the working tree during this
> audit; every claim marked **[CITED]** is reproduced from a document and not independently
> re-tested.

---

## Table of Contents

0. [Executive Fast Briefing (5-Minute Birds-Eye Summary)](#0-executive-fast-briefing-5-minute-birds-eye-summary)
1. [Executive Mandate & Action Instructions](#1-executive-mandate--action-instructions)
2. [System Architecture — The Clean Triad, Three Planes, and A-B-C-D](#2-system-architecture--the-clean-triad-three-planes-and-a-b-c-d)
3. [Complete Repository Tree & Subsystem Directory](#3-complete-repository-tree--subsystem-directory)
4. [Index of Reviews & Research Literature](#4-index-of-reviews--research-literature)
5. [Neutral Analysis of Open Architectural Tensions](#5-neutral-analysis-of-open-architectural-tensions)
6. [Macro Roadmap Ladder & Director Decision Checklist](#6-macro-roadmap-ladder--director-decision-checklist)
7. [Audit Findings — What This Pass Verified](#7-audit-findings--what-this-pass-verified)

---

## 0. Executive Fast Briefing (5-Minute Birds-Eye Summary)

> [!TIP]
> **Reading Guide for the Director:**  
> • **Need the 5-minute birds-eye orientation?** Read this Section 0 and [§1](#1-executive-mandate--action-instructions) + [§6.3](#63-director-decision-checklist).  
> • **Need the verified, deep forensic audit?** Continue through [§2](#2-system-architecture--the-clean-triad-three-planes-and-a-b-c-d) through [§7](#7-audit-findings--what-this-pass-verified).

### 0.1 The System in 60 Seconds
* **What it is today:** A Python-first, domain-blind recursive agency substrate built on a strict separation of three planes: an unnegotiable Trusted Computing Base reference monitor ($\le 1438$ LOC, currently 1,365 LOC), an immutable SQLite WAL event-sourced state plane (`State = fold(events)`), and an exterior Ed25519-signed evaluation daemon (UID 10002) in a rootless sandbox (UID 10001)—currently proving its trust spine on an autonomous software-engineering proving ground (`vg` CLI).
* **What it becomes in the future:** A universal multi-agent operating ecosystem that compiles declarative manifests into dynamic **Named Component Graphs** (expressing debate, tree search, reflection loops, and swarms with zero core changes), exposes capability-mediated `agent.spawn` delegation, and harvests rich, unforgeable execution trajectories to drive active inference, continuous skill synthesis, and safe meta-cognitive reinforcement learning (Waves 5–10).

### 0.2 The Clean Triad & 3 Planes
```text
┌───────────────────────────────────────────────────────────────────────────────┐
│                              THE CLEAN TRIAD                                  │
│                                                                               │
│  1. THE LAW (WHAT)        ──► docs/SPEC.md (+ docs/04_annex/)                 │
│  2. THE DECISIONS (WHY)   ──► docs/05_adr/ (Immutable, append-only records)   │
│  3. THE EXECUTION (HOW)   ──► docs/03_sprints/sprint_active.md & 02_roadmap   │
└───────────────────────────────────────────────────────────────────────────────┘
```
1. **Decision Plane (Volatile / Reconstructible):** S0–S12 Reference Monitor in [`kernel/`](../../vanguard/packages/kernel/). Monotonic capability attenuation and 6D typed leases.
2. **State Plane (Immutable / Event-Sourced):** [`adapters/stores/event_store.py`](../../vanguard/packages/adapters/stores/event_store.py) (SQLite WAL `PRAGMA journal_mode = WAL`). `State = fold(events)` reconstructible cold from disk.
3. **Evidence Plane (Exterior / Unreachable):** [`adapters/evaluators/daemon.py`](../../vanguard/packages/adapters/evaluators/daemon.py) (UID 10002). Ed25519-signed verdicts bound to request nonces.

### 0.3 The A-B-C-D Operating Foundation
* **A — Authority (Kernel):** Descriptor-bound grants, monotonic attenuation, typed 6D budgets ($\le 1438$ LOC TCB). *Status: Solid & Generic (1,365 LOC).*
* **B — Bundle (Composition):** Manifest $\to$ `FrozenHarness(D_H)` compiler. *Status: Currently a fixed-slot template; evolving to a Component Graph.*
* **C — Corpus (Evidence):** SQLite WAL `fold(events)` emitting `mhf.trajectory/1`. *Status: Schema-valid, but requires non-zero cost wiring.*
* **D — Digest (Identity):** Cryptographic identity trinity ($D_H \neq D_R \neq D_X$). *Status: Locked & Generic.*

### 0.4 Fast Master Index of Key Files
| Category | File Path | Role / Content |
|---|---|---|
| **The Law** | [`docs/SPEC.md`](../SPEC.md) | Pure RFC-2119 Normative Specification for MHF v1. |
| **Decisions** | [`docs/05_adr/INDEX.md`](../05_adr/INDEX.md) | Immutable records (ADRs 0069–0076 lock the foundation). |
| **Active Sprint** | [`docs/03_sprints/sprint_active.md`](../03_sprints/sprint_active.md) | Single living execution board and milestone ladder. |
| **TCB Kernel** | [`vanguard/packages/kernel/`](../../vanguard/packages/kernel/) | 9 files, 1365 LOC logical (threshold $\le 1438$). 100% green. |
| **Verified Gaps** | [`002 Gap Register`](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md) | Falsifiers F-01 through F-21 and wave exit gates. |
| **Generality Review** | [`005 Generality Review`](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/005_V061_SUBSTRATE_GENERALITY_REVIEW.md) | Component graph and mediated `agent.spawn` blueprint. |
| **SOTA Research** | [`RESEARCH_k3_harness-suggestion.md`](../06_references/RESEARCH_k3_harness-suggestion.md) | SOTA Plan formulating the A-B-C-D operating model. |

---

## 1. Executive Mandate & Action Instructions

### 1.1 Your authority

> [!IMPORTANT]
> **You hold 100% decision authority** over the architecture, scope, milestone sequence, and release
> strategy for **v0.6.1**, **v0.6.2**, and **v0.7.0**.
>
> Everything under [`docs/07_reviews/`](../07_reviews/) and [`docs/06_references/`](../06_references/)
> is **advisory input, option space, and historical evidence — not unquestioned law.** The reviews
> themselves say so: `005` is stamped *"Advisory. Does not amend SPEC or any ADR"*, and SPEC's
> authority-on-conflict clause explicitly ranks `docs/07_reviews/` last, adding that
> **"no ticket may cite them as a requirement."**

Your instrument for making a decision binding is a **new append-only ADR numbered `0077`+**. ADRs
`0069`–`0076` are append-only and may not be silently edited; a new ADR that narrows an old one must
name it and give evidence ([`ADR-0086`](../05_adr/0086-historical-adr-working-tree-consolidation.md)).

### 1.2 What is already settled and should NOT be relitigated here

These carry a Director signature already ([`ADR-0075`](../05_adr/0075-director-review-v060-approved-wave0-authorized.md)):
the packages lattice as canonical, `spawn` as the sole delegation primitive, the three planes, the
identity trinity, wire-first plugins, the exterior judge, sequential execution (I-11), and the
refusal list in [`SPEC.md` §9](../SPEC.md). Reopening any of them requires **reversal evidence**,
which each ADR states in its own text — not preference.

### 1.3 What this document asks you to decide

Six live scope questions, all reaching you because they are **shape decisions that get expensive
after M-4**, not because they are blocked on engineering. They are laid out neutrally in
[§5](#5-neutral-analysis-of-open-architectural-tensions) and reduced to a checklist in
[§6.3](#63-director-decision-checklist).

### 1.4 How to read the evidence

| If you want… | Read |
|---|---|
| The law, in one file | [`docs/SPEC.md`](../SPEC.md) |
| Why each decision was made | [`docs/05_adr/INDEX.md`](../05_adr/INDEX.md) |
| What is unfinished, with named falsifiers | [`002` gap register](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md) §4 |
| What is being worked on right now | [`sprint_active.md`](../03_sprints/sprint_active.md) |
| The strongest independent critique | [`005` Substrate Generality Review](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/005_V061_SUBSTRATE_GENERALITY_REVIEW.md) §3 |
| The failure this whole programme exists to prevent | [`VANGUARD_V060_FORENSIC_DISCOVERY.md`](../07_reviews/VANGUARD_V060_FORENSIC_DISCOVERY.md) §1 |

---

## 2. System Architecture — The Clean Triad, Three Planes, and A-B-C-D

### 2.1 The Clean Triad — where each kind of statement lives

```text
┌───────────────────────────────────────────────────────────────────────────────┐
│                              THE CLEAN TRIAD                                  │
│                                                                               │
│  1. THE LAW        (WHAT MUST BE TRUE)   ──►  docs/SPEC.md + docs/04_annex/   │
│     RFC-2119 binding. The ONLY place MUST/SHALL/SHOULD are normative.         │
│                                                                               │
│  2. THE DECISIONS  (WHY IT IS SO)        ──►  docs/05_adr/  (0000 … 0076)     │
│     Append-only. A newer ADR wins by citation, never by silent edit.          │
│                                                                               │
│  3. THE EXECUTION  (HOW / WHEN / WHO)    ──►  docs/02_roadmap/ +              │
│                                               docs/03_sprints/                │
│     Boards and plans. May never contradict (1) or (2).                        │
└───────────────────────────────────────────────────────────────────────────────┘
                                     ▲
                                     │  advisory only — never citable as requirement
              docs/07_reviews/   ────┘
              docs/06_references/
```

**Authority on conflict**, verbatim from SPEC's header: `SPEC.md` → `docs/05_adr/` → GAMMA (`001`) →
the `002` register → `docs/02_roadmap/milestones.md` → `docs/03_sprints/sprint_active.md` →
git-history archive and `docs/07_reviews/`.

### 2.2 The Three Planes of Responsibility

The organizing insight is that **who decides**, **who records**, and **who judges** must be three
different things with three different reachability properties.

```text
╔═══════════════════════════════════════════════════════════════════════════════════╗
║  DECISION PLANE — volatile, reconstructible                                       ║
║  vanguard/packages/kernel/  ·  vanguard/packages/agency/                          ║
║                                                                                   ║
║   S0 ENTER → S1 PARSE → S2 RESOLVE → S3 DESCRIBE → S4 CLASSIFY → S5 AUTHORIZE     ║
║   → S6 GRANT → S7 RESERVE → [ S8 VERIFY → S8a INTENT(fsync) → S9 DISPATCH         ║
║   → S10 COMMIT ] → S11 RELEASE → S12 EMIT                                         ║
║                                                                                   ║
║   Decides: who acts, when, under what lease, with what capability.                 ║
║   Holds NO truth. Everything it concludes must become an event or it did not       ║
║   happen (Axiom A-3).                                                             ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
                                       │  Decision → DurableEvent
                                       ▼
╔═══════════════════════════════════════════════════════════════════════════════════╗
║  STATE PLANE — immutable, event-sourced, the ONLY source of truth                 ║
║  vanguard/packages/domain/ledger/  ·  adapters/stores/event_store.py              ║
║                                                                                   ║
║   State = fold(events).  SQLite WAL + FULL sync. Per-Project hash chain           ║
║   (prev_digest), monotonic seq, JCS-canonical JSON, SHA-256 content digest.       ║
║   project_id is the consistency unit — total order holds inside a Project.        ║
║                                                                                   ║
║   Proof standard (I-4): a COLD fold from disk in a FRESH process, structurally     ║
║   diffed against live terminal state. Folding an in-memory list twice is NOT it.  ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
                                       │  terminal event observed
                                       ▼
╔═══════════════════════════════════════════════════════════════════════════════════╗
║  EVIDENCE PLANE — exterior, unreachable from the judged                           ║
║  adapters/evaluators/daemon.py (UID 10002)  ·  runtime/evaluator_gateway.py       ║
║                                                                                   ║
║   Separate OS identity, separate mount namespace, Ed25519 signing keys that       ║
║   never enter any plugin cell. Verdicts are request-bound (nonce + subject +      ║
║   oracle). The gateway is the SOLE legal writer of VerdictRecorded.               ║
║                                                                                   ║
║   Worker runs UID 10001 (rootless bwrap). K-40 as AMENDED by ADR-M0-08: the       ║
║   judge sits OUTSIDE the worker perimeter, not co-located inside it.              ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
```

**Why this is the moat.** The separability thesis — *"what solved it must be separable, and the
judge must be unreachable from the judged"* — is not a security nicety. It is the precondition for
any future training signal being un-gameable **by construction** rather than by policy. Collapsing
these three planes into one execution object is what makes a system unable to do science about
itself.

### 2.3 The A-B-C-D Operating Foundation

Four load-bearing subsystems, each with its verified state as of this audit.

| | Pillar | Mechanism | Owner on disk | State **[VERIFIED]** |
|---|---|---|---|---|
| **A** | **Authority** | Descriptor-bound grants, monotonic attenuation, typed 6D leases, S0–S12 reference monitor | [`kernel/`](../../vanguard/packages/kernel/) | **Solid & generic.** 1365 logical LOC against a 1438 ceiling. Implements KERNEL.md §2 rule-for-rule. |
| **B** | **Bundle** | `manifest → compose() → FrozenHarness(D_H)` | [`runtime/compose.py`](../../vanguard/packages/runtime/compose.py), [`domain/artifacts/manifest.py`](../../vanguard/packages/domain/artifacts/manifest.py) | **Fixed-slot template.** Works; expresses one agent shape. The open tension — see [§5.1](#51-t-1--manifest-shape--fixed-slots-vs-named-component-graph). |
| **C** | **Corpus** | `fold(events)` → SQLite WAL → `mhf.trajectory/1` at `EpisodeCompleted` | [`adapters/stores/event_store.py`](../../vanguard/packages/adapters/stores/event_store.py), [`runtime/trajectory.py`](../../vanguard/packages/runtime/trajectory.py) | **Ledger strong; trajectory hollow.** Cold replay is real. Trajectory emits a zero cost vector — see [§5.4](#54-t-4--trajectory-quality--the-born-hollow-corpus-g1--nova-1). |
| **D** | **Digest** | Identity trinity `D_H` ≠ `D_R` ≠ `D_X`, all bytes via RFC 8785 JCS | [`domain/canonicalisation/jcs.py`](../../vanguard/packages/domain/canonicalisation/jcs.py) | **Locked & generic.** `D_H` covers prompt, ceiling, approval policy, and model routes — not just plugin refs. |

**Identity trinity, restated precisely** (this is the most commonly misunderstood piece):

```text
D_H  = JCS digest of the COMPLETE behaviour-affecting composition
       { resolved plugin refs + digests, system prompt, capability ceiling,
         approval policy, model routes }
       Two harnesses differing ONLY in system prompt MUST NOT share D_H.

D_R  = D_H + runtime + environment + model identity + oracle identity
       (one execution)

D_X  = D_R + dataset + protocol
       (one experiment cell)
```

These are **the denominators of every future measurement**. Collapsing them is the mistake that
permanently forecloses self-improvement, because every A-vs-B comparison built on a collapsed
identity is invalid and cannot be repaired retroactively.

### 2.4 The universal turn loop

```text
observe → propose → authorize → effect → receipt → evaluate → (reflect)*
```

`reflect` is a Phase-2 outer-loop stage, not implemented in v0.6. The loop is **mechanism, not
plugin** — algorithms differ in *what they propose and when they spawn*, never in whether effects
get authorized. `005` §W3 asks that this claim be published **with a falsifier** rather than left
implicit; see [§5.6](#56-t-6--the-loop-as-mechanism--publish-the-claim-with-its-falsifier).

---

## 3. Complete Repository Tree & Subsystem Directory

### 3.1 Full repository map **[VERIFIED]**

```text
Aether-D-System/
│
├── vanguard/                              ★ CANONICAL PRODUCTION CODEBASE (ADR-0069)
│   ├── packages/                          Hexagonal production lattice — CI SUBJECT OF RECORD
│   │   ├── domain/                        Pure stdlib value objects (imports nothing in-repo)
│   │   ├── ports/                         Abstract interfaces (imports domain/ only)
│   │   ├── kernel/                        TRUSTED COMPUTING BASE — 1365 / 1438 logical LOC
│   │   ├── agency/                        Recursive turn engine, context compiler, manifests
│   │   ├── runtime/                       Composition root, session, governance, ledger bridge
│   │   ├── adapters/                      Models · evaluators · sandbox · stores · environment
│   │   └── apps/                          Reserved client-lattice slot (currently empty)
│   └── clients/
│       ├── cli/                           TypeScript/React/Ink interactive TUI (`vg`)
│       └── client-core/                   Shared TS client contract + adapters
│
├── layer0/                                ⚠ CONVERGENCE FORK — SHRINKING, dies at 3.1
│   ├── compose/compiler.py                Manifest → FrozenHarness digest shape (to absorb)
│   ├── registry/                          Lifecycle FSM + isolation broker (to absorb, Wave 3)
│   │   ├── lifecycle.py  broker.py  isolation.py  sandbox.py  validator.py  grants.py  worker.py
│   ├── events/                            emitter · envelope · store · taxonomy (partial残)
│   └── README.md                          Absorption map
│     NOTE: kernel/, scheduler/, spi/ and events/{selectors,canonical,fold,blob}.py
│           were DELETED at 2.2-B. The F1 unsigned-"pass" defect died with them.
│
├── packs/                                 DOMAIN PACKS (data, not core)
│   └── code-default/                      Domain Pack #1 — coding
│       ├── harness.yaml                   The compile target (mhf.harness/1)
│       ├── plugin.yaml  system-prompt.txt  approval-policy.json  context-policy.json
│       ├── plugins/                       8 plugin manifests (fs, ast-patch, terminal, index,
│       │                                  context, memory, planner, evaluation)
│       ├── toolkits/                      ast_patch · repo_map · terminal_runner · fs_toolkit
│       ├── planners/single_planner.py     Drive-until-green planner
│       └── oracles/                       gate.py + registry.json  (F-20 artifact home)
│
├── benchmarks/                            UNIFIED BENCHMARK FRAMEWORK
│   ├── run.py  bench.py  build.py  diff.py  guard.py
│   ├── swe_bench/                         Real-world GitHub issue resolution
│   ├── greenfield/                        dogfood-01/02/03 + API/webapp construction
│   └── datalog_engine/                    Frontier deductive query-engine task
│
├── test/                                  TEST SUITE — 23 directories, ~1176 collected
│   ├── kernel/ (8)          contracts/ (10)     agency/ (12)      runtime/ (40)
│   ├── adapters/ (16)       packs/ (3)          registry/ (3)     security/ (4)
│   ├── trust/ (1)           falsifiers/ (1)     lab/ (16)         tools/ (14)
│   ├── integration/ (5)     governance/ (1)     benchmarks/ (5)   layer0/ (advisory)
│   ├── broken/fixtures/     ← 30+ INTENTIONAL violations proving linters fail closed
│   └── support/  fixtures/  apps/
│
├── tools/                                 STATIC ENFORCEMENT & INSTRUMENTS
│   ├── linters/                           15 checkers (see §3.4)
│   ├── codegen/generate_types.py          Schema → dataclasses (A-4; `--check` gates CI)
│   ├── common/                            repo_paths · simple_yaml · run_broken_tests
│   ├── telemetry/  substrate_visualizer/  Measurement apparatus — NEVER imported by kernel (D-40)
│   ├── 001_LLM_API_ROUTER/                LAR — router probe project
│   └── 002_LLM_API_MOCK/                  LAM — deterministic mock model server + answer bank
│
├── schemas/
│   ├── mhf/                               effect_request · event_envelope · harness_manifest
│   │                                      · spi_payloads · trajectory   (mhf.*/1 — the type source)
│   └── v4/vectors/                        Golden conformance vectors, 13 families, valid+invalid
│
├── containers/                            worker.Dockerfile (UID 10001) · evaluator.Dockerfile
│                                          (UID 10002) · manifest.json
│
└── docs/
    ├── SPEC.md                        ★ THE LAW — sole living normative spec (RFC-2119)
    ├── README.md                        Documentation navigation
    ├── 01_executive/vision.md           Executive vision
    ├── 02_roadmap/                      milestones.md (M-0…M-10) · backlog.md (pointer)
    ├── 03_sprints/
    │   ├── sprint_active.md           ★ THE ONLY LIVING BOARD
    │   ├── plans/                       wave1_trust_spine · wave2_convergence
    │   │                                · wave3_extensibility · wave4_foundation_e2e
    │   └── _delete_guidelines.md
    ├── 04_annex/                      ★ NORMATIVE ANNEXES
    │   ├── KERNEL.md                    Security constitution — K-01…K-49, S0–S12, F-01…F-25,
    │   │                                AT-01…AT-12, threat model T-01…T-08
    │   └── MEASUREMENT.md               Measurement constitution
    ├── 05_adr/                          77 ADRs + 13 ADR-M0 + INDEX + DEFERRED_REJECTED
    │                                    + DRIFT_REGISTER_v045
    ├── 06_references/                   12 research documents (advisory — §4.2)
    ├── 07_reviews/                      8 review documents (advisory — §4.1)
    ├── 08_diagrams/                     4 SVGs (three planes, tier continuum, v060→v061, DPO loop)
    └── 08_workflows/                    (empty)
```

### 3.2 `vanguard/packages/` — module-by-module inventory **[VERIFIED]**

```text
                 ┌──────────────────────────────────────────────────────────────┐
                 │  domain ◄── ports ◄── kernel ◄── agency ◄── runtime ──► adapters │
                 │                                                    └──► apps   │
                 │  adapters MUST NEVER import kernel/ or agency/                │
                 └──────────────────────────────────────────────────────────────┘
                       enforced every commit by tools/linters/check_boundaries.py
```

#### `domain/` — pure stdlib value objects, imports nothing in-repo

| Module | LOC | Single responsibility |
|---|---:|---|
| [`canonicalisation/jcs.py`](../../vanguard/packages/domain/canonicalisation/jcs.py) | 226 | RFC 8785 JCS canonicaliser — **the sole byte source** for every digest and every signature |
| [`canonicalisation/digest.py`](../../vanguard/packages/domain/canonicalisation/digest.py) | 24 | SHA-256 over canonical bytes |
| [`ledger/events.py`](../../vanguard/packages/domain/ledger/events.py) | 471 | `EVENT_KINDS` — the closed catalog (56 kinds) + envelope types |
| [`ledger/reducer.py`](../../vanguard/packages/domain/ledger/reducer.py) | 654 | Deterministic `fold(events) → LedgerState`. The `unknown_events` tail is the honesty channel |
| [`ledger/state.py`](../../vanguard/packages/domain/ledger/state.py) | 297 | `LedgerState` + `to_canonical_dict()` (feeds the state digest) |
| [`ledger/reconciliation.py`](../../vanguard/packages/domain/ledger/reconciliation.py) | 86 | Undeterminable-effect reconciliation (F-22) |
| [`ledger/session_projection.py`](../../vanguard/packages/domain/ledger/session_projection.py) | 94 | Read-model projection for sessions |
| [`selectors/resource_selector.py`](../../vanguard/packages/domain/selectors/resource_selector.py) | 501 | **The one selector algebra.** Total, fail-closed. Unknown pair ⇒ deny (K-48) |
| [`primitives/primitives.py`](../../vanguard/packages/domain/primitives/primitives.py) | 257 | `Principal`, `Digest`, `Reservation`, `SinkClass`, core value types |
| [`artifacts/manifest.py`](../../vanguard/packages/domain/artifacts/manifest.py) | 172 | `FrozenHarness` / `D_H` compile output |
| [`artifacts/graph.py`](../../vanguard/packages/domain/artifacts/graph.py) | 212 | Provenance DAG projections |
| [`artifacts/skill_index.py`](../../vanguard/packages/domain/artifacts/skill_index.py) | 76 | Skill-card index |
| [`evidence/claim.py`](../../vanguard/packages/domain/evidence/claim.py) | 373 | `EvidenceClaim` + hedge fields (ADR-0068) |
| [`wire/contracts.py`](../../vanguard/packages/domain/wire/contracts.py) | 362 | Wire contract types |
| [`wire/types_gen.py`](../../vanguard/packages/domain/wire/types_gen.py) | 368 | **GENERATED** from `schemas/mhf/` — hand-editing fails CI (F-13) |
| [`wire/jsonrpc.py`](../../vanguard/packages/domain/wire/jsonrpc.py) | 64 | JSON-RPC 2.0 line-delimited codec (absorbed from `layer0/` at 2.1-A) |
| [`wire/result.py`](../../vanguard/packages/domain/wire/result.py) | 34 | `Result[T]` |

#### `ports/` — abstract interfaces, imports `domain/` only

| Module | LOC | Single responsibility |
|---|---:|---|
| [`spi.py`](../../vanguard/packages/ports/spi.py) | 125 | **The five frozen SPIs** — `IPlanner`, `IMemoryEngine`, `IToolkit`, `IContextManager`, `IEvaluationGate` (ADR-M0-03; a sixth requires a design review) |
| [`kernel.py`](../../vanguard/packages/ports/kernel.py) | 75 | `KernelPort` — the single dispatch entry |
| [`environment.py`](../../vanguard/packages/ports/environment.py) | 173 | Workspace/environment port |
| [`sandbox.py`](../../vanguard/packages/ports/sandbox.py) | 83 | `ISandbox` |
| [`event_store.py`](../../vanguard/packages/ports/event_store.py) | 82 | `IEventStore` |
| [`evaluator.py`](../../vanguard/packages/ports/evaluator.py) | 65 | `EvaluatorPort` — request only, never render |
| [`determinism.py`](../../vanguard/packages/ports/determinism.py) | 50 | `ClockPort` / `RandomPort` (replay substitution) |
| [`index.py`](../../vanguard/packages/ports/index.py) | 52 | Repo-index port |
| [`model.py`](../../vanguard/packages/ports/model.py) | 44 | `ModelPort` / `IModelProvider` |
| [`blob_store.py`](../../vanguard/packages/ports/blob_store.py) | 39 | `IBlobStore` — `write→fsync→emit(digest)` ordering (D-19) |

#### `kernel/` — the Trusted Computing Base ⚠ **TCB BUDGET: 1365 / 1438 logical LOC**

| Module | Logical LOC | Single responsibility |
|---|---:|---|
| [`dispatch.py`](../../vanguard/packages/kernel/dispatch.py) | **364** | The S0–S12 pipeline. **The only path from a model output to an effect** (AT-01). Enforces K-04 (resolve before lease), K-05 (verify at point of effect), K-06 (release before emit), K-07 (overruns debited), K-47/S8a (durable intent fsynced before dispatch) |
| [`grants.py`](../../vanguard/packages/kernel/grants.py) | 201 | Descriptor-bound, single-use grants; MAC across process boundaries (K-18…K-22) |
| [`attenuation.py`](../../vanguard/packages/kernel/attenuation.py) | 171 | Monotonic narrowing. **No silent intersection** (K-26); out-of-scope ⇒ alertable denial (K-27) |
| [`budget.py`](../../vanguard/packages/kernel/budget.py) | 139 | Typed 6D algebra: additive `{usd_micros, tokens, bytes, millis}` vs structural `{depth, turns}`. **Sibling depths are not summed** |
| [`model.py`](../../vanguard/packages/kernel/model.py) | 137 | Kernel-internal request/decision models |
| [`provenance.py`](../../vanguard/packages/kernel/provenance.py) | 110 | The authority predicate. Justifying spans accumulate **monotonically** (K-33) — the control that was documented, tested, and inert in the prototype |
| [`policy.py`](../../vanguard/packages/kernel/policy.py) | 106 | `policy.authorize(AuthorityRequest)` at S5 |
| [`classifier.py`](../../vanguard/packages/kernel/classifier.py) | 96 | Capability-widening classifier at S4. **A call, never a constant** (K-08); raises ⇒ treated as widening (F-05) |
| [`__init__.py`](../../vanguard/packages/kernel/__init__.py) | 41 | Public kernel surface |

> **Why the ceiling matters and what it does not mean.** [`KERNEL.md` §1.1](../04_annex/KERNEL.md)
> is explicit: *"A ceiling on the policy kernel is a tripwire, not a guarantee."* The annex has
> already **struck** the LOC number from its normative prose (AP-8: a LOC ceiling is a Goodharted
> metric that rewards density in exactly the code that must be clearest) and names a replacement
> triple — mutation score on kernel+reducers, % of controls with production call-site proofs, and
> event-kind emission coverage. **That replacement does not exist yet.** Until it does,
> `check_tcb_budget.py` remains the living gate. This dual state is deliberate (ADR-M0-05), and it
> is a standing Director decision surface.

#### `agency/` — the recursive turn engine

| Module | LOC | Single responsibility |
|---|---:|---|
| [`episode/engine.py`](../../vanguard/packages/agency/episode/engine.py) | 693 | `EpisodeEngine` — the turn loop and `spawn()`. **Today `spawn` is engine-owned**; see [§5.2](#52-t-2--spawning--engine-owned-vs-capability-mediated-agentspawn) |
| [`episode/state.py`](../../vanguard/packages/agency/episode/state.py) | 237 | Episode FSM state |
| [`context/compiler.py`](../../vanguard/packages/agency/context/compiler.py) | 290 | Prefix-stable prompt assembly; L1–L3 frozen at composition |
| [`context/compaction.py`](../../vanguard/packages/agency/context/compaction.py) | 256 | Structured compaction under token pressure |
| [`context/layers.py`](../../vanguard/packages/agency/context/layers.py) | 235 | L1–L5 context layer model |
| [`manifests/loader.py`](../../vanguard/packages/agency/manifests/loader.py) | 259 | YAML → harness parse (converges to one parser at 3.2-C) |
| [`manifests/discovery.py`](../../vanguard/packages/agency/manifests/discovery.py) | 106 | Manifest discovery across scan paths |
| `manifests/vg-*/` | — | 6 shipped manifests: `vg-code-default`, `vg-code-claude-shaped`, `vg-code-opencode-shaped`, `vg-code-swe-mini`, `vg-shell-only`, `vg-table-default` |

#### `runtime/` — composition root and system services

| Module | LOC | Single responsibility |
|---|---:|---|
| [`root.py`](../../vanguard/packages/runtime/root.py) | **126** | Composition root. Was a ~1418-LOC god object; **split in place at 2.2-C** into the three below |
| [`compose.py`](../../vanguard/packages/runtime/compose.py) | 390 | `Runtime.compose` — manifest → `FrozenHarness(D_H)`, ceiling intersection stored |
| [`session.py`](../../vanguard/packages/runtime/session.py) | 646 | `HarnessSession` lifecycle. Exceeds the plan's ~500 guidance; accepted as one cohesive class |
| [`wiring.py`](../../vanguard/packages/runtime/wiring.py) | 347 | Dependency wiring |
| [`ledger_emitter.py`](../../vanguard/packages/runtime/ledger_emitter.py) | 331 | **The single authorized ledger writer.** Holds `PRIVILEGED_KIND_OWNERS` — the writer-authority table |
| [`evaluator_gateway.py`](../../vanguard/packages/runtime/evaluator_gateway.py) | 58 | **Sole legal writer of `VerdictRecorded`.** Refuses anything without a bound, signed body |
| [`evaluation_listener.py`](../../vanguard/packages/runtime/evaluation_listener.py) | 129 | Observes terminal events, requests judgment |
| [`trajectory.py`](../../vanguard/packages/runtime/trajectory.py) | 113 | `mhf.trajectory/1` builder. ⚠ **Emits `_ZERO_COST` at lines 53 and 75** — [§5.4](#54-t-4--trajectory-quality--the-born-hollow-corpus-g1--nova-1) |
| [`governance/approvals.py`](../../vanguard/packages/runtime/governance/approvals.py) | 565 | Ed25519 approval service; `ApprovalResolved` is ledgered (fixes D-13) |
| [`governance/engine.py`](../../vanguard/packages/runtime/governance/engine.py) | 97 | Governance rule engine |
| [`governance/definitions.py`](../../vanguard/packages/runtime/governance/definitions.py) | 93 | Governance definitions |
| [`ledger/projections.py`](../../vanguard/packages/runtime/ledger/projections.py) | 339 | Read-model projections |
| [`ledger/recovery.py`](../../vanguard/packages/runtime/ledger/recovery.py) | 278 | Crash recovery: scan `EffectStarted` without terminal ⇒ undeterminable ⇒ probe |
| [`lab_driver.py`](../../vanguard/packages/runtime/lab_driver.py) | 461 | Lab measurement driver (promotion deferred) |
| [`service/service.py`](../../vanguard/packages/runtime/service/service.py) | 531 | UDS RuntimeService daemon (ADR-0062) |
| [`service/server.py`](../../vanguard/packages/runtime/service/server.py) | 177 | Socket server |
| [`service/inbox.py`](../../vanguard/packages/runtime/service/inbox.py) | 202 | Inbox/outbox — idempotent commands (D-17) |
| [`tier_escalation.py`](../../vanguard/packages/runtime/tier_escalation.py) | 236 | Free→Cheap→Frontier escalation on `verdict_fail` (the D-41 salvage) |
| [`model_selection.py`](../../vanguard/packages/runtime/model_selection.py) | 224 | Route selection |
| [`autonomous_grant.py`](../../vanguard/packages/runtime/autonomous_grant.py) | 162 | Autonomous-mode grant policy |
| [`repair.py`](../../vanguard/packages/runtime/repair.py) | 144 | Repair rounds |
| [`explain.py`](../../vanguard/packages/runtime/explain.py) | 134 | Decision explanation |
| [`scoring.py`](../../vanguard/packages/runtime/scoring.py) | 128 | Outcome scoring |
| [`provider_health.py`](../../vanguard/packages/runtime/provider_health.py) | 117 | Provider health probes |
| [`determinism.py`](../../vanguard/packages/runtime/determinism.py) | 101 | Clock/random injection for replay |
| [`session_log.py`](../../vanguard/packages/runtime/session_log.py) | 220 | Session log |
| [`skill_index.py`](../../vanguard/packages/runtime/skill_index.py) | 94 | Skill index runtime |
| [`outcome_labels.py`](../../vanguard/packages/runtime/outcome_labels.py) | 65 | Outcome labels |
| [`task_sets.py`](../../vanguard/packages/runtime/task_sets.py) | 61 | Task set loading |
| [`telemetry.py`](../../vanguard/packages/runtime/telemetry.py) | 50 | Telemetry emission |

#### `adapters/` — concrete external integrations (imports `domain/` + `ports/` only)

| Module | LOC | Single responsibility |
|---|---:|---|
| [`evaluators/daemon.py`](../../vanguard/packages/adapters/evaluators/daemon.py) | 261 | **UID 10002 exterior evaluator daemon.** Binds verdicts to request/subject/oracle/nonce |
| [`evaluators/signing.py`](../../vanguard/packages/adapters/evaluators/signing.py) | 58 | `VerdictSigner` — Ed25519 over JCS bytes |
| [`evaluators/isolated.py`](../../vanguard/packages/adapters/evaluators/isolated.py) | 298 | Isolated evaluation execution |
| [`evaluators/gate.py`](../../vanguard/packages/adapters/evaluators/gate.py) | 132 | Reads ledgered verdicts; signature verification is **the reader's job**, not the reducer's |
| [`evaluators/client.py`](../../vanguard/packages/adapters/evaluators/client.py) | 140 | UDS client to the daemon |
| [`evaluators/suites/`](../../vanguard/packages/adapters/evaluators/suites/) | — | Preregistered oracles (bug-001/002/003, greenfield webapp, task 01–03) |
| [`sandbox/worker.py`](../../vanguard/packages/adapters/sandbox/worker.py) | 242 | **UID 10001 worker.** `setrlimit` + no-new-privs in pre-exec |
| [`sandbox/rootless.py`](../../vanguard/packages/adapters/sandbox/rootless.py) | — | Rootless bubblewrap perimeter (K-34…K-41) |
| [`sandbox/ceiling.py`](../../vanguard/packages/adapters/sandbox/ceiling.py) | — | Plugin-cell capability gate. **Fail-closed since M-1**; delegates to `domain/selectors/` (2.1-D) |
| [`sandbox/toolkit.py`](../../vanguard/packages/adapters/sandbox/toolkit.py) | — | Toolkit cell over the JSON-RPC wire |
| [`stores/event_store.py`](../../vanguard/packages/adapters/stores/event_store.py) | 354 | **SQLite WAL + FULL sync** event store, per-Project hash chain |
| [`stores/blob_store.py`](../../vanguard/packages/adapters/stores/blob_store.py) | 126 | Content-addressed blobs, `write→fsync→emit` |
| [`stores/ledger_jsonl.py`](../../vanguard/packages/adapters/stores/ledger_jsonl.py) | 163 | JSONL export |
| [`stores/repo_index.py`](../../vanguard/packages/adapters/stores/repo_index.py) | 124 | Merkle repo index |
| [`stores/memory_engine.py`](../../vanguard/packages/adapters/stores/memory_engine.py) | 87 | KV memory engine |
| [`models/invocation.py`](../../vanguard/packages/adapters/models/invocation.py) | 577 | `ProposalTranslator` — the schema-driven model→kernel waist (D-28) |
| [`models/cassette.py`](../../vanguard/packages/adapters/models/cassette.py) | 190 | Deterministic replay cassettes |
| [`models/ollama.py`](../../vanguard/packages/adapters/models/ollama.py) | 164 | Tier-1 local route |
| [`models/lam.py`](../../vanguard/packages/adapters/models/lam.py) | 120 | LAM mock-server adapter |
| [`models/env_loader.py`](../../vanguard/packages/adapters/models/env_loader.py) | 121 | Provider credential loading |
| [`environment/git.py`](../../vanguard/packages/adapters/environment/git.py) | 847 | Git worktree environment (rollback fallback) |
| [`environment/fake.py`](../../vanguard/packages/adapters/environment/fake.py) | 642 | Deterministic fake environment |
| [`environment/sandboxed.py`](../../vanguard/packages/adapters/environment/sandboxed.py) | 265 | Sandboxed environment binding |
| [`environment/tableworld.py`](../../vanguard/packages/adapters/environment/tableworld.py) | 138 | TableWorld — **the orphaned Pack #2 candidate** (D-27) |
| [`context/window.py`](../../vanguard/packages/adapters/context/window.py) | 65 | Context-window accounting |

**Totals [VERIFIED]:** 100 Python modules, 23,349 physical lines across `vanguard/packages/`.

### 3.3 Boundary law

```text
domain  ← imports NOTHING in-repo
ports   ← domain
kernel  ← domain, ports                      … and MUST stay domain-blind (I-7)
agency  ← domain, ports, kernel
runtime ← domain, ports, kernel, agency
adapters← domain, ports                      … MUST NEVER import kernel or agency
apps    ← runtime                            (client boundary slot)
```

### 3.4 Enforcement instruments **[VERIFIED — 15 linters on disk, 9 wired into living CI]**

| Linter | Enforces |
|---|---|
| `check_boundaries.py` | The lattice above (283 files scanned) |
| `check_tcb_budget.py` | Kernel logical LOC ≤ 1438 (currently 1365) |
| `check_domain_blindness.py` | I-7 — no `coding\|pytest\|ast` tokens in the core (**widened per F-18**) |
| `check_isolation_policy.py` | I-6 — container/subprocess execution declared |
| `check_duplication.py --enforce` | F-16 — a second selector algebra fails the build |
| `check_event_coverage.py` | E-COV — production-emittable ⊆ `EVENT_KINDS` (ADR-0076 §6) |
| `check_stale_paths.py` | Documentation citing deleted paths |
| `check_markdown_links.py` | Local link validity |
| `scan_secrets.py` | Secret leakage |
| `generate_types.py --check` | F-13 — generated types are not hand-edited |
| *(also present, not CI-gated)* | `check_active_mvp_contract`, `check_backend_artifacts`, `check_baseline_manifest`, `check_core_changes`, `check_receipt` |

`test/broken/fixtures/` holds 30+ **intentional** architectural violations — the negative harness
that proves each linter fails closed rather than merely passing on clean code.

---

## 4. Index of Reviews & Research Literature

> Everything in this section is **advisory**. It is options and evidence, not requirements.

### 4.1 Review corpus — [`docs/07_reviews/`](../07_reviews/) (8 documents)

| # | Document | Lines | What it is | What it concluded | Weight |
|---|---|---:|---|---|---|
| — | [`VANGUARD_V060_FORENSIC_DISCOVERY.md`](../07_reviews/VANGUARD_V060_FORENSIC_DISCOVERY.md) | 858 | 25-section forensic investigation at HEAD `c7e9ded` | **Two Python runtimes claimed the same Layer-0 job.** Living CI gated `test/layer0` (25 OK) and did **not** run `test/kernel` (95 OK). `layer0/scheduler/driver.py:138` fabricated `VerdictRecorded {verdict:"pass"}`. `layer0/spi/ceiling.py:21` fail-opened on an empty capability list. **This is the failure the entire programme exists to prevent.** | Investigation, explicitly **not law** |
| — | [`ARCHIVE.md`](../07_reviews/ARCHIVE.md) | 24 | Pointer to the pre-lock corpus | Everything pre-v0.6 lives in git history at anchor `4f9f8b1`. No `docs/archive/` tree exists on disk | Navigational |
| 001 | [`001_V060_concept_phase_GAMMA.md`](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md) | 624 | The Concept Lock plan — adjudicates four independent advisory lanes claim-by-claim | Twelve architectural P0s stand. Four **strengthening amendments** adopted: proof obligations (every lock ships a falsifier), typed budget algebra, event-kind writer authority, AI-load-bearing identity (`D_H` includes prompt/ceiling/policy/routes). `Project` locked as consistency unit. `ChildPrincipal` is **not** a second type | Lock plan, **not a second SPEC** |
| 002 | [`002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md) | 313 | **The operational register.** Falsifiers F-01…F-21, wave exit gates, deferred/refused tables, P1-1…P1-17 | Wave 0 → Wave 4 sequence, then **stop**. A wave green by lexical grep is not done. §4.3 is the as-built-vs-law matrix | Authoritative on **outcomes**; cannot contradict SPEC/ADRs |
| 003 | [`003_V060_DIRECTOR_REVIEW.md`](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/003_V060_DIRECTOR_REVIEW.md) | 56 | Engineering Director independent review at `4f9f8b1` | **APPROVED.** Rationale: the lock tells the truth about the code; the kernel matches its constitution rule-for-rule; the decisions are correctly shaped; the roadmap is in the right order; every defect is registered. Adds **F-18** (linter narrower than I-7), **F-19** (13 tests silently uncollected), **F-20** (`preregistered_oracles.json` deleted, not relocated), **F-21** (`ProposalTranslator` really does degrade tool calls to prose) | **Binding via ADR-0075** |
| 004 | [`004_V061_ALIGNMENT_ROADMAP.md`](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/004_V061_ALIGNMENT_ROADMAP.md) | 155 | v0.6.1 formalization mandate **plus** the full M-2→M-10 task ladder (Portuguese) | Names the corrections to formalize as ADR `0077`+: component graph, absent-vs-forged, `agent.spawn` design-only, F-12 hardening, Wave-3 rebalancing, Pack #2 as a gate, scheduled doc consolidation. Introduces **NOVA-1…NOVA-5** | Advisory instruction set; **the ADRs it calls for do not exist yet** |
| 005 | [`005_V061_SUBSTRATE_GENERALITY_REVIEW.md`](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/005_V061_SUBSTRATE_GENERALITY_REVIEW.md) | 334 | **The strongest independent critique.** Asks: substrate, or coding harness with a kernel attached? | *"You are building the substrate. The primitives are right. The composition surface is not yet, and it is the layer your users will actually touch."* Eight weaknesses **W1–W8** and a 15-row decision register. W1 (fixed-slot manifest) is named highest leverage | Advisory. **Two recommendations request a Director scope call at M-3** |
| 006 | [`006_V061_aether-substrate-briefing.md`](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/006_V061_aether-substrate-briefing.md) | 104 | Theoretical briefing (Portuguese), lecture-shaped: Ch.1 theory, Ch.2 application | Ch.1 derives the separability thesis, the three planes, why one identifier is not enough, recursion as a single primitive, the authority-vs-strategy line, and why schema-valid ≠ learnable. Ch.2 grades AETHER against each. Same conclusion as `005`, reached independently from theory rather than from code | Advisory / pedagogical |

### 4.2 Research corpus — [`docs/06_references/`](../06_references/) (12 documents)

| # | Document | Lines | Thesis | Disposition |
|---|---|---:|---|---|
| 1 | [`RESEARCH_harness_agentic_coding_builder_research_and_framework.md`](../06_references/RESEARCH_harness_agentic_coding_builder_research_and_framework.md) | 2323 | **SOTA survey.** *"Model is cognitive capacity; agent is an iterative decision policy; harness is the operating system that turns that policy into verifiable autonomous behaviour."* Terminal-Bench 2.0 evidence: same GPT-5.3-Codex, harness swing 64.7% → 78.4% | **Adopt the consensus.** Harness-as-independent-variable is already the project's thesis |
| 2 | [`RESEARCH_harness_agentic_coding_builder_research_and_framework_B.md`](../06_references/RESEARCH_harness_agentic_coding_builder_research_and_framework_B.md) | 3266 | Successor synthesis. Ch.I research; Ch.II Harness-Builder architecture and the trajectory to meta-cognition / Meta-Harness / governed self-improvement | Advisory, explicitly **non-normative**. Largest single document in the corpus |
| 3 | [`RESEARCH_k3_harness-suggestion.md`](../06_references/RESEARCH_k3_harness-suggestion.md) | 204 | **SOTA plan.** Restates the north star as four falsifiable claims: unforgeable · domain-blind · bounded solvers · proven on SWE. Origin of the **A-B-C-D** framing | **Reorders and hardens; never rewrites.** On conflict, SPEC/ADR/roadmap win — its own words |
| 4 | [`RESEARCH_THEORETICAL_SYNTHESIS.md`](../06_references/RESEARCH_THEORETICAL_SYNTHESIS.md) | 380 | Wave-6 first-principles math: variational free energy, causal credit assignment over discrete action traces, crystallizing verified invariants into procedure memory | **Defer to M-10.** Fits the law only as exterior, domain-blind, promotion-gated plugin/policy |
| 5 | [`RESEARCH_THEORETICAL_SYNTHESIS_B.md`](../06_references/RESEARCH_THEORETICAL_SYNTHESIS_B.md) | 380 | Near-identical successor of #4 (same `id: REF-06-M5`) | **Duplicate pair.** A consolidation candidate for M-5's doc collapse |
| 6 | [`RESEARCH_deepseek-harness_algorithms-ideas.md`](../06_references/RESEARCH_deepseek-harness_algorithms-ideas.md) | 280 | Four-step reverse-engineering playbook against a competitor harness; PhD-style experiment sandbox structure | **Mine for method, not architecture.** Source of the "profile = ordered stack of plugin bundles" observation `005` §W1 cites |
| 7 | [`RESEARCH_Harness_Builder_Framework.md`](../06_references/RESEARCH_Harness_Builder_Framework.md) | 714 | Greenfield product PRD for a universal plugin-composition framework (Redis / NATS / ChromaDB / K8s / event bus) | ⚠ **REJECT as a competing architecture.** It contradicts the locked hexagonal lattice and would re-create the dual-runtime failure. **Mine only as a catalog of plugin/adapter ideas** |
| 8 | [`proposal_glm_harness_BETA.md`](../06_references/proposal_glm_harness_BETA.md) | 245 | External GLM independent assessment against live tree `83b5009` | *"The goal is reachable on this trajectory… the parts that remain are mostly surface, sequencing, and **one verified data-quality defect** that would quietly poison the entire third layer."* That defect is the hollow trajectory | The **only** reference that verifies claims against a working tree |
| 9 | [`proposal_hy3_harness.md`](../06_references/proposal_hy3_harness.md) | 76 | Meta-analysis: what to *do* with the reference corpus | Five rulings: treat GLM as the operating synthesis · trajectory hardening is highest leverage · reject #7 as a second core · adopt the matching consensus · defer meta-cognition | Written under the pre-development-hold assumption |
| 10 | [`proposal_hy3_improved.md`](../06_references/proposal_hy3_improved.md) | 76 | Corrected successor of #9 | Same five rulings, but corrects the premise: **ADR-0075 already lifted the hold**; only M-5…M-10, `agent.spawn`, Pack #2, and concurrency are gated. NOVA-1 is registered `PRONTA` — authorized, not blocked | **Supersedes #9.** Use this one |
| 11 | [`vanguard_body_detailed.md`](../06_references/vanguard_body_detailed.md) | 484 | "Living treatise" — computational physics, biological emergence, neuro-symbolic cognition, evolutionary blueprint | ⚠ **Directly conflicts with ADR-M0-10 / REJ-10**, which forbids biological/cosmological framing in any document under `docs/`. Retain as inspiration or retire — a Director call ([§6.3](#63-director-decision-checklist) item 8) |
| 12 | [`openrouter_llm_models_suggested.md`](../06_references/openrouter_llm_models_suggested.md) | 37 | Model routing reference — free / low-cost / frontier tiers | Operational input to `model_routes` in `harness.yaml`. Not architecture |

**Reading the corpus honestly.** Documents 1, 2, 3, 8, 10 form the coherent advisory spine and
agree with the law. Document 7 is a competing architecture and must not be built. Documents 4 and 5
are a duplicate pair for a deferred milestone. Document 11 conflicts with a standing refusal.

---

## 5. Neutral Analysis of Open Architectural Tensions

Each tension is presented as a genuine trade-off. No recommendation is smuggled into the framing;
where this audit has an opinion it is labelled **[Audit view]** and separated from the evidence.

### 5.1 T-1 · Manifest shape — fixed slots vs. named component graph

**Where it lives:** [`packs/code-default/harness.yaml`](../../packs/code-default/harness.yaml),
[`runtime/compose.py`](../../vanguard/packages/runtime/compose.py), `schemas/mhf/harness_manifest.schema.json`.

| | **Option A — keep fixed 5-slot template** | **Option B — named component graph** |
|---|---|---|
| **Shape** | `planner:` `context:` `memory:` `evaluation:` `toolkits: []` `model_routes: []` | A map of named component instances, each declaring SPI kind, ref, config, ceiling — plus an explicit binding/wiring section |
| **Expresses well** | A ReAct coding agent with swappable parts. Exactly Pack #1 | Critic loops (2 planner-class components), debate (N proposers + aggregator), tree search (expansion/scoring/selection as separate policies), evolutionary search, dual evaluation gates |
| **Cannot express** | Any of the right-hand column — they can only be smuggled inside one monolithic planner plugin | — |
| **`D_H`** | Unchanged | Covers the graph; **principle unchanged** (still full behaviour-affecting composition) |
| **Cost now** | Zero | One schema revision + a compose-v2 resolving a map instead of six keys — **work 3.1-B is already doing** |
| **Cost after M-4** | — | Schema migration + `D_H` migration + every pack rewritten + **every trajectory in the corpus attributed to a superseded shape** |
| **Risk** | Ships the coding-agent shape as the permanent composition API. `005` §15(a) names this as the #1 thing that prevents SOTA | Wave 3 gains scope in a wave already flagged as under-weighted (W7). Slot names must survive as pack convention or Pack #1 churns |

**Neutral framing.** The disagreement is not about whether the primitives can express these
algorithms — all reviews agree they can, via spawn topology + policy. It is about whether there is
**anywhere in the manifest to name them**. This is a surface question with a hard deadline: it is
cheap before M-4 and expensive after, because `D_H` is computed over the manifest shape.

**The external comparison, stated carefully.** DeepSeek Harness organises configuration as a flat
profile — an ordered stack of plugin bundles — and states it has *"no privileged core to patch."*
`005` §W1 is explicit that these are **two separable properties**: import the flat composition
surface, refuse the absent authority boundary. Flatness at the composition surface is orthogonal to
rigidity at the authority boundary.

**Status:** `004` §2 lists this as requiring ADR `0077`+. `sprint_active.md` carries it as **3.3-B,
marked DIRECTOR**. No such ADR exists on disk **[VERIFIED]**.

---

### 5.2 T-2 · Spawning — engine-owned vs. capability-mediated `agent.spawn`

**Where it lives:** [`agency/episode/engine.py`](../../vanguard/packages/agency/episode/engine.py) (693 LOC),
[`ports/spi.py`](../../vanguard/packages/ports/spi.py).

| | **Option A — `spawn` stays engine-owned** | **Option B — `agent.spawn` as a kernel verb** |
|---|---|---|
| **Mechanism** | `EpisodeEngine.spawn(parent, harness, capabilities, budget)`. `IPlanner` gets `plan/observe/reflect` only | `spawn` dispatched through S0–S12 like any other effect. A planner may spawn only if its composition granted the verb |
| **Authority** | Delegation is a **privileged engine call** | Delegation becomes a **mediated effect with a receipt** — ledgered, budgeted, attributed |
| **Consequence** | Any algorithm whose *structure is recursion* — tree search, hierarchical decomposition, conditional delegation, the §5.1 outer loop — has nowhere to live except inside the engine | Those algorithms become planner plugins. Attenuation, budgets, and ledgering are reused unchanged |
| **TCB impact** | None | **Touches the kernel.** Wave 4 must not absorb a kernel change |
| **Risk** | This is the one place the current design most plausibly **forces a new engine later** — which is ADR-0070's own stated reversal condition | New dispatch surface in the most security-critical file in the tree, immediately before the foundation stop line |

**Neutral framing.** Note that Option B *strengthens* authority rather than weakening it: today
delegation bypasses the reference monitor because the engine is trusted; under B every spawn is
verified, leased, and receipted like every other privileged effect. The objection to B is not
security — it is **sequencing**.

**Convergent recommendation across all sources:** design now, decide at M-3, implement post-M-4.
`005` register row 9, `004` §2, `sprint_active.md` 3.5-A/B/C (3.5-C marked **DIRECTOR**),
`milestones.md` M-6.

---

### 5.3 T-3 · Guardrails — mandatory mechanism vs. declarable "absent-vs-forged"

**Where it lives:** `schemas/mhf/harness_manifest.schema.json`,
[`runtime/compose.py`](../../vanguard/packages/runtime/compose.py),
[`adapters/evaluators/daemon.py`](../../vanguard/packages/adapters/evaluators/daemon.py).

| | **Option A — mandatory UID-10002 daemon** | **Option B — declarable absence, never forgeable** |
|---|---|---|
| **Rule** | Every composition runs with an exterior evaluator and a preregistered oracle | *"You may turn a guardrail off; you may never turn off the record that it was off."* |
| **Mechanics** | — | A composition declares `evaluation: none`. Compose accepts. `D_H` records it. The trajectory records `oracle: null`. The run is marked **unattributable for promotion** |
| **The distinction** | Guarded vs. unguarded | **Absent vs. forged.** An unsigned verdict stays categorically illegal under every composition; an *acknowledged absence* is a legitimate composition |
| **Scope** | — | Same treatment for sandbox tier and approval policy, per composition and per component |
| **Pro** | Maximum uniform assurance; no configuration can weaken evidence | A research agent or pure-compute optimisation loop should not need a daemon and an oracle to run. Removes the pressure that eventually produces a *bad* escape hatch |
| **Con** | Guardrails drift from infrastructure into **product constraint** (`005` §13) | Every optional guardrail is a surface a future reviewer must re-audit |

**The seven that stay non-negotiable under any composition** (`005` §W4): writer authority on
privileged kinds · envelope lineage · fail-closed selector inclusion · ledger-as-truth · capability
attenuation on spawn · the signature requirement on any verdict that *is* claimed · JCS as the byte
source. **Everything else is policy.**

**Status:** `sprint_active.md` sprint 3.4 (3.4-A DESIGN → ADR; 3.4-B/C/D READY once the ADR lands).
No ADR on disk **[VERIFIED]**.

---

### 5.4 T-4 · Trajectory quality — the "born-hollow" corpus (G1 / NOVA-1)

**This is the only tension in this section that is a verified live defect rather than a design choice.**

**[VERIFIED on disk, this audit]** — [`vanguard/packages/runtime/trajectory.py`](../../vanguard/packages/runtime/trajectory.py):

```python
line 10:  _ZERO_COST = {"usd_micros": 0, "tokens": 0, "bytes": 0, "millis": 0}
line 53:              "cost": dict(_ZERO_COST),      # per-turn cost
line 75:      "cost": dict(_ZERO_COST),              # episode cost
```

Every completed episode therefore emits a record that is **schema-valid, cryptographically
attributable, and unusable**: zero per-turn cost, no model fingerprint, no embedded verdict.

**Why this is exactly the failure I-9 was written to prevent.** Invariant I-9 says a digest over
`{ids, n}` is *not* a trajectory. F-12 as currently written asserts only **schema validity** — which
a content-free record satisfies. The falsifier passes while the invariant fails. `005` §W8:
*"That is precisely the shape of failure I-9 was written to prevent."*

**What depends on it.** Cost-aware policy learning · escalation calibration (SPEC §5.3's
`P(pass | action, context)`) · any router experiment · the DPO harvest (SPEC §7) · skill synthesis
(§5.4) · the entire M-10 meta-cognitive layer.

**Why timing is not negotiable.** Every episode completing before the fix is a permanently degraded
row in the only corpus Layer 3 will ever train on. Trajectories cannot be back-filled — the
governor's settled cost ledger for a past run is gone.

| | **Option A — fix now (NOVA-1)** | **Option B — carry to Wave 4** |
|---|---|---|
| **Content** | Strengthen F-12 to assert: non-zero cost vector · populated turns · model fingerprint present · verdict embedded or explicitly null | Wire real cost at the E2E, when the governor's settled ledger is naturally available |
| **Cost** | Cheap. `sprint_active.md` registers NOVA-1 as **PRONTA** in M-2 — authorized, not blocked | Zero now |
| **Risk** | Small scope addition to a wave at its closing gate | Every run between now and M-4 produces a poisoned corpus row |

**Note the internal disagreement, unresolved:** `sprint_active.md`'s Wave-1 carry-out table sends
this to **Wave 4** (*"real per-turn cost needs the governor's settled ledger"*), while `004`, `005`
§W8, `008`/`010` (`proposal_hy3_*`) and the GLM review all call it the **single highest-leverage fix
available right now**. `milestones.md` M-4 also carries NOVA-5 as the confirmation step. This is a
live contradiction between the board and the register — **[Audit view]** it is the cleanest,
cheapest item on your checklist and the only one with an irreversible clock attached.

---

### 5.5 T-5 · Layer-0 absorption timeline

**[VERIFIED]** `layer0/` currently holds, and only holds:

```text
layer0/compose/compiler.py            manifest → FrozenHarness digest shape
layer0/registry/                      lifecycle.py · broker.py · isolation.py
                                      sandbox.py · validator.py · grants.py · worker.py
layer0/events/                        emitter.py · envelope.py · store.py · taxonomy.py
```

`kernel/`, `scheduler/`, `spi/`, and `events/{selectors,canonical,fold,blob}.py` **were deleted at
2.2-B**. The two headline forensic defects — the fabricated `"pass"` and the fail-open ceiling —
died with them. Zero `layer0` imports remain under `vanguard/` (provenance comments only).

| | **Option A — absorb registry+compose at 3.1, then delete (current plan)** | **Option B — delete now, rebuild in packages** |
|---|---|---|
| **Rationale** | `layer0/registry/` and `layer0/compose/` are the **only** plugin-lifecycle code in the tree. Absorbing preserves working semantics | Removes the fork earlier; nothing is inherited from unproven code |
| **Risk** | `005` §W7: these have **no packages twin and have never run on the canonical path.** Wave 3 builds its entire framework claim on them | Wave 3 grows from "absorb + prove" to "write + prove" |
| **Governing rule** | SPEC §1: *"Duplicate kernels, schedulers, mocks, and synthetic verdict paths MUST NOT be deleted until a behavioral parity gate."* | Would need a Director exception to that rule |

**Status:** `milestones.md` M-3 exit gate reads *"`layer0/` fully deleted."*
`sprint_active.md` records the triage correction: layer0 **shrinks** at 2.2-B and **dies at 3.1**.

---

### 5.6 T-6 · The loop as mechanism — publish the claim with its falsifier

Not a choice between options; a request to **make an implicit claim explicit and refutable**.

The turn loop stays mechanism, never plugin. Competing harnesses make the loop itself a plugin —
coherent for them only because they have no authority boundary to preserve. `005` §W3 asks that the
claim be published with a bound falsifier:

> **"Name an agentic algorithm that cannot be expressed as spawn-topology + planner policy over this loop."**

If someone produces one, that is genuine ADR-0070 reversal evidence. If nobody can within a year,
the loop is proven and the argument ends. Without this, the question gets relitigated every quarter
at full cost.

---

### 5.7 T-7 · `K ≪ N` — asserted, never tested (the suspend/resume falsifier)

The `002` register §5 claims many logical agents share a bounded worker pool. **Nothing in the tree
demonstrates logical-agent / worker separation** — `EpisodeEngine` *is* the scheduler shell, and
`HarnessSession` holds live per-run state.

The precise question:

> **Is an episode's continuation reconstructible from the ledger alone, or does resuming require the live Python object?**

F-02 (cold replay) proves grants, budgets, approvals and episode FSM survive a cold fold — most of
the answer. The remaining test is **NOVA-2**: suspend an episode mid-turn → reconstruct in a fresh
process from the WAL → resume → complete.

- **Green** ⇒ the concurrency future is a scheduling refactor, and I-11 can be lifted on measurement alone.
- **Red** ⇒ there is hidden in-process coupling, and you want to know now, not at M-7.

`005` calls this *"the highest-value cheap test not currently on the board."* It is now registered as
**NOVA-2, PRONTA in M-2** and is the stated **precondition** for I-11's measurement gate.

---

### 5.8 T-8 · Governance mass vs. capability (the doc-collapse question)

`005` §W6 measures the governance corpus at roughly 3.4k lines of normative and planning prose
across seven authority tiers — **currently larger than the substrate work it governs.** Two costs
are already visible: the deferred/refusal list is maintained in four places (SPEC §9, ADR-0073,
`002` §2, `milestones.md`), and ADR-0076 exists solely to adjudicate which of two live artifacts is
canonical — *the tax on having let the fork live*, not a permanent feature.

Every source agrees on **both** the target (collapse to **SPEC + ADR log + one living board**) and
the timing (**after M-4** — mid-flight documentation surgery during Wave 2/3 is strictly worse than
the duplication). Registered as `sprint_active` 5.1-A/B/C. Target: a senior developer productive
from three documents, not seven.

---

### 5.9 T-9 · The five-SPI freeze

The [consolidated M0-03 lineage](../05_adr/INDEX.md#consolidated-historical-lineage), retained by
ADR-0086, freezes exactly five SPIs and requires *"a design
review, not a PR"* for a sixth. `005` §8 records the one caveat worth your attention: the freeze *"is
defended more strongly than its evidence supports."* The guard is correct; what must not happen is
`"a sixth SPI requires a design review"` hardening into `"there are five SPIs forever."` Scheduled
for revisit at M-9 (`9.2-B`, marked TECH-LEAD) once a mature component graph exists.

---

## 6. Macro Roadmap Ladder & Director Decision Checklist

### 6.1 The ladder, M-0 → M-10 **[VERIFIED against `milestones.md` + `sprint_active.md`]**

```text
╔═══════════════════════════ FOUNDATION PHASE — ends at a STOP LINE ═══════════════════════════╗
║                                                                                              ║
║  M-0 · Wave 0 — Engineering truth                                     ✅ COMPLETE            ║
║        Living CI measures vanguard/packages/, not a self-signing fork.                       ║
║        Gate: production suites wired · F-01…F-21 registered · codegen --check gating.        ║
║                                                                                              ║
║  M-1 · Wave 1 — Trust spine                                           ✅ COMPLETE (GREEN)    ║
║        False gates can no longer certify the trust spine.                                    ║
║        Gate: F-01…F-15 green on canonical path · suites green · TCB ≤ 1438.                  ║
║        Landed: signed request-bound verdicts · fail-closed ceilings · complete D_H ·         ║
║                envelope lineage · typed budget algebra · cold replay from disk.              ║
║                                                                                              ║
║  M-2 · Wave 2 — One runtime                          🔵 IN FLIGHT — re-gate round 4          ║
║        Gate: F-16 green · zero layer0 imports · kill surfaces deleted · reducer folds        ║
║              complete (EffectFailed, EffectRejected, BudgetExhausted, CapabilityAttenuated,  ║
║              TurnStarted, Plugin*×5) · catalogued-AND-folded property test.                  ║
║        Done: 2.1-A…E · 2.2-A/B/C.   Remaining: Tech Lead sign-off, then 2.2-D.               ║
║        Carrying: NOVA-1 (trajectory content) · NOVA-2 (suspend/resume) · NOVA-3 (_PROC_PATTERN)║
║                                                                                              ║
║  M-3 · Wave 3 — Extensibility        ⚪ QUEUED  ← ⚠ THE FRAMEWORK CLAIM LIVES OR DIES HERE   ║
║        Gate: echo plugin walks DISCOVERED→RESOLVED→VERIFIED→ACTIVATED→QUIESCING→RETIRED      ║
║              over UDS, every transition ledgered (ADR-M0-13) · code-default loads through    ║
║              the same lifecycle · I-7 green on the widened surface · layer0/ deleted.        ║
║        New sprints from 004: 3.3 component graph · 3.4 absent-vs-forged · 3.5 spawn design.  ║
║        ⚠ 005 §W7: Wave 1 got 17 tasks + 15 falsifiers for the trust spine.                   ║
║          Wave 3 gets 7 tasks for the entire product claim — built on layer0 code that        ║
║          has never run on the canonical path. NOVA-4 adds the six missing negatives.         ║
║                                                                                              ║
║  M-4 · Wave 4 — Foundation E2E                       ⚪ QUEUED   ███ STOP LINE ███           ║
║        Nine rows true on ONE uninterrupted run:                                              ║
║          real model · authorized effect · filesystem change · sandbox · exterior signed      ║
║          eval · WAL ledger · cold replay · schema-valid populated trajectory · one runtime.  ║
║        Escalate to Director any temptation to widen scope to make the run pass.              ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
                                            ║
                                            ║   ◄── nothing below starts before the gate above
                                            ▼
╔═══════════════════ MACRO GENERALITY & META-COGNITION PHASE — outcomes only ══════════════════╗
║                                                                                              ║
║  M-5 · Generality Proof & Consolidation                             deps: M-4                ║
║        Doc collapse to SPEC + ADR log + one board. Pack #2 (non-coding: math or data).       ║
║        Gate: ZERO diffs under domain/ and kernel/ for Pack #2 — I-7 becomes FACT, not thesis.║
║              Suspend/resume cold-reconstruction falsifier passes at scale.                   ║
║                                                                                              ║
║  M-6 · Mediated Delegation (agent.spawn)                            deps: M-5 + 3.5-C        ║
║        Gate: planner without a spawn grant cannot delegate · child stays monotonically       ║
║              attenuated · spawn recorded as a mediated effect with a receipt.                ║
║        Validation cases: hierarchical decomposition · tree search.                           ║
║                                                                                              ║
║  M-7 · Controlled Concurrency                                       deps: M-5, M-6           ║
║        Independence groups activated for non-intersecting selectors; K ≪ N separation.       ║
║        Gate: selector-disjointness measurement · zero event loss under backpressure.         ║
║        I-11 stands until THIS gate fires.                                                    ║
║                                                                                              ║
║  M-8 · Framework Builder Abstraction                                deps: M-6, M-7           ║
║        Debate · critic/revisor · evolutionary search · multi-agent delegation, all           ║
║        composed declaratively over the component graph.                                      ║
║        Gate: reference suites run multi-pack WITHOUT engine modification.                    ║
║                                                                                              ║
║  M-9 · Scaled High-Performance Orchestration                        deps: M-7, M-8           ║
║        Gate: measured IPC / serialization / plugin-call overhead; bounded ledger pressure.   ║
║        Also: revisit the five-SPI freeze against the mature component graph.                 ║
║                                                                                              ║
║  M-10 · Meta-Cognitive Substrate (FINAL)                            deps: M-8, M-9           ║
║        Outer-loop planner at the `outer` slot · manifest mutation · skill synthesis ·        ║
║        DPO harvest · continuous promotion loop · calibrated active-inference gate.           ║
║        FINAL GATE: the system proposes, verifies, and promotes an improved version of its    ║
║        own composition — with the whole chain attributable via D_H/D_R/D_X and signed        ║
║        verdicts, on a corpus whose evidence was never forgeable.                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
```

### 6.2 Proposed version nomenclature

The mapping below is **a proposal for your determination**, not an existing decision. No ADR on disk
assigns version numbers to these milestones **[VERIFIED]**.

| Version | Name | Content | Cut when |
|---|---|---|---|
| **v0.6.0** | Concept Lock | SPEC + ADRs `0069`–`0076`. **Already locked** (ADR-0075) | — |
| **v0.6.1** | Substrate Correction Lock | ADRs `0077`+ formalizing T-1, T-3, T-6; F-12 hardening (T-4); NOVA-2 (T-7); Wave-3 rebalancing | M-2 green |
| **v0.6.2** | Extensibility Lock | Wave 3 complete: registry FSM · compose v2 · echo plugin lifecycle · component-graph manifest live · `layer0/` deleted | M-3 gate |
| **v0.7.0** | Foundation MVP | The nine-row E2E green on one run. **The foundation stop line.** Package version cuts from `0.4.5b1` | M-4 gate |

### 6.3 Director decision checklist

Record your determination beside each. Items 1–6 correspond to the tensions in §5; items 7–10 are
governance decisions this audit surfaced.

---

**☐ 1 · TRAJECTORY CONTENT (T-4 / G1 / NOVA-1) — the only item with an irreversible clock**

*Verified live defect: `runtime/trajectory.py` lines 53 & 75 emit `_ZERO_COST`.*

- ☐ **1a.** Authorize NOVA-1 **now, in M-2** — strengthen F-12 to assert non-zero per-turn cost, populated turns, model fingerprint, and verdict-embedded-or-explicitly-null.
- ☐ **1b.** Or confirm the `sprint_active.md` carry to **Wave 4**, accepting that every run until then produces a permanently degraded corpus row.
- ☐ **1c.** Resolve the contradiction between the board (Wave 4) and the register/reviews (now) either way, in writing.

**Determination:** ____________________________________________

---

**☐ 2 · MANIFEST SHAPE (T-1) — the highest-leverage, hardest-deadline scope call**

- ☐ **2a.** Authorize `harness.yaml` → **named component graph** at 3.1-B/3.3, via a new ADR `0077`+.
- ☐ **2b.** Confirm slot names survive as **pack convention**, not schema constraint.
- ☐ **2c.** Confirm `D_H` extends to cover the graph, principle unchanged.
- ☐ **2d.** Or explicitly accept the fixed 5-slot template as the permanent composition API, with reasons.

**Determination:** ____________________________________________

---

**☐ 3 · GUARDRAIL DECLARATION MODEL (T-3)**

- ☐ **3a.** Authorize the **absent-vs-forged** rule via ADR: a composition may declare `evaluation: none` / optional sandbox tier / optional approval policy; `D_H` records it; the trajectory is marked **unattributable for promotion**.
- ☐ **3b.** Ratify the **seven permanent non-negotiables** (§5.3) as the fixed substrate boundary.
- ☐ **3c.** Confirm an unsigned verdict remains categorically illegal under every composition.

**Determination:** ____________________________________________

---

**☐ 4 · `agent.spawn` (T-2)**

- ☐ **4a.** Confirm **design-only** through Waves 1–4 (3.5-A/B), with the falsifier sketch written now.
- ☐ **4b.** Confirm implementation blocked until **post-M-4** (3.5-C, owner: Director), landing at M-6.
- ☐ **4c.** Confirm the kernel gains **nothing but tests** in Waves 1–4; TCB ceiling stands at 1438.

**Determination:** ____________________________________________

---

**☐ 5 · LAYER-0 RETIREMENT (T-5)**

- ☐ **5a.** Confirm `layer0/registry/` and `layer0/compose/` absorb into `vanguard/packages/runtime/` at **3.1**, *then* `layer0/` is deleted — behavioural parity first, per SPEC §1.
- ☐ **5b.** Note the risk `005` §W7 raises: this code has never run on the canonical path and Wave 3's entire framework claim rests on it.

**Determination:** ____________________________________________

---

**☐ 6 · WAVE-3 WEIGHTING (T-1/T-5 consequence)**

- ☐ **6a.** Authorize **NOVA-4** — the six plugin-lifecycle negatives as first-class falsifiers, not implied behaviour: unknown-ref-fails-at-compose · empty-ceiling-denies · registry-exclusive-`Plugin*`-write · faulted-cell-cannot-stay-active · `in_process`-requires-explicit-grant · frozen-composition-immutable.
- ☐ **6b.** Decide whether Wave 3 is rebalanced (more sprints) or merely re-labelled.

**Determination:** ____________________________________________

---

**☐ 7 · `K ≪ N` PROOF (T-7)**

- ☐ **7a.** Authorize **NOVA-2** in M-2: suspend mid-turn → cold-reconstruct in a fresh process → resume → complete.
- ☐ **7b.** Confirm this is the **precondition** for I-11's measurement gate, not its satisfaction.

**Determination:** ____________________________________________

---

**☐ 8 · GOVERNANCE & CORPUS HYGIENE (T-8)**

- ☐ **8a.** Confirm doc collapse to **SPEC + ADR log + one living board** is scheduled at **M-5**, not now.
- ☐ **8b.** Rule on [`vanguard_body_detailed.md`](../06_references/vanguard_body_detailed.md) — its biological/cosmological framing conflicts with ADR-M0-10 / REJ-10, which forbids that framing in any document under `docs/`. Retain as inspiration, relocate, or retire.
- ☐ **8c.** Rule on the duplicate `RESEARCH_THEORETICAL_SYNTHESIS` / `_B` pair.
- ☐ **8d.** Confirm [`RESEARCH_Harness_Builder_Framework.md`](../06_references/RESEARCH_Harness_Builder_Framework.md) is **rejected as a competing architecture** and mined only for plugin/adapter ideas.

**Determination:** ____________________________________________

---

**☐ 9 · TCB METRIC (§3.2)**

- ☐ **9a.** Confirm the LOC gate (1365/1438) remains the living gate until the KERNEL.md §1.1 replacement triple exists — mutation score on kernel+reducers, % of controls with production call-site proofs, E-COV.
- ☐ **9b.** Or authorize building the replacement metric, and name its milestone.

**Determination:** ____________________________________________

---

**☐ 10 · VERSION & RELEASE STRATEGY (§6.2)**

- ☐ **10a.** Ratify or amend the v0.6.1 / v0.6.2 / v0.7.0 mapping.
- ☐ **10b.** Confirm the package version cut from `0.4.5b1` happens **at the M-4 gate** (it is already listed as a Director-only decision on `sprint_active.md`).
- ☐ **10c.** Confirm **Wave 4's stop condition is unchanged and non-negotiable** — `agent.spawn`, concurrency, Pack #2, and all of M-5…M-10 stay out of implementation scope until the nine-row gate is green.

**Determination:** ____________________________________________

---

### 6.4 What every determination must produce

For each item you decide, the binding output is:

1. A new **append-only ADR `0077`+** citing which prior ADR it narrows or extends, with evidence.
2. A **bound falsifier** — per ADR-0074, *a concept without a bound falsifier is not locked.*
3. A row in the [`002` register](../07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md) §4.2, in the same table format.
4. A task with a readiness label in [`sprint_active.md`](../03_sprints/sprint_active.md).
5. An explicit disposition label: **lock now / strengthen now / generalize now / design-only-implement-later / revisit after Wave 4 / reject.**

---

## 7. Audit Findings — What This Pass Verified

### 7.1 Claims re-executed against the tree **[VERIFIED]**

| Claim | Result |
|---|---|
| Kernel within TCB budget | ✅ `1365 / 1438` logical LOC across 9 files |
| Hollow trajectory (G1 / NOVA-1) | ✅ **Confirmed live** — `_ZERO_COST` at `trajectory.py:53` and `:75` |
| `layer0/` shrunk, not deleted | ✅ Only `compose/`, `registry/`, `events/` remain; `kernel/`, `scheduler/`, `spi/` gone |
| F1 fabricated `"pass"` | ✅ **Gone** — died with `layer0/scheduler/` at 2.2-B |
| Fail-open ceiling | ✅ **Gone** — `layer0/spi/ceiling.py` deleted; `adapters/sandbox/ceiling.py` delegates to the domain algebra |
| `root.py` split in place | ✅ 126 LOC facade; `compose.py` 390, `session.py` 646, `wiring.py` 347 |
| CI is the packages lattice | ✅ 11 packages test steps + cold `replay-parity` + 9 linters wired |
| Linter inventory | ✅ 15 on disk, 9 gating CI |
| Packages inventory | ✅ 100 modules, 23,349 physical lines |

### 7.2 Discrepancies found in the documentation corpus

| # | Finding | Evidence |
|---|---|---|
| **D-A** | **`docs/03_sprints/plans/000_CANONICAL_EXECUTION_PATH.md` does not exist.** Both `005` (evidence base) and `proposal_glm_harness_BETA.md` cite it as a load-bearing source, and `005` §W6 uses its existence as an argument about governance mass | `find . -name '000_CANONICAL*'` → no match |
| **D-B** | **The ADRs that `004` mandates (`0077`+) do not exist.** The component graph, absent-vs-forged, and spawn-design decisions are described as formalized across `004`/`005`/`milestones.md`, but no ADR carries them. They remain **advisory-only**, which is exactly why they are on your checklist | `ls docs/05_adr/` — highest is `0076` |
| **D-C** | **Live contradiction on NOVA-1 timing.** `sprint_active.md` carries trajectory cost to **Wave 4**; `004`, `005` §W8, and both `proposal_hy3_*` documents call it the highest-leverage fix available **now**. `milestones.md` M-2 lists NOVA-1 as `PRONTA` | §5.4, item 1c on the checklist |
| **D-D** | **`check_markdown_links.py` validates only two files.** Its `DOC_GLOBS` is `("README.md", "docs/README.md", "docs/agile/sprint6B/*.md")` — the third glob matches nothing since the sprint-6B removal. The gate reports `LINK PASS` while the entire `docs/` corpus, all ADRs, and both Director briefings go unchecked. **This is the same defect class as F-18: a linter narrower than the invariant it certifies.** It is why V1's four broken ADR links (§7.4) survived CI | `grep DOC_GLOBS tools/linters/check_markdown_links.py`; V1's `0070`/`0071`/`0072`/`0074` targets confirmed absent |
| **D-E** | **`docs/08_workflows/` is empty** but is carried in the documentation tree | `ls docs/08_workflows` |
| **D-F** | **`DELETE.md` is a zero-byte file at repo root** | `ls -la DELETE.md` → 0 bytes |
| **D-G** | **`docs/06_references/RESEARCH_THEORETICAL_SYNTHESIS.md` and `_B.md`** are a near-duplicate pair sharing `id: REF-06-M5` and identical titles | Front-matter comparison |
| **D-H** | **`vanguard_body_detailed.md` conflicts with a standing refusal.** ADR-M0-10 / REJ-10 forbids biological/cosmological framing in **any** document under `docs/`; this document is built on it | SPEC §9; the document's own epigraph |

### 7.3 What this audit did **not** examine

Stated so the boundary of the finding is honest: the TypeScript client lattice
(`vanguard/clients/cli/`, `client-core/`) was inventoried but not audited; the full test suite was
not re-executed (per-directory module counts only); `benchmarks/` and `lab/` were mapped but not
exercised; no runtime or E2E execution was performed.

### 7.4 Corrections to V1

`DIRECTOR_TODO_LOCK_CONCEPTS.md` (V1, recoverable at commit `b36481c`) is a sound executive
summary. Four factual corrections, none of which change its conclusions:

1. **Four ADR links in V1 §5.2 point at filenames that do not exist.** The correct paths are
   [`0070-recursive-substrate-agent-spawn-swarm-as-policy.md`](../05_adr/0070-recursive-substrate-agent-spawn-swarm-as-policy.md),
   [`0071-authority-state-ledger-identity-trinity.md`](../05_adr/0071-authority-state-ledger-identity-trinity.md),
   [`0072-plugin-boundary-wire-first-evaluator-exterior.md`](../05_adr/0072-plugin-boundary-wire-first-evaluator-exterior.md), and
   [`0074-gamma-lock-amendments-proof-budget-writer-identity.md`](../05_adr/0074-gamma-lock-amendments-proof-budget-writer-identity.md).
2. **V1 §3 places `jcs.py` under `domain/ledger/`.** It is at
   [`domain/canonicalisation/jcs.py`](../../vanguard/packages/domain/canonicalisation/jcs.py).
3. **V1 §3 shows `layer0/` as holding only `registry/` and `compose/`.** `layer0/events/` (emitter,
   envelope, store, taxonomy) is also still present.
4. **V1 §3 states "434 Tests 100% Green."** The last recorded full-root baseline is **1119 collected
   with 12 reds** (`003` §4), and the most recent board entry records **1176 collected with 6 reds**
   (3 Ollama-offline, 3 pre-existing integration). The per-suite counts are green; the root discovery
   is not, and the register is explicit that **honest red is acceptable** while lexical green is not.

---

## Appendix A — Invariants I-1 … I-11 (quick reference)

| # | Invariant | Enforced by |
|---|---|---|
| I-1 | One `EffectRequest`, generated from one schema, used at S0, on the wire, and in adapters | `generate_types.py --check` (F-13) |
| I-2 | Emitted = declared, **and forged is not accepted**. Lexical coverage is not this invariant | `check_event_coverage.py` + F-03/F-05 |
| I-3 | A control merges with its call site (activation-bundle rule) | Review rule |
| I-4 | `State = fold(events)`, proven by a **cold** replay from durable storage | `ColdReplayParity` (F-02) |
| I-5 | The judge stays exterior — separate identity, signed verdicts, unreachable | UID 10002 + gateway-only writes (F-03/F-04) |
| I-6 | Plugins untrusted by default; `in_process` is a policy-granted privilege | `check_isolation_policy.py` |
| I-7 | The core is domain-blind — no `coding\|ast\|pytest` in `layer0/` or `packages/{domain,kernel}/` | `check_domain_blindness.py` (F-18) |
| I-8 | Specs are generated **or** normative, never both | Drift is a CI failure |
| I-9 | **Telemetry is a dataset** — every episode ends in a schema-valid `mhf.trajectory/1` that is, without transformation, a valid harvest row | F-12 — ⚠ **currently asserts validity only; see §5.4** |
| I-10 | Metaphors ship as comments, not architecture | ADR-M0-10 |
| I-11 | The scheduler is **sequential**; concurrency is gated on measurement. Unknown selector footprint means conflict, not independence | Design + M-7 gate |

## Appendix B — The refusal list (SPEC §9, do not reopen without reversal evidence)

No self-updating release pipeline · no competence-graph pretence · no parallel fan-out before
independence groups are measurable · no second wire contract for clients · **no metaphysical taxonomy
of any kind** · no playbook runtime (advisory and guided are the ceiling; `strict` DAG execution is
rejected outright) · MCP is configuration and an adapter, never authority · no GUI/TUI as a backend
gate · no scalar reward for promotion · no always-on full-content training capture · **no third
runtime tree** · no swarm engine, workflow DAG engine, or graph database · no byte-identical
concurrent ledger as general law · no mid-run `FrozenHarness` hot-swap · no evaluator as a product
plugin · no Rust TCB rewrite, WASM-default isolation, or multi-host distribution in v0.6 · no
Meta-Harness implementation in v0.6 · no Skill/Task/Orchestrator-as-engine/Experiment/Promotion as
substrate primitives.

---

*Prepared as an independent audit lane. This document is advisory and amends nothing. Law remains
[`docs/SPEC.md`](../SPEC.md) → [`docs/05_adr/`](../05_adr/) → [`docs/04_annex/`](../04_annex/).
Every determination recorded in [§6.3](#63-director-decision-checklist) becomes binding only through
a new append-only ADR carrying a bound falsifier.*
