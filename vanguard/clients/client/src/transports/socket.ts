import { createConnection, type Socket } from "node:net";
import { createInterface } from "node:readline";
import { randomUUID } from "node:crypto";
import {
  fail,
  parseDaemonLine,
  toClientFailureCode,
  type ApprovalChallenge,
  type ApprovalDecision,
  type ArtifactExplanation,
  type CancelOptions,
  type CheckpointOptions,
  type CommandReceipt,
  type CorrectionRecord,
  type DaemonStatus,
  type EventCursor,
  type ExplainArtifactOptions,
  type ListRunsOptions,
  type RecordCorrectionRequest,
  type ResolveApprovalRequest,
  type Result,
  type ResumeOptions,
  type RunRef,
  type RunSnapshot,
  type RunSummary,
  type SignerPort,
  type StartRunRequest,
  type StreamItem,
} from "@aether/contracts";
import type { RuntimeClient } from "../client.js";
import { resolveSocketPath, type RuntimeTransport } from "./transport.js";

export type SocketTransportOptions = {
  socketPath?: string;
  connectTimeoutMs?: number;
  commandTimeoutMs?: number;
  maxReconnects?: number;
  backoffMs?: number;
  signer?: SignerPort;
};

function challengeFromPayload(payload: Record<string, unknown>): ApprovalChallenge | undefined {
  const approvalId = payload.approvalId;
  if (typeof approvalId !== "string") return undefined;
  return {
    approvalId,
    processId: String(payload.processId ?? ""),
    action: String(payload.action ?? ""),
    normalizedDiff: String(payload.normalizedDiff ?? payload.unifiedDiff ?? payload.diff ?? ""),
    argsDigest: typeof payload.argsDigest === "string" ? payload.argsDigest : "",
    descriptorDigest: typeof payload.descriptorDigest === "string" ? payload.descriptorDigest : "",
    principal: String(payload.principal ?? "operator"),
    expiresAt: typeof payload.expiresAt === "string" ? payload.expiresAt : "",
  };
}

export class SocketTransport implements RuntimeTransport {
  readonly kind = "socket" as const;
  private readonly socketPath: string;
  private readonly connectTimeoutMs: number;
  private readonly commandTimeoutMs: number;
  private readonly maxReconnects: number;
  private readonly backoffMs: number;

  constructor(options: SocketTransportOptions = {}) {
    this.socketPath = resolveSocketPath(options.socketPath);
    this.connectTimeoutMs = options.connectTimeoutMs ?? 300;
    this.commandTimeoutMs = options.commandTimeoutMs ?? 500;
    this.maxReconnects = options.maxReconnects ?? 3;
    this.backoffMs = options.backoffMs ?? 50;
  }

  get path(): string {
    return this.socketPath;
  }

