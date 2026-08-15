---
id: VG-04
file: 04_vanguard_core_contracts_and_wire_schema_v040.md
title: "Vanguard v4.0 — Core Contracts & Wire Schema"
version: 4.0.0
status: NORMATIVE
authority_scope: >
  The source of truth for wire contracts; conventions and canonicalisation;
  primitives; content addressing; provenance; context blocks; capabilities and
  effect descriptors; budgets and leases; tools; the model interface; task and
  proposal separation; the competence and evidence graph; the event envelope and
  minimum event set; port interfaces; configuration; versioning; conformance.
supersedes: none (v4 is the first version of this document)
superseded_by: none
budget_words: 6000
owners: [Tech Lead]
last_reviewed: 2026-08-14
---

# Vanguard v4.0 — Core Contracts & Wire Schema

> **One sentence.** This is the corpus format: the set of decisions that, if wrong, must be paid for by re-running everything ever recorded.

---

## 0. Conventions

### 0.1 The source of truth

**JSON Schema 2020-12 is normative.** The artifacts live in `schemas/v4/` and are accompanied by a semantic specification — the invariants that are not structural — and golden vectors covering canonicalisation, codecs, errors and cross-language agreement.

A TypeScript validator is an **implementation** of those schemas, verified against them, and generates the TypeScript types. It is never the interface definition. A TypeScript-first validator expresses refinements, transforms, branded types and custom union logic that have no schema representation; as an interface definition it hands other languages a lossy derivative that drifts silently, and drift in a wire contract outlives the code that caused it.

| # | Rule |
|---|---|
| `CT-01` | JSON Schema 2020-12 is normative; validators in any language are implementations verified against it |
| `CT-02` | Types are **derived** from schemas, never hand-written alongside them |
| `CT-03` | Anything crossing a process boundary is parsed. A cast on external data is a lint error — parsing is the only way a value acquires its type |

### 0.2 Wire rules

| # | Rule | Rationale |
|---|---|---|
| `CT-04` | JSON only; every type round-trips without loss | Several languages must read it |
| `CT-05` | No `undefined` on the wire. Optional fields are omitted or explicitly `null` | `undefined` does not survive JSON |
| `CT-06` | No floating point for money. Currency is integer micro-units | Accumulated rounding error in a ledger is unacceptable |
| `CT-07` | No floating point for durations. Integer milliseconds | Same |
| `CT-08` | Timestamps are RFC 3339 UTC strings with millisecond precision | Readable, lexicographically sortable, unambiguous across languages |
| `CT-09` | Digests are `sha256:` plus 64 lowercase hex characters | One digest format, everywhere |
| `CT-10` | Enums are string literals, never integers | Readable in a raw stream; safe to extend |
| `CT-11` | Readers preserve unknown fields; writers emit only known schema | Forward compatibility for readers, strictness at the boundary |
| `CT-12` | Arrays are never sparse; maps are objects with string keys | Cross-language safety |
| `CT-13` | UTF-8 throughout; no lone surrogates | Strict-UTF-8 consumers will reject them |

### 0.3 Canonicalisation

**RFC 8785 / JCS, without local variation.** Sort and number rules are not reinvented here; a conformant library plus the shared vectors is the whole specification. Canonical form is the input to every digest and every descriptor.

> A descriptor computed differently in one language than another breaks loop detection and policy caching **silently**. This is why canonicalisation is a vendored standard rather than a house convention.

### 0.4 Large integers

Any field that may exceed 2⁵³−1 is a decimal string, not a JSON number:

```ts
const IntString = /^(0|[1-9][0-9]*)$/;   // wire form
```

This is not pedantry. Cumulative cost in micro-units and cumulative token counts both cross that boundary at corpus scale, and JSON numbers corrupt above it without raising anything.

### 0.5 Naming

Types are `PascalCase`, fields `camelCase`, enum members `snake_case` string literals. **Every event type name is a past-tense verb phrase** — `ProposalProduced`, never `ProduceProposal`. An event is a record of something that happened; a name in the imperative invites treating the stream as a command queue.

---

## 1. Primitives and identifiers

Branded identifiers exist so that passing a grant identifier where an episode identifier is expected fails at compile time rather than at a policy check.

