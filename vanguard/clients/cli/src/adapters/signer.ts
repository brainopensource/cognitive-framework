import { generateKeyPairSync, sign, type KeyObject, createPrivateKey } from "node:crypto";
import type { ApprovalChallenge, ApprovalDecision } from "../contract/types.js";

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

    // RFC 8785 Canonical JSON sort keys
    const canonicalJson = JSON.stringify(signedPayload, Object.keys(signedPayload).sort());
    const signatureBuffer = sign(null, Buffer.from(canonicalJson, "utf-8"), this.privateKey);

    return {
      ...signedPayload,
      signature: signatureBuffer.toString("hex"),
    };
  }
}
