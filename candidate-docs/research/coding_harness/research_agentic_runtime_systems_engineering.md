# Research: Agentic Runtime Systems Engineering

## Causal Execution, Runtime Architecture, Recovery, Performance, Plugins, Memory, Fault Localization, and Tool-Oriented Agent Design

**Filename:** `research_agentic_runtime_systems_engineering.md`  
**Document class:** technical research synthesis / implementation-idea corpus  
**Posture:** non-normative research; not a roadmap, sprint plan, milestone plan, or implementation mandate  
**Companion document:** `research_harness_agentic_systems_engineering.md`  
**Source inspirations:** `GPT_SOL_MASTERPLAN_V0.9.0_beta.md`, `VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_OPUS_PLAN.md`, `VANGUARD_BACKEND_M1_M9_MASTER_REPORT.md`, `VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md`, `Higgs_update_concepts.md`, `masterplan_todo_rev1.md`

---

# Abstract

This report extracts a second, more implementation-oriented body of research from the Vanguard/AETHER backend reports.

The companion report, `research_harness_agentic_systems_engineering.md`, already covers the broad theory of harness engineering: harness-as-independent-variable, composition, Pareto control, Active Inference, stigmergic coordination, context projection, generic caching, retrieval, macro compilation, preference optimization, scientific methodology, multi-agent topologies, and provenance.

This document intentionally does **not** repeat those topics at introductory level.

Instead, it focuses on the lower-level systems questions that determine whether such ideas can be implemented efficiently and correctly:

- how to compile a declarative agent composition into an executable runtime;
- how to represent control, effects, results, and state transitions;
- how to design an event log without drowning in lifecycle ceremony;
- how to batch durable writes without weakening causal semantics;
- how to distinguish projection replay, deterministic decision replay, and continuation;
- how to prevent duplicate external effects after crashes;
- how to allocate sequence numbers under concurrency;
- how to separate observer instrumentation from controller authority;
- how to design plugin interfaces that survive process and language boundaries;
- how to preserve semantics across stdio, HTTP, WebSocket, gRPC, or in-process execution;
- how to make artifact capture asynchronous without publishing non-durable references;
- how to implement durable memory with authorization-before-ranking;
- how to classify failures and perform typed retry instead of blind retry;
- how to combine fault localization, test selection, static structure, and model reasoning;
- how to measure event amplification, checkpoint utility, write throughput, and useful concurrency;
- how to make multi-role execution deterministic and exactly-once at the logical level;
- how to reason about CoW workspaces, process-level parallelism, mutation testing, CEGIS, and other optional advanced techniques.

The central thesis of this report is:

> **The quality of an agentic system depends not only on what the agent decides, but on the semantics and economics of the runtime that turns decisions into durable, recoverable, attributable effects.**

---

# 1. Non-Overlap Contract With the Companion Research

The following topics are intentionally treated as already documented and are not reintroduced here except when necessary to support a deeper systems mechanism:

- harness as independent variable;
- model vs agent vs harness distinction;
- A-B-C-D conceptual foundation;
- Pareto routing at conceptual level;
- VFE vs EFE;
- stigmergic coordination as a general pattern;
- general context-layer hierarchy;
- generic prompt-prefix caching;
- generic AST repository maps;
- hybrid dense + lexical retrieval;
- generic skill scoring;
- DPO mathematics;
- macro-tool compilation;
- generic experiment design;
- exact McNemar;
- generic provenance identities;
- general multi-agent topology catalog.

This report instead asks:

> What machinery must exist underneath those ideas so that they remain fast, deterministic, recoverable, auditable, and composable?

---

# 2. The Runtime as a Compilation Pipeline

A recurring idea in the source corpus is that a declarative manifest should not be executed directly.

A stronger systems model is:

```text
Authored Configuration
        ↓
Canonical Manifest
        ↓
Normalized ComponentGraph
        ↓
FrozenComposition
        ↓
ActivationPlan
        ↓
RunPlan
        ↓
Episode / Scheduler
        ↓
Effects + Events + Artifacts
```

Each stage answers a different question.

## 2.1 Canonical Manifest

Represents authored intent.

Examples:

- component names;
- interfaces;
- bindings;
- policy references;
- model routes;
- declared capabilities;
- requested isolation.

It may have compatibility frontends, but those frontends should normalize to one canonical representation.

## 2.2 Normalized ComponentGraph

Removes authoring syntax and exposes semantic structure:

```python
@dataclass(frozen=True)
class ComponentNode:
    id: str
    interface_id: str
    implementation_ref: str
    config_digest: str
    requested_capabilities: tuple[str, ...]

@dataclass(frozen=True)
class Binding:
    source: str
    target: str
    interface_id: str
    relation: str

@dataclass(frozen=True)
class ComponentGraph:
    nodes: tuple[ComponentNode, ...]
    bindings: tuple[Binding, ...]
```

This representation should contain no runtime objects, sockets, process handles, open files, or provider sessions.

It is pure identity-bearing configuration.

## 2.3 FrozenComposition

A `FrozenComposition` binds every behavior-affecting configuration input.

Conceptually:

\[
D_H = H(\operatorname{canonical}(G, P, C, I))
\]

where:

- \(G\): normalized graph;
- \(P\): policies;
- \(C\): effective capability ceilings;
- \(I\): implementation identities.

Important property:

> Two executions with the same `FrozenComposition` should have the same intended behavioral configuration even if they happen at different times.

## 2.4 ActivationPlan

The `ActivationPlan` is where declarative intent becomes an executable process topology.

It resolves:

- concrete plugin implementation;
- process/in-process/container boundary;
- interface version;
- lifecycle order;
- cleanup order;
- capability attenuation;
- provider factory;
- environment adapter;
- ports;
- optional dependencies;
- health/readiness probes.

Example:

```python
@dataclass(frozen=True)
class ActivationUnit:
    component_id: str
    implementation: str
    interface_id: str
    isolation: str
    effective_capabilities: tuple[str, ...]
    dependencies: tuple[str, ...]
    start_order: int
    stop_order: int

@dataclass(frozen=True)
class ActivationPlan:
    units: tuple[ActivationUnit, ...]
    composition_digest: str
```

This is a crucial conceptual boundary:

> The graph describes **what is connected**. The activation plan describes **what must exist at runtime to make those connections real**.

## 2.5 RunPlan

A `RunPlan` binds runtime-specific identity:

- task;
- model/provider;
- environment;
- evaluator;
- budget;
- effective overrides;
- persistence configuration;
- capture configuration.

Possible identity:

\[
D_R =
H(
D_H \parallel
D_{task} \parallel
D_{model} \parallel
D_{env} \parallel
D_{eval} \parallel
D_{effective\_config}
).
\]

The distinction between `FrozenComposition` and `RunPlan` is useful because model route or workspace may vary without redefining the conceptual agent composition.

---

# 3. Composition Correctness Is End-to-End, Not Parser-Level

A subtle but important systems insight from the reports is:

> A declarative graph that can be parsed and hashed but does not determine activation, invocation, lifecycle, failure, and cleanup is metadata—not runtime architecture.

A useful generality test is therefore:

```text
parse
→ normalize
→ freeze identity
→ activate components
→ wire interfaces
→ execute
→ fail/recover
→ stop/cleanup
```

A composition abstraction should be considered real only if all of those transitions are controlled by it.

## 3.1 Graph-Liveness Property

For every node \(v\) required by an execution path:

\[
required(v) \Rightarrow
activated(v)
\land
interface\_compatible(v)
\land
cleanup\_reachable(v).
\]

## 3.2 Edge-Liveness Property

For each binding \(e=(u,v)\):

\[
binding(e)
\Rightarrow
resolved(e)
\land
authorized(e)
\land
version\_compatible(e).
\]

## 3.3 No Shadow Wiring

A useful falsifier:

> If changing a graph binding does not change the runtime wiring or execution identity, the graph is not authoritative.

---

# 4. A Minimal Public Mental Model: Five Verbs

The internal runtime may be sophisticated, but the public mental model can remain:

```text
Observe
→ Decide
→ Authorize
→ Execute
→ Record
```

This is intentionally simpler than a deep internal dispatch pipeline.

## 4.1 Minimal Execution Pseudocode

```python
def execute(command, runtime):
    run = runtime.resolve(command)

    observation = runtime.observe(run.scope)
    proposal = run.agent.decide(observation)

    decision = runtime.kernel.authorize(
        proposal,
        authority=run.authority,
        budget=run.budget,
    )

    if decision.denied:
        return runtime.record_denial(
            run=run,
            proposal=proposal,
            decision=decision,
        )

    reservation = runtime.kernel.reserve(decision)

    try:
        receipt = runtime.effects.execute(decision.operation)
    except Exception as exc:
        receipt = classify_effect_failure(exc)

    settlement = runtime.kernel.settle(
        reservation=reservation,
        receipt=receipt,
    )

    return runtime.record_result(
        run=run,
        receipt=receipt,
        settlement=settlement,
    )
```

The key invariant is ordering:

\[
Authorize < ExternalEffect < Settlement < ResultPublication.
\]

---

# 5. Command → Events → Result as a Universal Logical Contract

