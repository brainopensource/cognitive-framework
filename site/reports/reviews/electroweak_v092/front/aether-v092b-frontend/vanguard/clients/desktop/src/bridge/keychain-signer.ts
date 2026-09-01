import type { ApprovalChallenge, ApprovalDecision, SignerPort } from "@aether/contracts";
import { WebCryptoSigner } from "@aether/client";
import { TauriNativeBridge } from "./tauri-bridge.js";

export class DesktopKeychainSigner implements SignerPort {
  public readonly keyId: string = "desktop-keychain-key";
  public readonly principal: string = "operator";
  private readonly bridge: TauriNativeBridge;
  private readonly webSigner: WebCryptoSigner;

  constructor(bridge: TauriNativeBridge = new TauriNativeBridge()) {
    this.bridge = bridge;
    this.webSigner = new WebCryptoSigner(this.keyId);
  }

  async signChallenge(
    challenge: ApprovalChallenge,
    resolution: "approved" | "rejected" = "approved",
    reviewer: string = "operator"
  ): Promise<ApprovalDecision> {
    if (this.bridge.isTauri()) {
      return this.bridge.signApproval(challenge, resolution);
    }
    return this.webSigner.signChallenge(challenge, resolution, reviewer);
  }
}
