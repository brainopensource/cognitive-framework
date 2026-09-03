import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { jcsCanonicalize, OperatorSigner } from "../src/adapters/signer.js";

const PYTHON_OPERATOR_SIGNER_VECTOR = {
  approvalId: "appr-1",
  argsDigest: "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  descriptorDigest: "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  expiresAt: "2026-08-16T00:00:00.000Z",
  keyId: "operator-key-default",
  resolution: "approved",
  reviewer: "operator",
} as const;

/** RFC 8785 / Python `canonicalise` of OperatorSigner.signed_payload() for the vector above. */
const PYTHON_JCS =
  '{"approvalId":"appr-1","argsDigest":"sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","descriptorDigest":"sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","expiresAt":"2026-08-16T00:00:00.000Z","keyId":"operator-key-default","resolution":"approved","reviewer":"operator"}';

test("JCS matches Python OperatorSigner signed_payload canonical bytes", () => {
  assert.equal(jcsCanonicalize(PYTHON_OPERATOR_SIGNER_VECTOR), PYTHON_JCS);
});

test("OperatorSigner persists keys at 0600", () => {
  const dir = mkdtempSync(join(tmpdir(), "vg-keys-"));
  const first = OperatorSigner.loadOrCreate(dir, "test-key");
  const again = OperatorSigner.loadOrCreate(dir, "test-key");
  assert.equal(first.keyId, "test-key");
  assert.equal(again.keyId, "test-key");
  const mode = statSync(join(dir, "test-key.pem")).mode & 0o777;
  assert.equal(mode, 0o600);
});

test("signChallenge refuses empty digests", () => {
  const signer = new OperatorSigner();
  assert.throws(() =>
    signer.signChallenge({
      approvalId: "a",
      processId: "p",
      action: "fs.patch",
      normalizedDiff: "",
      argsDigest: "",
      descriptorDigest: "",
      principal: "op",
      expiresAt: "",
    })
  );
});
