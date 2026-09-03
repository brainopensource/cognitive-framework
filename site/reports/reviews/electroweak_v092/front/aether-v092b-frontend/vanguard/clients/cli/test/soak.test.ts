import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { DEMO_SCENARIOS, demoFixturePath, packageRootFrom } from "../src/composition/catalog.js";
import { parseJsonlLine } from "../src/contract/parse.js";
import { emptyRunView, reduceRunView } from "../src/application/run-view.js";

test("fixture catalog files exist and soak-reduce without throwing", () => {
  const root = packageRootFrom(import.meta.url);
  assert.equal(existsSync(join(root, "test")), true);
  for (const id of DEMO_SCENARIOS) {
    const path = demoFixturePath(root, id);
    assert.equal(existsSync(path), true, path);
    const text = readFileSync(path, "utf8");
    let view = emptyRunView();
    let count = 0;
    for (const line of text.split(/\r?\n/)) {
      if (!line.trim()) continue;
      const parsed = parseJsonlLine(line);
      assert.equal(parsed.ok, true, `${id}: ${parsed.ok ? "" : parsed.error.message}`);
      if (parsed.ok) {
        view = reduceRunView(view, parsed.value);
        count += 1;
      }
    }
    assert.ok(count >= 1, id);
    assert.ok(view.thoughts.length <= 21);
  }
});
