import { fail, parseJsonlLine } from "../contract/parse.js";
import type {
  EventCursor,
  Result,
  ResumeRunRequest,
  ResolveApprovalRequest,
  RuntimeClient,
  StartRunRequest,
  StreamItem,
} from "../contract/types.js";

function unavailable(method: string): Result<never> {
  return fail("not_available", `${method} is not available on the live adapter until the runtime IPC is connected`, true);
}

export class LiveRuntimeClient implements RuntimeClient {
  constructor(private readonly lines: AsyncIterable<string>) {}

  async startRun(_request: StartRunRequest): Promise<Result<never>> {
    return unavailable("startRun");
  }

  async *streamEvents(_cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
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
      yield { ok: true, value: { contractVersion: "0.1", source: "live", envelope: parsed.value } };
    }
  }

  async getRun(runId: string): Promise<Result<never>> {
    return unavailable(`getRun(${runId})`);
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

  async explainArtifact(artifactId: string): Promise<Result<never>> {
    return unavailable(`explainArtifact(${artifactId})`);
  }

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<never>> {
    return unavailable(`resolveApproval(${request.approvalId})`);
  }
}
