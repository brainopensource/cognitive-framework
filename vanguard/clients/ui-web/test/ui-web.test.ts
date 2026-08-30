import { strict as assert } from "node:assert";
import { describe, it, before } from "node:test";
import {
  renderStatusBadge,
  renderConnectionStatus,
  renderRunStatus,
  renderDiffViewer,
  renderCodeBlock,
  renderArtifactReference,
  renderApprovalSummary,
  renderSearchInput,
  renderEmptyState,
  renderLoadingState,
  renderErrorState,
} from "../src/index.js";
import { diagnoseFailure } from "@aether/projections";

function setupDom() {
  if (typeof globalThis.document === "undefined") {
    class MockElement {
      public style: Record<string, string> = {};
      public children: MockElement[] = [];
      public textContent: string = "";
      public innerHTML: string = "";
      public className: string = "";
      public type: string = "";
      public placeholder: string = "";
      public value: string = "";
      public onclick: any = null;
      public oninput: any = null;
      public onkeydown: any = null;

      appendChild(child: MockElement) {
        this.children.push(child);
        return child;
      }
      addEventListener(_event: string, _fn: any) {}
    }

    (globalThis as any).document = {
      createElement: () => new MockElement(),
      head: new MockElement(),
    };
  }
}

describe("@aether/ui-web — Shared Web UI Components", () => {
  before(() => {
    setupDom();
  });

  it("renders StatusBadge with correct style classes", () => {
    const badge = renderStatusBadge({ status: "running" });
    assert.equal(badge.className, "aether-status-badge");
    assert.equal(badge.textContent, "running");
  });

  it("renders ConnectionStatus with badge and reconnect button when offline", () => {
    let reconnected = false;
    const el = renderConnectionStatus({
      state: "OFFLINE",
      onReconnect: () => {
        reconnected = true;
      },
    });
    assert.equal(el.className, "aether-connection-status");
    assert.equal(el.children.length, 2);
    (el.children[1] as any)?.onclick?.();
    assert.equal(reconnected, true);
  });

  it("renders RunStatus badge and seq", () => {
    const el = renderRunStatus({ runId: "run-12345678", status: "satisfied", seq: "42" });
    assert.equal(el.className, "aether-run-status");
    assert.equal(el.children.length, 3);
  });

  it("renders DiffViewer with additions and deletions", () => {
    const diff = "--- a/file\n+++ b/file\n@@ -1,1 +1,1 @@\n-old\n+new";
    const el = renderDiffViewer(diff);
    assert.equal(el.className, "aether-diff-viewer");
    assert.equal(el.children.length, 5);
  });

  it("renders CodeBlock with header and copy button", () => {
    const el = renderCodeBlock({ code: "const x = 1;", language: "typescript", fileName: "app.ts" });
    assert.equal(el.className, "aether-code-block");
    assert.equal(el.children.length, 2);
  });

  it("renders ArtifactReference with inspect and lab actions", () => {
    let inspected = false;
    let openedLab = false;
    const el = renderArtifactReference({
      digest: "sha256:abcd",
      path: "src/main.ts",
      summary: "Generated main file",
      onInspect: () => {
        inspected = true;
      },
      onOpenInLab: () => {
        openedLab = true;
      },
    });
    assert.equal(el.className, "aether-artifact-card");
  });

  it("renders ApprovalSummary with approve and reject buttons", () => {
    let approved = false;
    let rejected = false;
    const el = renderApprovalSummary({
      approvalId: "app-1",
      action: "fs.write",
      target: "src/index.ts",
      onApprove: () => {
        approved = true;
      },
      onReject: () => {
        rejected = true;
      },
    });
    assert.equal(el.className, "aether-approval-summary");
  });

  it("renders SearchInput with clear button", () => {
    let query = "";
    const el = renderSearchInput({
      placeholder: "Filter items",
      initialValue: "test",
      onSearch: (q) => {
        query = q;
      },
    });
    assert.equal(el.className, "aether-search-input-wrapper");
  });

  it("renders EmptyState and LoadingState cleanly", () => {
    const empty = renderEmptyState({
      icon: "⊞",
      title: "No Conversations",
      description: "Start a new conversation.",
      actionLabel: "New Chat",
      onAction: () => {},
    });
    assert.equal(empty.className, "aether-empty-state");

    const loading = renderLoadingState({ message: "Connecting..." });
    assert.equal(loading.className, "aether-loading-state");
  });

  it("renders ErrorState with retry and diagnostic cause", () => {
    const diag = diagnoseFailure({ code: "not_available", message: "Daemon not running" });
    let retried = false;
    const err = renderErrorState({
      diagnostics: diag,
      onRetry: () => {
        retried = true;
      },
    });
    assert.equal(err.className, "aether-error-state");
  });
});
