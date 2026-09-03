import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  canonicalHarnessId,
  executionProfileFor,
  resolveHarnessManifestPath,
  FrontendAppController,
  FakeRuntimeClient,
  InMemoryPersistenceAdapter,
} from "../src/index.js";

const REPO_ROOT = fileURLToPath(new URL("../../../../..", import.meta.url));

test("coding-agent aliases to the product vg-code-default harness", () => {
  assert.equal(canonicalHarnessId("coding-agent"), "vg-code-default");
  assert.equal(canonicalHarnessId("vg-code-balanced"), "vg-code-balanced");
});

test("resolveHarnessManifestPath finds real agency manifests from the repo", () => {
  const defaultPath = resolveHarnessManifestPath("coding-agent", REPO_ROOT);
  assert.ok(defaultPath, "coding-agent must resolve to a real manifest file");
  assert.ok(defaultPath.endsWith(join("vg-code-default", "manifest.json")));
  assert.equal(existsSync(defaultPath), true);

  const balanced = resolveHarnessManifestPath("vg-code-balanced", REPO_ROOT);
  assert.ok(balanced);
  assert.ok(balanced.endsWith(join("vg-code-balanced", "manifest.json")));
  assert.equal(existsSync(balanced), true);
});

test("executionProfileFor maps plan mode to the plan preset, otherwise local", () => {
  assert.equal(executionProfileFor(true), "plan");
  assert.equal(executionProfileFor(false), "local");
});

test("FrontendAppController.startRun sends a real harness manifestPath, not the workspace, and does not use the agent id as profileId", async () => {
  const client = new FakeRuntimeClient();
  const persistence = new InMemoryPersistenceAdapter();
  const controller = new FrontendAppController({
    client,
    persistence,
    initialWorkspace: REPO_ROOT,
    initialAgentId: "coding-agent",
  });

  const run = await controller.startRun("fix the failing test");
  assert.ok(run);

  const start = client.commandsReceived.find((c) => c.method === "startRun");
  assert.ok(start, "startRun must be issued");
  const request = start.args[0] as {
    manifestPath?: string;
    repoPath?: string;
    profileId?: string;
    brief?: string;
    prompt?: string;
  };

  assert.equal(request.profileId, "local");
  assert.ok(request.manifestPath && existsSync(request.manifestPath), "manifestPath must be a real file");
  assert.ok(
    request.manifestPath.endsWith(join("vg-code-default", "manifest.json")),
    `expected vg-code-default, got ${request.manifestPath}`,
  );
  assert.notEqual(request.manifestPath, REPO_ROOT);
  assert.notEqual(request.manifestPath, ".");
  assert.equal(dirname(request.manifestPath) !== REPO_ROOT, true);
  assert.equal(request.prompt ?? request.brief, "fix the failing test");
});
