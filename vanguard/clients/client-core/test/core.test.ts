import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import {
  parseEventEnvelope,
  parseJsonlLine,
  isUuid,
  isDigest,
  fail,
  afterCursor,
  emptyRunView,
  reduceRunView,
  OperatorSigner,
  ReplayRuntimeClient,
} from "../src/index.js";
import type { EventEnvelope, ApprovalChallenge } from "../src/index.js";

const VALID_ENVELOPE: EventEnvelope = {
  schemaVersion: "vg.4",
  eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8c",
  scope: "episode",
  runId: "run-core-1",
  episodeId: "ep-core-1",
  traceId: "trace-core-1",
  spanId: "span-core-1",
  seq: "1",
  occurredAt: "2026-08-15T00:00:00.000Z",
  recordedAt: "2026-08-15T00:00:00.001Z",
  principal: "agent-core",
  tenantId: "tenant-default",
  ownerId: "owner-platform",
  confidentiality: "internal",
  retentionClass: "standard",
  trainability: "prohibited",
  redactionStatus: "none",
  payload: { kind: "EpisodeStarted", repo: "." },
};

describe("client-core — parseEventEnvelope", () => {
  it("parses valid vg.4 envelope", () => {
    const res = parseEventEnvelope(VALID_ENVELOPE);
    assert.ok(res.ok);
    assert.equal(res.value.schemaVersion, "vg.4");
  });

  it("rejects non-object envelope", () => {
    const res = parseEventEnvelope("invalid");
    assert.ok(!res.ok);
    assert.equal(res.error.code, "invalid_request");
  });

  it("rejects invalid UUID", () => {
    const res = parseEventEnvelope({ ...VALID_ENVELOPE, eventId: "bad-uuid" });
    assert.ok(!res.ok);
  });
});

describe("client-core — helpers", () => {
  it("isUuid returns true for UUID", () => {
    assert.ok(isUuid("018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8c"));
  });

  it("isDigest returns true for sha256 prefix", () => {
    assert.ok(isDigest("sha256:" + "a".repeat(64)));
  });

  it("fail constructs failure Result", () => {
    const res = fail("not_found", "item missing", false);
    assert.ok(!res.ok);
    assert.equal(res.error.code, "not_found");
  });
});

describe("client-core — run-view reducer", () => {
  it("emptyRunView returns initial state", () => {
    const vm = emptyRunView();
    assert.equal(vm.thoughts.length, 0);
    assert.equal(vm.tools.length, 0);
    assert.equal(vm.tokens, 0);
  });

  it("reduceRunView tracks thoughts and lastKind", () => {
    const env: EventEnvelope = {
      ...VALID_ENVELOPE,
      payload: { kind: "ObservationProduced", text: "analyzing codebase" },
    };
    const vm = reduceRunView(emptyRunView(), env);
    assert.equal(vm.lastKind, "ObservationProduced");
    assert.equal(vm.thoughts.length, 1);
    assert.equal(vm.thoughts[0], "analyzing codebase");
  });
});

describe("client-core — OperatorSigner", () => {
  it("generates keypair and signs challenge", () => {
    const signer = new OperatorSigner();
    const challenge: ApprovalChallenge = {
      approvalId: "appr-core-1",
      processId: "proc-1",
      action: "write",
      normalizedDiff: "+line",
      argsDigest: "sha256:" + "1".repeat(64),
      descriptorDigest: "sha256:" + "2".repeat(64),
      principal: "operator",
      expiresAt: "2026-08-15T01:00:00.000Z",
    };
    const decision = signer.signChallenge(challenge, "approved", "operator");
    assert.equal(decision.approvalId, "appr-core-1");
    assert.equal(decision.resolution, "approved");
    assert.ok(decision.signature.length > 0);
  });
});

describe("client-core — ReplayRuntimeClient", () => {
  it("streams events from JSONL text", async () => {
    const jsonl = JSON.stringify(VALID_ENVELOPE) + "\n";
    const client = ReplayRuntimeClient.fromJsonl(jsonl);
    const items = [];
    for await (const item of client.streamEvents({ runId: "run-core-1" })) {
      if (item.ok) items.push(item.value);
    }
    assert.equal(items.length, 1);
    assert.equal(items[0]?.envelope.runId, "run-core-1");
  });
});
