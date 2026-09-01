import test from "node:test";
import assert from "node:assert/strict";
import {
  DEFAULT_DISCOVERED_CAPABILITIES,
  isFeaturePermitted,
  ColumnarEventStore,
  initialStudioFold,
  reduceStudioFold,
  StudioFoldEngine,
  runAllAnomalyDetectors,
  computeWaterfallLayout,
  type EventEnvelope,
  compileManifest,
  compositionDigest,
  generateAaaCSource,
  validateAgentDefinition,
  applyCompositionDelta,
  type AgentDefinition,
} from "../src/index.js";

const canonicalAgent: AgentDefinition = {
  schemaVersion: "aether.agent-definition/1", name: "coding-agent", description: "test",
  model: { router: "configured", temperature: 0.2, maxTokens: 32000, reasoningEffort: "high" },
  systemPrompt: "Work through RuntimeService.", skills: ["patch", "read"],
  context: { strategy: "l1-l5", retrieval: ["ledger"] }, memory: { policy: "event-sourced", scopes: ["run"] },
  tools: ["fs.read", "fs.patch"], plugins: [],
  budget: { usdMicros: 1000000, tokens: 50000, timeoutMs: 120000, maxDepth: 2, maxTurns: 15 },
  approvalPolicy: { mode: "governed-effects", editable: true }, planner: { policy: "evidence-first" },
  recoveryPolicy: { policy: "checkpoint-resume", maxRetries: 2 }, verifier: { policy: "exterior", exteriorRequired: true },
  completionGate: { policy: "verified", requireVerification: true }, subagents: [], topology: { kind: "single_agent", channels: [] },
};

test("Agent Studio compiles deterministic immutable manifests and safe AaaC source", async () => {
  assert.deepEqual(validateAgentDefinition(canonicalAgent), []);
  const first = compileManifest(canonicalAgent);
  const second = compileManifest({ ...canonicalAgent, skills: ["read", "patch"] });
  assert.equal(await compositionDigest(first), await compositionDigest(second));
  assert.equal(Object.isFrozen(first), true);
  assert.equal(Object.isFrozen(first.model), true);
  const source = generateAaaCSource(canonicalAgent);
  assert.match(source, /build_composition_request/);
  assert.doesNotMatch(source, /subprocess|requests\.|urllib|os\.system/);
});

test("Agent Studio rejects unsafe policy and binds child deltas to an exact base digest", () => {
  assert.equal(validateAgentDefinition({ ...canonicalAgent, approvalPolicy: { mode: "never", editable: false } }).some((issue) => issue.code === "unsafe_policy"), true);
  assert.throws(() => applyCompositionDelta(canonicalAgent, { baseDigest: "latest", childRole: "reviewer", changes: {}, disposition: "discard" }), /exact composition/);
  const child = applyCompositionDelta(canonicalAgent, { baseDigest: `sha256:${"a".repeat(64)}`, childRole: "reviewer", changes: { tools: ["fs.read"] }, disposition: "discard" });
  assert.equal(child.name, "coding-agent.reviewer");
  assert.deepEqual(child.tools, ["fs.read"]);
});

test("DEFAULT_DISCOVERED_CAPABILITIES enforces feature gates and disables speculative features", () => {
  assert.equal(isFeaturePermitted(DEFAULT_DISCOVERED_CAPABILITIES, "liveSingleRun", "command"), true);
  assert.equal(isFeaturePermitted(DEFAULT_DISCOVERED_CAPABILITIES, "fixtureReplay", "command"), true);
  assert.equal(isFeaturePermitted(DEFAULT_DISCOVERED_CAPABILITIES, "draftComposition", "read"), true);
  assert.equal(isFeaturePermitted(DEFAULT_DISCOVERED_CAPABILITIES, "draftComposition", "command"), false);
  assert.equal(isFeaturePermitted(DEFAULT_DISCOVERED_CAPABILITIES, "m7Scheduler", "read"), false);
  assert.equal(isFeaturePermitted(DEFAULT_DISCOVERED_CAPABILITIES, "m8SwarmTopology", "read"), false);
  assert.equal(isFeaturePermitted(DEFAULT_DISCOVERED_CAPABILITIES, "m9SecondBrain", "read"), false);
});

