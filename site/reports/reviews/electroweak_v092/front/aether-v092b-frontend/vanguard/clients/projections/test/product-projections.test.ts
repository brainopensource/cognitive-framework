import { test } from "node:test";
import assert from "node:assert/strict";
import type { EventEnvelope } from "@aether/contracts";
import {
  reduceMultiFileDiff,
  parseUnifiedDiffToFiles,
  reduceVerificationSummaries,
  reduceResearchSummary,
  reduceMultiAgentExecution,
  reconcileOfflineStream,
  evaluateStartupReadiness,
} from "../src/index.js";

function makeEnv(
  eventId: string,
  seq: string,
  payload: Record<string, unknown> & { kind: string },
  runId = "run-1"
): EventEnvelope {
  return {
    schemaVersion: "vg.4",
    eventId,
    scope: "episode",
    runId,
    traceId: "t-1",
    spanId: `s-${seq}`,
    seq,
    occurredAt: new Date().toISOString(),
    recordedAt: new Date().toISOString(),
    principal: "test",
    tenantId: "t",
    ownerId: "o",
    confidentiality: "internal",
    retentionClass: "standard",
    trainability: "prohibited",
    redactionStatus: "none",
    payload,
  };
}

test("parseUnifiedDiffToFiles splits multi-file git diff accurately", () => {
  const sampleDiff = `diff --git a/src/a.ts b/src/a.ts
--- a/src/a.ts
+++ b/src/a.ts
@@ -1,3 +1,4 @@
 import foo;
+import bar;
 const x = 1;
diff --git a/src/b.ts b/src/b.ts
--- a/src/b.ts
+++ b/src/b.ts
@@ -10,2 +10,1 @@
-console.log("old");
+console.log("new");
`;

  const files = parseUnifiedDiffToFiles(sampleDiff, "PROPOSED");
  assert.equal(files.length, 2);
  assert.equal(files[0]?.filePath, "src/a.ts");
  assert.equal(files[0]?.additions, 1);
  assert.equal(files[0]?.deletions, 0);
  assert.equal(files[1]?.filePath, "src/b.ts");
  assert.equal(files[1]?.additions, 1);
  assert.equal(files[1]?.deletions, 1);
});

test("reduceMultiFileDiff resolves 5 canonical mutation states correctly", () => {
  const baseEvent = makeEnv("00000000-0000-0000-0000-000000000001", "1", {
    kind: "ApprovalRequested",
    approvalId: "app-1",
    action: "Modify file",
    unifiedDiff: "--- a/x.ts\n+++ b/x.ts\n+const a = 1;",
  });

  const proposed = reduceMultiFileDiff([baseEvent]);
  assert.equal(proposed.overallStatus, "PROPOSED");

  const approved = reduceMultiFileDiff([
    baseEvent,
    makeEnv("00000000-0000-0000-0000-000000000002", "2", {
      kind: "ApprovalResolved",
      approvalId: "app-1",
      resolution: "approved",
    }),
  ]);
  assert.equal(approved.overallStatus, "APPROVED");

  const applied = reduceMultiFileDiff([
    baseEvent,
    makeEnv("00000000-0000-0000-0000-000000000002", "2", {
      kind: "ApprovalResolved",
      approvalId: "app-1",
      resolution: "approved",
    }),
    makeEnv("00000000-0000-0000-0000-000000000003", "3", {
      kind: "PatchApplied",
      approvalId: "app-1",
    }),
  ]);
  assert.equal(applied.overallStatus, "APPLIED");

  const verified = reduceMultiFileDiff([
    baseEvent,
    makeEnv("00000000-0000-0000-0000-000000000002", "2", {
      kind: "ApprovalResolved",
      approvalId: "app-1",
      resolution: "approved",
    }),
    makeEnv("00000000-0000-0000-0000-000000000003", "3", {
      kind: "PatchApplied",
      approvalId: "app-1",
    }),
    makeEnv("00000000-0000-0000-0000-000000000004", "4", {
      kind: "VerificationPassed",
    }),
  ]);
  assert.equal(verified.overallStatus, "VERIFIED");
});

