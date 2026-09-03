import { spawnSync } from "node:child_process";

export interface ShellResult {
  readonly command: string;
  readonly stdout: string;
  readonly stderr: string;
  readonly exitCode: number;
  readonly truncated: boolean;
}

const MAX_OUTPUT_BYTES = 16_000;
const DEFAULT_TIMEOUT_MS = 15_000;

/**
 * Hermes's zero-cost "!cmd" trick: runs a shell command locally and returns
 * its output as plain text, to be added to the composer/transcript as
 * context -- it never touches the model or the kernel's effect pipeline.
 * This is local developer convenience only; it carries no capability grant
 * and is never routed through the agent's own proc.exec authority.
 */
export function runShellCommand(command: string, cwd: string): ShellResult {
  const proc = spawnSync("/bin/sh", ["-c", command], {
    cwd,
    encoding: "utf-8",
    timeout: DEFAULT_TIMEOUT_MS,
    maxBuffer: MAX_OUTPUT_BYTES * 2,
    stdio: ["ignore", "pipe", "pipe"],
  });

  let stdout = proc.stdout ?? "";
  let stderr = proc.stderr ?? "";
  const exitCode = proc.error ? 1 : (proc.status ?? 1);
  if (proc.error && !stderr) {
    stderr = proc.error.message;
  }

  let truncated = false;
  if (stdout.length > MAX_OUTPUT_BYTES) {
    stdout = stdout.slice(0, MAX_OUTPUT_BYTES);
    truncated = true;
  }
  if (stderr.length > MAX_OUTPUT_BYTES) {
    stderr = stderr.slice(0, MAX_OUTPUT_BYTES);
    truncated = true;
  }

  return { command, stdout, stderr, exitCode, truncated };
}
