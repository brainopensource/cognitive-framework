/**
 * Opaque, boundary-parsed primitives — TypeScript reader.
 *
 * Owning contract: VG-04 §1 / `CT-03`, `CT-06`..`CT-10`, `CT-14`..`CT-16`;
 * `schemas/v4/primitives.schema.json`; `REQ-SCHEMA-002`.
 *
 * Identifiers are branded, so `PrincipalId` and `EpisodeId` are distinct at
 * compile time even though both are strings on the wire (VG-04 §1). A brand
 * cannot be produced by assertion — `parse` is the only constructor
 * (`CT-03`).
 */

export class ParseError extends Error {
  readonly kind: string;
  readonly code: string;

  constructor(kind: string, code: string, message: string) {
    super(`${kind}: ${message}`);
    this.name = "ParseError";
    this.kind = kind;
    this.code = code;
  }
}

declare const brand: unique symbol;
export type Branded<Kind extends string, Carrier> = Carrier & {
  readonly [brand]: Kind;
};

export type Timestamp = Branded<"Timestamp", string>;
export type Digest = Branded<"Digest", string>;
export type IntString = Branded<"IntString", string>;
export type UsdMicros = Branded<"UsdMicros", string>;
export type Millis = Branded<"Millis", number>;
export type BranchId = Branded<"BranchId", number>;
export type Uuidv7 = Branded<"Uuidv7", string>;
export type PrincipalId = Branded<"PrincipalId", string>;
export type EpisodeId = Branded<"EpisodeId", string>;
export type ProcessId = Branded<"ProcessId", string>;
export type RunId = Branded<"RunId", string>;
export type GrantId = Branded<"GrantId", string>;

type Checker = (kind: string, value: unknown) => string | number;

const TIMESTAMP = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;
const DIGEST = /^sha256:[0-9a-f]{64}$/;
const INT_STRING = /^(0|[1-9][0-9]*)$/;
const UUIDV7 = /^[0-9a-f]{8}-[0-9a-f]{4}-7[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;

const DAYS_IN_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

function isLeap(year: number): boolean {
  return year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0);
}

function checkTimestamp(kind: string, value: unknown): string {
  if (typeof value !== "string") {
    throw new ParseError(kind, "type", `expected string, got ${typeof value}`);
  }
  if (!TIMESTAMP.test(value)) {
    throw new ParseError(kind, "pattern", `not RFC 3339 UTC millisecond form: ${value}`);
  }
  const year = Number(value.slice(0, 4));
  const month = Number(value.slice(5, 7));
  const day = Number(value.slice(8, 10));
  const hour = Number(value.slice(11, 13));
  const minute = Number(value.slice(14, 16));
  const second = Number(value.slice(17, 19));
  if (month < 1 || month > 12) {
    throw new ParseError(kind, "semantic", `month ${month} out of range`);
  }
  const limit = DAYS_IN_MONTH[month - 1]! + (month === 2 && isLeap(year) ? 1 : 0);
  if (day < 1 || day > limit) {
    throw new ParseError(kind, "semantic", `day ${day} out of range for month ${month}`);
  }
  if (hour > 23 || minute > 59) {
    throw new ParseError(kind, "semantic", "time out of range");
  }
  if (second > 59) {
    // RFC 3339 permits :60; `CT-08` wants one unambiguous ordering across
    // languages, and a leap second is not that. Denied, never truncated.
    throw new ParseError(kind, "semantic", "second out of range (no leap seconds)");
  }
  return value;
}

interface StringRule {
  pattern?: RegExp;
  minLength?: number;
  maxLength?: number;
  enum?: readonly string[];
  const?: string;
}

/**
 * Build a checker whose failure codes are the schema keywords themselves. The
 * order matters: a closed value set is checked before the type, because that
 * is the keyword the normative schema reports for a wrongly typed instance of
 * a `const` or `enum` definition.
 */
function stringChecker(rule: StringRule): Checker {
  return (kind, value) => {
    if (rule.const !== undefined && value !== rule.const) {
      throw new ParseError(kind, "const", `${String(value)} is not ${rule.const}`);
    }
    if (rule.enum && !rule.enum.includes(value as string)) {
      throw new ParseError(kind, "enum", `${String(value)} is not one of ${rule.enum.join("|")}`);
    }
    if (typeof value !== "string") {
      throw new ParseError(kind, "type", `expected string, got ${typeof value}`);
    }
    if (rule.minLength !== undefined && value.length < rule.minLength) {
      throw new ParseError(kind, "minLength", "value is shorter than the minimum");
    }
    if (rule.maxLength !== undefined && value.length > rule.maxLength) {
      throw new ParseError(kind, "maxLength", "value is longer than the maximum");
    }
    if (rule.pattern && !rule.pattern.test(value)) {
      throw new ParseError(kind, "pattern", `${value} does not match ${rule.pattern.source}`);
    }
    return value;
  };
}

