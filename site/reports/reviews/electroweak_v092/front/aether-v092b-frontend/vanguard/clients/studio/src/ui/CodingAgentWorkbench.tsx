import React, { useState } from "react";
import type { StudioFold } from "../store/fold.js";
import { formatDigestShort, formatMicrosToUsd } from "../store/session.js";

type CodingTask = {
  id: string;
  title: string;
  description: string;
  status: "idle" | "running" | "evaluating" | "solved" | "failed";
  targetFile: string;
  initialCode: string;
  modifiedCode: string;
  unifiedDiff: string;
  testOutput: string;
  turnCount: number;
  tokensUsed: number;
  costMicros: number;
  evaluatorVerdict: "1" | "0" | "pending";
};

const DEMO_TASKS: CodingTask[] = [
  {
    id: "task-001-race-fix",
    title: "M-4 Task: Fix Memory Store Lease Race Condition",
    description: "Prevent S7 governor lease leak when adapter raises unexpected connection error before S10 commit.",
    status: "solved",
    targetFile: "vanguard/packages/kernel/dispatch.py",
    initialCode: `# Vulnerable S11 Release placement
try:
    outcome = adapter.execute(request)
    settlement = self._governor.commit(lease, outcome.actual_cost)
    self._governor.release(lease) # BUG: missed on exception
except Exception as exc:
    outcome = AdapterOutcome("error", Occurrence.UNDETERMINABLE)`,
    modifiedCode: `# Corrected S11 Release in mandatory finally block (K-06)
try:
    outcome = adapter.execute(request)
    settlement = self._governor.commit(lease, outcome.actual_cost)
finally:
    self._governor.release(lease) # K-06: release on EVERY exit path`,
    unifiedDiff: `--- a/vanguard/packages/kernel/dispatch.py
+++ b/vanguard/packages/kernel/dispatch.py
@@ -315,5 +315,6 @@
         outcome = adapter.execute(request)
         settlement = self._governor.commit(lease, outcome.actual_cost)
-        self._governor.release(lease)
+    finally:
+        # K-06: guaranteed lease reclamation before S12 emit
+        self._governor.release(lease)`,
    testOutput: `test_s11_release_on_adapter_raise (test.kernel.test_dispatch.TestDispatch) ... ok
test_k06_guaranteed_lease_reclaim ... ok
----------------------------------------------------------------------
Ran 2 tests in 0.042s
OK (Verified by Exterior Evaluator UID 10002; Verdict Y(tau) = 1)`,
    turnCount: 3,
    tokensUsed: 2420,
    costMicros: 484000,
    evaluatorVerdict: "1",
  },
  {
    id: "task-002-ast-refactor",
    title: "M-4 Task: AST-Aware Surgical Syntax Patching",
    description: "Ensure whitespace-invariant replacements preserve docstrings and type annotations.",
    status: "running",
    targetFile: "vanguard/packages/domain/canonicalisation/jcs.py",
    initialCode: `def canonical_bytes(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True).encode("utf-8")`,
    modifiedCode: `def canonical_bytes(payload: Any) -> bytes:
    # RFC 8785 JSON Canonicalization Scheme (JCS) strict formatting
    return json.dumps(payload, ensure_ascii=False, allow_nan=False, indent=None, separators=(',', ':'), sort_keys=True).encode("utf-8")`,
    unifiedDiff: `--- a/vanguard/packages/domain/canonicalisation/jcs.py
+++ b/vanguard/packages/domain/canonicalisation/jcs.py
@@ -1,3 +1,4 @@
 def canonical_bytes(payload: Any) -> bytes:
-    return json.dumps(payload, sort_keys=True).encode("utf-8")
+    # RFC 8785 JSON Canonicalization Scheme (JCS)
+    return json.dumps(payload, ensure_ascii=False, allow_nan=False, indent=None, separators=(',', ':'), sort_keys=True).encode("utf-8")`,
    testOutput: `Running test.domain.test_jcs ... in progress`,
    turnCount: 2,
    tokensUsed: 1680,
    costMicros: 310000,
    evaluatorVerdict: "pending",
  },
];

