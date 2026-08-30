---
id: research.frontend-integration-plan
kind: research
status: historical-reference
authority: non-canonical
summary: "Frontend-to-runtime integration dossier and archival reference."
topic:
  - frontend
---

# AETHER / Vanguard frontend-to-runtime integration dossier

## 0. Status, authority, and implementation rule

This document is an implementation-ready technical review, not an authorization source. It lives
under `_archive/`, so it cannot amend the Vision, specification, ADRs, schemas, milestone gates, or
active sprint. Before starting a slice from this plan, copy its bounded work package into
`docs/03_execution/sprint_active.md` through the repository's normal leadership process. If this
plan conflicts with a canonical source, the canonical source wins.

Authority order for this work:

1. `VISION.md` — constitutional identity and product direction.
2. `docs/SPEC.md` and `docs/01_law/` — normative invariants.
3. accepted ADRs — binding decisions reflected in law.
4. `schemas/v4/` and canonical protocol documents — wire contracts.
5. `docs/03_execution/milestones.md` — stable gates.
6. `docs/03_execution/sprint_active.md` — sole current authorization.
7. this dossier — advisory implementation decomposition only.

The integration is governed by one rule:

> The Python runtime owns execution and durable truth. Stdio, UDS, HTTP, and SSE are replaceable
> transport adapters over one command vocabulary, one event contract, and event-derived read
> models. A frontend and gateway never become a second runtime, ledger, policy engine, or authority.

The minimum useful product outcome is not “all 45 routes exist.” It is a vertical slice in which a
real run can be started, observed, approved, interrupted, resumed, and reconstructed identically
through CLI/TUI and Studio. Route count is an inventory; accepted behavior is the gate.

## 1. Verified baseline and corrections to the previous plan

The following statements are verified against the repository on 2026-08-27:

- `Runtime.execute_profiled()` is the canonical profiled execution seam.
- `RuntimeService` and `RuntimeServer` already implement a partial vg.4 UDS service.
- `studio_gateway.py` still starts `_pilot_run_simulation()` and emits synthetic, incomplete events.
- the service's `ServiceInboxStore.event_outbox` and production `SqliteEventStore.events` are
  separate event histories; exposing both as truth would violate event-sourcing invariants.
- `HttpRuntimeClient` implements only a subset of `RuntimeClient` and returns placeholders for run
  snapshots.
- the Studio browser entry bypasses `@vanguard/client-core` for health, SSE, and approval calls.
- the HTTP approval body and `RuntimeService._cmd_ResolveApproval()` disagree on shape.
- gateway-generated event IDs and envelopes do not satisfy the TypeScript vg.4 parser.
- no installed Python console script starts `RuntimeServer`; smoke commands must not pretend one
  exists until a daemon entrypoint is implemented.
- M-7 runtime integration is incomplete and M-8 is not authorized by current execution state.

Corrections applied by this dossier:

1. Do not create a second “service event store.” The canonical event store is the runtime ledger.
   The command inbox may be a separate delivery/idempotency table, but it is not causal truth.
2. Do not have the gateway call `Runtime.execute_profiled()` directly. All command transports call
   the same `RuntimeService` application boundary; its injected runner reaches the runtime.
3. Do not broadcast objects as if they were events. Commit a schema-valid `EventEnvelope` through
   the sole ledger writer first; stream readers then tail committed truth.
4. Do not freeze 45 improvised payloads inside one generic schema. Define a closed command union and
   generated readers before exposing routes.
5. Do not implement M-7/M-8 mutation routes merely to satisfy a frontend screen. Capability
   discovery must distinguish `absent`, `read_only`, `experimental`, and `available`.
6. Do not store browser signing keys in source, localStorage, event payloads, or gateway memory.
7. Do not claim server cursor support unless reconnect, gap, race, and fresh-process tests pass.

## 2. Non-negotiable architecture

```text
                                      COMMAND PLANE
       vg/Ink ── UDS NDJSON ─┐
                             ├──> RuntimeService ──> RuntimeRunner ──> Runtime.execute_profiled
 Studio ── HTTP JSON ────────┘          │                    │
                                        │                    └── canonical composition/runtime
                                        └── command inbox (idempotency, not causal truth)

                                      STATE PLANE
 Runtime / LedgerEmitter ── append ──> EventStorePort ──> SQLite WAL `events`
                                              │
                                              ├──> event-derived query projections
                                              ├──> UDS `StreamEvents`
                                              ├──> HTTP historical reads
                                              └──> SSE tailer

                                    ARTIFACT PLANE
 Runtime / ArtifactWriter ────────────────> BlobStorePort / content-addressed blobs
                                              │
                                              └──> authorized metadata/content reads

                                    CLIENT PLANE
 @vanguard/client-core = contracts + transport ports + parsers + reducers + signer port
               ├──> @vanguard/cli (commands and Ink presentation)
               └──> @vanguard/studio (browser presentation)
```

### 2.1 Layer placement

| Concern | Legal location | Forbidden placement |
|---|---|---|
| Wire values and generated readers | `domain/`, schemas, TS domain package | handwritten UI mirrors |
| Transport/application protocols | `ports/` or client-core ports | Kernel branches |
| Command coordination and projections | `runtime/service/` | adapters or frontend reducers with authority |
| Runtime composition | `runtime/root.py`, bootstrap/wiring | HTTP handler |
| SQLite, HTTP server, UDS, blob implementation | `adapters/` or runtime edge composition | domain/kernel |
| UI folds and presentation | `@vanguard/client-core`, CLI, Studio | Python causal truth |
| Approval verification | runtime governance boundary | gateway or UI |

