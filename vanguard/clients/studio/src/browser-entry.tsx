import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { ColumnarEventStore } from "./store/event-store.js";
import { initialStudioFold, StudioFoldEngine } from "./store/fold.js";
import { INITIAL_SESSION_STATE } from "./store/session.js";
import { CSS_VARIABLES } from "./ui/tokens.js";
import { StudioApp } from "./ui/StudioApp.js";
import type { EventEnvelope } from "./contract/index.js";

const base = (seq: string, eventId: string, kind: string, payload: Record<string, unknown>): EventEnvelope => ({
  schemaVersion: "vg.4", eventId, scope: "episode", runId: "demo-observatory", traceId: "demo-trace", spanId: `demo-span-${seq}`,
  seq, occurredAt: new Date(Date.now() + Number(seq) * 1000).toISOString(), recordedAt: new Date().toISOString(), principal: "demo",
  tenantId: "local", ownerId: "local", confidentiality: "internal", retentionClass: "standard", trainability: "prohibited", redactionStatus: "none",
  payload: { kind, ...payload },
});

const demoEvents: EventEnvelope[] = [
  base("1", "demo-1", "EpisodeStarted", { repo: "~/aether-demo" }),
  base("2", "demo-2", "ObservationProduced", { text: "Observatory demo stream attached." }),
  base("3", "demo-3", "EffectStarted", { descriptor: "sha256:demo-read", action: "fs.read", durationMs: 42 }),
  base("4", "demo-4", "EffectCompleted", { descriptor: "sha256:demo-read", outcome: "satisfied", durationMs: 18 }),
  base("5", "demo-5", "BudgetCommitted", { tokens: 1840, costMicros: "412000" }),
  base("6", "demo-6", "ApprovalRequested", { approvalId: "approval-demo", action: "net.fetch", normalizedDiff: "GET https://example.test/fixture", argsDigest: "sha256:demo-args", descriptorDigest: "sha256:demo-network", expiresAt: new Date(Date.now() + 3600000).toISOString() }),
  base("7", "demo-7", "ApprovalResolved", { approvalId: "approval-demo", decision: "approved" }),
  base("8", "demo-8", "EpisodeCompleted", { outcome: "satisfied" }),
];

const rootElement = document.getElementById("root");
if (!rootElement) throw new Error("Missing #root element");
const style = document.createElement("style");
style.textContent = CSS_VARIABLES;
document.head.appendChild(style);

function DemoObservatory() {
  const [store] = useState(() => new ColumnarEventStore());
  const [engine] = useState(() => new StudioFoldEngine());
  const [count, setCount] = useState(5);
  const [session, setSession] = useState(INITIAL_SESSION_STATE);
  const rows = useMemo(() => store.appendBatch(demoEvents.slice(0, count)), [count, store]);
  const liveFold = engine.foldAll(rows);
  const fold = session.isScrubbing ? engine.foldToSeq(session.selectedSeq, rows) : liveFold;
  const appendNext = () => setCount((value) => Math.min(demoEvents.length, value + 1));
  const selectSeq = (seq: bigint) => setSession((value) => ({ ...value, selectedSeq: seq, isScrubbing: seq > 0n && seq < BigInt(count) }));
  const resolveApproval = async () => { setCount((value) => Math.max(value, 7)); };
  return <>
    <div style={{ position: "fixed", zIndex: 20, bottom: 48, left: 16, display: "flex", gap: 6, padding: 6, background: "rgba(11, 23, 27, .94)", border: "1px solid var(--border-medium)", borderRadius: 8, boxShadow: "var(--shadow-glow)" }}>
      <button onClick={() => setCount(5)} style={demoButton}>Reset fixture</button>
      <button onClick={appendNext} disabled={count >= demoEvents.length} style={demoButton}>Advance event ({count}/{demoEvents.length})</button>
      <button onClick={() => setSession((value) => ({ ...value, selectedSeq: 0n, isScrubbing: false }))} style={demoButton}>Return live</button>
    </div>
    <StudioApp fold={fold} rows={rows} latestSeq={liveFold.atSeq} session={session} onSelectSurface={(activeSurface) => setSession((value) => ({ ...value, activeSurface }))} onSelectSeq={selectSeq} onResolveApproval={resolveApproval} />
  </>;
}

const demoButton: React.CSSProperties = { border: "1px solid var(--border-medium)", borderRadius: 5, padding: "6px 9px", background: "var(--bg-card)", color: "var(--text-primary)", cursor: "pointer", fontSize: 11 };
createRoot(rootElement).render(<DemoObservatory />);
