import { useState } from "react";
import { DiffEditor } from "@monaco-editor/react";
import { OperatorSigner, type PendingApproval, type RuntimeClient } from "@vanguard/client-core";
import { SlotFrame } from "./files";

export function ApproveSlot({ approval, client }: { approval?: PendingApproval; client: RuntimeClient }) {
  const [state, setState] = useState<"idle" | "requested" | "not_available">("idle");
  const valid = Boolean(approval?.argsDigest && approval.descriptorDigest && approval.expiresAt);
  async function resolve(decision: "approve" | "reject") { if (!approval || !valid) return; setState("requested"); try { const signed = new OperatorSigner().signChallenge({ approvalId: approval.approvalId, processId: "gui", action: "replay", normalizedDiff: approval.unifiedDiff, argsDigest: approval.argsDigest, descriptorDigest: approval.descriptorDigest, principal: "operator", expiresAt: approval.expiresAt }, decision === "approve" ? "approved" : "rejected"); const result = await client.resolveApproval({ approvalId: approval.approvalId, decision, signature: signed.signature, signerKeyRef: signed.keyId }); if (!result.ok) setState("not_available"); } catch { setState("not_available"); } }
  return <SlotFrame title="MONACO DIFF / APPROVE">{approval ? <DiffEditor height="360px" original="" modified={approval.unifiedDiff} language="diff" theme="vs-dark" options={{ readOnly: true, minimap: { enabled: false } }} /> : <div className="not-available">No ApprovalRequested envelope in this replay.</div>}<div className="approve-actions"><button disabled={!valid || state === "requested"} onClick={() => resolve("approve")}>APPROVE &amp; SIGN</button><button disabled={!valid || state === "requested"} onClick={() => resolve("reject")}>REJECT</button></div>{!valid && approval && <p className="muted">not_available · J4 approval challenge is missing required digests.</p>}{state === "requested" && <p className="muted">requested · waiting for ApprovalResolved.</p>}{state === "not_available" && <p className="muted">not_available · replay resolve is read-only.</p>}</SlotFrame>;
}
