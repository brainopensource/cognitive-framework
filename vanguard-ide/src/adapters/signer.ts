// FE-B4: OperatorSigner — Ed25519, RFC 8785 JCS (same semantics as FE-A3 / CLI signer).
// Vendored from vanguard/clients/cli/src/adapters/signer.ts (FE-A owns original).
// NOTE: JSON.stringify key-sort is a stub; use a conformant RFC 8785 library before production.

import { generateKeyPairSync, sign, createPrivateKey, type KeyObject } from "node:crypto";
import type { ApprovalChallenge, ApprovalDecision } from "../contract/types";

export class OperatorSigner {
  private readonly privateKey: KeyObject;
  public readonly keyId: string;

  constructor(privateKeyPemOrKey?: KeyObject | string, keyId: string = "operator-key-default") {
    this.keyId = keyId;
    if (!privateKeyPemOrKey) {
      const { privateKey } = generateKeyPairSync("ed25519");
      this.privateKey = privateKey;
    } else if (typeof privateKeyPemOrKey === "string") {
      this.privateKey = createPrivateKey(privateKeyPemOrKey);
    } else {
      this.privateKey = privateKeyPemOrKey;
    }
  }

  public signChallenge(
    challenge: ApprovalChallenge,
    resolution: "approved" | "rejected" = "approved",
    reviewer: string = "operator"
  ): ApprovalDecision {
    const signedPayload = {
      approvalId: challenge.approvalId,
      argsDigest: challenge.argsDigest,
      descriptorDigest: challenge.descriptorDigest,
      expiresAt: challenge.expiresAt,
      keyId: this.keyId,
      resolution,
      reviewer,
    };

    // RFC 8785 Canonical JSON: sort keys. Use a conformant library (e.g. canonicalize) in production.
    const canonicalJson = JSON.stringify(signedPayload, Object.keys(signedPayload).sort() as (keyof typeof signedPayload)[]);
    const signatureBuffer = sign(null, Buffer.from(canonicalJson, "utf-8"), this.privateKey);

    return {
      ...signedPayload,
      signature: signatureBuffer.toString("hex"),
    };
  }
}