  async probe(): Promise<Result<{ status: "running"; socketPath: string }>> {
    return new Promise((resolve) => {
      let settled = false;
      const socket = createConnection({ path: this.socketPath });
      const cleanup = () => {
        socket.removeAllListeners();
        socket.destroy();
      };
      const timer = setTimeout(() => {
        if (settled) return;
        settled = true;
        cleanup();
        resolve(fail("not_available", `Socket probe timed out at ${this.socketPath}`, true));
      }, this.connectTimeoutMs);

      socket.once("error", (err) => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        cleanup();
        resolve(fail("not_available", `Socket probe failed at ${this.socketPath}: ${err.message}`, true));
      });

      socket.once("connect", () => {
        if (settled) return;
        settled = true;
        clearTimeout(timer);
        cleanup();
        resolve({ ok: true, value: { status: "running", socketPath: this.socketPath } });
      });
    });
  }

  async sendCommand<T>(
    name: string,
    payload: Record<string, unknown>,
    runId: string,
    actor: string = "operator"
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
        resolve(fail("not_available", `RuntimeService timed out at ${this.socketPath}`, true));
      }, this.commandTimeoutMs);

      socket.once("error", (err) => {
        if (resolved) return;
        resolved = true;
        clearTimeout(timer);
        cleanup();
        resolve(fail("not_available", `RuntimeService unreachable at ${this.socketPath}: ${err.message}`, true));
      });

      socket.once("connect", () => {
        const commandId = randomUUID();
        const frame = {
          version: "vg.4",
          frameType: "command",
          frameId: randomUUID(),
          command: {
            name,
            commandId,
            idempotencyKey: randomUUID(),
            runId: runId || undefined,
            actor,
            payload,
          },
        };

        const rl = createInterface({ input: socket, crlfDelay: Infinity });
        rl.on("line", (line) => {
          if (resolved) return;
          const parsed = parseDaemonLine(line);
          if (!parsed.ok) {
            resolved = true;
            clearTimeout(timer);
            cleanup();
            resolve(parsed as Result<T>);
            return;
          }
          const f = parsed.value;
          if (f.frameType === "error") {
            resolved = true;
            clearTimeout(timer);
            cleanup();
            resolve(fail(toClientFailureCode(f.error.code), f.error.message, f.error.retryable, { ...f.error }));
            return;
          }
          if (f.frameType === "receipt") {
            resolved = true;
            clearTimeout(timer);
            cleanup();
            if (f.receipt.status === "error" && f.receipt.error) {
              const code = toClientFailureCode(f.receipt.error.code);
              resolve(fail(code, f.receipt.error.message, f.receipt.error.retryable, { ...f.receipt.error }));
              return;
            }
            resolve({ ok: true, value: (f.receipt.result ?? f.receipt) as T });
            return;
          }
        });

        socket.write(JSON.stringify(frame) + "\n");
      });
    });
  }

  async *streamItems(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    let afterSeq = cursor.afterSeq ? BigInt(cursor.afterSeq) : undefined;
    let lastSeenSeq = afterSeq ?? 0n;
    let reconnectAttempts = 0;

    while (true) {
      if (signal?.aborted) {
        yield fail("transport_interrupted", "Stream aborted by caller", true);
        return;
      }

      let socket: Socket | undefined;
      let connected = false;

      try {
        socket = await new Promise<Socket>((resolve, reject) => {
          const s = createConnection({ path: this.socketPath });
          const timeout = setTimeout(() => {
            s.destroy();
            reject(new Error("Connection timeout"));
          }, this.connectTimeoutMs);

          s.once("connect", () => {
            clearTimeout(timeout);
            resolve(s);
          });
          s.once("error", (err) => {
            clearTimeout(timeout);
            reject(err);
          });
        });

        connected = true;
        reconnectAttempts = 0;

        const streamCmd = {
          version: "vg.4",
          frameType: "command",
          frameId: randomUUID(),
          command: {
            name: "StreamEvents",
            commandId: randomUUID(),
            idempotencyKey: randomUUID(),
            runId: cursor.runId,
            actor: "operator",
            payload: lastSeenSeq > 0n ? { afterSeq: lastSeenSeq.toString() } : {},
          },
        };

        socket.write(JSON.stringify(streamCmd) + "\n");

        const rl = createInterface({ input: socket, crlfDelay: Infinity });

        for await (const line of rl) {
          if (signal?.aborted) {
            socket.destroy();
            yield fail("transport_interrupted", "Stream aborted by caller", true);
            return;
          }
          const parsed = parseDaemonLine(line);
          if (!parsed.ok) {
            yield parsed;
            continue;
          }
          const frame = parsed.value;
          if (frame.frameType === "error") {
            const code = toClientFailureCode(frame.error.code);
            yield fail(code, frame.error.message, frame.error.retryable);
            return;
          }
          if (frame.frameType === "event") {
            const env = frame.event;
            const seq = BigInt(env.seq);
            if (lastSeenSeq > 0n && seq <= lastSeenSeq) {
              continue;
            }
            lastSeenSeq = seq;
            yield {
              ok: true,
              value: {
                contractVersion: "vg.4",
                source: "live",
                envelope: env,
              },
            };
          }
        }
      } catch (err) {
        if (connected) {
          // Dropped mid-stream
        }
        reconnectAttempts++;
        if (reconnectAttempts > this.maxReconnects || signal?.aborted) {
          yield fail(
            "not_available",
            `RuntimeService stream connection failed after ${reconnectAttempts} attempts: ${String(err)}`,
            true
          );
          return;
        }
        await new Promise((r) => setTimeout(r, this.backoffMs * Math.pow(2, reconnectAttempts - 1)));
      } finally {
        if (socket) {
          socket.removeAllListeners();
          socket.destroy();
        }
      }
    }
  }
}

export class SocketRuntimeClient implements RuntimeClient {
  private readonly transport: SocketTransport;
  private readonly signer: SignerPort | undefined;
  private currentRunId: string = "";
  private lastChallenge: ApprovalChallenge | undefined;

  constructor(options: SocketTransportOptions = {}) {
    this.transport = new SocketTransport(options);
    this.signer = options.signer;
  }

  async startRun(request: StartRunRequest, _signal?: AbortSignal): Promise<Result<RunRef>> {
    const runId = request.runId ?? `run-${Date.now()}`;
    this.currentRunId = runId;
    const payload: Record<string, unknown> = {
      manifestPath: request.manifestPath ?? request.repo ?? request.repoPath ?? ".",
      repoPath: request.repoPath ?? request.repo ?? ".",
      brief: request.brief ?? request.prompt ?? "Execute task",
    };
    if (request.profileId || request.profile) payload.profileId = request.profileId ?? request.profile;
    if (request.model) payload.model = request.model;
    if (request.episodeId) payload.episodeId = request.episodeId;
    if (request.expectedSeq !== undefined) payload.expectedSeq = String(request.expectedSeq);

    const res = await this.transport.sendCommand<{ runId?: string; episodeId?: string }>(
      "StartRun",
      payload,
      runId
    );
    if (!res.ok) return res;
    return {
      ok: true,
      value: {
        runId: res.value.runId ?? runId,
        episodeId: res.value.episodeId,
      },
    };
  }

