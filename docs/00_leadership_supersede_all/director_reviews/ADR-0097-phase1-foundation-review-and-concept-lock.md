---
id: adr-0097-phase1-foundation-review-and-concept-lock
adr: 0097
class: decision
authority: binding-decision
canonical_for:
  - phase1-foundation-review-record
  - adr-0096-adjudication
  - canonical-concept-lock
  - m5a-substrate-change-set
status: proposed
owner: principal-systems-architect
version: "0.1.0"
last_verified: 2026-08-25
extends:
  - ADR-0095
  - ADR-0096
supersedes: []
superseded_by: null
---

# ADR-0097 — Phase 1 Foundation Review: Adjudication, Corrections, and Concept Lock

## Status

**Proposed — requires Engineering Director ratification.** Companion evidence:
`AETHER_PHASE1_ASSESSMENT.md` (findings register F-1…F-9, open questions OQ-1…OQ-8).

## What was reviewed

The complete constitutional stack (VISION v0.7.0, SPEC v0.7.0, six law leaves, ADRs 0069–0096),
the execution stack (`milestones.md`, `sprint_active.md`), and the implementation baseline
(`vanguard/packages/*`, `packs/*`, `schemas/*`, `tools/linters/*`), including import-direction
audit, TCB measurement, event-vocabulary reconciliation, `ExecutionProfile` axis verification,
and local execution of the kernel/contract/runtime/security suites.

## §1 What did not change

The architectural thesis of Law Zero is **confirmed, not amended**: event-sourced general agentic
computation substrate; typed causal operations within lineages; agents as
`Identity + Policy + Event-Derived Projection + Execution Boundary`; domain-blind kernel behind
S0–S12; composition/trajectory duality; exterior signed evaluation; falsifier-gated evolution.
The layer stack `domain → ports → kernel → agency → runtime → adapters → packs/clients` is
confirmed with zero merges, splits, or renames. Roadmap ordering
M-4 → M-5a → M-5b → M-6 → M-6.5 → M-7 → M-8 → M-9 is confirmed. All architectural refusals in
SPEC remain in force. Historical ADRs remain immutable provenance.

## §2 ADR-0096 adjudication: ratify with two amendments

Phase 1's blocking incoherence was ADR-0096 sitting in `proposed` state, creating dual candidate
constitutions and blocking M4-04 bullet 3. Decision: **ratify ADR-0096**, executing its §12 Vision
edits and §12.1 subordinate edits in one atomic commit, subject to:

### §2.1 Amendment A — reproducibility vector value domains (closes OQ-1)

ADR-0096 §8.1 names six dimensions but no value domains, leaving RF-100 unexecutable. The
following domains are adopted; each value MUST be derived from observable facts per §8.3:

```text
state_reconstruction   ∈ {none, from_checkpoint, full_cold}     ← reducer/schema pins + WAL presence
semantic_replay        ∈ {unverified, pinned_verified}          ← replay under pinned reducer/schema set
external_reexecution   ∈ {unavailable, degraded, available}     ← provider/model/tool identity liveness
artifact_retention     ∈ {digests_only, partial, full}          ← retention profile × artifact availability
environment_capture    ∈ {none, declared, snapshot}             ← environment_snapshot presence/kind
provider_model_identity∈ {unattributed, attributed, attested}   ← model route identity + attestation
```

`reproducibility_at_run_close` records this vector immutably; `reproducibility_current` MAY be
recomputed and MUST never overwrite it (0096 §8.4). Capture lands in M4-04; computation in M-5a
(RF-100 unchanged).

### §2.2 Amendment B — trusted import closure in RF-97

The multidimensional Trusted Core Budget (0096 §7.1) MUST measure the **trusted import closure**
of the kernel, not the `kernel/` directory. As of this baseline the closure additionally contains
`domain/canonicalisation/digest.py`, `domain/canonicalisation/jcs.py`, and
`domain/selectors/resource_selector.py`. `check_tcb_budget.py` MUST enumerate the closure and gate:
invariant count, public contracts, privileged operations, dependency count, domain-specific
concepts (=0), extension knowledge (=0), and change amplification. LOC remains one signal among
several. (Closes finding F-3; RF-97 milestone assignment M-5a unchanged.)

