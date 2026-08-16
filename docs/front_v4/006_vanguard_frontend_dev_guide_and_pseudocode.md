# Vanguard Frontend Developer Implementation Guide & Pseudocode

**Document ID:** `VG-FE-006`  
**Version:** `0.4.1-beta`  
**Status:** `Normative / Authoritative`  
**Owner:** `Lead Software Engineer & Frontend Core Team`  
**Target:** `vanguard/clients/cli/src/`

---

## 1. Socket Client & Reconnection Engine (`adapters/live.ts`)

The `LiveDaemonClient` maintains a resilient Unix Domain Socket (UDS) connection to the Python `RuntimeService` daemon with framed NDJSON line parsing and automatic exponential backoff.

### Complete Reference Implementation Pseudocode
```typescript
import * as net from "node:net";
import * as fs from "node:fs";
import { EventEmitter } from "node:events";
import { LedgerEvent } from "../contract/wire";

export interface DaemonConfig {
  socketPath: string;
  autoReconnect?: boolean;
  maxRetries?: number;
}

export class LiveDaemonClient extends EventEmitter {
  private socket: net.Socket | null = null;
  private buffer: string = "";
  private retryCount: number = 0;
  private pendingRequests: Map<string, { resolve: Function; reject: Function }> = new Map();

  constructor(private config: DaemonConfig) {
    super();
  }

  public async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket = net.createConnection({ path: this.config.socketPath }, () => {
        this.retryCount = 0;
        this.emit("connected");
        resolve();
      });

      this.socket.setEncoding("utf8");

      this.socket.on("data", (chunk: string) => {
        this.handleData(chunk);
      });

      this.socket.on("error", (err) => {
        this.emit("error", err);
        if (this.retryCount === 0) reject(err);
      });

      this.socket.on("close", () => {
        this.emit("disconnected");
        this.scheduleReconnect();
      });
    });
  }

  private handleData(chunk: string): void {
    this.buffer += chunk;
    const lines = this.buffer.split("\n");
    // Keep the remainder in buffer
    this.buffer = lines.pop() || "";

    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const message = JSON.parse(line);
        if (message.id && this.pendingRequests.has(message.id)) {
          const handler = this.pendingRequests.get(message.id)!;
          this.pendingRequests.delete(message.id);
          if (message.error) {
            handler.reject(new Error(message.error.message));
          } else {
            handler.resolve(message.result);
          }
        } else if (message.kind) {
          // It is a streaming ledger event
          this.emit("event", message as LedgerEvent);
        }
      } catch (err) {
        console.error("Malformed NDJSON frame:", line, err);
      }
    }
  }

  public async callRPC<T>(method: string, params: Record<string, unknown>): Promise<T> {
    if (!this.socket || this.socket.destroyed) {
      throw new Error("Cannot call RPC: Socket is not connected");
    }

    const id = `req_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;
    const payload = JSON.stringify({ jsonrpc: "2.0", id, method, params }) + "\n";

    return new Promise<T>((resolve, reject) => {
      this.pendingRequests.set(id, { resolve, reject });
      this.socket!.write(payload, "utf8");
    });
  }

  private scheduleReconnect(): void {
    if (!this.config.autoReconnect) return;
    const delay = Math.min(100 * Math.pow(1.5, this.retryCount), 5000);
    this.retryCount++;
    setTimeout(() => {
      this.connect().catch(() => {});
    }, delay);
  }
}
```

---

## 2. Operator Signer Module (`adapters/signer.ts`)

Implements RFC 8785 canonical bytes hashing and Ed25519 asymmetric signature generation.

```typescript
import * as crypto from "node:crypto";
import * as fs from "node:fs";
import canonicalize from "canonicalize";

export class OperatorSigner {
  private privateKeyPem: string;
  public readonly publicKeyDerHex: string;

