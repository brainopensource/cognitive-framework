import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { ManagedRuntimeHost, type ManagedRuntimeEvent } from "../src/runtime/managed-runtime.js";
import type { ProductLayout } from "../src/product/paths.js";

/**
 * F4 Phase 4: ManagedRuntimeHost's spawnRuntimeProcess called
 * vanguard/packages/runtime/standalone_daemon.py with `--socket-path`, a
 * flag that daemon's real argparse doesn't have (it's `--socket`) --
 * confirmed by reading the daemon's source, not assumed. This test spawns
 * the real daemon process end-to-end (no mocks) to prove the fix actually
 * reaches RUNNING against the real backend, not just that the flag string
 * looks right.
 */

// Compiled test lives at vanguard/clients/client/dist/test/*.js; 5 levels up
// (dist/test -> dist -> client -> clients -> vanguard) reaches the repo root.
const REPO_ROOT = fileURLToPath(new URL("../../../../..", import.meta.url));

function tempLayout(): ProductLayout {
  const base = mkdtempSync(join(tmpdir(), "aether-managed-runtime-test-"));
  return {
    appRoot: REPO_ROOT,
    binDir: join(REPO_ROOT, "bin"),
    runtimeDir: join(REPO_ROOT, "vanguard", "packages"),
    runtimeEntrypoint: join(REPO_ROOT, "vanguard", "packages", "runtime", "standalone_daemon.py"),
    schemasDir: join(REPO_ROOT, "schemas"),
    labDir: join(REPO_ROOT, "vanguard", "clients", "lab", "dist"),
    configDir: join(base, "config"),
    configFile: join(base, "config", "config.json"),
    credentialsFile: join(base, "config", "credentials.json"),
    stateDir: join(base, "state"),
    dataDir: join(base, "data"),
    socketPath: join(base, "state", "runtime.sock"),
    pidFile: join(base, "state", "runtime.pid"),
    logsDir: join(base, "logs"),
    cacheDir: join(base, "cache"),
  };
}

describe("@aether/client — ManagedRuntimeHost (real daemon spawn)", () => {
  it("spawns the real standalone_daemon.py, reaches RUNNING, and shuts down cleanly", { timeout: 15_000 }, async () => {
    const layout = tempLayout();
    // Guards against silently re-breaking REPO_ROOT resolution: a wrong
    // path here doesn't throw, it just makes waitForReadiness poll for the
    // full timeout with nothing ever listening -- this turns that into an
    // immediate, obvious failure instead.
    assert.ok(existsSync(layout.runtimeEntrypoint), `runtimeEntrypoint does not exist: ${layout.runtimeEntrypoint}`);

    const events: ManagedRuntimeEvent[] = [];
    const pythonExecutable =
      process.env.PYTHON_BIN ??
      (existsSync(join(REPO_ROOT, ".venv", "bin", "python"))
        ? join(REPO_ROOT, ".venv", "bin", "python")
        : "python3");
    const host = new ManagedRuntimeHost({
      layout,
      pythonExecutable,
      autoRestart: false,
      startupTimeoutMs: 8_000,
      onEvent: (e) => events.push(e),
    });

    try {
      const { client, report } = await host.ensureRunning();
      assert.equal(host.getStatus(), "RUNNING");
      assert.equal(host.isManaged(), true);
      assert.notEqual(report.status, "INCOMPATIBLE");

      const status = await client.getDaemonStatus();
      assert.equal(status.ok, true);
      if (status.ok) {
        assert.equal(status.value.status, "running");
      }

      const sawStarting = events.some((e) => e.type === "status_changed" && e.status === "STARTING");
      const sawRunning = events.some((e) => e.type === "status_changed" && e.status === "RUNNING");
      assert.ok(sawStarting, "never observed STARTING transition");
      assert.ok(sawRunning, "never observed RUNNING transition");
    } finally {
      await host.shutdown();
      assert.equal(host.getStatus(), "OFFLINE");
      rmSync(layout.stateDir, { recursive: true, force: true });
      rmSync(layout.dataDir, { recursive: true, force: true });
    }
  });

  it("rejects quickly when the daemon entrypoint does not exist, including stderr in the error", async () => {
    const layout = tempLayout();
    layout.runtimeEntrypoint = join(layout.stateDir, "no-such-daemon.py");
    const started = Date.now();
    const host = new ManagedRuntimeHost({
      layout,
      pythonExecutable: "python3",
      autoRestart: false,
      startupTimeoutMs: 8_000,
    });
    try {
      await assert.rejects(
        () => host.ensureRunning(),
        (err: unknown) => {
          const message = err instanceof Error ? err.message : String(err);
          assert.ok(/no-such-daemon|can't open file|No such file/i.test(message), message);
          return true;
        },
      );
      assert.ok(Date.now() - started < 4000, "must fail faster than the startup timeout");
    } finally {
      await host.shutdown();
      rmSync(layout.stateDir, { recursive: true, force: true });
      rmSync(layout.dataDir, { recursive: true, force: true });
    }
  });
});
