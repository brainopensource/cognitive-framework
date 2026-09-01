import type { ParsedCli } from "../composition/parse-cli.js";
import { EXIT_CODES, jsonOutput, writeJson } from "../output.js";
import { clientFor } from "../composition/client-for.js";

// vg composition list [--json]
// vg composition validate <path> [--json]
// vg composition freeze <composition-id> [--json]
// vg composition diff <id-a> <id-b> [--json]
// vg composition activate <composition-id> [--json]
export async function handleComposition(args: string[], options: ParsedCli): Promise<number> {
  const subcommand = args[0];
  const client = await clientFor(options);

  if (!subcommand) {
    console.error("Missing subcommand for composition (list, validate, freeze, diff, activate)");
    return EXIT_CODES.INPUT_ERROR;
  }

  if (options.json) {
    writeJson(jsonOutput({ message: `Composition ${subcommand} not fully implemented yet` }));
  } else {
    console.log(`Composition ${subcommand} not fully implemented yet`);
  }

  return EXIT_CODES.SUCCESS;
}
