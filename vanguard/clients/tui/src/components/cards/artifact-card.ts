import type { TerminalScreen } from "../../terminal/screen.js";
import { DEFAULT_THEME, type ThemeTokens } from "../../theme.js";

export function renderArtifactCard(
  screen: TerminalScreen,
  row: number,
  digest: string,
  kind: string,
  path?: string,
  theme: ThemeTokens = DEFAULT_THEME
): number {
  const shortDigest = digest.startsWith("sha256:") ? digest.slice(0, 15) + "…" : digest.slice(0, 10);
  const text = `📦 Artifact [${kind}]: ${path ?? shortDigest}`;
  screen.writeString(row, 2, text, theme.accent);
  return 1;
}
