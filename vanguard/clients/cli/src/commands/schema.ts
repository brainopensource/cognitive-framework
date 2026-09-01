import type { ParsedCli } from "../composition/parse-cli.js";
import { EXIT_CODES, jsonOutput, writeJson } from "../output.js";
import { clientFor } from "../composition/client-for.js";

// vg schema list [--json]
// vg schema show <schema-id> [--json]
// vg schema check [--json] (contract compatibility check)
export async function handleSchema(args: string[], options: ParsedCli): Promise<number> {
  const subcommand = args[0];
  const client = await clientFor(options);

  if (!subcommand) {
    console.error("Missing subcommand for schema (list, show, check)");
    return EXIT_CODES.INPUT_ERROR;
  }

  if (options.json) {
    writeJson(jsonOutput({ message: `Schema ${subcommand} not fully implemented yet` }));
  } else {
    console.log(`Schema ${subcommand} not fully implemented yet`);
  }

  return EXIT_CODES.SUCCESS;
}
