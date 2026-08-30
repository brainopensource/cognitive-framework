---
id: product.frontend.cli
class: product
authority: proposal
canonical_for:
  - aether-cli-product-requirements
status: proposed
owner: product-architecture
version: "0.1.0"
last_verified: 2026-08-29
future_canonical_owner: docs/product/frontend/PRD_AETHER_CLI.md
subordinate_to:
  - product.frontend.platform
  - ../../../SPEC.md
---

# Product Requirements Document: AETHER CLI (Headless Automation & CI)

## 1. Executive Summary & Product Thesis

**AETHER CLI** (`aether` / `vg`) is the headless, scriptable command-line interface for the AETHER agentic substrate. It is specifically optimized for deterministic automation, continuous integration (CI) environments, shell scripting pipelines, and remote orchestration.

### 1.1 Core Thesis

> **The CLI is a precision UNIX instrument: quiet by default, deterministic in exit codes, pipe-friendly in streaming data, and strictly decoupled from terminal rendering engines.**

The CLI operates purely as a command dispatcher and structured stream transmitter. When executed in an interactive terminal without subcommands, it MAY auto-detect TTY presence and offer to delegate to the AETHER TUI. When invoked with explicit commands or in non-interactive pipes, it executes strictly headlessly.

---

## 2. AS_BUILT vs. TARGET State Assessment

| Dimension | AS_BUILT (Repository Evidence) | TARGET (Electroweak Baseline) | Strategic Gap & Action |
|---|---|---|---|
| **Runtime & Packaging** | Node.js + `tsx` runtime (`vanguard/clients/cli/package.json`), running interpreted TypeScript. | Standalone compiled native binary built with **Bun** (`bun build --compile`). | Migrate build pipeline to Bun to achieve low cold startup latency for automation. |
| **Command Implementation** | Mixed legacy handlers in `vanguard/clients/cli/src/commands/legacy.tsx` with Ink dependencies. | Clean command handlers in `@aether/cli` relying purely on `@aether/client` SDK. | Remove all React/Ink dependencies from CLI command execution paths. |
| **Streaming Output** | Basic console logging with partial JSON flags. | Strict dual-mode output: Human-readable ANSI summaries vs Line-delimited NDJSON streams (`--ndjson`). | Implement strict NDJSON event streaming to `stdout` with diagnostics on `stderr`. |
| **Exit Code Protocol** | Ad-hoc exit codes (0 for success, 1 for error). | Formally specified exit code contract (0–6, 130) matching machine-verifiable failure classes. | Standardize exit codes across all commands and automated tests. |

---

## 3. Users & Jobs-to-be-Done

- **CI/CD Engineers**: Embed autonomous agent runs into pull request evaluation workflows (e.g. `aether run --agent pr-reviewer --repo .`).
- **DevOps & Automation Developers**: Write shell scripts that trigger agent runs, stream structured events into `jq` or observability sinks, and extract generated artifacts.
- **Systems Developers**: Inspect daemon health (`aether doctor`), tail event ledgers (`aether event tail`), and manage agent manifests without launching graphical interfaces.

---

## 4. Proposed Command Taxonomy & Grammar (Product Scope)

```text
aether [command] [subcommand] [flags]
```

### 4.1 Execution & Run Management

```text
aether run [options]
  --agent <id>            Agent identifier or path to agent manifest
  --workflow <id>         Workflow identifier or path to workflow manifest
  --repo <path>           Target repository/workspace path (default: current directory)
  --prompt <string>       Initial user prompt/objective
  --profile <id>          Execution assurance profile (default: standard)
  --non-interactive       Fail immediately if human approval is required
  --json                  Output single terminal JSON snapshot upon completion
  --ndjson                Stream line-delimited EventFrame JSON to stdout

aether run list [options]
  --limit <n>             Maximum number of runs to return (default: 20)
  --status <state>        Filter by state: running|satisfied|failed|awaiting_approval
  --json                  Emit JSON array of run summaries

aether run inspect <run-id> [--json]
aether run stream <run-id> [--after-seq <n>] [--ndjson]
aether run cancel <run-id> [--reason <string>]
aether run checkpoint <run-id>
aether run resume <run-id> [--checkpoint <id>]
aether run replay <fixture-path> [--speed <multiplier>]
```

### 4.2 Agents & Workflows

```text
aether agent list [--json]
aether agent inspect <agent-id> [--json]
aether agent validate <manifest-path> [--json]

aether workflow list [--json]
aether workflow inspect <workflow-id> [--json]
aether workflow validate <manifest-path> [--json]
aether workflow run <workflow-path> [--input <json-file>]
```

### 4.3 Artifacts, Ledger & Governance

```text
aether artifact list [--run-id <id>] [--kind <kind>] [--json]
aether artifact get <digest> [--output <file-path>]
aether artifact explain <digest> [--json]

aether event tail <run-id> [--after-seq <n>] [--ndjson]
aether evidence verify <run-id> [--trust-root <path>]

aether approve <approval-id> --decision approved|rejected [--key <path>]
aether doctor [--json]
aether daemon start|stop|status
```

