---
id: ref.configuration
canonical_id: ref.configuration
class: reference
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: runtime-composition
canonical_for:
  - profile presets/aliases
  - configuration keys
  - state/store locations
  - provider selection inputs
purpose: Own execution profiles, environment keys, state paths and model/provider configuration.
audience:
  - operator
  - developer
  - contributor
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
evidence:
  - E-B-002
  - E-B-024
  - E-B-025
  - E-B-042
  - E-B-043
  - E-B-045
  - E-B-047
  - E-B-048
  - E-B-052
relationships:
  - arch.system.overview
  - guide.getting-started
  - ref.commands
reviewer: documentation-specialist
confidence: high
---

# Configuration & Execution Profiles Reference

## Purpose
This document is the canonical reference owner for runtime execution profiles, profile presets, environment variable configuration, filesystem state directory layouts, and model provider routing options.

## Scope
- `ExecutionProfile` presets (`product`, `local`, `hermetic`, `sandboxed`, `evaluation`) and schema fields (`mhf.execution-profile/2`).
- Environment variables governing runtime operation, provider selection, and debug logging.
- Default filesystem locations for workspace state, SQLite databases, blobs, and keyrings.
- Model adapter selection parameters.

## Non-responsibilities
- Step-by-step setup guides (owned by [`guide.getting-started`](../guides/getting-started.md)).
- Kernel security containment and isolation architecture (owned by [`arch.trust.kernel`](../architecture/kernel.md)).
- Storing live secrets or credentials in repository files (forbidden by security rules).

## AS_BUILT Status
- `IMPLEMENTED` — Profiles and runtime bootstrap configurations are fully enforced in `vanguard.packages.runtime.profiles` and `vanguard.packages.runtime.bootstrap`.

---

## 1. Execution Profile Presets (`PRESETS`)

Execution profiles (`mhf.execution-profile/2`) define the containment backend, approval requirements, persistence mode, assurance level, and retention for a run (`RF-87`).

| Profile ID | Process Backend | Workspace Mode & Access | Approval Default | Persistence | Evaluation Mode | Assurance Level | Retention |
|---|---|---|---|---|---|---|---|
| `product` (Default) | `host` | `in-place` / `workspace-write` | `ask` | `sqlite-wal` (durable) | `none` (optional) | `recorded` | `standard` |
| `local` | `host` | `in-place` / `workspace-write` | `ask` | `sqlite-wal` (durable) | `none` | `recorded` | `standard` |
| `hermetic` | `platform-sandbox` | `sealed` / `read-only` | `deny` | `sqlite-wal` (durable) | `exterior` | `hermetic` | `full` |
| `sandboxed` | `platform-sandbox` | `sealed` / `workspace-write` | `ask` | `sqlite-wal` (durable) | `none` | `recorded` | `standard` |
| `evaluation` | `platform-sandbox` | `sealed` / `read-only` | `deny` | `sqlite-wal` (durable) | `exterior` | `hermetic` | `full` |

### Key Profile Constraints
- **Fail-Closed Sandbox**: If `sandboxed` or `hermetic` is selected and the sandbox backend (`bwrap`) is unavailable, runtime fails immediately with `SandboxUnavailable` (`INV-B-001`, `RF-88`). Silent fallback to `host` is prohibited.
- **Hermetic Invariants**: `hermetic` assurance requires `attestation_required: true`, `retention: "full"`, and `evaluation_mode: "exterior"`.

---

## 2. Filesystem State Layout

Runtime operations persist state inside the workspace `.vanguard/` directory by default:

```text
<workspace_root>/.vanguard/
├── state.db                # SQLite WAL database for event store, checkpoints, and runs
├── state.db-wal            # SQLite Write-Ahead Log
├── blobs/                  # Content-addressed artifact blob storage (CAS)
│   └── sha256/
│       └── <aa>/<bb>/<digest>
├── keys/                   # Local Ed25519 operator signing keys
│   └── operator.key
└── cassettes/              # Recorded model interaction cassettes (optional)
```

---

## 3. Environment Variables

Runtime configuration reads exclusively from environment variables:

| Variable Name | Default Value | Description |
|---|---|---|
| `VANGUARD_STATE_DIR` | `<workspace>/.vanguard` | Root directory for runtime state, databases, and blobs. |
| `VANGUARD_PROFILE` | `product` | Default execution profile ID if not specified in command. |
| `VANGUARD_LOG_LEVEL` | `INFO` | Python logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `VANGUARD_EVALUATOR_PORT`| `10002` | Default TCP port for `vanguard-evaluator` daemon. |
| `VANGUARD_DAEMON_SOCKET` | `<state_dir>/daemon.sock` | UNIX domain socket path for `vanguard-daemon`. |
| `OPENROUTER_API_KEY` | *(None)* | API credential for OpenRouter model provider adapter. |
| `DEEPSEEK_API_KEY` | *(None)* | API credential for DeepSeek model provider adapter. |
| `OPENAI_API_KEY` | *(None)* | API credential for OpenAI model provider adapter. |
| `OLLAMA_HOST` | `http://localhost:11434` | Endpoint for local Ollama model provider adapter. |

---

## 4. Model Adapter Inputs

Model routing is selected via model route IDs (e.g. `openrouter:anthropic/claude-3.5-sonnet`, `ollama:llama3.1`, `cassette:fixtures/task1.json`, `fake:deterministic`):

- **`openrouter`**: Requires `OPENROUTER_API_KEY`.
- **`ollama`**: Connects to `OLLAMA_HOST`.
- **`cassette`**: Loads recorded interactions from file path; completely hermetic with zero network calls.
- **`fake`**: In-memory deterministic responses for unit and contract testing.

---

## Implementation Evidence

- **Profiles Implementation**: `vanguard/packages/runtime/profiles.py` (`ExecutionProfile`, `PRESETS`, `resolve_profile`).
- **Bootstrap & Configuration**: `vanguard/packages/runtime/bootstrap.py`.
- **Model Adapters**: `vanguard/packages/adapters/models/openrouter.py`, `ollama.py`, `cassette.py`, `fake.py`.
- **Profile Contract Tests**: `test/contracts/test_execution_profile_v2.py`, `test/falsifiers/test_rf87_execution_profile_identity.py`.
