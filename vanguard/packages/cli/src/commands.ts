import type { RuntimePort, RunRequest } from "./runtime.js";
import { jsonLine } from "./runtime.js";

export type CliOptions = { headless: boolean; runId?: string; resumeFrom?: string; checkpointEvery?: number; repo: string; artifact?: string };

export async function streamRun(runtime: RuntimePort, options: CliOptions, write: (line: string) => void): Promise<void> {
  const source = options.resumeFrom ? runtime.resume(options.resumeFrom) : runtime.run({ repo: options.repo, runId: options.runId, resumeFrom: options.resumeFrom, checkpointEvery: options.checkpointEvery } satisfies RunRequest);
  for await (const event of source) write(jsonLine(event));
}

export async function streamTrace(runtime: RuntimePort, runId: string, write: (line: string) => void): Promise<void> {
  for await (const event of runtime.trace(runId)) write(jsonLine(event));
}

export async function explain(runtime: RuntimePort, artifact: string, write: (line: string) => void): Promise<void> {
  write(jsonLine(await runtime.why(artifact)));
}
