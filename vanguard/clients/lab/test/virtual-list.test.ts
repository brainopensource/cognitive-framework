import { strict as assert } from "node:assert";
import { describe, it, before } from "node:test";
import { VirtualList } from "../src/virtual/virtual-list.js";
import { setupDomMock } from "./dom-mock.js";

describe("@aether/lab — Virtualized List (100k Items Scale)", () => {
  before(() => {
    setupDomMock();
  });

  it("virtualizes large datasets and only renders bounded window of items", () => {
    const largeList = Array.from({ length: 100_000 }, (_, i) => ({ id: i, text: `Item #${i}` }));

    let renderedDomCount = 0;
    const vlist = new VirtualList({
      items: largeList,
      itemHeight: 30,
      containerHeight: 400,
      overscan: 5,
      renderItem: (item) => {
        renderedDomCount++;
        const el = document.createElement("div");
        el.textContent = item.text;
        return el;
      },
    });

    vlist.render();

    const container = vlist.getElement();
    assert.ok(container !== null);

    // Total items is 100,000, but rendered items wrapper should contain <= 40 items
    const wrapper = container.children[0]?.children[1];
    assert.ok(wrapper !== null);
    assert.ok(wrapper?.children.length <= 50, `Rendered DOM count was ${wrapper?.children.length}, expected <= 50`);
  });

  it("updates window when scrolled", () => {
    const items = Array.from({ length: 1000 }, (_, i) => i);
    const vlist = new VirtualList({
      items,
      itemHeight: 30,
      containerHeight: 300,
      overscan: 2,
      renderItem: (item) => {
        const el = document.createElement("div");
        el.textContent = String(item);
        return el;
      },
    });

    vlist.scrollToIndex(100);
    const container = vlist.getElement();
    assert.equal(container.scrollTop, 3000);
  });
});
