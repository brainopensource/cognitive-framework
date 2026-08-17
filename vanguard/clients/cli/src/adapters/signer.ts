import canonicalize from "canonicalize";
import { generateKeyPairSync, sign, type KeyObject, createPrivateKey } from "node:crypto";
import { chmodSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import type { ApprovalChallenge, ApprovalDecision } from "../contract/types.js";

export function jcsCanonicalize(value: unknown): string {
  const text = canonicalize(value);
  if (typeof text !== "string") {
    throw new Error("RFC 8785 canonicalize produced no string");
  }
  return text;
}

export function defaultKeyDir(): string {
  return join(homedir(), ".vanguard", "keys");
}

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

  static loadOrCreate(dir: string = defaultKeyDir(), keyId: string = "operator-key-default"): OperatorSigner {
    const pemPath = join(dir, `${keyId}.pem`);
    if (existsSync(pemPath)) {
      return new OperatorSigner(readFileSync(pemPath, "utf8"), keyId);
    }
    mkdirSync(dir, { recursive: true, mode: 0o700 });
    const { privateKey } = generateKeyPairSync("ed25519");
    const pem = privateKey.export({ type: "pkcs8", format: "pem" });
    if (typeof pem !== "string") throw new Error("failed to export operator key");
    writeFileSync(pemPath, pem, { mode: 0o600 });
    chmodSync(pemPath, 0o600);
    return new OperatorSigner(privateKey, keyId);
  }

  public signChallenge(
    challenge: ApprovalChallenge,
    resolution: "approved" | "rejected" = "approved",
    reviewer: string = "operator"
  ): ApprovalDecision {
    if (!challenge.argsDigest || !challenge.descriptorDigest || !challenge.expiresAt) {
      throw new Error("approval challenge missing argsDigest, descriptorDigest, or expiresAt");
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
    const signatureBuffer = sign(null, Buffer.from(canonicalJson, "utf-8"), this.privateKey);
    return {
      ...signedPayload,
      signature: signatureBuffer.toString("hex"),
    };
  }
}
