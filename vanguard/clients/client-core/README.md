# `@vanguard/client-core`

Headless core package for Vanguard runtime clients. Provides contract types, vg.4 parser, RFC 8785 Ed25519 signer, live UDS/feed transports, replay/scenario adapters, session selectors, DAG trace projections, and run-view state reducers.

Shared by Ink TUI (`@vanguard/cli`) and Standalone GUI IDE (`vanguard-gui`).

Skins (Ink TUI `@vanguard/cli` and Standalone GUI `vanguard-gui`) must **never** import `vanguard/packages` directly. All agent runtime interactions, governance approvals, session streaming, and trace projections pass exclusively through `@vanguard/client-core` public ports and VG-04 wire envelopes.

## Exported SDK API Table

| Export | Kind | Description |
|---|---|---|
| `RuntimeClient` | Port Interface | Core port contract for daemon interaction (`startRun`, `streamEvents`, `getRun`, etc.) |
| `reduceRunView` | Reducer | Pure state reducer projecting `RunViewModel` from VG-04 `EventEnvelope` items |
| `selectStatusBar` | Selector | Pure selector returning `StatusBarModel` (`source`, `seq`, `tokens`, `costMicros`, `kind`) |
| `windowTranscript` | Selector | DOM-free virtualized transcript windowing with cursor clamping |
| `toTraceGraph` | Projection | UI-agnostic DAG projection (`nodes`, `edges`) from VG-04 event envelopes |
| `subscribeRun` | Helper | Single stream subscriber handling `for await` iteration and `AbortSignal` |
| `attachLive` | Factory | Connect factory returning `LiveRuntimeClient` over Unix Domain Socket |
| `whyFromResult` | Helper | Artifact activation explanation formatter pass-through (`formatExplanation`) |
| `OperatorSigner` | Security Adapter | RFC 8785 JCS Ed25519 cryptographic signer for operator approval receipts |

## Reconnection & Cursor Strategy

`LiveRuntimeClient` automatically handles UDS socket reconnects using `EventCursor.afterSeq`. Upon reconnect, client resumes streaming after the last received sequence number without losing event order or duplicating state.