No integration phase may add imports to `vanguard/packages/kernel/`. The kernel remains domain-blind,
and its TCB budget remains `<=1438` logical LOC.

### 2.2 One write path, many read paths

Commands may enter over three transports, but they normalize to the same command value and handler.
Queries may have transport-specific framing, but they derive from the same durable events and
artifacts. A read model may be cached; it must be rebuildable and carry its reducer/schema version
and `asOfSeq`.

`ServiceInboxStore` is allowed to own:

- command ID and idempotency key;
- actor/authentication context reference;
- accepted/completed/rejected delivery state;
- serialized command receipt;
- operational lease/heartbeat needed to recover command handling.

It must not remain an alternative event ledger after migration. Remove or retire
`event_outbox` only through a compatibility migration that preserves existing test fixtures and
documents how legacy rows are read. Do not silently discard a file-backed service database.

## 3. Canonical transport matrix

| Property | Stdio | UDS | HTTP/SSE |
|---|---|---|---|
| Primary users | `vg code`, `vg doctor` | CLI and Ink TUI | browser Studio |
| Framing | one NDJSON request/result per line | vg.4 NDJSON frames | JSON command/query + SSE event frames |
| Process model | child process, no daemon | long-lived local daemon | loopback gateway over same service |
| Command semantics | coding projection request | canonical runtime commands | canonical runtime commands |
| Streaming | no; final structured result | `StreamEvents` | SSE plus historical query |
| Resume cursor | request field if supported | `afterSeq` IntString | `afterSeq` / `Last-Event-ID` |
| Authentication | parent process identity/env | peer UID + socket `0600` | same-origin session + operator identity |
| Required parity | outcome projection | command/event semantics | command/event semantics |

Stdio is intentionally not forced into the daemon protocol. It is a fast product bridge with its
own closed request/result schema, but it must call the same runtime bootstrap and may not implement
another execution engine.

## 4. Contract model

### 4.1 Version vocabulary

Do not conflate these identifiers:

- `schemaVersion: "vg.4"` — event wire family currently parsed by clients.
- `version: "vg.4"` — RuntimeService frame family.
- `mhf.event/2` — canonical writer format named by law and milestones.
- `contractVersion: "0.1"` — current client-core stream wrapper version.
- package versions — sourced from each package manifest.

The contract-freeze slice must decide and test the exact mapping between `vg.4` and
`mhf.event/2`; comments and aliases are insufficient. Writers single-write the active canonical
format; compatibility readers may dual-read only where law allows it.

### 4.2 RuntimeService frame algebra

The schema must be a discriminated `oneOf`, not a loose object with optional `command`, `receipt`,
`event`, and `error` fields.

```text
RuntimeServiceFrame = CommandFrame | ReceiptFrame | EventFrame | ErrorFrame

CommandFrame = {
  version, frameType="command", frameId,
  command: CommandEnvelope
}

ReceiptFrame = {
  version, frameType="receipt", frameId,
  inReplyTo, receipt: CommandReceipt
}

EventFrame = {
  version, frameType="event", frameId,
  event: EventEnvelope
}

ErrorFrame = {
  version, frameType="error", frameId,
  inReplyTo?, error: ServiceError
}
```

Closed command union for the first integration release:

```text
Command = StartRun
        | GetRun
        | ListRuns
        | StreamEvents
        | Cancel
        | Checkpoint
        | Resume
        | ResolveApproval
        | RecordCorrection
        | ExplainArtifact
        | GetCapabilities
```

`ListRuns` currently appears in the gateway but is absent from
`runtime-service.schema.json`; either add it to the closed union with tests or remove its use. No
handler may exist only by Python `getattr` convention without schema membership.

### 4.3 Command envelope

```json
{
  "name": "StartRun",
  "commandId": "018f...",
  "idempotencyKey": "018f...",
  "runId": "run-...",
  "actor": "operator:local",
  "expectedSeq": "0",
  "payload": {}
}
```

Rules:

- `commandId` identifies one attempt; `idempotencyKey` identifies one logical command.
- retries reuse `idempotencyKey` and may use a new `commandId` only if the schema explicitly permits
  attempt identity; the service always returns the first terminal logical receipt.
- `runId` is required for run-scoped commands and forbidden only where a specific command contract
  says so.
- `expectedSeq` is an IntString CAS precondition for state-sensitive commands.
- actor identity comes from authenticated transport context. A payload cannot self-assert a more
  privileged actor.
- unknown fields fail closed.

### 4.4 Command payloads and results

| Command | Required request fields | Success result | CAS/security notes |
|---|---|---|---|
| `StartRun` | `manifestPath`, `repoPath`, `brief`, `profileId` | `runId`, `episodeId`, `status`, `acceptedAt` | canonicalize repo path; profile must fail closed |
| `GetRun` | none | `RunSnapshot` | event-derived, includes `asOfSeq` |
| `ListRuns` | cursor/page limit/filter | `RunPage` | stable sort by durable identity, not active threads |
| `StreamEvents` | `afterSeq` | event frames | run authorization checked before each attach |
| `Cancel` | `reason`, `expectedSeq` | receipt | idempotent terminal transition |
| `Checkpoint` | `expectedSeq` | `checkpointId`, digest, seq | checkpoint is cache/evidence, not truth replacement |
| `Resume` | `checkpointId?`, `expectedSeq` | run ref and recovery mode | cold-fold fallback on invalid checkpoint |
| `ResolveApproval` | complete signed decision, `expectedSeq` | resolution receipt | one terminal decision; signature verified |
| `RecordCorrection` | schema-valid correction, `expectedSeq` | event ID and seq | correction reader validates scope rules |
| `ExplainArtifact` | `artifactId`, optional run | typed explanation | read-only evidence projection |
| `GetCapabilities` | none | capability document | reports implementation and authorization separately |

