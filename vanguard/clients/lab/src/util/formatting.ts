export function formatSeq(seq: string | number | undefined): string {
  if (seq === undefined || seq === null) return "-";
  const str = String(seq);
  return `#${str.padStart(4, "0")}`;
}

export function formatTimestamp(isoString?: string): string {
  if (!isoString) return "-";
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toISOString().replace("T", " ").replace("Z", "");
  } catch {
    return isoString;
  }
}

export function formatRelativeTime(isoString?: string): string {
  if (!isoString) return "-";
  try {
    const d = new Date(isoString);
    const now = Date.now();
    const diff = Math.max(0, now - d.getTime());
    const seconds = Math.floor(diff / 1000);
    if (seconds < 5) return "just now";
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  } catch {
    return "-";
  }
}

export function formatDuration(ms?: number): string {
  if (ms === undefined || ms === null || isNaN(ms)) return "-";
  if (ms < 1) return `${Math.round(ms * 1000)}µs`;
  if (ms < 1000) return `${Math.round(ms)}ms`;
  const sec = (ms / 1000).toFixed(2);
  return `${sec}s`;
}

export function formatTokens(tokens?: number): string {
  if (tokens === undefined || tokens === null) return "0";
  if (tokens < 1000) return `${tokens}`;
  if (tokens < 1000000) return `${(tokens / 1000).toFixed(1)}k`;
  return `${(tokens / 1000000).toFixed(2)}M`;
}

export function formatCost(micros?: string | number): string {
  if (!micros) return "$0.00";
  const num = typeof micros === "string" ? parseInt(micros, 10) : micros;
  if (isNaN(num)) return "$0.00";
  const dollars = num / 1_000_000;
  if (dollars < 0.01 && dollars > 0) return `$${dollars.toFixed(4)}`;
  return `$${dollars.toFixed(2)}`;
}

export function formatBytes(bytes?: number): string {
  if (bytes === undefined || bytes === null || isNaN(bytes)) return "-";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function truncateDigest(digest: string, keep: number = 10): string {
  if (!digest) return "";
  if (digest.startsWith("sha256:")) {
    const raw = digest.slice(7);
    if (raw.length <= keep) return digest;
    return `sha256:${raw.slice(0, keep)}…`;
  }
  if (digest.startsWith("mhf:")) {
    const raw = digest.slice(4);
    if (raw.length <= keep) return digest;
    return `mhf:${raw.slice(0, keep)}…`;
  }
  if (digest.length <= keep + 4) return digest;
  return `${digest.slice(0, keep)}…`;
}

export function isDigest(value: unknown): boolean {
  if (typeof value !== "string") return false;
  return (
    value.startsWith("sha256:") ||
    value.startsWith("mhf:") ||
    /^[a-f0-9]{64}$/i.test(value) ||
    /^[a-f0-9]{32}$/i.test(value)
  );
}
