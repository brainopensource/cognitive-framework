---
id: adr-0096-constitutional-correction-evidence-causal-invariants-and-falsifiers
adr: 0096
class: decision
authority: vision-superseding
canonical_for:
  - evidence-admissibility-and-vision-amendment
  - causal-history-invariants
  - authority-provenance
  - trusted-core-minimality
  - reproducibility-metadata
  - composition-level-skill-promotion
status: proposed
owner: principal-systems-architect
version: "0.2.0"
last_verified: 2026-08-25
extends:
  - ADR-0095-vision-as-law-zero-and-roadmap-reconciliation
supersedes:
  - ADR-0095-lock-clause-only
superseded_by: null
---

# ADR-0096 — Constitutional Correction: Evidence Admissibility, Causal Invariants and Falsifiers

## Status

**Proposed — Vision-superseding constitutional correction.**

Requires ratification by the Engineering Director and atomic reflection in `VISION.md`.

---

## What this ADR is not

This ADR introduces **no new architectural direction**. It corrects governance mechanisms and abstraction boundaries that were missing or over-constrained in Law Zero v0.7.0.

Specifically, it does **not**:

* reopen M-4 or alter its scope;
* change milestone sequencing or roadmap ordering;
* rewrite the Vision's central thesis or product direction;
* mandate new product surfaces;
* require creation of artificial domain packs for governance purposes;
* constitutionalize a particular learning, search, scheduling, memory, telemetry, or settlement implementation.

Where this ADR changes Vision text, the changes are surgical and enumerated in §12.

---

# Context

Law Zero v0.7.0 was written to defend AETHER against a specific failure mode:

**architectural drift by subordinate prose or incomplete implementation.**

Rule 3 of the precedence ladder correctly states that implementation which has not yet reached the Vision is a documented gap and is never, by itself, justification for weakening the Vision.

That protection is retained.

However, review of the constitution exposed a second failure mode: the Vision commissions experiments and falsifiers, while providing no constitutional path for their negative results to challenge the hypotheses being tested.

The architecture therefore needs to distinguish **implementation non-conformance** from **empirical falsification**.

Additional review identified further boundary problems:

1. **Empirical falsification has no constitutional path.**
   M-5b exists to challenge substrate generality and M-6.5 requires experimental evaluation of metacognitive control, yet the existing Law Zero can classify negative evidence only as implementation gap.

2. **Several engineering mechanisms were elevated too close to ontology.**
   Event sourcing is the reference realization of durable causal history in AETHER, but the constitution should bind causal, replay, authority, and reconstruction invariants rather than make one realization eternally mandatory.

3. **Trusted Core minimality lacks a falsifier.**
   Generality is tested, but nothing formally detects gradual Kernel accretion through individually defensible additions.

4. **Authority provenance is insufficiently represented in the universal protocol.**
   Security is correctly no longer the strategic identity of AETHER, but authority remains fundamental to effect correctness, recovery, auditability, and replay.

5. **Learning promotion can evaluate the wrong unit.**
   A candidate skill may improve some workloads while causing regressions elsewhere, including effects caused by its mere presence in a composition.

6. **Reproducibility is multidimensional and time-dependent.**
   Reconstruction, semantic replay, external re-execution, artifact retention, and environment capture are independent properties and may change differently over time.

7. **Causal truth and telemetry have different authority semantics.**
   Tracing explains operational behavior; it does not define authoritative system state.

8. **Future capability families were described too strongly as predetermined architectural layers.**
   Memory, topology, metacognition, learning, delegation, and scheduling must remain derivable and replaceable rather than becoming mandatory independent runtimes.

---

# Decision

## 1. Evidence admissibility and Vision amendment

Reproducible evidence may **falsify a Vision hypothesis**. It may **not silently amend the Vision**.

Epistemological authority and governance authority remain separate.

### 1.1 Divergence classes

Law Zero MUST distinguish:

