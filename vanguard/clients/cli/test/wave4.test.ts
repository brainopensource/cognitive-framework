import test from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import {
  LiveRuntimeClient,
  ReplayRuntimeClient,
  ScenarioRuntimeClient,
  streamRun,
} from "@aether/client";
import { emptyRunView } from "../src/application/run-view.js";
import { clientFor } from "../src/composition/client-for.js";
import { parseCliOptions } from "../src/composition/parse-cli.js";
import { packageRootFrom } from "../src/composition/catalog.js";
import { statusBarFromView } from "../src/tui/status-bar.js";

function root(): string {
  return packageRootFrom(import.meta.url);
}

function vg(args: string[]) {
  const bin = join(root(), "dist/src/main.js");
  return spawnSync(process.execPath, [bin, ...args], { encoding: "utf8" });
}

test("clientFor demo is replay/mock; default and --yes are live attach (not Replay)", async () => {
  // --headless on the live/--yes cases too: clientFor's non-headless path
  // now spawns a real daemon via ManagedRuntimeHost (F4 Phase 5) -- this
  // test checks client *class* selection, not connectivity, so it stays on
  // the fail-fast headless path to avoid a real subprocess spawn here.
  const demo = await clientFor(parseCliOptions(["--demo", "--headless"]));
  const replay = await clientFor(parseCliOptions(["--replay", join(root(), "fixtures/successful-episode.jsonl")]));
  const scenario = await clientFor(parseCliOptions(["--scenario"]));
  const live = await clientFor(parseCliOptions(["--headless", "--socket-path", "/tmp/missing-vg-wave4.sock"]));
  const yes = await clientFor(parseCliOptions(["--yes", "--headless", "--socket-path", "/tmp/missing-vg-wave4.sock"]));
  assert.equal(demo instanceof ReplayRuntimeClient, true);
  assert.equal(replay instanceof ReplayRuntimeClient, true);
  assert.equal(scenario instanceof ScenarioRuntimeClient, true);
  assert.equal(live instanceof LiveRuntimeClient, true);
  assert.equal(yes instanceof LiveRuntimeClient, true);
  assert.equal(live instanceof ReplayRuntimeClient, false);
  assert.equal(yes instanceof ReplayRuntimeClient, false);
});

test("headless live path without daemon is not_available and never source mock", async () => {
  const client = await clientFor(parseCliOptions(["--headless", "--socket-path", "/tmp/missing-vg-wave4.sock"]));
  const lines: string[] = [];
  const code = await streamRun(client, parseCliOptions(["--headless", "--socket-path", "/tmp/missing-vg-wave4.sock"]), (l) =>
    lines.push(l)
  );
  assert.equal(code, 2);
  assert.equal(JSON.parse(lines[0]!).error.code, "not_available");
  assert.equal(lines.some((line) => line.includes('"source":"mock"')), false);
});

test("status bar uses session chrome: not_available is not live and does not invent policy daemon", () => {
  const line = statusBarFromView({
    view: emptyRunView(),
    source: "unknown",
    lastKind: "not_available",
  });
  assert.match(line, /source: unknown/);
  assert.equal(/source: live/.test(line), false);
  assert.match(line, /daemon: not_available/);
  assert.equal(/policy: daemon/.test(line), false);
  assert.equal(/sandbox: daemon/.test(line), false);
});

test("vg run --demo --headless stays source: mock", () => {
  const result = vg(["run", "--demo", "--headless"]);
  assert.equal(result.status, 0);
  const text = `${result.stdout}${result.stderr}`;
  assert.match(text, /"source":"mock"/);
  assert.equal(text.includes('"source":"live"'), false);
});

test("vg run --headless without daemon fails honestly (not_available, not mock)", () => {
  const result = vg(["run", "--headless", "--socket-path", "/tmp/missing-vg-wave4.sock"]);
  assert.equal(result.status, 2);
  const text = `${result.stdout}${result.stderr}`;
  assert.match(text, /not_available/);
  assert.equal(text.includes('"source":"mock"'), false);
});
