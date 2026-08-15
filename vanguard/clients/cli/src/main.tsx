#!/usr/bin/env node
import React from "react";
import { render } from "ink";
import { explain, streamRun, streamTrace, type CliOptions } from "./commands.js";
import { MockRuntime } from "./mock-runtime.js";
import { RunTui } from "./tui.js";

process.stdout.on("error", (error) => {
  if ((error as NodeJS.ErrnoException).code === "EPIPE") process.exit(0);
});

function usage(): never {
  console.error("Usage: vg run [repo] [--headless] | vg trace <runId> [--headless] | vg why <artifact> [--headless]");
  process.exit(2);
}

function options(args: string[]): CliOptions {
  const positional = args.filter((arg) => !arg.startsWith("--"));
  const value = (name: string) => { const index = args.indexOf(name); return index >= 0 ? args[index + 1] : undefined; };
  return { headless: args.includes("--headless"), repo: positional[0] ?? ".", runId: value("--run-id"), resumeFrom: value("--resume"), checkpointEvery: Number(value("--checkpoint-every") ?? 2) };
}

const [command, target, ...rest] = process.argv.slice(2);
const runtime = new MockRuntime();
const parsed = options([target, ...rest].filter(Boolean));

if (command === "run") {
  if (parsed.headless) await streamRun(runtime, parsed, console.log);
  else render(<RunTui runtime={runtime} repo={parsed.repo} runId={parsed.runId} resumeFrom={parsed.resumeFrom} checkpointEvery={parsed.checkpointEvery} />);
} else if (command === "trace") {
  await streamTrace(runtime, target ?? usage(), console.log);
} else if (command === "why") {
  await explain(runtime, target ?? usage(), console.log);
} else usage();
