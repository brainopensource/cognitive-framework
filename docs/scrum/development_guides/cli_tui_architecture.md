# CLI/TUI architecture and runtime-client contract

Status: `APPROVED — Tech Lead, frontend foundation scope`  
Decision date: 2026-08-15  
Revision: 1.1 (2026-08-16 — binding tree, live-socket appendix, `--demo` labelling, fixture catalog)  
Applies to: `vanguard/clients/cli/**` (lane FE-A)  
Authority: implementation-level client interface under VG-04 and ADR-0062; this document does not amend VG-04 wire schemas, authority paths, or backend sprint exit gates  
Parent lock: `docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md`

## 1. Decision

T6.4 frontend work may proceed before the engine is complete. It must remain a client of the runtime and may not become a seventh core package, a second event model, a policy authority, or a substitute process engine.

The permanent location is `vanguard/clients/cli/`, outside `vanguard/packages/`. The six directories under `vanguard/packages/` remain the complete core package set. This changes no core boundary and requires no new ADR.

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
scenario adapter | replay adapter | live vg.4-frame adapter
       |
RuntimeService daemon (Unix domain socket)
```

Dependencies point inward. Presentation depends on application contracts. Application code depends on the client port and parsed domain types. Adapters depend on the client port. The application and presentation layers never import runtime internals, kernel, agency, concrete adapters, transport libraries, process globals, or filesystem APIs.

**Binding (rev 1.1):** the target tree in §5 is the required layout after FE-A4. `src/ui/` is a transitional path until that move lands.

## 2. Minimum client contract v0.1

This is a client API, not a durable wire schema and not a new core `Port`. Source of truth: `vanguard/clients/cli/src/contract/types.ts` and `parse.ts`. Semantics:

```ts
type ClientContractVersion = "0.1";
type StreamSource = "mock" | "replay" | "live";

