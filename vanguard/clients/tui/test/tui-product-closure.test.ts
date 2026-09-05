process.env.NODE_ENV = "test";
process.env.AETHER_IN_MEMORY_PERSISTENCE = "1";

import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync, rmSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { TuiStore } from "../src/store.js";
import { KeyboardManager } from "../src/keyboard.js";
import { InMemoryPersistenceAdapter, FrontendAppController } from "@aether/client";

test("TUI daily-use: slash commands execution (/workspace, /agent, /workflow, /provider, /model, /history, /new, /clear)", () => {
  const persistence = new InMemoryPersistenceAdapter();
  const controller = new FrontendAppController({ persistence });
  const store = new TuiStore({}, undefined);

  // /workspace
  store.executeSlashCommand("/workspace /test/dir");
  assert.equal(store.get().workspacePath, "/test/dir");

  // /agent
  store.executeSlashCommand("/agent research-agent");
  assert.equal(store.get().agentId, "research-agent");

  // /workflow
  store.executeSlashCommand("/workflow multi-agent-audit");
  assert.equal(store.get().workflowId, "multi-agent-audit");

  // /provider
  store.executeSlashCommand("/provider provider-openrouter");
  assert.equal(store.get().selectedProviderId, "provider-openrouter");

  // /model — validated against the model registry, fails closed on paid
  // models unless VANGUARD_ALLOW_PAID is set (a free-tier model succeeds)
  store.executeSlashCommand("/model deepseek/deepseek-v4-flash-0731");
  assert.equal(store.get().model, "openrouter/free", "paid model without VANGUARD_ALLOW_PAID should be rejected, leaving the model unchanged");

  store.executeSlashCommand("/model free");
  assert.equal(store.get().model, "openrouter/free");

  store.executeSlashCommand("/model not-a-real-model");
  assert.equal(store.get().model, "openrouter/free", "unknown model id should be rejected");

  // /history
  store.executeSlashCommand("/history");
  assert.equal(store.get().activeModal, "history");

  // /clear
  store.executeSlashCommand("/clear");
  assert.equal(store.get().turns.length, 0);

  // /new
  store.executeSlashCommand("/new");
  assert.equal(store.get().turns.length, 0);
});

test("TUI keyboard grammar: slash command trigger and execution", () => {
  const store = new TuiStore();
  const keyboard = new KeyboardManager(store);

  // Type slash command
  store.setComposerText("/agent coding-agent", 19);
  keyboard.handleKey({ name: "return", ctrl: false, meta: false, shift: false, sequence: "\r" });

  assert.equal(store.get().agentId, "coding-agent");
  assert.equal(store.get().composerText, "");
});

test("command palette selection dispatches the command shown at that index, not a shifted one", () => {
  // Regression test for the historical bug: app.ts's rendered palette and
  // keyboard.ts's execution list were two independently maintained arrays
  // whose positions disagreed, so picking "cancel" fired "history" instead.
  // Both now render from and dispatch against @aether/tui-core's single
  // registry, so selecting an index always runs the command shown there.
  const store = new TuiStore();
  const keyboard = new KeyboardManager(store);

  // Open the palette
  store.setComposerText("", 0);
  keyboard.handleKey({ name: "/", ctrl: false, meta: false, shift: false, sequence: "/" });
  assert.equal(store.get().activeModal, "command-palette");

  // The registry's 3rd entry (index 2) is "workflow" — select it and confirm
  // the workflow modal opens, not some unrelated command.
  keyboard.handleKey({ name: "down", ctrl: false, meta: false, shift: false, sequence: "" });
  keyboard.handleKey({ name: "down", ctrl: false, meta: false, shift: false, sequence: "" });
  keyboard.handleKey({ name: "return", ctrl: false, meta: false, shift: false, sequence: "\r" });

  assert.equal(store.get().activeModal, "select-workflow");
});