A useful transport-independent abstraction is:

```text
Command
   ↓
ordered causal events
   ↓
Result + Artifact References
```

## 5.1 Command

```python
class Command:
    command_id: str
    project_id: str
    run_id: str
    operation: str
    payload: object
    idempotency_key: str | None
    expected_state_digest: str | None
```

## 5.2 Result

```python
class Result:
    run_id: str
    status: str
    value: object | None
    artifact_refs: tuple[str, ...]
    state_digest: str
    terminal_event_id: str
    diagnostics: tuple[object, ...]
```

The result is a projection over history.

It does not replace the history.

## 5.3 Event Order

For independent causal lineages, global total order is usually unnecessary.

A more scalable rule is:

\[
e_i \prec e_j
\]

only when:

- they belong to the same causal stream; or
- an explicit dependency joins their streams.

This suggests per-lineage ordering with explicit join events rather than forcing one global sequence across all independent work.

---

# 6. Compact Semantic Event Grammar

A practical event grammar extracted from the reports:

```text
RunRequested
→ CompositionResolved
→ RunStarted

→ ObservationRecorded*
→ DecisionProposed

→ AuthorizationGranted | AuthorizationDenied

→ BudgetReserved?
→ EffectStarted?
→ EffectCompleted | EffectFailed | EffectUnknown?
→ BudgetCommitted | BudgetReleased?

→ ArtifactRecorded*

→ ChildSpawned / ChildSettled*

→ RunCompleted | RunFailed | RunStopped | RunSuspended
```

Telemetry events may be sampled.

Authority, effect, settlement, and terminal facts should not be sampled when they are part of causal truth.

---

# 7. Semantic Events vs Lifecycle Ceremony

One of the most concrete findings in the source corpus is that event-sourced systems can become slow not because event sourcing is intrinsically expensive, but because **the event grammar contains too much ceremonial detail**.

A measured example reported:

- 90 events in a minimal episode;
- 72 plugin lifecycle events;
- ~80% of event count;
- ~74% of envelope bytes.

This motivates a formal metric.

## 7.1 Event Amplification Coefficient

Define:

\[
A_E =
\frac{N_{events}}
{N_{semantic\_operations}}.
\]

Similarly, byte amplification:

\[
A_B =
\frac{B_{ledger}}
{B_{semantic\_payload}}.
\]

High \(A_E\) is not automatically bad: auditability can require many facts.

But it becomes suspicious when most events are mechanically predictable from one already-digested structure.

## 7.2 Lifecycle Compression

Instead of emitting six lifecycle events for every configured component on every run:

```text
PluginDiscovered
PluginResolved
PluginVerified
PluginActivated
PluginQuiesced
PluginRetired
```

one can maintain modes:

```text
full
summary
off
```

Research interpretation:

- `full`: every transition;
- `summary`: semantically relevant transitions + one digest of full lifecycle;
- `off`: no lifecycle telemetry, only when no lifecycle claim is needed.

## 7.3 Digest-Backed Summary

```python
full_record = canonicalize(all_component_transitions)
summary = {
    "active_components": active_component_ids,
    "full_lifecycle_digest": sha256(full_record),
    "state_machine_version": lifecycle_version,
}
emit("RegistryComposed", summary)
```

This preserves the ability to prove what lifecycle definition was used without multiplying every run by predictable rows.

---

# 8. The Economics of Durable Event Appends

A central measured defect in the source corpus was not event serialization but **fsync frequency**.

When each event produces an independent durable append:

\[
T_{write}
\approx
N_e
(
t_{encode}
+
t_{hash}
+
t_{sql}
+
t_{fsync}
).
\]

If \(t_{fsync}\) dominates:

\[
T_{write}
\approx
N_e t_{fsync}.
\]

This creates linear latency in event count even when events are tiny.

## 8.1 Group Commit

If events are batched into \(B\) durability groups:

\[
T_{write}
\approx
N_e(t_{encode}+t_{hash}+t_{sql})
+
B t_{fsync}.
\]

For \(B \ll N_e\), the improvement can be large without weakening the storage engine's durability mode.

The source measurements reported approximately:

- 519 events/s with SQLite WAL `synchronous=FULL`, one-by-one;
- 3,949 events/s with the same durability mode, batched.

The key engineering lesson is:

> **Batch the durability boundary, not the identity computation.**

---

# 9. Per-Turn Group Commit

A natural batch boundary in agent systems is the logical turn.

```python
class TurnBuffer:
    def __init__(self):
        self.events = []

    def emit(self, event):
        # Digest and order immediately.
        event = assign_identity(event)
        self.events.append(event)

    def commit(self, store):
        if not self.events:
            return
        store.append(self.events)
        self.events.clear()
```

Important invariants:

1. event digest computed before buffering;
2. event order fixed before buffering;
3. append rejection fails closed;
4. effect intent and effect settlement needed for recovery should share a safe durability boundary;
5. terminal state forces flush.

## 9.1 Crash Envelope

With per-turn group commit, the crash-loss window is approximately one uncommitted turn.

This is acceptable only if recovery semantics can reconcile open durable intents.

A design should explicitly model:

\[
LossWindow \le 1\ turn
\]

rather than claiming event-level durability if that is no longer true.

---

# 10. Turn-Boundary Commit Pseudocode

```python
def execute_turn(session):
    batch = EventBatch()

    observation = session.observe()
    batch.emit(ObservationRecorded(observation.ref))

    proposal = session.propose(observation)
    batch.emit(DecisionProposed(proposal.ref))

    decision = session.authorize(proposal)
    batch.emit(event_for(decision))

    if decision.denied:
        batch.emit(TurnSettled(status="denied"))
        batch.commit(session.store)
        return

    reservation = session.reserve(decision)
    batch.emit(BudgetReserved(reservation.id))

    intent = session.record_effect_intent(decision)
    batch.emit(intent)

    # If intent must survive process death before effect execution,
    # flush here or use an explicit sub-boundary.
    batch.commit(session.store)

    receipt = session.execute_effect(decision)

    batch.emit(event_for(receipt))
    batch.emit(event_for(session.settle(reservation, receipt)))
    batch.commit(session.store)
```

This illustrates that “per-turn” does not necessarily mean one fsync for the entire turn.

External-effect safety may require a **pre-effect intent barrier** plus a post-effect settlement barrier.

---

# 11. Optimal Commit Granularity as a Cost Function

Derived research extension.

Let:

- \(L\): expected latency cost;
- \(R\): expected recovery cost;
- \(P_c\): probability of crash inside a commit window;
- \(W\): lost/reconciliation work per crash;
- \(B\): number of commit batches.

Then:

\[
J(B)
=
B t_{fsync}
+
P_c(B) W(B).
\]

The optimal durability granularity is:

\[
B^*
=
\arg\min_B J(B)
\]

subject to semantic constraints on external effects.

This is a more precise way to reason about per-event vs per-turn vs per-operation durability.

---

# 12. Sequence Allocation Under Concurrency

A reported concurrency failure exposed a classic race:

```text
read current seq
increment locally
append
```

Two writers can observe the same prior sequence.

Formally:

\[
read_A(s)=n,\qquad read_B(s)=n
\]

then:

\[
write_A(n+1),\qquad write_B(n+1).
\]

Monotonicity checks correctly reject one of them, but the error occurs late.

## 12.1 Three Architectures

### A. Enforced Single Writer

The simplest model:

```text
many workers
   ↓ proposals
single ledger writer
   ↓
ordered append
```

Strength:

- trivial sequence correctness;
- deterministic ordering;
- simple recovery.

Cost:

- centralized write serialization.

### B. Transactional Sequence Allocation

Allocate sequence numbers inside the SQLite transaction:

```sql
BEGIN IMMEDIATE;
SELECT last_seq FROM project_sequence WHERE project_id=?;
UPDATE project_sequence SET last_seq=last_seq+1 WHERE project_id=?;
INSERT INTO events(... seq=last_seq+1 ...);
COMMIT;
```

Better implementations avoid select/update races via an atomic `RETURNING` operation.

### C. Per-Lineage Sequences

If global ordering is unnecessary:

```text
(project_id, lineage_id, seq)
```

Cross-lineage synchronization is represented explicitly through dependency events.

This reduces contention substantially.

---

# 13. Process-Level Parallelism vs Thread-Level Parallelism

The reports include a measurement where thread-level parallelism peaked at two workers and regressed at four.

The explanation included:

- Python GIL;
- subprocess-heavy verification;
- increased contention.

For agent systems, most expensive work is often:

- model I/O;
- tool subprocesses;
- sandbox setup;
- filesystem access.

Threads can still help for network-bound phases.

But CPU-heavy orchestration, parsing, compression, and verification may require process isolation.

A general model:

\[
Throughput(n)
=
\frac{n}
{T_{serial}+T_{parallel}/n+T_{contention}(n)}.
\]

Unlike ideal Amdahl scaling, \(T_{contention}(n)\) often rises quickly in agent runtimes.

Therefore maximum worker count should be measured, not inferred from CPU count.

---

# 14. Concurrency as a Conflict-Graph Problem

Instead of “enable parallel execution”, derive safe parallelism from actual effects.