### 4.5 Service errors

Use one error vocabulary in Python and TypeScript:

| Code | HTTP | Retryable by default | Meaning |
|---|---:|---:|---|
| `invalid_request` | 400 | no | syntax/schema/semantic request failure |
| `unauthenticated` | 401 | no | no valid operator session |
| `permission_denied` | 403 | no | identity lacks authority |
| `not_found` | 404 | no | named durable subject absent or undisclosed |
| `conflict` | 409 | yes after refresh | CAS or terminal-state conflict |
| `incompatible_version` | 426 | no | unsupported wire version |
| `frame_too_large` | 413 | no | transport limit exceeded |
| `rate_limited` | 429 | yes | bounded gateway protection |
| `not_available` | 503 | yes/declared | dependency or capability unavailable |
| `internal` | 500 | maybe | redacted internal fault with correlation ID |

Never expose raw exception strings, filesystem roots, SQL, environment values, model keys, or
private artifact content. Preserve a correlation ID in logs and the redacted response.

### 4.6 Event stream contract

An SSE message transports the same `EventFrame` used on UDS:

```text
id: 42
event: vg.4
data: {"version":"vg.4","frameType":"event","frameId":"...","event":{...}}

```

SSE rules:

- `id` is the event's run-local sequence rendered as an IntString.
- `Last-Event-ID` and query `afterSeq` are equivalent; conflicting values are rejected.
- heartbeat comments are transport metadata and never ledger events.
- stream order is strictly increasing for one run.
- duplicates may occur across reconnect boundaries; clients deduplicate by stable event identity and
  reject same `(runId, seq)` with different digest.
- an idle stream sends a comment heartbeat, not a fabricated `Heartbeat` domain event.
- malformed stored envelopes fail the stream with a typed integrity error; they are not repaired.

### 4.7 Cursor race-free algorithm

The ledger is authoritative; in-memory queues are wake-up hints only.

```python
def tail(run_id: str, after_seq: int, stop: StopToken):
    authorize_read(run_id)
    cursor = after_seq
    while not stop.cancelled:
        rows = event_store.read_after(run_id=run_id, after_seq=cursor, limit=512)
        for envelope in rows:
            assert int(envelope.seq) > cursor
            yield envelope
            cursor = int(envelope.seq)
        if run_projection(run_id).terminal and not rows:
            return
        commit_notifier.wait(run_id=run_id, after_seq=cursor, timeout=heartbeat_interval)
```

The notifier is signalled only after successful append commit. A missed notification is harmless
because every wake or timeout re-queries the ledger. This removes the historical-read/live-subscribe
race without making a queue a second truth.

### 4.8 Projection envelope

Every REST read model returns provenance:

```json
{
  "api": "aether.run-view/1",
  "subjectId": "run-...",
  "reducerVersion": "run-view/1",
  "asOfSeq": "42",
  "sourceDigest": "sha256:...",
  "data": {}
}
```

Unknown event kinds are preserved by generic folds. A specialized projection may report
`partial: true` with understood/unknown kinds; it must not silently interpret an unknown event.

## 5. Runtime composition design

### 5.1 Required runtime service dependencies

Prefer explicit dependencies over handler-global construction:

```python
@dataclass(frozen=True)
class RuntimeServiceDependencies:
    inbox: CommandInboxPort
    events: EventStorePort
    blobs: BlobStorePort
    runner: RuntimeRunnerPort
    approvals: ApprovalAuthority
    clock: ClockPort
    ids: IdPort
    commit_notifier: CommitNotifier
    capabilities: CapabilityProvider
```

`RuntimeService` owns command normalization and lifecycle coordination. A runtime composition root
constructs concrete SQLite/blob adapters and injects them. The HTTP handler and UDS server receive
the already-composed service.

### 5.2 Runtime runner protocol

The runner must represent lifecycle, not merely a callback that returns `Any`:

```python
class RuntimeRunHandle(Protocol):
    run_id: str
    def cancel(self, reason: str) -> None: ...
    def join(self, timeout: float | None = None) -> RunOutcome | None: ...

class RuntimeRunnerPort(Protocol):
    def start(self, request: StartRunCommand) -> RuntimeRunHandle: ...
    def recover(self, run_id: str, checkpoint_id: str | None) -> RuntimeRunHandle: ...
```

The production implementation builds `TaskContext`, resolves the approved profile through runtime
bootstrap, and invokes `Runtime.execute_profiled()`. It must not construct a model adapter from an
unvalidated arbitrary endpoint supplied by the browser.

### 5.3 Event publication

Preferred order:

```text
Runtime operation
  -> LedgerEmitter builds canonical envelope
  -> EventStorePort.append(transaction)
  -> commit succeeds
  -> notifier emits run/seq hint
  -> UDS/SSE readers query committed envelope
```

`RuntimeService.publish_event()` must not remain a general bypass around `LedgerEmitter`. Service
commands that legally produce causal facts use the same canonical emitter/writer authority table as
other runtime producers.

## 6. Gateway and browser security profile

### 6.1 Local-first deployment

Initial release constraints:

