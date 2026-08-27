import { fail, parseEventEnvelope, toClientFailureCode } from "../contract/parse.js";
import type {
  ApprovalChallenge,
  ArtifactExplanation,
  CommandReceipt,
  CorrectionRecord,
  DaemonStatus,
  EventCursor,
  ResolveApprovalRequest,
  Result,
  ResumeRunRequest,
  RunRef,
  RunSnapshot,
  RuntimeClient,
  StartRunRequest,
  StreamItem,
} from "../contract/types.js";
import { OperatorSigner } from "./signer.js";

export type HttpTransportOptions = {
  baseUrl?: string;
  retryAttempts?: number;
  retryBaseMs?: number;
  headers?: Record<string, string>;
  signer?: OperatorSigner;
};

/** Shape every RuntimeService command route returns via `_send_json_response(execute_command(...))`. */
type WireReceiptFrame = {
  frameType?: string;
  receipt?: {
    status?: string;
    result?: Record<string, unknown>;
    detail?: string;
    error?: { code?: unknown; message?: unknown; retryable?: unknown };
  };
  error?: { code?: unknown; message?: unknown; retryable?: unknown };
};

function challengeFromPayload(payload: Record<string, unknown>): ApprovalChallenge | undefined {
  const approvalId = payload.approvalId;
  if (typeof approvalId !== "string") return undefined;
  return {
    approvalId,
    processId: String(payload.processId ?? ""),
    action: String(payload.action ?? ""),
    normalizedDiff: String(payload.normalizedDiff ?? payload.unifiedDiff ?? payload.diff ?? ""),
    argsDigest: typeof payload.argsDigest === "string" ? payload.argsDigest : "",
    descriptorDigest: typeof payload.descriptorDigest === "string" ? payload.descriptorDigest : "",
    principal: String(payload.principal ?? "operator"),
    expiresAt: typeof payload.expiresAt === "string" ? payload.expiresAt : "",
  };
}

export class HttpRuntimeClient implements RuntimeClient {
  private readonly baseUrl: string;
  private readonly retryAttempts: number;
  private readonly retryBaseMs: number;
  private readonly headers: Record<string, string>;
  private readonly signer: OperatorSigner | undefined;
  private currentRunId = "";
  private lastChallenge: ApprovalChallenge | undefined;

  constructor(options?: HttpTransportOptions) {
    this.baseUrl = options?.baseUrl ?? "http://localhost:8080";
    this.retryAttempts = options?.retryAttempts ?? 3;
    this.retryBaseMs = options?.retryBaseMs ?? 1000;
    this.headers = { "Content-Type": "application/json", ...options?.headers };
    this.signer = options?.signer;
  }

  private async fetchWithRetry(url: string, init?: RequestInit): Promise<Response> {
    let attempt = 0;
    while (true) {
      try {
        const response = await fetch(url, init);
        if (response.ok || (response.status >= 400 && response.status < 500)) {
          return response;
        }
        throw new Error(`HTTP ${response.status}`);
      } catch (error) {
        attempt++;
        if (attempt > this.retryAttempts || init?.signal?.aborted) {
          throw error;
        }
        await new Promise((r) => setTimeout(r, this.retryBaseMs * Math.pow(2, attempt - 1)));
      }
    }
  }

  /** Parse a `RuntimeService` command receipt/error frame into a typed `Result`. */
  private async parseCommandResponse<T>(response: Response): Promise<Result<T>> {
    let body: WireReceiptFrame;
    try {
      body = (await response.json()) as WireReceiptFrame;
    } catch {
      return fail("internal", "gateway returned non-JSON response");
    }
    if (body.frameType === "error" || (!response.ok && body.error)) {
      const err = body.error ?? {};
      return fail(toClientFailureCode(err.code), typeof err.message === "string" ? err.message : "gateway error", Boolean(err.retryable));
    }
    const receipt = body.receipt;
    if (!receipt) {
      return fail("internal", "gateway response missing receipt");
    }
    if (receipt.status === "error") {
      const err = receipt.error ?? {};
      const message = typeof err.message === "string" ? err.message : receipt.detail ?? "command failed";
      return fail(toClientFailureCode(err.code), message, Boolean(err.retryable));
    }
    return { ok: true, value: (receipt.result ?? {}) as T };
  }

