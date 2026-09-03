import { dispatchApproval, OperatorSigner, type PendingApproval, type RuntimeClient } from "@aether/client";
import type { CommandReceipt, Result } from "@aether/contracts";

function hasChallengeDigests(approval: PendingApproval): boolean {
  return Boolean(approval.argsDigest && approval.descriptorDigest && approval.expiresAt);
}

/** P0-4 TUI path: y/n signs with OperatorSigner when challenge digests exist; never fabricates empty digests. */
export async function submitInteractiveApproval(
  client: Pick<RuntimeClient, "resolveApproval">,
  approval: PendingApproval,
  key: string,
  signer?: OperatorSigner
): Promise<Result<CommandReceipt>> {
  if (!hasChallengeDigests(approval)) {
    return dispatchApproval(client, approval.approvalId, key);
  }
  const action = key === "y" ? "approve" : key === "n" ? "reject" : undefined;
  if (!action) {
    return dispatchApproval(client, approval.approvalId, key);
  }
  const op = signer ?? OperatorSigner.loadOrCreate();
  const signed = op.signChallenge(
    {
      approvalId: approval.approvalId,
      processId: approval.episodeId,
      action: "",
      normalizedDiff: approval.unifiedDiff,
      argsDigest: approval.argsDigest,
      descriptorDigest: approval.descriptorDigest,
      principal: "operator",
      expiresAt: approval.expiresAt,
    },
    action === "approve" ? "approved" : "rejected"
  );
  return client.resolveApproval({
    approvalId: approval.approvalId,
    decision: action,
    signature: signed.signature,
    signerKeyRef: signed.keyId,
  });
}
