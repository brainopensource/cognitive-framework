---
id: research.frontend-aether-frontend-masterplan
kind: research
status: reference
authority: non-canonical
summary: "Research masterplan for TypeScript CLI, TUI, Observatory app, and Agent Development Studio."
topic:
  - frontend
---
# AETHER Frontend Masterplan

## TypeScript CLI, TUI, Observatory App and Agent Development Studio

**Status:** Proposed implementation authority  
**Target:** AETHER v0.7 Higgs through the M-8 MVP, with bounded compatibility for M-9/M-10  
**Audience:** Principal/Staff engineers, senior frontend/backend engineers, product engineering, UX, QA, AI systems research  
**Normative language:** `MUST`, `MUST NOT`, `SHOULD`, `MAY` carry their RFC 2119 meanings  
**Primary outcome:** a complete product surface for creating, running, observing, validating and improving AETHER agents without creating a second runtime, ledger or source of truth.

---

## 0. Executive decision

AETHER needs one coherent product system with three TypeScript surfaces:

1. **CLI** — automation, scripting, packaging, CI and headless use.
2. **TUI** — low-friction interactive agent operation and live observability in a terminal.
3. **App / Studio** — visual agent construction, workflow inspection, scientific comparison, debugging and controlled promotion of improvements.

All three surfaces MUST consume the same generated contracts and the same TypeScript SDK. They are clients of the existing AETHER Runtime; none may implement agent loops, capability authorization, event authority, scheduling truth, ledger semantics or metacognitive authority locally.

The frontend is not a decorative dashboard. It is simultaneously:

- a product interface for coding, research and mixed-agent workloads;
- an observability instrument for causal trajectories;
- a development environment for packs, plugins, policies, skills and topologies;
- an experimental workbench for replay, comparison, ablation and falsification;
- an operations console for capabilities, budgets, failures and recovery;
- a controlled interface for proposing, evaluating, promoting and rolling back improvements.

The architectural rule is:

> The backend owns facts and admissibility; the frontend owns interaction, visualization and user intent.

The first useful vertical slice MUST exist before the complete visual studio: start a coding run, stream events, show trajectory state, inspect artifacts and return a verified result. Each later milestone enriches that slice rather than creating a new product.

---

## 1. Product thesis and success definition

### 1.1 Product thesis

AETHER becomes valuable when a user can do five things without reading its source code:

1. describe or select an agent composition;
2. grant bounded capabilities and budgets;
3. run a real task against an isolated workspace;
4. understand what happened through causal evidence;
5. compare and improve the composition without corrupting the evidence.

The product must make the distinction between **composition** and **trajectory** explicit. Composition defines the available policies, plugins, tools, models, limits, topologies and context providers. Trajectory records which possibilities were actually used, in what causal order, with which artifacts, costs and outcomes.

### 1.2 Target user modes

| Mode | Primary user | Main job | Default surface |
|---|---|---|---|
| Operator | developer/researcher | run an existing agent safely | CLI or TUI |
| Builder | agent engineer | create packs, policies, tools and topologies | Studio |
| Investigator | AETHER developer | debug runtime, events, projections and recovery | Observatory |
| Scientist | evaluator/researcher | design trials, compare variants and falsify claims | Experiment Lab |
| Promoter | authorized reviewer | approve or roll back compositions/skills | Governance view |
| Integrator | product/CI engineer | embed AETHER through stable contracts | CLI and SDK |

### 1.3 Product-level acceptance

The frontend program is complete only when:

- a clean external repository can install or invoke the AETHER client without importing repository internals;
- the same agent can be run from CLI, TUI and App with semantically equivalent requests;
- all surfaces display event-derived state and never maintain an independent truth;
- coding, research and at least one mixed-agent composition execute through the same Runtime;
- a run can be inspected, replayed, compared, exported and independently evaluated;
- a new agent can be assembled from declared components without changing Kernel code;
- errors, authorization failures, missing evidence and partial recovery are visible rather than hidden;
- an improvement proposal cannot be promoted from the ordinary run UI without evaluation evidence and promoter authority;
- held-out validation demonstrates product utility outside the AETHER repository.

---

## 2. Constitutional architectural boundaries

### 2.1 Backend authority retained

The frontend MUST preserve the existing dependency and authority lattice:

```text
domain <- ports <- kernel <- agency <- runtime -> adapters
                                      ^
                                      |
                                client gateway
                                      |
                      TypeScript SDK / CLI / TUI / App
```

The backend remains authoritative for:

- append-only causal events;
- content-addressed artifacts;
- capability grants, attenuation and effect authorization;
- execution scopes, budgets and lineage identity;
- composition freezing and activation;
- effect dispatch, settlement, recovery and idempotency;
- deterministic projections such as `AgentView`;
- topology lowering and scheduler mechanism;
- memory access enforcement and promotion authority;
- evidence production and milestone gates.

### 2.2 Frontend responsibilities

The frontend owns:

- user intent capture and validation before submission;
- accessible representation of compositions and schemas;
- event-stream consumption and causal visualization;
- local interaction state such as panels, filters and drafts;
- optimistic UX only for non-authoritative drafts;
- artifact preview and safe diff rendering;
- agent, topology, experiment and policy editors;
- request formation for authorized backend commands;
- comparison of backend-produced projections and evidence;
- export, reports, links and navigation.

### 2.3 Explicit refusals

The frontend MUST NOT:

- invent, rewrite or reorder ledger facts;
- infer completion when the backend reports an open gate;
- execute tools directly to bypass Kernel dispatch;
- store hidden prompts, memory or skills outside declared backend stores;
- own a competing workflow engine or scheduler;
- model metacognition as a privileged UI-only agent;
- treat telemetry timestamps as causal ordering;
- mutate a historical event or artifact;
- grant itself capabilities;
- promote a skill or composition using client-side scores alone;
- use a visual graph as execution truth; graphs are projections or configuration drafts;
- silently retry non-idempotent commands;
- couple coding-specific UI ontology to generic runtime contracts.

---

## 3. Product surfaces and information architecture

### 3.1 Unified application model

The product family SHOULD be presented as **AETHER Studio**, containing modes rather than separate conceptual products:

- **Run** — task execution and operator console.
- **Agents** — catalog, creation, composition and versioning.
- **Observe** — events, trajectory, lineages, artifacts and runtime state.
- **Workflows** — topology editor and realized causal graph comparison.
- **Context** — selected context, compaction, provenance, retrieval and memory.
- **Skills** — candidates, active versions, evidence, promotion and rollback.
- **Experiments** — paired runs, ablations, held-out sets and reports.
- **System** — plugins, adapters, providers, schemas, capabilities and health.
- **Development** — contract tests, replay, fixtures, diagnostics and links to source/docs.