export const CodingAgentWorkbench: React.FC<{
  readonly fold: StudioFold;
  readonly onResolveApproval?: (approvalId: string, decision: "approve" | "reject") => Promise<void>;
}> = ({ fold, onResolveApproval }) => {
  const [selectedTask, setSelectedTask] = useState<CodingTask>(DEMO_TASKS[0]);
  const [activeTab, setActiveTab] = useState<"diff" | "source" | "context" | "exact_io" | "tests">("diff");
  const [promptInput, setPromptInput] = useState<string>("");
  const [isLiveRunning, setIsLiveRunning] = useState<boolean>(false);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%", gap: 12 }}>
      {/* Top Coding Control Bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          background: "var(--bg-surface)",
          padding: "8px 16px",
          borderRadius: "var(--radius-md)",
          border: "1px solid var(--border-subtle)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <span style={{ fontWeight: 700, fontSize: 13, color: "var(--text-primary)" }}>
            M-4 CODING AGENT WORKBENCH
          </span>
          <select
            value={selectedTask.id}
            onChange={(e) => {
              const found = DEMO_TASKS.find((t) => t.id === e.target.value);
              if (found) setSelectedTask(found);
            }}
            style={{
              background: "var(--bg-card)",
              border: "1px solid var(--border-subtle)",
              borderRadius: "var(--radius-sm)",
              padding: "4px 8px",
              color: "var(--text-primary)",
              fontSize: 11,
              fontWeight: 600,
            }}
          >
            {DEMO_TASKS.map((t) => (
              <option key={t.id} value={t.id}>
                {t.title} ({t.status.toUpperCase()})
              </option>
            ))}
          </select>
        </div>

        {/* Task Metrics & Verdict */}
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Verdict Y(τ):</span>
            <span
              className="badge-mono"
              style={{
                background: selectedTask.evaluatorVerdict === "1" ? "rgba(74, 222, 128, 0.15)" : "rgba(251, 191, 36, 0.15)",
                color: selectedTask.evaluatorVerdict === "1" ? "var(--signal-proof)" : "var(--signal-hold)",
                fontWeight: 700,
              }}
            >
              {selectedTask.evaluatorVerdict === "1" ? "VERIFIED (1)" : "PENDING (0)"}
            </span>
          </div>

          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Turns:</span>
            <span className="font-mono" style={{ fontSize: 12, fontWeight: 700, color: "var(--text-primary)" }}>
              {selectedTask.turnCount}
            </span>
          </div>

          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>Tokens:</span>
            <span className="font-mono" style={{ fontSize: 12, fontWeight: 700, color: "var(--signal-flow)" }}>
              {selectedTask.tokensUsed.toLocaleString()}
            </span>
          </div>

          <button
            onClick={() => setIsLiveRunning((v) => !v)}
            style={{
              background: isLiveRunning ? "var(--signal-deny)" : "var(--signal-flow)",
              color: "#000",
              border: "none",
              borderRadius: "var(--radius-sm)",
              padding: "6px 14px",
              fontSize: 11,
              fontWeight: 700,
              cursor: "pointer",
            }}
          >
            {isLiveRunning ? "PAUSE STEPPER" : "RUN CODING TURN"}
          </button>
        </div>
      </div>

      {/* Main Dual-Pane Layout */}
      <div style={{ display: "grid", gridTemplateColumns: "280px 1fr 340px", gap: 12, flex: 1, minHeight: 0 }}>
        {/* Left Pane: File Tree & L1-L5 Context */}
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
          <div style={{ padding: "10px 12px", borderBottom: "1px solid var(--border-subtle)", fontWeight: 700, fontSize: 11, color: "var(--text-secondary)" }}>
            WORKSPACE &amp; CONTEXT STACK
          </div>

          <div style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10, overflowY: "auto", flex: 1 }}>
            {/* Target File */}
            <div>
              <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 4 }}>
                Active Target File
              </div>
              <div
                className="font-mono"
                style={{
                  fontSize: 11,
                  background: "var(--bg-card)",
                  padding: "6px 8px",
                  borderRadius: "var(--radius-sm)",
                  border: "1px solid var(--border-subtle)",
                  color: "var(--signal-flow)",
                  wordBreak: "break-all",
                }}
              >
                {selectedTask.targetFile}
              </div>
            </div>

            {/* Context Layers L1–L5 Breakdown */}
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase" }}>
                Context Compiler (L1–L5)
              </div>
              {[
                { layer: "L1", name: "System Role", tokens: 340, status: "Cached" },
                { layer: "L2", name: "AST Repo Map", tokens: 720, status: "Cached" },
                { layer: "L3", name: "Tool Contracts", tokens: 480, status: "Active" },
                { layer: "L4", name: "Observations", tokens: 280, status: "Dynamic" },
                { layer: "L5", name: "Turn Dialogue", tokens: 600, status: "Evictable" },
              ].map((l) => (
                <div
                  key={l.layer}
                  style={{
                    background: "var(--bg-panel)",
                    padding: "6px 8px",
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid var(--border-subtle)",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    <span className="font-mono" style={{ fontSize: 10, fontWeight: 700, color: "var(--signal-flow)" }}>
                      {l.layer}
                    </span>
                    <span style={{ fontSize: 11, color: "var(--text-primary)" }}>{l.name}</span>
                  </div>
                  <span className="font-mono" style={{ fontSize: 10, color: "var(--text-muted)" }}>
                    {l.tokens} tok
                  </span>
                </div>
              ))}
            </div>

            {/* Exact Model I/O Stamping */}
            <div style={{ background: "var(--bg-card)", padding: 8, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: "var(--signal-proof)", marginBottom: 4 }}>
                EXACT MODEL I/O PROVENANCE (C-01)
              </div>
              <div className="font-mono" style={{ fontSize: 10, color: "var(--text-secondary)" }}>
                <div>Prompt Ref: <span style={{ color: "var(--signal-flow)" }}>sha256:prm_9a8b</span></div>
                <div>Output Ref: <span style={{ color: "var(--signal-flow)" }}>sha256:out_4c3d</span></div>
                <div>TTFT: <span style={{ color: "var(--text-primary)" }}>412ms</span></div>
              </div>
            </div>
          </div>
        </div>

        {/* Center Pane: Surgical Diff & Interactive Editor */}
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
          {/* Editor Header Navigation */}
          <div
            style={{
              display: "flex",
              borderBottom: "1px solid var(--border-subtle)",
              background: "var(--bg-surface)",
              padding: "0 8px",
            }}
          >
            {[
              { id: "diff", label: "Surgical Unified Diff" },
              { id: "source", label: "Resulting Source Code" },
              { id: "exact_io", label: "Exact Model Input/Output" },
              { id: "tests", label: "Test Suite Output" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                style={{
                  background: activeTab === tab.id ? "var(--bg-panel)" : "transparent",
                  border: "none",
                  borderBottom: activeTab === tab.id ? "2px solid var(--signal-flow)" : "2px solid transparent",
                  padding: "10px 14px",
                  color: activeTab === tab.id ? "var(--text-primary)" : "var(--text-muted)",
                  fontSize: 11,
                  fontWeight: 600,
                  cursor: "pointer",
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Editor Content Body */}
          <div style={{ flex: 1, padding: 12, overflowY: "auto", background: "var(--bg-canvas)" }}>
            {activeTab === "diff" && (
              <pre
                className="font-mono"
                style={{
                  margin: 0,
                  fontSize: 11,
                  lineHeight: 1.5,
                  color: "var(--text-primary)",
                  whiteSpace: "pre-wrap",
                }}
              >
                {selectedTask.unifiedDiff.split("\n").map((line, i) => {
                  let color = "var(--text-secondary)";
                  let bg = "transparent";
                  if (line.startsWith("+") && !line.startsWith("+++")) {
                    color = "var(--signal-proof)";
                    bg = "rgba(74, 222, 128, 0.08)";
                  } else if (line.startsWith("-") && !line.startsWith("---")) {
                    color = "var(--signal-deny)";
                    bg = "rgba(248, 113, 113, 0.08)";
                  } else if (line.startsWith("@@")) {
                    color = "var(--signal-void)";
                  }
                  return (
                    <div key={i} style={{ color, background: bg, padding: "1px 4px" }}>
                      {line}
                    </div>
                  );
                })}
              </pre>
            )}

            {activeTab === "source" && (
              <pre
                className="font-mono"
                style={{
                  margin: 0,
                  fontSize: 11,
                  lineHeight: 1.5,
                  color: "var(--text-primary)",
                  whiteSpace: "pre-wrap",
                }}
              >
                {selectedTask.modifiedCode}
              </pre>
            )}

            {activeTab === "exact_io" && (
              <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                <div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 4 }}>
                    Exact Assembled Bundle (Prompt Input)
                  </div>
                  <pre
                    className="font-mono"
                    style={{
                      background: "var(--bg-panel)",
                      padding: 8,
                      borderRadius: "var(--radius-sm)",
                      border: "1px solid var(--border-subtle)",
                      fontSize: 10,
                      color: "var(--text-secondary)",
                      margin: 0,
                    }}
                  >
                    {JSON.stringify(
                      {
                        system: "AETHER Autonomous Coding Engine v0.7",
                        taskBrief: selectedTask.description,
                        target: selectedTask.targetFile,
                        tools: ["fs.read", "fs.patch", "proc.exec", "git.status"],
                      },
                      null,
                      2
                    )}
                  </pre>
                </div>

                <div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 4 }}>
                    Raw Structured Model Output (Before Downstream Parsing)
                  </div>
                  <pre
                    className="font-mono"
                    style={{
                      background: "var(--bg-panel)",
                      padding: 8,
                      borderRadius: "var(--radius-sm)",
                      border: "1px solid var(--border-subtle)",
                      fontSize: 10,
                      color: "var(--signal-flow)",
                      margin: 0,
                    }}
                  >
                    {JSON.stringify(
                      {
                        action: "fs.patch",
                        args: {
                          file: selectedTask.targetFile,
                          diff: selectedTask.unifiedDiff,
                        },
                        note: "Enforce K-06 guaranteed lease release in finally block",
                      },
                      null,
                      2
                    )}
                  </pre>
                </div>
              </div>
            )}

            {activeTab === "tests" && (
              <pre
                className="font-mono"
                style={{
                  margin: 0,
                  fontSize: 11,
                  lineHeight: 1.5,
                  color: "var(--signal-proof)",
                  whiteSpace: "pre-wrap",
                }}
              >
                {selectedTask.testOutput}
              </pre>
            )}
          </div>

          {/* Interactive Agent Command / Chat Input */}
          <div
            style={{
              padding: 8,
              borderTop: "1px solid var(--border-subtle)",
              background: "var(--bg-surface)",
              display: "flex",
              gap: 8,
            }}
          >
            <input
              type="text"
              placeholder="Inject steering instruction, inspect variable, or declare next goal..."
              value={promptInput}
              onChange={(e) => setPromptInput(e.target.value)}
              style={{
                flex: 1,
                background: "var(--bg-panel)",
                border: "1px solid var(--border-subtle)",
                borderRadius: "var(--radius-sm)",
                padding: "6px 10px",
                color: "var(--text-primary)",
                fontSize: 11,
              }}
            />
            <button
              onClick={() => {
                if (promptInput.trim()) {
                  setPromptInput("");
                }
              }}
              style={{
                background: "var(--text-primary)",
                color: "#000",
                border: "none",
                borderRadius: "var(--radius-sm)",
                padding: "6px 12px",
                fontSize: 11,
                fontWeight: 700,
                cursor: "pointer",
              }}
            >
              SEND
            </button>
          </div>
        </div>

        {/* Right Pane: Cryptographic Approval Desk & Live Diagnostics */}
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
          <div style={{ padding: "10px 12px", borderBottom: "1px solid var(--border-subtle)", fontWeight: 700, fontSize: 11, color: "var(--text-secondary)" }}>
            ED25519 HUMAN GOVERNANCE &amp; APPROVALS
          </div>

          <div style={{ padding: 12, display: "flex", flexDirection: "column", gap: 12, overflowY: "auto", flex: 1 }}>
            {fold.pendingApproval ? (
              <div style={{ background: "rgba(251, 191, 36, 0.1)", border: "1px solid var(--signal-hold)", padding: 12, borderRadius: "var(--radius-md)" }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "var(--signal-hold)", marginBottom: 6 }}>
                  APPROVAL REQUIRED (S5 GATE)
                </div>
                <div className="font-mono" style={{ fontSize: 10, color: "var(--text-secondary)", marginBottom: 8 }}>
                  <div>Action: <span style={{ color: "var(--text-primary)" }}>{fold.pendingApproval.action}</span></div>
                  <div>Descriptor: <span style={{ color: "var(--signal-flow)" }}>{formatDigestShort(fold.pendingApproval.descriptorDigest)}</span></div>
                </div>

                <div style={{ display: "flex", gap: 8 }}>
                  <button
                    onClick={() => onResolveApproval?.(fold.pendingApproval!.approvalId, "approve")}
                    style={{
                      flex: 1,
                      background: "var(--signal-proof)",
                      color: "#000",
                      border: "none",
                      padding: "6px",
                      borderRadius: "var(--radius-sm)",
                      fontWeight: 700,
                      fontSize: 11,
                      cursor: "pointer",
                    }}
                  >
                    SIGN &amp; APPROVE (Ed25519)
                  </button>
                  <button
                    onClick={() => onResolveApproval?.(fold.pendingApproval!.approvalId, "reject")}
                    style={{
                      flex: 1,
                      background: "var(--signal-deny)",
                      color: "#000",
                      border: "none",
                      padding: "6px",
                      borderRadius: "var(--radius-sm)",
                      fontWeight: 700,
                      fontSize: 11,
                      cursor: "pointer",
                    }}
                  >
                    DENY
                  </button>
                </div>
              </div>
            ) : (
              <div style={{ background: "var(--bg-panel)", padding: 10, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }}>
                <div style={{ fontSize: 10, color: "var(--signal-proof)", fontWeight: 700 }}>
                  GOVERNANCE GATE: CLEAR
                </div>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
                  No pending suspensions. All previous mutations cryptographically signed by Operator.
                </div>
              </div>
            )}

            {/* Test Run Status */}
            <div>
              <div style={{ fontSize: 10, color: "var(--text-muted)", textTransform: "uppercase", marginBottom: 4 }}>
                Exterior Evaluator Daemon (UID 10002)
              </div>
              <div style={{ background: "var(--bg-panel)", padding: 8, borderRadius: "var(--radius-sm)", border: "1px solid var(--border-subtle)" }}>
                <div className="font-mono" style={{ fontSize: 10, color: "var(--text-secondary)" }}>
                  <div>Daemon Port: <span style={{ color: "var(--signal-flow)" }}>/run/evaluator.sock</span></div>
                  <div>Protocol: <span style={{ color: "var(--text-primary)" }}>JSON-RPC over UDS</span></div>
                  <div>Oracle Hash: <span style={{ color: "var(--signal-flow)" }}>sha256:orc_7f2e</span></div>
                  <div>Verdict Signature: <span style={{ color: "var(--signal-proof)" }}>ed25519_valid</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
