# Vanguard / GTS — System Specification Theory

Normative synthesis of the `docs/main_v4/` corpus (VG-00 … VG-12, GTS-13C) at spec version `4.0.0`
(with the v0.4.1 "v4B" patch set applied per `ADR-0061`). This document is a compressed, structurally
mirrored restatement of the specification only. It contains no observations about implementation.

Source authority is unchanged: where this synthesis and a `docs/main_v4/` document disagree, the source
document wins. Rule identifiers, type names, port names, state names and numeric budgets are reproduced
verbatim so that they can be matched against symbols in code.

---

## Table of Contents

0. [Document Registry, Precedence & Identifier Namespaces (VG-00)](#0-document-registry-precedence--identifier-namespaces-vg-00)
1. [System Identity, Claims & Non-Claims (VG-02)](#1-system-identity-claims--non-claims-vg-02)
2. [Turn Lifecycle, Planes & Execution Model (VG-03)](#2-turn-lifecycle-planes--execution-model-vg-03)
3. [Core Contracts & Wire Schema (VG-04)](#3-core-contracts--wire-schema-vg-04)
4. [Policy Kernel, Capability Attenuation & Security Model (VG-05)](#4-policy-kernel-capability-attenuation--security-model-vg-05)
5. [Competence, Memory & Evidence Model (VG-06)](#5-competence-memory--evidence-model-vg-06)
6. [Loop Engineering, Measurement & Self-Improvement (VG-07)](#6-loop-engineering-measurement--self-improvement-vg-07)
7. [Architectural Decision Record Summary (VG-09)](#7-architectural-decision-record-summary-vg-09)
8. [Deferred & Rejected Design Space (VG-10)](#8-deferred--rejected-design-space-vg-10)
9. [Build Plan, Programme Spine & Roadmap Milestones (VG-08, GTS-13C)](#9-build-plan-programme-spine--roadmap-milestones-vg-08-gts-13c)
10. [Engineering Handbook Principles (VG-01)](#10-engineering-handbook-principles-vg-01)
11. [Convergence Evidence & Vision Annex (VG-11, VG-12)](#11-convergence-evidence--vision-annex-vg-11-vg-12)
12. [Appendix — Internal Contradictions & Ambiguities in the Corpus](#12-appendix--internal-contradictions--ambiguities-in-the-corpus)

---

## 0. Document Registry, Precedence & Identifier Namespaces (VG-00)

### 0.1 Precedence rules (`PR-1` … `PR-5`)

| # | Rule |
|---|---|
| `PR-1` | **One owner per contract.** Each contract has exactly one owning document. Others reference it by anchor and may not restate it |
| `PR-2` | **The registry is the authority.** Precedence is resolved by VG-00 Ch. 2, never by a document's claim about itself |
| `PR-3` | **Registration is a gate.** A document not listed in VG-00 Ch. 2 is not normative, regardless of content, location or status header |
| `PR-4` | **Conflict is a defect, not a ranking.** Disagreement between v4 documents is a bug in owner assignment, fixed by removing the duplicate |
| `PR-5` | **Independence.** No v4 document may cite as authority or require reading any pre-v4 document |

Ambiguity resolution order: owning document → registry → Tech Lead. No fourth step.

### 0.2 The document set and status classes

| # | File stem | Authority scope | Status |
|---|---|---|---|
| 00 | `00_vanguard_registry` | Precedence, status, budget, supersession, retirement | AUTHORITY MAP |
| 01 | `01_vanguard_engineering_handbook` | Mental models, SOLID/DRY, testing taxonomy, ADR format, repo layout, glossary | LIVING |
| 02 | `02_vanguard_charter_claims_and_non_claims` | Mission, scope, non-claims, claims, axioms, norms, locks, risk, limits | NORMATIVE |
| 03 | `03_vanguard_architecture_planes_and_execution_model` | Planes, episode engine, concurrency, context, environments, playbooks, failure taxonomy | NORMATIVE |
| 04 | `04_vanguard_core_contracts_and_wire_schema` | Schemas, wire format, canonicalisation, capability/competence/event types, ports, versioning | NORMATIVE |
| 05 | `05_vanguard_kernel_capabilities_and_security` | Policy kernel, dispatch, grants, attenuation, sandbox, self-modification, threat model | NORMATIVE |
| 06 | `06_vanguard_competence_memory_and_evidence` | Competence graph lifecycle, claim pipeline, verification, substrate invariance | NORMATIVE |
| 07 | `07_vanguard_loop_engineering_and_measurement` | Closure conditions, measurement doctrine, promotion, release pipeline, experiment registry | NORMATIVE |
| 08 | `08_vanguard_phase_0_build_plan` | Increments, tickets, must-fail suite, CI gates, exit criterion | DISPOSABLE |
| 09 | `09_vanguard_decision_register` | ADRs with reversal conditions | LIVING |
| 10 | `10_vanguard_deferred_and_rejected_register` | Deferrals and rejections with reversal conditions | LIVING |
| 11 | `11_vanguard_design_convergence_evidence` | Attested convergence summary | EVIDENCE (secondary) |
| 12 | `12_vanguard_vision_annex` | Analogies, long-horizon framing, product language | **NON-NORMATIVE** |
| 13C | `13_C_gts_mvp_program_and_engineering_plan` | Programme plan and rationale only (not registered in Ch. 2) | LIVING, non-normative |

Status semantics: `NORMATIVE` (binding contract, change requires an ADR in 09) · `LIVING` (binding practice,
PR-changeable) · `DISPOSABLE` (binding until phase end) · `AUTHORITY MAP` · `EVIDENCE` (append-only) ·
`NON-NORMATIVE` · `SKELETON`.

Document 12 must carry the header: `NON-NORMATIVE. Not a specification. No ticket may cite this document.`

### 0.3 Word budget ledger

**Envelope: ≤32,000 normative + ≤15,000 supporting = ≤47,000 total.** Normative target ~29,000.
Per-document caps (target in brackets): `02` 3,000 [2,700] · `03` 6,000 [5,400] · `04` 6,000 [5,400] ·
`05` 5,000 [4,500] · `06` 4,000 [3,600] · `07` 5,000 [4,500] · `08` 3,000 [2,700] — normative subtotal
32,000 [28,800]. Supporting: `00` 4,500 · `01` 4,000 · `09` 3,000 · `10` 2,000 · `11` 1,000 · `12` 1,000 —
subtotal 15,000.

`BR-1` — CI fails on any cap breach; resolved by deleting duplication or moving content to its owner,
never by silently raising the cap. The authoritative counter is `tools/wordcount_v4.sh`: strip leading
YAML front-matter, strip fenced code blocks including fences, count whitespace-separated tokens
containing ≥1 alphanumeric character. Tables, headings, links and blockquotes count; code does not.

### 0.4 Identifier namespaces (global, permanent, never reassigned)

| Prefix | Meaning | Owner |
|---|---|---|
| `VG-nn` | Document identity, **equal to the file index** | 00 |
| `SC-n` · `GV-n` | Schema and vector conventions | `schemas/v4/` |
| `C-nn` / `NC-nn` / `A-nn` / `N-nn` / `L-n` / `RSK-nn` | Claim / non-claim / axiom / norm / lock / risk | 02 |
| `LT-n` / `CC-n` / `FT-nn` | Layer contract / concurrency rule / failure class | 03 |
| `CT-nn` / `D-n` / `INV-n` | Contract rule / descriptor normalisation / invalidation | 04 |
| `K-nn` / `F-nn` / `SA-n` / `R0`–`R4` / `T-nn` / `AT-nn` | Kernel rule / failure path / self-mod rule / mutability class / threat / architecture test | 05 |
| `MEM-n` / `V-nn` | Memory rule / verification invariant | 06 |
| `CL-n` / `M-nn` | Closure condition / measurement rule | 07 |
| `TK-nn` / `MF-nn` | Phase 0 ticket / must-fail test | 08 |
| `ADR-nnnn` | Architecture decision record | 09 |
| `DEF-nn` / `REJ-nn` | Deferred / rejected item | 10 |
| `PR-n`, `BR-n`, `AR-n`, `CV-n`, `H-nn` | Registry rules | 00 |

Anchoring: a reference to a *rule* carries its ID (`05 §3 [K-07]`); a reference to a *topic* may cite the
section alone. Renumbering a frozen document requires an ADR because references resolve positionally.

### 0.5 Rule-family census (VG-00 §6)

Claims 12 · Axioms 12 · Non-claims 12 · Norms 21 · Locks 6 · Risks 15 · Layer contracts 8 ·
Concurrency 7 · Failure taxonomy 17 · Contracts (`CT-*`) 53 · Descriptor 6 · Invalidation 2 ·
Kernel (`K-*`) 49 · Failure paths (`F-*`) 26 · Self-modification 6 · Architecture tests 12 · Threats 8 ·
Memory 7 · Verification 13 · Closure 3 · Measurement 28 · Must-fail 37 · Tickets 13 · Decisions 45 ·
Deferred+Rejected 24 · Schema/vector 18.

**Coverage is generated, not asserted** by `tools/rule_test_map.py` (enforces `CI-9`).
**Phase 0 baseline: 203 normative rules · 28 tested · 42 untestable-with-justification · 133 uncovered.**

### 0.6 CI rules and acceptance verification

| ID | Rule | Method |
|---|---|---|
| `CI-1` | Registry Ch. 2 and `docs/v4/` are in exact bijection | Script |
| `CI-2` | No v4 file names a pre-v4 source, except `00 §7` | `tools/audit_v4.py` |
| `CI-3` | Every cross-reference resolves | `tools/audit_v4.py` |
| `CI-4` | No identifier is defined in two documents | `tools/audit_v4.py` |
| `CI-5` | Per-document and subtotal caps hold | `tools/wordcount_v4.sh` |
| `CI-6` | Every schema validates against JSON Schema 2020-12 and has golden vectors | Schema job |
| `CI-7` | Every rule ID prefix is declared in Ch. 5 | `tools/audit_v4.py` |
| `CI-8` | Document 12 carries its header; no other document references it | Grep |
| `CI-9` | Every rule maps to a test, or is marked untestable with justification | `rule_test_map.py` |

Acceptance checks `CV-1` … `CV-13` gate removal of the pre-v4 corpus. `CV-13` is the **comprehension
gate**: a non-author engineer reading only the v4 set must state unaided which document is normative
for a given contract and how they know; the three closure conditions; the self-modification contract and
why in-place modification is prohibited; why a verb-only permission set cannot authorise; and why a
passing suite does not establish semantic truth. **Not waivable.**

Recorded acceptance state: 13 of 13 documents authored, `02`–`08` frozen; `CI-1`…`CI-8` PASS;
`CI-9` **RED by construction** (regression-blocking at 133); `CV-1`…`CV-12` PASS (12/12);
`CV-13` **OPEN**, not self-certifiable; 7 writer + 7 reader schemas valid 2020-12, all `DRAFT`;
`SC-7` and `SC-12` OPEN, assigned to `TK-01`. Verdict: *development ready pending `CV-13` and PL acceptance*.

Archive protocol: `AR-1` nothing deleted before acceptance · `AR-2` annotated git tag `pre-v4-corpus`
before removal · `AR-4` archived material never edited · `AR-5` normative text is English-only ·
`AR-6` the prototype repository is frozen, forensic source only · `AR-7` a `DISPOSABLE` document retires
at phase exit, its surviving contracts having first moved to a `NORMATIVE` owner.

---

## 1. System Identity, Claims & Non-Claims (VG-02)

### 1.1 Mission and operational thesis

Vanguard is an **evidence-directed competence runtime**: it executes episodes over typed environments,
authorises effects through scoped capabilities, evaluates outcomes with independent evaluators,
accumulates competence artifacts with explicit validity, and produces candidate versions of its own
components through an external release pipeline.

The problem being solved is an **instrument problem**: when an agent solves a task, model, scaffold,
prompt, tool design, context strategy and retry policy are confounded because every agent ships as an
indivisible artifact. If harness components are genuinely composable and the judge is genuinely outside
the system being judged, one-variable experiments become possible: same model, same manifest, same
evaluator, one component changed.

### 1.2 The persistent object

The persistent object is not a conversation, a prompt, or a snapshot of ability:

```
S_t = (G_C, G_E, L, A_t)
```

- `G_C` — the **immutable graph of competence artifacts**
- `G_E` — the graph of **claims, evaluations and invalidations**
- `L` — the **ledger** of episodes, effects and lineage
- `A_t` — the **activation set** valid for the current context

The four-part view of competence (representations, operators, methods, policies) is a **typed projection
of `G_C`**, not the store itself.

**The Coding Cell is the runtime's first client, not its ontology.** Coding is chosen because it has
cheap, objective, adversarially-robust verification. "Cognitive operating system" is product language,
not architecture; it appears in VG-12 only.

### 1.3 Unit of execution

```
Episode E = (Task, EnvironmentSnapshot, ActivationSet, Budget, PolicySet)
```

An episode produces transitions of the form *state → proposal → authorisation → effect → receipt →
observation*. The runtime does not call this "thought"; it is an observable operational trail. Private
reasoning inside a model provider is neither required nor assumed accessible.

**In scope (first two phases):** the coding environment; one deliberately non-coding environment; the
kernel, capability and evaluation machinery; the measurement laboratory.
**Explicitly out of scope:** autonomous operation without an accountable principal; a graphical authoring
surface; multi-model orchestration beyond a port; any mechanism requiring the runtime to modify itself in
place.

### 1.4 Non-claims (`NC-01` … `NC-12`)

| # | Not claimed |
|---|---|
| `NC-01` | AGI, or open-ended discovery of new paradigms |
| `NC-02` | That every syscall passes a mediating layer in the host language — a logical mediator is not a containment boundary |
| `NC-03` | Resistance to a malicious operator, or to a kernel-level exploit. The threat model is untrusted *content*, not an untrusted principal at the console |
| `NC-04` | That the model is trusted. It is treated as potentially adversarial |
| `NC-05` | Semantic truth from passing tests |
| `NC-06` | Determinism from remote models. Reproducibility is by recording and replay |
| `NC-07` | Complete provenance tracking. Best-effort at sub-block granularity; the block label is the enforced unit |
| `NC-08` | Instantaneously exact budget enforcement. Exact at commit; a single in-flight call may overrun and is debited |
| `NC-09` | Cryptographic protection of stored artifacts against an adversary with write access |
| `NC-10` | Autonomous self-update of the policy kernel. Candidate generation permitted; promotion externally gated |
| `NC-11` | Transferable learning, until demonstrated by ablation and holdout |
| `NC-12` | That a shell classifier is a security boundary. It is a parser, and parsers can be parsed around |

### 1.5 Falsifiable claims (`C-01` … `C-12`)

| # | Claim | Falsified by |
|---|---|---|
| `C-01` | Every reference harness is expressible as configuration, no core change | Any reconstruction requiring a loop modification |
| `C-02` | Memory, retrieval, tool protocols, web search and knowledge graphs are registry entries plus configuration | Any of them requiring a core change |
| `C-03` | An adapter's implementation language changes without touching anything above its port | A language swap forcing changes above the port |
| `C-04` | Parallel execution of declared-independent work materially reduces wall-clock | Measured latency parity |
| `C-05` | Operator context isolation improves outcomes on long tasks against a flat agent at equal budget | No measured lift |
| `C-06` | At least one distilled competence artifact beats the unguided baseline, CI excluding zero, above the null-comparison floor | Nothing clearing the floor |
| `C-07` | The policy kernel stays within its stated size ceiling through Phase 2 | Drift |
| `C-08` | Every externally consequential effect is bounded by an enforcement boundary independent of the model | Any effect reaching a resource outside its declared selector under a granted capability |
| `C-09` | A competence artifact survives replacement of the underlying model without re-derivation | Systematic degradation on model change |
| `C-10` | The same core serves a second, non-coding environment with no special cases | Any coding capability inexpressible in the shared competence space |
| `C-11` | A killed process is closed by the recovery controller, with uncertainty preserved where an external effect's occurrence cannot be determined | Any recovery path resolving an undeterminable effect to success or failure |
| `C-12` | An active artifact carries an automatic invalidation condition (`04 [INV-2]`) that fires when it goes stale | Staleness discovered only by human review |

### 1.6 Design axioms (`A-01` … `A-12`)

| # | Axiom | Enforcement |
|---|---|---|
| `A-01` | The episode is the only execution primitive | No workflow engine, topology language, graph validator or node registry exists in the tree |
| `A-02` | Extensions compose by invocation; cognitive operators are data rather than control flow | One composition mechanism; operators are addressable, versioned, replaceable entries |
| `A-03` | Effects are authorised before a capability is issued, and bounded by an enforcement boundary independent of the model | Two classes: broker-mediated effects and in-sandbox effects |
| `A-04` | Content carries provenance on orthogonal axes; provenance constrains authority | Type-level: raw strings cannot enter context assembly |
| `A-05` | The verifier is outside the mutable surface | Reachability test: no capability resolves to a verifier-owned path |
| `A-06` | Emitted effect order is preserved; parallelism requires declared independence | Independence groups or provably disjoint read/write sets over a common snapshot |
| `A-07` | Everything is an event | One durable typed ledger; every surface is a projection of it |
| `A-08` | Configuration is declarative at the agent level, never at the graph level | Adding a capability is a registry entry plus a configuration line |
| `A-09` | Clients are pure consumers; events never schedule work | Architecture test: client modules hold no adapter handles |
| `A-10` | A gate that cannot fail is not a gate — and a requirement that cannot be satisfied is not a requirement | Every fix ships a test proven to fail against pre-fix code; satisfiability checked before a test is written |
| `A-11` | Extensions resolve once at composition, then freeze | No runtime discovery, no dynamic registration |
| `A-12` | Instrument error is not task failure | *Inconclusive* is a first-class verdict, never coerced into failure |

### 1.7 Cross-cutting norms (`N-01` … `N-21`)

| # | Norm |
|---|---|
| `N-01` | The model proposes; the broker authorises; the environment executes; the evaluator evidences |
| `N-02` | A guarantee may not exceed the boundary that actually enforces it |
| `N-03` | Every capability carries principal, action, resource, constraints, purpose and expiry |
| `N-04` | An over-broad request is denied and recorded as an escalation attempt; never silently narrowed |
| `N-05` | Child capabilities are a subset of the parent's; child limits do not exceed the parent's remaining budget |
| `N-06` | Shell is contained by the sandbox; it is not mediated by the host language |
| `N-07` | Control plane, worker, evaluator and updater have distinct identities and surfaces |
| `N-08` | The agent creates candidates; it never alters the live runtime |
| `N-09` | Origin, instruction authority, integrity, confidentiality and epistemic state are distinct axes |
| `N-10` | Only the verifier admits; rankers rank |
| `N-11` | An evaluator produces a scoped claim; no claim is granted abstract objectivity |
| `N-12` | Local success does not promote a generalisation without its own test |
| `N-13` | A claim or artifact that cannot state what would refute it is inadmissible |
| `N-14` | Competence is an immutable graph plus activation views; forgetting removes from the active view and preserves lineage |
| `N-15` | A dead process is closed by the recovery controller, never by fiction inside the dead process |
| `N-16` | Leases release on every path, including creation failure |
| `N-17` | Registries freeze at composition; unknown names fail at composition, not at first use |
| `N-18` | Safety, privacy and authority are hard constraints; performance lives on the frontier |
| `N-19` | Full content capture happens by policy only; the training corpus is separately opt-in |
| `N-20` | Playbooks constrain — masking tools, injecting context, evaluating gates — and never dispatch |
| `N-21` | The brief is immutable and exempt from compaction |

### 1.8 Irreversible locks (`L-1` … `L-6`)

| # | Lock | Why irreversible |
|---|---|---|
| `L-1` | Trajectory, event and competence schemas | This is the corpus format; changing it means re-running everything ever recorded |
| `L-2` | Kernel boundary and TCB partition | Every safety property and the self-improvement argument rest on it |
| `L-3` | Operators as data, not control flow | Determines whether operator-level improvement is reachable at all |
| `L-4` | The improvement relation: hard constraints, then frontier, then activation | Scalar objectives are self-reinforcing through the corpus |
| `L-5` | Verifier exteriority and predicate-scoped evaluator classes | No other mechanism keeps proxy reward at or below zero |
| `L-6` | Seams: subprocess with line-delimited JSON, versioned artifacts on disk | Cross-language contracts outlive the code that produced them |

Genuinely open: the core runtime language; native-addon optimisation; which cognitive operators to build;
discovery-engine sophistication; multi-model orchestration depth; the full metric suite.

### 1.9 Strategic frame and generality constraint

The v4 correction: competence becomes an evidenced graph; permission becomes a scoped capability; the
trajectory becomes transactional storage with projections; the sandbox becomes a real boundary; the
verifier becomes claim-specific; self-editing becomes a release pipeline.

**Dual track, asymmetrically weighted** — roughly 80% coding as the verifiable laboratory, roughly 20%
one deliberately impoverished non-coding environment sharing the same competence space, kernel and
operator registry, governed by a hard constraint:

> **No capability may be added to the coding track that cannot be expressed in the shared competence
> space.** A coding feature needing a special case is capture happening, and is a design defect.

**The strategic exit criterion.** A competence artifact that (a) was not author-written, (b) demonstrably
improves performance on tasks it was not distilled from, (c) survives replacement of the underlying model,
and (d) carries an evidence block that would survive adversarial review by someone trying to show it is
memorisation. If the criterion looks too demanding for the budget, extend the timeline — never weaken it.

### 1.10 Approved stack — decision level

| Area | Decision |
|---|---|
| Control plane | **Python** (`ADR-0063`, 2026-08-16), reversing the original TypeScript-on-Node decision (`ADR-0001`) on evidence. Alternative runtimes stay behind a conformance matrix and soak test |
| Interaction client | TypeScript (strict) on Node.js LTS; also the `ADR-0014` second-language contract reader |
| Wire contracts | JSON Schema 2020-12, normative, with semantic specification and golden vectors |
| Validation | A TypeScript validator as *implementation*, verified against the schemas — never the source of truth |
| Canonicalisation | RFC 8785 / JCS, with conformance vectors |
| Durable store | Embedded transactional store with write-ahead logging, single writer; line-delimited JSON as export/interchange |
| Blob store | Content-addressed on the filesystem, with an encryption hook from the first contract |
| Sandbox | Hardened rootless container for development; stronger isolation by risk tier, reported rather than asserted |
| Evaluator | Separate process and identity, distinct image digest and mounts |
| Laboratory | Python, offline, reading exports; never in the request path |
| Systems seams | Subprocess with line-delimited JSON over standard streams |

### 1.11 Risk register (`RSK-01` … `RSK-15`)

| # | Risk | Mitigation | Severity |
|---|---|---|---|
| `RSK-01` | Verifier compromise | Immutable by construction, sealed execution, unreachable from every capability, adversarial audit before any training run | Critical |
| `RSK-02` | Reward hacking through a weak proxy becoming the objective | Predicate-scoped evaluator classes; proxies rank but never admit; drift monitored against human judgement | Critical |
| `RSK-03` | Memory poisoning | Scoped claim pipeline, per-record provenance, adversarial ablation at activation, automatic demotion | High |
| `RSK-04` | Measurement theatre — vacuous passes, degenerate floors, undeclared families | Instruments that refuse rather than report; every gate proven able to fail | High |
| `RSK-05` | Contamination of holdout or sealed splits | Split discipline, touch ledger, per-instance corpus membership check | High |
| `RSK-06` | Underpowered claims | Sample size derived from the floor, recorded in the family declaration | High |
| `RSK-07` | Capability escalation through resource-blind permissions | Resource-scoped capabilities; explicit denial and an alertable escalation event | High |
| `RSK-08` | Silent self-modification of the live runtime | Candidate generation only; hermetic external build, attestation, signed canary, automatic rollback | High |
| `RSK-09` | Optimiser monoculture | Explicit variance budget against a held-out different set | Medium |
| `RSK-10` | Circular training — the model tunes to this harness | Harness comparisons always use an untuned model | Medium |
| `RSK-11` | Core drift — a workflow engine reinvented under new names | Size budget as a tracked metric with an alert; an ADR per core change | Medium |
| `RSK-12` | Competence ossification | Staleness windows, invalidation conditions, automatic demotion, re-evaluation on model change | Medium |
| `RSK-13` | Calibration collapse — abstention trained out | Abstention as a first-class scored outcome | Medium |
| `RSK-14` | Governance re-accretion | Reinstate weight only when team size makes coordination costly | Low |
| `RSK-15` | Premature generalisation before the coding case pays | Let evidence answer the generality question | Low |

### 1.12 Honest limits

The flywheel is bounded by the evaluator (central unsolved problem). Optimisation does not leap; paradigm
shifts come from humans reading trajectories. Coding is a privileged domain. Reconstructions are
reconstructions. Most measured differences will be noise at achievable sample sizes. Statistical power is
expensive and experiment selection is human. Genuine novelty may not be operationalisable without being
gameable. Credit assignment is unsolved for long runs. Some claims here will fail (`C-06` may never clear
the floor). "AGI" is not a claim this project makes.

---

## 2. Turn Lifecycle, Planes & Execution Model (VG-03)

### 2.1 The execution protocol

Every capability, in every environment, reduces to one protocol:

```
observe → propose → authorise → effect → receipt → evaluate
```

| Step | Who | Constraint |
|---|---|---|
| observe | Environment adapter | Returns a snapshot-bound observation, **never a live handle** |
| propose | Cognitive operator | Produces a proposal; a proposal is not an authorisation |
| authorise | Broker (VG-05) | Issues a scoped capability, or denies and records the attempt |
| effect | Environment adapter, inside the workload perimeter | Bounded by the perimeter, not by the caller's intentions |
| receipt | Environment adapter | Verifiable, idempotency-keyed, reconcilable |
| evaluate | Evaluator, separate identity | Produces a scoped claim, never unscoped truth |

The loop knows how to reduce events, apply budgets, request authorisation and terminate. It does not know
what "planning", "debugging", "abstraction" or "analogy" are — those live in the operator registry, as data.

### 2.2 The inversion: agent loop over workflow DAG

> **The episode loop is at least as expressive as the static topology language rejected, at a small
> fraction of the machinery.** The expressiveness half is proved by construction against static DAG
> topologies. The machinery half is an *estimate* anchored on one measurement (a 501-line graph
> validator). Strict superiority holds under static constraints; dynamic graphs with runtime-generated
> nodes and recursive tasks may express equivalent behaviour but require significantly greater machinery.

Proof by construction — graph node → loop equivalent:

| Graph node | Loop equivalent |
|---|---|
| `retrieve` | Not a node. The agent reads, globs and greps when it decides it needs to |
| `architect` | An operator with read-only capabilities and a planning brief, exposed to its parent as a tool |
| `generate` + `apply` | The parent holding edit capabilities. The environment's own diff is the sole definition of the change |
| `evaluate` | **Not an operator.** A deterministic evaluator the agent may invoke and may never modify |
| `repair` | Does not exist. The agent observes failing output as a result and continues |
| fan-out + join | N branches in isolated snapshots under one task group, ranked by verdict |

**Static topology is a strict subset.** Preserved goals: reproducibility via pinned configuration plus
recorded replay; recording via the event stream; composition at the operator level; visualisation by
rendering the trajectory as a graph *after* the run; enforced methodology via playbooks at `strict`
rigidity. **Graphs are an excellent authoring and visualisation surface and a poor runtime control-flow
substrate.** The authoring canvas is deferred (`DEF-01`); the runtime graph is rejected (`REJ-01`).

### 2.3 The six planes

The load-bearing property is not module separation but **distinct OS identities, mount namespaces and
credential sets**.

```
Interaction  ── CLI · API · Inspector
     │  authenticated requests, event subscriptions
Cognition    ── Episodes · Operators · Activation sets
     │  proposals
Control      ── Broker · Policy · Budget · Secrets
     │  scoped grants
Workload     ── Sandboxed environment adapters
     │  receipts
Evidence     ── Evaluators · Claims · Experiments
     │  candidates
Evolution    ── Build · Attest · Canary · Rollback
     └──────── signed activation pointer ──▶ Cognition
```

| Plane | Holds | Does not hold |
|---|---|---|
| **Interaction** | Clients as pure consumers; approvals carrying identity, scope, expiry and descriptor | Adapter handles; the ability to schedule work |
| **Cognition** | Episode state; operator selection and invocation; proposal construction | Environment credentials, signing keys, direct host access |
| **Control** | Principal authentication; capability and policy validation; budget reservation; secret references; kill switch and revocation | Any cognitive discretion |
| **Workload** | Ephemeral execution with only granted mounts and egress; real containment reporting | Mounts of the control plane, evaluator, secret store or updater |
| **Evidence** | Evaluators under a distinct identity; protocol, dataset split, image digest, provenance. **Owns the evaluation trigger** — observes episode termination in the ledger and emits `EvaluationRequested`. **No episode can request its own evaluation** | Authority to admit anything into the live activation set |
| **Evolution** | Candidate artifacts without operational authority; build, attest, canary, roll back; activation-pointer updates | Write access to live files. It moves pointers, never contents |

Two non-negotiable consequences:
1. **Cognition may fail without compromising the ledger or the evaluator.** Holds fully from Phase 1. In
   Phase 0, Cognition is co-located with Control *and the event store*, so it holds against a crash (the
   store is transactional, the writer is single) and **not** against a compromised cognition plane. The
   evaluator half holds in both phases.
2. **The Evolution plane applies stricter policy to control-plane and policy-kernel candidates than to
   prompts and operators.** The gradient of risk is explicit.

### 2.4 Intra-process layer topology (`LT-1` … `LT-8`)

```
clients/     CLI · inspector · API surface        pure consumers
runtime/     composition root · daemon            wiring, frozen at composition
agency/      loop · context · playbooks           cognition
kernel/      dispatch · policy · governor · grants · evaluator boundary
ports/       interfaces only
domain/      pure types, no I/O
adapters/    implements ports; imported ONLY by runtime/
lab/         offline; consumes exported artifacts only
```

| # | Contract |
|---|---|
| `LT-1` | `domain/` imports nothing from the project |
| `LT-2` | `ports/` imports only `domain/` |
| `LT-3` | `kernel/` imports `domain/` and `ports/`. **Never `adapters/`, never `agency/`** |
| `LT-4` | `agency/` imports `domain/`, `ports/` and kernel interfaces. **Never `adapters/`, never `lab/`** |
| `LT-5` | `adapters/` imports `domain/` and `ports/`. **Never each other** |
| `LT-6` | `runtime/` may import everything. It is the only module that may |
| `LT-7` | `clients/` imports `domain/` and the daemon client. No adapter handles |
| `LT-8` | Nothing imports `lab/`. It is offline and consumes exported files |

`LT-4`'s prohibition on cognition reaching the laboratory is the structural expression of evaluator
exteriority: **a component that can construct its own evaluator is a second judge.**

Standing caution: these contracts prove properties of the *import graph* only. They do not constrain a
subprocess spawned under a granted execution capability; containment is the workload perimeter's job.

### 2.5 Composition — the four extension forms

Everything pluggable is exactly one of four things; a fifth is a design review, not a pull request.

| Form | Answers | Example |
|---|---|---|
| `ObservationSource` | What can be seen? | Repository conventions, retrieved priors, memory recall |
| `CognitiveOperator` | What produces a proposal? | Plan, localise, consolidate, critique |
| `EffectAdapter` | What can act? | File edit, shell, table update, external call |
| `Evaluator` | What produces evidence? | Test-suite runner, invariant checker, human adjudication |

**Operators are data, not control flow.** An operator is a versioned, addressable, content-hashed entry in
the competence graph — a brief, a capability requirement, a budget shape, an output contract — not a
function in the loop. Invocation is the single composition mechanism: an operator exposed to a parent
appears in the parent's catalog as a tool; invoking it spawns a **fresh-context child under attenuated
capabilities**.

| Concern | Rule |
|---|---|
| Return value | Text or a structured payload. **Never a handle, never shared mutable state** |
| Workspace | The parent's snapshot by default; an isolated snapshot when exploring in parallel |
| Failure | A typed failure result, not an exception propagated into the parent's loop |
| Budget | A child lease. Exhaustion returns a result, not a crash |
| Depth | A budget dimension, bounded like any other |
| Events | Child events carry the parent identifier and nest in the inspector |
| Provenance | The returned text is untrusted-derived at minimum |

Three properties follow: recursive composition with no new mechanism; attenuation at the broker rather
than at the absence of a call site; and **context isolation** — a child's exploration never enters the
parent's window, and only the result returns.

**Registries freeze at composition.** All four registries resolve once at the composition root and then
freeze. Unknown names fail at composition, not at first use.

### 2.6 The episode engine

#### 2.6.1 The loop

```ts
while (!episode.terminal) {
  const view     = await stateAssembler.materialize(episode);
  const operator = await operatorPolicy.select(view, activationSet);
  const proposal = await operatorRunner.invoke(operator, view, childBudget());

  await eventStore.append(ProposalProduced(proposal));

  if (proposal.kind === "finish" || proposal.kind === "abstain") {
    episode = reduce(episode, proposal);
    continue;
  }

  const decision = await broker.authorize(toEffectRequest(proposal));
  if (decision.kind !== "grant") {
    episode = reduce(episode, decision);   // denial is an event, not an exception
    continue;
  }

  const receipt = await effectExecutor.execute(decision.grant);
  episode = reduce(episode, receipt);

  if (regroundPolicy.shouldRun(episode)) {
    // Re-grounding is an OBSERVATION EFFECT, not a privileged side channel.
    const obs = await broker.authorize(observationRequest(episode));
    if (obs.kind === "grant") {
      episode = reduce(episode, await environment.observe(freshRequest(), obs.grant));
    }
  }
}
```

Named collaborators: `stateAssembler.materialize`, `operatorPolicy.select`, `operatorRunner.invoke`,
`eventStore.append`, `broker.authorize`, `effectExecutor.execute`, `regroundPolicy.shouldRun`,
`environment.observe`, `reduce`.

*Event emission.* `ProposalProduced` is appended by the loop because proposal production happens
**outside** the dispatch sequence. Grants, denials, budget events, receipts and observations are appended
by the kernel. Emission is **split**: intent durably appended at S8a *before* the effect runs, outcome at
S12 (`05 [K-47]`). Every effect is preceded by a durable append, which is what makes reconciliation of an
interrupted effect possible.

*Evaluation.* No evaluator is invoked in this loop. An episode **terminates**; it does not grade itself.

#### 2.6.2 Terminal states — two separate axes

| Run termination | Evaluation outcome |
|---|---|
| `completed` · `abstained` · `escalated` · `cancelled` · `budget_exhausted` · `instrument_error` · `runtime_error` · `abandoned` | `satisfied` · `unsatisfied` · `partially_satisfied` · `inconclusive` · `invalid_evaluation` |

Collapsing them is how instrument failure silently becomes task failure. A provider rate-limit is
`instrument_error`, never a task verdict. A *wrong but real* answer is `unsatisfied` — the instrument-error
category must not shrink the denominator.

#### 2.6.3 Two distinct retries

| Kind | Owner | Conditions |
|---|---|---|
| Transport retry | Adapter | Transient failure, idempotent operation, bounded count, recorded backoff |
| Cognitive retry | Operator | A new proposal after observing a result |

#### 2.6.4 No-progress detection

Progress is judged over the tuple:

```
(state_digest, proposal_descriptor, receipt_digest, progress_signal)
```

Termination fires when the same transition reappears without a change in state or progress signal, for a
configured limit. Deliberate polling declares an **expected-no-change flag and a deadline**, which exempts it.

#### 2.6.5 Inner-loop invariants

| Invariant | Prevents |
|---|---|
| Every turn is bounded on every budget dimension, and the bound is a **lease** rather than a constant | Unbounded runs and budget theatre |
| A denial names the offending call, not the one after it | Misattributed exhaustion |
| Results are labelled at construction, never at consumption | Provenance laundering |
| Capability-widening is a **classifier output**, never a constant | A hardcoded constant standing in for a defence |
| Leases release on every path, including creation failure | A permanently subtracted ceiling |
| Depth is a budget dimension | Runaway recursion |

### 2.7 Environments and the adapter protocol

```ts
interface EnvironmentAdapter {
  profile():   Promise<EnvironmentProfile>;
  snapshot():  Promise<EnvironmentSnapshot>;
  observe(req: ObservationRequest, grant: CapabilityGrant): Promise<Observation>;
  preview(req: EffectRequest,      grant: CapabilityGrant): Promise<EffectPreview>;
  apply(req:   EffectRequest,      grant: CapabilityGrant): Promise<EffectReceipt>;
  reconcile(receipt: EffectReceipt, grant: CapabilityGrant): Promise<Reconciliation>;
  compensate?(receipt: EffectReceipt, grant: CapabilityGrant): Promise<EffectReceipt>;
  dispose(): Promise<void>;
}
```

**Where a coding-shaped architecture breaks** (assumption → correction): worktree workspace → adapter with
snapshot/transaction/compensation/reconciliation · patch-is-a-diff → receipt, idempotency key, preview,
commit, compensating action · read-only implies commutative → snapshot or version token with explicit
dependencies · tests are truth → composite evidence, calibrated proxies, human gates · files are resources
→ a typed resource taxonomy · shell is universal → per-environment adapters and scoped capabilities · one
operator at a console → principal, resource, context; tenant isolation; audit policy · rollback is a
workspace reset → compensations, approvals, risk tiers · any trajectory is training data → data policy,
redaction, retention, corpus opt-in.

**The two Phase 0 environments.**
- **Git environment.** Snapshot = base commit + working-tree digest; preview = a patch *including new
  files*; apply happens inside an ephemeral worktree; reconcile = status and read-back; compensate discards
  the worktree. Publishing externally is a separate, higher-risk effect.
- **TableWorld**, mandatory in Phase 0. Versioned tables; verbs `select`, `derive`, `update`, `validate`;
  constraints over sums, uniqueness, ranges and reconciliation; **no version control, no shell, no paths as
  a domain concept**; a deterministic evaluator over invariants and expected relations. If adding
  TableWorld requires changing the episode engine, the capability algebra or the event envelope,
  generality is falsified early.

**The frozen atom set.** The coding environment's set — `read`, `write`, `edit`, `glob`, `grep`, `shell` —
is frozen. Within an environment, capability grows by composition, not by more atoms. The **universal**
abstraction is the adapter, not any particular six tools.

| Rule | Rationale |
|---|---|
| No tool receives a filesystem handle, path object or open socket | Bytes reach the workspace only through the mediated path |
| Every tool declares its capability requirement and its **read and write sets** | Routing, attenuation, independence analysis and the ledger all key on them |
| The environment's own diff is *the* definition of what changed | No second patch path |
| A tool may never write into pinned evaluator paths | Enforced at the broker, never in tool code |
| The catalog freezes at composition | A runtime-discovered tool is an unaudited capability |

**Irreversible effects** require: two-phase preview and commit where possible; an idempotency key; a
declared risk tier; approval for externally consequential effects; a verifiable receipt; later
reconciliation; a compensating action where one exists; **and plain text stating so when no rollback
exists** (a specification requirement, not a UX nicety).

### 2.8 Concurrency (`CC-1` … `CC-7`)

| # | Rule |
|---|---|
| `CC-1` | Emitted order is preserved by default |
| `CC-2` | Mutations are barriers |
| `CC-3` | Parallelism requires an explicit **independence group**, or demonstrably disjoint read and write sets |
| `CC-4` | Parallel reads observe the same snapshot |
| `CC-5` | Every branch holds a **child lease and a cancellation scope** |
| `CC-6` | Conflict raises an explicit conflict event — never silent last-write-wins |
| `CC-7` | Mixed batches are never reordered |

`CC-7`: hoisting reads ahead of writes changes the observed value; the justification is a claim about model
intent, not execution semantics. **Commutativity is a property of the resource, not the verb.** At Phase 0,
the model adapter may form independence groups only when the provider declares parallel calls and all of
them are reads against the same snapshot.

**Structured concurrency requirements:** task groups with automatic cancellation propagation; every branch
holds a child lease of the parent; cancellation is cooperative and **reaches subprocesses** (kills the
process group); per-branch workspaces destroyed in a `finally`; events carry a branch identifier.

**Parallel exploration.** N branches in isolated snapshots under one task group and one parent lease; each
evaluated; a ranker orders them; **only the activation policy admits a branch into use**. Two distinct
admissions must not be confused: the verifier admits *evidence* (`06 [V-02]`); the activation policy admits
*an artifact into the active set*.

### 2.9 Abnormal termination and recovery

A killed process emits nothing. Any requirement that a dying process emit a terminal event is satisfiable
only against a graceful-shutdown mock.

| Element | Behaviour |
|---|---|
| Run lease | Every active episode holds a lease with an expiry |
| Heartbeat | The worker renews while alive |
| Recovery scanner | Detects expired leases independently of the dead process |
| Recovery controller | Emits the terminal record — recovered or aborted — **from outside** the failed process |
| Effect reconciliation | In-flight effects reconciled by **idempotency key** through the adapter |
| Preserved uncertainty | Where an external effect's occurrence cannot be determined, the record says so |

An implementation that resolves an undeterminable external effect to either success or failure has
manufactured evidence, and `C-11` is falsified.

### 2.10 Context engineering

#### 2.10.1 The layer model

```
L1  SYSTEM      role + output contract         stable across the entire run
L2  TOOLS       tool schemas                   stable; rides on the request
L3  ENVIRONMENT conventions, retrieved priors  stable within a task
L4  TASK        the brief, the plan            stable within a task
L5  DIALOGUE    turns, results, notes          mutates every turn
```

Rendered in order, one message per non-empty layer, every block tagged with its producing source and its
provenance label.

#### 2.10.2 Cache boundaries

| Rule | Rationale |
|---|---|
| A small fixed ceiling on breakpoints | Provider limit |
| Breakpoints only at **L1, L3 and L4** boundaries | These layers do not mutate within a run |
| **L5 never carries a breakpoint** | It is the only layer permitted to mutate |
| Exceeding the ceiling raises **at assembly** | Never discovered afterwards from cache-hit telemetry |
| Prefix stability is a monitored CI metric over a fixed replay | A metric without a replay to run over is an intention |

**Corollary:** anything appended to L1–L4 mid-run destroys every downstream cache hit. Mid-run additions go
to L5, always.

#### 2.10.3 Compaction strategies (pluggable and comparable)

| Strategy | Mechanism | Loss profile |
|---|---|---|
| `recency_window` | Keep the last N exchanges | Drops the load-bearing early decision |
| `result_eviction` | Keep that a file was read; drop the body once superseded | Low. Usually the correct first move |
| `model_summarize` | A child summarises the middle | Prose loses structure |
| `structured_consolidate` | A child emits a structured record | Lowest measured; **the recommended default** |
| `operator_isolation` | Never admit exploration to the parent context | **Bounded** at the return contract — raw exploration retained in child trajectory, summary loss measurable |

**The cheapest way to keep a context window clean is never to put the exploration in it.** Isolation is
primary; compaction handles the remainder.

#### 2.10.4 Structured consolidation

```ts
interface StructuredRecord {
  decisions:  { what, why, alternativesRejected, confidence }[];
  invariants: { claim, evidenceRef, verifiedAt }[];
  open:       { question, blockedOn }[];
  artifacts:  { path, role, lastVerifiedState }[];
  deadEnds:   { approach, whyAbandoned }[];
}
```

Consolidation quality is measurable: replace the full transcript with the record, re-run, compare outcomes.

#### 2.10.5 Long-horizon invariants

| Failure | Mechanism |
|---|---|
| Compaction drops the load-bearing detail | Structured consolidation with a schema declaring what may not be dropped |
| Error compounds silently | **Periodic re-grounding** — re-verify assumptions against actual environment state, not accumulated notes |
| Goal drift | The brief is **immutable**, sits in L4, is cheap to re-read, and is **exempt from compaction** (`N-21`) |

### 2.11 Playbooks: methodology as data

#### 2.11.1 The rigidity dial

| Rigidity | Semantics | Use |
|---|---|---|
| `advisory` | Injected as guidance; the agent may ignore it | Novel, exploratory, ill-specified work |
| `guided` | Phases enforced in order; behaviour *within* a phase is the agent's free loop. Skipping requires a recorded justification | The common case |
| `strict` | Phases gated; the agent cannot leave a phase until its gate passes | Known problem classes, compliance, production hotfix |

**At `strict`, a playbook is a graph** — the full procedural capability recovered as a parameter on a data
artifact, not as the architecture of the runtime.

#### 2.11.2 Three levers, and no fourth

A playbook **constrains; it never dispatches** (`N-20`).

| Lever | Mechanism |
|---|---|
| Tool masking | The current phase narrows the offered catalog, through the same attenuation as everything else |
| Context injection | Phase intent enters as an **L5 note** — never L1–L4 mid-run |
| Gate evaluation | On phase exit: `strict` appends the failure and remains in-phase; `guided` advances, recording the skip and its justification; `advisory` has no gate |

The playbook never calls a tool, never selects a model and never writes to the workspace.

#### 2.11.3 Earned, not authored

Playbooks are distilled from verified episodes, evaluated against both the unguided baseline **and** the
incumbent, promoted only under the improvement relation, and demoted automatically on decay. Every playbook
carries an evidence block and its invalidation conditions.

### 2.12 Process topology, seams and performance

**Three processes at Phase 0, not five:** controller with broker (one process, distinct modules, an audited
internal boundary), worker, and evaluator — each with its own OS identity, mount namespace and credential set.

| Plane | Phase 0 | Phase 1 |
|---|---|---|
| Interaction · Cognition · Control | One process; module boundary, audited | Split; distinct identities |
| Workload | Separate process, identity, namespace, perimeter | Hardened perimeter |
| Evidence | Separate process, identity, image digest | Unchanged |
| Evolution | **No runtime component.** Human-operated | Release controller as a distinct identity |

| Seam | Mechanism |
|---|---|
| Daemon ↔ clients | Structured RPC over a local transport |
| Daemon ↔ systems components | **Subprocess with line-delimited JSON over standard streams** (the preferred default) |
| Daemon ↔ laboratory | Versioned exported artifacts on disk |

**Daemon, not a CLI with a UI bolted on.**

Performance levers, by expected magnitude: prompt caching via a stable L1–L4 prefix (largest single cost
lever; vendor-reported reductions roughly **50–90%** on multi-turn work, **unverified here**); parallel
independent reads (largest latency lever); model tier routing; operator isolation; result eviction.
**The named anti-pattern:** optimising orchestration — under **five milliseconds** against **two to thirty
seconds** of model latency and up to **two minutes** of test execution.

### 2.13 The transparency surface

The trajectory is the substrate, so the inspector is a **view over data already emitted**.

| Surface | Content |
|---|---|
| Layered prompt | L1–L5 with per-block source attribution and exact cache-breakpoint positions |
| Provenance colouring | Every span rendered by label |
| Per turn | Request, reply, effects, results, cost from the ledger, latency, cache-hit rate |
| Decisions | Which playbook and on what evidence; which policy rule granted or denied; where a budget bit; why a phase advanced |
| Parallel branches | Branches side by side with per-branch verdicts |
| Memory | What was recalled, from where, at what score, and **whether it changed the outcome** |
| Replay | Deterministic re-execution from recordings |

**Constraint:** the inspector is a pure consumer, holds no adapter handles and never schedules work,
enforced by architecture test (`AT-03`).

### 2.14 Failure taxonomy (`FT-01` … `FT-17`)

| Class | Manifestation | Mechanism |
|---|---|---|
| `FT-01` Instrument error | Provider rate limit, socket reset, unbuildable image | Inconclusive outcome, excluded from resolve rate, per-branch rate reported |
| `FT-02` Livelock | Repeating transitions without progress | Progress-tuple detection |
| `FT-03` Budget exhaustion | Any dimension | Typed denial naming the offending call |
| `FT-04` Lease leak | An effect raising while holding a lease | Adapter resolved before reservation; release in `finally` |
| `FT-05` Grant staleness | A resumed run with a mutated request | Digest-bound expiring grant, verified at the effect |
| `FT-06` Prompt injection | Untrusted content steering a capability widening | Authority constraints and intent binding |
| `FT-07` Judge tampering | A candidate editing its evaluator | Unreachability plus the double probe |
| `FT-08` Second patch path | Two definitions of what changed | The environment's diff is the only one |
| `FT-09` Second judge | A ranker admitting | Only the activation policy admits |
| `FT-10` Decorative switch | A flag that reads as enabled and changes nothing | Single-object configuration; disconnection tests |
| `FT-11` Goal drift | Optimising the summary rather than the brief | Immutable, compaction-exempt brief |
| `FT-12` Context collapse | A load-bearing early decision compacted away | Structured consolidation; dead-end records |
| `FT-13` Cache thrash | Mid-run mutation of L1–L4 | Assembly-time breakpoint check |
| `FT-14` Orphaned concurrency | A failed branch leaving siblings or subprocesses | Task groups with cancellation reaching process groups |
| `FT-15` Silent recovery fiction | An undeterminable external effect resolved to success or failure | Preserved uncertainty |
| `FT-16` Conflict swallowing | Concurrent branches racing on one resource | Explicit conflict event; never last-write-wins |
| `FT-17` Escalation blindness | Repeated over-broad capability requests unnoticed | Denial recorded as an alertable event |

---

## 3. Core Contracts & Wire Schema (VG-04)

> **This is the corpus format: the set of decisions that, if wrong, must be paid for by re-running
> everything ever recorded.**

### 3.1 Source of truth and wire conventions (`CT-01` … `CT-13`)

**JSON Schema 2020-12 is normative.** Artifacts live in `schemas/v4/`, accompanied by a semantic
specification (invariants that are not structural) and golden vectors covering canonicalisation, codecs,
errors and cross-language agreement. A TypeScript validator is an **implementation** of those schemas,
verified against them, and generates the TypeScript types. It is never the interface definition.

| # | Rule |
|---|---|
| `CT-01` | JSON Schema 2020-12 is normative; validators in any language are implementations verified against it |
| `CT-02` | Types are **derived** from schemas, never hand-written alongside them |
| `CT-03` | Anything crossing a process boundary is **parsed**. A cast on external data is a lint error |
| `CT-04` | JSON only; every type round-trips without loss |
| `CT-05` | No `undefined` on the wire. Optional fields are omitted or explicitly `null` |
| `CT-06` | No floating point for money. Currency is **integer micro-units** |
| `CT-07` | No floating point for durations. **Integer milliseconds** |
| `CT-08` | Timestamps are **RFC 3339 UTC strings with millisecond precision** |
| `CT-09` | Digests are `sha256:` plus **64 lowercase hex characters** |
| `CT-10` | Enums are string literals, never integers |
| `CT-11` | **Readers preserve unknown fields; writers emit only known schema** |
| `CT-12` | Arrays are never sparse; maps are objects with string keys |
| `CT-13` | UTF-8 throughout; no lone surrogates |

**Canonicalisation: RFC 8785 / JCS, without local variation.** Canonical form is the input to every digest
and every descriptor. A descriptor computed differently in one language than another breaks loop detection
and policy caching **silently**.

**Large integers.** Any field that may exceed 2⁵³−1 is a decimal string, not a JSON number:

```ts
const IntString = /^(0|[1-9][0-9]*)$/;   // wire form
```

**Naming.** Types `PascalCase`, fields `camelCase`, enum members `snake_case` string literals. **Every
event type name is a past-tense verb phrase** — `ProposalProduced`, never `ProduceProposal`.

### 3.2 Primitives and branded identifiers (`CT-14` … `CT-16`)

```
Timestamp     RFC 3339 UTC, millisecond precision
Digest        sha256:<64 hex>
UsdMicros     IntString
Millis        integer
SchemaVersion "vg.4"

EventId       UUIDv7          ordering aid, not causal order
RunId · EpisodeId · BranchId · TaskId · ArtifactId · ClaimId
GrantId · LeaseId · ApprovalId · CandidateId · ToolCallId
PrincipalId · TenantId · OwnerId · EvaluatorId
```

| # | Rule |
|---|---|
| `CT-14` | `EventId` is a UUIDv7. It aids indexing and **does not** replace causal order, carried by the `seq` field |
| `CT-15` | `ToolCallId` is provider-assigned and echoed verbatim. Never regenerated, normalised or trimmed |
| `CT-16` | `TenantId`, `OwnerId` and `PrincipalId` exist from the **first** schema version |

### 3.3 Content addressing and blobs (`CT-17` … `CT-20`)

| # | Rule |
|---|---|
| `CT-17` | A blob is immutable and addressed by the digest of its bytes |
| `CT-18` | An event and its blob references commit **atomically**, or through staging with reconciliation. Never separately |
| `CT-19` | Every blob reference carries a **classification**, and the store exposes an **encryption hook keyed by classification** from the first contract |
| `CT-20` | Digests give integrity against corruption and accidental substitution; not a defence against an adversary with write access |

### 3.4 Provenance — six orthogonal axes (`CT-21` … `CT-23`)

| Axis | Question |
|---|---|
| `origin` | Where did this content come from? |
| `instructionAuthority` | May it direct behaviour, or only inform it? |
| `integrity` | How strongly is its content attested? |
| `confidentiality` | Who may see it? |
| `epistemic` | How well established is it as a belief? |
| `influence` | What did it plausibly contribute to? |

| # | Rule |
|---|---|
| `CT-21` | A raw string cannot enter context assembly. **Provenance laundering by concatenation is impossible by type signature** |
| `CT-22` | Results are labelled **at construction**, never at consumption |
| `CT-23` | Labels are declared **once per source class**, so a new call site cannot introduce an unlabelled path |

Provenance **does not establish causation**. For sensitive effects the mechanism is **intent binding**: the
effect is bound to a brief, a purpose digest and an approval, rather than inferred from attention.

### 3.5 Context blocks and epistemic state

A **context block** is the unit of assembly: content, its source class, its provenance axes, its layer
assignment, and its epistemic state.

The `epistemic` axis carries its own ordered lattice — `observed`, `derived`, `hypothesised`,
`corroborated`, `contradicted`, `retracted` — one axis among six, ordered where the others are categorical.

`influence` is the only axis that is **best-effort and non-enforcing**. No authorisation decision reads it.

### 3.6 Capabilities and effect descriptors

#### 3.6.1 Why a verb set is insufficient

A permission set over verbs is a **verb lattice**. It cannot express "read only this repository", "write
only this branch", "egress only to this endpoint", or "use this secret without disclosing its value".
Under verb-only attenuation a "read-only" child can read the evaluator bundle, the policy configuration and
the operator's private keys. Every serious authorisation system models `(principal, action, resource,
context)`.

#### 3.6.2 The grant

```ts
type ResourceSelector =
  | { kind: "fs";      root: ResourceUri; paths: string[] }
  | { kind: "network"; hosts: string[]; ports: number[] }
  | { kind: "secret";  refs: SecretRef[]; discloseToModel: false }
  | { kind: "git";     repo: ResourceUri; refs: string[] }
  | { kind: "table";   table: ResourceUri; ranges?: string[] }
  | { kind: "browser"; origin: string; accountRef?: string }
  | { kind: "generic"; uriPattern: string };

type CapabilityGrant = {
  id: GrantId;
  principal: PrincipalId;
  descriptorDigest: Digest;        // REQUIRED — the one call this grant authorises
  actions: ActionId[];
  resources: ResourceSelector[];
  constraints: {
    expiresAt: Timestamp;
    maxUses: IntString;
    maxBytes?: IntString;
    maxEffects?: IntString;
    budgetLeaseId: LeaseId;
    environmentSnapshot?: Digest;
    networkPolicy?: "deny" | "allowlist";
    requirePreview?: boolean;
    requireApprovalAboveRisk?: RiskTier;
  };
  purposeDigest: Digest;
  parentGrantId?: GrantId;
  approvalRef?: ApprovalId;
  authenticator?: MacOrSignature;
};
```

> **`CT-51` — a grant authorises one call, not a class of calls.** `descriptorDigest` is the digest of the
> normalised effect descriptor, computed at **S3** and verified at **S8**. It is **not** `purposeDigest`:
> purpose is the brief the effect serves; descriptor is the exact call. Without this field the
> point-of-effect verification in `05 [K-18]` has nothing to compare and `F-14` is untestable.

`discloseToModel: false` is typed as a **literal**, not a boolean: a secret reference that could be
disclosed to the model is a different type, and no code path flips the flag.

#### 3.6.3 Attenuation rules (`CT-24` … `CT-28`)

A child grant is valid only when actions are a subset, resources are a subset, and constraints never
increase time, uses, bytes, budget, risk or resource surface.

| # | Rule |
|---|---|
| `CT-24` | An out-of-scope request is **denied**; the denial records both what was requested and what was grantable |
| `CT-25` | **There is no silent intersection.** Narrowing an over-broad request without saying so destroys the highest-value intrusion signal available |
| `CT-26` | A grant crossing a process boundary is authenticated by a MAC or signature. An in-process grant may be an opaque reference |
| `CT-27` | A grant is **single-use** when the effect has no safe idempotency key |
| `CT-28` | Long operations renew lease and grant explicitly. **There is no universal fixed TTL** |

#### 3.6.4 Selector inclusion (`CT-52`)

"Resources are a subset" is undecidable without a per-kind relation. **A selector pair with no defined
relation is denied, never intersected.**

| Kind | Child ⊆ Parent when |
|---|---|
| `fs` | Same `root`, and every child path is a normalised (`D-2`) prefix-match under some parent path. **No globs in a grant — expand at issuance** |
| `network` | Child hosts a subset after lowercasing and IDNA normalisation; a parent wildcard `*.example.com` contains a child label but **never another wildcard**; ports a numeric subset |
| `secret` | Child refs a **literal** subset. `discloseToModel` is `false` on both by type |
| `git` | Same `repo`; child refs a subset of parent refs after **full-ref expansion**. No pattern refs |
| `table` | Same `table`; child ranges contained by parent ranges under interval containment on normalised coordinates |
| `browser` | **Exact origin equality** — scheme, host and port. No subdomain or path containment |
| `generic` | **Literal equality of `uriPattern` only.** Pattern-versus-pattern containment is undecidable in general |

> **`CT-52`.** Inclusion is decidable, total on the pairs above, and denies everything else — including any
> cross-kind comparison. A checker that returns "unknown" must **fail closed** and emit
> `AuthorizationDenied{scope_escalation}`.

#### 3.6.5 Execution capabilities

Granting subprocess execution grants execution **inside an already-limited environment**. It does not imply
that anything intercepts syscalls. The receipt records what actually bounded the effect: image or root
filesystem digest; normalised argument vector and working directory; environment variable **keys, never
secret values**; mounts; network policy; resource limits; redacted output references; exit/cancellation/
timeout; and the containment runtime in force.

#### 3.6.6 The effect descriptor and normalisation (`D-1` … `D-6`)

The descriptor serves three consumers: loop detection compares consecutive descriptors; policy caching keys
on it; a grant binds one and it is verified at the point of effect.

| # | Rule | Rationale |
|---|---|---|
| `D-1` | Object keys sorted per canonical JSON | Key order is not semantic |
| `D-2` | Path arguments resolved against the workspace root, relative segments collapsed, no trailing slash, forward slashes always | Two spellings of one path are the same call |
| `D-3` | **The provider-assigned call identifier is excluded** | It differs between otherwise identical calls |
| `D-4` | String arguments are **not** trimmed or case-folded | Whitespace is semantic in commands and in file content |
| `D-5` | Absent optional arguments omitted, never `null` | Presence with a null value must not differ from absence |
| `D-6` | Numbers canonicalised to shortest round-trip form | Cross-language formatting differs |

> **`D-3` is the rule that gets forgotten**, and its failure is invisible: include the provider-assigned
> identifier and every descriptor is unique, loop detection never fires, and the symptom presents as *"the
> agent got stuck"*.

### 3.7 Budgets, reservations and leases (`CT-29` … `CT-32`)

A budget is a **vector** — cost, tokens, wall-clock, turns, depth, concurrency — and a bound is a **lease**,
not a constant. A lease is reserved before an effect, committed at its receipt, and released on every path
including creation failure.

**`EvaluationBudget` is a sibling dimension**, covering evaluator compute, wall-clock and human adjudication
time. Under best-of-N with per-branch verification, evaluation compute routinely exceeds generation compute.

| # | Rule |
|---|---|
| `CT-29` | Every reservation carries its **lease identifier** into the effect and into the receipt |
| `CT-30` | A denial names the offending call, not the following one |
| `CT-31` | Enforcement is **exact at commit, not instantaneous**. A single in-flight call may overrun; the overrun is debited and the ceiling moves |
| `CT-32` | Evaluation and human-adjudication time are **budgeted dimensions**, not untracked overhead |

### 3.8 Tools

A tool declares its **name**, its **required capability**, its **argument schema**, and its **read set and
write set**. **There is no commutativity flag** — commutativity is a property of the resource, not the verb.
Independence for parallel execution is established either by an explicit independence group or by
demonstrably disjoint read/write sets over a common snapshot.

### 3.9 The model interface (`CT-33` … `CT-34`)

The wire shape for tool-calling: an assistant message carrying the tool calls **must** precede the results,
and each result **must** carry the call identifier it answers.

| # | Rule |
|---|---|
| `CT-33` | A provider adapter **never throws** for a provider-side failure. It returns a reply marked as **instrument error** with an error kind |
| `CT-34` | Throwing is reserved for **programmer error**, such as a malformed request |

> **The generalisable lesson.** A mock built by reading your own consumer code proves the harness is
> *self-consistent*; it cannot prove the harness agrees with a real endpoint.

### 3.10 Task, plan, proposal, effect request

Four separate types, from the first schema version:

| Type | Is |
|---|---|
| `TaskSpec` | What is being asked, with its acceptance conditions |
| `PlanArtifact` | A proposed approach, evaluable **without executing any effect** |
| `Proposal` | What an operator produced this turn |
| `EffectRequest` | What is submitted to the broker for authorisation |

Plus: explicit hypothesis, evidence, decision and stop states; branch and fork parentage; plan evaluators
that execute no effects; role-specific capability grants; and a trajectory that records **which operator
produced which proposal** (the basis of credit assignment).

An operator receives **no effect capabilities by default**. If it must observe the environment it receives a
scoped read-only grant. Mutating effects remain proposals to the broker, always.

### 3.11 The competence and evidence graph

#### 3.11.1 Why a graph

An array cannot express contradiction between entries, partial supersession, per-domain activation,
quarantine, or lineage-preserving forgetting. Artifacts are classified into four quadrants —
**representations, operators, methods, primitives** — which survive as a **typed projection** of the graph.

> A recalled fact is not automatically a representation. It is first a claim in the evidence graph.

#### 3.11.2 The contracts

```ts
type CompetenceArtifact = {
  id: ArtifactId;
  kind: "R" | "O" | "M" | "P";
  artifactVersion: SemVer;
  body: BlobRef;
  interfaceSchema: SchemaRef;
  createdBy: PrincipalId;
  createdFrom: ArtifactId[];
  dependencies: ArtifactRequirement[];
  supersedes: ArtifactId[];
  contentDigest: Digest;
  createdAt: Timestamp;
  invalidationConditions: InvalidationCondition[];   // .min(1), REQUIRED
};

type EvidenceClaim = {
  id: ClaimId;
  subject: ArtifactId | RunId | CandidateId;
  predicate: ClaimPredicate;
  value: ClaimValue;
  protocol: ProtocolRef;
  evaluator: EvaluatorRef;
  environmentProfile: Digest;
  substrateProfile: Digest;
  taskDistribution: ManifestRef;
  uncertainty: Uncertainty;
  validity: ValidityDomain;
  evidenceRefs: BlobRef[];
  derivedFrom: ClaimId[];
  contradicts: ClaimId[];
  expiresAt?: Timestamp;
  invalidationConditions: InvalidationCondition[];   // .min(1), REQUIRED
};
```

**Typed edges:** `derived_from`, `requires`, `supersedes`, `contradicts`, `evaluated_by`, `valid_under`.
**States:** `candidate`, `active`, `quarantined`, `deprecated`, `retired`.

Optional hedge fields on `EvidenceClaim` (`ADR-0068`): `supportCount`, `lastCorroboratedAt`,
`protectionClass`. Named by the writer schema; defaults omit them so historical canonical bytes hold. They
are **recorded, not consumed** — they must not move staleness or validity.

#### 3.11.3 Invalidation conditions (`INV-1`, `INV-2`)

```ts
type InvalidationCondition = {
  condition: string;                    // machine-checkable where possible
  checkKind: "automatic" | "scheduled" | "manual";
  checkRef?: EvaluatorRef;              // required when checkKind is automatic
};

// Check state is MUTABLE and therefore lives outside the content-addressed artifact.
type InvalidationCheckRecord = {
  artifact: ArtifactId | ClaimId;
  conditionIndex: number;
  lastChecked: Timestamp;
  outcome: "holds" | "violated" | "inconclusive";
};
```

> **`INV-1`.** A claim or artifact that cannot state what would refute it is **not admissible**. An empty
> array fails validation **at parse time**.
>
> **`INV-2`.** An artifact promoted to `active` carries **at least one** condition with
> `checkKind: "automatic"`. Candidate and quarantined artifacts may carry only scheduled or manual
> conditions.

The greatest risk is not forgetting true knowledge; it is **generalising true knowledge beyond the domain
where it was proven**. A validity domain records where a claim held; invalidation conditions record what
would show it no longer holds.

#### 3.11.4 Lifecycle rules (`CT-35` … `CT-39`, `CT-53`)

| # | Rule |
|---|---|
| `CT-35` | Artifacts are **immutable**. Status and activation live in separate records |
| `CT-36` | `retired` removes from the activation set; it never deletes lineage |
| `CT-37` | `quarantined` blocks automatic selection |
| `CT-38` | Expired evidence is not deleted; it loses eligibility |
| `CT-39` | A new version never alters the evidence attached to its predecessor |
| `CT-53` | **No mutable field appears inside a content-addressed artifact.** Check state, status and activation live in separate keyed records |

### 3.12 The instrument tuple (shape)

The tuple identifying a measurement context — schema version, environment profile, substrate profile,
evaluator identity and protocol, dataset split, task manifest — travels with every claim. Its shape is fixed
here so that a cross-version comparison is representable as a **tuple delta** rather than an undetected
apples-to-oranges comparison. Composition and use are owned by VG-07 §5.

### 3.13 The event stream

#### 3.13.1 The envelope

```ts
type EventEnvelope = {
  schemaVersion: SchemaVersion;
  eventId: UUIDv7;
  scope: "episode" | "governance" | "evolution" | "recovery";
  runId?: RunId;               // REQUIRED iff scope is episode or recovery
  episodeId?: EpisodeId;       // REQUIRED iff scope is episode
  branchId?: BranchId;
  parentEventId?: UUIDv7;
  traceId: TraceId;
  spanId: SpanId;
  seq: IntString;              // canonical order within a run, writer-allocated
  occurredAt: Timestamp;
  recordedAt: Timestamp;
  principal: PrincipalId;
  tenantId: TenantId;
  ownerId: OwnerId;
  confidentiality: ConfidentialityLabel;
  retentionClass: RetentionClass;
  trainability: TrainabilityLabel;
  redactionStatus: RedactionStatus;
  encryptionKeyRef?: KeyRef;
  environmentSnapshot?: Digest;
  payload: TypedEvent;
};
```

The `scope` discriminator exists because approvals, candidate attestations, canary promotions and rollbacks
occur **outside any episode**. Forcing a synthetic run identifier onto them would put fiction in the ledger.

Tenancy and data-policy fields are not optional and not deferred. They support **four projections** a single
stream must serve: encrypted raw audit, redacted operational trace, content-free metrics, and training
examples **only** after a separate corpus opt-in.

#### 3.13.2 The minimum event set

| Group | Events |
|---|---|
| Episode lifecycle | `EpisodeStarted`, `EpisodeStateChanged`, `EpisodeCompleted` |
| Observation & cognition | `ObservationRequested`, `ObservationProduced`, `OperatorSelected`, `OperatorInvoked`, `ProposalProduced` |
| Authorisation | `AuthorizationRequested`, `CapabilityGranted`, **`AuthorizationDenied`**, `CapabilityRevoked` |
| Budget | `BudgetReserved`, `BudgetCommitted`, `BudgetReleased` |
| Effects | `EffectPreviewed`, **`EffectStarted`**, `EffectCompleted`, `EffectReconciled`, `ConflictDetected` |
| Evidence | `EvaluationRequested`, `EvidenceClaimProduced` |
| Competence | `ArtifactCreated`, `ActivationChanged`, `CompetencePriorRecorded` |
| Human | `ApprovalRequested`, `ApprovalResolved` |
| Liveness & recovery | `Heartbeat`, `RunRecovered`, `RunAborted` |
| Evolution | `CandidateBuilt`, `CandidateAttested`, `CanaryPromoted`, `RollbackTriggered` |

- `AuthorizationDenied` carries the reason, what was requested and what was grantable. **Scope escalation is
  a first-class, alertable signal.**
- `CompetencePriorRecorded` carries a **pre-action** prior `P(success | task)` and the **digest of the exact
  context vector** it was a prior for. Emitted before the first turn reaches the provider.
- `ConflictDetected` discharges `CC-6`. `CapabilityRevoked` discharges the Control plane's revocation and
  kill-switch authority.

#### 3.13.3 Storage (`CT-40` … `CT-43`)

| # | Rule |
|---|---|
| `CT-40` | An embedded transactional store with **write-ahead logging**, fully synchronous on the critical ledger, **single writer** |
| `CT-41` | Versioned migrations; blobs addressed by digest **outside** the database |
| `CT-42` | Line-delimited JSON is **export, replay and interchange** — never the primary store |
| `CT-43` | The inspector reads **through a port**, never a partially written file |

Append-only files as primary store fail on four counts: no atomic multi-record commit, torn writes on crash,
no safe concurrent read during write, and no indices.

#### 3.13.4 Recovery events

`Heartbeat`, `RunRecovered` and `RunAborted` exist so termination can be recorded **from outside** the
failed process. `EffectReconciled` carries a **preserved-uncertainty** state for external effects whose
occurrence cannot be determined.

### 3.14 Port interfaces (VG-04 §13)

Ports import **domain types only**. Adapters implement them and are imported only by the composition root.

| Port | Responsibility |
|---|---|
| `ModelProvider` | Inference; returns instrument errors rather than throwing (`CT-33`) |
| `EnvironmentAdapter` | The universal environment protocol (VG-03 §7.1) |
| `OperatorRunner` | Invokes a versioned operator under a child budget |
| `EvaluatorPort` | Produces scoped claims; runs under a separate identity |
| `EventStore` | Append and read the durable ledger |
| `BlobStore` | Content-addressed bytes with a classification-keyed encryption hook |
| `ObservationSource` | Supplies labelled context blocks |
| `PolicyEngine` | **Decides; does not execute** |
| `Governor` | Budget reservation, commitment, release |
| `SandboxRunner` | Executes within a perimeter and returns a **containment report** |

`SandboxRunner` returns a structured report, not a boolean. The report states runtime, namespace
configuration, profiles, network enforcement, writable mounts, exposed sockets, resource limits, startup
probes and attestation time.

### 3.15 Configuration schemas

Configuration is **authored**, so its rules differ from wire rules: **unknown fields are rejected at
authoring time**, names resolve at composition, and a name that does not resolve fails the composition
rather than the first use. Agent, harness, operator and playbook definitions are all configuration and all
freeze at composition.

### 3.16 Cross-language contract

Two implementations at the first lock: **TypeScript and Python**. Vectors are written **as data** at that
lock. A third language is added when a third consumer exists.

Frames between processes carry: a maximum size, a request identifier, version negotiation, a cancellation
frame, backpressure, diagnostics on a separate channel, explicit content references for large payloads, and
an authenticated channel wherever grants cross a process boundary.

### 3.17 Versioning and compatibility (`CT-44` … `CT-50`)

| Class | Definition | Action |
|---|---|---|
| Additive | New optional field with a default; new event kind; new enum member in a non-exhaustively matched position | None |
| Compatible-breaking | Field made required; default changed; enum member removed; semantics changed | Minor bump plus migration |
| Incompatible | Field removed or retyped; event removed; envelope changed | **Major bump plus corpus re-derivation** |

| # | Rule |
|---|---|
| `CT-44` | Readers handle an **unknown event kind** by preserving it and continuing |
| `CT-45` | Consumers do not exhaustively match on extensible enums without a default |
| `CT-46` | Every version bump ships a migration, **even a no-op one** |
| `CT-47` | **Every version bump runs a migration rehearsal in CI** against a synthetic corpus |
| `CT-48` | A corpus records the schema version it was derived under; valid only against readers of that version |
| `CT-49` | Event kinds are **never removed from history** |
| `CT-50` | A field is deprecated for at least one minor version before removal: marked, warned on write, still accepted on read |

### 3.18 Conformance

| Kind | Establishes |
|---|---|
| Vector conformance | Two implementations agree on parse, reject, canonical form and digest |
| Property tests | Algebraic laws hold — attenuation narrows, descriptors are stable, order is preserved |
| Round-trip tests | Unknown-field preservation and version tolerance |
| Must-fail tests | Each control can actually fail |

**A vector is never edited to make an implementation pass.**

### 3.19 What locks here

VG-04 carries **three of the six irreversible decisions**: the corpus format (§1, §10, §12), the wire
interface definition (§0), and the seams (§15).

> **Operational rule with no exceptions:** a schema marked `DRAFT` in `schemas/v4/MANIFEST.md` may not be
> used to record anything intended to survive. (`SC-10` writer/reader profile split; `SC-12` — no schema
> locks while any VG-04 type lacks an artifact.)

---

## 4. Policy Kernel, Capability Attenuation & Security Model (VG-05)

> **Standing exception.** Compression applies everywhere in the corpus except here. Nothing in VG-05 is
> shortened to meet a budget.

### 4.1 Audit stance

> **`K-01`.** **A guarantee may not exceed the boundary that actually enforces it.**

A logical mediator in the host language is not a containment boundary. A parser is not a perimeter. A policy
enforced by human attention is not a mechanism.

**Assurance method — four independent kinds, none substituting for another:**
1. **Architecture tests** proving paths do not exist (§4.13).
2. **Must-fail tests** proving each control can fail (VG-08 §5).
3. **Fault injection** against the recovery paths.
4. **Adversarial audit of the verifier** by someone who did not write it, **mandatory before any training run**.

### 4.2 The trusted computing base

**The auditable size ceiling applies to the *policy kernel*** — dispatch, policy evaluation, grant issuance
and verification, attenuation, the governor, and the provenance predicate.

**It does not apply to the TCB**, which is larger and must be **declared rather than hidden**: operating-system
kernel or hypervisor; container or micro-VM runtime; the supervisor; the policy configuration and its parser;
the secret broker; the ledger and event store; the build and release controller; the evaluator runtime and its
images; every transitive dependency loaded into a privileged process; and the identity, key and signing system.

> **`K-02`.** The project does not count the operating system against its internal size budget. It declares
> the dependency, its version, its hardening posture, its update cadence and its threat assumption.
> **Concealing a dependency does not remove it from the TCB.**

A ceiling on the policy kernel is a **tripwire, not a guarantee**; `AT-08` makes growth an explicit decision.

#### 4.2.1 Mutability classes (`R0` … `R4`)

The boundary is enforced **at the dispatcher**, not by governance.

| Class | Contents | Initial policy |
|---|---|---|
| `R0` root | Update root, signing policy, capability algebra | **Human plus threshold. No automation** |
| `R1` TCB | Policy kernel, broker, evaluator gate | Automatic candidate; human promotion |
| `R2` runtime | Episode engine, stores, adapters | Candidate plus CI plus canary; explicit approval |
| `R3` cognition | Prompts, operators, methods, routing | Promotion delegable to evidence policy |
| `R4` content | Memories, indexes, episodic data | Automatic write with quarantine and retention |

> **`K-03`.** At composition the dispatcher builds a **closed adapter table**. Any effect request whose
> normalised target resolves into `R0` or `R1` is **rejected before policy rules are evaluated**. The
> rejection is not configurable, because the check precedes the rule engine that could grant an exception.

### 4.3 The security claim `S1`

> **S1.** For any agent A executing under Vanguard, and any sequence of model outputs — including
> adversarial ones, including outputs induced by untrusted content in A's context — A cannot:
> **(a)** perform an effect outside its granted actions **and resources**;
> **(b)** cause a child to hold authority outside the parent's;
> **(c)** modify the verifier, its image, its inputs, or the measurement protocol;
> **(d)** exceed its limits without the overrun being debited and recorded;
> **(e)** cause untrusted content to authorise a capability-widening effect;
> **(f)** promote a claim to active competence without independent evidence;
> **(g)** reach the runtime, its configuration, its keys or its update path.

Clause (a) says *and resources* deliberately. Clause (g) is new in v4 and is what makes self-modification
safe to discuss at all.

### 4.4 The dispatch sequence `S0` … `S12`

**The single execution path for all effects.** Two distinct principals invoke it across well-defined
boundaries (`ADR-0061`):

1. **`Principal::Episode`** — ingress from the agent loop; submits action proposals (`observe`, `fs.patch`,
   `proc.test`). Subject to grant verification, selector attenuation and budget reservation.
2. **`Principal::EvidencePlane`** — ingress from the evaluator daemon, a **separate OS process identity**;
   submits evaluation executions triggered solely on observing a terminal ledger event. **The episode holds
   zero capability to invoke or request this path.**

The pipeline S0–S12 is identical and strictly mediated for both; the distinction resides in caller authority
and provenance. There is no second path, and `AT-01` proves it.

```
 S0  ENTER      EffectRequest { action, resource, args, principal, depth,
                                justifyingSpans, runId, parentLease }
 S1  PARSE      validate against the contract schema
 S2  RESOLVE    action → adapter                    ◄── BEFORE any lease
 S3  DESCRIBE   descriptor = digest(canonical(name, normalisedArgs))
 S4  CLASSIFY   widensCapability := classifier(request)   ◄── not a constant
 S5  AUTHORIZE  decision := policy.authorize(AuthorityRequest)
 S6  GRANT      grant := issue(descriptor, principal, resources, ttl)
 S7  RESERVE    lease := governor.reserve(runId, resources, parentLease)
 ┌── try ──────────────────────────────────────────────────────────────┐
 │ S8  VERIFY   assert the grant binds THIS descriptor and is unexpired │
 │              ◄── at the point of effect, not at issuance             │
 │ S8a INTENT   durably append EffectStarted{descriptor, grantId,       │
 │              idempotencyKey} and FSYNC   ◄── BEFORE the effect       │
 │ S9  DISPATCH adapter.execute(...)                                    │
 │ S10 COMMIT   governor.commit(lease, actual)                          │
 └── finally ──────────────────────────────────────────────────────────┘
 S11 RELEASE    governor.release(lease)             ◄── every path, always
 S12 EMIT       outcome events                      ◄── after release
```

#### 4.4.1 Ordering rules

| # | Rule | Defect prevented |
|---|---|---|
| `K-04` | **S2 precedes S7.** Adapter resolution before lease acquisition | An unknown action raising while holding a lease that is never released and never committed |
| `K-05` | **S8 is inside the guarded block, after S7.** The grant is verified at the point of effect | A resumed run, mutated request or stale decision riding an earlier grant |
| `K-06` | **S11 precedes S12.** Release before emit, including on the exception path | If the emit raises, the lease is already back. A leaked lease is worse than a lost event |
| `K-07` | **S10 debits reality, including overruns.** Refund is reserved minus actual, **retained when negative** | Clamping the refund at zero means an overrun is never debited |
| `K-08` | **S4 is a classifier call**, computed per request | A hardcoded value makes the predicate appear to fail closed on all tool use |
| `K-47` | **S8a precedes S9, and the intent record is durable before the effect begins.** Emission is split: intent before, outcome at S12 | A crash between dispatch and emit otherwise leaves no record that the effect was attempted, making an executed external effect **invisible** rather than **undeterminable** |

#### 4.4.2 Failure paths (`F-01` … `F-25`) — exhaustive; an exit not in this table is a defect (`AT-09`)

| # | Stage | Condition | Lease | Emitted | Returned |
|---|---|---|---|---|---|
| `F-01` | S1 | Schema validation fails | never opened | `EffectRejected{schema}` | contract error |
| `F-02` | S2 | Unknown action | **never opened** (`K-04`) | `EffectRejected{unknown_action}` | composition error |
| `F-03` | S2 | Adapter present but unhealthy | never opened | `EffectRejected{adapter_unavailable}` | instrument error |
| `F-04` | S3 | Arguments not canonicalisable | never opened | `EffectRejected{descriptor}` | contract error |
| `F-05` | S4 | Classifier raises | never opened | `EffectRejected{classifier_error}` | **fail closed** — treated as widening |
| `F-06` | S5 | Decision is reject | never opened | `AuthorizationDenied{reject}` | denied |
| `F-07` | S5 | Approval required, **benchmark mode** | never opened | `AuthorizationDenied{ask_fail_closed}` | denied |
| `F-08` | S5 | Approval required, **interactive mode** | never opened | `ApprovalRequested` | **suspend** |
| `F-09` | S5 | Authority predicate violated | never opened | `AuthorizationDenied{untrusted_justifying}` | denied |
| `F-10` | S5 | Request exceeds parent scope | never opened | `AuthorizationDenied{scope_escalation}` | denied, **alertable** |
| `F-11` | S6 | Grant issuance fails | never opened | `EffectRejected{grant_issue}` | kernel error |
| `F-12` | S7 | Budget denied on any dimension | denied | `BudgetReleased{denied}` | budget exhausted |
| `F-13` | S7 | Parent lease already closed | denied | `BudgetReleased{parent_closed}` | budget exhausted |
| `F-14` | S8 | Grant does not bind this descriptor | released | `EffectRejected{grant_mismatch}` | kernel error |
| `F-15` | S8 | Grant expired | released | `EffectRejected{grant_expired}` | kernel error |
| `F-16` | S8 | Grant already consumed | released | `EffectRejected{grant_replay}` | kernel error |
| `F-17` | S8 | Grant authenticator invalid across a process boundary | released | `EffectRejected{grant_forged}` | kernel error, **alertable** |
| `F-18` | S9 | Adapter raises | released | `EffectCompleted{error}` | error |
| `F-19` | S9 | Timeout | released | `EffectCompleted{timeout}` | timeout |
| `F-20` | S9 | Cancelled | released | `EffectCompleted{cancelled}` | cancellation |
| `F-21` | S9 | Perimeter unavailable or crashed | released | `EffectCompleted{error}` | **instrument error** |
| `F-21a` | S8a | Intent append fails | released | `KernelAlarm{intent_append_failed}` | kernel error — **the effect never starts** |
| `F-22` | S9 | External effect occurrence undeterminable | released | `EffectReconciled{unknown}` | **uncertainty preserved** |
| `F-23` | S10 | Commit fails | released | `BudgetReleased` | kernel error |
| `F-24` | S11 | Release itself fails | **leaked — alarm** | `KernelAlarm{lease_leak}` | kernel error |
| `F-25` | S12 | Emit fails | already released (`K-06`) | `EffectReconciled{unknown}` | **transactional outbox: intent record exists from S8a; recovery scanner reconciles to `undeterminable`** |

- `F-05`: failing open would mean an exception in the classifier disables the authority predicate.
- `F-22`: the enforcement point for `C-11`.
- `F-24`: the **only** condition raising a kernel alarm. **It must page, not log.**
- `F-25` (`ADR-0061`): an emission failure does **not** re-execute the effect; the transaction is enqueued to
  the outbox and the recovery scanner reconciles to `undeterminable`.

#### 4.4.3 Idempotence and replay (`K-09` … `K-12`)

| # | Rule |
|---|---|
| `K-09` | S1–S8 are **pure** given the request and kernel state. Re-execution yields the same decision or a replay rejection |
| `K-10` | S9 is **not** idempotent. Replaying a dispatch is a correctness violation, prevented by single-use grants |
| `K-11` | On resume, prior grants are **not** honoured. A resumed run re-authorises from S1 |
| `K-12` | Recorded replay bypasses **S9 only**; **S1–S8 execute normally** |

#### 4.4.4 Suspension (`K-13` … `K-17`)

Approval in interactive mode suspends **before** the lease is opened (`F-08`). Re-entry is at **S1** with the
same request.

| # | Rule | Rationale |
|---|---|---|
| `K-13` | No lease is held across a suspension | A suspension may last hours |
| `K-14` | Re-entry is at S1, never at S6 | An approval authorises a *request*; it does not bypass authorisation |
| `K-15` | The suspension token **binds the descriptor** | An approval cannot be transplanted onto a different call |
| `K-16` | Tokens expire, and expiry resolves as **denied** | Fails closed |
| `K-17` | In **benchmark mode**, approval never suspends (`F-07`) | A run blocking for a human has unbounded wall-clock and a human contributing to the measured outcome |

### 4.5 Grants — kernel obligations (`K-18` … `K-22`)

| # | Rule |
|---|---|
| `K-18` | A grant carries `descriptorDigest` (`CT-51`) and authorises **exactly that call**. S8 compares the descriptor recomputed at S3 against it; mismatch is `F-14`. **A grant without the field cannot be issued** |
| `K-19` | A grant is **single-use** whenever the effect has no safe idempotency key |
| `K-20` | A grant crossing a process boundary carries a **MAC or signature over its full contents**. An in-process grant may be an opaque reference |
| `K-21` | Long-running operations renew lease and grant explicitly. **There is no universal fixed time-to-live** |
| `K-22` | Granting subprocess execution grants execution **inside an already-limited environment**. It does not imply syscall interception, and **no document may describe it as though it does** |

### 4.6 Attenuation (`K-23` … `K-27`, `K-48`, `K-49`)

A child grant is valid only when its actions ⊆ parent's, its resources ⊆ parent's, and its constraints never
increase time, uses, bytes, budget, risk or resource surface.

| # | Rule |
|---|---|
| `K-23` | Attenuation **narrows**. It is idempotent, and the result is a subset of both the parent and the request |
| `K-48` | Resource inclusion is decided by the per-kind relation in `04 §5.3.1`. Total on defined pairs; **denies every undefined pair**, including all cross-kind comparisons. A checker returning "unknown" fails closed |
| `K-24` | **Depth is a budget dimension**; a child's depth is the parent's plus one, bounded |
| `K-25` | An out-of-scope request is **denied**, recording both what was requested and what was grantable |
| `K-26` | **There is no silent intersection** |
| `K-27` | Denial for scope escalation emits `AuthorizationDenied` as an **alertable** event (`F-10`), never a log line |
| `K-49` | **Revocation is immediate, applies to descendants transitively, and emits `CapabilityRevoked`** |

> **Why `K-26` is a security rule.** A child repeatedly requesting authority beyond its parent is the single
> strongest intrusion signal a system of this shape produces. Silent intersection discards that signal by
> construction, and does so while appearing more helpful.

**`ADR-0067` refinement — sealed scopes.** `Scope.sealed` is set by `attenuate()` when the parent withholds
verbs (`request.actions < parent.actions`). `StandardPolicy.authorize` denies
`request.action ∉ requested_scope.actions` **only when `requested_scope.sealed`**, before the approval gate,
as `DENIED_SCOPE_ESCALATION` (alertable; names requested vs grantable). Depth and proper-subset requested
scopes are **not** the signal — an unsealed narrower requested scope may still widen on a trusted operator
span. A blanket membership rule was measured and reverted.

### 4.7 Provenance and the authority predicate (clause S1(e))

> **Untrusted content may inform work; it may never authorise it.**

A violation occurs when a request **widens capability** *and* **any span justifying it carries an untrusted
label**. Evaluated at S5; violation is `F-09`.

| # | Rule |
|---|---|
| `K-28` | **Labels never improve.** No operation produces a label lower than its inputs |
| `K-29` | Model output that consumed any untrusted span is **untrusted-derived at minimum** |
| `K-30` | A tool or environment result is **untrusted-external at construction**, never at consumption |
| `K-31` | Labels are declared **per source class**, never at a call site |

#### 4.7.1 The two operands, both of which have failed silently

**First operand — capability widening must be a classifier output.**

> **`K-32`.** Capability widening is *true* when the request would grant an effect the principal does not
> already hold, or would escalate outside the perimeter; *false* when the request lies fully within the
> principal's declared actions and resources and escalates nothing.

Running the test suite under an already-held execution capability escalates nothing and classifies false. An
attempt at privilege elevation, egress outside the allowlist, or a write outside the granted resource
selector classifies true. **The corresponding must-fail test must fail against a hardcoded value** (`MF-01`).

**Second operand — justifying spans must accumulate monotonically.**

> **`K-33`.** Justifying spans at turn *n* are the **union** of the spans at turn *n−1*, the spans of the
> model reply at *n−1*, and the spans of the results at *n−1*. **Monotone, never reset within a run.** A
> child operator starts a fresh accumulation, and its **return value** enters the parent's accumulation as
> untrusted-derived at minimum.

The corresponding must-fail test must fail against a reset (`MF-02`).

#### 4.7.2 What provenance does not do

It does not prevent untrusted content from **influencing** model output. It does not track laundering within
a single model reply. It is not a defence against a compromised model. It does **not establish causation**.
For sensitive effects the mechanism is **intent binding** — the effect binds to a brief, a purpose digest and
an approval.

### 4.8 The workload perimeter (`K-34` … `K-46`)

> **The shell classifier is not a security boundary.** It classifies for policy and for the widening
> computation. **What contains an attacker is the perimeter.**

| # | Requirement |
|---|---|
| `K-34` | Separate **process, mount, IPC and network namespaces**; unprivileged user |
| `K-35` | **Only** the granted resource surface is writable. No host mounts, no privileged pseudo-filesystems, no container-control sockets |
| `K-36` | Network **denied by default**; egress only to an explicit allowlist, **enforced outside the sandboxed process** |
| `K-37` | CPU, memory, process-count and wall-clock limits **derived from the lease** where dimensionally possible |
| `K-38` | Cancellation kills the **process group**, not the direct child |
| `K-39` | A **syscall filter** denying process tracing, mounting, key operations, kernel program loading and namespace creation |
| `K-40` | The **evaluator runs inside the same perimeter**, with network **denied unconditionally** |
| `K-41` | The perimeter supervisor is a small, independently auditable, **statically linked binary** |

`K-40`: an asymmetric perimeter — contained evaluator, uncontained tools — was the prototype's recorded
deviation and is not carried forward.

**Containment is reported, never asserted.** The perimeter returns a **containment report**: runtime and
version, namespace configuration, syscall profile, network enforcement point, writable mounts, exposed
sockets, resource limits, the startup probes actually run, and the attestation time.

| # | Rule |
|---|---|
| `K-42` | Containment is **verified at startup by probing** — attempt a denied syscall, attempt a denied egress — **never inferred from configuration** |
| `K-43` | A runtime that cannot verify containment **reports that it cannot** |
| `K-44` | Where containment is unverified, the **publication path refuses to emit a number**, and the claim records the fact |
| `K-45` | The containment report is **part of the instrument tuple**. Two results with differing containment are **not comparable** |
| `K-46` | Degrading to an uncontained runtime is permitted for local development and **must be visible in every artifact it touches** |

### 4.9 Self-modification (clause S1(g)) — `SA-1` … `SA-6`

> **The agent may fabricate its successor; it may not replace its own brain while using it.**

| # | Rule |
|---|---|
| `SA-1` | **No model-controlled principal holds a capability reaching the live runtime's files, configuration, keys or process** |
| `SA-2` | Self-modification produces only a **candidate artifact** in an ephemeral workspace |
| `SA-3` | Candidate and evaluator **share no writable mount** |
| `SA-4` | Installation requires an artifact identified by **digest**, a **build and test attestation**, and a **release-controller policy decision** |
| `SA-5` | The policy kernel and the update root require **human or threshold approval**. **No fully autonomous promotion exists for that class** |
| `SA-6` | Every active version has a **bootable predecessor and a tested rollback** |

In-place self-modification is **prohibited outright**. When the optimiser proposes a core change: reject the
change, record the proposal with its rationale, and escalate it to a human as a design proposal. The
*pattern* of repeated proposals is valuable signal and is never a reason to relax the boundary.

### 4.10 Architecture tests (`AT-01` … `AT-12`)

These prove that **paths do not exist**, which is stronger than proving they are not taken.

| # | Assertion | Prevents |
|---|---|---|
| `AT-01` | No module outside the kernel imports an adapter, except the composition root | A second dispatch path |
| `AT-02` | No cognition or adapter module imports the laboratory or the evaluator gate | An agent constructing its own judge |
| `AT-03` | No client module holds an adapter handle or imports the kernel | An inspector that can act |
| `AT-04` | Every observation source declares a **static provenance label** | Per-call-site provenance judgement |
| `AT-05` | No tool declares a **commutativity claim** | Commutativity is a property of the resource |
| `AT-06` | No kernel or contract module imports cognition, adapters, clients or laboratory | TCB inversion |
| `AT-07` | Every path in the TCB list is covered by a review rule requiring human approval | Silent TCB drift |
| `AT-08` | The **policy kernel is within its declared size ceiling** | Unauditable growth |
| `AT-09` | Every action class has a case in the dispatcher's table, **and every dispatch exit appears in §2.3** | A silently unhandled path |
| `AT-10` | **No cast on data crossing a process boundary** | Unparsed external data acquiring a type |
| `AT-11` | Every plane the current phase declares process-separated runs under a **distinct OS identity and mount namespace**, verified at startup against the phase's declared topology. In Phase 0 that is **controller, worker and evaluator**; the updater has no runtime component | Plane separation existing only in documentation |
| `AT-12` | **No capability resolves to a path owned by the verifier, the policy configuration, the key store or the updater** | Clauses S1(c) and S1(g) becoming aspirational |

`AT-11` and `AT-12` are cross-process identity tests and are new in v4.

### 4.11 Threat model

**Attacker capabilities in scope:** control of content in the repository under work, in web or protocol
responses, and in dependencies the agent reads; inducing arbitrary model output through any of those;
influencing which trajectories enter the corpus through task content.
**Out of scope:** modifying operator configuration; modifying kernel code; a kernel-level container escape;
adversarial write access to the blob store.

| # | Asset | Consequence of compromise |
|---|---|---|
| `A1` | The verifier | Every number and every trained model becomes worthless. **Catastrophic** |
| `A2` | The host system | Standard remote-execution consequences |
| `A3` | The principal's authority | Privilege escalation within the run |
| `A4` | The budget ledger | Unbounded spend |
| `A5` | Competence and memory | Self-reinforcing corruption of all future runs |
| `A6` | The training corpus | Poisoned weights — persistent and hard to detect |
| `A7` | The release pipeline | Attacker-authored successor promoted with valid attestation |

| # | Attack | Controls | Residual risk |
|---|---|---|---|
| `T-01` | Prompt injection to capability escalation (A2, A3) | `K-30`, `K-32`, `K-33`, `K-34`–`K-41` | An attacker can cause the agent to do anything it was **already permitted** to do. Accepted; bounded by minimal per-principal authority and by the perimeter, not by the predicate |
| `T-02` | Reward hacking to verifier compromise (A1, A6) | Unreachability, double probe, containment honesty, `AT-02`, `AT-12` | Requires adversarial audit before any training run |
| `T-03` | Tool escape (A2) | `K-34`–`K-41` | The classifier is deliberately **not** load-bearing |
| `T-04` | Budget evasion (A4) | `K-04`, `K-07`, `K-13`, `K-24`, `K-25` | A single in-flight call may overrun before commit. Enforcement is eventually exact |
| `T-05` | Memory poisoning (A5, A6) | Four-stage claim pipeline and adversarial ablation, `K-30` | A record from a genuinely passing run can still encode a bad generalisation. Mitigation is statistical |
| `T-06` | Corpus poisoning (A6) | Verifier as sole admission gate; split discipline; containment and modification checks | Contamination discovered late is expensive |
| `T-07` | **Release-pipeline compromise (A7)** | `SA-3`–`SA-6`, hermetic build, attestation over inputs, signed canary, tested rollback | An attacker controlling the build host controls the successor. This is why `R0`/`R1` have no autonomous path |
| `T-08` | **Recovery-path forgery (A1, A4)** | Recovery controller outside the failed process; reconciliation by idempotency key; `F-22` | An adversary who can forge a heartbeat can keep a dead run apparently alive. **Heartbeats are authenticated on the same channel as grants** |

### 4.12 Audit checklist (one-day reviewer)

1. Enumerate every path from a model output to an effect. Is it exactly the S0–S12 sequence? Does `AT-01` prove it?
2. Is capability widening a classifier call, and does a must-fail test fail against a constant?
3. Do justifying spans accumulate monotonically, and does a must-fail test fail against a reset?
4. Take a granted capability. Name the resource selector. Can it reach the verifier, the policy configuration, the key store or the updater? `AT-12` must answer no.
5. Does an over-broad request produce a denial and an alertable event, or a quiet narrowing?
6. Is containment probed at startup, and does an unverified perimeter block publication?
7. Kill the worker. Who writes the terminal record? Is an undeterminable external effect recorded as undeterminable?
8. Show a grant crossing a process boundary. Is it authenticated?
9. Do the planes run under distinct identities at runtime, or only in the diagram?
10. For every control, name its must-fail test. **A control without one is not a control.**

> **Outstanding obligation recorded in the spec.** Until `CI-9` passes, every rule in VG-05 is *asserted and
> unproven*. **No rule may be cited as an established control before its test exists.**

---

## 5. Competence, Memory & Evidence Model (VG-06)

> Competence is the persistent object of the system: an **immutable graph of artifacts**, an **evidence
> graph** that says where each holds and what would refute it, and an **activation policy** that decides
> which of them apply right now.

### 5.1 The governing asymmetry

> **Reading memory is cheap and safe. Writing memory is expensive and dangerous.**

> **`MEM-1`.** **A passing verdict does not imply a semantically valid claim.** The verdict gates the
> *artifact*, never the *generalisation* extracted from it.

The replacement for verdict-gating is not a weaker gate; it is a **staged** one.

### 5.2 The four stores

| Store | Contents | Admission |
|---|---|---|
| **Working** | The current episode view | Automatic, ephemeral |
| **Episodic** | Events, observations, receipts | Integrity plus data policy |
| **Semantic claims** | Scoped assertions | Extraction plus evidence policy |
| **Competence** | Reusable representations, operators, methods, primitives | Ablation, transfer and activation policy |

**Four problems, not one:** **retention** (what is kept), **retrieval** (what surfaces when), **integration**
(how it enters context), and **degradation** (how it stops being trusted). Degradation decides whether the
library compounds or ossifies.

### 5.3 The claim pipeline

```
episode evidence
  → candidate claim              (extraction: origin, validity, counterpoints, expiry)
  → schema, provenance, validity check
  → contradiction search
  → corroboration or reproduction
  → quarantine
  → activation, for a bounded domain
  → continuous outcome attribution
  → demotion or expiry
```

**Four stages of standing**; authority is never acquired automatically:

1. **Episodic** — any complete trajectory may be retained, subject to data policy.
2. **Candidate claim** — an extracted observation carrying origin, validity domain, counterpoints and an expiry.
3. **Corroborated claim** — independent evidence, re-execution, or repetition across distinct contexts.
4. **Active competence** — ablation shows utility *outside* the cases it was derived from, no safety
   regression, and an expiry and demotion plan exists.

| # | Rule |
|---|---|
| `MEM-2` | Claims preserve environment, code version, evaluator, protocol and validity domain |
| `MEM-3` | A failure may produce a **dead-end claim**; it receives **no authority over effects** |
| `MEM-4` | Recall enters context as **data without instruction authority** |
| `MEM-5` | Every recall is recorded with its **candidates, scores, selected records and outcome attribution** |
| `MEM-6` | Automatic activation requires a **staleness policy and a demotion path** |
| `MEM-7` | The training corpus is a **separate, opt-in projection**. Episodic retention grants no training licence |

`MEM-4` is the memory-side expression of the authority predicate. `MEM-5` is what makes *"did memory change
the outcome?"* answerable at all.

**Adversarial ablation at activation.** Before a claim becomes active competence it is evaluated by someone —
or something — attempting to show that its apparent utility is **memorisation of its derivation cases**. A
claim that survives is admitted; one that does not is **quarantined, not deleted**.

**Contradiction.** Do **not** overwrite the older claim. Record a `contradicts` edge, run a resolution
operator, and **scope both by validity**. Two claims can be simultaneously correct in different versions or
environments.

### 5.4 Verification

#### 5.4.1 Evaluator classes

| Class | Example | Can support |
|---|---|---|
| `mechanically_reproducible` | Compiler, test suite, schema validator | Conformance to that instrument |
| `externally_grounded` | API read-back, sensor, confirmed transaction | An observed external effect |
| `human_adjudicated` | Blind review | Quality under a stated rubric |
| `learned_proxy` | Critic or process-reward model | **Ranking and triage** |
| `composite` | Checks plus humans plus environment | Whatever the protocol defines |

| # | Rule |
|---|---|
| `V-01` | **No class receives abstract authority as "objective".** A claim is scoped to its predicate |
| `V-02` | Rankers order candidates. **Only the verifier admits** |
| `V-03` | **Corpus admission requires a mechanically reproducible verdict**; structural and proxy verdicts may rank and never admit |
| `V-04` | A proxy's **drift against human judgement is monitored**; unmonitored drift demotes it |

#### 5.4.2 Verifier unreachability — three independent layers

For the set of paths owned by the verifier — its implementation, its image, its injected inputs, and the
measurement protocol — **no request of any effect class held by any agent may target them**. Enforced in
three independent layers so no single failure defeats it:

1. Static architecture test (`AT-02`, `AT-12`).
2. Dispatch-time rejection **before policy evaluation** (`K-03`).
3. **Read-only mounting** of injected inputs.

#### 5.4.3 The double probe

Read-only mounting is necessary and **not sufficient**, because a candidate can add a *new* file that
shadows the grader.

```
inputsUnmodified :=  tracked evaluator inputs unchanged
                  ∧  no untracked additions under the evaluator input paths
```

**Both probes are required fields on the verdict's evidence. A verifier that cannot compute them cannot
construct a verdict.**

#### 5.4.4 Inconclusive as a first-class state (`V-05` … `V-09`)

Three outcomes, not two: the change is correct per an instrument that worked; the change is wrong per an
instrument that worked; **the instrument did not work**.

| # | Rule |
|---|---|
| `V-05` | Provider errors, socket resets, unbuildable images and perimeter crashes yield *inconclusive* |
| `V-06` | Inconclusive runs are excluded from resolve-rate **numerators and denominators** |
| `V-07` | The **per-arm instrument-error rate is reported**, and asymmetry is a confound rather than a footnote |
| `V-08` | A **wrong-but-real answer is a failure**. The guard must not shrink the denominator |
| `V-09` | A verifier that cannot verify emits *inconclusive*, never a pass. **Fail closed** |

**Why this is an integrity control:** an attacker who can induce rate limits on one arm can otherwise
**manufacture a lift result**.

### 5.5 Promotion, activation and demotion

#### 5.5.1 Three stages, in order

**Stage 1 — hard constraints.** Never negotiable, never traded: capability containment; evaluator integrity;
privacy and licensing policy; absence of TCB mutation; the risk budget; declared safety non-regression;
data-split and contamination rules. A candidate violating any of these is rejected regardless of performance.

**Stage 2 — the frontier.** For performance, cost, latency, transfer and calibration: estimate effects with
uncertainty, reject hard-constraint violations, admit candidates that are **not clearly dominated**, and
**retain alternatives with distinct trade-offs**.

**Stage 3 — activation.** Which frontier member applies is a **per-context policy decision**, not a global
ranking.

> A scalar objective is not merely imprecise; it is **self-reinforcing through the corpus**.

#### 5.5.2 Promotion criteria — all must hold for domain D

- its interface and dependencies are valid;
- an evidence claim exists for D;
- evaluation used tasks **not** used in its derivation;
- **ablation without it degrades the outcome beyond practical uncertainty**;
- there is no safety regression;
- validity and staleness are defined;
- substrate dependence is known;
- **activation is reversible**.

**Novelty is observable, never an optimisation target.** Any operational novelty metric is trivially gamed by
generating unusual junk.

#### 5.5.3 Demotion and anti-ossification (`V-10` … `V-13`)

The greatest risk is **retaining knowledge past the conditions that made it true**.

| # | Rule |
|---|---|
| `V-10` | Every active artifact carries **non-empty invalidation conditions**, automatically checked where machine-checkable |
| `V-11` | **Continuous outcome attribution demotes** artifacts correlated with degraded results |
| `V-12` | **Model replacement triggers re-evaluation of every active artifact**, not a confidence carry-forward |
| `V-13` | Retirement removes from the activation set and **preserves lineage** (`CT-36`) |

### 5.6 The outer loop

```
run episodes → verify → distil candidates → evaluate against baseline and
incumbent → promote under §5 → attribute outcomes → demote → repeat
```

**Distillation** extracts a candidate artifact from verified episodes — a playbook, an operator brief, a
representation. **Selection** is a **contextual bandit over the frontier**: which active artifact applies to
this task class, learned from outcomes rather than declared.

**Why this compounds and prompt-tuning does not.** A tuned prompt is a point estimate against one model, one
task distribution and one moment. An artifact with an evidence block, a validity domain, invalidation
conditions and an ablation record is a *claim with a lifecycle*: it can be re-tested, scoped, demoted and
superseded. The first decays silently; the second **decays visibly**.

### 5.7 Substrate invariance

**The substrate profile** — provider, model identity and fingerprint, adapter version, capability probe
results, context window, tool protocol, sampling controls, measurement time and probe-suite digest — travels
with every claim and is part of the instrument tuple.

**Migration protocol**, run whenever the substrate changes:

1. **freeze** the activation set under the current substrate;
2. **measure** the new substrate with the probe suite;
3. **re-execute a stratified sample without retuning**;
4. **classify** each artifact as `portable`, `degraded` or `incompatible`;
5. permit compatibility adapters as **new artifacts**, never as silent mutation of the original;
6. repeat **after tuning**, separately and labelled as such;
7. report performance, cost and calibration deltas.

> **"Survived the model change" means retention of effect under protocol** — not that the file still loads.

**Substrate debt** is tracked explicitly: the count and proportion of active artifacts whose portability has
not been re-measured since the current substrate was adopted. Reported metric with a refresh cadence.

### 5.8 Honest limits

The flywheel is bounded by the evaluator. Ablation is the only trustworthy attribution and it is expensive
(hence `EvaluationBudget` as a first-class dimension). A claim from a genuinely passing run can still encode
a bad generalisation — mitigation is statistical, not architectural. Transfer claims require ablation **and**
holdout.

---

## 6. Loop Engineering, Measurement & Self-Improvement (VG-07)

> **A number produced outside the rules in §5 is not a number.**

**Implementation binding (`S8-J-07`, 2026-08-17).** The in-tree apparatus that must obey §5 is
`tools/telemetry/` (`tuple.py` for `M-18`, `preregistration.py`, `aa_runner.py`, `statistics.py`,
`splits.py`, `gap_freeze.py`) and `lab/{build,run,diff,bench}.py`. A lift across differing `K_compat` is
refused. Degenerate A/A designs are refused. p-values at n<20 are refused.

### 6.1 The three closure conditions

| # | Condition | Failure mode when violated |
|---|---|---|
| `CL-1` | **Judge exteriority** — the verifier is not reachable by anything it judges | Reward hacking; the system optimises the measurement |
| `CL-2` | **Evaluation exteriority** — the task set used to *promote* is disjoint from the set used to *optimise* | Training-set scoring; improvements that do not replicate |
| `CL-3` | **Noise exteriority** — the observed delta exceeds the variance of the identical configuration against itself | Publishing noise; a random seed presented as a design insight |

`CL-1` is **architectural** and enforced by VG-05 §7 and VG-06 §4.2. `CL-2` and `CL-3` are **protocol** and
enforced in VG-07.

### 6.2 Levels of loop engineering — vocabulary, never a roadmap

| Level | Work |
|---|---|
| `L0` | Single completion; no loop |
| `L1` | Tool loop; retry on failure |
| `L2` | Context engineering, compaction, re-grounding |
| `L3` | Composition: operators, isolation, playbooks |
| `L4` | Outer loop: distillation, promotion, demotion |
| `L5` | Corpus and training feedback |

> **`M-01`.** The levels are vocabulary, never a backlog. **No ticket may ever read "implement L6."**

### 6.3 Long-horizon instrumentation

| Signal | Measurement |
|---|---|
| Consolidation loss | Replace the transcript with the structured record, re-run, compare outcomes |
| Re-grounding divergence | How often re-grounding finds a divergence, and whether a rising rate predicts eventual failure. Available **during** the run |
| Retrieval value | Arm A with recall, arm B without; **per-record counterfactual attribution** against a matched base rate |

The retrieval question is **"did retrieval change the outcome, and in which direction"**, not "did we
retrieve something relevant". A record whose recall correlates with worse outcomes is a poisoned record and
is demoted automatically (`V-11`).

### 6.4 Distillation and promotion pipeline

```
run tasks
  → the verifier admits successes                          (CL-1)
    → distil recurring patterns (offline operator)
      → candidate artifact + pre-registered hypothesis
        → paired comparison on HOLDOUT, against unguided
          AND against the incumbent                        (CL-2)
          → effect must exceed the A/A floor               (CL-3)
            → promotion under the three-stage relation     (06 §5)
              → continuous attribution → demotion
```

**Two comparisons, not one.** Against unguided establishes that the artifact does anything; against the
incumbent establishes that it does more than what is already active.

### 6.5 The measurement doctrine (`M-02` … `M-20`)

#### 6.5.1 Paired designs and the test

Task difficulty variance dominates every other variance component: between-task variance in solvability
exceeds between-configuration variance by a large margin. **An unpaired comparison of two configurations on
two random task samples is measuring which sample was easier.**

| # | Rule |
|---|---|
| `M-02` | **Every comparison is paired**: both arms attempt the same instances, and the analysis is over **discordant pairs only** |
| `M-03` | **McNemar's exact test** on the discordant counts — the exact binomial form, **not** the chi-squared approximation |
| `M-04` | Report **all** of: both discordant counts, their total, the exact p-value, the effect size, and a **confidence interval** on the paired difference. **A p-value without an effect size and an interval is not a result** |
| `M-05` | Any experiment testing more than one hypothesis controls family-wise error by **Holm–Bonferroni** |
| `M-06` | **The family is declared before any arm runs**, as a pre-registered artifact with a hash — hypotheses, primary metrics, alpha, correction, manifest hash, and a **fixed stopping rule**. Optional stopping is not permitted |

#### 6.5.2 The A/A noise floor (`M-07` … `M-11`)

The floor is the same configuration against itself under pure stochasticity.

| # | Rule | Rationale |
|---|---|---|
| `M-07` | **A floor whose arms sit at 0% or 100% is refused, not reported** | Zero discordance there is *unobserved*, not *low*. The statistics module must refuse it |
| `M-08` | Floor sample size must be **adequate** | A floor at three instances characterises nothing |
| `M-09` | The floor is computed on the **same manifest** as the comparison it licenses | Noise is task-set dependent |
| `M-10` | A **preliminary** floor is marked as such and **may not size an admission run** | |
| `M-11` | A new floor is a **new artifact with a new hash**, never an in-place edit | Any published number citing the old hash must remain checkable |

**Sample size** is derived numerically from the floor's discordance rate, the minimum detectable effect,
alpha and power, and is recorded in the family declaration. **Detecting a five-point effect against a
realistic floor typically requires low hundreds of paired instances.**

#### 6.5.3 Arm design (`M-12` … `M-17`)

| # | Rule | Defect prevented |
|---|---|---|
| `M-12` | **Both arms' change mechanisms must have equal expressive power** | One arm's mechanism silently dropped newly created files. *A comparison whose mechanisms differ measures the mechanism* |
| `M-13` | **Identical model fingerprint and sampling parameters** | Otherwise you measured the model |
| `M-14` | The baseline is specified exactly and **its template hashed** | "We used the standard prompt" must be checkable |
| `M-15` | **Both arms must be posed the actual problem** | A baseline that received an identifier as its brief. Both arms equally uninformed; the lift characterises a harness never told what to do |
| `M-16` | Instrument errors excluded, and the **per-arm error rate reported** | An asymmetric error rate is a confound masquerading as a result |
| `M-17` | **Cost non-inferiority must be non-vacuous** | If every row reports zero cost, the cost condition passes vacuously |

#### 6.5.4 The instrument tuple and the comparability rule (`M-18`)

```
Tuple = ⟨ K_compat , D_treatment , S_strat , M_meta ⟩
```

- **`K_compat` (Compatibility Key)** — benchmark ID, split hash, model fingerprint and sampling parameters,
  harness commit, agent definition hash, evaluator image digest, **containment report digest**, substrate
  profile, runner version, schema version. Must be **strictly equal** (`K_A = K_B`) across compared arms.
- **`D_treatment` (Treatment Dimensions)** — the declared experimental axis under test (e.g.
  `vg-code-default` vs `vg-shell-only`; L1–L5 prefix-cache enabled vs disabled).
- **`S_strat` (Stratification Fields)** — controlled categorical dimensions (task difficulty tier,
  repository programming language).
- **`M_meta` (Observation Metadata)** — physical timestamp, run ID, node ID, operator identity.
  **Explicitly excluded from the strict equality comparison operator.**

> **`M-18` — the comparability rule.** Two results are comparable **if and only if** their compatibility keys
> match (`K_A = K_B`) and their tuples differ in **exactly** the declared treatment dimensions. The
> comparison harness **refuses** to compute a lift between runs differing in an undeclared dimension.

#### 6.5.5 Splits and contamination (`M-19`, `M-20`)

| Split | Purpose | Access |
|---|---|---|
| `DEV` | Iteration, debugging, optimisation | Unrestricted |
| `HOLDOUT` | Promotion decisions (`CL-2`) | **Read at promotion time only; never optimised against** |
| `SEALED` | Publication | Touched only under the full publication protocol; every touch logged; **a fixed number of touches per period** |

| # | Rule |
|---|---|
| `M-19` | **Contamination is one-directional and irreversible.** A sealed set used for iteration is a development set **forever**. Touches are a depleting budget recorded in a ledger |
| `M-20` | Any instance whose trajectory entered the training corpus is **contaminated for evaluation permanently**. **Corpus membership must be checkable per instance** |

#### 6.5.6 What becomes measurable (the one-variable experiment set)

Caching on/off against cost per resolved task; single-turn against tool-loop at the same model; a faster
index against resolve rate (determines whether a systems-language investment is justified); playbook
rigidity across its three settings; a flat agent against composition **at equal total budget**; operator
isolation against horizon length; consolidated record against full transcript; recall on/off; model-tier
routing across the cost-quality frontier.

> **A change showing a six-point improvement has measured nothing until the A/A floor on that task set is known.**

### 6.6 Optimisation and what it cannot do

Hill-climbing under a fixed evaluator improves the configuration you have. The **exploitation trap** is
structural: the corpus records what the current system does, promotion favours what the corpus supports, the
next generation optimises harder within the same basin. Mitigation is an **explicit variance budget** — a
fixed fraction of experimental capacity reserved for non-incremental changes, evaluated against a held-out
**different** set.

**Paradigm shifts come from humans reading trajectories.** The apparatus exists to surface anomalies, not to
have the idea.

### 6.7 The release pipeline (`M-21` … `M-24`)

```
candidate artifact (ephemeral workspace, no writable mount shared with the evaluator)
  → hermetic build          reproducible, inputs pinned
    → attestation           over inputs, toolchain and outputs, by digest
      → evaluation          hard constraints, then frontier (06 §5)
        → signed canary     bounded traffic, bounded blast radius
          → promotion       activation pointer moved, never file contents
            → rollback      predecessor bootable, rollback tested before promotion
```

| # | Rule |
|---|---|
| `M-21` | Promotion **moves an activation pointer**. It never writes over a running component |
| `M-22` | **A rollback that has not been executed successfully is not a rollback.** It is tested before the promotion it protects |
| `M-23` | Canary telemetry is compared against the incumbent **under the tuple rule (`M-18`)**, not against expectations |
| `M-24` | Root and TCB classes have **no autonomous promotion path** (`SA-5`) |

### 6.8 The transfer experiment (impoverished-ontology, Phase 2)

> **What is the smallest system in which a structure the designers did not author, and could not have
> anticipated, measurably improves performance on tasks it was not derived from, survives replacement of the
> model that produced it, and can be shown not to be memorisation, retrieval, or proxy optimisation?**

1. An environment with hidden structure expressible only through a representation absent from the initial artifact set.
2. An agent with minimal representations, a bare operator set, and the competence machinery of VG-06.
3. Run until performance plateaus. **Plateau is the trigger** — the observable form of *"my representation is inadequate."*
4. Invoke representation invention. The candidate enters as a **candidate**, never as active.
5. **Control A** — an agent given the candidate must outperform one given an equal-length random or shuffled structure. *Guards against novelty theatre.*
6. **Control B** — evaluate on a structurally related environment never seen and not used in distillation. *Guards against memorisation.*
7. **Control C** — rehydrate under a **different model family** and re-run control B. *Guards against substrate dependence.*
8. **Control D** — an agent with the full trajectory history but **without** the candidate entry must underperform. Distinguishes *the representation* from *the experience of having encountered the data*. **The control most likely to fail, which is why it is the one that matters.**
9. Report against the A/A floor on the transfer environment, with the family declared in advance.

**This falsifies the programme** if no candidate ever clears controls A through D.

### 6.9 The experiment registry (`M-25` … `M-28`)

| # | Rule |
|---|---|
| `M-25` | Every experiment is **registered before it runs**: family declaration, manifest, hypotheses, derived sample size, and the split it will consume |
| `M-26` | The registry tracks **committed capacity** — compute, wall-clock and human adjudication time — against available capacity per period |
| `M-27` | **Human adjudication time is a budgeted, scheduled resource**, not overhead absorbed by whoever is available |
| `M-28` | **An experiment that cannot be powered at the available capacity is not run at reduced power.** It is deferred, redesigned, or its effect target is raised |

### 6.10 Preparation for search, process rewards and reflection

None of these is built in Phase 0; **all three are foreclosed by contract decisions made in Phase 0**.

| Capability | What must exist first |
|---|---|
| Search over trajectories | Branch and fork parentage in the event stream; isolated snapshots per branch; per-branch verdicts |
| Process reward models | **Step-level attribution** — which operator produced which proposal — recorded from the first episode |
| Reflection | Structured records and dead-end capture **as data rather than prose** |

**Deferring the capability is correct. Deferring the contracts it will require is not**, because the retrofit
is a corpus migration rather than a feature.

---

## 7. Architectural Decision Record Summary (VG-09)

**Format:** Decision · Context · Alternative (stated fairly enough that its advocate would recognise it) ·
**Reversal condition** · Status (`accepted` · `superseded by ADR-nnnn` · `reversed on evidence`).
**Append-only.** An entry is never edited; it is superseded by a later entry that cites it.

### 7.1 Foundational decisions

| ADR | Decision | Reversal condition |
|---|---|---|
| `0000` | ADRs are append-only, numbered, each states a reversal condition | Never — meta-rule |
| `0001` | TypeScript on a Node-compatible runtime for the control plane | Team composition shifts decisively, or the interactive-surface roadmap is abandoned. **REVERSED by `ADR-0063`** |
| `0002` | Subprocess with line-delimited JSON as the seam to systems components | A measured hot path exceeds thousands of calls/sec |
| `0003` | Agent-loop primary; **no runtime workflow graph** | A reference reconstruction proves inexpressible without a graph |
| `0004` | The verifier is immutable and unreachable from every capability | Never within this programme's assumptions |
| `0005` | No runtime extension discovery; **registries freeze at composition** | Never without a replacement audit mechanism |
| `0006` | No systems-language components in Phase 0, including the index | A measured number on a real repository crosses a stated threshold |
| `0007` | **Parallel independent execution from the first loop commit** | Measured latency parity, which falsifies `C-04` |

### 7.2 Adjudications between the two pre-v4 lineages

| ADR | Decision | Reversal condition |
|---|---|---|
| `0008` | **JSON Schema 2020-12 normative**; a TypeScript validator is an implementation | Only one language ever consumes the contracts |
| `0009` | **RFC 8785 canonicalisation**, not a house algorithm | The standard proves inadequate for a required type, documented with the failing case |
| `0010` | **Transactional embedded store with WAL**; line-delimited JSON is export only | Storage volume exceeds what an embedded store handles |
| `0011` | **Capabilities carry resources, not only verbs** | Never — this is `S1(a)` |
| `0012` | Attenuation **denies** out-of-scope requests; never silently intersects | Denial noise proves unmanageable (a policy-authoring defect, not an argument for silence) |
| `0013` | **Three processes in Phase 0, not five** | Phase 1, when the perimeter hardens — a **scheduled** reversal |
| `0014` | **Two languages at the first contract lock**, not three | A third consumer appears |
| `0015` | **Promotion is a partial order over a frontier**, not a scalar objective | A domain where every dimension is genuinely commensurable |
| `0016` | **Operators are data in the competence graph**, not functions in the loop | Never without abandoning self-improvement above the prompt level |
| `0017` | **Competence is a graph, not an array** | Never |
| `0018` | **Invalidation conditions are mandatory and non-empty** | Never |
| `0019` | **Self-modification is a release pipeline**; in-place modification prohibited | Never within this programme's assumptions |
| `0020` | `VG-nn` document identity equals the file index | Never |

### 7.3 Corrections — each bound to the test that now catches it

| ADR | Claim found false | Now caught by |
|---|---|---|
| `0021` | "Every effect passes a mediating layer" — a logical mediator is not a containment boundary | `K-01`, `K-22`, `MF-11` |
| `0022` | Containment reported as a boolean | `K-42`, `MF-13` |
| `0023` | A size ceiling covering the whole TCB (it applies to the policy kernel) | `K-02`, `AT-08` |
| `0024` | Concurrency safe because reads precede writes | `CC-7`, `MF-19` |
| `0025` | A dying process emits a terminal event | `03 §9`, `MF-21` |
| `0026` | An external effect always resolves to success or failure | `F-22`, `MF-22` |
| `0027` | Capability widening as a constant | `K-32`, `MF-01` |
| `0028` | Justifying spans reset each turn | `K-33`, `MF-02` |
| `0029` | Read-only mounts protect the evaluator (necessary, not sufficient) | `06 §4.3`, `MF-16` |
| `0030` | A passing verdict licenses a memory write | `MEM-1`, four-stage pipeline |
| `0031` | Provider errors as task failures | `V-05`, `MF-17` |
| `0032` | Schemas strict for both readers and writers | `SC-10`, `MF-27` |
| `0033` | Vector agreement establishes schema equivalence | `04 §17` property tests |
| `0034` | An architecture test requiring four process identities in Phase 0 | `AT-11`, `03 §12` |
| `0039` | A grant carrying no descriptor | `CT-51`, `MF-31` |
| `0040` | "Resources are a subset" with no decision procedure | `CT-52`, `MF-32` |
| `0041` | A mutable timestamp inside a content-addressed artifact | `CT-53`, `MF-33` |
| `0042` | Invalidation satisfiable with only manual conditions | `INV-2`, `MF-34` |
| `0043` | Every event bound to an episode | `04 §12.1`, `MF-35` |
| `0044` | A single trailing emit point | `K-47`, `MF-36` |

### 7.4 Deferrals with a scheduled reversal

`0035` five-process split → Phase 1 perimeter hardening · `0036` third-language conformance vectors → when
the perimeter supervisor exists · `0037` memory-write gating tests → Phase 2 with the memory ticket ·
`0038` schema `LOCKED` status → `TK-01`, when two implementations agree and canonicalisation triples exist.

### 7.5 Sprint 0 governance baseline (`ADR-0045` … `ADR-0053`)

| ADR | Decision |
|---|---|
| `0045` | New decisions use expanded ADR fields (scope, evidence, consequences, affected components, approval metadata); old entries remain immutable |
| `0046` | **GTS-13C is the sole active programme plan** and owns sequencing and rationale only — never a contract |
| `0047` | **`spike/` and `slice/` are disposable consumers only**, may never be imported, and **must be deleted at the S4 gate** |
| `0048` | The **S4 trust-spine gate runs a scripted trajectory with no model dependency** |
| `0049` | Shipped tools begin as typed `read/search/patch/test`; **shell is selector-scoped and privileged**; `vg-shell-only` remains the **permanent experimental baseline** |
| `0050` | **Effects are execution primitives; Episodes coordinate open-ended work; declared durable state machines coordinate approvals, releases and governance; tools are not Episodes** |
| `0051` | **Every effect is attributed and recorded; only `privileged` sinks require descriptor-bound capability mediation.** Sink class is schema data; misclassification is adversarially tested |
| `0052` | The Active MVP Contract has **two independent 100% gates**: baseline assignment coverage and merged-scope evidence coverage |
| `0053` | **No implementation PR merges before the governance baseline is jointly approved** (documented one-time bootstrap exception for governance/CI) |

Approval events: `APPROVAL-0001` (accept 0045–0053 as the Sprint 0 governance baseline, 2026-08-15);
`APPROVAL-0002` (ICD, Active MVP Contract v1, Verification Plan; 22 assigned requirements — 10 covered S0
rows, 12 open T1 rows); `DECISION-0001` (conditional go for Sprint 1 prep; no schema lock or product merge).

### 7.6 Kernel, sprint-structure and phase-authorisation decisions

| ADR | Decision |
|---|---|
| `0054` | Implement **T2 dispatch as the single S0–S12 path**, durable intent before execution, descriptor-bound grants for privileged sinks, recording for every sink class. **Measured kernel baseline 1,307 logical source lines with a 131-line review alarm** |
| `0055` | Rebase Sprint 3 off covered T2/T3: S3 = port bundles + first cassette episode slice + process engine; S4a = finish episode + no-model trajectory; S4b = perimeter + S4 exit deletion of `spike/`/`slice/` |
| `0056` | Four parallel packets (`S3-SA/SB/DC/DD`, `S4-SA/SB/DC/DD`); real OpenRouter is S4-DC and must not be imported by `TEST-TRUST-001` |
| `0057` | **Beta = GTS-13C Ch.10 Q1+Q2 at S6**: one framework, one harness `vg-code-default`, OpenRouter, typed tools, Git, human approve of the exact descriptor. TableWorld and A/A are out of beta. **`DEF-12` superseded for privileged apply. VG-03 §6.2 run-termination vocabulary wins over GTS-13C T4.5** |
| `0058` | Authorize **Phase 2 (Sprints 5–6)** as the Lightweight Beta MVP wave: S5 lands T5.3–T5.6 exterior evaluator OS isolation and T4.9–T4.11 prefix-stable context compiler; S6 lands T6.1–T6.8 runtime composition root, descriptor-bound approvals, live OpenRouter coding harness |
| `0059` | **Polyglot plugin and port decoupling** via standard wire envelopes (JSON-RPC/IPC/stdio/WebSocket). Heavy domain extensions in Rust/Go/TypeScript-Node/Python live **strictly outside the TCB** and connect across port adapters |
| `0060` | **The Domain Generality Invariant.** The microkernel (S0–S12) and recursive episode loop must remain **100% agnostic to task domains**. Coding is merely a configuration manifest (`vg-code-default`). Adding non-coding domains must require **zero lines of code modified in `kernel/` or `agency/episode/`** |
| `0061` | Apply **Specification v0.4.1 (v4B)** patches before Sprint 5: partition `M-18` into 4 algebraic subsets; formalize **dual kernel ingress** (`Principal::Episode` vs `Principal::EvidencePlane`); replace `F-25` log-only fallback with **transactional outbox + recovery reconciliation to `undeterminable`**; correct `DEF-02` test namespace; annotate `DEF-12` supersession; qualify expressiveness and operator-isolation loss-profile claims |
| `0062` | Implement **Unix Domain Socket `RuntimeService` daemon** and **asymmetric Ed25519 operator approval authority** for Sprint 6B Close (Beta v0.4.1). NDJSON wire RPC (`StartRun`, `GetRun`, `StreamEvents`, `ResolveApproval`, `Cancel`, `Resume`) with **SQLite WAL transaction inbox/outbox**. Approvals signed **outside** the runtime process over **descriptor-bound RFC 8785 canonical bytes**; the runtime retains **only public-key verification authority** |
| `0063` | **The control plane is Python.** `ADR-0001` reversed on evidence. The TypeScript CLI remains the Interaction-plane client and the `ADR-0014` second-language contract reader |
| `0064` | **Record MVP gate status at `0238b1a`: Q1 partially met and regressed, Q2 not demonstrated, Q3 not met, Q4 not met.** No artifact, tag, README or external communication may describe the system as having passed GTS-13C Ch. 10 until the closing sprint for each gate lands (Q1→S7, Q2→S9, Q3→S9, Q4→S10) |
| `0065` | Adopt **D-01…D-15** from the LAM/manifests roadmap as binding: dual cassette stores; **depth-1 until independence groups exist**; **no live PTY**; new verbs are registry rows not engine branches; the proposal translator becomes **manifest-driven**; **`vg-shell-only` is the only legal control arm** |
| `0066` | **MCP is configuration and an adapter after v0.4.3, never authority.** MCP may discover and name tools; it must **not** issue grants, widen scope, bypass `Kernel.dispatch`, or sit on the evaluator plane. An MCP-shaped tool is a capability row + adapter. ACP/A2A are client protocols and do not replace VG-04 |
| `0067` | **Sealed scopes** (see §4.6). `Scope.sealed` set by `attenuate()` when the parent withholds verbs; action-membership denial applies **only when sealed**, before the approval gate, as `DENIED_SCOPE_ESCALATION` |
| `0068` | `EvidenceClaim` optional hedge fields `supportCount`, `lastCorroboratedAt`, `protectionClass` — named by the writer schema, omitted by default, **recorded but not consumed** |

Further governance events: `APPROVAL-0003` (close Sprints 0–2; tag `v0.0.0-sprint0`; T1 remains DRAFT, not
LOCKED); `APPROVAL-0004` (close Sprints 3–4; tag `v0.4.0-sprint4`; `spike/` and `slice/` deleted and proven
absent by `MF-S4-001`; 252 unittests pass; 42/42 merged-scope contract evidence; 21 broken counterparts pass;
**TCB 1307 LOC pass**); `DECISION-0005` (authorize **Phase 3 as Waves W6–W9 / Sprints 7–10**; **Sprint 7 is a
subtraction sprint** — no features, ~1,530 LOC deleted, three boundary rules added; **`MetaLoopEngine`
(`runtime/loops/`) is rejected, not deferred** — it executes effects outside the kernel and grades its own
work, inverting `A-05`); `DECISION-0006` (**`SEC-01` reopened** — `scan_secrets.py --all-refs` fails on a
reachable `.env` blob with 21 `refs/original` refs; remediation order is binding: rotate at the provider,
then rewrite history under repository-owner authorisation, then verify `--all-refs` **and** a clean-clone
scan; CI must run strict mode).

### 7.7 What belongs in the register

An ADR is written when a decision would otherwise become tribal knowledge. **The test:** would a competent
engineer arriving in six months be surprised by this, and unable to reconstruct why?

---

## 8. Deferred & Rejected Design Space (VG-10)

A **deferral** is a capability worth building later (scheduled work). A **rejection** is an idea examined and
declined (a closed question that may reopen only on new evidence). **Nothing is removed from this register
silently.**

### 8.1 Deferred (`DEF-01` … `DEF-12`)

| # | Deferred | Why now | Reversal condition |
|---|---|---|---|
| `DEF-01` | **Graphical authoring canvas** | A graph is an excellent authoring surface and a poor runtime substrate | A recorded trajectory renderer exists and users ask to *edit* rather than only inspect |
| `DEF-02` | **Semantic memory in Phase 0** | The claim pipeline needs an evaluator and a corpus, neither of which exists | Phase 2, with the memory ticket and dedicated memory-write gating tests in a clean `MF-` namespace allocation |
| `DEF-03` | **General subagents** | Operator invocation covers the Phase 0 cases | Phase 2, when a real task needs depth beyond operator invocation |
| `DEF-04` | **Protocol integrations, browser, web search, retrieval index** | Each is a registry entry plus configuration by construction (`C-02`) | Phase 2+, or earlier if a dogfood opt-out reason names one |
| `DEF-05` | **Systems-language index** | Orchestration is under five milliseconds against seconds of inference | A measured number on a real repository crosses a stated threshold |
| `DEF-06` | **Search over trajectories, process rewards, reflection** | Not built in Phase 0; **their contracts are** | (capability only; contracts land now) |
| `DEF-07` | **Autonomous updater as a runtime component** | `R0`/`R1` promotion is a human action (`SA-5`) | Phase 1, as a distinct identity — **never as autonomous promotion for those classes** |
| `DEF-08` | **Public benchmark participation** | A number before the A/A floor exists is the premature-measurement error | Phase 3, once `07 §5` apparatus runs |
| `DEF-09` | **Training on the corpus** | Requires corpus opt-in, per-instance contamination tracking, and licensing | Phase 3, **and never before the adversarial verifier audit** |
| `DEF-10` | **A dedicated discovery / competence-expansion document** | The machinery it would specify does not exist | When `06 §5` promotion has run on real artifacts |
| `DEF-11` | **Compaction beyond a recency window in Phase 0** | Strategy comparison is a `07 §5.8` experiment; no instrument yet | Phase 2, once consolidation loss is measurable |
| `DEF-12` | **Approvals, suspension and session resume** | Phase 0 runs interactive with a human present throughout | **Superseded by `ADR-0057` for privileged effects in beta.** Descriptor-bound human approval for `fs.patch` (sink class `privileged`) lands in Phase 2 (Sprint 6). **General multi-turn session suspension outside privileged effects remains deferred** |

### 8.2 Rejected (`REJ-01` … `REJ-12`) — never classify these as "missing"

| # | Rejected | Why | Would reopen if |
|---|---|---|---|
| `REJ-01` | **Runtime workflow graph or topology language** | Strictly less expressive than a loop that can invoke a loop, at roughly ten times the machinery | A reference reconstruction proves inexpressible without one |
| `REJ-02` | **Levels as a roadmap (`L6`, `L7`, …)** | A level taxonomy invites treating movement up the ladder as progress | **Never.** The vocabulary stays; the backlog does not |
| `REJ-03` | **Novelty as an optimisation objective** | Any operational novelty metric is trivially gamed by generating unusual junk | A metric provably resistant to adversarial generation — none is known |
| `REJ-04` | **Self-generated evaluation criteria as a promotion gate** | An evaluation regress; `CL-1` violated at the definition | Never within this programme's assumptions |
| `REJ-05` | **Commutativity as a tool property** | Commutativity belongs to the resource, not the verb | Never |
| `REJ-06` | **A single ordered provenance lattice** | Conflates independent questions and forces one number to answer all of them | Never |
| `REJ-07` | **Shell classification as a security boundary** | It is a parser, and parsers can be parsed around | **Never — the perimeter is the boundary** |
| `REJ-08` | **Governance as TCB enforcement** | A policy is routed around by a motivated optimiser and forgotten by a tired human | **Never. Enforcement is at the dispatcher** |
| `REJ-09` | **"Cognitive operating system" as architectural language** | Promises scheduling, isolation, resource ownership and lifecycle the system does not provide | When the system provides them |
| `REJ-10` | **Biological, cosmological and particle-physics analogies as specification content** | They leaked into specifications and produced the two-lineage divergence | Never in a normative document |
| `REJ-11` | **Scalar reward for promotion** | Self-reinforcing through the corpus (`ADR-0015`) | A domain where all dimensions are genuinely commensurable |
| `REJ-12` | **An always-on full-content training capture** | Content may be secret, personal or unlicensed | Never |

Additionally rejected by later decision: **`MetaLoopEngine` (`runtime/loops/`)** — rejected, not deferred
(`DECISION-0005`); **MCP as an authority path** — MCP is configuration and an adapter only (`ADR-0066`).

### 8.3 How an entry moves

A deferral becomes work when its reversal condition is met — deleted from §1 and appearing as a ticket, with
an ADR recording the transition. A rejection reopens **only** on evidence named in its final column.

---

## 9. Build Plan, Programme Spine & Roadmap Milestones (VG-08, GTS-13C)

### 9.1 Phase 0 scope (VG-08)

**In:** wire schemas and conformance; controller with broker; the episode reducer; budgets and leases;
capability grants; the transactional event store with line-delimited export; the blob store; a fake model
and one real provider; the Git environment; **TableWorld**; minimal tools and operators; a
separately-identified evaluator; `vg run` and `vg trace`; a rootless worker perimeter with containment
reporting; crash recovery; basic redaction; and CI carrying boundary, property, conformance and must-fail
tests.

**Out, and not renegotiable mid-phase:** canvas or any GUI; protocol integrations and browser; semantic
memory; automatic competence promotion; general subagents; search, process rewards or training; public
benchmarks; an autonomous updater; a systems-language index; **measurement and the A/A floor**.

> **The failure this list prevents:** Phase 0 quietly becoming Phase 0–2, taking four months, and never being
> dogfooded. If something in the right-hand column seems necessary to make Phase 0 work, **that is evidence
> the loop is wrong, not that the scope is wrong.**

### 9.2 Phase 0 hypotheses

| # | Hypothesis | Falsified by |
|---|---|---|
| `H0` | One episode engine serves coding and TableWorld | Any environment-specific change to the core |
| `H1` | All external authority derives from a scoped capability | Any effect without a valid grant |
| `H2` | A compromised worker cannot reach the control or evidence planes | Any read, write, secret or egress escape in the red-team suite |
| `H3` | Events permit recovery without inventing certainty | An in-flight effect that cannot be reconciled being marked as definitely succeeded or failed |
| `H4` | The Coding Cell closes the feedback loop on real work | Inability to fix simple and multi-file bugs without manual intervention |
| `H5` | The store supports operational replay | Reduced state diverging from stored events |

### 9.3 Three increments

- **Increment A — Trust Spine.** Runs a deterministic script with **no model at all** and proves: denial by
  resource scope; child attenuation; budget enforcement; event atomicity; recovery from a kill; evaluator
  isolation; secret non-disclosure; redaction.
- **Increment B — Coding Cell.** Adds a provider, minimal operators and the Git environment. Must resolve: a
  single-file bug; a multi-file bug; a bug requiring a test to be run and reacted to; a bug creating a new
  file; and **one task where the correct outcome is abstention or escalation**.
- **Increment C — Generality Witness.** Adds TableWorld **through registries, configuration and adapters
  only**. Must resolve: a constrained reconciliation; a derived transformation; an inconsistency detection
  ending in abstention; and a local compensation. If Increment C requires touching the episode engine, the
  capability algebra or the event envelope, **`H0` is falsified**.

### 9.4 Phase 0 tickets (`TK-00` … `TK-12`)

| # | Ticket | Depends | Exit test |
|---|---|---|---|
| `TK-00` | Repo, tooling, CI, dependency boundaries, `ADR-0000`…`0012` | — | A deliberately cyclic import fails the boundary gate |
| `TK-01` | Wire schemas, canonicalisation, vectors, **TypeScript + Python conformance**, generated reader profiles | `TK-00` | **`SC-7` and `SC-12` both closed** |
| `TK-02` | Identifiers, resources, principals, capability grants, attenuation | `TK-01` | Scope escalation denied and emitted as an alertable event |
| `TK-03` | Budget ledger and lease tree | `TK-01` | An overrun is debited negative and moves the ceiling; a child cannot exceed the parent's remainder |
| `TK-04` | Event store, reducer, replay | `TK-01` | Replay reproduces an identical state digest |
| `TK-05` | Recovery controller | `TK-04` | A killed worker yields a terminal record written from outside it, with undeterminable effects marked undeterminable |
| `TK-06` | **Broker, policy, dispatch** | `TK-02`, `TK-03` | Fault injection covering every path in `05 §2.3`; no adapter executes without a grant |
| `TK-07` | Secret references and data policy | `TK-02` | No secret value appears in any prompt, event, export or diagnostic stream |
| `TK-08` | Worker perimeter and containment report | `TK-06` | Mount, egress and syscall probes recorded; an unverified perimeter blocks publication |
| `TK-09` | Evaluator under a separate identity | `TK-06` | A candidate can neither read nor write the evaluator bundle |
| `TK-10` | End-to-end episode on a fake model, then a real provider | `TK-04`, `TK-06` | Proposal → grant → receipt → evaluation completes; a simulated rate limit becomes an instrument termination, never a task failure |
| `TK-11` | Git environment, coding operators, `vg trace` | `TK-10` | A new file appears in preview and patch; export is complete, redacted and correlated |
| `TK-12` | TableWorld, its evaluator, and the Phase 0 review | `TK-11` | Added with **zero** episode-engine changes; exit criteria signed |

**`TK-01` before everything.** Its completion criteria (all three deliverables): a TypeScript validator
generated from the schemas agreeing with Python on every vector (valid, invalid, canonical, digest,
round-trip, unknown-field families) → closes `SC-7`; canonicalisation triples (input, RFC 8785 form, digest)
for every digest-carrying type → closes `SC-7`/`GV-2`; **a schema artifact for every type defined in VG-04**
→ closes `SC-12`. **No ticket beyond `TK-01` begins until both close.**
**`TK-06` is the ticket to slow down on.** It is the policy kernel.

### 9.5 CI gates (VG-08 §4)

| Gate | Checks |
|---|---|
| `typecheck`, `lint` | Strict mode; **no casts on data crossing a process boundary**; no direct system calls outside adapters |
| `boundaries` | The layer lattice of `03 §4` |
| `test-unit`, `test-property` | Algebraic laws: attenuation narrows, provenance never improves, descriptors stable |
| `test-vectors` | Cross-language conformance, both profiles |
| `test-must-fail` | §5, **against the broken implementations in `test/broken/`** |
| `test-fault-injection` | Every failure path in `05 §2.3` |
| `tcb-size` | Policy kernel within its declared ceiling |
| `schema-drift` | Generated artifacts match their source; reader profiles regenerate identically |
| `docs-audit` | `CI-1`…`CI-9` from `00 §9` |

**If a must-fail test passes against its broken counterpart, CI fails.**

### 9.6 The must-fail suite (`MF-01` … `MF-37`)

| # | Broken implementation it must catch | Guards | Ticket |
|---|---|---|---|
| `MF-01` | Capability widening hardcoded to a constant | `K-32` | TK-06 |
| `MF-02` | Justifying spans reset each turn | `K-33` | TK-06 |
| `MF-03` | A grant issued with no resource scope | `K-18` | TK-02 |
| `MF-04` | A child scope broader than its parent | `K-23` | TK-02 |
| `MF-05` | An over-broad request silently narrowed | `K-26` | TK-02 |
| `MF-06` | Lease released only on the success path | `K-06` | TK-03 |
| `MF-07` | Refund clamped at zero | `K-07` | TK-03 |
| `MF-08` | Adapter resolution after lease acquisition | `K-04` | TK-06 |
| `MF-09` | A consumed grant replayed successfully | `K-19` | TK-06 |
| `MF-10` | A grant crossing a process boundary unauthenticated | `K-20` | TK-06 |
| `MF-11` | Worker reading a control-plane mount | `K-35` | TK-08 |
| `MF-12` | Egress outside the allowlist | `K-36` | TK-08 |
| `MF-13` | Containment inferred from configuration rather than probed | `K-42` | TK-08 |
| `MF-14` | A secret value reaching a prompt, event or diagnostic | `K-22` | TK-07 |
| `MF-15` | An evaluator bundle writable by the candidate | `06 §4.2` | TK-09 |
| `MF-16` | A shadowing file under an evaluator input path scoring as a pass | `06 §4.3` | TK-09 |
| `MF-17` | A provider error counted as a task failure | `V-05` | TK-10 |
| `MF-18` | A wrong-but-real answer excluded from the denominator | `V-08` | TK-10 |
| `MF-19` | A mixed batch reordered | `CC-7` | TK-06 |
| `MF-20` | A duplicate non-idempotent effect after retry | `K-19` | TK-06 |
| `MF-21` | A kill producing no recovery record | `03 §9` | TK-05 |
| `MF-22` | An undeterminable external effect resolved to success or failure | `F-22` | TK-05 |
| `MF-23` | Line-delimited JSON used as the primary store, truncated mid-commit | `CT-42` | TK-04 |
| `MF-24` | An untracked new file omitted from the patch | `03 §7.3` | TK-11 |
| `MF-25` | An integer above 2⁵³−1 corrupted on the wire | `04 §0.4` | TK-01 |
| `MF-26` | An unknown schema version accepted silently | `CT-48` | TK-01 |
| `MF-27` | A reader profile rejecting an unknown field | `CT-44` | TK-01 |
| `MF-28` | A descriptor including the provider-assigned call identifier | `D-3` | TK-01 |
| `MF-29` | An empty invalidation-conditions array accepted | `INV-1` | TK-01 |
| `MF-30` | TableWorld requiring a conditional in the core | `C-10` | TK-12 |
| `MF-31` | A grant issued without a descriptor digest | `CT-51` | TK-02 |
| `MF-32` | Selector inclusion approximating pattern containment instead of denying | `CT-52` | TK-02 |
| `MF-33` | A check timestamp written inside a content-addressed artifact | `CT-53` | TK-01 |
| `MF-34` | An artifact activated with only manual invalidation conditions | `INV-2` | TK-01 |
| `MF-35` | An evolution event forced to carry a synthetic run identifier | `04 §12.1` | TK-04 |
| `MF-36` | **A crash between dispatch and emit leaving no intent record** | `K-47` | TK-06 |
| `MF-37` | A conflict resolved as last-write-wins with no event | `CC-6` | TK-06 |

**Deferred and recorded:** memory-write gating and adversarial ablation at activation have no Phase 0 test.

### 9.7 The rule-to-test map and its untestable classes

The map is **generated**, not hand-maintained. Three classes are marked **untestable, with justification**:

| Class | Why | Compensating assurance |
|---|---|---|
| Architectural prohibitions (`LT-*`) | Prove the absence of a path, not a behaviour | Static analysis, stronger than a runtime test |
| Statistical rules (`M-*`) | Hold over a family of experiments, not a single execution | **Refusal behaviour is testable**: a degenerate floor must be refused |
| Human-gated rules (`SA-5`) | Depend on an out-of-band approval | Tested by proving **no autonomous code path exists** |

Coverage is satisfied by **any** of five test families: must-fail against a broken implementation;
architecture test proving a path does not exist; property test over an algebraic law; cross-language
conformance vector; fault injection over the dispatch failure paths.

**Baseline: 203 normative rules · 28 tested · 42 untestable-with-justification · 133 uncovered.**
`CI-9` is a **Phase 0 exit gate**, not a documentation gate.

### 9.8 Phase 0 exit criterion

**Mechanical:** the five coding tasks and three TableWorld tasks ran with **no core change between
environments**; no effect occurred without a valid capability; the red-team suite reached neither the control
plane, nor the evaluator, nor secrets; kill and restart preserved the distinction between known and
uncertain; replay reconstructs state; budgets and cancellation reach the subprocess tree; a full audit trace
exists and the operational trace contains no known secret; provider errors did not contaminate task
outcomes; every must-fail test fails against its broken counterpart; **`CI-9` is green**; an engineer who did
not write the policy kernel can audit it and reproduce the suite; every Phase 0 ADR remains accepted or was
explicitly reversed on evidence.

**Measurable dogfood.** Over a **fourteen-day window**, the team routes **at least 60% of eligible bug-fix
work** through the Coding Cell, and **every opt-out is logged with a reason**.

**Judgement, retained deliberately.** Three real bugs in a repository someone knows well — at least one
requiring edits in more than one file, at least one requiring running tests and reacting. Run each
interactively, **do not fix things by hand mid-run**, then answer: *next time, would you reach for it?*

**What does not close Phase 0:** all tickets merged; CI green; a demo that worked once; a number.

**Early warnings:** nobody has run it on a real bug by the halfway point (the single most reliable predictor
of a Phase 0 that never closes); a must-fail test is hard to write; the policy kernel is growing past its
ceiling; someone wants a "just this once" second dispatch path; scope creep toward memory or general
subagents; Increment C needing a core change.

### 9.9 GTS-13C — programme artifact ownership

| Artifact | Owns | Status |
|---|---|---|
| **Decision Record** | Every locked decision, its trade-off, its reversal condition | Append-only, authoritative |
| **System Architecture & ICD** | Package boundaries, port signatures, isolation topology | Authoritative for structure |
| **Active MVP Contract** | `requirement → component → owner → test → evidence` | **The only merge gate** |
| **Verification, Threat & Evaluation Plan** | Must-fail suite, adversarial suite, A/A protocol, gap monitor | Authoritative for assurance |
| **Issue tracker** | What is being worked on, by whom, when | Source of truth for execution |
| **GTS-13C** | The plan and the reasoning | **Non-normative.** Owns nothing else |

### 9.10 GTS-13C — the task spine (`T0` … `T11`)

Contract-relevance tag: **[C]** generates Active MVP Contract rows · **[B]** stays in the backlog only.

| Series | Scope | Tag |
|---|---|---|
| `T0` **Schema archaeology** | Three real bugs fixed by hand, recorded as observation/proposal/effect/receipt/judgement lines; a third engineer reconstructs from the file alone; produce `field-inventory.md`; repeat for one **non-coding** task; time each manual fix (the human baseline). **Blocks the *locking* of T1 contracts only** | **[B]** |
| `T0a` **Provider API spike** (S1a, deleted at S4) | Throwaway script against one real provider; discovers wire format, streaming shape, rate-limit behaviour, error taxonomy, token-accounting quirks. Lives in `spike/`, unimportable. Output `provider-notes.md` — **the notes survive; the code does not** | **[B]** |
| `T0b` **End-to-end disposable slice** (S2, deleted at S4) | One vertical path: *prompt → model call → proposed patch → human approval → applied diff → test run → result shown*. May consume real T1 schemas and the event store; **may not be depended on** by them or by `kernel/`, `agency/`, `governance/`, `adapters/`. Output `slice-findings.md`. **Deleted outright at the S4 exit review**, verified in CI | **[B]** |
| `T1` **Contracts — the keel** | See §9.11 | **[C]** |
| `T2` **Kernel — enforcement, permanent** | See §9.12 | **[C]** |
| `T3` **Ledger** | `T3.1` transactional append-only store, single writer, monotonic sequence, crash-safe · `T3.2` pure reducer `(State, Event) → State` in `domain/`, zero I/O, associative over batches · `T3.3` replay yields identical state digest · `T3.4` **projections rebuildable from zero — a projection is a cache, never a source of truth** · `T3.5` NDJSON export with redaction, correlation preserved · `T3.6` run lease + heartbeat + **recovery scanner outside the dying process** · `T3.7` effect reconciliation by idempotency key; `undeterminable` **stays** that way · `T3.8` **cassette recorder/player for the model port** | **[C]** |
| `T4` **Execution — effects, episodes, processes** | See §9.13 | **[C]** |
| `T5` **Perimeter & evaluator** | `T5.1` rootless worker (own OS identity, mount namespace, credential set; network denied by default; egress through a **destination-aware proxy with logs**) · `T5.2` containment report per run; unverified perimeter blocks publication · `T5.3` evaluator under **separate identity and image digest** · `T5.4` **double probe on every verdict** · `T5.5` Evidence plane owns the evaluation trigger — **no episode may request its own evaluation** · `T5.6` `inconclusive` fail-closed; per-arm instrument-error rate reported | **[C]** |
| `T6` **Coding harness — the first, disposable, point design** | See §9.14 | **[C]** |
| `T7` **Artifact graph & harness manifests** (moved to S2a) | See §9.15 | **[C]** |
| `T8` **Instrument** | `T8.1` A/A runner (**no delta is interpretable until this number exists**) · `T8.2` paired runner over discordant pairs · `T8.3` statistics module — McNemar exact for paired binary, **paired bootstrap/permutation** for cost and latency, **survival methods** for timeouts and censoring, **hierarchical models** for repeated repos/models/task families · `T8.4` pre-registration artifact hashed before any arm runs · `T8.5` splits `DEV / HOLDOUT / SEALED / LIVE / DEPLOYMENT` + touch ledger + per-instance corpus membership check · `T8.6` **oracle suite beyond repo tests** (property, metamorphic, mutation-score delta, differential vs pre-change binary, sanitizers, type/borrow checks) · `T8.7` **meta-evaluator dashboard** for the verifier–deployment gap, which **freezes promotions automatically** past threshold · `T8.8` **seeded-sabotage suite** | **[C]** |
| `T9` **Generality falsifier** | `T9.1` one genuinely non-coding environment (structured-data reconciliation) · `T9.2` domain-native evaluator under the same evaluator contract · `T9.3` **added through registries, configuration and adapters only** | **[C]** |
| `T10` **Engineering discipline — CI from day one** | See §9.16 | **[C]** |
| `T11` **The four executable artifacts** (S0, before the first merge) | Decision Record; System Architecture & ICD; **Active MVP Contract**; Verification, Threat & Evaluation Plan; issue-tracker backlog; cross-document consistency review then tag the baseline | **[B]** |

**The merge rule.** `T11.6` does not block `T0`, `T0a`, `T0b`, `T10.1`–`T10.3` or any local spike. It **does
block merging to main**: no PR lands until the Active MVP Contract exists and the baseline is tagged.

### 9.11 `T1` — contract deliverables

| # | Deliverable |
|---|---|
| `T1.1` | Canonicalisation spec: deterministic byte encoding, integer handling, field ordering, digest algorithm. **≥40 golden triples** (`input → canonical → digest`) |
| `T1.2` | `primitives`: `Digest`, `Timestamp`, `EpisodeId`, `RunId`, `BranchId`, `ProcessId`, `ArtifactId`, `ClaimId`, `GrantId`, `PrincipalId`, `EvaluatorId`. Opaque, validated at parse |
| `T1.3` | `ResourceSelector` with a **decidable inclusion relation per kind**. Kinds at v0.1: `path`, `glob`, `command`, `host`, `record`. `includes(a,b)` total, **denies** every undefined pair. Property test: reflexive, transitive, antisymmetric-up-to-equality |
| `T1.4` | `EffectDescriptor` — `{verb, sinkClass, selector, args, argsDigest, idempotencyKey, riskTier, provenance}`. **`sinkClass ∈ {pure, observation, privileged}`** is data on the descriptor, not a convention |
| `T1.5` | `CapabilityGrant` — `{grantId, principal, descriptorDigest, selector, constraints, expiry, parent, maxUses}`. **A grant with no descriptor digest fails at parse** |
| `T1.6` | `Receipt` — `{grantId?, outcome: ok\|failed\|undeterminable, observedAt, resultDigest, note}`. `grantId` optional because non-privileged effects are recorded without a grant. **`undeterminable` is a first-class outcome** |
| `T1.7` | `EventEnvelope` — `{seq, at, kind, episodeId?, processId?, causationId, correlationId, payload, provenance, dataPolicy, tenant}`. Both scope ids optional |
| `T1.8` | `Artifact` — `{artifactId, kind, class, compensatesFor?, hypothesis, evidenceRefs, invalidationConditions[], riskDelta}`. `kind` resolves against an **extensible registry**, never an enum. `class ∈ {enforcement, compensation}`; `compensatesFor` required iff `compensation` |
| `T1.9` | `Claim` — VG-06's evidence claim, **unchanged**. `invalidationConditions` `minItems: 1` enforced in schema |
| `T1.10` | `CorrectionRecord` — `{episodeId, proposedPatchDigest, acceptedPatchDigest, reasonCodes[], magnitude, scope}`. Reason codes: `functional_defect \| missing_requirement \| security_policy \| test_inadequacy \| maintainability \| architecture_preference \| style \| product_change \| environment_change \| reviewer_disagreement`. **Style and preference corrections are user/team/repo-scoped and may never become general competence** |
| `T1.11` | `Recording` — `{modelCassetteDigest, imageDigest, envSnapshotDigest, seed, clockPolicy}`. What makes **counterfactual re-execution** possible |
| `T1.12` | `ProcessDefinition` + `ProcessInstance` — the durable state machine contract. `{processId, definitionDigest, currentState, allowedTransitions[], pendingApprovals[], boundEffectVerbs[]}`. States and transitions are **declared data**, readable by a non-engineer, **resumable from the ledger without replaying any agent reasoning** |
| `T1.13` | Writer profile (`additionalProperties: false`) and **generated** reader profile (`additionalProperties: true`) |
| `T1.14` | Second-language **reader-only** implementation. Conformance = both readers agree on all golden vectors |
| `T1.15` | Migration rehearsal: add a field, bump minor, prove old readers survive and old events still reduce |

### 9.12 `T2` — kernel deliverables

| # | Deliverable |
|---|---|
| `T2.1` | **Principal model:** `user`, `operator`, `episode`, `process`, `evaluator`, `release` are **distinct principals**. A governance process must not borrow an episode's authority |
| `T2.2` | Grant issuance bound to `descriptorDigest`; point-of-effect verification recomputes and compares |
| `T2.3` | **Attenuation algebra.** A child grant may only narrow: verb ⊆, selector ⊆, constraints ⊆, expiry ≤, uses ≤, budget ≤. Property test: monotone, **no widening fixpoint** |
| `T2.4` | Explicit denial as an **alertable event**, never a silent no-op |
| `T2.5` | Budget as a **lease tree**. Child holds a lease on the parent's remainder. Overrun at commit debits negative and lowers the ceiling. Property test: **conservation** |
| `T2.6` | Dispatch with **complete failure enumeration**, and an **intent record written before dispatch** |
| `T2.7` | **Secret references only.** No secret value in any prompt, event, export or diagnostic stream. Test: grep the full export for every known secret |
| `T2.8` | **Mediation scoped by `sinkClass`** (see below) |
| `T2.9` | Provenance axes (**origin, integrity, sensitivity, trust**) with **conservative sink-oriented propagation**: a `privileged` effect whose args derive from an untrusted block requires elevation regardless of verb. Do not claim causal isolation; claim only that the sink narrowed authority |
| `T2.10` | **TCB size budget as a tracked metric with an alarm**, plus an ADR per kernel change |

**`T2.8` — the sink-class mediation table (`ADR-0051`, `L-17`):**

| `sinkClass` | Recorded in ledger | Capability-mediated | Examples |
|---|---|---|---|
| `pure` | **Yes** | No | Deterministic transform, digest computation, reduction |
| `observation` | **Yes** | No — but **selector-checked** and provenance-labelled | File read within an already-granted scope, index query, event query |
| `privileged` | **Yes** | **Yes — grant required, descriptor-bound** | File write, patch apply, process exec, network egress, model call, secret access, memory write, irreversible external effect |

> **Everything is recorded. Only `privileged` traverses the kernel.** Recording and mediation are
> **independent properties** and were previously conflated. `sinkClass` is a **field on the descriptor**, so a
> must-fail test can plant a `privileged` effect declared as `pure` and confirm the kernel rejects it.

### 9.13 `T4` — the execution spine

| # | Deliverable |
|---|---|
| `T4.1` | **Effects are the primitive, and every effect is recorded.** Every touch of the world produces an `EffectDescriptor` and a `Receipt` in the ledger — no exceptions |
| `T4.2` | **Two coordinators, not interchangeable.** **Episodes** carry open-ended agentic work (recursive loop; the model reasons here). **Durable state machines** carry approvals, releases and governance (finite declared state set, auditable by a non-engineer, survives restart without replaying agent reasoning). **The test:** *if you can enumerate the states in advance and someone outside engineering would want to read them, it is a process.* Otherwise it is an episode |
| `T4.3` | Episode loop `observe → propose → authorise → effect → receipt → evaluate`. **The engine knows no cognitive vocabulary** — a lint rule forbids `plan`, `debug`, `reflect`, `architect` as identifiers in `agency/` |
| `T4.4` | **Recursion, correctly scoped.** An episode may spawn child episodes with attenuated leases and a cancellation scope: one type, one budget algebra, one attenuation rule, one event stream, at every level of *coordination*. **A tool is not an episode** |
| `T4.5` | Terminal states `resolved \| abandoned \| denied \| inconclusive \| abstained \| recovered`. **Abstention is a scored success.** (Superseded by VG-03 §6.2 vocabulary per `ADR-0057`) |
| `T4.6` | Structured concurrency: task groups, automatic cancellation propagation, per-branch workspace destroyed in `finally`, cancellation reaching the subprocess **group** |
| `T4.7` | Ordering: emitted order preserved; mutations are barriers; parallelism requires a declared independence group or provably disjoint read/write sets; conflict raises an explicit event |
| `T4.8` | **Process engine:** load `ProcessDefinition`, advance `ProcessInstance` on events, block on pending approvals, **resume after restart from the ledger alone**. Property test: an interrupted process resumes to the same state without re-running any episode |
| `T4.9` | **Context compiler as a separately versioned artifact.** Layers `L1 SYSTEM / L2 TOOLS / L3 ENVIRONMENT / L4 TASK / L5 DIALOGUE`, rendered **prefix-stable** for provider cache economics. Every block tagged with source and provenance label |
| `T4.10` | **Operator invocation = child episode with a pinned artifact set.** An operator is **data** (prompt + tool subset + context policy + termination rule), never a class |
| `T4.11` | **Competence estimate recorded before acting, scored after.** Nothing consumes it yet; retrofitting later costs a corpus migration |

### 9.14 `T6` — the coding harness

| # | Deliverable |
|---|---|
| `T6.1` | Git environment adapter: worktree per branch, snapshot-bound observation, diff/patch/apply, preview before effect. Real provider rebuilt cleanly behind `ModelPort` — **never lifted from `T0a` or `T0b`** |
| `T6.2` | **Default tool set is typed, not shell.** `read`, `search`, `patch`, `test` ship as the default, each with a typed schema, an explicit `sinkClass`, a risk tier and a resource selector. `shell` is a **selector-scoped fallback**, reachable only through a `command`-kind allowlist, always `sinkClass: privileged`, at a risk tier **no weaker than** the typed tool it substitutes for |
| `T6.3` | `build` joins the typed set once the first four are stable. Every new typed tool earns its place against the `vg-shell-only` baseline |
| `T6.4` | CLI: interactive TUI + headless. Streaming, cancel, resume, checkpoint. **`vg run`, `vg trace`, `vg why`** |
| `T6.5` | **`vg why <artifact>`** — what evidence activated it, what it predicts, what would demote it |
| `T6.6` | **Descriptor-bound approvals:** the approval authorises the **normalised descriptor shown to the human**, not a later-altered command. Approval is an effect against the process engine, **not a side channel** |
| `T6.7` | Correction capture in the merge path. Reason code prompt is one keystroke, not a form |
| `T6.8` | **Latency instrumentation:** startup, time-to-first-token, time-to-first-effect, approval round trips, event-write overhead, **p95 resume** |

### 9.15 `T7` — artifact graph and harness manifests

| # | Deliverable |
|---|---|
| `T7.1` | **`kind` registry:** `system_prompt`, `tool_schema`, `tool_impl`, `middleware`, `skill`, `context_policy`, `retrieval_policy`, `compaction_policy`, `routing_policy`, `budget_policy`, `subagent_config`, `playbook`, `process_definition`, `runtime_image`, `operator`, `competence_claim`. **Extensible — new kinds require a schema, never a core change** |
| `T7.2` | **One logical edit = one commit** in the harness workspace |
| `T7.3` | **`HarnessManifest`:** component graph + capability requirements + evaluator bindings + budget policy. **Resolves and freezes at composition, per episode** |
| `T7.4` | **`vg-shell-only` registered as a permanent baseline manifest.** One tool, selector-scoped, no middleware, no skills, no sub-agents. **Never deleted; flagged undeletable in the registry.** The standing zero-assumption control |
| `T7.5` | **`vg harness build \| run \| diff \| bench`** |
| `T7.6` | **Reconstruction suite** — express a Claude-Code-shaped, an OpenCode-shaped and a minimal-SWE-agent-shaped harness as manifests. The direct test of "every reference harness is configuration" (`C-01`) |
| `T7.7` | **Between-episode discovery:** signed, allow-listed manifests may install between runs under operator policy. **Within an episode, the set is frozen** |

**Reference manifest `vg-code-default`:**

```yaml
harness: vg-code-default
components:
  system_prompt:    sha256:…
  tools:            [read@1, search@1, patch@1, test@1]   # typed, selector-scoped
  fallback_tools:   [shell@1]                              # allowlist only, elevated tier
  context_policy:   layered-l1l5@1
  routing:          single-model@1
  budget:           interactive-default@1
capabilities:
  - verb: fs.read     sink: observation  selector: {kind: glob, pattern: "${repo}/**"}
    risk: low
  - verb: fs.patch    sink: privileged   selector: {kind: glob, pattern: "${repo}/**"}
    risk: medium
  - verb: proc.test   sink: privileged   selector: {kind: command, allow: [pytest, go, cargo]}
    risk: medium
  - verb: proc.exec   sink: privileged   selector: {kind: command, allow: [git]}
    risk: high          # shell fallback — never weaker than what it replaces
evaluators: [coding-oracle@3]
```

**Permanent baseline manifest `vg-shell-only`:**

```yaml
harness: vg-shell-only          # NEVER DELETED. The instrument's floor.
components:
  system_prompt:    sha256:…    # minimal
  tools:            [shell@1]
  context_policy:   recency-window@1
  routing:          single-model@1
capabilities:
  - verb: proc.exec   sink: privileged   selector: {kind: command, allow: [git, pytest, ruff]}
    risk: high
evaluators: [coding-oracle@3]
```

### 9.16 `T10` — engineering discipline

| # | Deliverable |
|---|---|
| `T10.1` | **Dependency direction enforced as a build failure:** `domain ← ports ← kernel ← agency ← runtime → adapters`; **`governance → domain, ports, kernel` only**; `cli → runtime`; `lab/` imports nothing and is imported by nothing; **`spike/` and `slice/` are imported by nothing** |
| `T10.2` | **Two implementations per port from day one** (fake + real). A contract satisfied by one implementation is an implementation wearing an interface |
| `T10.3` | **`test/broken/`** — deliberately broken implementations; every must-fail test runs against its broken counterpart and **must fail** |
| `T10.4` | **Architecture tests proving paths do not exist.** Minimum set: nothing imports `spike/` or `slice/`; **no route from `agency` to `adapters/evaluators`**; **`governance/` has no model dependency**; **`agency/` contains no approval logic** |
| `T10.5` | Fault injection over every dispatch failure path |
| `T10.6` | Generated **requirement-to-test map** from the Active MVP Contract. CI fails on any row with neither a passing test nor an `untestable-with-justification` marker |
| `T10.7` | **Specification gate: 100% test-or-justification coverage of the Active MVP Contract. No partial threshold.** No new normative rule enters any v4 document while a single contract row is uncovered and unjustified |
| `T10.8` | **Margin alarms, not limits**: TCB LOC, p95 first-token, p95 first-effect, context tokens, schema extension slack |
| `T10.9` | **No-special-cases review item**: a conditional naming one provider, one environment or one task type fails review |

### 9.17 GTS-13C spine — one primitive, two coordinators, five nouns

```
Effect     descriptor → [authorisation if privileged] → execution → receipt
             │            ALL effects recorded. Only privileged mediated.
             │
             ├── Tool       executes ONE typed effect. Coordinates nothing.
             │
             ├── Episode    identity + lease + context + operators + terminal state
             │              ⟵ RECURSIVE. Open-ended agentic work.
             │
             └── Process    definition + instance + states + transitions + approvals
                            ⟵ DURABLE. Known, finite, auditable governance.

Artifact   content-addressed, typed by an extensible kind registry
Claim      scoped assertion with non-empty invalidation conditions
Event      immutable record of all of the above
```

**`domain/` inventory (GTS-13C §5.1):**

```
Digest, Timestamp, EpisodeId, RunId, BranchId, ProcessId,
ArtifactId, ClaimId, GrantId, PrincipalId, EvaluatorId      // opaque, parsed not cast

SinkClass          = pure | observation | privileged
ResourceSelector   { kind, pattern }        + includes(a,b): total, denies unknown pairs
EffectDescriptor   { verb, sinkClass, selector, args, argsDigest, idempotencyKey,
                     riskTier, provenance }
CapabilityGrant    { grantId, principal, descriptorDigest, selector, constraints,
                     expiry, parent, maxUses }
Receipt            { grantId?, outcome: ok|failed|undeterminable, observedAt, resultDigest }
BudgetVector       { tokens, wallClock, cost, effects, evaluations, depth }
Lease              { leaseId, parent, remaining: BudgetVector, expiry }
EventEnvelope      { seq, at, kind, episodeId?, processId?, causationId, correlationId,
                     payload, provenance, dataPolicy, tenant }
Artifact           { artifactId, kind, class, compensatesFor?, hypothesis,
                     evidenceRefs, invalidationConditions[], riskDelta }
Claim              { subject, predicate, value, protocol, evaluator, environmentProfile,
                     substrateProfile, uncertainty, validity, invalidationConditions[] }
CorrectionRecord   { episodeId, proposedPatchDigest, acceptedPatchDigest,
                     reasonCodes[], magnitude, scope }
Recording          { modelCassetteDigest, imageDigest, envSnapshotDigest, seed, clockPolicy }

ProcessDefinition  { definitionDigest, states[], transitions[], approvalPoints[],
                     boundEffectVerbs[] }     // an Artifact of kind `process_definition`
ProcessInstance    { processId, definitionDigest, currentState, pendingApprovals[],
                     history[] }              // resumable from the ledger alone

EpisodeState
reduce(State, Event) -> State                 // reduces BOTH episodes and processes
```

**`ports/` inventory (GTS-13C §5.2) — interfaces only, two implementations each:**

```
ModelPort        propose(ContextBundle, ToolSchemas, Sampling) -> Proposal
EnvironmentPort  observe(Selector) -> Observation      // snapshot-bound, never a live handle
                 effect(Grant?, Descriptor) -> Receipt // Grant required iff privileged
EvaluatorPort    evaluate(RunRef, Protocol) -> Verdict | Inconclusive
EventStorePort   append(Event[]) / read(range) / digest()
BlobStorePort    put(bytes) -> Digest / get(Digest)
IndexPort        query(Query) -> RankedRefs
ClockPort        now()          // determinism seam — never call the system clock directly
RandomPort       next()         // determinism seam
```

> **No `ProcessPort` and no `ToolPort`.** A process advances by reading events and emitting effects; a tool
> *is* an effect.

**`kernel/` contents:** `grants` · `attenuation` · `policy` · `budget` · `dispatch` · `provenance`. **Nothing
else.** Tracked LOC budget with an alarm; an ADR per change. Only `privileged` effects reach it. Both
episodes and processes authorise through it; **there is no second dispatch path.**

**`agency/` vs `governance/`:**

| Package | Holds | Explicitly does not hold |
|---|---|---|
| `agency/` | `episode` (recursive coordinator) · `context` (layered compiler) · `operators` · `playbooks` | **Declared state machines. Approval logic. Release logic** |
| `governance/` | `process` (definition loader, instance advancer, approval blocking, restart resume) | **Any model call. Any open-ended control flow** |

**Isolation topology (MVP):**

| Trust domain | MVP | Enforced by |
|---|---|---|
| Interaction · Cognition · Control · Governance | One process | Module boundary + architecture test |
| **Workload** | **Separate process, identity, namespace** | OS |
| **Evidence** | **Separate process, identity, image digest** | OS |
| Evolution | **No runtime component** | Human action |

### 9.18 GTS-13C locked concepts (`L-01` … `L-18`) and open concepts (`O-01` … `O-11`)

| # | Locked concept |
|---|---|
| `L-01` | The evaluator is unreachable from everything it judges |
| `L-02` | Authority is **resource-scoped**, never verb-scoped |
| `L-03` | A guarantee may not exceed the boundary that actually enforces it |
| `L-04` | Every claim carries non-empty invalidation conditions, **enforced at parse** |
| `L-05` | Promotion moves an activation pointer; it never overwrites a running component |
| `L-06` | Rollback is tested **before** the promotion it protects |
| `L-07` | `inconclusive` is first-class, excluded from **both** numerator and denominator |
| `L-08` | Comparisons are paired; effects reported with intervals; families pre-registered and hashed |
| `L-09` | No self-authored evaluation criteria; no scalar reward; novelty observed, never optimised |
| `L-10` | No runtime workflow graph governs **open-ended agentic control flow**. This does **not** prohibit a durable state machine for approvals, releases and governance |
| `L-11` | Registries freeze at composition **per episode**; **signed discovery between episodes is permitted** |
| `L-12` | Every mutable component declares `enforcement` or `compensation` + its **expiry hypothesis** |
| `L-13` | Coding is the first environment, not the ontology |
| `L-14` | Biological, cosmological and physical analogies are non-normative |
| `L-15` | Default tools are typed; shell is a selector-scoped fallback; **`vg-shell-only` retained permanently** |
| `L-16` | The Active MVP Contract gates every merge at **100% test-or-justification** |
| `L-17` | **All effects are recorded; only `privileged` sinks are capability-mediated** |
| `L-18` | **Tools execute typed effects; Episodes coordinate open-ended work. A tool is not an Episode** |

| # | Open concept | Design when |
|---|---|---|
| `O-01` | Competence graph lifecycle (promotion/demotion/activation topology) | One distilled artifact clears the A/A floor. **Derive the lifecycle from the survivor** |
| `O-02` | Semantic memory and consolidation schedule | A corpus exists and retrieval value is measurable |
| `O-03` | General subagent composition beyond operator invocation | A real task needs depth the operator mechanism cannot reach |
| `O-04` | Model routing policy | Two providers are live and a cost/quality frontier is measurable |
| `O-05` | Search over trajectories, process rewards, reflection | Deferred as capability; **their contracts land now** |
| `O-06` | Training on the corpus | Opt-in, licensing, per-instance contamination tracking, adversarial verifier audit all exist |
| `O-07` | Autonomous promotion of any class | Measured false-promotion and rollback rates acceptable. **Never for kernel or evaluator** |
| `O-08` | Multi-tenant isolation and enterprise policy | A second tenant exists |
| `O-09` | Graphical authoring canvas | Users ask to *edit* a rendered trajectory |
| `O-10` | Cross-domain artifact portability classes | Two environments have produced artifacts worth comparing |
| `O-11` | Process-definition authoring surface | More than three governance processes exist |

**None of the open concepts generate Active MVP Contract rows.**

### 9.19 Where every capability lives (the falsification test for the abstraction)

**Anything fitting none of these columns means the spine is wrong.**

| Capability | Adapter behind a port | Artifact in the graph | Policy parameter |
|---|---|---|---|
| Tools, scripting, files | Environment adapter | Tool schema + description | Risk tier, sink class |
| Browsing, research, sensors | Environment adapter | Retrieval policy | Egress scope |
| LLMs (primary + auxiliary) | Model port, n providers | Routing policy | Budget vector |
| Short/long-term knowledge | Store adapter (4 stores) | Write + consolidation policy | Retention |
| Indexing, search, cache, compression | Index adapter | Context compiler | Token budget |
| Context | — | Context compiler (versioned, evaluated) | Layer budgets |
| Cognition, planning, decomposition | — | Operators | Activation set |
| Reflection | — | Operator emitting a **candidate Claim** | Rigidity |
| Methodologies, workflows | — | Playbooks (agentic) · **Process definitions (governance)** | Selection policy |
| Approvals, releases, compliance | — | **Process definition** | Approval points |
| Skills | — | Artifact | Scope |
| Harness engineering | — | *Editing the artifact graph* | Tier 1/2/3 |
| Loop engineering | — | *Editing episode-policy artifacts* | — |
| Learning | Offline optimiser reading the ledger | Emits candidate Artifacts | Promotion gate |
| Evaluating, judging | **Evaluator — outside, unreachable** | Emits Claims | Sealed set |
| Integrations, comms (MCP/ACP/HTTP) | Protocol adapter | Tool schemas | Trust level |

### 9.20 Sprint schedule (GTS-13C Part II)

Two-week sprints, half-sprint milestones (a/b) where a dependency would otherwise be unsatisfiable.
Complexity: **S** = days · **M** = ~1 sprint for one dev · **L** = ~1 sprint for a pair · **XL** =
multi-sprint · **⚠** = high design risk.

| Sprint | Deliverables |
|---|---|
| **S0** | `T11.1`–`T11.6` four executable artifacts (L ⚠); `T0.1`–`T0.6` schema archaeology (M ⚠); `T10.1`–`T10.3` repo, CI, boundaries (S) |
| **S1a** | `T0a.1`–`T0a.3` provider API spike (S); `T1.1`–`T1.6` wire schema v0.1 (L ⚠) |
| **S1b** | `T1.7`–`T1.12` envelope, artifact, claim, correction, recording, process (L) |
| **S2a** | `T0b.1`–`T0b.4` end-to-end disposable slice (M ⚠); `T7.1`–`T7.3` artifact graph + manifest, *moved from S7* (L ⚠); `T3.1`–`T3.5` event store & reducer (M); `T2.1`–`T2.5` capabilities & budgets (L ⚠) |
| **S2b** | `T1.13`–`T1.15` reader profiles + migration (M); `T7.4` `vg-shell-only` permanent baseline (S) |
| **S3** | `T2.6`–`T2.10` dispatch & sink-class mediation (L ⚠); `T3.6`–`T3.8` recovery & cassettes (L) |
| **S4** | `T4.1`–`T4.7` episode engine + recursion — **trust-spine demo, scripted trajectory with no model at all** (XL ⚠); `T4.8` process engine (M ⚠); `T5.1`–`T5.2` worker perimeter (L ⚠) |
| **S4 gate** | **DELETE `spike/` + `slice/`** — absence verified in CI |
| **S5** | `T5.3`–`T5.6` evaluator identity (L); `T4.9`–`T4.11` context compiler + competence estimate (M) |
| **S6** | `T6.1`–`T6.3` Git env + typed tools (L); `T6.4`–`T6.8` CLI, approvals, corrections, latency (L ⚠) |
| **S7** | `T7.5`–`T7.7` `vg harness` + reconstructions (XL ⚠); `T8.1`–`T8.2` A/A floor + paired runner (M) |
| **S8** | `T8.3`–`T8.6` statistics, splits, oracles (L ⚠); `T8.7`–`T8.8` meta-evaluator + sabotage (L ⚠); `T9.1`–`T9.3` non-coding environment (L ⚠) |
| **S0→S8** | `T10.4`–`T10.9` continuous — 100% Active MVP Contract coverage; margins alarmed (M) |
| **S9** | **MVP gate review** — go/no-go on the four gate questions |

### 9.21 Test doctrine — six families (GTS-13C Ch. 8)

| Family | Proves | Example |
|---|---|---|
| **Must-fail** | The control can fail | Verb-only attenuation reads the evaluator bundle; a `privileged` effect declared `pure` is accepted |
| **Architecture** | A path does **not** exist | Nothing imports `spike/` or `slice/`; no route from `agency` to `adapters/evaluators`; `governance/` has no model dependency; `agency/` has no approval logic |
| **Property** | An algebraic law holds | Attenuation monotone; budget conserved; selector inclusion transitive; process resumes to the same state |
| **Conformance** | Two implementations agree | Golden canonicalisation triples across both readers |
| **Fault injection** | Every failure path recovers | Crash at each dispatch stage |
| **Adversarial** | The threat model is real | Injection, escalation, exfiltration, memory poisoning, descriptor substitution |

Plus two statistical families that are **not** unit tests: **A/A** (noise floor) and **paired comparison**
(effect estimation).

### 9.22 Margins — carried and alarmed

| Margin | Alarm at | Why |
|---|---|---|
| TCB size | Budget exceeded | Logic belonging in cognition has leaked into the kernel |
| p95 time-to-first-token | Budget exceeded | The product becomes unpleasant and dogfood collapses |
| p95 time-to-first-effect | Budget exceeded | Governance has reached the interactive path |
| Context tokens per turn | Budget exceeded | The compiler is padding |
| Schema extension slack | Below threshold | The next contract change becomes a migration |
| **Active MVP Contract coverage** | **Below 100%** (test or justification) | **Blocks all new normative rules** |
| Substrate debt | Above threshold | The activation set has become a set of assumptions |
| Verifier–deployment gap | Widening | **Freezes automated promotions** |

> **A margin with a hard limit gets gamed. A margin with an alarm gets discussed.**

### 9.23 The MVP gate — four questions (GTS-13C Ch. 10)

1. **Is the boundary real?** Red team reaches neither control plane, evaluator, nor secrets. Every must-fail
   test fails against its broken counterpart. Kill and restart preserve the distinction between known and
   uncertain. `spike/` and `slice/` are gone.
2. **Is it useful?** Three real bugs in a repository someone knows well, fixed interactively without
   hand-patching mid-run. Then honestly: *next time, would you reach for it?*
3. **Is it measurable?** An A/A floor exists per task class, computed against `vg-shell-only`. A paired
   comparison runs. **The verifier–deployment gap has a number.**
4. **Is it general?** The non-coding environment was added with **zero episode-engine changes**.

**Recorded gate status at `0238b1a`** (`ADR-0064`): Q1 partially met and regressed · Q2 not demonstrated ·
Q3 not met · Q4 not met. Closing sprints: Q1→S7, Q2→S9, Q3→S9, Q4→S10.

### 9.24 How the MVP grows itself — four stages

1. **The ledger accumulates** — episodes, processes, effects of every sink class, receipts, verdicts, correction deltas. No learning; the corpus is the asset.
2. **The corpus becomes attributable** — artifact graph populated from S2 plus counterfactual re-execution makes *which component caused this* answerable.
3. **Attribution becomes proposal** — the offline optimiser clusters failure modes and proposes Tier-1 edits (prompts, skills, retrieval, context, routing), each with a **declared prediction**; predictions verified against next-round outcomes give the **progressive-vs-degenerating ratio**.
4. **Proposal becomes structure** — **plateau is the observable form of "my representation is inadequate"**; at plateau the system proposes a representation it was not given.

The coordination hierarchy — agents → teams → departments — is **discovered**, not built.

### 9.25 The Active MVP Contract (GTS-13C Ch. 15)

**Shape:** `req_id` (e.g. `REQ-KRN-014`) · `statement` (one sentence, testable as written) · `source` (Part I
task + v4 rule) · `component` (the package that implements it) · `owner` (a person, not a team) · `test`
(identifier, or `untestable-with-justification:<reason>`) · `test_family` (one of the six) ·
`acceptance_evidence` · `status` (`open` · `covered` · `justified`).

**What enters:** product requirements (observable behaviour of the shipped system); assurance requirements
(a boundary, an invariant, a failure mode, a recorded property); anything a PR could regress; series tagged
**[C]**.
**What stays in the issue tracker:** management tasks; research tasks; anything with no code artifact to
regress; series tagged **[B]**. **Rows for deferred capability (Ch. 3) never enter.**

**Rules:** every PR cites at least one `req_id` (a PR citing none is rejected **by CI, not by a reviewer**);
a row is `covered` only when its named test exists and passes; `justified` requires a written reason **and a
compensating assurance** using the three untestable classes; coverage is generated into a report each CI run;
**no PR merges to main until this contract exists and the baseline is tagged**.

### 9.26 Standing programme risks (GTS-13C Ch. 14)

Specification capture (new normative rules outpace tests) · Nobody dogfoods (no real bug attempted by
mid-S6) · Latency collapse · TCB growth · **Disposable becomes architecture** (*the argument to keep it is
the signal to delete it faster*) · Reward hacking (seeded sabotage passes) · Statistical noise as signal ·
Baseline manifest deleted as "dead code" · Ontology rigidity (a new capability needs a new layer) ·
Process/episode confusion (approval logic appears in `agency/`) · **Mediation drift** (a `privileged` effect
declared `pure`) · Contract inflation · Conway drift · A special case appears.

---

## 10. Engineering Handbook Principles (VG-01)

VG-01 states nothing normative — every rule in it belongs to another document — but it is the practice layer.

### 10.1 Mental models (`M1` … `M11`)

| # | Model |
|---|---|
| `M1` | **The episode is the program.** There is no workflow engine, no topology language, no graph validator. Declaring a shape for the work *before* the work runs is building the thing VG-03 §2 rejected |
| `M2` | **Everything pluggable is one of exactly four things** — observation source, cognitive operator, effect adapter, evaluator. A fifth is a design review, not a pull request |
| `M3` | **The broker grants; the sandbox contains.** The broker decides *whether* an effect is permitted; the perimeter decides *what an attacker can reach when the broker was wrong* |
| `M4` | **Content carries provenance; provenance constrains authority.** Untrusted content may **inform** work but never **authorise** a capability-widening action. *This control is easy to implement in a way that looks correct and does nothing. It has happened twice* |
| `M5` | **The verifier is outside everything.** Nothing the system can modify may judge the system |
| `M6` | **A gate that cannot fail is not a gate.** Its twin: **a requirement that cannot be satisfied is not a requirement** |
| `M7` | **Competence is the persistent object** — an immutable graph of artifacts with an evidence graph saying where each holds and what would refute it |
| `M8` | **One document is normative per contract.** The same rule in two places is a defect; delete the copy |
| `M9` | **Minimise what must be simultaneously correct before the first signal.** *How many things must be simultaneously correct before anything tells us we are wrong?* **Standing exception:** the kernel, verifier and capability boundary stay at full rigor |
| `M10` | **Polyglot plugins outside the TCB (the Narrow Waist Wire Law).** The microkernel and state ledger are minimal, deterministic and language-neutral in wire representation. Domain computation (Tree-sitter indexing, browser automation, microVM sandboxes, vector engines) or plugins in Rust, Go, TypeScript/Node or Python must execute **strictly outside the TCB**, communicating across port boundaries via standard wire contracts (stdio, JSON-RPC, IPC, Unix domain sockets). **The TCB never imports an external plugin runtime** |
| `M11` | **The Generality Falsification Invariant.** The core loop and microkernel must remain **100% agnostic to task domains**. Coding is merely a configuration manifest (`vg-code-default`). Adding a research, legal, medical or robotics task must require **zero lines of code modified** in the kernel package or the episode engine |

### 10.2 SOLID, concretely

**Single responsibility** — the assembler builds a prompt and does not fetch, dispatch or decide; the
governor accounts for budget and holds no opinion about policy; a tool executes one effect. *The smell:* you
cannot name the module's job in one clause without "and".

**Open/closed** — adding a capability is a registry entry plus a configuration line. The loop, the dispatcher
and the schemas do not change.

**Liskov substitution** — every implementation of a port is interchangeable **including in its failure
behaviour**:

| Port | Substitutability contract |
|---|---|
| `ModelProvider` | **Never throws for a provider-side failure**; returns an instrument error |
| `EvaluatorPort` | **Never throws.** Cannot verify implies **inconclusive**, never a pass |
| `SandboxRunner` | The containment report reflects reality. A runner claiming containment it lacks **is lying** |
| `EnvironmentAdapter` | Returns a **typed result for every outcome**, including denial |

**Interface segregation** — ports are small and role-specific. Ten narrow interfaces, not one runtime
god-object.

**Dependency inversion** — kernel and cognition depend on ports, never on adapters. Only the composition root
knows concrete implementations, and it knows them for exactly one function call. Enforced mechanically by the
boundary gate and by `AT-01`/`AT-06`, **never by discipline**.

**DRY applies to knowledge, not to text that happens to look similar.** Genuinely DRY: provenance labels
declared once per source class; canonicalisation implemented once per language driven by shared vectors; one
definition of the patch (the environment's own diff). Harmful: a shared base class three unrelated tools
inherit for two helper methods; merging `read` and `glob` because both touch the filesystem; a generic effect
handler with a kind switch (that is the dispatcher, and it already exists).

### 10.3 The shape of a change

```
1. UNDERSTAND    Which layer? Which document says what the behaviour should be?
2. WRITE THE TEST FIRST   ...and watch it fail. If it passes, you misunderstood.
3. SMALLEST CHANGE        Make the test pass. Nothing else.
4. CHECK THE BOUNDARY     Did you touch a layer you did not intend to?
5. ADR?                   Would this decision otherwise be tribal knowledge?
6. COMMIT                 The message says WHY. The diff says what.
```

**Step 2 is not negotiable.** **Watching a test fail first is the only evidence that it tests anything.**
Commit messages carry three things — what layer, why, and what proves it (including the broken counterpart
the test fails against).

### 10.4 Testing taxonomy — seven kinds

| Kind | Answers | Speed |
|---|---|---|
| Unit | Does this function do what it says? | ms |
| Property | Does this algebraic law hold for arbitrary inputs? | ms |
| Vector | Do the implementations agree byte-for-byte? | ms |
| Must-fail | Can this control actually fail? | ms |
| Fault injection | Does every failure path in `05 §2.3` behave as specified? | ms |
| Cassette | Does the harness still behave as on this recorded real interaction? | seconds |
| Live canary | Do real models emit what our parsers expect? | slow, costs money |

**Mock / cassette / live.**

| Path | Answers | Cannot answer |
|---|---|---|
| Mock | Given a known output, does the harness do the right thing? | Whether a real model would emit that output |
| Cassette | Does behaviour still match this recorded interaction? | Anything about a prompt that just changed |
| Live canary | Do real models emit what our parsers expect? | Anything cheap, fast or deterministic |

**Canary rules:** asserts **wire shape, never task outcome**; pre-merge only; deselected from the inner loop.
A task failure in a canary is **not** a gate failure.

**The satisfiability check.** Before writing a test, ask whether the requirement is physically achievable. If
the only implementation that passes is a mock of the failure mode, **the requirement is wrong**.

**What not to test:** schema libraries doing what they do; getters, constructors and trivial delegation;
adapter internals the port contract already pins. **A test that has never failed and cannot fail is a
maintenance cost with no benefit. Delete it.**

### 10.5 Practices and working agreements

Parse at the boundary, never cast · Fail at composition, not at first use · Make illegal states
unrepresentable · Trajectory over logging (`vg trace <runId>` beats a print statement) · Cassettes for the
inner loop.

**Working agreements:** trunk-based with short-lived branches; every fix ships with a test proven to fail
against pre-fix code; kernel changes get a second pair of eyes; an ADR when a decision would otherwise be
tribal knowledge; **no status document** — the ticket table is the status; and weekly, thirty minutes,
three questions: what merged, what is blocked, **has anything changed our mind about `02`–`07`?**

### 10.6 Review checklist

1. Does the change touch only the layer it should?
2. Is there a test, and was it watched failing first?
3. Does a new capability touch the loop or the dispatcher? If so, why?
4. Does any new external data acquire its type by cast rather than parse?
5. Does any new failure path leave a lease held?
6. Does a new source declare its provenance label **at the class, not the call site**?
7. **Are there special cases?** A conditional naming one environment, one provider or one task type is the generality constraint failing quietly
8. If a rule changed, does its entry in the rule-to-test map still hold?

### 10.7 ADR format

Decision, context, alternative rejected, **reversal condition**, status. **State the losing alternative
fairly enough that its advocate would recognise it.** Write one when a competent engineer arriving in six
months would be surprised and unable to reconstruct why.

### 10.8 Repository layout (VG-01 §8)

```
vanguard/
├── packages/
│   ├── wire-schema/       schemas, semantic rules, vectors, reader profiles
│   ├── domain/            pure types and reducers, no I/O
│   ├── ports/             interfaces only
│   ├── policy-kernel/     capabilities, grants, budgets, dispatch
│   ├── controller/        episode lifecycle and recovery
│   ├── agency/            the loop, context assembly, playbooks
│   ├── adapters/
│   │   ├── environments/  git, tableworld
│   │   ├── operators/     model, deterministic
│   │   ├── evaluators/    coding, tableworld
│   │   └── stores/        event store, blob store, export
│   ├── runtime/           composition root and daemon
│   └── cli/               vg run, vg trace
├── lab/                   offline; consumes exports only
├── schemas/v4/            normative artifacts and golden vectors
├── docs/
│   ├── v4/                the document set + generated rule-test map
│   └── adr/               append-only from day one
├── test/broken/           deliberately broken implementations
└── tools/                 wordcount, audit, reader-profile, rule-test-map
```

**Dependency direction is enforced, not documented:**
`domain ← ports ← kernel ← agency ← runtime → adapters`, `cli → runtime`.
`lab/` imports nothing and is imported by nothing.

### 10.9 Glossary

| Term | Meaning |
|---|---|
| **Episode** | The unit of execution: task, snapshot, activation set, budget, policy |
| **Effect** | Anything that changes state outside the process, or reads from outside it |
| **Descriptor** | The canonical digest of a call; input to loop detection, policy caching and grant binding |
| **Grant** | A scoped, expiring authorisation binding a principal, actions, resources and a purpose |
| **Attenuation** | Deriving a child authority that is a subset of its parent's |
| **Lease** | A reservation against a budget dimension, released on every path |
| **Provenance** | Six orthogonal axes describing where content came from and what it may do |
| **Context block** | The only type admissible into context assembly |
| **Operator** | A versioned artifact producing a proposal; data, not control flow |
| **Playbook** | Methodology as data, with a rigidity dial |
| **Competence artifact** | An immutable, content-addressed node in the competence graph |
| **Evidence claim** | A scoped assertion with validity, uncertainty and invalidation conditions |
| **Activation set** | The artifacts valid for the current context |
| **Instrument tuple** | The complete configuration that produced a result |
| **A/A floor** | The variance of a configuration compared against itself |
| **Containment report** | What the perimeter actually enforced, probed rather than asserted |
| **Inconclusive** | The instrument did not work. **Never a task verdict** |
| **Candidate** | A proposed successor artifact with no operational authority |

### 10.10 The ten rules

1. One path from a proposal to an effect. Never a second.
2. Untrusted content informs; it never authorises.
3. The verifier is outside everything you can change.
4. A gate that cannot fail is not a gate.
5. A requirement that cannot be satisfied is not a requirement.
6. Parse at the boundary; never cast.
7. Fail at composition, not at first use.
8. Release the lease on every path, including the one you did not plan for.
9. If a rule appears in two documents, delete one.
10. If it needs a special case, the abstraction is wrong — or you are about to lose the general system to the coding track.

---

## 11. Convergence Evidence & Vision Annex (VG-11, VG-12)

### 11.1 Independent design convergence (VG-11) — EVIDENCE, secondary

**Evidentiary status.** This is a **secondary** account. The primary artifacts (the two independent design
reviews as written) are **not preserved in the v4 set and were not available when the summary was compiled**.
No claim of verbatim preservation is made.

Two design lineages were produced independently from a shared problem statement — one approaching from
execution mechanics, the other from competence and evaluation. **Convergent conclusions:**

1. A static workflow graph is the wrong runtime substrate; an agent loop that can invoke an agent loop is strictly more expressive.
2. Every effect must pass a single authorisation point, structurally incapable of being bypassed.
3. The evaluator must be unreachable from everything it judges, or every downstream number is worthless.
4. Measurement apparatus is not optional infrastructure — without it, improvement claims are unfalsifiable.
5. Instrument failure is not task failure; collapsing them corrupts every comparison.
6. The trajectory is the substrate, not a debugging side effect.
7. Extensions must resolve at composition and then freeze; runtime discovery is an unaudited capability.
8. A control that has never been observed failing is not known to work.

> **Convergence is not validation.** Two designs sharing an author's influences, a problem statement and a
> literature will converge for reasons other than correctness. What it supports is a narrower claim: these
> eight conclusions are not idiosyncratic to one line of reasoning.

**Divergences and their resolutions:**

| Divergence | Resolution |
|---|---|
| Interface definition: validator-first vs schema-first | **Schema-first** (`ADR-0008`) |
| Permission model: verbs vs verbs plus resources | **Resources are mandatory** (`ADR-0011`) |
| Promotion: scalar objective vs partial order | **Partial order over a frontier** (`ADR-0015`) |
| Competence store: array vs graph | **Graph** (`ADR-0017`) |
| Trusted-base scope: policy kernel vs transitive dependencies | **Both, declared separately** (`ADR-0023`) |
| Storage: append-only files vs a transactional store | **Transactional, with export** (`ADR-0010`) |
| Memory gating: verdict-gated vs staged pipeline | **Staged** (`ADR-0030`) |

### 11.2 Vision annex (VG-12) — NON-NORMATIVE

> **Not a specification. No ticket may cite this document.**

The annex exists as a **quarantine**: metaphor in a specification is unfalsifiable, and unfalsifiable
statements in a normative document cannot be adjudicated when two people read them differently.

**The project in one sentence:** a system that measurably improves its own harness under an evaluator it
cannot game, in a domain where verification is cheap enough to run constantly.

**Analogies, each with its stated failure point:** *the organism* (breaks at: biology has no verifier) ·
*the laboratory* (breaks at: instruments do not modify themselves between trials) · *the operating system*
(breaks at: the most dangerous input arrives as **content**, not as a call — hence `REJ-09`) ·
*the apprentice* (breaks at: calibrated abstention is a research problem, not a default).

**How the other sciences are used (GTS-13C Ch. 12)** — imported as **mechanism with a falsifiable
prediction**, never as module names. Legitimate imports: least privilege, attenuation, unforgeable tokens
and namespace isolation (capability security / OS); **falsifiability as a required schema field**, Lakatos
hard-core/protective-belt as the mutability partition, **progressive-vs-degenerating as a measured ratio**
(philosophy of science); pre-registration, pairing, family correction, MDE, A/A floors (replication crisis);
fast episodic store / slow consolidated store, offline interleaved replay, forgetting as competition (CLS);
**competence estimate recorded pre-action and scored post, Brier score as an alertable metric**
(metacognition); Pareto/QD archives and the failure of scalar fitness (evolutionary computation); estimated
state, bounded actions, stop rules, rate limits, rollback (control theory); EV-gated exploration, cost per
verified change, two-clock queueing (economics). Illegitimate: any of the above rendered as a module name.

---

## 12. Appendix — Internal Contradictions & Ambiguities in the Corpus

Recorded for downstream drift analysis. These are conflicts **within the specification corpus itself**, not
observations about implementation.

### 12.1 Load-bearing contradictions

| # | Contradiction | Where |
|---|---|---|
| **X-01** | **Universal mediation vs. sink-class mediation.** `A-03` ("Effects are authorised before a capability is issued") and `05 §2.1` ("The dispatch sequence is the single execution path for **all** effects") vs. `T2.8` / `ADR-0051` / `L-17` ("only `privileged` sinks are capability-mediated; `pure` and `observation` do not traverse the kernel"). GTS-13C is non-normative, but `ADR-0051` is a decision record and decisions bind. The normative VG-02/VG-05 text was never amended | `02 [A-03]`, `05 §2.1`, `ADR-0051`, GTS-13C `T2.8`, `L-17` |
| **X-02** | **Observation requires a grant, or does not.** `EnvironmentAdapter.observe(req, grant: CapabilityGrant)` (VG-03 §7.1) and VG-03 §6.1's re-grounding comment ("It is authorised like any other effect … there is no unauthorised read") vs. `EnvironmentPort.observe(Selector) -> Observation` (GTS-13C §5.2, no grant parameter) and `T2.8` (`observation` is selector-checked but not grant-mediated) | `03 §6.1`, `03 §7.1`, GTS-13C §5.2, `T2.8` |
| **X-03** | **`A-01` "the episode is the only execution primitive" vs. durable state machines.** `A-01`'s enforcement clause says *"No workflow engine, topology language, graph validator or node registry exists in the tree"*; `ADR-0050`/`L-10`/`T4.8` introduce `ProcessDefinition`/`ProcessInstance` with declared states, transitions and a process engine, and a `governance/` package. `L-10` carves out the exception; `A-01` was never amended, and `governance/` appears in **no** VG-03 plane or `LT-*` layer contract | `02 [A-01]`, `03 §3`, `03 §4`, `ADR-0050`, `L-10`, GTS-13C §5.4 |
| **X-04** | **Terminal-state vocabularies conflict.** VG-03 §6.2 keeps run termination and evaluation outcome on **separate axes** (`completed/abstained/escalated/cancelled/budget_exhausted/instrument_error/runtime_error/abandoned` vs `satisfied/unsatisfied/partially_satisfied/inconclusive/invalid_evaluation`). GTS-13C `T4.5` collapses them into one list (`resolved/abandoned/denied/inconclusive/abstained/recovered`) — the exact collapse VG-03 §6.2 forbids. **`ADR-0057` resolves in VG-03's favour**, but both texts remain | `03 §6.2`, `T4.5`, `ADR-0057` |
| **X-05** | **Provenance axis count is stated three different ways.** VG-04 §3.1 defines **six** axes (`origin`, `instructionAuthority`, `integrity`, `confidentiality`, `epistemic`, `influence`); `N-09` lists **five** (omits `influence`); `REJ-06` says a single lattice "conflates **five** independent questions"; `T2.9` lists **four** and renames them (`origin`, `integrity`, `sensitivity`, `trust`) | `04 §3.1`, `02 [N-09]`, `REJ-06`, `T2.9` |
| **X-06** | **`ResourceSelector` kinds are disjoint between specs.** VG-04 §5.2: `fs`, `network`, `secret`, `git`, `table`, `browser`, `generic` (each with a bespoke shape and inclusion relation). GTS-13C `T1.3`/§5.1: `path`, `glob`, `command`, `host`, `record` with a uniform `{kind, pattern}` shape. The harness manifests use `glob` and `command`. `CT-52`'s per-kind inclusion table covers only the VG-04 set, so the GTS-13C kinds have **no defined inclusion relation** and would be denied under `CT-52`/`K-48` | `04 §5.2`, `04 §5.3.1`, `T1.3`, GTS-13C §5.1, §7.1 |
| **X-07** | **`CapabilityGrant` shape differs.** VG-04 has `actions: ActionId[]`, `resources: ResourceSelector[]` (plural), `constraints{expiresAt, maxUses, maxBytes, maxEffects, budgetLeaseId, environmentSnapshot, networkPolicy, requirePreview, requireApprovalAboveRisk}`, `purposeDigest`, `parentGrantId`, `approvalRef`, `authenticator`. GTS-13C `T1.5` has `{grantId, principal, descriptorDigest, selector (singular), constraints, expiry, parent, maxUses}` — **no `actions`, no `purposeDigest`, no `authenticator`**. `N-03` requires purpose on every capability | `04 §5.2`, `02 [N-03]`, `T1.5` |
| **X-08** | **`EventEnvelope` shape differs.** VG-04 §12.1 uses a `scope` discriminator (`episode\|governance\|evolution\|recovery`) plus `runId?`, `episodeId?`, `branchId?`, `traceId`, `spanId`, `seq`, `occurredAt`/`recordedAt`, `principal`, `tenantId`, `ownerId`, `confidentiality`, `retentionClass`, `trainability`, `redactionStatus`, `encryptionKeyRef?`, `environmentSnapshot?`. GTS-13C `T1.7` uses `{seq, at, kind, episodeId?, processId?, causationId, correlationId, payload, provenance, dataPolicy, tenant}` — introduces `processId` (a concept VG-04 does not model), drops `scope`, `branchId`, `traceId`/`spanId`, `ownerId`, and the split occurred/recorded timestamps | `04 §12.1`, `T1.7` |
| **X-09** | **Port rosters differ.** VG-04 §13: `ModelProvider`, `EnvironmentAdapter`, `OperatorRunner`, `EvaluatorPort`, `EventStore`, `BlobStore`, `ObservationSource`, `PolicyEngine`, `Governor`, `SandboxRunner`. GTS-13C §5.2: `ModelPort`, `EnvironmentPort`, `EvaluatorPort`, `EventStorePort`, `BlobStorePort`, `IndexPort`, `ClockPort`, `RandomPort`. Only `EvaluatorPort` is named identically. `IndexPort`, `ClockPort`, `RandomPort` are new; `OperatorRunner`, `ObservationSource`, `PolicyEngine`, `Governor`, `SandboxRunner` are absent from GTS-13C despite being referenced by `K-03`/`K-07`/`AT-04`/`K-42` | `04 §13`, GTS-13C §5.2 |
| **X-10** | **Three repository layouts.** VG-03 §4 (`clients/`, `runtime/`, `agency/`, `kernel/`, `ports/`, `domain/`, `adapters/`, `lab/`); VG-01 §8 (`packages/wire-schema/`, `domain/`, `ports/`, **`policy-kernel/`**, **`controller/`**, `agency/`, `adapters/{environments,operators,evaluators,stores}`, `runtime/`, **`cli/` inside packages**, `lab/`); GTS-13C `T10.1` (adds **`governance/`**, `spike/`, `slice/`, and `cli → runtime`). `kernel/` vs `policy-kernel/` and `clients/` vs `cli/` are unreconciled | `03 §4`, `01 §8`, `T10.1` |
| **X-11** | **Split taxonomy differs.** VG-07 §5.7 defines three splits (`DEV`, `HOLDOUT`, `SEALED`); GTS-13C `T8.5` defines five (`DEV`, `HOLDOUT`, `SEALED`, `LIVE`, `DEPLOYMENT`). `M-19`/`M-20` are written against the three-split model | `07 §5.7`, `T8.5` |
| **X-12** | **Statistics strategy.** `M-03` names McNemar's exact test as *the* test; `T8.3` states **"McNemar alone is not a statistics strategy"** and adds paired bootstrap/permutation, survival methods and hierarchical models. Not strictly contradictory, but `M-03` is normative and narrower than the programme plan assumes | `07 [M-03]`, `T8.3` |
| **X-13** | **Principal enumerations differ.** `N-07` names four surfaces (control plane, worker, evaluator, updater); `05 §2.1` names two kernel-ingress principals (`Principal::Episode`, `Principal::EvidencePlane`); `T2.1` names six (`user`, `operator`, `episode`, `process`, `evaluator`, `release`); `AT-11` names three Phase 0 identities (controller, worker, evaluator). The VG-05 audit checklist item 9 asks about **"the four planes"** while VG-03 §3 defines **six** | `02 [N-07]`, `05 §2.1`, `05 §10`, `AT-11`, `T2.1` |
| **X-14** | **Budget vector dimensions differ.** VG-04 §6: cost, tokens, wall-clock, turns, depth, concurrency (+ `EvaluationBudget`). GTS-13C `BudgetVector`: `{tokens, wallClock, cost, effects, evaluations, depth}` — adds `effects`, drops `turns` and `concurrency` | `04 §6`, GTS-13C §5.1 |
| **X-15** | **`DEF-12` vs. `K-13`–`K-17`.** `DEF-12` defers "approvals, suspension and session resume" while VG-05 §2.5 specifies the full suspension protocol normatively (`K-13`…`K-17`, `F-07`, `F-08`) and VG-03 §3 gives the Interaction plane approval semantics. `ADR-0057` partially supersedes `DEF-12` for privileged apply, leaving general suspension deferred while normative rules for it already exist | `DEF-12`, `05 §2.5`, `ADR-0057` |

### 12.2 Ambiguities and undefined terms

| # | Ambiguity |
|---|---|
| **Y-01** | **The provenance label enum is never defined.** `K-28`–`K-33` refer to labels — `untrusted`, `untrusted-derived`, `untrusted-external`, `agent-originated` — and to labels "improving"/"lowering", but no document defines the ordered label set, its ordering, or its schema type. `CT-21`–`CT-23` enforce *where* labels are declared, not *what* they are |
| **Y-02** | **The policy-kernel size ceiling has no number in any normative document.** `C-07`, `K-02`, `AT-08` and the `tcb-size` CI gate all reference a "declared size ceiling"; the only numbers appear in ADRs (`ADR-0054`: 1,307 logical SLOC baseline with a 131-line review alarm; `ADR-0067` cites `1333/1438`) |
| **Y-03** | **"Attenuation Kernel" is not a corpus term.** The spec calls it *the policy kernel*, *the dispatcher*, *the broker*, or `kernel/`. Names appearing in code or elsewhere as `AttenuationKernel` have no spec anchor; the closest normative names are `Kernel.dispatch` (`ADR-0066`), `StandardPolicy.authorize` and `attenuate()` (`ADR-0067`) |
| **Y-04** | **`EffectReceipt` has no wire shape in VG-04.** It is referenced by `EnvironmentAdapter`, `CT-29` and `05 §3`, but only GTS-13C `T1.6` defines fields, and that shape (`{grantId?, outcome, observedAt, resultDigest, note}`) omits the lease identifier `CT-29` requires |
| **Y-05** | **Two admission verbs share one word.** `V-02` ("only the verifier admits") governs *evidence*; VG-03 §8.4 ("only the activation policy admits") governs *artifacts into the active set*. `N-10` states only the first. The spec flags the confusion but keeps both usages |
| **Y-06** | **Risk tiers are never enumerated.** `RiskTier` appears in `CapabilityGrant.constraints.requireApprovalAboveRisk`, in `EffectDescriptor.riskTier`, in the manifests (`low`/`medium`/`high`) and in `03 §7.5`, but no normative document defines the tier set or its ordering |
| **Y-07** | **`ActionId` / verb namespace is undefined.** Verbs appear as `fs.read`, `fs.patch`, `fs.delete`, `proc.test`, `proc.exec`, `observe` across VG-05 §2.1, `ADR-0067` and the manifests, but the naming grammar and registry are not specified |
| **Y-08** | **VG-07 §0 cites in-tree implementation paths** (`tools/telemetry/*.py`, `lab/{build,run,diff,bench}.py`) inside a NORMATIVE document, which sits awkwardly with `PR-1` and with `LT-8` ("nothing imports `lab/`"). Similarly VG-01 `M11` cites `vanguard/packages/...` paths in a document that "states nothing normative" |
| **Y-09** | **VG-01 §1 is titled "Nine mental models" but enumerates eleven** (`M1`–`M11`); `M10` and `M11` were added by `ADR-0059`/`ADR-0060` without updating the heading |
| **Y-10** | **`MF-*` namespace is fragmented.** VG-08 §5 owns `MF-01`…`MF-37`; later artifacts introduce `MF-KRN-008..011` (`ADR-0054`) and `MF-S4-001` (`APPROVAL-0004`); `DEF-02` promises "a clean `MF-` namespace allocation" for memory tests. `CI-4` forbids an identifier defined in two documents |
| **Y-11** | **VG-09 structural defect.** An `ADR-0067` row is embedded inside §8 ("Sprint 0 approval events") above that section's table header, while `ADR-0066` and `ADR-0068` live in §12. ADR numbering is therefore non-monotonic across sections |
| **Y-12** | **Registry acceptance state is internally stale.** VG-00 §11.1 records "`02`–`08` frozen" while the §12 change log records "`04` **unfrozen** and corrected" with `ADR-0039`…`0044`. It also records `CV-13` as OPEN and "not self-certifiable" — a gate that remains open through the current version |
| **Y-13** | **GTS-13C is not registered in VG-00 Ch. 2**, so by `PR-3` it is not normative and by `CI-1` (Ch. 2 ↔ `docs/v4/` bijection) its presence in the corpus directory is itself a registry violation. It self-declares non-normativity, but `ADR-0046` makes it "the sole active programme plan" and `ADR-0057`/`ADR-0064` treat its Ch. 10 gate questions as binding |
| **Y-14** | **`ADR-0063`'s stated context is already stale.** It says "`VG-02 §9` still states TypeScript normatively", but VG-02 §9 as it now stands already records Python and cites `ADR-0063` — the correction was applied without a superseding note |
| **Y-15** | **Measurement scheduling conflict.** VG-08 §0 places "measurement and the A/A floor" firmly **out** of Phase 0, while GTS-13C titles `T8` *"Instrument — concurrent, not later"* and its own sprint table schedules `T8.1`–`T8.8` at S7–S8 |
| **Y-16** | **The `epistemic` axis is described as both an axis and a lattice.** VG-04 §4 says it "carries its own ordered lattice" and is "**not** a second model", while §3.1 lists `integrity` ("how strongly attested") which is also implicitly ordered. Only `epistemic` gets an enumerated value set |
| **Y-17** | **`influence` axis has no consumer.** VG-04 §4 states no authorisation decision reads it and it is best-effort; no document specifies who writes it, when, or what forensic query consumes it |
| **Y-18** | **Sprint/phase numbering overlaps two schemes.** VG-08 uses Phase 0 / Increments A-B-C / `TK-*`; GTS-13C uses S0–S9 / `T0`–`T11`; the ADRs add Waves W6–W9 / Sprints 7–10 and "Phase 1 (Trust Spine)", "Phase 2 (Sprints 5–6)", "Phase 3". `TK-*` and `T*` are never cross-mapped |
| **Y-19** | **`AT-09` requires the dispatch exit set to be exhaustive**, but the failure table contains `F-21a` (an out-of-sequence identifier inserted between `F-21` and `F-22`), so the enumeration is 26 entries under 25 sequential IDs. Any generated check keyed on `F-01..F-25` misses `F-21a` |
| **Y-20** | **The word "broker" has no owning definition.** It appears in `N-01`, `A-03`, `M3`, VG-03 §3 (Control plane), and VG-05 (which mostly says "dispatcher" / "policy kernel"). The glossary defines `Grant` and `Attenuation` but not `Broker`, and no port or module name corresponds to it |

### 12.3 Known-open governance gates (spec-recorded, not implementation observations)

- `CV-13` comprehension gate: **OPEN**, not self-certifiable, packet at `cv13/`.
- `CI-9` rule-to-test map: **RED by construction**, 133 of 203 rules uncovered; a Phase 0 **exit** gate.
- `SC-7` and `SC-12`: **OPEN**, assigned to `TK-01`. All 14 schemas held at `DRAFT`.
- Schema `LOCKED` status deferred (`ADR-0038`); `T1` recorded as DRAFT not LOCKED (`APPROVAL-0003`).
- `SEC-01` reopened (`DECISION-0006`) with a binding remediation order.
- MVP gate Q1–Q4 all recorded as not met or regressed at `0238b1a` (`ADR-0064`).
- VG-05 §10 standing caveat: **until `CI-9` passes, every rule in VG-05 is asserted and unproven, and no
  rule may be cited as an established control before its test exists.**
