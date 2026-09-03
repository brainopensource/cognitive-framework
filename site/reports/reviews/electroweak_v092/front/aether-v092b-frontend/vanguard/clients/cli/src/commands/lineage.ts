import type { ParsedCli } from "../composition/parse-cli.js";
import { EXIT_CODES, jsonOutput, writeJson } from "../output.js";
import { clientFor } from "../composition/client-for.js";

// vg lineage tree <run-id> [--json]
// vg lineage inspect <lineage-id> [--json]
export async function handleLineage(args: string[], options: ParsedCli): Promise<number> {
  const subcommand = args[0];
  const client = clientFor(options);

  if (!subcommand) {
    console.error("Missing subcommand for lineage (tree, inspect)");
    return EXIT_CODES.INPUT_ERROR;
  }

  if (options.json) {
    writeJson(jsonOutput({ message: `Lineage ${subcommand} not fully implemented yet` }));
  } else {
    console.log(`Lineage ${subcommand} not fully implemented yet`);
  }

  return EXIT_CODES.SUCCESS;
}
