// FE-B5: LiveRuntimeClient — vg.4 NDJSON over UDS; same wire as CLI.
// Ported from vanguard/clients/cli/src/adapters/live.ts (FE-A owns original).
// Socket path resolution: --socket-path → VANGUARD_RUNTIME_SOCKET → /tmp/vanguard-runtime.sock

import { createConnection } from "node:net";
import { createInterface } from "node:readline";
import { randomUUID } from "node:crypto";
import { fail, parseJsonlLine } from "../contract/parse";
import type {
  ArtifactExplanation,
  CommandReceipt,
  CorrectionRecord,
  DaemonStatus,
  EventCursor,
  Result,
  ResumeRunRequest,
  ResolveApprovalRequest,
  RunRef,
  RunSnapshot,
  RuntimeClient,
  StartRunRequest,
  StreamItem,
} from "../contract/types";

export type LiveClientOptions = {
  repo?: string;
  brief?: string;
  manifest?: string;
  runId?: string;
  socketPath?: string;
  autoApprove?: boolean;
};

/** Resolve socket path: setting → env → default (D1, docs/front_v4/003_wire_consumer.md §Socket path resolution) */
export function resolveSocketPath(socketPathSetting?: string): string {
  if (socketPathSetting && socketPathSetting.trim()) return socketPathSetting.trim();
  const env = process.env["VANGUARD_RUNTIME_SOCKET"];
  if (env && env.trim()) return env.trim();
  return "/tmp/vanguard-runtime.sock";
}

export class LiveRuntimeClient implements RuntimeClient {
  private readonly options: LiveClientOptions;
  private currentRunId: string;
  private currentEpisodeId: string;
  private lastSeenSeq: bigint = 0n;
  private status: string = "pending";
  private readonly socketPath: string;
  private readonly boundedBuffer: StreamItem[] = [];
  private static readonly MAX_BUFFER_SIZE = 10_000;
  private readonly corrections: CorrectionRecord[] = [];

  constructor(options: LiveClientOptions = {}) {
    this.options = options;
    this.currentRunId = options.runId ?? `run-${Date.now()}`;
    this.currentEpisodeId = `episode-${Date.now()}`;
    this.socketPath = resolveSocketPath(options.socketPath);
  }

