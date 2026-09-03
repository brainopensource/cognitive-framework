#!/usr/bin/env node
import {
  ManagedRuntimeHost,
  OperatorSigner,
  ProductPaths,
  SocketRuntimeClient,
} from "@aether/client";
import { TuiApplication } from "./app.js";

function parseArgs(args: string[]) {
  const options: Record<string, string> = {};
  for (let i = 0; i < args.length; i++) {
    const arg = args[i]!;
    if (arg.startsWith("--") && i + 1 < args.length) {
      options[arg.slice(2)] = args[i + 1]!;
      i++;
    }
  }
  return options;
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));
  const layout = ProductPaths.resolveLayout();
  if (args["socket-path"]) layout.socketPath = args["socket-path"];

  const host = new ManagedRuntimeHost({ layout });
  await host.ensureRunning();
  const client = new SocketRuntimeClient({
    socketPath: layout.socketPath,
    signer: OperatorSigner.loadOrCreate(),
  });

  const app = new TuiApplication({
    client,
    initialState: {
      workspacePath: args["repo"] ?? ".",
      agentId: args["agent"] ?? "vg-code-balanced",
      model: args["model"] ?? "openrouter/free",
    },
    onExit: () => {
      process.exit(0);
    },
  });

  app.start();
}

main().catch((err) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