  constructor(keyPath: string) {
    if (!fs.existsSync(keyPath)) {
      // Auto-generate keypair if not existing (0600 mode)
      const { publicKey, privateKey } = crypto.generateKeyPairSync("ed25519");
      this.privateKeyPem = privateKey.export({ type: "pkcs8", format: "pem" }) as string;
      fs.mkdirSync(require("path").dirname(keyPath), { recursive: true });
      fs.writeFileSync(keyPath, this.privateKeyPem, { mode: 0o600 });
      this.publicKeyDerHex = (publicKey.export({ type: "spki", format: "der" }) as Buffer).toString("hex");
    } else {
      this.privateKeyPem = fs.readFileSync(keyPath, "utf8");
      const pubKey = crypto.createPublicKey(this.privateKeyPem);
      this.publicKeyDerHex = (pubKey.export({ type: "spki", format: "der" }) as Buffer).toString("hex");
    }
  }

  public signApproval(approvalId: string, actionDescriptor: unknown, nonce: string, verdict: "allow" | "deny") {
    const payloadToCanonicalize = {
      approval_id: approvalId,
      action_descriptor: actionDescriptor,
      nonce: nonce,
      verdict: verdict,
    };

    const canonicalString = canonicalize(payloadToCanonicalize);
    if (!canonicalString) throw new Error("Failed to canonicalize approval descriptor");

    const dataBuffer = Buffer.from(canonicalString, "utf8");
    const signature = crypto.sign(null, dataBuffer, this.privateKeyPem);

    return {
      approval_id: approvalId,
      verdict: verdict,
      operator_pubkey: this.publicKeyDerHex,
      signature: signature.toString("hex"),
    };
  }
}
```

---

## 3. Custom React Hook: `useVanguardRun`

Connects the UI state with live streaming events and interactive approval requests.

```typescript
import { useState, useEffect, useCallback, useRef } from "react";
import { LiveDaemonClient } from "../adapters/live";
import { OperatorSigner } from "../adapters/signer";
import { LedgerEvent } from "../contract/wire";

export function useVanguardRun(client: LiveDaemonClient, signer: OperatorSigner) {
  const [events, setEvents] = useState<LedgerEvent[]>([]);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);
  const [status, setStatus] = useState<"idle" | "running" | "waiting_approval" | "completed" | "error">("idle");
  const [pendingApproval, setPendingApproval] = useState<any | null>(null);
  const [tokenStream, setTokenStream] = useState<string>("");
  const [thinkingStream, setThinkingStream] = useState<string>("");

  useEffect(() => {
    const onEvent = (event: LedgerEvent) => {
      setEvents((prev) => [...prev.slice(-4999), event]); // Bounded 5000 items

      switch (event.kind) {
        case "run.started":
          setActiveRunId(event.run_id);
          setStatus("running");
          break;
        case "stream.thinking":
          setThinkingStream((prev) => prev + event.delta);
          break;
        case "stream.token":
          setTokenStream((prev) => prev + event.delta);
          break;
        case "approval.requested":
          setStatus("waiting_approval");
          setPendingApproval(event);
          break;
        case "approval.resolved":
          setPendingApproval(null);
          setStatus("running");
          break;
        case "run.completed":
          setStatus("completed");
          break;
        case "run.failed":
          setStatus("error");
          break;
      }
    };

    client.on("event", onEvent);
    return () => {
      client.off("event", onEvent);
    };
  }, [client]);

  const startRun = useCallback(async (manifestId: string, prompt: string, cwd: string) => {
    setEvents([]);
    setTokenStream("");
    setThinkingStream("");
    setStatus("running");
    const res = await client.callRPC<{ run_id: string }>("StartRun", {
      manifest_id: manifestId,
      prompt,
      cwd
    });
    setActiveRunId(res.run_id);
    await client.callRPC("StreamEvents", { run_id: res.run_id });
  }, [client]);

  const resolveApproval = useCallback(async (verdict: "allow" | "deny") => {
    if (!pendingApproval) return;
    const signedPayload = signer.signApproval(
      pendingApproval.approval_id,
      pendingApproval.descriptor.action_descriptor,
      pendingApproval.descriptor.nonce,
      verdict
    );
    await client.callRPC("ResolveApproval", signedPayload);
  }, [client, signer, pendingApproval]);

  return {
    status,
    activeRunId,
    events,
    tokenStream,
    thinkingStream,
    pendingApproval,
    startRun,
    resolveApproval,
  };
}
```
