/**
 * RFC 8785 (JCS) canonical JSON — TypeScript reader.
 *
 * Owning contract: VG-04 §0.3 / `CT-04`, `SC-2`, `REQ-SCHEMA-001`.
 *
 * Pure values only: no I/O, no clock, no randomness, no environment access
 * (`system-architecture-icd.md` §2, `domain` row).
 *
 * `JSON.stringify` already implements the ECMAScript number and string rules
 * RFC 8785 adopts by reference, so scalars delegate to it; structure, key
 * ordering and the rejection rules are implemented here.
 */

export type JsonValue =
  | null
  | boolean
  | number
  | string
  | JsonValue[]
  | { [key: string]: JsonValue };

export class CanonicalisationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CanonicalisationError";
  }
}

const MAX_DEPTH = 128;
const LONE_SURROGATE = /[\uD800-\uDBFF](?![\uDC00-\uDFFF])|(?<![\uD800-\uDBFF])[\uDC00-\uDFFF]/;

/** Escape a string per RFC 8785 §3.2.2.2. */
export function serialiseString(value: string): string {
  if (LONE_SURROGATE.test(value)) {
    // `CT-13`: UTF-8 throughout, no lone surrogates. There is no canonical
    // form to produce, so fail rather than emit a replacement character.
    throw new CanonicalisationError("lone surrogate is not valid UTF-8 (CT-13)");
  }
  return JSON.stringify(value);
}

/** Serialise a JSON number per RFC 8785 §3.2.2.3. */
export function serialiseNumber(value: number): string {
  if (!Number.isFinite(value)) {
    throw new CanonicalisationError("NaN and Infinity have no JSON form");
  }
  // Every JSON number is an IEEE-754 double here, including integer-valued
  // ones past 2^53-1. Rejecting those would be a local variation on RFC 8785
  // that no other reader shares (VG-04 §0.3); keeping a field inside the safe
  // range is the schema layer's job, via `IntString` (VG-04 §0.4, `CT-06`).
  return JSON.stringify(value === 0 ? 0 : value);
}

/** RFC 8785 §3.2.3 sorts keys by UTF-16 code unit, which is `<` on strings. */
function byCodeUnit(a: string, b: string): number {
  return a < b ? -1 : a > b ? 1 : 0;
}

function serialise(value: unknown, depth: number): string {
  if (depth > MAX_DEPTH) {
    throw new CanonicalisationError("nesting deeper than 128 levels");
  }
  if (value === null) return "null";
  switch (typeof value) {
    case "boolean":
      return value ? "true" : "false";
    case "string":
      return serialiseString(value);
    case "number":
      return serialiseNumber(value);
    case "object":
      break;
    default:
      throw new CanonicalisationError(`${typeof value} has no JSON form`);
  }
  if (Array.isArray(value)) {
    return `[${value.map((item) => serialise(item, depth + 1)).join(",")}]`;
  }
  const record = value as Record<string, unknown>;
  const keys = Object.keys(record).sort(byCodeUnit);
  const members = keys.map(
    (key) => `${serialiseString(key)}:${serialise(record[key], depth + 1)}`,
  );
  return `{${members.join(",")}}`;
}

/** Canonical JSON text for an already-parsed JSON value. */
export function canonicalise(value: unknown): string {
  return serialise(value, 0);
}

/** Canonical UTF-8 bytes — the input to every digest (`SC-2`). */
export function canonicalBytes(value: unknown): Uint8Array {
  return new TextEncoder().encode(canonicalise(value));
}

/**
 * Reject duplicate object keys.
 *
 * `JSON.parse` keeps the last of a duplicate pair silently, and the reviver
 * runs over the collapsed result, so the only place a duplicate is still
 * visible is the source text. The scan assumes the text already parsed.
 */
function rejectDuplicateKeys(text: string): void {
  const stack: Array<{ object: boolean; keys: Set<string> }> = [];
  let expectKey = false;
  let index = 0;
  while (index < text.length) {
    const char = text[index];
    if (char === '"') {
      let end = index + 1;
      while (end < text.length) {
        if (text[end] === "\\") end += 2;
        else if (text[end] === '"') break;
        else end += 1;
      }
      if (expectKey) {
        const frame = stack[stack.length - 1]!;
        const key = JSON.parse(text.slice(index, end + 1)) as string;
        if (frame.keys.has(key)) {
          throw new CanonicalisationError(`duplicate object key ${JSON.stringify(key)}`);
        }
        frame.keys.add(key);
        expectKey = false;
      }
      index = end + 1;
      continue;
    }
    if (char === "{" || char === "[") {
      stack.push({ object: char === "{", keys: new Set() });
      expectKey = char === "{";
    } else if (char === "}" || char === "]") {
      stack.pop();
      expectKey = false;
    } else if (char === ",") {
      expectKey = stack.length > 0 && stack[stack.length - 1]!.object;
    }
    index += 1;
  }
}

/** Parse JSON text, rejecting the forms RFC 8785 cannot canonicalise. */
export function parseJsonText(text: string): JsonValue {
  let parsed: JsonValue;
  try {
    parsed = JSON.parse(text) as JsonValue;
  } catch (error) {
    throw new CanonicalisationError(`invalid JSON: ${(error as Error).message}`);
  }
  rejectDuplicateKeys(text);
  return parsed;
}

/** Parse then canonicalise JSON text in one step. */
export function canonicaliseText(text: string): string {
  return canonicalise(parseJsonText(text));
}
