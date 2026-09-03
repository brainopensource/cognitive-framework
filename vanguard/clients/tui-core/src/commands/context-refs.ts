import { existsSync, readFileSync, statSync } from "node:fs";
import { join, isAbsolute } from "node:path";

export interface FileReference {
  readonly raw: string;
  readonly resolvedPath: string;
  readonly found: boolean;
  readonly truncated: boolean;
}

export interface ExpandedPrompt {
  readonly text: string;
  readonly references: readonly FileReference[];
}

const REF_PATTERN = /@([^\s]+)/g;
const MAX_BYTES_PER_FILE = 8_000;

/**
 * Expands "@path/to/file" references in a composer prompt into inline file
 * content before the prompt is sent, per Hermes/opencode's "@file fuzzy
 * refs" convention (W1's SOTA command set). This is on-submit inline
 * expansion, not a live fuzzy-search popup -- the existing hand-rolled
 * renderer has no autocomplete surface to drive one from.
 */
export function expandFileReferences(text: string, cwd: string): ExpandedPrompt {
  const references: FileReference[] = [];
  const blocks: string[] = [];

  const expanded = text.replace(REF_PATTERN, (match, rawPath: string) => {
    const resolvedPath = isAbsolute(rawPath) ? rawPath : join(cwd, rawPath);
    const found = existsSync(resolvedPath) && statSync(resolvedPath).isFile();
    let truncated = false;

    if (found) {
      let content = readFileSync(resolvedPath, "utf-8");
      if (content.length > MAX_BYTES_PER_FILE) {
        content = content.slice(0, MAX_BYTES_PER_FILE);
        truncated = true;
      }
      blocks.push(`--- ${rawPath} ---\n${content}${truncated ? "\n[truncated]" : ""}`);
    }

    references.push({ raw: rawPath, resolvedPath, found, truncated });
    return match;
  });

  if (blocks.length === 0) {
    return { text, references };
  }

  return {
    text: `${expanded}\n\n${blocks.join("\n\n")}`,
    references,
  };
}