- bind HTTP to `127.0.0.1` only;
- reject non-loopback bind unless an explicit authenticated deployment profile exists;
- UDS parent directory is private and socket mode is `0600`;
- validate UDS peer credentials where supported; socket permissions remain mandatory fallback;
- accept only configured `Origin` values;
- no wildcard CORS on command routes;
- set request-body, header, connection, stream, and page-size limits;
- workspace roots are server-configured capabilities, not arbitrary browser paths.

For Studio, prefer same-origin serving/proxy and an HttpOnly, `SameSite=Strict` session cookie. If
the client uses bearer authentication, use fetch-based SSE so authorization headers are available.
Do not place bearer tokens in SSE query strings.

### 6.2 CSRF and origin rules

Mutation routes require all of:

- authenticated operator session;
- allowed `Origin`/`Host`;
- CSRF token or same-origin double-submit mechanism;
- JSON content type;
- command idempotency key;
- command-specific authorization.

Loopback is not authentication: hostile websites can target localhost.

### 6.3 Workspace file access

Replace string-prefix containment checks with path semantics:

```python
root = configured_workspace.resolve(strict=True)
target = (root / requested_relative_path).resolve(strict=True)
if not target.is_relative_to(root):
    raise NotFound()
```

Additionally reject absolute paths, NULs, device files, non-files, and policy-disallowed content.
Prefer artifact reads over arbitrary workspace reads. Never expose this route remotely by default.

### 6.4 Secret and content redaction

- Provider keys are read only by model adapters from environment/configured secret sources.
- Request/response logging uses field allowlists, not recursive “best effort” redaction.
- Event payload schemas mark digest-only, sensitive, and artifact-reference fields.
- Large prompts, diffs, outputs, and source snapshots belong in authorized artifacts, not SSE.
- `trainability`, retention, confidentiality, owner, and redaction metadata survive every transport.
- Retention never grants capture authority.

## 7. Cryptographic approval protocol

### 7.1 Trust model

- operator client holds the private Ed25519 key;
- backend `ApprovalAuthority` holds registered public keys and status metadata;
- gateway transports a decision but cannot sign or approve;
- runtime verifies the decision against the durable challenge before appending resolution;
- effect execution re-enters the ordinary S1-S12 path.

Canonical signed body:

```json
{
  "approvalId": "...",
  "argsDigest": "sha256:...",
  "descriptorDigest": "sha256:...",
  "expiresAt": "2026-08-27T12:00:00.000Z",
  "keyId": "operator-key-id",
  "resolution": "approved",
  "reviewer": "operator:local"
}
```

Sign exact RFC 8785/JCS bytes. Base64 encoding, Unicode normalization, timestamp precision, field
names, and resolution vocabulary must have cross-language golden vectors.

### 7.2 Approval transaction

```text
1. Runtime persists ApprovalRequested(challenge, challengeDigest).
2. Client reads it from the ledger stream.
3. Client shows action, normalized diff, principal, expiry, and bound digests.
4. Signer signs canonical decision bytes.
5. Client submits ResolveApproval(decision, expectedSeq).
6. Runtime transaction checks pending state, CAS, expiry, key status, signature and digest binding.
7. Runtime appends exactly one ApprovalResolved or returns a typed rejection.
8. Suspended operation resumes through the normal policy/dispatch path.
```

Two concurrent decisions must produce one winner and one `conflict`; neither may create duplicate
resolution events.

### 7.3 Client signer implementations

`SignerPort` belongs in client-core. Supported adapters may include:

- Node/CLI signer using the existing Node crypto implementation;
- browser WebCrypto signer in a secure context with a non-exportable `CryptoKey` and explicit key
  registration;
- local companion/hardware signer where browser Ed25519 support or key policy requires it.

`localStorage`, checked-in seed bytes, unsigned compatibility decisions, and gateway-generated keys
are forbidden. If no approved signer is available, the UI is read-only for approval and reports
`signer_unavailable`.

## 8. Frontend integration standard

### 8.1 One client API

Studio and CLI import the public `@vanguard/client-core` API. `browser-entry.tsx` must not own direct
`fetch`, `EventSource`, approval payload, cursor, or reconnect logic. Those belong to an HTTP
transport implementing the same `RuntimeClient` used by the TUI.

```ts
interface RuntimeClient {
  startRun(request: StartRunRequest, signal?: AbortSignal): Promise<Result<RunRef>>;
  getRun(runId: string, signal?: AbortSignal): Promise<Result<RunSnapshot>>;
  listRuns(request: ListRunsRequest, signal?: AbortSignal): Promise<Result<RunPage>>;
  streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>>;
  requestCancel(runId: string, expectedSeq: string): Promise<Result<CommandReceipt>>;
  requestCheckpoint(runId: string, expectedSeq: string): Promise<Result<CheckpointRef>>;
  requestResume(request: ResumeRunRequest): Promise<Result<RunRef>>;
  resolveApproval(request: SignedApprovalRequest): Promise<Result<CommandReceipt>>;
  recordCorrection(request: CorrectionRequest): Promise<Result<CommandReceipt>>;
  explainArtifact(request: ExplainArtifactRequest): Promise<Result<ArtifactExplanation>>;
  getCapabilities(): Promise<Result<CapabilityDocument>>;
}
```

### 8.2 Client stream state machine

```text
idle -> connecting -> live -> reconnecting -> live
                       |            |
                       v            v
                     ended        failed
```

Client rules:

- persist the last validated cursor per run in session state;
- advance cursor only after schema validation and reducer acceptance;
- reject sequence regression and same-sequence/different-digest corruption;
- surface missing ranges to the UI; never paint a contiguous timeline over a gap;
- reconnect with bounded exponential backoff and jitter;
- reset attempt count after a stable live interval;
- abort fetch/UDS work when switching runs or unmounting;
- retain unknown events as opaque timeline entries.

