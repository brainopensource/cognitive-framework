import type { ParsedCli } from "../composition/parse-cli.js";
import { clientFor } from "../composition/client-for.js";
import {
  CLI_EXIT_CODES,
  exitCodeForErrorCode,
  logDiagnostic,
  writeJsonOutcome,
} from "../output.js";

export async function handleDoctor(args: string[], options: ParsedCli): Promise<number> {
  const client = clientFor(options) as any;

  const [statusRes, capRes] = await Promise.all([
    client.getDaemonStatus(),
    typeof client.getCapabilities === "function"
      ? client.getCapabilities()
      : Promise.resolve({ ok: true, value: { mode: "standard", capabilities: ["StartRun", "GetRun", "StreamEvents"] } }),
  ]);

  const report = {
    healthy: statusRes.ok && capRes.ok,
    daemon: statusRes.ok ? statusRes.value : { status: "unreachable", error: statusRes.error.message },
    capabilities: capRes.ok ? capRes.value : { error: capRes.error.message },
    nodeVersion: process.version,
    platform: process.platform,
    arch: process.arch,
  };

  if (options.json) {
    writeJsonOutcome({
      api: "aether.cli-outcome/1",
      command: "doctor",
      status: report.healthy ? "success" : "error",
      data: report,
    });
  } else {
    console.log("\nAETHER / Vanguard System Doctor:");
    console.log(`  Platform:     ${report.platform} (${report.arch})`);
    console.log(`  Node/Bun:     ${report.nodeVersion}`);
    console.log(`  Daemon:       ${statusRes.ok ? "ONLINE (" + statusRes.value.socketPath + ")" : "OFFLINE"}`);
    if (capRes.ok) {
      console.log(`  Capabilities: OK`);
    } else {
      console.log(`  Capabilities: UNREACHABLE`);
    }
  }

  return report.healthy ? CLI_EXIT_CODES.SUCCESS : CLI_EXIT_CODES.DAEMON_UNAVAILABLE;
}
