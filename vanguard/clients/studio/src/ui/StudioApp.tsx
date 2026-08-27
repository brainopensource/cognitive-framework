import React, { useEffect, useState } from "react";
import type { InternedRow } from "../store/event-store.js";
import type { StudioFold } from "../store/fold.js";
import type { StudioSessionState, StudioSurface } from "../store/session.js";
import { formatMicrosToUsd } from "../store/session.js";
import { EffectInspector } from "./EffectInspector.js";
import { ApprovalInterceptor } from "./ApprovalInterceptor.js";
import { TrajectoryWaterfall } from "./TrajectoryWaterfall.js";
import { EvidenceGrid } from "./EvidenceGrid.js";
import { LedgerExplorerView } from "./LedgerExplorerView.js";
import { SubstrateMapView } from "./SubstrateMapView.js";
import { MetaDevelopmentWorkbench } from "./MetaDevelopmentWorkbench.js";
import { CodingAgentWorkbench } from "./CodingAgentWorkbench.js";
import { GeneralityLabView } from "./GeneralityLabView.js";
import { LineageGraphView } from "./LineageGraphView.js";
import { EvolutionFoundryView } from "./EvolutionFoundryView.js";
import { VisualHarnessBuilder } from "./VisualHarnessBuilder.js";
import { ContextCompactionView } from "./ContextCompactionView.js";
import { FactorialExperimentView } from "./FactorialExperimentView.js";
import { TopologyEditor } from "./TopologyStudio/TopologyEditor.js";
import { SkillPipeline } from "./SkillLifecycle/SkillPipeline.js";
import { ContextExplorer } from "./ContextExplorer/ContextExplorer.js";
import { GovernanceView } from "./GovernanceView.js";
import { AgentCatalog } from "./AgentCatalog.js";
import { AgentBuilderWizard } from "./AgentBuilder/AgentBuilderWizard.js";
import { ObservatoryView } from "./Observatory/ObservatoryView.js";
import { RunDiffView } from "./RunDiff/RunDiffView.js";

export type StudioAppProps = {
  readonly fold: StudioFold;
  readonly rows: readonly InternedRow[];
  readonly session: StudioSessionState;
  readonly onSelectSurface: (surface: StudioSurface) => void;
  readonly onSelectSeq: (seq: bigint) => void;
  readonly onResolveApproval?: (approvalId: string, decision: "approve" | "reject") => Promise<void>;
  readonly latestSeq?: bigint;
};

type NavTab = {
  id: StudioSurface;
  label: string;
  icon: string;
  shortcut: string;
  desc: string;
};

const NAV_TABS: NavTab[] = [
  { id: "coding", label: "Coding IDE", icon: "💻", shortcut: "⌘1", desc: "Interactive Claude Code-style coding agent & surgical diffs" },
  { id: "builder", label: "Harness Builder", icon: "🛠️", shortcut: "⌘2", desc: "Visual agent composer & manifest generator (mhf.manifest/2)" },
  { id: "workbench", label: "Kernel Cockpit", icon: "🎛️", shortcut: "⌘3", desc: "M-1 to M-8 milestone stepper & S0-S12 reference monitor" },
  { id: "context", label: "Context & Cache", icon: "📑", shortcut: "⌘4", desc: "L1-L5 context stack, prompt prefix cache & compactor epochs" },
  { id: "lineage", label: "Lineage DAG", icon: "🌳", shortcut: "⌘5", desc: "Recursive agent.spawn tree & capability attenuation" },
  { id: "generality", label: "Generality Lab", icon: "🔬", shortcut: "⌘6", desc: "Multi-domain falsification benchmarks (Code vs Math vs Research)" },
  { id: "experiments", label: "A/B Experiments", icon: "📊", shortcut: "⌘7", desc: "Factorial trial matrix & McNemar statistical gating (p < 0.05)" },
  { id: "evolution", label: "Evolution Foundry", icon: "🧬", shortcut: "⌘8", desc: "DPO preference pairs (τ_win vs τ_lose) & skill card synthesizer" },
  { id: "ledger", label: "WAL Ledger", icon: "🗄️", shortcut: "⌘9", desc: "Single-writer SQLite WAL stream & deterministic state reduction" },
  { id: "theatre", label: "Turn Theatre", icon: "🎭", shortcut: "⌘0", desc: "Unary turn loop stream & event transcript" },
  { id: "evidence", label: "Evidence Grid", icon: "🛡️", shortcut: "⌥E", desc: "Cryptographic proof assertions & execution spans" },
  { id: "topology", label: "Topology Studio", icon: "🕸️", shortcut: "⌥T", desc: "Visual editor for mhf.topology/1 configurations" },
  { id: "skill", label: "Skill Lifecycle", icon: "🎓", shortcut: "⌥S", desc: "Gated self-improvement pipeline" },
  { id: "explorer", label: "Context Explorer", icon: "🔍", shortcut: "⌥C", desc: "Unified context and retrieved memory inspection" },
  { id: "governance", label: "Governance View", icon: "⚖️", shortcut: "⌥G", desc: "Governance audit log and policy compliance checks" },
  { id: "catalog", label: "Agent Catalog", icon: "📚", shortcut: "⌥A", desc: "Catalog of reusable agent skills and memory" },
  { id: "observatory", label: "Observatory", icon: "🔭", shortcut: "⌥O", desc: "Real-time stream and metric telemetry" },
  { id: "rundiff", label: "Run Diff", icon: "🔄", shortcut: "⌥R", desc: "Compare evaluation runs and benchmark deltas" },
];

