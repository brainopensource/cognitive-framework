/** Real repository side of the disposable T0b path. Deleted at S4. */

import { spawn } from "node:child_process";
import { realpath } from "node:fs/promises";
import path from "node:path";

import type { PatchEnvironment, TestResult } from "./workflow.ts";

type CommandResult = TestResult;

export class GitPatchEnvironment implements PatchEnvironment {
  private readonly repository: string;

  private constructor(repository: string) { this.repository = repository; }

  static async open(repository: string): Promise<GitPatchEnvironment> {
    const requested = await realpath(path.resolve(repository));
    const result = await command(requested, ["git", "rev-parse", "--show-toplevel"]);
    if (result.exitCode !== 0) throw new TypeError("VG_SLICE_REPO is not a git repository");
    const root = await realpath(result.stdout.trim());
    if (root !== requested) throw new TypeError("VG_SLICE_REPO must name the repository root exactly");
    return new GitPatchEnvironment(root);
  }

  async preview(patch: string): Promise<string> {
    const checked = await command(this.repository, ["git", "apply", "--check", "--whitespace=error-all", "-"], patch);
    if (checked.exitCode !== 0) throw new TypeError(`git apply --check failed: ${checked.stderr.trim()}`);
    const stat = await command(this.repository, ["git", "apply", "--stat", "-"], patch);
    if (stat.exitCode !== 0) throw new TypeError(`git apply --stat failed: ${stat.stderr.trim()}`);
    return stat.stdout.trim();
  }

  async apply(patch: string): Promise<void> {
    const result = await command(this.repository, ["git", "apply", "--whitespace=error-all", "-"], patch);
    if (result.exitCode !== 0) throw new TypeError(`git apply failed: ${result.stderr.trim()}`);
  }

  async test(argv: readonly string[]): Promise<TestResult> {
    if (argv.length === 0) throw new TypeError("test argv must not be empty");
    return command(this.repository, argv);
  }
}

function command(cwd: string, argv: readonly string[], stdin?: string): Promise<CommandResult> {
  return new Promise((resolve, reject) => {
    const child = spawn(argv[0]!, argv.slice(1), { cwd, shell: false, env: process.env });
    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf8").on("data", (chunk: string) => { stdout += chunk; });
    child.stderr.setEncoding("utf8").on("data", (chunk: string) => { stderr += chunk; });
    child.on("error", reject);
    child.on("close", (code) => resolve({ exitCode: code ?? 1, stdout, stderr }));
    if (stdin !== undefined) child.stdin.end(stdin); else child.stdin.end();
  });
}
