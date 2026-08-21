# 004 — Delta Review: Full GLM-5.3 Proposal — AETHER as a General Task-Solving Swarm Meta-Framework

| Field | Value |
|---|---|
| **Classification** | Engineering Director / Leadership-7 collective executive review and technical proposal |
| **Body** | Leadership 7: Engineering Director · CTO · CIO · Principal Staff Engineer · Principal Systems Architect · Tech Lead · PhD AI Specialist (Cognitive Systems, Active Inference & RL) |
| **Subject** | Exhaustive delta review of AETHER/Vanguard at `main` @ `85070be`, and the definitive phased proposal for evolving the substrate from a coding-agent proving ground into a **general task-solving swarm meta-framework** |
| **Version ladder addressed** | v0.6.1 → v0.6.2 → v0.6.3 → v0.7.0 → v0.8.0 → v0.9.0 → v1.0.0 |
| **Date** | 2026-08-21 |
| **Evidence base** | `docs/SPEC.md` + ADRs `0069`–`0076`; `docs/00_overview/SYSTEM_OVERVIEW.md` (V2 audit); Principal reviews `001`–`006`; `docs/06_references/` research corpus; **forensic code verification against `vanguard/packages/` on disk**; live arXiv SOTA survey performed 2026-08-21 |
| **Status** | **ADVISORY PROPOSAL.** This document amends nothing. Law remains `docs/SPEC.md` → `docs/05_adr/` → `docs/04_annex/`. The drafted ADR texts in §3 are **proposals for adoption**, not adopted law. |
| **Hard constraint honored** | No specification, ADR, or source file was edited in producing this report. The full report lives in this single file at repository root. |

---

## Table of Contents

0. Verification Basis & Method
1. Executive Rulings & Strategic Paradigm Shift
2. Adjudication of All Open Architectural Tensions (T-1 … T-9)
3. Drafted Append-Only ADR Catalog (ADR-0077 … ADR-0082)
4. Phased Milestone Roadmap & Version Ladder (v0.6.1 → v1.0.0)
5. Theories, Algorithms & Mathematical Formulations
6. Zero-Guesswork Developer Implementation Bridge
7. Repository Hygiene & Document Update Cascade
8. Leadership-7 Sign-Off Matrix & Final Word

---

## 0. Verification Basis & Method

Every load-bearing claim in this report was grounded in one of three evidence lanes, each re-checked during this pass:

