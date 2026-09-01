import { OperatorSigner } from "@aether/client";
import type { ParsedCli } from "../composition/parse-cli.js";
import { clientFor } from "../composition/client-for.js";
import {
  CLI_EXIT_CODES,
  exitCodeForErrorCode,
  logDiagnostic,
  writeJsonOutcome,
} from "../output.js";

export async function handleApprove(args: string[], options: ParsedCli): Promise<number> {
  const approvalId = args.find((a) => !a.startsWith("-")) || options.runId;
  const decisionArg = options.decision ?? (args.includes("approve") ? "approve" : args.includes("reject") ? "reject" : undefined);

  if (!approvalId || !decisionArg) {
    logDiagnostic("Usage: aether approve <approval-id> --decision approve|reject");
    return CLI_EXIT_CODES.INVALID_INPUT;
  }

  const client = await clientFor(options);

  try {
    const res = await client.resolveApproval({
      approvalId,
      decision: decisionArg,
    });

    if (!res.ok) {
      logDiagnostic(`Approval resolution failed [${res.error.code}]: ${res.error.message}`);
      if (options.json) {
        writeJsonOutcome({
          api: "aether.cli-outcome/1",
          command: "approve",
          status: "error",
          error: {
            code: res.error.code,
            message: res.error.message,
            retryable: res.error.retryable,
          },
        });
      }
      return exitCodeForErrorCode(res.error.code);
    }

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "approve",
        status: "success",
        data: res.value,
      });
    } else {
      console.log(`Successfully resolved approval ${approvalId} with decision: ${decisionArg}`);
    }

    return CLI_EXIT_CODES.SUCCESS;
  } catch (err) {
    logDiagnostic(`Error resolving approval: ${String(err)}`);
    return CLI_EXIT_CODES.EXECUTION_FAILED;
  }
}
