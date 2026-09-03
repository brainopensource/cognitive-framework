import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
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
