---
id: FE-03
file: 003_wire_consumer.md
title: "Vanguard v4.0 — Wire Protocol Consumer Contracts"
version: 4.0.0
status: NORMATIVE
authority_scope: >
  Client-side wire protocol consumption, NDJSON framing, command payloads,
  and RFC 8785 (JCS) cryptographic signing rules.
supersedes: none
superseded_by: none
budget_words: 2500
owners: [Tech Lead]
last_reviewed: 2026-08-17
---

# Vanguard v4.0 — Wire Protocol Consumer Contracts

> **Who this is for.** Client transport implementers consuming daemon event streams.

---

## 1. Frame Structure & Protocols

NDJSON over Unix domain socket. `version: "vg.4"`. Maximum frame size **1 MiB** (`MAX_FRAME_BYTES = 1024 * 1024`).

| `frameType` | Role |
|---|---|
| `command` | Client → daemon. Body: `command.{name,commandId,idempotencyKey,runId,actor,payload}` |
| `receipt` | Daemon → client. `receipt.{commandId,status,runId,result?\|detail?}` |
| `error` | Parse / frame-too-large / stream errors |
| `event` | Stream body; `event` is a VG-04 envelope |

**Command names in `RuntimeService`:** `StartRun`, `GetRun`, `StreamEvents`, `ResolveApproval`, `Cancel`, `Checkpoint`, `Resume`, `RecordCorrection`, `ExplainArtifact`.

---

## 2. Socket Path Resolution

1. `--socket-path` (CLI argument or GUI setting)
2. `VANGUARD_RUNTIME_SOCKET` environment variable
3. `/tmp/vanguard-runtime.sock` (Default fallback)

---

## 3. Cryptographic Canonicalisation (RFC 8785 JCS)

Canonicalisation applies strictly to **approval decision bytes**:
Sign `ApprovalDecision` fields derived from `ApprovalChallenge`: `approvalId`, `argsDigest`, `descriptorDigest`, `expiresAt`, `keyId`, `resolution`, `reviewer`. Use conformant RFC 8785 canonicalisation.
