import test from "node:test";
import assert from "node:assert/strict";
import { WebCryptoSigner } from "../src/adapters/web-signer.js";
import type { ApprovalChallenge } from "../src/contract/types.js";

test("WebCryptoSigner initializes, signs approval challenge with JCS canonical payload", async () => {
  const signer = await WebCryptoSigner.create("test-web-key", "operator:web-test");
  assert.equal(signer.keyId, "test-web-key");
  assert.equal(signer.principal, "operator:web-test");

  const challenge: ApprovalChallenge = {
    approvalId: "approval-test-01",
    processId: "proc-1",
    action: "fs.patch",
    normalizedDiff: "--- a/file\n+++ b/file\n@@ -1 +1 @@\n-a\n+b",
    argsDigest: "sha256:args_123",
    descriptorDigest: "sha256:desc_456",
    principal: "operator:web-test",
    expiresAt: "2026-08-27T23:59:59.000Z",
  };

  const decision = await signer.signChallenge(challenge, "approved");
  assert.equal(decision.approvalId, "approval-test-01");
  assert.equal(decision.resolution, "approved");
  assert.equal(decision.keyId, "test-web-key");
  assert.equal(decision.reviewer, "operator:web-test");
  assert.ok(decision.signature && decision.signature.length > 0, "signature must be non-empty hex");
});

test("WebCryptoSigner refuses challenges with missing digests", async () => {
  const signer = await WebCryptoSigner.create();
  const badChallenge: ApprovalChallenge = {
    approvalId: "approval-bad",
    processId: "proc-1",
    action: "fs.patch",
    normalizedDiff: "",
    argsDigest: "",
    descriptorDigest: "sha256:desc",
    principal: "operator",
    expiresAt: "2026-08-27T23:59:59.000Z",
  };

  await assert.rejects(
    async () => {
      await signer.signChallenge(badChallenge);
    },
    /approval challenge missing argsDigest, descriptorDigest, or expiresAt/
  );
});
