import { fail } from "../contract/parse.js";
import type {
  ApprovalChallenge,
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
import { OperatorSigner } from "./signer.js";
import { FeedTransport, SocketTransport, resolveSocketPath, type RuntimeTransport } from "./transport.js";

export type LiveClientOptions = {
  repo?: string;
  prompt?: string;
  brief?: string;
  model?: string;
  manifest?: string;
  runId?: string;
  socketPath?: string;
  autoApprove?: boolean;
  signer?: OperatorSigner;
  connectTimeoutMs?: number;
  commandTimeoutMs?: number;
  maxReconnects?: number;
  backoffMs?: number;
};

function challengeFromPayload(payload: Record<string, unknown>): ApprovalChallenge | undefined {
  const approvalId = payload.approvalId;
  const argsDigest = payload.argsDigest;
  const descriptorDigest = payload.descriptorDigest;
  const expiresAt = payload.expiresAt;
  if (typeof approvalId !== "string") return undefined;
  return {
    approvalId,
    processId: String(payload.processId ?? ""),
    action: String(payload.action ?? ""),
    normalizedDiff: String(payload.normalizedDiff ?? payload.unifiedDiff ?? payload.diff ?? ""),
    argsDigest: typeof argsDigest === "string" ? argsDigest : "",
    descriptorDigest: typeof descriptorDigest === "string" ? descriptorDigest : "",
    principal: String(payload.principal ?? "operator"),
    expiresAt: typeof expiresAt === "string" ? expiresAt : "",
  };
}

export class LiveRuntimeClient implements RuntimeClient {
  private readonly transport: RuntimeTransport;
  private readonly socket: SocketTransport | undefined;
  private readonly options: LiveClientOptions;
  private readonly signer: OperatorSigner | undefined;
  private currentRunId: string;
  private currentEpisodeId: string;
  private lastSeenSeq: bigint = 0n;
  private status: string = "pending";
  private readonly boundedBuffer: StreamItem[] = [];
  private static readonly MAX_BUFFER_SIZE = 10_000;
  private readonly corrections: CorrectionRecord[] = [];
  private lastChallenge: ApprovalChallenge | undefined;

  constructor(lines?: AsyncIterable<string>, options: LiveClientOptions = {}) {
    this.options = options;
    this.currentRunId = options.runId ?? `run-${Date.now()}`;
    this.currentEpisodeId = `episode-${Date.now()}`;
    this.signer = options.signer;
    if (lines) {
      this.transport = new FeedTransport(lines);
    } else {
      const socket = new SocketTransport({
        socketPath: resolveSocketPath(options.socketPath),
        connectTimeoutMs: options.connectTimeoutMs ?? 300,
        commandTimeoutMs: options.commandTimeoutMs ?? 500,
        maxReconnects: options.maxReconnects ?? 3,
        backoffMs: options.backoffMs ?? 50,
      });
      this.socket = socket;
      this.transport = socket;
    }
  }

  private async sendCommand<T>(name: string, payload: Record<string, unknown>, runId: string): Promise<Result<T>> {
    return this.transport.sendCommand<T>(name, payload, runId);
  }

  async startRun(request: StartRunRequest, _signal?: AbortSignal): Promise<Result<RunRef>> {
    if (this.transport.kind === "feed") {
      if (request.runId) this.currentRunId = request.runId;
      this.status = "running";
      return { ok: true, value: { runId: this.currentRunId, episodeId: this.currentEpisodeId } };
    }

    const runId = request.runId ?? this.currentRunId;
    const res = await this.sendCommand<{ runId: string }>(
      "StartRun",
      {
        manifestPath: request.manifest ?? this.options.manifest ?? "manifest.json",
        repoPath: request.repo ?? this.options.repo ?? ".",
        brief: request.brief ?? request.prompt ?? this.options.brief ?? this.options.prompt ?? "run",
      },
      runId
    );
    if (!res.ok) return res;
    this.currentRunId = res.value.runId;
    this.status = "running";
    return { ok: true, value: { runId: this.currentRunId, episodeId: this.currentEpisodeId } };
  }

  async *streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    for await (const result of this.transport.streamItems(cursor, signal)) {
      if (!result.ok) {
        yield result;
        continue;
      }
      const item = result.value;
      const seq = BigInt(item.envelope.seq);
      this.lastSeenSeq = seq;
      if (item.envelope.payload.kind === "ApprovalRequested") {
        this.lastChallenge = challengeFromPayload(item.envelope.payload);
      }
      if (this.boundedBuffer.length >= LiveRuntimeClient.MAX_BUFFER_SIZE) {
        this.boundedBuffer.shift();
      }
      this.boundedBuffer.push(item);
      yield result;
    }
    this.status = "completed";
  }

  async getRun(runId: string): Promise<Result<RunSnapshot>> {
    if (this.transport.kind === "feed") {
      return { ok: true, value: { runId, status: this.status, seq: this.lastSeenSeq.toString() } };
    }
    const res = await this.sendCommand<{ status: string }>("GetRun", {}, runId);
    if (!res.ok) return res;
    return { ok: true, value: { runId, status: res.value.status, seq: this.lastSeenSeq.toString() } };
  }

  async requestCancel(runId: string): Promise<Result<CommandReceipt>> {
    if (this.transport.kind === "feed") {
      this.status = "cancelled";
      return { ok: true, value: { runId, command: "cancel", status: "requested" } };
    }
    const res = await this.sendCommand<{ status: string }>("Cancel", {}, runId);
    if (!res.ok) return res;
    this.status = "cancelled";
    return { ok: true, value: { runId, command: "cancel", status: "accepted" } };
  }

  async requestCheckpoint(runId: string): Promise<Result<CommandReceipt>> {
    if (this.transport.kind === "feed") {
      return { ok: true, value: { runId, command: "checkpoint", status: "requested" } };
    }
    const res = await this.sendCommand<{ status: string }>("Checkpoint", {}, runId);
    if (!res.ok) return res;
    return { ok: true, value: { runId, command: "checkpoint", status: "accepted" } };
  }

  async requestResume(request: ResumeRunRequest): Promise<Result<RunRef>> {
    if (this.transport.kind === "feed") {
      return { ok: true, value: { runId: request.runId } };
    }
    const res = await this.sendCommand<{ status: string }>("Resume", {}, request.runId);
    if (!res.ok) return res;
    return { ok: true, value: { runId: request.runId } };
  }

  async explainArtifact(artifactId: string): Promise<Result<ArtifactExplanation>> {
    if (this.transport.kind === "feed") {
      return fail("not_available", "explainArtifact has no evidence on JSONL feed transport", false);
    }
    const res = await this.sendCommand<{ explanation?: unknown }>("ExplainArtifact", { artifactId }, this.currentRunId);
    if (!res.ok) return res;
    const explanation = res.value.explanation;
    if (explanation === null || typeof explanation !== "object" || Array.isArray(explanation)) {
      return fail("not_available", `no artifact explanation from daemon for ${artifactId}`, false);
    }
    const body = explanation as Record<string, unknown>;
    const status = body.status;
    if (status !== "active" && status !== "inactive" && status !== "unknown") {
      return fail("not_available", `no artifact explanation from daemon for ${artifactId}`, false);
    }
    return {
      ok: true,
      value: {
        artifactId,
        status,
        prediction: typeof body.prediction === "string" ? body.prediction : "",
        activatedBy: Array.isArray(body.activatedBy) ? (body.activatedBy as ArtifactExplanation["activatedBy"]) : [],
        demotedBy: Array.isArray(body.demotedBy) ? (body.demotedBy as ArtifactExplanation["demotedBy"]) : [],
        freshness: { source: "live", asOfSeq: this.lastSeenSeq.toString() },
      },
    };
  }

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<CommandReceipt>> {
    if (this.transport.kind === "feed") {
      return {
        ok: true,
        value: { runId: this.currentRunId, command: "resolve_approval", status: "requested" },
      };
    }
    const challenge = this.lastChallenge;
    if (!challenge || challenge.approvalId !== request.approvalId) {
      return fail("not_available", "no ApprovalRequested challenge with digests is loaded (Joint J4)", false);
    }
    if (!challenge.argsDigest || !challenge.descriptorDigest || !challenge.expiresAt) {
      return fail("not_available", "approval challenge digests are empty (Joint J4)", false);
    }
    const signer = this.signer ?? OperatorSigner.loadOrCreate();
    const decision = signer.signChallenge(
      challenge,
      request.decision === "approve" ? "approved" : "rejected",
      "operator"
    );
    const res = await this.sendCommand<{ status: string }>("ResolveApproval", { decision }, this.currentRunId);
    if (!res.ok) return res;
    return {
      ok: true,
      value: { runId: this.currentRunId, command: "resolve_approval", status: "accepted" },
    };
  }

  async recordCorrection(record: CorrectionRecord): Promise<Result<CommandReceipt>> {
    if (this.transport.kind === "feed") {
      this.corrections.push(record);
      return { ok: true, value: { runId: this.currentRunId, command: "record_correction", status: "requested" } };
    }
    const res = await this.sendCommand<{ status: string }>("RecordCorrection", { correction: record }, this.currentRunId);
    if (!res.ok) return res;
    this.corrections.push(record);
    return { ok: true, value: { runId: this.currentRunId, command: "record_correction", status: "accepted" } };
  }

  async getDaemonStatus(_signal?: AbortSignal): Promise<Result<DaemonStatus>> {
    if (this.transport.kind === "feed") {
      return fail("not_available", "JSONL feed mode has no RuntimeService daemon", false);
    }
    if (!this.socket) {
      return fail("not_available", "no socket transport", false);
    }
    const probed = await this.socket.probe();
    if (!probed.ok) return probed;
    return {
      ok: true,
      value: {
        status: "running",
        socketPath: probed.value.socketPath,
      },
    };
  }
}
