import type { ParsedCli } from "../composition/parse-cli.js";
import { NodeFsPersistenceAdapter } from "@aether/client";
import { DEFAULT_FRONTEND_SETTINGS } from "@aether/projections";
import type { FrontendSettings } from "@aether/contracts";
import {
  CLI_EXIT_CODES,
  logDiagnostic,
  writeJsonOutcome,
} from "../output.js";

export async function handleConfig(args: string[], options: ParsedCli): Promise<number> {
  const persistence = new NodeFsPersistenceAdapter();
  const subcommand = args[0] || "show";

  if (subcommand === "show") {
    const loaded = (await persistence.loadSettings()) ?? {};
    const settings: FrontendSettings = {
      ...DEFAULT_FRONTEND_SETTINGS,
      ...loaded,
      runtime: { ...DEFAULT_FRONTEND_SETTINGS.runtime, ...(loaded.runtime ?? {}) },
      appearance: { ...DEFAULT_FRONTEND_SETTINGS.appearance, ...(loaded.appearance ?? {}) },
      general: { ...DEFAULT_FRONTEND_SETTINGS.general, ...(loaded.general ?? {}) },
      terminal: { ...DEFAULT_FRONTEND_SETTINGS.terminal, ...(loaded.terminal ?? {}) },
      accessibility: { ...DEFAULT_FRONTEND_SETTINGS.accessibility, ...(loaded.accessibility ?? {}) },
    };

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "config show",
        status: "success",
        data: { settings },
      });
    } else {
      console.log("\nAETHER Configuration:");
      console.log(`  runtime.socketPath:       ${settings.runtime.socketPath}`);
      console.log(`  runtime.reconnectMax:     ${settings.runtime.maxReconnectAttempts}`);
      console.log(`  general.defaultWorkspace:  ${settings.general.defaultWorkspace}`);
      console.log(`  general.defaultAgent:      ${settings.general.defaultAgent}`);
      console.log(`  general.defaultWorkflow:   ${settings.general.defaultWorkflow}`);
      console.log(`  appearance.theme:         ${settings.appearance.theme}`);
      console.log(`  terminal.tuiColorMode:    ${settings.terminal.tuiColorMode}`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "set") {
    const key = args[1];
    const value = args[2];
    if (!key || value === undefined) {
      logDiagnostic("Usage: aether config set <key> <value>");
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    const loaded = (await persistence.loadSettings()) ?? {};
    const settings: FrontendSettings = {
      ...DEFAULT_FRONTEND_SETTINGS,
      ...loaded,
      runtime: { ...DEFAULT_FRONTEND_SETTINGS.runtime, ...(loaded.runtime ?? {}) },
      appearance: { ...DEFAULT_FRONTEND_SETTINGS.appearance, ...(loaded.appearance ?? {}) },
      general: { ...DEFAULT_FRONTEND_SETTINGS.general, ...(loaded.general ?? {}) },
      terminal: { ...DEFAULT_FRONTEND_SETTINGS.terminal, ...(loaded.terminal ?? {}) },
      accessibility: { ...DEFAULT_FRONTEND_SETTINGS.accessibility, ...(loaded.accessibility ?? {}) },
    };

    if (key === "runtime.socketPath") {
      settings.runtime.socketPath = value;
    } else if (key === "general.defaultWorkspace") {
      settings.general.defaultWorkspace = value;
    } else if (key === "general.defaultAgent") {
      settings.general.defaultAgent = value;
    } else if (key === "general.defaultWorkflow") {
      settings.general.defaultWorkflow = value;
    } else if (key === "appearance.theme") {
      settings.appearance.theme = value as any;
    } else if (key === "terminal.tuiColorMode") {
      settings.terminal.tuiColorMode = value as any;
    } else {
      logDiagnostic(`Unknown configuration key '${key}'`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    await persistence.saveSettings(settings);

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "config set",
        status: "success",
        data: { key, value, settings },
      });
    } else {
      console.log(`Config updated: ${key} = ${value}`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "reset") {
    await persistence.saveSettings(DEFAULT_FRONTEND_SETTINGS);
    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "config reset",
        status: "success",
        data: { settings: DEFAULT_FRONTEND_SETTINGS },
      });
    } else {
      console.log("Configuration reset to defaults.");
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  logDiagnostic(`Unknown config subcommand '${subcommand}' (supported: show, set, reset)`);
  return CLI_EXIT_CODES.INVALID_INPUT;
}
