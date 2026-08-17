// FE-B7 — Unit tests: reducers, parse, signer (pyramid level 1)
// Run: node --test dist/test/unit.test.js

import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { parseEventEnvelope, parseJsonlLine, isUuid, isDigest, fail, afterCursor } from "../src/contract/parse";
import { emptyRunView, reduceRunView } from "../src/application/run-view";
import { OperatorSigner } from "../src/adapters/signer";
import type { EventEnvelope, ApprovalChallenge } from "../src/contract/types";

const VALID_ENVELOPE: EventEnvelope = {
  schemaVersion: "vg.4",
  eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8c",
  scope: "episode",
  runId: "run-1",
  episodeId: "ep-1",
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

describe("parse — parseEventEnvelope", () => {
  it("accepts a valid vg.4 episode envelope", () => {
    const res = parseEventEnvelope(VALID_ENVELOPE);
    assert.ok(res.ok);
    assert.equal(res.value.schemaVersion, "vg.4");
  });

  it("rejects non-object", () => {
    const res = parseEventEnvelope("string");
    assert.ok(!res.ok);
    assert.equal(res.error.code, "invalid_request");
  });

  it("rejects wrong schemaVersion", () => {
    const res = parseEventEnvelope({ ...VALID_ENVELOPE, schemaVersion: "vg.3" });
    assert.ok(!res.ok);
    assert.equal(res.error.code, "incompatible_version");
  });

  it("rejects invalid eventId UUID", () => {
    const res = parseEventEnvelope({ ...VALID_ENVELOPE, eventId: "not-a-uuid" });
    assert.ok(!res.ok);
  });

  it("rejects invalid seq (non-integer string)", () => {
    const res = parseEventEnvelope({ ...VALID_ENVELOPE, seq: "-1" });
    assert.ok(!res.ok);
  });

  it("rejects governance scope with runId", () => {
    const res = parseEventEnvelope({ ...VALID_ENVELOPE, scope: "governance", runId: "run-1", episodeId: undefined });
    assert.ok(!res.ok);
  });

  it("rejects episode without episodeId", () => {
    const res = parseEventEnvelope({ ...VALID_ENVELOPE, episodeId: undefined });
    assert.ok(!res.ok);
  });

  it("rejects missing payload.kind", () => {
    const res = parseEventEnvelope({ ...VALID_ENVELOPE, payload: {} });
    assert.ok(!res.ok);
  });
});

describe("parse — helpers", () => {
  it("isUuid returns true for valid UUID", () => {
    assert.ok(isUuid("018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8c"));
  });
  it("isUuid returns false for non-UUID", () => {
    assert.ok(!isUuid("notauuid"));
  });
  it("isDigest accepts sha256 prefix", () => {
    assert.ok(isDigest("sha256:" + "a".repeat(64)));
  });
  it("fail constructs error result", () => {
    const r = fail("not_found", "missing", false);
    assert.ok(!r.ok);
    assert.equal(r.error.code, "not_found");
  });
  it("afterCursor: no afterSeq is always true", () => {
    assert.ok(afterCursor("5", undefined));
  });
  it("afterCursor: seq > afterSeq returns true", () => {
    assert.ok(afterCursor("5", "3"));
  });
  it("afterCursor: seq <= afterSeq returns false", () => {
    assert.ok(!afterCursor("3", "5"));
  });
});

describe("parse — parseJsonlLine", () => {
  it("parses a raw envelope JSONL line", () => {
    const line = JSON.stringify(VALID_ENVELOPE);
    const res = parseJsonlLine(line);
    assert.ok(res.ok);
  });

  it("parses a StreamItem-wrapped JSONL line", () => {
    const wrapped = JSON.stringify({ contractVersion: "0.1", source: "replay", envelope: VALID_ENVELOPE });
    const res = parseJsonlLine(wrapped);
    assert.ok(res.ok);
  });

  it("rejects empty line", () => {
    const res = parseJsonlLine("  ");
    assert.ok(!res.ok);
    assert.equal(res.error.code, "invalid_request");
  });

  it("rejects non-JSON", () => {
    const res = parseJsonlLine("not json");
    assert.ok(!res.ok);
  });
});

describe("run-view — reducer", () => {
  it("emptyRunView returns zero state", () => {
    const vm = emptyRunView();
    assert.equal(vm.thoughts.length, 0);
    assert.equal(vm.tools.length, 0);
    assert.equal(vm.tokens, 0);
  });

  it("tracks lastKind", () => {
    const vm = reduceRunView(emptyRunView(), VALID_ENVELOPE);
    assert.equal(vm.lastKind, "EpisodeStarted");
  });

  it("ObservationProduced appends thought", () => {
    const env: EventEnvelope = { ...VALID_ENVELOPE, payload: { kind: "ObservationProduced", text: "thinking…" } };
    const vm = reduceRunView(emptyRunView(), env);
    assert.equal(vm.thoughts.length, 1);
    assert.equal(vm.thoughts[0], "thinking…");
  });

  it("OperatorInvoked appends tool", () => {
    const env: EventEnvelope = { ...VALID_ENVELOPE, payload: { kind: "OperatorInvoked", tool: "bash", status: "invoked" } };
    const vm = reduceRunView(emptyRunView(), env);
    assert.equal(vm.tools.length, 1);
    assert.equal(vm.tools[0]!.name, "bash");
  });

  it("BudgetCommitted sets tokens", () => {
    const env: EventEnvelope = { ...VALID_ENVELOPE, payload: { kind: "BudgetCommitted", tokens: 42, costMicros: "100" } };
    const vm = reduceRunView(emptyRunView(), env);
    assert.equal(vm.tokens, 42);
    assert.equal(vm.costMicros, "100");
  });

  it("ApprovalRequested sets pendingApproval", () => {
    const env: EventEnvelope = { ...VALID_ENVELOPE, payload: { kind: "ApprovalRequested", approvalId: "appr-1", unifiedDiff: "+line", proposedPatchDigest: "sha256:" + "a".repeat(64) } };
    const vm = reduceRunView(emptyRunView(), env);
    assert.ok(vm.pendingApproval);
    assert.equal(vm.pendingApproval.approvalId, "appr-1");
  });

  it("ApprovalResolved clears pendingApproval", () => {
    const envReq: EventEnvelope = { ...VALID_ENVELOPE, payload: { kind: "ApprovalRequested", approvalId: "appr-1" } };
    const envRes: EventEnvelope = { ...VALID_ENVELOPE, seq: "2", payload: { kind: "ApprovalResolved", approvalId: "appr-1" } };
    const intermediate = reduceRunView(emptyRunView(), envReq);
    const final = reduceRunView(intermediate, envRes);
    assert.ok(!final.pendingApproval);
  });

  it("unknown kind is kept in lastKind without crashing (CT-44)", () => {
    const env: EventEnvelope = { ...VALID_ENVELOPE, payload: { kind: "UnknownKindFromFuture" } };
    const vm = reduceRunView(emptyRunView(), env);
    assert.equal(vm.lastKind, "UnknownKindFromFuture");
  });
});

describe("signer — OperatorSigner", () => {
  it("generates a key pair by default", () => {
    const signer = new OperatorSigner();
    assert.ok(signer.keyId);
  });

  it("signChallenge returns ApprovalDecision with same approvalId", () => {
    const signer = new OperatorSigner();
    const challenge: ApprovalChallenge = {
      approvalId: "appr-123",
      processId: "proc-1",
      action: "write",
      normalizedDiff: "+line",
      argsDigest: "sha256:" + "b".repeat(64),
      descriptorDigest: "sha256:" + "c".repeat(64),
      principal: "agent-1",
      expiresAt: "2026-08-15T01:00:00.000Z",
    };
    const decision = signer.signChallenge(challenge, "approved", "operator");
    assert.equal(decision.approvalId, "appr-123");
    assert.equal(decision.resolution, "approved");
    assert.equal(decision.reviewer, "operator");
    assert.ok(typeof decision.signature === "string" && decision.signature.length > 0);
  });

  it("reject produces rejected resolution", () => {
    const signer = new OperatorSigner();
    const challenge: ApprovalChallenge = {
      approvalId: "appr-456",
      processId: "proc-2",
      action: "delete",
      normalizedDiff: "-line",
      argsDigest: "sha256:" + "d".repeat(64),
      descriptorDigest: "sha256:" + "e".repeat(64),
      principal: "agent-1",
      expiresAt: "2026-08-15T01:00:00.000Z",
    };
    const decision = signer.signChallenge(challenge, "rejected");
    assert.equal(decision.resolution, "rejected");
  });
});
