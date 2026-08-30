import { readdirSync, readFileSync, existsSync } from "node:fs";
import { join, basename } from "node:path";
import type { ParsedCli } from "../composition/parse-cli.js";
import {
  CLI_EXIT_CODES,
  logDiagnostic,
  writeJsonOutcome,
} from "../output.js";

type WorkflowSummary = {
  id: string;
  name: string;
  path: string;
  description?: string;
};

function scanLocalWorkflows(dir: string = process.cwd()): WorkflowSummary[] {
  const workflows: WorkflowSummary[] = [];
  const candidateDirs = [
    join(dir, "workflows"),
    join(dir, ".aether", "workflows"),
    join(dir, "vanguard", "packages", "runtime"),
  ];

  for (const cDir of candidateDirs) {
    if (existsSync(cDir)) {
      try {
        const files = readdirSync(cDir);
        for (const file of files) {
          if (file.endsWith(".json") || file.endsWith(".yaml") || file.endsWith(".yml") || file.endsWith(".py")) {
            const id = basename(file, file.includes(".") ? file.slice(file.lastIndexOf(".")) : "");
            workflows.push({
              id,
              name: id,
              path: join(cDir, file),
            });
          }
        }
      } catch {
        /* ignore */
      }
    }
  }

  if (!workflows.some((w) => w.id === "default-turn-loop")) {
    workflows.push({
      id: "default-turn-loop",
      name: "Default Turn Loop Workflow",
      path: "built-in://default-turn-loop",
      description: "Observe -> Decide -> Authorize -> Execute -> Record loop",
    });
  }

  return workflows;
}

export async function handleWorkflow(args: string[], options: ParsedCli): Promise<number> {
  const subcommand = args[0] || "list";

  if (subcommand === "list") {
    const workflows = scanLocalWorkflows(options.repo);
    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "workflow list",
        status: "success",
        data: { workflows },
      });
    } else {
      console.log(`\nDiscovered Local Workflows (${workflows.length}):`);
      for (const wf of workflows) {
        console.log(`  ${wf.id.padEnd(24)} ${wf.path}`);
      }
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "inspect" || subcommand === "show") {
    const wfId = args[1];
    if (!wfId) {
      logDiagnostic("Missing <workflow-id> for workflow inspect");
      return CLI_EXIT_CODES.INVALID_INPUT;
    }
    const workflows = scanLocalWorkflows(options.repo);
    const match = workflows.find((w) => w.id === wfId);
    if (!match) {
      logDiagnostic(`Workflow '${wfId}' not found`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }
    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "workflow inspect",
        status: "success",
        data: match,
      });
    } else {
      console.log(`\nWorkflow: ${match.name} (${match.id})`);
      console.log(`Path:     ${match.path}`);
      if (match.description) console.log(`Description: ${match.description}`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "validate") {
    const manifestPath = args[1];
    if (!manifestPath) {
      logDiagnostic("Missing <manifest-path> for workflow validate");
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
          command: "workflow validate",
          status: "success",
          data: { valid: true, path: manifestPath },
        });
      } else {
        console.log(`Valid workflow manifest: ${manifestPath}`);
      }
      return CLI_EXIT_CODES.SUCCESS;
    } catch (err) {
      logDiagnostic(`Validation failed: ${String(err)}`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }
  }

  logDiagnostic(`Unknown workflow subcommand '${subcommand}' (supported: list, inspect, validate)`);
  return CLI_EXIT_CODES.INVALID_INPUT;
}
