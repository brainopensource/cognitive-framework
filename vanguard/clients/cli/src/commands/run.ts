import { readFileSync, existsSync } from "node:fs";
import {
  foldEvents,
  reduceRunSnapshot,
  emptyRunSnapshot,
} from "@aether/projections";
import {
  parseJsonlLine,
  type EventEnvelope,
  type StartRunRequest,
} from "@aether/contracts";
import {
  ReplayRuntimeClient,
  type RuntimeClient,
} from "@aether/client";
import { streamRun } from "@aether/client";
import type { ParsedCli } from "../composition/parse-cli.js";
import { clientFor } from "../composition/client-for.js";
import { TuiApplication } from "@aether/tui";
import {
  CLI_EXIT_CODES,
  exitCodeForErrorCode,
  logDiagnostic,
  writeJsonOutcome,
  writeNdjsonFrame,
} from "../output.js";

export async function handleRun(args: string[], options: ParsedCli): Promise<number> {
  const subcommand = args[0];

  // Subcommand dispatch
  if (subcommand === "list") {
    return handleRunList(args.slice(1), options);
  }
  if (subcommand === "inspect") {
    return handleRunInspect(args.slice(1), options);
  }
  if (subcommand === "stream") {
    return handleRunStream(args.slice(1), options);
  }
  if (subcommand === "cancel") {
    return handleRunCancel(args.slice(1), options);
  }
  if (subcommand === "checkpoint") {
    return handleRunCheckpoint(args.slice(1), options);
  }
  if (subcommand === "resume") {
    return handleRunResume(args.slice(1), options);
  }
  if (subcommand === "replay") {
    return handleRunReplay(args.slice(1), options);
  }

  // Load configured defaults if flags omitted
  const { NodeFsPersistenceAdapter, DEFAULT_PROVIDERS } = await import("@aether/client");
  const { DEFAULT_FRONTEND_SETTINGS } = await import("@aether/projections");
  const persistence = new NodeFsPersistenceAdapter();
  const [settings, providers] = await Promise.all([
    persistence.loadSettings().then((s) => s ?? DEFAULT_FRONTEND_SETTINGS),
    persistence.loadProviders().then((p) => p ?? DEFAULT_PROVIDERS),
  ]);
  const defaultProvider = (providers as any[]).find((p: any) => p.isDefault) ?? (providers as any[])[0];

  if (!options.repo && (settings as any).general?.defaultWorkspace) {
    options.repo = (settings as any).general.defaultWorkspace;
  }
  if (!options.model && defaultProvider?.selectedModel) {
    options.model = defaultProvider.selectedModel;
  }

  // Direct execution: aether run [repo] [options]
  if (options.json) {
    return executeRun(options);
  }

  if (options.headless) {
    const runtime = await clientFor(options);
    return await streamRun(runtime, options, console.log);
  }

  const runtime = await clientFor(options);
  return new Promise<number>((resolve) => {
    const app = new TuiApplication({
      client: runtime,
      initialState: {
        workspacePath: options.repo ?? ".",
        runId: options.runId ?? "",
        agentId: "vg-code-balanced",
      },
      onExit: () => resolve(0),
    });
    app.start();
    if (options.resumeFrom) {
      app.store.controller.resumeRun(options.resumeFrom);
    } else if (options.promptExplicit && options.prompt) {
      app.store.setComposerText(options.prompt);
      app.store.submitComposer(runtime);
    }
  });
}

