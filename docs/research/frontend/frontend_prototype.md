---
id: research.frontend-prototype
kind: research
status: experiment
authority: non-canonical
summary: "Exploratory research and pilot architecture for AETHER Observatory frontend prototype."
topic:
  - frontend
---

# AETHER Observatory — Frontend Prototype and Pilot Architecture

> [!IMPORTANT]
> This is an archived, non-authorizing research and implementation blueprint. It does not open M-5,
> M-6, M-7, M-8, retrieval, swarms, or meta-cognition. Current authority remains in `docs/SPEC.md`,
> accepted ADRs, and `docs/03_execution/sprint_active.md`.

## 1. Executive decision

Build the frontend prototype as an **observatory and control client**, not as another agent runtime.
Its purpose is to make the existing AETHER/Vanguard substrate visible, testable, comparable, and
composable without moving authority into the browser.

The prototype should let an engineer understand a run at five levels:

1. what was configured;
2. what authority was granted or denied;
3. what the agent and tools actually did;
4. how immutable events reduced into state and evidence;
5. why the exterior evaluator accepted, rejected, or could not verify the result.

The long-term pilot may become a visual harness laboratory for coding agents, researchers, general
task solvers, mediated agent teams, scientific benchmarks, retrieval, context engineering, and
governed self-improvement. The first implementation must remain intentionally smaller:

- replay deterministic fixture runs;
- attach to one live sequential run;
- inspect events, state, budgets, capabilities, plugins, composition, and evidence;
- create and validate a draft composition;
- compare two recorded runs over the same task/model/environment tuple;
- issue only existing authenticated runtime commands;
- demonstrate that the browser can be deleted without changing execution semantics.

The product name used in this report is **AETHER Observatory**. “Studio” is acceptable internally,
but the existing `vanguard/packages/runtime/studio/` static prototype should not become the new
architecture by accretion.

## 2. Product thesis

The frontend is a scientific instrument for the meta-framework.

```text
Compose -> Validate -> Run -> Observe -> Explain -> Compare -> Falsify -> Improve
```

It should answer questions that are currently expensive to answer from logs:

- Which manifest, profile, model route, plugins, bindings, selectors, and budgets defined this run?
- Which component was active at each point in time?
- Which event caused this state transition?
- Which effect crossed the kernel and which grant authorized it?
- What data entered model context, what was compacted, and what was retrieved later?
- Which operation consumed time, tokens, money, memory, or retries?
- Was a cache hit valid, stale, or bypassed?
- Did an MCP server receive only the authority intended for it?
- Which evidence row failed, and which canonical source would be needed to close it?
- Why did two harnesses using the same model diverge?
- Is a proposed workflow faster because of better context, tools, scheduling, or evaluator leakage?
- Can the complete UI projection be rebuilt from the ledger and blob references?

The frontend is successful when it reduces time-to-understanding without becoming a source of truth.

## 3. Scope boundaries

### 3.1 Prototype scope

The prototype includes:

- run catalog and launch form;
- live/replay event stream;
- run timeline and causal trace graph;
- reducer-derived state inspector;
- composition and plugin dependency graph;
- kernel dispatch stage inspector;
- capability, selector, grant, lease, budget, approval, and effect views;
- agent-loop and context-layer views;
- evidence and evaluator panels;
- log, metric, cost, latency, and cache dashboards;
- two-run experiment comparison;
- draft workflow/harness canvas that compiles to existing manifest contracts;
- read-only “second brain” graph prototype over artifacts, claims, citations, and relations;
- responsive desktop layout and keyboard-accessible core inspection paths.

### 3.2 Explicit non-goals

The prototype must not:

- implement a browser-side kernel, reducer authority, evaluator, scheduler, or grant issuer;
- append ledger events directly;
- edit WAL or evidence artifacts;
- infer success from attractive visuals;
- enable `agent.spawn`, concurrency, swarms, or topologies before their gates;
- expose private hidden chain-of-thought;
- treat an index, cache, graph layout, or browser database as canonical truth;
- import `vanguard/packages` from the GUI;
- bypass `@vanguard/client-core` or the VG-04 wire contract;
- build a second manifest dialect;
- make autonomous self-modification a UI toggle.

### 3.3 Feature flags by milestone

| Capability | Prototype state | Authority gate |
|---|---|---|
| Fixture replay | Enabled | Existing client contracts |
| One live sequential run | Enabled | Existing runtime service |
| Draft composition editor | Enabled, validate/preview only | Existing manifest schema/compiler |
| Operator approval | Enabled through signed command path | Existing governance authority |
| Two-run comparison | Enabled for completed or live sequential runs | Measurement only |
| M7-01 effect independence overlay | Enabled after measurement schema lands | ADR-0092 measurement scope |
| Child-agent tree | Fixture/read-only until M-6 | M-6 closure |
| Concurrent execution controls | Disabled | Explicit M-7 ADR |
| Swarm/topology execution | Disabled | M-8 closure |
| Retrieval laboratory | Read-only/mock projection | M-9 authorization |
| Self-improvement/promotion | Simulation only | M-10 governance |

## 4. Architecture principles

### 4.1 The GUI is a skin over client-core

The existing `vanguard/clients/client-core/` package is the correct seam. It already provides:

- VG-04 parsing and typed contracts;
- live, replay, and scenario adapters;
- resumable event subscription;
- run-view reducers and selectors;
- trace-graph projection;
- approval signing;
- command and receipt handling.

The future GUI should be another workspace client, for example:

```text
vanguard/clients/
  client-core/       # headless shared TypeScript client/application layer
  cli/               # Ink skin
  observatory/       # React browser/desktop skin
```

Neither CLI nor Observatory may import Python production packages. Both consume the same client
ports and wire frames. A behavior that exists only in one skin is presentation behavior, not runtime
semantics.

### 4.2 Commands and events are different channels

```text
GUI intent
  -> typed command
  -> runtime inbox/idempotency
  -> authorization and execution
  -> command receipt
  -> canonical events
  -> client projection
  -> pixels
```

The frontend never assumes that a successful HTTP/UDS send means the operation occurred. It renders
command receipt state separately from effect settlement and ledger truth.

