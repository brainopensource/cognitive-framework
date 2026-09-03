#!/usr/bin/env node
import { createRuntimeClient } from "@aether/client";
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

const args = parseArgs(process.argv.slice(2));
const client = createRuntimeClient({
  socketOptions: {
    socketPath: args["socket-path"] ?? "/tmp/vanguard-runtime.sock",
  },
});

const app = new TuiApplication({
  client,
  initialState: {
    workspacePath: args["repo"] ?? ".",
    agentId: args["agent"] ?? "coding-agent",
    model: args["model"] ?? "openrouter/free",
  },
});

app.start();