### 3.2 Primary navigation

The main navigation MUST be task-oriented and stable:

| Area | Question answered |
|---|---|
| Runs | What is running, completed, blocked or failed? |
| Agents | What can I run or create? |
| Studio | How is this composition assembled? |
| Observatory | What happened internally and why? |
| Experiments | Is variant B actually better than A? |
| Skills & Memory | What knowledge is available, used, proposed or promoted? |
| Artifacts | What durable outputs exist and where did they come from? |
| Governance | Who authorized, evaluated or promoted this change? |
| System | Are Runtime, providers, stores and plugins healthy? |

### 3.3 Progressive disclosure

The UI MUST support three information depths:

- **Essential:** task, current phase, outcome, cost, elapsed time and blocking action.
- **Technical:** model calls, tools, context, lineages, artifacts, failures and projections.
- **Forensic:** raw event envelope, digests, causation/correlation, writer role, grant, policy version, schema and evidence references.

The default user view must remain usable. Forensic data must be one click away and copyable, not continuously dumped into the main interface.

---

## 4. TypeScript workspace architecture

### 4.1 Recommended repository shape

```text
frontend/
  apps/
    cli/                    # headless commands and CI surface
    tui/                    # interactive terminal client
    studio/                 # React web/local application
    desktop/                # optional thin desktop shell; no domain logic
  packages/
    contracts/              # generated wire types and schema validators
    sdk/                    # transport-independent AETHER client
    command-model/          # typed command builders and idempotency
    projection-model/       # read models consumed by all clients
    graph-model/            # causal/topology graph normalization
    experiment-model/       # trial definitions and statistical summaries
    ui-system/              # tokens, accessibility and shared components
    observability-ui/       # timeline, event, lineage and artifact components
    agent-builder/          # manifest/topology/policy editing components
    testkit/                # fixtures, fake gateway, contract/golden helpers
  tooling/
    codegen/                # JSON Schema/OpenAPI/event catalog generation
    contract-check/         # drift detection
  docs/
    frontend/               # UX contracts, ADRs, runbooks
```

### 4.2 Dependency rules

```text
apps -> feature packages -> sdk/projection-model -> contracts
                    graph-model -> contracts
                    ui-system   -> no domain imports
```

Rules:

- `contracts` MUST NOT import any application package.
- `sdk` MUST NOT import React, terminal libraries or app state.
- `projection-model` MUST contain no network code.
- UI packages MUST consume stable view models, not raw backend internals.
- applications MAY compose packages but MUST NOT duplicate domain contracts.
- generated code MUST be committed or deterministically generated in CI.
- handwritten wire types that duplicate backend schemas are forbidden.

### 4.3 Technology decision

The default implementation SHOULD use:

- TypeScript in strict mode;
- a workspace package manager with lockfile and reproducible builds;
- Node.js for CLI, TUI and local integration;
- React for the visual App;
- a lightweight local web deployment as the first App target;
- an optional desktop shell only after the web/local application is stable;
- a terminal rendering library with React-style composition for the TUI;
- JSON Schema-derived runtime validation;
- Server-Sent Events for ordered one-way run updates initially;
- WebSocket only for demonstrably bidirectional interactive flows that SSE plus commands cannot serve;
- indexed local cache only for rebuildable frontend projections and offline browsing.

The desktop wrapper MUST remain replaceable. No backend authority or AETHER semantics may be placed in Electron-, Tauri- or browser-specific code.

---

## 5. Backend client gateway

### 5.1 Purpose

The existing Python Runtime needs a thin **Client Gateway** above the public composition path. It adapts frontend requests to existing application services; it does not become a new orchestrator.

Gateway responsibilities:

- authenticate the local or remote client;
- validate commands against versioned schemas;
- attach request and idempotency identities;
- invoke the single canonical Runtime composition/activation path;
- expose read-only projections and artifacts under capability checks;
- stream committed events and correlated telemetry;
- return explicit accepted/rejected/conflict responses;
- negotiate contract versions;
- expose health and compatibility information.

### 5.2 Gateway resources

The minimum resource model is:

| Resource | Commands | Queries/streams |
|---|---|---|
| Composition | draft, validate, freeze, activate | list, get, diff, compatibility |
| Agent definition | create draft, validate, version | catalog, detail, dependencies |
| Run | start, pause-request, resume, cancel | status, projection, event stream |
| Lineage | spawn request through run authority | tree, scope, budget, projection |
| Artifact | create through authorized service | metadata, verified content, refs |
| Topology | validate, freeze | graph, lowered plan, realized graph |
| Experiment | create, launch, stop | trials, metrics, evidence, report |
| Skill candidate | propose, evaluate request | lifecycle, evidence, composition impact |
| Promotion | request | status, attestation, rollback state |
| System | enable/disable declared plugin through config workflow | health, capabilities, schemas |

### 5.3 Command envelope

All mutating client requests MUST use a versioned command envelope:

```typescript
type CommandEnvelope<T> = Readonly<{
  schemaVersion: "aether.command/1";
  commandId: string;
  idempotencyKey: string;
  commandType: string;
  requestedAt: string;
  actor: { principalId: string; sessionId: string };
  target: { projectId?: string; runId?: string; lineageId?: string };
  expectedVersion?: string;
  capabilityReference?: string;
  payload: T;
}>;
```

Semantics:

- `commandId` identifies the request fact from the client perspective.
- `idempotencyKey` is mandatory for retryable submission.
- `expectedVersion` enables compare-and-swap for mutable configuration drafts and promotion pointers.
- the gateway MUST return rejection if the client contract is unsupported.
- acceptance means the command entered backend processing; it does not mean the requested outcome occurred.

### 5.4 Command response

```typescript
type CommandResult =
  | { status: "accepted"; commandId: string; operationRef: string; streamCursor?: string }
  | { status: "rejected"; commandId: string; error: AetherProblem }
  | { status: "conflict"; commandId: string; currentVersion: string; error: AetherProblem };
```

### 5.5 Query envelope and pagination

Queries MUST return:

- `schemaVersion`;
- resource identity and version;
- projection coverage cursor;
- reducer/schema pins when relevant;
- page cursor rather than page number for ordered event collections;
- explicit completeness (`complete`, `partial`, `degraded`);
- warnings for missing artifacts, invalid checkpoints or unavailable telemetry.

### 5.6 Event streaming protocol

The client stream MUST distinguish durable facts from operational telemetry:

