import { fail, type CommandReceipt, type Result } from "@aether/contracts";
import type { RuntimeClient } from "../client.js";

export type ApprovalAction = "approve" | "reject" | "correct";

export function approvalActionForKey(key: string): ApprovalAction | undefined {
  if (key === "y") return "approve";
  if (key === "n") return "reject";
  if (key === "c") return "correct";
  return undefined;
}

export async function dispatchApproval(
  client: Pick<RuntimeClient, "resolveApproval">,
  approvalId: string,
  key: string,
): Promise<Result<CommandReceipt>> {
  const action = approvalActionForKey(key);
  if (action !== "approve" && action !== "reject") {
    return fail("invalid_request", `key ${key} is not an approval decision`);
  }
  return client.resolveApproval({ approvalId, decision: action });
}
