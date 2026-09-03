---
id: arch.interfaces.clients
canonical_id: arch.interfaces.clients
class: architecture
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: PARTIAL
owner: application-interfaces
canonical_for:
  - application boundary responsibility
  - transport relationships
  - client projection ownership
  - known interface drift
purpose: Map external application, CLI, daemon, and Studio client surfaces and their architectural boundaries.
audience:
  - developer
  - architect
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-09-03
evidence:
  - E-B-002
  - E-B-005
  - E-B-025
  - E-B-042
  - E-B-043
  - E-B-044
  - E-B-045
  - E-B-046
  - E-B-047
  - E-B-048
  - E-B-049
  - E-B-052
relationships:
  - arch.system.overview
  - ref.commands
  - ref.runtime-service
reviewer: documentation-specialist
confidence: high
---

# Application & Client Interfaces Architecture

## Purpose
This document is the canonical architecture owner for the external interface map, client-runtime transport boundaries, client-side projection models, and documented integration asymmetries between Python and TypeScript client stacks.

## Scope
- Architecture of client interaction surfaces: Python CLI, TypeScript `vg` CLI, Runtime Service Daemon, and Vanguard Studio Gateway.
- Client-side projection ownership and event stream ingestion.
- Transport mechanisms: UNIX domain sockets, standard I/O, WebSockets, in-process Python APIs.
- Documented interface drift and known integration findings (`UNR-B-001`, `UNR-B-003`, `UNR-B-008`).

## Non-responsibilities
- Exact CLI command syntax and option tables (owned by [`ref.commands`](../reference/commands.md)).
- Wire frame definitions and error code enums (owned by [`ref.runtime-service`](../reference/runtime-service.md)).
- Visual UI design and CSS/component styling.

## AS_BUILT Status
- `PARTIAL` — Core Python and TypeScript client layers are fully functional, but operate with command vocabulary asymmetry (`UNR-B-003`) and a known live `StartRun` profile default caveat (`UNR-B-001`).

---

## 1. Substrate Interface Architecture Map

Clients interact with Vanguard through distinct entry paths depending on the host environment:

```text
┌─────────────────────────────────────────────────────────────┐
│                       CLIENT SURFACES                       │
│  Python CLI (vanguard)   TS CLI (vg)   Studio Browser / UI │
└──────────────┬─────────────────┬───────────────────┬────────┘
               │                 │                   │
      Direct In-Process      IPC Socket /        WebSocket /
         Python API          vg.4 Frames         JSON Bridge
               │                 │                   │
               │         ┌───────▼───────────────────▼────────┐
               │         │      RuntimeService / Studio       │
               │         │        (Daemon Gateway)            │
               │         └─────────────────┬──────────────────┘
               │                           │
┌──────────────▼───────────────────────────▼──────────────────┐
│                   CANONICAL RUNTIME CORE                    │
│   ApplicationService · HarnessSession · EpisodeEngine       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. In-Process Python Path (`ApplicationService` / CLI)

The Python CLI (`vanguard run`, `vanguard resume`) and applications (`apps/coding_max`) instantiate `ApplicationService` (`vanguard.packages.runtime.app_service.ApplicationService`) and `HarnessSession` within the same OS process:
- **Zero Serialization Overhead**: Uses in-memory domain objects directly.
- **Direct Event Subscription**: Ingests events synchronously via callback handlers.
- **Cassette Support**: Records and deterministically replays model interactions via local cassette files.

---

## 3. Daemon IPC & `vg.4` Service Path

The TypeScript client stack (`@vanguard/cli`, `@vanguard/client-core`) communicates with `vanguard-daemon` using the `vg.4` framed protocol (`ref.runtime-service`):
- **Transport**: Communicates over UNIX domain sockets or standard I/O streams.
- **Client-Side Projections**: `client-core` maintains an in-memory run cache by subscribing to `StreamEvents` and applying optimistic concurrency checks (`expectedSeq`).
- **Cryptographic Signing**: Client-side operators generate and sign Ed25519 approval decisions (`ResolveApproval`) submitted to the daemon.

---

## 4. Vanguard Studio Gateway

`vanguard-studio` (`vanguard.packages.runtime.service.studio_gateway`) acts as a bridge for browser-based visual interfaces:
- Exposes WebSockets for real-time turn visualization, DAG graph inspection, and artifact previews.
- Translates browser REST/WebSocket messages into internal `vg.4` service frames.

---

## 5. Known Integration Realities & Asymmetries

### 1. `StartRun` Profile Mismatch (`UNR-B-001`)
The TypeScript live `StartRun` builder in `client-core` omits `profileId` by default. When the daemon receives a blank profile, it falls back to `code-default` in legacy paths, which is unsupported. Clients must explicitly specify `profileId: "product"` or `profileId: "local"`.

### 2. Command Surface Asymmetry (`UNR-B-003`)
The Python CLI (`vanguard`) and TypeScript CLI (`vg`) expose non-identical command sets (e.g. `cassette` exists only in Python, whereas `vg code`, `vg trace`, `vg why` exist in TypeScript) without a shared command catalog.

### 3. Applications Slot (`apps/coding_max`)
The directory `vanguard/packages/apps/` houses thin application facades (such as `apps/coding_max/facade.py` exposing `CodingMaxFacade`). It operates strictly as a client of `ApplicationService`, selecting presets and validating input without duplicating runtime orchestration.

---

## Implementation Evidence

- **Application Service**: `vanguard/packages/runtime/app_service.py`.
- **Python CLI**: `vanguard/packages/runtime/cli.py`.
- **Daemon Server**: `vanguard/packages/runtime/service/server.py`.
- **TypeScript Client**: `vanguard/clients/client-core/`, `vanguard/clients/cli/`.
- **Parity Tests**: `test/runtime/test_app_service_and_cli.py`, `test/contracts/test_runtime_service_contract_parity.py`.
