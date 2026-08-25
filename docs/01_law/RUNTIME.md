---
id: normative-runtime-law
class: law
authority: normative
canonical_for:
  - vanguard-meta-harness-framework-v1
  - detailed-runtime-law
status: living
owner: principal-systems-architect
version: "0.6.2"
last_verified: 2026-08-25
read_when:
  - implementing-runtime-events
  - implementing-cold-recovery
do_not_read_when:
  - changing-only-documentation-navigation
subordinate_to: ../../VISION.md
supersedes: []
superseded_by: null
---

# Detailed Runtime Law — Vanguard Meta-Harness Framework (MHF v1)

> This is the preserved detailed body of the former root `SPEC.md`. The compact normative index is
> [`../SPEC.md`](../SPEC.md). No clause was discarded; this file remains the canonical source for
> runtime, plugin, safety, evolution, migration, and invariant detail.

**Status:** Normative detailed law. RFC-2119 language (MUST/SHALL/SHOULD) is binding here and in
the compact [`../SPEC.md`](../SPEC.md) index only — nowhere else in `docs/`.
**Version anchor:** v0.6.1 Foundation Evolution Lock (accepted ADRs `0069`–`0086`; see
[`../02_decisions/INDEX.md`](../02_decisions/INDEX.md)). The as-built Python package
version remains `0.4.5b1` in `pyproject.toml` until a later release cut.
**Supersedes:** v0.5.0 Foundation Lock destination story (`layer0/` as M1 rewrite target) and
mid-run plugin hot-swap as a v0.6 feature; `SYSTEM_SPEC_THEORY.md`, `SYSTEM_SPEC_ASBUILT.md`,
README's old biological/tier taxonomy, `docs/01_specs/backend/**` (archived, evidence not law; the
pre-lock corpus is retained only in git history, anchor commit `4f9f8b1` — no `docs/archive/` tree
exists on disk, `ADR-0075`).
**Consumes:** the archived Tech Lead review corpus — `CRITICAL_GAP_ANALYSIS_AND_AUDIT.md`
(Kill/Keep/Refactor register, invariants I-1…I-10), `NEXT_GEN_META_HARNESS_SPECIFICATION.md` (MHF v1
blueprint, the direct ancestor of this document), `01_SPECS_MIGRATION_MATRIX.md` (per-file merge
disposition) — all in git history at `4f9f8b1`. Forensic and proposal reports under
`../_archive/reviews/` are investigation and provenance, not law.
**Design lineage preserved:** S0–S12 dispatch kernel, JCS canonicalisation + golden vectors, exterior
signed evaluator, harness-as-data manifests, measurement lab, SQLite WAL ledger.
**Authority on conflict:** the compact index, this detailed law, and the other `01_law/` leaves define normative behavior;
accepted ADRs record why that law was narrowed or extended and MUST be reflected here before
implementation; `docs/03_execution/sprint_active.md` is the sole current execution authority; the
milestone ladder is macro sequencing only. Reviews, proposals, research, completed boards, and git
history are evidence, never implementation requirements.

---

## Preamble

> **Authority.** This leaf is normative but **subordinate to [`VISION.md`](../../VISION.md)** (Law
> Zero, `ADR-0095`). Where a clause here still describes the pre-0095 architecture, the Vision wins
> and the clause is reconciled — it is never a counter-authority. Clauses marked
> *current-state gap* describe implementation that has not yet reached the locked target.

**Vanguard is a general event-sourced agentic computation substrate that compiles harnesses.** The first *domain pack* is
coding; coding is not the architecture. One execution machine
(`Agent = Principal + HarnessInstance`, `ADR-0070`) runs every agent, subagent, and (later) swarm
participant. Declarative manifests plus versioned plugins compile into specialised harnesses. The
attenuation kernel, durable execution record, and optional assurance/evaluation modes are reusable
substrate capabilities. Self-improvement and
meta-cognition are Phase-2 plugins, not Layer-0 features, and they are **not implemented in v0.6**
(`ADR-0073`).

**What solved it must remain separable from the substrate that executed it.** Domain behavior belongs
in packs, plugins, adapters, and clients rather than the kernel or generic turn engine. When a run
claims independent promotion evidence, the judge must additionally be exterior and unreachable from
the judged process. Ordinary product runs may declare no evaluator and remain useful but
non-promotional.

**Non-claims** (merged line-by-line from the charter's §3, now folded into §9 below rather than kept as
a separate document): this specification does not claim continuous learning, does not claim the system
improves itself without human promotion of the release pipeline it explicitly refuses to build, does not
claim a competence graph exists, does not claim GUI/TUI parity is a backend requirement, and does not
claim any biological, cosmological, or "cognitive operating system" framing has operational meaning.
Every non-claim below in §9 is a promise about what will *not* be asserted, not a roadmap gap.

---

## 0. Design Axioms

**A-1. Microkernel, literally.** The trusted kernel is the S0–S12 effect reference monitor under
`vanguard/packages/kernel/`, with an enforced logical-LOC ceiling of 1438. Event reduction, plugin
lifecycle, scheduling, planning, memory, tools, context, evaluation, models, sandboxes, and domains
remain outside that TCB behind typed boundaries. State, price, belief, rating, or cached success
MUST NOT widen capability authority.

**A-2. The kernel governs effects; the loader governs plugins.** Two independent authority systems:
capability grants constrain what the *agent* may do (existing kernel); isolation tiers constrain what
*plugin code* may do (new). Neither trusts the other's subjects. *(Handbook M3 "the broker grants; the
sandbox contains" is this axiom's ancestor.)*

**A-3. Everything is an event or it didn't happen.** Grants, budgets, approvals, plugin activation,
evaluation requests, spawns — all ledger events. Replay is a *required* CI-enforced property
(Invariant I-4, `ADR-0071`, `ADR-0074`), not a slogan. Folding the same in-memory list twice is not
I-4. The production replay-parity gate MUST fold durable storage in a fresh process.

**A-4. One schema, many languages.** JSON Schema + JCS + golden vectors are the sole source of truth.
Python dataclasses and TS readers are *generated*. Hand-written mirrors are banned (closes AP-6 — Python
is the runtime language; TypeScript clients consume generated readers only, no hand-written TS domain
logic, per `ADR-0063`).

**A-5. Harness = f(manifest, plugins).** A harness is compiled at composition time from a declarative
manifest resolving plugin references; the compile output (`FrozenHarness`) is content-addressed. That
digest is harness identity **`D_H` only** (`ADR-0071`, `ADR-0074`). Execution identity `D_R` and
experiment-cell identity `D_X` MUST NOT be collapsed into `D_H`. `D_H` MUST include every
behavior-affecting input: resolved plugin refs and digests, system prompt, capability ceiling,
approval policy, and model routes. Two identical full compositions ⇒ byte-identical `D_H`. Two
harnesses that differ only in system prompt MUST NOT share `D_H`.

**A-6. Asymmetric evolution.** Later capabilities land as packs, plugins, manifests, adapters,
policies, or exterior/offline pipelines. The kernel changes only for a new irreducible authority verb
with its bound falsifier and TCB-budget proof; `agent.spawn` is the sole planned M-6 case.

---

## 1. Layer 0 — The Microkernel

