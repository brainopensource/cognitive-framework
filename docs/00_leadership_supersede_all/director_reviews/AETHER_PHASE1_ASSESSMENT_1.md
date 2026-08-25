# AETHER — Phase 1 First-Principles Architectural, Scientific & Constitutional Assessment

**Prepared by:** Principal AI Systems Architect, for Engineering Leadership
**Baseline:** `brainopensource/cognitive-framework` @ `main` (2026-08-25), VISION v0.7.0 (Law Zero, ADR-0095), SPEC v0.7.0 Higgs, ADRs 0069–0096.
**Method:** documentation review (VISION, SPEC, 6 law leaves, ADRs 0088–0096, milestones, sprint board, glossary, theory), static code audit of `vanguard/packages/*` (import-graph direction, TCB measurement, event vocabulary reconciliation, ExecutionProfile axes, blob/artifact port surface), and local execution of the kernel/contract/runtime/security test suites.

---

## 0. Executive verdict

**The foundational thesis is coherent, internally consistent, and empirically disciplined. It should be locked, not redesigned.** The central question — *is AETHER founded on abstractions that survive capability growth without foundational rewrites?* — receives a qualified **yes**, conditional on three corrections, all of which are governance/reconciliation actions rather than architecture changes:

1. **Adjudicate ADR-0096.** A vision-superseding constitutional correction sits in `status: proposed`, and the sprint board already treats one M4-04 bullet as blocked on its ratification. Until ratified or rejected, the repository has *two candidate constitutions*, which is precisely the incoherence Phase 1 exists to eliminate. Recommendation: **ratify with the amendments in ADR-0097 §2**, execute the §12/§12.1 atomic edits, and re-lock VISION.
2. **Schedule event-vocabulary unification at M-5a.** `EVENT_KINDS = generated-wire-enum(42) ∪ hand-maintained `_V4_ONLY_KINDS`(16)`, of which 8 kinds are normative-but-dead (no writer, no reducer, no schema presence). This violates the spirit of A-4/I-8 ("one schema"; "generated or normative, never both"). The drift is honestly documented in `domain/ledger/events.py`, and the envelope-digest preimage protection correctly forbids fixing it before M-5a — so the fix is a *scheduled decision*, recorded in ADR-0097, not an edit today.
3. **Extend the Trusted Core boundary accounting.** `kernel/dispatch.py` imports `domain.canonicalisation.digest`, `domain.canonicalisation.jcs`, and `domain.selectors.resource_selector`. Those modules are *inside the trust boundary* but *outside the 1438-LLOC budget*. The LOC-only budget is already condemned by ADR-0096 §7.1 (RF-97); the multidimensional replacement must count transitively imported trusted modules.

Everything else in this document is confirmation, refinement, or explicitly deferred work. **No foundational rewrite is required. No layer merge/split is required. The roadmap ordering M-4 → M-5a → M-5b → M-6 → M-6.5 → M-7 → M-8 → M-9 is confirmed.**

---

## 1. The foundational computational model — audit of each concept

The architecture is treated below as a hypothesis. For each concept: does it need to exist, what does it own, what must it never own, and is it foundational or a higher-level mechanism. The full canonical lock table with responsibilities, non-responsibilities, adjacencies and stability classes is in **ADR-0097 §4** (single canonical definition; this section carries only the adjudication and rationale).

**Event (causal fact).** Foundational. The append-only, envelope-typed, digest-identified causal record is the ontological pivot of the entire design and every downstream property (replay, recovery, science, attribution) derives from it. ADR-0096 §2 correctly demotes *event sourcing the mechanism* to "reference realization" while promoting the *invariants* (durable causal history, provenance, reconstructable projections, committed-outcome semantics, cold replay, process-independent continuation) to constitutional status. This is the right epistemic posture: bind properties, not implementations. **Preserve; ratify the §2 reframing.**

**Artifact (content-addressed large content).** Foundational as a *contract* (`BlobRef`/`ArtifactRef`, digest identity, CT-53 immutability). The ledger/artifact split is the correct answer to the "ledger as memory dump" anti-pattern. **Gap (M4-04):** the writer path for prompts, raw model outputs, snapshots and patches does not exist; `ArtifactCreated` is a dead event kind. The contract is right; the realization is incomplete. This is the single most consequential implementation gap in the repository because RF-95 and every later scientific claim depend on it.

