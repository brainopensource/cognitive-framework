import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import {
  approveDecision,
  explain,
  manageDaemon,
  resumeRun,
  streamRun,
  streamTrace,
} from "../src/application/commands.js";
import { ReplayRuntimeClient } from "../src/adapters/replay.js";
import { LiveRuntimeClient } from "../src/adapters/live.js";
import { jsonLine } from "../src/headless/jsonl.js";
import { parseEventEnvelope, parseJsonlLine } from "../src/contract/parse.js";
import {
  SHORT_FLAG_BINDINGS,
  parseCliOptions,
  wantsHelp,
} from "../src/composition/parse-cli.js";
import type { EventEnvelope, StreamItem } from "../src/contract/types.js";

function packageRoot(): string {
  let dir = dirname(fileURLToPath(import.meta.url));
  while (!existsSync(join(dir, "package.json"))) {
    const parent = dirname(dir);
    if (parent === dir) throw new Error("package root not found");
    dir = parent;
  }
  return dir;
}

const fixtures = join(packageRoot(), "fixtures");
const cassette = readFileSync(join(fixtures, "successful-episode.jsonl"), "utf8");
const whyCassette = readFileSync(join(fixtures, "why-typed-tools.jsonl"), "utf8");

function envelopesFromJsonl(text: string): EventEnvelope[] {
  const envelopes: EventEnvelope[] = [];
  for (const line of text.split(/\r?\n/)) {
    if (!line.trim()) continue;
    const parsed = parseJsonlLine(line);
    if (!parsed.ok) throw new Error(parsed.error.message);
    envelopes.push(parsed.value);
  }
  return envelopes;
}

function parseLines(lines: string[], expectedSource: StreamItem["source"] = "replay"): StreamItem[] {
  return lines.map((line) => {
    assert.equal(line.includes(""), false, "headless stdout must not contain terminal escapes");
    const parsed = JSON.parse(line) as StreamItem;
    assert.equal(parsed.contractVersion, "vg.4");
    assert.equal(parsed.source, expectedSource);
    assert.equal(parsed.envelope.schemaVersion, "vg.4");
    assert.equal(typeof parsed.envelope.payload.kind, "string");
    return parsed;
  });
}

test("headless run parses live EventEnvelope JSONL without terminal escapes", async () => {
  // F4 Phase 5: feed-fed streaming lives on ReplayRuntimeClient now --
  // LiveRuntimeClient (SocketRuntimeClient) is socket-only, no feed mode.
  const envelopes = envelopesFromJsonl(cassette);
  const client = ReplayRuntimeClient.fromEnvelopes(envelopes);
  const collected: string[] = [];
  await streamRun(client, { repo: ".", headless: true, runId: envelopes[0]!.runId! }, (line: string) => collected.push(line));
  const items = parseLines(collected);
  assert.equal(items[0]?.envelope.payload.kind, "EpisodeStarted");
  assert.ok(items.some((item) => item.envelope.payload.kind === "EpisodeCompleted"));
  assert.equal(items.at(-1)?.envelope.seq, envelopes.at(-1)?.seq);
});

test("trace renders a timeline from a golden cassette JSONL without invoking a model", async () => {
  const client = ReplayRuntimeClient.fromEnvelopes(envelopesFromJsonl(cassette));
  const collected: string[] = [];
  await streamTrace(client, "run-1", (line: string) => collected.push(line));
  const items = parseLines(collected);
  assert.deepEqual(items.map((item) => item.envelope.payload.kind), [
    "EpisodeStarted",
    "EpisodeStateChanged",
    "EffectPreviewed",
    "EpisodeCompleted",
  ]);
  assert.deepEqual(items.map((item) => item.envelope.seq), ["1", "2", "3", "4"]);
});

test("why displays activation evidence projected from recorded JSONL events", async () => {
  const client = ReplayRuntimeClient.fromEnvelopes(envelopesFromJsonl(whyCassette));
  let value = "";
  await explain(client, "typed-tools", (line: string) => {
    value = line;
  });
  assert.equal(value.includes(""), false);
  const explanation = JSON.parse(value);
  assert.equal(explanation.artifactId, "typed-tools");
  assert.equal(explanation.status, "replay_mock");
});

