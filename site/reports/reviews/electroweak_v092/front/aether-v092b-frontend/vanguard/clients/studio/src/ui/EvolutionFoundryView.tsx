import React, { useState } from "react";
import type { StudioFold } from "../store/fold.js";

type DPOPair = {
  pairId: string;
  taskTitle: string;
  chosenTrajectory: {
    runId: string;
    turns: number;
    tokens: number;
    costMicros: number;
    verdict: "1";
    strategySummary: string;
  };
  rejectedTrajectory: {
    runId: string;
    turns: number;
    tokens: number;
    costMicros: number;
    verdict: "0";
    failureReason: string;
  };
  extractedSkillName: string;
  mcnemarPValue: number;
  promotionStatus: "PROMOTED" | "EVALUATING" | "REJECTED";
};

const DEMO_DPO_PAIRS: DPOPair[] = [
  {
    pairId: "dpo_001_lease_leak",
    taskTitle: "Fix Governor Lease Leak on Adapter Raise",
    chosenTrajectory: {
      runId: "run-winner-49a",
      turns: 2,
      tokens: 1420,
      costMicros: 284000,
      verdict: "1",
      strategySummary: "Placed S11 release in mandatory finally block (K-06) immediately after guarded execution.",
    },
    rejectedTrajectory: {
      runId: "run-loser-12c",
      turns: 6,
      tokens: 4900,
      costMicros: 980000,
      verdict: "0",
      failureReason: "Tried catching specific exception types in caller and missed unhandled adapter abort.",
    },
    extractedSkillName: "skills/governor_finally_reclamation.md",
    mcnemarPValue: 0.008,
    promotionStatus: "PROMOTED",
  },
  {
    pairId: "dpo_002_jcs_canonical",
    taskTitle: "RFC 8785 JSON Canonicalization Format",
    chosenTrajectory: {
      runId: "run-winner-88f",
      turns: 1,
      tokens: 980,
      costMicros: 196000,
      verdict: "1",
      strategySummary: "Applied json.dumps with exact strict separators=(',', ':') and ensure_ascii=False.",
    },
    rejectedTrajectory: {
      runId: "run-loser-33a",
      turns: 4,
      tokens: 3200,
      costMicros: 640000,
      verdict: "0",
      failureReason: "Used default json.dumps whitespace which caused descriptor digest mismatch.",
    },
    extractedSkillName: "skills/jcs_rfc8785_canonical.md",
    mcnemarPValue: 0.015,
    promotionStatus: "PROMOTED",
  },
];

export const EvolutionFoundryView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => {
  const [selectedPair, setSelectedPair] = useState<DPOPair>(DEMO_DPO_PAIRS[0]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontWeight: 700, fontSize: 13, color: "var(--text-primary)" }}>
              M-8 CONTINUOUS SELF-EVOLUTION &amp; DPO SKILL FOUNDRY
            </span>
            <span className="badge-mono" style={{ color: "var(--signal-proof)" }}>
              MCNEMAR GATED (p &lt; 0.05)
            </span>
          </div>
          <p style={{ margin: "4px 0 0 0", fontSize: 11, color: "var(--text-secondary)" }}>
            Transforming execution trajectories into durable intelligence. Gated DPO preference pairs and procedural skill cards.
          </p>
        </div>

        <div className="badge-mono" style={{ padding: "6px 12px", background: "rgba(74, 222, 128, 0.1)", color: "var(--signal-proof)" }}>
          LOCAL MODEL DISTILLATION (7B/14B): READY
        </div>
      </div>

      {/* DPO Preference Pairs Table */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Chosen (Winner) Trajectory */}
        <div
          style={{
            background: "var(--bg-surface)",
            padding: 16,
            borderRadius: "var(--radius-md)",
            border: "1px solid rgba(74, 222, 128, 0.3)",
            display: "flex",
            flexDirection: "column",
            gap: 10,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontWeight: 700, fontSize: 12, color: "var(--signal-proof)" }}>
              CHOSEN TRAJECTORY (τ_chosen)
            </span>
            <span className="badge-mono" style={{ background: "rgba(74, 222, 128, 0.15)", color: "var(--signal-proof)" }}>
              VERDICT Y = 1 (PASSED)
            </span>
          </div>

          <div className="font-mono" style={{ fontSize: 11, color: "var(--text-secondary)" }}>
            <div>Run ID: <span style={{ color: "var(--text-primary)" }}>{selectedPair.chosenTrajectory.runId}</span></div>
            <div>Turns: <span style={{ color: "var(--signal-proof)" }}>{selectedPair.chosenTrajectory.turns}</span></div>
            <div>Tokens: <span style={{ color: "var(--text-primary)" }}>{selectedPair.chosenTrajectory.tokens}</span></div>
          </div>

          <div style={{ background: "var(--bg-panel)", padding: 10, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)", fontSize: 11, color: "var(--text-primary)" }}>
            {selectedPair.chosenTrajectory.strategySummary}
          </div>
        </div>

        {/* Rejected (Loser) Trajectory */}
        <div
          style={{
            background: "var(--bg-surface)",
            padding: 16,
            borderRadius: "var(--radius-md)",
            border: "1px solid rgba(248, 113, 113, 0.3)",
            display: "flex",
            flexDirection: "column",
            gap: 10,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontWeight: 700, fontSize: 12, color: "var(--signal-deny)" }}>
              REJECTED TRAJECTORY (τ_rejected)
            </span>
            <span className="badge-mono" style={{ background: "rgba(248, 113, 113, 0.15)", color: "var(--signal-deny)" }}>
              VERDICT Y = 0 (FAILED)
            </span>
          </div>

          <div className="font-mono" style={{ fontSize: 11, color: "var(--text-secondary)" }}>
            <div>Run ID: <span style={{ color: "var(--text-primary)" }}>{selectedPair.rejectedTrajectory.runId}</span></div>
            <div>Turns: <span style={{ color: "var(--signal-deny)" }}>{selectedPair.rejectedTrajectory.turns}</span></div>
            <div>Tokens: <span style={{ color: "var(--text-primary)" }}>{selectedPair.rejectedTrajectory.tokens}</span></div>
          </div>

          <div style={{ background: "var(--bg-panel)", padding: 10, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)", fontSize: 11, color: "var(--text-secondary)" }}>
            {selectedPair.rejectedTrajectory.failureReason}
          </div>
        </div>
      </div>

      {/* Extracted Procedural Skill Card & Statistical Gating */}
      <div
        style={{
          background: "var(--bg-surface)",
          padding: 16,
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-subtle)",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase" }}>
            Synthesized Procedural Skill Card
          </div>
          <div className="font-mono" style={{ fontWeight: 700, fontSize: 13, color: "var(--signal-flow)", marginTop: 2 }}>
            {selectedPair.extractedSkillName}
          </div>
        </div>

        <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase" }}>
              McNemar p-value
            </div>
            <div className="font-mono" style={{ fontSize: 12, fontWeight: 700, color: "var(--signal-proof)" }}>
              p = {selectedPair.mcnemarPValue} (&lt; 0.05)
            </div>
          </div>

          <div
            className="badge-mono"
            style={{
              padding: "6px 14px",
              background: "rgba(74, 222, 128, 0.15)",
              color: "var(--signal-proof)",
              fontWeight: 800,
            }}
          >
            {selectedPair.promotionStatus}
          </div>
        </div>
      </div>
    </div>
  );
};
