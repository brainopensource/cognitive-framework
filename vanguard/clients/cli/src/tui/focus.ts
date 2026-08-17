import type { Result } from "@vanguard/client-core";

export type TuiMode = "prompt" | "approval" | "correct" | "help" | "run";

export const HELP_TEXT = [
  "vg keys",
  "  type + Enter   start run with brief (empty Enter = invalid_request)",
  "  Tab            focus prompt <-> run",
  "  y / n / c      approve / reject / correct (approval mode only)",
  "  j k / PgUp PgDn  scroll transcript (run mode)",
  "  w              explain selected tool (why); shows not_available if empty",
  "  ctrl+c         requestCancel",
  "  Esc            requestCancel unless prompt or help",
  "  ?              toggle this help",
  "  q              quit (not while typing a brief)",
].join("\n");

export function shouldDispatchApproval(mode: TuiMode, key: string): boolean {
  return mode === "approval" && (key === "y" || key === "n");
}

export function shouldEnterCorrect(mode: TuiMode, key: string): boolean {
  return mode === "approval" && key === "c";
}

export function submitBrief(brief: string): Result<{ brief: string }> {
  const trimmed = brief.trim();
  if (!trimmed) {
    return { ok: false, error: { code: "invalid_request", message: "empty brief", retryable: false } };
  }
  return { ok: true, value: { brief: trimmed } };
}

export function shouldRequestCancel(mode: TuiMode, event: { ctrlC: boolean; escape: boolean }): boolean {
  if (event.ctrlC) return true;
  if (event.escape && mode !== "prompt" && mode !== "help") return true;
  return false;
}

export function shouldQuit(mode: TuiMode, input: string): boolean {
  return input === "q" && mode !== "prompt";
}

export function modeAfterPendingApproval(mode: TuiMode, pending: boolean): TuiMode {
  if (pending && mode !== "correct" && mode !== "help") return "approval";
  if (!pending && mode === "approval") return "run";
  return mode;
}

export function toggleHelp(mode: TuiMode, previous: TuiMode): TuiMode {
  return mode === "help" ? previous : "help";
}