### 8.3 Browser state

Studio state is divided into:

- durable truth: validated events and artifact references;
- deterministic projections: run view, causal graph, approval queue, capability view;
- ephemeral UI state: selected panel, filters, scroll position, open modal;
- transport state: connected/reconnecting/gap/error.

Never mix transport connection events into the causal fold. Demo fixtures must be selected by an
explicit demo adapter and can never appear in live mode.

## 9. Product API catalog — 45 routes

This is a target catalog, not blanket implementation authority. `Core` is required for the first
vertical integration. `Projection` is read-only and may ship when its reducer and authorization
exist. `M-7` and `M-8` routes remain disabled until the corresponding active work package exists.

Standard response types:

- command route: RuntimeService `ReceiptFrame` translated losslessly to HTTP;
- projection route: `ProjectionEnvelope<T>`;
- collection: cursor page with stable ordering;
- unsupported capability: `not_available` with capability state, never fake data.

### 9.1 Runs — 10

| # | Method | Route | Class | Canonical operation |
|---:|---|---|---|---|
| 1 | GET | `/api/v1/runs` | Core | `ListRuns` projection |
| 2 | POST | `/api/v1/runs` | Core | `StartRun` |
| 3 | GET | `/api/v1/runs/{runId}` | Core | `GetRun` projection |
| 4 | POST | `/api/v1/runs/{runId}:cancel` | Core | `Cancel` |
| 5 | POST | `/api/v1/runs/{runId}:checkpoint` | Core | `Checkpoint` |
| 6 | POST | `/api/v1/runs/{runId}:resume` | Core | `Resume` |
| 7 | GET | `/api/v1/runs/{runId}/events` | Core | historical event page |
| 8 | GET | `/api/v1/runs/{runId}/events:stream` | Core | SSE tail |
| 9 | GET | `/api/v1/runs/{runId}/lineage` | Projection | event-derived lineage |
| 10 | GET | `/api/v1/runs/{runId}/trajectory` | Projection | trajectory reader output |

### 9.2 Compositions — 7

| # | Method | Route | Class | Canonical operation |
|---:|---|---|---|---|
| 11 | GET | `/api/v1/compositions` | Projection | immutable composition registry page |
| 12 | POST | `/api/v1/compositions:validate` | Core/read-only | parse/canonicalize without activation |
| 13 | GET | `/api/v1/compositions/{digest}` | Projection | composition by digest |
| 14 | POST | `/api/v1/compositions/{digest}:plan-activation` | Core/read-only | activation plan preview |
| 15 | POST | `/api/v1/compositions/{digest}:activate` | Governed | ordinary runtime activation |
| 16 | GET | `/api/v1/compositions/{digest}/artifacts` | Projection | frozen artifact references |
| 17 | GET | `/api/v1/compositions/{digest}/diff/{otherDigest}` | Projection | immutable structural diff |

Compositions are immutable and digest-addressed. Do not expose generic PUT/DELETE CRUD. Future M-8
promotion changes an authorized registry pointer by CAS; it does not mutate a composition.

### 9.3 Agents — 6

| # | Method | Route | Class | Canonical operation |
|---:|---|---|---|---|
| 18 | GET | `/api/v1/agents` | Projection | AgentView identities/page |
| 19 | GET | `/api/v1/agents/{lineageId}` | Projection | event-derived AgentView |
| 20 | GET | `/api/v1/agents/{lineageId}/events` | Projection | lineage-filtered events |
| 21 | GET | `/api/v1/agents/{lineageId}/children` | Projection | durable child lineages |
| 22 | GET | `/api/v1/agents/{lineageId}/context` | Projection | authorized context evidence |
| 23 | GET | `/api/v1/agents/{lineageId}/budget` | Projection | event-derived budget view |

There is no mutable Agent CRUD API. An agent is a projection, not a persistent privileged object.

### 9.4 Artifacts — 7

| # | Method | Route | Class | Canonical operation |
|---:|---|---|---|---|
| 24 | GET | `/api/v1/artifacts` | Projection | authorized metadata page |
| 25 | POST | `/api/v1/artifacts:query` | Projection | typed resource selector query |
| 26 | GET | `/api/v1/artifacts/{digest}` | Projection | metadata and policy state |
| 27 | GET | `/api/v1/artifacts/{digest}/content` | Governed read | authorized blob range read |
| 28 | GET | `/api/v1/artifacts/{digest}/lineage` | Projection | provenance graph |
| 29 | GET | `/api/v1/artifacts/{digest}/explanation` | Projection | `ExplainArtifact` |
| 30 | GET | `/api/v1/artifacts/{digest}/diff/{otherDigest}` | Projection | bounded artifact diff |

### 9.5 Topologies — 5

| # | Method | Route | Class | Canonical operation |
|---:|---|---|---|---|
| 31 | GET | `/api/v1/topologies` | M-7 projection | declared topology page |
| 32 | POST | `/api/v1/topologies:validate` | M-7 read-only | parse and reject authority |
| 33 | POST | `/api/v1/topologies:lower` | M-7 read-only | sequential lowering preview |
| 34 | GET | `/api/v1/topologies/{digest}` | M-7 projection | immutable declaration |
| 35 | GET | `/api/v1/topologies/{digest}/realization/{runId}` | M-7 projection | declared/lowered/realized diff |

No topology mutation API is exposed before the immutable registry contract and M-7 runtime
integration exist. Topology execution occurs only as a digest-pinned run-plan extension through the
sole runtime.

