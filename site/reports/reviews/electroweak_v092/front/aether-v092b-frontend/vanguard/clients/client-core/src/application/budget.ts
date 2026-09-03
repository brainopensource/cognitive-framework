/** Parse CLI currency once into integer microdollars. No reinterpretation downstream. */

export const USD_TO_MICROS = 1_000_000;
/** Hard client-side reject above $100 — product campaigns use far less. */
export const MAX_BUDGET_USD = 100;
export const MAX_BUDGET_MICROS = MAX_BUDGET_USD * USD_TO_MICROS;

export type BudgetParseError = {
  code: "invalid_budget";
  message: string;
};

export type BudgetParseResult =
  | { ok: true; micros: number }
  | { ok: false; error: BudgetParseError };

/**
 * Convert a `--budget-usd` string to integer microdollars.
 * Rejects negative, non-finite, empty, excess, and malformed values.
 */
export function parseBudgetUsdToMicros(raw: string | undefined): BudgetParseResult {
  if (raw === undefined || raw.trim() === "") {
    return { ok: false, error: { code: "invalid_budget", message: "budget-usd is required when coding with a spend ceiling" } };
  }
  const trimmed = raw.trim().replace(/^\$/, "");
  if (!/^-?\d+(\.\d+)?$/.test(trimmed)) {
    return { ok: false, error: { code: "invalid_budget", message: `malformed budget-usd: ${raw}` } };
  }
  const dollars = Number(trimmed);
  if (!Number.isFinite(dollars)) {
    return { ok: false, error: { code: "invalid_budget", message: "budget-usd must be finite" } };
  }
  if (dollars < 0) {
    return { ok: false, error: { code: "invalid_budget", message: "budget-usd cannot be negative" } };
  }
  if (dollars > MAX_BUDGET_USD) {
    return { ok: false, error: { code: "invalid_budget", message: `budget-usd exceeds ${MAX_BUDGET_USD}` } };
  }
  const micros = Math.round(dollars * USD_TO_MICROS);
  if (!Number.isSafeInteger(micros) || micros > MAX_BUDGET_MICROS) {
    return { ok: false, error: { code: "invalid_budget", message: "budget-usd overflows microdollar integer" } };
  }
  return { ok: true, micros };
}

/** Format micros for human receipts; unknown stays unknown, never zero. */
export function formatUsdFromMicros(micros: number | null | undefined): string {
  if (micros === null || micros === undefined) return "unknown";
  if (!Number.isFinite(micros)) return "unknown";
  return `$${(micros / USD_TO_MICROS).toFixed(4)}`;
}
