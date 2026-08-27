/**
 * AUTO-GENERATED: Observatory Runtime Inspector
 */
import React from "react";

export interface RuntimeInspectorProps {
  readonly agentCoverage: string;
  readonly goalRevision: number;
  readonly planRevision: number;
  readonly strategy: string;
  readonly effects: readonly string[];
  readonly failures: readonly string[];
  readonly budgetAllocated: number;
  readonly budgetConsumed: number;
  readonly capabilities: readonly string[];
  readonly attenuationChain: readonly string[];
}

export const RuntimeInspector: React.FC<RuntimeInspectorProps> = ({
  agentCoverage,
  goalRevision,
  planRevision,
  strategy,
  effects,
  failures,
  budgetAllocated,
  budgetConsumed,
  capabilities,
  attenuationChain
}) => {
  return (
    <div style={{ padding: "16px", background: "var(--bg-canvas)", color: "var(--text-primary)", display: "flex", flexDirection: "column", gap: "16px" }}>
      <h2>Runtime Inspector</h2>
      
      <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>
        <div style={{ background: "var(--bg-panel)", padding: "12px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", flex: "1 1 200px" }}>
          <h4>Agent View Coverage</h4>
          <p className="font-mono">{agentCoverage}</p>
        </div>
        
        <div style={{ background: "var(--bg-panel)", padding: "12px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", flex: "1 1 200px" }}>
          <h4>Revisions</h4>
          <div>Goal Revision: {goalRevision}</div>
          <div>Plan Revision: {planRevision}</div>
        </div>

        <div style={{ background: "var(--bg-panel)", padding: "12px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", flex: "1 1 200px" }}>
          <h4>Strategy</h4>
          <p>{strategy}</p>
        </div>

        <div style={{ background: "var(--bg-panel)", padding: "12px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)", flex: "1 1 200px" }}>
          <h4>Budget</h4>
          <div>Allocated: {budgetAllocated}</div>
          <div>Consumed: {budgetConsumed}</div>
        </div>
      </div>

      <div style={{ display: "flex", gap: "16px" }}>
        <div style={{ flex: 1, background: "var(--bg-panel)", padding: "12px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
          <h4>Settled Effects & Failures</h4>
          <div><strong>Effects:</strong></div>
          <ul>{effects.map((e, i) => <li key={i}>{e}</li>)}</ul>
          <div><strong>Failures:</strong></div>
          <ul>{failures.map((f, i) => <li key={i} style={{ color: "var(--signal-deny)" }}>{f}</li>)}</ul>
        </div>
        
        <div style={{ flex: 1, background: "var(--bg-panel)", padding: "12px", borderRadius: "var(--radius-md)", border: "1px solid var(--border-subtle)" }}>
          <h4>Capabilities & Attenuation</h4>
          <div><strong>Active Capabilities:</strong></div>
          <ul>{capabilities.map((c, i) => <li key={i}>{c}</li>)}</ul>
          <div><strong>Attenuation Chain:</strong></div>
          <ul className="font-mono">{attenuationChain.map((a, i) => <li key={i}>{a}</li>)}</ul>
        </div>
      </div>
    </div>
  );
};
