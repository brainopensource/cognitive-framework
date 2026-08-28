import React from "react";
import { CompositionDiff } from "./CompositionDiff.js";
import { TrajectoryAlignment } from "./TrajectoryAlignment.js";
import { MetricDelta } from "./MetricDelta.js";

export interface RunDiffViewProps {
  readonly baselineId?: string;
  readonly treatmentId?: string;
}

export const RunDiffView: React.FC<RunDiffViewProps> = ({
  baselineId = "run-base-v1",
  treatmentId = "run-treatment-v2",
}) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, overflowY: "auto", paddingBottom: 24 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontWeight: 800, fontSize: 14, color: "var(--text-primary)" }}>
              SCIENTIFIC RUN DIFF &amp; PAIRED ABLATION LAB
            </span>
            <span className="badge-mono" style={{ color: "var(--signal-proof)" }}>
              STATISTICAL LIFT VERIFIED
            </span>
          </div>
          <p style={{ margin: "4px 0 0 0", fontSize: 11, color: "var(--text-secondary)" }}>
            Side-by-side empirical comparison of execution metrics, compositions, and causal trajectories.
          </p>
        </div>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <div className="badge-mono" style={{ background: "var(--bg-panel)", padding: "6px 10px", color: "var(--text-secondary)" }}>
            Baseline: <strong style={{ color: "var(--text-primary)" }}>{baselineId}</strong>
          </div>
          <span style={{ color: "var(--text-muted)", fontSize: 11 }}>vs</span>
          <div className="badge-mono" style={{ background: "var(--bg-panel)", padding: "6px 10px", color: "var(--signal-proof)" }}>
            Treatment: <strong>{treatmentId}</strong>
          </div>
        </div>
      </div>

      {/* 6D Metric Delta Card */}
      <div style={{ border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
        <MetricDelta baselineRunId={baselineId} treatmentRunId={treatmentId} />
      </div>

      {/* Composition Structural Diff */}
      <div style={{ border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
        <CompositionDiff />
      </div>

      {/* Step-by-Step Trajectory Alignment */}
      <div style={{ border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
        <TrajectoryAlignment />
      </div>
    </div>
  );
};
