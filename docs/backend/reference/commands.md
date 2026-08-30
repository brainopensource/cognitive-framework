---
id: ref.commands
canonical_id: ref.commands
class: reference
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: PARTIAL
owner: runtime-clients
canonical_for:
  - console scripts
  - CLI commands/options/exit semantics
  - command surface differences
purpose: Provide exact installed Python and TypeScript command surfaces.
audience:
  - operator
  - developer
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
evidence:
  - E-B-002
  - E-B-003
  - E-B-004
  - E-B-005
  - E-B-006
  - E-B-025
  - E-B-040
  - E-B-042
  - E-B-043
  - E-B-046
  - E-B-047
relationships:
  - arch.system.overview
  - guide.getting-started
  - ref.runtime-service
reviewer: documentation-specialist
confidence: high
---

# Command Surfaces Reference

## Purpose
This document is the canonical reference owner for installed console scripts, CLI command-line options, exit codes, output modes, and the structural differences between the Python runtime CLI and the TypeScript client CLI.

## Scope
- Console scripts registered via `pyproject.toml` and `package.json`.
- `vanguard` Python CLI subcommands, flags, arguments, and exit codes.
- `vg` TypeScript CLI subcommands, flags, arguments, and execution behavior.
- Documented behavioral divergence and known command asymmetries (`UNR-B-003`).

## Non-responsibilities
- Runtime internal execution architecture (owned by [`arch.runtime.execution`](../architecture/runtime-execution.md)).
- Detailed step-by-step operator workflows (owned by [`guide.getting-started`](../guides/getting-started.md) and [`guide.operate-service`](../guides/operate-runtime-service.md)).
- Wire frame definitions and daemon protocol mechanics (owned by [`ref.runtime-service`](runtime-service.md)).

## AS_BUILT Status
- `PARTIAL` — Both Python and TypeScript entry points are operational, but expose non-identical command vocabularies and operate independently without a unified command catalog registry (`UNR-B-003`).

---

## 1. Installed Entry Points

The repository registers Python console entry points in `pyproject.toml` and TypeScript workspace binaries in `package.json` / `vanguard/clients/cli/package.json`.

### Python Console Scripts (`pyproject.toml`)

| Console Script | Target Module & Entry Point | Primary Responsibility |
|---|---|---|
| `vanguard` | `vanguard.packages.runtime.cli:main` | Direct local runtime harness execution, run inspection, state queries, and replay. |
| `vanguard-evaluator` | `vanguard.packages.adapters.evaluators.daemon:main` | Standalone exterior evaluator RPC daemon (default port: `10002`). |
| `vanguard-daemon` | `vanguard.packages.runtime.service.server:main` | JSON-RPC / IPC runtime daemon service providing the `vg.4` protocol. |
| `vanguard-studio` | `vanguard.packages.runtime.service.studio_gateway:main` | Gateway server exposing WebSocket and HTTP bridges to visual client UIs. |

### TypeScript Binaries (`package.json`)

| Script / Binary | Path / Invocation | Description |
|---|---|---|
| `vg` | `npm --workspace @vanguard/cli run vg --` | Interactive CLI client interacting with the runtime daemon and local state. |

---

## 2. `vanguard` Python CLI Commands

The Python CLI (`vanguard.packages.runtime.cli:main`) interacts directly with local runtime engines, storage, and cassettes.

### Command Grammar & Options

```text
vanguard [-h] [--version] {init,doctor,cassette,run,resume,status,events,artifacts} ...
```

#### Global Flags
- `-h, --help`: Show help message and exit.
- `--version`: Display runtime package version.

#### Subcommand Summary

| Subcommand | Arguments & Options | Description |
|---|---|---|
| `init` | `[--path PATH]` | Initialize workspace `.vanguard` state directory and generate operator key material. |
| `doctor` | `[--json]` | Verify environment health, tool qualifications, provider reachability, and capability state. |
| `cassette record` | `--run-id RUN_ID --output FILE` | Extract episode interactions from run ledger into a deterministic cassette fixture. |
| `cassette replay` | `--cassette FILE --task TASK` | Replay task execution deterministically against a recorded cassette fixture. |
| `run` | `TASK [--manifest PATH] [--profile ID] [--timeout SECONDS] [--json]` | Execute a single task end-to-end via canonical `HarnessSession`. |
| `resume` | `--run-id RUN_ID [--timeout SECONDS] [--json]` | Resume an interrupted run by replaying its durable SQLite WAL ledger state. |
| `status` | `--run-id RUN_ID [--json]` | Query execution status, current sequence counter, and terminal disposition. |
| `events` | `--run-id RUN_ID [--after-seq N] [--limit N] [--json]` | Query causally ordered event sequence from the event store. |
| `artifacts` | `--run-id RUN_ID --digest SHA256 [--output PATH]` | Retrieve and verify content-addressed artifact bytes against their digest. |

