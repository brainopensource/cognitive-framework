import React from "react";
import type { EffectRecord, PipelineStage } from "../store/fold.js";

const ALL_STAGES: readonly { stage: PipelineStage; name: string; desc: string }[] = [
  { stage: "S0", name: "ENTER", desc: "EffectRequest received" },
  { stage: "S1", name: "PARSE", desc: "Schema validation" },
  { stage: "S2", name: "RESOLVE", desc: "Action to adapter" },
  { stage: "S3", name: "DESCRIBE", desc: "Canonical descriptor digest" },
  { stage: "S4", name: "CLASSIFY", desc: "Widens capability check" },
  { stage: "S5", name: "AUTHORIZE", desc: "Policy authorization" },
  { stage: "S6", name: "GRANT", desc: "Capability grant issued" },
  { stage: "S7", name: "RESERVE", desc: "Governor lease reserved" },
  { stage: "S8", name: "VERIFY", desc: "Grant binding verified" },
  { stage: "S8a", name: "INTENT", desc: "Durable intent fsync" },
  { stage: "S9", name: "DISPATCH", desc: "Adapter execution" },
  { stage: "S10", name: "COMMIT", desc: "Governor lease committed" },
  { stage: "S11", name: "RELEASE", desc: "Governor lease released" },
  { stage: "S12", name: "EMIT", desc: "Outcome event emitted" },
];

export type EffectInspectorProps = {
  readonly effect?: EffectRecord;
  readonly onClose?: () => void;
};

export const EffectInspector: React.FC<EffectInspectorProps> = ({ effect, onClose }) => {
  if (!effect) {
    return (
      <div style={{ padding: 16, color: "var(--text-muted)", fontSize: 12 }}>
        Select an effect from transcript to inspect S0–S12 execution pipeline.
      </div>
    );
  }

  const stageIndex = ALL_STAGES.findIndex((s) => s.stage === effect.stage);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <span style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase" }}>
            Pipeline Inspector (S0–S12)
          </span>
          <div style={{ fontSize: 14, fontWeight: "bold", color: "var(--text-primary)" }}>
            {effect.action}
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            style={{
              background: "transparent",
              border: "1px solid var(--border-subtle)",
              color: "var(--text-secondary)",
              padding: "2px 8px",
              cursor: "pointer",
              borderRadius: 4,
            }}
          >
            ✕
          </button>
        )}
      </div>

      {/* 13-stage progress rail */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(14, 1fr)",
          gap: 2,
          background: "var(--bg-panel)",
          padding: 8,
          borderRadius: 6,
          border: "1px solid var(--border-subtle)",
        }}
      >
        {ALL_STAGES.map((s, idx) => {
          const isReached = idx <= stageIndex;
          const isCurrent = idx === stageIndex;
          let color = "var(--border-medium)";
          if (isReached) {
            if (effect.outcome === "denied") color = "var(--signal-deny)";
            else if (effect.outcome === "undeterminable") color = "var(--signal-void)";
            else if (effect.outcome === "failed") color = "var(--signal-deny)";
            else color = "var(--signal-flow)";
          }

          return (
            <div
              key={s.stage}
              title={`${s.stage} ${s.name}: ${s.desc}`}
              style={{
                height: 24,
                background: color,
                borderRadius: 2,
                opacity: isReached ? (isCurrent ? 1 : 0.8) : 0.2,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 9,
                fontWeight: "bold",
                color: "#000",
              }}
            >
              {s.stage}
            </div>
          );
        })}
      </div>

      {/* Stage Detail Card */}
      <div
        style={{
          background: "var(--bg-card)",
          padding: 12,
          borderRadius: 6,
          border: "1px solid var(--border-subtle)",
          fontSize: 12,
          display: "flex",
          flexDirection: "column",
          gap: 8,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span style={{ color: "var(--text-muted)" }}>Current Stage:</span>
          <span style={{ fontWeight: "bold", color: "var(--signal-flow)" }}>
            {effect.stage} • {ALL_STAGES.find((s) => s.stage === effect.stage)?.name}
          </span>
        </div>

        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span style={{ color: "var(--text-muted)" }}>Outcome State:</span>
          <span
            style={{
              fontWeight: "bold",
              color:
                effect.outcome === "denied"
                  ? "var(--signal-deny)"
                  : effect.outcome === "undeterminable"
                  ? "var(--signal-void)"
                  : effect.outcome === "settled"
                  ? "var(--signal-proof)"
                  : "var(--signal-flow)",
            }}
          >
            {effect.outcome.toUpperCase()}
          </span>
        </div>

        {effect.descriptorDigest && (
          <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <span style={{ color: "var(--text-muted)", fontSize: 10 }}>Descriptor Digest (JCS S3):</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-secondary)", wordBreak: "break-all" }}>
              {effect.descriptorDigest}
            </span>
          </div>
        )}

        {effect.denialReason && (
          <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <span style={{ color: "var(--signal-deny)", fontSize: 10 }}>Denial Reason (S5 Refusal):</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-primary)" }}>
              {effect.denialReason}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