## §3 M-5a substrate change set (decided now, executed only inside the M-5a window)

The event envelope digest preimage MUST NOT change before M-5a (0096 §6.2bis). The following are
therefore **decided in this ADR and executed together at M-5a**, after which `M-5-BASE` is
re-tagged exactly once:

### §3.1 Envelope authority provenance

Add `authority_source`, `policy_version`, `approval_reference` (nullable), `capability_grant`
(nullable) as typed envelope fields per 0096 §6 (RF-99).

### §3.2 Event vocabulary unification (closes finding F-2)

`EVENT_KINDS` currently equals the schema-generated wire enum (42 kinds) plus a hand-maintained
`_V4_ONLY_KINDS` set (16 kinds). At M-5a:

- **Fold into the generated schema** every V4-only kind with a live writer or reducer
  (`ActivationChanged`, `ArtifactCreated`, `CompetencePriorRecorded`, `ConflictDetected`,
  `EffectPreviewed`, `EpisodeStateChanged`, `EvidenceClaimProduced`, `ObservationProduced`).
- **Formally deprecate** the eight normative-but-dead kinds (`ObservationRequested`,
  `OperatorInvoked`, `OperatorSelected`, `CorrectionRecorded`, `CandidateBuilt`,
  `CandidateAttested`, `CanaryPromoted`, `RollbackTriggered`) into a deprecated register.
  Reintroduction requires the standard package: ADR, allocation, writer, reducer, schema,
  conformance vector, coverage proof. Nothing may emit a deprecated kind.
- Delete `_V4_ONLY_KINDS`; `schemas/mhf/event_envelope.schema.json` becomes the sole kind
  authority, restoring A-4/I-8 without exception text.

### §3.3 Checkpointed projection fold (closes OQ-6 at design level)

`AgentView`/canonical-reducer reconstruction MUST support snapshot + suffix replay with the
checkpoint identity carried in provenance, so cold reconstruction cost is O(suffix). Contract
shape is an M5a-P1 deliverable.

## §4 Canonical concept lock

Format: **term → meaning → layer → owns → never owns → adjacency → stability**.
Stability classes: `constitutional` (Vision-superseding ADR to change), `locked`
(ADR to change), `contract-pending` (semantics locked, wire shape lands at the named milestone),
`hypothesis` (experimental; falsifier named), `deferred`.