```text
implementation non-conformance
    → documented gap
    → no constitutional effect

reproducible material counter-evidence
    → mandatory Vision review
    → Vision-superseding ADR when sustained
```

### 1.2 Counter-evidence

Material reproducible counter-evidence MUST trigger explicit architectural review.

It MUST NOT be dismissed merely as an implementation gap.

### 1.3 No implicit amendment

Until a Vision-superseding ADR is ratified, the standing Vision remains normative authority.

**There is no implicit constitutional amendment.**

### 1.4 Pre-registration

Pre-registration is NOT constitutionally required for evidence to be admissible.

Reproducible evidence discovered outside a pre-registered experiment remains evidence.

Stronger assurance profiles MAY require pre-registration for particular claims or promotion decisions.

Pre-registration increases assurance; it does not determine whether observations exist.

### 1.5 Drift remains non-authoritative

Prose drift, implementation convenience, outdated subordinate documentation, and incomplete implementation remain incapable of altering the constitution.

---

## 2. Causal-history invariants; event sourcing as reference realization

The constitution binds the properties required for durable agentic computation rather than permanently binding their current implementation mechanism.

### 2.1 Constitutional invariants

AETHER MUST preserve:

* durable causal history;
* provenance;
* attributable artifacts;
* reconstructable projections;
* committed-outcome semantics;
* authority semantics;
* cold replay;
* process-independent continuation.

### 2.2 Reference realization

Event sourcing is the **reference realization** of these invariants in AETHER v0.7+.

It is not itself elevated to an irreplaceable ontology.

### 2.3 Replacement standard

Any future alternative realization MUST satisfy the same invariants and pass the same architectural falsifiers.

This ADR creates **no permission** to return to mutable authoritative in-memory state.

---

## 3. Agent object permitted; authoritative in-memory state prohibited

### 3.1 Runtime objects

An `Agent` object MAY exist as an ergonomic, performance, orchestration, or operational convenience.

### 3.2 Authority boundary

No in-memory `Agent`, workflow object, planner object, cache, session object, or equivalent mutable structure may constitute authoritative persistent state.

Durable authority resides in the causal record and its attributable artifacts.

Live objects are reconstructable projections, execution views, or caches.

### 3.3 Architectural model

The AETHER architectural model remains:

```text
Agent
=
Identity
+ Policy
+ Event-Derived Projection
+ Execution Boundary
```

This is an AETHER architectural decision.

It MUST NOT be represented as external scientific consensus.

### 3.4 Executable falsifier

A conforming agentic execution MUST be capable, at the milestone where reconstruction is required, of surviving process destruction and reconstruction without depending on inaccessible authoritative object state.

---

## 4. Effect settlement belongs to the substrate, not the Kernel

### 4.1 Kernel responsibility

The Kernel owns:

* admissibility;
* authority enforcement;
* invariant enforcement;
* generic resource and effect constraints assigned to the Trusted Core.

### 4.2 Settlement responsibility

The Event/Effect Substrate owns authoritative outcome semantics.

Its settlement model MUST be capable of representing at least the semantic distinctions corresponding to:

```text
PROPOSED
AUTHORIZED
DISPATCHED
OBSERVED
SETTLED
COMMITTED
INVALIDATED
```

These names describe required semantic distinctions; protocol evolution MAY refine their concrete representation.

### 4.3 Observation is not commitment

An observed event and an authoritatively committed outcome are distinct.

This distinction MUST be representable wherever it materially affects:

* recovery;
* resume;
* idempotency;
* external effects;
* human approval;
* cache validity;
* replay;
* compensation or invalidation.

---

## 5. Causal record is not telemetry

AETHER MUST maintain a strict semantic distinction between authoritative causal evidence and operational telemetry.

### 5.1 Causal record

The ledger and attributable artifacts represent the authoritative causal record for:

* correctness;
* recovery;
* provenance;
* replay;
* settlement;
* historical reconstruction.

### 5.2 Telemetry

Telemetry — including traces, spans and metrics — represents operational observability for:

* latency;
* diagnostics;
* performance;
* resource consumption;
* operational analysis.

### 5.3 Correlation

The two systems MUST be correlatable through stable shared identifiers where applicable.

Telemetry MUST NOT become authoritative persistent state.

The causal ledger MUST NOT be overloaded into a generic telemetry dump.

---

## 6. Authority provenance is first-class protocol data

Every operation of consequence, and every externally or durably consequential effect in particular, MUST carry sufficient protocol-level authority provenance.

The canonical authority provenance model includes:

```text
actor_identity
authority_source
policy_version
approval_reference
capability_grant
causation_id
correlation_id
```

### 6.1 Protocol fields

These values are protocol data, not informal log messages.

For an operation to which authority provenance applies:

* `actor_identity` MUST identify the actor or system principal responsible for initiation;
* `authority_source` MUST identify the authority basis under which the operation proceeds;
* `policy_version` MUST identify the governing policy or deterministic authority rule;
* `causation_id` MUST preserve immediate causal ancestry where applicable;
* `correlation_id` MUST permit association with the enclosing execution, transaction, lineage, or effect flow.

### 6.2 Nullable authority references

`approval_reference` and `capability_grant` MUST be **representable as typed protocol fields**, but MAY be explicitly `null` when semantically inapplicable.

Their absence of applicability MUST NOT require fabrication of synthetic approvals or grants.

Where an approval or capability grant materially authorizes an operation, the corresponding reference MUST be populated.

### 6.3 Strategic identity versus operational ontology

Security is not the strategic identity of AETHER.

**Authority remains part of its operational ontology.**

### 6.4 Memory and retrieval

The constitutional invariant for memory access and retrieval is:

```text
capability enforcement
+ provenance
+ authority semantics
+ auditability
+ revocation
```

The concrete effect, retrieval, or settlement pipeline implementing those properties remains substitutable.

No current staging sequence is constitutionalized by this ADR.

---

## 7. Trusted Core Budget and recurring Kernel Neutrality Gate

Trusted Core minimality MUST be continuously falsifiable.

### 7.1 Multidimensional Trusted Core Budget

Minimality MUST NOT be measured by LOC alone.

The standing Trusted Core Budget evaluates at least:

* number and scope of Kernel-owned invariants;
* public Kernel contracts;
* privileged operations;
* Kernel dependencies;
* domain-specific concepts — target: **zero**;
* Kernel knowledge of extensions — target: **zero**;
* change amplification caused by Kernel modifications;
* whether introduction of a new capability or domain requires Kernel semantic modification.

### 7.2 Kernel Neutrality Gate

Every milestone that modifies foundational contracts MUST demonstrate that existing heterogeneous domains require no new domain-specific Kernel semantics.

### 7.3 Novel-domain probes

Novel-domain probes are required at architectural inflection points rather than at every milestone.

At minimum:

* M-5b performs the first material second-domain falsification;
* major structural expansions after M-5b, including M-7/M-8 when applicable, MUST re-run neutrality evidence and SHOULD introduce a novel-domain probe where existing domains are insufficient to challenge the new abstraction.

Manufacturing artificial domain packs solely to satisfy governance is an anti-pattern and is explicitly not required.

### 7.4 Primary falsifier

The desired invariant is:

```text
new capability or domain
→ kernel semantic diff == 0
```

If Kernel semantic modification is required, an architectural ADR MUST explain why the responsibility cannot reside in:

* Event/Effect Substrate;
* Runtime mechanism;
* policy;
* plugin;
* capability;
* projection;
* derived structure.

A justified Kernel change is possible.

An unexplained Kernel change is an architectural failure.

---

## 8. Reproducibility metadata is vectorized, computed, and time-aware

Reproducibility is not an ordinal maturity ladder.

Its dimensions are independent.

### 8.1 Minimum vector

Each scientifically relevant run MUST be classifiable across at least:

