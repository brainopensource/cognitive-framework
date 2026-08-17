// FE-B7 — VG-04 golden vector tests (pyramid level 2).
// Client parse must agree with the schema vectors.
// Vectors derived from VG-04 §12.2; do NOT edit vectors to pass the tests.

import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { parseEventEnvelope } from "../src/contract/parse";

// ── VG-04 §12.2 canonical vectors ────────────────────────────────────────────
// These are minimal but structurally correct envelopes for each scope.

const VECTORS = {
  episode_started: {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8c",
    scope: "episode",
    runId: "run-v1",
    episodeId: "ep-v1",
    traceId: "trace-v1",
    spanId: "span-v1",
    seq: "1",
    occurredAt: "2026-01-01T00:00:00.000Z",
    recordedAt: "2026-01-01T00:00:00.001Z",
    principal: "agent",
    tenantId: "t1",
    ownerId: "o1",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: { kind: "EpisodeStarted" },
  },
  episode_completed: {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8d",
    scope: "episode",
    runId: "run-v1",
    episodeId: "ep-v1",
    traceId: "trace-v1",
    spanId: "span-v2",
    seq: "2",
    occurredAt: "2026-01-01T00:00:01.000Z",
    recordedAt: "2026-01-01T00:00:01.001Z",
    principal: "agent",
    tenantId: "t1",
    ownerId: "o1",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: { kind: "EpisodeCompleted", outcome: "satisfied" },
  },
  governance_activation: {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7b01",
    scope: "governance",
    traceId: "trace-gov",
    spanId: "span-gov-1",
    seq: "1",
    occurredAt: "2026-01-01T00:00:01.000Z",
    recordedAt: "2026-01-01T00:00:01.001Z",
    principal: "operator",
    tenantId: "t1",
    ownerId: "o1",
    confidentiality: "internal",
    retentionClass: "extended",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: { kind: "ActivationChanged", artifactId: "art-1", status: "active" },
  },
  approval_requested: {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7b02",
    scope: "episode",
    runId: "run-v2",
    episodeId: "ep-v2",
    traceId: "trace-v2",
    spanId: "span-v2-1",
    seq: "3",
    occurredAt: "2026-01-01T00:01:00.000Z",
    recordedAt: "2026-01-01T00:01:00.001Z",
    principal: "agent",
    tenantId: "t1",
    ownerId: "o1",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: { kind: "ApprovalRequested", approvalId: "appr-v1", unifiedDiff: "+line" },
  },
  budget_committed: {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7b03",
    scope: "episode",
    runId: "run-v3",
    episodeId: "ep-v3",
    traceId: "trace-v3",
    spanId: "span-v3-1",
    seq: "4",
    occurredAt: "2026-01-01T00:02:00.000Z",
    recordedAt: "2026-01-01T00:02:00.001Z",
    principal: "agent",
    tenantId: "t1",
    ownerId: "o1",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: { kind: "BudgetCommitted", tokens: 100, costMicros: "500" },
  },
  recovery_scope: {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7b04",
    scope: "recovery",
    runId: "run-v4",
    traceId: "trace-v4",
    spanId: "span-v4-1",
    seq: "1",
    occurredAt: "2026-01-01T00:03:00.000Z",
    recordedAt: "2026-01-01T00:03:00.001Z",
    principal: "agent",
    tenantId: "t1",
    ownerId: "o1",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: { kind: "RunRecovered" },
  },
} as const;

// ── Rejection vectors (must NOT parse) ──────────────────────────────────────
const REJECTION_VECTORS = {
  wrong_schema_version: { ...VECTORS.episode_started, schemaVersion: "vg.3" },
  governance_with_runId: { ...VECTORS.governance_activation, runId: "run-should-fail" },
  episode_without_episodeId: { ...VECTORS.episode_started, episodeId: undefined },
  invalid_seq_negative: { ...VECTORS.episode_started, seq: "-1" },
  invalid_seq_float: { ...VECTORS.episode_started, seq: "1.5" },
  invalid_uuid_eventId: { ...VECTORS.episode_started, eventId: "not-a-uuid" },
  missing_payload_kind: { ...VECTORS.episode_started, payload: { noKind: true } },
  invalid_occurredAt: { ...VECTORS.episode_started, occurredAt: "2026-01-01" },
} as const;

describe("VG-04 golden vectors — MUST parse", () => {
  for (const [name, vector] of Object.entries(VECTORS)) {
    it(`parses ${name}`, () => {
      const result = parseEventEnvelope(vector);
      assert.ok(result.ok, `expected ok but got error: ${!result.ok ? result.error.message : ""}`);
    });
  }
});

describe("VG-04 rejection vectors — MUST NOT parse", () => {
  for (const [name, vector] of Object.entries(REJECTION_VECTORS)) {
    it(`rejects ${name}`, () => {
      const result = parseEventEnvelope(vector);
      assert.ok(!result.ok, `expected failure for ${name} but got ok`);
    });
  }
});
