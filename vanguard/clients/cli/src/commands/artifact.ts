import type { ParsedCli } from "../composition/parse-cli.js";
import { EXIT_CODES, jsonOutput, writeJson } from "../output.js";
import { clientFor } from "../composition/client-for.js";

// vg artifact list <run-id> [--kind <kind>] [--json]
// vg artifact get <artifact-id> [--output <path>] [--json]
// vg artifact verify <artifact-id> [--json]
export async function handleArtifact(args: string[], options: ParsedCli): Promise<number> {
  const subcommand = args[0];
  const client = clientFor(options);

  if (!subcommand) {
    console.error("Missing subcommand for artifact (list, get, verify)");
    return EXIT_CODES.INPUT_ERROR;
  }

  if (options.json) {
    writeJson(jsonOutput({ message: `Artifact ${subcommand} not fully implemented yet` }));
  } else {
    console.log(`Artifact ${subcommand} not fully implemented yet`);
  }

  return EXIT_CODES.SUCCESS;
}
