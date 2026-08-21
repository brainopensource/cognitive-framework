# 007 — ZETA REVIEW: The General Task-Solving Swarm Meta-Framework

**Definitive Executive Review, Architectural Adjudication, and Phased Technical Proposal**

| Field | Value |
|---|---|
| **Document ID** | `007_zeta_review_full_opus_proposal.md` |
| **Prepared by** | The Leadership 7 — Engineering Director · CTO · CIO · Principal Staff Engineer · Principal Systems Architect · Tech Lead · PhD AI Specialist |
| **Prepared for** | The Director of Record, AETHER / Vanguard |
| **Date** | 2026-08-21 |
| **Baseline** | `main` @ `733855b` — every `[VERIFIED]` claim below was re-executed against the working tree during this pass |
| **Scope** | Version ladder **v0.6.1 → v0.6.2 → v0.6.3 → v0.7.0 → v0.8.0 → v0.9.0 → v1.0.0**, milestones **M-0 … M-10** |
| **Predecessors consumed** | `002` gap register · `003` Director review · `004` alignment roadmap · `005` substrate generality review · `006` substrate briefing · `SYSTEM_OVERVIEW.md` · `RESEARCH_k3` · `RESEARCH_THEORETICAL_SYNTHESIS` · `proposal_glm_harness_BETA` · `proposal_hy3_improved` |
| **Authority** | **Advisory until ratified.** This document amends nothing by itself. Law remains `docs/SPEC.md` → `docs/05_adr/` → `docs/04_annex/`. §3 below contains the *drafted text* of ADRs `0077`–`0082`; they become binding only when committed as files under `docs/05_adr/` with a Director signature. |
| **Output constraint honoured** | No specification file, ADR, or source file was edited in producing this report. |

---

## Table of Contents