```text
state_reconstruction
semantic_replay
external_reexecution
artifact_retention
environment_capture
provider/model_identity
```

### 8.2 Assessment evidence

Each assessment MUST carry:

```text
assessed_at
basis/evidence
relevant versions
relevant digests
```

### 8.3 Computed, not self-declared

Reproducibility metadata MUST be derived from observable execution facts such as:

* reducer versions;
* schema versions;
* artifact availability;
* retention profile;
* environment capture;
* model identity;
* provider identity;
* dependency pinning.

The executing agent MUST NOT be the authority that simply declares its own reproducibility status.

### 8.4 Historical versus current reproducibility

AETHER MUST preserve:

```text
reproducibility_at_run_close
```

as historical evidence.

The system MAY later compute:

```text
reproducibility_current
```

to account for changes such as provider disappearance, model retirement, missing external dependencies, or artifact expiry.

`reproducibility_current` MUST NEVER overwrite the historical run-close assessment.

### 8.5 Scoped claims

Unscoped absolute reproducibility claims are prohibited.

For example, semantic replay should be expressed using scoped language equivalent to:

```text
verified under pinned reducer/schema set
```

rather than:

```text
guaranteed
```

unless the guarantee and its boundary have been formally established.

---

## 9. Composition-level, regression-aware skill promotion

A skill is not promoted merely because it performs well in isolation.

### 9.1 Candidate evaluation

A skill MAY be evaluated independently as a candidate.

### 9.2 Promotion unit

Promotion occurs only as part of a **versioned active composition/library** that passes regression evaluation.

Therefore:

```text
candidate skill evaluation
≠
library/composition promotion
```

Admitting skill `N+1` creates a new composition version.

### 9.3 Promotion evidence

Net improvement greater than zero is insufficient.

Promotion evidence MUST be capable of decomposing at least:

* gross gains;
* regressions;
* residual failures;
* presence-only effects;
* invocation effects;
* grounding failures;
* verification failures;
* transfer performance;
* held-out performance.

### 9.4 Regression budget

The constitutional requirement is **composition-level regression evidence**, not exhaustive execution of every historical workload after every admission.

Evaluation policy MAY use:

* held-out regression suites;
* affected-context suites;
* adversarial presence-only tests;
* grounding tests;
* verification tests;
* periodic full sweeps;
* risk-based evaluation budgets.

Stronger assurance profiles MAY require full revalidation.

### 9.5 Skill design posture

Skills SHOULD preferentially improve grounded observation, evidence use, verification, reusable procedure, or other empirically validated capabilities.

No category of skill benefit is assumed constitutionally.

---

## 10. Generator, evaluator and promoter separation

### 10.1 Self-evaluation

A generator MAY evaluate, critique, inspect, or score its own output.

### 10.2 Independent promotion authority

A generator MUST NOT be the sole authority for evaluation or promotion.

Promotion requires independently attributable evidence.

### 10.3 Normative distinction

```text
self-critique
=
allowed capability

self-certification
=
insufficient promotion authority
```

The degree of evaluator independence MAY vary by assurance profile, but promotion MUST NOT rest solely on the generator's own assertion of improvement.

---

## 11. Framing corrections carried by this ADR

### 11.1 Evidence-first and composition-first

The standing architectural posture of AETHER v0.7+ is:

```text
product-useful
evidence-first
composition-first
substrate-preserving
experiment-driven
```

The coding agent remains the first principal laboratory.

It is not the ontological center of the architecture.

### 11.2 Derived capability families

The phrase **future mandatory layers** is retired.

The following are recognized as **derived capability families**:

* Memory;
* Delegation;
* Metacognition;
* Topology;
* Learning / Adaptation;
* Scheduling.

These families are conceptual groupings, not mandatory independent architectural layers.

Their mechanisms MAY reside across Runtime, substrate, policies, plugins, projections, capabilities, or derived structures where architectural responsibility requires.

No family receives independent runtime authority merely because it has a name.

### 11.3 Scheduling boundary

