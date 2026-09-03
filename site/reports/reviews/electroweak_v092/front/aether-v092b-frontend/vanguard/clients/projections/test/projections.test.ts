import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import {
  emptyRunSnapshot,
  reduceRunSnapshot,
  foldEvents,
  toTraceGraph,
  emptyEvidenceGrid,
  reduceEvidence,
  toConversationTurns,
  emptyApprovalState,
  reduceApprovalState,
} from "../src/index.js";
import type { EventEnvelope } from "@aether/contracts";

const FIXTURE_EVENTS: EventEnvelope[] = [
  {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000001",
    scope: "episode",
    runId: "run-p-1",
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
    payload: { kind: "GoalDeclared", goal: "Fix lease leak in kernel dispatch" },
  },
  {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000002",
    scope: "episode",
    runId: "run-p-1",
    parentEventId: "018f3a2b-7c4d-7e1f-9a2b-000000000001",
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
    payload: { kind: "ObservationProduced", text: "Analyzing kernel dispatch pipeline" },
  },
  {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000003",
    scope: "episode",
    runId: "run-p-1",
    parentEventId: "018f3a2b-7c4d-7e1f-9a2b-000000000002",
    traceId: "t-1",
    spanId: "s-3",
    seq: "3",
    occurredAt: "2026-08-29T20:00:02.000Z",
    recordedAt: "2026-08-29T20:00:02.001Z",
    principal: "agent",
    tenantId: "t",
    ownerId: "o",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: {
      kind: "ApprovalRequested",
      approvalId: "app-k06",
      action: "fs.write",
      unifiedDiff: "--- a/dispatch.py\n+++ b/dispatch.py\n@@ -1 +1 @@\n-old\n+new",
      argsDigest: "sha256:" + "a".repeat(64),
      descriptorDigest: "sha256:" + "b".repeat(64),
      expiresAt: "2026-08-30T00:00:00.000Z",
    },
  },
  {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000004",
    scope: "governance",
    runId: "run-p-1",
    parentEventId: "018f3a2b-7c4d-7e1f-9a2b-000000000003",
    traceId: "t-1",
    spanId: "s-4",
    seq: "4",
    occurredAt: "2026-08-29T20:00:03.000Z",
    recordedAt: "2026-08-29T20:00:03.001Z",
    principal: "operator",
    tenantId: "t",
    ownerId: "o",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: {
      kind: "ApprovalResolved",
      approvalId: "app-k06",
      resolution: "approved",
    },
  },
  {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000005",
    scope: "episode",
    runId: "run-p-1",
    parentEventId: "018f3a2b-7c4d-7e1f-9a2b-000000000004",
    traceId: "t-1",
    spanId: "s-5",
    seq: "5",
    occurredAt: "2026-08-29T20:00:04.000Z",
    recordedAt: "2026-08-29T20:00:04.001Z",
    principal: "agent",
    tenantId: "t",
    ownerId: "o",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: {
      kind: "ArtifactCreated",
      digest: "sha256:" + "c".repeat(64),
      kindCategory: "patch",
      path: "vanguard/packages/kernel/dispatch.py",
    },
  },
  {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000006",
    scope: "episode",
    runId: "run-p-1",
    parentEventId: "018f3a2b-7c4d-7e1f-9a2b-000000000005",
    traceId: "t-1",
    spanId: "s-6",
    seq: "6",
    occurredAt: "2026-08-29T20:00:05.000Z",
    recordedAt: "2026-08-29T20:00:05.001Z",
    principal: "evaluator",
    tenantId: "t",
    ownerId: "o",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: {
      kind: "EpisodeCompleted",
      verdict: "satisfied",
    },
  },
];

describe("@aether/projections — RunSnapshot", () => {
  it("folds events deterministically into RunSnapshotModel", () => {
    const snapshot = foldEvents(FIXTURE_EVENTS, "run-p-1");
    assert.equal(snapshot.runId, "run-p-1");
    assert.equal(snapshot.status, "satisfied");
    assert.equal(snapshot.verdict, "satisfied");
    assert.equal(snapshot.thoughts.length, 1);
    assert.equal(snapshot.thoughts[0], "Analyzing kernel dispatch pipeline");
    assert.equal(snapshot.artifacts.length, 1);
    assert.equal(snapshot.artifacts[0]?.path, "vanguard/packages/kernel/dispatch.py");
    assert.equal(snapshot.lastSeq, "6");
  });
});

describe("@aether/projections — TraceGraph", () => {
  it("generates causal DAG linking parents to children", () => {
    const graph = toTraceGraph(FIXTURE_EVENTS);
    assert.equal(graph.nodes.length, 6);
    assert.equal(graph.edges.length, 5);
    assert.equal(graph.edges[0]?.source, "018f3a2b-7c4d-7e1f-9a2b-000000000001");
    assert.equal(graph.edges[0]?.target, "018f3a2b-7c4d-7e1f-9a2b-000000000002");
  });
});

describe("@aether/projections — EvidenceGrid", () => {
  it("tracks created artifacts and verdicts", () => {
    let grid = emptyEvidenceGrid("run-p-1");
    for (const env of FIXTURE_EVENTS) {
      grid = reduceEvidence(grid, env);
    }
    assert.equal(grid.artifacts.length, 1);
    assert.equal(grid.verdicts.length, 1);
    assert.equal(grid.verdicts[0]?.verdict, "satisfied");
  });
});

describe("@aether/projections — ConversationTurns", () => {
  it("groups prompt and thoughts into structured turns with activity cards", () => {
    const turns = toConversationTurns(FIXTURE_EVENTS);
    assert.ok(turns.length >= 2);
    assert.equal(turns[0]?.speaker, "user");
    assert.equal(turns[0]?.text, "Fix lease leak in kernel dispatch");
    assert.equal(turns[1]?.speaker, "agent");
    assert.equal(turns[1]?.text, "Analyzing kernel dispatch pipeline");
    assert.equal(turns[1]?.verdict, "satisfied");
  });
});

describe("@aether/projections — ApprovalState", () => {
  it("transitions pending challenge to resolved", () => {
    let state = emptyApprovalState();
    state = reduceApprovalState(state, FIXTURE_EVENTS[2]!); // ApprovalRequested
    assert.equal(state.pendingChallenges.size, 1);
    assert.ok(state.pendingChallenges.has("app-k06"));

    state = reduceApprovalState(state, FIXTURE_EVENTS[3]!); // ApprovalResolved
    assert.equal(state.pendingChallenges.size, 0);
    assert.equal(state.resolvedApprovals.length, 1);
    assert.equal(state.resolvedApprovals[0]?.status, "approved");
  });
});
