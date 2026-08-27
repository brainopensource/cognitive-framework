#!/usr/bin/env node
import type { RuntimeClient } from "@vanguard/client-core";
import { parseCliOptions, usage, USAGE } from "./composition/parse-cli.js";
import { COMMANDS } from "./commands/index.js";

process.stdout.on("error", (error) => {
  if ((error as NodeJS.ErrnoException).code === "EPIPE") process.exit(0);
});

const argv = process.argv.slice(2);
if (!argv[0] || argv[0] === "--help" || argv[0] === "-h") {
  console.error(USAGE);
  process.exit(argv[0] ? 0 : 2);
}

const [command, ...rest] = argv;
const parsed = parseCliOptions(rest);

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
  command === "daemon" ||
  command === "approve" ||
  command === "trace" ||
  command === "why" ||
  command === "resume" ||
  command === "code" ||
  command === "explain" ||
  command === "doctor"
) {
  process.exit(exitCode);
}
