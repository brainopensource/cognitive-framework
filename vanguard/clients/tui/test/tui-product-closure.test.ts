import { test } from "node:test";
import assert from "node:assert/strict";
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

  // /model
  store.executeSlashCommand("/model deepseek/deepseek-chat");
  assert.equal(store.get().model, "deepseek/deepseek-chat");

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
