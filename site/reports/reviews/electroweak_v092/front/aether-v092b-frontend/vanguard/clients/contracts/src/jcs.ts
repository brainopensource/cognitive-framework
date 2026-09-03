/**
 * Deterministic JSON Canonicalization Scheme (RFC 8785 / JCS).
 * Matches Python's `governance/approvals.py:OperatorSigner.canonical_bytes`
 * and standard JCS implementations.
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
  const pairs: string[] = [];
  for (const key of keys) {
    if (obj[key] !== undefined) {
      pairs.push(JSON.stringify(key) + ":" + jcsCanonicalize(obj[key]));
    }
  }
  return "{" + pairs.join(",") + "}";
}
