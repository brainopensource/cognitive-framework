import assert from "node:assert/strict";
import test from "node:test";

import type { SliceModelProvider } from "./contracts.ts";
import { extractPatch, runSlice, type PatchEnvironment } from "./workflow.ts";

const patch = "diff --git a/a.txt b/a.txt\n--- a/a.txt\n+++ b/a.txt\n@@ -1 +1 @@\n-old\n+new\n";

const provider = (text = patch): SliceModelProvider => ({
  async propose() { return { ok: true, value: { text, toolCalls: [] } }; },
});

class FakeEnvironment implements PatchEnvironment {
  readonly calls: string[] = [];
  async preview(value: string) { this.calls.push("preview"); assert.equal(value, patch); return "a.txt | 2"; }
  async apply(value: string) { this.calls.push("apply"); assert.equal(value, patch); }
  async test(argv: readonly string[]) { this.calls.push("test"); assert.deepEqual(argv, ["python3", "-m", "unittest"]); return { exitCode: 0, stdout: "OK", stderr: "" }; }
}

test("full slice orders proposal, preview, approval, apply, test and result", async () => {
  const environment = new FakeEnvironment();
  const result = await runSlice({ task: "change a", testArgv: ["python3", "-m", "unittest"] }, provider(), environment, async ({ summary }) => {
    environment.calls.push("approval"); assert.equal(summary, "a.txt | 2"); return true;
  });
  assert.equal(result.outcome, "applied");
  assert.deepEqual(environment.calls, ["preview", "approval", "apply", "test"]);
});

test("rejection never applies or tests", async () => {
  const environment = new FakeEnvironment();
  const result = await runSlice({ task: "change a", testArgv: ["python3", "-m", "unittest"] }, provider(), environment, async () => false);
  assert.equal(result.outcome, "rejected");
  assert.deepEqual(environment.calls, ["preview"]);
});

test("non-patch provider output fails before approval", async () => {
  const environment = new FakeEnvironment();
  const result = await runSlice({ task: "change a", testArgv: ["python3"] }, provider("looks good"), environment, async () => true);
  assert.equal(result.outcome, "patch_invalid");
  assert.deepEqual(environment.calls, []);
});

test("extractPatch rejects an explicit parent traversal", () => {
  assert.throws(() => extractPatch("diff --git a/../x b/../x\n--- a/../x\n+++ b/../x"), /escape/);
});
