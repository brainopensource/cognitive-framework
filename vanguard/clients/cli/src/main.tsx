#!/usr/bin/env node
import React from "react";
import { render } from "ink";
import {
  approveDecision,
  explain,
  manageDaemon,
  resumeRun,
  streamRun,
  streamTrace,
  type CliOptions,
} from "./application/commands.js";
import { LiveRuntimeClient } from "./adapters/live.js";
import { ReplayRuntimeClient } from "./adapters/replay.js";
import { ScenarioRuntimeClient } from "./adapters/scenario.js";
import type { RuntimeClient } from "./contract/types.js";
import { RunTui } from "./tui.js";

process.stdout.on("error", (error) => {
  if ((error as NodeJS.ErrnoException).code === "EPIPE") process.exit(0);
});

function usage(): never {
  console.error(
    "Usage:\n" +
      "  vg daemon start|status|stop\n" +
      "  vg run [repo] --headless --prompt <text> [--model <id>] [--manifest <id>]\n" +
      "  vg approve <run-id> --decision approve|reject\n" +
      "  vg resume <run-id> [--headless]\n" +
      "  vg trace <run-id> [--headless] [--replay <file.jsonl>]\n" +
      "  vg why <artifact> [--headless] [--replay <file.jsonl>]"
  );
  process.exit(2);
}

function parseCliOptions(args: string[]): CliOptions {
  const value = (name: string) => {
    const index = args.indexOf(name);
    return index >= 0 && index + 1 < args.length ? args[index + 1] : undefined;
  };
  const flag = (name: string) => args.includes(name);

  const flagNamesWithVal = new Set([
    "--replay",
    "--run-id",
    "--resume",
    "--checkpoint-every",
    "--repo",
    "--prompt",
    "--model",
    "--manifest",
    "--decision",
    "--socket-path",
  ]);

  const positional: string[] = [];
  for (let i = 0; i < args.length; i++) {
    const arg = args[i]!;
    if (arg.startsWith("--") || arg.startsWith("-")) {
      if (flagNamesWithVal.has(arg)) i++;
      continue;
    }
    positional.push(arg);
  }

  let prompt = value("--prompt");
  let repo = value("--repo");
  const decisionVal = value("--decision");
  const decision: "approve" | "reject" | undefined =
    decisionVal === "approve" || decisionVal === "reject" ? decisionVal : undefined;

  if (positional.length > 0) {
    if (!prompt && !repo) {
      if (positional[0]!.startsWith(".") || positional[0]!.includes("/")) {
        repo = positional[0];
        if (positional.length > 1) prompt = positional.slice(1).join(" ");
      } else {
        prompt = positional.join(" ");
      }
    } else if (!prompt && repo) {
      prompt = positional.join(" ");
    } else if (prompt && !repo) {
      repo = positional[0];
    }
  }

  return {
    headless: flag("--headless"),
    feed: flag("--feed"),
    scenario: flag("--scenario"),
    prompt: prompt ?? "Execute default coding task",
    brief: prompt ?? "Execute default coding task",
    repo: repo ?? ".",
    runId: value("--run-id") ?? (positional[0] && !prompt ? positional[0] : undefined),
    resumeFrom: value("--resume"),
    checkpointEvery: Number(value("--checkpoint-every") ?? 2),
    replay: value("--replay"),
    model: value("--model"),
    manifest: value("--manifest") ?? "vg-code-default",
    decision,
    autoApprove: flag("--yes") || flag("-y"),
    socketPath: value("--socket-path"),
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
  if (parsed.scenario) return new ScenarioRuntimeClient();
  if (parsed.feed) return new LiveRuntimeClient(stdinLines(), { repo: parsed.repo, prompt: parsed.prompt, model: parsed.model });
  return new LiveRuntimeClient(undefined, {
    repo: parsed.repo,
    prompt: parsed.prompt,
    model: parsed.model,
    autoApprove: parsed.autoApprove,
    socketPath: parsed.socketPath,
  });
}

const [command, ...rest] = process.argv.slice(2);
if (!command) usage();

const parsed = parseCliOptions(rest);
const runtime = clientFor(parsed);

let exitCode = 0;

if (command === "run") {
  if (parsed.headless) {
    exitCode = await streamRun(runtime, parsed, console.log);
  } else {
    render(<RunTui runtime={runtime} repo={parsed.repo} runId={parsed.runId} resumeFrom={parsed.resumeFrom} />);
  }
} else if (command === "approve") {
  const runId = parsed.runId ?? rest.find((a) => !a.startsWith("-"));
  if (!runId || !parsed.decision) usage();
  exitCode = await approveDecision(runtime, runId, parsed.decision, console.log);
} else if (command === "resume") {
  const runId = parsed.runId ?? rest.find((a) => !a.startsWith("-"));
  if (!runId) usage();
  exitCode = await resumeRun(runtime, { ...parsed, runId }, console.log);
} else if (command === "trace") {
  const target = rest.find((arg) => !arg.startsWith("-")) ?? usage();
  exitCode = await streamTrace(runtime, target, console.log);
} else if (command === "why") {
  const target = rest.find((arg) => !arg.startsWith("-")) ?? usage();
  exitCode = await explain(runtime, target, console.log);
} else if (command === "daemon") {
  const action = rest.find((a) => ["start", "status", "stop"].includes(a)) as "start" | "status" | "stop" | undefined;
  if (!action) usage();
  exitCode = await manageDaemon(runtime, action, console.log);
} else {
  usage();
}

process.exitCode = exitCode;
if (parsed.headless || command === "daemon" || command === "approve" || command === "trace" || command === "why") {
  process.exit(exitCode);
}
