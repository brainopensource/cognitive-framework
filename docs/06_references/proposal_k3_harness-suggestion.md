# k3_suggestion — SOTA Plan for AETHER

**Authors (roles):** Staff Engineer · Principal Architect · Senior Developer · Tech Lead
**Date:** 2026-08-21
**Classification:** Advisory. Law remains `docs/SPEC.md` + ADRs `0069`–`0076` + `002` (gap register) + `004` (v0.6.1 roadmap). This plan **reorders and hardens**; it never rewrites the locked concepts. On any conflict, SPEC/ADR/roadmap win.

---

## 0. North Star (restated operationally)

> **AETHER is an unforgeable, domain-blind operating substrate for building bounded autonomous task solvers — proven on software engineering, and architected to evolve into sovereign, self-improving multi-agent ecologies.**

Translated into falsifiable engineering claims:

1. **Unforgeable** — no execution grades itself; every capability claim traces to an exterior, signed, request-bound verdict that the agent cannot read, patch, or reason about.
2. **Domain-blind** — a new domain (Math, Data Science, Research) arrives as data (manifest + plugins + oracles) with zero diffs under `domain/` or `kernel/`.
3. **Bounded solvers** — agents run under monotonic authority and typed 6D leases; delegation never widens capability or budget.
4. **Proven on software engineering** — the first domain pack is the empirical stress-test of the kernel against compilers, test suites, and git diffs.
5. **Self-improving ecologies** — the substrate harvests signed trajectories into skills and DPO pairs, and improves *only* through a human-gated, partial-order promotion frontier it cannot drive itself.

---

## 1. Executive verdict

**The goal is reachable. The least reversible parts are already built correctly. Two defects remain, and both are cheap now and expensive forever after Wave 4.**

| Layer of the vision | State (verified) |
|---|---|
| **Foundation** (Decision/State/Evidence, domain-blind kernel, sandboxes, 6D leases) | **Essentially delivered.** M-0/M-1 green; M-2 in flight. |
| **Proving Ground & Abstraction** (coding pack as stress-test; declarative manifests for any domain, zero core changes) | **Half-built.** `packs/code-default` exists, but the plugin lifecycle has never run on the canonical path, and the manifest is a fixed-slot template. |
| **Emergence & Self-improvement** (spawn topologies, dual-process, learning loop) | **Correctly deferred (M-6…M-10).** The identity architecture that makes it safe is locked — but the corpus it will learn from is currently **born hollow**. |

Two compounding findings drive the whole sequencing below:

- **The trajectory corpus is hollow.** `vanguard/packages/runtime/trajectory.py` emits `dict(_ZERO_COST)` (lines 53, 75 — verified). Every episode that completes before this is fixed produces a schema-valid, attributable, but **unusable** training row. Everything Layer 3 promises (skill cards, DPO, calibrated escalation) is undefined without per-turn cost, model fingerprint, and verdict.
- **The manifest is a template, not a composition algebra.** `harness.yaml`'s five fixed slots describe the first pack, not the substrate. Debate, critic loops, tree search, and swarm topologies are spawn topologies + policy — but there is nowheres in the manifest to name them.

---

## 2. The A-B-C-D operating foundation

A bounded, evolvable, sovereign ecosystem is buildable **iff all four properties are generic**. Treat them as the load-bearing contract for every decision below:

| | Property | Plane | Weak today? |
|---|---|---|---|
| **A — Authority** | S0–S12 mediator: descriptor-bound grants, `Capabilities(child) ⊆ Capabilities(parent)`, typed leases `{additive: usd/tokens/bytes/millis} vs {structural: depth/turns}`, fail-closed selectors, one JCS canonicalisation, one writer (LedgerEmitter). | Decision | No — structurally sound. TCB ≤ 1438 LOC stands. |
| **B — Bundle** | Composition: manifest + resolved plugins + ceilings + policies → `FrozenHarness`. The composition surface your developers touch. | Composition | **Yes — fixed-slot template.** Must become a named component graph; slots degrade to pack convention. |
| **C — Corpus** | State + Evidence: SQLite WAL `fold(events)`; `mhf.trajectory/1` emitted at every `EpisodeCompleted`, rich with per-turn cost, model fingerprint, and **signed verdict-or-explicit-null**. | State / Evidence | **Yes — hollow.** Zero-cost rows satisfy F-12 today. |
| **D — Digest** | Measurement identity: `D_H` (composition) ≠ `D_R` (run) ≠ `D_X` (experiment). Never collapsed. The denominators of every future A/B. | Identity | No — locked and correctly scoped; remains generic **only if** B and C stay generic. |

