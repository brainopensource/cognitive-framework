import test from "node:test";
import assert from "node:assert/strict";
import { runShellCommand } from "../src/commands/shell.js";

test("runShellCommand captures stdout and a zero exit code on success", () => {
  const result = runShellCommand("echo hello-from-shell", "/tmp");
  assert.match(result.stdout, /hello-from-shell/);
  assert.equal(result.exitCode, 0);
  assert.equal(result.truncated, false);
});

test("runShellCommand captures a non-zero exit code without throwing", () => {
  const result = runShellCommand("exit 3", "/tmp");
  assert.equal(result.exitCode, 3);
});

test("runShellCommand captures stderr separately from stdout", () => {
  const result = runShellCommand("echo out; echo err 1>&2", "/tmp");
  assert.match(result.stdout, /out/);
  assert.match(result.stderr, /err/);
});
