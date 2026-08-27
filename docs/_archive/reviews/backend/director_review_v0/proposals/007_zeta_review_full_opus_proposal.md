# 007 — ZETA MASTER ARCHITECTURE (Tier S+)

## The Pareto Harness: a Stigmergic, Actively-Inferring, Self-Compiling Task-Solving Substrate

**Synthesis of proposals `002`–`008` into one master architecture and one execution plan.**

| Field | Value |
|---|---|
| **Document** | `007_zeta_review_full_opus_proposal.md` — supersedes the Zeta review draft of the same path |
| **Class** | Master architecture + phased technical proposal. **ADVISORY.** Amends nothing. |
| **Prepared by** | The Leadership 7 — Engineering Director · CTO · CIO · Principal Staff Engineer · Principal Systems Architect · Tech Lead · PhD AI Specialist |
| **Baseline** | `main` @ `67e1803`. Every `[VERIFIED]` claim was re-executed against the working tree during this pass. |
| **Synthesized from** | `002_beta` (GEM) · `004_delta` (GLM-5.3) · `005_epsilon` (DSv4) · `006_fi` (GPT-sol) · `008_alfa` (Grok) · the prior `007_zeta` draft |
| **Scope** | Version ladder **v0.6.1 → v1.0.0**, milestones **M-0 … M-10** |
| **Authority** | Law remains `docs/SPEC.md` → `docs/05_adr/` → `docs/04_annex/`. §7 contains **drafted** ADR texts; they bind only when committed with a Director signature. |
| **Constraint honoured** | No specification file, ADR, schema, or source file was edited in producing this document. |

---

## Table of Contents