For pending operations \(o_i\), define conflict:

\[
C_{ij}
=
\begin{cases}
1 & \text{if selectors overlap and at least one operation mutates}\\
0 & \text{otherwise}
\end{cases}
\]

Then construct conflict graph:

\[
G_C=(O,E_C).
\]

Operations in an independent set can run concurrently.

## 14.1 Static Selector Approximation

```python
def conflicts(a, b):
    if not selectors_overlap(a.selector, b.selector):
        return False
    return a.is_write or b.is_write
```

## 14.2 Dynamic Effect Observation

Static paths can be overly conservative.

Record actual resolved resources:

```text
EffectStarted:
  declared_selector=/workspace/**
  resolved_resource=/workspace/src/foo.py
```

Repeated measurements can estimate:

\[
P(conflict \mid operation\_classes).
\]

This supports selective concurrency without inventing a broad scheduler prematurely.

---

# 15. Concurrency Value Function

Derived extension.

Let:

- \(S_n\): speedup at \(n\) workers;
- \(C_n\): additional cost;
- \(F_n\): failure/retry overhead;
- \(R_n\): recovery complexity.

A useful score:

\[
V_n =
\frac{S_n}
{1+\lambda_c C_n+\lambda_f F_n+\lambda_r R_n}.
\]

Parallelism should be enabled only where \(V_n\) beats the sequential baseline materially.

---

# 16. Replay Is Three Different Mechanisms

The source material makes an important distinction often lost in event-sourced architectures.

## 16.1 Projection Rebuild

```text
events
  ↓ fold
derived state
```

This proves that state can be reconstructed.

It does not prove that agent decisions would repeat.

## 16.2 Deterministic Decision Replay

```text
historical state
  ↓ controller
predicted command
  ↓ compare
historical command
```

This detects behavioral drift after code changes.

Useful rule:

\[
command_{replayed}(s_t)
=
command_{historical}(s_t).
\]

A mismatch is a replay incompatibility.

## 16.3 Continuation

Continuation asks:

> After a crash, what work is incomplete, what effects are known complete, and what can safely resume?

This is a different problem from fold/replay.

---

# 17. Durable Intent and Exactly-Once Logical Effects

External effects are dangerous because a crash can occur between execution and settlement recording.

The critical states are:

```text
NO_INTENT
INTENT_DURABLE
EFFECT_MAY_HAVE_RUN
RECEIPT_DURABLE
SETTLED
```

## 17.1 Crash Cases

### Crash before durable intent

Safe to retry from scratch.

### Crash after intent, before effect

Usually safe to execute.

### Crash after external effect, before receipt

Ambiguous.

Must reconcile.

### Crash after receipt, before settlement projection

Do not execute again.

Re-fold and settle.

## 17.2 Reconciliation Interface

```python
class EffectAdapter:
    def execute(self, request) -> Receipt: ...
    def reconcile(self, intent) -> Receipt | Unknown: ...
    def compensate(self, receipt) -> Receipt | Unsupported: ...
```

This is more robust than a generic retry loop.

---

# 18. Idempotency Keys

For logical operation \(o\):

\[
K_{idem}
=
H(
run\_id
\parallel operation\_identity
\parallel attempt\_identity
).
\]

Adapters that support idempotency should reject repeated execution under the same key or return the prior result.

The runtime rule:

```python
if store.has_settled(idempotency_key):
    return store.prior_receipt(idempotency_key)

if store.has_open_intent(idempotency_key):
    return reconcile(open_intent)

return execute_new_attempt()
```

---

# 19. Unknown Settlement Is a First-Class State

Many systems incorrectly collapse unknown into failure.

But:

```text
FAILED
```

means the effect is known not to have produced the intended result.

```text
UNKNOWN
```

means the runtime cannot establish whether it did.

These require different recovery logic.

Unsafe rule:

```python
if not success:
    retry()
```

Safe rule:

```python
match result.state:
    case "failed":
        maybe_retry()
    case "unknown":
        reconcile_or_stop()
```

---

# 20. Child Execution and Kill-Tree Semantics

Recursive agents require parent-child cancellation semantics.

Parent termination should not simply kill everything blindly.

A child can be:

```text
NOT_STARTED
RUNNING
SETTLED
UNKNOWN
CANCEL_REQUESTED
CANCELLED
```

## 20.1 Kill Tree

```python
def stop_tree(root):
    descendants = reverse_topological_descendants(root)

    for child in descendants:
        if child.settled:
            continue

        request_cancel(child)

        if child.effect_open:
            reconcile(child)

    stop(root)
```

Important property:

> Already-settled child work must never be retried merely because the parent died.

---

# 21. Checkpoints Are Performance Caches, Not Truth

A checkpoint can reduce reconstruction work, but correctness should derive from the event history.

A checkpoint:

\[
CP_k =
(state_k, seq_k, reducer\_version, digest).
\]

Recovery:

\[
state_n =
fold(CP_k, events_{k+1:n}).
\]

## 21.1 Break-Even Condition

Let:

- \(T_f(N)\): full fold time for \(N\) events;
- \(T_{cp}\): checkpoint decode/validation;
- \(T_s(M)\): suffix fold for \(M\) events.

Checkpoint is useful when:

\[
T_{cp}+T_s(M)<T_f(N).
\]

One source measurement showed only ~1.04× improvement for a 10,000-event history with a 9,000-event checkpoint.

That suggests checkpoint complexity should be justified by representative state size, not event count alone.

---

# 22. Adaptive Checkpoint Placement

Derived extension.

Checkpointing every fixed \(K\) events is crude.

A better trigger can be based on reconstruction cost:

```python
if estimated_fold_cost(events_since_checkpoint) > target_recovery_ms:
    checkpoint()
```

Or state size:

```python
if serialized_projection_bytes > size_threshold:
    checkpoint()
```

Or external lifecycle boundary:

```text
before deployment
after child fan-in
after large compaction
before long suspension
```

---

# 23. Blob-First, Event-Second Artifact Capture

A recurring correctness principle:

```text
capture bytes
→ redact / transform
→ persist retained bytes
→ compute content identity
→ emit event reference
→ publish result
```

The causal record must never refer to bytes that are not durable.

Unsafe:

```text
emit ArtifactRecorded(hash=future_hash)
→ async upload
```

If the process dies, the event points to missing content.

Safe:

```python
blob_ref = blob_store.put(retained_bytes)
assert blob_store.exists(blob_ref)

emit(ArtifactRecorded(ref=blob_ref))
```

---

# 24. Asynchronous Artifact Capture With a Completion Barrier

Asynchronous persistence can still be safe if publication waits on a barrier.

```python
future = artifact_pool.submit(store_blob, data)

# Other independent computation can continue.

blob_ref = future.result()  # durability barrier
emit(ArtifactRecorded(ref=blob_ref))
```

General rule:

> Parallelize expensive preparation, not authoritative publication.

---

# 25. Capture, Telemetry, Retention, Evaluation, and Control Are Different Axes

A significant insight from the backend audit is that execution presets often bundle orthogonal concerns.

These should be independently configurable:

```yaml
capture:
  prompts: full
  context: full
  outputs: full
  tools: full
  patches: full

telemetry:
  traces: sampled
  metrics: basic

recovery:
  events: durable
  checkpoints: adaptive

evaluation:
  evaluators: []
  repetitions: 1

control:
  allowed: [accept, reject, retry]

retention:
  artifacts: standard
  events: durable

containment:
  backend: sandbox

approval:
  default: ask
```

The exact YAML is illustrative.

The deeper principle is:

\[
EffectiveConfig =
Capture
\times Telemetry
\times Recovery
\times Evaluation
\times Control
\times Retention
\times Containment
\times Approval.
\]

Named profiles should be presets over this Cartesian product rather than indivisible “modes”.

---

# 26. Capture Is Not Retention

These are frequently confused.

## Capture Policy

Answers:

> May these bytes be persisted at all?

## Retention Policy

Answers:

> If persisted, for how long and under what lifecycle?

Example:

```text
prompt:
  capture = redact_and_store
  retention = 7_days
```

versus:

```text
secret-bearing tool output:
  capture = digest_only
  retention = permanent_digest
```

---

# 27. Privacy Before Content Addressing

If sensitive bytes must be redacted, digesting should normally occur **after** applying the declared retained representation.

```text
raw bytes
→ sensitivity classifier
→ redaction/transformation
→ retained bytes
→ digest
→ persistence
```

Otherwise a content hash may identify content that the system is not permitted to retain or reconstruct.

The system may separately record a protected source digest if policy explicitly permits it.

---

# 28. Observer vs Controller Interceptors

The reports identify an important missing abstraction: lifecycle interception.

Observer hooks:

```text
before_operation
after_operation
on_event
after_result
on_failure
```

Observers can:

- trace;
- collect metrics;
- record diagnostics;
- sample payload metadata.

They must not change control flow.

Controllers are different.

Possible closed vocabulary:

```text
ACCEPT
REJECT
RETRY
REDIRECT
FORK
STOP
```

## 28.1 Why a Closed Vocabulary?

Arbitrary callback return values create implicit control semantics.

A closed algebra makes conflicts explicit.

