export type ClientContractVersion = "0.1";
export type StreamSource = "mock" | "replay" | "live";

export type ClientFailure = {
  code:
    | "invalid_request"
    | "not_found"
    | "conflict"
    | "not_available"
    | "permission_denied"
    | "transport_interrupted"
    | "incompatible_version";
  message: string;
  retryable: boolean;
  details?: Readonly<Record<string, unknown>>;
};

export type Result<T> =
  | { ok: true; value: T }
  | { ok: false; error: ClientFailure };

export type EventEnvelope = {
  schemaVersion: "vg.4";
  eventId: string;
  scope: "episode" | "governance" | "evolution" | "recovery";
  runId?: string;
  episodeId?: string;
  branchId?: string;
  parentEventId?: string;
  traceId: string;
  spanId: string;
  seq: string;
  occurredAt: string;
  recordedAt: string;
  principal: string;
  principalRole?: "user" | "operator" | "episode" | "process" | "evaluator" | "release";
  tenantId: string;
  ownerId: string;
  confidentiality: string;
  retentionClass: string;
  trainability: string;
  redactionStatus: string;
  encryptionKeyRef?: string;
  environmentSnapshot?: string;
  payload: Record<string, unknown> & { kind: string };
  [key: string]: unknown;
};

export type EventCursor = { runId: string; afterSeq?: string };
export type StreamItem = {
  contractVersion: ClientContractVersion;
  source: StreamSource;
  envelope: EventEnvelope;
};

export type StartRunRequest = {
  repo: string;
  runId?: string;
  resumeFrom?: string;
  checkpointEvery?: number;
};

export type RunRef = { runId: string; episodeId?: string };
export type RunSnapshot = { runId: string; status: string; seq: string };
export type CommandReceipt = {
  runId: string;
  command: "cancel" | "checkpoint" | "resume" | "resolve_approval";
  status: "requested";
};
export type ResumeRunRequest = { runId: string; checkpointId?: string };
export type ResolveApprovalRequest = { approvalId: string; decision: "approve" | "reject" };

export type ArtifactExplanation = {
  artifactId: string;
  status: "active" | "inactive" | "unknown";
  prediction: string;
  activatedBy: ReadonlyArray<{ evidence: string; strength?: number }>;
  demotedBy: ReadonlyArray<{ condition: string; effect: string }>;
  freshness: { source: StreamSource; asOfSeq?: string };
};

export interface RuntimeClient {
  startRun(request: StartRunRequest, signal?: AbortSignal): Promise<Result<RunRef>>;
  streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>>;
  getRun(runId: string, signal?: AbortSignal): Promise<Result<RunSnapshot>>;
  requestCancel(runId: string, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  requestCheckpoint(runId: string, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
  requestResume(request: ResumeRunRequest, signal?: AbortSignal): Promise<Result<RunRef>>;
  explainArtifact(artifactId: string, signal?: AbortSignal): Promise<Result<ArtifactExplanation>>;
  resolveApproval(request: ResolveApprovalRequest, signal?: AbortSignal): Promise<Result<CommandReceipt>>;
}
