# 006 — AETHER Tier S+ Master Architecture

## Verified Adaptive Obligation Harness for General Task-Solving Swarms

**Document class:** definitive synthesis of proposals 002–008; comprehensive executive architecture and implementation mandate<br>
**Status:** **PROPOSED — NOT LAW — NO IMPLEMENTATION AUTHORITY**<br>
**Review date:** 2026-08-21<br>
**Evidence snapshot:** package/source evidence revalidated at Git `67e1803`; working tree was non-clean before this synthesis and unrelated changes were preserved<br>
**Decision horizon:** v0.6.1 → v1.0.0; milestones M-0 → M-10<br>
**Authority boundary:** this document proposes append-only ADRs 0077–0082. Until the Engineering Director accepts them and the canonical artifacts are updated, `docs/SPEC.md`, accepted ADRs 0069–0076, and the active board remain controlling.

> **Stop-line notice.** This proposal does not authorize implementation of `agent.spawn` as a mediated effect, concurrent episode execution, Pack #2, adaptive routing, macro-tool promotion, self-modification, DPO training, or other M-5–M-10 work before the M-4 Foundation Stop Line is green. It authorizes nothing by itself. NOVA-1 and NOVA-2 are recommended corrections inside the already-authorized M-2 scope; the Director must still record their disposition in the canonical board.

---

## 0. Decision in one page

The Leadership 7 reaches a unanimous Tier S+ architectural conclusion:

**AETHER should become a general task-solving swarm meta-framework by preserving its universal trusted mechanism and replacing coding-shaped composition with a frozen Named Component Graph.** Domain behavior belongs in packs, named components, policies, adapters, and exterior evaluators. Authority remains in the S0–S12 kernel; durable coordination remains in the SQLite WAL State Plane; truth remains in the exterior Evidence Plane. A swarm is therefore a policy over independently attenuated episodes communicating through attributed state, not a new privileged runtime and not an all-to-all chat room.

The final synthesis adds one coherent adaptive layer above that foundation:

1. **Typed obligations are the unit of schedulable work.** An obligation declares a content-addressed goal, a preregistered witness type, a six-dimensional price ceiling, dependencies, and a parent lineage.
2. **The obligation frontier is a stigmergic projection of the State Plane.** Workers pull lease-bound claims, publish immutable artifacts/witnesses, and never need a privileged peer-to-peer channel.
3. **The Pareto harness is the exterior control policy.** It selects context, model route, refinement rule, swarm width, and verification strength from the admissible frontier. Capability and budget feasibility are checked before optimization; safety can never be traded for cost or speed.
4. **Active inference supplies belief and action semantics.** VFE updates beliefs from ledger observations; EFE ranks feasible policies by pragmatic value, epistemic value, and declared resource prices. Neither can mint authority or truth.
5. **The flywheel compounds in four stages:** exact witness memoization; verified trajectory-to-macro compilation; skill/routing adaptation; and signed DPO/harness evolution. Every learned or compiled artifact re-enters the ordinary registry, capability, sandbox, evaluator, and human promotion path.

This architecture is called the **Verified Adaptive Obligation Harness (VAOH)**. It is not a second runtime. It is a set of exterior components and State-Plane projections compiled by `mhf.manifest/2` and executed by the one universal turn mechanism.

The immediate priority is not “more agents.” It is trustworthy evidence. `vanguard/packages/runtime/trajectory.py` currently writes `_ZERO_COST` for every turn and episode, does not populate the model route/fingerprint, and can produce an empty turn list. Every such completion irreversibly weakens the future learning corpus. **NOVA-1 must close in M-2.** In the same milestone, **NOVA-2 must prove cold suspend/resume from SQLite WAL in a fresh process**; without it, `K ≪ N` is a slogan rather than a concurrency premise.

The second priority is composition generality. There are presently two manifest surfaces:

1. `packs/code-default/harness.yaml` conforms to fixed-slot `mhf.harness/1` (`planner`, `context`, `memory`, `toolkits`, `evaluation`, `model_routes`).
2. The canonical `Runtime.compose` path consumes v4 JSON manifests with an open `components` map, but `ManifestLoader.REGISTERED_COMPONENT_CONSUMERS` and `runtime.compose.ROLE_KIND` hard-code the accepted roles.

This is not a simple YAML key rename. M-3 must converge both surfaces into `mhf.manifest/2`, compile a named typed graph to one immutable `FrozenHarness`, migrate the packs, absorb the remaining `layer0/registry` and `layer0/compose` behavior into `vanguard/packages/runtime/`, run NOVA-4, and delete all of `layer0/`—including its residual `events/` fork.

The M-4 stop line remains exactly one uncheated real run satisfying nine evidence rows. Only after it is green may M-5 prove substrate generality with **Pack #2: Math & Formal Deductive Verification**, with zero changes under `vanguard/packages/domain/` and `vanguard/packages/kernel/`, and add the deterministic Tier-0 witness cache. Only after that may M-6 implement capability-mediated `agent.spawn`; M-7 may add the pull-based obligation frontier and controlled concurrency; M-8 may expose graph/profile construction; M-9 may compile and benchmark candidate macro-tools; and M-10 may perform promotion-gated Active Inference, DPO, and harness evolution.

### Leadership 7 mandates

| Seat | Binding proposal | Stop condition |
|---|---|---|
| Engineering Director | Accept/reject ADRs 0077–0082 append-only; keep M-4 as the non-negotiable foundation gate. | No post-M-4 feature enters implementation early. |
| CTO | Make the content-addressed harness graph, Pareto policy, compiled macro registry, and verifiable evaluation corpus the moat; treat model vendors as replaceable routes. | No strategy depends on a single model, provider, coding domain, or unverifiable reward. |
| CIO | Make every promotion input reconstructible from signed evidence, JCS digests, WAL lineage, and explicit missingness. | Missing evidence never becomes inferred success or fabricated zero. |
| Principal Staff Engineer | Close G1/NOVA-1 now; make Pack #2 an executable I-7 falsifier; maintain the gap register as tests. | A claimed capability without a bound falsifier remains a thesis. |
| Principal Systems Architect | Preserve `domain ← ports ← kernel ← agency ← runtime → adapters`, domain blindness, monotone attenuation, single-writer ownership, the TCB ceiling, and one universal loop. | No obligation scheduler, Pareto optimizer, memory learner, or macro compiler enters the kernel. Any unavoidable kernel growth must remain `<=1438` logical LOC or first remove equivalent complexity. |
| Tech Lead | Deliver in M-0…M-10 dependency order with exact entry/exit gates, named tests, and compatibility sunsets. | No “mostly green,” manual evidence stitching, hidden alternate runtime, or promoted macro without replay evidence. |
| PhD AI Specialist | Use VFE/EFE, graph credit assignment, retrieval, macro synthesis, DPO, and statistical promotion only as exterior, evidence-bound policies. | No scalar “intelligence” objective, self-scoring, causal claim from chronology, unpaired promotion, or cost-collapse percentage without measurement. |

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

- Every proposal artifact available in the requested 002–008 range: `002_beta_review_full_gem_proposal.md`, `004_delta_review_full_glm53_proposal.md`, `005_epsilon_review_full_dsv4-proposal.md`, this 006 baseline, `007_zeta_review_full_opus_proposal.md`, and `008_alfa_review_full_grok_proposal.md`. No `003*proposal*.md` exists on disk. The synthesis imports mechanisms, not conclusions by vote.
- `README.md`, `docs/00_overview/SYSTEM_OVERVIEW.md`, all of `docs/SPEC.md`, ADRs 0069–0076, ADR-M0-01…13, the milestone/board/wave documents, and the backlog.
- All six files under `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/`, with particular weight on reviews 002, 004, 005, and 006.
- All twelve files under `docs/06_references/`. The two theoretical-synthesis files are byte-identical (`sha256:45bddc7483db62c90a49ba028d591954315aa1f4b0760b42e2ab4956fd7f24e3`). Useful claims were adopted only where compatible with the Clean Triad and current law.
- The live `domain`, `ports`, `kernel`, `agency`, `runtime`, and `adapters` packages; both manifest schemas and representative packs; all remaining `layer0/` sources; related tests and architecture tools.

Proposal synthesis ledger:

| Source | Adopted contribution | Correction or refusal |
|---|---|---|
| 002 Beta | Adaptive Pareto profiles, informational bottleneck, exterior oracle, trajectory-to-macro flywheel. | Remove fixed performance promises, invalid “exact” statistics, fixed component enums, and unconditional complexity claims. Profiles become priors, not hard-coded latency/token guarantees. |
| 004 Delta | Compact T-1…T-9 rulings, milestone discipline, and requirement-to-falsifier style. | Later implementation detail is subordinated to verified package paths and the stricter schema/causal/statistical rules here. |
| 005 Epsilon | Corpus-first sequencing, Pack #2 choice, declared-absence guardrails, and practical zero-diff generality gate. | Replace closed component kinds and heuristic causal/statistical shortcuts with namespaced interfaces, intervention labels, and exact paired inference. |
| 006 Fi | Correct VFE/EFE split, product-order economics, two-manifest forensic finding, typed graph with cycles, suspicion-not-causation, signed pair certificates, and exact two-sided McNemar. | Extended here with a native Pareto scheduler, obligation frontier, deterministic witness cache, and macro-tool compiler. |
| 007 Zeta | Obligation Market transplants: memoized witnesses, price ceilings as objectives, lease-bound pull frontier; lifecycle and namespace forensic findings. | Do not replace the universal loop, total-order ledger, or exterior judge. Do not forbid composition cycles or claim unconditional `Theta(N)` scaling. |
| 008 Alfa | Explicit stop-line discipline, path-bag-versus-graph correction, ghost-briefing hygiene, and the rule that ranking state is runtime state unless frozen into `D_H`. | Do not label a continuity-corrected chi-square test “exact,” and do not let review prose outrank source or accepted ADRs. |

### 1.3 External primary-source research

The SOTA label below means “relevant evidence available by the review date,” not “automatic architectural authority.” Preprints are identified as such and remain provisional.

