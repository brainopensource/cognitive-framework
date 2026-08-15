---
id: VG-03
file: 03_vanguard_architecture_planes_and_execution_model_v040.md
title: "Vanguard v4.0 — Architecture: Planes & Execution Model"
version: 4.0.0
status: NORMATIVE
authority_scope: >
  The execution model; the plane decomposition; intra-process layer topology;
  composition and operator invocation; the episode engine; environments and the
  adapter protocol; concurrency; abnormal termination; context engineering;
  playbooks; process topology and seams; the transparency surface; the failure taxonomy.
supersedes: none (v4 is the first version of this document)
superseded_by: none
budget_words: 6000
owners: [Tech Lead]
last_reviewed: 2026-08-14
---

# Vanguard v4.0 — Architecture: Planes & Execution Model

> **One sentence.** The runtime is one loop over typed environments, decomposed into planes with distinct identities, where everything the loop can vary is data and everything that enforces a guarantee is exterior to it.

---

## 0. What this document owns

The shape of the running system: what the planes are, what the loop does, how work is composed and parallelised, and how context is built. It owns the *structure*, not the *types* — every schema referenced here is defined by `04`, and every authorisation decision by `05`.

Claims, axioms and norms are owned by `02`. Where this document says "must", it is implementing a norm stated there.

---

## 1. The execution model in one page

Every capability in the system, in every environment, reduces to one protocol:

```
observe → propose → authorise → effect → receipt → evaluate
```

The abstraction that generalises is **not** a set of very powerful tools. It is this common protocol over different environments. A coding task, a spreadsheet reconciliation, and a browser workflow differ in their adapters and evaluators; they do not differ in this sequence.

| Step | Who | Constraint |
|---|---|---|
| observe | Environment adapter | Returns a snapshot-bound observation, never a live handle |
| propose | Cognitive operator | Produces a proposal; a proposal is not an authorisation |
| authorise | Broker (`05`) | Issues a scoped capability, or denies and records the attempt |
| effect | Environment adapter, inside the workload perimeter | Bounded by the perimeter, not by the caller's good intentions |
| receipt | Environment adapter | Verifiable, idempotency-keyed, reconcilable |
| evaluate | Evaluator, separate identity | Produces a scoped claim, never unscoped truth |

The loop knows how to reduce events, apply budgets, request authorisation and terminate. It does not know what "planning", "debugging", "abstraction" or "analogy" are. Those live in the operator registry, as data.

---

## 2. The inversion: agent loop over workflow DAG

### 2.1 Evidence

The prototype modelled a coding task as a statically declared graph of typed steps — *retrieve → architect → generate → apply → evaluate → repair* — validated by a 501-line validator enforcing socket compatibility, linear-chain structure, acyclicity, bounded iteration, fan-out declaration, join correctness and instrument-error routing.

| Symptom | Root cause |
|---|---|
| All agentic behaviour lived inside one method, inside one node, inside one step | The agent was a leaf of the workflow rather than its substrate |
| "Repair" was a bounded `for` loop over a fixed chain | The loop was declared by the topology, not controlled by the agent |
| Enabling a tool required three booleans in three layers, plus a test proving they were connected | Configuration distributed across layers with no single authority |
| Best-of-N was a sequential loop despite a concurrency budget dimension | Concurrency modelled in accounting, never in execution |
| A socket table shadowed the type system, and a test checked the shadow against the original | Static graph validation re-encoding what the types already carried |
| Retrieval read one entry file before the agent had any say, so the model patched code it never saw | Retrieval as preprocessing rather than as an agent decision |

None of these are incidents. They are what happens when a dynamic process is expressed in a static language.

### 2.2 The expressiveness claim

> **The episode loop is at least as expressive as the static topology language rejected above, at a small fraction of the machinery.**

The expressiveness half is proved below against static DAG topologies. The machinery half is an **estimate**, anchored on one measurement — the prototype's graph validator alone was 501 lines, and the loop that replaces it is smaller than that. Strict superiority holds under the static constraints enumerated in §2.1; dynamic graphs with runtime-generated nodes and recursive tasks may express equivalent behavior, but require significantly greater machinery. Treat it as an order-of-magnitude expectation, not an absolute proof over all possible workflow languages.

