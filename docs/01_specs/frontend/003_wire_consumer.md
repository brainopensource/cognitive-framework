# 003 — Wire consumer note (Proposed)

Status: `Proposed`  
Date: 2026-08-16  
**This file is not a protocol spec.** Normative sources: VG-04 §0, §12, §15; ADR-0062 (`docs/main_v4/09_vanguard_decision_register_v040.md`). Implementation: `vanguard/packages/runtime/service/server.py`, `service.py`; client: `vanguard/clients/cli/src/adapters/live.ts`.

Do not add verbs. Do not describe a second envelope format.

## Frames as implemented

NDJSON over Unix domain socket. `version: "vg.4"`. Maximum frame size **1 MiB** (`MAX_FRAME_BYTES = 1024 * 1024`).

| `frameType` | Role |
|---|---|
| `command` | Client → daemon. Body: `command.{name,commandId,idempotencyKey,runId,actor,payload}` |
| `receipt` | Daemon → client. `receipt.{commandId,status,runId,result?\|detail?}` |
| `error` | Parse / frame-too-large / stream errors |
| `event` | Stream body; `event` is a VG-04 envelope |

**Command names in `RuntimeService`:** `StartRun`, `GetRun`, `StreamEvents`, `ResolveApproval`, `Cancel`, `Checkpoint`, `Resume`, `RecordCorrection`, `ExplainArtifact`.

There is no health command. Connect-only probe is current supervisor behavior (Joint **J2**).

## Socket path resolution (CLI / IDE live adapter)

1. `--socket-path` (or IDE setting equivalent)
2. `VANGUARD_RUNTIME_SOCKET`
3. `/tmp/vanguard-runtime.sock`

## JCS (RFC 8785)

Canonicalisation applies to **approval bytes**, not to inventing a house JSON encoding for all frames.

Sign `ApprovalDecision` fields derived from `ApprovalChallenge`: `approvalId`, `argsDigest`, `descriptorDigest`, `expiresAt`, `keyId`, `resolution`, `reviewer`. Use a conformant RFC 8785 library (FE-A3). Do not treat `JSON.stringify(..., Object.keys().sort())` as JCS.

## StartRun payload (do not extend)

`manifestPath`, `repoPath`, `brief`. New fields require a Joint note (D6).
