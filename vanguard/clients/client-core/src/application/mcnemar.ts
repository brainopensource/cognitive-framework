/**
 * Exact McNemar statistical significance test for paired binomial comparisons
 * (e.g., AETHER vs. Baseline model on matched benchmarks).
 *
 * Given a 2x2 contingency table:
 *                Baseline Pass (1)  Baseline Fail (0)
 * Treatment Pass (1)       a                 b
 * Treatment Fail (0)       c                 d
 *
 * b = Baseline Failed, Treatment Passed (Treatment Wins)
 * c = Treatment Failed, Baseline Passed (Baseline Wins)
 */

export type McNemarResult = {
  treatmentWins: number; // b
  baselineWins: number;  // c
  concordantPairs: number; // a + d
  totalPairs: number;
  chiSquare: number;
  pValue: number;
  significant: boolean; // p < 0.05
  oddsRatio: number;
  oddsRatioCi95: [number, number];
};

/**
 * Standard normal cumulative distribution function approximation (Abramowitz & Stegun).
 */
function standardNormalCdf(z: number): number {
  if (z < 0) return 1 - standardNormalCdf(-z);
  const p = 0.2316419;
  const b1 = 0.31938153;
  const b2 = -0.356563782;
  const b3 = 1.781477937;
  const b4 = -1.821255978;
  const b5 = 1.330274429;
  const t = 1 / (1 + p * z);
  const pdf = Math.exp(-0.5 * z * z) / Math.sqrt(2 * Math.PI);
  return 1 - pdf * (b1 * t + b2 * Math.pow(t, 2) + b3 * Math.pow(t, 3) + b4 * Math.pow(t, 4) + b5 * Math.pow(t, 5));
}

/**
 * Computes exact or continuity-corrected McNemar test.
 */
export function computeMcNemarTest(
  bothPassed: number,       // a
  treatmentWon: number,     // b
  baselineWon: number,      // c
  bothFailed: number        // d
): McNemarResult {
  const total = bothPassed + treatmentWon + baselineWon + bothFailed;
  const b = treatmentWon;
  const c = baselineWon;

  if (b + c === 0) {
    return {
      treatmentWins: 0,
      baselineWins: 0,
      concordantPairs: bothPassed + bothFailed,
      totalPairs: total,
      chiSquare: 0,
      pValue: 1.0,
      significant: false,
      oddsRatio: 1.0,
      oddsRatioCi95: [1.0, 1.0],
    };
  }

  // Edwards continuity correction: (|b - c| - 1)^2 / (b + c)
  const diff = Math.abs(b - c);
  const numerator = Math.max(0, diff - 1);
  const chiSquare = (numerator * numerator) / (b + c);

  // 1-degree-of-freedom Chi-square p-value = 2 * (1 - normal_cdf(sqrt(chiSquare)))
  const z = Math.sqrt(chiSquare);
  const pValue = 2 * (1 - standardNormalCdf(z));

  // Odds Ratio = b / c (with Haldane-Anscombe correction if c=0)
  const adjB = b === 0 || c === 0 ? b + 0.5 : b;
  const adjC = b === 0 || c === 0 ? c + 0.5 : c;
  const oddsRatio = adjB / adjC;

  const logOr = Math.log(oddsRatio);
  const seLogOr = Math.sqrt(1 / adjB + 1 / adjC);
  const ciLower = Math.exp(logOr - 1.96 * seLogOr);
  const ciUpper = Math.exp(logOr + 1.96 * seLogOr);

  return {
    treatmentWins: b,
    baselineWins: c,
    concordantPairs: bothPassed + bothFailed,
    totalPairs: total,
    chiSquare: Number(chiSquare.toFixed(4)),
    pValue: Number(Math.min(1.0, Math.max(0.0, pValue)).toFixed(6)),
    significant: pValue < 0.05,
    oddsRatio: Number(oddsRatio.toFixed(3)),
    oddsRatioCi95: [Number(ciLower.toFixed(3)), Number(ciUpper.toFixed(3))],
  };
}
