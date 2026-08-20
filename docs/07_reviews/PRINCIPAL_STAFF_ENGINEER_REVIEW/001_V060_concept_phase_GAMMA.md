---
name: v0.6 Concept Lock GAMMA
overview: "Final Principal Staff Engineer Concept Lock for C-level review. Adjudicates four independent advisory lanes against live evidence. Locks ontology, proof obligations, tech stack, and the post-lock engineering sequence. Does not reopen P0 architecture. Does not authorize runtime code in this wave."
todos:
  - id: G0-adjudication
    content: Adjudicate Tech Lead / Architect / AI Specialist / Systems-Eng reviews into this GAMMA lock
    status: completed
  - id: G1-spec-self-review
    content: Finish SPEC v0.6 self-review so no sentence still contradicts ADR-0069–0074
    status: completed
  - id: G2-kernel-amendment
    content: Amend KERNEL.md front-matter destination sentence to cite ADR-0069; do not rewrite S0–S12
    status: completed
  - id: G3-hygiene
    content: CLAUDE.md v0.6.0 pointer; sprint_active superseded note; non-normative banners on review corpus
    status: completed
  - id: G4-exit-gate
    content: Recite Concept Lock exit gate against files; no commit unless C-level asks
    status: completed
  - id: G5-gap-class
    content: Gap/migration classification absorbed into 002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md
    status: completed
  - id: G6-wave0-ci
    content: FIRST CODE WAVE after director approval — CI subject-of-record + named falsifiers (not this wave)
    status: pending
isProject: false
---

# Vanguard / AETHER v0.6 — Concept Lock GAMMA

**Classification:** Final Principal Staff Engineer lock for CTO / CIO / CEO / Engineering Director review.  
**Status:** Concept Lock **complete**. Pre-development foundation ready for Director review. Production coding **not started**.  
**Date:** 2026-08-20  
**Author role:** Principal Staff Engineer / Tech Lead / Architect  
**Relationship:** Successor of the BETA (procedure) and DELTA (status) phase documents (removed at Director consolidation, `ADR-0075`; git history `4f9f8b1`). Incorporates only independently validated conclusions from four advisory lanes.  
**Normative after Director accept:** `docs/SPEC.md` + `docs/05_adr/0069`–`0074` + `docs/04_annex/{KERNEL,MEASUREMENT}.md`. This file is the **lock plan**, not a second SPEC.  
**Operational register:** [002 Foundation Roadmap and Gap Register](002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md).

> **For agentic workers:** G1–G5 are done. Do not migrate runtimes, rewire CI, delete `layer0/`, add Rust, or commit unless the user asks. G6 (Wave 0) is the *next* authorized programme **after Director approval**.

**Goal:** One engineering authority so a billion-scale product can grow from a verified substrate instead of from competing runtimes and false gates.

**Architecture:** One recursive Python agency substrate. Production lattice is `vanguard/packages/`. `layer0/` is a copy-fork to absorb. Ledger is state. Scheduler/kernel are the decision plane. Judge is exterior. Plugins are wire-first. Graphs, swarms, and Meta-Harness are compositions, not engines.

**Tech stack (locked):** Python 3.10+ stdlib core, JSON Schema + RFC 8785 JCS, JSON-RPC 2.0 line-delimited over UDS, SQLite WAL ledger, Ed25519 exterior evaluator, rootless bubblewrap for untrusted exec. Rust / WASM-default / gRPC / multi-host remain behind evidence gates.

---

## 0. What C-level is being asked to approve

Approve **GAMMA** as the v0.6 Concept Lock. That means:

1. The twelve architectural P0s (Python-first, packages canonical, recursive `Agent`, ledger authority, identity trinity, WAL, wire-first plugins, exterior judge, sequential execution, CI subject-of-record, deferred list) **stand**.
2. Four **strengthening amendments** from independent review are adopted into law (via SPEC self-review / a short ADR addendum in the hygiene wave, not a new architecture):
   - **Proof obligations** — every locked concept ships a named falsifier.
   - **Typed budget algebra** — additive dimensions ≠ structural ceilings (`depth`).
   - **Event-kind writer authority** — the orchestrator cannot append privileged truth.
   - **AI-load-bearing identity** — `D_H` includes prompt/ceiling/policy/routes; trajectory schema is locked; model identity is part of `D_R`.
3. `Project` is locked with a one-sentence definition (consistency unit), not as an undefined mandatory field.
4. `ChildPrincipal` is **not** a second type — it is `Principal` with `parent_id`.
5. Skill, Swarm, Orchestrator-as-engine, Experiment, Promotion, Meta-Harness, Cache, Task are **refused as substrate primitives**.
6. The next engineering programme is **this register (002) → Director approve → Wave 0 CI truth + falsifiers → converge → one real coding-agent path**. No Rust rewrite. No third tree. No sprint dates in this lock.

**Reject** if you want a new `vanguard/substrate/` tree, a Rust core, `layer0/` as destination, evaluator-as-plugin, or mid-run harness hot-swap. Those are already adjudicated **no**.

---

## 1. Authority ranking (unchanged)

