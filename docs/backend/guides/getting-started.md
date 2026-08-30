---
id: guide.getting-started
canonical_id: guide.getting-started
class: how-to
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: guides-operator
canonical_for:
  - installation/run procedure
  - expected output
  - basic troubleshooting
purpose: Guide newcomers through environment setup, workspace initialization, first task run, and basic troubleshooting.
audience:
  - newcomer
  - operator
  - developer
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
evidence:
  - E-B-002
  - E-B-024
  - E-B-025
  - E-B-040
  - E-B-042
  - E-B-043
  - E-B-046
  - E-B-047
  - E-B-052
relationships:
  - arch.system.overview
  - ref.commands
  - ref.configuration
  - guide.run-resume
reviewer: documentation-specialist
confidence: high
---

# Getting Started with Vanguard

## Purpose
This guide is the canonical owner for the end-to-end installation procedure, workspace state initialization, first agent run execution, expected console outputs, and basic troubleshooting steps.

## Scope
- Installing Python (`vanguard`) and TypeScript (`vg`) tools.
- Initializing workspace `.vanguard/` state and key material.
- Running a first task through the canonical runtime harness.
- Verification and doctor health checks.

## Non-responsibilities
- Complete command-line flag syntax tables (owned by [`ref.commands`](../reference/commands.md)).
- Deep runtime execution lifecycle internals (owned by [`arch.runtime.execution`](../architecture/runtime-execution.md)).
- Advanced service daemon clustering (owned by [`guide.operate-service`](operate-runtime-service.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Verified working procedures across Python 3.10+ and Node.js 20+ environments.

---

## 1. Prerequisites

- **Python**: `>= 3.10` (Python 3.12 recommended).
- **Node.js**: `>= 20.0.0` with `npm` (for TypeScript CLI).
- **Bubblewrap** (`bwrap`): Optional, required only when running with `hermetic` or `sandboxed` execution profiles.
- **Model API Key**: `OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY`, `OPENAI_API_KEY`, or a running local Ollama daemon (`http://localhost:11434`).

---

## 2. Installation

From the repository root:

```bash
# 1. Install Python dev package in editable mode
python3 -m pip install -e ".[dev]"

# 2. Install TypeScript dependencies and build client binaries
npm ci
npm run build
```

Verify installed console scripts:

```bash
vanguard --version
```

---

## 3. Workspace Initialization (`init`)

Initialize the local workspace state directory and generate local operator Ed25519 signing keys:

```bash
vanguard init
```

This creates the `.vanguard/` directory layout:
- `.vanguard/state.db` (SQLite WAL database for events and checkpoints)
- `.vanguard/blobs/` (Content-addressed artifact storage)
- `.vanguard/keys/` (Local operator keypair)

---

## 4. Environment Health Check (`doctor`)

Run the diagnostics command to verify system readiness:

```bash
vanguard doctor
```

Expected output:
```text
[OK] Python Runtime: 3.12.x
[OK] SQLite WAL Store: writable (.vanguard/state.db)
[OK] Blob Store: writable (.vanguard/blobs/)
[OK] Bubblewrap Backend: available (/usr/bin/bwrap)
[OK] Default Profile: product
```

---

## 5. Running Your First Task (`run`)

Execute a task using the Python CLI:

```bash
vanguard run "Create a python script that computes fibonacci numbers"
```

### Expected Output
1. Composition logs showing loaded pack (`code-default`) and computed digests ($D_H, D_R$).
2. Monotonic turn steps (`Observe` -> `Propose` -> `Dispatch` -> `Ingest`).
3. Tool execution receipts (`view_file`, `replace_file_content`, etc.).
4. Terminal disposition: `COMPLETED` with final run summary and artifact reference.

---

## 6. Basic Troubleshooting

| Symptom | Probable Cause | Corrective Action |
|---|---|---|
| `SandboxUnavailable` error | `hermetic` or `sandboxed` profile requested without `bwrap` installed. | Install `bubblewrap` package or switch to `--profile product` (`ref.configuration`). |
| `Missing API Key` | Model provider environment variable unset. | Set `OPENROUTER_API_KEY` in environment or run local Ollama daemon. |
| `Database Locked` | Concurrent process accessing SQLite without WAL enabled. | Verify `.vanguard/state.db-wal` exists and kill orphan daemon processes. |

---

## Next Steps
- Learn how to inspect runs, stream events, and resume from interruptions in [Run, Inspect & Resume Guide](run-and-resume.md).
- Learn how to operate the background daemon in [Operate Runtime Service Guide](operate-runtime-service.md).
