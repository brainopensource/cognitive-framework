import React, { useState } from "react";
import type { PendingApprovalRecord } from "../store/fold.js";

export type ApprovalInterceptorProps = {
  readonly pendingApproval?: PendingApprovalRecord;
  readonly onResolve?: (approvalId: string, decision: "approve" | "reject") => Promise<void>;
};

export const ApprovalInterceptor: React.FC<ApprovalInterceptorProps> = ({
  pendingApproval,
  onResolve,
}) => {
  const [submitting, setSubmitting] = useState(false);

  if (!pendingApproval) {
    return (
      <div
        style={{
          padding: 16,
          background: "var(--bg-panel)",
          borderRadius: 6,
          border: "1px solid var(--border-subtle)",
          color: "var(--text-muted)",
          fontSize: 12,
          display: "flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        <span style={{ color: "var(--signal-proof)" }}>✓</span> No privileged actions currently awaiting operator approval.
      </div>
    );
  }

  const handleDecision = async (decision: "approve" | "reject") => {
    if (!onResolve) return;
    setSubmitting(true);
    try {
      await onResolve(pendingApproval.approvalId, decision);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      style={{
        background: "var(--bg-card)",
        border: "1px solid var(--signal-hold)",
        borderRadius: 8,
        padding: 16,
        display: "flex",
        flexDirection: "column",
        gap: 12,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ color: "var(--signal-hold)", fontSize: 16 }}>⚠️</span>
          <span style={{ fontWeight: "bold", fontSize: 13, color: "var(--text-primary)" }}>
            Approval Required (F-08 Suspended Before Lease)
          </span>
        </div>
        <span
          style={{
            background: "rgba(245, 158, 11, 0.15)",
            color: "var(--signal-hold)",
            padding: "2px 6px",
            borderRadius: 4,
            fontSize: 10,
            fontFamily: "var(--font-mono)",
            border: "1px solid var(--signal-hold)",
          }}
        >
          K-14 BOUND
        </span>
      </div>

      <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>
        Action: <strong style={{ color: "var(--signal-flow)" }}>{pendingApproval.action}</strong> requested by{" "}
        <span style={{ fontFamily: "var(--font-mono)" }}>{pendingApproval.principal}</span>
      </div>

      {pendingApproval.normalizedDiff && (
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Normalized Patch Diff:</span>
          <pre
            style={{
              background: "var(--bg-canvas)",
              padding: 8,
              borderRadius: 4,
              border: "1px solid var(--border-subtle)",
              fontFamily: "var(--font-mono)",
              fontSize: 11,
              color: "var(--text-primary)",
              maxHeight: 120,
              overflowY: "auto",
              whiteSpace: "pre-wrap",
            }}
          >
            {pendingApproval.normalizedDiff}
          </pre>
        </div>
      )}

      <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
        <button
          disabled={submitting}
          onClick={() => handleDecision("approve")}
          style={{
            flex: 1,
            padding: "8px 12px",
            background: "var(--signal-proof)",
            color: "#000",
            fontWeight: "bold",
            fontSize: 12,
            border: "none",
            borderRadius: 4,
            cursor: submitting ? "not-allowed" : "pointer",
            opacity: submitting ? 0.6 : 1,
          }}
        >
          {submitting ? "Signing..." : "Approve & Sign Decision"}
        </button>
        <button
          disabled={submitting}
          onClick={() => handleDecision("reject")}
          style={{
            flex: 1,
            padding: "8px 12px",
            background: "transparent",
            color: "var(--signal-deny)",
            fontWeight: "bold",
            fontSize: 12,
            border: "1px solid var(--signal-deny)",
            borderRadius: 4,
            cursor: submitting ? "not-allowed" : "pointer",
            opacity: submitting ? 0.6 : 1,
          }}
        >
          Reject (Fail-Closed)
        </button>
      </div>
    </div>
  );
};
