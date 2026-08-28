import React, { useState } from "react";

type AgentTemplate = {
  id: string;
  name: string;
  icon: string;
  domain: "Software Engineering" | "Formal Reasoning" | "Deep Research" | "Security & Audit" | "Meta-Optimization";
  description: string;
  harnessDigest: string;
  requiredTools: string[];
  budgetTokens: number;
  evalEvidence: string;
  sandboxProfile: "RootlessConcealed" | "NetworkIsolated" | "ReadWriteWorkspace";
  status: "PRODUCTION_READY" | "EXPERIMENTAL" | "CANDIDATE";
};

const TEMPLATES: AgentTemplate[] = [
  {
    id: "agent_coder_v2",
    name: "Autonomous Software Engineer (Surgical Refactor)",
    icon: "💻",
    domain: "Software Engineering",
    description: "Surgical AST refactoring, bug diagnosis, and test-driven patch application under strict sandbox containment.",
    harnessDigest: "sha256:harness_coder_99af2b",
    requiredTools: ["fs.read", "fs.patch", "proc.exec", "git.diff"],
    budgetTokens: 45000,
    evalEvidence: "Passed 96.2% on SWE-bench Lite paired evaluations (p = 0.004)",
    sandboxProfile: "ReadWriteWorkspace",
    status: "PRODUCTION_READY",
  },
  {
    id: "agent_research_v1",
    name: "Deep Citation Synthesizer & Knowledge Distiller",
    icon: "🔬",
    domain: "Deep Research",
    description: "Comprehensive multi-paper survey, Pareto frontier extraction, and cryptographic citation integrity verification.",
    harnessDigest: "sha256:harness_research_44d18e",
    requiredTools: ["web.search", "arxiv.fetch", "pdf.parse", "citation.verify"],
    budgetTokens: 60000,
    evalEvidence: "Zero hallucinated citations across 120 benchmark queries",
    sandboxProfile: "NetworkIsolated",
    status: "PRODUCTION_READY",
  },
  {
    id: "agent_formal_z3",
    name: "Inductive SMT Invariant Prover (Lean / Z3)",
    icon: "📐",
    domain: "Formal Reasoning",
    description: "Automated synthesis of inductive state-machine invariants with machine-checked SAT-witness validation.",
    harnessDigest: "sha256:harness_formal_77c30a",
    requiredTools: ["smt.solve", "lean.verify", "witness.check"],
    budgetTokens: 30000,
    evalEvidence: "100% sound counter-example generation on distributed mutual exclusion benchmarks",
    sandboxProfile: "RootlessConcealed",
    status: "PRODUCTION_READY",
  },
  {
    id: "agent_security_audit",
    name: "TCB Invariant & Policy Auditor",
    icon: "🛡️",
    domain: "Security & Audit",
    description: "Static and dynamic analysis of capability attenuation, governor lease reclamation, and boundary violations.",
    harnessDigest: "sha256:harness_audit_11b89f",
    requiredTools: ["ast.scan", "policy.check", "secret.scan"],
    budgetTokens: 25000,
    evalEvidence: "Zero false-negative leak detection in K-06 fault injection suite",
    sandboxProfile: "RootlessConcealed",
    status: "PRODUCTION_READY",
  },
  {
    id: "agent_evolution_foundry",
    name: "DPO Trajectory Distiller & Skill Synthesizer",
    icon: "🧬",
    domain: "Meta-Optimization",
    description: "Continuous self-improvement pipeline analyzing winning vs losing trajectories to generate procedural skill cards.",
    harnessDigest: "sha256:harness_dpo_55e21c",
    requiredTools: ["trajectory.align", "dpo.synthesize", "skill.register"],
    budgetTokens: 80000,
    evalEvidence: "Statistically verified skill promotion with McNemar p < 0.05 gating",
    sandboxProfile: "ReadWriteWorkspace",
    status: "CANDIDATE",
  },
];

