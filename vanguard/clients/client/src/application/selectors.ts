import type { StreamSource } from "@aether/contracts";
import type { RunViewModel } from "./run-view.js";

export type StatusBarModel = {
  source: StreamSource | "unknown";
  seq: string;
  tokens: number;
  costMicros: string;
  kind: string;
};

export function selectStatusBar(input: {
  view: RunViewModel;
  source: StreamSource | "unknown";
  lastSeq?: string;
  lastKind?: string;
}): StatusBarModel {
  return {
    source: input.source,
    seq: input.lastSeq ?? "0",
    tokens: input.view.tokens,
    costMicros: input.view.costMicros,
    kind: input.lastKind ?? input.view.lastKind ?? "",
  };
}

export type TranscriptRow =
  | { kind: "thought"; text: string }
  | { kind: "tool"; name: string; status: string }
  | { kind: "opaque"; label: string };

export function windowTranscript(
  view: RunViewModel,
  cursor: number,
  height: number = 16
): { rows: TranscriptRow[]; cursor: number; total: number } {
  const allRows: TranscriptRow[] = [
    ...view.thoughts.map((text): TranscriptRow => ({ kind: "thought", text })),
    ...view.tools.map((t): TranscriptRow => ({ kind: "tool", name: t.name, status: t.status })),
  ];
  const total = allRows.length;
  const clampedHeight = Math.max(1, height);
  const maxCursor = Math.max(0, total - clampedHeight);
  const clampedCursor = Math.min(Math.max(0, cursor), maxCursor);
  const rows = allRows.slice(clampedCursor, clampedCursor + clampedHeight);

  return {
    rows,
    cursor: clampedCursor,
    total,
  };
}

export type SessionChromeModel = StatusBarModel & {
  runId: string;
  daemon: "running" | "not_available" | "unknown";
};

export function selectSessionChrome(input: {
  view: RunViewModel;
  source: StreamSource | "unknown";
  lastSeq?: string;
  lastKind?: string;
  runId?: string;
  daemon?: "running" | "not_available" | "unknown";
}): SessionChromeModel {
  const statusBar = selectStatusBar(input);
  return {
    ...statusBar,
    runId: input.runId ?? "",
    daemon: input.daemon ?? "unknown",
  };
}
