---
id: VG-02
file: 02_vanguard_charter_claims_and_non_claims_v040.md
title: "Vanguard v4.0 — Charter, Claims & Non-Claims"
version: 4.0.0
status: NORMATIVE
authority_scope: >
  Mission and operational thesis; scope and the unit of execution; non-claims;
  falsifiable claims; design axioms; cross-cutting norms; irreversibility analysis;
  strategic frame; approved stack at decision level; risk register; honest limits.
supersedes: none (v4 is the first version of this document)
superseded_by: none
budget_words: 3000
owners: [Tech Lead, Research Lead]
last_reviewed: 2026-08-14
---

# Vanguard v4.0 — Charter, Claims & Non-Claims

> **One sentence.** Vanguard is an evidence-directed competence runtime: it executes episodes over typed environments, authorises effects through scoped capabilities, evaluates outcomes with independent evaluators, accumulates competence artifacts with explicit validity, and produces candidate versions of its own components through an external release pipeline.

---

## 0. What this document owns

This is the entry point to the v4 set. It owns the claims the system makes about itself, the claims it refuses to make, the axioms every other document is measured against, and the norms cutting across all of them.

It owns **no mechanism**: planes and execution belong to `03`; schemas to `04`; kernel and security to `05`; competence and memory to `06`; measurement and self-improvement to `07`; the build plan to `08`. Precedence is resolved by `00 §2`, never here. If a statement below would tell an engineer *how* to build something, that is a defect under `00 §1 [PR-1]`.

Read this first, then `03`, then whichever document owns the contract you are about to change.

---

## 1. Mission and operational thesis

The field cannot answer a basic question: **when an agent solves a task, what solved it?** Model, scaffold, prompt, tool design, context strategy and retry policy are confounded in every published result, because every agent ships as an indivisible artifact and every benchmark measures the artifact rather than the decisions inside it.

This is an instrument problem. If harness components are genuinely composable and the judge is genuinely outside the system being judged, one-variable experiments become possible: same model, same manifest, same evaluator, one component changed. That comparison is currently unavailable to anyone, and once it exists a search over configuration space becomes meaningful, because the evaluator decides what survives.

The persistent object is therefore not a conversation, a prompt or a snapshot of ability. It is:

$$S_t = (G_C,\; G_E,\; L,\; A_t)$$

where $G_C$ is the immutable graph of competence artifacts, $G_E$ the graph of claims, evaluations and invalidations, $L$ the ledger of episodes, effects and lineage, and $A_t$ the activation set valid for the current context. The familiar four-part view of competence — representations, operators, methods and policies — is a **typed projection of $G_C$**, not the store itself.

**The Coding Cell is the runtime's first client, not its ontology.** Coding is chosen as the primary laboratory because it has cheap, objective, adversarially-robust verification, which is the property the entire improvement flywheel runs on. It is not chosen because the system is a coding tool.

"Cognitive operating system" is product language, not architecture. It promises scheduling, isolation, resource ownership and lifecycle that the system does not yet provide. It appears in `12`, never in a specification. **The system earns the name before it prints it on the kernel.**

---

## 2. Scope and the unit of execution

The unit of execution is an **Episode**:

$$E = (\text{Task},\; \text{EnvironmentSnapshot},\; \text{ActivationSet},\; \text{Budget},\; \text{PolicySet})$$

An episode produces transitions of the form *state → proposal → authorisation → effect → receipt → observation*. The runtime does not call this "thought"; it is an observable operational trail. Private reasoning inside a model provider is neither required nor assumed accessible.

In scope for the first two phases: the coding environment; one deliberately non-coding environment; the kernel, capability and evaluation machinery; the measurement laboratory. Explicitly out of scope: autonomous operation without an accountable principal; a graphical authoring surface; multi-model orchestration beyond a port; any mechanism requiring the runtime to modify itself in place.

---

## 3. Non-claims

Stated before the claims, because a charter that lists only guarantees is misleading.

| # | Not claimed | Why it matters |
|---|---|---|
| NC-01 | AGI, or open-ended discovery of new paradigms | The falsifiable version is narrower and stated in §4 |
| NC-02 | That every syscall passes a mediating layer in the host language | A logical mediator is not a containment boundary; see `A-03` |
| NC-03 | Resistance to a malicious operator, or to a kernel-level exploit | The threat model is untrusted *content*, not an untrusted principal at the console |
| NC-04 | That the model is trusted | It is treated as potentially adversarial; its outputs pass the same authorisation as any other request |
| NC-05 | Semantic truth from passing tests | A passing suite proves conformance to that oracle, under that protocol, in that environment |
| NC-06 | Determinism from remote models | Reproducibility is achieved by recording and replay, not by assuming stability |
| NC-07 | Complete provenance tracking | It is best-effort at sub-block granularity; the block label is the enforced unit |
| NC-08 | Instantaneously exact budget enforcement | Exact at commit; a single in-flight call may overrun and is debited |
| NC-09 | Cryptographic protection of stored artifacts against an adversary with write access | Digests give integrity against corruption and accidental substitution |
| NC-10 | Autonomous self-update of the policy kernel | Candidate generation is permitted; promotion is externally gated |
| NC-11 | Transferable learning, until demonstrated by ablation and holdout | Claimed transfer without ablation is memorisation with better marketing |
| NC-12 | That a shell classifier is a security boundary | It is a parser, and parsers can be parsed around |

