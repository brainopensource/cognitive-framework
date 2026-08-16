# CLI/TUI architecture and runtime-client contract

Status: `APPROVED — Tech Lead, frontend foundation scope`
Decision date: 2026-08-15
Applies to: T6.4/T6.5 frontend scaffolding before S6 and production integration during S3-S6
Authority: implementation-level client interface under the approved ICD; this document does not amend VG-04 wire schemas, authority paths, or sprint exit gates

## 1. Decision

T6.4 frontend work may proceed before the engine is complete. It must remain a client of the runtime and may not become a seventh core package, a second event model, a policy authority, or a substitute process engine.

The permanent location is `vanguard/clients/cli/`, outside `vanguard/packages/`. The six directories under `vanguard/packages/` remain the complete core package set. The scaffold has been relocated to that client boundary. This changes no core boundary and requires no new ADR because it restores conformance with the approved ICD.

The frontend architecture is hexagonal:

```text
terminal / JSONL
       |
presentation: Ink screens, reusable components, formatters
       |
application: run/trace/why use cases, reducers, selectors
       |
outbound client port: RuntimeClient
       |
mock adapter | replay adapter | future IPC/HTTP adapter
       |
runtime composition root -> ledger/process/engine
```

Dependencies point inward. Presentation depends on application contracts. Application code depends on the client port and parsed domain types. Adapters depend on the client port. The application and presentation layers never import runtime internals, kernel, agency, concrete adapters, transport libraries, process globals, or filesystem APIs.

## 2. Minimum client contract v0.1

This is a client API, not a durable wire schema and not a new core `Port`. Its implementation belongs to the runtime-client adapter. The TypeScript source must expose equivalent semantics to the following:

```ts
type ClientContractVersion = "0.1";
type StreamSource = "mock" | "replay" | "live";

type ClientFailure = {
  code:
    | "invalid_request"
    | "not_found"
    | "conflict"
    | "not_available"
    | "permission_denied"
    | "transport_interrupted"
    | "incompatible_version";
  message: string;
  retryable: boolean;
  details?: Readonly<Record<string, unknown>>;
};

type Result<T> =
  | { ok: true; value: T }
  | { ok: false; error: ClientFailure };

type EventCursor = { runId: RunId; afterSeq?: IntString };
type StreamItem = {
  contractVersion: ClientContractVersion;
  source: StreamSource;
  envelope: EventEnvelope;
};

interface RuntimeClient {
  startRun(request: StartRunRequest, signal?: AbortSignal): Promise<Result<RunRef>>;
  streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>>;
  getRun(runId: RunId, signal?: AbortSignal): Promise<Result<RunSnapshot>>;
  requestCancel(runId: RunId, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  requestCheckpoint(runId: RunId, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  requestResume(request: ResumeRunRequest, signal?: AbortSignal): Promise<Result<RunRef>>;
  explainArtifact(artifactId: ArtifactId, signal?: AbortSignal): Promise<Result<ArtifactExplanation>>;
  resolveApproval(request: ResolveApprovalRequest, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
}
```

Required semantics:

1. `startRun`, cancel, checkpoint, resume and approval methods submit requests; a successful receipt does not claim that the requested state transition completed. Completion is learned from canonical events.
2. `streamEvents` carries parsed VG-04 `EventEnvelope` values. The client must preserve unknown event kinds and unknown reader fields.
3. Resume uses a durable run/checkpoint identity, never in-memory UI state. Reconnect uses `afterSeq` and deduplicates by `eventId`; ordering uses the writer-assigned decimal-string `seq`, never timestamps.
4. Cancellation uses `AbortSignal` for the local operation and `requestCancel` for the durable run. These are distinct actions.
5. `resolveApproval` is present for UI composition and mock scenarios, but its live adapter remains unavailable until T4.8/T6.6. It may never call agency or authorise an effect directly.
6. `ArtifactExplanation` is a read projection containing activation evidence references, prediction, invalidation/demotion conditions, and projection freshness. It must not invent evidence absent from the governance/evidence stores.
7. Transport, parsing, incompatibility and domain rejection are typed failures. Rendering code does not recover semantics from exception text.
8. Secrets and unrestricted payloads never enter diagnostics. The live trace consumes the redacted operational projection, not raw encrypted audit material.

