import { readFileSync } from "node:fs";
import {
  ManagedRuntimeHost,
  OperatorSigner,
  ProductPaths,
  ReplayRuntimeClient,
  ScenarioRuntimeClient,
  SocketRuntimeClient,
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
 * Unlike attachLive, this guarantees a daemon is actually running first --
 * ManagedRuntimeHost attaches to an existing one or spawns
 * standalone_daemon.py if none is found -- rather than assuming the operator
 * started it out of band. The signed client is built separately from the
 * host's own probe/spawn client, since ManagedRuntimeHost has no signer
 * concept (that's a per-command-dispatch concern, not a lifecycle one).
 */
async function attachManaged(opts: { socketPath?: string; signer?: OperatorSigner }): Promise<RuntimeClient> {
  const layout = ProductPaths.resolveLayout();
  if (opts.socketPath) layout.socketPath = opts.socketPath;
  const host = new ManagedRuntimeHost({ layout });
  await host.ensureRunning();
  return new SocketRuntimeClient({ socketPath: layout.socketPath, signer: opts.signer });
}

/** --demo/--replay/--scenario = mock; --feed = stdin NDJSON; else attach (spawn-or-attach, no fixture fallback). */
export async function clientFor(parsed: CliOptions): Promise<RuntimeClient> {
  if (parsed.demo) {
    const scenario = parsed.demoScenario ?? "successful-episode";
    const path = demoFixturePath(packageRootFrom(import.meta.url), scenario);
    return ReplayRuntimeClient.fromEnvelopes(envelopesFromFile(path));
  }
  if (parsed.replay) return ReplayRuntimeClient.fromEnvelopes(envelopesFromFile(parsed.replay));
  if (parsed.scenario) return new ScenarioRuntimeClient();
  if (parsed.feed) return new ReplayRuntimeClient(stdinLines());
  return attachManaged({
    socketPath: parsed.socketPath,
    signer: OperatorSigner.loadOrCreate(),
  });
}
