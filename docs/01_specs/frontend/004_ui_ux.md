# 004 — UI / UX (Proposed)

Status: `Proposed`  
Date: 2026-08-17  
Event names: VG-04 §12.2 only.  
Skins: Ink TUI (`tui_product_surface.md`) and GUI slots (`gui_ide_slots.md`) share tokens and reducers.

## Run state machine (derived, not a second ledger)

| Kind | Typical view effect |
|---|---|
| `EpisodeStarted` | run active |
| `EpisodeStateChanged` | status text from payload |
| `EpisodeCompleted` | terminal success/fail from payload |
| `AuthorizationDenied` | hard fail banner |
| `BudgetReserved` / `BudgetCommitted` / `BudgetReleased` | budget panel |
| `EffectPreviewed` / `EffectStarted` / `EffectCompleted` / `EffectReconciled` | tool / effect timeline |
| `ApprovalRequested` | TUI modal / GUI approve slot pending |
| `ApprovalResolved` | close pending chrome; never mark approved on local click alone |
| `Heartbeat` / `RunRecovered` / `RunAborted` | connection / recovery chrome |

Unknown `payload.kind`: keep in the timeline as opaque; do not crash (`CT-44`).

## Tokens (TUI + GUI)

Semantic names: `success`, `warning`, `danger`, `muted`, `accent`. Information must survive `NO_COLOR` in the TUI. GUI maps the same names to CSS variables (not VS Code workbench APIs).

## Labelling

`source: mock` vs `replay` vs `live` must be visible on the run header in **both** skins.