async function executeRun(options: ParsedCli): Promise<number> {
  let runtime: any;

  if (options.replay) {
    if (!existsSync(options.replay)) {
      logDiagnostic(`Replay fixture not found: ${options.replay}`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }
    const content = readFileSync(options.replay, "utf-8");
    const lines = content.split("\n").filter((l) => l.trim().length > 0);
    async function* gen() {
      for (const line of lines) yield line;
    }
    runtime = new ReplayRuntimeClient(gen());
  } else {
    runtime = await clientFor(options);
  }

  const startReq: StartRunRequest = {
    repo: options.repo ?? ".",
    prompt: options.prompt,
    brief: options.brief,
    model: options.plannerModel ?? options.model,
    profileId: options.profile,
    runId: options.runId,
    resumeFrom: options.resumeFrom,
    checkpointEvery: options.checkpointEvery,
    autoApprove: options.autoApprove,
    nonInteractive: Boolean(options.headless || options.json || !options.interactive),
  };

  const startRes = await runtime.startRun(startReq);
  if (!startRes.ok) {
    logDiagnostic(`Run start failed [${startRes.error.code}]: ${startRes.error.message}`);
    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "run",
        runId: options.runId,
        status: "error",
        error: {
          code: startRes.error.code,
          message: startRes.error.message,
          retryable: startRes.error.retryable,
        },
      });
    }
    return exitCodeForErrorCode(startRes.error.code);
  }

  const runId = startRes.value.runId;
  let snapshot = emptyRunSnapshot(runId);
  const isNdjson = Boolean(options.feed || (process.argv.includes("--ndjson")));

  try {
    for await (const item of runtime.streamEvents({ runId })) {
      if (!item.ok) {
        logDiagnostic(`Stream item error [${item.error.code}]: ${item.error.message}`);
        if (isNdjson) {
          writeNdjsonFrame({
            version: "vg.4",
            frameType: "error",
            frameId: `err-${Date.now()}`,
            error: item.error,
          });
        }
        return exitCodeForErrorCode(item.error.code);
      }

      const env = item.value.envelope;
      snapshot = reduceRunSnapshot(snapshot, env);

      if (isNdjson) {
        writeNdjsonFrame({
          version: "vg.4",
          frameType: "event",
          frameId: `frm-${env.seq}`,
          event: env,
        });
      }

      // Handle approval if requested
      if (env.payload.kind === "ApprovalRequested") {
        if (options.autoApprove) {
          logDiagnostic(`Auto-approving challenge ${env.payload.approvalId}...`);
          const resolveRes = await runtime.resolveApproval({
            approvalId: String(env.payload.approvalId),
            decision: "approve",
          });
          if (!resolveRes.ok) {
            logDiagnostic(`Failed to resolve approval: ${resolveRes.error.message}`);
          }
        } else if (startReq.nonInteractive) {
          logDiagnostic(`Governance approval required for action '${env.payload.action}' (halting non-interactive execution).`);
          if (options.json) {
            writeJsonOutcome({
              api: "aether.cli-outcome/1",
              command: "run",
              runId,
              status: "awaiting_approval",
              metrics: {
                totalTokens: snapshot.tokens.totalTokens,
                inTokens: snapshot.tokens.inTokens,
                outTokens: snapshot.tokens.outTokens,
                costMicros: snapshot.costMicros,
                turns: snapshot.turns,
              },
            });
          }
          return CLI_EXIT_CODES.APPROVAL_REQUIRED; // 3
        }
      }
    }
  } catch (err) {
    logDiagnostic(`Stream ingestion error: ${String(err)}`);
    return CLI_EXIT_CODES.EXECUTION_FAILED;
  }

  const isSatisfied = snapshot.status === "satisfied" || snapshot.verdict === "satisfied" || snapshot.verdict === "1";

  if (options.json) {
    writeJsonOutcome({
      api: "aether.cli-outcome/1",
      command: "run",
      runId,
      status: snapshot.status,
      verdict: snapshot.verdict ?? (isSatisfied ? "satisfied" : "failed"),
      metrics: {
        totalTokens: snapshot.tokens.totalTokens,
        inTokens: snapshot.tokens.inTokens,
        outTokens: snapshot.tokens.outTokens,
        costMicros: snapshot.costMicros,
        turns: snapshot.turns,
      },
      artifacts: snapshot.artifacts,
    });
  } else if (!isNdjson) {
    console.log(`\nRun ${runId} finished with status: ${snapshot.status.toUpperCase()}`);
    if (snapshot.verdict) console.log(`Verdict: ${snapshot.verdict}`);
    console.log(`Tokens: ${snapshot.tokens.totalTokens} (cost: ${snapshot.costMicros} µUSD) | Turns: ${snapshot.turns}`);
    if (snapshot.artifacts.length > 0) {
      console.log(`Artifacts (${snapshot.artifacts.length}):`);
      for (const art of snapshot.artifacts) {
        console.log(`  - [${art.kind}] ${art.path ?? art.digest}`);
      }
    }
  }

  return isSatisfied ? CLI_EXIT_CODES.SUCCESS : CLI_EXIT_CODES.EXECUTION_FAILED;
}

export async function handleRunList(args: string[], options: ParsedCli): Promise<number> {
  const client = await clientFor(options) as any;
  const limitIdx = args.indexOf("--limit");
  const limit = limitIdx >= 0 && args[limitIdx + 1] ? Number(args[limitIdx + 1]) : 20;

  if (typeof client.listRuns !== "function") {
    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "run list",
        status: "success",
        data: { runs: [] },
      });
    } else {
      console.log("\nNo active runs list available on this client");
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  const res = await client.listRuns({ limit });
  if (!res.ok) {
    logDiagnostic(`List runs failed [${res.error.code}]: ${res.error.message}`);
    return exitCodeForErrorCode(res.error.code);
  }

  if (options.json) {
    writeJsonOutcome({
      api: "aether.cli-outcome/1",
      command: "run list",
      status: "success",
      data: { runs: res.value },
    });
  } else {
    console.log(`\nActive and recent runs (${res.value.length}):`);
    for (const run of res.value) {
      console.log(`  ${run.runId.padEnd(30)} ${run.status.padEnd(12)} seq: ${run.seq}`);
    }
  }

  return CLI_EXIT_CODES.SUCCESS;
}