  async getRun(runId: string, expectedSeq?: string | number): Promise<Result<RunSnapshot>> {
    const payload: Record<string, unknown> = {};
    if (expectedSeq !== undefined) payload.expectedSeq = String(expectedSeq);
    const res = await this.transport.sendCommand<{
      runId?: string;
      status?: string;
      seq?: string;
      verdict?: string;
      metrics?: Record<string, unknown>;
    }>("GetRun", payload, runId);
    if (!res.ok) return res;
    return {
      ok: true,
      value: {
        runId: res.value.runId ?? runId,
        status: res.value.status ?? "running",
        seq: String(res.value.seq ?? "0"),
        verdict: res.value.verdict,
        metrics: res.value.metrics,
      },
    };
  }

  async listRuns(options: ListRunsOptions = {}): Promise<Result<RunSummary[]>> {
    const payload: Record<string, unknown> = {};
    if (options.limit !== undefined) payload.limit = options.limit;
    if (options.offset !== undefined) payload.offset = options.offset;
    const res = await this.transport.sendCommand<{ runs?: RunSummary[] }>("ListRuns", payload, "");
    if (!res.ok) return res;
    return {
      ok: true,
      value: Array.isArray(res.value.runs) ? res.value.runs : [],
    };
  }

  async *streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    for await (const item of this.transport.streamItems(cursor, signal)) {
      if (item.ok) {
        const env = item.value.envelope;
        if (env.payload.kind === "ApprovalRequested") {
          const ch = challengeFromPayload(env.payload);
          if (ch) this.lastChallenge = ch;
        }
      }
      yield item;
    }
  }

  async requestCancel(runId: string, options: CancelOptions = {}): Promise<Result<CommandReceipt>> {
    const payload: Record<string, unknown> = {};
    if (options.reason) payload.reason = options.reason;
    if (options.expectedSeq !== undefined) payload.expectedSeq = String(options.expectedSeq);
    return this.transport.sendCommand<CommandReceipt>("Cancel", payload, runId);
  }

  async requestCheckpoint(runId: string, options: CheckpointOptions = {}): Promise<Result<CommandReceipt>> {
    const payload: Record<string, unknown> = {};
    if (options.reason) payload.reason = options.reason;
    if (options.expectedSeq !== undefined) payload.expectedSeq = String(options.expectedSeq);
    return this.transport.sendCommand<CommandReceipt>("Checkpoint", payload, runId);
  }

  async requestResume(runId: string, options: ResumeOptions = {}): Promise<Result<CommandReceipt>> {
    const payload: Record<string, unknown> = {};
    if (options.checkpointId) payload.checkpointId = options.checkpointId;
    if (options.expectedSeq !== undefined) payload.expectedSeq = String(options.expectedSeq);
    return this.transport.sendCommand<CommandReceipt>("Resume", payload, runId);
  }

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<CommandReceipt>> {
    let decision: ApprovalDecision;
    if (typeof request.decision === "object") {
      decision = request.decision;
    } else {
      if (!this.lastChallenge) {
        return fail("invalid_request", "No pending approval challenge cached for signing");
      }
      if (!this.signer) {
        return fail("permission_denied", "No signer configured to resolve approval");
      }
      const resolution = request.decision === "reject" ? "rejected" : "approved";
      decision = await this.signer.signChallenge(this.lastChallenge, resolution);
    }

    const payload: Record<string, unknown> = { decision };
    if (request.expectedSeq !== undefined) payload.expectedSeq = String(request.expectedSeq);
    return this.transport.sendCommand<CommandReceipt>(
      "ResolveApproval",
      payload,
      this.currentRunId || (request.approvalId ?? "")
    );
  }

  async recordCorrection(request: RecordCorrectionRequest): Promise<Result<CommandReceipt>> {
    const payload: Record<string, unknown> = { correction: request.correction };
    if (request.expectedSeq !== undefined) payload.expectedSeq = String(request.expectedSeq);
    return this.transport.sendCommand<CommandReceipt>(
      "RecordCorrection",
      payload,
      request.correction.runId || this.currentRunId
    );
  }

  async explainArtifact(artifactId: string, options: ExplainArtifactOptions = {}): Promise<Result<ArtifactExplanation>> {
    const payload: Record<string, unknown> = { artifactId };
    if (options.substrateProfile) payload.substrateProfile = options.substrateProfile;
    if (options.expectedSeq !== undefined) payload.expectedSeq = String(options.expectedSeq);
    return this.transport.sendCommand<ArtifactExplanation>("ExplainArtifact", payload, this.currentRunId);
  }

  async getCapabilities(): Promise<Result<Record<string, unknown>>> {
    return this.transport.sendCommand<Record<string, unknown>>("GetCapabilities", {}, "");
  }

  async getDaemonStatus(): Promise<Result<DaemonStatus>> {
    const probe = await this.transport.probe();
    if (!probe.ok) {
      return fail("not_available", probe.error.message, true);
    }
    return {
      ok: true,
      value: {
        status: "running",
        socketPath: this.transport.path,
      },
    };
  }
}

export { SocketRuntimeClient as LiveRuntimeClient };