**SOTA claim.** Sovereign, self-improving multi-agent ecologies emerge *only* if A, B, C, D are all generic. Today **A and D are generic; B and C are template-shaped / hollow.** The whole plan is the order in which we make B and C generic without ever weakening A or collapsing D.

---

## 3. Gap register (priority-ordered; every item verified or already on the board)

| # | Gap | Why it is (eventually) fatal | Fix | Gate |
|---|---|---|---|---|
| **G1** | Hollow trajectory (`_ZERO_COST` @ `trajectory.py:53,75`) | Layer 3 learns from rows that can never train it | **NOVA-1 / F-12 hardening:** non-zero per-turn cost, populated turns, model fingerprint, verdict-or-null; F-12 moves from schema-validity to **content assertions** | NOVA-1 green |
| **G2** | Fixed-slot manifest (W1) | Blocks Layer-2/3 compositions; every pack written against the old shape migrates | **Component graph** (3.1-B design, **3.3-B Director scope call**), slots → pack convention, `D_H` covers graph | Director call at Wave-3 entry |
| **G3** | Planners cannot spawn (W2) | Recursive algorithms (tree search, decomposition, delegation) have no home except inside the engine | **`agent.spawn` as mediated verb** (3.5): design note + falsifier sketch now; implementation post-M-4 | Design at M-3, decide post-M-4 |
| **G4** | Guardrails structural, not declarable (W4) | A research/math composition should not require a UID-10002 daemon; "universal" must not weaken trust | **Absent-vs-forged rule** (3.4): declare `evaluation: none`; `D_H` records it; trajectory marks **non-attributable-for-promotion**; unsigned verdict stays categorically illegal | Wave 3 |
| **G5** | `K ≪ N` unproven (W5) | M-7 concurrency is a refactor or a rewrite — the answer is one test | **NOVA-2 suspend/resume falsifier:** suspend mid-turn → cold-reconstruct from WAL in a fresh process → resume → complete | NOVA-2 green |
| **G6** | Governance corpus mass (W6) | 7 authority tiers drift like code; DUPLICATED deferred lists must be edited in 4 places | **Docs collapse post-M-4** → SPEC + ADR log + one living board | Scheduled |
| **G7** | Wave-3 falsifiers thin vs. Wave 1 (W7) | The framework claim is proven by the least-proven code (`layer0/registry` + `compose`) | **NOVA-4 negative suite:** unknown-ref-at-compose, empty-ceiling-denies, registry-exclusive-write, faulted-cell-not-active, `in_process` requires grant, frozen-composition-immutable | NOVA-4 green |
| **G8** | First-pack quality unmeasured externally (GLM §3.5) | A substrate whose first pack loses to a naive ReAct loop has a falsified composition surface | **Post-M-4 external benchmark run** of compiled `code-default` with cost/latency telemetry — not for leaderboard, for composition falsification | Post-M-4 |

---

## 4. Solution spine (phased; every phase names its gate)

### Phase I — Seize the unforgeable corpus *(Wave 2 close → first actions of the current sprint)*
Make **C** rich before anything learns from it.

1. **Close M-2** (convergence gate): duplication-detector green, zero `layer0.*` imports, no behaviour change.
2. **Execute NOVA-1 (G1) immediately.** It is registered `PRONTA` in M-2 — authorized Wave 2 work. Land it **before** Wave-3 features. Any episode that completes before this is a permanently degraded row in the only corpus Layer 3 will ever have.
3. **Execute NOVA-3** (`_PROC_PATTERN` read from the compiled ceiling, not restated).
4. **Land NOVA-2 (G5) before M-3 closes.** One falsifier decides whether M-7 concurrency is a scheduling refactor or a rewrite — buy that option value now while it is cheap.
5. **Make the 3.3-B component-graph decision (G2) at Wave-3 entry, before `compose v2` is written.** The cost of deciding late migrates every pack, every trajectory, every `D_H` attribution.