### 9.6 Skills and memory — 5

| # | Method | Route | Class | Canonical operation |
|---:|---|---|---|---|
| 36 | GET | `/api/v1/skills` | M-8 projection | authorized skill index |
| 37 | GET | `/api/v1/skills/{digest}` | M-8 projection | immutable skill card |
| 38 | GET | `/api/v1/memory/records` | M-8 projection | authorized category query |
| 39 | GET | `/api/v1/memory/records/{digest}` | M-8 governed read | authorized record dereference |
| 40 | POST | `/api/v1/memory:retrieve` | M-8 governed read | authorization-before-ranking retrieval |

Candidate generation, evaluation, promotion, rollback, retention, and legal hold should not be
collapsed into casual REST CRUD. Add mutation routes only when ADR-0100 contracts and active M-8
work specify their commands, authorities, and evidence.

### 9.7 Governance and service — 5

| # | Method | Route | Class | Canonical operation |
|---:|---|---|---|---|
| 41 | GET | `/api/v1/health` | Core | liveness only, no internal details |
| 42 | GET | `/api/v1/capabilities` | Core | implementation/authorization matrix |
| 43 | GET | `/api/v1/approvals` | Core projection | pending approval page |
| 44 | GET | `/api/v1/approvals/{approvalId}` | Core projection | durable challenge/status |
| 45 | POST | `/api/v1/approvals/{approvalId}:resolve` | Core governed command | `ResolveApproval` |

Temporary aliases (`/api/health`, `/api/runs/launch`, `/api/events/stream`,
`/api/approvals/resolve`) may exist for one compatibility window. They must call canonical handlers,
emit deprecation headers, have contract tests, and carry a removal version. They must not preserve
synthetic behavior.

## 10. Capability discovery

Capability discovery reports two independent dimensions:

```json
{
  "api": "aether.capabilities/1",
  "serverVersion": "0.7.3.dev0",
  "wireVersions": ["vg.4"],
  "capabilities": {
    "run.stream": {
      "implementation": "available",
      "authorization": "enabled",
      "contract": "runtime-service/vg.4"
    },
    "topology.execute": {
      "implementation": "partial",
      "authorization": "disabled",
      "reasonCode": "milestone_gate_open",
      "requires": ["M-7 accepted work package"]
    },
    "memory.retrieve": {
      "implementation": "prototype",
      "authorization": "disabled",
      "reasonCode": "m8_not_authorized"
    }
  }
}
```

Allowed implementation states: `absent`, `prototype`, `partial`, `available`, `degraded`.
Allowed authorization states: `disabled`, `read_only`, `enabled`. Frontends derive disabled actions
from this document but the backend enforces them independently.

## 11. Delivery roadmap

Each phase is a vertical, independently reviewable work package. Do not combine backend milestone
work, frontend integration, generated schemas, and unrelated leadership changes in one PR.

### F0 — Contract and falsifier freeze

Modify:

- `schemas/v4/runtime-service.schema.json`
- command-specific schemas or `$defs` under existing `schemas/v4/`
- `vanguard/clients/client-core/src/contract/*`
- generated Python/TypeScript readers through the existing codegen path

Deliver:

- discriminated frame union;
- closed first-release command union;
- command payload/result schemas;
- service error schema;
- approval JCS golden vectors;
- schema-version compatibility matrix;
- negative vectors for unknown field/name/version and malformed envelope.

Exit gate: Python and TypeScript accept/reject the same corpus byte-for-byte. No production handler
changes before this contract review is accepted.

### F1 — RuntimeService over canonical ledger

Modify:

- `runtime/service/service.py`
- `runtime/service/inbox.py`
- `runtime/root.py` or a dedicated runtime service composition module
- `runtime/ledger_emitter.py`
- `ports/event_store.py` only if a required read-after-cursor operation is missing
- SQLite adapter implementation as required by that port

Deliver:

- explicit service dependencies;
- runtime runner/handle;
- command inbox separated from causal events;
- all service events written through canonical ledger authority;
- event-derived run snapshots;
- clean recovery of commands accepted before process death;
- legacy service DB compatibility test.

Exit gate: one fake-model run started through `RuntimeService` produces a valid file-backed WAL and
fresh-process fold identical to direct canonical runtime execution.

### F2 — UDS daemon and protocol parity

Modify:

- `runtime/service/server.py`
- add an explicit daemon `main()` and project script only if authorized;
- `client-core/src/adapters/transport.ts`
- daemon parsers and tests.

Deliver:

- bounded frame parser;
- peer/socket security;
- typed errors and reply correlation;
- cancellation-aware stream;
- reconnect cursor parity;
- graceful shutdown and stale-socket handling;
- daemon lifecycle command or documented foreground process.

Exit gate: qualified Linux AF_UNIX tests prove start/get/stream/cancel/checkpoint/resume/approval,
disconnect/reconnect, duplicate command, malformed frame, oversized frame, and shutdown cleanup.

### F3 — HTTP gateway core

Modify:

- `runtime/service/studio_gateway.py`
- runtime service composition module
- `client-core/src/adapters/http.ts`
- Studio proxy script only for same-origin development wiring.

Deliver:

- remove `_pilot_run_simulation` and gateway sequence counter;
- core `/api/v1` routes 1-8 and 41-45;
- same service and contracts as UDS;
- secure local profile, limits, origin/CSRF checks;
- race-free historical/SSE cursor;
- compatibility aliases with deprecation policy.

Exit gate: UDS and HTTP command receipts normalize identically, and both stream the same persisted
event IDs, sequences, and digests.

### F4 — Client-core convergence

