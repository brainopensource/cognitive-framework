import type { CliOptions } from "@vanguard/client-core";

export type ParsedCli = CliOptions & { promptExplicit: boolean };

export const USAGE =
  "Usage:\n" +
  "  vg daemon start|status|stop\n" +
  "  vg run [repo] [--headless] [--prompt <text>] [--brief <text>] [--model <id>] [--manifest <path>]\n" +
  "          [--run-id <id>] [--resume <id>] [--checkpoint-every <n>] [--socket-path <path>]\n" +
  "          [--demo [scenario]] [--replay <file.jsonl>] [--scenario] [--feed] [--yes|-y]\n" +
  "  vg approve <run-id> --decision approve|reject\n" +
  "  vg resume <run-id> [--headless]\n" +
  "  vg trace <run-id> [--headless] [--replay <file.jsonl>] [--demo [scenario]]\n" +
  "  vg why <artifact> [--headless] [--replay <file.jsonl>] [--demo [scenario]]\n" +
  "Flags: --headless --feed --scenario --demo --replay --run-id --resume --checkpoint-every\n" +
  "       --repo --prompt --brief --model --manifest --decision --socket-path --yes|-y --help";

export function usage(): never {
  console.error(USAGE);
  process.exit(2);
}

export function parseCliOptions(args: string[]): ParsedCli {
  const value = (name: string) => {
    const index = args.indexOf(name);
    return index >= 0 && index + 1 < args.length ? args[index + 1] : undefined;
  };
  const flag = (name: string) => args.includes(name);

  const flagNamesWithVal = new Set([
    "--replay",
    "--run-id",
    "--resume",
    "--checkpoint-every",
    "--repo",
    "--prompt",
    "--brief",
    "--model",
    "--manifest",
    "--decision",
    "--socket-path",
  ]);

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
      if (flagNamesWithVal.has(arg)) i++;
      continue;
    }
    positional.push(arg);
  }

  const promptFromFlags = value("--prompt") ?? value("--brief");
  let prompt = promptFromFlags;
  let repo = value("--repo");
  const decisionVal = value("--decision");
  const decision: "approve" | "reject" | undefined =
    decisionVal === "approve" || decisionVal === "reject" ? decisionVal : undefined;

  if (positional.length > 0) {
    if (!prompt && !repo) {
      if (positional[0]!.startsWith(".") || positional[0]!.includes("/")) {
        repo = positional[0];
        if (positional.length > 1) prompt = positional.slice(1).join(" ");
      } else {
        prompt = positional.join(" ");
      }
    } else if (!prompt && repo) {
      prompt = positional.join(" ");
    } else if (prompt && !repo) {
      repo = positional[0];
    }
  }

  const promptExplicit = Boolean(prompt);

  return {
    headless: flag("--headless"),
    feed: flag("--feed"),
    scenario: flag("--scenario"),
    prompt: prompt ?? "Execute default coding task",
    brief: prompt ?? "Execute default coding task",
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
  };
}
