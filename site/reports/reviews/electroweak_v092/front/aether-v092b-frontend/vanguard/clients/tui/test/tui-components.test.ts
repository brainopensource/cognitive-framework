import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { PassThrough } from "node:stream";
import { TerminalScreen } from "../src/terminal/screen.js";
import { TuiStore } from "../src/store.js";
import { renderHeader } from "../src/components/header.js";
import { renderComposer } from "../src/components/composer.js";
import { renderStatusFooter } from "../src/components/status-footer.js";
import { renderApprovalDeck } from "../src/components/approval-deck.js";
import { renderDiffViewer } from "../src/components/diff-viewer.js";
import { renderDiffCard } from "../src/components/cards/diff-card.js";

describe("@aether/tui — Presentation Components", () => {
  it("renders header with session metadata and status tag", () => {
    const stream = new PassThrough();
    let written = "";
    stream.on("data", (chunk) => {
      written += chunk.toString("utf-8");
    });

    const screen = new TerminalScreen({ stdout: stream as any, colorMode: "plain" });
    screen.resize(80, 24);
    const store = new TuiStore({
      agentId: "coding-agent",
      model: "openrouter/free",
      workspacePath: "/repo",
    });

    renderHeader(screen, store.get(), 0);
    screen.render();

    assert.ok(written.includes("AETHER"));
    assert.ok(written.includes("coding-agent"));
    assert.ok(written.includes("openrouter/free"));
  });

  it("renders composer with placeholder and prompt text", () => {
    const stream = new PassThrough();
    let written = "";
    stream.on("data", (chunk) => {
      written += chunk.toString("utf-8");
    });

    const screen = new TerminalScreen({ stdout: stream as any, colorMode: "plain" });
    screen.resize(80, 24);
    const store = new TuiStore();

    renderComposer(screen, store.get(), 20, 3);
    screen.render();

    assert.ok(written.includes("Message AETHER"));
  });

  it("renders approval deck with action and buttons", () => {
    const stream = new PassThrough();
    let written = "";
    stream.on("data", (chunk) => {
      written += chunk.toString("utf-8");
    });

    const screen = new TerminalScreen({ stdout: stream as any, colorMode: "plain" });
    screen.resize(80, 24);
    const store = new TuiStore({
      pendingApproval: {
        approvalId: "app-test-1",
        unifiedDiff: "+diff",
        proposedPatchDigest: "sha256:1",
        episodeId: "ep-1",
        argsDigest: "sha256:2",
        descriptorDigest: "sha256:3",
        expiresAt: "2026-08-30T00:00:00.000Z",
      },
    });

    const rows = renderApprovalDeck(screen, store.get(), 15);
    screen.render();

    assert.equal(rows, 5);
    assert.ok(written.includes("APPROVAL REQUIRED"));
    assert.ok(written.includes("Approve & Sign"));
  });

  it("renders diff viewer with additions and deletions", () => {
    const stream = new PassThrough();
    let written = "";
    stream.on("data", (chunk) => {
      written += chunk.toString("utf-8");
    });

    const screen = new TerminalScreen({ stdout: stream as any, colorMode: "plain" });
    screen.resize(80, 24);
    const diff = "--- a/file\n+++ b/file\n@@ -1,1 +1,1 @@\n-old\n+new";

    renderDiffViewer(screen, diff, 0);
    screen.render();

    assert.ok(written.includes("Unified Diff Viewer"));
    assert.ok(written.includes("-old"));
    assert.ok(written.includes("+new"));
  });

  it("renders diff card with additions/deletions summary", () => {
    const stream = new PassThrough();
    const screen = new TerminalScreen({ stdout: stream as any, colorMode: "plain" });
    screen.resize(80, 24);
    const diff = "--- a/file\n+++ b/file\n@@ -1,1 +1,1 @@\n-old\n+new";

    const lines = renderDiffCard(screen, 0, "Modified dispatch.py", diff, true);
    assert.ok(lines > 1);
  });
});