test("jsonLine emits a single parseable object with no escape sequences", () => {
  const line = jsonLine({ contractVersion: "vg.4", source: "replay", envelope: { payload: { kind: "UnknownFutureEvent" } } });
  assert.equal(line.includes(""), false);
  assert.equal(JSON.parse(line).envelope.payload.kind, "UnknownFutureEvent");
});

test("LiveRuntimeClient supports startRun and headless prompt stream", async () => {
  const envelopes = envelopesFromJsonl(cassette);
  const client = ReplayRuntimeClient.fromEnvelopes(envelopes);
  const started = await client.startRun({
    repo: "./test-repo",
    prompt: "fix bug in main.py",
    runId: "run-live-test",
  });
  assert.equal(started.ok, true);
  if (started.ok) {
    assert.equal(started.value.runId, "run-live-test");
  }

  const collected: string[] = [];
  await streamRun(
    client,
    { repo: "./test-repo", prompt: "fix bug in main.py", headless: true, runId: envelopes[0]!.runId! },
    (line: string) => collected.push(line)
  );
  const items = parseLines(collected);
  assert.equal(items[0]?.envelope.payload.kind, "EpisodeStarted");
});

test("LiveRuntimeClient refuses lifecycle stubs when no daemon peer exists", async () => {
  const client = new LiveRuntimeClient({ socketPath: "/tmp/missing-vg-commands-test.sock" });
  const started = await client.startRun({ repo: ".", runId: "run-ops-1" });
  assert.equal(started.ok, false);
  if (!started.ok) {
    assert.equal(started.error.code, "not_available");
  }

  const runSnap = await client.getRun("run-ops-1");
  assert.equal(runSnap.ok, false);

  const artifact = await client.explainArtifact("art-1");
  assert.equal(artifact.ok, false);

  const approval = await client.resolveApproval({ approvalId: "appr-1", decision: "approve" });
  assert.equal(approval.ok, false);

  const correction = await client.recordCorrection({
    correction: {
      correctionId: "corr-1",
      runId: "run-ops-1",
      reasonCode: "functional_defect",
      scope: "general",
      recordedAt: new Date().toISOString(),
      author: "operator",
    },
  });
  assert.equal(correction.ok, false);

  const cancel = await client.requestCancel("run-ops-1");
  assert.equal(cancel.ok, false);
});

test("parseEventEnvelope strictly rejects non-UUID, invalid timestamp, and missing fields", () => {
  const valid = JSON.parse(cassette.trim().split("\n")[0]!) as EventEnvelope;
  assert.equal(parseEventEnvelope(valid).ok, true);

  // Non-UUID eventId
  const badUuid = { ...valid, eventId: "not-a-uuid" };
  const resUuid = parseEventEnvelope(badUuid);
  assert.equal(resUuid.ok, false);
  if (!resUuid.ok) assert.equal(resUuid.error.message.includes("UUID"), true);

  // Invalid schema version
  const badVersion = { ...valid, schemaVersion: "vg.3" };
  const resVer = parseEventEnvelope(badVersion);
  assert.equal(resVer.ok, false);

  // Invalid timestamp
  const badTime = { ...valid, occurredAt: "yesterday" };
  const resTime = parseEventEnvelope(badTime);
  assert.equal(resTime.ok, false);

  // Missing seq
  const missingSeq = { ...valid, seq: undefined };
  const resSeq = parseEventEnvelope(missingSeq);
  assert.equal(resSeq.ok, false);
});

test("LiveRuntimeClient drops duplicate frames and respects afterSeq cursor", async () => {
  const envelopes = envelopesFromJsonl(cassette);
  // Feed frames with duplicates: seq 1, 2, 2, 3, 4
  const framesWithDuplicates = [
    envelopes[0]!,
    envelopes[1]!,
    envelopes[1]!, // duplicate
    envelopes[2]!,
    envelopes[3]!,
  ];

  async function* lines() {
    for (const f of framesWithDuplicates) yield JSON.stringify(f);
  }

  const client = new ReplayRuntimeClient(lines());
  const received: EventEnvelope[] = [];
  for await (const item of client.streamEvents({ runId: "run-1", afterSeq: "1" })) {
    if (item.ok) received.push(item.value.envelope);
  }

  // afterSeq: "1" should skip seq 1, and duplicate seq 2 should be dropped
  assert.equal(received.length, 3);
  assert.deepEqual(received.map((e) => e.seq), ["2", "3", "4"]);
});