### 4.3 Every screen is a projection

All visual state must declare its source:

- `live`: derived from a verified ordered stream;
- `replay`: rebuilt from a stored fixture or event range;
- `draft`: local uncommitted composition state;
- `derived`: calculated from canonical events/artifacts;
- `unknown`: missing or unsupported evidence.

The source badge is always visible. No view may silently mix lineages or live and fixture data.

### 4.4 Progressive disclosure

The interface must be understandable at three depths:

- **Overview:** run status, objective, active phase, major costs, failures, and evidence.
- **Engineering:** events, plugins, capabilities, context, effects, and timings.
- **Forensics:** raw canonical frame, hashes, signatures, causation, reducer before/after, and blob
  references.

This keeps the design minimal without hiding rigor.

## 5. Visual model of the substrate

### 5.1 Five separation lenses

“Five separation lenses” is a proposed explanatory model for the UI, not a new normative layering
claim. It makes the separability thesis inspectable:

| Lens | What it shows | What it must not do |
|---|---|---|
| Intent/Solution | Task, plan, artifacts, claims, expected result | Pretend an answer proves its execution |
| Agent/Agency | Turns, model calls, context, proposals, child lineage | Mint capabilities or judge itself |
| Execution/Effects | Kernel stages, grants, selectors, tools, MCP, sandbox receipts | Hide denied or undeterminable effects |
| State/Evidence | Ledger, reducers, trajectory, provenance, costs, checkpoints | Mutate history or trust asserted booleans |
| Evaluation/Governance | Approvals, evaluator isolation, oracle, verdict, promotion status | Accept agent-authored judgment |

The same run can be viewed through any lens while retaining one shared event cursor.

### 5.2 Hexagonal lattice view

Render the canonical dependency lattice:

```text
domain <- ports <- kernel <- agency <- runtime -> adapters
                                      |
                                   clients
```

Clicking a subsystem opens:

- responsibility statement;
- allowed and forbidden imports;
- active components;
- relevant requirements/ADRs;
- events produced or consumed;
- ports implemented;
- test and falsifier coverage;
- current LOC/budget metrics where applicable.

Boundary violations should be shown from linter output, never inferred solely by the browser.

### 5.3 Kernel dispatch microscope

Provide a horizontal S0–S12 view. For a selected effect, each stage shows:

- input descriptor digest;
- classifier result and sink class;
- selector and resolved resource;
- capability/grant match;
- budget reservation and lease;
- policy/approval decision;
- durable intent event;
- adapter invocation;
- receipt/reconciliation;
- terminal event and provenance edge.

Colors communicate status, but never alone:

- neutral: not reached;
- blue: observed/processing;
- green plus check icon: verified;
- amber plus diamond: pending/unknown;
- red plus stop icon: denied/failed;
- violet plus signature icon: externally verified.

### 5.4 Agent-loop engineering view

Show the loop as a time-aligned sequence rather than decorative animation:

```text
observe -> compile context -> model -> proposal -> authorize -> effect -> receipt -> evaluate
```

Each turn expands into:

- context layers and token contribution;
- prompt/model/provider identity;
- tool schemas exposed;
- proposal payload and validation;
- dispatch/effect spans;
- observations returned;
- compaction or checkpoint boundary;
- cost and latency breakdown;
- stop or continuation reason.

The interface may display model-provided reasoning summaries if the provider returns them and policy
permits storage. It must label them as model output, not ground truth, and must not imply access to
hidden chain-of-thought.

## 6. Information architecture

### 6.1 Global shell

Desktop layout:

```text
+--------------------------------------------------------------------------------+
| AETHER | Project / Run | LIVE seq 184 | profile | model | budget | command bar |
+---------------+------------------------------------------------+---------------+
| Navigation    | Primary workspace                              | Inspector     |
| Runs          | timeline / graph / canvas / comparison         | selected fact |
| Compose       |                                                | raw/evidence  |
| Plugins       |                                                | provenance    |
| Experiments   |                                                | actions       |
| Knowledge     |                                                |               |
| System        |                                                |               |
+---------------+------------------------------------------------+---------------+
| Event scrubber | stream health | cursor | dropped=0 | reconnect | diagnostics  |
+--------------------------------------------------------------------------------+
```

The inspector is contextual and collapsible. The bottom scrubber is global so selecting an event
updates every visible projection to the same sequence.

### 6.2 Primary routes

| Route | Purpose |
|---|---|
| `/runs` | Search, filter, resume, compare, and inspect runs |
| `/runs/:id/overview` | Outcome, status, evidence, active phase, cost, critical path |
| `/runs/:id/timeline` | Virtualized event and span timeline |
| `/runs/:id/trace` | Causal/provenance DAG |
| `/runs/:id/loop` | Turn/context/model/tool loop |
| `/runs/:id/kernel` | S0–S12 effect microscope |
| `/runs/:id/state` | Reducer state and before/after diffs |
| `/runs/:id/evidence` | Nine-row/general evidence, signatures, sources |
| `/compose` | Draft manifest and harness canvas |
| `/plugins` | Catalog, dependency graph, ports, lifecycle, configuration |
| `/experiments` | Paired run definitions and analysis |
| `/knowledge` | Artifacts, sources, claims, citations, semantic relations |
| `/system` | Runtime profiles, stores, evaluator, sandbox, health, linter gates |

### 6.3 Command palette

The command palette is the fastest interaction surface. Example actions:

- attach to run;
- jump to sequence/event/effect;
- replay from fixture;
- compare with another run;
- show why artifact is active;
- validate draft composition;
- request run start/cancel/checkpoint;
- open pending approval;
- filter to errors, denials, cache misses, or model calls;
- copy stable deep link to selected evidence.

Every mutating command shows actor, target, selector, risk, expected receipt, and whether approval is
required before submission.

## 7. Core workbenches

### 7.1 Run Observatory

The overview page should answer “what is happening?” in under five seconds:

- status and termination reason;
- objective and domain pack;
- composition/run/environment digests;
- active model and route;
- current turn and latest effect;
- token, cost, wall-clock, tool-time, and evaluator-time totals;
- budget remaining by dimension;
- pending approval/reconciliation;
- evidence completeness;
- containment and evaluator identity;
- anomalies and performance regressions.

