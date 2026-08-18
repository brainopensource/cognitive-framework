import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { createInterface } from "node:readline";
import { fileURLToPath } from "node:url";

import { jsonLine } from "./commands.js";
import { renderProjectionLines } from "./coding-receipts.js";
import {
  exitCodeForOutcome,
  type CodingExitCode,
  type CodingProjection,
  type CodingRequest,
  type CodingTerminalResult,
} from "./coding-types.js";

export type CodingBackend = {
  invoke(request: CodingRequest): Promise<{
    result: CodingTerminalResult;
    exitCode: CodingExitCode;
  }>;
};

function findRepoRoot(start: string): string {
  let dir = start;
  for (let i = 0; i < 12; i++) {
    if (existsSync(join(dir, "tools", "002_LLM_API_MOCK", "models.json"))) {
      return dir;
    }
    if (existsSync(join(dir, "vanguard", "packages", "runtime"))) {
      return dir;
    }
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return process.env.VANGUARD_ROOT ?? process.cwd();
}

/**
 * Invoke the thin Python coding entrypoint. The TypeScript client never
 * routes models, dispatches effects, or implements recovery loops.
 */
export function createPythonCodingBackend(options?: {
  pythonBin?: string;
  module?: string;
  cwd?: string;
  pythonPath?: string;
}): CodingBackend {
  const pythonBin = options?.pythonBin ?? process.env.VANGUARD_PYTHON ?? "python3";
  const module = options?.module ?? "vanguard.packages.runtime.coding_entrypoint";
  const cwd =
    options?.cwd ??
    process.env.VANGUARD_ROOT ??
    findRepoRoot(fileURLToPath(new URL(".", import.meta.url)));
  const pythonPath = options?.pythonPath ?? [cwd, process.env.PYTHONPATH ?? ""]
    .filter(Boolean)
    .join(":");

  return {
    async invoke(request: CodingRequest) {
      return new Promise((resolve, reject) => {
        const child = spawn(pythonBin, ["-m", module, "--stdin-json"], {
          cwd,
          stdio: ["pipe", "pipe", "pipe"],
          env: { ...process.env, PYTHONPATH: pythonPath },
        });
        const projections: CodingProjection[] = [];
        let terminal: CodingTerminalResult | null = null;
        let stderr = "";

        const rl = createInterface({ input: child.stdout });
        rl.on("line", (line) => {
          if (!line.trim()) return;
          let parsed: Record<string, unknown>;
          try {
            parsed = JSON.parse(line) as Record<string, unknown>;
          } catch {
            return;
          }
          if (parsed.type === "projection" && parsed.projection) {
            projections.push(parsed.projection as CodingProjection);
            return;
          }
          if (parsed.type === "result" && parsed.result) {
            terminal = {
              ...(parsed.result as CodingTerminalResult),
              projections,
            };
          }
        });

        child.stderr.on("data", (chunk) => {
          stderr += String(chunk);
        });

        child.on("error", (error) => reject(error));
        child.on("close", (code) => {
          if (!terminal) {
            const outcome =
              code === 3 ? "unavailable" : code === 2 ? "invalid_request" : "instrument_error";
            terminal = {
              runId: request.runId ?? "unknown",
              outcome,
              phase: "failed",
              attempts: 0,
              turns: 0,
              planDigest: null,
              activeStepId: null,
              verifiedStepIds: [],
              modelRoutes: [],
              promptTokens: null,
              completionTokens: null,
              spentUsdMicros: null,
              detail: stderr.trim() || `coding_entrypoint exited ${code ?? "null"}`,
              projections,
            };
          }
          const mapped = exitCodeForOutcome(terminal.outcome);
          resolve({ result: terminal, exitCode: mapped });
        });

        child.stdin.write(JSON.stringify(request));
        child.stdin.end();
      });
    },
  };
}

export async function runCodingCommand(
  request: CodingRequest,
  write: (line: string) => void,
  backend: CodingBackend = createPythonCodingBackend()
): Promise<CodingExitCode> {
  try {
    const { result, exitCode } = await backend.invoke(request);
    const human = !request.headless && !request.json;
    for (const line of renderProjectionLines(result.projections, { human })) {
      write(line);
    }
    if (request.json || request.headless) {
      write(jsonLine({ type: "result", result }));
    } else if (result.projections.every((p) => p.kind !== "complete")) {
      write(
        renderProjectionLines(
          [
            {
              kind: "complete",
              outcome: result.outcome,
              turns: result.turns,
              spentUsdMicros: result.spentUsdMicros,
            },
          ],
          { human: true }
        )[0]!
      );
    }
    return exitCode;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    write(jsonLine({ ok: false, error: { code: "not_available", message, retryable: false } }));
    return 3;
  }
}