| Rank | Source | Role |
|---|---|---|
| 1 | This GAMMA lock + ADRs `0069`–`0074` + `docs/SPEC.md` | Law after Director accept |
| 2 | `docs/04_annex/KERNEL.md`, `MEASUREMENT.md` | Normative annexes (S0–S12 not silently rewritten) |
| 3 | Active ADRs `0000`–`0068`, `ADR-M0-01`…`13` | Law unless a newer ADR cites reversal |
| 4 | `principal_engineer_proposal.md` | Conceptual north star; **non-normative**; body/abstract conflict on runtime target already resolved toward packages |
| 5 | Four advisory reviews in `docs/07_reviews/OLD_TECH_LEAD_REVIEW_archive/` | Evidence only |
| 6 | Parecer v4 / Full Refactor v3.1 / Execution Plan / Aether waves | Evidence only |
| 7 | `docs/02_roadmap/`, `docs/03_sprints/` | Historical planning; rewrite is a later phase |

**Conflict rule:** If an advisory review disagrees with (1), record it and keep (1). Do not average architectures.

---

## 2. Adjudication of the four advisory lanes

Advisory inputs were evaluated against the repository and against evidence already gathered on this tree (`c7e9ded`; kernel 95 OK; full suite 1119 / 7 FAIL / 5 ERROR; F1 at `layer0/scheduler/driver.py:138-139`; WAL in packages; MemoryLedger in layer0). They are **not** requirements.

### 2.1 Independent Tech Lead (`00_tech_lead_concept_lock_plan_suggestion.md`)

**Verdict:** Highest-value empirical review. Architecture agrees with GAMMA. Sequencing and lock *quality* improve BETA.

| Claim | Ruling | Action in GAMMA |
|---|---|---|
| Central problem is false gates, not just dual trees | **ACCEPT** | Proof obligations become P0, not a footnote |
| F1 fabricated `VerdictRecorded: pass` | **ACCEPT** (re-verified) | Falsifier: scheduler cannot accept unsigned verdict |
| Four independent fail-open ceiling steps (parse drop, discarded intersect, `ceiling.py:21`, empty `allowed`) | **ACCEPT** | Stronger than BETA’s single fail-open note |
| CI-gated dispatch tests use ADVISORY so grant path is dead | **ACCEPT** as reported | Falsifier: privileged verb requires bound grant |
| Replay-parity folds the same list twice | **ACCEPT** (re-verified) | Falsifier: cold reader from disk |
| `generate_types.py --check` stale; generator can emit invalid Python | **ACCEPT** as reported; not re-run this session | Codegen `--check` is a Wave-0 CI gate |
| Living CI first step can be red (`test_repo_paths`) | **ACCEPT** (re-verified on this tree) | Docs hygiene / Wave 0, not architecture |
| Lock fewer primitives; refuse Skill/Experiment/Orchestrator/Meta-Harness | **ACCEPT** | Primitive table §5 |
| `project_id` cannot be mandatory while `Project` is undefined | **ACCEPT; MODIFY** | Lock the one-sentence Project definition below |
| Directional convergence + duplication detector (`check_duplication.py`) | **ACCEPT** | Wave 0 gate; deletion only after parity |
| Restore CI *inside* the docs-lock wave | **MODIFY** | Obligations lock now; wiring is Wave 0. Mixing them recreates “docs claim done.” |
| Drop `ChildPrincipal` as a distinct type | **ACCEPT** | One `Principal` type |
| `attenuation._exceeds` treats `None` as non-exceeding | **ACCEPT** as defect to fix in code phase | Fail-closed unbounded child |
| Receipt needs `lease_id` / `grant_digest` | **ACCEPT** as schema refine | Code phase; lock the fields |
| Shrink the P0 set by dropping identity trinity / spawn | **REJECT** | Irreversible if wrong |

### 2.2 Principal Architect (`00_arch_lead_concept_lock_plan_suggestion.md`)

**Verdict:** Correct TCB/plugin split and falsification-criterion habit. Destination-tree proposal is the hazard.

| Claim | Ruling | Action in GAMMA |
|---|---|---|
| Selective convergence; keep packages WAL/evaluator/sandbox/kernel; absorb layer0 broker/SPI | **ACCEPT** | Already ADR-0069 |
| `Agent = Principal + HarnessInstance`; swarm is policy | **ACCEPT** | ADR-0070 |
| Wire-first JSON-RPC/UDS; Protocol is client SDK | **ACCEPT** | ADR-0072 |
| `K` workers `≪` `N` logical agents; sequential until proven | **ACCEPT** | ADR-0073 |
| Per-decision falsification criterion | **ACCEPT** | §4 proof table |
| New canonical tree `vanguard/substrate/` or “canonical layer0/” | **REJECT** | Third identity. Packages *is* the lattice. |
| “packages is legacy” | **REJECT** | Packages is production truth |
| Split `root.py` (1418 LOC) | **ACCEPT as P1 code** | Not a new concept; not this wave |
| packages violated A-1 by having `apps/coding/` | **MODIFY** | `apps/` is a client by design; the defect is coding logic remaining *in* kernel/domain, not the package existing |
| Rust behind measured gate | **ACCEPT** | Already P0-12 |

### 2.3 AI Agentic Systems Specialist (`00_AI-Specialist_lead_concept_lock_plan_suggestion.md`)

**Verdict:** Architecture endorsed. The lock was under-weighting the data exhaust that makes later intelligence *science* rather than folklore.

