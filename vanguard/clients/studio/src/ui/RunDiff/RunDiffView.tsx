/**
 * AUTO-GENERATED: RunDiff View
 */
import React from "react";
import { CompositionDiff } from "./CompositionDiff.js";
import { TrajectoryAlignment } from "./TrajectoryAlignment.js";
import { MetricDelta } from "./MetricDelta.js";

export interface RunDiffViewProps {
  readonly baselineId: string;
  readonly treatmentId: string;
}

export const RunDiffView: React.FC<RunDiffViewProps> = ({ baselineId, treatmentId }) => {
  return (
    <div style={{ padding: "16px", background: "var(--bg-canvas)", color: "var(--text-primary)", display: "flex", flexDirection: "column", gap: "24px" }}>
      <h2>Run Diff</h2>
      <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
        <div style={{ padding: "8px", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", background: "var(--bg-panel)" }}>
          Baseline: <strong>{baselineId}</strong>
        </div>
        <span>vs</span>
        <div style={{ padding: "8px", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-sm)", background: "var(--bg-panel)" }}>
          Treatment: <strong>{treatmentId}</strong>
        </div>
      </div>
      
      <div style={{ border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
        <MetricDelta />
      </div>

      <div style={{ border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
        <CompositionDiff />
      </div>

      <div style={{ border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", overflow: "hidden" }}>
        <TrajectoryAlignment />
      </div>
    </div>
  );
};
