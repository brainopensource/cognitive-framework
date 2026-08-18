---
id: FE-04
file: 004_ui_ux.md
title: "Vanguard v4.0 — UI/UX Views & Interaction Workflows"
version: 4.0.0
status: LIVING
authority_scope: >
  State machines, color tokens, and labelling rules across Ink TUI
  and Standalone GUI IDE surfaces.
supersedes: none
superseded_by: none
budget_words: 2000
owners: [Tech Lead]
last_reviewed: 2026-08-17
---

# Vanguard v4.0 — UI/UX Views & Interaction Workflows

> **Who this is for.** Designers and frontend developers implementing TUI and GUI views.

---

## 1. Derived Run State Machine

| Event Kind | Typical View Effect |
|---|---|
| `EpisodeStarted` | Run active indicator |
| `EpisodeStateChanged` | Status text update from payload |
| `EpisodeCompleted` | Terminal success / failure banner |
| `AuthorizationDenied` | Hard failure alert banner |
| `BudgetReserved` / `BudgetCommitted` / `BudgetReleased` | Budget tracker panel |
| `EffectPreviewed` / `EffectStarted` / `EffectCompleted` | Effect timeline item |
| `ApprovalRequested` | Interactive modal / pending approval panel |
| `ApprovalResolved` | Close pending modal; update timeline state |
| `Heartbeat` / `RunRecovered` / `RunAborted` | Connection & recovery status |

Unknown `payload.kind` events are preserved opaquely in the timeline without crashing the UI (`CT-44`).

---

## 2. Color Tokens & Design Tokens

Semantic names: `success`, `warning`, `danger`, `muted`, `accent`.
- **TUI**: Information must remain distinguishable under `NO_COLOR`.
- **GUI**: Maps identical semantic names to standard CSS variables.

---

## 3. Mandatory Source Labelling

`source: mock` vs `source: replay` vs `source: live` must be explicitly visible on the header in both TUI and GUI.
