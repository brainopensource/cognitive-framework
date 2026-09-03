import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { TuiStore, createSignal } from "../src/store.js";
import type { EventEnvelope } from "@aether/contracts";

const SAMPLE_EVENT: EventEnvelope = {
  schemaVersion: "vg.4",
  eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000001",
  scope: "episode",
  runId: "run-tui-1",
  episodeId: "ep-tui-1",
  traceId: "t-1",
  spanId: "s-1",
  seq: "1",
  occurredAt: "2026-08-29T20:00:00.000Z",
  recordedAt: "2026-08-29T20:00:00.001Z",
  principal: "user",
  tenantId: "t",
  ownerId: "o",
  confidentiality: "internal",
  retentionClass: "standard",
  trainability: "prohibited",
  redactionStatus: "none",
  payload: { kind: "GoalDeclared", goal: "Fix race condition in dispatch" },
};

const APPROVAL_EVENT: EventEnvelope = {
  schemaVersion: "vg.4",
  eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000002",
  scope: "governance",
  runId: "run-tui-1",
  episodeId: "ep-tui-1",
  traceId: "t-1",
  spanId: "s-2",
  seq: "2",
  occurredAt: "2026-08-29T20:00:01.000Z",
  recordedAt: "2026-08-29T20:00:01.001Z",
  principal: "agent",
  tenantId: "t",
  ownerId: "o",
  confidentiality: "internal",
  retentionClass: "standard",
  trainability: "prohibited",
  redactionStatus: "none",
  payload: {
    kind: "ApprovalRequested",
    approvalId: "app-tui-01",
    action: "fs.write",
    unifiedDiff: "+fixed",
    argsDigest: "sha256:" + "a".repeat(64),
    descriptorDigest: "sha256:" + "b".repeat(64),
    expiresAt: "2026-08-30T00:00:00.000Z",
  },
};

describe("@aether/tui — Reactive Store & Ingestion", () => {
  it("fine-grained signal reacts to state updates", () => {
    const sig = createSignal(10);
    let captured = 0;
    sig.subscribe((val) => {
      captured = val;
    });

    sig.set(20);
    assert.equal(captured, 20);
  });

  it("ingests event envelopes and projects turns and status", () => {
    const store = new TuiStore();
    store.ingestEnvelope(SAMPLE_EVENT);

    const s = store.get();
    assert.equal(s.runId, "run-tui-1");
    assert.equal(s.turns.length >= 1, true);
    assert.equal(s.turns[0]?.speaker, "user");
    assert.equal(s.turns[0]?.text, "Fix race condition in dispatch");
    assert.equal(s.snapshot.status, "running");
  });

  it("switches focus to approval deck automatically on ApprovalRequested", () => {
    const store = new TuiStore();
    store.ingestEnvelope(SAMPLE_EVENT);
    assert.equal(store.get().focus, "composer");

    store.ingestEnvelope(APPROVAL_EVENT);
    assert.equal(store.get().focus, "approval");
    assert.ok(store.get().pendingApproval);
    assert.equal(store.get().pendingApproval?.approvalId, "app-tui-01");
  });
});
