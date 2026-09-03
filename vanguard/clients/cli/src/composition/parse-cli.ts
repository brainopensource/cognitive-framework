import type { CliOptions } from "@aether/client";
import { parseBudgetUsdToMicros } from "@aether/client";
import { existsSync } from "node:fs";

export type ParsedCli = CliOptions & {
  promptExplicit: boolean;
  budgetError?: string;
};

export const USAGE =
  "Usage:\n" +
  "  aether | vg                  interactive TUI in the current directory\n" +
  "  vg daemon start|status|stop\n" +
  "  vg run [repo] [--headless] [--prompt <text>] [--brief <text>] [--model <id>] [--manifest <path>]\n" +
  "          [--run-id <id>] [--resume <id>] [--checkpoint-every <n>] [--socket-path <path>]\n" +
  "          [--demo [scenario]] [--replay <file.jsonl>] [--scenario] [--feed] [--yes|-y]\n" +
  "  vg code PATH [--brief TASK.md] [--planner MODEL] [--provider PROVIDER] [--model-port PORT]\n" +
  "          [--executor-band free|medium|high] [--recovery-model MODEL] [--profile PROFILE]\n" +
  "          [--wal-path PATH] [--store-path PATH] [--max-turns N] [--max-episodes N] [--max-replans N]\n" +
  "          [--token-budget N] [--effect-budget N] [--budget-usd DOLLARS] [--interactive|--benchmark]\n" +
  "          [--dry-plan] [--resume RUN_ID] [--jsonl-out PATH] [--json] [--headless]\n" +
  "  vg explain PATH --question TEXT [--headless] [--json]\n" +
  "  vg doctor [PATH] [--headless] [--json]\n" +
  "  vg approve <run-id> --decision approve|reject\n" +
  "  vg resume <run-id> [--headless] [--wal-path PATH]\n" +
  "  vg trace <run-id> [--headless] [--replay <file.jsonl>] [--demo [scenario]]\n" +
  "  vg why <artifact> [--headless] [--replay <file.jsonl>] [--demo [scenario]]\n" +
  "Flags: --headless --feed --scenario --demo --replay --run-id --resume --checkpoint-every\n" +
  "       --repo --workspace --prompt --brief --model --manifest --decision --socket-path --yes|-y\n" +
  "       --planner --provider --model-port --executor-band --recovery-model --profile\n" +
  "       --wal-path --store-path --token-budget --effect-budget --max-turns --max-episodes --max-replans\n" +
  "       --budget-usd --interactive --benchmark --dry-plan --jsonl-out --json --question --help";

export function usage(): never {
  console.error(USAGE);
  process.exit(2);
}

const VALUE_FLAGS = new Set([
  "--replay",
  "--run-id",
  "--resume",
  "--checkpoint-every",
  "--repo",
  "--workspace",
  "--prompt",
  "--brief",
  "--model",
  "--manifest",
  "--decision",
  "--socket-path",
  "--planner",
  "--provider",
  "--model-port",
  "--profile",
  "--wal-path",
  "--store-path",
  "--token-budget",
  "--effect-budget",
  "--executor-band",
  "--recovery-model",
  "--max-turns",
  "--max-episodes",
  "--max-replans",
  "--budget-usd",
  "--jsonl-out",
  "--question",
]);

