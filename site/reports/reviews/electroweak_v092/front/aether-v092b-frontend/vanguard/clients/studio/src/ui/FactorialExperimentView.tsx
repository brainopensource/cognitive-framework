import React, { useState } from "react";
import type { StudioFold } from "../store/fold.js";

type BenchmarkTrial = {
  id: string;
  name: string;
  modelA: string;
  modelB: string;
  trialsCount: number;
  modelASuccess: number;
  modelBSuccess: number;
  bWinsOnly: number; // b: A failed, B succeeded (n01)
  aWinsOnly: number; // c: A succeeded, B failed (n10)
  bothSucceeded: number; // n11
  bothFailed: number; // n00
  meanCostA: number;
  meanCostB: number;
  meanTimeA: number;
  meanTimeB: number;
};

export const FactorialExperimentView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => {
  const [selectedTrialId, setSelectedTrialId] = useState<string>("trial-01");
  const [isRunning, setIsRunning] = useState<boolean>(false);

  const trials: BenchmarkTrial[] = [
    {
      id: "trial-01",
      name: "AST Race Condition & Lease Safety Suite (N=50)",
      modelA: "Claude 3.7 Sonnet (Baseline)",
      modelB: "DeepSeek R1 + Local 14B Fast Reflex (Challenger)",
      trialsCount: 50,
      modelASuccess: 44, // 88%
      modelBSuccess: 48, // 96%
      bothSucceeded: 43,
      bothFailed: 1,
      bWinsOnly: 5, // n01 = 5
      aWinsOnly: 1, // n10 = 1
      meanCostA: 0.142,
      meanCostB: 0.038,
      meanTimeA: 1840,
      meanTimeB: 920,
    },
    {
      id: "trial-02",
      name: "SMT Invariant Proof & Lean Witness Suite (N=30)",
      modelA: "Direct Single Agent",
      modelB: "Stigmergic Debate Pair (M-7)",
      trialsCount: 30,
      modelASuccess: 21, // 70%
      modelBSuccess: 28, // 93%
      bothSucceeded: 20,
      bothFailed: 1,
      bWinsOnly: 8, // n01 = 8
      aWinsOnly: 1, // n10 = 1
      meanCostA: 0.220,
      meanCostB: 0.310,
      meanTimeA: 3400,
      meanTimeB: 2800,
    },
  ];

  const activeTrial = trials.find((t) => t.id === selectedTrialId) || trials[0];

  // Calculate McNemar statistic with continuity correction:
  // chi_square = (|b - c| - 1)^2 / (b + c)
  const b = activeTrial.bWinsOnly;
  const c = activeTrial.aWinsOnly;
  const denominator = b + c;
  const chiSquare = denominator > 0 ? Math.pow(Math.abs(b - c) - 1, 2) / denominator : 0;
  const isSignificant = chiSquare >= 3.841; // p < 0.05 threshold
  const pEstimate = isSignificant ? (chiSquare > 6.635 ? "< 0.01" : "< 0.05") : "> 0.05 (Not Significant)";

  const handleRunExperiment = () => {
    setIsRunning(true);
    setTimeout(() => setIsRunning(false), 3000);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 14, overflow: "hidden" }}>
      {/* Top Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          background: "var(--bg-surface)",
          padding: "10px 16px",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-subtle)",
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontWeight: 800, fontSize: 13, color: "var(--text-primary)" }}>
              A/B FACTORIAL EXPERIMENTATION LAB
            </span>
            <span className="badge-mono" style={{ color: "var(--signal-flow)" }}>
              McNemar Hypothesis Gating (p &lt; 0.05)
            </span>
          </div>
          <p style={{ margin: "2px 0 0 0", fontSize: 11, color: "var(--text-muted)" }}>
            Statistically compare models, prompts, compactions, and topologies across benchmark suites.
          </p>
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <button
            onClick={handleRunExperiment}
            disabled={isRunning}
            style={{
              background: isRunning ? "var(--bg-card)" : "var(--text-primary)",
              color: isRunning ? "var(--text-muted)" : "#000",
              border: "none",
              borderRadius: "var(--radius-sm)",
              padding: "6px 14px",
              fontSize: 11,
              fontWeight: 700,
              cursor: isRunning ? "wait" : "pointer",
            }}
          >
            {isRunning ? "RUNNING TRIAL MATRIX..." : "EXECUTE FACTORIAL SUITE"}
          </button>
        </div>
      </div>

      {/* Main Grid: Trial Selector + Statistical Results */}
      <div style={{ display: "grid", gridTemplateColumns: "360px 1fr", gap: 14, flex: 1, minHeight: 0 }}>
        {/* Left: Trial Selector */}
        <div
          style={{
            background: "var(--bg-surface)",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-subtle)",
            padding: 12,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: 8,
          }}
        >
          <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 4 }}>
            Active Factorial Experiments
          </div>

          {trials.map((trial) => {
            const isSelected = trial.id === selectedTrialId;
            return (
              <div
                key={trial.id}
                onClick={() => setSelectedTrialId(trial.id)}
                style={{
                  background: isSelected ? "var(--bg-card)" : "var(--bg-panel)",
                  border: isSelected ? "1px solid var(--signal-flow)" : "1px solid var(--border-subtle)",
                  borderRadius: "var(--radius-sm)",
                  padding: 10,
                  cursor: "pointer",
                  display: "flex",
                  flexDirection: "column",
                  gap: 4,
                }}
              >
                <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-primary)" }}>{trial.name}</span>
                <div style={{ fontSize: 10, color: "var(--text-secondary)" }}>
                  {trial.modelA} <span style={{ color: "var(--signal-flow)" }}>vs</span> {trial.modelB}
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 9, color: "var(--text-muted)", marginTop: 2 }}>
                  <span>N = {trial.trialsCount} runs</span>
                  <span style={{ color: "var(--signal-proof)" }}>
                    Δ = +{Math.round(((trial.modelBSuccess - trial.modelASuccess) / trial.trialsCount) * 100)}%
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Statistical Verification Deck */}
        <div
          style={{
            background: "var(--bg-surface)",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-subtle)",
            padding: 16,
            overflowY: "auto",
            display: "flex",
            flexDirection: "column",
            gap: 16,
          }}
        >
          {/* Comparison Cards */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div style={{ background: "var(--bg-panel)", padding: 12, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase" }}>
                Baseline Configuration (A)
              </div>
              <div style={{ fontSize: 12, fontWeight: 800, color: "var(--text-primary)", marginTop: 2 }}>
                {activeTrial.modelA}
              </div>
              <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 4, fontSize: 11 }}>
                <div>Success Rate: <strong>{Math.round((activeTrial.modelASuccess / activeTrial.trialsCount) * 100)}%</strong> ({activeTrial.modelASuccess}/{activeTrial.trialsCount})</div>
                <div>Mean Cost: <strong>${activeTrial.meanCostA.toFixed(3)}</strong> / task</div>
                <div>Mean Latency: <strong>{activeTrial.meanTimeA} ms</strong></div>
              </div>
            </div>

            <div style={{ background: "var(--bg-panel)", padding: 12, borderRadius: "var(--radius-sm)", border: "1px solid var(--signal-flow)" }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: "var(--signal-flow)", textTransform: "uppercase" }}>
                Challenger Configuration (B)
              </div>
              <div style={{ fontSize: 12, fontWeight: 800, color: "var(--text-primary)", marginTop: 2 }}>
                {activeTrial.modelB}
              </div>
              <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 4, fontSize: 11 }}>
                <div>Success Rate: <strong style={{ color: "var(--signal-proof)" }}>{Math.round((activeTrial.modelBSuccess / activeTrial.trialsCount) * 100)}%</strong> ({activeTrial.modelBSuccess}/{activeTrial.trialsCount})</div>
                <div>Mean Cost: <strong style={{ color: "var(--signal-proof)" }}>${activeTrial.meanCostB.toFixed(3)}</strong> / task</div>
                <div>Mean Latency: <strong style={{ color: "var(--signal-proof)" }}>{activeTrial.meanTimeB} ms</strong></div>
              </div>
            </div>
          </div>

          {/* McNemar 2x2 Contingency Table */}
          <div style={{ background: "var(--bg-panel)", padding: 12, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }}>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 8 }}>
              2×2 Paired Contingency Matrix
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "140px 1fr 1fr", gap: 6, textAlign: "center", fontSize: 11 }}>
              <div />
              <div style={{ fontWeight: 700, color: "var(--text-secondary)" }}>Challenger PASS (1)</div>
              <div style={{ fontWeight: 700, color: "var(--text-secondary)" }}>Challenger FAIL (0)</div>

              <div style={{ fontWeight: 700, textAlign: "left" }}>Baseline PASS (1)</div>
              <div style={{ background: "var(--bg-card)", padding: 6, borderRadius: 3 }}>
                {activeTrial.bothSucceeded} (Both Pass)
              </div>
              <div style={{ background: "var(--bg-card)", padding: 6, borderRadius: 3, color: "var(--signal-deny)" }}>
                {activeTrial.aWinsOnly} (Baseline Only)
              </div>

              <div style={{ fontWeight: 700, textAlign: "left" }}>Baseline FAIL (0)</div>
              <div style={{ background: "var(--bg-card)", padding: 6, borderRadius: 3, color: "var(--signal-proof)", fontWeight: 700 }}>
                {activeTrial.bWinsOnly} (Challenger Only)
              </div>
              <div style={{ background: "var(--bg-card)", padding: 6, borderRadius: 3 }}>
                {activeTrial.bothFailed} (Both Fail)
              </div>
            </div>
          </div>

          {/* Statistical Hypothesis Gate Banner */}
          <div
            style={{
              padding: 12,
              borderRadius: "var(--radius-sm)",
              border: isSignificant ? "1px solid var(--signal-proof)" : "1px solid var(--signal-hold)",
              background: isSignificant ? "rgba(74, 222, 128, 0.08)" : "rgba(251, 191, 36, 0.08)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <div>
              <div style={{ fontWeight: 800, fontSize: 12, color: isSignificant ? "var(--signal-proof)" : "var(--signal-hold)" }}>
                {isSignificant ? "✓ STATISTICALLY SIGNIFICANT (PROMOTION AUTHORIZED)" : "⚠ INSUFFICIENT SIGNIFICANCE (FAIL-CLOSED)"}
              </div>
              <div className="font-mono" style={{ fontSize: 10, color: "var(--text-secondary)", marginTop: 2 }}>
                McNemar χ² = {chiSquare.toFixed(3)} • p-value {pEstimate} (Threshold: χ² ≥ 3.841)
              </div>
            </div>

            <button
              disabled={!isSignificant}
              style={{
                background: isSignificant ? "var(--signal-proof)" : "var(--bg-card)",
                color: isSignificant ? "#000" : "var(--text-muted)",
                border: "none",
                borderRadius: "var(--radius-sm)",
                padding: "6px 12px",
                fontSize: 10,
                fontWeight: 800,
                cursor: isSignificant ? "pointer" : "not-allowed",
              }}
            >
              PROMOTE TO PRODUCTION
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
