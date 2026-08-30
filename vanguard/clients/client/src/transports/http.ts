import {
  fail,
  parseEventEnvelope,
  toClientFailureCode,
  type ApprovalChallenge,
  type ApprovalDecision,
  type ArtifactExplanation,
  type CancelOptions,
  type CheckpointOptions,
  type CommandReceipt,
  type DaemonStatus,
  type EventCursor,
  type ExplainArtifactOptions,
  type ListRunsOptions,
  type RecordCorrectionRequest,
  type ResolveApprovalRequest,
  type Result,
  type ResumeOptions,
  type RunRef,
  type RunSnapshot,
  type RunSummary,
  type ServiceError,
  type SignerPort,
  type StartRunRequest,
  type StreamItem,
} from "@aether/contracts";
import type { RuntimeClient } from "../client.js";

export type HttpTransportOptions = {
  baseUrl?: string;
  retryAttempts?: number;
  retryBaseMs?: number;
  headers?: Record<string, string>;
  signer?: SignerPort;
};

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
  private readonly signer: SignerPort | undefined;
  private currentRunId = "";
  private lastChallenge: ApprovalChallenge | undefined;

  constructor(options?: HttpTransportOptions) {
    this.baseUrl = (options?.baseUrl ?? "http://127.0.0.1:8080").replace(/\/$/, "");
    this.retryAttempts = options?.retryAttempts ?? 3;
    this.retryBaseMs = options?.retryBaseMs ?? 200;
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

  private async parseCommandResponse<T>(response: Response): Promise<Result<T>> {
    let body: WireReceiptFrame;
    try {
      body = (await response.json()) as WireReceiptFrame;
    } catch {
      return fail("internal", "Gateway returned non-JSON response");
    }
    if (body.frameType === "error" || (!response.ok && body.error)) {
      const err = body.error ?? {};
      const code = toClientFailureCode(err.code);
      return fail(code, String(err.message ?? "Command execution failed"), Boolean(err.retryable));
    }
    if (body.receipt?.status === "error" && body.receipt.error) {
      const err = body.receipt.error;
      const code = toClientFailureCode(err.code);
      return fail(code, String(err.message ?? "Command receipt error"), Boolean(err.retryable));
    }
    const res = (body.receipt?.result ?? body.receipt ?? body) as T;
    return { ok: true, value: res };
  }

  async startRun(request: StartRunRequest, signal?: AbortSignal): Promise<Result<RunRef>> {
    const runId = request.runId ?? `run-http-${Date.now()}`;
    this.currentRunId = runId;
    const body = {
      manifestPath: request.manifestPath ?? request.repo ?? request.repoPath ?? ".",
      repoPath: request.repoPath ?? request.repo ?? ".",
      brief: request.brief ?? request.prompt ?? "Execute task",
      profileId: request.profileId ?? request.profile,
      model: request.model,
      episodeId: request.episodeId,
      runId,
    };
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/runs/launch`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify(body),
        signal,
      });
      const parsed = await this.parseCommandResponse<{ runId?: string; episodeId?: string }>(response);
      if (!parsed.ok) return parsed;
      return {
        ok: true,
        value: {
          runId: parsed.value.runId ?? runId,
          episodeId: parsed.value.episodeId,
        },
      };
    } catch (err) {
      return fail("not_available", `Failed to reach runtime at ${this.baseUrl}: ${String(err)}`, true);
    }
  }

  async getRun(runId: string, expectedSeq?: string | number): Promise<Result<RunSnapshot>> {
    try {
      const url = `${this.baseUrl}/api/runs/${encodeURIComponent(runId)}`;
      const response = await this.fetchWithRetry(url, { headers: this.headers });
      const parsed = await this.parseCommandResponse<{
        runId?: string;
        status?: string;
        seq?: string;
        verdict?: string;
        metrics?: Record<string, unknown>;
      }>(response);
      if (!parsed.ok) return parsed;
      return {
        ok: true,
        value: {
          runId: parsed.value.runId ?? runId,
          status: parsed.value.status ?? "running",
          seq: String(parsed.value.seq ?? "0"),
          verdict: parsed.value.verdict,
          metrics: parsed.value.metrics,
        },
      };
    } catch (err) {
      return fail("not_available", `Failed to get run ${runId}: ${String(err)}`, true);
    }
  }

  async listRuns(options: ListRunsOptions = {}): Promise<Result<RunSummary[]>> {
    try {
      const params = new URLSearchParams();
      if (options.limit !== undefined) params.set("limit", String(options.limit));
      if (options.offset !== undefined) params.set("offset", String(options.offset));
      const url = `${this.baseUrl}/api/runs?${params.toString()}`;
      const response = await this.fetchWithRetry(url, { headers: this.headers });
      const parsed = await this.parseCommandResponse<{ runs?: RunSummary[] }>(response);
      if (!parsed.ok) return parsed;
      return {
        ok: true,
        value: Array.isArray(parsed.value.runs) ? parsed.value.runs : [],
      };
    } catch (err) {
      return fail("not_available", `Failed to list runs: ${String(err)}`, true);
    }
  }

  async *streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    const runId = cursor.runId || this.currentRunId;
    const url = new URL(`${this.baseUrl}/api/v1/runs/${encodeURIComponent(runId)}/events:stream`);
    if (cursor.afterSeq !== undefined) {
      url.searchParams.set("afterSeq", String(cursor.afterSeq));
    }

    let response: Response;
    try {
      response = await this.fetchWithRetry(url.toString(), {
        headers: { Accept: "text/event-stream" },
        signal,
      });
    } catch (err) {
      yield fail("not_available", `Cannot connect to event stream: ${String(err)}`, true);
      return;
    }

    if (!response.ok || !response.body) {
      yield fail("not_available", `Stream failed with HTTP ${response.status}`, true);
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        if (signal?.aborted) {
          yield fail("transport_interrupted", "Stream aborted by caller", true);
          return;
        }

        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed || trimmed.startsWith(":")) continue;
          if (trimmed.startsWith("data: ")) {
            const rawJson = trimmed.slice(6);
            try {
              const eventObj = JSON.parse(rawJson);
              const envRes = parseEventEnvelope(eventObj.event ?? eventObj);
              if (envRes.ok) {
                const env = envRes.value;
                if (env.payload.kind === "ApprovalRequested") {
                  const ch = challengeFromPayload(env.payload);
                  if (ch) this.lastChallenge = ch;
                }
                yield {
                  ok: true,
                  value: {
                    contractVersion: "vg.4",
                    source: "live",
                    envelope: env,
                  },
                };
              }
            } catch {
              /* ignore malformed frame in stream */
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  async requestCancel(runId: string, options: CancelOptions = {}): Promise<Result<CommandReceipt>> {
    try {
      const url = `${this.baseUrl}/api/runs/${encodeURIComponent(runId)}:cancel`;
      const response = await this.fetchWithRetry(url, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({ reason: options.reason ?? "Operator cancelled" }),
      });
      return this.parseCommandResponse<CommandReceipt>(response);
    } catch (err) {
      return fail("not_available", `Failed to cancel run ${runId}: ${String(err)}`, true);
    }
  }

  async requestCheckpoint(runId: string, options: CheckpointOptions = {}): Promise<Result<CommandReceipt>> {
    try {
      const url = `${this.baseUrl}/api/runs/${encodeURIComponent(runId)}:checkpoint`;
      const response = await this.fetchWithRetry(url, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({ reason: options.reason }),
      });
      return this.parseCommandResponse<CommandReceipt>(response);
    } catch (err) {
      return fail("not_available", `Failed to checkpoint run ${runId}: ${String(err)}`, true);
    }
  }

  async requestResume(runId: string, options: ResumeOptions = {}): Promise<Result<CommandReceipt>> {
    try {
      const url = `${this.baseUrl}/api/runs/${encodeURIComponent(runId)}:resume`;
      const response = await this.fetchWithRetry(url, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({ checkpointId: options.checkpointId }),
      });
      return this.parseCommandResponse<CommandReceipt>(response);
    } catch (err) {
      return fail("not_available", `Failed to resume run ${runId}: ${String(err)}`, true);
    }
  }

  async resolveApproval(request: ResolveApprovalRequest): Promise<Result<CommandReceipt>> {
    let decision: ApprovalDecision;
    if (typeof request.decision === "object") {
      decision = request.decision;
    } else {
      if (!this.lastChallenge) {
        return fail("invalid_request", "No pending approval challenge cached for signing");
      }
      if (!this.signer) {
        return fail("permission_denied", "No signer configured to resolve approval");
      }
      const resolution = request.decision === "reject" ? "rejected" : "approved";
      decision = await this.signer.signChallenge(this.lastChallenge, resolution);
    }

    try {
      const url = `${this.baseUrl}/api/approvals/resolve`;
      const response = await this.fetchWithRetry(url, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({ decision }),
      });
      return this.parseCommandResponse<CommandReceipt>(response);
    } catch (err) {
      return fail("not_available", `Failed to resolve approval: ${String(err)}`, true);
    }
  }

  async recordCorrection(request: RecordCorrectionRequest): Promise<Result<CommandReceipt>> {
    try {
      const url = `${this.baseUrl}/api/corrections/record`;
      const response = await this.fetchWithRetry(url, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({ correction: request.correction }),
      });
      return this.parseCommandResponse<CommandReceipt>(response);
    } catch (err) {
      return fail("not_available", `Failed to record correction: ${String(err)}`, true);
    }
  }

  async explainArtifact(artifactId: string, options: ExplainArtifactOptions = {}): Promise<Result<ArtifactExplanation>> {
    try {
      const url = `${this.baseUrl}/api/artifacts/${encodeURIComponent(artifactId)}:explain`;
      const response = await this.fetchWithRetry(url, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify({ substrateProfile: options.substrateProfile }),
      });
      return this.parseCommandResponse<ArtifactExplanation>(response);
    } catch (err) {
      return fail("not_available", `Failed to explain artifact ${artifactId}: ${String(err)}`, true);
    }
  }

  async getCapabilities(): Promise<Result<Record<string, unknown>>> {
    try {
      const url = `${this.baseUrl}/api/capabilities`;
      const response = await this.fetchWithRetry(url, { headers: this.headers });
      return this.parseCommandResponse<Record<string, unknown>>(response);
    } catch (err) {
      return fail("not_available", `Failed to get capabilities: ${String(err)}`, true);
    }
  }

  async getDaemonStatus(): Promise<Result<DaemonStatus>> {
    try {
      const url = `${this.baseUrl}/api/health`;
      const response = await this.fetchWithRetry(url, { headers: this.headers });
      if (!response.ok) {
        return fail("not_available", `HTTP health probe returned status ${response.status}`, true);
      }
      return {
        ok: true,
        value: {
          status: "running",
          socketPath: this.baseUrl,
        },
      };
    } catch (err) {
      return fail("not_available", `Daemon probe failed: ${String(err)}`, true);
    }
  }
}
