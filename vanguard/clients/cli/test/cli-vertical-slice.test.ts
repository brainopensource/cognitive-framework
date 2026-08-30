import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { parseCliOptions } from "../src/composition/parse-cli.js";
import { handleRun } from "../src/commands/run.js";
import { handleAgent } from "../src/commands/agent.js";
import { handleWorkflow } from "../src/commands/workflow.js";
import { handleArtifact } from "../src/commands/artifact.js";
import { handleDoctor } from "../src/commands/doctor.js";
import { handleDaemon } from "../src/commands/daemon.js";
import { CLI_EXIT_CODES, exitCodeForErrorCode } from "../src/output.js";

describe("@aether/cli — Vertical Slice & Exit Code Contract", () => {
  it("maps all canonical error codes according to the PRD exit code contract", () => {
    // 0: SUCCESS
    assert.equal(exitCodeForErrorCode(undefined), 0);
    // 1: EXECUTION_FAILED
    assert.equal(exitCodeForErrorCode("conflict"), 1);
    assert.equal(exitCodeForErrorCode("internal"), 1);
    assert.equal(exitCodeForErrorCode("TASK_FAILED"), 1);
    // 2: INVALID_INPUT
    assert.equal(exitCodeForErrorCode("invalid_request"), 2);
    assert.equal(exitCodeForErrorCode("not_found"), 2);
    assert.equal(exitCodeForErrorCode("incompatible_version"), 2);
    assert.equal(exitCodeForErrorCode("frame_too_large"), 2);
    // 4: PERMISSION_DENIED
    assert.equal(exitCodeForErrorCode("unauthenticated"), 4);
    assert.equal(exitCodeForErrorCode("permission_denied"), 4);
    // 5: RESOURCE_EXHAUSTED
    assert.equal(exitCodeForErrorCode("rate_limited"), 5);
    // 6: DAEMON_UNAVAILABLE
    assert.equal(exitCodeForErrorCode("not_available"), 6);
  });

  it("executes headless run on replay fixture with clean exit code 0", async () => {
    const options = parseCliOptions([
      "--replay",
      "fixtures/successful-episode.jsonl",
      "--headless",
      "--json",
    ]);
    const exitCode = await handleRun([], options);
    assert.equal(exitCode, CLI_EXIT_CODES.SUCCESS);
  });

  it("handles agent list and inspect", async () => {
    const listOptions = parseCliOptions(["--json"]);
    const listCode = await handleAgent(["list"], listOptions);
    assert.equal(listCode, CLI_EXIT_CODES.SUCCESS);

    const inspectCode = await handleAgent(["inspect", "coding-agent"], listOptions);
    assert.equal(inspectCode, CLI_EXIT_CODES.SUCCESS);

    const missingCode = await handleAgent(["inspect", "nonexistent-agent-id-xyz"], listOptions);
    assert.equal(missingCode, CLI_EXIT_CODES.INVALID_INPUT);
  });

  it("handles workflow list and inspect", async () => {
    const options = parseCliOptions(["--json"]);
    const listCode = await handleWorkflow(["list"], options);
    assert.equal(listCode, CLI_EXIT_CODES.SUCCESS);

    const inspectCode = await handleWorkflow(["inspect", "default-turn-loop"], options);
    assert.equal(inspectCode, CLI_EXIT_CODES.SUCCESS);
  });

  it("handles artifact explain and documents BACKEND-GAP on artifact get", async () => {
    const replayOptions = parseCliOptions(["--demo", "--json"]);
    const explainCode = await handleArtifact(["explain", "sha256:" + "a".repeat(64)], replayOptions);
    assert.equal(explainCode, CLI_EXIT_CODES.SUCCESS);

    const getCode = await handleArtifact(["get", "sha256:" + "b".repeat(64)], replayOptions);
    assert.equal(getCode, CLI_EXIT_CODES.DAEMON_UNAVAILABLE);
  });

  it("handles daemon status cleanly", async () => {
    const options = parseCliOptions(["--json"]);
    const status = await handleDaemon(["status"], options);
    // Socket is not running during hermetic unit test -> DAEMON_UNAVAILABLE (6)
    assert.equal(status, CLI_EXIT_CODES.DAEMON_UNAVAILABLE);
  });

  it("handles doctor report fail-closed when daemon is offline", async () => {
    const options = parseCliOptions(["--json"]);
    const doctorCode = await handleDoctor([], options);
    assert.equal(doctorCode, CLI_EXIT_CODES.DAEMON_UNAVAILABLE);
  });
});