*Note: The exact command-line options, argument parsing conventions, and formatting schemas belong to future reference documentation (`docs/reference/frontend/cli-commands.md`).*

---

## 5. Machine-Readable Output Formats

### 5.1 JSON Output Mode (`--json`)

When `--json` is specified, `stdout` MUST contain only a single valid JSON object representing the command outcome, and `stderr` receives all diagnostic or logging information:

```json
{
  "api": "aether.cli-outcome/1",
  "command": "run",
  "runId": "run-018f-9a4b-7c12",
  "status": "satisfied",
  "verdict": "1",
  "metrics": {
    "totalTokens": 3840,
    "costMicros": "76800",
    "durationMs": 4250,
    "turns": 3
  },
  "artifacts": [
    {
      "digest": "sha256:44a2b8e390c1f4...",
      "kind": "patch",
      "path": "vanguard/packages/kernel/dispatch.py"
    }
  ]
}
```

### 5.2 NDJSON Streaming Mode (`--ndjson`)

When `--ndjson` is specified, each emitted `EventEnvelope` is written as a single line of minified JSON to `stdout`, enabling real-time streaming into external tools:

```text
{"version":"vg.4","frameType":"event","frameId":"frm-01","event":{"seq":"1","payload":{"kind":"GoalDeclared","goal":"Fix auth race"}}}
{"version":"vg.4","frameType":"event","frameId":"frm-02","event":{"seq":"2","payload":{"kind":"ContextCompiled","tokens":1240}}}
{"version":"vg.4","frameType":"event","frameId":"frm-03","event":{"seq":"3","payload":{"kind":"EffectStarted","action":"fs.read"}}}
```

---

## 6. AETHER CLI Exit Code Contract

The CLI MUST adhere to a deterministic, structured exit code contract:

| Code | Label | Trigger Condition |
|---:|---|---|
| `0` | `SUCCESS` | Run satisfied all objectives, verification passed, command completed normally. |
| `1` | `EXECUTION_FAILED` | Agent completed execution but failed task assertions or tests. |
| `2` | `INVALID_INPUT` | Command-line arguments failed schema validation or manifest was malformed. |
| `3` | `APPROVAL_REQUIRED` | Non-interactive execution halted because governance approval was requested. |
| `4` | `PERMISSION_DENIED` | Capability check failed, cryptographic signature invalid, or unauthenticated. |
| `5` | `RESOURCE_EXHAUSTED` | Execution terminated due to budget exhaustion (tokens, cost, turns, or time). |
| `6` | `DAEMON_UNAVAILABLE` | Could not establish connection to local AETHER RuntimeService UDS/HTTP socket. |
| `130` | `INTERRUPTED` | Process received `SIGINT` (Ctrl+C) and completed graceful cancellation. |

---

## 7. Stream Handling & Signal Management

- **Graceful Cancellation (`SIGINT` / `SIGTERM`)**: Upon receiving an interrupt signal, the CLI MUST send a CAS `Cancel` command to `RuntimeService` with the current `expectedSeq`, wait up to 5 seconds for the runtime to settle, and exit with code `130`.
- **Broken Pipe Handling (`EPIPE`)**: If `stdout` is closed by a downstream consumer (e.g. `aether run stream ... | head -n 5`), the CLI MUST handle `EPIPE` cleanly and exit immediately with code `0` without printing unhandled traceback errors to `stderr`.

---

## 8. Provisional Performance Targets

The following values represent **provisional engineering budgets (TARGET thresholds)** subject to verification via automated performance benchmarks:

- **Cold Startup Latency**: Provisional target of $<15\text{ ms}$ for binary invocation to version/help output under Bun on reference hardware.
- **Memory Consumption**: Provisional target of Resident Set Size (RSS) $<35\text{ MB}$ during active NDJSON streaming.
- **Zero VDOM / React Footprint**: The CLI binary MUST contain zero React, VDOM, or UI framework dependencies.

---

## 9. Non-Goals & Out-of-Scope Boundaries

- **NON-GOAL 1**: Interactive full-screen terminal dashboards (owned exclusively by `PRD_AETHER_TUI`).
- **NON-GOAL 2**: Local execution of LLMs or sandboxed tools directly within the CLI process.
- **NON-GOAL 3**: Persistent local state management outside of standard CLI configuration files (`~/.config/aether/config.json`).

---

## 10. Candidate Future Documents & Ownership References

- **Candidate Architecture Owner**: `docs/architecture/frontend/cli-architecture.md`
- **Candidate Reference Owner**: `docs/reference/frontend/cli-commands.md`
- **Candidate Decisions Owner**: `docs/decisions/frontend/0108-cli-headless-posix-standard.md`
- **Candidate Execution Owner**: `docs/execution/frontend/cli-backlog.md`
