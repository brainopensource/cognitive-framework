import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { KeyParser } from "../src/terminal/input.js";
import { KeyboardManager } from "../src/keyboard.js";
import { TuiStore } from "../src/store.js";

describe("@aether/tui — Keystroke Parser & Keyboard Grammar", () => {
  it("parses single characters, return, tabs, and arrows", () => {
    const parser = new KeyParser();

    const [a] = parser.parse("a");
    assert.equal(a?.name, "a");

    const [enter] = parser.parse("\n");
    assert.equal(enter?.name, "return");

    const [up] = parser.parse("\x1b[A");
    assert.equal(up?.name, "up");

    const [shiftTab] = parser.parse("\x1b[Z");
    assert.equal(shiftTab?.name, "tab");
    assert.equal(shiftTab?.shift, true);
  });

  it("handles bracketed paste mode", () => {
    const parser = new KeyParser();
    const pasted = parser.parse("\x1b[200~Fix lease leak in kernel dispatch\x1b[201~");
    assert.equal(pasted.length, 1);
    assert.equal(pasted[0]?.isPaste, true);
    assert.equal(pasted[0]?.pasteText, "Fix lease leak in kernel dispatch");
  });

  it("edits composer text with typing, backspace, and cursor movement", () => {
    const store = new TuiStore();
    const kb = new KeyboardManager(store);

    kb.handleKey({ name: "h", sequence: "h" });
    kb.handleKey({ name: "i", sequence: "i" });
    assert.equal(store.get().composerText, "hi");
    assert.equal(store.get().composerCursor, 2);

    kb.handleKey({ name: "backspace", sequence: "\x7f" });
    assert.equal(store.get().composerText, "h");

    kb.handleKey({ name: "left", sequence: "\x1b[D" });
    assert.equal(store.get().composerCursor, 0);

    kb.handleKey({ name: "a", sequence: "a" });
    assert.equal(store.get().composerText, "ah");
  });

  it("cycles focus across regions on Tab / Shift+Tab", () => {
    const store = new TuiStore();
    const kb = new KeyboardManager(store);

    assert.equal(store.get().focus, "composer");

    kb.handleKey({ name: "tab", sequence: "\t" });
    assert.equal(store.get().focus, "transcript");

    kb.handleKey({ name: "tab", sequence: "\t" });
    assert.equal(store.get().focus, "composer");

    kb.handleKey({ name: "tab", shift: true, sequence: "\x1b[Z" });
    assert.equal(store.get().focus, "transcript");
  });
});
