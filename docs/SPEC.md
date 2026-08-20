# SPEC — Vanguard Meta-Harness Framework (MHF v1)

**Status:** Normative. The **only** living normative specification of Vanguard/GTS. RFC-2119 language
(MUST/SHALL/SHOULD) is binding here and in `docs/04_annex/*` only — nowhere else in `docs/`.
**Version anchor:** v0.6.0 Concept Lock (`docs/05_adr/0069`–`0074`). The as-built Python package
version remains `0.4.5b1` in `pyproject.toml` until a later release cut.
**Supersedes:** v0.5.0 Foundation Lock destination story (`layer0/` as M1 rewrite target) and
mid-run plugin hot-swap as a v0.6 feature; `SYSTEM_SPEC_THEORY.md`, `SYSTEM_SPEC_ASBUILT.md`,
README's old biological/tier taxonomy, `docs/01_specs/backend/**` (archived, evidence not law, at
`docs/archive/v045/`).
**Consumes:** `docs/TECH_LEAD_REVIEW/CRITICAL_GAP_ANALYSIS_AND_AUDIT.md` (Kill/Keep/Refactor register,
invariants I-1…I-10), `docs/TECH_LEAD_REVIEW/NEXT_GEN_META_HARNESS_SPECIFICATION.md` (MHF v1 blueprint,
the direct ancestor of this document), `docs/TECH_LEAD_REVIEW/01_SPECS_MIGRATION_MATRIX.md` (per-file
merge disposition). Forensic report
`docs/07_reviews/VANGUARD_V060_FORENSIC_DISCOVERY.md` is investigation, not law.
**Design lineage preserved:** S0–S12 dispatch kernel, JCS canonicalisation + golden vectors, exterior
signed evaluator, harness-as-data manifests, measurement lab, SQLite WAL ledger.
**Authority on conflict:** this document, then `docs/05_adr/` (a newer ADR wins by citation, never by
silent edit — **`0069`–`0074` outrank the v0.5.0 M1-destination paragraph they reverse**), then
`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/001_V060_concept_phase_GAMMA.md` (lock plan, not a
second SPEC), then `docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`
(post-lock engineering register; cannot contradict this document), then
`docs/02_roadmap/milestones.md` (historical; cannot contradict this document; rewrite is a later phase),
then `docs/03_sprints/sprint_active.md` (execution board only), then `docs/archive/v045/` and
`docs/07_reviews/` (evidence and proposals, not law — no ticket may cite them as a requirement).

---

## Preamble

**Vanguard is a recursive agency substrate that compiles harnesses.** The first *domain pack* is
coding; coding is not the architecture. One execution machine
(`Agent = Principal + HarnessInstance`, `ADR-0070`) runs every agent, subagent, and (later) swarm
participant. Declarative manifests plus versioned plugins compile into specialised harnesses. The
attenuation kernel, the exterior judge, and the measurement lab are the moat. Self-improvement and
meta-cognition are Phase-2 plugins, not Layer-0 features, and they are **not implemented in v0.6**
(`ADR-0073`).