| Claim | Ruling | Action in GAMMA |
|---|---|---|
| Trajectory digest is content-free (`driver.py` over `{schema, ids, n}`) | **ACCEPT** | Lock `mhf.trajectory/1` schema + emission point |
| No `trajectory.schema.json` on disk | **ACCEPT** as reported | Wave 0 schema file |
| Real `spawn()` lives in packages, mock in layer0 | **ACCEPT** (re-verified) | Canonical spawn is `agency/episode/engine.py` |
| `D_H` currently blind to system prompt, ceiling, approval policy | **ACCEPT** | **Amend P0-6**: those fields MUST enter `D_H` |
| Model identity required for `D_R`; packages has adapters, layer0 has none | **ACCEPT** | `D_R` includes model identity; `IModelProvider` stays first-party port |
| Envelope lineage dropped by `LedgerEmitter.emit()` | **ACCEPT** as reported | Falsifier: every envelope carries lineage |
| Prompt identity is harness identity | **ACCEPT** | Highest-leverage AI correction |
| Skill / Swarm / Meta-Harness are compositions, not primitives | **ACCEPT** | §5 refusals |
| “Missing middle” is a multi-harness *orchestrator engine* | **MODIFY** | Missing middle is attribution + trajectory + compose correctness. Scheduler is the mechanism. Do not mint Orchestrator as a primitive. |
| Model inference as `model.infer` effect | **DEFER (P1)** | Semantic slot later; do not block Wave 0 |

### 2.4 Systems Verification (`00_SYTEMS-ENG_lead_concept_lock_plan_suggestion.md`)

**Verdict:** Conditional accept of the architecture; **no-go** on claiming mathematical guarantees. This is the correct epistemic posture for a high-assurance substrate.

| Claim | Ruling | Action in GAMMA |
|---|---|---|
| `HashIntegrity ⇏ SemanticTruth`; replay of forged events is still false | **ACCEPT** | Writer authority + signed-verdict construction rules |
| 6-D vector is not one additive algebra; `depth` is a path ceiling | **ACCEPT** | **Amend P0-5** budget typing |
| `millis` additive only if defined as charged compute, not wall-clock under concurrency | **ACCEPT** | Lock definition: v0.6 `millis` = charged compute; wall deadline is separate |
| Orchestrator generic-append can forge ledger truth | **ACCEPT** | Event-kind writer matrix is P0 |
| Exactly-once external effects is impossible | **ACCEPT** | Contract is durable intent + reconcile/idempotency (K-47), not exactly-once |
| Signed verdict must bind request/subject/oracle/`D_R`/`D_X`/nonce | **ACCEPT** | Verdict anti-replay in Wave 0/1 tests |
| Bernstein independence: unknown footprint = conflict | **ACCEPT** | Concurrency stays off until selectors over-approximate |
| “Formally verified substrate” as a present-tense claim | **REJECT the claim** | Lock is verification-*oriented*, not verified |
| Conditional accept of Python-first / WAL / exterior judge / sequential | **ACCEPT** | Unchanged |

### 2.5 What GAMMA does *not* take from the corpus

- Rust core, Tokio orchestrator, three-language golden-vector programme as v0.6.
- New top-level `core/` or `vanguard/substrate/`.
- Evaluator as a product plugin.
- Mid-run FrozenHarness hot-swap.
- Byte-identical concurrent ledgers as a general requirement.
- Graph database / workflow DAG engine / swarm engine.
- pytest-as-universal-runner, WASM-default, k8s, NATS.
- Claiming the current implementation already satisfies I-2 / I-4 / I-9.

---

## 3. Locked ontology (P0) — not reopenable without a new ADR

These are the Staff Engineer locks. Implementation PRs do not get to renegotiate them.

### P0-1 Runtime target — ADR-0069

Python 3.10+. One production lattice: `vanguard/packages/` (`domain → ports → kernel → agency → runtime → adapters`; `apps/` is a client). Composition root remains `vanguard/packages/runtime/root.py` until it is *split in place*, not moved to a new tree. No `aether-rust/`. Rust only if a later measured gate fires on a **named** TCB hot path.

**Falsifier:** a merge that adds a third runtime tree, or CI that treats `layer0/` as the sole subject of record after Wave 0.

### P0-2 Dual-tree strategy — ADR-0069

`layer0/` is a nine-day-scale copy-fork, not a destination rewrite. **Converge, do not rebuild.**

Keep from packages: S0–S12 kernel, JCS, SQLite WAL, exterior evaluator, bwrap sandbox, stores, model adapters, episode `spawn()`.  
Promote from layer0: SPI protocols, `jsonrpc.py`, broker/cell, lifecycle FSM, compose digest shape.  
Delete duplicated layer0 modules **only after** behavioral parity. Add `tools/check_duplication.py` so the fork cannot recur.

**Falsifier:** a second selector algebra above similarity threshold, or deletion of layer0 jsonrpc before packages speaks it on the canonical path (it already imports it).

### P0-3 Authority — ADR-0071, strengthened

Decision plane (scheduler / kernel / grant issuer / governor) decides who / when / lease / budget / capability.  
State plane (ledger + pure reducers) is what happened.

```text
Decision → DurableEvent (legal writer) → fold → EffectiveState
```

