/**
 * AUTO-GENERATED: Observatory Causal Graph View
 */
import React, { useState, useMemo } from "react";
import type { GraphNode, GraphEdge } from "@vanguard/client-core/application/graph-model.js";

export interface CausalGraphViewProps {
  readonly nodes: readonly GraphNode[];
  readonly edges: readonly GraphEdge[];
}

type ZoomLevel = "Run" | "Lineage" | "Event";

export const CausalGraphView: React.FC<CausalGraphViewProps> = ({ nodes, edges }) => {
  const [zoom, setZoom] = useState<ZoomLevel>("Run");

  const getNodeStyle = (semanticClass: string): React.CSSProperties => {
    switch (semanticClass) {
      case "fact": return { border: "2px solid var(--signal-proof)", background: "var(--bg-card)" };
      case "projection": return { border: "1px dashed var(--signal-void)", background: "var(--bg-surface)" };
      case "telemetry": return { border: "1px dotted var(--text-muted)", background: "transparent" };
      case "draft": return { border: "1px solid var(--border-subtle)", background: "var(--bg-panel)" };
      default: return { border: "1px solid var(--border-medium)", background: "var(--bg-card)" };
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", width: "100%", background: "var(--bg-canvas)", color: "var(--text-primary)", padding: "16px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <h2>Causal Graph</h2>
        <div>
          <select value={zoom} onChange={(e) => setZoom(e.target.value as ZoomLevel)}>
            <option value="Run">Run Level</option>
            <option value="Lineage">Lineage Level</option>
            <option value="Event">Event Level</option>
          </select>
        </div>
      </div>

      <div style={{ flex: 1, position: "relative", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", overflow: "auto" }}>
        {nodes.map(n => (
          <div key={n.id} style={{
            ...getNodeStyle(n.semanticClass),
            margin: "8px",
            padding: "8px",
            borderRadius: "var(--radius-sm)",
            display: "inline-block"
          }}>
            <div style={{ fontWeight: "bold" }}>{n.label}</div>
            <div style={{ fontSize: "10px", color: "var(--text-secondary)" }}>{n.kind} ({n.status})</div>
          </div>
        ))}

        <div style={{ marginTop: "16px", padding: "8px" }}>
          <h4>Edges (Relations)</h4>
          <ul>
            {edges.map(e => (
              <li key={e.id} style={{ fontSize: "12px" }}>
                {e.source} <span style={{ color: "var(--signal-flow)" }}>--[{e.relation}]--&gt;</span> {e.target}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
