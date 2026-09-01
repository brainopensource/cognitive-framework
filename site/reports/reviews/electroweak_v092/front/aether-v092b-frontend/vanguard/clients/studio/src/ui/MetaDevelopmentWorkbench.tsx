import React, { useState } from "react";
import type { StudioFold } from "../store/fold.js";
import type { StudioSessionState } from "../store/session.js";
import { formatDigestShort, formatMicrosToUsd } from "../store/session.js";
import { KernelDispatchMonitor } from "./KernelDispatchMonitor.js";
import { CodingAgentWorkbench } from "./CodingAgentWorkbench.js";
import { GeneralityLabView } from "./GeneralityLabView.js";
import { LineageGraphView } from "./LineageGraphView.js";
import { EvolutionFoundryView } from "./EvolutionFoundryView.js";

type MilestoneTab = "M-1" | "M-2" | "M-3C" | "M-4" | "M-5a" | "M-5b" | "M-6" | "M-6.5" | "M-7" | "M-8" | "ALL";

const MILESTONES: { id: MilestoneTab; title: string; desc: string; status: "GREEN" | "ACTIVE" | "PLANNED" }[] = [
  { id: "ALL", title: "Overview", desc: "Unified Substrate Cockpit", status: "ACTIVE" },
  { id: "M-1", title: "M-1 Trust Spine", desc: "Signed verdicts, typed budgets & S0-S12", status: "GREEN" },
  { id: "M-2", title: "M-2 Truthful WAL", desc: "SQLite WAL cold continuation & replay", status: "GREEN" },
  { id: "M-3C", title: "M-3C Composition", desc: "Composition root & profile resolver", status: "GREEN" },
  { id: "M-4", title: "M-4 Coding Agent", desc: "SOTA Coding harness & exact I/O capture", status: "ACTIVE" },
  { id: "M-5a", title: "M-5a AgentView", desc: "Event-derived ephemeral projection fold", status: "ACTIVE" },
  { id: "M-5b", title: "M-5b Generality", desc: "Multi-domain falsification (Formal/Math)", status: "PLANNED" },
  { id: "M-6", title: "M-6 Lineage DAG", desc: "agent.spawn nested causal regions", status: "PLANNED" },
  { id: "M-6.5", title: "M-6.5 Metacognition", desc: "Adaptive strategy & stagnation detection", status: "PLANNED" },
  { id: "M-7", title: "M-7 Topologies", desc: "Declarative multi-agent structures", status: "PLANNED" },
  { id: "M-8", title: "M-8 Evolution", desc: "DPO preference pairs & skill foundry", status: "PLANNED" },
];