test("LiveRuntimeClient reports daemon unreachable when the socket has no peer", async () => {
  const client = new LiveRuntimeClient({ socketPath: "/tmp/mock-runtime.sock" });
  const status = await client.getDaemonStatus();
  assert.equal(status.ok, false);
  if (!status.ok) {
    assert.equal(status.error.code, "not_available");
  }
});

test("streamRun returns exit code 0 for satisfied outcome", async () => {
  const envelopes = envelopesFromJsonl(cassette);
  const client = ReplayRuntimeClient.fromEnvelopes(envelopes);
  const linesOut: string[] = [];
  const exitCode = await streamRun(client, { repo: ".", headless: true, runId: envelopes[0]!.runId! }, (l) => linesOut.push(l));
  assert.equal(exitCode, 0);
  assert.equal(linesOut.length, 4);
});

test("approveDecision fails closed when the live daemon is not on the wire", async () => {
  const client = new LiveRuntimeClient({ socketPath: "/tmp/missing-vg-commands-test-2.sock" });
  const linesApprove: string[] = [];
  const codeApprove = await approveDecision(client, "appr-123", "approve", (l) => linesApprove.push(l));
  assert.equal(codeApprove, 2);

  const linesReject: string[] = [];
  const codeReject = await approveDecision(client, "appr-123", "reject", (l) => linesReject.push(l));
  assert.equal(codeReject, 2);
});

test("approveDecision maps approve and reject to stable exit codes on a JSONL feed", async () => {
  async function* empty() {
    return;
  }
  const client = new ReplayRuntimeClient(empty());
  const linesApprove: string[] = [];
  const codeApprove = await approveDecision(client, "appr-123", "approve", (l) => linesApprove.push(l));
  assert.equal(codeApprove, 0);
  assert.equal(JSON.parse(linesApprove[0]!).status, "completed");

  const linesReject: string[] = [];
  const codeReject = await approveDecision(client, "appr-123", "reject", (l) => linesReject.push(l));
  assert.equal(codeReject, 1);
});

test("manageDaemon fails closed when the daemon socket has no peer", async () => {
  const client = new LiveRuntimeClient({ socketPath: "/tmp/test-commands.sock" });
  const linesDaemon: string[] = [];
  const code = await manageDaemon(client, "status", (l) => linesDaemon.push(l));
  assert.equal(code, 2);
  assert.equal(JSON.parse(linesDaemon[0]!).ok, false);
});

test("ReplayRuntimeClient rejects recordCorrection with permission_denied", async () => {
  const client = ReplayRuntimeClient.fromEnvelopes(envelopesFromJsonl(cassette));
  const res = await client.recordCorrection({
    correction: {
      correctionId: "corr-1",
      runId: "run-1",
      reasonCode: "functional_defect",
      scope: "general",
      recordedAt: new Date().toISOString(),
      author: "operator",
    },
  });
  assert.equal(res.ok, false);
  if (!res.ok) {
    assert.equal(res.error.code, "permission_denied");
  }
});

// ---------------------------------------------------------------------------
// T-97: CLI product surface — help exits zero, `-m` binds explicitly
// ---------------------------------------------------------------------------

function cliBin(): string {
  return join(packageRoot(), "dist/src/main.js");
}

function runCli(args: string[]): { status: number; text: string } {
  const result = spawnSync(process.execPath, [cliBin(), ...args], {
    encoding: "utf8",
    // A help request must not reach a provider. Removing every credential from
    // the child proves that on the harness rather than by inspection: a run
    // that tried to call one could not succeed here.
    env: Object.fromEntries(
      Object.entries(process.env).filter(([key]) => !/API_KEY|AUTH_TOKEN|SECRET/i.test(key))
    ) as NodeJS.ProcessEnv,
  });
  return { status: result.status ?? -1, text: `${result.stdout}${result.stderr}` };
}

test("T-97: help exits zero for every subcommand without a completion frame", () => {
  // Before repair, `vg code --help` fell through to the coding handler and
  // printed `[complete] instrument_error, 0 turns, unknown` with exit 3.
  for (const args of [
    ["--help"],
    ["-h"],
    ["code", "--help"],
    ["code", "-h"],
    ["explain", "--help"],
    ["doctor", "--help"],
    ["run", "--help"],
    ["resume", "--help"],
    ["code", ".", "--brief", "do a thing", "--help"],
  ]) {
    const { status, text } = runCli(args);
    assert.equal(status, 0, `exit code for ${args.join(" ")}`);
    assert.ok(text.includes("Usage:"), `usage text for ${args.join(" ")}`);
    assert.equal(
      /\[complete\]/.test(text),
      false,
      `help emitted a completion frame for ${args.join(" ")}`
    );
    assert.equal(/\[complete\]|instrument_error/.test(text), false, args.join(" "));
  }
});

