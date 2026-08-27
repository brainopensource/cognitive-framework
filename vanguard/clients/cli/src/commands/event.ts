import type { ParsedCli } from "../composition/parse-cli.js";
import { EXIT_CODES, jsonOutput, writeJson } from "../output.js";
import { clientFor } from "../composition/client-for.js";

// vg event tail <run-id> [--follow] [--kind <kind>] [--lineage <id>] [--json]
// vg event show <event-id> [--json]
// vg event verify <event-id> [--json]
export async function handleEvent(args: string[], options: ParsedCli): Promise<number> {
  const subcommand = args[0];
  const client = clientFor(options);

  if (!subcommand) {
    console.error("Missing subcommand for event (tail, show, verify)");
    return EXIT_CODES.INPUT_ERROR;
  }

  if (options.json) {
    writeJson(jsonOutput({ message: `Event ${subcommand} not fully implemented yet` }));
  } else {
    console.log(`Event ${subcommand} not fully implemented yet`);
  }

  return EXIT_CODES.SUCCESS;
}
