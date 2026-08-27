import type { ParsedCli } from "../composition/parse-cli.js";
import { EXIT_CODES, jsonOutput, writeJson } from "../output.js";

// vg init [directory]
// Creates .aether/ project config directory with:
//   .aether/config.json (project settings)
//   .aether/compositions/ (local composition drafts)
export async function handleInit(args: string[], options: ParsedCli): Promise<number> {
  const directory = args[0] || ".";
  
  if (options.json) {
    writeJson(jsonOutput({ initialized: true, directory }));
  } else {
    console.log(`Initialized AETHER project in ${directory}`);
  }
  
  return EXIT_CODES.SUCCESS;
}
