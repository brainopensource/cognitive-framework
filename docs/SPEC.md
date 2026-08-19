# SPEC — Vanguard Meta-Harness Framework (MHF v1)

**Status:** Normative. The **only** living normative specification of Vanguard/GTS. RFC-2119 language
(MUST/SHALL/SHOULD) is binding here and in `docs/04_annex/*` only — nowhere else in `docs/`.
**Version anchor:** v0.5.0 Foundation Lock (concept lock), `docs/MASTER_REFACTOR_GUIDELINE_FINAL.md`.
**Supersedes:** `SYSTEM_SPEC_THEORY.md`, `SYSTEM_SPEC_ASBUILT.md`, README's old biological/tier taxonomy,
`docs/01_specs/backend/**` (archived, evidence not law, at `docs/archive/v045/`).
**Consumes:** `docs/TECH_LEAD_REVIEW/CRITICAL_GAP_ANALYSIS_AND_AUDIT.md` (Kill/Keep/Refactor register,
invariants I-1…I-10), `docs/TECH_LEAD_REVIEW/NEXT_GEN_META_HARNESS_SPECIFICATION.md` (MHF v1 blueprint,
the direct ancestor of this document), `docs/TECH_LEAD_REVIEW/01_SPECS_MIGRATION_MATRIX.md` (per-file
merge disposition).
**Design lineage preserved:** S0–S12 dispatch kernel, JCS canonicalisation + golden vectors, exterior
signed evaluator, harness-as-data manifests, measurement lab.
**Authority on conflict:** this document, then `docs/05_adr/` (a newer ADR wins by citation, never by
silent edit), then `docs/02_roadmap/milestones.md` (cannot contradict this document), then
`docs/03_sprints/sprint_active.md` (execution board only), then `docs/archive/v045/` (evidence, not law
— no ticket may cite it as a requirement).

---

## Preamble

**Vanguard is a meta-harness compiler.** Declarative manifests plus versioned plugins compile into
specialised coding-agent harnesses. The attenuation kernel, the exterior judge, and the measurement lab
are the moat. Self-improvement and meta-cognition are Phase-2 plugins, not Layer-0 features.

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
evaluation requests, spawns — all ledger events. Replay is a CI-enforced property (Invariant I-4), not
a slogan.

**A-4. One schema, many languages.** JSON Schema + JCS + golden vectors are the sole source of truth.
Python dataclasses and TS readers are *generated*. Hand-written mirrors are banned (closes AP-6 — Python
is the runtime language; TypeScript clients consume generated readers only, no hand-written TS domain
logic, per `ADR-0063`).

**A-5. Harness = f(manifest, plugins).** A harness is compiled at composition time from a declarative
manifest resolving plugin references; the compile output (`FrozenHarness`) is content-addressed. Two
identical manifests + plugin digests ⇒ byte-identical harness digest ⇒ attributable A/B measurement (the
separability thesis, kept, operationalised).

**A-6. Asymmetric evolution.** Phase 2 and 3 capabilities land as new plugins and new event kinds —
never as Layer-0 modifications. Layer 0 exposes *extension points*, not features.

---

## 1. Layer 0 — The Microkernel

```text
layer0/
├── events/        # Event taxonomy, JCS envelope, hash chain, reducers   (from domain/ledger, domain/canonicalisation)
├── kernel/        # S0–S12 dispatch, attenuation, grants, budget, policy (KEEP verbatim, +provenance wiring)
├── registry/      # Plugin manifest schema, resolver, lifecycle FSM, isolation broker   (NEW)
├── scheduler/     # Turn scheduler, independence groups, cancellation, heartbeats       (NEW)
├── spi/           # Frozen SPI protocols + generated types                              (replaces ports/)
└── compose/       # Composition: manifest → FrozenHarness (content-addressed)           (from runtime/root, rewritten)
```

