import { test } from "node:test";
import assert from "node:assert/strict";
import {
  FrontendAppController,
  InMemoryPersistenceAdapter,
  ProductPaths,
  CompatibilityNegotiator,
  ConfigurationResolver,
  DEFAULT_AGENTS,
  DEFAULT_WORKFLOWS,
  DEFAULT_PROVIDERS,
} from "../src/index.js";
import type { EventEnvelope } from "@aether/contracts";

test("Product Integration: Clean-Machine First-Run, Persistence, and Coding Flow", async () => {
  // 1. First-run Experience: Clean persistence store
  const persistence = new InMemoryPersistenceAdapter();
  const controller = new FrontendAppController({ persistence });

  // Verify default state initialization
  const s0 = controller.getState();
  assert.equal(s0.selectedAgentId, "coding-agent");
  assert.equal(s0.selectedWorkflowId, "default-turn-loop");
  assert.equal(s0.providers.length > 0, true);

  // 2. Configure provider, workspace, and model
  controller.selectWorkspace("/tmp/my-clean-repo");
  controller.selectAgent("coding-agent");
  controller.selectWorkflow("default-turn-loop");
  await persistence.saveSecureCredential("cred-openrouter", "sk-secret-key-12345");

  // Verify secrets are never exposed in state
  const credState = await persistence.getCredentialState("cred-openrouter");
  assert.equal(credState, "CONFIGURED");
  assert.ok(!JSON.stringify(controller.getState()).includes("sk-secret-key-12345"));

  // 3. Simulate Coding Run Flow: Ingest Goal, Diff, and Verification
  const runId = "run-prod-001";
  const goalEvent: EventEnvelope = {
    schemaVersion: "vg.4",
    eventId: "ev-01",
    scope: "episode",
    runId,
    traceId: "tr-01",
    spanId: "sp-01",
    seq: "1",
    occurredAt: "2026-08-30T10:00:00.000Z",
    recordedAt: "2026-08-30T10:00:00.000Z",
    principal: "operator",
    tenantId: "local",
    ownerId: "user",
    confidentiality: "public",
    retentionClass: "standard",
    trainability: "allowed",
    redactionStatus: "none",
    payload: {
      kind: "GoalDeclared",
      brief: "Fix failing unit tests in auth module",
    },
  };
  controller.ingestEnvelope(goalEvent);

  const diffEvent: EventEnvelope = {
    schemaVersion: "vg.4",
    eventId: "ev-02",
    scope: "episode",
    runId,
    traceId: "tr-01",
    spanId: "sp-02",
    seq: "2",
    occurredAt: "2026-08-30T10:00:01.000Z",
    recordedAt: "2026-08-30T10:00:01.000Z",
    principal: "process",
    tenantId: "local",
    ownerId: "user",
    confidentiality: "public",
    retentionClass: "standard",
    trainability: "allowed",
    redactionStatus: "none",
    payload: {
      kind: "ToolCallRequested",
      tool: "fs.write",
      filePath: "src/auth.ts",
      unifiedDiff: "--- src/auth.ts\n+++ src/auth.ts\n@@ -1,2 +1,2 @@\n-const valid = false;\n+const valid = true;\n",
    },
  };
  controller.ingestEnvelope(diffEvent);

  const verEvent: EventEnvelope = {
    schemaVersion: "vg.4",
    eventId: "ev-03",
    scope: "episode",
    runId,
    traceId: "tr-01",
    spanId: "sp-03",
    seq: "3",
    occurredAt: "2026-08-30T10:00:02.000Z",
    recordedAt: "2026-08-30T10:00:02.000Z",
    principal: "evaluator",
    tenantId: "local",
    ownerId: "user",
    confidentiality: "public",
    retentionClass: "standard",
    trainability: "allowed",
    redactionStatus: "none",
    payload: {
      kind: "VerificationSucceeded",
      testSuite: "auth-tests",
      passed: 5,
      failed: 0,
      detail: "All 5 authentication tests passed.",
    },
  };
  controller.ingestEnvelope(verEvent);

  // Verify projections folded correctly
  const s1 = controller.getState();
  assert.equal(s1.activeRunId, runId);
  assert.equal(s1.turns.length >= 1, true);
  assert.equal(s1.multiFileDiff.files.length, 1);
  assert.equal(s1.multiFileDiff.files[0]?.filePath, "src/auth.ts");
  assert.equal(s1.verificationSummaries.length, 1);
  assert.equal(s1.verificationSummaries[0]?.status, "pass");

  // 4. Simulate App Restart: create new controller instance with same persistence
  const restartedController = new FrontendAppController({ persistence });
  await restartedController.restoreFromPersistence();

  const sRestart = restartedController.getState();
  assert.equal(sRestart.currentWorkspace, "/tmp/my-clean-repo");
  assert.equal(sRestart.selectedAgentId, "coding-agent");
  assert.equal(sRestart.selectedWorkflowId, "default-turn-loop");
});
