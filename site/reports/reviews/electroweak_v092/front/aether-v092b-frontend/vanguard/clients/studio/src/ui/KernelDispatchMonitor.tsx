import React, { useState } from "react";
import type { StudioFold, EffectRecord, PipelineStage } from "../store/fold.js";
import { formatDigestShort, formatMicrosToUsd } from "../store/session.js";

const STAGES: { stage: PipelineStage; name: string; desc: string; domainBlind: boolean }[] = [
  { stage: "S0", name: "ENTER", desc: "EffectRequest ingested from Decision Plane", domainBlind: true },
  { stage: "S1", name: "PARSE", desc: "Contract schema & JSON-RPC validation", domainBlind: true },
  { stage: "S2", name: "RESOLVE", desc: "Adapter lookup before any lease (K-04)", domainBlind: true },
  { stage: "S3", name: "DESCRIBE", desc: "Canonical RFC-8785 JCS SHA-256 digest", domainBlind: true },
  { stage: "S4", name: "CLASSIFY", desc: "Dynamic capability widening check (K-08)", domainBlind: true },
  { stage: "S5", name: "AUTHORIZE", desc: "Policy check & Ed25519 human approval gate", domainBlind: true },
  { stage: "S6", name: "GRANT", desc: "Single-use descriptor-bound cryptographic grant", domainBlind: true },
  { stage: "S7", name: "RESERVE", desc: "6D Economic Tensor debit (USD, ms, tok, bytes)", domainBlind: true },
  { stage: "S8", name: "VERIFY", desc: "Point-of-effect grant & unexpired check (K-05)", domainBlind: true },
  { stage: "S8a", name: "INTENT", desc: "EffectStarted appended to WAL & FSYNC (K-47)", domainBlind: true },
  { stage: "S9", name: "DISPATCH", desc: "Isolated execution in rootless bwrap UID 10001", domainBlind: true },
  { stage: "S10", name: "COMMIT", desc: "Debit reality & actual costs (overruns included)", domainBlind: true },
  { stage: "S11", name: "RELEASE", desc: "Governor.release(lease) in finally block (K-06)", domainBlind: true },
  { stage: "S12", name: "EMIT", desc: "Durable outcome events emitted to State Plane", domainBlind: true },
];

export const KernelDispatchMonitor: React.FC<{
  readonly fold: StudioFold;
  readonly activeEffect?: EffectRecord;
}> = ({ fold, activeEffect }) => {
  const [selectedStage, setSelectedStage] = useState<PipelineStage>("S9");
  const currentStage = activeEffect?.stage || "S12";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* Header Bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontWeight: 700, fontSize: 13, color: "var(--text-primary)" }}>
              TCB Capability Microkernel (S0–S12 Reference Monitor)
            </span>
            <span className="badge-mono" style={{ color: "var(--signal-flow)" }}>
              LOC ≤ 1438 (CURRENT: 1365)
            </span>
            <span className="badge-mono" style={{ color: "var(--signal-proof)" }}>
              I-7 DOMAIN-BLIND
            </span>
          </div>
          <p style={{ margin: "4px 0 0 0", fontSize: 11, color: "var(--text-secondary)" }}>
            The sole path from proposal to effect. No secondary bypass. Monotonic capability attenuation and fail-closed isolation.
          </p>
        </div>

        {/* 6D Economic Tensor Live Summary */}
        <div style={{ display: "flex", gap: 12, background: "var(--bg-panel)", padding: "6px 12px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 9, color: "var(--text-muted)", textTransform: "uppercase" }}>Cost USD</div>
            <div className="font-mono" style={{ fontSize: 12, fontWeight: 700, color: "var(--signal-flow)" }}>
              {formatMicrosToUsd(fold.totalCostMicros)}
            </div>
          </div>
          <div style={{ width: 1, background: "var(--border-subtle)" }} />
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 9, color: "var(--text-muted)", textTransform: "uppercase" }}>Tokens</div>
            <div className="font-mono" style={{ fontSize: 12, fontWeight: 700, color: "var(--text-primary)" }}>
              {fold.totalTokens.toLocaleString()}
            </div>
          </div>
          <div style={{ width: 1, background: "var(--border-subtle)" }} />
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 9, color: "var(--text-muted)", textTransform: "uppercase" }}>Active Leases</div>
            <div className="font-mono" style={{ fontSize: 12, fontWeight: 700, color: "var(--signal-proof)" }}>
              {fold.leases.size}
            </div>
          </div>
        </div>
      </div>

      {/* 13 Stages Pipeline Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 6 }}>
        {STAGES.map((s, idx) => {
          const isCurrent = s.stage === currentStage;
          const isSelected = s.stage === selectedStage;
          const isGuarded = ["S8", "S8a", "S9", "S10"].includes(s.stage);

          let statusColor = "var(--border-subtle)";
          let badgeBg = "var(--bg-card)";
          if (isCurrent) {
            statusColor = "var(--signal-flow)";
            badgeBg = "rgba(56, 189, 248, 0.15)";
          } else if (isSelected) {
            statusColor = "var(--text-secondary)";
          }

          return (
            <button
              key={s.stage}
              onClick={() => setSelectedStage(s.stage)}
              style={{
                background: badgeBg,
                border: `1px solid ${statusColor}`,
                borderRadius: "var(--radius-sm)",
                padding: "8px 6px",
                textAlign: "left",
                cursor: "pointer",
                position: "relative",
                display: "flex",
                flexDirection: "column",
                gap: 4,
                boxShadow: isCurrent ? "var(--shadow-glow)" : "none",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className="font-mono" style={{ fontSize: 11, fontWeight: 800, color: isCurrent ? "var(--signal-flow)" : "var(--text-primary)" }}>
                  {s.stage}
                </span>
                {isGuarded && (
                  <span style={{ fontSize: 8, color: "var(--signal-void)", fontWeight: 700 }}>
                    GUARD
                  </span>
                )}
              </div>
              <div style={{ fontSize: 10, fontWeight: 600, color: "var(--text-secondary)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                {s.name}
              </div>
            </button>
          );
        })}
      </div>

      {/* Detail Pane for Selected Stage */}
      {(() => {
        const info = STAGES.find((s) => s.stage === selectedStage) || STAGES[0];
        return (
          <div
            style={{
              padding: 12,
              background: "var(--bg-panel)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--border-subtle)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span className="font-mono" style={{ fontWeight: 800, fontSize: 13, color: "var(--signal-flow)" }}>
                  {info.stage} — {info.name}
                </span>
                <span className="badge-mono" style={{ color: "var(--text-muted)" }}>
                  INVARIANT ENFORCED
                </span>
              </div>
              <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>
                {info.desc}
              </div>
            </div>

            {activeEffect && (
              <div className="font-mono" style={{ fontSize: 11, color: "var(--text-muted)", textAlign: "right" }}>
                <div>Action: <span style={{ color: "var(--text-primary)" }}>{activeEffect.action}</span></div>
                <div>Descriptor: <span style={{ color: "var(--signal-flow)" }}>{formatDigestShort(activeEffect.descriptorDigest)}</span></div>
              </div>
            )}
          </div>
        );
      })()}
    </div>
  );
};