- [§0 · Preface — What This Document Is, and What It Corrects](#0--preface--what-this-document-is-and-what-it-corrects)
- [§1 · The S+ Master Architecture](#1--the-s-master-architecture)
- [§2 · Pillar I — The Pareto Harness](#2--pillar-i--the-pareto-harness)
- [§3 · Pillar II — Stigmergic Coordination](#3--pillar-ii--stigmergic-coordination)
- [§4 · Pillar III — Active Inference, Stated Correctly](#4--pillar-iii--active-inference-stated-correctly)
- [§5 · Pillar IV — Macro-Tool Compilation & the Four-Tier Flywheel](#5--pillar-iv--macro-tool-compilation--the-four-tier-flywheel)
- [§6 · Final Adjudication of Tensions T-1 … T-9](#6--final-adjudication-of-tensions-t-1--t-9)
- [§7 · Drafted Append-Only ADR Catalog — `ADR-0077` … `ADR-0084`](#7--drafted-append-only-adr-catalog--adr-0077--adr-0084)
- [§8 · Milestone Roadmap & Version Ladder](#8--milestone-roadmap--version-ladder)
- [§9 · Zero-Guesswork Developer Implementation Bridge](#9--zero-guesswork-developer-implementation-bridge)
- [§10 · Repository Hygiene & Document Update Cascade](#10--repository-hygiene--document-update-cascade)
- [Appendix A · Forensic Verification Log](#appendix-a--forensic-verification-log)
- [Appendix B · Provenance Matrix — Which Idea Came From Where](#appendix-b--provenance-matrix--which-idea-came-from-where)
- [Appendix C · Corrections Applied to Predecessor Proposals](#appendix-c--corrections-applied-to-predecessor-proposals)
- [Appendix D · External Sources](#appendix-d--external-sources)

---

## §0 · Preface — What This Document Is, and What It Corrects

### 0.1 The synthesis, in one paragraph

Six independent leadership passes converged on the same six rulings (component graph, un-hollow the corpus, absent-vs-forged, spawn design-locked, `layer0/` absorbed then deleted, loop-as-mechanism published with a falsifier). That convergence is now settled and is **not re-argued here**. What each pass contributed *uniquely* is the material worth keeping, and four such contributions are strong enough to become architectural pillars rather than footnotes: **`002`'s Pareto profile matrix**, **`004`/`006`'s stigmergic complexity argument**, **`006`'s correct separation of variational from expected free energy**, and **`002`'s macro-tool distillation** fused with **the prior `007`'s memoized-witness flywheel**. This document promotes those four into the architecture, adds two ADRs (`0083`, `0084`) to carry them, corrects six factual and two mathematical errors that propagated across the predecessor set, and reduces the whole to one executable plan.

### 0.2 The Tier S+ claim, stated so it can fail

> **AETHER becomes a general task-solving swarm meta-framework when four properties hold simultaneously, and it is *not* one until all four are demonstrated:**
>
> 1. **Composable** — arbitrary agentic topologies are declared as data over a Named Component Graph, with zero engine diff. *(falsified by `RF-30`, `RF-65`)*
> 2. **Economical** — every strategy quotes a price, and the runtime selects on a measured cost/latency/quality frontier rather than a hardcoded loop. *(falsified by `RF-46`, `RF-47`)*
> 3. **Stigmergic** — N logical agents coordinate through the State Plane at `Θ(N)` messaging, never `O(N²)` peer chatter. *(falsified by `RF-60`)*
> 4. **Compounding** — each solved task measurably lowers the expected cost of the next, deterministically before it does so statistically. *(falsified by `RF-52`, `RF-67`)*
>
> All four rest on a fifth that is not negotiable and is already built: **unforgeable evidence**. Properties 1–4 without property 5 describe every framework in the 2026 literature. Property 5 is the moat.

### 0.3 Six factual corrections this synthesis applies

Each was disputed across the predecessor set and is settled here by re-execution `[VERIFIED this pass]`.

| # | Disputed claim | Resolution |
|---|---|---|
| C-1 | Boundary linter scans "283 files" (`CLAUDE.md`, `SYSTEM_OVERVIEW`, `002`) | **248.** `BOUNDARY PASS: 248 source files checked`. `006` is correct; the documentation number is stale. |
| C-2 | `test/agency` has 107 tests (board, `SYSTEM_OVERVIEW`) | **105.** `Ran 105 tests … OK`. `006` is correct. |
| C-3 | `RESEARCH_THEORETICAL_SYNTHESIS.md` and `_B.md` are "near-duplicates" (prior `007`) | **Byte-identical** — both `sha256:45bddc74…f7a24e3`. `006` and `002` are correct. **The prior `007` draft's instruction to "keep `_B`, the successor" was wrong and is withdrawn.** There is no successor. |
| C-4 | `DELETE.md` is not present (`008`) | **Present, 0 bytes.** `008`'s log ran at `e84dfda`, three commits back. |
| C-5 | The review and research corpora are "ghost" / absent (`008` §7.1 "G0") | **Refuted.** All 6 files under `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/` and all 12 under `docs/06_references/` exist at HEAD. `008`'s G0 is a stale-tree artifact and **must not** be carried into any directive. |
| C-6 | `layer0/` deletion is complete once the directory is removed | **False, and this is `008`'s best finding.** `pyproject.toml:40` reads `include = ["vanguard*", "layer0*"]` `[VERIFIED]`. Setuptools still ships the fork. Deletion without this line is cosmetic. |

### 0.4 Two mathematical corrections

| # | Error | Correction |
|---|---|---|
| M-1 | `002`, `004`, `005` and the prior `007` all inherit `F(θ) = D_KL[q‖p] − E[ln p(Y=1)] + λΣR/R_max` from `RESEARCH_THEORETICAL_SYNTHESIS.md` and use it as an **action-selection** objective, calling it Variational Free Energy. | **Category error.** VFE is *belief fitting*; **Expected** Free Energy `G(π)` is *policy selection*. `006` is the only predecessor to state this correctly. §4 adopts `006`'s formulation and discards the conflated form. |
| M-2 | `002` and `005` prescribe McNemar via **χ² ≥ 3.841** with continuity correction. | `docs/04_annex/MEASUREMENT.md` **M-03** mandates the **exact binomial** form and explicitly states the chi-squared approximation *"is unreliable at the discordant counts achievable at realistic sample sizes."* §5.4 uses the exact test. Prescribing χ² contradicts standing law. |

### 0.5 One architectural reversal

The prior `007` draft ruled that **cycles in the composition graph fail at compose**. `006` is right and this is reversed:

> **A critic loop *is* cyclic. A debate with rebuttal *is* cyclic. Rejecting cycles at compose rejects the exact topologies `ADR-0077` exists to enable.** Cycles are **permitted**; termination is enforced by the budget algebra — `turns`, `depth`, `usd_micros`, `millis` — never inferred from graph acyclicity. This is also what keeps the graph a *composition* graph rather than a workflow DAG: a DAG engine needs acyclicity because it derives execution order from topology; AETHER derives execution order from the turn loop, so it does not need acyclicity and must not pretend to.

### 0.6 One methodological correction to the prior `007`

`008` §Appendix B/2 is correct against the prior `007`'s finding B-2. `domain/artifacts/manifest.py` types `components` as `tuple[tuple[str, tuple[str, ...]], ...]` — a **role → paths bag with no edges**, not a graph. Converging the two parsers onto that shape does **not** buy debate, critic loops, or tree search.

> **Therefore: `bindings` — the typed edge set — is the actual deliverable of T-1, not `components`.** The existing named bag lowers the cost of the *node* half and buys nothing on the *edge* half. §7's `ADR-0077` is written against that corrected premise, and `RF-31` (a binding-edge change must move `D_H`) is the falsifier that proves the edge half landed.

---

## §1 · The S+ Master Architecture

### 1.1 The one diagram

```text
╔═══════════════════════════════════════════════════════════════════════════════════════════════╗
║  L5  COMPOUNDING LAYER  (M-9/M-10 · exterior, domain-blind, promotion-gated)                  ║
║      T0 memo cache · T1 macro-tool compiler · T2 skill cards (Elo) · T3 DPO harvest           ║
║      consumes trajectories; NEVER drives them; admitted only by paired exact McNemar          ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════╣
║  L4  PARETO ROUTER  (M-3 schema · M-7 active)          ◄── Pillar I                          ║
║      profile ∈ {α flash, β balanced, γ deductive, δ adaptive}                                 ║
║      argmin_θ  E[G(π_θ)] + Σ λ_j E[c_j]   s.t.  c_add ≼ R_add,  T ≤ r_turn,  d ≤ r_depth      ║
║      A PLANNER-SIDE POLICY. Never a second authorization path.                                ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════╣
║  L3  COMPOSITION SURFACE — Named Component Graph  `mhf.manifest/2`   (M-3)                    ║
║      components{name → kind,ref,config,ceiling,isolation} + bindings[from,to,relation]        ║
║      cycles PERMITTED · termination by budget · compose→FrozenHarness(D_H)                    ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════╣
║  L2  AGENCY — the universal turn loop (MECHANISM, never plugin)                                ║
║      observe → propose → authorize → effect → receipt → evaluate → (reflect)*                 ║
║      topology varies infinitely; the authority boundary never moves                            ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════╣
║  L1  THE THREE PLANES — already built, already verified                                        ║
║   ┌───────────────────┬────────────────────────────┬────────────────────────────────────────┐ ║
║   │ DECISION          │ STATE                      │ EVIDENCE                               │ ║
║   │ kernel/ S0–S12    │ SQLite WAL, State=fold(e)  │ UID 10002, Ed25519, nonce-bound        │ ║
║   │ 1365/1438 LOC     │ per-project hash chain     │ gateway is sole VerdictRecorded writer │ ║
║   │ volatile          │ immutable, sole truth      │ exterior, unreachable from the judged  │ ║
║   └───────────────────┴────────────────────────────┴────────────────────────────────────────┘ ║
║        ▲ Pillar II: agents address the LEDGER, never each other → Θ(N), not O(N²)             ║
╠═══════════════════════════════════════════════════════════════════════════════════════════════╣
║  L0  IDENTITY — D_H ≠ D_R ≠ D_X, all bytes via JCS (RFC 8785). The denominators.               ║
╚═══════════════════════════════════════════════════════════════════════════════════════════════╝
```

### 1.2 A-B-C-D, re-scored against disk `[VERIFIED this pass]`

| | Pillar | Generic? | Evidence | Ruling |
|---|---|---|---|---|
| **A** | Authority | ✅ | `TCB PASS: 1365 logical lines across 9 files (alarm above 1438)` — 73 LOC headroom. `policy.py` orders attenuate → sealed membership (`ADR-0067`) → authority predicate → approval, three outcomes, no "allow with a warning". | **Keep. Zero growth until M-6.** |
| **B** | Bundle | ❌ | Two dialects: `schemas/mhf/harness_manifest.schema.json` freezes six slots under `additionalProperties: false`; `domain/artifacts/manifest.py:64` holds a **path bag, not a graph**. Neither has edges. | **`ADR-0077`. Edges are the deliverable.** |
| **C** | Corpus | ❌ | `runtime/trajectory.py:10,53,75` — `_ZERO_COST`. No `model_routes_used`, no `execution_digest`, no `attribution` in the emitted object. `D_R` is **never computed anywhere in the tree**. | **`ADR-0078`. Fix inside M-2.** |
| **D** | Digest | ✅ | `manifest.py:83-95` — `composition_digest` over `{harness, components, capabilities, evaluators, budgetPolicy, graphDigest, **identity}`, `episode_id` excluded as instance identity. | **Keep. Extend over the graph; principle unchanged.** |

**The whole plan is the order in which B and C become generic without weakening A or collapsing D.** Pillars I–IV are what B and C become *for*.

### 1.3 The six settled rulings (convergent across all six passes — do not re-argue)

| # | Ruling | ADR | Lands |
|---|---|---|---|
| R-1 | Un-hollow the corpus **now**; the board's carry-to-Wave-4 is overruled in writing | `0078` | **v0.6.1 / M-2** |
| R-2 | `harness.yaml` → Named Component Graph, **with typed edges** | `0077` | v0.6.2 / M-3 |
| R-3 | Guardrails declarable, evidence never forgeable | `0079` | v0.6.2 / M-3 |
| R-4 | `agent.spawn` design-locked; **zero kernel diff** until M-4 closes | `0080` | design v0.6.1, code v0.8.0 / M-6 |
| R-5 | `layer0/` absorbed behind NOVA-4, then deleted — **including `pyproject.toml:40`** | `0081` | v0.6.2 / M-3 |
| R-6 | Loop-as-mechanism published with a bound falsifier; NOVA-2 is I-11's precondition | `0082` | v0.6.1 / M-2 |

### 1.4 The two rulings this synthesis adds

| # | Ruling | ADR | Lands |
|---|---|---|---|
| **R-7** | **The Pareto Router.** Execution profiles become manifest data; strategy selection becomes a priced, measured, planner-side decision on a constrained frontier — never a second authorization path. | **`0083`** | schema v0.6.2 / M-3 · active v0.9.0 / M-7 |
| **R-8** | **Macro-Tool Compilation.** A verified multi-turn pattern is compiled into a deterministic tool that is a **plugin with a `D_H`-affecting digest**, admitted only through paired exact McNemar. The flywheel starts at Tier 0 (memoization) and needs no ML to begin compounding. | **`0084`** | v0.7.0 / M-5 (T0) · v1.0.0 / M-10 (T1–T3) |

---

## §2 · Pillar I — The Pareto Harness

> **Source:** `002` §11.4 (the profile matrix — the strongest single contribution in the predecessor set) fused with `006` §5.2 (constrained optimization with a retained Pareto frontier) and the prior `007` §8.3 (priced work as a scheduler objective).

### 2.1 The problem this solves

A harness with a fixed loop, a fixed model tier, and a fixed context budget is **one point** on a four-dimensional trade-off surface. Terminal-Bench 2.0 evidence in the internal corpus records the same GPT-5.3-Codex model swinging **64.7% → 78.4%** on harness alone; the 2026 automatic-harness-evolution literature lifts pass@1 from **69.7% → 77.0%** over ten iterations, surpassing a human-designed harness. The swing is the point: *the harness is the independent variable, and a substrate that cannot move along that surface at runtime has hardcoded one answer to a question that has four.*

### 2.2 The four dimensions and the one objective

```text
   C  financial cost      (usd_micros)   ┐
   T  token volume        (tokens)       ├─ additive, conserved, debited from the parent
   L  latency             (millis)       ┘  (charged compute, NEVER wall-clock under concurrency)
   Q  quality / assurance (witness class + P̂(pass))    ─ a floor, never a currency
```

Selection is **constrained minimization with a retained frontier**, never a scalar score:

```
   θ*  =  argmin_{θ ∈ Θ}  (  E[G(π_θ)]  +  Σ_{j∈C} λ_j · E[c_j(θ)]  )

   subject to   E[c_add(θ)] ≼ (r_$ , r_tok , r_byte , r_ms)      component-wise
                T ≤ r_turn ,   d ≤ r_depth                        structural, never summed
                witness_class(θ) ⪰ floor(task)                    hard, never traded
```

`λ_j ≥ 0` are **declared policy parameters, not learned excuses to violate ceilings.** Feasibility and assurance are checked *first*; among feasible policies AETHER retains a **Pareto frontier** unless a preregistered product policy specifies a lexicographic order. This is `006`'s formulation and it is the one that survives the `SPEC.md` §9 refusal of *scalar reward for promotion*.

### 2.3 The four execution profiles — manifest data, not code

| Profile | Optimizes | Target latency | Tokens/turn | Routing | Topology | Task class |
|---|---|---|---|---|---|---|
| **α — Flash Tactical** | min(C, L) | `< 1 s` | 500 – 2 000 | tier-1 local, strict heuristic prompt | single ephemeral worker, direct tool stream, **memo-first**, no debate | syntax fixes, single-test repair, lookups, file reads |
| **β — Balanced Autonomous** | frontier | 3 – 10 s | 2 000 – 8 000 | tier-2, dynamic context projection | scout → executor, single-pass evaluation | multi-file features, refactors, triage, data analysis |
| **γ — Deductive / SOTA** | max(Q) | 15 – 60 s | 8 000 – 35 000 | tier-3 frontier, multi-candidate | speculative tree search · debate · dual-gate evaluation | architecture, formal proof, security audit, hard math |
| **δ — Adaptive Escalating** | dynamic | variable | dynamic | starts α, escalates on signed `verdict_fail` while budget holds | tiered escalation with state preservation — **only the delta and the falsifier carry forward, never a full context replay** | general autonomy under a hard ceiling |

A profile is a **weighting of §2.2's objective plus a topology preset**, declared in `mhf.manifest/2` under `profiles:` and selected per task. It is **not** a code path. Adding a fifth profile is a manifest edit.

### 2.4 The escalation rule that makes δ cheap

`δ` is the profile that pays for itself, and the mechanism matters:

```text
1.  classify task → θ₀ (lightweight heuristic; a model call is permitted but not required)
2.  execute under lease L(θ₀); submit the candidate to the evaluation component
3.  on fail:  capture the FALSIFIER (the specific failing assertion / denied capability /
              overflow signature) as a durable event
              θ_{i+1} := escalate(θ_i, failure_class)      ← §4.4 transition rules
              carry forward ONLY (workspace delta + falsifier). NOT the transcript.
4.  charge every attempt to the same episode's additive budget. Escalation is not a new wallet.
```

Carrying the falsifier rather than the transcript is what keeps tier-3 invocations short. It is also why `ADR-0078`'s per-turn cost is a **precondition**: without measured cost per attempt, `δ` cannot know whether escalating is cheaper than abandoning.

### 2.5 Hard boundary — where the router may not go

> **The Pareto Router is a planner-side policy. It selects *what to propose and at what tier*. It never decides *whether an effect is authorized*.**

| Permitted to the router | Forbidden to the router |
|---|---|
| choose model tier, context budget, topology preset, repair-round count | widen a capability ceiling |
| decide to escalate, retry, abandon, or spawn (post-M-6, with a grant) | bypass S0–S12 or pre-filter authorization |
| read measured cost, latency, and `P̂(pass)` from the ledger | author a cost field, or mint a verdict |
| propose a manifest mutation (M-10, capability-restricted) | apply one in place |

A "sub-5 ms pre-flight filter" is **advisory only** and may never become a second authorization path. `S0–S12` remains the sole mediator (`ADR-0069`, `ADR-0070`).

### 2.6 Cost-per-pass becomes a primary key

Because every strategy quotes a price before it runs, and every outcome is exterior-signed, the substrate computes without additional instrumentation:

```
                       Σ_{runs of strategy s on class k}  cost_add(run)
   CPP(s, k)  =  ─────────────────────────────────────────────────────────
                  |{ runs of s on k with signed verdict.pass = true }|
```

`CPP` is the selection signal for §5's flywheel and the reporting unit for every strategy claim. **A strategy whose `CPP` does not beat the incumbent on a task class is starved of work automatically** — deprecation becomes a measurement, not a meeting.

---

## §3 · Pillar II — Stigmergic Coordination

> **Source:** `004` §1.2(b) (the 2026 topology-cost citations), `006` §2.3 + §7.4 (the honest complexity bound and the CAS claim protocol), `002` §2.2 (the blackboard framing).

### 3.1 The 2026 evidence

The multi-agent literature has converged on the failure mode: natural-language message passing as the sole inter-agent medium is a **structural** limit on consistency, efficiency, and auditability. The dominant synchronisation pattern is **full-state rebroadcast** — on any artifact modification the orchestrator injects the complete updated artifact into the next prompt of every agent that might need it — and that is the source of quadratic cost. Reward-guided autoregressive topology generation and causal edge-pruning (`E2-Explainer`) both exist *specifically because* fully-connected chatter is prohibitively expensive. `CodeCRDT` demonstrates coordination by **observing shared state** — agents watch edits, skip completed work, avoid conflicts — with no centralized assignment.

### 3.2 The complexity claim, stated honestly

`006` is right that the naive `O(N²)` figure needs qualification, and this document adopts the honest form:

```text
                        messages / round      context bytes / round
  full-mesh chat            N(N−1) = Θ(N²)      Θ(N² · |artifact|)     ← the pattern in the wild
  sparse peer topology      Θ(N)                Θ(N · |artifact|)      ← achievable, but needs a topology search
  STIGMERGIC (AETHER)       0 peer messages     Θ(c·N · |Δ|)           ← c = state ops per agent per round
                            Θ(c·N) state ops                              large values → blob store by digest
```

**The `Θ(N²)` term does not exist in AETHER's architecture, and not by optimization — by construction.** Sibling agents never address each other. They append to the ledger and read a projection. Causal relations (`spawned_by`, `caused_by`, `produced`, `evaluated_by`) are **projections of events, never a maintained graph** (`ADR-0003`, `ADR-0070`).

**What this does *not* mean:** it does not mean every token goes into SQLite. Large values go to the blob store by digest (`write → fsync → emit(digest)`, D-19); the WAL carries authoritative envelopes and refs; semantic retrieval reads a *rebuildable projection* that never becomes the source of truth. Contention and query cost depend on indexing and hot keys, which is why §3.5 makes the property a **measurement**, not an assertion.

### 3.3 The State-Plane work protocol

Coordination uses immutable content-addressed work plus authoritative claim events with **compare-and-swap** semantics:

```text
WorkPublished  (work_digest, required_interface, budget_offer, parent_lineage)
WorkClaimed    (work_digest, child_principal, lease_id, expected_version)   ← CAS on reduced version
ArtifactPublished (work_digest, artifact_digest, provenance_root)
WorkReturned   (work_digest, child_principal, terminal_state, artifact_refs)
WorkReleased   (work_digest, reason)                                        ← lease expiry / cancellation
```

> ⚠ **These five kinds are DESIGN PLACEHOLDERS.** New event kinds are a **Director-only escalation** (`sprint_active.md`). They must not be added ad hoc, and they are **not** in scope before M-7. They are named now so M-7 has a contract rather than an improvisation.

**Four safety rules, none optional:**

1. Each child holds an **attenuated principal**, a budget **sublease** (not copied counters), a depth, and explicit parent lineage.
2. Coordination writes are **typed and role-owned** — `PRIVILEGED_KIND_OWNERS` governs, exactly as it does today.
3. Shared artifacts are **immutable / content-addressed**, or versioned by CAS. A worker that loses the claim **cannot commit a privileged effect under that lease.**
4. Only the **exterior evaluator** may mint the signed verdict used for promotion. A swarm has **one court**.

At-least-once claim delivery is acceptable **only** because effects carry durable intent (S8a), idempotency keys, and reconciliation (`ADR-0026`). It must never become at-least-once *external effects*.

### 3.4 Direct messages are observations, never authority

Where a direct agent-to-agent message is genuinely useful, it is permitted — as an **observation entering the receiving agent's context at `UNTRUSTED_DERIVED` or lower**. It is attributed, it is ledgered, and it **cannot authorize anything** (`provenance.authority_violation` over justifying spans, `K-33`). A parallel authority channel is the one thing a stigmergic design must never grow.

### 3.5 The property as a falsifiable measurement

> **`RF-60` (M-7 gate).** Measured inter-agent messages per round MUST remain `Θ(N)` — and peer messages MUST remain **zero** — as `N` scales 1 → 64 over a bounded worker pool `K`. Measured state operations per round must remain `Θ(c·N)` with `c` bounded and declared. If either fails, the Stigmergic Coordination Property is **refuted** and the `SPEC.md` §1.4 claim is struck.

**Refused, explicitly:** CRDTs, eventual consistency, and MESI-style coherence protocols. `project_id` is the consistency unit with a **total order**; a CRDT trades that total order for concurrency AETHER has not yet earned the right to enable (I-11). Revisit only if `RF-47` demands it.

---

## §4 · Pillar III — Active Inference, Stated Correctly

> **Source:** `006` §5.2, adopted verbatim in structure. This section **replaces** the conflated formulation carried by `002`, `004`, `005`, and the prior `007`.
>
> **Placement:** exterior, domain-blind, promotion-gated policy for M-10. Never a kernel primitive. `tools/telemetry/`, `lab/`, and the harvester are siblings of the kernel tree and are never imported by it (D-40).
>
> **Framing:** `ADR-M0-10` / `REJ-10` forbid biological, cosmological, or tier-of-being framing anywhere under `docs/`. *"Free energy"* here is the variational bound of Bayesian inference and nothing else.

### 4.1 The category error being corrected

`RESEARCH_THEORETICAL_SYNTHESIS.md` §2.2 writes a single functional `F(θ)` combining a KL term, a success-likelihood term, and a cost regulariser, and calls it Variational Free Energy used for harness selection. **Four of the six predecessor proposals copied it.** It is two different objects welded together:

- **VFE `F`** is *inference*: how well a belief fits the evidence. Minimising it tightens an evidence bound. **It does not choose an action.**
- **EFE `G(π)`** is *action selection*: the expected free energy of a policy under preferred outcomes, decomposing into pragmatic value and epistemic value.

Collapsing them produces a scalar that looks principled and licenses exactly the thing `SPEC.md` §9 refuses: **a single fitness number that lets a cost win offset a safety regression.**

### 4.2 Variational free energy — belief fitting

Let `s` be latent task state, `o` observations and signed evidence, `τ = (o_{0:T}, a_{0:T−1})` a trajectory, `θ` the frozen harness graph, `q_φ(s|τ)` the approximate posterior, `p_θ(τ,s)` the generative model.

```
   F(φ, θ; τ)  =  E_{q_φ(s|τ)} [ log q_φ(s|τ) − log p_θ(τ, s) ]

               =  D_KL( q_φ(s|τ) ‖ p_θ(s|τ) )  −  log p_θ(τ)
                  └──── belief error ────┘        └─ log-evidence ─┘
```

Minimising `F` over `φ` tightens an evidence bound on the observed trajectory. **That is all it does.**

### 4.3 Expected free energy — policy selection

Candidate policies `π` are scored against preferred outcomes `p_C(o)`:

```
   G(π)  =  E_{q(o,s|π)} [ log q(s|π) − log p_C(o, s) ]

         =    pragmatic risk + ambiguity      −      epistemic information gain
              └ "will it pass, cheaply?" ┘           └ "what will I learn?" ┘
```

Under the 2026 result AETHER adopts, EFE minimisation becomes tractable when **recast as variational inference with epistemic priors**; factor-graph message passing then scales **linearly in the number of factors**. AETHER's structure is already a factor graph:

```text
   factors  =  { (D_H, task_digest, turn-prefix context_digest) → signed verdict }
   edges    =  the component-graph bindings of mhf.manifest/2       ← ADR-0077 creates these
   messages =  per-turn (cost, latency, fingerprint) vectors        ← ADR-0078 makes these non-zero
```

**Neither factor exists today.** The edges do not exist until `bindings` lands; the messages are `_ZERO_COST` until NOVA-1 lands. **That is the mathematical statement of why `ADR-0077` and `ADR-0078` are the two prerequisites of the entire M-10 arc**, and why building the learning layer first would be optimising noise.

### 4.4 The five-step operating cycle

```text
1. PERCEPTION   minimize F: update the task-state belief from observations and signed evidence
2. PLANNING     estimate G(π_θ) for candidate graph policies / profiles / routes    ← Pillar I
3. ADMISSION    reject candidates outside R, capability, safety, or evidence constraints
4. ACTION       run the selected proposal through S0–S12 — unchanged, unbypassed
5. LEARNING     update priors ONLY from evidence-complete trajectories
                NEVER modify authority from a posterior belief
```

Step 5's second clause is the whole safety argument. A belief may change what the system *tries*; it may never change what the system is *permitted* to do.

### 4.5 The calibrated gate — the operational form (`SPEC.md` §5.3)

The full formalism does not enter the runtime. The planner maintains a calibrated posterior and scores on one scalar *within a feasible, assurance-satisfying set*:

```
   score(a | c)  =  P̂(pass | a, c) · value(pass)  −  λ · Σ_{d∈A} R_d(a) / R_max,d
```

- `P̂(pass | a, c)` is calibrated **per `D_H`** from `CompetencePriorRecorded` / `VerdictRecorded` history. The prior recorder already exists.
- Escalation, retry, and abandonment become **threshold policies on this one scalar**, unifying `tier_escalation.py`, repair-round bounds, and abandonment under a single calibrated rule.
- Miscalibration becomes measurable:

```
   Brier(D_H)  =  (1/N) Σ_i ( P̂_i(pass) − Y_i )²        Y_i from the EXTERIOR SIGNED verdict only
```

> **This is the differentiated claim, in equation form.** Because `Y_i` comes from a request-bound, Ed25519-signed verdict the agent cannot read, patch, or reason about, **the calibration signal is un-gameable by construction rather than by policy.** Every published automatic-harness-evolution loop in the 2026 literature calibrates against self-reported or benchmark-scored outcomes.

### 4.6 Mutation operators over the manifest genome

`θ` ranges over **JCS-diffable** fields of `mhf.manifest/2`. Failure class → licensed mutation:

| Op | Trigger | Mutation |
|---|---|---|
| M1 | `CONTEXT_WINDOW_OVERFLOW` | `tokens ← min(⌈tokens·(1+α)⌉, R_max.tokens)`, `α = 0.5` |
| M2 | `REPAIR_OSCILLATION` | `planner_ref ← tree-search variant`; `repair_rounds += 2` |
| M3 | `MODEL_CAPABILITY_DEFICIT` | `tier ← min(tier+1, tier_max)` **iff** budget headroom permits |
| M4 | prompt-attributable failure | substitute one L1 fragment from the **preregistered** variant set |
| **M5** | topology-attributable failure | **add / remove one component or one binding edge** ← exists only because of `ADR-0077` |
| **M6** | profile mis-selection | adjust `λ_j` or a profile threshold ← exists only because of `ADR-0083` |
| — | **`AUTHORIZATION_DENIED`** | **NONE. Escalate to a human.** |

> **CIO standing rule, normative.** `AUTHORIZATION_DENIED` MUST NEVER license an automatic mutation. **A system that widens its own ceiling in response to being denied has inverted the reference monitor.** This is the single most important line in §4.

Every mutation produces a **new `D_H`**. Nothing is ever mutated in place (`ADR-0072` §3); promotion flips a pointer (§5.4).

---

## §5 · Pillar IV — Macro-Tool Compilation & the Four-Tier Flywheel

> **Source:** `002` §11.5 step 2 (macro-skill distillation — *"turns 50k tokens of agent reasoning into a 500-token tool call"*) fused with the prior `007` §8.4 (memoized witnesses as a Tier-0 deterministic flywheel) and disciplined by `006`'s promotion protocol.

### 5.1 The four tiers, and why the order matters

```text
T0  MEMOIZATION            a verified result cached by (goal_digest, D_H-invariant inputs)
    → an identical sub-task is discharged at ~zero cost, DETERMINISTICALLY
    → needs NO corpus, NO statistical power, NO training run.  COMPOUNDS ON DAY ONE.

T1  MACRO-TOOL COMPILATION recurring verified multi-turn patterns are compiled into ONE
    deterministic tool with a declared schema and a declared capability ceiling
    → collapses a 15-turn reasoning loop into a single mediated tool dispatch

T2  SKILL CARDS            residual patterns that resist compilation become retrieval-ranked
    procedure cards with Elo-decayed utility (§5.3)

T3  DPO / DISTILLATION     turn-level (chosen, rejected) pairs train cheaper models to
    match frontier decision quality on this substrate's task classes (§5.4)
```

**Every predecessor proposal defers *all* compounding to T3.** That is a mistake of sequencing: T3 needs hundreds of paired instances before it says anything, while **T0 lowers cost from the first repeated sub-task and does so with a hash table.** T0 is authorized at **M-5**; T1–T3 at M-10.

### 5.2 Macro-Tool Compilation — the mechanism, and its hard constraint

```text
DETECT     mine verdict-PASS trajectories for effect n-grams with high verdict-conditional lift
           lift(g) = P(pass | g ⊂ τ) / P(pass)          computed over the SIGNED verdict only
COMPILE    emit a candidate plugin:  plugin.yaml + deterministic implementation
           + JSON-Schema'd verbs + a capability ceiling ⊆ the union of the n-gram's own grants
ADMIT      the candidate is a PLUGIN. It enters through discovery → resolve → VERIFIED → activate
           like any other, and its digest enters D_H.
PROVE      paired exact McNemar (§5.4) against the undeletable baseline on the target class,
           reported with cost-per-pass (§2.6). Cheaper AND not-worse, or it does not ship.
```

> **The constraint that keeps this safe.** A compiled macro-tool is **not** a shortcut around the kernel. It is a plugin cell speaking the same JSON-RPC wire, holding a ceiling that is a **subset** of the capabilities the original n-gram actually exercised, and its verbs dispatch through S0–S12 exactly as before. **Compilation collapses tokens, never authority.** A macro-tool that requires a wider ceiling than the pattern it replaces is rejected at compose — that is `RF-42`.

Second constraint: a macro-tool changes `D_H`, so it is **never** hot-swapped into a running composition (`ADR-0072` §3). It becomes available to the *next* compose.

### 5.3 Skill cards — hybrid retrieval and Elo eviction

`S_i = (v_i, Pattern_i, Procedure_i, E_i, t_created, t_last_used)`, `v_i ∈ R^384` (dense embedding over error signature + context prompt).

```
                          q · v_i
  Score(S_i, q, K_q) = α ───────── + (1−α)·BM25(K_q, Pattern_i) + β·σ(E_i)     σ(E)=1/(1+e^{−E/400})
                         ‖q‖‖v_i‖
                         └semantic┘   └───── lexical ─────┘        └utility┘

  Y=1 (signed green):  E ← E + K(1 − σ(E − Ē))
  Y=0 (signed red):    E ← E − K·σ(E − Ē)
  idle decay:          E(t) = E₀·e^{−λ_decay(t − t_last_used)}
  EVICT to cold store iff  E < 1000  (E₀ = 1200)  or  idle > 30 days     — archived, never deleted
```

**Why hybrid and not pure vector.** The `Voyager`-family failure is *semantic retrieval collision plus procedural bloat*. `SPEC.md` §4.2 already mandates **structural retrieval before semantic** — Merkle index, tree-sitter tags, personalised PageRank as L4, embeddings as an *optional sidecar declared as a memory capability*. The `β·σ(E_i)` term is the anti-bloat control: **a card that never earned a signed green cannot outrank a structural match.**

**Two hard constraints:** (1) Elo updates key on the **exterior-signed verdict only** — a card cannot raise its own rating; (2) **Elo ranks retrieval, never promotion.** `SPEC.md` §9 refuses scalar reward for promotion; `ADR-0015` makes promotion a partial order over a frontier. Elo decides what is *shown*; McNemar decides what is *shipped*.

### 5.4 Unforgeable DPO harvest and the exact paired promotion protocol

**The pairing key — turn-level, which is why `RF-23` is a precondition:**

```
  key(τ,t) = ( task_digest , D_H , context_digest(τ,t) )

  pair = (τ⁺, τ⁻) with  key(τ⁺,t) = key(τ⁻,t)
                     ∧  τ⁺.verdict.pass = 1  ∧  τ⁻.verdict.pass = 0
                     ∧  both signatures verify against the exterior public key
                     ∧  neither is unattributable_for_promotion            (ADR-0079 D4)
                     ∧  no train/eval overlap and no contamination flag

  chosen = τ⁺.turns[t].proposal      rejected = τ⁻.turns[t].proposal
```

The divergence point is the first turn where `context_digest` differs — **edge-level credit assignment**, which the 2026 graph-based-credit-assignment literature establishes as strictly better than trajectory-level attribution. `turns[].context_digest` is already the right field; it is **useless without populated turns**.

**The promotion protocol — exact, paired, frontier-gated:**

```text
 1  ASSERT  baseline.undeletable = true                      the control cannot be removed
 2  ASSERT  D_H(B) ≠ D_H(C)   ∧   D_X(B) = D_X(C)            same cell, different composition
 3  BOTH arms attempt EVERY instance i ∈ I                   PAIRED. Never two random samples.
 4  2×2 discordance from SIGNED verdicts only:  b = (B pass, C fail),  c = (B fail, C pass)
 5  Analyse DISCORDANT pairs only. Concordant pairs carry no information about the difference.
 6  EXACT McNemar (binomial), NEVER χ²:
        p = 2 · Σ_{k=c}^{b+c} C(b+c, k) · 0.5^{b+c}          two-sided, H₀: P(b) = P(c)
 7  Effect size + interval:  Δ̂ = (c − b)/|I| ;  exact Clopper-Pearson on c/(b+c), mapped to Δ̂
 8  REPORT ALL OF: b, c, b+c, exact p, Δ̂, CI, and CPP for both arms.
        A p-value without an effect size and an interval is NOT a result.
 9  PROMOTE iff  p < 0.05  ∧  Δ̂ > 0  ∧  CI excludes 0
        ∧ candidate is on or improves the admissible PARETO FRONTIER over the 6D economics
        ∧ NO safety/assurance regression on any dimension        ← cannot be averaged away
        ∧ anti-cheat lint clean  ∧ cassette-replay regression green
        ∧ A HUMAN FLIPS THE POINTER                              SPEC §9, ADR-0019
10  EMIT signed promotion event → registry default pointer moves to D_H(C).
    B is retained forever. Rollback restores the pointer without deleting either.
```

**Power, stated so it is not discovered late.** `MEASUREMENT.md`: *"detecting a five-point effect against a realistic floor typically requires low hundreds of paired instances"* and *"most published agent comparisons are underpowered by an order of magnitude."* Between-task difficulty variance dominates every other variance component — **an unpaired comparison of two configurations on two random samples measures which sample was easier.** Sample size is derived numerically and recorded in the family declaration **before** the run.

### 5.5 Why the whole loop is un-gameable — five structural properties

| # | Property | Mechanism |
|---|---|---|
| 1 | The agent cannot forge the label | exterior UID 10002, Ed25519, nonce-and-subject-bound; `runtime/evaluator_gateway.py` is the sole legal writer of `VerdictRecorded` |
| 2 | The denominators cannot drift | `D_H ≠ D_R ≠ D_X`, locked before any experiment existed |
| 3 | Unguarded runs cannot leak in | `unattributable_for_promotion` is **derived by compose**, not declarable (`ADR-0079` D4) |
| 4 | The harvester consumes, never drives | outer loop is a plugin at a graph slot whose ceiling excludes the workspace (`ADR-M0-12`) |
| 5 | A cost win cannot buy a safety loss | promotion is a **frontier**, not a scalar (`ADR-0015`, step 9 above) |

---

## §6 · Final Adjudication of Tensions T-1 … T-9

All six passes converged. This section records the settled ruling, its disposition, its ADR, and its falsifier — **condensed, because the argument is over.** Where this synthesis *changes* a predecessor ruling, the change is flagged **▲**.

| # | Tension | Ruling | Disposition | ADR | Falsifiers | Lands |
|---|---|---|---|---|---|---|
| **T-1** | Manifest: fixed slots vs named component graph | Adopt `mhf.manifest/2`. **▲ `bindings` (typed edges) is the deliverable; the existing `components` path-bag is not a graph.** Slot names → pack convention. `D_H` covers nodes **and edges**. **▲ Cycles PERMITTED**; termination by budget. | `generalize now` | `0077` | `RF-28`…`RF-33` | v0.6.2 / M-3 |
| **T-2** | Spawn: engine-owned vs capability-mediated verb | Design-lock now, **zero kernel diff until M-4 closes**, implement M-6. Delegation targets are **resources** (`agent://spawn/harness/<D_H>`), so a grant may permit one composition and deny another. **▲ `ChildSpawned`/`ChildReturned` already exist in `EventKind` — no new kinds needed.** | `design-only-implement-later` | `0080` | `RF-55`…`RF-59` | design v0.6.1 · code v0.8.0 / M-6 |
| **T-3** | Guardrails: mandatory vs absent-vs-forged | *You may turn a guardrail off; you may never turn off the record that it was off, and you may never forge its output.* Three states: **present/valid · absent/declared · forged/broken**. `unattributable_for_promotion` is **derived by compose**, never declarable. | `generalize now` | `0079` | `RF-34`…`RF-37` | v0.6.2 / M-3 |
| **T-4** | Hollow trajectory (G1 / NOVA-1) | Execute **inside M-2**. The board's carry-to-Wave-4 is overruled in writing. **▲ Unknown measurement is `measurement_status: unavailable` + reason — NEVER zero.** `D_R` defined constructively and emitted. | `strengthen now` | `0078` | `RF-23`…`RF-27` | **v0.6.1 / M-2** |
| **T-5** | `layer0/` absorption timeline | Absorb registry + compose into `runtime/`, prove with NOVA-4, **then** delete. `layer0/events/` is **not absorbed** — it is dead weight with live twins. **▲ Deletion includes `pyproject.toml:40` `include = [… "layer0*"]`.** | `lock now` | `0081` | `RF-38`…`RF-45` | v0.6.2 / M-3 |
| **T-6** | Loop as mechanism | Published as a bound claim with a 12-month Standing Challenge, adjudicated at M-8 by the four validation topologies running multi-pack with zero engine diff. | `keep, document` | `0082` | `RF-65`, `RF-66` | v0.6.1 / M-2 (doc) |
| **T-7** | `K ≪ N` — asserted, never tested | **NOVA-2 is a hard M-3 entry gate.** SIGKILL mid-turn → cold fold in a fresh interpreter → reconcile → resume → complete. Green ⇒ M-7 is a scheduling refactor. Red ⇒ M-3 must not build on a false premise. | `strengthen now` | `0082` | `RF-25` | **v0.6.1 / M-2** |
| **T-8** | Governance mass | Collapse to the Clean Triad — SPEC + ADR log + one board — **at M-5, forbidden before M-4 closes.** Mid-flight surgery during Waves 2–3 is strictly worse than the duplication. | `revisit after M-4` | `0082` | — | v0.7.0 / M-5 |
| **T-9** | Five-SPI freeze | Freeze **stands** through M-8; reviewed at **M-9** against the mature graph. A sixth SPI requires two independent implementations, a stable wire contract, a boundary owner, and **deletion of more complexity than it adds**. `IAggregator` may be dissolved by `mhf.manifest/2`'s multiplicity; `IScheduler` is **provisionally refused** (the scheduler is Decision Plane). | `revisit after M-4` | `0082` | — | v0.9.0 / M-9 |

### 6.1 The two tensions this synthesis adds

| # | Tension | Ruling | ADR | Falsifiers | Lands |
|---|---|---|---|---|---|
| **T-10** | **Execution strategy: hardcoded loop vs priced frontier.** Today the loop, tier, context budget, and repair-round count are fixed per composition. There is nowhere to declare *"this task class is worth 35k tokens and 60 s; that one is worth 2k and 1 s."* | Adopt the **Pareto Router** (§2). Profiles are manifest data; selection is a constrained minimization retaining a frontier; the router is planner-side and never a second authorization path. | `0083` | `RF-46`, `RF-47`, `RF-48` | schema v0.6.2 / M-3 · active v0.9.0 / M-7 |
| **T-11** | **Compounding: statistical-only vs deterministic-first.** Every predecessor defers *all* cost collapse to DPO at M-10, which needs hundreds of paired instances before it says anything. | Adopt the **four-tier flywheel** (§5). **T0 memoization ships at M-5** and compounds deterministically from the first repeated sub-task; T1 macro-tool compilation and T2/T3 land at M-10, each admitted only through paired exact McNemar. | `0084` | `RF-52`, `RF-53`, `RF-67`, `RF-68` | T0 v0.7.0 / M-5 · T1–T3 v1.0.0 / M-10 |

---

## §7 · Drafted Append-Only ADR Catalog — `ADR-0077` … `ADR-0084`

> **Status.** Complete proposed texts, ready to be written to the named paths. **Drafts until committed with a Director signature.** Per `ADR-0000` each names what it narrows or extends and states its reversal condition; per `ADR-0074` **a concept without a bound falsifier is not locked**.
>
> **Falsifier namespace.** `F-01…F-25` exist with *different meanings* in `docs/04_annex/KERNEL.md` (kernel controls, embedded in ~19 source and test files) and in the `002` register (bound falsifiers, embedded in docs and `test/falsifiers/`) `[VERIFIED]`. `ADR-M0-02` names only `I-*`, `ADR-*`, `S-M*`. **Ruling (`ADR-0082` D5):** `F-*` stays with the annex; the register renames to **`RF-*`**, with the one-time alias `RF-01 ≡ F-01 … RF-22 ≡ F-22`. **New falsifiers begin at `RF-23` in one monotonic sequence — §9.3 is authoritative and there is no second numbering anywhere in this document.**

---

### 7.1 `ADR-0077` — The Named Component Graph, and its edges

**Path:** `docs/05_adr/0077-named-component-graph-with-typed-bindings.md`

**Status.** `accepted` — v0.6.1 lock, v0.6.2 / M-3 implementation.
**Narrows / extends.** Extends `ADR-0071` (`D_H` covers the graph, principle unchanged) and `ADR-0072` (components are plugin instances). Narrows `SPEC.md` §2.3's fixed-key example by superseding the shape, not the semantics. Does not reopen `0069`, `0070`, `0073`, `0074`.

**Context.** `schemas/mhf/harness_manifest.schema.json#/$defs/PluginBindings` binds six keys under `additionalProperties: false` — a five-hole agent shape that expresses one ReAct coding agent exactly and cannot express a critic loop (two planner-kind components with declared roles), debate (N proposers + aggregator), tree search (expansion/scoring/selection as separate policies), evolutionary search, or a dual-gate research agent.

Two verified facts drive timing and cost. **First**, `D_H` is computed over the manifest pre-image (`domain/artifacts/manifest.py:83-95`); changing the shape changes every `D_H`, which costs one deliberate re-attribution of a pre-production corpus before M-4 and a full schema + `D_H` + pack + corpus migration after it. **Second — and this corrects a claim in the prior draft** — `domain/artifacts/manifest.py:64` types `components` as `tuple[tuple[str, tuple[str, ...]], ...]`: a **role → paths bag with no edges**. Converging the two parsers onto that shape buys the *node* half and **nothing on the edge half.** The edges are the product.

**Decision.**

- **D1.** The manifest becomes a **named component graph**, published as `mhf.manifest/2`: `components: {<name>: {kind, ref, config, ceiling, isolation, spawn_grant}}` plus **`bindings: [{from, to[], relation}]`**.
- **D2.** `kind` is one of the five frozen SPI kinds (`ADR-M0-03` is **not** reopened). **What changes is that `kind` no longer implies cardinality one.** A composition MAY declare N components of the same kind under distinct names.
- **D3.** Slot names survive as **pack convention**, never schema constraint. Nothing in `compose()`, `kernel/`, or `agency/` may key on a component name. `if name == "planner"` in `runtime/` is a boundary violation in disguise.
- **D4.** `D_H` extends over **component names, kinds, resolved refs and digests, per-component config digests, per-component ceilings, isolation tiers, AND the binding edge set** — in addition to system prompt, harness ceiling, approval policy, and model routes. **Two graphs differing only in one binding edge MUST NOT share `D_H`.** Principle unchanged (`A-5`).
- **D5.** **▲ Cycles are PERMITTED.** A critic loop and a debate-with-rebuttal are cyclic. Termination is enforced by the budget algebra — `turns`, `depth`, additive ceilings — **never** inferred from acyclicity. Self-edges are rejected. The compiler rejects: unknown refs, unresolvable semver ranges, unregistered `kind`, unknown binding endpoints, unsatisfied required ports, capability widening, and **unconsumed security-relevant components** — all at compose, never at runtime (`ADR-0005`).
- **D6.** **One parser.** `agency/manifests/loader.py` is deleted as a second YAML→harness path. Exactly one function produces a `HarnessManifest` from bytes. Board task `3.2-C` is re-labelled **`DEV-LOCAL` → `DIRECTOR`** and folded into sprint 3.3 — *a `DEV-LOCAL` task must never be the vehicle for a decision that fixes `D_H`'s pre-image.*
- **D7.** **Flatness at the composition surface is imported; absence of a privileged core is refused.** These are orthogonal and this ADR takes exactly one. Every component ceiling intersects the harness ceiling **fail-closed**; an empty ceiling authorizes nothing; no component may write a privileged kind. `SPEC.md` §9's refusal of "no privileged core" flatness stands and is restated here so a future reader cannot conflate them.
- **D8.** The graph is **not** a workflow DAG and grants no execution semantics. `bindings` declares *what a component may address*, not *when it runs*. Execution order remains the universal turn loop plus spawn topology. The `relation` roster is **closed** — an open string set is how a DAG engine smuggles itself in.
- **D9.** `mhf.harness/1` is **frozen, not deleted**; readable through M-4 for corpus attribution, normalised to `/2` at parse, acceptance removed at M-5.

**Compile fixtures — the acceptance test for the schema.** Five reference topologies MUST compile to five distinct `D_H` **with zero diff** under `vanguard/packages/kernel/` and `agency/episode/engine.py`: `react-single` · `generator-critic` · `debate-two` · `tree-search` · `stigmergic-swarm`. *Compiling* is the whole M-3 test; *executing* them is M-8's job. Separating those is what keeps this a Wave-3-sized change.

**Bound falsifiers.** `RF-28` two same-kind components with distinct names compile · `RF-29` five topologies → five distinct `D_H`, zero engine diff · **`RF-30` binding-edge change changes `D_H`** (the edge-half proof) · `RF-31` component ceiling intersects fail-closed · `RF-32` unknown endpoint / unconsumed authority component fails **at compose** · `RF-33` exactly one manifest parser exists.

**Reversal condition.** A topology the graph cannot express that a fixed-slot template can; or measured evidence that graph resolution at compose materially degrades run latency. Preference, aesthetics, and migration inconvenience are not sufficient grounds.

---

### 7.2 `ADR-0078` — The trajectory content contract (NOVA-1); I-9 operationalised

**Path:** `docs/05_adr/0078-trajectory-content-contract.md`

**Status.** `accepted` — implements **immediately, inside M-2**.
**Narrows / extends.** Narrows `F-12` (schema validity only) by replacing it with `RF-23` (content assertions). Extends `ADR-0074` §7 and `SPEC.md` I-9. **Overrules** the `sprint_active.md` follow-up row carrying per-turn cost to Wave 4.

**Context.** `runtime/trajectory.py:10` defines `_ZERO_COST`, emitted at line 53 (every turn) and line 75 (every episode) `[VERIFIED]`. The returned object omits `model_routes_used`, `execution_digest`, and `attribution`, all optional in the schema — so the record validates. **Every completed episode emits a record that is schema-valid, cryptographically attributable, and unusable.**

I-9 requires a record that is *"without transformation, a valid harvest row"* and states that *"a digest over `{ids, n}` is not this invariant."* `F-12` asserts only schema validity, which a content-free record satisfies. **The falsifier is green while the invariant it certifies is violated** — the same defect class as `F-18` (a linter narrower than its invariant) and `check_markdown_links.py` (a `LINK PASS` over two files).

**The board's objection — *"real per-turn cost needs the governor's settled ledger"* — is correct but insufficient.** The settled ledger already exists at `EpisodeCompleted`: `Receipt.cost` is a `Reservation`, `BudgetCommitted`/`BudgetReleased` are ledgered kernel events, and `assemble_trajectory` **already receives both `events` and `receipts` as parameters.** The data is in the function's arguments and is being discarded.

**Decision.**

- **D1. Per-turn cost is computed, not stubbed.** `_ZERO_COST` is deleted. For each turn `t`:
  `cost(t) = ⊕ {BudgetCommitted.cost : causation_id ∈ turn_t.effect_ids} ⊕ {Receipt.cost} ⊕ {model usage}`, where `⊕` is component-wise addition over the **additive** dimensions only. Structural ceilings `{depth, turns}` are **not costs** and MUST NOT appear in a `CostVector` — the schema already fails this closed with `additionalProperties: false`.
- **D2. Episode cost reconciles exactly:** `episode.cost = Σ_t turn_t.cost + cost_overhead`, component-wise, with `cost_overhead` explicitly identified. A discrepancy is a defect, not rounding.
- **D3. `D_R` is defined constructively and emitted.** `execution_digest` is currently **never assigned anywhere in the tree** `[VERIFIED]`. It becomes
  `D_R = JCS-SHA256{ harness_digest: D_H, runtime:{python, platform, package}, environment:{kind, digest}, model_identity:[{tier,provider,model,model_fingerprint}…] sorted, oracle_identity }`.
  `D_R ≠ D_H` MUST hold and MUST be asserted. Without `D_R`, a corpus cannot distinguish *"same harness, different model build"* from *"same run"* — which silently invalidates every router experiment and therefore all of Pillar I.
- **D4. ▲ Unknown ≠ zero.** Where a dimension is genuinely unmeasurable, the record carries `measurement_status: "unavailable"` **plus a reason code** — never a zero. A fabricated zero is indistinguishable from a measured zero, and the whole point of I-9 is that the corpus never lies. A genuinely free local model may record `usd_micros: 0`; `tokens` and/or charged `millis` still establish non-hollowness.
- **D5. Latency is a first-class dimension.** `millis` is **charged compute time**, never wall-clock under concurrency. Under I-11 they coincide; the distinction is locked now so M-7 cannot silently redefine the corpus.
- **D6. Cost is written by the governor, never by the planner.** Trajectory assembly reads ledgered kernel events and receipts. **No plugin, planner, or model adapter may author a cost field.** Self-reported cost is a forgery surface identical in kind to a self-reported verdict.
- **D7. Required-now vs required-later**, stated so no field becomes a false green:

| Field | Required from | Why not earlier/later |
|---|---|---|
| `turns[].cost` (`tokens`>0 or `millis`>0 on invoked turns) | **M-2** | the core defect |
| `cost` (episode, reconciles exactly) | **M-2** | checkable now |
| `model_routes_used[].model_fingerprint` | **M-2** | provider metadata, available at the adapter |
| `execution_digest` (`D_R`) | **M-2** | computable at compose + wire time |
| `verdict` (SignedVerdict **xor** null + `verdict_absent_reason`) | **M-2** | already ledgered; only the reasoned-null case is new |
| `guardrails`, `unattributable_for_promotion` | **M-3** | depends on `ADR-0079` |
| `profile_used`, `escalations[]` | **M-3** | depends on `ADR-0083` |
| `attribution.prefix_hits` | **M-10** | the pack cannot compute it before the harvester exists — requiring it now manufactures a false green |

- **D8. No historical rewriting.** Pre-fix rows are tagged `legacy_incomplete` and excluded from promotion. They are not back-filled, because the governor's settled cost ledger for a past run is **gone** — this is the only item on the register with a one-way clock.

**Bound falsifiers.** `RF-23` populated trajectory (all eight assertions) · `RF-24` planner cannot author a cost field · `RF-27` `D_R` present and `≠ D_H` · `RF-49` (M-4) the **real run's** trajectory carries non-zero cost.

**Reversal condition.** Measured evidence that per-turn cost accounting materially distorts the latency it records, or a demonstration that a downstream learner performs equally well on cost-free rows.

---

### 7.3 `ADR-0079` — Absent vs Forged: guardrails are declarable, evidence never is

**Path:** `docs/05_adr/0079-absent-vs-forged-guardrails.md`

**Status.** `accepted` — v0.6.2 / M-3.
**Narrows / extends.** Extends `ADR-0072` (evaluator exteriority) and `ADR-0074` (writer authority). Narrows the implicit reading under which an exterior evaluator is mandatory per composition. Does not weaken `ADR-0004`.

**Context.** The guardrail *mechanism* is mandatory **and** the guardrail *policy* is mandatory, and only the second needs to be. A research agent, a math pack, or a pure-compute optimisation loop should not need a UID-10002 daemon and a preregistered oracle to run. Left unresolved this produces exactly one outcome: under deadline pressure someone builds a *bad* escape hatch — a debug flag, an env-var bypass, a test-only unsigned path. **This ADR is the good escape hatch, designed before the pressure exists.**

**Decision.**

- **D1. Three evidence states, and only three.**
  **present/valid** — a required evaluator produced a correctly-bound signed verdict.
  **absent/declared** — the manifest declares `guardrails.evaluation: none` with a **reason code** and an assurance class ineligible for promotion.
  **forged/broken** — evidence was required or claimed but is missing, unsigned, wrongly bound, self-produced, unreachable, or tampered. This maps to `instrument_error` / `EvaluationTampered`. **It never silently degrades into declared absence.**
- **D2. Declared absence is composition identity.** The declaration enters the `D_H` pre-image. Two harnesses differing only in whether an evaluator was declared MUST NOT share `D_H`. **The declaration is frozen at compose, so it cannot be selected after observing the result.**
- **D3. Consequence is recorded.** The trajectory carries `guardrails: {evaluation, sandbox, approval}`, `verdict: null`, and `verdict_absent_reason: "guardrail_absent"`. A null verdict with a *declared* oracle is an instrument error, not a legitimate absence.
- **D4. `unattributable_for_promotion` is DERIVED, never DECLARED.** Computed by `compose()` from the resolved graph and stamped on `FrozenHarness`. **Not** a manifest field, **not** plugin-writable, **not** settable by any runtime flag. Without this clause the entire model is theatre: a composition could declare itself attributable while running unguarded.
- **D5. An unsigned verdict is categorically illegal under every composition.** `evaluation: none` means **no verdict** — it never means an easier verdict. Such a run may complete operationally, but it cannot produce `passed`, license a verdict-gated memory write, enter a DPO pair, or promote anything. **A compute-only pack may still use a sandbox** — the guardrail being declared absent here is *evaluation evidence*, not effect mediation.
- **D6. The seven permanent non-negotiables** are ratified as the fixed substrate boundary. No composition, declaration, policy, or future ADR short of an explicit reversal may weaken them:

| # | Non-negotiable | Enforced by `[VERIFIED]` |
|---|---|---|
| N-1 | Writer authority on privileged kinds | `runtime/ledger_emitter.py:37-60` — 22 kinds → owning roles; `WriterAuthorityError` |
| N-2 | Envelope lineage by construction | `LINEAGE_FIELDS` at `ledger_emitter.py:27-33` |
| N-3 | Fail-closed selector inclusion | `domain/selectors/resource_selector.decide()` — total; unknown pair ⇒ deny (`K-48`) |
| N-4 | Ledger-as-truth, proven by **cold** replay | `ColdReplayParity`, `test/runtime/test_ledger_truth.py` |
| N-5 | Capability attenuation on spawn | `kernel/attenuation.py:183` auto-seal + `kernel/policy.py` step 1b (`ADR-0067`) |
| N-6 | Signature on any verdict that **is** claimed | `runtime/evaluator_gateway.py` — sole legal writer, refuses unbound bodies |
| N-7 | JCS (RFC 8785) as the sole byte source | `domain/canonicalisation/jcs.py`; `check_duplication.py --enforce` |

  **Everything else is policy.** That sentence is the substrate's actual API contract.
- **D7. Absence is per-component as well as per-composition.** A graph may declare `container` for `terminal` and `in_process` for `context`. `in_process` remains a **policy-granted privilege that still speaks the wire**, never a default (I-6, `ADR-0072`).

**Bound falsifiers.** `RF-34` `evaluation: none` compiles and changes `D_H` · `RF-35` unsigned verdict rejected even under a declared absence · `RF-36` the attributability flag is derived and not manifest-writable · `RF-37` `in_process` requires an explicit policy grant.

**Reversal condition.** Evidence that a declared-absent guardrail produced a promotion-eligible result — i.e. D4 failed to propagate — in which case guardrails become mandatory again until it is fixed.

---

### 7.4 `ADR-0080` — `agent.spawn` as a capability-mediated kernel verb (design-locked)

**Path:** `docs/05_adr/0080-agent-spawn-capability-mediated-verb.md`

**Status.** `accepted (design-locked, implementation deferred)` — design v0.6.1; implementation authorized at **M-6 / v0.8.0** and **forbidden before M-4 closes**.
**Narrows / extends.** Extends `ADR-0070` by moving the delegation primitive from the engine to the reference monitor. Constrained by `ADR-0023` (TCB ceiling) and `ADR-0075` (stop line).

**Context.** `EpisodeEngine.spawn(...)` (`agency/episode/engine.py:531`) is a **privileged engine call**; `IPlanner` exposes only `plan/observe/reflect`. Any algorithm whose *structure is recursion* — tree search, hierarchical decomposition, conditional delegation, the `SPEC.md` §5.1 outer loop — has nowhere to live except inside the engine. That is *"a new engine per algorithm"*, which is `ADR-0070`'s own stated reversal condition.

**A forensic correction, verified this pass.** `engine.py:556-571` documents at length that *"`StandardPolicy.authorize` … never checks that `request.action` is a member of `requested_scope.actions`"* and that closing it *"needs its own ADR (`ADR-0054`)"*. **That is stale.** `kernel/policy.py` step 1b implements sealed membership under `ADR-0067`, and `kernel/attenuation.py:183` sets `sealed = request.sealed or request.actions < parent.actions` — so `attenuate()` **auto-seals on every spawn that withholds verbs**. The engine-side refusal is now defence in depth. A stale comment inside the TCB's nearest neighbour is a real defect, because a reviewer who trusts it mis-models the kernel.

**Decision.**

- **D1. Design now; code later.** The verb spec, event shape, budget algebra, and falsifier suite below are normative from v0.6.1. **The kernel gains nothing but tests in Waves 1–4.** A `vanguard/packages/kernel/` diff inside the M-4 evidence window **voids the evidence bundle**, because the nine-row run would no longer be attributable to the reviewed kernel.
- **D2. Verb specification.**

```text
verb      : agent.spawn
sink      : PRIVILEGED                    → SinkRegistry.inferred_class ⇒ requires a bound grant
selector  : {kind: generic, uriPattern: "agent://spawn/harness/<D_H>"}
args      : {harness_digest, brief, capabilities[], reservation, parent_lease, graph_entrypoint}
receipt   : {request_digest, outcome, child_principal_id, child_episode_id, cost, lease_id, grant_digest}
events    : ChildSpawned / ChildReturned          ▲ ALREADY EXIST in EventKind — no new kinds
```

  **Delegation targets are resources.** A grant may permit spawning one harness digest and deny another — this is what converts *"may this agent delegate?"* into *"may this agent delegate **to this composition**?"*, and it is the property that makes heterogeneous swarms governable.
- **D3. Effective child authority is an intersection, and its budget is a sublease:**
  `A_child = A_parent ∩ A_manifest ∩ A_plugin ∩ A_request`, with the reservation a **parent-linked sublease, not copied counters.** Additive dimensions debit the parent's *remaining* vector; `depth` increments with `child.depth = parent.depth + 1 ≤ root.max_depth`; **sibling depths are not summed**; `turns` is per-episode.
- **D4. Child output enters the parent context as `UNTRUSTED_DERIVED` at minimum** and can never authorize widening (`K-33`).
- **D5. S0–S12 mapping** (normative; no stage is skipped): S0 typed request, no child exists · S1 validate and reject unknown fields · S2 resolve adapter and graph entrypoint **before any lease** · S3 JCS-digest all authority-relevant inputs · S4 widening vs held authority, unknown comparison ⇒ widening · S5 policy on the **exact descriptor** · S6 descriptor-bound expiring grant · S7 reserve the child sublease · S8 re-verify descriptor/principal/expiry/attenuation **at the point of spawn** · S8a durable intent **before** any child process or workspace exists · S9 create isolated principal/workspace/session, **no implicit inherited handles** · S10 debit actual use including overruns, return unused reserve · S11 release on every terminal, failure, and cancellation path · S12 emit lineage and outcome **after** release, never leaking secrets or raw context.
- **D6. Singular Court and Attenuated Reachability.** A swarm has **one** judge exterior to every participant; depth and heterogeneity do not multiply the evidence plane. Unreachability must be **monotonic under delegation** — the evaluator endpoint MUST be expressed as a resource in the selector algebra so reachability is attenuated rather than ambient. `[VERIFIED]` it is not today: `adapters/evaluators/client.py` is composition-wired, not selector-gated. Tracked as `RF-58`, landing with this ADR.
- **D7. TCB budget: ≤ 40 logical LOC.** Headroom is `1438 − 1365 = 73`. Exceeding 40 is a design failure to escalate, **not** grounds to raise the ceiling.
- **D8. `spawn` remains the only delegation primitive.** No `MetaAgent`, no `SwarmEngine`, no `Orchestrator` as a type. Swarm coordination is a **policy over agents**; causal relations are **projections of events**.

**Bound falsifiers** (authored red at M-3, run at M-6). `RF-55` planner without a spawn grant cannot delegate · `RF-56` spawn is a mediated effect with a receipt · `RF-57` spawn selector denies an undeclared `D_H` · `RF-58` child cannot reach the evaluator without a selector grant · `RF-59` child grant wider than parent is denied **whole**, not silently intersected (`K-26`) · `RF-26` sealed child scope rejects an out-of-scope action **at S5** with the engine-side refusal disabled (the stale-docstring scenario).

**Reversal condition.** `RF-55`…`RF-59` unimplementable within 40 LOC, or measured evidence that mediating every spawn through S0–S12 makes deep delegation topologies impractical. Either reopens the engine-owned option — with data.

---

### 7.5 `ADR-0081` — Terminal absorption of `layer0/`; NOVA-4; two new plugin event kinds

**Path:** `docs/05_adr/0081-layer0-terminal-absorption-and-plugin-lifecycle.md`

**Status.** `accepted` — v0.6.2 / M-3. Contains a **Director-only escalation** (D3).
**Narrows / extends.** Extends `ADR-0069` and `ADR-M0-13`. Discharges `SPEC.md` §1's behavioural-parity precondition. Extends `ADR-0074`'s writer table and `ADR-0076` §6.

**Context.** `layer0/` holds exactly `compose/compiler.py`, `registry/{broker,grants,isolation,lifecycle,sandbox,validator,worker}.py`, and `events/{emitter,envelope,store,taxonomy}.py` `[VERIFIED]`. The headline forensic defects — the fabricated unsigned `"pass"` and the fail-open empty-capability branch — died at 2.2-B with `kernel/`, `scheduler/`, and `spi/`. But registry and compose are the **only** plugin-lifecycle code in the tree and have **never run on the canonical path**, and Wave 3 rests the entire framework claim on them.

**Three concrete instances of that risk, all verified this pass:**

1. **The FSM cannot ledger two of its seven states.** `layer0/registry/lifecycle.py:33-39` maps `RESOLVED`, `ACTIVATED`, `QUIESCING`, `RETIRED`, `FAULTED` to event kinds. **`DISCOVERED` and `VERIFIED` map to nothing**, and `_go()` guards with `if kind is not None:` — so those transitions mutate state and emit **silently**. `EventKind` confirms only five `PLUGIN_*` members exist. **`VERIFIED` is where the capability-ceiling policy check happens** — the most security-relevant transition leaves no evidence, and the M-3 gate *"every transition ledgered"* is **unsatisfiable against the closed 56-kind catalog.**
2. **The old compiler computes `intersect_ceilings` and discards the result** — a fail-open shape that must not be copied forward.
3. **`pyproject.toml:40` reads `include = ["vanguard*", "layer0*"]`.** Setuptools still packages the fork. `rm -rf layer0/` without this line is cosmetic deletion.

**Decision.**

- **D1. Absorb, prove, then delete — in that order.** `layer0/registry/` → `runtime/registry/`; `layer0/compose/compiler.py` merged into `runtime/compose.py` as compose v2. `SPEC.md` §1's parity precondition is discharged by NOVA-4 plus the `ADR-M0-13` echo-plugin walk, **not** by code review.
- **D2. `layer0/events/` is NOT absorbed.** It is dead weight with live packages twins (`runtime/ledger_emitter.py`, `domain/ledger/events.py`, `adapters/stores/event_store.py`). It is mapped to the canonical contracts and deleted. Stated explicitly so no developer "absorbs" a fourth event taxonomy.
- **D3. Two new event kinds — Director escalation, ruled here.** `PluginDiscovered` and `PluginVerified` are added to `EventKind` (schema-generated, `A-4`/`I-1`), to `EVENT_KINDS` (**56 → 58**), to `PRIVILEGED_KIND_OWNERS` as `frozenset({"registry"})`, and to `reducer.py` as fold rules over `LedgerState.plugins`. `CataloguedKindsAreFoldedOrAllowlisted` extends to 58 with **zero** additions to `UNFOLDED_ALLOWLIST` — a lifecycle kind that is catalogued but unfolded is the round-3 M-2 blocker resurfacing at M-3.
- **D4. NOVA-4 is non-negotiable Wave-3 scope.** The six negatives become first-class falsifiers, not implied behaviour. **If Wave 3 will not fit, breadth is shed — never falsifiers.** WASM tier, mandatory plugin signatures, and any second product plugin stay out.
- **D5. Deletion is atomic with its evidence and includes the packaging manifest.** One commit: `rm -rf layer0/` · delete `test/layer0/` · remove the advisory CI step · **remove `"layer0*"` from `pyproject.toml:40`** · a green NOVA-4 run recorded in the commit message. A tree with `layer0/` deleted and NOVA-4 red is worse than the fork.
- **D6. Freeze-at-compose is a deletion precondition.** Unknown refs, unresolvable ranges, unknown endpoints, and empty ceilings fail at **compose**. No code path mutates a frozen composition.

**The complete FSM after this ADR** is in §9.2. **Illegal by construction, each a test:** `RETIRED → *` · `FAULTED → ACTIVATED` without re-traversal · **any transition emitting no event** · a non-`registry` role appending a `Plugin*` kind · a ref resolved at runtime · any mutation of a frozen composition.

**Bound falsifiers.** `RF-38`…`RF-45` (§9.3), including **`RF-43` every FSM transition emits a ledgered event** and **`RF-45` `layer0` is absent from the tree *and* from `pyproject.toml`.**

**Reversal condition.** NOVA-4 red at the parity gate with a diagnosis that the absorbed semantics are irreparable — in which case `layer0/registry/` is deleted **without** absorption and the lifecycle is written fresh, at the cost of Wave 3 growing from "absorb + prove" to "write + prove". Recorded now so the fallback is a decision, not an improvisation.

---

### 7.6 `ADR-0082` — Loop-as-mechanism; cold continuation; and three scheduled reviews

**Path:** `docs/05_adr/0082-loop-as-mechanism-cold-continuation-scheduled-reviews.md`

**Status.** `accepted` — D1/D2 implement in M-2; D3 schedules M-5; D4 schedules M-9; D5 immediate.
**Narrows / extends.** Extends `ADR-0070`, `ADR-0071`/I-4, `ADR-M0-02` (namespaces), `ADR-M0-03` (adds a review date, not a change).

**D1 — The Universal Turn Loop is Mechanism, published with `RF-66`.**

> `observe → propose → authorize → effect → receipt → evaluate → (reflect)*` is **mechanism, never plugin.** Agentic algorithms differ in what they propose and when and to whom they delegate — never in whether an effect is authorized, a receipt recorded, or a verdict signed. Any algorithm expressible at all is expressible as **spawn topology + component-graph wiring + planner policy** over this one loop.
>
> **`RF-66` — the Standing Challenge.** *Name an agentic algorithm that cannot be so expressed, and demonstrate it as a manifest that fails to compile or a behaviour that requires an engine diff.* Refuted ⇒ genuine `ADR-0070` reversal evidence. Unrefuted at **M-8 adjudication (12 months from ratification)** ⇒ the loop is proven and the argument closes by evidence rather than fatigue.

The **M-8 validation suite** is the structured half: debate, critic/revisor, evolutionary search, and multi-agent economic delegation MUST run multi-pack with **zero engine modification** (`RF-65`). A red there is a partial refutation. Competing harnesses make the loop itself a plugin — coherent for them precisely because they have no authority boundary to preserve.

**D2 — `K ≪ N` is proven by NOVA-2 (`RF-25`), a hard M-3 entry gate.** The deciding question: *is an episode's continuation reconstructible from the ledger alone, or does resuming require the live Python object?* The test asserts: SIGKILL mid-turn (not a graceful shutdown, which may flush state a crash would not) · fresh interpreter, cold fold from the WAL · **no Python object identity, open lease handle, in-memory callback, or process-local queue is required** · reconstructed FSM, grant tree, and remaining budget are structurally identical · the `prev_digest` chain is continuous across the restart · **already-completed effects are not repeated** · an S8a-started, unresolved effect stays `undeterminable` until reconciled, never assumed failed or successful · the final trajectory references both pre- and post-restart turns and satisfies `RF-23`. **Green ⇒ M-7 is a scheduling refactor. Red ⇒ M-3 must not build on a false premise.**

**D3 — Documentation collapse at M-5, forbidden before M-4 closes.** Target: `SPEC.md` + `docs/05_adr/` + one living board; a senior developer productive from three documents, not seven. GAMMA and the `002` register retire as standing authorities once absorbed; their falsifier tables migrate into the invariant section and the board. **No evidence is destroyed to make navigation tidy** — completed reviews get superseded banners and stay.

**D4 — The five-SPI freeze stands through M-8, reviewed at M-9.** `ADR-M0-03`'s guard is reaffirmed; what is refused is its hardening into *"there are five SPIs forever."* A sixth requires **two independent implementations, a stable wire contract, a boundary owner, and deletion of more complexity than it adds.** *"Useful component type"* is not sufficient. Two candidates are named now so the review has subjects: **`IAggregator`** — which `mhf.manifest/2`'s multiplicity may **dissolve**, itself the strongest argument for reviewing *after* the graph matures — and **`IScheduler`**, **provisionally refused** because the scheduler decides who acts when, which is Decision Plane, and making it pluggable moves authority above the extension line.

**D5 — The `RF-*` namespace is opened.** `F-*` stays with `KERNEL.md`; the register renames to `RF-*` with the one-time alias table. `RF-72` (a linter asserting falsifier-id uniqueness across the annex and the register) prevents recurrence.

**Bound falsifiers.** `RF-66` the Standing Challenge · `RF-25` cold continuation · `RF-72` namespace uniqueness · `RF-65` four topologies multi-pack, zero engine diff.

**Reversal conditions.** D1: a successful `RF-66` demonstration. D2: `RF-25` red — which does not reverse the decision to *test*; it reverses the M-7 scoping assumption. D3: evidence that collapse loses a property the seven tiers were actually providing. D4: an M-9 review concluding a sixth SPI is required, which this ADR anticipates rather than forbids.

---

### 7.7 `ADR-0083` — The Pareto Router: execution profiles as composition data

**Path:** `docs/05_adr/0083-pareto-router-execution-profiles.md`

**Status.** `accepted` — schema v0.6.2 / M-3; **router activation deferred to v0.9.0 / M-7**, gated on `RF-25` and selector soundness.
**Narrows / extends.** Extends `ADR-0077` (profiles are graph data) and `ADR-0074` (the 6D tensor becomes an *objective* as well as a constraint). Does **not** narrow `ADR-0069`/`ADR-0070`: the router is planner-side and holds no authority. Salvages and generalises `runtime/tier_escalation.py` (the D-41 salvage).

**Context.** A composition today fixes its loop, its model tier, its context budget, and its repair-round count. There is nowhere to declare *"this task class is worth 35k tokens and 60 seconds; that one is worth 2k and 1 second."* The consequence is that the substrate hardcodes one point on a four-dimensional surface whose spread is the largest single measured effect in the harness literature (**64.7% → 78.4%** on identical model weights). Worse, `tier_escalation.py` already implements a *fragment* of this — Free→Cheap→Frontier on `verdict_fail` — as a runtime module rather than as composition data, which means it is neither declarable, nor attributable through `D_H`, nor measurable per task class.

**Decision.**

- **D1. Profiles are manifest data.** `mhf.manifest/2` gains a `profiles: {<name>: {weights, ceilings, topology_preset, escalate_to?}}` block. The four reference profiles (`α` flash · `β` balanced · `γ` deductive · `δ` adaptive) ship as **pack convention**, exactly like slot names — a fifth profile is a manifest edit, never a code change.
- **D2. Profiles enter `D_H`.** A composition differing only in its profile weights is a different composition. Without this, no A/B over routing policy is attributable and Pillar I is unmeasurable.
- **D3. Selection is constrained minimization retaining a frontier** (§2.2). `λ_j ≥ 0` are **declared policy parameters, never learned excuses to violate a ceiling.** Feasibility and assurance are checked first. **No scalar score may allow a cost win to offset a safety or assurance regression** (`ADR-0015`, `SPEC.md` §9).
- **D4. The router is planner-side and holds no authority.** It selects *what to propose and at what tier*. It **never** decides whether an effect is authorized, never widens a ceiling, never pre-filters authorization, never mints or reads a verdict, and never authors a cost field. **A "sub-5 ms pre-flight filter" is advisory only and may never become a second authorization path.** S0–S12 remains the sole mediator.
- **D5. Escalation carries the falsifier, not the transcript.** On a signed `verdict_fail`, `δ` captures the specific failing assertion / denied capability / overflow signature as a durable event and forwards **only** (workspace delta + falsifier) to the next tier. Every attempt debits the **same** episode's additive budget — escalation is not a new wallet.
- **D6. Cost-per-pass is a first-class reported metric** (§2.6), computed per `(strategy, task_class)` from ledgered cost and signed verdicts. Every strategy claim in this project reports `CPP` alongside resolve rate, or it is not a claim.
- **D7. Activation is gated.** The **schema** lands at M-3 so that `D_H` is stable across the boundary and profiles are recorded in the corpus from M-3 onward. The **router** activates at M-7, after `RF-25` (cold continuation) and selector-disjointness measurement — because speculative parallel branching under `γ` is concurrency, and I-11 stands until M-7's gate fires. Until then `profile` is recorded and honoured **sequentially**.

**Bound falsifiers.** **`RF-46` a profile change changes `D_H`** · **`RF-47` the router cannot widen a ceiling or bypass S0–S12** — an attempted widening is denied at S5 and alertable · **`RF-48` escalation debits the same episode budget and forwards only the delta plus the falsifier, never a full transcript replay.**

**Reversal condition.** Measured evidence that profile selection overhead exceeds the spread it exploits on real task classes, or that `CPP` fails to discriminate between strategies that a human reviewer can distinguish. Either means the surface is wrong, and the fixed-loop composition returns — with data.

---

### 7.8 `ADR-0084` — Macro-Tool Compilation and the four-tier compounding flywheel

**Path:** `docs/05_adr/0084-macro-tool-compilation-and-compounding.md`

**Status.** `accepted` — **T0 (memoization) at v0.7.0 / M-5**; T1–T3 at v1.0.0 / M-10.
**Narrows / extends.** Extends `ADR-0072` (a macro-tool is a plugin on the wire), `ADR-0015` (promotion is a partial order), and `SPEC.md` §5.4 (skill synthesis). Narrows nothing.

**Context.** Every predecessor proposal defers **all** compounding to a DPO pipeline at M-10 that needs low hundreds of paired instances before it can say anything. That is a sequencing error: a substrate that solves the same sub-task a hundred times and pays full price each time is leaving a deterministic, ML-free cost reduction on the table for four milestones. Separately, `002` §11.5 identifies the sharpest single compounding mechanism in the predecessor set — *"turns 50k tokens of agent reasoning into a 500-token tool call"* — and no other proposal carries it.

**Decision.**

- **D1. Four tiers, in this order** (§5.1). **T0 memoization ships at M-5 and needs no corpus, no statistical power, and no training run.** T1 macro-tool compilation, T2 skill cards, T3 DPO land at M-10.
- **D2. T0 — memoized results are keyed on `(goal_digest, behaviour-affecting inputs)` and are evidence-gated.** A cached result is reusable **only** if its originating episode carried a signed `verdict.pass` and was **not** `unattributable_for_promotion`. Cache hits are ledgered as such, and the trajectory records `memo_hit: true` with the source `episode_id` — a memoized turn is attributable, not invisible. Any change to the resolved graph, ceiling, or model route invalidates the entry, because the key includes them.
- **D3. T1 — a compiled macro-tool is a PLUGIN, not a shortcut.** Detection mines verdict-PASS trajectories for effect n-grams with high verdict-conditional lift; compilation emits `plugin.yaml` + a deterministic implementation + JSON-Schema'd verbs + a **capability ceiling that is a subset of the union of the grants the original n-gram actually exercised.** The candidate enters through `DISCOVERED → RESOLVED → VERIFIED → ACTIVATED` like any other plugin, speaks the same JSON-RPC wire, and its digest enters `D_H`. **Compilation collapses tokens, never authority.** A macro-tool requiring a wider ceiling than the pattern it replaces is **rejected at compose** (`RF-67`).
- **D4. Admission is by paired exact McNemar** (§5.4), reported with cost-per-pass for both arms. **Cheaper *and* not worse, or it does not ship.** A macro-tool that is faster and less reliable does not promote — it joins the frontier or is discarded.
- **D5. No hot-swap.** A new macro-tool changes `D_H` and therefore becomes available to the **next** compose, never to a running composition (`ADR-0072` §3).
- **D6. T2 Elo ranks retrieval, never promotion.** Elo updates key on the exterior-signed verdict only; a card cannot raise its own rating. Cards enter a manifest **only** through D4's pipeline. Eviction archives to cold storage; **nothing is deleted**, because the corpus is append-only evidence.
- **D7. T3 pairs are turn-level and filtered** (§5.4): identical `(task_digest, D_H, context_digest)`, divergent **signed** verdicts, both signatures verifying, neither `unattributable_for_promotion`, anti-cheat lint clean, no train/eval overlap.
- **D8. The harvester consumes; it never drives.** It runs as a plugin at the `outer` graph slot with a capability ceiling restricted to manifest-mutation proposals, skill writes, and oracle preregistration — **never the workspace** (`ADR-M0-12`, `ADR-0041`).

**Bound falsifiers.** `RF-52` a memo hit is ledgered, attributable, and invalidated by any `D_H`-affecting change · `RF-53` an unsigned or unattributable episode's result never enters the memo cache · `RF-67` a macro-tool whose ceiling exceeds its source n-gram's exercised grants is rejected at compose · **`RF-68` a macro-tool dispatches through S0–S12 exactly as the pattern it replaced** · `RF-69` exact McNemar matches enumerated binomial cases · `RF-70` promotion denies on any assurance regression regardless of a cost win.

**Reversal condition.** Measured evidence that T0 hit rates on real task distributions are negligible (memoization is a bet on sub-task recurrence, and that bet is falsifiable), or that compiled macro-tools measurably reduce solve rate by over-specialising. Either finding demotes the tier without touching the others.

---

## §8 · Milestone Roadmap & Version Ladder

### 8.1 The ladder

| Version | Name | Content | Cut when | `pyproject` |
|---|---|---|---|---|
| **v0.6.0** | Concept Lock | SPEC + ADRs `0069`–`0076`. Locked (`ADR-0075`). | — | `0.4.5b1` |
| **v0.6.1** | **Evidence & Correction Lock** | ADRs `0077`–`0084` filed · **NOVA-1 (`RF-23`)** · **NOVA-2 (`RF-25`)** · NOVA-3 · `D_R` emitted · spawn design-locked · loop claim published · `RF-*` namespace opened | **M-2 green** | `0.4.5b1` |
| **v0.6.2** | **Extensibility Lock** | `mhf.manifest/2` with **typed edges** · registry FSM with **all seven transitions ledgered** · echo-plugin walk · absent-vs-forged · Pareto **schema** · NOVA-4 · **`layer0/` deleted incl. `pyproject.toml:40`** | **M-3 green** | `0.4.5b1` |
| **v0.6.3** | **Foundation Release Candidate** | The nine-row E2E green on one uninterrupted real run · NOVA-5 · cassette captured · evidence bundle produced | **M-4 evidence produced** | `0.4.5b1` |
| **v0.7.0** | **Foundation MVP + Generality** | **Director attests the same nine-row run** · docs collapse to the Clean Triad · **Pack #2 Math & Formal Deductive Verification** · **T0 memoization** | **M-5 green** | **`0.7.0`** |
| **v0.8.0** | **Mediated Delegation** | `agent.spawn` through S0–S12 · evaluator reachability selector-gated · hierarchical decomposition + tree search as validation compositions | **M-6 green** | `0.8.0` |
| **v0.9.0** | **Controlled Swarm Framework** | Independence groups · `K ≪ N` at scale · **Pareto Router active** · debate / critic / evolutionary / economic-delegation multi-pack with zero engine diff · `RF-66` adjudicated | **M-7 + M-8 green** | `0.9.0` |
| **v1.0.0** | **Promotion-Gated Meta-Framework** | Scale measured · SPI review · outer loop · macro-tool compilation · skill synthesis · unforgeable DPO · exact-McNemar promotion with rollback | **M-9 + M-10 green** | `1.0.0` |

> **Why v0.6.3 and v0.7.0 are separate versions sharing one technical run.** `v0.6.3` is the **candidate artifact**; `v0.7.0` is the **Director's acceptance of its evidence**. Collapsing them creates pressure to declare the stop line passed by merging code rather than by accepting evidence — the exact failure `ADR-0075` exists to prevent. **No second "cleaner" run may be stitched from different row winners.**

### 8.2 M-0 … M-10

```text
╔══════════════ FOUNDATION — ends at a STOP LINE ══════════════╗
║ M-0 Engineering truth                        ✅ COMPLETE     ║
║ M-1 Trust spine                              ✅ COMPLETE     ║
║ M-2 One runtime + Evidence integrity   🔵 IN FLIGHT → v0.6.1 ║
║ M-3 Extensibility + Composition algebra ⚪ QUEUED → v0.6.2   ║
║ M-4 Foundation E2E                      ⚪ QUEUED → v0.6.3   ║
║                  ███ STOP LINE ███                           ║
╚══════════════════════════════════════════════════════════════╝
                        ║  ◄── nothing below starts before the gate above
╔════════ GENERALITY & META-COGNITION — outcomes and gates only ════════╗
║ M-5 Generality proof + consolidation + T0 memoization → v0.7.0        ║
║ M-6 Mediated delegation                                → v0.8.0        ║
║ M-7 Controlled concurrency + Pareto Router active   ┐                  ║
║ M-8 Framework builder                               ┘ → v0.9.0         ║
║ M-9 Scale, retrieval, SPI review                    ┐                  ║
║ M-10 Meta-cognitive substrate (FINAL)               ┘ → v1.0.0         ║
╚═══════════════════════════════════════════════════════════════════════╝
```

#### M-2 → **v0.6.1** *(in flight, re-gate round 4)*

**Entry.** M-1 green. **Outcome.** One runtime authority **and a corpus that can be learned from before any episode is run in anger.**

| ID | Task | ADR | Falsifier | State |
|---|---|---|---|---|
| 2.1-A…E, 2.2-A/B/C | wire · codegen · SPI ports · fail-closed ceiling · duplication detector · KILL-surface deletion · `root.py` split | — | — | DONE |
| 2.2-D | widen the I-7 domain-blindness linter and boundary rows | — | — | READY |
| **NOVA-1** | un-hollow the trajectory: per-turn cost, latency, fingerprint, `D_R`, verdict-or-reasoned-null, `measurement_status` | `0078` | `RF-23`, `RF-24`, `RF-27` | **READY** |
| **NOVA-2** | SIGKILL mid-turn → fresh-process cold fold → reconcile → resume → complete | `0082` | `RF-25` | **READY** |
| **NOVA-3** | `_PROC_PATTERN` read from the compiled ceiling, not restated in `adapters/models/planner.py` | — | `RF-71` | READY |
| 2.6-A | write ADRs `0077`–`0084` to `docs/05_adr/`; update `INDEX.md` | — | — | **DIRECTOR** |
| 2.6-B | open the `RF-*` namespace; alias table into the `002` register; land the uniqueness linter | `0082` D5 | `RF-72` | READY |
| 2.6-C | correct the stale `spawn()` docstring; land the sealed-scope test | `0080` | `RF-26` | READY |
| 2.6-D | adjudicate the 6 currently-red tests (3 adapter isolated-evaluator, 3 runtime Ollama-taxonomy) as **product drift or environment sensitivity**, with a bounded reason each | — | — | TECH-LEAD |

**Exit gate.** Duplication detector green with `--enforce` · zero `layer0` imports under `vanguard/` · reducer folds complete with **zero silent `unknown_events`** · **`RF-23` green** · **`RF-25` green** *(red ⇒ M-3 does not open; re-scope M-7 as a rewrite first)* · `RF-26`, `RF-27`, `RF-71`, `RF-72` green · every currently-red test adjudicated · TCB ≤ 1438 with **zero kernel diff beyond tests**.
**Out of scope.** Any kernel diff · any plugin-lifecycle work · `mhf.manifest/2` *implementation* (design only) · any `layer0/` deletion beyond 2.2-B's authorized scope.

#### M-3 → **v0.6.2**

**Entry.** M-2 gate green **including `RF-25`**. **Outcome.** The framework claim becomes testable.

> ⚠ **Wave 1 received 17 tasks and 15 falsifiers for the trust spine. Wave 3 as originally boarded received 7 for the entire product claim, built on code that has never run on the canonical path. Rebalanced below to 6 sprints and 18 falsifiers.**

| Sprint | Content | Falsifiers | ADR |
|---|---|---|---|
| **3.1** | registry FSM → `runtime/registry/`, **all 7 transitions ledgered** (+ `PluginDiscovered`, `PluginVerified`) · compose v2 · echo plugin + fault injection · isolation broker rlimits | `RF-38`…`RF-43` | `0081` |
| **3.2** | `code-default` toolkits through the real lifecycle · coding-token sweep · **one manifest parser** *(was `3.2-C`/`DEV-LOCAL` — now `DIRECTOR`)* | `RF-33`, `RF-44` | `0077` D6 |
| **3.3** | **`mhf.manifest/2`** — components **and typed bindings** · `D_H` over nodes + edges · cycles permitted · five reference topologies compile · `code-default` migrates | `RF-28`…`RF-32` | `0077` |
| **3.4** | **absent-vs-forged** — three evidence states · derived attributability · trajectory `guardrails` block | `RF-34`…`RF-37` | `0079` |
| **3.5** | **`agent.spawn` design only** — verb spec, S0–S12 mapping, falsifier sketches authored red. **Zero kernel diff.** | `RF-55`…`RF-59` (unrun) | `0080` |
| **3.6** | **Pareto profile schema** — `profiles:` block, profiles enter `D_H`, recorded in the trajectory. **Router not activated.** | `RF-46`…`RF-48` | `0083` |
| **3.1-Z** | `rm -rf layer0/` · delete `test/layer0/` · drop the advisory CI step · **remove `"layer0*"` from `pyproject.toml:40`** — **atomic with a green NOVA-4** | `RF-45` | `0081` D5 |

**Exit gate.** Echo plugin walks all seven transitions over UDS, **each ledgered** · `code-default` loads through the same lifecycle · NOVA-4 six green · five topologies → five distinct `D_H`, binding-edge change moves `D_H` · declared absence compiles, changes `D_H`, and an unsigned verdict is **still** rejected · profile change moves `D_H` · I-7 green on the widened surface · exactly one manifest parser · **`layer0` absent from the tree and from the packaging manifest** · TCB ≤ 1438, zero kernel diff.
**Out of scope.** WASM tier · mandatory plugin signatures · any second product plugin · model/sandbox behind the wire · **any `agent.spawn` implementation** · **router activation**.

#### M-4 → **v0.6.3** · ███ THE STOP LINE ███

**The nine rows — all true on ONE uninterrupted run, zero human intervention, one `run_id`.**

| # | Row | Uncheated evidence | Falsified by |
|---|---|---|---|
| 1 | Real model | provider/model/fingerprint + measured usage from a **non-fake, non-cassette** invocation | — |
| 2 | Authorized effect | descriptor-bound grant, S5 decision, S7 lease, S8 verification, matching request | `RF-08` |
| 3 | Real filesystem change | before/after artifact digests + patch receipt in the run workspace | — |
| 4 | Rootless sandbox | recorded mount/network/syscall/UID **probes**; evaluator path absent; **no fallback-to-host success** | — |
| 5 | Exterior signed evaluation | UID/image/oracle/subject/nonce binding, verifiable signature; the agent cannot mint it | `RF-03`, `RF-04` |
| 6 | WAL ledger | full event range, project hash-chain continuity, durable S8a intent | `RF-05` |
| 7 | Cold replay | a fresh runtime folds the persisted chain to the same terminal state digest | `RF-02` |
| 8 | **Schema-valid AND POPULATED trajectory** | `/1` row with populated turns, non-hollow cost, fingerprint, `D_H`/`D_R`, receipts, outcome, evidence | **`RF-23` + `RF-49`** |
| 9 | One runtime authority | trace/import evidence: `Runtime.compose → execute_harness → HarnessSession`; no alternate path | `RF-45` |

> **Row 8 is strengthened by this synthesis.** The original gate said *"schema-valid `mhf.trajectory/1`"* — which a `_ZERO_COST` record satisfies. **The stop line contained the exact defect it exists to prevent.** It now reads *"schema-valid **and populated**"*.
>
> **Director standing order.** *Escalate any temptation to widen scope in order to make the run pass.* A widened gate is not a passed gate. **"Equivalent demo", cassette substitution, a manually copied verdict, or separately successful runs do not count.**

#### M-5 → **v0.7.0** — Generality, consolidation, and the first flywheel tier

**Entry.** M-4 evidence **accepted by the Director** (not merely produced).

- **5.1 Documentation collapse to the Clean Triad** (`ADR-0082` D3). SPEC + ADR log + one board. GAMMA and `002` retire as standing authorities with superseded banners. **No evidence destroyed.**
- **5.2 Pack #2 — Math & Formal Deductive Verification** (§8.3).
- **5.3 T0 memoization** (`ADR-0084` D2) — evidence-gated, ledgered, `D_H`-invalidated.
- **5.4 Measurement** — selector-soundness for independence groups · `RF-25` re-run at scale (≥ 8 concurrent logical episodes) · name and register the I-11 measurement gate · **build the `KERNEL.md` §1.1 TCB metric replacement triple** (mutation score on kernel + reducers, % of controls with production call-site proofs, E-COV) · **external benchmark run** of compiled `code-default` with cost/latency telemetry, for **composition falsification, not leaderboard position**.

**Exit gate.** `RF-50` **zero diffs under `packages/domain/` and `packages/kernel/`** for Pack #2 · `RF-51` **trajectory parity** — Pack #2 emits rows satisfying `RF-23` identically · `RF-52`/`RF-53` memoization is attributable and evidence-gated · `RF-54` a proof comment without a proof term cannot pass · `RF-25` green at scale · reading path is three documents · **package version cut to `0.7.0`**.

#### M-6 → **v0.8.0** · M-7 + M-8 → **v0.9.0** · M-9 + M-10 → **v1.0.0**

| M | Outcome | Exit gate |
|---|---|---|
| **M-6** | `agent.spawn` as an S0–S12 verb; recursive algorithms gain a legal home outside the engine | `RF-55`…`RF-59` green · `RF-26` green · hierarchical decomposition **and** tree search run **with zero engine diff** · **TCB ≤ 1438 with the verb costing ≤ 40 logical LOC** |
| **M-7** | Independence groups active · `K ≪ N` real · **Pareto Router activated** · mid-lease `CapabilityRevoked` | `RF-60` **zero peer messages, `Θ(c·N)` state ops as N: 1→64** · `RF-61` independent cells match the sequential reduction · `RF-62` unknown selector footprint serializes or denies · `RF-63` worker crash reclaims the claim without repeating an effect · `RF-64` revocation terminates a live lease · **I-11 formally lifted by ADR** |
| **M-8** | Debate · critic/revisor · evolutionary search · multi-agent economic delegation, composed **declaratively** | `RF-65` all four run multi-pack with **zero diffs under `kernel/` and `agency/episode/engine.py`** · **`RF-66` (the Standing Challenge) adjudicated** · SDK/CLI + dry-run compose + developer guide shipped |
| **M-9** | Scale measured, not asserted; retrieval; SPI review | published IPC / serialization / plugin-call / ledger-pressure measurements against declared budgets · retrieval lift demonstrated in **paired** tests · a written ruling on the sixth SPI recorded append-only |
| **M-10** | Outer loop · macro-tool compilation · skill synthesis · DPO · promotion with rollback | `RF-67`…`RF-70` green · **FINAL GATE** below |

**FINAL GATE (M-10).** A promotion occurs in which: the mutation was proposed by the outer loop; the comparison was **paired** against the **undeletable** baseline; the decision used **McNemar's exact test** on discordant pairs with a reported effect size, confidence interval, and cost-per-pass for both arms; **no assurance dimension regressed**; every verdict in the chain is exterior-signed and request-bound; `D_H ≠ D_R ≠ D_X` held throughout; **a human flipped the pointer**; and **rollback restores the baseline pointer without deleting either composition.**

### 8.3 Pack #2 — Math & Formal Deductive Verification

**Ruling: a gate, not an aspiration.** Selected because it is maximally distant from coding on every axis that matters: **no filesystem mutation as the primary effect, no subprocess as the primary verb, a decidable oracle, a different selector vocabulary, and a genuine exercise of `ADR-0079`.** TableWorld (`adapters/environment/tableworld.py`, orphaned, D-27) is **demoted to Pack #3** — it exists inside this repo's assumptions, which is exactly what makes it a weak generality test. Data analysis is Pack #4: too close to coding (filesystem + subprocess + test-runner-shaped oracle) to stress I-7.

```text
packs/math-formal/
├── manifest.yaml            mhf.manifest/2 — the FIRST pack written natively in /2
├── components/
│   ├── source.problems      kind: context   — immutable theorem statements by digest
│   ├── context.proof-state   kind: context   — assumptions, goals, prior lemmas, bounded history
│   ├── planner.proof-search  kind: planner   — single | critic | tree topology, no engine change
│   ├── memory.lemma-kv       kind: memory    — proven-lemma cache keyed by statement digest
│   └── evaluation.proof-check kind: evaluation — requests judgment; never renders it
├── toolkits/  proof_assistant · lemma_search · smt_query
│      selectors:  proof://tactic/<name> · lemma://index/<ns> · smt://solver/z3
└── oracles/   pinned, NETWORKLESS formal checker image, distinct from the worker sandbox
```

**Task strata (five, deliberately including two negatives):** exact rational/algebraic identity with a checkable normal form · finite combinatorial construction with an exhaustive certificate checker · a theorem accepted by the pinned formal kernel · **an inconsistent or underspecified premise where correct *abstention* is verified** · **an adversarial candidate containing a proof comment or string but no valid proof term.**

**Capability scope.** Read-only problem corpus · write-only/read-back scratch proof artifacts · one explicitly allowlisted compute executable · **no network** · no access to the evaluator bundle, the expected proof, the signing key, or the host home. **`proc.exec` stays a generic mediated verb — the kernel never learns "theorem", "Lean", or "proof".**

**Why it is the strongest available I-7 probe.** (1) A genuinely new selector vocabulary — if the algebra needs a `domain/` diff to express `proof://`, **I-7 is refuted and we learn it from a pack rather than a customer.** (2) A **decidable** oracle: no flakiness, no environment sensitivity, no partial credit — the cleanest possible signal for `RF-51` trajectory parity and for M-10. (3) It exercises `ADR-0079` non-trivially: a pure-deduction component may legitimately declare `sandbox: none` while an SMT subprocess may not — **per-component guardrail declaration gets its first real test in the milestone that first needs it.** (4) **Proof search *is* tree search**, so Pack #2 becomes M-6's validation composition at zero extra cost.

**The gate fails** if Pack #2 requires any modification under `domain/` or `kernel/`, a math branch in `agency/` or `runtime/`, direct checker access by the agent, an unsigned result, or a manually interpreted answer. Adapter and pack additions are expected; **a genuinely missing general port triggers an SPI/port review, never a domain shortcut.**

---

## §9 · Zero-Guesswork Developer Implementation Bridge

> **The contract of this section.** A developer picking up any task below needs **no interpretive judgement**. Every requirement has a schema, an FSM row, a fully-qualified test target, and an explicit list of what would be wrong. Where a decision is genuinely open it is labelled `DIRECTOR` or `TECH-LEAD` and **must not** be resolved locally.

### 9.1 Normative JSON Schema — `mhf.manifest/2` (Draft 2020-12)

**Path:** `schemas/mhf/manifest_v2.schema.json`, added **alongside** the frozen `mhf.harness/1`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://vanguard.dev/schemas/mhf/manifest_v2.schema.json",
  "$comment": "mhf.manifest/2 — the Named Component Graph (ADR-0077) plus execution profiles (ADR-0083) and guardrail declarations (ADR-0079). Supersedes the fixed-slot PluginBindings of mhf.harness/1, which is FROZEN and readable through M-4 for corpus attribution. compose() freezes this into FrozenHarness; the JCS digest of the FULL behaviour-affecting composition — components, kinds, resolved refs and digests, config digests, ceilings, isolation tiers, BINDING EDGES, profiles, guardrails, system prompt, harness ceiling, approval policy, model routes — is D_H and D_H ONLY (ADR-0071, ADR-0074, A-5). Slot names are pack convention, never schema constraint (ADR-0077 D3). Schema validation is NECESSARY AND NOT SUFFICIENT: referential integrity and graph semantics require the compiler.",
  "title": "HarnessManifestV2",
  "type": "object",
  "additionalProperties": false,
  "required": ["api", "id", "components"],
  "properties": {
    "api": { "type": "string", "const": "mhf.manifest/2" },
    "id":  { "type": "string", "pattern": "^[a-z0-9][a-z0-9-]{0,63}$" },

    "components": {
      "$comment": "Property NAMES are instance names chosen by the pack. 'planner'/'context'/'memory'/'evaluation' carry NO special meaning to compose() — `if name == \"planner\"` in runtime/ is a boundary violation in disguise (ADR-0077 D3). Multiplicity per kind is UNBOUNDED: two planner-kind components is a critic loop; N is debate.",
      "type": "object",
      "minProperties": 1,
      "propertyNames": { "pattern": "^[a-z][a-z0-9_-]{0,63}$" },
      "additionalProperties": { "$ref": "#/$defs/Component" }
    },

    "bindings": {
      "$comment": "THE DELIVERABLE OF T-1 (ADR-0077 D1). The existing domain-side `components` value is a role→paths BAG WITH NO EDGES; converging parsers onto it buys the node half and nothing else. Bindings declare WHAT a component may address, never WHEN it runs — execution order is the universal turn loop plus spawn topology. NOT a workflow DAG (SPEC §9 refusal stands). CYCLES ARE PERMITTED (ADR-0077 D5): a critic loop is cyclic. Termination is enforced by turns/depth/cost budgets, NEVER inferred from acyclicity. Self-edges are rejected.",
      "type": "array",
      "default": [],
      "items": { "$ref": "#/$defs/Binding" }
    },

    "profiles": {
      "$comment": "ADR-0083. Execution profiles as composition data. Enters D_H — a composition differing only in profile weights is a different composition. The four reference profiles are PACK CONVENTION, exactly like slot names. SCHEMA LANDS M-3; ROUTER ACTIVATES M-7 (gated on RF-25 + selector soundness). Until then `profile` is recorded and honoured SEQUENTIALLY (I-11).",
      "type": "object",
      "propertyNames": { "pattern": "^[a-z][a-z0-9_-]{0,31}$" },
      "additionalProperties": { "$ref": "#/$defs/Profile" }
    },

    "guardrails": { "$ref": "#/$defs/GuardrailDeclaration" },
    "model_routes": { "type": "array", "items": { "$ref": "#/$defs/ModelRoute" }, "default": [] },
    "system_prompt": { "type": ["string", "null"],
      "$comment": "Path to the byte-stable L1 prompt. Its CONTENT digest enters D_H — two harnesses differing only in prompt MUST NOT share D_H (A-5)." },
    "capabilities": {
      "$comment": "The HARNESS ceiling. Every component ceiling intersects this FAIL-CLOSED at compose (ADR-0072). An empty array authorises NOTHING (RF-39).",
      "type": "array", "items": { "$ref": "#/$defs/CapabilityRequirement" }, "default": []
    },
    "budget": {
      "type": "object", "additionalProperties": false,
      "required": ["usd_micros", "tokens", "bytes", "millis", "turns", "depth"],
      "properties": {
        "usd_micros": { "type": "integer", "minimum": 0 },
        "tokens":     { "type": "integer", "minimum": 0 },
        "bytes":      { "type": "integer", "minimum": 0 },
        "millis":     { "type": "integer", "minimum": 0,
                        "$comment": "CHARGED COMPUTE, never wall-clock under concurrency (ADR-0074 §2)." },
        "turns":      { "type": "integer", "minimum": 0, "$comment": "STRUCTURAL ceiling, not a cost." },
        "depth":      { "type": "integer", "minimum": 0, "$comment": "STRUCTURAL. Sibling depths are NOT summed." }
      }
    },
    "approval_policy": { "type": ["string", "null"],
      "$comment": "null is a LEGAL declared absence (ADR-0079 D1); it enters D_H and marks the run unattributable." },
    "undeletable": { "type": "boolean", "default": false }
  },

  "$defs": {

    "Component": {
      "type": "object", "additionalProperties": false, "required": ["kind", "ref"],
      "properties": {
        "kind": {
          "$comment": "One of the five frozen SPI kinds (ADR-M0-03 NOT reopened). kind no longer implies cardinality one (ADR-0077 D2).",
          "type": "string", "enum": ["planner", "context", "memory", "toolkit", "evaluation"] },
        "ref": { "type": "string", "minLength": 1,
          "$comment": "Plugin reference with a semver caret range. An UNKNOWN ref FAILS AT COMPOSE, never at runtime (ADR-0005; RF-38). A semver range that resolves differently MUST change D_H." },
        "config": { "type": "object", "default": {},
          "$comment": "Validated against the plugin's declared config_schema at VERIFIED. Its JCS digest enters D_H." },
        "ceiling": {
          "$comment": "ABSENT means 'inherit the harness ceiling'. PRESENT-BUT-EMPTY means 'authorise nothing'. These are DIFFERENT and both are tested (RF-31, RF-39).",
          "type": "array", "items": { "$ref": "#/$defs/CapabilityRequirement" } },
        "isolation": { "type": "string", "enum": ["in_process", "subprocess", "container", "wasm"],
          "default": "subprocess",
          "$comment": "I-6: plugins untrusted by default. 'in_process' is a POLICY-GRANTED PRIVILEGE that still speaks the same JSON-RPC wire (ADR-0072). RF-37 pins it." },
        "spawn_grant": { "type": "boolean", "default": false,
          "$comment": "ADR-0080 D1 — DESIGN-LOCKED, INERT UNTIL M-6. compose() MUST parse and digest this field from v0.6.2 so D_H is stable across the M-6 cut, and MUST reject `true` with 'agent.spawn not implemented before M-6'. Parse early, enforce late." }
      }
    },

    "Binding": {
      "type": "object", "additionalProperties": false, "required": ["from", "to", "relation"],
      "properties": {
        "from": { "type": "string", "$comment": "A component name that MUST exist." },
        "to":   { "type": "array", "minItems": 1, "items": { "type": "string" },
                  "$comment": "Component names that MUST exist. `from` ∈ `to` is a self-edge and FAILS AT COMPOSE." },
        "relation": {
          "$comment": "CLOSED ROSTER. A new relation is a schema change with an ADR, never a free string — an open string set is how a workflow DAG smuggles itself in.",
          "type": "string",
          "enum": ["uses", "gated_by", "reviewed_by", "aggregates", "scores", "selects", "expands", "revises"] }
      }
    },

    "Profile": {
      "$comment": "ADR-0083 D1/D3. λ weights and hard ceilings for the constrained selection of §2.2. Feasibility and assurance are checked FIRST; among feasible policies a Pareto frontier is retained. NO scalar score may let a cost win offset an assurance regression (ADR-0015, SPEC §9).",
      "type": "object", "additionalProperties": false,
      "properties": {
        "weights": {
          "type": "object", "additionalProperties": false,
          "properties": {
            "usd_micros": { "type": "number", "minimum": 0 },
            "tokens":     { "type": "number", "minimum": 0 },
            "millis":     { "type": "number", "minimum": 0 }
          },
          "$comment": "λ_j ≥ 0 — DECLARED POLICY PARAMETERS, not learned excuses to violate a ceiling." },
        "ceilings":        { "$ref": "#/$defs/ProfileCeilings" },
        "quality_floor":   { "type": "string", "enum": ["none", "inline", "exterior_signed"],
                             "$comment": "A HARD constraint, never a currency." },
        "topology_preset": { "type": "string",
                             "$comment": "Names a subgraph of `components`/`bindings` to activate. Never new code." },
        "escalate_to":     { "type": ["string", "null"],
                             "$comment": "ADR-0083 D5. On a SIGNED verdict_fail, forward ONLY (workspace delta + falsifier) to this profile. NEVER a full transcript replay. Every attempt debits the SAME episode budget — escalation is not a new wallet (RF-48)." }
      }
    },

    "ProfileCeilings": {
      "type": "object", "additionalProperties": false,
      "properties": {
        "max_tokens_per_turn": { "type": "integer", "minimum": 1 },
        "max_millis_per_turn": { "type": "integer", "minimum": 1 },
        "max_tier":            { "type": "integer", "minimum": 1 },
        "max_repair_rounds":   { "type": "integer", "minimum": 0 },
        "max_parallel_claims": { "type": "integer", "minimum": 1,
          "$comment": "INERT UNTIL M-7. Values > 1 MUST be rejected at compose while I-11 stands." }
      }
    },

    "GuardrailDeclaration": {
      "$comment": "ADR-0079. Declaring a guardrail absent is LEGAL and enters D_H; forging its OUTPUT is categorically illegal under every composition (D5). NOTE: `unattributable_for_promotion` is DERIVED by compose() and stamped on FrozenHarness — it is DELIBERATELY ABSENT here (D4). A manifest-writable attributability flag is a forgery surface.",
      "type": "object", "additionalProperties": false,
      "properties": {
        "evaluation": { "type": "string", "enum": ["required", "none"], "default": "required" },
        "sandbox":    { "type": "string", "enum": ["required", "none"], "default": "required" },
        "approval":   { "type": "string", "enum": ["required", "none"], "default": "required" },
        "absence_reason": { "type": ["string", "null"], "default": null,
          "$comment": "REQUIRED to be non-null whenever any field above is 'none'. An unexplained absence is indistinguishable from an oversight." }
      }
    },

    "CapabilityRequirement": {
      "type": "object", "additionalProperties": false, "required": ["verb", "selector"],
      "properties": {
        "verb":     { "type": "string", "minLength": 1 },
        "selector": { "type": "object",
          "$comment": "MUST parse under domain/selectors/resource_selector.parse_selector. SELECTOR_KINDS = {fs, network, secret, git, table, browser, generic}. `kind: proc` is REJECTED — express process capability as {kind: generic, uriPattern: 'proc://exec/allow/...'} (settled at 2.1-D)." },
        "sink":     { "type": "string", "enum": ["observation", "advisory", "privileged"] },
        "risk":     { "type": "string", "enum": ["low", "medium", "high"] }
      }
    },

    "ModelRoute": {
      "type": "object", "additionalProperties": false, "required": ["tier", "provider", "model"],
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

**Worked example — the critic loop `mhf.harness/1` cannot express:**

```yaml
api: mhf.manifest/2
id: critic-loop-reference
components:
  proposer: {kind: planner,    ref: mhf.planner.drive-until-green@^1}
  critic:   {kind: planner,    ref: mhf.planner.critic@^1, config: {max_rounds: 3}}
  inline:   {kind: evaluation, ref: mhf.eval.lint-gate@^1}        # cheap, agent-side
  terminal: {kind: evaluation, ref: mhf.eval.oracle-gate@^1}      # exterior, signed
bindings:
  - {from: proposer, to: [critic],   relation: reviewed_by}
  - {from: critic,   to: [proposer], relation: revises}       # ← CYCLE. Legal. Bounded by turns/depth.
  - {from: proposer, to: [inline, terminal], relation: gated_by}
profiles:
  beta:  {weights: {tokens: 1.0, millis: 0.5}, ceilings: {max_tier: 2, max_repair_rounds: 4},
          quality_floor: exterior_signed, escalate_to: gamma}
  gamma: {weights: {tokens: 0.2, millis: 0.1}, ceilings: {max_tier: 3, max_repair_rounds: 8},
          quality_floor: exterior_signed, escalate_to: null}
```

#### 9.1.1 Companion delta — `mhf.trajectory/1`

Not re-versioned; no existing field changes meaning. Three optional fields become required and two objects are added.

```jsonc
{
  "required": ["schema","project_id","run_id","episode_id","principal_id","harness_digest",
               "turns","verdict","cost",
               "execution_digest",     // + ADR-0078 D3 — D_R; RF-27 asserts D_R != D_H
               "model_routes_used",    // + ADR-0078 D4 — with model_fingerprint or a reasoned unavailable
               "guardrails"],          // + ADR-0079 D3
  "properties": {
    "execution_digest": { "type": "string", "pattern": "^sha256:[0-9a-f]{64}$" },
    "model_routes_used": { "type": "array", "minItems": 1,
      "items": { "required": ["tier","provider","model","model_fingerprint"] } },
    "guardrails": { "type": "object", "additionalProperties": false,
      "required": ["evaluation","sandbox","approval"],
      "properties": { "evaluation": {"type":"string"}, "sandbox": {"type":"string"},
                      "approval": {"type":"string"} } },
    "unattributable_for_promotion": { "type": "boolean",
      "$comment": "DERIVED by compose(), copied from FrozenHarness. Never authored (ADR-0079 D4)." },
    "verdict_absent_reason": { "type": ["string","null"],
      "enum": ["guardrail_absent","aborted","budget_exhausted","instrument_error", null],
      "$comment": "REQUIRED non-null whenever verdict is null. A null verdict with a null reason is an unexplained gap in the evidence chain." },
    "measurement_status": { "type": "string", "enum": ["measured","unavailable"], "default": "measured",
      "$comment": "ADR-0078 D4. UNKNOWN IS NEVER ZERO. A fabricated zero is indistinguishable from a measured zero." },
    "measurement_unavailable_reason": { "type": ["string","null"], "default": null },
    "profile_used": { "type": ["string","null"], "$comment": "ADR-0083. Required from M-3." },
    "escalations": { "type": "array", "items": { "type": "object",
      "required": ["from_profile","to_profile","falsifier_digest"] },
      "$comment": "ADR-0083 D5. The falsifier digest, not the transcript." },
    "memo_hit": { "type": "boolean", "default": false,
      "$comment": "ADR-0084 D2. A memoized turn is ATTRIBUTABLE, not invisible." },
    "memo_source_episode_id": { "type": ["string","null"], "default": null },
    "legacy_incomplete": { "type": "boolean", "default": false,
      "$comment": "ADR-0078 D8. Pre-NOVA-1 rows. Excluded from promotion. NEVER back-filled." }
  }
}
```

> ⚠ **`CostVector` is deliberately UNCHANGED.** `additionalProperties: false` over `{usd_micros, tokens, bytes, millis}` already encodes `ADR-0074`'s type split. **Adding `depth` or `turns` to a `CostVector` is the single most likely accidental violation of the budget algebra**, and the schema already fails it closed. Do not "helpfully" widen it.

### 9.2 Complete plugin lifecycle FSM

**Every row emits.** A transition with no event is the verified defect `RF-43` exists to kill.

| # | From | To | Trigger | Ledger event | Writer | Payload (beyond lineage) |
|---|---|---|---|---|---|---|
| 1 | ∅ | `DISCOVERED` | scan path / `mhf.plugins` entry point resolves | **`PluginDiscovered`** ⭐ | `registry` | `{plugin_id, source_path, manifest_digest}` |
| 2 | `DISCOVERED` | `RESOLVED` | deps topologically resolved; SPI version negotiated | `PluginResolved` | `registry` | `{plugin_id, resolved_version, spi_version, dep_digests[]}` |
| 3 | `DISCOVERED` | `FAULTED` | unknown ref / unsatisfiable semver | `PluginFaulted` | `registry` | `{plugin_id, reason: "unresolvable_ref"}` |
| 4 | `RESOLVED` | `VERIFIED` | config schema ✓ · signature policy ✓ · **ceiling ∩ harness ceiling, fail-closed** ✓ | **`PluginVerified`** ⭐ | `registry` | `{plugin_id, config_digest, ceiling_digest, signature_ok}` |
| 5 | `RESOLVED` | `FAULTED` | schema / signature / **empty-ceiling** failure | `PluginFaulted` | `registry` | `{plugin_id, reason: "verification_failed"}` |
| 6 | `VERIFIED` | `ACTIVATED` | isolation broker starts the cell; UDS handshake ✓ | `PluginActivated` | `registry` | `{plugin_id, isolation_tier, cell_pid, socket_digest}` |
| 7 | `VERIFIED` | `FAULTED` | cell start failure / rlimit refusal / handshake timeout | `PluginFaulted` | `registry` | `{plugin_id, reason: "activation_failed"}` |
| 8 | `ACTIVATED` | `QUIESCING` | drain requested; in-flight calls draining | `PluginQuiesced` | `registry` | `{plugin_id, inflight_count}` |
| 9 | `ACTIVATED` | `FAULTED` | crash · rlimit kill · RPC timeout · protocol violation | `PluginFaulted` | `registry` | `{plugin_id, reason, exit_code, restart_count}` |
| 10 | `QUIESCING` | `RETIRED` | drain complete; cell exited | `PluginRetired` | `registry` | `{plugin_id, final_call_count}` |
| 11 | `QUIESCING` | `FAULTED` | drain timeout ⇒ forced kill | `PluginFaulted` | `registry` | `{plugin_id, reason: "drain_timeout"}` |
| 12 | `FAULTED` | `RETIRED` | crash-loop backoff exhausted, or a declared substitute activated | `PluginRetired` | `registry` | `{plugin_id, reason, substitute_id?}` |
| 13 | `RETIRED` | — | terminal | — | — | — |

⭐ = **new event kind** (`ADR-0081` D3, Director escalation ruled). `EVENT_KINDS` **56 → 58**. Both fold into `LedgerState.plugins` and are included in `to_canonical_dict()`. `CataloguedKindsAreFoldedOrAllowlisted` extends to 58 with **zero** additions to `UNFOLDED_ALLOWLIST`.

**Illegal by construction — each is a test, not a comment:** `RETIRED → *` · `FAULTED → ACTIVATED` without re-traversing from `DISCOVERED` · **any transition emitting no event** · a non-`registry` role appending a `Plugin*` kind · a ref resolved at runtime rather than compose · any mutation of a frozen composition.

### 9.3 The authoritative 1-to-1 falsifier matrix

**This table is the single source of truth for `RF-*` numbering. There is no second numbering anywhere in this document.** `RF-01 … RF-22` alias the existing register `F-01 … F-22`; `F-*` in `docs/04_annex/KERNEL.md` is a different, unchanged namespace (`ADR-0082` D5).

#### Aliased (existing, Wave 0/1)

| ID | Test | State |
|---|---|---|
| `RF-01` | `test_every_emitted_envelope_carries_full_lineage` | ✅ |
| `RF-02` | `ColdReplayParity.test_cold_reader_reconstructs_live_state_from_disk` | ✅ |
| `RF-03` | `test_scheduler_cannot_produce_a_verdict_without_a_signature` | ✅ |
| `RF-04` | `test_replayed_or_unbound_signature_is_rejected` | ✅ |
| `RF-05` | `test_orchestrator_cannot_append_privileged_kinds` | ✅ |
| `RF-06` | `test_declared_ceiling_survives_compilation_and_denies` | ✅ |
| `RF-07` | `test_empty_ceiling_denies_everything` | ✅ |
| `RF-08` | `test_privileged_verb_requires_a_bound_grant` | ⚠ **STALE — formally retired.** It dispatched a fully authorized `fs.write` and asserted the grant path must fail on its own happy path. The kernel is correct: S6 issues via `SinkRegistry.requires_grant`, S8 re-verifies at the point of effect (`K-05`), S8a records `grantId`/`grantDigest`. **The register must say so in its own table** (§10.2). |
| `RF-09`…`RF-11` | spawn attenuation · depth algebra · `D_H` completeness | ✅ |
| `RF-12` | `test_episode_completed_emits_schema_valid_trajectory` | 🔴 **SUPERSEDED by `RF-23`** — schema validity is necessary and not sufficient |
| `RF-13`…`RF-22` | codegen · duplication · CI subject · I-7 scope · collection · oracle artifact · translator · reconciliation | ✅ |

#### New — authoritative

| ID | Test target | ADR | Gate |
|---|---|---|---|
| **`RF-23`** | `test.runtime.test_trajectory_v2.TrajectoryV2Tests.test_each_invoked_turn_has_a_positive_measured_dimension` **(NOVA-1)** | `0078` | **M-2** |
| **`RF-24`** | `test.runtime.test_trajectory_v2.TrajectoryV2Tests.test_planner_cannot_author_a_cost_field` | `0078` D6 | M-2 |
| **`RF-25`** | `test.runtime.test_cold_continuation.ColdContinuationFalsifier.test_sigkilled_midturn_episode_cold_resumes_to_completion` **(NOVA-2)** | `0082` D2 | **M-2 (hard M-3 entry gate)** |
| **`RF-26`** | `test.kernel.test_policy.SealedScope.test_sealed_child_rejects_out_of_scope_action_at_S5` | `0080` C | M-2 |
| **`RF-27`** | `test.runtime.test_trajectory_v2.TrajectoryV2Tests.test_execution_digest_present_and_distinct_from_harness_digest` | `0078` D3 | M-2 |
| **`RF-28`** | `test.contracts.test_manifest_v2_graph.ManifestV2GraphTests.test_two_same_kind_components_with_distinct_names_compile` | `0077` D2 | M-3 |
| **`RF-29`** | `test.contracts.test_manifest_v2_graph.ManifestV2GraphTests.test_five_topologies_compile_to_five_distinct_digests_without_engine_change` | `0077` D1 | M-3 |
| **`RF-30`** | `test.contracts.test_manifest_v2_digest.ManifestV2DigestTests.test_binding_edge_change_changes_D_H` | `0077` D4 | **M-3 (the edge-half proof)** |
| **`RF-31`** | `test.runtime.test_compose_v2.ComposeV2Tests.test_component_ceiling_intersects_harness_ceiling_fail_closed` | `0077` D7 | M-3 |
| **`RF-32`** | `test.runtime.test_manifest_v2_negatives.ManifestV2NegativeTests.test_unknown_endpoint_or_unconsumed_authority_component_fails_at_compose` | `0077` D5 | M-3 |
| **`RF-33`** | `test.contracts.test_manifest_parser.ParserConvergenceTests.test_exactly_one_manifest_parser_exists` | `0077` D6 | M-3 |
| **`RF-34`** | `test.trust.test_evidence_states.EvidenceStateTests.test_evaluation_none_compiles_and_changes_D_H` | `0079` D1/D2 | M-3 |
| **`RF-35`** | `test.trust.test_evidence_states.EvidenceStateTests.test_unsigned_verdict_rejected_under_declared_absence` | `0079` D5 | M-3 |
| **`RF-36`** | `test.runtime.test_compose_v2.ComposeV2Tests.test_unattributable_flag_is_derived_not_manifest_writable` | `0079` D4 | M-3 |
| **`RF-37`** | `test.packs.test_gates.IsolationPolicyGateTests.test_in_process_requires_explicit_policy_grant` | `0079` D7 | M-3 |
| **`RF-38`** | `test.runtime.registry.test_nova4.Nova4Tests.test_unknown_plugin_ref_fails_at_compose_not_runtime` | `0081` D4 | M-3 |
| **`RF-39`** | `test.runtime.registry.test_nova4.Nova4Tests.test_empty_component_ceiling_denies_everything` | `0081` D4 | M-3 |
| **`RF-40`** | `test.runtime.registry.test_nova4.Nova4Tests.test_only_registry_may_append_plugin_kinds` | `0081` D4 | M-3 |
| **`RF-41`** | `test.runtime.registry.test_nova4.Nova4Tests.test_faulted_cell_cannot_remain_active` | `0081` D4 | M-3 |
| **`RF-42`** | `test.runtime.registry.test_nova4.Nova4Tests.test_no_code_path_mutates_a_frozen_composition` | `0081` D6 | M-3 |
| **`RF-43`** | `test.runtime.registry.test_lifecycle_events.PluginLifecycleTests.test_every_legal_transition_emits_a_ledgered_owned_event` | `0081` D3 | **M-3 (the silent-transition defect)** |
| **`RF-44`** | `test.packs.test_lifecycle_load.PackLifecycleTests.test_code_default_toolkits_load_through_the_lifecycle` | `0081` D1 | M-3 |
| **`RF-45`** | `test.packs.test_gates.Layer0RetirementTests.test_layer0_absent_from_tree_and_from_pyproject_include` | `0081` D5 | **M-3 (incl. `pyproject.toml:40`)** |
| **`RF-46`** | `test.contracts.test_manifest_v2_digest.ManifestV2DigestTests.test_profile_change_changes_D_H` | `0083` D2 | M-3 |
| **`RF-47`** | `test.trust.test_router_authority.RouterAuthorityTests.test_router_cannot_widen_ceiling_or_bypass_dispatch` | `0083` D4 | M-3 |
| **`RF-48`** | `test.runtime.test_escalation.EscalationTests.test_escalation_debits_same_budget_and_forwards_only_delta_and_falsifier` | `0083` D5 | M-3 |
| **`RF-49`** | `test.integration.test_foundation_e2e.NineRowTests.test_real_run_trajectory_carries_nonzero_cost` **(NOVA-5)** | `0078` | **M-4** |
| **`RF-50`** | `test.packs.math_formal.test_generality.MathGeneralityFalsifier.test_pack_runs_with_domain_and_kernel_tree_hash_unchanged` | I-7 | **M-5 (the generality gate)** |
| **`RF-51`** | `test.packs.math_formal.test_generality.MathGeneralityFalsifier.test_pack2_trajectory_parity_with_pack1` | `0078` | M-5 |
| **`RF-52`** | `test.runtime.test_memo.MemoTests.test_memo_hit_is_ledgered_attributable_and_invalidated_by_digest_change` | `0084` D2 | M-5 |
| **`RF-53`** | `test.runtime.test_memo.MemoTests.test_unsigned_or_unattributable_result_never_enters_the_cache` | `0084` D2 | M-5 |
| **`RF-54`** | `test.packs.math_formal.test_oracle.MathOracleTests.test_comment_or_string_without_proof_term_fails` | Pack #2 | M-5 |
| **`RF-55`** | `test.trust.test_mediated_spawn.MediatedSpawnFalsifier.test_planner_without_spawn_grant_cannot_delegate` | `0080` D4 | M-6 |
| **`RF-56`** | `test.trust.test_mediated_spawn.MediatedSpawnFalsifier.test_spawn_is_a_mediated_effect_with_a_receipt` | `0080` D2 | M-6 |
| **`RF-57`** | `test.trust.test_mediated_spawn.MediatedSpawnFalsifier.test_spawn_selector_denies_undeclared_harness_digest` | `0080` D2 | M-6 |
| **`RF-58`** | `test.security.test_evaluator_security.EvaluatorBoundary.test_child_cannot_reach_evaluator_without_selector_grant` | `0080` D6 | M-6 |
| **`RF-59`** | `test.kernel.test_attenuation.Attenuation.test_child_grant_wider_than_parent_is_denied_whole` | `0080` D3 | M-6 |
| **`RF-60`** | `test.runtime.test_stigmergy.StigmergyTests.test_zero_peer_messages_and_linear_state_ops_as_N_scales` | §3.5 | **M-7 (the swarm claim)** |
| **`RF-61`** | `test.runtime.test_controlled_concurrency.ConcurrencyTests.test_independent_cells_match_sequential_reduction` | I-11 | M-7 |
| **`RF-62`** | `test.runtime.test_controlled_concurrency.ConcurrencyTests.test_unknown_selector_footprint_serializes_or_denies` | I-11 | M-7 |
| **`RF-63`** | `test.runtime.test_controlled_concurrency.ConcurrencyTests.test_worker_crash_reclaims_claim_without_repeating_effect` | §3.3 | M-7 |
| **`RF-64`** | `test.kernel.test_revocation.RevocationTests.test_capability_revoked_terminates_a_live_lease` | TOCTOU | M-7 |
| **`RF-65`** | `test.integration.test_framework_builder.BuilderTests.test_four_topologies_run_multipack_with_zero_engine_diff` | `0082` D1 | **M-8** |
| **`RF-66`** | **The Standing Challenge** — adjudicated by the Director, not automated | `0082` D1 | **M-8** |
| **`RF-67`** | `test.runtime.test_macro_tool.MacroToolTests.test_macro_tool_ceiling_within_source_ngram_exercised_grants` | `0084` D3 | M-10 |
| **`RF-68`** | `test.runtime.test_macro_tool.MacroToolTests.test_macro_tool_dispatches_through_S0_S12_as_the_pattern_it_replaced` | `0084` D3 | M-10 |
| **`RF-69`** | `test.runtime.test_promotion_statistics.PromotionStatisticsTests.test_exact_p_matches_enumerated_binomial_cases` | `0084` D4 | M-10 |
| **`RF-70`** | `test.runtime.test_promotion_protocol.PromotionProtocolFalsifier.test_promotion_denies_on_any_assurance_regression_regardless_of_cost_win` | `0084` D4 | M-10 |
| **`RF-71`** | `test.adapters.test_planner_ceiling.ProcPatternTests.test_proc_pattern_read_from_compiled_ceiling` **(NOVA-3)** | — | M-2 |
| **`RF-72`** | `tools/linters/check_falsifier_ids.py` — ids unique across the annex and the register | `0082` D5 | M-2 |

### 9.4 Negative constraints & anti-pattern checklist

**The implementation is rejected if any answer is "yes."**

**TCB & kernel** — Does `kernel/` exceed 1438 logical LOC, or import a domain verb, planner, model, evaluator, registry, task type, or learning policy? Is there a kernel diff before M-4 closes beyond tests? Is a ceiling being raised to fit an implementation rather than escalated? Is there a second selector algebra, canonicalisation, writer, manifest compiler, event store, or episode driver? Is there an "allow with a warning" outcome? Is a constant standing in for the S4 classifier?

**Domain blindness (I-7)** — Do `coding|pytest|ast` tokens appear under `packages/{domain,kernel}/`? At M-5, do `proof|lemma|smt`? Is a pack-specific verb, selector kind, or oracle name in core? Does the kernel import `tools/telemetry/`, `lab/`, or the harvester?

**Evidence & writer authority** — Can anything but `runtime/evaluator_gateway.py` write `VerdictRecorded`? Can a plugin, planner, or model adapter author a cost field? Is `unattributable_for_promotion` manifest-writable? Does any FSM transition emit nothing? Does the reducer verify signatures (it must not — that is the reader's job)? **Are unknown token, price, or fingerprint values written as zero instead of `measurement_status: unavailable`?** Can declared-absent evidence become a pass, a preference pair, a memory license, or a promotion? Does a critic or agent inside the worker mint the authoritative verdict?

**Budget algebra** — Are sibling depths summed? Do `depth` or `turns` appear in a `CostVector`? Does a child get an independent wallet instead of a parent sublease? Does a duck-typed `as_map()` silently restore sibling-depth summing? Are wall-clock milliseconds summed across concurrent workers as if they were conserved compute?

**Composition & freeze** — Does anything resolve at runtime that should fail at compose? Can a `FrozenHarness` mutate? Does `compose()` key on a component *name*? Is there a `relation` outside the closed roster? Can a semver ref resolve differently without changing `D_H`? **Is a graph rejected merely for containing a cycle?** *(It must not be — `ADR-0077` D5.)*

**Router (`ADR-0083`)** — Can the router widen a ceiling, pre-filter authorization, mint or read a verdict, or author a cost? Does escalation open a new wallet or replay a full transcript? Does any scalar score let a cost win offset an assurance regression? Is `max_parallel_claims > 1` accepted while I-11 stands?

**Concurrency (I-11)** — Is there parallel fan-out before M-7's gate? Is unknown selector footprint treated as independence rather than conflict? Is byte-identical concurrent ledgering claimed as a requirement? Does a swarm use full-mesh chat, shared mutable memory, or unowned state writes? Is a direct agent message treated as anything but an `UNTRUSTED_DERIVED` observation?

**Learning (`ADR-0084`)** — Does DPO consume unpaired, unsigned, incomparable, contaminated, or train/eval-overlapping examples? Does a macro-tool need a wider ceiling than its source pattern, or bypass S0–S12? Is a macro-tool hot-swapped into a running composition? Does a causal label come from temporal adjacency without a recorded dependency? Does the outer loop reach the workspace? **Does `AUTHORIZATION_DENIED` license an automatic mutation?** *(It must never — §4.6.)*

**Governance** — Is an accepted ADR being silently edited? Is a locked concept shipping without a bound falsifier? Is a falsifier being traded away to make a wave fit? Is documentation being collapsed before M-4 closes, or historical evidence erased to make navigation tidy? Is a `DEV-LOCAL` task the vehicle for a decision that fixes `D_H`'s pre-image? Is a wave being declared green by grep? Is a scalar reward being used for promotion?

---

## §10 · Repository Hygiene & Document Update Cascade

> **Sequencing rule.** Hygiene that is cheap, local, and reversible executes in M-2. Hygiene that is structural (the Clean Triad collapse) is **forbidden before M-4 closes** (`ADR-0082` D3). Do not mix them.

### 10.1 Stale artifacts — M-2, no ADR required

| # | Artifact | Verified state | Directive |
|---|---|---|---|
| H-1 | `DELETE.md` | **present, 0 bytes** `[VERIFIED]` — refutes `008`'s "absent" | **`git rm`.** A zero-byte file whose name is an instruction is a landmine for every future reader. Deleted paths belong in git history plus `docs/07_reviews/ARCHIVE.md`. |
| H-2 | `docs/08_workflows/` | empty directory | Delete. `docs/08_diagrams/` already holds the four SVGs. |
| H-3 | `RESEARCH_THEORETICAL_SYNTHESIS.md` / `_B.md` | **byte-identical**, `sha256:45bddc74…f7a24e3`, both `id: REF-06-M5` `[VERIFIED]` | **Delete `_B`. There is no "successor" — the prior draft's rationale was inferred, not verified, and is withdrawn.** Two files claiming one id is the prose form of a duplicate primary key. |
| H-4 | `docs/06_references/vanguard_body_detailed.md` | biological / cosmological framing | **Director ruling: retire from `docs/`.** `ADR-M0-10` / `REJ-10` forbid that framing in *any* document under `docs/`; a standing refusal with a live exception is not a refusal. Preserve in git history; surviving ideas re-enter as ADR-shaped proposals in plain language. |
| H-5 | `docs/06_references/RESEARCH_Harness_Builder_Framework.md` | Redis/NATS/ChromaDB/K8s PRD contradicting the locked lattice | **Retain with a mandatory banner:** *"REJECTED AS A COMPETING ARCHITECTURE (`ADR-0069`, `ADR-0070`). Mine for plugin/adapter ideas only. This design would re-create the dual-runtime failure."* Deleting loses the catalog; leaving it unmarked invites a re-import. |
| H-6 | `002`, `004`, `005`, `006`, `007`, `008` at repo root | review artifacts outside the documentation tree and outside every linter's scan path | Move to `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/` with superseded banners. **This document included.** |
| H-7 | `workflow_visualizer.html` (49 KB, root, unreferenced) | — | Move to `tools/substrate_visualizer/` or delete. |
| **H-8** | **`tools/linters/check_markdown_links.py`** | `DOC_GLOBS = ("README.md", "docs/README.md", "docs/agile/sprint6B/*.md")` — the third glob matches nothing | **Widen to `docs/**/*.md` + repo-root `*.md`. HIGHEST-VALUE ITEM IN THIS TABLE.** The gate reports `LINK PASS` while the entire `docs/` corpus, all 90 ADRs, and both Director briefings go unchecked — **the same defect class as `F-18` and hollow `F-12`: a gate certifying something narrower than the invariant it claims.** Fix in M-2, **before** eight new ADRs land. |
| H-9 | `CLAUDE.md` §3 / `SYSTEM_OVERVIEW` §3.4 | claim the boundary linter scans **283** files | **248** `[VERIFIED]`. Correct both. |
| H-10 | `sprint_active.md` / `SYSTEM_OVERVIEW` | claim `test/agency` has **107** tests | **105** `[VERIFIED]`. Correct both. |
| H-11 | `sprint_active.md` front-matter `plans:` | points at `docs/03_sprints/plans/`; wave plans live in `doing/` and `done/` | Repoint; add both directories to `check_stale_paths.py`. |
| **H-12** | **`pyproject.toml:40`** | `include = ["vanguard*", "layer0*"]` `[VERIFIED]` | **Remove `"layer0*"` at M-3, atomically with the `layer0/` deletion (`ADR-0081` D5).** `008`'s best finding: without this, deletion is cosmetic and setuptools still ships the fork. |

**Explicitly NOT a finding — do not act on it.** `008` §7.1 reports the review and research corpora as absent ("ghost corpus G0"). **Refuted `[VERIFIED]`:** all six files under `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/` and all twelve under `docs/06_references/` exist at HEAD. That log ran at `e84dfda`, three commits back. **A directive to "restore files from git history" would corrupt a healthy tree.**

### 10.2 `002` gap register

Add a header note recording the `F-*` → `RF-*` rename and the M-5 retirement schedule · rename column `ID` → `RF-ID`, add `Authorising ADR` · **restate `RF-08` as retired-stale in its own row** (it currently lives only in a sprint-board footnote) · **replace the `F-12` row with `RF-23`** and the eight content assertions, noting *"schema validity is necessary and not sufficient"* · add §4.2a (the alias table) and §4.2b (`RF-23` … `RF-72` verbatim from §9.3) · amend the Wave-2 exit gate to include `RF-23` and `RF-25`, with **`RF-25` red blocking M-3 entry** · amend Wave-3 to the seven-clause M-3 gate · **change Wave-4 row 8 to "schema-valid AND populated"** · append to the deferred table: *"automated environment/arena synthesis — refused as a substrate feature; preregistered oracles exist so the judged cannot author its own arena; may enter as pack data behind a preregistration event"* and *"CRDT / eventual consistency / cache-coherence protocols for inter-agent state — refused; `project_id` is the consistency unit with a total order."*

### 10.3 `docs/05_adr/`

**CREATE** `0077`…`0084` from §7 · **UPDATE** `INDEX.md` with eight rows and their narrows/extends citations · **DO NOT EDIT** `0069`–`0076` or any `ADR-M0-*` — `ADR-0082` D5 **extends** `ADR-M0-02` by citation with evidence; it does not edit it · **`DEFERRED_REJECTED.md`** gains `REJ-13` (automated arena synthesis as a core capability) and `REJ-14` (CRDTs / eventual consistency for inter-agent state).

**Note on `ADR-0070`:** it still cites `layer0/scheduler/driver.py`, deleted at 2.2-B. **Do not silently edit it.** At M-5 a narrowing ADR may record that the path is historical.

### 10.4 `docs/SPEC.md` — section-by-section

| § | Directive |
|---|---|
| Header | Version anchor → `v0.6.1 Evidence & Correction Lock (ADRs 0069–0074, Director-approved by 0075; corrections 0077–0084)`. **Do not** cut `pyproject.toml` from `0.4.5b1` — that is M-5/v0.7.0 and Director-only. |
| §1.0 | Append: *"`spawn` is engine-owned in v0.6. `agent.spawn` as a capability-mediated verb is design-locked by `ADR-0080` and implemented at M-6. Delegation targets are resources: a grant may permit spawning one `D_H` and deny another. `ChildSpawned`/`ChildReturned` already exist."* |
| §1.1 | Insert the **Universal Turn Loop as Mechanism** claim with `RF-66` named inline and the M-8 adjudication date stated. |
| §1.2 | Plugins row → **seven** kinds (add `PluginDiscovered`, `PluginVerified`); writer table → both `registry`-owned; note the count change **56 → 58**. |
| §1.4 | Add the **Stigmergic Coordination Property** with the honest complexity bound (§3.2) and `RF-60` as its falsifier. Mark as a claim **under measurement, activated at M-7** — not a v0.6 property. |
| **§2.3** | **The largest edit.** Replace the fixed-slot example with the `mhf.manifest/2` example of §9.1. State: components are a named map; `kind` does not imply cardinality one; slot names are pack convention; **`bindings` is a closed relation roster and cycles are permitted with termination by budget**; `D_H` covers nodes **and edges**; `/1` frozen through M-4, removed at M-5. Include the critic-loop example as the concrete demonstration. |
| §2.3 (new) | *Declared absence* — the three evidence states, the `D_H` consequence, `unattributable_for_promotion` as **derived not declared**, and the categorical illegality of an unsigned verdict under every composition. |
| §2.3 (new) | *Execution profiles* — `ADR-0083`: profiles are composition data, enter `D_H`, and the router is planner-side with no authority. |
| §4 | Pack #2 is **Math & Formal Deductive Verification** and is the **M-5 generality gate**. Acceptance: zero diffs under `packages/{domain,kernel}/` **and** trajectory parity. TableWorld → **Pack #3**. |
| §5.3 | Replace the conflated `F(θ)` with the corrected **VFE (inference) / EFE (action selection)** formulation of §4. Add the constrained form with a retained Pareto frontier and the Brier calibration metric. |
| §5.4 | Add the **four-tier flywheel**: T0 memoization, T1 macro-tool compilation, T2 skill cards, T3 DPO — with T0's evidence gate. |
| §7 | Replace the trajectory example with a **populated** one. State the eight `RF-23` assertions as normative. Define `D_R` constructively. Add the required-now/required-later table and **`measurement_status: unavailable` — unknown is never zero.** |
| §9 | Append `REJ-13` and `REJ-14`. Do not duplicate the list into the ADRs — §9 is its single home once M-5's collapse lands. |
| I-1…I-11 | **I-9 gains teeth:** *"…a valid harvest row — populated turns, non-zero per-turn cost and latency, a model fingerprint or a reasoned unavailable, `D_R` distinct from `D_H`, and a signed verdict or an explicitly-reasoned null. Schema validity is necessary and not sufficient."* **I-11 gains its precondition:** *"…whose precondition is `RF-25` and whose gate is `RF-60` plus selector-disjointness."* |

### 10.5 Board, roadmap, wave plans, and agent guidance

**`sprint_active.md`** — strike the Wave-1 follow-up row carrying trajectory cost to Wave 4; replace with the `ADR-0078` ruling and the *mechanism* reason (**the settled ledger is already in `assemble_trajectory`'s arguments and is being discarded**) — **this closes discrepancy D-C in writing** · add NOVA-1/2/3, 2.6-A…D to Wave 2 · rebalance Wave 3 to six sprints per §8.2 and **re-label `3.2-C` `DEV-LOCAL` → `DIRECTOR`** · Wave-4 row 8 → *"schema-valid and populated"*, add NOVA-5 · **Decision queue:** ratify `0077`–`0084` (Director) · new event kinds `PluginDiscovered`/`PluginVerified` (Director, ruled in `ADR-0081` D3) · retire `vanguard_body_detailed.md` (Director) · `3.2-C` re-label (Director) · adjudicate the six red tests (Tech Lead) · **Director-Only Escalations gains:** manifest schema version bump · falsifier namespace change · any change to the nine-row gate · any `agent.spawn` implementation before M-6 · **any router activation before M-7**.

**`milestones.md`** — add a **Version** column across M-2…M-10 per §8.1 · M-3 exit gains all seven ledgered transitions, five topologies → five `D_H`, absent-vs-forged, profile schema, NOVA-4, and **`pyproject.toml` cleanup** · M-4 row 8 → populated · M-5 names Pack #2 explicitly and adds `RF-51`, T0 memoization, and the TCB metric replacement · M-7 gains `RF-60` and router activation · Standing Constraints gains *"a wave may shed breadth; it may never shed falsifiers."*

**Wave plans** — `wave3_extensibility.md`: add sprints 3.3–3.6 and 3.1-Z, extend 3.1 acceptance to seven ledgered transitions, add the NOVA-4 table with `RF-38`…`RF-45`, re-label `3.2-C`, keep WASM / mandatory signatures / any second product plugin explicitly out. `wave4_foundation_e2e.md`: strike the cost deferral, row 8 → populated, add `4.1-E` NOVA-5, and specify the evidence bundle contents — ledger digest · `D_H` · `D_R` · full trajectory · containment probes · **the exact `RF-*` list green on that `run_id`**. **Do not create `wave5_*` yet** — detailing unstarted work is waste; it is authored at M-4 exit.

**`CLAUDE.md` / `AGENTS.md`** — **§2's Pre-Development Hold block is stale**: it reads *"Wave 0 is the only authorized next code change"* and *"No Wave 0 code has been written yet"* while M-0 and M-1 are complete and M-2 is at re-gate round 4 `[VERIFIED contradiction]`. **A stale hold notice trains every future reader to ignore hold notices.** Replace with the current state. Correct the 283 → 248 figure (H-9), add `packs/math-formal/` (M-5), mark `layer0/` as deleted at M-3, and add ADRs `0077`–`0084` to the precedence list. The two files must not drift.

**`README.md`** — update the reading order to the post-M-5 three-document path (`SPEC.md` → `docs/05_adr/INDEX.md` → `sprint_active.md`), marked as the *target* until M-5 lands it.

### 10.6 Execution order

```text
M-2 wk1   H-1 H-2 H-8 H-9 H-10 H-11        H-8 FIRST, so everything after it is actually checked
M-2 wk1   2.6-A: write ADRs 0077–0084 → docs/05_adr/ ; update INDEX.md          [DIRECTOR]
M-2 wk1   2.6-B: RF-* namespace + alias table + RF-72 linter
M-2 wk2   SPEC §1.0 §1.1 §1.2 §5.3 §7 §9 + I-9/I-11     (§1.4 and §2.3 wait for M-3)
M-2 wk2   002 register §4.2/§4.2a/§4.2b ; sprint_active ; milestones ; CLAUDE/AGENTS/README
M-2 wk2   H-3 H-5 H-6 H-7
M-2 exit  H-4  (Director ruling on vanguard_body_detailed.md)
M-3 entry SPEC §2.3 rewrite (graph + declared absence + profiles) — WITH the code, not before
M-3 exit  wave3 plan final ; layer0/ deleted ; H-12 pyproject cleanup ; stale-path linter re-run
M-4 exit  evidence bundle ; Director attestation                                 [DIRECTOR]
M-5       pyproject version cut → 0.7.0  ·  THE COLLAPSE to the Clean Triad      [DIRECTOR]
```

> **The rule that governs the order:** documentation describing **shipped** behaviour is written *with* the code. Documentation describing **decided** behaviour is written *before* the code. **Nothing describes hoped-for behaviour at all.**

---

## Appendix A · Forensic Verification Log

Re-executed against the working tree at `main` @ `67e1803` during this synthesis pass. Where a predecessor disagreed, the disagreement is named and settled.

| # | Claim | Method | Result |
|---|---|---|---|
| A-1 | Kernel within TCB budget | `python3 tools/linters/check_tcb_budget.py` | ✅ `TCB PASS: 1365 logical lines across 9 files (alarm above 1438)` — **73 LOC headroom** |
| A-2 | Boundary linter file count | `python3 tools/linters/check_boundaries.py` | ✅ **`BOUNDARY PASS: 248 source files checked`** — settles C-1 in favour of `006`; `CLAUDE.md`'s 283 is stale |
| A-3 | `test/agency` test count | `python3 -m unittest discover -s test/agency -t .` | ✅ **`Ran 105 tests … OK`** — settles C-2 in favour of `006`; the board's 107 is stale |
| A-4 | Hollow trajectory | `cat -n vanguard/packages/runtime/trajectory.py` | ✅ **CONFIRMED LIVE** — `_ZERO_COST` at line 10, consumed at 53 (per-turn) and 75 (episode) |
| A-5 | `execution_digest` (`D_R`) computed anywhere | grep across `vanguard/packages/` | ✅ **CONFIRMED ABSENT** — no assignment; `assemble_trajectory` omits the key entirely |
| A-6 | Plugin FSM ledgers all states | `sed -n '30,80p' layer0/registry/lifecycle.py` | ✅ **CONFIRMED GAP** — `_EVENT` maps 5 of 7; `DISCOVERED`/`VERIFIED` → `None`; `_go()` guards `if kind is not None:` and emits nothing |
| A-7 | Only five `PLUGIN_*` kinds exist | grep `domain/wire/types_gen.py` | ✅ `PLUGIN_{RESOLVED,ACTIVATED,QUIESCED,RETIRED,FAULTED}` — no `DISCOVERED`, no `VERIFIED` |
| A-8 | `ChildSpawned`/`ChildReturned` already exist | grep `types_gen.py:63-64` | ✅ `CHILD_SPAWNED`, `CHILD_RETURNED` present — **`agent.spawn` needs no new event kinds** (`008`) |
| A-9 | `components` is a graph | read `domain/artifacts/manifest.py:64` | ✅ **`tuple[tuple[str, tuple[str,...]], ...]` — a role→paths BAG WITH NO EDGES.** Settles §0.6 in favour of `008`: **bindings are the deliverable**, not the named bag |
| A-10 | Two live manifest dialects | `harness_manifest.schema.json` + `vg-code-default/manifest.json` | ✅ schema freezes six slots under `additionalProperties: false`; the JSON path ships seven named components with no edges |
| A-11 | `pyproject.toml` still packages the fork | `grep -n layer0 pyproject.toml` | ✅ **line 40: `include = ["vanguard*", "layer0*"]`** — `008`'s best finding, verified |
| A-12 | Synthesis reference pair | `sha256sum` on both files | ✅ **BYTE-IDENTICAL** — `45bddc74…f7a24e3`. Settles C-3; the prior draft's "keep the successor" instruction is withdrawn |
| A-13 | `DELETE.md` | `ls -la DELETE.md` | ✅ **present, 0 bytes** — refutes `008`'s "absent" |
| A-14 | Review + research corpora | `ls docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/` · `ls docs/06_references/` | ✅ **6 and 12 files, all present.** **Refutes `008`'s "ghost corpus G0" entirely** — that log ran at `e84dfda`, three commits back |
| A-15 | Writer authority table live | `grep -A40 PRIVILEGED_KIND_OWNERS runtime/ledger_emitter.py` | ✅ 22 privileged kinds mapped; `VerdictRecorded → {evaluator_gateway}`; `Plugin*` → `{registry}`; orchestrator owns nothing |
| A-16 | Sealed-membership check live | `cat vanguard/packages/kernel/policy.py` | ✅ Step 1b present under `ADR-0067`; `attenuation.py:183` sets `sealed = request.sealed or request.actions < parent.actions` |
| A-17 | `spawn()` docstring accuracy | read `agency/episode/engine.py:531-572` | ✅ **STALE** — claims the `ADR-0054` kernel gap is open; `ADR-0067` closed it. Corrected by `ADR-0080` C, pinned by `RF-26` |
| A-18 | Classifier fails closed | `cat vanguard/packages/kernel/classifier.py` | ✅ unknown principal ⇒ widens · unheld action ⇒ widens · depth overrun ⇒ widens · undecidable resource pair ⇒ widens (`K-48`) |
| A-19 | Five frozen SPIs, no sixth | `cat vanguard/packages/ports/spi.py` | ✅ exactly five |
| A-20 | `F-*` namespace collision | `grep -o "F-[0-9]\+" docs/04_annex/KERNEL.md \| sort -u` vs `002` §4.2 | ✅ `F-01…F-25` in both with different meanings; `ADR-M0-02` names only `I-*`, `ADR-*`, `S-M*` |
| A-21 | `CostVector` excludes structural dims | read `schemas/mhf/trajectory.schema.json` | ✅ `additionalProperties: false` over `{usd_micros, tokens, bytes, millis}` — the algebra is already schema-enforced |
| A-22 | `check_markdown_links.py` scope | `grep DOC_GLOBS tools/linters/check_markdown_links.py` | ✅ two real globs; the third (`docs/agile/sprint6B/*.md`) matches nothing |
| A-23 | `CLAUDE.md` hold notice | read §2 vs `sprint_active.md` | ✅ **STALE** — says *"No Wave 0 code has been written yet"*; M-0/M-1 complete, M-2 at re-gate round 4 |
| A-24 | `CapabilityRevoked` emitter | grep `vanguard/packages/` | ✅ in the catalog; **no production emitter, no falsifier**. Registered `RF-64`, M-7 |

**Not examined**, so the boundary of the finding is honest: the TypeScript client lattice (`vanguard/clients/`); the full test suite was not re-executed end to end (per-suite only); `benchmarks/` and `lab/` were mapped, not exercised; no runtime or E2E execution was performed; `KERNEL.md` was read for the namespace question only, not audited rule-for-rule.

---

## Appendix B · Provenance Matrix — Which Idea Came From Where

Attribution is recorded so a future reader can trace any ruling to its origin and, if it fails, know which pass to re-examine.

| Contribution | Origin | Status in this synthesis |
|---|---|---|
| **α/β/γ/δ Pareto profile matrix** with concrete latency bands, token ranges, routing, and topology per profile | **`002_beta`** §11.4 | **PROMOTED to Pillar I / `ADR-0083`.** The single strongest contribution in the predecessor set and absent from four of the six. |
| **Macro-skill distillation** — *"turns 50k tokens of agent reasoning into a 500-token tool call"* | **`002_beta`** §11.5 | **PROMOTED to Pillar IV / `ADR-0084` T1**, with a ceiling-subset constraint added so it collapses tokens and not authority. |
| Blackboard `W = ⟨A, H, E, T⟩` and the informational-bottleneck projection `B_θ` | `002_beta` §11.2 | Adopted as framing for §3; the bottleneck is `IContextManager` and needs no new primitive. |
| **Topology-cost SOTA grounding** — reward-guided autoregressive topology generation, `E2-Explainer` causal edge pruning, the *"communication topology is the dominant cost driver"* finding | **`004_delta`** §1.2(b) | **ADOPTED into §3.1.** The best-cited stigmergy argument in the set. |
| Twelve numbered leadership rulings R-1…R-12 with per-tension bound falsifiers | `004_delta` §1.1, §2 | Absorbed into §1.3 and §6. |
| A-B-C-D restated as *"the order in which B and C become generic without weakening A or collapsing D"* | `005_epsilon` §0, §1.2(e) | **ADOPTED verbatim as §1.2's framing.** The clearest one-line statement of the whole plan. |
| Compact ADR form with explicit narrows/extends and a landing sprint | `005_epsilon` §3 | Adopted as the ADR template in §7. |
| **VFE (inference) ≠ EFE (action selection)**, and the naming of the category error in the internal research corpus | **`006_fi`** §5.2 | **ADOPTED as Pillar III.** Replaces the conflated formulation carried by `002`, `004`, `005`, **and the prior `007`**. |
| **Exact McNemar** with enumerated binomial cases, plus Pareto-frontier safety gating | **`006_fi`** §5.7, §7.5 | **ADOPTED into §5.4.** `002` and `005` prescribed χ² ≥ 3.841, which `MEASUREMENT.md` M-03 explicitly forbids. |
| **Cycles permitted in the composition graph**, termination by budget | **`006_fi`** T-1 | **ADOPTED — and it reverses the prior `007` draft's D8.** A critic loop is cyclic. |
| **State-plane work protocol** — `WorkPublished`/`WorkClaimed`/`ArtifactPublished`/`WorkReturned`/`WorkReleased` with CAS on the reduced version | **`006_fi`** §7.4 | **ADOPTED into §3.3**, flagged as design placeholders requiring a Director-gated event-kind decision at M-7. |
| **`measurement_status: unavailable`** — unknown is never a fabricated zero | **`006_fi`** T-4 | **ADOPTED into `ADR-0078` D4.** A materially better formulation than "non-zero cost". |
| Fully-qualified `module.Class.method` falsifier targets with existing-vs-proposed marking | **`006_fi`** §7.5 | **ADOPTED as §9.3's format.** |
| Boundary=248, agency=105, byte-identical synthesis pair | **`006_fi`** §1.2, §1.4 | **ADOPTED as corrections C-1…C-3.** All three independently re-verified. |
| Bubblewrap policy-args caveat and the setuid advisory; *"uses bwrap" ≠ a containment claim* | **`006_fi`** §1.3 | **ADOPTED into M-4 row 4** — containment requires recorded probes, not a dependency name. |
| **`pyproject.toml` still packages `layer0*`** | **`008_alfa`** App. B/7 | **ADOPTED as H-12 / `ADR-0081` D5.** The best finding in `008` and unique to it. |
| **The named bag is not a graph — `bindings` is the deliverable of T-1** | **`008_alfa`** App. B/2 | **ADOPTED as §0.6.** Corrects the prior `007`'s B-2 claim. |
| `ChildSpawned`/`ChildReturned` already exist | `008_alfa` App. A | Adopted into `ADR-0080` D2 — no new kinds needed for spawn. |
| Pack #2 ≠ TableWorld, because using the orphaned adapter would fake the I-7 proof | `008_alfa` App. B/5 | Adopted into §8.3's demotion rationale. |
| `F-*` namespace collision across the annex and the register | prior **`007_zeta`** | Retained as `ADR-0082` D5 + `RF-72`. Unique to `007`; independently reached by `008` §7.3. |
| **`D_R` is never computed anywhere in the tree** | prior **`007_zeta`** | Retained as `ADR-0078` D3 + `RF-27`. Unique to `007`. |
| **M-4 row 8 accepts a hollow trajectory — the stop line contains the defect it exists to prevent** | prior **`007_zeta`** | Retained as §8.2's strengthening. Unique to `007`. |
| The NOVA-1 timing contradiction resolved by *mechanism* — the settled ledger is already in `assemble_trajectory`'s arguments and is being discarded | prior **`007_zeta`** | Retained in `ADR-0078` and §10.5. |
| Plugin FSM cannot ledger `DISCOVERED`/`VERIFIED` | prior **`007_zeta`** and **`006_fi`** and **`008_alfa`**, independently | Retained as `ADR-0081` D3 + `RF-43`. **Three independent passes found it; the prior `007`'s "unique to this pass" claim is withdrawn.** |
| **T0 memoization as a deterministic, ML-free flywheel tier** | prior **`007_zeta`** §8 (Obligation Market) | **PROMOTED to Pillar IV / `ADR-0084` T0**, with an evidence gate added. |
| Typed obligations + witnesses as an alternative architecture | prior `007_zeta` §8 | **RETIRED as an alternative.** Its three transplantable ideas (T0 memoization, priced work, pull-based frontier) are now in `ADR-0083`/`ADR-0084` and §3.3; the rest is not proposed. |

---

## Appendix C · Corrections Applied to Predecessor Proposals

Recorded because a synthesis that hides what it overrode is not a synthesis.

| # | Proposal | Correction |
|---|---|---|
| 1 | `002`, `004`, `005`, prior `007` | **VFE/EFE conflation.** Replaced by §4's separated formulation. |
| 2 | `002`, `005` | **McNemar χ² ≥ 3.841.** Replaced by the exact binomial per `MEASUREMENT.md` M-03. |
| 3 | `002` | **"100% pass across ~1176 tests" as a v0.6.3 exit gate.** Struck. The `002` register is explicit that **honest red is acceptable and lexical green is not**; three Ollama-offline failures are environmental. Replaced by §8.2's M-2 clause: *every currently-red test adjudicated as product drift or environment sensitivity with a bounded reason.* |
| 4 | `002` | **FSM table invents `PluginQuiescing` and collapses `ACTIVATED --fault--> RETIRED`**, losing the `FAULTED` state. Replaced by §9.2's 13-row table. |
| 5 | `002` | Baseline `afa8e2a` is stale; ADRs are pseudo-code sketches without reversal conditions. Rebuilt in §7. |
| 6 | `004` | The first-published revision was **truncated after §2.9**, delivering 3 of 8 promised sections. Its completed §3–§8 are consistent with this synthesis; its §1.2(b) is adopted. |
| 7 | `005` | **FSM folds `VERIFIED` into a `PluginResolved` payload flag** — it notices the missing transition and resolves it by *not ledgering it*, contradicting the *"every transition ledgered"* gate it states two sections earlier. Replaced by `ADR-0081` D3 (two new kinds). |
| 8 | `006` | **Pareto flexibility is its thinnest dimension** — promotion-frontier safety only, no task-profile routing. Supplied by `ADR-0083`. `ADR-0077` at 280 lines is also far outside this repo's 20–40-line ADR norm; §7.1 is condensed. |
| 9 | `008` | **"Ghost corpus G0" is refuted** — all 18 cited files exist at HEAD. **`DELETE.md` is present, not absent.** Both are stale-tree artifacts from `e84dfda`. **Neither directive may be executed.** |
| 10 | prior `007` | **`RESEARCH_THEORETICAL_SYNTHESIS` "keep `_B`, the successor"** — the files are byte-identical; there is no successor; the rationale was inferred and marked `[VERIFIED]` on a front-matter glance. **Withdrawn.** |
| 11 | prior `007` | **Two incompatible `RF-nn` numberings** reconciled only by a precedence note, in a document selling zero-guesswork. **Replaced by §9.3's single monotonic sequence.** |
| 12 | prior `007` | **"Findings not present in any prior review"** — three passes independently found the FSM gap and a sharper form of the manifest finding. **Claim withdrawn**; Appendix B attributes honestly. |
| 13 | prior `007` | **Cycles fail at compose (ADR-0077 D8).** Reversed per §0.5 — a critic loop is cyclic. |
| 14 | prior `007` | **B-2 "the component graph already exists in `domain/`."** Corrected per §0.6 — it is a path bag with no edges. |

---

## Appendix D · External Sources

**Harness engineering** — [Agent Harness Engineering: A Survey](https://picrew.github.io/LLM-Harness/main.pdf) · [Agentic Harness Engineering: Observability-Driven Automatic Evolution of Coding-Agent Harnesses](https://arxiv.org/abs/2604.25850) · [Harness-Bench](https://arxiv.org/html/2605.27922v1) · [From Question Answering to Task Completion: A Survey on Agent System and Harness Design](https://arxiv.org/pdf/2606.20683) · [Harness as an Asset (CAAF)](https://arxiv.org/pdf/2604.17025) · Anthropic, [Building a multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)

**Stigmergic / shared-state coordination** — [CodeCRDT](https://arxiv.org/pdf/2510.18893) · [Beyond Text-Passing: Shared Cognitive Substrates](https://openreview.net/forum?id=RRIw2L4Z1g) · [PatchBoard](https://arxiv.org/pdf/2605.29313) · [Token Coherence (MESI for MAS)](https://arxiv.org/pdf/2603.15183) · [LLM multi-agent blackboard](https://arxiv.org/abs/2510.01285) · ICML 2025, [asymptotic analysis with LLM primitives](https://proceedings.mlr.press/v267/meyerson25a.html)

**Capability sandboxing, provenance, execution security** — [From Agent Traces to Trust](https://arxiv.org/pdf/2606.04990) · [Lingering Authority: Revocable Resource-and-Effect Capabilities](https://arxiv.org/pdf/2606.22504) · [Balkanization of Execution-Security Research (TOCTOU)](https://arxiv.org/pdf/2607.05743) · [Progent](https://arxiv.org/abs/2504.11703) · [MiniScope](https://arxiv.org/abs/2512.11147) · [Landlock](https://www.kernel.org/doc/html/latest/userspace-api/landlock.html) · [Bubblewrap security notes](https://github.com/containers/bubblewrap) and the [2026 setuid advisory](https://github.com/containers/bubblewrap/security/advisories/GHSA-xq78-7hw4-5jvp) · [W3C PROV](https://www.w3.org/groups/wg/prov/publications/) · [in-toto / SLSA provenance](https://github.com/in-toto/attestation/blob/main/spec/predicates/provenance.md)

**Active inference, credit assignment, trajectory RL** — [Expected Free Energy-based Planning as Variational Inference](https://arxiv.org/html/2606.20658) · [Active Inference as a Convex MDP](https://arxiv.org/pdf/2607.20152) · [ASTRA](https://arxiv.org/abs/2601.21558) · [Beyond Trajectory-Level Attribution: Graph-Based Credit Assignment](https://arxiv.org/abs/2605.26684) · [TRACE](https://arxiv.org/abs/2607.13988) · [Agent Lightning](https://arxiv.org/abs/2508.03680) · [DPO](https://arxiv.org/abs/2305.18290) · [DMPO](https://arxiv.org/abs/2406.14868)

**Declarative composition & harness search** — [AgentFlow: Agent Dependency Graphs](https://arxiv.org/html/2607.01640) · [Graph-Based Agent Workflow Orchestration: the 2026 Landscape](https://zylos.ai/research/2026-04-14-graph-based-agent-workflow-orchestration-production/) · [Declarative Data Services](https://arxiv.org/abs/2605.20690) · DeepMind, [AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) · ICLR 2026, [Darwin Gödel Machine](https://openreview.net/pdf?id=pUpzQZTvGY) · [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)

---

## Closing Statement of the Leadership 7

**What `v0.6.1` locks that `v0.6.0` did not.** `v0.6.0` locked the *primitives*: authority as a reference monitor, state as fold, evidence as an exterior signature, identity split three ways, recursion as one attenuated delegation. `v0.6.1` locks the *surfaces those primitives are reached through* — a composition algebra with real edges (`0077`), a corpus rich enough to learn from and honest enough to say *unavailable* rather than zero (`0078`), guardrails that may be declared absent but never forged (`0079`), a delegation verb whose design is fixed before its implementation is permitted (`0080`), a plugin lifecycle whose every transition leaves evidence (`0081`), two standing claims made refutable (`0082`), an execution frontier the substrate can actually move along (`0083`), and a flywheel that begins compounding deterministically on day one rather than statistically in a year (`0084`).

**`v0.6.0` made AETHER trustworthy. `v0.6.1` makes it general. `v0.9.0` makes it a swarm. `v1.0.0` makes it improve itself — on a corpus whose evidence was never forgeable.**

**The M-4 stop line is unchanged and non-negotiable.** Nine rows, one uninterrupted real run, one `run_id`, zero human intervention. Row 8 is *strengthened*, not widened — a hollow trajectory could have passed the original wording, and **the stop line must not contain the defect it exists to prevent.** `agent.spawn`, concurrency, router activation, Pack #2, and all of M-5 through M-10 remain **out of implementation scope** until the gate is green. Any temptation to widen scope to make the run pass is escalated to the Director, not absorbed by the sprint.

**M-5 through M-10 exist as outcomes and gates only.** No sprint-level detail is authorised beyond §8.2. Detailing unstarted work is waste, and worse, it manufactures the appearance of a plan where only an intention exists.

**What a developer reads first, today:** `README.md` → `docs/SPEC.md` → `docs/05_adr/INDEX.md` (ADRs `0069`–`0084`) → `docs/03_sprints/sprint_active.md` → **§9 of this document for the implementation bridge.** After M-5's collapse the first four become three, and this document retires into git history with the rest of the review corpus.

**The single sentence this body would keep if it could keep only one:**

> **Make the corpus learnable, the composition surface general, the frontier navigable, and the flywheel deterministic — in that order, before the stop line — because everything after M-4 consumes one of them, and none can be repaired retroactively.**

---

*Prepared as a synthesis of six independent leadership passes. This document is **advisory** and amends nothing. Law remains [`docs/SPEC.md`](../../../../docs/SPEC.md) → [`docs/05_adr/`](../../../../docs/05_adr/) → [`docs/04_annex/`](../../../../docs/04_annex/). Every ruling in §1–§6 becomes binding only through the corresponding append-only ADR in §7, committed with a Director signature and carrying its bound falsifier. No specification file, ADR, schema, or source file was modified in producing this document.*
