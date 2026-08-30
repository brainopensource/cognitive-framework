import type { ParsedCli } from "../composition/parse-cli.js";
import { clientFor } from "../composition/client-for.js";
import {
  CLI_EXIT_CODES,
  exitCodeForErrorCode,
  logDiagnostic,
  writeJsonOutcome,
} from "../output.js";

export async function handleDaemon(args: string[], options: ParsedCli): Promise<number> {
  const action = args[0] || "status";
  const client = clientFor(options);

  if (action === "status") {
    const res = await client.getDaemonStatus();
    if (!res.ok) {
      logDiagnostic(`Daemon is unreachable at ${options.socketPath || "/tmp/vanguard-runtime.sock"}`);
      if (options.json) {
        writeJsonOutcome({
          api: "aether.cli-outcome/1",
          command: "daemon status",
          status: "error",
          error: {
            code: "not_available",
            message: res.error.message,
            retryable: true,
          },
        });
      }
      return CLI_EXIT_CODES.DAEMON_UNAVAILABLE;
    }

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "daemon status",
        status: "success",
        data: res.value,
      });
    } else {
      console.log(`Runtime daemon is ${res.value.status.toUpperCase()} at ${res.value.socketPath}`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (action === "start") {
    logDiagnostic("Daemon start should be invoked via Python Runtime service manager (`python3 -m vanguard.packages.runtime.service.server`)");
    return CLI_EXIT_CODES.INVALID_INPUT;
  }

  if (action === "stop") {
    logDiagnostic("Daemon stop: terminating local socket connections");
    return CLI_EXIT_CODES.SUCCESS;
  }

  logDiagnostic(`Unknown daemon action '${action}' (supported: status, start, stop)`);
  return CLI_EXIT_CODES.INVALID_INPUT;
}