test("ColumnarEventStore appends events, interns kinds, and maintains idempotency on duplicate seq", () => {
  const store = new ColumnarEventStore(100);

  const env1: EventEnvelope = {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a01",
    scope: "episode",
    runId: "run-test-1",
    traceId: "trace-1",
    spanId: "span-1",
    seq: "1",
    occurredAt: "2026-08-15T00:00:00.000Z",
    recordedAt: "2026-08-15T00:00:00.001Z",
    principal: "agent-1",
    tenantId: "tenant-default",
    ownerId: "owner-platform",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: { kind: "EpisodeStarted", repo: "." },
  };

  const row1 = store.append(env1);
  assert.equal(row1.seq, 1n);
  assert.equal(store.size(), 1);

  // Duplicate seq test: should return same row and not increase store size
  const duplicate = store.append(env1);
  assert.equal(duplicate.index, row1.index);
  assert.equal(store.size(), 1);
});

test("ColumnarEventStore records missing cursor ranges instead of silently presenting a contiguous stream", () => {
  const store = new ColumnarEventStore(10);
  const make = (seq: string, eventId: string): EventEnvelope => ({
    schemaVersion: "vg.4", eventId, scope: "episode", runId: "run-gap", traceId: "trace-gap", spanId: `span-${seq}`,
    seq, occurredAt: "2026-08-15T00:00:00.000Z", recordedAt: "2026-08-15T00:00:00.001Z", principal: "operator",
    tenantId: "tenant", ownerId: "owner", confidentiality: "internal", retentionClass: "standard", trainability: "prohibited", redactionStatus: "none",
    payload: { kind: "Heartbeat" },
  });
  store.append(make("1", "event-1"));
  store.append(make("3", "event-3"));
  assert.deepEqual(store.getGaps(), [{ from: 2n, to: 2n }]);
});

test("initial evidence is never green without a canonical proof projection", () => {
  assert.equal(initialStudioFold().evidenceRows.every((row) => row.state === "unverifiable"), true);
});

test("StudioFoldEngine folds deterministically over canonical event stream", () => {
  const store = new ColumnarEventStore(100);
  const engine = new StudioFoldEngine();

  const envs: EventEnvelope[] = [
    {
      schemaVersion: "vg.4",
      eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a01",
      scope: "episode",
      runId: "run-test-1",
      traceId: "trace-1",
      spanId: "span-1",
      seq: "1",
      occurredAt: "2026-08-15T00:00:00.000Z",
      recordedAt: "2026-08-15T00:00:00.001Z",
      principal: "agent-1",
      tenantId: "tenant-default",
      ownerId: "owner-platform",
      confidentiality: "internal",
      retentionClass: "standard",
      trainability: "prohibited",
      redactionStatus: "none",
      payload: { kind: "EpisodeStarted", repo: "/workspace/project" },
    },
    {
      schemaVersion: "vg.4",
      eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a02",
      scope: "episode",
      runId: "run-test-1",
      traceId: "trace-1",
      spanId: "span-2",
      seq: "2",
      occurredAt: "2026-08-15T00:00:00.010Z",
      recordedAt: "2026-08-15T00:00:00.011Z",
      principal: "agent-1",
      tenantId: "tenant-default",
      ownerId: "owner-platform",
      confidentiality: "internal",
      retentionClass: "standard",
      trainability: "prohibited",
      redactionStatus: "none",
      payload: { kind: "BudgetCommitted", tokens: 150, costMicros: "1500" },
    },
    {
      schemaVersion: "vg.4",
      eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a03",
      scope: "episode",
      runId: "run-test-1",
      traceId: "trace-1",
      spanId: "span-3",
      seq: "3",
      occurredAt: "2026-08-15T00:00:00.020Z",
      recordedAt: "2026-08-15T00:00:00.021Z",
      principal: "agent-1",
      tenantId: "tenant-default",
      ownerId: "owner-platform",
      confidentiality: "internal",
      retentionClass: "standard",
      trainability: "prohibited",
      redactionStatus: "none",
      payload: { kind: "EpisodeCompleted", outcome: "satisfied" },
    },
  ];

  const rows = store.appendBatch(envs);
  const fold = engine.foldAll(rows);

  assert.equal(fold.runId, "run-test-1");
  assert.equal(fold.status, "satisfied");
  assert.equal(fold.totalTokens, 150);
  assert.equal(fold.totalCostMicros, 1500n);
  assert.equal(fold.repo, "/workspace/project");

  // Scrubbing test: fold back to seq 1
  const foldSeq1 = engine.foldToSeq(1n, rows);
  assert.equal(foldSeq1.status, "running");
  assert.equal(foldSeq1.totalTokens, 0);
  assert.equal(foldSeq1.totalCostMicros, 0n);
});

