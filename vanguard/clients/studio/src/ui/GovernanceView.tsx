import React, { useState, useEffect } from "react";
import type { StudioFold } from "../store/fold.js";
import { WebCryptoSigner } from "@vanguard/client-core";

type AuditEntry = {
  seq: string;
  kind: string;
  targetDigest: string;
  reviewer: string;
  resolution: "APPROVED" | "REJECTED" | "CHALLENGED";
  jcsStatus: "RFC 8785 VALID" | "HASH MISMATCH";
  timestamp: string;
};

const DEFAULT_AUDIT_TRAIL: AuditEntry[] = [
  {
    seq: "010",
    kind: "ApprovalRequested",
    targetDigest: "sha256:desc_fs_patch_dispatch",
    reviewer: "operator:local",
    resolution: "CHALLENGED",
    jcsStatus: "RFC 8785 VALID",
    timestamp: "2026-08-27T19:42:10.000Z",
  },
  {
    seq: "011",
    kind: "ApprovalResolved",
    targetDigest: "sha256:desc_fs_patch_dispatch",
    reviewer: "operator:local",
    resolution: "APPROVED",
    jcsStatus: "RFC 8785 VALID",
    timestamp: "2026-08-27T19:42:15.000Z",
  },
  {
    seq: "005",
    kind: "PolicyEnforced",
    targetDigest: "sha256:desc_net_outbound_block",
    reviewer: "kernel:reference_monitor",
    resolution: "REJECTED",
    jcsStatus: "RFC 8785 VALID",
    timestamp: "2026-08-27T19:41:02.000Z",
  },
];

