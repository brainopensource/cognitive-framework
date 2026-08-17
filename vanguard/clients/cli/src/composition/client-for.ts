import {
  attachLive,
  LiveRuntimeClient,
  OperatorSigner,
  ReplayRuntimeClient,
  ScenarioRuntimeClient,
  type CliOptions,
  type RuntimeClient,
} from "@vanguard/client-core";
import { demoFixturePath, packageRootFrom } from "./catalog.js";

async function* stdinLines(): AsyncIterable<string> {
  let buffer = "";
  for await (const chunk of process.stdin) {
    buffer += String(chunk);
    const parts = buffer.split(/\r?\n/);
    buffer = parts.pop() ?? "";
    for (const line of parts) if (line.trim()) yield line;
  }
  if (buffer.trim()) yield buffer;
}

/** --demo/--replay/--scenario = mock; --feed = stdin NDJSON; else attachLive (no fixture fallback). */
export function clientFor(parsed: CliOptions): RuntimeClient {
  if (parsed.demo) {
    const scenario = parsed.demoScenario ?? "successful-episode";
    const path = demoFixturePath(packageRootFrom(import.meta.url), scenario);
    return ReplayRuntimeClient.fromFile(path, "mock");
  }
  if (parsed.replay) return ReplayRuntimeClient.fromFile(parsed.replay);
  if (parsed.scenario) return new ScenarioRuntimeClient();
  if (parsed.feed) {
    return new LiveRuntimeClient(stdinLines(), {
      repo: parsed.repo,
      prompt: parsed.prompt,
      model: parsed.model,
    });
  }
  return attachLive({
    repo: parsed.repo,
    model: parsed.model,
    socketPath: parsed.socketPath,
    manifest: parsed.manifest,
    signer: OperatorSigner.loadOrCreate(),
  });
}