test("typing a full command with args at the palette (e.g. '/busy queue') dispatches with the typed args, not empty ones", () => {
  // Regression: pressing "/" opens the palette, and everything typed after
  // it went into a filter query that was matched with a plain substring
  // check against the *whole* typed string (including args) -- so typing
  // "busy queue" matched nothing (no command name contains "busy queue"),
  // and even when a match survived, Enter dispatched with args="" always,
  // silently dropping anything typed after the command name.
  const store = new TuiStore();
  const keyboard = new KeyboardManager(store);

  const type = (text: string) => {
    for (const ch of text) {
      keyboard.handleKey({ name: ch, ctrl: false, meta: false, shift: false, sequence: ch });
    }
  };

  keyboard.handleKey({ name: "/", ctrl: false, meta: false, shift: false, sequence: "/" });
  assert.equal(store.get().activeModal, "command-palette");

  type("busy queue");
  keyboard.handleKey({ name: "return", ctrl: false, meta: false, shift: false, sequence: "\r" });

  assert.equal(store.get().busyMode, "queue");
});

test("newly added SOTA slash commands: /status, /context, /cost, /compact, /doctor, /diff, /undo, /init, /title", () => {
  const dir = mkdtempSync(join(tmpdir(), "aether-tui-init-"));
  try {
    const store = new TuiStore({ workspacePath: dir });

    store.executeSlashCommand("/status");
    assert.match(store.get().statusMessage, /agent:.*workspace:/);

    store.executeSlashCommand("/context");
    assert.match(store.get().statusMessage, /context: \d+ tokens/);

    store.executeSlashCommand("/cost");
    assert.match(store.get().statusMessage, /cost: \$/);

    store.executeSlashCommand("/doctor");
    assert.match(store.get().statusMessage, /doctor: connection=/);

    store.executeSlashCommand("/diff");
    assert.equal(store.get().statusMessage, "No pending diff.");

    store.executeSlashCommand("/undo");
    assert.match(store.get().statusMessage, /not yet implemented/);

    store.executeSlashCommand("/title my session");
    // No active conversation in this fixture, so it should not throw and should
    // still report the attempted title.
    assert.match(store.get().statusMessage, /Title: my session/);

    store.executeSlashCommand("/init");
    assert.match(store.get().statusMessage, /Wrote /);
    assert.equal(existsSync(join(dir, "AETHER.md")), true);

    // Re-running /init must not clobber the existing file
    store.executeSlashCommand("/init");
    assert.match(store.get().statusMessage, /already exists/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("/compact trims the local transcript view without touching run state", () => {
  const store = new TuiStore();
  store.update((s) => ({
    ...s,
    turns: Array.from({ length: 10 }, (_, i) => ({ id: `t${i}` } as any)),
  }));
  store.executeSlashCommand("/compact");
  assert.equal(store.get().turns.length, 5);
});

test("!cmd runs a local shell command and shows its output without invoking the model", () => {
  const store = new TuiStore();
  const keyboard = new KeyboardManager(store);

  store.setComposerText("!echo hello-from-tui", 21);
  keyboard.handleKey({ name: "return", ctrl: false, meta: false, shift: false, sequence: "\r" });

  assert.equal(store.get().composerText, "");
  assert.equal(store.get().activeModal, "diff-viewer");
  assert.match(store.get().diffViewerContent, /hello-from-tui/);
  // No run was started: no model/client was ever provided to the keyboard manager.
  assert.equal(store.get().runId, "");
});

test("@path references expand to inline file content before a prompt reaches expandComposerReferences", () => {
  const dir = mkdtempSync(join(tmpdir(), "aether-tui-refs-"));
  try {
    writeFileSync(join(dir, "notes.txt"), "important context here");
    const store = new TuiStore({ workspacePath: dir });
    const expanded = store.expandComposerReferences("please read @notes.txt");
    assert.match(expanded, /important context here/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("/model without arguments opens select-model modal and keyboard selects a model", () => {
  const store = new TuiStore();
  const keyboard = new KeyboardManager(store);

  // Execute /model without arguments
  store.executeSlashCommand("/model");
  assert.equal(store.get().activeModal, "select-model");
  assert.ok(store.get().availableModels.length > 0, "availableModels should be populated");

  // Press down arrow, then return
  keyboard.handleKey({ name: "down", ctrl: false, meta: false, shift: false, sequence: "" });
  keyboard.handleKey({ name: "return", ctrl: false, meta: false, shift: false, sequence: "\r" });

  assert.equal(store.get().activeModal, "none");
  assert.equal(store.get().focus, "composer");
  assert.equal(store.get().model, store.get().availableModels[1]?.id);
});

