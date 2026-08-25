import React from "react";
import type { StudioFold } from "../store/fold.js";
import { runAllAnomalyDetectors } from "../store/detectors.js";

export const AutonomyWatchView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => {
  const findings = runAllAnomalyDetectors(fold);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div>
        <h3 style={{ margin: 0, fontSize: 14, color: "var(--text-primary)" }}>
          Ambient Autonomy Watch (⌘8)
        </h3>
        <p style={{ margin: "4px 0 0 0", fontSize: 12, color: "var(--text-muted)" }}>
          Low-cognitive-load event stream with 9 pure anomaly detectors and substrate health rings.
        </p>
      </div>

      {/* Substrate Health Rings */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
        <div style={{ padding: 12, background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: 6 }}>
          <div style={{ fontSize: 11, color: "var(--text-muted)" }}>TCB LoC Budget</div>
          <div style={{ fontSize: 16, fontWeight: "bold", color: "var(--signal-hold)", marginTop: 4 }}>UNVERIFIED</div>
          <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 2 }}>No linter projection attached</div>
        </div>
        <div style={{ padding: 12, background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: 6 }}>
          <div style={{ fontSize: 11, color: "var(--text-muted)" }}>I-7 Domain-Blindness</div>
          <div style={{ fontSize: 16, fontWeight: "bold", color: "var(--signal-hold)", marginTop: 4 }}>UNVERIFIED</div>
          <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 2 }}>No linter projection attached</div>
        </div>
        <div style={{ padding: 12, background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: 6 }}>
          <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Undeterminable Intents</div>
          <div style={{ fontSize: 16, fontWeight: "bold", color: "var(--signal-void)", marginTop: 4 }}>
            {Array.from(fold.effects.values()).filter((e) => e.outcome === "undeterminable").length}
          </div>
          <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 2 }}>Observed in current fold</div>
        </div>
        <div style={{ padding: 12, background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", borderRadius: 6 }}>
          <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Active Leases</div>
          <div style={{ fontSize: 16, fontWeight: "bold", color: "var(--signal-flow)", marginTop: 4 }}>
            {Array.from(fold.leases.values()).filter((l) => l.state !== "released").length}
          </div>
          <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 2 }}>Observed lease records</div>
        </div>
      </div>

      {/* Active Anomaly Findings */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        <h4 style={{ margin: 0, fontSize: 13, color: "var(--text-primary)" }}>
          Active Findings ({findings.length})
        </h4>

        {findings.length === 0 ? (
          <div style={{ padding: 16, background: "var(--bg-panel)", borderRadius: 6, border: "1px solid var(--border-subtle)", color: "var(--signal-proof)", fontSize: 12 }}>
            ✓ No anomalous behavior detected across 9 pure detector rules.
          </div>
        ) : (
          findings.map((f) => (
            <div
              key={f.id}
              style={{
                padding: 12,
                background: "var(--bg-card)",
                borderRadius: 6,
                border: `1px solid ${
                  f.severity === "error"
                    ? "var(--signal-deny)"
                    : f.severity === "warning"
                    ? "var(--signal-hold)"
                    : "var(--signal-flow)"
                }`,
                display: "flex",
                flexDirection: "column",
                gap: 4,
                fontSize: 12,
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ fontWeight: "bold", color: "var(--text-primary)" }}>{f.title}</span>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-muted)" }}>
                  {f.code}
                </span>
              </div>
              <div style={{ color: "var(--text-secondary)", fontSize: 11 }}>{f.message}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
