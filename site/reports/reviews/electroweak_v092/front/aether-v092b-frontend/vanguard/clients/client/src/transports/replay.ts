import {
  fail,
  parseJsonlLine,
  type ApprovalChallenge,
  type ArtifactExplanation,
  type CancelOptions,
  type CheckpointOptions,
  type CommandReceipt,
  type CorrectionRecord,
  type DaemonStatus,
  type EventCursor,
  type EventEnvelope,
  type ExplainArtifactOptions,
  type ListRunsOptions,
  type RecordCorrectionRequest,
  type ResolveApprovalRequest,
  type Result,
  type ResumeOptions,
  type RunRef,
  type RunSnapshot,
  type RunSummary,
  type StartRunRequest,
  type StreamItem,
} from "@aether/contracts";
import type { RuntimeClient } from "../client.js";
import type { RuntimeTransport } from "./transport.js";

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
    if (name === "ListRuns") {
      return { ok: true, value: { runs: [] } as T };
    }
    if (name === "Cancel" || name === "Checkpoint" || name === "Resume" || name === "ResolveApproval") {
      return { ok: true, value: { commandId: "feed-cmd", status: "completed", runId } as T };
    }
    return fail("not_available", `${name} is not available on offline FeedTransport`, false);
  }

  async *streamItems(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    const afterSeq = cursor.afterSeq !== undefined ? BigInt(cursor.afterSeq) : undefined;
    let lastSeenSeq = 0n;

    for await (const line of this.lines) {
      if (signal?.aborted) {
        yield fail("transport_interrupted", "Stream aborted by caller", true);
        return;
      }
      const parsed = parseJsonlLine(line);
      if (!parsed.ok) {
        yield parsed;
        continue;
      }
      const env = parsed.value;
      const seq = BigInt(env.seq);
      if (afterSeq !== undefined && seq <= afterSeq) continue;
      if (lastSeenSeq > 0n && seq <= lastSeenSeq) continue;
      lastSeenSeq = seq;
      yield {
        ok: true,
        value: {
          contractVersion: "vg.4",
          source: "replay",
          envelope: env,
        },
      };
    }
  }
}

export class ReplayRuntimeClient implements RuntimeClient {
  private readonly feed: FeedTransport;
  private currentRunId: string = "replay-run-default";
  private status: string = "running";

  constructor(lines: AsyncIterable<string>) {
    this.feed = new FeedTransport(lines);
  }

  static fromEnvelopes(envelopes: readonly EventEnvelope[]): ReplayRuntimeClient {
    async function* gen() {
      for (const env of envelopes) {
        yield JSON.stringify(env);
      }
    }
    return new ReplayRuntimeClient(gen());
  }

  async startRun(request: StartRunRequest, _signal?: AbortSignal): Promise<Result<RunRef>> {
    if (request.runId) this.currentRunId = request.runId;
    this.status = "running";
    return { ok: true, value: { runId: this.currentRunId, episodeId: "ep-replay-1" } };
  }

  async getRun(runId: string, _expectedSeq?: string | number): Promise<Result<RunSnapshot>> {
    return {
      ok: true,
      value: {
        runId,
        status: this.status,
        seq: "1",
      },
    };
  }

  async listRuns(_options?: ListRunsOptions): Promise<Result<RunSummary[]>> {
    return {
      ok: true,
      value: [{ runId: this.currentRunId, status: this.status, seq: "1" }],
    };
  }

  async *streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    yield* this.feed.streamItems(cursor, signal);
  }

  async requestCancel(runId: string, _options?: CancelOptions): Promise<Result<CommandReceipt>> {
    this.status = "cancelled";
    return { ok: true, value: { commandId: "cancel-1", status: "completed", runId } };
  }

  async requestCheckpoint(runId: string, _options?: CheckpointOptions): Promise<Result<CommandReceipt>> {
    return { ok: true, value: { commandId: "cp-1", status: "completed", runId } };
  }

  async requestResume(runId: string, _options?: ResumeOptions): Promise<Result<CommandReceipt>> {
    this.status = "running";
    return { ok: true, value: { commandId: "resume-1", status: "completed", runId } };
  }

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<CommandReceipt>> {
    return { ok: true, value: { commandId: "approval-1", status: "completed", runId: this.currentRunId } };
  }

  async recordCorrection(_request: RecordCorrectionRequest): Promise<Result<CommandReceipt>> {
    return fail("permission_denied", "Offline replay client cannot record durable corrections", false);
  }

  async explainArtifact(artifactId: string, _options?: ExplainArtifactOptions): Promise<Result<ArtifactExplanation>> {
    return {
      ok: true,
      value: {
        artifactId,
        status: "replay_mock",
        prediction: "Artifact recorded in replay fixture",
      },
    };
  }

  async getCapabilities(): Promise<Result<Record<string, unknown>>> {
    return {
      ok: true,
      value: {
        mode: "replay",
        replaySupported: true,
      },
    };
  }

  async getDaemonStatus(): Promise<Result<DaemonStatus>> {
    return {
      ok: true,
      value: {
        status: "running",
        socketPath: "memory://replay",
      },
    };
  }
}