---

## 3. `vg` TypeScript CLI Commands

The TypeScript CLI (`vanguard/clients/cli/src/commands/index.ts`) communicates with running services or inspects compiled schemas and lineages.

### Command Handlers

| Command | Handler (`vanguard/clients/cli/src/commands/`) | Functionality |
|---|---|---|
| `vg init` | `handleInit` (`init.ts`) | Setup local client configuration and key storage. |
| `vg run` | `handleRun` (`legacy.tsx`) | Dispatch a `StartRun` command to the runtime service. |
| `vg code` | `handleCode` (`legacy.tsx`) | Shortcut for coding task execution using default coding pack. |
| `vg explain` | `handleExplain` (`legacy.tsx`) | Request causal explanation of a past decision or artifact. |
| `vg doctor` | `handleDoctor` (`legacy.tsx`) | Probe local and daemon capability health. |
| `vg approve` | `handleApprove` (`legacy.tsx`) | Submit Ed25519-signed operator approval for a pending gate decision. |
| `vg resume` | `handleResume` (`legacy.tsx`) | Dispatch `Resume` command for a suspended run. |
| `vg trace` | `handleTrace` (`legacy.tsx`) | Stream and format live event trace from active execution. |
| `vg why` | `handleWhy` (`legacy.tsx`) | Inspect decision rationale provenance DAG. |
| `vg daemon` | `handleDaemon` (`legacy.tsx`) | Start or inspect local runtime daemon background process. |
| `vg agent` | `handleAgent` (`agent.ts`) | Inspect and validate agent composition definitions. |
| `vg composition` | `handleComposition` (`composition.ts`) | Inspect and validate composed pack configurations. |
| `vg event` | `handleEvent` (`event.ts`) | Validate and inspect raw wire event envelopes. |
| `vg artifact` | `handleArtifact` (`artifact.ts`) | Verify and fetch content-addressed artifact blobs. |
| `vg schema` | `handleSchema` (`schema.ts`) | Validate payloads against JSON Schema definitions. |
| `vg lineage` | `handleLineage` (`lineage.ts`) | Traverse causal parent-child run and episode ancestry. |

---

## 4. Exit Codes and Output Modes

### Exit Codes

| Exit Code | Meaning | Python CLI | TypeScript CLI |
|---|---|---|---|
| `0` | Success / Clean Completion | Task succeeded or query returned valid records. | Command executed and receipt status was `completed`. |
| `1` | General Failure / Evaluation Failure | Task failed, budget exhausted, or evaluator returned `FAILED`. | Service returned `error` or uncaught client error. |
| `2` | Usage / Syntax Error | Invalid command-line arguments or missing required flags. | Argument parse error. |
| `3` | Approval Denied / Policy Violation | Kernel blocked effect due to policy deny or approval rejection. | Operator explicitly denied gate approval. |
| `4` | Connection / Daemon Error | Evaluator or daemon service unreachable. | Runtime service daemon unavailable. |

### Output Modes
- **Human-readable Text / TUI (Default)**: Formatted console output, colorized logs, and status summaries.
- **Structured JSON (`--json`)**: Emits JSON objects to `stdout` for programmatic pipelines, log ingestion, and test automation.

---

## 5. Known Differences & Divergence (`UNR-B-003`)

The Python CLI (`vanguard`) and TypeScript CLI (`vg`) maintain distinct implementations and do not share a single command registry:

1. **Direct Execution vs. Daemon Client**: `vanguard run` directly constructs the Python in-process `HarnessSession`, while `vg run` sends a `StartRun` frame over IPC/JSON-RPC to `vanguard-daemon`.
2. **Command Vocabulary Asymmetry**:
   - `cassette record/replay` is only available in the Python CLI (`vanguard`).
   - `vg code`, `vg explain`, `vg why`, `vg lineage`, `vg approve` exist exclusively in the TypeScript CLI.
3. **Default Profile Handling**: When `vg run` invokes `StartRun` without an explicit `--profile`, it relies on the daemon default (`UNR-B-001`), whereas `vanguard run` defaults to the validated `product` profile.

---

## Implementation Evidence

- **Console scripts**: `pyproject.toml:project.scripts`, `package.json:scripts`.
- **Python CLI source**: `vanguard/packages/runtime/cli.py` (`main`, `build_parser`).
- **TypeScript CLI source**: `vanguard/clients/cli/src/commands/index.ts`, `vanguard/clients/cli/src/commands/legacy.tsx`.
- **CLI Tests**: `vanguard/clients/cli/test/commands.test.ts`, `test/runtime/test_app_service_and_cli.py`.
