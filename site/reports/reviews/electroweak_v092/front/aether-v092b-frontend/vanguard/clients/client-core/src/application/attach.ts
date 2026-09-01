import type { RuntimeClient } from "../contract/types.js";
import { OperatorSigner } from "../adapters/signer.js";
import { LiveRuntimeClient, type LiveClientOptions } from "../adapters/live.js";
import { resolveSocketPath } from "../adapters/transport.js";

export function attachLive(
  opts: {
    socketPath?: string;
    signer?: OperatorSigner;
    manifest?: string;
    repo?: string;
    model?: string;
  } = {}
): RuntimeClient {
  const signer = opts.signer ?? OperatorSigner.loadOrCreate();
  const options: LiveClientOptions = {
    socketPath: resolveSocketPath(opts.socketPath),
    signer,
    manifest: opts.manifest,
    repo: opts.repo,
    model: opts.model,
  };
  return new LiveRuntimeClient(undefined, options);
}
