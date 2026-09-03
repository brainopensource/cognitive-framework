import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

import { validateCommandFrame } from "../src/index.js";

/**
 * B-O2-01 (TypeScript half): replay the frozen vg.4 RuntimeService golden vectors.
 *
 * The corpus in `schemas/v4/vectors/runtime-service/` is data, not tests: it is the
 * cross-language contract that `vanguard/packages/runtime/service/contract.py` and this
 * package's `validateCommandFrame` must both agree with. This is the TypeScript half of
 * that replay; `test/contracts/test_runtime_service_vectors.py` is the Python half, and
 * both read the same bytes.
 */

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(__dirname, "../../../../..");
const VECTORS = path.join(REPO_ROOT, "schemas", "v4", "vectors", "runtime-service");

function cases(kind: "valid" | "invalid"): Array<{ name: string; file: string }> {
  const dir = path.join(VECTORS, kind);
  return readdirSync(dir)
    .filter((f) => f.endsWith(".json") && !f.endsWith(".expect.json"))
    .sort()
    .map((f) => ({ name: f.replace(/\.json$/, ""), file: path.join(dir, f) }));
}

function readJson(file: string): unknown {
  return JSON.parse(readFileSync(file, "utf-8"));
}

describe("RuntimeService vg.4 golden vector corpus (TypeScript reader)", () => {
  it("corpus is present and non-trivial", () => {
    assert.ok(cases("valid").length > 0, "no valid vectors published");
    assert.ok(cases("invalid").length > 0, "no invalid vectors published");
  });

  it("every valid vector is accepted", () => {
    for (const { name, file } of cases("valid")) {
      const frame = readJson(file);
      const result = validateCommandFrame(frame);
      assert.equal(result.ok, true, `golden vector ${name} rejected: ${!result.ok ? `[${result.error.code}] ${result.error.message}` : ""}`);
    }
  });

  it("every invalid vector is rejected with the declared code", () => {
    for (const { name, file } of cases("invalid")) {
      const frame = readJson(file);
      const expectFile = file.replace(/\.json$/, ".expect.json");
      const expect = readJson(expectFile) as { expectedCode: string };
      const result = validateCommandFrame(frame);
      assert.equal(result.ok, false, `${name} was accepted`);
      if (!result.ok) {
        assert.equal(result.error.code, expect.expectedCode, `${name}: wrong canonical error code`);
      }
    }
  });
});