`StartRunRequest`, `RunSnapshot`, `CommandReceipt`, `ResumeRunRequest`, `ArtifactExplanation`, and `ResolveApprovalRequest` are client projections. Their fields may be drafted in the frontend package, but any field that claims durable identity, ledger state, authority, or wire meaning must reference an approved domain/schema type rather than redefine it.

## 3. Event and state rules

There is one durable event vocabulary: VG-04. Names such as `run.started`, `progress`, `token`, or `checkpoint.created` may exist only as local mock scenario instructions or presentation categories; they must not be emitted as ledger events or exported as if canonical.

The UI derives its state through a pure reducer:

```text
EventEnvelope[] -> reduceRunView(previous, envelope) -> RunViewModel
RunViewModel -> selectors -> screen props
```

The reducer must be deterministic, side-effect free, exhaustive only over locally closed UI state, and tolerant of unknown wire events. Components receive view models and callbacks; they do not inspect transport responses or mutate domain state.

Keep three states visibly distinct:

- backend truth: parsed envelopes and query snapshots;
- application state: cursor, connection status, pending command receipts and reduced views;
- presentation state: focus, selected row, panel visibility and local filter text.

Optimistic UI may show a command as `requested`; it must not show `cancelled`, `approved`, `checkpointed`, or `resumed` until the corresponding canonical event or refreshed snapshot confirms it.

## 4. Adapter boundary and fakes

Implementations of `RuntimeClient` are replaceable adapters:

- `ScenarioRuntimeClient`: deterministic scripted scenarios using injected clock, IDs and seed; no timers in contract tests;
- `ReplayRuntimeClient`: reads validated JSONL fixtures and supports cursor/reconnect behavior;
- `LiveRuntimeClient`: future authenticated IPC/HTTP client with version negotiation, bounded frames, cancellation, backpressure and a separate diagnostics channel.

Every adapter runs the same contract suite. The suite covers ordering, unknown events, cancellation, reconnect, duplicate delivery, malformed input, incompatible versions, backpressure, typed failures and secret-free diagnostics. Mock output must be visibly labelled `source: mock`; it cannot be used as acceptance evidence for backend behavior, security, persistence, recovery or approval correctness.

Scenarios are declarative fixtures, not branches embedded in the fake. Minimum fixtures are:

- successful episode;
- authorization denial;
- pending and resolved approval;
- cancel requested then confirmed;
- checkpoint requested then confirmed;
- interrupted stream, reconnect and duplicate delivery;
- resume from durable checkpoint;
- failed and undeterminable effect;
- unknown future event;
- active, inactive and unknown artifact explanation.

## 5. Module structure

Use this target structure after relocation:

```text
vanguard/clients/cli/
  src/
    contract/       client API, Result/failure types, validated projections
    application/    run/trace/why use cases, reducers, selectors
    adapters/       scenario, replay and live runtime clients
    headless/       JSONL serializers, exit-code mapping, non-TTY behavior
    tui/
      components/   small reusable visual components
      screens/      route-level composition only
      hooks/        stream lifecycle, keys, terminal capabilities
      theme/        semantic color, spacing and symbols
    composition/    dependency construction and command routing
  fixtures/         versioned deterministic scenarios and replay ledgers
  test/             contract, reducer, component and CLI tests
```

Start with these reusable components: `RunSummary`, `ConnectionBadge`, `EventTimeline`, `EventDetails`, `ProgressSummary`, `EffectPreview`, `ApprovalPrompt`, `CheckpointList`, `FailureNotice`, `WhyEvidence`, `KeyHints` and `EmptyState`. Components remain domain-light; selectors convert the view model to component props.

Do not create a generic component framework. Extract a reusable component after two real uses or when it owns a clear terminal behavior such as virtualized lists, focus, truncation or keyboard hints.

## 6. Development order and integration gates

Follow this order:

