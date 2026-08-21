# 006 — Leadership 7 Full Architectural Mandate and Meta-Framework Proposal

**Document class:** comprehensive executive proposal  
**Status:** **PROPOSED — NOT LAW — NO IMPLEMENTATION AUTHORITY**  
**Review date:** 2026-08-21  
**Evidence snapshot:** Git `03e2187`; working tree non-clean before this report was written  
**Decision horizon:** v0.6.1 → v1.0.0; milestones M-0 → M-10  
**Authority boundary:** this document proposes append-only ADRs 0077–0082. Until the Engineering Director accepts them and the canonical artifacts are updated, `docs/SPEC.md`, accepted ADRs 0069–0076, and the active board remain controlling.

> **Stop-line notice.** This proposal does not authorize implementation of `agent.spawn` as a mediated effect, concurrent episode execution, Pack #2, self-modification, DPO training, or M-5–M-10 work before the M-4 Foundation Stop Line is green. It authorizes nothing by itself. NOVA-1 and NOVA-2 are recommended corrections inside the already-authorized M-2 scope; the Director must still record their disposition in the canonical board.

---

## 0. Decision in one page

The Leadership 7 reaches a unanimous architectural conclusion:

**AETHER should become a general task-solving swarm meta-framework by preserving its universal trusted mechanism and replacing coding-shaped composition with a frozen Named Component Graph.** Domain behavior belongs in packs, named components, policies, adapters, and exterior evaluators. Authority remains in the S0–S12 kernel; durable coordination remains in the SQLite WAL State Plane; truth remains in the exterior Evidence Plane. A swarm is therefore a policy over independently attenuated episodes communicating through attributed state, not a new privileged runtime and not an all-to-all chat room.

The immediate priority is not “more agents.” It is trustworthy evidence. `vanguard/packages/runtime/trajectory.py` currently writes `_ZERO_COST` for every turn and episode, does not populate the model route/fingerprint, and can produce an empty turn list. Every such completion irreversibly weakens the future learning corpus. **NOVA-1 must close in M-2.** In the same milestone, **NOVA-2 must prove cold suspend/resume from SQLite WAL in a fresh process**; without it, `K ≪ N` is a slogan rather than a concurrency premise.

The second priority is composition generality. There are presently two manifest surfaces:

1. `packs/code-default/harness.yaml` conforms to fixed-slot `mhf.harness/1` (`planner`, `context`, `memory`, `toolkits`, `evaluation`, `model_routes`).
2. The canonical `Runtime.compose` path consumes v4 JSON manifests with an open `components` map, but `ManifestLoader.REGISTERED_COMPONENT_CONSUMERS` and `runtime.compose.ROLE_KIND` hard-code the accepted roles.

This is not a simple YAML key rename. M-3 must converge both surfaces into `mhf.manifest/2`, compile a named typed graph to one immutable `FrozenHarness`, migrate the packs, absorb the remaining `layer0/registry` and `layer0/compose` behavior into `vanguard/packages/runtime/`, run NOVA-4, and delete all of `layer0/`—including its residual `events/` fork.

The M-4 stop line remains exactly one uncheated real run satisfying nine evidence rows. Only after it is green may M-5 prove substrate generality with **Pack #2: Math & Formal Deductive Verification**, with zero changes under `vanguard/packages/domain/` and `vanguard/packages/kernel/`. Only after that may M-6 implement capability-mediated `agent.spawn`; M-7 may add controlled concurrency; M-8–M-10 may add framework construction, scale, and promotion-gated learning.

### Leadership 7 mandates

