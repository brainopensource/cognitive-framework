# Vanguard Wire Protocols, RPC & MCP Specification

**Document ID:** `VG-FE-003`  
**Version:** `0.4.1-beta`  
**Status:** `Normative / Authoritative`  
**Owner:** `Tech Lead & Systems Architect`  
**Related Specs:** [`04_vanguard_core_contracts_and_wire_schema_v040.md`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/04_vanguard_core_contracts_and_wire_schema_v040.md), [`ADR-0008`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/09_vanguard_decision_register_v040.md#L61), [`ADR-0062`](file:///home/rocha/Coding/Aether-D-System/docs/main_v4/09_vanguard_decision_register_v040.md#L181)

---

## 1. Protocol Architecture & Framing

All communication between the Frontend (CLI/TUI/IDE) and the Backend Runtime occurs over a line-delimited JSON (**NDJSON**) stream formatted in **UTF-8**.

Each message frame is a single JSON object terminated by a newline character (`\n` or `0x0A`).
* **Maximum Frame Size:** $4\text{ MB}$ ($4,194,304\text{ bytes}$). Payloads exceeding this limit must use external content-addressed blob references.
* **Canonical Encoding:** Payloads subject to cryptographic verification must be encoded in **RFC 8785 JSON Canonicalization Scheme (JCS)**.

---

## 2. Request & Response Envelope Format

### 2.1 Request Envelope (`Client -> Daemon`)
```json
{
  "jsonrpc": "2.0",
  "id": "req_01HPX94J7G2K1M4N",
  "method": "StartRun",
  "params": {
    "manifest_id": "vg-code-default",
    "prompt": "Fix unit test in test/kernel/test_dispatch.py",
    "cwd": "/workspace/project",
    "budget": {
      "max_tokens": 100000,
      "max_turns": 15
    }
  }
}
```

### 2.2 Response Envelope (`Daemon -> Client`)
```json
{
  "jsonrpc": "2.0",
  "id": "req_01HPX94J7G2K1M4N",
  "result": {
    "run_id": "run_01HPX94K9Z8Q3V1B",
    "status": "pending",
    "created_at": "2026-08-16T20:00:00Z"
  }
}
```

---

## 3. Core RPC Methods (Verbs)

| Method | Parameters | Return | Description |
| :--- | :--- | :--- | :--- |
| `StartRun` | `manifest_id`, `prompt`, `cwd`, `budget?`, `env?` | `{ run_id, status }` | Starts a new agentic run session |
| `GetRun` | `run_id` | Full Run State Object | Retrieves run summary, status, and spend |
| `StreamEvents` | `run_id`, `from_seq?` | Continuous NDJSON stream | Subscribes to the live event ledger for a run |
| `ResolveApproval` | `approval_id`, `verdict`, `signature`, `pubkey` | `{ acknowledged: true }` | Submits signed operator decision |
| `Cancel` | `run_id`, `reason?` | `{ cancelled: true }` | Safely aborts a run and reclaims sandbox |
| `Resume` | `run_id` | `{ resumed: true }` | Resumes an interrupted run from last checkpoint |
| `Ping` | `{}` | `{ pong: true, uptime, version }` | Transport liveness probe |

---

## 4. Ledger Event Stream Types (`Daemon -> Client`)

When subscribed via `StreamEvents`, the daemon streams structured events matching the following schema:

```typescript
export type LedgerEvent =
  | { seq: number; timestamp: string; kind: "run.started"; run_id: string; manifest: string }
  | { seq: number; timestamp: string; kind: "turn.started"; turn_index: number }
  | { seq: number; timestamp: string; kind: "stream.thinking"; delta: string }
  | { seq: number; timestamp: string; kind: "stream.token"; delta: string }
  | { seq: number; timestamp: string; kind: "tool.requested"; call_id: string; tool_name: string; args: Record<string, unknown> }
  | { seq: number; timestamp: string; kind: "approval.requested"; approval_id: string; descriptor: ApprovalDescriptor }
  | { seq: number; timestamp: string; kind: "approval.resolved"; approval_id: string; verdict: "allow" | "deny" }
  | { seq: number; timestamp: string; kind: "tool.completed"; call_id: string; tool_name: string; result: string; exit_code: number }
  | { seq: number; timestamp: string; kind: "turn.completed"; turn_index: number; tokens_used: number; cost_usd: number }
  | { seq: number; timestamp: string; kind: "run.completed"; exit_status: "success" | "budget_exhausted" | "cancelled" }
  | { seq: number; timestamp: string; kind: "run.failed"; error_code: string; message: string };
```

---

## 5. Asymmetric Ed25519 Operator Approval Specification

To fulfill **`ADR-0062`** and **`REQ-APP-001`**, approval resolution requires cryptographic operator authority outside the runtime memory space.

### 5.1 Approval Request Descriptor Format
When an agent requests a capability requiring approval (e.g., destructive bash command, root filesystem write, external network access), the daemon emits `approval.requested`:

```json
{
  "approval_id": "appr_01HPX98C7B",
  "run_id": "run_01HPX94K9Z8Q3V1B",
  "capability": "proc.exec",
  "action_descriptor": {
    "command": "rm -rf /workspace/temp_build",
    "cwd": "/workspace",
    "risk_level": "high"
  },
  "nonce": "a7f9c2e1b4d83015",
  "expires_at": "2026-08-16T20:15:00Z"
}
```

### 5.2 Canonical Signing Flow in TypeScript
```typescript
import * as crypto from "node:crypto";
import canonicalize from "canonicalize"; // RFC 8785 JCS

export interface SignedApprovalPayload {
  approval_id: string;
  verdict: "allow" | "deny";
  operator_pubkey: string; // Hex-encoded Ed25519 public key
  signature: string;       // Hex-encoded Ed25519 signature
}

export function signApproval(
  descriptor: Record<string, unknown>,
  verdict: "allow" | "deny",
  privateKeyPem: string
): SignedApprovalPayload {
  // 1. Construct canonical data object
  const envelope = {
    approval_id: descriptor.approval_id,
    action_descriptor: descriptor.action_descriptor,
    nonce: descriptor.nonce,
    verdict: verdict
  };

  // 2. Compute deterministic RFC 8785 bytes
  const canonicalBytes = Buffer.from(canonicalize(envelope)!, "utf8");

  // 3. Sign using Ed25519 Private Key
  const signature = crypto.sign(null, canonicalBytes, privateKeyPem);

  // 4. Extract public key
  const pubKey = crypto.createPublicKey(privateKeyPem).export({ type: "spki", format: "der" });

  return {
    approval_id: descriptor.approval_id as string,
    verdict: verdict,
    operator_pubkey: pubKey.toString("hex"),
    signature: signature.toString("hex")
  };
}
```

---

## 6. Model Context Protocol (MCP) Bridge

Vanguard supports standard Model Context Protocol (MCP) servers (Stdio, SSE) to dynamically expose external tools to the Python kernel without compromising TCB isolation.

```
┌─────────────────┐       Stdio / JSON-RPC       ┌────────────────────────┐
│  Vanguard Core  │ ◄──────────────────────────► │ External MCP Server    │
│  (Python Kernel)│   (MCP tools/list, call)     │ (e.g. Postgres, Brave) │
└─────────────────┘                              └────────────────────────┘
```

1. **Discovery:** On session startup, the client or runtime loads active MCP servers configured in `~/.vanguard/mcp.json`.
2. **Attenuation:** Each discovered MCP tool is assigned a capability grant policy in the kernel. By default, write/destructive MCP tools require an interactive operator signature.
