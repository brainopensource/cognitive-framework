import test from "node:test";
import assert from "node:assert/strict";

import {
  createPythonCodingBackend,
  exitCodeForOutcome,
  formatHumanReceipt,
  formatUsdFromMicros,
  parseBudgetUsdToMicros,
  renderProjectionLines,
  runCodingCommand,
  type CodingBackend,
  type CodingRequest,
  type CodingTerminalResult,
} from "@vanguard/client-core";
import { parseCliOptions } from "../src/composition/parse-cli.js";

function baseRequest(overrides: Partial<CodingRequest> = {}): CodingRequest {
  return {
    command: "code",
    workspace: ".",
    brief: "TASK.md",
    plannerModel: "deepseek/deepseek-v4-flash",
    executorBand: "free",
    executorModels: [],
    recoveryModels: ["deepseek/deepseek-v4-flash"],
    reviewerModel: null,
    maxTurnsPerEpisode: 40,
    maxEpisodes: 12,
    maxReplans: 2,
    maxPaidCalls: 0,
    budgetUsdMicros: 50_000,
    interactive: true,
    dryPlan: false,
    json: true,
    headless: true,
    fakeBackend: "greenfield-adaptive",
    ...overrides,
  };
}

test("parseBudgetUsdToMicros converts once and rejects bad values", () => {
  assert.deepEqual(parseBudgetUsdToMicros("0.05"), { ok: true, micros: 50_000 });
  assert.deepEqual(parseBudgetUsdToMicros("$1.25"), { ok: true, micros: 1_250_000 });
  assert.equal(parseBudgetUsdToMicros("-1").ok, false);
  assert.equal(parseBudgetUsdToMicros("nope").ok, false);
  assert.equal(parseBudgetUsdToMicros("Infinity").ok, false);
  assert.equal(parseBudgetUsdToMicros("1000").ok, false);
});

test("parseCliOptions freezes coding flags and budget micros", () => {
  const parsed = parseCliOptions([
    "./empty-app",
    "--brief",
    "TASK.md",
    "--planner",
    "deepseek/deepseek-v4-flash",
    "--executor-band",
    "free",
    "--recovery-model",
    "deepseek/deepseek-v4-flash",
    "--max-turns",
    "40",
    "--max-episodes",
    "12",
    "--max-replans",
    "2",
    "--budget-usd",
    "0.05",
    "--interactive",
    "--jsonl-out",
    "run.jsonl",
  ]);
  assert.equal(parsed.repo, "./empty-app");
  assert.equal(parsed.brief, "TASK.md");
  assert.equal(parsed.plannerModel, "deepseek/deepseek-v4-flash");
  assert.equal(parsed.executorBand, "free");
  assert.equal(parsed.recoveryModel, "deepseek/deepseek-v4-flash");
  assert.equal(parsed.maxTurns, 40);
  assert.equal(parsed.maxEpisodes, 12);
  assert.equal(parsed.maxReplans, 2);
  assert.equal(parsed.budgetUsdMicros, 50_000);
  assert.equal(parsed.interactive, true);
  assert.equal(parsed.jsonlOut, "run.jsonl");
  assert.equal(parsed.budgetError, undefined);
});

test("malformed budget surfaces as budgetError for exit 2", () => {
  const parsed = parseCliOptions([".", "--budget-usd", "abc"]);
  assert.ok(parsed.budgetError);
});

test("coding defaults are usable and cost-safe", () => {
  const parsed = parseCliOptions(["."]);
  assert.equal(parsed.plannerModel, "openrouter/free");
  assert.equal(parsed.recoveryModel, "openrouter/free");
  assert.equal(parsed.interactive, true);

  const benchmark = parseCliOptions([".", "--benchmark"]);
  assert.equal(benchmark.interactive, false);
});

test("human receipts cover required transitions without ANSI", () => {
  const lines = renderProjectionLines(
    [
      { kind: "plan", model: "deepseek/deepseek-v4-flash", stepTotal: 6 },
      { kind: "step", stepIndex: 1, stepTotal: 6, text: "Create HTTP API" },
      { kind: "read", path: "server.py missing" },
      { kind: "write", path: "server.py", text: "+112" },
      { kind: "test", path: "test.test_server", exitCode: 1, failures: 2 },
      { kind: "verified", stepId: "step-001" },
      { kind: "rotate", text: "malformed response x2 -> next free provider" },
      { kind: "escalate", text: "repeated failure fingerprint x2" },
      { kind: "diagnose", model: "deepseek/deepseek-v4-flash" },
      { kind: "resume", model: "cohere/north-mini-code:free" },
      { kind: "oracle", text: "final acceptance exit 0", exitCode: 0 },
      { kind: "complete", outcome: "oracle_green", turns: 27, spentUsdMicros: 13400 },
    ],
    { human: true }
  );
  assert.equal(lines[0], "[plan] deepseek/deepseek-v4-flash: 6 validated steps");
  assert.ok(lines.some((line) => line.startsWith("[escalate]")));
  assert.equal(lines.at(-1), "[complete] oracle_green, 27 turns, $0.0134");
  for (const line of lines) assert.equal(line.includes("\u001b"), false);
  assert.equal(formatUsdFromMicros(null), "unknown");
  assert.equal(formatHumanReceipt({ kind: "budget", remainingUsdMicros: null }), "[budget] remaining unknown");
});