### 7.2 Event Explorer

Requirements:

- virtualized rows;
- cursor pagination by immutable sequence;
- live tail with pause and deterministic catch-up;
- filters by kind, principal, episode, span, plugin, tool, sink, status, and time;
- column presets for operator, performance, security, and research modes;
- structured payload diff;
- raw canonical JSON with digest verification;
- causation/parent links;
- bookmark and shareable URL state;
- export selected event range without altering source data.

Pseudocode:

```ts
type EventWindowState = {
  runId: string;
  afterSeq: bigint;
  items: readonly EventEnvelope[];
  paused: boolean;
  source: "live" | "replay";
};

async function followRun(client: RuntimeClient, state: EventWindowState) {
  await subscribeRun(
    client,
    { runId: state.runId, afterSeq: state.afterSeq.toString() },
    {
      onItem(item) {
        assertMonotonic(item.envelope.seq, state.afterSeq);
        eventWorker.postMessage({ type: "append", item });
      },
      onError(error) { connectionStore.report(error); },
      onDone() { connectionStore.markClosed(); },
    },
  );
}
```

### 7.3 Causal Trace and Provenance Graph

Use two renderers with a shared graph model:

- React Flow for editable, human-scale composition/workflow diagrams;
- Sigma.js/WebGL for large read-only event, artifact, citation, or provenance graphs.

Never attempt to render every event as a DOM node. Collapse by run, episode, turn, effect, plugin,
or artifact and expand on demand. Graph layout runs in a Web Worker and is cached by graph digest.

Node classes:

- run, episode, turn, event;
- model invocation;
- effect and receipt;
- grant, lease, approval;
- plugin/component;
- artifact/blob;
- claim/source/citation;
- evaluator request/verdict;
- child agent after M-6.

Edge classes:

- causation;
- parent/child;
- produced/consumed;
- authorized-by;
- evaluated-by;
- derived-from;
- cites/supports/contradicts;
- activated-before/retired-after.

### 7.4 Harness Composer

The composer is a schema-backed editor over the existing manifest representation.

It includes:

- component palette from runtime/plugin catalog;
- typed ports and compatibility validation;
- drag-to-connect edges with immediate schema feedback;
- profile, capability, selector, budget, isolation, and entrypoint panels;
- generated canonical JSON/YAML preview;
- digest preview from the backend compiler;
- validation issues linked to the exact field/node;
- differential comparison against another composition;
- save as a local draft or submit through an existing governed command when authorized.

The browser must not calculate authoritative `D_H`. It may calculate a provisional local digest for
UI caching, clearly labeled `draft`; only the backend compiler returns canonical identity.

```ts
interface CompositionGateway {
  catalog(): Promise<Result<ComponentCatalog>>;
  validateDraft(draft: AuthoredManifest): Promise<Result<ValidationReport>>;
  previewComposition(draft: AuthoredManifest): Promise<Result<FrozenCompositionView>>;
}
```

### 7.5 Plugin Laboratory

For each plugin/component show:

- identifier, version, package, digest, source, and status;
- provided and required interfaces;
- configuration schema and effective configuration;
- granted selectors/capabilities;
- isolation mode and process identity;
- lifecycle transitions and cleanup;
- events and metrics attributed to it;
- failures, restarts, cache behavior, and average latency;
- dependency graph and blast radius;
- requirements, ADRs, and tests that govern it.

The prototype can simulate composition changes in memory but cannot hot-install arbitrary code into
a production run.

### 7.6 Experiment Arena

The “agents fighting” concept should be implemented as a scientifically controlled tournament, not
an unstructured swarm.

An experiment definition binds:

- immutable task set and oracle;
- same eligible LLM snapshot/route or declared model factor;
- same budget, environment, tool availability, and evaluator;
- harness A and harness B composition digests;
- seed/randomness policy;
- stopping conditions;
- primary metric and guardrail metrics;
- paired comparison method;
- preregistration digest.

Views:

- side-by-side synchronized timelines;
- divergence point detection;
- tool/context/effect comparison;
- solution diff;
- cost/latency/quality scatter;
- critical-path waterfall;
- evaluator agreement/disagreement;
- paired task outcome matrix;
- confidence intervals and explicit insufficient-power state.

Claude-Code-like and Codex-like coding harnesses should be **behavioral profiles built with Vanguard
primitives**, not copied proprietary internals. They can differ in tool exposure, context loading,
planning, compaction, approval UX, skills, hooks, or delegation while using the same model and
evaluation contract.

### 7.7 Knowledge Observatory / second brain

The Obsidian-like surface is a derived knowledge graph:

- document/source nodes;
- typed artifact nodes;
- claims and evidence spans;
- concepts/entities;
- tasks, decisions, experiments, and results;
- supports, contradicts, refines, supersedes, cites, produced-by, and used-by edges.

Canvas positions, colors, groups, and personal notes are user-interface metadata. They must not
pollute canonical evidence. Graph relations derived by models remain proposals until a deterministic
extractor or human/evaluator confirms them.

Support local spatial canvases, backlinks, saved queries, graph filters, time travel, and “show me
why this node exists.” Retrieval results must link back to immutable source artifacts and spans.

### 7.8 Autonomous Watch Mode

Watch Mode is a monitoring posture, not unlimited permission.

It shows:

- active goals/runs;
- current phase and latest event;
- heartbeat and liveness;
- budgets and exhaustion forecasts;
- approvals waiting;
- open durable intents;
- stalled effects and retries;
- anomaly detection;
- evaluator queue;
- promotion eligibility;
- kill/cancel/checkpoint controls.

The system may propose improvements as structured artifacts. Applying an improvement remains an
explicit governed workflow with experiment, evaluator, approval, and rollback.

## 8. High-performance frontend architecture

### 8.1 Recommended stack