- [§0 · Ten-Minute Executive Briefing](#0--ten-minute-executive-briefing)
- [§1 · Executive Rulings & the Strategic Paradigm Shift](#1--executive-rulings--the-strategic-paradigm-shift)
- [§2 · Adjudication of Open Architectural Tensions T-1 … T-9](#2--adjudication-of-open-architectural-tensions-t-1--t-9)
- [§3 · Drafted Append-Only ADR Catalog — `ADR-0077` … `ADR-0082`](#3--drafted-append-only-adr-catalog--adr-0077--adr-0082)
- [§4 · Phased Milestone Roadmap & Version Ladder (v0.6.1 → v1.0.0)](#4--phased-milestone-roadmap--version-ladder-v061--v100)
- [§5 · Theories, Algorithms & Mathematical Formalisation](#5--theories-algorithms--mathematical-formalisation)
- [§6 · Zero-Guesswork Developer Implementation Bridge](#6--zero-guesswork-developer-implementation-bridge)
- [§7 · Repository Hygiene & Document Update Cascade](#7--repository-hygiene--document-update-cascade)
- [Appendix A · Forensic Verification Log (this pass)](#appendix-a--forensic-verification-log-this-pass)
- [Appendix B · New Findings Not Present in Any Prior Review](#appendix-b--new-findings-not-present-in-any-prior-review)
- [Appendix C · External Sources](#appendix-c--external-sources)

---

## §0 · Ten-Minute Executive Briefing

### 0.1 The one-paragraph verdict

AETHER's four load-bearing pillars are **A — Authority** (the S0–S12 reference monitor, 1365/1438 logical LOC, verified green), **B — Bundle** (the composition surface), **C — Corpus** (the event ledger and the trajectory record), and **D — Digest** (the `D_H`/`D_R`/`D_X` identity trinity). **A and D are already generic and correct. B is template-shaped and C is hollow.** Every remaining decision in this document is the order in which B and C are made generic *without weakening A or collapsing D*. That ordering has a hard deadline: `D_H` is computed over the manifest shape, so B's shape change is nearly free before M-4 and permanently expensive afterwards, and C's content defect writes one irrecoverably degraded row into the training corpus for every episode that completes before it is fixed. The Leadership 7 therefore rules: **NOVA-1 (corpus content) executes immediately inside M-2; the component graph (`mhf.manifest/2`) is authorised now and lands at M-3; `agent.spawn` is design-locked now and implemented at M-6; the M-4 nine-row stop line is non-negotiable.**

### 0.2 The paradigm shift, stated once

> **AETHER stops being "a coding harness with a security kernel attached" the moment the composition surface can name more than one cognitive component — and it becomes a *swarm meta-framework* the moment delegation itself becomes a mediated effect.**

Those are two schema/dispatch changes, not two engines. Everything else the swarm ambition requires — debate, critic loops, MCTS, evolutionary search, hierarchical decomposition, economic delegation — is already expressible as **spawn topology + planner policy over the one universal turn loop**. The moat is that the loop's authority boundary never moves while the topology varies infinitely.

### 0.3 The six rulings, on one line each

| # | Ruling | Vehicle | Lands |
|---|---|---|---|
| **R-1** | Un-hollow the corpus **now**. Per-turn cost, model fingerprint, latency, verdict-or-explicit-null. | `ADR-0078` | **v0.6.1 / M-2** |
| **R-2** | `harness.yaml` becomes a **named component graph** (`mhf.manifest/2`). Slots degrade to pack convention. | `ADR-0077` | **v0.6.2 / M-3** |
| **R-3** | Guardrails become **declarable but never forgeable** — the absent-vs-forged rule. | `ADR-0079` | **v0.6.2 / M-3** |
| **R-4** | `agent.spawn` is **design-locked now**, kernel untouched until M-4 closes, implemented at M-6. | `ADR-0080` | design **v0.6.1**, code **v0.8.0 / M-6** |
| **R-5** | `layer0/` is absorbed into `runtime/registry/` + `runtime/compose.py` and **deleted**, behind the NOVA-4 negative suite. | `ADR-0081` | **v0.6.2 / M-3** |
| **R-6** | The **loop-as-mechanism** claim is published with a bound falsifier; **NOVA-2** cold suspend/resume is I-11's precondition. | `ADR-0082` | **v0.6.1 / M-2** |

### 0.4 The three findings this pass adds that no prior review contains

1. **`[VERIFIED]` The plugin lifecycle cannot satisfy its own M-3 exit gate.** `layer0/registry/lifecycle.py:33-39` maps only five of seven states to event kinds. `DISCOVERED` and **`VERIFIED` emit nothing** — `_EVENT.get(target)` returns `None` and the transition passes silently. The M-3 gate reads *"every transition ledgered"*; with the closed 56-kind catalog as it stands, that gate is **unsatisfiable by construction**. Closing it requires two new event kinds (`PluginDiscovered`, `PluginVerified`), which is a **Director-only escalation** under `sprint_active.md`'s escalation list. See `ADR-0081` §D3.
2. **`[VERIFIED]` The composition graph already exists — in the wrong dialect.** `domain/artifacts/manifest.py:64` types `HarnessManifest.components` as `tuple[tuple[str, tuple[str, ...]], ...]` — a **named component map** — and `agency/manifests/vg-code-default/manifest.json` populates it with seven named components. Meanwhile `schemas/mhf/harness_manifest.schema.json` freezes the *five fixed slots*. There are **two live manifest dialects**, and the more general one is already the one the domain layer parses. T-1 is therefore not "build a component graph"; it is **"converge two parsers onto the general dialect that is already written"** — materially cheaper than `005` §W1 assumed. See `ADR-0077` §C2.
3. **`[VERIFIED]` The falsifier identifier namespace collides.** `F-01 … F-25` exist with **different meanings** in `docs/04_annex/KERNEL.md` (kernel controls) and in the `002` register (bound falsifiers). `ADR-M0-02` declares exactly three namespaces (`I-*`, `ADR-*`, `S-M*`) and **does not list `F-*` at all**. The kernel spelling is embedded in ~19 source and test files; the register spelling is embedded in docs and `test/falsifiers/`. See §7.3 for the ruling (`RF-*` for the register, `F-*` stays with the annex).

---

## §1 · Executive Rulings & the Strategic Paradigm Shift

### 1.1 The Leadership 7 — consensus, and where it was not unanimous

Each officer states a position and a dissent where one exists. Consensus that hides a dissent is not consensus.

| Officer | Position | Dissent / condition recorded |
|---|---|---|
| **Engineering Director** (authority, governance, stop lines) | Ratify R-1…R-6. The **M-4 nine-row stop line is absolute**; any proposal to widen its scope in order to make the run pass is escalated, not absorbed. Version cut from `0.4.5b1` happens **at M-4**, not before. | *Condition:* `ADR-0080` must state in its own text that a kernel diff before M-4 closes voids the M-4 evidence bundle. Sequencing is the whole objection to `agent.spawn`; nothing else. |
| **CTO** (moat, SOTA, macro strategy) | The moat is **not** the sandbox and **not** the kernel LOC count — both are replicable. The moat is *separability*: an un-gameable training signal **by construction**. 2026 SOTA (Meta-Harness, AHE, Harness-Bench) has converged on harness-as-independent-variable and is now automating harness search; whoever automates it **on a forgeable corpus is optimising noise**. R-1 is therefore the strategy, not the hygiene. | *Dissent:* argued for pulling the external benchmark run (G8) forward to M-4. **Overruled** by the Director — measuring the pack before the pack loads through its own lifecycle measures the wrong artifact. Rescheduled to M-5. |
| **CIO** (auditability, traceability, security) | R-3's *absent-vs-forged* rule is the only formulation that survives audit: **turning a guardrail off is a recorded composition property; forging evidence is categorically illegal under every composition.** Ratifies the seven permanent non-negotiables (§2.3.3) as the fixed substrate boundary. | *Condition:* `unattributable_for_promotion` must be a **derived, non-writable** field computed by `compose()` from `D_H`, never a manifest-authored boolean. A self-declared attributability flag is a forgery surface. |
| **Principal Staff Engineer** (gap register, generality) | The gap register is correct and the priority order stands: **G1 (hollow corpus) → G2 (fixed slots) → G5 (`K ≪ N`) → G7 (Wave-3 falsifiers) → G4 (guardrails) → G3 (`spawn`)**. Adds **G9**: the plugin FSM cannot ledger `VERIFIED` (Appendix B, Finding 1). | *Note:* declares `F-08` permanently **stale** (settled at Wave-1 exit) and requires that the register say so in its own table rather than in a sprint-board footnote. |
| **Principal Systems Architect** (boundary lattice, TCB invariants) | The lattice `domain ← ports ← kernel ← agency ← runtime → adapters` holds and must not be relaxed for the component graph. `mhf.manifest/2` is parsed in **`domain/`**, resolved in **`runtime/`**, and never seen by **`kernel/`**. TCB delta for `v0.6.1`+`v0.6.2` is **exactly zero**; the first legal TCB growth is `ADR-0080`'s `agent.spawn` at M-6, budgeted at **≤ 40 logical LOC** against the 1438 ceiling (1365 today ⇒ 73 LOC of headroom, so the verb must land with headroom left over). | *Dissent:* considers the LOC ceiling a Goodharted metric (`KERNEL.md` §1.1, AP-8) and wants the mutation-score replacement built. **Deferred** to M-5 (§4, M-5 scope) rather than refused. |
| **Tech Lead** (sprint execution, zero-guesswork bridge) | Every ruling ships with (a) a Draft 2020-12 schema, (b) an FSM row with its ledger event, (c) a named executable falsifier `RF-nn` mapped 1-to-1 to a concrete test function, and (d) a negative-constraints checklist. Nothing enters a sprint board as prose. | *Condition:* refuses to open M-3 until **NOVA-2** is green, because a red NOVA-2 changes M-7 from a refactor to a rewrite and therefore changes what M-3's abstractions must support. |
| **PhD AI Specialist** (cognitive systems, active inference, RL) | The corpus is the substrate for **all** of Layer 3. A trajectory without `(cost, latency, model_fingerprint, signed_verdict)` per turn admits **no** credit assignment, **no** calibrated `P(pass ∣ a, c)`, **no** DPO pairing, and **no** McNemar-gated promotion. Formalises the six-dimensional economic tensor **R** and the VFE objective in §5. | *Dissent:* wanted `attribution.prefix_hits` promoted to a required field at M-2. **Compromise:** required at **M-10** (`ADR-0078` §D4), optional-but-emitted from M-2, because a required field the pack cannot yet compute produces a false green. |

**Unanimous, recorded as the standing mandate of this body:**

> The substrate ships **B** (a real composition algebra) and **C** (a learnable corpus) before it ships any consumer of either. Optimisation machinery built on a forgeable or hollow corpus is not merely useless — it is actively misleading, because it produces confident numbers about nothing.

### 1.2 SOTA 2026 alignment — what the literature forces us to concede, and what it does not

The mandated external research pass was executed. Four findings bear directly on the ladder.

#### 1.2.1 Harness engineering is now the measured independent variable — and it is being automated

The 2026 literature has converged on the thesis this project locked a year early. `Agent Harness Engineering: A Survey` and `Harness-Bench: Measuring Harness Effects across Models in Realistic Agent Workflows` both treat the harness as the controlled variable rather than the model. The empirical swing is large: a GPT-5.2-Codex agent was lifted **52.8% → 66.5%** on Terminal-Bench 2.0 purely by restructuring the system prompt, injecting context through middleware, and adding self-verification hooks; ten iterations of *Observability-Driven Automatic Evolution of Coding-Agent Harnesses* lifted pass@1 on Terminal-Bench 2 from **69.7% → 77.0%**, surpassing the human-designed Codex-CLI harness at 71.9%.

**What this forces us to concede.** Automated harness search is no longer speculative; it is a published, reproducible result. M-10 is therefore not a research fantasy — it is a **race**, and the competitive question is *whose search signal is trustworthy*.

**What it does not force.** Every published automatic-harness-evolution loop optimises against **self-reported or benchmark-scored** outcomes. None of them has an exterior, unreachable, cryptographically-bound judge. That is precisely the separability thesis, and it is why `ADR-0078` (rich corpus) plus `ADR-0079` (declared-absence never forges) plus the existing UID-10002 daemon is the *differentiated* position: **AETHER's harness-search signal is un-gameable by construction; theirs is un-gameable by hope.**

> **CTO ruling:** `D_H` is already the harness-search parameter vector. Because `D_H` covers prompt, ceiling, approval policy, and model routes, an AETHER harness search operates over a *content-addressed genome* whose every evaluation is exterior-signed. Publish this claim in `SPEC.md` §7 at M-10, not before — a claim without its corpus is marketing.

#### 1.2.2 Stigmergic swarms via the State Plane defeat `O(N²)` chatter

The 2026 multi-agent literature has independently rediscovered AETHER's State Plane. `CodeCRDT: Observation-Driven Coordination for Multi-Agent LLM Code Generation` demonstrates coordination by *monitoring shared state* — observing edits, skipping completed work, avoiding conflicts — **without centralized task assignment or message passing**. `Beyond Text-Passing: Shared Cognitive Substrates for Multi-Agent LLM Coordination` names the failure mode explicitly: natural-language message-passing as the sole inter-agent medium is a **structural** limitation on consistency, efficiency and auditability. The cost is quantified: the prevailing synchronisation pattern is **full-state rebroadcast** — on any artifact modification the orchestrator injects the complete updated artifact into the next prompt of every agent that might need it — which is the source of the `O(N²)` communication overhead. `PatchBoard` and `Token Coherence` (MESI-style cache protocols for agent state) attack the same problem from the schema and coherence directions.

**The AETHER translation, stated formally.** Let `N` be logical agents and `T` turns.

```text
Message-passing swarm:   messages(N, T) ∈ Θ(N² · T)      context bytes ∈ Θ(N² · T · |artifact|)
Stigmergic swarm:        appends(N, T)  ∈ Θ(N · T)        reads via fold/projection ∈ Θ(N · T · |Δ|)
```

Because `State = fold(events)` over one WAL stream per `project_id`, and because causal relations (`spawned_by`, `caused_by`, `produced`, `evaluated_by`) are **projections of events, never a maintained graph** (`ADR-0003`, `ADR-0070`), an AETHER swarm coordinates by *reading a projection of the ledger*, not by broadcasting to peers. **The `O(N²)` term does not exist in this architecture.** Sibling agents never address each other; they address the ledger, and the ledger is single-writer, hash-chained, and replayable.

> **Principal Systems Architect ruling:** this is the strongest un-priced asset in the tree. It must be **named** in `SPEC.md` §1.4 at M-7 as the *Stigmergic Coordination Property*, with the complexity claim above stated as a falsifiable measurement (§4, M-9 gate: measured messages-per-turn must remain `Θ(N)` as `N` scales, or the property is refuted).
>
> **What we refuse to import:** CRDTs, eventual consistency, and MESI-style coherence protocols. `project_id` is the consistency unit with a *total order*; a CRDT would trade the total order for concurrency we have not yet earned the right to enable (I-11). Revisit only if the M-7 measurement gate demands it.

#### 1.2.3 Provenance and capability attenuation are converging on our primitives

`From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents` (2026) describes provenance-aware guardrails that check *whether the tool is authorized, whether user intent is present, whether arguments are well-formed, whether sensitive fields come from trusted sources* — which is, line for line, the S4 classifier plus the S5 authority predicate plus `provenance.authority_violation()` over justifying spans. `Lingering Authority: Revocable Resource-and-Effect Capabilities for Coding Agents` (2026) is the closest external work to `kernel/attenuation.py` and names the exact defect our `CapabilityRevoked` kind exists to close. `The Balkanization of Execution-Security Research for AI Coding Agents` catalogues **TOCTOU** as the field's dominant unsolved class.

> **CIO ruling — and one genuine gap.** AETHER's `K-05` (re-verify at the point of effect) and `K-47`/S8a (durable intent fsynced *before* dispatch) are a stronger TOCTOU answer than anything in that survey, and `dispatch.py` implements both `[VERIFIED]`. **But** the same survey's threat model covers *revocation during a live lease*, and AETHER has `CapabilityRevoked` in the catalog with **no production emitter and no reducer fold path exercised by any falsifier**. This is not an M-2 blocker. It is registered as **`RF-38`** (§6.3) and scheduled at **M-7**, where concurrency makes mid-lease revocation reachable for the first time.

#### 1.2.4 Active inference and trajectory-graph RL are tractable — and they need exactly the corpus we do not yet emit

`Expected Free Energy-based Planning as Variational Inference` (2026) shows EFE minimisation becomes tractable when recast as variational free energy minimisation with epistemic priors, with factor-graph message passing scaling **linearly in the number of factors**. `ASTRA: Automated Synthesis of agentic Trajectories and Reinforcement Arenas` (2026) synthesises multi-turn tool-use trajectories from the *static topology of tool-call graphs* and trains against rule-verifiable environments with deterministic rewards. `Beyond Trajectory-Level Attribution: Graph-Based Credit Assignment for Agentic Reinforcement Learning` (2026) aggregates rollouts into a unified state-transition graph and assigns credit per **edge** rather than per trajectory.

> **PhD AI Specialist ruling.** Three concessions and one refusal.
>
> - **Concede:** edge-level (per-turn) credit assignment beats trajectory-level. Our `mhf.trajectory/1` `turns[]` array is already the right shape — it is simply **empty of the signal that makes an edge measurable**. `ADR-0078` fixes exactly that.
> - **Concede:** ASTRA's insight that *tool-call graph topology is the trajectory generator* maps onto our component graph: once `mhf.manifest/2` exists, the graph is both the composition **and** the synthesis topology. This is a genuine dual-use of `ADR-0077` that no prior review noticed.
> - **Concede:** EFE-as-VFE-with-epistemic-priors is the tractable formulation. §5.2 adopts it and drops the intractable trajectory-integral form.
> - **Refuse:** ASTRA's *automated environment synthesis* as a substrate feature. Preregistered oracles exist precisely so the judged cannot author its own arena. Synthesised environments enter — if ever — as **pack data behind a preregistration event**, never as a core capability. This refusal joins `SPEC.md` §9 at M-10.

### 1.3 The A-B-C-D foundation, re-scored against disk **[VERIFIED this pass]**

| | Pillar | Generic? | Evidence on disk (this pass) | Ruling |
|---|---|---|---|---|
| **A** | **Authority** | ✅ **Yes** | `check_tcb_budget.py` → `TCB PASS: 1365 logical lines across 9 files (alarm above 1438)`. `policy.py` implements attenuate → sealed-membership (`ADR-0067`) → authority predicate → approval, in that order, with `Outcome` having exactly three members and no "allow with a warning". `classifier.py:widens_capability` fails closed on unknown principal, unheld action, depth overrun, and undecidable resource pairs (`K-48`). | **Keep as-is. Zero TCB growth until M-6.** |
| **B** | **Bundle** | ❌ **No — template-shaped, and split across two dialects** | `schemas/mhf/harness_manifest.schema.json#/$defs/PluginBindings` declares exactly `planner · context · memory · toolkits · evaluation · model_routes` with `additionalProperties: false`. `packs/code-default/harness.yaml` instantiates precisely that. **But** `domain/artifacts/manifest.py:64` already types `components` as a named map, and `agency/manifests/vg-code-default/manifest.json` already ships seven named components. | **`ADR-0077`. Converge onto the general dialect.** |
| **C** | **Corpus** | ❌ **No — born hollow** | `runtime/trajectory.py:10` `_ZERO_COST = {"usd_micros": 0, "tokens": 0, "bytes": 0, "millis": 0}`; consumed at **line 53** (per-turn) and **line 75** (episode). No `model_routes_used`, no `execution_digest`, no `attribution` in the emitted object — all three are `schemas/mhf/trajectory.schema.json` *optional* fields, so the record validates while carrying nothing. | **`ADR-0078`. Fix inside M-2.** |
| **D** | **Digest** | ✅ **Yes** | `domain/artifacts/manifest.py:83-95` — `composition_digest` is `digest_of({harness, components, capabilities, evaluators, budgetPolicy, graphDigest, **identity})` with `episode_id` explicitly excluded as instance identity, and `Runtime.compose` supplying prompt/ceiling/approval/routes into `identity`. | **Keep. `D_H` extends over the graph; principle unchanged.** |

**The claim, restated with its dependency:** *sovereign, self-improving multi-agent ecologies are reachable **iff** A, B, C, D are all generic.* A and D are. **The entirety of v0.6.1 and v0.6.2 exists to make B and C generic.** Nothing after v0.7.0 is safe to start before that is true.

### 1.4 The Separability Thesis, sharpened for the swarm era

The thesis as written — *"what solved it must be separable, and the judge must be unreachable from the judged"* — was formulated for a single agent. A swarm requires two amendments, both of which the current architecture already satisfies and neither of which is currently *stated*:

> **S-1 (Singular Court).** A swarm has **one** judge, exterior to **every** participant. Delegation depth, sibling count, and heterogeneous harness composition do not multiply the evidence plane. `ADR-0072` and `SPEC.md` §6.3 (*"one economy, one court"*) already imply this; `ADR-0080` §D5 states it.
>
> **S-2 (Attenuated Reachability).** Unreachability must be **monotonic under delegation**: if a parent cannot reach the judge, no descendant may reach it. This follows from `Capabilities(child) ⊆ Capabilities(parent)` under one selector partial order — but only if the evaluator's UDS socket is expressed as a *resource in the selector algebra*, so that reachability is attenuated rather than ambient. **`[VERIFIED]` it is not today**: the evaluator client (`adapters/evaluators/client.py`) is wired at composition, not selector-gated. Registered as **`RF-39`**, scheduled at **M-6** alongside `agent.spawn`, because M-6 is the first milestone where a planner-authored child exists that the parent did not construct.

---

## §2 · Adjudication of Open Architectural Tensions T-1 … T-9

Each tension is adjudicated with: **the ruling**, **the disposition label** (`lock now` / `strengthen now` / `generalize now` / `design-only-implement-later` / `revisit after M-4` / `reject`), **the authorising ADR**, **the bound falsifier**, and **the milestone**.

### 2.1 T-1 · Manifest shape — fixed slots vs. named component graph

**RULING: `generalize now`. Authorise `mhf.manifest/2`, the Named Component Graph. → `ADR-0077`. Falsifier `RF-23`…`RF-27`. Lands v0.6.2 / M-3 (sprint 3.3), designed in v0.6.1 / M-2.**

#### 2.1.1 The forensic correction that changes the cost estimate

`005` §W1 and `SYSTEM_OVERVIEW` §5.1 both cost this as *"one schema revision + a compose-v2 resolving a map instead of six keys."* That is a fair estimate but it misses a decisive fact verified this pass:

```text
DIALECT 1 — schemas/mhf/harness_manifest.schema.json  (mhf.harness/1)
  plugins: { planner, context, memory, toolkits[], evaluation, model_routes[] }
  additionalProperties: false          ← the five-hole agent shape
  instantiated by: packs/code-default/harness.yaml
  parsed by:       agency/manifests/loader.py  (YAML path)

DIALECT 2 — vanguard/packages/domain/artifacts/manifest.py:64
  components: tuple[tuple[str, tuple[str, ...]], ...]   ← ALREADY A NAMED COMPONENT MAP
  instantiated by: agency/manifests/vg-*/manifest.json  (7 named components in vg-code-default)
  parsed by:       domain/artifacts/manifest.parse_manifest()  (JSON path)
```

The domain layer — the *innermost, purest* layer, which nothing may import — **already models composition as a named map**, and `FrozenHarness.composition_digest` already hashes it as one. The fixed-slot shape lives only in the **schema** and the **YAML loader**. Sprint `3.2-C` ("one manifest parser", currently `DEV-LOCAL`) is therefore not a layout tidy-up: **it is the T-1 decision, and it is already on the board under the wrong readiness label.**

> **Tech Lead ruling:** `3.2-C` is re-labelled **`DIRECTOR`** and merged into sprint 3.3. A `DEV-LOCAL` task must never be the vehicle for a decision that fixes `D_H`'s pre-image.

#### 2.1.2 What the graph must express, and the acceptance test for the schema

The schema is correct **iff** all six reference topologies compile without an engine diff:

| Topology | Component shape it requires | Expressible under `mhf.harness/1`? |
|---|---|---|
| ReAct coding agent (Pack #1) | 1 planner · 1 context · 1 memory · 1 eval · N toolkits | ✅ (it *is* the shape) |
| Critic / revisor loop | **2** planner-kind components with declared roles (`proposer`, `critic`) | ❌ |
| Multi-proposer debate | **N** planner-kind + 1 aggregator + shared evaluation | ❌ |
| Tree search / MCTS | 3 distinct policies: `expansion`, `scoring`, `selection` | ❌ |
| Evolutionary search | population operator + fitness binding to an evaluation component | ❌ |
| Dual-gate research agent | 2 evaluation-kind components (cheap inline + exterior terminal) | ❌ |

**`RF-24` is the falsifier that makes this concrete and non-negotiable:** *six reference manifests, one per row, MUST compile to six distinct `FrozenHarness` digests through `compose()` with zero diffs under `vanguard/packages/kernel/` and `vanguard/packages/agency/episode/engine.py`.* Compiling is the whole test at M-3 — **executing** them is M-8's job. Separating "the surface can name it" from "the runtime can run it" is what keeps this a Wave-3-sized change.

#### 2.1.3 The DeepSeek-Harness comparison, adjudicated

`005` §W1 and `006` §1.7 both flag the same external system: a flat, ordered stack of plugin bundles with *"no privileged core to patch."* The two properties are **orthogonal and must be separated by ruling, not by tone**:

| Property | Verdict |
|---|---|
| **Flat composition surface** (no fixed slots; components named, not positioned) | **IMPORT.** This is `ADR-0077`. |
| **No privileged core** (no authority boundary; any plugin may write any state) | **REFUSE — permanently.** This is the exact architecture whose evidence cannot be trusted, and it is already refused by `ADR-0070` and `SPEC.md` §9. `ADR-0077` §D7 restates the refusal *inside* the ADR that imports the flatness, so the two can never be conflated by a future reader. |

> **CTO:** "Flat at the composition surface, rigid at the authority boundary" is a position **no one currently occupies**. It is the differentiated claim. It is also the only claim that survives the CIO's audit.

#### 2.1.4 Migration and blast radius

| Artifact | Migration | Owner |
|---|---|---|
| `schemas/mhf/harness_manifest.schema.json` | Add `mhf.manifest/2` **alongside** `mhf.harness/1`. `/1` is **frozen, not deleted** — it remains readable through M-4 for corpus attribution. | Dev A |
| `packs/code-default/harness.yaml` | Mechanical rewrite: 6 slot keys → 8 named components. Slot names preserved verbatim **as component names**, so `code-default` reads almost identically. | Dev A |
| `agency/manifests/vg-*/manifest.json` (6 packs) | Already the target dialect. Gain a `kind:` and `ceiling:` per component. | Dev B |
| `domain/artifacts/manifest.py` | Extend `components` element type from `(name, refs)` to `(name, kind, refs, config_digest, ceiling)`. `composition_digest` pre-image changes ⇒ **every `D_H` changes once**, deliberately, before M-4. | Dev B |
| `runtime/compose.py` | Resolve a map with topological ordering; enforce per-component ceiling ∩ harness ceiling, fail-closed. | Dev B |
| `agency/manifests/loader.py` | **Deleted as a second parser.** One YAML/JSON → `HarnessManifest` path. | Dev A |
| Trajectories emitted before the cut | Attributed to `mhf.harness/1` `D_H` values. **Acceptable only because this happens before M-4**, when the corpus is still pre-production. This is the entire reason for the deadline. | — |

---

### 2.2 T-2 · Spawning — engine-owned vs. capability-mediated `agent.spawn`

**RULING: `design-only-implement-later`. Design and falsifier-sketch land in v0.6.1 / M-2. Kernel diff is FORBIDDEN until M-4 closes. Implementation lands v0.8.0 / M-6. → `ADR-0080`. Falsifiers `RF-31`…`RF-35`.**

#### 2.2.1 Why Option B strengthens rather than weakens authority

Today `EpisodeEngine.spawn(...)` at `agency/episode/engine.py:531` is a **privileged engine call**. Delegation therefore bypasses the reference monitor — not because it is unsafe, but because the engine is *trusted by position*. Under `agent.spawn` as an S0–S12 verb, every delegation becomes a mediated effect with a lease, a descriptor-bound grant, a durable intent record, and a receipt. **The security argument runs entirely in favour of Option B.** The only objection is sequencing, and the Director sustains that objection.

#### 2.2.2 A forensic correction to the engine's own docstring `[VERIFIED]`

`engine.py:556-571` documents, at length, that:

> *"`StandardPolicy.authorize` attenuates `requested_scope` against the policy's parent and never checks that `request.action` is a member of `requested_scope.actions` … a child narrowed to one read verb reached a privileged adapter … Closing the same gap inside the kernel is a `kernel/` change and needs its own ADR (`ADR-0054`)."*

**That statement is now stale.** `kernel/policy.py` step **1b** implements sealed membership under `ADR-0067`:

```python
if requested_scope.sealed and request.action not in requested_scope.actions:
    return Decision(Outcome.REJECT, FailurePath.DENIED_SCOPE_ESCALATION, ...)
```

and `kernel/attenuation.py:183` sets `sealed=request.sealed or request.actions < parent.actions` — i.e. **`attenuate()` seals automatically whenever the parent withholds verbs**, which is by definition true of every spawn. The kernel-side gap the docstring reports as open is closed; the engine-side refusal is now defence in depth, not the sole control.

> **Principal Systems Architect ruling:** this is not a code change — it is a **documentation defect inside the TCB's nearest neighbour**, and a reviewer who trusts it will mis-model the kernel. `ADR-0080` §C3 records the correction, and **`RF-40`** pins it: *a sealed child scope MUST reject an out-of-scope action **at S5**, with the engine-side refusal disabled.* If `RF-40` is red, the docstring was right and `ADR-0067` is unimplemented — either way we learn it from a test, not from prose.

#### 2.2.3 The design that is being locked (not built)

```text
verb:      agent.spawn
sink:      PRIVILEGED              (SinkRegistry.inferred_class → PRIVILEGED; requires a bound grant)
selector:  {kind: generic, uriPattern: "agent://spawn/harness/<D_H>"}
           ← delegation targets are RESOURCES, so a grant may permit spawning
             one harness digest and deny another. This is the whole point.
args:      { harness_digest, brief, capabilities[], reservation, parent_lease }
receipt:   { child_principal_id, child_episode_id, outcome, cost }
events:    ChildSpawned (scheduler) … ChildReturned (scheduler, carries provenance spans)
           + the ordinary kernel quartet: AuthorizationRequested / CapabilityGranted
             / CapabilityAttenuated / BudgetReserved
budget:    additive {usd_micros, tokens, bytes, millis} debit the PARENT's remaining vector;
           structural {depth} increments, {turns} is per-episode. Sibling depths NOT summed.
```

**TCB budget for the verb: ≤ 40 logical LOC.** Current headroom is `1438 − 1365 = 73`. If the implementation exceeds 40, it is a design failure, not a ceiling problem — escalate rather than raise the ceiling.

**Why not earlier.** `004` §3 and `002` §6 both state it, and the Director sustains it: *the kernel gains nothing in Waves 1–4 except tests.* A TCB diff inside the M-4 evidence window makes the nine-row run un-attributable to the reviewed kernel.

---

### 2.3 T-3 · Guardrails — mandatory mechanism vs. declarable "absent-vs-forged"

**RULING: `generalize now`. Adopt the absent-vs-forged model. → `ADR-0079`. Falsifiers `RF-28`…`RF-30`. Lands v0.6.2 / M-3 (sprint 3.4).**

#### 2.3.1 The rule, in one sentence

> **You may turn a guardrail off. You may never turn off the record that it was off. And you may never, under any composition, forge the guardrail's output.**

#### 2.3.2 The mechanics, made unforgeable

Three properties must hold simultaneously, and the third is the one prior formulations left implicit:

1. **Declaration is composition data.** `evaluation: none`, `sandbox: none`, `approval_policy: null` are legal manifest values. `compose()` accepts them and they enter the `D_H` pre-image. Two harnesses differing only in whether the evaluator was declared **MUST NOT** share `D_H`.
2. **Consequence is recorded, not hidden.** The trajectory carries `verdict: null` and `guardrails: {evaluation: "absent", sandbox: "container", approval: "absent"}`.
3. **Attributability is *derived*, never *declared*.** `unattributable_for_promotion` is computed by `compose()` from the resolved graph and stamped onto `FrozenHarness`; it is **not** a manifest field and **not** writable by any plugin. *(CIO's condition from §1.1 — a self-declared attributability flag is a forgery surface, and this is the specific mechanism that closes it.)*

#### 2.3.3 The seven permanent non-negotiables — ratified as the fixed substrate boundary

No composition, no declaration, no policy, and no future ADR short of a reversal may weaken these:

| # | Non-negotiable | Enforced today by `[VERIFIED]` |
|---|---|---|
| **N-1** | **Writer authority on privileged kinds** | `runtime/ledger_emitter.py:37-60` — `PRIVILEGED_KIND_OWNERS` maps 22 kinds to owning roles; `WriterAuthorityError` on violation |
| **N-2** | **Envelope lineage by construction** | `LINEAGE_FIELDS` at `ledger_emitter.py:27-33`; falsifier `RF-01` |
| **N-3** | **Fail-closed selector inclusion** | `domain/selectors/resource_selector.decide()` — total, unknown pair ⇒ deny (`K-48`) |
| **N-4** | **Ledger-as-truth** — `State = fold(events)`, proven by cold replay | `ColdReplayParity` in `test/runtime/test_ledger_truth.py` |
| **N-5** | **Capability attenuation on spawn** | `kernel/attenuation.py:183` (auto-seal) + `kernel/policy.py` step 1b |
| **N-6** | **Signature requirement on any verdict that *is* claimed** | `runtime/evaluator_gateway.py` is the sole legal writer of `VerdictRecorded` and refuses an unbound body |
| **N-7** | **JCS (RFC 8785) as the sole byte source** for every digest and signature | `domain/canonicalisation/jcs.py`; `check_duplication.py --enforce` fails a second algorithm |

**Everything else is policy.** That sentence is the substrate's actual API contract, and `ADR-0079` §D6 puts it in the ADR log where it cannot be lost.

#### 2.3.4 Why this is load-bearing for the general-task-solver thesis

A math pack, a formal-verification pack, or a pure-compute optimisation loop should not be forced to stand up a UID-10002 daemon and preregister an oracle merely to run. Forcing it produces exactly one outcome: someone eventually builds a *bad* escape hatch under deadline pressure. **`ADR-0079` is the good escape hatch, designed before the pressure exists.** This is the precondition for Pack #2 (§4, M-5) being buildable at all.

---

### 2.4 T-4 · Trajectory quality — the born-hollow corpus (G1 / NOVA-1)

**RULING: `strengthen now`. Execute NOVA-1 inside M-2. The `sprint_active.md` carry-to-Wave-4 is OVERRULED in writing. → `ADR-0078`. Falsifier: `RF-12` supersedes `F-12`. Confirmed at M-4 by NOVA-5.**

#### 2.4.1 The verified defect

```text
vanguard/packages/runtime/trajectory.py
  line 10:  _ZERO_COST = {"usd_micros": 0, "tokens": 0, "bytes": 0, "millis": 0}
  line 53:      "cost": dict(_ZERO_COST),   # ← EVERY turn
  line 75:  "cost": dict(_ZERO_COST),       # ← EVERY episode
```

And by omission from `assemble_trajectory`'s return dict: **no `model_routes_used`, no `execution_digest` (`D_R`), no `attribution`.** All three are optional in `schemas/mhf/trajectory.schema.json`, so the record validates.

#### 2.4.2 Why `F-12` passing while I-9 fails is the exact failure I-9 was written to prevent

Invariant I-9: *"Every episode terminates in a schema-valid `mhf.trajectory/1` record that is, **without transformation, a valid harvest row**. A digest over `{ids, n}` is not this invariant."* `F-12` as written asserts only `test_episode_completed_emits_schema_valid_mhf_trajectory_1`. **A content-free record satisfies a schema-validity falsifier.** The falsifier is green; the invariant is violated. `005` §W8 states it precisely: *"That is precisely the shape of failure I-9 was written to prevent."*

#### 2.4.3 Resolution of the live contradiction (finding D-C)

Three artifacts disagree, and this document resolves the disagreement rather than noting it:

| Source | Position |
|---|---|
| `sprint_active.md` "Follow-ups carried out of Wave 1" | → **Wave 4** (*"real per-turn cost needs the governor's settled ledger"*) |
| `004` §2, `005` §W8, `RESEARCH_k3` G1, `proposal_glm_harness_BETA`, `proposal_hy3_improved` | → **now**, single highest-leverage fix available |
| `docs/02_roadmap/milestones.md` / `004` roadmap table | NOVA-1 registered **`PRONTA`** in M-2 |

**Adjudication.** The board's technical premise is *correct but insufficient*. Real settled cost does require the governor's ledger — but the governor's ledger **already exists at `EpisodeCompleted`**: `Receipt.cost` is a `Reservation`, `BudgetCommitted`/`BudgetReleased` are ledgered kernel events, and `assemble_trajectory` already receives the full `events` sequence and the `receipts` sequence as parameters. **The data is in the function's arguments and is being discarded.** The correct scope is therefore not "wait for Wave 4"; it is:

```text
per-turn cost  := fold(BudgetCommitted ∪ BudgetReleased events with causation_id == turn's proposal id)
                  ⊕ Receipt.cost for the turn's receipts          (⊕ = component-wise additive sum)
episode cost   := Σ over turns  (additive dimensions only; depth/turns are structural, never summed)
```

Wave 4's genuine remaining contribution is **NOVA-5**: confirming on one *real* run that the wired values are non-zero and internally consistent. That is confirmation, not implementation.

> **Director determination, recorded:** item 1a of the `SYSTEM_OVERVIEW` §6.3 checklist is **selected**; item 1b is **rejected**; item 1c is **discharged by this section**. `sprint_active.md`'s carry-out row must be struck and replaced (§7.2).

#### 2.4.4 What "populated" must mean — the content assertions

`RF-12` asserts, for every `EpisodeCompleted` on any path that ran at least one turn:

```text
1.  len(turns) == count(ProposalProduced in episode)            and > 0
2.  ∃ t ∈ turns : t.cost.tokens > 0                              (a real model was called)
3.  ∀ t ∈ turns : t.cost.millis > 0                              (latency is recorded per turn)
4.  episode.cost == Σ_t t.cost   component-wise, additive dims only
5.  model_routes_used ≠ []  ∧  ∀ r : r.model_fingerprint is not None
6.  execution_digest (D_R) is present ∧ execution_digest ≠ harness_digest
7.  verdict is a SignedVerdict object  XOR  verdict is null with a recorded reason
8.  guardrails object present (ADR-0079)  ∧  unattributable_for_promotion ∈ {true,false}
```

Assertion **6** is the one no prior review named: `D_R` is currently **never computed anywhere in the tree** `[VERIFIED — no assignment to `execution_digest` exists]`. `D_R` is the denominator of every future A/B comparison. A corpus with `D_H` but no `D_R` cannot distinguish "same harness, different model build" from "same run" — which silently invalidates every router experiment. `ADR-0078` §D3 defines `D_R` constructively.

#### 2.4.5 The irreversibility argument, stated once and not repeated

Trajectories cannot be back-filled. The governor's settled cost ledger for a past run is *gone* — not expensive to recover, **gone**. Every episode completing before this lands is a permanently degraded row in the only corpus Layer 3 will ever have. This is the sole item on the entire register with a **one-way clock**.

---

### 2.5 T-5 · Layer-0 absorption timeline

**RULING: `lock now` — confirm absorb-then-delete at 3.1, gated on NOVA-4. → `ADR-0081`. Falsifiers `RF-13`…`RF-19` (the NOVA-4 six, plus the FSM gap). Lands v0.6.2 / M-3.**

#### 2.5.1 Current state `[VERIFIED this pass]`

```text
layer0/
├── __init__.py
├── compose/{__init__,compiler}.py                        → absorb into runtime/compose.py
├── events/{__init__,emitter,envelope,store,taxonomy}.py  → dead weight; packages twins exist
└── registry/{__init__,broker,grants,isolation,
             lifecycle,sandbox,validator,worker}.py       → absorb into runtime/registry/
```
`kernel/`, `scheduler/`, `spi/`, and `events/{selectors,canonical,fold,blob}.py` are **gone** (deleted at 2.2-B). The two headline forensic defects — `driver.py:138`'s fabricated unsigned `"pass"` and `spi/ceiling.py:21`'s fail-open empty-capability branch — **died with them**. Zero `layer0` imports remain under `vanguard/` (provenance comments only).

#### 2.5.2 The risk `005` §W7 names, sharpened by this pass

`layer0/registry/` and `layer0/compose/` have **no packages twin and have never run on the canonical path**, and Wave 3 rests its entire framework claim on them. This pass adds a concrete instance of that risk rather than restating it in the abstract:

> **`[VERIFIED]` `layer0/registry/lifecycle.py` cannot ledger two of its seven states.** `_EVENT` (lines 33-39) maps `RESOLVED → PluginResolved`, `ACTIVATED → PluginActivated`, `QUIESCING → PluginQuiesced`, `RETIRED → PluginRetired`, `FAULTED → PluginFaulted`. **`DISCOVERED` and `VERIFIED` map to nothing**, and `_go()` does `kind = _EVENT.get(target)` followed by `if kind is not None:` — so those transitions mutate `self.state` and emit **silently**.
>
> The `EventKind` enum in `domain/wire/types_gen.py:56-60` confirms only five `PLUGIN_*` members exist. `SPEC.md` §1.2's Plugins row lists the same five. **The M-3 exit gate — "every transition ledgered" — is therefore unsatisfiable against the closed 56-kind catalog.**

**Consequences, all three of which must be discharged together:**

1. `VERIFIED` is the state at which **the capability-ceiling policy check occurs**. An unledgered `VERIFIED` means the single most security-relevant lifecycle transition leaves no evidence. This is a **CIO-class** defect, not a cosmetic one.
2. Closing it requires two new event kinds — `PluginDiscovered`, `PluginVerified` — which `sprint_active.md` lists under **Director-Only Escalations**. `ADR-0081` §D3 is that escalation, ruled here.
3. `PRIVILEGED_KIND_OWNERS` gains two `registry`-owned rows; `reducer.py` gains two fold rules; the `CataloguedKindsAreFoldedOrAllowlisted` property test extends from 56 to 58 kinds.

#### 2.5.3 The absorb-then-delete sequence, with its parity gate

`SPEC.md` §1 is binding: *"Duplicate kernels, schedulers, mocks, and synthetic verdict paths MUST NOT be deleted until a behavioral parity gate."* The sequence is therefore fixed:

```text
3.1-A  Absorb registry FSM  → runtime/registry/{lifecycle,broker,isolation,validator}.py
       (+ PluginDiscovered / PluginVerified kinds, ADR-0081 §D3)
3.1-B  Absorb compose       → runtime/compose.py (compose v2, mhf.manifest/2 aware)
3.1-C  Echo plugin walks DISCOVERED→…→RETIRED over UDS, all SEVEN transitions ledgered
NOVA-4 Six negatives green (RF-13…RF-18) + FSM completeness (RF-19)
──────── parity gate ────────
3.1-Z  rm -rf layer0/  ·  delete test/layer0/  ·  remove the advisory CI step
```

`layer0/events/` is **not** absorbed — it is dead weight with live packages twins (`runtime/ledger_emitter.py`, `domain/ledger/events.py`, `adapters/stores/event_store.py`). It is deleted at 3.1-Z with no absorption step. Recording this explicitly prevents a well-meaning developer from "absorbing" a fourth event taxonomy.

#### 2.5.4 Wave-3 rebalancing — the ruling on T-1/T-5's consequence

`005` §W7's arithmetic is correct and damning: **Wave 1 received 17 tasks and 15 falsifiers for the trust spine; Wave 3 receives 7 tasks for the entire product claim, built on the least-proven code in the tree.** The Leadership 7 rules that Wave 3 is **rebalanced, not re-labelled**:

| Sprint | Content | Falsifiers |
|---|---|---|
| 3.1 | Registry FSM · compose v2 · echo plugin · isolation broker | `RF-13`…`RF-19` (NOVA-4 six + FSM completeness) |
| 3.2 | Pack on the wire · coding-token sweep · **one manifest parser (was `3.2-C`, now the T-1 vehicle)** | `RF-20`, `RF-21` |
| **3.3** | **Component graph** — `mhf.manifest/2`, `D_H` over the graph, `code-default` migration | `RF-23`…`RF-27` |
| **3.4** | **Absent-vs-forged** — declarable guardrails, derived attributability | `RF-28`…`RF-30` |
| **3.5** | **`agent.spawn` design only** — design note + falsifier sketches, **zero kernel diff** | `RF-31`…`RF-35` (written red, unrun until M-6) |

**Falsifiers are never traded away to make a wave fit.** If Wave 3 will not fit, **breadth is shed** — the WASM tier, mandatory plugin signatures, and any second product plugin are already out of scope and stay out.

---

### 2.6 T-6 · The loop as mechanism — publishing the claim with its falsifier

**RULING: `lock now` + `keep, document`. → `ADR-0082` §D1. Falsifier `RF-36` (an open standing challenge with a one-year clock). Lands v0.6.1 / M-2 as documentation; the clock runs to M-8.**

#### 2.6.1 The claim, stated normatively for the first time

> **The Universal Turn Loop is Mechanism, not Plugin.**
> `observe → propose → authorize → effect → receipt → evaluate → (reflect)*`
> Agentic algorithms differ in **what they propose** and **when and to whom they delegate**. They do **not** differ in whether an effect is authorized, whether a receipt is recorded, or whether a verdict is signed. Any algorithm expressible at all is expressible as **spawn topology + component-graph wiring + planner policy** over this one loop.

#### 2.6.2 The bound falsifier `RF-36`

> **`RF-36` — the Standing Challenge.** *Name an agentic algorithm that cannot be expressed as spawn-topology + planner policy over the universal turn loop, and demonstrate it as a manifest that fails to compile or a behaviour that requires an engine diff.*
>
> - **Refuted** ⇒ that is genuine `ADR-0070` reversal evidence and the loop becomes negotiable.
> - **Survives one year** (opened at M-2 ratification, adjudicated at M-8) ⇒ the loop is proven and the argument is closed by evidence rather than by fatigue.

**The M-8 validation suite is the structured half of this challenge:** debate, critic/revisor, evolutionary search, and multi-agent economic delegation must all run **multi-pack with zero engine modification**. A red there is a partial refutation of `RF-36` and reopens `ADR-0070` on its own terms.

#### 2.6.3 Why the claim must be published rather than assumed

`005` §W3: *"State this as a claim with a falsifier, or it will be relitigated every quarter."* This is a governance ruling, not a technical one. Every quarter the question is re-asked at full cost is a quarter not spent on B and C. A published claim with an open bounty converts a recurring debate into a **single, dated, falsifiable proposition**.

---

### 2.7 T-7 · `K ≪ N` — proving concurrency via NOVA-2 (cold suspend/resume)

**RULING: `strengthen now`. NOVA-2 executes in M-2 and is a **hard entry gate for M-3**. → `ADR-0082` §D2. Falsifier `RF-22`.**

#### 2.7.1 The precise question

> **Is an episode's continuation reconstructible from the ledger alone, or does resuming require the live Python object?**

`002` §5 asserts *"many logical agents share a bounded worker pool (`K ≪ N`)"*. **Nothing in the tree demonstrates logical-agent / worker separation** `[VERIFIED]`: `EpisodeEngine` *is* the scheduler shell and `HarnessSession` (646 LOC) holds live per-run state. `F-02` (`ColdReplayParity`) proves grants, budgets, approvals and the episode FSM survive a cold fold — **most** of the answer, but not the part that decides M-7.

#### 2.7.2 `RF-22` — the falsifier, specified to the assertion

```text
GIVEN   an episode E on a real SQLite WAL ledger, driven to mid-turn:
        TurnStarted emitted · ProposalProduced emitted · a lease RESERVED
        · EffectStarted (S8a durable intent, fsynced) emitted · NO terminal effect event
WHEN    the process is terminated (SIGKILL — not a graceful shutdown; a graceful
        path may flush state that a crash would not)
AND     a FRESH interpreter process opens the same WAL, folds cold, and resumes
THEN    1. the reconstructed episode FSM state == the pre-kill state, structurally
        2. the reconstructed grant tree and remaining budget vector are byte-equal
        3. the undeterminable effect is reconciled via EffectReconciled (ADR-0026)
        4. the episode runs to a terminal event and emits a trajectory satisfying RF-12
        5. no object identity from the first process is required at any point
```

#### 2.7.3 Why the Tech Lead makes this an M-3 entry gate rather than a Wave-2 nice-to-have

| Outcome | Consequence |
|---|---|
| **Green** | M-7 concurrency is a **scheduling refactor**. I-11 may be lifted on measurement alone. `HarnessSession` is a cache, not a source of truth. M-3's abstractions may assume ledger-reconstructibility. |
| **Red** | There is hidden in-process coupling. M-7 is a **rewrite**. M-3 must *not* build a component graph and plugin lifecycle on top of an assumption that is false — and we would rather discover that in a 200-line test at M-2 than in a re-architecture at M-7. |

`005` calls it *"the highest-value cheap test not currently on the board."* This document puts it on the board as a **gate**, which is the only form in which a cheap high-value test reliably gets run.

---

### 2.8 T-8 · Governance mass — scheduling the documentation collapse

**RULING: `revisit after M-4` — collapse is scheduled at **M-5**, and is FORBIDDEN before M-4 closes. → `ADR-0082` §D3.**

#### 2.8.1 The measured problem

`005` §W6 measures ~3.4k lines of normative and planning prose across **seven authority tiers** — *currently larger than the substrate work it governs*. Two costs are already realised:

1. The deferred/refusal list is maintained in **four** places: `SPEC.md` §9, `ADR-0073`, `002` §2, `milestones.md`.
2. `ADR-0076` exists **solely** to adjudicate which of two live artifacts is canonical — *the tax on having let the fork live*, not a permanent feature of the process.

**Prose duplication drifts exactly the way code duplication drifts, and prose has no linter.** This pass found a third instance directly: the `F-*` namespace collision (§1.4 finding 3, §7.3) — two documents using the same identifiers for different things, undetected because no tool checks.

#### 2.8.2 The target and the timing

**Target:** `SPEC.md` (law) + `docs/05_adr/` (decisions) + **one** living board. A senior developer productive from **three** documents, not seven. GAMMA (`001`) and the `002` register are retired as standing authorities once their content is absorbed — their falsifier tables migrate into `SPEC.md`'s invariant section and the board respectively.

**Timing is not negotiable in the other direction either:** mid-flight documentation surgery during Wave 2/3 is strictly worse than the duplication, because the corpus is the only thing keeping two concurrent developers coherent. **Every source agrees on both the target and the timing.** Scheduled as `5.1-A/B/C`.

---

### 2.9 T-9 · The five-SPI freeze

**RULING: `revisit after M-4` — the freeze **stands** through M-8 and is re-examined at **M-9** (`9.2-B`) against a mature component graph. → `ADR-0082` §D4.**

`ADR-M0-03` freezes exactly five SPIs (`IPlanner`, `IMemoryEngine`, `IToolkit`, `IContextManager`, `IEvaluationGate`) `[VERIFIED — all five present in ports/spi.py, no sixth]` and requires *"a design review, not a PR"* for a sixth. `005` §8 records the caveat worth acting on: the freeze *"is defended more strongly than its evidence supports."*

> **Ruling.** The **guard** is correct and stays. What must not happen is *"a sixth SPI requires a design review"* hardening into *"there are five SPIs forever."* `ADR-0082` §D4 therefore does two things: it **reaffirms the guard** and it **schedules the review** at M-9, so the revisit happens by calendar rather than by argument.

**Two candidate sixth SPIs are named now so the M-9 review has concrete subjects rather than a blank page:**

| Candidate | Case for | Case against |
|---|---|---|
| `IAggregator` (debate/voting/tie-break over N proposals) | M-8 debate and evolutionary compositions need a *typed* reduction over sibling results; today it must hide inside a planner | May be `IPlanner` with a different component `kind` under `mhf.manifest/2` — in which case the component graph **dissolves the need**, which is itself the strongest argument for shipping `ADR-0077` first |
| `IScheduler` (independence-group policy at M-7) | Concurrency policy is strategy, not authority | The scheduler decides *who acts when* — that is the Decision Plane. Making it pluggable moves authority above the extension line. **Provisionally refuse.** |

Note the shape of that table: **the component graph may make the sixth SPI unnecessary.** That is the strongest available argument for the M-9 timing — reviewing the freeze before the graph is mature would answer the wrong question.

---

## §3 · Drafted Append-Only ADR Catalog — `ADR-0077` … `ADR-0082`

> **Status of this section.** Each block below is the **complete proposed text** of a new append-only ADR, ready to be written to the named path. They are **drafts** until committed with a Director signature. Per `ADR-0000`, every ADR states what it narrows or extends and names its reversal condition; per `ADR-0074`, **a concept without a bound falsifier is not locked**, so every ADR carries a 1-to-1 falsifier table.
>
> **Namespace note.** New falsifiers use the `RF-*` (Register Falsifier) prefix per §7.3, which resolves the verified collision between `docs/04_annex/KERNEL.md`'s `F-01…F-25` and the `002` register's `F-01…F-22`. Existing register falsifiers are aliased `RF-01 ≡ F-01 … RF-22 ≡ F-22`.
>
> ⚠ **Numbering precedence.** The `RF-nn` identifiers used narratively in §2 and §3 are *thematic groupings*. Because `RF-01…RF-22` are consumed by the aliased Wave-0/1 falsifiers, the **authoritative monotonic numbering starts at `RF-23` and is defined in [§6.3](#63-the-1-to-1-executable-falsifier-matrix)**. Where §2/§3 and §6.3 differ on a number, **§6.3 wins**; the test-function names are identical in both and are the stable key.

---

### 3.1 `ADR-0077` — The Named Component Graph is the composition surface (`mhf.manifest/2`)

**Path:** `docs/05_adr/0077-named-component-graph-is-the-composition-surface.md`

---

#### Status
`accepted` — v0.6.1 Substrate Correction Lock. Implements v0.6.2 / M-3 sprint 3.3.

#### Narrows / extends
**Extends** `ADR-0071` (identity trinity: `D_H` now covers the graph, principle unchanged) and `ADR-0072` (wire-first plugin boundary: components are plugin instances). **Narrows** `SPEC.md` §2.3's fixed-key `harness.yaml` example by superseding the *shape*, not the semantics. **Does not reopen** `ADR-0069`, `ADR-0070`, `ADR-0073`, or `ADR-0074`.

#### Context

`SPEC.md` §2.3 and `schemas/mhf/harness_manifest.schema.json#/$defs/PluginBindings` bind six fixed keys — `planner`, `context`, `memory`, `toolkits[]`, `evaluation`, `model_routes[]` — under `additionalProperties: false`. This is a **five-hole agent shape**. It expresses "a ReAct coding agent with swappable parts" exactly, and it cannot express a critic loop (two planner-kind components), debate (N proposers + aggregator), tree search (expansion/scoring/selection as separate policies), evolutionary search (population operator + fitness binding), or a dual-gate research agent (cheap inline + exterior terminal evaluation).

None of these needs a new engine — all are spawn topologies plus policy (`ADR-0070`). But there is **nowhere in the manifest to name them**, so today they can only be smuggled inside one monolithic planner plugin. That is the "inherit from a large predefined agent architecture" outcome the substrate thesis rejects, arriving through the configuration file instead of through a base class.

**Two verified facts drive the timing and the cost:**

1. `D_H` is computed over the manifest pre-image (`domain/artifacts/manifest.py:83-95`). Changing the manifest shape changes every `D_H`. Before M-4 that costs one deliberate re-attribution of a pre-production corpus; after M-4 it costs a schema migration, a `D_H` migration, a rewrite of every pack, and the permanent attribution of every trajectory in the corpus to a superseded shape.
2. The general dialect **already exists in `domain/`**. `HarnessManifest.components` is typed `tuple[tuple[str, tuple[str, ...]], ...]` — a named component map — and `agency/manifests/vg-code-default/manifest.json` populates it with seven named components. There are two live manifest dialects and two parsers (`agency/manifests/loader.py` for YAML, `domain/artifacts/manifest.parse_manifest()` for JSON). This decision **converges them onto the general one**; it does not invent a new model.

The external comparison (DeepSeek Harness: an ordered stack of plugin bundles with *"no privileged core to patch"*) contributes exactly one importable property and one refused one — see D7.

#### Decision

**D1.** The harness manifest becomes a **named component graph**, published as **`mhf.manifest/2`**. A manifest declares a map `components: {<name>: {kind, ref, config, ceiling}}` plus an explicit `bindings` section describing wiring between named components.

**D2.** `kind` is one of the five frozen SPI kinds (`planner`, `context`, `memory`, `toolkit`, `evaluation`) — `ADR-M0-03` is **not** reopened. **Multiplicity is what changes: `kind` no longer implies cardinality one.** A composition MAY declare N components of the same kind under distinct names.

**D3.** Slot names (`planner`, `context`, `memory`, `evaluation`, `toolkits`) survive as **pack convention**, never as schema constraint. `packs/code-default` declares one planner *named* `planner`; nothing in `compose()`, `kernel/`, or `agency/` may key on that name.

**D4.** `D_H` extends to cover the graph: component names, kinds, resolved refs and digests, per-component config digests, per-component ceilings, **and the bindings** — in addition to the existing system prompt, harness capability ceiling, approval policy, and model routes. **Principle unchanged** (`ADR-0071`, `ADR-0074`, `A-5`): `D_H` is the digest of the complete behaviour-affecting composition. Two graphs differing only in a binding edge MUST NOT share `D_H`.

**D5.** `mhf.harness/1` is **frozen, not deleted**. It remains readable through M-4 so that pre-cut trajectories stay attributable. `compose()` accepts both `api` values; `/1` inputs are normalised to the `/2` internal model at parse time. `/1` acceptance is removed at M-5.

**D6.** **One parser.** `agency/manifests/loader.py` is deleted as a second YAML→harness path. Exactly one function produces a `HarnessManifest` from bytes, in `domain/artifacts/manifest.py`, for both YAML and JSON surface syntax. Board task `3.2-C` is re-labelled from `DEV-LOCAL` to `DIRECTOR` and folded into sprint 3.3.

**D7.** **Flatness at the composition surface is imported; absence of a privileged core is refused.** These are orthogonal properties and this ADR takes exactly one. Every component ceiling is intersected with the harness ceiling **fail-closed** at compose (`ADR-0072`); an empty component ceiling authorises nothing; no component may write a privileged event kind (`ADR-0074`, `PRIVILEGED_KIND_OWNERS`). `SPEC.md` §9's refusal of "no privileged core" flatness stands and is restated here so the two properties can never be conflated by a future reader.

**D8.** Compose resolves the graph in **topological order** over `bindings`. A cycle is a **compose-time error**, never a runtime behaviour (`ADR-0005`: registries freeze at composition; unknown names and cycles fail at composition). Self-edges are rejected.

**D9.** The graph is **not** a workflow DAG and grants no execution semantics. `bindings` declares *what a component may address*, not *when it runs*. Execution order remains the universal turn loop plus spawn topology (`ADR-0070`, `ADR-0082` §D1). `SPEC.md` §9's refusal of workflow-DAG engines is unaffected.

#### Normative schema — `mhf.manifest/2` (JSON Schema Draft 2020-12)

Full text in §6.1. Summary of the delta from `mhf.harness/1`:

```yaml
api: mhf.manifest/2
id: code-default
components:
  planner:    {kind: planner,    ref: mhf.planner.drive-until-green@^1, config: {...}}
  context:    {kind: context,    ref: mhf.context.repo-map@^1,          config: {...}}
  memory:     {kind: memory,     ref: mhf.memory.sqlite-kv@^1}
  evaluation: {kind: evaluation, ref: mhf.eval.oracle-gate@^1,          config: {oracle: coding-oracle@3}}
  fs:         {kind: toolkit,    ref: mhf.toolkit.fs@^1,       ceiling: [{verb: fs.read,     selector: {...}}]}
  patch:      {kind: toolkit,    ref: mhf.toolkit.ast-patch@^2, ceiling: [{verb: patch.apply, selector: {...}}]}
  terminal:   {kind: toolkit,    ref: mhf.toolkit.terminal@^1,  ceiling: [{verb: proc.exec,   selector: {...}}]}
  index:      {kind: toolkit,    ref: mhf.toolkit.index@^1}
bindings:
  - {from: planner, to: [context, memory, fs, patch, terminal, index], relation: uses}
  - {from: planner, to: [evaluation],                                  relation: gated_by}
model_routes: [...]        # unchanged from /1
system_prompt: ./system-prompt.txt
capabilities: [...]        # harness ceiling; every component ceiling ⊆ this
budget:  {usd_micros: 250000, millis: 1800000, tokens: 64000, bytes: 0, turns: 40, depth: 2}
approval_policy: ./approval-policy.json
```

**Critic-loop example — the shape `mhf.harness/1` cannot express:**

```yaml
api: mhf.manifest/2
id: critic-loop-reference
components:
  proposer: {kind: planner,    ref: mhf.planner.drive-until-green@^1}
  critic:   {kind: planner,    ref: mhf.planner.critic@^1, config: {max_rounds: 3}}
  inline:   {kind: evaluation, ref: mhf.eval.lint-gate@^1}          # cheap, agent-side
  terminal: {kind: evaluation, ref: mhf.eval.oracle-gate@^1}        # exterior, signed
bindings:
  - {from: proposer, to: [critic],   relation: reviewed_by}
  - {from: proposer, to: [inline],   relation: gated_by}
  - {from: proposer, to: [terminal], relation: gated_by}
```

#### Bound falsifiers

| ID | Falsifier | Wrong implementation it kills |
|---|---|---|
| `RF-23` | `test_component_graph_compiles_two_planners_with_distinct_names` | `kind` implying cardinality one; a compose that keys on slot names |
| `RF-24` | `test_six_reference_topologies_compile_to_six_distinct_D_H` | A graph schema that cannot express debate / tree search / dual-gate |
| `RF-25` | `test_binding_edge_change_changes_D_H` | `D_H` over components only, ignoring wiring — the §D4 collapse |
| `RF-26` | `test_component_ceiling_intersects_harness_ceiling_fail_closed` | A per-component ceiling that widens, or an empty ceiling that authorises |
| `RF-27` | `test_cyclic_binding_fails_at_compose_not_runtime` | Cycle detection deferred to execution (violates `ADR-0005`) |
| `RF-21` | `test_exactly_one_manifest_parser_exists` (`check_duplication.py --enforce`) | A second YAML→harness path surviving D6 |

#### Reversal condition

A composition topology that the graph **cannot** express and that a fixed-slot template **can** — or measured evidence that graph resolution at compose time costs more than the fixed-slot path by a margin that materially affects run latency. Preference, aesthetics, or migration inconvenience are **not** sufficient grounds (`ADR-0000`).

---

### 3.2 `ADR-0078` — The trajectory content contract: a learnable corpus (NOVA-1)

**Path:** `docs/05_adr/0078-trajectory-content-contract-learnable-corpus.md`

---

#### Status
`accepted` — v0.6.1 Substrate Correction Lock. Implements **immediately, inside M-2**.

#### Narrows / extends
**Narrows** `F-12` as written in the `002` register §4.2 (schema validity only) by replacing it with `RF-12` (content assertions). **Extends** `ADR-0074` §7 and `SPEC.md` I-9. **Overrules** the `sprint_active.md` "Follow-ups carried out of Wave 1" row that carries per-turn cost to Wave 4.

#### Context

`vanguard/packages/runtime/trajectory.py` defines `_ZERO_COST` at line 10 and emits it at line 53 (every turn) and line 75 (every episode). The returned object also omits `model_routes_used`, `execution_digest`, and `attribution`, all of which are optional in `schemas/mhf/trajectory.schema.json`. **Every completed episode therefore emits a record that is schema-valid, cryptographically attributable, and unusable.**

Invariant I-9 states that a trajectory must be *"without transformation, a valid harvest row"* and that *"a digest over `{ids, n}` is not this invariant."* `F-12` asserts only schema validity, which a content-free record satisfies. **The falsifier is green while the invariant it certifies is violated** — the same defect class as `F-18` (a linter narrower than its invariant) and `D-D` (a link checker scanning two files).

Everything downstream is undefined without this: cost-aware policy learning; escalation calibration (`SPEC.md` §5.3's `P(pass ∣ action, context)`); any router experiment; the DPO harvest (`SPEC.md` §7); skill synthesis (§5.4); the entire M-10 meta-cognitive layer.

**Trajectories cannot be back-filled.** The governor's settled cost ledger for a past run is gone. This is the only item in the register with a one-way clock.

**The objection recorded on the board — *"real per-turn cost needs the governor's settled ledger"* — is correct but insufficient.** The settled ledger already exists at `EpisodeCompleted`: `Receipt.cost` is a `Reservation`, `BudgetCommitted`/`BudgetReleased` are ledgered kernel events, and `assemble_trajectory` already receives both `events` and `receipts` as parameters. **The data is in the function's arguments and is being discarded.**

#### Decision

**D1. Per-turn cost is computed, not stubbed.** `_ZERO_COST` is deleted. For each turn `t`:

```text
cost(t) = ⊕ { BudgetCommitted.payload.cost : causation_id ∈ turn_t.effect_ids }
        ⊕ { Receipt.cost : receipt ∈ turn_t.receipts }
        ⊕ { model usage for turn_t : (tokens, usd_micros, millis) from ModelPort usage accounting }
```
where `⊕` is component-wise addition over the **additive** dimensions `{usd_micros, tokens, bytes, millis}` only. Structural ceilings `{depth, turns}` are **not costs** and MUST NOT appear in a `CostVector` (`ADR-0074` §2; already enforced by the schema's `additionalProperties: false`).

**D2. Episode cost is the additive sum over turns**, and this MUST be assertable: `episode.cost == Σ_t turn_t.cost` component-wise. A discrepancy is a defect, not rounding.

**D3. `D_R` is defined constructively and emitted.** `execution_digest` is currently never assigned anywhere in the tree. It becomes:

```text
D_R = JCS-SHA256 {
    "harness_digest":   D_H,
    "runtime":          {python: <version>, platform: <sys.platform>, package: <version>},
    "environment":      {kind: "git-worktree"|"fake"|"sandboxed", digest: <workspace root digest>},
    "model_identity":   [ {tier, provider, model, model_fingerprint} … ],   # sorted, JCS-canonical
    "oracle_identity":  <preregistered oracle id@version>  |  null
}
```
`D_R ≠ D_H` MUST hold and MUST be asserted (`RF-12` clause 6). `D_X` (`D_R` + dataset + protocol) remains lab-owned and is not emitted per-episode.

**D4. Required-now vs required-later, stated explicitly** so that no field becomes a false green:

| Field | Required from | Rationale |
|---|---|---|
| `turns[].cost` (non-zero `tokens`, `millis`) | **M-2** | The core defect |
| `cost` (episode, == Σ turns) | **M-2** | Internal consistency is checkable now |
| `model_routes_used[].model_fingerprint` | **M-2** | Provider response metadata; available at the adapter |
| `execution_digest` (`D_R`) | **M-2** | Computable at compose+wire time |
| `verdict` (SignedVerdict **or** explicit `null` + reason) | **M-2** | Already ledgered; only the null-with-reason case is new |
| `guardrails` + `unattributable_for_promotion` | **M-3** | Depends on `ADR-0079` |
| `attribution.prefix_hits` | **M-10** | The pack cannot compute it before the harvester exists; requiring it now manufactures a false green |
| `attribution.escalations`, `attribution.repair_rounds` | **M-2** | Both are already counted by `tier_escalation.py` and the planner |

**D5. Latency is a first-class cost dimension.** `millis` is **charged compute time**, never wall-clock under concurrency (`ADR-0074` §2). Under sequential execution (I-11) they coincide; the distinction is locked now so that M-7 does not silently redefine the corpus.

**D6. Cost is written by the governor, never by the planner.** Trajectory assembly reads ledgered kernel events and receipts. **No plugin, planner, or model adapter may author a cost field.** Self-reported cost is a forgery surface identical in kind to a self-reported verdict.

#### Bound falsifier — `RF-12` (supersedes `F-12`)

```python
# test/falsifiers/test_rf12_trajectory_content.py
def test_episode_completed_emits_populated_mhf_trajectory_1():
    traj = run_scripted_episode_to_completion()          # real ledger, cassette model
    assert traj["schema"] == "mhf.trajectory/1"
    validate_against_schema(traj, "schemas/mhf/trajectory.schema.json")     # necessary, not sufficient
    # 1 — turns are populated and match ProposalProduced count
    assert len(traj["turns"]) == count_events(kind="ProposalProduced") > 0
    # 2/3 — a real model was called, and latency is per-turn
    assert any(t["cost"]["tokens"] > 0 for t in traj["turns"])
    assert all(t["cost"]["millis"] > 0 for t in traj["turns"])
    # 4 — episode cost is the additive sum, component-wise
    for dim in ("usd_micros", "tokens", "bytes", "millis"):
        assert traj["cost"][dim] == sum(t["cost"][dim] for t in traj["turns"])
    # 5 — model fingerprint present
    assert traj["model_routes_used"]
    assert all(r["model_fingerprint"] for r in traj["model_routes_used"])
    # 6 — D_R present and NOT collapsed into D_H
    assert traj["execution_digest"] and traj["execution_digest"] != traj["harness_digest"]
    # 7 — verdict embedded or explicitly null with a reason
    assert traj["verdict"] is not None or traj["outcome"] in ("aborted", "budget_exhausted")
```

| ID | Falsifier | Wrong implementation it kills |
|---|---|---|
| `RF-12` | `test_episode_completed_emits_populated_mhf_trajectory_1` | `_ZERO_COST`; a digest over `{ids, n}`; schema-validity-only assertions |
| `RF-37` | `test_planner_cannot_author_a_cost_field` | Self-reported cost from a plugin or model adapter (D6) |
| `NOVA-5` / `RF-12-E2E` | `test_real_run_trajectory_carries_nonzero_cost` (M-4) | Green unit cost with a hollow real run |

#### Reversal condition

Measured evidence that per-turn cost accounting materially distorts the measured latency it records (an observer-effect argument), **or** a demonstration that a downstream learner performs equally well on cost-free rows. Neither is currently plausible; both are stated so the ADR is falsifiable rather than merely asserted.

---

### 3.3 `ADR-0079` — Absent-vs-Forged: guardrails are declarable, evidence never is

**Path:** `docs/05_adr/0079-absent-vs-forged-declarable-guardrails.md`

---

#### Status
`accepted` — v0.6.1 Substrate Correction Lock. Implements v0.6.2 / M-3 sprint 3.4.

#### Narrows / extends
**Extends** `ADR-0072` (evaluator exteriority) and `ADR-0074` (writer authority). **Narrows** the implicit reading of `SPEC.md` §2.1 under which an exterior evaluator is mandatory per composition. **Does not** weaken `ADR-0004` (the verifier is immutable and unreachable) — it is restated as N-6 below.

#### Context

Today the guardrail **mechanism** is mandatory and the guardrail **policy** is mandatory, and only the second needs to be. A research agent, a formal-verification pack, or a pure-compute optimisation loop should not require a UID-10002 daemon and a preregistered oracle merely to run. Guardrails are drifting from infrastructure into **product constraint** (`005` §13).

Left unresolved, this produces a predictable outcome: under deadline pressure someone builds a *bad* escape hatch — a debug flag, an env-var bypass, a test-only unsigned path. `ADR-0079` is the **good** escape hatch, designed before the pressure exists.

The distinction the substrate must enforce is **not** *guarded vs unguarded*. It is **absent vs forged**.

#### Decision

**D1. A composition MAY declare a guardrail absent.** Legal declarations: `evaluation: none` (no evaluation component in the graph), `sandbox: none` (no container tier for a component whose verbs have no external footprint), `approval_policy: null`.

**D2. Declared absence is composition identity.** The declaration enters the `D_H` pre-image. Two harnesses differing **only** in whether an evaluator was declared MUST NOT share `D_H`. Absence is therefore permanently attributable and can never be retroactively denied.

**D3. Consequence is recorded in the trajectory.** The record carries:

```json
"guardrails": {
  "evaluation": "absent" | "<oracle-id@version>",
  "sandbox":    "absent" | "in_process" | "subprocess" | "container" | "wasm",
  "approval":   "absent" | "<approval-policy-digest>"
},
"unattributable_for_promotion": true
```
and `verdict: null` when evaluation is absent. A `null` verdict with `guardrails.evaluation == "absent"` is **legitimate**; a `null` verdict with a declared oracle is an **instrument error**.

**D4. `unattributable_for_promotion` is DERIVED, never DECLARED.** It is computed by `compose()` from the resolved graph and stamped onto `FrozenHarness`; it is **not** a manifest field, **not** writable by any plugin, and **not** settable by any runtime flag. *(Without this clause the whole model is a forgery surface: a composition could declare itself attributable while running unguarded.)*

**D5. An unsigned verdict remains categorically illegal under every composition.** `runtime/evaluator_gateway.py` stays the sole legal writer of `VerdictRecorded` and refuses any body without a valid, request-bound Ed25519 signature. **`evaluation: none` means no verdict — it never means an easier verdict.** This is the whole content of the word "forged".

**D6. The seven permanent non-negotiables** (N-1 … N-7 of §2.3.3) are ratified as the fixed substrate boundary. No composition, declaration, policy, or future ADR short of an explicit reversal may weaken them. **Everything else is policy.**

**D7. Absence is per-component as well as per-composition.** A graph may declare a container tier for `terminal` and `in_process` for `context`. `in_process` remains a **privilege granted by policy**, never a default (I-6, `ADR-M0-11`), and still speaks the same JSON-RPC wire (`ADR-0072`).

#### Bound falsifiers

| ID | Falsifier | Wrong implementation it kills |
|---|---|---|
| `RF-28` | `test_evaluation_none_compiles_and_changes_D_H` | Compose rejecting declared absence; or accepting it without changing `D_H` |
| `RF-29` | `test_unsigned_verdict_rejected_even_with_evaluation_none_declared` | "Absence" degrading into "unsigned is fine here" — the forgery path |
| `RF-30` | `test_unattributable_flag_is_derived_and_not_manifest_writable` | A manifest-authored or plugin-writable attributability boolean (D4) |
| `RF-30b` | `test_in_process_component_requires_explicit_policy_grant` | `in_process` as a default rather than a privilege (I-6) |

#### Reversal condition

Evidence that a declared-absent guardrail was used to produce a promotion-eligible result — i.e. that `unattributable_for_promotion` failed to propagate to the promotion frontier. That would mean D4 is unimplemented, and the correct response would be to make guardrails mandatory again until it is.

---

### 3.4 `ADR-0080` — `agent.spawn` as a capability-mediated kernel verb (design-locked; implementation deferred to M-6)

**Path:** `docs/05_adr/0080-agent-spawn-as-capability-mediated-kernel-verb.md`

---

#### Status
`accepted (design-locked, implementation deferred)` — v0.6.1 design lock; implementation authorised at **M-6 / v0.8.0** and **forbidden before M-4 closes**.

#### Narrows / extends
**Extends** `ADR-0070` (recursive substrate; `spawn` as the sole delegation primitive) by moving the primitive from the engine to the reference monitor. **Corrects** a stale statement in `agency/episode/engine.py`'s `spawn()` docstring regarding `ADR-0054` (see C3). **Constrained by** `ADR-0023` (TCB size ceiling) and `ADR-0075` (Wave-4 stop line).

#### Context

**C1.** `EpisodeEngine.spawn(...)` at `agency/episode/engine.py:531` is a privileged **engine call**. `IPlanner` (`ports/spi.py`) exposes only `plan` / `observe` / `reflect`. Therefore any algorithm whose *structure is recursion* — tree search, hierarchical decomposition, conditional delegation, the `SPEC.md` §5.1 outer loop — has nowhere to live except inside the engine. That is "a new engine per algorithm", which `ADR-0070` exists to prevent, and it is `ADR-0070`'s own stated reversal condition.

**C2.** Under `agent.spawn`, delegation becomes a **mediated effect with a receipt**: verified at S8 against the descriptor digest, leased at S7, debited at S10, ledgered, attributed. **Authority strengthens.** The objection is not security — it is sequencing.

**C3. A forensic correction, verified this pass.** The `spawn()` docstring states at length that *"`StandardPolicy.authorize` … never checks that `request.action` is a member of `requested_scope.actions`"* and that closing the gap "needs its own ADR (`ADR-0054`)". **That is stale.** `kernel/policy.py` step 1b implements sealed membership under `ADR-0067`, and `kernel/attenuation.py:183` sets `sealed=request.sealed or request.actions < parent.actions` — so `attenuate()` auto-seals on every spawn that withholds verbs. The engine-side refusal is now defence in depth. **A stale comment inside the TCB's nearest neighbour is a real defect**, because a reviewer who trusts it mis-models the kernel. `RF-40` pins the behaviour so the correction is carried by a test rather than by prose.

#### Decision

**D1. The design is locked now; the code is not written now.** The verb specification, event shape, budget algebra, and falsifier suite below are normative from v0.6.1. **The kernel gains nothing but tests in Waves 1–4.** A `vanguard/packages/kernel/` diff before the M-4 gate **voids the M-4 evidence bundle**, because the nine-row run would no longer be attributable to the reviewed kernel.

**D2. Verb specification** (normative):

```text
verb      : agent.spawn
sink      : PRIVILEGED           # SinkRegistry.inferred_class → PRIVILEGED (requires bound grant)
selector  : {kind: generic, uriPattern: "agent://spawn/harness/<D_H>"}
args      : {harness_digest, brief, capabilities[], reservation, parent_lease}
receipt   : {request_digest, outcome, child_principal_id, child_episode_id, cost, lease_id, grant_digest}
```
**Delegation targets are resources.** A grant may permit spawning one harness digest and deny another. This is what converts "may this agent delegate?" into "may this agent delegate *to this composition*?" — and it is the property that makes heterogeneous swarms governable.

**D3. Budget algebra is reused unchanged** (`ADR-0074`): additive `{usd_micros, tokens, bytes, millis}` debit the parent's *remaining* vector, component-wise; structural `depth` increments with `child.depth = parent.depth + 1 ≤ root.max_depth`; **sibling depths are not summed**; `turns` is per-episode.

**D4. A planner may spawn only if its composition granted the verb.** No grant ⇒ `AuthorizationDenied`, alertable (`K-27`). The spawn capability is declared per-component in `mhf.manifest/2` (`ADR-0077` D1) and intersected fail-closed with the harness ceiling.

**D5. Singular Court (S-1) and Attenuated Reachability (S-2).** A swarm has **one** judge, exterior to every participant; delegation depth and heterogeneous composition do not multiply the evidence plane. Unreachability is **monotonic under delegation**: the evaluator endpoint MUST be expressed as a resource in the selector algebra so that reachability is attenuated rather than ambient. `[VERIFIED]` it is not today — `adapters/evaluators/client.py` is composition-wired, not selector-gated. Tracked as `RF-39`, landing with this ADR at M-6.

**D6. TCB budget: ≤ 40 logical LOC.** Headroom is `1438 − 1365 = 73`. Exceeding 40 is a design failure to be escalated, **not** grounds to raise the ceiling. `check_tcb_budget.py` remains the living gate until its `KERNEL.md` §1.1 replacement triple exists (§4, M-5).

**D7. `spawn` remains the *only* delegation primitive.** `ADR-0070` is not reopened: no `MetaAgent`, no `SwarmEngine`, no `Orchestrator` as a type. Swarm coordination stays a **policy over agents** and causal relations stay **projections of events**.

#### Falsifier sketches (written now, red until M-6)

| ID | Falsifier | Wrong implementation it kills |
|---|---|---|
| `RF-31` | `test_planner_without_spawn_grant_cannot_delegate` | Ambient delegation for any planner |
| `RF-32` | `test_child_grant_wider_than_parent_is_denied_whole` | Silent intersection instead of whole-request denial (`K-26`) |
| `RF-33` | `test_spawn_is_recorded_as_a_mediated_effect_with_a_receipt` | Delegation without `EffectStarted`/receipt/lease |
| `RF-34` | `test_sibling_depths_are_not_summed` | `Σ depth_child ≤ depth_parent` |
| `RF-35` | `test_spawn_selector_denies_undeclared_harness_digest` | Spawn as a blanket verb, ignoring the resource half (D2) |
| `RF-39` | `test_child_cannot_reach_evaluator_endpoint_without_selector_grant` | Ambient evaluator reachability (D5 / S-2) |
| `RF-40` | `test_sealed_child_scope_rejects_out_of_scope_action_at_S5` | The stale-docstring scenario in C3, with the engine-side refusal disabled |

#### Reversal condition

`RF-31`…`RF-35` demonstrably unimplementable within the TCB budget, **or** measured evidence that mediating every spawn through S0–S12 imposes a latency cost that makes deep delegation topologies impractical. Either finding reopens the engine-owned option — with data.

---

### 3.5 `ADR-0081` — Terminal absorption and deletion of `layer0/`; the NOVA-4 negative suite; two new plugin event kinds

**Path:** `docs/05_adr/0081-layer0-terminal-absorption-nova4-plugin-event-kinds.md`

---

#### Status
`accepted` — implements v0.6.2 / M-3 sprint 3.1. Contains a **Director-only escalation** (new event kinds, D3).

#### Narrows / extends
**Extends** `ADR-0069` (packages canonical) and `ADR-M0-13` (walking-skeleton rule). **Discharges** `SPEC.md` §1's behavioural-parity precondition for deleting duplicated surfaces. **Extends** `ADR-0074`'s writer-authority table and `ADR-0076` §6's event-coverage rule.

#### Context

`layer0/` now holds exactly `compose/compiler.py`, `registry/{broker,grants,isolation,lifecycle,sandbox,validator,worker}.py`, and `events/{emitter,envelope,store,taxonomy}.py` `[VERIFIED]`. The forensic defects that motivated the fork's quarantine — `scheduler/driver.py:138`'s fabricated unsigned `"pass"` and `spi/ceiling.py:21`'s fail-open empty-capability branch — died with the 2.2-B deletions.

`layer0/registry/` and `layer0/compose/` are the **only** plugin-lifecycle code in the tree, and they have **no packages twin and have never run on the canonical path** (`005` §W7). Wave 3 rests the entire framework claim on them. Wave 1 received 17 tasks and 15 falsifiers for the trust spine; Wave 3 as boarded receives 7 tasks for the product claim.

**A concrete instance of that risk, verified this pass:** `layer0/registry/lifecycle.py`'s `_EVENT` map (lines 33-39) covers five of seven states. `DISCOVERED` and `VERIFIED` map to nothing, and `_go()` guards with `if kind is not None:` — so those transitions **mutate state and emit silently**. `VERIFIED` is the state at which the capability-ceiling policy check occurs. **The M-3 exit gate ("every transition ledgered") is unsatisfiable against the current closed catalog.**

#### Decision

**D1. Absorb, prove, then delete — in that order.** `layer0/registry/` → `vanguard/packages/runtime/registry/`; `layer0/compose/compiler.py` → merged into `vanguard/packages/runtime/compose.py` as compose v2. `SPEC.md` §1's parity precondition is discharged by the NOVA-4 suite (D4) plus the `ADR-M0-13` echo-plugin walk, **not** by code review.

**D2. `layer0/events/` is NOT absorbed.** It is dead weight with live packages twins (`runtime/ledger_emitter.py`, `domain/ledger/events.py`, `adapters/stores/event_store.py`). It is deleted at 3.1-Z with no absorption step. Stated explicitly so no developer "absorbs" a fourth event taxonomy.

**D3. Two new event kinds — Director escalation, ruled here.** `PluginDiscovered` and `PluginVerified` are added to `EventKind` (schema-generated, `A-4`/`I-1`), to `EVENT_KINDS` (56 → 58), to `PRIVILEGED_KIND_OWNERS` as `frozenset({"registry"})`, and to `reducer.py` as fold rules over `LedgerState.plugins`. The `CataloguedKindsAreFoldedOrAllowlisted` property test extends accordingly. **Rationale:** without them, the FSM's two most security-relevant transitions are unledgered and the M-3 gate is a false green.

**D4. NOVA-4 is non-negotiable Wave-3 scope.** The six negatives named in `005` §W7 become first-class falsifiers, not implied behaviour. If Wave 3 will not fit, **breadth is shed — never falsifiers.** WASM tier, mandatory plugin signatures, and any second product plugin are already out of scope and stay out.

**D5. Deletion is atomic with its evidence.** `rm -rf layer0/` lands in the same commit as: deletion of `test/layer0/`, removal of the advisory CI step, and a green NOVA-4 run recorded in the commit message. A tree with `layer0/` deleted and NOVA-4 red is worse than the fork.

**D6. Freeze-at-compose is restated as a deletion precondition.** Unknown refs, unresolvable semver ranges, cyclic bindings, and empty ceilings MUST fail at **compose**, never at runtime (`ADR-0005`, `ADR-0072`). No code path may mutate a frozen composition (`ADR-0072` §3: no mid-run hot-swap).

#### The complete lifecycle FSM after this ADR

| From | To | Trigger | Ledger event | Writer | New? |
|---|---|---|---|---|---|
| — | `DISCOVERED` | scan path / entry point hit | **`PluginDiscovered`** | registry | ✅ **D3** |
| `DISCOVERED` | `RESOLVED` | deps + SPI version negotiated | `PluginResolved` | registry | |
| `DISCOVERED` | `FAULTED` | unresolvable ref | `PluginFaulted` | registry | |
| `RESOLVED` | `VERIFIED` | schema + signature + **ceiling policy** check | **`PluginVerified`** | registry | ✅ **D3** |
| `RESOLVED` | `FAULTED` | verification failure | `PluginFaulted` | registry | |
| `VERIFIED` | `ACTIVATED` | isolation broker starts the cell | `PluginActivated` | registry | |
| `VERIFIED` | `FAULTED` | cell start failure | `PluginFaulted` | registry | |
| `ACTIVATED` | `QUIESCING` | drain in-flight calls | `PluginQuiesced` | registry | |
| `ACTIVATED` | `FAULTED` | crash / rlimit kill / RPC timeout | `PluginFaulted` | registry | |
| `QUIESCING` | `RETIRED` | drain complete | `PluginRetired` | registry | |
| `QUIESCING` | `FAULTED` | drain timeout | `PluginFaulted` | registry | |
| `FAULTED` | `RETIRED` | backoff exhausted / substitute activated | `PluginRetired` | registry | |
| `RETIRED` | — | terminal | — | — | |

**Illegal by construction:** `RETIRED → *`; `FAULTED → ACTIVATED` (a faulted cell may not become active without re-traversing from `DISCOVERED`); any transition emitting no event.

#### Bound falsifiers — the NOVA-4 suite plus FSM completeness

| ID | Falsifier | Wrong implementation it kills |
|---|---|---|
| `RF-13` | `test_unknown_plugin_ref_fails_at_compose_not_runtime` | Late binding; runtime resolution (`ADR-0005`) |
| `RF-14` | `test_empty_component_ceiling_denies_everything` | `if not capabilities: return True` — the resurrected fail-open |
| `RF-15` | `test_only_registry_may_append_plugin_kinds` | Generic `append(any Event)` (`ADR-0074`) |
| `RF-16` | `test_faulted_cell_cannot_remain_active` | An FSM that leaves a crashed cell serving calls |
| `RF-17` | `test_in_process_requires_explicit_policy_grant` | `in_process` as a default (I-6) |
| `RF-18` | `test_no_code_path_mutates_a_frozen_composition` | Any hot-swap surface (`ADR-0072` §3) |
| `RF-19` | `test_every_fsm_transition_emits_a_ledgered_event` | **The verified `_EVENT.get() is None` silent-transition defect** |
| `RF-20` | `test_code_default_toolkits_load_through_the_lifecycle` | Direct imports bypassing discovery→freeze |
| `RF-17b` | `test_layer0_directory_does_not_exist` | A deletion that never happened |

#### Reversal condition

NOVA-4 red at the parity gate with a diagnosis that the absorbed semantics are irreparable — in which case `layer0/registry/` is deleted **without** absorption and the lifecycle is written fresh in `runtime/registry/`, at the cost of Wave 3 growing from "absorb + prove" to "write + prove". Recorded now so the fallback is a decision rather than an improvisation.

---

### 3.6 `ADR-0082` — The loop is mechanism; `K ≪ N` is proven, not asserted; and two scheduled reviews

**Path:** `docs/05_adr/0082-loop-as-mechanism-cold-resume-and-scheduled-reviews.md`

---

#### Status
`accepted` — v0.6.1 Substrate Correction Lock. D1 and D2 implement in M-2; D3 schedules M-5; D4 schedules M-9.

#### Narrows / extends
**Extends** `ADR-0070` (recursion as one primitive) by publishing its central claim with a bound falsifier. **Extends** `ADR-0071` / I-4 (cold replay) with the mid-turn resume case. **Extends** `ADR-M0-03` (five SPIs) with a scheduled review date rather than a change. **Extends** `ADR-M0-02` (identifier namespaces) with the `RF-*` namespace (§7.3).

#### Context

Four items reach this ADR because each is a **standing claim that has never been made refutable**, and an unfalsifiable claim is relitigated at full cost every quarter.

#### Decision

**D1. The Universal Turn Loop is published as Mechanism, with `RF-36` as its bound falsifier.**

> `observe → propose → authorize → effect → receipt → evaluate → (reflect)*` is **mechanism, never plugin**. Agentic algorithms differ in what they propose and when and to whom they delegate — never in whether an effect is authorized, a receipt recorded, or a verdict signed. Any algorithm expressible at all is expressible as **spawn topology + component-graph wiring + planner policy** over this one loop.
>
> **`RF-36` — The Standing Challenge.** *Name an agentic algorithm that cannot be expressed as spawn-topology + planner policy over this loop, and demonstrate it as a manifest that fails to compile or a behaviour that requires an engine diff.* Refuted ⇒ genuine `ADR-0070` reversal evidence. Unrefuted at **M-8 adjudication (one year from ratification)** ⇒ the loop is proven and the question is closed by evidence.

The **M-8 validation suite** is the structured half of the challenge: debate, critic/revisor, evolutionary search, and multi-agent economic delegation MUST run multi-pack with **zero engine modification**. A red there is a partial refutation and reopens `ADR-0070` on its own terms.

**Competing harnesses make the loop itself a plugin.** That is coherent for them precisely because they have no authority boundary to preserve. It is not coherent here, and this ADR says why once, in the ADR log, rather than repeatedly in review threads.

**D2. `K ≪ N` is proven by NOVA-2 (`RF-22`), which is a hard M-3 entry gate.**

`002` §5 asserts that many logical agents share a bounded worker pool. Nothing demonstrates logical-agent / worker separation: `EpisodeEngine` *is* the scheduler shell and `HarnessSession` holds live per-run state. The deciding question is precise:

> **Is an episode's continuation reconstructible from the ledger alone, or does resuming require the live Python object?**

`RF-22` (full specification in §2.7.2) suspends an episode mid-turn with a **SIGKILL** — not a graceful shutdown, which may flush state a crash would not — reconstructs cold in a fresh interpreter from the WAL, reconciles the undeterminable effect (`ADR-0026`), resumes, and completes with a trajectory satisfying `RF-12`.

**This is I-11's *precondition*, not its satisfaction.** Green permits M-7 to be scoped as a scheduling refactor and permits I-11 to be lifted on measurement alone. Red means M-3 must not build a component graph on a false assumption — which is exactly why the Tech Lead makes it a **gate** rather than a task.

**D3. Documentation collapse is scheduled at M-5 and forbidden before M-4 closes.** Target: `SPEC.md` (law) + `docs/05_adr/` (decisions) + **one** living board; a senior developer productive from three documents, not seven. GAMMA (`001`) and the `002` register retire as standing authorities once absorbed — falsifier tables migrate into `SPEC.md`'s invariant section and the board. Mid-flight documentation surgery during Waves 2–3 is strictly worse than the duplication.

**D4. The five-SPI freeze stands through M-8 and is reviewed at M-9 (`9.2-B`).** `ADR-M0-03`'s guard — *"a sixth SPI requires a design review, not a PR"* — is reaffirmed. What is refused is its hardening into *"there are five SPIs forever."* Two candidate sixth SPIs are named now so the review has subjects: **`IAggregator`** (may be dissolved by `mhf.manifest/2`'s multiplicity — see §2.9) and **`IScheduler`** (**provisionally refused**: the scheduler decides who acts when, which is Decision Plane, and making it pluggable moves authority above the extension line).

**D5. The `RF-*` namespace is opened.** `ADR-M0-02` declares exactly three namespaces (`I-*`, `ADR-*`, `S-M*`) and does not list `F-*` at all, while `F-01…F-25` exist with **different meanings** in `docs/04_annex/KERNEL.md` and in the `002` register `[VERIFIED]`. Because the kernel spelling is embedded in ~19 source and test files and the register spelling in docs plus `test/falsifiers/`, the **register** side renames: `F-*` remains the annex's kernel-control namespace; `RF-*` (Register Falsifier) becomes the register's, with the one-time alias table `RF-01 ≡ F-01 … RF-22 ≡ F-22` recorded in the register.

#### Bound falsifiers

| ID | Falsifier | Wrong implementation it kills |
|---|---|---|
| `RF-36` | The Standing Challenge (adjudicated at M-8 via the validation suite) | An unfalsifiable architectural claim |
| `RF-22` | `test_episode_suspends_cold_reconstructs_and_resumes_to_completion` | In-process coupling that makes M-7 a rewrite |
| `RF-41` | `test_falsifier_ids_are_unique_across_annex_and_register` (linter) | The verified `F-*` namespace collision recurring |

#### Reversal condition

**D1:** a successful `RF-36` demonstration. **D2:** `RF-22` red — which does not reverse the decision to test, it reverses the M-7 scoping assumption. **D3:** evidence that collapse loses a governance property the seven tiers were actually providing. **D4:** an M-9 review concluding a sixth SPI is required — which this ADR anticipates rather than forbids.

---

## §4 · Phased Milestone Roadmap & Version Ladder (v0.6.1 → v1.0.0)

### 4.1 The version ladder — ratified mapping

`SYSTEM_OVERVIEW` §6.2 correctly records that **no ADR on disk assigns version numbers to milestones** `[VERIFIED]`. This section is that assignment, ratified by the Leadership 7 and carried into `ADR-0082`'s companion changelog.

| Version | Name | Content | Cut when | Package version |
|---|---|---|---|---|
| **v0.6.0** | Concept Lock | `SPEC.md` + ADRs `0069`–`0076`. **Already locked** (`ADR-0075`) | — | `0.4.5b1` |
| **v0.6.1** | **Substrate Correction Lock** | ADRs `0077`–`0082` written · **NOVA-1 (`RF-12`) landed** · **NOVA-2 (`RF-22`) green** · NOVA-3 · Wave-3 rebalanced · `agent.spawn` design-locked · loop claim published | **M-2 gate green** | `0.4.5b1` |
| **v0.6.2** | **Extensibility Lock** | Registry FSM on packages with all 7 transitions ledgered · compose v2 · echo plugin walk · **`mhf.manifest/2` live** · **absent-vs-forged live** · NOVA-4 green · **`layer0/` deleted** | **M-3 gate green** | `0.4.5b1` |
| **v0.6.3** | **Evidence Bundle Lock** | The nine-row E2E green on one uninterrupted real run · NOVA-5 confirms non-zero cost on that run · cassette captured for per-PR CI · evidence bundle published | **M-4 gate green** | `0.4.5b1` |
| **v0.7.0** | **Foundation MVP — THE STOP LINE** | v0.6.3 evidence accepted by the Director. **Package version cuts from `0.4.5b1` here and nowhere earlier.** Docs collapse to the Clean Triad · Pack #2 proves I-7 as fact | **M-5 gate green** | **`0.7.0`** |
| **v0.8.0** | **Mediated Delegation** | `agent.spawn` as an S0–S12 verb · hierarchical decomposition and tree search as validation compositions · evaluator reachability selector-gated (`RF-39`) | **M-6 gate green** | `0.8.0` |
| **v0.9.0** | **Controlled Concurrency & Framework Builder** | Independence groups activated · `K ≪ N` demonstrated at scale · debate / critic / evolutionary / economic-delegation compositions run multi-pack with zero engine diff · `RF-36` adjudicated | **M-7 + M-8 gates green** | `0.9.0` |
| **v1.0.0** | **Meta-Cognitive Substrate** | Scaled orchestration measured (M-9) · outer-loop planner · manifest mutation · skill synthesis · unforgeable DPO harvest · McNemar-gated promotion frontier | **M-10 final gate green** | `1.0.0` |

> **Why v0.6.3 exists as its own version.** `SYSTEM_OVERVIEW` §6.2 proposed M-4 cutting straight to v0.7.0. The Leadership 7 separates them deliberately: **v0.6.3 is the run; v0.7.0 is the Director's acceptance of the run's evidence.** Collapsing them creates pressure to declare the stop line passed by merging code rather than by accepting evidence — which is precisely the failure mode `ADR-0075` and the M-4 stop line exist to prevent.

---

### 4.2 The milestone ladder, M-0 → M-10

```text
╔════════════════════ FOUNDATION PHASE — ends at a STOP LINE ════════════════════╗
║  M-0  Engineering truth                                    ✅ COMPLETE         ║
║  M-1  Trust spine                                          ✅ COMPLETE (GREEN) ║
║  M-2  One runtime + Substrate Correction      🔵 IN FLIGHT → v0.6.1            ║
║  M-3  Extensibility + Composition Algebra     ⚪ QUEUED    → v0.6.2            ║
║  M-4  Foundation E2E                          ⚪ QUEUED    → v0.6.3            ║
║                          ███ STOP LINE ███                                     ║
╚════════════════════════════════════════════════════════════════════════════════╝
                                     ║  ◄── nothing below starts before the gate above
╔══════════ GENERALITY & META-COGNITION PHASE — outcomes and gates only ═════════╗
║  M-5  Generality Proof & Consolidation                     → v0.7.0            ║
║  M-6  Mediated Delegation (agent.spawn)                    → v0.8.0            ║
║  M-7  Controlled Concurrency                               ┐                   ║
║  M-8  Framework Builder Abstraction                        ┘→ v0.9.0           ║
║  M-9  Scaled High-Performance Orchestration                ┐                   ║
║  M-10 Meta-Cognitive Substrate (FINAL)                     ┘→ v1.0.0           ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

---

#### M-0 · Engineering truth — ✅ COMPLETE

**Outcome.** Living CI measures `vanguard/packages/` and the named falsifiers, not a self-signing fork.
**Exit gate (met).** Production suites wired; `F-01…F-21` registered as tests (red permitted — red is honest); `generate_types.py --check` a hard gate; duplication detector present; `F-18`…`F-21` added by `ADR-0075`.
**Evidence `[VERIFIED]`.** 11 packages test steps + cold `replay-parity` + 9 linters wired; 15 linters on disk.

---

#### M-1 · Trust spine — ✅ COMPLETE (GREEN)

**Outcome.** False gates can no longer certify the trust spine.
**Exit gate (met).** `F-01…F-15` green on the canonical path; suites of record green; TCB ≤ 1438.
**Landed.** Signed request-bound verdicts · fail-closed ceilings · complete `D_H` · envelope lineage · typed budget algebra · **cold replay from disk in a fresh process**.
**Adjudication carried forward.** `F-08` is a **stale falsifier, not a production defect** — it dispatched a fully authorized `fs.write` and asserted the grant path must fail on its own happy path. The register must say so in its own table (§7.2), not only on the sprint board.

---

#### M-2 · One runtime + Substrate Correction → **v0.6.1**

**Entry.** M-1 green.
**Outcome.** One runtime authority; **and the corpus becomes learnable before any episode is run in anger.**

**Scope — carried (already boarded):**

| ID | Task | State |
|---|---|---|
| 2.1-A…E | jsonrpc → `domain/wire/` · codegen target · SPI Protocols → `ports/spi.py` · ceiling delegates to domain algebra · duplication detector | DONE |
| 2.2-A/B/C | Parity triage · KILL-surface deletion · `root.py` split in place | DONE |
| 2.2-D | Widen I-7 domain-blindness linter & boundary rows | READY |

**Scope — added by this document:**

| ID | Task | Authorised by | Falsifier |
|---|---|---|---|
| **NOVA-1** | Un-hollow the trajectory: per-turn cost, latency, model fingerprint, `D_R`, verdict-or-explicit-null | `ADR-0078` | `RF-12`, `RF-37` |
| **NOVA-2** | Cold suspend/resume falsifier (SIGKILL mid-turn → fresh-process fold → resume → complete) | `ADR-0082` §D2 | `RF-22` |
| **NOVA-3** | `_PROC_PATTERN` read from the compiled ceiling, not restated in `adapters/models/planner.py` | board carry-over | `RF-21b` |
| **2.6-A** | Write ADRs `0077`–`0082` to `docs/05_adr/`; update `INDEX.md` | this document | — |
| **2.6-B** | Open the `RF-*` namespace; add the alias table to the `002` register; land `RF-41` uniqueness linter | `ADR-0082` §D5 | `RF-41` |
| **2.6-C** | Correct the stale `spawn()` docstring in `engine.py` (`ADR-0080` §C3); land `RF-40` | `ADR-0080` | `RF-40` |

**Exit gate (all must hold):**
1. `F-16` / duplication detector green with `--enforce`; **zero** `layer0` imports under `vanguard/`.
2. Reducer folds complete — `EffectFailed`, `EffectRejected`, `BudgetExhausted`, `CapabilityAttenuated`, `TurnStarted`, `Plugin*`×5 — and the `CataloguedKindsAreFoldedOrAllowlisted` property test green with **zero silent `unknown_events`**.
3. **`RF-12` green** — a completed episode emits a populated trajectory (all 8 content assertions).
4. **`RF-22` green** — cold suspend/resume completes. *(If red: M-3 does not open; scope M-7 as a rewrite and re-plan §4's M-7 row before proceeding.)*
5. `RF-40`, `RF-41` green. ADRs `0077`–`0082` on disk with Director signature.
6. TCB ≤ 1438 with **zero kernel diff** beyond tests.

**Out of scope, explicitly:** any kernel diff; any plugin lifecycle work; `mhf.manifest/2` *implementation* (design only); any `layer0/` deletion beyond 2.2-B's authorised scope.

---

#### M-3 · Extensibility + Composition Algebra → **v0.6.2**

**Entry.** M-2 gate green — **including `RF-22`**.
**Outcome.** The framework claim becomes testable: new capability enters through manifests, plugins, and policy, and the composition surface can name more than one cognitive component.

> ⚠ **This is where the product claim lives or dies.** Wave 1 received 17 tasks and 15 falsifiers for the trust spine. Wave 3 as originally boarded received 7 tasks for the entire framework claim, built on code that has never run on the canonical path. **Rebalanced below to 5 sprints and 20 falsifiers.**

| Sprint | Content | Falsifiers | Authorised by |
|---|---|---|---|
| **3.1** | Registry FSM → `runtime/registry/` with **all 7 transitions ledgered** (incl. new `PluginDiscovered`/`PluginVerified`) · compose v2 · echo plugin walk + fault injection · isolation broker rlimits | `RF-13`…`RF-19` | `ADR-0081` |
| **3.2** | `code-default` toolkits through the real lifecycle · coding-token sweep (I-7 on the widened surface) · **one manifest parser** *(was `3.2-C`/`DEV-LOCAL`, now `DIRECTOR` and the T-1 vehicle)* | `RF-20`, `RF-21` | `ADR-0077` §D6 |
| **3.3** | **`mhf.manifest/2`** — named component graph · `D_H` over the graph and bindings · `code-default` mechanical migration · six reference topologies compile | `RF-23`…`RF-27` | `ADR-0077` |
| **3.4** | **Absent-vs-forged** — `evaluation: none`, optional sandbox tier, optional approval policy · derived `unattributable_for_promotion` · trajectory `guardrails` object | `RF-28`…`RF-30b` | `ADR-0079` |
| **3.5** | **`agent.spawn` design only** — design note, verb spec, falsifier sketches. **Zero kernel diff.** | `RF-31`…`RF-35` (authored red, unrun) | `ADR-0080` |
| **3.1-Z** | `rm -rf layer0/` · delete `test/layer0/` · remove advisory CI step — **atomic with a green NOVA-4** | `RF-17b` | `ADR-0081` §D5 |

**Exit gate (all must hold):**
1. Echo plugin walks `DISCOVERED → RESOLVED → VERIFIED → ACTIVATED → QUIESCING → RETIRED` over UDS with **every one of the seven transitions ledgered** (`RF-19`).
2. `code-default` loads through the **same** lifecycle — no direct imports (`RF-20`).
3. NOVA-4 six negatives green (`RF-13`…`RF-18`).
4. Six reference topologies compile to six distinct `D_H` (`RF-24`); binding-edge change moves `D_H` (`RF-25`).
5. `evaluation: none` compiles, changes `D_H`, and an unsigned verdict is **still** rejected (`RF-28`, `RF-29`); attributability is derived, not writable (`RF-30`).
6. I-7 green on the widened surface; exactly one manifest parser (`RF-21`).
7. `layer0/` **does not exist** (`RF-17b`); TCB ≤ 1438 with zero kernel diff.

**Out of scope, explicitly:** WASM tier · mandatory plugin signatures · any second product plugin beyond echo · model/sandbox behind the wire (`P1-11`/`P1-12` deferred) · **any `agent.spawn` implementation**.

---

#### M-4 · Foundation E2E → **v0.6.3** · ███ THE STOP LINE ███

**Entry.** M-1 + M-2 + M-3 all green.
**Outcome.** One real coding-agent run through the complete substrate with trustworthy state and evidence.

**The nine rows — all true on ONE uninterrupted run, zero human intervention:**

| # | Row | Falsified by |
|---|---|---|
| 1 | **Real model** — not a stub planner | a cassette-only path |
| 2 | **Authorized effect** — kernel grant + lease, not `ADVISORY`-only | `RF-08` |
| 3 | **Filesystem change** — durable, receipted | an in-memory workspace |
| 4 | **Sandbox** — untrusted exec contained (UID 10001, rootless bwrap) | host execution |
| 5 | **Exterior signed eval** — no unsigned pass (UID 10002, Ed25519, nonce-bound) | `RF-03`, `RF-04` |
| 6 | **WAL ledger** — the packages store, not `MemoryLedger` | `RF-05` |
| 7 | **Cold replay** — reconstruct from disk in a fresh process | `RF-02` |
| 8 | **Schema-valid AND POPULATED trajectory** | **`RF-12` / NOVA-5** |
| 9 | **One runtime authority** — no competing scheduler or kernel | `RF-16`, `RF-17b` |

**Row 8 is strengthened by this document.** The original nine-row gate says "schema-valid `mhf.trajectory/1`". As `ADR-0078` establishes, a content-free record satisfies that. **Row 8 now reads "schema-valid and populated", and NOVA-5 is its confirmation on the real run.**

**Sprint 4.1:** fixture repo + preregistered oracle (`4.1-A`) · nine-row integration test (`4.1-B`) · cassette of the green run for per-PR CI (`4.1-C`) · evidence bundle report — ledger digest, `D_H`/`D_R`, trajectory, containment boolean (`4.1-D`) · **NOVA-5** (`4.1-E`).

> **Director standing order.** *Escalate to the Director any temptation to widen scope in order to make the run pass.* A widened gate is not a passed gate. `agent.spawn`, concurrency, Pack #2, and all of M-5…M-10 stay out of implementation scope until the nine rows are green.

---

#### M-5 · Generality Proof & Consolidation → **v0.7.0**

**Entry.** M-4 evidence bundle **accepted by the Director** (not merely produced).
**Outcome.** Domain-blindness stops being a thesis and becomes a demonstrated fact; the governance corpus collapses to the Clean Triad.

**5.1 — Documentation collapse to the Clean Triad** (`ADR-0082` §D3). Collapse to `SPEC.md` + `docs/05_adr/` + one living board. Retire GAMMA (`001`) and the `002` register as standing authorities once absorbed. Target: a senior developer productive from **three** documents.

**5.2 — Pack #2: Math & Formal Deductive Verification** *(the generality gate; specified in §4.3)*.

**5.3 — Measurement and metric work.**
- Selector-soundness measurement for independence groups; `RF-22` re-run at scale with multiple concurrent episodes.
- Name and register the I-11 measurement gate (documented decision; **concurrency still not enabled**).
- Build the `KERNEL.md` §1.1 **TCB metric replacement triple** — mutation score on kernel + reducers, % of controls with production call-site proofs, event-kind emission coverage — resolving the Principal Systems Architect's standing dissent (§1.1). The LOC gate remains living until the triple exists.
- **External benchmark run** of compiled `code-default` with cost/latency telemetry (`RESEARCH_k3` G8) — for **composition falsification**, not leaderboard position. *(This is the CTO's overruled M-4 request, rescheduled to its correct home: after the pack loads through its own lifecycle.)*

**Exit gate:**
1. **Zero diffs under `vanguard/packages/domain/` and `vanguard/packages/kernel/`** for Pack #2 — I-7 becomes fact (`RF-42`).
2. **Trajectory parity** — Pack #2 emits `mhf.trajectory/1` rows satisfying `RF-12` identically to Pack #1 (`RF-43`). *(Without this, "domain-blind" could mean "domain-blind but only Pack #1 is learnable".)*
3. `RF-22` green at scale (≥ 8 concurrent logical episodes over a bounded pool).
4. Reading path is three documents; `002` and GAMMA carry a retirement banner.
5. Package version cut to `0.7.0`.

---

#### M-6 · Mediated Delegation (`agent.spawn`) → **v0.8.0**

**Entry.** M-5 green **and** `ADR-0080`'s implementation decision signed by the Director.
**Outcome.** Delegation becomes a mediated effect; recursive algorithms gain a legal home outside the engine.

**Scope.** Implement `agent.spawn` in S0–S12 (`ADR-0080` §D2) · per-component spawn grant in `mhf.manifest/2` · reuse existing attenuation and budget algebra unchanged · selector-gate the evaluator endpoint (`RF-39`, closing S-2) · two validation compositions: **hierarchical decomposition** (recursive planner) and **tree search** (expansion / scoring / selection as three separate components in the graph).

**Exit gate:** `RF-31`…`RF-35` green · `RF-39`, `RF-40` green · both validation compositions run **with zero engine diff** · **TCB ≤ 1438 with the verb costing ≤ 40 logical LOC**.

---

#### M-7 · Controlled Concurrency → contributes to **v0.9.0**

**Entry.** M-5's I-11 measurement gate named and met; M-6 green.
**Outcome.** Independence groups activated for non-intersecting selectors; `K ≪ N` logical-to-worker separation real.

**Scope.** Activate independence groups (proposals already declare read/write selectors — `Proposal.independence_groups` exists in the SPI) · backpressure, cooperative cancellation, resource accounting · async/event-driven scheduler prototype · **mid-lease `CapabilityRevoked`** — the emitter and fold path that `RF-38` pins (§1.2.3).

**Exit gate:** selector-disjointness measurement published · **zero event loss under backpressure** · `RF-22` green at production scale · `RF-38` green · **stigmergic property measured**: messages-per-turn remains `Θ(N)` as `N` scales, refuting the `O(N²)` broadcast pattern (`RF-44`) · I-11 formally lifted by ADR.

---

#### M-8 · Framework Builder Abstraction → contributes to **v0.9.0**

**Entry.** M-6 + M-7 green.
**Outcome.** Arbitrary agentic topologies are composed **declaratively** over the component graph, with no engine modification.

**Four validation compositions, each a manifest and nothing else:**

| Composition | Component graph shape |
|---|---|
| **Debate** | N `planner`-kind proposers + 1 aggregator + shared `evaluation`, bound `reviewed_by` |
| **Critic / revisor** | 2 `planner`-kind (proposer, critic) + 2 `evaluation`-kind (inline cheap, terminal exterior) |
| **Evolutionary search** | population operator component + fitness binding to `evaluation` + `agent.spawn` per candidate |
| **Multi-agent economic delegation** | heterogeneous child harnesses (different `D_H`) + Vickrey allocator as planner policy (`SPEC.md` §6.2) |

**Scope also includes:** SDK/CLI for declarative composition · dry-run compose with ceiling preview · developer guide *"how to build a new agent"* · three packs running side by side (coding, math, one more).

**Exit gate:** all four compositions run **multi-pack with zero diffs under `kernel/`, `agency/episode/engine.py`** (`RF-45`) · **`RF-36` (the Standing Challenge) adjudicated** — refuted or declared survived · single runtime confirmed across three packs.

---

#### M-9 · Scaled High-Performance Orchestration → contributes to **v1.0.0**

**Entry.** M-7 + M-8 green.
**Outcome.** Many logical agents over a bounded worker pool, with the overhead measured rather than asserted.

**Scope.** Load test `K ≪ N` · measure IPC, serialization, plugin-call overhead · measure ledger pressure and isolation cost at scale · targeted optimisation **only where 9.1's measurement names a real bottleneck** · **the five-SPI freeze review** (`9.2-B`, `ADR-0082` §D4) against the now-mature component graph.

**Exit gate:** published measurements against declared latency and resource budgets · bounded ledger pressure demonstrated at `N` logical agents · a written ruling on the sixth SPI (`IAggregator` — needed, or dissolved by the graph?).

---

#### M-10 · Meta-Cognitive Substrate (FINAL) → **v1.0.0**

**Entry.** M-8 + M-9 green.
**Outcome.** The system proposes, verifies, and promotes an improved version of its own composition — with the whole chain attributable via `D_H`/`D_R`/`D_X` and signed verdicts, on a corpus whose evidence was never forgeable.

| Sprint | Content |
|---|---|
| 10.1 | Harden production data exhaust: cost/turn, fingerprint, verdict present in **every** pack; `attribution.prefix_hits` becomes required (`ADR-0078` §D4) |
| 10.2 | Outer loop as a **second registered `IPlanner`** at graph slot `outer`, invoked at `reflect()`; capability-restricted to manifest-mutation proposals, skill writes, oracle preregistration — **never the workspace** |
| 10.3 | Evolutionary mutation operators over JCS-diffable manifest fields; paired runs against the **undeletable** baseline as the selection function; signed promotion event flips the registry default pointer |
| 10.4 | Skill harvester: verdict-conditional high-lift effect n-grams → candidate skill cards, entering the manifest **only** through 10.3's selection pipeline |
| 10.5 | DPO harvest: `(chosen, rejected)` pairs keyed on `(task_digest, harness_digest, turn-prefix context_digest)`; anti-cheat filter + verdict signature validity; fine-tune tier-1/2; cassette-replay regression |
| 10.6 | Continuous loop: telemetry → harvest → fine-tune → regression → promotion, as a permanent process; **calibrated active-inference gate** using verdict history per harness digest |
| 10.7 | **Final validation:** the system proposes, tests, and promotes an improved version of its own composition, attributable end to end |

**FINAL GATE.** A promotion occurs in which: the mutation was proposed by the outer loop; the comparison was **paired** against the undeletable baseline; the decision used **McNemar's exact test** on discordant pairs with a reported effect size and confidence interval (`MEASUREMENT.md` `M-02`…`M-04`); every verdict in the evidence chain is exterior-signed and request-bound; `D_H` ≠ `D_R` ≠ `D_X` held throughout; and **a human promoted the pointer** (`SPEC.md` §9 — no self-updating release pipeline; `ADR-0019` stands).

---

### 4.3 Pack #2 — Math & Formal Deductive Verification (the M-5 generality gate)

**Ruling: Pack #2 is Math & Formal Deductive Verification. It is a gate, not an aspiration.**

#### 4.3.1 Why this domain and not the alternatives

| Candidate | Verdict |
|---|---|
| **Math / formal deductive verification** | ✅ **Selected.** Maximally distant from coding along every axis that matters: no filesystem mutation, no subprocess as the primary effect, a **decidable** oracle, a different selector vocabulary, and a genuine exercise of `ADR-0079` (a pure-deduction composition may legitimately declare `sandbox: none`). |
| TableWorld (`adapters/environment/tableworld.py`, orphaned, D-27) | ⚠ **Demoted to Pack #3.** It exists and is cheap, which is exactly why it is a weak generality test — it was written *inside* this repo's assumptions. |
| Data analysis | ⚠ Pack #4. Too close to coding: filesystem + subprocess + test-runner-shaped oracle. It would pass I-7 without stressing it. |

#### 4.3.2 The pack contents (a Domain Pack = toolkits + oracle suite + manifest defaults + selector vocabulary)

```text
packs/math-formal/
├── manifest.yaml                     # mhf.manifest/2 — the FIRST pack written natively in /2
│                                     # declares: sandbox: none for pure-deduction components
│                                     #           evaluation: <proof-checker oracle>  (NOT absent)
├── system-prompt.txt
├── components/
│   ├── planner.proof-search          # kind: planner   — tactic selection; at M-6 becomes recursive via agent.spawn
│   ├── context.lemma-map             # kind: context   — dependency-ranked lemma neighbourhood (structural, not semantic)
│   ├── memory.lemma-kv               # kind: memory    — proven-lemma cache keyed by statement digest
│   └── evaluation.proof-check        # kind: evaluation— requests exterior judgment; never renders it
├── toolkits/
│   ├── proof_assistant.py            # verb: proof.step   selector {kind: generic, uriPattern: "proof://tactic/<name>"}
│   ├── lemma_search.py               # verb: lemma.search selector {kind: generic, uriPattern: "lemma://index/<ns>"}
│   └── smt_query.py                  # verb: smt.query    selector {kind: generic, uriPattern: "smt://solver/z3"}
└── oracles/
    ├── registry.json                 # preregistered: proof-checker@1  (decidable, deterministic)
    └── gate.py
```

#### 4.3.3 Why this is the strongest available I-7 test

1. **A new selector vocabulary.** `proof://`, `lemma://`, `smt://` — none of which resembles `fs://` or `proc://`. If the selector algebra needs a `domain/` diff to express them, I-7 is **refuted** and we learn it from a pack rather than from a customer.
2. **A decidable oracle.** A proof either checks or it does not. Unlike a test suite, there is no flakiness, no environment sensitivity, and no partial credit — which makes it the cleanest possible signal for the M-10 learning loop and the ideal first corpus for `RF-43` trajectory parity.
3. **It exercises `ADR-0079` non-trivially.** A pure-deduction component has no external footprint and may legitimately declare `sandbox: none`; an SMT-solver subprocess may not. **Per-component guardrail declaration (D7) gets its first real test**, in the same milestone that first needs it.
4. **It is a natural `agent.spawn` consumer at M-6.** Proof search *is* tree search. Pack #2 written at M-5 becomes M-6's validation composition at zero additional cost — the same dual-use `ADR-0077` gives us for ASTRA-style trajectory synthesis (§1.2.4).

#### 4.3.4 The gate

| # | Assertion | Falsifier |
|---|---|---|
| 1 | `git diff --stat` under `vanguard/packages/domain/` and `vanguard/packages/kernel/` is **empty** for the entire Pack #2 delivery | `RF-42` |
| 2 | Pack #2 emits `mhf.trajectory/1` rows satisfying **every** `RF-12` content assertion | `RF-43` |
| 3 | `check_domain_blindness.py` green — no `coding\|pytest\|ast` tokens introduced, and no `proof\|lemma\|smt` tokens either | existing `F-18`/`RF-18a` |
| 4 | The pack compiles under `mhf.manifest/2` with **no `/1` compatibility shim** | `RF-24` extension |

> **If assertion 1 fails, I-7 is refuted and M-5 does not close.** That is the entire point of making Pack #2 a gate. A generality claim that has never had the opportunity to fail is not evidence.

---

## §5 · Theories, Algorithms & Mathematical Formalisation

> **Scope discipline.** Everything in this section is **deferred to M-10** as *implementation*, and **locked now** as *data contract*. The reason is stated once: the corpus must be rich before anything consumes it, and the shape of the consumer determines which fields must exist. `ADR-0078` exists because of §5.1–§5.4, not the other way round.
>
> **Placement discipline.** Every algorithm below lives in an **exterior, domain-blind plugin** (`ADR-M0-06`, D-40): `tools/telemetry/` and the harvester are siblings to the kernel tree and are **never imported by it**. None of this is core.
>
> **Metaphysics discipline.** `ADR-M0-10` / `REJ-10` forbid biological, cosmological, or tier-of-being framing in any document under `docs/`. The formalism below is stated as mathematics with named variables. *"Free energy"* here is the variational bound of Bayesian inference and nothing else.

### 5.0 Notation

| Symbol | Meaning | Where it lives on disk |
|---|---|---|
| `τ` | An episode trajectory | `mhf.trajectory/1` |
| `T` | Horizon (turn count) | `len(traj.turns)` |
| `s_t` | Context state at turn `t` | `turns[t].context_digest` |
| `a_t` | Executed action (verb + selector) | `turns[t].proposal.requests[]` |
| `r_t` | Emitted kernel receipt | `turns[t].receipts[]` |
| `Y(τ) ∈ {0,1}` | Terminal outcome | `traj.verdict.pass`, exterior-signed |
| **R** | The 6-dimensional economic tensor | `Reservation` |
| `θ ∈ Θ` | Harness manifest parameters (the genome) | JCS-diffable fields of `mhf.manifest/2` |
| `D_H, D_R, D_X` | Composition / execution / experiment identity | `harness_digest`, `execution_digest`, lab-owned |

**The 6D economic tensor, with its type split (`ADR-0074` §2) — this split is load-bearing everywhere below:**

```text
R = ( usd_micros , tokens , bytes , millis | depth , turns )
    └──────────── additive conserved ─────┘ └─ structural ceilings ─┘
        child ≼ remaining(parent), component-wise      depth: child = parent+1 ≤ root.max_depth
        Σ over siblings is MEANINGFUL                  SIBLING DEPTHS ARE NOT SUMMED
```

A `CostVector` is the **projection of R onto its additive subspace**. `schemas/mhf/trajectory.schema.json#/$defs/CostVector` already enforces exactly this with `additionalProperties: false` over `{usd_micros, tokens, bytes, millis}` — the mathematics is already in the schema, and `ADR-0078` merely makes the values real.

---

### 5.1 Trajectory error credit assignment and backward fault isolation

#### 5.1.1 The counterfactual formulation

For a failed episode (`Y(τ) = 0`), the **Counterfactual Causal Contribution** of turn `t` is:

```
                                                                  Tokens(a_t)
  C(a_t)  =  Δ E_oracle [ Y(τ) | do(a_t := a_null) ]  +  λ_cost · ─────────────
                                                                  Σ_k Tokens(a_k)
```

The first term is a *do*-intervention: what the exterior oracle would have returned had turn `t` been a no-op. The second is a cost-share regulariser that prevents attributing failure to cheap turns merely because they are numerous.

**Why this is not directly computable, and what we do instead.** Evaluating the *do*-term requires re-running the episode `T` times with one turn ablated each — `O(T)` full episodes per failed episode, at production model cost. This is precisely the *"exponential token explosion"* failure mode the literature attributes to LATS-style MCTS-with-LLM-value-heuristic. **We refuse the naive estimator** and adopt a gradient-free structural surrogate.

#### 5.1.2 The Backward Fault Isolation algorithm (the surrogate we implement)

```text
ALGORITHM  BackwardFaultIsolation(τ)
INPUT      τ : mhf.trajectory/1 satisfying RF-12   (populated — this is why NOVA-1 is a precondition)
OUTPUT     (t*, mode, W)  : causal turn index, failure mode, per-turn weight vector

 1  ASSERT  τ.verdict is not None  AND  τ.verdict.pass == False
            ∧ τ.verdict.signature verifies against the exterior public key
            ∧ τ.guardrails.evaluation != "absent"        # ADR-0079: absent ⇒ non-attributable
 2  FOR t = T DOWNTO 0:                                   # BACKWARD scan — first violation is the last cause
 3      IF  ∃ r ∈ τ.turns[t].receipts : r.outcome ∈ {"failed","rejected"}
            OR  ∃ e ∈ events(t) : e.kind ∈ {"AuthorizationDenied","BudgetExhausted","EffectRejected"}
            OR  exit_code(τ.turns[t]) != 0:
 4          t* := t ;  BREAK
 5  mode := Classify(τ, t*)                               # §5.1.3 taxonomy — deterministic, no model call
 6  IF mode ∈ {SYNTAX, SEMANTIC}:                          # attribute to the most recent mutation
 7      t* := max { t ≤ t* : ∃ a ∈ τ.turns[t].proposal.requests, a.verb ∈ MUTATING_VERBS }
 8  FOR t = 0..T:  W[t] := γ^(t* − t) · 1[t ≤ t*]          # γ ∈ (0,1), discount BACKWARD from the fault
 9  RETURN (t*, mode, normalise(W))
```

**Complexity: `O(T)` with zero additional model calls.** The whole estimator is a scan over ledgered events, which is why it is affordable at production volume and why it cannot exist before `RF-12`.

**Why backward and not forward.** The earliest turn at which an invariant was violated is the *last* turn at which the trajectory was still repairable. Scanning forward finds the first *symptom*; scanning backward from the terminal finds the first *cause*. `MUTATING_VERBS` is **pack data**, never core — for Pack #1 it is `{patch.apply, fs.write}`; for Pack #2 it is `{proof.step}`. The algorithm is domain-blind; the verb set is not.

#### 5.1.3 The deterministic failure taxonomy

Classification is a **pure function of ledgered events** — never a model call, and never natural-language self-verbalisation. This is the `Reflexion`-family failure mode (*"hallucinatory loop recursion; ungrounded self-evaluation"*) refused by construction.

| Mode | Ledger signature | Manifest mutation it licenses (§5.2) |
|---|---|---|
| `CONTEXT_WINDOW_OVERFLOW` | compaction pressure ≥ 1.0, or provider context error | `tokens ← min(⌈tokens·1.5⌉, R_max.tokens)` |
| `TOOL_SCHEMA_VIOLATION` | `EffectRejected` with a schema-validation reason | tool-schema phrasing variant; translator alias |
| `AUTHORIZATION_DENIED` | `AuthorizationDenied`, `alertable=True` | **none — never widen a ceiling automatically.** Escalate to a human |
| `TEST_ASSERTION_FAILURE` / `PROOF_CHECK_FAILURE` | signed `verdict.pass == false` from the preregistered oracle | `repair_rounds += 2`; planner → tree-search variant |
| `INFINITE_LOOP_TIMEOUT` | lease `millis` exhausted with no terminal receipt | lower per-effect `millis`; enable early-classification |
| `BUDGET_EXHAUSTION` | `BudgetExhausted` | `tier ← min(tier+1, tier_max)` **iff** budget headroom permits |
| `UNKNOWN_ANOMALY` | none of the above | **no mutation.** Emit a `KernelAlarm`-class telemetry record |

> **CIO standing rule, normative:** `AUTHORIZATION_DENIED` MUST NEVER license an automatic mutation. A system that widens its own ceiling in response to being denied has inverted the reference monitor. This row is the single most important line in §5.

---

### 5.2 Active inference: variational free energy minimisation over the manifest genome

#### 5.2.1 The objective

Meta-cognitive tuning is the search for a manifest genome `θ ∈ Θ` minimising **Variational Free Energy** `F(θ)` subject to the economic tensor:

```
  θ*  =  argmin_{θ ∈ Θ}  F(θ)        subject to     Cost(θ) ≼ R_max     (component-wise, additive dims)
```

`F(θ)` decomposes into an epistemic term and a pragmatic term, plus an explicit economic penalty:

```
                ┌──────────────────────────┐   ┌────────────────────────────────┐        R_d(θ)
  F(θ)  =  D_KL[ q(φ | τ)  ‖  p(φ) ]        −   E_{q(φ|τ)}[ ln p(Y = 1 | τ, θ) ]  +  λ · Σ  ────────
                └──── epistemic ───────────┘   └──────── pragmatic ─────────────┘  d∈A   R_max,d
```

where `φ` are latent competence parameters, `q(φ | τ)` the posterior induced by observed trajectories, `p(φ)` the prior from `CompetencePriorRecorded` history, and `A = {usd_micros, tokens, bytes, millis}` the **additive** dimensions only. Structural ceilings `{depth, turns}` appear as **hard constraints in `Θ`**, never as penalty terms — summing a depth would violate `ADR-0074`'s type split.

#### 5.2.2 Why VFE and not EFE, and why this is now tractable

Expected Free Energy in its canonical form requires expectations over full trajectory distributions and integrals that are intractable in the discrete-but-large action space of a coding or proof agent. The 2026 result we adopt is that **recasting EFE minimisation as variational free energy minimisation with epistemic priors renders the policy search tractable**, and that factor-graph message passing over the resulting structure **scales linearly in the number of factors**.

AETHER's structure is already a factor graph:

```text
  factors  =  { (D_H, task_digest, turn-prefix context_digest) → signed verdict }
  edges    =  the component-graph bindings of mhf.manifest/2      ← ADR-0077 makes these explicit
  messages =  per-turn cost/latency/fingerprint vectors           ← ADR-0078 makes these non-zero
```

**Neither factor is computable today.** The edges do not exist until `mhf.manifest/2` lands; the messages are `_ZERO_COST` until NOVA-1 lands. This is the mathematical statement of why `ADR-0077` and `ADR-0078` are the two prerequisites of the entire M-10 arc.

#### 5.2.3 The calibrated gate — the operational form (`SPEC.md` §5.3)

The full formalism is **not** imported into the runtime. The planner maintains a calibrated posterior and scores actions on one scalar:

```
  score(a | c)  =  E[ verdict_gain | a, c ]  −  λ · ‖ Reservation(a) ‖_R

               =  P(pass | a, c) · value(pass)  −  λ · Σ_{d∈A}  R_d(a) / R_max,d
```

- `P(pass | a, c)` is calibrated from the ledger's `CompetencePriorRecorded` / `VerdictRecorded` history, **per `D_H`**. The prior recorder already exists.
- **Escalation, retry, and abandonment become threshold policies on this one scalar** — unifying `tier_escalation.py`, repair rounds, and abandonment under a single calibrated rule instead of three independent heuristics.
- **Miscalibration becomes measurable:** Brier score per harness digest, emitted as telemetry.

```
  Brier(D_H)  =  (1/N) · Σ_{i=1..N} ( P̂_i(pass)  −  Y_i )²          Y_i from the SIGNED verdict only
```

> **This is the pivotal property.** Because `Y_i` comes from an exterior, request-bound, Ed25519-signed verdict that the agent cannot read, patch, or reason about, **the calibration signal is un-gameable by construction rather than by policy.** Every published automatic-harness-evolution loop in the 2026 literature calibrates against self-reported or benchmark-scored outcomes. This is the differentiated claim, and it is the CTO's §1.2.1 ruling in equation form.

#### 5.2.4 Mutation operators over the genome

`θ` ranges over **JCS-diffable** fields of `mhf.manifest/2`: system-prompt fragments, tool-schema phrasing, compaction strategy, escalation thresholds, repair-round bounds, model-route tiers, **and — new under `ADR-0077` — component-graph topology and binding edges.**

```text
M1  token growth       tokens ← min(⌈tokens · (1 + α)⌉, R_max.tokens),  α = 0.5      ← E_OOM
M2  strategy switch    planner_ref ← tree-search variant ;  repair_rounds += 2        ← E_oscillation
M3  tier escalation    tier ← min(tier + 1, tier_max)                                 ← E_complexity
M4  prompt fragment    substitute one L1 fragment from the preregistered variant set
M5  TOPOLOGY (new)     add / remove one component or one binding edge                 ← ADR-0077 D4
```

**M5 is the operator that only exists because of `ADR-0077`.** Without a component graph, mutation can only tune scalars inside a fixed shape. With it, the search space includes *the shape itself* — which is exactly what the 2026 automatic-harness-evolution results exploit. **Every mutation produces a new `D_H`. Nothing is ever mutated in place** (`ADR-0072` §3: no mid-run hot-swap; promotion flips a pointer).

---

### 5.3 Skill memory: hybrid retrieval and Elo-decayed eviction

A synthesised skill card is `S_i = ( v_i , Pattern_i , Procedure_i , E_i , t_created , t_last_used )` with `v_i ∈ R^384` a dense embedding (`all-MiniLM-L6-v2`) over the error signature and context prompt.

#### 5.3.1 Hybrid semantic-lexical retrieval

```
                            q · v_i
  Score(S_i, q, K_q)  =  α ─────────── ​ +  (1 − α) · BM25(K_q, Pattern_i)  +  β · σ(E_i)
                          ‖q‖ ‖v_i‖
                          └ semantic ┘     └────── lexical ──────┘          └ utility ┘

                    1
  σ(E_i)  =  ─────────────────            Elo-normalised utility weight
             1 + e^(−E_i / 400)
```

**Why hybrid and not pure vector.** The `Voyager`-family failure mode is *"semantic retrieval collision; procedural bloat and amnesia"*. The Aider-lesson counterpart, already recorded in `RESEARCH_k3` §6, is **structural retrieval before semantic** — and it is why `SPEC.md` §4.2 specifies a Merkle index plus tree-sitter tag extraction plus personalised-PageRank ranking as L4, with embeddings as an *optional sidecar declared as a memory capability*. `ContextBench`'s recall-over-precision warning is the same lesson from the evaluation side. **The `β · σ(E_i)` term is the anti-bloat control:** a card that has never earned a green verdict cannot outrank a structural match, no matter how similar its embedding.

#### 5.3.2 Elo dynamics and eviction

On retrieval and injection into an episode with exterior-signed outcome `Y`:

```
  Y = 1 (oracle green):   E_{t+1}(S_i) = E_t(S_i) + K · ( 1 − σ( E_t(S_i) − Ē ) )
  Y = 0 (oracle red):     E_{t+1}(S_i) = E_t(S_i) − K ·      σ( E_t(S_i) − Ē )
  idle decay:             E(t)         = E_0 · e^( −λ_decay · (t − t_last_used) )

  EVICT  iff   E_i < E_evict = 1000        (initial E_0 = 1200)
          or   (t − t_last_used) > 30 days
```

Eviction moves a card to cold storage; it is **never deleted**, because the corpus is append-only evidence and a card's history remains attributable.

> **Two hard constraints on this subsystem.**
> 1. **Elo updates key on the exterior-signed verdict only.** A card that self-reports success cannot raise its own Elo — that is the skill-card analogue of a forged verdict.
> 2. **Elo is a *retrieval-ranking* signal, never a *promotion* signal.** `SPEC.md` §9 refuses scalar reward for promotion; `ADR-0015` makes promotion a partial order over a frontier. A card enters a manifest **only** through the §5.4 paired-McNemar pipeline. Elo decides what gets *shown*; McNemar decides what gets *shipped*.

---

### 5.4 Unforgeable DPO harvesting and the paired McNemar promotion protocol

#### 5.4.1 The pairing key — and why turn-prefix granularity requires `RF-12`

Two trajectories form a preference pair iff they agree on all three components of the key and disagree on the signed verdict:

```
  key(τ, t)  =  ( task_digest ,  harness_digest (D_H) ,  context_digest(τ, t) )

  pair       =  ( τ⁺ , τ⁻ )  such that   key(τ⁺, t) = key(τ⁻, t)
                              ∧  τ⁺.verdict.pass = 1  ∧  τ⁻.verdict.pass = 0
                              ∧  both signatures verify against the exterior public key
                              ∧  neither is unattributable_for_promotion          (ADR-0079 D4)

  chosen     =  τ⁺.turns[t].proposal        rejected  =  τ⁻.turns[t].proposal
```

**The divergence point is turn `t` — the first turn at which `context_digest` differs.** This is *edge-level* credit assignment, which the 2026 graph-based-credit-assignment literature establishes as strictly better than trajectory-level attribution. `mhf.trajectory/1.turns[].context_digest` is already the right field; it is simply **useless without `RF-12`'s populated turns**, because a pair with no cost, no fingerprint, and no latency cannot be filtered, weighted, or cost-normalised.

#### 5.4.2 Why the signal is un-gameable — the four structural properties

| # | Property | Mechanism |
|---|---|---|
| 1 | The agent cannot forge the label | Verdicts are exterior (UID 10002), Ed25519-signed, nonce-and-subject-bound; `runtime/evaluator_gateway.py` is the sole legal writer of `VerdictRecorded` (N-6) |
| 2 | The denominators cannot drift | `D_H ≠ D_R ≠ D_X`, locked before any experiment existed (`ADR-0071`, `ADR-0074`) |
| 3 | Unguarded runs cannot leak in | `unattributable_for_promotion` is **derived by compose**, not declarable (`ADR-0079` D4) |
| 4 | The harvester consumes; it never drives | The outer loop is a plugin at a graph slot with a capability ceiling excluding the workspace (`ADR-M0-12`, `ADR-0041`) |

Plus an anti-cheat lint pass (existing `test_anticheat.py` semantics) on every candidate pair.

#### 5.4.3 The promotion protocol — paired McNemar exact

Promotion is a **statistical decision**, not a threshold on a mean. `docs/04_annex/MEASUREMENT.md` `M-02`…`M-04` are binding.

```text
PROTOCOL  PairedPromotion(baseline B, candidate C, instance set I)

 1  ASSERT  B.undeletable == true                          # ADR-0015 frontier; the baseline cannot be removed
 2  ASSERT  D_H(B) ≠ D_H(C)  ∧  D_X(B) = D_X(C)            # same experiment cell, different composition
 3  BOTH arms attempt EVERY instance i ∈ I                 # M-02: paired design. NEVER two random samples
 4  Build the 2×2 discordance table from SIGNED verdicts only:

                          C pass      C fail
              B pass    [   n11    |    b   ]
              B fail    [    c     |   n00  ]

 5  Analyse DISCORDANT pairs only: (b, c). Concordant pairs carry NO information about the difference.
 6  McNemar EXACT (binomial), never the χ² approximation:
        p  =  2 · Σ_{k=c}^{b+c}  C(b+c, k) · 0.5^(b+c)        two-sided, H0: P(b) = P(c)
 7  Effect size and interval (M-04):
        Δ̂  =  (c − b) / |I|                                   paired difference in resolve rate
        CI  =  exact Clopper-Pearson interval on c / (b + c),  mapped back to Δ̂
 8  REPORT ALL OF: b, c, b+c, exact p, Δ̂, CI.
        A p-value without an effect size and an interval is NOT a result.
 9  PROMOTE iff  p < 0.05  ∧  Δ̂ > 0  ∧  CI excludes 0  ∧  no anti-cheat flag
        ∧  cassette-replay regression green  ∧  A HUMAN FLIPS THE POINTER      # SPEC §9, ADR-0019
10  EMIT signed promotion event → registry default pointer moves to D_H(C). B is retained forever.
```

**Power, stated so it is not discovered late.** `MEASUREMENT.md` is explicit and uncomfortable: *"detecting a five-point effect against a realistic floor typically requires low hundreds of paired instances"*, and *"most published agent comparisons are underpowered by an order of magnitude."* Between-task difficulty variance dominates every other variance component, which is why **an unpaired comparison of two configurations on two random task samples is measuring which sample was easier.** Sample size is derived numerically from the floor's discordance rate, the minimum detectable effect, alpha, and power — and recorded in the family declaration **before** the run.

> **The refusal that keeps this honest.** `SPEC.md` §9: **no scalar reward for promotion.** Promotion is a partial order over a frontier (`ADR-0015`, `REJ-11`). A candidate that wins on resolve rate while losing on cost does **not** dominate the baseline and does **not** promote — it joins the frontier. Collapsing the 6D tensor into one number to make promotion easy is the exact move that makes the frontier meaningless.

#### 5.4.4 Complexity of the stigmergic swarm, stated as a falsifiable measurement

For `N` logical agents over `T` turns, coordinating through the State Plane rather than through message passing:

```
                      messages / turn      context bytes / turn        AETHER mechanism
  message-passing        Θ(N²)              Θ(N² · |artifact|)         (full-state rebroadcast)
  stigmergic             Θ(N)               Θ(N · |Δ|)                 append to WAL; read a projection
```

Because `State = fold(events)` over one WAL stream per `project_id`, and because causal relations are **projections of events rather than a maintained graph** (`ADR-0003`, `ADR-0070`), sibling agents never address each other — they address the ledger. **The `O(N²)` term does not exist in this architecture.**

> **`RF-44` (M-7 gate).** Measured inter-agent messages per turn MUST remain `Θ(N)` as `N` scales from 1 to 64 over a bounded worker pool. If it does not, the Stigmergic Coordination Property is **refuted** and the `SPEC.md` §1.4 claim is struck. Stated as a measurement so the property can fail — which is the standard this project already applies everywhere else.

---

## §6 · Zero-Guesswork Developer Implementation Bridge

> **The contract of this section.** A developer picking up any task below needs **no interpretive judgement**. Every requirement has a schema, an FSM row, a named test function, and an explicit list of what would be wrong. Where a decision is genuinely open, it is labelled `DIRECTOR` or `TECH-LEAD` and **must not** be resolved locally.

### 6.1 Normative JSON Schema — `mhf.manifest/2` (Draft 2020-12)

**Path:** `schemas/mhf/harness_manifest.schema.json` — added **alongside** `mhf.harness/1`, which is frozen, not deleted (`ADR-0077` D5).

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://vanguard.dev/schemas/mhf/manifest_v2.schema.json",
  "$comment": "mhf.manifest/2 — the Named Component Graph (ADR-0077). Supersedes the fixed-slot PluginBindings of mhf.harness/1, which is FROZEN and remains readable through M-4 for corpus attribution. compose() freezes this into FrozenHarness; the JCS digest of the FULL behaviour-affecting composition — components, kinds, resolved refs and digests, config digests, per-component ceilings, bindings, system prompt, harness ceiling, approval policy, model routes — is D_H and D_H ONLY (ADR-0071, ADR-0074, A-5). Slot names are pack convention, never schema constraint (ADR-0077 D3).",
  "title": "HarnessManifestV2",
  "type": "object",
  "additionalProperties": false,
  "required": ["api", "id", "components"],
  "properties": {
    "api": { "type": "string", "const": "mhf.manifest/2" },
    "id":  { "type": "string", "minLength": 1 },

    "components": {
      "$comment": "The named component graph. Property NAMES are instance names chosen by the pack; 'planner'/'context'/'memory'/'evaluation' carry no special meaning to compose() (ADR-0077 D3). Multiplicity per kind is UNBOUNDED — two planner-kind components is the critic loop; N is debate.",
      "type": "object",
      "minProperties": 1,
      "propertyNames": { "pattern": "^[a-z][a-z0-9_-]{0,63}$" },
      "additionalProperties": { "$ref": "#/$defs/Component" }
    },

    "bindings": {
      "$comment": "Explicit wiring. Declares WHAT a component may address, never WHEN it runs — execution order is the universal turn loop plus spawn topology (ADR-0082 D1). This is NOT a workflow DAG (SPEC §9 refusal stands). Cycles and self-edges FAIL AT COMPOSE (ADR-0077 D8).",
      "type": "array",
      "default": [],
      "items": { "$ref": "#/$defs/Binding" }
    },

    "model_routes": { "type": "array", "items": { "$ref": "#/$defs/ModelRoute" }, "default": [] },
    "system_prompt": { "type": ["string", "null"],
      "$comment": "Path to the byte-stable L1 prompt. Its CONTENT digest enters D_H — two harnesses differing only in prompt MUST NOT share D_H (A-5)." },
    "capabilities": {
      "$comment": "The HARNESS ceiling. Every component ceiling is intersected with this FAIL-CLOSED at compose (ADR-0072). An empty array authorises NOTHING (RF-14).",
      "type": "array", "items": { "$ref": "#/$defs/CapabilityRequirement" }, "default": []
    },
    "budget": { "$ref": "effect_request.schema.json#/$defs/Reservation" },
    "approval_policy": { "type": ["string", "null"],
      "$comment": "null is a LEGAL declared absence (ADR-0079 D1). It enters D_H and marks the trajectory unattributable_for_promotion." },
    "guardrails": { "$ref": "#/$defs/GuardrailDeclaration" },
    "undeletable": { "type": "boolean", "default": false }
  },

  "$defs": {

    "Component": {
      "title": "Component",
      "type": "object",
      "additionalProperties": false,
      "required": ["kind", "ref"],
      "properties": {
        "kind": {
          "$comment": "One of the five frozen SPI kinds (ADR-M0-03 is NOT reopened). kind no longer implies cardinality one (ADR-0077 D2).",
          "type": "string",
          "enum": ["planner", "context", "memory", "toolkit", "evaluation"]
        },
        "ref": {
          "type": "string", "minLength": 1,
          "$comment": "Plugin reference with a semver caret range, e.g. 'mhf.planner.drive-until-green@^1'. An UNKNOWN ref FAILS AT COMPOSE, never at runtime (ADR-0005; RF-13)."
        },
        "config": { "type": "object", "default": {},
          "$comment": "Validated against the plugin's declared config_schema at VERIFIED. Its JCS digest enters D_H." },
        "ceiling": {
          "$comment": "Per-component capability ceiling. Intersected fail-closed with the harness ceiling. ABSENT means 'inherit the harness ceiling'; PRESENT-BUT-EMPTY means 'authorise nothing' — these are DIFFERENT and both must be tested (RF-26, RF-14).",
          "type": "array", "items": { "$ref": "#/$defs/CapabilityRequirement" }
        },
        "isolation": {
          "type": "string",
          "enum": ["in_process", "subprocess", "container", "wasm"],
          "default": "subprocess",
          "$comment": "I-6: plugins are untrusted by default. 'in_process' is a PRIVILEGE granted by policy and still speaks the same JSON-RPC wire (ADR-0072). RF-17 pins it."
        },
        "spawn_grant": {
          "type": "boolean", "default": false,
          "$comment": "ADR-0080 D4 — DESIGN-LOCKED, INERT UNTIL M-6. compose() MUST parse and digest this field from v0.6.2 so that D_H is stable across the M-6 cut, and MUST reject `true` with 'agent.spawn not implemented before M-6' until the verb exists. Parsing early, enforcing late — this is what keeps the corpus attributable across the boundary."
        }
      }
    },

    "Binding": {
      "title": "Binding",
      "type": "object",
      "additionalProperties": false,
      "required": ["from", "to", "relation"],
      "properties": {
        "from": { "type": "string", "$comment": "A component name that MUST exist in `components`." },
        "to":   { "type": "array", "minItems": 1, "items": { "type": "string" },
                  "$comment": "Component names that MUST exist. `from` ∈ `to` is a self-edge and FAILS AT COMPOSE." },
        "relation": {
          "type": "string",
          "enum": ["uses", "gated_by", "reviewed_by", "aggregates", "scores", "selects", "expands"],
          "$comment": "Closed roster. A new relation is a schema change with an ADR, never a free string — an open string set is how a workflow DAG smuggles itself in."
        }
      }
    },

    "GuardrailDeclaration": {
      "title": "GuardrailDeclaration",
      "$comment": "ADR-0079. Declaring a guardrail absent is LEGAL and enters D_H. Forging its OUTPUT is categorically illegal under every composition (D5). NOTE: `unattributable_for_promotion` is DERIVED by compose() and stamped on FrozenHarness — it is deliberately ABSENT from this schema (ADR-0079 D4). A manifest-writable attributability flag is a forgery surface.",
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "evaluation": { "type": "string", "enum": ["required", "none"], "default": "required" },
        "sandbox":    { "type": "string", "enum": ["required", "none"], "default": "required" },
        "approval":   { "type": "string", "enum": ["required", "none"], "default": "required" }
      }
    },

    "CapabilityRequirement": {
      "title": "CapabilityRequirement",
      "type": "object",
      "additionalProperties": false,
      "required": ["verb", "selector"],
      "properties": {
        "verb":     { "type": "string", "minLength": 1 },
        "selector": { "$comment": "MUST parse under domain/selectors/resource_selector.parse_selector. SELECTOR_KINDS = {fs, network, secret, git, table, browser, generic}. `kind: proc` is REJECTED — express process capability as {kind: generic, uriPattern: 'proc://exec/allow/...'} (settled at 2.1-D).", "type": "object" },
        "sink":     { "type": "string", "enum": ["observation", "advisory", "privileged"] },
        "risk":     { "type": "string", "enum": ["low", "medium", "high"] }
      }
    },

    "ModelRoute": {
      "title": "ModelRoute",
      "type": "object",
      "additionalProperties": false,
      "required": ["tier", "provider", "model"],
      "properties": {
        "tier":        { "type": "integer", "minimum": 1 },
        "provider":    { "type": "string", "minLength": 1 },
        "model":       { "type": "string", "minLength": 1 },
        "escalate_on": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

#### 6.1.1 Companion delta — `mhf.trajectory/1` (`ADR-0078` + `ADR-0079`)

The trajectory schema is **not** re-versioned; three currently-optional fields become **required**, and one object is added. `mhf.trajectory/1` stays the schema id because no existing field changes meaning.

```jsonc
// schemas/mhf/trajectory.schema.json — DELTA ONLY
{
  "required": ["schema","project_id","run_id","episode_id","principal_id","harness_digest",
               "turns","verdict","cost",
               "execution_digest",     // + ADR-0078 D3 — D_R, and D_R != D_H is asserted by RF-12
               "model_routes_used",    // + ADR-0078 D4 — with model_fingerprint non-null
               "guardrails"],          // + ADR-0079 D3
  "properties": {
    "execution_digest": { "type": "string", "pattern": "^sha256:[0-9a-f]{64}$" },   // was ["string","null"]
    "model_routes_used": { "type": "array", "minItems": 1,
      "items": { "required": ["tier","provider","model","model_fingerprint"],
                 "properties": { "model_fingerprint": { "type": "string", "minLength": 1 } } } },
    "guardrails": {
      "type": "object", "additionalProperties": false,
      "required": ["evaluation","sandbox","approval"],
      "properties": { "evaluation": {"type":"string"}, "sandbox": {"type":"string"}, "approval": {"type":"string"} }
    },
    "unattributable_for_promotion": { "type": "boolean",
      "$comment": "DERIVED by compose() from the resolved graph and copied from FrozenHarness. Never authored." },
    "verdict_absent_reason": { "type": ["string","null"], "enum":
      ["guardrail_absent","aborted","budget_exhausted","instrument_error", null],
      "$comment": "REQUIRED to be non-null whenever verdict is null (RF-12 clause 7). A null verdict with a null reason is an unexplained gap in the evidence chain." }
  }
}
```

> ⚠ **`CostVector` is deliberately NOT changed.** `additionalProperties: false` over `{usd_micros, tokens, bytes, millis}` already encodes `ADR-0074`'s type split. **Adding `depth` or `turns` to a `CostVector` is the single most likely accidental violation of the budget algebra**, and the schema already fails it closed. Do not "helpfully" widen it.

---

### 6.2 Complete plugin lifecycle FSM — implementation table

Authoritative transition table (`ADR-0081`). **Every row emits.** A transition with no event is the verified defect `RF-19` exists to kill.

| # | From | To | Trigger | Ledger event | Writer role | Payload (beyond lineage) | Falsifier |
|---|---|---|---|---|---|---|---|
| 1 | ∅ | `DISCOVERED` | scan path / `mhf.plugins` entry point resolves | **`PluginDiscovered`** ⭐ | `registry` | `{plugin_id, source_path, manifest_digest}` | `RF-19` |
| 2 | `DISCOVERED` | `RESOLVED` | deps topologically resolved; SPI version negotiated | `PluginResolved` | `registry` | `{plugin_id, resolved_version, spi_version, dep_digests[]}` | `RF-13` |
| 3 | `DISCOVERED` | `FAULTED` | unknown ref / unsatisfiable semver | `PluginFaulted` | `registry` | `{plugin_id, reason: "unresolvable_ref"}` | `RF-13` |
| 4 | `RESOLVED` | `VERIFIED` | config schema ✓ · signature policy ✓ · **ceiling ∩ harness ceiling ✓ (fail-closed)** | **`PluginVerified`** ⭐ | `registry` | `{plugin_id, config_digest, ceiling_digest, signature_ok}` | `RF-19`, `RF-14` |
| 5 | `RESOLVED` | `FAULTED` | schema / signature / **empty-ceiling** failure | `PluginFaulted` | `registry` | `{plugin_id, reason: "verification_failed"}` | `RF-14` |
| 6 | `VERIFIED` | `ACTIVATED` | isolation broker starts the cell; UDS handshake ✓ | `PluginActivated` | `registry` | `{plugin_id, isolation_tier, cell_pid, socket_digest}` | `RF-17` |
| 7 | `VERIFIED` | `FAULTED` | cell start failure / rlimit refusal / handshake timeout | `PluginFaulted` | `registry` | `{plugin_id, reason: "activation_failed"}` | `RF-16` |
| 8 | `ACTIVATED` | `QUIESCING` | drain requested; in-flight calls draining | `PluginQuiesced` | `registry` | `{plugin_id, inflight_count}` | — |
| 9 | `ACTIVATED` | `FAULTED` | crash · rlimit kill · RPC timeout · protocol violation | `PluginFaulted` | `registry` | `{plugin_id, reason, exit_code, restart_count}` | `RF-16` |
| 10 | `QUIESCING` | `RETIRED` | drain complete; cell exited | `PluginRetired` | `registry` | `{plugin_id, final_call_count}` | — |
| 11 | `QUIESCING` | `FAULTED` | drain timeout ⇒ forced kill | `PluginFaulted` | `registry` | `{plugin_id, reason: "drain_timeout"}` | `RF-16` |
| 12 | `FAULTED` | `RETIRED` | crash-loop backoff exhausted, or declared substitute activated | `PluginRetired` | `registry` | `{plugin_id, reason, substitute_id?}` | `RF-16` |
| 13 | `RETIRED` | — | terminal | — | — | — | — |

⭐ = **new event kind** (`ADR-0081` D3, Director escalation ruled). `EVENT_KINDS` 56 → 58.

**Illegal by construction — each must be a test, not a comment:**

| Illegal | Why | Falsifier |
|---|---|---|
| `RETIRED → *` | Terminal is terminal | `RF-16` |
| `FAULTED → ACTIVATED` | A faulted cell may not become active without re-traversing from `DISCOVERED` | `RF-16` |
| Any transition with no event | The verified `_EVENT.get() is None` silent path | `RF-19` |
| A non-`registry` role appending a `Plugin*` kind | `ADR-0074` writer authority; `PRIVILEGED_KIND_OWNERS` | `RF-15` |
| A ref resolved at runtime rather than compose | `ADR-0005` freeze-at-composition | `RF-13` |
| Any mutation of a frozen composition | `ADR-0072` §3 no hot-swap | `RF-18` |

**Reducer obligation.** Both new kinds fold into `LedgerState.plugins` as `PluginRecord` state transitions, included in `to_canonical_dict()` (and therefore in the state digest). `CataloguedKindsAreFoldedOrAllowlisted` extends 56 → 58 with **zero** additions to `UNFOLDED_ALLOWLIST` — a lifecycle kind that is catalogued but unfolded is exactly the round-3 M-2 blocker, resurfacing at M-3.

---

### 6.3 The 1-to-1 executable falsifier matrix

Every requirement in this document maps to exactly one named test function. **`RF-*` is the register namespace** (`ADR-0082` D5); `RF-01 … RF-22` alias the existing `F-01 … F-22`.

#### Carried (existing, aliased) — status as of this pass

| ID | Test function | Wave | Status |
|---|---|---|---|
| `RF-01` | `test_every_emitted_envelope_carries_full_lineage` | 1 | ✅ green |
| `RF-02` | `test_cold_reader_reconstructs_live_state_from_disk` (`ColdReplayParity`) | 0/1 | ✅ green |
| `RF-03` | `test_scheduler_cannot_produce_a_verdict_without_a_signature` | 1 | ✅ green |
| `RF-04` | `test_replayed_or_unbound_signature_is_rejected` | 1 | ✅ green |
| `RF-05` | `test_orchestrator_cannot_append_privileged_kinds` | 1 | ✅ green |
| `RF-06` | `test_declared_ceiling_survives_compilation_and_denies` | 1 | ✅ green |
| `RF-07` | `test_empty_ceiling_denies_everything` | 1 | ✅ green |
| `RF-08` | `test_privileged_verb_requires_a_bound_grant` | 0/1 | ⚠ **STALE — formally retired here.** It dispatched a fully authorized `fs.write` and asserted the grant path must fail on its own happy path. Restated in both directions in `test/falsifiers/`. **The register must say so in its own table** (§7.2) |
| `RF-09` | `test_child_grant_wider_than_parent_is_denied_whole` | 1 | ✅ green |
| `RF-10` | `test_sibling_depths_are_not_summed` | 1 | ✅ green |
| `RF-11` | `test_prompt_or_ceiling_change_changes_digest` | 1 | ✅ green |
| **`RF-12`** | **`test_episode_completed_emits_populated_mhf_trajectory_1`** | **2** | 🔴 **SUPERSEDED & RED — `ADR-0078`. The content assertions replace schema-validity-only** |
| `RF-13`…`RF-19` | NOVA-4 suite + FSM completeness | 3 | ⚪ authored at 3.1 |
| `RF-16` | `check_duplication.py --enforce` (no second selector algebra) | 0/2 | ✅ green *(note: also the NOVA-4 FSM id — see the collision note below)* |
| `RF-17` | living CI runs `test/kernel` + packages suites | 0 | ✅ green |
| `RF-18` | `check_domain_blindness.py` scans `layer0/` **and** `packages/{domain,kernel}/` | 0 | ✅ green |
| `RF-19` | discovery collects `test/integration/` + `test/governance/` | 0 | ✅ green |
| `RF-20` | `preregistered_oracles.json` resolves at a canonical path | 0 | ✅ green |
| `RF-21` | `ProposalTranslator` lifts `parameters` spelling and fenced payloads | 0/1 | ✅ green |
| `RF-22` | `test_reconciliation_of_undeterminable_effects` | 1 | ✅ green |

> ⚠ **Numbering collision inside this table, and its resolution.** `RF-13`…`RF-22` are already taken by the aliased Wave-0/1 falsifiers, so the NOVA-4 suite and the new work **cannot** start at 13. **Ruling: new falsifiers begin at `RF-23`.** The NOVA-4 six become `RF-23n`…`RF-28n`? — **No.** Cleanest and final: **new falsifiers are numbered `RF-23` upward in a single monotonic sequence**, and the NOVA-4 / component-graph / guardrail IDs used narratively in §2–§3 are normalised by the table below. **This table is authoritative over §2 and §3 where they differ.**

#### New — authoritative numbering

| ID | Test function | Authorised by | Milestone | Falsifies |
|---|---|---|---|---|
| **`RF-23`** | `test_episode_completed_emits_populated_mhf_trajectory_1` **(NOVA-1)** | `ADR-0078` | **M-2** | `_ZERO_COST`; schema-validity-only |
| **`RF-24`** | `test_planner_cannot_author_a_cost_field` | `ADR-0078` D6 | M-2 | self-reported cost |
| **`RF-25`** | `test_episode_suspends_cold_reconstructs_and_resumes_to_completion` **(NOVA-2)** | `ADR-0082` D2 | **M-2 (gate)** | in-process coupling |
| **`RF-26`** | `test_proc_pattern_read_from_compiled_ceiling` **(NOVA-3)** | board carry-over | M-2 | ceiling restated as a literal |
| **`RF-27`** | `test_sealed_child_scope_rejects_out_of_scope_action_at_S5` | `ADR-0080` C3 | M-2 | the stale-docstring scenario |
| **`RF-28`** | `test_falsifier_ids_are_unique_across_annex_and_register` (linter) | `ADR-0082` D5 | M-2 | the `F-*` namespace collision |
| **`RF-29`** | `test_unknown_plugin_ref_fails_at_compose_not_runtime` **(NOVA-4/1)** | `ADR-0081` D4 | M-3 | late binding |
| **`RF-30`** | `test_empty_component_ceiling_denies_everything` **(NOVA-4/2)** | `ADR-0081` D4 | M-3 | `if not capabilities: return True` |
| **`RF-31`** | `test_only_registry_may_append_plugin_kinds` **(NOVA-4/3)** | `ADR-0081` D4 | M-3 | generic append |
| **`RF-32`** | `test_faulted_cell_cannot_remain_active` **(NOVA-4/4)** | `ADR-0081` D4 | M-3 | crashed cell still serving |
| **`RF-33`** | `test_in_process_requires_explicit_policy_grant` **(NOVA-4/5)** | `ADR-0081` D4 | M-3 | `in_process` as default |
| **`RF-34`** | `test_no_code_path_mutates_a_frozen_composition` **(NOVA-4/6)** | `ADR-0081` D4 | M-3 | any hot-swap surface |
| **`RF-35`** | `test_every_fsm_transition_emits_a_ledgered_event` | `ADR-0081` D3 | M-3 | the verified silent-transition defect |
| **`RF-36`** | `test_code_default_toolkits_load_through_the_lifecycle` | `ADR-0081` D1 | M-3 | direct imports |
| **`RF-37`** | `test_layer0_directory_does_not_exist` | `ADR-0081` D5 | M-3 | a deletion that never happened |
| **`RF-38`** | `test_exactly_one_manifest_parser_exists` | `ADR-0077` D6 | M-3 | a second YAML→harness path |
| **`RF-39`** | `test_component_graph_compiles_two_planners_with_distinct_names` | `ADR-0077` D2 | M-3 | `kind` implying cardinality one |
| **`RF-40`** | `test_six_reference_topologies_compile_to_six_distinct_D_H` | `ADR-0077` D1 | M-3 | a graph that cannot express debate / tree search |
| **`RF-41`** | `test_binding_edge_change_changes_D_H` | `ADR-0077` D4 | M-3 | `D_H` ignoring wiring |
| **`RF-42`** | `test_component_ceiling_intersects_harness_ceiling_fail_closed` | `ADR-0077` D7 | M-3 | a widening component ceiling |
| **`RF-43`** | `test_cyclic_binding_fails_at_compose_not_runtime` | `ADR-0077` D8 | M-3 | cycle detection at runtime |
| **`RF-44`** | `test_evaluation_none_compiles_and_changes_D_H` | `ADR-0079` D1/D2 | M-3 | rejecting declared absence |
| **`RF-45`** | `test_unsigned_verdict_rejected_even_with_evaluation_none` | `ADR-0079` D5 | M-3 | absence degrading into forgery |
| **`RF-46`** | `test_unattributable_flag_is_derived_not_manifest_writable` | `ADR-0079` D4 | M-3 | a declarable attributability flag |
| **`RF-47`** | `test_spawn_grant_true_is_rejected_before_M6` | `ADR-0080` D1 | M-3 | premature `agent.spawn` enablement |
| **`RF-48`** | `test_real_run_trajectory_carries_nonzero_cost` **(NOVA-5)** | `ADR-0078` | **M-4** | a green unit test over a hollow real run |
| **`RF-49`** | `test_pack2_introduces_zero_diffs_under_domain_and_kernel` | `ADR-0077`+I-7 | M-5 | I-7 as an untested thesis |
| **`RF-50`** | `test_pack2_trajectory_parity_with_pack1` | `ADR-0078` | M-5 | "domain-blind but only Pack #1 is learnable" |
| **`RF-51`** | `test_planner_without_spawn_grant_cannot_delegate` | `ADR-0080` D4 | M-6 | ambient delegation |
| **`RF-52`** | `test_spawn_is_recorded_as_a_mediated_effect_with_a_receipt` | `ADR-0080` D2 | M-6 | unledgered delegation |
| **`RF-53`** | `test_spawn_selector_denies_undeclared_harness_digest` | `ADR-0080` D2 | M-6 | spawn as a blanket verb |
| **`RF-54`** | `test_child_cannot_reach_evaluator_without_selector_grant` | `ADR-0080` D5 | M-6 | ambient evaluator reachability (S-2) |
| **`RF-55`** | `test_capability_revoked_terminates_a_live_lease` | §1.2.3 | M-7 | a catalogued kind with no emitter (TOCTOU) |
| **`RF-56`** | `test_inter_agent_messages_per_turn_stay_linear_in_N` | §5.4.4 | M-7 | the `O(N²)` broadcast pattern |
| **`RF-57`** | `test_four_topologies_run_multipack_with_zero_engine_diff` | `ADR-0082` D1 | M-8 | the loop-as-mechanism claim (partial refutation of the Standing Challenge) |
| **`RF-58`** | **The Standing Challenge** — adjudicated, not automated | `ADR-0082` D1 | M-8 | an unfalsifiable architectural claim |

---

### 6.4 Negative constraints & anti-patterns checklist

**Print this. It is the review checklist for every PR from M-2 through M-10.**

#### ❌ TCB and the kernel

- [ ] **No `vanguard/packages/kernel/` diff before M-4 closes**, except tests. A kernel diff inside the M-4 evidence window **voids the evidence bundle**.
- [ ] **No raising the TCB ceiling to fit an implementation.** 1365/1438 today; `agent.spawn` is budgeted at **≤ 40 logical LOC** at M-6. Exceeding it is a design failure to escalate, not a ceiling to raise.
- [ ] **No second decision procedure.** One selector algebra, one canonicalisation (JCS/RFC 8785), one writer. `check_duplication.py --enforce` fails a second; do not weaken its heuristics to pass.
- [ ] **No "allow with a warning".** `Outcome` has exactly three members. `K-26` forbids narrowing a request without saying so.
- [ ] **No constant standing in for a classifier.** `K-08`: S4 is a *call*. A hardcoded `widens_capability` is the prototype defect the classifier docstring exists to memorialise.

#### ❌ Domain blindness (I-7)

- [ ] **No `coding` / `pytest` / `ast` tokens** under `vanguard/packages/{domain,kernel}/`. At M-5, add `proof` / `lemma` / `smt` — Pack #2 must not leak either.
- [ ] **No pack-specific verb, selector kind, or oracle name in core.** `MUTATING_VERBS` (§5.1.2) is **pack data**.
- [ ] **No measurement apparatus imported by the kernel.** `tools/telemetry/`, `lab/`, and the harvester are siblings, never dependencies (D-40).

#### ❌ Evidence and writer authority

- [ ] **No `VerdictRecorded` from anything but `runtime/evaluator_gateway.py`.** Unsigned or unbound ⇒ refuse. This is defect F1 and it killed the previous architecture.
- [ ] **No self-reported cost.** Cost is folded from ledgered kernel events and receipts (`ADR-0078` D6). A plugin-authored cost is a forged verdict wearing a different hat.
- [ ] **No manifest-writable `unattributable_for_promotion`.** Derived by `compose()`, or the whole guardrail model is theatre (`ADR-0079` D4).
- [ ] **No silent FSM transition.** Every row of §6.2 emits. `_EVENT.get(target)` returning `None` is the verified defect.
- [ ] **No signature verification inside the reducer.** That is the reader's job (`adapters/evaluators/gate.py`). The reducer stays pure.

#### ❌ Budget algebra (`ADR-0074`)

- [ ] **Never sum sibling depths.** `depth` is structural: `child = parent + 1 ≤ root.max_depth`.
- [ ] **Never add `depth` or `turns` to a `CostVector`.** The schema fails it closed; do not widen `additionalProperties`.
- [ ] **Never give a child an independent wallet.** Additive dimensions debit the parent's *remaining* vector, component-wise.
- [ ] **Beware duck-typed `as_map()`.** The 2.2-A finding stands: a permissive map view can *silently* restore sibling-depth summing. Keep the types.

#### ❌ Composition and freeze

- [ ] **No runtime resolution.** Unknown refs, unsatisfiable semver, cyclic bindings, and empty ceilings fail **at compose** (`ADR-0005`).
- [ ] **No mid-run `FrozenHarness` mutation.** Quiesce exists for fault and restart, never for flipping composition under a live `D_H` (`ADR-0072` §3).
- [ ] **No `compose()` keying on a slot name.** Names are pack convention (`ADR-0077` D3). `if name == "planner"` in `runtime/` is a boundary violation in disguise.
- [ ] **No `bindings` relation outside the closed roster.** An open string set is how a workflow DAG smuggles itself in.

#### ❌ Concurrency (I-11)

- [ ] **No parallel fan-out before M-7's measurement gate.** Unknown selector footprint means **conflict**, not independence.
- [ ] **No claim that byte-identical concurrent ledgers are required.** They are not, and asserting it invents an impossible requirement (`ADR-0071`).

#### ❌ Governance and process

- [ ] **No editing `ADR-0069`–`0082`.** Append-only. A new ADR narrows an old one by **citation with evidence**, never by silent edit (`ADR-0000`).
- [ ] **No locked concept without a bound falsifier.** `ADR-0074`: a concept without one is not locked.
- [ ] **No falsifier traded away to make a wave fit.** Shed breadth. Never falsifiers.
- [ ] **No documentation surgery before M-4 closes** (`ADR-0082` D3).
- [ ] **No `DEV-LOCAL` label on a decision that fixes `D_H`'s pre-image.** That is how `3.2-C` nearly became the T-1 vehicle by accident.
- [ ] **No lexical green.** A wave green by grep is not done. `E-COV` is a weak structural lint and **is not I-2**.
- [ ] **No scalar reward for promotion.** Partial order over a frontier (`ADR-0015`, `REJ-11`).
- [ ] **No metaphysical framing** in any document under `docs/` (`ADR-M0-10`, `REJ-10`).

---

## §7 · Repository Hygiene & Document Update Cascade

> **Sequencing rule that governs this whole section.** Hygiene that is **cheap, local, and reversible** executes in M-2. Hygiene that is **structural** (the collapse to the Clean Triad) is **forbidden before M-4 closes** (`ADR-0082` D3). Do not mix them.

### 7.1 Stale artifacts — immediate, M-2, no ADR required

| # | Artifact | Verified state | Directive | Owner |
|---|---|---|---|---|
| H-1 | `DELETE.md` (repo root) | **0 bytes** `[VERIFIED]` | **`git rm DELETE.md`.** A zero-byte file whose name is an instruction is a landmine for every future reader | Dev A |
| H-2 | `docs/08_workflows/` | **Empty directory** `[VERIFIED]` | **Delete.** If workflow docs are wanted later, `docs/08_diagrams/` already exists and holds four SVGs | Dev A |
| H-3 | `docs/06_references/RESEARCH_THEORETICAL_SYNTHESIS.md` **and** `_B.md` | Near-duplicate pair, **both carrying `id: REF-06-M5`** and identical titles `[VERIFIED]` | **Keep `_B` (the successor); delete the original; strike the duplicate front-matter id.** Two documents claiming one id is the prose form of a duplicate primary key | Tech Lead |
| H-4 | `docs/06_references/vanguard_body_detailed.md` | Built on biological / cosmological framing | **Director ruling: RETIRE from `docs/`.** `ADR-M0-10` / `REJ-10` forbid that framing in *any* document under `docs/`, and a standing refusal with a live exception is not a refusal. Preserve in git history; the ideas that survive re-enter as ADR-shaped proposals in plain language | **Director** |
| H-5 | `docs/06_references/RESEARCH_Harness_Builder_Framework.md` | A greenfield PRD (Redis / NATS / ChromaDB / K8s / event bus) contradicting the locked hexagonal lattice | **Retain, with a mandatory banner:** *"REJECTED AS A COMPETING ARCHITECTURE (`ADR-0069`, `ADR-0070`). Mine for plugin/adapter ideas only. This design would re-create the dual-runtime failure."* Deleting it loses the catalog; leaving it unmarked invites a re-import | Tech Lead |
| H-6 | `002_beta_…`, `004_delta_…`, `005_epsilon_…`, `006_fi_…`, **`007_zeta_…` (this file)** at repo root | Review artifacts outside the documentation tree; three are 0 bytes `[VERIFIED]` | **Move all non-empty ones to `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/`; delete the empty ones.** Root-level review files are outside the Clean Triad and outside every linter's scan path | Tech Lead |
| H-7 | `workflow_visualizer.html` (repo root, 49 KB) | Unreferenced by any doc or tool `[VERIFIED]` | **Move to `tools/substrate_visualizer/`** (which already exists) or delete. Not a root artifact | Dev B |
| H-8 | `docs/00_overview/SYSTEM_OVERVIEW.md` §1.4, §7.4 | References `DIRECTOR_TODO_LOCK_CONCEPTS.md` (V1) — **not present at that path** `[VERIFIED]` | Repoint or strike. `check_markdown_links.py` does not catch it — see H-9 | Tech Lead |
| H-9 | `tools/linters/check_markdown_links.py` | `DOC_GLOBS = ("README.md", "docs/README.md", "docs/agile/sprint6B/*.md")` — the third glob **matches nothing** `[VERIFIED]` | **Widen to `docs/**/*.md` + repo-root `*.md`.** The gate currently reports `LINK PASS` while the entire `docs/` corpus, all 90 ADRs, and both Director briefings go unchecked. **This is the same defect class as `F-18`: a linter narrower than the invariant it certifies** — and it is why four broken ADR links survived CI | Dev B |
| H-10 | `docs/03_sprints/plans/` referenced by `sprint_active.md`; wave plans actually live in `docs/03_sprints/doing/` and `done/` `[VERIFIED]` | Path drift between the board and the tree | Repoint `sprint_active.md`'s `plans:` front-matter key; add both directories to `check_stale_paths.py` | Dev A |

> **H-9 is the highest-value item in this table** and is not cosmetic. A link checker that validates two files while reporting `LINK PASS` is a gate that **manufactures false confidence** — precisely the failure mode `F-18` was raised for and precisely the failure mode that let `SYSTEM_OVERVIEW` ship with four dead ADR links (`003` §7.4). Fix it in M-2, before the corpus grows by six ADRs.

### 7.2 `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_…GAP_REGISTER.md`

**Authority:** authoritative on **outcomes**; cannot contradict `SPEC.md` or the ADRs. Retires at M-5 (`ADR-0082` D3).

| § | Directive |
|---|---|
| **Header** | Add: *"Falsifier namespace renamed `F-*` → `RF-*` (`ADR-0082` D5) to resolve the verified collision with `docs/04_annex/KERNEL.md`'s kernel-control `F-01…F-25`. Alias table in §4.2a. Scheduled to retire as a standing authority at M-5."* |
| **§4.2 header** | Rename column `ID` → `RF-ID`; add an `Authorising ADR` column |
| **§4.2 `F-08` row** | **Restate as retired:** *"`RF-08` — **STALE, retired at Wave-1 exit.** The test dispatched a fully authorized `fs.write` and asserted the grant path must fail on its own happy path. The kernel is correct: S6 issues via `SinkRegistry.requires_grant`; S8 re-verifies against the descriptor digest at the point of effect (`K-05`); S8a records `grantId`/`grantDigest` in durable intent. Restated in both directions in `test/falsifiers/`. No kernel change."* This currently lives only in a sprint-board table and **must** be in the register |
| **§4.2 `F-12` row** | **Replace with `RF-23`** and the eight content assertions of `ADR-0078`. Add: *"Schema validity is necessary and not sufficient — a content-free record satisfies a validity assertion while violating I-9."* |
| **§4.2a (NEW)** | The alias table `RF-01 ≡ F-01 … RF-22 ≡ F-22` |
| **§4.2b (NEW)** | Insert rows `RF-23` … `RF-58` verbatim from §6.3 of this document, in the same table format, each naming its authorising ADR and milestone |
| **§3 Wave 2 exit gate** | Append: *"`RF-23` (populated trajectory) and `RF-25` (cold suspend/resume) are M-2 exit conditions. `RF-25` red blocks M-3 entry and re-scopes M-7 as a rewrite."* |
| **§3 Wave 3 exit gate** | Replace with the seven-clause M-3 gate of §4.2 above, including **all seven** FSM transitions ledgered |
| **§3 Wave 4** | Row 8 changes from *"Schema-valid `mhf.trajectory/1`"* to *"**Schema-valid AND populated** `mhf.trajectory/1` (`RF-23` + `RF-48`)"* |
| **§2 deferred table** | Append: *"Automated environment/arena synthesis — **refused as a substrate feature** (§1.2.4). Preregistered oracles exist so the judged cannot author its own arena. May enter as pack data behind a preregistration event, never as a core capability."* |
| **§4.4** | `P1-14` (concurrency) gains: *"gated on `RF-25`, then on `RF-56` (`Θ(N)` messaging) at M-7."* |

### 7.3 `docs/05_adr/` — the ADR cascade

| Action | Detail |
|---|---|
| **CREATE** `0077-named-component-graph-is-the-composition-surface.md` | Full text: §3.1 |
| **CREATE** `0078-trajectory-content-contract-learnable-corpus.md` | Full text: §3.2 |
| **CREATE** `0079-absent-vs-forged-declarable-guardrails.md` | Full text: §3.3 |
| **CREATE** `0080-agent-spawn-as-capability-mediated-kernel-verb.md` | Full text: §3.4 |
| **CREATE** `0081-layer0-terminal-absorption-nova4-plugin-event-kinds.md` | Full text: §3.5 |
| **CREATE** `0082-loop-as-mechanism-cold-resume-and-scheduled-reviews.md` | Full text: §3.6 |
| **UPDATE** `INDEX.md` | Six rows; note that `0077` extends `0071`/`0072`, `0078` narrows `F-12`, `0079` extends `0072`/`0074`, `0080` extends `0070`, `0081` extends `0069`/`M0-13`, `0082` extends `0070`/`0071`/`M0-02`/`M0-03` |
| **DO NOT EDIT** `0069`–`0076`, `ADR-M0-*` | Append-only (`ADR-0000`). `ADR-0082` D5 **extends** `ADR-M0-02` by citation with evidence; it does not edit it |
| **`DEFERRED_REJECTED.md`** | Add `REJ-13`: *"Automated environment/arena synthesis as a core capability"* (§1.2.4). Add `REJ-14`: *"CRDTs / eventual consistency / cache-coherence protocols for inter-agent state"* — `project_id` is the consistency unit with a total order; revisit only if `RF-56` at M-7 demands it (§1.2.2) |

**The namespace ruling, stated once for implementers.** `F-01 … F-25` exist with different meanings in `KERNEL.md` (kernel controls, embedded in ~19 source and test files) and in the `002` register (bound falsifiers, embedded in docs and `test/falsifiers/`). The **register** side renames because its blast radius is smaller: `F-*` stays with the annex; `RF-*` becomes the register's. `RF-28` (`test_falsifier_ids_are_unique_across_annex_and_register`) is the linter that prevents recurrence, and it belongs in `tools/linters/`.

### 7.4 `docs/SPEC.md` — section-by-section diff directives

> **These are `v0.6.1`/`v0.6.2` edits to the version anchor and four sections. `SPEC.md` is law; every edit below cites its authorising ADR.**

| § | Directive |
|---|---|
| **Header — Version anchor** | `v0.6.0 Concept Lock` → `v0.6.1 Substrate Correction Lock (ADRs 0069–0074, Director-approved by 0075; corrections 0077–0082)`. **Do not** cut `pyproject.toml` from `0.4.5b1` — that happens at M-4/v0.7.0 and is Director-only |
| **§1.0** — Recursive machine | Append after the `spawn(...)` line: *"`spawn` is engine-owned in v0.6. `agent.spawn` as a capability-mediated kernel verb is **design-locked** by `ADR-0080` and implemented at M-6. Delegation targets are resources: a grant may permit spawning one `D_H` and deny another."* |
| **§1.1** — Turn state machine | Insert the **Universal Turn Loop as Mechanism** claim verbatim from `ADR-0082` D1, with `RF-58` (the Standing Challenge) named inline and the M-8 adjudication date stated |
| **§1.2** — Event taxonomy | Plugins row: `PluginResolved, PluginActivated, PluginQuiesced, PluginRetired, PluginFaulted` → **`PluginDiscovered, PluginResolved, PluginVerified, PluginActivated, PluginQuiesced, PluginRetired, PluginFaulted`** (`ADR-0081` D3). Writer-authority table: both new kinds → `registry`. Note the count change 56 → 58 |
| **§1.4** — Scheduler | Add the **Stigmergic Coordination Property** with its complexity claim and `RF-56` as its bound falsifier (§5.4.4). Mark as a claim under measurement, activated at M-7, **not** a v0.6 property |
| **§2.3** — Harness manifest | **The largest edit.** Replace the fixed-slot `harness.yaml` example with the `mhf.manifest/2` example of `ADR-0077`. State: components are a named map; `kind` does not imply cardinality one; slot names are pack convention; bindings are a closed relation roster and **not** a workflow DAG; `D_H` covers the graph including bindings; `mhf.harness/1` is frozen and readable through M-4, removed at M-5. Add the critic-loop example as the concrete demonstration of what `/1` cannot express |
| **§2.3** — new subsection *Declared absence* | The absent-vs-forged rule from `ADR-0079`: what may be declared absent, that the declaration enters `D_H`, that `unattributable_for_promotion` is **derived not declared**, and that an unsigned verdict stays categorically illegal under every composition |
| **§4** — Coding Domain Pack | Add: *"Pack #2 is **Math & Formal Deductive Verification** and is the **M-5 generality gate** — not an aspiration (§4.3). Acceptance: zero diffs under `packages/{domain,kernel}/` **and** trajectory parity with Pack #1."* Correct the orphaned-TableWorld note: TableWorld is demoted to **Pack #3** |
| **§7** — Telemetry | Replace the trajectory example with a **populated** one. State the eight `RF-23` content assertions as normative. Define `D_R` constructively (`ADR-0078` D3). Add the required-now/required-later table (`ADR-0078` D4) so no field becomes a false green |
| **§9** — Refusals | Append two: *"No automated environment/arena synthesis as a substrate feature"* and *"No CRDT / eventual-consistency / cache-coherence protocol for inter-agent state."* **Do not** duplicate the whole list into the ADRs — §9 is its single home once M-5's collapse lands |
| **Invariants I-1…I-11** | **I-9 gains its teeth:** *"…a valid harvest row — meaning populated turns, non-zero per-turn cost and latency, a model fingerprint, `D_R` distinct from `D_H`, and a signed verdict or an explicitly-reasoned null. Schema validity is necessary and not sufficient (`ADR-0078`)."* **I-11 gains its precondition:** *"…gated on a measurement whose precondition is `RF-25` (cold suspend/resume) and whose gate is `RF-56` (`Θ(N)` messaging)."* |

### 7.5 `docs/03_sprints/sprint_active.md`

| Location | Directive |
|---|---|
| Front-matter | `milestone:` → `M-2 (Wave 2 + Substrate Correction) — v0.6.1`. Fix `plans:` to point at `docs/03_sprints/doing/` (H-10) |
| **"Follow-ups carried out of Wave 1"** | **STRIKE** the row *"`assemble_trajectory` reports a zero cost vector; real per-turn cost needs the governor's settled ledger → Wave 4"*. **REPLACE** with: *"**NOVA-1 / `RF-23` — landed in M-2 per `ADR-0078`.** The board's premise was correct but insufficient: the governor's settled ledger already exists at `EpisodeCompleted` — `Receipt.cost`, `BudgetCommitted`/`BudgetReleased`, and the `events` sequence are already parameters of `assemble_trajectory` and were being discarded. Wave 4's remaining contribution is **NOVA-5 / `RF-48`** — confirmation on one real run."* **This closes discrepancy D-C in writing, which is what checklist item 1c required.** |
| Wave 2 table | Add `NOVA-1` (`READY`), `NOVA-2` (`READY`), `NOVA-3` (`READY`), `2.6-A` ADR authoring (`DIRECTOR`), `2.6-B` namespace + linter (`READY`), `2.6-C` docstring correction + `RF-27` (`READY`) |
| Wave 3 table | Rebalance to five sprints per §4.2's M-3 table. **Re-label `3.2-C` from `DEV-LOCAL` to `DIRECTOR`** and fold into 3.3 — *a `DEV-LOCAL` task must never be the vehicle for a decision that fixes `D_H`'s pre-image*. Add sprints 3.3, 3.4, 3.5 and 3.1-Z with their falsifier IDs |
| Wave 4 table | Row 8 of the nine-row gate → *"schema-valid **and populated**"*; add `4.1-E` NOVA-5 |
| **Decision queue** | Add: **(a)** ratify `ADR-0077`–`0082` — *Director*; **(b)** new event kinds `PluginDiscovered`/`PluginVerified` — *Director, escalated and ruled in `ADR-0081` D3*; **(c)** retire `vanguard_body_detailed.md` — *Director*; **(d)** `3.2-C` re-label — *Director* |
| **Director-Only Escalations** | Append: *"Manifest schema version bump · falsifier namespace change · any change to the nine-row M-4 gate · any `agent.spawn` implementation before M-6."* |
| **Definition of done** | Append: *"…**and** the trajectory emitted by any touched path satisfies `RF-23`."* |

### 7.6 `docs/02_roadmap/milestones.md`

| Location | Directive |
|---|---|
| M-2 row | Outcome gains *"+ Substrate Correction"*; exit gate gains `RF-23` and `RF-25`; add a **Version** column, value `v0.6.1` |
| M-3 row | Exit gate gains: **all seven** FSM transitions ledgered · six reference topologies compile to distinct `D_H` · absent-vs-forged live · NOVA-4 green. Version `v0.6.2` |
| M-4 row | Row 8 → *"populated trajectory"*; version `v0.6.3`; add *"Director acceptance of the evidence bundle is a separate act from producing it"* |
| M-5 row | Name Pack #2 explicitly as **Math & Formal Deductive Verification**; add trajectory parity (`RF-50`) and the TCB-metric replacement triple. Version `v0.7.0`; note the `pyproject.toml` cut lands here |
| M-6…M-10 rows | Add the **Version** column: `v0.8.0`, `v0.9.0`, `v0.9.0`, `v1.0.0`, `v1.0.0`. Add `RF-54` to M-6, `RF-55`/`RF-56` to M-7, `RF-57`/`RF-58` to M-8 |
| Standing Architectural Constraints | Append: *"**Falsifier discipline** — a wave may shed breadth; it may never shed falsifiers."* |

### 7.7 Wave plan files (`docs/03_sprints/doing/`)

| File | Directive |
|---|---|
| `wave3_extensibility.md` | Add sprints **3.3** (component graph), **3.4** (absent-vs-forged), **3.5** (spawn design-only), **3.1-Z** (layer0 deletion, atomic with green NOVA-4). Extend 3.1's acceptance to **all seven** ledgered transitions incl. the two new kinds. Re-label `3.2-C` `DIRECTOR`. Add the NOVA-4 acceptance table with `RF-29`…`RF-35`. Restate *"Deliberately not in scope"* to keep WASM, mandatory signatures, and any second product plugin out |
| `wave4_foundation_e2e.md` | Strike the "cost row" deferral; row 8 → populated; add `4.1-E` NOVA-5 / `RF-48`. Add the evidence-bundle contents: ledger digest · `D_H` · `D_R` · full trajectory · containment boolean · **the exact `RF-*` list green on the run** |
| `wave2B_review.md` | This document supersedes it as the review artifact. Add a pointer banner and move to `docs/07_reviews/` with H-6 |
| **NEW** `wave5_generality_proof.md` | **Do not create yet.** `004` §3 and the project's engineering posture are explicit: detailing unstarted future work is waste. M-5 exists as outcome + gate in `milestones.md`; the plan file is authored at M-4 exit |

### 7.8 `CLAUDE.md` / `AGENTS.md` / `README.md`

| File | Directive |
|---|---|
| `CLAUDE.md` §2 | **The "Pre-Development Hold" block is stale** — it reads *"Wave 0 is the only authorized next code change"* and *"No Wave 0 code has been written yet"*, while M-0 and M-1 are complete and M-2 is at re-gate round 4 `[VERIFIED contradiction]`. Replace with the current state: **M-0/M-1 green, M-2 in flight, Waves 3–4 authorized in sequence, M-5+ gated on the M-4 stop line.** A stale hold notice trains every future reader to ignore hold notices |
| `CLAUDE.md` §3 | Add `packs/math-formal/` (M-5) to the inventory; correct `layer0/` to its verified remaining contents and mark it *"deleted at M-3"* |
| `CLAUDE.md` §7 | Add ADRs `0077`–`0082` to the precedence list |
| `AGENTS.md` | Mirror all of the above — the two files must not drift |
| `README.md` | Update the reading order to the post-M-5 three-document path (`SPEC.md` → `docs/05_adr/INDEX.md` → `sprint_active.md`), marked as the *target* until M-5 lands it |

### 7.9 Execution order for the cascade

```text
M-2, week 1   H-1 H-2 H-9 H-10        cheap, local, reversible; H-9 FIRST so the rest is checked
M-2, week 1   2.6-A: write ADRs 0077–0082 → docs/05_adr/ ; update INDEX.md
M-2, week 1   2.6-B: RF-* namespace + alias table + RF-28 linter
M-2, week 2   SPEC.md §1.0 §1.1 §1.2 §7 + I-9/I-11    (§1.4 and §2.3 wait for M-3)
M-2, week 2   002 register §4.2/§4.2a/§4.2b ; sprint_active.md ; milestones.md
M-2, week 2   H-3 H-5 H-6 H-7 H-8 ; CLAUDE.md / AGENTS.md / README.md
M-2, exit     H-4 (Director ruling on vanguard_body_detailed.md)
M-3, entry    SPEC.md §2.3 rewrite (component graph + declared absence) — WITH the code, not before
M-3, exit     wave3_extensibility.md final ; layer0/ deleted ; stale-path linter re-run
M-4, exit     wave4 evidence bundle ; pyproject.toml version cut → 0.7.0    [DIRECTOR]
M-5           THE COLLAPSE: SPEC + ADR log + one board ; retire GAMMA and 002   (ADR-0082 D3)
```

> **The one rule that governs the order:** documentation that describes **shipped** behaviour is written *with* the code. Documentation that describes **decided** behaviour is written *before* the code. Nothing describes **hoped-for** behaviour at all.

---

## Appendix A · Forensic Verification Log (this pass)

Every row was re-executed against the working tree at `main` @ `733855b`.

| # | Claim | Method | Result |
|---|---|---|---|
| A-1 | Kernel within TCB budget | `python3 tools/linters/check_tcb_budget.py` | ✅ `TCB PASS: 1365 logical lines across 9 files (alarm above 1438)` — 73 LOC headroom |
| A-2 | Hollow trajectory | `cat -n vanguard/packages/runtime/trajectory.py` | ✅ **CONFIRMED LIVE** — `_ZERO_COST` at line 10, consumed at 53 (per-turn) and 75 (episode) |
| A-3 | `execution_digest` (`D_R`) never computed | grep across `vanguard/packages/` | ✅ **CONFIRMED** — no assignment anywhere; `assemble_trajectory` omits the key entirely |
| A-4 | `layer0/` remaining contents | `find layer0 -name '*.py'` | ✅ 16 files: `compose/` (2) · `events/` (5) · `registry/` (8) · `__init__` (1). `kernel/`, `scheduler/`, `spi/` **gone** |
| A-5 | **Plugin FSM cannot ledger `VERIFIED`** | `sed -n '30,80p' layer0/registry/lifecycle.py` | ✅ **NEW FINDING** — `_EVENT` maps 5 of 7 states; `DISCOVERED`/`VERIFIED` → `None`; `_go()` guards `if kind is not None:` and emits nothing |
| A-6 | Only five `PLUGIN_*` event kinds exist | grep `domain/wire/types_gen.py`, `domain/ledger/events.py` | ✅ `PLUGIN_{RESOLVED,ACTIVATED,QUIESCED,RETIRED,FAULTED}` — no `DISCOVERED`, no `VERIFIED` |
| A-7 | **Two live manifest dialects** | read `schemas/mhf/harness_manifest.schema.json` + `domain/artifacts/manifest.py` + `agency/manifests/vg-code-default/manifest.json` | ✅ **NEW FINDING** — schema freezes 5 fixed slots; `domain/` already types `components` as a named map; `vg-code-default` ships 7 named components |
| A-8 | Fixed-slot `harness.yaml` on disk | `cat packs/code-default/harness.yaml` | ✅ Exactly `planner · context · memory · evaluation · toolkits[4] · model_routes[3]` |
| A-9 | Writer authority table live | `grep -A40 PRIVILEGED_KIND_OWNERS runtime/ledger_emitter.py` | ✅ 22 privileged kinds mapped; `VerdictRecorded → {evaluator_gateway}`; `Plugin*` → `{registry}`; orchestrator owns nothing |
| A-10 | Sealed-membership check live in the kernel | `cat vanguard/packages/kernel/policy.py` | ✅ Step 1b present under `ADR-0067`; `attenuation.py:183` auto-seals when `request.actions < parent.actions` |
| A-11 | **`spawn()` docstring is stale** | read `agency/episode/engine.py:531-572` | ✅ **NEW FINDING** — claims the `ADR-0054` kernel gap is open; `ADR-0067` closed it. Corrected by `ADR-0080` C3, pinned by `RF-27` |
| A-12 | Classifier fails closed | `cat vanguard/packages/kernel/classifier.py` | ✅ Unknown principal ⇒ widens; unheld action ⇒ widens; depth overrun ⇒ widens; undecidable resource pair ⇒ widens (`K-48`) |
| A-13 | Five frozen SPIs, no sixth | `cat vanguard/packages/ports/spi.py` | ✅ `IPlanner`, `IContextManager`, `IToolkit`, `IMemoryEngine`, `IEvaluationGate` — exactly five |
| A-14 | **`F-*` namespace collision** | `grep -o "F-[0-9]\+" docs/04_annex/KERNEL.md \| sort -u` vs `002` §4.2 | ✅ **NEW FINDING** — `F-01…F-25` in both, different meanings. `ADR-M0-02` names only `I-*`, `ADR-*`, `S-M*` |
| A-15 | `CostVector` excludes structural dims | read `schemas/mhf/trajectory.schema.json` | ✅ `additionalProperties: false` over `{usd_micros, tokens, bytes, millis}` — the algebra is already schema-enforced |
| A-16 | `check_markdown_links.py` scans two files | `grep DOC_GLOBS tools/linters/check_markdown_links.py` | ✅ Third glob (`docs/agile/sprint6B/*.md`) matches nothing |
| A-17 | `DELETE.md` is 0 bytes; `docs/08_workflows/` empty | `ls -la` | ✅ Both confirmed |
| A-18 | Duplicate research pair | front-matter comparison | ✅ `RESEARCH_THEORETICAL_SYNTHESIS.md` and `_B.md` both `id: REF-06-M5`, identical titles |
| A-19 | `CLAUDE.md` hold notice is stale | read `CLAUDE.md` §2 vs `sprint_active.md` | ✅ Says *"No Wave 0 code has been written yet"*; M-0/M-1 are complete and M-2 is at re-gate round 4 |
| A-20 | `CapabilityRevoked` has no emitter | grep `vanguard/packages/` | ✅ In the catalog; no production emitter; no falsifier. Registered `RF-55`, M-7 |

**Not examined** (stated so the boundary of the finding is honest): the TypeScript client lattice (`vanguard/clients/`); the full test suite was not re-executed; `benchmarks/` and `lab/` were not exercised; no runtime or E2E execution was performed; `docs/04_annex/KERNEL.md` was read for the `F-*` namespace only, not audited rule-for-rule.

---

## Appendix B · New Findings Not Present in Any Prior Review

| # | Finding | Severity | Disposition |
|---|---|---|---|
| **B-1** | **The plugin lifecycle FSM cannot ledger `DISCOVERED` or `VERIFIED`.** `_EVENT` maps 5 of 7 states; `_go()` emits nothing for the other two. `VERIFIED` is where the capability-ceiling policy check happens — the most security-relevant transition leaves no evidence. **The M-3 exit gate ("every transition ledgered") is unsatisfiable against the closed 56-kind catalog.** | **HIGH** — blocks M-3 as specified | `ADR-0081` D3 (Director escalation, ruled). `RF-35`. Two new event kinds; 56 → 58 |
| **B-2** | **Two live manifest dialects, and the general one already exists in `domain/`.** `HarnessManifest.components` is already a named component map; `vg-code-default/manifest.json` already ships seven. T-1 is a **convergence**, not a build — materially cheaper than `005` §W1 assumed. Board task `3.2-C` ("one manifest parser") is the T-1 vehicle and is labelled `DEV-LOCAL`. | **HIGH** — a `DEV-LOCAL` task is the vehicle for a `D_H` pre-image decision | `ADR-0077` D6. Re-label `3.2-C` → `DIRECTOR`, fold into 3.3 |
| **B-3** | **`F-*` falsifier namespace collision.** `F-01…F-25` exist with different meanings in `KERNEL.md` and the `002` register; `ADR-M0-02` does not list `F-*` at all. Undetected because no tool checks identifier uniqueness across authority tiers. | **MEDIUM** — a reviewer citing "F-07" means one of two different things | `ADR-0082` D5. `RF-*` for the register; `RF-28` linter |
| **B-4** | **`D_R` (`execution_digest`) is never computed anywhere in the tree.** The identity trinity is *specified* three ways and *emitted* one way. A corpus with `D_H` but no `D_R` cannot distinguish "same harness, different model build" from "same run" — silently invalidating every router experiment. | **HIGH** — invalidates the M-10 measurement basis | `ADR-0078` D3 defines it constructively. `RF-23` clause 6 |
| **B-5** | **The `spawn()` docstring reports a kernel gap that `ADR-0067` closed.** A stale comment inside the TCB's nearest neighbour mis-models the kernel for every reviewer who trusts it. | **MEDIUM** — correctness of understanding, not of code | `ADR-0080` C3; `RF-27` pins the behaviour with the engine-side refusal disabled |
| **B-6** | **Evaluator reachability is ambient, not selector-gated.** `adapters/evaluators/client.py` is composition-wired. Under `agent.spawn`, a planner-authored child inherits reachability the parent never explicitly attenuated — violating the swarm-era Attenuated Reachability property (S-2). | **MEDIUM** — latent until M-6, structural then | `ADR-0080` D5; `RF-54` at M-6 |
| **B-7** | **`CapabilityRevoked` is catalogued with no production emitter and no falsifier.** The 2026 execution-security literature names mid-lease revocation as a live threat class. Unreachable today under I-11; reachable the moment M-7 enables concurrency. | **LOW now / MEDIUM at M-7** | `RF-55` at M-7 |
| **B-8** | **`check_markdown_links.py` validates two files while reporting `LINK PASS`.** Same defect class as `F-18`. It is why four dead ADR links survived CI. | **MEDIUM** — a gate manufacturing false confidence | H-9, fix in M-2 **before** six new ADRs land |
| **B-9** | **`CLAUDE.md`'s Pre-Development Hold block is stale**, asserting no Wave-0 code exists while M-0/M-1 are complete. A stale hold notice trains readers to ignore hold notices. | **MEDIUM** — process integrity | §7.8, M-2 week 2 |
| **B-10** | **The M-4 nine-row gate's row 8 accepts a hollow trajectory.** "Schema-valid `mhf.trajectory/1`" is satisfied by a content-free record — so **the stop line could be passed with an unusable corpus.** | **HIGH** — the stop line's own definition has the gap it exists to prevent | Row 8 → *"schema-valid **and populated**"*; `RF-23` + `RF-48` |

---

## Appendix C · External Sources

Consulted during the mandated SOTA research pass (§1.2).

**Harness engineering**
- [Agent Harness Engineering: A Survey](https://picrew.github.io/LLM-Harness/main.pdf)
- [Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses](https://arxiv.org/abs/2604.25850)
- [Harness-Bench: Measuring Harness Effects across Models in Realistic Agent Workflows](https://arxiv.org/html/2605.27922v1)
- [From Question Answering to Task Completion: A Survey on Agent System and Harness Design](https://arxiv.org/pdf/2606.20683)
- [Harness as an Asset: Enforcing Determinism via the Convergent AI Agent Framework (CAAF)](https://arxiv.org/pdf/2604.17025)

**Stigmergic / shared-state multi-agent coordination**
- [CodeCRDT: Observation-Driven Coordination for Multi-Agent LLM Code Generation](https://arxiv.org/pdf/2510.18893)
- [Beyond Text-Passing: Shared Cognitive Substrates for Multi-Agent LLM Coordination](https://openreview.net/forum?id=RRIw2L4Z1g)
- [PatchBoard: Schema-Grounded State Mutation for Reliable and Auditable LLM Multi-Agent Collaboration](https://arxiv.org/pdf/2605.29313)
- [Token Coherence: Adapting MESI Cache Protocols to Minimize Synchronization Overhead in Multi-Agent LLM Systems](https://arxiv.org/pdf/2603.15183)

**Capability sandboxing, provenance, execution security**
- [From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents](https://arxiv.org/pdf/2606.04990)
- [Lingering Authority: Revocable Resource-and-Effect Capabilities for Coding Agents](https://arxiv.org/pdf/2606.22504)
- [The Balkanization of Execution-Security Research for AI Coding Agents: Isolation, Access Control, and TOCTOU Vulnerabilities](https://arxiv.org/pdf/2607.05743)

**Active inference, credit assignment, trajectory RL**
- [Expected Free Energy-based Planning as Variational Inference](https://arxiv.org/html/2606.20658)
- [Active Inference as a Convex Markov Decision Process](https://arxiv.org/pdf/2607.20152)
- [ASTRA: Automated Synthesis of agentic Trajectories and Reinforcement Arenas](https://arxiv.org/abs/2601.21558)
- [Beyond Trajectory-Level Attribution: Graph-Based Credit Assignment for Agentic Reinforcement Learning](https://arxiv.org/abs/2605.26684)
- [AstraFlow: Dataflow-Oriented Reinforcement Learning for Agentic LLMs](https://arxiv.org/html/2605.15565v1)

**Declarative composition graphs**
- [AgentFlow: Building Agent Dependency Graphs for Static Analysis of Agent Programs](https://arxiv.org/html/2607.01640)
- [Graph-Based Agent Workflow Orchestration in Production: The 2026 Landscape](https://zylos.ai/research/2026-04-14-graph-based-agent-workflow-orchestration-production/)
- [Declarative Data Services: Structured Agentic Discovery for Composing Data Systems](https://arxiv.org/abs/2605.20690)

---

## Closing Statement of the Leadership 7

**What `v0.6.1` locks that `v0.6.0` did not.** `v0.6.0` locked the *primitives*: authority as a reference monitor, state as fold, evidence as an exterior signature, identity split three ways, recursion as one attenuated delegation. `v0.6.1` locks the *surfaces those primitives are reached through*: a composition algebra that can name more than one cognitive component (`ADR-0077`), a corpus rich enough to learn from (`ADR-0078`), guardrails that may be declared absent but never forged (`ADR-0079`), a delegation verb whose design is fixed before its implementation is permitted (`ADR-0080`), a plugin lifecycle whose every transition leaves evidence (`ADR-0081`), and two standing claims made refutable rather than assumed (`ADR-0082`). **`v0.6.0` made AETHER trustworthy. `v0.6.1` makes it general.**

**Wave 4's stop condition is unchanged and non-negotiable.** Nine rows on one uninterrupted real run with zero human intervention. Row 8 is *strengthened*, not widened — a hollow trajectory could have passed the original wording, and the stop line must not contain the defect it exists to prevent. `agent.spawn`, concurrency, Pack #2, and all of M-5 through M-10 remain **out of implementation scope** until the gate is green. Any temptation to widen scope in order to make the run pass is escalated to the Director, not absorbed by the sprint.

**M-5 through M-10 exist as outcomes and gates only.** No sprint-level detail is authorised beyond what §4.2 records. Detailing unstarted work is waste, and worse, it manufactures the appearance of a plan where only an intention exists. `wave5_generality_proof.md` is authored at M-4 exit and not before.

**What a developer reads first, today:** `README.md` → `docs/SPEC.md` → `docs/05_adr/INDEX.md` (ADRs `0069`–`0082`) → `docs/03_sprints/sprint_active.md` → **this document, §6, for the implementation bridge.** After M-5's collapse, the first four become three and this document retires into git history along with the rest of the review corpus.

**The single sentence this body would keep if it could keep only one:**

> **Make the corpus learnable and the composition surface general — in that order, before the stop line — because everything after M-4 consumes one or the other, and neither can be repaired retroactively.**

---

*Prepared as an independent leadership review. This document is **advisory** and amends nothing. Law remains [`docs/SPEC.md`](docs/SPEC.md) → [`docs/05_adr/`](docs/05_adr/) → [`docs/04_annex/`](docs/04_annex/). Every ruling in §1–§2 becomes binding only through the corresponding append-only ADR in §3, committed with a Director signature and carrying its bound falsifier. No specification file, ADR, or source file was modified in producing this report.*