```ts
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
| `CT-14` | `EventId` is a UUIDv7. It aids indexing and **does not** replace causal order, which is carried by the sequence field (§12.1) |
| `CT-15` | `ToolCallId` is provider-assigned and echoed verbatim. It is never regenerated, normalised or trimmed |
| `CT-16` | `TenantId`, `OwnerId` and `PrincipalId` exist from the first schema version. Retrofitting identity into an envelope after a corpus exists is the corpus-format problem in its most expensive form |

---

## 2. Content addressing and blobs

Large payloads live outside the event store, addressed by digest. The envelope carries references; the blob store carries bytes.

| # | Rule |
|---|---|
| `CT-17` | A blob is immutable and addressed by the digest of its bytes |
| `CT-18` | An event and its blob references commit atomically, or through staging with reconciliation. Never separately |
| `CT-19` | Every blob reference carries a classification, and the store exposes an **encryption hook keyed by classification** from the first contract — not as a later addition |
| `CT-20` | Digests provide integrity against corruption and accidental substitution. They are not a defence against an adversary with write access to the store |

---

## 3. Provenance

### 3.1 Six orthogonal axes

A single ordered lattice conflates independent properties and forces one number to answer six questions. The axes are separate:

| Axis | Question |
|---|---|
| `origin` | Where did this content come from? |
| `instructionAuthority` | May it direct behaviour, or only inform it? |
| `integrity` | How strongly is its content attested? |
| `confidentiality` | Who may see it? |
| `epistemic` | How well established is it as a belief? |
| `influence` | What did it plausibly contribute to? |

### 3.2 Structural enforcement

The axes describe; the type system enforces. Provenance is declared **per source class**, not per call site, and context assembly accepts context blocks only.

| # | Rule |
|---|---|
| `CT-21` | A raw string cannot enter context assembly. **Provenance laundering by concatenation is impossible by type signature**, not by review |
| `CT-22` | Results are labelled at construction, never at consumption |
| `CT-23` | Labels are declared once per source class, so a new call site cannot introduce an unlabelled path |

### 3.3 What provenance does not do

It does not establish causation. You cannot attribute from outside a model what "justified" its action — if untrusted content was in context, it may have influenced the output, and no span accounting recovers that. For sensitive effects the mechanism is **intent binding**: the effect is bound to a brief, a purpose digest and an approval, rather than inferred from attention. Enforcement is owned by `05 §5`.

---

## 4. Context blocks and epistemic state

A context block is the unit of assembly: content, its source class, its provenance axes, its layer assignment, and its epistemic state.

The `epistemic` axis (§3.1) carries its own ordered lattice — `observed`, `derived`, `hypothesised`, `corroborated`, `contradicted`, `retracted` — and it is **not** a second model. It is one axis among six, ordered where the others are categorical. A statement can be highly trusted in origin and weakly established as belief; collapsing the two is how a confident source becomes an established fact.

`influence` is the only axis that is **best-effort and non-enforcing**: it records what a block plausibly contributed to, for forensics. No authorisation decision reads it, because causation inside a model is not observable from outside (§3.3).

---

## 5. Capabilities and effect descriptors

### 5.1 Why a verb set is insufficient

A permission set over verbs — read, write, execute, network — is a **verb lattice**. It cannot express "read only this repository", "write only this branch", "egress only to this endpoint", or "use this secret without disclosing its value". Under verb-only attenuation, a "read-only" child can read the evaluator bundle, the policy configuration and the operator's private keys: all read-class, all permitted. Every serious authorisation system models `(principal, action, resource, context)`.

### 5.2 The grant

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

> **`CT-51` — a grant authorises one call, not a class of calls.** `descriptorDigest` is the digest of the normalised effect descriptor (§5.5), computed at S3 and verified at S8 (`05 §2.1`). It is **not** `purposeDigest`: purpose is the brief the effect serves, descriptor is the exact call. Without this field the point-of-effect verification in `05 [K-18]` has nothing to compare, and `F-14` is untestable — which is how the field came to be missing from the first draft of this document.

`discloseToModel: false` is typed as a literal rather than a boolean. A secret reference that could be disclosed to the model is a different type, and there is no code path that flips the flag.

### 5.3 Attenuation

A child grant is valid only when actions are a subset, resources are a subset, and constraints never increase time, uses, bytes, budget, risk or resource surface.

| # | Rule |
|---|---|
| `CT-24` | An out-of-scope request is **denied**, and the denial records both what was requested and what was grantable |
| `CT-25` | There is no silent intersection. Narrowing an over-broad request without saying so destroys the highest-value intrusion signal available |
| `CT-26` | A grant crossing a process boundary is authenticated by a message authentication code or signature. An in-process grant may be an opaque reference |
| `CT-27` | A grant is single-use when the effect has no safe idempotency key |
| `CT-28` | Long operations renew lease and grant explicitly. There is no universal fixed time-to-live |

### 5.3.1 Selector inclusion

"Resources are a subset" is undecidable without a per-kind relation. Each is defined; **a selector pair with no defined relation is denied, never intersected.**

| Kind | Child ⊆ Parent when |
|---|---|
| `fs` | Same `root`, and every child path is a normalised (`D-2`) prefix-match under some parent path. No globs in a grant — expand at issuance |
| `network` | Child hosts are a subset after lowercasing and IDNA normalisation; a parent wildcard `*.example.com` contains a child label but never another wildcard; ports are a numeric subset |
| `secret` | Child refs are a literal subset. `discloseToModel` is `false` on both by type |
| `git` | Same `repo`; child refs a subset of parent refs after full-ref expansion. No pattern refs |
| `table` | Same `table`; child ranges contained by parent ranges under interval containment on normalised coordinates |
| `browser` | Exact origin equality — scheme, host and port. **No subdomain or path containment**, because origin is the browser's own trust unit |
| `generic` | **Literal equality of `uriPattern` only.** Pattern-versus-pattern containment is undecidable in general, and an approximation here silently widens authority |

> **`CT-52`.** Inclusion is decidable, total on the pairs above, and denies everything else — including any cross-kind comparison. A checker that returns "unknown" must fail closed and emit `AuthorizationDenied{scope_escalation}`.

`CT-25` deserves its rationale stated once: a child repeatedly requesting capabilities beyond its parent is one of the strongest anomaly detectors a system of this shape can have, and silent narrowing discards it by design.

### 5.4 Execution capabilities

Granting subprocess execution grants execution **inside an already-limited environment**. It does not imply that anything intercepts syscalls. The receipt therefore records what actually bounded the effect: image or root filesystem digest; normalised argument vector and working directory; environment variable **keys, never secret values**; mounts; network policy; resource limits; redacted output references; exit, cancellation or timeout; and the containment runtime in force.

### 5.5 The effect descriptor

The descriptor serves three consumers, which is why it is specified to the byte: loop detection compares consecutive descriptors; policy caching keys on it; and a grant binds one and is verified at the point of effect.

Normalisation rules, normative because independent implementations must agree byte-for-byte:

| # | Rule | Rationale |
|---|---|---|
| `D-1` | Object keys sorted per canonical JSON | Key order is not semantic |
| `D-2` | Path arguments resolved against the workspace root, relative segments collapsed, no trailing slash, forward slashes always | Two spellings of one path are the same call |
| `D-3` | **The provider-assigned call identifier is excluded** | It differs between otherwise identical calls |
| `D-4` | String arguments are not trimmed or case-folded | Whitespace is semantic in commands and in file content |
| `D-5` | Absent optional arguments are omitted, never `null` | Presence with a null value must not differ from absence |
| `D-6` | Numbers canonicalised to shortest round-trip form | Cross-language formatting differs |

> **`D-3` is the rule that gets forgotten**, and its failure is invisible. Include the provider-assigned identifier and every descriptor is unique, loop detection never fires, and the symptom presents to the user as *"the agent got stuck"* rather than as a descriptor defect.

---

## 6. Budgets, reservations and leases

A budget is a vector — cost, tokens, wall-clock, turns, depth, concurrency — and a bound is a **lease**, not a constant. A lease is reserved before an effect, committed at its receipt, and released on every path including creation failure.

**`EvaluationBudget` is a sibling dimension**, covering evaluator compute, wall-clock and human adjudication time. Both lineages of the pre-v4 corpus budgeted the agent meticulously and the evaluator not at all. Under best-of-N with per-branch verification, evaluation compute routinely exceeds generation compute — so without this, cost accounting is structurally wrong from the very first experiment, and human-gated paths become the throughput ceiling invisibly.

| # | Rule |
|---|---|
| `CT-29` | Every reservation carries its lease identifier into the effect and into the receipt |
| `CT-30` | A denial names the offending call, not the following one |
| `CT-31` | Enforcement is exact at commit, not instantaneous. A single in-flight call may overrun; the overrun is debited and the ceiling moves |
| `CT-32` | Evaluation and human-adjudication time are budgeted dimensions, not untracked overhead |

---

## 7. Tools

A tool declares its name, its required capability, its argument schema, and its **read set and write set**. There is no commutativity flag: commutativity is a property of the resource, not the verb, and a static boolean on a verb is false as soon as the resource is a queue, a clock or a remote service.

Independence for parallel execution is established either by an explicit independence group or by demonstrably disjoint read and write sets over a common snapshot (`03 §8`). The frozen atom set and its rules are owned by `03 §7.4`.

---

## 8. The model interface

The wire shape for tool-calling is specified explicitly because it has broken more than once in practice: an assistant message carrying the tool calls **must** precede the results, and each result **must** carry the call identifier it answers.

| # | Rule |
|---|---|
| `CT-33` | A provider adapter **never throws** for a provider-side failure. It returns a reply marked as instrument error with an error kind |
| `CT-34` | Throwing is reserved for programmer error, such as a malformed request |

`CT-33` is what makes "instrument error is not task failure" mechanical rather than aspirational. If a rate limit propagates as an exception, every call site must remember to classify it, and one that forgets silently depresses a measured arm.

> **The generalisable lesson.** A mock built by reading your own consumer code proves the harness is *self-consistent*; it cannot prove the harness agrees with a real endpoint. Any parser assumption a real model would violate is precisely the shape the mock was taught to avoid. The three model paths and their division of labour are owned by `01 §4`.

---

## 9. Task, plan, proposal, effect request

Deferring autonomy is correct. Deferring the contracts autonomy will require is not — because without them the first implementation becomes the loop, and the later planner is grafted in as conditionals inside it.

Four separate types, from the first schema version:

| Type | Is |
|---|---|
| `TaskSpec` | What is being asked, with its acceptance conditions |
| `PlanArtifact` | A proposed approach, evaluable **without executing any effect** |
| `Proposal` | What an operator produced this turn |
| `EffectRequest` | What is submitted to the broker for authorisation |

Plus: explicit hypothesis, evidence, decision and stop states; branch and fork parentage; plan evaluators that execute no effects; role-specific capability grants; and a trajectory that records **which operator produced which proposal**. That last point is what makes credit assignment possible at all.

An operator (`03 §5.2`) receives no effect capabilities by default. If it must observe the environment it receives a scoped read-only grant. Mutating effects remain proposals to the broker, always.

---

## 10. The competence and evidence graph

### 10.1 Why a graph

An array of entries cannot express contradiction between entries, partial supersession, per-domain activation, quarantine, or lineage-preserving forgetting. A typed graph expresses all of them, and history is never destroyed: forgetting removes an artifact from the active view and preserves its lineage.

Artifacts are classified into four quadrants — representations, operators, methods, primitives — which survive as a **typed projection** of the graph rather than as the store itself.

> A recalled fact is not automatically a representation. It is first a claim in the evidence graph. A representation is a reusable artifact, not any remembered sentence.

### 10.2 The contracts

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

Typed edges: `derived_from`, `requires`, `supersedes`, `contradicts`, `evaluated_by`, `valid_under`. States: `candidate`, `active`, `quarantined`, `deprecated`, `retired`.

### 10.3 Invalidation conditions

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

> **`INV-1`.** A claim or artifact that cannot state what would refute it is **not admissible**. An empty array fails validation at parse time.
>
> **`INV-2`.** An artifact promoted to `active` carries **at least one** condition with `checkKind: "automatic"`. Candidate and quarantined artifacts may carry only scheduled or manual conditions. Without `INV-2`, a wholly manual artifact satisfies `INV-1` and still falsifies `02 [C-12]`, whose falsifier is precisely *"staleness discovered only by scheduled human review."*

The greatest risk in a system that accumulates competence is not forgetting true knowledge. It is **generalising true knowledge beyond the domain where it was proven.** A validity domain records where a claim held; invalidation conditions record what would show it no longer holds. That is the operational form of falsifiability, and it is the difference between stale competence being detected automatically and being detected by a review that nobody schedules.

### 10.4 Lifecycle rules

| # | Rule |
|---|---|
| `CT-35` | Artifacts are immutable. Status and activation live in separate records |
| `CT-36` | `retired` removes from the activation set; it never deletes lineage |
| `CT-37` | `quarantined` blocks automatic selection |
| `CT-38` | Expired evidence is not deleted; it loses eligibility |
| `CT-39` | A new version never alters the evidence attached to its predecessor |
| `CT-53` | **No mutable field appears inside a content-addressed artifact.** Check state, status and activation live in separate keyed records. A `lastChecked` timestamp embedded in the artifact would change its digest on every check, which is `CT-35` violated by a field nobody noticed |

---

## 11. The instrument tuple

The tuple that identifies a measurement context — schema version, environment profile, substrate profile, evaluator identity and protocol, dataset split, task manifest — travels with every claim. Its composition and use are owned by `07 §5`; its shape is fixed here so that a cross-version comparison is representable as a tuple delta rather than as an undetected apples-to-oranges comparison.

---

## 12. The event stream

### 12.1 The envelope

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

**On `scope`.** Approvals, candidate attestations, canary promotions and rollbacks occur outside any episode — `03 §12` states the Evolution plane has no Phase 0 runtime component at all. Forcing a synthetic run identifier onto them would put fiction in the ledger to satisfy a schema. The discriminator makes the requirement conditional and keeps the correlation honest.

The tenancy and data-policy fields are not optional and are not deferred. They support four projections that a single stream must serve: encrypted raw audit, redacted operational trace, content-free metrics, and training examples **only** after a separate corpus opt-in.

### 12.2 The minimum event set

Episode lifecycle: `EpisodeStarted`, `EpisodeStateChanged`, `EpisodeCompleted`.
Observation and cognition: `ObservationRequested`, `ObservationProduced`, `OperatorSelected`, `OperatorInvoked`, `ProposalProduced`.
Authorisation: `AuthorizationRequested`, `CapabilityGranted`, **`AuthorizationDenied`**, `CapabilityRevoked`.
Budget: `BudgetReserved`, `BudgetCommitted`, `BudgetReleased`.
Effects: `EffectPreviewed`, **`EffectStarted`**, `EffectCompleted`, `EffectReconciled`, `ConflictDetected`.
Evidence: `EvaluationRequested`, `EvidenceClaimProduced`.
Competence: `ArtifactCreated`, `ActivationChanged`.
Human: `ApprovalRequested`, `ApprovalResolved`.
Liveness and recovery: `Heartbeat`, `RunRecovered`, `RunAborted`.
Evolution: `CandidateBuilt`, `CandidateAttested`, `CanaryPromoted`, `RollbackTriggered`.

`AuthorizationDenied` carries the reason, what was requested and what was grantable. Scope escalation is a first-class, alertable signal — not a log line.

`ConflictDetected` discharges `03 [CC-6]`: concurrent branches racing on one resource produce a record, never last-write-wins. `CapabilityRevoked` discharges the Control plane's revocation and kill-switch authority (`03 §3`); a revocation that leaves no event is indistinguishable from a grant that was never issued.

### 12.3 Storage

| # | Rule |
|---|---|
| `CT-40` | An embedded transactional store with write-ahead logging, fully synchronous on the critical ledger, single writer |
| `CT-41` | Versioned migrations; blobs addressed by digest outside the database |
| `CT-42` | Line-delimited JSON is **export, replay and interchange** — never the primary store |
| `CT-43` | The inspector reads through a port, never a partially written file |

Append-only files as the primary store fail on four counts: no atomic multi-record commit, torn writes on crash, no safe concurrent read during write, and no indices. A transactional embedded store solves all four for a small, one-off integration cost, and the export format survives unchanged.

### 12.4 Recovery events

A dead process promises nothing. `Heartbeat`, `RunRecovered` and `RunAborted` exist so that termination can be recorded **from outside** the failed process, and `EffectReconciled` carries a preserved-uncertainty state for external effects whose occurrence cannot be determined. The episode-level model is owned by `03 §9`, the controller's authority by `05`.

---

## 13. Port interfaces

Ports import domain types only. Adapters implement them and are imported only by the composition root.

| Port | Responsibility |
|---|---|
| `ModelProvider` | Inference; returns instrument errors rather than throwing (`CT-33`) |
| `EnvironmentAdapter` | The universal environment protocol (`03 §7.1`) |
| `OperatorRunner` | Invokes a versioned operator under a child budget |
| `EvaluatorPort` | Produces scoped claims; runs under a separate identity |
| `EventStore` | Append and read the durable ledger |
| `BlobStore` | Content-addressed bytes with a classification-keyed encryption hook |
| `ObservationSource` | Supplies labelled context blocks |
| `PolicyEngine` | Decides; does not execute |
| `Governor` | Budget reservation, commitment, release |
| `SandboxRunner` | Executes within a perimeter and returns a **containment report** |

`SandboxRunner` returns a structured report rather than a boolean. A single `isContained: true` claims a property the runtime cannot verify at that granularity; the report states runtime, namespace configuration, profiles, network enforcement, writable mounts, exposed sockets, resource limits, startup probes and attestation time, and the publication policy decides whether that is sufficient for a given claim.

---

## 14. Configuration schemas

Configuration is authored, so its rules differ from wire rules: **unknown fields are rejected at authoring time**, names resolve at composition, and a name that does not resolve fails the composition rather than the first use. Agent, harness, operator and playbook definitions are all configuration, and all freeze at composition.

---

## 15. Cross-language contract

Two implementations at the first lock: TypeScript and Python. Vectors are written **as data** at that lock — that is the durable artifact — and a third language is added when a third consumer exists, not before. There is no consumer for a systems language until the sandbox supervisor lands, and vectors validated against a single implementation are self-agreement rather than conformance.

Frames between processes carry a maximum size, a request identifier, version negotiation, a cancellation frame, backpressure, diagnostics on a separate channel, explicit content references for large payloads, and an authenticated channel wherever grants cross a process boundary.

---

## 16. Versioning and compatibility

| Class | Definition | Action |
|---|---|---|
| Additive | New optional field with a default; new event kind; new enum member in a non-exhaustively matched position | None |
| Compatible-breaking | Field made required; default changed; enum member removed; semantics changed | Minor bump plus migration |
| Incompatible | Field removed or retyped; event removed; envelope changed | Major bump plus corpus re-derivation |

| # | Rule |
|---|---|
| `CT-44` | Readers handle an unknown event kind by preserving it and continuing. An old inspector must not crash on a new event type |
| `CT-45` | Consumers do not exhaustively match on extensible enums without a default |
| `CT-46` | Every version bump ships a migration, even a no-op one, to establish the habit before it is needed |
| `CT-47` | **Every version bump runs a migration rehearsal in CI** against a synthetic corpus |
| `CT-48` | A corpus records the schema version it was derived under; it is valid only against readers of that version |
| `CT-49` | Event kinds are never removed from history |
| `CT-50` | A field is deprecated for at least one minor version before removal: marked, warned on write, still accepted on read |

`CT-47` closes a gap present in both pre-v4 lineages, which mandated versioned migrations and never rehearsed them. Untested migrations are discovered in year two, when the corpus is large and the failure is expensive.

---

## 17. Conformance

Every implementation in every language passes the same vectors. The suite has four distinct kinds, and none substitutes for another:

| Kind | Establishes |
|---|---|
| Vector conformance | Two implementations agree on parse, reject, canonical form and digest |
| Property tests | Algebraic laws hold — attenuation narrows, descriptors are stable, order is preserved |
| Round-trip tests | Unknown-field preservation and version tolerance |
| Must-fail tests | Each control can actually fail (`08 §5`) |

**A vector is never edited to make an implementation pass.** It changes only when the schema's semantics change, under a decision recorded in `09`.

---

## 18. What locks here

`04` carries three of the six irreversible decisions: the corpus format (§1, §10, §12), the wire interface definition (§0), and the seams (§15). The rest of the system can be rewritten. These cannot — they can only be migrated, and every migration is paid for by everything already recorded.

Therefore, one operational rule with no exceptions: **a schema marked draft in `schemas/v4/MANIFEST.md` may not be used to record anything intended to survive.** Recording production trajectories against a draft schema is a defect, not a shortcut.
