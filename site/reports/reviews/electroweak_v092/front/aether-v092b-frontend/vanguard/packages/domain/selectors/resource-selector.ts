/**
 * ResourceSelector algebra — TypeScript reader.
 *
 * Owning contract: VG-04 §5.2 and §5.3.1 / `CT-24`..`CT-28`, `CT-52`, `D-2`;
 * `schemas/v4/resource-selector.schema.json`; `REQ-SCHEMA-003`.
 *
 * `includes(parent, child)` is the "resources are a subset" half of
 * attenuation (VG-04 §5.3). It is **total**: every pair returns a decision,
 * and every pair without a defined relation is denied (`CT-52`). Nothing is
 * intersected or narrowed (`CT-25`).
 *
 * The relation is a partial order on canonical selectors — reflexive,
 * transitive, and antisymmetric up to canonical equality. Antisymmetry is why
 * `parseSelector` prunes members another member already covers: `/repo` plus
 * `/repo/src` denotes the same authority as `/repo` alone, so the two must
 * reduce to the same canonical bytes.
 *
 * Semantic rules not expressible in JSON Schema are recorded in
 * `vanguard/packages/domain/SEMANTICS.md` as ADR candidates.
 */

import { canonicalise } from "../canonicalisation/jcs.ts";

export const SELECTOR_KINDS = [
  "fs", "network", "secret", "git", "table", "browser", "generic",
] as const;

export type SelectorKind = (typeof SELECTOR_KINDS)[number];

/**
 * `included` · `not_included` · `cross_kind` · `undefined_relation` ·
 * `unparsable`. Every denial maps to `AuthorizationDenied{scope_escalation}`
 * at the policy boundary.
 */
export type DecisionReason =
  | "included"
  | "not_included"
  | "cross_kind"
  | "undefined_relation"
  | "unparsable";

export interface Decision {
  readonly included: boolean;
  readonly reason: DecisionReason;
}

export class SelectorError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(`${code}: ${message}`);
    this.name = "SelectorError";
    this.code = code;
  }
}

export type ParsedSelector = Record<string, unknown> & { kind: SelectorKind };

