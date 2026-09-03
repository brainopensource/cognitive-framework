/**
 * RFC 8785 JSON Canonicalization Scheme (JCS) serializer.
 * Pure TypeScript, zero external or Node.js dependencies (browser-safe).
 */
export function jcsCanonicalize(value: unknown): string {
  if (value === null || typeof value !== "object") {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return "[" + value.map((item) => jcsCanonicalize(item)).join(",") + "]";
  }
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).sort();
  const pairs = keys
    .filter((key) => obj[key] !== undefined)
    .map((key) => JSON.stringify(key) + ":" + jcsCanonicalize(obj[key]));
  return "{" + pairs.join(",") + "}";
}
