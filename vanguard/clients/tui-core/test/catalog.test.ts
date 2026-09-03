import test from "node:test";
import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import {
  loadAgentCatalog,
  canWrite,
  resolveManifestsDir,
} from "../src/catalog/agents.js";
import {
  loadModelCatalog,
  resolveModelsRegistryPath,
  resolveModelSelection,
  ModelPolicyError,
} from "../src/catalog/models.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
// vanguard/clients/tui-core/dist/test -> repo root
const repoRoot = join(__dirname, "../../../../..");

test("resolveManifestsDir finds the in-repo manifest registry", () => {
  const dir = resolveManifestsDir(repoRoot);
  assert.ok(dir, "expected to resolve a manifests dir from the repo root");
});

test("loadAgentCatalog reads real manifests and distinguishes read-only vs write agents", () => {
  const dir = resolveManifestsDir(repoRoot);
  const catalog = loadAgentCatalog(dir);
  assert.ok(catalog.length > 0, "expected at least one manifest entry");

  const codeMax = catalog.find((a) => a.id === "vg-code-max");
  assert.ok(codeMax, "vg-code-max should exist in the catalog");
  assert.equal(canWrite(codeMax!), true);

  const shellOnly = catalog.find((a) => a.id === "vg-shell-only");
  assert.ok(shellOnly, "vg-shell-only should exist in the catalog");
});

test("loadAgentCatalog returns empty (not throw) when no manifests dir resolves", () => {
  const catalog = loadAgentCatalog(null);
  assert.deepEqual(catalog, []);
});

test("resolveModelsRegistryPath finds the in-repo model registry", () => {
  const path = resolveModelsRegistryPath(repoRoot);
  assert.ok(path, "expected to resolve models_registry.json from the repo root");
});

test("loadModelCatalog fails closed when the registry cannot be found", () => {
  assert.throws(() => loadModelCatalog(null), ModelPolicyError);
});

test("loadModelCatalog reads real tiers and aliases", () => {
  const path = resolveModelsRegistryPath(repoRoot);
  const catalog = loadModelCatalog(path);
  assert.ok(catalog.entries.length > 0);
  assert.ok(catalog.entries.some((e) => e.id === "openrouter/free" && e.free));
});

test("resolveModelSelection rejects unknown ids and fails closed on paid models without the env flag", () => {
  const path = resolveModelsRegistryPath(repoRoot);
  const catalog = loadModelCatalog(path);

  assert.throws(() => resolveModelSelection("totally-not-a-model", catalog, {}), ModelPolicyError);

  const paidEntry = catalog.entries.find((e) => !e.free);
  assert.ok(paidEntry, "expected at least one paid-tier entry in the registry");
  assert.throws(() => resolveModelSelection(paidEntry!.id, catalog, {}), ModelPolicyError);
  assert.equal(
    resolveModelSelection(paidEntry!.id, catalog, { VANGUARD_ALLOW_PAID: "1" }),
    paidEntry!.id
  );

  const freeEntry = catalog.entries.find((e) => e.free)!;
  assert.equal(resolveModelSelection(freeEntry.id, catalog, {}), freeEntry.id);
});

test("resolveModelSelection resolves aliases", () => {
  const path = resolveModelsRegistryPath(repoRoot);
  const catalog = loadModelCatalog(path);
  const resolved = resolveModelSelection("free", catalog, {});
  assert.equal(resolved, catalog.aliases["free"]);
});