| Concern | Recommendation | Rationale |
|---|---|---|
| Language | TypeScript 5.x strict | Matches client-core and prevents wire-shape drift |
| UI | React 19 + Vite | Existing React expertise; fast prototype/build loop; client-heavy app |
| Routing | TanStack Router or React Router | Typed route state and deep links; benchmark bundle impact before choice |
| Server state | TanStack Query | Cursor queries, cancellation, deduplication, cache policy |
| Local UI state | Zustand with selector subscriptions | Small surface, compatible with React Flow; avoid global rerender storms |
| Event state | Pure client-core reducers + worker-owned append buffer | Keeps authority-free projection deterministic |
| Tables/logs | TanStack Table + TanStack Virtual | Headless, virtualized large datasets |
| Editable graphs | React Flow | Strong node editor ergonomics; memoization and collapsed subgraphs required |
| Large graphs | Sigma.js + Graphology | WebGL graph inspection at thousands/tens of thousands of elements |
| Charts | Apache ECharts, modular imports | Streaming/progressive Canvas charts and large datasets |
| Local analytics | DuckDB-Wasm in a Worker, optional | Ad hoc Arrow/Parquet analysis for bounded downloaded datasets |
| Data interchange | VG-04 JSON frames initially; Arrow/Parquet for bulk derived analytics | Do not replace canonical wire contract for premature speed |
| Schemas | Generated TypeScript + runtime parsers from canonical schemas | Compile-time and boundary validation |
| Styling | CSS variables + CSS Modules or vanilla-extract | Theme tokens without utility-class sprawl |
| Components | Headless accessible primitives | Visual ownership, keyboard semantics, minimal design |
| Testing | Vitest, Testing Library, Playwright, axe-core | Unit, contract, accessibility, E2E, visual regression |
| Profiling | Performance API, React Profiler, Long Tasks, Web Vitals | Measured budgets rather than aesthetic assumptions |

Technology choices are provisional until a thin vertical benchmark proves them. Do not introduce a
frontend meta-framework merely to visualize the backend meta-framework.

### 8.2 Data plane

```text
Runtime UDS/service
   -> transport bridge (desktop/local daemon or authenticated web gateway)
   -> VG-04 frames
   -> parser + sequence verifier
   -> event ingestion Worker
   -> normalized immutable event chunks
   -> pure projections/selectors
   -> virtualized views / WebGL graphs / Canvas charts
```

For a browser, UDS requires a narrow local gateway or desktop shell. The gateway transports bytes,
authenticates the operator, applies origin/CSRF policy, and forwards existing commands. It must not
create new runtime semantics.

### 8.3 Worker topology

Use dedicated Web Workers for:

- event parsing, validation, chunking, and projection;
- graph layout and community aggregation;
- DuckDB-Wasm analytical queries;
- diff/search/index operations over downloaded data;
- optional compression/decompression.

The main thread owns interaction and rendering only. Workers exchange transferable typed arrays,
Arrow batches, or compact structured messages rather than duplicating entire event histories.

```ts
type WorkerRequest =
  | { type: "append-events"; batch: ArrayBuffer }
  | { type: "project-at"; seq: string; views: ViewKind[] }
  | { type: "layout"; graphDigest: string; nodes: NodeInput[]; edges: EdgeInput[] }
  | { type: "query"; sql: string; parameters: unknown[] };

type WorkerResponse =
  | { type: "append-ack"; lastSeq: string; count: number }
  | { type: "projection"; seq: string; digest: string; value: unknown }
  | { type: "layout-result"; graphDigest: string; positions: ArrayBuffer }
  | { type: "query-result"; arrow: ArrayBuffer };
```

### 8.4 Event storage in the browser

Keep only a bounded live window in React-visible memory. Older chunks may be stored in IndexedDB for
session convenience, keyed by run ID, event range, and digest. They remain disposable.

DuckDB-Wasm is appropriate for bounded analytical extracts because it can query Arrow, Parquet,
CSV, and JSON locally. It is not the primary run store: browser memory is limited and DuckDB-Wasm is
single-threaded by default. Server-side cursor queries and pre-aggregated projections remain
necessary for large histories.

### 8.5 Rendering budgets

Initial performance service-level objectives:

| Operation | Target |
|---|---:|
| App shell interactive on reference laptop | < 1.5 s warm, < 3 s cold |
| Live event to visible timeline | p95 < 100 ms at 200 events/s |
| Main-thread long task | none > 50 ms during steady streaming |
| Timeline DOM rows | < 300 including overscan |
| Graph pan/zoom | 60 fps target; never below 30 fps p95 interaction |
| Select event and update linked panels | p95 < 50 ms |
| Filter 100k local event extract | < 250 ms in worker |
| Reconnect and catch up 10k events | < 2 s without duplicate sequence |
| Memory for 100k summarized events | < 250 MB total tab heap |
| Initial JS, compressed | target < 350 KB excluding lazy graph/analytics chunks |

Budgets must be measured in CI on fixed fixtures. A feature that breaches a budget requires evidence,
not a larger budget by default.

### 8.6 React performance rules

- Keep canonical event arrays outside component-local state.
- Subscribe components to minimal selectors, not whole node/event collections.
- Memoize React Flow node types, callbacks, and option objects.
- Collapse large trees and DAG groups by default.
- Use CSS transforms for pan/zoom; avoid layout-triggering animation.
- Avoid shadows, filters, animated gradients, and per-edge DOM labels at scale.
- Lazy-load Sigma, ECharts, Monaco/editor, and DuckDB routes.
- Batch stream updates at animation-frame or bounded time intervals.
- Use `startTransition` only for non-critical projection changes; do not hide data loss.
- Never stringify the full event history on the main thread.

## 9. Clean minimalistic design system

“World champion design” cannot be guaranteed by adjectives. It comes from information hierarchy,
speed, restraint, accessibility, and evidence-rich interaction.

### 9.1 Visual direction

- Dark and light themes based on neutral surfaces, one accent, and semantic status colors.
- Dense but calm: 4/8 px spacing grid, restrained borders, almost no decorative shadows.
- Monospace only for identifiers, code, payloads, sequence, and metrics; humanist sans elsewhere.
- One primary visual question per screen.
- Motion communicates state change; it never decorates idle screens.
- Stable spatial layout during streaming; new events do not make panels jump.
- Raw complexity is available one click away, not forced into the overview.