```typescript
type StreamMessage =
  | { channel: "event"; cursor: string; event: EventEnvelope }
  | { channel: "projection"; cursor: string; projection: ProjectionDelta }
  | { channel: "telemetry"; cursor: string; sample: TelemetrySample }
  | { channel: "control"; cursor: string; message: StreamControl };
```

Rules:

- `event` contains committed causal facts only.
- `projection` is rebuildable and MUST identify coverage through an event.
- `telemetry` is correlated evidence and MUST NOT alter causal order.
- `control` communicates heartbeat, resync requirements, retention gaps and schema changes.
- cursors MUST support reconnect and resume.
- duplicates are allowed across reconnect; clients deduplicate by stable identity.
- gaps require a resync query; clients must not interpolate missing events.
- out-of-order physical delivery must not be shown as causal order.

### 5.7 Error contract

```typescript
type AetherProblem = Readonly<{
  type: string;
  title: string;
  status: number;
  code: string;
  detail: string;
  retryability: "never" | "safe-idempotent" | "after-user-action" | "unknown";
  correlationId: string;
  causes?: readonly AetherProblem[];
  remediation?: readonly RemediationAction[];
  evidenceRefs?: readonly string[];
}>;
```

The UI MUST show what failed, where, whether retry is safe, and which evidence supports the diagnosis. Stack traces are developer-only and must be scrubbed before ordinary display.

---

## 6. Contract generation and compatibility

### 6.1 Single schema authority

Backend JSON Schemas and accepted protocol documents are the source of truth. A code-generation pipeline MUST produce:

- TypeScript wire types;
- runtime validators;
- discriminated unions for event kinds;
- payload type maps;
- schema identifiers and version registries;
- test vectors and example fixtures;
- human-readable event catalog metadata.

### 6.2 Build-time drift gate

```text
read backend schema registry
-> normalize schemas
-> generate TypeScript contracts
-> compile strict
-> validate golden vectors
-> compare generated tree with committed tree
-> fail CI on unexplained diff
```

Any new event kind requires the backend's complete kind package before frontend support: schema, authority, reducer handling or justified no-op, golden vector and documentation. The frontend must not accept a free-form event kind merely to avoid updating its types.

### 6.3 Compatibility negotiation

On connection, the SDK performs:

```text
client supported contract set
-> gateway compatibility response
-> exact common versions
-> optional degraded feature set
-> reject if safety-critical contract has no common version
```

Unknown additive fields MAY be preserved. Unknown semantic event kinds MUST cause a visible compatibility failure for projections that require them. Historical `/1` events can be read through backend-normalized projections; the frontend SHOULD not independently recreate backend migration semantics.

---

## 7. Shared TypeScript SDK

### 7.1 Public SDK boundary

```typescript
interface AetherClient {
  system: SystemClient;
  compositions: CompositionClient;
  agents: AgentCatalogClient;
  runs: RunClient;
  artifacts: ArtifactClient;
  experiments: ExperimentClient;
  skills: SkillClient;
  governance: GovernanceClient;
}
```

The SDK MUST support local HTTP, authenticated remote HTTP and an in-process test transport. Surface applications receive the interface, never construct fetch calls directly.

### 7.2 Run lifecycle pseudocode

```text
function startRun(draft):
  validate draft locally using generated schema
  request backend validation
  if invalid: return structured issues
  freeze composition or resolve immutable composition reference
  submit StartRun with idempotency key
  receive accepted operation reference
  subscribe from returned cursor
  fold incoming projection deltas into UI read model
  on gap: pause live claim, resync authoritative projection, resume
  on terminal: fetch final projection, evidence summary and artifacts
```

### 7.3 Client caching

Client caches are convenience projections only. Every cached object MUST retain:

- backend resource version;
- projection coverage cursor;
- fetched time;
- contract version;
- completeness state;
- invalidation relation.

Cache loss must not affect backend correctness. Offline mode may inspect previously fetched runs but must visibly mark them as snapshots and forbid authoritative mutations.

---

## 8. CLI masterplan

### 8.1 CLI principles

The CLI is the canonical automation surface. It MUST be deterministic, scriptable, composable and usable in CI. Human-friendly output is default for interactive terminals; machine-readable output is stable under `--output json`.

### 8.2 Command taxonomy

```text
aether init
aether doctor
aether login / context
aether agent list|show|create|validate|pack|publish
aether composition validate|freeze|diff|activate
aether run start|watch|inspect|cancel|resume|replay|export
aether lineage tree|inspect
aether event tail|show|verify
aether artifact list|get|verify
aether topology validate|render|lower|compare
aether experiment create|run|watch|compare|report
aether skill list|inspect|propose|evaluate|promote|rollback
aether plugin list|inspect|validate|enable|disable
aether schema list|show|check
aether test contract|replay|falsifier|integration|product-gate
```

### 8.3 CLI output contract

- exit code `0`: command completed successfully;
- exit code `2`: user input/schema error;
- exit code `3`: authorization or capability rejection;
- exit code `4`: conflict/version mismatch;
- exit code `5`: backend unavailable;
- exit code `6`: run completed with failed task outcome;
- exit code `7`: evidence or verification failure;
- other codes are reserved and documented.

Every JSON output MUST include `schemaVersion`, `status`, `correlationId` and either `data` or `error`.

### 8.4 External product validation

The CLI package MUST be tested in a clean consumer workspace:

1. install the released client and pinned backend package/container;
2. initialize a new project outside the AETHER repository;
3. select the coding composition;
4. grant workspace-scoped capabilities;
5. execute a held-out coding task;
6. run consumer tests;
7. export trajectory, artifacts and evaluation;
8. verify that no AETHER source-tree import or fixture was used.

This is a product gate, not merely an integration test.

---

## 9. TUI masterplan

### 9.1 Purpose

The TUI provides the shortest path from CLI operation to interactive product. It should be developed before the full Studio reaches feature parity because it reveals backend integration defects with minimal presentation overhead.

### 9.2 Layout

```text
Top bar: project | composition | run | connection | budget | cost
Left: runs / agents / lineages / tasks
Center: conversation or event timeline
Right: context / tool / artifact / projection inspector
Bottom: command palette, approvals, errors and current operation
```

### 9.3 TUI views

- Run console with user input and structured agent responses.
- Event tail with filtering by lineage, kind, writer and status.
- Child-lineage tree with independent budgets and terminals.
- Artifact list and safe text/diff preview.
- Context summary showing selected sources, tokens, compaction and retrieval provenance.
- Capability/approval queue with explicit scope and consequence.
- Runtime health and provider state.
- Compact experiment comparison.

### 9.4 Interaction rules

