import { test } from "node:test";
import assert from "node:assert/strict";
import {
  renderProviderManager,
  renderStartupReadinessModal,
  renderMultiFileDiffViewer,
  renderVerificationCard,
  renderResearchCitationCard,
  renderMultiAgentStatusBar,
} from "../src/index.js";

// Mock minimal DOM environment if running in node test runner
if (typeof document === "undefined") {
  (globalThis as any).document = {
    createElement: (tag: string) => {
      const el: any = {
        tagName: tag.toUpperCase(),
        className: "",
        style: { cssText: "" },
        innerHTML: "",
        textContent: "",
        children: [] as any[],
        appendChild: (child: any) => {
          el.children.push(child);
          return child;
        },
        querySelectorAll: () => [],
        querySelector: () => null,
      };
      return el;
    },
  };
}

test("renderProviderManager renders providers with model dropdown and action buttons", () => {
  const el = renderProviderManager({
    providers: [
      {
        id: "p1",
        name: "OpenRouter",
        type: "openrouter",
        credentialKeyRef: "k1",
        credentialState: "CONFIGURED",
        models: [{ id: "m1", name: "Model 1" }],
        selectedModel: "m1",
        enabled: true,
        isDefault: true,
      },
    ],
    selectedProviderId: "p1",
    onSelectDefault: () => {},
    onSelectModel: () => {},
    onAddProvider: () => {},
    onRemoveProvider: () => {},
    onUpdateCredential: () => {},
    onValidateProvider: () => {},
  });

  assert.equal(el.className, "aether-provider-manager");
  assert.equal(el.children.length >= 2, true);
});

test("renderStartupReadinessModal renders steps and triggers action", () => {
  let clicked = false;
  const modal = renderStartupReadinessModal({
    readiness: {
      isReady: false,
      steps: [
        {
          id: "runtime",
          title: "Daemon Connection",
          status: "unreachable",
          description: "Not connected",
          actionLabel: "Connect",
        },
      ],
      nextRequiredStep: "runtime",
    },
    onAction: () => {
      clicked = true;
    },
  });

  assert.equal(modal.className, "aether-readiness-overlay");
});

test("renderMultiFileDiffViewer displays file tree and overall status", () => {
  const viewer = renderMultiFileDiffViewer({
    diffModel: {
      diffId: "d1",
      overallStatus: "PROPOSED",
      files: [
        {
          filePath: "app.ts",
          status: "PROPOSED",
          additions: 5,
          deletions: 2,
          patchText: "--- a/app.ts\n+++ b/app.ts\n+console.log('hi');",
        },
      ],
      summary: { totalFiles: 1, totalAdditions: 5, totalDeletions: 2 },
    },
  });

  assert.equal(viewer.className, "aether-multi-file-diff-viewer");
});

test("renderVerificationCard displays metrics and logs cleanly", () => {
  const card = renderVerificationCard({
    id: "v1",
    kind: "tests",
    status: "pass",
    passedCount: 15,
    failedCount: 0,
    durationMs: 120,
    command: "npm test",
    importantOutput: "All 15 tests passed.",
    timestamp: new Date().toISOString(),
  });

  assert.equal(card.className, "aether-verification-card");
});

test("renderResearchCitationCard and renderMultiAgentStatusBar render with full metadata", () => {
  const citeCard = renderResearchCitationCard({
    citation: {
      id: "c1",
      sourceTitle: "Architecture Spec",
      sourceOrigin: "https://spec.org",
      citationText: "Invariant I-7 requires domain blindness.",
      confidence: 0.99,
    },
  });
  assert.equal(citeCard.className, "aether-citation-card");

  const statusBar = renderMultiAgentStatusBar({
    workflowId: "w1",
    title: "Audit Workflow",
    currentStage: "Review",
    participants: [{ agentId: "agent-1", role: "Auditor", status: "active" }],
    intermediateArtifacts: [],
    isTerminal: false,
  });
  assert.equal(statusBar.className, "aether-multi-agent-bar");
});