### 9.2 Design tokens

```ts
type ThemeTokens = {
  color: {
    canvas: string; surface: string; raised: string; text: string; muted: string;
    border: string; accent: string; success: string; warning: string; danger: string;
    unknown: string; verified: string;
  };
  space: { 1: "4px"; 2: "8px"; 3: "12px"; 4: "16px"; 6: "24px"; 8: "32px" };
  radius: { sm: "4px"; md: "8px"; lg: "12px" };
  type: { xs: "11px"; sm: "12px"; md: "14px"; lg: "18px"; xl: "28px" };
};
```

### 9.3 Accessibility

Target WCAG 2.2 AA for the prototype and audit AAA criteria where operational safety benefits.

- Every graph has an equivalent navigable list/table.
- Keyboard navigation supports panels, events, nodes, edges, timeline, and command palette.
- Focus is always visible and never covered.
- Status never depends on color alone.
- Touch/click targets meet WCAG target-size expectations.
- Reduced-motion preference disables animated traversal and streaming transitions.
- Screen readers announce new critical events, not every high-volume event.
- Charts provide tabular data and plain-language summaries.
- Time, cost, token, and uncertainty units are explicit.

## 10. Testing strategy

### 10.1 Contract and projection tests

- Parse every existing CLI fixture through client-core and Observatory.
- Assert CLI and GUI reducers yield equivalent state for the same frame sequence.
- Reject malformed, duplicated, regressed, mixed-run, and unknown-required frames.
- Preserve unknown future events without crashing or inventing meaning.
- Prove reconnect resumes strictly after the last acknowledged sequence.
- Verify every projection can rebuild from sequence zero.

### 10.2 UI tests

- component interaction tests for inspectors, filters, and commands;
- keyboard-only golden paths;
- accessibility scans and manual screen-reader checks;
- deterministic screenshots for key fixture states;
- approval and cancellation safety flows;
- responsive layouts at laptop, ultrawide, and tablet widths;
- no live network in unit or component tests.

### 10.3 Performance tests

Fixtures should include:

- 1k, 10k, 100k, and 1m event histories;
- high-frequency stream bursts;
- deep causation graphs;
- wide plugin graphs;
- large context payload references;
- reconnect with overlapping replay response;
- malformed sequence near the end of a large stream;
- two-run comparison with unequal lengths;
- large knowledge/citation graph.

Automated gates record time-to-interactive, heap, dropped frames, long tasks, interaction latency,
worker query latency, and bundle size.

### 10.4 Security tests

- browser cannot append an event or forge a receipt;
- command replay is idempotent;
- approval signature binds exact challenge;
- XSS payloads in model/tool/source text remain inert;
- blob URLs and source previews enforce content security policy;
- gateway rejects cross-origin command submission;
- secrets are redacted before browser delivery;
- MCP/plugin configuration does not expose secret values;
- deep links cannot change run state;
- exported reports identify redaction and incomplete evidence.

## 11. Development guidelines

1. Start every feature with the user question it answers and the canonical source it projects.
2. Extend `client-core` only for domain-neutral client behavior shared by CLI and GUI.
3. Put coding-specific view models in a coding client module, not the generic core.
4. Never import backend Python modules into TypeScript clients.
5. Generate contract types; do not hand-maintain parallel wire interfaces.
6. Use exhaustive discriminated unions for frames, commands, and view states.
7. Treat `unknown`, `absent`, `invalid`, `unverified`, and `denied` as distinct UI states.
8. Separate command receipt from ledger settlement visually and in code.
9. Keep URL state serializable for investigations and reviews.
10. Profile before optimizing and preserve a benchmark fixture with every performance fix.
11. Keep renderer-specific objects outside domain/client-core models.
12. Every mutation needs confirmation proportional to risk and a visible audit result.
13. Use feature gates from backend capability discovery, never hard-coded milestone assumptions.
14. Do not expose experimental features as if operationally authorized.
15. Prefer deletion and composable primitives over screen-specific infrastructure.

Suggested frontend module structure:

```text
vanguard/clients/observatory/
  src/
    app/                 # router, shell, providers, feature gates
    contracts/           # generated/imported client-core types only
    commands/            # command presenters and confirmation flows
    projections/         # UI-specific pure derived models
    workers/             # event, layout, analytics workers
    features/
      runs/
      events/
      trace/
      loop/
      kernel/
      composition/
      plugins/
      evidence/
      experiments/
      knowledge/
      system/
    components/          # accessible generic presentation primitives
    design/              # tokens, themes, typography, icons
    test-fixtures/       # references shared VG-04 scenarios
  test/
    contract/
    component/
    e2e/
    performance/
    accessibility/
```

## 12. Implementation plan

### Milestone UI-0 — Contract and benchmark lock

**Goal:** prove the frontend can consume current truth without backend invention.

Tasks:

- UI0-01: inventory VG-04 frames, commands, receipts, client-core exports, and fixtures;
- UI0-02: document existing `runtime/studio` behavior and mark it reference-only;
- UI0-03: define supported browser/desktop transport decision;
- UI0-04: establish performance reference hardware and datasets;
- UI0-05: create wire compatibility matrix and negative fixtures;
- UI0-06: define accessibility and visual-regression baselines;
- UI0-07: create a threat model for command, approval, blob, and untrusted text surfaces.

Deliverables:

- UI architecture decision proposal;
- frozen initial route and feature matrix;
- 1k/10k/100k event fixtures;
- measurable performance and accessibility budgets;
- no production runtime change.

Exit gate: replay adapter renders an ordered textual event list through client-core and rejects a
corrupt sequence.

### Milestone UI-1 — Observatory vertical slice

**Goal:** one successful episode can be understood end to end.

Tasks:

- UI1-01: app shell, routing, theme, command palette, responsive layout;
- UI1-02: run overview projection;
- UI1-03: virtualized event explorer;
- UI1-04: contextual raw/provenance inspector;
- UI1-05: replay transport and fixture chooser;
- UI1-06: state-at-sequence scrubber;
- UI1-07: evidence and evaluator summary;
- UI1-08: accessibility golden path;
- UI1-09: performance instrumentation and CI budgets.

