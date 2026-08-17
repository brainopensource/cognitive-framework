# 004 — UI / UX (Proposed)

Status: `Proposed`  
Date: 2026-08-16  
Event names: VG-04 §12.2 only.

## Run state machine (derived, not a second ledger)

Reduce envelopes into view states. Canonical kinds that drive the run chrome:

| Kind | Typical view effect |
|---|---|
| `EpisodeStarted` | run active |
| `EpisodeStateChanged` | status text from payload |
| `EpisodeCompleted` | terminal success/fail from payload |
| `AuthorizationDenied` | hard fail banner |
| `BudgetReserved` / `BudgetCommitted` / `BudgetReleased` | budget panel |
| `EffectPreviewed` / `EffectStarted` / `EffectCompleted` / `EffectReconciled` | tool / effect timeline |
| `ApprovalRequested` | modal / CodeLens pending |
| `ApprovalResolved` | modal closed; never mark approved on local click alone |
| `Heartbeat` / `RunRecovered` / `RunAborted` | connection / recovery chrome |

Unknown `payload.kind`: keep in the timeline as opaque; do not crash (`CT-44`).

## Tokens

Semantic tokens (success, warning, danger, muted, accent). Information must survive `NO_COLOR`. IDE webview (FE-B3) reuses the same names; map to VS Code CSS variables where possible.

## Labelling

`source: mock` vs `replay` vs `live` must be visible on the run header (CLI and IDE).