**Proof by construction.** Take any such topology:

| Graph node | Loop equivalent |
|---|---|
| `retrieve` | Not a node. The agent reads, globs and greps when it decides it needs to |
| `architect` | An operator with read-only capabilities and a planning brief, exposed to its parent as a tool |
| `generate` + `apply` | The parent holding edit capabilities. The environment's own diff remains the sole definition of the change |
| `evaluate` | **Not an operator.** A deterministic evaluator the agent may invoke and may never modify |
| `repair` | Does not exist. The agent observes failing output as a result and continues — *that is the loop* |
| fan-out + join | N branches in isolated snapshots under one task group, ranked by verdict |

Every static graph is expressible. The converse fails for static topologies: a static graph cannot express the agent deciding at runtime that it needs three more files before planning, that this task needs no architect, or that two branches should be spawned and compared. **Static topology is a strict subset.**

### 2.3 What the graph was for, and how each goal survives

The original motivations were sound; the mechanism was wrong.

| Goal | Preserved by |
|---|---|
| Procedural, reproducible problem-solving | Pinned configuration plus recorded replay. A replayed loop is exactly as deterministic as a replayed graph |
| Recording how the system thinks | The event stream, which records what actually happened rather than what was pre-declared |
| Composing context, memory, tools, external protocols | Composition at the operator level — a far smaller surface than a topology language plus validator |
| Visualisation | Render the trajectory as a graph *after* the run. Strictly more honest: the executed shape, not the intended one |
| Enforced methodology where warranted | Playbooks with a rigidity dial (§11). At `strict`, a playbook **is** a graph — recovered as a parameter, not as architecture |

**Refined position: graphs are an excellent authoring and visualisation surface and a poor runtime control-flow substrate.** The authoring canvas is deferred (`10`), and the runtime graph is rejected outright.

---

## 3. The six planes

The plane decomposition exists because the load-bearing property is not module separation but **distinct OS identities, mount namespaces and credential sets**. Two modules in one process share everything that matters to an attacker.

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

| Plane | Holds | Explicitly does not hold |
|---|---|---|
| **Interaction** | Clients as pure consumers; approvals carrying identity, scope, expiry and descriptor | Adapter handles; the ability to schedule work |
| **Cognition** | Episode state; operator selection and invocation; proposal construction | Environment credentials, signing keys, direct host access |
| **Control** | Principal authentication; capability and policy validation; budget reservation; secret references; kill switch and revocation | Any cognitive discretion. It answers requests; it does not originate them |
| **Workload** | Ephemeral execution with only the mounts and egress explicitly granted; real containment reporting | Mounts of the control plane, evaluator, secret store or updater |
| **Evidence** | Evaluators under a distinct identity; protocol, dataset split, image digest and provenance. **Owns the evaluation trigger**: it observes episode termination in the ledger and emits `EvaluationRequested`. No episode can request its own evaluation | Authority to admit anything into the live activation set |
| **Evolution** | Candidate artifacts without operational authority; build, attest, canary, roll back; activation-pointer updates | Write access to live files. It moves pointers, never contents |

Two structural consequences, both non-negotiable:

- **Cognition may fail without compromising the ledger or the evaluator.** A crashed or misbehaving cognition plane loses work, never evidence. **This holds fully from Phase 1.** In Phase 0, Cognition is co-located with Control *and the event store* (§12), so the property holds against a crash — the store is transactional and the writer is single — and **not** against a compromised cognition plane, which shares that process. The evaluator half holds in both phases, because the evaluator is separately identified from day one.
- **The Evolution plane applies stricter policy to control-plane and policy-kernel candidates than to prompts and operators.** The gradient of risk is explicit rather than uniform.

---

## 4. Layer topology within a process

Plane separation is the inter-process model. This is the intra-process discipline, enforced by static analysis rather than convention.

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
| LT-1 | `domain/` imports nothing from the project |
| LT-2 | `ports/` imports only `domain/` |
| LT-3 | `kernel/` imports `domain/` and `ports/`. Never `adapters/`, never `agency/` |
| LT-4 | `agency/` imports `domain/`, `ports/` and kernel interfaces. Never `adapters/`, never `lab/` |
| LT-5 | `adapters/` imports `domain/` and `ports/`. Never each other |
| LT-6 | `runtime/` may import everything. It is the only module that may |
| LT-7 | `clients/` imports `domain/` and the daemon client. No adapter handles |
| LT-8 | Nothing imports `lab/`. It is offline and consumes exported files |