export const StudioApp: React.FC<StudioAppProps> = ({
  fold,
  rows,
  session,
  onSelectSurface,
  onSelectSeq,
  onResolveApproval,
  latestSeq,
}) => {
  const [selectedEffectDesc, setSelectedEffectDesc] = useState<string | undefined>();
  const [selectedSpanId, setSelectedSpanId] = useState<string | undefined>();
  const [filterQuery, setFilterQuery] = useState<string>("");

  const activeEffect = selectedEffectDesc
    ? fold.effects.get(selectedEffectDesc)
    : fold.effects.size > 0
    ? Array.from(fold.effects.values())[fold.effects.size - 1]
    : undefined;

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) return;
      const surfaceByKey: Record<string, StudioSurface> = {
        "1": "coding",
        "2": "builder",
        "3": "workbench",
        "4": "context",
        "5": "lineage",
        "6": "generality",
        "7": "experiments",
        "8": "evolution",
        "9": "ledger",
        "0": "theatre",
      };
      const surface = surfaceByKey[event.key];
      if (surface) {
        event.preventDefault();
        onSelectSurface(surface);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [onSelectSurface]);

  const activeTabInfo = NAV_TABS.find((t) => t.id === session.activeSurface) || NAV_TABS[0];

  return (
    <div
      data-theme={session.theme}
      data-density={session.density}
      className="observatory-shell"
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        background: "var(--bg-canvas)",
        color: "var(--text-primary)",
        fontFamily: "var(--font-sans)",
        overflow: "hidden",
      }}
    >
      {/* Top Header / Breadcrumb & Status */}
      <header
        style={{
          height: 44,
          background: "var(--bg-surface)",
          borderBottom: "1px solid var(--border-subtle)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 16px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 22,
              height: 22,
              borderRadius: "var(--radius-sm)",
              background: "var(--text-primary)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 900,
              fontSize: 10,
              color: "#000",
            }}
          >
            Æ
          </div>
          <span style={{ fontWeight: 800, fontSize: 12, letterSpacing: "0.5px" }}>AETHER OBSERVATORY</span>
          <span style={{ fontSize: 10, color: "var(--text-muted)" }}>/</span>
          <span style={{ fontSize: 11, fontWeight: 700, color: "var(--signal-flow)" }}>
            {activeTabInfo.icon} {activeTabInfo.label}
          </span>
          <span className="badge-mono" style={{ color: "var(--text-muted)", fontSize: 9 }}>
            {fold.runId || "run-live-01"}
          </span>
        </div>

        {/* 6D Economic Tensor Telemetry */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div className="font-mono" style={{ fontSize: 10, color: "var(--text-secondary)" }}>
            Seq: <strong style={{ color: "var(--text-primary)" }}>{fold.atSeq.toString()}</strong>
          </div>
          <span style={{ fontSize: 10, color: "var(--text-faint)" }}>•</span>
          <div className="font-mono" style={{ fontSize: 10, color: "var(--signal-proof)" }}>
            USD: <strong>{formatMicrosToUsd(fold.totalCostMicros)}</strong>
          </div>
          <span style={{ fontSize: 10, color: "var(--text-faint)" }}>•</span>
          <div className="font-mono" style={{ fontSize: 10, color: "var(--text-secondary)" }}>
            Leases: <strong style={{ color: "var(--signal-flow)" }}>{fold.leases.size} active</strong>
          </div>
        </div>
      </header>

      {/* Main Body: Far-Left Icon Rail + Focused Viewport */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Far-Left Vertical Icon Navigation Rail */}
        <nav
          style={{
            width: 56,
            background: "var(--bg-surface)",
            borderRight: "1px solid var(--border-subtle)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            padding: "8px 0",
            gap: 6,
            zIndex: 10,
          }}
        >
          {NAV_TABS.map((tab) => {
            const isActive = session.activeSurface === tab.id;
            return (
              <button
                key={tab.id}
                title={`${tab.label} (${tab.shortcut})\n${tab.desc}`}
                onClick={() => onSelectSurface(tab.id)}
                style={{
                  width: 40,
                  height: 40,
                  borderRadius: "var(--radius-md)",
                  border: isActive ? "1px solid var(--signal-flow)" : "1px solid transparent",
                  background: isActive ? "var(--bg-card)" : "transparent",
                  color: isActive ? "var(--text-primary)" : "var(--text-muted)",
                  fontSize: 16,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: "pointer",
                  position: "relative",
                  transition: "all 0.15s ease",
                }}
              >
                <span>{tab.icon}</span>
                <span style={{ fontSize: 7, fontWeight: 700, color: isActive ? "var(--signal-flow)" : "var(--text-faint)", marginTop: -2 }}>
                  {tab.shortcut}
                </span>
              </button>
            );
          })}
        </nav>

        {/* Focused Single-Purpose Viewport (Square Canvas) */}
        <main style={{ flex: 1, display: "flex", overflow: "hidden", padding: 14 }}>
          {session.activeSurface === "coding" && (
            <CodingAgentWorkbench fold={fold} onResolveApproval={onResolveApproval} />
          )}

          {session.activeSurface === "builder" && <VisualHarnessBuilder fold={fold} />}

          {session.activeSurface === "workbench" && (
            <MetaDevelopmentWorkbench
              fold={fold}
              session={session}
              onSelectSurface={onSelectSurface}
              onResolveApproval={onResolveApproval}
            />
          )}

          {session.activeSurface === "context" && <ContextCompactionView fold={fold} />}

          {session.activeSurface === "lineage" && <LineageGraphView fold={fold} />}

          {session.activeSurface === "generality" && <GeneralityLabView fold={fold} />}

          {session.activeSurface === "experiments" && <FactorialExperimentView fold={fold} />}

          {session.activeSurface === "evolution" && <EvolutionFoundryView fold={fold} />}

          {session.activeSurface === "ledger" && (
            <LedgerExplorerView rows={rows} filterQuery={filterQuery} onFilterChange={setFilterQuery} />
          )}

          {session.activeSurface === "theatre" && (
            <div style={{ flex: 1, display: "grid", gridTemplateColumns: "260px 1fr 340px", gap: 12, overflow: "hidden" }}>
              {/* Turn Spine */}
              <div style={{ background: "var(--bg-surface)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", padding: 12, display: "flex", flexDirection: "column", gap: 8 }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
                  Turn Spine (Unary Loop)
                </div>
                <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
                  {fold.turns.length === 0 ? (
                    <div style={{ padding: 10, color: "var(--text-muted)", fontSize: 11 }}>Turn telemetry streaming...</div>
                  ) : (
                    fold.turns.map((turn) => (
                      <div key={turn.turnNumber} style={{ padding: 8, background: "var(--bg-card)", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)", fontSize: 11 }}>
                        <div style={{ display: "flex", justifyContent: "space-between" }}>
                          <span style={{ fontWeight: 700, color: "var(--signal-flow)" }}>Turn {turn.turnNumber}</span>
                          <span style={{ color: "var(--text-secondary)" }}>{turn.invocations.length} inv</span>
                        </div>
                        <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 4 }}>
                          Cost: {formatMicrosToUsd(turn.totalCostMicros)} • {turn.totalTokens} tok
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Event Transcript & Approvals */}
              <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 12, overflow: "hidden" }}>
                <ApprovalInterceptor pendingApproval={fold.pendingApproval} onResolve={onResolveApproval} />

                <div style={{ flex: 1, background: "var(--bg-surface)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", padding: 12, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
                    Causal Event Log ({rows.length} Events)
                  </div>

                  {rows.map((r) => {
                    const env = r.envelope;
                    const kind = String(env.payload?.kind ?? "unknown");
                    return (
                      <div
                        key={r.index}
                        onClick={() => {
                          onSelectSeq(r.seq);
                          if (env.payload?.descriptor) {
                            setSelectedEffectDesc(String(env.payload.descriptor));
                          }
                        }}
                        style={{
                          padding: "6px 8px",
                          background: r.seq === session.selectedSeq ? "var(--bg-card-hover)" : "var(--bg-panel)",
                          borderRadius: "var(--radius-sm)",
                          border: "1px solid var(--border-subtle)",
                          cursor: "pointer",
                          fontSize: 11,
                        }}
                      >
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 9, color: "var(--text-muted)" }}>
                          <span className="font-mono">seq {r.seq.toString()}</span>
                          <span>{new Date(r.occurredAtMs).toISOString().slice(11, 19)}</span>
                        </div>
                        <div style={{ fontWeight: 700, color: "var(--signal-flow)", marginTop: 2 }}>{kind}</div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Effect Inspector */}
              <div style={{ background: "var(--bg-surface)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", overflowY: "auto" }}>
                <EffectInspector effect={activeEffect} />
              </div>
            </div>
          )}

          {session.activeSurface === "evidence" && (
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 12, overflowY: "auto" }}>
              <EvidenceGrid rows={fold.evidenceRows} />
              <TrajectoryWaterfall spans={fold.spans} selectedSpanId={selectedSpanId} onSelectSpan={setSelectedSpanId} />
            </div>
          )}

          {session.activeSurface === "map" && <SubstrateMapView fold={fold} />}
          
          {session.activeSurface === "topology" && <TopologyEditor fold={fold} />}
          {session.activeSurface === "skill" && <SkillPipeline fold={fold} />}
          {session.activeSurface === "explorer" && <ContextExplorer fold={fold} />}
          {session.activeSurface === "governance" && <GovernanceView fold={fold} />}
          {session.activeSurface === "catalog" && <AgentCatalog />}
          {session.activeSurface === "observatory" && <ObservatoryView fold={fold} />}
          {session.activeSurface === "rundiff" && <RunDiffView baselineId="base" treatmentId="treat" />}
        </main>
      </div>

      {/* Bottom Causal WAL Scrubber Tape */}
      <footer
        style={{
          height: 34,
          background: "var(--bg-surface)",
          borderTop: "1px solid var(--border-subtle)",
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          gap: 12,
          fontSize: 10,
          fontFamily: "var(--font-mono)",
        }}
      >
        <span style={{ color: "var(--text-muted)" }}>CAUSAL WAL TAPE</span>
        <input
          type="range"
          min="1"
          max={Math.max(1, Number(latestSeq ?? fold.atSeq)).toString()}
          value={session.selectedSeq.toString() || "1"}
          onChange={(e) => onSelectSeq(BigInt(e.target.value))}
          style={{ flex: 1, cursor: "pointer" }}
        />
        <span style={{ color: "var(--signal-flow)", fontWeight: 700 }}>
          {session.selectedSeq === 0n || session.selectedSeq >= (latestSeq ?? fold.atSeq) ? "● LIVE HEAD" : `⧗ seq ${session.selectedSeq}`}
        </span>
      </footer>
    </div>
  );
};
