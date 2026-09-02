import { strict as assert } from "node:assert";
import { describe, it, before } from "node:test";
import { installMockDom, type MockDocument } from "./support/mock-dom.js";
import {
  captureFocus,
  restoreFocus,
  FOCUS_KEY_ATTRIBUTE,
} from "../src/dom/focus-preservation.js";

let doc: MockDocument;

/**
 * The desktop rebuilds its whole tree on every state change, so an element
 * that had focus before a render is a different object after it. These assert
 * the carry-across directly: capture, discard the tree, rebuild, restore.
 */
describe("@aether/desktop — focus survives a full re-render", () => {
  before(() => {
    doc = installMockDom();
  });

  function buildTree(value: string) {
    const container = doc.createElement("div");
    const textarea = doc.createElement("textarea");
    textarea.setAttribute(FOCUS_KEY_ATTRIBUTE, "composer-input");
    textarea.value = value;
    const search = doc.createElement("input");
    search.setAttribute(FOCUS_KEY_ATTRIBUTE, "sidebar-search");
    container.appendChild(textarea);
    container.appendChild(search);
    return { container, textarea, search };
  }

  it("returns focus to the same keyed field after the tree is replaced", () => {
    const first = buildTree("hell");
    first.textarea.focus();

    const captured = captureFocus(doc as any);
    const second = buildTree("hello");
    const restored = restoreFocus(captured, second.container as any);

    assert.equal(restored, true);
    assert.equal(doc.activeElement, second.textarea);
  });

  it("restores the caret position, not just the field", () => {
    const first = buildTree("hello");
    first.textarea.focus();
    first.textarea.setSelectionRange(3, 3);

    const captured = captureFocus(doc as any);
    const second = buildTree("hello");
    restoreFocus(captured, second.container as any);

    assert.equal(second.textarea.selectionStart, 3);
    assert.equal(second.textarea.selectionEnd, 3);
  });

  it("clamps a caret that outruns a shortened value", () => {
    const first = buildTree("hello world");
    first.textarea.focus();
    first.textarea.setSelectionRange(11, 11);

    const captured = captureFocus(doc as any);
    const second = buildTree("hi");
    restoreFocus(captured, second.container as any);

    assert.equal(second.textarea.selectionStart, 2);
  });

  it("distinguishes fields, so focus does not jump to the wrong input", () => {
    const first = buildTree("");
    first.search.focus();

    const captured = captureFocus(doc as any);
    const second = buildTree("");
    restoreFocus(captured, second.container as any);

    assert.equal(doc.activeElement, second.search);
  });

  it("captures nothing when focus is on an unkeyed element", () => {
    const unkeyed = doc.createElement("button");
    unkeyed.focus();

    assert.equal(captureFocus(doc as any), null);
  });

  it("restoring a key that no longer exists reports false and throws nothing", () => {
    const first = buildTree("x");
    first.textarea.focus();
    const captured = captureFocus(doc as any);

    const bare = doc.createElement("div");
    assert.equal(restoreFocus(captured, bare as any), false);
  });

  it("restoring null focus is a no-op", () => {
    const tree = buildTree("x");
    assert.equal(restoreFocus(null, tree.container as any), false);
  });
});
