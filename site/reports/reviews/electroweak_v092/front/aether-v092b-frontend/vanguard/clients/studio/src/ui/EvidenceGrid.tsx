import React from "react";
import type { EvidenceRow } from "../store/fold.js";

export type EvidenceGridProps = {
  readonly rows: readonly EvidenceRow[];
};

export const EvidenceGrid: React.FC<EvidenceGridProps> = ({ rows }) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div>
        <h3 style={{ margin: 0, fontSize: 14, color: "var(--text-primary)" }}>
          M-4 Single-Run Evidence Grid (Canonical 9 Rows)
        </h3>
        <p style={{ margin: "4px 0 0 0", fontSize: 12, color: "var(--text-muted)" }}>
          Audited against canonical four-valued vocabularies: absent / invalid / unverifiable / present_valid.
        </p>
      </div>

      <div
        style={{
          border: "1px solid var(--border-subtle)",
          borderRadius: 6,
          overflow: "hidden",
          background: "var(--bg-panel)",
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
          <thead>
            <tr style={{ background: "var(--bg-card)", borderBottom: "1px solid var(--border-subtle)" }}>
              <th style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)", width: 48 }}>#</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)", width: 140 }}>Category</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)", width: 220 }}>Evidence Fact</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)" }}>Audit Details</th>
              <th style={{ padding: "8px 12px", textAlign: "left", color: "var(--text-muted)", width: 120 }}>State</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              let badgeColor = "var(--text-muted)";
              let badgeBg = "rgba(100, 116, 139, 0.15)";
              let glyph = "○";

              if (row.state === "present_valid") {
                badgeColor = "var(--signal-proof)";
                badgeBg = "rgba(16, 185, 129, 0.15)";
                glyph = "✓";
              } else if (row.state === "invalid") {
                badgeColor = "var(--signal-deny)";
                badgeBg = "rgba(236, 72, 153, 0.15)";
                glyph = "✗";
              } else if (row.state === "unverifiable") {
                badgeColor = "var(--signal-hold)";
                badgeBg = "rgba(245, 158, 11, 0.15)";
                glyph = "⧗";
              }

              return (
                <tr key={row.line} style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                  <td style={{ padding: "8px 12px", fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>
                    R{row.line}
                  </td>
                  <td style={{ padding: "8px 12px", fontWeight: "500", color: "var(--text-secondary)" }}>
                    {row.category}
                  </td>
                  <td style={{ padding: "8px 12px", color: "var(--text-primary)", fontWeight: "bold" }}>
                    {row.title}
                  </td>
                  <td style={{ padding: "8px 12px", color: "var(--text-secondary)", fontSize: 11 }}>
                    {row.details}
                  </td>
                  <td style={{ padding: "8px 12px" }}>
                    <span
                      style={{
                        display: "inline-flex",
                        alignItems: "center",
                        gap: 4,
                        padding: "2px 8px",
                        borderRadius: 4,
                        fontSize: 10,
                        fontWeight: "bold",
                        fontFamily: "var(--font-mono)",
                        color: badgeColor,
                        background: badgeBg,
                        border: `1px solid ${badgeColor}`,
                      }}
                    >
                      <span>{glyph}</span>
                      <span>{row.state.toUpperCase()}</span>
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
