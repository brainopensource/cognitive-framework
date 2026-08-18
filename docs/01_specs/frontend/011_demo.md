---
id: FE-11
file: 011_demo.md
title: "Vanguard v4.0 — Mock Prototype & Demo Specification"
version: 4.0.0
status: DISPOSABLE
authority_scope: >
  Offline fixture playback, `--demo` catalog specifications, and replay rules.
supersedes: none
superseded_by: none
budget_words: 1500
owners: [Tech Lead]
last_reviewed: 2026-08-17
---

# Vanguard v4.0 — Mock Prototype & Demo Specification

> **Who this is for.** Anyone testing or demonstrating Vanguard frontend surfaces offline.

---

## 1. Demo Fixtures & Storage

- Standard fixtures live under `vanguard/clients/cli/fixtures/*.jsonl`.
- Catalog demonstrations live under `vanguard/clients/cli/fixtures/sessions/`.
- No mock fixtures may be stored under `docs/`.

---

## 2. Mandatory Mock Labelling

Every replay and demo surface must display `source: mock` explicitly on headers, JSONL stream items, and GUI badges. Offline replays must never claim live status.

---

## 3. Daemonless Execution

Both `vg --demo` and the standalone GUI shell render full episode lifecycles offline via `ReplayRuntimeClient` without requiring an active daemon socket.
