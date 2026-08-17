import type { RunViewModel } from "@vanguard/client-core";

export type TranscriptRow =
  | { kind: "thought"; text: string }
  | { kind: "tool"; name: string; status: string };

export const DEFAULT_TRANSCRIPT_HEIGHT = 16;

export function windowTranscript(
  view: RunViewModel,
  cursor: number,
  height: number = DEFAULT_TRANSCRIPT_HEIGHT
): { rows: TranscriptRow[]; cursor: number; total: number } {
  const rows: TranscriptRow[] = [
    ...view.thoughts.map((text) => ({ kind: "thought" as const, text })),
    ...view.tools.map((tool) => ({ kind: "tool" as const, name: tool.name, status: tool.status })),
  ];
  const total = rows.length;
  const h = Math.max(1, height);
  const maxCursor = Math.max(0, total - h);
  const clamped = Math.min(Math.max(0, cursor), maxCursor);
  return { rows: rows.slice(clamped, clamped + h), cursor: clamped, total };
}

export function moveTranscriptCursor(
  cursor: number,
  total: number,
  height: number,
  delta: number
): number {
  const h = Math.max(1, height);
  const maxCursor = Math.max(0, total - h);
  return Math.min(Math.max(0, cursor + delta), maxCursor);
}