Modify:

- `client-core/src/contract/*`
- `client-core/src/adapters/http.ts`
- `client-core/src/adapters/transport.ts`
- `client-core/src/application/*` where projection contracts require it.

Deliver:

- one `RuntimeClient` API;
- transport-neutral error preservation;
- stream state machine and gap detection;
- capability negotiation;
- signed approval request type;
- contract fixtures shared by socket and HTTP adapters.

Exit gate: identical client-core behavioral suite runs against fake HTTP and UDS servers, including
abort, retry, stale CAS, gap, unknown event, and incompatible version.

### F5 — CLI/TUI live vertical slice

Modify:

- CLI composition/transport wiring;
- TUI hooks and approval flow;
- no domain or authority duplication.

Deliver:

- select/start/attach run;
- live timeline with visible gap state;
- checkpoint/cancel/resume;
- signed approval;
- artifact explanation;
- capability-aware commands.

Exit gate: a hermetic fake-model scenario and a separately selected live-provider smoke complete
through the same UI path; only the live attributable run may support promotion evidence.

### F6 — Studio live vertical slice

Modify:

- `studio/src/browser-entry.tsx`
- `studio/src/runtime/StudioRuntime.tsx`
- Studio session/store integration;
- browser signer adapter if separately authorized.

Deliver:

- remove direct API calls from browser entry;
- inject `RuntimeClient`;
- explicit demo/live adapters;
- run selection and cursor persistence;
- live observatory and forensic inspector over validated events;
- secure approval or explicit signer-unavailable mode;
- capability-aware disabled panels.

Exit gate: browser refresh/reconnect preserves truth, no demo event enters live store, and Studio and
TUI show equivalent run terminal/approval/artifact projections.

### F7 — Projection APIs

Add routes 9-30 only as their reducers and artifact authorization are verified. Benchmark cold fold,
incremental fold, cursor page, and artifact range reads. Every projection must prove rebuild parity.

### F8 — M-7/M-8 frontend activation

This phase is staged, not currently authorized. After the corresponding milestone work is active:

- enable topology routes 31-35 only after topology is bound into the sole runtime;
- enable skill/memory routes 36-40 only after verified durable authorization and provenance exist;
- keep unavailable actions visible with reasons when useful, but fail closed server-side;
- never use frontend presence as milestone evidence.

## 12. Failure modes and required behavior

| Failure | Required behavior | Prohibited behavior |
|---|---|---|
| malformed frame | typed rejection, no inbox/ledger append | best-effort coercion |
| duplicate idempotency key | return original logical receipt | execute twice |
| reused key with different digest | conflict and audit signal | return unrelated receipt |
| stale `expectedSeq` | conflict with current safe cursor | last-write-wins |
| WAL busy | bounded retry then `not_available` | drop event |
| append failure | operation fails/undeterminable per law | stream uncommitted event |
| notifier loss | ledger poll catches up | declare gap from queue state |
| SSE disconnect | reconnect after last validated seq | restart at zero silently |
| sequence collision/digest mismatch | integrity failure, stop fold | overwrite prior event |
| process crash after command accept | recover inbox and reconcile | blind re-execute |
| approval expires | reject closed | extend expiry in gateway |
| invalid/revoked signing key | permission denied | unsigned fallback |
| unavailable profile/sandbox | fail closed | host fallback |
| missing artifact authority | not found/denied without leakage | digest implies read access |
| M-7/M-8 gate open | structured disabled capability | placeholder success |
| unknown event | preserve opaque fact, projection partial | discard or invent semantics |

## 13. Verification strategy

### 13.1 Test pyramid

1. Schema vectors: Python/TypeScript parity and JCS signatures.
2. Pure service tests: handlers with fake ports and deterministic clock/IDs.
3. Adapter contract tests: SQLite WAL, UDS framing, HTTP/SSE framing.
4. Integration tests: composed service plus fake model and file-backed stores.
5. Fresh-process tests: crash, restart, cold fold, resume, cursor replay.
6. UI contract tests: client-core fake/scenario adapters.
7. Qualified E2E: Linux AF_UNIX, browser, real profile selected explicitly.
8. External clean-room gate: new checkout/process, keys unset for hermetic suite.

### 13.2 Mandatory falsifiers

- HTTP and UDS produce different canonical command results.
- gateway emits an event absent from WAL.
- an event is visible before its append transaction commits.
- reconnect loses or mutates an event.
- same seq with different content is accepted.
- a second approval decision is appended.
- expired/tampered/revoked approval reaches effect execution.
- browser can resolve approval without a signer.
- arbitrary path escapes configured workspace.
- secret marker reaches logs, event stream, projection, or artifact metadata.
- disabled M-7/M-8 capability returns success.
- fresh-process projection differs from live projection.
- integration changes Kernel imports or exceeds TCB budget.

### 13.3 Performance budgets to establish before release

Measure and record, rather than inventing pass thresholds:

- command p50/p95/p99 latency excluding model execution;
- event append-to-SSE visibility latency;
- reconnect catch-up at 1k/10k/100k events;
- projection cold fold and incremental fold;
- memory usage for Studio event ingestion and TUI long sessions;
- maximum sustainable SSE clients for the local profile;
- SQLite busy rate and checkpoint behavior;
- artifact metadata and authorized range-read latency.

The release work package must freeze explicit budgets after baseline measurement and before tuning.

## 14. Commands and smoke-test runbook

These commands exist today unless marked “after implementation.” Run from repository root.

### 14.1 Baseline gates