/** `04 §5.3.1`: "No globs in a grant — expand at issuance." */
const GLOB = /[*?[\]{}]/;
const LABEL = /^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$/;
const ORIGIN = /^([a-z][a-z0-9+.-]*):\/\/([^/?#]+)$/i;
const RANGE = /^(0|[1-9][0-9]*)\.\.(0|[1-9][0-9]*)$/;
const DEFAULT_PORTS: Record<string, number> = { http: 80, https: 443, ws: 80, wss: 443 };
const WHOLE_TABLE: Interval = [0, -1];

type Interval = readonly [number, number];

function require_(condition: boolean, code: string, message: string): asserts condition {
  if (!condition) throw new SelectorError(code, message);
}

function requireString(value: unknown, field: string): string {
  require_(typeof value === "string", "type", `${field} must be a string`);
  return value;
}

/** `D-2`: forward slashes, relative segments collapsed, no trailing slash. */
function normalisePath(raw: unknown, field = "path"): string {
  let text = requireString(raw, field);
  require_(text !== "", "empty", `${field} must not be empty`);
  require_(
    !GLOB.test(text),
    "glob",
    `${field} contains glob metacharacters; expand at issuance (§5.3.1)`,
  );
  text = text.replace(/\\/g, "/");
  const absolute = text.startsWith("/");
  const segments: string[] = [];
  for (const segment of text.split("/")) {
    if (segment === "" || segment === ".") continue;
    if (segment === "..") {
      // Collapsing past the start would silently widen the surface, so an
      // unresolvable ascent is a parse failure, not a clamp.
      require_(segments.length > 0, "traversal", `${field} escapes its root`);
      segments.pop();
      continue;
    }
    segments.push(segment);
  }
  const joined = segments.join("/");
  return absolute ? `/${joined}` : joined;
}

function normaliseUri(raw: unknown, field: string): string {
  const text = requireString(raw, field);
  require_(text !== "", "empty", `${field} must not be empty`);
  return text;
}

/**
 * `fs.root` is a `ResourceUri`, compared for equality after one rule: a
 * trailing separator is not part of the identity of a root.
 */
function normaliseRoot(raw: unknown): string {
  let text = normaliseUri(raw, "root").replace(/\\/g, "/");
  if (text.length > 1) text = text.replace(/\/+$/, "") || "/";
  return text;
}

/** Lowercase, NFC, IDNA A-labels, no trailing root dot (§5.3.1, network). */
function normaliseHost(raw: unknown): string {
  const text = requireString(raw, "host");
  require_(text !== "", "empty", "host must not be empty");
  const wildcard = text.startsWith("*.");
  let body = (wildcard ? text.slice(2) : text).normalize("NFC").toLowerCase();
  body = body.replace(/\.+$/, "");
  require_(body !== "", "empty", "host must have at least one label");
  require_(!body.includes("*"), "wildcard", "a wildcard is only allowed as the leading label");
  const labels: string[] = [];
  for (const raw_label of body.split(".")) {
    require_(raw_label !== "", "label", "empty DNS label");
    let label = raw_label;
    // eslint-disable-next-line no-control-regex
    if (/[^\x00-\x7F]/.test(label)) {
      let encoded: string;
      try {
        encoded = new URL(`http://${label}`).hostname;
      } catch {
        throw new SelectorError("idna", `label ${label} is not IDNA-encodable`);
      }
      label = encoded;
    }
    require_(LABEL.test(label), "label", `${label} is not a DNS label`);
    labels.push(label);
  }
  const normalised = labels.join(".");
  require_(normalised.length <= 253, "length", "host exceeds 253 characters");
  return wildcard ? `*.${normalised}` : normalised;
}

function normalisePort(raw: unknown): number {
  require_(typeof raw === "number" && Number.isInteger(raw), "type", "port must be an integer");
  require_(raw >= 1 && raw <= 65535, "range", `port ${raw} out of range`);
  return raw;
}

/** Scheme, host and port only — the browser's own trust unit (§5.3.1). */
function normaliseOrigin(raw: unknown): string {
  const text = requireString(raw, "origin");
  const match = ORIGIN.exec(text);
  require_(match !== null, "origin", `${text} is not a scheme://host[:port] origin`);
  const scheme = match[1]!.toLowerCase();
  const authority = match[2]!;
  require_(!authority.includes("@"), "origin", "an origin carries no userinfo");
  let host: string;
  let rest: string;
  if (authority.startsWith("[")) {
    const close = authority.indexOf("]");
    require_(close > 0, "origin", "unterminated IPv6 literal");
    host = authority.slice(0, close + 1).toLowerCase();
    rest = authority.slice(close + 1);
  } else {
    const colon = authority.indexOf(":");
    host = normaliseHost(colon === -1 ? authority : authority.slice(0, colon));
    require_(!host.startsWith("*."), "origin", "a wildcard origin is not an origin");
    rest = colon === -1 ? "" : authority.slice(colon);
  }
  if (rest !== "") {
    require_(rest.startsWith(":"), "origin", "trailing junk after host");
    const digits = rest.slice(1);
    require_(/^[0-9]+$/.test(digits), "origin", "port must be decimal digits");
    const port = normalisePort(Number(digits));
    rest = DEFAULT_PORTS[scheme] === port ? "" : `:${port}`;
  }
  return `${scheme}://${host}${rest}`;
}

/** Full-ref expansion (§5.3.1, git). Pattern refs are rejected. */
function expandRef(raw: unknown): string {
  const text = requireString(raw, "ref");
  require_(text !== "", "empty", "ref must not be empty");
  require_(!GLOB.test(text), "glob", "pattern refs are not grantable (§5.3.1)");
  if (text === "HEAD" || text.startsWith("refs/")) return text;
  return `refs/heads/${text}`;
}

/**
 * `lo..hi` half-open interval over normalised integer coordinates, or `*`.
 *
 * VG-04 §5.3.1 requires "interval containment on normalised coordinates" but
 * fixes no coordinate grammar. This reader defines exactly one and denies
 * every other spelling rather than guessing (ADR candidate D1-003).
 */
function parseRange(raw: unknown): Interval {
  const text = requireString(raw, "range");
  if (text === "*") return WHOLE_TABLE;
  const match = RANGE.exec(text);
  require_(match !== null, "range", `${text} is not \`lo..hi\` or \`*\` (ADR candidate D1-003)`);
  const low = Number(match[1]);
  const high = Number(match[2]);
  require_(low < high, "range", "range must be non-empty and low < high");
  return [low, high];
}

function renderRange(interval: Interval): string {
  return interval[1] === -1 ? "*" : `${interval[0]}..${interval[1]}`;
}

function rangeContains(outer: Interval, inner: Interval): boolean {
  if (outer[1] === -1) return true;
  if (inner[1] === -1) return false;
  return outer[0] <= inner[0] && inner[1] <= outer[1];
}

function requireFields(
  selector: Record<string, unknown>,
  required: readonly string[],
  optional: readonly string[] = [],
): void {
  for (const field of required) {
    require_(field in selector, "required", `missing required field ${field}`);
  }
  const allowed = new Set([...required, ...optional, "kind"]);
  for (const field of Object.keys(selector)) {
    require_(allowed.has(field), "additionalProperties", `unknown field ${field}`);
  }
}

function requireArray(value: unknown, field: string, minItems: number): unknown[] {
  require_(Array.isArray(value), "type", `${field} must be an array`);
  require_(value.length >= minItems, "minItems", `${field} needs at least ${minItems} item(s)`);
  return value;
}

function pathUnder(parent: string, child: string): boolean {
  if (parent === child) return true;
  if (parent === "" || parent === "/") return child.startsWith(parent);
  return child.startsWith(`${parent}/`);
}

function prunePaths(paths: string[]): string[] {
  const unique = [...new Set(paths)].sort();
  return unique.filter((p) => !unique.some((q) => q !== p && pathUnder(q, p)));
}

/**
 * Wildcard containment (§5.3.1, network).
 *
 * A parent wildcard contains a child *label*, never another wildcard. Equal
 * hosts always contain one another, wildcards included; without that the
 * relation would not be reflexive, and `includes(x, x)` must hold for every
 * value a grant can carry.
 */
function hostCovers(parent: string, child: string): boolean {
  if (parent === child) return true;
  if (!parent.startsWith("*.")) return false;
  if (child.startsWith("*.")) return false;
  const suffix = parent.slice(2);
  if (!child.endsWith(`.${suffix}`)) return false;
  const label = child.slice(0, child.length - suffix.length - 1);
  return label !== "" && !label.includes(".");
}

function pruneHosts(hosts: string[]): string[] {
  const unique = [...new Set(hosts)].sort();
  return unique.filter((h) => !unique.some((g) => g !== h && hostCovers(g, h)));
}

function pruneRanges(intervals: Interval[]): Interval[] {
  const unique = [...new Map(intervals.map((i) => [`${i[0]}..${i[1]}`, i])).values()]
    .sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  return unique.filter(
    (i) => !unique.some((j) => j !== i && rangeContains(j, i)),
  );
}

function sortedUnique(values: string[]): string[] {
  return [...new Set(values)].sort();
}

/**
 * Parse and normalise one selector, or throw. The result is the canonical
 * form: normalised, pruned of members another member already covers, ordered.
 * Two selectors denote the same authority exactly when these forms are equal.
 */
export function parseSelector(value: unknown): ParsedSelector {
  require_(
    typeof value === "object" && value !== null && !Array.isArray(value),
    "type",
    "selector must be an object",
  );
  const record = value as Record<string, unknown>;
  const kind = record["kind"];
  require_(
    typeof kind === "string" && (SELECTOR_KINDS as readonly string[]).includes(kind),
    "kind",
    `unknown selector kind ${String(kind)}`,
  );

  switch (kind as SelectorKind) {
    case "fs": {
      requireFields(record, ["kind", "root", "paths"]);
      const paths = requireArray(record["paths"], "paths", 1).map((p) => normalisePath(p));
      return { kind: "fs", root: normaliseRoot(record["root"]), paths: prunePaths(paths) };
    }
    case "network": {
      requireFields(record, ["kind", "hosts", "ports"]);
      const hosts = requireArray(record["hosts"], "hosts", 1).map(normaliseHost);
      const ports = requireArray(record["ports"], "ports", 0).map(normalisePort);
      return {
        kind: "network",
        hosts: pruneHosts(hosts),
        ports: [...new Set(ports)].sort((a, b) => a - b),
      };
    }
    case "secret": {
      requireFields(record, ["kind", "refs", "discloseToModel"]);
      require_(
        record["discloseToModel"] === false,
        "const",
        "discloseToModel is the literal false; there is no path that flips it (§5.2)",
      );
      const refs = requireArray(record["refs"], "refs", 1).map((r) => requireString(r, "ref"));
      for (const ref of refs) require_(ref !== "", "empty", "secret ref must not be empty");
      return { kind: "secret", refs: sortedUnique(refs), discloseToModel: false };
    }
    case "git": {
      requireFields(record, ["kind", "repo", "refs"]);
      const refs = requireArray(record["refs"], "refs", 1).map(expandRef);
      return { kind: "git", repo: normaliseUri(record["repo"], "repo"), refs: sortedUnique(refs) };
    }
    case "table": {
      requireFields(record, ["kind", "table"], ["ranges"]);
      // An absent `ranges` denotes the whole table, so it normalises to the
      // explicit whole-table range. Two spellings of one authority must not
      // produce two canonical forms.
      const rawRanges = "ranges" in record ? record["ranges"] : ["*"];
      let intervals = requireArray(rawRanges, "ranges", 0).map(parseRange);
      if (intervals.length === 0) intervals = [WHOLE_TABLE];
      return {
        kind: "table",
        table: normaliseUri(record["table"], "table"),
        ranges: pruneRanges(intervals).map(renderRange),
      };
    }
    case "browser": {
      requireFields(record, ["kind", "origin"], ["accountRef"]);
      const parsed: ParsedSelector = {
        kind: "browser",
        origin: normaliseOrigin(record["origin"]),
      };
      if ("accountRef" in record) {
        parsed["accountRef"] = requireString(record["accountRef"], "accountRef");
      }
      return parsed;
    }
    default:
      requireFields(record, ["kind", "uriPattern"]);
      // `04 §5.3.1`: literal equality only. No normalisation, because any
      // normalisation here approximates pattern containment, and an
      // approximation silently widens authority.
      return { kind: "generic", uriPattern: requireString(record["uriPattern"], "uriPattern") };
  }
}

/** Canonical RFC 8785 bytes of a selector, as text (`SC-2`). */
export function canonicaliseSelector(value: unknown): string {
  return canonicalise(parseSelector(value));
}

function includesParsed(parent: ParsedSelector, child: ParsedSelector): Decision {
  if (parent.kind !== child.kind) {
    // `CT-52`: any cross-kind comparison is denied, never intersected.
    return { included: false, reason: "cross_kind" };
  }
  const verdict = (ok: boolean): Decision => ({
    included: ok,
    reason: ok ? "included" : "not_included",
  });

  switch (parent.kind) {
    case "fs": {
      if (parent["root"] !== child["root"]) return verdict(false);
      const parents = parent["paths"] as string[];
      return verdict((child["paths"] as string[]).every((c) => parents.some((p) => pathUnder(p, c))));
    }
    case "network": {
      const hosts = parent["hosts"] as string[];
      const ports = new Set(parent["ports"] as number[]);
      const hostsOk = (child["hosts"] as string[]).every((c) => hosts.some((p) => hostCovers(p, c)));
      const portsOk = (child["ports"] as number[]).every((p) => ports.has(p));
      return verdict(hostsOk && portsOk);
    }
    case "secret": {
      const refs = new Set(parent["refs"] as string[]);
      return verdict((child["refs"] as string[]).every((r) => refs.has(r)));
    }
    case "git": {
      const refs = new Set(parent["refs"] as string[]);
      return verdict(
        parent["repo"] === child["repo"] && (child["refs"] as string[]).every((r) => refs.has(r)),
      );
    }
    case "table": {
      if (parent["table"] !== child["table"]) return verdict(false);
      const parents = (parent["ranges"] as string[]).map(parseRange);
      const children = (child["ranges"] as string[]).map(parseRange);
      return verdict(children.every((c) => parents.some((p) => rangeContains(p, c))));
    }
    case "browser": {
      // Exact origin equality. No subdomain or path containment: origin is
      // the browser's own trust unit (§5.3.1).
      if (parent["origin"] !== child["origin"]) return verdict(false);
      if (!("accountRef" in parent)) return verdict(true);
      return verdict(child["accountRef"] === parent["accountRef"]);
    }
    default:
      return verdict(parent["uriPattern"] === child["uriPattern"]);
  }
}

/**
 * Total inclusion decision for any two values (`CT-52`). `included` is true
 * only when `child` is provably a subset of `parent`; anything unparseable,
 * cross-kind or without a defined relation is denied, and the caller emits
 * `AuthorizationDenied{scope_escalation}` recording both what was requested
 * and what was grantable (`CT-24`).
 */
export function decide(parent: unknown, child: unknown): Decision {
  let parsedParent: ParsedSelector;
  let parsedChild: ParsedSelector;
  try {
    parsedParent = parseSelector(parent);
    parsedChild = parseSelector(child);
  } catch (error) {
    if (!(error instanceof SelectorError)) throw error;
    return { included: false, reason: "unparsable" };
  }
  return includesParsed(parsedParent, parsedChild);
}

/** `child ⊆ parent`. False on every undefined pair (`CT-52`). */
export function includes(parent: unknown, child: unknown): boolean {
  return decide(parent, child).included;
}
