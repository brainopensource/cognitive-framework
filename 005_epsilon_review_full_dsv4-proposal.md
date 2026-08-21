# Epsilon Review — Full DSv4 Proposal

**The Definitive Executive Review & Technical Proposal for Evolving AETHER from a Coding Substrate into a General Task-Solving Swarm Meta-Framework**

| Field | Value |
|---|---|
| **Prepared by** | The **Leadership 7** — collective executive body |
| **Composition** | Engineering Director · CTO · CIO · Principal Staff Engineer · Principal Systems Architect · Tech Lead · PhD AI Specialist |
| **Date** | 2026-08-21 |
| **Baseline** | `main` @ `733855b` — verified against the living tree during this review |
| **Subject** | Version ladder **v0.6.1 → v1.0.0** (M-2 through M-10) |
| **Grounding** | `docs/00_overview/SYSTEM_OVERVIEW.md` (V2 audit) · `docs/SPEC.md` · ADRs `0069`–`0076` + M0-01…M0-13 · `002` gap register · `004`/`005`/`006` reviews · `docs/06_references/` research corpus · forensic read of `vanguard/packages/` · external SOTA survey (2023–2026) |
| **Output constraint** | **ONE document.** No existing SPEC/ADR/source file is edited by this review. This file is advisory — it amends nothing. Binding force accrues only through the ADRs it drafts (`0077`–`0082`), which must be adopted by their normal append-only process. |

---

## 0. Executive Fast Briefing

> **Verdict of the Leadership 7 — unanimous.**

The substrate is real. The primitives are correct. The composition surface is not yet. Two defects are cheap now and permanently expensive after the M-4 stop line: **(1)** the trajectory corpus is **born hollow** (`runtime/trajectory.py:53,75` emit `_ZERO_COST` — verified on disk this review), and **(2)** `harness.yaml` is a **fixed-slot template**, not a composition algebra. The remaining work is the order in which we make the **Bundle** (B) and the **Corpus** (C) generic without ever weakening **Authority** (A) or collapsing **Digest** (D).

Four rulings carry the whole plan:

1. **Seize the corpus now.** NOVA-1/2/3 execute inside M-2, not Wave 4. This is the only decision with an irreversible clock — every episode completing before the fix is a permanently degraded row in the only corpus Layer 3 will ever train on.
2. **Component graph at the composition surface only.** Flatness at the surface is orthogonal to rigidity at the authority boundary. We take DeepSeek's flat surface and refuse its "no privileged core."
3. **Absent-vs-forged, never optional-vs-optional.** You may turn a guardrail off; you may never turn off the record that it was off. Seven non-negotiables stay permanent.
4. **The M-4 stop line is sacred.** Nine rows on one uncheated real run. Nothing on the far side (`agent.spawn` implementation, concurrency, Pack #2, M-5…M-10) starts before it is green.

The version ladder the Leadership 7 ratifies:

```text
v0.6.0  Concept Lock                  ✅ M-0/M-1  (already locked, ADR-0075)
v0.6.1  Substrate Correction Lock     → M-2      (ADRs 0077–0082 · NOVA-1/2/3 · F-12 hardened)
v0.6.2  Extensibility Lock            → M-3      (registry FSM · compose v2 · component graph · NOVA-4 · layer0 deleted)
v0.6.3  Foundation MVP                → M-4      (nine-row E2E · STOP LINE · package cut from 0.4.5b1)
v0.7.0  Generality Proof              → M-5      (Pack #2 Math & Formal Deductive Verification · doc collapse)
v0.8.0  Mediated Delegation + Concurrency → M-6/M-7
v0.9.0  Framework Builder + Orchestration → M-8/M-9
v1.0.0  Meta-Cognitive Substrate      → M-10     (final gate)
```

---

## 1. Executive Rulings & Strategic Paradigm Shift

### 1.1 The consensus and mandates of the Leadership 7

Each principal records their ruling. These are mandates, not preferences — each binds the wave plans it names.

| # | Principal | Ruling | Disposition |
|---|---|---|---|
| 1 | **Engineering Director** | The M-4 stop line is **non-negotiable and unchanged**. Scope widening to make the run pass is grounds to halt the wave. `agent.spawn` implementation, concurrency, Pack #2, and all of M-5…M-10 stay out of implementation scope until the nine-row gate is green on one real, uncheated run. Package version cut from `0.4.5b1` happens **at the M-4 gate** (v0.6.3). | **Lock now** |
| 2 | **CTO** | The moat is the **separability thesis + identity trinity**. Harness-as-independent-variable (Terminal-Bench 2.0: 64.7%→78.4% swing on identical model) is already our thesis — we build the substrate that makes that swing *measurable without collapsible denominators*. The component graph is adopted because it is the layer users touch; it is refused at the authority boundary. | **Generalize now (surface) / refuse (core)** |
| 3 | **CIO** | **Absent-vs-forged** is the security posture. An unsigned verdict is categorically illegal under *every* composition; an *acknowledged absence* is a legitimate composition marked non-attributable. Writer authority on privileged kinds, envelope lineage, fail-closed selectors, ledger-as-truth, attenuation-on-spawn, signature-required-for-claimed-verdict, JCS-as-byte-source — these seven are permanent. | **Generalize now** |
| 4 | **Principal Staff Engineer** | NOVA-1/2/3 land in M-2 (not Wave 4). The board's carry-out to Wave 4 is **overruled**; it contradicts `004`, `005` §W8, `proposal_hy3_*`, and the GLM review, and it is the single highest-leverage-per-cost item in the corpus. Wave 3 is **rebalanced**, not re-labelled (NOVA-4 becomes six first-class falsifiers). | **Strengthen now** |
| 5 | **Principal Systems Architect** | The TCB LOC gate (1365/1438) **stands** as the living gate until KERNEL.md §1.1's replacement triple exists (mutation score on kernel+reducers · % controls with production call-site proofs · E-COV). The kernel gains **nothing but tests** in Waves 1–4. The five-SPI freeze stays, but "a sixth SPI needs a review" must not harden into "five SPIs forever" — revisit at M-9. | **Lock now / revisit at M-9** |
| 6 | **Tech Lead** | Zero-guesswork bridge is mandatory: every ADR ships a bound falsifier, every falsifier maps 1:1 to a named test function, every schema is JSON-Schema 2020-12 normative, every lifecycle transition is ledgered. No task on the board may cite `docs/07_reviews/` or `docs/06_references/` as a requirement. | **Lock now (process)** |
| 7 | **PhD AI Specialist** | Active-inference, trajectory credit assignment, skill synthesis, and DPO harvesting are **exterior, domain-blind, promotion-gated policies** — never kernel primitives. The math in §5 is formalized now so that when M-10 opens, the layer is implemented against equations already accepted, not equations invented under pressure. Metaphysics stays out (ADR-M0-10 / REJ-10). | **Defer to M-10 / design now** |

### 1.2 SOTA 2026 alignment

Our review of the external literature (2023–2026) and the internal research corpus converges on five positions. Each is stated with its external anchor and its consequence for AETHER.

**(a) Harness Engineering — the harness is the independent variable.** The SOTA survey (`RESEARCH_harness_agentic_coding_builder_research_and_framework.md`) records Terminal-Bench 2.0 evidence that a harness swing moves the same GPT-5.3-Codex model from 64.7% to 78.4%. *Consequence:* the substrate's product is not the agent, it is the operating system that turns a policy into verifiable behaviour. The M-4 E2E proves our harness is *real*; the M-5 Pack #2 gate proves it is *general*.

**(b) Stigmergic Swarms via the State Plane, not O(N²) chatter.** Generative-agent and swarm literature (Generative Agents, arXiv:2304.03442; multi-agent coordination surveys) defaults to message-passing coordination — an O(N²) chatter cost that also forfeits attribution. AETHER's alternative is **stigmergy**: agents coordinate through the *ledger* — the shared, immutable, hash-chained state plane — rather than through pairwise dialogue. A spawn topology is a *policy over events*; a swarm is a *projection over the ledger*, never a graph database or a swarm engine (refused, ADR-0070). This keeps coordination cost O(events), keeps every causal relation attributable via `parent_id`, and keeps the judge exterior. *Consequence:* M-8's "debate/critic/evolutionary" compositions are named component graphs whose agents communicate by writing to and reading from the ledger — not by speaking to each other directly.

**(c) The Separability Thesis.** "What solved it must be separable from what judged it, and the judge must be unreachable from the judged." This is the moat no competitor holds, and it is the precondition for an un-gameable training signal — not by policy but by construction. *Consequence:* every future learning loop (DPO, skill synthesis, promotion) consumes corpus rows whose verdicts were exterior-signed and whose identities (`D_H`/`D_R`/`D_X`) never collapsed.

**(d) Flat surface, rigid core.** DeepSeek Harness organises configuration as a flat ordered stack of plugin bundles with "no privileged core to patch." We **import the first property, refuse the second.** Flatness at the composition surface (the named component graph) is orthogonal to rigidity at the authority boundary (S0–S12, single writer, exterior judge). This is the differentiated position no one occupies. *Consequence:* T-1 is decided as a surface generalization, and the refusal list grows by zero.

**(e) The A-B-C-D Foundation.** Sovereign, self-improving multi-agent ecologies emerge **iff all four are generic**:

| | Property | Plane | Today |
|---|---|---|---|
| **A — Authority** | S0–S12 mediator, descriptor-bound grants, monotonic attenuation, typed 6D leases | Decision | **Generic** (1365/1438 LOC, rule-for-rule vs KERNEL.md) |
| **B — Bundle** | manifest → `FrozenHarness(D_H)` | Composition | **Template-shaped** → component graph (ADR-0077) |
| **C — Corpus** | WAL `fold(events)` → `mhf.trajectory/1` | State/Evidence | **Hollow** → rich rows (ADR-0081) |
| **D — Digest** | `D_H ≠ D_R ≠ D_X`, JCS bytes | Identity | **Generic & locked** |

*Consequence:* the entire plan is the order in which B and C become generic without weakening A or collapsing D.

### 1.3 The strategic paradigm shift, in one sentence

> AETHER stops being *a coding harness with a kernel attached* and becomes *the substrate from which many generations of bounded, attributable, self-improving task-solvers are composed* — by making the **surface** (B) expressive, the **corpus** (C) learnable, and the **authority** (A) and **identity** (D) exactly as rigid as they already are.

---

## 2. Adjudication of All Open Architectural Tensions (T-1 … T-9)

Each tension is decided. Each decision carries its disposition label and its bound falsifier (per ADR-0074: *a concept without a bound falsifier is not locked*).

### 2.1 T-1 — Manifest shape: fixed slots vs. named component graph → **GENERALIZE NOW**

**Determination:** `harness.yaml` becomes a **named component graph**. Slot names (`planner`, `context`, `memory`, `evaluation`, `toolkits`) survive only as a **pack convention**, not a schema constraint. `D_H` extends to cover the graph — principle unchanged (still the complete behaviour-affecting composition).

**Rationale:** The five-hole template expresses exactly one ReAct coding agent. Debate, critic loops, tree search, and evolutionary search are all spawn-topologies + policy, but there is *nowhere in the manifest to name them*. This is cheap before M-4 and — because `D_H` is computed over the manifest shape — expensive after (schema migration + `D_H` migration + every pack rewritten + every trajectory re-attributed).

**Falsifier (ADR-0077):** `test_component_graph_expresses_two_planners` — a manifest naming two planner-class components with a binding section compiles to distinct `gene_digests`; and `test_slot_names_are_convention` — a manifest using *no* slot names still compiles, and `code-default`'s slot-named manifest produces a component graph where `planner` is a graph key, not a schema-required field.

**Landing:** Wave 3 (3.1-B design, 3.3-B Director call at Wave-3 entry — *before* compose-v2 is written).

### 2.2 T-2 — Spawning: engine-owned vs. capability-mediated `agent.spawn` → **DESIGN NOW, IMPLEMENT POST-M-4 (M-6)**

**Determination:** `agent.spawn` is formalized as a **capability-mediated kernel verb**, dispatched through S0–S12 like any other effect. Design note and falsifier sketch are written now; **implementation is blocked until post-M-4** and lands at M-6.

**Rationale:** Today `spawn()` is engine-owned (`agency/episode/engine.py:531`), so any algorithm whose structure *is* recursion has nowhere to live except inside the engine — the one place the current design most plausibly forces a new engine later (ADR-0070's stated reversal condition). Option B *strengthens* authority: delegation stops being a privileged engine call and becomes a mediated effect with a receipt — ledgered, budgeted, attributed, attenuated by existing machinery. The objection is sequencing, not security.

**Falsifier (ADR-0079, sketch for M-6):** `test_planner_without_spawn_grant_cannot_delegate` — a planner whose composition lacks the `agent.spawn` verb cannot create a child; `test_child_stays_monotonically_attenuated`; `test_spawn_recorded_as_mediated_effect_with_receipt`.

**Landing:** design at M-3 (3.5-A/B), decide at M-3 (3.5-C, Director), implement at M-6.

### 2.3 T-3 — Guardrails: mandatory mechanism vs. declarable "absent-vs-forged" → **GENERALIZE NOW**

**Determination:** Adopt the **absent-vs-forged** rule. A composition may declare `evaluation: none`, an optional sandbox tier, or an optional approval policy. Compose accepts the declaration, `D_H` records it, the trajectory records `oracle: null`, and the run is marked **non-attributable for promotion**. An unsigned verdict remains **categorically illegal** under every composition.

**Ratified seven permanent non-negotiables** (the fixed substrate boundary, never optional): (1) writer authority on privileged kinds; (2) envelope lineage by construction; (3) fail-closed selector inclusion; (4) ledger-as-truth; (5) capability attenuation on spawn; (6) signature required on any verdict *that is claimed*; (7) JCS as the sole byte source.

**Rationale:** Guardrails must not drift from infrastructure into product constraint. A research or pure-compute optimisation loop should not require a UID-10002 daemon and a preregistered oracle to run. The distinction the substrate enforces is **absent vs. forged** — not guarded vs. unguarded.

**Falsifier (ADR-0078):** `test_unsigned_verdict_illegal_under_any_composition` — an unsigned `VerdictRecorded` is rejected even when another component declared `evaluation: none`; `test_declared_absence_is_recorded` — `D_H` differs between guarded and unguarded compositions, and the trajectory marks `oracle: null`.

**Landing:** Wave 3 (3.4-A ADR → 3.4-B schema → 3.4-C marking → 3.4-D falsifier).

### 2.4 T-4 — Trajectory quality: the "born-hollow" corpus (G1 / NOVA-1) → **STRENGTHEN NOW (the only decision with an irreversible clock)**

**Determination:** **Authorize NOVA-1 now, in M-2.** The `sprint_active.md` carry-out to Wave 4 is overruled. F-12 is strengthened from *schema validity* to **content assertions**: non-zero per-turn cost vector, populated turns, model fingerprint present, verdict embedded-or-explicitly-null.

**[VERIFIED on disk this review]** `vanguard/packages/runtime/trajectory.py`:

```python
line 10:  _ZERO_COST = {"usd_micros": 0, "tokens": 0, "bytes": 0, "millis": 0}
line 53:              "cost": dict(_ZERO_COST),      # per-turn cost
line 75:      "cost": dict(_ZERO_COST),              # episode cost
```

**Rationale:** This is the failure I-9 was written to prevent — a digest over `{ids, n}` was rejected for the same reason. F-12 currently asserts schema validity, which a content-free record satisfies: the falsifier passes while the invariant fails. Every episode completing before the fix is a permanently degraded row; trajectories cannot be back-filled because the governor's settled cost ledger for a past run is gone. The board (Wave 4) and the register/reviews (now) were in live contradiction; **the Leadership 7 resolves it in favor of now**, writing the contradiction closed (§7.2).

**Falsifier:** `test_episode_completed_emits_populated_trajectory` (strengthened F-12) — asserts `turns` non-empty, per-turn `cost != _ZERO_COST`, `model_fingerprint` present, `verdict` embedded or explicitly `null`.

**Landing:** M-2 (NOVA-1, `PRONTA`). Confirmed at M-4 by NOVA-5 (the real run's trajectory carries non-zero cost).

### 2.5 T-5 — Layer-0 absorption timeline → **ABSORB AT 3.1, THEN DELETE (parity first)**

**Determination:** `layer0/registry/` and `layer0/compose/` absorb into `vanguard/packages/runtime/` at **3.1**, *then* `layer0/` is deleted. Behavioral parity first, per SPEC §1 — *"Duplicate kernels, schedulers, mocks, and synthetic verdict paths MUST NOT be deleted until a behavioral parity gate."*

**Risk accepted and mitigated:** `005` §W7 is correct that this code has no packages twin and has never run on the canonical path. The mitigation is NOVA-4 (six negatives) plus a behavioral parity assertion before deletion. The two headline forensic defects — the fabricated `"pass"` (`layer0/scheduler/driver.py:138`) and the fail-open ceiling (`layer0/spi/ceiling.py:21`) — are already dead (deleted at 2.2-B), verified this review.

**Falsifier (part of ADR-0082 / NOVA-4):** `test_layer0_fully_deleted_at_M3_gate` — `layer0/` is absent from the tree, and `check_stale_paths` reports zero references to `layer0.*`.

### 2.6 T-6 — The loop as mechanism → **KEEP, DOCUMENT WITH ITS FALSIFIER**

**Determination:** The universal turn loop `observe → propose → authorize → effect → receipt → evaluate → (reflect)*` stays **mechanism, never plugin**. Published as a claim with a bound falsifier.

**The published claim and its falsifier (ADR-0080):**

> **Claim:** Every agentic algorithm expressible as "bounded recursive solvers" is expressible as *spawn-topology + planner policy* over this loop.
> **Falsifier:** *Name one agentic algorithm that cannot be so expressed.* If someone produces one within 12 months of adoption, that is genuine ADR-0070 reversal evidence. If nobody can, the loop is proven and the argument ends.

**Rationale:** Competing harnesses make the loop itself a plugin — coherent only because they have no authority boundary to preserve. Without a published falsifier, the question is relitigated every quarter at full cost.

### 2.7 T-7 — `K ≪ N` asserted, never tested → **STRENGTHEN NOW (NOVA-2)**

**Determination:** Authorize **NOVA-2 in M-2**: suspend an episode mid-turn → cold-reconstruct in a fresh process from the WAL → resume → complete. This is the **precondition** for I-11's measurement gate, not its satisfaction.

**Rationale:** `002` §5 claims many logical agents share a bounded worker pool; nothing demonstrates logical-agent/worker separation — `EpisodeEngine` *is* the scheduler shell. The precise question: *is an episode's continuation reconstructible from the ledger alone, or does resuming require the live Python object?* Green ⇒ the M-7 concurrency future is a scheduling refactor. Red ⇒ hidden in-process coupling, and we want to know now, not at M-7.

**Falsifier:** `test_suspend_midturn_cold_reconstruct_resume_completes` — an episode suspended mid-turn, reconstructed in a fresh process from the WAL file (not an in-memory list — that is the I-4 proof standard), resumes and completes with identical folded state.

### 2.8 T-8 — Governance mass vs. capability → **SIMPLIFY AFTER M-4 (M-5)**

**Determination:** Documentation collapse to **SPEC (law) + ADR log (decisions) + one living board** is scheduled at M-5, not now. Mid-flight documentation surgery during Wave 2/3 is strictly worse than the duplication. GAMMA and `002` retire as standing authorities once their content is absorbed.

**Rulings on corpus hygiene (checklist item 8):**
- **8b** `vanguard_body_detailed.md` — its biological/cosmological framing conflicts with ADR-M0-10/REJ-10. **Retire** (or relocate out of `docs/`); its computational-physics/emergence content is not normative and must not sit under `docs/` in conflict with a standing refusal.
- **8c** `RESEARCH_THEORETICAL_SYNTHESIS.md` / `_B.md` — duplicate pair sharing `id: REF-06-M5`. **Consolidate to one** (keep the non-`_B` file; retire `_B`), at M-5.
- **8d** `RESEARCH_Harness_Builder_Framework.md` — **rejected as a competing architecture**; mined only as a catalog of plugin/adapter ideas.

### 2.9 T-9 — The five-SPI freeze → **KEEP, REVISIT AT M-9**

**Determination:** ADR-M0-03's freeze of exactly five SPIs (`IPlanner`, `IContextManager`, `IToolkit`, `IMemoryEngine`, `IEvaluationGate` — `ports/spi.py`, verified) stands. The guard is correct; what must not happen is *"a sixth SPI requires a design review"* hardening into *"there are five SPIs forever."* Revisit at M-9 (9.2-B, TECH-LEAD) against the mature component graph.

**Related ruling — TCB metric (checklist item 9):** the LOC gate (1365/1438) remains the living gate until KERNEL.md §1.1's replacement triple exists. Build that replacement at M-9 as a named milestone (not a side task).

---

## 3. Drafted Append-Only ADR Catalog (`ADR-0077` — `ADR-0082`)

The following are **complete draft texts**. Adoption is by the normal append-only process (ADR-0000); each narrows or extends prior ADRs by explicit citation and ships a 1:1 bound falsifier. The Leadership 7 recommends adoption of all six.

---

### ADR-0077 — Named Component Graph at the Composition Surface

- **Status:** Proposed
- **Narrows/extends:** ADR-0072 (plugin boundary), ADR-0076 (canonical artifacts), ADR-0069 (composition lattice). Does not reopen ADR-0070 (no swarm engine), ADR-0071 (identity trinity).
- **Context:** `harness.yaml` (`packs/code-default/harness.yaml`) binds five fixed keys. The Substrate Generality Review (`005` §W1) and the v0.6.1 roadmap (`004` §2) name this the highest-leverage, hardest-deadline scope call. `D_H` is computed over the manifest shape, so the decision is cheap before M-4 and expensive after.
- **Decision:**
  1. The manifest schema advances to `mhf.manifest/2` (§6.1): a **named component graph** — a map of component instances, each declaring `spi`, `ref`, `config`, `capabilities`, `ceiling` — plus an explicit `bindings` section describing wiring (roles and edge targets).
  2. Slot names (`planner`, `context`, `memory`, `evaluation`, `toolkits`) are **pack convention**, not schema constraint. `code-default` declares one planner named `main`; its `harness.yaml` migrates mechanically.
  3. `D_H` covers the graph. Principle unchanged: still the complete behaviour-affecting composition (prompt, ceiling, approval policy, model routes, resolved component refs+digests).
  4. `gene_digests` (already present in `compose.py`, verified) become the per-component attribution surface, so a trajectory can name *which* component proposed what.
- **Schema:** `schemas/mhf/manifest.schema.json` → version 2 (§6.1).
- **Bound falsifier:** `test_component_graph_expresses_two_planners` + `test_slot_names_are_convention` (§2.1).
- **Landing:** Wave 3, 3.3-A/B/C/D. Director scope call at Wave-3 entry (3.3-B), *before* compose-v2 is written.

---

### ADR-0078 — Absent-vs-Forged Guardrails

- **Status:** Proposed
- **Narrows/extends:** ADR-0072 (exterior judge), ADR-0074 (writer authority), ADR-0073 (defer/refuse boundaries). Does not weaken any.
- **Context:** `005` §W4: guardrails are structural where they should be declarable. A research or pure-compute composition should not require a UID-10002 daemon and a preregistered oracle to run.
- **Decision:**
  1. **Rule:** *you may turn a guardrail off; you may never turn off the record that it was off.* A composition may declare `evaluation: none`, an optional sandbox tier, or an optional approval policy. Compose accepts; `D_H` records; the trajectory records `oracle: null`; the run is marked **non-attributable for promotion**.
  2. The substrate enforces **absent vs. forged**, not guarded vs. unguarded. An unsigned `VerdictRecorded` is categorically illegal under every composition.
  3. **Seven permanent non-negotiables** (the fixed substrate, never optional): writer authority on privileged kinds · envelope lineage · fail-closed selector inclusion · ledger-as-truth · capability attenuation on spawn · signature required on any claimed verdict · JCS as the sole byte source.
- **Schema:** `mhf.manifest/2` `guardrails` block (§6.1).
- **Bound falsifier:** `test_unsigned_verdict_illegal_under_any_composition` + `test_declared_absence_is_recorded` (§2.3).
- **Landing:** Wave 3, 3.4-A (ADR) → 3.4-B (schema) → 3.4-C (marking) → 3.4-D (falsifier).

---

### ADR-0079 — `agent.spawn` as a Capability-Mediated Kernel Verb (Design Only)

- **Status:** Proposed
- **Narrows/extends:** ADR-0070 (recursion primitive). Explicitly defers implementation per ADR-0073 (defer register).
- **Context:** `005` §W2: `spawn()` is engine-owned (`agency/episode/engine.py:531`); `IPlanner` gets only `plan/observe/reflect`. Recursive algorithms have no home except inside the engine.
- **Decision:**
  1. `agent.spawn` is **designed** as a capability-mediated kernel verb dispatched through S0–S12. A planner may spawn only if its composition granted the verb; children are monotonically attenuated by existing machinery; every spawn is a ledgered, budgeted, attributed effect with a receipt.
  2. **Implementation is blocked until post-M-4** (lands at M-6, owner: Director, decision 3.5-C).
  3. The kernel gains **nothing but tests** in Waves 1–4; the TCB LOC ceiling (1438) stands.
- **Bound falsifier (sketch, executed at M-6):** `test_planner_without_spawn_grant_cannot_delegate` · `test_child_stays_monotonically_attenuated` · `test_spawn_recorded_as_mediated_effect_with_receipt`.
- **Landing:** design at M-3 (3.5-A/B), decide at M-3 (3.5-C), implement at M-6 (6.1-A…D).

---

### ADR-0080 — The Universal Turn Loop as Mechanism (Published Claim with Falsifier)

- **Status:** Proposed
- **Extends:** ADR-0070 (loop as mechanism, not plugin).
- **Context:** `005` §W3: the loop `observe → propose → authorize → effect → receipt → evaluate → (reflect)*` stays mechanism, but the claim is left implicit and gets relitigated every quarter at full cost.
- **Decision:**
  1. The claim is published: *every agentic algorithm expressible as bounded recursive solvers is expressible as spawn-topology + planner policy over this loop.*
  2. The bound falsifier: *name one agentic algorithm that cannot be so expressed.* A valid counterexample is genuine ADR-0070 reversal evidence. No counterexample within 12 months of adoption proves the loop and ends the argument.
  3. `reflect` remains a Phase-2 outer-loop stage (not implemented in v0.6); the loop is unchanged in Waves 1–4.
- **Bound falsifier:** the claim itself, bound to a 12-month window, with reversal evidence protocol.
- **Landing:** Wave 3 (documentation; no code).

---

### ADR-0081 — Corpus Seizure: NOVA-1/2/3 and F-12 Content Hardening

- **Status:** Proposed
- **Narrows/extends:** ADR-0074 (falsifier discipline), ADR-0071 (I-4/I-9). Overrules the `sprint_active.md` carry-out of trajectory cost to Wave 4 (the contradiction is resolved in favor of now).
- **Context:** `runtime/trajectory.py:53,75` emit `_ZERO_COST` (verified). F-12 asserts schema validity only. Every pre-fix episode is a permanently degraded corpus row; trajectories cannot be back-filled.
- **Decision:**
  1. **NOVA-1 (M-2):** F-12 strengthened to content assertions — non-zero per-turn cost, populated turns, model fingerprint present, verdict embedded-or-explicitly-null.
  2. **NOVA-2 (M-2):** the suspend-mid-turn → cold-reconstruct-from-WAL → resume-to-completion falsifier (the `K ≪ N` proof; precondition, not satisfaction, of I-11's gate).
  3. **NOVA-3 (M-2):** `_PROC_PATTERN` read from the compiled harness ceiling, not restated as a literal.
- **Bound falsifier:** `test_episode_completed_emits_populated_trajectory` (NOVA-1) · `test_suspend_midturn_cold_reconstruct_resume_completes` (NOVA-2) · `test_proc_pattern_reads_compiled_ceiling` (NOVA-3).
- **Landing:** M-2 (all three `PRONTA`, authorized Wave 2 work). NOVA-5 at M-4 confirms NOVA-1 on the real run.

---

### ADR-0082 — Wave-3 Rebalancing, layer0 Retirement, and Post-Foundation Scheduling

- **Status:** Proposed
- **Narrows/extends:** ADR-0073 (defer register), ADR-0076 (canonical artifacts). Schedules M-5 doc collapse (T-8) and M-9 TCB-metric replacement (§3.2, §2.9).
- **Context:** `005` §W7: Wave 3 carries the entire framework claim on far fewer falsifiers than Wave 1 carried for the trust spine, built on `layer0/registry/` + `layer0/compose/` which have never run on the canonical path.
- **Decision:**
  1. **NOVA-4** adds six first-class negative falsifiers (not implied behaviour): unknown-ref-fails-at-compose (never at runtime) · empty-ceiling-denies · registry-exclusive-`Plugin*`-write · faulted-cell-cannot-stay-active · `in_process`-requires-explicit-grant · frozen-composition-immutable.
  2. **layer0 retirement:** `layer0/registry/` and `layer0/compose/` absorb into `vanguard/packages/runtime/` at 3.1 (behavioral parity first, SPEC §1), then `layer0/` is deleted. M-3 exit gate reads *"`layer0/` fully deleted."*
  3. **M-5 doc collapse** (T-8) and **M-9 TCB-metric replacement** (§2.9) are scheduled now, executed later.
  4. Wave 3 is **rebalanced** (more sprints), not re-labelled. Shed breadth, never falsifiers.
- **Bound falsifier:** the NOVA-4 six + `test_layer0_fully_deleted_at_M3_gate`.
- **Landing:** Wave 3 (3.1-A…D, 3.2-A…C), M-5 (collapse), M-9 (metric).

---

## 4. Phased Milestone Roadmap & Version Ladder (v0.6.1 → v1.0.0)

Each milestone: goal, entry gate, exit gate (objective evidence), deliverables, scope boundary.

### 4.1 Foundation phase — ends at the STOP LINE

```text
╔══════════════════════════ FOUNDATION PHASE — ends at a STOP LINE ══════════════════════════╗
║  M-0/M-1 · v0.6.0 Concept Lock + Trust Spine                     ✅ COMPLETE (GREEN)       ║
║  M-2     · v0.6.1 Substrate Correction Lock                      🔵 IN FLIGHT (re-gate r4) ║
║  M-3     · v0.6.2 Extensibility Lock                             ⚪ QUEUED                 ║
║  M-4     · v0.6.3 Foundation MVP                                 ⚪ QUEUED  ███ STOP ███   ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝
```

**M-2 — v0.6.1 Substrate Correction Lock** *(in flight — re-gate round 4)*

- **Goal:** One runtime; hollow corpus seized; the `K ≪ N` option bought while cheap.
- **Entry gate:** M-1 green (satisfied).
- **Exit gate:** F-16 green · zero `layer0` imports under `vanguard/` · kill surfaces deleted · reducer folds complete (`EffectFailed`, `EffectRejected`, `BudgetExhausted`, `CapabilityAttenuated`, `TurnStarted`, `Plugin*`×5) · catalogued-AND-folded property test green · **NOVA-1, NOVA-2, NOVA-3 green** · all suites + 9 CI linters green · TCB ≤ 1438.
- **Deliverables:** 2.2-D (linter widening) · ADRs 0077–0082 adopted · F-12 hardened · suspend/resume falsifier · `_PROC_PATTERN` from compiled ceiling.
- **Scope boundary:** no Wave-3 features start before M-2 green.

**M-3 — v0.6.2 Extensibility Lock** *(queued; entry M-2 green — unchanged)*

- **Goal:** Plugin lifecycle real on the canonical path; named component graph live; absent-vs-forged declarable; kernel domain-blind.
- **Entry gate:** M-2 green.
- **Exit gate:** echo plugin walks DISCOVERED→RESOLVED→VERIFIED→ACTIVATED→QUIESCING→RETIRED over UDS with every transition ledgered (ADR-M0-13) · `code-default` loads through the same lifecycle · NOVA-4 six negatives green · component-graph manifest compiles (3.3) · absent-vs-forged schema live (3.4) · I-7 green on the widened surface · **`layer0/` fully deleted**.
- **Deliverables:** registry FSM absorbed into `runtime/registry/` (3.1-A) · compose v2 (3.1-B) · echo plugin + fault injection (3.1-C) · isolation broker rlimits (3.1-D) · code-default toolkits through lifecycle (3.2-A) · coding-token sweep (3.2-B) · one manifest parser (3.2-C) · component graph (3.3-A…D) · guardrail schema (3.4-A…D) · spawn design note (3.5-A/B) + decision (3.5-C).
- **Scope boundary:** `agent.spawn` is DESIGN-only here; kernel gains nothing but tests.

**M-4 — v0.6.3 Foundation MVP** *(queued; entry M-1+M-2+M-3) — **███ STOP LINE ███***

- **Goal:** Nine rows true on **one** uncheated real run.
- **Nine rows:** real model · authorized effect · filesystem change · sandbox · exterior signed eval · WAL ledger · cold replay · schema-valid **populated** trajectory · one runtime.
- **Exit gate:** all nine green on one path, zero human intervention. **Escalate to Director any temptation to widen scope to make the run pass.**
- **Deliverables:** fixture repo + preregistered oracle (4.1-A) · nine-row E2E (4.1-B) · cassette of the green run (4.1-C) · evidence bundle (4.1-D) · NOVA-5 confirms NOVA-1 (4.1-E).
- **Package version cut:** `0.4.5b1` → `0.6.3` **at this gate** (Director-only decision).
- **Scope boundary:** `agent.spawn` implementation, concurrency, Pack #2, and all of M-5…M-10 stay out until this gate is green.

### 4.2 Macro generality & meta-cognition phase — outcomes only

```text
╔══════════════════ MACRO GENERALITY & META-COGNITION PHASE — outcomes only ═════════════════╗
║  M-5  · v0.7.0 Generality Proof (Pack #2 Math + doc collapse)          deps: M-4          ║
║  M-6  · v0.8.0 Mediated Delegation (agent.spawn)                       deps: M-5 + 3.5-C  ║
║  M-7  · v0.8.0 Controlled Concurrency                                  deps: M-5, M-6     ║
║  M-8  · v0.9.0 Framework Builder Abstraction                           deps: M-6, M-7     ║
║  M-9  · v0.9.0 High-Performance Orchestration                          deps: M-7, M-8     ║
║  M-10 · v1.0.0 Meta-Cognitive Substrate (FINAL)                        deps: M-8, M-9     ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝
```

**M-5 — v0.7.0 Generality Proof & Consolidation** *(deps M-4)*

- **Goal:** Prove domain-blindness is a **fact, not a thesis**; collapse governance.
- **Pack #2 = Math & Formal Deductive Verification** (the Leadership 7 names it precisely, per the brief's mandate): toolkits for proof-checking (e.g. Lean/Coq proof verification, SAT/SMT solving, or a symbolic-algebra DSL), oracle suites that judge *deductive validity* rather than *test passage*, manifest defaults, and a selector vocabulary (`kind: proof`, `kind: theory`, `kind: statement`). This is a genuine non-coding domain — the strongest possible I-7 probe, since it exercises compute-only effects and an evidence plane that judges provability, not compilation.
- **Exit gate (I-7 gate):** **zero diffs under `domain/` and `kernel/`** for Pack #2 · trajectory-parity assertion (Pack #2 emits the same rich `mhf.trajectory/1` rows) · suspend/resume cold-reconstruction falsifier passes at scale · doc collapse to SPEC + ADR log + one board (GAMMA and `002` retired as standing authorities).
- **Deliverables:** 5.1-A/B/C (collapse) · 5.2-A/B/C (Pack #2 + I-7 gate) · 5.3-A/B/C (selector-soundness measurement, I-11 gate naming).

**M-6 — v0.8.0 Mediated Delegation** *(deps M-5 + 3.5-C)*

- **Goal:** `agent.spawn` as a capability-mediated kernel verb.
- **Exit gate:** planner without a spawn grant cannot delegate · child stays monotonically attenuated · spawn recorded as a mediated effect with a receipt.
- **Validation cases:** hierarchical decomposition (6.2-A) · tree search — expansion/scoring/selection as separate components (6.2-B).

**M-7 — v0.8.0 Controlled Concurrency** *(deps M-5, M-6)*

- **Goal:** Independence groups for non-intersecting selectors; `K ≪ N` logical-vs-worker separation; async/event-driven scheduler prototype.
- **Exit gate:** selector-disjointness measurement · zero event loss under backpressure · NOVA-2 at scale. **I-11 stands until this gate fires.**

**M-8 — v0.9.0 Framework Builder Abstraction** *(deps M-6, M-7)*

- **Goal:** Debate · critic/revisor · evolutionary search · multi-agent delegation composed **declaratively** over the component graph.
- **Exit gate:** reference suites run multi-pack **without engine modification**; three packs (coding + Math + one more) side-by-side, zero core diffs.

**M-9 — v0.9.0 High-Performance Orchestration** *(deps M-7, M-8)*

- **Goal:** Measured IPC/serialization/plugin-call overhead; bounded ledger pressure.
- **Exit gate:** measured overhead under bound · `project_id` sharding validated · **five-SPI freeze revisited** (9.2-B) · **TCB replacement metric built** (§2.9).

**M-10 — v1.0.0 Meta-Cognitive Substrate (FINAL)** *(deps M-8, M-9)*

- **Goal:** Outer-loop planner at the `outer` slot, capability-restricted to manifest-mutation / skill-write / oracle-preregistration (never workspace) · harvest → distill → promote as a permanent process.
- **Final gate:** the system proposes, verifies, and promotes an improved version of its own composition — the whole chain attributable via `D_H`/`D_R`/`D_X` and signed verdicts, on a corpus whose evidence was never forgeable.

### 4.3 The M-4 Foundation Stop Line — exact terms

- **Nine rows** (§4.1), one run, zero cheating. "Cheating" includes: stubbing the planner, ADVISORY-only effects, pre-seeded verdicts, MemoryLedger, in-memory replay posing as cold replay.
- **Escalation rule:** any scope widening to make the run pass goes to the Director *before* it is attempted.
- **Release cut:** package version `0.4.5b1` → `0.6.3` at this gate.

---

## 5. Theories, Algorithms & Mathematical Equations

> All of §5 is **exterior, domain-blind, promotion-gated policy** for M-10 — never a kernel primitive. It is formalized now so M-10 implements against accepted equations, not equations invented under pressure. Metaphysics stays out (ADR-M0-10).

### 5.1 Active Inference: Variational Free Energy over the 6D Economic Tensor R

The meta-cognitive tuning of a harness configuration $\theta \in \Theta$ (tokens, turns, model_tier, repair_rounds, planner_strategy) is posed as **Variational Free Energy (VFE) minimization** bounded by the 6D economic tensor $\mathbf{R}$:

$$\theta^* = \arg\min_{\theta \in \Theta} \mathcal{F}(\theta) \quad \text{s.t.} \quad \text{Cost}(\theta) \le \mathbf{R}_{\max}$$

where $\mathbf{R} = (\mathbf{R}_{\text{additive}}, \mathbf{R}_{\text{structural}})$ with additive dimensions $\{usd\_micros,\ tokens,\ bytes,\ millis\}$ (conserved by the governor — `kernel/budget.py`, verified) and structural ceilings $\{depth,\ turns\}$ (enforced by attenuation and the episode loop, **not summed across siblings** — the F-10 defect). The free energy decomposes:

$$\mathcal{F}(\theta) = \underbrace{D_{\mathrm{KL}}\big[q(\phi\mid\tau)\,\|\,p(\phi)\big]}_{\text{epistemic uncertainty}} - \underbrace{\mathbb{E}_{q(\phi\mid\tau)}\big[\ln p(Y=1\mid\tau,\theta)\big]}_{\text{pragmatic success likelihood}} + \lambda\!\!\sum_{d\in\{\$,t,k,b\}}\!\frac{R_d(\theta)}{R_{\max,d}}$$

- $q(\phi\mid\tau)$ is the variational posterior over a task's latent difficulty, conditioned on the trajectory $\tau$; $p(\phi)$ the prior.
- The KL term drives **information gain** (epistemic value); the expectation term drives **task completion** (pragmatic value); the third term is the cost regularizer, and it is **only defined when the corpus rows carry non-zero per-turn cost** — which is precisely why NOVA-1 (§2.4) is the plan's first action.
- The constraint `Cost(θ) ≤ R_max` is enforced **by the governor, not by the optimizer**: the mutation is *proposed* as a manifest change, then *verified* at compose against the ceiling, exactly like any other composition.

**Mutation transition rules** (failure-class → manifest change, all JCS-differentiable fields):

1. Context overflow ($E_{\text{OOM}}$): $\text{tokens}_{\text{new}} = \min\left(\lceil \text{tokens}_{\text{curr}}(1+\alpha)\rceil,\ \mathbf{R}_{\text{tokens,max}}\right),\ \alpha=0.5$.
2. Repair oscillation ($E_{\text{osc}}$): $\text{planner\_strategy}_{\text{new}} = \text{TreeSearch};\ \text{repair\_rounds}_{\text{new}} = \text{repair\_rounds}_{\text{curr}} + 2$.
3. Capability deficit ($E_{\text{cx}}$): $\text{tier}_{\text{new}} = \min(\text{tier}_{\text{curr}}+1,\ \text{tier}_{\max})$.

### 5.2 Trajectory Error Credit Assignment — Backward Fault Isolation

An episode trajectory $\tau$ of horizon $T$ is the immutable event ledger:

$$\tau = \big((s_0,a_0,r_0),\dots,(s_T,a_T,r_T)\big),\quad s_t\in\mathcal{S}\ (\text{context digest}),\ a_t\in\mathcal{A}\ (\text{effect verb}),\ r_t\in\mathcal{R}\ (\text{kernel receipt})$$

The terminal outcome $Y(\tau)\in\{0,1\}$ is decided **strictly** by the exterior oracle $\mathcal{O}_{\text{exterior}}$. The counterfactual causal contribution of turn $t$:

$$\mathcal{C}(a_t) = \Delta\mathbb{E}_{\mathcal{O}}\big[Y(\tau)\mid \mathrm{do}(a_t=a_{\text{null}})\big] + \lambda_{\text{cost}}\cdot\frac{\text{Tokens}(a_t)}{\sum_{k=0}^{T}\text{Tokens}(a_k)}$$

**Gradient-free backward fault-isolation algorithm:**

1. **Backward scan** the ledger $t = T \to 0$.
2. **First invariant violation:** locate the earliest $t^*$ where a non-zero exit code or `AuthorizationDenied` / `EffectFailed` / `BudgetExhausted` is recorded in a folded receipt.
3. **AST/effect-delta attribution:** if a syntactic/semantic error is detected at $t^*$, assign failure weight $W_f(t) = \gamma^{T-t}$ to the most recent `patch.apply` preceding $t^*$.

This runs **over the folded ledger state** — never over the live process — so it is replayable and attributable via `D_R`.

### 5.3 Dense 384-d Hybrid Semantic-Lexical Retrieval & Elo-Decayed Skill Eviction

Each synthesized skill card $S_i = (\mathbf{v}_i, \text{Pattern}_i, \text{Procedure}_i, E_i, t_{\text{created}}, t_{\text{last\_used}})$ with $\mathbf{v}_i \in \mathbb{R}^{384}$ (dense embedding over error signature + context prompt).

**Retrieval score** (hybrid, combining dense + sparse + utility):

$$\text{Score}(S_i,\mathbf{q},K_q) = \alpha\cdot\frac{\mathbf{q}\cdot\mathbf{v}_i}{\|\mathbf{q}\|\|\mathbf{v}_i\|} + (1-\alpha)\cdot\text{BM25}(K_q,\text{Pattern}_i) + \beta\cdot\sigma(E_i),\qquad \sigma(E_i)=\frac{1}{1+e^{-E_i/400}}$$

**Elo dynamics** (K-factor updates on signed outcomes):

- Green ($Y=1$): $E_{t+1} = E_t + K\,(1-\sigma(E_t-\bar{E}))$.
- Red ($Y=0$): $E_{t+1} = E_t - K\,\sigma(E_t-\bar{E})$.
- **Forgetting curve:** $E(t) = E_0\,e^{-\lambda_{\text{decay}}(t-t_{\text{last\_used}})}$.

**Eviction criterion:** evict to cold storage when $E_i < E_{\text{evict}} = 1000$ (baseline $1200$) or unused $\Delta t > 30$ days. Cards enter the active cache **only** via the §5.4 promotion pipeline — retrieval never self-promotes.

### 5.4 Unforgeable DPO Preference Harvesting & Paired McNemar Promotion

The learning loop (from `RESEARCH_k3_harness-suggestion.md` §5, made rigorous):

```
harvest signed trajectories (rich rows: cost / fingerprint / signed verdict)
        ↓
distill DPO pairs (chosen vs. rejected by turn-prefix within a fixed (task_digest, harness_digest))
        ↓
paired McNemar vs. undeletable baseline (χ² ≥ 3.841, p < 0.05, N ≥ 50)
        ↓
signed promotion pointer flips the registry default (new D_H, never in-place)
        ↓
cassette-replay regression in the lab → human promotion gate
```

**Unforgeability, by construction:** (1) verdicts are exterior-signed (UID 10002, Ed25519, nonce-bound); (2) `D_H`/`D_R`/`D_X` never collapse, so a preference pair is always attributed to the correct denominators; (3) promotion flips a **pointer** — production never mutates in-place; (4) the harvester **consumes** the corpus, never drives it.

**Paired McNemar exact promotion protocol** (Mill's Canon of Difference; `docs/04_annex/MEASUREMENT.md`):

$$\chi^2 = \frac{\big(|n_{10}-n_{01}| - 1\big)^2}{n_{10}+n_{01}}$$

- $n_{10}$: tasks where candidate **B** passed and baseline **A** failed. $n_{01}$: the reverse.
- **PROMOTE iff** $\chi^2 \ge 3.841$ ($\alpha=0.05$, 1 df) **and** $n_{10} > n_{01}$ (positive net lift) **and** power $(1-\beta) \ge 0.80$ over $N \ge 50$ held-out tasks.
- The baseline is **undeletable** (a standing composition pointer that cannot be retired), so the test can never be gamed by removing the control.

---

## 6. Zero-Guesswork Developer Implementation Bridge

### 6.1 Normative Draft — `mhf.manifest/2` (JSON Schema 2020-12)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aether.dev/schemas/mhf/manifest/2",
  "title": "mhf.manifest/2 — Named Component Graph",
  "type": "object",
  "required": ["api", "id", "components", "bindings", "budget"],
  "additionalProperties": false,
  "properties": {
    "api": { "const": "mhf.manifest/2" },
    "id": { "type": "string", "pattern": "^[a-z0-9][a-z0-9-]{0,63}$" },
    "components": {
      "type": "object",
      "minProperties": 1,
      "additionalProperties": {
        "type": "object",
        "required": ["spi", "ref"],
        "properties": {
          "spi": { "enum": ["planner", "context", "memory", "toolkit", "evaluation"] },
          "ref": { "type": "string" },
          "config": { "type": "object" },
          "capabilities": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["verb", "selector"],
              "properties": {
                "verb": { "type": "string" },
                "selector": { "type": "object" }
              }
            }
          },
          "ceiling": { "$ref": "#/$defs/capabilityCeiling" }
        }
      }
    },
    "bindings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from", "to", "role"],
        "properties": {
          "from": { "type": "string" },
          "to": { "type": "string" },
          "role": {
            "enum": ["propose", "expand", "score", "select", "critic", "revise", "aggregate", "observe"]
          }
        }
      }
    },
    "model_routes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["tier", "provider", "model"],
        "properties": {
          "tier": { "type": "integer", "minimum": 1 },
          "provider": { "type": "string" },
          "model": { "type": "string" },
          "escalate_on": { "type": "array", "items": { "type": "string" } }
        }
      }
    },
    "system_prompt": { "type": "string" },
    "budget": {
      "type": "object",
      "required": ["usd_micros", "tokens", "bytes", "millis", "turns", "depth"],
      "properties": {
        "usd_micros": { "type": "integer", "minimum": 0 },
        "tokens":     { "type": "integer", "minimum": 0 },
        "bytes":      { "type": "integer", "minimum": 0 },
        "millis":     { "type": "integer", "minimum": 0 },
        "turns":      { "type": "integer", "minimum": 0 },
        "depth":      { "type": "integer", "minimum": 0 }
      }
    },
    "approval_policy": { "type": "string" },
    "guardrails": {
      "type": "object",
      "properties": {
        "evaluation": { "type": ["string", "null"], "default": null },
        "sandbox_tier": { "type": ["string", "null"], "default": null },
        "approval": { "type": ["string", "null"], "default": null }
      }
    },
    "undeletable": { "type": "boolean", "default": false }
  },
  "$defs": {
    "capabilityCeiling": {
      "type": "object",
      "description": "Fail-closed. Empty ceiling denies everything (F-07).",
      "properties": { "verbs": { "type": "array", "items": { "type": "string" } } }
    }
  }
}
```

**Migration note:** `packs/code-default/harness.yaml` migrates mechanically — its five slots become `components` entries (`planner` → component named `main` of `spi: planner`), `toolkits` become four toolkit components, `model_routes`/`budget`/`capabilities`/`approval_policy` are unchanged in position. `D_H` is computed over the JCS-canonical graph; `gene_digests` name each component.

### 6.2 Plugin Lifecycle Finite State Machine — full table with ledger events

States (ADR-M0-13 walking-skeleton walk) and their ledger events (EVENT_KINDS, 56 kinds, verified):

| # | State | Entry trigger | Exit → | Ledger event emitted on transition | Emitter (writer authority) |
|---|---|---|---|---|---|
| 0 | `DISCOVERED` | registry scan finds a manifest | `RESOLVED` | `PluginResolved` | registry (sole `Plugin*` writer) |
| 1 | `RESOLVED` | ref resolved, schema+signature verified, ceiling intersected | `VERIFIED` | *(verification folded into `PluginResolved` payload: `verified: true`)* | registry |
| 2 | `VERIFIED` | verification gate passed; not yet active | `ACTIVATED` | `PluginActivated` | registry |
| 3 | `ACTIVATED` | cell instantiated over the wire | `QUIESCING` / `FAULTED` | `PluginQuiesced` / `PluginFaulted` | registry |
| 4 | `QUIESCING` | drain in-flight calls, refuse new | `RETIRED` | `PluginRetired` | registry |
| 5 | `RETIRED` | terminal | — | *(no further event)* | — |
| ✗ | `FAULTED` | any active state hits an uncaught cell fault | *(retry → ACTIVATED, else RETIRED)* | `PluginFaulted` | registry |

**Invariants the FSM must preserve (NOVA-4, §2.5/§2.7):**

- **Registry exclusivity:** only the registry may append `Plugin*` kinds — enforced by `PRIVILEGED_KIND_OWNERS` in `runtime/ledger_emitter.py` (single-writer, ADR-0076).
- **Unknown-ref fails at compose, never at runtime:** `RESOLVED` is a compose-time state; an unresolved ref never reaches `ACTIVATED`.
- **Empty ceiling denies:** a component whose intersected ceiling is empty is denied at `VERIFIED` (fail-closed, F-07).
- **Faulted cell cannot stay active:** `FAULTED` is not a resting state on the active path; a fault forces `QUIESCING`→`RETIRED` or a bounded retry to `ACTIVATED`.
- **`in_process` requires explicit grant:** the in-process cell is a policy-granted privilege that *still speaks the wire* (ADR-0072); it never bypasses S0–S12.
- **Frozen composition immutable:** no code path mutates a `FrozenHarness` after freeze; the graph and `D_H` are fixed at compose.

### 6.3 1-to-1 executable falsifier matrix

| Requirement / Invariant | Falsifier (test function) | File | Wave |
|---|---|---|---|
| Envelope lineage (I-2) | `test_every_emitted_envelope_carries_full_lineage` | test/falsifiers/ | 1 (done) |
| `State = fold(events)` from disk (I-4) | `ColdReplayParity.test_cold_reader_reconstructs_live_state_from_disk` | test/runtime/test_ledger_truth.py | 0/1 (done) |
| Evaluator exteriority (I-5) | `test_scheduler_cannot_produce_a_verdict_without_a_signature` | test/falsifiers/ | 1 (done) |
| Verdict binding | `test_replayed_or_unbound_signature_is_rejected` | test/falsifiers/ | 1 (done) |
| Writer authority | `test_orchestrator_cannot_append_privileged_kinds` | test/falsifiers/ | 1 (done) |
| Capability ceiling | `test_declared_ceiling_survives_compilation_and_denies` | test/falsifiers/ | 1 (done) |
| Fail-closed authority | `test_empty_ceiling_denies_everything` | test/falsifiers/ | 1 (done) |
| Spawn attenuation | `test_child_grant_wider_than_parent_is_denied_whole` | test/falsifiers/ | 1 (done) |
| Depth algebra (F-10) | `test_sibling_depths_are_not_summed` | test/kernel/ | 1 (done) |
| `D_H` completeness | `test_prompt_or_ceiling_change_changes_digest` | test/falsifiers/ | 1 (done) |
| **Trajectory content (NOVA-1)** | `test_episode_completed_emits_populated_trajectory` | test/runtime/ | **2 (M-2)** |
| **Suspend/resume (NOVA-2)** | `test_suspend_midturn_cold_reconstruct_resume_completes` | test/runtime/ | **2 (M-2)** |
| **`_PROC_PATTERN` (NOVA-3)** | `test_proc_pattern_reads_compiled_ceiling` | test/adapters/ | **2 (M-2)** |
| Component graph (T-1) | `test_component_graph_expresses_two_planners` + `test_slot_names_are_convention` | test/packs/ | 3 (M-3) |
| Absent-vs-forged (T-3) | `test_unsigned_verdict_illegal_under_any_composition` + `test_declared_absence_is_recorded` | test/contracts/ | 3 (M-3) |
| Lifecycle negatives (NOVA-4) | `test_unknown_ref_fails_at_compose` · `test_empty_ceiling_denies` · `test_registry_exclusive_plugin_write` · `test_faulted_cell_cannot_stay_active` · `test_in_process_requires_explicit_grant` · `test_frozen_composition_immutable` | test/registry/ | 3 (M-3) |
| layer0 retirement | `test_layer0_fully_deleted_at_M3_gate` | (CI step) | 3 (M-3) |
| `agent.spawn` (T-2, sketch) | `test_planner_without_spawn_grant_cannot_delegate` · `test_child_stays_monotonically_attenuated` · `test_spawn_recorded_as_mediated_effect_with_receipt` | test/kernel/ | 6 (M-6) |
| Pack #2 generality (I-7 gate) | `test_pack2_zero_diffs_under_domain_and_kernel` + `test_pack2_trajectory_parity` | test/packs/ | 5 (M-5) |
| Loop-as-mechanism (T-6) | (bound claim, 12-month window; reversal-evidence protocol) | ADR-0080 | 3 (M-3) |

### 6.4 Negative constraints & anti-patterns checklist

- **TCB budget:** nothing added to `vanguard/packages/kernel/` in Waves 1–4 except tests; logical LOC ≤ 1438 (currently 1365). Kernel change during Wave 4 is a halt condition.
- **Domain blindness (I-7):** no `coding|pytest|ast` tokens in `packages/{domain,kernel}`; `check_domain_blindness.py` scans both `layer0/` and `vanguard/packages/{domain,kernel}` (F-18).
- **Single writer:** `LedgerEmitter` is the sole authorized ledger writer; `evaluator_gateway` the sole `VerdictRecorded` writer; registry the sole `Plugin*` writer.
- **No duplicate surface:** a second selector algebra, second canonicalisation, or second manifest parser fails the build (`check_duplication.py --enforce`).
- **Generated-or-normative, never both (I-8):** `types_gen.py` is generated; hand-editing fails CI (`generate_types.py --check`, F-13).
- **No forged pass:** any path that emits `VerdictRecorded{verdict:"pass"}` without a bound Ed25519 signature is a defect (F1, dead).
- **No live-object replay:** cold replay must fold from the WAL file in a fresh process, never the same in-memory list twice (I-4, F-02).
- **No float money:** budget is integer micro-units and integer millis; no float anywhere in `budget.py` (verified).
- **Refusal list (SPEC §9) stays closed:** no self-updating release pipeline · no competence-graph pretence · no parallel fan-out before independence is measurable · no second wire contract · no metaphysical taxonomy · no playbook `strict` DAG · MCP is configuration/adapter only · no GUI/TUI backend gate · no scalar reward for promotion · no always-on full-content capture · no third runtime tree · no swarm/workflow/graph-DB engine · no byte-identical concurrent ledger as general law · no mid-run hot-swap · no evaluator-as-product-plugin · no Rust TCB / WASM-default / multi-host in v0.6 · no Meta-Harness in v0.6 · no Skill/Task/Orchestrator-as-engine/Experiment/Promotion as substrate primitives.

---

## 7. Repository Hygiene & Document Update Cascade

> Per the strict anti-sprawl invariant (AGENTS.md §7, Clean Triad), this review creates **no** new documentation files beyond this single root-level report, edits **no** SPEC/ADR/source, and issues only the following **directives** to be applied by their normal processes.

### 7.1 Stale artifact cleanup

| Artifact | Action | Owner |
|---|---|---|
| `DELETE.md` (0 bytes at root) | Delete. It is a zero-byte scratch file with no content; its existence is D-F. | hygiene |
| `docs/06_references/RESEARCH_THEORETICAL_SYNTHESIS_B.md` | Delete (duplicate of `RESEARCH_THEORETICAL_SYNTHESIS.md`, same `id: REF-06-M5`) — at M-5. | M-5 |
| `docs/06_references/vanguard_body_detailed.md` | Retire or relocate out of `docs/` (conflicts with ADR-M0-10/REJ-10). | M-5 (Director) |
| `docs/08_workflows/` (empty) | Remove the empty directory (D-E). | hygiene |
| `docs/03_sprints/plans/000_CANONICAL_EXECUTION_PATH.md` citation | It does not exist (D-A). Replace all citations in `005`/`proposal_glm_harness_BETA.md` with the real source (`SYSTEM_OVERVIEW.md` §2/§3). | M-5 |

### 7.2 Section-by-section diff directives

These are **directives**, not edits — apply via the ADR adoption process and normal board maintenance.

**`docs/SPEC.md`:**
- §2.3 (manifest/composition): replace the fixed-slot description with the named component graph; cross-reference ADR-0077 and `mhf.manifest/2`.
- §9 (refusal list): no change — the component graph, absent-vs-forged, and `agent.spawn`-as-verb do **not** reopen any refusal. Confirm the seven non-negotiables (§2.3) are stated.
- Version anchor: note v0.6.1 = Substrate Correction Lock (ADRs 0077–0082).
- Invariants: F-12 strengthened to content assertions (I-9); NOVA-2 added as the I-11 measurement-gate precondition.

**`docs/02_roadmap/milestones.md`:**
- M-2 exit gate: add NOVA-1/2/3.
- M-3: add 3.3 (component graph), 3.4 (absent-vs-forged), 3.5 (spawn design), NOVA-4, and `layer0/` full deletion.
- M-4: name NOVA-5; keep the nine rows and the stop line unchanged.
- M-5: Pack #2 = **Math & Formal Deductive Verification**; add trajectory-parity assertion and doc-collapse.
- Version ladder: ratify v0.6.1/v0.6.2/v0.6.3/v0.7.0/v0.8.0/v0.9.0/v1.0.0 (§0).

**`docs/03_sprints/sprint_active.md`:**
- Resolve the NOVA-1 timing contradiction (D-C): trajectory cost lands in **M-2**, not Wave 4. Update the Wave-1 follow-up row.
- 3.1-D, 3.3, 3.4, 3.5, NOVA-4, NOVA-2-at-scale rows: mark readiness per §4.1.
- Decision queue: add "release cut at M-4 gate" and "Pack #2 domain = Math & Formal Deductive Verification."

**Wave plans:**
- `wave3_extensibility.md`: add the NOVA-4 negatives, component-graph design, absent-vs-forged schema, spawn design note.
- `wave4_foundation_e2e.md`: add NOVA-5 (confirm rich trajectory on the real run); re-assert the stop line.

### 7.3 What v0.6.1 locks that v0.6.0 did not

v0.6.1 (ADRs 0077–0082) makes binding: (1) the named component graph as the composition surface; (2) the absent-vs-forged guardrail model with seven permanent non-negotiables; (3) `agent.spawn` as a designed, deferred kernel verb; (4) the universal-turn-loop claim with its falsifier; (5) the corpus-seizure mandate (NOVA-1/2/3 + F-12 hardening); (6) Wave-3 rebalancing (NOVA-4) and layer0 retirement with the M-5/M-9 scheduling decisions. **Wave 4's stop condition and scope are unchanged.**

---

*Advisory only. This document amends nothing. Law remains `docs/SPEC.md` → `docs/05_adr/` → `docs/04_annex/`. Each determination becomes binding only through adoption of ADRs `0077`–`0082` by the append-only process, each carrying a bound falsifier. Prepared by the Leadership 7 against baseline `main` @ `733855b`, with the hollow-trajectory defect and S0–S12 dispatch stages re-verified on disk.*

---

# Alternative Approach

**A different solution to the same goal — the meta-framework as an informational-flow controller.** *(Briefing only; no implementation detail.)*

## 1. The north star: result + data, not a substrate

The alternative is not "the same architecture in a different language." It is a different solution with a different center of gravity: a **meta-framework whose product is outcomes and whose byproduct is compounding data.** Success is measured along three knobs — **cost, tokens, time** — each independently optimizable, or held in deliberate balance. The language and the isolation mechanism are implementation details and are deliberately out of scope here: what matters is that the framework can *tune the trade-off*, run-to-run, per task class, without changing primitives.

## 2. The core insight: control the harness ⇒ control informational flow

If you own the meta-framework **and** the harness, you control *what information reaches the model at every step*: the prompt, the context window, the tools exposed, the memory injected, the model route, when to stop, when to spawn, when to escalate, when to reflect. Each configuration is a distinct **informational regime**; each regime produces a distinct *behaviour* from the same primitives.

> One primitive set ⇒ many agent shapes. A coding-CLI behaviour, a deep-research behaviour, a swarm behaviour — all are configurations, not products. It is *"claude code cli and hermes, together, on steroids, with swarming"*: one factory that emits many behaviours instead of one fixed agent.

This is the concrete meaning of "harness as the independent variable." A coding harness CLI is one frozen informational-flow configuration. The meta-framework is the **space of all such configurations**, plus the machinery to measure which one wins on which task.

## 3. Higher-order abstraction + data beats single-agent CLIs

- **Higher-order abstraction:** strategies (planner, critic, verifier, router, escalation policy) are *composed as data* — a declarative component graph — rather than baked into code. Debating, tree-searching, critiquing, swarming are all *topologies over the same primitives*, named in configuration.
- **Data:** every run is a learnable trace (per-turn cost, model fingerprint, signed verdict). This is what lets the framework answer, with measurement rather than taste, "which composition is cheapest / fastest / most reliable for this task class?"
- **Generality from the same primitives:** because the primitives are domain-blind, the same factory that closes coding tasks also closes math, data, and research tasks — *effectively*, because the informational-flow control and the measurement layer don't care what the task is about.

This is how it both *outperforms* single-agent CLIs (it optimizes the configuration they hard-code) and *generalizes* beyond them (it is not shaped like the first use case).

## 4. The flywheel — how result and data compound

1. **Rich corpus:** signed trajectories with real per-turn cost and verdict, from the first run.
2. **Measurable strategy selection:** compute `P(pass | action, context)` and `E[tokens | action]`; pick the cheapest strategy that still passes.
3. **Skill retrieval:** solved-task patterns are recalled and injected, so similar tasks skip the expensive search.
4. **Distillation:** the base policy improves on measured chosen/rejected pairs.
5. **Meta-cognitive control:** the outer loop mutates the *composition* (planner, tools, routes) to minimize cost/tokens/time subject to bounded authority.

Each solved task lowers the expected cost of the next. **Data is not a byproduct — it is the product.** A swarm is just the flywheel running at higher parallelism: orchestrator / worker / critic / verifier coordinated **stigmergically** through a shared log (never O(N²) chatter), with each role's *marginal contribution* measured so the topology itself is tunable.

## 5. What must stay principled (survives any implementation)

The differentiator is *not* speed or surface. It is that the data is **trustworthy and un-gameable by construction**:

- **Separability** — an exterior, unreachable judge; what solved it is separable from what graded it.
- **Three planes** — decision / state / evidence, never collapsed into one execution object.
- **Identity trinity** — composition ≠ run ≠ experiment; the denominators of measurement never collapse.
- **Absent-vs-forged** — you may turn a guardrail off, never the record that it was off; an unsigned verdict stays illegal.
- **Bounded solvers** — monotonic attenuation; delegation never widens capability or budget.

These are the reason a SOTA alternative that adopts "no privileged core / everything-is-a-plugin" forfeits the one thing that makes its data usable for self-improvement. The alternative approach keeps a *small non-negotiable core* — only the mechanism differs.

## 6. Trade-offs vs. the vanguard path

| | This alternative | The vanguard path |
|---|---|---|
| Center of gravity | Result + data flywheel, informational-flow control first | Verified trust spine first, then surface |
| Primary abstraction | "Which configuration produces this behaviour, and how do I measure it?" | "What is the minimal authority boundary, and how do I prove it?" |
| Advantage | Outcome/optimization story is native from day one | The trust spine and corpus already exist and are verified |
| Risk | Re-deriving a trustworthy judge + ledger; corpus cold-start | Reaching the outcome story *through* the verification discipline |

## 7. Honest recommendation

Both roads converge on the same principles — separability, three planes, identity trinity, absent-vs-forged, bounded solvers, component graph. The alternative's genuine contribution is the **result/data flywheel and informational-flow control as the primary abstraction**, not any substrate or language choice. That abstraction is the map to follow if we ever re-center the project on *outcomes first* rather than *verification first*; the vanguard path remains the one that already holds the trust spine that the flywheel needs in order to trust its own data.
