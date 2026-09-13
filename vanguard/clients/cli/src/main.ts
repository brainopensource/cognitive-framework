#!/usr/bin/env node
import type { RuntimeClient } from "@aether/client";
import { parseCliOptions, usage, USAGE, normalizeArgv, wantsHelp } from "./composition/parse-cli.js";
import { COMMANDS } from "./commands/index.js";

// EPIPE signal handling: silent clean exit code 0 when pipe closes (e.g. | head -n 5)
process.stdout.on("error", (error) => {
  if ((error as NodeJS.ErrnoException).code === "EPIPE") {
    process.exit(0);
  }
});

// Interrupt signals: deterministic exit code 130
process.on("SIGINT", () => {
  process.exit(130);
});
process.on("SIGTERM", () => {
  process.exit(130);
});

const argv = normalizeArgv(process.argv.slice(2));

// T-97. Help is a question, not an execution. `vg --help` already exited zero;
// `vg code --help` used to fall through to the coding handler, compose a
// harness and print a completion frame (`[complete] instrument_error`) before
// exiting 3. Answering help here -- for every subcommand, before a handler is
// resolved -- means no model call, no ledger and no fabricated frame.
if (wantsHelp(argv)) {
  console.log(USAGE);
  process.exit(0);
}

const [command, ...rest] = argv;

const parsed = parseCliOptions(rest);

// T-97. An argument that cannot be bound to exactly one meaning is refused
// here, before dispatch, so no ambiguous invocation reaches a model call.
if (parsed.flagError) {
  console.error(parsed.flagError);
  process.exit(2);
}

// Support --output json as alias to --json
if (rest.includes("--output") && rest[rest.indexOf("--output") + 1] === "json") {
  parsed.json = true;
  parsed.headless = true;
}

const handler = COMMANDS[command];

if (!handler) {
  usage();
}

let exitCode = 0;
try {
  exitCode = await handler(rest, parsed);
} catch (err) {
  console.error(err);
  exitCode = 1;
}

process.exitCode = exitCode;
if (
  parsed.headless ||
  parsed.json ||
  parsed.feed ||
  command === "daemon" ||
  command === "approve" ||
  command === "trace" ||
  command === "why" ||
  command === "resume" ||
  command === "code" ||
  command === "explain" ||
  command === "doctor" ||
  command === "agent" ||
  command === "workflow" ||
  command === "artifact" ||
  command === "event" ||
  command === "config" ||
  command === "provider" ||
  command === "model" ||
  command === "workspace" ||
  command === "history" ||
  command === "attach" ||
  command === "run"
) {
  process.exit(exitCode);
}