1. **Forensic code verification (`vanguard/packages/`, `packs/`, `layer0/`, `test/`, `tools/linters/`).** Verified on disk, not cited from documents: the hollow-trajectory defect (`vanguard/packages/runtime/trajectory.py` — `_ZERO_COST` at line 10, injected per-turn at line 53 and per-episode at line 75); the fixed-slot manifest (`packs/code-default/harness.yaml` — exactly `planner`, `context`, `memory`, `evaluation`, `toolkits` as the only composition keys); the S0–S12 dispatch pipeline (`kernel/dispatch.py` lines 4–19: ENTER, PARSE, RESOLVE, DESCRIBE, CLASSIFY, AUTHORIZE, GRANT, RESERVE, VERIFY, INTENT(fsync), DISPATCH, COMMIT, RELEASE, EMIT, with guards K-04…K-08 and K-47); the engine-owned `spawn()` (`agency/episode/engine.py` line 531 — planners receive only `plan/observe/reflect` over the SPI); TCB budget **1365 / 1438 logical LOC** (re-executed `tools/linters/check_tcb_budget.py` during this review: PASS); `layer0/` reduced to `compose/`, `registry/`, `events/` only; 15 linters on disk, 9 CI-wired.
2. **Internal research literature (`docs/06_references/`).** The A-B-C-D operating model (`RESEARCH_k3_harness-suggestion.md` §2), the first-principles mathematics (`RESEARCH_THEORETICAL_SYNTHESIS.md` §2: VFE objective, credit assignment, 384d hybrid retrieval, Elo decay, McNemar protocol), and the harness-as-independent-variable thesis (`RESEARCH_harness_agentic_coding_builder_research_and_framework.md`: Terminal-Bench 2.0, same GPT-5.3-Codex model, harness swing 64.7% → 78.4%).
3. **Active external SOTA research (performed 2026-08-21).** Live arXiv queries on frontier multi-agent architectures, agentic RL over trajectories, active inference in agent loops, capability-based sandboxing, and DPO. Key contemporaneous evidence: topology-cost-aware MAS design (reward-guided autoregressive graph generation for communication topologies, 2026-08-20; E2-Explainer's causal pruning of redundant communication edges, 2026-08-13 — both confirming that **communication topology is the dominant cost driver in multi-agent LLM systems**); trajectory-level learning trends (EnvHarness 2026-08-20: environment-as-harness plug-in layer with retained verifiers; Agentic ESOpt 2026-08-18: evolution strategies beat backprop-RL at long horizons precisely because *trajectory-level attribution without reward decomposition* is the hard part — direct confirmation of our corpus-first strategy); curiosity-based intrinsic reward for multi-turn agents (Wan et al. 2025); capability-based defense (CaMeL operationalization 2025-05: capability-mediated sandboxing against prompt injection — the same design point as our S0–S12 mediation); DPO (Rafailov et al., arXiv:2305.18290: closed-form reward parameterization, classification loss over (chosen, rejected) pairs, no explicit reward model — with documented failure modes of reward hacking and distribution collapse that our exterior-signed verdicts structurally exclude).

The Leadership 7's standing epistemic rule applies throughout: **a claim is either verified against disk, cited to its source, or it does not carry weight in a ruling.**

---

## 1. Executive Rulings & Strategic Paradigm Shift

### 1.1 The consensus of the Leadership 7

The seven roles deliberated over the evidence lanes above and reached **unanimous consensus** on the following rulings. Each is binding on this proposal's roadmap; none amends Law directly — the ones requiring Law land as drafted ADRs in §3.

| # | Ruling | Owner | Weight |
|---|---|---|---|
| **R-1** | **The destination is re-affirmed as the swarm meta-framework, reached strictly through the substrate path.** Swarms are spawn-topologies + policy over the State Plane — never a new engine, never peer-to-peer chatter. | CTO | Strategic |
| **R-2** | **The M-4 Foundation Stop Line is absolute.** No meta-cognition, no swarm features, no `agent.spawn` kernel change, before 9 verified rows on one uncheated real run. The Director personally owns the stop. | Engineering Director | Non-negotiable |
| **R-3** | **NOVA-1 (un-hollowing the trajectory corpus) executes immediately in Wave 2.** Every episode completing before the fix is a permanently degraded training row; the clock is irreversible. | Tech Lead + Principal Staff Engineer | Immediate |
| **R-4** | **The manifest becomes a Named Component Graph (ADR-0077) at Wave-3 entry (3.1-B).** The Director scope call is made **now**, not at mid-wave: composing the graph twice is the waste the roadmap exists to prevent. | Engineering Director (scope call) | Immediate design, Wave-3 implementation |
| **R-5** | **Guardrails adopt the Absent-vs-Forged model (ADR-0078).** "You may turn a guardrail off; you may never turn off the record that it was off." Unsigned verdicts remain categorically illegal under every configuration. | CIO + Principal Systems Architect | Law-level |
| **R-6** | **`agent.spawn` is designed now (ADR-0080), implemented in M-6 only.** Design-now protects against a forced engine rewrite later; defer-implement protects the TCB before the stop line. | Principal Systems Architect | Sequencing |
| **R-7** | **`layer0/` dies at Wave 3 by absorption, not deletion** (ADR-0081): registry + compose compiler move into `vanguard/packages/runtime/` under the NOVA-4 negative-test suite, then the fork is deleted behind a behavioral parity gate per SPEC §1. | Principal Staff Engineer | Wave-3 |
| **R-8** | **The Universal Turn Loop claim is published as a mechanism claim with a bound falsifier (ADR-0082)** — not asserted as metaphysics. ADR-M0-10 stands: no metaphysics in normative documents. | PhD AI Specialist | Law-level |
| **R-9** | **Concurrency is proven cheap, now: NOVA-2 (cold suspend/resume from WAL) lands before M-3 closes.** It is the single test that decides whether M-7 is a scheduling refactor or a rewrite. | Tech Lead | Immediate |
| **R-10** | **Pack #2 is Math & Formal Deductive Verification, and it is a gate, not a nice-to-have** (M-5). Zero diffs under `domain/` and `kernel/`, plus trajectory parity, or I-7 (domain blindness) remains a thesis. | Principal Staff Engineer | M-5 gate |
| **R-11** | **Documentation collapses to the Clean Triad post-M-4** (scheduled, not immediate). Mid-flight documentation surgery during Waves 2–3 is strictly worse than the duplication it removes. | Engineering Director | Post-M-4 |
| **R-12** | **The learning layer (M-10) is corpus-first, exterior-signed, and McNemar-gated.** Active inference math stays in SPEC §5.3 as calibrated `P(pass | action, context)`; DPO harvesting is unforgeable by construction; promotion is a partial order over a frontier the system cannot drive itself. | PhD AI Specialist | M-10 |

### 1.2 SOTA 2026 alignment — the four paradigms this plan is aligned with

**(a) Harness Engineering as the independent variable.** The industry has converged on the thesis this project locked at v0.6.0: *model is cognitive capacity; agent is an iterative decision policy; harness is the operating system that turns that policy into verifiable autonomous behaviour.* The Terminal-Bench 2.0 evidence in our own research corpus — the same GPT-5.3-Codex model swinging from 64.7% to 78.4% purely by harness — is now the mainstream result. The 2026 literature extends it in two directions we already accommodate: **EnvHarness** (2026-08-20) treats the *environment* itself as a plug-in harness layer whose reshaped worlds retain their original verifiers — structurally identical to our "new capability enters as plugin + manifest + policy + composition" growth rule; and **Agentic ESOpt** (2026-08-18) shows trajectory-level black-box optimization outperforming backprop-RL at long horizons — vindicating our decision to make the trajectory corpus (`mhf.trajectory/1`) the substrate's primary learning asset rather than embedding a differentiable training loop in the kernel. **Leadership consequence:** the moat is not the agent; it is the trustworthy corpus plus the composition surface. Both are named as Wave-2/Wave-3 deliverables in §4.

**(b) Stigmergic swarms via the State Plane, not O(N²) chatter.** The strongest 2026 MAS results are unanimous that communication topology is the dominant cost driver in multi-agent LLM systems: reward-guided autoregressive topology generation (2026-08-20) exists specifically because token consumption of fully-connected chatter is prohibitive; E2-Explainer (2026-08-13) shows that masking/pruning communication edges while *preserving task outcome* is both explainable and cheaper; topology explanation is formalized as causal attribution over communication subgraphs. AETHER's answer is stronger than all of these because it was architectural rather than algorithmic: **agents do not talk to each other at all.** Coordination is *stigmergic* — agents coordinate by writing and reading durable events in the immutable State Plane (`State = fold(events)`), exactly as social insects coordinate through marks on the environment. The O(N²) peer-message channel never exists; the coordination medium is the append-only ledger with per-Project hash chains, and the coordination cost is O(N) in ledger events. Topology, when it is needed, is a **projection/policy over events** (ADR-0070), not a communication mechanism. **Leadership consequence:** the swarm claim must be proven as "N logical agents, one ledger, K ≪ N workers" — which is precisely NOVA-2 + M-7's design.

**(c) The Separability Thesis.** Our theoretical briefing (review `006`, Ch.1) derives it and the 2026 empirical literature keeps re-confirming it: *that which solved the problem must be separable from that which judged the solution, and the judge must be unreachable by the judged.* Contemporaneous multi-agent research shows measurable, state-dependent misalignment emerging in competitive multi-agent environments *without engineered elicitation* (2026-08-14) — i.e., agents that can influence their evaluation channel corrupt it, silently. The exterior Ed25519-signed evaluator (UID 10002, nonce-bound verdicts, gateway-only writes), the rootless sandbox (UID 10001), and the fail-closed capability ceiling are the structural guarantee that AETHER's training signal can never be corrupted by the agent that produced it. **No competing framework occupies this intersection**: flat declarative composition surface × mathematically verified authority boundary × unreachable exterior evaluation. That intersection is the moat (CTO ruling).

**(d) The A-B-C-D Foundation.** The k3 research's load-bearing contract remains the correct generality test, and we re-verify its current state on disk:

| | Property | Plane | Verified state at `85070be` |
|---|---|---|---|
| **A — Authority** | S0–S12 mediator: descriptor-bound grants, `Capabilities(child) ⊆ Capabilities(parent)`, typed leases (additive `{usd_micros, tokens, bytes, millis}` vs structural `{depth, turns}`), fail-closed selectors, one JCS canonicalisation, one writer | Decision | **Sound.** TCB 1365/1438 LOC. Unchanged by this proposal. |
| **B — Behavior surface** | The composition a developer declares (manifest → frozen harness) | Decision | **The weak plane.** Fixed-slot template today; becomes the Named Component Graph (ADR-0077). |
| **C — Corpus** | State + Evidence: WAL `fold(events)`; `mhf.trajectory/1` at every `EpisodeCompleted`, rich with per-turn cost, model fingerprint, signed verdict-or-explicit-null | State / Evidence | **Hollow.** `_ZERO_COST` verified at `trajectory.py:10,53,75`. NOVA-1 closes it in Wave 2. |
| **D — Digest** | Measurement identity: `D_H` (composition) ≠ `D_R` (run) ≠ `D_X` (experiment) | Identity | **Locked and correctly scoped**; remains generic only if B and C stay generic — hence ADR-0077 and NOVA-1 are both pre-Wave-4 obligations. |

**The paradigm shift, stated once:** AETHER stops being *a coding agent with a kernel attached* and becomes *the operating substrate from which coding agents, debate systems, tree searches, critic loops, evolutionary searches, and stigmergic swarms are all compositions* — each expressed as a Named Component Graph + spawn topology + policy over one loop, one ledger, one judge. Everything in §2–§7 exists to make that sentence falsifiable rather than aspirational.

---

## 2. Adjudication of All Open Architectural Tensions (T-1 … T-9)

The nine tensions catalogued in the V2 audit (§5 of `SYSTEM_OVERVIEW.md`) are adjudicated here. Format per tension: *state → ruling → rationale → falsifier*. All ADR references point to the drafts in §3.

### 2.1 T-1 · Manifest shape — fixed slots vs. Named Component Graph

**State [VERIFIED].** `packs/code-default/harness.yaml` exposes exactly five composition keys (`planner`, `context`, `memory`, `evaluation`, `toolkits`) plus `model_routes`, `capabilities`, `budget`, `approval_policy`. Debate (N planners), critic loops (planner + critic evaluator in a loop), tree search (planner spawning branch planners), and swarms (N heterogeneous agents) have **nowhere to be named**. The primitives can express all of them (spawn topology + policy — every review agrees); the surface cannot. `D_H` is computed over the manifest shape, so every pack and every attributed trajectory migrates if this changes late.

**Ruling (R-4, Director scope call — MADE NOW).** Adopt the Named Component Graph at Wave-3 entry as **compose-v2** with schema `mhf.manifest/2` (ADR-0077). The five slot names survive as a **pack convention** (`code-default` declares one planner named `main`, one context named `default`, …) — removed from the schema, not from the ecosystem. `D_H` computation extends to cover the resolved graph (nodes: name, ref, config digest; edges: binding section); the graph topology itself is hashed, so two compositions differing only in wiring yield different `D_H`.

**Rationale.** Cost now: one schema revision + a compose-v2 that resolves a map instead of six keys — work 3.1-B is already doing. Cost after M-4: schema migration + `D_H` migration + every pack rewritten + every corpus row attributed to a superseded shape. DeepSeek Harness's flat composition surface is imported; its absent authority boundary is refused (flatness at the composition surface is orthogonal to rigidity at the authority boundary).

**Falsifier (bound).** `test/registry/test_compose_v2_graph.py::test_dh_distinguishes_wiring` — two manifests identical in component set but different in binding edges MUST produce different `D_H`; plus `test_unknown_component_role_fails_at_compose` (a node whose role is not a registered SPI role fails at compose, never at runtime).

### 2.2 T-2 · Spawning — engine-owned vs. capability-mediated `agent.spawn`

**State [VERIFIED].** `EpisodeEngine.spawn()` (`agency/episode/engine.py:531`) is a privileged engine call; `IPlanner` exposes only `plan/observe/reflect`. Every algorithm whose *structure is recursion* — tree search, hierarchical decomposition, conditional delegation — has nowhere to live except inside the engine. ADR-0070's own stated reversal condition is "a feature that needs a new engine."

**Ruling (R-6).** **Design now, implement M-6** (ADR-0080). The full S0–S12 design for `agent.spawn` as a mediated effect is in §3.4: `EffectRequest(verb="agent.spawn")` classified at S4 as capability-widening *unless* covered by an explicit spawn grant; attenuated child budget reservation at S7; child provenance DAG edge; ledgered spawn effect with receipt at S12. Note the ruling's counter-intuitive core: mediation **strengthens** authority — today delegation bypasses the reference monitor because the engine is trusted; under the verb, every spawn is verified, leased, and receipted like every other privileged effect. The objection was never security; it is sequencing — Wave 4 must not absorb a kernel change.

**Falsifier (bound, sketched now, executed in M-6).** `test/kernel/test_agent_spawn_verb.py`: (i) spawn without grant denies at S5; (ii) child capabilities ⊆ parent, verified by grant digests; (iii) child budget reservation debits parent lease at S7; (iv) spawn event appears in the provenance DAG with a parent edge; (v) spawn receipt carries `lease_id` + `grant_digest` (P1-9 fields).

### 2.3 T-3 · Guardrails — mandatory mechanism vs. declarable "Absent-vs-Forged"

**State.** `schemas/mhf/harness_manifest.schema.json`, `runtime/compose.py`, and the evaluator gateway currently assume an evaluator is always composed; a research/math composition is forced to carry a UID-10002 daemon it does not need, or is impossible to declare at all.

**Ruling (R-5).** Adopt the **Absent-vs-Forged** model (ADR-0078). A composition may declare `evaluation: {mode: "none"}`, a reduced sandbox tier, or an absent approval policy. The system MUST: (1) accept the declaration; (2) bake it into `D_H` (an absent guardrail is behavior-affecting identity); (3) mark every resulting trajectory `attributable_for_promotion: false`; and (4) proceed cleanly. What the system MUST NEVER do, under any declaration: accept an unsigned verdict, allow a privileged event from a writer without authority, or let a `none`-declared run silently acquire an evaluator mid-run (frozen compositions are immutable — freeze-at-compose).

**Rationale.** This distinguishes the two separable properties the SOTA confuses: *flexibility of declaration* (wanted, needed for Pack #2 and compute-only packs) versus *forgeability of evidence* (categorically refused). "Universal substrate" must not mean "weak trust spine." The trajectory marking preserves measurement integrity: unattributable rows never enter the DPO harvest or the McNemar promotion protocol.

**Falsifier (bound).** `test/trust/test_absent_vs_forged.py::test_absent_evaluator_marks_unattributable` and `::test_unsigned_verdict_still_illegal` — an unsigned verdict inside a `none`-declared composition MUST be rejected at the gateway, exactly as it is today.

### 2.4 T-4 · The hollow trajectory — NOVA-1, immediately

**State [VERIFIED].** `trajectory.py` assembles per-turn records with `dict(_ZERO_COST)` at line 53 and the episode total at line 75. F-12 as currently written asserts only schema validity — a content-free record passes. Invariant I-9 says a digest over `{ids, n}` is *not* a trajectory; the falsifier passes while the invariant fails. Dependencies blocked: cost-aware policy learning, escalation calibration (`P(pass | action, context)`, SPEC §5.3), router experiments, the DPO harvest (SPEC §7), skill synthesis (§5.4), all of M-10.

**Ruling (R-3).** Execute NOVA-1 **in Wave 2, now**. This resolves the live contradiction D-C: `sprint_active.md`'s Wave-1 carry-out table sends cost to Wave 4 ("real per-turn cost needs the governor's settled ledger") while `004`, `005` §W8, both `proposal_hy3_*` documents, and the GLM beta review all call it the single highest-leverage fix available. The contradiction resolves in favor of NOW because: the governor's *reservation* ledger is available per-turn even where the *settled* figure arrives at commit; and where a turn genuinely has no model cost (pure-effect turns), the row must carry **explicit zeros with a fingerprint of `none`**, not implicit zeros that are indistinguishable from "not measured." Trajectories cannot be back-filled — the settled cost ledger of a past run is gone.

**Falsifier (bound, F-12 hardened).** F-12 assertions strengthened to content assertions: every turn has a non-negative cost vector with at least one non-zero component across the episode OR an explicit `unmetered: true` marker; `turns` non-empty for non-trivial episodes; `model_fingerprint` present per model-involving turn; verdict embedded-or-explicitly-null.

### 2.5 T-5 · Layer-0 absorption timeline

**State [VERIFIED].** `layer0/` holds only `compose/compiler.py`, `registry/{lifecycle,broker,isolation,sandbox,validator,grants,worker}.py`, `events/{emitter,envelope,store,taxonomy}.py`. The two headline forensic defects (fabricated `"pass"`, fail-open ceiling) died with `layer0/kernel`, `scheduler`, `spi` at 2.2-B. Zero `layer0` imports remain under `vanguard/`. But: registry and compose are the **only** plugin-lifecycle code in the tree and have **never run on the canonical path** (review `005` §W7).

**Ruling (R-7).** Absorb at 3.1 under the **NOVA-4 negative-test suite** (ADR-0081): unknown-ref-fails-at-compose; empty-ceiling-denies; registry-exclusive-write; faulted-cell-cannot-stay-active; `in_process`-requires-explicit-grant; frozen-composition-immutable. Deletion of `layer0/` then proceeds behind SPEC §1's behavioral parity gate. Option B (delete now, rewrite in packages) is REJECTED — it violates SPEC §1 and converts Wave 3 from "absorb + prove" to "write + prove."

**Falsifier (bound).** The six NOVA-4 negatives as first-class tests in `test/registry/`, plus `test/layer0` deleted only when its assertions are re-homed verbatim.

### 2.6 T-6 · The loop as mechanism — publish the claim with its falsifier

**Ruling (R-8).** The turn loop stays **mechanism, never plugin**. Competing harnesses make the loop itself a plugin — coherent for them only because they have no authority boundary to preserve. AETHER publishes the Universal Turn Loop as a *mechanism claim with a bound falsifier* (ADR-0082):

> **Falsifier F-LOOP:** *Name an agentic algorithm that cannot be expressed as spawn-topology + planner policy over this loop.* Any such algorithm, demonstrated, is genuine ADR-0070 reversal evidence and triggers a Director review to amend the loop. Absent one, the question is closed and does not get relitigated quarterly.

**Rationale.** An unfalsified-but-published claim is science; an unpublishable claim is metaphysics, and ADR-M0-10 forbids metaphysics in normative documents. The falsifier is cheap (it is a standing invitation, not a test to run) and it terminates a recurring argument at zero engineering cost.

### 2.7 T-7 · `K ≪ N` — asserted, never tested (NOVA-2)

**State.** `002` register §5 claims many logical agents share a bounded worker pool. Nothing in the tree demonstrates logical-agent/worker separation: `EpisodeEngine` *is* the scheduler shell and `HarnessSession` holds live per-run state. F-02 (cold replay) proves grants, budgets, approvals and episode FSM survive a cold fold — most of the answer.

**Ruling (R-9).** Land **NOVA-2 before M-3 closes**: suspend an episode mid-turn → cold-reconstruct from the SQLite WAL in a **fresh process** → resume → complete. Green ⇒ the concurrency future (M-7) is a scheduling refactor and I-11 can be lifted on measurement alone. Red ⇒ hidden in-process coupling exists, and we want to know now, not at M-7. Review `005` calls this "the highest-value cheap test not currently on the board."

**Falsifier (bound).** `test/runtime/test_nova2_cold_resume.py` — a subprocess-isolated harness that (i) runs an episode to turn *k* and receives SIGTERM-mid-turn, (ii) starts a fresh Python process, folds the WAL, reconstructs engine/session state, (iii) resumes and completes, (iv) asserts the completed episode's trajectory and ledger hash-chain are indistinguishable from an uninterrupted control run under the same seed.

### 2.8 T-8 · Governance mass vs. capability (documentation collapse)

**State.** ~3.4k lines of normative and planning prose across seven authority tiers — currently larger than the substrate work it governs. The deferred/refusal list is maintained in four places (SPEC §9, ADR-0073, `002` §2, `milestones.md`); ADR-0076 exists solely to adjudicate which of two live artifacts is canonical.

**Ruling (R-11).** Collapse to the Clean Triad (SPEC + append-only ADR log + one living board) **post-M-4**, as `sprint_active` 5.1-A/B/C already schedules. Target: a senior developer is productive from three documents, not seven. Pre-M-4, the only allowed documentation work is the §7 update cascade of this proposal (which *reduces* mass: DELETE.md, duplicate synthesis docs).

### 2.9 T-9 · The five-SPI freeze

**Ruling.** The freeze stands (ADR-M0-03); its caveat is recorded: "a sixth SPI requires a design review" must not harden into "there are five SPIs forever." Scheduled for revisit at M-9 (`9.2-B`, TECH-LEAD) once a mature component graph exists. No action before then.

---

## 3. Drafted Append-Only ADR Catalog (ADR-0077 … ADR-0082)

> **Note on process.** These are **drafts proposed for adoption** by the Leadership 7. Per ADR-0000 they are append-only, numbered, and each states its own falsifier. None silently edits `0069`–`0076`; each that narrows or extends a prior ADR cites it explicitly, exactly as `0076` did. Adoption happens through the normal Director review; until then this section is advisory text inside an advisory document.

### 3.1 ADR-0077 — The manifest is a named component graph, not fixed slots

**Status:** PROPOSED. **Extends:** ADR-0059 (polyglot plugin/port decoupling), ADR-0072 (plugin boundary, wire-first), ADR-0073 (v0.6.0 lock vs defer). **Wave:** 3 (3.1-B). **Decision owner:** Engineering Director (scope call made in this review, §2.1).

**Context.** `mhf.harness/1` fixes five composition keys (`planner`, `context`, `memory`, `evaluation`, `toolkits`). This shape describes Pack #1, not the substrate. Algorithms requiring N planners, N evaluators, or declared wiring between components (debate, critic/revisor loops, tree search, evolutionary search, swarms) cannot be named in the manifest even though the runtime primitives (spawn topology + policy) can express them. `D_H` is computed over the manifest shape; late migration re-attributes every pack and every corpus row. Reviews `004` §2 and `005` §W1/§3.1-B both require this change at Wave 3.

**Decision.**

1. The composition schema moves from `mhf.harness/1` to **`mhf.manifest/2`** (normative JSON Schema 2020-12 draft in §6.1). Composition is a **named component graph**: an unordered map of named component declarations (each: `role`, `ref`, `config`) plus an explicit **binding section** describing wiring between named components.
2. The five slot names are **removed from the schema** and survive as a *pack convention*: `code-default` names its single planner `main`, its context `default`, etc. Nothing in `runtime/`, `kernel/`, or `agency/` may branch on slot names.
3. A component's `role` MUST be one of the registered SPI roles. An unknown `role` or an unresolvable `ref` fails **at compose**, never at runtime.
4. **`D_H` covers the graph.** `D_H = JCS-digest(resolved graph)` where the resolved graph includes every node (name, ref, config digest), every binding edge, the ceiling, the system prompt digest, the approval policy, and the model routes. Two compositions differing only in wiring yield different `D_H`.
5. Compositions freeze at compose (ADR-0005 unchanged). Migration of `code-default` is mechanical and ships in the same wave.
6. Model/sandbox remain first-party ports (P1-11/12 stay DEFERRED); the graph names *components*, not processes.

**Consequences.** Debate = two planner nodes + an aggregator policy; critic loop = planner + evaluation node wired cyclically with a turn-bounded policy; tree search = planner + spawn grant (post-M-6); swarm = N heterogeneous nodes over one Project ledger. None requires an engine change — which is the point. Cost: one schema revision, one compose-v2, one mechanical pack migration, all pre-M-4.

**Falsifier (1-to-1, bound).**
- `test/registry/test_compose_v2_graph.py::test_dh_distinguishes_wiring` — same node set, different binding edges ⇒ different `D_H`.
- `::test_unknown_role_fails_at_compose` — `{role: "oracle"}` (not an SPI role) fails at compose with a typed error.
- `::test_slot_names_not_schema_special` — a manifest with a planner named `proposer` and a second named `opponent` composes; the loader never reads the key `planner`.
- `test/packs/code_default/test_migration_parity.py::test_dh_migration_recorded` — the migrated pack's `D_H` changes exactly once, and the old↔new mapping is recorded as a composition supersession event in the ledger.

### 3.2 ADR-0078 — Guardrails are declarable-absent, never forgeable

**Status:** PROPOSED. **Extends:** ADR-0004 (verifier immutable & unreachable), ADR-0030 (passing verdict licenses memory write), ADR-0071 (identity trinity). **Wave:** 3.

**Context.** Guardrail presence is currently structural: an evaluator, sandbox tier, and approval policy are assumed composed. A research or math composition should not require a UID-10002 daemon; "universal substrate" must not weaken trust. Review `005` §3.4, decision register row 7; briefing `006` §2.3 derives the same rule from the separability thesis ("switching off is permitted, forging never is").

**Decision.**

1. A composition MAY declare any guardrail absent: `evaluation: {mode: "none"}`, `sandbox: {tier: "none"}`, `approval: {mode: "none"}`.
2. The system MUST accept the declaration, bake it into `D_H` (absence is behavior-affecting identity), and mark every resulting trajectory **`attributable_for_promotion: false`**.
3. The system MUST NOT, under ANY declaration: accept an unsigned verdict as legitimate; emit a privileged event from a writer without authority for that kind; or mutate a frozen composition mid-run to add a guardrail (an absent guardrail cannot silently reappear).
4. `attributable_for_promotion: false` trajectories are excluded from the DPO harvest (SPEC §7), the McNemar promotion protocol (MEASUREMENT.md), and skill-card selection. They remain fully auditable state.
5. A verdict that IS present must satisfy every existing binding rule (request-bound, nonce-bound, Ed25519-signed, gateway-written). The Absent-vs-Forged rule changes nothing about what a *valid* verdict is.

**Consequences.** Non-coding and compute-only packs compose without dragging an evaluator daemon; the trust spine is untouched; measurement integrity is preserved by exclusion, not by blocking execution.

**Falsifier (1-to-1, bound).**
- `test/trust/test_absent_vs_forged.py::test_absent_evaluator_marks_unattributable` — a `none`-declared run completes; its trajectory carries `attributable_for_promotion: false`; the DPO harvester rejects it.
- `::test_unsigned_verdict_still_illegal` — an unsigned verdict payload injected into a `none`-declared composition is rejected at the gateway (fail-closed).
- `::test_absence_baked_into_dh` — manifests differing only in `evaluation.mode` yield different `D_H`.
- `::test_frozen_composition_cannot_gain_evaluator` — post-compose manifest mutation adding an evaluator is rejected.

### 3.3 ADR-0079 — Trajectory truth density: the corpus must be learnable (NOVA-1)

**Status:** PROPOSED. **Extends:** ADR-0071 (identity trinity), ADR-0074 (proof budget). **Wave:** 2 (immediate). **Reverses the Wave-4 deferral** recorded in `sprint_active.md`'s Wave-1 carry-out table — that deferral is the one live board/register contradiction (audit finding D-C) and is resolved here.

**Context.** `runtime/trajectory.py` emits `dict(_ZERO_COST)` per turn (line 53) and per episode (line 75). F-12 asserts schema validity only; a content-free record passes. Every Layer-3 consumer (cost-aware routing, escalation calibration, DPO harvest, skill synthesis, Elo dynamics) is undefined without per-turn cost, model fingerprint, and verdict. Trajectories cannot be back-filled.

**Decision.**

1. `mhf.trajectory/1` (schema id unchanged; field requirements strengthened) MUST carry per turn: `cost: {usd_micros, tokens, bytes, millis}` measured from the governor's per-turn reservation and settled at commit; `model_fingerprint` (JCS digest of provider+model+params actually serving the turn; the literal string `"none"` for pure-effect turns); `latency_millis`; and the receipts already present.
2. Episode-level `cost` is the sum over turns; `verdict` remains signed-or-explicitly-`null` (embedded binding + signature, or `null` when `evaluation.mode: "none"` — in which case `attributable_for_promotion: false` per ADR-0078).
3. Turns with genuinely no metered consumption carry explicit zeros **plus** `model_fingerprint: "none"` — implicit and unmeasured must never be indistinguishable.
4. F-12 moves from schema-validity to **content assertions** (below). NOVA-5 (Wave 4 E2E confirmation) remains as the final check on a real run.

**Falsifier (1-to-1, bound, F-12 hardened — executes in Wave 2).**
- `test/falsifiers/test_falsifiers.py` (F-12): `test_trajectory_nonzero_cost_or_explicit_none` — for every non-trivial completed episode: `turns` non-empty; every turn has a 4-component non-negative cost vector; at least one turn has a non-zero component OR all turns carry `model_fingerprint: "none"`; `model_fingerprint` present on every turn; `verdict` is a signed object or literal `null`.
- `test/runtime/test_trajectory_metering.py::test_reservation_settles_into_turn_cost` — a turn whose model call reserves `R` and commits actual `a` records `cost = a` (overruns included, K-07).
- `::test_fingerprint_none_for_effect_only_turn` — a pure-effect turn records zeros + `"none"`.

### 3.4 ADR-0080 — `agent.spawn` as a capability-mediated kernel verb (design record; implementation deferred to M-6)

**Status:** PROPOSED (design record). **Extends:** ADR-0070 (recursive substrate: spawn/swarm as policy), ADR-0011 (capabilities carry resources), ADR-0012 (attenuation denies, never negotiates). **Design lands Wave 3; code lands M-6, post-M-4. No kernel change before Wave 4 closes.**

**Context.** Today only `EpisodeEngine.spawn()` (`agency/episode/engine.py:531`) can delegate; planners receive `plan/observe/reflect`. Any algorithm whose shape *is* a spawn topology must live inside the engine — ADR-0070's own reversal condition. All advisory reviews converge on: design now, decide at M-3, implement post-M-4.

**Decision (the design).** `agent.spawn` becomes an ordinary mediated effect through the existing 13 stages — no new stage, no new authority path:

| Stage | Behavior for `EffectRequest(action="agent.spawn")` |
|---|---|
| S1 PARSE | Standard contract validation; `args` MUST contain `child_manifest_ref` (or inline sub-graph), `child_budget` (additive + structural), `child_capabilities` (requested subset). |
| S2 RESOLVE | Resolves to the runtime's principal-spawner adapter (the same code path the engine uses today, externalized). |
| S3 DESCRIBE | Descriptor = digest(canonical(action, child graph digest, budget, capabilities)). |
| S4 CLASSIFY | `widens_capability := true` unless an explicit spawn grant covers the requested child subset — a spawn is widening by default and must be positively authorized. |
| S5 AUTHORIZE | Fail-closed: no grant ⇒ `AuthorizationDenied`; the child's requested capabilities MUST be a subset of the caller's effective capabilities (else deny, never attenuate-and-continue — ADR-0012). |
| S6 GRANT | Issue child grant bound to the child descriptor; `Capabilities(child) ⊆ Capabilities(parent)`; sibling depths not summed. |
| S7 RESERVE | Child lease reserved **against the parent lease**: `R_child ≤ R_parent_remaining` on every additive dimension; structural `{depth: parent+1, turns}`; `depth` beyond the ceiling denies. |
| S8/S8a | Grant verification + durable `ChildSpawned` intent before any child process exists (K-47). |
| S9 DISPATCH | Child principal constructed (same `Principal` type, `parent_id` set); child episode engine started; child writes to the **same Project ledger** with lineage by construction. |
| S10 COMMIT | Child budget debits parent; overruns included. |
| S11 RELEASE | Child lease released on every path. |
| S12 EMIT | `ChildSpawned` event with receipt `{request_digest, grant_digest, lease_id, child_principal_id, parent_episode_id}`; provenance DAG gains the parent→child edge. |

**Invariants preserved:** monotonic attenuation (I-3), typed budget algebra, single writer, provenance DAG completeness, sequential execution (I-11) — the child runs as a scheduled logical agent, not a thread.

**Falsifier (bound; executed at M-6 entry).** The five cases in §2.2, plus `test/trust/test_spawn_is_denied_not_attenuated` — a spawn requesting capabilities ⊄ parent denies at S5 rather than spawning a clipped child.

### 3.5 ADR-0081 — Final absorption of `layer0/` registry and compose, with the NOVA-4 negative suite

**Status:** PROPOSED. **Extends:** ADR-0069 (runtime convergence), ADR-0076 (foundation execution decisions). **Wave:** 3 (3.1). 

**Context.** `layer0/` retains only `compose/`, `registry/`, `events/`. Registry and compose are the only plugin-lifecycle code in the tree and have never run on the canonical path (review `005` §W7 — the extensibility thesis is unproven until they do). SPEC §1 forbids deleting duplicate kernels/schedulers/mocks/synthetic verdict paths before a behavioral parity gate.

**Decision.**

1. `layer0/registry/{lifecycle,broker,isolation,sandbox,validator,grants,worker}.py` are absorbed into `vanguard/packages/runtime/registry/` (runtime layer; adapters may implement cells but never import kernel/agency — boundary flow unchanged).
2. `layer0/compose/compiler.py` is superseded by **compose-v2** (ADR-0077): the graph compiler is written fresh against `mhf.manifest/2`, inheriting the fork's validated semantics (freeze-at-compose, ceiling compilation, `D_H` shape) but not its slot-based API.
3. `layer0/events/*` is absorbed into the existing runtime ledger path (`ledger_emitter.py`, `session.py`), completing the single-writer convergence.
4. Absorption ships **behind the NOVA-4 negative-test suite** (six negatives of §2.5) as first-class falsifiers, plus a walking-skeleton echo plugin lifecycle on the wire (ADR-M0-13).
5. `layer0/` is then deleted behind SPEC §1's behavioral parity gate: for each absorbed module, the re-homed tests pass on the canonical path and the fork's tests are deleted verbatim — the same procedure that killed `layer0/kernel` at 2.2-B. `test/layer0/` and `test/registry/` collapse into `test/runtime/registry/`.
6. `_PROC_PATTERN` is read from the compiled ceiling, never restated (decision register row 5).

**Falsifier (1-to-1, bound).** NOVA-4, as six named negatives in `test/runtime/registry/test_nova4_negatives.py`: `test_unknown_ref_fails_at_compose`; `test_empty_ceiling_denies_all`; `test_registry_exclusive_write`; `test_faulted_cell_cannot_stay_active`; `test_in_process_requires_explicit_grant`; `test_frozen_composition_immutable`. Plus `test_layer0_deleted` — a repo-lint asserting no `layer0/` directory and no `layer0` imports anywhere under `vanguard/` or `test/` (extends `check_boundaries.py`).

### 3.6 ADR-0082 — The Universal Turn Loop is a mechanism claim with a bound falsifier; documentation collapses post-M-4

**Status:** PROPOSED. **Extends:** ADR-0003 (agent loop primary, no runtime workflow graph), ADR-M0-10 (no metaphysics), ADR-0070. **Wave:** 3 (publication), M-5+ (collapse).

**Context.** Whether the single turn loop should remain fixed mechanism or become a plugin is relitigated periodically. Competing harnesses plugin-ize the loop because they have no authority boundary to preserve; AETHER cannot, because the loop is where every proposal passes the reference monitor. Review `005` §W3 asks the claim be published with a falsifier rather than asserted. Separately, governance mass (~3.4k lines over seven tiers) exceeds the work it governs; the collapse target and timing are agreed (post-M-4) but not yet recorded as a decision.

**Decision.**

1. The turn loop (observe → propose → mediate S0–S12 → receipt → reflect) is **mechanism, not plugin**. Any agentic algorithm is claimed expressible as **spawn-topology + planner policy over this loop**.
2. This claim is published with **bound falsifier F-LOOP**: *"Name an agentic algorithm that cannot be expressed as spawn-topology + planner policy over this loop."* A demonstrated counter-example is ADR-0070 reversal evidence and triggers a Director review to amend the loop. No counter-example within 12 months of publication closes the question.
3. **Documentation collapse is scheduled post-M-4** (M-5 deliverable): the corpus collapses to the Clean Triad — SPEC + append-only ADR log + one living board (`sprint_active.md`). The deferred/refusal list survives in exactly one place (SPEC §9). Review/advisory documents are archived to git history, not maintained as live tiers. Exit test: a senior developer reaches productivity from three documents.
4. The claim in (1) is normative *engineering law* (what we build), not cognitive-science metaphysics; ADR-M0-10 applies to its phrasing.

**Falsifier (1-to-1, bound).**
- F-LOOP as above (a standing falsifier, not a test).
- `test/docs/test_triad_collapse.py` (M-5): asserts the four-place deferred/refusal duplication is reduced to one (grep count of the refusal-list heading across `docs/` equals 1); asserts no live wave-plan files exist outside the single board; asserts `docs/07_reviews/` contains only archive pointers.

---

## 4. Phased Milestone Roadmap & Version Ladder (v0.6.1 → v1.0.0)

### 4.1 Version ladder (binding summary)

| Version | Name | Milestones | Theme | Exit evidence |
|---|---|---|---|---|
| **v0.6.1** | Substrate Correction Lock | M-2 close | NOVA-1 (truth-dense corpus), NOVA-2 (cold suspend/resume), `root.py` split completion, single-algebra/single-writer convergence; ADR-0077…0082 adopted as law | F-16 green; F-12 content assertions green; NOVA-2 green; zero `layer0` imports under `vanguard/` |
| **v0.6.2** | Extensibility & Plugin Walking Skeleton | M-3 | compose-v2 graph manifest; registry absorbed (ADR-0081) + NOVA-4; echo-plugin lifecycle on the wire; `layer0/` deleted; F-LOOP published | ADR-M0-13 echo lifecycle green; six NOVA-4 negatives green; `layer0/` absent from tree |
| **v0.6.3** | Foundation E2E — **STOP LINE** | M-4 | One real, uncheated coding-agent run on `packs/code-default/` + `vg`; NOVA-5 trajectory confirmation | **9-row integration verification** (below), zero human intervention |
| **v0.7.0** | Generality & Mediated Delegation | M-5, M-6 | Pack #2 (Math & Formal Deductive Verification) with zero core diffs; documentation collapse; `agent.spawn` verb live | I-7 gate (zero diffs under `domain/`+`kernel/`, trajectory parity); spawn falsifiers of §3.4 green |
| **v0.8.0** | Topology Builder & Concurrency | M-7, M-8 | Independence groups, async scheduling (K ≪ N measured); debate/critic/tree-search reference compositions, multi-pack side-by-side with zero core diffs | M-7 measurement gate (selector disjointness, zero event loss under backpressure); M-8 gate (three packs, one runtime, zero engine changes) |
| **v0.9.0** | Scaled Orchestration | M-9 | Load tests over bounded worker pool; IPC/serialization/ledger-pressure measurement; SPI-freeze revisit; external benchmark of `code-default` with telemetry; System-1 latency hypotheses measured | Performance gates satisfied; benchmark report with cost/latency telemetry |
| **v1.0.0** | Meta-Cognitive Substrate | M-10 | Active-inference harness tuning over the corpus; skill synthesis with Elo-decayed eviction; unforgeable DPO harvest; McNemar promotion frontier; the self-improvement loop closed | The system proposes, verifies, and promotes an improved composition; full chain attributable `D_H`/`D_R`/`D_X` end-to-end |

### 4.2 Milestone definitions, entry/exit gates, and scope boundaries

**M-0 / M-1 (COMPLETE — recorded for continuity).** Engineering truth (living CI on `vanguard/packages/`, F-01…F-21 registered) and the trust spine (F-01…F-15 green; TCB ≤ 1438 LOC, currently 1365). No changes proposed.

**M-2 · One runtime (v0.6.1) — IN FLIGHT.** *Entry:* already entered. *Scope:* NOVA-1 per ADR-0079 (this review moves it from Wave 4 to now, resolving board contradiction D-C); NOVA-2 per §2.7; complete the `root.py` in-place split; finish reducer fold rules; delete remaining duplicate surfaces. *Exit gate:* F-16 green; F-12 content assertions green; NOVA-2 green; zero `layer0` imports under `vanguard/`. *Out of scope:* any manifest work (Wave 3), any kernel growth except tests.

**M-3 · Extensibility (v0.6.2).** *Entry:* M-2 exit + Director scope call on compose-v2 (made in this review, §2.1). *Scope:* ADR-0077 graph manifest + compose-v2; ADR-0078 guardrail declarations; ADR-0080 design record published; ADR-0081 registry absorption + NOVA-4 + echo-plugin walking skeleton; `layer0/` deletion behind the parity gate; F-LOOP published (ADR-0082). *Exit gate:* all falsifiers of §3.1/3.2/3.5 green; F-18 domain-blindness green; `layer0/` absent. *Out of scope:* `agent.spawn` implementation; concurrency enablement; Pack #2.

**M-4 · Foundation E2E (v0.6.3) — THE STOP LINE.** *Entry:* M-1 + M-2 + M-3. *Scope:* exactly one real coding-agent run through the complete substrate — real model route, real effects, bwrap sandbox, signed exterior evaluation, WAL persistence, cold replay — with **zero human intervention** ("no human cheating": no hand-edited workspace, no manual verdict, no silently patched state). *Exit gate — the 9 rows:*

| # | Row | Evidence |
|---|---|---|
| 1 | Real model invocation | Model-route receipt with non-zero cost + fingerprint (NOVA-1 live) |
| 2 | Real effect execution | `proc.exec`/`patch.apply` receipts from the UID-10001 sandbox |
| 3 | Containment | Sandbox perimeter held (K-34…K-41); no capability outside the ceiling |
| 4 | Signed evaluation | Exterior UID-10002 verdict, Ed25519 over JCS bytes, nonce-bound |
| 5 | Durable state | SQLite WAL, FULL sync, per-Project hash chain intact end-to-end |
| 6 | Cold replay | Fresh process folds the ledger to the identical effective state (I-4) |
| 7 | Trajectory truth | `mhf.trajectory/1` with per-turn cost, fingerprint, verdict (NOVA-5) |
| 8 | Attribution | `D_H`/`D_R`/`D_X` distinct and complete for the run |
| 9 | Zero human intervention | Full event stream contains no operator-mediated repair |

*Stop-line rule:* no M-5+ work of any kind begins until all nine rows are green on one uninterrupted run. If the run fails, the failure is registered and the run repeated — the stop line is not satisfied by partial credit across multiple runs.

**M-5 · Generality proof & consolidation (v0.7.0, part 1).** *Entry:* M-4 green. *Scope:* **Pack #2 = Math & Formal Deductive Verification** (below); documentation collapse to the Clean Triad (ADR-0082 §3); NOVA-2's scalability confirmation. *Exit gate:* I-7 verified — zero diffs under `domain/` and `kernel/` for the entire pack; trajectory-parity assertion (Pack #2 emits the same rich `mhf.trajectory/1` rows: cost, fingerprint, verdict-or-null); triad-collapse test green. *Why Math:* it is maximally distant from coding in tools (CAS, proof checkers such as Lean/Isabelle adapters, LaTeX artifacts), maximally close in verifiability (a proof checker is a natural exterior oracle — the separability thesis still applies), and it exercises Absent-vs-Forged in both directions (formal packs may declare `evaluation: none` for exploration, `proof-checker` for verification).

**M-6 · Mediated delegation (v0.7.0, part 2).** *Entry:* M-5. *Scope:* implement ADR-0080 in the kernel (TCB budget headroom: 1438 − 1365 = 73 logical LOC must cover the spawn classification and reservation delta — the design in §3.4 is deliberately dispatch-table-shaped to fit; if it does not fit, the overflow goes to runtime pre-classification, never to a kernel growth beyond budget). *Exit gate:* all six spawn falsifiers green; planners without a spawn grant cannot delegate; every spawn is a ledgered, budgeted, attributed effect.

**M-7 · Controlled concurrency (v0.8.0, part 1).** *Entry:* M-5 + M-6. *Scope:* activate independence groups for non-conflicting selectors; async scheduling with the K ≪ N logical-to-worker separation; backpressure on the single writer. *Exit gate:* measurement gate on selector disjointness; zero event loss under backpressure; cold-resume scalability (NOVA-2 generalized to N suspended episodes); I-11 lifted **on measurement alone**. *Out of scope:* any change to the sequential semantics of a single episode.

**M-8 · Framework-builder abstraction (v0.8.0, part 2).** *Entry:* M-6 + M-7. *Scope:* reference validation compositions — Debate (two planner nodes + aggregator), Critic/Revisor (cyclic planner+evaluation wiring), Tree Search (planner + spawn grant + bounded branching), Evolutionary Search (mutation over JCS-differentiable manifest fields, paired runs as selection) — each composed **declaratively via the named component graph with zero engine modifications**; multi-pack side-by-side (code-default + Pack #2 + a third); declarative composition SDK/CLI + dry-run compose validator + builder's guide. *Exit gate:* three packs on one runtime with zero core diffs; all reference topologies run without engine changes.

**M-9 · Scaled orchestration (v0.9.0).** *Entry:* M-7 + M-8. *Scope:* load tests (many logical agents over a bounded worker pool); measure IPC, serialization, plugin-call, and ledger pressure; optimize only where measurement points; revisit the five-SPI freeze (9.2-B, TECH-LEAD); external benchmark run of `code-default` with cost/latency telemetry; measure the System-1 `<100ms` and tier-cost claims (stated as named hypotheses until here — the k3 risk register's R-5: latency claims must not degrade into marketing). *Exit gate:* performance gates satisfied on measured numbers.

**M-10 · Meta-cognitive substrate (v1.0.0).** *Entry:* M-8 + M-9. *Scope:* the exterior meta-cognition plugin consuming the now-trustworthy corpus — backward error attribution, active-inference config mutation (§5.1), Elo-decayed skill synthesis (§5.3), DPO harvest (§5.4), McNemar promotion (§5.5), the signed promotion frontier, the continuous outer loop. *Exit gate:* the system proposes, verifies (exterior oracle), and promotes (McNemar + signed pointer swap) an improved composition of itself; every step attributable via `D_H`/`D_R`/`D_X` from first to last.

### 4.3 Standing constraints across all milestones

- **Sequential execution (I-11)** until the M-7 measurement gate fires.
- **TCB ≤ 1438 LOC** enforced by linter every commit; kernel growth requires headroom accounting (M-6 notes the 73-LOC headroom explicitly).
- **Domain blindness (I-7)** enforced by `check_domain_blindness.py`; Pack #2 is the first gate that proves it rather than assumes it.
- **Single execution board:** all live task-level execution in `sprint_active.md`; this proposal does not create a second board — §7.3 gives the merge directives.
- **Refusals hold** (SPEC §9): no third tree, no Rust TCB rewrite, no swarm/DAG/graph-DB engine, no vector DB as core, no evaluator-as-plugin, no mid-run hot-swap, no "no privileged core" flatness, no metaphysics in normative docs, no benchmark scores as evidence without separability.

---

## 5. Theories, Algorithms & Mathematical Formulations

> These formulations are the mathematical basis of the M-10 layer and of the calibration clauses in SPEC §5.3. They are stated here in full so that implementation never has to guess. Per ADR-M0-10, they are engineering objectives, not ontology claims.

### 5.1 Active Inference formulation — VFE minimization over the 6D economic tensor

Harness configuration is a parameter vector $\theta \in \Theta$ over the declarative manifest fields — $\theta = \{\text{tokens}, \text{turns}, \text{model\_tier}, \text{repair\_rounds}, \ldots\}$ — and the 6D economic reservation tensor is $\mathbf{R} = (R_{\text{usd}}, R_{\text{tokens}}, R_{\text{bytes}}, R_{\text{millis}}; R_{\text{depth}}, R_{\text{turns}})$, the first four additive, the last two structural (sibling depths never summed). Tuning is the bounded optimization:

$$\theta^* = \arg\min_{\theta \in \Theta} \mathcal{F}(\theta) \quad \text{subject to} \quad \text{Cost}(\theta) \le \mathbf{R}_{\max}$$

with the Variational Free Energy objective decomposing into epistemic and pragmatic terms plus the economic penalty:

$$\mathcal{F}(\theta) = \underbrace{D_{\mathrm{KL}}\big[q(\phi \mid \tau) \,\|\, p(\phi)\big]}_{\text{epistemic: uncertainty reduction}} \;-\; \underbrace{\mathbb{E}_{q(\phi \mid \tau)}\big[\ln p(Y = 1 \mid \tau, \theta)\big]}_{\text{pragmatic: success likelihood}} \;+\; \lambda \sum_{d \in \{\$, t, k\}} \frac{R_d(\theta)}{R_{\max,d}}$$

where $\tau$ is the observed trajectory corpus, $q(\phi \mid \tau)$ the posterior over task-latent structure $\phi$, and $Y(\tau) \in \{0,1\}$ the **exterior signed oracle verdict** — the only quantity in the objective the agent cannot influence. The expected-free-energy reading is direct: the epistemic term drives information gain (curiosity over unexplored task contexts), the pragmatic term drives exploitation; the 2025 curiosity-reward literature (Wan et al.) confirms the multi-turn benefit of exactly this decomposition.

**Discrete mutation transition rules** (gradient-free, over the declarative manifold):

1. Context overflow $E_{\text{OOM}}$: $\text{Tokens}_{\text{new}} = \min(\lceil \text{Tokens}_{\text{curr}} \times 1.5 \rceil, \mathbf{R}_{\text{tokens},\max})$
2. Repair oscillation $E_{\text{oscillation}}$: $\text{Strategy} \to \text{TreeSearch}$; $\text{RepairRounds}_{\text{new}} = \text{RepairRounds}_{\text{curr}} + 2$
3. Capability deficit $E_{\text{complexity}}$: $\text{Tier}_{\text{new}} = \min(\text{Tier}_{\text{curr}} + 1, \text{Tier}_{\max})$

Mutations act only on manifest fields (the JCS-differentiable surface), are proposed by the exterior meta-reflector plugin, and take effect only through the paired McNemar protocol (§5.5) — **the optimizer never writes the live harness directly.**

### 5.2 Trajectory error credit assignment and backward fault isolation

Let an episode trajectory of horizon $T$ be the immutable event ledger

$$\tau = \big((s_0, a_0, r_0), (s_1, a_1, r_1), \ldots, (s_T, a_T, r_T)\big)$$

with $s_t$ the environment context digest, $a_t$ the executed tool-action verb, $r_t$ the kernel effect receipt. The terminal outcome $Y(\tau) \in \{0,1\}$ is determined strictly by the exterior oracle. When $Y(\tau) = 0$, the **counterfactual causal contribution** of turn $t$ is defined by localized state perturbation:

$$\mathcal{C}(a_t) = \Delta\,\mathbb{E}_{\text{oracle}}\big[Y(\tau) \mid \mathrm{do}(a_t = a_{\text{null}})\big] + \lambda_{\text{cost}} \cdot \frac{\text{Tokens}(a_t)}{\sum_{k=0}^{T}\text{Tokens}(a_k)}$$

The practical gradient-free isolation algorithm (deterministic, replayable, no counterfactual rollouts required):

1. **Backward error scan** — traverse the ledger in reverse ($t = T \to 0$).
2. **First invariant violation** — locate the earliest turn $t^*$ where a compiler, test runner, or capability gate emitted a non-zero exit code or `AuthorizationDenied`.
3. **AST delta attribution** — if a syntax/semantic error is detected at $t^*$, attribute failure weight $W_f(t) = \gamma^{T-t}$ to the most recent `patch.apply` action preceding $t^*$ (exponential recency decay; $\gamma = 0.9$ default).
4. Failure-mode classification (taxonomy: `CONTEXT_WINDOW_OVERFLOW`, `TOOL_SCHEMA_VIOLATION`, `AUTHORIZATION_DENIED`, `TEST_ASSERTION_FAILURE`, `INFINITE_LOOP_TIMEOUT`, `BUDGET_EXHAUSTION`, `UNKNOWN_ANOMALY`) selects the mutation rule of §5.1.

Because the scan reads only the immutable ledger, attribution is **deterministic and independently re-runnable** — an auditor with the WAL reproduces the diagnosis exactly. This is what the 2026 trajectory-RL literature (Agentic ESOpt's trajectory-level attribution; EnvHarness's diagnosis-driven synthesis) approximates with expensive rollouts; AETHER gets it from event-sourcing by construction — provided the corpus is truth-dense (NOVA-1), which is why NOVA-1 precedes everything in this section.

### 5.3 Dense 384d hybrid semantic-lexical retrieval and Elo-decayed skill-card eviction

Each synthesized skill card is the tuple

$$S_i = \big(\mathbf{v}_i,\ \text{Pattern}_i,\ \text{Procedure}_i,\ E_i,\ t_{\text{created}},\ t_{\text{last\_used}}\big)$$

where $\mathbf{v}_i \in \mathbb{R}^{384}$ is the dense embedding (encoder: `all-MiniLM-L6-v2`, 384 dimensions — chosen for local, CPU-viable inference; the encoder is plugin-side, never core) over the error signature and context prompt.

**Hybrid retrieval score** for an incoming failure signature with embedding $\mathbf{q}$ and keyword set $K_q$:

$$\text{Score}(S_i, \mathbf{q}, K_q) = \alpha \cdot \frac{\mathbf{q} \cdot \mathbf{v}_i}{\lVert \mathbf{q} \rVert \, \lVert \mathbf{v}_i \rVert} + (1 - \alpha) \cdot \text{BM25}(K_q, \text{Pattern}_i) + \beta \cdot \sigma(E_i)$$

with $\sigma(E_i) = \big(1 + e^{-E_i/400}\big)^{-1}$ the Elo-normalized utility weight (the logistic's 400 scale makes a 400-point Elo gap ≈ 10:1 odds, per standard chess-Elo convention). Defaults: $\alpha = 0.6$, $\beta = 0.2$. The BM25 term prevents the semantic-collision and amnesia failure modes documented for pure-vector skill libraries (Voyager's known weaknesses); the Elo term makes retrieval trust-weighted by verified utility.

**Elo update dynamics** — when skill $S_i$ is retrieved and injected into an episode:

- Episode achieves oracle-green ($Y = 1$): $E_{t+1}(S_i) = E_t(S_i) + K\,\big(1 - \sigma(E_t(S_i) - \bar{E})\big)$
- Episode fails ($Y = 0$): $E_{t+1}(S_i) = E_t(S_i) - K\,\sigma(E_t(S_i) - \bar{E})$

with baseline $E_0 = 1200$ and pool mean $\bar{E}$. **Continuous-time decay (forgetting curve):** $E(t) = E_0 \cdot e^{-\lambda_{\text{decay}}(t - t_{\text{last\_used}})}$.

**Eviction criterion:** a card falls below $E_{\text{evict}} = 1000$ or remains unused for $\Delta t > 30$ days ⇒ evicted from the active cache to cold storage on disk. Skill cards enter the library **only** through the promotion pipeline (a green signed verdict crystallizes a candidate card; the McNemar gate admits it into any manifest), never by direct write — so procedural bloat is paid for in evidence, not tokens.

### 5.4 Unforgeable DPO preference harvesting

DPO (Rafailov et al., arXiv:2305.18290) optimizes a policy directly over preference pairs with the closed-form reward parameterization and classification-style loss

$$\mathcal{L}_{\text{DPO}}(\pi_\theta; \pi_{\text{ref}}) = -\mathbb{E}_{(x,\,y_w,\,y_l) \sim \mathcal{D}}\Big[\log \sigma\Big(\beta \log \frac{\pi_\theta(y_w \mid x)}{\pi_{\text{ref}}(y_w \mid x)} - \beta \log \frac{\pi_\theta(y_l \mid x)}{\pi_{\text{ref}}(y_l \mid x)}\Big)\Big]$$

requiring no explicit reward model — but it inherits whatever bias lives in $\mathcal{D}$. AETHER's contribution is that $\mathcal{D}$ is **unforgeable by construction**:

1. **Pairing key:** $(\text{task\_digest}, \text{harness\_digest}, \text{prefix})$ — pairs are formed between trajectories that share task, composition, and a common execution prefix, diverging only in the compared dimension. `D_H` equality is enforced by digest, not by label.
2. **Label source:** the chosen/rejected orientation is set solely by the **exterior Ed25519-signed verdict** ($Y = 1$ beats $Y = 0$; on ties, lower $\text{Cost}$ over the 4 additive dimensions wins). The agent under training can neither read, predict, nor write the label channel.
3. **Anti-cheat filter:** rows with `attributable_for_promotion: false` (ADR-0078) are excluded; verdict signature validity is re-verified at harvest time; prefix-parity is re-checked against the ledger fold.
4. **Regression:** fine-tuned tier-1/2 models are regression-tested by cassette replay in the lab before any promotion pointer moves.

This addresses DPO's documented failure modes where the preference signal is self-generated (reward hacking, out-of-distribution policy collapse): the label channel is structurally outside the agent's reach — the separability thesis operationalized as a training-set invariant.

### 5.5 Paired McNemar exact statistical promotion protocol

Every promotion decision — a mutated manifest, a new skill card, a fine-tuned model route — is a hypothesis test against the non-deletable baseline under Mill's Canon of Difference (MEASUREMENT.md is already law here). Given $N$ paired tasks evaluated under identical model weights, sampling temperature, and initial environment seed:

$$\chi^2 = \frac{\big(|n_{10} - n_{01}| - 1\big)^2}{n_{10} + n_{01}}$$

where $n_{10}$ = tasks where candidate B passed and baseline A failed; $n_{01}$ = tasks where A passed and B failed (continuity-corrected). For small discordant counts ($n_{10} + n_{01} < 25$), the **exact binomial** form is used instead of the χ² approximation:

$$p = 2 \sum_{i=0}^{\min(n_{10}, n_{01})} \binom{n_{10}+n_{01}}{i} \left(\tfrac{1}{2}\right)^{n_{10}+n_{01}}$$

**Promotion accepted iff:**
1. $\chi^2 \ge 3.841$ (α = 0.05, 1 dof) — or exact $p < 0.05$;
2. $n_{10} > n_{01}$ (directionality: positive net lift);
3. statistical power $(1 - \beta) \ge 0.80$ across at least $N = 50$ distinct held-out tasks;
4. the A/A floor is respected: an A/A run (candidate = baseline) must show no significant difference before any A/B is believed.

Promotion is a **signed event that swaps the registry's default pointer** — a partial order over a frontier (ADR-0015) that the system proposes but cannot itself drive: the promotion controller is exterior to the agents it judges, and every promotion is attributable through `D_H` (candidate) ≠ `D_H` (baseline) ≠ `D_R` ≠ `D_X`.

---

## 6. Zero-Guesswork Developer Implementation Bridge

### 6.1 Normative JSON Schema 2020-12 — `mhf.manifest/2` (draft)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aether.dev/schemas/mhf.manifest/2.schema.json",
  "title": "AETHER composition manifest (named component graph)",
  "type": "object",
  "required": ["api", "id", "components", "bindings", "model_routes",
               "capabilities", "budget"],
  "properties": {
    "api": { "const": "mhf.manifest/2" },
    "id": { "type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$" },
    "components": {
      "type": "object",
      "propertyNames": { "pattern": "^[a-z0-9][a-z0-9_-]*$" },
      "additionalProperties": {
        "type": "object",
        "required": ["role", "ref"],
        "properties": {
          "role": { "enum": ["planner", "context", "memory", "evaluation",
                             "toolkit"] },
          "ref": { "type": "string",
                   "pattern": "^mhf\\.[a-z0-9.-]+@\\^?[0-9]+" },
          "config": { "type": "object" }
        },
        "additionalProperties": false
      }
    },
    "bindings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from", "to"],
        "properties": {
          "from": { "type": "string" },
          "to": { "type": "string" },
          "channel": { "type": "string" }
        },
        "additionalProperties": false
      }
    },
    "model_routes": { "type": "array", "minItems": 1,
      "items": { "type": "object", "required": ["tier", "provider", "model"],
        "properties": { "tier": { "type": "integer", "minimum": 1 },
          "provider": { "enum": ["ollama", "openrouter", "cassette", "fake"] },
          "model": { "type": "string" },
          "escalate_on": { "type": "array", "items": { "type": "string" } } } } },
    "capabilities": { "type": "array", "items": {
      "type": "object", "required": ["verb", "selector"],
      "properties": { "verb": { "type": "string" },
        "selector": { "$ref": "#/$defs/selector" } } } },
    "budget": { "$ref": "#/$defs/budget6d" },
    "evaluation": { "enum": ["none"], "default": "signed" },
    "sandbox": { "type": "object",
      "properties": { "tier": { "enum": ["rootless", "none"] } } },
    "approval": { "type": "object",
      "properties": { "mode": { "enum": ["signed", "none"] } } },
    "system_prompt": { "type": "string" },
    "undeletable": { "type": "boolean", "default": false }
  },
  "$defs": {
    "selector": { "oneOf": [
      { "type": "object", "required": ["kind", "root", "paths"],
        "properties": { "kind": { "const": "fs" }, "root": { "type": "string" },
          "paths": { "type": "array", "items": { "type": "string" } } } },
      { "type": "object", "required": ["kind", "uriPattern"],
        "properties": { "kind": { "const": "generic" },
          "uriPattern": { "type": "string" } } } ] },
    "budget6d": { "type": "object",
      "required": ["usd_micros", "tokens", "bytes", "millis", "turns", "depth"],
      "properties": {
        "usd_micros": { "type": "integer", "minimum": 0 },
        "tokens":     { "type": "integer", "minimum": 0 },
        "bytes":      { "type": "integer", "minimum": 0 },
        "millis":     { "type": "integer", "minimum": 0 },
        "turns":      { "type": "integer", "minimum": 1 },
        "depth":      { "type": "integer", "minimum": 0 } } }
  }
}
```

Notes: `role.enum` lists the five SPI roles (the M-3 composition roles; the SPI set itself stays frozen per ADR-M0-03 until the M-9 revisit). Slot-shaped keys are absent by design — `components` is an open map. Vector pairs for this schema live under `schemas/v4/vectors/manifest/` (valid minimal graph; invalid: unknown role, unresolvable ref, missing bindings, 5-dimension budget).

### 6.2 Plugin Lifecycle Finite State Machine (complete table with ledger events)

The absorbed registry (ADR-0081) implements exactly this FSM on the canonical path. Every transition emits a ledger event; writer authority is the registry for lifecycle kinds (event-kind writer authority per ADR-0074).

| # | State | Entry action | Ledger event (writer: registry) | Guard / invariant |
|---|---|---|---|---|
| 0 | `Declared` | Manifest parsed against `mhf.manifest/2`; `ref` resolved | `ComponentDeclared {ref, role, name}` | Unknown role or unresolvable ref ⇒ terminal `Rejected` (fails at compose, never at runtime) |
| 1 | `Validated` | Schema + ceiling compilation; selector algebra parse | `ComponentValidated {ceiling_digest}` | Empty capability list compiles to a deny-all ceiling (fail-closed) |
| 2 | `Frozen` | Composition frozen; `D_H` computed over resolved graph | `CompositionFrozen {D_H}` | Post-freeze mutation of any input ⇒ `Rejected`; frozen compositions immutable |
| 3 | `Provisioned` | Cell allocated (in-process or UDS); grants compiled | `ComponentProvisioned {cell_id, grant_digests}` | `in_process` requires an explicit grant in the manifest (NOVA-4) |
| 4 | `Active` | Plugin serves the wire (JSON-RPC 2.0 / UDS; `in_process` still speaks the wire) | `ComponentActive {cell_id}` | Heartbeat liveness; capability ceiling enforced per call |
| 5 | `Degraded` | Heartbeat missed / wire error | `ComponentDegraded {reason}` | A faulted cell **cannot stay Active** (NOVA-4); effects fail closed while degraded |
| 6 | `Recovering` | Cell restart under the same grants and ceiling | `ComponentRecovering {attempt}` | Grant digests and `D_H` unchanged across restart |
| 7 | `Faulted` | Recovery budget exhausted | `ComponentFaulted {attempts}` | Terminal for the cell; run continues only if composition policy allows |
| 8 | `Suspended` | NOVA-2 suspend: state durable in WAL | `ComponentSuspended {checkpoint}` | Cold reconstruct in a fresh process resumes to `Active` with identical effective state |
| 9 | `Retired` | Composition ends; cell torn down | `ComponentRetired {cell_id}` | Leases released (S11 semantics) before `Retired` is emitted |
| 10 | `Rejected` | Any guard failure at 0–3 | `ComponentRejected {stage, reason}` | Terminal; never transitions to `Active` |

Transitions are strictly forward except `Active ↔ Degraded ↔ Recovering` and `Active → Suspended → Active` (cold resume). There is **no** `Retired → Provisioned` (no mid-run hot-swap — standing refusal). Registry is the exclusive writer of these kinds (NOVA-4).

### 6.3 The 1-to-1 executable falsifier matrix

Every requirement in this proposal maps to exactly one named test. If a requirement has no test, it is not a requirement.

| Requirement | ADR / ruling | Executable falsifier |
|---|---|---|
| Graph manifest composes; wiring changes `D_H` | 0077 / R-4 | `test/registry/test_compose_v2_graph.py::test_dh_distinguishes_wiring` |
| Unknown role fails at compose | 0077 | `test/registry/test_compose_v2_graph.py::test_unknown_role_fails_at_compose` |
| Slot names not schema-special | 0077 | `::test_slot_names_not_schema_special` |
| Migration recorded once | 0077 | `test/packs/code_default/test_migration_parity.py::test_dh_migration_recorded` |
| Absent evaluator ⇒ unattributable | 0078 / R-5 | `test/trust/test_absent_vs_forged.py::test_absent_evaluator_marks_unattributable` |
| Unsigned verdict illegal under `none` | 0078 | `::test_unsigned_verdict_still_illegal` |
| Absence baked into `D_H` | 0078 | `::test_absence_baked_into_dh` |
| Frozen composition cannot gain guardrail | 0078 | `::test_frozen_composition_cannot_gain_evaluator` |
| Per-turn cost non-zero or explicit-none | 0079 / R-3 (NOVA-1) | `test/falsifiers/test_falsifiers.py` F-12: `test_trajectory_nonzero_cost_or_explicit_none` |
| Reservation settles into turn cost | 0079 | `test/runtime/test_trajectory_metering.py::test_reservation_settles_into_turn_cost` |
| Fingerprint `none` for effect-only turns | 0079 | `::test_fingerprint_none_for_effect_only_turn` |
| Spawn denied without grant (S5) | 0080 / R-6 | `test/kernel/test_agent_spawn_verb.py::test_spawn_without_grant_denies` |
| Child caps ⊆ parent | 0080 | `::test_child_capabilities_subset` |
| Spawn debits parent budget (S7) | 0080 | `::test_child_reservation_debits_parent` |
| Provenance DAG parent edge | 0080 | `::test_spawn_in_provenance_dag` |
| Spawn receipt P1-9 fields | 0080 | `::test_spawn_receipt_fields` |
| Spawn denied-not-attenuated | 0080 | `test/trust/test_spawn_is_denied_not_attenuated` |
| Unknown ref fails at compose (registry) | 0081 / R-7 (NOVA-4) | `test/runtime/registry/test_nova4_negatives.py::test_unknown_ref_fails_at_compose` |
| Empty ceiling denies all | 0081 | `::test_empty_ceiling_denies_all` |
| Registry exclusive write | 0081 | `::test_registry_exclusive_write` |
| Faulted cell cannot stay active | 0081 | `::test_faulted_cell_cannot_stay_active` |
| `in_process` requires explicit grant | 0081 | `::test_in_process_requires_explicit_grant` |
| Frozen composition immutable | 0081 | `::test_frozen_composition_immutable` |
| `layer0/` deleted, no imports | 0081 | `test_layer0_deleted` (repo lint extending `check_boundaries.py`) |
| Cold suspend/resume from WAL | R-9 (NOVA-2) | `test/runtime/test_nova2_cold_resume.py` (fresh-process fold + resume + parity vs control) |
| Echo plugin lifecycle on the wire | ADR-M0-13 | `test/runtime/registry/test_echo_lifecycle.py` (FSM §6.2 walked end-to-end on the wire) |
| Loop claim published with falsifier | 0082 / R-8 | F-LOOP (standing falsifier; publication checked by `test/docs/test_adr0082_published.py`) |
| Triad collapse executed | 0082 / R-11 | `test/docs/test_triad_collapse.py` (M-5) |
| Pack #2 zero core diffs | R-10 / M-5 | `test/packs/math_default/test_i7_zero_core_diffs.py` + `::test_trajectory_parity` |

### 6.4 Negative constraints and anti-pattern checklist (hard rules for implementers)

Every item below is a **build-breaking rule**, not advice. Each maps to an existing enforcement instrument.

1. **TCB budget:** any PR adding code to `vanguard/packages/kernel/` must keep logical LOC ≤ 1438 (`check_tcb_budget.py`). The M-6 spawn verb has 73 LOC of headroom (1438 − 1365). If the implementation does not fit, move logic to runtime pre-classification; **never** raise the ceiling without a new ADR.
2. **Domain blindness (I-7):** no token from `{coding, pytest, ast, git, python, math, lean, latex, …}` may appear in `domain/` or `kernel/` (`check_domain_blindness.py`, widened per F-18). Domain semantics live in packs, plugins, oracles, and prompts — data, not code.
3. **Single writer:** exactly one `LedgerEmitter` writes the stream; every event kind has exactly one privileged writer role (`check_event_coverage.py`, E-COV; falsifiers F-03/F-05). No component ever emits another component's kinds.
4. **Boundary lattice:** `domain ← ports ← kernel ← agency ← runtime → adapters`; adapters never import kernel or agency; `apps/` is a client (`check_boundaries.py`).
5. **One canonicalisation:** every digest and signature is over RFC 8785 JCS bytes (`domain/canonicalisation/jcs.py`). A second serialization path is F-16-class duplication and fails the build.
6. **One selector algebra:** total and fail-closed (`domain/selectors/resource_selector.py`). `check_duplication.py --enforce` fails a second algebra.
7. **Fail-closed everywhere:** unknown action, unparsable selector, empty ceiling, expired grant, absent verifier ⇒ deny. An `except: pass` on an authorization path is a security defect, not a robustness technique.
8. **No mid-run mutation:** frozen compositions are immutable (ADR-0005); no harness hot-swap; no `Retired → Provisioned` transition.
9. **Schemas strict for both readers and writers** (ADR-0032): generated types are never hand-edited (`generate_types.py --check`).
10. **Hermetic tests:** no network, no live API keys (`scan_secrets.py`; provider keys read only from env and unset in CI). Determinism: same seed ⇒ same trajectory digest.
11. **Anti-patterns explicitly rejected:** putting the embedding index in core (skill retrieval is a plugin); a second authorization fast-path (sub-5 ms pre-flight filters are advisory, planner-side, never mediators); an O(N²) peer-message bus (coordination is the State Plane); benchmark scores as evidence without separability; biological/cosmological framing in `docs/` (ADR-M0-10).
12. **Docs anti-sprawl:** no new scratch/plan/review Markdown anywhere in the tree (AGENTS.md §7). Law edits go to SPEC; decisions to new ADRs; execution to `sprint_active.md`. This proposal file itself is a root-level advisory artifact, not a `docs/` citizen — it registers nothing and commands nothing until adopted through the cascade in §7.3.

---

## 7. Repository Hygiene & Document Update Cascade

### 7.1 Stale-artifact cleanup (verified findings D-D … D-G)

| Artifact | Verified state | Action |
|---|---|---|
| `DELETE.md` (repo root) | 0 bytes [VERIFIED] | **Delete the file.** An empty file is not a placeholder; it is noise that linters and humans both trip over. |
| `docs/06_references/RESEARCH_THEORETICAL_SYNTHESIS_B.md` | Near-duplicate of `RESEARCH_THEORETICAL_SYNTHESIS.md`: identical front-matter `id: REF-06-M5`, identical title [VERIFIED] | **Merge the delta into the primary and delete `_B.md`**, recording the merge in git history. Two documents sharing one id break the reference index. |
| `docs/08_workflows/` | Empty directory [VERIFIED] | **Remove the directory** and its entry from the docs tree map, or populate it — carrying an empty tier is how the seven-tier problem happened. |
| `docs/06_references/vanguard_body_detailed.md` | Built on biological/cosmological framing that ADR-M0-10/REJ-10 forbids in `docs/` [VERIFIED] | **Relocate out of the governed `docs/` tree or rewrite without the framing.** The research value is real; the placement conflicts with standing law. |
| `check_markdown_links.py` `DOC_GLOBS` | Validates only `README.md`, `docs/README.md`, and a dead sprint-6B glob — the same defect class as F-18 (a linter narrower than the invariant it certifies) [VERIFIED] | **Widen `DOC_GLOBS` to `docs/**/*.md` + root `*.md`** so the four historically broken ADR links could never have survived CI. |
| Empty root proposals `005_*`, `006_*`, `007_*.md` | 0 bytes each [VERIFIED] | Delete or fill them; empty advisory slots invite confusion about which review is canonical. |
| `layer0/__pycache__` | Compiled caches in-tree | Add to `.gitignore` housekeeping if not already; delete from the working tree. |

### 7.2 What this proposal deliberately does NOT touch

`docs/SPEC.md`, all ADRs, `sprint_active.md`, `milestones.md`, wave plans, and all source code — untouched, per the output constraint. §7.3 is the instruction set a Director would execute **upon adoption**, not a change that has happened.

### 7.3 Section-by-section diff directives (executed only upon Director adoption)

**A. `docs/05_adr/` — six new files** (text from §3, verbatim, each with standard front matter per ADR-0000):
`0077-manifest-is-a-named-component-graph.md` · `0078-guardrails-declarable-absent-never-forgeable.md` · `0079-trajectory-truth-density.md` · `0080-agent-spawn-capability-mediated-verb-design-record.md` · `0081-layer0-final-absorption-with-nova4.md` · `0082-universal-turn-loop-mechanism-claim.md`. Update `INDEX.md` with the six rows. No edits to `0069`–`0076`.

**B. `docs/SPEC.md`** (four touches):
1. Header version anchor: `v0.6.0 Concept Lock` → `v0.6.1 Substrate Correction Lock (ADR-0077…0082)`.
2. §2.3 (manifest shape): replace the fixed-slot description with the named component graph; cite ADR-0077; keep slot names described as pack convention.
3. §5.3 (calibration): add the `attributable_for_promotion` exclusion and the explicit-`none` fingerprint rule; cite ADR-0078/0079.
4. §9 (refusals): no additions — the refusals this proposal re-affirms are already law; do not duplicate (that is the four-place duplication being collapsed).

**C. `docs/03_sprints/sprint_active.md`**:
1. Resolve contradiction D-C: remove NOVA-1 from the Wave-4 carry-out table; add it to the active Wave-2 packet with ADR-0079 as its law reference.
2. Add NOVA-2 (`test_nova2_cold_resume.py`) to the Wave-2 closing gate, precondition of M-3 entry.
3. 3.3-B (compose-v2): change status from `DIRECTOR` to `AUTHORIZED (scope call made, 004 §2.1)`.
4. 3.5-C (`agent.spawn` implementation): remains deferred to M-6; attach ADR-0080 as the design record.
5. Add the six NOVA-4 negatives to the Wave-3 packet as first-class falsifiers (not implied behavior).
6. Register Pack #2 = Math & Formal Deductive Verification on the post-M-4 section, as the I-7 gate with trajectory parity.

**D. `docs/02_roadmap/milestones.md`**:
1. Attach version tags to the milestone table per §4.1 (M-2→v0.6.1 … M-10→v1.0.0).
2. M-4 exit gate: expand to the nine-row table of §4.2 (or cite it) — "9-row integration verification" should name its rows.
3. M-5: name Pack #2 as Math & Formal Deductive Verification; add trajectory-parity to the exit gate.
4. Post-foundation table: no sprint-level detail (unchanged posture).

**E. Wave plans** (`docs/03_sprints/doing/wave2B_review.md`, `wave3_extensibility.md`, `wave4_foundation_e2e.md`): align each wave's task list with the corresponding ADR numbers and falsifier names from §6.3; remove any text still sending trajectory cost to Wave 4.

**F. Sequencing of the cascade:** ADRs first (they are the law everything else cites), then SPEC touches, then board/roadmap, then wave plans, then hygiene deletions (§7.1) in the same PR series. Each PR cites at least one active requirement (`REQ-TRUST-*`, `REQ-LATTICE-*` or the new ADR numbers) and confirms `check_boundaries.py`, `check_tcb_budget.py`, `scan_secrets.py` pass — per AGENTS.md §5.

---

## 8. Leadership-7 Sign-Off Matrix & Final Word

| Role | Position on this proposal | Named reservation |
|---|---|---|
| **Engineering Director** | APPROVE — with the stop line personally owned | M-4 is not satisfied by partial credit across runs |
| **CTO** | APPROVE — moat = corpus × composition surface × separability | Latency/tier-cost claims stay hypotheses until M-9 measurement |
| **CIO** | APPROVE — Absent-vs-Forged preserves auditability | Unsigned verdict rejection must be tested under every declaration combination |
| **Principal Staff Engineer** | APPROVE — gap register G1–G5 all closed by named falsifiers | NOVA-4 negatives are non-negotiable Wave-3 scope; shed breadth, not falsifiers |
| **Principal Systems Architect** | APPROVE — boundary lattice and TCB untouched by design | M-6 spawn implementation must fit 73 LOC headroom or overflow to runtime, never to budget growth |
| **Tech Lead** | APPROVE — every task has a file, a schema, and a test | The board contradiction D-C must be resolved in the same sprint that lands NOVA-1 |
| **PhD AI Specialist** | APPROVE — math is stated, constants are pinned, metaphysics excluded | Active-inference formulation is an engineering objective function, not a cognitive claim (ADR-M0-10) |

### Final word

The delta between AETHER today and the general task-solving swarm meta-framework of v1.0.0 is small in architecture and concentrated in surface and proof: **one schema revision, one guardrail declaration model, one metered corpus, one absorbed registry, one mediated verb, and one uncheated run.** The least reversible decisions — recursion as one primitive, authority as a reference monitor, state as fold, evidence as an exterior signature, identity split three ways — were already made in the general form, at real cost, before product pressure required it. What remains is to finish the surface people compose against, fill the corpus the future will learn from, and hold the stop line until the foundation has nine green rows of proof. Then — and only then — the swarm, the debate, the tree search, and the self-improving loop are all just manifests.

*Advisory only. SPEC/ADR/roadmap win on conflict. This document reorders and hardens; it never rewrites — and it has rewritten nothing.*

---

### Appendix — External SOTA references consulted (2026-08-21)

- Rafailov et al., *Direct Preference Optimization: Your Language Model is Secretly a Reward Model*, arXiv:2305.18290 (v3 2024-07).
- *Reward-Guided Autoregressive Graph Generation for Efficient Multi-Agent Communication Topology Design*, arXiv:2608.20099 (2026-08-20).
- *Discovering Efficient and Explainable Communication Topologies for LLM-based Multi-Agent Systems via Causal Inference* (E2-Explainer), arXiv:2608.12921 (2026-08-13).
- *EnvHarness: Awakening Static Worlds for Agent Learning*, arXiv:2608.19880 (2026-08-20).
- *Agentic ESOpt: Fine-Tuning Long-Horizon LLM Agents with Minimal GPU Requirements*, arXiv:2608.17310 (2026-08-18).
- *Enhancing Personalized Multi-Turn Dialogue with Curiosity Reward*, arXiv:2504.03206 (2025).
- *Operationalizing CaMeL: Strengthening LLM Defenses for Enterprise Deployment*, arXiv:2505.22852 (2025-05).
- *Empowering WebAssembly with Thin Kernel Interfaces*, arXiv:2312.03858 (EuroSys 2025) — capability-based sandboxing precedent.
- Competitive multi-agent misalignment emergence study (2026-08-14) — separability thesis confirmation.
- Internal corpus: `RESEARCH_k3_harness-suggestion.md` (A-B-C-D; Terminal-Bench 2.0 harness swing 64.7% → 78.4%), `RESEARCH_THEORETICAL_SYNTHESIS.md` (§2 mathematics, §4 McNemar), `RESEARCH_harness_agentic_coding_builder_research_and_framework*.md` (harness-as-independent-variable), principal reviews `001`–`006`, and `docs/00_overview/SYSTEM_OVERVIEW.md` (V2 audit, findings D-A…D-H).


















