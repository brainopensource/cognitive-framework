import { createConnection, type Socket } from "node:net";
import { createInterface } from "node:readline";
import { fail, parseJsonlLine } from "../contract/parse.js";
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
} from "../contract/types.js";

export type LiveClientOptions = {
  repo?: string;
  prompt?: string;
  brief?: string;
  model?: string;
  manifest?: string;
  runId?: string;
  socketPath?: string;
  autoApprove?: boolean;
};

export class LiveRuntimeClient implements RuntimeClient {
  private readonly lines?: AsyncIterable<string>;
  private readonly options: LiveClientOptions;
  private currentRunId: string;
  private currentEpisodeId: string;
  private lastSeenSeq: bigint = 0n;
  private status: string = "pending";
  private socketPath: string;
  private readonly boundedBuffer: StreamItem[] = [];
  private static readonly MAX_BUFFER_SIZE = 10_000;
  private readonly corrections: CorrectionRecord[] = [];

  constructor(lines?: AsyncIterable<string>, options: LiveClientOptions = {}) {
    this.lines = lines;
    this.options = options;
    this.currentRunId = options.runId ?? `run-${Date.now()}`;
    this.currentEpisodeId = `episode-${Date.now()}`;
    this.socketPath = options.socketPath ?? process.env.VANGUARD_RUNTIME_SOCKET ?? "/tmp/vanguard-runtime.sock";
  }

  private isFeedMode(): boolean {
    return this.lines !== undefined;
  }

  private unavailable(action: string): Result<never> {
    return fail(
      "not_available",
      `RuntimeService daemon has no ${action} protocol at ${this.socketPath}`,
      true,
    );
  }

  async startRun(request: StartRunRequest, _signal?: AbortSignal): Promise<Result<RunRef>> {
    if (!this.isFeedMode()) {
      return this.unavailable("startRun");
    }
    if (request.runId) this.currentRunId = request.runId;
    this.status = "running";
    return {
      ok: true,
      value: {
        runId: this.currentRunId,
        episodeId: this.currentEpisodeId,
      },
    };
  }

  async *streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    const afterSeq = cursor.afterSeq ? BigInt(cursor.afterSeq) : undefined;

    if (this.lines) {
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
        if (afterSeq !== undefined && seq <= afterSeq) {
          continue;
        }
        if (this.lastSeenSeq > 0n && seq <= this.lastSeenSeq) {
          // Deduplicate duplicate sequence frames
          continue;
        }
        this.lastSeenSeq = seq;

        const item: StreamItem = {
          contractVersion: "0.1",
          source: "live",
          envelope: parsed.value,
        };

        if (this.boundedBuffer.length >= LiveRuntimeClient.MAX_BUFFER_SIZE) {
          this.boundedBuffer.shift();
        }
        this.boundedBuffer.push(item);

        yield { ok: true, value: item };
      }
      this.status = "completed";
      return;
    }

    // Connect to RuntimeService daemon over Unix domain socket
    let socket: Socket;
    try {
      socket = createConnection({ path: this.socketPath });
    } catch {
      yield fail("not_available", `RuntimeService daemon not reachable at ${this.socketPath}`, true);
      return;
    }

    if (signal) {
      signal.addEventListener("abort", () => {
        socket.destroy();
      });
    }

    const rl = createInterface({ input: socket });

    try {
      for await (const line of rl) {
        if (signal?.aborted) {
          yield fail("transport_interrupted", "live stream aborted", true);
          return;
        }
        if (!line.trim()) continue;
        const parsed = parseJsonlLine(line);
        if (!parsed.ok) {
          yield parsed;
          continue;
        }
        const seq = BigInt(parsed.value.seq);
        if (afterSeq !== undefined && seq <= afterSeq) {
          continue;
        }
        if (this.lastSeenSeq > 0n && seq <= this.lastSeenSeq) {
          continue;
        }
        this.lastSeenSeq = seq;

        const item: StreamItem = {
          contractVersion: "0.1",
          source: "live",
          envelope: parsed.value,
        };

        if (this.boundedBuffer.length >= LiveRuntimeClient.MAX_BUFFER_SIZE) {
          this.boundedBuffer.shift();
        }
        this.boundedBuffer.push(item);

        yield { ok: true, value: item };
      }
      this.status = "completed";
    } catch {
      yield fail("transport_interrupted", "daemon connection closed unexpectedly", true);
    } finally {
      socket.destroy();
    }
  }

  async getRun(runId: string): Promise<Result<RunSnapshot>> {
    if (!this.isFeedMode()) {
      return this.unavailable("getRun");
    }
    return {
      ok: true,
      value: {
        runId,
        status: this.status,
        seq: this.lastSeenSeq.toString(),
      },
    };
  }

  async requestCancel(runId: string): Promise<Result<CommandReceipt>> {
    if (!this.isFeedMode()) {
      return this.unavailable("cancel");
    }
    this.status = "cancelled";
    return {
      ok: true,
      value: {
        runId,
        command: "cancel",
        status: "requested",
      },
    };
  }

  async requestCheckpoint(runId: string): Promise<Result<CommandReceipt>> {
    if (!this.isFeedMode()) {
      return this.unavailable("checkpoint");
    }
    return {
      ok: true,
      value: {
        runId,
        command: "checkpoint",
        status: "requested",
      },
    };
  }

  async requestResume(request: ResumeRunRequest): Promise<Result<RunRef>> {
    if (!this.isFeedMode()) {
      return this.unavailable("resume");
    }
    return {
      ok: true,
      value: {
        runId: request.runId,
      },
    };
  }

  async explainArtifact(artifactId: string): Promise<Result<ArtifactExplanation>> {
    if (!this.isFeedMode()) {
      return this.unavailable("explainArtifact");
    }
    return {
      ok: true,
      value: {
        artifactId,
        status: "active",
        prediction: `Live artifact ${artifactId} active under RuntimeService`,
        activatedBy: [{ evidence: `live stream seq=${this.lastSeenSeq}`, strength: 1.0 }],
        demotedBy: [],
        freshness: { source: "live", asOfSeq: this.lastSeenSeq.toString() },
      },
    };
  }

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<CommandReceipt>> {
    if (!this.isFeedMode()) {
      return this.unavailable("resolveApproval");
    }
    return {
      ok: true,
      value: {
        runId: this.currentRunId,
        command: "resolve_approval",
        status: "requested",
      },
    };
  }

  async recordCorrection(record: CorrectionRecord): Promise<Result<CommandReceipt>> {
    if (!this.isFeedMode()) {
      return this.unavailable("recordCorrection");
    }
    this.corrections.push(record);
    return {
      ok: true,
      value: {
        runId: this.currentRunId,
        command: "record_correction",
        status: "requested",
      },
    };
  }

  async getDaemonStatus(_signal?: AbortSignal): Promise<Result<DaemonStatus>> {
    if (this.isFeedMode()) {
      return fail("not_available", "JSONL feed mode has no RuntimeService daemon", false);
    }
    return await new Promise((resolve) => {
      const socket = createConnection({ path: this.socketPath });
      const timer = setTimeout(() => {
        socket.destroy();
        resolve(fail("not_available", `RuntimeService daemon not reachable at ${this.socketPath}`, true));
      }, 400);
      socket.once("connect", () => {
        clearTimeout(timer);
        socket.destroy();
        resolve({
          ok: true,
          value: {
            status: "running",
            socketPath: this.socketPath,
            version: "0.4.0",
          },
        });
      });
      socket.once("error", () => {
        clearTimeout(timer);
        resolve(fail("not_available", `RuntimeService daemon not reachable at ${this.socketPath}`, true));
      });
    });
  }
}


