import test from "node:test";
import assert from "node:assert/strict";
import { FixedClock, FixedEvaluatorPort, FixedIndexPort, InMemoryBlobStore, InMemoryEnvironmentAdapter, InMemoryEventStore, ScriptedModelProvider, SeededRandom } from "./index.ts";

test("fake clock and random are deterministic", () => {
  assert.equal(new FixedClock().now(), "2000-01-01T00:00:00.000Z");
  assert.deepEqual(new SeededRandom(7).next(), new SeededRandom(7).next());
});

test("fake model returns typed script exhaustion instead of throwing", async () => {
  const provider = new ScriptedModelProvider([]);
  const result = await provider.propose({ blocks: [] }, [], { temperature: 0, maxTokens: 1 });
  assert.equal(result.ok, false);
  if (!result.ok) assert.equal(result.error.kind, "instrument_error");
});

test("in-memory blob store preserves immutable copies", async () => {
  const store = new InMemoryBlobStore();
  const bytes = new Uint8Array([1, 2, 3]);
  const put = await store.put({ bytes, classification: "internal" });
  assert.equal(put.ok, true);
  if (!put.ok) return;
  bytes[0] = 9;
  const read = await store.get(put.value);
  assert.equal(read.ok, true);
  if (read.ok) assert.deepEqual([...read.value.bytes], [1, 2, 3]);
});

test("event store rejects non-monotonic append", async () => {
  const store = new InMemoryEventStore();
  const event = { schemaVersion: "vg.4", eventId: "00000000-0000-7000-8000-000000000001", scope: "episode", runId: "run", episodeId: "episode", seq: "1", occurredAt: "2000-01-01T00:00:00.000Z", recordedAt: "2000-01-01T00:00:00.000Z", principal: "test", tenantId: "test", ownerId: "test", confidentiality: "internal", retentionClass: "standard", trainability: "prohibited", redactionStatus: "complete", payload: { kind: "EpisodeStarted" } } as const;
  assert.equal((await store.append([event])).ok, true);
  const duplicate = await store.append([event]);
  assert.equal(duplicate.ok, false);
  if (!duplicate.ok) assert.equal(duplicate.error.kind, "conflict");
});

test("environment, evaluator and index fakes provide deterministic typed values", async () => {
  const environment = new InMemoryEnvironmentAdapter({ "/repo/readme": "hello" });
  const snapshot = await environment.snapshot();
  assert.equal(snapshot.ok, true);
  const evaluator = new FixedEvaluatorPort({ outcome: "inconclusive", claims: [], reason: "fixed fixture" });
  const evaluation = await evaluator.evaluate({ runId: "run", episodeId: "episode" }, "sha256:0000000000000000000000000000000000000000000000000000000000000000");
  assert.deepEqual(evaluation, { ok: true, value: { outcome: "inconclusive", claims: [], reason: "fixed fixture" } });
  const index = new FixedIndexPort([{ ref: "repo/readme", score: 1 }]);
  assert.deepEqual(await index.query({ text: "readme", limit: 1 }), { ok: true, value: [{ ref: "repo/readme", score: 1 }] });
});
