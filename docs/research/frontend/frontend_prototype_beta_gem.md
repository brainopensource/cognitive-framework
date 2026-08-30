---
id: research.frontend-prototype-beta-gem
kind: research
status: experiment
authority: non-canonical
summary: "Integrated frontend prototype research, PRD, and engineering roadmap."
topic:
  - frontend
---

# AETHER Observatory — Final Integrated Frontend Prototype, PRD, and Engineering Specification

> **Authority note.** This document is `_archive/brainstorm`. It is *evidence and intent*, never law.
> Nothing here amends [`docs/SPEC.md`](../../SPEC.md).
> Where this document and law disagree, law wins and this document is wrong. Every backend change
> proposed in the final chapter is a *proposal requiring an ADR*, not an authorization.

---

## 0. Executive summary

We have a substrate — a microkernel with a mediated S0–S12 effect pipeline, a durable event ledger,
frozen SPIs, capability grants, packs, manifests, three identity digests (`D_H`/`D_R`/`D_X`), and a
statistical measurement law. What we do not have is a way to **see** it. Today the only windows are
the Ink TUI at [`vanguard/clients/cli/`](../../../vanguard/clients/cli/), a 327-line static
studio page at [`vanguard/packages/runtime/studio/ui/`](../../../vanguard/packages/runtime/studio/ui/),
and `jq` over NDJSON.

That is a real bottleneck, and not a cosmetic one. The substrate's core claims — replay parity,
truthful trajectories, budget conservation, containment fidelity, harness-identity discrimination —
are all claims about **structure over time**. Structure over time is exactly the class of thing that
text scrolls hide and that a well-built visual surface reveals in under a second.

This document specifies **AETHER Observatory**: a local-first, high-performance, event-sourced frontend
that is a *second client of the same contract the CLI already speaks*, not a second runtime. Its
design thesis in one sentence:

> **The frontend is a pure, deterministic fold over the same event stream the ledger stores; every
> pixel it draws must be derivable from events the backend already emits, and any pixel that is not
> is either a backend gap to be filed or a lie to be deleted.**

That single constraint gives us, for free: replayability of the UI itself, offline inspection of any
recorded run, screenshot-stable regression tests, and — most importantly — a UI that *cannot* drift
from the substrate, because drifting would mean rendering something no event supports.

### What the first authorized pilot must do

1. **Watch** a live run: turn loop, invocations, effects, leases, approvals, verdicts, costs.
2. **Inspect** the substrate statically: manifest → composition → activation plan → run plan, the
   plugin roster, the capability grants, the five-SPI boundary, the S0–S12 pipeline.
3. **Author** compositions: build a `mhf.manifest/2` visually, freeze it, see its `D_H` change.
4. **Compare** two harnesses on one task — including *our* coding harness vs. Claude Code CLI on the
   same model — as a paired experiment, with McNemar as the arbiter (`lab/bench.py` already has it).
5. **Compare sequential runs honestly**: inspect two already-authorized harness executions over a
   controlled task/model/environment tuple; do not implement a scheduler to make the comparison.
6. **Watch** authorized autonomous activity in an ambient, low-cognitive-load event theatre where
   anomalies surface as findings, never as browser-triggered corrective actions.
7. **Prepare schemas and projections** for future knowledge graphs, RAG, delegation, topology, and
   governed improvement without implementing or operationally exposing locked milestones.

### Product success criteria

The pilot succeeds when a reviewer can:

1. replay a canonical fixture and identify every major state transition;
2. attach to a live sequential run without a gap or duplicate event;
3. trace one effect through proposal, authorization, durable intent, receipt, reduced state, and
   exterior evaluation;
4. visually author a draft manifest and obtain the same canonical backend validation/digest as a
   non-GUI caller;
5. compare two controlled runs without mixing lineages or overstating statistical evidence;
6. delete all browser caches and rebuild equivalent projections from canonical sources;
7. close the GUI mid-run without changing execution, safety, persistence, or evaluation.

### Authority-bound feature gates

The frontend discovers runtime capabilities; it never hard-codes milestone assumptions. Discovery
does not grant authority: both the accepted milestone state and the runtime capability response must
permit a control before it appears as enabled.

| Capability | Pilot behavior | Required authority |
|---|---|---|
| Fixture replay and inspection | Enabled | Existing VG-04/client-core contracts |
| One live sequential run | Enabled | Existing runtime service and I-11 |
| Draft composition authoring | Validate/preview only | Existing schema/compiler |
| Signed operator approval | Enabled through current command path | Existing governance contract |
| Controlled completed-run comparison | Enabled | Measurement law and existing run authority |
| M7-01 independence overlay | Read-only when schema exists | ADR-0092 measurement-only scope |
| Child-agent tree | Fixture/read-only | M-6 closure |
| Multi-run scheduling/concurrency | Disabled | Explicit M-7 Director ADR |
| Swarm/topology execution | Disabled | M-8 closure |
| Retrieval/second-brain operations | Schema/mock/read-only scaffold | M-9 authorization |
| Self-improvement/promotion | Simulation/proposal display only | M-10 governance |

### Non-goals at beta

