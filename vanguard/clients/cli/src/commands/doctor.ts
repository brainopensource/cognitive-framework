import type { ParsedCli } from "../composition/parse-cli.js";
import { clientFor } from "../composition/client-for.js";
import { NodeFsPersistenceAdapter, DEFAULT_PROVIDERS } from "@aether/client";
import { DEFAULT_FRONTEND_SETTINGS } from "@aether/projections";
import type { ModelProviderConfig } from "@aether/contracts";
import {
  CLI_EXIT_CODES,
  writeJsonOutcome,
} from "../output.js";

export async function handleDoctor(args: string[], options: ParsedCli): Promise<number> {
  const client = clientFor(options) as any;
  const persistence = new NodeFsPersistenceAdapter();

  const [statusRes, capRes, settings, providers] = await Promise.all([
    client.getDaemonStatus(),
    typeof client.getCapabilities === "function"
      ? client.getCapabilities()
      : Promise.resolve({ ok: true, value: { mode: "standard", capabilities: ["StartRun", "GetRun", "StreamEvents"] } }),
    persistence.loadSettings().then((s) => s ?? DEFAULT_FRONTEND_SETTINGS),
    persistence.loadProviders().then((p) => p ?? DEFAULT_PROVIDERS),
  ]);

  const defaultProvider = (providers as ModelProviderConfig[]).find((p: ModelProviderConfig) => p.isDefault) ?? (providers as ModelProviderConfig[])[0];
  let credState = "NOT_CONFIGURED";
  if (defaultProvider?.credentialKeyRef) {
    credState = await persistence.getCredentialState(defaultProvider.credentialKeyRef);
  }

  const report = {
    healthy: statusRes.ok && capRes.ok,
    daemon: statusRes.ok ? statusRes.value : { status: "unreachable", error: statusRes.error?.message },
    capabilities: capRes.ok ? capRes.value : { error: capRes.error?.message },
    provider: {
      defaultProviderId: defaultProvider?.id ?? "none",
      defaultModel: defaultProvider?.selectedModel ?? "none",
      credentialStatus:
        credState === "CONFIGURED"
          ? "READY"
          : credState === "INVALID"
          ? "INVALID"
          : "MISSING CREDENTIAL",
    },
    workspace: {
      defaultWorkspace: (settings as any).general?.defaultWorkspace ?? process.cwd(),
      currentDirectory: process.cwd(),
    },
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
    console.log(`  Platform:         ${report.platform} (${report.arch})`);
    console.log(`  Node/Bun:         ${report.nodeVersion}`);
    console.log(`  Daemon:           ${statusRes.ok ? "ONLINE (" + (statusRes.value.socketPath ?? "/tmp/vanguard-runtime.sock") + ")" : "OFFLINE (" + (statusRes.error?.message ?? "unreachable") + ")"}`);
    console.log(`  Capabilities:     ${capRes.ok ? "OK" : "UNREACHABLE"}`);
    console.log(`  Default Provider: ${report.provider.defaultProviderId} [${report.provider.credentialStatus}]`);
    console.log(`  Default Model:    ${report.provider.defaultModel}`);
    console.log(`  Default Dir:      ${report.workspace.defaultWorkspace}`);
  }

  return report.healthy ? CLI_EXIT_CODES.SUCCESS : CLI_EXIT_CODES.DAEMON_UNAVAILABLE;
}