export function parseCliOptions(args: string[]): ParsedCli {
  const value = (name: string) => {
    const index = args.indexOf(name);
    return index >= 0 && index + 1 < args.length ? args[index + 1] : undefined;
  };
  const flag = (name: string) => args.includes(name);

  const positional: string[] = [];
  let demo = false;
  let demoScenario: string | undefined;
  for (let i = 0; i < args.length; i++) {
    const arg = args[i]!;
    if (arg === "--demo") {
      demo = true;
      const next = args[i + 1];
      if (next && !next.startsWith("-")) {
        demoScenario = next;
        i++;
      }
      continue;
    }
    if (arg.startsWith("--") || arg.startsWith("-")) {
      if (VALUE_FLAGS.has(arg)) i++;
      continue;
    }
    positional.push(arg);
  }

  const promptFromFlags = value("--prompt") ?? value("--brief");
  let prompt = promptFromFlags;
  let repo = value("--workspace") ?? value("--repo");
  const decisionVal = value("--decision");
  const decision: "approve" | "reject" | undefined =
    decisionVal === "approve" || decisionVal === "reject" ? decisionVal : undefined;

  if (positional.length > 0) {
    if (!prompt && !repo) {
      if (positional[0]!.startsWith(".") || positional[0]!.includes("/") || positional[0] === ".") {
        repo = positional[0];
        if (positional.length > 1) prompt = positional.slice(1).join(" ");
      } else {
        // First positional for `code`/`explain` is always the workspace path.
        repo = positional[0];
        if (positional.length > 1) prompt = positional.slice(1).join(" ");
      }
    } else if (!prompt && repo) {
      prompt = positional.join(" ");
    } else if (prompt && !repo) {
      repo = positional[0];
    }
  }

  const promptExplicit = Boolean(prompt);
  const budgetRaw = value("--budget-usd");
  let budgetUsdMicros: number | undefined;
  let budgetError: string | undefined;
  if (budgetRaw !== undefined) {
    const parsedBudget = parseBudgetUsdToMicros(budgetRaw);
    if (parsedBudget.ok) budgetUsdMicros = parsedBudget.micros;
    else budgetError = parsedBudget.error.message;
  }

  const intOr = (raw: string | undefined, fallback: number) => {
    if (raw === undefined) return fallback;
    const n = Number(raw);
    return Number.isFinite(n) && n >= 0 ? Math.floor(n) : fallback;
  };

  return {
    headless: flag("--headless"),
    feed: flag("--feed"),
    scenario: flag("--scenario"),
    prompt: prompt ?? "Execute default coding task",
    brief: value("--brief") ?? prompt ?? "Execute default coding task",
    repo: repo ?? ".",
    runId: value("--run-id") ?? (positional[0] && !prompt ? positional[0] : undefined),
    resumeFrom: value("--resume"),
    checkpointEvery: Number(value("--checkpoint-every") ?? 2),
    replay: value("--replay"),
    model: value("--model"),
    manifest: value("--manifest") ?? "vg-code-default",
    decision,
    autoApprove: flag("--yes") || flag("-y"),
    socketPath: value("--socket-path"),
    demo,
    demoScenario,
    promptExplicit,
    plannerModel: value("--planner") ?? value("--model") ?? "openrouter/free",
    modelPort: value("--model-port") ?? value("--provider"),
    storePath: value("--store-path") ?? value("--wal-path"),
    profile: value("--profile"),
    tokenBudget: intOr(value("--token-budget"), undefined as unknown as number),
    effectBudget: intOr(value("--effect-budget"), undefined as unknown as number),
    executorBand: value("--executor-band") ?? "free",
    recoveryModel: value("--recovery-model") ?? "openrouter/free",
    maxTurns: intOr(value("--max-turns"), 40),
    maxEpisodes: intOr(value("--max-episodes"), 12),
    maxReplans: intOr(value("--max-replans"), 2),
    budgetUsdMicros,
    interactive: !flag("--benchmark"),
    dryPlan: flag("--dry-plan"),
    json: flag("--json"),
    jsonlOut: value("--jsonl-out"),
    question: value("--question"),
    budgetError,
  };
}

const CLI_COMMANDS = new Set([
  "run",
  "agent",
  "workflow",
  "artifact",
  "event",
  "approve",
  "doctor",
  "daemon",
  "config",
  "provider",
  "model",
  "workspace",
  "history",
  "attach",
  "code",
  "explain",
  "resume",
  "trace",
  "why",
  "init",
  "composition",
  "schema",
  "lineage",
]);

/** Map a bare `aether` / `vg` invocation onto `run .` without stealing --help. */
export function normalizeArgv(argv: string[]): string[] {
  if (argv.length === 0) return ["run", "."];
  const head = argv[0]!;
  if (head === "--help" || head === "-h") return argv;
  if (CLI_COMMANDS.has(head)) return argv;
  if (head.startsWith("-")) return ["run", ".", ...argv];
  if (existsSync(head)) return ["run", ...argv];
  return argv;
}