| Area | Primary source | What AETHER adopts | Bound or refusal |
|---|---|---|---|
| Automated harness evolution | 2026 [Agentic Harness Engineering](https://arxiv.org/abs/2604.25850) preprint | Component-, experience-, and decision-observability; harness edits as falsifiable contracts; frozen candidates evaluated across model families. | Reported benchmark gains are evidence for that system, not promised AETHER gains. AETHER requires signed exterior outcomes and immutable pairing cells. |
| Multi-agent harnesses | Anthropic’s 2025 [multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | Explicit delegation contracts, isolated workers, parallel specialization, measured coordination cost. | Orchestrator/worker is one policy topology, not the engine. |
| Agent scaling | ICML 2025 position paper on [asymptotic analysis with LLM primitives](https://proceedings.mlr.press/v267/meyerson25a.html) | Count model calls, token volume, critical path, and coordination edges—not just CPU complexity. | “Swarm scales” is invalid without an explicit cost model. |
| Shared-state coordination | 2025 preprint on an [LLM multi-agent blackboard](https://arxiv.org/abs/2510.01285) | State-mediated work discovery can decouple workers and reduce required peer knowledge. | A blackboard is not automatically safe: AETHER requires typed writes, lineage, leases, and single-writer ownership. |
| Verifiable trajectory learning | 2026 ASTRA preprint and [released implementation](https://arxiv.org/abs/2601.21558) | Tool-topology-grounded trajectories, executable environments, rule-verifiable rewards, SFT/RL separation. | ASTRA validates the value of executable evidence; it does not authorize synthetic evidence to replace real signed runs. |
| Graph credit assignment | 2026 [GraphGPO](https://arxiv.org/abs/2605.26684) preprint | Aggregate comparable rollouts into a state-transition graph and estimate edge contribution to goal-distance reduction. | Graph advantage is a learned attribution signal, not causal proof and never an authoritative verdict. |
| Decoupled agent RL | 2025 [Agent Lightning](https://arxiv.org/abs/2508.03680) | Separate agent execution from training and preserve transition-level credit data. | Training remains exterior and promotion-gated; it never becomes kernel logic. |
| Turn credit | 2026 [TRACE](https://arxiv.org/abs/2607.13988) | Terminal outcome alone is inadequate for long-horizon credit assignment. | Learned credit is a hypothesis until corroborated by replay/intervention. |
| Active inference | 2025 [Expected Free Energy-based Planning as Variational Inference](https://arxiv.org/abs/2504.14898) | Separate posterior inference (VFE) from action selection (EFE); retain epistemic value and bounded-resource complexity. | AETHER will not call an arbitrary weighted reward “free energy.” |
| Skill synthesis | 2026 [SkillTTA](https://arxiv.org/abs/2605.16986), [Globalized Skill Evolution](https://arxiv.org/abs/2608.06153), and [MACRO](https://arxiv.org/abs/2603.05860) preprints | Retrieve evidence-relevant trajectories, consolidate related skills, discover recurring verified tool sequences, and replay-test candidates for generalization. | A prose skill is not a macro-tool; a macro is executable, least-privilege, content-addressed, replay-verified, and separately promoted. Domain-specific results do not establish universal cost collapse. |
| Multi-turn preference optimization | 2024 [DMPO](https://arxiv.org/abs/2406.14868) | Multi-turn preferences require occupancy/length-aware treatment rather than naively applying single-turn DPO to entire transcripts. | DMPO remains an exterior training option. Evidence certificates and promotion evaluation are stricter than the training loss. |
| Least privilege | 2025 [Progent](https://arxiv.org/abs/2504.11703) and 2025 [MiniScope](https://arxiv.org/abs/2512.11147) | Deterministic, fine-grained tool policy and permission hierarchies outside model discretion. | Natural-language safety prompts never substitute for kernel enforcement. |
| Sandbox mechanism | Linux [Landlock documentation](https://www.kernel.org/doc/html/latest/userspace-api/landlock.html) and Bubblewrap’s [official security notes](https://github.com/containers/bubblewrap) | Layer namespaces, no-new-privileges, filesystem policy, network denial, seccomp/LSM where available, and explicit probes. | Bubblewrap states that policy arguments determine protection; “uses bwrap” alone is not a containment claim. Setuid mode is disallowed, especially in light of the 2026 [setuid advisory](https://github.com/containers/bubblewrap/security/advisories/GHSA-xq78-7hw4-5jvp). |
| Provenance | W3C [PROV publications](https://www.w3.org/groups/wg/prov/publications/) and [SLSA v1.2 provenance](https://slsa.dev/spec/v1.2/provenance) | Represent entities, activities, agents, derivations, inputs, builders, and immutable subjects. | A hash chain proves integrity/order, not semantic truth; exterior verdicts remain necessary. |
| Evolutionary harness search | Google DeepMind’s 2025 [AlphaEvolve](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) and ICLR 2026 [Darwin Gödel Machine](https://openreview.net/pdf?id=pUpzQZTvGY) | Candidate populations plus objective evaluation can improve algorithms/harnesses. | No in-place self-rewrite; candidates pass AETHER’s external, paired release pipeline. |
| Preference optimization | Original [DPO paper](https://arxiv.org/abs/2305.18290) | A precise pairwise objective can train a policy without an explicit learned reward model. | The pair label must be evidence-derived and unforgeable; DPO is not itself an evaluator. |
| Schema dialect | Official [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12) | Strict dialect declaration, `$defs`, conditional validation, and closed objects. | Referential integrity and graph semantics still require a compiler; schema validation alone is insufficient. |
| Canonical identity and durable state | [RFC 8785 JCS](https://www.ietf.org/rfc/rfc8785.html) and SQLite’s [WAL specification](https://www.sqlite.org/wal.html) | Deterministic signature/hash preimages and recoverable, concurrent-reader event persistence. | JCS gives canonical bytes, not truth. WAL gives persistence/concurrency properties, not application-level exactly-once effects. |

### 1.4 Forensic snapshot

Verified facts, not roadmap claims:

- `vanguard/packages/kernel/dispatch.py` implements S0–S12 with S2 before lease, S8 verification after reservation, durable S8a intent before S9, actual-cost S10 commit, S11 release before S12 emit.
- At Git `67e1803`, the kernel architecture gate reports **1365 logical LOC across 9 files**, leaving 73 LOC beneath the `<=1438` limit. This is a hard warning against putting orchestration or learning in the TCB.
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

The graph is a **composition graph**, never a runtime workflow graph. It declares named nodes, typed interfaces, and connections, then freezes them into $D_H$. Debate, tree search, generator–critic, reflection, and swarm algorithms execute inside planner/controller components over the same turn mechanism. This preserves ADR-0003 and ADR-0069: there is one episode loop, not an accumulating family of privileged schedulers.

### 2.3 Stigmergic swarm through the State Plane

For $N$ agents, an all-to-all round has at most $N(N-1)$ directed peer messages and therefore $O(N^2)$ message edges. That bound applies only to a full mesh; sparse peer topologies can be $O(N)$. A state-mediated design instead has agents publish and consume typed work claims, artifacts, observations, and terminal summaries through the ledger/blob/index surfaces. If each agent performs at most $c$ state operations per round, coordination operations are $O(cN)$, while contention and query cost depend on indexing and hot keys.

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
| **D — Digests** | $D_H$, $D_R$, and $D_X$ are conceptually separated and partially implemented. | Require all three at promotion boundaries and never substitute one for another. |

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

`harness_digest` carries $D_H$ only. A changed model fingerprint changes $D_R$; a changed benchmark item changes $D_X$. “Same harness” is not “same execution.”

### 2.5 Tier S+ reference architecture — the Verified Adaptive Obligation Harness

VAOH composes the strongest compatible ideas from the proposal set without moving a single policy into the TCB:

```text
 USER GOAL
    │
    ▼
 admission: goal digest + witness contract + 6D ceiling + safety class
    │
    ▼
┌──────────────────── DECISION PLANE — exterior, replaceable ────────────────────┐
│ Context bottleneck Bφ │ VFE belief update │ Pareto/EFE router │ graph policy  │
│ refinement quotes     │ model/tool choice │ swarm width       │ escalation    │
└────────────────────────────────┬───────────────────────────────────────────────┘
                                 │ typed proposal only
                                 ▼
┌──────────────────── AUTHORITY MECHANISM — fixed TCB ───────────────────────────┐
│ universal turn loop → S0–S12 → attenuation → 6D lease → durable intent       │
│ no planner, obligation market, optimizer, learner, domain, or macro compiler  │
└────────────────────────────────┬───────────────────────────────────────────────┘
                                 │ receipts / attributed observations
                                 ▼
┌──────────────────── STATE PLANE — authoritative order ─────────────────────────┐
│ SQLite WAL envelopes │ obligation/claim projection │ BlobStore artifact refs  │
│ provenance DAG       │ checkpoints                │ rebuildable search index │
└────────────────────────────────┬───────────────────────────────────────────────┘
                                 │ subject-bound evidence request
                                 ▼
┌──────────────────── EVIDENCE PLANE — exterior truth ───────────────────────────┐
│ deterministic witness checkers │ UID 10002 │ signed verdict │ pair certificate │
└────────────────────────────────┬───────────────────────────────────────────────┘
                                 │ eligible corpus only
                                 ▼
┌──────────────────── COMPOUNDING PLANE — exterior/offline ──────────────────────┐
│ T0 witness memo │ T1 macro compiler │ T2 skill/router │ T3 DPO/harness search │
└────────────────────────────────────────────────────────────────────────────────┘
```

The “Compounding Plane” is a deployment view, not a fourth authority plane. Its services are ordinary runtime clients/plugins with narrower capabilities than the work they analyze. They consume signed projections and can publish candidates; they cannot write verdicts, grants, budget events, or default pointers.

The architecture has four nested loops:

| Loop | Frequency | Mutable state | Gate |
|---|---|---|---|
| **L0 — effect loop** | Every tool/effect | Episode state and receipts | S0–S12, current lease. |
| **L1 — episode control loop** | Every turn | Belief, context projection, open obligations | Frozen harness, profile, and remaining budget. |
| **L2 — experiment loop** | Across paired runs | Candidate harness/model/skill/macro statistics | Exterior verdicts, immutable trial plan. |
| **L3 — promotion loop** | Rare release decision | Registry default pointer | Pareto safety gate, exact paired statistics, promotion authority/human. |

No inner loop may perform an outer-loop transition. In particular, an episode cannot promote what it produced.

### 2.6 Stigmergic State Plane as a typed obligation frontier

Define the shared informational state as:

\[
\mathcal W_t=\langle \mathcal A_t,\mathcal O_t,\mathcal E_t,\mathcal M_t\rangle,
\]

where $\mathcal A$ is the content-addressed artifact set, $\mathcal O$ the obligation/claim projection, $\mathcal E$ the evidence and provenance projection, and $\mathcal M$ measured telemetry plus rebuildable memory indices. $\mathcal W$ is reduced from authoritative events and immutable blobs; it is not an unowned mutable Python dictionary and not a transcript.

The schedulable unit is:

\[
o=\langle g,w,\mathbf R_{max},d,\mathcal D,p,\kappa\rangle,
\]

with goal specification $g$, witness contract $w$, six-dimensional ceiling $\mathbf R_{max}$, deadline $d$, dependency refs $\mathcal D$, parent $p$, and protection/capability class $\kappa$. Its identity is:

\[
D_O=H(\operatorname{JCS}(g,w,\mathbf R_{max},d,\mathcal D,p,\kappa)).
\]

A refinement rule $r$ can either produce a candidate witness or decompose the obligation:

\[
\operatorname{Refine}_r(o)\rightarrow
\begin{cases}
\widehat w(o), & \text{candidate discharge},\\
\{o_1,\dots,o_m\},\Gamma, & \text{children plus a declared composition rule }\Gamma.
\end{cases}
\]

The root is discharged only when every required witness verifies and $\Gamma$ is accepted by the pack’s exterior checker. For fuzzy domains, `adjudicated_by(panel)` or `signed_by(human)` is an explicit lower-assurance witness type; an LLM-rendered assertion never silently becomes a formal witness.

Workers coordinate by a pull protocol:

1. publisher records an obligation ref and required interface;
2. a worker requests an exclusive claim with expected version and sublease;
3. the runtime performs compare-and-swap on the reduced version and binds the lease to the claimant;
4. the worker proposes effects only through its attenuated principal;
5. it publishes immutable artifact/witness refs and returns the claim;
6. expiry or crash releases the claim after intent reconciliation; it does not imply re-execution of an uncertain external effect.

There is no correctness theorem that shared state makes coordination $O(N)$. The bounded claim is: if each of $N$ logical agents performs at most $c$ indexed state operations per scheduling round, coordination envelopes are $O(cN)$. The M-7/M-9 measurement must separately report model calls, coordination envelopes, bytes read/written, WAL lock time, hot-key contention, retries, and critical-path latency. Full-mesh chat is $O(N^2)$ only when every agent addresses every other agent.

### 2.7 Pareto harness — feasibility first, optimization second

For each open obligation $o$, candidate refinement $r$, model tier $m$, context policy $b$, and swarm width $k$, the controller obtains a quote:

\[
q=(o,r,m,b,k,\widehat{\mathbf c},\widehat p_{pass},\widehat I,\widehat q_{evidence}),
\]

where $\widehat{\mathbf c}$ is predicted 6D consumption, $\widehat p_{pass}$ calibrated success probability, $\widehat I$ expected information gain, and $\widehat q_{evidence}$ the assurance class of the proposed witness. Quotes are advisory. The kernel authorizes only concrete effects and commits measured cost.

The controller applies a lexicographic gate:

1. capability, selector, isolation, evidence, and hard-safety constraints;
2. six-dimensional lease feasibility and dependency readiness;
3. minimum witness/quality floor;
4. nondominance on expected success, epistemic value, cost, tokens, latency, and risk;
5. declared product preference among the remaining Pareto set.

For a bounded scheduling epoch, the allocation problem is:

\[
\max_{x}\quad
\left(
\sum_qx_q\widehat p_{pass,q}V_q,
\sum_qx_q\widehat I_q,
-\sum_qx_q\widehat{\mathbf c}_{q}^{add},
-\operatorname{critical\_path}(x)
\right)
\]

subject to, for each additive dimension $j$,

\[
\sum_qx_q\widehat c_{q,j}\le R_{remaining,j},
\quad x_q\in\{0,1\},
\]

plus worker count, dependency, exclusivity, turn, depth, protection, and quality constraints. The runtime may use a Lagrangian or bandit approximation to choose locally, but it must retain the original vector and constraint results in telemetry. A weighted score may rank feasible choices; it may not average away a failed invariant or decide release promotion.

Operational profiles are versioned priors, not promises:

| Profile | Prior | Initial topology | Escalation rule |
|---|---|---|---|
| `flash` | Minimize latency/cost under an ordinary witness floor. | Memo/macro first, then one small worker. | Escalate only on verifier failure, low calibrated confidence, or an explicit ambiguity trigger. |
| `balanced` | Minimize expected cost-per-signed-pass. | Scout/context projection then one executor and oracle. | Add context, stronger model, or one critic according to marginal expected value. |
| `certain` | Maximize assurance subject to the ceiling. | Multiple independent candidates and strengthened witness. | Spend on disagreement resolution, proof, or adversarial evaluation—not repetitive prose. |
| `frontier` | Maximize information gain under an experiment budget. | Diverse refinement rules / controlled branches. | Stop at preregistered information or budget boundary; results cannot auto-promote. |
| `adaptive` | Begin with the cheapest feasible policy and re-plan after evidence. | Dynamic. | Every escalation is a new authorized reservation; no self-estimated ROI can renew a lease implicitly. |

Context selection is part of the same control problem. A bottleneck $\mathcal B_\phi(\mathcal W,o,k)$ projects attributed refs into at most $k$ tokens/bytes. It must disclose omissions, source digests, protection labels, and compaction lineage. Higher compression that hides a failing invariant is not an optimization.

### 2.8 Active Inference binding

VAOH does not use “Active Inference” as branding for a weighted reward. Its operational mapping is exact:

| Active-Inference term | AETHER object |
|---|---|
| observation $o_t$ | Reduced ledger facts, receipts, artifact metadata, and signed evaluator evidence. |
| latent state $s_t$ | Task progress, dependency validity, failure class, tool/model reliability, and unresolved uncertainty. |
| action/policy $\pi$ | A refinement quote: component-graph path, model route, context projection, tool/macro, and optional child topology. |
| preferences $p_C(o)$ | Preregistered witness success, invariant preservation, and economic bounds. |
| VFE $\mathcal F$ | Belief-fit objective after observations. |
| EFE $\mathcal G$ | Feasible next-policy objective combining pragmatic and epistemic value. |

The controller records predicted distributions before execution and settled observations after execution. Calibration error is therefore measurable. A policy that systematically understates cost or overstates pass probability loses routing probability; it does not gain a larger authority ceiling.

### 2.9 The compounding flywheel and macro-tool compilation

The flywheel begins deterministically and becomes statistical only when sufficient evidence exists:

| Tier | Mechanism | Earliest milestone | Promotion condition |
|---|---|---|---|
| **T0 — witness memo** | Reuse an already verified witness for an identical obligation cell. | M-5 | Exact cache-key and validity match; no learning or benchmark power required. |
| **T1 — macro-tool compiler** | Anti-unify recurring verified effect subgraphs into a typed executable candidate. | Candidate pipeline M-8/M-9 | Replay equivalence, least privilege, adversarial negatives, paired cost/pass evidence. |
| **T2 — skill and router adaptation** | Retrieve procedural cards and update calibrated quote/routing priors. | M-9 | Evidence-backed lift; rating affects retrieval only until separately promoted into $D_H$. |
| **T3 — model/harness learning** | DPO/DMPO, graph credit, manifest mutation, evolutionary search. | M-10 | Signed pairs, held-out paired protocol, Pareto safety, exact statistics, human pointer promotion. |

#### T0 — safe deterministic memoization

The memo key is not merely natural-language goal text:

\[
K_{memo}=H(D_O\parallel D_{inputs}\parallel D_{environment}\parallel
D_{witness\ checker}\parallel D_{toolchain}\parallel assurance\parallel policy\ version).
\]

A cache hit returns the original signed witness bundle by reference. It is invalid if any bound input, environment, checker, revocation epoch, expiry, protection class, or policy version is incompatible. Non-deterministic/freshness-sensitive obligations require an explicit TTL or replay check. Memoization never copies a verdict onto a different subject digest.

#### T1 — verified macro-tool compiler

A macro-tool is not a prompt snippet. It is a content-addressed, typed, least-privilege executable artifact that replaces a recurring multi-turn effect subgraph while preserving externally observed semantics.

Compilation pipeline:

```text
eligible signed trajectories
  → mine frequent causally connected effect subgraphs
  → anti-unify values into typed parameters
  → infer minimum interface and selector ceiling from receipts
  → synthesize workflow IR or implementation candidates
  → generate positive replay + adversarial/property tests
  → run in ordinary worker sandbox through S0–S12
  → evaluate with the original exterior witness checker
  → compare macro vs expanded baseline on held-out paired obligations
  → publish candidate plugin artifact
  → human promotion changes registry/default pointer
```

Eligibility requires evidence-complete trajectories, signed pass, no alarm/tamper/instrument error, stable interfaces, explicit license/protection compatibility, and enough distinct task/input support to avoid memorizing a single fixture. Constants such as paths, secrets, task answers, tenant IDs, and evaluator-private values must not be captured during anti-unification.

Capability inference is conservative:

\[
C_{macro}=\operatorname{hull}\left(\bigcup_{v\in subgraph}C_v\right)
\cap C_{pack}\cap C_{publisher},
\]

where `hull` is the least representable selector set covering observed required effects—not `*`. The candidate is rejected if the selector algebra cannot express a narrow ceiling. Its execution cost includes dispatch, sandbox, verification, and fallback overhead; token collapse is measured, never assumed.

The compiler may emit a portable workflow IR interpreted by an allowlisted runner or source/bytecode for a registered language runtime. Language is metadata. Authority is the same typed effect protocol. A Python, Rust, WASM, shell, or proof-tactic implementation receives no privilege from its format.

#### T2/T3 — statistical compounding

Skill cards and learned routers reduce search/context costs; DPO/DMPO distills evidence-selected choices into model policies; harness evolution mutates the named graph. These are separate treatments and must not be changed simultaneously in a pair unless a factorial protocol attributes them. The deterministic baseline and every rejected candidate remain reproducible.

### 2.10 Tier S+ invariants

The synthesis is accepted only if all of the following remain true:

1. **One mechanism:** obligations, macros, critics, swarms, and learned policies reduce to ordinary turns/effects; no second driver.
2. **Authority monotonicity:** state, price, posterior belief, skill rating, or cached success can never widen a capability.
3. **Evidence exteriority:** only the bound exterior writer can mint promotion-eligible verdicts.
4. **Identity completeness:** every composition, execution, experiment, obligation, witness, memo, and macro candidate is content-addressed over its semantic inputs.
5. **Single writer:** projections and indices may be many; privileged event-kind ownership remains singular.
6. **State-plane attribution:** every claim, result, and artifact has a principal, lease, lineage, and digest.
7. **Pareto honesty:** raw vectors and hard constraints are preserved; no scalar hides a safety/evidence regression.
8. **Causal humility:** graph credit ranks interventions; chronology or attention never establishes cause.
9. **Compounding reversibility:** caches can invalidate, skills can archive, candidates can lose, and default pointers can roll back without deleting evidence.
10. **TCB austerity:** optimizer, scheduler, learner, retriever, and compiler live outside `kernel/`; the `<=1438` gate remains binding.

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
- `obligation-pareto`: obligation source → quote providers → Pareto selector → lease-bound refiners → witness composer.

All six must compile without a diff to kernel or episode engine. If one requires a new engine branch, the graph is not general enough.

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

Forgery maps to `instrument_error`, `inconclusive`, or `EvaluationTampered` as the active contract dictates; it never silently degrades to declared absence. The declaration is frozen into $D_H$, so it cannot be selected after observing the result.

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
- budgets, depth, parent lineage, $D_H$, and $D_R$ survive reconstruction;
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

---

## 4. Proposed append-only ADR catalog

The following are complete drafts. Their numbers are reserved proposals, not accepted records. If the Director chooses different decisions, the rejected drafts should not be silently edited into acceptance; record the final decision append-only.

### ADR-0077 — Named Component Graph and `mhf.manifest/2`

**Status:** Proposed  
**Date:** 2026-08-21  
**Deciders:** Engineering Director, CTO, Principal Systems Architect  
**Requirements:** REQ-MAN2-001…008  
**Supersedes after migration:** `mhf.harness/1` fixed plugin binding surface and v4 hard-coded component-role surface; does not supersede frozen composition, ADR-0003, ADR-0069, or ADR-0072.

#### Context

The fixed pack surface cannot express debate, critic/reviser loops, tree search, or swarms without adding another privileged engine. The v4 manifest has an open map syntactically but only a closed consumer table semantically. Because $D_H$ covers the manifest, delaying the correction until after the corpus grows makes migration and attribution substantially more expensive.

#### Decision

1. A harness is a named, typed **composition graph** compiled once into an immutable `FrozenHarness`.
2. Nodes refer to data or executable components; edges bind provided to required namespaced interfaces. The schema does not prescribe a workflow schedule.
3. Unknown refs, unregistered interfaces, missing required endpoints, endpoint type mismatch, duplicate bindings where cardinality is one, capability widening, unconsumed authority-bearing nodes, and mutable/unpinned resolved artifacts fail composition.
4. Graph cycles are legal. Runtime termination is enforced by economic/structural budgets.
5. Every ref resolves to a content digest. The JCS-normalized resolved graph—including configs, isolation, evidence mode, capability intersections, endpoints, and edges—defines $D_H$.
6. The runtime continues to expose one `Runtime.compose` and one execution authority. No alternate YAML runtime is created.
7. `mhf.harness/1` and the current v4 format receive read-only migration adapters for one release. Writers emit only `mhf.manifest/2`; adapters are removed by v0.7.0.
8. Namespaced interface strings, not a growing enum in kernel, provide extensibility. Interface implementations still resolve through registered ports and wire contracts.

#### Normative Draft 2020-12 schema

Target: `schemas/mhf/manifest_v2.schema.json`. YAML is permitted only as an input serialization; after safe parsing it must validate as this JSON data model. References to the existing selector schema are normative, not placeholders.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://vanguard.dev/schemas/mhf/manifest_v2.schema.json",
  "title": "MHF Named Component Graph Manifest",
  "description": "mhf.manifest/2; compiled and JCS-frozen before execution",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema", "id", "components", "connections", "entrypoints",
    "capabilities", "budget", "evidence", "undeletable"
  ],
  "properties": {
    "schema": { "const": "mhf.manifest/2" },
    "id": { "$ref": "#/$defs/Name" },
    "description": { "type": "string", "maxLength": 4096 },
    "components": {
      "type": "object",
      "minProperties": 1,
      "propertyNames": { "$ref": "#/$defs/Name" },
      "additionalProperties": { "$ref": "#/$defs/Component" }
    },
    "connections": {
      "type": "array",
      "items": { "$ref": "#/$defs/Connection" }
    },
    "entrypoints": {
      "type": "object",
      "minProperties": 1,
      "propertyNames": { "$ref": "#/$defs/Interface" },
      "additionalProperties": { "$ref": "#/$defs/Endpoint" }
    },
    "capabilities": {
      "type": "array",
      "items": { "$ref": "#/$defs/Capability" }
    },
    "budget": { "$ref": "#/$defs/Budget6D" },
    "evidence": { "$ref": "#/$defs/EvidencePolicy" },
    "metadata": {
      "type": "object",
      "additionalProperties": {
        "type": ["string", "integer", "boolean", "null"]
      }
    },
    "undeletable": { "type": "boolean" }
  },
  "$defs": {
    "Name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 128,
      "pattern": "^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$"
    },
    "Interface": {
      "type": "string",
      "minLength": 3,
      "maxLength": 160,
      "pattern": "^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)+/[1-9][0-9]*$"
    },
    "Digest": {
      "type": "string",
      "pattern": "^sha256:[0-9a-f]{64}$"
    },
    "ComponentRef": {
      "type": "string",
      "minLength": 3,
      "maxLength": 256,
      "pattern": "^[a-z][a-z0-9._-]+@(?:[0-9]+(?:\\.[0-9]+){0,2}|sha256:[0-9a-f]{64}|[~^><=0-9., -]+)$"
    },
    "Interfaces": {
      "type": "object",
      "additionalProperties": false,
      "required": ["provides", "requires"],
      "properties": {
        "provides": {
          "type": "array",
          "items": { "$ref": "#/$defs/Interface" },
          "uniqueItems": true
        },
        "requires": {
          "type": "array",
          "items": { "$ref": "#/$defs/Interface" },
          "uniqueItems": true
        }
      }
    },
    "Execution": {
      "type": "object",
      "additionalProperties": false,
      "required": ["mode"],
      "properties": {
        "mode": {
          "enum": ["data", "in_process", "subprocess", "exterior"]
        },
        "grant_ref": { "$ref": "#/$defs/Digest" },
        "image_digest": { "$ref": "#/$defs/Digest" },
        "uid": { "type": "integer", "minimum": 1 },
        "protocol": { "$ref": "#/$defs/Interface" }
      },
      "allOf": [
        {
          "if": { "properties": { "mode": { "const": "in_process" } } },
          "then": { "required": ["grant_ref"] }
        },
        {
          "if": {
            "properties": { "mode": { "enum": ["subprocess", "exterior"] } }
          },
          "then": { "required": ["protocol"] }
        }
      ]
    },
    "Component": {
      "type": "object",
      "additionalProperties": false,
      "required": ["ref", "interfaces", "execution", "capability_requests", "config"],
      "properties": {
        "ref": { "$ref": "#/$defs/ComponentRef" },
        "expected_digest": { "$ref": "#/$defs/Digest" },
        "interfaces": { "$ref": "#/$defs/Interfaces" },
        "execution": { "$ref": "#/$defs/Execution" },
        "capability_requests": {
          "type": "array",
          "items": { "$ref": "#/$defs/Name" },
          "uniqueItems": true
        },
        "config": { "type": "object" }
      }
    },
    "Endpoint": {
      "type": "object",
      "additionalProperties": false,
      "required": ["component", "interface"],
      "properties": {
        "component": { "$ref": "#/$defs/Name" },
        "interface": { "$ref": "#/$defs/Interface" }
      }
    },
    "Connection": {
      "type": "object",
      "additionalProperties": false,
      "required": ["from", "to", "delivery"],
      "properties": {
        "from": { "$ref": "#/$defs/Endpoint" },
        "to": { "$ref": "#/$defs/Endpoint" },
        "delivery": { "enum": ["call", "stream", "state_ref", "evidence_ref"] },
        "cardinality": { "enum": ["one", "many"] },
        "required": { "type": "boolean", "default": true }
      }
    },
    "Capability": {
      "type": "object",
      "additionalProperties": false,
      "required": ["id", "verb", "sink", "selector", "risk"],
      "properties": {
        "id": { "$ref": "#/$defs/Name" },
        "verb": { "$ref": "#/$defs/Name" },
        "sink": { "enum": ["pure", "observation", "privileged"] },
        "selector": { "$ref": "../v4/resource-selector.schema.json" },
        "risk": { "enum": ["low", "medium", "high", "critical"] }
      }
    },
    "Budget6D": {
      "type": "object",
      "additionalProperties": false,
      "required": ["usd_micros", "tokens", "bytes", "millis", "turns", "depth"],
      "properties": {
        "usd_micros": { "type": "integer", "minimum": 0 },
        "tokens": { "type": "integer", "minimum": 0 },
        "bytes": { "type": "integer", "minimum": 0 },
        "millis": { "type": "integer", "minimum": 0 },
        "turns": { "type": "integer", "minimum": 1 },
        "depth": { "type": "integer", "minimum": 0 }
      }
    },
    "EvidencePolicy": {
      "type": "object",
      "additionalProperties": false,
      "required": ["mode", "evaluators", "assurance_class", "promotion_eligible"],
      "properties": {
        "mode": { "enum": ["required", "absent"] },
        "evaluators": {
          "type": "array",
          "items": { "$ref": "#/$defs/Name" },
          "uniqueItems": true
        },
        "assurance_class": {
          "enum": ["verified", "exploratory", "diagnostic"]
        },
        "promotion_eligible": { "type": "boolean" },
        "absence_reason": {
          "type": "string",
          "enum": [
            "no_correctness_claim", "compute_only_exploration",
            "observation_only", "diagnostic_run"
          ]
        }
      },
      "allOf": [
        {
          "if": { "properties": { "mode": { "const": "required" } } },
          "then": {
            "properties": {
              "evaluators": { "minItems": 1 },
              "assurance_class": { "const": "verified" },
              "promotion_eligible": { "const": true }
            }
          }
        },
        {
          "if": { "properties": { "mode": { "const": "absent" } } },
          "then": {
            "required": ["absence_reason"],
            "properties": {
              "evaluators": { "maxItems": 0 },
              "assurance_class": { "enum": ["exploratory", "diagnostic"] },
              "promotion_eligible": { "const": false }
            }
          }
        }
      ]
    }
  }
}
```

Schema validation is followed by these mandatory semantic passes:

```text
P0 parse with no aliases/duplicate keys → P1 Draft-2020-12 validation
→ P2 resolve each ref and verify expected digest
→ P3 validate endpoint existence and provided/required interface compatibility
→ P4 validate entrypoint cardinality and reject unconsumed authority-bearing nodes
→ P5 intersect harness, component, principal and request capability ceilings
→ P6 construct lifecycle cells and verify isolation/protocol/image/UID
→ P7 JCS-freeze the fully resolved graph and derive D_H
→ P8 activate only from that FrozenHarness
```

#### Consequences

Positive: topologies become pack data; attribution is per named node; graph mutation is JCS-diffable; model routes and evaluators are ordinary components without becoming untrusted authority. Cost: one schema/digest migration, compiler work, pack rewrites, and explicit compatibility removal.

#### Rejected alternatives

- Keep fixed slots and add one slot per new algorithm: rejected as engine-by-enum.
- Adopt a workflow DAG runtime: rejected by ADR-0003 and because cycles/search are policy, not trusted mechanism.
- Permit runtime discovery/hot mutation: rejected; composition freezes before execution.

#### One bound falsifier

`test/contracts/test_manifest_v2_graph.py::ManifestV2GraphFalsifier.test_six_topologies_compile_without_kernel_or_engine_change` snapshots the kernel/episode public sources, compiles the six required profiles twice, asserts stable $D_H$, and fails on an unknown/unconsumed interface. Any source diff or profile-specific engine branch is red.

---

### ADR-0078 — Evidence Guardrail States: Required, Declared Absent, or Forged

**Status:** Proposed  
**Date:** 2026-08-21  
**Deciders:** Engineering Director, CIO, Principal Staff Engineer  
**Requirements:** REQ-EVID-001…007

#### Context

Requiring a coding oracle for every domain would make generality dishonest; allowing missing evaluation to masquerade as success would make evidence dishonest. “Optional evaluator” conflates intentional absence with broken or forged evidence.

#### Decision

1. The frozen manifest declares `evidence.mode` before execution.
2. `required` demands at least one registered exterior evaluator and a signed verdict bound to $D_X$, oracle/image identity, subject artifacts, and protocol.
3. `absent` requires an enumerated reason and forces `promotion_eligible=false`. Operational completion remains distinct from evidence outcome.
4. Claimed, required, or expected evidence that is missing, unsigned, self-issued, wrong-key, wrong-image, wrong-subject, wrong-protocol, unreachable, or tampered is **forged/broken**, never absent.
5. Declared-absent runs cannot mint `passed`, license verdict-gated memory, supply chosen/rejected labels, enter promotion statistics, or change a default registry pointer.
6. Sandboxing, capability checks, and budgets remain mandatory regardless of evidence mode.
7. Absence/forgery state and reason are ledgered and carried into the trajectory.

Normative outcome fragment:

```json
{
  "$defs": {
    "EvidenceOutcome": {
      "oneOf": [
        {
          "type": "object",
          "additionalProperties": false,
          "required": ["state", "verdict"],
          "properties": {
            "state": { "const": "verified" },
            "verdict": { "type": "object" }
          }
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": ["state", "reason"],
          "properties": {
            "state": { "const": "declared_absent" },
            "reason": { "type": "string" }
          }
        },
        {
          "type": "object",
          "additionalProperties": false,
          "required": ["state", "reason"],
          "properties": {
            "state": { "const": "forged_or_broken" },
            "reason": { "type": "string", "minLength": 1 }
          }
        }
      ]
    }
  }
}
```

#### Consequences

Non-coding exploratory packs can be honest without inventing an oracle. Promotion remains evidence-backed. UI and reducers must show `not_evaluated` separately from pass/fail/inconclusive.

#### Rejected alternatives

- Mandatory evaluator for every pack: rejected as false generality.
- Nullable verdict with no declaration: rejected because missingness is ambiguous and gameable.
- Let the agent self-grade when exterior evaluation is absent: rejected as forgery.

#### One bound falsifier

`test/trust/test_evidence_guardrail_states.py::EvidenceGuardrailFalsifier.test_required_absent_and_forged_are_disjoint` runs three frozen fixtures and asserts respectively signed eligibility, explicit non-eligibility, and fail-closed instrument/tamper status. Any path that converts the latter two to `passed` is red.

---

### ADR-0079 — Canonical Plugin Lifecycle, Composition Absorption, and Layer-0 Retirement

**Status:** Proposed  
**Date:** 2026-08-21  
**Deciders:** Engineering Director, Principal Systems Architect, Tech Lead  
**Requirements:** REQ-PLUG-001…010  
**Retires on completion:** all of `layer0/`.

#### Context

Plugin lifecycle/broker and composition behavior remain in a copy-fork. The Layer-0 compiler discards the computed capability intersection. Its alternate event machinery conflicts with the canonical package writer. The current seven-state FSM also has no event for discovery or verification.

#### Decision

1. Port registry/compose semantics into `vanguard/packages/runtime/registry/` and the existing runtime composition root; shared pure values/contracts remain in domain/ports only where allowed by the lattice.
2. Use the canonical `LedgerEmitter` and `EventStorePort`; no second store, envelope, taxonomy, or writer survives.
3. Add `PluginDiscovered` and `PluginVerified` to the event schema/generated enum/reducer/writer table so every state entry is auditable. Registry is their sole writer.
4. Apply capability intersections as immutable activation inputs. An empty intersection denies all effect execution.
5. Activation is atomic with respect to health/isolation verification. A broker/process failure moves the cell to `FAULTED` before it can be observed as active.
6. `FAULTED` has no recovery transition; retirement is required before rediscovery creates a new cell identity.
7. Delete all `layer0/` only after package-path parity plus NOVA-4 is green.

#### Complete lifecycle FSM

| Current state | Operation | Target | Ledger event on entry | Required payload/evidence | Illegal alternatives |
|---|---|---|---|---|---|
| — | discover | `DISCOVERED` | `PluginDiscovered` | plugin/cell ID, manifest node, requested ref, $D_H$ | Anonymous cell creation |
| `DISCOVERED` | resolve | `RESOLVED` | `PluginResolved` | resolved content digest, version, source registry | Mutable/unpinned ref |
| `DISCOVERED` | fault | `FAULTED` | `PluginFaulted` | from/to, reason code, stage | Remain discovered after fatal error |
| `RESOLVED` | verify | `VERIFIED` | `PluginVerified` | signature/image/protocol/interface/ceiling verification digests | Self-asserted verification |
| `RESOLVED` | fault | `FAULTED` | `PluginFaulted` | reason and failed proof | Activate anyway |
| `VERIFIED` | activate | `ACTIVATED` | `PluginActivated` | effective ceiling digest, isolation identity, health receipt | Activation before freeze |
| `VERIFIED` | fault | `FAULTED` | `PluginFaulted` | reason | Retry in same cell |
| `ACTIVATED` | quiesce | `QUIESCING` | `PluginQuiesced` | outstanding leases, deadline, cause | New work admission |
| `ACTIVATED` | fault | `FAULTED` | `PluginFaulted` | broker/health reason; revoke admission | Stay active |
| `QUIESCING` | retire | `RETIRED` | `PluginRetired` | zero open leases/process stopped/final digest | Return to active |
| `QUIESCING` | fault | `FAULTED` | `PluginFaulted` | shutdown failure | Silent disappearance |
| `FAULTED` | retire | `RETIRED` | `PluginRetired` | cleanup outcome and prior fault event ID | Direct reactivation |
| `RETIRED` | — | — | — | terminal | Any transition |

Event payload schema shared by all transitions:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["plugin_id", "cell_id", "from_state", "to_state", "composition_digest"],
  "properties": {
    "plugin_id": { "type": "string", "minLength": 1 },
    "cell_id": { "type": "string", "minLength": 1 },
    "from_state": {
      "type": ["string", "null"],
      "enum": [null, "discovered", "resolved", "verified", "activated", "quiescing", "faulted"]
    },
    "to_state": {
      "enum": ["discovered", "resolved", "verified", "activated", "quiescing", "retired", "faulted"]
    },
    "composition_digest": { "type": "string", "pattern": "^sha256:[0-9a-f]{64}$" },
    "component_digest": { "type": "string", "pattern": "^sha256:[0-9a-f]{64}$" },
    "effective_ceiling_digest": { "type": "string", "pattern": "^sha256:[0-9a-f]{64}$" },
    "reason_code": { "type": "string" },
    "evidence_refs": { "type": "array", "items": { "type": "string" } }
  }
}
```

#### Consequences

The copy-fork disappears and event authority becomes coherent. Two event kinds and their schema/golden vectors are added, but no new writer role is created.

#### Rejected alternatives

- Keep Layer-0 as a compatibility subsystem: rejected as two production truths.
- Copy the old event store into runtime: rejected as split State Plane.
- Preserve silent discovered/verified transitions: rejected because activation provenance would be incomplete.

#### One bound falsifier

`test/runtime/registry/test_nova4_retirement.py::Layer0RetirementFalsifier.test_package_registry_owns_full_fsm_and_all_six_negatives` runs every legal/illegal transition and NOVA-4, then asserts `rg`-equivalent import/file checks find no `layer0` runtime dependency or directory. Any discarded ceiling or non-registry `Plugin*` write is red.

---

### ADR-0080 — Universal Turn Mechanism, Typed Obligations, and Deferred Capability-Mediated Delegation

**Status:** Proposed  
**Date:** 2026-08-21  
**Deciders:** Engineering Director, Principal Systems Architect, PhD AI Specialist  
**Requirements:** REQ-LOOP-001…006, REQ-SPAWN-001…010, REQ-OBL-001…010

#### Context

The system needs a public substrate claim narrow enough to falsify. Recursive algorithms also need a safe, caller-visible delegation mechanism, but putting spawn directly in planner APIs would create an authority bypass and expanding the kernel before the foundation proof would violate sequencing.

#### Decision

1. Publish the Universal Turn Loop only as the mechanism in T-6.
2. All task/topology semantics remain components/policy; every effect remains an `EffectRequest` through S0–S12.
3. Preserve engine-owned spawn as semantic reference through M-5.
4. Implement `agent.spawn` in M-6 as a privileged, registered effect using the exact S0–S12 mapping in T-2.
5. Bind objective, graph entrypoint, child authority, selectors, sublease, depth, workspace mode, and context refs into the descriptor/grant.
6. Emit `ChildSpawned` only after durable intent and child creation; emit `ChildReturned` with causation/correlation and untrusted return provenance. Failure never upgrades trust.
7. A parent cannot delegate authority or budget it does not currently hold. Unknown subset comparison denies.
8. No child can access evaluator secrets, parent operator context, unreferenced workspace paths, or live parent handles.
9. Implement typed obligations only after M-6, as an M-7 State-Plane projection over ordinary events, blobs, claims, leases, and child episodes—not as a second workflow runtime.
10. An obligation binds goal digest, witness contract, 6D ceiling, dependencies, parent, deadline, and protection class. Worker return does not discharge it; only a bound accepted witness does.
11. Claims are exclusive, compare-and-swap versioned, principal-bound, and lease-bound. Crash/expiry enters reconciliation before reuse; an uncertain effect is never repeated automatically.
12. Refinement/decomposition is policy executed through the same turn loop and is bounded by depth, child count, price, and progress predicates.

Normative spawn request outline:

```json
{
  "schema": "mhf.effect-request/1",
  "verb": "agent.spawn",
  "args": {
    "objective_digest": "sha256:…",
    "entrypoint": "mhf.planner/1",
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

#### Consequences

Recursive policy and pull-based stigmergy become expressible without an agency escape hatch or trusted workflow scheduler. Implementation waits until evidence and generality are established, limiting TCB risk.

#### Rejected alternatives

- Planner calls `spawn()` directly: rejected as unmediated authority.
- New swarm kernel/scheduler: rejected as duplicated mechanism.
- Implement in M-3/M-4: rejected by the Foundation Stop Line.

#### One bound falsifier

`test/trust/test_universal_mechanism.py::UniversalMechanismFalsifier.test_spawn_and_obligation_frontier_reduce_to_mediated_turns_without_widening` instruments stages and the obligation projection, crashes each post-reservation/claim path, and asserts intent-before-child, grant binding, sublease conservation, release, lineage, isolation, exclusive versioned claims, witness-before-discharge, and untrusted return. Any direct child creation before S9, stale-claim commit, worker-self-discharge, second driver, or authority widening is red.

---

### ADR-0081 — Evidence-Complete Trajectories and Cold Continuation

**Status:** Proposed  
**Date:** 2026-08-21  
**Deciders:** CIO, Principal Staff Engineer, Tech Lead  
**Requirements:** REQ-TRAJ-001…012, REQ-RESUME-001…008

#### Context

`mhf.trajectory/1` exists, but the current writer emits fabricated zero vectors and omits identity fields needed for attribution. The WAL can replay state, yet process-independent continuation has not been proved end to end. Learning and concurrency both depend on these facts.

#### Decision

1. NOVA-1 and NOVA-2 close in M-2.
2. Strengthen the writer and schema as `mhf.trajectory/2`; retain a reader for `/1`, marking it `legacy_incomplete` unless it meets `/2` semantics.
3. Every actual model turn records provider, model, fingerprint (or explicit `unavailable` reason), prompt/completion/cache token breakdown, charged milliseconds, byte accounting, context digest/ref policy, proposal, receipts, and effect lineage.
4. Episode totals are checked against turn plus overhead totals. Unknown price is not zero dollars; record price status separately.
5. Require $D_H,D_R,D_X$, resolved component/gene digests, terminal state, evidence outcome, and a pointer to the final WAL event range.
6. A completed episode with a model invocation has at least one turn and each invoked turn has a non-zero measured cost vector. Aborted-before-model episodes may have no turns only with an enumerated termination reason.
7. Suspend/resume reconstructs from ports and ledger reduction in a fresh process. A checkpoint is an optimization, not authority; replay from the authoritative chain must yield the same reduced state.
8. No training/promotion consumer accepts legacy, forged, missing, or non-reconstructible rows.

Required turn shape (abridged only to avoid duplicating proposal/receipt schemas already normative):

```json
{
  "turn": 0,
  "context_digest": "sha256:…",
  "model": {
    "route_tier": 1,
    "provider": "openrouter",
    "model": "provider/model",
    "fingerprint": "sha256:…",
    "fingerprint_status": "measured"
  },
  "usage": {
    "prompt_tokens": 1,
    "completion_tokens": 1,
    "cache_read_tokens": 0,
    "cache_write_tokens": 0,
    "pricing_status": "known"
  },
  "cost": { "usd_micros": 1, "tokens": 2, "bytes": 100, "millis": 10 },
  "proposal": {},
  "receipts": [],
  "event_range": { "first_seq": 1, "last_seq": 9 }
}
```

#### Consequences

Future evidence is learnable and audit-ready; historical weakness remains honestly visible. The runtime must connect existing telemetry to the assembler and derive route/fingerprint data at invocation time.

#### Rejected alternatives

- Backfill zeros: rejected as forged measurement.
- Derive trajectories later from prose logs: rejected because raw, exact execution identity may be unrecoverable.
- Enable concurrency based only on replay unit tests: rejected; cold continuation must cross a process boundary.

#### One bound falsifier

`test/runtime/test_nova1_nova2.py::EvidenceContinuationFalsifier.test_rich_trajectory_survives_cold_process_resume` performs a measured first turn, suspends, resumes in a spawned fresh interpreter from SQLite, finishes, and asserts continuous lineage, no repeated effect, exact cost sum, populated model fingerprint, $D_H/D_R/D_X$, and signed/null evidence semantics. Any all-zero invoked turn or dependence on the original process is red.

---

### ADR-0082 — Foundation-to-Meta-Framework Pareto, Compounding, and Promotion Protocol

**Status:** Proposed  
**Date:** 2026-08-21  
**Deciders:** Leadership 7  
**Requirements:** REQ-GEN-001…006, REQ-MEMO-001…006, REQ-PARETO-001…010, REQ-MACRO-001…012, REQ-PROM-001…014
**Program scope:** v0.6.1–v1.0.0

#### Context

A generality claim, witness reuse, macro-tool, skill-memory claim, model improvement, or self-improving harness is unsafe if selected by self-reported reward, incomplete cache identity, unpaired benchmarks, mutable baselines, or a scalar that hides security/cost regressions. The M-4 foundation must precede generality and adaptive learning.

#### Decision

1. M-4 is a nine-row gate on one real, uninterrupted, unstitched run.
2. M-5 uses Math & Formal Deductive Verification as Pack #2. It passes only with zero domain/kernel diffs and the same runtime mechanism.
3. Candidate versus baseline trials are preregistered and paired by $D_X$, protocol, seed policy, environment, and oracle. Baselines are undeletable.
4. Only exterior signed verdicts create preference labels. Declared-absent, inconclusive, instrument-error, legacy-incomplete, tampered, or incomparable trials cannot create a pair.
5. Promotion uses Pareto safety/economics gates plus an exact paired statistical test; no scalar score can compensate for an invariant regression.
6. Skill retrieval/eviction and model/harness mutation remain reversible candidate operations. Default-pointer changes require a signed promotion event by the promotion authority.
7. DPO training is exterior. The trained artifact is a new content-addressed model component subject to cassette regression, paired evaluation, and rollback.
8. Self-modification means propose → isolate → evaluate → compare → approve/promote; never modify the live trusted runtime in place.
9. The compounding ladder is ordered: T0 exact witness memoization; T1 verified macro compilation; T2 skill/router adaptation; T3 DPO/harness evolution. A higher tier may not be used to excuse a missing lower-tier identity or evidence control.
10. A memo key binds obligation, inputs, environment, witness checker, toolchain, assurance, protection, and policy version. Cache reuse never transfers a verdict to a different subject.
11. A macro-tool candidate is an ordinary untrusted artifact until replay, least-privilege, adversarial, held-out paired, and registry lifecycle gates pass. It executes through S0–S12 and cannot contain evaluator-private data or undeclared ambient authority.
12. Pareto profiles are versioned policy inputs. Predictions and settled costs are both retained. Profiles may rank only feasible choices and cannot auto-renew leases or auto-promote candidates.
13. M-5–M-10 proceed only in the dependency order in §6.

#### Preference certificate

```json
{
  "schema": "mhf.preference-pair/1",
  "pair_id": "sha256:…",
  "task_digest": "sha256:…",
  "prefix_context_digest": "sha256:…",
  "protocol_digest": "sha256:…",
  "environment_digest": "sha256:…",
  "chosen_execution_digest": "sha256:…",
  "rejected_execution_digest": "sha256:…",
  "chosen_verdict_event": "event-id",
  "rejected_verdict_event": "event-id",
  "comparison_basis": ["correctness", "safety", "cost"],
  "issuer": "promotion-service",
  "signature": "base64url…"
}
```

The certificate is JCS-signed. The issuer verifies both evaluator signatures and pair comparability but cannot rewrite either execution. Cross-harness comparison deliberately permits different $D_H$; it requires identical pairing cells through $D_X$’s task/protocol/environment inputs.

#### Consequences

Learning is slower than self-scoring but produces defensible evidence, reversible promotion, and a compounding corpus moat. Inconclusive results remain in denominators where the registered protocol requires them.

#### Rejected alternatives

- Unpaired leaderboard promotion: rejected due task-mix variance.
- Agent/critic preference without exterior evidence: rejected as forgeable.
- Weighted sum of safety, correctness, and cost: rejected because catastrophic regression can be averaged away.
- Live self-rewrite: rejected by ADR-0019 and the TCB boundary.

#### One bound falsifier

`test/runtime/test_meta_framework_promotion.py::MetaFrameworkPromotionFalsifier.test_only_bound_equivalent_paired_signed_pareto_safe_candidate_promotes` feeds valid and adversarial memo, macro, skill, model, and harness treatments. Only an exact memo cell may reuse; only a semantically equivalent least-privilege macro may enter comparison; and only the signed, comparable, safety-green treatment with exact McNemar significance may emit `PromotionApproved`. Changed memo bindings, tainted macro constants, widened ceilings, flipped signatures, absent verdicts, incomparable cells, multiplicity failure, or any safety regression must deny.

---

## 5. Theories, algorithms, and mathematical operating model

### 5.1 The six-dimensional economic tensor

The locked budget is not an ordinary vector space because its dimensions have different algebra:

\[
\mathbf R =
(r_{\$},r_{tok},r_{byte},r_{ms};r_{turn},r_{depth})
\in \mathbb N^4_{add}\times\mathbb N^2_{struct}.
\]

The first four dimensions are additive and conserved across leases. Turns are counted sequential decisions; depth is a maximum on a lineage path. Define the component-wise feasibility order:

\[
\mathbf R_a\preceq\mathbf R_b
\iff
\bigwedge_{j\in\{\$,tok,byte,ms,turn,depth\}}R_{a,j}\le R_{b,j}.
\]

This is a product partial order, not permission to add dollars to tokens or depth to time. Normalization may support dashboards, but admission and promotion preserve dimension identity.

For a parent lease $L_p$ partitioned among children $L_i$:

\[
\sum_i L_{i,j} + L_{remaining,j}=L_{p,j}
\quad\text{for }j\in\{\$,tok,byte,ms\},
\]

while $turn_i\le turn_p$ and $depth_i<depth_p$ are structural constraints. Actual use, including overruns, is committed; it is never clamped to make accounting look valid.

### 5.2 Variational Free Energy and Expected Free Energy

Let:

- $s$ be latent task/world state;
- $o$ be observations and signed evidence;
- $\tau=(o_{0:T},a_{0:T-1})$ be a trajectory;
- $\theta$ parameterize the frozen harness graph/policy;
- $q_\phi(s\mid\tau)$ be the agent’s approximate posterior;
- $p_\theta(\tau,s)$ be its generative model.

The variational free energy for belief fitting is:

\[
\mathcal F(\phi,\theta;\tau)
=\mathbb E_{q_\phi(s\mid\tau)}
\left[\log q_\phi(s\mid\tau)-\log p_\theta(\tau,s)\right]
\]

\[
=D_{KL}\!\left(q_\phi(s\mid\tau)\,\|\,p_\theta(s\mid\tau)\right)
-\log p_\theta(\tau).
\]

Minimizing $\mathcal F$ tightens an evidence bound for posterior inference. It does **not** by itself choose the next action. Candidate policies $\pi$ are selected using expected free energy under preferred outcomes $p_C(o)$:

\[
\mathcal G(\pi)=
\mathbb E_{q(o,s\mid\pi)}
\left[\log q(s\mid\pi)-\log p_C(o,s)\right].
\]

Under standard factorization, this can be read as pragmatic risk/ambiguity minus epistemic information gain. A practical AETHER selection problem is constrained, not a metaphysical scalar:

\[
\theta^*=\arg\min_{\theta\in\Theta}
\left(
\mathbb E[\mathcal G(\pi_\theta)]
+\sum_{j\in C}\lambda_j\mathbb E[c_j(\theta)]
\right)
\]

subject to

\[
\mathbb E[\mathbf c_{add}(\theta)]\preceq
(r_{\$},r_{tok},r_{byte},r_{ms}),\quad
T\le r_{turn},\quad d\le r_{depth},
\]

plus hard safety/evidence constraints. The multipliers $\lambda_j\ge0$ are declared policy parameters, not learned excuses to violate ceilings. Feasibility and safety are checked first; among feasible policies, AETHER should retain a Pareto frontier unless a preregistered product policy specifies a lexicographic choice.

Operationally:

1. **Perception:** minimize $\mathcal F$ by updating the task-state belief from observations.
2. **Planning:** estimate $\mathcal G$ for candidate graph policies/routes.
3. **Admission:** reject candidates outside $\mathbf R$, capability, safety, or evidence constraints.
4. **Action:** run the selected proposal through S0–S12.
5. **Learning:** update candidate priors only from evidence-complete trajectories; never modify authority from a posterior belief.

This formulation corrects a common category error in the internal research: VFE is inference, EFE is action selection, and neither legitimizes collapsing the six dimensions into a single unverifiable “fitness.”

### 5.3 Trajectory error credit and backward fault isolation

Each execution yields an attributed provenance graph

\[
G_\tau=(V,E_c\cup E_d\cup E_a),
\]

where vertices are component invocations, proposals, effects, receipts, artifacts, checkpoints, and verdict claims; $E_c$ is recorded causation, $E_d$ is data/artifact derivation, and $E_a$ is authority lineage. Correlation IDs alone are not causal edges.

For a failed terminal claim $z$, compute the reverse reachable set:

\[
B(z)=\{v\in V\mid v\leadsto z\text{ through }E_c\cup E_d\}.
\]

The structural pass is linear:

\[
O(|V|+|E_c|+|E_d|).
\]

Candidate suspicion—not causal guilt—is ranked by:

\[
S(v)=\mathbf 1[v\in B(z)]\,
\gamma^{\operatorname{dist}(v,z)}
\left(
\alpha q_v+\beta n_v+\chi u_v+\delta \rho_v
\right),
\]

where $q_v$ is severity contribution, $n_v$ is component/config novelty, $u_v$ is uncertainty or missing evidence, $\rho_v$ is attributable cost share, and $0<\gamma\le1$. These coefficients rank experiments only.

Bounded algorithm:

```text
input: signed terminal claim z, trajectory DAG Gτ, intervention budget B
1. verify D_H/D_R/D_X, signatures, hash chain, and event coverage
2. reverse-slice from z over causation and derivation edges
3. cut nodes that cannot influence the failed claim by interface/data type
4. group remaining nodes by named component + config digest
5. rank groups by S(v); mark missing evidence as uncertainty, never failure
6. for top B groups, create a paired replay cell:
     same task/protocol/environment/seed policy,
     replace or disable exactly one candidate component,
     run only in cassette/sandbox/exterior-evaluator conditions
7. estimate Δ_v = outcome(intervention) - outcome(control)
8. call v causal only after preregistered repeated interventions support Δ_v;
   otherwise emit "suspected" with the backward slice and uncertainty
```

If several components changed, use factorial/ablation or Shapley-style attribution within a bounded candidate set. A single failed trajectory supports provenance and fault localization, not Pearlian causal identification.

### 5.4 Dense 384-dimensional hybrid retrieval

The 384-dimensional embedding is an **M-9 implementation profile**, not a kernel contract. It is appropriate for a compact local encoder, but model identity/fingerprint and embedding version must be part of the derived index identity.

For query $q$ and skill card $i$, first apply hard symbolic filters: tenant/project protection class, invalidation state, required tools/interfaces, schema version, and capability compatibility. Then calculate:

\[
s_d(i)=\frac{e(q)^\top e(i)}{\|e(q)\|_2\|e(i)\|_2},
\quad e(\cdot)\in\mathbb R^{384},
\]

\[
s_l(i)=\operatorname{norm}_{[0,1]}(\operatorname{BM25}(q,i)),
\]

\[
s(i)=\alpha s_d(i)+\beta s_l(i)+\eta L_i+\zeta C_i-\kappa A_i,
\]

where $L_i$ is evidence-backed lift, $C_i$ confidence/reliability, and $A_i$ age/invalidation risk. Weights are versioned and sum to one only for the comparable normalized terms. Exact identifier/requirement matches receive a deterministic lexical boost; embeddings cannot override a protection or capability filter.

Retrieval returns refs and rationales. Raw skill text is inserted by the context compiler under a token budget. Index deletion never deletes the content-addressed evidence source.

### 5.5 Elo-decayed skill-card dynamics and eviction

For a skill card $i$ evaluated against a matched baseline with ratings $\mu_i,\mu_b$:

\[
p_i=\frac{1}{1+10^{(\mu_b-\mu_i)/400}},
\]

\[
\mu_i' = \mu_i + K(n_i)\,w_i\,(y_i-p_i),
\]

where $y_i\in\{0,\tfrac12,1\}$, $K(n)$ decreases with evidence count, and $w_i\in[0,1]$ is attributable contribution. Set $w_i=1$ only when the skill is the sole changed treatment; for multiple skills, use a preregistered ablation/Shapley estimate. Unsigned/self-scored outcomes have $w_i=0$.

Idle confidence decays toward a prior $\mu_0$, not toward negative infinity:

\[
\mu_i(t)=\mu_0+(\mu_i(t_0)-\mu_0)e^{-\lambda(t-t_0)}.
\]

Let the conservative utility be

\[
U_i=\operatorname{LCB}_{1-\alpha}(\Delta success_i)
-\lambda_c\Delta cost_i-\lambda_t\Delta latency_i-\lambda_r risk_i.
\]

Eviction is two-stage: `ACTIVE → COLD → ARCHIVED`. A card becomes cold only after minimum paired trials and $U_i<\tau_{cold}$ for $m$ consecutive windows or a valid invalidation condition fires. It becomes archived after a further retention window and no undeletable/legal hold. Archive removes it from default retrieval but preserves card, evidence, ratings, and digests. Reactivation is a new signed decision; no silent resurrection.

### 5.6 Unforgeable DPO harvesting

For prompt/prefix $x$, evidence-selected completion $y^+$, rejected completion $y^-$, policy $\pi_\theta$, reference policy $\pi_{ref}$, and temperature $\beta>0$, the DPO loss is:

\[
\mathcal L_{DPO}(\theta)=
-\mathbb E_{(x,y^+,y^-)\sim\mathcal D}
\log\sigma\left(
\beta\left[
\log\frac{\pi_\theta(y^+\mid x)}{\pi_{ref}(y^+\mid x)}
-\log\frac{\pi_\theta(y^-\mid x)}{\pi_{ref}(y^-\mid x)}
\right]
\right).
\]

A pair enters $\mathcal D$ only if:

- both runs are evidence-complete and reconstructible;
- the task, prefix through divergence, protocol, environment, oracle, and seed policy are comparable;
- both verdicts are exterior, signed, subject-bound, and non-inconclusive;
- chosen dominates rejected on the preregistered correctness/safety order, with cost tie-breaking only where allowed;
- no candidate saw oracle-private material or reference answers;
- a JCS-signed `mhf.preference-pair/1` certificate binds both execution digests and source verdict event IDs;
- training, evaluation, and promotion datasets are separated by immutable task digests.

DPO optimizes the policy against supplied preferences; it does not validate those preferences. If the certificate is forgeable, the learning loop is forgeable.

### 5.7 Exact paired McNemar promotion

For paired binary trials, let:

- $b$: candidate succeeds, baseline fails;
- $c$: baseline succeeds, candidate fails;
- concordant pairs are ignored by McNemar but remain reported;
- $n_d=b+c$: discordant count.

Under the null of equal marginal success, $B\sim\operatorname{Binomial}(n_d,1/2)$. The exact two-sided p-value is:

\[
p_{exact}=\min\left(
1,
2\sum_{k=0}^{\min(b,c)}{n_d\choose k}2^{-n_d}
\right).
\]

Promotion requires all of:

1. preregistered task set, primary endpoint, $\alpha$, minimum detectable effect, stopping rule, and multiplicity family;
2. $b>c$ and $p_{exact}\le\alpha_{adjusted}$;
3. a reported confidence interval/effect size, not p-value alone;
4. zero regression on hard security/trust invariants;
5. candidate lies on or improves the admissible Pareto frontier for the 6D economics;
6. instrument-error/inconclusive handling follows the preregistered denominator rule;
7. an undeletable baseline and replay bundle remain available.

There is no universal `N=50` guarantee. Power depends on discordance rate and target effect. Optional sequential testing requires an alpha-spending/e-value protocol selected before results are observed. The common chi-square approximation is not labeled “exact.”

### 5.8 Formal acceptance rule for compiled macro-tools

Let $g$ be an expanded effect subgraph and $m$ a candidate macro compiled from it. For held-out obligation cell $x$, let:

- $V(x,a)\in\{pass,fail,inconclusive,instrument\_error\}$ be the exterior verdict for implementation $a$;
- $Y(x,a)$ be the canonical observable output/artifact digest set;
- $E(x,a)$ be the security/evidence invariant vector;
- $\mathbf C(x,a)$ be settled 6D cost;
- $T(a)$ be the declared typed interface and witness contract.

The macro is semantically eligible only if:

\[
T(m)\preceq T(g),
\qquad C_{cap}(m)\subseteq C_{cap}(g),
\]

and, on every mandatory equivalence/replay cell,

\[
V(x,m)=V(x,g)=pass,
\quad Y(x,m)\equiv_{witness}Y(x,g),
\quad E(x,m)\succeq E_{required}.
\]

`equiv_witness` is pack-defined and exterior: byte equality where required, semantic proof/test equivalence where appropriate, or a preregistered human/panel contract for fuzzy outputs. The macro generator cannot choose the equivalence relation after seeing results.

Economic superiority is a separate statistical claim. Define paired deltas:

\[
\Delta\mathbf C_x=\mathbf C(x,m)-\mathbf C(x,g).
\]

The candidate must be nondominated under the preregistered economics and must pass the binary correctness promotion rule in §5.7. A lower median token count does not compensate for a new tail-latency, failure, capability, or evidence regression. Report median, quantiles, confidence intervals, and fallback rate for each additive dimension; do not publish an unqualified “cost collapse” percentage.

Macro fallback is explicit. If invocation fails before an external effect and the profile permits fallback, the expanded rule may run under a new reservation and both attempts remain in settled cost. After an effect is `undeterminable`, automatic fallback is forbidden until reconciliation proves it safe. This preserves exactly-once effect semantics even when tool compilation is imperfect.

The candidate’s provenance root binds:

\[
D_M=H(\operatorname{JCS}(
T(m), implementation, runner, C_{cap}(m), source\ pattern,
training\ trajectories, compiler, tests, checker, dependencies)).
\]

Any change to implementation, runner, interface, ceiling, dependency, compiler, or validation suite creates a new $D_M$ and restarts evaluation. A version label alone is never identity.

---

## 6. Milestone roadmap and version ladder

### 6.1 Version semantics

| Version | Meaning | Milestone gate |
|---|---|---|
| v0.6.1 | **Evidence & Correction Lock** | M-2 green: one runtime, NOVA-1, NOVA-2, current failures adjudicated. |
| v0.6.2 | **Extensibility Lock** | M-3 green: manifest/2 graph, canonical plugin FSM, NOVA-4, `layer0/` absent. |
| v0.6.3 | **Foundation Release Candidate** | M-4 evidence candidate produced; no scope expansion. |
| v0.7.0 | **Foundation MVP** | Director attests the same nine-row M-4 run; compatibility writers removed. |
| v0.8.0 | **General Substrate & Delegation** | M-5 Pack #2 + safe witness memo and M-6 mediated spawn green. |
| v0.9.0 | **Verified Adaptive Swarm Framework** | M-7 obligation/Pareto concurrency, M-8 builder/macro IR, M-9 scale/retrieval/macro laboratory/SPI review green. |
| v1.0.0 | **Promotion-Gated Tier S+ Meta-Framework** | M-10 Active-Inference routing, macro/skill/model/harness promotion, and rollback demonstration green with full evidence chain. |

v0.6.3 and v0.7.0 deliberately share the M-4 technical evidence: the former is the candidate artifact; the latter is the Director’s release promotion. No second “cleaner” run may be stitched from different row winners.

### 6.2 M-0 through M-10

| Milestone | Entry gate | Exact scope/deliverables | Exit gate | Explicitly out |
|---|---|---|---|---|
| **M-0 — Engineering Truth** | Director Wave-0 authorization | Canonical packages subject-of-record; CI/test truth; risk/identifier/SPI/plane decisions; architecture checks. | Named falsifiers execute against packages; evidence recorded. **Current: complete.** | Runtime features. |
| **M-1 — Fail-Closed Trust Spine** | M-0 green | Fix capability/budget/writer/identity gaps; canonical emitter; WAL cold replay primitives; sandbox ceiling; signed verdict binding. | Trust, kernel, contract, security gates green. **Current: complete.** | General graph, concurrency. |
| **M-2 — One Runtime & Evidence Integrity** | M-1 green | Finish package runtime convergence; NOVA-1 trajectory/2; NOVA-2 fresh-process cold continuation; resolve `_PROC_PATTERN`; classify current runtime/adapter reds; preserve one `Runtime.compose/execute_harness`. | Package runtime is sole authority; rich measured trajectory survives restart; no unadjudicated blocking red; ADR-0081 accepted. | Component-graph runtime, public spawn, concurrency. |
| **M-3 — Extensibility** | M-2 green; ADRs 0077–0079 accepted | Implement manifest/2 compiler/migration; six topology fixtures; canonical registry/FSM/broker; add lifecycle events/golden vectors; run NOVA-4; migrate code-default; delete all `layer0/`. | Unknown/unconsumed refs fail; ceiling applied; immutable $D_H$; full lifecycle on package path; no `layer0` import/file; walking skeleton through canonical runtime. | Real foundation claim, spawn implementation. |
| **M-4 — Foundation E2E STOP** | M-3 green; real provider/evaluator environment explicitly configured | One real coding-agent run across all nine rows below; capture one evidence bundle and v0.6.3 RC. | Director verifies every row from the same `run_id`, $D_H/D_R/D_X$, WAL chain, and artifacts; cut v0.7.0. | Pack #2, public spawn, concurrency, learning, doc collapse before evidence. |
| **M-5 — Generality & Consolidation** | M-4 Director attestation | Build Math & Formal Deductive Verification pack; prove zero domain/kernel diffs; run declared-absent compute profile and required-evaluator formal profile; implement T0 witness memo behind `IMemoryEngine`; collapse docs to Clean Triad; freeze evidence inventory. | Non-coding tasks pass exterior formal oracle through same loop; exact memo hit reuses only an identical valid witness cell; cache invalidation negatives green; I-7 supported; docs/link/stale gates green. | New kernel verb for math; approximate cache; swarm concurrency. |
| **M-6 — Mediated Delegation** | M-5 green; ADR-0080 accepted; TCB headroom plan | Implement `agent.spawn` through S0–S12; subleases, attenuation, isolation, cancellation, child lineage; graph profiles use it where needed. | Every spawn falsifier green; no direct planner spawn; TCB `<=1438`; no evaluator/secret reachability. | Parallel scheduler. |
| **M-7 — Controlled Concurrency & Pareto Frontier** | M-5/M-6 green; NOVA-2 green; selector independence sound | Durable obligation/claim projection; lease-bound pull scheduling; bounded (K) workers over (N) obligations; versioned Pareto profiles and quotes; deterministic conflict/admission policy; charged compute timing. | Sequential/concurrent semantic equivalence on independent cells; stale/double claims deny; conflict cases serialize/fail closed; crash recovery/no duplicate effect; predictions vs settled cost recorded; scaling claim measured. | Macro synthesis; framework mutation; auto-promotion. |
| **M-8 — Framework Builder & Macro IR** | M-6/M-7 green | User-facing builder compiles graph presets, witness contracts, profiles, and constraints to manifest/2; define portable `mhf.macro-tool/1` candidate IR; static diagnostics; experiment cell generation; immutable registry publication. | A user creates ReAct, debate, critic, tree, obligation-swarm, and macro-expanded variants without kernel/engine changes; invalid graphs/macros explain exact path. | Automatic synthesis promotion/default changes. |
| **M-9 — Scale, Retrieval & Macro Laboratory** | M-8 green with representative eligible corpus | 384d hybrid index profile; skill rating/cold/archive; mine and compile macro candidates; replay/property/adversarial macro suite; high-scale WAL/blob/index measurements; Pareto calibration; five-SPI evidence review; protocol conformance. | Registered throughput/latency/recovery targets met; no evidence loss; retrieval lift demonstrated in paired tests; at least one macro candidate is semantically equivalent and least-privilege on held-out cells; no default pointer changed; SPI decision recorded append-only. | Live self-improvement or automatic macro promotion. |
| **M-10 — Meta-Cognitive Tier S+ Substrate** | M-8/M-9 green; ADR-0082 accepted; corpus eligibility threshold met | Exterior VFE/EFE policy selector; trajectory graph harvester; T1 macro promotion; T2 skill/router promotion; unforgeable pairs; DPO/DMPO candidate training; paired exact promotion; evolutionary manifest mutations; rollback. | System proposes, isolates, verifies, statistically promotes, and can roll back a superior macro/skill/model/harness candidate while $D_H/D_R/D_X/D_O/D_M$, signatures, raw Pareto vectors, and baseline remain reconstructible. | In-place TCB rewrite, self-issued truth, autonomous release pointer. |

### 6.3 M-4 nine-row single-run evidence table

The run is green only if all rows bind the same run/episode lineage. “Equivalent demo,” cassette substitution, manually copied verdict, or separately successful runs do not count.

| # | Required observation | Uncheated evidence |
|---:|---|---|
| 1 | Real model invocation | Provider/model/fingerprint and measured usage from a non-fake, non-cassette invocation. |
| 2 | Authorized effect | Descriptor-bound grant, S5 decision, S7 lease, S8 verification, and matching effect request. |
| 3 | Real filesystem change | Before/after artifact digests and patch receipt inside the run workspace. |
| 4 | Rootless sandbox | Recorded mount/network/syscall/UID probes; evaluator path absent; no fallback-to-host success. |
| 5 | Exterior signed evaluation | UID/image/oracle/subject/protocol binding and verifiable signature; agent cannot mint it. |
| 6 | SQLite WAL record | Full event range with project hash-chain continuity and durable S8a intent. |
| 7 | Cold replay | A fresh runtime reduces the persisted chain to the same terminal state/digest. |
| 8 | Rich trajectory | `/2` row with populated turns, non-hollow cost, model fingerprint, $D_H/D_R/D_X$, receipts, outcome, evidence. |
| 9 | One runtime authority | Trace/call/import evidence shows `Runtime.compose → execute_harness → HarnessSession`; no driver/Layer-0 alternate path. |

### 6.4 Pack #2 — Math & Formal Deductive Verification

**Purpose:** falsify the coding-substrate hypothesis with a domain whose artifacts, verbs, context, and oracle are not source-code editing.

Proposed path: `packs/math-formal/`.

Composition:

- a problem-source component providing immutable theorem/problem statements by digest;
- a proof-state context component rendering assumptions, goals, prior lemmas, and bounded history;
- a search planner that may use single, critic, or tree topology without engine changes;
- pure/sandboxed computation toolkits for rational arithmetic, finite enumeration, and candidate proof construction;
- a submit component that writes proof certificates to a scratch artifact namespace;
- an exterior formal evaluator in a pinned, networkless image (for example a pinned Lean 4 checker and/or independently verified proof-certificate checker), distinct from the worker sandbox;
- an optional `evidence.mode=absent` compute-only exploratory profile to test the guardrail model, never used for the generality pass.

Task strata:

1. exact rational/algebraic identity with independently checkable normal form;
2. finite combinatorial construction with exhaustive certificate checker;
3. theorem proof accepted by the pinned formal kernel;
4. inconsistent/underspecified premise where correct abstention is verified;
5. adversarial candidate containing a proof comment/string but no valid proof term.

Required capability scope: read-only problem corpus; write-only/read-back scratch proof artifacts; explicitly allowlisted compute executable; no network; no access to evaluator bundle, expected proof, signing key, or host home. `proc.exec` remains a generic mediated verb—the kernel never learns “theorem,” “Lean,” or “proof.”

The M-5 gate fails if Pack #2 requires any modification in `domain/` or `kernel/`, a math branch in agency/runtime, direct checker access by the agent, an unsigned result, or a manually interpreted answer. Adapter/pack additions are expected; a genuinely missing general port triggers a separate SPI/port review rather than a domain shortcut.

---

## 7. Zero-guesswork developer implementation bridge

### 7.1 Ordered file-level change map after authorization

This is a target map, not permission to edit now.

| Milestone | Primary targets | Required companion changes |
|---|---|---|
| M-2/NOVA-1 | `runtime/trajectory.py`, `runtime/session.py`, model invocation telemetry, `schemas/mhf/trajectory.schema.json` or new `/2` file | Generated types/vectors, reducers, runtime/trust tests, legacy-reader status. |
| M-2/NOVA-2 | runtime recovery/session root, SQLite store port/adapter only if needed | Fresh-process fixture, reconciliation tests, no checkpoint authority. |
| M-3 graph | new domain manifest/graph values, `agency/manifests/loader.py`, `runtime/compose.py`, schema/codegen | Compatibility reader, five fixtures, JCS vectors, pack migration. |
| M-3 registry | `runtime/registry/`, canonical wiring/broker; delete Layer-0 only at gate | Event schema, generated enum, reducer, writer ownership, lifecycle/NOVA-4 tests. |
| M-4 | dogfood/CLI invocation and evidence exporter if restored | One signed evidence manifest; no special E2E runtime. |
| M-5 | `packs/math-formal/`, adapter/environment/evaluator implementations | Pack tests, oracle pin/signing, zero-domain/kernel-diff gate, docs collapse. |
| M-6 | existing effect schema/registry, agency spawn adapter, kernel only if unavoidable | S0–S12 stage tests, TCB check, security/trust suite. |
| M-5 memo | runtime memory service behind existing `IMemoryEngine`; pack witness-key policy | Canonical memo key vectors, expiry/revocation/protection negatives, original witness refs retained. |
| M-7 | runtime obligation/claim projection, scheduler/profile components, lab calibration | CAS/lease/recovery tests, raw quote-vs-settlement telemetry, no alternate store/writer/evaluator. |
| M-8/M-9 macro | `schemas/mhf/macro_tool.schema.json`, exterior compiler/lab plugin, registry candidate artifacts | Workflow-IR vectors, taint/capability inference, replay/property/adversarial tests, held-out paired cells. |
| M-9/M-10 learning | index/retrieval, graph harvester, lab/training/promotion services | Registered measurement protocols, signed pair certificates, immutable baselines, rollback. |

### 7.2 Manifest compiler pseudocode

```python
def compose_manifest_v2(raw, registry, authority, episode_id):
    parsed = parse_json_without_duplicate_keys(raw)
    validate_draft_2020_12(parsed)

    resolved = {}
    for node_id, node in sorted(parsed.components.items()):
        artifact = registry.resolve(node.ref)          # unknown -> fail
        verify_expected_digest(node, artifact)         # mismatch -> fail
        verify_interfaces(node, artifact)              # mismatch -> fail
        verify_isolation(node.execution, artifact)     # missing grant/protocol -> fail
        resolved[node_id] = artifact

    validate_endpoints_and_cardinality(parsed, resolved)
    reject_unconsumed_authority_nodes(parsed, resolved)

    effective = {}
    for node_id, node in parsed.components.items():
        requested = selectors_for(node.capability_requests, parsed.capabilities)
        effective[node_id] = intersect_all(
            authority.principal_ceiling,
            selectors_for_all(parsed.capabilities),
            resolved[node_id].declared_ceiling,
            requested,
        )
        # empty is a real deny-all ceiling; never replaced with a default

    frozen_doc = materialize_resolved_graph(parsed, resolved, effective)
    digest = sha256(jcs(frozen_doc))
    return FrozenHarnessV2(document=deep_freeze(frozen_doc), digest=digest)
```

All errors include a JSON Pointer/node/interface path and occur before activation. The compiler never catches an error and substitutes a generous default.

### 7.3 Universal loop pseudocode

```python
while state.is_runnable and budget.turns_remaining:
    observation = reduce_authoritative_state(store, episode_id)
    context = context_component.compile(observation, immutable_refs)
    proposal, model_usage = planner.propose(context)
    ledger.proposal_produced(redact_and_digest(proposal), model_usage.identity)

    if proposal.terminal:
        terminate_as_run_state(proposal.terminal)
        break
    if proposal.has_effect:
        receipt = kernel.dispatch(to_effect_request(proposal))
        observation = receipt_as_untrusted_observation(receipt)
    telemetry.commit_turn(model_usage, receipt)

trajectory = assemble_from_exact_events_telemetry_and_refs()
evaluate_exterior_if_required()
emit_terminal_only_after_trajectory_and_evidence_are_bound()
```

Multiple planners, critics, or workers are components around `planner.propose`; they do not get a privileged effect channel.

### 7.4 State-plane swarm protocol

Use immutable content-addressed work/artifacts plus authoritative claim events:

```text
WorkPublished(work_digest, required_interface, budget_offer, parent_lineage)
WorkClaimed(work_digest, child_principal, lease_id, expected_version)
ArtifactPublished(work_digest, artifact_digest, provenance_root)
WorkReturned(work_digest, child_principal, terminal_state, artifact_refs)
WorkReleased(work_digest, reason)
```

These event names are design placeholders until an ADR/schema assigns emitters; they must not be added ad hoc. Claim is compare-and-swap on the reduced work version. A worker that loses the claim cannot commit a privileged effect under that lease. Large artifacts live in BlobStore; IndexPort is a rebuildable projection. At-least-once delivery is acceptable only with effect intent/idempotency/reconciliation semantics; it must not become at-least-once external effects.

The projection must expose `open`, `claimed`, `blocked`, `witness_pending`, `discharged`, `failed`, and `indeterminate` without inventing new authority. `discharged` means an accepted exterior witness is bound to the obligation subject; worker completion alone is `witness_pending`. Decomposition has an explicit maximum depth, child-count price, and progress predicate so obligation explosion stops at admission rather than exhausting the queue.

### 7.5 Pareto controller and macro compiler implementation contract

The Pareto controller is deterministic given frozen quotes, beliefs, profile, and tie-break seed:

```python
def select_refinement(obligation, quotes, belief, profile, remaining):
    feasible = [
        q for q in quotes
        if capability_compatible(q, obligation)
        and evidence_floor(q) >= obligation.evidence_floor
        and predicted_cost(q).precedes_or_equals(remaining)
        and safety_constraints_hold(q)
        and dependencies_ready(q)
    ]
    if not feasible:
        return typed_no_feasible_policy(obligation)

    predicted = [estimate_vfe_efe(q, belief, profile) for q in feasible]
    frontier = nondominated(predicted, preserve_raw_vectors=True)
    choice = profile.lexicographic_select(frontier)
    ledger.record_quote_set_and_choice(obligation.digest, predicted, choice)
    return request_new_reservation(choice)  # kernel still decides
```

`nondominated` never receives an infeasible quote. The profile and calibration model identities enter $D_R$; a frozen profile promoted into the harness enters $D_H$. Settled cost is joined to the quote after completion so calibration cannot be silently rewritten.

Proposed Draft 2020-12 contract for a macro candidate:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://aether.local/schemas/mhf/macro-tool-1.schema.json",
  "title": "mhf.macro-tool/1",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema", "id", "interfaces", "implementation", "capability_ceiling",
    "source", "validation"
  ],
  "properties": {
    "schema": {"const": "mhf.macro-tool/1"},
    "id": {"type": "string", "pattern": "^[a-z][a-z0-9_.-]{0,127}$"},
    "interfaces": {
      "type": "object",
      "additionalProperties": false,
      "required": ["input", "output", "witness"],
      "properties": {
        "input": {"type": "string", "format": "uri-reference"},
        "output": {"type": "string", "format": "uri-reference"},
        "witness": {"type": "string", "format": "uri-reference"}
      }
    },
    "implementation": {
      "type": "object",
      "additionalProperties": false,
      "required": ["artifact_ref", "digest", "media_type", "runner_ref"],
      "properties": {
        "artifact_ref": {"type": "string", "minLength": 1},
        "digest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
        "media_type": {"type": "string", "minLength": 1},
        "runner_ref": {"type": "string", "minLength": 1},
        "entrypoint": {"type": "string", "minLength": 1}
      }
    },
    "capability_ceiling": {
      "type": "array",
      "items": {"type": "string", "minLength": 1},
      "uniqueItems": true
    },
    "source": {
      "type": "object",
      "additionalProperties": false,
      "required": ["pattern_digest", "compiler_digest", "trajectory_digests"],
      "properties": {
        "pattern_digest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
        "compiler_digest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
        "trajectory_digests": {
          "type": "array", "minItems": 1, "uniqueItems": true,
          "items": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"}
        }
      }
    },
    "validation": {
      "type": "object",
      "additionalProperties": false,
      "required": ["protocol_digest", "checker_digest", "held_out_set_digest"],
      "properties": {
        "protocol_digest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
        "checker_digest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
        "held_out_set_digest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"}
      }
    }
  }
}
```

The candidate compiler is outside the TCB:

```python
def compile_macro(eligible_trajectories, registry, lab_protocol):
    rows = verify_eligibility_and_signatures(eligible_trajectories)
    graphs = [project_effect_subgraph(row) for row in rows]
    patterns = mine_frequent_connected_subgraphs(graphs)

    for pattern in patterns:
        params = anti_unify_without_tainted_constants(pattern)
        ceiling = least_representable_selector_hull(pattern.receipts)
        if ceiling is None or ceiling.is_wildcard:
            reject(pattern, "capability_not_narrowly_expressible")
            continue

        for candidate in synthesize_portable_candidates(pattern, params, ceiling):
            freeze_candidate_digest(candidate)
            run_positive_replays(candidate, lab_protocol)
            run_property_and_adversarial_negatives(candidate, lab_protocol)
            run_held_out_paired_cells(candidate, expanded=pattern)
            publish_as_untrusted_candidate(candidate)  # never default
```

After validation, the macro is packaged as an ordinary plugin manifest and enters the canonical plugin FSM. Compiler success does not skip discovery, verification, resolution, activation, sandbox, evaluation, or promotion. The compiler has no registry-default or verdict writer capability.

### 7.6 Requirement-to-falsifier matrix

Every row is one requirement and one executable test. Existing tests are marked **existing**; all others are exact proposed targets.

| Requirement | Exact executable falsifier | Gate |
|---|---|---|
| REQ-AUTH-001 unknown action opens no lease | `test.kernel.test_dispatch.OrderingRules.test_unknown_action_never_opens_a_lease` **existing** | all |
| REQ-AUTH-002 intent durable before effect | `test.trust.test_spine.Atomicity.test_intent_is_durable_before_the_effect_begins` **existing** | all |
| REQ-AUTH-003 denied effect never reaches adapter | `test.trust.test_spine.Denial.test_a_denied_effect_never_reaches_its_adapter` **existing** | all |
| REQ-AUTH-004 child attenuation never widens | `test.agency.test_episode_spawn.TestEpisodeEngineSpawn.test_spawn_widening_denied_returns_typed_result` **existing** | M-6 |
| REQ-MAN2-001 six topologies are data | `test.contracts.test_manifest_v2_graph.ManifestV2GraphFalsifier.test_six_topologies_compile_without_kernel_or_engine_change` | M-3/M-7 |
| REQ-MAN2-002 unknown ref fails at compose | `test.runtime.test_manifest_v2_negatives.ManifestV2NegativeTests.test_unknown_ref_fails_before_activation` | M-3/NOVA-4 |
| REQ-MAN2-003 unknown interface fails | `test.runtime.test_manifest_v2_negatives.ManifestV2NegativeTests.test_unregistered_interface_names_json_pointer` | M-3 |
| REQ-MAN2-004 unconsumed authority node fails | `test.runtime.test_manifest_v2_negatives.ManifestV2NegativeTests.test_unconsumed_authority_component_fails` | M-3 |
| REQ-MAN2-005 identical resolved graph has identical $D_H$ | `test.contracts.test_manifest_v2_digest.ManifestV2DigestTests.test_order_and_yaml_json_do_not_change_digest` | M-3 |
| REQ-MAN2-006 meaningful config/edge change changes $D_H$ | `test.contracts.test_manifest_v2_digest.ManifestV2DigestTests.test_authority_config_or_edge_changes_digest` | M-3 |
| REQ-MAN2-007 frozen graph immutable | `test.runtime.test_manifest_v2_negatives.ManifestV2NegativeTests.test_frozen_composition_rejects_nested_mutation` | M-3/NOVA-4 |
| REQ-MAN2-008 old manifests migrate deterministically | `test.contracts.test_manifest_migration.ManifestMigrationTests.test_v1_and_v4_migrate_to_one_v2_digest` | M-3 |
| REQ-EVID-001 declared absence is explicit | `test.trust.test_evidence_guardrail_states.EvidenceGuardrailFalsifier.test_absent_has_reason_and_no_verdict` | M-3/M-5 |
| REQ-EVID-002 absence cannot promote | `test.runtime.test_promotion_negatives.PromotionNegativeTests.test_declared_absent_never_enters_pair_or_promotion` | M-10 |
| REQ-EVID-003 unsigned/wrong-bound is forged | `test.packs.test_oracles.OracleSuiteTests.test_unsigned_verdicts_cannot_pass_the_gate` **existing** | all |
| REQ-EVID-004 evaluator remains unreachable | `test.security.test_evaluator_security.EvaluatorSecurityBoundary.test_runtime_cannot_import_evaluator_implementation` **existing** | all |
| REQ-PLUG-001 every lifecycle entry ledgered | `test.runtime.registry.test_lifecycle_events.PluginLifecycleTests.test_every_legal_transition_emits_owned_event` | M-3 |
| REQ-PLUG-002 illegal transitions deny | `test.runtime.registry.test_lifecycle_events.PluginLifecycleTests.test_illegal_transition_changes_neither_state_nor_ledger` | M-3 |
| REQ-PLUG-003 empty ceiling denies | `test.adapters.test_sandbox_ceiling.PluginCeilingTests.test_empty_capabilities_deny_execute` **existing; reroute canonical fixture** | M-3/NOVA-4 |
| REQ-PLUG-004 only registry writes `Plugin*` | `test.contracts.test_event_coverage.EventCoverageTests.test_plugin_kinds_have_only_registry_owner` | M-3/NOVA-4 |
| REQ-PLUG-005 faulted cell not active | `test.runtime.registry.test_nova4_retirement.Nova4Tests.test_broker_failure_atomically_faults_and_revokes_admission` | M-3/NOVA-4 |
| REQ-PLUG-006 in-process requires grant | `test.packs.test_gates.IsolationPolicyGateTests.test_in_process_proc_exec_fails` **existing; extend v2** | M-3/NOVA-4 |
| REQ-PLUG-007 no Layer-0 remains | `test.packs.test_gates.DomainBlindnessGateTests.test_layer0_is_clean` **existing; change to absence/import assertion** | M-3 |
| REQ-TRAJ-001 invoked turns non-hollow | `test.runtime.test_trajectory_v2.TrajectoryV2Tests.test_each_model_turn_has_positive_measured_dimension` | M-2/NOVA-1 |
| REQ-TRAJ-002 total equals turns plus overhead | `test.runtime.test_trajectory_v2.TrajectoryV2Tests.test_episode_cost_reconciles_exactly` | M-2/NOVA-1 |
| REQ-TRAJ-003 model identity/fingerprint explicit | `test.runtime.test_trajectory_v2.TrajectoryV2Tests.test_route_and_fingerprint_measured_or_reasoned_unavailable` | M-2/NOVA-1 |
| REQ-TRAJ-004 verdict exact or permitted null | `test.runtime.test_trajectory_v2.TrajectoryV2Tests.test_verdict_is_ledger_object_or_reasoned_null` | M-2/NOVA-1 |
| REQ-TRAJ-005 all three digests distinct/bound | `test.runtime.test_trajectory_v2.TrajectoryV2Tests.test_harness_execution_experiment_digests_have_correct_inputs` | M-2/NOVA-1 |
| REQ-RESUME-001 fresh-process continuation | `test.runtime.test_nova1_nova2.EvidenceContinuationFalsifier.test_rich_trajectory_survives_cold_process_resume` | M-2/NOVA-2 |
| REQ-RESUME-002 no repeated resolved effect | `test.runtime.test_cold_resume.ColdResumeTests.test_completed_effect_is_not_dispatched_twice` | M-2/NOVA-2 |
| REQ-RESUME-003 unresolved intent stays unknown | `test.trust.test_spine.Atomicity.test_an_adapter_that_raises_leaves_occurrence_undeterminable` **existing; add process crash** | M-2/NOVA-2 |
| REQ-SPAWN-001 spawn enters S0–S12 | `test.trust.test_mediated_spawn.MediatedSpawnFalsifier.test_spawn_traverses_every_dispatch_invariant_and_never_widens` | M-6 |
| REQ-SPAWN-002 child return untrusted | `test.agency.test_episode_spawn.TestEpisodeEngineSpawn.test_spawn_return_enters_as_untrusted_derived_at_minimum` **existing** | M-6 |
| REQ-SPAWN-003 child workspace always destroyed | `test.agency.test_episode_spawn.TestEpisodeEngineSpawn.test_workspace_destroyed_in_finally_including_on_failure` **existing** | M-6 |
| REQ-CONC-001 independent results equivalent | `test.runtime.test_controlled_concurrency.ConcurrencyTests.test_independent_cells_match_sequential_reduction` | M-7 |
| REQ-CONC-002 unknown footprint conflicts | `test.runtime.test_controlled_concurrency.ConcurrencyTests.test_unknown_selector_serializes_or_denies` | M-7 |
| REQ-CONC-003 crash does not duplicate effect | `test.runtime.test_controlled_concurrency.ConcurrencyTests.test_worker_crash_reclaims_claim_without_repeating_effect` | M-7 |
| REQ-OBL-001 claim is exclusive and lease-bound | `test.runtime.test_obligation_frontier.ObligationFrontierTests.test_stale_or_second_claim_cannot_commit` | M-7 |
| REQ-OBL-002 completion is not discharge | `test.runtime.test_obligation_frontier.ObligationFrontierTests.test_worker_return_waits_for_bound_exterior_witness` | M-7 |
| REQ-OBL-003 decomposition cannot explode | `test.runtime.test_obligation_admission.ObligationAdmissionTests.test_depth_child_count_and_no_progress_decomposition_deny` | M-7 |
| REQ-PARETO-001 infeasible quote never scores | `test.runtime.test_pareto_controller.ParetoControllerTests.test_safety_capability_and_budget_gate_precedes_ranking` | M-7 |
| REQ-PARETO-002 raw vectors survive scalar ranking | `test.runtime.test_pareto_controller.ParetoControllerTests.test_profile_choice_records_full_frontier_and_raw_cost_vectors` | M-7 |
| REQ-PARETO-003 quote reconciles to settlement | `test.runtime.test_pareto_calibration.ParetoCalibrationTests.test_prediction_and_settled_cost_are_immutable_joined_records` | M-7/M-9 |
| REQ-PARETO-004 escalation requires new lease | `test.trust.test_pareto_escalation.ParetoEscalationTests.test_efe_or_roi_cannot_renew_or_widen_reservation` | M-7 |
| REQ-GEN-001 Pack #2 needs no domain/kernel diff | `test.packs.math_formal.test_generality.MathGeneralityFalsifier.test_pack_runs_with_domain_and_kernel_tree_hash_unchanged` | M-5 |
| REQ-GEN-002 proof comment cannot pass | `test.packs.math_formal.test_oracle.MathOracleTests.test_comment_or_string_without_proof_term_fails` | M-5 |
| REQ-GEN-003 valid formal proof is exterior-signed | `test.packs.math_formal.test_oracle.MathOracleTests.test_valid_certificate_returns_bound_signed_verdict` | M-5 |
| REQ-MEMO-001 exact cell reuses original witness | `test.runtime.test_witness_memo.WitnessMemoTests.test_identical_bound_cell_returns_original_signed_witness_ref` | M-5 |
| REQ-MEMO-002 changed binding misses or invalidates | `test.runtime.test_witness_memo.WitnessMemoTests.test_input_checker_environment_revocation_or_policy_change_cannot_hit` | M-5 |
| REQ-RETR-001 protection filter precedes similarity | `test.runtime.test_hybrid_skill_index.HybridIndexTests.test_high_similarity_wrong_protection_class_is_never_returned` | M-9 |
| REQ-RETR-002 eviction archives evidence | `test.runtime.test_skill_eviction.SkillEvictionTests.test_cold_archive_preserves_card_ratings_and_trajectory_refs` | M-9 |
| REQ-MACRO-001 schema and digest close all authority inputs | `test.contracts.test_macro_tool_contract.MacroToolContractTests.test_unknown_field_or_changed_runner_ceiling_dependency_changes_or_rejects_digest` | M-8 |
| REQ-MACRO-002 synthesis captures no tainted constant | `test.lab.test_macro_compiler_negatives.MacroCompilerNegativeTests.test_secret_path_tenant_answer_and_oracle_private_values_never_compile` | M-9 |
| REQ-MACRO-003 ceiling is least privilege | `test.lab.test_macro_capabilities.MacroCapabilityTests.test_candidate_ceiling_covers_required_receipts_without_wildcard_or_widening` | M-9 |
| REQ-MACRO-004 held-out semantic equivalence | `test.lab.test_macro_equivalence.MacroEquivalenceFalsifier.test_macro_and_expanded_graph_match_exterior_witness_on_held_out_cells` | M-9 |
| REQ-MACRO-005 uncertain effect forbids fallback | `test.trust.test_macro_fallback.MacroFallbackTests.test_undeterminable_effect_requires_reconciliation_before_expanded_fallback` | M-9 |
| REQ-MACRO-006 compiler cannot publish default | `test.security.test_macro_compiler_authority.MacroCompilerAuthorityTests.test_compiler_can_publish_candidate_but_cannot_write_verdict_or_default_pointer` | M-9/M-10 |
| REQ-MACRO-007 promoted macro is Pareto-safe | `test.runtime.test_macro_promotion.MacroPromotionTests.test_only_equivalent_least_privilege_paired_significant_candidate_promotes` | M-10 |
| REQ-PROM-001 only valid signed pairs harvested | `test.runtime.test_preference_harvest.PreferenceHarvestTests.test_invalid_incomparable_or_self_scored_pairs_rejected` | M-10 |
| REQ-PROM-002 exact McNemar implementation | `test.runtime.test_promotion_statistics.PromotionStatisticsTests.test_exact_p_matches_enumerated_binomial_cases` | M-10 |
| REQ-PROM-003 safety regression cannot average out | `test.runtime.test_promotion_protocol.PromotionProtocolFalsifier.test_only_paired_signed_pareto_safe_exactly_significant_candidate_promotes` | M-10 |
| REQ-PROM-004 rollback preserves baseline | `test.runtime.test_promotion_rollback.PromotionRollbackTests.test_default_pointer_rolls_back_without_deleting_candidate_or_baseline` | M-10 |

### 7.7 Negative constraints and anti-pattern checklist

The implementation is rejected if any answer is “yes”:

- Does `kernel/` exceed 1438 logical LOC, import a domain verb, planner, model, evaluator, plugin registry, task type, or learning policy?
- Does any lower layer import a higher layer, or do adapters import kernel/agency?
- Is there a second runtime, event store, envelope constructor, writer authority, manifest compiler, evaluator gate, or episode driver?
- Can a plugin/pack write `Plugin*`, capability, budget, effect, verdict, or approval events outside its assigned role facade?
- Does an empty/missing capability ceiling become allow-all, or is a selector intersection computed then discarded?
- Can `in_process` execution occur without an explicit frozen grant?
- Can the model/worker read evaluator code, oracle-private fixtures, signing keys, host home/env files, sockets, or unrestricted network?
- Is Bubblewrap presence treated as proof without policy probes, or is setuid Bubblewrap accepted?
- Is a denied/unknown action able to reserve a lease or reach an adapter?
- Is a started effect non-durable, repeated after recovery, or forced into success/failure when occurrence is unknown?
- Are wall-clock milliseconds summed across concurrent workers as if conserved compute, or are overruns clamped?
- Are unknown token/price/fingerprint values written as zero/empty success?
- Can declared-absent evidence become pass, preference data, memory license, or promotion?
- Does a critic/agent/evaluator inside the worker mint the authoritative verdict?
- Can graph config mutate after $D_H$, or can a semver ref resolve differently without changing $D_H$?
- Is a runtime workflow DAG introduced beside the universal loop?
- Does a swarm use unrestricted full-mesh chat, shared mutable memory, or unowned state writes?
- Can an obligation be marked discharged by worker return rather than a subject-bound witness, or can a stale claim commit?
- Can decomposition create unbounded children/depth or consume budget without a declared progress predicate?
- Does the Pareto controller score a capability-, safety-, evidence-, or budget-infeasible quote?
- Does a profile discard the original 6D vector, hide tail cost/fallback, or implicitly renew a lease from predicted ROI/EFE?
- Can a witness memo hit after its input, environment, checker, toolchain, protection, revocation epoch, assurance, or policy binding changes?
- Is a “macro-tool” merely prose, an untyped script, ambient shell authority, or a captured task/secret/oracle-private constant?
- Can a compiled macro bypass S0–S12, ordinary plugin lifecycle, sandbox, exterior witness, held-out comparison, or human promotion?
- Does macro fallback repeat an effect whose occurrence is unknown, or omit the failed attempt from settled cost?
- Is a token/cost-collapse percentage claimed without a paired held-out protocol, uncertainty, tails, and failure/fallback accounting?
- Does a causal label come from temporal adjacency without a recorded dependency and paired intervention?
- Does DPO consume unpaired, unsigned, incomparable, contaminated, or train/eval-overlapping examples?
- Does a scalar fitness allow safety/trust regression to be offset by task success or lower cost?
- Does a documentation update erase historical evidence or rewrite an accepted ADR?

---

## 8. Repository hygiene and document update cascade

These edits occur only after the relevant ADR is accepted; the cleanup/collapse itself is scheduled after M-4. This report makes none of them.

### 8.1 Stale artifacts and research evidence

1. **`DELETE.md`:** it is a tracked zero-byte root artifact. At M-5, remove it with an ordinary reviewed deletion. No replacement is required.
2. **Duplicate synthesis:** keep `docs/06_references/RESEARCH_THEORETICAL_SYNTHESIS.md` as the canonical historical reference; delete `_B` only after adding its path and identical SHA-256 to a migration ledger/commit message and fixing incoming links. Do not pretend two independent sources supported the claim.
3. **Superseded HY3 proposal:** retain `proposal_hy3_improved.md`; archive or remove the earlier `proposal_hy3_harness.md` only with a supersession record because its pre-approval premise is stale.
4. **Conflicting aspirational research:** retain `RESEARCH_Harness_Builder_Framework.md` and `vanguard_body_detailed.md` as research evidence, but add prominent advisory/superseded banners in the M-5 cascade. Their central orchestrator/workflow bus, infrastructure stack, cosmological hierarchy, and metaphysical language are not active architecture and conflict with ADR-0003/0069/ADR-M0-10.
5. **Model suggestions:** label provider/model lists as dated observations. Never copy current price/availability into law; resolve routes through measured adapter configuration.
6. **Completed reviews:** archive by status and backlink from the decision they influenced. Do not delete forensic findings.

### 8.2 `docs/SPEC.md` diff directive

Only after ADR acceptance:

- **Header/status:** advance the concept version to v0.6.1 correction lock; link ADRs 0077–0082. Do not mark future milestones implemented.
- **§1 boundary/planes:** add a short normative statement that swarm coordination uses State Plane refs/events and never gains authority from state. Define the obligation frontier as a projection, not a new store. Preserve the one writer per privileged kind table; add `PluginDiscovered` and `PluginVerified` owned by registry.
- **§2 composition:** replace fixed-slot/v4 manifest wording with `mhf.manifest/2`, Named Component Graph, semantic compiler passes, freeze point, compatibility-reader sunset, $D_H$ definition, and the six topology fixtures including `obligation-pareto`.
- **§3 authority:** add the future `agent.spawn` descriptor/attenuation requirements with `DEFERRED UNTIL M-6`; do not list it as live.
- **§5 harness/pack:** formalize Separability Thesis as a bound claim and cite Pack #2 as its falsifier, not proof already obtained. Define witness contracts and declared-assurance classes as pack data.
- **§7 trajectory:** norm `/2` non-hollow turns, model fingerprint status, predicted quote plus settled-cost reconciliation, evidence state, $D_H/D_R/D_X/D_O$ and optional $D_M$, legacy exclusion, and cold-continuation requirement.
- **§8 evaluator/guardrail:** define required/declared-absent/forged and promotion consequences.
- **§9 learning:** add the T0–T3 compounding ladder, exact memo-key invalidation, `mhf.macro-tool/1`, signed preference certificate, paired comparison, exact promotion, Pareto safety gate, and no in-place self-modification as deferred law. Make explicit that macro/skill/model/harness candidates cannot change the default pointer without human promotion authority.
- **Falsifier annex:** add the exact test IDs from §7.5 one-to-one. Remove no prior active falsifier unless an ADR explicitly supersedes it.

### 8.3 `docs/03_sprints/sprint_active.md` diff directive

- Replace ambiguous status prose with one table whose columns are ID, milestone, owner, dependency, authorized?, implementation state, exact test, evidence link.
- Put NOVA-1 and NOVA-2 in M-2 as Director-disposition rows; remove any contradictory “Wave 4” timing for trajectory content. NOVA-5 at M-4 is confirmation of `/2` on the real run, not the first implementation.
- List current adapter/runtime reds with named cause owner and closure/quarantine criteria; do not claim a green full suite.
- Keep graph/registry/NOVA-4 in M-3, with ADR acceptance as entry dependencies.
- Keep Pack #2/memo, public spawn, obligation/Pareto concurrency, macro compilation, and M-8–M-10 visibly blocked by the M-4 stop line.
- Correct stale links from nonexistent `plans/` targets to actual `doing/`/`done/` paths or reorganize once and let the link checker enforce it.

### 8.4 `docs/04_roadmap/milestones.md` diff directive

- Add the version mapping in §6.1 and exact M-0…M-10 entry/exit gates in §6.2.
- In M-2, name NOVA-1/NOVA-2 as release blockers and define legacy trajectory handling.
- In M-3, replace “plugin slots” with Named Component Graph; require all residual `layer0/events` removal and the six NOVA-4 negatives.
- In M-4, reproduce the nine-row table verbatim and state “one run, one lineage, no stitching.”
- In M-5, name **Math & Formal Deductive Verification**—not “math or data”—and the exact zero-diff generality criterion.
- In M-6, bind public spawn to S0–S12 and TCB budget.
- In M-7, make NOVA-2 and selector soundness entry gates; specify the obligation projection, pull claims, versioned profiles, quote/settlement calibration, and conditional—not categorical—scaling metric.
- In M-8/M-9, add the macro candidate IR and laboratory pipeline. Candidate synthesis is not registry promotion.
- In M-9, make the five-SPI revisit evidence-based rather than an assumed expansion.
- In M-10, require unforgeable pairs, exact paired statistics, safety Pareto gate, human pointer authority, and rollback for macro, skill, model, and harness treatments.

### 8.5 Wave-plan diff directive

- **Wave 2 active plan:** add NOVA-1 telemetry-to-trajectory wiring and schema tests; add NOVA-2 fresh-process fixture; add explicit non-goals (no graph/spawn/concurrency). Re-gate only when current runtime/adapter failures are adjudicated.
- **Wave 3 plan:** order work as manifest/2 law/schema → compiler semantic passes → registry/FSM events → capability intersection → six topology fixtures → code-default migration → NOVA-4 → delete all Layer-0 → walking skeleton. Do not delete first.
- **Wave 4 plan:** replace broad demo prose with the nine-row evidence table, exact artifact paths, same-run binding checks, anti-cheat rules, abort criteria, and Director sign-off block. A failed row leaves M-4 red even if the task output looks correct.
- **Post-M-4 plan:** create M-5 only after the sign-off; put doc collapse, Pack #2, and exact witness memoization there. Create M-6+ packets just in time. M-7 owns obligations/Pareto, M-8 owns builder/macro IR, M-9 owns macro lab, and M-10 owns promotion—none is active work early.

### 8.6 `README.md` and agent-guidance consistency

The repository currently contains stale pre-development-hold language in contributor guidance while ADR-0075/README state that Wave 0 was authorized and M-0/M-1 are complete. After this proposal is adjudicated, reconcile the guidance to say exactly which milestone is authorized and which stop lines remain. The safer form is a pointer to the one living board, not duplicated status prose that will drift again.

---

## 9. Risk register, stop lines, and ownership

| Risk | Likelihood / impact | Early signal | Mitigation / owner |
|---|---|---|---|
| Hollow corpus continues | High / critical | New `/1` rows with zero costs | NOVA-1 M-2 release blocker / CIO + Tech Lead |
| Graph becomes workflow engine | Medium / critical | scheduling semantics enter compiler/kernel | ADR-0077 tests and ADR-0003 / Systems Architect |
| Manifest migration breaks attribution | Medium / high | same resolved graph gets unstable $D_H$ | golden JCS vectors, compatibility reader, no backfill / CIO |
| Layer-0 behavior copied fail-open | Medium / critical | discarded ceiling, dual emitter/store | NOVA-4 and deletion gate / Tech Lead |
| Sandbox overclaim | Medium / critical | “bwrap present” without probes or setuid use | pinned unprivileged mode, probes, layered LSM/seccomp / CIO |
| Swarm state corruption | Medium / high | mutable shared blobs, unowned writes, hot-key conflicts | content refs, CAS claims, writer roles, conflict tests / Systems Architect |
| Obligation explosion | Medium / high | decomposition rate exceeds discharge; frontier grows without evidence | child/depth prices, progress predicate, admission/backpressure / Tech Lead |
| Pareto theater | High / high | infeasible choices scored; raw vectors discarded; predictions replace settlement | lexicographic gates, quote/settlement join, calibration tests / CTO + AI Specialist |
| Poisoned memo reuse | Medium / critical | witness reused after input/checker/policy/revocation change | complete memo key, TTL/revalidation, subject-bound original witness / CIO |
| Macro authority smuggling | Medium / critical | wildcard ceiling, captured secret/oracle value, untyped runner | taint scan, least selector hull, ordinary plugin/S0–S12 path / Systems Architect |
| Macro benchmark overfit | High / high | replay green but held-out failures/tail regression | held-out paired cells, adversarial properties, immutable baseline, exact promotion / AI Specialist |
| Spawn bloats TCB | Medium / critical | kernel exceeds 1438 or knows task topology | reuse dispatch, remove equivalent LOC, M-6 gate / Director |
| Generality theater | Medium / high | Pack #2 adds math logic to kernel/domain | zero-diff tree hash falsifier / Principal Staff Engineer |
| Causal overclaim | High / medium | blame inferred from order/attention | provenance slice + paired intervention labels / AI Specialist |
| Reward/preference forgery | Medium / critical | agent/critic labels enter training | signed pair certificate and exterior verdict gate / CIO |
| Statistical p-hacking | Medium / high | task/alpha/stopping selected after results | preregistration, multiplicity correction, immutable trials / AI Specialist |
| Documentation drift | High / medium | contradictory milestone/status/links | M-5 Clean Triad collapse / Director |

Hard stops:

- Any authority widening, evaluator reachability, writer ownership violation, or evidence forgery stops the milestone.
- Any TCB over-budget result stops merge.
- Any M-4 row missing stops v0.7.0 and all M-5+ implementation.
- Any Pack #2 domain/kernel diff stops the generality claim and M-6.
- Any memo that crosses a subject/environment/checker/protection binding stops M-5.
- Any stale/double obligation claim, unbounded decomposition, or implicit lease renewal stops M-7.
- Any macro with widened authority, captured tainted constants, uncertain-effect fallback, or no held-out exterior equivalence stops M-9/M-10.
- Any safety invariant regression stops promotion regardless of task score or p-value.

---

## 10. Director decision package

The Engineering Director should record one explicit disposition for each item:

1. Accept/reject ADR-0077 and authorize manifest/2 implementation at M-3.
2. Accept/reject ADR-0078 and the required/declared-absent/forged trichotomy.
3. Accept/reject ADR-0079, including the two lifecycle event kinds and full Layer-0 deletion gate.
4. Accept/reject ADR-0080’s bounded loop claim, keep mediated spawn implementation at M-6, and schedule typed obligations/pull claims only at M-7.
5. Accept/reject ADR-0081 and place NOVA-1/NOVA-2 in M-2 now.
6. Accept/reject ADR-0082’s T0–T3 compounding ladder and paired, signed, Pareto-safe promotion protocol.
7. Confirm v0.6.1/v0.6.2/v0.6.3/v0.7.0 mapping and M-4’s same-run nine-row stop.
8. Confirm Pack #2 as Math & Formal Deductive Verification and its zero-domain/kernel-diff gate.
9. Confirm documentation collapse at M-5, after—not before—M-4.
10. Assign owners to the currently red adapter/runtime evidence before claiming a release-quality baseline.
11. Accept/reject VAOH as the post-M-4 synthesis: obligation frontier at M-7, Pareto profiles as exterior policy, and no new trusted scheduler.
12. Accept/reject the T0–T3 compounding ladder and `mhf.macro-tool/1` candidate contract, including human-only default-pointer promotion.

### Final Leadership 7 mandate

AETHER’s defensible moat is not the number of agents it can launch. It is the ability to compose arbitrary cognitive topologies while keeping authority attenuated, state reconstructible, and evidence exterior and unforgeable. The path to a swarm meta-framework is therefore:

\[
\boxed{
\text{one mechanism}
+\text{named frozen graph}
+\text{typed obligation frontier}
+\text{Pareto/EFE exterior control}
+\text{exterior signed evidence}
+\text{memoized witnesses}
+\text{verified macro compilation}
+\text{paired human-gated promotion}
}
\]

Close the corpus and continuation defects first. Converge composition and delete the fork second. Prove the nine-row foundation once, without cheating. Prove a non-coding formal domain and exact witness reuse next. Only then add mediated delegation, a lease-bound obligation swarm, Pareto/Active-Inference routing, framework construction, macro compilation, and statistical learning. If any later feature requires weakening the Clean Triad, bypassing the universal loop, or allowing a candidate to certify itself, the feature is wrong for this substrate—not the invariant.
