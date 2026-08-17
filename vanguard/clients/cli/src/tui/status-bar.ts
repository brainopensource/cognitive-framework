import { sourceLabel } from "./theme/tokens.js";

export function formatStatusBar(input: {
  source: string;
  seq?: string;
  tokens: number;
  costMicros: string;
  kind: string;
}): string {
  return `vg · ${sourceLabel(input.source)} · seq ${input.seq ?? "—"} · tok ${String(input.tokens)} · ${input.costMicros}µ · ${input.kind || "—"}`;
}
