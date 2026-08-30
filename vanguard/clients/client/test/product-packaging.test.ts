import { test } from "node:test";
import assert from "node:assert/strict";
import {
  ProductPaths,
  CompatibilityNegotiator,
  ConfigurationResolver,
  InMemoryPersistenceAdapter,
} from "../src/index.js";
import type { DaemonStatus } from "@aether/contracts";

test("ProductPaths: deterministic resolution of platform directories", () => {
  const layout = ProductPaths.resolveLayout("/opt/aether-test");
  assert.equal(layout.appRoot, "/opt/aether-test");
  assert.equal(layout.binDir, "/opt/aether-test/bin");
  assert.equal(layout.schemasDir, "/opt/aether-test/schemas");
  assert.ok(layout.configDir.length > 0);
  assert.ok(layout.stateDir.length > 0);
  assert.ok(layout.dataDir.length > 0);
  assert.ok(layout.socketPath.length > 0);
  assert.ok(layout.pidFile.length > 0);
});

test("CompatibilityNegotiator: COMPATIBLE status on matching versions and protocol", () => {
  const status: DaemonStatus = {
    status: "running",
    socketPath: "/tmp/vanguard-runtime.sock",
    version: "0.9.1-rc1",
    uptimeSeconds: 120,
  };

  const report = CompatibilityNegotiator.evaluate(status, "0.9.1-rc1", "vg.4");
  assert.equal(report.status, "COMPATIBLE");
  assert.equal(report.reasons.length, 0);
});

test("CompatibilityNegotiator: INCOMPATIBLE status on protocol or major version mismatch", () => {
  const status: DaemonStatus = {
    status: "running",
    socketPath: "/tmp/vanguard-runtime.sock",
    version: "1.0.0",
    uptimeSeconds: 120,
  };

  const report = CompatibilityNegotiator.evaluate(status, "0.9.1-rc1", "vg.4");
  assert.equal(report.status, "INCOMPATIBLE");
  assert.ok(report.reasons.some((r) => r.includes("Major version mismatch")));
});

test("CompatibilityNegotiator: INCOMPATIBLE when daemon is offline or null", () => {
  const report = CompatibilityNegotiator.evaluate(null);
  assert.equal(report.status, "INCOMPATIBLE");
});

test("ConfigurationResolver: strict precedence resolution", async () => {
  const persistence = new InMemoryPersistenceAdapter();
  await persistence.saveSettings({
    general: {
      defaultRuntime: "managed",
      defaultWorkspace: "/user/saved/ws",
      defaultAgent: "coding-agent",
      defaultWorkflow: "default-turn-loop",
      autoFollowStreaming: true,
    },
    runtime: {
      socketPath: "/user/saved/sock",
      httpUrl: "http://localhost:8000",
      reconnectIntervalMs: 1000,
      maxReconnectAttempts: 10,
      requestTimeoutMs: 30000,
    },
    appearance: {
      theme: "dark",
      density: "comfortable",
      reducedMotion: false,
    },
    workspace: {
      recentWorkspaces: [],
      maxRecentWorkspaces: 10,
    },
    terminal: {
      tuiAnimation: true,
      tuiColorMode: "truecolor",
    },
    accessibility: {
      highContrast: false,
      screenReaderOptimized: false,
      fontSize: 14,
    },
  });

  // Explicit override takes highest precedence
  const resolved = await ConfigurationResolver.resolve(
    {
      defaultWorkspace: "/explicit/override/ws",
      theme: "light",
    },
    persistence
  );

  assert.equal(resolved.general.defaultWorkspace, "/explicit/override/ws");
  assert.equal(resolved.appearance.theme, "light");
  assert.equal(resolved.runtime.socketPath, "/user/saved/sock");
});
