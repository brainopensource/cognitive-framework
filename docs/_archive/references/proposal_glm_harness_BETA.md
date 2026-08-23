# GLM Review — v0.6.1 BETA

**Classification:** Independent advisory review (external model assessment).
**Subject:** Can AETHER reach its stated goal — *a universal operating substrate and framework for building verifiably grounded, autonomous task-solving agents*, structured in three evolutionary layers — on the current v0.6.1 BETA trajectory?
**Evidence base:** `docs/SPEC.md` (v0.6.0 Concept Lock); ADRs `0069`–`0076` (+ ADR-M0 namespace via `docs/05_adr/INDEX.md`); `docs/03_sprints/plans/000_CANONICAL_EXECUTION_PATH.md`; `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/005` (Substrate Generality Review), `004` (v0.6.1 Alignment Roadmap), `006` (substrate briefing); `sprint_active.md`; wave plans 1–4; live repository state at commit `83b5009` (verified on disk, listed in §5); reference research corpus under `docs/06_references/RESEARCH_*` (treated as **input, not law**, per the review mandate).
**Status:** Advisory. Does not amend SPEC or any ADR. Where it agrees with `005`/`004` it says so rather than restating; where it adds or diverges, it is marked **[GLM]**.

---

## 0. Verdict first

**The goal is reachable on this trajectory, and the parts of the goal that are hardest to reverse are already built correctly. The parts that remain are mostly surface, sequencing, and one verified data-quality defect that would quietly poison the entire third layer if it survives to production.**

The three-layer vision maps cleanly onto the programme:

| Vision layer | Programme mapping | State (verified) |
|---|---|---|
| **1. Foundation** — Decision/State/Evidence separation, domain-blind capability microkernel, rootless sandboxes, 6D resource leases | Waves 0–2 (M-0 CI truth, M-1 trust spine, M-2 convergence) | **M-0 and M-1 green; M-2 at closing gate** (`layer0/` shrunk to `compose/` + `registry/` only; `root.py` split landed; CI runs `test/kernel` as subject of record) |
| **2. Proving Ground & Universal Abstraction** — coding agent `vg` as stress-test; declarative manifests for any domain, zero core changes | Waves 3–4 (M-3 extensibility, M-4 Foundation E2E) + M-5 (Pack #2 generality gate) | **Half-built.** The coding pack exists (`packs/code-default`), but the plugin lifecycle has never run on the canonical path, the manifest is a fixed-slot template, and domain-generality is declared, not demonstrated |
| **3. High-Order Emergence & Self-Improvement** — stigmergic swarms, dual-process reflex, continuous learning | M-6 through M-10 (deliberately blocked post-M-4) | **Correctly deferred.** The identity architecture (`D_H`/`D_R`/`D_X`) and signed-verdict evidence plane that make this layer *possible without cheating* are locked and mostly wired. The dataset this layer will learn from is currently **born hollow** (§4.3, verified on disk) |

Two headline findings **[GLM]**:

1. **The Foundation is stronger than the vision's own vocabulary.** The vision speaks of "thermodynamic" leases and "emergence"; the law speaks of typed budget algebra (additive `{usd_micros, tokens, bytes, charged millis}` vs structural `{depth, turns}`, ADR-0074 §2) and projections of events (ADR-0070). That translation is exact and correct — and the discipline that keeps vision language out of normative documents (ADR-M0-10) is itself one of the project's strengths. The vision is safe *as a vision* precisely because the law refuses to be the vision.
2. **The single highest-leverage defect open today is not architectural.** `vanguard/packages/runtime/trajectory.py` still emits a hard-coded `_ZERO_COST` vector (verified: lines 53 and 75). Every episode completed before F-12/NOVA-1 hardening lands produces a schema-valid, cryptographically attributable, and **unusable** training row. The third layer of the vision — skill cards, DPO, calibrated escalation (SPEC §5.3, §7) — is *undefined* without per-turn cost, model fingerprint, and embedded verdict. This is the exact failure shape I-9 was written to prevent, and it is live on the canonical path today.

---

## 1. What the goal requires, restated operationally

The review mandate says: the vision statement is the only rule; the `RESEARCH_*` corpus is suggestion. Restating the vision as falsifiable engineering claims:

- **G1 (Grounded):** No execution may grade itself; every capability claim must trace to an exterior, signed, request-bound verdict. → Separability thesis; `SignedVerdict` binding fields (ADR-0076 §5); `VerdictRecorded` gateway-only writer (ADR-0074 §3).
- **G2 (Autonomous):** Agents must operate under bounded resources with monotonic authority — no unbounded delegation, no capability widening, no forged history. → S0–S12 reference monitor, attenuation, typed budget algebra, writer authority, `State = fold(events)` with cold replay (I-4).
- **G3 (Universal):** A new domain (Math, Data Science, Security, Research) must arrive as data — manifests, plugins, oracles — with **zero diffs under `domain/` and `kernel/`**. → Invariant I-7, gated on Pack #2 at M-5.
- **G4 (Task-solving, at scale):** Many logical agents over bounded physical resources; coordination that does not cost O(N²) tokens; sub-100ms reflexes alongside frontier deliberation. → `spawn` as sole primitive; swarm-as-policy; `project_id` sharding; sequential-until-measured (I-11); model routes inside `D_H`.
- **G5 (Self-improving, safely):** The system harvests its own signed trajectories into skills and fine-tuning data, and improves *only* through a promotion pipeline it cannot drive itself. → SPEC §5/§7 deferred blueprints; M-10; ADR-0073 deferral register; human-promotion discipline.

## 2. Layer 1 — Foundation: built, and built right

**Assessment: the Foundation layer is essentially delivered.** Verified on disk and in the board:

- **Three planes are real, not aspirational.** `LedgerEmitter` (`runtime/ledger_emitter.py`, 331 LOC) is the single writer construction point; `evaluator_gateway.py` exists as the sole legal `VerdictRecorded` writer; `ColdReplayParity` in `test/runtime/test_ledger_truth.py` folds from a real WAL file in a fresh process — the strong version of I-4 (ADR-0071's replay taxonomy is honoured: the tautological same-list fold was deleted, per the Wave-1 adjudication in `sprint_active.md`).
- **One algebra, one canonicalisation, one wire.** ADR-0076 §2/§3 settled the dual-artifact ambiguities; the Wave-2 board records the selector-conformance fix landing with `domain/selectors/` byte-unchanged — the fork conformed to the law, not vice versa. This is the drift-killing discipline the previous architecture died without.
- **The kernel gained nothing except tests** (TCB gate 1359/1438 at the 1.3-C adjudication). The vision's "microkernel" claim survives contact with an actual LOC budget — rare.
- **The 6D lease maps exactly** to the vision's "(USD, tokens, time, bytes, turns, depth)" — with the crucial correction that `millis` is *charged compute time*, not wall-clock, and `depth`/`turns` are structural ceilings, not additive quantities (ADR-0074 §2). "Thermodynamic" is acceptable shorthand for *conserved quantities under conservation laws*; the law's version is the one that survives adversarial review (sibling depths are not summed; unbounded child under bounded parent = deny).

**Residual Layer-1 items (all already on the board):** close M-2 (gate: duplication detector green, zero `layer0.*` imports, no behaviour change); the `_PROC_PATTERN` restatement fix (NOVA-3); the suspend/resume falsifier (NOVA-2) — which is really the *bridge* from Layer 1 to G4, because it is the test that decides whether future concurrency is a scheduling refactor or a rewrite.

**[GLM] One caution:** the Foundation's maturity creates a temptation to keep polishing it. The corpus already names this risk (governance mass, W6 in `005`). The Foundation is good enough to prove the framework claim; the framework claim is currently unproven. Attention must move to Wave 3.

---

## 3. Layer 2 — Proving Ground & Universal Abstraction: the gap is the surface, not the machine

**Assessment: the machine can express the vision; the manifest cannot yet *ask for* it.** This is `005`'s W1/W2/W4 triad, formalized in the `004` roadmap as M-3.3/M-3.5/M-3.4. The GLM review agrees with all three and adds weighting evidence:

### 3.1 The fixed-slot manifest is the single biggest architectural distance-to-goal

`harness.yaml`'s five named slots describe *the first pack*, not *the substrate*. Every vision-level capability in Layer 3 — debate, critic loops, tree search, evolutionary search, stigmergic swarms — is a composition of *N planners/evaluators with declared wiring*, which the current schema cannot name. The vision promises "anyone can construct task solvers for any domain"; today that promise is only executable for domains whose agent shape is ReAct-with-swappable-parts.

The correction (component graph at 3.1-B, slots become pack convention, `D_H` covers the graph) is right, cheap now, and expensive after Wave 4 (every pack, every trajectory, every `D_H` attribution migrates). **[GLM]** The Director scope call (3.3-B) should be made at Wave-3 *entry*, not mid-wave: compose-v2 (3.1-B) is where the graph lands, and building it twice is the waste the roadmap exists to prevent.

### 3.2 `agent.spawn` as a mediated verb is the unlock for Layer 3 — and correctly design-only now

The vision's "stigmergic swarms" and "hierarchical decomposition" are *spawn topologies plus policy*. Today `spawn` is engine-owned, so recursive algorithms have no home except inside the engine — the exact outcome ADR-0070 was written to prevent. Exposing `agent.spawn` as a capability-mediated kernel verb (M-6) converts "a strong ReAct harness with a kernel" into "a framework for agentic algorithms." The roadmap's sequencing (design note at 3.5, decide at M-3, implement post-M-4) is correct: it touches the TCB, and Wave 4 must not absorb a kernel change.

**[GLM] Stigmergy specifically:** the O(N²)-avoidance claim is architecturally sound *because* coordination is projected from the ledger and blob store (shared environment artifacts) rather than agent-to-agent channels — swarm-as-policy (ADR-0070). But this must remain a *pack/policy*, never a "stigmergy engine" with pheromone machinery in the core; the research corpus's pheromone-decay formalism belongs, if anywhere, in a plugin's strategy code where it is measurable and replaceable.

### 3.3 Guardrails: absent-vs-forged is the right rule for the vision's universality

A pure-math or research composition should not require a UID-10002 daemon and a preregistered oracle to run. "You may turn a guardrail off; you may never turn off the record that it was off" (M-3.4) preserves everything: unsigned verdicts stay categorically illegal, `D_H` records the absence, trajectories are marked non-attributable for promotion. This keeps the substrate *universal* (G3) without weakening G1. No divergence from `005` — recorded here because the vision's "universal" language makes this correction load-bearing.

### 3.4 Domain-generality is a fact, not a thesis — only after Pack #2

I-7 currently passes because nothing has tested it. The corpus is honest about this. Pack #2 at M-5 as an **exit gate** (zero diffs under `domain/`/`kernel/`) is the correct conversion of the vision's "zero core engine changes" promise into a falsifier. **[GLM]** Suggested addition when M-5 is entered: the Pack #2 gate should also assert *trajectory parity* — the non-coding pack must emit the same rich `mhf.trajectory/1` rows (cost, fingerprint, verdict-or-null) as the coding pack, or the M-10 learning loop will be coding-only in practice.

### 3.5 The proving ground itself (`vg`) is under-weighted in the evidence plan **[GLM]**

The vision names the coding CLI as the *empirical stress-test* of the kernel ("against compilers, test suites, and git diffs"). Wave 4's nine-row E2E gate is one real run. That proves the spine fires once; it does not stress it. The reference corpus's Terminal-Bench evidence (same model, harness spread of ~14 points) cuts both ways: it validates *harness-as-substrate* as a thesis, and it implies AETHER's own harness quality must be measured against external benchmarks before Layer-3 claims. Recommendation: after M-4, before M-8, run the compiled `code-default` harness on a public terminal/coding benchmark with cost/latency telemetry — not to chase leaderboard position, but because a substrate whose first pack loses to a naive ReAct loop has a falsified composition surface, and that signal should arrive *before* Pack #2 and the M-8 validation compositions are built on the same surface.

---

## 4. Layer 3 — Emergence & Self-Improvement: architecture ready, corpus at risk

### 4.1 The identity architecture is the vision's quiet enabler

`D_H`/`D_R`/`D_X` (ADR-0071, completed by ADR-0074 §4) plus exterior-signed verdicts mean the future training signal is **un-gameable by construction** — the property the vision's "verifiably grounded" reduces to at scale, and the property no competitor pipeline has. Skill cards harvested from signed trajectories, DPO pairs keyed on `(task_digest, harness_digest, turn-prefix)`, calibrated escalation (SPEC §5.3): all of it consumes a corpus whose denominators were locked before any experiment existed. This is the strongest single argument that the three-layer vision is a programme rather than a narrative.

### 4.2 Dual-process reflex: expressible today, measurable only later

The vision's "System 1 sub-100ms + System 2 frontier" is already *expressible* as composition data: `model_routes` with tier-1 local models (the Ollama adapter exists), escalation policy (`tier_escalation.py` survives in `runtime/`), all inside `D_H`. What does not exist: any measurement of the <100 ms claim, plugin-cell IPC overhead, or container cold-start on the canonical path. The SPEC's tier latency table (~0 / 1–5 ms / 10–50 ms) is asserted, not measured. **[GLM]** M-9's measurement tasks (IPC, serialization, ledger pressure) are correctly sequenced; the review's only addition is that the System-1 latency claim should be stated as a *hypothesis with a named falsifier* now (e.g., "tier-1 local round-trip < 100 ms p50 on commodity hardware, measured at M-9"), so it cannot silently degrade into marketing language — the same treatment `005` recommended for the loop-pluggability claim (its W3).

### 4.3 The corpus is born hollow — verified, and the highest-leverage cheap fix open today

On disk at `83b5009`: `vanguard/packages/runtime/trajectory.py` builds both its turn records and its episode summary with `dict(_ZERO_COST)` (lines 53, 75). F-12 asserts schema validity; a zero-cost, fingerprint-less, verdict-less record satisfies it. Consequences, mapped to the vision:

- **Skill cards (SPEC §5.4):** mining "recurring effect n-grams with high verdict-conditional lift" requires the verdict *and* cost per turn in the row. Not present.
- **DPO harvest (SPEC §7):** prefix-attribution telemetry needs per-turn cost divergence. Not present.
- **Calibrated escalation (SPEC §5.3):** `P(pass | action, context)` needs outcome + model identity per turn. Not present.

NOVA-1 (roadmap task 2.2, status PRONTA) closes this. **[GLM] Recommendation: promote NOVA-1 from "ready" to "next", ahead of any Wave-3 feature work.** Rationale: every canonical-path episode that completes before the fix is a permanently degraded row in the only corpus Layer 3 will ever have; the fix is small; and M-4's NOVA-5 (confirming the real run carries non-zero cost) already depends on it. The cost of ordering it second is invisible until the day it is catastrophic.

### 4.4 Self-improvement safety posture: correctly conservative

The vision says the substrate should "safely improve its own models and configurations over time." The law says: no self-updating release pipeline (SPEC §9, SA-1…SA-6 refused), promotion is a signed event flipping a registry pointer after paired McNemar selection, and the outer loop is capability-restricted to manifest-mutation proposals / skill writes / oracle preregistration and can never touch the workspace (SPEC §5.1). **[GLM]** This is the right reading of "safely": the system may *propose*; the lab and a partial-order promotion frontier *decide*; the evidence chain stays attributable end-to-end (M-10.7-B is exactly the right final gate). No divergence.

---

## 5. As-built claims verified on disk (this review's own evidence pass)

Claims in this review were checked directly against the working tree at `83b5009`, not taken from documents:

| Claim | Verification |
|---|---|
| CI subject of record is wired | `.github/workflows/ci.yml:31` runs `unittest discover -s test/kernel`; board records M-0 closed |
| `layer0/` shrunk per 2.2-B | `layer0/` now contains only `compose/` and `registry/` (+ README/py.typed) — kernel, scheduler, events, spi are gone; deletion of the remainder is 3.1 scope, as triaged |
| `root.py` split in place (2.2-C) | `runtime/compose.py` (390), `session.py` (646), `wiring.py` (347) exist beside `root.py` |
| Single writer + gateway (ADR-0076 §5/§6) | `runtime/ledger_emitter.py` (331) and `runtime/evaluator_gateway.py` (58) exist |
| Trajectory assembly exists (I-9) | `runtime/trajectory.py` (113) exists and emits `mhf.trajectory/1`-shaped rows |
| **Trajectory content is hollow (W8 live)** | `runtime/trajectory.py:53` and `:75` both write `dict(_ZERO_COST)`; no model fingerprint; no embedded verdict found in the assembly path |
| Coding pack is real | `packs/code-default/` contains `harness.yaml`, `plugin.yaml`, plugins, oracles, system prompt, approval policy |
| Schema contracts exist | `schemas/mhf/` contains event_envelope, effect_request, spi_payloads (incl. `SignedVerdict`), harness_manifest, trajectory schemas |

The one material negative finding of the pass is the trajectory row. Everything else the documents claim about M-0/M-1/M-2 state was confirmed.

---

## 6. Assessment of the v0.6.1 Alignment Roadmap (`004`)

The roadmap is judged on its own terms: *make the documentation say what the review concluded, so developers can execute against it.*

**Correct and confirmed:**

- **Append-only discipline** — new ADRs `0077+` for component graph, absent-vs-forged, `agent.spawn` design note; `0069`–`0076` untouched. Matches ADR-0000 and the `0076` precedent.
- **Wave-3 falsifier hardening (NOVA-4)** — the six negatives (unknown-ref fails at compose, empty-ceiling denies, registry-exclusive write, faulted-cell-cannot-stay-active, `in_process`-requires-grant, frozen-composition-immutable) are first-class falsifiers. This is the single most important process correction in `004`, because Wave 3 carries the framework claim on the least-proven code in the tree (`layer0/registry/` + `layer0/compose/` have never run on the canonical path).
- **M-4 stop condition unchanged**; `agent.spawn`, concurrency, Pack #2, M-5…M-10 all locked out of implementation until the nine-row gate is green on one real run.
- **Macro-roadmap M-5…M-10 at outcome/gate granularity only** — correctly resists detailing unstarted work; the M-5→M-10 arc (consolidation+Pack #2 → delegation → concurrency → framework-builder proofs → scale → meta-cognition) is a faithful operationalization of the vision's Layer 3, in the right dependency order.
- **Documentation collapse scheduled post-M-4, not now** — the governance corpus (seven authority tiers, ~3.4k lines) is a real and rising cost (W6), but mid-flight doc surgery during Wave 2/3 would be worse.

**[GLM] Cautions and additions:**

1. **Task-count asymmetry persists.** NOVA-4 adds the *falsifiers* for Wave 3, but Wave 3's task list is still the thinnest relative to what it must prove (registry FSM + compose v2 + echo plugin + fault injection + broker + rlimits + pack migration + token sweep + component-graph design + guardrail schema + spawn design note). Compare Wave 1: seventeen tasks, fifteen falsifiers. If Wave 3 slips, the temptation will be to cut the echo plugin's full lifecycle or the negative suite — precisely the two things that constitute the proof.
2. **The 3.3-B Director decision should be first, not parallel.** Compose v2 (3.1-B) will be written once; if the component graph is decided after compose v2 solidifies around six keys, the graph becomes a v3. Decide at entry.
3. **NOVA-1 ordering** (§4.3 above): trajectory content hardening is currently "PRONTA" inside 2.2; it should be executed before Wave 3 opens, not as background hygiene.
4. **The vision statement itself deserves one normative artifact slot.** The corpus currently has no document that states the *goal* (the three-layer vision) as a first-class, versioned object distinct from SPEC's normative content. Risk: the goal lives only in prompts and review preambles, where it cannot be cited or tracked. Cheap fix: one page (README opening or a dedicated `docs/` page) explicitly marked non-normative vision, so every future review measures distance against the same sentence. (ADR-M0-10 stays satisfied: it bans metaphysics in architecture, not the existence of a goal.)

---

## 7. The reference research corpus — adopt / adapt / refuse

The `RESEARCH_*` documents are suggestions. Judged strictly against the goal and the law:

### Adopt (consistent with locked law; several already scheduled)

- **Harness is the independent variable** (Terminal-Bench spread; harness-builder framing) — this *is* the project's thesis; the corpus supplies external empirical support for it.
- **Flat composition surface at the composition layer** (profile/stack of bundles) — already formalized as the component graph (M-3.3). Orthogonal to rigidity at the authority boundary; AETHER can and should have both.
- **Structural retrieval before semantic** (Aider lesson; repo-map, AST, reference graphs) — already SPEC §4.2; ContextBench's recall-over-precision warning reinforces it.
- **"Delegation must pay rent"** — matches `005` and the spawn-attenuation design; M-8's validation compositions (debate, critic loop, evolutionary search) are exactly the rent-paying proof.
- **Harness-native optimization** (LEGO-RL; train where you infer) — converges with SPEC §7's DPO-on-own-trajectories, with the added property competitors lack: the training signal is exterior-signed and therefore un-gameable. Scheduled M-10.
- **Small-model channels** (System-1 local models, error-signature classifiers, skill-card synthesizers) — all land as *plugins/policies above the wire*: model routes, outer-loop toolkits, memory capabilities. None requires core change.

### Adapt (useful, but must be re-expressed within the law)

- **Sub-5 ms pre-flight filters on tool proposals** — valuable as an *advisory* classifier that rejects malformed proposals before a process fork, but it MUST NOT become a second authorization path; S0–S12 remains the only mediator, and the filter's rejections must surface as ordinary kernel decisions (or planner-side, pre-proposal).
- **Elo-decayed skill cards with eviction thresholds** — the dynamics are a reasonable `IMemoryEngine`/harvester strategy, but cards enter manifests only through the §5.2 selection pipeline (paired McNemar against the undeletable baseline); no free-text skill is ever trusted because it scored well.
- **Active-inference framing** — SPEC §5.3 already operationalizes it as calibrated `P(pass | action, context)` + threshold policies; keep the math, drop the metaphysics (ADR-M0-10).
- **McNemar protocol** — already law (`docs/04_annex/MEASUREMENT.md`); the research docs add nothing beyond restating it.

### Refuse (contradict locked law or the goal)

- **"No privileged core to patch"** — the privileged core is the differentiation; a flat plugin graph with no authority boundary is a system whose evidence cannot be trusted. `005` said this first; this review concurs emphatically.
- **Swarm engine, workflow DAG engine, graph database** — refused by ADR-0070/`REJ-01`; pheromone/stigmergy formalisms are plugin policy at most.
- **Vector database as core infrastructure** — embeddings are an `IMemoryEngine` capability (SPEC §6.1), negotiated, not substrate.
- **RL / multi-agent-first sequencing** — the corpus's own §76 ("do not start with swarm / RL / 30 adapters") matches ADR-0073's deferral register exactly. First stabilize the harness; then learn from it.
- **Biological/cosmological framing in documents** — ADR-M0-10; the research corpus's neuroscience vocabulary (hippocampal buffers, dopaminergic TD) stays in references.
- **Benchmark scores as evidence without separability** — a leaderboard pass by a self-graded harness is worthless as evidence (the project's own one-sentence identity).

---

## 8. What should be done about it — priority-ordered

The mandate asks not just for assessment but prescription. Ordered by leverage-per-unit-cost, consistent with (not replacing) the `004` roadmap:

1. **Close M-2.** In flight; the remaining work (duplication detector, zero `layer0.*` imports, linter extension) is mechanical. Do not open anything else first.
2. **Execute NOVA-1 immediately after (or within) M-2 closure.** Trajectory rows must carry non-zero per-turn cost, model fingerprint, and embedded-or-explicitly-null verdict, with F-12 strengthened from schema-validity to content assertions. Verified gap; small fix; compounding cost every day it waits. Every Wave-3/4 episode that completes before this lands is a degraded row in the only corpus Layer 3 will ever train on.
3. **Make the 3.3-B Director decision (component graph) at Wave-3 entry, before compose-v2 is written.** This is the one decision whose cost compounds through every pack, trajectory, and `D_H` attribution after Wave 4.
4. **Give Wave 3 the Wave-1 treatment.** The NOVA-4 negative suite plus the full echo-plugin lifecycle on the canonical path *is* the extensibility proof; protect both from schedule pressure. If the wave must shed scope, shed breadth (fewer toolkits migrated), never the falsifiers.
5. **Add the NOVA-2 suspend/resume falsifier before M-3 closes.** Cheap now; decides whether M-7 concurrency is a refactor or a rewrite; nothing else on the board buys that much option value per test.
6. **Hold the M-4 stop line exactly as written.** The temptation after a green nine-row run will be to start `agent.spawn` or Pack #2 immediately. The roadmap is right: consolidate docs, then prove generality, then delegate, then scale, then learn — in that order.
7. **State the vision as a versioned, non-normative artifact** so future reviews and contributors measure against the same sentence (§6, caution 4).
8. **Post-M-4 (already scheduled, keep):** documentation collapse to SPEC + ADR log + one board; Pack #2 as the I-7 gate; `agent.spawn` implementation decision; then the M-6→M-10 arc.

---

## 9. Risk register (goal-level)

| # | Risk | Likelihood | Impact | Mitigation (already on board unless noted) |
|---|---|---|---|---|
| R1 | **Hollow corpus survives to production** — Layer 3 built on rows without cost/fingerprint/verdict | Medium | Fatal to Layer 3 | NOVA-1/F-12 hardening; **[GLM] promote to next** |
| R2 | **Wave 3 under-delivers the extensibility proof** — echo plugin or negative suite cut under pressure | Medium | Fatal to Layer 2 claim | NOVA-4; W7 rebalancing; **[GLM] shed breadth, never falsifiers** |
| R3 | **`D_H` migration cost compounds** — component graph decided late | Medium | High (every pack/trajectory re-attributed) | 3.3-B at Wave-3 entry **[GLM]** |
| R4 | **Governance mass grows faster than capability** — docs cost rising (W6) | Medium | Medium (velocity, onboarding) | Scheduled M-5 collapse; resist adding tiers before then |
| R5 | **Latency claims degrade into marketing** — <100 ms System-1, ms-level tier costs asserted, never measured | Medium | Medium (credibility, M-9 rework) | **[GLM]** name the falsifiers now; measure at M-9 |
| R6 | **K ≪ N unproven** — suspend/resume never tested; concurrency becomes a rewrite | Low–Medium | High (M-7/M-9 cost) | NOVA-2 falsifier |
| R7 | **M-4 stop-line erosion** — product pressure before evidence | Low | High (repeats the dual-runtime failure mode) | Roadmap discipline; Director owns the stop |
| R8 | **First-pack quality unmeasured externally** — composition surface falsified late | Medium | Medium | **[GLM]** post-M-4 external benchmark run with telemetry |

---

## 10. Decision register

| # | Item | Call | When |
|---|---|---|---|
| 1 | Foundation (three planes, S0–S12, typed budgets, exterior judge, WAL, sandboxes, one algebra/one JCS/one writer) | **Keep as-is** — verified delivered | — |
| 2 | Trajectory content assertions (NOVA-1: non-zero cost, fingerprint, verdict-or-null) | **Execute next** — verified hollow on disk | M-2 close / Wave-3 entry |
| 3 | Component-graph manifest (3.3) | **Adopt** — and decide 3.3-B at Wave-3 entry, before compose-v2 | Wave 3 |
| 4 | Absent-vs-forged guardrail policy (3.4) | **Adopt** as scheduled | Wave 3 |
| 5 | `agent.spawn` as mediated verb | **Design now, implement post-M-4** — correct as scheduled | M-3/M-6 |
| 6 | Suspend/resume falsifier (NOVA-2) | **Add before M-3 closes** | Wave 2/3 |
| 7 | Wave-3 falsifier set (NOVA-4) + full echo lifecycle | **Non-negotiable scope** | Wave 3 |
| 8 | Pack #2 as I-7 gate, with trajectory parity | **Adopt** (+ parity assertion) | M-5 |
| 9 | External benchmark run of `code-default` with telemetry | **Add** — composition-surface falsification signal | Post-M-4, pre-M-8 |
| 10 | System-1 latency and tier-cost claims as named hypotheses | **Add** (falsifier wording now, measurement M-9) | Now / M-9 |
| 11 | Vision statement as versioned non-normative artifact | **Add** (one page) | Any time; cheap |
| 12 | Documentation collapse | **Keep scheduled** post-M-4 | M-5 |
| 13 | "No privileged core", swarm/DAG/graph-DB engines, vector DB as core, RL-first, metaphysics in docs | **Reject** — already correctly refused; nothing here reopens them | — |

---

## 11. Bottom line

Measured strictly against the stated goal — a universal operating substrate for verifiably grounded autonomous task-solving agents — **AETHER is not a thesis wearing an architecture; it is an architecture that has not yet finished earning its thesis.** The irreversible decisions (exterior unforgeable evidence, one recursion primitive under monotonic attenuation, state as cold-replayable fold, identity split three ways, a kernel small enough to audit) were all made in the general form, before product pressure, and have survived an unusually honest falsifier culture. Layer 1 of the vision is effectively built. Layer 2 is one well-scoped wave away from being *provable*, provided the component-graph decision is made early and Wave 3 keeps its falsifiers. Layer 3 is correctly deferred and — uniquely among systems of this ambition — rests on a training signal that its own agents cannot corrupt.

The two things this review adds to the existing register are both cheap and both urgent in the compounding sense: **make the trajectory corpus real before another episode completes** (verified: it is currently born hollow), and **make the one decision (3.3-B) whose cost grows with every pack written against the current manifest shape.** Everything else on the board is in the right order.

---

*Report generated 2026-08-21 from the working tree at `83b5009`. Advisory only: on conflict, `docs/SPEC.md` and `docs/05_adr/` win.*