**Projection (derived state).** Foundational as a *rule* (`S = fold(Events)`; projections are never a second truth), not as a specific reducer. The single canonical ledger reducer plus domain-owned projections is correct. `AgentView` (M-5a) is correctly specified as a projection. **Preserve.**

**Typed causal operation.** Foundational *as thesis*, currently realized only implicitly (proposals → effects → settlements). M5a-P1 correctly schedules the explicit `Operation` contract. Adjudication: the operation contract must remain a *protocol shape* (identity, input refs, output refs, causal parentage, scope, resource requirements, status, observability metadata — VISION cap. 19), never a class hierarchy of operation types. Domain-specific verbs enter through capability declaration, not subclassing.

**Execution lineage & scope.** Foundational. Lineage = causal region identity + ancestry; Scope = the spatiotemporal boundary (budgets across the 6D tensor, depth, turns, capabilities, terminal conditions). This pair is the *definition* of "agent boundary" and is the strongest conceptual asset AETHER has over conventional frameworks: it gives "agent" a falsifiable, non-anthropomorphic definition. `ChildSpawned`/`ChildReturned` already exist as kinds; `runtime/delegation.py` is the M-6 seam. **Preserve; contracts land at M-5a per plan.**

**Agent = Identity + Policy + Event-Derived Projection + Execution Boundary.** Foundational as an *architectural decision* (ADR-0096 §3.3 correctly forbids presenting it as external scientific consensus). ADR-0096 §3.1 permits transient `Agent` objects as ergonomic/performance conveniences while §3.2 prohibits authoritative in-memory state — this resolves the only real tension in the original formulation (purity vs. operational pragmatism) and is falsified by RF-96 cold reconstruction. **Ratify.**

**Policy.** Foundational as a *slot*, not a mechanism: substitutable decision logic (deterministic or model-backed) that selects among admissible possibilities. Correctly kept out of the kernel. The one discipline to enforce: policies must be identity-bearing (they enter `D_H`) — already the case via `FrozenComposition`.

**Effect & settlement.** Foundational. ADR-0096 §4 places settlement semantics (PROPOSED → … → COMMITTED/INVALIDATED as *semantic distinctions*, not a new event roster) in the substrate and admissibility in the kernel. §4.3's observed-vs-committed distinction is essential for idempotent recovery, external effects, and approvals. The existing roster already carries the distinctions. **Ratify; no roster change before M-5a.**