interface RuntimeClient {
  startRun(request: StartRunRequest, signal?: AbortSignal): Promise<Result<RunRef>>;
  streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>>;
  getRun(runId: RunId, signal?: AbortSignal): Promise<Result<RunSnapshot>>;
  requestCancel(runId: RunId, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  requestCheckpoint(runId: RunId, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  requestResume(request: ResumeRunRequest, signal?: AbortSignal): Promise<Result<RunRef>>;
  explainArtifact(artifactId: ArtifactId, signal?: AbortSignal): Promise<Result<ArtifactExplanation>>;
  resolveApproval(request: ResolveApprovalRequest, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  recordCorrection(record: CorrectionRecord, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  getDaemonStatus(signal?: AbortSignal): Promise<Result<DaemonStatus>>;
}
```

Required semantics:

1. Command methods submit requests; a successful receipt does not claim the durable transition completed. Completion is learned from canonical events.
2. `streamEvents` carries parsed VG-04 `EventEnvelope` values. Preserve unknown event kinds and unknown reader fields (`CT-11`, `CT-44`).
3. Resume uses a durable run/checkpoint identity. Reconnect uses `afterSeq` and deduplicates by `eventId`; ordering uses writer-assigned decimal-string `seq`.
4. `AbortSignal` cancels the local operation; `requestCancel` cancels the durable run.
5. Live `resolveApproval` must send a signed `ApprovalDecision` whose digests come from the challenge (FE-A8). Do not call agency or authorise an effect in the client.
6. `explainArtifact` is a read projection. If the daemon has no explanation, return `not_available`; do not invent evidence.
7. Transport, parsing, incompatibility and domain rejection are typed `Result` failures (`CT-03`: parse, never cast).
8. Secrets and unrestricted payloads never enter diagnostics.

Field types that claim durable identity must reference VG-04 / schema types rather than redefine them.

Live frame verbs and socket path order: **Appendix A**. Do not restate the daemon contract here.

## 3. Event and state rules

There is one durable event vocabulary: VG-04 §12.2. Names such as `run.started`, `progress`, `token`, or `checkpoint.created` may exist only as local mock scenario instructions or presentation categories; they must not be emitted as ledger events or exported as if canonical.

The UI derives its state through a pure reducer:

```text
EventEnvelope[] -> reduceRunView(previous, envelope) -> RunViewModel
RunViewModel -> selectors -> screen props
```

Keep three states visibly distinct:

- backend truth: parsed envelopes and query snapshots;
- application state: cursor, connection status, pending command receipts and reduced views;
- presentation state: focus, selected row, panel visibility and local filter text.

Optimistic UI may show a command as `requested`; it must not show `cancelled`, `approved`, `checkpointed`, or `resumed` until the corresponding canonical event or refreshed snapshot confirms it.

## 4. Adapter boundary and fakes

Implementations of `RuntimeClient` are replaceable adapters:

- `ScenarioRuntimeClient`: deterministic scripted scenarios; no timers in contract tests;
- `ReplayRuntimeClient`: reads validated JSONL fixtures; supports cursor/reconnect;
- `LiveRuntimeClient`: vg.4 NDJSON over UDS (Appendix A), bounded frames, cancellation, backpressure.

Every adapter runs the same contract suite. Mock and replay output must be visibly labelled **`source: mock`** (replay may additionally show fixture id). They cannot be used as acceptance evidence for backend behavior, security, persistence, recovery or approval correctness.

### 4.1 `--demo` mock-labelling (binding)

`--demo` (FE-A6, to-build) is replay of catalogued fixtures. Rules:

1. The TUI chrome and headless JSONL `StreamItem.source` must not be `live`.
2. Visible label: `source: mock` (and fixture name). Color is not sufficient (`NO_COLOR`).
3. `vg --demo` must not open the runtime socket unless the operator also passes an explicit live flag (default: no socket).
4. Demo is not a substitute for live conformance tests.

### 4.2 Fixture catalog (binding)

Canonical location: `vanguard/clients/cli/fixtures/`. Session scenarios for `--demo` land under `fixtures/sessions/` (FE-A6/A10).

**Shipped today:**

| File | Covers |
|---|---|
| `fixtures/successful-episode.jsonl` | Happy-path episode envelopes |
| `fixtures/why-typed-tools.jsonl` | Why / typed-tool projection |

**Required catalog (architecture §4 + FE-A10).** Each row is a named JSONL (or session dir) with VG-04 kinds only:

| Fixture id | Required coverage |
|---|---|
| `successful-episode` | `EpisodeStarted` … `EpisodeCompleted` |
| `authorization-denied` | `AuthorizationDenied` |
| `approval-pending-resolved` | `ApprovalRequested`, `ApprovalResolved` |
| `cancel-requested-confirmed` | cancel command + confirming events |
| `checkpoint-requested-confirmed` | checkpoint command + confirming events |
| `stream-interrupt-reconnect` | interrupted stream, reconnect, duplicate `seq` |
| `resume-from-checkpoint` | durable resume |
| `effect-failed-undeterminable` | `EffectCompleted` failure / `EffectReconciled` uncertainty |
| `unknown-future-event` | unknown `payload.kind` preserved |
| `why-artifact-active-inactive-unknown` | explanation statuses |
| `why-typed-tools` | typed tools why path |

Subagent / multi-agent demo scenarios are **Phase-2 deferred (DEF-03)** — do not add them as live product claims.

Scenarios are declarative fixtures, not branches in the fake.

## 5. Module structure (binding after FE-A4)

```text
vanguard/clients/cli/
  src/
    contract/       client API, Result/failure types, validated projections
    application/    run/trace/why use cases, reducers, selectors
    adapters/       scenario, replay, live (FeedTransport / SocketTransport), signer
    headless/       JSONL serializers, exit-code mapping, non-TTY behavior
    tui/
      components/   small reusable visual components
      screens/      route-level composition only
      hooks/        stream lifecycle (`useVanguardRun`), keys, terminal capabilities
      theme/        semantic color, spacing and symbols
    composition/    dependency construction and command routing
  fixtures/         versioned deterministic scenarios and replay ledgers
  fixtures/sessions/  --demo catalog (FE-A6)
  test/             contract, reducer, component, CLI, soak (not tools/ci/)
```

**Transitional (until FE-A4):** `src/ui/`, `src/tui.tsx`, `src/main.tsx`. Dead files deleted in FE-A1: `src/commands.ts`, `src/runtime.ts`, `src/mock-runtime.ts`. `adapters/signer.ts` stays and is wired for signed approvals.

Start with these reusable components: `RunSummary`, `ConnectionBadge`, `EventTimeline`, `EventDetails`, `ProgressSummary`, `EffectPreview`, `ApprovalPrompt`, `CheckpointList`, `FailureNotice`, `WhyEvidence`, `KeyHints` and `EmptyState`.

Do not create a generic component framework. Extract a reusable component after two real uses or when it owns a clear terminal behavior.

## 6. Development order and integration gates

Lane kits in `docs/scrum/sprints_front/` replace the old S3–S6 numbered frontend story. Order of meaning:

1. Boundary (complete): client under `vanguard/clients/cli`.
2. Contract + parse + adapters (in progress).
3. Reducer/selectors; headless JSONL.
4. FE-A1–A5 hygiene and protocol truth.
5. FE-A6–A10 product surface (`--demo`, honest daemon, approvals, distro, fixtures).
6. Live conformance is proven by VG-04 vectors + `test/contracts/t1_wire_contracts.py` + CLI live tests — not by mock green.

A live adapter may replace one method at a time. Unsupported operations return `not_available`. Live mode must never silently fall back to mock data.

## 7. Engineering rules

- Keep business and reduction logic in `.ts`; use `.tsx` only for rendering/composition.
- Prefer pure functions, readonly inputs and explicit dependency injection. No module-level mutable runtime singleton.
- One stream subscription owner per screen/use case. Cleanup and `AbortController` ownership must be explicit.
- Bound retained events and rendered rows.
- Semantic theme tokens; respect `NO_COLOR`.
- Keyboard actions go through commands/use cases. Components do not call runtime adapters directly.
- Headless and TUI share application use cases and reducers.
- Separate stdout machine output from stderr diagnostics.
- Validate every external object at the adapter edge. Never use a TypeScript cast as parsing (`CT-03`).
- Preserve causality and identity exactly. Never generate missing backend IDs in presentation code.
- Avoid barrel files across architectural layers.
- Tests use fake clocks and deterministic IDs; timing sleeps are prohibited in contract/reducer tests.

## 8. Required verification

- `cd vanguard/clients/cli && npm run typecheck && npm test`
- Adapter contract tests for scenario and replay
- Reducer tests: duplicates, unknown events, bounded buffer
- Golden tests for JSONL and exit codes
- Component tests: keyboard, focus, narrow terminals, no-color
- Boundary CI: no client import of kernel, agency, or `vanguard/packages`
- Live methods: `not_available` rather than mock fallback

## 9. Change control

The client contract uses semantic versions independently from the VG-04 schema version. Additive projection fields and methods may bump the client minor version. Removing or changing semantics requires a client major version.

This approval does not authorize changes to `EventEnvelope`, event meanings, effect authority, approval semantics, package boundaries or process ownership. Missing durable fields become Joint notes (D6). Do not solve them in UI types.

---

## Appendix A — Live socket frames (consumer)

Normative: VG-04 §0, §12, §15; ADR-0062; implementation `vanguard/packages/runtime/service/server.py` + `service.py`. FE does not add verbs.

**Transport:** Unix domain socket, NDJSON lines, `version: "vg.4"`. Max frame **1 MiB** (`MAX_FRAME_BYTES`). Socket file mode 0600 on the daemon side.

**Path resolution (CLI, binding):** `--socket-path` → env `VANGUARD_RUNTIME_SOCKET` → `/tmp/vanguard-runtime.sock`.

**Client command frame:** `frameType: "command"` with `command.{name,commandId,idempotencyKey,runId,actor,payload}`.

**Implemented command names:** `StartRun`, `GetRun`, `StreamEvents`, `ResolveApproval`, `Cancel`, `Checkpoint`, `Resume`, `RecordCorrection`, `ExplainArtifact`.

**Responses:** `frameType: "receipt"` (`receipt.status` completed/error) or `frameType: "error"`. Event stream: `frameType: "event"` with `event` envelope.

**Not implemented (do not call; Joint if needed):** `Ping`, `ListManifests`, Named Pipe, TCP.

**StartRun payload (existing shape):** `manifestPath`, `repoPath`, `brief`. Editor context (FE-B6) must fold into `brief` unless Joint adds a field.

---

## Appendix B — FE-B vendoring

FE-A owns `src/contract/` and `adapters/signer.ts`. FE-B copies them into `vanguard-ide/src/contract/` as a build step. The extension must not import `vanguard/clients/cli` at runtime.
