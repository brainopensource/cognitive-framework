import type { ParsedCli } from "../composition/parse-cli.js";
import { clientFor } from "../composition/client-for.js";
import {
  CLI_EXIT_CODES,
  exitCodeForErrorCode,
  logDiagnostic,
  writeNdjsonFrame,
} from "../output.js";

export async function handleEvent(args: string[], options: ParsedCli): Promise<number> {
  const subcommand = args[0];

  if (subcommand !== "tail" && subcommand !== "stream") {
    logDiagnostic("Usage: aether event tail <run-id> [--after-seq <n>] [--ndjson]");
    return CLI_EXIT_CODES.INVALID_INPUT;
  }

  const runId = args[1] || options.runId;
  if (!runId) {
    logDiagnostic("Missing <run-id> for event tail");
    return CLI_EXIT_CODES.INVALID_INPUT;
  }

  const afterSeqIdx = args.indexOf("--after-seq");
  const afterSeq = afterSeqIdx >= 0 && args[afterSeqIdx + 1] ? args[afterSeqIdx + 1] : undefined;

  const client = await clientFor(options);

  try {
    for await (const item of client.streamEvents({ runId, afterSeq })) {
      if (!item.ok) {
        logDiagnostic(`Event tail stream failed [${item.error.code}]: ${item.error.message}`);
        return exitCodeForErrorCode(item.error.code);
      }
      const env = item.value.envelope;
      if (options.json || options.feed || true) {
        writeNdjsonFrame({
          version: "vg.4",
          frameType: "event",
          frameId: `frm-${env.seq}`,
          event: env,
        });
      }
    }
  } catch (err) {
    logDiagnostic(`Event tail error: ${String(err)}`);
    return CLI_EXIT_CODES.EXECUTION_FAILED;
  }

  return CLI_EXIT_CODES.SUCCESS;
}