test("StudioFoldEngine preserves unknown future event kinds per CT-44", () => {
  const store = new ColumnarEventStore(100);
  const engine = new StudioFoldEngine();

  const unknownEnv: EventEnvelope = {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a99",
    scope: "evolution",
    runId: "run-test-1",
    traceId: "trace-1",
    spanId: "span-99",
    seq: "1",
    occurredAt: "2026-08-15T00:00:00.000Z",
    recordedAt: "2026-08-15T00:00:00.001Z",
    principal: "agent-1",
    tenantId: "tenant-default",
    ownerId: "owner-platform",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: { kind: "QuantumEvolutionStateChanged", quantumSpin: 0.5 },
  };

  const rows = store.appendBatch([unknownEnv]);
  const fold = engine.foldAll(rows);

  assert.equal(fold.unknownEvents.length, 1);
  assert.equal(fold.unknownEvents[0]!.kind, "QuantumEvolutionStateChanged");
});

test("9 Anomaly Detectors identify F-22 undeterminable and fail-closed refusals correctly", () => {
  const store = new ColumnarEventStore(100);
  const engine = new StudioFoldEngine();

  const envs: EventEnvelope[] = [
    {
      schemaVersion: "vg.4",
      eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f8001",
      scope: "episode",
      runId: "run-test-2",
      traceId: "trace-2",
      spanId: "span-10",
      seq: "1",
      occurredAt: "2026-08-15T00:00:00.000Z",
      recordedAt: "2026-08-15T00:00:00.001Z",
      principal: "agent-1",
      tenantId: "tenant-default",
      ownerId: "owner-platform",
      confidentiality: "internal",
      retentionClass: "standard",
      trainability: "prohibited",
      redactionStatus: "none",
      payload: { kind: "EffectStarted", descriptor: "desc-write-01", action: "fs.write" },
    },
    {
      schemaVersion: "vg.4",
      eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f8002",
      scope: "episode",
      runId: "run-test-2",
      traceId: "trace-2",
      spanId: "span-11",
      seq: "2",
      occurredAt: "2026-08-15T00:00:00.010Z",
      recordedAt: "2026-08-15T00:00:00.011Z",
      principal: "agent-1",
      tenantId: "tenant-default",
      ownerId: "owner-platform",
      confidentiality: "internal",
      retentionClass: "standard",
      trainability: "prohibited",
      redactionStatus: "none",
      payload: { kind: "EffectReconciled", descriptor: "desc-write-01", uncertainty: "undeterminable" },
    },
  ];

  const rows = store.appendBatch(envs);
  const fold = engine.foldAll(rows);

  const findings = runAllAnomalyDetectors(fold);
  const staleIntent = findings.find((f) => f.code === "stale_intent");
  assert.ok(staleIntent, "Should detect F-22 undeterminable unreconciled intent");
  assert.equal(staleIntent?.severity, "warning");
});

test("computeWaterfallLayout computes non-zero span geometries and bounds correctly", () => {
  const spans = [
    {
      spanId: "s1",
      name: "S0 ENTER",
      startMs: 1000,
      endMs: 1005,
      durationMs: 5,
      outcome: "satisfied" as const,
      depth: 0,
    },
    {
      spanId: "s2",
      name: "S8a INTENT",
      startMs: 1006,
      endMs: 1010,
      durationMs: 4,
      outcome: "satisfied" as const,
      depth: 1,
    },
  ];

  const layout = computeWaterfallLayout(spans, 800, 24);
  assert.equal(layout.nodes.length, 2);
  assert.ok(layout.nodes[0]!.width >= 4, "Width must satisfy MIN_PX rule");
  assert.equal(layout.nodes[0]!.y, 0);
  assert.equal(layout.nodes[1]!.y, 26);
});