| Seat | Binding proposal | Stop condition |
|---|---|---|
| Engineering Director | Accept/reject ADRs 0077–0082 append-only; keep M-4 as the non-negotiable foundation gate. | No post-M-4 feature enters implementation early. |
| CTO | Make the harness graph and verifiable evaluation the moat; treat model vendors as replaceable routes. | No strategy depends on a single model, provider, or coding domain. |
| CIO | Make every promotion input reconstructible from signed evidence, JCS digests, WAL lineage, and explicit missingness. | Missing evidence never becomes inferred success or fabricated zero. |
| Principal Staff Engineer | Close G1/NOVA-1 now; make Pack #2 an executable I-7 falsifier; maintain the gap register as tests. | A claimed capability without a bound falsifier remains a thesis. |
| Principal Systems Architect | Preserve `domain ← ports ← kernel ← agency ← runtime → adapters`, domain blindness, monotone attenuation, single-writer ownership, and the TCB ceiling. | Any required kernel growth must stay `<=1438` logical LOC or first remove equivalent complexity. |
| Tech Lead | Deliver in M-0…M-10 dependency order with exact entry/exit gates and named tests. | No “mostly green,” manual evidence stitching, or hidden alternate runtime. |
| PhD AI Specialist | Use active inference, graph credit assignment, retrieval, DPO, and statistical promotion only as exterior, evidence-bound policies. | No scalar “intelligence” objective, self-scoring, causal claim from chronology, or unpaired promotion. |

---

## 1. Method, evidence hierarchy, and limitations

### 1.1 Evidence hierarchy

Determinations in this report use the following precedence:

1. **Law:** `docs/SPEC.md` plus accepted ADRs, especially 0069–0076.
2. **Canonical decisions:** append-only ADR log and Director authorization.
3. **Execution truth:** active milestone/board and wave packets.
4. **As-built evidence:** source, schemas, generated contracts, tests, and tool output from the live workspace.
5. **Advisory evidence:** Principal Staff reviews and internal research.
6. **External research:** primary papers, official specifications, and first-party engineering reports.

Research does not silently override law. Code does not silently repeal law. A contradiction becomes an explicit gap, owner, and falsifier.

### 1.2 Material inspected

The review covered:

- `README.md`, `docs/00_overview/SYSTEM_OVERVIEW.md`, all of `docs/SPEC.md`, ADRs 0069–0076, ADR-M0-01…13, the milestone/board/wave documents, and the backlog.
- All six files under `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/`, with particular weight on reviews 002, 004, 005, and 006.
- All twelve files under `docs/06_references/`. The two theoretical-synthesis files are byte-identical (`sha256:45bddc7483db62c90a49ba028d591954315aa1f4b0760b42e2ab4956fd7f24e3`). Useful claims were adopted only where compatible with the Clean Triad and current law.
- The live `domain`, `ports`, `kernel`, `agency`, `runtime`, and `adapters` packages; both manifest schemas and representative packs; all remaining `layer0/` sources; related tests and architecture tools.

### 1.3 External primary-source research

The SOTA label below means “relevant evidence available by the review date,” not “automatic architectural authority.” Preprints are identified as such and remain provisional.

