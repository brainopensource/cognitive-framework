 # AETHER / Vanguard frontend integration plan

  The integration should converge on one rule:

  > The Python runtime remains the authority. Stdio, UDS, and HTTP/SSE are transport adapters over the same command, projection, and event-ledger
  > contracts.

  The current implementation is not yet safe to expose directly. In particular:

  - studio_gateway.py still emits synthetic events through _pilot_run_simulation.
  - RuntimeService uses ServiceInboxStore, while Runtime.execute_profiled() normally uses SqliteEventStore; these are currently separate ledgers.
  - Gateway SSE emits incomplete envelopes such as evt-*, which do not satisfy the TypeScript parser’s UUID and required-field checks.
  - The HTTP client currently implements only launch, health, list-runs, approval resolution, and a partial SSE path.
  - ResolveApproval has incompatible payload shapes: TypeScript sends { approvalId, decision }, while RuntimeService._cmd_ResolveApproval() expects
    a signed decision object nested under payload.decision.

  - M-7 is only partially integrated and M-8 is explicitly not started; their endpoints must advertise capability state rather than pretending to
    be complete.

  Relevant implementation seams:

  - vanguard/packages/runtime/service/studio_gateway.py
  - vanguard/packages/runtime/service/server.py
  - vanguard/packages/runtime/service/service.py
  - vanguard/packages/runtime/service/inbox.py
  - vanguard/packages/runtime/root.py
  - vanguard/packages/runtime/entrypoint.py
  - vanguard/clients/client-core/src/adapters/transport.ts
  - vanguard/clients/client-core/src/adapters/http.ts
  - schemas/v4/runtime-service.schema.json

  ## 1. Target architecture and transport matrix

                           Browser Studio
                                │
                   HTTP JSON commands + SSE events
                                │
                      studio_gateway.py
                                │
                ┌───────────────┴────────────────┐
                │                                │
         RuntimeService facade              Projection/query layer
                │                                │
                └───────────────┬────────────────┘
                                │
                      Runtime composition root
                                │
            Runtime.execute_profiled / Runtime.run_composed
                                │
                   adapters, sandbox, model, evaluator
                                │
                      Single SQLite-WAL ledger
                                │
                   EventEnvelope vg.4 / mhf.event/2
                                │
        ┌───────────────────────┼──────────────────────┐
        │                       │                      │
     UDS daemon              SSE cursor              Replay
   server.py              /api/events/stream       fresh-process fold
        │
   NDJSON vg.4 frames
        │
  @vanguard/client-core
        │
   Ink TUI / vg CLI

   Surface                Transport                  Write operations                       Read operations                       Streaming
  ━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━
   vg code, vg doctor     subprocess stdin/stdout    Coding request only                    Structured projection                 One JSON
                                                                                                                                  response per
                                                                                                                                  input
  ─────────────────────  ─────────────────────────  ─────────────────────────────────────  ────────────────────────────────────  ──────────────────
   CLI/TUI                UDS NDJSON                 Start, cancel, approval,               Run snapshot, artifact explanation    StreamEvents
                                                     checkpoint, resume, correction                                               with afterSeq
  ─────────────────────  ─────────────────────────  ─────────────────────────────────────  ────────────────────────────────────  ──────────────────
   Studio browser         HTTP JSON                  Same commands through gateway          REST projections                      SSE backed by
                                                                                                                                  SQLite WAL
  ─────────────────────  ─────────────────────────  ─────────────────────────────────────  ────────────────────────────────────  ──────────────────
   Replay/test harness    Files or SQLite            None                                   Event replay                          Deterministic
                                                                                                                                  cursor iteration

  The gateway must not become a second runtime. It should:

  1. authenticate and validate transport requests;
  2. translate HTTP/JSON to RuntimeService commands;
  3. query durable projections;
  4. stream already-persisted events;
  5. never authorize effects, mutate ledger history directly, or duplicate reducers.

  ## 2. Phased execution roadmap

  ### Phase 0 — Contract freeze and gap inventory

  Files:

  - schemas/v4/runtime-service.schema.json
  - schemas/v4/event-envelope.schema.json
  - vanguard/clients/client-core/src/contract/types.ts
  - vanguard/clients/client-core/src/contract/parse.ts
  - vanguard/clients/client-core/src/adapters/http.ts
  - vanguard/clients/client-core/src/adapters/transport.ts

  Actions:

  - Freeze one canonical command frame:

  {
    "version": "vg.4",
    "frameType": "command",
    "frameId": "uuid",
    "command": {
      "name": "StartRun",
      "commandId": "uuid",
      "idempotencyKey": "uuid",
      "runId": "run-id",
      "actor": "operator",
      "payload": {}
    }
  }

  - Freeze one canonical event frame:

  {
    "version": "vg.4",
    "frameType": "event",
    "frameId": "uuid",
    "event": {
      "schemaVersion": "vg.4",
      "eventId": "uuid",
      "scope": "episode",
      "runId": "run-id",
      "episodeId": "episode-id",
      "traceId": "uuid",
      "spanId": "uuid",
      "seq": "42",
      "occurredAt": "timestamp",
      "recordedAt": "timestamp",
      "principal": "runtime",
      "tenantId": "local",
      "ownerId": "owner",
      "confidentiality": "internal",
      "retentionClass": "standard",
      "trainability": "prohibited",
      "redactionStatus": "none",
      "payload": { "kind": "..." }
    }
  }

  - Resolve the schema discrepancy where runtime-service.schema.json describes event as an envelope while the client expects an event wrapper.
  - Add generated or shared validation tests for Python and TypeScript.
  - Define CapabilityStatus:

  {
    "available": false,
    "state": "degraded",
    "reason": "M-8 not started",
    "requires": ["M-7 acceptance"]
  }

  No kernel changes are required.

  ### Phase 1 — Unify the ledger and runtime execution path

  Files to modify:

  - vanguard/packages/runtime/service/service.py
  - vanguard/packages/runtime/service/inbox.py
  - vanguard/packages/runtime/root.py
  - vanguard/packages/runtime/ledger_emitter.py
  - vanguard/packages/adapters/stores/event_store.py

  New runtime-layer files:

  - vanguard/packages/runtime/service/runner.py
  - vanguard/packages/runtime/service/projections.py
  - vanguard/packages/runtime/service/capabilities.py

  Actions:

  1. Make the service receive an explicit durable SqliteEventStore.
  2. Retain command idempotency in ServiceInboxStore, but make the event ledger the SqliteEventStore.
  3. Inject a runtime runner into RuntimeService:

  class RuntimeRunner(Protocol):
      def start(self, request: StartRunRequest, emit: Callable[[EventEnvelope], None]) -> None: ...

  4. Implement the runner by calling Runtime.execute_profiled().
  5. Emit only canonical EventEnvelope values through the existing ledger emitter path.
  6. Remove _pilot_run_simulation.
  7. Ensure run completion, failure, cancellation, and approval suspension update the same durable run projection.
  8. Publish events to subscribers only after successful WAL commit.

  The runner must not import into kernel. All new integration logic belongs under runtime/service/.

  Recommended startup composition:

  store = SqliteEventStore(runtime_db)
  inbox = ServiceInboxStore(service_db)
  service = RuntimeService(
      inbox_store=inbox,
      event_store=store,
      harness_runner=runtime_runner,
  )

  If retaining one database is preferable, place command inbox and event tables in the same SQLite file while preserving separate responsibilities.

  ### Phase 2 — Durable cursor-resumable streaming

  Files:

  - vanguard/packages/runtime/service/service.py
  - vanguard/packages/runtime/service/studio_gateway.py
  - vanguard/packages/adapters/stores/event_store.py
  - vanguard/clients/client-core/src/adapters/http.ts
  - vanguard/clients/studio/src/browser-entry.tsx

  Implement:

  GET /api/events/stream?runId=<id>&afterSeq=<n>

  Requirements:

  - Read historical events from SQLite where seq > afterSeq.
  - Subscribe to the live queue only after the historical boundary is established.
  - Re-check the WAL after subscription to close the historical/live race.
  - Emit id: <seq> in SSE in addition to data:.
  - Support Last-Event-ID as an alternative cursor.
  - Deduplicate by (runId, seq).
  - Return a typed gap response if the cursor is invalid or compacted.
  - Never use a gateway-local sequence counter.
  - Never emit connection/demo events as EventEnvelopes.

  SSE format:

  id: 42
  event: vg.4
  data: {"version":"vg.4","frameType":"event","frameId":"...","event":{...}}


  The browser currently connects without a run cursor. Change it to select a run and reconnect with the last accepted sequence.

  ### Phase 3 — UDS protocol alignment

  Files:

  - vanguard/packages/runtime/service/server.py
  - vanguard/packages/runtime/service/service.py
  - vanguard/clients/client-core/src/adapters/transport.ts
  - vanguard/clients/client-core/src/contract/parse.ts
  - schemas/v4/runtime-service.schema.json

  Commands:

   Command             Required payload                                                  Result
  ━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   StartRun            repo, brief/prompt, manifest, profile, model, resume reference    run and episode IDs
  ──────────────────  ────────────────────────────────────────────────────────────────  ──────────────────────────────────────────
   GetRun              none                                                              durable run snapshot and latest sequence
  ──────────────────  ────────────────────────────────────────────────────────────────  ──────────────────────────────────────────
   StreamEvents        afterSeq                                                          event frames until disconnect/terminal
  ──────────────────  ────────────────────────────────────────────────────────────────  ──────────────────────────────────────────
   ResolveApproval     signed ApprovalDecision                                           accepted/rejected receipt
  ──────────────────  ────────────────────────────────────────────────────────────────  ──────────────────────────────────────────
   Checkpoint          optional expected sequence                                        checkpoint ID and digest
  ──────────────────  ────────────────────────────────────────────────────────────────  ──────────────────────────────────────────
   Resume              checkpoint ID or run ID                                           resumed run reference
  ──────────────────  ────────────────────────────────────────────────────────────────  ──────────────────────────────────────────
   Cancel              cancellation reason                                               cancellation receipt
  ──────────────────  ────────────────────────────────────────────────────────────────  ──────────────────────────────────────────
   RecordCorrection    schema-valid correction                                           appended event receipt
  ──────────────────  ────────────────────────────────────────────────────────────────  ──────────────────────────────────────────
   ExplainArtifact     artifact ID                                                       evidence-backed explanation

  Changes:

  - Validate every incoming frame against runtime-service.schema.json.
  - Return the request frameId or command correlation ID in all receipts/errors.
  - Preserve commandId and idempotencyKey.
  - Reject missing runId where required.
  - Reject unknown fields where the schema says additionalProperties: false.
  - Use typed error codes: invalid_request, not_found, conflict, permission_denied, not_available, incompatible_version.
  - Make StreamEvents cancellation-aware rather than blocking forever on q.get().
  - Do not stringify arbitrary Python exceptions into externally visible details; log them internally and return a redacted detail.

  The client must also stop converting every daemon error into invalid_request; preserve the server error code.

  ### Phase 4 — HTTP/SSE gateway

  Files:

  - vanguard/packages/runtime/service/studio_gateway.py
  - vanguard/packages/runtime/service/projections.py
  - vanguard/packages/runtime/service/capabilities.py
  - vanguard/clients/client-core/src/adapters/http.ts
  - vanguard/clients/studio/scripts/serve-browser.mjs

  Implement the REST matrix below. Every route should call a service command or a read-only projection. No route should access _active_runs as its
  authoritative state.

  HTTP response envelope:

  {
    "ok": true,
    "data": {},
    "cursor": "42",
    "capabilities": {}
  }

  Errors:

  {
    "ok": false,
    "error": {
      "code": "conflict",
      "message": "expected sequence 42, current sequence 44",
      "retryable": true
    }
  }

  ### Phase 5 — Governance and approval wire

  Files:

  - vanguard/packages/runtime/governance/approvals.py
  - vanguard/packages/runtime/service/service.py
  - vanguard/packages/runtime/service/studio_gateway.py
  - vanguard/clients/client-core/src/adapters/signer.ts
  - vanguard/clients/studio/src/runtime/StudioRuntime.tsx
  - vanguard/clients/studio/src/ui/ApprovalInterceptor.tsx

  Protocol:

  1. Runtime emits ApprovalRequested with challenge fields.
  2. Client displays the challenge.
  3. OperatorSigner signs the canonical JCS payload.
  4. Client submits the complete ApprovalDecision.
  5. Runtime verifies:
      - approval exists;
      - approval is still pending;
      - approval ID matches;
      - argsDigest matches;
      - descriptorDigest matches;
      - expiration has not passed;
      - resolution is valid;
      - key ID is registered;
      - Ed25519 signature is valid;
      - expected ledger sequence/digest has not changed.

  6. Runtime appends ApprovalResolved.
  7. The suspended run resumes through the normal runtime path.

  The browser must not generate or invent a signature. If the browser lacks a configured signer, the UI must show “operator signer unavailable” and
  fail closed.

  The current /api/approvals/resolve implementation must stop broadcasting synthetic ApprovalResolved, EffectCompleted, and EpisodeCompleted
  events. Those events must originate only from the runtime execution path.

  ### Phase 6 — Degraded M-6/M-7/M-8 behavior

  Files:

  - vanguard/packages/runtime/service/capabilities.py
  - vanguard/packages/runtime/topology.py
  - vanguard/packages/runtime/memory.py
  - vanguard/packages/runtime/service/studio_gateway.py

  Rules:

  - M-6 unavailable: reject recursive child-run requests with not_available; do not silently flatten recursion.
  - M-7 partially available: expose parse/validate/lower capability separately from execute capability.
  - M-8 unavailable: expose memory inspection as not_available or read-only prototype status; never persist unauthorized memory mutations.
  - UI receives capability metadata at /api/capabilities.
  - Commands requiring unavailable features return structured errors, not HTTP 500.
  - No endpoint may imply acceptance merely because a parser or prototype exists.

  This respects the active sprint status: M-7 is partial and M-8 is not started.

  ## 3. REST endpoint implementation checklist

  The following is a proposed canonical 45-endpoint matrix for the Studio and future HTTP client. It should be frozen in an existing canonical
  contract location before implementation.

  ### Runs — 8

   Method    Route                           Backend operation
  ━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GET       /api/runs                       List durable run projections
  ────────  ──────────────────────────────  ───────────────────────────────
   POST      /api/runs                       Create/start run
  ────────  ──────────────────────────────  ───────────────────────────────
   POST      /api/runs/launch                Compatibility alias for start
  ────────  ──────────────────────────────  ───────────────────────────────
   GET       /api/runs/{runId}               GetRun projection
  ────────  ──────────────────────────────  ───────────────────────────────
   POST      /api/runs/{runId}/cancel        Cancel command
  ────────  ──────────────────────────────  ───────────────────────────────
   POST      /api/runs/{runId}/checkpoint    Checkpoint command
  ────────  ──────────────────────────────  ───────────────────────────────
   POST      /api/runs/{runId}/resume        Resume command
  ────────  ──────────────────────────────  ───────────────────────────────
   GET       /api/runs/{runId}/events        Historical cursor query

  SSE:

  GET /api/runs/{runId}/events/stream?afterSeq=n

  ### Compositions — 7

   Method    Route                              Backend operation
  ━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GET       /api/compositions                  List registered compositions
  ────────  ─────────────────────────────────  ────────────────────────────────────────────────────
   POST      /api/compositions                  Validate/store declaration
  ────────  ─────────────────────────────────  ────────────────────────────────────────────────────
   GET       /api/compositions/{id}             Read canonical composition
  ────────  ─────────────────────────────────  ────────────────────────────────────────────────────
   PUT       /api/compositions/{id}             CAS update declaration
  ────────  ─────────────────────────────────  ────────────────────────────────────────────────────
   DELETE    /api/compositions/{id}             Tombstone/deactivate, never physical-delete ledger
  ────────  ─────────────────────────────────  ────────────────────────────────────────────────────
   POST      /api/compositions/{id}/validate    Parse and validate
  ────────  ─────────────────────────────────  ────────────────────────────────────────────────────
   POST      /api/compositions/{id}/activate    Runtime activation plan

  ### Agents — 7

   Method    Route                        Backend operation
  ━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GET       /api/agents                  Agent catalog projection
  ────────  ───────────────────────────  ─────────────────────────────────────────────
   POST      /api/agents                  Create agent declaration
  ────────  ───────────────────────────  ─────────────────────────────────────────────
   GET       /api/agents/{id}             Agent detail
  ────────  ───────────────────────────  ─────────────────────────────────────────────
   PUT       /api/agents/{id}             CAS update
  ────────  ───────────────────────────  ─────────────────────────────────────────────
   DELETE    /api/agents/{id}             Deactivate declaration
  ────────  ───────────────────────────  ─────────────────────────────────────────────
   POST      /api/agents/{id}/validate    Manifest/profile validation
  ────────  ───────────────────────────  ─────────────────────────────────────────────
   GET       /api/agents/{id}/lineage     Durable provenance/child lineage projection

  ### Artifacts — 7

   Method    Route                                      Backend operation
  ━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GET       /api/artifacts                             Artifact index with cursor
  ────────  ─────────────────────────────────────────  ────────────────────────────────────
   POST      /api/artifacts/query                       Selector-based read projection
  ────────  ─────────────────────────────────────────  ────────────────────────────────────
   GET       /api/artifacts/{artifactId}                Artifact metadata
  ────────  ─────────────────────────────────────────  ────────────────────────────────────
   GET       /api/artifacts/{artifactId}/content        Blob/CAS retrieval, policy checked
  ────────  ─────────────────────────────────────────  ────────────────────────────────────
   GET       /api/artifacts/{artifactId}/lineage        Provenance graph
  ────────  ─────────────────────────────────────────  ────────────────────────────────────
   GET       /api/artifacts/{artifactId}/explanation    ExplainArtifact
  ────────  ─────────────────────────────────────────  ────────────────────────────────────
   GET       /api/artifacts/{artifactId}/diff           Immutable artifact diff projection

  Inline artifact content should be redacted or omitted from event payloads. Return content only through the blob/CAS policy boundary.

  ### Topologies — 6

   Method    Route                            Backend operation
  ━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GET       /api/topologies                  List topology declarations
  ────────  ───────────────────────────────  ──────────────────────────────────
   POST      /api/topologies                  Parse/store topology
  ────────  ───────────────────────────────  ──────────────────────────────────
   GET       /api/topologies/{id}             Read topology
  ────────  ───────────────────────────────  ──────────────────────────────────
   PUT       /api/topologies/{id}             CAS update
  ────────  ───────────────────────────────  ──────────────────────────────────
   POST      /api/topologies/{id}/validate    parse_topology
  ────────  ───────────────────────────────  ──────────────────────────────────
   POST      /api/topologies/{id}/lower       lower_topology, capability-gated

  Do not expose topology fields that carry authority. topology.py already rejects authority-bearing topology data; the gateway must preserve that
  behavior.

  ### Skills — 5

   Method    Route                        Backend operation
  ━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GET       /api/skills                  Skill index
  ────────  ───────────────────────────  ──────────────────────────────────────
   POST      /api/skills/candidates       Candidate registration
  ────────  ───────────────────────────  ──────────────────────────────────────
   GET       /api/skills/{id}             Skill card/detail
  ────────  ───────────────────────────  ──────────────────────────────────────
   POST      /api/skills/{id}/evaluate    Evaluation request, capability-gated
  ────────  ───────────────────────────  ──────────────────────────────────────
   POST      /api/skills/{id}/promote     Governance-gated promotion

  Promotion must not be implemented as a plain CRUD update. It requires the relevant evaluation and governance evidence.

  ### Governance — 5

   Method    Route                                     Backend operation
  ━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   GET       /api/governance/approvals                 Pending durable approval projection
  ────────  ────────────────────────────────────────  ─────────────────────────────────────
   GET       /api/governance/approvals/{id}            Approval challenge/status
  ────────  ────────────────────────────────────────  ─────────────────────────────────────
   POST      /api/governance/approvals/{id}/resolve    Signed approval decision
  ────────  ────────────────────────────────────────  ─────────────────────────────────────
   GET       /api/governance/processes                 Governance process projection
  ────────  ────────────────────────────────────────  ─────────────────────────────────────
   GET       /api/capabilities                         M-6/M-7/M-8 capability status

  Existing compatibility routes:

  - /api/health
  - /api/events/stream
  - /api/approvals/resolve

  These should remain temporarily, but be documented as aliases and routed through the canonical handlers.

  ## 4. Failure modes and invariants

  ### Ledger invariants

  - One authoritative SQLite-WAL event store.
  - Sequence numbers are monotonic per run/project.
  - Event sequence assignment occurs inside the database transaction.
  - SSE broadcasts happen only after commit.
  - Cursor replay and live subscription are race-safe.
  - Duplicate commands return the original receipt.
  - Event payloads are never rewritten after append.
  - Projection bugs never mutate ledger history.
  - Fresh-process replay must produce the same folded state and digest.

  ### CAS/concurrency invariants

  Every mutable declaration endpoint must accept:

  {
    "expectedSeq": "42",
    "expectedDigest": "sha256:..."
  }

  Reject stale writes with 409 Conflict.

  Approval resolution must use an expected approval state or challenge digest. Two operators resolving the same approval must result in exactly one
  accepted durable resolution.

  Checkpoint and resume must bind to the checkpoint digest and run sequence.

  ### Security gates

  - Gateway binds to 127.0.0.1 by default.
  - UDS remains mode 0600.
  - Remote HTTP requires authentication before enabling non-loopback binding.
  - CORS must not remain wildcard in production.
  - Browser commands cannot bypass RuntimeService.
  - No API key or private signing key enters event payloads, logs, or HTTP responses.
  - Secrets are redacted at adapter, gateway, and UI projection boundaries.
  - Ed25519 verification is performed only by backend ApprovalAuthority.
  - Approval signatures cover canonical JCS fields, including approval ID, digests, expiry, key ID, resolution, and reviewer.
  - RuntimeService never creates signatures.
  - No gateway route imports kernel or agency.
  - No adapter imports kernel or agency.
  - Kernel LOC remains at or below 1438.

  ### Failure-mode table

   Failure                              Required behavior
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Runtime unavailable                  503 not_available, capability remains degraded
  ───────────────────────────────────  ─────────────────────────────────────────────────────────────────────────────
   Unknown run                          404 not_found
  ───────────────────────────────────  ─────────────────────────────────────────────────────────────────────────────
   Stale cursor                         structured gap/conflict response; client must replay from supplied boundary
  ───────────────────────────────────  ─────────────────────────────────────────────────────────────────────────────
   Duplicate command                    original receipt returned
  ───────────────────────────────────  ─────────────────────────────────────────────────────────────────────────────
   Invalid envelope                     reject before persistence
  ───────────────────────────────────  ─────────────────────────────────────────────────────────────────────────────
   Invalid signature                    403 permission_denied; no resolution event
  ───────────────────────────────────  ─────────────────────────────────────────────────────────────────────────────
   Expired approval                     reject closed
  ───────────────────────────────────  ─────────────────────────────────────────────────────────────────────────────
   M-7/M-8 unavailable                  409 or 503 with capability reason
  ───────────────────────────────────  ─────────────────────────────────────────────────────────────────────────────
   WAL busy/locked                      retry boundedly, then 503; never drop event
  ───────────────────────────────────  ─────────────────────────────────────────────────────────────────────────────
   Client disconnects during command    idempotency key allows safe retry
  ───────────────────────────────────  ─────────────────────────────────────────────────────────────────────────────
   Client disconnects during SSE        reconnect using last accepted sequence
  ───────────────────────────────────  ─────────────────────────────────────────────────────────────────────────────
   Workspace path escape                403 or 404; do not reveal filesystem details
  ───────────────────────────────────  ─────────────────────────────────────────────────────────────────────────────
   Model/provider unavailable           durable run failure/degraded result, not synthetic success

  ## 5. Verification and smoke-test sequence

  Run from the repository root.

  ### Baseline structural gates

  python3 tools/linters/check_boundaries.py
  python3 tools/linters/check_tcb_budget.py
  python3 tools/linters/scan_secrets.py
  python3 tools/linters/check_domain_blindness.py
  python3 tools/linters/check_isolation_policy.py
  python3 tools/linters/check_markdown_links.py

  python3 -m unittest discover -s test -t .

  ### Contract and transport tests

  python3 -m unittest discover -s test/contracts -t .
  python3 -m unittest discover -s test/runtime -t .

  cd vanguard/clients/client-core
  npm test
  npm run typecheck

  cd ../cli
  npm test
  npm run typecheck

  cd ../studio
  npm test
  npm run typecheck

  ### UDS smoke test

  Start a service with a file-backed WAL database and the runtime server:

  python3 -m vanguard.packages.runtime.service.server \
    --socket /tmp/vanguard-runtime.sock

  Then, from the CLI package:

  VANGUARD_RUNTIME_SOCKET=/tmp/vanguard-runtime.sock npm run vg -- \
    run --repo "$PWD" --brief "deterministic integration smoke" --fake-backend

  Verify:

  VANGUARD_RUNTIME_SOCKET=/tmp/vanguard-runtime.sock npm run vg -- doctor
  VANGUARD_RUNTIME_SOCKET=/tmp/vanguard-runtime.sock npm run vg -- event list
  VANGUARD_RUNTIME_SOCKET=/tmp/vanguard-runtime.sock npm run vg -- run checkpoint <run-id>
  VANGUARD_RUNTIME_SOCKET=/tmp/vanguard-runtime.sock npm run vg -- run resume <run-id>

  The exact command aliases should follow the CLI router in vanguard/clients/cli/src/commands/.

  ### Raw NDJSON contract probe

  python3 - <<'PY'
  import json
  import socket
  import uuid

  path = "/tmp/vanguard-runtime.sock"
  frame = {
      "version": "vg.4",
      "frameType": "command",
      "frameId": str(uuid.uuid4()),
      "command": {
          "name": "GetRun",
          "commandId": str(uuid.uuid4()),
          "idempotencyKey": str(uuid.uuid4()),
          "runId": "run-smoke",
          "actor": "operator",
          "payload": {},
      },
  }

  with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
      s.connect(path)
      s.sendall((json.dumps(frame) + "\n").encode())
      print(s.recv(65536).decode())
  PY

  Validate the returned frame against schemas/v4/runtime-service.schema.json.

  ### HTTP gateway smoke test

  Start the gateway against the same durable service composition:

  python3 -m vanguard.packages.runtime.service.studio_gateway \
    --host 127.0.0.1 \
    --port 8000 \
    --workspace "$PWD"

  Probe health:

  curl --fail http://127.0.0.1:8000/api/health
  curl --fail http://127.0.0.1:8000/api/capabilities
  curl --fail http://127.0.0.1:8000/api/runs

  Launch a deterministic run:

  curl --fail \
    -H 'Content-Type: application/json' \
    -d '{"repo":"'"$PWD"'","brief":"gateway smoke","fakeBackend":"deterministic"}' \
    http://127.0.0.1:8000/api/runs/launch

  Stream events with a cursor:

  curl -N \
    'http://127.0.0.1:8000/api/runs/<run-id>/events/stream?afterSeq=0'

  Reconnect using the last received sequence:

  curl -N \
    'http://127.0.0.1:8000/api/runs/<run-id>/events/stream?afterSeq=12'

  The second stream must contain no event with seq <= 12.

  ### Stdio bridge smoke test

  printf '%s\n' \
    '{"command":"doctor","profile":"product"}' \
    '{"command":"code","workspace":"'"$PWD"'","brief":"deterministic stdio smoke","fakeBackend":"deterministic"}' \
  | python3 -m vanguard.packages.runtime.entrypoint --stdin-json

  Confirm that:

  - each input yields exactly one JSON result;
  - no logs are written to stdout;
  - failures are structured;
  - doctor remains daemon-free;
  - code does not create synthetic event-ledger entries unless explicitly requested.

  ### Browser Studio smoke test

  cd vanguard/clients/studio
  npm run build
  npm run serve

  Open:

  http://127.0.0.1:4173

  Verify in order:

  1. health changes to connected;
  2. run launch returns a real run ID;
  3. SSE receives valid vg.4 envelopes;
  4. event sequence is monotonic;
  5. browser reload resumes from the last cursor;
  6. approval UI displays the real challenge;
  7. unsigned approval is rejected;
  8. correctly signed approval produces exactly one ApprovalResolved;
  9. M-7/M-8 unavailable features show capability status instead of crashing.

  ### Replay parity gate

  For every integration fixture:

  1. run through Stdio;
  2. run through UDS;
  3. run through HTTP/SSE;
  4. persist the resulting WAL;
  5. replay the WAL in a fresh Python process;
  6. compare event digest, terminal state, approval state, artifact references, and projection output.

  The three transports may differ in framing and latency, but they must produce identical durable runtime truth.