test("exitCodeForOutcome keeps budget and unavailable distinct", () => {
  assert.equal(exitCodeForOutcome("oracle_green"), 0);
  assert.equal(exitCodeForOutcome("verification_failed"), 1);
  assert.equal(exitCodeForOutcome("invalid_request"), 2);
  assert.equal(exitCodeForOutcome("unavailable"), 3);
  assert.equal(exitCodeForOutcome("budget_exhausted"), 4);
});

test("TypeScript coding path has no model-routing or effect-dispatch loop", async () => {
  const { readFileSync } = await import("node:fs");
  const { dirname, join } = await import("node:path");
  const { fileURLToPath } = await import("node:url");
  // dist/test -> package root -> src (not dist/src)
  const packageRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
  const srcRoot = join(packageRoot, "src");
  const files = [
    join(srcRoot, "main.tsx"),
    join(srcRoot, "composition", "parse-cli.ts"),
    join(srcRoot, "application", "commands.ts"),
  ];
  for (const file of files) {
    const text = readFileSync(file, "utf8");
    assert.equal(text.includes("OpenRouter"), false);
    assert.equal(text.includes("dispatchEffect"), false);
    assert.equal(text.includes("while (true)"), false);
  }
});

test("runCodingCommand with fake backend streams clean JSON and green exit", async () => {
  const fake: CodingBackend = {
    async invoke(request) {
      assert.equal(request.executorBand, "free");
      assert.equal(request.budgetUsdMicros, 50_000);
      assert.equal(request.plannerModel, "deepseek/deepseek-v4-flash");
      const result: CodingTerminalResult = {
        runId: "run-fake",
        outcome: "oracle_green",
        phase: "complete",
        attempts: 3,
        turns: 27,
        planDigest: "sha256:dead",
        activeStepId: null,
        verifiedStepIds: ["step-001"],
        modelRoutes: [{ role: "architect", model: request.plannerModel }],
        promptTokens: 1,
        completionTokens: 1,
        spentUsdMicros: 13400,
        detail: "ok",
        projections: [
          { kind: "plan", model: request.plannerModel, stepTotal: 1 },
          { kind: "complete", outcome: "oracle_green", turns: 27, spentUsdMicros: 13400 },
        ],
      };
      return { result, exitCode: 0 };
    },
  };
  const lines: string[] = [];
  const code = await runCodingCommand(baseRequest(), (line) => lines.push(line), fake);
  assert.equal(code, 0);
  for (const line of lines) {
    assert.equal(line.includes("\u001b"), false);
    JSON.parse(line);
  }
});

test("non-green fake backend returns non-zero", async () => {
  const fake: CodingBackend = {
    async invoke() {
      return {
        result: {
          runId: "run-2",
          outcome: "verification_failed",
          phase: "failed",
          attempts: 1,
          turns: 2,
          planDigest: null,
          activeStepId: "step-001",
          verifiedStepIds: [],
          modelRoutes: [],
          promptTokens: null,
          completionTokens: null,
          spentUsdMicros: 0,
          detail: "failed",
          projections: [{ kind: "complete", outcome: "verification_failed", turns: 2, spentUsdMicros: 0 }],
        },
        exitCode: 1,
      };
    },
  };
  const code = await runCodingCommand(baseRequest({ fakeBackend: "non-green" }), () => {}, fake);
  assert.equal(code, 1);
});

test("python coding backend doctor is real, deterministic and read-only (integration)", async () => {
  const backend = createPythonCodingBackend();
  const request = baseRequest({
    command: "doctor",
    fakeBackend: undefined,
    brief: undefined,
    interactive: false,
  });
  const { result, exitCode } = await backend.invoke(request);
  // doctor never calls a model or spends budget; it only probes the host.
  assert.ok(["completed", "unavailable"].includes(result.outcome));
  assert.equal(exitCode, result.outcome === "completed" ? 0 : 3);
  assert.equal(result.spentUsdMicros, null);
  assert.equal(result.modelRoutes.length, 0);
  const route = result.projections.find((item) => item.kind === "route");
  assert.ok(route, "doctor result must embed a route projection with host facts");
  const facts = (route as { facts?: Record<string, unknown> }).facts;
  assert.ok(facts && typeof facts.enforcement === "string");
});

test("vg doctor human line renders host facts without inventing values", () => {
  const lines = renderProjectionLines(
    [{ kind: "route", facts: { enforcement: "full", isWsl: true } }],
    { human: true }
  );
  assert.equal(lines.length, 1);
  assert.match(lines[0]!, /^\[doctor\] /);
  assert.match(lines[0]!, /enforcement="full"/);
  assert.match(lines[0]!, /isWsl=true/);
});

test("python coding backend deterministic fake reaches the runtime", async () => {
  const backend = createPythonCodingBackend();
  const { result, exitCode } = await backend.invoke(baseRequest());
  assert.equal(exitCode, 0);
  assert.equal(result.outcome, "completed");
  const kinds = result.projections.map((item) => item.kind);
  assert.ok(kinds.includes("complete"));
});
