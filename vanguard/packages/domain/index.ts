/** Pure values and reducers. No project imports, no I/O (ICD §2, `domain`). */

export {
  CanonicalisationError,
  canonicalBytes,
  canonicalise,
  canonicaliseText,
  parseJsonText,
  serialiseNumber,
  serialiseString,
} from "./canonicalisation/jcs.ts";
export type { JsonValue } from "./canonicalisation/jcs.ts";
export { digestBytes, digestOf } from "./canonicalisation/digest.ts";
export {
  PRIMITIVE_KINDS,
  ParseError,
  intStringFromInt,
  intStringToInt,
  parse,
  parseDigest,
  parseEpisodeId,
  parsePrincipalId,
  parseTimestamp,
  unparse,
} from "./primitives/primitives.ts";
export {
  SELECTOR_KINDS,
  SelectorError,
  canonicaliseSelector,
  decide,
  includes,
  parseSelector,
} from "./selectors/resource-selector.ts";
export type { Decision, DecisionReason, ParsedSelector, SelectorKind } from "./selectors/resource-selector.ts";
