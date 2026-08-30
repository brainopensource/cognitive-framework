import type {
  ArtifactExplanation,
  CancelOptions,
  CheckpointOptions,
  CommandReceipt,
  DaemonStatus,
  EventCursor,
  ExplainArtifactOptions,
  ListRunsOptions,
  RecordCorrectionRequest,
  ResolveApprovalRequest,
  Result,
  ResumeOptions,
  RunRef,
  RunSnapshot,
  RunSummary,
  StartRunRequest,
  StreamItem,
} from "@aether/contracts";

export interface RuntimeClient {
  startRun(request: StartRunRequest, signal?: AbortSignal): Promise<Result<RunRef>>;
  getRun(runId: string, expectedSeq?: string | number): Promise<Result<RunSnapshot>>;
  listRuns(options?: ListRunsOptions): Promise<Result<RunSummary[]>>;
  streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>>;
  requestCancel(runId: string, options?: CancelOptions): Promise<Result<CommandReceipt>>;
  requestCheckpoint(runId: string, options?: CheckpointOptions): Promise<Result<CommandReceipt>>;
  requestResume(runId: string, options?: ResumeOptions): Promise<Result<CommandReceipt>>;
  resolveApproval(request: ResolveApprovalRequest): Promise<Result<CommandReceipt>>;
  recordCorrection(request: RecordCorrectionRequest): Promise<Result<CommandReceipt>>;
  explainArtifact(artifactId: string, options?: ExplainArtifactOptions): Promise<Result<ArtifactExplanation>>;
  getCapabilities(): Promise<Result<Record<string, unknown>>>;
  getDaemonStatus(): Promise<Result<DaemonStatus>>;
}
