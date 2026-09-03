import { sourceLabel } from "./theme/tokens.js";
import { selectSessionChrome, type RunViewModel, type StreamSource } from "@vanguard/client-core";

export function formatStatusBar(input: {
  source: string;
  seq?: string;
  tokens: number;
  costMicros: string;
  kind: string;
  daemon?: "running" | "not_available" | "unknown";
}): string {
  const daemon = input.daemon ?? "unknown";
  return `vg · ${sourceLabel(input.source)} · seq ${input.seq ?? "—"} · tok ${String(input.tokens)} · ${input.costMicros}µ · ${input.kind || "—"} · daemon: ${daemon}`;
}

function daemonFromEvidence(input: { source: StreamSource | "unknown"; lastKind?: string }): "running" | "not_available" | "unknown" {
  if (input.lastKind === "not_available") return "not_available";
  return "unknown";
}

export function statusBarFromView(input: {
  view: RunViewModel;
  source: StreamSource | "unknown";
  lastSeq?: string;
  lastKind?: string;
}): string {
  const chrome = selectSessionChrome({
    ...input,
    daemon: daemonFromEvidence(input),
  });
  return formatStatusBar({
    source: chrome.source,
    seq: chrome.seq,
    tokens: chrome.tokens,
    costMicros: chrome.costMicros,
    kind: chrome.kind,
    daemon: chrome.daemon,
  });
}
