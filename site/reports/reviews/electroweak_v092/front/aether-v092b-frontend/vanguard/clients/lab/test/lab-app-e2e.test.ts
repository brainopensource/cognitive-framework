import { strict as assert } from "node:assert";
import { describe, it, before } from "node:test";
import { LabApp } from "../src/components/LabApp.js";
import { LabStore } from "../src/state/lab-store.js";
import { setupDomMock } from "./dom-mock.js";

describe("@aether/lab — Application Shell & End-to-End Mounting", () => {
  before(() => {
    setupDomMock();
  });

  it("mounts application shell into root container and unmounts cleanly", () => {
    const store = new LabStore();
    const app = new LabApp({ store });

    const root = document.createElement("div");
    root.id = "root";
    document.body.appendChild(root);

    app.mount(root);

    assert.ok(root.children.length > 0);
    assert.equal(root.children[0]?.className, "aether-lab-shell");

    app.unmount();
    assert.equal(root.children.length, 0);
  });
});