test("reduceVerificationSummaries captures test and lint runs accurately", () => {
  const events: EventEnvelope[] = [
    makeEnv("00000000-0000-0000-0000-000000000001", "1", {
      kind: "TestExecuted",
      checkType: "tests",
      command: "npm test",
      passedCount: 42,
      failedCount: 0,
      durationMs: 320,
      status: "passed",
    }),
    makeEnv("00000000-0000-0000-0000-000000000002", "2", {
      kind: "LintExecuted",
      checkType: "lint",
      command: "eslint .",
      status: "passed",
      durationMs: 110,
    }),
  ];

  const summaries = reduceVerificationSummaries(events);
  assert.equal(summaries.length, 2);
  assert.equal(summaries[0]?.kind, "tests");
  assert.equal(summaries[0]?.status, "pass");
  assert.equal(summaries[0]?.passedCount, 42);
  assert.equal(summaries[1]?.kind, "lint");
  assert.equal(summaries[1]?.status, "pass");
});

test("reduceResearchSummary extracts citations and claims without fabrication", () => {
  const events: EventEnvelope[] = [
    makeEnv("00000000-0000-0000-0000-000000000001", "1", {
      kind: "CitationAdded",
      sourceTitle: "RFC 9110 HTTP Semantics",
      sourceUrl: "https://rfc-editor.org/rfc/rfc9110",
      citationText: "HTTP status code 429 indicates rate limiting.",
      confidence: 0.98,
    }),
  ];

  const research = reduceResearchSummary(events);
  assert.equal(research.totalSources, 1);
  assert.equal(research.citations[0]?.sourceTitle, "RFC 9110 HTTP Semantics");
  assert.equal(research.citations[0]?.confidence, 0.98);
});

test("reconcileOfflineStream deduplicates events and maintains monotonic sequence", () => {
  const existing: EventEnvelope[] = [
    makeEnv("00000000-0000-0000-0000-000000000001", "1", { kind: "A" }, "r1"),
    makeEnv("00000000-0000-0000-0000-000000000002", "2", { kind: "B" }, "r1"),
  ];

  const incoming: EventEnvelope[] = [
    makeEnv("00000000-0000-0000-0000-000000000002", "2", { kind: "B" }, "r1"),
    makeEnv("00000000-0000-0000-0000-000000000003", "3", { kind: "C" }, "r1"),
  ];

  const reconciled = reconcileOfflineStream(existing, incoming, "2");
  assert.equal(reconciled.length, 3);
  assert.equal(
    reconciled.map((e) => e.eventId).join(","),
    "00000000-0000-0000-0000-000000000001,00000000-0000-0000-0000-000000000002,00000000-0000-0000-0000-000000000003"
  );
});

test("evaluateStartupReadiness detects missing dependencies accurately", () => {
  const unconfigured = evaluateStartupReadiness({
    runtimeConnected: false,
    daemonStatus: null,
    providers: [],
    activeWorkspace: "",
    activeAgentOrWorkflowId: "",
  });
  assert.equal(unconfigured.isReady, false);
  assert.equal(unconfigured.nextRequiredStep, "runtime");

  const ready = evaluateStartupReadiness({
    runtimeConnected: true,
    daemonStatus: { status: "running", socketPath: "/tmp/vg.sock" },
    providers: [
      {
        id: "p1",
        name: "OpenRouter",
        type: "openrouter",
        credentialKeyRef: "key-1",
        credentialState: "CONFIGURED",
        models: [{ id: "m1", name: "Model 1" }],
        selectedModel: "m1",
        enabled: true,
        isDefault: true,
      },
    ],
    activeWorkspace: "/home/user/repo",
    activeAgentOrWorkflowId: "coding-agent",
  });
  assert.equal(ready.isReady, true);
  assert.equal(ready.nextRequiredStep, undefined);
});
