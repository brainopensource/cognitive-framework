import { readFileSync } from "node:fs";
import { afterCursor, fail, parseJsonlLine } from "../contract/parse.js";
import type {
  ArtifactExplanation,
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

function unavailable(method: string): Result<never> {
  return fail("not_available", `${method} is not available on the replay adapter`);
}

function projectExplanation(envelopes: readonly EventEnvelope[], artifactId: string): ArtifactExplanation {
  const matches = envelopes.filter((envelope) => envelope.payload.kind === "ActivationChanged" && envelope.payload.artifactId === artifactId);
  const latest = matches.at(-1);
  if (!latest) {
    return {
      artifactId,
      status: "unknown",
      prediction: "No activation pointer is present in the recorded ledger.",
      activatedBy: [],
      demotedBy: [],
      freshness: { source: "replay" },
    };
  }
  const payload = latest.payload;
  const status = payload.status === "active" || payload.status === "inactive" ? payload.status : "unknown";
  const activatedBy = Array.isArray(payload.activatedBy) ? payload.activatedBy as ArtifactExplanation["activatedBy"] : [];
  const demotedBy = Array.isArray(payload.demotedBy) ? payload.demotedBy as ArtifactExplanation["demotedBy"] : [];
  return {
    artifactId,
    status,
    prediction: typeof payload.prediction === "string" ? payload.prediction : "",
    activatedBy,
    demotedBy,
    freshness: { source: "replay", asOfSeq: latest.seq },
  };
}

export class ReplayRuntimeClient implements RuntimeClient {
  private constructor(private readonly envelopes: readonly EventEnvelope[]) {}

  static fromJsonl(text: string): ReplayRuntimeClient {
    const envelopes: EventEnvelope[] = [];
    for (const line of text.split(/\r?\n/)) {
      if (!line.trim()) continue;
      const parsed = parseJsonlLine(line);
      if (!parsed.ok) throw new Error(parsed.error.message);
      envelopes.push(parsed.value);
    }
    return new ReplayRuntimeClient(envelopes);
  }

  static fromFile(path: string): ReplayRuntimeClient {
    return ReplayRuntimeClient.fromJsonl(readFileSync(path, "utf8"));
  }

  async startRun(request: StartRunRequest): Promise<Result<RunRef>> {
    const match = this.envelopes.find((envelope) => envelope.runId === (request.runId ?? envelope.runId) && envelope.scope === "episode");
    if (!match?.runId) return fail("not_found", `run ${request.runId ?? "<missing>"} is not in the replay ledger`);
    return { ok: true, value: { runId: match.runId, episodeId: match.episodeId } };
  }

  async *streamEvents(cursor: EventCursor): AsyncIterable<Result<StreamItem>> {
    for (const envelope of this.envelopes) {
      if (envelope.runId !== undefined && envelope.runId !== cursor.runId) continue;
      if (!afterCursor(envelope.seq, cursor.afterSeq)) continue;
      yield { ok: true, value: { contractVersion: "0.1", source: "replay", envelope } };
    }
  }

  async getRun(runId: string): Promise<Result<RunSnapshot>> {
    const events = this.envelopes.filter((envelope) => envelope.runId === runId);
    const last = events.at(-1);
    if (!last) return fail("not_found", `run ${runId} is not in the replay ledger`);
    return { ok: true, value: { runId, status: String(last.payload.kind), seq: last.seq } };
  }

  async requestCancel(runId: string): Promise<Result<never>> {
    return unavailable(`requestCancel(${runId})`);
  }

  async requestCheckpoint(runId: string): Promise<Result<never>> {
    return unavailable(`requestCheckpoint(${runId})`);
  }

  async requestResume(request: ResumeRunRequest): Promise<Result<never>> {
    return unavailable(`requestResume(${request.runId})`);
  }

  async explainArtifact(artifactId: string): Promise<Result<ArtifactExplanation>> {
    return { ok: true, value: projectExplanation(this.envelopes, artifactId) };
  }

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<never>> {
    return unavailable(`resolveApproval(${request.approvalId})`);
  }
}