Scheduling mechanism belongs to the Runtime wherever generic readiness, dispatch, concurrency, reservation, or execution ordering requires machinery.

Scheduling policy remains substitutable and MAY be implemented through policy, plugin, configuration, or other derived control.

A Scheduler MUST NOT become a second Kernel or second execution authority.

### 11.4 Topology

Topology is an experimental organization of computation.

It is not:

* a capability hierarchy;
* a security authority;
* proof of greater intelligence;
* justification for additional Kernel semantics.

More agents, more hierarchy, and more parallelism MUST NOT be assumed to imply superior performance.

Topology variants MUST remain experimentally comparable.

### 11.5 Evolution and search remain plural

No search, adaptation, or evolutionary family is constitutionalized as the privileged mechanism for improvement.

This applies to mechanisms used to discover or optimize:

* skills;
* policies;
* prompts;
* compositions;
* topology;
* scheduling policies;
* memory policies;
* delegation strategies;
* other derived structures.

Sequential search, evolutionary algorithms, quality-diversity methods, MCTS, Bayesian optimization, meta-agent editing, deterministic optimization, and future mechanisms MAY compete on the same substrate.

This rule does **not** require multiple implementations of every runtime mechanism. It prevents one adaptive/search family from becoming architectural law.

### 11.6 Conceptual primitive hierarchy

AETHER uses the following hierarchy as a **reasoning and documentation model**:

```text
Computational primitives
OBSERVE · REPRESENT · SELECT · ACT · STORE · RETRIEVE
COMMUNICATE · ALLOCATE · EVALUATE · VARIATE · COMPOSE · SCHEDULE

        ↓

Capabilities / operations
fs.read · fs.search · patch.apply · proc.exec
model.invoke · http.fetch · agent.spawn · ...

        ↓

Derived structures
planner · critic · memory · skill · lineage · AgentView · ...

        ↓

Phenotypes
coding agent · researcher · debate system · swarm · ...
```

This hierarchy MUST NOT be mechanically reproduced as a package hierarchy, class hierarchy, or package-per-concept taxonomy.

The purpose is to classify behavior and architectural responsibility, not generate empty abstractions.

### 11.7 Metacognition

Metacognition remains an **experimental hypothesis**, never an assumed intelligence layer.

The standing architectural decomposition is:

```text
monitoring
+ uncertainty / calibration
+ self-model
+ resource model
+ value-of-computation
+ control
+ external outcome feedback
```

The following distinctions are normative:

```text
reflection       ≠ evidence
confidence       ≠ correctness
self-evaluation  ≠ external evaluation
memory           ≠ validated knowledge
```

The rule remains:

> **Metacognition is policy/reducer/plugin, never a Kernel primitive.**

Before M-6.5, a **Confidence/Uncertainty Measurement Protocol** MUST be defined that permits comparison among applicable signals including:

* self-reported confidence;
* token/logprob-derived confidence where available;
* behavioral confidence;
* external-verifier confidence;
* ensemble disagreement;
* calibration error.

No single confidence measurement mechanism is constitutionalized in advance.

---

# 12. Required surgical edits