Deliverable: standalone fixture-driven Observatory build.

Exit gate: a reviewer identifies the objective, complete event order, effects, final state,
trajectory, and verdict without reading raw files.

### Milestone UI-2 — Live control plane

**Goal:** attach safely to a real sequential RuntimeService.

Tasks:

- UI2-01: local authenticated transport bridge for browser or desktop decision;
- UI2-02: live subscription with cursor resume and backpressure;
- UI2-03: stream health, pause, catch-up, and source badges;
- UI2-04: start/cancel/checkpoint commands through idempotent inbox;
- UI2-05: pending approval challenge and signer integration;
- UI2-06: disconnect, restart, duplicate, and out-of-order tests;
- UI2-07: CSP, origin, CSRF, XSS, and secret-redaction controls;
- UI2-08: operator audit view.

Deliverable: live sequential run control and inspection.

Exit gate: interrupt the client, reconnect, and show the same final projection without duplicate or
missing sequence; browser state alone cannot claim an effect completed.

### Milestone UI-3 — Composition and plugin laboratory

**Goal:** visually prototype harnesses against existing canonical contracts.

Tasks:

- UI3-01: backend-provided component catalog projection;
- UI3-02: typed component/port palette;
- UI3-03: React Flow composition canvas;
- UI3-04: schema-driven configuration forms;
- UI3-05: capability/selector/budget/isolation editor;
- UI3-06: validate/preview through canonical compiler;
- UI3-07: composition differential view;
- UI3-08: plugin lifecycle and dependency explorer;
- UI3-09: draft persistence separate from canonical run state;
- UI3-10: invalid-authority and second-dialect falsifiers.

Deliverable: coding and research/formal draft compositions can be built and validated visually.

Exit gate: exported authored manifest round-trips through the canonical backend and returns the same
frozen facts/digest as a non-GUI caller.

### Milestone UI-4 — Kernel, loop, context, and performance microscopes

**Goal:** expose why a run behaves as it does.

Tasks:

- UI4-01: S0–S12 effect microscope;
- UI4-02: grant/selector/lease/budget views;
- UI4-03: turn and model invocation timeline;
- UI4-04: context-layer and compaction view;
- UI4-05: critical-path and latency waterfall;
- UI4-06: token/cost/cache/tool attribution;
- UI4-07: anomaly and regression markers;
- UI4-08: M7-01 independence overlay when its schema exists;
- UI4-09: sequence-linked multi-panel selection.

Deliverable: one effect can be traced from proposal to authorization, intent, adapter receipt,
reduced state, trajectory, and evaluation.

Exit gate: no panel derives authority from UI assumptions; every displayed fact links to source.

### Milestone UI-5 — Experiment Arena

**Goal:** compare harness designs scientifically.

Tasks:

- UI5-01: experiment/preregistration viewer;
- UI5-02: paired run launcher using existing authorized commands;
- UI5-03: synchronized A/B timelines;
- UI5-04: first-divergence analysis;
- UI5-05: cost/latency/quality/evidence comparison;
- UI5-06: paired outcome statistics and insufficient-power reporting;
- UI5-07: Claude-like versus Codex-like Vanguard profile experiment;
- UI5-08: export review bundle with immutable identifiers;
- UI5-09: prohibit mixed model/environment/oracle comparisons unless declared as factors.

Deliverable: reproducible harness A/B report using the same model and task set.

Exit gate: the UI can explain both observed difference and experimental limitations; it cannot mark
a winner from incomparable runs.

### Milestone UI-6 — Knowledge Observatory

**Goal:** inspect research, RAG, artifacts, and high-order relations without making them authority.

Tasks:

- UI6-01: artifact/source/claim/citation schemas and projections;
- UI6-02: WebGL knowledge graph with progressive expansion;
- UI6-03: document and exact-span viewer;
- UI6-04: backlinks, saved queries, timelines, and relation filters;
- UI6-05: retrieval trace and ranking explanation;
- UI6-06: contradiction and supersession views;
- UI6-07: local spatial canvas metadata;
- UI6-08: DuckDB-Wasm bounded analytical workspace;
- UI6-09: deletion/rebuild and privacy/retention tests.

Deliverable: an Obsidian-like evidence navigator backed by immutable artifact references.

Exit gate: deleting all browser indexes and layout metadata then rebuilding produces equivalent
knowledge facts and different presentation metadata only.

### Milestone UI-7 — Governed autonomous operations

**Goal:** prepare, but do not pre-authorize, future delegated and self-regulating operation.

Tasks after corresponding backend milestones:

- UI7-01: child-agent tree and budget conservation after M-6;
- UI7-02: scheduler/lease/concurrency visualization after M-7;
- UI7-03: topology authoring and execution after M-8;
- UI7-04: proposal/evaluation/promotion pipeline after M-10;
- UI7-05: kill tree, pause, quarantine, and rollback controls;
- UI7-06: long-duration watch mode and notification policy;
- UI7-07: audit of autonomous actions and human intervention.

Deliverable: safe operations console driven entirely by authorized backend contracts.

Exit gate: disabling Observatory leaves autonomous execution, safety, persistence, and evaluation
unchanged.

## 13. Research basis and decisions

The recommendations above use the following research selectively.

### React Flow

React Flow's official performance guidance identifies unnecessary React rerenders as a major issue
for large node sets. It recommends memoized node components/functions, narrow store subscriptions,
collapsing large trees, and simplified styles. These practices fit the editable composition canvas.
React Flow is not selected for million-event visualization.

Source: <https://reactflow.dev/learn/advanced-use/performance>

### Sigma.js

Sigma.js uses WebGL and targets graphs with thousands of nodes and edges. Its rendering model and
Graphology integration fit read-only provenance, knowledge, and citation graphs. The current v4
track includes GPU timing/debug statistics but is alpha; the prototype should use a stable release
unless a benchmark justifies v4.

Sources: <https://www.sigmajs.org/docs/> and
<https://v4.sigmajs.org/how-to/technical/performance/>

### TanStack Virtual