```python
ControlDecision = Literal[
    "ACCEPT",
    "REJECT",
    "RETRY",
    "REDIRECT",
    "FORK",
    "STOP",
]
```

Unsupported values fail closed.

---

# 29. Controller Conflict Resolution

If multiple controllers exist, registration order must not silently determine behavior.

Possible policies:

## Lexicographic

```text
STOP > REJECT > FORK > REDIRECT > RETRY > ACCEPT
```

## Veto-Based

Any `REJECT` blocks.

## Capability-Weighted

Only controllers holding a specific authority may return certain decisions.

## Consensus

Require quorum for selected decisions.

A conflict event should be observable:

```python
ControllerConflict(
    decisions=...,
    resolution_policy=...,
    final_decision=...,
)
```

---

# 30. `before_commit` Is Not an Ordinary Hook

A hook before authoritative publication is security-sensitive.

If it can prevent or redirect a commit, it is a controller, not an observer.

This yields a useful classification:

```text
observation hook:
  cannot modify authoritative outcome

control hook:
  can modify future execution

commit hook:
  can prevent authoritative publication
```

Each deserves different capability requirements.

---

# 31. Plugin Contract Families

Rather than one universal `Plugin` interface, use semantically distinct families.

## Model Plugin

```python
propose(context) -> ModelResponse
```

## Tool Plugin

```python
describe() -> ToolDescriptor
execute(request) -> ToolReceipt
```

## Context Plugin

```python
compile(task, state, budget) -> ContextBundle
```

## Compaction Plugin

```python
compact(context, policy) -> CompactedContext
```

## Retrieval Plugin

```python
query(request, authorized_scope) -> RankedEvidence
```

## Memory Plugin

```python
store(fact)
query(scope, request)
revoke(id)
```

## Policy Plugin

```python
decide(observation) -> PolicyDecision
```

## Evaluator Plugin

```python
evaluate(subject_ref, witness_contract) -> Evaluation
```

## Scheduling Plugin

```python
ready(state) -> tuple[OperationRef, ...]
```

## Sandbox Plugin

```python
run(effect, ceiling) -> SandboxedReceipt
```

This avoids the “god plugin” anti-pattern.

---

# 32. Portable Interface Descriptor

A plugin boundary should be definable without Python-specific classes.

Minimum descriptor:

```text
interface_id
version_range
request_schema
response_schema
error_taxonomy
cancellation_semantics
deadline_semantics
idempotency_semantics
streaming_mode
capability_requirements
lifecycle_contract
```

Example:

```yaml
interface_id: tool.exec/2
version_range: ">=2,<3"
request_schema: schemas/tool_exec_request.json
response_schema: schemas/tool_exec_receipt.json
cancellation: cooperative
idempotency: key_required
streaming: none
capabilities:
  - proc.exec
lifecycle:
  start: required
  health: optional
  stop: required
```

This makes WIT/gRPC/JSON-RPC generation possible later.

---

# 33. Plugin Lifecycle State Machine

Possible lifecycle:

```text
DISCOVERED
→ VERIFIED
→ ACTIVATED
→ HEALTHY
→ QUIESCING
→ QUIESCED
→ RETIRED
```

Failure side states:

```text
QUARANTINED
FAULTED
INCOMPATIBLE
```

## 33.1 Activation Pseudocode

```python
candidate = discover_plugin(path)

verification = verify_plugin(
    manifest=candidate.manifest,
    schema=plugin_schema,
    digest=candidate.content_digest,
    signature=candidate.signature,
    runtime_compatibility=current_runtime,
)

if not verification.ok:
    quarantine(candidate)
    return PluginFailure("verification_failed")

effective_scope = attenuate(
    configured_ceiling,
    candidate.requested_scope,
)

if not authority_available(effective_scope):
    return PluginFailure("authority_unavailable")

service = activate(candidate, effective_scope)

if service is None:
    return PluginFailure("activation_without_service")

persist_activation_receipt(
    plugin_digest=candidate.content_digest,
    effective_scope=effective_scope,
    service_identity=service.identity,
)
```

---

# 34. Plugin Cleanup Must Be Total

Every activation must have exactly one cleanup path.

For every activated component \(c\):

\[
activated(c)
\Rightarrow
eventually(
retired(c)
\lor faulted(c)
).
\]

This should hold across:

- normal completion;
- compose failure;
- cancellation;
- plugin crash;
- evaluator failure;
- parent process exception.

Reverse-topological cleanup is a useful default when dependencies exist.

---

# 35. Transport Equivalence

A runtime may expose:

- in-process API;
- stdio;
- HTTP;
- WebSocket;
- gRPC.

These should not become separate semantics.

## 35.1 Equivalence Rule

Equivalent commands under equivalent effective configuration should produce semantically equivalent causal histories.

Not byte-identical histories.

Transport-specific fields can differ.

Formally:

\[
Semantics(E_{local})
=
Semantics(E_{stdio})
=
Semantics(E_{http}).
\]

## 35.2 In-Process Fast Path

Local callers should not serialize to JSON and deserialize immediately.

```python
if transport == "in_process":
    result = service.execute(command_object)
```

Transport adapters own serialization only at actual process/network boundaries.

---

# 36. Stdio Framing

Simple robust framing:

```text
<length>\n
<json bytes>
```

or JSONL if payloads are bounded and escaping rules are strict.

Each message should carry:

- schema version;
- command ID;
- correlation ID;
- deadline;
- idempotency key.

---

# 37. Streaming Event Contract

For HTTP/WebSocket/gRPC streaming:

```text
CommandAccepted
Event*
TerminalResult
```

Client resumption:

```python
stream(run_id, after_event_id=last_seen)
```

This allows reconnectable UI without duplicating execution.

---

# 38. Polyglot Replacement as Differential Equivalence

The source corpus proposes a staged polyglot boundary rather than rewriting the system.

A candidate implementation in Rust/Go/TypeScript must produce equivalent semantics.

## 38.1 Golden Vector Gate

Given identical input vector \(x\):

\[
canonical(Python(x))
=
canonical(Candidate(x)).
\]

Compare:

- canonical bytes;
- digests;
- authorization decisions;
- error codes;
- reconstructed state;
- capability attenuation;
- lifecycle behavior.

## 38.2 Differential Replay

```python
for vector in corpus:
    py = python_impl.run(vector)
    rs = rust_impl.run(vector)

    assert canonical(py.output) == canonical(rs.output)
    assert py.digest == rs.digest
    assert py.error_code == rs.error_code
```

Include malformed and crash-boundary vectors, not only happy paths.

---

# 39. Candidate Polyglot Migration Order as Research

Low-semantic-risk candidates:

1. telemetry collector;
2. model/network gateway;
3. sandbox worker;
4. plugin sidecar;
5. evaluator;
6. scheduler/registry broker.

High-semantic-risk:

- kernel;
- canonical reducer;
- identity/canonicalization.

The latter should retain a reference implementation even if another language is introduced.

---

# 40. Durable Memory: Authorization Before Ranking

The source corpus contains a strong security ordering:

```text
authorize scope
→ fetch candidates
→ remove expired/revoked/forbidden
→ rank
→ attach provenance
```

Never:

```text
global search
→ rank
→ filter unauthorized results
```

because the ranking process itself can leak information about protected records.

## 40.1 Pseudocode

```python
authorized_scope = authorize_before_ranking(
    principal=principal,
    request=request,
    policy=memory_policy,
)

if not authorized_scope:
    return Denied()

candidates = memory.fetch(authorized_scope)

visible = [
    item
    for item in candidates
    if not item.expired
    and not item.revoked
    and retention_allows(item)
]

ranked = rank(visible, request.query)

return attach_provenance(
    ranked,
    policy_digest=memory_policy.digest,
    authorization_receipt=authorized_scope.receipt,
)
```

---

# 41. Durable Memory Lifecycle

Memory is not merely “vector DB persistence”.

A production-grade lifecycle can include:

```text
CREATE
→ ACTIVE
→ EXPIRED | REVOKED
→ QUARANTINED?
→ GC_ELIGIBLE
→ DELETED
```

Additional constraints:

- legal hold;
- tenant isolation;
- backup/restore;
- corruption quarantine;
- index rebuild;
- provenance retention.

---

# 42. Memory Store vs Index

A useful separation:

```text
canonical memory object store
        ↓
rebuildable indexes
        ↓
retrieval ranking
```

Index corruption should not corrupt canonical memory.

Rebuild property:

\[
Index =
Build(CanonicalMemory).
\]

A cold rebuild should be deterministic for a fixed implementation/version.

---

# 43. Corruption Quarantine

If object digest does not match:

```python
if sha256(bytes) != expected_digest:
    quarantine(object_id)
    emit(MemoryCorruptionDetected(object_id))
    exclude_from_retrieval(object_id)
```

Do not silently “repair” corrupted content unless a verified prior copy exists.

---

# 44. Backup and Restore Semantics

A useful restore invariant:

\[
Digest(State_{restored})
=
Digest(State_{source})
\]

for canonical objects and policy metadata.

Indexes may differ physically and then be rebuilt.

A restore process should verify:

- object digests;
- schema versions;
- encryption metadata;
- tombstones;
- revocation records;
- legal holds.

---

# 45. Cache Safety Must Be Effect-Aware

The companion report already documents generic caching.

This section goes deeper: **not every operation is cacheable**.

Define effect class:

```text
PURE_OBSERVATION
IDENTITY_BOUND_QUERY
DETERMINISTIC_COMPUTE
PRIVILEGED_EFFECT
EXTERNAL_MUTATION
NONDETERMINISTIC_CALL
```

## 45.1 Cacheability Predicate

Derived extension:

\[
Cacheable(o)
=
Deterministic(o)
\land
NoExternalMutation(o)
\land
IdentityComplete(o)
\land
PolicyAllows(o).
\]

Examples:

| Operation | Cacheable? |
|---|---|
| parse AST | yes |
| tokenize prompt | yes |
| read immutable blob by digest | yes |
| deterministic evaluator on exact subject | yes |
| `git status` | short-lived only |
| filesystem write | no |
| process with side effects | no |
| payment API | no |
| random model generation | usually no |
| temperature-0 provider response | only with strict identity/policy |

---

# 46. Cache Provenance Record

A cache hit should be an observable event:

```python
CacheHit(
    key=...,
    source_artifact=...,
    source_created_at=...,
    policy=...,
    validator=...,
    age_ms=...,
)
```

This allows later questions such as:

> Did the agent solve the task, or reuse a stale result?

---

# 47. Stale-Denial Instead of Silent Recompute

For some high-assurance caches, stale content should fail closed instead of silently recomputing.

Example:

```python
if entry.expired and request.requires_exact_reproducibility:
    return CacheStaleDenied(entry.key)
```

This can be useful when evaluation requires all runs to use the same preregistered artifacts.

---

# 48. Typed Failure Taxonomy

Blind retry is one of the most expensive anti-patterns in agentic systems.

A useful taxonomy:

```text
MODEL_TRANSIENT
MODEL_RATE_LIMIT
MODEL_INVALID_RESPONSE

TOOL_TRANSIENT
TOOL_DETERMINISTIC_FAILURE
TOOL_PERMISSION_DENIED

LOCALIZATION_ERROR
PATCH_APPLY_ERROR
TEST_FAILURE
TEST_INFRA_ERROR

CONTEXT_MISSING
CONTEXT_STALE
BUDGET_EXHAUSTED

EVALUATOR_FAIL
EVALUATOR_UNAVAILABLE

CONTAINMENT_FAIL
RECOVERY_UNKNOWN
ARTIFACT_CORRUPTION
```

Retryability depends on type.

---

# 49. Typed Retry

```python
attempt = run_once()

if attempt.passed:
    return settle(attempt)

failure = classify(attempt)

if (
    failure.kind in RETRYABLE_TYPED_FAILURES
    and retry_budget_available(failure)
):
    preserve(attempt.artifacts)

    context = build_targeted_retry_context(
        failure=failure,
        prior_attempt=attempt,
    )

    return retry(context)

return settle_without_retry(attempt)
```

The critical idea:

> Retry with **new information**, not merely another sample.

---

# 50. Expected Value of Retry

Derived research extension.

Let:

- \(p_r\): probability retry succeeds;
- \(V\): value of successful completion;
- \(C_r\): expected retry cost;
- \(C_d\): delay/latency cost;
- \(R\): risk penalty.

Retry is rational when:

\[
p_rV
>
C_r+C_d+R.
\]

A failure classifier improves the estimate of \(p_r\).

For deterministic failures, \(p_r\) without changed context/tooling can be near zero.

---

# 51. Retry Context Should Be Failure-Specific

Examples:

## Test Failure

Include:

- failing test;
- assertion diff;
- relevant patch;
- touched symbols.

Do not resend entire repository transcript.

## Permission Denied

Include:

- denied capability;
- selector;
- requested effect.

Do not ask a stronger model to “try harder”.

## Missing Context

Retrieve missing dependency or symbol.

## Rate Limit

Retry later or change provider route.

This makes retry a controlled state transition rather than stochastic repetition.

---

# 52. Spectrum-Based Fault Localization (SBFL)

**Derived research extension inspired by the LEX/LIM and SBFL references in the source corpus.**

When tests provide coverage data, suspiciousness can rank code locations.

## 52.1 Ochiai

For program element \(e\):

- \(n_{ef}\): failing tests executing \(e\);
- \(n_{ep}\): passing tests executing \(e\);
- \(n_f\): total failing tests.

\[
Ochiai(e)
=
\frac{n_{ef}}
{\sqrt{
n_f(n_{ef}+n_{ep})
}}.
\]

High score indicates stronger correlation with failures.

## 52.2 Tarantula

\[
Tarantula(e)
=
\frac{
n_{ef}/n_f
}{
n_{ef}/n_f+n_{ep}/n_p
}.
\]

These are correlation scores, not causal proof.

---

# 53. Multi-Signal Fault Localization

Pure SBFL can be combined with static and semantic evidence.

Define normalized signals:

- \(S_{sbfl}\): coverage suspiciousness;
- \(S_{stack}\): stack-trace proximity;
- \(S_{diff}\): recent-change proximity;
- \(S_{dep}\): dependency centrality;
- \(S_{llm}\): model-generated semantic relevance.

Combined score:

\[
S(e)
=
w_1S_{sbfl}
+w_2S_{stack}
+w_3S_{diff}
+w_4S_{dep}
+w_5S_{llm}.
\]

The important research design is not the exact weights but measuring whether adding each signal improves:

- top-k localization accuracy;
- patch success;
- tokens consumed;
- files inspected.

---

# 54. Fault Localization Workflow

```text
failing tests
   ↓
coverage matrix
   ↓
SBFL ranking
   ↓
stack trace fusion
   ↓
dependency neighborhood
   ↓
recent diff proximity
   ↓
top-k files/symbols
   ↓
LLM inspection
   ↓
candidate patch
```

This can dramatically reduce context expansion before the LLM sees the repository.

---

# 55. Test Selection as an Impact Graph

After a patch changes symbols \(M\), select tests by dependency distance.

Let graph \(G=(V,E)\) contain:

- code symbols;
- files;
- tests.

Distance:

\[
d(t,M)
=
\min_{m\in M}
shortestPath(t,m).
\]

A simple priority:

\[
Priority(t)
=
\alpha\frac{1}{1+d(t,M)}
+\beta Ownership(t,M)
+\gamma FailureHistory(t).
\]

Run high-priority tests first, then expand.

This is useful for agent loops because fast feedback can prevent expensive broad regressions early.

---

# 56. Progressive Verification

```text
syntax / parse
   ↓
targeted unit test
   ↓
related test shard
   ↓
type/lint/static checks
   ↓
full relevant suite
   ↓
exterior evaluator
```

The harness should not run a full multi-minute suite after every one-line edit if a cheap deterministic check can reject the patch first.

---

# 57. Artifact-Preserving Repair Loop

```text
Attempt 1
  ↓
patch_1
test_receipt_1
failure_1
  ↓ preserve immutable refs
Retry
  ↓
patch_2
test_receipt_2
...
```

Never overwrite negative attempts.

This allows post-hoc comparison:

- which failure types were recoverable;
- how much cost each repair consumed;
- whether retry improved or regressed.

---

# 58. Dynamic Model Escalation by Failure Class

The source corpus discusses using cheap models for routine work and stronger models for difficult architectural cases.

A more precise controller:

```python
def choose_model(task, failure=None):
    if failure is None:
        return cheap_model(task)

    if failure.kind in {
        "MODEL_INVALID_RESPONSE",
        "CONTEXT_MISSING",
    }:
        return same_or_mid_model()

    if failure.kind in {
        "ARCHITECTURAL_CONTRADICTION",
        "SECURITY_INVARIANT",
        "MULTI_MODULE_CAUSAL_ERROR",
    }:
        return frontier_model()

    return current_model
```

Escalation should be triggered by typed evidence, not vague “difficulty”.

---

# 59. Escalation Should Preserve the Falsifier

Rather than forwarding the entire previous transcript:

```text
workspace state
+ patch delta
+ exact failure
+ relevant evidence
+ unresolved assumptions
```

This is a stronger implementation form of “artifact-preserving context compaction”.

---

# 60. Dual-Harness Engineering Pattern

The source corpus contains a useful meta-pattern:

```text
Fault / invariant analyzer
        ↓
ranked problem localization
        ↓
fast surgical coding agent
        ↓
sandboxed verification
        ↓
invariant / telemetry judge
        ↓
evidence receipt
```

The original reports refer to a LEX/LIM pairing.

Abstracted generically:

## Analyzer Harness

Responsibilities:

- SBFL;
- invariant detection;
- telemetry;
- suspicious region ranking;
- regression analysis.

## Coder Harness

Responsibilities:

- minimal patch;
- code modification;
- targeted verification;
- retry.

## Judge Harness

Responsibilities:

- architecture/security checks;
- benchmark metrics;
- independent evidence.

The important insight:

> The solver and diagnostic harnesses can specialize independently while sharing the same execution substrate.

---

# 61. Codebase Explanation as a Distinct Agent Benchmark

