import test from "node:test";
import assert from "node:assert/strict";
import { computeMcNemarTest } from "../src/application/mcnemar.js";

test("computeMcNemarTest computes chiSquare, p-value, and odds ratios correctly", () => {
  // 40 tasks: 20 both passed, 15 treatment won, 2 baseline won, 3 both failed
  const result = computeMcNemarTest(20, 15, 2, 3);
  assert.equal(result.totalPairs, 40);
  assert.equal(result.treatmentWins, 15);
  assert.equal(result.baselineWins, 2);
  assert.equal(result.concordantPairs, 23);
  assert.ok(result.chiSquare > 8.0, "chiSquare should be > 8");
  assert.ok(result.pValue < 0.05, "pValue should be statistically significant (< 0.05)");
  assert.equal(result.significant, true);
  assert.ok(result.oddsRatio > 5.0, "odds ratio should reflect strong treatment advantage");
});

test("computeMcNemarTest handles zero discordant pairs gracefully", () => {
  const result = computeMcNemarTest(20, 0, 0, 10);
  assert.equal(result.totalPairs, 30);
  assert.equal(result.treatmentWins, 0);
  assert.equal(result.baselineWins, 0);
  assert.equal(result.pValue, 1.0);
  assert.equal(result.significant, false);
});
