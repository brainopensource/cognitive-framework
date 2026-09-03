import type { ParsedCli } from "../composition/parse-cli.js";
import { clientFor } from "../composition/client-for.js";
import {
  CLI_EXIT_CODES,
  exitCodeForErrorCode,
  logDiagnostic,
  writeJsonOutcome,
} from "../output.js";

export async function handleArtifact(args: string[], options: ParsedCli): Promise<number> {
  const subcommand = args[0];
  const client = await clientFor(options) as any;

  if (!subcommand || subcommand === "--help") {
    logDiagnostic("Usage: aether artifact explain <digest> [--json]");
    logDiagnostic("       aether artifact get <digest> [--output <path>]");
    logDiagnostic("       aether artifact list <run-id> [--json]");
    return CLI_EXIT_CODES.INVALID_INPUT;
  }

  if (subcommand === "explain") {
    const digest = args[1] || options.runId;
    if (!digest) {
      logDiagnostic("Missing <digest> or <artifact-id> for artifact explain");
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    const res = await client.explainArtifact(digest, { substrateProfile: options.profile });
    if (!res.ok) {
      logDiagnostic(`Explain artifact failed [${res.error.code}]: ${res.error.message}`);
      if (options.json) {
        writeJsonOutcome({
          api: "aether.cli-outcome/1",
          command: "artifact explain",
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
        command: "artifact explain",
        status: "success",
        data: res.value,
      });
    } else {
      console.log(`\nArtifact Provenance: ${digest}`);
      console.log(`Status:     ${res.value.status ?? "recorded"}`);
      if (res.value.prediction) console.log(`Prediction: ${res.value.prediction}`);
      if (res.value.activatedBy && res.value.activatedBy.length > 0) {
        console.log(`Activated By: ${res.value.activatedBy.join(", ")}`);
      }
      if (res.value.demotedBy && res.value.demotedBy.length > 0) {
        console.log(`Demoted By:   ${res.value.demotedBy.join(", ")}`);
      }
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "get") {
    const digest = args[1];
    if (!digest) {
      logDiagnostic("Missing <digest> for artifact get");
      return CLI_EXIT_CODES.INVALID_INPUT;
    }
    // Documented BACKEND-GAP: raw blob store retrieval endpoint is pending in RuntimeService
    const gapMessage = `BACKEND-GAP: Direct blob content retrieval for '${digest}' is pending RuntimeService BlobStore endpoint. Direct database or filesystem access is forbidden per architecture boundaries.`;
    logDiagnostic(gapMessage);
    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "artifact get",
        status: "error",
        error: {
          code: "not_available",
          message: gapMessage,
          retryable: false,
          detail: "BACKEND-GAP: BlobStore content route pending",
        },
      });
    }
    return CLI_EXIT_CODES.DAEMON_UNAVAILABLE;
  }

  if (subcommand === "list") {
    const runId = args[1] || options.runId;
    if (!runId) {
      logDiagnostic("Missing <run-id> for artifact list");
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    const res = await client.getRun(runId);
    if (!res.ok) {
      logDiagnostic(`Failed to inspect run ${runId} for artifacts: ${res.error.message}`);
      return exitCodeForErrorCode(res.error.code);
    }

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "artifact list",
        runId,
        status: "success",
        data: { artifacts: (res.value as any).metrics?.artifacts ?? [] },
      });
    } else {
      console.log(`\nArtifacts for run ${runId}:`);
      console.log("  (Check run inspect for comprehensive artifact breakdown)");
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  logDiagnostic(`Unknown artifact subcommand '${subcommand}' (supported: explain, get, list)`);
  return CLI_EXIT_CODES.INVALID_INPUT;
}