A code explainer is a useful probe because it tests structural understanding without mutation.

Benchmark dimensions:

- path accuracy;
- symbol accuracy;
- call-graph accuracy;
- dependency-direction accuracy;
- security-boundary accuracy;
- persistence/recovery explanation;
- impact analysis;
- test selection;
- extension-point identification;
- contradiction detection.

## 61.1 Unsupported-Claim Rate

Let:

- \(N_c\): total factual claims;
- \(N_u\): claims lacking resolvable evidence.

\[
UCR =
\frac{N_u}{N_c}.
\]

Lower is better.

## 61.2 Evidence Coverage

\[
EC =
\frac{N_{supported\ claims}}
{N_{claims}}.
\]

This benchmark measures whether the harness can reconstruct a codebase model, not merely generate plausible prose.

---

# 62. Contradiction Detection as a Research Task

A high-value codebase-analysis task is:

```text
documentation claim
      ↓
resolve code path
      ↓
resolve tests
      ↓
compare
      ↓
SUPPORTED | STALE | CONTRADICTED | UNVERIFIABLE
```

Examples:

- docs say feature is canonical, runtime still uses legacy path;
- docs say test count X, current collection differs;
- docs say milestone complete, evidence fails;
- docstring says one ownership model, imports contradict it.

This is a practical agentic research task because it requires mixed symbolic and semantic reasoning.

---

# 63. Deterministic Multi-Role Readiness

A strong topology execution algorithm from the source corpus:

```python
while not topology_settled:
    state = cold_fold(project_ledger)

    ready = canonical_sort(
        role
        for role in topology.roles
        if predecessors_settled(role, state)
        and required_artifacts_authorized(role, state, cas)
        and not role_settled(role, state)
    )

    if not ready:
        return typed_blocked_or_failed_state(state)

    role = ready[0]

    request = build_child_request(role, state)

    append_spawn_intent(request)
    result = spawn(request)
    append_role_settlement(result)
```

Key properties:

- readiness derived from durable state;
- deterministic ordering;
- no in-memory hidden scheduler truth;
- settled roles are never repeated.

---

# 64. Exactly-Once Logical Child Execution

Use deterministic child identity:

\[
ChildID =
H(
TopologyDigest
\parallel RoleID
\parallel AttemptIdentity
).
\]

Before spawn:

```python
if state.child_settled(child_id):
    return prior_result(child_id)

if state.child_open(child_id):
    return reconcile_child(child_id)

spawn_new(child_id)
```

This makes crash recovery compatible with multi-role workflows.

---

# 65. Artifact-Authorized Edges

A topology edge should not merely say:

```text
planner → executor
```

It should specify what the executor may consume.

Example:

```yaml
bindings:
  - from: planner
    to: executor
    artifact_roles:
      - implementation_plan
```

The executor receives digest refs, not ambient access to all planner history.

This reduces accidental context coupling.

---

# 66. Fork / Read / Merge

A useful topology:

```text
           ┌→ reader A ─┐
root → fork├→ reader B ─┼→ merge
           └→ reader C ─┘
```

Each reader operates on a controlled snapshot.

Merge consumes declared artifacts.

Potential uses:

- parallel code inspection;
- candidate solution generation;
- research source scouting;
- independent critique.

---

# 67. Copy-on-Write Workspace Forking

The source corpus treats CoW snapshots as an optional research idea.

For \(N\) branches, naïve full workspace copies cost:

\[
Storage \approx N \cdot |Workspace|.
\]

Copy-on-write can approach:

\[
Storage
\approx
|Workspace|
+
\sum_i |\Delta_i|.
\]

Candidate implementations:

- Git worktrees;
- overlayfs;
- reflinks;
- filesystem snapshots;
- content-addressed virtual workspaces.

Research metrics:

- fork latency;
- changed-byte storage;
- merge conflict rate;
- isolation;
- cleanup cost.

---

# 68. Merge as a Typed Operation

Instead of arbitrary “agent merges branches”:

```python
MergeRequest(
    base_digest=...,
    branch_artifacts=(...),
    conflict_policy=...,
)
```

Output:

```python
MergeReceipt(
    result_digest=...,
    conflicts=(...),
    applied=(...),
)
```

This makes fan-in reproducible.

---

# 69. Process-Local vs Durable Scheduler State

A scheduler may maintain caches, but the authoritative readiness state should be derivable.

Unsafe:

```python
self.completed_roles.add(role)
```

with no durable fact.

Safe:

```text
RoleSettled(role_id, result_digest)
```

then:

```python
completed = projection.role_settled
```

This makes scheduler restart cheap.

---

# 70. Scheduling Is Not Authorization

This separation deserves explicit preservation:

```text
scheduler:
  chooses which ready operation to run

kernel:
  decides whether the operation is permitted
```

Even a compromised scheduler should not be able to widen authority.

---

# 71. Control Topology vs Effect Protocol

The source corpus refines the “universal loop” thesis.

A useful distinction:

## Universal Effect Protocol

```text
observe
propose
authorize
effect
receipt
record
```

## Plural Control Topologies

```text
single agent
critic/reviser
planner/executor
tree
debate
research fan-out
evolutionary population
```

This prevents a false choice between:

- one monolithic loop for everything;
- completely different runtimes for every algorithm.

---

# 72. Workflow DSL Sufficiency Test

Before designing a general workflow language:

Implement several real compositions.

Record friction points.

Only add a primitive if at least two independent compositions need it.

Pseudocode:

```python
gaps = Counter()

for workflow in reference_workflows:
    implementation = express_with_current_primitives(workflow)

    for workaround in implementation.custom_workarounds:
        gaps[workaround.missing_primitive] += 1

new_primitives = [
    p for p, count in gaps.items()
    if count >= 2
]
```

This is a pragmatic defense against premature workflow-engine complexity.

---

# 73. Mutation Testing as an Optional Evaluator

Mutation testing should not run on every ordinary task.

It can be used when the claim is:

> the patch meaningfully improves test sensitivity or correctness.

Workflow:

```text
candidate patch
   ↓
normal tests
   ↓
mutation operator
   ↓
mutant set
   ↓
run selected tests
   ↓
mutation score
```

\[
MutationScore =
\frac{KilledMutants}
{NonEquivalentMutants}.
\]

Use as a specialized evaluator, not default runtime machinery.

---

# 74. CEGIS as a Pack-Level Algorithm

Counterexample-Guided Inductive Synthesis:

```text
candidate
  ↓
verifier
  ├─ pass → done
  └─ counterexample
         ↓
      refine candidate
         ↓
      verifier
```

This maps naturally onto:

- formal proof;
- synthesis;
- constraint solving;
- invariant generation.

It should be treated as a domain/topology policy, not trusted core semantics.

---

# 75. MCTS as a Budgeted Topology Experiment

Monte Carlo Tree Search can be expressed with:

- node state;
- candidate actions;
- rollout evaluator;
- budget;
- backpropagated value.

Classic UCB1 selection:

\[
UCB_i =
\bar X_i
+
c
\sqrt{
\frac{\ln N}{n_i}
}.
\]

In agentic systems, the expensive variable is not simulation count alone but model/tool/evaluator cost.

A more practical version:

\[
Score_i =
\bar X_i
+
c\sqrt{\frac{\ln N}{n_i}}
-
\lambda Cost_i.
\]

This remains an optional policy experiment unless it beats simpler strategies.

---

# 76. Taint-Aware Agent Dataflow

The reports mention confidentiality/trainability metadata and possible future taint policies.

A useful dataflow label:

```python
Label = {
    confidentiality,
    tenant,
    exportability,
    trainability,
    retention_class,
}
```

Propagation:

\[
Label(output)
=
join(
Label(input_1),
...,
Label(input_n),
Policy(transform)
).
\]

A sink accepts data only if:

\[
Label(data) \preceq SinkPolicy.
\]

This can prevent:

- secrets entering model prompts;
- private output entering training corpora;
- restricted artifacts being exported;
- cross-tenant memory contamination.

---

# 77. Taint-Aware Context Compilation

```python
def build_context(candidates, target_model, policy):
    safe = []

    for item in candidates:
        if policy.may_send(item.labels, target_model):
            safe.append(item)
        else:
            emit(ContextItemDenied(item.ref, reason="taint_policy"))

    return compile_context(safe)
```

This turns privacy from a post-hoc redaction problem into a selection constraint.

---

# 78. Service Health vs Readiness

Agentic runtimes benefit from distinguishing:

## Health

> Is the process alive?

## Readiness

> Can this process execute the requested class of work?

Readiness can depend on:

- model provider reachable;
- required sandbox available;
- migrations current;
- event store writable;
- plugin set valid;
- evaluator available if required.

This prevents routing work to a process that is alive but incapable.

---

# 79. Typed Diagnostics

Avoid:

```text
Runtime failed.
```

Prefer:

```python
Diagnostic(
    code="EVALUATOR_UNAVAILABLE",
    layer="runtime",
    retryable=True,
    subject="run-...",
    details={
        "endpoint": "...",
        "required_by_profile": True,
    },
)
```

Typed diagnostics improve:

- automated retry;
- UI;
- telemetry;
- statistical failure analysis.

---

# 80. Event Store Optimization Beyond Batching

Derived extensions motivated by measured append degradation.

Potential optimizations:

## 80.1 Sequence Allocation Once per Batch

Instead of querying latest sequence for every event:

```python
start = reserve_sequence_range(project_id, len(batch))

for i, event in enumerate(batch):
    event.seq = start + i
```

## 80.2 Prepared Statements

Avoid repeated SQL parse/prepare overhead.

## 80.3 Bulk Insert

```sql
INSERT INTO events (...) VALUES (...), (...), (...);
```

or efficient `executemany`.

## 80.4 Incremental Chain Digest

Maintain the prior chain digest in the writer instead of querying it repeatedly.

Persist writer state carefully and verify against database on restart.

## 80.5 WAL Checkpoint Policy

Separate application checkpoints from SQLite WAL checkpoints.

Measure:

- WAL growth;
- checkpoint stalls;
- fsync tail latency.

---

# 81. Storage Efficiency Should Be Reported per Semantic Operation

Events per second can hide event amplification.

A better metric:

\[
BytesPerSemanticEffect
=
\frac{TotalLedgerBytes}
{NumberOfSemanticEffects}.
\]

Also:

\[
FsyncPerSemanticEffect
=
\frac{FsyncCount}
{SemanticEffects}.
\]

These directly reveal lifecycle ceremony and poor batching.

---

# 82. Useful Runtime Performance Decomposition

For one agent turn:

\[
T_{turn}
=
T_{context}
+
T_{model}
+
T_{authorize}
+
T_{effect}
+
T_{persist}
+
T_{evaluate}
+
T_{overhead}.
\]

For local fake-model benchmarking:

\[
T_{model}\approx 0
\]

which exposes substrate overhead.

For real workloads:

\[
T_{model}
\]

may dominate, so optimizations should be evaluated by both absolute milliseconds and percentage of real end-to-end cost.

---

# 83. Critical Path vs Aggregate Work

For multi-agent execution:

\[
T_{wall}
\neq
\sum_i T_i.
\]

Instead:

\[
T_{wall}
\approx
CriticalPath(G)
+
CoordinationOverhead
+
Contention.
\]

Therefore telemetry should record:

- aggregate worker time;
- wall time;
- scheduler wait;
- model queue time;
- tool time;
- evaluator time;
- serialization time;
- persistence time.

---

# 84. Distinguish Model Queue, TTFT, and Generation

Provider latency should be decomposed:

\[
T_{model}
=
T_{queue}
+
T_{TTFT}
+
T_{generation}
+
T_{retry}.
\]

Otherwise a routing policy may incorrectly attribute provider congestion to model reasoning cost.

---

# 85. Artifact Capture Cost as a Separate Budget

The source measurements suggest artifact capture can be modest relative to durable event writes.

This motivates tracking:

\[
C_{capture}
=
C_{serialize}
+
C_{redact}
+
C_{hash}
+
C_{persist}.
\]

Then decisions about turning capture off can be evidence-based rather than intuitive.

---

# 86. In-Memory Fallbacks Are Semantically Significant

An in-memory event store is not merely a faster backend.

It changes:

- crash semantics;
- resume capability;
- durability;
- auditability.

Therefore persistence mode belongs in execution identity.

```text
sqlite-wal
memory
remote-log
```

must not be silently interchangeable.

---

# 87. Environment Ports as a Generality Boundary

A task domain can often be generalized by making environment semantics explicit.

A useful environment interface:

```python
class EnvironmentPort:
    def profile(self) -> EnvironmentProfile: ...
    def snapshot(self) -> SnapshotRef: ...
    def observe(self, request) -> Observation: ...
    def preview(self, operation) -> Preview: ...
    def apply(self, operation) -> Receipt: ...
    def reconcile(self, intent) -> Receipt | Unknown: ...
    def compensate(self, receipt) -> Receipt | Unsupported: ...
    def dispose(self) -> None: ...
```

A domain is “portable” only when its environment implements the full lifecycle, not merely its domain verbs.

---

# 88. Preview Before Mutation

A generic pattern:

```text
operation proposal
   ↓
preview
   ↓
authorization against resolved target
   ↓
apply
```

This can reduce TOCTOU problems where the abstract selector differs from the concrete resource.

Example:

```python
preview = env.preview(operation)

decision = authorize(
    requested=operation,
    resolved_resources=preview.resources,
)

if decision.allowed:
    receipt = env.apply(operation)
```

---

# 89. Point-of-Effect Verification

Where possible, re-check security-sensitive resource identity immediately before effect execution.

If a file path, symlink, or remote object changed after planning:

```python
if current_descriptor != authorized_descriptor:
    deny("resource_changed_after_authorization")
```

This is particularly useful for agent systems because the delay between proposal and execution can be nontrivial.

---

# 90. Reference Agent as a Systems Probe

A “reference workflow” is more than a demo.

Different workflows stress different substrate surfaces.

## Code Editor

Stresses:

- mutable workspace;
- process execution;
- tests;
- patch capture.

## Code Explainer

Stresses:

- read-only permissions;
- indexing;
- evidence citation;
- abstention.

## Formal Solver

Stresses:

- deterministic verifier;
- exact witnesses;
- non-coding domain.

## Research Agent

Stresses:

- network acquisition;
- document normalization;
- long-lived provenance;
- citation.

The substrate should be evaluated by how many semantics remain unchanged across these probes.

---

# 91. Research Hypotheses Emerging From These Reports

## R1 — Event-sourced runtime overhead is dominated by durability granularity, not event encoding.

Test with controlled batch size and constant event corpus.

## R2 — Lifecycle event summarization can reduce storage by >3× while preserving audit equivalence through digests.

Compare full vs summary lifecycle.

## R3 — Cold fold can remain cheaper than checkpoint complexity for surprisingly long histories.

Measure break-even over realistic state shapes.

## R4 — Process-based parallelism will outperform thread-based parallelism for multi-agent Python workloads once verification subprocess cost dominates.

Compare threads/processes/async.

## R5 — Selector-derived conflict graphs can unlock useful parallelism without introducing a general concurrent scheduler.

Measure conflict rate and speedup.

## R6 — Typed failure classification reduces wasted retries and token usage relative to blind retry.

Run matched task sets.

## R7 — SBFL + static dependency signals can reduce repository context size while maintaining or improving bug-fix success.

Measure top-k localization and pass rate.

## R8 — Authorization-before-ranking prevents information leakage in multi-tenant memory systems without materially hurting retrieval quality.

Measure retrieval quality and side-channel exposure.

## R9 — A portable interface descriptor plus golden vectors is sufficient to replace selected runtime components across languages without semantic drift.

Implement one sidecar in another language.

## R10 — Orthogonal execution axes produce better experimental identifiability than monolithic presets.

Compare configuration experiments under both models.

---

# 92. Suggested Micro-Experiments

These are experiments, not development phases.

## E1 — Event Amplification

Run the same semantic operation under:

- full lifecycle;
- summary lifecycle;
- lifecycle off.

Measure:

- event count;
- bytes;
- replay equivalence;
- audit reconstruction.

## E2 — Commit Granularity

Compare:

- per event;
- pre-effect + terminal;
- per turn;
- adaptive batch.

Measure:

- p50/p95;
- fsync count;
- crash-loss window;
- recovery correctness.

## E3 — Sequence Allocation

Compare:

- single writer;
- transactional global sequence;
- per-lineage sequence.

Measure contention and causal usability.

## E4 — Checkpoint Break-Even

Vary:

- events;
- state size;
- checkpoint frequency.

Fit:

\[
T_{recovery}(N,S,K).
\]

## E5 — Fault Localization

Compare:

- grep/manual search;
- stack trace only;
- SBFL;
- SBFL + dependency graph;
- SBFL + graph + LLM.

## E6 — Typed Retry

Compare blind retry vs failure-class retry.

Measure:

- success;
- tokens;
- attempts;
- latency.

## E7 — Transport Equivalence

Run identical command through:

- in-process;
- stdio;
- HTTP.

Compare normalized causal event sequence.

## E8 — Polyglot Sidecar

Implement one pure component twice and run differential vectors.

## E9 — Memory Authorization

Compare authorization-before-ranking vs rank-before-filter using adversarial cross-tenant queries.

## E10 — Concurrent Workspaces

Compare:

- full copy;
- Git worktree;
- reflink;
- overlayfs.

---

# 93. Compact Pseudocode Library

## 93.1 Safe Effect Execution

```python
def safe_effect(req):
    decision = authorize(req)
    if not decision.allowed:
        return denied(decision)

    reservation = reserve(decision)
    intent = persist_intent(decision, reservation)

    try:
        receipt = execute(intent)
    except UnknownExternalState:
        return mark_unknown(intent)

    persist_receipt(receipt)
    settle(reservation, receipt)
    return receipt
```

## 93.2 Safe Retry

```python
def retry_or_settle(attempt):
    failure = classify(attempt)

    if failure.state == "unknown":
        return reconcile(attempt)

    if not failure.retryable:
        return settle(attempt)

    if not retry_budget_available(failure):
        return settle(attempt)

    return retry(
        context=targeted_context(failure),
        preserved_artifacts=attempt.artifacts,
    )
```

