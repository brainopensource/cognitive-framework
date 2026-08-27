import { fail, parseEventEnvelope } from "../contract/parse.js";
import type {
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

export type HttpTransportOptions = {
  baseUrl?: string;
  retryAttempts?: number;
  retryBaseMs?: number;
  headers?: Record<string, string>;
};

export class HttpRuntimeClient implements RuntimeClient {
  private readonly baseUrl: string;
  private readonly retryAttempts: number;
  private readonly retryBaseMs: number;
  private readonly headers: Record<string, string>;

  constructor(options?: HttpTransportOptions) {
    this.baseUrl = options?.baseUrl ?? "http://localhost:8080";
    this.retryAttempts = options?.retryAttempts ?? 3;
    this.retryBaseMs = options?.retryBaseMs ?? 1000;
    this.headers = { "Content-Type": "application/json", ...options?.headers };
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

  async startRun(request: StartRunRequest, signal?: AbortSignal): Promise<Result<RunRef>> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/runs/launch`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify(request),
        signal,
      });
      const data = (await response.json()) as { error?: string; runId?: string };
      if (!response.ok) {
        return fail("invalid_request", data.error || "Failed to start run");
      }
      return { ok: true, value: { runId: data.runId! } };
    } catch (e: any) {
      return fail("transport_interrupted", e.message, true);
    }
  }

  async *streamEvents(cursor: EventCursor, signal?: AbortSignal): AsyncIterable<Result<StreamItem>> {
    let afterSeq = cursor.afterSeq ? BigInt(cursor.afterSeq) : undefined;
    let attempt = 0;

    while (true) {
      if (signal?.aborted) {
        yield fail("transport_interrupted", "stream aborted", true);
        return;
      }

      try {
        const response = await fetch(`${this.baseUrl}/api/events/stream?runId=${cursor.runId}`, {
          headers: { ...this.headers, Accept: "text/event-stream" },
          signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        if (!response.body) {
          throw new Error("No response body");
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

            if (parsedData && typeof parsedData === "object" && "payload" in parsedData) {
              const parsedEvent = parseEventEnvelope(parsedData);
              if (parsedEvent.ok) {
                const seq = BigInt(parsedEvent.value.seq);
                if (afterSeq !== undefined && seq <= afterSeq) continue;
                afterSeq = seq;
                yield { ok: true, value: { contractVersion: "0.1", source: "live", envelope: parsedEvent.value } };
              } else {
                yield parsedEvent;
              }
            }
          }
        }

        attempt++;
        if (attempt > this.retryAttempts) break;
        await new Promise((r) => setTimeout(r, this.retryBaseMs * Math.pow(2, attempt - 1)));
      } catch (e: any) {
        if (e.name === "AbortError" || signal?.aborted) {
          yield fail("transport_interrupted", "stream aborted", true);
          return;
        }
        attempt++;
        if (attempt > this.retryAttempts) {
          yield fail("transport_interrupted", e.message, true);
          return;
        }
        await new Promise((r) => setTimeout(r, this.retryBaseMs * Math.pow(2, attempt - 1)));
      }
    }
  }

  async getRun(runId: string, signal?: AbortSignal): Promise<Result<RunSnapshot>> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/runs`, {
        headers: this.headers,
        signal,
      });
      if (!response.ok) {
        return fail("not_found", "Failed to get run");
      }
      return { ok: true, value: { runId, status: "unknown", seq: "0" } };
    } catch (e: any) {
      return fail("transport_interrupted", e.message, true);
    }
  }

  async requestCancel(_runId: string, _signal?: AbortSignal): Promise<Result<CommandReceipt>> {
    return fail("not_available", "requestCancel not implemented on http gateway");
  }

  async requestCheckpoint(_runId: string, _signal?: AbortSignal): Promise<Result<CommandReceipt>> {
    return fail("not_available", "requestCheckpoint not implemented on http gateway");
  }

  async requestResume(_request: ResumeRunRequest, _signal?: AbortSignal): Promise<Result<RunRef>> {
    return fail("not_available", "requestResume not implemented on http gateway");
  }

  async explainArtifact(_artifactId: string, _signal?: AbortSignal): Promise<Result<ArtifactExplanation>> {
    return fail("not_available", "explainArtifact not implemented on http gateway");
  }

  async resolveApproval(request: ResolveApprovalRequest, signal?: AbortSignal): Promise<Result<CommandReceipt>> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/approvals/resolve`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify(request),
        signal,
      });
      const data = (await response.json()) as { error?: string; approvalId?: string };
      if (!response.ok) {
        return fail("invalid_request", data.error || "Failed to resolve approval");
      }
      return { ok: true, value: { runId: data.approvalId!, command: "resolve_approval", status: "requested" } };
    } catch (e: any) {
      return fail("transport_interrupted", e.message, true);
    }
  }

  async recordCorrection(_record: CorrectionRecord, _signal?: AbortSignal): Promise<Result<CommandReceipt>> {
    return fail("not_available", "recordCorrection not implemented on http gateway");
  }

  async getDaemonStatus(signal?: AbortSignal): Promise<Result<DaemonStatus>> {
    try {
      const response = await this.fetchWithRetry(`${this.baseUrl}/api/health`, {
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
    } catch (e: any) {
      return fail("transport_interrupted", e.message, true);
    }
  }
}