- keyboard-first operation and command palette;
- no mouse dependency;
- shortcuts displayed contextually;
- confirmation for capability expansion, cancellation and promotion;
- streaming content must not move focus or destroy scroll position;
- errors stay anchored to the operation that caused them;
- raw events are inspectable without flooding the main conversation;
- terminal width degradation must remain functional down to a documented minimum.

---

## 10. Studio App masterplan

### 10.1 App shell

The App is a React/TypeScript local web application first. It uses a three-region shell:

- navigation rail for product areas;
- primary workspace for the selected graph, timeline or editor;
- contextual inspector for the selected entity.

A persistent run strip shows active run, lineage, phase, budget, cost, warnings and connection state. Deep links MUST address stable identities: project, composition, run, lineage, event, artifact, skill or experiment.

### 10.2 Run Console

Purpose: operate coding, research or mixed agents.

Components:

- task composer with attachments and workspace selection;
- composition selector with immutable version display;
- capability and budget preview;
- live response stream;
- current phase and strategy indicator;
- tool/effect cards;
- approval requests;
- verification and final outcome panel;
- export and reproduce actions.

The conversation is a view of a run, not the run's source of truth. Reloading the page must reconstruct it from projections and artifacts.

### 10.3 Execution Observatory

The Observatory is the central development instrument.

#### Timeline view

Displays durable events in physical append order while rendering causal relations separately. Filters include:

- lineage and ancestry;
- event kind and semantic family;
- writer role and policy version;
- operation and idempotency identity;
- success/failure/recovery;
- capability grant and approval;
- artifact production;
- model/tool/context/meta-controller activity.

Each row shows identity, causal parent, logical time, wall time when available, writer, kind, summary and evidence state.

#### Causal graph

Nodes represent events, operations, lineages or artifacts depending on zoom. Edges represent causation, correlation, ancestry, artifact production/consumption or declared topology relations. Physical sequence MUST NOT be rendered as causal dependence unless the relation exists.

#### Runtime inspector

Shows:

- `AgentView` and coverage cursor;
- goal, plan revisions, strategy and progress;
- settled effects and failures;
- budget allocation and consumption;
- children and terminal states;
- checkpoint selected and suffix folded;
- active composition and policy pins;
- capabilities and attenuation chain.

#### Event forensic inspector

Tabs:

1. Summary.
2. Payload validated against schema.
3. Causation/correlation/lineage.
4. Authority and capability basis.
5. Artifacts and digests.
6. Reducer/projection impact.
7. Related telemetry.
8. Raw canonical envelope.

### 10.4 Architecture Explorer

This view answers “Kernel versus plugin” without requiring source reading.

It shows a static component dependency view and overlays realized run activity:

- domain and ports as contracts;
- Kernel as admissibility/effect reference monitor;
- agency as policies/context/decision support;
- Runtime as composition and execution mechanism;
- adapters as environment bindings;
- packs/plugins as domain behavior;
- clients as external surfaces.

Selecting a run highlights only components used by that run. Selecting an event highlights its writer, consumers, schema and affected projection. Links MAY open the corresponding documentation or source file when repository metadata is available.

### 10.5 Context and Memory Explorer

The view MUST distinguish:

- candidate context;
- selected context;
- compacted context;
- retrieved experience;
- validated knowledge;
- project memory;
- session state derived from ledger;
- active skills.

For each context item display source identity, policy, parameters digest, token contribution, inclusion reason when available, provenance, retention class and artifact link. “Used in prompt” must be derived from recorded selection/output identity, not guessed from availability.

### 10.6 Artifact Explorer

Features:

- role/schema/producer filtering;
- content digest verification;
- provenance graph;
- safe preview for text, JSON, patches, reports and snapshots;
- side-by-side diff;
- missing-content explanation for digest-only retention;
- retention and legal-hold status;
- references to producing and consuming events;
- export with a manifest of identities and hashes.

### 10.7 Lineage Explorer

Shows nested executions rather than pretending every child is a chat persona. Each lineage card contains goal, parent, scope, budget, capability subset, context configuration, status, result and evidence. The tree supports collapse, critical-path highlighting, orphan/recovery state and parent-child artifact flow.

### 10.8 Workflow and Topology Studio

The editor manipulates versioned `mhf.topology/1` configuration drafts. It must distinguish:

- **Declared topology:** permitted roles, relations and artifact flows.
- **Lowered run plan:** backend-produced execution templates.
- **Realized trajectory:** what actually occurred.

The UI MUST never execute directly from its graph. Saving produces a versioned draft; validation and lowering occur in the backend. Required editor functions:

- role creation and policy binding;
- scope and budget templates;
- `may_delegate_to`, `reviews` and `merges_into` relations;
- artifact-flow schema selection;
- entry role;
- capability conflict checks;
- unreachable-role and cycle diagnostics where applicable;
- visual diff between topology versions;
- simulation preview based on backend lowering, explicitly marked non-execution;
- comparison of declared versus realized graph.

### 10.9 Agent Builder

An agent definition is a composition preset, not a new core class.

The builder guides the user through:

1. identity, purpose and domain pack;
2. model policy and fallback rules;
3. tools/plugins and capabilities;
4. context providers and compaction strategy;
5. memory/retrieval policy;
6. evaluator and terminal conditions;
7. execution profile and budgets;
8. optional topology and meta-controller;
9. test fixtures and evaluation suite;
10. validation, freeze and version.

The builder MUST provide an “architecture placement” explanation for every extension: pack, plugin, adapter, policy, projection or Runtime mechanism. Any proposal requiring Kernel modification is blocked and routed to architectural review.

### 10.10 Agent Catalog and use

Catalog entries include:

- immutable version and content digest;
- domain and supported task types;
- required capabilities and providers;
- default and maximum budgets;
- compatibility range;
- evaluation evidence and known limitations;
- dependencies, skills and topology;
- publisher/provenance;
- example tasks;
- deprecation/revocation state.

Running an agent requires selecting an immutable version or an explicitly tracked channel. The UI displays the exact resolved composition digest before execution.

### 10.11 Experiment Lab

The Lab supports scientific comparison without turning the browser into the evaluator.

Features:

- fixed and held-out task-set registration;
- baseline and treatment composition selection;
- controlled variable declaration;
- seeds, repetitions and budgets;
- paired-run launch;
- ablation of one component at a time;
- primary metric and regression budgets;
- run eligibility and evidence completeness;
- result distributions and confidence/calibration views;
- trajectory diff and failure clustering;
- signed report artifact access;
- decision record: accept, reject, inconclusive or redesign.

