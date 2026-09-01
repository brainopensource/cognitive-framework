import React, { useEffect, useMemo, useState } from "react";
import type { StudioFold } from "../store/fold.js";
import { canonicalManifestJson, compileManifest, compositionDigest, generateAaaCSource, validateAgentDefinition, type AgentDefinition } from "../agent-definition.js";

type HarnessConfig = {
  name: string;
  version: string;
  description: string;
  model: string;
  temperature: number;
  maxTokens: number;
  reasoningEffort: "low" | "medium" | "high";
  tools: string[];
  budget: {
    usdMicros: number;
    tokens: number;
    timeoutMs: number;
    maxDepth: number;
    maxTurns: number;
  };
  profile: "lab" | "hermetic" | "live" | "ci";
  topology: "single_agent" | "planner_executor" | "critic_reviser" | "debate_swarm" | "fanout_research";
  compaction: "l1_l5_hierarchical" | "sliding_window" | "semantic_epoch";
};

const AVAILABLE_MODELS = [
  { id: "free", name: "Configured Tier 1 (Free)", local: false },
  { id: "fast", name: "Configured Tier 2 (Budget)", local: false },
  { id: "ollama/qwen2.5-coder:14b", name: "Ollama Qwen 2.5 Coder 14B (Sub-100ms Local Reflex)", local: true },
  { id: "cassette/recorded-fixture", name: "Cassette Replay Double (Hermetic Zero-Cost)", local: true },
];

const AVAILABLE_TOOLS = [
  { id: "fs.read", name: "fs.read / fs.search", category: "Filesystem", desc: "AST search & file reading", default: true },
  { id: "fs.patch", name: "fs.patch (Surgical)", category: "Editing", desc: "Unified diff surgical patch editor", default: true },
  { id: "proc.exec", name: "proc.exec (Sandbox)", category: "Execution", desc: "Rootless bubblewrap command execution", default: true },
  { id: "git.status", name: "git.status / commit", category: "VCS", desc: "Git repository inspection and commit", default: true },
  { id: "agent.spawn", name: "agent.spawn (M-6)", category: "Delegation", desc: "Recursive sub-agent lineage creation", default: true },
  { id: "mcp.invoke", name: "mcp.invoke (MCP Wire)", category: "Extensibility", desc: "Model Context Protocol tools", default: false },
  { id: "smt.solve", name: "smt.solve (Z3/Lean)", category: "Formal Logic", desc: "SMT solver & witness verification", default: false },
  { id: "web.search", name: "web.search / fetch", category: "Research", desc: "Web search & citation extraction", default: false },
];

