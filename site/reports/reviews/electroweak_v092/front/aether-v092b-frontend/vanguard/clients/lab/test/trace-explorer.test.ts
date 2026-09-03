import { strict as assert } from "node:assert";
import { describe, it, before } from "node:test";
import { LabStore } from "../src/state/lab-store.js";
import { renderTraceWorkbench } from "../src/components/workbenches/TraceWorkbench.js";
import { setupDomMock } from "./dom-mock.js";
import type { EventEnvelope } from "@aether/contracts";

function createMockEnvelope(
  seq: string,
  kind: string,
  parentEventId?: string
): EventEnvelope {
  return {
    schemaVersion: "vg.4",
    eventId: `evt-${seq}`,
    scope: "episode",
    traceId: "trace-01",
    spanId: `span-${seq}`,
    parentEventId,
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
    payload: { kind, goal: `Goal ${seq}` },
  };
}

describe("@aether/lab — Causal Trace Explorer Graph", () => {
  before(() => {
    setupDomMock();
  });

  it("renders SVG causal graph elements and handles causal edges", () => {
    const store = new LabStore();
    store.ingestEnvelope(createMockEnvelope("1", "GoalDeclared"));
    store.ingestEnvelope(createMockEnvelope("2", "ModelProposalProduced", "evt-1"));
    store.ingestEnvelope(createMockEnvelope("3", "EffectStarted", "evt-2"));
    store.ingestEnvelope(createMockEnvelope("4", "ArtifactCreated", "evt-3"));

    const el = renderTraceWorkbench(store);
    assert.equal(el.className, "aether-trace-workbench");

    const graph = store.get().traceGraph;
    assert.equal(graph.nodes.length, 4);
    assert.ok(graph.edges.length >= 3);
  });
});
