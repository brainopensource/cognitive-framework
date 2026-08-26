import type { StudioFold } from "./fold.js";

export type StudioSurface =
  | "coding"
  | "builder"
  | "workbench"
  | "context"
  | "lineage"
  | "generality"
  | "experiments"
  | "evolution"
  | "ledger"
  | "theatre"
  | "evidence"
  | "map"
  | "studio"
  | "effect"
  | "arena"
  | "watch"
  | "brain";

export type StudioSessionState = {
  readonly activeSurface: StudioSurface;
  readonly activeMilestone: "M-1" | "M-2" | "M-3C" | "M-4" | "M-5a" | "M-5b" | "M-6" | "M-6.5" | "M-7" | "M-8" | "ALL";
  readonly density: "operate" | "watch";
  readonly theme: "dark" | "light";
  readonly selectedSeq: bigint;
  readonly selectedTurnNumber?: number;
  readonly selectedEffectDescriptor?: string;
  readonly selectedSpanId?: string;
  readonly isScrubbing: boolean;
  readonly filterQuery: string;
  readonly isCommandPaletteOpen: boolean;
};

export const INITIAL_SESSION_STATE: StudioSessionState = {
  activeSurface: "coding",
  activeMilestone: "ALL",
  density: "operate",
  theme: "dark",
  selectedSeq: 0n,
  isScrubbing: false,
  filterQuery: "",
  isCommandPaletteOpen: false,
};

export function selectActiveEffect(fold: StudioFold, descriptor?: string) {
  if (!descriptor) return undefined;
  return fold.effects.get(descriptor);
}

export function selectActiveTurn(fold: StudioFold, turnNumber?: number) {
  if (turnNumber === undefined) return undefined;
  return fold.turns.find((t) => t.turnNumber === turnNumber);
}

export function formatMicrosToUsd(micros: bigint | string | number): string {
  const n = typeof micros === "bigint" ? Number(micros) : Number(micros);
  return `$${(n / 1_000_000).toFixed(4)}`;
}

export function formatDigestShort(digest?: string): string {
  if (!digest) return "";
  if (digest.length <= 16) return digest;
  return `${digest.slice(0, 8)}…${digest.slice(-6)}`;
}
