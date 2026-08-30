import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { TauriNativeBridge } from "../src/bridge/tauri-bridge.js";
import { DesktopKeychainSigner } from "../src/bridge/keychain-signer.js";
import type { ApprovalChallenge } from "@aether/contracts";

describe("@aether/desktop — Native Platform Bridge & Keychain Signer", () => {
  const challenge: ApprovalChallenge = {
    approvalId: "app-desk-01",
    processId: "proc-1",
    action: "fs.write",
    normalizedDiff: "+test",
    argsDigest: "sha256:" + "a".repeat(64),
    descriptorDigest: "sha256:" + "b".repeat(64),
    principal: "operator",
    expiresAt: "2026-08-30T00:00:00.000Z",
  };

  it("TauriNativeBridge reports non-Tauri in standard node/browser environment", () => {
    const bridge = new TauriNativeBridge();
    assert.equal(bridge.isTauri(), false);
  });

  it("DesktopKeychainSigner signs challenge cleanly with web fallback", async () => {
    const signer = new DesktopKeychainSigner();
    const decision = await signer.signChallenge(challenge, "approved");
    assert.equal(decision.approvalId, "app-desk-01");
    assert.equal(decision.resolution, "approved");
    assert.ok(decision.signature.length > 0);
  });
});