TanStack Virtual is headless and renders only the viewport plus overscan, retaining full control of
markup and style. It fits high-volume event, log, tool-call, and artifact lists. Virtualization does
not eliminate the need for server-side cursors when datasets exceed browser memory.

Sources: <https://tanstack.com/virtual/latest/docs/introduction> and
<https://tanstack.com/table/latest/docs/framework/react/guide/virtualization>

### DuckDB-Wasm

DuckDB-Wasm can run analytical SQL in the browser and ingest Arrow, Parquet, CSV, and JSON. This is
useful for bounded experiment extracts and local exploratory analytics. Official documentation
notes a default single-threaded implementation and browser/Wasm memory limits, so it should not
replace the server event store or become mandatory for live views.

Sources: <https://duckdb.org/docs/stable/clients/wasm/overview> and
<https://github.com/duckdb/duckdb-wasm>

### Apache ECharts

ECharts supports Canvas/SVG renderers, streaming data, and progressive rendering for large datasets.
It is appropriate for latency, cost, token, throughput, and comparison charts when imported
modularly and paired with accessible tabular alternatives.

Source: <https://echarts.apache.org/en/feature.html>

### OpenTelemetry

OpenTelemetry semantic conventions provide common vocabulary across spans, metrics, logs, and
events. The current GenAI agent conventions cover operations such as `invoke_agent`, `plan`,
`execute_tool`, retrieval, workflow, and memory. These conventions are useful at export boundaries,
but remain under development. Vanguard should maintain a versioned translation adapter from its
canonical ledger rather than making unstable OTel names its domain ontology.

Sources: <https://opentelemetry.io/docs/specs/semconv/> and
<https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md>

### WCAG 2.2

WCAG 2.2 adds or strengthens guidance around focus visibility, target sizing, and interaction. The
observatory is an operational tool, so accessibility is a safety property as well as a compliance
goal.

Source: <https://www.w3.org/TR/WCAG22/>

## 14. Final recommendation

Approve the frontend as a staged observability/client program after the active backend gates, with a
fixture-first vertical slice allowed immediately because it does not change runtime semantics.

The winning architecture is deliberately asymmetric:

- the backend is authoritative, durable, capability-aware, and conservative;
- client-core is typed, headless, and shared;
- the frontend is fast, local-first where useful, richly visual, and disposable;
- scientific comparisons are preregistered and evidence-bound;
- future autonomy is observable but never granted by pixels.

The most valuable early demonstration is not a swarm. It is this:

> Replay one canonical run, inspect every important transformation, attach live without losing an
> event, visually compose two different harness profiles, execute a controlled paired comparison
> with the same model, and explain the divergence from immutable evidence.

That demonstration would prove the Observatory is more than a dashboard: it is the visual testing
instrument for AETHER as a general meta-framework.

# BACKEND CHANGES

## B1. Decision posture

The backend should evolve only through narrow client-facing ports and projections. No frontend
requirement justifies moving domain logic into a gateway, duplicating reducers in Python and
TypeScript, or adding UI-specific events to the canonical ledger.

Most foundational integration already exists:

- `RuntimeService` owns durable commands, event streaming, approvals, and run lookup;
- VG-04 provides typed command/event/receipt envelopes;
- `@vanguard/client-core` supplies live/replay/scenario transports, reducers, selectors, graph
  projection, resumable subscription, and signing;
- the CLI already proves one client skin can remain outside runtime authority;
- ledger projections are explicitly rebuildable caches rather than truth.

The backend changes below should be considered proposals for later authorized slices.

## B2. Required narrow additions

### B2.1 Capability discovery endpoint

Add a read-only service response describing what this runtime instance supports:

```json
{
  "wireVersion": "vg.4",
  "features": {
    "startRun": true,
    "checkpoint": true,
    "approval": true,
    "compositionPreview": false,
    "delegation": false,
    "concurrency": false
  },
  "eventSchemas": ["..."],
  "commandSchemas": ["..."],
  "limits": {"maxPageSize": 1000}
}
```

Clients render discovered capabilities and never infer milestone state from version strings.

### B2.2 Cursor-based historical event query

Live subscription exists, but the GUI needs bounded historical ranges:

```python
class RuntimeQueryPort(Protocol):
    def events(
        self,
        run_id: str,
        *,
        after_seq: str | None,
        before_seq: str | None,
        limit: int,
        kinds: tuple[str, ...] = (),
    ) -> Result[EventPage]: ...
```

The result includes first/last sequence, chain/range digest, continuation cursors, and completeness.
Filtering must not reorder or renumber canonical events.

### B2.3 Snapshot plus tail attach

Prevent races between initial state fetch and live subscription:

1. request a projection snapshot at sequence N;
2. verify snapshot digest/source range;
3. subscribe strictly after N;
4. reject gaps or duplicates;
5. rebuild from an earlier verified point when needed.

```ts
const snapshot = await client.getRun({ runId });
await subscribeRun(client, { runId, afterSeq: snapshot.lastSeq }, handlers, signal);
```

The backend should offer this as one documented consistency contract, even if implemented with
existing operations.

### B2.4 Generic projection query

Expose named, versioned read models for overview performance, not arbitrary Python objects:

- run summary;
- budget/lease status;
- plugin lifecycle;
- evidence summary;
- effect summary;
- context/cost summary;
- experiment summary.

Every response declares schema, source event range, projection digest, and rebuildability. A client
can always fall back to raw events for supported ranges.

### B2.5 Composition catalog and preview

The GUI needs read-only discovery and canonical validation:

- list components and interfaces;
- retrieve JSON schemas and safe configuration metadata;
- validate an authored draft;
- preview normalized/frozen facts and canonical digest;
- explain validation failures and unconsumed authority.

The canonical compiler remains the only authority. The frontend never writes directly to pack files
or runtime bindings.

### B2.6 Artifact/blob access

Add content-addressed, authorization-aware reads:

- metadata before content;
- range reads for large files;
- MIME and encoding;
- redaction state;
- content digest verification;
- retention/availability status;
- short-lived access tokens for web delivery when needed.

The ledger remains the authority for why an artifact exists; the blob endpoint supplies bytes only.

