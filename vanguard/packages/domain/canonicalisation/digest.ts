/**
 * Content digests over canonical bytes — TypeScript reader.
 *
 * Owning contract: VG-04 `CT-09` (`sha256:` plus 64 lowercase hex), `SC-2`
 * (every digest is computed over the RFC 8785 canonical form).
 *
 * `node:crypto` is a pure computation over the supplied bytes: no I/O, no
 * clock, no randomness, no environment access. It is the only host module
 * `domain` reaches for, and it is confined to this file.
 */

import { createHash } from "node:crypto";

import { canonicalBytes } from "./jcs.ts";

/** `sha256:<64 lowercase hex>` over raw bytes (`CT-09`). */
export function digestBytes(payload: Uint8Array): string {
  return `sha256:${createHash("sha256").update(payload).digest("hex")}`;
}

/** Digest of a JSON value over its canonical form — the only supported path. */
export function digestOf(value: unknown): string {
  return digestBytes(canonicalBytes(value));
}