### Phase II — Walking-skeleton extensibility *(Wave 3)*
Make **B** a real composition surface; prove plugins end-to-end on the canonical path.

1. Registry FSM absorbed into `runtime/registry/`; every transition ledgered.
2. `compose v2`: discovery → resolve → verify (ceilings + signature) → freeze → `FrozenHarness(D_H)`.
3. **Echo plugin traverses the full lifecycle** (DISCOVERED…RETIRED on the wire) before any product plugin.
4. **NOVA-4 negative suite green** (G7). Shed breadth, never falsifiers.
5. Component-graph design (3.1-B); guardrail schema (3.4-B/C); spawn-verb design note (3.5).
6. **Gate M-3:** echo plugin lifecycle green; `code-default` loads via the same path; I-7 holds.

### Phase III — Foundation E2E *(Wave 4 — the STOP line)*
Nine-row gate green on **one real run**:

real model + authorized effect + filesystem + sandbox + **signed** eval + WAL + cold replay + **rich trajectory** (NOVA-1 validated by NOVA-5) + single runtime.

Nothing on the far side of this gate (`agent.spawn`, Pack #2, M-5…M-10, concurrency) may start until this is green.

### Phase IV — Consolidation + generality proof *(post-M-4; M-5)*
Prove the substrate claim with a **non-coding** pack; then pay down governance mass.

1. Docs collapse (G6): SPEC + ADR log + one living board; retire GAMMA and `002` once absorbed.
2. **Pack #2 built** (data-science / math / research): toolkits + oracles + manifest + selector vocabulary.
3. **Gate 5.2 (I-7 gate):** zero diffs under `domain/` and `kernel/`. Add a **trajectory-parity** assertion (GLM §3.4): the non-coding pack must emit the same rich `mhf.trajectory/1` rows.
4. External benchmark run of `code-default` (G8) — evidence for the composition surface, not leaderboard position.

### Phase V — Emergence unlock *(M-6 → M-10 arc)*
Build the learning loop only against a now-real corpus.

- **M-6 `agent.spawn` as kernel verb:** capability-gated delegation; debate/critic/tree-search/evolutionary compositions land as `spawn` topologies + policy — **not** a swarm engine.
- **M-7 controlled concurrency** (gated on NOVA-2 green + selector soundness).
- **M-8 framework-builder proven:** debate, critic-loop, evolutionary, multi-agent delegation as data; zero new engines.
- **M-9 high-performance orchestration:** `K ≪ N` many logical agents over a bounded worker pool; `project_id` sharding; measure IPC / serialization / ledger pressure.
- **M-10 meta-cognitive substrate:** outer-loop planner at slot `outer`, capability-restricted to manifest-mutation / skill-write / oracle-preregistration; harvest → distill → promote (below).

---

## 5. The learning loop (how self-improvement stays un-gameable)

```
harvest signed trajectories (C: rich rows: cost / fingerprint / signed verdict)
        ↓
distill skill cards & DPO pairs  (verified n-grams / chosen-vs-rejected by turn-prefix)
        ↓
paired McNemar vs. undeletable baseline (χ² ≥ 3.841, p < 0.05, N ≥ 50)
        ↓
signed promotion pointer flips the registry default (new D_H, never in-place)
        ↓
cassette-replay regression in the lab → human promotion gate
```

Why this cannot be gamed by construction:

1. Verdicts are **exterior-signed** (UID 10002, Ed25519, nonce-bound) — the agent cannot forge the signal.
2. `D_H`/`D_R`/`D_X` **never collapse** — the denominators of measurement are locked before any experiment exists.
3. Promotion **flips a pointer**; mutation never happens in production in-place.
4. The harvester **consumes** the corpus; it never drives it.

The entire loop is undefined without **G1 (rich corpus)** — that is why NOVA-1 is the plan's first action.

---

## 6. Adoption map (research corpus → law)

**Adopt (already matches locked law):**
- Harness-as-the-independent-variable (Terminal-Bench evidence; it is the project's thesis).
- Component graph **at the composition layer only** (DeepSeek's flat surface) — orthogonal to rigidity at the authority boundary; AETHER has both. (Do NOT import "no privileged core.")
- Structural retrieval before semantic (Aider lesson); recall-over-precision warning (ContextBench).
- Delegation must pay rent (matches 005; M-8 validation compositions are the rent-paying proof).
- Harness-native learning (LEGO-RL): train where you infer — converges with SPEC §7 DPO, with the un-gameable exterior-signed signal competitors lack.
- Small-model channels (System-1 local, error classifier, skill synthesizer) as policy above the wire.

**Adapt (re-express within the law):**
- Sub-5 ms pre-flight filter → planner-side or advisory; **never** a second authorization path (S0–S12 remains the sole mediator).
- Elo-decayed skill eviction → a harvester/retrieval strategy; cards enter only via paired McNemar (§5.2).
- Active inference → keep the math in SPEC §5.3 (calibrated `P(pass | action, context)`); drop the metaphysics (ADR-M0-10).
- McNemar protocol → already law (`docs/04_annex/MEASUREMENT.md`).

**Refuse (contradict locked law):**
- "No privileged core"; swarm/DAG/graph-DB engines; vector DB as core; RL/multi-agent-first sequencing; metaphysics in normative docs; benchmark scores as evidence without separability. All correctly refused by `ADR-0070` / `REJ-01` / `ADR-M0-10`.

---

## 7. Risk register

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | Hollow corpus survives to production | **Fatal to Layer 3** | NOVA-1 now; F-12 content assertions |
| R2 | Component graph decided late | **High** (every pack/trajectory/`D_H` re-attributed) | 3.3-B Director call at Wave-3 entry |
| R3 | Wave-3 falsifiers cut under pressure | **Fatal to L2 claim** | NOVA-4 non-negotiable; shed breadth |
| R4 | M-4 stop line eroded | **High** (repeats dual-runtime failure) | Director owns the stop |
| R5 | Latency claims degrade into marketing | Medium | Name as hypotheses now; measure at M-9 |
| R6 | First-pack unmeasured externally | Medium | Post-M-4 benchmark run with telemetry |
| R7 | Governance mass grows | Medium | Docs collapse scheduled post-M-4 |

---

## 8. Decision register (numbered calls)

1. **Trust spine (A) — keep as-is.** No kernel growth except tests.
2. **NOVA-1 (C) — execute now.** Highest leverage-per-cost in the corpus.
3. **Component graph (B) — adopt at 3.3-B.** Director scope call at Wave-3 entry.
4. **Absent-vs-forged guardrails — adopt as ADR.** Never permit unsigned verdicts.
5. **`agent.spawn` as mediated verb — design at M-3, implement post-M-4.** No TCB change before Wave 4 closes.
6. **NOVA-2 suspend/resume — land before M-3 closes.**
7. **NOVA-4 negative suite — non-negotiable scope for Wave 3.**
8. **M-4 stop line — hold exactly.**
9. **Pack #2 — gate, not nice-to-have; include trajectory-parity assertion.**
10. **External benchmark — post-M-4, pre-M-8.**
11. **Docs collapse — scheduled post-M-4.**
12. **Vision artifact** — optional one-page, versioned, non-normative.
13. **Reject** the greenfield PRD framework, "no-privileged-core" flatness, swarm/DAG/graph-DB engines, vector-DB-as-core, metaphysics-in-normative-docs.

---

## 9. The four claims this plan will falsify (the proof)

- **P1 — "The corpus is learnable."** NOVA-1: F-12 content assertions green.
- **P2 — "The substrate is domain-general."** I-7 gate: Pack #2 ships with zero `domain/`/`kernel/` diffs.
- **P3 — "Concurrency is a scheduler refactor."** NOVA-2 suspend/resume green.
- **P4 — "Self-improvement is safe."** Signed promotion frontier + McNemar gates + `D_H`/`D_R`/`D_X` never collapse.

Until these survive falsification, the goal is a thesis. The moment they do, **A-B-C-D** are all generic — and the substrate earns the right to evolve into sovereign, self-improving ecologies.

*Advisory only. SPEC/ADR/roadmap win on conflict. This plan reorders and hardens; it never rewrites.*
