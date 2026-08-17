export function jsonLine(value: unknown): string {
  return JSON.stringify(value);
}
import type { RuntimeClient } from "../contract/types.js";

export type CliOptions = {
  headless: boolean;
  feed?: boolean;
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
  socketPath?: string;
  demo?: boolean;
  demoScenario?: string;
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
  let exitCode = 2; // Default to 2 (error) unless terminal confirmation received
  let seenTerminal = false;

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
      seenTerminal = true;
      const outcome = String(payload.outcome ?? "");
      if (outcome === "satisfied" || outcome === "completed") {
        exitCode = 0;
      } else if (
        outcome === "aborted" ||
        outcome === "cancelled" ||
        outcome === "rejected" ||
        outcome === "denied"
      ) {
        exitCode = 1;
      } else {
        exitCode = 2;
      }
    } else if (kind === "RunAborted" || kind === "ApprovalDenied") {
      seenTerminal = true;
      exitCode = 1;
    } else if (kind === "RunFailed") {
      seenTerminal = true;
      exitCode = 2;
    }
  }

  if (!seenTerminal && exitCode === 2) {
    return 2;
  }

  return exitCode;
}

export async function resumeRun(
  client: RuntimeClient,
  options: CliOptions,
  write: (line: string) => void
): Promise<number> {
  if (!options.runId) {
    write(
      jsonLine({
        ok: false,
        error: { code: "invalid_request", message: "runId required to resume", retryable: false },
      })
    );
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
    return 2;
  }
  write(jsonLine(result.value));
  return decision === "approve" ? 0 : 1;
}

export async function explain(
  client: RuntimeClient,
  artifactId: string,
  write: (line: string) => void
): Promise<number> {
  const result = await client.explainArtifact(artifactId);
  if (!result.ok) {
    write(jsonLine({ ok: false, error: result.error }));
    return 2;
  }
  write(jsonLine(result.value));
  return 0;
}

export async function streamTrace(
  client: RuntimeClient,
  runId: string,
  write: (line: string) => void
): Promise<number> {
  let hasEvents = false;
  for await (const result of client.streamEvents({ runId })) {
    if (!result.ok) {
      write(jsonLine({ ok: false, error: result.error }));
      return 2;
    }
    hasEvents = true;
    write(jsonLine(result.value));
  }
  return hasEvents ? 0 : 2;
}

const J1_MESSAGE =
  "Daemon self-launch is not available until Joint note J1 (the RuntimeService server module has no __main__). Start the RuntimeService process yourself, then use vg daemon status.";

export async function manageDaemon(
  client: RuntimeClient,
  action: "start" | "status" | "stop",
  write: (line: string) => void
): Promise<number> {
  if (action === "start" || action === "stop") {
    write(
      jsonLine({
        ok: false,
        error: { code: "not_available", message: J1_MESSAGE, retryable: false, details: { joint: "J1", action } },
      })
    );
    return 2;
  }
  const status = await client.getDaemonStatus();
  if (!status.ok) {
    write(jsonLine({ ok: false, error: status.error }));
    return 2;
  }
  write(jsonLine({ action, ...status.value }));
  return status.value.status === "running" ? 0 : 1;
}
