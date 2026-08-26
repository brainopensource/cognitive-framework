import React, { useEffect, useState } from "react";
import type { InternedRow } from "../store/event-store.js";
import type { StudioFold } from "../store/fold.js";
import type { StudioSessionState, StudioSurface } from "../store/session.js";
import { formatMicrosToUsd, formatDigestShort } from "../store/session.js";
import { EffectInspector } from "./EffectInspector.js";
import { ApprovalInterceptor } from "./ApprovalInterceptor.js";
import { TrajectoryWaterfall } from "./TrajectoryWaterfall.js";
import { EvidenceGrid } from "./EvidenceGrid.js";
import { CompositionStudioView } from "./CompositionStudioView.js";
import { ArenaView } from "./ArenaView.js";
import { AutonomyWatchView } from "./AutonomyWatchView.js";
import { LedgerExplorerView } from "./LedgerExplorerView.js";
import { SubstrateMapView } from "./SubstrateMapView.js";
import { MetaDevelopmentWorkbench } from "./MetaDevelopmentWorkbench.js";
import { CodingAgentWorkbench } from "./CodingAgentWorkbench.js";
import { GeneralityLabView } from "./GeneralityLabView.js";
import { LineageGraphView } from "./LineageGraphView.js";
import { EvolutionFoundryView } from "./EvolutionFoundryView.js";

export type StudioAppProps = {
  readonly fold: StudioFold;
  readonly rows: readonly InternedRow[];
  readonly session: StudioSessionState;
  readonly onSelectSurface: (surface: StudioSurface) => void;
  readonly onSelectSeq: (seq: bigint) => void;
  readonly onResolveApproval?: (approvalId: string, decision: "approve" | "reject") => Promise<void>;
  readonly latestSeq?: bigint;
};

const NAV_ITEMS: { id: StudioSurface; label: string; shortcut: string }[] = [
  { id: "workbench", label: "Meta Workbench", shortcut: "⌘1" },
  { id: "coding", label: "Coding IDE", shortcut: "⌘2" },
  { id: "generality", label: "Generality Lab", shortcut: "⌘3" },
  { id: "lineage", label: "Lineage DAG", shortcut: "⌘4" },
  { id: "evolution", label: "Evolution Foundry", shortcut: "⌘5" },
  { id: "theatre", label: "Turn Theatre", shortcut: "⌘6" },
  { id: "evidence", label: "Evidence Grid", shortcut: "⌘7" },
  { id: "ledger", label: "WAL Ledger", shortcut: "⌘8" },
  { id: "map", label: "Substrate Map", shortcut: "⌘9" },
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
        "1": "workbench",
        "2": "coding",
        "3": "generality",
        "4": "lineage",
        "5": "evolution",
        "6": "theatre",
        "7": "evidence",
        "8": "ledger",
        "9": "map",
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
      {/* Top Header / Status Bar */}
      <header
        style={{
          height: 48,
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
              width: 24,
              height: 24,
              borderRadius: "var(--radius-sm)",
              background: "var(--text-primary)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: 900,
              fontSize: 11,
              color: "#000",
            }}
          >
            Æ
          </div>
          <span style={{ fontWeight: 800, fontSize: 12, letterSpacing: "0.5px" }}>AETHER OBSERVATORY</span>
          <span className="badge-mono" style={{ color: "var(--signal-flow)" }}>
            {fold.runId || "run-meta-dev-01"}
          </span>
          <span style={{ fontSize: 10, color: "var(--text-muted)" }}>•</span>
          <span className="font-mono" style={{ fontSize: 10, color: "var(--text-secondary)" }}>
            Seq: {fold.atSeq.toString()}
          </span>
          <span style={{ fontSize: 10, color: "var(--text-muted)" }}>•</span>
          <span className="font-mono" style={{ fontSize: 10, color: "var(--signal-proof)" }}>
            USD: {formatMicrosToUsd(fold.totalCostMicros)}
          </span>
        </div>

        {/* Surface Navigation Strip */}
        <nav
          style={{
            display: "flex",
            gap: 2,
            background: "var(--bg-panel)",
            padding: 3,
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-subtle)",
          }}
        >
          {NAV_ITEMS.map((item) => {
            const isActive = session.activeSurface === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectSurface(item.id)}
                style={{
                  padding: "4px 8px",
                  background: isActive ? "var(--bg-card)" : "transparent",
                  color: isActive ? "var(--text-primary)" : "var(--text-muted)",
                  border: isActive ? "1px solid var(--border-subtle)" : "1px solid transparent",
                  borderRadius: "var(--radius-sm)",
                  fontSize: 11,
                  fontWeight: isActive ? 700 : 500,
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: 4,
                }}
              >
                <span>{item.label}</span>
                <span style={{ fontSize: 9, color: "var(--text-faint)" }}>{item.shortcut}</span>
              </button>
            );
          })}
        </nav>
      </header>

      {/* Main Surface Viewport */}
      <main style={{ flex: 1, display: "flex", overflow: "hidden", padding: 14 }}>
        {session.activeSurface === "workbench" && (
          <MetaDevelopmentWorkbench
            fold={fold}
            session={session}
            onSelectSurface={onSelectSurface}
            onResolveApproval={onResolveApproval}
          />
        )}

        {session.activeSurface === "coding" && (
          <CodingAgentWorkbench fold={fold} onResolveApproval={onResolveApproval} />
        )}

        {session.activeSurface === "generality" && <GeneralityLabView fold={fold} />}

        {session.activeSurface === "lineage" && <LineageGraphView fold={fold} />}

        {session.activeSurface === "evolution" && <EvolutionFoundryView fold={fold} />}

        {session.activeSurface === "theatre" && (
          <div style={{ flex: 1, display: "grid", gridTemplateColumns: "240px 1fr 320px", gap: 12, overflow: "hidden" }}>
            {/* Left: Turn Spine */}
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

            {/* Center: Live Transcript & Approvals */}
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

            {/* Right: Effect Inspector */}
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

        {session.activeSurface === "ledger" && (
          <LedgerExplorerView rows={rows} filterQuery={filterQuery} onFilterChange={setFilterQuery} />
        )}

        {session.activeSurface === "map" && <SubstrateMapView fold={fold} />}
        {session.activeSurface === "studio" && <CompositionStudioView fold={fold} />}
        {session.activeSurface === "effect" && (
          <div style={{ flex: 1, background: "var(--bg-surface)", border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-md)", padding: 16 }}>
            <EffectInspector effect={activeEffect} />
          </div>
        )}
        {session.activeSurface === "arena" && <ArenaView fold={fold} />}
        {session.activeSurface === "watch" && <AutonomyWatchView fold={fold} />}
      </main>

      {/* Bottom Ledger Tape */}
      <footer
        style={{
          height: 36,
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