| Vision section             | Required edit                                                                                                                                          |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Precedence ladder / Rule 2 | Preserve explicit ADR-only amendment and add mandatory Vision review for sustained material counter-evidence                                           |
| Precedence ladder / Rule 3 | Split divergence into `implementation non-conformance` and `reproducible counter-evidence`                                                             |
| Cap. 1                     | Replace `agent-first` posture with evidence-first/composition-first language                                                                           |
| Cap. 2                     | Reframe event sourcing as the reference realization of constitutional causal-history invariants                                                        |
| Cap. 3                     | Introduce vectorized, computed and time-aware reproducibility semantics; remove unscoped determinism language                                          |
| Cap. 4                     | Permit transient Agent objects while prohibiting authoritative in-memory state                                                                         |
| Cap. 5                     | Replace the flat primitives framing with the conceptual four-level hierarchy without creating new code taxonomy                                        |
| Cap. 6                     | Replace future mandatory layers with derived capability families; locate generic scheduling mechanism in Runtime and settlement semantics in substrate |
| Cap. 9                     | Separate authoritative causal record from telemetry and require correlation                                                                            |
| Cap. 14                    | Add metacognitive invariants and the Confidence/Uncertainty Measurement Protocol as an M-6.5 prerequisite                                              |
| Cap. 16                    | Clarify topology as experimental structure and scheduling policy as replaceable                                                                        |
| Cap. 17                    | Add explicit memory authority/provenance constraints and cross-reference time-aware reproducibility                                                    |
| Cap. 18                    | Replace net-improvement promotion with composition-level regression-aware promotion and generator/evaluator/promoter separation                        |
| Cap. 19                    | Add first-class authority provenance and nullable semantics for non-applicable approval/capability references                                          |
| Cap. 20                    | Add Trusted Core Budget and recurring Kernel Neutrality Gate; preserve existing roadmap                                                                |

Historical ADRs remain immutable provenance.

ADR-0095 is superseded only where its lock semantics prevent admissible empirical falsification from triggering constitutional review.

The Vision-as-Law-Zero authority ladder introduced by ADR-0095 is retained and strengthened.

---

# Consequences

## Accepted costs

Composition-level promotion is more expensive than isolated skill promotion.

Kernel Neutrality Gates add an explicit proof burden whenever foundational contracts change.

Computed reproducibility metadata requires the substrate to retain enough information about reducer, schema, environment, artifact, model and provider identity to evaluate its claims.

Authority provenance expands protocol data.

These costs are accepted because they directly support falsifiability, recovery, security, reproducibility and controlled evolution.

## Accepted risk

§1 deliberately makes Vision hypotheses empirically falsifiable.

This is intentional.

Protection against opportunistic or accidental architectural change remains:

```text
evidence
→ review

review
→ explicit ADR

ratified ADR
→ constitutional amendment
```

Evidence never edits the constitution implicitly.

## Rejected alternatives

The following alternatives are rejected:

* **Evidence as direct amendment authority** — conflates epistemology with governance.
* **Constitutional pre-registration requirement** — unnecessarily restricts evidence admissibility.
* **Event sourcing as immutable ontology** — binds implementation rather than invariant.
* **Mutable authoritative Agent state** — breaks reconstruction and process independence.
* **Settlement semantics inside the Kernel** — expands the Trusted Core unnecessarily.
* **Telemetry as authoritative history** — confuses observability with causal truth.
* **LOC-only core budgets** — trivially gameable and semantically weak.
* **Ordinal reproducibility classes** — collapse independent dimensions.
* **Skill-only promotion** — fails to detect composition-level regressions.
* **Generator self-certification** — lacks independent promotion evidence.
* **New domain at every milestone** — manufactures product work for governance rather than testing architecture.
* **Mandatory future capability layers** — prematurely freezes decomposition.
* **Primitive-per-package or primitive-per-class taxonomy** — converts conceptual classification into empty implementation abstraction.
* **Constitutionalizing the current effect/retrieval staging** — prevents mechanism replacement without strengthening invariants.

---

# Ratification and execution

Upon ratification:

1. apply all §12 changes atomically;
2. update subordinate architecture documentation where terminology changed;
3. verify that no subordinate normative text contradicts the amended Vision;
4. update ADR-0096 status to `accepted`;
5. update `VISION.md` metadata and supersession references;
6. re-freeze the constitution;
7. return to the active execution plan.

This ADR MUST NOT reopen M-4.

It MUST NOT alter the reconciled milestone sequence:

```text
M-4
→ M-5a
→ M-5b
→ M-6
→ M-6.5
→ M-7
→ M-8
→ M-9
```

Implementation-heavy consequences remain assigned to their appropriate milestones.

ADR-0096 is a **constitutional correction**, not a project rewrite and not a new architectural direction.