function integerChecker(minimum: number): Checker {
  return (kind, value) => {
    if (typeof value !== "number" || !Number.isInteger(value)) {
      throw new ParseError(kind, "type", `expected integer, got ${typeof value}`);
    }
    if (value < minimum) {
      throw new ParseError(kind, "minimum", `${value} is below ${minimum}`);
    }
    if (!Number.isSafeInteger(value)) {
      throw new ParseError(kind, "range", "beyond 2^53-1; use IntString (VG-04 §0.4)");
    }
    return value;
  };
}

const IDENTIFIER = stringChecker({ minLength: 1, maxLength: 128 });

const ID_KINDS = [
  "RunId", "EpisodeId", "ProcessId", "TaskId", "ArtifactId", "ClaimId", "GrantId",
  "LeaseId", "ApprovalId", "CandidateId", "PrincipalId", "TenantId",
  "OwnerId", "EvaluatorId", "ToolCallId", "Identifier",
] as const;

const CHECKERS: Record<string, Checker> = {
  SchemaVersion: stringChecker({ const: "vg.4" }),
  Timestamp: checkTimestamp,
  Digest: stringChecker({ pattern: DIGEST }),
  IntString: stringChecker({ pattern: INT_STRING }),
  UsdMicros: stringChecker({ pattern: INT_STRING }),
  Millis: integerChecker(0),
  BranchId: integerChecker(0),
  Uuidv7: stringChecker({ pattern: UUIDV7 }),
  ResourceUri: stringChecker({ minLength: 1 }),
  RiskTier: stringChecker({ enum: ["low", "medium", "high", "critical"] }),
  ConfidentialityLabel: stringChecker({
    enum: ["public", "internal", "confidential", "restricted"],
  }),
  RetentionClass: stringChecker({
    enum: ["ephemeral", "standard", "extended", "legal_hold"],
  }),
  TrainabilityLabel: stringChecker({
    enum: ["prohibited", "opt_in_required", "opt_in_granted"],
  }),
  RedactionStatus: stringChecker({ enum: ["none", "partial", "complete", "pending"] }),
  EpistemicState: stringChecker({
    enum: ["observed", "derived", "hypothesised", "corroborated", "contradicted", "retracted"],
  }),
};
for (const kind of ID_KINDS) {
  CHECKERS[kind] = IDENTIFIER;
}

/**
 * Every primitive kind this reader parses. The vector suite iterates it, so a
 * new kind without vectors fails the coverage assertion.
 */
export const PRIMITIVE_KINDS: readonly string[] = Object.keys(CHECKERS).sort();

/** Parse an external value into a branded primitive of `kind` (`CT-03`). */
export function parse<T = string | number>(kind: string, value: unknown): T {
  const checker = CHECKERS[kind];
  if (checker === undefined) {
    throw new ParseError(kind, "unknown_kind", "no such primitive kind");
  }
  return checker(kind, value) as T;
}

/** The wire form of a parsed primitive. `unparse(parse(k, x)) === x`. */
export function unparse(primitive: unknown): string | number {
  if (typeof primitive !== "string" && typeof primitive !== "number") {
    throw new ParseError("?", "type", "not a parsed primitive");
  }
  return primitive;
}

export const parseTimestamp = (value: unknown): Timestamp => parse<Timestamp>("Timestamp", value);
export const parseDigest = (value: unknown): Digest => parse<Digest>("Digest", value);
export const parsePrincipalId = (value: unknown): PrincipalId =>
  parse<PrincipalId>("PrincipalId", value);
export const parseEpisodeId = (value: unknown): EpisodeId => parse<EpisodeId>("EpisodeId", value);

/**
 * Widen an `IntString` to an exact integer (`CT-06`, VG-04 §0.4). `bigint`
 * rather than `number`: the whole point of the wire form is that the value
 * may exceed 2^53-1.
 */
export function intStringToInt(value: IntString | UsdMicros): bigint {
  return BigInt(value as unknown as string);
}

/** Narrow an exact non-negative integer to its wire form. */
export function intStringFromInt(kind: string, value: bigint): IntString {
  if (value < 0n) {
    throw new ParseError(kind, "minimum", "IntString is non-negative");
  }
  return parse<IntString>(kind, value.toString());
}
