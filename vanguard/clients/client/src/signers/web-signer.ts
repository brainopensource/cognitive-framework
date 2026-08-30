import {
  jcsCanonicalize,
  type ApprovalChallenge,
  type ApprovalDecision,
  type SignerPort,
} from "@aether/contracts";

function bufferToHex(buffer: ArrayBuffer): string {
  return Array.from(new Uint8Array(buffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export class WebCryptoSigner implements SignerPort {
  private keyPair: CryptoKeyPair | null = null;
  public readonly keyId: string;
  public readonly principal: string = "operator";

  constructor(keyId: string = "web-operator-key-default") {
    this.keyId = keyId;
  }

  async init(): Promise<void> {
    if (!this.keyPair) {
      if (typeof globalThis.crypto?.subtle === "undefined") {
        throw new Error("WebCrypto is not supported in this environment");
      }
      this.keyPair = (await globalThis.crypto.subtle.generateKey(
        {
          name: "Ed25519",
        },
        false,
        ["sign", "verify"]
      )) as CryptoKeyPair;
    }
  }

  async signChallenge(
    challenge: ApprovalChallenge,
    resolution: "approved" | "rejected" = "approved",
    reviewer: string = "operator"
  ): Promise<ApprovalDecision> {
    if (!this.keyPair) {
      await this.init();
    }
    if (!challenge.argsDigest || !challenge.descriptorDigest || !challenge.expiresAt) {
      throw new Error("Approval challenge missing argsDigest, descriptorDigest, or expiresAt");
    }

    const signedPayload = {
      approvalId: challenge.approvalId,
      argsDigest: challenge.argsDigest,
      descriptorDigest: challenge.descriptorDigest,
      expiresAt: challenge.expiresAt,
      keyId: this.keyId,
      resolution,
      reviewer,
    };

    const canonicalJson = jcsCanonicalize(signedPayload);
    const encoder = new TextEncoder();
    const data = encoder.encode(canonicalJson);

    const signatureBuffer = await globalThis.crypto.subtle.sign(
      {
        name: "Ed25519",
      },
      this.keyPair!.privateKey,
      data
    );

    return {
      ...signedPayload,
      signature: bufferToHex(signatureBuffer),
    };
  }
}