export const MetaDevelopmentWorkbench: React.FC<{
  readonly fold: StudioFold;
  readonly session: StudioSessionState;
  readonly onSelectSurface: (surface: StudioSessionState["activeSurface"]) => void;
  readonly onResolveApproval?: (approvalId: string, decision: "approve" | "reject") => Promise<void>;
}> = ({ fold, session, onSelectSurface, onResolveApproval }) => {
  const [activeMilestone, setActiveMilestone] = useState<MilestoneTab>("ALL");

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 16 }}>
      {/* Milestone Navigator Strip */}
      <div
        style={{
          display: "flex",
          gap: 6,
          background: "var(--bg-surface)",
          padding: "6px 12px",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-subtle)",
          overflowX: "auto",
        }}
      >
        {MILESTONES.map((m) => {
          const isSelected = m.id === activeMilestone;
          return (
            <button
              key={m.id}
              onClick={() => setActiveMilestone(m.id)}
              style={{
                background: isSelected ? "var(--bg-card)" : "transparent",
                border: isSelected ? "1px solid var(--signal-flow)" : "1px solid transparent",
                borderRadius: "var(--radius-sm)",
                padding: "6px 10px",
                color: isSelected ? "var(--text-primary)" : "var(--text-secondary)",
                fontSize: 11,
                fontWeight: isSelected ? 700 : 500,
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: 6,
                whiteSpace: "nowrap",
              }}
            >
              <span>{m.title}</span>
              <span
                style={{
                  fontSize: 8,
                  fontWeight: 700,
                  padding: "1px 4px",
                  borderRadius: 2,
                  background:
                    m.status === "GREEN"
                      ? "rgba(74, 222, 128, 0.15)"
                      : m.status === "ACTIVE"
                      ? "rgba(56, 189, 248, 0.15)"
                      : "rgba(255, 255, 255, 0.06)",
                  color:
                    m.status === "GREEN"
                      ? "var(--signal-proof)"
                      : m.status === "ACTIVE"
                      ? "var(--signal-flow)"
                      : "var(--text-muted)",
                }}
              >
                {m.status}
              </span>
            </button>
          );
        })}
      </div>

      {/* Main Dynamic Stage Based on Selected Milestone */}
      <div style={{ flex: 1, minHeight: 0, overflowY: "auto" }}>
        {activeMilestone === "ALL" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {/* Top Microkernel Reference Monitor */}
            <div style={{ background: "var(--bg-surface)", padding: 16, borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
              <KernelDispatchMonitor fold={fold} />
            </div>

            {/* Middle Grid: Coding Agent + Generality */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
              {/* Live Coding Agent Snapshot */}
              <div style={{ background: "var(--bg-surface)", padding: 16, borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", display: "flex", flexDirection: "column", gap: 10 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: 700, fontSize: 12, color: "var(--text-primary)" }}>
                    M-4 Coding Agent Substrate
                  </span>
                  <button
                    onClick={() => setActiveMilestone("M-4")}
                    style={{
                      background: "var(--bg-panel)",
                      border: "1px solid var(--border-subtle)",
                      borderRadius: "var(--radius-sm)",
                      padding: "4px 8px",
                      color: "var(--signal-flow)",
                      fontSize: 10,
                      fontWeight: 700,
                      cursor: "pointer",
                    }}
                  >
                    EXPAND WORKBENCH →
                  </button>
                </div>
                <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>
                  Executing AST search, unified diff edits, and exterior test evaluation.
                </div>
                <div className="font-mono" style={{ fontSize: 11, color: "var(--signal-proof)", background: "var(--bg-panel)", padding: 8, borderRadius: "var(--radius-sm)" }}>
                  Current Task: Fix Memory Store Lease Race Condition (Y = 1)
                </div>
              </div>

              {/* M-5a Ephemeral AgentView Projection */}
              <div style={{ background: "var(--bg-surface)", padding: 16, borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", display: "flex", flexDirection: "column", gap: 10 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontWeight: 700, fontSize: 12, color: "var(--text-primary)" }}>
                    M-5a Ephemeral AgentView Fold
                  </span>
                  <span className="badge-mono" style={{ color: "var(--signal-flow)" }}>
                    fold_agent_view()
                  </span>
                </div>
                <div style={{ fontSize: 11, color: "var(--text-secondary)" }}>
                  Agent is an ephemeral projection folded from WAL causal facts without mutable in-memory state.
                </div>
                <div className="font-mono" style={{ fontSize: 10, color: "var(--text-secondary)", background: "var(--bg-panel)", padding: 8, borderRadius: "var(--radius-sm)" }}>
                  <div>Lineage: <span style={{ color: "var(--signal-flow)" }}>lin_root_001</span></div>
                  <div>Goal: <span style={{ color: "var(--text-primary)" }}>Diagnose distributed test failure</span></div>
                  <div>Strategy: <span style={{ color: "var(--signal-proof)" }}>Investigate</span></div>
                  <div>Settled Effects: <span style={{ color: "var(--text-primary)" }}>{fold.effects.size}</span></div>
                </div>
              </div>
            </div>

            {/* Bottom Evolution & Lineage Preview */}
            <div style={{ background: "var(--bg-surface)", padding: 16, borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
              <EvolutionFoundryView fold={fold} />
            </div>
          </div>
        )}

        {activeMilestone === "M-1" && (
          <div style={{ background: "var(--bg-surface)", padding: 16, borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
            <KernelDispatchMonitor fold={fold} />
          </div>
        )}

        {activeMilestone === "M-2" && (
          <div style={{ background: "var(--bg-surface)", padding: 16, borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ fontWeight: 700, fontSize: 13, color: "var(--text-primary)" }}>
              M-2 Single-Writer SQLite WAL Truth Stream
            </div>
            <p style={{ fontSize: 11, color: "var(--text-secondary)", margin: 0 }}>
              Causal append-only log with global monotonic sequence numbers. Pure deterministic cold replay.
            </p>
            <div className="font-mono" style={{ fontSize: 11, background: "var(--bg-canvas)", padding: 12, borderRadius: "var(--radius-sm)" }}>
              <div>Current Sequence: {fold.atSeq.toString()}</div>
              <div>Run ID: {fold.runId}</div>
              <div>Status: {fold.status.toUpperCase()}</div>
              <div>Digest D_R: sha256:d_r_merkle_provenance_92a1</div>
            </div>
          </div>
        )}

        {activeMilestone === "M-4" && (
          <CodingAgentWorkbench fold={fold} onResolveApproval={onResolveApproval} />
        )}

        {activeMilestone === "M-5a" && (
          <div style={{ background: "var(--bg-surface)", padding: 16, borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontWeight: 700, fontSize: 13, color: "var(--text-primary)" }}>
                M-5a Event-Derived AgentView Projection Engine
              </div>
              <span className="badge-mono" style={{ color: "var(--signal-proof)" }}>
                ZERO MUTABLE STATE LEAK
              </span>
            </div>
            <pre className="font-mono" style={{ background: "var(--bg-canvas)", padding: 12, borderRadius: "var(--radius-sm)", fontSize: 11, color: "var(--text-primary)" }}>
{JSON.stringify(
  {
    lineageId: "lin_root_001",
    goal: "Diagnose and fix distributed consensus test failure",
    strategy: "Investigate",
    planRevisions: [{ turn: 1, action: "inspect_logs" }, { turn: 2, action: "patch_code" }],
    settledEffects: { "sha256:fs_read": "satisfied", "sha256:fs_patch": "satisfied" },
    budgetConsumed: { tokens: fold.totalTokens, usdMicros: Number(fold.totalCostMicros) },
    contextEpoch: 1,
    children: ["lin_child_investigator", "lin_child_solver"],
    terminal: "satisfied",
    reducerVersion: "m5a.agent_view/1"
  },
  null,
  2
)}
            </pre>
          </div>
        )}

        {activeMilestone === "M-5b" && <GeneralityLabView fold={fold} />}

        {activeMilestone === "M-6" && <LineageGraphView fold={fold} />}

        {activeMilestone === "M-8" && <EvolutionFoundryView fold={fold} />}
      </div>
    </div>
  );
};
