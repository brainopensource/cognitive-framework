import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import {
  ReplayRuntimeClient,
  SocketRuntimeClient,
  OperatorSigner,
  WebCryptoSigner,
  createRuntimeClient,
} from "../src/index.js";
import type { EventEnvelope, ApprovalChallenge } from "@aether/contracts";

const SAMPLE_EVENTS: EventEnvelope[] = [
  {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000001",
    scope: "episode",
    runId: "run-test-1",
    episodeId: "ep-test-1",
    traceId: "t-1",
    spanId: "s-1",
    seq: "1",
    occurredAt: "2026-08-29T20:00:00.000Z",
    recordedAt: "2026-08-29T20:00:00.001Z",
    principal: "agent",
    tenantId: "t",
    ownerId: "o",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload: { kind: "GoalDeclared", goal: "Test goal" },
  },
  {
    schemaVersion: "vg.4",
    eventId: "018f3a2b-7c4d-7e1f-9a2b-000000000002",
    scope: "episode",
    runId: "run-test-1",
    episodeId: "ep-test-1",
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
    payload: { kind: "ObservationProduced", text: "Processing complete" },
  },
];

describe("@aether/client — ReplayRuntimeClient", () => {
  it("streams events and honors afterSeq filter", async () => {
    const client = ReplayRuntimeClient.fromEnvelopes(SAMPLE_EVENTS);
    const allItems = [];
    for await (const item of client.streamEvents({ runId: "run-test-1" })) {
      if (item.ok) allItems.push(item.value);
    }
    assert.equal(allItems.length, 2);
    assert.equal(allItems[0]?.envelope.seq, "1");
    assert.equal(allItems[1]?.envelope.seq, "2");

    const resumedClient = ReplayRuntimeClient.fromEnvelopes(SAMPLE_EVENTS);
    const resumedItems = [];
    for await (const item of resumedClient.streamEvents({ runId: "run-test-1", afterSeq: "1" })) {
      if (item.ok) resumedItems.push(item.value);
    }
    assert.equal(resumedItems.length, 1);
    assert.equal(resumedItems[0]?.envelope.seq, "2");
  });

  it("handles lifecycle commands cleanly", async () => {
    const client = ReplayRuntimeClient.fromEnvelopes(SAMPLE_EVENTS);
    const startRes = await client.startRun({ repo: "." });
    assert.ok(startRes.ok);

    const getRes = await client.getRun("run-test-1");
    assert.ok(getRes.ok);
    if (getRes.ok) {
      assert.equal(getRes.value.status, "running");
    }

    const cancelRes = await client.requestCancel("run-test-1");
    assert.ok(cancelRes.ok);
  });
});

describe("@aether/client — SocketRuntimeClient fail-closed behavior", () => {
  it("fails closed with not_available when socket is missing", async () => {
    const client = new SocketRuntimeClient({
      socketPath: "/tmp/nonexistent-aether-test-socket.sock",
      connectTimeoutMs: 100,
      commandTimeoutMs: 100,
    });

    const status = await client.getDaemonStatus();
    assert.ok(!status.ok);
    if (!status.ok) {
      assert.equal(status.error.code, "not_available");
      assert.equal(status.error.retryable, true);
    }

    const run = await client.startRun({ repo: "." });
    assert.ok(!run.ok);
    if (!run.ok) {
      assert.equal(run.error.code, "not_available");
    }
  });
});

describe("@aether/client — Signers", () => {
  const challenge: ApprovalChallenge = {
    approvalId: "app-test-1",
    processId: "proc-1",
    action: "fs.write",
    normalizedDiff: "--- a/file\n+++ b/file",
    argsDigest: "sha256:" + "a".repeat(64),
    descriptorDigest: "sha256:" + "b".repeat(64),
    principal: "operator",
    expiresAt: "2026-08-30T00:00:00.000Z",
  };

  it("OperatorSigner generates valid 128-char hex Ed25519 signature", () => {
    const signer = new OperatorSigner();
    const decision = signer.signChallenge(challenge, "approved");
    assert.equal(decision.approvalId, challenge.approvalId);
    assert.equal(decision.resolution, "approved");
    assert.match(decision.signature, /^[0-9a-fA-F]{128}$/);
  });

  it("OperatorSigner refuses challenges with missing digests", () => {
    const signer = new OperatorSigner();
    assert.throws(() => {
      signer.signChallenge({ ...challenge, argsDigest: "" });
    });
  });

  it("WebCryptoSigner generates valid 128-char hex Ed25519 signature", async () => {
    const signer = new WebCryptoSigner();
    const decision = await signer.signChallenge(challenge, "approved");
    assert.equal(decision.approvalId, challenge.approvalId);
    assert.equal(decision.resolution, "approved");
    assert.match(decision.signature, /^[0-9a-fA-F]{128}$/);
  });
});
