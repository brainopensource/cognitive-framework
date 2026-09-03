import React from "react";

export const CompositionDiff: React.FC = () => {
  return (
    <div style={{ padding: 16, background: "var(--bg-surface)", display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <span style={{ fontWeight: 700, fontSize: 13, color: "var(--text-primary)" }}>
            COMPOSITION &amp; HARNESS MANIFEST STRUCTURAL DIFF
          </span>
          <p style={{ margin: "2px 0 0 0", fontSize: 11, color: "var(--text-secondary)" }}>
            Exact structural delta between Baseline (`D_H: sha256:base_77a1`) and Treatment (`D_H: sha256:treat_88c4`).
          </p>
        </div>
        <span className="badge-mono" style={{ color: "var(--signal-flow)" }}>
          SCHEMA: mhf.manifest/2
        </span>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        {/* Baseline Pane */}
        <div style={{ border: "1px solid var(--border-subtle)", padding: 14, borderRadius: "var(--radius-sm)", background: "var(--bg-panel)", display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-subtle)", paddingBottom: 6 }}>
            <span style={{ fontWeight: 700, fontSize: 11, color: "var(--text-muted)" }}>BASELINE: code-agent-v1</span>
            <span className="badge-mono" style={{ color: "var(--signal-deny)" }}>D_H: sha256:base_77a1</span>
          </div>

          <pre className="font-mono" style={{ fontSize: 11, margin: 0, lineHeight: 1.5, color: "var(--text-secondary)" }}>
{`schemaVersion: "mhf.manifest/2"
pack: "code-default@1.0.0"
model:
  provider: "openrouter"
  modelId: "anthropic/claude-3.5-sonnet"
  temperature: 0.2
policies:
  - "policy.sandbox.read_only"
tools:
  - name: "fs.read"
  - name: "proc.exec"
limits:
  maxTurns: 20
  tokenBudget: 30000`}
          </pre>
        </div>

        {/* Treatment Pane */}
        <div style={{ border: "1px solid var(--border-subtle)", padding: 14, borderRadius: "var(--radius-sm)", background: "var(--bg-panel)", display: "flex", flexDirection: "column", gap: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between", borderBottom: "1px solid var(--border-subtle)", paddingBottom: 6 }}>
            <span style={{ fontWeight: 700, fontSize: 11, color: "var(--signal-proof)" }}>TREATMENT: code-agent-v2 (Surgical)</span>
            <span className="badge-mono" style={{ color: "var(--signal-proof)" }}>D_H: sha256:treat_88c4</span>
          </div>

          <pre className="font-mono" style={{ fontSize: 11, margin: 0, lineHeight: 1.5, color: "var(--text-primary)" }}>
{`schemaVersion: "mhf.manifest/2"
pack: "code-default@1.1.0"
model:
  provider: "openrouter"
  modelId: "anthropic/claude-3.5-sonnet"
  temperature: 0.0
policies:
  - "policy.sandbox.workspace_isolated"
`}
<span style={{ color: "var(--signal-proof)" }}>{`+ - "policy.governance.ed25519_approval"`}</span>
{`tools:
  - name: "fs.read"
`}
<span style={{ color: "var(--signal-proof)" }}>{`+ - name: "fs.patch"`}</span>
{`  - name: "proc.exec"
`}
<span style={{ color: "var(--signal-proof)" }}>{`+ - name: "git.diff"`}</span>
{`limits:
  maxTurns: 10
`}
<span style={{ color: "var(--signal-proof)" }}>{`  tokenBudget: 15000  # -50% Conservation`}</span>
          </pre>
        </div>
      </div>
    </div>
  );
};
