import { fail } from "../contract/parse.js";
import type {
  ArtifactExplanation,
  CorrectionRecord,
  DaemonStatus,
  EventCursor,
  EventEnvelope,
  Result,
  ResumeRunRequest,
  ResolveApprovalRequest,
  RunRef,
  RunSnapshot,
  RuntimeClient,
  StartRunRequest,
  StreamItem,
} from "../contract/types.js";

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
  readonly corrections: CorrectionRecord[] = [];

  async startRun(request: StartRunRequest): Promise<Result<RunRef>> {
    const runId = request.runId ?? "scenario-run";
    const events = [
      envelope(runId, "1", request.resumeFrom ? "RunRecovered" : "EpisodeStarted", { repo: request.repo, resumedFrom: request.resumeFrom }),
      envelope(runId, "2", "EpisodeStateChanged", { state: "observing" }),
      envelope(runId, "3", "EffectPreviewed", { sinkClass: "privileged" }),
      envelope(runId, "4", "EpisodeCompleted", { outcome: "satisfied" }),
    ];
    this.runs.set(runId, events);
    return { ok: true, value: { runId, episodeId: events[0]?.episodeId } };
  }

  async *streamEvents(cursor: EventCursor): AsyncIterable<Result<StreamItem>> {
    const events = this.runs.get(cursor.runId) ?? [];
    for (const item of events) {
      yield { ok: true, value: { contractVersion: "0.1", source: "mock", envelope: item } };
    }
  }

  async getRun(runId: string): Promise<Result<RunSnapshot>> {
    const last = this.runs.get(runId)?.at(-1);
    if (!last) return fail("not_found", `run ${runId} is not in the scenario adapter`);
    return { ok: true, value: { runId, status: last.payload.kind, seq: last.seq } };
  }

  async requestCancel(runId: string): Promise<Result<{ runId: string; command: "cancel"; status: "requested" }>> {
    const events = this.runs.get(runId);
    if (!events) return fail("not_found", `run ${runId} is not in the scenario adapter`);
    events.push(envelope(runId, String(events.length + 1), "RunAborted", { reason: "operator_cancel" }));
    return { ok: true, value: { runId, command: "cancel", status: "requested" } };
  }

  async requestCheckpoint(runId: string): Promise<Result<{ runId: string; command: "checkpoint"; status: "requested" }>> {
    return { ok: true, value: { runId, command: "checkpoint", status: "requested" } };
  }

  async requestResume(request: ResumeRunRequest): Promise<Result<RunRef>> {
    return this.startRun({ repo: ".", runId: request.runId, resumeFrom: request.checkpointId });
  }

  async explainArtifact(artifactId: string): Promise<Result<ArtifactExplanation>> {
    const known = ["default-harness", "typed-tools", "mock-agent"].includes(artifactId);
    return {
      ok: true,
      value: {
        artifactId,
        status: known ? "active" : "unknown",
        prediction: known
          ? "Improves observable, typed repository work under bounded authority."
          : "No activation pointer is present in the mock registry.",
        activatedBy: known ? [{ evidence: "mock-evidence: deterministic smoke baseline", strength: 0.82 }] : [],
        demotedBy: [
          { condition: "evaluation confidence falls below 0.60", effect: "remove activation pointer" },
          { condition: "integrity or provenance check fails", effect: "mark inactive pending review" },
        ],
        freshness: { source: "mock" },
      },
    };
  }

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<{ runId: string; command: "resolve_approval"; status: "requested" }>> {
    return { ok: true, value: { runId: request.approvalId, command: "resolve_approval", status: "requested" } };
  }

  async recordCorrection(record: CorrectionRecord): Promise<Result<{ runId: string; command: "record_correction"; status: "requested" }>> {
    this.corrections.push(record);
    return { ok: true, value: { runId: record.episodeId, command: "record_correction", status: "requested" } };
  }

  async getDaemonStatus(_signal?: AbortSignal): Promise<Result<DaemonStatus>> {
    return {
      ok: true,
      value: {
        status: "running",
        socketPath: "<scenario>",
        version: "0.4.0",
      },
    };
  }
}