`LT-4`'s prohibition on cognition reaching the laboratory is the structural expression of evaluator exteriority: **a component that can construct its own evaluator is a second judge.**

> **A standing caution.** These contracts prove properties of the import graph. They do **not** constrain a subprocess spawned under a granted execution capability. Containment is the workload perimeter's job (`05 §6`), and no static analysis substitutes for it.

---

## 5. Composition: operators as data

### 5.1 The four extension forms

Everything pluggable is one of exactly four things. A proposal to add a fifth is a design review, not a pull request.

| Form | Answers | Example |
|---|---|---|
| `ObservationSource` | What can be seen? | Repository conventions, retrieved priors, memory recall |
| `CognitiveOperator` | What produces a proposal? | Plan, localise, consolidate, critique |
| `EffectAdapter` | What can act? | File edit, shell, table update, external call |
| `Evaluator` | What produces evidence? | Test-suite runner, invariant checker, human adjudication |

### 5.2 Operators are data, not control flow

An operator is a versioned, addressable, content-hashed entry in the competence graph (`04 §10`) — a brief, a capability requirement, a budget shape, an output contract — not a function in the loop. This is what makes operator-level improvement reachable at all: a loop that hard-codes "planning" can never replace its planner. It also converts the runtime language question from strategic to tactical, because cognitive content lives in data rather than code.

Invocation is the single composition mechanism. An operator exposed to a parent appears in the parent's catalog as a tool; invoking it spawns a fresh-context child under attenuated capabilities.

| Concern | Rule |
|---|---|
| Return value | Text or a structured payload. **Never a handle, never shared mutable state** |
| Workspace | The parent's snapshot by default; an isolated snapshot when exploring in parallel |
| Failure | A typed failure result, not an exception propagated into the parent's loop |
| Budget | A child lease. Exhaustion returns a result, not a crash |
| Depth | A budget dimension, bounded like any other |
| Events | Child events carry the parent identifier and nest in the inspector |
| Provenance | The returned text is untrusted-derived at minimum — a child that read the environment consumed untrusted input |

Three properties follow, and the third is the most valuable: recursive composition with no new mechanism; attenuation at the broker rather than at the absence of a call site; and **context isolation** — a child's exploration never enters the parent's window, and only the result returns. Property three is the one no static graph can express, because a graph's nodes share a payload while operators own contexts.

### 5.3 Registries freeze at composition

All four registries resolve once, at the composition root, and then freeze. Unknown names fail at composition, not at first use. A runtime-discovered extension is an unaudited capability, and a name that fails at first use fails in production rather than in CI.

---

## 6. The episode engine

