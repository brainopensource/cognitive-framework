import type { ParsedCli } from "../composition/parse-cli.js";
import { clientFor } from "../composition/client-for.js";
import { streamRun } from "@vanguard/client-core";
import {
  CLI_EXIT_CODES,
  logDiagnostic,
} from "../output.js";

export async function handleAttach(args: string[], options: ParsedCli): Promise<number> {
  const runId = args[0] ?? options.runId;
  if (!runId || runId.startsWith("-")) {
    logDiagnostic("Usage: aether attach <run-id> [--headless] [--json]");
    return CLI_EXIT_CODES.INVALID_INPUT;
  }

  const runtime = clientFor(options);
  options.runId = runId;
  options.headless = true;

  return await streamRun(runtime, options, console.log);
}