---

## 4. Falsifiable claims

Recorded so they can be lost. Each names what would falsify it.

| # | Claim | Falsified by |
|---|---|---|
| C-01 | Every reference harness is expressible as configuration, with no core change | Any reconstruction requiring a loop modification |
| C-02 | Memory, retrieval, tool protocols, web search and knowledge graphs are registry entries plus configuration | Any of them requiring a core change |
| C-03 | An adapter's implementation language changes without touching anything above its port | A language swap forcing changes above the port |
| C-04 | Parallel execution of declared-independent work materially reduces wall-clock on real tasks | Measured latency parity |
| C-05 | Operator context isolation improves outcomes on long tasks against a flat agent at equal budget | No measured lift |
| C-06 | At least one distilled competence artifact beats the unguided baseline, with a confidence interval excluding zero, above the null-comparison floor | Nothing clearing the floor — a genuinely interesting negative result |
| C-07 | The policy kernel stays within its stated size ceiling through Phase 2 | Drift, which is the early warning that a workflow engine is being reinvented |
| C-08 | Every externally consequential effect is bounded by an enforcement boundary independent of the model | Any effect reaching a resource outside its declared selector under a granted capability |
| C-09 | A competence artifact survives replacement of the underlying model without re-derivation | Systematic degradation on model change |
| C-10 | The same core serves a second, non-coding environment with no special cases | Any coding capability that cannot be expressed in the shared competence space |
| C-11 | A killed process is closed by the recovery controller, with uncertainty preserved where an external effect's occurrence cannot be determined | Any recovery path that resolves an undeterminable effect to success or failure |
| C-12 | An active artifact carries an automatic invalidation condition (`04 [INV-2]`) that fires when it goes stale | Staleness discovered only by human review |

---

## 5. Design axioms

Load-bearing. A feature violating one is rejected, or the axiom is amended explicitly — never silently.

| # | Axiom | Enforcement |
|---|---|---|
| A-01 | The episode is the only execution primitive | No workflow engine, topology language, graph validator or node registry exists in the tree |
| A-02 | Extensions compose by invocation, and cognitive operators are data rather than control flow | One composition mechanism; operators are addressable, versioned, replaceable entries |
| A-03 | Effects are authorised before a capability is issued, and bounded by an enforcement boundary independent of the model | Two classes: broker-mediated effects and in-sandbox effects |
| A-04 | Content carries provenance on orthogonal axes, and provenance constrains authority | Type-level: raw strings cannot enter context assembly |
| A-05 | The verifier is outside the mutable surface | Reachability test: no capability resolves to a verifier-owned path |
| A-06 | Emitted effect order is preserved; parallelism requires declared independence | Independence groups or provably disjoint read/write sets over a common snapshot |
| A-07 | Everything is an event | One durable typed ledger; every surface is a projection of it |
| A-08 | Configuration is declarative at the agent level, never at the graph level | Adding a capability is a registry entry plus a configuration line |
| A-09 | Clients are pure consumers; events never schedule work | Architecture test: client modules hold no adapter handles |
| A-10 | A gate that cannot fail is not a gate — and a requirement that cannot be satisfied is not a requirement | Every fix ships a test proven to fail against pre-fix code; every requirement is checked for physical satisfiability before a test is written for it |
| A-11 | Extensions resolve once at composition, then freeze | No runtime discovery, no dynamic registration |
| A-12 | Instrument error is not task failure | *Inconclusive* is a first-class verdict, never coerced into failure |

---

## 6. Cross-cutting norms

Rules that bind more than one document, and that are not already stated as axioms. Document-local rules live with their owner and are indexed in `00 §6`.

