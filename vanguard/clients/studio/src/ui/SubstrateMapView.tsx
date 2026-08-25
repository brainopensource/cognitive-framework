import React from "react";
import type { StudioFold } from "../store/fold.js";

export const SubstrateMapView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div>
        <h3 style={{ margin: 0, fontSize: 14, color: "var(--text-primary)" }}>
          Substrate Architectural Map (⌘2 Five-Layer Lattice)
        </h3>
        <p style={{ margin: "4px 0 0 0", fontSize: 12, color: "var(--text-muted)" }}>
          Hexagonal boundary flow: domain ← ports ← kernel ← agency ← runtime → adapters.
        </p>
      </div>

      {/* Five Concentric / Stacked Architectural Bands */}
      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {/* L0: Trusted Computing Base Kernel */}
        <div
          style={{
            padding: 16,
            background: "var(--bg-card)",
            border: "2px solid var(--signal-flow)",
            borderRadius: 8,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontWeight: "bold", fontSize: 14, color: "var(--signal-flow)" }}>L0 Kernel (TCB Core)</span>
              <span style={{ fontSize: 10, background: "rgba(0, 210, 255, 0.15)", color: "var(--signal-flow)", padding: "2px 6px", borderRadius: 4 }}>
                I-7 DOMAIN-BLIND
              </span>
            </div>
            <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>
              Reference monitor • 13-stage dispatch pipeline (S0–S12) • Monotonic budget & grants • TCB budget: unavailable
            </div>
          </div>
          <span style={{ color: "var(--signal-hold)", fontWeight: "bold", fontSize: 12 }}>UNVERIFIED</span>
        </div>

        {/* L1: Domain */}
        <div
          style={{
            padding: 14,
            background: "var(--bg-panel)",
            border: "1px solid var(--border-subtle)",
            borderRadius: 6,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontWeight: "bold", fontSize: 13, color: "var(--text-primary)" }}>L1 Domain Layer</div>
            <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
              Pure value objects • RFC-8785 JCS canonicalization • Event contracts • Stdlib Python only
            </div>
          </div>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>vanguard/packages/domain</span>
        </div>

        {/* L2: Ports & SPI */}
        <div
          style={{
            padding: 14,
            background: "var(--bg-panel)",
            border: "1px solid var(--border-subtle)",
            borderRadius: 6,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontWeight: "bold", fontSize: 13, color: "var(--text-primary)" }}>L2 Ports & 5 Frozen SPI Protocols</div>
            <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
              IPlanner • IMemoryEngine • IToolkit • IContextAssembler • IEvaluator • Capability negotiation
            </div>
          </div>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>vanguard/packages/ports</span>
        </div>

        {/* L3: Adapters */}
        <div
          style={{
            padding: 14,
            background: "var(--bg-panel)",
            border: "1px solid var(--border-subtle)",
            borderRadius: 6,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontWeight: "bold", fontSize: 13, color: "var(--text-primary)" }}>L3 Adapters Layer</span>
              <span style={{ fontSize: 10, background: "rgba(245, 158, 11, 0.15)", color: "var(--signal-hold)", padding: "1px 5px", borderRadius: 3 }}>
                I-6 UNTRUSTED PLUGINS
              </span>
            </div>
            <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
              Rootless sandbox (bwrap UID 10001) • SQLite event store • Evaluator RPC client (UID 10002) • Model providers
            </div>
          </div>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>vanguard/packages/adapters</span>
        </div>

        {/* L4: Runtime & Agency */}
        <div
          style={{
            padding: 14,
            background: "var(--bg-panel)",
            border: "1px solid var(--border-subtle)",
            borderRadius: 6,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <div style={{ fontWeight: "bold", fontSize: 13, color: "var(--text-primary)" }}>L4 Runtime & Agency</div>
            <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 2 }}>
              EpisodeEngine turn loop (I-11) • Context compiler • Ledger emitter • Runtime service daemon
            </div>
          </div>
          <span style={{ fontSize: 11, color: "var(--text-muted)" }}>vanguard/packages/runtime</span>
        </div>
      </div>
    </div>
  );
};
