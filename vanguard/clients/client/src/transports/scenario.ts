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
  type ResumeOptions,
  type Result,
  type RunRef,
  type RunSnapshot,
  type RunSummary,
  type StartRunRequest,
  type StreamItem,
} from "@aether/contracts";
import type { RuntimeClient } from "../client.js";

/**
 * Fixed-scenario offline demo client, ported from
 * @vanguard/client-core's ScenarioRuntimeClient (F4 Phase 5). Plays back a
 * hardcoded 4-event episode for `vg run --scenario`; used for smoke demos,
 * never a live transport.
 */

const CLOCK = "2026-08-15T00:00:00.000Z";

function envelope(runId: string, seq: string, kind: string, extra: Record<string, unknown> = {}): EventEnvelope {
  const n = Number(seq);
  return {
    schemaVersion: "vg.4",
    eventId: `018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a${(0x8b + n).toString(16)}`,
    scope: "episode",
    runId,
    episodeId: `episode-${runId}`,
    traceId: `trace-${runId}`,
    spanId: `span-${seq}`,
    seq,
    occurredAt: CLOCK,
    recordedAt: CLOCK,
    principal: "scenario-agent",
    principalRole: "episode",
    tenantId: "tenant-default",
    ownerId: "owner-platform",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: { kind, ...extra },
  };
}

export class ScenarioRuntimeClient implements RuntimeClient {
  private readonly runs = new Map<string, EventEnvelope[]>();
  readonly corrections: unknown[] = [];

  async startRun(request: StartRunRequest): Promise<Result<RunRef>> {
    const runId = request.runId ?? "scenario-run";
    const events = [
      envelope(runId, "1", request.resumeFrom ? "RunRecovered" : "EpisodeStarted", {
        repo: request.repo ?? request.repoPath,
        resumedFrom: request.resumeFrom,
      }),
      envelope(runId, "2", "EpisodeStateChanged", { state: "observing" }),
      envelope(runId, "3", "EffectPreviewed", { sinkClass: "privileged" }),
      envelope(runId, "4", "EpisodeCompleted", { outcome: "satisfied" }),
    ];
    this.runs.set(runId, events);
    return { ok: true, value: { runId, episodeId: events[0]?.episodeId } };
  }

  async getRun(runId: string, _expectedSeq?: string | number): Promise<Result<RunSnapshot>> {
    const last = this.runs.get(runId)?.at(-1);
    if (!last) return fail("not_found", `run ${runId} is not in the scenario adapter`);
    return { ok: true, value: { runId, status: String(last.payload.kind), seq: last.seq } };
  }

  async listRuns(_options?: ListRunsOptions): Promise<Result<RunSummary[]>> {
    const summaries: RunSummary[] = [...this.runs.entries()].map(([runId, events]) => {
      const last = events.at(-1);
      return { runId, status: last ? String(last.payload.kind) : "unknown", seq: last?.seq ?? "0" };
    });
    return { ok: true, value: summaries };
  }

  async *streamEvents(cursor: EventCursor, _signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    const events = this.runs.get(cursor.runId) ?? [];
    for (const item of events) {
      yield { ok: true, value: { contractVersion: "vg.4", source: "mock", envelope: item } };
    }
  }

  async requestCancel(runId: string, _options?: CancelOptions): Promise<Result<CommandReceipt>> {
    const events = this.runs.get(runId);
    if (!events) return fail("not_found", `run ${runId} is not in the scenario adapter`);
    events.push(envelope(runId, String(events.length + 1), "RunAborted", { reason: "operator_cancel" }));
    return { ok: true, value: { commandId: `scenario-cancel-${runId}`, runId, status: "completed" } };
  }

  async requestCheckpoint(runId: string, _options?: CheckpointOptions): Promise<Result<CommandReceipt>> {
    return { ok: true, value: { commandId: `scenario-checkpoint-${runId}`, runId, status: "completed" } };
  }

  async requestResume(runId: string, options?: ResumeOptions): Promise<Result<CommandReceipt>> {
    const started = await this.startRun({ repo: ".", runId, resumeFrom: options?.checkpointId });
    if (!started.ok) return started;
    return { ok: true, value: { commandId: `scenario-resume-${runId}`, runId: started.value.runId, status: "completed" } };
  }

  async explainArtifact(artifactId: string, _options?: ExplainArtifactOptions): Promise<Result<ArtifactExplanation>> {
    const known = ["default-harness", "typed-tools", "mock-agent"].includes(artifactId);
    return {
      ok: true,
      value: {
        artifactId,
        status: known ? "active" : "unknown",
        prediction: known
          ? "Improves observable, typed repository work under bounded authority."
          : "No activation pointer is present in the mock registry.",
        activatedBy: known ? ["mock-evidence: deterministic smoke baseline"] : [],
        demotedBy: [
          "evaluation confidence falls below 0.60",
          "integrity or provenance check fails",
        ],
      },
    };
  }

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<CommandReceipt>> {
    return {
      ok: true,
      value: { commandId: `scenario-resolve-${request.approvalId ?? "unknown"}`, status: "completed" },
    };
  }

  async recordCorrection(request: RecordCorrectionRequest): Promise<Result<CommandReceipt>> {
    this.corrections.push(request.correction);
    return {
      ok: true,
      value: { commandId: `scenario-correction-${request.correction.correctionId}`, runId: request.correction.runId, status: "completed" },
    };
  }

  async getCapabilities(): Promise<Result<Record<string, unknown>>> {
    return { ok: true, value: { protocol: "vg.4", mode: "scenario" } };
  }

  async getDaemonStatus(): Promise<Result<DaemonStatus>> {
    return { ok: true, value: { status: "running", socketPath: "<scenario>", version: "0.4.0" } };
  }
}
