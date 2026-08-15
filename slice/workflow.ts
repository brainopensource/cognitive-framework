/** Disposable T0b vertical path. No production package may import this file. */

import type { SliceModelProvider } from "./contracts.ts";

export type SliceInput = {
  readonly task: string;
  readonly testArgv: readonly string[];
};

export type TestResult = {
  readonly exitCode: number;
  readonly stdout: string;
  readonly stderr: string;
};

export type SliceResult =
  | { readonly outcome: "rejected"; readonly patch: string }
  | { readonly outcome: "provider_failed" | "patch_invalid"; readonly reason: string }
  | { readonly outcome: "applied" | "tests_failed"; readonly patch: string; readonly test: TestResult };

export interface PatchEnvironment {
  preview(patch: string): Promise<string>;
  apply(patch: string): Promise<void>;
  test(argv: readonly string[]): Promise<TestResult>;
}

export type Approval = (preview: { readonly task: string; readonly patch: string; readonly summary: string }) => Promise<boolean>;

export async function runSlice(
  input: SliceInput,
  provider: SliceModelProvider,
  environment: PatchEnvironment,
  approve: Approval,
): Promise<SliceResult> {
  const proposal = await provider.propose({ blocks: [
    { label: "slice.task", content: input.task },
    { label: "slice.output-contract", content: "Return only a git unified diff. Do not use markdown fences and do not explain it." },
  ] }, [], { temperature: 0, maxTokens: 4096 });
  if (!proposal.ok) return { outcome: "provider_failed", reason: proposal.error.message };

  let patch: string;
  try { patch = extractPatch(proposal.value.text); }
  catch (error) {
    return { outcome: "patch_invalid", reason: error instanceof Error ? error.message : "invalid patch" };
  }

  let summary: string;
  try { summary = await environment.preview(patch); }
  catch (error) {
    return { outcome: "patch_invalid", reason: error instanceof Error ? error.message : "patch preview failed" };
  }
  if (!await approve({ task: input.task, patch, summary })) return { outcome: "rejected", patch };

  try { await environment.apply(patch); }
  catch (error) {
    return { outcome: "patch_invalid", reason: error instanceof Error ? error.message : "patch apply failed" };
  }
  const test = await environment.test(input.testArgv);
  return { outcome: test.exitCode === 0 ? "applied" : "tests_failed", patch, test };
}

export function extractPatch(text: string): string {
  const trimmed = text.trim();
  const unfenced = trimmed.startsWith("```diff") && trimmed.endsWith("```")
    ? trimmed.slice(7, -3).trim()
    : trimmed;
  if (!unfenced.startsWith("diff --git ")) throw new TypeError("provider output is not a git unified diff");
  if (/^diff --git a\/\.\.(?:\/|$)/m.test(unfenced) || /^\+\+\+ b\/\.\.(?:\/|$)/m.test(unfenced)) {
    throw new TypeError("patch attempts to escape the repository");
  }
  return `${unfenced}\n`;
}