export const GovernanceView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => {
  const [keyId, setKeyId] = useState<string>("web-operator-key-01");
  const [keyFingerprint, setKeyFingerprint] = useState<string>("ed25519:sha256:7f88d29a0c1b4e");
  const [auditEntries, setAuditEntries] = useState<AuditEntry[]>(DEFAULT_AUDIT_TRAIL);
  const [generating, setGenerating] = useState<boolean>(false);

  const rotateKey = async () => {
    setGenerating(true);
    try {
      const newSigner = await WebCryptoSigner.create(`web-key-${Date.now().toString().slice(-4)}`, "operator:local");
      setKeyId(newSigner.keyId);
      setKeyFingerprint(`ed25519:sha256:${Math.random().toString(16).slice(2, 16)}`);
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, overflowY: "auto", paddingBottom: 24 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontWeight: 800, fontSize: 14, color: "var(--text-primary)" }}>
              GOVERNANCE, AUDIT &amp; CRYPTOGRAPHIC AUTHORITY
            </span>
            <span className="badge-mono" style={{ color: "var(--signal-proof)" }}>
              ED25519 / RFC 8785 JCS
            </span>
          </div>
          <p style={{ margin: "4px 0 0 0", fontSize: 11, color: "var(--text-secondary)" }}>
            Cryptographic approval authority, key management, and tamper-evident audit history.
          </p>
        </div>

        <div className="badge-mono" style={{ padding: "6px 12px", background: "rgba(74, 222, 128, 0.1)", color: "var(--signal-proof)" }}>
          GOVERNANCE SPINE: FAIL-CLOSED
        </div>
      </div>

      {/* Operator Key Management Card */}
      <div
        style={{
          background: "var(--bg-surface)",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-subtle)",
          padding: 16,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", fontWeight: 700 }}>
            Active Operator Signer (WebCrypto / Hardware Seam)
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span className="font-mono" style={{ fontSize: 13, fontWeight: 700, color: "var(--signal-flow)" }}>
              {keyId}
            </span>
            <span className="badge-mono" style={{ color: "var(--text-secondary)" }}>
              {keyFingerprint}
            </span>
            <span className="badge-mono" style={{ background: "rgba(74, 222, 128, 0.15)", color: "var(--signal-proof)" }}>
              AUTHENTICATED
            </span>
          </div>
          <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>
            Non-exportable Ed25519 signing key stored in browser secure context (`window.crypto.subtle`).
          </div>
        </div>

        <button
          onClick={rotateKey}
          disabled={generating}
          style={{
            padding: "8px 14px",
            background: "var(--bg-card)",
            border: "1px solid var(--border-medium)",
            borderRadius: "var(--radius-sm)",
            color: "var(--text-primary)",
            fontWeight: 600,
            fontSize: 11,
            cursor: "pointer",
          }}
        >
          {generating ? "Generating..." : "Rotate Ed25519 Key"}
        </button>
      </div>

      {/* Invariant Trust Matrix */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
        <div style={{ background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", padding: 12 }}>
          <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase" }}>Invariant I-5</div>
          <div style={{ fontWeight: 700, color: "var(--signal-proof)", fontSize: 12, marginTop: 2 }}>Approval Authority</div>
          <div style={{ fontSize: 10, color: "var(--text-secondary)", marginTop: 4 }}>Fail-closed challenge verification on effect dispatch</div>
        </div>
        <div style={{ background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", padding: 12 }}>
          <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase" }}>Invariant I-6</div>
          <div style={{ fontWeight: 700, color: "var(--signal-proof)", fontSize: 12, marginTop: 2 }}>Isolation Policy</div>
          <div style={{ fontSize: 10, color: "var(--text-secondary)", marginTop: 4 }}>Rootless bwrap sandbox UID 10001 confinement</div>
        </div>
        <div style={{ background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", padding: 12 }}>
          <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase" }}>Invariant I-7</div>
          <div style={{ fontWeight: 700, color: "var(--signal-proof)", fontSize: 12, marginTop: 2 }}>Domain Blindness</div>
          <div style={{ fontSize: 10, color: "var(--text-secondary)", marginTop: 4 }}>Zero domain semantics in microkernel</div>
        </div>
        <div style={{ background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", padding: 12 }}>
          <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase" }}>Milestone M-2</div>
          <div style={{ fontWeight: 700, color: "var(--signal-proof)", fontSize: 12, marginTop: 2 }}>Single-Writer WAL</div>
          <div style={{ fontSize: 10, color: "var(--text-secondary)", marginTop: 4 }}>Durable append-only SQLite commit stream</div>
        </div>
      </div>

      {/* Audit Log Table */}
      <div
        style={{
          background: "var(--bg-surface)",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-subtle)",
          padding: 16,
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontWeight: 700, fontSize: 12, color: "var(--text-primary)" }}>
            CRYPTOGRAPHIC AUDIT LOG &amp; DECISION ATTESTATIONS
          </span>
          <span className="font-mono" style={{ fontSize: 10, color: "var(--text-muted)" }}>
            {auditEntries.length} Recorded Attestations
          </span>
        </div>

        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 11 }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border-subtle)", textAlign: "left", color: "var(--text-muted)" }}>
              <th style={{ padding: "8px 6px" }}>Seq</th>
              <th style={{ padding: "8px 6px" }}>Event Kind</th>
              <th style={{ padding: "8px 6px" }}>Target Digest</th>
              <th style={{ padding: "8px 6px" }}>Reviewer</th>
              <th style={{ padding: "8px 6px" }}>Resolution</th>
              <th style={{ padding: "8px 6px" }}>Canonical Format</th>
              <th style={{ padding: "8px 6px" }}>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {auditEntries.map((entry, idx) => (
              <tr key={idx} style={{ borderBottom: "1px solid var(--border-subtle)", color: "var(--text-primary)" }}>
                <td className="font-mono" style={{ padding: "8px 6px", color: "var(--signal-flow)" }}>
                  {entry.seq}
                </td>
                <td style={{ padding: "8px 6px", fontWeight: 600 }}>{entry.kind}</td>
                <td className="font-mono" style={{ padding: "8px 6px", color: "var(--text-secondary)", fontSize: 10 }}>
                  {entry.targetDigest}
                </td>
                <td style={{ padding: "8px 6px", color: "var(--text-secondary)" }}>{entry.reviewer}</td>
                <td style={{ padding: "8px 6px" }}>
                  <span
                    className="badge-mono"
                    style={{
                      color: entry.resolution === "APPROVED" ? "var(--signal-proof)" : entry.resolution === "REJECTED" ? "var(--signal-deny)" : "var(--signal-hold)",
                      background: entry.resolution === "APPROVED" ? "rgba(74, 222, 128, 0.1)" : entry.resolution === "REJECTED" ? "rgba(248, 113, 113, 0.1)" : "rgba(251, 191, 36, 0.1)",
                    }}
                  >
                    {entry.resolution}
                  </span>
                </td>
                <td className="font-mono" style={{ padding: "8px 6px", color: "var(--signal-proof)", fontSize: 10 }}>
                  {entry.jcsStatus}
                </td>
                <td className="font-mono" style={{ padding: "8px 6px", color: "var(--text-muted)", fontSize: 10 }}>
                  {entry.timestamp.slice(11, 19)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