The UI MUST prevent a comparison from being labeled causal when multiple undeclared dimensions changed.

### 10.12 Metacognition view

Metacognition is visualized as an ordinary derived loop:

```text
AgentView + ProgressProjection + confidence evidence
-> MetaController assessment
-> optional StrategyDirective
-> ordinary proposal and authorization
-> effect/event/result
-> later evaluation
```

Display:

- observed progress signals;
- confidence records and calibration basis;
- controller identity/version;
- considered or emitted directive when recorded;
- strategy change attribution;
- cost of intervention;
- outcome difference in paired trials.

The view MUST label reflection without external evidence as a claim, not a fact.

### 10.13 Skills and self-improvement

The lifecycle UI is a gated pipeline:

```text
trajectory corpus
-> analysis/failure clusters
-> candidate skill
-> isolated evaluation
-> promotion proposal
-> independent review
-> new composition version
-> canary/held-out validation
-> promote or rollback
```

Required views:

- candidate origin and generating evidence;
- exact skill artifact and version;
- generator/evaluator/promoter separation;
- affected contexts and risk level;
- presence-only, invocation, grounding, verification and transfer tests;
- gross gains, regressions and residual failures;
- active composition pointer;
- rollback control with expected-version guard;
- audit history.

Ordinary agents may propose candidates. Only authorized governance commands can promote.

### 10.14 Feature Development workspace

This workspace connects product behavior to engineering work:

- run/event/artifact permalink capture;
- “create bug report” draft populated with identities and environment pins;
- expected versus actual projection comparison;
- contract/schema validation results;
- replay parity result;
- linked ADR/spec/milestone/task metadata;
- regression test fixture export with sensitive-content review;
- benchmark comparison;
- feature flag/composition version correlation.

It MUST avoid automatically exporting secrets, raw private context or unrestricted workspaces.

---

## 11. UI/UX system

### 11.1 Design principles

1. **Causality before animation.** Visual effects never imply unsupported order.
2. **Truth state is explicit.** Fact, projection, telemetry, claim and attestation use distinct visual semantics.
3. **Failure is first-class.** Rejections, gaps and degraded reconstruction remain visible.
4. **Identity is navigable.** Every significant entity has a stable permalink and copyable identity.
5. **Progressive disclosure.** Operators see outcomes; investigators can reach raw contracts.
6. **Comparison over impression.** Improvements are shown against baselines and regression budgets.
7. **Safe action design.** Scope, authority and consequences precede destructive or privileged actions.
8. **Keyboard-first expert workflows.** Command palette and shortcuts complement pointer interaction.

### 11.2 Semantic visual language

| Semantic class | Visual treatment | Examples |
|---|---|---|
| Durable fact | solid node/line | committed event, artifact fact |
| Projection | outlined panel with coverage | AgentView, progress view |
| Telemetry | dotted/secondary trace | latency, CPU, live token rate |
| Claim | labeled assertion badge | confidence self-report |
| Attestation | signed/verified badge | independent evaluation |
| Draft | editable neutral surface | topology or composition draft |
| Rejection/failure | persistent error state | capability rejection, failed effect |
| Degraded/missing | warning with reason | missing blob, invalid checkpoint |

Color MUST NOT be the sole discriminator. Icons, labels and patterns are required.

### 11.3 Core component inventory

- `IdentityLink`
- `SchemaBadge`
- `AuthorityBadge`
- `CapabilityScopeView`
- `BudgetMeter`
- `EvidenceState`
- `RunStateChip`
- `EventRow`
- `EventInspector`
- `CausalGraph`
- `LineageTree`
- `ArtifactPreview`
- `ProjectionCoverage`
- `ContextContribution`
- `StrategyChangeCard`
- `ExperimentComparison`
- `PromotionGate`
- `ProblemPanel`
- `CommandConfirmation`
- `ConnectionAndGapIndicator`

Each component must document input view model, empty/loading/error/degraded states, accessibility behavior, performance limits and test fixtures.

### 11.4 Accessibility

The App MUST meet WCAG AA expectations:

- complete keyboard navigation;
- visible focus and skip navigation;
- screen-reader labels for graph equivalents;
- tabular fallback for every graph;
- reduced-motion mode;
- high-contrast mode;
- non-color semantic distinctions;
- live-region discipline for streaming updates;
- pause/freeze controls for rapidly updating timelines.

---

## 12. State management and frontend projections

### 12.1 State classes

Frontend state is divided into:

1. **Authoritative snapshots:** fetched backend projections and resources.
2. **Stream deltas:** committed updates awaiting integration.
3. **Drafts:** unsaved agent/topology/experiment definitions.
4. **Ephemeral UI state:** selection, layout, filters and open panels.
5. **Cached history:** rebuildable offline snapshots.

These classes MUST not be placed in one undifferentiated global store.

### 12.2 Projection update pseudocode

```text
onStreamMessage(message):
  validate message contract
  if duplicate identity: ignore
  if cursor gap: mark view degraded; request authoritative resync
  if durable event: append to local event index only
  if projection delta:
      require base version matches local projection
      apply delta immutably
      update coverage cursor
  if telemetry: store in bounded time window
  never derive backend terminal truth solely from UI timers
```

### 12.3 Graph normalization

The graph model converts multiple backend resources into a stable frontend representation:

```typescript
type GraphNode = Readonly<{
  id: string;
  kind: "event" | "operation" | "lineage" | "artifact" | "role" | "component";
  label: string;
  status?: string;
  refs: readonly string[];
  semanticClass: "fact" | "projection" | "telemetry" | "draft";
}>;

type GraphEdge = Readonly<{
  id: string;
  source: string;
  target: string;
  relation: "causes" | "correlates" | "parent" | "produces" | "consumes" | "permits" | "reviews" | "merges";
  authoritative: boolean;
}>;
```

Layout coordinates are ephemeral UI state and never enter backend topology or evidence.

---

## 13. Security and capability UX

### 13.1 Threat model

The product must assume:

- untrusted task text and repository content;
- prompt injection in documents and tool output;
- malicious or defective plugins;
- secrets in environment, artifacts or logs;
- capability escalation attempts;
- replayed or duplicated commands;
- compromised client cache;
- cross-project data leakage;
- misleading self-evaluation;
- unauthorized skill promotion.

### 13.2 Security controls

- local gateway binds to loopback by default;
- remote access requires authenticated encrypted transport;
- short-lived session credentials are stored using platform facilities;
- commands are idempotent and actor-attributed;
- capability requests display resource selector, sink, duration and budget;
- workspace grants are path-scoped and normalized by the backend;
- artifact previews sandbox active content;
- secrets are redacted at gateway and rendering boundaries;
- plugin manifests and signatures are visible;
- frontend never receives provider secrets when proxy execution suffices;
- promotion controls require fresh authorization and expected-version checks;
- audit export omits sensitive content by default while preserving digests.