test("T-97: help documents every bound short flag and claims no others", () => {
  const { text } = runCli(["code", "--help"]);
  for (const [short, long] of Object.entries(SHORT_FLAG_BINDINGS)) {
    assert.ok(text.includes(short), `help omits ${short}`);
    assert.ok(text.includes(long), `help omits ${long}`);
  }
  assert.deepEqual(Object.keys(SHORT_FLAG_BINDINGS).sort(), ["-h", "-m", "-y"]);
});

test("T-97: wantsHelp reads a request, not a flag value", () => {
  assert.equal(wantsHelp(["code", "--help"]), true);
  assert.equal(wantsHelp(["code", "-h"]), true);
  assert.equal(wantsHelp(["code", "."]), false);
  // `--help` in the value position of a value flag is that flag's value.
  assert.equal(wantsHelp(["code", ".", "--brief", "--help"]), false);
  assert.equal(wantsHelp(["code", ".", "--prompt", "-h"]), false);
});

test("T-97: -m binds to --model and its value never leaks into the brief", () => {
  const parsed = parseCliOptions([".", "-m", "openrouter/anthropic/claude-3"]);
  assert.equal(parsed.flagError, undefined);
  assert.equal(parsed.model, "openrouter/anthropic/claude-3");
  assert.equal(parsed.plannerModel, "openrouter/anthropic/claude-3");
  // The defect this replaces: the value was dropped from the flag and appended
  // to the task brief, where nothing downstream could see what happened.
  assert.equal((parsed.prompt ?? "").includes("claude-3"), false);
  assert.equal((parsed.brief ?? "").includes("claude-3"), false);
});

test("T-97: a conflicting -m/--model pair is refused, never silently resolved", () => {
  const conflicting = parseCliOptions([".", "--model", "model-a", "-m", "model-b"]);
  assert.notEqual(conflicting.flagError, undefined);
  assert.match(conflicting.flagError!, /-m/);
  assert.match(conflicting.flagError!, /--model/);
  // The losing spellings are named so the operator is told what -m is NOT.
  for (const losing of ["--manifest", "--model-port", "--max-turns"]) {
    assert.ok(conflicting.flagError!.includes(losing), losing);
  }
  // The same value twice is not a conflict.
  assert.equal(parseCliOptions([".", "--model", "m", "-m", "m"]).flagError, undefined);
  // A different long flag beside -m is not a conflict either.
  const distinct = parseCliOptions([".", "--manifest", "vg-code-max", "-m", "claude-3"]);
  assert.equal(distinct.flagError, undefined);
  assert.equal(distinct.model, "claude-3");
  assert.equal(distinct.manifest, "vg-code-max");
});

test("T-97: an unbound short flag errors instead of swallowing its value", () => {
  for (const short of ["-M", "-p", "-x"]) {
    const parsed = parseCliOptions([".", short, "some-value"]);
    assert.notEqual(parsed.flagError, undefined, short);
    assert.match(parsed.flagError!, /short flags are never inferred/);
  }
  // The bound ones stay bound.
  for (const short of Object.keys(SHORT_FLAG_BINDINGS)) {
    assert.equal(parseCliOptions([".", short]).flagError, undefined, short);
  }
});

test("T-97: an ambiguous invocation exits non-zero before any execution", () => {
  const { status, text } = runCli(["code", ".", "--model", "a", "-m", "b"]);
  assert.notEqual(status, 0);
  assert.equal(status, 2);
  assert.equal(/\[complete\]/.test(text), false, "ambiguity produced a completion frame");
  const unknown = runCli(["code", ".", "-M", "b"]);
  assert.notEqual(unknown.status, 0);
  assert.equal(/\[complete\]/.test(unknown.text), false);
});

test("T-97: non-success execution still returns non-zero", () => {
  // No daemon, no provider credentials: the run cannot succeed, and the CLI
  // must say so with a non-zero status rather than a zero-exit success frame.
  const { status } = runCli(["code", ".", "--headless", "--max-turns", "1"]);
  assert.notEqual(status, 0);
});
