import { test } from "node:test";
import assert from "node:assert/strict";
import {
  FrontendAppController,
  InMemoryPersistenceAdapter,
} from "../src/index.js";
import type { EventEnvelope } from "@aether/contracts";

function makeEnv(eventId: string, seq: string, payload: Record<string, unknown> & { kind: string }, runId = "run-1"): EventEnvelope {
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

test("FrontendAppController manages providers, models, and credentials safely", async () => {
  const persistence = new InMemoryPersistenceAdapter();
  const ctrl = new FrontendAppController({ persistence });

  assert.equal(ctrl.getState().providers.length >= 3, true);

  const newId = ctrl.addProvider({
    name: "Custom Gateway",
    type: "custom",
    baseUrl: "https://api.custom.ai",
    credentialKeyRef: "cred-custom-1",
    credentialState: "NOT_CONFIGURED",
    models: [{ id: "custom-model-1", name: "Custom 1" }],
    selectedModel: "custom-model-1",
    enabled: true,
    isDefault: false,
  });

  assert.equal(ctrl.getState().providers.some((p) => p.id === newId), true);

  // Set secret credential
  await ctrl.setProviderCredential(newId, "sk-test-secret-12345");
  const validation = await ctrl.validateProvider(newId);
  assert.equal(validation.ok, true);

  const updatedProvider = ctrl.getState().providers.find((p) => p.id === newId);
  assert.equal(updatedProvider?.credentialState, "CONFIGURED");

  // Ensure secrets are never exposed on the provider object
  assert.equal((updatedProvider as any).secret, undefined);
  assert.equal((updatedProvider as any).apiKey, undefined);

  // Delete credential
  await ctrl.deleteProviderCredential(newId);
  const recheckProvider = ctrl.getState().providers.find((p) => p.id === newId);
  assert.equal(recheckProvider?.credentialState, "NOT_CONFIGURED");
});

test("FrontendAppController auto-saves and restores drafts per conversation", async () => {
  const persistence = new InMemoryPersistenceAdapter();
  const ctrl = new FrontendAppController({ persistence });

  const convId = ctrl.getState().activeConversationId;
  ctrl.setConversationDraft("Explain quantum electrodynamics");

  assert.equal(ctrl.getState().conversations.find((c) => c.id === convId)?.draft, "Explain quantum electrodynamics");
  assert.equal(await persistence.loadDraft(convId), "Explain quantum electrodynamics");

  // Switch conversation
  ctrl.newChat();
  const nextConvId = ctrl.getState().activeConversationId;
  assert.notEqual(nextConvId, convId);
  assert.equal(ctrl.getState().conversations.find((c) => c.id === nextConvId)?.draft, "");

  // Switch back
  ctrl.selectConversation(convId);
  assert.equal(ctrl.getState().conversations.find((c) => c.id === convId)?.draft, "Explain quantum electrodynamics");
});

test("FrontendAppController folds mutation, verification, and research events into state", () => {
  const persistence = new InMemoryPersistenceAdapter();
  const ctrl = new FrontendAppController({ persistence });

  ctrl.ingestEnvelope(
    makeEnv("00000000-0000-0000-0000-000000000001", "1", {
      kind: "ApprovalRequested",
      approvalId: "app-42",
      action: "Modify router",
      unifiedDiff: "--- a/router.ts\n+++ b/router.ts\n+export const route = 1;",
    })
  );

  assert.equal(ctrl.getState().multiFileDiff.overallStatus, "PROPOSED");
  assert.equal(ctrl.getState().multiFileDiff.files.length, 1);
  assert.equal(ctrl.getState().multiFileDiff.files[0]?.filePath, "router.ts");

  ctrl.ingestEnvelope(
    makeEnv("00000000-0000-0000-0000-000000000002", "2", {
      kind: "CitationAdded",
      sourceTitle: "RFC 7230",
      sourceUrl: "https://tools.ietf.org/html/rfc7230",
      citationText: "HTTP/1.1 Message Syntax and Routing",
    })
  );

  assert.equal(ctrl.getState().researchSummary.totalSources, 1);
  assert.equal(ctrl.getState().researchSummary.citations[0]?.sourceTitle, "RFC 7230");

  ctrl.ingestEnvelope(
    makeEnv("00000000-0000-0000-0000-000000000003", "3", {
      kind: "TestExecuted",
      checkType: "tests",
      command: "cargo test",
      passedCount: 10,
      failedCount: 0,
      status: "passed",
    })
  );

  assert.equal(ctrl.getState().verificationSummaries.length, 1);
  assert.equal(ctrl.getState().verificationSummaries[0]?.passedCount, 10);
});