Orchestrator/plugin memory is never source of truth. `Projection = f(Ledger)`. `Cache = g(Ledger, CAS)`.

**New:** event-kind **writer authority**. Untrusted coordination MUST NOT append `CapabilityGranted`, `BudgetReleased`, `VerdictRecorded`, or other privileged kinds. A policy may *request*; only the owning authority may *originate*.

**Falsifier:** a test obtains the orchestrator append API and inserts `VerdictRecorded` or `CapabilityGranted` without the owning authority.

Also: `HashIntegrity ⇏ SemanticTruth`. Folding forged events is deterministic fiction.

### P0-4 Recursive machine — ADR-0070, refined

```text
Agent    = Principal + HarnessInstance
SubAgent = Principal(parent_id=…) + HarnessInstance     # same type, not ChildPrincipal
```

Swarm = N agents + coordination **policy**. Graph relations are **projections of events** (ADR-0003). No workflow engine, no graph DB, no swarm engine, no `MetaLoopEngine`.

`Agent` is a definition, never a privileged runtime subclass hierarchy (`SwarmAgent`, `CriticAgent`, …).

### P0-5 Spawn and resources — ADR-0070 / ADR-M0-07, algebra corrected

**Capabilities:** `C_child ⊆ C_parent` under **one** selector partial order. Unknown / undefined relation = **deny**. Unbounded child under bounded parent = **deny** (fix `_exceeds`/`None`).

**Budget — two algebras, not one:**

| Kind | Dimensions | Rule |
|---|---|---|
| Additive conserved | `usd_micros`, `tokens`, `bytes`, charged `millis` | `child ≼ remaining(parent)` component-wise; parent remaining decreases when child reserves |
| Structural ceilings | `depth`, `turns` (episode/turn caps) | `child.depth = parent.depth + 1 ≤ root.max_depth`; sibling depths are **not** summed |

v0.6 `millis` means **charged compute time**, not wall-clock under future concurrency. Wall deadline is a separate constraint if ever added.

**Project (minimum definition, now locked):**

> A **Project** is a durable named scope that owns one ledger stream, one capability ceiling, and one root budget. Every Episode, Principal, and Artifact belongs to exactly one Project. `project_id` is the consistency unit: total order holds inside a Project, not across Projects.

If an implementation cannot yet persist Project rows, it still MUST stamp `project_id` (even as a single default project) so the corpus is not born without a consistency unit.

### P0-6 Identity trinity — ADR-0071, AI-amended

- `D_H` = digest of **full behavior-affecting composition**: resolved manifest, plugin digests, **system prompt**, **capability ceiling**, **approval policy**, **model routes**. Two harnesses that differ in any of these MUST differ in `D_H`. FrozenHarness digest is `D_H` only. **Prompt identity is harness identity.**
- `D_R` = `H(D_H ∥ runtime ∥ environment ∥ model identity ∥ oracle identity)`.
- `D_X` = `H(D_R ∥ dataset ∥ protocol)`.

A/B measurement MUST NOT collapse these.

**Falsifier:** two manifests differing only in system prompt compile to the same `D_H`.

### P0-7 Ledger / CAS / replay — ADR-0071

`State = fold(Events)`. Snapshots are optimization. CAS holds bytes; events hold refs. Blob `write → fsync → emit(digest)` order stands. SQLite WAL (ADR-0010). Inbox/outbox (ADR-0062) kept.

Replay taxonomy (do not conflate):

| Kind | Bar |
|---|---|
| State replay | Grants, budgets, approvals, episode FSM from disk |
| Schedule replay | Needs recorded nondeterminism (clock, RNG, cassettes) |
| Real-world re-execution | Not required to match |
| Byte-identical fixtures | Fully controlled inputs only |

Concurrent executions are **not** required to produce byte-identical ledgers.

**Falsifier:** `fold(list) == fold(same list)` presented as I-4.

### P0-8 Plugin boundary — ADR-0072

Wire is the contract: JSON-RPC 2.0, line-delimited, UDS. Python `Protocol` is a client. `in_process` is a privilege that still speaks the wire (loopback). Five SPIs (ADR-M0-03): Planner, Memory, Toolkit, Context, EvaluationGate. Model/sandbox/stores remain first-party ports in v0.6.

ADR-0005 stands: freeze at composition. No mid-run FrozenHarness hot-swap. Quiesce is for fault/restart.

Mechanism below the line: identity, authority, effect mediation, event semantics, resource conservation, plugin lifecycle, scheduling, **trajectory emission**.  
Strategy above the line: planner, memory, context, compression, indexing, AST, heuristics, tools, skills, model routing, reflection, Meta-Harness strategies (deferred).

Walking skeleton (ADR-M0-13) on the **canonical** path before product plugins migrate.

### P0-9 Evaluator — ADR-0072 / ADR-0004 / ADR-M0-08

Exterior signed judge. `IEvaluationGate` only requests. Scheduler **reads** a signature-valid, request-bound verdict. Fabricating `"pass"` is defect **F1**.

Signed statement MUST bind: evaluation request id, subject digest, oracle identity, `D_R`/`D_X` as applicable, single-use nonce. Authenticity ≠ oracle validity; anti-replay is mandatory.

**Falsifier:** `emit(VERDICT_RECORDED, {verdict: "pass"})` can complete an episode as success.

