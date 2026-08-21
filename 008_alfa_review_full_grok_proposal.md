# 008 — ALFA REVIEW: Mandate for a General Task-Solving Swarm Meta-Framework

**Leadership 7 executive review, architectural adjudication, and phased technical proposal**

| Field | Value |
|---|---|
| **Document ID** | `008_alfa_review_full_grok_proposal.md` |
| **Prepared by** | The Leadership 7 — Engineering Director · CTO · CIO · Principal Staff Engineer · Principal Systems Architect · Tech Lead · PhD AI Specialist |
| **Prepared for** | The Director of Record, AETHER / Vanguard |
| **Date** | 2026-08-21 |
| **Baseline** | working tree at `e84dfda` (short hash from this pass). Every claim marked **`[VERIFIED]`** was inspected on disk. Claims marked **`[CITED]`** are reproduced from living documents and were not re-executed as tests. Claims marked **`[ABSENT]`** name a path that the briefing cites and that **does not exist** in this tree. |
| **Scope** | Version ladder **v0.6.1 → v0.6.2 → v0.6.3 → v0.7.0 → v0.8.0 → v0.9.0 → v1.0.0**, milestones **M-0 … M-10** |
| **Law consumed** | `docs/SPEC.md` · ADRs `0069`–`0076` · `docs/04_annex/KERNEL.md` · `002` gap register · `003` Director review · `SYSTEM_OVERVIEW.md` · `sprint_active.md` · `milestones.md` |
| **Research consumed (on disk)** | `docs/06_references/WAVE_6_SOTA_RESEARCH_AND_THEORETICAL_SYNTHESIS.md` · `_B.md` · `deepseek-harness_algorithms-ideas.md` · `research_Harness_Builder_Framework.md` · `vanguard_body_detailed.md` · `guidelines.md` |
| **Authority** | **Advisory until ratified.** This file amends nothing. Law remains `docs/SPEC.md` → `docs/05_adr/` → `docs/04_annex/`. §3 contains *draft* text of ADRs `0077`–`0082`. They bind only when committed under `docs/05_adr/` with a Director signature. |
| **Output constraint honoured** | No specification file, ADR, or source file was edited in producing this report. |

---

## Table of Contents