### 13.3 Approval UX

Approval dialogs MUST answer:

- what operation is proposed;
- which agent/lineage requested it;
- which resources and sinks are affected;
- what capability and budget are requested;
- why the operation is needed when rationale exists;
- whether it is one-shot, session-scoped or persistent;
- what alternatives exist: deny, narrow, allow once, allow scoped;
- what evidence and policy produced the request.

The UI must never offer “always allow” without a precise revocable scope.

---

## 14. Observability, diagnostics and bug discovery

### 14.1 Required observability data

The App should expose, when recorded:

- selected context and compaction identities;
- model/provider identity and attestation state;
- tool calls, selectors, sinks and settlement;
- retries, failures and recovery actions;
- tokens, cost, latency and cache behavior;
- artifact production and verification;
- strategy and progress changes;
- lineage spawning, return and budget conservation;
- topology version and lowering result;
- retrieval provenance and skill usage;
- evaluation, promotion and rollback evidence.

### 14.2 Automated diagnostics

Diagnostics are rules over projections and evidence, not new authority. Initial detectors:

- stream gap or duplicate settlement;
- unresolved effect beyond policy threshold;
- child budget conservation mismatch;
- capability reference missing from an effect;
- artifact fact with unavailable required blob;
- checkpoint mismatch and cold-fold fallback;
- repeated action signature/stall;
- context compaction without provenance;
- declared topology role never realized;
- skill retrieved but not grounded or verified;
- terminal success without required verifier evidence;
- promotion pointer/evidence mismatch;
- UI/backend schema incompatibility.

Every diagnostic returns severity, basis, affected identities, confidence, remediation and whether it is deterministic or heuristic.

### 14.3 Run diff

Run comparison aligns trajectories by semantic operation and causation, not merely array index. It shows:

- composition differences;
- context and retrieval differences;
- model/tool/strategy divergence point;
- cost and latency deltas;
- outcome and verifier deltas;
- artifact differences;
- causal subgraphs unique to each run.

When alignment is uncertain, the UI must show ambiguity rather than force a false match.

---

## 15. Testing strategy

### 15.1 Test pyramid

| Layer | Required tests |
|---|---|
| Contracts | schema vectors, discriminated unions, backward compatibility |
| Pure models | reducers, graph normalization, formatting, diff alignment |
| SDK | command idempotency, cursor reconnect, gap recovery, problem mapping |
| Components | all states, accessibility, keyboard behavior, large fixtures |
| Feature integration | mocked gateway plus golden trajectories |
| Backend integration | real gateway against isolated stores/providers |
| Replay | cold reconstruction and UI equivalence from recorded run |
| Product E2E | clean external workspace and real task |
| Scientific validation | baseline/treatment and held-out evidence |
| Security | injection, scope escape, secret leakage, unauthorized promotion |
| Performance | large ledger, graph virtualization, stream burst, artifact preview |

### 15.2 Contract testkit

The shared testkit MUST provide:

- valid and invalid command fixtures;
- event-envelope golden vectors;
- M-4 trajectory fixture;
- M-5a checkpoint and cold-reconstruction fixture;
- M-6 nested lineage and recovery fixture;
- M-6.5 strategy-change comparison fixture;
- M-7 declared/lowered/realized topology fixtures;
- M-8 candidate/promotion/rollback fixture;
- deterministic fake clock and cursor stream;
- gap, duplication and reconnect scenarios;
- redacted sensitive artifact examples.

### 15.3 UI replay equivalence gate

For a pinned recorded run:

```text
live stream -> final frontend view model A
cold backend projection + event query -> frontend view model B
assert semantic A == B
```

This catches hidden dependence on transient websocket/SSE timing.

### 15.4 Clean-room product gate

The final M-8 frontend gate MUST run outside the monorepo against a sealed task set. Required variants:

- coding agent on a fresh software repository;
- research agent on a documented evidence task;
- mixed planner/researcher/coder/critic composition;
- restart during an active run;
- denied capability path;
- promoted skill followed by injected regression and rollback.

The gate captures installation time, time-to-first-run, success rate, cost, latency, operator interventions, replay quality and evidence completeness.

---

## 16. Performance and scalability budgets

### 16.1 Frontend budgets

Targets must be calibrated with real fixtures, but the implementation begins with these engineering constraints:

- first useful local screen in approximately two seconds on a development machine;
- visible reaction to a committed event within 250 ms excluding backend/network latency;
- event timeline virtualized beyond 1,000 rows;
- interactive filtering for 100,000 indexed event summaries;
- graph defaults to aggregation above 2,000 visible nodes;
- telemetry buffers bounded by time and count;
- artifact previews streamed and size-limited;
- no full-ledger load to show a run list;
- projection queries prefer checkpoint plus suffix;
- expensive graph layout runs off the main UI thread;
- reconnect does not refetch retained artifacts unnecessarily.

### 16.2 Backpressure

During event bursts:

- durable facts are never dropped;
- UI rendering may batch updates;
- telemetry may be sampled according to declared policy;
- the current operation and terminal events receive priority;
- control messages expose lag;
- the client requests resync if its bounded queue cannot preserve correctness.

---

## 17. Packaging and deployment

### 17.1 Deliverables

The product SHOULD ship as:

- `@aether/contracts` — generated contracts;
- `@aether/sdk` — programmatic TypeScript client;
- `@aether/cli` — executable CLI;
- `@aether/tui` — terminal application;
- `@aether/studio` — static/local web App;
- optional desktop distribution wrapping the same Studio build;
- backend Python package and/or container with the Client Gateway;
- example coding, research and mixed composition packs;
- clean-room validation kit.

### 17.2 Local launch model

```text
aether studio
-> verify backend compatibility
-> start or connect to local gateway
-> serve/open Studio
-> display health and composition catalog
```

The launcher must show exact frontend/backend versions, schema compatibility, project boundary and data location. Startup failure must provide actionable diagnosis.

### 17.3 Versioning

- contracts use explicit schema identifiers independent from package versions;
- packages follow semantic versioning;
- agent compositions, topologies, policies and skills use immutable content identity plus human version;
- Studio features declare required backend capabilities;
- unsupported features are disabled with a reason, not allowed to fail later;
- the CLI JSON contract receives its own version.

---

## 18. Development workflow and engineering standards

### 18.1 Definition of ready

