import React, { useState } from "react";
import type { StudioFold } from "../store/fold.js";
import { formatDigestShort, formatMicrosToUsd } from "../store/session.js";

type LineageNode = {
  lineageId: string;
  parentLineageId?: string;
  role: string;
  goal: string;
  depth: number;
  status: "running" | "completed" | "interrupted" | "escalated" | "recovery" | "orphan";
  budgetAllocated: { tokens: number; usdMicros: number };
  budgetConsumed: { tokens: number; usdMicros: number };
  allowedActions: string[];
  outputArtifactRef?: string;
};

const DEMO_LINEAGES: LineageNode[] = [
  {
    lineageId: "lin_root_001",
    role: "Root Orchestrator / Principal",
    goal: "Diagnose and fix distributed consensus test failure",
    depth: 0,
    status: "running",
    budgetAllocated: { tokens: 10000, usdMicros: 2000000 },
    budgetConsumed: { tokens: 4120, usdMicros: 824000 },
    allowedActions: ["fs.read", "fs.patch", "proc.exec", "agent.spawn", "git.status"],
  },
  {
    lineageId: "lin_child_investigator",
    parentLineageId: "lin_root_001",
    role: "Child Investigator (Attenuated)",
    goal: "Isolate flake in test_quorum_election via log analysis",
    depth: 1,
    status: "completed",
    budgetAllocated: { tokens: 3000, usdMicros: 600000 },
    budgetConsumed: { tokens: 1840, usdMicros: 368000 },
    allowedActions: ["fs.read", "proc.exec"], // strictly attenuated (no patch, no spawn)
    outputArtifactRef: "sha256:art_investigation_summary_88c9",
  },
  {
    lineageId: "lin_child_solver",
    parentLineageId: "lin_root_001",
    role: "Child Solver / Surgical Patcher",
    goal: "Generate unified diff for election timeout backoff",
    depth: 1,
    status: "running",
    budgetAllocated: { tokens: 3000, usdMicros: 600000 },
    budgetConsumed: { tokens: 1280, usdMicros: 256000 },
    allowedActions: ["fs.read", "fs.patch"], // strictly attenuated (no spawn)
  },
];

