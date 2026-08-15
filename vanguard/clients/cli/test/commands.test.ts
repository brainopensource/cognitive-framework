import test from "node:test";
import assert from "node:assert/strict";
import { explain, streamRun } from "../src/commands.js";
import { MockRuntime } from "../src/mock-runtime.js";

test("headless run emits checkpoints and a completion event as JSON lines", async () => {
  const lines: string[] = [];
  await streamRun(new MockRuntime(), { repo: ".", runId: "test-run", headless: true, checkpointEvery: 2 }, (line) => lines.push(line));
  const events = lines.map((line) => JSON.parse(line));
  assert.equal(events[0].type, "run.started");
  assert.ok(events.some((event) => event.type === "checkpoint.created"));
  assert.equal(events.at(-1).type, "run.completed");
});

test("why returns inspectable activation and demotion evidence", async () => {
  let value = "";
  await explain(new MockRuntime(), "typed-tools", (line) => { value = line; });
  const explanation = JSON.parse(value);
  assert.equal(explanation.status, "active");
  assert.ok(explanation.activatedBy.length > 0);
  assert.ok(explanation.demotedBy.length > 0);
});

test("a cancelled run records a resumable cancellation event", async () => {
  const runtime = new MockRuntime();
  const stream = runtime.run({ repo: ".", runId: "cancel-run", checkpointEvery: 1 });
  const first = await stream[Symbol.asyncIterator]().next();
  assert.equal(first.value.type, "run.started");
  await runtime.cancel("cancel-run");
  const events = [];
  for await (const event of stream) events.push(event);
  assert.equal(events.at(-1)?.type, "run.cancelled");
});