export const AgentCatalog: React.FC<{ onLaunch?: (templateId: string) => void }> = ({ onLaunch }) => {
  const [search, setSearch] = useState<string>("");
  const [selectedDomain, setSelectedDomain] = useState<string>("ALL");

  const filtered = TEMPLATES.filter((tpl) => {
    const matchSearch =
      tpl.name.toLowerCase().includes(search.toLowerCase()) ||
      tpl.description.toLowerCase().includes(search.toLowerCase()) ||
      tpl.requiredTools.some((t) => t.toLowerCase().includes(search.toLowerCase()));
    const matchDomain = selectedDomain === "ALL" || tpl.domain === selectedDomain;
    return matchSearch && matchDomain;
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16, overflowY: "auto", paddingBottom: 24 }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontWeight: 800, fontSize: 14, color: "var(--text-primary)" }}>
              VERIFIED AGENT COMPOSITION CATALOG
            </span>
            <span className="badge-mono" style={{ color: "var(--signal-flow)" }}>
              {TEMPLATES.length} READY COMPOSITIONS
            </span>
          </div>
          <p style={{ margin: "4px 0 0 0", fontSize: 11, color: "var(--text-secondary)" }}>
            Pre-certified, digest-pinned agent templates compiled to canonical `mhf.manifest/2` schemas.
          </p>
        </div>

        <div className="badge-mono" style={{ padding: "6px 12px", background: "rgba(0, 210, 255, 0.1)", color: "var(--signal-flow)" }}>
          SUBSTRATE: DOMAIN-BLIND
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div
        style={{
          background: "var(--bg-surface)",
          padding: 12,
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-subtle)",
          display: "flex",
          gap: 12,
          alignItems: "center",
        }}
      >
        <input
          type="text"
          placeholder="Search agents, tools (e.g. fs.patch, z3), or descriptions..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            flex: 1,
            background: "var(--bg-card)",
            border: "1px solid var(--border-medium)",
            borderRadius: "var(--radius-sm)",
            padding: "8px 12px",
            color: "var(--text-primary)",
            fontSize: 12,
            outline: "none",
          }}
        />

        <div style={{ display: "flex", gap: 6 }}>
          {["ALL", "Software Engineering", "Formal Reasoning", "Deep Research", "Security & Audit", "Meta-Optimization"].map((dom) => {
            const isSelected = selectedDomain === dom;
            return (
              <button
                key={dom}
                onClick={() => setSelectedDomain(dom)}
                style={{
                  background: isSelected ? "var(--bg-card)" : "transparent",
                  border: isSelected ? "1px solid var(--signal-flow)" : "1px solid var(--border-subtle)",
                  borderRadius: "var(--radius-sm)",
                  padding: "6px 10px",
                  fontSize: 10,
                  fontWeight: 600,
                  color: isSelected ? "var(--signal-flow)" : "var(--text-secondary)",
                  cursor: "pointer",
                }}
              >
                {dom}
              </button>
            );
          })}
        </div>
      </div>

      {/* Agents Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(360px, 1fr))", gap: 16 }}>
        {filtered.map((tpl) => (
          <div
            key={tpl.id}
            style={{
              background: "var(--bg-surface)",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--border-subtle)",
              padding: 16,
              display: "flex",
              flexDirection: "column",
              gap: 12,
              boxShadow: "var(--shadow-elevation)",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 20 }}>{tpl.icon}</span>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 13, color: "var(--text-primary)" }}>{tpl.name}</div>
                  <span className="badge-mono" style={{ fontSize: 9, color: "var(--text-muted)" }}>
                    {tpl.domain}
                  </span>
                </div>
              </div>

              <span
                className="badge-mono"
                style={{
                  color: tpl.status === "PRODUCTION_READY" ? "var(--signal-proof)" : "var(--signal-hold)",
                  background: tpl.status === "PRODUCTION_READY" ? "rgba(74, 222, 128, 0.1)" : "rgba(251, 191, 36, 0.1)",
                }}
              >
                {tpl.status}
              </span>
            </div>

            <p style={{ fontSize: 11, color: "var(--text-secondary)", lineHeight: 1.4, margin: 0 }}>
              {tpl.description}
            </p>

            <div style={{ background: "var(--bg-panel)", padding: 10, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)", display: "flex", flexDirection: "column", gap: 6, fontSize: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-muted)" }}>Harness Digest:</span>
                <span className="font-mono" style={{ color: "var(--signal-flow)" }}>{tpl.harnessDigest}</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-muted)" }}>Budget Ceiling:</span>
                <span className="font-mono" style={{ color: "var(--text-primary)" }}>{tpl.budgetTokens.toLocaleString()} tokens</span>
              </div>
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ color: "var(--text-muted)" }}>Sandbox Profile:</span>
                <span className="badge-mono" style={{ color: "var(--signal-proof)" }}>{tpl.sandboxProfile}</span>
              </div>
            </div>

            {/* Tools list */}
            <div>
              <div style={{ fontSize: 10, color: "var(--text-muted)", marginBottom: 4, textTransform: "uppercase" }}>
                Bound Port Tools
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                {tpl.requiredTools.map((t) => (
                  <span key={t} className="badge-mono" style={{ color: "var(--signal-flow)", fontSize: 9 }}>
                    {t}
                  </span>
                ))}
              </div>
            </div>

            {/* Evidence Footer */}
            <div style={{ borderTop: "1px solid var(--border-subtle)", paddingTop: 10, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ fontSize: 10, color: "var(--signal-proof)" }}>
                ✓ {tpl.evalEvidence}
              </div>

              <button
                onClick={() => onLaunch?.(tpl.id)}
                style={{
                  padding: "6px 12px",
                  background: "var(--signal-flow)",
                  color: "#000",
                  border: "none",
                  borderRadius: "var(--radius-sm)",
                  fontWeight: 700,
                  fontSize: 10,
                  cursor: "pointer",
                }}
              >
                Launch Run
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
