import React, { useEffect, useState } from "react";
import type { InternedRow } from "../store/event-store.js";
import type { StudioFold } from "../store/fold.js";
import type { StudioSessionState } from "../store/session.js";
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

export type StudioAppProps = {
  readonly fold: StudioFold;
  readonly rows: readonly InternedRow[];
  readonly session: StudioSessionState;
  readonly onSelectSurface: (surface: StudioSessionState["activeSurface"]) => void;
  readonly onSelectSeq: (seq: bigint) => void;
  readonly onResolveApproval?: (approvalId: string, decision: "approve" | "reject") => Promise<void>;
  readonly latestSeq?: bigint;
};

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
      const surfaceByKey: Record<string, StudioSessionState["activeSurface"]> = {
        "1": "theatre", "2": "map", "3": "studio", "4": "effect", "5": "evidence", "6": "arena", "7": "ledger", "8": "watch",
      };
      const surface = surfaceByKey[event.key];
      if (surface) { event.preventDefault(); onSelectSurface(surface); }
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
      {/* Top Header / Run Bar */}
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
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 6,
              background: "linear-gradient(135deg, #00d2ff, #3b82f6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontWeight: "bold",
              fontSize: 12,
              color: "#000",
            }}
          >
            VG
          </div>
          <span style={{ fontWeight: "bold", fontSize: 13, letterSpacing: "0.5px" }}>AETHER OBSERVATORY</span>
          <span
            style={{
              fontSize: 11,
              fontFamily: "var(--font-mono)",
              background: "var(--bg-panel)",
              padding: "2px 8px",
              borderRadius: 4,
              border: "1px solid var(--border-subtle)",
              color: "var(--signal-flow)",
            }}
          >
            {fold.runId || "run-code-default"}
          </span>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>•</span>
          <span style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--text-secondary)" }}>
            Seq: {fold.atSeq.toString()}
          </span>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>•</span>
          <span style={{ fontSize: 11, fontFamily: "var(--font-mono)", color: "var(--signal-proof)" }}>
            Cost: {formatMicrosToUsd(fold.totalCostMicros)}
          </span>
        </div>

        {/* Surface Navigation Bar (⌘1–⌘9) */}
        <nav style={{ display: "flex", gap: 4, background: "var(--bg-panel)", padding: 3, borderRadius: 6, border: "1px solid var(--border-subtle)" }}>
          <button
            onClick={() => onSelectSurface("theatre")}
            style={{
              padding: "4px 8px",
              background: session.activeSurface === "theatre" ? "var(--bg-card)" : "transparent",
              color: session.activeSurface === "theatre" ? "var(--signal-flow)" : "var(--text-secondary)",
              border: "none",
              borderRadius: 4,
              fontSize: 11,
              fontWeight: "500",
              cursor: "pointer",
            }}
          >
            ⌘1 Theatre
          </button>
          <button
            onClick={() => onSelectSurface("map")}
            style={{
              padding: "4px 8px",
              background: session.activeSurface === "map" ? "var(--bg-card)" : "transparent",
              color: session.activeSurface === "map" ? "var(--signal-flow)" : "var(--text-secondary)",
              border: "none",
              borderRadius: 4,
              fontSize: 11,
              fontWeight: "500",
              cursor: "pointer",
            }}
          >
            ⌘2 Map
          </button>
          <button
            onClick={() => onSelectSurface("studio")}
            style={{
              padding: "4px 8px",
              background: session.activeSurface === "studio" ? "var(--bg-card)" : "transparent",
              color: session.activeSurface === "studio" ? "var(--signal-flow)" : "var(--text-secondary)",
              border: "none",
              borderRadius: 4,
              fontSize: 11,
              fontWeight: "500",
              cursor: "pointer",
            }}
          >
            ⌘3 Studio
          </button>
          <button
            onClick={() => onSelectSurface("effect")}
            style={{
              padding: "4px 8px",
              background: session.activeSurface === "effect" ? "var(--bg-card)" : "transparent",
              color: session.activeSurface === "effect" ? "var(--signal-flow)" : "var(--text-secondary)",
              border: "none",
              borderRadius: 4,
              fontSize: 11,
              fontWeight: "500",
              cursor: "pointer",
            }}
          >
            ⌘4 Effect
          </button>
          <button
            onClick={() => onSelectSurface("evidence")}
            style={{
              padding: "4px 8px",
              background: session.activeSurface === "evidence" ? "var(--bg-card)" : "transparent",
              color: session.activeSurface === "evidence" ? "var(--signal-flow)" : "var(--text-secondary)",
              border: "none",
              borderRadius: 4,
              fontSize: 11,
              fontWeight: "500",
              cursor: "pointer",
            }}
          >
            ⌘5 Evidence
          </button>
          <button
            onClick={() => onSelectSurface("arena")}
            style={{
              padding: "4px 8px",
              background: session.activeSurface === "arena" ? "var(--bg-card)" : "transparent",
              color: session.activeSurface === "arena" ? "var(--signal-flow)" : "var(--text-secondary)",
              border: "none",
              borderRadius: 4,
              fontSize: 11,
              fontWeight: "500",
              cursor: "pointer",
            }}
          >
            ⌘6 Arena
          </button>
          <button
            onClick={() => onSelectSurface("ledger")}
            style={{
              padding: "4px 8px",
              background: session.activeSurface === "ledger" ? "var(--bg-card)" : "transparent",
              color: session.activeSurface === "ledger" ? "var(--signal-flow)" : "var(--text-secondary)",
              border: "none",
              borderRadius: 4,
              fontSize: 11,
              fontWeight: "500",
              cursor: "pointer",
            }}
          >
            ⌘7 Ledger
          </button>
          <button
            onClick={() => onSelectSurface("watch")}
            style={{
              padding: "4px 8px",
              background: session.activeSurface === "watch" ? "var(--bg-card)" : "transparent",
              color: session.activeSurface === "watch" ? "var(--signal-flow)" : "var(--text-secondary)",
              border: "none",
              borderRadius: 4,
              fontSize: 11,
              fontWeight: "500",
              cursor: "pointer",
            }}
          >
            ⌘8 Watch
          </button>
        </nav>
      </header>

      {/* Main Surface Viewport */}
      <main style={{ flex: 1, display: "flex", overflow: "hidden", padding: 16 }}>
        {session.activeSurface === "theatre" && (
          <div style={{ flex: 1, display: "grid", gridTemplateColumns: "minmax(210px, 0.8fr) minmax(320px, 2fr) minmax(260px, 1fr)", gap: 16, overflow: "hidden" }}>
            {/* Left: Turn Spine */}
            <div style={{ background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: 6, padding: 12, display: "flex", flexDirection: "column", gap: 8 }}>
              <div style={{ fontSize: 11, fontWeight: "bold", color: "var(--text-muted)", textTransform: "uppercase" }}>
                Turn Spine (Unary Loop I-11)
              </div>
              <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 6 }}>
                {fold.turns.length === 0 ? <div style={{ padding: 10, color: "var(--text-muted)", fontSize: 12 }}>Turn telemetry unavailable in this event stream.</div> : fold.turns.map((turn) => (
                  <div key={turn.turnNumber} className="reveal" style={{ padding: 8, background: "var(--bg-card)", borderRadius: 4, border: "1px solid var(--border-subtle)", fontSize: 12 }}>
                    <div style={{ display: "flex", justifyContent: "space-between" }}><span style={{ fontWeight: "bold", color: "var(--signal-flow)" }}>Turn {turn.turnNumber} ({turn.status})</span><span>{turn.invocations.length} invocations</span></div>
                    <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 4 }}>Cost: {formatMicrosToUsd(turn.totalCostMicros)} • Tokens: {turn.totalTokens}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Center: Live Transcript & Approvals */}
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 12, overflow: "hidden" }}>
              <ApprovalInterceptor
                pendingApproval={fold.pendingApproval}
                onResolve={onResolveApproval}
              />

              <div style={{ flex: 1, background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: 6, padding: 12, overflowY: "auto", display: "flex", flexDirection: "column", gap: 8 }}>
                <div style={{ fontSize: 11, fontWeight: "bold", color: "var(--text-muted)", textTransform: "uppercase" }}>
                  Transcript ({rows.length} Events)
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
                        padding: "6px 10px",
                        background: r.seq === session.selectedSeq ? "var(--bg-card-hover)" : "var(--bg-card)",
                        borderRadius: 4,
                        border: "1px solid var(--border-subtle)",
                        cursor: "pointer",
                        fontSize: 12,
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "var(--text-muted)" }}>
                        <span style={{ fontFamily: "var(--font-mono)" }}>seq {r.seq.toString()}</span>
                        <span>{new Date(r.occurredAtMs).toISOString().slice(11, 23)}</span>
                      </div>
                      <div style={{ fontWeight: "bold", color: "var(--signal-flow)", marginTop: 2 }}>{kind}</div>
                      {typeof env.payload?.text === "string" && (
                        <div style={{ color: "var(--text-secondary)", fontSize: 11, marginTop: 4 }}>
                          {env.payload.text}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Right: Effect Inspector */}
            <div style={{ background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: 6, overflowY: "auto" }}>
              <EffectInspector effect={activeEffect} />
            </div>
          </div>
        )}

        {session.activeSurface === "map" && <SubstrateMapView fold={fold} />}
        {session.activeSurface === "studio" && <CompositionStudioView fold={fold} />}
        {session.activeSurface === "effect" && (
          <div style={{ flex: 1, background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: 6, padding: 16 }}>
            <EffectInspector effect={activeEffect} />
          </div>
        )}
        {session.activeSurface === "evidence" && (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 16, overflowY: "auto" }}>
            <EvidenceGrid rows={fold.evidenceRows} />
            <TrajectoryWaterfall spans={fold.spans} selectedSpanId={selectedSpanId} onSelectSpan={setSelectedSpanId} />
          </div>
        )}
        {session.activeSurface === "arena" && <ArenaView fold={fold} />}
        {session.activeSurface === "ledger" && (
          <LedgerExplorerView rows={rows} filterQuery={filterQuery} onFilterChange={setFilterQuery} />
        )}
        {session.activeSurface === "watch" && <AutonomyWatchView fold={fold} />}
      </main>

      {/* Bottom Ledger Tape (Scrubbable Seq Axis) */}
      <footer
        style={{
          height: 36,
          background: "var(--bg-surface)",
          borderTop: "1px solid var(--border-subtle)",
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          gap: 16,
          fontSize: 11,
          fontFamily: "var(--font-mono)",
        }}
      >
        <span style={{ color: "var(--text-muted)" }}>LEDGER TAPE</span>
        <input
          type="range"
          min="1"
          max={Math.max(1, Number(latestSeq ?? fold.atSeq)).toString()}
          value={session.selectedSeq.toString() || "1"}
          onChange={(e) => onSelectSeq(BigInt(e.target.value))}
          style={{ flex: 1, cursor: "pointer" }}
        />
        <span style={{ color: "var(--signal-flow)" }}>
          {session.selectedSeq === 0n || session.selectedSeq >= (latestSeq ?? fold.atSeq) ? "● LIVE" : `⧗ seq ${session.selectedSeq}`}
        </span>
      </footer>
    </div>
  );
};
