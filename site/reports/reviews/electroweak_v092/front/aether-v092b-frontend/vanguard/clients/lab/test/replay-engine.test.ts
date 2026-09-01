import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { ReplayEngine } from "../src/state/replay-engine.js";
import type { EventEnvelope } from "@aether/contracts";

function createMockEvent(seq: string): EventEnvelope {
  return {
    schemaVersion: "vg.4",
    eventId: `evt-${seq}`,
    scope: "episode",
    traceId: "trace-01",
    spanId: `span-${seq}`,
    seq,
    occurredAt: "2026-08-29T20:00:00.000Z",
    recordedAt: "2026-08-29T20:00:00.050Z",
    principal: "operator",
    tenantId: "tenant-default",
    ownerId: "owner-default",
    confidentiality: "public",
    retentionClass: "standard",
    trainability: "allowed",
    redactionStatus: "none",
    payload: { kind: "ObservationProduced", text: `Step ${seq}` },
  };
}

describe("@aether/lab — Historical Replay Engine", () => {
  it("steps forward and backward through recorded events", () => {
    const events = [createMockEvent("1"), createMockEvent("2"), createMockEvent("3")];
    let stepCount = 0;
    const engine = new ReplayEngine(events, (visible) => {
      stepCount = visible.length;
    });

    assert.equal(engine.get().currentIndex, 0);

    engine.stepForward();
    assert.equal(engine.get().currentIndex, 1);
    assert.equal(stepCount, 2);

    engine.stepForward();
    assert.equal(engine.get().currentIndex, 2);
    assert.equal(stepCount, 3);

    // Boundary check: cannot step past end
    engine.stepForward();
    assert.equal(engine.get().currentIndex, 2);

    engine.stepBackward();
    assert.equal(engine.get().currentIndex, 1);
    assert.equal(stepCount, 2);
  });

  it("jumps to sequence and beginning/end", () => {
    const events = [createMockEvent("10"), createMockEvent("20"), createMockEvent("30")];
    const engine = new ReplayEngine(events);

    engine.jumpToSeq("20");
    assert.equal(engine.get().currentIndex, 1);
    assert.equal(engine.get().currentSeq, "20");

    engine.jumpToEnd();
    assert.equal(engine.get().currentIndex, 2);

    engine.jumpToBeginning();
    assert.equal(engine.get().currentIndex, 0);
  });

  it("updates replay speed multiplier cleanly", () => {
    const engine = new ReplayEngine([createMockEvent("1")]);
    assert.equal(engine.get().speed, 1);

    engine.setSpeed(5);
    assert.equal(engine.get().speed, 5);

    engine.setSpeed(100);
    assert.equal(engine.get().speed, 100);
  });
});
