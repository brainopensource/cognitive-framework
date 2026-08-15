#!/usr/bin/env node
import React from "react";
import { render } from "ink";
import { explain, streamRun, streamTrace, type CliOptions } from "./application/commands.js";
import { LiveRuntimeClient } from "./adapters/live.js";
import { ReplayRuntimeClient } from "./adapters/replay.js";
import { ScenarioRuntimeClient } from "./adapters/scenario.js";
import type { RuntimeClient } from "./contract/types.js";
import { RunTui } from "./tui.js";

process.stdout.on("error", (error) => {
  if ((error as NodeJS.ErrnoException).code === "EPIPE") process.exit(0);
});

function usage(): never {
  console.error("Usage: vg run [repo] [--headless] [--replay <file.jsonl>] | vg trace <runId> [--replay <file.jsonl>] | vg why <artifact> [--replay <file.jsonl>]");
  process.exit(2);
}

function options(args: string[]): CliOptions {
  const positional = args.filter((arg) => !arg.startsWith("--") && args[args.indexOf(arg) - 1] !== "--replay" && args[args.indexOf(arg) - 1] !== "--run-id" && args[args.indexOf(arg) - 1] !== "--resume" && args[args.indexOf(arg) - 1] !== "--checkpoint-every");
  const value = (name: string) => {
    const index = args.indexOf(name);
    return index >= 0 ? args[index + 1] : undefined;
  };
  return {
    headless: args.includes("--headless"),
    repo: positional[0] ?? ".",
    runId: value("--run-id"),
    resumeFrom: value("--resume"),
    checkpointEvery: Number(value("--checkpoint-every") ?? 2),
    replay: value("--replay"),
  };
}

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

function clientFor(parsed: CliOptions): RuntimeClient {
  if (parsed.replay) return ReplayRuntimeClient.fromFile(parsed.replay);
  if (!process.stdin.isTTY) return new LiveRuntimeClient(stdinLines());
  return new ScenarioRuntimeClient();
}

const [command, target, ...rest] = process.argv.slice(2);
const parsed = options([target, ...rest].filter(Boolean));
const runtime = clientFor(parsed);

if (command === "run") {
  if (parsed.headless) await streamRun(runtime, parsed, console.log);
  else render(<RunTui runtime={runtime} repo={parsed.repo} runId={parsed.runId} resumeFrom={parsed.resumeFrom} />);
} else if (command === "trace") {
  await streamTrace(runtime, target ?? usage(), console.log);
} else if (command === "why") {
  await explain(runtime, target ?? usage(), console.log);
} else usage();