### P0-10 Concurrency — ADR-0073 / I-11

Sequential execution. Independence groups may be *declared*. Unknown selector footprint = conflict, not independence. No vector clocks, NATS, k8s. Logical agents are cheap; workers are bounded (`K ≪ N`). Enable concurrency only after selector soundness + race tests.

### P0-11 CI subject of record + proof obligations — ADR-0073, now P0 not P1

The production lattice is the CI subject of record. Lexical E-COV is **not** I-2. TCB-LOC is not kernel correctness. Living CI that greens a self-signing judge is a **credibility failure**.

Every P0 concept in this document is locked **together with** the falsifier in §4. A concept without a bound falsifier is an announcement, not a lock.

**Wiring** those tests and the workflow file is **Wave 0 of the code programme**, not a silent edit inside this docs wave. The lock makes shipping without them a spec violation.

### P0-12 Deferred / rejected as v0.6 scope — ADR-0073

Deferred: Meta-Harness promotion, DPO harvest productionization, self-updating release pipeline (ADR-0019), heterogeneous swarms, market allocator, WASM-default, remote attestation, multi-host, graph DB, competence graph, pytest-as-universal-runner, model/sandbox behind plugin wire, `root.py` split (implementation), concurrency enablement.

Rejected as architecture: third runtime, swarm engine, workflow DAG engine, evaluator-as-plugin, hot-swap, Rust rewrite, byte-identical concurrent ledger as a general law.

---

## 4. Bound falsifiers (the lock’s immune system)

No P0 enters GAMMA without (a) one-sentence definition, (b) a test name, (c) the wrong implementation it rules out.

| Locked concept | Bound falsifier | Wrong implementation it rules out |
|---|---|---|
| Envelope lineage | `test_every_emitted_envelope_carries_full_lineage` | `LedgerEmitter.emit()` dropping `episode_id` / causation |
| `State = fold(Events)` | `test_cold_reader_reconstructs_live_state_from_disk` | Folding the same in-memory list twice |
| Evaluator exteriority | `test_scheduler_cannot_produce_a_verdict_without_a_signature` | `driver.py:138` fabricated pass |
| Verdict binding | `test_replayed_or_unbound_signature_is_rejected` | Bare Ed25519 blob without request/nonce |
| Writer authority | `test_orchestrator_cannot_append_privileged_kinds` | Generic `append(any Event)` |
| Capability ceiling | `test_declared_ceiling_survives_compilation_and_denies` | `_parse` ignoring `capabilities:` |
| Fail-closed authority | `test_empty_ceiling_denies_everything` | `if not capabilities: return True` |
| Grant path | `test_privileged_verb_requires_a_bound_grant` | ADVISORY-only CI fixtures |
| Spawn attenuation | `test_child_grant_wider_than_parent_is_denied_whole` | layer0 spawn stub |
| Depth algebra | `test_sibling_depths_are_not_summed` | `Σ depth_child ≤ depth_parent` |
| `D_H` completeness | `test_prompt_or_ceiling_change_changes_digest` | Digest over refs only |
| Trajectory | `test_episode_completed_emits_schema_valid_mhf_trajectory_1` | Digest over `{ids, n}` |
| Generated types | `generate_types.py --check` in CI | Hand-edited `DO NOT EDIT` file |
| Durable intent (K-47) | `test_intent_survives_process_death` | `self.intents.append` only |
| Budget lineage | `test_child_budget_debits_parent_remaining` | Independent child wallets |
| No duplicate kernel | `tools/check_duplication.py` | Second selector algebra |
| CI subject | living workflow runs `test/kernel` + packages suites | `test/layer0` as sole behavioural gate |

Twelve of these currently fail on `main`. That is the point of locking them.

---

## 5. Primitive vocabulary (lock vs refuse)

**Rule:** lock a concept only if getting it wrong forces a ledger migration or a kernel rewrite.

### 5.1 Substrate primitives (lock)

| Primitive | Note |
|---|---|
| `Project` | Consistency unit — definition in P0-5 |
| `Principal` | Typed `(id, parent_id?, depth)`, not a bare `str` |
| `HarnessManifest` / `FrozenHarness` / `HarnessInstance` | `D_H` complete |
| `Episode` | Bounded execution; tool ≠ episode (ADR-M0-12) |
| `Event` / `EventEnvelope` | Lineage fields mandatory |
| `EffectRequest` | One schema (I-1) |
| `Receipt` | Add `lease_id`, `grant_digest` |
| `ArtifactRef` / `BlobRef` / CAS | Bytes in CAS, refs in events |
| `Capability` / `Grant` / `Scope` | Descriptor-bound; one selector algebra |
| `Reservation` / `Lease` | Typed dimensions; parent lineage |
| `SinkClass` | Registry-derived, not caller-supplied |
| `SignedVerdict` / evaluator identity | Reducer rejects unsigned |
| `Trajectory` record | Schema + emitter; not the harvest pipeline |
| `Scheduler` | Sequential mechanism |
| Five SPIs | Shape only; implementations are plugins |

### 5.2 Definitions, not types

| Name | Meaning |
|---|---|
| `Agent` | `Principal + HarnessInstance` |
| `SubAgent` | Agent whose Principal has `parent_id` |
| Graph / causality | Projection of events |

### 5.3 Explicitly refused as v0.6 primitives