export async function handleRunInspect(args: string[], options: ParsedCli): Promise<number> {
  const runId = args[0] || options.runId;
  if (!runId) {
    logDiagnostic("Missing <run-id> for run inspect");
    return CLI_EXIT_CODES.INVALID_INPUT;
  }

  const client = await clientFor(options);
  const res = await client.getRun(runId);
  if (!res.ok) {
    logDiagnostic(`Inspect run ${runId} failed [${res.error.code}]: ${res.error.message}`);
    return exitCodeForErrorCode(res.error.code);
  }

  if (options.json) {
    writeJsonOutcome({
      api: "aether.cli-outcome/1",
      command: "run inspect",
      runId,
      status: res.value.status === "satisfied" ? "satisfied" : "success",
      verdict: res.value.verdict,
      data: res.value as any,
    });
  } else {
    console.log(`\nRun Details: ${runId}`);
    console.log(`Status:  ${res.value.status}`);
    console.log(`Seq:     ${res.value.seq}`);
    if (res.value.verdict) console.log(`Verdict: ${res.value.verdict}`);
  }

  return CLI_EXIT_CODES.SUCCESS;
}

export async function handleRunStream(args: string[], options: ParsedCli): Promise<number> {
  const runId = args[0] || options.runId;
  if (!runId) {
    logDiagnostic("Missing <run-id> for run stream");
    return CLI_EXIT_CODES.INVALID_INPUT;
  }

  const afterSeqIdx = args.indexOf("--after-seq");
  const afterSeq = afterSeqIdx >= 0 && args[afterSeqIdx + 1] ? args[afterSeqIdx + 1] : undefined;

  const client = await clientFor(options);
  for await (const item of client.streamEvents({ runId, afterSeq })) {
    if (!item.ok) {
      logDiagnostic(`Stream failed [${item.error.code}]: ${item.error.message}`);
      return exitCodeForErrorCode(item.error.code);
    }
    writeNdjsonFrame({
      version: "vg.4",
      frameType: "event",
      frameId: `frm-${item.value.envelope.seq}`,
      event: item.value.envelope,
    });
  }

  return CLI_EXIT_CODES.SUCCESS;
}

export async function handleRunCancel(args: string[], options: ParsedCli): Promise<number> {
  const runId = args[0] || options.runId;
  if (!runId) {
    logDiagnostic("Missing <run-id> for run cancel");
    return CLI_EXIT_CODES.INVALID_INPUT;
  }

  const reasonIdx = args.indexOf("--reason");
  const reason = reasonIdx >= 0 && args[reasonIdx + 1] ? args[reasonIdx + 1] : "Operator requested cancellation";

  const client = await clientFor(options) as any;
  const res = await client.requestCancel(runId, { reason });
  if (!res.ok) {
    logDiagnostic(`Cancel failed [${res.error.code}]: ${res.error.message}`);
    return exitCodeForErrorCode(res.error.code);
  }

  if (options.json) {
    writeJsonOutcome({
      api: "aether.cli-outcome/1",
      command: "run cancel",
      runId,
      status: "cancelled",
      data: res.value,
    });
  } else {
    console.log(`Cancelled run ${runId}`);
  }

  return CLI_EXIT_CODES.SUCCESS;
}

export async function handleRunCheckpoint(args: string[], options: ParsedCli): Promise<number> {
  const runId = args[0] || options.runId;
  if (!runId) {
    logDiagnostic("Missing <run-id> for run checkpoint");
    return CLI_EXIT_CODES.INVALID_INPUT;
  }

  const client = await clientFor(options) as any;
  const res = await client.requestCheckpoint(runId);
  if (!res.ok) {
    logDiagnostic(`Checkpoint failed [${res.error.code}]: ${res.error.message}`);
    return exitCodeForErrorCode(res.error.code);
  }

  if (options.json) {
    writeJsonOutcome({
      api: "aether.cli-outcome/1",
      command: "run checkpoint",
      runId,
      status: "success",
      data: res.value,
    });
  } else {
    console.log(`Checkpoint created for run ${runId}`);
  }

  return CLI_EXIT_CODES.SUCCESS;
}

export async function handleRunResume(args: string[], options: ParsedCli): Promise<number> {
  const runId = args[0] || options.runId;
  if (!runId) {
    logDiagnostic("Missing <run-id> for run resume");
    return CLI_EXIT_CODES.INVALID_INPUT;
  }

  const cpIdx = args.indexOf("--checkpoint");
  const checkpointId = cpIdx >= 0 && args[cpIdx + 1] ? args[cpIdx + 1] : undefined;

  const client = await clientFor(options) as any;
  const res = await client.requestResume(runId, { checkpointId });
  if (!res.ok) {
    logDiagnostic(`Resume failed [${res.error.code}]: ${res.error.message}`);
    return exitCodeForErrorCode(res.error.code);
  }

  if (options.json) {
    writeJsonOutcome({
      api: "aether.cli-outcome/1",
      command: "run resume",
      runId,
      status: "success",
      data: res.value,
    });
  } else {
    console.log(`Resumed run ${runId}`);
  }

  return CLI_EXIT_CODES.SUCCESS;
}

export async function handleRunReplay(args: string[], options: ParsedCli): Promise<number> {
  const fixturePath = args[0] || options.replay;
  if (!fixturePath) {
    logDiagnostic("Missing <fixture-path> for run replay");
    return CLI_EXIT_CODES.INVALID_INPUT;
  }

  return executeRun({ ...options, replay: fixturePath, headless: true });
}
