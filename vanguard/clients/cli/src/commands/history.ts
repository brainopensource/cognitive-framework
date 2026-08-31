import type { ParsedCli } from "../composition/parse-cli.js";
import { clientFor } from "../composition/client-for.js";
import type { RunSummary } from "@aether/contracts";
import {
  CLI_EXIT_CODES,
  logDiagnostic,
  writeJsonOutcome,
} from "../output.js";

export async function handleHistory(args: string[], options: ParsedCli): Promise<number> {
  const runtime = clientFor(options) as any;

  const statusIndex = args.indexOf("--status");
  const statusFilter = (statusIndex >= 0 ? args[statusIndex + 1] ?? "" : "").toLowerCase();
  const limitIndex = args.indexOf("--limit");
  const limit = limitIndex >= 0 ? parseInt(args[limitIndex + 1]!, 10) : 20;

  try {
    if (typeof runtime.listRuns !== "function") {
      logDiagnostic("Runtime does not support listRuns");
      return CLI_EXIT_CODES.EXECUTION_FAILED;
    }
    const res = await runtime.listRuns({});
    if (!res.ok) {
      logDiagnostic(`Failed to list run history: ${res.error.message}`);
      return CLI_EXIT_CODES.EXECUTION_FAILED;
    }

    let runs: RunSummary[] = res.value;
    if (statusFilter) {
      runs = runs.filter((r: RunSummary) => r.status.toLowerCase().includes(statusFilter));
    }
    if (!Number.isNaN(limit) && limit > 0) {
      runs = runs.slice(0, limit);
    }

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "history",
        status: "success",
        data: { count: runs.length, runs },
      });
    } else {
      console.log(`\nRun History (${runs.length}):`);
      console.log(`  ${"RUN ID".padEnd(20)} ${"STATUS".padEnd(16)} ${"OCCURRED AT".padEnd(26)} ${"VERDICT"}`);
      console.log(`  ${"-".repeat(78)}`);
      for (const r of runs) {
        console.log(
          `  ${r.runId.slice(0, 18).padEnd(20)} ${r.status.toUpperCase().padEnd(16)} ${(r.occurredAt ?? "unknown").slice(0, 24).padEnd(26)} ${r.verdict ?? "none"}`
        );
      }
    }
    return CLI_EXIT_CODES.SUCCESS;
  } catch (err) {
    logDiagnostic(`History error: ${String(err)}`);
    return CLI_EXIT_CODES.EXECUTION_FAILED;
  }
}
