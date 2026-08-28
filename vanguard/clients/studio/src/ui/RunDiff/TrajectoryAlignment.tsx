import React from "react";

type AlignedStep = {
  step: number;
  baselineAction: string;
  treatmentAction: string;
  baselineTokens: number;
  treatmentTokens: number;
  status: "IDENTICAL" | "IMPROVED" | "DIVERGENT";
};

const ALIGNED_STEPS: AlignedStep[] = [
  { step: 1, baselineAction: "GoalDeclared: Patch dispatch governor leak", treatmentAction: "GoalDeclared: Patch dispatch governor leak", baselineTokens: 120, treatmentTokens: 120, status: "IDENTICAL" },
  { step: 2, baselineAction: "ContextCompiled (full repo sweep)", treatmentAction: "ContextCompiled (L1-L5 prefix-cached)", baselineTokens: 1840, treatmentTokens: 620, status: "IMPROVED" },
  { step: 3, baselineAction: "ProposalProduced: fs.read full file (800 lines)", treatmentAction: "ProposalProduced: ast.query surgical block", baselineTokens: 950, treatmentTokens: 210, status: "IMPROVED" },
  { step: 4, baselineAction: "EffectStarted: proc.exec bash rewrite", treatmentAction: "ApprovalRequested: fs.patch mandatory finally", baselineTokens: 1100, treatmentTokens: 180, status: "DIVERGENT" },
  { step: 5, baselineAction: "EpisodeCompleted (outcome: fail, test timeout)", treatmentAction: "EpisodeCompleted (outcome: satisfied, 100% tests pass)", baselineTokens: 810, treatmentTokens: 280, status: "IMPROVED" },
];

export const TrajectoryAlignment: React.FC = () => {
  return (
    <div style={{ padding: 16, background: "var(--bg-surface)", display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <span style={{ fontWeight: 700, fontSize: 13, color: "var(--text-primary)" }}>
            CAUSAL TRAJECTORY STEP-BY-STEP ALIGNMENT
          </span>
          <p style={{ margin: "2px 0 0 0", fontSize: 11, color: "var(--text-secondary)" }}>
            Temporal and causal alignment of turns across execution traces.
          </p>
        </div>
        <span className="badge-mono" style={{ color: "var(--signal-proof)" }}>
          ALIGNMENT SCORE: 94.2%
        </span>
      </div>

      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 11 }}>
        <thead>
          <tr style={{ borderBottom: "1px solid var(--border-subtle)", textAlign: "left", color: "var(--text-muted)" }}>
            <th style={{ padding: "8px 6px" }}>Step</th>
            <th style={{ padding: "8px 6px" }}>Baseline Action (v1)</th>
            <th style={{ padding: "8px 6px" }}>Treatment Action (v2)</th>
            <th style={{ padding: "8px 6px" }}>Tokens (Base → Treat)</th>
            <th style={{ padding: "8px 6px" }}>Status</th>
          </tr>
        </thead>
        <tbody>
          {ALIGNED_STEPS.map((s) => (
            <tr key={s.step} style={{ borderBottom: "1px solid var(--border-subtle)", color: "var(--text-primary)" }}>
              <td className="font-mono" style={{ padding: "8px 6px", color: "var(--signal-flow)" }}>
                0{s.step}
              </td>
              <td style={{ padding: "8px 6px", color: "var(--text-secondary)" }}>{s.baselineAction}</td>
              <td style={{ padding: "8px 6px", fontWeight: 600, color: "var(--text-primary)" }}>{s.treatmentAction}</td>
              <td className="font-mono" style={{ padding: "8px 6px", fontSize: 10 }}>
                <span style={{ color: "var(--text-muted)" }}>{s.baselineTokens}</span> →{" "}
                <strong style={{ color: "var(--signal-proof)" }}>{s.treatmentTokens}</strong>
              </td>
              <td style={{ padding: "8px 6px" }}>
                <span
                  className="badge-mono"
                  style={{
                    color: s.status === "IMPROVED" ? "var(--signal-proof)" : s.status === "IDENTICAL" ? "var(--text-secondary)" : "var(--signal-hold)",
                    background: s.status === "IMPROVED" ? "rgba(74, 222, 128, 0.1)" : s.status === "IDENTICAL" ? "rgba(255,255,255,0.05)" : "rgba(251, 191, 36, 0.1)",
                  }}
                >
                  {s.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
