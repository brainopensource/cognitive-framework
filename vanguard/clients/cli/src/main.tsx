#!/usr/bin/env node
import React from "react";
import { render } from "ink";
import {
  approveDecision,
  explain,
  manageDaemon,
  resumeRun,
  runCodingCommand,
  streamRun,
  streamTrace,
  type CodingRequest,
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

function codingRequestFromParsed(
  cmd: "code" | "explain" | "resume" | "doctor",
  overrides: Partial<CodingRequest> = {}
): CodingRequest {
  return {
    command: cmd,
    workspace: parsed.repo,
    brief: parsed.brief,
    question: parsed.question,
    runId: parsed.runId,
    resumeFrom: parsed.resumeFrom,
    plannerModel: parsed.plannerModel ?? parsed.model ?? "openrouter/free",
    modelPort: parsed.modelPort,
    storePath: parsed.storePath,
    profile: parsed.profile ?? "product",
    tokenBudget: parsed.tokenBudget,
    effectBudget: parsed.effectBudget,
    executorBand: parsed.executorBand ?? "free",
    executorModels: [],
    recoveryModels: parsed.recoveryModel ? [parsed.recoveryModel] : [],
    reviewerModel: null,
    maxTurnsPerEpisode: parsed.maxTurns ?? 40,
    maxEpisodes: parsed.maxEpisodes ?? 12,
    maxReplans: parsed.maxReplans ?? 2,
    maxPaidCalls: (parsed.budgetUsdMicros ?? 0) > 0 ? 20 : 0,
    budgetUsdMicros: parsed.budgetUsdMicros ?? 0,
    interactive: Boolean(parsed.interactive),
    dryPlan: Boolean(parsed.dryPlan),
    jsonlOut: parsed.jsonlOut,
    json: Boolean(parsed.json),
    headless: Boolean(parsed.headless || parsed.json),
    ...overrides,
  };
}

let exitCode = 0;

if (command === "run") {
  if (parsed.headless) {
    exitCode = await streamRun(runtime, parsed, console.log);
  } else {
    render(
      <RunTui
        runtime={runtime}
        repo={parsed.repo}
        runId={parsed.runId}
        resumeFrom={parsed.resumeFrom}
        autostart={parsed.promptExplicit || Boolean(parsed.resumeFrom)}
        initialBrief={parsed.promptExplicit ? (parsed.prompt ?? "") : ""}
      />
    );
  }
} else if (command === "code") {
  if ((parsed as { budgetError?: string }).budgetError) {
    console.error((parsed as { budgetError?: string }).budgetError);
    process.exit(2);
  }
  if (parsed.executorBand && parsed.executorBand !== "free" && (parsed.budgetUsdMicros ?? 0) <= 0 && !parsed.dryPlan) {
    // Default execution stays free. Paid/medium bands require an explicit budget.
    // The Python entrypoint still refuses frontier without authorization.
  }
  const request = codingRequestFromParsed(parsed.resumeFrom ? "resume" : "code", {
    runId: parsed.resumeFrom ?? parsed.runId,
  });
  exitCode = await runCodingCommand(request, console.log);
} else if (command === "explain") {
  if (!parsed.question) usage();
  exitCode = await runCodingCommand(codingRequestFromParsed("explain"), console.log);
} else if (command === "doctor") {
  exitCode = await runCodingCommand(
    codingRequestFromParsed("doctor", { workspace: parsed.repo ?? "." }),
    console.log
  );
} else if (command === "approve") {
  const runId = parsed.runId ?? rest.find((a) => !a.startsWith("-"));
  if (!runId || !parsed.decision) usage();
  exitCode = await approveDecision(runtime, runId, parsed.decision, console.log);
} else if (command === "resume") {
  const runId = parsed.runId ?? rest.find((a) => !a.startsWith("-"));
  if (!runId) usage();
  if (parsed.socketPath || parsed.demo) {
    exitCode = await resumeRun(runtime, { ...parsed, runId }, console.log);
  } else {
    const request = codingRequestFromParsed("resume", {
      runId,
      resumeFrom: runId,
    });
    exitCode = await runCodingCommand(request, console.log);
  }
} else if (command === "trace") {
  const target = rest.find((arg) => !arg.startsWith("-") && arg !== parsed.demoScenario) ?? usage();
  exitCode = await streamTrace(runtime, target, console.log);
} else if (command === "why") {
  const target = rest.find((arg) => !arg.startsWith("-") && arg !== parsed.demoScenario) ?? usage();
  exitCode = await explain(runtime, target, console.log);
} else if (command === "daemon") {
  const action = rest.find((a) => ["start", "status", "stop"].includes(a)) as
    | "start"
    | "status"
    | "stop"
    | undefined;
  if (!action) usage();
  exitCode = await manageDaemon(runtime, action, console.log);
} else {
  usage();
}

process.exitCode = exitCode;
if (
  parsed.headless ||
  parsed.json ||
  command === "daemon" ||
  command === "approve" ||
  command === "trace" ||
  command === "why" ||
  command === "resume" ||
  command === "code" ||
  command === "explain" ||
  command === "doctor"
) {
  process.exit(exitCode);
}
