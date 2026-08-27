/**
 * AUTO-GENERATED: RunDiff Composition Diff
 */
import React from "react";

export const CompositionDiff: React.FC = () => {
  return (
    <div style={{ padding: "16px", background: "var(--bg-panel)" }}>
      <h3>Composition Diff</h3>
      <p style={{ fontSize: "14px", color: "var(--text-secondary)" }}>
        Visual diff between baseline and treatment compositions.
      </p>
      <div style={{ display: "flex", gap: "16px" }}>
        <div style={{ flex: 1, border: "1px solid var(--border-medium)", padding: "16px", borderRadius: "var(--radius-sm)", background: "var(--bg-card)" }}>
          <h4 style={{ color: "var(--text-muted)" }}>Baseline Composition</h4>
          <pre className="font-mono" style={{ fontSize: "12px", color: "var(--signal-deny)" }}>- pack: vanguard-core@1.0.0</pre>
          <pre className="font-mono" style={{ fontSize: "12px", color: "var(--signal-deny)" }}>- adapter: openai@2.1.0</pre>
        </div>
        <div style={{ flex: 1, border: "1px solid var(--border-medium)", padding: "16px", borderRadius: "var(--radius-sm)", background: "var(--bg-card)" }}>
          <h4 style={{ color: "var(--text-muted)" }}>Treatment Composition</h4>
          <pre className="font-mono" style={{ fontSize: "12px", color: "var(--signal-proof)" }}>+ pack: vanguard-core@1.1.0</pre>
          <pre className="font-mono" style={{ fontSize: "12px", color: "var(--signal-proof)" }}>+ adapter: anthropic@1.0.0</pre>
        </div>
      </div>
    </div>
  );
};