```bash
python3 -m unittest discover -s test -t .
python3 tools/linters/check_boundaries.py
python3 tools/linters/check_tcb_budget.py
python3 tools/linters/scan_secrets.py
python3 tools/linters/check_domain_blindness.py
python3 tools/linters/check_isolation_policy.py
python3 tools/linters/check_falsifier_ids.py
python3 tools/linters/check_markdown_links.py
python3 tools/linters/check_stale_paths.py
npm run typecheck
npm test
```

Frontend workspace gates:

```bash
npm --workspace @vanguard/client-core run typecheck
npm --workspace @vanguard/client-core test
npm --workspace @vanguard/cli run typecheck
npm --workspace @vanguard/cli test
npm --workspace @vanguard/studio run typecheck
npm --workspace @vanguard/studio test
```

### 14.2 Existing stdio bridge

```bash
printf '%s\n' '{"command":"doctor","profile":"product","runId":"doctor-smoke"}' \
  | python3 -m vanguard.packages.runtime.entrypoint --stdin-json
```

Hermetic coding preview:

```bash
printf '%s\n' \
  '{"command":"code","workspace":".","brief":"deterministic bridge smoke","fakeBackend":"deterministic","runId":"stdio-smoke"}' \
  | python3 -m vanguard.packages.runtime.entrypoint --stdin-json
```

Assert one JSON result per input line and no logs on stdout.

### 14.3 Focused existing transport tests

```bash
python3 -m unittest test.runtime.test_runtime_service -v
python3 -m unittest test.integration.test_stream_reconnect -v
python3 -m unittest test.governance.test_ed25519_approvals -v
python3 -m unittest test.runtime.test_approval_flow -v
python3 -m unittest test.runtime.test_coding_entrypoint -v
```

### 14.4 After daemon entrypoint implementation

The implementation must add and document a real foreground daemon command before using it here.
Target shape:

```bash
vg-runtime-daemon \
  --socket /tmp/vanguard-runtime-integration.sock \
  --database /tmp/vanguard-runtime-integration.sqlite3 \
  --workspace "$PWD" \
  --profile local
```

Then exercise CLI/TUI using the explicit socket:

```bash
VANGUARD_RUNTIME_SOCKET=/tmp/vanguard-runtime-integration.sock npm run vg -- doctor
VANGUARD_RUNTIME_SOCKET=/tmp/vanguard-runtime-integration.sock npm run vg -- run
```

Exact subcommands must be verified against the implemented CLI help before freezing the runbook.

### 14.5 After secure gateway implementation

```bash
python3 -m vanguard.packages.runtime.service.studio_gateway \
  --host 127.0.0.1 \
  --port 8000 \
  --workspace "$PWD"
```

With the issued local session/CSRF mechanism:

```bash
curl --fail http://127.0.0.1:8000/api/v1/health
curl --fail http://127.0.0.1:8000/api/v1/capabilities
curl --fail http://127.0.0.1:8000/api/v1/runs
```

Launch and stream only using the documented authentication headers/cookies; do not weaken the
gateway for curl convenience.

Studio development server:

```bash
npm --workspace @vanguard/studio run dev
```

Verify run selection, reconnect, gap display, approval, terminal state, and browser refresh.

### 14.6 Replay parity procedure

For each accepted E2E fixture:

1. execute through RuntimeService with a file-backed WAL;
2. capture event IDs, sequences, envelope digests, terminal projection, and artifact digests;
3. terminate every Python process;
4. start a fresh process and cold-fold the WAL;
5. compare live and cold projections;
6. reconnect UDS and HTTP clients from intermediate cursors;
7. verify identical suffixes and no same-seq divergence;
8. record environment/profile identity separately from causal truth.

## 15. Definition of done

The frontend/backend integration is complete for the core release only when all of the following are
true:

- Studio and CLI/TUI use `@vanguard/client-core` rather than independent command semantics.
- all command transports reach the same `RuntimeService` and canonical runtime bootstrap.
- synthetic pilot events and gateway-local sequence allocation are gone.
- exactly one canonical event ledger feeds UDS, HTTP, SSE, replay, and projections.
- command schemas, event schemas, error schemas, and approval signatures have cross-language vectors.
- cursor reconnect is race-safe, gap-aware, bounded, and fresh-process tested.
- signed approval is descriptor-bound, expiry-bound, CAS-protected, and fail-closed.
- workspace, origin, CSRF, authentication, size limits, and secret-redaction gates pass.
- direct runtime, UDS, and HTTP produce equivalent durable truth.
- Stdio remains fast, hermetic when selected, and structurally separate from daemon framing.
- unavailable M-7/M-8 capabilities are truthful and cannot be activated from the UI.
- boundaries, TCB budget, secret scan, Python tests, TypeScript tests, and qualified Linux UDS tests
  are green.
- a clean-room reviewer can follow this runbook without undocumented setup or private knowledge.

## 16. First implementation package recommendation

When leadership authorizes frontend integration, start with one bounded package containing F0 and
the smallest part of F1:

1. freeze RuntimeService frame/command/error schemas and golden vectors;
2. reconcile `ListRuns` and `ResolveApproval` contract drift;
3. add event-store cursor reads behind a port if needed;
4. inject the canonical event store into `RuntimeService`;
5. derive `GetRun`/`ListRuns` from committed events;
6. prove direct-runtime versus service-run WAL parity with a fake model;
7. leave HTTP route expansion and M-7/M-8 APIs out of that PR.

That package removes the highest-risk ambiguity—two event histories—before adding another
transport. F2 through F6 then become transport and presentation work over a stable substrate rather
than simultaneous redesign of runtime truth.