Skill, Task, Cache, Orchestrator-as-engine, Swarm, MetaAgent, ChildPrincipal (as a second type), Experiment, Promotion, Meta-Harness, Workflow/DAG, GraphDB, competence graph.

These may exist later as **artifacts, plugins, or policies**. They must not grow engines.

---

## 6. Theory — what kind of system this is

### 6.1 Product thesis

Vanguard is not “a coding agent with a kernel attached.” It is a **fail-closed effect machine** + **content-addressed harness compiler** + **unreachable judge**. Coding is Domain Pack #1, the first *witness* of generality, not the ontology.

The one-sentence identity remains: **what solved it must be separable, and the judge must be unreachable from the judged.** F1 is the existence proof that CI can invert that sentence while staying green.

### 6.2 Agentic thesis (research, not a claim of AGI)

Competence should enter as:

```text
new capability → plugin + manifest → existing substrate
```

If each new domain requires `NewDomainEngine` / `NewSwarmEngine` / `NewMetaEngine`, the abstraction has failed. That hypothesis is **falsifiable**. GAMMA does not claim it is already true.

SOTA patterns (ReAct, Reflexion, tool-calling, routers, skill libraries, debate, DPO) map as **planner/memory/context plugins and lab processes**, not new kernels. The packages episode loop is already a strong ReAct-class loop with unusually strong authority mediation and unusually weak **data exhaust**. v0.6 repairs exhaust (trajectory, lineage, `D_H`/`D_R`) so later learning is possible without a corpus migration.

### 6.3 Four planes

```text
STRATEGY   planner, memory, context, tools, skills, routing, reflection     (plugins, frozen at compose)
DECISION   scheduler, kernel S0–S12, grants, governor, plugin lifecycle     (mechanism; never source of truth)
STATE      ledger, pure reducers, CAS                                       (authoritative)
EVIDENCE   exterior evaluator, signed verdicts, trajectories, lab           (unreachable from the judged)
```

### 6.4 Compositional measurement (later; structurally anticipated now)

Without complete `D_H` and trajectories, A/B of prompts, tools, or models is undefined. GAMMA locks the *denominators* (`D_H`, `D_R`, `D_X`, `mhf.trajectory/1`). It does not lock a promotion controller.

---

## 7. Tech stack and TCB

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.10+ | As-built; ADR-0063; team-sustainable |
| Contracts | JSON Schema 2020-12 + JCS | One schema, many languages later |
| Plugin wire | JSON-RPC 2.0 / UDS | Exists (`layer0/spi/jsonrpc.py`); polyglot; ADR-0002/0059 |
| Ledger | SQLite WAL, `BEGIN IMMEDIATE` | Exists; single-node linearization; ADR-0010 |
| Eval | Separate process, Ed25519, UID 10002 | Exists in packages |
| Sandbox | Rootless bwrap for `proc.exec` / `patch.apply` | Exists; container tier regardless of plugin isolation |
| Models | First-party ports (OpenRouter, Ollama, cassette, …) | Real in packages; not a sixth SPI in v0.6 |
| CLI | TypeScript Ink (`@vanguard/cli`) | Client, not control plane |
| Tests | `unittest` | pytest migration deferred |
| Rust / WASM / gRPC / k8s | Behind evidence gates | Not v0.6 |

**Trusted core (must stay small and fail-closed):** JCS + envelope + fold; principal/grant/attenuation; S0–S12; governor; plugin lifecycle; scheduler mechanism; writer-scoped ledger append; trajectory emission; evaluator *gateway* (not the oracle).

**Not TCB:** planners, memory engines, AST, repo-map, prompts, model routing, skills, CLI, lab statistics.

---

## 8. Methodologies (how we will build after the lock)

1. **Evidence before assertion.** No gate that a lazy false implementation can pass. Planted negatives for F1, empty ceiling, writer forgery, tautological replay.
2. **Strangler with a detector.** Absorb contracts into packages; delete duplicates after parity; `check_duplication.py` so the fork cannot recur.
3. **TDD on falsifiers.** Wave 0 writes the failing tests first, then makes them pass on the canonical path.
4. **Fail-closed defaults.** Empty set ≠ universal grant. Unknown selector ≠ independent. Unsigned verdict ≠ pass.
5. **Activation-bundle rule (I-3).** A control does not merge without its production call site.
6. **Walking skeleton before product plugins (ADR-M0-13).** Echo plugin full lifecycle on packages path.
7. **One real path before fan-out.** Foundation stops only when one coding-agent E2E is true (model, authorized effect, filesystem, sandbox, signed eval, WAL, replay, trajectory, one runtime authority).
8. **No speculative engines.** If it can be a plugin or a projection, it is not a kernel feature.

---

## 9. Evidence snapshot (this tree)

Re-run for forensic/DELTA; not inherited from parecer `99d1e0b`. Advisory lanes used nearby HEADs (`c5d5fb5`, `60c0cba`); material defects (F1, MemoryLedger, fail-open ceiling, tautological replay, kernel-not-in-CI) are stable.