**What solved it must be separable, and the judge must be unreachable from the judged** (the
separability thesis, carried from `docs/01_specs/backend/02_vanguard_charter_claims_and_non_claims_v040.md`
§1, now archived — this sentence is the project's one-sentence identity and it stays). A harness that
passes a benchmark is worthless as evidence unless the mechanism that produced the pass is separable
from the mechanism that graded it, and the grader cannot be read, patched, or reasoned about by the
thing it grades.

**Non-claims** (merged line-by-line from the charter's §3, now folded into §9 below rather than kept as
a separate document): this specification does not claim continuous learning, does not claim the system
improves itself without human promotion of the release pipeline it explicitly refuses to build, does not
claim a competence graph exists, does not claim GUI/TUI parity is a backend requirement, and does not
claim any biological, cosmological, or "cognitive operating system" framing has operational meaning.
Every non-claim below in §9 is a promise about what will *not* be asserted, not a roadmap gap.

---

## 0. Design Axioms

**A-1. Microkernel, literally.** Layer 0 provides exactly four things: the event-sourced state machine,
the effect-dispatch kernel, the plugin registry + lifecycle, and the scheduler. Everything else —
planning, memory, tools, context, evaluation, models, sandboxes, domains — is a plugin behind a
versioned SPI. Layer-0 LOC target: ≤ 4,500 (kernel 1,700 is already written). *(Handbook M9 "minimise
what must be simultaneously correct" — merged here as this axiom's rationale, per matrix §1.4.)*

**A-2. The kernel governs effects; the loader governs plugins.** Two independent authority systems:
capability grants constrain what the *agent* may do (existing kernel); isolation tiers constrain what
*plugin code* may do (new). Neither trusts the other's subjects. *(Handbook M3 "the broker grants; the
sandbox contains" is this axiom's ancestor.)*

**A-3. Everything is an event or it didn't happen.** Grants, budgets, approvals, plugin activation,
evaluation requests, spawns — all ledger events. Replay is a *required* CI-enforced property
(Invariant I-4, `ADR-0071`, `ADR-0074`), not a slogan. Folding the same in-memory list twice is not
I-4. The production `replay-parity` job is not currently wired.

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

**A-6. Asymmetric evolution.** Phase 2 and 3 capabilities land as new plugins and new event kinds —
never as Layer-0 modifications. Layer 0 exposes *extension points*, not features.

---

## 1. Layer 0 — The Microkernel

Layer 0 is a *concern set*, not a mandate to rewrite the runtime into a second tree.

**Production lattice (as-built and canonical, `ADR-0069`).** `vanguard/packages/`:

```text
domain → ports → kernel → agency → runtime → adapters
         (apps/ is a client of runtime, not a second ontology)
```

Composition root remains `vanguard/packages/runtime/root.py`. This lattice is the **CI subject of
record** (`ADR-0073`): living CI MUST eventually run the packages kernel/runtime/agency/adapters
suites. A green `test/layer0` suite alone does not satisfy I-2 or I-4.

**Convergence fork (not the destination).** `layer0/` is a copy-fork that holds SPI protocols,
JSON-RPC/UDS codec, plugin-cell broker, lifecycle FSM, and a sequential driver. Useful contracts
are absorbed into the production lattice. Duplicate kernels, schedulers, mocks, and synthetic
verdict paths MUST NOT be deleted until a behavioral parity gate. A third tree (`core/`,
`aether-rust/`) is forbidden.

```text
layer0/          # fork under convergence — contracts to absorb, not a destination rewrite
├── events/      # taxonomy / envelope / fold — converge with domain/ledger
├── kernel/      # diverging S0–S12 port — packages kernel remains the semantic oracle
├── registry/    # lifecycle FSM + isolation broker — promote
├── scheduler/   # sequential driver; MUST NOT fabricate VerdictRecorded (defect F1)
├── spi/         # Protocols + jsonrpc + generated types — promote; Protocol is a client
└── compose/     # Manifest → FrozenHarness digest — converge with domain compose
```

Boundary lattice (CI-enforced, closed roster) for the production hexagon:
`domain ← ports ← kernel ← agency ← runtime → adapters`; adapters MUST NOT import `kernel` or
`agency`. Plugins import SPI + events only; Layer 0 never imports a plugin. The `layer0/` internal
order `events ← kernel ← spi ← registry ← scheduler ← compose` is the fork's own checker rows, not
a replacement identity.

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
the REJ on playbook runtimes, `docs/05_adr/DEFERRED_REJECTED.md` `REJ-01`. VG-03 §2's loop-over-DAG
inversion — "strictly less expressive than a loop that can invoke a loop, at roughly ten times the
machinery, proof by construction" — is the argument for this shape and is carried here by citation
rather than restated; see also `docs/05_adr/DEFERRED_REJECTED.md` `REJ-01`.)*

**I-11 (v0.6).** The scheduler is **sequential**. Concurrency (independence groups, §1.4) is a later
scheduler property, gated on a measurement. Unknown selector footprint means conflict, not
independence (`ADR-0073`, `ADR-0074`). This is Invariant I-11.

### 1.2 Event taxonomy (emission is mandatory)

Full kind set, grouped; every kind lists its single production *owner*. Lexical CI rule `E-COV`
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
| Plugins | `PluginResolved`, `PluginActivated`, `PluginQuiesced`, `PluginRetired`, `PluginFaulted` | registry |
| Health | `Heartbeat` (HMAC-authenticated, fixes D-14), `CheckpointCreated` | scheduler |
| Delegation | `ChildSpawned`, `ChildReturned` (carries provenance spans, fixes D-06) | scheduler |

Envelope: JCS-canonical JSON, SHA-256 content digest, `prev_digest` hash chain per **Project**
(`project_id`), monotonic `seq` within that unit, `causation_id`/`correlation_id`, idempotency key on
all command-derived events, `branch_id`, and the lineage fields of §1.0. Store: SQLite WAL + `FULL`
sync (keep, D-16) with JSONL export; blob writes are `write→fsync→emit(digest)` ordered, closing D-19
(event never references an undurable blob).

### 1.3 Determinism & replay contract

`ClockPort`, `RandomPort`, and model cassettes remain injected; replay mode substitutes recorded values
keyed by `(run_id, seq)`. **Replay taxonomy (`ADR-0071`) — these MUST NOT be conflated:** state replay
(deterministic reconstruction of grants, budgets, approvals, episode FSM); schedule replay (needs
recorded nondeterminism); real-world re-execution (not required to match); byte-identical fixtures
(only fully controlled inputs). Concurrent executions are not required to produce byte-identical
ledgers. Consistency unit is `project_id`.

**CI job `replay-parity` (requirement; not currently wired in `.github/workflows/ci.yml`):** execute a
live fixture run against the **production** ledger, fold its ledger cold, structurally diff
reconstructed vs live terminal state — grants tree, budget vector, approval log, episode FSM included.
Folding the same in-memory list twice is not this job. Time-travel debugging = fold to `seq=N` + resume
with a divergent `branch_id`. Crash recovery = scan for `EffectStarted` without terminal effect event
⇒ mark *undeterminable* ⇒ run `EffectReconciled` probe (existing semantics, kept).

### 1.4 Scheduler

Replaces the sequential `EpisodeEngine` outer shell (engine's dispatch discipline is preserved inside).
Adds: independence groups (proposals declare read/write resource selectors; non-intersecting selectors
*may* run concurrently once I-11's gate is met — this unlocks D-38 without touching the kernel, but does
not enable it in v0.5.0), cooperative cancellation tokens, turn/depth ceilings as first-class
`Reservation` dimensions (resolves D-09/D-24 per **ADR-M0-07**: the budget vector becomes six-dimensional,
`{usd_micros, millis, tokens, bytes, turns, depth}`, allowed only because the scheduler is the named
consumer), and heartbeat emission.

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
`ADR-0059`, `ADR-0072`). Python `typing.Protocol` is a client convenience. `in_process` is an
isolation privilege that still speaks the same wire (loopback), not a second SPI.

**Isolation tiers (A-2):**

| Tier | Mechanism | Latency | Use |
|---|---|---|---|
| `in_process` | Same interpreter; static import lint + audit hook | ~0 | First-party, signed, reviewed (context compiler) |
| `subprocess` | Fork per plugin; JSON-RPC over UDS; enforced rlimits + seccomp profile (closes D-31) | ~1–5 ms/call | Default for toolkits, planners |
| `container` | Rootless bubblewrap/OCI, UID-separated (existing worker pattern) | ~10–50 ms cold | Anything executing user/model-authored code |
| `wasm` | wasmtime component w/ WASI-preview2 caps | ~0.1–1 ms/call | Untrusted third-party pure-compute plugins |

The evaluator remains its own identity (UID 10002 daemon) — it is *not* a plugin an agent-side manifest
can replace; `IEvaluationGate` plugins run agent-side and merely *request* judgment; verdict signing keys
never enter any plugin cell. The scheduler MUST **read** a signed verdict; emitting
`VerdictRecorded {verdict: "pass"}` without a signature is defect F1, not a plugin strategy
(`ADR-0072`). See `docs/04_annex/KERNEL.md` §6 (`K-40`, amended by **ADR-M0-08**).

### 2.2 SPI definitions (Layer-0 `spi/` package — typed, frozen, versioned)

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
    reservation: Reservation  # {usd_micros, millis, tokens, bytes, turns, depth}

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
a PR** — see `docs/05_adr/ADR-M0-03-five-spis.md`.

### 2.3 Harness manifest (the compile target)

```yaml
# harness.yaml — mhf.harness/1 (successor of vg-code-* packs)
api: mhf.harness/1
id: code-default
plugins:
  planner:  {ref: mhf.planner.drive-until-green@^1, config: {max_repair_rounds: 4}}
  context:  {ref: mhf.context.repo-map@^1}
  memory:   {ref: mhf.memory.sqlite-kv@^1}
  toolkits: [{ref: mhf.toolkit.fs@^1}, {ref: mhf.toolkit.ast-patch@^2},
             {ref: mhf.toolkit.terminal@^1}, {ref: mhf.toolkit.index@^1}]
  evaluation: {ref: mhf.eval.oracle-gate@^1, config: {oracle: coding-oracle@3}}
  model_routes:
    - {tier: 1, provider: ollama, model: qwen2.5:1.5b}
    - {tier: 3, provider: openrouter, model: "$FRONTIER", escalate_on: [verdict_fail, budget_ok]}
system_prompt: ./system-prompt.txt          # L1, byte-stable
capabilities: [...]                          # grant ceiling (schema unchanged from v4)
budget: {usd_micros: 250000, turns: 40, depth: 2}
approval_policy: ./approval-policy.json
undeletable: false
```

`compose()` resolves plugin refs, verifies capability ceilings (plugin ceiling ∩ harness grant set;
**fail-closed**, empty ceilings authorize nothing, intersection stored on `FrozenHarness` —
`ADR-0072`), freezes L1–L3, and emits a `FrozenHarness` whose digest `D_H` = JCS of the **full**
behavior-affecting composition: resolved plugin refs and digests, system prompt, capability ceiling,
approval policy, model routes (`ADR-0074`). The existing `vg-code-claude-shaped` /
`vg-code-opencode-shaped` packs port mechanically — specialised harnesses are compiled artifacts of
one engine. Registries freeze at composition; unknown names fail at composition, not runtime.
Mid-run composition change is forbidden in v0.6 (`ADR-0005`, `ADR-0072`).

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

**Crash recovery.** On boot: fold ledger → find open runs → verify heartbeat staleness (HMAC) →
reconcile undeterminable effects → emit `RunRecovered` and resume at the exact turn, or `RunAborted` with
cause. Zero-data-loss claim now holds because §1.2 makes every state-bearing fact an event.

---

## 4. Coding Domain Pack (first domain; foundation E2E, not this lock wave)

**v0.6 status:** this section is the *shape* of Domain Pack #1. It is not authorized as the next
commit. Foundation coding-agent E2E is Wave 4 of
`docs/07_reviews/PRINCIPAL_STAFF_ENGINEER_REVIEW/002_V060_FOUNDATION_ROADMAP_AND_GAP_REGISTER.md`.

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

---

## 5. Evolution Blueprint — Phase 2 (autonomous & meta-cognitive)

**v0.6 status: deferred blueprint (`ADR-0073`).** Not foundation scope. Trajectory *schema and
emission* are locked now so this phase does not require a corpus migration; promotion, mutation, and
skill harvest are not.

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
thresholds. Selection = paired lab runs (existing McNemar machinery) against the undeletable baseline;
promotion = signed `CanaryPromoted` event flipping the registry's default pointer. Population bookkeeping
lives in `IMemoryEngine`; the lab is the fitness function — no new statistics code required.

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

**6.3 Multi-agent economic delegation.** `spawn()` generalises to contracts: `ChildSpawned` carries a
task brief, a capability attenuation (existing `Scope` machinery), a lease, and an acceptance oracle
preregistered with the exterior evaluator; `ChildReturned` carries receipts + signed verdict +
provenance spans. Heterogeneous swarms = children composed from *different harness manifests*
competing/cooperating under the §6.2 allocator. Delegation depth is a `Reservation` dimension; the judge
remains singular and exterior across the whole swarm — one economy, one court.

**6.4 Domain-agnostic decomposition.** A Domain Pack = {toolkit(s) + oracle suite + manifest defaults +
selector vocabulary}. TableWorld (currently orphaned, D-27) becomes Pack #2 as the generality witness; a
`math` or `data-analysis` pack is Pack #3. The decomposition planner (`mhf.planner.decompose`) is
domain-blind: it operates on verbs, selectors, oracles, and cost vectors — the domain lives entirely in
the pack. **Acceptance: adding Pack #N requires zero diffs under `layer0/` and under
`vanguard/packages/{domain,kernel}/` (Invariant I-7).**
— this is the handbook's M11 "Generality Falsification Invariant," merged here per matrix §1.4.

---

## 7. Telemetry, Self-Tuning & Model Distillation

**v0.6 foundation locks the trajectory record (I-9, `ADR-0074`).** DPO harvest, fine-tune, and
promotion remain deferred (`ADR-0073`). The schema MUST exist and MUST be emitted at
`EpisodeCompleted`; consumers of the dataset are not this version's kernel.

**Trajectory record (emitted at every `EpisodeCompleted`, no transformation step):**

```json
{
  "schema": "mhf.trajectory/1",
  "harness_digest": "...", "manifest_genome": {"...": "..."},
  "model_routes_used": [...],
  "turns": [{"context_digest": "...", "proposal": {...},
             "receipts": [...], "cost": {...}}],
  "verdict": {"signed": "...", "oracle": "coding-oracle@3", "pass": true},
  "attribution": {"prefix_hits": 0.91, "escalations": 1}
}
```

**DPO harvest pipeline (offline, `lab/`-adjacent):** pair trajectories on identical `(task_digest,
harness_digest, turn-prefix context_digest)` with divergent verdicts → (chosen, rejected) pairs at the
*turn* granularity (the prefix-attribution telemetry already computes the divergence point); filter by
verdict signature validity + anti-cheat lint (existing `test_anticheat.py` semantics); emit JSONL
conforming to standard DPO trainer schemas, plus an SFT split from verdict-pass trajectories. Because
verdicts are exterior-signed, the training signal is un-gameable by construction — the property no
competitor pipeline has. Continuous loop: production telemetry → harvest → fine-tune open-weight
tier-1/2 models → cassette-replay regression in the lab → promotion pointer. This converts the existing
tier-escalation cost curve into a self-lowering one. (VG-07 §4 "distillation & promotion" is this
section's rationale, merged per matrix §1.10.)

---

## 8. Migration Plan & CI Gates (v0.6 Concept Lock; `ADR-0069`, `ADR-0073`)

**Direction (inverted from v0.5.0).** Recover mature `vanguard/packages/` semantics (kernel, JCS, WAL
ledger, exterior evaluator, sandbox, stores, models, episode engine). Promote `layer0/` SPI contracts,
JSON-RPC/UDS broker, lifecycle FSM, and compose digest shape. Do **not** rebuild WAL, evaluator, or
sandbox inside `layer0/`. Do **not** create a third runtime. Do **not** rewrite the TCB in Rust.

The M0–M6 table below remains a *historical* Foundation Lock sketch. It is **not** the next roadmap
(roadmap is a later phase). Where it said "port kernel into `layer0/`", read: **converge onto
packages; absorb layer0 contracts**.

| Milestone | Content | Gate (proof command) |
|---|---|---|
| **M0 — Excise & Sanitize** (docs done in v0.5; v0.6 Concept Lock is this document + ADRs 0069–0074) | Docs collapsed; v0.6 destination reversed; GAMMA amendments | `G-M0-DOCS` plus ADRs 0069–0074 cited |
| **Next code phase — CI subject of record** | Wire living CI to packages kernel/runtime/agency/adapters; negative tests for F1 and ceilings | production suites in CI; forged verdict cannot become accepted `VerdictRecorded` |
| **Convergence** | Absorb SPI/jsonrpc; kill synthetic scheduler verdicts on the canonical path; parity then delete duplicates | behavioral parity, then deletion |
| **Plugin walking skeleton** | Manifest → Resolve → Verify → Freeze → FrozenHarness; echo plugin on the wire | ADR-M0-13 on the packages path |
| **Foundation E2E** | One real coding-agent path: model, authorized effect, filesystem, sandbox, signed eval, WAL, replay, trajectory | see exit gate below; **not** this Concept Lock wave |

**Standing CI gates for the code programme (Wave 0+, `ADR-0073`, `ADR-0074`):** production
kernel/runtime/agency/adapters suites as subject of record; `replay-parity` against disk (not
same-list fold); negative tests for forged verdict, empty ceiling, writer forgery, spawn widening;
`generate_types.py --check`; duplication detector; `check_boundaries`; secret scan; JCS vectors.
Lexical `E-COV` MAY remain as a weak structural lint; it MUST NOT be treated as I-2.

**This lock wave's own gates (docs):** ADRs `0069`–`0074` cited; SPEC does not name `layer0/` as M1
destination; KERNEL annex destination amended; GAMMA + gap register present. Living-CI green is
**not** claimed: `test_repo_paths` / stale `docs/sprint6B` remain a Wave-0 hygiene item.

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
  refusal `TSK-CORE-010` in `docs/02_roadmap/backlog.md`).
- **`MetaLoopEngine` stays deleted** — the outer loop is a plugin at a scheduler slot (§5.1), never an
  engine — `ADR-0041`/D-41 + **ADR-M0-12**, also `TSK-CORE-011`.

### 8.2 As-built DETERIORATIONs the code programme must close

Re-verified 2026-08-18 and again at Concept Lock (2026-08-20). These are **Wave 0–2** work, not a
`layer0/` destination rewrite:

- **Provenance / `EpisodeStarted` / `ApprovalResolved`:** landed on the packages path (keep).
- **Lexical E-COV 100%:** insufficient. Writer enforcement and F1 (unsigned pass) are the real I-2 gap.
- **One `EffectRequest` (D-21 / I-1):** still open; codegen must become the source (`ADR-0074`).
- **D-42 coding_session out of `domain/`:** already in `apps/coding/`; pack re-extraction is Wave 3–4,
  not a first extraction from `domain/`.
- **Fail-open ceilings, tautological replay, kernel-not-in-CI, content-free trajectory:** see
  gap register.

### 8.3 Honour table (SPEC §9, do not reopen)

See §9 below — restated once, not duplicated.

---

## 9. What This Specification Refuses To Build

Consistent with the audited codebase's own honoured deferrals (merged from the charter's §3 non-claims
and VG-10's `DEF-*`/`REJ-*` registers, now `docs/05_adr/DEFERRED_REJECTED.md`):

- **No self-updating release pipeline** (`SA-1`…`SA-6` stay out — `docs/04_annex/KERNEL.md` §7, amended by
  **ADR-M0-10**'s companion, D-34).
- **No competence-graph pretence** before the memory plugin ships (D-39; `docs/05_adr/DEFERRED_REJECTED.md`
  `DEF-02`).
- **No parallel fan-out** before independence-group events can be emitted and measured (D-38, Invariant
  I-11).
- **No second wire contract for clients** — generated readers only (`ADR-0063`, AP-6).
- **No metaphysical taxonomy of any kind** — biological, cosmological, or tier-of-being framing is
  forbidden in any document under `docs/` (**ADR-M0-10**, `REJ-10`).
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
emitter, and a paired measurement (`docs/04_annex/MEASUREMENT.md`) — or it does not enter.

---

## Invariants I-1 … I-11

I-1 through I-10 are carried from `docs/TECH_LEAD_REVIEW/CRITICAL_GAP_ANALYSIS_AND_AUDIT.md` §6
("Ten Non-Negotiable Invariants for v-next") verbatim:

1. **One `EffectRequest`.** A single frozen dataclass, generated from one JSON Schema, used at S0, on
   the wire, and in adapters.
2. **Emitted = declared, and forged is not accepted.** A declared kind without a production emitter
   fails the build. Lexical string coverage is not this invariant. A synthetic
   `VerdictRecorded {verdict: "pass"}` MUST fail the behavioural gate (`ADR-0074`).
3. **A control merges with its call site** (activation-bundle rule enforced, not aspirational).
4. **State = fold(events), proven** by a **cold** replay from durable storage that reconstructs
   grants, budgets, approvals, and episode lifecycle and diffs against live state. Same-list fold is
   not this invariant. The job is required and not currently wired (`ADR-0071`).
5. **The judge stays exterior** — separate identity, signed verdicts, unreachable from agent and from
   plugins.
6. **Plugins are untrusted by default.** Isolation tier declared in the plugin manifest; in-process
   execution is a privilege granted by policy, not the default.
7. **The core is domain-blind.** `coding|ast|pytest` MUST NOT appear under `layer0/` or
   `vanguard/packages/{domain,kernel}/`. Domain packs live in `packs/` and `apps/` as clients.
8. **Specs are generated or normative — never both.** One normative document (this one); schema
   references generated; drift is a CI failure, not a register.
9. **Telemetry is a dataset.** Every episode terminates in a schema-valid `mhf.trajectory/1` record
   that is, without transformation, a valid harvest row. A digest over `{ids, n}` is not this
   invariant (`ADR-0074`). DPO training itself is deferred.
10. **Metaphors ship as comments, not architecture.**

**I-11 (v0.6 Concept Lock).** The scheduler is sequential; concurrency is a later scheduler property
with a measurement gate (honours D-38). Unknown selector footprint means conflict, not independence.

---

*This specification word count is held near the ≤9k-word target by cross-referencing `docs/04_annex/` and
`docs/05_adr/` rather than restating their content — if a section here starts to restate a schema, that
content belongs in `docs/reference/` (generated, M1+) instead, not in this file.*