### B2.7 Metrics export adapter

Create an exterior adapter mapping canonical events/trajectory facts to OpenTelemetry spans,
metrics, and logs. Do not emit OTel data as a second canonical history.

```text
canonical ledger -> deterministic telemetry projection -> OTel exporter
```

Version the mapping centrally because GenAI conventions are evolving. Include stable Vanguard
identifiers so exported traces link back to evidence.

### B2.8 Backpressure and slow-consumer behavior

Define bounded subscription behavior:

- per-subscriber queue limit;
- high-water notification;
- close reason when the client cannot keep up;
- last safely delivered sequence;
- reconnect/catch-up procedure;
- no silent event dropping.

This replaces an implicit in-memory queue assumption with a testable transport contract.

## B3. Control-plane separation

Separate read queries, commands, and event streams at the protocol level:

| Plane | Operations | Safety property |
|---|---|---|
| Query | get run/events/projections/catalog/artifacts | No state mutation |
| Command | start/cancel/checkpoint/approve/configure | Idempotent receipt and actor identity |
| Stream | ordered canonical events and stream control | Resume cursor, no silent loss |

The web gateway may authenticate and translate transport framing but cannot authorize an effect. It
passes authenticated actor facts to the runtime, where policy remains authoritative.

## B4. Shared CLI/GUI contract evolution

All new generic operations land in this order:

1. Python domain/wire schema or existing protocol extension;
2. runtime service implementation;
3. generated TypeScript types;
4. `client-core` port and pure application projection;
5. CLI compatibility test;
6. GUI presentation;
7. live/replay differential fixture.

This prevents the GUI from racing ahead into private endpoints.

Suggested client port evolution:

```ts
interface RuntimeClient {
  capabilities(): Promise<Result<RuntimeCapabilities>>;
  startRun(command: StartRunCommand): Promise<Result<CommandReceipt>>;
  sendCommand(command: RuntimeCommand): Promise<Result<CommandReceipt>>;
  getRun(query: GetRunQuery): Promise<Result<RunSnapshot>>;
  getEvents(query: EventPageQuery): Promise<Result<EventPage>>;
  streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>>;
  getProjection<T>(query: ProjectionQuery<T>): Promise<Result<ProjectionEnvelope<T>>>;
  getArtifact(query: ArtifactQuery): Promise<Result<ArtifactResponse>>;
  catalog(): Promise<Result<ComponentCatalog>>;
  previewComposition(draft: AuthoredManifest): Promise<Result<FrozenCompositionView>>;
}
```

## B5. Event schema guidance

Do not add events for hover, panel state, graph coordinates, filters, or frontend analytics.

Backend events may be justified only for real material facts that currently cannot be reconstructed,
such as measured context compilation decisions or cache validations. Each new event still requires:

- allocation;
- one legal writer;
- schema;
- reducer or explicit advisory classification;
- coverage proof;
- replay behavior;
- privacy classification;
- compatibility vectors.

UI metadata belongs in a separate client preference store keyed by canonical identifiers.

## B6. Performance-oriented backend support

Avoid pushing raw million-event runs to every client. Add derived, reproducible acceleration:

- cursor indexes over event sequence/kind/principal/episode;
- materialized projection checkpoints with source range and digest;
- Arrow/Parquet export for experiment analysis;
- server aggregation for histograms and critical-path summaries;
- range reads for blobs;
- incremental graph summaries;
- optional compression negotiated at transport level;
- cancellation for expensive queries.

Every acceleration is disposable. Cold rebuild from canonical events and artifacts must remain the
truth test.

## B7. Security and deployment shapes

Support two deployment shapes behind the same client contract:

### Local desktop/browser

```text
Observatory browser -> localhost authenticated gateway -> UDS -> RuntimeService
```

- bind loopback only;
- random per-launch token;
- strict origin allowlist;
- no secret values in catalog/config responses;
- CSP and safe content rendering;
- gateway process has no more authority than the operator client.

### Remote team observatory

```text
Browser -> TLS gateway -> authenticated command/query service -> RuntimeService
```

- workload/user identity;
- role and project scoping;
- audit of every command;
- short-lived sessions;
- rate and payload limits;
- artifact-level authorization;
- no direct evaluator or event-store database exposure.

## B8. Backend implementation sequence

| Backend slice | Description | Depends on | Falsifier/deliverable |
|---|---|---|---|
| BG-0 | Freeze client/query/stream consistency contract | Current VG-04 | Contract tests only |
| BG-1 | Capabilities and historical cursor queries | BG-0 | Missing/gap/duplicate range cases |
| BG-2 | Snapshot-plus-tail attach | BG-1 | Concurrent append during attach |
| BG-3 | Versioned projection envelopes | BG-1 | Rebuild digest equality |
| BG-4 | Catalog and composition preview | Existing compiler | GUI/non-GUI frozen parity |
| BG-5 | Artifact range/redaction service | Blob/evidence contracts | Unauthorized/redacted access denial |
| BG-6 | Backpressure protocol | Stream contract | Slow consumer, reconnect, zero loss |
| BG-7 | OTel export adapter | Canonical events | Export deletion changes no run truth |
| BG-8 | Arrow/Parquet experiment export | Measurement schema | Export digest/source range verification |

These slices should be independently reversible. None should alter kernel semantics or open a
future milestone.

## B9. Backend acceptance criteria

The GUI integration is architecturally sound only if:

1. CLI and GUI use the same `RuntimeClient` semantics.
2. A replay fixture produces the same client projection in both skins.
3. The GUI can disappear mid-run without affecting execution.
4. Reconnection reconstructs the same state from a verified cursor.
5. Browser drafts cannot mint canonical composition identities.
6. Commands are idempotent, authenticated, and receipt-producing.
7. Approvals remain cryptographically bound to exact challenges.
8. No browser or gateway can write privileged ledger history.
9. All caches, indexes, graph layouts, and metrics can be deleted and rebuilt.
10. Evaluator isolation and kernel TCB are unchanged.

That boundary gives both CLI and GUI rich control and observability without coupling presentation to
execution or paying for a later major refactor.