Boundary lattice (CI-enforced, closed roster): `events ← kernel ← spi ← registry ← scheduler ← compose`;
plugins import `spi` + `events` only; Layer 0 never imports a plugin. This is `layer0/`'s *target*
lattice for M1+; the **current, as-built lattice is seven packages** — `domain, ports, kernel, agency,
runtime, adapters, apps` (`apps/` was added alongside the original six per `S060-A-10`, registered in
`tools/check_boundaries.py` with the same reach as `runtime`). Any description of "the hexagon" in this
document or `docs/04_annex/` reflects the current seven-package lattice, not the original six-package
diagram — `layer0/` above is the M1 destination, not the current tree.

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

**I-11 (new, Foundation Lock).** Phase-1 scheduler is **sequential**. Concurrency (independence groups,
§1.4) is a later scheduler property, gated on a measurement, never a v0.5.0 feature (honours drift D-38:
"do not add fan-out in v0.5.0 until CC-6 can emit"). This is Invariant I-11, added at the concept lock
alongside I-1…I-10 below.

### 1.2 Event taxonomy (emission is mandatory)

Full kind set, grouped; every kind lists its single production emitter. CI rule `E-COV`: declared kinds
without a reachable emitter fail the build (fixes 11/39 emission, D-11…D-15).

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

Envelope: JCS-canonical JSON, SHA-256 content digest, `prev_digest` hash chain per run, monotonic `seq`,
`causation_id`/`correlation_id`, idempotency key on all command-derived events, and a `branch_id` field
(M1: makes fold-to-seq-N + divergent branch resume a first-class envelope property, not a convention).
Store: SQLite WAL + `FULL` sync (keep, D-16) with JSONL export; blob writes are `write→fsync→emit(digest)`
ordered, closing D-19 (event never references an undurable blob).

### 1.3 Determinism & replay contract

`ClockPort`, `RandomPort`, and model cassettes remain injected; replay mode substitutes recorded values
keyed by `(run_id, seq)`. **CI job `replay-parity`:** execute a live fixture run, fold its ledger cold,
structurally diff reconstructed vs live terminal state — grants tree, budget vector, approval log,
episode FSM included. Time-travel debugging = fold to `seq=N` + resume with a divergent `branch_id`.
Crash recovery = scan for `EffectStarted` without terminal effect event ⇒ mark *undeterminable* ⇒ run
`EffectReconciled` probe (existing semantics, kept).

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
if the manifest names one). Hot-swap = activate new version → route new turns → quiesce old → retire; the
ledger records the exact turn at which routing flipped, preserving attribution. **A trivial echo-plugin
MUST traverse this full lifecycle before any real plugin is written (ADR-M0-13, the walking-skeleton
rule).**

**Isolation tiers (A-2):**

| Tier | Mechanism | Latency | Use |
|---|---|---|---|
| `in_process` | Same interpreter; static import lint + audit hook | ~0 | First-party, signed, reviewed (context compiler) |
| `subprocess` | Fork per plugin; JSON-RPC over UDS; enforced rlimits + seccomp profile (closes D-31) | ~1–5 ms/call | Default for toolkits, planners |
| `container` | Rootless bubblewrap/OCI, UID-separated (existing worker pattern) | ~10–50 ms cold | Anything executing user/model-authored code |
| `wasm` | wasmtime component w/ WASI-preview2 caps | ~0.1–1 ms/call | Untrusted third-party pure-compute plugins |

The evaluator remains its own identity (UID 10002 daemon) — it is *not* a plugin an agent-side manifest
can replace; `IEvaluationGate` plugins run agent-side and merely *request* judgment; verdict signing keys
never enter any plugin cell. See `docs/04_annex/KERNEL.md` §6 (`K-40`, amended by **ADR-M0-08**).

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

`compose()` resolves plugin refs, verifies capability ceilings (plugin ceiling ∩ harness grant set),
freezes L1–L3, and emits a `FrozenHarness` whose digest = JCS(manifest + resolved plugin digests). The
existing `vg-code-claude-shaped` / `vg-code-opencode-shaped` packs port mechanically — this is the
Meta-Harness compiler: *specialised harnesses (Claude-Code-shaped, OpenHands-shaped, SWE-mini-shaped)
are compiled artifacts of one engine.* Registries freeze at composition; unknown names fail at
composition, not runtime (handbook M5.3 "operators-as-data + registries freeze at composition" — merged
here; "operator" vocabulary is retired in favour of plugin refs, per matrix §1.6).

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

