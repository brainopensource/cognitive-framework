import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { FakeRuntimeClient } from "@vanguard/client-core/adapters/fake.js";
import { HttpRuntimeClient } from "@vanguard/client-core/adapters/http.js";
import { WebCryptoSigner } from "@vanguard/client-core/adapters/web-signer.js";
import type { RuntimeClient } from "@vanguard/client-core/contract/types.js";
import { useStudioRuntime } from "./runtime/StudioRuntime.js";
import { StudioApp } from "./ui/StudioApp.js";
import { CSS_VARIABLES } from "./ui/tokens.js";
import type { EventEnvelope } from "./contract/index.js";

const DEMO_RUN_ID = "demo-run";

const base = (seq: string, eventId: string, kind: string, payload: Record<string, unknown>): EventEnvelope => ({
  schemaVersion: "vg.4",
  eventId,
  scope: "episode",
  runId: DEMO_RUN_ID,
  traceId: "trace-meta-01",
  spanId: `span-${seq}`,
  seq,
  occurredAt: new Date(Date.now() + Number(seq) * 1000).toISOString(),
  recordedAt: new Date().toISOString(),
  principal: "developer-rocha",
  tenantId: "local",
  ownerId: "local",
  confidentiality: "internal",
  retentionClass: "standard",
  trainability: "prohibited",
  redactionStatus: "none",
  payload: { kind, ...payload },
});

const demoEvents: EventEnvelope[] = [
  base("1", "ev-001", "GoalDeclared", {
    goal: "Diagnose and patch governor lease leak in kernel dispatch sequence (K-06)",
    goalDigest: "sha256:goal_fix_lease_leak_44a2",
  }),
  base("2", "ev-002", "ContextCompiled", {
    brief: "Enforce guaranteed lease release on exception in guarded dispatch block",
    layers: ["L1", "L2", "L3", "L4", "L5"],
    tokens: 1840,
    promptDigest: "sha256:prm_bundle_88ef",
  }),
  base("3", "ev-003", "ProposalProduced", {
    kind: "effect",
    action: "fs.read",
    args: { path: "vanguard/packages/kernel/dispatch.py" },
    descriptor: "sha256:desc_fs_read_dispatch",
  }),
  base("4", "ev-004", "EffectStarted", {
    descriptor: "sha256:desc_fs_read_dispatch",
    action: "fs.read",
    durationMs: 24,
  }),
  base("5", "ev-005", "EffectCompleted", {
    descriptor: "sha256:desc_fs_read_dispatch",
    outcome: "satisfied",
    durationMs: 14,
  }),
  base("6", "ev-006", "BudgetCommitted", {
    tokens: 980,
    costMicros: "196000",
  }),
  base("7", "ev-007", "ChildSpawned", {
    parentLineageId: "lin_root_001",
    childLineageId: "lin_child_investigator",
    depth: 1,
    budget: { tokens: 3000, usdMicros: 600000 },
  }),
  base("8", "ev-008", "ChildReturned", {
    parentLineageId: "lin_root_001",
    childLineageId: "lin_child_investigator",
    artifactRef: "sha256:art_investigation_summary_88c9",
    status: "satisfied",
  }),
  base("9", "ev-009", "StrategyChanged", {
    directive: "patch_code",
    reason: "Investigation confirmed missing finally block in _guarded execution",
    confidence: 0.94,
  }),
  base("10", "ev-010", "ApprovalRequested", {
    approvalId: "approval-k06-patch",
    action: "fs.patch",
    normalizedDiff: `--- a/vanguard/packages/kernel/dispatch.py\n+++ b/vanguard/packages/kernel/dispatch.py\n@@ -315,5 +315,6 @@\n         outcome = adapter.execute(request)\n         settlement = self._governor.commit(lease, outcome.actual_cost)\n-        self._governor.release(lease)\n+    finally:\n+        self._governor.release(lease)`,
    argsDigest: "sha256:args_diff_k06",
    descriptorDigest: "sha256:desc_fs_patch_dispatch",
    expiresAt: new Date(Date.now() + 3600000).toISOString(),
  }),
  base("11", "ev-011", "ApprovalResolved", {
    approvalId: "approval-k06-patch",
    decision: "approved",
    reviewer: "developer-rocha",
  }),
  base("12", "ev-012", "EffectStarted", {
    descriptor: "sha256:desc_fs_patch_dispatch",
    action: "fs.patch",
    durationMs: 38,
  }),
  base("13", "ev-013", "EffectCompleted", {
    descriptor: "sha256:desc_fs_patch_dispatch",
    outcome: "satisfied",
    durationMs: 22,
  }),
  base("14", "ev-014", "EpisodeCompleted", {
    outcome: "satisfied",
    verdict: "1",
    terminalSignal: "all_tests_passed",
  }),
];

