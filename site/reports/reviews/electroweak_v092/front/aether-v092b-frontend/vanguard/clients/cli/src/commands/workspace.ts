import type { ParsedCli } from "../composition/parse-cli.js";
import { NodeFsPersistenceAdapter } from "@aether/client";
import { DEFAULT_FRONTEND_SETTINGS } from "@aether/projections";
import type { FrontendSettings } from "@aether/contracts";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import {
  CLI_EXIT_CODES,
  logDiagnostic,
  writeJsonOutcome,
} from "../output.js";

export async function handleWorkspace(args: string[], options: ParsedCli): Promise<number> {
  const persistence = new NodeFsPersistenceAdapter();
  const subcommand = args[0] || "current";

  if (subcommand === "current") {
    const cwd = process.cwd();
    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "workspace current",
        status: "success",
        data: { workspace: cwd },
      });
    } else {
      console.log(`Current workspace: ${cwd}`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "recent") {
    const recents = (await persistence.loadRecentWorkspaces()) ?? [process.cwd()];
    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "workspace recent",
        status: "success",
        data: { recentWorkspaces: recents },
      });
    } else {
      console.log(`\nRecent Workspaces (${recents.length}):`);
      for (const w of recents) {
        console.log(`  - ${w}`);
      }
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "default") {
    const targetPath = args[1];
    const settings: FrontendSettings = {
      ...DEFAULT_FRONTEND_SETTINGS,
      ...((await persistence.loadSettings()) ?? {}),
    };

    if (!targetPath) {
      const def = settings.general?.defaultWorkspace ?? process.cwd();
      if (options.json) {
        writeJsonOutcome({
          api: "aether.cli-outcome/1",
          command: "workspace default",
          status: "success",
          data: { defaultWorkspace: def },
        });
      } else {
        console.log(`Default workspace: ${def}`);
      }
      return CLI_EXIT_CODES.SUCCESS;
    }

    const fullPath = resolve(targetPath);
    if (!existsSync(fullPath)) {
      logDiagnostic(`Directory does not exist: ${fullPath}`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    const updated: FrontendSettings = {
      ...DEFAULT_FRONTEND_SETTINGS,
      ...settings,
      general: {
        ...DEFAULT_FRONTEND_SETTINGS.general,
        ...(settings.general ?? {}),
        defaultWorkspace: fullPath,
      },
    };
    await persistence.saveSettings(updated);

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "workspace default",
        status: "success",
        data: { defaultWorkspace: fullPath },
      });
    } else {
      console.log(`Default workspace set to: ${fullPath}`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "set" || subcommand === "switch") {
    const targetPath = args[1];
    if (!targetPath) {
      logDiagnostic("Usage: aether workspace set <directory-path>");
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    const fullPath = resolve(targetPath);
    if (!existsSync(fullPath)) {
      logDiagnostic(`Directory does not exist: ${fullPath}`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    const recents: string[] = (await persistence.loadRecentWorkspaces()) ?? [];
    const updatedRecents: string[] = [fullPath, ...recents.filter((r: string) => r !== fullPath)].slice(0, 10);
    await persistence.saveRecentWorkspaces(updatedRecents);

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "workspace set",
        status: "success",
        data: { workspace: fullPath, recentWorkspaces: updatedRecents },
      });
    } else {
      console.log(`Active workspace switched to: ${fullPath}`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  logDiagnostic(`Unknown workspace subcommand '${subcommand}' (supported: current, recent, default, set)`);
  return CLI_EXIT_CODES.INVALID_INPUT;
}