**Capability, grant, attenuation, authority.** Foundational. The two-authority model (A-2: capability grants constrain agents; plugin isolation constrains plugin code; neither trusts the other's subject) is a genuinely strong design that most agent frameworks lack entirely. ADR-0096 §6 elevating authority provenance (`actor_identity`, `authority_source`, `policy_version`, nullable `approval_reference`/`capability_grant`, causation/correlation) to first-class protocol data is correct, and §6.2bis correctly defers the envelope extension to M-5a to protect the digest preimage. **Ratify.**

**Budget (6D resource tensor).** Foundational. Additive conservation (usd_micros, tokens, bytes, millis) vs. structural ceilings (depth, turns) is a clean algebra; reservation/commit/release with leases is the right transactional shape. Scheduler claim TTL correctly excluded from budget millis. **Preserve.**

**Composition vs. trajectory.** Foundational distinction and one of the best ideas in the corpus: composition declares the *space of possibilities* (static, digested into `D_H`); trajectory is the *emergent causal graph of what happened*. This is what keeps AETHER from collapsing into a workflow engine (RF-66 refusal). **Preserve verbatim.**

**Runtime lifecycle, plugins, adapters, packs.** Correct as generic execution infrastructure / extension surfaces. The production chain `mhf.manifest/2 → CanonicalManifest → FrozenComposition → ActivationPlan → RunPlan → EpisodeEngine` with a single bootstrap seam is sound. Plugin activation must materialize a callable service or fail — verified present in the refusals and enforced in wiring. **Preserve.**

**Context, memory, trajectory, evaluation, skills, topology, scheduling, recursion, meta-control, metacognition, self-improvement.** None of these is foundational. All are correctly classified by ADR-0096 §11.2 as **derived capability families** — conceptual groupings whose mechanisms may live in runtime, policies, plugins, projections, or capabilities, with no family receiving independent runtime authority for having a name. The retirement of "future mandatory layers" is the single most important de-ossification in 0096 and should be ratified without dilution. Detailed positions in §5–§6 below.

**Conceptual overlaps found and resolved:**
- *Trajectory vs. telemetry* — overlapping in older text; ADR-0096 §5 separates authoritative causal record from operational telemetry with mandatory correlation. Ratify.
- *Reproducibility class (singular)* vs. reality — `EVIDENCE.md:53` still mandates a scalar class; ADR-0096 §8 replaces it with a computed, time-aware vector. The law leaf edit is pending ratification (§12.1). Ratify.
- *Memory* — the reference document's five-way split (session state / persistent knowledge / experience / skills / user-project memory) must be adopted as vocabulary at M-8 design time so these never collapse into one storage abstraction. Recorded as a locked distinction in ADR-0097 §4, mechanism deferred.
- *"Layer0"* — already deleted (ADR-0081); no residue found in production imports; only test fixtures reference it as negative cases. Confirmed clean.

**Premature domain specificity:** none found in kernel/domain/ports/agency. Coding-specific behavior lives in `packs/code-default/` (planners, oracles, toolkits, context policy) and adapters, exactly where it belongs. The one gravitational risk is sociological, not structural — see §9 Antithesis.

---

## 2. Layer architecture — verdict

Evaluated stack: **domain → ports → kernel → agency → runtime → adapters → packs/clients**, with the causal substrate spanning domain(ledger/artifacts) + runtime(ledger/WAL).

**Measured evidence.** Import-direction audit: kernel imports only `domain.*` (pure values) and `ports.kernel` (protocols); `domain`, `ports`, `agency` contain zero imports of `runtime` or `adapters`; runtime is the sole composition seam for concrete adapters. Package mass: kernel 1,737 physical / 1,366 logical LOC (budget 1,438 — PASS), domain 6,795, ports 886, agency 2,245, runtime 10,660, adapters 8,150. The trusted foundation is genuinely small; behavioral mass correctly accretes at the edges.

**Decisions:**
- **Trusted foundation** = kernel (S0–S12 reference monitor) **plus its transitively imported domain modules** (`canonicalisation.digest`, `canonicalisation.jcs`, `selectors.resource_selector`). Finding: the current budget does not count them. A compromised `jcs.canonicalise` compromises grant descriptors and event digests; it is TCB by any threat-model reading of SECURITY.md. **Correction: RF-97's multidimensional budget must enumerate the trusted import closure, not the `kernel/` directory.** This is an accounting correction, not a code change.
- **Generic execution infrastructure** = runtime (composition, activation, lifecycle, WAL, ledger emission with `PRIVILEGED_KIND_OWNERS`, recovery, profiles, scheduling *mechanism* per 0096 §11.3, delegation seam). Confirmed.
- **Agency** = generic proposal/observation/context mechanics (compiler, compaction strategy registry, episode loop) — no specific agents. Confirmed; the compaction registry is exactly the "many competing context policies, none foundational" shape the reference document demands.
- **Runtime policy vs. extensions vs. domain systems** — boundary justified by semantics throughout; no capability found masquerading as a kernel primitive; no genuinely foundational invariant found exiled to a plugin. The `agent.spawn` treatment (generic S0–S12 effect; kernel MUST NOT branch on the verb or know child topology) is the canonical example done right.
- **Outside the architecture:** UI frameworks, provider SDKs beyond adapter seams, benchmark harnesses (`benchmarks/`, `lab/`), and the assurance certification pipeline (RF-85 profile, per ADR-0094) — correctly exterior.

**Layer merges/splits considered and rejected:** merging agency into runtime (rejected: agency's zero-adapter purity is load-bearing for testability and for the M-5b neutrality proof); splitting a "substrate" package out of domain+runtime ledger code (rejected: the conceptual substrate is a *responsibility overlay*, and 0096 §11.6 explicitly forbids reifying conceptual hierarchy into package taxonomy).

---

## 3. Generality — the substrate as computational medium

The falsification protocol already encoded in the roadmap is methodologically correct and should be defended against enthusiasm in both directions:

- **M-4 (coding harness)** is the demanding falsifier, not the ontology (ADR-0096 §11.1: "first principal laboratory… not the ontological center"). The reference catalog's coding loop (`DISCOVER → … → COMPLETE`) maps onto the substrate as *pack policy + tools + projections* with zero kernel involvement — verified by inspecting `packs/code-default/` (planners, oracles, context policy live entirely in pack space).
- **M-5b (formal reasoning pack)** is the right second domain precisely because deterministic witnesses give an incorruptible oracle, minimizing evaluation ambiguity while maximizing semantic distance from coding. RF-86's "zero semantic diff vs. the re-tagged post-M-5a baseline" is the correct experimental design — the earlier ordering bug (proving zero-diff against a substrate about to change) was caught and fixed by ADR-0095; confirmed correct.
- **Kernel Neutrality Gate (RF-98)** generalizes this into a standing invariant: `new capability or domain → kernel semantic diff == 0`, with justified exceptions requiring an ADR explaining why the responsibility cannot live in substrate/runtime/policy/plugin/capability/projection. This converts "domain-blind kernel" from an aspiration into a recurring falsifiable claim. Ratify.
- **Deep research / tutoring / scientific investigation** loops from the reference document decompose into the same primitives (observe/retrieve/hypothesize/evaluate/synthesize) with domain packs supplying tools, oracles and projections. No missing degree of freedom identified *except one*: the epistemic-state vocabulary (`facts/hypotheses/evidence/attempted/rejected/unresolved/next`) has no event-kind support today. Adjudication: this is deliberately correct — those belong as **pack/agency-level projections over generic events** (`ProposalProduced`, `ClaimRecorded`, `ReflectionProduced`, plus M-5a's plan/strategy kinds), not as substrate kinds. If M-5b shows a formal pack cannot express hypothesis management through generic kinds, that is admissible counter-evidence under ratified 0096 §1 — the constitutional path now exists.

---

## 4. Cognitive architecture — placement decisions

Adopting ADR-0096 §11.2's derived-capability-families frame, each mechanism class from the review scope is assigned (and locked in ADR-0097 §4):

- **Generic infrastructure:** observation mediation, context assembly/compaction *mechanism* (agency), effect settlement, recovery, delegation *mechanism* (runtime), scheduling *mechanism* (runtime, per 0096 §11.3).
- **Data/projections:** state estimation, working context, reasoning state, hypothesis sets, progress (`ProgressProjection`, M-6.5), memory stores, repo maps, skill indexes.
- **Runtime policy:** verification depth, adaptive computation, model routing, budget allocation, delegation strategy, scheduling *policy*, context-selection policy.
- **Reusable cognitive mechanisms (plugins/policies):** critics/reviewers, planners, meta-controllers, compaction strategies, retrieval strategies. The generator/evaluator/promoter separation (0096 §10) governs all of them: self-critique is a capability; self-certification is never promotion authority.
- **Domain-specific capabilities (packs):** localization-before-edit, reproduction-before-fix, failure taxonomies, patch-scope gates, citation verification, learner models.
- **Rejected as architecture:** anthropomorphic "metacognition layer" (remains an experimental hypothesis with the 0096 §11.7 decomposition: monitoring + uncertainty/calibration + self-model + resource model + value-of-computation + control + external feedback); giant universal loops; a "repository brain" primitive.
- **Prerequisite gate confirmed:** the Confidence/Uncertainty Measurement Protocol must exist before M-6.5, comparing self-reported, logprob-derived, behavioral, external-verifier, ensemble-disagreement and calibration-error signals, constitutionalizing none. Without it, "the meta-controller helped" is unfalsifiable.

---

## 5. Self-improvement and meta-loops

The separation `execution → observation → analysis → candidate → evaluation → promotion` is fully specified across MEASUREMENT.md + ADR-0096 §9–§10 and is scientifically defensible:

- Promotion unit = **versioned composition/library**, never the isolated skill (§9.2), because presence-only effects and cross-skill interference are real regression channels — this is the composition-level analogue of held-out evaluation and is stricter than most published agent-skill pipelines.
- Promotion evidence must decompose gross gains / regressions / residual failures / presence-only / invocation / grounding / verification / transfer / held-out (§9.3), with risk-based regression budgets rather than exhaustive re-execution (§9.4) — the right cost/assurance trade.
- `evaluation: none` pre-declared ⇒ `unattributable_for_promotion = true`; unsigned/forged verdicts fail closed (SPEC refusals) — already enforced by the exterior signed judge (I-5).
- §11.5 keeps the search family plural (evolutionary, MCTS, Bayesian, meta-agent editing may compete on the same substrate) — prevents premature commitment to one improvement paradigm.

**One sharpening (ADR-0097 §2.2):** §8's reproducibility vector is declared "computed, not self-declared" but no value domains are defined per dimension. Before M4-04 closes, each of the six dimensions needs an enumerated domain and a derivation rule from observable facts (reducer/schema versions, artifact availability, retention profile, environment capture, model/provider identity), otherwise RF-100 is unexecutable as a falsifier.

---

## 6. Telemetry as scientific infrastructure

The design rule — *provenance by identity and digest for every materially result-affecting variable; content in the artifact store; ledger never a memory dump; causal record ≠ telemetry with mandatory correlation IDs* — is the correct information-theoretic compromise between causal sufficiency and storage amplification. Replay vs. re-execution is cleanly distinguished (VISION cap. 3): replay = deterministic fold under pinned reducers/schemas; re-execution = probabilistic resampling of models/tools with controlled variable substitution (re-simulation). Scoped claims only ("verified under pinned reducer/schema set"), per 0096 §8.5.

**The gap is execution, not design.** M4-04 status verified in code: (1) compaction produces `CompactionReport` in-memory and emits nothing durable; (2) no artifact-store writer path for prompts/outputs/snapshots/patches; (3) `ExecutionProfile` has no `retention` or reproducibility field, so neither reaches the `D_R` preimage; (4) one of four bullets done. The sprint board's **NO-GO on RF-95 until M4-04 closes is correct and must be defended** — burning the one-candidate live-run gate on a trajectory that cannot pass independent review would be an unrecoverable evidentiary waste. Ratifying ADR-0096 is on M-4's critical path because bullet 3's reproducibility-vector semantics are defined there.

---

## 7. Performance as architecture

Where indirection is justified vs. machinery:

- **Justified and already disciplined:** in-process dispatch is zero-copy (UDS and in-process share schemas, not overhead — SPEC refusal); the turn loop stays unary/sequential (I-11) until M7-01 measures effect independence, with a pre-committed cancellation default below ~30% useful independence — this is the correct "measure before building a scheduler" posture and should be praised, not eroded; artifact content-addressing bounds storage amplification; caches/indexes are rebuildable projections, never truth.
- **Identified hot-path costs (accepted, monitored):** JCS canonicalisation + SHA-256 per event append; single-writer SQLite-WAL as durability seam; per-event envelope validation. At current scale these are noise relative to model latency; at M-7 concurrency scale the single writer becomes the ordering bottleneck by design (it *is* the total-order authority). The move to causal partial order (VISION cap. 15: physical sequence numbers ≠ logical dependency) is the right eventual answer; M7-01's contention/cache-hit measurements are the right gate.
- **Unbounded-growth risk:** projection reconstruction cost grows with ledger length. `CheckpointCreated` exists as a kind; checkpointed-fold semantics (snapshot + suffix replay, with checkpoint identity in provenance) should be specified at M-5a alongside `AgentView` so cold reconstruction stays O(suffix), not O(history). Recorded as open question OQ-6, resolvable within existing abstractions — no new primitive required.
- **Benchmark obligation:** M4-04 should land an append/fold micro-benchmark in `lab/bench.py`'s harness so every later "the substrate is too slow" claim has a baseline. Cheap, and converts future performance arguments into measurements.

---

## 8. Code-versus-theory audit — findings register

| # | Finding | Class | Disposition |
|---|---|---|---|
| F-1 | ADR-0096 `proposed`; VISION lacks §12 edits; `EVIDENCE.md` still singular reproducibility class; law leaves lack §12.1 edits | Constitutional incoherence | **Phase-1 blocking.** Ratify-with-amendments per ADR-0097 §2; execute atomic edit set |
| F-2 | `EVENT_KINDS` = generated(42) ∪ `_V4_ONLY_KINDS`(16); 8 kinds normative-but-dead (`ObservationRequested`, `OperatorInvoked`, `OperatorSelected`, `CorrectionRecorded`, `CandidateBuilt`, `CandidateAttested`, `CanaryPromoted`, `RollbackTriggered`) | A-4/I-8 tension, honestly documented | Fold live kinds into generated schema and formally deprecate dead kinds **at M-5a** (envelope preimage protected until then); decision locked now in ADR-0097 §3.2 |
| F-3 | TCB budget counts `kernel/` only; trusted import closure (`domain.canonicalisation.*`, `domain.selectors.resource_selector`) uncounted | Trust-boundary accounting gap | Fold into RF-97 multidimensional budget definition (M-5a) |
| F-4 | M4-04 3-of-4 bullets absent in code (verified: no durable compaction/context/cache provenance; no artifact writer for prompts/outputs; no retention/reproducibility axis in `ExecutionProfile`) | Documented gap, not drift | Sprint-board truth confirmed accurate; RF-95 NO-GO upheld |
| F-5 | Import-direction audit: zero upward dependencies; kernel domain-blind; single bootstrap seam | Conformant | Confirms I-6, I-7, A-1; no action |
| F-6 | TCB 1,366 ≤ 1,438 LLOC; linter green | Conformant (measure weak per F-3) | RF-97 supersedes measure |
| F-7 | Local suites: kernel+contracts 313 passed / ~38.9k subtests, 1 fail (UDS lifecycle — environment); runtime/security failures all trace to absent `bwrap`/sandbox backends, and `SandboxUnavailable` fails closed exactly as ADR-0089 §4.3 requires | Environmental only | No action; fail-closed behavior positively verified |
| F-8 | Hand-maintained catalog comment in `domain/ledger/events.py` records its own drift history and derivation | Exemplary honesty | Pattern to preserve |
| F-9 | No hidden global state, no obsolete compat paths in production chain found; compatibility formats normalize at ingress only | Conformant | No action |

**No code edit is authorized in Phase 1.** F-2 and F-3 are decided now, executed at M-5a (the only ADR-authorized substrate-change window); F-4 is authorized sprint work under M4-04, not Phase-1 scope; F-1 is a documentation ratification act. This keeps Phase 1 exactly at "leave the foundation truthful and coherent" without expanding into feature development.

---

## 9. Dialectical stress test of the whole program

**Thesis — the foundation is correct.** AETHER has independently converged on, and in places exceeds, the strongest published mechanisms: capability-mediated effects with fail-closed authority (rarely present in agent frameworks at all), composition/trajectory separation, exterior signed evaluation, generator/evaluator/promoter separation, composition-level regression-aware promotion, replay/re-execution distinction, and a falsifier-per-obligation governance regime (RF-* register). The kernel-neutrality discipline plus the derived-capability-families frame gives exactly the degrees of freedom the reference catalog demands: every cataloged mechanism (epistemic state, context engineering, critics, multi-agent search, adaptive computation, skill lifecycles) is expressible as pack/policy/plugin/projection with zero foundational modification. The event-sourced substrate makes the system a *laboratory*, which is the only credible path to measured self-improvement rather than vibes-based agent reflection.

**Antithesis — the brutal critique.** (a) *Governance mass as failure mode:* 96 ADRs, six law leaves, a constitution, falsifier registers — for a system that has never completed one real-model coding run (RF-95 unexecuted). The apparatus optimizes for architectural correctness while the empirical loop that would actually validate it remains unfired; there is a real risk the project is better at constitutional law than at agency. (b) *Event-sourcing tax:* every capability pays the envelope/digest/settlement toll; competitors ship useful agents on a mutable dict and iterate 10× faster; the scientific premium is only worth it if the science actually happens (M-8 is far away). (c) *Coding gravity:* one live domain means every "generic" abstraction was shaped under coding pressure; M-5b may reveal that "generic" meant "coding, abstracted." (d) *Sequential loop as ceiling:* I-11 until M-7 forgoes cheap, obviously-safe parallelism (independent reads/fetches) that every production harness exploits today. (e) *Solo-founder bus factor:* the precedence ladder assumes a Director and independent reviewers; if these are the same person, generator/evaluator separation is procedural fiction at the governance level even while enforced at the artifact level.

**Synthesis — boundary conditions for leadership.** The critique does not falsify the architecture; it prices it. The governance mass is justified *iff* M-4 closes soon — therefore the operative Phase-1 output is deliberately anti-bureaucratic: ratify one ADR, lock the vocabulary, authorize nothing new, and put all energy into M4-04 → RF-95. The event-sourcing tax is a paid option on scientific capability whose strike is M-8; the roadmap correctly front-loads the observability that makes the option exercisable. Coding gravity is exactly what M-5b + RF-98 exist to detect, and ratified 0096 §1 now gives negative evidence a constitutional path — the system can lose the argument honestly, which is the strongest available guarantee against motivated reasoning. On I-11: the discipline is correct, but M7-01 is analysis-only and unblocked — start it early so the parallelism decision is evidence-backed the moment M-6.5 lands. The bus-factor risk is organizational, out of architectural scope, but the artifact-level separations (signed exterior verdicts, preregistration, immutable ADR provenance) are precisely the mitigations available to a small team.

---

## 10. Roadmap reconciliation at architectural resolution

Confirmed through M-8 with dependencies as stated in `milestones.md`; no responsibility moves, merges, splits or renames required. Corrections at this resolution only:

1. **ADR-0096 ratification is added to M-4's critical path** (it defines the reproducibility-vector semantics M4-04 bullet 3 must implement). Already implicit on the sprint board; made explicit in ADR-0097.
2. **M-5a scope is enlarged by three already-pending items and nothing else:** envelope authority-provenance fields (RF-99), event-vocabulary unification (F-2), RF-97 budget redefinition (F-3), checkpointed-fold semantics (OQ-6). All are inside the single authorized substrate-change window; `M-5-BASE` re-tags once, after all of them.
3. **M-9/M-10-class capabilities** (distributed execution, populations, online adaptation) remain stress-test-only. Stress result: the lineage/scope/settlement abstractions carry distribution (idempotent settlement per command identity, at-least-once physical attempts, claim TTL as coordination metadata are already distribution-shaped); no irreversible coupling found; persistence semantics (single-writer WAL) are the known, gated bottleneck with a declared evolution path (partial order at M-7+).

**Falsification gates confirmed:** RF-95 (M-4), RF-96 (M-5a cold reconstruction), RF-86 + RF-98 (M-5b neutrality), RF-55–59 (M-6), paired-runs (M-6.5), M7-01 decision ADR (M-7), held-out lift + rollback (M-8).

---

## 11. Open questions that must close before dependent implementation

- **OQ-1 (blocks M4-04 b3):** enumerated value domains + derivation rules for each reproducibility-vector dimension (ADR-0097 §2.2 carries the proposal).
- **OQ-2 (blocks M-5a):** concrete `Operation`/`Lineage`/`Scope`/`AgentView` contract shapes (M5a-P1) and the minimal event-kind additions/foldings, one ADR.
- **OQ-3 (blocks M-5a):** RF-97 metric definitions — trusted import closure enumeration, invariant count, public-contract count, privileged-op count, change-amplification measure.
- **OQ-4 (blocks M-6.5):** Confidence/Uncertainty Measurement Protocol.
- **OQ-5 (feeds M-7):** M7-01 execution + Director decision ADR (implement / simplify / cancel; default cancel below ~30% independence).
- **OQ-6 (M-5a design):** checkpointed projection fold (snapshot identity in provenance; O(suffix) reconstruction).
- **OQ-7 (M-8 design):** memory taxonomy realization (five categories as distinct projection/plugin contracts) and artifact retention/GC semantics vs. `retention_class`/`legal_hold`.
- **OQ-8 (pre-M-9):** multi-tenant semantics — `tenant_id`/`owner_id`/confidentiality exist on the envelope but no law leaf owns isolation semantics; either assign an owner or explicitly defer with rationale.

---

## 12. Completion-gate statement

With ADR-0097 accepted and ADR-0096 ratified-with-amendments, Engineering Leadership can truthfully state: *we understand what AETHER is (an event-sourced general agentic computation substrate whose agents are projections over causal regions), why each foundational abstraction exists (each is bound to an invariant with a named falsifier), where every major responsibility belongs (the lock table), which concepts are law versus policy (constitutional invariants vs. derived capability families), how the code realizes the model (audit register F-1…F-9, all divergences classified and dispositioned), and which decisions are stable enough for Phase-2 planning (everything in ADR-0097 §4 marked `locked`).* The repository then contains one theory, one architecture, one current interpretation — and one unfired experiment (RF-95) that Phase 2 exists to fire.