A frontend task is ready only when it contains:

- user outcome;
- backend authority/source contract;
- input/output schemas;
- target view model;
- loading/empty/error/degraded states;
- capability/security impact;
- accessibility acceptance;
- performance fixture;
- test plan;
- milestone and evidence reference.

### 18.2 Definition of done

A feature is done when:

- generated contracts compile with no drift;
- SDK behavior is transport-independent;
- CLI/TUI/App semantics agree where applicable;
- component and integration tests cover failure/degraded paths;
- keyboard and screen-reader behavior is verified;
- observability shows relevant identities and evidence;
- documentation and example workflows are updated;
- no backend authority is duplicated;
- product metrics are emitted as telemetry, not ledger facts unless causally required;
- a clean build and package installation succeed;
- the relevant product or milestone gate passes.

### 18.3 Pull-request boundaries

Keep separate commits/PRs for:

- backend gateway contracts;
- schema/code generation;
- SDK;
- shared UI system;
- CLI;
- TUI;
- Studio feature;
- experimental visualization;
- backend/research changes.

Frontend work MUST remain reviewable independently from changes that claim scientific lift.

### 18.4 Documentation set

The implementation should maintain:

- frontend architecture ADR;
- Client Gateway protocol;
- contract/version registry;
- UI semantic language;
- component catalog;
- CLI reference;
- observability and evidence guide;
- agent-building guide;
- experiment and promotion guide;
- threat model;
- deployment/runbook;
- product validation reports.

---

## 19. Delivery roadmap

### Phase F0 — Contract and gateway foundation

**Goal:** make the backend safely consumable without UI-specific imports.

Deliverables:

- frontend architecture ADR and authority boundary;
- Client Gateway with compatibility handshake;
- generated TypeScript contract pipeline;
- SDK transports and problem contract;
- run start/query/event-stream vertical slice;
- fake gateway and golden trajectory fixtures;
- clean workspace bootstrap.

Exit gate: a TypeScript script starts a real isolated run, reconnects, retrieves final projection and verifies an artifact.

### Phase F1 — Product CLI and M-4 Observatory

**Goal:** expose immediate product value and trajectory evidence.

Deliverables:

- installable CLI;
- coding agent start/watch/inspect/export;
- event tail, artifact inspection and verification;
- external clean-repository coding test;
- M-4 context, model, tool, cost, failure and outcome views;
- product-gate report.

Exit gate: held-out coding task completed from outside the AETHER repository with evidence export.

### Phase F2 — TUI and M-5a projections

**Goal:** interactive operation over event-derived state.

Deliverables:

- run console, event timeline and inspector;
- AgentView projection panel;
- checkpoint/reconstruction diagnostics;
- context provenance and compaction view;
- reconnect/gap recovery UX;
- coding and formal/non-coding agent selection.

Exit gate: live and cold-reconstructed TUI state are semantically equal.

### Phase F3 — Agent Builder and M-6 lineage operation

**Goal:** create and operate reusable agents and recursive teams.

Deliverables:

- agent catalog and version detail;
- guided composition builder;
- capability/budget preview;
- nested-lineage tree and recovery states;
- child budget/conservation diagnostics;
- coding, research and mixed agent examples.

Exit gate: a user creates a new agent composition without Kernel change and runs it with a real child lineage.

### Phase F4 — Studio Observatory and M-6.5

**Goal:** debug and measure adaptive behavior.

Deliverables:

- visual timeline, causal graph and architecture overlay;
- progress/confidence/meta-controller views;
- run diff and paired-trial UI;
- bug-report evidence bundle;
- explicit negative/inconclusive experiment states.

Exit gate: a strategy intervention can be traced from signals to directive to outcome and compared against control.

### Phase F5 — Workflow Studio and M-7

**Goal:** define topology as data and compare it with execution.

Deliverables:

- topology schema editor;
- backend validation/lowering preview;
- declared/lowered/realized graph modes;
- direct, planner/executor and critic/reviser templates;
- scheduler/concurrency evidence dashboard;
- ADR-0099 evidence navigation.

Exit gate: three topologies execute through one Runtime and are correctly visualized without workflow authority in the frontend.

### Phase F6 — Memory, Skills and M-8 product gate

**Goal:** expose provenance-safe learning and complete the MVP.

Deliverables:

- context/memory/experience explorer;
- retrieval provenance;
- skill candidate/evaluation/promotion/rollback lifecycle;
- governance separation and signed evidence display;
- clean-room coding, research and mixed-agent validation;
- packaged CLI, TUI and Studio beta;
- tested upgrade and rollback.

Exit gate: measured held-out lift for at least one promoted composition, provenance visible, injected regression detected, rollback tested, and Kernel neutrality evidenced.

### Phase F7 — Hardening after M-8

This phase is allowed to prepare M-9 compatibility but not implement speculative M-9/M-10 ontology.

Deliverables:

- performance and accessibility hardening;
- remote/multi-user authorization where required;
- plugin developer kit;
- stable public SDK;
- desktop packaging decision based on measured need;
- migration support and long-running operational testing.

---

## 20. Work packages

| ID | Package | Depends on | Principal output |
|---|---|---|---|
| FE-001 | Frontend authority ADR | convergence | fixed boundary and refusals |
| FE-002 | Client Gateway protocol | FE-001 | versioned commands/queries/streams |
| FE-003 | Schema-to-TypeScript codegen | FE-002 | generated contracts and validators |
| FE-004 | TypeScript SDK | FE-003 | transport-independent client |
| FE-005 | Fake gateway/testkit | FE-003 | deterministic frontend testing |
| FE-006 | CLI foundation | FE-004 | automation surface |
| FE-007 | External coding gate | FE-006, M-4 | clean-room product evidence |
| FE-008 | TUI foundation | FE-004 | interactive terminal product |
| FE-009 | Event/trajectory views | FE-005, M-4 | timeline and forensic inspector |
| FE-010 | Projection/replay views | FE-009, M-5a | AgentView and checkpoint diagnostics |
| FE-011 | Agent catalog/builder | FE-004 | versioned compositions |
| FE-012 | Lineage explorer | FE-010, M-6 | nested execution operation |
| FE-013 | Studio shell/design system | FE-004 | accessible visual foundation |
| FE-014 | Causal graph/architecture view | FE-009, FE-013 | internal-system visualization |
| FE-015 | Experiment Lab | FE-010, M-6.5 | paired trials and run diff |
| FE-016 | Topology Studio | FE-012, M-7 | declared/lowered/realized graphs |
| FE-017 | Context/memory explorer | FE-010, M-8 | retrieval provenance |
| FE-018 | Skill/governance pipeline | FE-015, M-8 | promotion and rollback UI |
| FE-019 | Mixed-agent templates | FE-011, FE-016 | coding/research collaboration |
| FE-020 | M-8 product acceptance | all above | packaged beta and evidence |