## 4. Phase 1 — Coding Domain Pack (immediate)

Everything below is plugins + one domain pack; Layer-0 diff = zero (Invariant I-7: `grep -rE
"coding|pytest|ast" layer0/` MUST return nothing).

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

**Phase-1 acceptance gate:** the compiled `code-default` harness passes the existing `lab/` dogfood
triple + `zero_hint_v1` at ≥ the v0.4.5 baseline pass rate under paired McNemar (`docs/04_annex/MEASUREMENT.md`),
with `replay-parity` green and E-COV = 100%.

---

## 5. Evolution Blueprint — Phase 2 (autonomous & meta-cognitive)

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
the pack. **Acceptance: adding Pack #N requires zero diffs under `layer0/` (Invariant I-7, CI-greppable)**
— this is the handbook's M11 "Generality Falsification Invariant," merged here per matrix §1.4.

---

## 7. Telemetry, Self-Tuning & Model Distillation

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

## 8. Migration Plan & CI Gates (from `b79093c`, the Foundation Lock commit)

| Milestone | Content | Gate (proof command) |
|---|---|---|
| **M0 — Excise & Sanitize** (docs done in this wave; purge deferred) | Docs collapsed per migration matrix (this document); artifact/secret purge and frontend removal are a **separately authorised, staged** plan (`docs/03_sprints/plans/m0-code-and-purge.md`), not part of the Foundation Lock | `G-M0-DOCS`: docs gates below all green; `find docs -name '*.md' \| wc -l` trending down |
| **M1 — Layer 0** (2 sprints) | Port kernel + events + canonicalisation verbatim; implement full event taxonomy + emitters; generate types from schemas (one `EffectRequest`); scheduler v1 (sequential, I-11) | `replay-parity` green; E-COV 100%; mutation score ≥ 80% on kernel+reducers |
| **M2 — Plugin runtime** (2 sprints) | Registry, lifecycle FSM, isolation broker (in_process + subprocess tiers), SPI v1, `compose()` v2 | third-party demo plugin loads/faults/hot-swaps with full ledger trail (ADR-M0-13 walking skeleton β) |
| **M3 — Coding Pack** (2–3 sprints) | Port `apps/coding` (already extracted from `domain/`, see §Deteriorations below) + adapters into plugins; ast-patch, repo-map, terminal toolkits; container tier + seccomp | Phase-1 acceptance gate (§4) |
| **M4 — Harness parity** | Recompile `vg-code-claude-shaped` / `opencode-shaped` / `swe-mini` / `pi-shaped` / TableWorld as manifests | 5 packs, zero Layer-0 diffs |
| **M5 — Phase 2 plugins** | Meta-reflector, genome mutation + lab selection, calibrated escalation, skill harvest; prerequisite: 200-task suite (statistical-power gate) | one promoted mutation beating baseline at p<0.05 (McNemar) |
| **M6 — Distillation loop** | Trajectory schema live; DPO harvest; first fine-tuned tier-1 model behind cassette regression | fine-tuned local model ≥ baseline free-tier pass rate at lower USD/episode |

**Standing CI gates from day M1:** `check_boundaries` (extended to plugin imports), `replay-parity`,
`E-COV`, control-call-site proof (AP-5 rule), secret scan, JCS vector conformance — replacing the
TCB-LOC and test-count badges (see `docs/05_adr/ADR-M0-01-control-coverage-discipline.md`).

**This wave's own gates (M0-docs, run now):** `python3 -m unittest test.test_repo_paths`;
`python3 tools/check_schema_archaeology.py`; `python3 tools/check_stale_paths.py`;
`python3 tools/check_markdown_links.py`; zero RFC-2119 keywords outside `docs/SPEC.md`/`docs/04_annex/`;
`python3 tools/check_boundaries.py`; `python3 tools/check_tcb_budget.py`.

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

### 8.2 As-built DETERIORATIONs M1 must close (verified against the ground-truth table, not claimed)

