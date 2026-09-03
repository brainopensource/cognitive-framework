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

  it("folds ProposalProduced note directly into agent turn without requiring ObservationProduced", () => {
    const makeEnv = (id: string, seq: string, principal: string, payload: any): EventEnvelope => ({
      schemaVersion: "vg.4",
      eventId: id,
      scope: "episode",
      runId: "run-p-2",
      traceId: "t-1",
      spanId: `s-${seq}`,
      seq,
      occurredAt: "2026-08-29T20:00:00.000Z",
      recordedAt: "2026-08-29T20:00:00.001Z",
      principal,
      tenantId: "t",
      ownerId: "o",
      confidentiality: "internal",
      retentionClass: "standard",
      trainability: "prohibited",
      redactionStatus: "none",
      payload,
    });

    const events: EventEnvelope[] = [
      makeEnv("018f-u1", "1", "user", { kind: "GoalDeclared", goal: "Compute sqrt(1333)" }),
      makeEnv("018f-a1", "2", "agent", {
        kind: "ProposalProduced",
        action: "finish",
        note: "The square root of 1333 is approximately 36.510.",
        proposalDescriptor: "sha256:abc",
      }),
      makeEnv("018f-c1", "3", "runtime", { kind: "RunCompleted", verdict: "completed" }),
    ];

    const turns = toConversationTurns(events);
    assert.equal(turns.length, 2);
    assert.equal(turns[0]?.speaker, "user");
    assert.equal(turns[0]?.text, "Compute sqrt(1333)");
    assert.equal(turns[1]?.speaker, "agent");
    assert.equal(turns[1]?.text, "The square root of 1333 is approximately 36.510.");
    assert.equal(turns[1]?.verdict, "completed");
  });

  it("folds EpisodeCompleted instrument_error detail and RunFailed error into visible failure notes", () => {
    const makeEnv = (id: string, seq: string, payload: any): EventEnvelope => ({
      schemaVersion: "vg.4",
      eventId: id,
      scope: "episode",
      runId: "run-p-3",
      traceId: "t-1",
      spanId: `s-${seq}`,
      seq,
      occurredAt: "2026-08-29T20:00:00.000Z",
      recordedAt: "2026-08-29T20:00:00.001Z",
      principal: "runtime",
      tenantId: "t",
      ownerId: "o",
      confidentiality: "internal",
      retentionClass: "standard",
      trainability: "prohibited",
      redactionStatus: "none",
      payload,
    });

    const events: EventEnvelope[] = [
      makeEnv("018f-u2", "1", { kind: "GoalDeclared", goal: "Fail gracefully" }),
      makeEnv("018f-e1", "2", {
        kind: "EpisodeCompleted",
        outcome: "instrument_error",
        detail: "OpenRouter rate limit reached",
      }),
      makeEnv("018f-f1", "3", {
        kind: "RunFailed",
        error: "Process terminated with non-zero exit code",
      }),
    ];

    const turns = toConversationTurns(events);
    assert.equal(turns.length, 2);
    assert.equal(turns[1]?.speaker, "agent");
    assert.match(turns[1]?.text ?? "", /OpenRouter rate limit reached/);
    assert.match(turns[1]?.text ?? "", /Process terminated with non-zero exit code/);
    assert.equal(turns[1]?.verdict, "failed");
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
