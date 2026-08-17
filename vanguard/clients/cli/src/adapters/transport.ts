import { createConnection, type Socket } from "node:net";
import { createInterface } from "node:readline";
import { randomUUID } from "node:crypto";
import { fail, parseDaemonLine, parseJsonlLine } from "../contract/parse.js";
import type { EventCursor, Result, StreamItem } from "../contract/types.js";

export function resolveSocketPath(explicit?: string): string {
  return explicit || process.env.VANGUARD_RUNTIME_SOCKET || "/tmp/vanguard-runtime.sock";
}

export type SocketTransportOptions = {
  socketPath: string;
  connectTimeoutMs: number;
  commandTimeoutMs: number;
  maxReconnects: number;
  backoffMs: number;
};

export interface RuntimeTransport {
  readonly kind: "feed" | "socket";
  sendCommand<T>(name: string, payload: Record<string, unknown>, runId: string): Promise<Result<T>>;
  streamItems(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>>;
}

export class FeedTransport implements RuntimeTransport {
  readonly kind = "feed" as const;

  constructor(private readonly lines: AsyncIterable<string>) {}

  async sendCommand<T>(name: string, _payload: Record<string, unknown>, runId: string): Promise<Result<T>> {
    if (name === "StartRun") {
      return { ok: true, value: { runId, status: "started" } as T };
    }
    if (name === "GetRun") {
      return { ok: true, value: { status: "running" } as T };
    }
    if (name === "Cancel" || name === "Checkpoint" || name === "Resume" || name === "ResolveApproval" || name === "RecordCorrection") {
      return { ok: true, value: { status: "ok" } as T };
    }
    return fail("not_available", `${name} is not available on JSONL feed transport`, false);
  }