| Term | Meaning | Layer | Owns | Never owns | Adjacent to | Stability |
|---|---|---|---|---|---|---|
| Event | Digest-identified durable causal fact in the append-only record | Substrate (domain/ledger + runtime/ledger) | Causal truth, ordering info, provenance | Large content; telemetry | Artifact, Projection | constitutional (invariants); realization = reference (0096 §2) |
| Artifact | Content-addressed immutable large content with schema, provenance, lifecycle | Substrate | Content identity; retention subjecthood | Causal ordering; mutable fields (CT-53) | Event, BlobStorePort | locked |
| Projection | Derived state, `S = fold(Events)`; rebuildable; never a second truth | Domain/agency/packs | Semantic state reconstruction | Authority; durability of new facts | Event, AgentView | constitutional (rule) |
| Ledger | The authoritative causal record (events + attributable artifacts) | Substrate | Correctness, recovery, replay, settlement history | Operational telemetry (0096 §5) | Telemetry (correlated) | constitutional |
| Telemetry | Traces/spans/metrics for operational analysis | Runtime/adapters | Latency, diagnostics, performance | Authoritative state | Ledger via correlation IDs | locked |
| Operation | Typed causal unit: identity, input/output refs, parentage, scope, resources, status | Substrate protocol | Composable action semantics | Class-hierarchy taxonomy of verbs | Effect, Lineage | contract-pending (M-5a) |
| Effect | Externally/durably consequential operation passing S0–S12 | Kernel (admissibility) + Substrate (settlement) | Admission; settlement distinctions PROPOSED…COMMITTED/INVALIDATED | Kernel-owned settlement (0096 §4) | Capability, Budget, Approval | locked |
| Lineage | Identity + ancestry of a causal region of execution | Substrate | Correlation, nesting, recovery unit | Privileged objecthood | Scope, agent.spawn | contract-pending (M-5a) |
| Scope | Execution boundary: 6D budget, depth, turns, capabilities, terminal conditions | Substrate | Boundary semantics; attenuation subject | Policy content | Lineage, Budget, Grant | contract-pending (M-5a) |
| Agent | `Identity + Policy + Event-Derived Projection + Execution Boundary`; transient objects permitted, authoritative in-memory state prohibited (0096 §3) | Conceptual / agency | Naming a coherent causal region | Persistent privileged objecthood | AgentView, Lineage | constitutional |
| AgentView | Projection reconstructing goal, plan, attempts, settled effects, budget, strategy, terminal status | Agency/domain | Semantic continuation state | Truth; write authority | Projection, RF-96 | contract-pending (M-5a) |
| Policy | Identity-bearing substitutable decision logic (deterministic or model-backed) | Runtime config / packs / plugins | Selection among admissible options | Authority widening; kernel residence | Composition (`D_H`) | locked |
| Capability / Grant | Attenuable authority to propose classes of effects | Kernel | Authority algebra; fail-closed denial | Intelligence; proposal content | Attenuation, Approval | constitutional |
| Budget | 6D tensor {usd_micros, tokens, bytes, millis, depth, turns}; additive dims conserved, structural dims ceilings | Kernel (Governor) | Reservation/commit/release; leases | Scheduler claim TTL semantics | Scope, Lease | locked |
| Kernel | S0–S12 domain-blind reference monitor; trusted import closure per §2.2 | Kernel | Admissibility, authority, invariants, generic resource constraints | Domain semantics; settlement; verbs; child topology | RF-97, RF-98 | constitutional |
| Substrate | Events + artifacts + settlement + lineage/scope semantics | domain/ledger + runtime/ledger | Authoritative outcome semantics | Intelligence; scheduling policy | Kernel, Runtime | constitutional (invariants) |
| Runtime | Composition, activation, lifecycle, WAL, recovery, profiles, scheduling *mechanism*, delegation *mechanism* | Runtime | Sole bootstrap seam; production chain | Second kernel; domain logic | Adapters, Profiles | locked |
| Agency | Generic observation/proposal/context/episode mechanics; no specific agents | Agency | Context assembly + compaction mechanism; turn loop (I-11) | Adapter imports; domain policy | Packs, Runtime | locked |
| Adapter | Concrete realization of a port (models, stores, sandboxes, environments, evaluators) | Adapters | External-system binding | Authority; composition | Ports | locked |
| Plugin | Isolated, untrusted-by-default extension with declared capabilities/lifecycle; activation materializes a service or fails | Extensions | Declared capability surface | Kernel trust; second engine | Manifest, SPI | locked |
| Pack | Domain organization of tools, policies, prompts, oracles, projections | Packs | Domain capability composition | Kernel/substrate semantics (RF-98) | Composition | locked |
| Composition | `mhf.manifest/2 → CanonicalManifest → FrozenComposition (D_H) → ActivationPlan → RunPlan` — the declared space of possibilities | Runtime | Behavioral identity | Being a workflow DAG authority (RF-66) | Trajectory, D_R | constitutional |
| ExecutionProfile | Identity-bearing containment/approval/persistence/evaluation/assurance/capture config entering `D_R`; gains retention + reproducibility axes (M4-04) | Runtime | Deployment/assurance identity; fail-closed containment | Silent fallback | D_R, RF-100 | locked |
| Trajectory | Emergent causal graph of what actually occurred; complete at terminal (I-9) | Substrate/evidence | Scientific record of a run | Being pre-declared control flow | Composition, Evaluation | constitutional |
| Evaluator / Verdict | Exterior signed judge; `evaluation: none` ⇒ unattributable for promotion | Adapters/evidence | Independent attribution | Generator self-certification (0096 §10) | MEASUREMENT.md | constitutional |
| Skill | Versioned reusable procedure/policy/fragment; candidate-evaluated alone, **promoted only as versioned composition** with regression decomposition | Derived structure | Reusable procedural knowledge | Self-promotion; storage-blob conflation | 0096 §9, M-8 | locked |
| Memory | Five distinct categories: session state, persistent knowledge, experience, skills, user/project memory — never one storage abstraction; access under capability + provenance + auditability + revocation (0096 §6.4) | Derived family | Category separation (vocabulary) | Kernel semantics; single blob store | Projections, M-8 | locked vocabulary; mechanism deferred (M-8) |
| Topology | Versioned data/config organizing lineages/roles; experimental structure lowered to ordinary scheduling + mediated spawn | Derived family | Structural possibility declaration | Capability hierarchy; second authority; assumed superiority | Scheduler, M-7 | locked (0096 §11.4) |
| Scheduler | Mechanism in Runtime (readiness/dispatch/reservation); policy substitutable | Runtime + policy | Temporal ordering of ready operations | Admissibility; second kernel | I-11, M7-01 | locked (0096 §11.3) |
| Meta-control / Metacognition | Higher-order control as policy/reducer/plugin over the same observations; experimental hypothesis with 0096 §11.7 decomposition; requires Confidence/Uncertainty Protocol before M-6.5 | Derived family | Strategy change proposals via ordinary S0–S12 | Special authority; kernel primitive | ProgressProjection, M-6.5 | hypothesis (paired-run falsifier) |
| Self-improvement | `execution → trajectory → evaluation → analysis → candidate → held-out evaluation → promotion/rollback`; search family plural (0096 §11.5) | Exterior pipelines + M-8 | Measured improvement | Unrestricted self-modification; generator promotion authority | MEASUREMENT.md | constitutional (separation) |
| Replay vs. re-execution | Replay = deterministic fold under pinned reducers/schemas; re-execution = probabilistic resampling with controlled variable substitution | Substrate/science | Scoped reproducibility claims | Determinism pretense | Reproducibility vector | constitutional |

