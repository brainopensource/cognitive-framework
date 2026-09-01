import { strict as assert } from "node:assert";
import { describe, it } from "node:test";
import { PassThrough } from "node:stream";
import { TerminalScreen } from "../src/terminal/screen.js";
import { charWidth, stringWidth, truncateToWidth, padToWidth } from "../src/terminal/cell.js";

describe("@aether/tui — Terminal Screen & Cell Geometry", () => {
  it("calculates correct unicode character and string widths", () => {
    assert.equal(charWidth("a".charCodeAt(0)), 1);
    assert.equal(charWidth(" ".charCodeAt(0)), 1);
    // CJK character
    assert.equal(charWidth("中".codePointAt(0)!), 2);
    // Emoji character
    assert.equal(charWidth("🚀".codePointAt(0)!), 2);

    assert.equal(stringWidth("hello"), 5);
    assert.equal(stringWidth("你好世界"), 8);
    assert.equal(stringWidth("AETHER 🚀"), 9); // 6 + 1 + 2
  });

  it("truncates and pads strings cleanly with width awareness", () => {
    assert.equal(truncateToWidth("AETHER Terminal", 10), "AETHER Te…");
    assert.equal(truncateToWidth("你好世界", 5), "你好…");
    assert.equal(padToWidth("AETHER", 10), "AETHER    ");
  });

  it("writes strings into virtual double buffer and diffs output", () => {
    const stream = new PassThrough();
    let written = "";
    stream.on("data", (chunk) => {
      written += chunk.toString("utf-8");
    });

    const screen = new TerminalScreen({ stdout: stream as any, colorMode: "plain" });
    screen.resize(40, 10);
    screen.writeString(0, 0, "AETHER TUI");
    screen.render();

    assert.ok(written.includes("AETHER TUI"));
  });
});