- [§0 · Ten-Minute Executive Briefing](#0--ten-minute-executive-briefing)
- [§1 · Executive Rulings & the Strategic Paradigm Shift](#1--executive-rulings--the-strategic-paradigm-shift)
- [§2 · Adjudication of Open Architectural Tensions T-1 … T-9](#2--adjudication-of-open-architectural-tensions-t-1--t-9)
- [§3 · Drafted Append-Only ADR Catalog — `ADR-0077` … `ADR-0082`](#3--drafted-append-only-adr-catalog--adr-0077--adr-0082)
- [§4 · Phased Milestone Roadmap & Version Ladder](#4--phased-milestone-roadmap--version-ladder-v061--v100)
- [§5 · Theories, Algorithms & Mathematical Formalisation](#5--theories-algorithms--mathematical-formalisation)
- [§6 · Zero-Guesswork Developer Implementation Bridge](#6--zero-guesswork-developer-implementation-bridge)
- [§7 · Repository Hygiene & Document Update Cascade](#7--repository-hygiene--document-update-cascade)
- [Appendix A · Forensic Verification Log](#appendix-a--forensic-verification-log-this-pass)
- [Appendix B · Findings Unique to This Pass](#appendix-b--findings-unique-to-this-pass)
- [Appendix C · External Sources](#appendix-c--external-sources)

---

## §0 · Ten-Minute Executive Briefing

### 0.1 The one-paragraph verdict

AETHER already has a **generic authority kernel** (A) and a **generic identity trinity** (D). It does not yet have a **generic composition algebra** (B) or a **learnable corpus** (C). The living lattice is hexagonal and fail-closed where Wave 1 required it to be. The remaining work is not a new engine. It is to (1) stop emitting hollow trajectories **this wave**, (2) replace the five-slot `harness.yaml` with a **named component graph that actually wires**, (3) absorb and delete `layer0/` behind negatives that the current plugin FSM cannot satisfy, and (4) keep the M-4 nine-row stop line inviolable. Swarm, debate, tree search, and meta-cognition are **pack + policy + spawn topology** after that stop line, not before.

### 0.2 What this pass refuses to rubber-stamp

The master briefing (`docs/00_overview/SYSTEM_OVERVIEW.md` §4) indexes principal reviews `004`, `005`, `006` and research files named `RESEARCH_k3_harness-suggestion.md`, `RESEARCH_THEORETICAL_SYNTHESIS.md`, `proposal_glm_harness_BETA.md`, and `proposal_hy3_improved.md`. **`[ABSENT]`** On this working tree, `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/` contains only `001`, `002`, and `003`. `docs/06_references/` contains six files, none of those names. A Leadership 7 that cites a ghost corpus is committing the same class of error as `assemble_trajectory` emitting `_ZERO_COST`: **schema-shaped index, empty bytes**. This document therefore grounds B/C decisions in **on-disk law + on-disk code + 2026 literature**, and treats the missing reviews as *optional later input*, not as settled mandate.

### 0.3 The six rulings, one line each

| # | Ruling | Vehicle | Lands |
|---|---|---|---|
| **R-1** | Un-hollow the corpus **now**. Per-turn cost, latency, model fingerprint, verdict-or-explicit-null. Strengthen F-12 so zeros fail. | `ADR-0078` | **v0.6.1 / M-2** |
| **R-2** | `harness.yaml` becomes `mhf.manifest/2`: a **named component graph with an explicit wiring section**. Today's `components` map is a **named bag of file paths**, not a graph. | `ADR-0077` | **v0.6.2 / M-3** |
| **R-3** | Guardrails are **declarable and never forgeable** (absent-vs-forged). `unattributable_for_promotion` is derived, not authored. | `ADR-0079` | **v0.6.2 / M-3** |
| **R-4** | `agent.spawn` is **design-locked now**. Kernel untouched until M-4 closes. Code at M-6. Engine-owned spawn stays until then. | `ADR-0080` | design **v0.6.1**, code **v0.8.0 / M-6** |
| **R-5** | Absorb `layer0/registry` + `layer0/compose` into `vanguard/packages/runtime/`, add `PluginDiscovered` + `PluginVerified`, run NOVA-4, **delete `layer0/`**. | `ADR-0081` | **v0.6.2 / M-3** |
| **R-6** | Publish the **loop-as-mechanism** claim with a bound falsifier. **NOVA-2** (cold suspend/resume from SQLite WAL) is the precondition for ever lifting I-11. | `ADR-0082` | **v0.6.1 / M-2** (NOVA-2) · claim published M-3 |

### 0.4 The paradigm shift, stated once

> **The 2026 literature has decided that two-thirds of multi-agent intelligence is harness, and that LLM-to-LLM chatter is the wrong coordination medium.** AETHER's State Plane (`State = fold(events)` over SQLite WAL, `project_id` as consistency unit) is already the stigmergic substrate those papers are rediscovering. The moat is **separability**: an exterior UID-10002 judge that the worker UID-10001 cannot reach, plus a trajectory that is *contentful enough to train on*. Without R-1, M-10 is an optimiser over zeros.

### 0.5 Stop lines that this body will not move

1. **M-4 Foundation Stop:** nine rows true on **one** uncheated real run (table in §4.4). Temptation to widen the run so it passes is an escalation, not a patch.
2. **Package version** stays `0.4.5b1` until M-4. The Concept Lock is already v0.6.0. The first *product* cut is **v0.6.3** at M-4 exit.
3. **No kernel LOC growth** in v0.6.1 or v0.6.2. First legal TCB growth is `agent.spawn` at M-6, budgeted **≤ 40 logical LOC** against `check_tcb_budget.py` (threshold 1438; last board figure 1359 after 1.3-C).
4. **I-11 sequential execution** stands until NOVA-2 is green **and** the M-7 measurement gate fires.
5. **`research_Harness_Builder_Framework.md` is REJECTED as architecture** (Redis / NATS / Chroma / K8s second core). Mine adapters only.
6. **`vanguard_body_detailed.md` conflicts with ADR-M0-10.** Do not cite cosmology in `docs/` law.

---

## §1 · Executive Rulings & the Strategic Paradigm Shift

### 1.1 The Leadership 7 — consensus, and where it was not unanimous

| Officer | Position | Dissent / condition |
|---|---|---|
| **Engineering Director** | Ratify R-1…R-6. M-4 nine-row stop is absolute. Version cut at M-4 → **v0.6.3**. Ghost-briefing (`[ABSENT]` reviews) is **not** a reason to delay R-1. | *Condition:* a kernel diff before M-4 closes voids the M-4 evidence bundle (`ADR-0080`). |
| **CTO** | Moat is unforgeable evaluation of a **content-addressed harness genome** (`D_H`), not bubblewrap fashion and not kernel LOC. 2026 SOTA (Harness Engineering as discipline; stigmergic / state-centric MAS; ASTRA trajectory+arena synthesis; DMPO multi-turn DPO) confirms the A-B-C-D bet. | *Dissent:* argued to pull an external Terminal-Bench-class run into M-4. **Overruled** — that measures the pack before the pack loads through its own lifecycle. Rescheduled to M-5 as G8, after Pack #2 also exists. |
| **CIO** | Absent-vs-forged is the only audit-stable rule. Unsigned `VerdictRecorded` remains illegal under every composition. Declared `evaluation: none` is a composition property recorded in `D_H` and the trajectory. | *Condition:* `unattributable_for_promotion` is **derived by compose()** from `D_H`. A manifest boolean is a forgery surface. |
| **Principal Staff Engineer** | Gap priority: **G0 ghost briefing (hygiene) → G1 hollow corpus → G2 composition surface → G9 plugin FSM ledger holes → G5 `K ≪ N` / NOVA-2 → G4 guardrails → G3 spawn**. F-08 is stale (board already said so). F-12 as currently written is **not** I-9. | *Note:* `002` §4.3 still describes Wave 0 as current. The board says M-0/M-1 complete, M-2 in flight. **Register drift** is a first-class hygiene item (§7). |
| **Principal Systems Architect** | Lattice `domain ← ports ← kernel ← agency ← runtime → adapters` is not relaxed for the graph. Parse in `domain/`, resolve in `runtime/`, kernel never sees YAML. `mhf.manifest/2` `bindings` are data. | *Dissent:* wants the KERNEL.md mutation-score TCB replacement. **Deferred to M-5**, not refused. LOC gate remains living law until then. |
| **Tech Lead** | Every ruling ships schema + FSM row + named test function + negative checklist. M-3 does not open until **NOVA-1 and NOVA-2 are green**. | *Condition:* `PluginDiscovered` / `PluginVerified` are **new event kinds** → Director-only per `sprint_active.md` escalation list. They ship inside `ADR-0081`, not as a drive-by. |
| **PhD AI Specialist** | Layer 3 (VFE, credit assignment, DPO, McNemar promotion, skill Elo) is **undefined** on `_ZERO_COST` rows. Formalism in §5 is the *consumer spec* for R-1, not a Wave-2 implementation. | *Dissent:* wanted `attribution.prefix_hits` required at M-2. **Compromise:** emitted when known from M-2; **required at M-10**. A required field the pack cannot compute is a false green. |

**Standing mandate:**

> Ship **B** (composition algebra with wiring) and **C** (learnable corpus) before any consumer of either. An optimiser over a forgeable or hollow corpus is not research. It is a lie with a learning rate.

### 1.2 SOTA 2026 alignment — concessions and refusals

#### 1.2.1 Harness engineering is the independent variable

Zenodo 2026 position paper *Harness Engineering: The Meta Layer as a First-Class Discipline* locates reliability in the loop, dispatch, memory, context, verification, and governance — not in the weights. Greyling's 2026 reading of the IEEE MAS survey: **two of three optimisation layers are harness**. Shankar (Jan 2026): domain-agnostic harness + code execution sandbox; product-specific loops are losing.

**Concede.** AETHER's thesis is already this. `D_H` covering prompt, ceiling, approval, and routes is the genome those papers lack.

**Refuse.** Wrapping Claude Code / Agents SDK as "the generic harness" **erases A**. The kernel is not optional middleware.

**CTO claim (publish at M-10, not before):** automated harness search over `D_H`, scored by UID-10002, is the race. Searching against self-reported pass marks is searching noise.

#### 1.2.2 Stigmergy via the State Plane, not \(O(N^2)\) chatter

State-centric MAS work (2026) and swarm layers such as Many Tems (scent field + shared SQLite, zero coordination tokens) independently rediscover **indirect coordination through environmental traces**. Conversational graphs (AutoGen / CrewAI-class) pay tokens per edge.

Let \(N\) be logical agents and \(T\) turns:

\[
\begin{aligned}
\text{message-passing:} &\quad \#\text{msgs} \in \Theta(N^2 T),\quad \text{context bytes} \in \Theta(N^2 T \lvert A\rvert) \\
\text{stigmergy on WAL:} &\quad \#\text{appends} \in \Theta(N T),\quad \text{reads} \in \Theta(N T \lvert \Delta\rvert)
\end{aligned}
\]

**`[VERIFIED]`** `SqliteEventStore` uses `PRAGMA journal_mode = WAL` and `synchronous=FULL`. `project_id` is the consistency unit (ADR-0071, `002` lock table). Causal relations are **projections** (ADR-0070 §4), not a graph database.

**Refuse.** CRDTs, MESI-style coherence, and NATS buses. They trade the total order for concurrency I-11 has not released. Revisit only if M-7's measurement gate demands it.

**Name at M-7 in SPEC §1.4:** *Stigmergic Coordination Property* — measured messages-per-turn remain \(\Theta(N)\) as \(N\) scales, or the property is refuted (M-9 gate).

#### 1.2.3 Capability sandboxing and provenance DAGs

2026 industry guidance (NVIDIA, Augment, Northflank) treats **shared-kernel containers as insufficient** for untrusted agent code and prefers Firecracker/Kata microVMs; Claude Code's bubblewrap remains opt-in. Signed provenance DAGs (e.g. `agent-provenance-dag`) are appearing as portable trust envelopes.

**Concede the threat model.** K-01 already says a logical mediator is not a containment boundary. UID split 10001/10002 + rootless bwrap is the **as-built** perimeter, not the asymptotic one.

**Refuse for foundation.** MicroVM migration is **not** an M-2–M-4 item. It is an M-9+ measurement if bwrap's shared kernel is the residual risk that actually bites. Chasing 2026 sandbox fashion before the nine-row run is how programmes miss their stop line.

**Provenance.** AETHER already has a receipted effect DAG in the ledger (`EffectStarted` → terminal, `grant_digest`, `lease_id`, `ChildSpawned`/`ChildReturned`). Do not import a second provenance product. Project it.

#### 1.2.4 Trajectories, ASTRA, and DPO

ASTRA (arXiv:2601.21558, 2026) synthesises tool-call-graph trajectories and **rule-verifiable Python arenas** for SFT then online RL — the field is starving for *verifiable* multi-turn data. DMPO (EMNLP 2024) extends DPO to multi-turn agents via occupancy-measure constraints and length normalisation. TRACE (arXiv:2607.13988, Jul 2026) assigns turn-level credit from a frozen reference model's gold-answer log-probability TD, **keeping the verifier as final arbiter**. CAR (2026) uses `do`-interventions because LLM-judge step attribution is ~14% accurate.

**Concede.** Hollow trajectories make all of the above undefined. R-1 is the data-plane prerequisite.

**Refuse TRACE's frozen LLM as AETHER's judge.** The exterior signed oracle is the gold. Frozen probes may be **advisory credit** inside Pack-scoped learners at M-10, never writers of `VerdictRecorded`.

**Refuse ASTRA-style environment synthesis inside the kernel.** Arenas are **packs**. The substrate provides the WAL, the ceiling, and the judge.

### 1.3 A-B-C-D, restated as operational law

| Letter | Meaning | On-disk status **`[VERIFIED]`** | This mandate |
|---|---|---|---|
| **A — Authority** | S0–S12, attenuation, 6D reservation, writer table | `kernel/dispatch.py` documents the sequence; `PRIVILEGED_KIND_OWNERS` in `runtime/ledger_emitter.py`; TCB gated at ≤1438 | Do not grow until M-6 |
| **B — Bundle** | Manifest → `FrozenHarness` / `D_H` | **Two dialects:** `schemas/mhf/harness_manifest.schema.json` is five slots (`mhf.harness/1`); `domain/artifacts/manifest.py` parses a **named path bag**; `packs/code-default/harness.yaml` is the slot dialect; `agency/manifests/vg-code-default/manifest.json` is the bag dialect | Converge to `mhf.manifest/2` **with wiring** |
| **C — Corpus** | `mhf.trajectory/1` at `EpisodeCompleted` | `runtime/trajectory.py` lines 10, 53, 75 force `_ZERO_COST`. Schema already *allows* fingerprints and attribution. Assembler does not populate them. F-12 asserts required keys exist, **not** that cost is non-zero | NOVA-1 in M-2 |
| **D — Digest** | \(D_H \neq D_R \neq D_X\) | `FrozenHarness.composition_digest` in `manifest.py` **must not** be confused with `D_H` (ADR-0076 §4 already said this) | Keep the split; graph change updates \(D_H\) inputs |

---

## §2 · Adjudication of Open Architectural Tensions T-1 … T-9

Each tension is **ruled**. Options from `SYSTEM_OVERVIEW.md` §5 are the input; the output is a Director-ready decision plus the ADR that will bind it.

### 2.1 T-1 — Manifest shape: slots vs named component graph

**Evidence.**

- **`[VERIFIED]`** `packs/code-default/harness.yaml` is `api: mhf.harness/1` with `plugins.{planner,context,memory,evaluation,toolkits,model_routes}`.
- **`[VERIFIED]`** `schemas/mhf/harness_manifest.schema.json` freezes those keys (`additionalProperties: false` on `PluginBindings`).
- **`[VERIFIED]`** `HarnessManifest.components` is `tuple[tuple[str, tuple[str, ...]], ...]` — a sorted map of **role name → artifact paths**. `vg-code-default/manifest.json` fills seven names (`system_prompt`, `tools`, `context_policy`, `routing_policy`, `approval_policy`, `retrieval_policy`, `skill`). There is **no** `bindings` / `wires` / `edges` field. Two planners cannot be named. A critic cannot subscribe to a proposer except by smuggling inside one plugin.

**Ruling (R-2 / `ADR-0077`): Option B, but not the cheap misreading.**

The cheap misreading is "we already have a component graph." We have a **named bag**. A graph is names **plus** typed edges (who observes whom, who may spawn whom, which evaluation gate binds which terminal). Without edges, debate and tree-search remain engine secrets.

**Compatibility.** Pack #1 keeps slot names as **pack convention aliases** compiled into graph nodes (`planner`, `context`, …) so `code-default` does not churn at M-3. New packs author the graph directly.

**`D_H`.** Still the digest of the full behaviour-affecting composition, now including the wiring section. Principle unchanged; input set grows.

**Deadline.** Before M-4. After M-4 every corpus row is attributed to a superseded shape.

### 2.2 T-2 — Engine-owned spawn vs capability-mediated `agent.spawn`

**Evidence.**

- **`[VERIFIED]`** `EpisodeEngine.spawn` (`agency/episode/engine.py` ~531+) is a privileged engine method. `ProposalKind.SPAWN` exists. ADR-0070 already names `spawn` as the sole delegation primitive.
- **`[VERIFIED]`** The spawn docstring records a **live kernel gap**: `StandardPolicy.authorize` does not check that `request.action` ∈ `requested_scope.actions`; a child narrowed to a read verb can still be authorised for any verb the principal holds unless the **engine refuses to ask**. That containment is currently engine-side, not kernel-side.

**Ruling (R-4 / `ADR-0080`): design now, implement at M-6 (v0.8.0).**

Option B *strengthens* authority: every spawn becomes a leased, receipted, attenuated effect. The objection is **sequencing**, not security. A kernel verb before the nine-row run contaminates the stop-line evidence.

**Design freeze now (non-code):**

- Verb `agent.spawn` / sink class `privileged`.
- Child ceiling = `intersect(parent, request.selector)`.
- Budget: additive dimensions conserved; `depth` increments by 1; sibling depths are not summed (F-10).
- Planner SPI does not gain `spawn()` as a Python handle. It proposes an effect like any other.
- Closing the action-membership hole in `policy.authorize` **is in scope for the M-6 kernel delta**, not a silent Wave-2 fix.

### 2.3 T-3 — Mandatory evaluator vs absent-vs-forged

**Ruling (R-3 / `ADR-0079`): Option B.**

A math pack or a pure-compute optimiser must be allowed to declare `evaluation: none`. The trajectory then carries `verdict: null` and compose derives `unattributable_for_promotion = true`. An unsigned object in `VerdictRecorded` remains illegal (writer table: only `evaluator_gateway`).

**Seven non-negotiables** (substrate, not pack policy):

1. Writer authority on privileged kinds  
2. Envelope lineage  
3. Fail-closed selector inclusion  
4. Ledger-as-truth  
5. Capability attenuation on spawn  
6. Signature required on any *claimed* verdict  
7. JCS as the only digest/signing byte source  

Everything else — daemon presence, sandbox tier, approval policy — is **per-composition and recorded**.

### 2.4 T-4 — Hollow trajectory (G1 / NOVA-1)

**This is a live defect, not a taste question.**

**`[VERIFIED]`** `vanguard/packages/runtime/trajectory.py`:

```text
_ZERO_COST = {"usd_micros": 0, "tokens": 0, "bytes": 0, "millis": 0}
# per-turn cost = dict(_ZERO_COST)
# episode cost  = dict(_ZERO_COST)
```

**`[VERIFIED]`** `test/falsifiers/test_falsifiers.py::TestF12Trajectory` checks required keys and `verdict is None` on abort. It **does not** fail on all-zero cost. Schema-valid zeros satisfy F-12 and violate I-9's intent ("a digest over `{ids, n}` is not a trajectory").

The schema **already** has `model_routes_used[].model_fingerprint`, `attribution`, `execution_digest`. The assembler ignores them.

**Ruling (R-1 / `ADR-0078`): Option A — fix in M-2, now.**

Board vs register disagreement (`sprint_active` carry-to-Wave-4 vs overview's irreversible clock) is **adjudicated**: the clock wins. Trajectories cannot be back-filled; the governor's settled ledger for a past run is gone.

**Minimum content for a non-aborted episode with at least one `ProposalProduced`:**

- Per-turn `cost.tokens` **or** `cost.millis` > 0 **or** an explicit `cost_absent_reason` enumerated field (`cassette`, `no_model`, `aborted_before_infer`) — never a silent zero for a live model turn.
- `model_fingerprint` or explicit null with reason.
- `verdict` object or explicit null (already true for abort).

Cassettes/fakes use `cost_absent_reason`, not fake micros. That is absent-vs-forged applied to **cost**.

### 2.5 T-5 — `layer0/` absorption

**`[VERIFIED]`** Remaining production files: `layer0/compose/compiler.py`, `layer0/registry/{lifecycle,broker,isolation,sandbox,validator,grants,worker}.py`, `layer0/events/{emitter,envelope,store,taxonomy}.py`. No `from layer0` under `vanguard/packages/` (this pass). `pyproject.toml` still `include = ["vanguard*", "layer0*"]`.

**`[VERIFIED]`** `layer0/registry/lifecycle.py` `_EVENT` maps only RESOLVED, ACTIVATED, QUIESCING, RETIRED, FAULTED. **DISCOVERED and VERIFIED emit nothing.** `EventKind` has no `PluginDiscovered` / `PluginVerified`. `PRIVILEGED_KIND_OWNERS` likewise omits them. M-3's "every transition ledgered" gate is **unsatisfiable** on the closed catalog.

**Ruling (R-5 / `ADR-0081`): Option A — absorb, then delete. Not delete-and-rewrite.**

SPEC §1 forbids deleting duplicate kernels until a parity gate. The remaining code *is* the only lifecycle. Rebuild-from-scratch would grow Wave 3 from "absorb + prove" to "write + prove" without a packages twin.

**NOVA-4** (negatives) is mandatory before `rm -rf layer0/`: freeze-at-compose, in-process still speaks JSON-RPC, illegal transitions, writer-authority on plugin kinds, I-7 on the absorbed modules, no `from layer0` left including `pyproject.toml`.

### 2.6 T-6 — Universal turn loop as mechanism

**Ruling (R-6 / `ADR-0082` §A): publish the claim.**

> **Claim UTL-1.** Every agentic algorithm this programme will ship is expressible as **spawn-topology + planner/policy plugins over the single observe→propose→authorize→effect→receipt→evaluate loop**. The loop is not a plugin.

**Bound falsifier UTL-F.** Name an agentic algorithm that cannot be so expressed, with a failed `mhf.manifest/2` composition attempt, within 12 months of ADR acceptance. That is ADR-0070 reversal evidence. Aesthetic preference for LangGraph-style loop plugins is not.

**Why competing harnesses plugin the loop:** they have no A to preserve. Pluginising S0–S12 would be a second kernel.

### 2.7 T-7 — `K ≪ N` and NOVA-2

**Ruling: run NOVA-2 in M-2 (v0.6.1).**

Question: **is continuation reconstructible from the WAL in a fresh process, or does resume require the live `HarnessSession` object?**

- Green → M-7 is a scheduler refactor; I-11 lifts on measurement.
- Red → hidden coupling; M-3 abstractions must not pretend otherwise.

F-02 (cold fold of grants/budgets/FSM) is necessary and not sufficient. NOVA-2 suspends **mid-turn** after S8a intent.

**Tech Lead condition stands:** M-3 does not open on a red or skipped NOVA-2.

### 2.8 T-8 — Documentation collapse

**Ruling: after M-4, not during Wave 2/3.** Target: SPEC + ADR log + one living board. Duplicate deferred/refusal lists (SPEC §9, ADR-0073, `002` §2, `milestones.md`) collapse then.

**Exception:** G0 ghost paths in `SYSTEM_OVERVIEW.md` §4 may be **corrected as hygiene** before M-4 (broken links are not "mid-flight surgery"; they are false evidence). See §7.

### 2.9 T-9 — Five-SPI freeze

**Ruling: freeze stands; it is not eternity.** ADR-M0-03 requires a design review for a sixth SPI. Revisit at M-9 (`9.2-B`) against a mature graph. No sixth SPI in v0.6.x.

---

## §3 · Drafted Append-Only ADR Catalog — `ADR-0077` … `ADR-0082`

> Drafts. Not law until filed under `docs/05_adr/` with Director signature. Numbering continues `0076`. Each states reversal conditions (ADR-0000, ADR-0018).

---

### ADR-0077 — Named Component Graph (`mhf.manifest/2`)

**Status (draft):** proposed · **Owner:** Principal Systems Architect / Tech Lead · **Lands:** M-3 / v0.6.2

**Context.** Two live manifest dialects exist. The MHF schema freezes five plugin slots. The domain parser accepts a named map of artifact paths. Neither encodes edges. `005`-class generality critiques (cited in the briefing, **`[ABSENT]` on disk**) and DeepSeek's "ordered stack of plugin bundles" observation (`deepseek-harness_algorithms-ideas.md`) agree that **privileged slot names are the composition bottleneck**. ADR-0070 already forbids a swarm engine; without a place to *name* topologies, those algorithms hide in `EpisodeEngine`.

**Decision.**

1. Normative composition API is **`mhf.manifest/2`** (schema in §6.1). A composition is:
   - `components`: map of instance id → `{spi, ref, config, ceiling?}`
   - `bindings`: list of `{from, to, kind}` where `kind ∈ {context, observe, evaluate, spawn_grant, route}`
   - `capabilities`, `budget`, `approval_policy`, `system_prompt`, `model_routes` remain first-class `D_H` inputs
2. `mhf.harness/1` remains readable through M-4 as a **compiler frontend** that emits a graph with conventional node ids (`planner`, `context`, `memory`, `evaluation`, `toolkit[i]`, `route[i]`). After M-4 the frontend is pack-local, not law.
3. `D_H` is JCS-SHA-256 over the **resolved** graph (pinned refs + bytes of prompts/policies + ceiling intersection + bindings + routes). `episode_id` is not in `D_H` (ADR-0076 §4).
4. Kernel remains domain-blind. Graph types live in `domain/artifacts/`. Resolution lives in `runtime/compose.py`.
5. SPI freeze (ADR-M0-03) unchanged: instance `spi` must be one of the five.

**Schema (normative excerpt).** Full Draft 2020-12 document: §6.1.

**Bound falsifier `RF-22`.** `test/runtime/test_manifest_v2.py::test_two_planner_instances_plus_aggregator_compose` — a graph with `proposer_a`, `proposer_b`, `aggregator` and bindings `proposer_* → aggregator` composes; `D_H` changes if either ref or an edge changes; the five-slot schema **rejects** the same document.

**Bound falsifier `RF-23`.** `test/packs/code_default/test_harness_v1_frontend.py` — Pack #1 `harness.yaml` still composes to a graph whose node ids include `planner`.

**Reversal.** A required topology that cannot be expressed as components+bindings without a sixth SPI or a kernel change, documented with a failed composition and a newer ADR.

---

### ADR-0078 — Trajectory Content (NOVA-1); I-9 operationalised

**Status (draft):** proposed · **Owner:** Tech Lead / PhD AI Specialist · **Lands:** M-2 / v0.6.1

**Context.** `mhf.trajectory/1` is emitted and schema-valid. Cost vectors are hardcoded zeros. F-12 does not look at magnitudes. I-9 and the schema comments already say a digest over `{ids, n}` is not a trajectory. Every completed episode before the fix is a permanently degraded harvest row (SPEC §7 consumers are deferred, the **bytes** are not).

**Decision.**

1. `assemble_trajectory` MUST populate per-turn and episode `CostVector` from the governor's committed leases and the model adapter's usage accounting. Silent zeros on a turn that invoked a model are a defect.
2. Add `cost_absent_reason`: `null | "cassette" | "no_model" | "aborted_before_infer" | "fake_port"`. Exactly one of (non-zero additive cost on at least one dimension, or a reason) MUST hold per turn.
3. Each turn MUST include `model` `{provider, model_id, model_fingerprint}` or `model: null` with the same reason enum.
4. `millis` is **charged** time (ADR-0074), not wall-clock.
5. `verdict` remains the SignedVerdict object or `null`. No synthesised prose summaries.
6. F-12 is **strengthened** (same test name, new assertions) so all-zero cost without `cost_absent_reason` fails. Kernel annex `F-12` (budget denied) is a **different namespace** — see §7.3. Register spelling becomes **`RF-12`** in new text; the test function name may keep historical `test_episode_completed_emits_schema_valid_mhf_trajectory_1` plus `test_trajectory_cost_not_silently_zero`.
7. `attribution.prefix_hits` MAY be emitted from M-2; MUST be present for promotion rows at M-10.

**Bound falsifier `RF-12b` (NOVA-1).** `test/runtime/test_trajectory_content.py::test_live_or_cassette_turn_has_cost_or_reason` and `::test_model_fingerprint_present_or_reason`.

**Bound falsifier `RF-12c`.** A unit test that feeds `_ZERO_COST` without reason **fails** (negative).

**Reversal.** A hermetic test environment in which no usage signal can exist *and* `cost_absent_reason` cannot be attached. That environment must not write promotion-eligible rows.

---

### ADR-0079 — Absent vs Forged Guardrails

**Status (draft):** proposed · **Owner:** CIO / Principal Staff Engineer · **Lands:** M-3 / v0.6.2

**Context.** Uniform UID-10002 + preregistered oracle maximises assurance and turns infrastructure into a product constraint. Non-coding and compute-only packs then grow illegal escape hatches. The forensic failure mode was **forged pass**, not **declared absence**.

**Decision.**

1. A composition MAY set `evaluation` to a component instance **or** to JSON `null` / YAML `none`.
2. Compose records the choice in `D_H`. Trajectories of such runs have `verdict: null` and derived `unattributable_for_promotion: true` (computed; not a manifest field).
3. `LedgerEmitter` still refuses `VerdictRecorded` from any writer other than `evaluator_gateway`. Gateway still refuses unbound/unsigned bodies.
4. Same pattern for `sandbox_tier: none` and `approval_policy: none` — declared, hashed, never forged.
5. Promotion pipelines (M-10) MUST drop unattributable rows. Lab/research MAY keep them as non-promotable.

**Bound falsifier `RF-24`.** `test/runtime/test_absent_evaluation.py::test_compose_accepts_evaluation_none_and_marks_unattributable`.

**Bound falsifier `RF-25`.** `test/trust/test_forged_verdict_still_illegal.py::test_unsigned_verdict_rejected_even_when_evaluation_none` — absence does not relax forgery.

**Reversal.** A domain pack whose correctness is defined only by an in-process heuristic that cannot be declared as an oracle plugin *and* cannot run unattributable. Then a new SPI review (T-9), not a forged verdict.

---

### ADR-0080 — Capability-Mediated `agent.spawn` (design lock)

**Status (draft):** proposed · **Owner:** Principal Systems Architect · **Design lands:** v0.6.1 · **Code lands:** M-6 / v0.8.0

**Context.** ADR-0070 locked spawn as the only delegation primitive. Implementation is engine-owned. Tree search, hierarchical decomposition, and swarm fan-out as *structure* have nowhere to live except the engine. Kernel change before M-4 would void the stop-line bundle. Engine docstring already records that policy does not enforce action ∈ scope.

**Decision.**

1. **Now (docs only):** specify verb `agent.spawn`, selector shape (child ceiling + brief digest + child harness ref), attenuation `child ≼ parent`, budget conservation, envelope fields `parent_episode_id`, `causation_id`, receipts `ChildSpawned` / `ChildReturned` remaining projections of kernel/runtime events.
2. **Forbidden until M-4 exit:** any `vanguard/packages/kernel/**` diff whose purpose is this verb.
3. **At M-6:** dispatch `agent.spawn` through S0–S12; close action-membership in `policy.authorize`; planner proposes, does not call `EpisodeEngine.spawn` as a Python privileged API. Engine `spawn()` becomes an adapter behind the kernel or is deleted.
4. TCB delta ≤ 40 logical LOC; `check_tcb_budget.py` remains green with headroom.
5. Planner without the grant cannot delegate (`RF-26`).

**Bound falsifier `RF-26` (M-6).** `test/kernel/test_spawn_verb.py::test_planner_without_spawn_grant_is_denied`.

**Bound falsifier `RF-27` (M-6).** `test/kernel/test_spawn_verb.py::test_child_action_outside_child_scope_denied_by_kernel` — the engine-side hole is closed in A.

**Bound falsifier `RF-28` (v0.6.1).** `test/tools/test_no_kernel_spawn_diff_before_m4.py` — optional CI comment gate; human-enforced if too brittle. The **process** falsifier is Director review of `git diff vanguard/packages/kernel` at M-4.

**Reversal.** Same as ADR-0070: a workload that cannot be attenuated spawn under a HarnessInstance without a second engine.

---

### ADR-0081 — Absorb `layer0/` Registry & Compose; NOVA-4; Delete

**Status (draft):** proposed · **Owner:** Tech Lead · **Lands:** M-3 / v0.6.2

**Context.** Wave 2 deleted kernel/scheduler/spi forks. Remaining `layer0/` is the only plugin lifecycle. M-3 claims a walking skeleton on the packages path. The FSM cannot ledger DISCOVERED or VERIFIED. Adding kinds is a Director escalation.

**Decision.**

1. Move lifecycle, broker, isolation, validator, grants into `vanguard/packages/runtime/registry/` (adapters stay in `adapters/` if they touch OS). Compose digest shape merges into `runtime/compose.py` (already the packages compose).
2. Add event kinds `PluginDiscovered`, `PluginVerified` to the schema + codegen + `PRIVILEGED_KIND_OWNERS` (`registry`).
3. Parity gate against `test/layer0` behaviour, then delete `layer0/` and drop `layer0*` from `pyproject.toml`.
4. NOVA-4 negatives (see §6.3) MUST be green before deletion.
5. `in_process` cells still speak JSON-RPC 2.0 (ADR-0072).

**Bound falsifier `RF-29`.** Echo plugin walks DISCOVERED→…→RETIRED over UDS; **seven** transitions emit seven kinds.

**Bound falsifier `RF-30`.** `tools/check_stale_paths.py` fails if `layer0/registry` is still cited as production after deletion.

**Reversal.** Parity gate red: behavioural divergence that would drop a security property. Then repair packages twin; do not keep two lives.

---

### ADR-0082 — Loop-as-Mechanism Claim; NOVA-2 Cold Suspend/Resume

**Status (draft):** proposed · **Owner:** Engineering Director (claim) · Tech Lead (NOVA-2) · **Lands:** M-2 / v0.6.1 (test) · M-3 (SPEC sentence)

**Context.** `002` §5 asserts `K ≪ N`. Nothing demonstrates logical-agent / worker separation. `HarnessSession` holds live state. I-11 forbids concurrency until a measurement gate. Competing frameworks plugin the loop because they have no reference monitor.

**Decision.**

1. Adopt claim UTL-1 and falsifier UTL-F (§2.6). Add one paragraph to SPEC after M-3 compose lands, not before (a claim without a graph is marketing).
2. **NOVA-2:** test `test/runtime/test_nova2_suspend_resume.py`:
   - Run an episode through S8a (`EffectStarted` durable).
   - Process exit.
   - New process opens the same SQLite WAL.
   - Recovery (`runtime/ledger/recovery.py`) probes undeterminable effects.
   - Resume reaches a terminal `EpisodeCompleted` with a trajectory.
3. Green NOVA-2 is **entry** to M-3. Red NOVA-2 is a Director stop: M-3 may not invent a plugin model that assumes schedulable workers.
4. I-11 still does not lift at NOVA-2 green. Lift is M-7 only.

**Bound falsifier `RF-31` (NOVA-2).** The test above, CI-gated, not an in-memory double fold (I-4).

**Bound falsifier `RF-32` (UTL-F).** `docs/05_adr/0082-…` itself is the standing invitation; a later ADR cites it to reverse 0070/0082.

**Reversal of the loop claim.** Successful UTL-F. **Reversal of NOVA-2 as M-3 gate.** Director exception in writing, naming the hidden coupling accepted.

---

## §4 · Phased Milestone Roadmap & Version Ladder (v0.6.1 → v1.0.0)

### 4.1 Mapping

| Version | Milestone | Theme | Package version on disk |
|---|---|---|---|
| Concept Lock v0.6.0 | M-0, M-1 | Truth + trust spine | `0.4.5b1` **`[VERIFIED]`** |
| **v0.6.1** | **M-2 close** | One runtime + NOVA-1 + NOVA-2 + ADR drafts filed | still `0.4.5b1` until M-4 |
| **v0.6.2** | **M-3** | Graph + absent-vs-forged + layer0 deleted | still `0.4.5b1` |
| **v0.6.3** | **M-4 STOP** | Nine-row uncheated E2E | **cut to `0.6.3`** |
| **v0.7.0** | **M-5** | Pack #2 math/deduction + doc collapse | `0.7.0` |
| **v0.8.0** | **M-6** | `agent.spawn` in S0–S12 | `0.8.0` |
| **v0.9.0** | **M-7 + M-8** | Concurrency + declarative topologies | `0.9.0` |
| **v1.0.0** | **M-9 + M-10** | Scale measurement + meta-cognition | `1.0.0` |

v0.6.1/v0.6.2 are **law and gate** versions (ADRs + falsifiers). The PyPI/semver cut waits for the stop line so `0.6.3` means "foundation actually ran."

### 4.2 M-0 and M-1 (historical; do not reopen)

| | M-0 | M-1 |
|---|---|---|
| **Goal** | CI subject of record = `vanguard/packages/` | False gates cannot certify the trust spine |
| **Status** | **COMPLETE** (`milestones.md`) | **COMPLETE GREEN** |
| **Exit** | F-01…F-21 registered; codegen `--check` | F-01…F-15 green; TCB ≤ 1438; signed verdicts; fail-closed ceilings; `D_H`; cold replay |
| **Note** | `002` text still says Wave 0 not started — **stale** (§7) | F-08 stale-as-defect; F-12 green-as-schema only |

### 4.3 M-2 / v0.6.1 — One runtime + corpus + suspend

**Entry.** M-1 green (satisfied).

**Goals.** F-16; zero `layer0` imports under `vanguard/`; kill surfaces deleted; reducer completeness; **NOVA-1**; **NOVA-2**; file ADRs `0077`–`0082` as accepted docs (code for 0077/0079/0081 waits for M-3).

**Out of scope.** Component graph implementation, `layer0/` deletion, kernel spawn, Pack #2, concurrency, M-10 maths in runtime.

**Exit gate.**

- Existing M-2 gate from `milestones.md` (F-16, reducers, no packages←layer0 imports).
- `RF-12b`, `RF-12c` green.
- `RF-31` green.
- ADRs 0077–0082 committed under `docs/05_adr/` (Director).
- `check_boundaries.py`, `check_tcb_budget.py`, `scan_secrets.py` green.
- Kernel LOC delta **0** vs M-1.

**Deliverables.** Cost wiring in assembler + model usage plumbing; NOVA-2 test; ADR files.

### 4.4 M-3 / v0.6.2 — Extensibility (the framework claim)

**Entry.** M-2 green **including NOVA-2**.

**Goals.** `mhf.manifest/2`; v1 frontend for Pack #1; absent-vs-forged; absorb registry/compose; NOVA-4; delete `layer0/`; echo plugin full FSM; I-7 on absorbed code; publish UTL-1 sentence in SPEC.

**Out of scope.** `agent.spawn` kernel verb; nine-row E2E (that is M-4); Pack #2.

**Exit gate.**

- `RF-22`, `RF-23`, `RF-24`, `RF-25`, `RF-29`, `RF-30`.
- `layer0/` directory gone; `pyproject.toml` no longer includes `layer0*`.
- ADR-M0-13 walking skeleton on UDS.

**Wave 3 was under-weighted in `002`.** This mandate **rebalances**: graph + FSM kinds + negatives are in-scope, not footnotes.

### 4.5 M-4 / v0.6.3 — Foundation Stop Line (nine rows, one run)

**Entry.** M-1 + M-2 + M-3 green.

**The nine rows** — all true on **one** uninterrupted `packs/code-default` run, no human in the loop, no cassette substituting for the "real model" row:

| # | Row | Meaning |
|---|---|---|
| 1 | Real model | Not a stub planner |
| 2 | Authorized effect | Kernel grant + lease, not ADVISORY-only |
| 3 | Filesystem change | Durable, receipted |
| 4 | Sandbox | Untrusted exec contained (UID 10001) |
| 5 | Exterior signed eval | UID 10002; no unsigned pass |
| 6 | WAL ledger | Packages `SqliteEventStore`, not MemoryLedger |
| 7 | Cold replay | Reconstruct from disk (I-4) |
| 8 | Trajectory | Schema-valid **and** NOVA-1 contentful |
| 9 | One runtime | No competing scheduler/kernel |

**Escalate, do not absorb:** any proposal to add a tenth row, swap in a fake model, skip sandbox, or "just this once" unsigned eval to make the run pass.

**Out of scope.** Extra packs, swarm policy, concurrency, Meta-Harness, DPO production, microVMs.

**Version cut.** `pyproject.toml` `0.4.5b1` → `0.6.3`.

### 4.6 M-5 / v0.7.0 — Generality proof & consolidation

**Entry.** M-4 closed.

**Pack #2: Math & Formal Deductive Verification** (not TableWorld).

**Why not TableWorld.** **`[VERIFIED]`** `adapters/environment/tableworld.py` and `vg-table-default/` already exist. Turning them on would **not** prove I-7: the adapter is already in the lattice. Pack #2 must be a **new pack directory** (`packs/math-default/`) whose verbs are domain-native (`math.reduce`, `lemma.check`, …) with:

- A **deductive oracle** (Lean/Coq/kernel-checker **or** a hermetic CAS with preregistered lemmas) as UID-10002 suite — **or** `evaluation: none` for compute-only search, which then cannot promote.
- **Zero diffs** under `vanguard/packages/domain/` and `kernel/` (I-7 becomes fact).
- No `pytest` / `ast` / `git` tokens required in the kernel (already forbidden).

TableWorld remains a **lab fixture**, not the generality gate.

**Also M-5.** Doc collapse to Clean Triad (§7). Optional: start TCB mutation-score pipeline (does not replace LOC until green). NOVA-2 at **scale** (N episodes). G8 external harness-effect measurement **after** Pack #1 lifecycle is real.

**Exit.** Pack #2 green; `git diff --stat` on `domain/`+`kernel/` empty for that PR; overview/register/sprint no longer contradict.

### 4.7 M-6 / v0.8.0 — Mediated delegation

**Entry.** M-5 + `ADR-0080` design.

**Exit.** `RF-26`, `RF-27`. Hierarchical decomposition and one tree-search **pack policy** run without engine edits. TCB ≤ 1438 with spawn verb.

### 4.8 M-7 + M-8 / v0.9.0 — Concurrency then builder

**M-7 entry.** M-5, M-6, NOVA-2 historically green.

**M-7 exit.** Selector-disjoint independence groups; zero event loss under backpressure; **I-11 lifted by ADR** citing measurements. `K ≪ N` demonstrated (logical agents > worker processes).

**M-8 exit.** Debate, critic/revisor, evolutionary search as **graphs** in `mhf.manifest/2`. Multi-pack reference suite, **zero** `agency/episode/engine.py` topology `if`s.

### 4.9 M-9 + M-10 / v1.0.0 — Scale and meta-cognition

**M-9.** IPC/serialisation/plugin-call overhead measured; ledger pressure bounded; five-SPI freeze revisited (T-9). Stigmergy \(\Theta(N)\) measurement. Sandbox residual (bwrap vs microVM) **measured**, not sloganeered.

**M-10.** Active inference over \(\mathbf{R}\) (§5.1); credit assignment (§5.2); skill cards Elo-decay (§5.3); unforgeable DPO harvest + paired McNemar promotion (§5.4). All **exterior plugins/policies**. No kernel "learner". Promotion never writes `VerdictRecorded`.

**v1.0.0 meaning.** The substrate is a general task-solving swarm **meta-framework**: new domains are packs; new topologies are graphs; new intelligence is promotion-gated against an unreachable judge.

---

## §5 · Theories, Algorithms & Mathematical Formalisation

> Implementation of this section is **M-10**, except that **symbols must exist in the corpus from M-2**. Equations are the consumer contract for NOVA-1.

### 5.1 Active inference: VFE over the 6D economic tensor \(\mathbf{R}\)

ADR-M0-07 / ADR-0074: reservation is six-dimensional. Split:

\[
\mathbf{R}^{\mathrm{add}} = (R_{\$}, R_{\mathrm{tok}}, R_{\mathrm{B}}, R_{\mathrm{ms}}),\quad
\mathbf{R}^{\mathrm{str}} = (R_{\mathrm{turns}}, R_{\mathrm{depth}}).
\]

Additive dimensions are conserved and committed (S7/S10). Structural dimensions are ceilings (siblings' depths do not sum; F-10).

Let \(\theta\) parameterise a harness genome (the preimage of \(D_H\)). Let \(q_\theta(s)\) be a variational belief over latent task state, \(p(o,s)\) a generative model whose observations \(o\) are **ledger projections** (receipts, oracles), not chat traces.

Variational free energy (Friston; Parr, Pezzulo & Friston; language-mediated AIF 2025–26):

\[
\mathcal{F}(\theta) = \mathbb{E}_{q_\theta(s)}\big[\log q_\theta(s) - \log p(o,s)\big]
= \underbrace{\mathrm{KL}\big(q_\theta(s)\,\|\,p(s\mid o)\big)}_{\text{divergence}} + \underbrace{(-\log p(o))}_{\text{surprise}}.
\]

Policy selection uses **expected** free energy, trading epistemic value (information gain over \(s\)) against pragmatic value (preferred outcomes = signed pass under budget):

\[
G(\pi) = \mathbb{E}_{q(o,s\mid\pi)}\big[\log q(s) - \log p(o,s\mid \tilde{o})\big]
\;-\; \mathbb{E}_{q(o\mid\pi)}\big[\log p(\tilde{o}\mid C)\big]
\]

where \(C\) is the preferred-outcome prior: `verdict=pass` ∧ \(\mathbf{R}^{\mathrm{add}}\) within remaining lease ∧ no `KernelAlarm`.

**AETHER binding.** \(\pi\) is a **path in the component graph plus spawn tree**, not a natural-language conversation. Minimising \(\mathcal{F}\) by forging \(o\) is exactly what UID-10002 exists to make physically hard. If `evaluation: none`, \(p(o\mid C)\) is undefined for promotion; those runs may still minimise a pack-local surrogate, never the global prior \(C\).

**Economic regulariser** (required so VFE does not ignore the governor):

\[
\mathcal{L}(\theta) = \mathcal{F}(\theta) + \lambda^\top \mathbb{E}\big[\mathbf{R}^{\mathrm{add}}\big],\quad \lambda \ge 0.
\]

Without NOVA-1, \(\mathbf{R}^{\mathrm{add}}\) is the zero vector and \(\lambda\) is unidentified.

### 5.2 Trajectory error credit assignment and backward fault isolation

Let a trajectory be \(\tau = (x, a_1, r_1, \ldots, a_T, r_T, v)\) with actions \(a_t\) (proposals), receipts \(r_t\), terminal signed verdict \(v \in \{+1,-1,\bot\}\).

**Gold signal.** \(v\) from UID-10002 when present. \(\bot\) ⇒ no promotion credit (ADR-0079).

**Process signal (M-10 plugin, not kernel).** Receipt outcomes already discretise `{completed, failed, rejected, undeterminable}`. Define a backward isolation pass:

```text
algorithm BackwardFaultIsolation(τ):
    if v is ⊥: return {}                     # unattributable
    credit[T+1] ← 1[v = +1] - 1[v = -1]
    for t = T … 1:
        if r_t.outcome = rejected:           # authority/ceiling — not a model error
            blame[t] ← POLICY
            credit[t] ← 0
        else if r_t.outcome = undeterminable:
            blame[t] ← INSTRUMENT             # do not DPO this turn
            credit[t] ← 0
        else:
            # TD-style: receipt moved evidence toward/away from oracle subject
            credit[t] ← δ(r_t) + γ · credit[t+1]
            blame[t] ← MODEL if |δ| > ε else NONE
    return (credit, blame)
```

\(\delta(r_t)\) is pack-defined (test oracle diff, lemma-check delta, …). **Refuse** LLM-as-judge attribution as writer of `blame` (CAR: ~14% step accuracy). Optional TRACE-style frozen probe may fill \(\delta\) **inside a pack learner**, never as `VerdictRecorded`.

First MODEL-blamed turn with negative credit is the **fault isolation cursor** for repair-round policy (already exists as `runtime/repair.py` / `tier_escalation.py` — keep them **consumers**, not a second judge).

### 5.3 Dense 384-d hybrid retrieval and Elo-decayed skill eviction

**As-built.** `runtime/skill_index.py` is a **character-budgeted name+description prefix**, bodies via `fs.read`. Order is pack-authored. No embeddings, no Elo.

**M-10 skill card** \(c\): `{id, text, embedding ∈ ℝ^{384}, elo, last_used, D_H_range}`.

Hybrid score for query \(q\) (lexical + dense):

\[
s(q,c) = \alpha \cdot \mathrm{BM25}(q, c_{\mathrm{text}}) + (1-\alpha)\cdot \cos(E(q), E(c)),
\quad \alpha \in [0,1].
\]

384-d is the **budgeted** width (small enough for in-prefix optional hints; bodies stay out of the frozen prefix — W12-A).

Elo update after a promotion-eligible episode that **retrieved** card \(c\):

\[
R'_c = R_c + K \big( S - \sigma(R_c - R_{\mathrm{opp}}) \big),\quad
S = \mathbf{1}[v=+1].
\]

Decay (unused cards):

\[
R_c(t) = R_{\mathrm{floor}} + (R_c(t_{\mathrm{used}}) - R_{\mathrm{floor}})\, e^{-\lambda (t - t_{\mathrm{used}})}.
\]

Evict if \(R_c < R_{\mathrm{floor}} + \varepsilon\) **and** not `undeletable`. Eviction is a **pack/index** mutation attributed in \(D_H\) if the index is composition-affecting; otherwise it is runtime state under \(D_R\) and MUST NOT silently change prompts. **Ruling:** skill **catalog** in the manifest is \(D_H\); Elo **ranking** is \(D_R\) unless a promotion freezes a new catalog.

### 5.4 Unforgeable DPO harvest and paired McNemar promotion

**Pair construction (SPEC §7, deferred consumer; contract now).** A preference pair is two trajectories \(\tau^w, \tau^\ell\) with:

- same `task` identity and same `context_digest` on the **paired turn** (schema comment: context digest is the DPO pairing key);
- \(v^w = +1\), \(v^\ell = -1\), both signed, same `oracle_id`;
- \(D_H^w\) vs \(D_H^\ell\) is the **treatment** (harness mutation) **xor** the model fingerprint is the treatment — not both unaccounted;
- `unattributable_for_promotion` false;
- `cost_absent_reason` null on the paired turns.

DMPO-style occupancy objective (length-normalised BT) may be used **outside** the TCB. Standard DPO:

\[
\mathcal{L}_{\mathrm{DPO}} = -\mathbb{E}\log \sigma\Big(\beta \big(\log\tfrac{\pi_\theta(\tau^w)}{\pi_{\mathrm{ref}}(\tau^w)} - \log\tfrac{\pi_\theta(\tau^\ell)}{\pi_{\mathrm{ref}}(\tau^\ell)}\big)\Big).
\]

**Promotion protocol (paired McNemar exact).** Let \(n_{10}\) be tasks the **challenger** harness passes and champion fails, \(n_{01}\) the converse, on a **frozen** preregistered set \(S\) with \(|S| \ge N_{\min}\) (Director sets \(N_{\min}\), suggested 40 for Pack #1 smoke, 200 for v1.0).

McNemar statistic with continuity correction:

\[
\chi^2 = \frac{(|n_{10}-n_{01}|-1)^2}{n_{10}+n_{01}}.
\]

Exact binomial test: under \(H_0\), \(n_{10} \sim \mathrm{Bin}(n_{10}+n_{01}, 1/2)\). Promote iff two-sided \(p < \alpha\) (suggested \(\alpha=0.05\)) **and** no `KernelAlarm` on challenger **and** cost regulariser \(\mathbb{E}[\mathbf{R}^{\mathrm{add}}]\) not worse than champion by a pre-registered margin.

**Refuse.** LLM-as-judge pairwise without oracle. **Refuse.** Promoting on training tasks. \(S\) is sealed before the search.

---

## §6 · Zero-Guesswork Developer Implementation Bridge

### 6.1 Normative Draft 2020-12 JSON Schema — `mhf.manifest/2`

To be filed as `schemas/mhf/manifest_v2.schema.json` at M-3 (not in this PR).

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://vanguard.dev/schemas/mhf/manifest_v2.schema.json",
  "title": "MHF Manifest v2 — Named Component Graph",
  "type": "object",
  "additionalProperties": false,
  "required": ["api", "id", "components", "bindings", "capabilities", "budget"],
  "properties": {
    "api": { "type": "string", "const": "mhf.manifest/2" },
    "id": { "type": "string", "minLength": 1 },
    "components": {
      "type": "object",
      "minProperties": 1,
      "additionalProperties": { "$ref": "#/$defs/ComponentInstance" }
    },
    "bindings": {
      "type": "array",
      "items": { "$ref": "#/$defs/Binding" }
    },
    "system_prompt": { "type": ["string", "null"] },
    "capabilities": { "type": "array", "items": { "type": "object" } },
    "budget": { "$ref": "effect_request.schema.json#/$defs/Reservation" },
    "approval_policy": { "type": ["string", "null"] },
    "evaluation": {
      "description": "Component id, or null for declared absence (ADR-0079).",
      "type": ["string", "null"]
    },
    "sandbox_tier": { "type": ["string", "null"] },
    "undeletable": { "type": "boolean", "default": false }
  },
  "$defs": {
    "SpiName": {
      "type": "string",
      "enum": ["planner", "context", "memory", "toolkit", "evaluation"]
    },
    "ComponentInstance": {
      "type": "object",
      "additionalProperties": false,
      "required": ["spi", "ref"],
      "properties": {
        "spi": { "$ref": "#/$defs/SpiName" },
        "ref": { "type": "string", "minLength": 1 },
        "config": { "type": "object" },
        "ceiling": { "type": ["object", "null"] }
      }
    },
    "Binding": {
      "type": "object",
      "additionalProperties": false,
      "required": ["from", "to", "kind"],
      "properties": {
        "from": { "type": "string", "minLength": 1 },
        "to": { "type": "string", "minLength": 1 },
        "kind": {
          "type": "string",
          "enum": ["context", "observe", "evaluate", "spawn_grant", "route"]
        }
      }
    }
  }
}
```

**Compile rule.** Every `bindings[].from`/`to` MUST be a key of `components` or a reserved id `self.episode`. Duplicate edges are errors. Cycles in `evaluate` edges are errors. Cycles in `observe` may exist (debate) but MUST be bounded by `budget.turns`.

**`mhf.harness/1` frontend.** Map slots → instances; synthesise bindings `context→planner`, `memory→planner`, `planner→toolkit[i]`, `evaluation→self.episode`.

### 6.2 Plugin lifecycle FSM (target after ADR-0081)

| From | To | Event kind | Writer role | Notes |
|---|---|---|---|---|
| (start) | DISCOVERED | `PluginDiscovered` | `registry` | **NEW** — today silent |
| DISCOVERED | RESOLVED | `PluginResolved` | `registry` | exists |
| DISCOVERED | FAULTED | `PluginFaulted` | `registry` | exists |
| RESOLVED | VERIFIED | `PluginVerified` | `registry` | **NEW** — today silent |
| RESOLVED | FAULTED | `PluginFaulted` | `registry` | |
| VERIFIED | ACTIVATED | `PluginActivated` | `registry` | exists |
| VERIFIED | FAULTED | `PluginFaulted` | `registry` | |
| ACTIVATED | QUIESCING | `PluginQuiesced` | `registry` | exists |
| ACTIVATED | FAULTED | `PluginFaulted` | `registry` | |
| QUIESCING | RETIRED | `PluginRetired` | `registry` | exists |
| QUIESCING | FAULTED | `PluginFaulted` | `registry` | |
| FAULTED | RETIRED | `PluginRetired` | `registry` | |
| RETIRED | — | — | — | terminal |

Illegal transitions raise; they MUST NOT emit a success kind (`RF-33`).

### 6.3 1-to-1 executable falsifier matrix

| ID | Requirement | Test function (to exist) | Wave |
|---|---|---|---|
| RF-12 | Trajectory required keys (historical F-12) | `test/falsifiers/test_falsifiers.py::TestF12Trajectory.test_episode_completed_emits_schema_valid_mhf_trajectory_1` | M-1 done / strengthen M-2 |
| RF-12b | Cost or reason | `test/runtime/test_trajectory_content.py::test_live_or_cassette_turn_has_cost_or_reason` | M-2 |
| RF-12c | Silent zero fails | `test/runtime/test_trajectory_content.py::test_silent_zero_cost_fails` | M-2 |
| RF-22 | Graph compose + \(D_H\) edge sensitivity | `test/runtime/test_manifest_v2.py::test_two_planner_instances_plus_aggregator_compose` | M-3 |
| RF-23 | v1 frontend | `test/packs/code_default/test_harness_v1_frontend.py` | M-3 |
| RF-24 | evaluation none | `test/runtime/test_absent_evaluation.py::test_compose_accepts_evaluation_none_and_marks_unattributable` | M-3 |
| RF-25 | forgery still illegal | `test/trust/test_forged_verdict_still_illegal.py` | M-3 |
| RF-26 | spawn grant | `test/kernel/test_spawn_verb.py::test_planner_without_spawn_grant_is_denied` | M-6 |
| RF-27 | action ∈ child scope | `test/kernel/test_spawn_verb.py::test_child_action_outside_child_scope_denied_by_kernel` | M-6 |
| RF-28 | no spawn kernel diff pre-M-4 | process / Director `git diff` | M-4 |
| RF-29 | seven ledgered plugin transitions | `test/runtime/test_plugin_lifecycle.py::test_echo_plugin_seven_kinds` | M-3 |
| RF-30 | layer0 gone | `tools/check_stale_paths.py` + `test/tools/test_no_layer0_packaging.py` | M-3 |
| RF-31 | NOVA-2 | `test/runtime/test_nova2_suspend_resume.py` | M-2 |
| RF-32 | UTL-F | standing ADR-0082 | M-3+ |
| RF-33 | illegal FSM | `test/runtime/test_plugin_lifecycle.py::test_illegal_transition_emits_nothing` | M-3 |
| RF-34 | NOVA-4 freeze-at-compose | `test/runtime/test_nova4_negatives.py::test_mid_run_manifest_swap_denied` | M-3 |
| RF-35 | NOVA-4 in_process wire | `::test_in_process_speaks_jsonrpc` | M-3 |
| RF-36 | NOVA-4 writer | `::test_orchestrator_cannot_append_plugin_verified` | M-3 |
| RF-37 | I-7 absorbed registry | `tools/check_domain_blindness.py` | M-3 |
| RF-38 | Pack #2 zero kernel diff | CI `git diff --exit-code vanguard/packages/kernel vanguard/packages/domain` on pack PR | M-5 |
| RF-39 | McNemar harness | `test/lab/test_mcnemar_promotion.py` (lab, not kernel) | M-10 |
| RF-40 | nine-row E2E | `test/integration/test_m4_nine_rows.py` | M-4 |

Historical `002` F-01…F-21 remain. New work uses **RF-*** to end the annex collision (§7.3).

### 6.4 Negative constraints and anti-patterns

| # | Constraint | Violation looks like |
|---|---|---|
| N-1 | TCB ≤ 1438; v0.6.1/0.6.2 kernel delta 0 | "tiny helper" in `kernel/` for spawn or YAML |
| N-2 | I-7 domain blindness | `pytest`/`ast`/`git` tokens in `kernel/` |
| N-3 | Single writer | second `emit` path; orchestrator appends `VerdictRecorded` |
| N-4 | Adapters ↛ kernel/agency | `adapters/` importing `EpisodeEngine` |
| N-5 | No third tree | `core/`, `aether-rust/` as destination |
| N-6 | No loop plugin | SPI `kind: loop` |
| N-7 | No forged cost | zeros without `cost_absent_reason` |
| N-8 | No authored attributability | `promotable: true` in YAML |
| N-9 | No CRDT/NATS core | `research_Harness_Builder_Framework.md` as architecture |
| N-10 | No metaphysics in `docs/` | ADR-M0-10 vs `vanguard_body_detailed.md` |
| N-11 | No microVM mandate pre-M-9 | rewriting sandbox to Firecracker to "match 2026 blogs" |
| N-12 | No DPO in kernel | learner in `dispatch.py` |
| N-13 | `in_process` still JSON-RPC | Python object smuggling across the waist |
| N-14 | No sixth SPI without review | `spi: orchestrator` |
| N-15 | I-11 until M-7 ADR | "just asyncio the session" |
| N-16 | Child workspace destroyed | spawn leak (engine already claims N-16) |
| N-17 | JCS only | new `json.dumps(sort_keys=True)` signing path |
| N-18 | Do not implement from this file | this report is not a ticket source until ADRs land |

---

## §7 · Repository Hygiene & Document Update Cascade

### 7.1 Ghost corpus (G0) — do this as hygiene, not as Wave-3

**`[ABSENT]` paths cited by `SYSTEM_OVERVIEW.md` §4 that are not in this tree:**

- `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/004_V061_ALIGNMENT_ROADMAP.md`
- `…/005_V061_SUBSTRATE_GENERALITY_REVIEW.md`
- `…/006_V061_aether-substrate-briefing.md`
- `docs/06_references/RESEARCH_k3_harness-suggestion.md`
- `RESEARCH_THEORETICAL_SYNTHESIS.md` / `_B.md`
- `RESEARCH_harness_agentic_coding_builder_research_and_framework.md` / `_B.md`
- `proposal_glm_harness_BETA.md`, `proposal_hy3_harness.md`, `proposal_hy3_improved.md`
- `openrouter_llm_models_suggested.md`

**On disk instead:** `WAVE_6_SOTA_RESEARCH_AND_THEORETICAL_SYNTHESIS.md` (+ `_B.md` duplicate), `deepseek-harness_algorithms-ideas.md`, `research_Harness_Builder_Framework.md`, `vanguard_body_detailed.md`, `guidelines.md`.

**Directive.** Either restore the cited files from git history **or** rewrite §4 of the overview to the six real files. Leaving ghost links is false evidence. `tools/check_markdown_links.py` SHOULD fail these; if it does not, that is a linter gap (fix in M-2 hygiene, not a concept change).

**`DELETE.md`:** not present **`[VERIFIED]`**. Do not create a graveyard file. Deleted paths belong in git history + `docs/07_reviews/ARCHIVE.md`.

**Duplicate WAVE_6 `_B`:** consolidate at M-5 doc collapse; until then, cite the non-`_B` file as primary.

**Reject as architecture:** `research_Harness_Builder_Framework.md` (second core).

**Retire or quarantine:** `vanguard_body_detailed.md` (ADR-M0-10).

### 7.2 Stale law citations

- **ADR-0070** still cites `layer0/scheduler/driver.py` spawn stub. File was deleted at 2.2-B. **Do not silently edit ADR-0070.** At M-5, a narrowing ADR may note the path is historical.
- **`002` register** still says Wave 0 not started and production coding not started. Board says M-0/M-1 complete. **After M-4**, replace §0/§6 hold language with a historical banner. Do not rewrite `002` mid-wave except a one-line status box if the Director insists.
- **`pyproject.toml`** `include layer0*` — remove at M-3 with ADR-0081.

### 7.3 Falsifier namespace

| Namespace | Meaning | Examples |
|---|---|---|
| `KERNEL.md` `F-*` | Kernel control ids (S7 budget deny is `F-12`) | annex table |
| `002` `F-01…F-21` | Bound falsifiers | trajectory schema was also `F-12` |
| This mandate `RF-*` | New register ids | RF-12b, RF-22… |

**Ruling.** New documents use `RF-*` for register tests. Annex `F-*` unchanged. Never mint `F-22` in KERNEL.md for a trajectory assertion.

### 7.4 Section-by-section diff directives (execute **after** ADRs are filed, not from this report)

#### `docs/SPEC.md`

| Section | Directive |
|---|---|
| Header / authority | Add ADR-0077…0082 to the living ADR range once filed |
| §1 architecture | After M-3: one paragraph on Named Component Graph; after M-7: Stigmergic Coordination Property |
| Composition / `harness.yaml` | After M-3: `mhf.manifest/2` is law; v1 is frontend |
| §7 trajectories / DPO | After M-2: cost/fingerprint MUST; DPO consumer still deferred until M-10 but **pairing keys** are now populated |
| Evaluator | After M-3: absent-vs-forged; unsigned still illegal |
| Spawn | After M-6: kernel verb; until then keep ADR-0070 semantics + engine implementation note |
| §9 refusals | Unchanged; add "loop as plugin", "authored promotable flag", "second provenance product" |
| UTL-1 | After M-3 only |

#### `docs/03_sprints/sprint_active.md`

| Section | Directive |
|---|---|
| Now / Wave 2 | Add NOVA-1, NOVA-2 as **M-2 exit**, not Wave-4 carry |
| Escalation list | `PluginDiscovered`/`PluginVerified` listed; satisfied by ADR-0081 when filed |
| Wave 3 | Expand 3.3 graph, 3.4 absent-vs-forged, 3.5 spawn **design**; 3.1 deletion after NOVA-4 |
| Do not | Keep "no kernel spawn before M-4" |

#### `docs/02_roadmap/milestones.md`

| Row | Directive |
|---|---|
| M-2 exit | Add NOVA-1 contentful trajectory; NOVA-2 |
| M-3 exit | Graph + layer0 deleted + seven plugin kinds |
| M-4 | Nine rows; row 8 cites NOVA-1 not mere schema |
| M-5 | Pack #2 = math/deductive; **not** TableWorld |
| Versions | Footnote the §4.1 ladder |

#### Wave plans (`docs/03_sprints/plans/`)

| Plan | Directive |
|---|---|
| `wave2_convergence.md` | NOVA-1 assembler + usage plumbing; NOVA-2 test; no graph code |
| `wave3_extensibility.md` | Schema v2, frontend, FSM kinds, NOVA-4, delete layer0 |
| `wave4_foundation_e2e.md` | `RF-40` nine-row; escalate scope creep |

Do **not** edit annex KERNEL.md F-tables to "fix" the F-12 collision. Namespace split is cheaper.

### 7.5 What developers do on Monday (after Director files ADRs)

1. NOVA-1 in `trajectory.py` + model usage fields + `RF-12b/c`.
2. NOVA-2 test against WAL + `recovery.py`.
3. Stop citing ghost reviews in new prose.
4. Do not start `mhf.manifest/2` code until M-2 exit including NOVA-2.

---

## Appendix A · Forensic Verification Log (this pass)

| Claim | Result |
|---|---|
| Git short HEAD | `e84dfda` |
| Package version | `0.4.5b1` in `pyproject.toml` |
| Trajectory zeros | `runtime/trajectory.py` `_ZERO_COST` at 10, 53, 75 |
| F-12 test strength | required keys + abort `verdict is None` only |
| Manifest dialects | YAML slots vs JSON named path bag vs domain `components` tuple |
| Path bag ≠ graph | `parse_manifest` sorts role→paths; no edges |
| Plugin FSM holes | `lifecycle.py` `_EVENT` 5 of 7 states; no Discovered/Verified kinds |
| Writer table | plugin kinds registry-owned; no Discovered/Verified |
| Spawn | `EpisodeEngine.spawn`; `ProposalKind.SPAWN`; kernel gap documented in docstring |
| layer0 remainder | compose + registry + events; no packages `from layer0` |
| WAL | `PRAGMA journal_mode = WAL`; `synchronous` default FULL |
| S0–S12 | `kernel/dispatch.py` module docstring |
| Principal reviews on disk | 001, 002, 003 only |
| `docs/06_references` | 6 files; WAVE_6 pair + deepseek + harness-builder + body + guidelines |
| DELETE.md | absent |
| TableWorld | adapter + `vg-table-default` already in tree |
| Skill index | prefix budget, no Elo/embeddings |
| EventKind spawn | `CHILD_SPAWNED`, `CHILD_RETURNED` already exist |

---

## Appendix B · Findings Unique to This Pass

1. **Ghost briefing (G0).** The overview's review/research index is not a function of this tree. Treat as the documentation analogue of I-9 failure.
2. **Named bag overclaimed as graph.** Converging parsers onto `components: {role: [paths]}` does **not** buy debate/tree-search. Bindings are the actual product of T-1.
3. **F-12 is a false green on I-9.** Strengthening the existing test is cheaper than a parallel mythic "NOVA-1 programme" if anyone tries to defer the assembler change.
4. **M-3 exit is unsatisfiable** without two new event kinds (Director-gated). Wave 3 is not "just absorb files."
5. **Pack #2 ≠ TableWorld.** Using the orphaned adapter would fake the I-7 proof.
6. **Engine already admits the spawn hole.** M-6 `RF-27` is not speculative; it is the kernel-side close of a documented bypass.
7. **`pyproject.toml` still packages `layer0*`.** Deletion is incomplete if setuptools still ships the fork.

These seven are the Alfa delta relative to a review that only restates `SYSTEM_OVERVIEW.md` §5.

---

## Appendix C · External Sources

Consulted 2026-08-21 (non-exhaustive; titles as retrieved):

- Shrivu Shankar, *Building Multi-Agent Systems (Part 3)*, Jan 2026 — domain-agnostic harness + sandbox.
- *Harness Engineering: The Meta Layer as a First-Class Discipline for Multi-Agent Systems*, Zenodo 10.5281/zenodo.20472667.
- Cobus Greyling, *Two-Thirds of Multi-Agent Intelligence Is Harness*, Apr 2026.
- State-centric / stigmergic LLM-MAS (shared traces, no direct calls), 2026.
- Many Tems / stigmergic SQLite coordination (research notes).
- *A Framework for Inherently Safer AGI through Language-Mediated Active Inference*, arXiv:2508.05766.
- *Active Inference for Self-Organizing Multi-LLM Systems*, arXiv:2412.10425.
- ASTRA: *Automated Synthesis of agentic Trajectories and Reinforcement Arenas*, arXiv:2601.21558.
- DMPO: *Direct Multi-Turn Preference Optimization for Language Agents*, EMNLP 2024, arXiv:2406.14868.
- TRACE: *Turn-level Reward Assignment via Credit Estimation*, arXiv:2607.13988, Jul 2026.
- Causal Agent Replay (CAR), arXiv:2606.08275.
- NVIDIA, *Practical Security Guidance for Sandboxing Agentic Workflows*; Augment / Northflank 2026 sandbox surveys (microVM vs shared kernel).
- `agent-provenance-dag` (signed causal envelopes) — imported as **literature**, not as a dependency.

Internal law: SPEC, ADRs 0069–0076, KERNEL.md, 002, 003, SYSTEM_OVERVIEW, sprint_active, milestones, on-disk packages as listed in Appendix A.

---

## Signature block (advisory)

| Role | Vote |
|---|---|
| Engineering Director | **R-1…R-6**; M-4 inviolable; v0.6.3 product cut |
| CTO | **R-1 is strategy**; stigmergy named at M-7; no SDK-wrap |
| CIO | **R-3**; derived unattributability |
| Principal Staff Engineer | **G0→G1→G2→G9**; F-12 false green |
| Principal Systems Architect | **bindings required**; TCB 0 until M-6 |
| Tech Lead | **NOVA-2 gates M-3**; RF matrix |
| PhD AI Specialist | **§5 is M-10 consumer**; symbols from M-2 |

*This document is the Alfa (Grok) Leadership 7 proposal. It does not amend SPEC or any ADR.*
