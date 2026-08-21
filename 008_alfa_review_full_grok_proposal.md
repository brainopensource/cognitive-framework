# 008 — ALFA MASTER (TIER S+): Adaptive Pareto Harness on an Unforgeable Stigmergic Substrate

**Leadership 7 definitive synthesis of proposals `002`–`008`**

| Field | Value |
|---|---|
| **Document ID** | `008_alfa_review_full_grok_proposal.md` |
| **Class** | **TIER S+ master architecture.** Supersedes prior Alfa draft in this same path. Does **not** amend SPEC or ADRs. |
| **Prepared by** | The Leadership 7 — Engineering Director · CTO · CIO · Principal Staff Engineer · Principal Systems Architect · Tech Lead · PhD AI Specialist |
| **Date** | 2026-08-21 |
| **Baseline** | working tree `e84dfda`. **`[VERIFIED]`** = inspected on disk this programme. **`[CITED]`** = from living law/docs. **`[ABSENT]`** = briefing path not in this tree. |
| **Synthesised from** | `002_beta` (Gem) · `004_delta` (GLM-5.3) · `005_epsilon` (DSv4) · `006_fi` (GPT-sol) · `007_zeta` (Opus) · prior `008_alfa` (Grok) |
| **Scope** | v0.6.1 → v1.0.0 · M-0 … M-10 · draft ADRs **0077–0082** (canonical numbering **locked in this file**) |
| **Authority** | Advisory until ADRs are filed under `docs/05_adr/` with a Director signature. Law remains `docs/SPEC.md` → `docs/05_adr/` → `docs/04_annex/`. |
| **Hard constraint** | This write updates **only** this file. No SPEC, ADR, or source file is edited. |

---

## Table of Contents

