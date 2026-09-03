import React from "react";
import type { StudioFold } from "../store/fold.js";

export const ArenaView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div>
        <h3 style={{ margin: 0, fontSize: 14, color: "var(--text-primary)" }}>
          Controlled Comparison Arena (Arm A vs. Arm B)
        </h3>
        <p style={{ margin: "4px 0 0 0", fontSize: 12, color: "var(--text-muted)" }}>
          Scientific paired comparison with immutable preregistration and McNemar discordant pair test.
        </p>
      </div>

      <div style={{ padding: 14, background: "rgba(245, 158, 11, .08)", border: "1px solid var(--signal-hold)", borderRadius: 6, color: "var(--signal-hold)", fontSize: 12 }}>
        Comparison data is unavailable: the runtime has not supplied a canonical preregistration and paired-run projection. No matrix or p-value is displayed.
      </div>
      {/* Preregistration banner */}
      <div
        style={{
          background: "var(--bg-panel)",
          border: "1px solid var(--border-subtle)",
          borderRadius: 6,
          padding: 12,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontSize: 12,
        }}
      >
        <div>
          <span style={{ color: "var(--text-muted)" }}>Preregistration Binding:</span>{" "}
          <strong style={{ color: "var(--signal-flow)", fontFamily: "var(--font-mono)" }}>
            unavailable
          </strong>
        </div>
        <span
          style={{
            background: "rgba(16, 185, 129, 0.15)",
            color: "var(--signal-proof)",
            border: "1px solid var(--signal-proof)",
            padding: "2px 6px",
            borderRadius: 4,
            fontSize: 10,
            fontWeight: "bold",
          }}
        >
          NOT AVAILABLE
        </span>
      </div>

      {/* 2x2 Contingency Matrix Card */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        <div
          style={{
            background: "var(--bg-card)",
            border: "1px solid var(--border-subtle)",
            borderRadius: 6,
            padding: 16,
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}
        >
          <div style={{ fontWeight: "bold", fontSize: 13, color: "var(--text-primary)" }}>
            2×2 Discordant Contingency Matrix
          </div>

          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12, textAlign: "center" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                <th style={{ padding: 6, color: "var(--text-muted)", textAlign: "left" }}></th>
                <th style={{ padding: 6, color: "var(--signal-flow)" }}>Arm A Pass</th>
                <th style={{ padding: 6, color: "var(--signal-deny)" }}>Arm A Fail</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                <td style={{ padding: 6, color: "var(--signal-proof)", fontWeight: "bold", textAlign: "left" }}>
                  Arm B Pass
                </td>
                <td style={{ padding: 8, color: "var(--text-muted)" }}>—</td>
                <td style={{ padding: 8, background: "rgba(236, 72, 153, 0.1)", fontWeight: "bold", color: "var(--signal-deny)" }}>
                  —
                </td>
              </tr>
              <tr>
                <td style={{ padding: 6, color: "var(--signal-deny)", fontWeight: "bold", textAlign: "left" }}>
                  Arm B Fail
                </td>
                <td style={{ padding: 8, background: "rgba(0, 210, 255, 0.1)", fontWeight: "bold", color: "var(--signal-flow)" }}>
                  —
                </td>
                <td style={{ padding: 8, color: "var(--text-muted)" }}>—</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Statistical Test Result from lab/bench.py */}
        <div
          style={{
            background: "var(--bg-card)",
            border: "1px solid var(--border-subtle)",
            borderRadius: 6,
            padding: 16,
            display: "flex",
            flexDirection: "column",
            justifyContent: "space-between",
          }}
        >
          <div>
            <div style={{ fontWeight: "bold", fontSize: 13, color: "var(--text-primary)", marginBottom: 8 }}>
              Exact Two-Sided McNemar Test
            </div>
            <div style={{ fontSize: 12, color: "var(--text-secondary)", display: "flex", flexDirection: "column", gap: 4 }}>
              <div>Discordant pairs: unavailable</div>
              <div>χ² statistic: unavailable</div>
              <div>p-value: withheld until preregistration and paired runs exist</div>
            </div>
          </div>

          <div
            style={{
              padding: 8,
              background: "rgba(245, 158, 11, 0.1)",
              border: "1px solid var(--signal-hold)",
              borderRadius: 4,
              fontSize: 11,
              color: "var(--signal-hold)",
              fontWeight: "bold",
            }}
          >
            ▸ NOT STATISTICALLY SIGNIFICANT (p &gt; 0.05) — Insufficient evidence for harness promotion.
          </div>
        </div>
      </div>
    </div>
  );
};