**Deprecated terminology (superseded, do not reuse):** "future mandatory layers"; "agent-first"
posture; singular "reproducibility class"; LOC-only TCB budget; `layer0` (deleted, ADR-0081);
the eight dead event kinds after §3.2 executes; "Agent" as persistent privileged object.

**Intentionally deferred:** distributed execution, population/evolutionary search runtimes,
online adaptation, multi-tenant isolation law (OQ-8), advanced scheduler (pending M7-01),
memory mechanism design (M-8). Each is stress-tested only, per Vision cap. 20 and 0096 §11.

**Hypotheses requiring experimentation (falsifier named):** substrate generality (RF-86/RF-98),
metacognitive value (M-6.5 paired runs), concurrency value (M7-01), skill lift (M-8 held-out),
closed-loop epistemic-controller framing (reference doc §21 — research posture only).

## §5 Corrections performed / authorized in Phase 1

1. Ratification package for ADR-0096 with Amendments A and B (§2) — documentation act.
2. Findings F-2/F-3 decided now, executed at M-5a (§3) — no pre-M-5a code change authorized.
3. RF-95 NO-GO discipline reaffirmed: no live run before M4-04 closes all four bullets.
4. **No other code change is authorized under Phase 1.** M4-04 implementation remains ordinary
   authorized sprint work; Phase 1 does not expand into feature development.

## §6 Invariants future work must preserve

I-1…I-11 unchanged; the 0096 constitutional invariants (§2.1) upon ratification; RF-96…RF-100 as
allocated; Kernel Neutrality Gate at every foundational-contract milestone; one canonical
definition per concept with subordinate references (this table is that canonical record for
vocabulary; law leaves remain canonical for their clauses).

## Consequences

Accepted costs: one more governance act (0096 ratification) before M-4 can close; a larger,
single-shot M-5a change window; multidimensional budget tooling work (RF-97). Accepted because
each converts a standing ambiguity into a falsifiable obligation. Rejected alternatives:
redesigning any layer (no evidence demanded it); ratifying 0096 unamended (leaves RF-100
unexecutable and the trust boundary miscounted); fixing the event vocabulary immediately
(violates the envelope-preimage protection); rejecting 0096 (re-freezes empirical falsification
out of the constitution).