export const VisualHarnessBuilder: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => {
  const [config, setConfig] = useState<HarnessConfig>({
    name: "vg-coding-autonomous",
    version: "0.7.2",
    description: "Autonomous coding harness with surgical diffs and exterior test evaluation.",
    model: "default",
    temperature: 0.2,
    maxTokens: 32000,
    reasoningEffort: "high",
    tools: ["fs.read", "fs.patch", "proc.exec", "git.status", "agent.spawn"],
    budget: {
      usdMicros: 2000000, // $2.00
      tokens: 50000,
      timeoutMs: 120000,
      maxDepth: 2,
      maxTurns: 15,
    },
    profile: "live",
    topology: "planner_executor",
    compaction: "l1_l5_hierarchical",
  });

  const [activeTab, setActiveTab] = useState<"visual" | "manifest" | "source">("visual");
  const [testStatus, setTestStatus] = useState<string | null>(null);

  const toggleTool = (toolId: string) => {
    setConfig((prev) => ({
      ...prev,
      tools: prev.tools.includes(toolId) ? prev.tools.filter((t) => t !== toolId) : [...prev.tools, toolId],
    }));
  };

  const definition = useMemo<AgentDefinition>(() => ({
    schemaVersion: "aether.agent-definition/1", name: config.name, description: config.description,
    model: { router: config.model, temperature: config.temperature, maxTokens: config.maxTokens, reasoningEffort: config.reasoningEffort },
    systemPrompt: "Solve through the mediated runtime and report only externally verifiable results.",
    skills: ["repository-understanding", "surgical-patching"],
    context: { strategy: config.compaction, retrieval: ["repository-index", "event-ledger"] },
    memory: { policy: "event-sourced", scopes: ["run", "workspace"] }, tools: config.tools, plugins: [], budget: config.budget,
    approvalPolicy: { mode: "governed-effects", editable: true }, planner: { policy: "evidence-first" },
    recoveryPolicy: { policy: "checkpoint-resume", maxRetries: 2 }, verifier: { policy: "exterior", exteriorRequired: true },
    completionGate: { policy: "verified-result", requireVerification: true },
    subagents: config.topology === "single_agent" ? [] : [{ role: "executor", agentRef: "self", grant: config.tools }],
    topology: { kind: config.topology, channels: config.topology === "single_agent" ? [] : [{ from: "planner", to: "executor", protocol: "event-ledger" }] },
  }), [config]);
  const validationIssues = useMemo(() => validateAgentDefinition(definition), [definition]);
  const manifest = validationIssues.length === 0 ? compileManifest(definition) : null;
  const compiledManifest = manifest ? JSON.stringify(JSON.parse(canonicalManifestJson(manifest)), null, 2) : "Manifest unavailable until validation passes.";
  const compiledSource = generateAaaCSource(definition);
  const [digest, setDigest] = useState("unavailable");
  useEffect(() => {
    let active = true;
    if (manifest) compositionDigest(manifest).then((value) => { if (active) setDigest(value); });
    else setDigest("unavailable");
    return () => { active = false; };
  }, [compiledManifest]);

  const handleTestRun = () => {
    setTestStatus(validationIssues.length === 0 ? "Dry-run valid; no effects executed." : `${validationIssues.length} validation error(s)`);
    setTimeout(() => setTestStatus(null), 4000);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 14, overflow: "hidden" }}>
      {/* Header Bar */}
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
              VISUAL HARNESS &amp; AGENT BUILDER
            </span>
            <span className="badge-mono" style={{ color: "var(--signal-flow)" }}>
              mhf.manifest/2
            </span>
          </div>
          <p style={{ margin: "2px 0 0 0", fontSize: 11, color: "var(--text-muted)" }}>
            Visually design, test, and export customized agentic coding CLI configurations.
          </p>
        </div>

        {/* Action Controls */}
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          {testStatus && (
            <span className="badge-mono" style={{ background: "rgba(74, 222, 128, 0.15)", color: "var(--signal-proof)" }}>
              {testStatus}
            </span>
          )}
          <button
            onClick={handleTestRun}
            style={{
              background: "var(--bg-card)",
              color: "var(--signal-flow)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-sm)",
              padding: "6px 12px",
              fontSize: 11,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            TEST IN SANDBOX
          </button>
          <button
            onClick={() => navigator.clipboard.writeText(compiledManifest)}
            style={{
              background: "var(--text-primary)",
              color: "#000",
              border: "none",
              borderRadius: "var(--radius-sm)",
              padding: "6px 14px",
              fontSize: 11,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            COPY MANIFEST
          </button>
        </div>
      </div>

      {/* Main Composer Viewport */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 420px", gap: 14, flex: 1, minHeight: 0 }}>
        {/* Left Form: Visual Configuration Grid */}
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
          {/* Section 1: Foundation Model & Sampling */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 8 }}>
              1. Foundation Reasoning Model &amp; Sampling
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              {AVAILABLE_MODELS.map((m) => (
                <div
                  key={m.id}
                  onClick={() => setConfig({ ...config, model: m.id })}
                  style={{
                    background: config.model === m.id ? "var(--bg-card)" : "var(--bg-panel)",
                    border: config.model === m.id ? "1px solid var(--signal-flow)" : "1px solid var(--border-subtle)",
                    borderRadius: "var(--radius-sm)",
                    padding: "8px 10px",
                    cursor: "pointer",
                    display: "flex",
                    flexDirection: "column",
                    gap: 2,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-primary)" }}>{m.name}</span>
                    <span className="badge-mono" style={{ fontSize: 8 }}>{m.local ? "LOCAL" : "CLOUD"}</span>
                  </div>
                  <span className="font-mono" style={{ fontSize: 9, color: "var(--text-muted)" }}>{m.id}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Section 2: Capability Tools Matrix */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 8 }}>
              2. Capability Tools Matrix (Pure Port Protocols)
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
              {AVAILABLE_TOOLS.map((t) => {
                const isChecked = config.tools.includes(t.id);
                return (
                  <div
                    key={t.id}
                    onClick={() => toggleTool(t.id)}
                    style={{
                      background: isChecked ? "var(--bg-card)" : "var(--bg-panel)",
                      border: isChecked ? "1px solid var(--signal-proof)" : "1px solid var(--border-subtle)",
                      borderRadius: "var(--radius-sm)",
                      padding: "8px 10px",
                      cursor: "pointer",
                      display: "flex",
                      flexDirection: "column",
                      gap: 2,
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span className="font-mono" style={{ fontSize: 11, fontWeight: 700, color: isChecked ? "var(--signal-proof)" : "var(--text-secondary)" }}>
                        {t.name}
                      </span>
                      <span className="badge-mono" style={{ fontSize: 8 }}>{t.category}</span>
                    </div>
                    <span style={{ fontSize: 10, color: "var(--text-muted)" }}>{t.desc}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Section 3: 6D Economic Tensor & Budgets */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 8 }}>
              3. 6D Economic Tensor Budgets (Kernel Enforced)
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10 }}>
              <div style={{ background: "var(--bg-panel)", padding: 8, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }}>
                <div style={{ fontSize: 9, color: "var(--text-muted)" }}>Max USD Ceiling</div>
                <input
                  type="number"
                  step="0.5"
                  value={config.budget.usdMicros / 1000000}
                  onChange={(e) => setConfig({ ...config, budget: { ...config.budget, usdMicros: Math.round(Number(e.target.value) * 1000000) } })}
                  style={{ width: "100%", background: "var(--bg-card)", border: "1px solid var(--border-subtle)", padding: 4, borderRadius: 3, marginTop: 4, fontSize: 11 }}
                />
              </div>

              <div style={{ background: "var(--bg-panel)", padding: 8, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }}>
                <div style={{ fontSize: 9, color: "var(--text-muted)" }}>Token Limit</div>
                <input
                  type="number"
                  step="10000"
                  value={config.budget.tokens}
                  onChange={(e) => setConfig({ ...config, budget: { ...config.budget, tokens: Number(e.target.value) } })}
                  style={{ width: "100%", background: "var(--bg-card)", border: "1px solid var(--border-subtle)", padding: 4, borderRadius: 3, marginTop: 4, fontSize: 11 }}
                />
              </div>

              <div style={{ background: "var(--bg-panel)", padding: 8, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }}>
                <div style={{ fontSize: 9, color: "var(--text-muted)" }}>Max Recursion Depth</div>
                <input
                  type="number"
                  min="0"
                  max="5"
                  value={config.budget.maxDepth}
                  onChange={(e) => setConfig({ ...config, budget: { ...config.budget, maxDepth: Number(e.target.value) } })}
                  style={{ width: "100%", background: "var(--bg-card)", border: "1px solid var(--border-subtle)", padding: 4, borderRadius: 3, marginTop: 4, fontSize: 11 }}
                />
              </div>
            </div>
          </div>

          {/* Section 4: Topology & Execution Profile */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div>
              <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 6 }}>
                Declarative Topology (M-7)
              </div>
              <select
                value={config.topology}
                onChange={(e) => setConfig({ ...config, topology: e.target.value as any })}
                style={{ width: "100%", background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", padding: 6, borderRadius: "var(--radius-sm)", fontSize: 11 }}
              >
                <option value="single_agent">Direct Single Agent</option>
                <option value="planner_executor">Planner &amp; Executor Pair</option>
                <option value="critic_reviser">Critic &amp; Surgical Reviser Duo</option>
                <option value="debate_swarm">Stigmergic Debate Swarm</option>
                <option value="fanout_research">Fan-out Research Tree</option>
              </select>
            </div>

            <div>
              <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 6 }}>
                Execution Profile Mode
              </div>
              <select
                value={config.profile}
                onChange={(e) => setConfig({ ...config, profile: e.target.value as any })}
                style={{ width: "100%", background: "var(--bg-panel)", border: "1px solid var(--border-subtle)", padding: 6, borderRadius: "var(--radius-sm)", fontSize: 11 }}
              >
                <option value="live">Live Production Provider</option>
                <option value="hermetic">Hermetic Double (Cassette Replay)</option>
                <option value="lab">Lab Benchmark (All Telemetry Retained)</option>
                <option value="ci">CI Strict (Zero Tolerance)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Right Output: Compiled Manifest Preview */}
        <div
          style={{
            background: "var(--bg-surface)",
            borderRadius: "var(--radius-md)",
            border: "1px solid var(--border-subtle)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          {/* Output Tab Header */}
          <div style={{ display: "flex", borderBottom: "1px solid var(--border-subtle)", background: "var(--bg-panel)" }}>
            <button
              onClick={() => setActiveTab("visual")}
              style={{
                background: activeTab === "visual" ? "var(--bg-surface)" : "transparent",
                border: "none",
                padding: "8px 12px",
                color: activeTab === "visual" ? "var(--text-primary)" : "var(--text-muted)",
                fontSize: 11,
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab("manifest")}
              style={{
                background: activeTab === "manifest" ? "var(--bg-surface)" : "transparent",
                border: "none",
                padding: "8px 12px",
                color: activeTab === "manifest" ? "var(--text-primary)" : "var(--text-muted)",
                fontSize: 11,
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Manifest
            </button>
            <button
              onClick={() => setActiveTab("source")}
              style={{
                background: activeTab === "source" ? "var(--bg-surface)" : "transparent",
                border: "none",
                padding: "8px 12px",
                color: activeTab === "source" ? "var(--text-primary)" : "var(--text-muted)",
                fontSize: 11,
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              AaaC Source
            </button>
          </div>

          {/* Code Viewer Body */}
          <div style={{ flex: 1, padding: 12, overflowY: "auto", background: "var(--bg-canvas)" }}>
            {activeTab === "manifest" && (
              <pre className="font-mono" style={{ margin: 0, fontSize: 10, lineHeight: 1.5, color: "var(--signal-flow)" }}>
                {compiledManifest}
              </pre>
            )}

            {activeTab === "source" && (
              <pre className="font-mono" style={{ margin: 0, fontSize: 10, lineHeight: 1.5, color: "var(--text-primary)" }}>
                {compiledSource}
              </pre>
            )}

            {activeTab === "visual" && (
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-primary)" }}>
                  Compiled Composition Summary
                </div>
                <div style={{ background: "var(--bg-panel)", padding: 10, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)", fontSize: 11, color: "var(--text-secondary)" }}>
                  <div><strong>Harness Name:</strong> {config.name}</div>
                  <div><strong>Active Model:</strong> {config.model}</div>
                  <div><strong>Enabled Tools:</strong> {config.tools.length} actions</div>
                  <div><strong>Topology:</strong> {config.topology}</div>
                  <div><strong>Profile Mode:</strong> {config.profile}</div>
                </div>

                <div style={{ background: "var(--bg-panel)", padding: 10, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }}>
                  <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 4 }}>
                    Composition Merkle Digest (D_H)
                  </div>
                  <div className="font-mono" style={{ fontSize: 10, color: "var(--signal-flow)", wordBreak: "break-all" }}>
                    {digest}
                  </div>
                </div>
                {validationIssues.length > 0 && (
                  <div style={{ color: "var(--signal-deny)", fontSize: 10 }}>
                    {validationIssues.map((issue) => `${issue.path}: ${issue.message}`).join(" · ")}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