Layer 0 is a *concern set*, not a mandate to rewrite the runtime into a second tree.

**Production lattice (as-built and canonical, `ADR-0069`).** `vanguard/packages/`:

```text
domain → ports → kernel → agency → runtime → adapters
         (apps/ is a client of runtime, not a second ontology)
```

Composition root remains `vanguard/packages/runtime/root.py`. This lattice is the **CI subject of
record** (`ADR-0073`): living CI runs the packages kernel/runtime/agency/adapters suites.

**Convergence boundary.** The former `layer0/` copy-fork has been removed from source, packaging,
CI, and tests during M-3 migration. Its behavior is authoritative only where absorbed into the
production lattice and covered by packages-path falsifiers. A compatibility stub or third runtime
tree is forbidden.

Boundary lattice (CI-enforced, closed roster) for the production hexagon:
`domain ← ports ← kernel ← agency ← runtime → adapters`; adapters MUST NOT import `kernel` or
`agency`. Plugins consume ports and wire contracts rather than importing the TCB.

### 1.0 Recursive machine, authority, and identity (`ADR-0070`, `ADR-0071`, `ADR-0074`)

```text
Agent    = Principal + HarnessInstance
SubAgent = Principal(parent_id set) + HarnessInstance   # same Principal type; not a second class
```

`Principal` is a typed value `(id, parent_id?, depth)`, not a bare string. `ChildPrincipal` is not a
distinct type. `spawn(parent, harness, capabilities, budget)` is the only delegation primitive.

**Project.** A Project is a durable named scope that owns one ledger stream, one capability ceiling,
and one root budget. Every Episode, Principal, and Artifact belongs to exactly one Project.
`project_id` is the consistency unit: total order holds inside a Project, not across Projects.

MUST hold:

- `Capabilities(child) ⊆ Capabilities(parent)` under one selector partial order. Unknown relation =
  deny. Unbounded child under bounded parent = deny.
- **Typed budget (`ADR-0074`).** Additive conserved: `usd_micros`, `tokens`, `bytes`, charged
  `millis` (compute time) — `child ≼ remaining(parent)` component-wise. Structural ceilings:
  `depth` (`child.depth = parent.depth + 1 ≤ root.max_depth`; sibling depths are not summed) and
  `turns`.

Swarm participation is a coordination **policy** over agents, not a swarm engine. Causal relations
(`spawned_by`, `caused_by`, `produced`, `evaluated_by`) are **projections of events** (`ADR-0003`).

**Decision plane** (scheduler / kernel / grant issuer / governor) decides who/when/lease/budget/capability.
**State plane** (ledger + pure reducers) decides what happened:
`Decision → DurableEvent → fold → EffectiveState`. Orchestrator memory is never source of truth.
Privileged event kinds MAY be originated only by their owning authority (`ADR-0074`). Hash-chain
integrity does not imply semantic truth.

Every new event kind MUST carry: `project_id`, `principal_id`, optional `parent_principal_id`,
`episode_id`, optional `parent_episode_id`, `harness_digest` (`D_H`), `causation_id`,
`correlation_id`.

Identity trinity: `D_H` complete composition (A-5); `D_R` execution
(`D_H` + runtime + environment + model identity + oracle identity); `D_X` experiment cell
(`D_R` + dataset + protocol). FrozenHarness digest is `D_H` only.

### 1.1 The turn state machine

The universal lifecycle is retained and completed — evaluation moves *inside* the event stream (fixes
D-02/D-03):

```text
observe → propose → authorize → effect → receipt → evaluate → (reflect)*
```

`reflect` is an optional stage owned by the Phase-2 outer loop (§7); Layer 0 knows only that a
registered `IPlanner` may be offered the terminal receipt set. State transitions are pure reducers over
the ledger (`state = fold(events)`); the engine holds no state a replay cannot reconstruct. *(Handbook
M1 "the episode is the program" — no workflow engine — is this section's ancestor and is reinforced by
the REJ on playbook runtimes, `docs/02_decisions/DEFERRED_REJECTED.md` `REJ-01`. VG-03 §2's loop-over-DAG
inversion — "strictly less expressive than a loop that can invoke a loop, at roughly ten times the
machinery, proof by construction" — is the argument for this shape and is carried here by citation
rather than restated; see also `docs/02_decisions/DEFERRED_REJECTED.md` `REJ-01`.)*

**I-11 (v0.6).** The scheduler is **sequential**. Concurrency (independence groups, §1.4) is a later
scheduler property, gated on a measurement. Unknown selector footprint means conflict, not
independence (`ADR-0073`, `ADR-0074`). This is Invariant I-11.

**Composition is not control flow (`ADR-0077`, `ADR-0082`).** The Named Component Graph is resolved
and frozen only at composition time. During execution, each episode still advances through one
unary, sequential turn loop. Bindings make components addressable; they MUST NOT be interpreted as
a dynamic workflow DAG, a graph scheduler, or authority to execute edges. Multi-agent topologies
MUST enter through capability-mediated `agent.spawn` when M-6 opens, or through already composed
plugins invoked by the same loop. No component name or graph edge may add an alternate runtime path.

### 1.2 Event taxonomy (emission is mandatory)

Full kind set, grouped; every kind lists its single production *owner*. M-3 lifecycle kinds are now
implemented on the packages path; M-3 cannot close until the remaining falsifiers prove complete
coverage, registry ownership, and atomic convergence. Lexical CI rule `E-COV`
(string presence in a named directory) is a **weak proxy**, not I-2 (`ADR-0074`). I-2 requires a
reachable production emitter *and* that forged/synthetic payloads (including
`VerdictRecorded {verdict: "pass"}`) cannot become accepted history. Writer authority per kind is
in the Evidence column conceptually: kernel owns grants/budgets/effects; evaluator gateway owns
`VerdictRecorded`; registry owns plugin lifecycle; scheduler owns run/episode lifecycle.

| Group | Kinds | Emitter |
|---|---|---|
| Lifecycle | `RunStarted`, `EpisodeStarted`, `TurnStarted`, `EpisodeCompleted`, `RunCompleted`, `RunAborted`, `RunRecovered` | scheduler |
| Cognition | `ProposalProduced`, `ProposalRejected`, `ReflectionProduced` | scheduler (from `IPlanner`) |
| Authorisation | `AuthorizationRequested`, `AuthorizationDenied`, `CapabilityGranted`, `CapabilityAttenuated`, `CapabilityRevoked` | kernel S5/S6 |
| Budget | `BudgetReserved`, `BudgetCommitted`, `BudgetReleased`, `BudgetExhausted` | kernel S7/S10/S11 |
| Effects | `EffectStarted` (S8a, fsync-before-dispatch, K-47), `EffectCompleted`, `EffectFailed`, `EffectRejected`, `EffectReconciled` | kernel |
| Evidence | `EvaluationRequested`, `VerdictRecorded` (signed), `ClaimRecorded`, `InvalidationChecked` | scheduler / evaluator gateway |
| Governance | `ApprovalRequested`, `ApprovalResolved` (ledgered, fixes D-13), `KernelAlarm` (F-21a **and** F-24, per ADR-M0-09) | kernel / approval service |
| Plugins | `PluginDiscovered` (M-3), `PluginResolved`, `PluginVerified` (M-3), `PluginActivated`, `PluginQuiesced`, `PluginRetired`, `PluginFaulted` | registry |
| Health | `Heartbeat` (HMAC-authenticated, fixes D-14), `CheckpointCreated` | scheduler |
| Delegation | `ChildSpawned`, `ChildReturned` (carries provenance spans, fixes D-06) | scheduler |