| # | Norm |
|---|---|
| N-01 | The model proposes; the broker authorises; the environment executes; the evaluator evidences |
| N-02 | A guarantee may not exceed the boundary that actually enforces it |
| N-03 | Every capability carries principal, action, resource, constraints, purpose and expiry |
| N-04 | An over-broad request is denied and recorded as an escalation attempt; it is never silently narrowed |
| N-05 | Child capabilities are a subset of the parent's; child limits do not exceed the parent's remaining budget |
| N-06 | Shell is contained by the sandbox; it is not mediated by the host language |
| N-07 | Control plane, worker, evaluator and updater have distinct identities and surfaces |
| N-08 | The agent creates candidates; it never alters the live runtime |
| N-09 | Origin, instruction authority, integrity, confidentiality and epistemic state are distinct axes |
| N-10 | Only the verifier admits; rankers rank |
| N-11 | An evaluator produces a scoped claim; no claim is granted abstract objectivity |
| N-12 | Local success does not promote a generalisation without its own test |
| N-13 | A claim or artifact that cannot state what would refute it is inadmissible |
| N-14 | Competence is an immutable graph plus activation views; forgetting removes from the active view and preserves lineage |
| N-15 | A dead process is closed by the recovery controller, never by fiction inside the dead process |
| N-16 | Leases release on every path, including creation failure |
| N-17 | Registries freeze at composition; unknown names fail at composition, not at first use |
| N-18 | Safety, privacy and authority are hard constraints; performance lives on the frontier |
| N-19 | Full content capture happens by policy only; the training corpus is separately opt-in |
| N-20 | Playbooks constrain — masking tools, injecting context, evaluating gates — and never dispatch |
| N-21 | The brief is immutable and exempt from compaction |

---

## 7. What locks now, what stays open

Irreversibility is the only reason to decide early. These six lock before a corpus exists.

| # | Lock | Why it is irreversible |
|---|---|---|
| L-1 | Trajectory, event and competence schemas | This is the corpus format. Changing it means re-running everything ever recorded |
| L-2 | Kernel boundary and TCB partition | Every safety property and the entire self-improvement argument rest on it |
| L-3 | Operators as data, not control flow | Determines whether operator-level improvement is reachable at all |
| L-4 | The improvement relation: hard constraints, then frontier, then activation | Scalar objectives are self-reinforcing through the corpus |
| L-5 | Verifier exteriority and predicate-scoped evaluator classes | There is no other mechanism keeping proxy reward at or below zero |
| L-6 | Seams: subprocess with line-delimited JSON, versioned artifacts on disk | Cross-language contracts outlive the code that produced them |

Genuinely open, and to be decided on evidence: the core runtime language; native-addon optimisation; which cognitive operators to build; discovery-engine sophistication; multi-model orchestration depth; and the full metric suite. Once `L-3` lands, cognitive content lives in data rather than code, which converts the language question from strategic to tactical.

---

## 8. Strategic frame

**The correction that defines v4.** Competence becomes an evidenced graph; permission becomes a scoped capability; the trajectory becomes transactional storage with projections; the sandbox becomes a real boundary; the verifier becomes claim-specific; self-editing becomes a release pipeline. With those six, the coding harness stops being a product disguised as a platform and becomes the first environment adapter of a general runtime.

**The capture risk, and the hedge.** A coding-first architecture risks permanent capture by coding's logic. A synthetic-environment-first architecture has the symmetric failure: no users means no forcing function, and research architectures without forcing functions produce elegant unfalsifiable layers. The resolution is a dual track, asymmetrically weighted — roughly 80% coding as the verifiable laboratory, roughly 20% one deliberately impoverished non-coding environment sharing the same competence space, kernel and operator registry — governed by a hard constraint:

> **No capability may be added to the coding track that cannot be expressed in the shared competence space.** If a coding feature needs a special case, that is the capture happening, and it is a design defect rather than a pragmatic exception.

The constraint does the work, not the ratio. Without it, the second track becomes a research project nobody staffs. With it, every coding feature is forced through the general abstraction, and the general abstraction is exercised daily by the thing that has users.

**The standing warning**, owned as a mental model by `01 §1`: premature formalisation is indistinguishable from rigor at the moment of the decision. Ask of every plan *how many things must be simultaneously correct before the first feedback signal?* — and collapse that number rather than lowering the ceiling. **The standing exception:** the kernel, verifier and capability boundary stay at full rigor. They are the only thing between "self-improving" and "self-deceiving".

**The strategic exit criterion.** A competence artifact that (a) was not author-written, (b) demonstrably improves performance on tasks it was not distilled from, (c) survives replacement of the underlying model, and (d) carries an evidence block that would survive adversarial review by someone trying to show it is memorisation. Achieving it means the next phase funds a demonstrated mechanism; failing it is a publishable negative result, and a better outcome than an unfalsifiable success. If the criterion looks too demanding for the budget, extend the timeline — never weaken the criterion.

---

## 9. Approved stack — decision level

Rationale and seams are owned by `03 §12`; security properties by `05`.

