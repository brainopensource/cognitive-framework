import type { CanonicalErrorCode, ClientFailure, ErrorCode, Result } from "./types.js";

export const CANONICAL_ERROR_CODES = new Set<CanonicalErrorCode>([
  "invalid_request",
  "unauthenticated",
  "permission_denied",
  "not_found",
  "conflict",
  "incompatible_version",
  "frame_too_large",
  "rate_limited",
  "not_available",
  "internal",
]);

export const DEFAULT_RETRYABLE_CODES = new Set<CanonicalErrorCode>([
  "conflict",
  "rate_limited",
  "not_available",
]);

export function isRetryableCode(code: CanonicalErrorCode): boolean {
  return DEFAULT_RETRYABLE_CODES.has(code);
}

export function toClientFailureCode(code: unknown): ErrorCode {
  if (typeof code === "string") {
    if (code === "transport_interrupted") return "transport_interrupted";
    if (CANONICAL_ERROR_CODES.has(code as CanonicalErrorCode)) {
      return code as CanonicalErrorCode;
    }
  }
  return "internal";
}

export function fail(
  code: ErrorCode,
  message: string,
  retryable?: boolean,
  details?: Readonly<Record<string, unknown>>
): Result<never> {
  const isRetry =
    retryable !== undefined
      ? retryable
      : code === "transport_interrupted"
      ? true
      : DEFAULT_RETRYABLE_CODES.has(code as CanonicalErrorCode);
  return {
    ok: false,
    error: {
      code,
      message,
      retryable: isRetry,
      details,
    },
  };
}

export function isOk<T, E>(result: Result<T, E>): result is { ok: true; value: T } {
  return result.ok;
}

export function isFail<T, E>(result: Result<T, E>): result is { ok: false; error: E } {
  return !result.ok;
}