## 93.3 Authorized Memory Query

```python
def query_memory(principal, q):
    scope = authorize_memory(principal, q)
    if not scope:
        return []

    candidates = store.fetch(scope)
    candidates = apply_lifecycle_filters(candidates)
    return rank(candidates, q)
```

## 93.4 Deterministic Topology Execution

```python
def execute_graph(graph, ledger):
    while True:
        state = fold(ledger)

        if graph.terminal(state):
            return graph.result(state)

        ready = sorted(
            graph.ready(state),
            key=lambda node: node.stable_id,
        )

        if not ready:
            return Blocked(graph.explain_block(state))

        node = ready[0]
        child_id = deterministic_child_id(graph, node, state)

        if state.settled(child_id):
            continue

        if state.open(child_id):
            reconcile_child(child_id)
            continue

        persist_spawn_intent(child_id, node)
        result = spawn_child(child_id, node)
        persist_settlement(child_id, result)
```

## 93.5 Observer / Controller Pipeline

```python
def run_operation(op):
    for observer in observers:
        observer.before_operation(op)

    decisions = [
        controller.before_operation(op)
        for controller in controllers
    ]

    control = resolve_control(decisions)

    if control == "REJECT":
        return rejected()

    if control == "REDIRECT":
        op = redirect(op)

    result = execute(op)

    for observer in observers:
        observer.after_operation(op, result)

    return result
```

---

# 94. Equation Index

## Event amplification

\[
A_E =
\frac{N_{events}}
{N_{semantic\ operations}}
\]

## Byte amplification

\[
A_B =
\frac{LedgerBytes}
{SemanticPayloadBytes}
\]

## Durable write cost

\[
T_{write}
\approx
N_e(t_{encode}+t_{hash}+t_{sql})
+B t_{fsync}
\]

## Commit objective

\[
J(B)
=
B t_{fsync}
+
P_c(B)W(B)
\]

## Conflict graph

\[
C_{ij}
=
1
\iff
overlap(i,j)
\land
(write_i\lor write_j)
\]

## Parallel value

\[
V_n =
\frac{S_n}
{1+\lambda_cC_n+\lambda_fF_n+\lambda_rR_n}
\]

## Checkpoint break-even

\[
T_{checkpoint}+T_{suffix}
<
T_{full-fold}
\]

## Retry value

\[
p_rV
>
C_r+C_d+R
\]

## Ochiai

\[
Ochiai(e)
=
\frac{n_{ef}}
{\sqrt{n_f(n_{ef}+n_{ep})}}
\]

## Test impact priority

\[
Priority(t)
=
\alpha\frac{1}{1+d(t,M)}
+\beta Ownership(t,M)
+\gamma FailureHistory(t)
\]

## Unsupported claim rate

\[
UCR =
\frac{UnsupportedClaims}
{TotalClaims}
\]

## CoW storage

\[
Storage_{CoW}
\approx
|Workspace|
+
\sum_i|\Delta_i|
\]

---

# 95. Practical Research Checklist

When evaluating a new runtime technique:

- [ ] Does it change causal semantics or only implementation?
- [ ] Does it change the durability boundary?
- [ ] Does it change event identity?
- [ ] Does it change authority?
- [ ] Does it create a second source of truth?
- [ ] Can state still be reconstructed after process death?
- [ ] Can an unknown external effect be reconciled?
- [ ] Are retries typed?
- [ ] Are negative attempts preserved?
- [ ] Is plugin cleanup total?
- [ ] Are local calls still zero-copy?
- [ ] Are remote transports semantically equivalent?
- [ ] Does a cache replay an observation or accidentally replay an effect?
- [ ] Is ranking performed only after authorization?
- [ ] Is checkpointing measurably useful?
- [ ] Is concurrency based on measured independence?
- [ ] Does batching reduce fsyncs without weakening required intent barriers?
- [ ] Is lifecycle detail semantic or ceremonial?
- [ ] Are large bytes stored outside the event envelope?
- [ ] Does every artifact reference point to durable content?
- [ ] Can a component be replaced across languages with golden-vector equivalence?

---

# 96. Final Synthesis

The most important additional insight across these reports is that **agentic systems engineering is fundamentally distributed-systems engineering at small scale**.

Even when an agent runs on one machine, the architecture contains familiar distributed-systems problems:

- independent components;
- partial failures;
- retries;
- durable intent;
- idempotency;
- event ordering;
- causal history;
- state reconstruction;
- stale caches;
- process crashes;
- external side effects;
- competing writers;
- versioned protocols;
- asynchronous persistence;
- authorization boundaries;
- scheduler decisions;
- eventually replaceable services.

The LLM adds a probabilistic decision process on top of those problems. It does not remove them.

A strong agent runtime therefore behaves less like a prompt script and more like a small durable operating system:

```text
Declarative composition
        ↓
identity-bearing activation
        ↓
bounded decision process
        ↓
authorized effects
        ↓
durable causal history
        ↓
recoverable projections
        ↓
typed artifacts
        ↓
observable results
```

The engineering objective is not maximum abstraction.

It is **minimum mechanism sufficient to preserve causal truth while allowing behavior to vary freely**.

That leads to several durable conclusions:

1. compile compositions before execution;
2. make activation explicit;
3. keep scheduling separate from authorization;
4. model external effects with durable intent and reconciliation;
5. distinguish failure from unknown settlement;
6. use idempotency for logical exactly-once semantics;
7. batch persistence at semantic boundaries instead of weakening durability;
8. measure lifecycle/event amplification before deleting observability;
9. keep checkpoints as derived caches;
10. let concurrency emerge from measured independence;
11. perform authorization before memory ranking;
12. separate capture from retention and telemetry;
13. treat observers and controllers as different trust classes;
14. define plugin boundaries independently of programming language;
15. demand semantic equivalence across transports;
16. use typed failure taxonomies to drive retry;
17. combine deterministic fault localization with model reasoning;
18. preserve failed attempts as scientific artifacts;
19. use specialized advanced algorithms—MCTS, CEGIS, mutation testing, CoW fan-out—only when their measured value exceeds simpler mechanisms;
20. keep the event/effect protocol universal while allowing control topology to remain plural.

The resulting research question is:

\[
\boxed{
\text{How can an agent runtime maximize useful adaptive behavior
while minimizing irreversible, unauditable, or unrecoverable state?}
}
\]

That question is complementary to the harness-level question documented in the previous report.

Together, the two documents form a broader research basis:

```text
research_harness_agentic_systems_engineering.md
    → what agentic systems should explore

research_agentic_runtime_systems_engineering.md
    → how the substrate can execute those explorations correctly and efficiently
```

---

# Appendix A — Source-Derived vs Derived Extensions

## Primarily source-derived

- canonical manifest → graph → frozen composition → activation plan → run plan;
- event grammar;
- group commit at turn boundaries;
- lifecycle event summarization;
- measured event amplification;
- sequence-allocation race;
- process-level vs thread-level concurrency findings;
- projection replay vs continuation distinction;
- durable memory authorization-before-ranking;
- observer/controller split;
- closed controller vocabulary;
- plugin contract families;
- transport equivalence;
- differential polyglot conformance;
- artifact capture ordering;
- orthogonal execution configuration;
- typed retry;
- codebase-explainer benchmark;
- CoW/MCTS/CEGIS/mutation testing as optional research ideas.

## Derived research extensions added in this report

- formal event-amplification equations;
- fsync/commit cost model;
- commit-granularity objective;
- concurrency conflict graph;
- parallel-value equation;
- adaptive checkpoint break-even policy;
- retry expected-value equation;
- classical SBFL Ochiai/Tarantula equations;
- multi-signal fault-localization equation;
- impact-graph test-selection equation;
- cacheability predicate;
- taint-label propagation model;
- semantic transport-equivalence formulation.

These extensions are analytical elaborations, not claims that the source code already implements them.

---

# Appendix B — Source Corpus

1. `GPT_SOL_MASTERPLAN_V0.9.0_beta.md`
   - typed retries, topology execution, durable memory, plugin lifecycle, benchmark/explainer concepts.

2. `VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_OPUS_PLAN.md`
   - measured event amplification, group commit, lifecycle ceremony, concurrency failure, capture economics, product/runtime simplification ideas.

3. `VANGUARD_BACKEND_M1_M9_MASTER_REPORT.md`
   - LEX/LIM collaboration concept, SBFL-oriented development, dynamic model escalation.

4. `VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md`
   - orthogonal operating configuration, interceptors, event/result contracts, transport equivalence, performance measurements, memory/capture separation.

5. `Higgs_update_concepts.md`
   - canonical composition-to-activation seam, effect-protocol vs topology distinction, polyglot interface design, replay semantics.

6. `masterplan_todo_rev1.md`
   - precise evidence-capture ordering, resource semantics, privacy-before-persistence, fail/degrade distinction, runtime/provider capture seam.

7. `research_harness_agentic_systems_engineering.md`
   - companion document used as an explicit exclusion baseline to avoid unnecessary duplication.

---

**End of report.**