| Area | Decision |
|---|---|
| Control plane | **Python (`ADR-0063`, 2026-08-16).** Reversed on evidence from the original TypeScript-on-Node decision (`ADR-0001`), whose stated reversal condition — decisive team-composition shift — had fired. Alternative runtimes stay behind a conformance matrix and soak test |
| Interaction client | TypeScript (strict) on Node.js LTS. Also the `ADR-0014` second-language contract reader |
| Wire contracts | JSON Schema 2020-12, normative, with semantic specification and golden vectors |
| Validation | A TypeScript validator as *implementation*, verified against the schemas — never as the source of truth |
| Canonicalisation | RFC 8785 / JCS, with conformance vectors |
| Durable store | Embedded transactional store with write-ahead logging, single writer; line-delimited JSON as export and interchange |
| Blob store | Content-addressed on the filesystem, with an encryption hook present from the first contract |
| Sandbox | Hardened rootless container for development; stronger isolation by risk tier, reported rather than asserted |
| Evaluator | Separate process and identity, distinct image digest and mounts |
| Laboratory | Python, offline, reading exports; never in the request path |
| Systems seams | Subprocess with line-delimited JSON over standard streams |

---

## 10. Risk register

| # | Risk | Mitigation | Severity |
|---|---|---|---|
| RSK-01 | Verifier compromise — every downstream number becomes worthless | Immutable by construction, sealed execution, unreachable from every capability, adversarial audit before any training run | Critical |
| RSK-02 | Reward hacking through a weak proxy silently becoming the objective | Predicate-scoped evaluator classes; proxies rank but never admit; drift monitored against human judgement | Critical |
| RSK-03 | Memory poisoning — an unverified lesson persists, is recalled, appears confirmed | Scoped claim pipeline, per-record provenance, adversarial ablation at activation, automatic demotion | High |
| RSK-04 | Measurement theatre — vacuous passes, degenerate floors, undeclared families | Instruments that refuse rather than report; every gate proven able to fail | High |
| RSK-05 | Contamination of holdout or sealed splits | Split discipline, touch ledger, per-instance corpus membership check | High |
| RSK-06 | Underpowered claims | Sample size derived from the floor and recorded in the family declaration | High |
| RSK-07 | Capability escalation through resource-blind permissions | Resource-scoped capabilities; explicit denial and an alertable escalation event | High |
| RSK-08 | Silent self-modification of the live runtime | Candidate generation only; hermetic external build, attestation, signed canary, automatic rollback | High |
| RSK-09 | Optimiser monoculture — steady gains, permanent plateau | Explicit variance budget against a held-out different set | Medium |
| RSK-10 | Circular training — the model tunes to this harness, invalidating harness comparisons | Harness comparisons always use an untuned model | Medium |
| RSK-11 | Core drift — the kernel grows and a workflow engine is reinvented under new names | Size budget as a tracked metric with an alert; an ADR per core change | Medium |
| RSK-12 | Competence ossification — the library encodes workarounds for weaknesses that no longer exist | Staleness windows, invalidation conditions, automatic demotion, re-evaluation on model change | Medium |
| RSK-13 | Calibration collapse — persistence rewarded, abstention trained out | Abstention as a first-class scored outcome | Medium |
| RSK-14 | Governance re-accretion — process overhead outpacing the artifact | Reinstate weight only when team size makes coordination genuinely costly | Low |
| RSK-15 | Premature generalisation before the coding case pays | Let evidence answer the generality question | Low |

---

## 11. Honest limits

1. **The flywheel is bounded by the evaluator.** In domains without cheap ground truth it stalls. This is the central unsolved problem, and no amount of architecture solves it.
2. **Optimisation does not leap.** Paradigm shifts come from humans reading trajectories. The system's contribution is making anomalies visible.
3. **Coding is a privileged domain.** Whether verifier-gated recursive improvement generalises to domains without objective ground truth is genuinely open, and treating it as settled causes over-investment in generality before the coding case has paid.
4. **Reconstructions are reconstructions.** A comparison against a faithful reimplementation of a published architecture is a comparison against *that reimplementation*, and is labelled as such.
5. **Most measured differences will be noise** at achievable sample sizes — and the temptation to believe a favourable result is strongest precisely when you designed the change.
6. **Statistical power is expensive.** Experiments per year are finite and fewer than intuition suggests. Choosing which to run is the scarcest resource in the programme, and it is human.
7. **Genuine novelty may not be operationalisable** without being gameable. If so, the retained-under-ablation proxy may be all that is ever available — making this a programme about *useful* rather than *genuine* competence expansion, which is weaker and still valuable.
8. **Credit assignment is unsolved for long runs.** Counterfactual ablation is correct and expensive; dense verifier signal helps in code and may not generalise.
9. **Some claims here will fail.** `C-06` may never clear the floor — a valuable negative result about methodology itself, and worth publishing.
10. **"AGI" is not a claim this project makes.** What is claimed: *a system that measurably improves its own harness under an evaluator that cannot be gamed, in a domain where verification is cheap.* Sharper, more defensible, and — unlike the label — falsifiable.


