import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { explain, streamRun, streamTrace } from "../src/application/commands.js";
import { ReplayRuntimeClient } from "../src/adapters/replay.js";
import { LiveRuntimeClient } from "../src/adapters/live.js";
import { jsonLine } from "../src/headless/jsonl.js";
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
