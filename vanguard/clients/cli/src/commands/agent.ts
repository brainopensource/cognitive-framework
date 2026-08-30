import { readdirSync, readFileSync, existsSync, statSync } from "node:fs";
import { join, basename } from "node:path";
import type { ParsedCli } from "../composition/parse-cli.js";
import {
  CLI_EXIT_CODES,
  logDiagnostic,
  writeJsonOutcome,
} from "../output.js";

type AgentManifestSummary = {
  id: string;
  name: string;
  path: string;
  version?: string;
  role?: string;
};

function scanLocalAgents(dir: string = process.cwd()): AgentManifestSummary[] {
  const agents: AgentManifestSummary[] = [];
  const candidateDirs = [
    join(dir, "agents"),
    join(dir, ".aether", "agents"),
    join(dir, "vanguard", "packages", "agency"),
  ];

  for (const cDir of candidateDirs) {
    if (existsSync(cDir)) {
      try {
        const files = readdirSync(cDir);
        for (const file of files) {
          if (file.endsWith(".json") || file.endsWith(".yaml") || file.endsWith(".yml") || file.endsWith(".py")) {
            const id = basename(file, file.includes(".") ? file.slice(file.lastIndexOf(".")) : "");
            agents.push({
              id,
              name: id,
              path: join(cDir, file),
            });
          }
        }
      } catch {
        /* ignore read errors */
      }
    }
  }

  // Always include default core agent
  if (!agents.some((a) => a.id === "coding-agent" || a.id === "vg-code-default")) {
    agents.push({
      id: "coding-agent",
      name: "AETHER Default Coding Agent",
      path: "built-in://coding-agent",
      version: "0.9.1",
      role: "Software Engineering Substrate",
    });
  }

  return agents;
}

export async function handleAgent(args: string[], options: ParsedCli): Promise<number> {
  const subcommand = args[0] || "list";

  if (subcommand === "list") {
    const agents = scanLocalAgents(options.repo);
    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "agent list",
        status: "success",
        data: { agents },
      });
    } else {
      console.log(`\nDiscovered Local Agents (${agents.length}):`);
      for (const ag of agents) {
        console.log(`  ${ag.id.padEnd(24)} ${ag.path}`);
      }
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "inspect" || subcommand === "show") {
    const agentId = args[1];
    if (!agentId) {
      logDiagnostic("Missing <agent-id> for agent inspect");
      return CLI_EXIT_CODES.INVALID_INPUT;
    }
    const agents = scanLocalAgents(options.repo);
    const match = agents.find((a) => a.id === agentId);
    if (!match) {
      logDiagnostic(`Agent '${agentId}' not found`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }
    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "agent inspect",
        status: "success",
        data: match,
      });
    } else {
      console.log(`\nAgent: ${match.name} (${match.id})`);
      console.log(`Path:  ${match.path}`);
      if (match.role) console.log(`Role:  ${match.role}`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "validate") {
    const manifestPath = args[1];
    if (!manifestPath) {
      logDiagnostic("Missing <manifest-path> for agent validate");
      return CLI_EXIT_CODES.INVALID_INPUT;
    }
    if (!existsSync(manifestPath)) {
      logDiagnostic(`Manifest not found: ${manifestPath}`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }
    try {
      const content = readFileSync(manifestPath, "utf-8");
      if (manifestPath.endsWith(".json")) {
        JSON.parse(content);
      }
      if (options.json) {
        writeJsonOutcome({
          api: "aether.cli-outcome/1",
          command: "agent validate",
          status: "success",
          data: { valid: true, path: manifestPath },
        });
      } else {
        console.log(`Valid manifest: ${manifestPath}`);
      }
      return CLI_EXIT_CODES.SUCCESS;
    } catch (err) {
      logDiagnostic(`Validation failed: ${String(err)}`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }
  }

  logDiagnostic(`Unknown agent subcommand '${subcommand}' (supported: list, inspect, validate)`);
  return CLI_EXIT_CODES.INVALID_INPUT;
}