- [§0 · Ten-Minute Executive Briefing](#0--ten-minute-executive-briefing)
- [§0.5 · Synthesis Ledger — what was kept from each proposal](#05--synthesis-ledger--what-was-kept-from-each-proposal)
- [§1 · Executive Rulings & the Adaptive Pareto Paradigm](#1--executive-rulings--the-adaptive-pareto-paradigm)
- [§2 · Adjudication of T-1 … T-9](#2--adjudication-of-t-1--t-9)
- [§3 · Drafted ADR Catalog `0077`–`0082`](#3--drafted-adr-catalog-00770082)
- [§4 · Version Ladder & Milestones](#4--version-ladder--milestones)
- [§5 · Theories, Algorithms & Mathematics](#5--theories-algorithms--mathematics)
- [§6 · Zero-Guesswork Developer Bridge](#6--zero-guesswork-developer-bridge)
- [§7 · Hygiene & Document Cascade](#7--hygiene--document-cascade)
- [§8 · Refused Alternative — Obligation Market (harvest only)](#8--refused-alternative--obligation-market-harvest-only)
- [Appendix A · Forensic Log](#appendix-a--forensic-log)
- [Appendix B · Master Findings](#appendix-b--master-findings)
- [Appendix C · External Sources](#appendix-c--external-sources)

---

## §0 · Ten-Minute Executive Briefing

### 0.1 One-paragraph verdict

AETHER already has **A — Authority** (S0–S12, TCB ≤ 1438, fail-closed ceilings, single writer) and **D — Digest** (\(D_H \neq D_R \neq D_X\)). It does not yet have **B — Bundle** (a *wired* composition graph) or **C — Corpus** (learnable trajectories). The 2026 SOTA that matters is not a second swarm engine. It is an **Adaptive Pareto harness**: a versioned policy that ranks feasible (cost, tokens, latency, quality) points, projects a stigmergic State Plane into a bounded context, and compounds by compiling repeated signed successes into **macro-tools**. That harness is **pack + policy + graph**. The kernel does not learn, does not chat, and does not grade itself.

### 0.2 The architecture in one diagram

```text
                         ADAPTIVE PARETO CONTROLLER  (policy, D_H-hashed)
                         profiles α Flash · β Balanced · γ Deductive · δ Escalate
                                          │  ranks only ≼-feasible R
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ STIGMERGIC STATE PLANE  W = (A artifacts, H hypothesis projection,          │
│                              E evidence ledger, T telemetry)                 │
│  State = fold(events)  ·  SQLite WAL + FULL sync  ·  project_id total order │
│  Agents NEVER address peers. They append/read.  Ops ∈ Θ(c N), not N(N−1).  │
└──────────────────────────────┬──────────────────────────▲───────────────────┘
                               │ B_θ informational bottleneck                  │
                               │ (context compiler L1–L5, VFE-minimising slice)│
                               ▼                                               │
                    observe → propose → authorize → effect → receipt → evaluate
                               │ S0–S12 reference monitor (A)     │ UID 10002 V │
                               │ UID 10001 worker                  │ unsigned=illegal
                               ▼
                    mhf.trajectory/1 writer with NOVA-1 content
                               │
                               ▼
         FLYWHEEL T0 memo → T1 macro-tool → T2 skill/router → T3 DPO/harness
         (each tier requires the evidence controls of all lower tiers)
```

### 0.3 Six binding rulings (canonical ADR map)

| # | Ruling | ADR | Lands |
|---|---|---|---|
| **R-1** | Un-hollow the corpus. No silent zeros. `cost_absent_reason` or measured \(\mathbf{R}^{\mathrm{add}}\). Populate \(D_R\). `/1` rows that fail content rules are `legacy_incomplete`. | **0078** | v0.6.1 / M-2 |
| **R-2** | `mhf.manifest/2` = named **instances + bindings**. Path bags and five-slots are frontends. `REGISTERED_COMPONENT_CONSUMERS` / `ROLE_KIND` must open to graph ids. | **0077** | v0.6.2 / M-3 |
| **R-3** | Absent-vs-forged. `unattributable_for_promotion` is **derived**. Unsigned verdicts illegal always. | **0079** | v0.6.2 / M-3 |
| **R-4** | `agent.spawn` design-locked; **kernel delta 0 until M-4**; implement M-6; close action∈scope in kernel. | **0080** | design v0.6.1 · code v0.8.0 |
| **R-5** | Absorb `layer0/`; add `PluginDiscovered` + `PluginVerified`; NOVA-4; delete fork including `pyproject` `layer0*`. | **0081** | v0.6.2 / M-3 |
| **R-6** | Loop is mechanism (UTL-1). NOVA-2 is **M-3 entry**. Pareto profiles, macro-tools, DPO, McNemar are **M-10 consumers** of R-1, never writers of `VerdictRecorded`. | **0082** | NOVA-2 v0.6.1 · UTL published M-3 |

### 0.4 Stop lines (Director)

1. **M-4 nine rows, one uncheated run.** Widening the run to make it pass is escalation, not a patch.
2. Package version stays `0.4.5b1` until M-4, then **v0.6.3**.
3. **No kernel LOC growth** in v0.6.1/v0.6.2. Spawn ≤ 40 logical LOC at M-6, TCB still ≤ 1438.
4. **I-11** until NOVA-2 green **and** an M-7 measurement ADR.
5. Adaptive Pareto, blackboard \(\mathcal{W}\), bottleneck \(\mathcal{B}_\theta\), flywheel — **all map onto existing planes**. They are not a third runtime.
6. `research_Harness_Builder_Framework.md` (Redis/NATS/Chroma/K8s) is **REJECTED as architecture**.
7. MicroVM fashion is **M-9 measurement**, not a foundation rewrite.

---

## §0.5 · Synthesis Ledger — what was kept from each proposal

| Source | IMPORTED into this master | REFUSED / corrected |
|---|---|---|
| **002_beta (Gem)** | Adaptive Pareto profiles α–δ; informational bottleneck \(\mathcal{B}_\theta\); stigmergic blackboard as **projection of W**; compounding flywheel; **macro-tool token collapse**; unified primitives across coding vs general tasks; as-built `tier_escalation.py` as the δ-profile ancestor | `stigmergic_blackboard: bool` in schema (coordination is the ledger, not a flag); §11 as a competing engine; treating CLI wrap as the generic harness |
| **004_delta (GLM)** | Topology-cost SOTA (chatter is the MAS cost driver); EnvHarness/ESOpt “corpus-first”; explicit zeros only with `fingerprint: none`; NOVA-4 six negatives; Pack #2 as I-7 gate | ADR numbering that assigned **0078 = guardrails** (conflicts with corpus-first clock); citing `[ABSENT]` research files as consumed |
| **005_epsilon (DSv4)** | Clearest version ladder (v0.6.1 correction → … → v1.0.0); “import DeepSeek flatness, refuse no privileged core”; NOVA-1/2/3 inside M-2; Wave-3 rebalance | ADR packing that made 0079=spawn / 0080=loop / 0081=NOVA (forks the catalog); thin Pareto |
| **006_fi (GPT-sol)** | **Primary forensic twin:** `REGISTERED_COMPONENT_CONSUMERS`, `ROLE_KIND`; honest mesh vs \(O(cN)\); VFE ≠ EFE; never backfill zeros; `legacy_incomplete`; PluginDiscovered/Verified; Pareto **safety gate** on promotion; T0–T3 compounding ladder; preference-pair certificate; spawn JSON outline | Filing `trajectory/2` as a **breaking** schema in M-2 (keep `/1` + content rules + `legacy_incomplete` reader instead — cheaper, same invariant) |
| **007_zeta (Opus)** | FSM cannot ledger DISCOVERED/VERIFIED; \(D_R\) never assigned; F- vs RF- namespace; recorded Leadership dissents; 40-LOC spawn budget; UTL-1 year-window; M-3 gated on NOVA-2 | **“The graph already exists”** — it is a named **path bag**; Obligation Market as replacement for the turn (harvest `witness_type` only) |
| **008_alfa prior** | Ghost briefing G0; F-12 false green; TableWorld ≠ Pack #2; engine-documented spawn hole; `pyproject` still ships `layer0*` | Under-weight Pareto/macro-tools relative to 002/006 |

**Canonical ADR numbering (this file wins over 004/005):** 0077 graph · 0078 corpus · 0079 absent-vs-forged · 0080 spawn · 0081 layer0 · 0082 loop+NOVA-2.

---

## §1 · Executive Rulings & the Adaptive Pareto Paradigm

### 1.1 Leadership 7 — consensus and recorded conditions

| Officer | Mandate | Condition / dissent |
|---|---|---|
| **Engineering Director** | Ratify R-1…R-6. M-4 inviolable. Product cut v0.6.3. G0 hygiene may land before M-4 (false links are not “doc surgery”). | Kernel diff before M-4 **voids** the nine-row bundle (`ADR-0080`). |
| **CTO** | Moat = separability × content-addressed \(D_H\) × unforgeable corpus. 2026 harness-engineering literature is a **race on signal quality**. Pareto profiles are the product UX; the kernel is not a router. | External Terminal-Bench-class run is **M-5 (G8)**, not M-4 — measuring a pack before it loads through its lifecycle measures the wrong artifact. |
| **CIO** | Derived unattributability. Unknown price is not `$0`. `legacy_incomplete` never promotes. Preference pairs require two signed verdicts. | Manifest must not contain `promotable: true`. |
| **Principal Staff Engineer** | Priority **G0 → G1 hollow corpus → G2 wired graph → G9 plugin FSM → G5 NOVA-2 → G4 guardrails → G3 spawn**. F-08 stale. F-12 is not I-9. | Register `002` still says Wave 0 not started — banner at M-5, not a silent rewrite now. |
| **Principal Systems Architect** | Lattice unchanged. Graph parsed in `domain/`, resolved in `runtime/`, invisible to `kernel/`. Map \(\mathcal{W},\mathcal{B}_\theta,\mathcal{L},\mathcal{V}\) onto WAL, context compiler, 6D reservation, UID-10002. | Mutation-score TCB replacement **M-5**; LOC gate remains living until then. |
| **Tech Lead** | Every ADR: schema + FSM row + named test + negatives. **M-3 does not open on red/skipped NOVA-2.** | `PluginDiscovered`/`PluginVerified` = Director escalation, shipped inside `ADR-0081` only. |
| **PhD AI Specialist** | VFE is **inference**; EFE is **action selection**; Pareto is **feasibility ranking**. Macro-tools are untrusted toolkits until promotion. LLM-as-judge is not a `VerdictRecorded` writer. | `attribution.prefix_hits` optional M-2, required for M-10 promotion rows. |

**Standing mandate:**

> Ship **C** (learnable corpus) and **B** (wired graph) before any consumer of either. An Adaptive Pareto controller over `_ZERO_COST` is a thermostat on a disconnected sensor.

### 1.2 SOTA 2026 — concessions and refusals

**(a) Harness engineering is ~⅔ of MAS intelligence.** Concede: \(D_H\) is the genome. Refuse: wrapping Claude Code / Agents SDK as AETHER.

**(b) Stigmergy beats mesh chatter.** Concede: agents coordinate through environmental traces. **006 correction imported:** a full mesh has ≤ \(N(N-1)\) directed messages; **sparse peer graphs can be \(O(N)\)**. AETHER’s bound is: if each agent does at most \(c\) ledger ops per round, coordination is \(\Theta(cN)\). Do **not** claim “\(O(N^2)\) cannot exist here” as a complexity theorem — claim it as a **forbidden protocol** (no peer RPC). Contention/hot keys are M-9 measurements.

**(c) Capability + provenance.** Concede NVIDIA/microVM residual on shared-kernel bwrap. Refuse foundation rewrite. Provenance is the existing receipt DAG, not a second product.

**(d) Trajectories / ASTRA / DMPO / TRACE / CAR.** Concede verifiable arenas and turn-level credit. Refuse frozen-LLM gold; refuse ASTRA env-synth inside the kernel (packs only).

**(e) DeepSeek flat surface.** Import flatness. Permanently refuse “no privileged core.”

### 1.3 Four primitives — mapped to as-built AETHER (002 imported, 006 bound)

| Primitive (002) | AETHER binding **`[VERIFIED]`** | Must not become |
|---|---|---|
| Blackboard \(\mathcal{W}=\langle\mathcal{A},\mathcal{H},\mathcal{E},\mathcal{T}\rangle\) | \(\mathcal{A}\) blob/workspace · \(\mathcal{H}\) **projection** of events (ADR-0003: not a graph DB) · \(\mathcal{E}\) WAL + signed verdicts · \(\mathcal{T}\) NOVA-1 cost vectors | CRDT, NATS, MESI cache, second event bus |
| Bottleneck \(\mathcal{B}_\theta\) | `agency/context/compiler.py` + L1–L5 + `skill_index.py` char budget | Kernel-resident “free energy optimiser” |
| Lease \(\mathcal{L}\) | 6D `Reservation` (ADR-M0-07): additive \(\{usd, tokens, bytes, millis\}\) vs structural \(\{turns, depth\}\) | A seventh speculative dimension; auto-renew without S7 |
| Oracle \(\mathcal{V}\) | UID 10002 daemon + gateway-only `VerdictRecorded`; pack oracles | In-engine critic as judge; authored `promotable` |

**As-built δ-profile ancestor:** `runtime/tier_escalation.py` already escalates Free→Cheap→Frontier on **stop reason**, never on self-grade. Pareto profiles **version that policy**; they do not add a MetaLoopEngine (ADR-M0-12).

### 1.4 A-B-C-D scored on disk

| | Plane | Status | This mandate |
|---|---|---|---|
| **A** | Decision / kernel | Generic | Freeze until M-6 |
| **B** | Composition | **Three surfaces:** (1) `mhf.harness/1` five slots; (2) JSON **path bag**; (3) `REGISTERED_COMPONENT_CONSUMERS` + `ROLE_KIND` **hard-coded roles** | `mhf.manifest/2` with **bindings**; open the two tables |
| **C** | State/Evidence | Hollow `_ZERO_COST`; F-12 keys-only; \(D_R\) unassigned | ADR-0078 |
| **D** | Identity | Locked in law; \(D_R\) missing in writer | Compute \(D_R\) at episode complete |

---

## §2 · Adjudication of T-1 … T-9

### 2.1 T-1 — Manifest: slots vs graph

**`[VERIFIED]`** Five-slot YAML; domain `components` as sorted `role → paths`; `vg-code-default/manifest.json` seven names; **no edges**; `loader.py:31-40` fail-closed on unknown roles; `compose.py:39-48` `ROLE_KIND` table.

**Ruling: R-2 / ADR-0077.** Option B with 008’s correction: a **named bag is not a graph**. Product is `components` + `bindings`. v1 YAML is a **compiler frontend** that synthesises conventional nodes and edges (`context→planner`, `planner→toolkit[i]`, `evaluation→self.episode`).

**Falsifiers:** RF-22 (two planners + aggregator, \(D_H\) edge-sensitive), RF-23 (Pack #1 frontend), RF-23b (unknown role currently denied — after M-3, unknown **spi** denied, unknown **instance id** allowed).

### 2.2 T-2 — Spawn

**`[VERIFIED]`** `EpisodeEngine.spawn` ~531; `ProposalKind.SPAWN`; docstring: policy does not check `action ∈ requested_scope.actions`.

**Ruling: R-4 / ADR-0080.** Design now (006 JSON outline imported). Code M-6. Engine spawn remains the semantic reference through M-5. RF-27 closes the kernel hole.

### 2.3 T-3 — Guardrails

**Ruling: R-3 / ADR-0079.** Declared absence hashed into \(D_H\). Derived `unattributable_for_promotion`. Seven non-negotiables: writer table · lineage · fail-closed selectors · ledger-as-truth · attenuation · signature on claimed verdicts · JCS-only bytes.

### 2.4 T-4 — Hollow corpus (NOVA-1)

**`[VERIFIED]`** `trajectory.py` 10/53/75; F-12 does not fail zeros.

**Ruling: R-1 / ADR-0078.** M-2 now. 006 import: unknown money ≠ 0; episode totals reconcile with turns; aborted-before-infer uses `cost_absent_reason`. **Do not** mint `mhf.trajectory/2` in M-2 (schema churn on the stop-line corpus). Keep `/1`; mark non-compliant historical rows `legacy_incomplete` in a **reader** flag (derived, not a silent rewrite of WAL bytes).

### 2.5 T-5 — layer0

**`[VERIFIED]`** compose + registry + events remain; no `from layer0` under `vanguard/packages/`; `_EVENT` misses DISCOVERED/VERIFIED; `pyproject` still `include layer0*`.

**Ruling: R-5 / ADR-0081.** Absorb, parity, NOVA-4, delete. New kinds are Director-gated here.

### 2.6 T-6 — Loop as mechanism

**Ruling: R-6 / ADR-0082.** UTL-1 + UTL-F (12-month named counterexample). M-8 topologies (debate, critic, evolutionary, stigmergic-swarm) are the structured half of the challenge — **zero** `engine.py` topology `if`s.

### 2.7 T-7 — NOVA-2

**Ruling:** M-2; **hard entry to M-3**. Green ⇒ M-7 is a scheduler refactor. Red ⇒ stop inventing worker-pool abstractions.

### 2.8 T-8 — Docs

Collapse to Clean Triad **post-M-4**. Exception: G0 broken links now.

### 2.9 T-9 — Five SPIs

Freeze through M-4. Revisit M-9. A sixth SPI needs two implementations, a wire contract, and net complexity deletion — “useful type” is insufficient (006).

---

## §3 · Drafted ADR Catalog `0077`–`0082`

Drafts. Bind only when filed. Each states reversal (ADR-0000 / 0018 / 0074).

---

### ADR-0077 — Named Component Graph (`mhf.manifest/2`)

**Extends:** ADR-0005, 0059, 0070, 0072, 0076. **Lands:** M-3.

**Decision.**

1. Normative API is `mhf.manifest/2`: `components` map (id → `{spi, ref, config, ceiling?}`) + `bindings` (`from`, `to`, `kind ∈ {context, observe, evaluate, spawn_grant, route}`).
2. `mhf.harness/1` is a frontend through M-4.
3. \(D_H\) = JCS-SHA-256 of resolved graph (pinned refs, prompt/policy bytes, ceiling intersection, **bindings**, routes). `episode_id` ∉ \(D_H\).
4. Open `REGISTERED_COMPONENT_CONSUMERS` and `ROLE_KIND` to instance ids; SPI ∈ five frozen names (ADR-M0-03).
5. Kernel never sees YAML. Cycles on `evaluate` forbidden; `observe` cycles bounded by `budget.turns`.
6. Pareto `profile` is an ordinary component or policy artifact hashed into \(D_H\), not a kernel enum.

**Falsifiers:** RF-22, RF-23, RF-23b.

**Reversal.** Topology requiring a sixth SPI or kernel `if domain==…`, with a failed composition.

---

### ADR-0078 — Trajectory Content (NOVA-1); I-9 operationalised

**Extends:** ADR-0071, 0074. **Lands:** M-2.

**Decision.**

1. Writer populates per-turn and episode `CostVector` from governor commits + model usage.
2. `cost_absent_reason ∈ {null, cassette, no_model, aborted_before_infer, fake_port}`. Exactly one of (non-zero additive dimension **or** reason).
3. Unknown *price* is `price_status: unknown`, never `usd_micros: 0` pretending measurement (006).
4. Turn `model: {provider, model_id, fingerprint}` or null+reason.
5. `millis` = charged time.
6. Compute \(D_R = H(D_H \parallel runtime \parallel env \parallel model_id \parallel oracle_id)\) at flush (007: currently **unassigned**).
7. Strengthen F-12 → RF-12b/c. Kernel annex `F-12` (budget deny) stays annex-local.
8. Reader marks content-fail rows `legacy_incomplete`; promotion consumers drop them.
9. `attribution.prefix_hits` optional now; required on M-10 promotion rows.

**Falsifiers:** RF-12b, RF-12c, RF-12d (`execution_digest` present on completed model episodes).

**Reversal.** An environment with neither usage nor attachable reason that still writes promotion-eligible rows — forbidden; do not write those rows.

---

### ADR-0079 — Absent vs Forged

**Extends:** ADR-0004, 0071, 0072. **Lands:** M-3.

**Decision.** `evaluation` / `sandbox_tier` / `approval_policy` MAY be JSON `null`. Compose hashes the choice. Trajectories get `verdict: null` and derived `unattributable_for_promotion=true`. Gateway still refuses unsigned bodies. Promotion drops unattributable rows.

**Falsifiers:** RF-24, RF-25.

**Reversal.** A pack whose only oracle cannot be declared as a plugin **and** cannot run unattributable — then T-9 SPI review, not a forged pass.

---

### ADR-0080 — Capability-mediated `agent.spawn` (design lock)

**Extends:** ADR-0070, 0011, 0012. **Design:** v0.6.1. **Code:** M-6.

**Decision.**

1. Verb `agent.spawn`, sink `privileged`. Descriptor binds objective digest, entrypoint, context refs, requested capabilities, 6D sublease, `workspace_mode`.
2. Child ≼ parent; additive conservation; `depth_child = depth_parent+1`; sibling depths not summed.
3. No kernel spawn diffs before M-4 exit.
4. M-6: dispatch through S0–S12; **`request.action ∈ granted_scope.actions`**; planner proposes, does not call `EpisodeEngine.spawn` as a Python privilege.
5. TCB Δ ≤ 40 LOC.
6. Untrusted child returns; failure never upgrades trust (006).

**Falsifiers:** RF-26, RF-27, RF-28 (process: empty `git diff kernel` at M-4).

**Reversal.** Same as ADR-0070.

---

### ADR-0081 — Absorb layer0; NOVA-4; delete

**Extends:** ADR-0069, 0072, M0-13. **Lands:** M-3.

**Decision.** Move registry/compose into `runtime/`; add `PluginDiscovered`, `PluginVerified` to schema, codegen, writer table (`registry`); parity vs `test/layer0`; NOVA-4; delete `layer0/` and `layer0*` packaging; `in_process` still JSON-RPC.

**NOVA-4:** unknown-ref fails at compose · empty ceiling denies · registry-exclusive Plugin* · faulted cell cannot stay active · `in_process` needs explicit grant · frozen composition immutable.

**Falsifiers:** RF-29, RF-30, RF-33…RF-37.

**Reversal.** Parity red that would drop a security property — repair packages twin; do not keep two lives.

---

### ADR-0082 — UTL-1; NOVA-2; Pareto is policy not kernel

**Extends:** ADR-0003, 0070, 0073. **Lands:** NOVA-2 M-2; UTL sentence M-3.

**Decision.**

1. **UTL-1.** Every shipped algorithm = spawn-topology + plugins over one loop. Loop is not a plugin.
2. **UTL-F.** Named failed composition within 12 months = ADR-0070 reversal evidence.
3. **NOVA-2.** Mid-turn after S8a → kill process → fresh process WAL → recovery → terminal + trajectory. Checkpoint is optimisation, not authority.
4. **NOVA-2 green is M-3 entry.** I-11 still lifts only at M-7.
5. Pareto α–δ profiles are **versioned policy artifacts** (hashed in \(D_H\)). They rank ≼-feasible \(\mathbf{R}\) points. They **must not** auto-renew leases or auto-promote (006 §12). Existing `tier_escalation.py` is the implementation seed for δ.

**Falsifiers:** RF-31, RF-32, RF-41 (profile cannot bypass S7).

**Reversal of UTL.** Successful UTL-F. **Reversal of NOVA-2-as-gate.** Director exception naming the coupling accepted.

---

## §4 · Version Ladder & Milestones

| Version | Milestone | Theme | Disk package |
|---|---|---|---|
| v0.6.0 | M-0/M-1 | Truth + trust spine | `0.4.5b1` |
| **v0.6.1** | **M-2** | One runtime + NOVA-1 + NOVA-2 + ADRs filed | `0.4.5b1` |
| **v0.6.2** | **M-3** | Graph + absent-vs-forged + layer0 gone | `0.4.5b1` |
| **v0.6.3** | **M-4 STOP** | Nine-row E2E | **`0.6.3`** |
| **v0.7.0** | **M-5** | Pack #2 math/deduction + Clean Triad collapse | `0.7.0` |
| **v0.8.0** | **M-6** | `agent.spawn` in S0–S12 | `0.8.0` |
| **v0.9.0** | **M-7+M-8** | Concurrency + declarative topologies | `0.9.0` |
| **v1.0.0** | **M-9+M-10** | Scale + Adaptive Pareto flywheel | `1.0.0` |

### 4.1 M-2 / v0.6.1 — Evidence & correction

**In:** M-1 green. **Out:** graph impl, layer0 delete, kernel spawn, Pack #2, DPO.

**Exit:** existing M-2 (F-16, reducers, no packages←layer0) · RF-12b/c/d · RF-31 · ADRs 0077–0082 **filed** · linters green · kernel Δ = 0.

**Also:** NOVA-3 `_PROC_PATTERN` from compiled ceiling (005).

### 4.2 M-3 / v0.6.2 — Extensibility

**Entry: M-2 including NOVA-2.** Graph + frontend · ADR-0079 · absorb/delete · seven plugin kinds · NOVA-4 · UTL paragraph in SPEC.

### 4.3 M-4 / v0.6.3 — Nine rows, one run

| # | Row |
|---|---|
| 1 | Real model (not stub planner) |
| 2 | Authorized effect (grant+lease) |
| 3 | Filesystem change, receipted |
| 4 | Sandbox UID 10001 |
| 5 | Exterior signed eval UID 10002 |
| 6 | WAL `SqliteEventStore` |
| 7 | Cold replay I-4 |
| 8 | Trajectory schema-valid **and** NOVA-1 contentful |
| 9 | One runtime authority |

Escalate scope creep. NOVA-5 = confirmation of row 8 on this run.

### 4.4 M-5 / v0.7.0 — Generality

**Pack #2 = Math & Formal Deductive Verification** (`packs/math-default/`). **Not TableWorld** (adapter already in-tree — would fake I-7). Zero diffs `domain/`+`kernel/`. Doc collapse. Optional TCB mutation pipeline. G8 external harness-effect measurement.

### 4.5 M-6 / v0.8.0 — Mediated spawn

RF-26, RF-27. Tree-search / hierarchy as **graph policy**.

### 4.6 M-7+M-8 / v0.9.0

M-7: independence groups, \(K \ll N\), I-11 lift ADR, stigmergy \(\Theta(cN)\) named in SPEC. M-8: debate, critic, evolutionary, stigmergic-swarm **fixtures** without engine edits.

### 4.7 M-9+M-10 / v1.0.0

M-9: IPC/ledger pressure; SPI freeze revisit; bwrap vs microVM **measured**. M-10: VFE/EFE policy, T0–T3 flywheel, Elo skills, DPO + McNemar + Pareto safety. **ADR-0083** (promotion protocol) files at M-5 design, executes M-10 — not in the 0077–0082 foundation set.

---

## §5 · Theories, Algorithms & Mathematics

> **M-10 implements this section.** Symbols MUST exist in the corpus from **M-2** (ADR-0078). VFE is not a kernel loop.

### 5.1 Six-dimensional tensor and Pareto order (006)

\[
\mathbf{R}=(r_{\$},r_{\mathrm{tok}},r_{\mathrm{B}},r_{\mathrm{ms}};\, r_{\mathrm{turns}},r_{\mathrm{depth}})
\in \mathbb{N}^4_{\mathrm{add}}\times\mathbb{N}^2_{\mathrm{struct}}.
\]

Feasibility is a **product partial order** — dollars are not added to tokens:

\[
\mathbf{R}_a \preceq \mathbf{R}_b \iff \bigwedge_j R_{a,j}\le R_{b,j}.
\]

Parent/child: additive dimensions conserve; `turn_i ≤ turn_p`; `depth_i = depth_p+1`. Overruns are committed, never clamped.

### 5.2 VFE vs EFE (006 correction of 002/007 conflation)

Belief update (perception):

\[
\mathcal{F}(\phi,\theta;\tau)
=\mathbb{E}_{q_\phi(s\mid\tau)}\big[\log q_\phi(s\mid\tau)-\log p_\theta(\tau,s)\big]
=\mathrm{KL}\big(q_\phi(s\mid\tau)\,\|\,p_\theta(s\mid\tau)\big)-\log p_\theta(\tau).
\]

Action selection (expected free energy), with preferred observations \(C\) = signed pass under remaining lease and no `KernelAlarm`:

\[
G(\pi)=\underbrace{\mathbb{E}_{q(o,s\mid\pi)}[\log q(s)-\log p(o,s)]}_{\text{epistemic + ambiguity}}
-\underbrace{\mathbb{E}_{q(o\mid\pi)}[\log p(\tilde o\mid C)]}_{\text{pragmatic}}.
\]

**Category error forbidden:** a weighted scalar “fitness” is not \(\mathcal{F}\). Feasibility \(\preceq\) is checked **first**. Among feasible \(\pi\), rank by Pareto on \((C,T,L,Q)\) unless a preregistered profile is lexicographic (α Flash = min \((L,C)\)).

Economic regulariser (007, only after feasibility):

\[
\mathcal{L}_{\mathrm{sel}}(\theta)=G(\pi_\theta)+\lambda^\top\mathbb{E}[\mathbf{R}^{\mathrm{add}}],\quad\lambda\ge 0\text{ declared, not learned to violate ceilings.}
\]

Observations \(o\) are **ledger projections**, not chat. If `evaluation: none`, \(p(\tilde o\mid C)\) is undefined for promotion.

### 5.3 Informational bottleneck \(\mathcal{B}_\theta\) (002 → context compiler)

\[
\mathcal{B}_\theta:\mathcal{W}\times\mathrm{TaskProfile}\to\mathrm{Context}_{\le k},\qquad
k=k(\theta)\text{ from the active Pareto profile.}
\]

Implementation: existing prefix-stable compiler; skill index bodies stay out of prefix (W12-A). VFE here means: drop context that does not change \(q(s)\). No new kernel module.

### 5.4 Adaptive Pareto profiles (002) — policy table

| Profile | Optimises | Typical use | Binding |
|---|---|---|---|
| **α Flash** | min \(L,C\) | syntax, lookup | cheap model, single worker, tight \(k\) |
| **β Balanced** | knee of frontier | multi-file repair | mid-tier; scout→executor as **graph**, not chat |
| **γ Deductive** | max \(Q\) | proofs, architecture | frontier; speculative spawn post-M-6; multi-oracle |
| **δ Escalate** | dynamic | general under ceiling | **as-built** `tier_escalation.py`: escalate on stop reason; separate labelled runs; no merged fake session |

Escalation passes **delta + falsifier node** in \(\mathcal{W}\), not a full replay (002). Each attempt remains its own \(D_R\).

### 5.5 Stigmergic \(\mathcal{W}\) and complexity

Forbidden protocol: peer LLM messages as the coordination medium.

Allowed: typed appends (work claims, artifact refs, receipts). Hypothesis graph \(\mathcal{H}\) is a **read model**, rebuilt by fold, never a workflow engine (ADR-0003, 0070).

### 5.6 Backward fault isolation (007 + TRACE-as-plugin)

Gold \(v\in\{+1,-1,\bot\}\) from UID-10002. \(\bot\) ⇒ no promotion credit.

```text
BackwardFaultIsolation(τ):
  if v = ⊥: return {}
  credit[T+1] ← 1[v=+1] − 1[v=−1]
  for t = T … 1:
    if r_t.outcome = rejected:    blame[t] ← POLICY; credit[t] ← 0
    else if r_t.outcome = undeterminable: blame[t] ← INSTRUMENT; credit[t] ← 0
    else: credit[t] ← δ(r_t) + γ·credit[t+1]; blame[t] ← MODEL if |δ|>ε
```

\(\delta\) is pack-defined (test diff, lemma check). TRACE-style frozen probes MAY fill \(\delta\) inside a pack learner. They MUST NOT write `VerdictRecorded`. CAR: LLM-judge step blame ~14% — refuse as gold.

### 5.7 Compounding ladder T0–T3 (006) + macro-tool collapse (002)

Higher tier may not excuse missing lower-tier evidence.

| Tier | Mechanism | Gate |
|---|---|---|
| **T0** | Exact witness memoization | Memo key binds obligation, inputs, env, checker, toolchain, policy version. Cache **never** transfers a verdict to a different subject. |
| **T1** | Macro-tool compilation | Repeated successful traces → deterministic toolkit plugin. Must pass replay, least-privilege, held-out paired eval, registry FSM. Executes **through S0–S12**. No evaluator secrets. Token collapse is a **consequence**, not a claim without RF-42. |
| **T2** | Skill/router Elo | 384-d hybrid BM25+cos after **symbolic** filters (capability, protection class). Elo-decay eviction. Catalog in manifest = \(D_H\); ranking = \(D_R\) until a promotion freezes a new catalog. |
| **T3** | DPO / harness search | Exterior training. Artifact is a new content-addressed component. Cassette regression + McNemar + Pareto safety. Live self-rewrite forbidden (ADR-0019). |

**Macro-tool intuition (002, bound by 006):** a 15-turn pattern becomes one `toolkit` dispatch. Until T1 gates pass, it is an untrusted candidate, not a privileged core patch.

### 5.8 Unforgeable DPO and paired McNemar

Pair \(\tau^w,\tau^\ell\): same task and paired-turn `context_digest`; both verdicts signed, same `oracle_id`; treatment is \(D_H\) **xor** model fingerprint, accounted; not unattributable; `cost_absent_reason` null on paired turns.

\[
\mathcal{L}_{\mathrm{DPO}}=-\mathbb{E}\log\sigma\Big(\beta\big(\log\tfrac{\pi_\theta(\tau^w)}{\pi_{\mathrm{ref}}(\tau^w)}-\log\tfrac{\pi_\theta(\tau^\ell)}{\pi_{\mathrm{ref}}(\tau^\ell)}\big)\Big).
\]

DMPO occupancy/length-norm allowed **outside** TCB.

McNemar exact: \(n_{10}\) challenger-only passes, \(n_{01}\) champion-only; \(H_0\): \(n_{10}\sim\mathrm{Bin}(n_{10}+n_{01},1/2)\). Promote iff \(p<\alpha\) **and** no `KernelAlarm` **and** \(\mathbf{R}^{\mathrm{add}}\) not worse than a pre-registered Pareto margin **and** no invariant regression (006: scalar must not average away a safety fail).

Sealed set \(S\) before search. Suggested \(|S|\ge 40\) smoke / 200 v1.0.

**Certificate (006, M-10):** `mhf.preference-pair/1` JCS-signed; issuer verifies both evaluator signatures; cannot rewrite executions.

---

## §6 · Zero-Guesswork Developer Bridge

### 6.1 `mhf.manifest/2` (Draft 2020-12) — file at M-3 as `schemas/mhf/manifest_v2.schema.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://vanguard.dev/schemas/mhf/manifest_v2.schema.json",
  "title": "MHF Manifest v2 — Named Component Graph",
  "type": "object",
  "additionalProperties": false,
  "required": ["api", "id", "components", "bindings", "capabilities", "budget"],
  "properties": {
    "api": { "const": "mhf.manifest/2" },
    "id": { "type": "string", "minLength": 1 },
    "components": {
      "type": "object",
      "minProperties": 1,
      "additionalProperties": { "$ref": "#/$defs/ComponentInstance" }
    },
    "bindings": { "type": "array", "items": { "$ref": "#/$defs/Binding" } },
    "system_prompt": { "type": ["string", "null"] },
    "capabilities": { "type": "array", "items": { "type": "object" } },
    "budget": { "$ref": "effect_request.schema.json#/$defs/Reservation" },
    "approval_policy": { "type": ["string", "null"] },
    "evaluation": { "type": ["string", "null"] },
    "sandbox_tier": { "type": ["string", "null"] },
    "pareto_profile": { "type": ["string", "null"], "description": "Ref to versioned α/β/γ/δ policy artifact; hashed into D_H." },
    "undeletable": { "type": "boolean", "default": false }
  },
  "$defs": {
    "SpiName": { "enum": ["planner", "context", "memory", "toolkit", "evaluation"] },
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
        "kind": { "enum": ["context", "observe", "evaluate", "spawn_grant", "route"] }
      }
    }
  }
}
```

YAML is a serialization; after parse it MUST validate as this JSON model (006). Compiler, not schema alone, enforces referential integrity of bindings.

**v1 frontend:** slots → instances; synthesise bindings; optional `pareto_profile: delta` mapping to current `model_routes` escalate_on.

### 6.2 Plugin FSM (target ADR-0081)

| From | To | Kind | Writer |
|---|---|---|---|
| (start) | DISCOVERED | `PluginDiscovered` **NEW** | registry |
| DISCOVERED | RESOLVED | `PluginResolved` | registry |
| RESOLVED | VERIFIED | `PluginVerified` **NEW** | registry |
| VERIFIED | ACTIVATED | `PluginActivated` | registry |
| ACTIVATED | QUIESCING | `PluginQuiesced` | registry |
| QUIESCING | RETIRED | `PluginRetired` | registry |
| * | FAULTED | `PluginFaulted` | registry |
| FAULTED | RETIRED | `PluginRetired` | registry |

Illegal transitions emit nothing (RF-33).

### 6.3 Spawn request outline (006, design-only until M-6)

```json
{
  "schema": "mhf.effect-request/1",
  "verb": "agent.spawn",
  "args": {
    "objective_digest": "sha256:…",
    "entrypoint": "planner-instance-id",
    "context_refs": ["sha256:…"],
    "requested_capability_ids": ["read-workspace"],
    "budget": {
      "usd_micros": 1000, "tokens": 2000, "bytes": 0,
      "millis": 30000, "turns": 4, "depth": 1
    },
    "workspace_mode": "isolated_snapshot"
  }
}
```

### 6.4 Falsifier matrix (RF-*)

| ID | Test | Wave |
|---|---|---|
| RF-12 | historical required-keys (keep) | M-1 |
| RF-12b | cost or reason | M-2 |
| RF-12c | silent zero fails | M-2 |
| RF-12d | `execution_digest` on completed model episode | M-2 |
| RF-22 | two planners + aggregator; \(D_H\) edge-sensitive | M-3 |
| RF-23 | v1 frontend | M-3 |
| RF-23b | instance ids beyond ROLE_KIND | M-3 |
| RF-24 | `evaluation: none` derived unattributable | M-3 |
| RF-25 | unsigned still illegal | M-3 |
| RF-26 | no spawn grant ⇒ deny | M-6 |
| RF-27 | action ∉ child scope denied **by kernel** | M-6 |
| RF-28 | empty kernel spawn diff at M-4 | M-4 |
| RF-29 | seven ledgered plugin transitions | M-3 |
| RF-30 | no `layer0` path or packaging | M-3 |
| RF-31 | NOVA-2 fresh-process resume | M-2 |
| RF-32 | UTL-F standing | M-3+ |
| RF-33 | illegal FSM silent | M-3 |
| RF-34…37 | NOVA-4 six + I-7 on absorbed registry | M-3 |
| RF-38 | Pack #2 zero kernel/domain diff | M-5 |
| RF-39 | McNemar harness (lab) | M-10 |
| RF-40 | nine-row E2E | M-4 |
| RF-41 | Pareto profile cannot skip S7 | M-10 / design test M-3 |
| RF-42 | macro-tool candidate cannot write VerdictRecorded or hold undeclared authority | M-10 |

### 6.5 Anti-patterns

N-1 TCB/kernel freeze until M-6 · N-2 I-7 · N-3 single writer · N-4 adapters↛kernel/agency · N-5 no third tree · N-6 no loop plugin · N-7 no forged cost · N-8 no authored promotable · N-9 no Redis/NATS core · N-10 no metaphysics (ADR-M0-10) · N-11 no microVM mandate pre-M-9 · N-12 no DPO in kernel · N-13 in_process speaks JSON-RPC · N-14 no sixth SPI without review · N-15 I-11 until M-7 · N-16 child workspace destroyed · N-17 JCS only · N-18 this file is not a ticket until ADRs land · N-19 no peer-chat coordination protocol · N-20 no `stigmergic_blackboard` boolean · N-21 do not equate path bag with graph · N-22 do not file 004/005 ADR numbers.

### 6.6 Monday after ADRs are filed

1. NOVA-1 writer + RF-12b/c/d.  
2. NOVA-2 WAL test.  
3. NOVA-3 ceiling pattern.  
4. Fix G0 links.  
5. Do **not** start `mhf.manifest/2` code until NOVA-2 green.

---

## §7 · Hygiene & Document Cascade

### 7.1 G0 ghost corpus

**`[ABSENT]` vs briefing:** reviews `004`–`006`; `RESEARCH_k3`; `RESEARCH_THEORETICAL_SYNTHESIS`; GLM/hy3 proposals; `openrouter_llm_models_suggested.md`.

**On disk:** WAVE_6 pair (duplicate `_B`), `deepseek-harness_algorithms-ideas.md`, `research_Harness_Builder_Framework.md` (reject as architecture), `vanguard_body_detailed.md` (ADR-M0-10 conflict), `guidelines.md`.

Restore from git **or** rewrite overview §4. `DELETE.md` does not exist — do not create a graveyard.

### 7.2 Stale citations

ADR-0070 still names deleted `layer0/scheduler/driver.py` — narrowing ADR at M-5, not a silent edit. `002` register Wave-0 “not started” — historical banner post-M-4. `pyproject` `layer0*` — ADR-0081.

### 7.3 Namespaces

Annex `F-*` = kernel controls. Register `RF-*` = this programme. Never mint annex `F-22` for a trajectory assertion.

### 7.4 Diff directives (after ADRs filed)

**SPEC.md:** add 0077–0082 to living range; §1 graph + (M-7) stigmergy \(\Theta(cN)\); §5.4 NOVA-1 MUSTs; §7 pairing keys populated, DPO consumer still deferred; evaluator absent-vs-forged; spawn engine-note until M-6; §9 add loop-plugin, authored promotable, second provenance product, peer-chat protocol.

**sprint_active.md:** NOVA-1/2 as M-2 **exit**; M-3 entry = NOVA-2; Plugin* kinds under ADR-0081.

**milestones.md:** M-2 contentful trajectory + NOVA-2; M-3 graph + delete layer0; M-4 row 8 = NOVA-1; M-5 Pack #2 math not TableWorld; footnote this ladder.

**wave2 plan:** assembler + usage + NOVA-2; no graph code. **wave3:** schema v2, FSM kinds, NOVA-4, delete. **wave4:** RF-40.

---

## §8 · Refused Alternative — Obligation Market (harvest only)

`007` §8 inverts the primitive from **turn** to **typed obligation** + `Refine`. Coordination by scarcity; `witness_type` declared at admission.

**Ruling: do not replace S0–S12 with an obligation kernel.** That is a second mechanism and violates UTL-1 / ADR-0070 until UTL-F succeeds.

**Harvest into the master:**

- Pack evaluation components SHOULD declare a **witness type** (`tests_green`, `proof_checks`, `schema_conforms`, `replay_equivalent`) — this is ADR-0079’s oracle, named.
- T0 memo keys SHOULD bind that witness type (006 §10).
- Price ceiling as 6D \(\mathbf{R}\) already exists; do not invent a market allocator (SPEC §9 / deferred).

---

## Appendix A · Forensic Log

| Claim | Result |
|---|---|
| HEAD | `e84dfda` |
| Version | `0.4.5b1` |
| `_ZERO_COST` | trajectory.py 10, 53, 75 |
| F-12 | required keys + abort null verdict only |
| Path bag | `parse_manifest` role→paths; no bindings |
| Role freeze | `REGISTERED_COMPONENT_CONSUMERS`; `ROLE_KIND` |
| Plugin FSM | 5/7 kinds; no Discovered/Verified |
| Spawn hole | documented in `engine.py` spawn docstring |
| layer0 | compose/registry/events; packages import-free; setuptools still includes |
| WAL | `journal_mode=WAL`, `synchronous=FULL` |
| \(D_R\) | no `execution_digest` assignment in assembler |
| Escalation | `tier_escalation.py` stop-reason ladder (δ ancestor) |
| Skill index | char budget, no Elo |
| TableWorld | already an adapter |
| Principal reviews on disk | 001, 002, 003 only |
| DELETE.md | absent |

---

## Appendix B · Master Findings

1. **G0** — briefing index with empty bytes (same class as I-9).  
2. **Path bag ≠ graph** — 007 overclaim corrected.  
3. **Hard-coded consumers** — 006 gem; T-1 is not YAML-only.  
4. **F-12 false green.**  
5. **FSM unsatisfiable M-3 exit** without two kinds.  
6. **\(D_R\) uncomputed** — router experiments undefined.  
7. **Pack #2 ≠ TableWorld.**  
8. **Spawn hole is documented**, not speculative.  
9. **`layer0*` packaging** survives directory deletion unless pyproject changes.  
10. **Pareto already has a seed** (`tier_escalation.py`) — do not rebuild MetaLoopEngine.  
11. **ADR-number fork** across 004/005/007 — this file locks 0077–0082.  
12. **VFE≠EFE**; **mesh \(O(N^2)\) is protocol-forbidden, not a free theorem.**

---

## Appendix C · External Sources

Harness Engineering (Zenodo 2026); Greyling 2026 two-thirds harness; Shankar 2026 domain-agnostic harness; stigmergic / state-centric MAS 2026; Many Tems scent+SQLite; language-mediated AIF arXiv:2508.05766; multi-LLM AIF arXiv:2412.10425; ASTRA arXiv:2601.21558; DMPO EMNLP 2024; TRACE arXiv:2607.13988; CAR arXiv:2606.08275; NVIDIA/Augment/Northflank sandbox surveys; CaMeL 2025; EnvHarness / Agentic ESOpt 2026 (via 004); Anthropic multi-agent research system 2025; JSON Schema 2020-12.

Internal law: SPEC, ADRs 0069–0076, KERNEL.md, 002, 003, SYSTEM_OVERVIEW, sprint_active, milestones, on-disk packages (Appendix A). Advisory proposals 002–007 consumed as option space, not law.

---

## Signature (advisory)

| Role | Vote |
|---|---|
| Engineering Director | R-1…R-6; M-4; v0.6.3 cut |
| CTO | Corpus is strategy; Pareto is product; no SDK-wrap |
| CIO | Derived unattributability; no silent `$0` |
| Principal Staff Engineer | G0→G1→G2→G9; locked ADR numbers |
| Principal Systems Architect | Bindings required; map 002 primitives onto planes; TCB 0 until M-6 |
| Tech Lead | NOVA-2 gates M-3; RF matrix |
| PhD AI Specialist | VFE≠EFE; T0–T3; McNemar∧Pareto |

*Tier S+ Alfa master. Advisory. Amends nothing until ADRs 0077–0082 are filed.*
