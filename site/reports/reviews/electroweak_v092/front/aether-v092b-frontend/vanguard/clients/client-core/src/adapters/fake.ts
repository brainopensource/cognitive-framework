import { fail } from "../contract/parse.js";
import type {
  ArtifactExplanation,
  CommandReceipt,
  CorrectionRecord,
  DaemonStatus,
  EventCursor,
  EventEnvelope,
  ResolveApprovalRequest,
  Result,
  ResumeRunRequest,
  RunRef,
  RunSnapshot,
  RuntimeClient,
  StartRunRequest,
  StreamItem,
} from "../contract/types.js";

export type FixtureSet = {
  runs?: Map<string, { status: string; events: EventEnvelope[] }>;
  health?: { status: string; version: string };
  artifacts?: Map<string, { content: string; digest: string }>;
};

export class FakeRuntimeClient implements RuntimeClient {
  public commandsReceived: Array<{ method: string; args: unknown[] }> = [];
  public injectedEvents: EventEnvelope[] = [];
  private readonly fixtures: FixtureSet;

  constructor(fixtures?: FixtureSet) {
    this.fixtures = fixtures ?? {};
  }

  private recordCommand(method: string, args: unknown[]) {
    this.commandsReceived.push({ method, args });
  }

  async startRun(request: StartRunRequest, signal?: AbortSignal): Promise<Result<RunRef>> {
    this.recordCommand("startRun", [request, signal]);
    const runId = request.runId ?? "fake-run";
    return { ok: true, value: { runId, episodeId: `episode-${runId}` } };
  }

  async *streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    this.recordCommand("streamEvents", [cursor, signal]);

    const runData = this.fixtures.runs?.get(cursor.runId);
    let events = runData ? [...runData.events] : [];
    events = events.concat(this.injectedEvents);

    const afterSeq = cursor.afterSeq ? BigInt(cursor.afterSeq) : undefined;

    for (const item of events) {
      if (signal?.aborted) {
        yield fail("transport_interrupted", "stream aborted", true);
        return;
      }
      const seq = BigInt(item.seq);
      if (afterSeq !== undefined && seq <= afterSeq) continue;

      yield { ok: true, value: { contractVersion: "0.1", source: "mock", envelope: item } };
    }
  }

  async getRun(runId: string, signal?: AbortSignal): Promise<Result<RunSnapshot>> {
    this.recordCommand("getRun", [runId, signal]);
    const runData = this.fixtures.runs?.get(runId);
    if (!runData) return fail("not_found", `Run ${runId} not found in fixtures`);

    const lastEvent = runData.events.at(-1);
    return {
      ok: true,
      value: {
        runId,
        status: runData.status,
        seq: lastEvent ? lastEvent.seq : "0",
      },
    };
  }

  async requestCancel(runId: string, signal?: AbortSignal): Promise<Result<CommandReceipt>> {
    this.recordCommand("requestCancel", [runId, signal]);
    return { ok: true, value: { runId, command: "cancel", status: "requested" } };
  }

  async requestCheckpoint(runId: string, signal?: AbortSignal): Promise<Result<CommandReceipt>> {
    this.recordCommand("requestCheckpoint", [runId, signal]);
    return { ok: true, value: { runId, command: "checkpoint", status: "requested" } };
  }

  async requestResume(request: ResumeRunRequest, signal?: AbortSignal): Promise<Result<RunRef>> {
    this.recordCommand("requestResume", [request, signal]);
    return { ok: true, value: { runId: request.runId, episodeId: `episode-${request.runId}` } };
  }

  async explainArtifact(artifactId: string, signal?: AbortSignal): Promise<Result<ArtifactExplanation>> {
    this.recordCommand("explainArtifact", [artifactId, signal]);
    const artifact = this.fixtures.artifacts?.get(artifactId);
    if (!artifact) return fail("not_found", `Artifact ${artifactId} not found in fixtures`);

    return {
      ok: true,
      value: {
        artifactId,
        status: "active",
        prediction: artifact.content,
        activatedBy: [],
        demotedBy: [],
        freshness: { source: "mock" },
      },
    };
  }

  async resolveApproval(request: ResolveApprovalRequest, signal?: AbortSignal): Promise<Result<CommandReceipt>> {
    this.recordCommand("resolveApproval", [request, signal]);
    return { ok: true, value: { runId: request.approvalId, command: "resolve_approval", status: "requested" } };
  }

  async recordCorrection(record: CorrectionRecord, signal?: AbortSignal): Promise<Result<CommandReceipt>> {
    this.recordCommand("recordCorrection", [record, signal]);
    return { ok: true, value: { runId: record.episodeId, command: "record_correction", status: "requested" } };
  }

  async getDaemonStatus(signal?: AbortSignal): Promise<Result<DaemonStatus>> {
    this.recordCommand("getDaemonStatus", [signal]);
    if (this.fixtures.health) {
      return {
        ok: true,
        value: {
          status: this.fixtures.health.status as DaemonStatus["status"],
          socketPath: "fake",
          version: this.fixtures.health.version,
        },
      };
    }
    return {
      ok: true,
      value: {
        status: "running",
        socketPath: "fake",
        version: "1.0.0",
      },
    };
  }

  public injectEvent(event: EventEnvelope) {
    this.injectedEvents.push(event);
  }
}