**Writer authority (`ADR-0074`).** The Emitter column is the *legal originator*. Untrusted
coordination (orchestrator, plugins, Protocol clients) MAY request; they MUST NOT generic-append
privileged kinds. Owning authorities:

| Kind class | Legal writer |
|---|---|
| Grants / budgets / `EffectStarted` and terminals | kernel |
| `VerdictRecorded` | evaluator gateway (signature-valid, request-bound) |
| Plugin lifecycle | registry |
| Run / episode lifecycle | scheduler |
| `ApprovalResolved` | approval service |

Envelope: JCS-canonical JSON, SHA-256 content digest, `prev_digest` hash chain per **Project**
(`project_id`), monotonic `seq` within that unit, `causation_id`/`correlation_id`, idempotency key on
all command-derived events, `branch_id`, and the lineage fields of §1.0. Store: SQLite WAL + `FULL`
sync (keep, D-16) with JSONL export; blob writes are `write→fsync→emit(digest)` ordered, closing D-19
(event never references an undurable blob).

### 1.3 Determinism & replay contract

**Replay and re-execution MUST NOT be conflated.**

*Replay* applies persisted events to compatible reducers and reconstructs the semantically equivalent
state that existed at a point in the execution. A prior model response is **not** recomputed: it is
already a recorded fact. Under identified schemas, reducer versions, and artifacts, replay is
deterministically reproducible. Replay answers: *what state results from the history that occurred?*

*Re-execution* runs models, tools, or policies again over equivalent inputs. It carries **no such
guarantee**. Even at temperature zero, backend changes, floating-point behaviour, batching, model
routing, provider revisions, and infrastructure differences may change the result. Low temperature
reduces variance; it does not make modern model inference deterministic. Re-execution answers:
*what would happen if equivalent conditions were submitted again?*

Both are legitimate and both are used. Re-execution over a recorded trajectory is the basis of
**re-simulation**: hold part of a trajectory fixed and vary a model, prompt, topology, compaction
policy, retrieval depth, recursion depth, budget, tool selection, or strategy controller. The
scientific requirement is not to pretend determinism exists, but to state exactly which variables
were held constant, which were changed, and what resulted — see
[`MEASUREMENT.md`](MEASUREMENT.md) and [`EVIDENCE.md`](EVIDENCE.md).

`ClockPort`, `RandomPort`, and model cassettes remain injected; replay mode substitutes recorded values
keyed by `(run_id, seq)`. **Replay taxonomy (`ADR-0071`) — these MUST NOT be conflated:** state replay
(deterministic reconstruction of grants, budgets, approvals, episode FSM); schedule replay (needs
recorded nondeterminism); real-world re-execution (not required to match); byte-identical fixtures
(only fully controlled inputs). Concurrent executions are not required to produce byte-identical
ledgers. Consistency unit is `project_id`.

**CI replay-parity gate (wired as `ColdReplayParity` in `.github/workflows/ci.yml`):** execute a
live fixture run against the **production** ledger, fold its ledger cold, structurally diff
reconstructed vs live terminal state — grants tree, budget vector, approval log, episode FSM included.
Folding the same in-memory list twice is not this job. Time-travel debugging = fold to `seq=N` + resume
with a divergent `branch_id`. Crash recovery = scan for `EffectStarted` without terminal effect event
⇒ mark *undeterminable* ⇒ run `EffectReconciled` probe (existing semantics, kept).

### 1.4 Scheduler

