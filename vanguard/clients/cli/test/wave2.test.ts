import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { manageDaemon, resumeRun, streamRun } from "../src/application/commands.js";
import { LiveRuntimeClient } from "../src/adapters/live.js";
import { ReplayRuntimeClient } from "../src/adapters/replay.js";
import { parseCliOptions, USAGE, normalizeArgv } from "../src/composition/parse-cli.js";
import { demoFixturePath, packageRootFrom } from "../src/composition/catalog.js";
import { sourceLabel } from "../src/tui/theme/tokens.js";
import { OperatorSigner } from "../src/adapters/signer.js";
import { parseJsonlLine, type EventEnvelope } from "@aether/contracts";

function root(): string {
  return packageRootFrom(import.meta.url);
}

function envelopesFromFile(path: string): EventEnvelope[] {
  const text = readFileSync(path, "utf8");
  const envelopes: EventEnvelope[] = [];
  for (const line of text.split(/\r?\n/)) {
    if (!line.trim()) continue;
    const parsed = parseJsonlLine(line);
    if (!parsed.ok) throw new Error(parsed.error.message);
    envelopes.push(parsed.value);
  }
  return envelopes;
}

test("usage documents all flags", () => {
  for (const flag of ["--demo", "--socket-path", "--manifest", "--replay", "--headless", "--yes", "--help"]) {
    assert.equal(USAGE.includes(flag), true, flag);
  }
  assert.match(USAGE, /aether.*interactive TUI|no args.*interactive/i);
});

test("normalizeArgv defaults a bare invocation to interactive run in .", () => {
  assert.deepEqual(normalizeArgv([]), ["run", "."]);
  assert.deepEqual(normalizeArgv(["--help"]), ["--help"]);
  assert.deepEqual(normalizeArgv(["-h"]), ["-h"]);
  assert.deepEqual(normalizeArgv(["run", "."]), ["run", "."]);
  assert.deepEqual(normalizeArgv(["--model", "openrouter/free"]), ["run", ".", "--model", "openrouter/free"]);
  assert.deepEqual(normalizeArgv(["doctor"]), ["doctor"]);
  assert.deepEqual(normalizeArgv(["."]), ["run", "."]);
});

test("vg --help prints every documented flag", () => {
  const bin = join(root(), "dist/src/main.js");
  const result = spawnSync(process.execPath, [bin, "--help"], { encoding: "utf8" });
  assert.equal(result.status, 0);
  const text = `${result.stdout}${result.stderr}`;
  for (const flag of ["--demo", "--socket-path", "--manifest", "--replay", "--headless", "--yes", "--help"]) {
    assert.equal(text.includes(flag), true, flag);
  }
});

test("parseCliOptions captures --demo scenario", () => {
  const parsed = parseCliOptions(["--demo", "authorization-denied", "--headless"]);
  assert.equal(parsed.demo, true);
  assert.equal(parsed.demoScenario, "authorization-denied");
  assert.equal(parsed.headless, true);
  assert.equal(parsed.promptExplicit, false);
});

test("parseCliOptions marks --prompt as explicit for TUI autostart", () => {
  const flagged = parseCliOptions(["--prompt", "fix tests"]);
  assert.equal(flagged.promptExplicit, true);
  assert.equal(flagged.prompt, "fix tests");
  const implicit = parseCliOptions([]);
  assert.equal(implicit.promptExplicit, false);
});

test("demo replay labels source mock", async () => {
  const path = demoFixturePath(root(), "successful-episode");
  const client = ReplayRuntimeClient.fromEnvelopes(envelopesFromFile(path), "mock");
  const lines: string[] = [];
  await streamRun(client, { repo: ".", headless: true, runId: "run-1" }, (l) => lines.push(l));
  const first = JSON.parse(lines[0]!);
  assert.equal(first.source, "mock");
  assert.equal(sourceLabel("mock"), "source: mock");
});

test("manageDaemon start is not_available (Joint J1)", async () => {
  const client = new LiveRuntimeClient({ socketPath: "/tmp/missing-vg.sock" });
  const lines: string[] = [];
  const code = await manageDaemon(client, "start", (l) => lines.push(l));
  assert.equal(code, 2);
  const body = JSON.parse(lines[0]!);
  assert.equal(body.error.code, "not_available");
  assert.equal(String(body.error.message).includes("J1"), true);
});

test("resumeRun without daemon is not_available and does not emit mock events", async () => {
  const client = new LiveRuntimeClient({ socketPath: "/tmp/missing-vg.sock" });
  const lines: string[] = [];
  const code = await resumeRun(client, { repo: ".", runId: "run-missing", headless: true }, (l) => lines.push(l));
  assert.equal(code, 2);
  assert.equal(JSON.parse(lines[0]!).error.code, "not_available");
  assert.equal(lines.some((line) => line.includes("\"source\":\"mock\"")), false);
});

test("getDaemonStatus does not invent a version string", async () => {
  const client = new LiveRuntimeClient({ socketPath: "/tmp/missing-vg.sock" });
  const status = await client.getDaemonStatus();
  assert.equal(status.ok, false);
});

test("socket resolveApproval refuses empty challenge digests", async () => {
  const client = new LiveRuntimeClient({
    socketPath: "/tmp/missing-vg.sock",
    signer: new OperatorSigner(),
  });
  const result = await client.resolveApproval({ approvalId: "appr-1", decision: "approve" });
  assert.equal(result.ok, false);
  // F4 Phase 5: @aether/client's SocketRuntimeClient checks for a cached
  // ApprovalRequested challenge before attempting any socket I/O -- fails
  // fast and honestly with invalid_request rather than trying (and
  // failing) a network call first for an approval that was never possible
  // to resolve either way.
  if (!result.ok) assert.equal(result.error.code, "invalid_request");
});

test("dead scaffold files are gone", () => {
  const dir = root();
  assert.equal(existsSync(join(dir, "src/commands.ts")), false);
  assert.equal(existsSync(join(dir, "src/runtime.ts")), false);
  assert.equal(existsSync(join(dir, "src/mock-runtime.ts")), false);
});
