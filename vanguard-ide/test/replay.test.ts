// FE-B7 — Replay E2E tests (pyramid level 4): webview works with no daemon.
// Reads vanguard/clients/cli/fixtures/*.jsonl relative to repo root.

import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import * as path from "node:path";
import * as fs from "node:fs";
import { ReplayRuntimeClient } from "../src/adapters/replay";
import { emptyRunView, reduceRunView } from "../src/application/run-view";

const FIXTURES_DIR = path.resolve(__dirname, "../../vanguard/clients/cli/fixtures");

async function collectStream(client: ReplayRuntimeClient, runId: string): Promise<Array<{ kind: string }>> {
  const kinds: Array<{ kind: string }> = [];
  for await (const item of client.streamEvents({ runId })) {
    if (!item.ok) throw new Error(item.error.message);
    kinds.push({ kind: String(item.value.envelope.payload.kind) });
  }
  return kinds;
}

describe("replay adapter — successful-episode.jsonl", () => {
  const fixturePath = path.join(FIXTURES_DIR, "successful-episode.jsonl");
  const text = fs.readFileSync(fixturePath, "utf8");
  const client = ReplayRuntimeClient.fromJsonl(text);

  it("loads fixture without throwing", () => {
    assert.ok(client);
  });

  it("startRun resolves the first runId in the fixture", async () => {
    const result = await client.startRun({ repo: "." });
    assert.ok(result.ok);
    assert.equal(result.value.runId, "run-1");
  });

  it("streamEvents yields EpisodeStarted → EpisodeCompleted in order", async () => {
    const kinds = await collectStream(client, "run-1");
    const kindNames = kinds.map((k) => k.kind);
    assert.ok(kindNames.includes("EpisodeStarted"), "should contain EpisodeStarted");
    assert.ok(kindNames.includes("EpisodeCompleted"), "should contain EpisodeCompleted");
    const startIdx = kindNames.indexOf("EpisodeStarted");
    const endIdx = kindNames.indexOf("EpisodeCompleted");
    assert.ok(startIdx < endIdx, "EpisodeStarted must precede EpisodeCompleted");
  });

  it("run-view reducer produces non-empty lastKind from replay stream", async () => {
    let vm = emptyRunView();
    for await (const item of client.streamEvents({ runId: "run-1" })) {
      if (!item.ok) throw new Error(item.error.message);
      vm = reduceRunView(vm, item.value.envelope);
    }
    assert.ok(vm.lastKind.length > 0, "lastKind must be non-empty after replay");
  });

  it("getDaemonStatus returns stopped (replay mode)", async () => {
    const status = await client.getDaemonStatus();
    assert.ok(status.ok);
    assert.equal(status.value.status, "stopped");
  });

  it("requestCancel returns not_available", async () => {
    const result = await client.requestCancel("run-1");
    assert.ok(!result.ok);
    assert.equal(result.error.code, "not_available");
  });
});

describe("replay adapter — why-typed-tools.jsonl (governance scope)", () => {
  const fixturePath = path.join(FIXTURES_DIR, "why-typed-tools.jsonl");
  const text = fs.readFileSync(fixturePath, "utf8");
  const client = ReplayRuntimeClient.fromJsonl(text);

  it("loads governance fixture without throwing", () => {
    assert.ok(client);
  });

  it("explainArtifact projects ActivationChanged for typed-tools", async () => {
    const result = await client.explainArtifact("typed-tools");
    assert.ok(result.ok);
    assert.equal(result.value.status, "active");
    assert.ok(result.value.activatedBy.length > 0);
  });

  it("explainArtifact for unknown artifact returns unknown status", async () => {
    const result = await client.explainArtifact("does-not-exist");
    assert.ok(result.ok);
    assert.equal(result.value.status, "unknown");
  });
});

describe("ReplayRuntimeClient.fromFile", () => {
  it("loads from filesystem path", () => {
    const fixturePath = path.join(FIXTURES_DIR, "successful-episode.jsonl");
    const client = ReplayRuntimeClient.fromFile(fixturePath);
    assert.ok(client);
  });

  it("throws on invalid JSONL", () => {
    assert.throws(() => {
      ReplayRuntimeClient.fromJsonl('not json at all\n');
    });
  });
});