Replaces the sequential `EpisodeEngine` outer shell (engine's dispatch discipline is preserved inside).
Adds: independence groups (proposals declare read/write resource selectors; non-intersecting selectors
*may* run concurrently once I-11's gate is met — this unlocks D-38 without touching the kernel, but does
not enable it in v0.6), cooperative cancellation tokens, turn/depth ceilings as first-class
`Reservation` dimensions (resolves D-09/D-24 per **ADR-M0-07**, algebra corrected by **ADR-0074**):
the six named fields remain `{usd_micros, millis, tokens, bytes, turns, depth}`, but they are **not**
one additive vector — additive conserved `{usd_micros, tokens, bytes, charged millis}` versus
structural ceilings `{depth, turns}`. Sibling depths are not summed. Heartbeat emission stays.

### 1.5 Agent state is a projection

**`Agent = Identity + Policy + Event-Derived Projection + Execution Boundary`.** There is no
privileged persistent `Agent` object in the architecture. *Identity* correlates a lineage; *policy*
influences which operations are chosen; *projection* derives the semantically relevant state from the
ledger; *execution boundary* bounds resources, context, budget, depth, and terminal conditions.

`Episode`, `HarnessSession`, `_LayeredOperator._dialogue`, and equivalent runtime objects MAY hold
transient optimization state — caches, buffers, open handles, memoized context. **No state required
for semantic continuation may exist only inside those objects.** Everything needed to recover the
current goal, plan, relevant observations, settled effects, budget state, strategy state, context
references, and terminal status MUST be reconstructible from canonical events and artifacts through
projections. A process may die; another process opens the ledger, rebuilds the lineage, and continues.

Because state is projected rather than stored in an object, a lineage may be **metamorphic**: the same
identity may begin exploring, adopt a planning strategy, enter debugging behaviour, request
delegation, abandon a hypothesis, and terminate as a synthesizer — without its ontological nature
being fixed in advance and without destroying provenance.

Domains MAY define their own projections. The canonical **ledger reducer remains single**; a
domain-specific view is a projection over it, never a second reducer of record and never a second
source of truth.

> **Current-state gap (closed by M-5a).** Today, part of the semantic continuation state still lives
> inside `Episode`/`HarnessSession` objects rather than in projections, and the `AgentView` event
> vocabulary (goal declaration, plan revision, strategy selection, progress assessment, context
> compaction) is not yet allocated. This is a documented migration, not a weakening of the rule
> above. The substrate is re-tagged as the new `M-5-BASE` once the migration lands.

### 1.6 Physical append order and the logical causal graph

`seq` is the **durable physical append order** within a consistency unit (`project_id`). It provides
total order for persistence, recovery scanning, and `(run_id, seq)` keying.

`seq` is **not** logical dependency. Causation, parentage, correlation, lineage, branches, and joins
define the **logical, partially ordered execution graph**. `A -> C` and `B -> C` may both hold without
any ordering between `A` and `B`. Conflating the two is what turns an event log into a false claim
about what depended on what.

> **Current-state gap.** The runtime today executes a single sequential turn loop (I-11) and the
> partially ordered graph is expressed only through `causation_id`/`correlation_id` on the envelope.
> Branch, join, and readiness semantics are **target architecture**, gated on the M7-01 measurement
> and a successor ADR under M-7. Nothing in this section claims those features exist today.

---

## 2. Plugin Architecture & SPI Definitions

### 2.1 Plugin model

A plugin is a directory (or wheel/OCI/WASM artifact) containing `plugin.yaml`, code, and schemas,
discovered via scan paths + Python entry points (`mhf.plugins`), content-addressed by the JCS digest of
its manifest + file tree.

```yaml
# plugin.yaml — declarative plugin manifest (JSON Schema: mhf.plugin/1)
api: mhf.plugin/1
id: mhf.toolkit.ast-patch
version: 2.1.0                # semver; registry enforces caret-compat resolution
provides:
  - spi: IToolkit
    spi_version: ">=1.0,<2"   # SPI version negotiation, independent of plugin version
requires:                     # inter-plugin deps, resolved topologically
  - id: mhf.index.tree-sitter
    version: ">=1"
isolation: subprocess          # in_process | subprocess | container | wasm
capabilities:                  # ceiling of grants this plugin may ever be offered
  - verb: fs.read
    selector: {kind: fs, root: /workspace}
  - verb: patch.apply
    selector: {kind: fs, root: /workspace}
entry: mhf_ast_patch.plugin:AstPatchToolkit
config_schema: ./config.schema.json
signature: ed25519:...         # optional publisher signature; policy may require it
```

**Lifecycle FSM (registry-owned, every transition ledgered):** `DISCOVERED → RESOLVED (deps + SPI
version negotiation) → VERIFIED (schema + signature + capability-ceiling policy check) → ACTIVATED
(isolation broker starts the cell) → QUIESCING (drain in-flight calls) → RETIRED`, with `FAULTED`
reachable from any active state (crash-loop backoff, automatic fallback to a declared substitute plugin
if the manifest names one). **v0.6 forbids mid-run FrozenHarness hot-swap (`ADR-0005`, `ADR-0072`).**
Quiesce exists for fault and restart, not for flipping composition under a live `D_H`. A restart MAY
activate a newly composed FrozenHarness as a *new* run with a new `D_H`. **A trivial echo-plugin
MUST traverse this full lifecycle before any real plugin is written (ADR-M0-13, the walking-skeleton
rule), on the canonical production path.**

The SPI **contract** is JSON-RPC 2.0, line-delimited, over Unix domain sockets (`ADR-0002`,
`ADR-0059`, `ADR-0072`). Python `typing.Protocol` is a client convenience. Wire parity means every
tier MUST accept and produce values conforming to the same generated JSON Schemas and method
semantics; it does not require every tier to serialize bytes or open a socket. `in_process` is an
isolation privilege, not a second SPI, and MUST dispatch validated typed values directly in memory.
It MUST NOT incur UDS, JSON encoding/decoding, or copy-through-wire overhead for heavy context
bundles. Subprocess and container tiers continue to use the normative UDS framing.

**Isolation tiers (A-2):**

| Tier | Mechanism | Latency | Use |
|---|---|---|---|
| `in_process` | Same interpreter; direct typed dispatch after schema-boundary validation; static import lint + audit hook | ~0 | First-party, signed, reviewed (context compiler) |
| `subprocess` | Fork per plugin; JSON-RPC over UDS; enforced rlimits + seccomp profile (closes D-31) | ~1–5 ms/call | Default for toolkits, planners |
| `container` | Rootless bubblewrap/OCI, UID-separated (existing worker pattern) | ~10–50 ms cold | Anything executing user/model-authored code |
| `wasm` | wasmtime component w/ WASI-preview2 caps | ~0.1–1 ms/call | Untrusted third-party pure-compute plugins |

The evaluator remains its own identity (UID 10002 daemon) — it is *not* a plugin an agent-side manifest
can replace; `IEvaluationGate` plugins run agent-side and merely *request* judgment; verdict signing keys
never enter any plugin cell. The scheduler MUST **read** a signed verdict; emitting
`VerdictRecorded {verdict: "pass"}` without a signature is defect F1, not a plugin strategy
(`ADR-0072`). See `docs/01_law/DISPATCH.md` §6 (`K-40`, amended by **ADR-M0-08**).

### 2.2 SPI definitions (typed, frozen, versioned)

The canonical SPI protocols live in `vanguard/packages/ports/spi.py`; JSON-RPC lives in
`vanguard/packages/domain/wire/jsonrpc.py` (`ADR-0069`). Python `Protocol` remains a client of the
JSON-RPC wire; no residual `layer0/` dialect is authoritative.

All payload types are frozen dataclasses **generated** from `schemas/mhf/*.json` (A-4; resolves
D-21/D-29 — exactly one `EffectRequest`). Signatures below are normative.

```python
# spi/types.py (generated) — excerpts
@dataclass(frozen=True, slots=True)
class EffectRequest:          # THE one and only
    verb: str
    args: JsonObject          # JCS-canonicalised for descriptor digest
    selector: ResourceSelector
    sink: SinkClass           # OBSERVATION | ADVISORY | PRIVILEGED
    reservation: Reservation  # six named fields; typed algebras per ADR-0074

@dataclass(frozen=True, slots=True)
class Proposal:
    thought: str | None
    requests: tuple[EffectRequest, ...]
    independence_groups: tuple[frozenset[int], ...] = ()
    confidence: float | None = None

@dataclass(frozen=True, slots=True)
class Receipt:
    request_digest: Digest
    outcome: Literal["completed", "failed", "rejected", "undeterminable"]
    stdout_ref: BlobRef | None
    artifacts: tuple[ArtifactRef, ...]
    cost: Reservation
    lease_id: str
    grant_digest: Digest
```

```python
# spi/planner.py — SPI v1
class IPlanner(Protocol):
    """Turn-level cognition. Inner planners emit Proposals; outer (meta)
    planners may also consume terminal receipts via reflect()."""
    spi_version: ClassVar[str]  # "1.0"

    def plan(self, view: EpisodeView, budget: Reservation) -> Result[Proposal]: ...
    def observe(self, receipts: Sequence[Receipt], view: EpisodeView) -> None: ...
    def reflect(self, outcome: EpisodeOutcome,
                trajectory: TrajectoryRef) -> Result[Reflection | None]: ...
```

```python
# spi/memory.py
class IMemoryEngine(Protocol):
    spi_version: ClassVar[str]
    def write(self, record: MemoryRecord) -> Result[MemoryId]: ...
    def recall(self, query: MemoryQuery, budget_tokens: int) -> Result[tuple[MemoryHit, ...]]: ...
    def consolidate(self, since: Seq) -> Result[ConsolidationReport]: ...
    def invalidate(self, claim: ClaimRef, reason: str) -> Result[None]: ...
    # Phase-3 graph extension is a *capability*, negotiated, not a new SPI:
    def capabilities(self) -> frozenset[str]: ...   # e.g. {"kv", "vector", "graph"}
```

```python
# spi/toolkit.py
class IToolkit(Protocol):
    """A bundle of effect adapters. The kernel resolves verbs to toolkits at
    S2; toolkits NEVER see grants — they receive only verified, leased work."""
    spi_version: ClassVar[str]
    def verbs(self) -> Mapping[str, ToolSchema]: ...           # JSON Schema per verb
    def execute(self, request: EffectRequest, ctx: EffectContext) -> Result[Receipt]: ...
    def compensate(self, receipt: Receipt) -> Result[Receipt]: ...   # deterministic rollback
    def health(self) -> Health: ...
```

```python
# spi/context.py
class IContextManager(Protocol):
    """Prefix-stable prompt assembly. L1–L3 frozen at composition (kept);
    strategy for L4/L5 is the plugin's business."""
    spi_version: ClassVar[str]
    def compile(self, view: EpisodeView, budget_tokens: int) -> Result[ContextBundle]: ...
    def ingest(self, receipts: Sequence[Receipt]) -> None: ...
    def compact(self, pressure: float) -> Result[CompactionReport]: ...
    def reground(self, error: EffectFailure) -> Result[ContextBundle]: ...  # wires D-10
```

```python
# spi/evaluation.py
class IEvaluationGate(Protocol):
    """Agent-side evidence plane. Requests judgment; never renders it.
    Verdicts arrive as signed VerdictRecorded events from the exterior daemon."""
    spi_version: ClassVar[str]
    def request(self, subject: EvaluationSubject) -> Result[EvaluationRequestId]: ...
    def gate(self, verdicts: Sequence[SignedVerdict]) -> GateDecision: ...  # PASS|RETRY|ESCALATE|ABANDON
    def preregister(self, oracle: OracleSpec) -> Result[PreregistrationId]: ...
```

Additional first-party SPIs (same pattern): `IModelProvider` (replaces `ModelPort`; typed messages, tool
schemas, usage accounting, cassette capability), `ISandbox`, `IEventStore`, `IBlobStore`,
`IApprovalChannel`. SPI evolution rule: additive within a major; `capabilities()` negotiation for
optional features; breaking change ⇒ new SPI major and a dual-routing deprecation window in the
registry.

**ADR-M0-03 (five SPIs, not four).** The engineering handbook's M2 "exactly four pluggable things" is
superseded: MHF has exactly **five** frozen SPIs above (`IPlanner`, `IMemoryEngine`, `IToolkit`,
`IContextManager`, `IEvaluationGate`) plus the first-party `IModelProvider`/`ISandbox`/store ports, which
are not user-pluggable extension points in the same sense. **A sixth SPI requires a design review, not
a PR** — see [`ADR-0072`](../02_decisions/0072-plugin-boundary-wire-first-evaluator-exterior.md) and the
[consolidated M0 lineage](../02_decisions/INDEX.md#consolidated-historical-lineage).

### 2.3 Canonical manifest and execution plans (the compile target)

`mhf.manifest/2` is the sole authored production form. It declares named components, typed bindings,
resolved implementation/config references, interfaces, entrypoints, profiles, isolation/evidence
policy, and capability ceilings. Supported `mhf.harness/1` bytes remain compatibility ingress through
M-4, but normalize immediately and never become a second runtime value.

```text
mhf.manifest/2 bytes
  -> CanonicalManifest
  -> FrozenComposition [JCS D_H]
  -> ActivationPlan [activation_digest binds D_H]
  -> RunPlan [execution identity D_R]
  -> EpisodeEngine -> S0-S12
```

`FrozenComposition` is the immutable logical graph. `ActivationPlan` is the deterministic runtime
projection containing component factories/cells, effective ceilings, validated interfaces,
initialization dependencies, readiness, and reverse cleanup; it introduces no authority and is not a
workflow scheduler. `RunPlan` binds the composition/activation to task, project, environment, store,
model, oracle/evaluator, root authority, budget, and execution mode. `run_id` correlates durable events
and is bound to `D_R`; it is not an identity substitute.

All behavior-affecting logical inputs enter `D_H`; activation/runtime/environment choices enter
`D_R`; dataset/protocol choices enter `D_X`. Mid-run plan or composition change is forbidden.
`FrozenHarness` may be a temporary API facade only when it wraps the single `FrozenComposition`.
Unknown fields/refs/providers/interfaces/endpoints, unread authority, empty/incomparable ceilings, or
eager activation cycles fail before activation. Domain verbs are provided by namespaced adapters
behind ports, never by a global coding-specific extension authority (`ADR-0088`).

---

## 3. Autonomous Execution Safety & Deterministic State

**Sandbox boundary.** All `proc.exec`/`patch.apply` effects execute inside the container tier regardless
of toolkit isolation tier (defense in depth: plugin cell + workspace cell). Mandatory closure of D-31:
seccomp allowlist profile per verb class, `setrlimit` enforced in the worker pre-exec, no-new-privs,
read-only base image, network default-deny with per-grant selectors (`proc://exec/allow/...` selectors
kept).

**Deterministic rollback.** Workspace mutations run on an overlayfs (or git-worktree fallback) snapshot
per turn; `Receipt.artifacts` carries the layer digest. Rollback policies, declared in the harness
manifest: `turn` (drop layer), `checkpoint` (fold to `CheckpointCreated`), `compensate` (invoke
`IToolkit.compensate` for effects with external footprint). A failed effect with a durable
`EffectStarted` and no receipt triggers reconciliation probes before any retry (idempotent replays, kept
semantics). *(VG-03 §7.5's irreversibility analysis is this rollback taxonomy's ancestor, per matrix
§1.6.)*

**Crash recovery and trajectory continuity (RF-25 / RF-23).** On boot in a fresh process: open the
file-backed SQLite-WAL store → verify and fold the durable event prefix → find open runs → restore
sequence/digest lineage and Governor budget state → release or reconcile every reserved-but-uncommitted
lease without widening the remaining budget → verify heartbeat staleness (HMAC) → classify open S8a
intents as undeterminable until an exterior reconciliation resolves them → emit `RunRecovered` through
the canonical writer → resume at the exact legal turn, or emit `RunAborted` with cause. Live Python
objects MUST NOT be a recovery input. The recovered session MUST retain the pre-crash prefix as an
input to `assemble_trajectory()`; at `EpisodeCompleted`, the emitted `mhf.trajectory/1` row MUST join
that prefix with all post-recovery turns exactly once. This joint obligation is I-9, not merely state
replay, and prevents both budget leakage and history truncation.

---

## 4. Coding Domain Pack (first domain; foundation E2E, not this lock wave)

**v0.6 status:** this section is the *shape* of Domain Pack #1. It is not authorized as the next
commit. Foundation coding-agent E2E is Wave 4 of
`docs/_archive/reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`.

Everything below is plugins + one domain pack; Layer-0 / production-core diff for a new pack MUST be
zero (Invariant I-7: domain tokens `coding|pytest|ast` MUST NOT appear under `layer0/` **or**
`vanguard/packages/{domain,kernel}/`).

**4.1 AST patch engine (`mhf.toolkit.ast-patch`).** Tree-sitter parse per file (incremental re-parse on
edit, sub-ms for typical files); patches expressed as **anchored edits** — `(node_kind, qualified_name,
content_digest_of_anchor) → replacement` — falling back to search/replace then unified diff (the Aider
lesson: match the edit format to model competence, negotiated via `IModelProvider.capabilities()`).
Every applied patch emits an AST-level structural diff into the receipt (symbol added/removed/
signature-changed), which is what the planner and the DPO harvester consume — raw text diffs are a blob
ref, not context.

**4.2 Dynamic file index (`mhf.toolkit.index` + `mhf.context.repo-map`).** Merkle tree over the
workspace (dirty-subtree invalidation on receipts); tree-sitter tag extraction (defs/refs); import-graph
+ reference-graph ranking (personalised PageRank seeded by task-mentioned symbols) rendered into a
token-budgeted repo map in L4; optional embedding sidecar declared as a memory capability. Index updates
are receipt-driven — the index never scans on the hot path.

**4.3 Terminal loop (`mhf.toolkit.terminal`).** PTY-backed persistent shell per workspace cell;
incremental output streaming with early-classification (test-runner adapters parse pytest/ruff output as
structured events at first failure, not at process exit) — this is the sub-second feedback mandate: the
planner receives the first structured failure typically <300 ms after it prints, while the process may
still be running under its lease. Timeout/censoring semantics from `dogfood-02` are preserved as
contract tests.

**4.4 Planner (`mhf.planner.drive-until-green`).** Port of `tier_escalation.py` (the D-41 salvage): plan
→ patch → verify loop, model-tier escalation Free→Cheap→Frontier on `verdict_fail` while budget holds,
repair rounds bounded by manifest config. Verification is `IEvaluationGate` against preregistered
oracles — the agent never grades itself.

**Pack acceptance (Wave 4, not this lock):** the compiled `code-default` harness exercises real model,
authorized effect, filesystem, sandbox, signed eval, WAL, cold replay, and a schema-valid
`mhf.trajectory/1`. Lexical E-COV = 100% is **not** that gate.

**M-5 generality proof (`ADR-0088`).** Pack #2 is Math & Formal Deductive Verification. Its exact
proof language/toolchain is selected and preregistered at M-5; it is not substrate law. The pack uses
the same `/2 -> FrozenComposition -> ActivationPlan -> RunPlan`, S0–S12, exterior verdict, WAL,
trajectory, and cold-reconstruction path. During the proof interval only pack, adapter,
evaluator/container, and test surfaces may change; the semantic tree under
`vanguard/packages/{domain,ports,kernel,agency,runtime}` remains unchanged. A missing generic
primitive fails the proof and returns to governance. RF-86 is the gate.

---

## 5. Evolution Blueprint — Phase 2 (autonomous & meta-cognitive)

**Status: post-v1 research-only blueprint (`ADR-0088`).** Trajectory schema/emission remains locked so
research can consume attributable data, but mutation, skill harvest, VFE/EFE, DPO, and promotion do
not enter the v1 foundation programme and have no implementation authority here.

All Phase-2 features are plugins consuming Phase-1 extension points.

**5.1 Dual-loop execution.** Inner loop: unchanged Phase-1 planner. Outer loop:
`mhf.planner.meta-reflector`, a *second* `IPlanner` instance registered at scheduler slot `outer`,
invoked at `reflect()` with the terminal trajectory. It runs in its own episode with its own budget lease
(the kernel already supports nested principals via `spawn()` — now provenance-carrying per §1.2
`ChildReturned`). The outer loop's effects are restricted by capability to: manifest-mutation proposals,
skill writes, and preregistration of new oracles. It cannot touch the workspace — meta-cognition is
capability-shaped, not trust-shaped. (A tool is not an episode and an episode does not become a second
engine — **ADR-M0-12** — this is what keeps the outer loop a plugin at a scheduler slot rather than a
`MetaLoopEngine` reincarnation, honouring `ADR-0041`/D-41.)

**5.2 Evolutionary prompt/manifest mutation.** The manifest is the genome (the repo's "genes" intuition,
operationalised without the biology talk). Mutation operators over JCS-diffable manifest fields:
system-prompt fragment substitution, tool-schema phrasing variants, compaction strategy, escalation
thresholds. Selection requires preregistered paired lab runs against an immutable baseline. No
`CanaryPromoted` event or automatic pointer change is presumed: only the human-controlled promotion
authority may move a versioned default after exact statistical, exterior-evidence, and rollback gates.
Population bookkeeping remains exterior research state and carries no runtime authority.

**5.3 Active-inference error minimisation.** Frame the gate decision as expected-free-energy
minimisation without importing the full formalism: the planner maintains `P(pass | action, context)`
calibrated from the ledger's `CompetencePriorRecorded`/`VerdictRecorded` history (the prior recorder
already exists); action selection scores `expected_verdict_gain − λ·reservation_cost`; escalation and
abandonment become threshold policies on the same scalar. This unifies tier escalation, retry, and
abandonment under one calibrated decision rule and makes miscalibration *measurable* (Brier score per
harness digest in telemetry).

**5.4 Dynamic skill synthesis.** Harvester (outer-loop toolkit) mines successful trajectories for
recurring effect n-grams with high verdict-conditional lift; emits candidate skill cards (the existing
skill-card format, `pytest-green.md` etc.); candidates enter the manifest only through the §5.2
selection pipeline. Skills are therefore *distilled, tested procedures*, never model free-text pasted
into prompts. This is the "advisory" rung of the playbook-rigidity dial — see the honour table (§9):
`guided` is a planner-plugin policy on top of this data; `strict` (deterministic DAG execution) is
rejected outright, not deferred.

---

## 6. Evolution Blueprint — Phase 3 (General Task Solver)

**v0.6 status: deferred blueprint (`ADR-0073`).** Recursive `spawn` semantics are locked now so this
phase does not require a second engine. Market allocators, memory graphs, and heterogeneous swarms
are not foundation scope.

**6.1 Neuro-symbolic memory graph.** `IMemoryEngine` implementation advertising the `graph` capability:
typed nodes (Claim, Artifact, Skill, Task, Entity), signed-evidence edges (supports/contradicts/derives),
embedding index over node text. The dormant v4 types (`Claim` graph fields, D-23; `Artifact.compensatesFor`)
become live: recall = graph walk seeded by vector hits, pruned by invalidation checks
(`InvalidationChecked` events). Symbolic edges give auditability; embeddings give recall; the ledger
gives provenance — no core change, one plugin. Gated on the activation-bundle rule (Invariant I-3): this
plugin carries no normative force until it actually ships.

**6.2 Market-based token budgeting.** The kernel `Governor` already implements leases; Phase 3 adds an
allocator plugin running a sealed-bid second-price (Vickrey) auction per scheduling round: child
episodes/agents bid reservation vectors against declared expected-verdict-gain (from §5.3 calibration);
truthful bidding is incentive-compatible under second-price, and the *kernel remains the settlement
layer* — the market only decides which reservations the scheduler submits. Budget conservation stays a
kernel invariant; economics is policy.

**6.3 Capability-mediated delegation (M-6 plan).** `agent.spawn` is an ordinary privileged effect
addressed by target `D_H`. Agency may request it but cannot create a production child. The generic
kernel mediates S0–S8a; after durable intent, a runtime adapter creates the child principal, session,
and workspace with the fail-closed intersection of parent, target, plugin, and request ceilings.
`ChildSpawned`/`ChildReturned` plus the effect receipt carry lineage and settlement. Output returns as
untrusted-derived context. No ambient handles, credentials, evaluator endpoint, or parent memory are
inherited. Recovery never repeats a settled spawn; an open intent stays undeterminable. The kernel
MUST NOT branch on the verb or learn child topology (`ADR-0080`, `ADR-0088`).

```text
spawn request -> S0..S8a intent -> runtime child adapter -> bounded child episode
  -> ChildReturned/receipt -> S10..S12 settle -> untrusted-derived return
```

**6.4 Domain-agnostic decomposition.** A Domain Pack = {toolkit(s) + oracle suite + manifest defaults +
selector vocabulary}. Pack #2 is **Math & Formal Deductive Verification**, the M-5 generality
witness. TableWorld may be a later pack but cannot satisfy that gate. The decomposition planner is
domain-blind: it operates on verbs, selectors, oracles, and cost vectors — the domain lives entirely in
the pack. **Acceptance: adding Pack #N requires zero diffs under
`vanguard/packages/{domain,kernel}/` (Invariant I-7).**
— this is the handbook's M11 "Generality Falsification Invariant," merged here per matrix §1.4.

---

## 7. Telemetry, Self-Tuning & Model Distillation

**v0.6 foundation locks the trajectory record (I-9, `ADR-0074`).** DPO harvest, fine-tune, and
promotion remain deferred (`ADR-0073`). The schema MUST exist and MUST be emitted at
`EpisodeCompleted`; consumers of the dataset are not this version's kernel.

Each turn MUST carry an ordered `invocations` sequence rather than a single implicit model call.
Every retry, fallback, critic call, or escalation is a distinct invocation with resolved route,
provider/model identity, fingerprint or typed absence reason, measurement status
(`measured`, `estimated`, or `unavailable`), and additive cost. Turn cost is the sum of its
invocations plus explicit non-model turn charges; episode cost is the sum of all turns plus explicit
non-turn charges. Missing operands propagate typed unavailability and MUST NOT be replaced by zero.
The ordered sequence is part of execution attribution and therefore contributes to `D_R`.

Evaluation policy has three states from `ADR-0079`: valid signed evidence, absence declared in the
frozen composition before execution, or forged/broken evidence. `evaluation: none` MUST derive
`unattributable_for_promotion = true` and a null verdict; it MUST NOT be selected after observing the
outcome. An unsigned, self-produced, wrongly bound, or fabricated verdict is forged/broken and MUST
fail closed. It MUST NOT degrade into declared absence or operational success.

**Trajectory record (emitted at every `EpisodeCompleted`, no transformation step):**

```json
{
  "schema": "mhf.trajectory/1",
  "harness_digest": "...", "manifest_genome": {"...": "..."},
  "model_routes_used": [...],
  "turns": [{"context_digest": "...", "proposal": {...},
             "invocations": [...], "receipts": [...], "cost": {...}}],
  "verdict": {"signed": "...", "oracle": "coding-oracle@3", "pass": true},
  "attribution": {"prefix_hits": 0.91, "escalations": 1}
}
```

**DPO harvest pipeline (deferred blueprint, not foundation):** pair trajectories on identical `(task_digest,
harness_digest, turn-prefix context_digest)` with divergent verdicts → (chosen, rejected) pairs at the
*turn* granularity (the prefix-attribution telemetry already computes the divergence point); filter by
verdict signature validity + anti-cheat lint (existing `test_anticheat.py` semantics); emit JSONL
conforming to standard DPO trainer schemas, plus an SFT split from verdict-pass trajectories. Because
exterior signatures make verdict substitution and subject rebinding tamper-evident under the stated
key-separation threat model. They do **not** prevent evaluator exploitation, benchmark leakage,
selection bias, Goodhart effects, or distribution shift; held-out and adversarial measurement gates
remain mandatory. Continuous loop: production telemetry → harvest → fine-tune open-weight
tier-1/2 models → cassette-replay regression in the lab → promotion pointer. This converts the existing
tier-escalation cost curve into a self-lowering one. (VG-07 §4 "distillation & promotion" is this
section's rationale, merged per matrix §1.10.)

---

## 8. Migration Plan & CI Gates (v0.6.2; accepted ADRs `0069`–`0088`)

**Direction (inverted from v0.5.0).** The mature `vanguard/packages/` semantics remain canonical
(kernel, JCS, WAL ledger, exterior evaluator, sandbox, stores, models, episode engine). Required SPI,
JSON-RPC/UDS, lifecycle, and compose behavior from the former fork is absorbed here. Do **not**
create a compatibility runtime, a third runtime, or a TCB rewrite.

The living execution sequence is [`sprint_active.md`](../03_execution/sprint_active.md); macro gates are
in [`milestones.md`](../03_execution/milestones.md). The gap register allocates falsifier identifiers but
does not authorize work.

| Milestone | Content | Gate (proof command) |
|---|---|---|
| **M-2 / v0.6.1** | Truthful per-turn trajectories and fresh-process SQLite-WAL continuation | RF-23 and RF-25 green; retained convergence gates green |
| **M-3 / v0.6.2** | Named graph/lifecycle contracts and atomic `layer0/` deletion | retained RF-28–RF-45 evidence; operational closure reopened |
| **M-3C / v0.6.2** | One canonical composition/activation path, two domain probes, durable/source-derived evidence preparation | RF-78–RF-84 and G0–G4 |
| **M-4 / v0.7.0** | One useful real coding-agent run with durable replay | RF-95; live model, mediated observe/edit/verify, diff, WAL, trajectory, fresh-process reconstruction |
| **M-5 / v0.7.0** | Formal Pack #2 and exact T0 witness memo | RF-86 and RF-52–RF-53; unchanged substrate; trajectory/evidence parity |
| **M-6 / v0.8.0** | Generic-dispatch capability-mediated spawn | RF-55–RF-59; attenuated lineage/budget/recovery |
| **M-7–M-8** | Measured concurrency then declarative topology support | RF-46–RF-48 and RF-65–RF-66; sequential until governance lift |
| **M-9+** | Exterior post-v1 research | no implementation authority from this law |

**Standing CI gates for the code programme (Wave 0+, `ADR-0073`, `ADR-0074`):** production
kernel/runtime/agency/adapters suites as subject of record; `replay-parity` against disk (not
same-list fold); negative tests for forged verdict, empty ceiling, writer forgery, spawn widening;
`generate_types.py --check`; duplication detector; `check_boundaries`; secret scan; JCS vectors.
Lexical `E-COV` MAY remain as a weak structural lint; it MUST NOT be treated as I-2.

**Current gate:** M-3C and W-3D are closed. M-4 is the active RF-95 product proof; M-5 remains closed
until RF-95 is satisfied. RF-85 continues independently as optional hermetic assurance.

### 8.1 As-built OPTIMIZATIONs this specification amends the old text to match (cite each)

These are cases where the shipped code is *better* than the spec it deviated from — the spec is amended,
the code is kept:

- **Sink-class mediation** (all effects recorded, only `PRIVILEGED` capability-mediated) — `ADR-0051`/D-04,
  ratified here as **ADR-M0-11**.
- **Evaluator outside the worker** (K-40 inverted) — D-32, ratified as **ADR-M0-08**.
- **Alarm set `{F-21a, F-24}`** (not `F-24` alone) — D-18, ratified as **ADR-M0-09**.
- **Inbox/outbox** as a second sequence store for idempotent commands — `ADR-0062`/D-17, kept.
- **Schema-driven translator** (`ProposalTranslator` + `aliases.json`) as the model-to-kernel waist —
  D-28, kept and specified as such in §2.2.
- **`REQ-*`** as the PR-visible requirement namespace, not `TK-*` — `ADR-0045`/D-45, kept.
- **Measurement apparatus stays outside `vanguard/packages/`** — `tools/telemetry/` and `lab/` remain
  siblings to the kernel tree, never imported by it — D-40, kept (also the "HONOUR TABLE" standing
  refusal `TSK-CORE-010` in `docs/03_execution/milestones.md`).
- **`MetaLoopEngine` stays deleted** — the outer loop is a plugin at a scheduler slot (§5.1), never an
  engine — `ADR-0041`/D-41 + **ADR-M0-12**, also `TSK-CORE-011`.

### 8.2 Current foundation gap

The Trust Spine, truthful trajectory, and cold continuation gates are retained green. M-3C closed the
operational split between legacy public composition and the named graph/registry side path and made
durable product and assurance evidence derivable. Current status is recorded only on the active board.

### 8.3 Honour table (SPEC §9, do not reopen)

See §9 below — restated once, not duplicated.

---

## 9. What This Specification Refuses To Build

Consistent with the audited codebase's own honoured deferrals (merged from the charter's §3 non-claims
and VG-10's `DEF-*`/`REJ-*` registers, now `docs/02_decisions/DEFERRED_REJECTED.md`):

- **No self-updating release pipeline** (`SA-1`…`SA-6` stay out — `docs/01_law/DISPATCH.md` §7, amended by
  **ADR-M0-10**'s companion, D-34).
- **No competence-graph pretence** before the memory plugin ships (D-39; `docs/02_decisions/DEFERRED_REJECTED.md`
  `DEF-02`).
- **No parallel fan-out** before independence-group events can be emitted and measured (D-38, Invariant
  I-11).
- **No second wire contract for clients** — generated readers only (`ADR-0063`, AP-6).
- **No metaphysical taxonomy as system architecture** — biological, cosmological, or tier-of-being
  framing is forbidden in living law, decisions, execution, architecture, contracts, protocols,
  engineering, and theory (**ADR-M0-10**, `REJ-10`). Frozen provenance under `_archive/` and
  `09_diagrams/` may preserve rejected historical language, but it never authorizes implementation.
- **No playbook runtime**, ever — advisory (skill cards, §5.4) and guided (planner policy) rungs are the
  ceiling; `strict` deterministic DAG execution reintroduces the workflow-engine anti-pattern §1.1
  exists to prevent (`REJ-01`, `N-20`).
- **MCP is configuration and an adapter, never authority** — it may discover and name tools; it must not
  issue grants, widen scope, bypass `Kernel.dispatch`, or sit on the evaluator plane (`ADR-0066`).
- **GUI/TUI as a backend gate** — clients live elsewhere; the daemon keeps emitting the generated client
  contract (A-4), but no backend milestone gates on a client shipping.
- **Scalar reward for promotion** — promotion stays a partial order over a frontier (`ADR-0015`, `REJ-11`).
- **An always-on full-content training capture** — capture is by policy; the corpus is separately opt-in
  (`REJ-12`).
- **No third runtime tree** — no `core/`, no `aether-rust/`, no `vanguard/substrate/` destination
  (`ADR-0069`).
- **No swarm engine, workflow DAG engine, or graph database** — policy and projections only
  (`ADR-0070`).
- **No byte-identical concurrent ledger as a general requirement** (`ADR-0071`).
- **No mid-run FrozenHarness hot-swap** (`ADR-0005`, `ADR-0072`).
- **No evaluator as a product plugin** (`ADR-0004`, `ADR-0072`).
- **No Rust TCB rewrite, WASM-default isolation, or multi-host distribution in v0.6** (`ADR-0073`).
- **No Meta-Harness / self-updating release pipeline implementation in v0.6** (`ADR-0073`).
- **No Skill / Task / Orchestrator-as-engine / Experiment / Promotion as substrate primitives**
  (`ADR-0074`).

Every future capability enters through a plugin manifest, a new event kind with a legal writer and an
emitter, and a paired measurement (`docs/01_law/MEASUREMENT.md`) — or it does not enter.

---

## Invariants I-1 … I-11

I-1 through I-10 are carried from the archived Tech Lead audit `CRITICAL_GAP_ANALYSIS_AND_AUDIT.md` §6
(git history, `4f9f8b1`)
("Ten Non-Negotiable Invariants for v-next"), **amended** by this Concept Lock (`ADR-0074`):

1. **One `EffectRequest`.** A single frozen dataclass, generated from one JSON Schema, used at S0, on
   the wire, and in adapters.
2. **Emitted = declared, and forged is not accepted.** A declared kind without a production emitter
   fails the build. Lexical string coverage is not this invariant. A synthetic
   `VerdictRecorded {verdict: "pass"}` MUST fail the behavioural gate (`ADR-0074`).
3. **A control merges with its call site** (activation-bundle rule enforced, not aspirational).
4. **State = fold(events), proven** by a **cold** replay from durable storage that reconstructs
   grants, budgets, approvals, and episode lifecycle and diffs against live state. Same-list fold is
   not this invariant. `ColdReplayParity` is the standing CI gate (`ADR-0071`); RF-25 strengthens it
   from reconstruction parity to legal continuation in a fresh interpreter.
5. **The judge stays exterior** — separate identity, signed verdicts, unreachable from agent and from
   plugins.
6. **Plugins are untrusted by default.** Isolation tier declared in the plugin manifest; in-process
   execution is a privilege granted by policy, not the default.
7. **The core is domain-blind.** `coding|ast|pytest` MUST NOT appear under `layer0/` or
   `vanguard/packages/{domain,kernel}/`. Domain packs live in `packs/` and `apps/` as clients.
8. **Specs are generated or normative — never both.** The normative specification is the compact
   `SPEC.md` index plus the six `class: law`, `authority: normative` leaves in `01_law/`; schema
   references are generated. Drift between them is a CI failure, not a register.
9. **Telemetry is a dataset.** Every episode terminates in a schema-valid `mhf.trajectory/1` record
   that is, without transformation, a valid harvest row. For every invoked turn the row MUST carry
   an ordered sequence of all invocations (including retries and escalations), attributable
   provider/model identity, fingerprint or an explicit unavailable reason, explicit measurement
   status, conserved invocation, turn, and episode cost, and distinct recomputable `D_H`, `D_R`,
   and (when evaluated as an experiment) `D_X` subjects. A recovered episode MUST join its verified
   pre-crash prefix with post-recovery turns exactly once. Unknown cost MUST NOT be encoded as zero;
   incomplete historical rows remain readable but are derived ineligible for learning or promotion
   (`ADR-0078`). A digest over `{ids, n}` is not this invariant (`ADR-0074`). DPO training itself is
   deferred.
10. **Metaphors ship as comments, not architecture.**

**I-11 (v0.6 Concept Lock).** The scheduler is sequential; concurrency is a later scheduler property
with a measurement gate (honours D-38). Unknown selector footprint means conflict, not independence.

---

*This detailed law body is retained as the complete source; the compact index and thematic law leaves
provide progressive navigation rather than competing authority. Generated schema reference belongs
beside its owning contract or under `schemas/`, not duplicated in this file.*
