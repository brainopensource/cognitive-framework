---
id: FE-08
file: 008_packaging.md
title: "Vanguard v4.0 — Build, Packaging & Distribution"
version: 4.0.0
status: LIVING
authority_scope: >
  Release channels, installer scripts, global bin distribution, and desktop bundling.
supersedes: none
superseded_by: none
budget_words: 1500
owners: [Tech Lead]
last_reviewed: 2026-08-17
---

# Vanguard v4.0 — Build, Packaging & Distribution

> **Who this is for.** DevOps, release engineers, and frontend packaging developers.

---

## 1. Active Release Channels (Phase 1)

| # | Channel | Target Artifact & Requirements |
|---|---|---|
| 1 | `curl \| sh` via `install.sh` | Requires Node $\ge$ 20, configures socket path, supports `--demo`. |
| 2 | npm global package | `@vanguard/cli` publishing binary `vg` (`vanguard/clients/cli/package.json`). |

---

## 2. Desktop GUI Packaging (Phase 2)

Standalone desktop application packaging (Tauri 2 / AppImage / DMG / MSI) belongs to Lane `FE-3` in Phase 2. VS Code extension packaging (`.vsix`) is VOID.
