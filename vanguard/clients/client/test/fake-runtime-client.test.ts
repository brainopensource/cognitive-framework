import { strict as assert } from "node:assert";
import { describe, it } from "node:test";

import { FakeRuntimeClient } from "../src/transports/fake.js";
import type { EventEnvelope } from "@aether/contracts";

/**
 * F4 Phase 0: `@vanguard/client-core`'s `FakeRuntimeClient` had no `@aether/client`
 * equivalent, and Studio's demo mode (`browser-entry.tsx`'s `makeDemoClient()`)
 * depends on it. This covers the ported version against `@aether/client`'s
 * `RuntimeClient` interface, which -- unlike client-core's -- requires
 * `listRuns` and `getCapabilities` rather than treating them as optional.
 */

const EVENT: EventEnvelope = {
  schemaVersion: "vg.4",
  eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8c",
  scope: "episode",
  runId: "demo-run",
  traceId: "trace-1",
  spanId: "span-1",
  seq: "1",
  occurredAt: "2026-08-15T00:00:00.000Z",
  recordedAt: "2026-08-15T00:00:00.000Z",
  principal: "developer-local",
  tenantId: "local",
  ownerId: "local",
  confidentiality: "internal",
  retentionClass: "standard",
  trainability: "prohibited",
  redactionStatus: "none",
  payload: { kind: "GoalDeclared" },
};

describe("@aether/client — FakeRuntimeClient", () => {
  it("replays fixture events and reports run status", async () => {
    const client = new FakeRuntimeClient({
      runs: new Map([["demo-run", { status: "running", events: [EVENT] }]]),
    });

    const events: EventEnvelope[] = [];
    for await (const result of client.streamEvents({ runId: "demo-run" })) {
      assert.equal(result.ok, true);
      if (result.ok) events.push(result.value.envelope);
    }
    assert.equal(events.length, 1);
    assert.equal(events[0].eventId, EVENT.eventId);

    const snapshot = await client.getRun("demo-run");
    assert.equal(snapshot.ok, true);
    if (snapshot.ok) {
      assert.equal(snapshot.value.status, "running");
      assert.equal(snapshot.value.seq, "1");
    }
  });

  it("implements the full RuntimeClient surface, including required listRuns/getCapabilities", async () => {
    const client = new FakeRuntimeClient({
      runs: new Map([["demo-run", { status: "completed", events: [EVENT] }]]),
    });

    const listed = await client.listRuns();
    assert.equal(listed.ok, true);
    if (listed.ok) {
      assert.equal(listed.value.length, 1);
      assert.equal(listed.value[0].runId, "demo-run");
    }

    const capabilities = await client.getCapabilities();
    assert.equal(capabilities.ok, true);
    if (capabilities.ok) assert.equal(capabilities.value.protocol, "vg.4");
  });

  it("fails closed with not_found for unknown runs and artifacts", async () => {
    const client = new FakeRuntimeClient();
    const run = await client.getRun("missing");
    assert.equal(run.ok, false);
    if (!run.ok) assert.equal(run.error.code, "not_found");

    const artifact = await client.explainArtifact("missing-artifact");
    assert.equal(artifact.ok, false);
    if (!artifact.ok) assert.equal(artifact.error.code, "not_found");
  });
});