  async *streamItems(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    const afterSeq = cursor.afterSeq ? BigInt(cursor.afterSeq) : undefined;
    let lastSeenSeq = 0n;
    for await (const line of this.lines) {
      if (signal?.aborted) {
        yield fail("transport_interrupted", "live stream aborted", true);
        return;
      }
      const parsed = parseJsonlLine(line);
      if (!parsed.ok) {
        yield parsed;
        continue;
      }
      const seq = BigInt(parsed.value.seq);
      if (afterSeq !== undefined && seq <= afterSeq) continue;
      if (lastSeenSeq > 0n && seq <= lastSeenSeq) continue;
      lastSeenSeq = seq;
      yield { ok: true, value: { contractVersion: "0.1", source: "live", envelope: parsed.value } };
    }
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export class SocketTransport implements RuntimeTransport {
  readonly kind = "socket" as const;

  constructor(private readonly options: SocketTransportOptions) {}

  async sendCommand<T>(name: string, payload: Record<string, unknown>, runId: string): Promise<Result<T>> {
    return new Promise((resolve) => {
      let resolved = false;
      const socket = createConnection({ path: this.options.socketPath });

      const cleanup = () => {
        socket.removeAllListeners();
        socket.destroy();
      };

      const timer = setTimeout(() => {
        if (resolved) return;
        resolved = true;
        cleanup();
        resolve(fail("not_available", `RuntimeService daemon timed out at ${this.options.socketPath}`, true));
      }, this.options.commandTimeoutMs);

      socket.once("error", () => {
        if (resolved) return;
        resolved = true;
        clearTimeout(timer);
        cleanup();
        resolve(fail("not_available", `RuntimeService daemon unreachable at ${this.options.socketPath}`, true));
      });

      socket.once("connect", () => {
        const commandId = randomUUID();
        const commandFrame = {
          version: "vg.4",
          frameType: "command",
          frameId: randomUUID(),
          command: {
            name,
            commandId,
            idempotencyKey: commandId,
            runId,
            actor: "operator",
            payload,
          },
        };
        socket.write(JSON.stringify(commandFrame) + "\n");
        const rl = createInterface({ input: socket, crlfDelay: Infinity });
        rl.once("line", (line) => {
          if (resolved) return;
          resolved = true;
          clearTimeout(timer);
          cleanup();
          const frame = parseDaemonLine(line);
          if (!frame.ok) {
            resolve(frame);
            return;
          }
          if (frame.value.frameType === "error") {
            resolve(fail("invalid_request", frame.value.message, false));
            return;
          }
          if (frame.value.frameType !== "receipt") {
            resolve(fail("invalid_request", "invalid response frame from daemon", false));
            return;
          }
          const receipt = frame.value.receipt;
          if (receipt.status === "error") {
            resolve(fail("invalid_request", String(receipt.detail ?? "command failed"), false));
            return;
          }
          resolve({ ok: true, value: (receipt.result ?? receipt) as T });
        });
      });
    });
  }

  async *streamItems(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    let afterSeq = cursor.afterSeq ? BigInt(cursor.afterSeq) : undefined;
    let lastSeenSeq = 0n;
    let attempt = 0;

    while (true) {
      if (signal?.aborted) {
        yield fail("transport_interrupted", "stream aborted", true);
        return;
      }

      const outcome = await this.openStreamSocket();
      if (!outcome.ok) {
        attempt += 1;
        if (attempt > this.options.maxReconnects) {
          yield outcome;
          return;
        }
        yield fail("transport_interrupted", `reconnect ${attempt}/${this.options.maxReconnects}`, true);
        await sleep(this.options.backoffMs * attempt);
        continue;
      }

      const { socket } = outcome.value;
      const commandFrame = {
        version: "vg.4",
        frameType: "command",
        frameId: randomUUID(),
        command: {
          name: "StreamEvents",
          commandId: randomUUID(),
          idempotencyKey: randomUUID(),
          runId: cursor.runId,
          actor: "operator",
          payload: { afterSeq: afterSeq !== undefined ? Number(afterSeq) : 0 },
        },
      };
      socket.write(JSON.stringify(commandFrame) + "\n");
      const rl = createInterface({ input: socket, crlfDelay: Infinity });
      let disconnected = true;

      try {
        for await (const line of rl) {
          if (signal?.aborted) {
            yield fail("transport_interrupted", "stream aborted", true);
            return;
          }
          if (!line.trim()) continue;
          const frame = parseDaemonLine(line);
          if (!frame.ok) {
            yield frame;
            continue;
          }
          if (frame.value.frameType === "error") {
            yield fail("transport_interrupted", frame.value.message, true);
            break;
          }
          if (frame.value.frameType !== "event") continue;
          const envelope = frame.value.event;
          const seq = BigInt(envelope.seq);
          if (afterSeq !== undefined && seq <= afterSeq) continue;
          if (lastSeenSeq > 0n && seq <= lastSeenSeq) continue;
          lastSeenSeq = seq;
          afterSeq = seq;
          yield { ok: true, value: { contractVersion: "0.1", source: "live", envelope } };
        }
      } catch {
        disconnected = true;
      } finally {
        socket.removeAllListeners();
        socket.destroy();
      }

      if (signal?.aborted) return;
      if (!disconnected) return;
      attempt += 1;
      if (attempt > this.options.maxReconnects) {
        yield fail("transport_interrupted", "daemon connection closed unexpectedly", true);
        return;
      }
      await sleep(this.options.backoffMs * attempt);
    }
  }

  private openStreamSocket(): Promise<Result<{ socket: Socket }>> {
    return new Promise((resolve) => {
      let resolved = false;
      const socket = createConnection({ path: this.options.socketPath });
      const timer = setTimeout(() => {
        if (resolved) return;
        resolved = true;
        socket.destroy();
        resolve(fail("not_available", `RuntimeService daemon unreachable at ${this.options.socketPath}`, true));
      }, this.options.connectTimeoutMs);
      socket.once("connect", () => {
        if (resolved) return;
        resolved = true;
        clearTimeout(timer);
        resolve({ ok: true, value: { socket } });
      });
      socket.once("error", () => {
        if (resolved) return;
        resolved = true;
        clearTimeout(timer);
        socket.destroy();
        resolve(fail("not_available", `RuntimeService daemon unreachable at ${this.options.socketPath}`, true));
      });
    });
  }

  probe(): Promise<Result<{ socketPath: string }>> {
    return new Promise((resolve) => {
      let resolved = false;
      const socket = createConnection({ path: this.options.socketPath });
      const timer = setTimeout(() => {
        if (resolved) return;
        resolved = true;
        socket.removeAllListeners();
        socket.destroy();
        resolve(fail("not_available", `RuntimeService daemon not reachable at ${this.options.socketPath}`, true));
      }, this.options.connectTimeoutMs);
      socket.once("connect", () => {
        if (resolved) return;
        resolved = true;
        clearTimeout(timer);
        socket.removeAllListeners();
        socket.destroy();
        resolve({ ok: true, value: { socketPath: this.options.socketPath } });
      });
      socket.once("error", () => {
        if (resolved) return;
        resolved = true;
        clearTimeout(timer);
        socket.removeAllListeners();
        socket.destroy();
        resolve(fail("not_available", `RuntimeService daemon not reachable at ${this.options.socketPath}`, true));
      });
    });
  }
}