1. **Boundary correction (complete):** the prototype is under `vanguard/clients/cli`; workspace paths and boundary CI restrict clients to domain/public runtime-client surfaces.
2. **Contract package:** implement v0.1 client types, parsing boundary, typed failures and adapter contract suite. Replace the prototype's custom `RuntimeEvent` with canonical-envelope fixtures plus local view categories.
3. **Reducer and selectors:** implement deterministic run, trace and explanation view models; test replay, duplicates, unknown events and large streams.
4. **Headless first:** implement stable JSONL, exit codes, signal handling, no-color behavior and golden CLI tests. This is the S3-S5 integration probe.
5. **Scenario and replay adapters:** add the required fixtures, controllable streams and a `--scenario`/`--replay` workflow.
6. **TUI foundation:** add routing, layout, focus, bounded/virtualized timelines, resizing, keyboard help, loading/empty/error states and clean shutdown.
7. **Basic screens:** ship run dashboard, trace inspector and why inspector using only selectors and reusable components.
8. **S3 integration:** connect the live adapter to event-store/runtime trace and prove reconnect, ordering, redaction and unknown-event behavior. Keep run mutations mocked if unavailable.
9. **S4 integration:** connect episode lifecycle, cancellation, durable checkpoints and resume. Add approval display only after the process contracts exist; enable approval mutation only after T4.8 contract tests pass.
10. **S5 integration:** connect context/evidence projections and make `vg why` factual. Add freshness and unavailable states rather than mock fallbacks in live mode.
11. **S6 completion:** connect typed tools, descriptor-bound approvals and correction capture; run substitution-after-approval must-fail tests and latency gates.
12. **Production hardening:** package the binary, test supported terminals, benchmark startup/render/event throughput, and document live/mock/replay modes.

A live adapter may replace one method at a time. It must return `not_available` for unsupported operations; live mode must never silently fall back to mock data.

## 7. Engineering rules

- Keep business and reduction logic in `.ts`; use `.tsx` only for rendering/composition.
- Prefer pure functions, readonly inputs and explicit dependency injection. No module-level mutable runtime singleton.
- One stream subscription owner per screen/use case. Cleanup and `AbortController` ownership must be explicit.
- Bound retained events and rendered rows. Use incremental reduction and virtualization; never rerender an unbounded ledger.
- Use semantic theme tokens and respect `NO_COLOR`. Information must never depend on color alone.
- Keyboard actions go through commands/use cases. Components do not call runtime adapters directly.
- Keep headless and TUI paths on the same application use cases and reducers. Only presentation differs.
- Separate stdout machine output from stderr diagnostics. JSONL stdout remains parseable during warnings and reconnects.
- Validate every external object at the adapter edge. Never use a TypeScript cast as parsing.
- Preserve causality and identity exactly. Never generate missing backend IDs in presentation code.
- Avoid barrel files across architectural layers, service locators, inheritance hierarchies and speculative generic abstractions.
- Pin dependency versions, minimize terminal dependencies and measure startup cost before adding state or styling libraries.
- Tests use fake clocks and deterministic IDs; timing sleeps are prohibited in contract/reducer tests.

## 8. Required verification

Before live integration, require:

- adapter contract tests passing for scenario and replay clients;
- reducer property tests for idempotence under duplicate delivery and stable replay state;
- golden tests for JSONL and exit codes;
- component tests for keyboard, focus, narrow terminals and no-color output;
- smoke tests for run, trace, why, cancel, checkpoint and resume scenarios;
- bounded-memory and render-throughput benchmarks on a large synthetic ledger;
- boundary CI proving no client import reaches kernel, agency, concrete adapters or runtime internals.

At each backend sprint integration, add the live adapter to the same contract suite. Mock tests prove frontend behavior only; the corresponding feature becomes production-ready only when its live conformance and governing backend acceptance tests pass.

## 9. Change control

The client contract uses semantic versions independently from the VG-04 schema version. Additive projection fields and methods may bump the client minor version. Removing or changing semantics requires a client major version and compatibility test updates.

This approval does not authorize changes to `EventEnvelope`, event meanings, effect authority, approval semantics, package boundaries or process ownership. Such changes follow ICD Section 8: ADR with reversal condition and linked Active MVP Contract rows. If implementation discovers a missing durable field, record the need and stop at the adapter boundary; do not solve it in UI types.