  async startRun(request: StartRunRequest, signal?: AbortSignal): Promise<Result<RunRef>> {
    try {
      const runId = request.runId ?? `run-${Date.now()}`;
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/v1/runs`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({
          runId,
          manifestPath: request.manifest ?? "harness.yaml",
          repoPath: request.repo,
          brief: request.brief ?? request.prompt ?? "run",
        }),
        signal,
      });
      const result = await this.parseCommandResponse<{ runId: string }>(response);
      if (!result.ok) return result;
      this.currentRunId = result.value.runId || runId;
      return { ok: true, value: { runId: this.currentRunId } };
    } catch (e) {
      return fail("transport_interrupted", e instanceof Error ? e.message : String(e), true);
    }
  }

  async *streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    this.currentRunId = cursor.runId;
    let afterSeq = cursor.afterSeq ? BigInt(cursor.afterSeq) : undefined;
    let attempt = 0;

    while (true) {
      if (signal?.aborted) {
        yield fail("transport_interrupted", "stream aborted", true);
        return;
      }

      try {
        const query = afterSeq !== undefined ? `?afterSeq=${afterSeq.toString()}` : "";
        const response = await fetch(`${this.baseUrl}/api/v1/runs/${encodeURIComponent(cursor.runId)}/events:stream${query}`, {
          headers: {
            ...this.headers,
            Accept: "text/event-stream",
            ...(afterSeq !== undefined ? { "Last-Event-ID": afterSeq.toString() } : {}),
          },
          signal,
        });

        if (!response.ok || !response.body) {
          throw new Error(`HTTP ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            if (signal?.aborted) {
              yield fail("transport_interrupted", "stream aborted", true);
              return;
            }
            if (!line.startsWith("data: ")) continue;
            const dataStr = line.slice(6).trim();
            if (!dataStr) continue;

            let parsedData: unknown;
            try {
              parsedData = JSON.parse(dataStr);
            } catch {
              continue;
            }

            const frameLike = parsedData as { event?: unknown };
            const rawEnvelope = frameLike && typeof frameLike === "object" && "event" in frameLike ? frameLike.event : parsedData;
            const parsedEvent = parseEventEnvelope(rawEnvelope);
            if (!parsedEvent.ok) {
              yield parsedEvent;
              continue;
            }
            const seq = BigInt(parsedEvent.value.seq);
            if (afterSeq !== undefined && seq <= afterSeq) continue;
            afterSeq = seq;
            if (parsedEvent.value.payload.kind === "ApprovalRequested") {
              this.lastChallenge = challengeFromPayload(parsedEvent.value.payload);
            }
            yield { ok: true, value: { contractVersion: "0.1", source: "live", envelope: parsedEvent.value } };
          }
        }

