import { strict as assert } from "node:assert";
import { describe, it, before } from "node:test";
import { DesktopStore } from "../src/state/desktop-store.js";
import { renderDiffViewer } from "../src/components/DiffViewer.js";
import { renderSidebar } from "../src/components/Sidebar.js";
import { renderTopBar } from "../src/components/TopBar.js";
import { renderApprovalBanner } from "../src/components/ApprovalBanner.js";
import { renderForensicDrawer } from "../src/components/ForensicDrawer.js";
import { renderComposer } from "../src/components/Composer.js";
import { renderTranscriptPane } from "../src/components/TranscriptPane.js";
import { installMockDom } from "./support/mock-dom.js";

describe("@aether/desktop — Presentation Components", () => {
  before(() => {
    installMockDom();
  });

  it("renders DiffViewer lines with additions and deletions", () => {
    const diff = "--- a/file\n+++ b/file\n@@ -1,1 +1,1 @@\n-old\n+new";
    const el = renderDiffViewer(diff);
    assert.equal(el.className, "aether-diff-viewer");
    assert.equal(el.children.length, 5);
  });

  it("renders Sidebar with brand, new chat button, and session items", () => {
    const store = new DesktopStore();
    const el = renderSidebar(store);
    assert.equal(el.className, "aether-sidebar");
    assert.ok(el.children.length >= 3);
  });

  it("renders TopBar with agent identity and status badge", () => {
    const store = new DesktopStore();
    const el = renderTopBar(store);
    assert.equal(el.className, "aether-topbar");
  });

  it("renders ApprovalBanner when pending approval is present", () => {
    const store = new DesktopStore({
      pendingApproval: {
        approvalId: "app-d-01",
        unifiedDiff: "+diff",
        proposedPatchDigest: "sha256:1",
        episodeId: "ep-1",
        argsDigest: "sha256:2",
        descriptorDigest: "sha256:3",
        expiresAt: "2026-08-30T00:00:00.000Z",
      },
    });
    const el = renderApprovalBanner(store);
    assert.ok(el !== null);
    assert.equal(el?.className, "aether-approval-banner");
  });

  it("renders ForensicDrawer when opened", () => {
    const store = new DesktopStore();
    store.openForensicDrawer("diffs", "--- a/file\n+++ b/file\n+new");
    const el = renderForensicDrawer(store);
    assert.ok(el !== null);
    assert.equal(el?.className, "aether-forensic-drawer");
  });

  it("renders Composer and TranscriptPane cleanly", () => {
    const store = new DesktopStore();
    const composerEl = renderComposer(store);
    assert.equal(composerEl.className, "aether-composer");

    const transcriptEl = renderTranscriptPane(store);
    assert.equal(transcriptEl.className, "aether-transcript-pane");
  });
});
