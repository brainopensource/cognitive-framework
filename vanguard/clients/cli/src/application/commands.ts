import { jsonLine } from "../headless/jsonl.js";
import type { RuntimeClient } from "../contract/types.js";

export type CliOptions = {
  headless: boolean;
  prompt?: string;
  brief?: string;
  runId?: string;
  resumeFrom?: string;
  checkpointEvery?: number;
  repo: string;
  artifact?: string;
  replay?: string;
  scenario?: boolean;
  model?: string;
  manifest?: string;
  decision?: "approve" | "reject";
  autoApprove?: boolean;
};

export async function streamRun(
  client: RuntimeClient,
  options: CliOptions,
  write: (line: string) => void
): Promise<number> {
  const started = await client.startRun({
    repo: options.repo,
    prompt: options.prompt ?? options.brief,
    brief: options.prompt ?? options.brief,
    runId: options.runId,
    resumeFrom: options.resumeFrom,
    checkpointEvery: options.checkpointEvery,
    model: options.model,
    manifest: options.manifest,
    autoApprove: options.autoApprove,
  });

  if (!started.ok) {
    write(jsonLine({ ok: false, error: started.error }));
    return 2;
  }

  const runId = started.value.runId;
  let exitCode = 0;

  for await (const result of client.streamEvents({ runId })) {
    if (!result.ok) {
      write(jsonLine({ ok: false, error: result.error }));
      exitCode = 2;
      continue;
    }
    write(jsonLine(result.value));
    const kind = result.value.envelope.payload.kind;
    const payload = result.value.envelope.payload;

    if (kind === "EpisodeCompleted") {
      const outcome = String(payload.outcome ?? "");
      if (outcome === "satisfied" || outcome === "completed") {
        exitCode = 0;
      } else if (outcome === "aborted" || outcome === "cancelled" || outcome === "rejected" || outcome === "denied") {
        exitCode = 1;
      } else {
        exitCode = 2;
      }
    } else if (kind === "RunAborted" || kind === "ApprovalDenied") {
      exitCode = 1;
    }
  }

  return exitCode;
}

export async function resumeRun(
  client: RuntimeClient,
  options: CliOptions,
  write: (line: string) => void
): Promise<number> {
  if (!options.runId) {
    write(jsonLine({ ok: false, error: { code: "invalid_request", message: "runId required to resume", retryable: false } }));
    return 2;
  }
  const resumed = await client.requestResume({ runId: options.runId, checkpointId: options.resumeFrom });
  if (!resumed.ok) {
    write(jsonLine({ ok: false, error: resumed.error }));
    return 2;
  }

  return streamRun(client, { ...options, runId: resumed.value.runId }, write);
}

export async function approveDecision(
  client: RuntimeClient,
  runId: string,
  decision: "approve" | "reject",
  write: (line: string) => void
): Promise<number> {
  const result = await client.resolveApproval({ approvalId: runId, decision });
  if (!result.ok) {
    write(jsonLine({ ok: false, error: result.error }));
    return decision === "reject" ? 1 : 2;
  }
  write(jsonLine(result.value));
  return decision === "approve" ? 0 : 1;
}

export async function streamTrace(
  client: RuntimeClient,
  runId: string,
  write: (line: string) => void
): Promise<number> {
  for await (const result of client.streamEvents({ runId })) {
    if (!result.ok) {
      write(jsonLine({ ok: false, error: result.error }));
      return 2;
    }
    write(jsonLine(result.value));
  }
  return 0;
}

export async function explain(
  client: RuntimeClient,
  artifact: string,
  write: (line: string) => void
): Promise<number> {
  const result = await client.explainArtifact(artifact);
  if (!result.ok) {
    write(jsonLine({ ok: false, error: result.error }));
    return 2;
  }
  write(jsonLine(result.value));
  return 0;
}

export async function manageDaemon(
  client: RuntimeClient,
  action: "start" | "status" | "stop",
  write: (line: string) => void
): Promise<number> {
  const status = await client.getDaemonStatus();
  if (!status.ok) {
    write(jsonLine({ ok: false, error: status.error }));
    return 2;
  }
  write(jsonLine({ command: `daemon_${action}`, ...status.value }));
  return 0;
}