| Surface | Result | Meaning |
|---|---|---|
| `test/layer0` | 25 OK, ~0.014s | CI-certified theatre |
| `test/packs` | 27 OK | Pack + I-6/I-7 fixtures |
| `test/kernel` | 95 OK, **not in living CI** | Real oracle, uncertified |
| `test/runtime` | 400 ran, 3 FAIL (Ollama label) | Env-sensitive |
| Full `test/` | 1119 ran, 7 FAIL, 5 ERROR, 8 skip | Not green |
| Living CI | `test/layer0` + packs + lexical tools | Wrong subject |
| `check_stale_paths` / `test_repo_paths` | FAIL `docs/sprint6B` on this tree | CI would be red |
| E-COV | “40 kinds, 100%” | False confidence |
| `root.py` | 1418 LOC | God-object, outside TCB glob |
| F1 | `driver.py:138-139` | Self-signing judge |
| Ceiling path | parse drop + discarded intersect + fail-open | Composition identity discarded |
| WAL | packages `PRAGMA journal_mode=WAL` | Real store |
| jsonrpc | packages toolkit already imports layer0 codec | Convergence started accidentally |

---

## 10. Status of *this* lock wave (docs)

| Item | Status |
|---|---|
| Forensic report (25 sections) | **DONE** — `docs/07_reviews/VANGUARD_V060_FORENSIC_DISCOVERY.md` |
| Concept-lock prompt | **DONE** — `docs/07_reviews/PROMPT_ARCHITECTURE_CONCEPT_LOCK_V060.md` |
| ADR-0069…0073 | **DONE** |
| ADR-0074 (proof, typed budget, writer, complete `D_H`, Project, trajectory) | **DONE** |
| ADR INDEX + M0 rows | **DONE**; `0067` remains a documented hole |
| SPEC v0.6 self-review vs `0069`–`0074` | **DONE** |
| KERNEL.md destination amendment + MEASUREMENT deferred note | **DONE** |
| CLAUDE.md / AGENTS.md / sprint_active / review banners / roadmap banners | **DONE** |
| Foundation roadmap + gap register | **DONE** — `002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md` |
| Runtime / CI code | **NOT STARTED** (correct) |
| Commit | **DEFERRED** until Director / user asks |

**Concept Lock docs wave is green.** Remaining work is Director approval, then Wave 0 — not more architecture.

---

## 11. Remaining docs work (G1–G4) — **complete**

1. SPEC self-review: demote E-COV; retitle §8.2; mark §4–§7 as deferred/Wave-4; add §9 bans; put complete `D_H`, typed budget, writer matrix, Project definition, trajectory schema, Receipt fields into law. **Done.**
2. KERNEL.md: destination amendment citing ADR-0069/0074; S0–S12 body unchanged. MEASUREMENT.md deferred-blueprint note. **Done.**
3. Hygiene: CLAUDE.md / AGENTS.md v0.6.0 pointers; `sprint_active.md` superseded; banners on Principal-review files and historical roadmap. **Done.**
4. Exit-gate recitation against files. **Done** (this section + §14.1).
5. Gap register absorbed into `002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md` (G5). **Done.**

No CI YAML. No F1 code fix. No `root.py` split.

---

## 12. Post-lock engineering sequence (planned, not currently executing)

Director visibility. **Not authorized until Director approval of GAMMA + 002.** No calendar dates in this lock (dates in a lock become fake certainty). The living copy of this sequence is `002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`.

```text
G1–G4 docs hygiene
    → C-level accept GAMMA
    → Gap / migration classification (one matrix: SPEC×ADR×packages×layer0×tests×CI)
    → Single operational plan (this sequence, not five reviews)
    → Wave 0  CI truth + falsifiers
    → Wave 1  Kill F1 / fail-closed ceilings / lineage / D_H / trajectory schema
    → Wave 2  Converge (absorb SPI/broker; duplication gate; parity; then delete dupes)
    → Wave 3  Walking skeleton on packages path; begin pack extraction
    → Wave 4  One real coding-agent E2E  ← foundation stop
    → Only then: extra packs, controlled concurrency, richer memory/context,
                 multi-agent policy, experimentation, Meta-Harness
```

### Wave 0 — Restore engineering truth

- Living CI runs `test/kernel` (already 95 OK), plus runtime/agency/adapters (quarantine env-sensitive Ollama tests).
- Wire `generate_types.py --check`, duplication detector, and the §4 falsifiers that can be expressed as tests.
- Fix stale `docs/sprint6B` path so living CI’s first step is not red for an archive citation.
- Do **not** treat a green layer0 suite as success.

### Wave 1 — Irreversible substrate on the canonical path

- Scheduler/engine **reads** signed, request-bound verdicts; F1 cannot complete a run.
- Compiler reads capabilities/prompt/policy; intersection stored; empty ceiling denies.
- Envelope lineage by construction; `LedgerEmitter` cannot drop episode/causation.
- `mhf.trajectory/1` schema file + emission at `EpisodeCompleted`.
- One selector algebra; `_exceeds(None)` fail-closed.
- Writer-scoped append for privileged kinds.

### Wave 2 — Converge without a third tree

- Packages remains the tree. Port layer0 SPI/jsonrpc/lifecycle *in*.
- Parity gate, then delete duplicate layer0 kernel/scheduler/mocks.
- Split `root.py` **in place** (compiler / session / ledger bridge / wiring), not `vanguard/substrate/`.

### Wave 3 — Extensibility foundation

