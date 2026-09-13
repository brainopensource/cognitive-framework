import type { CliOptions } from "@aether/client";
import { parseBudgetUsdToMicros } from "@aether/client";
import { existsSync } from "node:fs";

export type ParsedCli = CliOptions & {
  promptExplicit: boolean;
  budgetError?: string;
  /**
   * A flag-level parse refusal (T-97). Set when an argument cannot be bound to
   * exactly one meaning. The caller MUST report it and exit non-zero before
   * dispatching, so an ambiguous invocation never reaches a model call.
   */
  flagError?: string;
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
  "          [--token-budget N] [--effect-budget N] [--budget-usd DOLLARS] [--allow-paid] [--interactive|--benchmark]\n" +
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
  "       --budget-usd --allow-paid --interactive --benchmark --dry-plan --jsonl-out --json --question --help\n" +
  "Short flags (the only ones bound; no short flag is inferred):\n" +
  "       -h = --help    -y = --yes    -m = --model\n" +
  "       `-m` is --model and nothing else. --manifest, --model-port, --max-turns,\n" +
  "       --max-episodes and --max-replans have no short spelling; writing `-m` for\n" +
  "       one of them is refused, never silently resolved to the other.";

/**
 * The complete short-flag binding table (T-97).
 *
 * `-m` was a live ambiguity: it reads equally well as `--model`, `--manifest`,
 * `--model-port` or `--max-turns`, and the parser bound it to none of them --
 * so `vg code . -m claude-3` dropped the flag and silently appended
 * `claude-3` to the *task brief*. A wrong flag winning is bad; a flag value
 * leaking into the prompt is worse, because nothing downstream can see that it
 * happened.
 *
 * The resolution is explicit binding, not precedence: `-m` means `--model`,
 * every losing spelling has no short form at all, and anything unbound is a
 * parse error naming the long flag to write instead.
 */
export const SHORT_FLAG_BINDINGS: Readonly<Record<string, string>> = Object.freeze({
  "-h": "--help",
  "-y": "--yes",
  "-m": "--model",
});

/** Long flags a short spelling could plausibly be mistaken for. */
const SHORT_FLAG_NEAR_MISSES: Readonly<Record<string, readonly string[]>> = Object.freeze({
  "-m": ["--model", "--manifest", "--model-port", "--max-turns", "--max-episodes", "--max-replans"],
});

function isShortFlag(arg: string): boolean {
  return /^-[A-Za-z]$/.test(arg);
}

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
  // `-m` carries a value exactly as `--model` does; binding it here is what
  // stops its value being absorbed into the positional stream (T-97).
  "-m",
]);

/**
 * Does this argv ask for help?
 *
 * Help is a question, not an execution: `vg code --help` must print usage and
 * exit zero without composing a harness or calling a model. A `--help` sitting
 * in the *value* position of a value flag is that flag's value, not a request.
 */
export function wantsHelp(args: readonly string[]): boolean {
  for (let i = 0; i < args.length; i++) {
    const arg = args[i]!;
    if (arg === "--help" || arg === "-h") return true;
    if (VALUE_FLAGS.has(arg)) i++;
  }
  return false;
}

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

  // T-97. Bind short spellings explicitly, and refuse rather than guess.
  // Order matters: a refusal is reported before any value is consumed, so an
  // ambiguous invocation cannot reach a handler and call a model.
  let flagError: string | undefined;
  for (const arg of args) {
    if (!isShortFlag(arg) || arg in SHORT_FLAG_BINDINGS) continue;
    flagError =
      `unknown short flag ${arg}; short flags are never inferred. ` +
      `Bound short flags: ${Object.entries(SHORT_FLAG_BINDINGS)
        .map(([short, long]) => `${short}=${long}`)
        .join(", ")}. Write the long flag instead.`;
    break;
  }

  for (const [short, long] of Object.entries(SHORT_FLAG_BINDINGS)) {
    if (flagError || !VALUE_FLAGS.has(short) || !flag(short) || !flag(long)) continue;
    const shortValue = value(short);
    const longValue = value(long);
    if (shortValue === longValue) continue;
    const alternatives = SHORT_FLAG_NEAR_MISSES[short] ?? [long];
    flagError =
      `${short} and ${long} were both given with different values ` +
      `(${short}=${shortValue ?? "<missing>"}, ${long}=${longValue ?? "<missing>"}). ` +
      `${short} is bound to ${long} and to nothing else; it is never resolved ` +
      `to ${alternatives.filter((name) => name !== long).join(", ")}. ` +
      `Give one spelling.`;
  }

  const modelValue = value("--model") ?? value("-m");

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
    model: modelValue,
    manifest: value("--manifest") ?? "vg-code-default",
    decision,
    autoApprove: flag("--yes") || flag("-y"),
    socketPath: value("--socket-path"),
    demo,
    demoScenario,
    promptExplicit,
    plannerModel: value("--planner") ?? modelValue ?? "openrouter/free",
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
    allowPaid: flag("--allow-paid"),
    interactive: !flag("--benchmark"),
    dryPlan: flag("--dry-plan"),
    json: flag("--json"),
    jsonlOut: value("--jsonl-out"),
    question: value("--question"),
    budgetError,
    flagError,
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
