import { readFileSync } from "node:fs";
import {
  ManagedRuntimeHost,
  OperatorSigner,
  ProductPaths,
  ReplayRuntimeClient,
  ScenarioRuntimeClient,
  SocketRuntimeClient,
  resolveSocketPath,
  type RuntimeClient,
} from "@aether/client";
import { parseJsonlLine, type EventEnvelope } from "@aether/contracts";
import { demoFixturePath, packageRootFrom } from "./catalog.js";
import type { CliOptions } from "../application/commands.js";

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

function envelopesFromFile(path: string): EventEnvelope[] {
  const text = readFileSync(path, "utf8");
  const envelopes: EventEnvelope[] = [];
  for (const line of text.split(/\r?\n/)) {
    if (!line.trim()) continue;
    const parsed = parseJsonlLine(line);
    if (!parsed.ok) throw new Error(parsed.error.message);
    envelopes.push(parsed.value);
  }
  return envelopes;
}

/**
 * Live attach, ported off @vanguard/client-core's attachLive (F4 Phase 5).
 *
 * Two distinct contracts, chosen by `headless`:
 *  - headless (scripting/CI/automation): fail-fast, zero side effects. Just
 *    connects to whatever's at socketPath; if nothing's listening, every
 *    command reports not_available honestly -- exactly attachLive's old
 *    behavior. Never spawns a process; a script that didn't ask for a
 *    daemon must never get a side effect it didn't ask for.
 *  - interactive (TUI): ManagedRuntimeHost attaches to an existing daemon
 *    or spawns standalone_daemon.py if none is found, for the "just run vg
 *    and it works" experience. The signed client is built separately from
 *    the host's own probe/spawn client, since ManagedRuntimeHost has no
 *    signer concept (a per-command-dispatch concern, not a lifecycle one).
 */
async function attachLive(opts: { socketPath?: string; signer?: OperatorSigner; headless: boolean }): Promise<RuntimeClient> {
  if (opts.headless) {
    return new SocketRuntimeClient({ socketPath: resolveSocketPath(opts.socketPath), signer: opts.signer });
  }
  const layout = ProductPaths.resolveLayout();
  if (opts.socketPath) layout.socketPath = opts.socketPath;
  const host = new ManagedRuntimeHost({ layout });
  await host.ensureRunning();
  return new SocketRuntimeClient({ socketPath: layout.socketPath, signer: opts.signer });
}

/** --demo/--replay/--scenario = mock; --feed = stdin NDJSON; else attach (headless: fail-fast; interactive: spawn-or-attach). No fixture fallback. */
export async function clientFor(parsed: CliOptions): Promise<RuntimeClient> {
  if (parsed.demo) {
    const scenario = parsed.demoScenario ?? "successful-episode";
    const path = demoFixturePath(packageRootFrom(import.meta.url), scenario);
    return ReplayRuntimeClient.fromEnvelopes(envelopesFromFile(path), "mock");
  }
  if (parsed.replay) return ReplayRuntimeClient.fromEnvelopes(envelopesFromFile(parsed.replay));
  if (parsed.scenario) return new ScenarioRuntimeClient();
  if (parsed.feed) return new ReplayRuntimeClient(stdinLines());
  return attachLive({
    socketPath: parsed.socketPath,
    signer: OperatorSigner.loadOrCreate(),
    headless: Boolean(parsed.headless),
  });
}