  private async sendCommand<T = Record<string, unknown>>(
    name: string,
    payload: Record<string, unknown>,
    runId: string
  ): Promise<Result<T>> {
    return new Promise((resolve) => {
      let resolved = false;
      const socket = createConnection({ path: this.socketPath });

      const cleanup = () => {
        socket.removeAllListeners();
        socket.destroy();
      };

      const timer = setTimeout(() => {
        if (resolved) return;
        resolved = true;
        cleanup();
        resolve(fail("not_available", `RuntimeService daemon timed out at ${this.socketPath}`, true));
      }, 500);

      socket.once("error", () => {
        if (resolved) return;
        resolved = true;
        clearTimeout(timer);
        cleanup();
        resolve(fail("not_available", `RuntimeService daemon unreachable at ${this.socketPath}`, true));
      });

      socket.once("connect", () => {
        const commandId = randomUUID();
        const frameId = randomUUID();
        const commandFrame = {
          version: "vg.4",
          frameType: "command",
          frameId,
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
          try {
            const resp = JSON.parse(line);
            if (resp.frameType === "error") {
              resolve(fail("invalid_request", resp.error?.message ?? "command failed", false));
              return;
            }
            const receipt = resp.receipt;
            if (!receipt) {
              resolve(fail("invalid_request", "invalid response frame from daemon", false));
              return;
            }
            if (receipt.status === "error") {
              resolve(fail("invalid_request", receipt.detail ?? "command failed", false));
              return;
            }
            resolve({ ok: true, value: (receipt.result ?? receipt) as T });
          } catch (exc) {
            resolve(fail("transport_interrupted", `failed to parse daemon response: ${exc}`, true));
          }
        });
      });
    });
  }

  async startRun(request: StartRunRequest, _signal?: AbortSignal): Promise<Result<RunRef>> {
    const runId = request.runId ?? this.currentRunId;
    const res = await this.sendCommand<{ runId: string }>(
      "StartRun",
      {
        manifestPath: request.manifest ?? this.options.manifest ?? "manifest.json",
        repoPath: request.repo ?? this.options.repo ?? ".",
        brief: request.brief ?? request.prompt ?? this.options.brief ?? "run",
      },
      runId
    );
    if (!res.ok) return res;
    this.currentRunId = res.value.runId;
    this.status = "running";
    return {
      ok: true,
      value: { runId: this.currentRunId, episodeId: this.currentEpisodeId },
    };
  }

  async *streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    const afterSeq = cursor.afterSeq ? BigInt(cursor.afterSeq) : undefined;
    const socket = createConnection({ path: this.socketPath });

    try {
      await new Promise<void>((resolve, reject) => {
        socket.once("connect", () => resolve());
        socket.once("error", (err) => reject(err));
      });
    } catch {
      yield fail("not_available", `RuntimeService daemon unreachable at ${this.socketPath}`, true);
      return;
    }

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
        payload: { afterSeq: cursor.afterSeq ? parseInt(cursor.afterSeq, 10) : 0 },
      },
    };

    socket.write(JSON.stringify(commandFrame) + "\n");
    const rl = createInterface({ input: socket, crlfDelay: Infinity });

    try {
      for await (const line of rl) {
        if (signal?.aborted) {
          yield fail("transport_interrupted", "stream aborted", true);
          return;
        }
        if (!line.trim()) continue;

        let frame: Record<string, unknown>;
        try {
          frame = JSON.parse(line) as Record<string, unknown>;
        } catch (exc) {
          yield fail("transport_interrupted", `malformed json frame: ${exc}`, true);
          continue;
        }

        if (frame["frameType"] === "error") {
          const errFrame = frame["error"] as Record<string, unknown> | undefined;
          yield fail("transport_interrupted", (errFrame?.["message"] as string) ?? "stream error", true);
          return;
        }

        if (frame["frameType"] === "event" && frame["event"]) {
          const parsed = parseJsonlLine(JSON.stringify(frame["event"]));
          if (!parsed.ok) { yield parsed; continue; }
          const seq = BigInt(parsed.value.seq);
          if (afterSeq !== undefined && seq <= afterSeq) continue;
          if (this.lastSeenSeq > 0n && seq <= this.lastSeenSeq) continue;
          this.lastSeenSeq = seq;

          const item: StreamItem = { contractVersion: "0.1", source: "live", envelope: parsed.value };
          if (this.boundedBuffer.length >= LiveRuntimeClient.MAX_BUFFER_SIZE) this.boundedBuffer.shift();
          this.boundedBuffer.push(item);
          yield { ok: true, value: item };
        }
      }
      this.status = "completed";
    } catch {
      yield fail("transport_interrupted", "daemon connection closed unexpectedly", true);
    } finally {
      socket.removeAllListeners();
      socket.destroy();
    }
  }

  async getRun(runId: string): Promise<Result<RunSnapshot>> {
    const res = await this.sendCommand<{ status: string }>("GetRun", {}, runId);
    if (!res.ok) return res;
    return { ok: true, value: { runId, status: res.value.status, seq: this.lastSeenSeq.toString() } };
  }

  async requestCancel(runId: string): Promise<Result<CommandReceipt>> {
    const res = await this.sendCommand<{ status: string }>("Cancel", {}, runId);
    if (!res.ok) return res;
    this.status = "cancelled";
    return { ok: true, value: { runId, command: "cancel", status: "accepted" } };
  }

  async requestCheckpoint(runId: string): Promise<Result<CommandReceipt>> {
    const res = await this.sendCommand<{ status: string }>("Checkpoint", {}, runId);
    if (!res.ok) return res;
    return { ok: true, value: { runId, command: "checkpoint", status: "accepted" } };
  }

  async requestResume(request: ResumeRunRequest): Promise<Result<RunRef>> {
    const res = await this.sendCommand<{ status: string }>("Resume", {}, request.runId);
    if (!res.ok) return res;
    return { ok: true, value: { runId: request.runId } };
  }

  async explainArtifact(artifactId: string): Promise<Result<ArtifactExplanation>> {
    const res = await this.sendCommand<{ explanation?: string }>("ExplainArtifact", { artifactId }, this.currentRunId);
    if (!res.ok) return res;
    return {
      ok: true,
      value: {
        artifactId,
        status: "active",
        prediction: res.value.explanation ?? `Live artifact ${artifactId} active under RuntimeService`,
        activatedBy: [{ evidence: `live stream seq=${this.lastSeenSeq}`, strength: 1.0 }],
        demotedBy: [],
        freshness: { source: "live", asOfSeq: this.lastSeenSeq.toString() },
      },
    };
  }

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<CommandReceipt>> {
    const res = await this.sendCommand<{ status: string }>(
      "ResolveApproval",
      {
        decision: {
          approvalId: request.approvalId,
          resolution: request.decision === "approve" ? "approved" : "rejected",
          reviewer: "operator",
          argsDigest: "",
          descriptorDigest: "",
          expiresAt: "",
          signature: request.signature ?? "",
        },
      },
      this.currentRunId
    );
    if (!res.ok) return res;
    return { ok: true, value: { runId: this.currentRunId, command: "resolve_approval", status: "accepted" } };
  }

  async recordCorrection(record: CorrectionRecord): Promise<Result<CommandReceipt>> {
    const res = await this.sendCommand<{ status: string }>("RecordCorrection", { correction: record }, this.currentRunId);
    if (!res.ok) return res;
    this.corrections.push(record);
    return { ok: true, value: { runId: this.currentRunId, command: "record_correction", status: "accepted" } };
  }

  async getDaemonStatus(_signal?: AbortSignal): Promise<Result<DaemonStatus>> {
    return new Promise((resolve) => {
      let resolved = false;
      const socket = createConnection({ path: this.socketPath });
      const timer = setTimeout(() => {
        if (resolved) return;
        resolved = true;
        socket.removeAllListeners();
        socket.destroy();
        resolve(fail("not_available", `RuntimeService daemon not reachable at ${this.socketPath}`, true));
      }, 300);
      socket.once("connect", () => {
        if (resolved) return;
        resolved = true;
        clearTimeout(timer);
        socket.removeAllListeners();
        socket.destroy();
        resolve({ ok: true, value: { status: "running", socketPath: this.socketPath, version: "0.4.0" } });
      });
      socket.once("error", () => {
        if (resolved) return;
        resolved = true;
        clearTimeout(timer);
        socket.removeAllListeners();
        socket.destroy();
        resolve(fail("not_available", `RuntimeService daemon not reachable at ${this.socketPath}`, true));
      });
    });
  }
}