- No cloud, no multi-tenant server, no auth system. Local-first, single operator, `0600` socket.
- No workflow *execution* in the frontend. The frontend may **author** a static composition graph;
  it must never become a dynamic control-flow DAG engine — that is an explicit architectural refusal
  in [`SPEC.md`](../../SPEC.md#architectural-refusals), and violating it in the UI would smuggle the
  refused engine in through the back door.
- No mutation of ledger history. The UI is append-only-respecting: it issues *commands*, it never
  edits *events*.
- No browser-side kernel, reducer authority, evaluator, scheduler, grant issuer, or canonical
  digest authority.
- No claim that hidden chain-of-thought is observable. Provider-returned reasoning summaries, when
  policy permits them, remain model output rather than ground truth.
- No requirement that local selections, graph coordinates, draft forms, connectivity state, or
  accessibility state be ledger events. Every **runtime fact** must have canonical provenance;
  presentation state remains explicitly local.

---

## 1. What we are visualizing (backend ground truth)

Everything below is what actually exists in the repo today. The frontend design is derived from it,
not from an idealized system.

### 1.1 The kernel and the S0–S12 pipeline

From [`docs/01_law/DISPATCH.md`](../../01_law/DISPATCH.md):

```
 S0  ENTER      EffectRequest { action, resource, args, principal, depth, ... }
 S1  PARSE      validate against the contract schema
 S2  RESOLVE    action → adapter                    ◄── BEFORE any lease
 S3  DESCRIBE   descriptor = digest(canonical(name, normalisedArgs))
 S4  CLASSIFY   widensCapability := classifier(request)
 S5  AUTHORIZE  decision := policy.authorize(AuthorityRequest)
 S6  GRANT      grant := issue(descriptor, principal, resources, ttl)
 S7  RESERVE    lease := governor.reserve(runId, resources, parentLease)
 S8  VERIFY     assert the grant binds THIS descriptor and is unexpired
 S8a INTENT     durably append EffectStarted{...} and FSYNC  ◄── BEFORE the effect
 S9  DISPATCH   adapter.execute(...)
 S10 COMMIT     governor.commit(lease, actual)
 S11 RELEASE    governor.release(lease)             ◄── every path, always
 S12 EMIT       outcome events                      ◄── after release
```

This is the single most valuable thing to render, because it is where every failure path
`F-01…F-25` lands. The **Effect Inspector** (§4.4) is literally this diagram, live, per effect.

### 1.2 The layers of separation

The substrate's separation thesis, as encoded in the package tree
([`vanguard/packages/`](../../../vanguard/packages/)):

| Layer | Package | What it owns | Frontend surface |
|---|---|---|---|
| **L0 Kernel (TCB)** | `kernel/` | S0–S12 reference monitor, domain-blind (I-7) | Pipeline Inspector, TCB LoC budget gauge |
| **L1 Domain** | `domain/` | primitives, wire contracts, JCS canonicalisation, ledger events, evidence, artifacts, selectors | Schema Explorer, canonical-digest diffing |
| **L2 Ports/SPI** | `ports/` | the five frozen SPIs (`IPlanner`, `IMemoryEngine`, `IToolkit`, `IContextAssembler`, `IEvaluator`) + `IModelProvider`, `IApprovalChannel` | SPI Boundary Map, capability negotiation view |
| **L3 Adapters** | `adapters/` | stores, sandbox, environment, evaluators, context, models, bindings | Adapter Bench, containment-profile badges |
| **L4 Runtime/Agency** | `runtime/`, `agency/` | service, governance, ledger, registry, manifests, context, episode | Run Theatre, Governor panel, Registry panel |

Plus the **exterior**: `packs/`, `lab/`, `benchmarks/`, `tools/` — deliberately outside the
substrate, and rendered as such (visually outside the boundary line; see §4.2).

> **Design rule.** The layer boundary is drawn as a *hard visual line* in every map view. If a UI
> element ever needs to straddle it, that is a signal that a real architectural violation is being
> proposed. The UI's job is to make invariant I-7 (domain-blind kernel) and I-6 (plugins untrusted)
> *visible enough to be violated loudly*.

### 1.3 The wire contract we already speak

[`schemas/v4/runtime-service.schema.json`](../../../schemas/v4/runtime-service.schema.json) —
NDJSON frames over a Unix domain socket at `VANGUARD_RUNTIME_SOCKET` (default
`/tmp/vanguard-runtime.sock`, mode `0600`, 1 MiB max frame):

- `frameType`: `command` | `receipt` | `event` | `error`
- Commands: `StartRun`, `GetRun`, `StreamEvents`, `ResolveApproval`, `RecordCorrection`, `Cancel`,
  `Checkpoint`, `Resume`, `ExplainArtifact`
- Every command carries `commandId` + `idempotencyKey` + `runId` — **idempotency is already in the
  contract**, which is what makes an optimistic, reconnect-tolerant GUI tractable.
- `event` is a full [`event-envelope.schema.json`](../../../schemas/v4/event-envelope.schema.json):
  `seq` (writer-allocated canonical order), `traceId`/`spanId`, `parentEventId`, `runId`/`episodeId`/
  `branchId`, `scope` ∈ {`episode`, `governance`, `evolution`, `recovery`}, and the full data-policy
  block (`tenantId`, `ownerId`, `confidentiality`, `retentionClass`, `trainability`,
  `redactionStatus`).

That data-policy block is a gift. It means the frontend can implement **redaction-aware rendering**
and **trainability-aware export** from day one, rather than retrofitting it (which the schema comment
explicitly calls "the corpus-format problem in its most expensive form (CT-16)").

Known payload kinds observed in the runtime today (non-exhaustive; readers MUST preserve unknown
kinds per CT-44): `EpisodeStarted`, `EpisodeCompleted`, `EffectStarted`, `EffectReconciled`,
`AuthorizationDenied`, `ApprovalResolved`, `CorrectionRecorded`, `EvaluationRequested`,
`ProposalProduced`, `CompetencePriorRecorded`, `RunRecovered`, `RunAborted`, `RunFailed`,
`Heartbeat`.

### 1.4 The client core we do not need to rewrite

[`vanguard/clients/client-core/src/`](../../../vanguard/clients/client-core/src/) is already a
headless, transport-agnostic TypeScript client:

- `adapters/transport.ts` — `RuntimeTransport` interface with `SocketTransport` and `FeedTransport`
  (JSONL replay) implementations, cursor-based `streamItems(afterSeq)`, typed `Result<T>`.
- `application/` — `run-view.ts`, `subscribe-run.ts`, `selectors.ts`, `why.ts`, `trace-graph.ts`,
  `approvals.ts`, `corrections.ts`, `budget.ts`, `resume.ts`, `attach.ts`, coding-specific commands.
- `contract/` — parse + types, the schema-derived readers.

**This is the single most important finding of the research pass.** The GUI is not a new client; it
is a **new view layer over `@vanguard/client-core`**. The CLI and the GUI become peers, sharing
selectors, reducers, and the trace-graph builder. Any behavior that differs between CLI and GUI is a
bug in exactly one place.

### 1.5 Source taxonomy, capability discovery, and consistent attachment

Every datum presented by the Observatory carries a source class: **ledgered**, **canonical query**,
**client-derived**, **local draft**, or **unknown**. The first two are runtime facts; client-derived
values name their function and inputs; drafts are never confused with frozen objects; unknown stays
unknown. This taxonomy is more precise than pretending that window layout or selection belongs in
the event ledger.

Connection begins with capability discovery, not milestone inference:

```ts
type RuntimeCapabilities = {
  protocol: "vg.4";
  commands: readonly string[];
  eventKinds: readonly string[];
  projections: readonly string[];
  limits: { maxFrameBytes: number; maxStreams?: number };
  features: Record<string, "disabled" | "read" | "command">;
};

const visible = acceptedMilestoneAllows(feature) && runtimeCapabilitiesAllow(feature);
```

This is a compatibility handshake, not a grant. Every command still traverses the normal authority
path. Missing or unknown capabilities fail closed in the control plane while raw events remain
inspectable.

Attaching to a live run requires an atomic **snapshot-plus-tail** contract. A naive `GetRun` followed
by `StreamEvents` has a race: events can land between the calls. The query returns a snapshot folded
through cursor `C`; the stream starts strictly after `C`. The client deduplicates by canonical event
identity and rejects a gap rather than drawing a plausible fiction:

```text
AttachRun(runId)
  -> { snapshot, throughCursor: C, streamToken }
StreamEvents(streamToken, after: C)
  -> events C+1 ...
```

Large artifacts are not embedded in event frames. The runtime needs metadata-first access followed
by authorized byte-range reads, with redaction and policy applied server-side. Until that exists,
artifact panels show provenance and availability, not a broken download assumption.

---

## 2. Design thesis: "World Champion 2026"

The brief asks for a SOTA, high-performance, clean, minimalistic design. Here is what that actually
means in this domain, stated as falsifiable rules rather than adjectives.

### 2.1 The seven laws of the interface

**L-1 — Runtime views are folds; presentation state is local.**
Canonical run state is `fold(events, cursor)`. Panels are selectors over that fold and canonical
query results. Selection, layout, draft text, focus, connection health, and accessibility settings
are explicitly local and disposable. Consequence: replay is deterministic without the false claim
that every pixel preference belongs in the ledger.

**L-2 — No runtime fact lacks provenance.**
Every factual visual declares its event, canonical query, or named derivation. Missing data becomes
a filed backend gap, an unavailable state, or an explicit inference—not invented telemetry. Local
presentation is permitted because it makes no substrate claim.

**L-3 — Truth has a texture; inference has another.**
Derived, estimated, or interpolated values MUST be visually distinct from ledgered facts (we use a
dotted underline + a `~` prefix, and a tooltip naming the derivation). An `undeterminable` S8a
intent is rendered *as* `undeterminable` — never as success, never as failure, never hidden. F-22
says so; the UI obeys.

**L-4 — Density with a floor of calm.**
Two modes, one codebase. **Operate** (dense, monospace, information-maximal, for debugging) and
**Watch** (sparse, ambient, motion-minimal, for autonomous mode). Same components, different
`data-density` token scope. No separate implementations.

**L-5 — Performance claims have datasets, tiers, and reference hardware.**
The interactive pilot is budgeted and tested at 100k events; one-million-event runs are a stress and
analytics tier using collapse, server cursors, and bounded materialization. No document promises
60 fps over an unbounded million-row DOM or graph. Budgets and degradation modes are in §9.

**L-6 — Keyboard-first, mouse-optional.**
This is a tool for someone who lives in a terminal. Every action has a key. A command palette
(`⌘K`) is the primary navigation surface. The mouse is for the graph canvas and nothing else that
matters.

**L-7 — Two themes, one truth.**
Light and dark are token swaps, never separate stylesheets. Semantic colors are bound to *meaning*
(denied / reconciled / undeterminable / promoted / refused), not to aesthetics.

### 2.2 Visual language

Minimalist, high-contrast, near-monochrome with a **five-signal** accent palette. Color is scarce
and therefore meaningful:

| Signal | Meaning | Where it appears |
|---|---|---|
| `signal.flow` (cyan) | normal mediated flow, lease open | pipeline stages S0–S12, active spans |
| `signal.hold` (amber) | awaiting human — approval suspended at F-08 | approval modal, run status |
| `signal.deny` (magenta) | authorization denied, refusal, fail-closed | `AuthorizationDenied`, containment fallback refusal |
| `signal.void` (violet) | `undeterminable` — F-22, unreconciled S8a | reconciliation panel, evidence rows |
| `signal.proof` (green) | signed verdict, replay parity, promotion-eligible | evaluator badges, M-4 evidence grid |

Neutral greys carry everything else. `signal.void` deserves its own hue precisely because the
substrate's most subtle correctness property is that "we don't know" is a first-class outcome; if it
shares a color with failure, we have taught the operator to misread the system.

Typography: one variable sans (UI chrome) + one variable mono (all data, all identifiers, all
digests). Digests render as `abcd12…ef90` with click-to-copy-full and hover-to-expand; never
truncate without an affordance.

Motion: ≤ 150 ms, ease-out, transform/opacity only. In Watch mode, motion is reserved for *state
change* only — a still screen means a still system, which is itself information.

---

## 3. Technology stack

### 3.1 The decision, with reasons

| Concern | Choice | Why (and what we rejected) |
|---|---|---|
| Shell | **Decision gate: browser gateway first; Tauri 2 spike in UI-0** | Both must use the identical generated contract and `client-core`. Choose Tauri only if native UDS, packaging, CSP, accessibility, and update measurements beat the maintained local gateway. Do not create two APIs. |
| Browser transport | Thin local gateway translating authenticated HTTP/SSE or WebSocket to the runtime contract | Enables fast development and remote-read scenarios. It performs framing and authentication only; it owns no domain or authority logic. |
| Framework | **React 19** + TypeScript 5.7 strict | Team-known, huge ecosystem, RSC not needed (local-first). Concurrent features (`useTransition`, `useDeferredValue`) matter at our ingest rates. Rejected: Svelte 5 (great, but splits us from the existing Ink/React CLI), SolidJS (best raw perf, smallest ecosystem for graph/table work). |
| State | **Zustand** (UI/session) + a hand-written **event store** (domain) | The domain state is a fold, not a store — we own it. Zustand only holds view state (selection, filters, layout). Rejected: Redux Toolkit (ceremony), Jotai (atom explosion at this cardinality). |
| Async/query | **TanStack Query v5** for command/receipt round-trips only | Events do not go through Query; they go through the fold. |
| Tables | **TanStack Table v8** + **TanStack Virtual** | Windowed rendering is non-negotiable for long histories. |
| Graph canvas | **React Flow** for editable, bounded composition graphs; **Sigma.js WebGL** for large read-only trace/knowledge graphs; **ELK.js** layout in a worker | Editing and exploration have different interaction/performance needs. A custom renderer is a benchmark-triggered contingency, not a first implementation. Collapse and level-of-detail precede more GPU code. |
| Charts | Modular **Apache ECharts** for streaming/progressive operational charts; optional Observable Plot for bounded experiment analysis | ECharts covers zoom, progressive rendering, accessibility metadata, and dense operational plots. Keep experiment grammar separate from hot-path telemetry. |
| Timeline/waterfall | Virtualized rows plus Canvas/ECharts custom series; promote to a bespoke renderer only after profiling | Start with maintained primitives and isolate geometry/hit testing behind an interface so measured hotspots can be replaced without rewriting the feature. |
| Diff | **Monaco** (lazy chunk) for code/patch diffs; custom JSON differ for canonical objects | Monaco is heavy but is the only credible patch-review surface; loaded on demand only. |
| Styling | **CSS custom properties + CSS Modules**; no runtime CSS-in-JS | Zero runtime cost, trivial theming, works with the token system. Rejected: Tailwind (token indirection fights the semantic-signal palette), Emotion (runtime). |
| Workers | **Comlink** over dedicated workers for: parse/validate, layout, indexing, diff | Main thread does render only. |
| Storage | **IndexedDB** for bounded immutable event chunks and projection checkpoints; optional **DuckDB-Wasm** worker for user-requested analytical extracts | Browser storage is a rebuildable cache, never authority. DuckDB-Wasm is powerful for Arrow/Parquet analysis but browser memory/thread limits prohibit treating it as the canonical event store. OPFS + SQLite-Wasm + vector extension remains an M-9 benchmark candidate, not beta infrastructure. |
| Schema/codegen | Reuse existing **JSON Schema → TS reader** generation under `tools/codegen` | A-4: one schema. The frontend MUST NOT hand-write mirrors of wire types — that is invariant I-8. |
| Testing | Vitest + Testing Library + Playwright (visual) + a bespoke **replay-fixture harness** | Fixtures are recorded NDJSON runs; the UI is deterministic given a fixture, so screenshots are stable. |
| Build | Vite 6 + `rolldown` when stable; strict chunk budgets | See §9.4. |

### 3.2 Why not "just extend the studio page"

[`vanguard/packages/runtime/studio/`](../../../vanguard/packages/runtime/studio/) is a 324-line
static HTML page with a hardcoded `/api/status` payload (`tcb_loc: 1366`, `active_wave: "W-3D"`).
It is a placard, not an instrument, and its status endpoint literally violates L-2 (values not
derived from events). It should be **retired** into the new Studio's "About / TCB budget" panel,
with the numbers computed by the existing linters instead of typed by hand.

---

## 4. Feature architecture — the surfaces

Nine surfaces. Each is a route, a keyboard target, and an independently code-split chunk.

### 4.1 `⌘1` Run Theatre — the live run

The default surface. Four-pane, resizable, all panes driven by one fold.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ ◉ run_01J8… code-default · hermetic · D_H a91f… · turn 7/∞ · $0.412 · 00:03:11│  ← run bar
├───────────────┬──────────────────────────────────────────┬───────────────────┤
│ TURN SPINE    │ TRANSCRIPT / INVOCATIONS                 │ EFFECT INSPECTOR  │
│               │                                          │                   │
│ ▸ turn 1  ✓   │  turn 7 · invocation 2 (escalation)      │  fs.write         │
│ ▸ turn 2  ✓   │  ├ model  openrouter/deepseek-v4  1.8s   │  S0 ▸▸▸▸▸▸▸▸ S12  │
│ ▸ turn 3  ⚠   │  ├ plan   drive-until-green              │  ●●●●●●●○○○○○     │
│ ▸ …           │  ├ effect fs.read  /workspace/a.py  ✓    │  S7 RESERVE       │
│ ▾ turn 7  ◉   │  ├ effect patch.apply  ast-patch   ✓     │  lease 4211       │
│   ├ inv 1 ✓   │  └ effect terminal.run  pytest    ✗ 1    │  grant g_9f…      │
│   └ inv 2 ◉   │                                          │  descriptor 7c1a… │
│               │  ⧗ awaiting approval: net.fetch           │  args (canonical) │
├───────────────┴──────────────────────────────────────────┴───────────────────┤
│ LEDGER TAPE  ▏seq 1…4,812  ◂───────────────█████──────────▸  [live] [⏸] [⇤]  │
└──────────────────────────────────────────────────────────────────────────────┘
```

- **Turn spine** — the sequential turn loop (I-11). Turns are never parallel here; if the UI ever
  shows two concurrent turns in one episode, the substrate is broken or the UI is lying.
  Invocations nest under turns (retries/escalations conserve additive cost — the spine shows the
  running additive total per turn).
- **Transcript** — virtualized, event-backed. Each row links to its `eventId`. Model messages,
  plans, effects, verdicts. Collapsible by kind. `/` filters with a typed mini-query language (§4.7).
- **Effect inspector** — §4.4.
- **Ledger tape** — a scrubbable seq axis. Dragging it re-folds to that `seq`; the entire UI becomes
  the past. This is the feature that makes the frontend worth building.

**Approvals.** When the run suspends at F-08 (before the lease is opened), the tape halts, the run
bar turns `signal.hold`, and an approval sheet presents: the verb, the canonical descriptor, the
resource selector, the requesting span, the justifying spans, the budget delta, and the two
signable outcomes. Resolution goes out as `ResolveApproval` with an operator signature via the
existing `signer.ts` path. **The GUI must never bypass the operator-signature flow** — an unsigned
approval is exactly the forgery I-5/I-2 exist to reject.

### 4.2 `⌘2` Substrate Map — the five layers, live

A single zoomable canvas. Not a decoration — a live instrument.

- Concentric/stacked bands: **L0 Kernel** at the center (with its LoC-budget ring), then L1 Domain,
  L2 Ports/SPI, L3 Adapters, L4 Runtime/Agency, and outside the boundary line: packs, lab,
  benchmarks, tools.
- **Live flow**: during a run, effect requests animate inward through the SPI ring to the kernel and
  back out to adapters. Particle density = effect rate. Denied requests bounce off the S5 ring in
  `signal.deny`.
- **Boundary assertions rendered as guards**: hover the kernel ring → "domain-blind (I-7): 0 domain
  tokens under `kernel/`" with the linter result that proves it. Hover the plugin ring → "untrusted
  by default (I-6)" with the active isolation mode per plugin.
- **Click-through**: any band drills into its package, its modules, its owning law leaf, and its
  ADRs. This is how the map becomes documentation that cannot go stale.

An early static ancestor of this exists at
[`tools/substrate_visualizer/index.html`](../../../tools/substrate_visualizer/index.html); its
content should be lifted and made event-driven.

### 4.3 `⌘3` Composition Studio — manifests, plugins, packs, configs

The authoring surface, and the one that pays for itself fastest.

- **Left**: catalog of plugins by SPI slot, sourced from the registry
  ([`vanguard/packages/runtime/registry/`](../../../vanguard/packages/runtime/registry/)) — each
  card shows `ref`, version range, `spi_version`, negotiated `capabilities()`, isolation mode, and
  lifecycle FSM state (`DISCOVERED → RESOLVED → … `), every transition ledgered.
- **Center**: the composition as a **static graph** — five SPI slots + toolkits array + model routes
  + capability grants, exactly the shape of
  [`packs/code-default/harness.yaml`](../../../packs/code-default/harness.yaml). Drag a plugin into
  a slot; edit its `config` in a schema-driven form (forms generated from the plugin's declared
  config schema — never hand-written).
- **Right**: the **identity panel**. As you edit, the browser shows a clearly labeled provisional
  draft diff; a debounced `GetComposition`/preview query asks the canonical backend path to compute
  `D_H`. It shows: canonical `D_H`, the diff against the last frozen
  composition, and *which field changed the digest*. Then `D_R` (adds runtime/env/model/oracle) and
  `D_X` (adds dataset/protocol) stack below — **three separate rows, never collapsed** (A-5).
- **Capabilities editor**: verbs + resource selectors, with a live "what this grants" explainer that
  renders the selector as a concrete set (paths, hosts, commands). Widening a capability is shown in
  `signal.deny` amber-to-magenta with a warning that S4 will classify it as widening.
- **Validate draft** returns diagnostics and canonical identity but creates no runnable object.
  **Freeze** remains a distinct authorized command and then shows `FrozenComposition →
  ActivationPlan → RunPlan` as a read-only chain.

> **Refusal guard.** The composition canvas is a *static graph editor*. It has no conditionals, no
> loops, no runtime branching, and no "execute this node" affordance. A visible banner states:
> "Static composition — the runtime turn loop is unary and sequential (I-11)." If a future feature
> request wants edges with conditions, the answer is an ADR and RF-66 reversal evidence, not a UI
> ticket.

### 4.4 `⌘4` Effect Inspector — S0–S12, per effect

The diagram from §1.1, rendered as a 13-stage progress rail per effect, with:

- Per-stage timing (µs), per-stage outcome, and the exact failure code if it stopped (`F-01`…`F-25`).
- **S8a intent highlighting**: the durable intent record and its fsync are drawn as a *lock icon*
  before S9. If an intent has no reconciled outcome, the whole effect renders `signal.void`
  `undeterminable` — never "failed", never omitted (F-22, and the SPEC is explicit that reporting it
  as successful or settled is forbidden).
- **Lease lifecycle**: reserve → commit → release drawn as a bracket spanning S7…S11, with the
  reserved vs. actual amounts. A lease that appears released without a matching reserve, or vice
  versa, is drawn as a torn bracket and raised as an anomaly (§4.8).
- **Grant binding**: S8's "does this grant bind THIS descriptor" check renders both digests side by
  side. This is the check that makes capability confusion visible.
- **Canonical args viewer**: the JCS-canonical form with its digest, and a toggle to the raw form,
  and a byte-level diff between them when normalisation changed something.

### 4.5 `⌘5` Trajectory & Evidence — proof, not vibes

- **Trajectory viewer**: the complete recovered trajectory (I-9) as a span tree + waterfall.
  Waterfall on the left (canvas, virtualized), span tree on the right, linked selection. Gaps in the
  trajectory are rendered as explicit gap markers with their reason, because a trajectory that
  silently skips is the exact failure I-9 forbids.
- **Replay parity view**: run fresh-process replay, then show a three-column diff — recorded events,
  replayed events, divergence. Green means I-4 holds for this run. This is a *button*, and it should
  be the most-clicked button in the app.
- **Evidence grid (M-4)**: the nine source-derived evidence lines as rows, each with its state from
  the canonical auditor's four-valued vocabulary — `absent` / `invalid` / `unverifiable` /
  `present_valid` — and its source artifact. Self-attested booleans and defaulted paths are rendered
  as `invalid` with an explanation, per the SPEC's refusal. No row may be green without a link to the
  artifact that proves it.
- **Verdict inspector**: exterior signed judge (I-5). Shows the signature, the signer key, the
  verification result, and — critically — renders `evaluation: none` runs with a permanent
  `unattributable_for_promotion` badge that cannot be dismissed.
- **Cost ledger**: additive costs per turn/invocation, budget conservation check, Governor lease
  reconciliation. A budget leak is an anomaly with a dedicated visual.

### 4.6 `⌘6` Arena — harness vs. harness (incl. Claude Code CLI)

This is the surface the brief most wants, and it is also the one most likely to produce a
scientifically worthless result if built naively. So it is built as an **experiment runner**, not a
race track.

**The paired-comparison model.** Two arms, A and B. Same task set, same model tier, same seeds, same
containment profile, same oracle. The only permitted difference is the thing under test (the
harness composition). The UI *enforces* this: it computes `D_R` for both arms and shows which
components differ; any difference outside the declared independent variable is flagged red and the
experiment is marked confounded before it starts.

**Preregistration.** Arena runs write a
[`preregistration.schema.json`](../../../schemas/mhf/preregistration.schema.json) record before
execution: hypothesis, arms, task set, primary metric, stopping rule, N. The UI will not display a
p-value for an experiment that has no immutable preregistration bound to it. Post-hoc metric
selection is the failure mode the measurement law exists to prevent, and a GUI makes that failure
mode one click away unless we design against it.

**The comparison itself.** `lab/bench.py` already implements exact two-sided McNemar plus χ² over
discordant pairs and *refuses* when there are no discordant pairs. The Arena surface is a front-end
to exactly that, not a reimplementation:

```
ARM A  vg/code-default @ D_H a91f…      ARM B  claude-code-cli-shaped @ D_H 4d02…
model  openrouter/deepseek-v4 (identical)     profile  hermetic (identical)
task set  swe-mini-40 @ D_X 88ce…             oracle  coding-oracle@3 (identical)

  40 tasks  ████████████████████████░░░░  33/40 complete

           A pass   A fail                  b = 7   (A✓ B✗)
  B pass  │  21   │   4  │                  c = 4   (A✗ B✓)
  B fail  │   7   │   1  │                  χ² = 0.818   p = 0.549
                                            ▸ NOT SIGNIFICANT — no promotion
```

**Comparing against Claude Code CLI specifically.** Two honest modes:

1. **Black-box arm** — Claude Code runs as an *exterior process* under our sandbox adapter, with the
   same model, same repo snapshot, same oracle. We observe only its inputs, its diff, and the
   oracle's verdict. We do **not** claim to observe its internal trajectory; the trajectory panel for
   that arm renders as `unobservable`, not as an empty trajectory. This is the L-3 rule applied to a
   competitor.
2. **Shaped arm** — a pack under `packs/` that *reimplements* the Claude Code interaction shape
   (tool roster, prompt shape, loop policy) inside our substrate, giving a fully observable arm. The
   comparison A-vs-B-shaped is the scientifically strong one; A-vs-black-box is the externally
   credible one. Run both; report both; never conflate them.

**Future matrix/swarm mode (M-7/M-8 gated).** The intended view is `pack × model × seed × profile ×
task`, with every execution remaining a first-class run. Before scheduler authority exists, Arena
only imports or compares runs launched through already-authorized sequential paths. The disabled
matrix view is useful as a design fixture, but it must not acquire a hidden queue or browser-side
scheduler. When enabled later, the UI must distinguish independent run concurrency from concurrency
inside a turn.

### 4.7 `⌘7` Ledger Explorer — the query surface

The `jq` replacement. A virtualized table over server-side cursors and bounded IndexedDB chunks,
with optional DuckDB-Wasm analytical extracts, with:

- A small typed query language, e.g.
  `kind:EffectStarted AND runId:01J8* AND cost>0.01 AND NOT redacted` — parsed to SQL, executed in a
  worker.
- Saved queries, and **query→panel promotion**: any query can become a pinned dashboard card.
- Columns are schema-derived (A-4). Adding a field to the event schema adds a column; there is no
  hand-maintained column list.
- **Data-policy aware**: rows respect `confidentiality` / `redactionStatus`. Redacted payloads render
  as sealed blocks with the redaction reason. Export honors `trainability` — an export that would
  include non-trainable rows requires an explicit acknowledgment and stamps the export manifest.

### 4.8 `⌘8` Autonomy Watch — the ambient theatre

Low-density, motion-minimal, designed to be left on a second monitor for hours.

- A slow river of significant events only (significance is a scored filter, not a hardcoded list).
- **Anomaly surfacing**: the UI runs a small set of local detectors over the fold —
  lease imbalance, budget drift, unreconciled S8a intents older than T, verdict-signature failures,
  replay divergence, escalation-rate spikes, cost-per-verdict regressions, plugin lifecycle stalls,
  containment-fallback refusals. Each detector is a named, testable pure function over folded state
  and emits a UI-local finding with a link to the evidence.
- **Health rings**: TCB LoC vs. budget, invariant-linter status, falsifier suite status
  (`F-01…F-25`), open `undeterminable` count, active leases, budget headroom.
- **Escalate to Operate**: any anomaly is one key away from opening the exact Theatre state at the
  exact `seq` where it occurred.

Anomalies are *findings*, never *actions*. The Watch surface has no autonomous control affordances;
if we want the system to act on its own findings, that belongs in the substrate under the evolution
scope, with events, not in a browser tab.

### 4.9 `⌘9` Second Brain — RAG, graph, meta-cognition (beta scaffold)

Scaffold now, so the corpus is right later.

- **Graph view**: events, artifacts, verdicts, manifests, ADRs, law leaves, and packs as typed nodes;
  edges from `parentEventId`, `traceId`, artifact lineage, `D_H`/`D_R`/`D_X` binding, and document
  links. Rendered with the same WebGL canvas as §4.2.
- **High-order relations**: the graph is stored as a hypergraph-capable edge table (`edge(kind,
  members[], props)`), because "this verdict, under this composition, on this dataset, disagreed with
  that one" is a 4-ary relation and forcing it into binary edges destroys the exact structure
  meta-cognition will need.
- **Future vector index**: M-9 chooses server-side or browser-side storage from measured corpus size,
  deletion, portability, policy, and retrieval quality. Embeddings always use a mediated substrate
  path; the frontend never calls model APIs directly.
- **Obsidian bridge**: export a run, an arena result, or a query as a markdown note with frontmatter
  and `[[wikilinks]]` into a vault directory. The document you are reading is exactly the shape of
  what gets exported.
- **Context engineering lab**: visualize what the `IContextAssembler` actually assembled per turn —
  token budget, prefix-freeze boundary, compaction decisions, what was dropped and why. The
  `packs/code-default/harness.yaml` context config (`token_budget: 4000`, `compaction:
  recency-window`, `prefix_freeze: true`) becomes a live, inspectable, tunable object with a
  measured effect on outcomes.

> **Explicit scope boundary.** Per [`SPEC.md`](../../SPEC.md#milestone-compatibility), retrieval,
> macros, Active Inference and meta-cognition are **M-9+ post-v1 research and non-authorizing**.
> The Second Brain surface is therefore a *corpus-shaping and inspection* tool at beta. It reads. It
> does not steer the substrate.

---

## 5. Frontend internals — the engineering

### 5.1 Module layout

```
vanguard/clients/studio/
├─ src/
│  ├─ contract/            # RE-EXPORTS from @vanguard/client-core. No local wire types. (I-8)
│  ├─ store/
│  │  ├─ event-store.ts    # ring buffer + index + fold driver
│  │  ├─ fold/             # pure reducers, one file per concern
│  │  │  ├─ run.ts  turns.ts  effects.ts  leases.ts  budget.ts
│  │  │  ├─ approvals.ts  verdicts.ts  plugins.ts  trajectory.ts
│  │  ├─ selectors/        # pure, memoized, testable
│  │  └─ detectors/        # anomaly detectors (pure fns over folded state)
│  ├─ transport/
│  │  ├─ tauri-uds.ts      # invoke → Rust host → UDS
│  │  ├─ sse-bridge.ts     # dev/browser fallback
│  │  └─ file-replay.ts    # NDJSON fixture replay (wraps FeedTransport)
│  ├─ workers/
│  │  ├─ ingest.worker.ts  # parse, validate, index, seq-order
│  │  ├─ layout.worker.ts  # ELK graph layout
│  │  ├─ query.worker.ts   # bounded analytics; engine selected by benchmark
│  │  └─ diff.worker.ts    # canonical/JCS diff
│  ├─ render/
│  │  ├─ gl/               # WebGL2 graph + waterfall renderers
│  │  ├─ canvas/           # 2D sparklines, heatmaps, tape
│  │  └─ hit/              # offscreen hit-test buffers
│  ├─ surfaces/            # one dir per ⌘1…⌘9 surface
│  ├─ ui/                  # primitives: Table, Rail, Sheet, Palette, Tokens
│  └─ app.tsx
├─ shell/                  # selected gateway or Tauri bridge; translation only
├─ fixtures/               # recorded NDJSON runs used by tests
└─ bench/                  # performance harness (§9.4)
```

Placing it at `vanguard/clients/studio/` makes it a workspace peer of `cli/` and `client-core/` under
the existing `package.json` workspaces globs — no build-system surgery.

### 5.2 The event store (the hot core)

The single most performance-critical decision: **do not put events in React state, and do not put
them in objects**.

```ts
// Columnar, typed-array-backed ring store. Events are rows; hot fields are columns.
class EventStore {
  private cap: number;                 // ring capacity, default 1_000_000
  private seq  = new BigInt64Array(cap);
  private ts   = new Float64Array(cap);
  private kind = new Uint16Array(cap);   // interned kind → id
  private run  = new Uint32Array(cap);   // interned runId → id
  private span = new Uint32Array(cap);
  private parent = new Int32Array(cap);  // row index of parent, -1 if none
  private payloadOffset = new Uint32Array(cap);  // into a payload arena
  private arena: Uint8Array;             // raw JSON payload bytes, appended
  private byRun: Map<number, Int32Array>;      // secondary indices, rebuilt lazily
  private bySeq: (seq: bigint) => number;      // binary search over `seq`

  append(rows: ParsedEvent[]): AppendResult;   // called from the ingest worker
  slice(fromSeq: bigint, toSeq: bigint): RowRange;
  payload(row: number): unknown;               // lazy JSON.parse, LRU-cached
}
```

Rationale, each point load-bearing:

- **Interning** kinds/runIds/spanIds into integers can collapse dominant memory cost. At stress scale,
  object-per-event with string fields is ~1.2 GB; the columnar form is ~60 MB plus the payload arena.
- **Lazy payload parse** — 95% of payloads are never opened. Parse on demand, LRU 5k entries.
- **`parent` as a row index**, resolved at ingest, makes the span tree an O(n) array walk rather than
  a hash-join per render.
- **Bounded-cache semantics**: evicted rows remain queryable through the canonical backend cursor,
  so historical correctness does not require retaining the whole corpus in the browser.

**Ordering.** `seq` is writer-allocated and canonical; `eventId` is UUIDv7 and aids indexing but
carries no causal order — the schema says so explicitly, and the store MUST NOT sort by `eventId`.
Out-of-order arrivals are buffered in a small reorder window keyed on `seq`.

### 5.3 The fold and its cursor

```ts
type Fold = { at: bigint; run: RunState; effects: EffectMap; leases: LeaseMap; /* … */ };

// Reducers are pure and total: every event kind, including unknown, must be handled. (CT-44)
function reduce(prev: Fold, row: Row, store: EventStore): Fold;

// Incremental forward fold + periodic snapshots for O(1)-ish backward scrubbing.
class FoldEngine {
  private snapshots: Array<{ at: bigint; fold: Fold }>;  // every 5_000 events, structurally shared
  foldTo(seq: bigint): Fold {
    const base = nearestSnapshotAtOrBefore(seq);          // binary search
    let f = base.fold;
    for (const row of store.slice(base.at, seq)) f = reduce(f, row, store);
    return f;                                             // ≤ 5k reductions worst case
  }
}
```

Structural sharing can keep checkpoints cheap across the interactive window. Checkpoint interval and
representation are benchmark outcomes; checkpoints are disposable accelerators, never authority.

**Unknown-kind rule.** `reduce` for an unrecognized `payload.kind` MUST record the row in a
`unknownKinds` bucket and continue — CT-44 is explicit, and a UI that throws on a new event kind
would make every backend addition a frontend outage.

### 5.4 Render pipeline

```
UDS/SSE ─► ingest.worker ─► (validate, intern, index) ─► SharedArrayBuffer / postMessage
                                                              │
                            main thread: EventStore.append ───┤
                                                              ▼
              rAF tick (≤16.6ms) ─► FoldEngine.foldTo(cursor) ─► selectors (memoized)
                                                              ▼
                           React commit (useSyncExternalStore, batched, transition-wrapped)
                                                              ▼
                              Canvas/WebGL renderers draw from typed arrays directly
```

Key rules:

- **Coalesce to rAF.** Never render per event. Ingest fills a staging buffer; one rAF tick applies
  the batch. At 5k events/sec this is ~83 events per frame, one commit.
- **React renders chrome, not data.** Rows, spans, nodes, and points are drawn by canvas/WebGL from
  typed arrays. React handles selection, panels, forms, and layout.
- **`useSyncExternalStore`** with a version counter is the only bridge between the store and React.
- **Backpressure.** If the fold cannot keep up, the tape switches from `live` to `behind (N events)`
  and shows it. Silently dropping is forbidden (L-2/L-3).

### 5.5 Pseudocode: the live subscription

```ts
async function attachRun(runId: RunId, cursor: EventCursor, store: EventStore) {
  const transport = await resolveTransport();          // tauri-uds | sse-bridge | file-replay
  const staging: ParsedEvent[] = [];
  let lastSeq = cursor.afterSeq ?? 0n;

  const pump = (async () => {
    for await (const item of transport.streamItems({ afterSeq: lastSeq }, signal)) {
      if (!item.ok) {
        if (item.retryable) { await backoff(); continue; }   // reconnect resumes at lastSeq
        surfaceTransportError(item); return;
      }
      const env = item.value.envelope;
      if (BigInt(env.seq) <= lastSeq) continue;              // idempotent replay-safe
      lastSeq = BigInt(env.seq);
      staging.push(intern(env));
    }
  })();

  const tick = () => {
    if (staging.length) { store.append(staging.splice(0)); bumpVersion(); }
    requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
  await pump;
}
```

Reconnect correctness comes free: `streamItems` is cursor-based, `seq` is monotonic per run, and
duplicate `seq` values are dropped. This mirrors what `client-core`'s `FeedTransport` already does.

### 5.6 Pseudocode: the S0–S12 effect fold

```ts
function reduceEffect(f: Fold, row: Row): Fold {
  const p = payload(row);
  switch (p.kind) {
    case "EffectStarted": {                 // S8a intent — durable, pre-execution
      return upsertEffect(f, p.descriptor, {
        stage: "S8a", intentSeq: row.seq, grantId: p.grantId,
        idempotencyKey: p.idempotencyKey, outcome: "pending",
      });
    }
    case "EffectCompleted":
      return advance(f, p.descriptor, { stage: "S12", outcome: "settled", cost: p.cost });
    case "EffectRejected":
      return advance(f, p.descriptor, { stage: p.stage, outcome: "rejected", failure: p.code });
    case "AuthorizationDenied":
      return advance(f, p.descriptor, { stage: "S5", outcome: "denied", reason: p.reason });
    case "EffectReconciled":
      // F-25 / recovery scanner. `unknown` MUST render as undeterminable, never as success.
      return advance(f, p.descriptor, {
        stage: "S12", outcome: p.outcome === "unknown" ? "undeterminable" : p.outcome,
      });
    default:
      return noteUnknown(f, p.kind, row);
  }
}

// A separate, *derived* pass, clearly marked as inference (L-3):
function markStaleIntents(f: Fold, nowMs: number, thresholdMs: number): Finding[] {
  return effectsWithIntentButNoOutcome(f)
    .filter(e => nowMs - e.intentAtMs > thresholdMs)
    .map(e => finding("unreconciled-intent", e, "F-22 undeterminable — awaiting reconciliation"));
}
```

Note what this pseudocode refuses to do: it never synthesizes an outcome, never assumes success from
absence of failure, and never collapses `unknown` into a binary. That is not fastidiousness — it is
the F-22 rule, and it is the single most likely place for a frontend to introduce a falsehood.

### 5.7 Pseudocode: WebGL span waterfall

```ts
// One instanced draw call for all spans. Colors from a 1D LUT keyed on outcome.
function uploadSpans(gl: WebGL2RenderingContext, fold: Fold) {
  const n = fold.spans.count;
  const inst = new Float32Array(n * 6);          // x, w, y, h, colorIdx, depth
  for (let i = 0; i < n; i++) {
    inst[i*6+0] = tScale(fold.spans.startMs[i]);
    inst[i*6+1] = Math.max(tScale(fold.spans.durMs[i]), MIN_PX);   // never render a 0-width span
    inst[i*6+2] = fold.spans.depth[i] * ROW_H;
    inst[i*6+3] = ROW_H - 2;
    inst[i*6+4] = OUTCOME_LUT[fold.spans.outcome[i]];
    inst[i*6+5] = fold.spans.depth[i];
  }
  gl.bindBuffer(gl.ARRAY_BUFFER, instBuf);
  gl.bufferData(gl.ARRAY_BUFFER, inst, gl.DYNAMIC_DRAW);
  gl.drawArraysInstanced(gl.TRIANGLE_STRIP, 0, 4, n);              // one call, 10⁵ spans
}
```

`MIN_PX` matters: a sub-pixel span that renders as nothing is a span the operator will never
investigate. Zero-duration effects exist (rejections at S1) and must remain clickable.

Hit-testing uses an offscreen framebuffer where each span is drawn in a unique ID color; a
`readPixels` of one pixel under the cursor gives O(1) picking without a spatial index.

This is contingency pseudocode, not the initial renderer commitment. The same geometry contract
feeds the maintained Canvas/ECharts path first; custom WebGL ships only after UI-0 proves the need.

### 5.8 Accessibility and correctness of perception

- Every signal color pairs with a **shape or glyph** — colorblind operators must be able to read the
  `deny` / `void` / `proof` distinction without hue. This is a correctness requirement, not a
  courtesy: misreading `undeterminable` as `failed` produces wrong engineering decisions.
- Full keyboard reachability; focus rings always visible; `prefers-reduced-motion` disables the
  substrate-map particle flow and all transitions.
- All contrast ≥ 4.5:1 in both themes, verified in CI by a token-level checker.
- Every graph has a synchronized sortable table/tree with the same nodes, edges, states, and actions;
  pixels are never the sole semantic surface.
- Target WCAG 2.2 AA, including focus-not-obscured, target size, status announcements, and no
  drag-only operation. Accessibility is a correctness and safety property.

---

## 6. Development guidelines

**G-1 — No hand-written wire types.** Types come from `@vanguard/client-core`, which comes from
generated readers, which come from JSON Schema. A PR adding an `interface EventEnvelope` to the
frontend is rejected on sight (A-4, I-8).

**G-2 — Reducers and selectors are pure and unit-tested against fixtures.** Every reducer gets a
fixture-driven test. Fixtures are real recorded NDJSON runs committed under `fixtures/`, never
hand-authored objects — hand-authored fixtures encode our assumptions rather than the system's
behavior.

**G-3 — Provenance annotations are mandatory.** Every component that displays substrate data carries
a `provenance` prop or a doc comment naming the event kinds and fields it reads. A lint rule
enforces the annotation's presence; a test asserts the named kinds exist in the schema.

**G-4 — No effects from the frontend except through commands.** The GUI never touches the filesystem,
never calls a model, never spawns a process. It sends `command` frames. The Tauri host's allowlist is
narrow: connect to the socket, read fixture files under a scoped dir, write exports under a scoped
dir. Anything else is an unmediated effect and defeats the entire point of S0–S12.

**G-5 — Performance budgets are tests.** See §9.4. A PR that regresses frame time > 10% fails CI.

**G-6 — Two-mode discipline.** Every new component must render acceptably in both Operate and Watch
density. If it can only work dense, it belongs in a detail sheet, not a surface.

**G-7 — Feature flags for anything touching law-adjacent claims.** Replay-parity, evidence grid, and
promotion UI ship behind flags until their backend evidence path is real, so the UI never displays a
green badge whose backing does not exist.

**G-8 — Error states are designed first.** For each surface, the disconnected, empty, partial,
behind, and contradictory states are designed and implemented before the happy path. "Contradictory"
is a real state here: the ledger can contain an intent with no outcome, and the UI must have a
first-class rendering for it.

**G-9 — No dependency without a budget line.** Bundle budgets are per-chunk and enforced. Monaco and
the graph renderer are lazy chunks; the initial chunk stays under 250 KB gzipped.

**G-10 — Commit discipline.** Frontend commits reference the surface (`studio(theatre): …`), and any
commit that assumes a backend change references the ADR that authorizes it — or is blocked.

---

## 7. Data & protocol contract between GUI and substrate

Restated as the contract the GUI depends on. Items marked **(exists)** work today; items marked
**(gap)** are proposed in the BACKEND CHANGES chapter.

| Need | Status | Notes |
|---|---|---|
| Cursor-based event stream with `afterSeq` | **exists** | `StreamEvents` + `EventCursor` |
| Idempotent commands | **exists** | `commandId` + `idempotencyKey` in every frame |
| Full event envelope with trace/span/parent | **exists** | `event-envelope.schema.json` |
| Data-policy labels for redaction-aware render | **exists** | `confidentiality`/`retentionClass`/`trainability`/`redactionStatus` |
| Approval suspend/resolve with operator signature | **exists** | `ResolveApproval`, `signer.ts` |
| Artifact explain | **exists** | `ExplainArtifact` |
| Checkpoint/Resume/Cancel | **exists** | commands present |
| Multi-run subscription (one connection, many runs) | **gap** | today the stream is run-scoped; swarm needs a multiplexed or wildcard subscription |
| Enumerate runs / list history | **gap** | no `ListRuns` command |
| Read composition/activation/run plan as data | **gap** | no `GetComposition` / `DescribeManifest` |
| Read plugin registry + lifecycle FSM state | **gap** | registry exists in-process, not on the wire |
| Compute `D_H` for a draft composition (dry-run freeze) | **gap** | needed for the live identity panel |
| Trigger and report fresh-process replay parity | **gap** | replay exists as a procedure, not a command |
| Structured S0–S12 stage telemetry per effect | **partial** | `EffectStarted`/`EffectReconciled` exist; per-stage timing does not |
| Anomaly-relevant lease events (reserve/commit/release) | **partial** | governor has the data; not consistently on the wire |
| Backpressure/flow-control signal on the stream | **gap** | needed so the GUI can report `behind` truthfully |

---

## 8. Security & trust posture of the GUI

The GUI is a **client**, and — per A-2 — clients are not trusted subjects of either authority system.

- **Transport**: UDS only, mode `0600`, owner-only. No TCP listener at beta. If a remote pilot is
  ever needed, it is an `ADR` about a *gateway*, not a socket bind change.
- **Rendering untrusted content**: model output, tool output, file contents, and plugin names are all
  untrusted strings. They are rendered as text, never as HTML, never as a URL that auto-loads, never
  as anything the CSP would fetch. Strict CSP: `default-src 'none'`, no remote origins, all assets
  bundled.
- **Prompt-injection surface**: transcript content may contain text attempting to instruct an
  operator or a downstream agent. The transcript renders such content in a visually quarantined block
  and never lifts it into a command payload without explicit operator action.
- **Signatures**: verdict and approval signature verification happens in the substrate. The GUI
  displays the substrate's verification result and its own independent check where it can, and shows
  disagreement loudly rather than picking a winner.
- **Secrets**: the event stream may carry `secret`-kind selectors. The GUI never persists payloads
  labeled non-trainable or confidential to persistent browser storage without enforcing that label, and
  its export path refuses by default.

---

## 9. Performance engineering

### 9.1 Budgets (enforced)

| Metric | Budget |
|---|---|
| Cold start to interactive shell | < 800 ms |
| First meaningful paint, 100k-event fixture replay | < 500 ms |
| Sustained ingest without frame drop | ≥ 5,000 events/sec |
| Frame time at 100k-event interactive tier | ≤ 16.6 ms p95 during direct manipulation |
| Main-thread long tasks at steady ingest | none > 50 ms; p95 recorded |
| 1M-event stress tier | bounded-memory navigation via server cursor/collapse; no full materialization requirement |
| Fold-to-arbitrary-seq (backward scrub) | < 50 ms p95 |
| Graph layout, 10k nodes (worker) | < 2 s, non-blocking |
| Initial JS chunk | < 250 KB gzipped |

### 9.2 Techniques, in priority order

1. Columnar typed-array event store with interning (§5.2) — the single biggest win.
2. Everything off the main thread except render.
3. rAF coalescing of ingest.
4. Snapshot-based incremental fold with structural sharing.
5. Virtualization everywhere (tables, trees, transcript).
6. GPU-instanced drawing for spans/nodes/points; one draw call per layer.
7. Lazy payload parse with LRU.
8. Code-split per surface; prefetch on hover of the surface's key hint.
9. Server-side cursors for full history; IndexedDB for bounded cache; DuckDB-Wasm only for explicit extracts.
10. `content-visibility: auto` on offscreen panels; `contain: strict` on canvas hosts.

### 9.3 Anti-patterns explicitly banned

- Events in React state or in a Zustand store.
- `JSON.parse` on the main thread for stream payloads.
- Re-rendering a list on every event.
- SVG for anything with > 1,000 elements.
- A per-event React component. (The transcript is virtualized rows over a typed-array window.)
- `Date` objects per event (store epoch millis as `Float64`).

### 9.4 The performance harness

`bench/` contains a headless Playwright run over generated fixtures at 10k / 100k plus a 1M-event
degradation test, which
records ingest throughput, p95 frame time, fold latency, and peak heap, and writes a JSON report.
Budgets name browser version, CPU class, core count, memory, viewport, and power mode. CI compares
stable 10k/100k medians against a committed baseline and flags a statistically noisy or >10%
regression for review rather than laundering runner variance into false precision. Fixture generation is
deterministic (seeded), so the numbers are comparable across commits — the same discipline the
substrate applies to its own measurement law, applied to the UI.

---

## 10. Testing strategy

| Layer | Approach |
|---|---|
| Reducers/selectors | Vitest, property-based (`fast-check`) + real NDJSON fixtures |
| Fold determinism | Fold a fixture forward, snapshot at every 1k, refold from each snapshot, assert identity |
| Unknown-kind resilience | Inject synthetic unknown kinds into fixtures; assert no throw, assert bucketed (CT-44) |
| Contract conformance | Validate every fixture line against `event-envelope.schema.json`; the app must reject nothing the schema accepts |
| Transport | Fake UDS server replaying golden frames incl. reconnect, dup `seq`, out-of-order, oversize frame, error frames |
| Visual | Playwright screenshots over fixed fixtures at fixed `seq` cursors — deterministic because the fold is deterministic |
| Interaction | Testing Library for approval flow, correction flow, composition editing |
| A11y | axe-core in CI; token-level contrast checker; keyboard-only traversal test |
| Perf | §9.4 |
| E2E | Against a real local runtime with a fixture pack, in `hermetic` profile |

**The golden test.** Take a recorded run, replay it through the GUI, and assert the GUI's derived
run summary equals the substrate's own `mhf.trajectory/1` summary for that run. If the UI's fold and
the substrate's trajectory disagree, one of them is wrong, and the test says which fields.

---

## 11. Risk register & gap log

| # | Risk | Impact | Mitigation |
|---|---|---|---|
| R-1 | UI renders an inference as a fact | Wrong engineering decisions; erodes the substrate's core honesty claim | L-3 texture rule + provenance lint (G-3) + golden test |
| R-2 | Composition canvas grows conditionals and becomes the refused workflow engine | Architectural refusal violated | Explicit refusal guard in §4.3; ADR required; no execute affordance |
| R-3 | Arena produces p-values without preregistration | Statistically worthless claims that look authoritative | Prereg required before p-value display; `lab/bench.py` is the only arbiter |
| R-4 | Backend gaps (§7) block half the surfaces | Beta slips | Every gap has a fixture-backed mock so the surface can be built and tested before the wire exists |
| R-5 | Performance collapses at real corpus sizes | Tool becomes unusable exactly when it matters | Budgets as CI tests from sprint 1, not sprint 6 |
| R-6 | GUI and CLI drift | Two truths | Shared `client-core`; any divergent behavior is a bug in one shared module |
| R-7 | Untrusted content rendered unsafely | Injection / exfiltration | Strict CSP, text-only rendering, quarantined transcript blocks |
| R-8 | Studio scope creep into substrate features | TCB pressure | The GUI may not implement anything the substrate should own; §12 gate reviews |

---

## 12. Implementation plan

The plan is capability-gated, not calendar-authorized. Estimates support staffing; they do not open
substrate milestones. Every increment first works against canonical fixtures, then against a real
runtime only when the required command and milestone are authorized.

### UI-0 — Contract and benchmark spike

**Goal:** retire the highest-risk assumptions before choosing the shell or renderer.

| Task | Sub-tasks | Deliverable |
|---|---|---|
| U0.1 Contract inventory | generated schemas, `client-core` ownership, event/source taxonomy, unknown-kind behavior | signed interface matrix |
| U0.2 Attach proof | snapshot-plus-tail fixture, reconnect, duplicate and gap tests | zero-gap attach test |
| U0.3 Renderer bake-off | React Flow/Sigma/ECharts on representative 10k/100k shapes, graph→table parity | benchmark decision record |
| U0.4 Shell bake-off | browser gateway vs Tauri: UDS, CSP, packaging, accessibility, update and footprint | measured shell recommendation |
| U0.5 Threat/perf model | reference hardware, datasets, redaction, cache deletion/rebuild | accepted pilot budgets |

**Gate U0 — “We know what we are building.”** No production scaffold begins until ownership,
capability discovery, attachment consistency, renderer, and shell decisions have evidence.

### UI-1 — Fixture spine
**Goal:** canonical fixtures on screen, deterministic and fast.

| Task | Sub-tasks | Deliverable |
|---|---|---|
| S1.1 Scaffold | selected UI shell, Vite, TS strict, workspace peer, tokens, both themes | fixture app boots |
| S1.2 Transport | `FeedTransport`, generated readers, capability fixture, reconnect/gap semantics | transport tests incl. duplicate/out-of-order/oversize |
| S1.3 Projection cache | bounded chunks, interning where measured, lazy parse, disposable checkpoints | 100k fixture meets accepted budget |
| S1.4 Ingest worker | parse + validate + intern off-thread, Comlink, rAF coalescing | 5k events/s sustained, no dropped frames |
| S1.5 Fold engine | reducer skeleton, snapshots, structural sharing, unknown-kind bucket | Fold determinism test green |
| S1.6 Perf harness | fixture generator, Playwright bench, baseline JSON, CI job | Baseline committed |

**Gate U1 — "It replays."** A recorded run renders in a virtualized tape, has keyboard and table
equivalents, and rebuilds the same projection after cache deletion.

**Complexity note — the bounded-cache boundary.** The subtle part is eviction. When a row leaves the
cache, any checkpoint referencing it must remain valid. Checkpoints store folded state, never raw
row references; evicted raw data is fetched again through a canonical cursor. Write this test first.

### UI-2 — Live Run Theatre
**Goal:** the primary surface, complete, including approvals.

| Task | Sub-tasks | Deliverable |
|---|---|---|
| S2.1 Run fold | turns, invocations, additive cost conservation, status machine | `run.ts`, `turns.ts` + fixture tests |
| S2.2 Turn spine | virtualized tree, sequential-only assertion, cost rollup | Component + a11y pass |
| S2.3 Transcript | virtualized rows over typed arrays, kind filters, `/` query, quarantined untrusted blocks | Component + injection-safety test |
| S2.4 Ledger tape | canvas density strip, scrub → refold, live/behind indicator | < 50 ms p95 backward scrub |
| S2.5 Approvals | suspend detection at F-08, approval sheet, descriptor + selector + budget delta, signed resolve | Round-trip against local runtime |
| S2.6 Corrections | `RecordCorrection` flow, correction provenance in transcript | Round-trip |
| S2.7 Error states | disconnected, empty, partial, behind, contradictory | All five designed + implemented (G-8) |

**Gate U2 — "It operates."** An operator can run, watch, approve, correct, cancel, checkpoint
and resume a real coding run entirely from the GUI, and the GUI's summary matches the trajectory.

**Complexity note — approval must not race.** The suspend happens before the lease opens; a GUI that
optimistically renders "approved" before the receipt lands can desynchronize an operator's mental
model from the kernel's. Approvals are strictly pessimistic: no optimistic UI, receipt-gated only.

### UI-3 — Evidence and effect microscope
**Goal:** see the kernel and the proof.

| Task | Sub-tasks | Deliverable |
|---|---|---|
| S3.1 Effect Inspector | 13-stage rail, per-stage state, failure codes, lease bracket, grant-binding diff | Surface ⌘4 |
| S3.2 Undeterminable handling | intent-without-outcome detection, `signal.void` rendering, staleness finding | F-22 conformance test |
| S3.3 Canonical viewer | JCS canonical form, digest, raw↔canonical byte diff (worker) | Component |
| S3.4 Trajectory viewer | span tree + benchmark-selected waterfall, linked selection, gap markers, `MIN_PX` rule | Surface ⌘5 within U0 budget |
| S3.5 Evidence grid | four-valued auditor states, artifact links, no-green-without-proof rule | Surface ⌘5 part 2 (flagged) |
| S3.6 Verdict inspector | signature display + verification result, `unattributable_for_promotion` badge | Component |

**Gate U3 — "It proves what exists."** For any recorded run, the GUI shows the available effect
story without fabricating missing per-stage telemetry, plus the complete trajectory and evidence
grid. Any proposed new telemetry follows §B-4.

**Complexity note — the waterfall is the hard render.** Nested-span layout with correct depth,
overlap, and sub-pixel handling is where comparable tools visibly break. Build the layout as a pure
function `spans → {x,y,w,h,depth}[]` with its own unit tests, entirely separate from the renderer.
Then the renderer is trivial and the layout is testable.

### UI-4 — Composition Studio and Substrate Map
**Goal:** author and understand the system, not just watch it.

| Task | Sub-tasks | Deliverable |
|---|---|---|
| S4.1 Registry view | plugin catalog, SPI slots, versions, `capabilities()`, isolation mode, lifecycle FSM | Surface ⌘3 left pane |
| S4.2 Composition graph | static graph editor, slot constraints, schema-driven config forms, refusal guard banner | Surface ⌘3 center |
| S4.3 Identity panel | live `D_H`, field-level digest attribution, stacked `D_H`/`D_R`/`D_X` rows | Surface ⌘3 right |
| S4.4 Capability editor | verbs + selectors, "what this grants" expansion, widening warning | Component |
| S4.5 Freeze chain | manifest → CanonicalManifest → FrozenComposition → ActivationPlan → RunPlan, read-only | Chain view |
| S4.6 Substrate Map | WebGL layered map, live particle flow, boundary assertions, drill-through to code/law/ADR | Surface ⌘2 |

**Gate U4 — "It composes without becoming authority."** An operator builds and validates a draft,
receives canonical diagnostics and `D_H` from the backend, and can only freeze/launch through the
same authorized commands as the CLI.

**Complexity note — digest attribution.** "Which field changed `D_H`" requires canonicalizing both
versions and diffing the canonical forms, then mapping canonical paths back to UI fields. Build the
path-mapping table explicitly; do not infer it. Requires the `DescribeManifest`/dry-run-freeze
backend gap (§7).

### UI-5 — Controlled comparison
**Goal:** honest comparison of completed or otherwise already-authorized runs.

| Task | Sub-tasks | Deliverable |
|---|---|---|
| S5.1 Run import | select paired completed runs, preserve lineage and per-run cursors | comparison workspace |
| S5.2 Capability gate | disabled matrix fixture; no browser queue or scheduler | M-7/M-8 controls provably absent |
| S5.3 Confound detector | `D_R` diff between arms, red-flag any unintended difference | Blocks a confounded experiment |
| S5.4 Preregistration | prereg record write, immutable binding, p-value gate | No prereg → no p-value |
| S5.5 Paired analysis | 2×2 contingency, McNemar via `lab/bench.py` (not reimplemented), refusal on zero discordant pairs | Result card |
| S5.6 Claude Code arms | black-box (`unobservable`) and shaped-arm result import | both claims labeled correctly |
| S5.7 Analysis views | cross-filtered paired outcomes and uncertainty | accessible chart + table |

**Gate U5 — "It compares."** A preregistered paired comparison reuses `lab/bench.py`, detects `D_R`
confounds, preserves black-box observability limits, and refuses to overstate the result. Launching
parallel runs remains outside this gate.

**Complexity note — the confound detector is the scientific core.** It is tempting to ship the
matrix runner without it. Don't. A matrix runner without a confound detector is a machine for
producing confident wrong conclusions, and it will be believed because it has a nice UI.

### UI-6 — Hardening and passive Watch
**Goal:** make the authorized pilot safe, accessible, measurable, and operable for long sessions.

| Task | Sub-tasks | Deliverable |
|---|---|---|
| S6.1 Watch mode | density token scope, significance filter, health rings, reduced-motion path | Surface ⌘8 |
| S6.2 Detectors | lease imbalance, budget drift, stale intents, signature failure, replay divergence, escalation spike, cost regression, lifecycle stall, containment refusal | 9 pure detectors + tests |
| S6.3 Ledger Explorer | cursor-backed history, bounded cache, optional analytical extract | Surface ⌘7 |
| S6.4 Data-policy rendering | redaction-aware rows, trainability-aware export with stamped manifest | Compliance test |
| S6.5 Future-feature fixtures | read-only graph, topology, retrieval, and promotion fixtures with explicit gates | no M-8+ authority |
| S6.6 Context lab | per-turn context assembly view: budget, prefix-freeze boundary, compaction drops | Component |
| S6.7 Hardening | CSP audit, a11y sweep, perf re-baseline, packaging, docs | Release candidate |

**Gate U6 — "It watches safely."** The Observatory survives an eight-hour authorized sequential
session, identifies seeded observable anomalies, meets WCAG 2.2 AA targets, and exports only
policy-permitted data with a manifest.

### UI-7+ — Deferred capability increments

| Increment | Opens only after | Scope |
|---|---|---|
| Delegation tree | M-6 | mediated spawn/kill-tree inspection and commands already authorized by runtime |
| Concurrent matrix | M-7 Director decision | measured scheduler controls and composite-cursor monitoring |
| Declarative topology/swarm | M-8 | topology authoring lowered by backend; no browser workflow engine |
| Knowledge/second brain | M-9 | governed retrieval, lineage, retention, vector-store benchmark |
| Meta-cognition/improvement | M-10 | proposals, evaluation, rollback, promotion—never silent self-modification |

### Post-beta backlog (not scheduled)
Distributed/remote gateway; multi-operator presence; time-travel *branching* (requires substrate
branch semantics); model-cost forecasting; automated regression-triage agent driving the Observatory's own
query language; VS Code webview embedding of the Theatre.

---

## 13. Open questions for the Director

1. Does the Observatory live at `vanguard/clients/studio/` (workspace peer) or in a separate repo? This
   document assumes the former; it maximizes `client-core` reuse and minimizes contract drift.
2. Is Tauri acceptable as a Rust dependency in this repo's supply chain, or should beta ship as
   browser + Node sidecar only?
3. Arena vs. Claude Code CLI: is the black-box arm publishable, or internal-only? The shaped arm is
   scientifically stronger; the black-box arm is rhetorically stronger. They answer different
   questions.
4. Which of the §7 gaps are acceptable as `read-model` additions (see BACKEND CHANGES) versus
   requiring their own ADRs?
5. Which persistent caches are permitted by each data-policy class? Any second-brain corpus remains
   in scope for retention, redaction, deletion, tenancy, and trainability from day one.

---

# BACKEND CHANGES

This chapter proposes how the backend evolves to serve **both** a CLI and a GUI cleanly — decoupled
in code, integrated in contract. The organizing principle:

> **Add read models and streams; do not add UI-shaped endpoints. Every GUI need becomes either a new
> event, a new query over existing events, or a new command — never a special case in the kernel.**

The default integration requires no TCB change. Any exception—especially telemetry—requires measured
need and a Director ADR before implementation.

| Plane | Direction | Semantics |
|---|---|---|
| Query | client → runtime → response | read models, consistent snapshots, artifact metadata; no mutation |
| Command | client → runtime → receipt/events | idempotent intent through existing authority gates |
| Stream | runtime → client | ordered within its declared scope, resumable, explicit lag and gaps |

The UI never calls adapters, stores, evaluators, or the kernel directly. Removing it must leave all
execution behavior unchanged.

## B-1. The client-facing seam: one service, two clients (already true — make it explicit)

`RuntimeService` + `RuntimeServer` (UDS/NDJSON) is already the seam, and `client-core` is already the
shared client. The change is *policy*, not code:

- **Declare** in `docs/05_contracts/` that `runtime-service.schema.json` is the sole client contract,
  and that CLI and GUI are peer clients with no privileged path.
- **Forbid** the legacy Studio HTTP server (`runtime/studio/server.py`) from being a second, divergent API.
  Retire its hand-typed `/api/status` and either delete it or reduce it to a static asset server that
  proxies the same NDJSON contract over SSE.

**Why this matters:** two clients over one contract is the configuration in which contract violations
are caught immediately. Two clients over two contracts is how systems acquire two truths.

## B-2. Read models: `ListRuns`, `DescribeRun`, `GetComposition`, `DescribeRegistry`

Add only the **read-only, projection-backed** commands that existing calls cannot supply. They are
projections over the ledger, not new authority:

```
ListRuns        { filter?: {status, since, packRef, tag}, limit, cursor }
                → [{ runId, status, startedAt, endedAt, packRef, D_H, D_R, cost, verdict }]

DescribeRun     { runId }
                → { manifestRef, composition: {D_H, slots[], capabilities[]},
                    activation: {profile, adapters[], D_R}, plan: {...},
                    counts: {turns, invocations, effects, denials, undeterminable} }

GetComposition  { manifestRef | inlineManifest }
                → { canonicalManifest, D_H, frozen: bool, activationPlan?, runPlan?,
                    diagnostics: [{path, severity, message}] }

DescribeRegistry { }
                → [{ ref, spiSlot, version, spiVersion, capabilities[], isolation,
                     lifecycleState, lastTransitionEventId }]
```

**Design constraints.**
- All four are pure reads. They MUST NOT mutate, activate, or execute anything.
- `GetComposition` on an inline manifest is a **dry-run freeze**: it canonicalizes and computes `D_H`
  *without* producing a `FrozenComposition` that anything can run. This is what powers the live
  identity panel. It must be impossible for a dry-run result to be mistaken for a real freeze — give
  it a distinct type and no activation affordance.
- Projections are rebuilt from events, so they inherit replay correctness for free. A projection that
  cannot be rebuilt from the ledger is not permitted (it would be state outside the ledger, which is
  exactly what A-3 forbids).

**Non-refactoring path:** these live in `runtime/service/` beside the existing commands, backed by a
new `runtime/projections/` module that folds the same events the ledger stores. Zero kernel change.

## B-3. Multiplexed event subscription

Today `StreamEvents` is effectively run-scoped. Swarm and Watch need many runs on one connection.

```
StreamEvents { scope: "run", runId, afterSeq }                    # existing behavior, unchanged
StreamEvents { scope: "runs", runIds[], afterCursor }             # new: multiplexed
StreamEvents { scope: "global", kinds?[], afterCursor }           # new: governance/evolution scopes
```

**Cursor semantics.** Per-run `seq` remains the canonical order *within* a run — that is law and does
not change. A multiplexed subscription therefore carries a **composite cursor** (`{runId: seq}` map),
not a global sequence number. Inventing a global sequence would fabricate a cross-run total order the
system does not actually have, which is precisely the kind of convenient fiction the invariants are
written against.

**Flow control.** Add a `flow` frame so the server can tell the client it is behind and the client can
request slowdown:

```
{ frameType: "flow", lag: { runId, pendingEvents, oldestPendingSeq }, advice: "slow"|"ok" }
```

This lets the GUI display `behind (N)` truthfully instead of silently dropping (L-2/L-3), and gives
the server a principled place to shed load.

First add the smaller correctness primitive: `AttachRun` returns a snapshot, the exact cursor
through which it was folded, and a tail token. This closes the query/stream race for CLI and GUI.
Multiplexing remains deferred until M-7 authorizes its consumer use case.

## B-4. Per-stage effect telemetry (S0–S12)

The Effect Inspector wants stage timings, but that desire is not evidence for changing the TCB.
First derive what existing effect, reconciliation, trace, and receipt records prove; render the rest
as unavailable; and measure whether missing detail blocks diagnosis. Only then consider an ADR for a
**stage-observer hook** emitting a
single `EffectStagesRecorded` event at S12 with a fixed-size array of stage durations:

```
payload: { kind: "EffectStagesRecorded", descriptor, stages: [{s: "S0", us: 12}, …],
           terminalStage: "S12" | "S5" | …, failure?: "F-05" }
```

**Constraints.**
- One event per effect, appended at S12 alongside the outcome — **not** thirteen events, which would
  multiply ledger volume by an order of magnitude for observability's sake.
- Recording is a measurement of the pipeline, not a participant in it: the observer receives
  timestamps, cannot alter control flow, and cannot fail the effect. If recording throws, it is
  dropped and counted; an observability bug must never become an availability bug.
- Off by default; enabled per-run via the run plan. The stage-observer's enabled state enters `D_R`
  if and only if it can affect behavior — and it is designed so it cannot, so it should not.

**Decision: deferred by default.** If evidence justifies it, prove capture cannot alter authorization,
ordering, availability, determinism, or the TCB budget, mutation-test the no-op path, and allocate
the event kind before implementation. Observability must not become availability.

## B-5. Lease lifecycle events

First inventory whether existing events and projections already prove reserve/commit/release. If a
material transition is unobservable, emitting it as a first-class event
(`LeaseReserved`, `LeaseCommitted`, `LeaseReleased`, with `leaseId`, `parentLease`, reserved vs.
actual) makes budget conservation *checkable by any client* rather than only by the Governor's own
internal state — and makes the lease-bracket render and the leak detector possible.

This also strengthens the substrate independent of the GUI: a leaked lease currently has no ledger
footprint, which means cold continuation must reconstruct it rather than read it.

## B-6. `VerifyReplay` command

Replay parity (I-4) is currently a procedure. Make it a command:

```
VerifyReplay { runId, mode: "fresh-process" }
  → { parity: true|false, divergences: [{seq, field, recorded, replayed}], replayDigest, recordedDigest }
```

The command spawns the existing fresh-process replay path and returns a structured diff. It must
remain a *fresh process* — an in-memory double fold does not prove replay parity, and the SPEC says
so explicitly. Exposing it as a command is what turns "we believe replay works" into "the operator
pressed the button and it was green at 14:22."

## B-7. Evidence auditor as a queryable projection

The M-4 canonical auditor's four-valued output (`absent` / `invalid` / `unverifiable` /
`present_valid`) should be exposed as:

```
DescribeEvidence { runId | preregRef } → { rows: [{ line, state, sourceArtifact, reason }], eligible: bool }
```

with the eligibility rule computed by the auditor, not by the client. **The GUI must never compute
promotion eligibility.** If the client can compute it, the client can get it wrong, and a green badge
in a GUI is more persuasive than a correct answer in a log.

## B-8. Arena/experiment support

- **Preregistration write path**: a command to record a preregistration and return its immutable
  reference, so the Arena binds results to a hypothesis stated beforehand.
- **`D_R` diff service**: given two activation plans, return the component-level differences. This
  powers the confound detector and belongs in the backend because `D_R` composition is backend
  knowledge.
- **Exterior-arm harness**: a sandbox adapter profile for running a third-party CLI (e.g. Claude Code)
  as an exterior process under identical containment, capturing only inputs, workspace diff, and
  oracle verdict — with the trajectory explicitly marked `unobservable` rather than empty. This is a
  new *adapter*, which is exactly the asymmetric-evolution path A-6 prescribes: no new authority verb,
  no TCB change.
- **Bench as a service**: expose `lab/bench.py`'s McNemar computation through a command so the GUI
  never reimplements the statistics. One implementation of the arbiter, in Python, tested.

## B-9. Structured artifact & context introspection

- `ExplainArtifact` exists; extend lineage only where it is canonical. Add authorized
  `ReadArtifactRange {artifactId, offset, length}` with content length, digest, media type, redaction
  result, and stable range semantics. Policy and redaction apply before bytes cross the wire.
- Add `DescribeContext { runId, turn }` returning what the `IContextAssembler` actually assembled:
  included chunks with token counts, the prefix-freeze boundary, compaction decisions and what was
  dropped. This is high-value for context engineering and currently invisible.

## B-10. Wire hygiene and schema discipline

- Every new command/frame/event above lands **schema-first** in `schemas/v4/` with golden vectors, and
  TS/Python readers are regenerated (A-4, I-8). No handwritten mirrors on either side.
- New event kinds must be additive; clients preserve unknown kinds (CT-44), which is what allows the
  backend to ship new events before the GUI understands them.
- Version the frame contract explicitly: keep `version: "vg.4"` and negotiate capabilities per
  connection (`Hello`/`Welcome` frames listing commands, event kinds, projections, limits, and
  `disabled`/`read`/`command` feature modes), so an old CLI and a new GUI can
  share one daemon. This is the single cheapest change that prevents a lockstep-upgrade requirement
  between clients and runtime.

## B-11. What the backend should explicitly NOT do for the GUI

Stated so it does not happen by accident:

- **No UI-shaped endpoints.** No `GetDashboard`, no `GetTimelineForRender`. The backend serves events
  and projections; layout is the client's problem.
- **No push of derived presentation state.** Colors, groupings, and severity ranking are client
  concerns. The backend emits facts and, where genuinely semantic, classifications — never styling.
- **No workflow/topology engine** to satisfy the composition canvas. M-8 topology is declared
  component/policy data lowered to ordinary scheduling and mediated spawn; a substrate workflow engine
  requires RF-66 reversal evidence and a successor ADR. The canvas authors static data. Full stop.
- **No relaxation of the operator-signature requirement** to make GUI approvals smoother. A GUI is not
  a reason to weaken I-5 or the approval flow.
- **No second runtime path for "GUI mode."** One runtime, one dispatcher, one turn loop. The GUI is a
  client.
- **No global cross-run sequence number.** See B-3.

## B-12. Migration sequencing (backend, mapped to frontend sprints)

| Backend item | Needed by | ADR? | Risk |
|---|---|---|---|
| B-10 capability negotiation | UI-0/1 | yes (wire) | low |
| Snapshot-plus-tail `AttachRun` | UI-0/2 | yes (wire semantics) | medium |
| B-1 contract declaration + studio retirement | UI-1 | doc/cleanup decision | low |
| B-2 `ListRuns` / `DescribeRun` | UI-2 | yes | low |
| B-6 `VerifyReplay`; B-7 `DescribeEvidence` | UI-3 | yes | low |
| B-9 artifact range/redaction | UI-3 | yes (security) | medium |
| B-5 lease events, only after gap proof | UI-3 | yes | medium |
| B-4 stage telemetry, only after measurement | post-UI-3 | yes (TCB-adjacent) | high |
| B-2 composition preview / registry | UI-4 | yes | medium |
| B-8 prereg + canonical `D_R` diff + bench service | UI-5 | yes | medium |
| B-3 multiplexed stream + flow | M-7/UI-7+ | Director ADR | medium |
| B-9 governed knowledge introspection | M-9/UI-7+ | Director ADR | medium/high |

**Sequencing rule:** the frontend never blocks on the backend. Each gap ships first as a
fixture-backed mock behind a flag; when the real command lands, the mock is deleted and the same
tests run against the wire. That is what "decoupled but well integrated" means operationally.

---

## Appendix A — Sources consulted

Repository (primary):
[`docs/SPEC.md`](../../SPEC.md), [`docs/01_law/DISPATCH.md`](../../01_law/DISPATCH.md),
[`docs/01_law/RUNTIME.md`](../../01_law/RUNTIME.md),
[`docs/01_law/EXTENSIBILITY.md`](../../01_law/EXTENSIBILITY.md),
[`schemas/v4/`](../../../schemas/v4/), [`schemas/mhf/`](../../../schemas/mhf/),
[`vanguard/clients/client-core/`](../../../vanguard/clients/client-core/),
[`vanguard/clients/cli/`](../../../vanguard/clients/cli/),
[`vanguard/packages/runtime/service/`](../../../vanguard/packages/runtime/service/),
[`vanguard/packages/runtime/studio/`](../../../vanguard/packages/runtime/studio/),
[`packs/code-default/harness.yaml`](../../../packs/code-default/harness.yaml),
[`lab/bench.py`](../../../lab/bench.py),
[`tools/substrate_visualizer/`](../../../tools/substrate_visualizer/).

External primary technical sources:

- [React Flow performance guidance](https://reactflow.dev/learn/advanced-use/performance) — memoized
  components, narrow subscriptions, collapsed subgraphs, and simple styles for bounded editors.
- [Sigma.js documentation](https://www.sigmajs.org/docs/) and
  [performance notes](https://v4.sigmajs.org/how-to/technical/performance/) — WebGL rendering and
  measurement guidance for large read-only graphs.
- [TanStack Virtual introduction](https://tanstack.com/virtual/latest/docs/introduction) — headless
  row/column virtualization without imposing markup.
- [DuckDB-Wasm overview](https://duckdb.org/docs/stable/clients/wasm/overview) — in-browser analytical
  SQL and supported formats; its default single-threaded/browser-memory constraints motivate bounded
  extracts rather than a canonical browser store.
- [Apache ECharts features](https://echarts.apache.org/en/feature.html) — progressive and streaming
  rendering capabilities for operational plots.
- [OpenTelemetry semantic conventions](https://opentelemetry.io/docs/specs/semconv/) — an export
  interoperability target, not a replacement for AETHER's richer canonical event envelope.
- [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) — normative accessibility target.

**Research decisions.** Adopt maintained, specialized renderers before custom GPU code; virtualize
long semantic lists; keep analytical engines bounded and optional; expose every graph through an
accessible table; and treat OpenTelemetry as an exterior export mapping. Reject trend-blog claims as
architecture evidence, reject server-rendered/RSC complexity for this local event-fold client, and
reject any browser database as canonical truth. The unresolved React Flow/Sigma/Canvas crossover and
browser/Tauri shell decision are deliberately converted into UI-0 benchmarks rather than opinions.

## Appendix B — Decision summary

| Decision | Final position | Why |
|---|---|---|
| Product role | Observatory and peer client, never second runtime | preserves one authority |
| State | canonical folds/queries plus disposable local UI state | replayable without ledgering pixels |
| Attach | snapshot-plus-tail | closes the query/stream race |
| Feature exposure | capability discovery AND milestone gate | compatibility cannot mint authority |
| Graph stack | React Flow editor + Sigma viewer; custom only after proof | best maintainability/performance split |
| Local data | bounded IndexedDB; optional DuckDB-Wasm extracts | rebuildable and honest about browser limits |
| Experiments | preregistered, canonical `D_R` confound detection, reuse `lab/bench.py` | scientific claims remain attributable |
| Accessibility | WCAG 2.2 AA and graph→table parity | perception is part of correctness |
| Backend evolution | query/command/stream contracts, range-safe artifacts | decoupled clients without UI-shaped APIs |
| Roadmap | UI-0 through UI-6 now; UI-7+ bound to M-6–M-10 | no roadmap inversion |