### 6.1 The loop

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
    // It is authorised like any other effect (05 §2.1) and executes through
    // EnvironmentAdapter.observe(req, grant) — there is no unauthorised read.
    const obs = await broker.authorize(observationRequest(episode));
    if (obs.kind === "grant") {
      episode = reduce(episode, await environment.observe(freshRequest(), obs.grant));
    }
  }
}
```

**Two reading notes, because the example is otherwise misleading.**

*Event emission.* The loop appends `ProposalProduced` explicitly because proposal production happens **outside** the dispatch sequence. Grants, denials, budget events, receipts and observations are appended by the kernel, so they do not appear here. Emission is **split**: intent is appended durably at S8a *before* the effect runs, and the outcome at S12 (`05 [K-47]`). Every reduction above is therefore preceded by a durable append, and — the stronger property — **every effect is preceded by one too**, which is what makes reconciliation of an interrupted effect possible at all.

*Evaluation.* No evaluator is invoked in this loop, and that is deliberate. The evaluator runs under a separate identity in the Evidence plane (§3) and is reachable by no capability the episode holds (`05 §7`, `06 §4.2`). An episode **terminates**; it does not grade itself. Evaluation is requested against the completed episode by the Evidence plane, which is why §6.2 keeps run termination and evaluation outcome on separate axes.

### 6.2 Terminal states

Run state and evaluation result are **separate axes**. Collapsing them is how instrument failure silently becomes task failure.

| Run termination | Evaluation outcome |
|---|---|
| `completed` · `abstained` · `escalated` · `cancelled` · `budget_exhausted` · `instrument_error` · `runtime_error` · `abandoned` | `satisfied` · `unsatisfied` · `partially_satisfied` · `inconclusive` · `invalid_evaluation` |

A provider rate-limit is `instrument_error`; it is never a task verdict, because the evaluator may not have run at all. Conversely, a *wrong but real* answer is `unsatisfied` — the instrument-error category must not be allowed to shrink the denominator.

### 6.3 Two distinct retries

Leaving every retry to the model wastes tokens and duplicates effects. Hiding infrastructural retries from the trajectory destroys attribution. Both are therefore explicit and separately recorded.

| Kind | Owner | Conditions |
|---|---|---|
| Transport retry | Adapter | Transient failure, idempotent operation, bounded count, recorded backoff |
| Cognitive retry | Operator | A new proposal after observing a result |

### 6.4 No-progress detection

Identical consecutive descriptors are insufficient evidence of a livelock: re-running tests or polling a queue can be exactly correct. Progress is judged over the tuple:

```
(state_digest, proposal_descriptor, receipt_digest, progress_signal)
```

Termination fires when the same transition reappears without a change in state or progress signal, for a configured limit. Deliberate polling declares an expected-no-change flag and a deadline, which exempts it.

### 6.5 Inner-loop invariants

Properties the loop holds regardless of configuration. Each maps to a defect observed in the prototype.

| Invariant | Prevents |
|---|---|
| Every turn is bounded on every budget dimension, and the bound is a lease rather than a constant | Unbounded runs and budget theatre |
| A denial names the offending call, not the one after it | Misattributed exhaustion |
| Results are labelled at construction, never at consumption | Provenance laundering |
| Capability-widening is a classifier output, never a constant | A hardcoded constant standing in for a defence |
| Leases release on every path, including creation failure | A permanently subtracted ceiling |
| Depth is a budget dimension | Runaway recursion |

**Why the last three are stated explicitly.** In the prototype, the injection defence was unreachable dead code — an accumulator was reset each round, so the predicate evaluated over a set that could not contain untrusted content by construction — while the widening classifier was hardcoded to a constant, making every command appear to trip the defence. The invariant was documented, tested, and did nothing. *An invariant whose test cannot fail against a broken implementation is a comment.*

---

## 7. Environments and generality

### 7.1 The adapter protocol

One port, implemented per environment. This is where domain specificity is allowed to live, and the only place.

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

### 7.2 Where a coding-shaped architecture breaks

Enumerated because each assumption is individually reasonable and collectively a trap.

| Coding assumption | How it breaks | Correction |
|---|---|---|
| Workspace is a version-control worktree | Browsers, operating systems and hosted services have remote state and irreversible effects | Adapter with snapshot, transaction/compensation and reconciliation |
| The patch is a diff | A sent email, a payment or a permission change has no reversible diff | Receipt, idempotency key, preview, commit, compensating action |
| Read-only implies commutative | Readings of a queue, a market or a UI change with time | Snapshot or version token, with explicit dependencies |
| Tests are truth | Human-facing tasks have incomplete or subjective criteria | Composite evidence, calibrated proxies, human gates |
| Files are resources | Resources can be accounts, cells, URLs, devices, people | A typed resource taxonomy |
| Shell is universal | In hosted services and browsers, shell represents neither affordances nor authorisation | Per-environment adapters and scoped capabilities |
| One operator at a console | Organisations require identity, consent and segregation | Principal, resource and context; tenant isolation; audit policy |
| Rollback is a workspace reset | External effects may be irrevocable | Compensations, approvals, risk tiers |
| Any trajectory can be training data | Content may be secret, personal or unlicensed | Data policy, redaction, retention, corpus opt-in |

### 7.3 The two Phase 0 environments

**Git environment.** Snapshot is base commit plus working-tree digest; preview is a patch including new files; apply happens inside an ephemeral worktree; reconcile is a status and read-back; compensate discards the worktree. Publishing externally is a separate, higher-risk effect.

**TableWorld**, mandatory in Phase 0. Versioned tables; `select`, `derive`, `update`, `validate`; constraints over sums, uniqueness, ranges and reconciliation; **no version control, no shell, and no paths as a domain concept**; a deterministic evaluator over invariants and expected relations.

> If adding TableWorld requires changing the episode engine, the capability algebra or the event envelope, generality has been falsified early — cheaply, and therefore usefully. That is the point of building it first rather than last.

### 7.4 The frozen atom set

Within an environment, capability grows by composition, not by more atoms. The coding environment's set — read, write, edit, glob, grep, shell — is frozen. A large catalog burns tool-schema tokens, degrades selection accuracy and multiplies the permission surface. The **universal** abstraction is the adapter, not any particular six tools.

| Rule | Rationale |
|---|---|
| No tool receives a filesystem handle, path object or open socket | Bytes reach the workspace only through the mediated path |
| Every tool declares its capability requirement and its read and write sets | Routing, attenuation, independence analysis and the ledger all key on them |
| The environment's own diff is *the* definition of what changed | No second patch path |
| A tool may never write into pinned evaluator paths | Enforced at the broker, never in tool code |
| The catalog freezes at composition | A runtime-discovered tool is an unaudited capability |

### 7.5 Irreversible effects

Browser actions, email, payments and administrative changes require: two-phase preview and commit where possible; an idempotency key; a declared risk tier; approval for externally consequential effects; a verifiable receipt; later reconciliation; a compensating action where one exists; **and plain text stating so when no rollback exists.** The last is a specification requirement, not a UX nicety.

---

## 8. Concurrency

### 8.1 Why this is not an optimisation detail

The prototype declared a structured-concurrency library as a dependency, described task groups in its documentation, and never imported it. Best-of-N was a sequential loop. A concurrency budget dimension meticulously accounted for work that never ran concurrently. Meanwhile the two highest-leverage optimisations in agent workloads are exactly parallel independent reads within a turn and parallel branch exploration.

### 8.2 Ordering rules

| # | Rule |
|---|---|
| CC-1 | Emitted order is preserved by default |
| CC-2 | Mutations are barriers |
| CC-3 | Parallelism requires an explicit independence group, or demonstrably disjoint read and write sets |
| CC-4 | Parallel reads observe the same snapshot |
| CC-5 | Every branch holds a child lease and a cancellation scope |
| CC-6 | Conflict raises an explicit conflict event — never silent last-write-wins |
| CC-7 | Mixed batches are never reordered |

`CC-7` deserves its own line because the tempting optimisation is wrong. Hoisting reads ahead of writes in a mixed batch changes the observed value, and the justification — *"reads cannot observe writes they were emitted alongside, since the model chose them from the same pre-write state"* — is a claim about model intent rather than execution semantics. Models routinely emit a read after a write deliberately, to confirm the edit. Equally, commutativity is a property of the **resource**, not the **verb**: reading a queue, a price, a UI or a clock is non-commutative with time.

At Phase 0, the model adapter may form independence groups only when the provider declares parallel calls and all of them are reads against the same snapshot.

### 8.3 Structured concurrency

| Requirement | Rationale |
|---|---|
| Task groups with automatic cancellation propagation | A failed branch must not orphan its siblings |
| Every branch holds a child lease of the parent | Budget correctness under fan-out |
| Cancellation is cooperative and reaches subprocesses | A cancelled command kills the process group rather than leaking it |
| Per-branch workspaces destroyed in a `finally` | Lifetime owned by the guarded block, including creation failure |
| Events carry a branch identifier | Otherwise concurrent branches interleave into an unreadable stream |

### 8.4 Parallel exploration

N branches run in isolated snapshots under one task group and one parent lease; each is evaluated; a ranker orders them; **only the activation policy admits a branch into use** (`06 §5`). Two distinct operations share the verb and must not be confused: the verifier admits *evidence* (`06 [V-02]`), and the activation policy admits *an artifact into the active set*. Neither may perform the other's admission. This replaces fan-out declarations, join nodes, validator rules and a ranker registry — and is actually concurrent.

---

## 9. Abnormal termination and recovery

A killed process emits nothing. Neither does a power loss or an out-of-memory kill. Any requirement that a dying process emit a terminal event is satisfiable only against a graceful-shutdown mock, and a test for it can never fail against the real failure mode.

The episode-level model is therefore:

| Element | Behaviour |
|---|---|
| Run lease | Every active episode holds a lease with an expiry |
| Heartbeat | The worker renews while alive |
| Recovery scanner | Detects expired leases independently of the dead process |
| Recovery controller | Emits the terminal record — recovered or aborted — **from outside** the failed process |
| Effect reconciliation | In-flight effects are reconciled by idempotency key through the adapter |
| Preserved uncertainty | Where an external effect's occurrence cannot be determined, the record says so |

That last row is a hard requirement, not a nuance. An implementation that resolves an undeterminable external effect to either success or failure has manufactured evidence, and `02 [C-11]` is falsified. Event types are owned by `04 §12`; the controller's identity and authority by `05`.

---

## 10. Context engineering

The actual quality bottleneck, and the largest cost lever in the system. The prototype invested least here — a compactor that kept the last four blocks.

### 10.1 The layer model

```
L1  SYSTEM     role + output contract          stable across the entire run
L2  TOOLS      tool schemas                    stable; rides on the request
L3  ENVIRONMENT conventions, retrieved priors  stable within a task
L4  TASK       the brief, the plan             stable within a task
L5  DIALOGUE   turns, results, notes           mutates every turn
```

Rendered in order, one message per non-empty layer, every block tagged with its producing source and its provenance label.

### 10.2 Cache boundaries

Providers cache on exact prefix match, so cache economics are entirely a function of prefix stability.

| Rule | Rationale |
|---|---|
| A small fixed ceiling on breakpoints | Provider limit |
| Breakpoints only at L1, L3 and L4 boundaries | These are the layers that do not mutate within a run |
| **L5 never carries a breakpoint** | It is the only layer permitted to mutate; marking it stable is a lie to the provider about what is stable |
| Exceeding the ceiling raises **at assembly** | Never discovered afterwards from cache-hit telemetry |
| Prefix stability is a monitored CI metric over a fixed replay | A metric without a replay to run over is an intention |

**The corollary that is easy to get wrong:** anything appended to L1–L4 mid-run destroys every downstream cache hit. Mid-run additions go to L5, always.

### 10.3 Compaction strategies

Pluggable and comparable — which is the point, since "which compaction strategy is better" is exactly the kind of one-variable question the system exists to answer.

| Strategy | Mechanism | Loss profile |
|---|---|---|
| `recency_window` | Keep the last N exchanges | Drops the load-bearing early decision |
| `result_eviction` | Keep that a file was read; drop the body once superseded | Low. Usually the correct first move |
| `model_summarize` | A child summarises the middle | Prose loses structure |
| `structured_consolidate` | A child emits a structured record (§10.4) | Lowest measured; the recommended default |
| `operator_isolation` | Never admit exploration to the parent context | **Bounded** at the return contract — raw exploration is retained in child trajectory, summary loss measurable |

**The cheapest way to keep a context window clean is never to put the exploration in it.** Isolation is the primary mechanism; compaction handles the remainder.

### 10.4 Structured consolidation

Prose summaries lose exactly what long horizons need, so the consolidator emits structure:

```ts
interface StructuredRecord {
  decisions:  { what, why, alternativesRejected, confidence }[];
  invariants: { claim, evidenceRef, verifiedAt }[];
  open:       { question, blockedOn }[];
  artifacts:  { path, role, lastVerifiedState }[];
  deadEnds:   { approach, whyAbandoned }[];
}
```

`deadEnds` earns its place: an agent re-exploring an approach it already abandoned is among the most common and most expensive long-horizon failures, and it is trivially preventable once consolidation is explicit.

**Consolidation quality is measurable.** Replace the full transcript with the record, re-run, compare outcomes. If they degrade, consolidation is lossy in a way that matters — and that is a number, not an opinion.

### 10.5 Long-horizon invariants

| Failure | Mechanism |
|---|---|
| Compaction drops the load-bearing detail | Structured consolidation, with a schema declaring what may not be dropped |
| Error compounds silently | **Periodic re-grounding** — re-verify assumptions against actual environment state, not against accumulated notes. Cheap, and the highest-value scheduled interrupt in a long run |
| Goal drift | The brief is immutable, sits in L4, is cheap to re-read, and is exempt from compaction. Work is checked against the brief, never against the last summary of it |

---

## 11. Playbooks: methodology as data

The reconciliation of the procedural instinct with loop flexibility. A truck is waterfall; a spaceship is intrinsically non-linear. Both are the same artifact with a different parameter.

### 11.1 The rigidity dial

| Rigidity | Semantics | Use |
|---|---|---|
| `advisory` | Injected as guidance; the agent may ignore it | Novel, exploratory, ill-specified work |
| `guided` | Phases enforced in order; behaviour *within* a phase is the agent's free loop. Skipping requires a recorded justification | The common case |
| `strict` | Phases gated; the agent cannot leave a phase until its gate passes | Known problem classes, compliance, production hotfix |

**At `strict`, a playbook is a graph.** The full procedural capability is recovered as a parameter on a data artifact, not as the architecture of the runtime.

### 11.2 Three levers, and no fourth

A playbook **constrains; it never dispatches.**

| Lever | Mechanism |
|---|---|
| Tool masking | The current phase narrows the offered catalog, through the same attenuation as everything else |
| Context injection | Phase intent enters as an L5 note — never L1–L4 mid-run (§10.2) |
| Gate evaluation | On phase exit: `strict` appends the failure and remains in-phase; `guided` advances, recording the skip and its justification; `advisory` has no gate |

The playbook never calls a tool, never selects a model and never writes to the workspace. If it could, it would be a second control path and the loop would no longer be the only execution primitive.

### 11.3 Earned, not authored

Playbooks are distilled from verified episodes, evaluated against both the unguided baseline and the incumbent, promoted only under the improvement relation, and demoted automatically on decay. Every playbook carries an evidence block and its invalidation conditions. This is what prevents the library ossifying into folklore, which is the standard end state of prompt-library approaches. The promotion mechanism is owned by `06 §5`.

Selection is configurable: the agent may select by applicability, or an operator may pin one for a task class. *The system decides its own path, unless we have decided for it* — a policy, not a fork in the code.

---

## 12. Process topology, seams and performance

Three processes at Phase 0, not five: **controller with broker** (one process, distinct modules, an audited internal boundary), **worker**, and **evaluator** — each with its own OS identity, mount namespace and credential set.

**Which plane guarantees hold when.** The six planes of §3 are a *separation of authority*; a process boundary is the strongest way to enforce one, and it is not the only way. Phase 0 collapses Interaction, Cognition and Control into the controller process, where their separation is enforced by module boundary and architecture test rather than by OS identity. Workload and Evidence get real process, identity and namespace separation from day one, because those are the two boundaries an attacker actually stands on. **The Evolution plane has no process in Phase 0 at all** — there is no autonomous updater, and `R0`/`R1` promotion is a human action outside the runtime (`05 [SA-5]`).

| Plane | Phase 0 | Phase 1 |
|---|---|---|
| Interaction · Cognition · Control | One process; module boundary, audited | Split; distinct identities |
| Workload | Separate process, identity, namespace, perimeter | Hardened perimeter |
| Evidence | Separate process, identity, image digest | Unchanged |
| Evolution | **No runtime component.** Human-operated | Release controller as a distinct identity |

Stating this is not a concession — an unstated gap between a diagram and a deployment is how "we have plane separation" becomes true in documentation and false in production. Five processes means five supervision surfaces and five failure modes before any feedback signal exists. The split to five happens in Phase 1, when the perimeter hardens; the decision and its reversal condition are recorded in `09`.

| Seam | Mechanism | Rationale |
|---|---|---|
| Daemon ↔ clients | Structured RPC over a local transport | CLI, inspector and any future surface are peers |
| Daemon ↔ systems components | **Subprocess with line-delimited JSON over standard streams** | Crash-isolated, language-agnostic, trivially swappable. The preferred default |
| Daemon ↔ laboratory | Versioned exported artifacts on disk | One contract, several consumers; decisively not an embedded runtime |

**Daemon, not a CLI with a UI bolted on.** That process boundary is cheap on day one and brutal to retrofit.

| Lever | Expected magnitude |
|---|---|
| Prompt caching via a stable L1–L4 prefix | Largest single cost lever. Vendor-reported reductions span roughly 50–90% on multi-turn work; **unverified here**, and `07 §5.8` names the experiment that would measure it |
| Parallel independent reads | Largest latency lever |
| Model tier routing — cheap for planning and consolidation, frontier for editing | Expected to be a large share of cost. Unmeasured; see `07 §5.8` |
| Operator isolation | Compounds with caching, since a stable parent prefix survives the child task |
| Result eviction | Extends the usable horizon at near-zero cost |

**The anti-pattern, named so it can be refused:** optimising orchestration. It is under five milliseconds against two to thirty seconds of model latency and up to two minutes of test execution. Every hour spent there is an hour not spent on caching or parallelism.

---

## 13. The transparency surface

Current coding tools are opaque by construction: they log for debugging, and the trajectory is a side effect. This is inverted here — the trajectory is the substrate, so the inspector is a **view over data already emitted**, not a system to be built.

| Surface | Content |
|---|---|
| Layered prompt | L1–L5 with per-block source attribution and exact cache-breakpoint positions |
| Provenance colouring | Every span rendered by label, so the user *sees* which parts are untrusted and what they were permitted to justify |
| Per turn | Request, reply, effects, results, cost from the ledger, latency, cache-hit rate |
| Decisions | Which playbook and on what evidence; which policy rule granted or denied; where a budget bit; why a phase advanced |
| Parallel branches | Branches side by side with per-branch verdicts, making selection visible rather than mysterious |
| Memory | What was recalled, from where, at what score, and **whether it changed the outcome** |
| Replay | Deterministic re-execution from recordings — closer to a debugger than a log viewer |

**Constraint:** the inspector is a pure consumer, holds no adapter handles and never schedules work, enforced by architecture test. *An inspector that can act is a second control path.*

This is a product thesis, not a debugging convenience: an agent that can be audited is adoptable where an opaque one is not.

---

## 14. Failure taxonomy

Enumerated because each has a specific mechanism, and an unnamed failure mode is an unhandled one.

| Class | Manifestation | Mechanism |
|---|---|---|
| `FT-01` Instrument error | Provider rate limit, socket reset, unbuildable image | Inconclusive outcome, excluded from resolve rate, per-branch rate reported |
| `FT-02` Livelock | Repeating transitions without progress | Progress-tuple detection (§6.4) |
| `FT-03` Budget exhaustion | Any dimension | Typed denial naming the offending call |
| `FT-04` Lease leak | An effect raising while holding a lease | Adapter resolved before reservation; release in `finally` |
| `FT-05` Grant staleness | A resumed run with a mutated request | Digest-bound expiring grant, verified at the effect |
| `FT-06` Prompt injection | Untrusted content steering a capability widening | Authority constraints and intent binding (`05 §5`) |
| `FT-07` Judge tampering | A candidate editing its evaluator | Unreachability plus the double probe (`06 §4`) |
| `FT-08` Second patch path | Two definitions of what changed | The environment's diff is the only one |
| `FT-09` Second judge | A ranker admitting | Only the activation policy admits |
| `FT-10` Decorative switch | A flag that reads as enabled and changes nothing | Single-object configuration; disconnection tests |
| `FT-11` Goal drift | Optimising the summary rather than the brief | Immutable, compaction-exempt brief |
| `FT-12` Context collapse | A load-bearing early decision compacted away | Structured consolidation; dead-end records |
| `FT-13` Cache thrash | Mid-run mutation of L1–L4 | Assembly-time breakpoint check |
| `FT-14` Orphaned concurrency | A failed branch leaving siblings or subprocesses | Task groups with cancellation reaching process groups |
| `FT-15` Silent recovery fiction | An undeterminable external effect resolved to success or failure | Preserved uncertainty (§9) |
| `FT-16` Conflict swallowing | Concurrent branches racing on one resource | Explicit conflict event; never last-write-wins |
| `FT-17` Escalation blindness | Repeated over-broad capability requests unnoticed | Denial recorded as an alertable event (`05 §4`) |
