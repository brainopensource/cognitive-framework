export const theme = {
  accent: "cyan",
  warning: "yellow",
  danger: "red",
  muted: undefined,
} as const;

export function sourceLabel(source: string): string {
  if (source === "mock" || source === "replay") return `source: mock`;
  return `source: ${source}`;
}
