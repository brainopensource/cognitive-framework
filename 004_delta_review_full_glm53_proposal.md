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

<!-- §NEXT -->