export const LineageGraphView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => {
  const [selectedLineage, setSelectedLineage] = useState<LineageNode>(DEMO_LINEAGES[1]);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontWeight: 700, fontSize: 13, color: "var(--text-primary)" }}>
              M-6 RECURSIVE LINEAGE DAG (agent.spawn)
            </span>
            <span className="badge-mono" style={{ color: "var(--signal-flow)" }}>
              MONOTONIC CAPABILITY ATTENUATION
            </span>
          </div>
          <p style={{ margin: "4px 0 0 0", fontSize: 11, color: "var(--text-secondary)" }}>
            Nested causal scopes. Child lineages inherit strictly sub-attenuated capability grants and conserved budgets.
          </p>
        </div>

        <div className="badge-mono" style={{ padding: "6px 12px", background: "rgba(56, 189, 248, 0.1)", color: "var(--signal-flow)" }}>
          ACTIVE LINEAGES: 3 (DEPTH MAX: 2)
        </div>
      </div>

      {/* Lineage Tree Visualization */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 16 }}>
        {/* Visual DAG Nodes */}
        <div
          style={{
            background: "var(--bg-surface)",
            padding: 16,
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-subtle)",
            display: "flex",
            flexDirection: "column",
            gap: 16,
          }}
        >
          {DEMO_LINEAGES.map((node) => {
            const isSelected = node.lineageId === selectedLineage.lineageId;
            const isChild = !!node.parentLineageId;

            return (
              <div
                key={node.lineageId}
                style={{
                  marginLeft: node.depth * 32,
                  position: "relative",
                }}
              >
                {isChild && (
                  <div
                    style={{
                      position: "absolute",
                      left: -20,
                      top: 18,
                      width: 16,
                      height: 2,
                      background: "var(--border-medium)",
                    }}
                  />
                )}
                <button
                  onClick={() => setSelectedLineage(node)}
                  style={{
                    width: "100%",
                    background: isSelected ? "var(--bg-card)" : "var(--bg-panel)",
                    border: isSelected ? "1px solid var(--signal-flow)" : "1px solid var(--border-subtle)",
                    borderRadius: "var(--radius-md)",
                    padding: 12,
                    textAlign: "left",
                    cursor: "pointer",
                    display: "flex",
                    flexDirection: "column",
                    gap: 6,
                    boxShadow: isSelected ? "var(--shadow-glow)" : "none",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <span className="font-mono" style={{ fontSize: 11, fontWeight: 700, color: "var(--signal-flow)" }}>
                        {node.lineageId}
                      </span>
                      <span className="badge-mono">Depth {node.depth}</span>
                    </div>
                    <span
                      className="badge-mono"
                      style={{
                        color: node.status === "completed" ? "var(--signal-proof)" : "var(--signal-flow)",
                      }}
                    >
                      {node.status.toUpperCase()}
                    </span>
                  </div>

                  <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)" }}>
                    {node.role}
                  </div>
                  <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>
                    {node.goal}
                  </div>

                  {/* Budget Bar */}
                  <div style={{ marginTop: 4, display: "flex", justifyContent: "space-between", fontSize: 10, color: "var(--text-muted)" }}>
                    <span>Tokens: {node.budgetConsumed.tokens} / {node.budgetAllocated.tokens}</span>
                    <span>Cost: {formatMicrosToUsd(node.budgetConsumed.usdMicros)}</span>
                  </div>
                </button>
              </div>
            );
          })}
        </div>

        {/* Selected Lineage Authority Inspector */}
        <div
          style={{
            background: "var(--bg-surface)",
            padding: 16,
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-subtle)",
            display: "flex",
            flexDirection: "column",
            gap: 12,
          }}
        >
          <div style={{ fontWeight: 700, fontSize: 12, color: "var(--text-primary)" }}>
            Attenuated Scope Inspector
          </div>

          <div className="font-mono" style={{ fontSize: 11, color: "var(--text-secondary)" }}>
            <div>Lineage: <span style={{ color: "var(--signal-flow)" }}>{selectedLineage.lineageId}</span></div>
            <div>Parent: <span style={{ color: "var(--text-primary)" }}>{selectedLineage.parentLineageId || "NONE (ROOT)"}</span></div>
          </div>

          <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: 8 }}>
            <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 6 }}>
              Budget Waterfall (Parent -&gt; Child Conservation)
            </div>
            <div style={{ fontSize: 11, color: "var(--text-secondary)", marginBottom: 4 }}>
              Allocated: {selectedLineage.budgetAllocated.tokens} tokens
            </div>
            <div style={{ width: "100%", background: "var(--bg-panel)", height: 8, borderRadius: 4, overflow: "hidden" }}>
               <div style={{ width: `${Math.min(100, (selectedLineage.budgetConsumed.tokens / selectedLineage.budgetAllocated.tokens) * 100)}%`, background: "var(--signal-flow)", height: "100%" }} />
            </div>
            <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 4 }}>
              Consumed: {selectedLineage.budgetConsumed.tokens} tokens
            </div>
          </div>

          <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: 8 }}>
            <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 6 }}>
              Sealed Action Membership
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {selectedLineage.allowedActions.map((act) => (
                <span key={act} className="badge-mono" style={{ color: "var(--signal-proof)" }}>
                  {act}
                </span>
              ))}
            </div>
          </div>

          {selectedLineage.outputArtifactRef && (
             <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: 8 }}>
               <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 4 }}>
                 Parent-Child Artifact Flow Edge
               </div>
               <div className="font-mono" style={{ fontSize: 10, color: "var(--signal-flow)", background: "var(--bg-panel)", padding: 6, borderRadius: "var(--radius-sm)", display: "flex", alignItems: "center", gap: 8 }}>
                 <span>↑ Returns to Parent:</span>
                 {selectedLineage.outputArtifactRef}
               </div>
             </div>
          )}
        </div>
      </div>
    </div>
  );
};
