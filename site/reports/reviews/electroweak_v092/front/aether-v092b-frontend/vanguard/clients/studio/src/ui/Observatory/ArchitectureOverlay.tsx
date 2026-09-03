/**
 * AUTO-GENERATED: Observatory Architecture Overlay
 */
import React from "react";
import type { GraphNode, GraphEdge } from "@vanguard/client-core/application/graph-model.js";

export interface ArchitectureOverlayProps {
  readonly nodes: readonly GraphNode[];
  readonly edges: readonly GraphEdge[];
  readonly activeComponentIds: readonly string[];
}

export const ArchitectureOverlay: React.FC<ArchitectureOverlayProps> = ({ nodes, edges, activeComponentIds }) => {
  return (
    <div style={{ padding: "16px", background: "var(--bg-canvas)", color: "var(--text-primary)", display: "flex", flexDirection: "column", height: "100%" }}>
      <h2>Architecture Overlay</h2>
      <p style={{ color: "var(--text-muted)", fontSize: "14px" }}>
        Component dependency view (Domain, Ports, Kernel, Agency, Runtime, Adapters, Packs, Plugins, Clients).
      </p>

      <div style={{ flex: 1, position: "relative", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", overflow: "auto", padding: "16px", background: "var(--bg-surface)" }}>
        {nodes.map(n => {
          const isActive = activeComponentIds.includes(n.id);
          return (
            <div key={n.id} style={{
              border: isActive ? "2px solid var(--signal-flow)" : "1px solid var(--border-medium)",
              background: isActive ? "var(--bg-card-hover)" : "var(--bg-card)",
              boxShadow: isActive ? "var(--shadow-glow)" : "none",
              margin: "8px",
              padding: "12px",
              borderRadius: "var(--radius-sm)",
              display: "inline-block",
              opacity: isActive ? 1 : 0.6
            }}>
              <div style={{ fontWeight: "bold" }}>{n.label}</div>
              <div style={{ fontSize: "10px", color: "var(--text-secondary)" }}>{n.kind}</div>
            </div>
          );
        })}

        <div style={{ marginTop: "24px", padding: "12px", borderTop: "1px solid var(--border-subtle)" }}>
          <h4>Dependencies</h4>
          <ul>
            {edges.map(e => (
              <li key={e.id} style={{ fontSize: "12px", color: "var(--text-secondary)" }}>
                {e.source} <span style={{ color: "var(--text-muted)" }}>--&gt;</span> {e.target} ({e.relation})
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
