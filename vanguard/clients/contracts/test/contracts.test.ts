import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import {
  isUuid,
  isDigest,
  parseEventEnvelope,
  parseRuntimeServiceFrame,
  parseDaemonLine,
  parseJsonlLine,
  jcsCanonicalize,
  fail,
  toClientFailureCode,
  isOk,
  isFail,
  type EventEnvelope,
} from "../src/index.js";

const VALID_EVENT: EventEnvelope = {
  schemaVersion: "vg.4",
  eventId: "018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8c",
  scope: "episode",
  runId: "run-contract-1",
  episodeId: "ep-contract-1",
  traceId: "trace-contract-1",
  spanId: "span-contract-1",
  seq: "1",
  occurredAt: "2026-08-29T20:00:00.000Z",
  recordedAt: "2026-08-29T20:00:00.001Z",
  principal: "agent-aether",
  tenantId: "tenant-default",
  ownerId: "owner-platform",
  confidentiality: "internal",
  retentionClass: "standard",
  trainability: "prohibited",
  redactionStatus: "none",
  payload: { kind: "EpisodeStarted", repo: "." },
};

describe("@aether/contracts — parsing and validation", () => {
  it("parses valid vg.4 event envelope", () => {
    const res = parseEventEnvelope(VALID_EVENT);
    assert.ok(isOk(res));
    if (res.ok) {
      assert.equal(res.value.schemaVersion, "vg.4");
      assert.equal(res.value.eventId, VALID_EVENT.eventId);
      assert.equal(res.value.payload.kind, "EpisodeStarted");
    }
  });

  it("rejects invalid UUID and missing fields", () => {
    const badId = parseEventEnvelope({ ...VALID_EVENT, eventId: "not-a-uuid" });
    assert.ok(isFail(badId));
    if (!badId.ok) {
      assert.equal(badId.error.code, "invalid_request");
    }

    const badVersion = parseEventEnvelope({ ...VALID_EVENT, schemaVersion: "vg.3" });
    assert.ok(isFail(badVersion));
    if (!badVersion.ok) {
      assert.equal(badVersion.error.code, "incompatible_version");
    }

    const badScope = parseEventEnvelope({ ...VALID_EVENT, scope: "unauthorized" });
    assert.ok(isFail(badScope));
  });

  it("parses CommandFrame, ReceiptFrame, EventFrame, and ErrorFrame", () => {
    const cmdRes = parseRuntimeServiceFrame({
      version: "vg.4",
      frameType: "command",
      frameId: "f-1",
      command: {
        name: "StartRun",
        commandId: "cmd-1",
        idempotencyKey: "idem-1",
        runId: "run-1",
      },
    });
    assert.ok(isOk(cmdRes));
    if (cmdRes.ok && cmdRes.value.frameType === "command") {
      assert.equal(cmdRes.value.command.name, "StartRun");
    }

    const receiptRes = parseRuntimeServiceFrame({
      version: "vg.4",
      frameType: "receipt",
      frameId: "f-2",
      inReplyTo: "f-1",
      receipt: {
        commandId: "cmd-1",
        status: "completed",
        runId: "run-1",
      },
    });
    assert.ok(isOk(receiptRes));
    if (receiptRes.ok && receiptRes.value.frameType === "receipt") {
      assert.equal(receiptRes.value.receipt.status, "completed");
    }

    const errRes = parseRuntimeServiceFrame({
      version: "vg.4",
      frameType: "error",
      frameId: "f-3",
      error: {
        code: "permission_denied",
        message: "Key verification failed",
        retryable: false,
      },
    });
    assert.ok(isOk(errRes));
    if (errRes.ok && errRes.value.frameType === "error") {
      assert.equal(errRes.value.error.code, "permission_denied");
      assert.equal(errRes.value.error.retryable, false);
    }
  });

  it("handles line parsing for NDJSON feeds", () => {
    const line = JSON.stringify(VALID_EVENT);
    const parsed = parseJsonlLine(line);
    assert.ok(isOk(parsed));
    if (parsed.ok) {
      assert.equal(parsed.value.eventId, VALID_EVENT.eventId);
    }

    const frameLine = JSON.stringify({
      version: "vg.4",
      frameType: "receipt",
      frameId: "f-line",
      receipt: { commandId: "c-1", status: "completed" },
    });
    const frameParsed = parseDaemonLine(frameLine);
    assert.ok(isOk(frameParsed));
  });
});

describe("@aether/contracts — JCS canonicalization", () => {
  it("canonicalizes JSON keys in lexicographical order", () => {
    const unordered = { z: 1, a: "test", m: [3, 2, 1], k: { b: 2, a: 1 } };
    const canonical = jcsCanonicalize(unordered);
    assert.equal(canonical, '{"a":"test","k":{"a":1,"b":2},"m":[3,2,1],"z":1}');
  });

  it("omits undefined properties", () => {
    const withUndefined = { a: 1, b: undefined, c: "ok" };
    assert.equal(jcsCanonicalize(withUndefined), '{"a":1,"c":"ok"}');
  });
});

describe("@aether/contracts — error mapping", () => {
  it("maps canonical error codes faithfully", () => {
    assert.equal(toClientFailureCode("invalid_request"), "invalid_request");
    assert.equal(toClientFailureCode("conflict"), "conflict");
    assert.equal(toClientFailureCode("rate_limited"), "rate_limited");
    assert.equal(toClientFailureCode("unknown_custom_code"), "internal");
  });

  it("constructs fail results with appropriate retryable defaults", () => {
    const failConflict = fail("conflict", "CAS version mismatch");
    assert.ok(!failConflict.ok);
    if (!failConflict.ok) {
      assert.equal(failConflict.error.code, "conflict");
      assert.equal(failConflict.error.retryable, true);
    }

    const failInvalid = fail("invalid_request", "Malformed JSON");
    assert.ok(!failInvalid.ok);
    if (!failInvalid.ok) {
      assert.equal(failInvalid.error.code, "invalid_request");
      assert.equal(failInvalid.error.retryable, false);
    }
  });

  it("validates UUIDs and SHA-256 digests", () => {
    assert.ok(isUuid("018f3a2b-7c4d-7e1f-9a2b-3c4d5e6f7a8c"));
    assert.ok(!isUuid("not-uuid"));
    assert.ok(isDigest("sha256:" + "0123456789abcdef".repeat(4)));
    assert.ok(!isDigest("md5:12345"));
  });
});