Re-verified 2026-08-18 per `docs/MASTER_REFACTOR_GUIDELINE_FINAL.md` Step 0 (commands actually run, not
assumed from `[DONE] ✅` tags):

- **Provenance on the production path** (D-05/D-06): `rg "child_return" vanguard/packages/agency
  vanguard/packages/kernel` shows `agency/episode/engine.py` and `kernel/provenance.py` both call it —
  **confirmed landed**, not open. `rg "Trust.OPERATOR"` shows three call sites including `root.py` —
  **confirmed landed**. These port with the kernel as ported facts, not new M1 work.
- **`EpisodeStarted` emission** (D-12): `rg "EpisodeStarted" vanguard/packages/agency
  vanguard/packages/runtime` shows emitters in `runtime/root.py` and `runtime/ledger/projections.py` —
  **confirmed landed**.
- **`ApprovalResolved` ledgered** (D-13): `rg "ApprovalResolved"` shows it in
  `domain/ledger/{reducer,events}.py`, `runtime/governance/{approvals,engine}.py`,
  `runtime/service/service.py`, `runtime/ledger/{recovery,projections}.py` — **confirmed landed**, but
  claimed `[DONE]` status is re-proven under E-COV in M1, not just trusted.
- **E-COV 100%** — still open. `EVENT_KINDS` writer enforcement (D-11) is not yet closed at the writer.
- **One `EffectRequest`** (D-21) — still open; three types remain until M1 codegen.
- **`domain/ledger/coding_session.py` out of `domain/`** (D-42): confirmed — `vanguard/packages/apps/coding/`
  exists with 7 modules including `coding_session.py`; `apps` is registered as a 7th boundary-lattice
  package in `tools/check_boundaries.py` (`PACKAGE_NAMES = {"domain", "ports", "kernel", "agency",
  "runtime", "adapters", "apps"}`). **Do not list D-42 as open** — it is already resolved. M3's "extract
  coding pack" is a **re-extraction** from `apps/coding/` into `packs/`, not a first extraction from
  `domain/`.

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

Every future capability enters through a plugin manifest, a new event kind with an emitter, and a paired
measurement (`docs/04_annex/MEASUREMENT.md`) — or it does not enter.

---

## Invariants I-1 … I-11

I-1 through I-10 are carried from `docs/TECH_LEAD_REVIEW/CRITICAL_GAP_ANALYSIS_AND_AUDIT.md` §6
("Ten Non-Negotiable Invariants for v-next") verbatim:

1. **One `EffectRequest`.** A single frozen dataclass, generated from one JSON Schema, used at S0, on
   the wire, and in adapters.
2. **Emitted = declared.** CI computes event-kind emission coverage against production call sites; a
   declared kind without an emitter fails the build.
3. **A control merges with its call site** (activation-bundle rule enforced, not aspirational).
4. **State = fold(events), proven** by a replay test that reconstructs grants, budgets, approvals, and
   episode lifecycle from the ledger alone and diffs against live state every CI run.
5. **The judge stays exterior** — separate identity, signed verdicts, unreachable from agent and from
   plugins.
6. **Plugins are untrusted by default.** Isolation tier declared in the plugin manifest; in-process
   execution is a privilege granted by policy, not the default.
7. **The core is domain-blind.** `grep -r "coding\|ast\|pytest" layer0/` returns nothing.
8. **Specs are generated or normative — never both.** One normative document (this one); schema
   references generated; drift is a CI failure, not a register.
9. **Telemetry is a dataset.** Every episode terminates in a trajectory record that is, without
   transformation, a valid row in the DPO harvest schema.
10. **Metaphors ship as comments, not architecture.**

**I-11 (added at the Foundation Lock, §1.1 above).** Phase-1 scheduler is sequential; concurrency is a
later scheduler property with a measurement gate (honours D-38).

---

*This specification word count is held near the ≤9k-word target by cross-referencing `docs/04_annex/` and
`docs/05_adr/` rather than restating their content — if a section here starts to restate a schema, that
content belongs in `docs/reference/` (generated, M1+) instead, not in this file.*
