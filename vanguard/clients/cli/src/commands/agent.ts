import type { ParsedCli } from "../composition/parse-cli.js";
import { EXIT_CODES, jsonOutput, writeJson } from "../output.js";
import { clientFor } from "../composition/client-for.js";

// vg agent list [--json]
// vg agent show <agent-id> [--json]
// vg agent validate <manifest-path> [--json]
// vg agent pack <manifest-path> [--output <path>]
export async function handleAgent(args: string[], options: ParsedCli): Promise<number> {
  const subcommand = args[0];
  const client = clientFor(options);

  if (!subcommand) {
    console.error("Missing subcommand for agent (list, show, validate, pack)");
    return EXIT_CODES.INPUT_ERROR;
  }

  if (options.json) {
    writeJson(jsonOutput({ message: `Agent ${subcommand} not fully implemented yet` }));
  } else {
    console.log(`Agent ${subcommand} not fully implemented yet`);
  }

  return EXIT_CODES.SUCCESS;
}
