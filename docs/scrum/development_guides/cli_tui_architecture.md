# CLI/TUI architecture and runtime-client contract

Status: `APPROVED — Tech Lead, frontend foundation scope`  
Decision date: 2026-08-15  
Revision: 2.0 (2026-08-17 — Client core extraction, Ink TUI scope, GUI reuse boundaries)  
Applies to: `vanguard/clients/cli/**` (Lane FE-2) and `@vanguard/client-core` (Lane FE-1)  
Authority: implementation-level client interface under VG-04 and ADR-0062; this document does not amend VG-04 wire schemas, authority paths, or backend sprint exit gates  
Parent lock: `docs/scrum/development_guides/frontend_senior_review_and_two_lanes.md`

## 1. Decision

T6.4 frontend work proceeds independently from the engine. It remains a pure client of the runtime and does not become a seventh core package, a second event model, a policy authority, or a substitute process engine.

The architecture follows **One Client Core, Multiple Skins**:

```text
terminal / JSONL / GUI Host
       |
presentation: Ink TUI screens (vanguard/clients/cli/src/tui) OR GUI Slots (vanguard-gui)
       |
application & core: @vanguard/client-core (run-view reducer, approvals, use cases)
       |
outbound client port: RuntimeClient
       |
scenario adapter | replay adapter | live vg.4-frame adapter
       |
RuntimeService daemon (Unix domain socket /tmp/vanguard-runtime.sock)
```

Dependencies point inward. Presentation depends on application contracts. Application code depends on the client port and parsed domain types. Adapters depend on the client port. Presentation and application layers never import runtime internals, kernel, agency, concrete backend adapters, transport libraries, or process globals.

---

## 2. Minimum client contract v0.1

This is a client API, not a durable wire schema and not a new core `Port`. Source of truth: `@vanguard/client-core` (`src/contract/types.ts` and `parse.ts`). Semantics:

```ts
type ClientContractVersion = "0.1";
type StreamSource = "mock" | "replay" | "live";

interface RuntimeClient {
  startRun(request: StartRunRequest, signal?: AbortSignal): Promise<Result<RunRef>>;
  streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>>;
  getRun(runId: string, signal?: AbortSignal): Promise<Result<RunSnapshot>>;
  requestCancel(runId: string, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  requestCheckpoint(runId: string, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  requestResume(request: ResumeRunRequest, signal?: AbortSignal): Promise<Result<RunRef>>;
  explainArtifact(artifactId: string, signal?: AbortSignal): Promise<Result<ArtifactExplanation>>;
  resolveApproval(request: ResolveApprovalRequest, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  recordCorrection(record: CorrectionRecord, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  getDaemonStatus(signal?: AbortSignal): Promise<Result<DaemonStatus>>;
}
```

Required semantics:

1. Command methods submit requests; a successful receipt does not claim the durable transition completed. Completion is learned from canonical events.
2. `streamEvents` yields only valid `EventEnvelope` structures. It does not synthesize imaginary envelopes.
3. Every method returns an explicit `Result<T>`. Throwing across layer boundaries is prohibited.
4. `explainArtifact` projects `ActivationChanged` events. When no activation exists, it returns `status: "unknown"`.

---

## 3. Core Package Boundaries & GUI Reuse

1. **`@vanguard/client-core`** contains:
   - `contract/`: pure TypeScript types and `parseEventEnvelope` parser.
   - `adapters/`: `LiveRuntimeClient`, `ReplayRuntimeClient`, `ScenarioRuntimeClient`, `OperatorSigner` (RFC 8785 Ed25519).
   - `application/`: `run-view` reducer (`reduceRunView`), approvals state.
2. **`vanguard/clients/cli/**`** contains Ink TUI presentation (`tui/`), CLI composition, headless mode (`--headless`), and executable entrypoints (`src/main.tsx`).
3. **GUI Reuse Rule:** The GUI (`vanguard-gui/**`) imports `@vanguard/client-core`. It **must not import Ink components**. If the GUI needs terminal execution of `vg`, it embeds an xterm PTY running the CLI binary.

---

## 4. Engineering rules

- Keep business and reduction logic in `.ts`; use `.tsx` only for rendering/composition.
- Prefer pure functions, readonly inputs, and explicit dependency injection. No module-level mutable runtime singleton.
- One stream subscription owner per screen/use case. Cleanup and `AbortController` ownership must be explicit.
- Bound retained events and rendered rows.
- Semantic theme tokens; respect `NO_COLOR`.
- Keyboard actions go through commands/use cases. Components do not call runtime adapters directly.
- Headless and TUI share application use cases and reducers.
- Separate stdout machine output from stderr diagnostics.
- Validate every external object at the adapter edge. Never use a TypeScript cast as parsing (`CT-03`).
- Preserve causality and identity exactly. Never generate missing backend IDs in presentation code.
- Tests use fake clocks and deterministic IDs; timing sleeps are prohibited in contract/reducer tests.

---

## 5. Required verification

- `cd vanguard/clients/cli && npm run typecheck && npm test`
- Adapter contract tests for scenario and replay
- Reducer tests: duplicates, unknown events, bounded buffer
- Golden tests for JSONL and exit codes
- Component tests: keyboard, focus, narrow terminals, no-color
- Boundary CI: no client import of kernel, agency, or `vanguard/packages`
- Live methods: `not_available` rather than mock fallback

---

## Appendix A — Live socket frames (consumer)

Normative: VG-04 §0, §12, §15; ADR-0062; implementation `vanguard/packages/runtime/service/server.py` + `service.py`. FE does not add verbs.

**Transport:** Unix domain socket, NDJSON lines, `version: "vg.4"`. Max frame **1 MiB** (`MAX_FRAME_BYTES`). Socket file mode 0600 on the daemon side.

**Path resolution (CLI & GUI):** `--socket-path` (or GUI config) → env `VANGUARD_RUNTIME_SOCKET` → `/tmp/vanguard-runtime.sock`.

**Client command frame:** `frameType: "command"` with `command.{name,commandId,idempotencyKey,runId,actor,payload}`.

**Implemented command names:** `StartRun`, `GetRun`, `StreamEvents`, `ResolveApproval`, `Cancel`, `Checkpoint`, `Resume`, `RecordCorrection`, `ExplainArtifact`.

**Responses:** `frameType: "receipt"` (`receipt.status` completed/error) or `frameType: "error"`. Event stream: `frameType: "event"` with `event` envelope.

**Not implemented (do not call; Joint if needed):** `Ping` (J2), `ListManifests` (J3), Named Pipe / TCP (J5).

**StartRun payload (existing shape):** `manifestPath`, `repoPath`, `brief`. Editor / workspace context folds into `brief`.

---

## Appendix B — Fixture Catalog & Replay

Replay fixtures live in `vanguard/clients/cli/fixtures/`:
- `successful-episode.jsonl`: Full episode trajectory with `EpisodeStarted`, `EpisodeStateChanged`, `EffectPreviewed`, and `EpisodeCompleted`.
- `why-typed-tools.jsonl`: Governance `ActivationChanged` envelope for testing `explainArtifact`.
