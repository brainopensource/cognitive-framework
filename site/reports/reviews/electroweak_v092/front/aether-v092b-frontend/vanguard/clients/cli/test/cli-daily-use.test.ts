import { test } from "node:test";
import assert from "node:assert/strict";
import { handleConfig } from "../src/commands/config.js";
import { handleProvider } from "../src/commands/provider.js";
import { handleModel } from "../src/commands/model.js";
import { handleWorkspace } from "../src/commands/workspace.js";
import { handleAgent } from "../src/commands/agent.js";
import { handleWorkflow } from "../src/commands/workflow.js";
import { parseCliOptions } from "../src/composition/parse-cli.js";

test("CLI Daily Use: config show, set, and reset", async () => {
  const parsed = parseCliOptions(["--json"]);

  // Show
  let code = await handleConfig(["show"], parsed);
  assert.equal(code, 0);

  // Set
  code = await handleConfig(["set", "general.defaultAgent", "coding-agent"], parsed);
  assert.equal(code, 0);

  // Reset
  code = await handleConfig(["reset"], parsed);
  assert.equal(code, 0);
});

test("CLI Daily Use: provider list, inspect, and default", async () => {
  const parsed = parseCliOptions(["--json"]);

  // List
  let code = await handleProvider(["list"], parsed);
  assert.equal(code, 0);

  // Inspect
  code = await handleProvider(["inspect", "provider-openrouter"], parsed);
  assert.equal(code, 0);

  // Default
  code = await handleProvider(["default", "provider-openrouter"], parsed);
  assert.equal(code, 0);
});

test("CLI Daily Use: model list and default", async () => {
  const parsed = parseCliOptions(["--json"]);

  // List
  let code = await handleModel(["list"], parsed);
  assert.equal(code, 0);

  // Default
  code = await handleModel(["default"], parsed);
  assert.equal(code, 0);
});

test("CLI Daily Use: workspace current, recent, default, set", async () => {
  const parsed = parseCliOptions(["--json"]);

  // Current
  let code = await handleWorkspace(["current"], parsed);
  assert.equal(code, 0);

  // Recent
  code = await handleWorkspace(["recent"], parsed);
  assert.equal(code, 0);

  // Default
  code = await handleWorkspace(["default"], parsed);
  assert.equal(code, 0);

  // Set
  code = await handleWorkspace(["set", "."], parsed);
  assert.equal(code, 0);
});

test("CLI Daily Use: agent and workflow default command handling", async () => {
  const parsed = parseCliOptions(["--json"]);

  let code = await handleAgent(["default", "coding-agent"], parsed);
  assert.equal(code, 0);

  code = await handleWorkflow(["default", "default-turn-loop"], parsed);
  assert.equal(code, 0);
});