        attempt++;
        if (attempt > this.retryAttempts) break;
        await new Promise((r) => setTimeout(r, this.retryBaseMs * Math.pow(2, attempt - 1)));
      } catch (e) {
        if ((e instanceof Error && e.name === "AbortError") || signal?.aborted) {
          yield fail("transport_interrupted", "stream aborted", true);
          return;
        }
        attempt++;
        if (attempt > this.retryAttempts) {
          yield fail("transport_interrupted", e instanceof Error ? e.message : String(e), true);
          return;
        }
        await new Promise((r) => setTimeout(r, this.retryBaseMs * Math.pow(2, attempt - 1)));
      }
    }
  }

  async getRun(runId: string, signal?: AbortSignal): Promise<Result<RunSnapshot>> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/v1/runs/${encodeURIComponent(runId)}`, {
        headers: this.headers,
        signal,
      });
      const result = await this.parseCommandResponse<{ status?: string; asOfSeq?: string; eventCount?: number }>(response);
      if (!result.ok) return result;
      return {
        ok: true,
        value: {
          runId,
          status: result.value.status ?? "unknown",
          seq: result.value.asOfSeq ?? String(result.value.eventCount ?? 0),
        },
      };
    } catch (e) {
      return fail("transport_interrupted", e instanceof Error ? e.message : String(e), true);
    }
  }

  async requestCancel(runId: string, signal?: AbortSignal): Promise<Result<CommandReceipt>> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/v1/runs/${encodeURIComponent(runId)}:cancel`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({}),
        signal,
      });
      const result = await this.parseCommandResponse<Record<string, unknown>>(response);
      if (!result.ok) return result;
      return { ok: true, value: { runId, command: "cancel", status: "accepted" } };
    } catch (e) {
      return fail("transport_interrupted", e instanceof Error ? e.message : String(e), true);
    }
  }

  async requestCheckpoint(runId: string, signal?: AbortSignal): Promise<Result<CommandReceipt>> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/v1/runs/${encodeURIComponent(runId)}:checkpoint`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({}),
        signal,
      });
      const result = await this.parseCommandResponse<Record<string, unknown>>(response);
      if (!result.ok) return result;
      return { ok: true, value: { runId, command: "checkpoint", status: "accepted" } };
    } catch (e) {
      return fail("transport_interrupted", e instanceof Error ? e.message : String(e), true);
    }
  }

  async requestResume(request: ResumeRunRequest, signal?: AbortSignal): Promise<Result<RunRef>> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/v1/runs/${encodeURIComponent(request.runId)}:resume`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify(request.checkpointId ? { checkpointId: request.checkpointId } : {}),
        signal,
      });
      const result = await this.parseCommandResponse<Record<string, unknown>>(response);
      if (!result.ok) return result;
      return { ok: true, value: { runId: request.runId } };
    } catch (e) {
      return fail("transport_interrupted", e instanceof Error ? e.message : String(e), true);
    }
  }

  async explainArtifact(_artifactId: string, _signal?: AbortSignal): Promise<Result<ArtifactExplanation>> {
    return fail("not_available", "explainArtifact has no HTTP gateway route yet");
  }

  async resolveApproval(request: ResolveApprovalRequest, signal?: AbortSignal): Promise<Result<CommandReceipt>> {
    const challenge = this.lastChallenge;
    if (!challenge || challenge.approvalId !== request.approvalId) {
      return fail("not_available", "no ApprovalRequested challenge with digests is loaded (Joint J4)", false);
    }
    if (!challenge.argsDigest || !challenge.descriptorDigest || !challenge.expiresAt) {
      return fail("not_available", "approval challenge digests are empty (Joint J4)", false);
    }
    try {
      const signer = this.signer ?? OperatorSigner.loadOrCreate();
      const decision = signer.signChallenge(
        challenge,
        request.decision === "approve" ? "approved" : "rejected",
        "operator"
      );
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/approvals/resolve`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({ ...decision, runId: this.currentRunId }),
        signal,
      });
      const result = await this.parseCommandResponse<Record<string, unknown>>(response);
      if (!result.ok) return result;
      return { ok: true, value: { runId: this.currentRunId, command: "resolve_approval", status: "accepted" } };
    } catch (e) {
      return fail("transport_interrupted", e instanceof Error ? e.message : String(e), true);
    }
  }

  async recordCorrection(_record: CorrectionRecord, _signal?: AbortSignal): Promise<Result<CommandReceipt>> {
    // studio_gateway.py has no RecordCorrection HTTP route yet (only UDS exposes it).
    // Reporting not_available here is the honest answer; a fabricated 200 would not be.
    return fail("not_available", "recordCorrection has no HTTP gateway route yet");
  }

  async getDaemonStatus(signal?: AbortSignal): Promise<Result<DaemonStatus>> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/v1/health`, {
        headers: this.headers,
        signal,
      });
      const data = (await response.json()) as { version?: string };
      if (!response.ok) {
        return fail("not_available", "Daemon is unreachable");
      }
      return {
        ok: true,
        value: {
          status: "running",
          socketPath: "http",
          version: data.version,
        },
      };
    } catch (e) {
      return fail("transport_interrupted", e instanceof Error ? e.message : String(e), true);
    }
  }
}
