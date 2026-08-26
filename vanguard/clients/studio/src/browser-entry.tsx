import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { ColumnarEventStore } from "./store/event-store.js";
import { initialStudioFold, StudioFoldEngine } from "./store/fold.js";
import { INITIAL_SESSION_STATE } from "./store/session.js";
import { CSS_VARIABLES } from "./ui/tokens.js";
import { StudioApp } from "./ui/StudioApp.js";
import type { EventEnvelope } from "./contract/index.js";

const base = (seq: string, eventId: string, kind: string, payload: Record<string, unknown>): EventEnvelope => ({
  schemaVersion: "vg.4",
  eventId,
  scope: "episode",
  runId: "run-meta-dev-01",
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

function DemoObservatory() {
  const [store] = useState(() => new ColumnarEventStore());
  const [engine] = useState(() => new StudioFoldEngine());
  const [mode, setMode] = useState<"live" | "demo">("demo");
  const [isBackendOnline, setIsBackendOnline] = useState<boolean>(false);
  const [demoCount, setDemoCount] = useState(demoEvents.length);
  const [session, setSession] = useState(INITIAL_SESSION_STATE);
  const [eventVersion, setEventVersion] = useState(0);

  // Check Backend Health & Connect SSE
  useEffect(() => {
    let sse: EventSource | null = null;

    const checkHealth = async () => {
      try {
        const res = await fetch("/api/health");
        if (res.ok) {
          setIsBackendOnline(true);
          setMode("live");
          connectSSE();
        }
      } catch {
        setIsBackendOnline(false);
      }
    };

    const connectSSE = () => {
      try {
        sse = new EventSource("/api/events/stream");
        sse.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data) as EventEnvelope;
            store.append(parsed);
            setEventVersion((v) => v + 1);
          } catch (err) {
            console.error("SSE parse error", err);
          }
        };
        sse.onerror = () => {
          console.warn("SSE disconnected, polling fallback...");
        };
      } catch (e) {
        console.error("SSE init failed", e);
      }
    };

    checkHealth();

    return () => {
      if (sse) sse.close();
    };
  }, [store]);

  const rows = useMemo(() => {
    if (mode === "demo") {
      return store.appendBatch(demoEvents.slice(0, demoCount));
    }
    // Live mode
    return store.getAllRows();
  }, [mode, demoCount, store, eventVersion]);

  const liveFold = engine.foldAll(rows);
  const fold = session.isScrubbing ? engine.foldToSeq(session.selectedSeq, rows) : liveFold;

  const appendNext = () => setDemoCount((value) => Math.min(demoEvents.length, value + 1));
  const selectSeq = (seq: bigint) =>
    setSession((value) => ({
      ...value,
      selectedSeq: seq,
      isScrubbing: seq > 0n && seq < BigInt(rows.length),
    }));

  const resolveApproval = async (approvalId: string, decision: "approve" | "reject") => {
    if (mode === "live") {
      try {
        await fetch("/api/approvals/resolve", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ approvalId, decision }),
        });
      } catch (err) {
        console.error("Failed to submit live approval", err);
      }
    } else {
      setDemoCount((value) => Math.max(value, 11));
    }
  };

  return (
    <>
      {/* Floating Mode Switcher & Stepper Pill */}
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
              background: isBackendOnline ? "var(--signal-proof)" : "var(--signal-hold)",
              display: "inline-block",
            }}
          />
          <span className="font-mono" style={{ fontSize: 10, fontWeight: 700, color: "var(--text-primary)" }}>
            {mode === "live" ? "LIVE BACKEND" : "FIXTURE MODE"}
          </span>
        </div>

        <div style={{ width: 1, height: 16, background: "var(--border-subtle)" }} />

        {mode === "demo" ? (
          <>
            <button onClick={() => setDemoCount(5)} style={pillButton}>
              Reset
            </button>
            <button onClick={appendNext} disabled={demoCount >= demoEvents.length} style={pillButton}>
              Advance ({demoCount}/{demoEvents.length})
            </button>
          </>
        ) : (
          <button
            onClick={() => setMode("demo")}
            style={{ ...pillButton, color: "var(--signal-flow)" }}
          >
            Switch to Demo
          </button>
        )}

        <button
          onClick={() => setSession((value) => ({ ...value, selectedSeq: 0n, isScrubbing: false }))}
          style={pillButton}
        >
          Live Head
        </button>
      </div>

      <StudioApp
        fold={fold}
        rows={rows}
        latestSeq={liveFold.atSeq}
        session={session}
        onSelectSurface={(activeSurface) => setSession((value) => ({ ...value, activeSurface }))}
        onSelectSeq={selectSeq}
        onResolveApproval={resolveApproval}
      />
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

createRoot(rootElement).render(<DemoObservatory />);