| Area | Primary source | What AETHER adopts | Bound or refusal |
|---|---|---|---|
| Multi-agent harnesses | Anthropic’s 2025 [multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | Explicit delegation contracts, isolated workers, parallel specialization, measured coordination cost. | Orchestrator/worker is one policy topology, not the engine. |
| Agent scaling | ICML 2025 position paper on [asymptotic analysis with LLM primitives](https://proceedings.mlr.press/v267/meyerson25a.html) | Count model calls, token volume, critical path, and coordination edges—not just CPU complexity. | “Swarm scales” is invalid without an explicit cost model. |
| Shared-state coordination | 2025 preprint on an [LLM multi-agent blackboard](https://arxiv.org/abs/2510.01285) | State-mediated work discovery can decouple workers and reduce required peer knowledge. | A blackboard is not automatically safe: AETHER requires typed writes, lineage, leases, and single-writer ownership. |
| Verifiable trajectory learning | 2026 ASTRA preprint and [released implementation](https://arxiv.org/abs/2601.21558) | Tool-topology-grounded trajectories, executable environments, rule-verifiable rewards, SFT/RL separation. | ASTRA validates the value of executable evidence; it does not authorize synthetic evidence to replace real signed runs. |
| Decoupled agent RL | 2025 [Agent Lightning](https://arxiv.org/abs/2508.03680) | Separate agent execution from training and preserve transition-level credit data. | Training remains exterior and promotion-gated; it never becomes kernel logic. |
| Turn credit | 2026 [TRACE](https://arxiv.org/abs/2607.13988) | Terminal outcome alone is inadequate for long-horizon credit assignment. | Learned credit is a hypothesis until corroborated by replay/intervention. |
| Active inference | 2025 [Expected Free Energy-based Planning as Variational Inference](https://arxiv.org/abs/2504.14898) | Separate posterior inference (VFE) from action selection (EFE); retain epistemic value and bounded-resource complexity. | AETHER will not call an arbitrary weighted reward “free energy.” |
| Least privilege | 2025 [Progent](https://arxiv.org/abs/2504.11703) and 2025 [MiniScope](https://arxiv.org/abs/2512.11147) | Deterministic, fine-grained tool policy and permission hierarchies outside model discretion. | Natural-language safety prompts never substitute for kernel enforcement. |
| Sandbox mechanism | Linux [Landlock documentation](https://www.kernel.org/doc/html/latest/userspace-api/landlock.html) and Bubblewrap’s [official security notes](https://github.com/containers/bubblewrap) | Layer namespaces, no-new-privileges, filesystem policy, network denial, seccomp/LSM where available, and explicit probes. | Bubblewrap states that policy arguments determine protection; “uses bwrap” alone is not a containment claim. Setuid mode is disallowed, especially in light of the 2026 [setuid advisory](https://github.com/containers/bubblewrap/security/advisories/GHSA-xq78-7hw4-5jvp). |
| Provenance | W3C [PROV publications](https://www.w3.org/groups/wg/prov/publications/) and [in-toto/SLSA provenance](https://github.com/in-toto/attestation/blob/main/spec/predicates/provenance.md) | Represent entities, activities, agents, derivations, inputs, builders, and immutable subjects. | A hash chain proves integrity/order, not semantic truth; exterior verdicts remain necessary. |
| Evolutionary harness search | Google DeepMind’s 2025 [AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) and ICLR 2026 [Darwin Gödel Machine](https://openreview.net/pdf?id=pUpzQZTvGY) | Candidate populations plus objective evaluation can improve algorithms/harnesses. | No in-place self-rewrite; candidates pass AETHER’s external, paired release pipeline. |
| Preference optimization | Original [DPO paper](https://arxiv.org/abs/2305.18290) | A precise pairwise objective can train a policy without an explicit learned reward model. | The pair label must be evidence-derived and unforgeable; DPO is not itself an evaluator. |
| Schema dialect | Official [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12) | Strict dialect declaration, `$defs`, conditional validation, and closed objects. | Referential integrity and graph semantics still require a compiler; schema validation alone is insufficient. |

### 1.4 Forensic snapshot

Verified facts, not roadmap claims:

- `vanguard/packages/kernel/dispatch.py` implements S0–S12 with S2 before lease, S8 verification after reservation, durable S8a intent before S9, actual-cost S10 commit, S11 release before S12 emit.
- The kernel architecture gate reports **1365 logical LOC across 9 files**, leaving 73 LOC beneath the `<=1438` limit. This is a hard warning against putting orchestration or learning in the TCB.
- The boundary tool checked **248 Python files** successfully. Boundary, TCB, secret, domain-blindness, isolation-policy, duplicate-symbol, event-coverage, Markdown-link, and stale-path tools passed in this workspace.
- The SQLite event store uses WAL, `synchronous=FULL`, transactionally serialized append, per-project digest chains, and cold-replay support. `LedgerEmitter` is the canonical role-scoped writer.
- The evaluator is exterior by port and UID/image/signature checks; the sandbox path excludes evaluator material and denies network in the rootless policy.
- `EpisodeEngine.spawn()` already provides engine-owned recursive delegation with attenuation, child lineage, budget conservation, workspace cleanup, and untrusted return provenance. It is **not yet** a caller-visible capability-mediated effect.
- `Runtime.compose` is the canonical composition authority. The old Layer-0 compiler still computes and discards the result of `intersect_ceilings`; this fail-open behavior must not be copied.
- `layer0/` still contains `compose/`, `registry/`, and a residual `events/` fork. Deletion therefore requires more than moving two directories.
- The plugin FSM has seven states, but `DISCOVERED` and `VERIFIED` lack corresponding event kinds today. The runtime writer table already exclusively assigns the five existing `Plugin*` kinds to `registry`.
- `mhf.trajectory/1` permits optional execution/model/genome/outcome fields and `runtime/trajectory.py` emits zero cost at both turn and episode level. Session/model telemetry exists elsewhere but is not wired into the trajectory assembler.

Test evidence gathered for this review:

| Command/suite | Result | Interpretation |
|---|---|---|
| kernel | 93 passed | Trusted dispatch baseline green. |
| contracts | 142 passed | Wire/port baseline green. |
| agency | 105 passed | Current count differs from a stale 107 claim on the board. |
| trust | 22 passed | Trust-spine tests green. |
| falsifiers | 23 passed | Existing named falsifiers green. |
| registry | 26 passed | Layer-0 registry baseline green. |
| packs | 31 passed | Pack baseline green. |
| security, host-capable rerun | 45 passed | Initial sandboxed failure was environmental; host-capable rerun green. |
| adapters, host-capable rerun | 132 run: 3 failed, 1 skipped | Three isolated-evaluator expectations remain red (`dropped_socket`, genuine fix event, modified oracle non-pollution). These are not waived. |
| runtime | 392 run: 3 failed, 1 error, 7 skipped | Ollama cause taxonomy drift (`provider_unreachable` vs `model_tag_absent`) and missing `tools/export_coding_session.py`. Full-suite green must not be claimed. |

The failures above are evidence hygiene issues, not permission to weaken tests. M-2/M-3 entry gates must name whether each is product drift or environment sensitivity and close or quarantine it with a bounded reason.

---

## 2. Strategic paradigm: mechanism, graph, state, evidence

### 2.1 The separability thesis

Let a task family be described by domain semantics (d), a harness composition (H), a universal episode mechanism (U), and an exterior verifier (V_d). AETHER’s substrate claim is:

\[
\operatorname{Solve}(d, x) = V_d\!\left(U\left(\operatorname{compile}(H_d), x\right)\right),
\]

where changing (d) changes only (H_d), adapters, data, and (V_d), while the trusted authority mechanism and domain value contracts remain unchanged.

This is a **bound engineering thesis**, not a theorem. It becomes a supported fact only if Pack #2 completes representative non-coding tasks with:

\[
\Delta\texttt{vanguard/packages/domain}=0,
\qquad
\Delta\texttt{vanguard/packages/kernel}=0,
\]

and without a pack-specific branch in `EpisodeEngine`, `Runtime.execute_harness`, or `Runtime.compose`. Any such diff falsifies the present abstraction and forces a generality review before M-6.

### 2.2 Harness Engineering

The model is cognitive capacity; the harness is the controlled experiment. The independent variables are prompt/context policy, tools, memory, planner topology, routing, budget, evaluator, and graph wiring. The dependent variables are signed task outcome and the six-dimensional resource trace. A model upgrade is one component mutation, not a platform rewrite.

The graph is a **composition graph**, never a runtime workflow graph. It declares named nodes, typed interfaces, and connections, then freezes them into (D_H). Debate, tree search, generator–critic, reflection, and swarm algorithms execute inside planner/controller components over the same turn mechanism. This preserves ADR-0003 and ADR-0069: there is one episode loop, not an accumulating family of privileged schedulers.

### 2.3 Stigmergic swarm through the State Plane

For (N) agents, an all-to-all round has at most (N(N-1)) directed peer messages and therefore (O(N^2)) message edges. That bound applies only to a full mesh; sparse peer topologies can be (O(N)). A state-mediated design instead has agents publish and consume typed work claims, artifacts, observations, and terminal summaries through the ledger/blob/index surfaces. If each agent performs at most (c) state operations per round, coordination operations are (O(cN)), while contention and query cost depend on indexing and hot keys.

This does **not** mean “every token goes into SQLite.” Large values go to the blob store by digest. The WAL carries authoritative envelopes and refs. Semantic retrieval reads a derived index; it does not become the source of truth. Direct agent messages, where useful, are observations and must still be attributed—not a parallel authority channel.

Swarm safety follows four rules:

1. each child has an attenuated principal, budget lease, depth, and explicit parent lineage;
2. coordination writes are typed and role-owned;
3. shared artifacts are immutable/content-addressed or versioned by compare-and-swap semantics;
4. only the exterior evaluator can mint the signed verdict used for promotion.

### 2.4 A-B-C-D foundation

| Foundation | Present truth | Mandate |
|---|---|---|
| **A — Authority** | Strong: S0–S12, selectors, attenuation, budget leases, fail-closed policy. | Keep small and domain-blind; add no orchestration algorithm. |
| **B — Bundle** | Frozen and attributable, but composition roles are coding-shaped/hard-coded across two manifest surfaces. | Replace with the Named Component Graph in M-3; freeze all resolved refs/config/edges. |
| **C — Corpus** | Contract exists, but current assembler creates hollow economics and incomplete identity. | NOVA-1 in M-2; never backfill unknown measurements as zero. |
| **D — Digests** | (D_H), (D_R), and (D_X) are conceptually separated and partially implemented. | Require all three at promotion boundaries and never substitute one for another. |

Identity is defined as:

\[
D_H = H(\operatorname{JCS}(\text{resolved manifest graph})),
\]

\[
D_R = H(D_H \parallel \text{runtime} \parallel \text{environment} \parallel
\text{model identity} \parallel \text{oracle identity}),
\]

\[
D_X = H(D_R \parallel \text{task} \parallel \text{seed} \parallel
\text{initial state} \parallel \text{protocol cell}).
\]

`harness_digest` carries (D_H) only. A changed model fingerprint changes (D_R); a changed benchmark item changes (D_X). “Same harness” is not “same execution.”

---

## 3. Adjudication of architectural tensions T-1 through T-9

### T-1 — Fixed slots versus Named Component Graph

**Ruling: adopt the Named Component Graph now, implement in M-3.** `mhf.manifest/2` replaces both fixed `plugins` slots and the effectively fixed v4 consumer maps. Nodes are named, typed by namespaced interfaces, and connected by explicit endpoints. The compiler rejects unknown refs, interfaces, endpoints, multiple incompatible providers, unsatisfied required ports, capability widening, and unconsumed security-relevant components before activation.

Cycles are permitted in the composition graph because a critic loop or debate topology may be cyclic. Termination is not inferred from graph acyclicity; it is enforced by turn, depth, cost, and effect budgets. The graph cannot encode arbitrary hidden effects: every executable node resolves through a registered SPI/port and receives the intersection of harness and plugin ceilings.

Required graph profiles used as compile fixtures:

- `react-single`: planner → context/model → toolkit → observation.
- `generator-critic`: generator output → critic → revision controller.
- `debate-two`: two isolated proponents → adjudicator.
- `tree-search`: frontier controller → candidate workers → scorer → selector.
- `stigmergic-swarm`: coordinator publishes work refs; workers claim/return through State Plane; aggregator reads attributed results.

All five must compile without a diff to kernel or episode engine. If one requires a new engine branch, the graph is not general enough.

### T-2 — Engine-owned spawn versus capability-mediated `agent.spawn`

**Ruling: specify now, decision checkpoint at M-3, implement only in M-6 after M-4 and M-5.** Existing `EpisodeEngine.spawn()` remains the semantic oracle. The future public verb `agent.spawn` is a privileged effect and must traverse S0–S12 like any other effect; it cannot be a planner callback that bypasses authorization.

The request descriptor binds child objective digest, requested selectors/actions, budget sublease, maximum depth, graph entrypoint, context refs, and workspace mode. The effective child authority is:

\[
A_{child}=A_{parent}\cap A_{manifest}\cap A_{plugin}\cap A_{request},
\]

and its resource ceiling is an actual parent sublease, not copied counters. Child output enters the parent context as `UNTRUSTED_DERIVED` at minimum and cannot authorize widening.

S0–S12 design mapping:

| Stage | `agent.spawn` behavior |
|---|---|
| S0 ENTER | Receive a typed spawn request; no child exists. |
| S1 PARSE | Validate objective/ref/scope/budget/depth; reject unknown fields. |
| S2 RESOLVE | Resolve the registered spawn adapter and graph entrypoint before any lease. |
| S3 DESCRIBE | JCS-digest all authority-relevant child inputs. |
| S4 CLASSIFY | Compute widening against held parent authority; unknown comparison means widening. |
| S5 AUTHORIZE | Apply policy/approval to the exact descriptor. |
| S6 GRANT | Mint a descriptor-bound, expiring grant to the parent principal. |
| S7 RESERVE | Reserve the child budget as a parent-linked lease. |
| S8 VERIFY | Reverify descriptor, principal, expiry, and attenuation at the point of spawn. |
| S8a INTENT | Durably record intent before a child process/workspace can be created. |
| S9 DISPATCH | Create isolated child principal/workspace/session; no implicit inherited handles. |
| S10 COMMIT | Debit actual child use, including overruns; return unused reserve. |
| S11 RELEASE | Close lease on every terminal/failure/cancellation path. |
| S12 EMIT | Emit child lineage and outcome only after release; never leak secrets/raw context. |

### T-3 — Mandatory guardrail versus Absent-vs-Forged

**Ruling: absence may be declared; forgery always fails closed.** The system must distinguish:

- **present/valid:** a required evaluator produced a correctly bound signed verdict;
- **absent/declared:** the manifest explicitly declares `evidence.mode: absent`, a reason code, and an assurance class that is ineligible for promotion;
- **forged/broken:** evidence was required or claimed but is missing, unsigned, incorrectly bound, self-produced, unreachable, or tampered.

Declared absence is valid for exploratory pure computation, transformation, or observation packs where no correctness claim is published. Such a run may complete operationally, but its evidence outcome is `not_evaluated`; it cannot produce `passed`, license a memory write that requires a verdict, enter DPO pairs, or promote a harness/model/skill. A compute-only pack may still use a sandbox—the “guardrail” here is evaluation evidence, not effect mediation.

Forgery maps to `instrument_error`, `inconclusive`, or `EvaluationTampered` as the active contract dictates; it never silently degrades to declared absence. The declaration is frozen into (D_H), so it cannot be selected after observing the result.

### T-4 — Hollow trajectory / NOVA-1

**Ruling: fix immediately in M-2.** Every completed turn must carry measured model identity, provider/model/fingerprint, context digest, proposals, receipts, and a cost vector with at least one positive measured dimension. Every episode total equals the component-wise sum of its turns plus explicitly identified non-turn charges. Unknown measurement is represented by `measurement_status: unavailable` plus a reason—not zero.

For additive dimensions (C=\{usd\_micros,tokens,bytes,millis\}):

\[
\mathbf c_{episode}=\sum_{t=0}^{T-1}\mathbf c_t + \mathbf c_{overhead},
\qquad \mathbf c_t\in\mathbb N^4,
\]

and for each actually invoked model turn:

\[
\sum_{j\in C}c_{t,j}>0.
\]

`millis` means charged compute duration, not wall-clock duration under concurrency. `turns` and `depth` remain structural ceilings, not additive costs. A genuinely zero-price local model can have `usd_micros=0`; tokens and/or charged milliseconds still establish non-hollow measurement.

NOVA-1 must also require populated `execution_digest`, `manifest_genome` or component digests, `model_routes_used`, terminal outcome, and verdict exactly as ledgered or explicitly null with a permitted termination/absence reason. No historical row is rewritten; legacy rows are tagged `legacy_incomplete` and excluded from promotion.

### T-5 — Layer-0 absorption and deletion

**Ruling: parity-first absorption in M-3, then delete all `layer0/`.** Move/adapt registry lifecycle, validation, isolation broker, grants, and composition behavior into package-canonical modules. Do not port the alternate event envelope/store/taxonomy: map it to the canonical domain event contracts, runtime `LedgerEmitter`, and `EventStorePort`, then remove it.

The packages implementation must preserve good Layer-0 behavior, reject the discarded-ceiling defect, and pass NOVA-4:

1. unknown plugin ref fails during composition;
2. empty capability ceiling denies execution;
3. only the registry writer can append `Plugin*` events;
4. a faulted plugin cell cannot remain active;
5. `in_process` execution requires an explicit, frozen grant;
6. a frozen composition cannot mutate.

Deletion is allowed only after import scans, parity vectors, schema/golden-vector tests, and all six negatives pass on `vanguard/packages`. `layer0/README.md` is deleted with the tree; historical rationale remains in Git and ADRs.

### T-6 — Universal Turn Loop as mechanism

**Ruling: publish a bounded mechanism claim, not a universal intelligence claim.** The mechanism is:

```text
observe durable state
→ compile bounded context
→ ask the selected planner/model for one typed proposal
→ mediate zero or one effect through S0–S12
→ persist receipt/observation
→ continue, finish, abstain, escalate, or terminate by budget
```

Planner components may internally propose parallel branches, debate, reflection, or search, but effects remain mediated and terminal states remain distinct from evaluation outcomes.

**Bound falsifier:** implement the five graph profiles from T-1 plus Pack #2 using the unchanged public episode-engine dispatch path. Any required domain verb in kernel, task-type conditional in the engine, direct evaluator reachability, or unmediated effect falsifies the claim.

### T-7 — `K ≪ N` and NOVA-2

**Ruling: prove cold reconstructability in M-2 before enabling concurrency.** Suspend an episode after durable intent/state has been recorded, destroy the original process, create a new runtime instance, reduce the SQLite WAL chain, reconcile any undetermined effect according to policy, resume, and complete with one continuous lineage.

The test must assert:

- no Python object identity, open lease handle, in-memory callback, or process-local queue is required;
- the resumed sequence and `prev_digest` chain are continuous;
- already-completed effects are not repeated;
- an S8a-started but unresolved effect is `undeterminable` until reconciled, never assumed failed/successful;
- budgets, depth, parent lineage, (D_H), and (D_R) survive reconstruction;
- the final trajectory refers to both pre- and post-restart turns.

Only after this proof and selector-conflict soundness may M-7 keep (K) active workers for (N) durable episodes. Concurrency is a scheduling optimization over reconstructible state, not a new semantic path.

### T-8 — Governance mass and documentation collapse

**Ruling: collapse immediately after M-4, in M-5; not during M-2/M-3.** The target is the Clean Triad:

1. one specification for law;
2. one append-only ADR log for decisions;
3. one living board for execution.

Research and completed reviews remain historical evidence, clearly bannered as superseded/advisory. Wave packets move to done/archive with backlinks. No evidence is destroyed merely to make navigation tidy.

### T-9 — Five-SPI freeze

**Ruling: retain through M-4; measure and revisit at M-9.** The Named Component Graph should first express new behavior by composing current planner/context/memory/toolkit/evaluator interfaces. At M-9, inspect actual graph adapters and impedance: duplicated shims, leaky abstractions, unused ports, cross-language conformance cost, and performance. A new SPI requires at least two independent implementations, a stable wire contract, a boundary owner, and deletion of more complexity than it adds. “Useful component type” is not sufficient.
