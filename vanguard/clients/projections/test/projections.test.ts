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

describe("@aether/projections — ConversationTurns (full ledger vocabulary)", () => {
  const ev = (seq: number, payload: any): EventEnvelope => ({
    schemaVersion: "vg.4",
    eventId: `018f-v${seq}`,
    scope: "episode",
    runId: "run-v-1",
    traceId: "t-1",
    spanId: `s-${seq}`,
    seq: String(seq),
    occurredAt: "2026-09-03T10:00:00.000Z",
    recordedAt: "2026-09-03T10:00:00.001Z",
    principal: "runtime",
    tenantId: "t",
    ownerId: "o",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload,
  });

  const foldOne = (payload: any) => {
    const turns = toConversationTurns([
      ev(1, { kind: "GoalDeclared", goal: "do the thing" }),
      ev(2, payload),
    ]);
    return turns[1]!;
  };

  it("renders a revised plan with its ordered steps", () => {
    const turn = foldOne({ kind: "PlanRevised", plan: "split the refactor", steps: ["read", "edit"] });
    const card = turn.activityCards.find((c) => c.kind === "plan");
    assert.ok(card, "expected a plan card");
    assert.match(card!.title, /split the refactor/);
    assert.equal(card!.details, "1. read\n2. edit");
  });

  it("surfaces reflection as its own card rather than inline prose", () => {
    const turn = foldOne({ kind: "ReflectionProduced", reflection: "the lease is never released" });
    assert.equal(turn.activityCards[0]?.kind, "reflection");
    assert.equal(turn.text, "", "reflection must not be folded into model prose");
  });

  it("closes an open tool card as failed on EffectFailed", () => {
    const turns = toConversationTurns([
      ev(1, { kind: "GoalDeclared", goal: "g" }),
      ev(2, { kind: "EffectStarted", tool: "write_file" }),
      ev(3, { kind: "EffectFailed", error: "permission denied" }),
    ]);
    const card = turns[1]!.activityCards[0]!;
    assert.equal(card.status, "failed");
    assert.equal(card.details, "permission denied");
  });

  it("marks a policy-rejected effect rejected, not failed", () => {
    const turns = toConversationTurns([
      ev(1, { kind: "GoalDeclared", goal: "g" }),
      ev(2, { kind: "EffectStarted", tool: "rm" }),
      ev(3, { kind: "EffectRejected", reason: "outside workspace" }),
    ]);
    assert.equal(turns[1]!.activityCards[0]?.status, "rejected");
  });

  it("records a rejected approval as rejected rather than completed", () => {
    const turns = toConversationTurns([
      ev(1, { kind: "GoalDeclared", goal: "g" }),
      ev(2, { kind: "ApprovalRequested", action: "apply patch" }),
      ev(3, { kind: "ApprovalResolved", decision: "reject" }),
    ]);
    assert.equal(turns[1]!.activityCards[0]?.status, "rejected");
  });

  it("pairs a returning sub-agent with the card its spawn opened", () => {
    const turns = toConversationTurns([
      ev(1, { kind: "GoalDeclared", goal: "g" }),
      ev(2, { kind: "ChildSpawned", childRunId: "c-9", role: "reviewer" }),
      ev(3, { kind: "ChildReturned", childRunId: "c-9", outcome: "satisfied" }),
    ]);
    const cards = turns[1]!.activityCards.filter((c) => c.kind === "child");
    assert.equal(cards.length, 1, "spawn and return must fold onto one card");
    assert.equal(cards[0]?.status, "completed");
  });

  it("accumulates committed budget onto a single cost card", () => {
    const turns = toConversationTurns([
      ev(1, { kind: "GoalDeclared", goal: "g" }),
      ev(2, { kind: "BudgetCommitted", usdMicros: 1_500_000 }),
      ev(3, { kind: "BudgetCommitted", usdMicros: 500_000 }),
    ]);
    const cards = turns[1]!.activityCards.filter((c) => c.kind === "budget");
    assert.equal(cards.length, 1);
    assert.match(cards[0]!.title, /\$2\.0000/);
  });

  it("exposes a checkpoint as a branch point", () => {
    const turn = foldOne({ kind: "CheckpointCreated", checkpointId: "ck-3", branchId: "alt" });
    const card = turn.activityCards.find((c) => c.kind === "checkpoint");
    assert.ok(card);
    assert.match(card!.title, /ck-3/);
    assert.match(card!.title, /alt/);
  });

  it("reports context compaction with its token delta", () => {
    const turn = foldOne({ kind: "ContextCompacted", beforeTokens: 90000, afterTokens: 12000 });
    assert.match(turn.activityCards[0]!.title, /90000 → 12000/);
  });

  it("clears a terminal verdict when the run recovers", () => {
    const turns = toConversationTurns([
      ev(1, { kind: "GoalDeclared", goal: "g" }),
      ev(2, { kind: "RunAborted", reason: "sigkill" }),
      ev(3, { kind: "RunRecovered", from: "ck-2" }),
    ]);
    assert.equal(turns[1]!.verdict, undefined, "a recovered run is not still aborted");
    assert.match(turns[1]!.text, /Recovered from ck-2/);
  });

  it("folds VerdictRecorded, the kind the backend actually writes", () => {
    const turn = foldOne({ kind: "VerdictRecorded", verdict: "satisfied" });
    assert.equal(turn.verdict, "satisfied");
    assert.equal(turn.activityCards[0]?.kind, "verification");
  });

  it("reports a faulted plugin but stays quiet on healthy lifecycle chatter", () => {
    // A healthy activation contributes nothing, so the agent turn stays empty
    // and is filtered out of the transcript entirely.
    const noisy = toConversationTurns([
      ev(1, { kind: "GoalDeclared", goal: "do the thing" }),
      ev(2, { kind: "PluginActivated", plugin: "ruff" }),
    ]);
    assert.equal(noisy.length, 1);
    assert.equal(noisy[0]?.speaker, "user");
    const faulted = foldOne({ kind: "PluginFaulted", plugin: "ruff", reason: "segfault" });
    assert.equal(faulted.activityCards[0]?.kind, "plugin");
    assert.equal(faulted.activityCards[0]?.status, "failed");
  });

  it("does not open an empty leading turn for run lifecycle events", () => {
    const turns = toConversationTurns([
      ev(1, { kind: "RunStarted" }),
      ev(2, { kind: "GoalDeclared", goal: "g" }),
      ev(3, { kind: "ProposalProduced", action: "finish", note: "done" }),
    ]);
    assert.equal(turns.length, 2);
    assert.equal(turns[0]?.speaker, "user");
  });

  it("preserves an unrecognised future kind without throwing (CT-44)", () => {
    const turns = toConversationTurns([
      ev(1, { kind: "GoalDeclared", goal: "g" }),
      ev(2, { kind: "SomeKindFromTheFuture", detail: "x" }),
      ev(3, { kind: "ProposalProduced", action: "finish", note: "still here" }),
    ]);
    assert.match(turns[1]!.text, /still here/);
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
