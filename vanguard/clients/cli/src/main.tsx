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
} from "@vanguard/client-core";
import { clientFor } from "./composition/client-for.js";
import { parseCliOptions, usage, USAGE } from "./composition/parse-cli.js";
import { RunTui } from "./tui/screens/run-tui.js";

process.stdout.on("error", (error) => {
  if ((error as NodeJS.ErrnoException).code === "EPIPE") process.exit(0);
});

const argv = process.argv.slice(2);
if (!argv[0] || argv[0] === "--help" || argv[0] === "-h") {
  console.error(USAGE);
  process.exit(argv[0] ? 0 : 2);
}

const [command, ...rest] = argv;
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
  const target = rest.find((arg) => !arg.startsWith("-") && arg !== parsed.demoScenario) ?? usage();
  exitCode = await streamTrace(runtime, target, console.log);
} else if (command === "why") {
  const target = rest.find((arg) => !arg.startsWith("-") && arg !== parsed.demoScenario) ?? usage();
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