- Manifest → Resolve → Verify → Freeze → FrozenHarness on packages.
- Echo plugin over UDS.
- Coding-specific behavior continues extracting into `packs/code-default/`; domain stays blind.

### Wave 4 — Foundation E2E (stop condition)

Must all be true on one path:

real model · real authorized tool/effect · real filesystem change · real sandbox · real exterior signed eval · real WAL · real cold replay · schema-valid trajectory · no duplicate runtime authority.

**Do not** start heterogeneous subagents, swarm policy, or Meta-Harness before Wave 4 is green.

---

## 13. P1 registry (LOCK NOW vs DEFER)

| ID | Item | Classification |
|---|---|---|
| P1-1 | Envelope lineage fields + emitter fix | LOCK NOW (semantics); implement Wave 1 |
| P1-2 | Trajectory schema + emission | LOCK NOW; implement Wave 1 |
| P1-3 | Complete `D_H` inputs | LOCK NOW; implement Wave 1 |
| P1-4 | Writer authority matrix | LOCK NOW; implement Wave 1 |
| P1-5 | Typed budget algebra | LOCK NOW; implement Wave 1 |
| P1-6 | One generated `EffectRequest` | LOCK NOW as I-1; codegen Wave 0/1 |
| P1-7 | Walking skeleton on packages path | LOCK NOW as sequencing; Wave 3 |
| P1-8 | `in_process` still speaks the wire | LOCK NOW as rule |
| P1-9 | Receipt `lease_id` / `grant_digest` | LOCK NOW as fields; Wave 1 schema |
| P1-10 | Split `root.py` in place | DEFER to Wave 2 |
| P1-11 | Model/sandbox behind plugin wire | DEFER |
| P1-12 | `model.infer` as kernel verb | DEFER (P1+, not Wave 0) |
| P1-13 | Plugin TS conformance / pytest runner | DEFER |
| P1-14 | Concurrency enablement | DEFER (I-11 measurement) |
| P1-15 | Stale `docs/sprint6B` | Wave 0 hygiene, not architecture |
| P1-16 | Ollama unreachable vs `model_tag_absent` | DEFER (test isolation) |
| P1-17 | Selector `process` vs `generic` | Wave 0/1 contract bug |

---

## 14. Exit gates

### 14.1 Concept Lock (this file’s job) — **RECITED 2026-08-20**

| # | Gate | Evidence |
|---|---|---|
| 1 | Forensic report exists with labeled live evidence | `docs/07_reviews/VANGUARD_V060_FORENSIC_DISCOVERY.md` |
| 2 | ADRs `0069`–`0074` exist; INDEX lists them and `ADR-M0-*` | `docs/05_adr/` + INDEX (`0067` hole documented) |
| 3 | SPEC v0.6 does not call `layer0/` the M1 destination; does not authorize hot-swap; cites P0s including complete `D_H`, typed budget, writer matrix, Project definition, trajectory schema | `docs/SPEC.md` header, §1.0, §1.2, A-5, §8, §9, I-1…I-11 |
| 4 | KERNEL annex destination sentence amended | `docs/04_annex/KERNEL.md` front-matter + lead; MEASUREMENT deferred note |
| 5 | Hygiene notes in CLAUDE.md + AGENTS.md + sprint_active | those files; historical roadmap banners |
| 6 | Advisory reviews remain non-normative | banners on Principal-review corpus |
| 7 | No runtime/CI implementation of Waves 0–4 in this lock wave | no edits to `.github/workflows/`, `vanguard/packages/`, `layer0/` for this purpose |
| 8 | Director can delete BETA/DELTA/advisory files later without losing a locked sentence | those sentences live in SPEC/ADRs; sequence lives in 002 |

### 14.2 Foundation (Wave 4) — later

The E2E list in §12 / 002. Not this engagement.

---

## 15. Risks if GAMMA is not followed

| Risk | Failure mode |
|---|---|
| CI stays on layer0 | Self-signing judge remains “proven” |
| Third tree / Rust now | Split-brain; lose WAL/evaluator/sandbox |
| Lock without falsifiers | Ontology as press release |
| `D_H` without prompt/ceiling | A/B of the actual knobs is blind |
| Trajectories deferred | Episodes during convergence are scientifically lost |
| Additive `depth` | Recursion safety proof is false |
| Generic ledger append | Orchestrator forges history that replays |

---

## 16. Document map (what to keep after C-level review)

**Keep as law:** `docs/SPEC.md`, `docs/05_adr/0069`–`0074` (and prior ADRs), annexes, this GAMMA until archived after Director accept.

**Keep as the operational register:** `002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`.

**Keep as evidence:** forensic discovery, the four advisory reviews, BETA/DELTA (process history).

**Do not keep as competing plans:** Full Refactor v3.1, Execution Plan as destination, Aether wave roadmap, parecer’s `core/` tree, historical M0–M6 as next work.

---

**GAMMA bottom line.** The architecture is the recursive Python substrate with packages as production truth. The independent reviews did not change that. They changed what it means to *lock*: a lock is a set of falsifiers, a typed resource algebra, a writer-scoped ledger, and an identity/trajectory scheme that future intelligence can actually use. SPEC can no longer be quoted against those sentences. The Director packet is GAMMA + 002. Restore CI truth only after approval. Then make one coding-agent path real. Then grow.
