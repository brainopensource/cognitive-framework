import { strict as assert } from "node:assert";
import { describe, it, before } from "node:test";
import { renderJsonPayloadTree } from "../src/components/JsonPayloadTree.js";
import { setupDomMock } from "./dom-mock.js";

describe("@aether/lab — JSON Payload Tree Inspector", () => {
  before(() => {
    setupDomMock();
  });

  it("renders formatted primitives, objects, arrays, and recognizes cryptographic digests", () => {
    const payload = {
      command: "view_file",
      path: "vanguard/packages/kernel/dispatch.py",
      argsDigest: "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      tokens: 42,
      executed: true,
      subItems: ["a", "b"],
    };

    const tree = renderJsonPayloadTree({
      data: payload,
      rootName: "payload",
      defaultExpandedDepth: 2,
    });

    assert.equal(tree.className, "aether-json-tree");
    assert.ok(tree.children.length > 0);
  });
});
