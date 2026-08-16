import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { explain, streamRun, streamTrace } from "../src/application/commands.js";
import { ReplayRuntimeClient } from "../src/adapters/replay.js";
import { LiveRuntimeClient } from "../src/adapters/live.js";
import { jsonLine } from "../src/headless/jsonl.js";
import { parseEventEnvelope } from "../src/contract/parse.js";
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

function parseLines(lines: string[]): StreamItem[] {
  return lines.map((line) => {
    assert.equal(line.includes("\u001b"), false, "headless stdout must not contain terminal escapes");
    const parsed = JSON.parse(line) as StreamItem;
    assert.equal(parsed.contractVersion, "0.1");
    assert.equal(parsed.envelope.schemaVersion, "vg.4");
    assert.equal(typeof parsed.envelope.payload.kind, "string");
    return parsed;
  });
}

test("headless run parses live EventEnvelope JSONL without terminal escapes", async () => {
  const envelopes = cassette.trim().split("\n").map((line) => JSON.parse(line) as EventEnvelope);
  async function* lines() {
    for (const envelope of envelopes) yield JSON.stringify(envelope);
  }
  const collected: string[] = [];
  await streamRun(new LiveRuntimeClient(lines()), { repo: ".", headless: true, runId: "run-1" }, (line: string) => collected.push(line));
  const items = parseLines(collected);
  assert.equal(items[0]?.source, "live");
  assert.equal(items[0]?.envelope.payload.kind, "EpisodeStarted");
  assert.ok(items.some((item) => item.envelope.payload.kind === "EpisodeCompleted"));
  assert.equal(items.at(-1)?.envelope.seq, envelopes.at(-1)?.seq);
});

test("trace renders a timeline from a golden cassette JSONL without invoking a model", async () => {
  const client = ReplayRuntimeClient.fromJsonl(cassette);
  const collected: string[] = [];
  await streamTrace(client, "run-1", (line: string) => collected.push(line));
  const items = parseLines(collected);
  assert.equal(items[0]?.source, "replay");
  assert.deepEqual(items.map((item) => item.envelope.payload.kind), [
    "EpisodeStarted",
    "EpisodeStateChanged",
    "EffectPreviewed",
    "EpisodeCompleted",
  ]);
  assert.deepEqual(items.map((item) => item.envelope.seq), ["1", "2", "3", "4"]);
});

test("why displays activation evidence projected from recorded JSONL events", async () => {
  const client = ReplayRuntimeClient.fromJsonl(whyCassette);
  let value = "";
  await explain(client, "typed-tools", (line: string) => {
    value = line;
  });
  assert.equal(value.includes("\u001b"), false);
  const explanation = JSON.parse(value);
  assert.equal(explanation.artifactId, "typed-tools");
  assert.equal(explanation.status, "active");
  assert.ok(explanation.activatedBy.length > 0);
  assert.ok(explanation.demotedBy.length > 0);
  assert.equal(explanation.freshness.source, "replay");
});

test("jsonLine emits a single parseable object with no escape sequences", () => {
  const line = jsonLine({ contractVersion: "0.1", source: "replay", envelope: { payload: { kind: "UnknownFutureEvent" } } });
  assert.equal(line.includes("\u001b"), false);
  assert.equal(JSON.parse(line).envelope.payload.kind, "UnknownFutureEvent");
});

test("LiveRuntimeClient supports startRun and headless prompt stream", async () => {
  const envelopes = cassette.trim().split("\n").map((l) => JSON.parse(l) as EventEnvelope);
  async function* lines() {
    for (const e of envelopes) yield JSON.stringify(e);
  }
  const client = new LiveRuntimeClient(lines(), { repo: "./test-repo", prompt: "fix bug in main.py" });
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
    { repo: "./test-repo", prompt: "fix bug in main.py", headless: true, runId: "run-live-test" },
    (line: string) => collected.push(line)
  );
  const items = parseLines(collected);
  assert.equal(items[0]?.source, "live");
  assert.equal(items[0]?.envelope.payload.kind, "EpisodeStarted");
});

test("LiveRuntimeClient supports lifecycle operations without failing not_available", async () => {
  const client = new LiveRuntimeClient(undefined, { runId: "run-ops-1" });
  const started = await client.startRun({ repo: ".", runId: "run-ops-1" });
  assert.equal(started.ok, true);

  const runSnap = await client.getRun("run-ops-1");
  assert.equal(runSnap.ok, true);
  if (runSnap.ok) {
    assert.equal(runSnap.value.runId, "run-ops-1");
  }

  const artifact = await client.explainArtifact("art-1");
  assert.equal(artifact.ok, true);

  const approval = await client.resolveApproval({ approvalId: "appr-1", decision: "approve" });
  assert.equal(approval.ok, true);

  const correction = await client.recordCorrection({
    episodeId: "ep-1",
    proposedPatchDigest: "sha256:1111",
    acceptedPatchDigest: "sha256:2222",
    reasonCodes: ["functional_defect"],
    magnitude: "minor",
    scope: "repo",
    correctingPrincipalRole: "operator",
  });
  assert.equal(correction.ok, true);

  const cancel = await client.requestCancel("run-ops-1");
  assert.equal(cancel.ok, true);
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
  const envelopes = cassette.trim().split("\n").map((l) => JSON.parse(l) as EventEnvelope);
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

  const client = new LiveRuntimeClient(lines());
  const received: EventEnvelope[] = [];
  for await (const item of client.streamEvents({ runId: "run-1", afterSeq: "1" })) {
    if (item.ok) received.push(item.value.envelope);
  }

  // afterSeq: "1" should skip seq 1, and duplicate seq 2 should be dropped
  assert.equal(received.length, 3);
  assert.deepEqual(received.map((e) => e.seq), ["2", "3", "4"]);
});

test("LiveRuntimeClient reports daemon status cleanly", async () => {
  const client = new LiveRuntimeClient(undefined, { socketPath: "/tmp/mock-runtime.sock" });
  const status = await client.getDaemonStatus();
  assert.equal(status.ok, true);
  if (status.ok) {
    assert.equal(status.value.socketPath, "/tmp/mock-runtime.sock");
    assert.equal(status.value.version, "0.4.0");
  }
});



