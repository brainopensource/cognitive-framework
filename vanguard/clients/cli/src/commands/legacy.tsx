import React from "react";
import { render } from "ink";
import {
  approveDecision,
  explain,
  manageDaemon,
  resumeRun,
  streamRun,
  streamTrace,
} from "@aether/client";
import { runCodingCommand, type CodingRequest } from "@vanguard/client-core";
import { clientFor } from "../composition/client-for.js";
import { parseCliOptions, usage, type ParsedCli } from "../composition/parse-cli.js";
import { RunTui } from "../tui/screens/run-tui.js";

function codingRequestFromParsed(
  parsed: ParsedCli,
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
    plannerModel: parsed.plannerModel ?? parsed.model ?? "default",
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

export async function handleRun(args: string[], parsed: ParsedCli): Promise<number> {
  const runtime = await clientFor(parsed);
  if (parsed.headless) {
    return await streamRun(runtime, parsed, console.log);
  } else {
    return new Promise<number>((resolve) => {
      const { waitUntilExit } = render(
        <RunTui
          runtime={runtime}
          repo={parsed.repo}
          runId={parsed.runId}
          resumeFrom={parsed.resumeFrom}
          autostart={parsed.promptExplicit || Boolean(parsed.resumeFrom)}
          initialBrief={parsed.promptExplicit ? (parsed.prompt ?? "") : ""}
        />
      );
      waitUntilExit().then(() => resolve(0)).catch(() => resolve(1));
    });
  }
}

export async function handleCode(args: string[], parsed: ParsedCli): Promise<number> {
  if (parsed.budgetError) {
    console.error(parsed.budgetError);
    process.exit(2);
  }
  const request = codingRequestFromParsed(parsed, parsed.resumeFrom ? "resume" : "code", {
    runId: parsed.resumeFrom ?? parsed.runId,
  });
  return await runCodingCommand(request, console.log);
}

export async function handleExplain(args: string[], parsed: ParsedCli): Promise<number> {
  if (!parsed.question) usage();
  return await runCodingCommand(codingRequestFromParsed(parsed, "explain"), console.log);
}

export async function handleDoctor(args: string[], parsed: ParsedCli): Promise<number> {
  return await runCodingCommand(
    codingRequestFromParsed(parsed, "doctor", { workspace: parsed.repo ?? "." }),
    console.log
  );
}

export async function handleApprove(args: string[], parsed: ParsedCli): Promise<number> {
  const runtime = await clientFor(parsed);
  const runId = parsed.runId ?? args.find((a) => !a.startsWith("-"));
  if (!runId || !parsed.decision) usage();
  return await approveDecision(runtime, runId, parsed.decision, console.log);
}

export async function handleResume(args: string[], parsed: ParsedCli): Promise<number> {
  const runtime = await clientFor(parsed);
  const runId = parsed.runId ?? args.find((a) => !a.startsWith("-"));
  if (!runId) usage();
  if (parsed.socketPath || parsed.demo) {
    return await resumeRun(runtime, { ...parsed, runId }, console.log);
  } else {
    const request = codingRequestFromParsed(parsed, "resume", {
      runId,
      resumeFrom: runId,
    });
    return await runCodingCommand(request, console.log);
  }
}

export async function handleTrace(args: string[], parsed: ParsedCli): Promise<number> {
  const runtime = await clientFor(parsed);
  const target = args.find((arg) => !arg.startsWith("-") && arg !== parsed.demoScenario) ?? usage();
  return await streamTrace(runtime, target, console.log);
}

export async function handleWhy(args: string[], parsed: ParsedCli): Promise<number> {
  const runtime = await clientFor(parsed);
  const target = args.find((arg) => !arg.startsWith("-") && arg !== parsed.demoScenario) ?? usage();
  return await explain(runtime, target, console.log);
}

export async function handleDaemon(args: string[], parsed: ParsedCli): Promise<number> {
  const runtime = await clientFor(parsed);
  const action = args.find((a) => ["start", "status", "stop"].includes(a)) as
    | "start"
    | "status"
    | "stop"
    | undefined;
  if (!action) usage();
  return await manageDaemon(runtime, action, console.log);
}
