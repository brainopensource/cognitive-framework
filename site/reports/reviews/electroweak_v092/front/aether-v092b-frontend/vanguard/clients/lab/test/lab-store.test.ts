import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { LabStore } from "../src/state/lab-store.js";
import type { EventEnvelope, RunSummary } from "@aether/contracts";

function createMockEnvelope(seq: string, kind: string, payload: Record<string, unknown> = {}): EventEnvelope {
  return {
    schemaVersion: "vg.4",
    eventId: `evt-${seq}`,
    scope: "episode",
    runId: "run-test-01",
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
    payload: { kind, ...payload },
  };
}

describe("@aether/lab — LabStore State & Projection Integration", () => {
  it("initializes with clean default state", () => {
    const store = new LabStore();
    const state = store.get();

    assert.equal(state.connectionState, "connected");
    assert.equal(state.mode, "live");
    assert.equal(state.liveTailState, "LIVE");
    assert.equal(state.events.length, 0);
    assert.equal(state.snapshot.status, "pending");
  });

  it("ingests envelopes incrementally and reduces snapshot, trace graph, evidence, and approvals", () => {
    const store = new LabStore();

    store.ingestEnvelope(createMockEnvelope("1", "GoalDeclared", { goal: "Verify substrate" }));
    store.ingestEnvelope(createMockEnvelope("2", "TurnStarted"));
    store.ingestEnvelope(createMockEnvelope("3", "ObservationProduced", { text: "Observed file tree" }));
    store.ingestEnvelope(
      createMockEnvelope("4", "OperatorInvoked", { tool: "view_file", argsSummary: "path=README.md" })
    );
    store.ingestEnvelope(
      createMockEnvelope("5", "ArtifactCreated", { digest: "sha256:abc12345", kindCategory: "manifest" })
    );
    store.ingestEnvelope(
      createMockEnvelope("6", "EvidenceClaimProduced", {
        claimId: "cl-1",
        statement: "Repo is clean",
        status: "verified",
      })
    );
    store.ingestEnvelope(
      createMockEnvelope("7", "ApprovalRequested", {
        approvalId: "app-1",
        unifiedDiff: "+line",
        argsDigest: "sha256:11",
        descriptorDigest: "sha256:22",
      })
    );

    const state = store.get();

    assert.equal(state.events.length, 7);
    assert.equal(state.snapshot.status, "awaiting_approval");
    assert.equal(state.snapshot.thoughts.length, 1);
    assert.equal(state.snapshot.tools.length, 1);
    assert.equal(state.snapshot.artifacts.length, 1);
    assert.equal(state.evidenceGrid.claims.length, 1);
    assert.equal(state.approvalState.pendingChallenges.size, 1);
    assert.equal(state.traceGraph.nodes.length, 7);
  });

  it("filters events by category (errors, approvals, effects, etc.)", () => {
    const store = new LabStore();

    store.ingestEnvelope(createMockEnvelope("1", "GoalDeclared"));
    store.ingestEnvelope(createMockEnvelope("2", "EffectStarted", { tool: "exec" }));
    store.ingestEnvelope(createMockEnvelope("3", "EffectFailed", { error: "Permission denied" }));
    store.ingestEnvelope(createMockEnvelope("4", "ApprovalRequested", { approvalId: "app-1" }));

    store.setEventFilters((prev) => ({ ...prev, category: "errors" }));
    const errorEvents = store.getFilteredEvents();
    assert.equal(errorEvents.length, 1);
    assert.equal(errorEvents[0]?.payload.kind, "EffectFailed");

    store.setEventFilters((prev) => ({ ...prev, category: "approvals" }));
    const approvalEvents = store.getFilteredEvents();
    assert.equal(approvalEvents.length, 1);
    assert.equal(approvalEvents[0]?.payload.kind, "ApprovalRequested");

    store.setEventFilters((prev) => ({ ...prev, category: "all" }));
    const allEvents = store.getFilteredEvents();
    assert.equal(allEvents.length, 4);
  });

  it("tracks unseen live count when user is scrolled up or paused", () => {
    const store = new LabStore();
    store.setIsUserScrolledUp(true);

    store.ingestEnvelope(createMockEnvelope("1", "GoalDeclared"));
    store.ingestEnvelope(createMockEnvelope("2", "TurnStarted"));

    assert.equal(store.get().unseenLiveCount, 2);

    store.jumpToLive();
    assert.equal(store.get().unseenLiveCount, 0);
    assert.equal(store.get().isUserScrolledUp, false);
  });

  it("loads and folds deterministic replay events", () => {
    const store = new LabStore();
    const replayEvents = [
      createMockEnvelope("1", "GoalDeclared", { goal: "Replay Test" }),
      createMockEnvelope("2", "TurnStarted"),
      createMockEnvelope("3", "EpisodeCompleted", { verdict: "satisfied" }),
    ];

    store.loadReplayEvents(replayEvents);
    const state = store.get();

    assert.equal(state.mode, "replay");
    assert.equal(state.events.length, 3);
    assert.equal(state.snapshot.status, "satisfied");
    assert.equal(state.traceGraph.nodes.length, 3);
  });
});
