import { jsonLine } from "../headless/jsonl.js";
import type { RuntimeClient } from "../contract/types.js";

export type CliOptions = {
  headless: boolean;
  runId?: string;
  resumeFrom?: string;
  checkpointEvery?: number;
  repo: string;
  artifact?: string;
  replay?: string;
};

export async function streamRun(client: RuntimeClient, options: CliOptions, write: (line: string) => void): Promise<void> {
  const started = await client.startRun({
    repo: options.repo,
    runId: options.runId,
    resumeFrom: options.resumeFrom,
    checkpointEvery: options.checkpointEvery,
  });
  if (!started.ok && started.error.code !== "not_available") {
    write(jsonLine({ ok: false, error: started.error }));
    return;
  }
  const runId = started.ok ? started.value.runId : options.runId ?? "";
  for await (const result of client.streamEvents({ runId })) {
    if (!result.ok) {
      write(jsonLine({ ok: false, error: result.error }));
      continue;
    }
    write(jsonLine(result.value));
  }
}

export async function streamTrace(client: RuntimeClient, runId: string, write: (line: string) => void): Promise<void> {
  for await (const result of client.streamEvents({ runId })) {
    if (!result.ok) {
      write(jsonLine({ ok: false, error: result.error }));
      continue;
    }
    write(jsonLine(result.value));
  }
}

export async function explain(client: RuntimeClient, artifact: string, write: (line: string) => void): Promise<void> {
  const result = await client.explainArtifact(artifact);
  if (!result.ok) {
    write(jsonLine({ ok: false, error: result.error }));
    return;
  }
  write(jsonLine(result.value));
}