const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("Missing #root element");
const style = document.createElement("style");
style.textContent = CSS_VARIABLES;
document.head.appendChild(style);

const urlParams = new URLSearchParams(window.location.search);
const liveRunIdFromUrl = urlParams.get("runId");

/**
 * Demo mode is an explicit, user-chosen client (FakeRuntimeClient), never a silent
 * fallback from a failed live connection: mode only changes via the pill switcher below.
 */
function makeDemoClient(): RuntimeClient {
  return new FakeRuntimeClient({
    runs: new Map([[DEMO_RUN_ID, { status: "running", events: demoEvents }]]),
    health: { status: "ok", version: "demo" },
  });
}

const webSigner = new WebCryptoSigner("web-operator-key", "operator:web");
void webSigner.initialize();

function makeLiveClient(): RuntimeClient {
  return new HttpRuntimeClient({ baseUrl: "", signer: webSigner });
}

function Observatory() {
  const [mode, setMode] = useState<"live" | "demo">(liveRunIdFromUrl ? "live" : "demo");
  const [runId, setRunId] = useState(liveRunIdFromUrl ?? DEMO_RUN_ID);

  const client = useMemo(() => (mode === "live" ? makeLiveClient() : makeDemoClient()), [mode]);
  const runtime = useStudioRuntime({ client, runId });

  const switchToLive = () => {
    const requested = window.prompt("Run ID to attach to", liveRunIdFromUrl ?? "");
    if (!requested) return;
    setRunId(requested);
    setMode("live");
  };

  const switchToDemo = () => {
    setRunId(DEMO_RUN_ID);
    setMode("demo");
  };

  const isLiveHealthy = mode === "live" && (runtime.connection === "live" || runtime.connection === "complete");
  const isLiveBroken = mode === "live" && runtime.connection === "interrupted";

  return (
    <>
      <div
        style={{
          position: "fixed",
          zIndex: 50,
          bottom: 48,
          left: 16,
          display: "flex",
          alignItems: "center",
          gap: 8,
          padding: "6px 10px",
          background: "rgba(18, 18, 21, 0.95)",
          border: "1px solid var(--border-medium)",
          borderRadius: "var(--radius-md)",
          boxShadow: "var(--shadow-elevation)",
          backdropFilter: "blur(8px)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: mode === "demo" ? "var(--signal-flow)" : isLiveHealthy ? "var(--signal-proof)" : "var(--signal-hold)",
              display: "inline-block",
            }}
          />
          <span className="font-mono" style={{ fontSize: 10, fontWeight: 700, color: "var(--text-primary)" }}>
            {mode === "demo" ? "FIXTURE MODE" : isLiveBroken ? "LIVE — DISCONNECTED" : "LIVE BACKEND"}
          </span>
        </div>

        <div style={{ width: 1, height: 16, background: "var(--border-subtle)" }} />

        {mode === "demo" ? (
          <button onClick={switchToLive} style={{ ...pillButton, color: "var(--signal-flow)" }}>
            Attach Live Run
          </button>
        ) : (
          <button onClick={switchToDemo} style={pillButton}>
            Switch to Demo
          </button>
        )}

        <button
          onClick={() => runtime.onSelectSeq(0n)}
          style={pillButton}
        >
          Live Head
        </button>
      </div>

      <StudioApp {...runtime} />
    </>
  );
}

const pillButton: React.CSSProperties = {
  border: "1px solid var(--border-subtle)",
  borderRadius: "var(--radius-sm)",
  padding: "3px 8px",
  background: "var(--bg-card)",
  color: "var(--text-primary)",
  cursor: "pointer",
  fontSize: 10,
  fontWeight: 600,
};

createRoot(rootElement).render(<Observatory />);
