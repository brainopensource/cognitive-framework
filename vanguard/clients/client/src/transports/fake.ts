import {
  fail,
  type ArtifactExplanation,
  type CancelOptions,
  type CheckpointOptions,
  type CommandReceipt,
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

/**
 * Fixture-backed `RuntimeClient` for demo mode and offline UI development.
 *
 * Ported from `@vanguard/client-core`'s `FakeRuntimeClient` (F4 Phase 0):
 * same fixture/injection model, adapted to `@aether/client`'s `RuntimeClient`
 * interface, which -- unlike client-core's -- makes `listRuns` and
 * `getCapabilities` required rather than optional.
 */
export type FixtureSet = {
  runs?: Map<string, { status: string; events: EventEnvelope[] }>;
  health?: { status: DaemonStatus["status"]; version: string };
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

  async getRun(runId: string, expectedSeq?: string | number): Promise<Result<RunSnapshot>> {
    this.recordCommand("getRun", [runId, expectedSeq]);
    const runData = this.fixtures.runs?.get(runId);
    if (!runData) return fail("not_found", `Run ${runId} not found in fixtures`);

    const lastEvent = runData.events.at(-1);
    return {
      ok: true,
      value: { runId, status: runData.status, seq: lastEvent ? lastEvent.seq : "0" },
    };
  }

  async listRuns(options?: ListRunsOptions): Promise<Result<RunSummary[]>> {
    this.recordCommand("listRuns", [options]);
    const runs = this.fixtures.runs ?? new Map();
    const summaries: RunSummary[] = [...runs.entries()].map(([runId, data]) => {
      const lastEvent = data.events.at(-1);
      return { runId, status: data.status, seq: lastEvent ? lastEvent.seq : "0" };
    });
    const offset = options?.offset ?? 0;
    const limit = options?.limit ?? summaries.length;
    return { ok: true, value: summaries.slice(offset, offset + limit) };
  }

  async *streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    this.recordCommand("streamEvents", [cursor, signal]);

    const runData = this.fixtures.runs?.get(cursor.runId);
    let events = runData ? [...runData.events] : [];
    events = events.concat(this.injectedEvents);

    const afterSeq = cursor.afterSeq !== undefined ? BigInt(cursor.afterSeq) : undefined;

    for (const item of events) {
      if (signal?.aborted) {
        yield fail("transport_interrupted", "stream aborted", true);
        return;
      }
      const seq = BigInt(item.seq);
      if (afterSeq !== undefined && seq <= afterSeq) continue;

      yield { ok: true, value: { contractVersion: "vg.4", source: "mock", envelope: item } };
    }
  }

  async requestCancel(runId: string, options?: CancelOptions): Promise<Result<CommandReceipt>> {
    this.recordCommand("requestCancel", [runId, options]);
    return { ok: true, value: { commandId: `fake-cancel-${runId}`, runId, status: "completed" } };
  }

  async requestCheckpoint(runId: string, options?: CheckpointOptions): Promise<Result<CommandReceipt>> {
    this.recordCommand("requestCheckpoint", [runId, options]);
    return { ok: true, value: { commandId: `fake-checkpoint-${runId}`, runId, status: "completed" } };
  }

  async requestResume(runId: string, options?: ResumeOptions): Promise<Result<CommandReceipt>> {
    this.recordCommand("requestResume", [runId, options]);
    return { ok: true, value: { commandId: `fake-resume-${runId}`, runId, status: "completed" } };
  }

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<CommandReceipt>> {
    this.recordCommand("resolveApproval", [request]);
    return {
      ok: true,
      value: { commandId: `fake-resolve-${request.approvalId ?? "unknown"}`, status: "completed" },
    };
  }

  async recordCorrection(request: RecordCorrectionRequest): Promise<Result<CommandReceipt>> {
    this.recordCommand("recordCorrection", [request]);
    return {
      ok: true,
      value: { commandId: `fake-correction-${request.correction.correctionId}`, status: "completed" },
    };
  }

  async explainArtifact(artifactId: string, options?: ExplainArtifactOptions): Promise<Result<ArtifactExplanation>> {
    this.recordCommand("explainArtifact", [artifactId, options]);
    const artifact = this.fixtures.artifacts?.get(artifactId);
    if (!artifact) return fail("not_found", `Artifact ${artifactId} not found in fixtures`);

    return {
      ok: true,
      value: { artifactId, status: "active", prediction: artifact.content },
    };
  }

  async getCapabilities(): Promise<Result<Record<string, unknown>>> {
    this.recordCommand("getCapabilities", []);
    return { ok: true, value: { protocol: "vg.4", source: "mock" } };
  }

  async getDaemonStatus(): Promise<Result<DaemonStatus>> {
    this.recordCommand("getDaemonStatus", []);
    if (this.fixtures.health) {
      return {
        ok: true,
        value: { status: this.fixtures.health.status, socketPath: "fake", version: this.fixtures.health.version },
      };
    }
    return { ok: true, value: { status: "running", socketPath: "fake", version: "1.0.0" } };
  }

  public injectEvent(event: EventEnvelope) {
    this.injectedEvents.push(event);
  }
}
