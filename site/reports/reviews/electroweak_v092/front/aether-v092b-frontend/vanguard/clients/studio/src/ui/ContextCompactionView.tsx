import React, { useState } from "react";
import type { StudioFold } from "../store/fold.js";

type ContextLayer = {
  id: string;
  name: string;
  tokens: number;
  cached: boolean;
  content: string;
};

export const ContextCompactionView: React.FC<{ readonly fold: StudioFold }> = ({ fold }) => {
  const [selectedLayerId, setSelectedLayerId] = useState<string>("L1");

  const layers: ContextLayer[] = [
    {
      id: "L1",
      name: "L1 Constitutional Law Zero",
      tokens: 420,
      cached: true,
      content: `[CONSTITUTIONAL LAW ZERO - RFC 2119]\n1. Monotonic capability attenuation is invariant.\n2. Fail-closed on any ambiguity, widened descriptor, or boundary breach.\n3. Domain-blindness in microkernel (threshold <= 1438 LOC).\n4. All mutations require deterministic causal logging prior to execution (S8a).\n5. Leases MUST be released in finally block before outcome emission (K-06).`,
    },
    {
      id: "L2",
      name: "L2 AST Skeleton & Topology Map",
      tokens: 880,
      cached: true,
      content: `[AST REPOSITORY TOPOLOGY]\n- vanguard/packages/domain/: pure value objects, reducers, JCS canon.\n- vanguard/packages/ports/: Port protocols (Kernel, Model, Sandbox, Evaluator).\n- vanguard/packages/kernel/: TCB dispatch S0-S12, budget governor.\n- vanguard/packages/agency/: EpisodeEngine, turn loop, spawn().\n- vanguard/packages/runtime/: Compose, session, SQLite WAL ledger.\n- vanguard/packages/adapters/: bwrap (10001), daemon (10002), providers.`,
    },
    {
      id: "L3",
      name: "L3 Tool Protocol Contracts",
      tokens: 310,
      cached: true,
      content: `[TOOL INTERFACES - JCS CANONICALIZED]\n- fs.read(path: string, start?: int, end?: int) -> text\n- fs.patch(path: string, patch_diff: unified_diff) -> patch_result\n- proc.exec(cmd: string, timeout_ms: int) -> exec_receipt\n- agent.spawn(scope: grant_mask, budget: budget_tensor) -> child_lineage`,
    },
    {
      id: "L4",
      name: "L4 Epistemic Procedural Memory",
      tokens: 240,
      cached: false,
      content: `[ACTIVE HEURISTIC CARDS]\n- skill_lease_safety_v2: Always wrap lease acquisition in try/finally blocks.\n- skill_surgical_diff: Match exact leading whitespace in replacement blocks.\n- skill_domain_blindness: Never introduce domain tokens into kernel/domain packages.`,
    },
    {
      id: "L5",
      name: "L5 Turn Dialogue & Ephemeral History",
      tokens: 1420,
      cached: false,
      content: `[TURN 1 - INVESTIGATE]\nUser: Diagnose lease leak in dispatch sequence.\nModel: Observed Governor.reserve() at S7, but release() missing on exception at S9.\n\n[TURN 2 - PROPOSE PATCH]\nModel proposed fs.patch for dispatch.py adding finally: release(lease).\n\n[COMPACTED EPOCH 1]\nTurns 1-2 condensed into 110 tokens (89% compression ratio).`,
    },
  ];

  const totalTokens = layers.reduce((acc, l) => acc + l.tokens, 0);
  const cachedTokens = layers.filter((l) => l.cached).reduce((acc, l) => acc + l.tokens, 0);
  const cacheHitRatio = Math.round((cachedTokens / totalTokens) * 100);
  const activeLayer = layers.find((l) => l.id === selectedLayerId) || layers[0];

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 14, overflow: "hidden" }}>
      {/* Top Telemetry Header */}
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
              CONTEXT COMPACTION &amp; PROMPT CACHE INSPECTOR
            </span>
            <span className="badge-mono" style={{ color: "var(--signal-flow)" }}>
              5-Layer Stack (L1–L5)
            </span>
          </div>
          <p style={{ margin: "2px 0 0 0", fontSize: 11, color: "var(--text-muted)" }}>
            Inspect compiled prompt structures, KV prefix cache hits, and historical turn compactions.
          </p>
        </div>

        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <div style={{ background: "var(--bg-panel)", padding: "4px 10px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }}>
            <span style={{ fontSize: 10, color: "var(--text-muted)" }}>Total Context: </span>
            <span className="font-mono" style={{ fontSize: 11, fontWeight: 700, color: "var(--text-primary)" }}>
              {totalTokens.toLocaleString()} tokens
            </span>
          </div>

          <div style={{ background: "var(--bg-panel)", padding: "4px 10px", borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }}>
            <span style={{ fontSize: 10, color: "var(--text-muted)" }}>Prefix Cache Hit: </span>
            <span className="font-mono" style={{ fontSize: 11, fontWeight: 700, color: "var(--signal-proof)" }}>
              {cacheHitRatio}% ({cachedTokens.toLocaleString()} tok)
            </span>
          </div>
        </div>
      </div>

      {/* Main Grid: Layer Selector & Content Preview */}
      <div style={{ display: "grid", gridTemplateColumns: "340px 1fr", gap: 14, flex: 1, minHeight: 0 }}>
        {/* Left: Layer Selector */}
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
            Compiled Context Layers
          </div>

          {layers.map((layer) => {
            const isSelected = layer.id === selectedLayerId;
            return (
              <div
                key={layer.id}
                onClick={() => setSelectedLayerId(layer.id)}
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
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-primary)" }}>{layer.name}</span>
                  <span
                    className="badge-mono"
                    style={{
                      fontSize: 8,
                      color: layer.cached ? "var(--signal-proof)" : "var(--text-faint)",
                    }}
                  >
                    {layer.cached ? "⚡ KV CACHED" : "UNCACHED"}
                  </span>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "var(--text-muted)" }}>
                  <span>{layer.tokens} tokens</span>
                  <span>{Math.round((layer.tokens / totalTokens) * 100)}% of budget</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Layer Content Viewer */}
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
          <div
            style={{
              padding: "8px 14px",
              background: "var(--bg-panel)",
              borderBottom: "1px solid var(--border-subtle)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-primary)" }}>
              {activeLayer.name} — Payload Inspection
            </span>
            <span className="badge-mono" style={{ fontSize: 9 }}>
              {activeLayer.tokens} tokens
            </span>
          </div>

          <div style={{ flex: 1, padding: 14, background: "var(--bg-canvas)", overflowY: "auto" }}>
            <pre
              className="font-mono"
              style={{
                margin: 0,
                fontSize: 11,
                lineHeight: 1.6,
                color: "var(--text-primary)",
                whiteSpace: "pre-wrap",
              }}
            >
              {activeLayer.content}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};