Parallelization rule: contract/SDK work precedes surface divergence. CLI and design-system work may proceed in parallel after FE-004. Each capability is first integrated through the SDK, then rendered in surfaces.

---

## 21. Canonical user journeys

### 21.1 Create a new agent

```text
open Agent Builder
-> choose domain pack or generic starting point
-> declare model policy, tools, context, evaluator and budgets
-> select capabilities and inspect effective scope
-> optionally bind topology/meta-controller/memory policy
-> validate schemas and compatibility in backend
-> run contract and smoke fixtures
-> freeze immutable composition version
-> publish to catalog with evidence and limitations
```

### 21.2 Use an agent

```text
select immutable agent version
-> select isolated project/workspace
-> describe task and attach inputs
-> review capability and budget request
-> start run
-> observe response, effects, lineages and artifacts
-> resolve approvals if needed
-> receive outcome and verifier result
-> export/replay/compare
```

### 21.3 Improve AETHER

```text
identify unexpected behavior in Observatory
-> pin run/event/artifact/composition identities
-> reproduce from ledger or re-execute controlled variant
-> classify contract, mechanism, policy, pack, adapter or UI defect
-> export minimal evidence fixture
-> implement change in correct layer
-> run contract/replay/falsifier/product tests
-> compare regression metrics
-> attach evidence to PR and milestone gate
```

### 21.4 Propose and promote a skill

```text
analyze trajectory corpus
-> produce versioned candidate artifact
-> evaluate in isolated treatment
-> compare against baseline/held-out work
-> independent evaluator attests evidence
-> promoter reviews regression budget and provenance
-> create new composition version using CAS
-> canary/validate
-> promote or rollback
```

### 21.5 Mixed coding and research agents

```text
research lineage gathers evidence and produces cited artifact
-> planner consumes artifact through declared flow
-> coding lineage implements bounded change
-> verifier lineage tests implementation
-> critic reviews evidence and patch
-> parent synthesizes outcome
```

Every step uses ordinary nested lineages, artifacts and capabilities. “Researcher”, “coder” and “critic” are policies/roles in compositions, not Kernel entities.

---

## 22. Product metrics

The frontend program should measure:

- time to install and first successful run;
- task success and verified success;
- operator interventions and approval burden;
- cost, tokens and latency per successful outcome;
- recovery success after restart;
- evidence completeness;
- replay/reconstruction parity;
- agent creation time and validation failures;
- percentage of runs explainable to the relevant causal event/artifact;
- plugin/agent compatibility failures caught before execution;
- regressions caught before promotion;
- frontend crash/error rate and stream gap rate;
- accessibility and keyboard task completion;
- clean-room success outside the source repository.

These metrics must be correlated with composition and contract versions. Product analytics must not leak private task content.

---

## 23. Risks and mitigations

| Risk | Consequence | Mitigation |
|---|---|---|
| Frontend becomes second runtime | divergent truth | gateway-only commands; projections-only reads |
| Graph implies false causality | incorrect debugging | typed edge semantics; sequence distinct from cause |
| Handwritten contract drift | runtime failures | schema generation and CI drift gate |
| Dashboard bloat precedes product | delayed validation | CLI/TUI vertical slice and external gate first |
| Huge ledgers freeze UI | unusable observability | pagination, virtualization, aggregation, worker layout |
| Client cache treated as truth | stale/unsafe decisions | coverage/version labels and resync |
| Plugin leaks secrets | security incident | sandbox, capability scopes, scrubbed previews |
| Self-evaluation promotes itself | epistemic failure | generator/evaluator/promoter separation |
| Agent Builder hardcodes coding | lost generality | generic composition contracts plus domain packs |
| Desktop wrapper locks architecture | maintenance burden | web-first App and replaceable shell |
| UI claims milestone completion | false governance | backend evidence/gate status only |
| Testing inside AETHER contaminates result | invalid product evidence | clean external consumer and sealed tasks |

---

## 24. Final acceptance checklist

### Architecture

- [ ] One backend Runtime, ledger and composition path remain authoritative.
- [ ] CLI, TUI and App use the same SDK and generated contracts.
- [ ] No frontend package imports backend implementation internals.
- [ ] Topology, metacognition, memory and skills remain derived capabilities.

### Agent product

- [ ] Coding, research and mixed agents are cataloged and runnable.
- [ ] New agent compositions can be created without Kernel changes.
- [ ] Capabilities, budgets and immutable versions are visible before execution.
- [ ] External clean-project installation and execution pass.

### Observatory

- [ ] Timeline distinguishes append order, causation and telemetry.
- [ ] Kernel, Runtime, adapters, packs and plugins can be inspected.
- [ ] Lineages, context, artifacts, projections and recovery are navigable.
- [ ] Live and cold-reconstructed views are equivalent.

### Workflows and experimentation

- [ ] Declared, lowered and realized topology views are distinct.
- [ ] Paired runs and one-variable ablations are supported.
- [ ] Negative and inconclusive findings are representable.
- [ ] Run diff exposes divergence and uncertainty.

### Self-improvement

- [ ] Candidate generation, evaluation and promotion authorities are separated.
- [ ] Retrieval and skill use show provenance.
- [ ] Held-out lift is measured.
- [ ] Promotion and real rollback are tested.

### Quality

- [ ] Contract, integration, replay, security, accessibility and performance gates pass.
- [ ] Errors and degraded states are explicit and actionable.
- [ ] Packages, docs and examples are independently installable.
- [ ] M-8 product evidence is accepted, not merely marked package-ready.

---

## 25. Final directive

Implement this frontend as an external product and scientific interface over AETHER's existing substrate. Start with the contract gateway, SDK and clean-room CLI proof; add the TUI for continuous operational feedback; then build the Studio around the same projections and commands. Every visual feature must answer one of four questions: what was configured, what happened, why it was admissible, and what evidence supports the outcome.

The completed system should make AETHER tangible. A developer will be able to build an agent, run it, observe its causal trajectory, inspect context and artifacts, understand Kernel-versus-plugin responsibility, reproduce failures, compare strategies and topologies, validate generality, and promote improvements under evidence and rollback. The frontend therefore closes the gap between a rigorous event-sourced framework and a useful family of coding, research and mixed-agent products—without weakening the small, domain-blind and scientifically falsifiable foundation that gives AETHER its long-term value.
